from pathlib import Path

import pytest

from omega.adapters.finite_relational.dynamic_continuation_profiles import (
    DeformationVerdict,
    FiniteControlSystem,
    alternating_refines,
    atom_respect_failures,
    behavior_fingerprint,
    behavior_signature,
    compare_state_capabilities,
    delayed_divergence_witness,
    deformation_fixture,
    deformation_witness,
    duplicate_action_witness,
    duplicate_outcome_systems,
    duplicate_outcome_witness,
    dynamic_continuation_profiles_summary,
    lushness_bridge_witness,
    negative_controls,
    novel_branch_witness,
    presentation_witness,
    quantifier_control_systems,
    quantifier_control_witness,
    switching_adaptive_witness,
    transition_deformation,
)
from omega.adapters.finite_relational.lushness_diversity import OrderVerdict
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_dynamic_continuation_profiles import (
    render_report,
    run_finite_relational_dynamic_continuation_profiles,
)


def test_duplicate_outcome_is_behaviorally_idempotent() -> None:
    witness = duplicate_outcome_witness()

    assert witness["raw_edge_count_changes"] is True
    assert witness["root_types_equal"] is True
    assert witness["profiles_equal"] is True


def test_effect_equivalent_duplicate_action_is_idempotent() -> None:
    witness = duplicate_action_witness()

    assert witness["raw_action_count_changes"] is True
    assert witness["root_types_equal"] is True


def test_novel_branch_strictly_refines_base() -> None:
    witness = novel_branch_witness()

    assert witness["state_verdict"] == OrderVerdict.RIGHT_REFINES.value
    assert witness["profile_verdict"] == OrderVerdict.RIGHT_REFINES.value
    assert witness["extension_strictly_refines"] is True
    assert len(witness["strict_new_capabilities"]) == 1


def test_delayed_divergence_reports_first_separating_horizon() -> None:
    witness = delayed_divergence_witness()

    assert witness["first_separation_depth"] == 2
    assert witness["fingerprints_equal_by_horizon"] == {
        0: True,
        1: True,
        2: False,
        3: False,
        4: False,
    }


def test_action_choice_is_not_flattened_into_environment_outcomes() -> None:
    witness = quantifier_control_witness()

    assert witness["flattened_successors_equal"] is True
    assert witness["nested_types_equal"] is False
    assert witness["choice_strictly_refines_risk"] is True
    assert witness["risk_to_choice_verdict"] == OrderVerdict.RIGHT_REFINES.value


def test_alternating_refinement_selects_action_before_outcome() -> None:
    choice, risk = quantifier_control_systems()

    assert alternating_refines(
        risk,
        "risk",
        choice,
        "choice",
        horizon=1,
    )
    assert not alternating_refines(
        choice,
        "choice",
        risk,
        "risk",
        horizon=1,
    )


def test_positive_atoms_are_compared_by_inclusion() -> None:
    smaller = FiniteControlSystem(
        system_id="smaller_atoms",
        states=("s",),
        actions=(),
        transitions=(),
        atoms=(("s", frozenset({"base"})),),
    )
    larger = FiniteControlSystem(
        system_id="larger_atoms",
        states=("t",),
        actions=(),
        transitions=(),
        atoms=(("t", frozenset({"base", "extra"})),),
    )

    assert (
        compare_state_capabilities(
            smaller,
            "s",
            larger,
            "t",
            horizon=0,
        )
        is OrderVerdict.RIGHT_REFINES
    )


def test_bounded_alternating_refinement_is_a_preorder_on_fixture() -> None:
    system = deformation_fixture()
    states = system.states
    relation = {
        (left, right)
        for left in states
        for right in states
        if alternating_refines(
            system,
            left,
            system,
            right,
            horizon=2,
        )
    }

    assert all((state, state) in relation for state in states)
    assert all(
        (left, right) in relation
        for left in states
        for middle in states
        for right in states
        if (left, middle) in relation and (middle, right) in relation
    )


def test_deformation_fixture_retains_all_four_verdicts() -> None:
    witness = deformation_witness()

    assert witness["all_four_retained"] is True
    assert witness["verdicts"] == {
        "expansion": DeformationVerdict.EXPANSION.value,
        "contraction": DeformationVerdict.CONTRACTION.value,
        "equivalent": DeformationVerdict.EQUIVALENT.value,
        "mixed": DeformationVerdict.MIXED.value,
    }


