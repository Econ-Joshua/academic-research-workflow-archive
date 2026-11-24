# Personal Research OS — Design v1.0

## 0. 定位

这是一个以“人类学术主权”为最高原则的 Personal Research OS（个人研究操作系统）。

核心目标不是让 AI 替代研究者，而是把研究过程拆解为：

> 问题发现 → 知识发现 → 证据获取 → 证据处理 → 理论/解释 → 研究设计 → 分析 → 验证/攻击 → 沟通与投稿

并把其中可重复、可验证、可规模化的部分固化为 Skills，由 Agent Runtime 执行；把决定研究质量、深度、逻辑、taste 和投稿层次的判断保留给人。

---

## 1. 核心设计原则

### 1.1 Human Sovereignty

凡是会改变下列对象的决定，默认属于 Human Sovereignty：

- Research Question
- Problem Significance
- Conceptual Lens
- Core Mechanism
- Contribution Positioning
- Evidence Standard
- Research Design Commitment
- Narrative Architecture
- Writing Taste
- Journal Positioning

AI可以搜索、生成候选方案、比较、攻击、模拟审稿人，但不得未经授权自动 commit。

### 1.2 Separate Intelligence from Execution

模型、Skill、Agent Runtime、Orchestrator、Tool 不属于同一层：

- Model：推理能力
- Skill：方法/程序知识
- Agent Runtime：执行循环、工具调用、上下文、权限、状态
- Orchestrator：任务拆解、路由、调度和转交
- Tool：浏览器、文件系统、Python、Stata、Web API 等
- Human：最终学术判断与价值排序

### 1.3 Skill First, New Tool Second

如果一个能力能够通过 instructions + 现有工具完成，优先做 Skill，不先开发新 Tool。

只有当已有工具和 Skill 不足以完成能力时，才开发新工具。

### 1.4 Evidence First

研究 Agent 的基本单位不是“答案”，而是 Claim–Evidence–Reasoning 三元组。

任何重要结论都应该尽量能追溯到：

- 来源
- 原文/数据位置
- 推理路径
- 验证状态

### 1.5 Attack before Commit

高价值研究判断优先采用：

> Candidate → Attack → Rival Explanation → Human Choice → Commit

而不是：

> Generate → Accept

### 1.6 Cheap Models for Throughput, Frontier Models for Judgment

预算约 400 元/月的模型层建议采用：

- GPT API：高价值理论、综合、攻击、关键研究设计讨论
- Claude API：复杂长程分析、工程/代码、复杂 review
- Kimi Allegretto：高吞吐阅读、批处理、中文材料和重复工作

模型路由按任务价值和不确定性决定，而不是按模型品牌固定分工。

### 1.7 API as Cognitive Backbone, Agent Runtime as Action Layer

长期生产架构：

> API → Orchestrator → Skill → Agent Runtime → Tools → Evidence/State

PowerShell 是启动器和系统级胶水；长期运行的编排逻辑应放在 Python/Orchestrator，而不是堆在 PowerShell 脚本里。

---

## 2. 从 AWS 图可以借鉴什么

给定 AWS 方案的关键结构是：客户端与模型服务解耦；统一 Proxy/Endpoint；Task Router；后端多个模型服务。

### 2.1 Unified Endpoint

借鉴“LiteLLM Proxy Endpoint”的思想：

> 上层客户端不直接绑定某个模型供应商，而是通过统一 API 入口访问 Model Router。

在 Personal Research OS 中对应：

```text
Hermes / VS Code / PowerShell / 自建 Agent
                ↓
        Unified Model Gateway
                ↓
        GPT / Claude / Kimi
```

优点：

- 随时替换模型
- 统一日志
- 统一密钥管理
- 统一成本统计
- 统一模型路由
- 避免每个 Skill 写一套供应商 API

第一版可以先不部署真正的 Proxy，使用 Python wrapper；架构上保留 Gateway 接口。

### 2.2 Task Router

AWS 图中“主线任务/支线任务”的思想值得直接吸收，但需要升级成 Research Task Router：

- 主线任务：理论、核心研究设计、核心分析、论文主线
- 支线任务：检索、整理、抽取、标注、格式化、重复分析

进一步按照 Human Authority 和 Task Value 做路由，而不只是“复杂/简单”。

### 2.3 Client / Model Decoupling

客户端不是模型。Claude Code、Hermes、Kimi Desktop、VS Code、PowerShell 可以共享同一 Model Gateway。

这样以后换模型，不必重做 Skill。

### 2.4 Backend Model Pool

不建立“一模型一 Agent”的固定关系，而建立 Model Pool + Routing Policy：

