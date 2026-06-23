"""Finite-horizon stochastic continuation loss checks.

This module is intentionally smaller than a full MDP layer. It handles finite
Markov kernels, exact rational hit probabilities, and stale-vs-reflected
abstraction controls.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from omega.adapters.finite_relational.audits import run_declared_audits
from omega.adapters.finite_relational.model import load_model, model_digest
from omega.adapters.finite_relational.stochastic_recovery import fraction_to_text


TransitionKernel = dict[str, dict[str, Fraction]]


@dataclass(frozen=True)
class StochasticContinuationFamily:
    """One finite-horizon stochastic continuation-loss family."""

    family_id: str
    description: str
    metrics: dict[str, object]


def generate_stochastic_continuation_loss_study() -> tuple[StochasticContinuationFamily, ...]:
    """Generate finite-horizon stochastic continuation-loss checks."""

    return (
        _noisy_line_grid_stale_hidden_hit_loss_family(),
        _same_expected_reach_different_tail_loss_family(),
    )


def stochastic_continuation_loss_summary() -> dict[str, object]:
    families = generate_stochastic_continuation_loss_study()
    return {
        "status": "PASS",
        "family_count": len(families),
        "families": [_family_as_dict(family) for family in families],
    }


def validate_transition_kernel(
    states: tuple[str, ...],
    kernel: TransitionKernel,
) -> None:
    """Require a total finite rational transition kernel whose rows sum to one."""

    missing_states = sorted(set(states) - set(kernel))
    if missing_states:
        raise ValueError(f"kernel is missing states: {missing_states}")
    extra_states = sorted(set(kernel) - set(states))
    if extra_states:
        raise ValueError(f"kernel has undeclared states: {extra_states}")
    for state in states:
        row = kernel[state]
        missing_targets = sorted(set(states) - set(row))
        if missing_targets:
            raise ValueError(f"kernel row {state!r} is missing targets: {missing_targets}")
        extra_targets = sorted(set(row) - set(states))
        if extra_targets:
            raise ValueError(f"kernel row {state!r} has undeclared targets: {extra_targets}")
        negative = {target: weight for target, weight in row.items() if weight < 0}
        if negative:
            raise ValueError(f"kernel row {state!r} has negative weights: {negative}")
        total = sum((row[target] for target in states), start=Fraction(0))
        if total != 1:
            raise ValueError(f"kernel row {state!r} sums to {total}, not 1")


def distribution_after_horizon(
    states: tuple[str, ...],
    kernel: TransitionKernel,
    start: str,
    horizon: int,
) -> dict[str, Fraction]:
    """State distribution after exactly `horizon` steps."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    if start not in states:
        raise ValueError(f"start state {start!r} is not in states")
    validate_transition_kernel(states, kernel)
    distribution = {state: Fraction(0) for state in states}
    distribution[start] = Fraction(1)
    for _step in range(horizon):
        distribution = {
            target: sum(
                (
                    distribution[source] * kernel[source][target]
                    for source in states
                ),
                start=Fraction(0),
            )
            for target in states
        }
    return distribution


