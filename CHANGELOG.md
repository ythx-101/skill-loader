# Changelog

## [0.1.1] - 2026-02-16

### Fixed
- **Legacy Claude Code format support**: Now detects both new (`.claude-plugin/SKILL.md`) and old (`SKILL.md`) Claude Code single skill formats
- Successfully tested with `skill-from-masters` (GBSOSS/skill-from-masters)

### Changed
- Updated `detect_skill_type()` to check for both `.claude-plugin/SKILL.md` and `SKILL.md`
- Updated `load_claude_single()` to fallback to root `SKILL.md` if `.claude-plugin/` directory doesn't exist

## [0.1.0] - 2026-02-15

### Added
- Initial release
- Support for Claude Code Marketplace format (multiple skills in one repo)
- Support for Claude Code Single Skill format
- Auto-detection of skill types
- Basic tool mapping (placeholder)
- CLI interface: `scan`, `load`, `find`