```text
High-value judgment → frontier model
High-volume processing → Kimi / lower-cost model
Coding → coding-capable model/runtime
Deterministic computation → Python/Stata/R
```

### 2.5 Enterprise Boundary → Research Security Boundary

AWS 用 VPC 划安全边界。个人 Research OS 可以对应：

- API Keys / .env
- 私有 research workspace
- 原始数据目录
- evidence store
- audit log
- tool permission

以后如果接敏感数据，可进一步把“高敏数据区”和“普通材料区”隔离。

### 2.6 不照搬的部分

AWS 图是服务基础设施架构，不是研究方法架构。因此不要照搬：

- 企业 VPC 复杂网络
- 云厂商服务层级
- 模型产品作为固定业务模块

你的系统的独特核心应该是：

> Human Sovereignty + Skill Registry + Evidence Architecture + Validation + Research Orchestration

---

## 3. 六层总体架构

```text
L0 HUMAN SOVEREIGNTY
    问题 / 理论 / 贡献 / 证据标准 / 选择 / Taste / 投稿

L1 COGNITIVE COLLABORATION
    Theory / Strategy / Synthesis / Attack / Alternatives

L2 RESEARCH ORCHESTRATION
    Task Router / Skill Router / Model Router / State / Checkpoints

L3 RESEARCH SKILLS
    Universal / Theory / Evidence / Paradigm / Adversarial / Communication

L4 EXECUTION ENGINES
    Hermes / Claude Code / Codex / Python / Stata / R / Browser

L5 INFRASTRUCTURE
    Unified Model Gateway / PowerShell / Files / Git / Storage / Logs
```

---

## 4. Permission Model

| Level | 名称 | AI 行为 | 人类角色 |
|---|---|---|---|
| H0 | Human Sovereign | 只能分析、建议、攻击 | 最终决定 |
| H1 | Human Decide | 生成并比较多个方案 | 选择方案 |
| H2 | Human Approve | 先生成完整方案 | 审批后执行 |
| H3 | Supervised Automation | 自动执行 | 抽查/验收 |
| H4 | Full Automation | 自动执行 | 仅异常/结果验收 |

---

## 5. Skill Registry 标准字段

每个 Skill 应包含：

```yaml
skill_id:
name:
version:
layer:
scope:
purpose:
input:
output:
trigger:
authority:
model_route:
tools:
execution_mode:
workflow:
validation:
stop_condition:
forbidden_actions:
evidence_requirement:
cost_tier:
memory:
failure_recovery:
output_schema:
```

### 三个特别重要的治理字段

1. forbidden_actions：明确 Agent 永远不能做什么。
2. stop_condition：明确什么时候必须停止。
3. validation：明确怎样证明自己做对了。

---

## 6. Skill Taxonomy v1.0

### H — Human Sovereignty

- H01 Research Question Selection
- H02 Conceptual Lens Selection
- H03 Mechanism Commitment
- H04 Contribution Positioning
- H05 Evidence Standard
- H06 Research Design Commitment
- H07 Narrative Architecture
- H08 Writing Taste
- H09 Journal Positioning

### U — Universal Research

- U01 Literature Discovery
- U02 Citation Chaining
- U03 Source Verification
- U04 Document Extraction
- U05 Classification & Tagging
- U06 Deduplication
- U07 Entity Resolution
- U08 Document Versioning

### K — Knowledge & Theory

- K01 Concept Definition
- K02 Concept Comparison
- K03 Theory Mapping
- K04 Mechanism Generation
- K05 Mechanism Attack
- K06 Rival Explanation Generation
- K07 Theory Integration
- K08 Theory Consistency Audit

### E — Evidence

- E01 Evidence Discovery
- E02 Evidence Acquisition
- E03 Evidence Extraction
- E04 Evidence Coding
- E05 Evidence–Claim Mapping
- E06 Source Triangulation
- E07 Chronology Reconstruction

### PE — Empirical

- PE01 Measurement
- PE02 Variable Construction
- PE03 Identification Strategy
- PE04 Estimation
- PE05 Heterogeneity
- PE06 Robustness
- PE07 Mechanism Testing
- PE08 Alternative Specification

### PC — Case

- PC01 Case Discovery
- PC02 Case Selection
- PC03 Case Boundary
- PC04 Material Acquisition
- PC05 Coding
- PC06 Within-Case Analysis
- PC07 Process Tracing
- PC08 Cross-Case Comparison
- PC09 Rival Explanation

### PP — Policy

