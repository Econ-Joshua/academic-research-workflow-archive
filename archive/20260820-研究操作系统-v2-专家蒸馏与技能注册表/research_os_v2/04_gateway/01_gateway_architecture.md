# Research Skill Gateway架构

## 核心原则

Gateway不是单纯Model Gateway，而是四级路由器：

```text
User Task
↓
Method Router
↓
Skill Router
↓
Model Router
↓
Runtime Router
↓
Validation Router
```

## 1. Method Router

识别当前任务属于：

- problem discovery
- knowledge discovery
- evidence
- theory
- empirical
- case
- policy
- economic history
- theoretical/formal
- adversarial
- communication

## 2. Skill Router

从Registry选择已验证的Skill；如果没有成熟Skill，必须升级为Human/Expert Distillation任务，而不是让Agent临时编一个规则作为“长期能力”。

## 3. Model Router

默认策略：

- GPT：理论、综合、红队、高价值判断
- Claude：长程分析、复杂工程、代码与复杂任务
- Kimi：批量阅读、中文、低成本高吞吐

具体模型以当期可用API和成本为准。

## 4. Runtime Router

- Hermes：通用电脑/浏览器/文件执行
- Codex / Claude Code：代码工程
- Python/Stata/R：确定性计算
- PowerShell：启动和系统胶水

## 5. Human Checkpoint

当Skill权限不足、出现冲突证据、核心研究决策或无法验证时，Gateway必须暂停并请求人工。
