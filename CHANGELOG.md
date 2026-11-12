# Changelog

## [0.1.3] - 2026-11-12

### Fixed
- CLI entry indentation error (the version check added after 0.1.2 left `main()` inside the `except` block, so the script could not run)
- `find` diagnostics ("加载 skill 失败") now go to stderr instead of mixing into JSON on stdout
- Version check only prompts when the remote version is newer than the local one
- `scan` reports a one-line error (exit code 1) instead of a traceback when the skills directory does not exist

### Added
- `SKILL_LOADER_DIR` environment variable to set the skills directory (default unchanged: `/root/clawd/skills`)
- `SKILL_LOADER_NO_UPDATE_CHECK=1` environment variable to disable the update check
- `.gitignore`, unit tests (`tests/test_loader.py`, standard library `unittest`), `llms.txt`

### Changed
- Removed the committed `__pycache__` from the repository
- README rewritten to match what the code actually implements

## [0.1.2] - 2026-02-16

### Fixed
- **Marketplace format variants support**: Now handles both axtonliu-style (explicit `skills` array) and lackeyjb-style (auto-discover from `skills/` directory) marketplace formats
- Successfully tested with `playwright-skill` (lackeyjb/playwright-skill, 1693 stars)

### Changed
- Updated `load_claude_marketplace()` to detect and handle two marketplace format variants:
  - Variant 1: `marketplace.json` with explicit `skills: []` array
  - Variant 2: Auto-discover all SKILL.md files in `skills/` directory when `skills` field is missing

### Validation
```bash
# Now works with both marketplace formats
python3 loader.py load /path/to/playwright-skill  # lackeyjb style
python3 loader.py load /path/to/obsidian-visual   # axtonliu style
```

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
