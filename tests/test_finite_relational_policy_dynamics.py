from fractions import Fraction
from pathlib import Path

import pytest

from omega.adapters.finite_relational import (
    generate_policy_dynamics_study,
    induced_transition_kernel,
    optimized_declared_policy_family_robust_hit,
    policy_hit_probability_within_horizon,
    robust_policy_hit_by_kernel,
    robust_policy_worst_case,
    support_summary_for_policy_kernel,
    validate_action_kernel,
)
from omega.validation.finite_relational_policy_dynamics import (
    run_finite_relational_policy_dynamics,
)


REQUIRED_FAMILY_IDS = {
    "policy_stale_reflected_hit_loss",
    "policy_nonfactorization_same_support_summary",
    "policy_correlated_shock_joint_robustness",
}


def test_policy_dynamics_covers_expected_families_and_separates_hypotheses() -> None:
    families = generate_policy_dynamics_study()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS
    assert all(family.all_hypotheses_passed for family in families)

    stale = by_id["policy_stale_reflected_hit_loss"]
    assert stale.facts["before_hit_probability"] == "9/10"
    assert stale.facts["after_hit_probability"] == "1/10"
    assert stale.facts["loss_amount"] == "4/5"
    assert stale.facts["stale_abstraction_hit_probability"] == "9/10"
    assert stale.facts["reflected_abstraction_hit_probability"] == "1/10"
    closure = stale.facts["hit_status_closure"]
    assert closure["threshold"] == "1/2"
    assert closure["horizon"] == 2
    assert closure["before_hit_status_by_start"] == {
        "x0": "high_hit",
        "x1": "high_hit",
        "goal": "high_hit",
    }
    assert closure["after_hit_status_by_start"] == {
        "x0": "low_hit",
        "x1": "low_hit",
        "goal": "high_hit",
    }
    assert closure["closure_audit_findings"] == ["closure_ok", "closure_ok"]
    assert closure["reflected_common_target_predicates"] == [
        "after_high_hit",
        "all_states",
    ]
    assert closure["stale_reflected_common_target_predicates"] == ["all_states"]
    assert [hypothesis.hypothesis_id for hypothesis in stale.hypotheses] == [
        "stale_hides_policy_loss",
        "reflected_reports_policy_loss",
        "reflected_policy_hit_status_preserves_after_high_hit",
        "stale_reflected_policy_hit_status_drops_after_high_hit",
    ]

    nonfactorization = by_id["policy_nonfactorization_same_support_summary"]
    assert nonfactorization.facts["same_support_summary"] is True
    assert nonfactorization.facts["different_policy_hit_probability"] is True
    assert nonfactorization.facts["high_hit_probability"] == "9/10"
    assert nonfactorization.facts["low_hit_probability"] == "3/5"
    assert nonfactorization.facts["high_support_summary"] == (
        nonfactorization.facts["low_support_summary"]
    )
    assert [hypothesis.hypothesis_id for hypothesis in nonfactorization.hypotheses] == [
        "same_support_summary_not_policy_hit_probability"
    ]

    joint = by_id["policy_correlated_shock_joint_robustness"]
    assert joint.facts["individual_targets_have_robust_policy"] is True
    assert joint.facts["joint_target_has_robust_policy"] is False
    assert joint.facts["optimized_target_a"]["policy_name"] == "protect_a"
    assert joint.facts["optimized_target_a"]["robust_worst_case_hit_probability"] == "1"
    assert joint.facts["optimized_target_b"]["policy_name"] == "protect_b"
    assert joint.facts["optimized_target_b"]["robust_worst_case_hit_probability"] == "1"
    assert joint.facts["optimized_target_joint"]["robust_worst_case_hit_probability"] == "0"
    assert joint.facts["optimized_target_joint"]["per_kernel_hit_probability"] == {
        "correlated_shock": "0",
        "nominal": "1",
    }
    assert [hypothesis.hypothesis_id for hypothesis in joint.hypotheses] == [
        "target_a_has_robust_policy_under_correlated_shock",
        "target_b_has_robust_policy_under_correlated_shock",
        "joint_target_has_no_robust_policy_under_correlated_shock",
        "individual_robust_policy_success_not_joint_robust_policy_success",
    ]

    for family in families:
        for reserved in ("expected", "observed", "passed"):
            assert reserved not in family.facts
        for hypothesis in family.hypotheses:
            assert hypothesis.passed is True


