from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .run_focused_boundary_recurrence import write_csv


INSTRUMENT_NAME = "rfs_mb0_stage_b2_spectral_augmented_instrument"
INSTRUMENT_VERSION = "0.2.1"
SCHEMA_VERSION = "2026-05-30.2"
CLAIM_BOUNDARY = (
    "No holdout scoring, no n=6 transfer, no alphabet expansion, no candidate "
    "promotion, no Omega detection, no agent detection, no identity detection, "
    "no valuer detection, and no value detection."
)
LOCAL_ONLY_ARTIFACT_POLICY = (
    "Generated CSV/JSON run artifacts are local-only and should not be committed "
    "unless explicitly promoted by a maintainer."
)


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    gate_name: str
    required: bool
    passed: bool
    threshold: object = ""
    observed: object = ""
    blocking_reason: str = ""

    def row(self) -> dict[str, object]:
        return {
            "gate_id": self.gate_id,
            "gate_name": self.gate_name,
            "required": int(self.required),
            "passed": int(self.passed),
            "threshold": self.threshold,
            "observed": self.observed,
            "blocking_reason": self.blocking_reason,
        }


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git_commit(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def instrument_metadata(spec_id: str, runner_module: str, repo_root: Path) -> dict[str, object]:
    return {
        "instrument_name": INSTRUMENT_NAME,
        "instrument_version": INSTRUMENT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "spec_id": spec_id,
        "runner_module": runner_module,
        "git_commit": git_commit(repo_root),
        "claim_boundary": CLAIM_BOUNDARY,
        "artifact_policy": LOCAL_ONLY_ARTIFACT_POLICY,
    }


def write_json(path: Path, payload: dict[str, object] | list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


def write_gate_results(path: Path, gates: list[GateResult]) -> None:
    write_csv(path, [gate.row() for gate in gates])


def output_manifest_rows(files: list[str], out_dir: Path, *, local_only: bool = True) -> list[dict[str, object]]:
    rows = []
    for name in files:
        path = out_dir / name
        exists = path.exists()
        rows.append({
            "file": name,
            "exists": exists,
            "status": "present" if exists else "missing",
            "artifact_scope": "local_only" if local_only else "retained",
            "commit_policy": "do_not_commit" if local_only else "ok_to_commit",
        })
    return rows


def executive_summary_lines(
    *,
    decision: str,
    interpretation: str,
    caveats: list[str],
    next_step: str,
) -> list[str]:
    lines = [
        "## Executive Summary",
        "",
        f"Decision: `{decision}`",
        "",
        interpretation,
        "",
        "Blocking caveats:",
    ]
    if caveats:
        lines.extend(f"- {item}" for item in caveats)
    else:
        lines.append("- none for the scoped smoke contract")
    lines.extend([
        "",
        f"Recommended next step: {next_step}",
        "",
        f"Artifact policy: {LOCAL_ONLY_ARTIFACT_POLICY}",
        "",
    ])
    return lines
