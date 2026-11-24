# LOOP POLICY

## Core principle
The Research Loop belongs to the Research OS, not to any single model, desktop app, IDE, or Agent runtime.

Hermes, Codex, Claude Code, VS Code, PowerShell, and API calls are workers/interfaces that enter and exit the same persistent loop.

## Canonical loop
```text
PROJECT STATE
→ DIAGNOSE
→ SELECT NEXT BEST TASK
→ LOAD SKILL
→ PERMISSION GATE
→ ROUTE MODEL
→ ROUTE RUNTIME
→ EXECUTE
→ VALIDATE
→ UPDATE STATE
→
PASS → NEXT TASK
FAIL → BACKTRACK
HUMAN → DECISION PACKET
BLOCKED → REPLAN
DONE → CLOSE / DELIVER
```

## Invariants
### I1 Human Sovereignty
No autonomous commitment to H0 decisions.

### I2 Evidence Traceability
Important claims must trace to evidence or explicitly labeled inference.

### I3 Candidate/Permanent Separation
Unvalidated machine output cannot silently become permanent knowledge.

### I4 Validation Before Promotion
Artifacts are promoted only after required checks pass.

### I5 Backtrack Before Patch
Repair the earliest failed dependency rather than cosmetically editing downstream output.

### I6 State Persistence
Every meaningful task updates Project State.

### I7 Provenance
Record model, runtime, Skill version, source/evidence and task ID for important outputs.

### I8 Stop Safety
Stop when:
- human decision is required
- evidence is insufficient
- repeated attempts do not improve results
- authority boundary is hit
- permission/safety boundary is hit
- validation repeatedly fails

## Next-best-task policy
Choose the next task using:
1. research dependency
2. unresolved critical risk
3. expected information gain
4. contribution impact
5. evidence readiness
6. cost/time

Do not choose a task merely because it is easy.

## Repeated-failure policy
- first failure → diagnose and retry
- second failure → change method/tool/model or narrow scope
- third failure → escalate to human
- repeated systemic failure → update Skill or research design

## Completion policy
A stage is complete only when:
- required artifacts exist
- required validation passes
- no critical unresolved dependency remains
- human checkpoints are resolved

## Cross-runtime compatibility
Any runtime can execute a task if it can:
- read Project State
- read the referenced Skill
- produce the required artifact
- write the task record
- update state
- respect permission and validation rules

Compatible entry points:
- VS Code + API
- PowerShell + API
- Hermes Desktop/CLI
- Claude Code
- Codex
- other compliant runtimes

## Human as a runtime node
Human execution is a legitimate loop state:
Decision Packet → human decision → state update → resume.
