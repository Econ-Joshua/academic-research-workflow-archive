# Skill Registry Specification v1.0

## Skill字段

```yaml
skill_id:
name:
version:
status: candidate | validated | deprecated
layer:
scope:
source:
source_experts:
purpose:
trigger:
input:
output:
authority:
  level:
  human_checkpoint:
model_route:
tools:
workflow:
decision_rules:
boundary_conditions:
failure_modes:
validation:
stop_condition:
forbidden_actions:
evidence_requirement:
cost_tier:
memory:
change_log:
```

## Skill来源标签

允许：

- expert_distilled
- literature_derived
- agent_inspired
- user_defined
- empirical_validated

其中`expert_distilled`优先级最高，但仍需验证。

## Skill状态

Candidate → Validated → Production → Deprecated

禁止从Candidate直接进入Production。
