"""Cross-platform baseline witness smoke runner."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

from omega.validation._common import (
    assert_equal,
    read_json,
    resolve_repo_path,
    run_pytest,
    timestamped_run_root,
)


WITNESS_SPECS: tuple[dict[str, str], ...] = (
    {
        "id": "same_reachability_different_recovery_v0",
        "module": "omega.baseline_witnesses.same_reachability_different_recovery",
        "expected_status": "same_reachability_different_declared_recovery",
        "retained_summary": "20260611_same_reachability_different_recovery_v0/witness_summary.json",
        "test": "tests/test_same_reachability_different_recovery.py",
    },
    {
        "id": "same_entropy_different_recovery_profile_v0",
        "module": "omega.baseline_witnesses.same_entropy_different_recovery_profile",
        "expected_status": "same_entropy_different_recovery_profile",
        "retained_summary": "20260611_same_entropy_different_recovery_profile_v0/witness_summary.json",
        "test": "tests/test_same_entropy_different_recovery_profile.py",
    },
    {
        "id": "same_frontier_morphology_different_loss_profile_v0",
        "module": "omega.baseline_witnesses.same_frontier_morphology_different_loss_profile",
        "expected_status": "same_frontier_morphology_different_declared_loss_profile",
        "retained_summary": "20260611_same_frontier_morphology_different_loss_profile_v0/witness_summary.json",
        "test": "tests/test_same_frontier_morphology_different_loss_profile.py",
    },
    {
        "id": "same_intervention_effect_different_declared_recovery_v0",
        "module": "omega.baseline_witnesses.same_intervention_effect_different_declared_recovery",
        "expected_status": "same_intervention_effect_different_declared_recovery",
        "retained_summary": "20260611_same_intervention_effect_different_declared_recovery_v0/witness_summary.json",
        "test": "tests/test_same_intervention_effect_different_declared_recovery.py",
    },
    {
        "id": "same_mutual_information_different_declared_recovery_v0",
        "module": "omega.baseline_witnesses.same_mutual_information_different_declared_recovery",
        "expected_status": "same_mutual_information_different_declared_recovery",
        "retained_summary": "20260611_same_mutual_information_different_declared_recovery_v0/witness_summary.json",
        "test": "tests/test_same_mutual_information_different_declared_recovery.py",
    },
    {
        "id": "same_observation_rank_different_declared_recovery_v0",
        "module": "omega.baseline_witnesses.same_observation_rank_different_declared_recovery",
        "expected_status": "same_observation_rank_different_declared_recovery",
        "retained_summary": "20260611_same_observation_rank_different_declared_recovery_v0/witness_summary.json",
        "test": "tests/test_same_observation_rank_different_declared_recovery.py",
    },
    {
        "id": "same_control_reach_different_declared_recovery_v0",
        "module": "omega.baseline_witnesses.same_control_reach_different_declared_recovery",
        "expected_status": "same_control_reach_different_declared_recovery",
        "retained_summary": "20260611_same_control_reach_different_declared_recovery_v0/witness_summary.json",
        "test": "tests/test_same_control_reach_different_declared_recovery.py",
    },
    {
        "id": "same_optimized_success_different_declared_recovery_v0",
        "module": "omega.baseline_witnesses.same_optimized_success_different_declared_recovery",
        "expected_status": "same_optimized_success_different_declared_recovery",
        "retained_summary": "20260611_same_optimized_success_different_declared_recovery_v0/witness_summary.json",
        "test": "tests/test_same_optimized_success_different_declared_recovery.py",
    },
    {
        "id": "same_viability_kernel_different_declared_recovery_v0",
        "module": "omega.baseline_witnesses.same_viability_kernel_different_declared_recovery",
        "expected_status": "same_viability_kernel_different_declared_recovery",
        "retained_summary": "20260611_same_viability_kernel_different_declared_recovery_v0/witness_summary.json",
        "test": "tests/test_same_viability_kernel_different_declared_recovery.py",
    },
    {
        "id": "same_marginal_success_different_joint_success_v0",
        "module": "omega.baseline_witnesses.same_marginal_success_different_joint_success",
        "expected_status": "same_marginal_success_different_joint_success",
        "retained_summary": "20260611_same_marginal_success_different_joint_success_v0/witness_summary.json",
        "test": "tests/test_same_marginal_success_different_joint_success.py",
    },
    {
        "id": "same_compression_score_different_merge_soundness_v0",
        "module": "omega.baseline_witnesses.same_compression_score_different_merge_soundness",
        "expected_status": "same_compression_score_different_merge_soundness",
        "retained_summary": "20260611_same_compression_score_different_merge_soundness_v0/witness_summary.json",
        "test": "tests/test_same_compression_score_different_merge_soundness.py",
    },
    {
        "id": "same_chain_evidence_different_class_soundness_v0",
        "module": "omega.baseline_witnesses.same_chain_evidence_different_class_soundness",
        "expected_status": "same_chain_evidence_different_class_soundness",
        "retained_summary": "20260611_same_chain_evidence_different_class_soundness_v0/witness_summary.json",
        "test": "tests/test_same_chain_evidence_different_class_soundness.py",
    },
    {
        "id": "same_coarse_bisimulation_different_consequence_profile_v0",
        "module": "omega.baseline_witnesses.same_coarse_bisimulation_different_consequence_profile",
        "expected_status": "same_coarse_bisimulation_different_consequence_profile",
        "retained_summary": "20260611_same_coarse_bisimulation_different_consequence_profile_v0/witness_summary.json",
        "test": "tests/test_same_coarse_bisimulation_different_consequence_profile.py",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the baseline witness smoke.")
    parser.add_argument("--out-root", type=Path, default=Path(".tmp/baseline_witness_smoke"))
    parser.add_argument("--retained-root", type=Path, default=Path("results/baseline_witnesses"))
    parser.add_argument("--skip-pytest", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_baseline_witness_smoke(
        out_root=args.out_root,
        retained_root=args.retained_root,
        skip_pytest=args.skip_pytest,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_baseline_witness_smoke(
    *,
    out_root: Path = Path(".tmp/baseline_witness_smoke"),
    retained_root: Path = Path("results/baseline_witnesses"),
    skip_pytest: bool = False,
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    witness_out_root = run_root / "witnesses"
    witness_out_root.mkdir(parents=True, exist_ok=True)
    retained_base = resolve_repo_path(retained_root)
    results: list[dict[str, object]] = []

    for spec in WITNESS_SPECS:
        out_dir = witness_out_root / spec["id"]
        result = run_witness_module(spec["module"], out_dir=out_dir)
        retained_path = retained_base / spec["retained_summary"]
        if not retained_path.exists():
            raise FileNotFoundError(f"retained witness summary missing: {retained_path}")
        retained = read_json(retained_path)
        generated = read_json(out_dir / "witness_summary.json")

        assert_equal(f"{spec['id']}.witness_id", result["witness_id"], spec["id"])
        assert_equal(
            f"{spec['id']}.witness_status",
            result["witness_status"],
            spec["expected_status"],
        )
        assert_equal(f"{spec['id']}.retained_witness_id", retained["witness_id"], spec["id"])
        assert_equal(
            f"{spec['id']}.retained_witness_status",
            retained["witness_status"],
            spec["expected_status"],
        )
        assert_equal(
            f"{spec['id']}.generated_summary_digest",
            generated["summary_digest"],
            result["summary_digest"],
        )
        assert_equal(
            f"{spec['id']}.retained_summary_digest",
            result["summary_digest"],
            retained["summary_digest"],
        )

        results.append(
            {
                "witness_id": spec["id"],
                "witness_status": result["witness_status"],
                "summary_digest": result["summary_digest"],
                "output": str(out_dir),
            }
        )

    if not skip_pytest:
        run_pytest([spec["test"] for spec in WITNESS_SPECS], run_root=run_root)

    return {
        "status": "PASS",
        "run_root": str(run_root),
        "witness_count": len(WITNESS_SPECS),
        "witness_outputs": str(witness_out_root),
        "retained_digest_check": "passed",
        "focused_pytest": "skipped" if skip_pytest else "passed",
        "witnesses": results,
    }


def run_witness_module(module_name: str, *, out_dir: Path) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    runner = getattr(module, "run_witness")
    result = runner(out_dir=out_dir)
    if not isinstance(result, dict):
        raise TypeError(f"{module_name}.run_witness returned {type(result)!r}")
    return result


if __name__ == "__main__":
    main()
