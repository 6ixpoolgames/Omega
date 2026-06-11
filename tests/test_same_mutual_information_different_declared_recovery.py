from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_mutual_information_different_declared_recovery import (
    DECLARED_CHANNEL,
    NUISANCE_CHANNEL,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_mutual_information_different_declared_recovery_witness(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_mutual_information_different_declared_recovery"
    assert result["information_controls_hold"] is True
    assert result["declared_recovery_differs"] is True
    assert result["all_expected_relations_hold"] is True
    assert result["declared_channel_mutual_information_bits"] == "1.000000"
    assert result["nuisance_channel_mutual_information_bits"] == "1.000000"
    assert result["declared_channel_capacity_bits"] == "1.000000"
    assert result["nuisance_channel_capacity_bits"] == "1.000000"
    assert result["declared_channel_exact_declared_recovery"] is True
    assert result["nuisance_channel_exact_declared_recovery"] is False

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}


def test_information_transfer_does_not_license_declared_recovery(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    information = {row["channel_id"]: row for row in read_csv(out / "information_baseline_by_channel.csv")}
    assert information[DECLARED_CHANNEL]["information_baseline_signature"] == (
        information[NUISANCE_CHANNEL]["information_baseline_signature"]
    )
    assert information[DECLARED_CHANNEL]["mutual_information_source_output_bits"] == "1.000000"
    assert information[NUISANCE_CHANNEL]["mutual_information_source_output_bits"] == "1.000000"
    assert information[DECLARED_CHANNEL]["deterministic_output_capacity_bits"] == "1.000000"
    assert information[NUISANCE_CHANNEL]["deterministic_output_capacity_bits"] == "1.000000"

    recovery = {row["channel_id"]: row for row in read_csv(out / "declared_recovery_by_channel.csv")}
    assert recovery[DECLARED_CHANNEL]["recovery_status"] == "declared_recovery_pass"
    assert recovery[NUISANCE_CHANNEL]["recovery_status"] == "declared_recovery_fail"
    assert recovery[NUISANCE_CHANNEL]["ambiguous_outputs"] == "0->{0,1};1->{0,1}"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_mutual_information_different_declared_recovery"
    assert "semantic recovery" in summary["not_claimed"]
