"""Canonical finite process monitors and passive history lifts.

Properties are supplied as complete deterministic Moore automata over
identifier-free edge observations. Equivalent property presentations minimize
to one canonical payload. Their passive products with exact world dynamics
support explicit unique-lifting, projection-conservation, and property-relative
history/corridor residue checks.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from typing import Any, Mapping

from omega.adapters.finite_relational.bounded_behavioral_logic import (
    derived_behavior_universe,
    derived_capability_profile,
)
from omega.adapters.finite_relational.dynamic_continuation_profiles import (
    Action,
    Edge,
    FiniteControlSystem,
    State,
    behavior_signature,
)


PROTOCOL_DOC = "docs/research_notes/omega_v2/canonical_process_monitors_protocol_v0.md"


@dataclass(frozen=True, order=True)
class ObservationSymbol:
    """Identifier-free observation of one concrete world edge."""

    source_atoms: tuple[str, ...]
    action_class: str
    target_atoms: tuple[str, ...]

    def payload(self) -> dict[str, Any]:
        return {
            "source_atoms": list(self.source_atoms),
            "action_class": self.action_class,
            "target_atoms": list(self.target_atoms),
        }


@dataclass(frozen=True)
class CertifiedObservationInterface:
    """Finite edge observation based on atoms and declared action classes."""

    interface_id: str
    action_classes: tuple[tuple[Action, str], ...]

    def __post_init__(self) -> None:
        if not self.interface_id:
            raise ValueError("interface_id must be nonempty")
        actions = tuple(action for action, _action_class in self.action_classes)
        if len(actions) != len(set(actions)):
            raise ValueError("each action may have at most one action class")
        if any(not action_class for _action, action_class in self.action_classes):
            raise ValueError("action classes must be nonempty")

    @property
    def action_class_map(self) -> dict[Action, str]:
        return dict(self.action_classes)

    def validate(self, system: FiniteControlSystem) -> None:
        if set(self.action_class_map) != set(system.actions):
            raise ValueError("action classes must be total on the system actions")

    def observe(
        self,
        system: FiniteControlSystem,
        edge: Edge,
    ) -> ObservationSymbol:
        self.validate(system)
        if edge not in system.transitions:
            raise ValueError(f"{edge!r} is not a concrete transition")
        source, action, target = edge
        return ObservationSymbol(
            source_atoms=tuple(sorted(system.atoms_at(source))),
            action_class=self.action_class_map[action],
            target_atoms=tuple(sorted(system.atoms_at(target))),
        )

    def alphabet(self, system: FiniteControlSystem) -> tuple[ObservationSymbol, ...]:
        return tuple(sorted({self.observe(system, edge) for edge in system.transitions}))

    def transport_actions(
        self,
        action_mapping: Mapping[Action, Action],
        *,
        interface_id: str,
    ) -> "CertifiedObservationInterface":
        if set(action_mapping) != set(self.action_class_map):
            raise ValueError("action transport must be total")
        if len(set(action_mapping.values())) != len(action_mapping):
            raise ValueError("action transport must be injective")
        return CertifiedObservationInterface(
            interface_id=interface_id,
            action_classes=tuple(
                (action_mapping[action], action_class)
                for action, action_class in self.action_classes
            ),
        )


TransitionRow = tuple[str, ObservationSymbol, str]
OutputRow = tuple[str, frozenset[str]]


@dataclass(frozen=True)
class PropertyAutomaton:
    """Complete deterministic Moore automaton for one declared property."""

    property_id: str
    states: tuple[str, ...]
    alphabet: tuple[ObservationSymbol, ...]
    initial_state: str
    transitions: tuple[TransitionRow, ...]
    outputs: tuple[OutputRow, ...]
    safe_states: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if not self.property_id:
            raise ValueError("property_id must be nonempty")
        if not self.states or len(self.states) != len(set(self.states)):
            raise ValueError("automaton states must be nonempty and unique")
        if self.initial_state not in self.states:
            raise ValueError("initial_state must be an automaton state")
        if len(self.alphabet) != len(set(self.alphabet)):
            raise ValueError("observation alphabet must be unique")

        state_set = set(self.states)
        alphabet_set = set(self.alphabet)
        transition_keys: set[tuple[str, ObservationSymbol]] = set()
        for source, symbol, target in self.transitions:
            if source not in state_set or target not in state_set:
                raise ValueError("automaton transition contains an unknown state")
            if symbol not in alphabet_set:
                raise ValueError("automaton transition contains an unknown symbol")
            key = (source, symbol)
            if key in transition_keys:
                raise ValueError("automaton update must be deterministic")
            transition_keys.add(key)
        required = {(state, symbol) for state in self.states for symbol in self.alphabet}
        if transition_keys != required:
            raise ValueError("automaton update must be total")

        output_states = tuple(state for state, _facts in self.outputs)
        if len(output_states) != len(set(output_states)):
            raise ValueError("each automaton state requires one output row")
        if set(output_states) != state_set:
            raise ValueError("automaton outputs must be total")

        if self.safe_states is not None:
            if len(self.safe_states) != len(set(self.safe_states)):
                raise ValueError("safe_states must be unique")
            if not set(self.safe_states) <= state_set:
                raise ValueError("safe_states contain an unknown state")

    @property
    def transition_map(self) -> dict[tuple[str, ObservationSymbol], str]:
        return {(source, symbol): target for source, symbol, target in self.transitions}

    @property
    def output_map(self) -> dict[str, frozenset[str]]:
        return dict(self.outputs)

    def update(self, state: str, symbol: ObservationSymbol) -> str:
        if state not in self.states:
            raise KeyError(state)
        if symbol not in self.alphabet:
            raise KeyError(symbol)
        return self.transition_map[(state, symbol)]

    def emit(self, state: str) -> frozenset[str]:
        if state not in self.states:
            raise KeyError(state)
        return self.output_map[state]

    def is_safe(self, state: str) -> bool:
        if self.safe_states is None:
            raise ValueError("this property automaton has no safety predicate")
        return state in self.safe_states


@dataclass(frozen=True, order=True)
class LiftedNode:
    world_state: State
    monitor_state: str


LiftedEdge = tuple[LiftedNode, Action, LiftedNode]


@dataclass(frozen=True)
class ConcretePath:
    start: State
    edges: tuple[Edge, ...]

    def validate(self, system: FiniteControlSystem) -> None:
        system._require_state(self.start)
        current = self.start
        for edge in self.edges:
            if edge not in system.transitions:
                raise ValueError(f"{edge!r} is not a concrete transition")
            source, _action, target = edge
            if source != current:
                raise ValueError("path edges must compose")
            current = target

    def end(self, system: FiniteControlSystem) -> State:
        self.validate(system)
        return self.edges[-1][2] if self.edges else self.start


@dataclass(frozen=True)
class ProcessLift:
    """Reachable category-of-elements presentation of one passive monitor."""

    base: FiniteControlSystem
    monitor: PropertyAutomaton
    observation: CertifiedObservationInterface
    initial_world_state: State
    nodes: tuple[LiftedNode, ...]
    edges: tuple[LiftedEdge, ...]

    @property
    def node_ids(self) -> dict[LiftedNode, str]:
        return {node: f"lifted_{index}" for index, node in enumerate(sorted(self.nodes))}

    def node_id(self, node: LiftedNode) -> str:
        try:
            return self.node_ids[node]
        except KeyError as exc:
            raise ValueError(f"unreachable lifted node: {node!r}") from exc

    def as_control_system(self, *, include_emits: bool) -> FiniteControlSystem:
        identifiers = self.node_ids
        atom_rows = []
        for node in self.nodes:
            atoms = set(self.base.atoms_at(node.world_state))
            if include_emits:
                atoms.update(f"monitor:{fact}" for fact in self.monitor.emit(node.monitor_state))
            if atoms:
                atom_rows.append((identifiers[node], frozenset(atoms)))
        return FiniteControlSystem(
            system_id=(
                f"{self.base.system_id}__{self.monitor.property_id}__"
                f"{'emit' if include_emits else 'world_only'}"
            ),
            states=tuple(identifiers[node] for node in sorted(self.nodes)),
            actions=self.base.actions,
            transitions=tuple(
                sorted(
                    (
                        identifiers[source],
                        action,
                        identifiers[target],
                    )
                    for source, action, target in self.edges
                )
            ),
            atoms=tuple(sorted(atom_rows)),
        )


def reachable_monitor_states(automaton: PropertyAutomaton) -> tuple[str, ...]:
    reached = {automaton.initial_state}
    queue = deque([automaton.initial_state])
    while queue:
        state = queue.popleft()
        for symbol in automaton.alphabet:
            target = automaton.update(state, symbol)
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return tuple(sorted(reached))


def minimize_property_automaton(automaton: PropertyAutomaton) -> PropertyAutomaton:
    """Return the canonical reachable Moore quotient, up to fixed mN names."""

    reachable = set(reachable_monitor_states(automaton))
    safe_marker = (
        None
        if automaton.safe_states is None
        else {state: automaton.is_safe(state) for state in reachable}
    )
    blocks: list[frozenset[str]] = []
    initial_groups: dict[tuple[frozenset[str], bool | None], set[str]] = {}
    for state in reachable:
        key = (
            automaton.emit(state),
            None if safe_marker is None else safe_marker[state],
        )
        initial_groups.setdefault(key, set()).add(state)
    blocks = [frozenset(group) for group in initial_groups.values()]

    changed = True
    while changed:
        changed = False
        block_of = {state: index for index, block in enumerate(blocks) for state in block}
        refined: list[frozenset[str]] = []
        for block in blocks:
            groups: dict[tuple[int, ...], set[str]] = {}
            for state in block:
                signature = tuple(
                    block_of[automaton.update(state, symbol)] for symbol in automaton.alphabet
                )
                groups.setdefault(signature, set()).add(state)
            refined.extend(frozenset(group) for group in groups.values())
            if len(groups) > 1:
                changed = True
        blocks = refined

    block_of = {state: index for index, block in enumerate(blocks) for state in block}
    initial_block = block_of[automaton.initial_state]
    ordered_blocks: list[int] = []
    queued = {initial_block}
    queue = deque([initial_block])
    while queue:
        block_index = queue.popleft()
        ordered_blocks.append(block_index)
        representative = min(blocks[block_index])
        for symbol in automaton.alphabet:
            target_block = block_of[automaton.update(representative, symbol)]
            if target_block not in queued:
                queued.add(target_block)
                queue.append(target_block)

    names = {block_index: f"m{index}" for index, block_index in enumerate(ordered_blocks)}
    transitions: list[TransitionRow] = []
    outputs: list[OutputRow] = []
    safe_states: list[str] | None = [] if automaton.safe_states is not None else None
    for block_index in ordered_blocks:
        name = names[block_index]
        representative = min(blocks[block_index])
        outputs.append((name, automaton.emit(representative)))
        if safe_states is not None and automaton.is_safe(representative):
            safe_states.append(name)
        for symbol in automaton.alphabet:
            target_block = block_of[automaton.update(representative, symbol)]
            transitions.append((name, symbol, names[target_block]))

    return PropertyAutomaton(
        property_id=f"{automaton.property_id}__minimal",
        states=tuple(names[index] for index in ordered_blocks),
        alphabet=automaton.alphabet,
        initial_state=names[initial_block],
        transitions=tuple(transitions),
        outputs=tuple(outputs),
        safe_states=None if safe_states is None else tuple(safe_states),
    )


def canonical_automaton_payload(automaton: PropertyAutomaton) -> dict[str, Any]:
    minimal = minimize_property_automaton(automaton)
    return {
        "alphabet": [symbol.payload() for symbol in minimal.alphabet],
        "initial_state": minimal.initial_state,
        "states": list(minimal.states),
        "outputs": [{"state": state, "facts": sorted(facts)} for state, facts in minimal.outputs],
        "safe_states": (None if minimal.safe_states is None else list(minimal.safe_states)),
        "transitions": [
            {
                "source": source,
                "symbol": symbol.payload(),
                "target": target,
            }
            for source, symbol, target in minimal.transitions
        ],
    }


def build_process_lift(
    base: FiniteControlSystem,
    monitor: PropertyAutomaton,
    observation: CertifiedObservationInterface,
    *,
    initial_world_state: State,
) -> ProcessLift:
    observation.validate(base)
    if monitor.alphabet != observation.alphabet(base):
        raise ValueError("monitor alphabet must equal the observed world alphabet")
    base._require_state(initial_world_state)

    initial = LiftedNode(initial_world_state, monitor.initial_state)
    reached = {initial}
    edges: set[LiftedEdge] = set()
    queue = deque([initial])
    while queue:
        node = queue.popleft()
        for action in base.enabled_actions(node.world_state):
            for target in base.successors(node.world_state, action):
                concrete_edge = (node.world_state, action, target)
                symbol = observation.observe(base, concrete_edge)
                next_node = LiftedNode(
                    target,
                    monitor.update(node.monitor_state, symbol),
                )
                edges.add((node, action, next_node))
                if next_node not in reached:
                    reached.add(next_node)
                    queue.append(next_node)

    return ProcessLift(
        base=base,
        monitor=monitor,
        observation=observation,
        initial_world_state=initial_world_state,
        nodes=tuple(sorted(reached)),
        edges=tuple(sorted(edges)),
    )


def run_monitor_on_path(
    monitor: PropertyAutomaton,
    observation: CertifiedObservationInterface,
    system: FiniteControlSystem,
    path: ConcretePath,
) -> str:
    path.validate(system)
    state = monitor.initial_state
    for edge in path.edges:
        state = monitor.update(state, observation.observe(system, edge))
    return state


def lift_path(
    lift: ProcessLift,
    start_monitor_state: str,
    path: ConcretePath,
) -> tuple[LiftedNode, ...]:
    path.validate(lift.base)
    current = LiftedNode(path.start, start_monitor_state)
    if current not in lift.nodes:
        raise ValueError("path lift must start at a reachable fibre point")
    nodes = [current]
    for edge in path.edges:
        source, action, target = edge
        if current.world_state != source:
            raise ValueError("path does not start over the current lifted node")
        next_monitor = lift.monitor.update(
            current.monitor_state,
            lift.observation.observe(lift.base, edge),
        )
        next_node = LiftedNode(target, next_monitor)
        matching = [
            candidate for candidate in lift.edges if candidate == (current, action, next_node)
        ]
        if len(matching) != 1:
            raise ValueError("concrete edge does not have exactly one lift")
        nodes.append(next_node)
        current = next_node
    return tuple(nodes)


def unique_step_lift_failures(lift: ProcessLift) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for node in lift.nodes:
        concrete_edges = [edge for edge in lift.base.transitions if edge[0] == node.world_state]
        for concrete_edge in concrete_edges:
            _source, action, target = concrete_edge
            expected_monitor = lift.monitor.update(
                node.monitor_state,
                lift.observation.observe(lift.base, concrete_edge),
            )
            matches = [
                edge
                for edge in lift.edges
                if edge[0] == node
                and edge[1] == action
                and edge[2] == LiftedNode(target, expected_monitor)
            ]
            if len(matches) != 1:
                failures.append(
                    {
                        "node": repr(node),
                        "concrete_edge": repr(concrete_edge),
                        "lift_count": len(matches),
                    }
                )
    return failures


def projection_conservation_failures(
    lift: ProcessLift,
    *,
    max_horizon: int,
) -> list[dict[str, Any]]:
    world_only_lift = lift.as_control_system(include_emits=False)
    failures: list[dict[str, Any]] = []
    for node in lift.nodes:
        lifted_state = lift.node_id(node)
        for horizon in range(max_horizon + 1):
            if behavior_signature(
                world_only_lift,
                lifted_state,
                horizon,
            ) != behavior_signature(
                lift.base,
                node.world_state,
                horizon,
            ):
                failures.append(
                    {
                        "node": repr(node),
                        "horizon": horizon,
                    }
                )
    return failures


def property_kernel(lift: ProcessLift) -> frozenset[LiftedNode]:
    if lift.monitor.safe_states is None:
        raise ValueError("property kernel requires a safety-property monitor")
    current = {node for node in lift.nodes if lift.monitor.is_safe(node.monitor_state)}
    changed = True
    while changed:
        changed = False
        next_states: set[LiftedNode] = set()
        for node in current:
            for action in lift.base.enabled_actions(node.world_state):
                successors = {
                    target
                    for source, candidate_action, target in lift.edges
                    if source == node and candidate_action == action
                }
                if successors and successors <= current:
                    next_states.add(node)
                    break
        if next_states != current:
            current = next_states
            changed = True
    return frozenset(current)


def admissible_action_classes(
    lift: ProcessLift,
    node: LiftedNode,
) -> frozenset[str]:
    kernel = property_kernel(lift)
    if node not in kernel:
        return frozenset()
    classes: set[str] = set()
    for action in lift.base.enabled_actions(node.world_state):
        successors = {
            target
            for source, candidate_action, target in lift.edges
            if source == node and candidate_action == action
        }
        if successors and successors <= kernel:
            classes.add(lift.observation.action_class_map[action])
    return frozenset(classes)


def history_residue(
    base: FiniteControlSystem,
    monitor: PropertyAutomaton,
    observation: CertifiedObservationInterface,
    left_path: ConcretePath,
    right_path: ConcretePath,
    *,
    horizon: int,
) -> dict[str, Any]:
    canonical = minimize_property_automaton(monitor)
    lift = build_process_lift(
        base,
        canonical,
        observation,
        initial_world_state=left_path.start,
    )
    if right_path.start != left_path.start:
        raise ValueError("compared histories must share one initial world state")
    left_monitor = run_monitor_on_path(canonical, observation, base, left_path)
    right_monitor = run_monitor_on_path(canonical, observation, base, right_path)
    left_node = LiftedNode(left_path.end(base), left_monitor)
    right_node = LiftedNode(right_path.end(base), right_monitor)
    lifted_system = lift.as_control_system(include_emits=True)
    semantic_universe = derived_behavior_universe(lifted_system, horizon=horizon)
    left_profile = derived_capability_profile(
        lifted_system,
        lift.node_id(left_node),
        universe=semantic_universe,
        horizon=horizon,
    )
    right_profile = derived_capability_profile(
        lifted_system,
        lift.node_id(right_node),
        universe=semantic_universe,
        horizon=horizon,
    )
    base_profiles_equal = behavior_signature(
        base, left_node.world_state, horizon
    ) == behavior_signature(base, right_node.world_state, horizon)
    current_emits_equal = canonical.emit(left_monitor) == canonical.emit(right_monitor)
    lifted_profiles_differ = left_profile != right_profile
    qualifies = base_profiles_equal and current_emits_equal and lifted_profiles_differ
    result = {
        "property_id": monitor.property_id,
        "horizon": horizon,
        "left_world_state": left_node.world_state,
        "right_world_state": right_node.world_state,
        "left_monitor_state": left_monitor,
        "right_monitor_state": right_monitor,
        "base_profiles_equal": base_profiles_equal,
        "current_emits_equal": current_emits_equal,
        "lifted_profiles_differ": lifted_profiles_differ,
        "history_residue": qualifies,
        "left_profile": sorted(left_profile),
        "right_profile": sorted(right_profile),
    }
    if canonical.safe_states is not None:
        left_actions = admissible_action_classes(lift, left_node)
        right_actions = admissible_action_classes(lift, right_node)
        result.update(
            {
                "left_admissible_action_classes": sorted(left_actions),
                "right_admissible_action_classes": sorted(right_actions),
                "admissible_actions_differ": left_actions != right_actions,
                "corridor_residue": qualifies and left_actions != right_actions,
            }
        )
    else:
        result.update(
            {
                "left_admissible_action_classes": None,
                "right_admissible_action_classes": None,
                "admissible_actions_differ": None,
                "corridor_residue": None,
            }
        )
    return result


def shared_fork_system() -> tuple[FiniteControlSystem, CertifiedObservationInterface]:
    system = FiniteControlSystem(
        system_id="canonical_process_shared_fork",
        states=("origin", "hub", "alpha_future", "beta_future"),
        actions=(
            "route_alpha",
            "route_beta",
            "choose_alpha",
            "choose_beta",
            "hold_alpha",
            "hold_beta",
        ),
        transitions=(
            ("origin", "route_alpha", "hub"),
            ("origin", "route_beta", "hub"),
            ("hub", "choose_alpha", "alpha_future"),
            ("hub", "choose_beta", "beta_future"),
            ("alpha_future", "hold_alpha", "alpha_future"),
            ("beta_future", "hold_beta", "beta_future"),
        ),
        atoms=(
            ("origin", frozenset({"origin"})),
            ("hub", frozenset({"junction"})),
            ("alpha_future", frozenset({"alpha_resource"})),
            ("beta_future", frozenset({"beta_resource"})),
        ),
    )
    observation = CertifiedObservationInterface(
        interface_id="shared_fork_observation",
        action_classes=tuple((action, action) for action in system.actions),
    )
    return system, observation


def shared_fork_histories() -> tuple[ConcretePath, ConcretePath]:
    return (
        ConcretePath(
            start="origin",
            edges=(("origin", "route_alpha", "hub"),),
        ),
        ConcretePath(
            start="origin",
            edges=(("origin", "route_beta", "hub"),),
        ),
    )


def ancestry_match_automaton(
    system: FiniteControlSystem,
    observation: CertifiedObservationInterface,
    *,
    redundant_complete_states: bool = False,
) -> PropertyAutomaton:
    alphabet = observation.alphabet(system)
    if redundant_complete_states:
        states = (
            "start",
            "alpha_pending",
            "beta_pending",
            "complete_alpha",
            "complete_beta",
            "violation",
        )
        complete_alpha = "complete_alpha"
        complete_beta = "complete_beta"
    else:
        states = ("start", "alpha_pending", "beta_pending", "complete", "violation")
        complete_alpha = "complete"
        complete_beta = "complete"
    rules = {
        ("start", "route_alpha"): "alpha_pending",
        ("start", "route_beta"): "beta_pending",
        ("alpha_pending", "choose_alpha"): complete_alpha,
        ("alpha_pending", "choose_beta"): "violation",
        ("beta_pending", "choose_alpha"): "violation",
        ("beta_pending", "choose_beta"): complete_beta,
    }
    outputs = {
        "start": frozenset(),
        "alpha_pending": frozenset({"pending"}),
        "beta_pending": frozenset({"pending"}),
        complete_alpha: frozenset({"complete"}),
        complete_beta: frozenset({"complete"}),
        "violation": frozenset({"violation"}),
    }
    safe_states = tuple(state for state in states if state != "violation")
    return _property_automaton_from_rules(
        property_id=("ancestry_match_redundant" if redundant_complete_states else "ancestry_match"),
        states=states,
        alphabet=alphabet,
        initial_state="start",
        rules=rules,
        outputs=outputs,
        safe_states=safe_states,
    )


def completion_automaton(
    system: FiniteControlSystem,
    observation: CertifiedObservationInterface,
) -> PropertyAutomaton:
    return _property_automaton_from_rules(
        property_id="completion",
        states=("start", "pending", "complete"),
        alphabet=observation.alphabet(system),
        initial_state="start",
        rules={
            ("start", "route_alpha"): "pending",
            ("start", "route_beta"): "pending",
            ("pending", "choose_alpha"): "complete",
            ("pending", "choose_beta"): "complete",
        },
        outputs={
            "start": frozenset(),
            "pending": frozenset({"pending"}),
            "complete": frozenset({"complete"}),
        },
        safe_states=("start", "pending", "complete"),
    )


def fixed_hazard_automaton(
    system: FiniteControlSystem,
    observation: CertifiedObservationInterface,
) -> PropertyAutomaton:
    return _property_automaton_from_rules(
        property_id="fixed_hazard",
        states=("start", "pending", "complete", "violation"),
        alphabet=observation.alphabet(system),
        initial_state="start",
        rules={
            ("start", "route_alpha"): "pending",
            ("start", "route_beta"): "pending",
            ("pending", "choose_alpha"): "complete",
            ("pending", "choose_beta"): "violation",
        },
        outputs={
            "start": frozenset(),
            "pending": frozenset({"pending"}),
            "complete": frozenset({"complete"}),
            "violation": frozenset({"violation"}),
        },
        safe_states=("start", "pending", "complete"),
    )


def direct_route_label_automaton(
    system: FiniteControlSystem,
    observation: CertifiedObservationInterface,
) -> PropertyAutomaton:
    return _property_automaton_from_rules(
        property_id="direct_route_label",
        states=("start", "alpha_seen", "beta_seen"),
        alphabet=observation.alphabet(system),
        initial_state="start",
        rules={
            ("start", "route_alpha"): "alpha_seen",
            ("start", "route_beta"): "beta_seen",
        },
        outputs={
            "start": frozenset(),
            "alpha_seen": frozenset({"alpha_seen"}),
            "beta_seen": frozenset({"beta_seen"}),
        },
        safe_states=None,
    )


def canonical_minimization_witness() -> dict[str, Any]:
    system, observation = shared_fork_system()
    compact = ancestry_match_automaton(system, observation)
    redundant = ancestry_match_automaton(
        system,
        observation,
        redundant_complete_states=True,
    )
    compact_payload = canonical_automaton_payload(compact)
    redundant_payload = canonical_automaton_payload(redundant)
    return {
        "compact_state_count": len(compact.states),
        "redundant_state_count": len(redundant.states),
        "compact_minimal_state_count": len(minimize_property_automaton(compact).states),
        "redundant_minimal_state_count": len(minimize_property_automaton(redundant).states),
        "canonical_payloads_equal": compact_payload == redundant_payload,
    }


def observation_equivariance_witness() -> dict[str, Any]:
    system, observation = shared_fork_system()
    state_mapping = {
        "origin": "renamed_origin",
        "hub": "renamed_hub",
        "alpha_future": "renamed_alpha_future",
        "beta_future": "renamed_beta_future",
    }
    action_mapping = {action: f"renamed_{action}" for action in system.actions}
    relabeled = system.relabel(
        state_mapping=state_mapping,
        action_mapping=action_mapping,
        system_id="shared_fork_relabeled",
    )
    transported = observation.transport_actions(
        action_mapping,
        interface_id="shared_fork_observation_relabel",
    )
    mismatches = []
    for edge in system.transitions:
        source, action, target = edge
        relabeled_edge = (
            state_mapping[source],
            action_mapping[action],
            state_mapping[target],
        )
        if observation.observe(system, edge) != transported.observe(relabeled, relabeled_edge):
            mismatches.append({"edge": repr(edge), "relabeled_edge": repr(relabeled_edge)})
    return {
        "edge_count": len(system.transitions),
        "mismatches": mismatches,
        "equivariant": not mismatches,
    }


def lifting_and_projection_witness(*, max_horizon: int = 3) -> dict[str, Any]:
    system, observation = shared_fork_system()
    monitor = minimize_property_automaton(ancestry_match_automaton(system, observation))
    lift = build_process_lift(
        system,
        monitor,
        observation,
        initial_world_state="origin",
    )
    step_failures = unique_step_lift_failures(lift)
    alpha_path, beta_path = shared_fork_histories()
    path_checks = []
    for path in (alpha_path, beta_path):
        lifted_nodes = lift_path(lift, monitor.initial_state, path)
        path_checks.append(
            {
                "edge_count": len(path.edges),
                "projected_world_states": [node.world_state for node in lifted_nodes],
                "expected_world_states": [path.start, path.end(system)],
                "projection_matches": (
                    [node.world_state for node in lifted_nodes] == [path.start, path.end(system)]
                ),
            }
        )
    projection_failures = projection_conservation_failures(
        lift,
        max_horizon=max_horizon,
    )
    return {
        "reachable_lifted_state_count": len(lift.nodes),
        "lifted_edge_count": len(lift.edges),
        "unique_step_lift_failures": step_failures,
        "path_checks": path_checks,
        "unique_path_lifting": not step_failures
        and all(row["projection_matches"] for row in path_checks),
        "projection_conservation_failures": projection_failures,
        "projection_conserved": not projection_failures,
        "max_horizon": max_horizon,
    }


def direct_emission_control_witness(*, horizon: int = 1) -> dict[str, Any]:
    system, observation = shared_fork_system()
    alpha_path, beta_path = shared_fork_histories()
    result = history_residue(
        system,
        direct_route_label_automaton(system, observation),
        observation,
        alpha_path,
        beta_path,
        horizon=horizon,
    )
    return {
        **result,
        "direct_profile_difference_visible": result["lifted_profiles_differ"],
        "direct_emission_excluded": (
            result["lifted_profiles_differ"]
            and not result["current_emits_equal"]
            and not result["history_residue"]
        ),
    }


def property_family_residue_witness(*, horizon: int = 1) -> dict[str, Any]:
    system, observation = shared_fork_system()
    alpha_path, beta_path = shared_fork_histories()
    monitors = (
        ancestry_match_automaton(system, observation),
        completion_automaton(system, observation),
        fixed_hazard_automaton(system, observation),
    )
    results = {
        monitor.property_id: history_residue(
            system,
            monitor,
            observation,
            alpha_path,
            beta_path,
            horizon=horizon,
        )
        for monitor in monitors
    }
    history_vector = {
        property_id: bool(result["history_residue"]) for property_id, result in results.items()
    }
    corridor_vector = {
        property_id: bool(result["corridor_residue"]) for property_id, result in results.items()
    }
    any_history = any(history_vector.values())
    all_history = all(history_vector.values())
    if all_history:
        classification = "family-core"
    elif any_history:
        classification = "family-dependent"
    else:
        classification = "absent"
    return {
        "horizon": horizon,
        "properties": results,
        "history_residue_vector": history_vector,
        "corridor_residue_vector": corridor_vector,
        "family_core_history_residue": all_history,
        "family_core_corridor_residue": all(corridor_vector.values()),
        "classification": classification,
        "classification_unambiguous": classification
        in {"family-core", "family-dependent", "absent"},
    }


def symmetric_copy_system() -> tuple[
    FiniteControlSystem,
    CertifiedObservationInterface,
    ConcretePath,
    ConcretePath,
]:
    system = FiniteControlSystem(
        system_id="symmetric_copy",
        states=("origin", "copy_a", "copy_b"),
        actions=("make_a", "make_b", "hold_a", "hold_b"),
        transitions=(
            ("origin", "make_a", "copy_a"),
            ("origin", "make_b", "copy_b"),
            ("copy_a", "hold_a", "copy_a"),
            ("copy_b", "hold_b", "copy_b"),
        ),
        atoms=(
            ("origin", frozenset({"origin"})),
            ("copy_a", frozenset({"copy"})),
            ("copy_b", frozenset({"copy"})),
        ),
    )
    observation = CertifiedObservationInterface(
        interface_id="symmetric_copy_observation",
        action_classes=(
            ("make_a", "make"),
            ("make_b", "make"),
            ("hold_a", "hold"),
            ("hold_b", "hold"),
        ),
    )
    return (
        system,
        observation,
        ConcretePath("origin", (("origin", "make_a", "copy_a"),)),
        ConcretePath("origin", (("origin", "make_b", "copy_b"),)),
    )


def symmetric_copy_witness(*, horizon: int = 2) -> dict[str, Any]:
    system, observation, left_path, right_path = symmetric_copy_system()
    automaton = _property_automaton_from_rules(
        property_id="symmetric_copy_property",
        states=("start", "copy_seen"),
        alphabet=observation.alphabet(system),
        initial_state="start",
        rules={("start", "make"): "copy_seen"},
        outputs={
            "start": frozenset(),
            "copy_seen": frozenset({"copy_seen"}),
        },
        safe_states=None,
    )
    result = history_residue(
        system,
        automaton,
        observation,
        left_path,
        right_path,
        horizon=horizon,
    )
    left_symbol = observation.observe(system, left_path.edges[0])
    right_symbol = observation.observe(system, right_path.edges[0])
    return {
        **result,
        "branch_observations_equal": left_symbol == right_symbol,
        "monitor_states_equal": result["left_monitor_state"] == result["right_monitor_state"],
        "verdict": "unresolved" if not result["history_residue"] else "separated",
    }


def canonical_process_monitors_summary() -> dict[str, Any]:
    observation = observation_equivariance_witness()
    minimization = canonical_minimization_witness()
    lifting = lifting_and_projection_witness()
    direct = direct_emission_control_witness()
    family = property_family_residue_witness()
    symmetric = symmetric_copy_witness()
    cases = {
        "PM1_observation_equivariance": observation["equivariant"],
        "PM2_canonical_minimization": minimization["canonical_payloads_equal"],
        "PM3_unique_lifting": lifting["unique_path_lifting"],
        "PM4_projection_conservation": lifting["projection_conserved"],
        "PM5_direct_emission_control": direct["direct_emission_excluded"],
        "PM6_property_relative_residue": all(
            result["base_profiles_equal"] and result["current_emits_equal"]
            for result in family["properties"].values()
        ),
        "PM7_symmetric_copy_unresolved": (
            symmetric["branch_observations_equal"]
            and symmetric["monitor_states_equal"]
            and symmetric["verdict"] == "unresolved"
        ),
        "PM8_family_classification": family["classification_unambiguous"],
    }
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "retained" if all(cases.values()) else "review",
        "case_results": cases,
        "cases": {
            "observation_equivariance": observation,
            "canonical_minimization": minimization,
            "lifting_and_projection": lifting,
            "direct_emission_control": direct,
            "property_family_residue": family,
            "symmetric_copy": symmetric,
        },
        "evidence_classification": {
            "instrument_correctness": [
                "PM1_observation_equivariance",
                "PM2_canonical_minimization",
                "PM3_unique_lifting",
                "PM4_projection_conservation",
                "PM5_direct_emission_control",
                "PM7_symmetric_copy_unresolved",
            ],
            "fixture_calibration": [
                "PM6_property_relative_residue",
                "PM8_family_classification",
            ],
            "risky_prediction": [],
        },
        "categorical_interpretation": (
            "The passive monitor is a finite-set functor on the concrete path "
            "category; its reachable lift is the category of elements and the "
            "projection has unique path lifting."
        ),
        "not_claimed": [
            "identity",
            "selfhood",
            "consciousness",
            "will",
            "agency",
            "valuerhood",
            "standing",
            "patienthood",
            "intrinsic continuation relevance",
            "moral license",
            "Omega validation",
        ],
    }


def case_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    correctness = set(summary["evidence_classification"]["instrument_correctness"])
    calibration = set(summary["evidence_classification"]["fixture_calibration"])
    return [
        {
            "case": case,
            "passes": passes,
            "evidence_class": (
                "instrument_correctness"
                if case in correctness
                else "fixture_calibration"
                if case in calibration
                else "unclassified"
            ),
        }
        for case, passes in summary["case_results"].items()
    ]


def residue_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    family = summary["cases"]["property_family_residue"]
    return [
        {
            "property": property_id,
            "history_residue": result["history_residue"],
            "corridor_residue": result["corridor_residue"],
            "base_profiles_equal": result["base_profiles_equal"],
            "current_emits_equal": result["current_emits_equal"],
            "lifted_profiles_differ": result["lifted_profiles_differ"],
            "left_admissible_action_classes": json.dumps(result["left_admissible_action_classes"]),
            "right_admissible_action_classes": json.dumps(
                result["right_admissible_action_classes"]
            ),
        }
        for property_id, result in family["properties"].items()
    ]


def lift_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    lifting = summary["cases"]["lifting_and_projection"]
    return [
        {
            "reachable_lifted_state_count": lifting["reachable_lifted_state_count"],
            "lifted_edge_count": lifting["lifted_edge_count"],
            "unique_step_lift_failure_count": len(lifting["unique_step_lift_failures"]),
            "projection_conservation_failure_count": len(
                lifting["projection_conservation_failures"]
            ),
            "unique_path_lifting": lifting["unique_path_lifting"],
            "projection_conserved": lifting["projection_conserved"],
        }
    ]


def _property_automaton_from_rules(
    *,
    property_id: str,
    states: tuple[str, ...],
    alphabet: tuple[ObservationSymbol, ...],
    initial_state: str,
    rules: Mapping[tuple[str, str], str],
    outputs: Mapping[str, frozenset[str]],
    safe_states: tuple[str, ...] | None,
) -> PropertyAutomaton:
    transitions = []
    for state in states:
        for symbol in alphabet:
            target = rules.get((state, symbol.action_class), state)
            transitions.append((state, symbol, target))
    return PropertyAutomaton(
        property_id=property_id,
        states=states,
        alphabet=alphabet,
        initial_state=initial_state,
        transitions=tuple(transitions),
        outputs=tuple((state, outputs[state]) for state in states),
        safe_states=safe_states,
    )
