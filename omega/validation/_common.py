"""Shared helpers for validation entry points."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def timestamped_run_root(out_root: Path) -> Path:
    root = out_root if out_root.is_absolute() else repo_root() / out_root
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_root = root / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    return run_root


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else repo_root() / path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_equal(name: str, actual: object, expected: object) -> None:
    if str(actual) != str(expected):
        raise AssertionError(f"{name} expected {expected!r} but got {actual!r}")


def run_pytest(test_paths: list[str], *, run_root: Path) -> None:
    pytest_tmp = run_root / "pytest_tmp"
    pytest_cache = run_root / "pytest_cache"
    pytest_tmp.mkdir(parents=True, exist_ok=True)
    pytest_cache.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        *test_paths,
        "-q",
        "--basetemp",
        str(pytest_tmp),
        "-o",
        f"cache_dir={pytest_cache}",
    ]
    subprocess.run(command, cwd=repo_root(), check=True)

