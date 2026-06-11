from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_observation_rank_different_declared_recovery import (
    DECLARED_OBSERVER,
    NUISANCE_OBSERVER,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_observation_rank_different_declared_recovery_witness(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_observation_rank_different_declared_recovery"
    assert result["baseline_controls_hold"] is True
    assert result["all_expected_relations_hold"] is True
    assert result["finite_observation_rank"] == 1
    assert result["declared_observer_exact_declared_recovery"] is True
    assert result["nuisance_observer_exact_declared_recovery"] is False

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}
    assert {row["metric"] for row in comparison} == {
        "state_count",
        "output_support_size",
        "output_support",
        "finite_observation_rank",
        "observation_block_count",
        "observation_block_size_signature",
        "output_to_state_count_signature",
        "deterministic_observer",
        "declared_recovery_signature",
    }


def test_observation_rank_does_not_license_declared_recovery(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    baseline = {
        row["observer_id"]: row
        for row in read_csv(out / "observability_baseline_by_observer.csv")
    }
    assert baseline[DECLARED_OBSERVER]["finite_observation_rank"] == "1"
    assert baseline[NUISANCE_OBSERVER]["finite_observation_rank"] == "1"
    assert baseline[DECLARED_OBSERVER]["observation_block_size_signature"] == (
        baseline[NUISANCE_OBSERVER]["observation_block_size_signature"]
    )
    assert baseline[DECLARED_OBSERVER]["output_to_state_count_signature"] == (
        baseline[NUISANCE_OBSERVER]["output_to_state_count_signature"]
    )

    recovery = {
        row["observer_id"]: row
        for row in read_csv(out / "declared_recovery_by_observer.csv")
    }
    assert recovery[DECLARED_OBSERVER]["recovery_status"] == "declared_recovery_pass"
    assert recovery[NUISANCE_OBSERVER]["recovery_status"] == "declared_recovery_fail"
    assert recovery[NUISANCE_OBSERVER]["ambiguous_outputs"] == "0->{0,1};1->{0,1}"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_observation_rank_different_declared_recovery"
    assert "full linear observability" in summary["not_claimed"]
    assert "control synthesis" in summary["not_claimed"]
