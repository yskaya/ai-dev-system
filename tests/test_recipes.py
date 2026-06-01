import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "recipes"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestRecipes(unittest.TestCase):
    def test_commands_have_targets(self) -> None:
        for path in sorted((RECIPES / "commands").glob("*.yaml")):
            data = yaml.safe_load(_read_text(path)) or {}
            self.assertIn(
                "targets",
                data,
                f"{path.name}: every command must declare targets (cursor and/or claude)",
            )

    def test_command_sources_exist(self) -> None:
        for path in sorted((RECIPES / "commands").glob("*.yaml")):
            data = yaml.safe_load(_read_text(path)) or {}
            source = data.get("source")
            if not source:
                continue
            schema_path = RECIPES / source
            self.assertTrue(schema_path.is_file(), f"{path.name}: missing {source}")

    def test_skill_sources_exist(self) -> None:
        for path in sorted((RECIPES / "skills").glob("*.yaml")):
            data = yaml.safe_load(_read_text(path)) or {}
            source = data.get("source")
            if not source:
                continue
            schema_path = RECIPES / source
            self.assertTrue(schema_path.is_file(), f"{path.name}: missing {source}")

    def test_outputs_index_matches_schemas(self) -> None:
        outputs = yaml.safe_load(_read_text(RECIPES / "outputs.yaml")) or {}
        for _key, meta in outputs.items():
            meta = meta or {}
            rel = meta.get("path", "")
            self.assertTrue(rel.startswith("schemas/"), f"outputs entry should use schemas/: {meta}")
            self.assertTrue((RECIPES / rel).is_file(), f"outputs.yaml points to missing file: {rel}")

    def test_rule_bodies_exist(self) -> None:
        rules_index = yaml.safe_load(_read_text(RECIPES / "rules" / "rules.yaml")) or {}
        for rule_key, rule in rules_index.items():
            rule = rule or {}
            body_rel = rule.get("body")
            self.assertTrue(body_rel, f"{rule_key}: missing body path")
            self.assertTrue((RECIPES / body_rel).is_file(), f"{rule_key}: missing {body_rel}")

    def test_mixed_skillsets_not_in_command_skills(self) -> None:
        skillsets = yaml.safe_load(_read_text(RECIPES / "skillsets.yaml")) or {}
        mixed = set()
        for sid, bundle in skillsets.items():
            members = (bundle or {}).get("skills") or []
            if any(isinstance(m, str) and not m.startswith("stack-") for m in members):
                mixed.add(sid)

        for path in sorted((RECIPES / "commands").glob("*.yaml")):
            data = yaml.safe_load(_read_text(path)) or {}
            skills = data.get("skills") or []
            if not isinstance(skills, list):
                continue
            for s in skills:
                self.assertNotIn(
                    s,
                    mixed,
                    f"{path.name}: mixed skillset {s!r} must be layered with @, not listed in skills:",
                )

    def test_command_name_matches_filename(self) -> None:
        for path in sorted((RECIPES / "commands").glob("*.yaml")):
            data = yaml.safe_load(_read_text(path)) or {}
            name = (data.get("name") or path.stem).strip()
            self.assertEqual(name, path.stem, f"{path.name}: name must match filename stem")

    def test_skill_name_matches_filename(self) -> None:
        for path in sorted((RECIPES / "skills").glob("*.yaml")):
            data = yaml.safe_load(_read_text(path)) or {}
            name = (data.get("name") or path.stem).strip()
            self.assertEqual(name, path.stem, f"{path.name}: name must match filename stem")

    def test_claude_models_use_canonical_ids(self) -> None:
        allowed = {"opus", "sonnet"}
        for path in sorted((RECIPES / "commands").glob("*.yaml")):
            data = yaml.safe_load(_read_text(path)) or {}
            claude = (data.get("targets") or {}).get("claude") or {}
            model = claude.get("model")
            if model:
                self.assertIn(model, allowed, f"{path.name}: use model opus or sonnet, got {model!r}")
            self.assertNotIn("routing", claude, f"{path.name}: use model instead of routing")

    def test_workflows_cover_all_commands(self) -> None:
        workflows = yaml.safe_load(_read_text(RECIPES / "workflows.yaml")) or {}
        wf_commands = workflows.get("commands") or {}
        command_ids = {p.stem for p in (RECIPES / "commands").glob("*.yaml")}
        for cmd_id in sorted(command_ids):
            self.assertIn(cmd_id, wf_commands, f"workflows.yaml: missing entry for {cmd_id!r}")

    def test_workflow_branch_commands_exist(self) -> None:
        workflows = yaml.safe_load(_read_text(RECIPES / "workflows.yaml")) or {}
        wf_commands = workflows.get("commands") or {}
        command_ids = {p.stem for p in (RECIPES / "commands").glob("*.yaml")}
        skill_ids = {p.stem for p in (RECIPES / "skills").glob("*.yaml")}
        skillsets = yaml.safe_load(_read_text(RECIPES / "skillsets.yaml")) or {}
        valid_skill_refs = skill_ids | set(skillsets.keys())

        for cmd_id, entry in wf_commands.items():
            entry = entry or {}
            for key in ("branches", "also"):
                for branch in entry.get(key) or []:
                    branch = branch or {}
                    ref = branch.get("command")
                    if ref:
                        self.assertIn(ref, command_ids, f"{cmd_id}.{key}: unknown command {ref!r}")
            default = entry.get("default") or {}
            ref = default.get("command")
            if ref:
                self.assertIn(ref, command_ids, f"{cmd_id}.default: unknown command {ref!r}")
            manual = entry.get("manual_skills") or {}
            for skill_ref in manual:
                self.assertIn(
                    skill_ref,
                    valid_skill_refs,
                    f"{cmd_id}.manual_skills: unknown skill/skillset {skill_ref!r}",
                )

    def test_workflow_manual_skills_not_in_command_skills(self) -> None:
        workflows = yaml.safe_load(_read_text(RECIPES / "workflows.yaml")) or {}
        wf_commands = workflows.get("commands") or {}
        skillsets = yaml.safe_load(_read_text(RECIPES / "skillsets.yaml")) or {}

        for path in sorted((RECIPES / "commands").glob("*.yaml")):
            cmd_id = path.stem
            cmd = yaml.safe_load(_read_text(path)) or {}
            wf = wf_commands.get(cmd_id) or {}
            manual = wf.get("manual_skills") or {}
            if not manual:
                continue
            raw_skills = cmd.get("skills") or []
            expanded: set[str] = set()
            for item in raw_skills:
                if item in skillsets:
                    for m in (skillsets[item] or {}).get("skills") or []:
                        if isinstance(m, str):
                            expanded.add(m)
                elif isinstance(item, str):
                    expanded.add(item)
            for skill_ref in manual:
                self.assertNotIn(
                    skill_ref,
                    raw_skills,
                    f"{cmd_id}: manual_skill {skill_ref!r} must not duplicate command skills: list",
                )
                self.assertNotIn(
                    skill_ref,
                    expanded,
                    f"{cmd_id}: manual_skill {skill_ref!r} must not duplicate expanded command skills",
                )


if __name__ == "__main__":
    unittest.main()
