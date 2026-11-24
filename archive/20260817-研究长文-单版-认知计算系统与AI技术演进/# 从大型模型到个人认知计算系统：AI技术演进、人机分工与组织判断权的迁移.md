# 从大型模型到个人认知计算系统：AI技术演进、人机分工与组织判断权的迁移

## 引言：从“模型能力”转向“认知生产系统”

2023年以来，大语言模型的快速发展通常以参数规模、基准测试成绩、上下文长度和推理能力等指标加以刻画。然而，如果将人工智能置于更长的计算史和组织演化史中考察，仅以模型能力描述这一轮变革可能低估其真正含义。计算机技术的历史表明，技术革命的经济和组织影响并不只来自计算能力本身，而来自计算能力、输入输出方式、存储、编程接口、软件生态、硬件成本、网络以及用户分工的协同演进。打孔卡、磁带和磁盘曾使数据处理从人工记录转向机器处理；个人计算机则进一步将原本集中于机房的计算能力迁移至个人终端；图形用户界面又进一步降低了计算机使用的编程门槛。IBM历史资料显示，打孔卡曾长期承担数据存储和程序输入功能；1981年IBM PC出现后，计算能力开始大规模进入个人工作环境。Xerox Alto则在20世纪70年代已经将图形界面、鼠标、网络和个人文件存储结合到一个面向个人的计算环境中，成为后来个人计算范式的重要先驱。

由此提出本文的基本问题：**2023年以来的大模型革命究竟处于计算机历史的哪个阶段？随着模型、Agent、Harness、记忆、推理和专用硬件进一步发展，人类在认知劳动中的合理参与边界将如何变化？哪些劳动会被压缩，哪些劳动会被强化？**

进一步的问题是：当前关于未来AI发展的预测大多默认“Transformer + 预训练 + 后训练 + 推理时计算”的技术路线。如果出现新的模型架构、持续学习机制、记忆架构、稀疏计算、专用硬件或算法—硬件协同路线，既有的时间预测是否会系统性失效？因此，本文不试图给出单线性的技术预测，而是建立一个由**计算系统演进—Agent自主性—人类判断权**组成的分析框架。

---

# 一、思考起点：为什么“Agent替代代码”并不等于“工程师消失”

2026年2月，OpenAI公布了一项具有代表性的工程实验：一个软件产品从空仓库开始构建，整个项目的应用逻辑、测试、CI、文档、可观测性和内部工具均由Codex生成，人类工程师没有直接编写代码。项目规模达到约百万行代码，团队将人类工程师的主要工作定义为设计环境、明确意图、构建反馈循环和建立架构约束；OpenAI将这一实践概括为“Humans steer. Agents execute”。该实验同时显示，随着代码生成能力提高，人类瓶颈从代码生产逐渐转向QA、系统可观测性、架构一致性以及人类注意力配置。

这一现象意味着，Agent化的软件工程并非简单的“机器代替程序员”，而是生产函数发生了重构。传统软件工程近似于：

[
Human \rightarrow Code \rightarrow Test \rightarrow Debug
]

而Agent化工程更接近：

[
Human
\rightarrow
Goal/Constraint
\rightarrow
Harness
\rightarrow
Agent
\rightarrow
Code
\rightarrow
Automated\ Evaluation
\rightarrow
Revision
]

因此，人类工程师并没有退出系统，而是从**实现者**转向**环境设计者、约束制定者、评价体系设计者和最终判断者**。

OpenAI的工程实践尤其揭示了Harness的作用：通过固定架构层次、限制依赖方向、建立自动化测试、提供浏览器、日志、指标和链路追踪等可观测环境，使Agent能够直接观察、验证和修正自己的工作；同时，把人类所谓的“工程品味”编码成golden principles，通过持续扫描和自动重构，将一次性的人类判断转化为可以长期运行的机器约束。

Anthropic关于长期运行Agent的研究也得出了相近结论：当任务跨越多个上下文窗口时，仅提高模型能力并不足以保证持续进展，必须通过初始化Agent、工作状态、持久化工件和上下文转换机制建立跨会话工作环境；到2026年，Anthropic进一步指出，Harness实际上编码了对于“模型当前无法做到什么”的假设，而随着模型能力提升，这些假设会逐渐过时。

由此产生第一个重要发现：

> **Harness的本质不是帮助AI“完成一次任务”，而是把人类关于任务边界、正确性和工作方法的知识转化为可执行的环境。**

因此，Harness可以理解为一种**认知制度化机制**：它把专家经验从人的头脑中提取出来，转化为规则、测试、反馈和环境，使后续Agent能够持续调用。

---

# 二、问题进一步推进：Harness、预训练与“给材料让AI创造新东西”究竟有什么不同

这三种机制经常被混淆，但它们实际上改变的是AI系统的不同组成部分。

可将一个复杂AI系统抽象表示为：

[
Y=f_{\theta}(X,C,H,R)
]

