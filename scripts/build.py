#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
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


def _claude_model_from_targets(cmd: dict[str, Any]) -> Optional[str]:
    t = (cmd.get("targets") or {}).get("claude") or {}
    model = t.get("model")
    if not isinstance(model, str) or not model.strip():
        return None
    val = model.strip().lower()
    return val if val in _VALID_MODELS else None


DEFAULT_ARTIFACT_DIR = "docs/ai"


@dataclass(frozen=True)
class ProjectConfig:
    artifact_dir: str = DEFAULT_ARTIFACT_DIR


def _normalize_artifact_dir(raw: Any) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return DEFAULT_ARTIFACT_DIR
    return raw.strip().strip("/")


def _load_project_config(
    recipes_dir: Path,
    *,
    override: Optional[str] = None,
) -> ProjectConfig:
    if override is not None:
        return ProjectConfig(artifact_dir=_normalize_artifact_dir(override))
    env = os.environ.get("AI_DEV_ARTIFACT_DIR")
    if env:
        return ProjectConfig(artifact_dir=_normalize_artifact_dir(env))
    project = _read_yaml(recipes_dir / "project.yaml") or {}
    return ProjectConfig(artifact_dir=_normalize_artifact_dir(project.get("artifact_dir")))


def _project_values(artifact_dir: str) -> dict[str, str]:
    return {"artifact_dir": artifact_dir}


def _apply_project(text: str, artifact_dir: str) -> str:
    return _apply_template(text, _project_values(artifact_dir))


def _artifact_path(output: str, *, artifact_dir: str) -> str:
    out = output.strip()
    if "/" in out:
        return out
    return f"{artifact_dir}/{out}"


def _artifact_template_and_values(
    *,
    schema: Optional[str],
    output: Optional[str],
    sections: Optional[list[str]],
    artifact_dir: str,
) -> tuple[Optional[str], dict[str, str]]:
    if not schema and not output:
        return None, {}
    vals: dict[str, str] = {
        "source": schema.strip() if schema else "",
        "output_path": _artifact_path(output, artifact_dir=artifact_dir) if output else "",
        "artifact_dir": artifact_dir,
        "sections": ", ".join([f"`{s}`" for s in sections]) if sections else "",
    }
    if sections and output:
        return "artifact-edit", vals
    if output:
        return "artifact-write", vals
    return "artifact-read", vals


def _render_artifact(
    *,
    schema: Optional[str],
    output: Optional[str],
    sections: Optional[list[str]],
    artifact_dir: str,
    templates_dir: Path = TEMPLATES_DIR,
) -> str:
    template_name, vals = _artifact_template_and_values(
        schema=schema, output=output, sections=sections, artifact_dir=artifact_dir
    )
    if not template_name:
        return ""
    if template_name in ("artifact-write", "artifact-edit"):
        vals["artifact_header"] = _render_partial(
            "artifact-header", {}, templates_dir=templates_dir
        )
    return _render_partial(template_name, vals, templates_dir=templates_dir)


def _parse_sections(raw: Any) -> Optional[list[str]]:
    if not isinstance(raw, list):
        return None
    return [str(s).split("#", 1)[0].rstrip() for s in raw if str(s).strip()]


def _load_template(target: str, kind: str, *, templates_dir: Path = TEMPLATES_DIR) -> str:
    path = templates_dir / target / f"{kind}.tmpl"
    if not path.is_file():
        raise SystemExit(f"missing template: {path}")
    return _read_text(path)


def _load_shared_template(name: str, *, templates_dir: Path = TEMPLATES_DIR) -> str:
    path = templates_dir / "_shared" / f"{name}.tmpl"
    if not path.is_file():
        raise SystemExit(f"missing shared template: {path}")
    return _read_text(path)


def _render_partial(name: str, values: dict[str, str], *, templates_dir: Path = TEMPLATES_DIR) -> str:
    return _apply_template(
        _load_shared_template(name, templates_dir=templates_dir),
        values,
        drop_empty_lines=True,
    )


