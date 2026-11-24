from __future__ import annotations

import json
from pathlib import Path

from paper_workflow_skill import PaperWorkflowSkill
from mock_agent_executor import MockAgentExecutor

BASE = Path('/mnt/data')


def main() -> None:
    skill = PaperWorkflowSkill.from_files(
        BASE / 'workflow.yaml',
        BASE / 'agent_prompts.yaml',
        agent_executor=MockAgentExecutor(),
    )

    with open(BASE / 'init_state.json', 'r', encoding='utf-8') as f:
        init_state = json.load(f)
    skill.set_initial_state(**init_state)

    # Run chain by chain
    skill.run_stage('stage_1_foundation')
    skill.run_stage('stage_2_manuscript')
    skill.run_stage('stage_3_stresstest')

    result = skill.snapshot()
    with open(BASE / 'mock_run_output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
