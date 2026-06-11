from __future__ import annotations

import pytest

from omega.baseline_witnesses.observation_rank_declared_recovery_family import (
    run_family,
    run_family_case,
    state_space,
)


def test_same_observation_rank_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_observation_rank_different_declared_recovery"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        expected_state_count = 2 ** (nuisance_bit_count + 1)
        expected_block_size_signature = f"{2**nuisance_bit_count};{2**nuisance_bit_count}"
        expected_output_count_signature = f"0:{2**nuisance_bit_count};1:{2**nuisance_bit_count}"

        declared_profile = case["declared_observation_profile"]
        nuisance_profile = case["nuisance_observation_profile"]

        assert case["state_count"] == expected_state_count
        assert case["observation_signatures_match"] is True
        assert declared_profile["state_count"] == expected_state_count
        assert nuisance_profile["state_count"] == expected_state_count
        assert declared_profile["finite_observation_rank"] == 1
        assert nuisance_profile["finite_observation_rank"] == 1
        assert declared_profile["observation_block_count"] == 2
        assert nuisance_profile["observation_block_count"] == 2
        assert declared_profile["observation_block_size_signature"] == expected_block_size_signature
        assert nuisance_profile["observation_block_size_signature"] == expected_block_size_signature
        assert declared_profile["output_to_state_count_signature"] == expected_output_count_signature
        assert nuisance_profile["output_to_state_count_signature"] == expected_output_count_signature
        assert case["declared_observer_exact_declared_recovery"] is True
        assert case["nuisance_observer_exact_declared_recovery"] is False
        assert case["nuisance_observer_ambiguous_outputs"] == "0->{0,1};1->{0,1}"


def test_family_case_checks_every_nuisance_coordinate() -> None:
    checked_ids = {
        run_family_case(nuisance_bit_count=4, nuisance_index=index)["nuisance_observer_id"]
        for index in range(4)
    }

    assert checked_ids == {
        "observe_nuisance_n1",
        "observe_nuisance_n2",
        "observe_nuisance_n3",
        "observe_nuisance_n4",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    with pytest.raises(ValueError, match="nuisance_index out of range"):
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