其中：

* (\theta)：预训练和后训练形成的模型参数；
* (X)：当前任务；
* (C)：当前任务中临时提供的上下文、文献、数据和其他材料；
* (H)：Harness，包括工具、规则、环境、工作流、验证机制和反馈；
* (R)：推理时投入的计算资源。

这意味着四种能力来源可以分开理解。

### （一）预训练：改变“模型本身”

预训练通过大规模数据和梯度优化改变模型参数，使知识、模式和一般能力被压缩进参数空间。它回答的是：

> **模型自身学会了什么？**

预训练以后，即便不给模型原始训练材料，模型仍可以调用经过训练形成的统计表征与能力。

### （二）上下文材料：改变“当前任务能调用什么”

当研究者向AI提供100篇论文、数据字典、审稿意见和历史研究设计时，这些材料通常并没有进入模型参数，而是在当前任务中构成一个临时工作记忆空间。

它回答的是：

> **这一次任务，模型可以看到什么？**

因此，“给AI一堆材料”与“训练AI”不是同一件事情。

### （三）Test-time compute：改变“模型愿意搜索多久、试多少次”

当AI不是简单总结100篇论文，而是按照：

[
文献
\rightarrow
理论抽取
\rightarrow
矛盾识别
\rightarrow
假设生成
\rightarrow
反例搜索
\rightarrow
模型修正
\rightarrow
再次验证
]

这样的流程工作时，关键变化并不是材料增加，而是**推理时计算预算增加**。

研究已经发现，在部分困难任务上，合理分配test-time compute可以显著提高推理性能；甚至在相同FLOPs预算下，小模型配合更有效的推理时搜索可能击败显著更大的模型。

因此：

[
Context = 当前知识空间
]

而：

[
Test\text{-}time\ Compute = 当前问题上的搜索资源
]

### （四）Harness：改变“AI如何工作”

Harness并不主要提供知识，而是规定：

* 可以调用什么工具；
* 应该如何分解任务；
* 什么结果才算正确；
* 失败后应该如何反馈；
* 是否需要重新尝试；
* 何时应该创建子Agent；
* 什么情况下必须升级给人类。

因此，Harness并不等于“更多知识”，也不等于“更多算力”，它是一种**行为环境和认知生产制度**。

由此得到第二个结论：

> **预训练解决“AI有什么脑子”，上下文解决“这次给AI什么材料”，Test-time compute解决“AI在这次任务上可以探索多少”，Harness则解决“AI在什么环境和规则下探索”。**

进一步而言，简单的“材料+推理”是一项认知任务，而“材料+Agent+工具+反馈+验证+循环”则开始构成一个**认知生产系统**。

---

# 三、从Harness进一步推演：它为什么可能被AI自身逐层吞并

如果Harness是一套规定Agent如何工作的环境，那么问题自然变成：

> **随着模型能力提高，Harness本身是否也会被模型自动生成？**

答案是肯定的，而且替代具有明显的层次性。

可以把Harness划分为六个层次：

[
L_1 基础设施
\rightarrow
L_2 工作流
\rightarrow
L_3 评价体系
\rightarrow
L_4 架构设计
\rightarrow
L_5 问题定义
\rightarrow
L_6 价值函数
]

其中：

**L1：** sandbox、filesystem、memory、retry、logging、tool routing等基础设施；

**L2：** 任务分解、工作流、subagent协作、工具调用；

**L3：** benchmark、测试、评价、反馈循环；

**L4：** 系统架构、模块边界、依赖结构；

**L5：** 研究问题、商业问题、战略问题本身；

**L6：** 到底什么目标值得优化。

替代最可能遵循：

[
L_1 \rightarrow L_2 \rightarrow L_3 \rightarrow L_4 \rightarrow L_5 \rightarrow L_6
]

即越靠近“怎么做”的层次越容易自动化，越接近“为什么做”的层次越难替代。

这一趋势已经出现。OpenAI在2026年的Codex实践中不仅让Agent生成业务代码，也让其生成测试、CI、内部工具和评估Harness；随后又提出Symphony，将项目管理系统转化为Agent的控制平面，使多个Coding Agent能够在较少人工协调的情况下并行运行。

因此，Harness的第一阶段是：

> **人设计环境，AI使用环境。**

下一阶段可能变成：

> **人规定目标与高层约束，AI自己设计大部分环境。**

再下一阶段：

> **AI不仅设计环境，还开始发现值得解决的问题。**

---

# 四、从时间维度看：未来三个阶段何时出现

如果以2026年8月为起点，可以提出一个“基准情景”。

## 第一阶段：Agent自主设计Harness与架构

预计时间：

> **2027—2029年形成明显主流能力。**

这一阶段的关键变化不是AI能否“生成架构图”，而是它能否主动完成：

[
Architecture\ A/B/C
\rightarrow
Benchmark
\rightarrow
Simulation
\rightarrow
Evaluation
\rightarrow
Rearchitecture
]