- PP01 Policy Discovery
- PP02 Policy Versioning
- PP03 Policy Timeline
- PP04 Institutional Mapping
- PP05 Actor Mapping
- PP06 Implementation Analysis
- PP07 Policy Comparison
- PP08 Policy Evaluation
- PP09 Counterfactual Policy Analysis

### PH — Economic History

- PH01 Archive Discovery
- PH02 Archive Retrieval
- PH03 Source Classification
- PH04 Chronology
- PH05 Actor Mapping
- PH06 Institutional Genealogy
- PH07 Source Triangulation
- PH08 Causal Reconstruction
- PH09 Counterfactual Reconstruction

### PT — Theoretical/Formal

- PT01 Assumption Generation
- PT02 Formalization
- PT03 Model Construction
- PT04 Proposition Generation
- PT05 Comparative Statics
- PT06 Boundary Conditions
- PT07 Internal Consistency

### A — Adversarial / Validation

- A01 Theory Red Team
- A02 Evidence Red Team
- A03 Method Red Team
- A04 Measurement Red Team
- A05 Alternative Explanation
- A06 Reviewer #1
- A07 Reviewer #2
- A08 Reviewer #3
- A09 Editor Simulation
- A10 Journal Fit Attack

### C — Communication

- C01 Outline Drafting
- C02 Paragraph Drafting
- C03 Literature Integration
- C04 Compression
- C05 Clarity Revision
- C06 Consistency Check
- C07 Citation Audit
- C08 Abstract Optimization
- C09 Introduction Architecture
- C10 Discussion Architecture
- C11 Reviewer Response

---

## 7. Orchestrator Design

Orchestrator 是“任务调度器”，不是“万能模型”。

职责：

1. 解析目标
2. 判断研究阶段
3. 判断研究范式
4. 找到匹配 Skill
5. 判断 Human Authority
6. 选择 Model Route
7. 选择 Runtime/Tool
8. 执行并保存状态
9. 触发 Validation
10. 在 H0/H1/H2 checkpoint 停下来交给人
11. 记录 Audit Trail
12. 结束后决定是否把经验沉淀为新 Skill

推荐第一版：Python Orchestrator + PowerShell launcher。

PowerShell 负责启动、环境变量、快捷命令和系统级调用；Python 负责实际路由。

---

## 8. Model Router

### GPT API

默认：
- 高价值理论综合
- 核心机制攻击
- Rival explanations
- 核心研究设计讨论
- 高价值 reviewer simulation
- Evidence–Claim reasoning

### Claude API

默认：
- 长程复杂分析
- 复杂代码工程
- 项目级 review
- 长上下文重构

### Kimi Allegretto

默认：
- 大规模文献初筛
- 中文材料
- 批量摘要
- 标签/分类
- 重复性研究劳动

### Execution Runtime

- Hermes：通用电脑/浏览器/文件/搜索执行
- Claude Code：coding workflow
- Codex：coding/project engineering
- Python/Stata/R：确定性计算

原则：

> Model = cognitive capacity；Runtime = action capacity。

---

## 9. Research Execution Loop

所有重要研究 Skill 尽量采用：

```text
PLAN
  ↓
RETRIEVE / ACT
  ↓
OBSERVE
  ↓
CHECK
  ↓
REVISE / RETRY
  ↓
VALIDATE
  ↓
SAVE STATE
  ↓
HUMAN CHECKPOINT（必要时）
```

禁止采用：

```text
Prompt → Answer → Done
```

---

## 10. Evidence Architecture

研究知识的基本对象不是“长文本”，而是结构化证据：

```text
Claim
Evidence
Source
Location
Interpretation
Confidence
Status
```

建议 Evidence Store 最终支持：

- source id
- source type
- provenance
- exact location
- extracted quote/data
- claim mapping
- verification status
- conflict status

---

## 11. Agent Forensics

对 Hermes / Claude Code / Codex / Kimi Code 重点逆向分析：

1. Task Decomposition
2. Triggering
3. Context Loading
4. Tool Selection
5. Execution Ordering
6. Execution Loop
7. Failure Recovery
8. Permission Boundary
9. Verification
10. Memory
11. Skill Evolution
12. Delegation / Subagent
13. Stop Condition

重点不是抄 Prompt，而是提炼 Execution Primitives。

---

## 12. 从零开始建立系统

### Phase 0 — 建目录和 Git 仓库

建立本目录树，进入根目录：

```powershell
cd <path>\\research_os_v1
git init
git add .
git commit -m "init research os"
```

### Phase 1 — 先不开发大 Agent

完成：

- Skill Registry
- Permission Matrix
- Model Router
- Agent Forensics Matrix
- Skill Template

### Phase 2 — 建立最小 Runtime

