from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_entropy_different_recovery_profile import (
    PRESERVE_A_CHANNEL,
    PRESERVE_B_CHANNEL,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_entropy_different_recovery_profile_witness(tmp_path: Path) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_entropy_different_recovery_profile"
    assert result["entropy_controls_hold"] is True
    assert result["all_expected_relations_hold"] is True
    assert result["recovery_profile_differs"] is True
    assert result["preserve_a_recovery_profile"] == "recovered:D_A|failed:D_B"
    assert result["preserve_b_recovery_profile"] == "recovered:D_B|failed:D_A"

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}


def test_entropy_controls_match_while_recovery_profiles_differ(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    entropy = {row["channel_id"]: row for row in read_csv(out / "entropy_baseline_by_channel.csv")}
    assert entropy[PRESERVE_A_CHANNEL]["global_target_entropy_bits"] == "2.000000"
    assert entropy[PRESERVE_B_CHANNEL]["global_target_entropy_bits"] == "2.000000"
    assert entropy[PRESERVE_A_CHANNEL]["per_source_entropy_bits_signature"] == (
        entropy[PRESERVE_B_CHANNEL]["per_source_entropy_bits_signature"]
    )
    assert entropy[PRESERVE_A_CHANNEL]["global_target_weight_signature"] == (
        entropy[PRESERVE_B_CHANNEL]["global_target_weight_signature"]
    )

    recovery = {
        (row["channel_id"], row["source_distinction_id"]): row
        for row in read_csv(out / "declared_recovery_by_distinction.csv")
    }
    assert recovery[(PRESERVE_A_CHANNEL, "D_A")]["recovery_status"] == "declared_recovery_pass"
    assert recovery[(PRESERVE_A_CHANNEL, "D_B")]["recovery_status"] == "declared_recovery_fail"
    assert recovery[(PRESERVE_B_CHANNEL, "D_A")]["recovery_status"] == "declared_recovery_fail"
    assert recovery[(PRESERVE_B_CHANNEL, "D_B")]["recovery_status"] == "declared_recovery_pass"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert "Omega validation" in summary["not_claimed"]
