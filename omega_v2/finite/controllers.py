"""Finite-state controllers and exact closed-loop compilation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from typing import Generic, Hashable, TypeVar

from omega_v2.finite.model import (
    ActionT,
    ControlledMarkovSystem,
    DeterministicPolicy,
    FiniteDistribution,
    StateT,
)


ObservationT = TypeVar("ObservationT", bound=Hashable)
MemoryT = TypeVar("MemoryT", bound=Hashable)

CLOSED_LOOP_ACTION = "step"


@dataclass(frozen=True)
class FiniteStateController(
    Generic[StateT, ActionT, ObservationT, MemoryT]
):
    """A total deterministic controller over finite observations and memory."""

    controller_id: str
    memory_states: tuple[MemoryT, ...]
    initial_memory: MemoryT
    observation_rows: tuple[tuple[StateT, ObservationT], ...]
    update_rows: tuple[tuple[MemoryT, ObservationT, MemoryT], ...]
    policy_rows: tuple[tuple[MemoryT, ObservationT, ActionT], ...]

    def __post_init__(self) -> None:
        if not self.controller_id:
            raise ValueError("controller_id must be nonempty")
        if not self.memory_states or len(self.memory_states) != len(
            set(self.memory_states)
        ):
            raise ValueError("memory states must be nonempty and unique")
        if self.initial_memory not in self.memory_states:
            raise ValueError("initial memory must be declared")

        observed_states = tuple(state for state, _observation in self.observation_rows)
        if not observed_states or len(observed_states) != len(set(observed_states)):
            raise ValueError("observation rows must be nonempty and functional")
        observations = frozenset(
            observation for _state, observation in self.observation_rows
        )
        required_keys = {
            (memory, observation)
            for memory in self.memory_states
            for observation in observations
        }

        update_keys = tuple(
            (memory, observation)
            for memory, observation, _target in self.update_rows
        )
        if len(update_keys) != len(set(update_keys)) or set(update_keys) != required_keys:
            raise ValueError("controller update must be total and deterministic")
        if any(
            target not in self.memory_states
            for _memory, _observation, target in self.update_rows
        ):
            raise ValueError("controller update references unknown memory")

        policy_keys = tuple(
            (memory, observation)
            for memory, observation, _action in self.policy_rows
        )
        if len(policy_keys) != len(set(policy_keys)) or set(policy_keys) != required_keys:
            raise ValueError("controller policy must be total and deterministic")

    @property
    def observation_map(self) -> dict[StateT, ObservationT]:
        return dict(self.observation_rows)

    @property
    def update_map(self) -> dict[tuple[MemoryT, ObservationT], MemoryT]:
        return {
            (memory, observation): target
            for memory, observation, target in self.update_rows
        }

    @property
    def policy_map(self) -> dict[tuple[MemoryT, ObservationT], ActionT]:
        return {
            (memory, observation): action
            for memory, observation, action in self.policy_rows
        }

    def validate(
        self,
        system: ControlledMarkovSystem[StateT, ActionT],
    ) -> None:
        if set(self.observation_map) != set(system.states):
            raise ValueError("controller observation map must cover the world states")
        if not set(self.policy_map.values()) <= set(system.actions):
            raise ValueError("controller policy references an unknown action")

    def observe(self, state: StateT) -> ObservationT:
        try:
            return self.observation_map[state]
        except KeyError as exc:
            raise KeyError(state) from exc

    def update(self, memory: MemoryT, observation: ObservationT) -> MemoryT:
        try:
            return self.update_map[(memory, observation)]
        except KeyError as exc:
            raise KeyError((memory, observation)) from exc

    def action(self, memory: MemoryT, observation: ObservationT) -> ActionT:
        try:
            return self.policy_map[(memory, observation)]
        except KeyError as exc:
            raise KeyError((memory, observation)) from exc


@dataclass(frozen=True)
class ClosedLoopState(Generic[StateT, MemoryT]):
    """One world state paired with one controller-memory state."""

    world_state: StateT
    memory_state: MemoryT


@dataclass(frozen=True)
class CompiledClosedLoop(Generic[StateT, MemoryT]):
    """An exact one-action Markov representation of a controller in a world."""

    system: ControlledMarkovSystem[ClosedLoopState[StateT, MemoryT], str]
    policy: DeterministicPolicy[ClosedLoopState[StateT, MemoryT], str]


def compile_closed_loop(
    system: ControlledMarkovSystem[StateT, ActionT],
    controller: FiniteStateController[StateT, ActionT, ObservationT, MemoryT],
) -> CompiledClosedLoop[StateT, MemoryT]:
    """Compile current-observation update and action choice into one Markov system."""

    controller.validate(system)
    states = tuple(
        ClosedLoopState(world_state, memory_state)
        for world_state in system.states
        for memory_state in controller.memory_states
    )
    transitions: list[
        tuple[
            ClosedLoopState[StateT, MemoryT],
            str,
            ClosedLoopState[StateT, MemoryT],
            Fraction,
        ]
    ] = []
    for source in states:
        observation = controller.observe(source.world_state)
        selected_action = controller.action(source.memory_state, observation)
        next_memory = controller.update(source.memory_state, observation)
        for target, probability in system.distribution(
            source.world_state,
            selected_action,
        ).rows:
            transitions.append(
                (
                    source,
                    CLOSED_LOOP_ACTION,
                    ClosedLoopState(target, next_memory),
                    probability,
                )
            )

    closed_system = ControlledMarkovSystem(
        system_id=f"{system.system_id}__{controller.controller_id}",
        states=states,
        actions=(CLOSED_LOOP_ACTION,),
        transitions=tuple(transitions),
    )
    closed_policy = DeterministicPolicy(
        policy_id=f"{controller.controller_id}__closed_loop",
        rows=tuple((state, CLOSED_LOOP_ACTION) for state in states),
    )
    return CompiledClosedLoop(system=closed_system, policy=closed_policy)


def closed_loop_initial_distribution(
    initial_world: FiniteDistribution[StateT],
    controller: FiniteStateController[StateT, ActionT, ObservationT, MemoryT],
) -> FiniteDistribution[ClosedLoopState[StateT, MemoryT]]:
    """Lift a world-state law into the controller's declared initial memory."""

    return initial_world.pushforward(
        lambda state: ClosedLoopState(state, controller.initial_memory)
    )


