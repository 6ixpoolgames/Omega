from __future__ import annotations

import pytest

from omega.baseline_witnesses.mutual_information_declared_recovery_family import (
    run_family,
    run_family_case,
    state_space,
)


def test_same_mutual_information_witness_generalizes_over_nuisance_bits() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 15
    assert {case["family_case_status"] for case in cases} == {
        "same_mutual_information_different_declared_recovery"
    }

    for case in cases:
        nuisance_bit_count = int(case["nuisance_bit_count"])
        expected_source_count = 2 ** (nuisance_bit_count + 1)
        expected_source_entropy = f"{nuisance_bit_count + 1:.6f}"
        expected_output_weight_signature = f"0:{2**nuisance_bit_count};1:{2**nuisance_bit_count}"

        declared_information = case["declared_information"]
        nuisance_information = case["nuisance_information"]

        assert case["source_count"] == expected_source_count
        assert case["information_signatures_match"] is True
        assert declared_information["source_entropy_bits"] == expected_source_entropy
        assert nuisance_information["source_entropy_bits"] == expected_source_entropy
        assert declared_information["output_weight_signature"] == expected_output_weight_signature
        assert nuisance_information["output_weight_signature"] == expected_output_weight_signature
        assert declared_information["mutual_information_source_output_bits"] == "1.000000"
        assert nuisance_information["mutual_information_source_output_bits"] == "1.000000"
        assert declared_information["deterministic_output_capacity_bits"] == "1.000000"
        assert nuisance_information["deterministic_output_capacity_bits"] == "1.000000"
        assert case["declared_channel_exact_declared_recovery"] is True
        assert case["nuisance_channel_exact_declared_recovery"] is False
        assert case["nuisance_channel_ambiguous_outputs"] == "0->{0,1};1->{0,1}"


def test_family_case_checks_every_nuisance_coordinate() -> None:
    checked_ids = {
        run_family_case(nuisance_bit_count=4, nuisance_index=index)["nuisance_channel_id"]
        for index in range(4)
    }

    assert checked_ids == {
        "transmit_nuisance_n1",
        "transmit_nuisance_n2",
        "transmit_nuisance_n3",
        "transmit_nuisance_n4",
    }


def test_family_rejects_degenerate_or_out_of_range_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="nuisance_bit_count must be >= 1"):
        state_space(0)

    with pytest.raises(ValueError, match="nuisance_index out of range"):
        run_family_case(nuisance_bit_count=2, nuisance_index=2)
