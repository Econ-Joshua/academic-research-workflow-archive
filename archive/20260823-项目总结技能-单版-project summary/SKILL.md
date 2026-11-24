---
name: distill-skill
description: 从项目代码库或对话记录中自动提炼最有价值、可复用的经验，一键生成为新技能（SKILL.md + 可独立运行的脚本），避免重复造轮子。当用户说"提炼技能/沉淀成skill/复用经验/总结可复用内容/不想重复造轮子"，或一段复杂任务刚完成想沉淀方法论时使用。
whenToUse: 用户要求把项目或对话中的经验提炼成 skill；想把重复劳动脚本化以节省 token；长任务结束后想沉淀流程、踩坑修复或工具脚本供下次复用。
---

# distill-skill：把会话/项目提炼成可复用技能

把一段已经完成的工作（项目代码库、对话导出记录、或刚结束的当前任务）中最有价值的部分——**可复用流程、踩坑修复、可脚本化的操作**——加工成一个新的标准技能，安装后可跨项目复用。

## 核心原则（违反任何一条必须返工）

1. **两阶段流水线**：采集、去重、评分、脚手架、校验全部交给本技能 `scripts/` 下的脚本完成（**零 token**）。你（模型）只做两件事：**判断候选是否值得沉淀**、**撰写新技能的 SKILL.md 正文**。
2. **只读 digest，不读原料**：永远不要把完整对话或整个项目喂给自己重读。所有分析只基于脚本产出的 digest / shortlist JSON（脚本已自动截断封顶）。
3. **能脚本化的必须脚本化**：确定性操作必须整理为独立脚本（纯标准库、argparse、`--help` 可用）放进新技能的 `scripts/`，正文只保留触发条件和用法。这样用户下次执行**不消耗任何 token**。
4. **原子性**：一个技能只解决一类问题。候选覆盖多类问题时，拆成多个技能分别生成。
5. **宁缺毋滥**：不满足沉淀标准的候选，明确告诉用户"不值得沉淀"及原因，绝不硬凑。

## 工作流程（严格按顺序执行）

### 第 0 步：确定输入来源

向用户确认或自行判断，三类输入：

- **A 项目目录**：给出项目根路径。
- **B 对话导出文件**：Kimi/ChatGPT/Claude 等导出的 `.json` / `.jsonl` / `.md` / `.txt`，可多个。
- **C 当前会话**：无法导出时，请用户把关键部分粘贴到一个临时文件（如 `_chat_export.md`），按 B 处理。注意：当前会话中你自己已经知道的内容可直接使用，不必绕道文件。

### 第 1 步：零 token 采集（运行脚本，不要自己通读原料）

```bash
# 项目目录输入（A）
python "${KIMI_SKILL_DIR}/scripts/scan_project.py" <项目路径> -o digest_project.json

# 对话文件输入（B/C），支持多个文件
python "${KIMI_SKILL_DIR}/scripts/parse_chat.py" <导出文件1> <导出文件2> -o digest_chat.json
```

> 非 Kimi 环境下把 `${KIMI_SKILL_DIR}` 替换为本技能目录的实际路径。

### 第 2 步：候选评分（零 token）

```bash
python "${KIMI_SKILL_DIR}/scripts/score_candidates.py" digest_chat.json digest_project.json -o shortlist.json
```

输入文件按实际有的传（可以只有 chat 或只有 project）。然后**读取 shortlist.json**——这是你唯一需要通读的采集产物（已封顶约 8KB），不要去读 digest 原文，除非 shortlist 中某个 preview 需要展开（此时用 `--show` 参数或 Read 对应片段）。

### 第 3 步：复用性判断（模型唯一重思考步骤）

对 shortlist 中每个候选，用**四问标准**打分（详见 `references/mining-guide.md`）：

1. **跨场景通用吗？**——去掉项目名/私有路径后，别的项目还用得上吗？
2. **重新发现成本高吗？**——是否包含踩坑、调参、多步流程、隐蔽依赖？一次 google 就能查到的不算。
3. **稳定可复现吗？**——是一次性数据/临时路径/未验证猜测，还是确定的操作？
4. **能部分脚本化吗？**——确定性步骤能否抽成脚本？

**≥3 个"是"→ 沉淀**；同时判定类型：

