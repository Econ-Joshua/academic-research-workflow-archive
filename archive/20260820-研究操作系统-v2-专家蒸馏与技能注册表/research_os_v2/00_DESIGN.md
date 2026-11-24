# Research OS v2.0 设计总图

## 关键纠偏

本版本以“真人专家工作蒸馏”为上游，而不是以“Agent逆向”为最终目标。Agent逆向只作为次级知识来源。

## 设计链

```text
真人专家
  ↓
Expert Practice Capture
  ↓
Workflow Reconstruction
  ↓
Decision Rule Extraction
  ↓
Boundary / Failure / Validation Extraction
  ↓
Candidate Skill
  ↓
Human Expert Review
  ↓
Validated Skill
  ↓
Skill Registry
  ↓
Method Router
  ↓
Model Router
  ↓
Runtime Router
  ↓
Validation
  ↓
Human Checkpoint
  ↓
Research Memory
```

## AWS方案可借鉴部分

- Client与后端模型解耦
- 统一入口/Proxy思路
- Task Router
- 不同任务使用不同后端模型
- 将应用层与模型服务层分离

但你的系统更进一步：AWS图主要做Model Routing；Research OS必须增加Method Routing、Skill Routing、Permission和Human Checkpoint。

## 核心技术栈

- GPT API / Claude API / Kimi API：认知引擎
- Hermes：通用执行Runtime
- Codex / Claude Code：工程Runtime
- Python / Stata / R：确定性分析Runtime
- PowerShell：启动和系统胶水
- VS Code：系统开发环境
- Skill Registry：研究方法资产库
- Evidence Store：证据基础设施
- Gateway：方法/模型/运行时调度
- Research Memory：长期积累

## 权限总原则

H0 Human Sovereignty
H1 Human Choice
H2 Human Approval
H3 Supervised Automation
H4 Full Automation

## 高权限资产

- Human Sovereignty
- Expert Distillation
- Skill Promotion / Deprecation
- Permission Policy
- Evidence Standard
- Research Memory Governance
