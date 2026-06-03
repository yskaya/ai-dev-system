#!/usr/bin/env python3
"""Copy built artifacts from dist/ into a target project."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RECIPES = ROOT / "recipes"

sys.path.insert(0, str(ROOT / "scripts"))
import build as build_module  # noqa: E402

CURSOR_MAP = [
    ("rules", ".cursor/rules"),
    ("commands", ".cursor/commands"),
    ("skills", ".cursor/skills"),
    ("schemas", ".cursor/schemas"),
]

CLAUDE_MAP = [
    ("rules", ".claude/rules"),
    ("commands", ".claude/commands"),
    ("skills", ".claude/skills"),
    ("schemas", ".claude/schemas"),
]


def _read_project_artifact_dir(project_dir: Path) -> Optional[str]:
    path = project_dir / ".ai-dev-system.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw = data.get("artifact_dir")
    if not isinstance(raw, str) or not raw.strip():
        return None
    return raw.strip()


def _copy_tree(src: Path, dest: Path) -> None:
    if not src.is_dir():
        print(f"missing build output: {src} (run: python3 scripts/build.py)", file=sys.stderr)
        raise SystemExit(1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _install_target(name: str, mapping: list[tuple[str, str]], project_dir: Path, dist_root: Path) -> None:
    src_root = dist_root / name
    for rel_src, rel_dest in mapping:
        src = src_root / rel_src
        dest = project_dir / rel_dest
        _copy_tree(src, dest)
        print(f"  {rel_dest}")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="Copy dist/ artifacts into a target project's .cursor/ and .claude/ dirs.",
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Target project directory (default: cwd)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--cursor-only", action="store_true", help="Install Cursor artifacts only")
    group.add_argument("--claude-only", action="store_true", help="Install Claude artifacts only")
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="Override artifact path (default: recipes/project.yaml or .ai-dev-system.yaml)",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    project_dir = Path(args.project_dir).resolve()

    do_cursor = not args.claude_only
    do_claude = not args.cursor_only

    artifact_dir = args.artifact_dir or _read_project_artifact_dir(project_dir)
    default_project = build_module._load_project_config(RECIPES)
    needs_rebuild = artifact_dir is not None and artifact_dir != default_project.artifact_dir

    dist_root = DIST
    tmp: Optional[tempfile.TemporaryDirectory[str]] = None
    if needs_rebuild:
        tmp = tempfile.TemporaryDirectory(prefix="ai-dev-system-install-")
        dist_root = Path(tmp.name) / "dist"
        targets = set()
        if do_cursor:
            targets.add("cursor")
        if do_claude:
            targets.add("claude")
        selection = build_module.BuildSelection(targets=targets, filters=[])
        paths = build_module.BuildPaths(recipes_dir=RECIPES, dist_dir=dist_root)
        build_module.run_build(selection, paths, artifact_dir=artifact_dir)
        print(f"Built dist with artifact_dir={artifact_dir!r}\n")

    print(f"Installing into {project_dir}\n")

    if do_cursor:
        print("Cursor (.cursor/):")
        _install_target("cursor", CURSOR_MAP, project_dir, dist_root)

    if do_claude:
        if do_cursor:
            print()
        print("Claude (.claude/):")
        _install_target("claude", CLAUDE_MAP, project_dir, dist_root)

    if tmp is not None:
        tmp.cleanup()

    print("\nDone. Rebuild recipes with: python3 scripts/build.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
