from __future__ import annotations

import json
from pathlib import Path

from omega.future_field_atlas.util import read_csv
from omega.stochastic_distinction_channel.probe import run_probe
from omega.stochastic_distinction_channel.theorem_transfer_audit import run_theorem_transfer_audit


def test_theorem_transfer_audit_builds_same_path_cascade_bounds(tmp_path: Path) -> None:
    source = tmp_path / "probe"
    out = tmp_path / "audit"
    run_probe(out_dir=source)

    result = run_theorem_transfer_audit(source_dir=source, out_dir=out)

    assert result["audit_status"] == "support_and_probabilistic_transfer_ready"
    bound_rows = read_csv(out / "cascade_bound_check.csv")
    assert bound_rows
    assert {row["theorem_applicability_status"] for row in bound_rows} == {
        "theorem_applicable_generated_natural_weights"
    }
    assert all(row["bound_pass"] == "1" for row in bound_rows)
    assert {row["cascade_evidence_status"] for row in bound_rows} == {"path_rows_retained"}
    assert {row["registry_digest"] for row in bound_rows} == {"unregistered_legacy_source"}
    assert {row["recovery_provenance_class"] for row in bound_rows} == {
        "fixed_declared_policy_no_registry"
    }

    denominator_rows = read_csv(out / "denominator_alignment_audit.csv")
    assert denominator_rows
    assert {row["denominator_alignment_status"] for row in denominator_rows} == {"aligned_same_path_ensemble"}
    assert all(row["uses_independently_normalized_stage_errors"] == "0" for row in denominator_rows)

    total_rows = read_csv(out / "cascade_total_mass.csv")
    assert total_rows
    assert all(row["path_total_equals_composed_total"] == "1" for row in total_rows)


def test_theorem_transfer_audit_preserves_policy_and_decoder_boundaries(tmp_path: Path) -> None:
    source = tmp_path / "probe"
    out = tmp_path / "audit"
    run_probe(out_dir=source)
    run_theorem_transfer_audit(source_dir=source, out_dir=out)

    policy_rows = read_csv(out / "decoder_policy_alignment_audit.csv")
    assert "aligned_declared_composition" in {row["policy_alignment_status"] for row in policy_rows}
    assert "measurement_only_best_decoder_comparison" in {row["policy_alignment_status"] for row in policy_rows}
    bayes_rows = [row for row in policy_rows if row["policy_alignment_status"] == "measurement_only_best_decoder_comparison"]
    assert {row["recovery_provenance_class"] for row in bayes_rows} == {"optimized_policy_search"}
    assert {row["cascade_evidence_status"] for row in bayes_rows} == {"summary_only_blocked"}

    decoder_audit = read_csv(out / "no_self_evidencing_decoder_audit.csv")
    assert decoder_audit
    assert all(row["audit_status"] == "PASS" for row in decoder_audit)
    assert all(row["allowed_for_recovery_claim"] == "1" for row in decoder_audit)
    assert all(row["uses_target_observation_only"] == "1" for row in decoder_audit)
    assert "recovery_provenance_class" in decoder_audit[0]
    assert {row["registry_digest"] for row in decoder_audit} == {"unregistered_legacy_source"}

    support_boundary = read_csv(out / "support_probability_theorem_boundary.csv")
    assert support_boundary
    assert "recovery_provenance_class" in support_boundary[0]
    assert "cascade_evidence_status" in support_boundary[0]

    bundle = json.loads((out / "probabilistic_channel_theorem_transfer_bundle.json").read_text(encoding="utf-8"))
    assert bundle["overall_status"] == "support_and_probabilistic_transfer_ready"
    assert bundle["cascade_bound_check"] == "cascade_bound_check.csv"
    assert bundle["registry_digest"] == "unregistered_legacy_source"
