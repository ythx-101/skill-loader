# Skill Loader

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Experimental](https://img.shields.io/badge/Status-Experimental-orange.svg)](https://github.com/ythx-101/skill-loader)

**skill-loader** 是给 OpenClaw 用户的 Claude Code skills 加载器：自动识别 `SKILL.md` / `.claude-plugin/marketplace.json` 格式的 skill，解析出名称、描述、触发词和指令内容，输出成 JSON，原 skill 一行都不用改。零依赖，纯 Python 标准库。

*A zero-dependency Python loader that detects and parses Claude Code skills (SKILL.md / marketplace.json) into JSON so they can be reused in OpenClaw. Codex and Gemini CLI support is planned.*

---

## 🎯 解决什么问题

Claude Code、Codex、Gemini CLI 的 Agent Skills 格式不同，不能直接在 OpenClaw 里用：

| 差异 | Claude Code | OpenClaw |
|------|-------------|----------|
| **文件结构** | `.claude-plugin/SKILL.md` | `skills/name/SKILL.md` |
| **工具调用** | `create_file()` | `write()` |
| **加载方式** | 启动时扫描 | 运行时按需 |

> 注：「工具调用」的映射目前为规划中，尚未实现。

skill-loader 做的事：**检测 → 解析 → 输出 JSON**，让跨平台复用 skill 不必改原仓库。

- ✅ **零修改**：只读，不改原 skill 文件
- ✅ **零依赖**：只用 Python 标准库
- ✅ **可扩展**：格式检测已覆盖 Codex / Gemini CLI，加载器计划中

---

## 📦 支持的格式

| 格式 | 状态 | 检测标志 |
|------|------|---------|
| **Claude Code Single（新格式）** | ✅ 已支持 | `.claude-plugin/SKILL.md`（优先） |
| **Claude Code Single（旧格式）** | ✅ 已支持 | 根目录 `SKILL.md` |
| **Claude Marketplace** | ✅ 已支持，两种变体：显式 `skills` 数组 / 自动发现 `skills/` 目录 | `.claude-plugin/marketplace.json` |
| **Codex** | ⏳ 计划中（目前只能检测，加载会提示尚未实现） | `codex.json` |
| **Gemini CLI** | ⏳ 计划中（目前只能检测，加载会提示尚未实现） | `skill.yaml` |

---

## 🚀 快速开始

**环境要求**：Python 3，无第三方依赖。

**安装**：

```bash
# Clone 到你的 OpenClaw skills 目录
cd /path/to/openclaw/workspace/skills
git clone https://github.com/ythx-101/skill-loader.git
```

**指定 skills 目录**（默认是 `/root/clawd/skills`）：

```bash
export SKILL_LOADER_DIR=/path/to/skills
```

**三条命令**（以下输出是用临时样例目录实际运行的结果，路径已替换为 `/path/to/skills`，`frontmatter` 字段略）：

```bash
# 扫描所有可用的 skills，按类型分组
python3 skill-loader/loader.py scan
```
```json
{
  "claude-marketplace": [
    "/path/to/skills/pack"
  ],
  "claude-single": [
    "/path/to/skills/draw"
  ]
}
```

```bash
# 加载指定 skill（单 skill 返回对象，marketplace 返回数组）
python3 skill-loader/loader.py load /path/to/skills/draw
```
```json
{
  "name": "draw",
  "description": "Draw diagrams. Triggers on \"画图\", \"diagram\"",
  "version": "1.0.0",
  "triggers": [
    "画图",
    "diagram"
  ],
  "content": "# Draw\nUse this to draw.",
  "source_type": "claude-single",
  "path": "/path/to/skills/draw"
}
```

```bash
# 查找触发词匹配的 skill（找不到时输出「未找到匹配的 skill」）
python3 skill-loader/loader.py find "帮我画图"
```

输出与 `load` 相同（返回第一个触发词出现在输入文本里的 skill）。

**示例**：加载一个真实的 Claude Marketplace skill

```bash
# 1. 克隆一个 Claude Code skill
cd skills
git clone https://github.com/axtonliu/axton-obsidian-visual-skills.git obsidian-visual

# 2. 自动识别并加载
python3 skill-loader/loader.py load obsidian-visual
# 输出一个 JSON 数组，每个子 skill 含 name / description / triggers / content / source_type
```

错误信息（目录不存在、无法识别的 skill 等）输出到 stderr，退出码为 1；stdout 只有 JSON 或「未找到匹配的 skill」。

---

## 🐍 在 Python 中使用

```python
import sys; sys.path.insert(0, "/path/to/skill-loader")
from loader import SkillLoader

loader = SkillLoader("/path/to/skills")
skill = loader.load_skill("/path/to/skills/obsidian-visual")  # marketplace 返回 list，single 返回 dict
prompt = skill[0]["content"] if isinstance(skill, list) else skill["content"]
```

---

## 🔧 工作原理

1. **检测**：按顺序判断目录里有 `.claude-plugin/marketplace.json`、`.claude-plugin/SKILL.md` 或根目录 `SKILL.md`、`codex.json`、`skill.yaml`，得到 skill 类型。
2. **解析**：读取 `SKILL.md`（或 marketplace 里列出 / 自动发现的多个 `SKILL.md`），提取 frontmatter 的 name / description，从 description 里找 `Triggers on "a", "b"` 提取触发词，其余正文作为 `content`。
3. **映射（规划中，尚未实现）**：把 Claude Code 的工具调用换成 OpenClaw 的等价调用。
4. **注入**：由 OpenClaw 侧完成，不是本仓库实现的。

**配合 OpenClaw 使用时**（以下由 OpenClaw 负责，本仓库不包含这部分代码，无法在此验证）：把外部 skill 克隆到 skills 目录后，由 OpenClaw 读取 skill-loader 的 JSON 输出，并在对话中按触发词匹配 skill、把 `content` 注入上下文。

### 工具映射（规划中，尚未实现）

| Claude Code 工具 | OpenClaw 等价 | 计划实现方式 |
|-----------------|--------------|------------|
| `create_file(path, content)` | `write(path, content)` | 直接映射 |
| `edit_file(path, changes)` | `read()` + `edit()` | 两步操作 |
| `search_files(pattern)` | `exec("grep ...")` | Shell 包装 |
| `run_terminal(cmd)` | `exec(cmd)` | 直接映射 |

---

## 🧭 适用场景 / 不适用场景

**适用**
- 手上有 Claude Code skill 仓库，想在 OpenClaw 里复用
- 想批量查看某个目录下有哪些 skills、各自的触发词
- 需要把 `SKILL.md` 转成 JSON 给自己的 AI Agent 使用

**不适用**
- 需要自动转换工具调用（还没实现）
- Codex / Gemini CLI 格式的加载（计划中）
- 需要完整 YAML frontmatter 解析（目前只做简单的 `key: value` 单行解析）

---

## ⚖️ 与其他做法对比

| 做法 | 特点 |
|------|------|
| 手动复制 `SKILL.md` 内容 | 简单直接，但多 skill 的 marketplace 仓库要逐个处理，没有统一格式，也没有触发词匹配 |
| **skill-loader** | 自动识别单 skill 与 marketplace（两种变体），统一 JSON 输出，支持触发词匹配；工具映射尚未实现 |
| 直接用 Claude Code | 原生支持 Claude Code skills，但不在 OpenClaw 里 |

---

## ❓ FAQ

**Claude Code 的 skill 能在 OpenClaw 里用吗？ / How do I use Claude Code skills in OpenClaw?**
把 skill 仓库放进 skills 目录，用 `loader.py load` 解析成 JSON，取出 `content` 作为指令即可（见「在 Python 中使用」）。把 JSON 接入对话由 OpenClaw 侧负责。Clone the skill repo, run `loader.py load <dir>`, and use the `content` field.

**skill-loader 支持哪些 skill 格式？**
Claude Code 的单 skill（`.claude-plugin/SKILL.md` 或根目录 `SKILL.md`）和 `marketplace.json`（显式 `skills` 数组或自动发现 `skills/` 目录）。

**支持 Codex / Gemini CLI skills 吗？**
目前只能检测（`codex.json` / `skill.yaml`），加载会提示「尚未实现」，计划中。

**触发词是怎么提取的？**
从 frontmatter 的 description 里找 `Triggers on "a", "b"` 这种写法，取引号里的词；没有就是空列表。

**需要安装依赖吗？**
不需要，只用 Python 标准库。

**会联网吗？**
只有在交互终端里运行时，每天最多请求一次 GitHub Releases API 检查新版本（结果缓存在 `~/.cache/openclaw-updates/`），提示输出到 stderr。可以用 `SKILL_LOADER_NO_UPDATE_CHECK=1` 关掉。

**会修改原 skill 文件吗？**
不会，只读。

---

## 📂 目录结构

```
skill-loader/
├── README.md          # 本文档
├── llms.txt           # 给 LLM 的项目摘要
├── loader.py          # 核心加载器 + CLI
├── version_check.py   # 版本检查（可用环境变量关闭）
├── tests/             # 单元测试（unittest）
│   └── test_loader.py
├── VERSION
├── CHANGELOG.md
└── LICENSE
```

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

---

## ✅ 已验证

- **[axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills)**（Claude Marketplace，显式 `skills` 数组）：解析出 3 个子 skill 的 name / description / content
- **[lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill)**（Claude Marketplace，自动发现 `skills/` 目录变体）
- **[GBSOSS/skill-from-masters](https://github.com/GBSOSS/skill-from-masters)**（旧的根目录 `SKILL.md` 单文件格式）

以上来自 CHANGELOG 记录的测试。

---

## 🗺️ 路线图

- [x] **v0.1.0** - Claude Code 支持（Single + Marketplace）
- [ ] **v0.2.0** - Codex skill 支持
- [ ] **v0.3.0** - Gemini CLI skill 支持
- [ ] **v0.4.0** - 自动工具映射优化
- [ ] **v1.0.0** - 生产就绪 + 完整测试覆盖

---

## 🤝 贡献

欢迎 PR！特别是：
- 新的 skill 格式适配器
- 更多已验证的 skill 案例
- 工具映射优化
- 文档改进

提交前请确保：
1. 代码能跑通
2. 添加了示例
3. 更新了 README

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 👤 作者

**林月** (@YuLin807)
- GitHub: [@ythx-101](https://github.com/ythx-101)
- X/Twitter: [@YuLin807](https://x.com/YuLin807)

**致谢**：小灵（OpenClaw Agent）协助开发

---

**版本**: v0.1.3 (Experimental)  
**最后更新**: 2026-11-12
