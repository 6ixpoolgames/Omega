from __future__ import annotations

import pytest

from omega.baseline_witnesses.viability_kernel_declared_recovery_family import (
    run_family,
    run_family_case,
    state_space,
)


def test_same_viability_kernel_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_viability_kernel_different_declared_recovery"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        expected_source_count = 2 ** (nuisance_bit_count + 1)
        expected_kernel_size = 2**nuisance_bit_count
        expected_kernel_signature = ";".join(
            state for state in state_space(nuisance_bit_count) if state[0] == "1"
        )

        declared_profile = case["declared_kernel_profile"]
        nuisance_profile = case["nuisance_kernel_profile"]

        assert case["source_count"] == expected_source_count
        assert case["kernel_signatures_match"] is True
        assert declared_profile["source_count"] == expected_source_count
        assert nuisance_profile["source_count"] == expected_source_count
        assert declared_profile["transition_edge_count"] == expected_source_count
        assert nuisance_profile["transition_edge_count"] == expected_source_count
        assert declared_profile["deterministic_transition"] == 1
        assert nuisance_profile["deterministic_transition"] == 1
        assert declared_profile["viability_kernel_size"] == expected_kernel_size
        assert nuisance_profile["viability_kernel_size"] == expected_kernel_size
        assert declared_profile["viability_kernel_signature"] == expected_kernel_signature
        assert nuisance_profile["viability_kernel_signature"] == expected_kernel_signature
        assert declared_profile["source_to_target_viability_signature"] == (
            declared_profile["source_viability_signature"]
        )
        assert nuisance_profile["source_to_target_viability_signature"] == (
            nuisance_profile["source_viability_signature"]
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
        "kernel_with_nuisance_n1_carried",
        "kernel_with_nuisance_n2_carried",
        "kernel_with_nuisance_n3_carried",
        "kernel_with_nuisance_n4_carried",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    with pytest.raises(ValueError, match="nuisance_index out of range"):
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