def hit_probability_within_horizon(
    states: tuple[str, ...],
    kernel: TransitionKernel,
    start: str,
    targets: frozenset[str],
    horizon: int,
) -> Fraction:
    """Probability of hitting `targets` at or before the finite horizon."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    if start not in states:
        raise ValueError(f"start state {start!r} is not in states")
    unknown_targets = sorted(targets - set(states))
    if unknown_targets:
        raise ValueError(f"targets include unknown states: {unknown_targets}")
    validate_transition_kernel(states, kernel)
    if start in targets:
        return Fraction(1)

    not_yet_hit = {state: Fraction(0) for state in states}
    not_yet_hit[start] = Fraction(1)
    hit = Fraction(0)
    for _step in range(horizon):
        next_not_yet = {state: Fraction(0) for state in states}
        for source in states:
            for target, weight in kernel[source].items():
                mass = not_yet_hit[source] * weight
                if target in targets:
                    hit += mass
                else:
                    next_not_yet[target] += mass
        not_yet_hit = next_not_yet
    return hit


def hit_profile(
    states: tuple[str, ...],
    kernel: TransitionKernel,
    start: str,
    targets: frozenset[str],
    horizons: tuple[int, ...],
) -> dict[str, str]:
    """Hitting probabilities for a list of finite horizons."""

    return {
        str(horizon): fraction_to_text(
            hit_probability_within_horizon(states, kernel, start, targets, horizon)
        )
        for horizon in horizons
    }


def hit_status_closure_summary(
    states: tuple[str, ...],
    before: TransitionKernel,
    after: TransitionKernel,
    targets: frozenset[str],
    *,
    horizon: int,
    threshold: Fraction,
) -> dict[str, object]:
    """Audit stale/reflected hit-status presentations against after-hit status."""

    before_status = _hit_status_by_start(
        states,
        before,
        targets,
        horizon=horizon,
        threshold=threshold,
    )
    after_status = _hit_status_by_start(
        states,
        after,
        targets,
        horizon=horizon,
        threshold=threshold,
    )
    after_high_hit = [
        state for state, status in after_status.items() if status == "high_hit"
    ]
    model_raw = {
        "model_id": "stochastic_continuation_hit_status_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            "after_high_hit": after_high_hit,
            "all_states": list(states),
        },
        "functions": {
            "stale_hit_status": before_status,
            "reflected_hit_status": after_status,
        },
        "audits": [
            {
                "id": "reflected_hit_status_preserves_after_high_hit",
                "kind": "presentation_fact_closure",
                "presentations": ["reflected_hit_status"],
                "target_predicates": ["after_high_hit", "all_states"],
                "expected_common_target_predicates": [
                    "after_high_hit",
                    "all_states",
                ],
                "expect": "closure_ok",
            },
            {
                "id": "stale_reflected_hit_status_drops_after_high_hit",
                "kind": "presentation_fact_closure",
                "presentations": ["stale_hit_status", "reflected_hit_status"],
                "target_predicates": ["after_high_hit", "all_states"],
                "expected_common_target_predicates": ["all_states"],
                "expected_absent_target_predicates": ["after_high_hit"],
                "expect": "closure_ok",
            },
        ],
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.stochastic_continuation_loss",
            "claim_boundary": (
                "Synthetic exact-rational stochastic continuation closure check; "
                "not empirical transition validation, value, agency, or Omega."
            ),
            "derivation_rules": [
                "hit_status=finite_horizon_hit_probability_threshold",
                "closure_audits=presentation_fact_closure(stale,reflected)",
            ],
        },
    }
    model = load_model(model_raw)
    results = tuple(run_declared_audits(model))
    if not all(result.passed for result in results):
        failures = [result.as_dict() for result in results if not result.passed]
        raise AssertionError(f"stochastic hit-status closure audit failed: {failures}")

    return {
        "threshold": fraction_to_text(threshold),
        "horizon": horizon,
        "before_hit_status_by_start": before_status,
        "after_hit_status_by_start": after_status,
        "closure_model_digest": model_digest(model),
        "closure_audit_findings": [result.finding for result in results],
        "closure_audits": [result.as_dict() for result in results],
    }


def _noisy_line_grid_stale_hidden_hit_loss_family() -> StochasticContinuationFamily:
    states = ("x0", "x1", "x2")
    start = "x0"
    targets = frozenset({"x2"})
    horizon = 2
    before = {
        "x0": {"x0": Fraction(0), "x1": Fraction(1), "x2": Fraction(0)},
        "x1": {"x0": Fraction(0), "x1": Fraction(1, 10), "x2": Fraction(9, 10)},
        "x2": {"x0": Fraction(0), "x1": Fraction(0), "x2": Fraction(1)},
    }
    after = {
        "x0": {"x0": Fraction(0), "x1": Fraction(1), "x2": Fraction(0)},
        "x1": {"x0": Fraction(0), "x1": Fraction(9, 10), "x2": Fraction(1, 10)},
        "x2": {"x0": Fraction(0), "x1": Fraction(0), "x2": Fraction(1)},
    }
    before_hit = hit_probability_within_horizon(states, before, start, targets, horizon)
    after_hit = hit_probability_within_horizon(states, after, start, targets, horizon)
    stale_hit = hit_probability_within_horizon(states, before, start, targets, horizon)
    reflected_hit = hit_probability_within_horizon(states, after, start, targets, horizon)
    closure = hit_status_closure_summary(
        states,
        before,
        after,
        targets,
        horizon=horizon,
        threshold=Fraction(1, 2),
    )

    return StochasticContinuationFamily(
        family_id="noisy_line_grid_stale_hidden_hit_loss",
        description=(
            "A finite-horizon noisy line-grid perturbation drops hit probability; "
            "a stale abstraction reports the old probability, while a reflected "
            "abstraction reports the drop."
        ),
        metrics={
            "horizon": horizon,
            "before_hit_probability": fraction_to_text(before_hit),
            "after_hit_probability": fraction_to_text(after_hit),
            "stale_abstraction_hit_probability": fraction_to_text(stale_hit),
            "reflected_abstraction_hit_probability": fraction_to_text(reflected_hit),
            "loss_amount": fraction_to_text(before_hit - after_hit),
            "stale_hides_loss": stale_hit == before_hit and stale_hit > after_hit,
            "reflected_reports_loss": reflected_hit == after_hit and reflected_hit < before_hit,
            "hit_status_closure": closure,
        },
    )


def _same_expected_reach_different_tail_loss_family() -> StochasticContinuationFamily:
    states = ("s", "safe", "loss")
    start = "s"
    targets = frozenset({"safe"})
    horizons = (1, 2, 3)
    fast_risk = {
        "s": {"s": Fraction(0), "safe": Fraction(3, 4), "loss": Fraction(1, 4)},
        "safe": {"s": Fraction(0), "safe": Fraction(1), "loss": Fraction(0)},
        "loss": {"s": Fraction(0), "safe": Fraction(0), "loss": Fraction(1)},
    }
    slow_safe = {
        "s": {"s": Fraction(1, 2), "safe": Fraction(1, 2), "loss": Fraction(0)},
        "safe": {"s": Fraction(0), "safe": Fraction(1), "loss": Fraction(0)},
        "loss": {"s": Fraction(0), "safe": Fraction(0), "loss": Fraction(1)},
    }
    fast_h1 = hit_probability_within_horizon(states, fast_risk, start, targets, 1)
    slow_h2 = hit_probability_within_horizon(states, slow_safe, start, targets, 2)

    return StochasticContinuationFamily(
        family_id="same_hit_probability_different_horizon_profile",
        description=(
            "A single hit-probability scalar can match while the finite-horizon "
            "profile differs, so stochastic continuation audits should retain "
            "profiles rather than only one scalar."
        ),
        metrics={
            "fast_horizon_1_hit_probability": fraction_to_text(fast_h1),
            "slow_horizon_2_hit_probability": fraction_to_text(slow_h2),
            "same_selected_hit_probability": fast_h1 == slow_h2,
            "fast_profile": hit_profile(states, fast_risk, start, targets, horizons),
            "slow_profile": hit_profile(states, slow_safe, start, targets, horizons),
            "same_profile": (
                hit_profile(states, fast_risk, start, targets, horizons)
                == hit_profile(states, slow_safe, start, targets, horizons)
            ),
        },
    )


def _family_as_dict(family: StochasticContinuationFamily) -> dict[str, object]:
    return {
        "family_id": family.family_id,
        "description": family.description,
        "metrics": family.metrics,
    }


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
