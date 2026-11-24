from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError as e:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Install it with: pip install pyyaml"
    ) from e


# ============================================================
# Utility functions
# ============================================================


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


WILDCARD_RE = re.compile(r"\[\*\]")
STATE_REF_RE = re.compile(r"\{\{\s*state\.([^}]+?)\s*\}\}")
PROMPT_REF_RE = re.compile(r"^prompts\.(.+)$")


def deep_get(data: Any, path: str, default: Any = None) -> Any:
    """Simple dotted-path getter supporting [*] wildcard for lists.

    Examples:
      research_object_card.true_research_object
      stress_test_report.failure_layer_map[*].rollback_node
    """
    if path == "":
        return data

    parts = path.split(".")

    def _walk(current: Any, idx: int) -> Any:
        if idx >= len(parts):
            return current
        part = parts[idx]

        if part.endswith("[*]"):
            key = part[:-3]
            if key:
                if not isinstance(current, dict):
                    return default
                current = current.get(key, default)
            if not isinstance(current, list):
                return default
            out = []
            for item in current:
                val = _walk(item, idx + 1)
                if isinstance(val, list):
                    out.extend(val)
                elif val is not default:
                    out.append(val)
            return out

        if isinstance(current, dict):
            if part not in current:
                return default
            return _walk(current[part], idx + 1)
        return default

    return _walk(data, 0)