def test_policy_hit_probability_uses_exact_rational_induced_kernel() -> None:
    states = ("x0", "x1", "goal")
    actions = ("move", "wait")
    action_kernel = {
        "x0": {
            "move": {"x0": Fraction(0), "x1": Fraction(1), "goal": Fraction(0)},
            "wait": {"x0": Fraction(1), "x1": Fraction(0), "goal": Fraction(0)},
        },
        "x1": {
            "move": {"x0": Fraction(0), "x1": Fraction(1, 10), "goal": Fraction(9, 10)},
            "wait": {"x0": Fraction(0), "x1": Fraction(1), "goal": Fraction(0)},
        },
        "goal": {
            "move": {"x0": Fraction(0), "x1": Fraction(0), "goal": Fraction(1)},
            "wait": {"x0": Fraction(0), "x1": Fraction(0), "goal": Fraction(1)},
        },
    }
    policy = {"x0": "move", "x1": "move", "goal": "wait"}

    validate_action_kernel(states, actions, action_kernel)
    assert induced_transition_kernel(states, actions, action_kernel, policy)["x1"] == {
        "x0": Fraction(0),
        "x1": Fraction(1, 10),
        "goal": Fraction(9, 10),
    }
    assert policy_hit_probability_within_horizon(
        states,
        actions,
        action_kernel,
        policy,
        "x0",
        frozenset({"goal"}),
        2,
    ) == Fraction(9, 10)


def test_policy_kernel_rejects_extra_declared_surface() -> None:
    states = ("x0", "goal")
    actions = ("move",)
    with_extra_state = {
        "x0": {
            "move": {"x0": Fraction(0), "goal": Fraction(1)},
        },
        "goal": {
            "move": {"x0": Fraction(0), "goal": Fraction(1)},
        },
        "outside": {
            "move": {"x0": Fraction(1), "goal": Fraction(0)},
        },
    }

    with pytest.raises(ValueError, match="undeclared states"):
        validate_action_kernel(states, actions, with_extra_state)

    with_extra_action = {
        "x0": {
            "move": {"x0": Fraction(0), "goal": Fraction(1)},
            "smuggled": {"x0": Fraction(1), "goal": Fraction(0)},
        },
        "goal": {
            "move": {"x0": Fraction(0), "goal": Fraction(1)},
        },
    }

    with pytest.raises(ValueError, match="undeclared actions"):
        validate_action_kernel(states, actions, with_extra_action)

    with_extra_target = {
        "x0": {"move": {"x0": Fraction(0), "goal": Fraction(1), "outside": Fraction(0)}},
        "goal": {"move": {"x0": Fraction(0), "goal": Fraction(1)}},
    }

    with pytest.raises(ValueError, match="undeclared targets"):
        validate_action_kernel(states, actions, with_extra_target)


def test_policy_rejects_extra_policy_state() -> None:
    states = ("x0", "goal")
    actions = ("move",)
    action_kernel = {
        "x0": {"move": {"x0": Fraction(0), "goal": Fraction(1)}},
        "goal": {"move": {"x0": Fraction(0), "goal": Fraction(1)}},
    }

    with pytest.raises(ValueError, match="policy has undeclared states"):
        induced_transition_kernel(
            states,
            actions,
            action_kernel,
            {"x0": "move", "goal": "move", "outside": "move"},
        )


