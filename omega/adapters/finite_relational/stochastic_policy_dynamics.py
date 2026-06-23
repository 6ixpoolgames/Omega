"""Policy-conditioned finite stochastic dynamics audits.

This is the first small layer with actions and deterministic policies. It is
still exact finite arithmetic, not full MDP policy validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from omega.adapters.finite_relational.audits import run_declared_audits
from omega.adapters.finite_relational.model import load_model, model_digest
from omega.adapters.finite_relational.stochastic_continuation_loss import (
    TransitionKernel,
    hit_probability_within_horizon,
    validate_transition_kernel,
)
from omega.adapters.finite_relational.stochastic_recovery import fraction_to_text


ActionKernel = dict[str, dict[str, dict[str, Fraction]]]
Policy = dict[str, str]


@dataclass(frozen=True)
class HypothesisCheck:
    """A hypothesis evaluated after generated finite facts are computed."""

    hypothesis_id: str
    statement: str
    expected: bool
    observed: bool

    @property
    def passed(self) -> bool:
        return self.expected == self.observed

    def as_dict(self) -> dict[str, object]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "expected": self.expected,
            "observed": self.observed,
            "passed": self.passed,
        }


@dataclass(frozen=True)
class PolicyDynamicsFamily:
    """One exact finite policy-conditioned dynamics family."""

    family_id: str
    description: str
    facts: dict[str, object]
    hypotheses: tuple[HypothesisCheck, ...]

    @property
    def all_hypotheses_passed(self) -> bool:
        return all(hypothesis.passed for hypothesis in self.hypotheses)

    def summary(self) -> dict[str, object]:
        return {
            "family_id": self.family_id,
            "description": self.description,
            "fact_count": len(self.facts),
            "hypothesis_count": len(self.hypotheses),
            "all_hypotheses_passed": self.all_hypotheses_passed,
        }


def generate_policy_dynamics_study() -> tuple[PolicyDynamicsFamily, ...]:
    """Generate the first policy-conditioned stochastic dynamics cases."""

    return (
        _policy_stale_reflected_hit_loss_family(),
        _policy_nonfactorization_same_support_summary_family(),
    )


def policy_dynamics_summary() -> dict[str, object]:
    families = generate_policy_dynamics_study()
    return {
        "status": "PASS",
        "family_count": len(families),
        "all_hypotheses_passed": all(family.all_hypotheses_passed for family in families),
        "families": [_family_as_dict(family) for family in families],
    }


def validate_action_kernel(
    states: tuple[str, ...],
    actions: tuple[str, ...],
    action_kernel: ActionKernel,
) -> None:
    """Require total finite rational transitions for every state/action pair."""

    missing_states = sorted(set(states) - set(action_kernel))
    if missing_states:
        raise ValueError(f"action kernel is missing states: {missing_states}")
    extra_states = sorted(set(action_kernel) - set(states))
    if extra_states:
        raise ValueError(f"action kernel has undeclared states: {extra_states}")
    for state in states:
        missing_actions = sorted(set(actions) - set(action_kernel[state]))
        if missing_actions:
            raise ValueError(f"action kernel state {state!r} is missing actions: {missing_actions}")
        extra_actions = sorted(set(action_kernel[state]) - set(actions))
        if extra_actions:
            raise ValueError(
                f"action kernel state {state!r} has undeclared actions: {extra_actions}"
            )
    for action in actions:
        transition = {state: action_kernel[state][action] for state in states}
        validate_transition_kernel(states, transition)


def induced_transition_kernel(
    states: tuple[str, ...],
    actions: tuple[str, ...],
    action_kernel: ActionKernel,
    policy: Policy,
) -> TransitionKernel:
    """Induce a Markov kernel from an action kernel and deterministic policy."""

    validate_action_kernel(states, actions, action_kernel)
    missing_policy_states = sorted(set(states) - set(policy))
    if missing_policy_states:
        raise ValueError(f"policy is missing states: {missing_policy_states}")
    extra_policy_states = sorted(set(policy) - set(states))
    if extra_policy_states:
        raise ValueError(f"policy has undeclared states: {extra_policy_states}")
    unknown_actions = {
        state: action for state, action in policy.items() if action not in actions
    }
    if unknown_actions:
        raise ValueError(f"policy uses unknown actions: {unknown_actions}")
    return {state: dict(action_kernel[state][policy[state]]) for state in states}


def policy_hit_probability_within_horizon(
    states: tuple[str, ...],
    actions: tuple[str, ...],
    action_kernel: ActionKernel,
    policy: Policy,
    start: str,
    targets: frozenset[str],
    horizon: int,
) -> Fraction:
    """Finite-horizon hit probability under a deterministic policy."""

    transition = induced_transition_kernel(states, actions, action_kernel, policy)
    return hit_probability_within_horizon(states, transition, start, targets, horizon)


def support_summary_for_policy_kernel(
    states: tuple[str, ...],
    actions: tuple[str, ...],
    action_kernel: ActionKernel,
    policy: Policy,
    start: str,
    targets: frozenset[str],
) -> dict[str, object]:
    """A deliberately coarse support summary for policy non-factorization."""

    transition = induced_transition_kernel(states, actions, action_kernel, policy)
    positive_edges = tuple(
        (source, target)
        for source in states
        for target in states
        if transition[source][target] > 0
    )
    reachable_from_start = _reachable_from(states, positive_edges, start)
    return {
        "positive_edge_count": len(positive_edges),
        "reachable_state_count": len(reachable_from_start),
        "target_reachable": bool(set(reachable_from_start) & targets),
    }


def policy_hit_status_closure_surface(
    states: tuple[str, ...],
    actions: tuple[str, ...],
    before: ActionKernel,
    after: ActionKernel,
    policy: Policy,
    targets: frozenset[str],
    *,
    horizon: int,
    threshold: Fraction,
) -> tuple[dict[str, object], tuple[HypothesisCheck, ...]]:
    """Compute policy-conditioned hit-status closure facts and hypotheses."""

    before_transition = induced_transition_kernel(states, actions, before, policy)
    after_transition = induced_transition_kernel(states, actions, after, policy)
    before_status = _hit_status_by_start(
        states,
        before_transition,
        targets,
        horizon=horizon,
        threshold=threshold,
    )
    after_status = _hit_status_by_start(
        states,
        after_transition,
        targets,
        horizon=horizon,
        threshold=threshold,
    )
    after_high_hit = [
        state for state, status in after_status.items() if status == "high_hit"
    ]
    model_raw = {
        "model_id": "policy_hit_status_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            "after_high_hit": after_high_hit,
            "all_states": list(states),
        },
        "functions": {
            "stale_policy_hit_status": before_status,
            "reflected_policy_hit_status": after_status,
        },
        "audits": [
            {
                "id": "reflected_policy_hit_status_preserves_after_high_hit",
                "kind": "presentation_fact_closure",
                "presentations": ["reflected_policy_hit_status"],
                "target_predicates": ["after_high_hit", "all_states"],
                "expected_common_target_predicates": [
                    "after_high_hit",
                    "all_states",
                ],
                "expect": "closure_ok",
            },
            {
                "id": "stale_reflected_policy_hit_status_drops_after_high_hit",
                "kind": "presentation_fact_closure",
                "presentations": [
                    "stale_policy_hit_status",
                    "reflected_policy_hit_status",
                ],
                "target_predicates": ["after_high_hit", "all_states"],
                "expected_common_target_predicates": ["all_states"],
                "expected_absent_target_predicates": ["after_high_hit"],
                "expect": "closure_ok",
            },
        ],
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.stochastic_policy_dynamics",
            "claim_boundary": (
                "Synthetic exact-rational policy-conditioned closure check; "
                "not policy safety validation, value, agency, or Omega."
            ),
            "derivation_rules": [
                "policy_kernel=action_kernel_induced_by_deterministic_policy",
                "hit_status=finite_horizon_hit_probability_threshold",
                "closure_audits=presentation_fact_closure(stale,reflected)",
            ],
        },
    }
    model = load_model(model_raw)
    results = tuple(run_declared_audits(model))
    by_id = {result.audit_id: result for result in results}
    reflected = by_id["reflected_policy_hit_status_preserves_after_high_hit"]
    stale_reflected = by_id[
        "stale_reflected_policy_hit_status_drops_after_high_hit"
    ]
    reflected_common = reflected.observed["common_target_predicates"]
    stale_reflected_common = stale_reflected.observed["common_target_predicates"]

    facts: dict[str, object] = {
        "threshold": fraction_to_text(threshold),
        "horizon": horizon,
        "before_hit_status_by_start": before_status,
        "after_hit_status_by_start": after_status,
        "closure_model_digest": model_digest(model),
        "closure_audit_findings": [result.finding for result in results],
        "reflected_common_target_predicates": reflected_common,
        "stale_reflected_common_target_predicates": stale_reflected_common,
    }
    hypotheses = (
        HypothesisCheck(
            hypothesis_id="reflected_policy_hit_status_preserves_after_high_hit",
            statement=(
                "The reflected policy hit-status presentation preserves the "
                "after-threshold hit target."
            ),
            expected=True,
            observed=reflected_common == ["after_high_hit", "all_states"],
        ),
        HypothesisCheck(
            hypothesis_id="stale_reflected_policy_hit_status_drops_after_high_hit",
            statement=(
                "The stale/reflected policy hit-status family drops the "
                "after-threshold hit target from common facts."
            ),
            expected=True,
            observed=(
                stale_reflected_common == ["all_states"]
                and stale_reflected.observed[
                    "present_expected_absent_target_predicates"
                ]
                == []
            ),
        ),
    )
    return facts, hypotheses


def _policy_stale_reflected_hit_loss_family() -> PolicyDynamicsFamily:
    states = ("x0", "x1", "goal")
    actions = ("move", "wait")
    policy = {"x0": "move", "x1": "move", "goal": "wait"}
    start = "x0"
    targets = frozenset({"goal"})
    horizon = 2
    before = _line_policy_kernel(goal_probability=Fraction(9, 10))
    after = _line_policy_kernel(goal_probability=Fraction(1, 10))
    before_hit = policy_hit_probability_within_horizon(
        states,
        actions,
        before,
        policy,
        start,
        targets,
        horizon,
    )
    after_hit = policy_hit_probability_within_horizon(
        states,
        actions,
        after,
        policy,
        start,
        targets,
        horizon,
    )
    stale_hit = policy_hit_probability_within_horizon(
        states,
        actions,
        before,
        policy,
        start,
        targets,
        horizon,
    )
    reflected_hit = policy_hit_probability_within_horizon(
        states,
        actions,
        after,
        policy,
        start,
        targets,
        horizon,
    )
    closure_facts, closure_hypotheses = policy_hit_status_closure_surface(
        states,
        actions,
        before,
        after,
        policy,
        targets,
        horizon=horizon,
        threshold=Fraction(1, 2),
    )
    facts = {
        "states": list(states),
        "actions": list(actions),
        "policy": policy,
        "start": start,
        "targets": sorted(targets),
        "horizon": horizon,
        "before_hit_probability": fraction_to_text(before_hit),
        "after_hit_probability": fraction_to_text(after_hit),
        "loss_amount": fraction_to_text(before_hit - after_hit),
        "stale_abstraction_hit_probability": fraction_to_text(stale_hit),
        "reflected_abstraction_hit_probability": fraction_to_text(reflected_hit),
        "hit_status_closure": closure_facts,
    }
    hypotheses = (
        HypothesisCheck(
            hypothesis_id="stale_hides_policy_loss",
            statement="The stale policy model reports the old hit probability after loss.",
            expected=True,
            observed=stale_hit == before_hit and stale_hit > after_hit,
        ),
        HypothesisCheck(
            hypothesis_id="reflected_reports_policy_loss",
            statement="The reflected policy model reports the lower after-perturbation hit probability.",
            expected=True,
            observed=reflected_hit == after_hit and reflected_hit < before_hit,
        ),
    ) + closure_hypotheses
    return PolicyDynamicsFamily(
        family_id="policy_stale_reflected_hit_loss",
        description=(
            "A deterministic policy in a tiny finite MDP loses target hit "
            "probability under perturbation; stale abstraction hides the loss, "
            "while reflected abstraction reports it."
        ),
        facts=facts,
        hypotheses=hypotheses,
    )


def _policy_nonfactorization_same_support_summary_family() -> PolicyDynamicsFamily:
    states = ("start", "goal", "trap")
    actions = ("try", "wait")
    policy = {"start": "try", "goal": "wait", "trap": "wait"}
    start = "start"
    targets = frozenset({"goal"})
    horizon = 1
    high = _one_step_policy_kernel(goal_probability=Fraction(9, 10))
    low = _one_step_policy_kernel(goal_probability=Fraction(3, 5))
    high_summary = support_summary_for_policy_kernel(
        states,
        actions,
        high,
        policy,
        start,
        targets,
    )
    low_summary = support_summary_for_policy_kernel(
        states,
        actions,
        low,
        policy,
        start,
        targets,
    )
    high_hit = policy_hit_probability_within_horizon(
        states,
        actions,
        high,
        policy,
        start,
        targets,
        horizon,
    )
    low_hit = policy_hit_probability_within_horizon(
        states,
        actions,
        low,
        policy,
        start,
        targets,
        horizon,
    )
    facts = {
        "states": list(states),
        "actions": list(actions),
        "policy": policy,
        "start": start,
        "targets": sorted(targets),
        "horizon": horizon,
        "high_support_summary": high_summary,
        "low_support_summary": low_summary,
        "same_support_summary": high_summary == low_summary,
        "high_hit_probability": fraction_to_text(high_hit),
        "low_hit_probability": fraction_to_text(low_hit),
        "different_policy_hit_probability": high_hit != low_hit,
    }
    hypotheses = (
        HypothesisCheck(
            hypothesis_id="same_support_summary_not_policy_hit_probability",
            statement=(
                "A coarse policy support summary does not determine finite-horizon "
                "policy hit probability."
            ),
            expected=True,
            observed=high_summary == low_summary and high_hit != low_hit,
        ),
    )
    return PolicyDynamicsFamily(
        family_id="policy_nonfactorization_same_support_summary",
        description=(
            "Two policy-conditioned stochastic dynamics have the same coarse "
            "support summary but different finite-horizon target hit probability."
        ),
        facts=facts,
        hypotheses=hypotheses,
    )


def _line_policy_kernel(*, goal_probability: Fraction) -> ActionKernel:
    if goal_probability < 0 or goal_probability > 1:
        raise ValueError("goal_probability must be in [0, 1]")
    stay_probability = Fraction(1) - goal_probability
    return {
        "x0": {
            "move": {"x0": Fraction(0), "x1": Fraction(1), "goal": Fraction(0)},
            "wait": {"x0": Fraction(1), "x1": Fraction(0), "goal": Fraction(0)},
        },
        "x1": {
            "move": {
                "x0": Fraction(0),
                "x1": stay_probability,
                "goal": goal_probability,
            },
            "wait": {"x0": Fraction(0), "x1": Fraction(1), "goal": Fraction(0)},
        },
        "goal": {
            "move": {"x0": Fraction(0), "x1": Fraction(0), "goal": Fraction(1)},
            "wait": {"x0": Fraction(0), "x1": Fraction(0), "goal": Fraction(1)},
        },
    }


def _one_step_policy_kernel(*, goal_probability: Fraction) -> ActionKernel:
    if goal_probability < 0 or goal_probability > 1:
        raise ValueError("goal_probability must be in [0, 1]")
    trap_probability = Fraction(1) - goal_probability
    return {
        "start": {
            "try": {"start": Fraction(0), "goal": goal_probability, "trap": trap_probability},
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


def _reachable_from(
    states: tuple[str, ...],
    positive_edges: tuple[tuple[str, str], ...],
    start: str,
) -> tuple[str, ...]:
    seen = {start}
    changed = True
    while changed:
        changed = False
        for left, right in positive_edges:
            if left in seen and right not in seen:
                seen.add(right)
                changed = True
    return tuple(state for state in states if state in seen)


def _hit_status_by_start(
    states: tuple[str, ...],
    kernel: TransitionKernel,
    targets: frozenset[str],
    *,
    horizon: int,
    threshold: Fraction,
) -> dict[str, str]:
    return {
        state: (
            "high_hit"
            if hit_probability_within_horizon(
                states,
                kernel,
                state,
                targets,
                horizon,
            )
            >= threshold
            else "low_hit"
        )
        for state in states
    }


def _family_as_dict(family: PolicyDynamicsFamily) -> dict[str, object]:
    return {
        "family_id": family.family_id,
        "description": family.description,
        "facts": family.facts,
        "hypotheses": [hypothesis.as_dict() for hypothesis in family.hypotheses],
        "all_hypotheses_passed": family.all_hypotheses_passed,
    }
