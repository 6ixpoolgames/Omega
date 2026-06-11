from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_viability_kernel_different_declared_recovery import (
    DECLARED_SYSTEM,
    NUISANCE_SYSTEM,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_viability_kernel_different_declared_recovery_witness(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_viability_kernel_different_declared_recovery"
    assert result["kernel_controls_hold"] is True
    assert result["all_expected_relations_hold"] is True
    assert result["viability_kernel_size"] == 2
    assert result["viability_kernel_signature"] == "10;11"
    assert result["declared_system_exact_declared_recovery"] is True
    assert result["nuisance_system_exact_declared_recovery"] is False

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}
    assert {row["metric"] for row in comparison} == {
        "source_count",
        "transition_edge_count",
        "deterministic_transition",
        "declared_viability_predicate",
        "viability_kernel_size",
        "viability_kernel_signature",
        "source_to_target_viability_signature",
        "source_viability_signature",
        "declared_recovery_signature",
    }


def test_viability_kernel_summary_does_not_license_declared_recovery(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    kernel = {
        row["system_id"]: row for row in read_csv(out / "viability_kernel_by_system.csv")
    }
    assert kernel[DECLARED_SYSTEM]["viability_kernel_signature"] == "10;11"
    assert kernel[NUISANCE_SYSTEM]["viability_kernel_signature"] == "10;11"
    assert kernel[DECLARED_SYSTEM]["source_to_target_viability_signature"] == (
        kernel[NUISANCE_SYSTEM]["source_to_target_viability_signature"]
    )
    assert kernel[DECLARED_SYSTEM]["source_to_target_viability_signature"] == (
        "00:0;01:0;10:1;11:1"
    )

    recovery = {
        row["system_id"]: row for row in read_csv(out / "declared_recovery_by_system.csv")
    }
    assert recovery[DECLARED_SYSTEM]["recovery_status"] == "declared_recovery_pass"
    assert recovery[NUISANCE_SYSTEM]["recovery_status"] == "declared_recovery_fail"
    assert recovery[NUISANCE_SYSTEM]["ambiguous_target_observations"] == "0->{0,1};1->{0,1}"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_viability_kernel_different_declared_recovery"
    assert "real-world viability" in summary["not_claimed"]
    assert "control synthesis" in summary["not_claimed"]
