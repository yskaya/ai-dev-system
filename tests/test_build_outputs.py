"""
Production dist/ smoke tests — validates real recipes/ build, not fixtures.

Golden-file coverage for templates and build logic lives in test_fixture_outputs.py.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

import yaml

from helpers import read_text, split_frontmatter


ROOT = Path(__file__).resolve().parents[1]


def _command_has_handoff_after_output(md: str) -> bool:
    text = md.rstrip()
    if "Output: " not in text:
        return "### Next recommended step" in text
    before, after = text.rsplit("Output: ", 1)
    output_line = "Output: " + after.split("\n", 1)[0]
    rest = after.split("\n", 1)[1] if "\n" in after else ""
    return output_line.startswith("Output: ") and "### Next recommended step" in rest


class TestProductionBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            ["python3", "scripts/build.py", "all"],
            cwd=str(ROOT),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_all_commands_include_handoff_block(self) -> None:
        for path in sorted((ROOT / "dist/cursor/commands").glob("*.md")):
            cmd = read_text(path)
            self.assertIn("When done", cmd, f"{path.name}: missing handoff preamble")
            self.assertIn("### Next recommended step", cmd, f"{path.name}: missing handoff heading")

    def test_build_step_handoff_includes_branch_and_manual_skills(self) -> None:
        cmd = read_text(ROOT / "dist/cursor/commands/build-step.md")
        self.assertIn("unchecked tasks remain", cmd.lower())
        self.assertIn("all plan or refactor tasks checked", cmd.lower())
        self.assertIn("NOT auto-attached", cmd)

    def test_create_brief_handoff_expands_next_command_skills(self) -> None:
        cmd = read_text(ROOT / "dist/cursor/commands/create-brief.md")
        self.assertIn("auto-attached", cmd)
        self.assertIn("@architecture-docs", cmd)
        self.assertIn("@ai-architecture", cmd)

    def test_review_security_output_targets_section(self) -> None:
        cmd = read_text(ROOT / "dist/cursor/commands/review-security.md")
        self.assertIn("schemas/REVIEW.md", cmd)
        self.assertTrue(_command_has_handoff_after_output(cmd))
        self.assertIn("`Security`", cmd.split("Output:")[-1])

    def test_schemas_are_copied_to_both_targets(self) -> None:
        schemas = list((ROOT / "recipes/schemas").glob("*.md"))
        self.assertGreater(len(schemas), 0)
        for s in schemas:
            self.assertTrue((ROOT / "dist/cursor/schemas" / s.name).exists(), s.name)
            self.assertTrue((ROOT / "dist/claude/schemas" / s.name).exists(), s.name)

    def test_manifest_is_written_per_target(self) -> None:
        for target in ("cursor", "claude"):
            manifest_path = ROOT / "dist" / target / "manifest.json"
            data = json.loads(read_text(manifest_path))
            self.assertEqual(data.get("target"), target)
            self.assertGreater(len(data.get("files") or []), 0)

    def test_filtered_build_prunes_stale_files(self) -> None:
        subprocess.run(
            ["python3", "scripts/build.py", "cursor", "auth"],
            cwd=str(ROOT),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        manifest = json.loads(read_text(ROOT / "dist/cursor/manifest.json"))
        files = set(manifest["files"])
        self.assertIn("skills/auth/SKILL.md", files)
        self.assertNotIn("commands/build-step.md", files)
        self.assertFalse((ROOT / "dist/cursor/commands/build-step.md").exists())
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
            fm, _ = split_frontmatter(read_text(path))
            model = fm.get("model")
            if model:
                self.assertIn(model, ("opus", "sonnet"), f"{path.name}: unexpected model {model!r}")

    def test_skill_outputs_use_name_dir_skill_md_layout(self) -> None:
        for y in sorted((ROOT / "recipes/skills").glob("*.yaml")):
            data = yaml.safe_load(read_text(y)) or {}
            skill_id = (data.get("name") or y.stem).strip()
            self.assertTrue((ROOT / "dist/cursor/skills" / skill_id / "SKILL.md").exists())
            self.assertTrue((ROOT / "dist/claude/skills" / skill_id / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
