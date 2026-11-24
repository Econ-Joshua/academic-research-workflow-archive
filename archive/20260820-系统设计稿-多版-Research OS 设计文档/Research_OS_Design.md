# Research OS Design

> Version: v0.1
> Status: Core architecture frozen; implementation-ready blueprint
> Purpose: 建立一个以 Hermes 为 Research HQ、多个模型按认知角色协作、GPT Sol + Codex 承担研究执行，并与 Obsidian 操作流深度耦合的长期研究系统。

---

## 0. 核心定义

Research OS 不是一个“AI 写论文工具”，而是一个能够在多年研究过程中持续积累、讨论、发现、质疑、重构并复用研究知识的个人研究操作系统。

核心目标：

> **让 Agent 在完成一次研究后，不只是留下论文产出，还获得关于“如何研究”的新能力；让下一次研究继承上一轮的知识、判断、失败经验和方法。**

系统的核心循环为：

```text
新知识
  ↓
冲突识别
  ↓
知识连接
  ↓
理论重构 → 研究设计
  ↓
执行与新证据
  ↓
重新进入“新知识发现”
```

Reviewer Attack 贯穿整个循环，作为 epistemic quality control；Codex 负责把理论判断转化为可执行的研究任务。

---

# 1. 最终总体架构

```text
                             YOU
                    Research Director
                    Final Judgment
                             │
                             ▼
                 ┌────────────────────┐
                 │    HERMES HQ       │
                 │ Research Orchestrator│
                 └─────────┬──────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      Research State                 Research Memory
       当前研究状态                  长期研究记忆
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
              RESEARCH COGNITIVE LOOP

       ① 新知识发现
              ↓
       ② 冲突识别
              ↓
       ③ 知识连接
              ↓
       ④ 理论重构 → 研究设计
              ↓
           Execution
              ↓
        新证据 / 新知识
              └──────────────→ ①

                     ↑
              Reviewer Attack
        epistemic quality control

                           │
                           ▼
                  GPT Sol + Codex
                 Research Execution
                           │
                           ▼
                Evidence / Results
                           │
                           └────→ Hermes

                Obsidian = Knowledge UI
        每次操作同时产生 Research Event
```

---

# 2. 系统中的角色分工

## 2.1 Human：Research Director

人保留最终判断权，尤其负责：

- 研究方向
- 核心研究问题
- 什么是真正的 research gap
- 什么算理论创新
- 什么证据足以挑战既有理论
- 是否接受新知识
- 是否推翻 / 保留 / 重构理论
- 最终研究设计
- 最终论文判断
- 研究审美与理论标准

核心原则：

> **AI 可以扩大搜索、比较、推理和批判能力，但不能自动取得最终 epistemic judgment。**

---

## 2.2 Hermes：Research HQ

Hermes 不是普通 research assistant，而是：

- Research Orchestrator
- Research State Manager
- Memory Manager
- Model Router
- Skill Dispatcher
- Research Event Coordinator

Hermes 决定：

1. 当前研究处于什么状态；
2. 应触发哪个核心 Skill；
3. 应调用哪个模型；
4. 是否需要人类判断；
5. 是否产生新的 Research Event；
6. 是否更新 Obsidian / Memory / Research State；
7. 是否进入理论重构；
8. 是否生成 Execution Spec 交给 Codex。

---

## 2.3 多模型：认知角色层

模型不作为“唯一大脑”，而作为不同认知角色。

### GPT Sol

默认角色：**Theory Architect / Theory Judge**

适合：

- 核心理论推理
- 理论重构
- 新机制
- reviewer attack
- competing explanations
- 理论与研究设计的连接
- 最终高价值判断的辅助

### Kimi K3

默认角色：**Knowledge Synthesizer**

适合：

- 大规模论文阅读
- 长文档综合
- 跨论文比较
- literature synthesis
- claim / concept / mechanism 初步归纳
- 长上下文材料吸收

### GLM-5.3