def _apply_template(tmpl: str, values: dict[str, str], *, drop_empty_lines: bool = False) -> str:
    out = tmpl
    for key, val in values.items():
        out = out.replace("{" + key + "}", val)
    lines: list[str] = []
    for line in out.splitlines():
        if re.fullmatch(r"\{[a-z_]+\}", line.strip()):
            continue
        if drop_empty_lines and not line.strip():
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


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def _resolve_command(
    cmd_id: str,
    commands: dict[str, Any],
    *,
    chain: tuple[str, ...] = (),
) -> dict[str, Any]:
    raw = commands.get(cmd_id)
    if not raw:
        raise SystemExit(f"unknown command {cmd_id!r}")
    cmd = dict(raw)
    extends = cmd.get("extends")
    if not extends:
        cmd.setdefault("name", cmd_id)
        return cmd
    if not isinstance(extends, str) or not extends.strip():
        raise SystemExit(f"{cmd_id}: extends must be a non-empty command id")
    parent_id = extends.strip()
    if parent_id not in commands:
        raise SystemExit(f"{cmd_id}: extends unknown command {parent_id!r}")
    if parent_id in chain:
        raise SystemExit(f"{cmd_id}: circular extends chain ({' -> '.join(chain + (cmd_id,))})")
    parent = _resolve_command(parent_id, commands, chain=chain + (cmd_id,))

    merged: dict[str, Any] = {}
    for key in set(parent) | set(cmd):
        if key == "extends":
            continue
        if key not in cmd or cmd[key] is None:
            merged[key] = parent.get(key)
            continue
        if key == "skills":
            p_skills = parent.get("skills") or []
            c_skills = cmd.get("skills") or []
            if isinstance(p_skills, list) and isinstance(c_skills, list):
                merged[key] = _dedupe_preserve_order([*(str(s) for s in p_skills), *(str(s) for s in c_skills)])
            else:
                merged[key] = cmd[key]
        elif key == "triggers":
            merged[key] = cmd[key]
        elif key == "body":
            p_body = (parent.get("body") or "").rstrip()
            c_body = (cmd.get("body") or "").rstrip()
            merged[key] = f"{p_body}\n\n{c_body}".strip() if p_body and c_body else (c_body or p_body)
        else:
            merged[key] = cmd[key]
    merged["name"] = (cmd.get("name") or cmd_id).strip()
    return merged


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


def _next_step_template_and_values(
    *,
    cmd: dict[str, Any],
    wf_entry: dict[str, Any],
    artifact_dir: str,
) -> tuple[Optional[str], dict[str, str]]:
    wf_entry = wf_entry or {}
    next_raw = wf_entry.get("next")
    next_cmd = next_raw.strip() if isinstance(next_raw, str) else ""

    section_raw = wf_entry.get("review_section") or wf_entry.get("section")
    review_section = f" ({section_raw})" if section_raw else ""

    output = str(cmd.get("output") or "")
    output_path = _artifact_path(output, artifact_dir=artifact_dir) if output else ""
    show_review = bool(cmd.get("source")) and bool(output_path) and bool(next_cmd)

    if not next_cmd:
        return None, {}

    vals = {
        "output_path": output_path,
        "review_section": review_section,
        "next": next_cmd,
    }
    if show_review and next_cmd:
        return "next-step-review", vals
    if next_cmd:
        return "next-step", vals
    return None, {}


def _render_next_step(
    *,
    cmd: dict[str, Any],
    wf_entry: dict[str, Any],
    artifact_dir: str,
    templates_dir: Path = TEMPLATES_DIR,
) -> str:
    template_name, vals = _next_step_template_and_values(
        cmd=cmd, wf_entry=wf_entry, artifact_dir=artifact_dir
    )
    if not template_name:
        return ""
    return _render_partial(template_name, vals, templates_dir=templates_dir)