真正的标志包括：

1. Agent主动发现架构瓶颈，而非等人类要求优化；
2. Agent能够自己产生或修改evaluation；
3. Agent可以同时探索多个候选架构；
4. Agent能够解释为什么某种架构优于其他方案；
5. 人类不再逐个设计工作流，而只提供高层目标和边界。

OpenAI已经展示了非常接近这一阶段的早期形态：Agent可以在运行过程中直接查看日志、metrics、DOM、截图和测试结果，并长期执行任务；与此同时，系统通过“golden principles”和自动化清理流程持续修正架构偏离。

---

## 第二阶段：AI自主发现问题

预计时间：

> **2029—2033年形成重要突破。**

这一阶段比自动写代码更加重要，因为认知生产链发生了改变：

[
Human \rightarrow Problem \rightarrow AI
]

变为：

[
Human \rightarrow Domain
\rightarrow AI \rightarrow Problem
]

例如，在科研环境中，人类不再告诉AI“研究耐心资本如何影响企业基础研究”，而是向其提供大规模文献、数据和现实约束，并要求AI寻找：

* 理论矛盾；
* 异常事实；
* 尚未解释的关系；
* 潜在机制；
* 可识别且值得研究的问题。

一个成熟的系统可能自主完成：

[
1000个问题
\rightarrow
理论筛选
\rightarrow
数据可行性筛选
\rightarrow
识别策略筛选
\rightarrow
深度验证
\rightarrow
保留少数高价值问题
]

这一阶段的核心标志不是“AI能回答问题”，而是：

> **AI能够发现人类原本没有明确提出的问题。**

---

## 第三阶段：AI开始参与目标函数形成

预计时间：

> **2031—2035年开始出现比较明确的能力，2035年以后才可能形成更成熟的组织化应用。**

原因在于，前两个阶段主要可以转化为可验证的搜索与优化问题：

[
\arg\max_x f(x)
]

而第三阶段的问题则是：

[
\text{Why should }f(x)\text{ be the objective?}
]

例如癌症治疗可以最大化：

* 平均寿命；
* 五年生存率；
* 医疗福利；
* 成本效率；
* 特定群体福利。

不同价值函数会导致不同最优解。

因此第三阶段的本质不是AI“会不会哲学”，而是AI能否：

1. 从人类行为推断隐含偏好；
2. 识别目标之间的冲突；
3. 比较不同长期目标的后果；
4. 主动提出目标函数；
5. 让人类在不同目标体系之间进行最终选择。

这意味着AI开始从：

> **执行目标**

转向：

> **参与目标形成。**

---

# 五、但是上述时间预测存在一个根本风险：我们假定了错误的技术路线

前面的时间预测实际上隐含了一个假设：

[
AI\ Capability
\approx
Pretraining
+
Post\text{-}training
+
Test\text{-}time\ Compute
]

但这一假设不一定成立。

如果未来出现新的模型架构、长期记忆、持续学习、稀疏计算、专用硬件或者软硬件共同设计，那么能力增长速度可能明显高于基于当前Transformer体系的外推。

因此未来更应该关注：

[
AI\ System =
Model
\times
Memory
\times
Learning
\times
Compute
\times
Environment
]

而不是单独关注模型参数规模。

---

# 六、可能改变时间表的第一条路线：Transformer之外的模型架构

Transformer的核心优势是attention能够直接访问上下文，但其计算和存储成本会随着序列长度增加而上升。Mamba等状态空间模型试图通过线性复杂度和选择性状态机制改善长序列处理效率。Mamba论文报告了线性随序列长度扩展的计算特征和较高的推理吞吐，其研究动机正是解决Transformer在长序列上的效率问题。

Google随后提出的Titans/MIRAS进一步把“长期记忆”本身纳入模型架构。其核心思想不是单纯扩大上下文，而是让模型在运行过程中更新神经记忆；Google报告其架构可以处理超过200万token的长上下文，并在相关任务上取得较强表现。

其潜在意义在于：

[
External\ Memory
\rightarrow
Internal\ Memory
]

如果模型能够真正持续学习，那么今天大量依靠RAG、向量数据库、context compression和外部memory完成的工作，未来可能被模型自身吸收。

---

# 七、第二条路线：稀疏化与MoE

第二条可能加速路径是Mixture-of-Experts等稀疏模型。

核心思想是：

[
Total\ Parameters \gg Active\ Parameters
]

即模型可以拥有巨大的总参数量，但一次任务只激活少量专家。

这使得未来可能同时获得：

* 更大的潜在能力空间；
* 更低的单次推理成本；
* 更专业化的模块调用；
* 更灵活的Agent协作。

因此未来的AI不一定表现为“一个巨大模型”，而可能表现为：

[
General\ Model
+
Experts
+
Memory
+
Tools
+
Agents
]

也就是说，AI的基本单位可能从“单模型”转向“认知系统”。

