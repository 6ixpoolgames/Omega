from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from omega_v2.experiments.directional_asymmetry_capability_v0 import (
    directional_asymmetry_capability_summary,
    matched_record_selector_study,
    passive_asymmetry_case,
    record_selector_case,
    reversible_action_census,
)
from omega_v2.validation.directional_asymmetry_capability_v0 import (
    render_report,
    run_directional_asymmetry_capability_v0,
)


def test_passive_directional_asymmetry_does_not_inject_selection() -> None:
    case = passive_asymmetry_case(horizon=3)

    assert case["directionality"]["comparison"]["total_variation"] == "11/16"
    assert case["directionality"]["comparison"]["support_equal"]
    assert not case["features"]["causal_action_influence"]
    assert not case["features"]["record_sensitive_selection"]
    assert case["features"]["closed_loop_persistence"]


def test_reversal_paired_census_is_exhaustive_and_deterministic() -> None:
    first = reversible_action_census(horizon=3)
    second = reversible_action_census(horizon=3)

    assert first == second
    assert first["permutation_count"] == first["expected_permutation_count"] == 6
    assert first["policy_count"] == first["expected_policy_count"] == 48
    assert len(first["manifest_digest"]) == 64


def test_reversal_paired_primitives_pass_exact_controls() -> None:
    census = reversible_action_census(horizon=3)

    assert census["all_primitive_actions_bijective"]
    assert census["all_reversal_contracts_hold"]
    assert census["all_reverse_pair_distances_zero"]
    assert all(
        row["reverse_pair_total_variation"] == "0"
        for row in census["permutations"]
    )


def test_generated_feedback_can_make_reversible_actions_noninjective() -> None:
    census = reversible_action_census(horizon=3)
    witness = census["first_qualifying_witness"]

    assert census["qualifying_witness_count"] == 12
    assert witness is not None
    assert witness["uses_both_actions"]
    assert witness["actions_have_distinct_effects"]
    assert witness["primitive_actions_bijective"]
    assert witness["closed_loop_image_size"] < 3
    assert not witness["closed_loop_injective"]


def test_balanced_record_selector_has_operational_features_without_bias() -> None:
    case = record_selector_case(
        clockwise_probability=Fraction(1, 2),
        directionality_horizon=3,
    )

    assert case["directionality"]["comparison"]["total_variation"] == "0"
    assert case["selector_profile"]["causal_action_influence"]
    assert case["selector_profile"]["record_sensitive_selection"]
    assert case["selector_profile"]["closed_loop_persistence"]
    assert case["baseline_profile"]["causal_action_influence"]
    assert not case["baseline_profile"]["record_sensitive_selection"]
    assert case["selector_branch_fidelity"] == "1"
    assert case["baseline_branch_fidelity"] == "1/2"
    assert case["branch_fidelity_advantage"] == "1/2"
    assert case["policy_deformation_total_variation"] == "1/2"
    assert case["selector_closed_loop_directionality"]["total_variation"] == "1"
    assert not case["selector_closed_loop_directionality"]["support_equal"]


def test_matched_bias_pair_reconstructs_every_control() -> None:
    study = matched_record_selector_study(horizon=3)

    assert study["all_matched_controls_hold"]
    assert all(study["matched_surface"].values())
    assert study["balanced_directionally_null"]
    assert study["biased_directionally_nonzero"]
    assert (
        study["biased"]["directionality"]["comparison"]["total_variation"]
        == "11/16"
    )


def test_independent_directional_bias_does_not_change_operational_profile() -> None:
    study = matched_record_selector_study(horizon=3)

    assert study["operational_signature_unchanged"]
    assert study["branch_fidelity_unchanged"]
    assert study["policy_deformation_unchanged"]
    assert (
        study["balanced"]["selector_branch_fidelity"]
        == study["biased"]["selector_branch_fidelity"]
        == "1"
    )


def test_preregistered_summary_keeps_hypotheses_separate() -> None:
    summary = directional_asymmetry_capability_summary(horizon=3)

    assert summary["status"] == "retained"
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert summary["hypothesis_verdicts"] == {
        "directional_asymmetry_sufficiency": "rejected",
        "preexisting_substrate_bias_necessity": (
            "rejected_for_declared_operational_features"
        ),
        "process_level_asymmetry_necessity": "unresolved",
        "independent_directional_bias_enabling": (
            "rejected_in_matched_product_control"
        ),
        "coupled_directional_resource_enabling": "unresolved",
    }
    assert "valuerhood" in summary["claim_boundary"]


def test_summary_rejects_nonpositive_horizon() -> None:
    with pytest.raises(ValueError, match="horizon must be positive"):
        directional_asymmetry_capability_summary(horizon=0)


def test_validation_writes_all_preregistered_artifacts(tmp_path: Path) -> None:
    result = run_directional_asymmetry_capability_v0(
        out_root=tmp_path,
        horizon=3,
    )
    run_root = Path(result["run_root"])

    assert result["status"] == "retained"
    assert {path.name for path in run_root.iterdir()} == {
        "summary.json",
        "case_results.csv",
        "passive_asymmetry.csv",
        "reversible_action_census.csv",
        "record_selector_comparison.csv",
        "report.md",
    }
    report = render_report(result)
    assert "Noninjective mixed-policy witnesses: 12" in report
    assert "coupled_directional_resource_enabling: unresolved" in report
