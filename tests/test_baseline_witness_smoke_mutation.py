from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RETAINED_ROOT = REPO_ROOT / "results" / "baseline_witnesses"
REACHABILITY_SUMMARY = (
    "20260611_same_reachability_different_recovery_v0",
    "witness_summary.json",
)


def test_baseline_witness_smoke_rejects_corrupt_retained_digest(tmp_path: Path) -> None:
    retained = copy_retained_root(tmp_path)
    mutate_summary(retained, {"summary_digest": "mutated_digest"})

    completed = run_smoke_with_retained_root(tmp_path, retained)

    assert completed.returncode != 0
    assert "same_reachability_different_recovery_v0.retained_summary_digest" in combined_output(completed)


def test_baseline_witness_smoke_rejects_corrupt_retained_status(tmp_path: Path) -> None:
    retained = copy_retained_root(tmp_path)
    mutate_summary(retained, {"witness_status": "mutated_status"})

    completed = run_smoke_with_retained_root(tmp_path, retained)

    assert completed.returncode != 0
    assert "same_reachability_different_recovery_v0.retained_witness_status" in combined_output(completed)


def copy_retained_root(tmp_path: Path) -> Path:
    target = tmp_path / "retained_baseline_witnesses"
    shutil.copytree(RETAINED_ROOT, target)
    return target


def mutate_summary(retained_root: Path, updates: dict[str, str]) -> None:
    summary_path = retained_root.joinpath(*REACHABILITY_SUMMARY)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload.update(updates)
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def run_smoke_with_retained_root(
    tmp_path: Path,
    retained_root: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "omega.validation.baseline_witness_smoke",
            "--out-root",
            str(tmp_path / "out"),
            "--retained-root",
            str(retained_root),
            "--skip-pytest",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def combined_output(completed: subprocess.CompletedProcess[str]) -> str:
    return f"{completed.stdout}\n{completed.stderr}"