---

# 八、第三条路线：从显式思维链转向更高效的推理时计算

当前推理模型常通过增加reasoning tokens来增加测试时计算，但test-time scaling并不必然等于更长的自然语言思维链。

未来可能出现更多隐空间搜索、内部状态计算和候选搜索机制，使：

[
More\ Compute
\neq
More\ Visible\ Tokens
]

而更接近：

[
More\ Compute
=============

More\ Internal\ Search
]

这一方向一旦成熟，将降低复杂推理的单位成本，从而加速Agent自主搜索。现有研究已经表明，对test-time compute进行计算最优分配，在部分任务上可以显著提高效率，并超过简单的best-of-N策略。

---

# 九、第四条路线：AI专用硬件与软件协同设计

未来的计算系统也不太可能只是“更快的GPU”。

Agent的成本结构越来越涉及：

* memory；
* KV cache；
* 数据移动；
* 通信；
* 长时间推理；
* 多Agent并发；
* inference scheduling。

因此，真正的下一代AI基础设施可能是：

[
Model
+
Memory
+
Interconnect
+
Compiler
+
Runtime
+
Inference\ Hardware
]

而不是单独提高峰值FLOPs。

这也意味着，对未来AI的衡量指标应该逐渐从：

> “模型有多少参数、benchmark多少分”

转向：

> **单位成本能够完成多少有效认知工作。**

---

# 十、第五条路线：持续学习可能比单纯扩大模型更重要

当前主流流程仍接近：

[
Pretraining
\rightarrow
Post\text{-}training
\rightarrow
Deployment
\rightarrow
Inference
]

即模型部署以后通常相对稳定。

另一条可能的路线则是：

[
Training
\rightarrow
Deployment
\rightarrow
Experience
\rightarrow
Memory\ Update
\rightarrow
Learning
\rightarrow
Policy\ Adaptation
\rightarrow
Better\ Agent
]

如果持续学习成熟，模型就不再是静态工具，而成为能够在现实环境中积累经验的系统。

这会使之前的阶段④和阶段⑤明显提前，因为Agent不仅能够运行，还能够：

> **从运行过程中学习如何更好地运行。**

---

# 十一、因此更合理的未来预测应该是“基准情景+加速情景”

如果继续沿着当前主流路线：

| 认知阶段                | 基准情景      |
| ------------------- | --------- |
| Agent自主设计Harness/架构 | 2027—2029 |
| AI自主发现问题            | 2029—2033 |
| AI参与问题定义/目标构建       | 2031—2035 |
| AI参与价值函数形成          | 2035年以后   |

如果出现“持续学习+长期记忆+更高效推理+专用硬件”组合，则可能明显提前：

| 认知阶段                | 加速情景           |
| ------------------- | -------------- |
| Agent自主设计Harness/架构 | **2026—2028**  |
| AI自主发现问题            | **2028—2030**  |
| AI参与问题定义/目标构建       | **2029—2033**  |
| AI参与价值函数形成          | **2032—2035+** |

这里的重点不是某一个年份，而是：

> **新技术路线可能压缩不同阶段之间的过渡时间，甚至使阶段④与阶段⑤部分重叠。**

---

# 十二、从计算机史重新定位2023—未来：AI还没有真正进入“PC时代”

要判断AI目前处于哪个历史阶段，不能仅观察模型是否强大，而应该同时考虑：

1. 输入输出方式；
2. 信息处理能力；
3. 存储与记忆；
4. 计算是否集中或分散；
5. 便携性；
6. 编程接口；
7. 软件生态；
8. 网络能力；
9. 自主行动；
10. 持续学习。

按这一标准，2023年的AI仍然高度类似于：

> **大型机时代的中央计算中心 + 极先进的终端。**

复杂计算集中于云端，个人通过浏览器或App访问模型；这种结构在组织方式上仍与大型机—终端体系具有可比性。IBM关于大型机历史的资料表明，20世纪50—60年代大型机通常位于企业的数据处理中心，是组织的中央数据仓库和计算设施。

但2024—2026年开始出现质变：Agent不再只是发送文本给中央模型并等待答案，而是可以直接调用文件系统、shell、浏览器、代码库、数据库、观测系统和其他工具。OpenAI的Codex实践已经表现出典型的“中央大模型+个人工作环境+工具链”结构。

因此，2026年的AI更准确地说处于：

> **云端大型机 → 个人工作站/Agent工作站的过渡时期。**

它尚未真正进入Windows式的成熟个人AI计算时代。

---

# 十三、为什么“个人AI计算机”可能比PC革命快得多

PC革命真正改变的是：

[
Centralized\ Computing
\rightarrow
Personal\ Computing
]

AI革命可能进一步改变：

[
Personal\ Computing
\rightarrow
Personal\ Cognitive\ Computing
]

PC要求用户：

> 打开程序—学习软件—输入命令—处理文件—自己判断结果。

