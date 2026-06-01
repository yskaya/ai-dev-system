"""
Golden-file tests: build tests/fixtures/recipes and match tests/expected/{cursor,claude}.

Regenerate expected output after template or build.py changes:
  python3 tests/generate_expected.py
"""

from __future__ import annotations

import unittest

from helpers import (
    FixtureBuildTestCase,
    OutputCase,
    extract_skills_mentions,
    read_text,
    split_frontmatter,
)


# --- Golden files (full document match) ---------------------------------------

RULE_CASES = [
    OutputCase("rule-always", "rules/rule-always.mdc", ("cursor",)),
    OutputCase("rule-always", "rules/rule-always.md", ("claude",)),
    OutputCase("rule-scoped", "rules/rule-scoped.mdc", ("cursor",)),
    OutputCase("rule-scoped", "rules/rule-scoped.md", ("claude",)),
]

SKILL_CASES = [
    OutputCase("skill-plain", "skills/skill-plain/SKILL.md"),
    OutputCase("skill-scoped", "skills/skill-scoped/SKILL.md"),
    OutputCase("skill-output", "skills/skill-output/SKILL.md"),
]

COMMAND_CASES = [
    OutputCase("cmd-minimal", "commands/cmd-minimal.md"),
    OutputCase("cmd-skills-direct", "commands/cmd-skills-direct.md"),
    OutputCase("cmd-skills-skillset", "commands/cmd-skills-skillset.md"),
    OutputCase("cmd-next-rich", "commands/cmd-next-rich.md"),
    OutputCase("cmd-next-branches", "commands/cmd-next-branches.md"),
]


class TestRuleGoldenFiles(FixtureBuildTestCase):
    def test_rule_outputs(self) -> None:
        for case in RULE_CASES:
            with self.subTest(case.id, target=case.targets):
                self.assert_matches_expected(case)


class TestSkillGoldenFiles(FixtureBuildTestCase):
    def test_skill_outputs(self) -> None:
        for case in SKILL_CASES:
            with self.subTest(case.id):
                self.assert_matches_expected(case)


class TestCommandGoldenFiles(FixtureBuildTestCase):
    def test_command_outputs(self) -> None:
        for case in COMMAND_CASES:
            with self.subTest(case.id):
                self.assert_matches_expected(case)


# --- Semantic checks (recipe props → built artifacts) -------------------------

class TestFixtureRuleSemantics(FixtureBuildTestCase):
    def test_cursor_always_apply_omits_globs(self) -> None:
        path = self.dist_dir / "cursor/rules/rule-always.mdc"
        fm, _ = split_frontmatter(read_text(path))
        self.assertTrue(fm.get("alwaysApply"))
        self.assertNotIn("globs", fm)

    def test_cursor_scoped_rule_includes_globs(self) -> None:
        path = self.dist_dir / "cursor/rules/rule-scoped.mdc"
        fm, _ = split_frontmatter(read_text(path))
        self.assertFalse(fm.get("alwaysApply"))
        self.assertEqual(fm.get("globs"), ["**/*.ts", "**/*.tsx"])

    def test_claude_always_rule_has_empty_frontmatter(self) -> None:
        path = self.dist_dir / "claude/rules/rule-always.md"
        fm, body = split_frontmatter(read_text(path))
        self.assertNotIn("paths", fm)
        self.assertIn("Always-on rule body", body)

    def test_claude_scoped_rule_uses_paths_not_globs(self) -> None:
        path = self.dist_dir / "claude/rules/rule-scoped.md"
        fm, _ = split_frontmatter(read_text(path))
        self.assertEqual(fm.get("paths"), ["**/*.ts", "**/*.tsx"])
        self.assertNotIn("globs", fm)
        self.assertNotIn("alwaysApply", fm)


