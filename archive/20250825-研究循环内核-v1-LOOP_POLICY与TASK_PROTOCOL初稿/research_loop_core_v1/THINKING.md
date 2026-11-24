# 本对话最终核心思路 v1.0

## 一、总目标
建立一个 Personal Research OS，不是“一个超级Agent”，而是一套能够长期生产高水平论文、案例研究、政策分析、经济史研究及研究报告的研究基础设施。

核心不是自动写作，而是：
- 将研究劳动拆成可治理的功能；
- 将真人专家实践蒸馏成可复用Skill；
- 将Knowledge、Evidence、Argument、Validation形成持久化闭环；
- 将模型、Agent、桌面应用降级为可替换执行资源；
- 将关键学术判断权留在人。

## 二、最重要的架构原则
### Human sovereignty
研究问题、理论lens、机制、贡献、证据标准、研究设计commitment、叙事、写作taste、期刊定位默认由人最终决定。

### Method before model
先判断需要什么方法动作，再选择Skill、模型与Runtime。

### Skill before automation
先形成经过验证的Skill，再自动化；不要让Agent凭空发明研究流程。

### Expert-driven skill generation
核心能力优先来自：真人专家实践 → 专家实践蒸馏 → Skill → Agent执行。
Agent机制只能作为次级来源。

### Memory is not chat history
Memory是经过提炼、验证、可复用的Research Knowledge，而不是聊天记录堆积。

### Candidate vs permanent
AI生成的关系、Insight、理论延伸、问题先进入Candidate；验证或人工确认后才进入Permanent Knowledge。

### Loop is external to runtime
Research Loop由持久化Project State + Task Protocol + Loop Policy定义，不绑定Hermes、VS Code、Codex等入口。

### Backtracking is first-class
验证失败应找到最早失效节点并回溯。

## 三、六大核心功能
### F1 读论文
四通道：Skill extraction / Human reading / AI dialogue / Cross-memory association；随后Research Synthesis + Meta-reflection。

### F2 分类、存储、形成记忆
Obsidian保存：Paper / Concept / Theory / Mechanism / Method / Evidence / Insight / Question / Project / Research Memory。
标签描述稳定属性；关系表达知识结构。

### F3 深度思考、联想、辩论
围绕Memory：association / contradiction / extension / reframing / rival explanation / theory attack / new-question generation。

### F4 论文结构设计
RQ → Puzzle → Theory → Mechanism → Boundary → Evidence Architecture → Research Design → Claim/Evidence → Contribution → Narrative。

### F5 实证/案例研究
统一抽象：Claim → Evidence → Identification/Explanation → Test → Validation。
不同范式是不同Method Pack。

### F6 核查、回溯、自检
Claim → Evidence → Logic → Alternative Explanation → Verification；失败则回溯。

## 四、完整Research Lifecycle
为了生产各种论文/报告，还需要：
F0 Problem Framing
F4 Research Design & Evidence Architecture
F5 Analysis / Inference
F8 Communication / Writing
F9 Publication / Decision Translation

完整链条：
Problem → Question → Explanation → Evidence → Inference → Claim → Validation → Communication。

## 五、专家蒸馏
专家实践不直接变成Prompt。
Practice Capture → Workflow Reconstruction → Decision Rules → Heuristics → Boundaries → Failure Modes → Validation Rules → Stop Conditions → Skill Formalization → Expert Review → Validated Skill。

## 六、Gateway
Task → Function → Skill → Permission → Model → Runtime → Validation → Human Checkpoint → Memory。

模型角色：
- GPT：高价值理论、综合、攻击
- Claude：长程分析、复杂工程
- Kimi：高吞吐、中文、批量

Runtime角色：
- Hermes：浏览器/文件/电脑执行
- Codex/Claude Code：代码工程
- Python/Stata/R：确定性计算
- PowerShell：启动和系统级胶水

## 七、Paper Reading的核心成果
每篇核心论文不是一个摘要，而是四通道Research Knowledge Object：
1. Skill Extraction
2. Human Reading
3. AI Dialogue
4. Cross-Memory Association

然后：
Research Synthesis → Meta-Reflection → Research Memory。

## 八、长期资产
真正的复利资产不是某个模型或桌面应用，而是：
Expert Practice → Distilled Skill → Knowledge → Project Memory → Research Insight → Workflow → Validation。

## 九、最终Loop
```text
Project State
→ Diagnose
→ Select Next Best Task
→ Skill
→ Permission
→ Model
→ Runtime
→ Execute
→ Validate
→ State Update
→ Next Task
```
允许：
PASS → 继续
FAIL → 回溯
HUMAN → 人决策
BLOCKED → 重规划
DONE → 交付/归档

## 十、最重要的系统观点
目标不是“让Agent一直工作”，而是“让研究过程本身持续工作”。

Agent是可替换劳动力；
Model是可替换认知引擎；
Skill是可积累的方法；
Memory是可积累的知识；
Project State是持久状态；
Loop是研究系统的时间结构；
Human是最终学术主权者。