AI-native computer则可能允许用户直接表达：

> “帮我把过去两年的研究材料整理成一个理论框架，寻找现有文献之间的矛盾，再提出三个可以通过现有数据验证的研究路径。”

系统随后自行：

[
Search
\rightarrow
Read
\rightarrow
Reason
\rightarrow
Code
\rightarrow
Experiment
\rightarrow
Evaluate
\rightarrow
Revise
]

真正的AI PC时代因此不是“PC里装了AI”，而是：

> **计算机的操作系统、文件系统、工具调用、应用程序和工作流本身围绕AI重新组织。**

---

# 十四、一个更完整的AI计算史类比

综合输入输出、处理能力、存储、便携性、编程接口、自主行动等因素，可以做如下映射：

| 计算机史          | AI发展          | 主要变化                               |
| ------------- | ------------- | ---------------------------------- |
| 大型机           | **2023**      | 云端集中计算、文本终端                        |
| 小型机/工作站过渡     | **2024—2026** | Agent开始直接操作工具和环境                   |
| 个人工作站         | **2026—2028** | 一个个体可以持续运行自己的Agent                 |
| PC时代          | **2027—2030** | AI成为个人计算环境                         |
| GUI/Windows时代 | **2029—2033** | Agent OS、Skills、Memory、自然语言成为统一交互层 |
| 网络化计算         | **2030年代**    | Agent跨设备、跨环境、跨组织协作                 |
| 移动互联网之后       | **2030年代以后**  | AI从“设备中的应用”转向持续存在的认知基础设施           |

其中2026年尤其像“工作站时代”，而非已经成熟的Windows时代。

Xerox Alto之所以具有历史意义，不只是因为它用了GUI，而是因为它把显示器、鼠标、个人文件存储和网络组合成了一个完整的个人计算环境。

这为理解Agent提供了一个重要启示：

> **新的计算范式不是由单一模型能力构成，而是由“硬件+软件+输入输出+存储+网络+交互”共同构成。**

---

# 十五、问题转向人的分工：AI替代的不是“职业”，而是认知劳动链中的不同层次

如果从人类分工而非AI技术出发，传统认知劳动可以拆成：

[
问题定义
\rightarrow
信息搜集
\rightarrow
理解
\rightarrow
分析
\rightarrow
方案生成
\rightarrow
执行
\rightarrow
验证
\rightarrow
决策
]

AI并不会在所有层次同时替代，而更可能从链条底部逐渐向上侵入。

---

# 十六、第一层：信息搬运劳动大幅下降

包括：

* 搜索；
* 摘要；
* 转录；
* 分类；
* 文档整理；
* 数据清洗；
* 初步汇总。

这类任务的特点是：

[
可标准化
+
可验证
+
低不可逆性
]

因此最适合自动化。

未来人类不再主要承担：

> “找到信息。”

而转向：

> “定义我需要知道什么。”

其所需劳动量可能从当前水平下降一个数量级，而不是只下降几十个百分点。

---

# 十七、第二层：执行型知识劳动进一步下降

包括：

* 代码实现；
* 常规数据分析；
* 普通报告；
* 标准化建模；
* 常规法律检索；
* 常规财务处理；
* 基础科研计算；
* 大量格式化写作。

这些任务同样具有较高的可验证性。

因此，未来不是“这些职业消失”，而是：

> **完成一个单位成果所需要的人数显著下降。**

例如原来需要5个初级分析人员完成的数据工程，未来可能由：

> 1名高级人员 + 多个Agent

完成。

因此真正改变的是**劳动投入系数**。

---

# 十八、第三层：协调劳动也会开始下降

这是容易被低估的一环。

大量中层管理者、项目经理、协调人员承担的其实不是专业判断，而是：

[
谁做什么
\rightarrow
什么时候做
\rightarrow
结果如何
\rightarrow
哪里卡住
\rightarrow
如何重新分配
]

如果Multi-Agent系统能够自己：

[
Task\ Decomposition
\rightarrow
Agent\ Allocation
\rightarrow
Monitoring
\rightarrow
Evaluation
\rightarrow
Reallocation
]

那么部分协调劳动也会被压缩。

因此AI对组织结构的冲击不仅是：

> **减少执行者。**

还可能是：

> **减少中间协调者。**

---

# 十九、第四层：专业判断短期反而增强

高级律师、资深工程师、教授、投资负责人、战略人员等在短期可能不会因为AI而立即下降。

原因在于：

[
Expert + AI
\gg
Expert
]

一个高级专家获得Agent以后，相当于拥有一个可以持续运行的：

* 研究团队；
* 数据团队；
* 编程团队；
* 分析团队；
* 文档团队。

因此AI可能首先产生一个“超级杠杆”效应：

> **少数高水平人员的产出能力急剧提高。**

这甚至可能造成：

[
Top\ Human + AI
]

与

[
Average\ Human + AI
]

之间的差距扩大。

---

