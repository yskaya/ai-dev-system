#!/usr/bin/env python3
"""Regenerate tests/expected from tests/fixtures/recipes."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR))

from helpers import EXPECTED_DIR, build_fixture_dist  # noqa: E402


def main() -> int:
    if EXPECTED_DIR.exists():
        shutil.rmtree(EXPECTED_DIR)
    build_fixture_dist(dist_dir=EXPECTED_DIR, targets=("cursor", "claude"))
    print(f"Wrote golden files under {EXPECTED_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
