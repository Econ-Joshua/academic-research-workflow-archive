# Expert Practice Distillation：真人专家工作蒸馏方法

## 1. 定义

这里的“蒸馏”不是传统机器学习里的teacher-student model distillation，而是Expert Practice Distillation：

> 从真人专家的真实工作实践中提取可迁移的隐性知识、判断规则和操作程序，将其显性化、结构化、验证后编译成Reusable Skill。

## 2. 蒸馏目标

不要蒸馏“专家说了什么”，而要蒸馏：

1. 专家试图完成什么目标
2. 他看哪些输入
3. 他先做什么、后做什么
4. 哪些节点需要判断
5. 什么证据会让他改变路径
6. 什么情况下跳过某一步
7. 什么情况下换方法
8. 什么情况下认为“已经足够”
9. 什么情况属于危险的误判
10. 怎样验证自己没有犯错

## 3. D0：专家实践采集

优先材料：

- 专家本人写的工作总结
- 专家对自己工作过程的详细复盘
- 屏幕录制/操作记录
- 方法论文章
- 案例讲解
- 专家对失败案例的解释
- 同一专家在多个相似任务上的工作比较

不要只采集最终答案。

## 4. D1：Workflow Reconstruction

从材料中重建：

```text
Goal
↓
Input
↓
Initial Scan
↓
Decision Node
├─ Condition A → Action A
├─ Condition B → Action B
└─ Condition C → Stop/Ask Human
↓
Validation
↓
Output
```

## 5. D2：提取Decision Rules

每条规则用以下形式记录：

> IF [可观察条件] → THEN [专家动作] BECAUSE [判断依据] UNLESS [边界条件]

例如：

> IF 文献只是关键词相似但理论问题不同 → THEN 不纳入主文献池 → BECAUSE 主题相似不等于理论相关 → UNLESS 它提供了竞争机制。

## 6. D3：区分三类知识

### Principle
更高层的原理。

### Heuristic
专家长期经验形成的经验规则。

### Procedure
可以按步骤执行的操作流程。

只有Procedure已经稳定、且Heuristic能被明确表达时，才适合直接编译成Skill。

## 7. D4：提取Boundary / Failure / Verification

必须记录：

- 什么时候这个方法不适用
- 最常见误区
- 专家如何识别错误
- 什么时候停止
- 什么时候上升到更高权限并咨询人

## 8. D5：形成Candidate Skill

Candidate Skill必须包含：

- purpose
- trigger
- input
- workflow
- decision rules
- tools
- model route
- authority
- forbidden actions
- validation
- stop condition
- exceptions
- output schema

## 9. D6：人工专家审核

原则：

> Skill不能由模型自己宣布“蒸馏成功”。

至少由你或原专家回答：

- 是否准确反映专家原意？
- 是否误把个体习惯当成通用规则？
- 是否过度泛化？
- 是否遗漏关键例外？
- 是否能迁移到第二个任务？

## 10. D7：验证与版本化

至少使用两个不同案例验证Candidate Skill。

记录：

- 成功条件
- 失败条件
- 人工修正
- 适用边界
- v0.1 → v0.2 → v1.0变更记录

只有经过验证的Skill才能进入`validated_skills/`。
