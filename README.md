# OpenClaw Skill Loader

**通用 Claude Code / Codex / Gemini CLI Skill 适配器**

让 OpenClaw 能够自动识别并使用市面上所有为 Claude Code、Codex、Gemini CLI 设计的 skills。

---

## 🎯 核心功能

- ✅ 自动检测 skill 格式（Claude Code / Codex / Gemini CLI）
- ✅ 解析 skill 文档（SKILL.md / marketplace.json）
- ✅ 工具映射（Claude Code 工具 → OpenClaw 工具）
- ✅ 运行时加载（无需预编译）

---

## 📦 支持的 Skill 格式

### 1. Claude Code Skills

**标准格式**：
```
skill-name/
├── .claude-plugin/
│   └── SKILL.md          # 单一 skill
└── README.md
```

**Marketplace 格式**：
```
skill-pack/
├── .claude-plugin/
│   └── marketplace.json  # 索引多个子 skills
├── skill-1/
│   └── SKILL.md
├── skill-2/
│   └── SKILL.md
└── README.md
```

### 2. Codex Skills
（待实现）

### 3. Gemini CLI Skills
（待实现）

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

## ✅ 已验证的 Skills

- ✅ **axton-obsidian-visual-skills** — Excalidraw / Mermaid / Canvas 生成器
  - 格式：Claude Marketplace
  - 状态：已适配，完全可用
  - 示例：生成记忆系统架构图

---

## 🔜 路线图

- [x] Phase 1: Claude Code 单一 skill 支持
- [x] Phase 2: Claude Marketplace 格式支持
- [x] Phase 3: Excalidraw 生成器验证
- [ ] Phase 4: Mermaid / Canvas 适配
- [ ] Phase 5: Codex skill 支持
- [ ] Phase 6: Gemini CLI skill 支持
- [ ] Phase 7: 自动 skill 市场（从 GitHub 安装）

---

## 🤝 贡献

欢迎提交 PR 添加更多适配器！

---

**作者**: 小灵（OpenClaw Agent）  
**审校**: 林月 (@YuLin807)  
**版本**: 0.1.0  
**最后更新**: 2026-02-16
