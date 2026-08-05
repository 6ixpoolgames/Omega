from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from omega_v2.experiments.generated_controller_robust_separation_v0 import (
    ACTIONS,
    CANDIDATES,
    FULL_ENVIRONMENTS,
    HORIZON,
    OBSERVATION,
    behavior_class_rows,
    behavior_classes,
    controller_rows,
    enumerate_bounded_controllers,
    environment_scope_rows,
    generated_controller_robust_separation_summary,
    generated_run_rows,
    may_fiber_rows,
    positive_generated_case,
    robust_fiber_rows,
    strict_generated_case,
    strict_environments,
    structural_control_rows,
    terminal_facts,
)
from omega_v2.finite.controllers import (
    FiniteStateController,
    deterministic_controller_rollout,
)
from omega_v2.finite.model import ControlledMarkovSystem
from omega_v2.validation.generated_controller_robust_separation_v0 import (
    retain_generated_controller_robust_separation_v0,
)


def test_controller_class_is_exhaustive_and_behavior_quotient_is_complete() -> None:
    controllers = enumerate_bounded_controllers()
    classes = behavior_classes(controllers)

    assert len(controllers) == 36
    assert len(
        {
            (controller.update_rows, controller.policy_rows)
            for controller in controllers
        }
    ) == 36
    assert set(classes) == {
        (left, right) for left in ACTIONS for right in ACTIONS
    }
    assert sum(len(controller_ids) for controller_ids in classes.values()) == 36


def test_exact_controller_rollout_retains_world_action_observation_and_memory() -> None:
    controller = next(
        item
        for item in enumerate_bounded_controllers()
        if item.controller_id == "controller:u10:axy"
    )
    environment = strict_environments()[0]
    run = deterministic_controller_rollout(
        environment.system,
        controller,
        initial_state=environment.initial_state,
        horizon=environment.horizon,
    )

    assert run.world_path.horizon == HORIZON
    assert run.action_sequence == ("x", "y")
    assert run.observations == (OBSERVATION, OBSERVATION)
    assert run.memory_states == ("m0", "m1", "m0")
    assert terminal_facts(run.world_path.end) == frozenset(CANDIDATES)


def test_controller_rollout_refuses_stochastic_selected_rows() -> None:
    system = ControlledMarkovSystem(
        system_id="stochastic_controller_row",
        states=("start", "left", "right"),
        actions=("x",),
        transitions=(
            ("start", "x", "left", Fraction(1, 2)),
            ("start", "x", "right", Fraction(1, 2)),
            ("left", "x", "left", Fraction(1)),
            ("right", "x", "right", Fraction(1)),
        ),
    )
    controller = FiniteStateController(
        controller_id="stochastic_row_controller",
        memory_states=("m0",),
        initial_memory="m0",
        observation_rows=(
            ("start", "tick"),
            ("left", "tick"),
            ("right", "tick"),
        ),
        update_rows=(("m0", "tick", "m0"),),
        policy_rows=(("m0", "tick", "x"),),
    )

    with pytest.raises(ValueError, match="point-mass"):
        deterministic_controller_rollout(
            system,
            controller,
            initial_state="start",
            horizon=1,
        )


def test_both_strict_environments_individually_admit_the_triple() -> None:
    case = strict_generated_case()

    assert case["may_triple_fiber"].nonempty
    assert case["north_triple_fiber"].nonempty
    assert case["south_triple_fiber"].nonempty
    assert case["north_triple_sequences"] == ["xy"]
    assert case["south_triple_sequences"] == ["yx"]


def test_every_pair_is_robust_over_the_same_full_scope() -> None:
    case = strict_generated_case()

    assert all(fiber.nonempty for fiber in case["pair_fibers"].values())
    assert case["pair_sequences"] == {
        "AB": ["xy", "yx"],
        "AC": ["xz", "zx"],
        "BC": ["yz", "zy"],
    }
    assert {
        fiber.environment_ids for fiber in case["pair_fibers"].values()
    } == {FULL_ENVIRONMENTS}
    assert case["pair_triple_scope_match"]


def test_no_controller_secures_the_strict_triple_across_both_environments() -> None:
    case = strict_generated_case()

    assert case["full_triple_fiber"].nonempty is False
    assert case["full_triple_fiber"].policy_ids == ()
    assert case["full_triple_sequences"] == []
    assert case["may_triple_fiber"].nonempty


