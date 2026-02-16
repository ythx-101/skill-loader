# Skill Loader

> Universal skill adapter for OpenClaw - load Claude Code, Codex, and Gemini CLI skills seamlessly

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Experimental](https://img.shields.io/badge/Status-Experimental-orange.svg)](https://github.com/ythx-101/skill-loader)

**打通 AI Agent 生态 - 让不同平台的 skills 无缝互通**

---

## 🎯 问题

Claude Code、Codex、Gemini CLI 的 skills 格式不同，不能直接在 OpenClaw 里用：

| 差异 | Claude Code | OpenClaw |
|------|-------------|----------|
| **文件结构** | `.claude-plugin/SKILL.md` | `skills/name/SKILL.md` |
| **工具调用** | `create_file()` | `write()` |
| **加载方式** | 启动时扫描 | 运行时按需 |

## ✨ 解决方案

四步自动适配：**检测 → 解析 → 映射 → 注入**

- ✅ **零修改**：不改原 skill 代码
- ✅ **自动化**：用户无感知
- ✅ **可扩展**：支持多种 skill 格式

---

## 🚀 快速开始

### 安装

```bash
# Clone 到你的 OpenClaw skills 目录
cd /path/to/openclaw/workspace/skills
git clone https://github.com/ythx-101/skill-loader.git
```

### 使用

```bash
# 扫描所有可用的 skills
python3 skill-loader/loader.py scan

# 加载指定 skill
python3 skill-loader/loader.py load /path/to/skill

# 查找触发词匹配的 skill
python3 skill-loader/loader.py find "画个架构图"
```

### 示例

```bash
# 1. 克隆一个 Claude Code skill
cd skills
git clone https://github.com/axtonliu/axton-obsidian-visual-skills.git obsidian-visual

# 2. 自动识别并加载
python3 skill-loader/loader.py load obsidian-visual

# 输出：
# [
#   {
#     "name": "excalidraw-diagram",
#     "description": "...",
#     "triggers": ["画图", "Excalidraw", ...],
#     "content": "...",
#     "source_type": "claude-marketplace"
#   },
#   ...
# ]
```

---

## 📦 支持的格式

| 格式 | 状态 | 检测标志 |
|------|------|---------|
| **Claude Code Single** | ✅ 已支持 | `.claude-plugin/SKILL.md` |
| **Claude Marketplace** | ✅ 已支持 | `.claude-plugin/marketplace.json` |
| **Codex** | ⏳ 计划中 | `codex.json` |
| **Gemini CLI** | ⏳ 计划中 | `skill.yaml` |

---

## 🚀 使用方法

### 方式1: 克隆外部 skill

```bash
cd /root/clawd/skills
git clone https://github.com/user/some-claude-skill.git
```

OpenClaw 会自动识别并加载。

### 方式2: 手动触发加载

在对话中说：
```
"加载 excalidraw skill"
"画个架构图"（自动匹配 skill 触发词）
```

### 方式3: Python API

```python
from skills.skill_loader import load_skill

skill = load_skill('/root/clawd/skills/obsidian-visual')
skill.execute('画个流程图')
```

---

## 🔧 工作原理

### 1. 自动检测

```python
def detect_skill_type(skill_dir):
    if os.path.exists(f"{skill_dir}/.claude-plugin/marketplace.json"):
        return "claude-marketplace"
    elif os.path.exists(f"{skill_dir}/.claude-plugin/SKILL.md"):
        return "claude-single"
    elif os.path.exists(f"{skill_dir}/codex.json"):
        return "codex"
    elif os.path.exists(f"{skill_dir}/skill.yaml"):
        return "gemini-cli"
    return None
```

### 2. 解析 Skill

- 读取 SKILL.md 内容
- 提取 frontmatter（name / description / triggers）
- 提取指令部分（Workflow / Design Rules / Examples）

### 3. 工具映射

| Claude Code 工具 | OpenClaw 等价 | 实现 |
|-----------------|--------------|------|
| `create_file(path, content)` | `write(path, content)` | 直接映射 |
| `edit_file(path, changes)` | `read()` + `edit()` | 两步操作 |
| `search_files(pattern)` | `exec("grep ...")` | Shell 包装 |
| `run_terminal(cmd)` | `exec(cmd)` | 直接映射 |

### 4. 运行时注入

当用户触发 skill 时：
```python
# 1. 读取 skill prompt
prompt = parse_skill_md(skill_path)

# 2. 注入到当前上下文
context = f"{current_context}\n\n{prompt}"

# 3. 执行用户请求
execute_with_context(context, user_request)
```

---

## 📂 目录结构

```
skills/skill-loader/
├── README.md              # 本文档
├── loader.py              # 核心加载器
├── adapters/              # 适配器目录
│   ├── claude_code.py     # Claude Code 适配器
│   ├── codex.py           # Codex 适配器（待实现）
│   └── gemini_cli.py      # Gemini CLI 适配器（待实现）
├── tools_mapping.py       # 工具映射表
└── tests/                 # 测试用例
    └── test_loader.py
```

---

## ✅ 已验证

**[axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills)** (Claude Marketplace)
- ✅ 自动识别 3 个子 skill（excalidraw / mermaid / canvas）
- ✅ 工具映射正确（`create_file` → `write`）
- ✅ 在 OpenClaw 里完全可用

---

## 🛠️ 工作原理

### 1. 检测 Skill 类型

```python
def detect_skill_type(skill_path):
    if exists(f"{skill_path}/.claude-plugin/marketplace.json"):
        return "claude-marketplace"
    elif exists(f"{skill_path}/.claude-plugin/SKILL.md"):
        return "claude-single"
    # ... 其他格式
```

### 2. 解析 Skill 文档

- 读取 `SKILL.md` / `marketplace.json`
- 提取：name, description, triggers, workflow
- 构建结构化数据

### 3. 工具映射

| Claude Code | OpenClaw | 实现 |
|-------------|----------|------|
| `create_file(path, content)` | `write(path, content)` | 直接映射 |
| `edit_file(path, changes)` | `read() + edit()` | 两步操作 |
| `search_files(pattern)` | `exec("grep...")` | Shell 包装 |
| `run_terminal(cmd)` | `exec(cmd)` | 直接映射 |

### 4. 运行时注入

```python
# 1. 加载 skill
skill = loader.load_skill(path)

# 2. 提取 prompt
prompt = skill['content']

# 3. 注入到上下文
# OpenClaw 把 skill 当作原生能力执行
```

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

**版本**: v0.1.0 (Experimental)  
**最后更新**: 2026-02-16
