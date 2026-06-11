from __future__ import annotations

import pytest

from omega.baseline_witnesses.control_reach_declared_recovery_family import (
    run_family,
    run_family_case,
    state_space,
)


def test_same_control_reach_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_control_reach_different_declared_recovery"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        states = state_space(nuisance_bit_count)
        expected_source_count = 2 ** (nuisance_bit_count + 1)
        expected_per_source_signature = ";".join(f"{state}:2" for state in states)

        declared_profile = case["declared_control_reach_profile"]
        nuisance_profile = case["nuisance_control_reach_profile"]

        assert case["source_count"] == expected_source_count
        assert case["control_reach_signatures_match"] is True
        assert declared_profile["source_count"] == expected_source_count
        assert nuisance_profile["source_count"] == expected_source_count
        assert declared_profile["control_count"] == 2
        assert nuisance_profile["control_count"] == 2
        assert declared_profile["transition_edge_count"] == expected_source_count * 2
        assert nuisance_profile["transition_edge_count"] == expected_source_count * 2
        assert declared_profile["deterministic_transition"] == 1
        assert nuisance_profile["deterministic_transition"] == 1
        assert declared_profile["global_target_support"] == "00;01;10;11"
        assert nuisance_profile["global_target_support"] == "00;01;10;11"
        assert declared_profile["per_source_reachable_target_count_signature"] == (
            expected_per_source_signature
        )
        assert nuisance_profile["per_source_reachable_target_count_signature"] == (
            expected_per_source_signature
        )
        assert declared_profile["target_count_by_control_signature"] == (
            "drive_0:2;drive_1:2"
        )
        assert nuisance_profile["target_count_by_control_signature"] == (
            "drive_0:2;drive_1:2"
        )
        assert declared_profile["target_control_bits_by_control_signature"] == (
            "drive_0:0;drive_1:1"
        )
        assert nuisance_profile["target_control_bits_by_control_signature"] == (
            "drive_0:0;drive_1:1"
        )
        assert case["declared_system_exact_declared_recovery"] is True
        assert case["nuisance_system_exact_declared_recovery"] is False
        assert case["nuisance_system_ambiguous_observations"] == "0->{0,1};1->{0,1}"


def test_family_case_checks_every_nuisance_coordinate() -> None:
    checked_ids = {
        run_family_case(nuisance_bit_count=4, nuisance_index=index)["nuisance_system_id"]
        for index in range(4)
    }

    assert checked_ids == {
        "control_with_nuisance_n1_carried",
        "control_with_nuisance_n2_carried",
        "control_with_nuisance_n3_carried",
        "control_with_nuisance_n4_carried",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    with pytest.raises(ValueError, match="nuisance_index out of range"):
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