实现：

```text
PowerShell
  → Python launcher
    → simple model client
      → skill loader
        → result writer
```

这一阶段不做自动多 Agent。

### Phase 3 — 接入 Model Gateway

先做一个统一接口：

```text
call_model(provider, model, messages, tools, response_schema)
```

以后 Skill 不直接调用 GPT/Claude/Kimi，而调用这个接口。

### Phase 4 — 接入 Execution Runtime

优先复用 Hermes、Codex、Claude Code、Python/Stata 等现成能力。

### Phase 5 — 建 Validation / Checkpoint

任何高权限 Skill 都要支持：

- validation
- stop condition
- human checkpoint

### Phase 6 — 真实研究项目试运行

先拿一个已有的论文项目跑，不要一开始拿一个完全陌生的大项目测试。

### Phase 7 — 从任务中沉淀 Skills

每完成一个复杂任务，问：

> 哪些步骤是稳定可复用的？

把这些步骤沉淀成 Skill。

---


## 12A. 实际文件树

完整文件树见 `TREE.md`。核心结构如下：

```text
research_os_v1/
├── design.md
├── README.md
├── TREE.md
├── registry/
├── architecture/
├── skills/
│   ├── human/
│   ├── universal/
│   ├── knowledge_theory/
│   ├── evidence/
│   └── paradigms/
│       ├── empirical/
│       ├── case/
│       ├── policy/
│       ├── economic_history/
│       └── theoretical/
├── adversarial/
├── communication/
├── agent_forensics/
│   ├── hermes/
│   ├── claude_code/
│   ├── codex/
│   └── kimi_code/
├── templates/
├── projects/
├── workspace/
│   ├── inbox/
│   ├── active/
│   ├── outputs/
│   └── archive/
├── state/
└── logs/
```

各研究 Skill 文件均已按 Registry 编号创建为空白 Markdown 文件；`templates/`、`registry/`、`architecture/` 与 `agent_forensics/` 中的核心方法文档已预置最小内容。

## 13. 下一步最值得做的三件事

### T1 — Agent Forensics Sprint

目标：搞清楚 Hermes / Claude Code / Codex / Kimi Code 的执行语法。

步骤：

1. 对每个 Agent 选择 3 个相同任务：搜索整理、PDF处理、代码/debug。
2. 记录 Task Decomposition、Tool Ordering、Context、Permission、Verification、Failure Recovery。
3. 填写 `agent-forensics/*/forensics.md`。
4. 找出所有可迁移的 Execution Primitive。
5. 形成 `agent-forensics/primitives.md`。

不要分析“哪个模型回答得好”，重点分析：

> 为什么它能把任务做完。

### T2 — 做三个最小可执行 Skill

建议：

- U01 literature-discovery
- U03 source-verification
- E05 evidence-claim-mapping

原因：三个 Skill 刚好覆盖：

> 找 → 验 → 证明

它们也是跨实证、案例、政策、经济史的通用基础能力。

每个 Skill 先写 SKILL.md，然后用 Hermes 执行，不做自己的大 Agent。

### T3 — 建最小 Model Gateway + Orchestrator

第一版只需要：

```text
PowerShell
  ↓
run.py
  ↓
Task Router
  ↓
Model Router
  ↓
Skill Loader
  ↓
Hermes / Python / Web
  ↓
Validation
  ↓
Output
```

只支持三个模型接口：

- GPT API
- Claude API
- Kimi API

先做到：

> 一个入口 + 一个 Skill + 三个模型可切换 + 日志可追踪。

不要先做多 Agent 自主协作。

---

## 14. v1 的成功标准

如果以下事情能够稳定完成，Research OS v1 就算成功：

```text
用户提出研究任务
↓
系统识别任务类型
↓
匹配 Skill
↓
选择模型
↓
调用工具/Runtime
↓
保存 Evidence
↓
验证结果
↓
在需要处停下来询问人
↓
输出结构化结果
↓
留下 Audit Log
```

而不是：

> “能自动写一篇论文”。

---

## 15. 长期目标

最终形成：

```text
Personal Research OS
│
├── Human Sovereignty Layer
├── Research Orchestrator
├── Skill Registry
├── Model Router
├── Tool Router
├── Permission Engine
├── Validation Engine
├── Evidence Store
├── Context / Memory Manager
├── Agent Runtime Adapter
└── Audit / Learning Layer
```

核心资产不是某一个模型，也不是某一个 Agent 软件，而是：

> Research Skills + Research Memory + Evidence Structure + Permission Rules + Validation Rules + Execution Primitives

这些才构成长期可积累的个人研究基础设施。