# 二十、但高级专业劳动会出现第二次变化：从解决问题转向选择问题

随着Agent开始自主发现问题，专家的核心工作会逐渐发生迁移：

[
Problem\ Solver
\rightarrow
Problem\ Selector
]

例如科研：

传统模式：

> 教授提出问题 → 博士生找文献、做数据、跑模型、写论文。

Agent模式：

> Agent产生1000个候选问题 → 自动筛选 → 深挖少数问题 → 提交给教授判断。

于是教授真正稀缺的能力不再是：

> “如何亲自完成一个研究。”

而是：

> **“哪一个问题值得投入稀缺的研究资源。”**

---

# 二十一、进一步上移：从问题选择到目标设定

这就是前面六层中最难被替代的部分。

随着AI能够自动搜索大量问题，人类真正需要处理的是：

[
Problem\ Selection
\rightarrow
Evaluation
\rightarrow
Goal\ Setting
]

也就是说，人类逐渐从：

> “怎样做得更好”

转向：

> “什么值得做”

甚至进一步转向：

> “为什么这个目标值得追求”。

---

# 二十二、因此人类劳动不是简单下降，而是发生“深度两极化”

从总劳动时间看：

[
人类执行劳动 \downarrow
]

但从单位决策的重要性和责任看：

[
人类关键判断 \uparrow
]

由此可能出现：

> **低层认知劳动大量减轻，高层判断劳动显著加深。**

因此不能简单说：

> “未来人类工作越来越少。”

更准确的是：

> **人类直接参与认知生产的频率下降，但每一次参与的决策权重上升。**

---

# 二十三、一个更完整的人类分工变化矩阵

| 人类活动      |  趋势 | 可能的长期变化            |
| --------- | --: | ------------------ |
| 信息检索      | ↓↓↓ | 大部分自动化             |
| 信息整理      | ↓↓↓ | 大部分自动化             |
| 标准化分析     | ↓↓↓ | 大规模Agent化          |
| 代码实现      | ↓↓↓ | 人类从实现退到约束和审查       |
| 常规写作      | ↓↓↓ | 人类编辑和判断            |
| 数据处理      | ↓↓↓ | 高度自动化              |
| 项目协调      |  ↓↓ | Agent负责大量调度        |
| 流程管理      |  ↓↓ | 动态工作流自动生成          |
| 常规专业分析    |  ↓↓ | 高比例AI化             |
| 架构设计      |   ↓ | 逐渐转为Agent搜索问题      |
| Harness设计 | ↑→↓ | 先上升，再被自动化          |
| 问题发现      |  →↑ | 人类逐渐转向筛选           |
| 问题选择      |  ↑↑ | 重要性大幅提升            |
| 评价标准设计    | ↑↑↑ | 成为核心能力             |
| 目标设定      | ↑↑↑ | 人类核心权力             |
| 价值判断      | ↑↑↑ | 最难自动化              |
| 最终责任      | ↑↑↑ | 仍需要人类承担            |
| 战略选择      | ↑↑↑ | 候选空间越大，选择越重要       |
| 监督与治理     |  ↑↑ | AI越强，对验证和责任配置需求越高  |
| 社会授权与信任   |  ↑↑ | 技术能力无法完全替代合法性和责任关系 |

---

# 二十四、因此未来的人类角色可能不是“监督者”，而是“认知系统的目标与判断层”

这一变化可以用四个阶段概括。

### 阶段一：执行者

[
Human:
How
]

人自己完成任务。

### 阶段二：监督者

[
Human:
What + Check
]

Agent负责执行，人负责检查。

### 阶段三：问题选择者

[
Human:
Which\ Problem?
]

Agent负责发现、执行和验证，人负责选择值得推进的问题。

### 阶段四：目标设定者

[
Human:
Why?
]

Agent负责问题搜索、架构设计、实验、执行和验证，人类决定目标、价值边界和最终接受条件。

因此，人类分工的迁移可以概括为：

[
\boxed{
Execution
\rightarrow
Supervision
\rightarrow
Problem\ Selection
\rightarrow
Goal\ Setting
\rightarrow
Value\ Judgment
}
]

---

# 二十五、一个更深的组织学含义：组织从“配置知识”转向“配置判断权”

传统组织的主要任务之一，是把知识配置给最合适的人：

[
Knowledge
\rightarrow
Person
\rightarrow
Task
]

但在Agent时代，知识开始成为可以被动态检索和调用的资源：

[
Goal
\rightarrow
Agent
\rightarrow
Knowledge
\rightarrow
Action
]

于是组织设计的核心就发生改变：

> **不再主要是“谁知道什么”，而开始是“谁有权决定什么”。**

尤其当Agent可以：

* 搜索知识；
* 生成方案；
* 设计工作流；
* 编写代码；
* 自行验证；
* 自主产生问题；

之后，组织中的真正稀缺资源越来越接近：

