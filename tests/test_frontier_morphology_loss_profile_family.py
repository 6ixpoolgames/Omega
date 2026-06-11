from __future__ import annotations

import pytest

from omega.baseline_witnesses.frontier_morphology_loss_profile_family import (
    run_family,
    run_family_case,
    state_space,
)


def test_same_frontier_morphology_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 5
    assert {case["family_case_status"] for case in cases} == {
        "same_frontier_morphology_different_declared_loss_profile"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        states = state_space(nuisance_bit_count)
        viable_states = tuple(state for state in states if state[0] == "1")
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
        expected_viable_multiset = ";".join(
            ["0"] * expected_support_count + [str(expected_support_count)] * expected_support_count
        )
        expected_preserve_loss_signature = ";".join(f"{state}:0" for state in viable_states)
        expected_flip_loss_signature = ";".join(f"{state}:1" for state in viable_states)

        preserve_morphology = case["preserve_morphology"]
        flip_morphology = case["flip_morphology"]
        preserve_loss = case["preserve_loss"]
        flip_loss = case["flip_loss"]

        assert case["source_count"] == expected_source_count
        assert case["support_count"] == expected_support_count
        assert case["morphology_signatures_match"] is True
        assert case["loss_profile_differs"] is True
        assert preserve_morphology["source_count"] == expected_source_count
        assert flip_morphology["source_count"] == expected_source_count
        assert preserve_morphology["edge_count"] == expected_edge_count
        assert flip_morphology["edge_count"] == expected_edge_count
        assert preserve_morphology["global_target_support_size"] == expected_source_count
        assert flip_morphology["global_target_support_size"] == expected_source_count
        assert preserve_morphology["global_target_weight_signature"] == expected_target_weight_signature
        assert flip_morphology["global_target_weight_signature"] == expected_target_weight_signature
        assert preserve_morphology["global_target_entropy_bits"] == f"{nuisance_bit_count + 1:.6f}"
        assert flip_morphology["global_target_entropy_bits"] == f"{nuisance_bit_count + 1:.6f}"
        assert (
            preserve_morphology["per_source_support_count_signature"]
            == expected_support_count_signature
        )
        assert (
            flip_morphology["per_source_support_count_signature"]
            == expected_support_count_signature
        )
        assert preserve_morphology["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert flip_morphology["per_source_entropy_bits_signature"] == expected_entropy_signature
        assert preserve_morphology["viable_target_count_multiset"] == expected_viable_multiset
        assert flip_morphology["viable_target_count_multiset"] == expected_viable_multiset
        assert preserve_loss["viable_source_count"] == expected_support_count
        assert flip_loss["viable_source_count"] == expected_support_count
        assert preserve_loss["loss_count"] == 0
        assert flip_loss["loss_count"] == expected_support_count
        assert preserve_loss["loss_signature"] == expected_preserve_loss_signature
        assert flip_loss["loss_signature"] == expected_flip_loss_signature


def test_family_case_scales_viable_loss_count() -> None:
    small = run_family_case(nuisance_bit_count=1)
    large = run_family_case(nuisance_bit_count=5)

    assert small["preserve_loss"]["loss_count"] == 0
    assert small["flip_loss"]["loss_count"] == 2
    assert large["preserve_loss"]["loss_count"] == 0
    assert large["flip_loss"]["loss_count"] == 32


def test_family_rejects_degenerate_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)