def reachable_closed_loop_states(
    compiled: CompiledClosedLoop[StateT, MemoryT],
    initial: FiniteDistribution[ClosedLoopState[StateT, MemoryT]],
) -> frozenset[ClosedLoopState[StateT, MemoryT]]:
    """Return the support-reachable closed-loop states."""

    if not set(initial.support) <= set(compiled.system.states):
        raise ValueError("initial distribution references an unknown closed-loop state")
    reached = set(initial.support)
    queue = deque(initial.support)
    while queue:
        source = queue.popleft()
        for target in compiled.system.support_successors(
            source,
            CLOSED_LOOP_ACTION,
        ):
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return frozenset(reached)


def _has_reachable_cycle(
    compiled: CompiledClosedLoop[StateT, MemoryT],
    reached: frozenset[ClosedLoopState[StateT, MemoryT]],
) -> bool:
    adjacency = {
        source: compiled.system.support_successors(source, CLOSED_LOOP_ACTION)
        for source in reached
    }
    for start in reached:
        frontier = list(adjacency[start])
        seen: set[ClosedLoopState[StateT, MemoryT]] = set()
        while frontier:
            state = frontier.pop()
            if state == start:
                return True
            if state in seen:
                continue
            seen.add(state)
            frontier.extend(adjacency.get(state, frozenset()))
    return False


@dataclass(frozen=True)
class OperationalFeatureProfile(Generic[MemoryT]):
    """Operational controller features, deliberately short of valuerhood."""

    controller_id: str
    reachable_state_count: int
    reachable_memory_states: frozenset[MemoryT]
    selected_actions: frozenset[Hashable]
    causal_action_influence: bool
    record_sensitive_selection: bool
    closed_loop_persistence: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "controller_id": self.controller_id,
            "reachable_state_count": self.reachable_state_count,
            "reachable_memory_count": len(self.reachable_memory_states),
            "reachable_memory_states": sorted(
                (repr(memory) for memory in self.reachable_memory_states)
            ),
            "selected_action_count": len(self.selected_actions),
            "selected_actions": sorted(
                (repr(action) for action in self.selected_actions)
            ),
            "causal_action_influence": self.causal_action_influence,
            "record_sensitive_selection": self.record_sensitive_selection,
            "closed_loop_persistence": self.closed_loop_persistence,
        }


def audit_operational_features(
    system: ControlledMarkovSystem[StateT, ActionT],
    controller: FiniteStateController[StateT, ActionT, ObservationT, MemoryT],
    initial_world: FiniteDistribution[StateT],
) -> OperationalFeatureProfile[MemoryT]:
    """Derive finite operational features from reachable closed-loop behavior."""

    compiled = compile_closed_loop(system, controller)
    initial = closed_loop_initial_distribution(initial_world, controller)
    reached = reachable_closed_loop_states(compiled, initial)

    selected_actions: set[ActionT] = set()
    causal_action_influence = False
    for node in reached:
        observation = controller.observe(node.world_state)
        selected = controller.action(node.memory_state, observation)
        selected_actions.add(selected)
        selected_distribution = system.distribution(node.world_state, selected)
        if any(
            system.distribution(node.world_state, alternative)
            != selected_distribution
            for alternative in system.actions
        ):
            causal_action_influence = True

    reached_by_world: dict[StateT, list[ClosedLoopState[StateT, MemoryT]]] = {}
    for node in reached:
        reached_by_world.setdefault(node.world_state, []).append(node)
    record_sensitive_selection = any(
        left.memory_state != right.memory_state
        and controller.action(
            left.memory_state,
            controller.observe(world_state),
        )
        != controller.action(
            right.memory_state,
            controller.observe(world_state),
        )
        for world_state, nodes in reached_by_world.items()
        for left in nodes
        for right in nodes
    )

    return OperationalFeatureProfile(
        controller_id=controller.controller_id,
        reachable_state_count=len(reached),
        reachable_memory_states=frozenset(
            node.memory_state for node in reached
        ),
        selected_actions=frozenset(selected_actions),
        causal_action_influence=causal_action_influence,
        record_sensitive_selection=record_sensitive_selection,
        closed_loop_persistence=_has_reachable_cycle(compiled, reached),
    )
