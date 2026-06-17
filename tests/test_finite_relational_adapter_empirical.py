from pathlib import Path

from omega.adapters.finite_relational import generate_controlled_experiment
from omega.validation.finite_relational_adapter_empirical import (
    run_finite_relational_adapter_empirical,
)


REQUIRED_FAMILY_IDS = {
    "bounded_recovery_same_histogram",
    "ordered_trace_same_bag",
    "hidden_reachability_loss_under_stale_abstraction",
    "endpoint_forward_reach_not_carrier_certificate",
}


def test_controlled_experiment_covers_expected_small_families() -> None:
    families = generate_controlled_experiment()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS
    assert all(family.all_passed for family in families)
    assert by_id["bounded_recovery_same_histogram"].metrics["recoverable_fraction"] == "4/16"
    assert (
        by_id["bounded_recovery_same_histogram"]
        .metrics["same_histogram_controls_recoverability"]
        is False
    )
    assert (
        by_id["ordered_trace_same_bag"].metrics["same_bag_target_change_pair_count"]
        > 0
    )
    assert (
        by_id["hidden_reachability_loss_under_stale_abstraction"]
        .metrics["hidden_loss_pair_count"]
        > 0
    )
    assert (
        by_id["endpoint_forward_reach_not_carrier_certificate"]
        .metrics["forward_reach_but_uncertified_count"]
        > 0
    )


def test_controlled_experiment_representatives_use_generic_audits() -> None:
    families = generate_controlled_experiment()
    findings = {
        case.case_id: [result.finding for result in case.audit_results]
        for family in families
        for case in family.representative_cases
    }

    assert findings["bounded_recovery_histogram_pass"] == ["recoverable"]
    assert findings["bounded_recovery_histogram_fail"] == ["not_recoverable"]
    assert findings["ordered_trace_same_bag_witness"] == ["witness"]
    assert findings["hidden_reachability_loss_representative"] == ["hidden_loss"]
    assert findings["endpoint_forward_reach_uncertified_representative"] == [
        "not_certified"
    ]


def test_controlled_empirical_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_adapter_empirical(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == len(REQUIRED_FAMILY_IDS)
    assert result["representative_case_count"] == 5
    assert result["all_passed"] is True
    assert (Path(str(result["run_root"])) / "summary.json").exists()
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert family_dir.exists()
        assert (family_dir / "family_summary.json").exists()
        for case in family["representative_cases"]:
            out_dir = Path(str(case["output"]))
            assert (out_dir / "model.json").exists()
            assert (out_dir / "model_digest.txt").exists()
            assert (out_dir / "audit_results.json").exists()
            assert (out_dir / "summary.json").exists()