def deep_set(data: Dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur = data
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


def render_prompt(template: str, state: Dict[str, Any]) -> str:
    def _replace(match: re.Match[str]) -> str:
        path = match.group(1).strip()
        value = deep_get(state, path, "")
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return "" if value is None else str(value)

    return STATE_REF_RE.sub(_replace, template)


# ============================================================
# Rule engine
# ============================================================


def normalize_to_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class RuleEvaluator:
    @staticmethod
    def eval_field_rule(state: Dict[str, Any], rule: Dict[str, Any], gates: Dict[str, bool]) -> bool:
        if "gate" in rule:
            gate_name = rule["gate"]
            op = rule["op"]
            if op != "passed":
                raise ValueError(f"Unsupported gate operator: {op}")
            return bool(gates.get(gate_name, False))

        field_path = rule["field"]
        op = rule["op"]
        value = deep_get(state, field_path, None)
        expected = rule.get("value")

        if op == "not_empty":
            return value not in (None, "", [], {})
        if op == "equals":
            return value == expected
        if op == "contains":
            if value is None:
                return False
            if isinstance(value, list):
                return expected in value
            return str(expected) in str(value)
        if op == "contains_all":
            if isinstance(value, list):
                return all(item in value for item in normalize_to_list(expected))
            s = "" if value is None else str(value)
            return all(str(item) in s for item in normalize_to_list(expected))
        if op == "contains_any":
            if isinstance(value, list):
                return any(item in value for item in normalize_to_list(expected))
            s = "" if value is None else str(value)
            return any(str(item) in s for item in normalize_to_list(expected))
        if op == "min_length":
            return hasattr(value, "__len__") and len(value) >= int(expected)
        if op == "max_length":
            return hasattr(value, "__len__") and len(value) <= int(expected)
        if op == "exact_length":
            return hasattr(value, "__len__") and len(value) == int(expected)
        if op == "min_chars":
            return len("" if value is None else str(value)) >= int(expected)
        if op == "all_not_empty":
            values = normalize_to_list(value)
            return len(values) > 0 and all(v not in (None, "", [], {}) for v in values)
        if op == "in":
            return value in normalize_to_list(expected)
        if op == "passed":
            raise ValueError("'passed' operator is only valid for gate rules")

        raise ValueError(f"Unsupported operator: {op}")

    @staticmethod
    def eval_all(state: Dict[str, Any], rules: List[Dict[str, Any]], gates: Dict[str, bool]) -> Tuple[bool, List[Dict[str, Any]]]:
        failed = []
        for rule in rules:
            ok = RuleEvaluator.eval_field_rule(state, rule, gates)
            if not ok:
                failed.append(rule)
        return len(failed) == 0, failed


# ============================================================
# Agent execution interfaces
# ============================================================


class AgentExecutionError(RuntimeError):
    pass


class BaseAgentExecutor:
    """Implement this class to connect your LLM / API / local model.

    The runner will call:
      run(agent_id, role, prompt, inputs, state) -> dict
    """

    def run(
        self,
        agent_id: str,
        role: str,
        prompt: Optional[str],
        inputs: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        raise NotImplementedError


class StubAgentExecutor(BaseAgentExecutor):
    """A minimal executor that raises clear errors.

    Replace this with your real model client.
    """

    def run(
        self,
        agent_id: str,
        role: str,
        prompt: Optional[str],
        inputs: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        raise AgentExecutionError(
            f"No real agent executor configured. Tried to run {agent_id} ({role})."
        )


# ============================================================
# Workflow runner
# ============================================================


@dataclass
class NodeResult:
    node_id: str
    passed: bool
    output: Optional[Dict[str, Any]] = None
    failed_rules: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class PaperWorkflowSkill:
    def __init__(
        self,
        workflow_config: Dict[str, Any],
        prompt_config: Dict[str, Any],
        agent_executor: Optional[BaseAgentExecutor] = None,
    ) -> None:
        self.workflow = workflow_config
        self.prompts = prompt_config.get("prompts", {})
        self.agent_executor = agent_executor or StubAgentExecutor()

        self.state: Dict[str, Any] = copy.deepcopy(workflow_config.get("state", {}))
        self.gates: Dict[str, bool] = {}
        self.history: List[Dict[str, Any]] = []

    # ---------------------------
    # Public API
    # ---------------------------

    @classmethod
    def from_files(
        cls,
        workflow_path: str | Path,
        prompts_path: str | Path,
        agent_executor: Optional[BaseAgentExecutor] = None,
    ) -> "PaperWorkflowSkill":
        return cls(load_yaml(workflow_path), load_yaml(prompts_path), agent_executor)

    def set_initial_state(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            self.state[k] = v

    def run_all(self) -> Dict[str, Any]:
        for stage_id in ["stage_1_foundation", "stage_2_manuscript", "stage_3_stresstest"]:
            self.run_stage(stage_id)
        return self.snapshot()

    def run_stage(self, stage_id: str) -> Dict[str, Any]:
        stages = self.workflow["stages"]
        stage = stages[stage_id]

        self._check_stage_entry(stage_id, stage)

        for node_id in stage["node_order"]:
            result = self.run_node(node_id)
            if not result.passed:
                raise AgentExecutionError(f"Node failed: {node_id} | error={result.error}")

        self._evaluate_stage_exit_gate(stage_id, stage)
        return self.snapshot()

    def run_node(self, node_id: str) -> NodeResult:
        node = self.workflow["nodes"][node_id]
        agents = node["agents"]

        # 1) check agent
        check_result = self._run_check_agent(node_id, agents["check"])
        if not check_result.passed:
            return self._handle_node_failure(node_id, check_result)

        # 2) generate agent
        gen_output = self._run_generate_agent(node_id, agents["generate"])
        output_key = node["output_key"]
        self.state[output_key] = gen_output

        # 3) validate agent
        validate_result = self._run_validate_agent(node_id, agents["validate"])
        if not validate_result.passed:
            return self._handle_node_failure(node_id, validate_result)

        self.history.append({"node": node_id, "status": "passed"})
        return NodeResult(node_id=node_id, passed=True, output=gen_output)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "state": copy.deepcopy(self.state),
            "gates": copy.deepcopy(self.gates),
            "history": copy.deepcopy(self.history),
        }

    # ---------------------------
    # Stage helpers
    # ---------------------------

    def _check_stage_entry(self, stage_id: str, stage: Dict[str, Any]) -> None:
        requirements = stage.get("entry_requirements", [])
        ok, failed = RuleEvaluator.eval_all(self.state, requirements, self.gates)
        if not ok:
            raise AgentExecutionError(
                f"Stage {stage_id} entry requirements failed: {json.dumps(failed, ensure_ascii=False)}"
            )

    def _evaluate_stage_exit_gate(self, stage_id: str, stage: Dict[str, Any]) -> None:
        gate = stage["exit_gate"]
        ok, failed = RuleEvaluator.eval_all(self.state, gate.get("conditions", []), self.gates)
        self.gates[gate["id"]] = ok
        if not ok:
            raise AgentExecutionError(
                f"Stage {stage_id} exit gate failed: {json.dumps(failed, ensure_ascii=False)}"
            )

    # ---------------------------
    # Agent runners
    # ---------------------------

    def _run_check_agent(self, node_id: str, agent_id: str) -> NodeResult:
        agent = self.workflow["agents"][agent_id]
        prompt = self._resolve_prompt(agent)
        inputs = self._collect_inputs(agent.get("inputs", []))
        output = self.agent_executor.run(agent_id, agent["role"], prompt, inputs, self.state)

        local_state = copy.deepcopy(self.state)
        local_state.update(output)
        ok, failed = RuleEvaluator.eval_all(local_state, agent.get("pass_rule", []), self.gates)
        return NodeResult(node_id=node_id, passed=ok, output=output, failed_rules=failed)

    def _run_generate_agent(self, node_id: str, agent_id: str) -> Dict[str, Any]:
        agent = self.workflow["agents"][agent_id]
        prompt = self._resolve_prompt(agent)
        inputs = self._collect_inputs(agent.get("inputs", []))
        output = self.agent_executor.run(agent_id, agent["role"], prompt, inputs, self.state)
        if not isinstance(output, dict):
            raise AgentExecutionError(f"Generate agent {agent_id} must return a dict")
        return output

    def _run_validate_agent(self, node_id: str, agent_id: str) -> NodeResult:
        agent = self.workflow["agents"][agent_id]
        local_state = copy.deepcopy(self.state)
        ok, failed = RuleEvaluator.eval_all(local_state, agent.get("rules", []), self.gates)
        return NodeResult(node_id=node_id, passed=ok, failed_rules=failed)

    # ---------------------------
    # Failure handling
    # ---------------------------

    def _handle_node_failure(self, node_id: str, result: NodeResult) -> NodeResult:
        node = self.workflow["nodes"][node_id]
        rollback_to = node["on_failure"]["rollback_to"]
        self.history.append(
            {
                "node": node_id,
                "status": "failed",
                "failed_rules": result.failed_rules,
                "rollback_to": rollback_to,
            }
        )
        result.error = f"Node {node_id} failed; rollback target: {rollback_to}"
        return result

    # ---------------------------
    # Internal utils
    # ---------------------------

    def _resolve_prompt(self, agent: Dict[str, Any]) -> Optional[str]:
        prompt_ref = agent.get("prompt_ref")
        if not prompt_ref:
            return None
        match = PROMPT_REF_RE.match(prompt_ref)
        if not match:
            raise ValueError(f"Invalid prompt_ref: {prompt_ref}")
        key = match.group(1)
        if key not in self.prompts:
            raise KeyError(f"Prompt key not found: {key}")
        return render_prompt(self.prompts[key], self.state)

    def _collect_inputs(self, input_keys: List[str]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key in input_keys:
            out[key] = self.state.get(key)
        return out


# ============================================================
# Example CLI
# ============================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Run paper workflow skill")
    parser.add_argument("--workflow", required=True, help="Path to workflow.yaml")
    parser.add_argument("--prompts", required=True, help="Path to agent_prompts.yaml")
    parser.add_argument("--state-json", help="Optional path to initial state JSON")
    parser.add_argument(
        "--stage",
        choices=["stage_1_foundation", "stage_2_manuscript", "stage_3_stresstest", "all"],
        default="all",
        help="Run a single stage or all stages",
    )
    args = parser.parse_args()

    skill = PaperWorkflowSkill.from_files(args.workflow, args.prompts)

    if args.state_json:
        with open(args.state_json, "r", encoding="utf-8") as f:
            initial_state = json.load(f)
        skill.set_initial_state(**initial_state)

    try:
        if args.stage == "all":
            result = skill.run_all()
        else:
            result = skill.run_stage(args.stage)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "history": skill.history}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