def test_deformation_requires_an_actual_transition() -> None:
    system = deformation_fixture()

    with pytest.raises(ValueError, match="is not a transition"):
        transition_deformation(
            system,
            "poor_expand",
            "mixed_right",
            basis=(),
            horizon=1,
        )


def test_state_and_action_relabeling_independently_preserve_type_and_profile() -> None:
    witness = presentation_witness()

    assert witness["state_relabeling_preserves_type"] is True
    assert witness["state_relabeling_preserves_profile"] is True
    assert witness["action_relabeling_preserves_type"] is True
    assert witness["action_relabeling_preserves_profile"] is True


def test_atom_respect_failure_rejects_unsound_merge() -> None:
    witness = presentation_witness()

    assert witness["atom_respect_failure_count"] == 1
    assert witness["unsound_merge_changes_bad_type"] is True
    assert witness["unsound_abstraction_rejected"] is True


def test_atom_respect_requires_total_mapping() -> None:
    base, _duplicate = duplicate_outcome_systems()

    with pytest.raises(ValueError, match="must be total"):
        atom_respect_failures(base, base, {"root": "root"})


def test_fingerprints_exclude_state_and_action_identifiers() -> None:
    base, _duplicate = duplicate_outcome_systems()
    relabeled = base.relabel(
        state_mapping={"root": "x", "persistent": "y"},
        action_mapping={"advance": "a", "remain": "b"},
        system_id="renamed",
    )

    assert behavior_signature(base, "root", 3) == behavior_signature(
        relabeled,
        "x",
        3,
    )
    assert behavior_fingerprint(base, "root", 3) == behavior_fingerprint(
        relabeled,
        "x",
        3,
    )


def test_adaptive_lift_strictly_refines_switching_at_horizon_two() -> None:
    witness = switching_adaptive_witness()

    assert witness["status"] == "adaptive-strictly-refines-switching"
    assert witness["first_strict_horizon"] == 2
    assert witness["verdicts_by_horizon"][0] == OrderVerdict.EQUIVALENT.value
    assert witness["verdicts_by_horizon"][1] == OrderVerdict.EQUIVALENT.value
    assert witness["verdicts_by_horizon"][2] == OrderVerdict.RIGHT_REFINES.value
    assert witness["sound_update_truth_preservation_failures"] == 0
    assert witness["information_state_atoms_excluded"] is True


def test_dynamic_profiles_feed_retained_lushness_instrument() -> None:
    witness = lushness_bridge_witness()

    assert witness["duplicate_family_profile_equal"] is True
    assert witness["novel_family_profile_strict"] is True
    assert witness["attributes_are_dynamic_fingerprints"] is True


def test_negative_controls_all_pass() -> None:
    controls = negative_controls()

    assert controls == {
        "state_relabeling_invariant": True,
        "action_relabeling_invariant": True,
        "duplicate_branch_idempotent": True,
        "effect_equivalent_action_idempotent": True,
        "atom_respect_failure_visible": True,
        "flat_union_not_control_type": True,
        "profile_identifiers_exclude_state_action_tokens": True,
        "raw_counts_not_primary": True,
        "negative_controls_pass": True,
    }


def test_system_validation_rejects_unknown_transition_state() -> None:
    with pytest.raises(ValueError, match="unknown state"):
        FiniteControlSystem(
            system_id="invalid",
            states=("s",),
            actions=("a",),
            transitions=(("s", "a", "missing"),),
        )


def test_summary_retains_only_when_cases_and_controls_pass() -> None:
    summary = dynamic_continuation_profiles_summary()

    assert summary["verdict"] == "retained"
    assert all(summary["case_results"].values())
    assert summary["negative_controls"]["negative_controls_pass"] is True
    assert "valuerhood" in summary["not_claimed"]
    assert "thermodynamic law" in summary["not_claimed"]


def test_validation_retains_machine_readable_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_dynamic_continuation_profiles(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "retained"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "case_results.csv").exists()
    assert (run_root / "signatures.csv").exists()
    assert (run_root / "deformations.csv").exists()
    assert (run_root / "report.md").exists()

    case_rows = read_csv(run_root / "case_results.csv")
    assert len(case_rows) == 9
    assert {row["passes"] for row in case_rows} == {"True"}

    deformation_rows = read_csv(run_root / "deformations.csv")
    assert {row["observed"] for row in deformation_rows} == {
        "expansion",
        "contraction",
        "equivalent",
        "mixed",
    }

    report = render_report(result)
    assert "Dynamic Continuation Profiles v0 Report" in report
    assert "Verdict: retained" in report
    assert "First strict adaptive horizon: 2" in report
