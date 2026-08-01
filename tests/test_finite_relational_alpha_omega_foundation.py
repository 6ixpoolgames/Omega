from fractions import Fraction
from pathlib import Path

import pytest

from omega.adapters.finite_relational.alpha_omega_foundation import (
    DeterministicPolicy,
    FiniteControlledKernel,
    FinitePath,
    PathReversal,
    alpha_omega_foundation_summary,
    cycle_directionality_profile,
    cycle_kernel,
    directionality_fixture_ladder,
    finite_path_law,
    hollow_triangle_assignment,
    omega_fixture_suite,
    path_probability,
    presentation_fixture_suite,
    probabilistic_nonreturn_fixture,
    process_fixture_suite,
    realization_space_from_assignment,
    residual_continuation_law,
    robust_support_viability_kernel,
    support_blindness_fixture,
    support_predecessor,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_alpha_omega_foundation import (
    render_report,
    run_finite_relational_alpha_omega_foundation,
)


def test_controlled_kernel_requires_exact_total_distributions() -> None:
    with pytest.raises(ValueError, match="sum exactly to one"):
        FiniteControlledKernel(
            system_id="bad_sum",
            states=("s",),
            actions=("a",),
            transitions=(("s", "a", "s", Fraction(1, 2)),),
        )

    with pytest.raises(ValueError, match="must be nonempty"):
        FiniteControlledKernel(
            system_id="missing_action_row",
            states=("s",),
            actions=("a", "b"),
            transitions=(("s", "a", "s", Fraction(1)),),
        )


def test_finite_path_law_and_residual_normalize_exactly() -> None:
    kernel = cycle_kernel(
        system_id="path_law_cycle",
        clockwise_weight=Fraction(3, 4),
    )
    policy = DeterministicPolicy(
        policy_id="advance",
        rows=tuple((state, "advance") for state in kernel.states),
    )
    initial = tuple((state, Fraction(1, 3)) for state in kernel.states)
    law = finite_path_law(kernel, policy, initial, horizon=3)

    assert sum(law.values(), Fraction(0)) == 1
    assert all(path.horizon == 3 for path in law)

    prefix = FinitePath(states=("s0", "s1"), actions=("advance",))
    residual = residual_continuation_law(
        kernel,
        policy,
        prefix,
        remaining_horizon=2,
    )
    assert sum(residual.values(), Fraction(0)) == 1
    assert all(path.start == "s1" and path.horizon == 2 for path in residual)


def test_path_probability_rejects_policy_inconsistent_path_by_zero() -> None:
    kernel = cycle_kernel(
        system_id="path_probability_cycle",
        clockwise_weight=Fraction(3, 4),
    )
    policy = DeterministicPolicy(
        policy_id="advance",
        rows=tuple((state, "advance") for state in kernel.states),
    )
    initial = (("s0", Fraction(1)),)
    live = FinitePath(states=("s0", "s1"), actions=("advance",))

    assert path_probability(kernel, policy, initial, live) == Fraction(3, 4)
    assert (
        path_probability(
            kernel,
            policy,
            initial,
            FinitePath(states=("s1",), actions=()),
        )
        == 0
    )


def test_path_reversal_requires_an_involution() -> None:
    with pytest.raises(ValueError, match="involutive"):
        PathReversal(
            convention_id="three_cycle",
            action_rows=(("a", "b"), ("b", "c"), ("c", "a")),
        )


def test_directionally_null_and_biased_reciprocal_cases_separate() -> None:
    ladder = directionality_fixture_ladder(horizon=3)

    assert ladder["reversal_round_trip"] is True
    assert ladder["null"]["reciprocal_support"] is True
    assert ladder["null"]["statistically_directional"] is False
    assert ladder["null"]["total_variation"] == 0.0
    assert ladder["null"]["kl_forward_to_reversed"] == 0.0

    assert ladder["biased_reciprocal"]["reciprocal_support"] is True
    assert ladder["biased_reciprocal"]["statistically_directional"] is True
    assert ladder["biased_reciprocal"]["total_variation"] > 0
    assert ladder["biased_reciprocal"]["kl_forward_to_reversed"] > 0


def test_directionality_scales_with_nonzero_horizon() -> None:
    biased = cycle_kernel(
        system_id="biased_cycle",
        clockwise_weight=Fraction(3, 4),
    )

    assert cycle_directionality_profile(biased, horizon=0).total_variation == 0.0
    assert cycle_directionality_profile(biased, horizon=1).total_variation > 0


def test_probabilistic_nonreturn_is_not_support_impossibility() -> None:
    fixture = probabilistic_nonreturn_fixture()

    assert fixture["return_probability_at_horizon_2"] == "1/10"
    assert fixture["nonreturn_probability_at_horizon_2"] == "9/10"
    assert fixture["support_return_possible"] is True


def test_support_only_operators_are_blind_to_weight_change() -> None:
    fixture = support_blindness_fixture(horizon=3)

    assert fixture["support_equivalent"] is True
    assert fixture["all_support_observables_equal"] is True
    assert fixture["predecessor_failures"] == []
    assert fixture["viability_failures"] == []
    assert fixture["reachability_failures"] == []
    assert fixture["directionality_separates"] is True


def test_support_predecessor_keeps_may_and_same_action_robust_distinct() -> None:
    kernel = FiniteControlledKernel(
        system_id="may_robust_split",
        states=("root", "good", "bad"),
        actions=("risk",),
        transitions=(
            ("root", "risk", "good", Fraction(1, 2)),
            ("root", "risk", "bad", Fraction(1, 2)),
            ("good", "risk", "good", Fraction(1)),
            ("bad", "risk", "bad", Fraction(1)),
        ),
    )

    assert "root" in support_predecessor(kernel, ("good",), robust=False)
    assert "root" not in support_predecessor(kernel, ("good",), robust=True)
    assert robust_support_viability_kernel(kernel, ("good",)) == frozenset({"good"})


def test_presentation_contracts_require_atoms_forward_and_back() -> None:
    fixtures = presentation_fixture_suite(horizon=3)

    assert fixtures["exact_relabeling"]["isomorphism"] is True
    assert fixtures["bisimilar_duplicate"]["functional_bisimulation"] is True

    assert fixtures["forward_failure"]["forward_failure_count"] == 1
    assert fixtures["forward_failure"]["functional_bisimulation"] is False

    assert fixtures["back_failure"]["back_failure_count"] == 1
    assert fixtures["back_failure"]["functional_bisimulation"] is False

    assert fixtures["atom_failure"]["atom_failure_count"] == 1
    assert fixtures["atom_failure"]["functional_bisimulation"] is False


def test_support_bisimulation_does_not_claim_weighted_invariance() -> None:
    witness = presentation_fixture_suite(horizon=3)["weighted_grain_hidden"]

    assert witness["support_bisimulation_passes"] is True
    assert witness["weighted_directionality_changes"] is True
    assert witness["concrete_directionality"]["statistically_directional"] is True
    assert witness["abstract_directionality"]["statistically_directional"] is False


def test_process_profiles_separate_effect_memory_and_labels() -> None:
    fixtures = process_fixture_suite()

    assert fixtures["passive"]["causal_deformer"] is False
    assert fixtures["effectful_memoryless"]["causal_deformer"] is True
    assert (
        fixtures["effectful_memoryless"]["endogenous_record_selector"] is False
    )
    assert fixtures["record_sensitive"]["causal_deformer"] is True
    assert fixtures["record_sensitive"]["endogenous_record_selector"] is True
    assert fixtures["record_sensitive"]["persistent_closed_loop"] is True
    assert fixtures["injected_label_changes_features"] is False
    assert all(
        profile["valuer_declared"] is False
        for profile in (
            fixtures["passive"],
            fixtures["effectful_memoryless"],
            fixtures["record_sensitive"],
            fixtures["injected_label"],
        )
    )


def test_realization_fibers_are_downward_closed_and_compositional() -> None:
    omega = realization_space_from_assignment(
        hollow_triangle_assignment()
    ).quotient_omega()

    assert omega.downward_closure_failures() == ()
    assert omega.restriction_failures() == ()
    assert len(omega.maximal_faces()) == 3


def test_pairwise_realization_does_not_imply_joint_realization() -> None:
    fixture = omega_fixture_suite()

    assert fixture["all_singletons_nonempty"] is True
    assert fixture["all_pairs_nonempty"] is True
    assert fixture["triple_empty"] is True
    assert fixture["maximal_face_count"] == 3
    assert fixture["greatest_face_exists"] is False


def test_exact_duplicate_candidate_does_not_inflate_quotient_omega() -> None:
    fixture = omega_fixture_suite()

    assert fixture["raw_candidate_count"] == 3
    assert fixture["duplicate_raw_candidate_count"] == 4
    assert fixture["candidate_class_count"] == 3
    assert fixture["duplicate_quotient_class_count"] == 3
    assert fixture["duplicate_structural_payload_equal"] is True


def test_summary_retains_only_when_cases_pass_and_kills_stay_false() -> None:
    summary = alpha_omega_foundation_summary(horizon=3)

    assert summary["status"] == "PASS"
    assert summary["verdict"] == "retained"
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert "standing" in summary["not_claimed"]
    assert "lushness as an imperative" in summary["not_claimed"]


def test_validation_retains_machine_readable_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_alpha_omega_foundation(
        out_root=tmp_path,
        horizon=3,
    )

    assert result["status"] == "PASS"
    assert result["verdict"] == "retained"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "case_results.csv").exists()
    assert (run_root / "directionality.csv").exists()
    assert (run_root / "presentations.csv").exists()
    assert (run_root / "process_profiles.csv").exists()
    assert (run_root / "omega_fibers.csv").exists()
    assert (run_root / "report.md").exists()

    case_rows = read_csv(run_root / "case_results.csv")
    assert len(case_rows) == 10
    assert {row["passes"] for row in case_rows} == {"True"}

    process_rows = read_csv(run_root / "process_profiles.csv")
    assert len(process_rows) == 4
    assert {row["valuer_declared"] for row in process_rows} == {"False"}

    report = render_report(result)
    assert "Alpha-Omega Foundation v0 Validation Report" in report
    assert "Verdict: retained" in report
    assert "Triple fiber empty: True" in report
