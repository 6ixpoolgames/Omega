from __future__ import annotations

import csv
import json
from pathlib import Path

from omega.future_field_atlas.util import read_csv, write_csv
from omega.stochastic_distinction_channel.probe import run_probe
from omega.stochastic_distinction_channel.theorem_transfer_audit import run_theorem_transfer_audit
from omega.stochastic_distinction_channel.thresholded_non_erasure import run_thresholded_non_erasure


def test_thresholded_non_erasure_predictive_fixtures(tmp_path: Path) -> None:
    probe, audit, out = run_all(tmp_path)

    rows = read_csv(out / "thresholded_prob_non_erasure_by_channel.csv")
    identity_all = one_non_erasure(rows, "identity_channel", "req_all_nontrivial", "threshold_1_00")
    assert identity_all["prob_non_erasing"] == "1"
    assert identity_all["non_erasure_status"] == "prob_non_erasing"

    bitflip_marginals = one_non_erasure(rows, "bit_flip_p_0_05", "req_marginals", "threshold_0_95")
    assert bitflip_marginals["prob_non_erasing"] == "1"
    assert bitflip_marginals["recovery_provenance_class"] == "fixed_declared_policy_no_registry"
    assert bitflip_marginals["registry_digest"] == "unregistered_legacy_source"
    assert bitflip_marginals["cascade_evidence_status"] == "path_rows_retained"
    assert bitflip_marginals["theorem_transfer_class"] == "fixed_declared_policy_unregistered_measurement"

    bitflip_joint = one_non_erasure(rows, "bit_flip_p_0_05", "req_joint", "threshold_0_95")
    assert bitflip_joint["prob_non_erasing"] == "0"
    assert bitflip_joint["non_erasure_status"] == "not_non_erasing_below_threshold"

    total_erasure_joint = one_non_erasure(rows, "total_erasure_channel", "req_joint", "threshold_0_80")
    assert total_erasure_joint["non_erasure_status"] == "blocked_missing_fixed_target"

    boundary = read_csv(out / "thresholded_support_probability_boundary.csv")
    bitflip_boundary = one_boundary(boundary, "bit_flip_p_0_05", "req_marginals", "threshold_0_95")
    assert bitflip_boundary["support_probability_relation"] == "prob_recovered_without_support_exact"


def test_thresholded_non_erasure_monotonicity_and_policy_separation(tmp_path: Path) -> None:
    _probe, _audit, out = run_all(tmp_path)

    monotonicity = read_csv(out / "prob_non_erasure_monotonicity_check.csv")
    assert monotonicity
    assert {row["status"] for row in monotonicity} == {"pass"}

    non_erasure = read_csv(out / "thresholded_prob_non_erasure_by_channel.csv")
    bayes_rows = [row for row in non_erasure if row["decoder_policy_id"] == "bayes_best_target_policy"]
    assert bayes_rows
    assert {row["non_erasure_status"] for row in bayes_rows} == {"measurement_only_bayes_best"}
    assert all(row["prob_non_erasing"] == "0" for row in bayes_rows)
    assert {row["recovery_provenance_class"] for row in bayes_rows} == {"optimized_policy_search"}
    assert {row["theorem_transfer_class"] for row in bayes_rows} == {"optimized_policy_search_measurement"}

    sensitivity = read_csv(out / "threshold_sensitivity_by_requirement.csv")
    one_sensitivity = [
        row
        for row in sensitivity
        if row["channel_id"] == "bit_flip_p_0_05"
        and row["requirement_set_id"] == "req_marginals"
        and row["decoder_policy_id"] == "fixed_declared_target_policy"
    ][0]
    assert one_sensitivity["threshold_0_80_status"] == "prob_non_erasing"
    assert one_sensitivity["threshold_0_95_status"] == "prob_non_erasing"
    assert one_sensitivity["threshold_0_99_status"] == "not_non_erasing_below_threshold"


def test_thresholded_non_erasure_missing_recoverability_blocks(tmp_path: Path) -> None:
    probe = tmp_path / "probe"
    audit = tmp_path / "audit"
    out = tmp_path / "thresholded"
    run_probe(out_dir=probe)
    rows = read_csv(probe / "recoverability_by_distinction.csv")
    rows = [
        row
        for row in rows
        if row["decoder_id"] != "dec::identity_channel::D_A::E_A::bayes_optimal_decoder"
    ]
    write_csv(probe / "recoverability_by_distinction.csv", rows)
    run_theorem_transfer_audit(source_dir=probe, out_dir=audit)
    run_thresholded_non_erasure(audit_source=audit, probe_source=probe, out_dir=out)

    recovery = read_csv(out / "thresholded_prob_recovery_by_distinction.csv")
    assert "recovery_provenance_class" in recovery[0]
    assert "registry_digest" in recovery[0]
    assert "cascade_evidence_status" in recovery[0]
    blocked = [
        row
        for row in recovery
        if row["channel_id"] == "identity_channel"
        and row["distinction_id"] == "D_A"
        and row["decoder_policy_id"] == "fixed_declared_target_policy"
        and row["threshold_id"] == "threshold_1_00"
    ][0]
    assert blocked["recovery_status"] == "blocked_missing_recoverability"


def test_thresholded_non_erasure_headers_do_not_promote_reserved_semantics(tmp_path: Path) -> None:
    _probe, _audit, out = run_all(tmp_path)
    reserved = {"agency", "value", "valuer", "compatibility", "capture", "ethical_erasure", "omega"}
    for path in out.glob("*.csv"):
        with path.open("r", newline="", encoding="utf-8") as handle:
            header = next(csv.reader(handle))
        normalized = {column.lower() for column in header}
        assert not (reserved & normalized), path.name


def test_thresholded_non_erasure_bundle_carries_provenance_status(tmp_path: Path) -> None:
    _probe, _audit, out = run_all(tmp_path)

    bundle = json.loads((out / "thresholded_prob_non_erasure_bundle.json").read_text(encoding="utf-8"))
    assert bundle["registry_digest"] == "unregistered_legacy_source"
    assert bundle["cascade_evidence_status"] == "path_rows_retained"

    summary = read_csv(out / "probabilistic_non_erasure_theorem_transfer_summary.csv")
    assert summary
    assert "recovery_provenance_class" in summary[0]
    assert {row["registry_digest"] for row in summary} == {"unregistered_legacy_source"}


def run_all(tmp_path: Path) -> tuple[Path, Path, Path]:
    probe = tmp_path / "probe"
    audit = tmp_path / "audit"
    out = tmp_path / "thresholded"
    run_probe(out_dir=probe)
    run_theorem_transfer_audit(source_dir=probe, out_dir=audit)
    run_thresholded_non_erasure(audit_source=audit, probe_source=probe, out_dir=out)
    return probe, audit, out


def one_non_erasure(
    rows: list[dict[str, str]],
    channel_id: str,
    requirement_set_id: str,
    threshold_id: str,
) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row["channel_id"] == channel_id
        and row["requirement_set_id"] == requirement_set_id
        and row["threshold_id"] == threshold_id
        and row["decoder_policy_id"] == "fixed_declared_target_policy"
    ]
    assert len(matches) == 1
    return matches[0]


def one_boundary(
    rows: list[dict[str, str]],
    channel_id: str,
    requirement_set_id: str,
    threshold_id: str,
) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row["channel_id"] == channel_id
        and row["requirement_set_id"] == requirement_set_id
        and row["threshold_id"] == threshold_id
        and row["decoder_policy_id"] == "fixed_declared_target_policy"
    ]
    assert len(matches) == 1
    return matches[0]
