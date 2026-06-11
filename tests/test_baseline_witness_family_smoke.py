from __future__ import annotations

import pytest

import omega.baseline_witnesses.family_smoke as family_smoke


def test_baseline_witness_family_smoke_checks_all_families() -> None:
    result = family_smoke.run_family_smoke(max_nuisance_bits=5)

    assert result["status"] == "PASS"
    assert result["family_count"] == 12
    assert result["case_count"] == 150
    assert result["failures"] == []
    assert "Omega validation" in result["not_claimed"]

    families = {family["family_id"]: family for family in result["families"]}
    assert set(families) == {
        "same_reachability_different_declared_recovery_family",
        "same_entropy_different_recovery_profile_family",
        "same_frontier_morphology_different_declared_loss_profile_family",
        "same_intervention_effect_different_declared_recovery_family",
        "same_mutual_information_different_declared_recovery_family",
        "same_optimized_success_different_declared_recovery_family",
        "same_marginal_success_different_joint_success_family",
        "same_compression_score_different_merge_soundness_family",
        "same_chain_evidence_different_class_soundness_family",
        "same_coarse_bisimulation_different_consequence_profile_family",
        "same_observation_rank_different_declared_recovery_family",
        "same_viability_kernel_different_declared_recovery_family",
    }

    assert families["same_reachability_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_entropy_different_recovery_profile_family"]["case_count"] == 15
    assert families["same_frontier_morphology_different_declared_loss_profile_family"]["case_count"] == 5
    assert families["same_intervention_effect_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_mutual_information_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_optimized_success_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_viability_kernel_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_marginal_success_different_joint_success_family"]["case_count"] == 5
    assert families["same_observation_rank_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_compression_score_different_merge_soundness_family"]["case_count"] == 15
    assert families["same_chain_evidence_different_class_soundness_family"]["case_count"] == 5
    assert families["same_coarse_bisimulation_different_consequence_profile_family"]["case_count"] == 15

    for family in families.values():
        assert family["case_count"] == family["expected_case_count"]
        assert family["statuses"] == [family["expected_status"]]


def test_baseline_witness_family_smoke_rejects_degenerate_max() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        family_smoke.run_family_smoke(max_nuisance_bits=0)


def test_baseline_witness_family_smoke_reports_case_count_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        family_smoke,
        "FAMILY_SPECS",
        (
            {
                "family_id": "mutated_count_family",
                "runner": lambda *, max_nuisance_bits: [
                    {"family_case_status": "expected_status"}
                ],
                "expected_status": "expected_status",
                "expected_case_count_at_max": lambda max_bits: 2,
            },
        ),
    )

    result = family_smoke.run_family_smoke(max_nuisance_bits=1)

    assert result["status"] == "FAIL"
    assert result["case_count"] == 1
    assert result["failures"] == [
        {
            "family_id": "mutated_count_family",
            "failure": "case_count_mismatch",
            "expected": 2,
            "actual": 1,
        }
    ]


def test_baseline_witness_family_smoke_reports_unexpected_case_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        family_smoke,
        "FAMILY_SPECS",
        (
            {
                "family_id": "mutated_status_family",
                "runner": lambda *, max_nuisance_bits: [
                    {"family_case_status": "unexpected_status"}
                ],
                "expected_status": "expected_status",
                "expected_case_count_at_max": lambda max_bits: 1,
            },
        ),
    )

    result = family_smoke.run_family_smoke(max_nuisance_bits=1)

    assert result["status"] == "FAIL"
    assert result["case_count"] == 1
    assert result["failures"] == [
        {
            "family_id": "mutated_status_family",
            "failure": "unexpected_family_case_status",
            "expected": "expected_status",
            "actual_statuses": ["unexpected_status"],
        }
    ]
