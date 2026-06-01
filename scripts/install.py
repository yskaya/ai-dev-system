#!/usr/bin/env python3
"""Copy built artifacts from dist/ into a target project."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

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


def _copy_tree(src: Path, dest: Path) -> None:
    if not src.is_dir():
        print(f"missing build output: {src} (run: python3 scripts/build.py)", file=sys.stderr)
        raise SystemExit(1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _install_target(name: str, mapping: list[tuple[str, str]], project_dir: Path) -> None:
    src_root = DIST / name
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
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    project_dir = Path(args.project_dir).resolve()

    do_cursor = not args.claude_only
    do_claude = not args.cursor_only

    print(f"Installing into {project_dir}\n")

    if do_cursor:
        print("Cursor (.cursor/):")
        _install_target("cursor", CURSOR_MAP, project_dir)

    if do_claude:
        if do_cursor:
            print()
        print("Claude (.claude/):")
        _install_target("claude", CLAUDE_MAP, project_dir)

    print("\nDone. Rebuild recipes with: python3 scripts/build.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
