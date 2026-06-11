from __future__ import annotations

import pytest

from omega.baseline_witnesses.compression_score_merge_soundness_family import (
    nuisance_abstraction,
    run_family,
    run_family_case,
    state_space,
)


def test_same_compression_score_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_compression_score_different_merge_soundness"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        expected_fragment_count = 2 ** (nuisance_bit_count + 1)
        expected_class_size = 2**nuisance_bit_count
        expected_unsound_count = 2 ** (2 * nuisance_bit_count - 1)
        expected_same_class_pair_count = 2 * (
            expected_class_size * (expected_class_size - 1) // 2
        )
        expected_allowed_unsound_class_pairs = 2**nuisance_bit_count * (
            (2 ** (nuisance_bit_count - 1)) - 1
        )

        sound_profile = case["sound_profile"]
        unsound_profile = case["unsound_profile"]
        sound_audit = case["sound_audit"]
        unsound_audit = case["unsound_audit"]

        assert case["fragment_count"] == expected_fragment_count
        assert case["compression_scores_match"] is True
        assert sound_profile["fragment_count"] == expected_fragment_count
        assert unsound_profile["fragment_count"] == expected_fragment_count
        assert sound_profile["class_count"] == 2
        assert unsound_profile["class_count"] == 2
        assert sound_profile["assignment_count"] == expected_fragment_count
        assert unsound_profile["assignment_count"] == expected_fragment_count
        assert sound_profile["class_size_signature"] == f"{expected_class_size};{expected_class_size}"
        assert unsound_profile["class_size_signature"] == f"{expected_class_size};{expected_class_size}"
        assert sound_profile["simple_compression_score"] == unsound_profile["simple_compression_score"]
        assert case["sound_abstraction_merge_sound"] is True
        assert case["unsound_abstraction_merge_sound"] is False
        assert sound_audit["unsound_merge_count"] == 0
        assert unsound_audit["unsound_merge_count"] == expected_unsound_count
        assert sound_audit["same_class_pair_count"] == expected_same_class_pair_count
        assert unsound_audit["same_class_pair_count"] == expected_same_class_pair_count
        assert unsound_audit["allowed_same_class_pair_count"] == expected_allowed_unsound_class_pairs
        assert unsound_audit["unsound_pair_signature"]


def test_family_case_checks_every_nuisance_coordinate() -> None:
    checked_ids = {
        run_family_case(nuisance_bit_count=4, nuisance_index=index)["unsound_abstraction_id"]
        for index in range(4)
    }

    assert checked_ids == {
        "classes_by_nuisance_n1",
        "classes_by_nuisance_n2",
        "classes_by_nuisance_n3",
        "classes_by_nuisance_n4",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    fragments = state_space(2)
    with pytest.raises(ValueError, match="nuisance_index out of range"):
        nuisance_abstraction(fragments, nuisance_index=2)

    with pytest.raises(ValueError, match="nuisance_index out of range"):
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
