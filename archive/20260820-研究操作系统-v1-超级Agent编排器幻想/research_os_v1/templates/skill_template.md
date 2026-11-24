# Skill: <SKILL_NAME>

```yaml
skill_id: <ID>
name: <NAME>
version: 0.1
layer: <H/U/K/E/P/A/C>
scope: <UNIVERSAL/PARADIGM_SPECIFIC>
purpose: <PURPOSE>

authority:
  level: <H0-H4>
  human_checkpoint: <YES/NO>

input:
  - <INPUT>
output:
  - <OUTPUT>

trigger:
  - <TRIGGER>

model_route:
  primary: <MODEL>
  secondary: <MODEL>
  fallback: <MODEL>

tools:
  - <TOOL>

execution_mode: <MANUAL/AGENT/BATCH/ITERATIVE>

workflow:
  - <STEP>

validation:
  required: true
  checks:
    - <CHECK>

stop_condition:
  - <CONDITION>

forbidden_actions:
  - <ACTION>

evidence_requirement:
  - <REQUIREMENT>

cost_tier: <LOW/MEDIUM/HIGH>

memory:
  persist:
    - <MEMORY>

failure_recovery:
  - <RECOVERY>
```

## Notes

Write operational instructions below this line only after the YAML is stable.
