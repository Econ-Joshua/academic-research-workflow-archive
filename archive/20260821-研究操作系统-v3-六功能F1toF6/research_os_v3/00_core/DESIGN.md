# Research OS v3.0 Design

## 一、设计目标
这不是“万能Agent”，而是围绕六项高价值研究活动建立的个人Research OS。

## F1 读论文
四通道并行：
A. Skill Extraction：真人专家蒸馏出的读论文方法。
B. Human Reading：本人肉眼阅读、批注、怀疑、直觉、灵感。
C. AI Dialogue：基于论文的批判、拓展、反事实、竞争解释。
D. Cross-Memory Association：与既有论文、概念、理论、机制、方法、项目记忆建立关系。
最终进入Research Synthesis和Meta-Reflection。

## F2 分类、存储、记忆
Obsidian作为知识层。Paper不是唯一对象；知识对象包括Paper/Concept/Theory/Mechanism/Method/Evidence/Insight/Question/Project/Memory。
Tags用于稳定属性；Links用于智识关系；AI候选关系先进入Candidate区。

## F3 记忆深度思考与辩论
不是围绕单篇论文聊天，而是调用Research Memory进行聚类、矛盾检测、理论重构、竞争解释、方法迁移和研究问题生成。

## F4 论文结构设计
RQ → Puzzle → Lens → Mechanism → Boundary → Evidence Architecture → Research Design → Result/Claim Mapping → Contribution → Narrative Architecture。
AI生成多个架构并攻击；人最终选择。

## F5 实证/案例研究
统一为Claim → Evidence → Method/Identification → Analysis → Validation。
实证：measurement / identification / estimation / mechanism / heterogeneity / robustness。
案例：case selection / boundary / evidence / coding / process tracing / comparison / rival explanation。

## F6 递归核查
Claim → Evidence → Logic → Alternative Explanation → Verification。失败时回溯到最早失效节点，而不是只修最后输出。

## 人机分工
Human：研究问题、理论Lens、核心机制、贡献、证据标准、最终设计、叙事和投稿。
Top models：综合、攻击、辩论、复杂推理。
Work models：批量阅读、提取、分类。
Runtime：Hermes=电脑/浏览器/文件；Codex/Claude Code=工程；Python/Stata/R=确定性计算；PowerShell=启动和系统胶水。

## 调度
Task → Function → Skill → Permission → Model → Runtime → Validation → Human Checkpoint → Memory。

## 关键原则
- Method before Model
- Human sovereignty
- Candidate vs Permanent knowledge
- Validation is mandatory
- Backtracking is first-class
- Memory is not chat history
