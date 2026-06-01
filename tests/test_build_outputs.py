import json
import subprocess
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _split_frontmatter(md: str) -> tuple[dict, str]:
    """
    Return (frontmatter_dict, body_text).
    Assumes a YAML frontmatter block delimited by --- on its own line.
    """
    if not md.startswith("---\n"):
        return {}, md
    # Split on first two '---' lines
    parts = md.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, md
    fm_raw = parts[0][4:]  # after leading '---\n'
    rest = parts[1]
    fm = yaml.safe_load(fm_raw) or {}
    if isinstance(fm, list) or isinstance(fm, str):
        # Defensive: frontmatter should be a mapping; treat others as empty.
        fm = {}
    return fm, rest.lstrip("\n")


def _extract_skills_mentions(md: str) -> list[str]:
    # Commands: "Skills: @a @b ..."
    _, body = _split_frontmatter(md)
    for line in body.splitlines():
        if line.startswith("Skills: "):
            return [tok[1:] for tok in line[len("Skills: ") :].split() if tok.startswith("@")]
    return []


def _ends_with_output_line(md: str) -> bool:
    lines = [ln.rstrip("\n") for ln in md.rstrip().splitlines()]
    return bool(lines) and lines[-1].startswith("Output: ")


class TestBuildOutputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Rebuild dist/ so assertions match current recipes.
        subprocess.run(
            ["python3", "scripts/build.py", "all"],
            cwd=str(ROOT),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_cursor_rules_reflect_globs_and_always_apply(self) -> None:
        rules_index = yaml.safe_load(_read_text(ROOT / "recipes/rules/rules.yaml")) or {}
        for rule_key, rule in rules_index.items():
            rule = rule or {}
            cursor_t = (rule.get("targets") or {}).get("cursor") or {}
            always_apply_src = bool(cursor_t.get("alwaysApply", False))
            globs_src = cursor_t.get("globs")
            globs_src_list = [p.strip() for p in (globs_src or "").split(",") if p.strip()]

            out_path = ROOT / f"dist/cursor/rules/{rule_key}.mdc"
            self.assertTrue(out_path.exists(), f"missing cursor rule output: {out_path}")
            fm, body = _split_frontmatter(_read_text(out_path))

            self.assertIn("alwaysApply", fm, f"cursor rule missing alwaysApply: {rule_key}")
            self.assertEqual(bool(fm["alwaysApply"]), always_apply_src, f"alwaysApply mismatch: {rule_key}")

            if always_apply_src:
                self.assertNotIn("globs", fm, f"alwaysApply=true should omit globs: {rule_key}")
            else:
                self.assertIn("globs", fm, f"scoped rule should include globs: {rule_key}")
                self.assertEqual(list(fm["globs"]), globs_src_list, f"globs mismatch: {rule_key}")

            body_src = _read_text(ROOT / "recipes" / str(rule.get("body"))).rstrip()
            self.assertEqual(body.rstrip(), body_src, f"rule body mismatch: {rule_key}")

    def test_claude_rules_use_paths_and_no_cursor_fields(self) -> None:
        rules_index = yaml.safe_load(_read_text(ROOT / "recipes/rules/rules.yaml")) or {}
        for rule_key, rule in rules_index.items():
            rule = rule or {}
            cursor_t = (rule.get("targets") or {}).get("cursor") or {}
            always_apply_src = bool(cursor_t.get("alwaysApply", False))
            globs_src = cursor_t.get("globs")
            globs_src_list = [p.strip() for p in (globs_src or "").split(",") if p.strip()]

            out_path = ROOT / f"dist/claude/rules/{rule_key}.md"
            self.assertTrue(out_path.exists(), f"missing claude rule output: {out_path}")
            fm, body = _split_frontmatter(_read_text(out_path))

            self.assertNotIn("alwaysApply", fm, f"claude rule must not contain alwaysApply: {rule_key}")
            self.assertNotIn("globs", fm, f"claude rule must not contain globs: {rule_key}")

            if always_apply_src:
                self.assertTrue(fm in ({}, None) or "paths" not in fm, f"always-on claude rule should omit paths: {rule_key}")
            else:
                self.assertIn("paths", fm, f"scoped claude rule should include paths: {rule_key}")
                self.assertEqual(list(fm["paths"]), globs_src_list, f"claude paths mismatch: {rule_key}")

            body_src = _read_text(ROOT / "recipes" / str(rule.get("body"))).rstrip()
            self.assertEqual(body.rstrip(), body_src, f"claude rule body mismatch: {rule_key}")

    def test_skillsets_are_expanded_in_command_outputs(self) -> None:
        # design-web includes set-web + set-api; output should contain stack-* members, not set-* ids
        cursor_cmd = _read_text(ROOT / "dist/cursor/commands/design-web.md")
        mentions = _extract_skills_mentions(cursor_cmd)
        self.assertIn("stack-react", mentions)
        self.assertIn("stack-nextjs", mentions)
        self.assertIn("stack-node", mentions)
        self.assertIn("stack-nestjs", mentions)
        self.assertNotIn("set-web", mentions)
        self.assertNotIn("set-api", mentions)

    def test_triggers_format_in_claude_outputs(self) -> None:
        # Claude command triggers and Claude skill triggers should be single-quoted
        # string of comma-separated quoted triggers, e.g. triggers: '"a", "b"'
        cmd = _read_text(ROOT / "dist/claude/commands/design-web.md")
        fm, _ = _split_frontmatter(cmd)
        self.assertIn("triggers", fm)
        self.assertRegex(str(fm["triggers"]), r'^"[^"]+"(,\s*"[^"]+")*$')

        skill = _read_text(ROOT / "dist/claude/skills/ai-architecture/SKILL.md")
        fm2, _ = _split_frontmatter(skill)
        self.assertIn("triggers", fm2)
        self.assertRegex(str(fm2["triggers"]), r'^"[^"]+"(,\s*"[^"]+")*$')

    def test_output_statement_is_last_when_defined(self) -> None:
        # Commands with output/source should end with Output line.
        cmd = _read_text(ROOT / "dist/cursor/commands/design-web.md")
        self.assertTrue(_ends_with_output_line(cmd))

        # Skills with source/output/sections should end with Output line.
        skill = _read_text(ROOT / "dist/cursor/skills/ai-architecture/SKILL.md")
        self.assertTrue(_ends_with_output_line(skill))

    def test_schemas_are_copied(self) -> None:
        schemas = list((ROOT / "recipes/schemas").glob("*.md"))
        self.assertGreater(len(schemas), 0)
        for s in schemas:
            self.assertTrue((ROOT / "dist/cursor/schemas" / s.name).exists(), f"missing cursor schema: {s.name}")
            self.assertTrue((ROOT / "dist/claude/schemas" / s.name).exists(), f"missing claude schema: {s.name}")

    def test_review_security_updates_security_section(self) -> None:
        cmd = _read_text(ROOT / "dist/cursor/commands/review-security.md")
        self.assertIn("schemas/REVIEW.md", cmd)
        self.assertTrue(_ends_with_output_line(cmd))
        self.assertIn("`Security`", cmd.split("Output:")[-1])

    def test_manifest_is_written(self) -> None:
        for target in ("cursor", "claude"):
            manifest_path = ROOT / "dist" / target / "manifest.json"
            self.assertTrue(manifest_path.exists(), f"missing {manifest_path}")
            data = json.loads(_read_text(manifest_path))
            self.assertEqual(data.get("target"), target)
            self.assertIn("files", data)
            self.assertGreater(len(data["files"]), 0)

    def test_filtered_build_prunes_stale_files(self) -> None:
        subprocess.run(
            ["python3", "scripts/build.py", "cursor", "auth"],
            cwd=str(ROOT),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        manifest = json.loads(_read_text(ROOT / "dist/cursor/manifest.json"))
        files = set(manifest["files"])
        self.assertIn("skills/auth/SKILL.md", files)
        self.assertNotIn("commands/build-step.md", files)
        self.assertFalse((ROOT / "dist/cursor/commands/build-step.md").exists())
        # Restore full dist for other tests / install
        subprocess.run(
            ["python3", "scripts/build.py", "all"],
            cwd=str(ROOT),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_claude_commands_use_canonical_model_ids(self) -> None:
        for path in sorted((ROOT / "dist/claude/commands").glob("*.md")):
            fm, _ = _split_frontmatter(_read_text(path))
            model = fm.get("model")
            if model:
                self.assertIn(model, ("opus", "sonnet"), f"{path.name}: unexpected model {model!r}")

    def test_skill_structure_is_name_dir_skill_md(self) -> None:
        # Ensure skills are emitted as dist/<target>/skills/<name>/SKILL.md
        skills = list((ROOT / "recipes/skills").glob("*.yaml"))
        self.assertGreater(len(skills), 0)
        for y in skills:
            data = yaml.safe_load(_read_text(y)) or {}
            skill_id = (data.get("name") or y.stem).strip()
            self.assertTrue((ROOT / "dist/cursor/skills" / skill_id / "SKILL.md").exists(), f"missing cursor skill file for {skill_id}")
            self.assertTrue((ROOT / "dist/claude/skills" / skill_id / "SKILL.md").exists(), f"missing claude skill file for {skill_id}")


if __name__ == "__main__":
    unittest.main()

