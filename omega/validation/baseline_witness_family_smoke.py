"""Cross-platform baseline witness family smoke runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.baseline_witnesses.family_smoke import run_family_smoke
from omega.validation._common import run_pytest, timestamped_run_root


FAMILY_TESTS = [
    "tests/test_chain_evidence_class_soundness_family.py",
    "tests/test_coarse_bisimulation_consequence_profile_family.py",
    "tests/test_compression_score_merge_soundness_family.py",
    "tests/test_control_reach_declared_recovery_family.py",
    "tests/test_entropy_recovery_profile_family.py",
    "tests/test_frontier_morphology_loss_profile_family.py",
    "tests/test_intervention_effect_declared_recovery_family.py",
    "tests/test_marginal_success_joint_success_family.py",
    "tests/test_mutual_information_declared_recovery_family.py",
    "tests/test_observation_rank_declared_recovery_family.py",
    "tests/test_optimized_success_declared_recovery_family.py",
    "tests/test_reachability_declared_recovery_family.py",
    "tests/test_viability_kernel_declared_recovery_family.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the baseline witness family smoke.")
    parser.add_argument("--out-root", type=Path, default=Path(".tmp/baseline_witness_family_smoke"))
    parser.add_argument("--max-nuisance-bits", type=int, default=5)
    parser.add_argument("--skip-pytest", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_baseline_witness_family_smoke(
        out_root=args.out_root,
        max_nuisance_bits=args.max_nuisance_bits,
        skip_pytest=args.skip_pytest,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_baseline_witness_family_smoke(
    *,
    out_root: Path = Path(".tmp/baseline_witness_family_smoke"),
    max_nuisance_bits: int = 5,
    skip_pytest: bool = False,
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    summary = run_family_smoke(max_nuisance_bits=max_nuisance_bits)
    if summary["status"] != "PASS":
        raise AssertionError(f"family smoke failed: {summary}")

    if not skip_pytest:
        run_pytest(FAMILY_TESTS, run_root=run_root)

    return {
        "status": "PASS",
        "run_root": str(run_root),
        "max_nuisance_bits": summary["max_nuisance_bits"],
        "family_count": summary["family_count"],
        "case_count": summary["case_count"],
        "aggregate_check": "passed",
        "focused_pytest": "skipped" if skip_pytest else "passed",
        "families": summary["families"],
        "not_claimed": summary["not_claimed"],
    }


if __name__ == "__main__":
    main()