def test_policy_support_summary_can_match_while_hit_probability_differs() -> None:
    states = ("start", "goal", "trap")
    actions = ("try", "wait")
    policy = {"start": "try", "goal": "wait", "trap": "wait"}
    high = {
        "start": {
            "try": {"start": Fraction(0), "goal": Fraction(9, 10), "trap": Fraction(1, 10)},
            "wait": {"start": Fraction(1), "goal": Fraction(0), "trap": Fraction(0)},
        },
        "goal": {
            "try": {"start": Fraction(0), "goal": Fraction(1), "trap": Fraction(0)},
            "wait": {"start": Fraction(0), "goal": Fraction(1), "trap": Fraction(0)},
        },
        "trap": {
            "try": {"start": Fraction(0), "goal": Fraction(0), "trap": Fraction(1)},
            "wait": {"start": Fraction(0), "goal": Fraction(0), "trap": Fraction(1)},
        },
    }
    low = {
        "start": {
            "try": {"start": Fraction(0), "goal": Fraction(3, 5), "trap": Fraction(2, 5)},
            "wait": {"start": Fraction(1), "goal": Fraction(0), "trap": Fraction(0)},
        },
        "goal": high["goal"],
        "trap": high["trap"],
    }
    targets = frozenset({"goal"})

    assert support_summary_for_policy_kernel(
        states,
        actions,
        high,
        policy,
        "start",
        targets,
    ) == support_summary_for_policy_kernel(
        states,
        actions,
        low,
        policy,
        "start",
        targets,
    )
    assert policy_hit_probability_within_horizon(
        states,
        actions,
        high,
        policy,
        "start",
        targets,
        1,
    ) == Fraction(9, 10)
    assert policy_hit_probability_within_horizon(
        states,
        actions,
        low,
        policy,
        "start",
        targets,
        1,
    ) == Fraction(3, 5)


def test_robust_policy_family_optimizes_worst_case_hit_probability() -> None:
    states = ("start", "goal", "partial", "fail")
    actions = ("safe", "risky", "wait")
    policies = {
        "safe": {
            "start": "safe",
            "goal": "wait",
            "partial": "wait",
            "fail": "wait",
        },
        "risky": {
            "start": "risky",
            "goal": "wait",
            "partial": "wait",
            "fail": "wait",
        },
    }
    nominal = {
        "start": {
            "safe": {"start": Fraction(0), "goal": Fraction(1, 2), "partial": Fraction(1, 2), "fail": Fraction(0)},
            "risky": {"start": Fraction(0), "goal": Fraction(1), "partial": Fraction(0), "fail": Fraction(0)},
            "wait": {"start": Fraction(1), "goal": Fraction(0), "partial": Fraction(0), "fail": Fraction(0)},
        },
        "goal": {
            action: {"start": Fraction(0), "goal": Fraction(1), "partial": Fraction(0), "fail": Fraction(0)}
            for action in actions
        },
        "partial": {
            action: {"start": Fraction(0), "goal": Fraction(0), "partial": Fraction(1), "fail": Fraction(0)}
            for action in actions
        },
        "fail": {
            action: {"start": Fraction(0), "goal": Fraction(0), "partial": Fraction(0), "fail": Fraction(1)}
            for action in actions
        },
    }
    shock = {
        "start": {
            "safe": {"start": Fraction(0), "goal": Fraction(1, 2), "partial": Fraction(1, 2), "fail": Fraction(0)},
            "risky": {"start": Fraction(0), "goal": Fraction(0), "partial": Fraction(0), "fail": Fraction(1)},
            "wait": {"start": Fraction(1), "goal": Fraction(0), "partial": Fraction(0), "fail": Fraction(0)},
        },
        "goal": nominal["goal"],
        "partial": nominal["partial"],
        "fail": nominal["fail"],
    }
    kernels = {"nominal": nominal, "shock": shock}
    targets = frozenset({"goal", "partial"})

    risky_hits = robust_policy_hit_by_kernel(
        states,
        actions,
        kernels,
        policies["risky"],
        "start",
        targets,
        1,
    )

    assert risky_hits == {"nominal": Fraction(1), "shock": Fraction(0)}
    assert robust_policy_worst_case(risky_hits) == Fraction(0)

    result = optimized_declared_policy_family_robust_hit(
        states,
        actions,
        kernels,
        policies,
        "start",
        targets,
        1,
    )
    assert result.policy_name == "safe"
    assert result.robust_worst_case_hit_probability == Fraction(1)
    assert result.as_dict()["robust_worst_case_hit_probability"] == "1"


def test_policy_dynamics_validation_retains_fact_and_hypothesis_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_policy_dynamics(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == len(REQUIRED_FAMILY_IDS)
    assert result["all_hypotheses_passed"] is True
    assert (Path(str(result["run_root"])) / "summary.json").exists()
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert family_dir.exists()
        assert (family_dir / "facts.json").exists()
        assert (family_dir / "hypotheses.json").exists()
        assert (family_dir / "family_summary.json").exists()
