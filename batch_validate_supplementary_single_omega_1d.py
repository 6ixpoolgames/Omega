from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SCRIPT = ROOT / "validate_supplementary_single_omega_1d.py"
SOURCE_RESULTS = ROOT / "supplementary_single_omega_1d_validation_results"
BATCH_RESULTS = ROOT / "supplementary_single_omega_1d_batched_validation_results"
SEEDS = [20260510, 20260511, 20260512, 20260513, 20260514]


def run_seed(seed: int) -> dict:
    env = os.environ.copy()
    env.update(
        {
            "OMEGA_WORKERS": "18",
            "OMEGA_VALIDATION_SEED": str(seed),
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_MAX_THREADS": "1",
        }
    )
    start = time.time()
    completed = subprocess.run(
        [str(PYTHON), str(SCRIPT)],
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
        timeout=1200,
    )
    elapsed = time.time() - start
    run_dir = BATCH_RESULTS / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        return {"seed": seed, "returncode": completed.returncode, "elapsed_seconds": elapsed, "flags": {}}
    for name in ["summary.json", "summary_by_start_and_feature.csv", "condition_feature_metrics.csv"]:
        src = SOURCE_RESULTS / name
        if src.exists():
            shutil.copy2(src, run_dir / name)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    return {
        "seed": seed,
        "returncode": completed.returncode,
        "elapsed_seconds": elapsed,
        "flags": summary["flags"],
        "ordering_checks": summary["ordering_checks"],
        "survival": summary["survival"],
    }


def main() -> int:
    BATCH_RESULTS.mkdir(parents=True, exist_ok=True)
    runs = [run_seed(seed) for seed in SEEDS]
    flag_rates = {}
    for key in sorted({k for run in runs for k in run.get("flags", {})}):
        vals = [bool(run["flags"].get(key)) for run in runs if run["returncode"] == 0]
        flag_rates[key] = sum(vals) / max(len(vals), 1)
    final = {
        "runs": runs,
        "flag_reproduction_rates": flag_rates,
        "all_runs_successful": all(run["returncode"] == 0 for run in runs),
        "all_claim_flags_reproduced_all_runs": all(rate == 1.0 for rate in flag_rates.values()),
        "mean_elapsed_seconds": sum(run["elapsed_seconds"] for run in runs) / len(runs),
    }
    (BATCH_RESULTS / "summary.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print("\nBATCHED SUPPLEMENTARY SINGLE OMEGA VALIDATION")
    print(f"- runs: {sum(run['returncode'] == 0 for run in runs)} / {len(runs)}")
    print(f"- mean runtime: {final['mean_elapsed_seconds']:.2f}s")
    for key, rate in flag_rates.items():
        print(f"- {key}: {rate:.2f}")
    print(f"- results: {BATCH_RESULTS.resolve()}")
    return 0 if final["all_runs_successful"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
