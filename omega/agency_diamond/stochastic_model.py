"""Exact-rational stochastic controlled-system model for agency-diamond pilots."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping


State = str
Action = str
Observation = str
Scenario = str
StateDistribution = dict[State, Fraction]
ActionKernel = Mapping[State, Mapping[Action, Mapping[State, Fraction]]]


@dataclass(frozen=True)
class StochasticControlledSystem:
    """Finite stochastic controlled system with declared agency-diamond interfaces.

    This is an exploratory realization surface. It does not assert agency,
    identity, value, valuerhood, or Omega; it supplies exact finite transition
    probabilities so the pilot can measure stochastic control, feedback,
    reflexive maintenance, joint effect, and presentation coherence.
    """

    system_id: str
    family: str
    description: str
    states: tuple[State, ...]
    actions: tuple[Action, ...]
    observations: tuple[Observation, ...]
    scenarios: tuple[Scenario, ...]
    nominal_scenario: Scenario
    scenario_starts: Mapping[Scenario, State]
    transition: Mapping[Scenario, ActionKernel]
    observe: Mapping[State, Observation]
    live_policy: Mapping[Observation, Action]
    target_states: frozenset[State]
    viable_states: frozenset[State]
    channel_states: frozenset[State]
    channel_challenge_scenarios: tuple[Scenario, ...] = ()
    joint_safe_states: frozenset[State] | None = None
    presentations: Mapping[str, Mapping[State, str]] | None = None


@dataclass(frozen=True)
class StochasticEvaluationCase:
    """A system/horizon pair for stochastic agency-diamond evaluation."""

    case_id: str
    system: StochasticControlledSystem
    horizon: int


def validate_stochastic_system(system: StochasticControlledSystem) -> None:
    """Reject malformed stochastic controlled-system surfaces."""

    states = set(system.states)
    actions = set(system.actions)
    observations = set(system.observations)
    scenarios = set(system.scenarios)

    if not system.states:
        raise ValueError("system must declare at least one state")
    if not system.actions:
        raise ValueError("system must declare at least one action")
    if not system.observations:
        raise ValueError("system must declare at least one observation")
    if system.nominal_scenario not in scenarios:
        raise ValueError("nominal scenario is not declared")
    if set(system.scenario_starts) != scenarios:
        raise ValueError("scenario starts must match declared scenarios")
    unknown_starts = set(system.scenario_starts.values()) - states
    if unknown_starts:
        raise ValueError(f"scenario starts use undeclared states: {sorted(unknown_starts)}")

    if set(system.observe) != states:
        raise ValueError("observation map must match declared states")
    unknown_obs = set(system.observe.values()) - observations
    if unknown_obs:
        raise ValueError(f"observation map uses undeclared observations: {sorted(unknown_obs)}")
    if set(system.live_policy) != observations:
        raise ValueError("live policy must match declared observations")
    unknown_policy_actions = set(system.live_policy.values()) - actions
    if unknown_policy_actions:
        raise ValueError(
            f"live policy uses undeclared actions: {sorted(unknown_policy_actions)}"
        )

    if set(system.transition) != scenarios:
        raise ValueError("transition table must match declared scenarios")
    for scenario, kernel in system.transition.items():
        _validate_action_kernel(
            states=system.states,
            actions=system.actions,
            kernel=kernel,
            label=scenario,
        )

    for name, subset in (
        ("target_states", system.target_states),
        ("viable_states", system.viable_states),
        ("channel_states", system.channel_states),
    ):
        unknown = set(subset) - states
        if unknown:
            raise ValueError(f"{name} contains undeclared states: {sorted(unknown)}")

    unknown_channel_scenarios = set(system.channel_challenge_scenarios) - scenarios
    if unknown_channel_scenarios:
        raise ValueError(
            "channel challenge scenarios are undeclared: "
            f"{sorted(unknown_channel_scenarios)}"
        )

    if system.joint_safe_states is not None:
        unknown_joint = set(system.joint_safe_states) - states
        if unknown_joint:
            raise ValueError(
                f"joint_safe_states contains undeclared states: {sorted(unknown_joint)}"
            )

    if system.presentations is not None:
        for name, presentation in system.presentations.items():
            if set(presentation) != states:
                raise ValueError(f"presentation {name!r} must map every state")
            if any(block == "" for block in presentation.values()):
                raise ValueError(f"presentation {name!r} uses an empty block label")


def live_action(system: StochasticControlledSystem, state: State) -> Action:
    return system.live_policy[system.observe[state]]


def point_mass(system: StochasticControlledSystem, state: State) -> StateDistribution:
    if state not in system.states:
        raise ValueError(f"state {state!r} is not declared")
    return {candidate: Fraction(1) if candidate == state else Fraction(0) for candidate in system.states}


def step_distribution(
    system: StochasticControlledSystem,
    distribution: Mapping[State, Fraction],
    *,
    scenario: Scenario,
    action_for_state,
) -> StateDistribution:
    """Advance a distribution by one step under a state-dependent action rule."""

    next_distribution = {state: Fraction(0) for state in system.states}
    kernel = system.transition[scenario]
    for state in system.states:
        mass = distribution.get(state, Fraction(0))
        if mass == 0:
            continue
        action = action_for_state(state)
        for target in system.states:
            next_distribution[target] += mass * kernel[state][action][target]
    return next_distribution


def support_successors(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    state: State,
    action: Action,
) -> frozenset[State]:
    """Positive-probability successors for a state/action/scenario triple."""

    row = system.transition[scenario][state][action]
    return frozenset(target for target, probability in row.items() if probability > 0)


def _validate_action_kernel(
    *,
    states: tuple[State, ...],
    actions: tuple[Action, ...],
    kernel: ActionKernel,
    label: str,
) -> None:
    missing_states = sorted(set(states) - set(kernel))
    if missing_states:
        raise ValueError(f"kernel {label!r} is missing states: {missing_states}")
    extra_states = sorted(set(kernel) - set(states))
    if extra_states:
        raise ValueError(f"kernel {label!r} has undeclared states: {extra_states}")

    for state in states:
        by_action = kernel[state]
        missing_actions = sorted(set(actions) - set(by_action))
        if missing_actions:
            raise ValueError(
                f"kernel {label!r}/{state!r} is missing actions: {missing_actions}"
            )
        extra_actions = sorted(set(by_action) - set(actions))
        if extra_actions:
            raise ValueError(
                f"kernel {label!r}/{state!r} has undeclared actions: {extra_actions}"
            )
        for action in actions:
            row = by_action[action]
            missing_targets = sorted(set(states) - set(row))
            if missing_targets:
                raise ValueError(
                    f"kernel {label!r}/{state!r}/{action!r} is missing targets: "
                    f"{missing_targets}"
                )
            extra_targets = sorted(set(row) - set(states))
            if extra_targets:
                raise ValueError(
                    f"kernel {label!r}/{state!r}/{action!r} has undeclared targets: "
                    f"{extra_targets}"
                )
            negative = {target: weight for target, weight in row.items() if weight < 0}
            if negative:
                raise ValueError(
                    f"kernel {label!r}/{state!r}/{action!r} has negative weights: "
                    f"{negative}"
                )
            total = sum((row[target] for target in states), start=Fraction(0))
            if total != 1:
                raise ValueError(
                    f"kernel {label!r}/{state!r}/{action!r} sums to {total}, not 1"
                )
