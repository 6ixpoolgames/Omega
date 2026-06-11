from __future__ import annotations

import pytest

from omega.baseline_witnesses.chain_evidence_class_soundness_family import (
    baseline_class_profile,
    class_members,
    run_family,
    run_family_case,
)


def test_same_chain_evidence_witness_generalizes_over_class_sizes() -> None:
    cases = run_family(max_nuisance_bits=5)

    assert len(cases) == 5
    assert {case["family_case_status"] for case in cases} == {
        "same_chain_evidence_different_class_soundness"
    }

    for case in cases:
        chain_intermediate_count = int(case["chain_intermediate_count"])
        member_count = chain_intermediate_count + 2
        expected_internal_pairs = member_count * (member_count - 1) // 2
        expected_chain_edges = member_count - 1
        expected_invalid_blocked_pairs = expected_internal_pairs - expected_chain_edges

        baseline_profile = case["baseline_profile"]
        valid_audit = case["valid_audit"]
        invalid_audit = case["invalid_audit"]

        assert case["member_count"] == member_count
        assert case["baseline_controls_match"] is True
        assert baseline_profile["member_count"] == member_count
        assert baseline_profile["declared_chain_edge_count"] == expected_chain_edges
        assert baseline_profile["internal_pair_count"] == expected_internal_pairs
        assert baseline_profile["chain_connected"] is True
        assert case["valid_declared_chain_edges_pass"] is True
        assert case["invalid_declared_chain_edges_pass"] is True
        assert case["valid_class_sound"] is True
        assert case["invalid_class_sound"] is False
        assert valid_audit["internal_pair_count"] == expected_internal_pairs
        assert valid_audit["allowed_pair_count"] == expected_internal_pairs
        assert valid_audit["blocked_pair_count"] == 0
        assert valid_audit["blocked_pair_signature"] == ""
        assert invalid_audit["internal_pair_count"] == expected_internal_pairs
        assert invalid_audit["allowed_pair_count"] == expected_chain_edges
        assert invalid_audit["blocked_pair_count"] == expected_invalid_blocked_pairs
        assert invalid_audit["blocked_pair_signature"]


def test_family_case_scales_blocked_non_adjacent_pairs() -> None:
    case = run_family_case(chain_intermediate_count=3)

    assert case["member_count"] == 5
    assert case["valid_class_id"] == "valid_clique_size_5"
    assert case["invalid_class_id"] == "invalid_chain_size_5"
    assert case["invalid_audit"]["allowed_pair_count"] == 4
    assert case["invalid_audit"]["blocked_pair_count"] == 6
    assert case["invalid_audit"]["blocked_pair_signature"] == (
        "i0,i2;i0,i3;i0,i4;i1,i3;i1,i4;i2,i4"
    )


def test_family_rejects_degenerate_requests() -> None:
    with pytest.raises(ValueError, match="max_nuisance_bits must be >= 1"):
        run_family(max_nuisance_bits=0)

    with pytest.raises(ValueError, match="chain_intermediate_count must be >= 1"):
        run_family_case(chain_intermediate_count=0)

    with pytest.raises(ValueError, match="member_count must be >= 3"):
        class_members("x", 2)

    with pytest.raises(ValueError, match="member_count must be >= 3"):
        baseline_class_profile(2)
