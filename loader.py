#!/usr/bin/env python3
"""
OpenClaw Skill Loader - 通用 Skill 适配器
支持 Claude Code / Codex / Gemini CLI 格式的 skills
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class SkillLoader:
    """通用 Skill 加载器"""
    
    SKILL_TYPES = {
        'claude-marketplace': lambda p: os.path.exists(f"{p}/.claude-plugin/marketplace.json"),
        'claude-single': lambda p: os.path.exists(f"{p}/.claude-plugin/SKILL.md") or os.path.exists(f"{p}/SKILL.md"),
        'codex': lambda p: os.path.exists(f"{p}/codex.json"),
        'gemini-cli': lambda p: os.path.exists(f"{p}/skill.yaml"),
    }
    
    def __init__(self, skills_dir: str = "/root/clawd/skills"):
        self.skills_dir = Path(skills_dir)
        self.loaded_skills = {}
    
    def detect_skill_type(self, skill_path: Path) -> Optional[str]:
        """检测 skill 类型"""
        for skill_type, detector in self.SKILL_TYPES.items():
            if detector(str(skill_path)):
                return skill_type
        return None
    
    def scan_skills(self) -> Dict[str, List[str]]:
        """扫描 skills 目录，返回所有可用的 skills"""
        skills = {}
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue
            
            skill_type = self.detect_skill_type(skill_dir)
            if skill_type:
                if skill_type not in skills:
                    skills[skill_type] = []
                skills[skill_type].append(str(skill_dir))
        
        return skills
    
    def load_claude_marketplace(self, skill_path: Path) -> List[Dict[str, Any]]:
        """加载 Claude Marketplace 格式的 skill pack"""
        marketplace_file = skill_path / ".claude-plugin" / "marketplace.json"
        
        with open(marketplace_file, 'r', encoding='utf-8') as f:
            marketplace = json.load(f)
        
        skills = []
        
        for plugin in marketplace.get('plugins', []):
            # 方案1: 如果有 skills 字段（axtonliu 格式）
            if 'skills' in plugin:
                for skill_ref in plugin['skills']:
                    skill_md_path = skill_path / skill_ref / "SKILL.md"
                    if skill_md_path.exists():
                        skill_data = self.parse_skill_md(skill_md_path)
                        skill_data['source_type'] = 'claude-marketplace'
                        skill_data['path'] = str(skill_md_path.parent)
                        skills.append(skill_data)
            
            # 方案2: 如果没有 skills 字段，检查 skills/ 目录（lackeyjb 格式）
            else:
                skills_dir = skill_path / "skills"
                if skills_dir.exists():
                    for skill_dir in skills_dir.iterdir():
                        if skill_dir.is_dir():
                            skill_md_path = skill_dir / "SKILL.md"
                            if skill_md_path.exists():
                                skill_data = self.parse_skill_md(skill_md_path)
                                skill_data['source_type'] = 'claude-marketplace'
                                skill_data['path'] = str(skill_md_path.parent)
                                skills.append(skill_data)
        
        return skills
    
    def load_claude_single(self, skill_path: Path) -> Dict[str, Any]:
        """加载单一 Claude Code SKILL.md（支持新旧格式）"""
        # 优先检查新格式 (.claude-plugin/SKILL.md)
        skill_md_path = skill_path / ".claude-plugin" / "SKILL.md"
        if not skill_md_path.exists():
            # 回退到旧格式 (SKILL.md)
            skill_md_path = skill_path / "SKILL.md"
        
        skill_data = self.parse_skill_md(skill_md_path)
        skill_data['source_type'] = 'claude-single'
        skill_data['path'] = str(skill_path)
        return skill_data
    
    def parse_skill_md(self, md_path: Path) -> Dict[str, Any]:
        """解析 SKILL.md 文件"""
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 frontmatter
        frontmatter = {}
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                fm_text = content[3:end].strip()
                for line in fm_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
                content = content[end+3:].strip()
        
        # 提取触发词
        triggers = []
        if 'description' in frontmatter:
            # 从 description 中提取触发词
            trigger_match = re.search(r'Triggers on (.+)', frontmatter['description'])
            if trigger_match:
                trigger_str = trigger_match.group(1)
                # 解析引号内的触发词
                triggers = re.findall(r'"([^"]+)"', trigger_str)
        
        return {
            'name': frontmatter.get('name', md_path.parent.name),
            'description': frontmatter.get('description', ''),
            'version': frontmatter.get('metadata', {}).get('version', '1.0.0') if isinstance(frontmatter.get('metadata'), dict) else frontmatter.get('version', '1.0.0'),
            'triggers': triggers,
            'content': content,
            'frontmatter': frontmatter
        }
    
    def load_skill(self, skill_path: str) -> Dict[str, Any]:
        """加载指定路径的 skill"""
        path = Path(skill_path)
        skill_type = self.detect_skill_type(path)
        
        if not skill_type:
            raise ValueError(f"无法识别 skill 类型: {skill_path}")
        
        if skill_type == 'claude-marketplace':
            return self.load_claude_marketplace(path)
        elif skill_type == 'claude-single':
            return self.load_claude_single(path)
        elif skill_type == 'codex':
            raise NotImplementedError("Codex skills 尚未实现")
        elif skill_type == 'gemini-cli':
            raise NotImplementedError("Gemini CLI skills 尚未实现")
    
    def find_skill_by_trigger(self, text: str) -> Optional[Dict[str, Any]]:
        """根据触发词查找匹配的 skill"""
        all_skills = self.scan_skills()
        
        for skill_type, paths in all_skills.items():
            for path in paths:
                try:
                    skills = self.load_skill(path)
                    # 处理单个 skill 或 skill list
                    if isinstance(skills, dict):
                        skills = [skills]
                    
                    for skill in skills:
                        for trigger in skill.get('triggers', []):
                            if trigger.lower() in text.lower():
                                return skill
                except Exception as e:
                    print(f"加载 skill 失败: {path} - {e}")
                    continue
        
        return None


def main():
    """CLI 入口"""
    import sys
    
    loader = SkillLoader()
    
    if len(sys.argv) < 2:
        print("用法: python loader.py <scan|load|find> [path|trigger]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "scan":
        skills = loader.scan_skills()
        print(json.dumps(skills, indent=2, ensure_ascii=False))
    
    elif action == "load" and len(sys.argv) == 3:
        skill = loader.load_skill(sys.argv[2])
        print(json.dumps(skill, indent=2, ensure_ascii=False))
    
    elif action == "find" and len(sys.argv) == 3:
        skill = loader.find_skill_by_trigger(sys.argv[2])
        if skill:
            print(json.dumps(skill, indent=2, ensure_ascii=False))
        else:
            print("未找到匹配的 skill")
    
    else:
        print("未知操作")
        sys.exit(1)


if __name__ == "__main__":
    main()
