# Skill / Agent / MCP 的资源检索与统合管理

> 本文档由一次 TRAE 会话迁移而来，记录：① 微信文章提到的两个 Claude 系 Skill；② 如何在公开渠道用"需求+关键词"做模糊搜索；③ 如何在 TRAE、ChatGPT 桌面版、VSCode 三者间统合管理 Skill 与 Agent。

---

## 1. 文章提到的两个 Skill

来源文章：公众号「计量经济圈」《AI agents写Stata总翻车? 装上这两个skills，从CSDID到RDD一键生成, 计量效率直接拉满.》

两个 Skill 均来自同一开源仓库：

> **GitHub: [dylantmoore/stata-skill](https://github.com/dylantmoore/stata-skill)**

| Skill | 作用 |
|---|---|
| `stata` | Stata 计量全流程参考库：37 份核心文档（数据清理、线性/面板/时间序列、因果推断 DiD/RDD/Matching、Mata 矩阵编程、绘图与报告）+ 20 个社区包指南（reghdfe、csdid、did_multiplegt、rdrobust、psmatch2、synth、ivreg2、xtabond2 等），让 AI 正确写出 CSDID、RDD、面板等计量代码 |
| `stata-c-plugins` | Stata C/C++ 插件开发专家：教 AI 用 C 插件给 Stata 提速，并给出把 Python/R 存量包翻译成 Stata 可调 C 插件的完整工作流（SDK、1-indexed 索引、内存安全、跨平台编译、pthreads 优化、测试与打包） |

安装方式（把仓库加为 Claude Code 插件市场）：

```
/plugin marketplace add dylantmoore/stata-skill
/plugin install stata            # 仅 Stata 参考
/plugin install stata-c-plugins  # 仅 C 插件开发
/plugin install stata-bundle     # 两者全装
```

作者还维护了合集 [dylantmoore/claude-plugins](https://github.com/dylantmoore/claude-plugins)。该仓库也是学习如何构建 Claude Code Skill 的良好范本（渐进式披露 progressive disclosure 的实践）。

---

## 2. 怎样在公开渠道搜索优质的 Skill / Agent / MCP（含模糊搜索）

### 2.1 主要渠道（MCP 与 Skills 是两套生态）

**MCP 目录站：**
- [Glama](https://glama.ai) —— 8.3 万+ server，带质量/安全评分、侧边对比、浏览器内测试，可一键部署
- [PulseMCP](https://pulsemcp.com) —— 每日更新，实验性 server 往往比别处早出现
- [Smithery](https://smithery.ai) —— 可 CLI 一键安装、也可用其托管远程 server
- mcp.so —— 社区与实验性质项目多，内置 playground 可实测
- 官方 MCP Registry —— 保真、规范兼容，但不做排序与推荐

**Skills 库：**
- 官方 [anthropics/skills](https://github.com/anthropics/skills)
- [obra/superpowers](https://github.com/obra/superpowers) —— 知名方法论级踩过坑的技能库
- [everything-claude-code/everything-claude-code](https://github.com/everything-claude-code/everything-claude-code)
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [claudskills.com](https://claudskills.com) —— 19 万+ 条目的聚合搜索站，跨 GitHub/GitLab/HuggingFace/Reddit/YouTube 等 26 个源

**GitHub 直接搜：** 用 topic 标签 `claude-skills`、`claude-code-marketplace`、`claude-plugins`、`mcp-server`，按 star 与最近更新排序。

### 2.2 只有需求和关键词时的模糊搜索法

1. **需求 → 关键词翻译**：把中文需求翻译成英文能力词，拼接成 `能力词 + skill/mcp/agent`。例：SE("SEC 财报提取") → `sec filings extraction mcp server`；不准就换同义词重试。
2. **描述性整句搜索**：把需求写成完整英文句子直接搜（目录站与搜索引擎的语义检索能匹配意图）。
3. **让 AI 拆解需求**：让当前对话的 LLM 把需求拆成 5–8 个能力点，再逐点去目录站 / GitHub 搜，命中率远高于凭直觉。
4. **目录站内过滤**：Glama 按分类+评分、PulseMCP 按"今日新增"，比 GitHub 泛搜更快锁定。
5. **交叉验证质量**：同一需求在 2–3 个目录各搜一次，对比 star、最新 commit、README 完整度；避开几个月不更新的死项目。
6. **顺藤摸瓜**：看优质 Skill 的依赖与 README 引用的项目，"相关推荐"质量往往高。
7. **留档记录**：把每次搜到的优质资源登记到自己的 registry 表（见下节）。

---

## 3. 怎样统合管理 TRAE + ChatGPT 桌面版（Codex）+ VSCode 的 Skill / Agent

### 3.1 三者生态差异

| 工具 | 配置位置 |
|---|---|
| TRAE | `~/.trae-cn/plugins`；MCP 在设置里配置 |
| ChatGPT 桌面版 / Codex | `~/.codex/skills`、`~/.codex/AGENTS.md`、`~/.codex/config.toml`（MCP） |
| VSCode | 依扩展而定：Codex 扩展 / Continue / Cline / Roo Code 各自管理各自的 MCP 与规则 |

好消息：**Anthropic 的 SKILL.md 已是跨工具事实标准**，同一份 Skill 拷到各工具目录即可用（TRAE、Codex、Cursor 均兼容）。

### 3.2 统合思路：一份主库 + 部署脚本 + 清单

核心理念：**仓库统一存、脚本统一发、清单统一记、按需启用**。

1. **单一来源仓库**：建 `~/agent-skill-library` 存所有 Skill（`SKILL.md` + 参考文档）。
2. **脚本化部署**：写同步脚本，把主库按需拷贝 / 符号链接到 `~/.trae-cn/skills`、`~/.codex/skills` 及各 VSCode 扩展的 skill 目录；改一处一键全端同步。
3. **MCP 主清单 + 生成器**：维护一份 `master-mcp.json`（所有 server 定义），脚本为每个工具生成对应配置（TRAE settings / Codex config.toml / VSCode mcp.json）；装新 server 只改主清单。
4. **规则分层**：全局规范放 `~/.codex/AGENTS.md` 与 TRAE 全局规则；项目特定规则放项目级 AGENTS.md，避免各处重复维护。
5. **注册清单表**：维护 `registry.md`（名称/用途/来源仓库/版本/已部署端），定期脚本对比各目录差异，防漏更新。
6. **按需启用，别全装**：Skill 装多会稀释上下文、降低响应质量。高频通用的放全局，低频专业的（如本文的 stata 系列）走 marketplace 按项目按需安装。
7. **版本固定**：用 git submodule 或 vendor 固定版本，升级时手动挑选，避免上游更新破坏现有工作流。

### 3.3 一句话原则

> 一份主库集中存 Skill，脚本统一分发到各工具，用 registry 清单记录版本与部署状态，再按需启用——即可在多个工具间维持一致且可控的 Skill/Agent 资产。