from __future__ import annotations

import json
from pathlib import Path

from omega.future_field_atlas.util import read_csv
from omega.stochastic_distinction_channel.probe import run_probe


def test_stochastic_channel_tightening_outputs_formal_consumption_bundle(tmp_path: Path) -> None:
    out = tmp_path / "channel_probe"
    result = run_probe(out_dir=out)

    assert result["formal_consumption_status"] == "support_level_ready_probabilistic_measurement_only"
    bundle = json.loads((out / "formal_channel_consumption_bundle.json").read_text(encoding="utf-8"))
    assert bundle["strict_support_consumption"] == 1
    assert bundle["consumption_artifacts"]["decoder_policy_manifest"] == "decoder_policy_manifest.csv"
    assert bundle["consumption_artifacts"]["declared_target_policy_summary"] == "declared_target_policy_summary.csv"

    support_probability = read_csv(out / "support_vs_probability_summary.csv")
    identity_joint = one_row(support_probability, "identity_channel", "D_joint")
    assert identity_joint["support_probability_relation"] == "exact_and_high_probability"
    assert identity_joint["exact_support_target_distinction_ids"] == "E_joint"

    bitflip_a = one_row(support_probability, "bit_flip_p_0_05", "D_A")
    assert bitflip_a["support_probability_relation"] == "probabilistic_without_exact_support"
    assert bitflip_a["best_probability_target_distinction_id"] == "E_A"

    non_erasure = read_csv(out / "non_erasure_by_channel.csv")
    identity_marginals = [
        row
        for row in non_erasure
        if row["channel_id"] == "identity_channel"
        and row["requirement_set_id"] == "req_marginals"
        and row["decoder_policy_id"] == "fixed_declared_target_distinction"
    ][0]
    assert "D_A=E_A" in identity_marginals["selected_target_distinction_ids"]
    assert "D_B=E_B" in identity_marginals["selected_target_distinction_ids"]

    marginal_joint_rows = read_csv(out / "marginal_joint_recoverability_diagnostic.csv")
    assert {
        row["decoder_policy_id"]
        for row in marginal_joint_rows
        if row["channel_id"] == "marginal_joint_degrade_q_0_10"
    } == {"bayes_best_target_distinction", "fixed_declared_target_distinction"}

    fixed_policy = read_csv(out / "declared_target_policy_summary.csv")
    parity_fixed = one_policy_row(fixed_policy, "marginal_joint_degrade_q_0_10", "D_parity")
    assert parity_fixed["fixed_target_distinction_id"] == "E_parity"
    assert parity_fixed["bayes_best_target_distinction_id"] == "E_joint"

    support_rows = read_csv(out / "support_recoverability.csv")
    noisy_a = [
        row
        for row in support_rows
        if row["channel_id"] == "bit_flip_p_0_05"
        and row["source_distinction_id"] == "D_A"
        and row["target_distinction_id"] == "E_A"
    ][0]
    assert noisy_a["exact_support_recoverability"] == "0"
    assert noisy_a["support_source_label_coverage_complete"] == "0"
    assert int(noisy_a["ambiguous_support_target_label_count"]) > 0


def one_row(rows: list[dict[str, str]], channel_id: str, source_distinction_id: str) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row["channel_id"] == channel_id and row["source_distinction_id"] == source_distinction_id
    ]
    assert len(matches) == 1
    return matches[0]


def one_policy_row(rows: list[dict[str, str]], channel_id: str, source_distinction_id: str) -> dict[str, str]:
    return one_row(rows, channel_id, source_distinction_id)
