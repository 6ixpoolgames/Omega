from __future__ import annotations

import pytest

from omega.baseline_witnesses.coarse_bisimulation_consequence_profile_family import (
    profile_signature,
    run_family,
    run_family_case,
    state_space,
)


def test_same_coarse_bisimulation_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_coarse_bisimulation_different_consequence_profile"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        state_count = 2 ** (nuisance_bit_count + 1)
        expected_pair_count = state_count * (state_count - 1) // 2
        expected_allowed_pair_count = 2 * (
            (state_count // 2) * ((state_count // 2) - 1) // 2
        )
        expected_blocked_pair_count = expected_pair_count - expected_allowed_pair_count

        declared_profile = case["declared_profile"]
        nuisance_profile = case["nuisance_profile"]

        assert case["state_count"] == state_count
        assert case["transition_edge_count"] == state_count
        assert case["baseline_controls_match"] is True
        assert case["profile_counts_match"] is True
        assert case["profile_signatures_differ"] is True
        assert declared_profile["pair_count"] == expected_pair_count
        assert nuisance_profile["pair_count"] == expected_pair_count
        assert declared_profile["allowed_pair_count"] == expected_allowed_pair_count
        assert nuisance_profile["allowed_pair_count"] == expected_allowed_pair_count
        assert declared_profile["blocked_pair_count"] == expected_blocked_pair_count
        assert nuisance_profile["blocked_pair_count"] == expected_blocked_pair_count
        assert declared_profile["allowed_pair_signature"] != nuisance_profile["allowed_pair_signature"]
        assert declared_profile["blocked_pair_signature"] != nuisance_profile["blocked_pair_signature"]


def test_family_case_checks_every_nuisance_coordinate() -> None:
    checked_panels = {
        run_family_case(nuisance_bit_count=4, nuisance_index=index)["nuisance_panel_id"]
        for index in range(4)
    }

    assert checked_panels == {
        "declared_n1_expanded_panel",
        "declared_n2_expanded_panel",
        "declared_n3_expanded_panel",
        "declared_n4_expanded_panel",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    states = state_space(2)
    with pytest.raises(ValueError, match="coordinate out of range"):
        profile_signature(states, coordinate=3)

    with pytest.raises(ValueError, match="coordinate out of range"):
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
