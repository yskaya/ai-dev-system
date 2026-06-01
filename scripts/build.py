#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


ROOT = Path(__file__).resolve().parents[1]
RECIPES_DIR = ROOT / "recipes"
DIST_DIR = ROOT / "dist"
TEMPLATES_DIR = ROOT / "templates"


@dataclass(frozen=True)
class BuildPaths:
    recipes_dir: Path
    dist_dir: Path
    templates_dir: Path = TEMPLATES_DIR


DEFAULT_PATHS = BuildPaths(recipes_dir=RECIPES_DIR, dist_dir=DIST_DIR)

# Canonical Claude command model ids emitted in frontmatter.
_VALID_MODELS = frozenset({"opus", "sonnet"})


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_yaml(path: Path) -> Any:
    return yaml.safe_load(_read_text(path))


def _single_quote_yaml(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def _csv_globs(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _yaml_list_block(key: str, items: list[str], indent: int = 0) -> str:
    if not items:
        return ""
    pad = " " * indent
    lines = [f"{pad}{key}:"]
    for it in items:
        lines.append(f'{pad}  - "{it}"')
    return "\n".join(lines)


def _triggers_scalar(triggers: Optional[list[str]]) -> str:
    if not triggers:
        return ""
    inner = ", ".join([f'"{t}"' for t in triggers])
    return f"triggers: {_single_quote_yaml(inner)}"


def _normalize_claude_model(raw: Any) -> Optional[str]:
    """Map recipe model/routing values to canonical opus | sonnet."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    val = raw.strip().lower()
    if val in _VALID_MODELS:
        return val
    if "sonnet" in val:
        return "sonnet"
    if "opus" in val:
        return "opus"
    return None


def _claude_model_from_targets(cmd: dict[str, Any]) -> Optional[str]:
    t = (cmd.get("targets") or {}).get("claude") or {}
    model = _normalize_claude_model(t.get("model"))
    if model:
        return model
    return _normalize_claude_model(t.get("routing"))


def _schema_ref(path: str) -> str:
    return path.strip()


def _output_statement(*, schema: Optional[str], output: Optional[str], sections: Optional[list[str]]) -> str:
    parts: list[str] = []
    if schema:
        parts.append(f"Read `{_schema_ref(schema)}` for context.")
    if output and sections:
        secs = ", ".join([f"`{s}`" for s in sections])
        parts.append(f"Update sections {secs} in `{output}` (create the file if missing).")
    elif output:
        parts.append(f"Create or update `{output}`.")
    if not parts:
        return ""
    return "Output: " + " ".join(parts)


def _parse_sections(raw: Any) -> Optional[list[str]]:
    if not isinstance(raw, list):
        return None
    return [str(s).split("#", 1)[0].rstrip() for s in raw if str(s).strip()]


def _load_template(target: str, kind: str, *, templates_dir: Path = TEMPLATES_DIR) -> str:
    path = templates_dir / target / f"{kind}.tmpl"
    if not path.is_file():
        raise SystemExit(f"missing template: {path}")
    return _read_text(path)


def _apply_template(tmpl: str, values: dict[str, str]) -> str:
    out = tmpl
    for key, val in values.items():
        out = out.replace("{" + key + "}", val)
    lines: list[str] = []
    for line in out.splitlines():
        if re.fullmatch(r"\{[a-z_]+\}", line.strip()):
            continue
        lines.append(line)
    result = "\n".join(lines)
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    return result.rstrip()


def _write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            return False
    path.write_text(content, encoding="utf-8")
    return True


def _prune_stale(out_root: Path, keep: set[str]) -> int:
    removed = 0
    for path in sorted(out_root.rglob("*"), reverse=True):
        if not path.is_file() or path.name == "manifest.json":
            continue
        rel = path.relative_to(out_root).as_posix()
        if rel not in keep:
            path.unlink()
            removed += 1
    for path in sorted(out_root.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    return removed


@dataclass(frozen=True)
class BuildSelection:
    targets: set[str]
    filters: list[str]


def _schema_token(schema_path: str) -> str:
    base = Path(schema_path).name
    return base.rsplit(".", 1)[0].lower()


def _collect_recipes(paths: BuildPaths) -> dict[str, Any]:
    recipes_dir = paths.recipes_dir
    skills: dict[str, dict[str, Any]] = {}
    commands: dict[str, dict[str, Any]] = {}

    for p in sorted((recipes_dir / "skills").glob("*.yaml")):
        data = _read_yaml(p) or {}
        skill_id = (data.get("name") or p.stem).strip()
        skills[skill_id] = data

    for p in sorted((recipes_dir / "commands").glob("*.yaml")):
        data = _read_yaml(p) or {}
        cmd_id = (data.get("name") or p.stem).strip()
        commands[cmd_id] = data

    skillsets = _read_yaml(recipes_dir / "skillsets.yaml") or {}
    outputs = _read_yaml(recipes_dir / "outputs.yaml") or {}
    rules_index = _read_yaml(recipes_dir / "rules" / "rules.yaml") or {}
    workflows = _read_yaml(recipes_dir / "workflows.yaml") or {}

    return {
        "skills": skills,
        "commands": commands,
        "skillsets": skillsets,
        "outputs": outputs,
        "rules_index": rules_index,
        "workflows": workflows,
    }


def _expand_command_skills(raw: Any, skillsets: dict[str, Any]) -> list[str]:
    if not raw:
        return []
    if not isinstance(raw, list):
        raise SystemExit("commands.*.skills must be a YAML list")
    expanded: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        if item in skillsets:
            members = (skillsets.get(item) or {}).get("skills") or []
            for m in members:
                if isinstance(m, str):
                    expanded.append(m)
        else:
            expanded.append(item)
    out: list[str] = []
    seen: set[str] = set()
    for s in expanded:
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out


def _filters_match_id(filters: list[str], item_id: str) -> bool:
    if not filters:
        return True
    return item_id in filters


def _filters_match_schema_related(filters: list[str], *, schema_path: Optional[str]) -> bool:
    if not filters or not schema_path:
        return False
    return _schema_token(schema_path) in filters


def _skills_block(skills: list[str]) -> str:
    if not skills:
        return ""
    return "Skills: " + " ".join([f"@{s}" for s in skills])


def _format_skill_list(skills: list[str]) -> str:
    if not skills:
        return ""
    return ", ".join([f"`@{s}`" for s in skills])


def _attached_skills_for_command(cmd: dict[str, Any], skillsets: dict[str, Any]) -> list[str]:
    return _expand_command_skills(cmd.get("skills"), skillsets)


def _format_branch_skills(raw: Any) -> str:
    if not isinstance(raw, list) or not raw:
        return ""
    tokens = [s if s.startswith("@") else f"@{s}" for s in raw if isinstance(s, str)]
    if len(tokens) == 1:
        return tokens[0]
    inner = ", ".join(tokens[:-1])
    return f"{inner}, or {tokens[-1]}"


def _emit_skill_notes(
    lines: list[str],
    *,
    next_cmd_id: Optional[str],
    workflows: dict[str, Any],
    commands: dict[str, Any],
    skillsets: dict[str, Any],
) -> None:
    if not next_cmd_id:
        return
    next_wf = (workflows.get("commands") or {}).get(next_cmd_id) or {}
    next_cmd_def = commands.get(next_cmd_id) or {}
    attached = _attached_skills_for_command(next_cmd_def, skillsets)
    if attached:
        lines.append(
            f"_Skills for `/{next_cmd_id}` (auto-attached):_ {_format_skill_list(attached)}"
        )
    manual = next_wf.get("manual_skills") or {}
    if manual:
        parts = [f"`@{k}` ({v})" for k, v in manual.items()]
        lines.append(f"_Layer manually if scope requires:_ {', '.join(parts)}")


def _next_step_block(
    *,
    cmd_id: str,
    wf_entry: dict[str, Any],
    skillsets: dict[str, Any],
    commands: dict[str, Any],
    workflows: dict[str, Any],
) -> str:
    lines: list[str] = [
        "**When done — print this as your final message:**",
        "",
        "### Next recommended step",
    ]

    review = wf_entry.get("review") or {}
    default = wf_entry.get("default") or {}
    branches = wf_entry.get("branches") or []
    also = wf_entry.get("also") or []
    manual_skills = wf_entry.get("manual_skills") or {}

    step_num = 1

    if isinstance(review, dict) and review.get("doc"):
        doc = review["doc"]
        prompt = review.get("prompt", "")
        section = review.get("section")
        if section:
            lines.append(f"{step_num}. **Review** `{doc}` ({section} section) — {prompt}.")
        else:
            lines.append(f"{step_num}. **Review** `{doc}` — {prompt}.")
        step_num += 1

    if default.get("command"):
        next_cmd = default["command"]
        why = default.get("why", "")
        why_suffix = f" to {why}" if why else ""
        skills_raw = default.get("skills")
        note = default.get("note")
        if skills_raw:
            formatted = _format_branch_skills(skills_raw)
            lines.append(f"{step_num}. **Run** `/{next_cmd}` {formatted}{why_suffix}.")
        else:
            lines.append(f"{step_num}. **Run** `/{next_cmd}`{why_suffix}.")
        if note:
            lines.append(f"   _{note}_")
        step_num += 1
    elif default.get("note"):
        lines.append(f"{step_num}. {default['note'].rstrip('.')}.")
        step_num += 1

    if branches:
        if step_num > 1:
            lines.append("")
        if default.get("command"):
            lines.append("_Alternatively:_")
        elif len(branches) > 1:
            lines.append("Inspect project state and pick **one**:")
        else:
            lines.append("Inspect project state:")
        for branch in branches:
            if not isinstance(branch, dict):
                continue
            when = branch.get("when", "")
            cmd = branch.get("command")
            note = branch.get("note")
            skills_raw = branch.get("skills")
            if cmd:
                skill_suffix = ""
                if skills_raw:
                    formatted = _format_branch_skills(skills_raw)
                    skill_suffix = f" with {formatted}"
                    if note:
                        skill_suffix += f" ({note.rstrip('.')})"
                elif note:
                    skill_suffix = f" — {note.rstrip('.')}"
                lines.append(f"- **{when}** → `/{cmd}`{skill_suffix}")
            elif note:
                lines.append(f"- **{when}** — {note.rstrip('.')}")

    if also:
        lines.append("")
        for item in also:
            if not isinstance(item, dict):
                continue
            when = item.get("when", "")
            cmd = item.get("command")
            if cmd:
                lines.append(f"_Also:_ if {when}, run `/{cmd}`.")

    skill_note_lines: list[str] = []
    if default.get("command"):
        _emit_skill_notes(
            skill_note_lines,
            next_cmd_id=default["command"],
            workflows=workflows,
            commands=commands,
            skillsets=skillsets,
        )
    if manual_skills:
        parts = [f"`@{k}` ({v})" for k, v in manual_skills.items()]
        skill_note_lines.append(f"_Layer manually if scope requires:_ {', '.join(parts)}")
    if skill_note_lines:
        lines.append("")
        lines.extend(skill_note_lines)

    return "\n".join(lines)


def _render_command(
    *,
    target: str,
    cmd: dict[str, Any],
    cmd_id: str,
    skillsets: dict[str, Any],
    commands: dict[str, Any],
    workflows: dict[str, Any],
    templates_dir: Path = TEMPLATES_DIR,
) -> str:
    description = _single_quote_yaml(str(cmd.get("description") or cmd_id))
    skills = _expand_command_skills(cmd.get("skills"), skillsets)

    model_line = ""
    triggers_line = ""
    if target == "claude":
        triggers_line = _triggers_scalar(cmd.get("triggers"))
        model = _claude_model_from_targets(cmd)
        if model:
            model_line = f"model: {model}"

    output_stmt = _output_statement(
        schema=cmd.get("source"),
        output=cmd.get("output"),
        sections=_parse_sections(cmd.get("sections")),
    )

    wf_commands = workflows.get("commands") or {}
    wf_entry = wf_commands.get(cmd_id)
    if not wf_entry:
        raise SystemExit(f"workflows.yaml: missing entry for command {cmd_id!r}")

    next_step = _next_step_block(
        cmd_id=cmd_id,
        wf_entry=wf_entry,
        skillsets=skillsets,
        commands=commands,
        workflows=workflows,
    )

    return _apply_template(
        _load_template(target, "command", templates_dir=templates_dir),
        {
            "description": description,
            "triggers_line": triggers_line,
            "model_line": model_line,
            "skills_block": _skills_block(skills),
            "body": (cmd.get("body") or "").rstrip(),
            "output_statement": output_stmt,
            "next_step_block": next_step,
        },
    )


def _render_skill(
    *,
    target: str,
    skill: dict[str, Any],
    skill_id: str,
    templates_dir: Path = TEMPLATES_DIR,
) -> str:
    description = _single_quote_yaml(str(skill.get("description") or ""))

    triggers_line = ""
    if target == "claude":
        triggers_line = _triggers_scalar(skill.get("triggers"))

    paths_block = ""
    paths_raw = skill.get("paths")
    if isinstance(paths_raw, str):
        paths_block = _yaml_list_block("paths", _csv_globs(paths_raw))

    output_stmt = _output_statement(
        schema=skill.get("source"),
        output=skill.get("output"),
        sections=_parse_sections(skill.get("sections")),
    )

    return _apply_template(
        _load_template(target, "skill", templates_dir=templates_dir),
        {
            "name": skill_id,
            "description": description,
            "triggers_line": triggers_line,
            "paths_block": paths_block,
            "body": (skill.get("body") or "").rstrip(),
            "output_statement": output_stmt,
        },
    )


def _render_rule_cursor(
    *, rule: dict[str, Any], body: str, templates_dir: Path = TEMPLATES_DIR
) -> str:
    cursor_t = (rule.get("targets") or {}).get("cursor") or {}
    always_apply = bool(cursor_t.get("alwaysApply", False))
    globs = _csv_globs(cursor_t.get("globs"))
    globs_block = _yaml_list_block("globs", globs) if (globs and not always_apply) else ""

    return _apply_template(
        _load_template("cursor", "rule", templates_dir=templates_dir),
        {
            "description": _single_quote_yaml(str(rule.get("description") or "")),
            "globs_block": globs_block,
            "alwaysApply": "true" if always_apply else "false",
            "body": body.rstrip(),
        },
    )


def _render_rule_claude(
    *, rule: dict[str, Any], body: str, templates_dir: Path = TEMPLATES_DIR
) -> str:
    cursor_t = (rule.get("targets") or {}).get("cursor") or {}
    always_apply = bool(cursor_t.get("alwaysApply", False))
    globs = _csv_globs(cursor_t.get("globs"))

    paths_block = ""
    if (not always_apply) and globs:
        paths_block = _yaml_list_block("paths", globs)

    return _apply_template(
        _load_template("claude", "rule", templates_dir=templates_dir),
        {
            "paths_block": paths_block,
            "body": body.rstrip(),
        },
    )


@dataclass
class _BuildResult:
    wrote: int = 0
    expected: set[str] = field(default_factory=set)


def _build_target(
    target: str,
    selection: BuildSelection,
    recipes: dict[str, Any],
    paths: BuildPaths,
) -> _BuildResult:
    recipes_dir = paths.recipes_dir
    templates_dir = paths.templates_dir
    skills: dict[str, Any] = recipes["skills"]
    commands: dict[str, Any] = recipes["commands"]
    skillsets: dict[str, Any] = recipes["skillsets"]
    outputs: dict[str, Any] = recipes["outputs"]
    rules_index: dict[str, Any] = recipes["rules_index"]
    workflows: dict[str, Any] = recipes["workflows"]

    out_root = paths.dist_dir / target
    result = _BuildResult()

    for _key, meta in sorted(outputs.items()):
        meta = meta or {}
        rel_path = meta.get("path")
        if not isinstance(rel_path, str) or not rel_path.startswith("schemas/"):
            continue
        schema_token = Path(rel_path).stem.lower()
        if selection.filters and schema_token not in selection.filters:
            continue
        src = recipes_dir / rel_path
        if not src.is_file():
            continue
        rel = rel_path
        result.expected.add(rel)
        if _write_if_changed(out_root / rel, _read_text(src).rstrip()):
            result.wrote += 1

    for rule_key in sorted(rules_index.keys()):
        rule = rules_index[rule_key] or {}
        rule_name = str(rule.get("name") or rule_key).strip()
        if selection.filters and (rule_key not in selection.filters and rule_name not in selection.filters):
            continue
        body_rel = rule.get("body")
        if not body_rel:
            continue
        body = _read_text(recipes_dir / body_rel).rstrip()
        if target == "cursor":
            content = _render_rule_cursor(rule=rule, body=body, templates_dir=templates_dir)
            rel = f"rules/{rule_key}.mdc"
        else:
            content = _render_rule_claude(rule=rule, body=body, templates_dir=templates_dir)
            rel = f"rules/{rule_key}.md"
        result.expected.add(rel)
        if _write_if_changed(out_root / rel, content):
            result.wrote += 1

    for cmd_id in sorted(commands.keys()):
        cmd = commands[cmd_id] or {}
        if not (_filters_match_id(selection.filters, cmd_id) or _filters_match_schema_related(selection.filters, schema_path=cmd.get("source"))):
            continue
        content = _render_command(
            target=target,
            cmd=cmd,
            cmd_id=cmd_id,
            skillsets=skillsets,
            commands=commands,
            workflows=workflows,
            templates_dir=templates_dir,
        )
        rel = f"commands/{cmd_id}.md"
        result.expected.add(rel)
        if _write_if_changed(out_root / rel, content):
            result.wrote += 1

    for skill_id in sorted(skills.keys()):
        skill = skills[skill_id] or {}
        if not (_filters_match_id(selection.filters, skill_id) or _filters_match_schema_related(selection.filters, schema_path=skill.get("source"))):
            continue
        content = _render_skill(
            target=target,
            skill=skill,
            skill_id=skill_id,
            templates_dir=templates_dir,
        )
        rel = f"skills/{skill_id}/SKILL.md"
        result.expected.add(rel)
        if _write_if_changed(out_root / rel, content):
            result.wrote += 1

    if selection.filters:
        result.wrote += _prune_stale(out_root, result.expected)

    manifest_files = sorted(result.expected) if selection.filters else sorted(
        p.relative_to(out_root).as_posix()
        for p in out_root.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    )
    manifest = {"target": target, "files": manifest_files}
    if _write_if_changed(out_root / "manifest.json", json.dumps(manifest, indent=2) + "\n"):
        result.wrote += 1

    print(f"[build {target}] wrote {result.wrote} file(s)")
    return result


def _parse_args(argv: list[str]) -> tuple[BuildSelection, BuildPaths]:
    parser = argparse.ArgumentParser(prog="build.py", add_help=True)
    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=["all", "cursor", "claude"],
        help="Build target(s)",
    )
    parser.add_argument("filters", nargs="*", help="Optional ids to build (commands, skills, rules, schemas)")
    parser.add_argument(
        "--recipes-dir",
        type=Path,
        default=None,
        help="Recipes root (default: repo recipes/)",
    )
    parser.add_argument(
        "--dist-dir",
        type=Path,
        default=None,
        help="Output root (default: repo dist/)",
    )
    ns = parser.parse_args(argv)

    targets = {"cursor", "claude"} if ns.target == "all" else {ns.target}
    selection = BuildSelection(
        targets=targets,
        filters=[f.strip() for f in ns.filters if f.strip()],
    )
    paths = BuildPaths(
        recipes_dir=(ns.recipes_dir or RECIPES_DIR).resolve(),
        dist_dir=(ns.dist_dir or DIST_DIR).resolve(),
    )
    return selection, paths


def run_build(selection: BuildSelection, paths: BuildPaths = DEFAULT_PATHS) -> int:
    recipes = _collect_recipes(paths)
    for t in sorted(selection.targets):
        _build_target(t, selection, recipes, paths)
    return 0


def main(argv: list[str]) -> int:
    selection, paths = _parse_args(argv)
    return run_build(selection, paths)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
