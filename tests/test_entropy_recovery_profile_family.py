from __future__ import annotations

import pytest

from omega.baseline_witnesses.entropy_recovery_profile_family import (
    coordinate_keyed_channel,
    run_family,
    run_family_case,
    state_space,
)


def test_same_entropy_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_entropy_different_recovery_profile"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        control_coordinate = int(case["nuisance_index"]) + 1
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
        failed_for_declared = ";".join(f"D_{index}" for index in range(1, nuisance_bit_count + 1))
        failed_for_control = ";".join(
            f"D_{index}"
            for index in range(0, nuisance_bit_count + 1)
            if index != control_coordinate
        )

        declared_entropy = case["declared_entropy"]
        control_entropy = case["control_entropy"]
        declared_recovery = case["declared_recovery"]
        control_recovery = case["control_recovery"]

        assert case["source_count"] == expected_source_count
        assert case["support_count"] == expected_support_count
        assert case["entropy_signatures_match"] is True
        assert case["recovery_profile_differs"] is True
        assert declared_entropy["source_count"] == expected_source_count
        assert control_entropy["source_count"] == expected_source_count
        assert declared_entropy["edge_count"] == expected_edge_count
        assert control_entropy["edge_count"] == expected_edge_count
        assert declared_entropy["global_target_support_size"] == expected_source_count
        assert control_entropy["global_target_support_size"] == expected_source_count
        assert declared_entropy["global_target_weight_signature"] == expected_target_weight_signature
        assert control_entropy["global_target_weight_signature"] == expected_target_weight_signature
        assert declared_entropy["global_target_entropy_bits"] == f"{nuisance_bit_count + 1:.6f}"
        assert control_entropy["global_target_entropy_bits"] == f"{nuisance_bit_count + 1:.6f}"
        assert (
            declared_entropy["per_source_support_count_signature"]
            == expected_support_count_signature
        )
        assert control_entropy["per_source_support_count_signature"] == expected_support_count_signature
        assert declared_entropy["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert control_entropy["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert declared_recovery["recovered_distinctions"] == "D_0"
        assert declared_recovery["failed_distinctions"] == failed_for_declared
        assert control_recovery["recovered_distinctions"] == f"D_{control_coordinate}"
        assert control_recovery["failed_distinctions"] == failed_for_control
        assert declared_recovery["recovered_distinction_count"] == 1
        assert control_recovery["recovered_distinction_count"] == 1


def test_family_case_checks_every_nuisance_coordinate() -> None:
    checked_ids = {
        run_family_case(nuisance_bit_count=4, nuisance_index=index)["control_channel_id"]
        for index in range(4)
    }

    assert checked_ids == {
        "preserve_D_1",
        "preserve_D_2",
        "preserve_D_3",
        "preserve_D_4",
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
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
