from __future__ import annotations

import pytest

from omega.baseline_witnesses.marginal_success_joint_success_family import (
    run_family,
    run_family_case,
    state_space,
)


def test_same_marginal_success_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 5
    assert {case["family_case_status"] for case in cases} == {
        "same_marginal_success_different_joint_success"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        states = state_space(nuisance_bit_count)
        expected_source_count = 2 ** (nuisance_bit_count + 2)
        expected_edge_count = expected_source_count * 4
        expected_support_count_signature = ";".join(f"{state}:4" for state in states)
        expected_weight_total_signature = ";".join(f"{state}:4" for state in states)
        expected_entropy_signature = ";".join(f"{state}:2.000000" for state in states)
        expected_total_weight = 2 ** (nuisance_bit_count + 4)

        correlated_baseline = case["correlated_baseline"]
        independent_baseline = case["independent_baseline"]
        correlated_recovery = case["correlated_recovery"]
        independent_recovery = case["independent_recovery"]

        assert case["source_count"] == expected_source_count
        assert case["baseline_signatures_match"] is True
        assert case["same_marginal_success"] is True
        assert case["different_joint_success"] is True
        assert correlated_baseline["source_count"] == expected_source_count
        assert independent_baseline["source_count"] == expected_source_count
        assert correlated_baseline["edge_count"] == expected_edge_count
        assert independent_baseline["edge_count"] == expected_edge_count
        assert (
            correlated_baseline["per_source_support_count_signature"]
            == expected_support_count_signature
        )
        assert (
            independent_baseline["per_source_support_count_signature"]
            == expected_support_count_signature
        )
        assert (
            correlated_baseline["per_source_weight_total_signature"]
            == expected_weight_total_signature
        )
        assert (
            independent_baseline["per_source_weight_total_signature"]
            == expected_weight_total_signature
        )
        assert correlated_baseline["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert independent_baseline["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert correlated_recovery["marginal_success_vector"] == "D_A:3/4;D_B:3/4"
        assert independent_recovery["marginal_success_vector"] == "D_A:3/4;D_B:3/4"
        assert correlated_recovery["D_AB_bayes_success_fraction"] == "5/8"
        assert independent_recovery["D_AB_bayes_success_fraction"] == "9/16"
        assert correlated_recovery["total_weight"] == expected_total_weight
        assert independent_recovery["total_weight"] == expected_total_weight


def test_family_case_scales_success_weights_with_nuisance_count() -> None:
    small = run_family_case(nuisance_bit_count=1)
    large = run_family_case(nuisance_bit_count=4)

    assert small["correlated_recovery"]["D_AB_success_weight"] == 20
    assert small["independent_recovery"]["D_AB_success_weight"] == 18
    assert large["correlated_recovery"]["D_AB_success_weight"] == 160
    assert large["independent_recovery"]["D_AB_success_weight"] == 144


def test_family_rejects_degenerate_or_invalid_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 0"):
        state_space(-1)