默认角色：**Research Operator / Exploratory Agent**

适合：

- 长程任务执行
- 工具调用
- 补充检索
- 中间研究任务
- alternative explanation exploration

模型角色不是永久固定的，可通过 Model Router 动态切换。

---

## 2.4 Codex：Research Execution Layer

Codex 是 Research Factory，不是 Research HQ。

主要负责：

- Python
- Stata
- 数据清洗
- 数据转换
- 自动实验
- robustness
- replication
- table
- figure
- PDF / 文本处理
- 自动化脚本
- 日志和 reproducibility

Codex 的原则：

> **执行“为什么做”已经由 Hermes / Human / Theory Layer 决定的任务；Codex 负责“把它做出来”。**

Codex 接收标准化 `Execution Spec`。

---

# 3. Obsidian 的地位：不是资料仓库，而是 Research OS 的知识 UI

Obsidian 与 Research OS 不平行存在。

错误架构：

```text
Obsidian = 资料库
AI = 另一个系统
```

正确架构：

```text
Obsidian
   ↕
Research Event Layer
   ↕
Hermes
   ↕
Memory + Research State
   ↕
Models / Codex
```

核心原则：

> **每一次 Obsidian 操作同时都是研究事件；每一次重要研究判断都应反向更新 Obsidian。**

例如：

```text
发现论文
↓
进入 Inbox
↓
下载 / metadata / 创建 note
↓
初始分类 / 标签
↓
阅读 / Claim
↓
知识连接
↓
产生冲突
↓
理论讨论
↓
Theory v2
```

因此 Obsidian 的角色是：

- 知识可视化界面
- 人工研究操作界面
- Literature / Concept / Evidence / Theory 的长期承载层
- Research State 的可见界面

---

# 4. 已经明确可以自动化或复用的基础层

用户预设以下组件已经成熟，无需在 ResearchOS 的核心认知层重新开发：

## 4.1 已做好 Skill

- `发现论文 Skill`
- `初始分类 Skill`
- `阅读-Claim 提取 Skill`
- `Reviewer Attack`

## 4.2 已脚本化 / 应脚本化

- 下载归档
- 文件命名
- metadata
- PDF 处理
- 数据处理
- 文件移动 / 去重
- Obsidian note 创建
- 日志 / 备份
- Stata / Python 执行
- 表格 / 图形生成

原则：

> **确定性任务 → 脚本；重复性判断 → Skill；高价值研究判断 → Human + AI。**

---

# 5. Research Cognitive Loop：真正持续自我迭代的四个核心 Skill

ResearchOS 的核心认知能力不是几十个 Skill，而是四个递归型 Skill。

## 5.1 Skill 1：新知识发现 `new-knowledge-discovery`

### 核心问题

> 新材料中，有什么足以改变现有研究理解的东西？

不是“找到新论文”，而是发现：

- New Claim
- New Concept
- New Mechanism
- New Boundary Condition
- New Puzzle
- New Empirical Pattern
- New Counterexample

### 输入

- 新论文
- 新数据
- 新实证结果
- 新案例
- Reviewer criticism
- 既有 Research Memory

### 输出

结构化的 `New Knowledge Event`。

### 必须迭代的原因

什么值得称为“新知识”，高度依赖研究语境与个人理论标准，不能一次设计完成。

---

## 5.2 Skill 2：冲突识别 `conflict-detection`

### 核心问题

> 新知识是否真正挑战了当前知识 / 理论？

必须区分：

```text
difference
≠ tension
≠ contradiction
≠ theoretical failure
```

需要识别：

- measurement conflict
- boundary-condition conflict
- timing conflict
- rival mechanism
- construct conflict
- causal logic conflict
- ontology / conceptual conflict

### 输出

`Conflict Event`：

- 与什么冲突
- 冲突发生在哪一层
- 是否真实冲突
- 是否可能只是测量或语境差异
- 对 current theory 的威胁程度

---

