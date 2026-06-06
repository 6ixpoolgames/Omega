from __future__ import annotations

from collections import Counter
from pathlib import Path

from omega.future_field_atlas.util import read_csv
from omega.stochastic_distinction_channel.registry_first_adversarial_audit import (
    audit_registry_first_output,
)
from omega.stochastic_distinction_channel.registry_first_x3_probe import (
    run_registry_first_x3_probe,
)


def test_registry_first_x3_probe_emits_expected_surface(tmp_path: Path) -> None:
    out = tmp_path / "registry_first_x3"

    result = run_registry_first_x3_probe(out_dir=out)

    assert result["carrier_id"] == "X3"
    assert result["overall_status"] == "registry_first_theorem_transfer_ready"
    assert result["channel_count"] == 15
    assert result["registered_rows"] == 120
    assert result["gap_rows"] == 120
    assert result["cascade_evidence_status"] == "path_rows_retained"

    carrier = read_csv(out / "carrier_manifest.csv")
    assert len(carrier) == 1
    assert carrier[0]["carrier_id"] == "X3"
    assert carrier[0]["carrier_role"] == "source_and_target"
    assert carrier[0]["state_count"] == "8"
    assert carrier[0]["states"] == "000;001;010;011;100;101;110;111"


def test_registry_first_x3_probe_gap_classes_are_revelatory(tmp_path: Path) -> None:
    out = tmp_path / "registry_first_x3"
    run_registry_first_x3_probe(out_dir=out)

    gap_rows = read_csv(out / "provenance_gap_by_distinction.csv")
    class_counts = Counter(row["theorem_transfer_class"] for row in gap_rows)

    assert class_counts == {
        "declared_registered_recovery_ready": 36,
        "existence_capacity_only": 13,
        "optimized_diagnostic_only": 8,
        "not_recovered": 63,
    }

    identity_bad = one_gap(gap_rows, "identity_channel", "reg_bad_declared_D_A_E_A")
    assert identity_bad["registered_recovery"] == "0"
    assert identity_bad["existence_recovery"] == "1"
    assert identity_bad["optimized_recovery"] == "1"
    assert identity_bad["theorem_transfer_class"] == "existence_capacity_only"

    rotate_a = one_gap(gap_rows, "rotate_bits_channel", "reg_declared_D_A_E_A")
    assert rotate_a["registered_recovery"] == "0"
    assert rotate_a["existence_recovery"] == "0"
    assert rotate_a["optimized_recovery"] == "1"
    assert rotate_a["theorem_transfer_class"] == "optimized_diagnostic_only"


def test_registry_first_x3_probe_readiness_and_path_evidence(tmp_path: Path) -> None:
    out = tmp_path / "registry_first_x3"
    run_registry_first_x3_probe(out_dir=out)

    readiness = {row["readiness_axis"]: row for row in read_csv(out / "theorem_transfer_readiness.csv")}
    assert readiness["support_exact_capacity_ready"]["status"] == "ready"
    assert readiness["registered_recovery_ready"]["status"] == "ready"
    assert readiness["declared_registered_recovery_ready"]["status"] == "ready"
    assert readiness["probability_measurement_ready"]["status"] == "ready"
    assert readiness["cascade_union_bound_ready"]["status"] == "ready"
    assert readiness["policy_substitution_blocked"]["status"] == "ready"
    assert readiness["optimized_diagnostic_only"]["status"] == "ready"
    assert readiness["substrate_bridge_ready"]["status"] == "not_ready"

    path_rows = read_csv(out / "path_ensemble_rows.csv")
    assert path_rows
    assert all(int(row["path_weight"]) > 0 for row in path_rows)
    assert {"registry_digest", "manifest_bundle_digest"}.issubset(path_rows[0])

    summary = read_csv(out / "cascade_evidence_summary.csv")
    assert summary
    assert {row["cascade_evidence_status"] for row in summary} == {"path_rows_retained"}
    assert {row["theorem_transfer_eligible"] for row in summary} == {"1"}
    assert all(int(row["composite_error_mass"]) <= int(row["bound_rhs_error_mass"]) for row in summary)


def test_registry_first_x3_output_passes_adversarial_audit(tmp_path: Path) -> None:
    source = tmp_path / "registry_first_x3"
    audit = tmp_path / "audit"
    run_registry_first_x3_probe(out_dir=source)

    result = audit_registry_first_output(source_dir=source, out_dir=audit)

    assert result["overall_status"] == "PASS"
    assert result["audit_rows"] == 105
    assert result["failure_count"] == 0
    rows = read_csv(audit / "registry_first_adversarial_audit.csv")
    assert rows
    assert {row["status"] for row in rows} == {"PASS"}


def one_gap(rows: list[dict[str, str]], channel_id: str, registry_id: str) -> dict[str, str]:
    matches = [
        row for row in rows if row["channel_id"] == channel_id and row["registry_id"] == registry_id
    ]
    assert len(matches) == 1
    return matches[0]