| 类型 | 特征 | 产出形态 |
|---|---|---|
| 脚本工具型 | 有可独立运行的代码 | SKILL.md + `scripts/*.py`（正文写触发和参数即可） |
| 流程型 | 多步骤有顺序依赖的操作 | 正文写步骤清单 + 每步命令 |
| 规范决策型 | 命名/结构/取舍类约定 | 正文写规则 + 正反例 |
| 领域知识型 | 踩坑修复、疑难排障 | 正文写"症状→原因→解法"条目 |

### 第 4 步：撰写新技能正文（模型写作）

- 写作模板与正反例见 `references/mining-guide.md`，正文必须包含：做什么、何时触发、用法/步骤、参数说明、边界与反例。
- 脚本工具型：把候选代码改写为独立脚本（见 mining-guide 的"脚本化改写清单"），调用示例统一写成 `python "${KIMI_SKILL_DIR}/scripts/<脚本>.py"`。
- **脱敏（强制）**：删除 API key/token/密码/内部 URL/真实用户路径，用 `<PROJECT_DIR>`、`<YOUR_KEY>` 等占位符替代。
- 把正文写入临时文件（如 `body.md`）。

### 第 5 步：脚手架生成（零 token）

```bash
python "${KIMI_SKILL_DIR}/scripts/make_skill.py" \
  --name <kebab-case技能名> \
  --description "<一句话功能+何时触发>" \
  --when-to-use "<触发场景描述>" \
  --body-file body.md \
  --script <整理好的脚本1.py> --script <脚本2.py> \
  --reference <可选参考文档.md> \
  --out <目标skills目录>
```

命名规范：全小写 + 连字符，动词-名词结构（如 `pdf-extract-tables`、`deploy-static-site`）。

### 第 6 步：校验（零 token，必须 PASS 才算完成）

```bash
python "${KIMI_SKILL_DIR}/scripts/validate_skill.py" <生成的技能目录>
```

任何 ERROR 必须修复后重跑，直到输出 `PASS`。

### 第 7 步：交付汇报

按 mining-guide.md 中的"提炼报告模板"向用户汇报：提炼了什么、为什么值得、新技能安装位置、触发方式（`/skill:<name>` 或自然语言触发）、脚本如何脱离模型独立运行（给出可直接复制到终端的命令）。

## 质量红线（校验脚本会拦截，写时就该避免）

- **禁止出现**：密钥、token、密码、内部地址、一次性数据（某次运行的输出/路径）、未验证的猜测。
- **description 必须含触发条件**（"当…时使用"），否则模型永远不知道何时调用它。
- **一个技能一件事**；发现候选混杂立即拆分。
- 脚本必须零第三方依赖（纯标准库），`--help` 可用，非零退出码表示失败。

## 脚本速查

| 脚本 | 用途 | 示例 |
|---|---|---|
| `scripts/scan_project.py` | 扫描项目：语言/框架/命令/入口/git热点/README 概要 | `python scripts/scan_project.py ~/myapp -o digest_project.json` |
| `scripts/parse_chat.py` | 解析对话导出：代码块(去重+频次)/命令/报错-修复对/用户意图 | `python scripts/parse_chat.py chat.json -o digest_chat.json` |
| `scripts/score_candidates.py` | 规则评分，输出候选 shortlist（模型只读这个） | `python scripts/score_candidates.py digest_chat.json -o shortlist.json` |
| `scripts/make_skill.py` | 生成技能目录：SKILL.md frontmatter + scripts/ + references/ | `python scripts/make_skill.py --name x --description "..." --body-file body.md --out skills` |
| `scripts/validate_skill.py` | 校验：frontmatter/命名/脱敏/脚本语法 | `python scripts/validate_skill.py skills/x` |

所有脚本都支持 `--help`，可完全脱离模型独立运行。

## 快速判例

**值得沉淀**：一段调试 3 轮才跑通的环境配置流程；一个重复出现的"报错→修复"配对；一段被反复请求生成的转换脚本；一套摸索出的目录组织规范。

**不值得沉淀**：只出现一次且无通用性的业务代码；包含真实密钥的一次性部署记录；未经确认的猜测性结论；纯项目数据（表格、路径清单）。