## 5.3 Skill 3：知识连接 `knowledge-connection`

### 核心问题

> 新知识与旧知识连接后，是否产生了此前不存在的理论结构？

重点不是“相似”，而是：

> **有理论意义的 knowledge recombination。**

重点维护：

- Concept Graph
- Mechanism Graph
- Evidence Graph
- Theory Graph
- Cross-project links

例如：

```text
Absorptive Capacity
+
Knowledge Boundaries
+
Patient Capital
+
Scientific Research Evidence
        ↓
Selective Scientific Knowledge Reconfiguration
```

这个 Skill 是 ResearchOS 最可能产生原创理论价值的部分之一。

---

## 5.4 Skill 4：理论重构—研究设计 `theory-reconstruction-research-design`

这是最高阶 Skill。

逻辑：

```text
Old Theory
   ↓
Conflict
   ↓
Reconceptualization
   ↓
New Mechanism
   ↓
Boundary
   ↓
New Prediction
   ↓
Research Design
```

核心问题：

> 什么时候修补旧理论？什么时候推翻旧理论？什么样的新理论值得进入实证检验？

输出：

- Theory Version
- Mechanism
- Boundary conditions
- Predictions / hypotheses
- Distinguishing tests
- Research Design
- Execution Spec

这个 Skill 必须长期递归迭代。

---

# 6. Reviewer Attack 的位置

Reviewer Attack 不应被看作与四个核心 Skill 平行的第五个认知 Skill。

它是：

> **Epistemic Quality Control Layer**

贯穿四个核心 Skill：

### 对新知识发现

> 这个所谓的新知识到底是不是新？

### 对冲突识别

> 这是理论冲突，还是误读 / 测量差异？

### 对知识连接

> 这个 connection 是理论机制还是语言相似？

### 对理论重构

> 你只是换了说法，还是产生了真正不同的理论？

### 对研究设计

> 这个设计真的能区分新旧理论吗？

---

# 7. Research Memory 与 Research State 必须分开

## Research Memory

回答：

> **我们知道什么？**

建议长期结构：

```text
memory/
├── literature/
├── concepts/
├── evidence/
├── theories/
├── rejected-theories/
├── research-decisions/
├── open-questions/
├── reviewer-attacks/
└── cross-project-links/
```

尤其保留：

### `rejected-theories/`

目的：防止 Agent 反复返回已经被证伪 / 否定的解释。

例如：

```text
Theory v1
→ rejected
Reason: cannot explain selectivity

Theory v2
→ accepted provisionally
```

## Research State

回答：

> **我们现在在哪里？**

至少包含：

- Current RQ
- Current Contribution
- Current Theory
- Current Mechanism
- Current Evidence
- Current Contradictions
- Current Open Questions
- Current Risks
- Next Critical Decision

Research State 是动态的；Memory 是长期知识。

---

# 8. Human-Derived Skills：真正必须从人类蒸馏的部分

不要把所有 Skill 都自研。

真正需要从研究者本人蒸馏的，是研究判断规则。

核心至少四类：

## H1 研究判断标准

- 什么算真正的 research gap
- 什么算理论创新
- 什么证据值得改变理论
- 什么 reviewer criticism 是致命的
- 什么理论是“漂亮 / 顶刊级”的

## H2 四个核心递归 Skill 的个人规则

从真实研究过程蒸馏：

- 你如何发现新知识
- 你如何判断冲突
- 你如何产生跨文献连接
- 你如何决定重构理论

## H3 研究后记忆蒸馏

每次出现以下事件，都应该记录 `human-distillation-episode`：

```text
AI proposed X
↓
你觉得哪里不对
↓
你注意到了什么
↓
什么证据改变了判断
↓
为什么选择 Y
```

多个 episode 才逐渐抽象成个人 Skill。

---

# 9. 哪些能力借鉴他人，哪些自己做

## 可以直接借鉴 / 适配

