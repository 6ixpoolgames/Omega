from __future__ import annotations

import json
from pathlib import Path

from omega.future_field_atlas.util import read_csv, write_csv
from omega.stochastic_distinction_channel.registry_first_adversarial_audit import (
    audit_registry_first_output,
)
from omega.stochastic_distinction_channel.registry_first_probe import run_registry_first_probe


def test_registry_first_adversarial_audit_passes_clean_output(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    audit = tmp_path / "audit"
    run_registry_first_probe(out_dir=source, panel="medium")

    result = audit_registry_first_output(source_dir=source, out_dir=audit)

    assert result["overall_status"] == "PASS"
    rows = read_csv(audit / "registry_first_adversarial_audit.csv")
    assert rows
    assert {row["status"] for row in rows} == {"PASS"}


def test_registry_first_adversarial_audit_rejects_registry_mutation(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source)

    rows = read_csv(source / "registry_manifest.csv")
    rows[0]["decoder_count"] = "999"
    write_csv(source / "registry_manifest.csv", rows)

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "artifact_digest_matches" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_threshold_mutation(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source)

    rows = read_csv(source / "threshold_manifest.csv")
    rows[1]["threshold_fraction"] = "99/100"
    write_csv(source / "threshold_manifest.csv", rows)

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "artifact_digest_matches" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_missing_scored_digest(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source)

    rows = read_csv(source / "registered_recovery_by_distinction.csv")
    rows[0]["registry_digest"] = ""
    write_csv(source / "registered_recovery_by_distinction.csv", rows)

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "scored_registry_digest_consistent" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_missing_digest_column(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source)

    rows = read_csv(source / "registered_recovery_by_distinction.csv")
    for row in rows:
        del row["registry_digest"]
    write_csv(source / "registered_recovery_by_distinction.csv", rows)

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "scored_registry_digest_present" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_missing_manifest_digest_column(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source)

    rows = read_csv(source / "registered_recovery_by_distinction.csv")
    for row in rows:
        del row["manifest_bundle_digest"]
    write_csv(source / "registered_recovery_by_distinction.csv", rows)

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "scored_manifest_bundle_digest_present" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_optimized_promotion(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source, panel="medium")

    rows = read_csv(source / "optimized_recovery_diagnostic.csv")
    rows[0]["theorem_transfer_class"] = "declared_registered_recovery_ready"
    write_csv(source / "optimized_recovery_diagnostic.csv", rows)

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "optimized_rows_diagnostic_only" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_optimized_readiness_promotion(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source, panel="medium")

    rows = read_csv(source / "theorem_transfer_readiness.csv")
    cascade_row = [row for row in rows if row["readiness_axis"] == "cascade_union_bound_ready"][0]
    cascade_row["recovery_provenance_class"] = "optimized_diagnostic"
    write_csv(source / "theorem_transfer_readiness.csv", rows)

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "readiness_optimized_evidence_not_transfer_ready" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_digest_chain_omission(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source, panel="medium")

    path = source / "manifest_digest_chain.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["scored_artifact_digests"]["registered_recovery_by_distinction.csv"]
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "digest_chain_required_artifact_listed" in result["failed_audits"]


def test_registry_first_adversarial_audit_rejects_missing_path_evidence(tmp_path: Path) -> None:
    source = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=source)

    (source / "path_ensemble_rows.csv").unlink()

    result = audit_registry_first_output(source_dir=source)

    assert result["overall_status"] == "FAIL_BLOCK_THEOREM_TRANSFER"
    assert "required_file_present" in result["failed_audits"]
    assert "cascade_ready_has_path_rows" in result["failed_audits"]