def _render_command(
    *,
    target: str,
    cmd: dict[str, Any],
    cmd_id: str,
    skillsets: dict[str, Any],
    commands: dict[str, Any],
    workflows: dict[str, Any],
    artifact_dir: str,
    templates_dir: Path = TEMPLATES_DIR,
) -> str:
    cmd = _resolve_command(cmd_id, commands)
    description = _single_quote_yaml(str(cmd.get("description") or cmd_id))
    skills = _expand_command_skills(cmd.get("skills"), skillsets)

    model_line = ""
    triggers_line = ""
    if target == "claude":
        triggers_line = _triggers_scalar(cmd.get("triggers"))
        model = _claude_model_from_targets(cmd)
        if model:
            model_line = f"model: {model}"

    output_stmt = _render_artifact(
        schema=cmd.get("source"),
        output=cmd.get("output"),
        sections=_parse_sections(cmd.get("sections")),
        artifact_dir=artifact_dir,
        templates_dir=templates_dir,
    )

    wf_commands = workflows.get("commands") or {}
    if cmd_id not in wf_commands:
        raise SystemExit(f"workflows.yaml: missing entry for command {cmd_id!r}")
    wf_entry = wf_commands.get(cmd_id) or {}

    next_step = _render_next_step(
        cmd=cmd, wf_entry=wf_entry, artifact_dir=artifact_dir, templates_dir=templates_dir
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
    artifact_dir: str,
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

    output_stmt = _render_artifact(
        schema=skill.get("source"),
        output=skill.get("output"),
        sections=_parse_sections(skill.get("sections")),
        artifact_dir=artifact_dir,
        templates_dir=templates_dir,
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
    *, rule: dict[str, Any], body: str, artifact_dir: str, templates_dir: Path = TEMPLATES_DIR
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
            "body": _apply_project(body, artifact_dir).rstrip(),
        },
    )


def _render_rule_claude(
    *, rule: dict[str, Any], body: str, artifact_dir: str, templates_dir: Path = TEMPLATES_DIR
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
            "body": _apply_project(body, artifact_dir).rstrip(),
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
    project: ProjectConfig,
) -> _BuildResult:
    recipes_dir = paths.recipes_dir
    templates_dir = paths.templates_dir
    skills: dict[str, Any] = recipes["skills"]
    commands: dict[str, Any] = recipes["commands"]
    skillsets: dict[str, Any] = recipes["skillsets"]
    outputs: dict[str, Any] = recipes["outputs"]
    rules_index: dict[str, Any] = recipes["rules_index"]
    workflows: dict[str, Any] = recipes["workflows"]

    artifact_dir = project.artifact_dir

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
            content = _render_rule_cursor(
                rule=rule, body=body, artifact_dir=artifact_dir, templates_dir=templates_dir
            )
            rel = f"rules/{rule_key}.mdc"
        else:
            content = _render_rule_claude(
                rule=rule, body=body, artifact_dir=artifact_dir, templates_dir=templates_dir
            )
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
            artifact_dir=artifact_dir,
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
            artifact_dir=artifact_dir,
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
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="Override recipes/project.yaml artifact_dir (env: AI_DEV_ARTIFACT_DIR)",
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
    return selection, paths, ns.artifact_dir


def run_build(
    selection: BuildSelection,
    paths: BuildPaths = DEFAULT_PATHS,
    *,
    artifact_dir: Optional[str] = None,
) -> int:
    project = _load_project_config(paths.recipes_dir, override=artifact_dir)
    recipes = _collect_recipes(paths)
    for t in sorted(selection.targets):
        _build_target(t, selection, recipes, paths, project)
    return 0


def main(argv: list[str]) -> int:
    selection, paths, artifact_dir = _parse_args(argv)
    return run_build(selection, paths, artifact_dir=artifact_dir)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
