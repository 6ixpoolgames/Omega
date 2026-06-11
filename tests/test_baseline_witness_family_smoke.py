from __future__ import annotations

import pytest

from omega.baseline_witnesses.family_smoke import run_family_smoke


def test_baseline_witness_family_smoke_checks_all_families() -> None:
    result = run_family_smoke(max_nuisance_bits=5)

    assert result["status"] == "PASS"
    assert result["family_count"] == 7
    assert result["case_count"] == 85
    assert result["failures"] == []
    assert "Omega validation" in result["not_claimed"]

    families = {family["family_id"]: family for family in result["families"]}
    assert set(families) == {
        "same_reachability_different_declared_recovery_family",
        "same_entropy_different_recovery_profile_family",
        "same_frontier_morphology_different_declared_loss_profile_family",
        "same_mutual_information_different_declared_recovery_family",
        "same_optimized_success_different_declared_recovery_family",
        "same_marginal_success_different_joint_success_family",
        "same_compression_score_different_merge_soundness_family",
    }

    assert families["same_reachability_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_entropy_different_recovery_profile_family"]["case_count"] == 15
    assert families["same_frontier_morphology_different_declared_loss_profile_family"]["case_count"] == 5
    assert families["same_mutual_information_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_optimized_success_different_declared_recovery_family"]["case_count"] == 15
    assert families["same_marginal_success_different_joint_success_family"]["case_count"] == 5
    assert families["same_compression_score_different_merge_soundness_family"]["case_count"] == 15

    for family in families.values():
        assert family["case_count"] == family["expected_case_count"]
        assert family["statuses"] == [family["expected_status"]]


def test_baseline_witness_family_smoke_rejects_degenerate_max() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family_smoke(max_nuisance_bits=0)