1. 目标设定权；
2. 评价标准制定权；
3. 问题选择权；
4. 最终接受权；
5. 资源配置权；
6. 责任承担权。

因此，AI时代组织结构未必只是简单“扁平化”，而更可能表现为：

> **执行层和协调层被压缩，而高层判断层的杠杆率显著提高。**

---

# 二十六、一个关键的反直觉结论：Harness本身就是“人类经验机器化”的机制

Harness之所以最终可能被AI替代，恰恰因为它具有强烈的“知识固化”作用。

一个顶级工程师最初可能只是知道：

> “这类问题通常应该这样处理。”

第一步：

[
经验
\rightarrow
SOP
]

第二步：

[
SOP
\rightarrow
规则
]

第三步：

[
规则
\rightarrow
测试
]

第四步：

[
测试
\rightarrow
自动评价
]

第五步：

[
评价
\rightarrow
Agent自我修正
]

一旦完成这一过程，原本只存在于一个专家头脑中的经验就被转化成了机器可以长期执行的制度。

因此：

> **Harness Engineering的深层作用不是帮助人管理AI，而是把优秀人类的经验固化成可以被Agent重复运行的认知基础设施。**

这正是为什么Harness最终很可能发生自我吞并：当“如何设计Harness”的经验本身被足够多地编码后，下一代Agent就可以学习如何设计Harness。

---

# 二十七、最终可能出现递归的AI生产系统

如果这个过程继续发展，认知生产将呈现：

[
Agent
\rightarrow
Harness
\rightarrow
Better\ Agent
\rightarrow
Better\ Harness
\rightarrow
Better\ Agent
\rightarrow \cdots
]

也就是说，AI不再只是使用环境，而开始：

> **设计产生AI能力的环境。**

当这个闭环真正成立以后，模型能力增长和人类工程师数量之间的关系就会发生根本变化。

人类不再需要随着Agent数量同比增加工程人员。

相反：

[
1\ Human
\rightarrow
N\ Agents
\rightarrow
N^2\ Cognitive\ Work
]

组织的核心生产率将越来越由：

> **一个高水平人类能够配置多少机器认知能力**

决定。

---

# 二十八、综合推演：2026年以后的人机边界

在基准技术路线下，可以提出如下演化：

### 2026—2027

人类：

> 设计Harness、工具、约束、评价。

Agent：

> 执行复杂任务。

### 2027—2029

人类：

> 提供目标与高层架构。

Agent：

> 自己设计越来越多的工作流、评价和架构。

### 2029—2033

人类：

> 提供领域和战略边界。

Agent：

> 自主产生、筛选和验证问题。

### 2031—2035

人类：

> 参与目标构建和价值比较。

Agent：

> 建模不同目标、预测后果、提出候选目标。

### 2035以后

真正的核心问题可能不再是：

> AI能不能做这项认知工作？

而变成：

> **谁拥有定义AI应该追求什么的权力？**

---

# 二十九、但这一时间表具有显著的技术路线风险

上述预测必须被视为条件预测，而非确定性预测。

如果未来出现以下技术组合：

[
Efficient\ Architecture
+
Persistent\ Memory
+
Continual\ Learning
+
Efficient\ Test\text{-}time\ Compute
+
Specialized\ Hardware
+
Agentic\ Runtime
]

那么阶段④、⑤甚至⑥之间的时间差可能明显缩短。

因此，未来最应该观察的并不是某个单一模型benchmark，而是六个结构性指标：

1. **单位有效认知工作成本**是否持续下降；
2. **模型是否具有真正持续的内部记忆**；
3. **推理是否从显式token扩展转向更加高效的内部搜索**；
4. **是否出现明显优于Transformer的架构组合**；
5. **模型是否能够在线持续学习**；
6. **Agent是否能够修改自身的工作环境和评价机制**。

其中最后两项尤其关键。

因为一旦出现：

[
Continual\ Learning
+
Self\text{-}designed\ Harness
]

AI系统便不再只是“越来越强的模型”，而开始成为：

> **能够积累经验、修改环境、搜索问题并改变自身工作方式的持续认知系统。**

---

# 三十、结论：AI革命真正改变的是“认知生产的基本单位”

本轮分析最终可以形成三个层次的结论。

### 第一，技术层面

2023—2026年的大模型仍主要处于：

> **云端大型计算中心向个人AI工作站过渡的阶段。**

2026年尚不能简单视为已经进入“Windows时代”，因为AI的计算、存储和模型主体仍高度集中于云端；但Agent已经使输入输出机制从“文本终端”转变为“直接操作计算环境”，因此它已经明显超越传统大型机—终端模式。

未来的“PC时刻”将不是AI被安装在PC中，而是：

> **计算机本身开始围绕AI重新组织。**

### 第二，认知劳动层面

AI首先压缩的是：

[
Information\ Handling
\rightarrow
Standardized\ Execution
\rightarrow
Coordination
]

随后逐渐侵入：