- 通用 literature review
- PDF parsing
- citation audit
- 通用 research paper workflow
- Git / Codex workflow
- 基础 Python / Stata workflow
- 文件管理
- 一般性 academic research skills

原则：

> **工程能力、通用流程、成熟工具优先借鉴。**

## 必须自研 / 人类蒸馏

- research-question formulation
- theory-gap detection
- novelty detection
- epistemic conflict detection
- knowledge connection
- theory reconstruction
- research-memory curation
- cross-project recombination
- research taste / theoretical aesthetics
- model routing rules

原则：

> **个人研究判断是核心 intellectual asset，不应该直接复制他人。**

---

# 10. 哪些必须多轮迭代

## 必须递归改进

1. `new-knowledge-discovery`
2. `conflict-detection`
3. `knowledge-connection`
4. `theory-reconstruction-research-design`
5. `novelty-detection`
6. `research-memory-curation`
7. `cross-project-recombination`
8. `reviewer-attack`
9. `model-routing`

这些都不应该追求 v1.0 一次定型。

## 可以较快稳定

- PDF extraction
- metadata
- 文件归档
- citation format / audit
- 基础数据清洗
- Stata / Python 常规执行
- 文件转换
- 日志 / 备份

---

# 11. 完整的人机操作流

用户实际操作被压缩为少数高价值动作。

```text
① 发现 / 收集论文
    ↓
② 放入 Obsidian Inbox
    ↓
③ AI 自动分类 / 初标
    ↓
④ 人快速确认标签与 relevance
    ↓
⑤ AI 阅读 / Claim 提取
    ↓
⑥ Hermes 与 Research Memory 比较
    ↓
⑦ 新知识发现
    ↓
⑧ 冲突识别
    ↓
⑨ 知识连接
    ↓
⑩ 人 + GPT Sol 做理论判断
    ↓
⑪ 理论重构 / 研究设计
    ↓
⑫ 生成 Execution Spec
    ↓
⑬ Codex 执行
    ↓
⑭ Evidence / anomaly
    ↓
⑮ 返回 Hermes
    ↓
⑯ Reviewer Attack
    ↓
⑰ 必要时再次理论重构
    ↓
⑱ 更新 Memory / Research State / Obsidian
    ↓
⑲ 进入下一轮
```

---

# 12. 人、AI Skill、脚本、Agent 的严格边界

| 工作 | Human | AI Skill | Script | Hermes | Codex |
|---|---:|---:|---:|---:|---:|
| 研究方向 | **核心** | 辅助 |  |  |  |
| 研究问题 | **核心** | 辅助 |  | 调度 |  |
| 论文发现 |  | ✅ | ✅ | ✅ |  |
| 下载归档 |  |  | **✅** |  |  |
| metadata |  |  | **✅** |  |  |
| 初始分类 |  | **✅** |  | ✅ |  |
| 标签最终确认 | **✅** | 建议 |  |  |  |
| Claim 提取 |  | **✅** |  | ✅ |  |
| 新知识发现 | **高** | **✅** |  | ✅ |  |
| 冲突识别 | **高** | **✅** |  | ✅ |  |
| 知识连接 | **高** | **✅** |  | ✅ |  |
| 理论重构 | **极高** | **✅** |  | ✅ |  |
| 研究设计 | **极高** | ✅ |  | ✅ |  |
| 数据处理 | 低 |  | **✅** |  | ✅ |
| Stata / Python | 低 |  | ✅ |  | **✅** |
| 实证解释 | **高** | **✅** |  | ✅ | ✅ |
| 初稿 | **中** | **✅** |  | ✅ |  |
| Reviewer Attack | **裁判** | **✅** |  | ✅ |  |
| 最终理论 | **最终判断** | 辅助 |  |  |  |

原则：

> **确定性任务 → Script**
>
> **重复性判断 → Skill**
>
> **研究协调 → Hermes**
>
> **高价值认知 → Human + 多模型**
>
> **研究执行 → Codex**

---

