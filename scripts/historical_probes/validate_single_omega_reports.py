from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
PROBE = ROOT / "probe_07_omega_profile_decomposition.py"
PROBE_RESULTS = ROOT / "probe_07_omega_profile_decomposition_results"
VALIDATION_DIR = ROOT / "single_omega_report_validation_results"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_probe(run_id: int, worlds_per_family: int) -> dict:
    env = os.environ.copy()
    env.update(
        {
            "OMEGA_WORKERS": "18",
            "OMEGA_WORLDS_PER_FAMILY": str(worlds_per_family),
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_MAX_THREADS": "1",
            "LOKY_MAX_CPU_COUNT": "18",
        }
    )
    start = time.time()
    completed = subprocess.run(
        [str(PYTHON), str(PROBE)],
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
        timeout=2700,
    )
    elapsed = time.time() - start
    run_dir = VALIDATION_DIR / f"run_{run_id:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        return {
            "run_id": run_id,
            "returncode": completed.returncode,
            "elapsed_seconds": elapsed,
            "status": "ERROR",
            "error": completed.stderr[-2000:],
        }
    for name in [
        "summary.json",
        "candidate_profile_summary.csv",
        "family_A_reversible_irreversible_contrasts.csv",
        "coarse_graining_diagnostics.csv",
        "estimator_report.csv",
    ]:
        src = PROBE_RESULTS / name
        if src.exists():
            shutil.copy2(src, run_dir / name)
    summary = load_json(run_dir / "summary.json")
    return {
        "run_id": run_id,
        "returncode": completed.returncode,
        "elapsed_seconds": elapsed,
        "status": summary.get("runtime_status"),
        "worlds_completed": summary.get("worlds_completed"),
        "truncation_fraction": summary.get("truncation_fraction"),
        "family_A_mean_contrasts": summary.get("family_A_mean_contrasts", {}),
        "flags": summary.get("flags", {}),
    }


def compare_runs(runs: list[dict]) -> dict:
    successful = [r for r in runs if r.get("returncode") == 0]
    if not successful:
        return {"reproducible": False, "reason": "no successful runs"}
    keys = ["Delta_p_viable", "Delta_H_cond", "Delta_H_weighted", "Delta_H_recoverability"]
    contrasts = {key: [r["family_A_mean_contrasts"].get(key, 0.0) for r in successful] for key in keys}
    spreads = {key: max(vals) - min(vals) for key, vals in contrasts.items()}
    flag_sets = [r.get("flags", {}) for r in successful]
    flag_agreement = {}
    for key in sorted({k for flags in flag_sets for k in flags}):
        values = {flags.get(key) for flags in flag_sets}
        flag_agreement[key] = len(values) == 1
    return {
        "successful_runs": len(successful),
        "requested_runs": len(runs),
        "mean_elapsed_seconds": sum(r["elapsed_seconds"] for r in successful) / len(successful),
        "contrast_spreads": spreads,
        "all_core_contrasts_stable": all(spread < 1e-9 for spread in spreads.values()),
        "all_flags_agree": all(flag_agreement.values()),
        "flag_agreement": flag_agreement,
    }


def main() -> int:
    runs = int(os.environ.get("OMEGA_VALIDATION_RUNS", "3"))
    worlds_per_family = int(os.environ.get("OMEGA_WORLDS_PER_FAMILY", "250"))
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    run_summaries = []
    for run_id in range(1, runs + 1):
        result = run_probe(run_id, worlds_per_family)
        run_summaries.append(result)
        (VALIDATION_DIR / "partial_summary.json").write_text(json.dumps(run_summaries, indent=2), encoding="utf-8")
    comparison = compare_runs(run_summaries)
    final = {
        "runs": run_summaries,
        "comparison": comparison,
        "worlds_per_family": worlds_per_family,
        "workers": 18,
    }
    (VALIDATION_DIR / "summary.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print("\nSINGLE OMEGA REPORT VALIDATION")
    print(f"- runs: {comparison.get('successful_runs', 0)} / {runs}")
    print(f"- mean runtime: {comparison.get('mean_elapsed_seconds', 0.0):.2f}s")
    print(f"- core contrasts stable: {str(comparison.get('all_core_contrasts_stable', False)).lower()}")
    print(f"- flags agree: {str(comparison.get('all_flags_agree', False)).lower()}")
    print(f"- results: {VALIDATION_DIR}")
    return 0 if comparison.get("successful_runs", 0) == runs else 1


if __name__ == "__main__":
    raise SystemExit(main())
