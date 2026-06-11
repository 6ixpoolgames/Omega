from __future__ import annotations

import pytest

from omega.baseline_witnesses.reachability_declared_recovery_family import (
    run_family,
    run_family_case,
    state_space,
)


def test_same_reachability_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_reachability_different_declared_recovery"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
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

        preserve_profile = case["preserve_profile"]
        control_profile = case["control_profile"]

        assert case["source_count"] == expected_source_count
        assert case["support_count"] == expected_support_count
        assert case["reachability_profiles_match"] is True
        assert preserve_profile["source_count"] == expected_source_count
        assert control_profile["source_count"] == expected_source_count
        assert preserve_profile["edge_count"] == expected_edge_count
        assert control_profile["edge_count"] == expected_edge_count
        assert preserve_profile["global_target_support_size"] == expected_source_count
        assert control_profile["global_target_support_size"] == expected_source_count
        assert preserve_profile["target_weight_signature"] == expected_target_weight_signature
        assert control_profile["target_weight_signature"] == expected_target_weight_signature
        assert (
            preserve_profile["per_source_reachable_count_signature"]
            == expected_support_count_signature
        )
        assert (
            control_profile["per_source_reachable_count_signature"]
            == expected_support_count_signature
        )
        assert preserve_profile["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert control_profile["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert preserve_profile["min_per_source_entropy_bits"] == f"{nuisance_bit_count:.6f}"
        assert control_profile["min_per_source_entropy_bits"] == f"{nuisance_bit_count:.6f}"
        assert preserve_profile["max_per_source_entropy_bits"] == f"{nuisance_bit_count:.6f}"
        assert control_profile["max_per_source_entropy_bits"] == f"{nuisance_bit_count:.6f}"
        assert case["preserve_channel_exact_declared_recovery"] is True
        assert case["control_channel_exact_declared_recovery"] is False
        assert case["control_channel_ambiguous_observations"] == "0->{0,1};1->{0,1}"


def test_family_case_checks_every_nuisance_coordinate() -> None:
    checked_ids = {
        run_family_case(nuisance_bit_count=4, nuisance_index=index)["control_channel_id"]
        for index in range(4)
    }

    assert checked_ids == {
        "keyed_by_nuisance_n1",
        "keyed_by_nuisance_n2",
        "keyed_by_nuisance_n3",
        "keyed_by_nuisance_n4",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    with pytest.raises(ValueError, match="nuisance_index out of range"):
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
