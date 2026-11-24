# TASK PROTOCOL

## Purpose
Every research action is a Task: the smallest meaningful unit that can be assigned to a Skill, executed by a model/runtime, validated, and written back to Project State.

## Task lifecycle
CREATE → ROUTE → PERMISSION CHECK → EXECUTE → OUTPUT → VALIDATE → UPDATE STATE → CLOSE / BACKTRACK / HUMAN CHECKPOINT

## Required fields
```yaml
task_id:
project_id:
function:
skill:
objective:
input:
expected_output:
authority:
model:
runtime:
validation_required:
stop_condition:
status:
created_at:
completed_at:
next_action:
```

## Function routing
F0 Problem Framing
F1 Paper Reading
F2 Knowledge Classification & Memory
F3 Memory Thinking / Association / Debate
F4 Research Design & Evidence Architecture
F5 Analysis / Inference / Empirical-Case Work
F6 Verification & Recursive Backtracking
F7 Argument / Paper Architecture
F8 Communication / Writing
F9 Publication / Decision Translation

## Authority
H0 Human Sovereign: research question, conceptual lens, mechanism commitment, contribution, evidence standard, final research design, narrative architecture, writing taste, journal positioning.
H1 Human Decision: AI proposes and attacks; human selects.
H2 Human Approval: AI builds an executable plan; human approves before execution.
H3 Supervised Automation: AI executes under predefined rules; human audits.
H4 Full Automation: deterministic/reversible/low-risk operations.

## Candidate vs Permanent
Unverified AI-generated insight, relation, hypothesis, extension, or question enters Candidate unless directly sourced and verified or explicitly accepted by the human.

## Output rules
Every Task produces:
1. artifact/output
2. validation record
3. state update
4. next-step recommendation

## Human checkpoint
For H0/H1 decisions, stop and produce a Decision Packet containing:
- decision needed
- alternatives
- evidence
- tradeoffs
- risks
- AI recommendation
- blank human decision field

Resume only after the decision is recorded.

## Backtracking
If validation fails, identify the earliest failed dependency and create a backtrack task. Do not silently patch only the final output.

## Idempotence
Completed tasks should be safe to rerun. Use versioned outputs and append-only logs.