[
Architecture
\rightarrow
Problem\ Discovery
\rightarrow
Problem\ Selection
]

但越往上，人类劳动的总量可能下降，**单次判断的重要性反而上升**。

### 第三，组织层面

因此，最深刻的变化并不是：

> “AI会不会替代程序员、研究人员、管理者？”

真正的问题是：

> **当知识、执行、搜索、协调乃至部分架构设计都成为可规模化的机器能力之后，组织究竟还需要由人控制什么？**

一个可能的答案是：

[
\boxed{
人类逐渐退出执行权，
保留并强化问题选择权、评价权、目标设定权和最终判断权。
}
]

由此，组织设计的核心也可能发生转变：

[
\boxed{
配置知识
\rightarrow
配置执行
\rightarrow
配置Agent
\rightarrow
配置判断权
\rightarrow
配置目标与价值
}
]

这比“AI替代多少岗位”的问题更具有一般性。因为岗位只是具体的劳动容器，而真正发生变化的是**认知劳动链中权力与责任的分布**。

因此，从更长的历史视角看，AI革命可能并不是第四次“计算机效率革命”，而是一次对**人—计算机之间认知分工结构**的重构：PC把计算能力从组织中心迁移到个人，互联网把信息访问能力从组织边界迁移到网络，而Agent正在尝试把部分认知执行能力迁移到个人。下一步真正具有制度意义的变化，则可能是：**当个人拥有一个可以持续运行、具有记忆、可以调用工具、自主生成工作流甚至自主发现问题的认知系统之后，人的稀缺性将越来越集中于“决定什么值得被机器去做”。**

---

# 参考文献与资料

1. OpenAI. (2026). *Harness engineering: leveraging Codex in an agent-first world*. OpenAI Engineering.

2. OpenAI. (2026). *Unlocking the Codex harness: how we built the App Server*. OpenAI Engineering.

3. OpenAI. (2026). *An open-source spec for Codex orchestration: Symphony*. OpenAI Engineering.

4. Anthropic. (2024). *Building effective agents*. Anthropic Research.

5. Anthropic. (2025). *Effective harnesses for long-running agents*. Anthropic Engineering.

6. Anthropic. (2026). *Harness design for long-running application development*. Anthropic Engineering.

7. Anthropic. (2026). *Scaling Managed Agents: Decoupling the brain from the hands*. Anthropic Engineering.

8. Anthropic. (2026). *Economic Index report: Cadences*.

9. Behrouz, A., Razaviyayn, M., & Mirrokni, V. (2025). *Titans + MIRAS: Helping AI have long-term memory*. Google Research.

10. Behrouz, A., Zhong, P., Razaviyayn, M., & Mirrokni, V. (2025). *Titans: Learning to Memorize at Test Time*. Google Research.

11. Gu, A., & Dao, T. (2023). *Mamba: Linear-Time Sequence Modeling with Selective State Spaces*. arXiv:2312.00752.

12. Snell, C., Lee, J., Xu, K., & Kumar, A. (2024). *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters*. arXiv:2408.03314.

13. *Test-Time Scaling in Reasoning LLMs: Inference Regimes, Evaluation, and Reproducibility*. (2026). arXiv:2608.04001.

14. IBM. *The IBM punched card*. IBM History.

15. IBM. *Floppy disk storage*. IBM History.

16. IBM. *The IBM PC*. IBM History.

17. IBM. *The S/360: A turning point in mainframe history*. IBM Documentation/History.

18. Computer History Museum. *Computers: Timeline of Computer History*.

19. Computer History Museum. *The Alto from the Industrial Designer's Perspective*.

20. Computer History Museum. *The Lisa: Apple's Most Influential Failure*.

21. Computer History Museum. *Introducing the Smalltalk Zoo*.

---

## 理论推演的边界

本文中的2027—2029、2029—2033和2031—2035等时间区间属于**基于技术趋势和机制推演的情景预测，而非实证估计或确定性预测**。尤其是“AI参与问题定义”和“AI参与价值函数形成”目前缺乏稳定的可量化外部证据，因此应被理解为理论推演。相比年份本身，更具观察价值的是本文提出的结构性指标：Agent是否能够自主设计工作环境、是否能够生成评价标准、是否能够主动发现问题，以及模型是否具备持续学习和长期记忆能力。

从这个意义上说，未来AI发展的真正拐点未必是某一个新模型发布，而可能是以下闭环首次稳定成立：

[
\boxed{
Model
\rightarrow
Memory
\rightarrow
Learning
\rightarrow
Harness
\rightarrow
Search
\rightarrow
Evaluation
\rightarrow
Self\text{-}Modification
}
]

一旦这个闭环建立，AI就不再只是一个“等待人类下达任务的模型”，而成为一种能够持续改变自身认知生产条件的系统。届时，人类与AI之间的核心分工也将从“谁做什么”进一步升级为“谁决定做什么、为什么做，以及什么结果值得被接受”。
