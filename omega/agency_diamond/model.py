"""Finite deterministic controlled-system model for agency-diamond pilots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


State = str
Action = str
Observation = str
Scenario = str


@dataclass(frozen=True)
class ControlledSystem:
    """A finite deterministic controlled system with declared interfaces.

    The fields are realization-supplied. The pilot computes whether the
    realization exhibits control, observation, feedback advantage, and
    reflexive-maintenance signatures under the declared perturbation scenarios.
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
    transition: Mapping[Scenario, Mapping[State, Mapping[Action, State]]]
    observe: Mapping[State, Observation]
    live_policy: Mapping[Observation, Action]
    target_states: frozenset[State]
    viable_states: frozenset[State]
    channel_states: frozenset[State]
    channel_challenge_scenarios: tuple[Scenario, ...] = ()
    joint_safe_states: frozenset[State] | None = None


@dataclass(frozen=True)
class EvaluationCase:
    """A system/horizon pair for the midscale pilot."""

    case_id: str
    system: ControlledSystem
    horizon: int


@dataclass(frozen=True)
class Trace:
    """A finite trajectory trace."""

    states: tuple[State, ...]
    observations: tuple[Observation, ...]
    actions: tuple[Action, ...]

    @property
    def final_state(self) -> State:
        return self.states[-1]


def validate_system(system: ControlledSystem) -> None:
    """Reject malformed or smuggled finite controlled-system surfaces."""

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
    for scenario, by_state in system.transition.items():
        if set(by_state) != states:
            raise ValueError(f"transition states do not match declared states in {scenario}")
        for state, by_action in by_state.items():
            if set(by_action) != actions:
                raise ValueError(
                    f"transition actions do not match declared actions in {scenario}/{state}"
                )
            unknown_targets = set(by_action.values()) - states
            if unknown_targets:
                raise ValueError(
                    f"transition uses undeclared targets in {scenario}/{state}: "
                    f"{sorted(unknown_targets)}"
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


def live_action(system: ControlledSystem, state: State) -> Action:
    return system.live_policy[system.observe[state]]


def simulate_live(
    system: ControlledSystem,
    *,
    scenario: Scenario,
    horizon: int,
    start: State | None = None,
) -> Trace:
    """Simulate the declared live observation-policy loop."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    current = system.scenario_starts[scenario] if start is None else start
    states = [current]
    observations: list[Observation] = []
    actions: list[Action] = []
    for _ in range(horizon):
        obs = system.observe[current]
        action = system.live_policy[obs]
        observations.append(obs)
        actions.append(action)
        current = system.transition[scenario][current][action]
        states.append(current)
    return Trace(tuple(states), tuple(observations), tuple(actions))


def simulate_replay(
    system: ControlledSystem,
    *,
    scenario: Scenario,
    replay_actions: tuple[Action, ...],
    start: State | None = None,
) -> Trace:
    """Simulate an open-loop replay action sequence."""

    current = system.scenario_starts[scenario] if start is None else start
    states = [current]
    observations: list[Observation] = []
    actions: list[Action] = []
    for action in replay_actions:
        if action not in system.actions:
            raise ValueError(f"replay action is undeclared: {action}")
        observations.append(system.observe[current])
        actions.append(action)
        current = system.transition[scenario][current][action]
        states.append(current)
    return Trace(tuple(states), tuple(observations), tuple(actions))

