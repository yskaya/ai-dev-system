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


def _command_has_handoff_after_artifact(md: str) -> bool:
    text = md.rstrip()
    if "**Artifact (required)**" not in text:
        return "### Next Step" in text
    artifact_idx = text.index("**Artifact (required)**")
    next_idx = text.index("### Next Step")
    return artifact_idx < next_idx


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
            self.assertIn("### Next Step", cmd, f"{path.name}: missing handoff heading")

    def test_build_step_handoff_includes_next(self) -> None:
        cmd = read_text(ROOT / "dist/cursor/commands/build-step.md")
        self.assertIn("Run `/build-step`", cmd)

    def test_custom_artifact_dir(self) -> None:
        subprocess.run(
            ["python3", "scripts/build.py", "cursor", "create-brief", "--artifact-dir", "docs/custom"],
            cwd=str(ROOT),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        cmd = read_text(ROOT / "dist/cursor/commands/create-brief.md")
        self.assertIn("Write `docs/custom/NNN-BRIEF.md`", cmd)
        self.assertIn("Create `docs/custom/` if missing", cmd)
        self.assertIn("Review `docs/custom/NNN-BRIEF.md` and run `/design`", cmd)
        subprocess.run(
            ["python3", "scripts/build.py", "all"],
            cwd=str(ROOT),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_create_brief_handoff_is_compact(self) -> None:
        cmd = read_text(ROOT / "dist/cursor/commands/create-brief.md")
        self.assertIn("Review `docs/ai/NNN-BRIEF.md` and run `/design`", cmd)
        self.assertNotIn("Alternatively:", cmd)

    def test_commands_with_artifact_write_docs_ai(self) -> None:
        cmd = read_text(ROOT / "dist/cursor/commands/create-brief.md")
        self.assertIn("**Artifact (required)**", cmd)
        self.assertIn("not chat-only", cmd)
        self.assertTrue(_command_has_handoff_after_artifact(cmd))

    def test_review_security_output_targets_section(self) -> None:
        cmd = read_text(ROOT / "dist/cursor/commands/review-security.md")
        self.assertIn("schemas/REVIEW.md", cmd)
        self.assertTrue(_command_has_handoff_after_artifact(cmd))
        self.assertIn("`Security`", cmd)
        self.assertIn("docs/ai/NNN-REVIEW.md", cmd)

    def test_operating_principles_include_layer_stack(self) -> None:
        rules = read_text(ROOT / "dist/cursor/rules/00-operating-principles.mdc")
        self.assertIn("Layer stack", rules)
        self.assertIn("@set-web", rules)

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
