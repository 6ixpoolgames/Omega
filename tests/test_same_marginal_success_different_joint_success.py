from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_marginal_success_different_joint_success import (
    CORRELATED_CHANNEL,
    INDEPENDENT_CHANNEL,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_marginal_success_different_joint_success_witness(tmp_path: Path) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_marginal_success_different_joint_success"
    assert result["controls_hold"] is True
    assert result["same_marginal_success"] is True
    assert result["different_joint_success"] is True
    assert result["correlated_marginal_success_vector"] == "D_A:3/4;D_B:3/4"
    assert result["independent_marginal_success_vector"] == "D_A:3/4;D_B:3/4"
    assert result["correlated_joint_success_fraction"] == "5/8"
    assert result["independent_joint_success_fraction"] == "9/16"

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}


def test_marginal_success_rows_do_not_claim_exact_marginal_preservation(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    marginal = {row["channel_id"]: row for row in read_csv(out / "marginal_success_by_channel.csv")}
    joint = {row["channel_id"]: row for row in read_csv(out / "joint_success_by_channel.csv")}

    assert marginal[CORRELATED_CHANNEL]["marginal_success_vector"] == "D_A:3/4;D_B:3/4"
    assert marginal[INDEPENDENT_CHANNEL]["marginal_success_vector"] == "D_A:3/4;D_B:3/4"
    assert joint[CORRELATED_CHANNEL]["joint_bayes_success_fraction"] == "5/8"
    assert joint[INDEPENDENT_CHANNEL]["joint_bayes_success_fraction"] == "9/16"

    recovery = {
        (row["channel_id"], row["source_distinction_id"]): row
        for row in read_csv(out / "bayes_recovery_by_distinction.csv")
    }
    assert recovery[(CORRELATED_CHANNEL, "D_A")]["bayes_success_fraction"] == "3/4"
    assert recovery[(CORRELATED_CHANNEL, "D_B")]["bayes_success_fraction"] == "3/4"
    assert recovery[(INDEPENDENT_CHANNEL, "D_A")]["bayes_success_fraction"] == "3/4"
    assert recovery[(INDEPENDENT_CHANNEL, "D_B")]["bayes_success_fraction"] == "3/4"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert "exact marginal preservation" in summary["not_claimed"]