# 13. Obsidian 与 Research Loop 的耦合规则

每个研究事件至少能产生一种可持久化结果：

```text
Paper
→ Literature Note
→ Claim
→ Concept
→ Relation
→ Conflict
→ Theory Version
→ Evidence
→ Research Decision
```

反过来，任何重要的 Obsidian 更新都可能成为 Hermes 的触发器：

- 新论文进入 Inbox
- 新 Claim 创建
- 新 Concept 创建
- 两个 Concept 建立关系
- Conflict 被标记
- Theory Version 更新
- Evidence 更新
- Rejected Theory 新增

从而触发相应 Skill。

---

# 14. Standard Research Event

所有核心认知事件都应采用统一事件结构，最低包含：

```yaml
event_id:
project_id:
timestamp:
event_type:
source:
input_objects:
old_state:
new_finding:
confidence:
related_concepts:
related_theories:
conflicts:
human_judgment_required:
decision:
next_action:
memory_updates:
```

`event_type` 至少包含：

- `new-knowledge`
- `conflict`
- `connection`
- `theory-reconstruction`
- `research-design`
- `evidence`
- `reviewer-attack`
- `research-decision`

---

# 15. Theory Versioning

理论不能被覆盖，只能版本化。

```text
Theory v1
↓
Theory v1.1
↓
Theory v2
↓
Theory v3
```

每个版本必须说明：

- What changed
- Why changed
- What old explanation was rejected
- What new mechanism emerged
- What new predictions emerged
- What remains unexplained

这使 ResearchOS 能够回答：

> **为什么 v3 比 v2 更好？**

---

# 16. Execution Spec

理论一旦进入可检验阶段，Hermes 将其转换为 Codex 可执行规格。

标准结构：

```yaml
experiment_id:
research_question:
claim:
hypothesis:
prediction:
data:
sample:
variables:
model:
tests:
robustness:
falsification:
deliverables:
interpretation_rules:
anomaly_rules:
```

关键原则：

> Codex 不负责偷偷改变理论以追求显著结果。

任何结果异常都必须返回 `Evidence / Anomaly Report`。

---

# 17. Evidence Feedback Loop

理论预测与实际结果发生偏离时：

```text
Prediction
↓
Execution
↓
Unexpected Result
↓
Anomaly Report
↓
Hermes
↓
Conflict Detection
↓
Knowledge Connection
↓
Theory Reconstruction
```

不能把失败结果简单标成 `FAIL`。

它可能意味着：

- measurement problem
- timing problem
- heterogeneity
- omitted mechanism
- boundary condition
- theory failure

因此实证异常本身是 New Knowledge。

---

# 18. Writing Loop

写作不是一次性生成，而是：

```text
Knowledge
↓
Argument
↓
Section
↓
Reviewer Attack
↓
Rewrite
↓
Theory Check
```

正文中的关键 claim 应可追溯至：

```text
Claim
↓
Concept
↓
Literature / Evidence
↓
Theory
```

最终应支持：

- Claim–Evidence Audit
- Claim–Citation Audit
- Theory–Evidence Consistency Audit
- Reviewer-risk audit

---

# 19. ResearchOS 的真正复利机制

系统的目标不是：

> “第一篇论文写得多快。”

而是：

> **第一篇论文完成后，ResearchOS 比第一篇开始之前更会做研究。**

每次研究结束后必须做 Research Postmortem：

- 哪些判断正确
- 哪些判断错误
- 哪个 Skill 失败
- 哪个 Skill 成功
- 哪些步骤浪费时间
- 哪些 human judgment 可以被蒸馏
- 哪些 memory 应长期保留
- 哪些规则应该更新

形成：

```text
Research Episode
↓
Postmortem
↓
Skill Update
↓
Memory Update
↓
ResearchOS v(n+1)
```

---

# 20. Skill 生命周期

所有核心 Skill 均采用递归版本管理：