def test_singleton_scopes_restore_the_required_ordered_controller() -> None:
    case = strict_generated_case()

    assert case["north_triple_sequences"] == ["xy"]
    assert case["south_triple_sequences"] == ["yx"]
    assert (
        case["full"].environment_antitone_failures(case["north"]) == ()
    )
    assert (
        case["full"].environment_antitone_failures(case["south"]) == ()
    )


def test_matched_positive_restores_full_scope_triple() -> None:
    strict = strict_generated_case()
    positive = positive_generated_case()

    assert positive["triple_fiber"].nonempty
    assert positive["triple_sequences"] == ["xy"]
    assert strict["may_support"] == positive["may_support"]


def test_generated_tables_match_fresh_and_compiled_rollouts() -> None:
    strict = strict_generated_case()
    positive = positive_generated_case()

    assert strict["fresh_rollout_match"]
    assert strict["compiled_rollout_match"]
    assert positive["fresh_rollout_match"]
    assert positive["compiled_rollout_match"]
    assert strict["shared_observation_stream"]
    assert strict["same_action_sequence_across_environments"]


def test_behavior_representatives_preserve_may_and_robust_verdicts() -> None:
    case = strict_generated_case()

    assert len(case["representatives"]) == 9
    assert case["behavior_reduction_may_invariant"]
    assert case["behavior_reduction_robust_invariant"]
    assert case["behavior_reduction_north_robust_invariant"]
    assert case["behavior_reduction_south_robust_invariant"]

    positive = positive_generated_case()
    assert positive["behavior_reduction_may_invariant"]
    assert positive["behavior_reduction_robust_invariant"]


def test_candidate_membership_is_terminal_trajectory_extensional() -> None:
    case = strict_generated_case()

    assert case["candidate_membership_extensional"]
    for run in case["trajectories"].values():
        assert terminal_facts(run.world_path.end) <= set(CANDIDATES)


def test_may_and_robust_structural_laws_remain_green() -> None:
    case = strict_generated_case()

    assert case["may_downward_closure_failures"] == []
    assert case["may_restriction_failures"] == []
    assert case["candidate_antitone_failures"] == []
    assert case["robust_restriction_failures"] == []
    assert case["robust_implies_may_failures"] == []
    assert case["north_environment_antitone_failures"] == []
    assert case["south_environment_antitone_failures"] == []
    assert case["complete_run_evidence"]


def test_summary_retains_every_preregistered_case() -> None:
    summary = generated_controller_robust_separation_summary()

    assert summary["status"] == "retained"
    assert summary["verdict"] == (
        "generated_controller_joint_realizability_does_not_imply_"
        "joint_robust_securability"
    )
    assert all(summary["case_results"].values())
    assert not any(summary["kill_conditions"].values())
    assert "moral compatibility" in summary["claim_boundary"]


def test_artifact_rows_cover_controller_runs_fibers_scopes_and_controls() -> None:
    summary = generated_controller_robust_separation_summary()

    assert len(controller_rows(summary)) == 36
    assert len(behavior_class_rows(summary)) == 9
    assert len(generated_run_rows(summary)) == 144
    assert len(may_fiber_rows(summary)) == 16
    assert len(robust_fiber_rows(summary)) == 32
    assert environment_scope_rows(summary) == [
        {
            "scope": "strict_north",
            "environment_ids": "north",
            "triple_robust": True,
            "triple_sequences": "xy",
        },
        {
            "scope": "strict_south",
            "environment_ids": "south",
            "triple_robust": True,
            "triple_sequences": "yx",
        },
        {
            "scope": "strict_full",
            "environment_ids": "north|south",
            "triple_robust": False,
            "triple_sequences": "",
        },
        {
            "scope": "positive_full",
            "environment_ids": "north|south",
            "triple_robust": True,
            "triple_sequences": "xy",
        },
    ]
    assert all(row["passed"] for row in structural_control_rows(summary))


def test_validation_retains_all_declared_artifacts(tmp_path: Path) -> None:
    result = retain_generated_controller_robust_separation_v0(tmp_path)

    assert result["status"] == "retained"
    assert {path.name for path in tmp_path.iterdir()} == {
        "summary.json",
        "controllers.csv",
        "behavior_classes.csv",
        "generated_runs.csv",
        "may_fibers.csv",
        "robust_fibers.csv",
        "environment_scope.csv",
        "structural_controls.csv",
        "report.md",
    }
