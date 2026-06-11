from __future__ import annotations

import pytest

from omega.baseline_witnesses.optimized_success_declared_recovery_family import (
    coordinate_keyed_channel,
    run_family,
    run_family_case,
    state_space,
)


def test_same_optimized_success_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_optimized_success_different_declared_recovery"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        shifted_coordinate = int(case["shifted_coordinate"])
        states = state_space(nuisance_bit_count)
        expected_source_count = 2 ** (nuisance_bit_count + 1)
        expected_support_count = 2**nuisance_bit_count
        expected_edge_count = expected_source_count * expected_support_count
        expected_target_weight_signature = ";".join(
            f"{state}:{expected_support_count}" for state in states
        )
        expected_support_count_signature = ";".join(
            f"{state}:{expected_support_count}" for state in states
        )
        expected_entropy_signature = ";".join(
            f"{state}:{nuisance_bit_count:.6f}" for state in states
        )

        declared_profile = case["declared_profile"]
        shifted_profile = case["shifted_profile"]

        assert case["source_count"] == expected_source_count
        assert case["support_count"] == expected_support_count
        assert case["baseline_profiles_match"] is True
        assert case["same_optimized_success"] is True
        assert declared_profile["source_count"] == expected_source_count
        assert shifted_profile["source_count"] == expected_source_count
        assert declared_profile["edge_count"] == expected_edge_count
        assert shifted_profile["edge_count"] == expected_edge_count
        assert declared_profile["global_target_support_size"] == expected_source_count
        assert shifted_profile["global_target_support_size"] == expected_source_count
        assert declared_profile["target_weight_signature"] == expected_target_weight_signature
        assert shifted_profile["target_weight_signature"] == expected_target_weight_signature
        assert (
            declared_profile["per_source_reachable_count_signature"]
            == expected_support_count_signature
        )
        assert (
            shifted_profile["per_source_reachable_count_signature"]
            == expected_support_count_signature
        )
        assert declared_profile["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert shifted_profile["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert case["declared_channel_exact_declared_recovery"] is True
        assert case["shifted_channel_exact_declared_recovery"] is False
        assert case["declared_channel_exact_optimized_recovery"] is True
        assert case["shifted_channel_exact_optimized_recovery"] is True
        assert case["declared_channel_best_observation_id"] == "O_0"
        assert case["shifted_channel_best_observation_id"] == f"O_{shifted_coordinate}"
        assert case["shifted_channel_declared_ambiguous_observations"] == "0->{0,1};1->{0,1}"


def test_family_case_checks_every_shifted_coordinate() -> None:
    checked_ids = {
        run_family_case(nuisance_bit_count=4, shifted_coordinate=coordinate)["shifted_channel_id"]
        for coordinate in range(1, 5)
    }

    assert checked_ids == {
        "d_in_target_coordinate_1",
        "d_in_target_coordinate_2",
        "d_in_target_coordinate_3",
        "d_in_target_coordinate_4",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    states = state_space(2)
    with pytest.raises(ValueError, match="coordinate out of range"):
        coordinate_keyed_channel(states, coordinate=3)

    with pytest.raises(ValueError, match="coordinate out of range"):
        run_family_case(nuisance_bit_count=2, shifted_coordinate=3)
