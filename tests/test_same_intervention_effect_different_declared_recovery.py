from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_intervention_effect_different_declared_recovery import (
    DECLARED_SYSTEM,
    NUISANCE_SYSTEM,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_intervention_effect_different_declared_recovery_witness(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_intervention_effect_different_declared_recovery"
    assert result["baseline_controls_hold"] is True
    assert result["all_expected_relations_hold"] is True
    assert result["source_count"] == 4
    assert result["intervention_count"] == 2
    assert result["declared_system_exact_declared_recovery"] is True
    assert result["nuisance_system_exact_declared_recovery"] is False

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}
    assert {row["metric"] for row in comparison} == {
        "source_count",
        "intervention_count",
        "transition_edge_count",
        "deterministic_transition",
        "target_support_size",
        "target_support",
        "effect_by_intervention_signature",
        "target_support_by_intervention_signature",
        "target_count_by_intervention_signature",
        "declared_recovery_signature",
    }


def test_intervention_effect_summary_does_not_license_declared_recovery(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    baseline = {
        row["system_id"]: row
        for row in read_csv(out / "intervention_effect_baseline_by_system.csv")
    }
    assert baseline[DECLARED_SYSTEM]["effect_by_intervention_signature"] == (
        baseline[NUISANCE_SYSTEM]["effect_by_intervention_signature"]
    )
    assert baseline[DECLARED_SYSTEM]["target_support_by_intervention_signature"] == (
        baseline[NUISANCE_SYSTEM]["target_support_by_intervention_signature"]
    )
    assert baseline[DECLARED_SYSTEM]["target_count_by_intervention_signature"] == (
        baseline[NUISANCE_SYSTEM]["target_count_by_intervention_signature"]
    )
    assert baseline[DECLARED_SYSTEM]["effect_by_intervention_signature"] == (
        "set_effect_0:0;set_effect_1:1"
    )

    recovery = {
        row["system_id"]: row for row in read_csv(out / "declared_recovery_by_system.csv")
    }
    assert recovery[DECLARED_SYSTEM]["recovery_status"] == "declared_recovery_pass"
    assert recovery[NUISANCE_SYSTEM]["recovery_status"] == "declared_recovery_fail"
    assert recovery[NUISANCE_SYSTEM]["ambiguous_target_observations"] == "0->{0,1};1->{0,1}"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_intervention_effect_different_declared_recovery"
    assert "causal abstraction" in summary["not_claimed"]
    assert "counterfactual semantics" in summary["not_claimed"]
