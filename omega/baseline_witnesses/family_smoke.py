"""Aggregate smoke for parameterized baseline witness families.

This module does not create retained artifacts. It runs the finite family
extensions for the retained baseline witnesses and checks that each case reports
the expected non-reduction status.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable

from omega.baseline_witnesses.compression_score_merge_soundness_family import (
    run_family as run_compression_family,
)
from omega.baseline_witnesses.entropy_recovery_profile_family import (
    run_family as run_entropy_family,
)
from omega.baseline_witnesses.frontier_morphology_loss_profile_family import (
    run_family as run_frontier_family,
)
from omega.baseline_witnesses.marginal_success_joint_success_family import (
    run_family as run_marginal_family,
)
from omega.baseline_witnesses.mutual_information_declared_recovery_family import (
    run_family as run_mutual_information_family,
)
from omega.baseline_witnesses.optimized_success_declared_recovery_family import (
    run_family as run_optimized_family,
)
from omega.baseline_witnesses.reachability_declared_recovery_family import (
    run_family as run_reachability_family,
)


FamilyRunner = Callable[..., list[dict[str, object]]]

FAMILY_SPECS: tuple[dict[str, object], ...] = (
    {
        "family_id": "same_reachability_different_declared_recovery_family",
        "runner": run_reachability_family,
        "expected_status": "same_reachability_different_declared_recovery",
        "expected_case_count_at_max": lambda max_bits: max_bits * (max_bits + 1) // 2,
    },
    {
        "family_id": "same_entropy_different_recovery_profile_family",
        "runner": run_entropy_family,
        "expected_status": "same_entropy_different_recovery_profile",
        "expected_case_count_at_max": lambda max_bits: max_bits * (max_bits + 1) // 2,
    },
    {
        "family_id": "same_frontier_morphology_different_declared_loss_profile_family",
        "runner": run_frontier_family,
        "expected_status": "same_frontier_morphology_different_declared_loss_profile",
        "expected_case_count_at_max": lambda max_bits: max_bits,
    },
    {
        "family_id": "same_mutual_information_different_declared_recovery_family",
        "runner": run_mutual_information_family,
        "expected_status": "same_mutual_information_different_declared_recovery",
        "expected_case_count_at_max": lambda max_bits: max_bits * (max_bits + 1) // 2,
    },
    {
        "family_id": "same_optimized_success_different_declared_recovery_family",
        "runner": run_optimized_family,
        "expected_status": "same_optimized_success_different_declared_recovery",
        "expected_case_count_at_max": lambda max_bits: max_bits * (max_bits + 1) // 2,
    },
    {
        "family_id": "same_marginal_success_different_joint_success_family",
        "runner": run_marginal_family,
        "expected_status": "same_marginal_success_different_joint_success",
        "expected_case_count_at_max": lambda max_bits: max_bits,
    },
    {
        "family_id": "same_compression_score_different_merge_soundness_family",
        "runner": run_compression_family,
        "expected_status": "same_compression_score_different_merge_soundness",
        "expected_case_count_at_max": lambda max_bits: max_bits * (max_bits + 1) // 2,
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the baseline witness family smoke.")
    parser.add_argument("--max-nuisance-bits", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_family_smoke(max_nuisance_bits=args.max_nuisance_bits)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_family_smoke(*, max_nuisance_bits: int = 5) -> dict[str, object]:
    if max_nuisance_bits < 1:
        raise ValueError("max_nuisance_bits must be >= 1")

    summaries = []
    failures = []
    total_case_count = 0

    for spec in FAMILY_SPECS:
        runner = spec["runner"]
        if not callable(runner):
            raise TypeError(f"runner is not callable for {spec['family_id']}")

        cases = runner(max_nuisance_bits=max_nuisance_bits)
        expected_status = str(spec["expected_status"])
        expected_cases = expected_case_count(spec, max_nuisance_bits)
        statuses = sorted({str(case["family_case_status"]) for case in cases})
        case_count = len(cases)
        failed_cases = [
            case
            for case in cases
            if str(case["family_case_status"]) != expected_status
        ]

        if case_count != expected_cases:
            failures.append(
                {
                    "family_id": spec["family_id"],
                    "failure": "case_count_mismatch",
                    "expected": expected_cases,
                    "actual": case_count,
                }
            )
        if failed_cases:
            failures.append(
                {
                    "family_id": spec["family_id"],
                    "failure": "unexpected_family_case_status",
                    "expected": expected_status,
                    "actual_statuses": statuses,
                }
            )

        summaries.append(
            {
                "family_id": spec["family_id"],
                "expected_status": expected_status,
                "case_count": case_count,
                "expected_case_count": expected_cases,
                "statuses": statuses,
            }
        )
        total_case_count += case_count

    return {
        "status": "PASS" if not failures else "FAIL",
        "max_nuisance_bits": max_nuisance_bits,
        "family_count": len(FAMILY_SPECS),
        "case_count": total_case_count,
        "failures": failures,
        "families": summaries,
        "not_claimed": [
            "infinite-family theorem",
            "Lean theorem transfer",
            "Omega validation",
            "value detection",
            "valuer detection",
            "agency detection",
            "identity detection",
            "substrate-general theory validation",
        ],
    }


def expected_case_count(spec: dict[str, object], max_nuisance_bits: int) -> int:
    count_fn = spec["expected_case_count_at_max"]
    if not callable(count_fn):
        raise TypeError(f"expected_case_count_at_max is not callable for {spec['family_id']}")
    return int(count_fn(max_nuisance_bits))


if __name__ == "__main__":
    main()