```text
S0 观察
↓
S1 人工蒸馏
↓
S2 Skill v0.1
↓
S3 真实研究使用
↓
S4 记录失败案例
↓
S5 Skill v0.2
↓
S6 多论文验证
↓
S7 Skill v1.0
↓
S8 周期性重构
```

尤其是四个核心 Cognitive Skills，不能一次定型。

---

# 21. ResearchOS v0.1 的实际建设顺序

## Phase 1：基础状态与界面

1. Obsidian 目录与 Properties
2. Literature Inbox
3. Research State
4. Memory Schema
5. Research Event Schema
6. Theory Version Schema

## Phase 2：基础自动化

7. 下载归档
8. metadata
9. 文件命名 / 去重
10. Obsidian note 自动创建
11. reading queue

## Phase 3：四个核心 Skill

12. new-knowledge-discovery
13. conflict-detection
14. knowledge-connection
15. theory-reconstruction-research-design

## Phase 4：循环质量控制

16. Reviewer Attack integration
17. Evidence / anomaly feedback
18. Memory curation
19. Rejected Theory memory

## Phase 5：Codex Execution

20. Execution Spec
21. Stata/Python integration
22. Evidence Pack
23. 自动 anomaly report

## Phase 6：Research Capability Compounding

24. Research Postmortem
25. Human Distillation Episodes
26. Skill versioning
27. Cross-project recombination
28. Model Router optimization

---

# 22. 当前已经确定的最简版本

ResearchOS 并不需要几十个递归 Skill。

基础生产流已经存在：

```text
发现论文
→ 初始分类
→ 阅读 / Claim 提取
→ Reviewer Attack
→ 下载 / metadata / 数据处理脚本
```

真正需要持续自我迭代的只有四个核心认知 Skill：

```text
① 新知识发现
② 冲突识别
③ 知识连接
④ 理论重构 → 研究设计
```

以及两个非认知基础设施：

```text
Research Memory Update
Research State Management
```

最终形成：

```text
       新知识发现
             ↓
       冲突识别
             ↓
       知识连接
             ↓
   理论重构 → 研究设计
             ↓
        Codex 执行
             ↓
       新证据 / 新知识
             ↓
             ↺
```

Reviewer Attack 横跨整个链条。

---

# 23. 最终原则

### Principle 1 — 不追求万能 Agent

ResearchOS 是一个多模型、多 Skill、多阶段的研究系统，而不是一个万能 prompt。

### Principle 2 — 工程能力借用，研究判断自研

能从 GitHub、成熟 Skill 和工具获得的通用工程能力，不重复造轮子。

### Principle 3 — Human judgment 是核心资产

最终研究判断、理论审美、贡献标准和推翻/重构理论的规则必须从真人研究过程中蒸馏。

### Principle 4 — Memory 不等于聊天记录

真正值得长期保存的是：

- 认知变化
- 研究决策
- 被否定的理论
- 新概念
- 新机制
- 新证据
- 跨项目连接

### Principle 5 — Research State 不等于 Memory

Memory = 我们知道什么。

Research State = 我们现在在哪里。

### Principle 6 — 失败结果是知识

Empirical failure、Reviewer criticism 和理论反例都是可能的新知识，不能简单丢弃。

### Principle 7 — 不覆盖理论，版本化理论

每次重大理论变化都必须留下可追溯路径。

### Principle 8 — 每一轮研究都应该提高下一轮 ResearchOS 的能力

最终形成：

> **Research → Postmortem → Skill → Memory → Better Research**

这才是 ResearchOS 的核心价值。

---

# 24. One-line Definition

> **ResearchOS 是一个以 Hermes 为研究中枢、以 Obsidian 为知识与研究状态界面、以多模型承担不同认知角色、以 GPT Sol + Codex 承担研究执行，并通过“新知识发现 → 冲突识别 → 知识连接 → 理论重构/研究设计 → 新证据”递归循环，使个人研究知识、判断规则和研究能力持续复利的长期 Research Operating System。**
