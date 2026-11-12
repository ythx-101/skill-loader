import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loader import SkillLoader  # noqa: E402
import version_check  # noqa: E402


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def skill_md(name, desc="A skill", body="Body text"):
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n{body}\n"


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_legacy_single(self):
        d = self.root / "legacy"
        write(d / "SKILL.md", skill_md("draw", 'Draw. Triggers on "画图", "diagram"'))
        loader = SkillLoader(str(self.root))
        self.assertEqual(loader.detect_skill_type(d), "claude-single")
        s = loader.load_skill(str(d))
        self.assertEqual(s["name"], "draw")
        self.assertEqual(s["triggers"], ["画图", "diagram"])
        self.assertEqual(s["source_type"], "claude-single")

    def test_plugin_dir_preferred_over_root(self):
        d = self.root / "both"
        write(d / "SKILL.md", skill_md("old"))
        write(d / ".claude-plugin" / "SKILL.md", skill_md("new"))
        self.assertEqual(SkillLoader(str(self.root)).load_skill(str(d))["name"], "new")

    def test_marketplace_explicit_skills(self):
        d = self.root / "mk1"
        write(d / ".claude-plugin" / "marketplace.json",
              json.dumps({"plugins": [{"skills": ["./a", "./b"]}]}))
        write(d / "a" / "SKILL.md", skill_md("a"))
        write(d / "b" / "SKILL.md", skill_md("b"))
        res = SkillLoader(str(self.root)).load_skill(str(d))
        self.assertIsInstance(res, list)
        self.assertEqual(sorted(x["name"] for x in res), ["a", "b"])

    def test_marketplace_autodiscover(self):
        d = self.root / "mk2"
        write(d / ".claude-plugin" / "marketplace.json",
              json.dumps({"plugins": [{"name": "p"}]}))
        write(d / "skills" / "x" / "SKILL.md", skill_md("x"))
        res = SkillLoader(str(self.root)).load_skill(str(d))
        self.assertEqual([x["name"] for x in res], ["x"])

    def test_find_by_trigger(self):
        write(self.root / "draw" / "SKILL.md",
              skill_md("draw", 'Draw. Triggers on "画图", "diagram"'))
        found = SkillLoader(str(self.root)).find_skill_by_trigger("帮我画图")
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "draw")
        self.assertIsNone(SkillLoader(str(self.root)).find_skill_by_trigger("nothing"))

    def test_unknown_dir_raises_value_error(self):
        d = self.root / "empty"
        d.mkdir()
        with self.assertRaises(ValueError):
            SkillLoader(str(self.root)).load_skill(str(d))

    def test_missing_dir_raises(self):
        with self.assertRaises(FileNotFoundError):
            SkillLoader(str(self.root / "nope")).scan_skills()


class VersionTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(version_check._parse("0.1.2"), (0, 1, 2))
        self.assertEqual(version_check._parse("v1.0.0"), (1, 0, 0))
        self.assertIsNone(version_check._parse("abc"))
        self.assertIsNone(version_check._parse(""))

    def test_is_newer(self):
        self.assertFalse(version_check._is_newer("0.1.2", "0.1.3"))
        self.assertTrue(version_check._is_newer("0.1.3", "0.1.2"))
        self.assertFalse(version_check._is_newer("0.1.2", "0.1.2"))
        self.assertFalse(version_check._is_newer("bad", "0.1.2"))
        self.assertFalse(version_check._is_newer("0.1.3", "bad"))

    def test_env_switch_starts_no_thread(self):
        with mock.patch.dict(os.environ, {"SKILL_LOADER_NO_UPDATE_CHECK": "1"}), \
             mock.patch.object(version_check.sys.stderr, "isatty", return_value=True, create=True), \
             mock.patch.object(version_check.threading, "Thread") as thread:
            version_check.check_for_update("x/y")
            thread.assert_not_called()


if __name__ == "__main__":
    unittest.main()