class TestFixtureSkillSemantics(FixtureBuildTestCase):
    def test_cursor_skill_plain_has_no_paths(self) -> None:
        path = self.dist_dir / "cursor/skills/skill-plain/SKILL.md"
        fm, _ = split_frontmatter(read_text(path))
        self.assertNotIn("paths", fm)
        self.assertNotIn("triggers", fm)

    def test_cursor_skill_scoped_has_paths_block(self) -> None:
        path = self.dist_dir / "cursor/skills/skill-scoped/SKILL.md"
        fm, _ = split_frontmatter(read_text(path))
        self.assertEqual(fm["paths"], ["**/*.ts", "src/lib/**"])

    def test_claude_skill_triggers_scalar_format(self) -> None:
        path = self.dist_dir / "claude/skills/skill-plain/SKILL.md"
        fm, _ = split_frontmatter(read_text(path))
        self.assertIn("triggers", fm)
        self.assertRegex(str(fm["triggers"]), r'^"[^"]+"(,\s*"[^"]+")*$')

    def test_skill_output_statement_with_sections(self) -> None:
        path = self.dist_dir / "cursor/skills/skill-output/SKILL.md"
        text = read_text(path)
        self.assertIn("Output: Read `schemas/SAMPLE.md`", text)
        self.assertIn("`Alpha`, `Beta`", text)
        self.assertTrue(text.rstrip().endswith(")."))


class TestFixtureCommandSemantics(FixtureBuildTestCase):
    def test_skillset_expands_to_members_not_bundle_id(self) -> None:
        path = self.dist_dir / "cursor/commands/cmd-skills-skillset.md"
        mentions = extract_skills_mentions(read_text(path))
        self.assertEqual(mentions, ["skill-plain", "skill-scoped"])
        self.assertNotIn("bundle-a", mentions)

    def test_direct_skills_listed_in_skills_line(self) -> None:
        path = self.dist_dir / "cursor/commands/cmd-skills-direct.md"
        self.assertEqual(extract_skills_mentions(read_text(path)), ["skill-plain", "skill-scoped"])

    def test_claude_model_and_triggers_on_rich_command(self) -> None:
        path = self.dist_dir / "claude/commands/cmd-next-rich.md"
        fm, _ = split_frontmatter(read_text(path))
        self.assertEqual(fm.get("model"), "sonnet")
        self.assertIn("triggers", fm)

    def test_output_line_precedes_next_handoff(self) -> None:
        path = self.dist_dir / "cursor/commands/cmd-next-rich.md"
        text = read_text(path)
        out_idx = text.index("Output:")
        next_idx = text.index("### Next recommended step")
        self.assertLess(out_idx, next_idx)

    def test_next_handoff_covers_review_default_branches_also_manual(self) -> None:
        path = self.dist_dir / "cursor/commands/cmd-next-rich.md"
        text = read_text(path)
        self.assertIn("**Review** `NNN-OUT.md` (Alpha section)", text)
        self.assertIn("**Run** `/cmd-minimal`", text)
        self.assertIn("_Alternatively:_", text)
        self.assertIn("_Also:_ if optional follow-up needed", text)
        self.assertIn("_Layer manually if scope requires:_", text)
        self.assertIn("@skill-output`", text)

    def test_branch_only_next_with_skills_suffix(self) -> None:
        path = self.dist_dir / "cursor/commands/cmd-next-branches.md"
        text = read_text(path)
        self.assertIn("Inspect project state and pick **one**:", text)
        self.assertIn("with @skill-scoped, or @skill-plain", text)
        self.assertIn("NOT auto-attached", text)
        self.assertNotIn("**Run** `/cmd-next-branches`", text.split("### Next recommended step")[0])


class TestFixtureFilteredBuild(unittest.TestCase):
    def test_filter_keeps_only_matching_artifacts(self) -> None:
        from helpers import build_fixture_dist

        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            build_fixture_dist(dist_dir=dist, targets=("cursor",), filters=["skill-plain"])
            self.assertTrue((dist / "cursor/skills/skill-plain/SKILL.md").exists())
            self.assertFalse((dist / "cursor/commands/cmd-minimal.md").exists())
            manifest = (dist / "cursor/manifest.json").read_text(encoding="utf-8")
            self.assertIn("skill-plain", manifest)
            self.assertNotIn("cmd-minimal", manifest)


if __name__ == "__main__":
    unittest.main()
