"""Shared utilities for ai-dev-system tests."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
FIXTURE_RECIPES = TESTS_DIR / "fixtures" / "recipes"
EXPECTED_DIR = TESTS_DIR / "expected"

sys.path.insert(0, str(ROOT / "scripts"))
import build as build_module  # noqa: E402


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(md: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text) for --- delimited YAML frontmatter."""
    if not md.startswith("---\n"):
        return {}, md
    parts = md.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, md
    fm_raw = parts[0][4:]
    rest = parts[1]
    fm = yaml.safe_load(fm_raw) or {}
    if not isinstance(fm, dict):
        fm = {}
    return fm, rest.lstrip("\n")


def extract_skills_mentions(md: str) -> list[str]:
    _, body = split_frontmatter(md)
    for line in body.splitlines():
        if line.startswith("Skills: "):
            return [tok[1:] for tok in line[len("Skills: ") :].split() if tok.startswith("@")]
    return []


@dataclass(frozen=True)
class OutputCase:
    """One golden-file comparison: fixture recipe id → expected dist relative path."""

    id: str
    rel_path: str
    targets: tuple[str, ...] = ("cursor", "claude")


def build_fixture_dist(
    *,
    dist_dir: Path,
    targets: Iterable[str] = ("cursor", "claude"),
    filters: Optional[list[str]] = None,
) -> None:
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)
    selection = build_module.BuildSelection(
        targets=set(targets),
        filters=filters or [],
    )
    paths = build_module.BuildPaths(
        recipes_dir=FIXTURE_RECIPES.resolve(),
        dist_dir=dist_dir.resolve(),
    )
    build_module.run_build(selection, paths)


class FixtureBuildTestCase(unittest.TestCase):
    """Build fixture recipes into a temp dist/ and compare to tests/expected/."""

    dist_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="ai-dev-system-fixture-")
        cls.dist_dir = Path(cls._tmp.name)
        build_fixture_dist(dist_dir=cls.dist_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def assert_matches_expected(self, case: OutputCase) -> None:
        for target in case.targets:
            built = self.dist_dir / target / case.rel_path
            expected = EXPECTED_DIR / target / case.rel_path
            self.assertTrue(built.is_file(), f"missing build output: {built}")
            self.assertTrue(expected.is_file(), f"missing golden file: {expected}")
            self.assertEqual(
                read_text(built),
                read_text(expected),
                f"{case.id} ({target}): output differs from expected — "
                f"re-run: python3 tests/generate_expected.py",
            )
