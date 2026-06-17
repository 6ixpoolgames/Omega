from pathlib import Path

import pytest

from omega.adapters.finite_relational import (
    SchemaError,
    load_model,
    load_model_path,
    model_digest,
    run_declared_audits,
    validate_provenance,
)
from omega.adapters.finite_relational.cli import run_model_file


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "omega" / "adapters" / "finite_relational" / "fixtures"


def test_sound_fixture_exposes_alpha_surface_and_carrier_certificate() -> None:
    model = load_model_path(FIXTURES / "sound_pass.json")

    provenance = validate_provenance(model)
    results = [result.as_dict() for result in run_declared_audits(model)]

    assert provenance["complete"] is True
    assert len(model_digest(model)) == 64
    assert all(result["passed"] for result in results)
    assert [result["finding"] for result in results] == [
        "alpha_laws_hold",
        "sound",
        "certified",
    ]

    carrier = next(result for result in results if result["kind"] == "carrier_certificate")
    assert carrier["observed"]["certified"] is True
    assert carrier["observed"]["mutually_reachable"] is True


def test_phantom_reachability_fixture_detects_fabricated_path() -> None:
    model = load_model_path(FIXTURES / "phantom_reachability_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "phantom"
    assert result["observed"]["exact_path"] is False
    assert result["observed"]["abstract_path"] is True


def test_hidden_reachability_loss_fixture_detects_abstractly_hidden_loss() -> None:
    model = load_model_path(FIXTURES / "hidden_reachability_loss_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "hidden_loss"
    assert result["observed"]["before_path"] is True
    assert result["observed"]["after_path"] is False
    assert result["observed"]["abstract_path"] is True


def test_proxy_fixture_detects_nonfactorization_witness() -> None:
    model = load_model_path(FIXTURES / "proxy_nonfactorization_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "witness"
    assert {frozenset(pair) for pair in result["observed"]["witnesses"]} == {
        frozenset({"safe_run", "loss_run"})
    }


def test_carrier_transfer_fixture_accepts_declared_transfer_contract() -> None:
    model = load_model_path(FIXTURES / "carrier_transfer_pass.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "transferred"
    assert result["observed"]["source_certified"] is True
    assert result["observed"]["target_certified"] is True
    assert result["observed"]["endpoint_correspondence"] is True
    assert result["observed"]["correspondence_total_on_source_carrier"] is True


def test_carrier_transfer_negative_fixture_rejects_missing_target_return() -> None:
    model = load_model_path(FIXTURES / "carrier_transfer_fail_missing_return.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "not_transferred"
    assert result["observed"]["source_certified"] is True
    assert result["observed"]["target_certified"] is False
    assert result["observed"]["endpoint_correspondence"] is True
    assert result["observed"]["target"]["mutually_reachable"] is False


def test_cli_retains_digest_provenance_audits_and_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "adapter_smoke"
    summary = run_model_file(FIXTURES / "sound_pass.json", out_dir)

    assert summary["all_passed"] is True
    assert summary["audit_count"] == 3
    assert (out_dir / "model_digest.txt").exists()
    assert (out_dir / "provenance_check.json").exists()
    assert (out_dir / "audit_results.json").exists()
    assert (out_dir / "summary.json").exists()


def test_provenance_requires_declaration_before_run() -> None:
    model = load_model(
        {
            "model_id": "missing_provenance_fixture",
            "carrier": ["x"],
            "provenance": {
                "declared_before_run": False,
                "source": "inline test",
                "claim_boundary": "negative provenance test",
            },
        }
    )

    assert validate_provenance(model)["complete"] is False


def test_schema_rejects_relation_elements_outside_declared_domain() -> None:
    with pytest.raises(SchemaError, match="not in domain"):
        load_model(
            {
                "carrier": ["x"],
                "relations": {
                    "bad_edge": [["x", "y"]],
                },
                "provenance": {
                    "declared_before_run": True,
                    "source": "inline test",
                    "claim_boundary": "negative schema test",
                },
            }
        )
