"""Finite support systems, projection-relative order, and sector diagnostics."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, Hashable, Iterable, TypeVar


StateT = TypeVar("StateT", bound=Hashable)
MappedStateT = TypeVar("MappedStateT", bound=Hashable)
LabelT = TypeVar("LabelT", bound=Hashable)
MappedLabelT = TypeVar("MappedLabelT", bound=Hashable)

TransitionRow = tuple[StateT, LabelT, StateT]


def _ordered_unique(values: Iterable[StateT]) -> tuple[StateT, ...]:
    return tuple(dict.fromkeys(values))


@dataclass(frozen=True)
class FiniteTransitionSystem(Generic[StateT, LabelT]):
    """A finite labelled transition relation with no totality assumption."""

    system_id: str
    states: tuple[StateT, ...]
    labels: tuple[LabelT, ...]
    transitions: tuple[TransitionRow[StateT, LabelT], ...]

    def __post_init__(self) -> None:
        if not self.system_id:
            raise ValueError("system_id must be nonempty")
        if not self.states or len(self.states) != len(set(self.states)):
            raise ValueError("states must be nonempty and unique")
        if len(self.labels) != len(set(self.labels)):
            raise ValueError("labels must be unique")
        if len(self.transitions) != len(set(self.transitions)):
            raise ValueError("transition rows must be unique")

        state_set = set(self.states)
        label_set = set(self.labels)
        for source, label, target in self.transitions:
            if source not in state_set or target not in state_set:
                raise ValueError("transition references an unknown state")
            if label not in label_set:
                raise ValueError("transition references an unknown label")

    def require_state(self, state: StateT) -> None:
        if state not in self.states:
            raise KeyError(state)

    def outgoing(self, state: StateT) -> tuple[TransitionRow[StateT, LabelT], ...]:
        self.require_state(state)
        return tuple(row for row in self.transitions if row[0] == state)

    def incoming(self, state: StateT) -> tuple[TransitionRow[StateT, LabelT], ...]:
        self.require_state(state)
        return tuple(row for row in self.transitions if row[2] == state)

    def successors(
        self,
        state: StateT,
        label: LabelT | None = None,
    ) -> tuple[StateT, ...]:
        rows = self.outgoing(state)
        if label is not None:
            if label not in self.labels:
                raise KeyError(label)
            rows = tuple(row for row in rows if row[1] == label)
        return _ordered_unique(target for _source, _label, target in rows)

    def predecessors(self, state: StateT) -> tuple[StateT, ...]:
        return _ordered_unique(source for source, _label, _target in self.incoming(state))

    def has_transition(self, source: StateT, label: LabelT, target: StateT) -> bool:
        return (source, label, target) in self.transitions

    def reachable_from(
        self,
        start: StateT,
        *,
        transitions: Iterable[TransitionRow[StateT, LabelT]] | None = None,
    ) -> tuple[StateT, ...]:
        """Return reflexive reachability in declared state order."""

        self.require_state(start)
        retained = self.transitions if transitions is None else tuple(transitions)
        allowed = set(retained)
        if not allowed <= set(self.transitions):
            raise ValueError("reachability transition set must be a subsystem")

        seen = {start}
        frontier = [start]
        while frontier:
            source = frontier.pop(0)
            for row in self.outgoing(source):
                if row not in allowed:
                    continue
                target = row[2]
                if target not in seen:
                    seen.add(target)
                    frontier.append(target)
        return tuple(state for state in self.states if state in seen)

    def is_reachable(
        self,
        source: StateT,
        target: StateT,
        *,
        transitions: Iterable[TransitionRow[StateT, LabelT]] | None = None,
    ) -> bool:
        return target in self.reachable_from(source, transitions=transitions)


class ProjectionPolarity(StrEnum):
    NULL = "NULL"
    POSITIVE_ONLY = "POSITIVE_ONLY"
    NEGATIVE_ONLY = "NEGATIVE_ONLY"
    BIDIRECTIONAL = "BIDIRECTIONAL"


@dataclass(frozen=True)
class FiniteProjection(Generic[StateT]):
    """A total integer-valued projection on one finite state interface."""

    projection_id: str
    states: tuple[StateT, ...]
    rows: tuple[tuple[StateT, int], ...]

    def __post_init__(self) -> None:
        if not self.projection_id:
            raise ValueError("projection_id must be nonempty")
        if not self.states or len(self.states) != len(set(self.states)):
            raise ValueError("projection states must be nonempty and unique")
        sources = tuple(state for state, _level in self.rows)
        if len(sources) != len(set(sources)):
            raise ValueError("projection rows must be functional")
        if set(sources) != set(self.states):
            raise ValueError("projection must be total on its state interface")

    @property
    def level_map(self) -> dict[StateT, int]:
        return dict(self.rows)

    def level(self, state: StateT) -> int:
        try:
            return self.level_map[state]
        except KeyError as exc:
            raise KeyError(state) from exc

    def validate(self, system: FiniteTransitionSystem[StateT, object]) -> None:
        if set(self.states) != set(system.states):
            raise ValueError("projection and system state interfaces must match")


def positive_transitions(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[TransitionRow[StateT, LabelT], ...]:
    projection.validate(system)
    return tuple(
        row for row in system.transitions if projection.level(row[0]) < projection.level(row[2])
    )


def negative_transitions(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[TransitionRow[StateT, LabelT], ...]:
    projection.validate(system)
    return tuple(
        row for row in system.transitions if projection.level(row[2]) < projection.level(row[0])
    )


def level_transitions(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[TransitionRow[StateT, LabelT], ...]:
    projection.validate(system)
    return tuple(
        row for row in system.transitions if projection.level(row[0]) == projection.level(row[2])
    )


def nondecreasing_transitions(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[TransitionRow[StateT, LabelT], ...]:
    projection.validate(system)
    return tuple(
        row for row in system.transitions if projection.level(row[0]) <= projection.level(row[2])
    )


def projected_reachable_from(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
    start: StateT,
) -> tuple[StateT, ...]:
    return system.reachable_from(
        start,
        transitions=nondecreasing_transitions(system, projection),
    )


def projected_reachability_rows(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[tuple[StateT, StateT], ...]:
    return tuple(
        (source, target)
        for source in system.states
        for target in projected_reachable_from(system, projection, source)
    )


def projected_reachability_is_preorder(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> bool:
    rows = set(projected_reachability_rows(system, projection))
    reflexive = all((state, state) in rows for state in system.states)
    transitive = all(
        (left, right) in rows
        for left, middle in rows
        for source, right in rows
        if middle == source
    )
    return reflexive and transitive


def mutual_projected_reachability_rows(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[tuple[StateT, StateT], ...]:
    reachability = set(projected_reachability_rows(system, projection))
    return tuple(
        (left, right)
        for left in system.states
        for right in system.states
        if (left, right) in reachability and (right, left) in reachability
    )


def mutual_projected_reachability_is_equivalence(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> bool:
    rows = set(mutual_projected_reachability_rows(system, projection))
    reflexive = all((state, state) in rows for state in system.states)
    symmetric = all((right, left) in rows for left, right in rows)
    transitive = all(
        (left, right) in rows
        for left, middle in rows
        for source, right in rows
        if middle == source
    )
    return reflexive and symmetric and transitive


def _strongly_connected_components(
    system: FiniteTransitionSystem[StateT, LabelT],
    transitions: Iterable[TransitionRow[StateT, LabelT]] | None = None,
) -> tuple[tuple[StateT, ...], ...]:
    retained = system.transitions if transitions is None else tuple(transitions)
    allowed = set(retained)
    if not allowed <= set(system.transitions):
        raise ValueError("component transition set must be a subsystem")

    outgoing = {
        state: tuple(
            target
            for source, _label, target in retained
            if source == state
        )
        for state in system.states
    }
    incoming = {
        state: tuple(
            source
            for source, _label, target in retained
            if target == state
        )
        for state in system.states
    }

    visited: set[StateT] = set()
    finish_order: list[StateT] = []

    def visit_forward(state: StateT) -> None:
        if state in visited:
            return
        visited.add(state)
        for target in outgoing[state]:
            visit_forward(target)
        finish_order.append(state)

    for state in system.states:
        visit_forward(state)

    visited.clear()
    components: list[tuple[StateT, ...]] = []

    def visit_reverse(state: StateT, retained_states: set[StateT]) -> None:
        if state in visited:
            return
        visited.add(state)
        retained_states.add(state)
        for source in incoming[state]:
            visit_reverse(source, retained_states)

    for state in reversed(finish_order):
        if state in visited:
            continue
        component_states: set[StateT] = set()
        visit_reverse(state, component_states)
        components.append(
            tuple(candidate for candidate in system.states if candidate in component_states)
        )

    state_index = {state: index for index, state in enumerate(system.states)}
    return tuple(
        sorted(
            components,
            key=lambda component: min(state_index[state] for state in component),
        )
    )


def projected_components(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[tuple[StateT, ...], ...]:
    return _strongly_connected_components(
        system,
        nondecreasing_transitions(system, projection),
    )


def projected_condensation_edges(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> tuple[tuple[int, int], ...]:
    components = projected_components(system, projection)
    component_of = {
        state: index for index, component in enumerate(components) for state in component
    }
    edges = {
        (component_of[source], component_of[target])
        for source, _label, target in nondecreasing_transitions(system, projection)
        if component_of[source] != component_of[target]
    }
    return tuple(sorted(edges))


def _has_directed_cycle(vertex_count: int, edges: Iterable[tuple[int, int]]) -> bool:
    outgoing = {vertex: [] for vertex in range(vertex_count)}
    for source, target in edges:
        outgoing[source].append(target)

    visiting: set[int] = set()
    visited: set[int] = set()

    def visit(vertex: int) -> bool:
        if vertex in visiting:
            return True
        if vertex in visited:
            return False
        visiting.add(vertex)
        if any(visit(target) for target in outgoing[vertex]):
            return True
        visiting.remove(vertex)
        visited.add(vertex)
        return False

    return any(visit(vertex) for vertex in range(vertex_count))


@dataclass(frozen=True)
class ProjectionProfile(Generic[StateT]):
    polarity: ProjectionPolarity
    positive_transition_count: int
    negative_transition_count: int
    level_transition_count: int
    janus_sources: tuple[StateT, ...]
    projected_component_count: int
    projected_source_component_count: int
    projected_sink_component_count: int
    condensation_acyclic: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "polarity": self.polarity.value,
            "positive_transition_count": self.positive_transition_count,
            "negative_transition_count": self.negative_transition_count,
            "level_transition_count": self.level_transition_count,
            "janus_sources": [repr(state) for state in self.janus_sources],
            "projected_component_count": self.projected_component_count,
            "projected_source_component_count": self.projected_source_component_count,
            "projected_sink_component_count": self.projected_sink_component_count,
            "condensation_acyclic": self.condensation_acyclic,
        }


def projection_profile(
    system: FiniteTransitionSystem[StateT, LabelT],
    projection: FiniteProjection[StateT],
) -> ProjectionProfile[StateT]:
    positive = positive_transitions(system, projection)
    negative = negative_transitions(system, projection)
    level = level_transitions(system, projection)
    if positive and negative:
        polarity = ProjectionPolarity.BIDIRECTIONAL
    elif positive:
        polarity = ProjectionPolarity.POSITIVE_ONLY
    elif negative:
        polarity = ProjectionPolarity.NEGATIVE_ONLY
    else:
        polarity = ProjectionPolarity.NULL

    janus_sources = tuple(
        state
        for state in system.states
        if any(row[0] == state for row in positive)
        and any(row[0] == state for row in negative)
    )

    components = projected_components(system, projection)
    condensation_edges = projected_condensation_edges(system, projection)
    sources = set(range(len(components)))
    sinks = set(range(len(components)))
    for source, target in condensation_edges:
        sinks.discard(source)
        sources.discard(target)

    return ProjectionProfile(
        polarity=polarity,
        positive_transition_count=len(positive),
        negative_transition_count=len(negative),
        level_transition_count=len(level),
        janus_sources=janus_sources,
        projected_component_count=len(components),
        projected_source_component_count=len(sources),
        projected_sink_component_count=len(sinks),
        condensation_acyclic=not _has_directed_cycle(
            len(components),
            condensation_edges,
        ),
    )


@dataclass(frozen=True, order=True)
class FiniteHistory(Generic[StateT, LabelT]):
    """One exact finite labelled history."""

    states: tuple[StateT, ...]
    labels: tuple[LabelT, ...]

    def __post_init__(self) -> None:
        if not self.states:
            raise ValueError("history must contain at least one state")
        if len(self.states) != len(self.labels) + 1:
            raise ValueError("a history with n labels must contain n + 1 states")

    def validate(self, system: FiniteTransitionSystem[StateT, LabelT]) -> None:
        for index, label in enumerate(self.labels):
            if not system.has_transition(
                self.states[index],
                label,
                self.states[index + 1],
            ):
                raise ValueError("history contains a transition outside the system")

    def projected_levels(self, projection: FiniteProjection[StateT]) -> tuple[int, ...]:
        return tuple(projection.level(state) for state in self.states)


@dataclass(frozen=True)
class FiniteSystemIsomorphism(
    Generic[StateT, MappedStateT, LabelT, MappedLabelT]
):
    """An explicit state/label relabeling preserving every transition row."""

    isomorphism_id: str
    state_rows: tuple[tuple[StateT, MappedStateT], ...]
    label_rows: tuple[tuple[LabelT, MappedLabelT], ...]

    @property
    def state_map(self) -> dict[StateT, MappedStateT]:
        return dict(self.state_rows)

    @property
    def label_map(self) -> dict[LabelT, MappedLabelT]:
        return dict(self.label_rows)

    def validate(
        self,
        source: FiniteTransitionSystem[StateT, LabelT],
        target: FiniteTransitionSystem[MappedStateT, MappedLabelT],
    ) -> None:
        if not self.isomorphism_id:
            raise ValueError("isomorphism_id must be nonempty")
        if set(self.state_map) != set(source.states):
            raise ValueError("state map must be total on source states")
        if set(self.state_map.values()) != set(target.states):
            raise ValueError("state map must be bijective onto target states")
        if len(self.state_rows) != len(self.state_map):
            raise ValueError("state map must be functional")
        if len(self.state_map.values()) != len(set(self.state_map.values())):
            raise ValueError("state map must be injective")
        if set(self.label_map) != set(source.labels):
            raise ValueError("label map must be total on source labels")
        if set(self.label_map.values()) != set(target.labels):
            raise ValueError("label map must be bijective onto target labels")
        if len(self.label_rows) != len(self.label_map):
            raise ValueError("label map must be functional")
        if len(self.label_map.values()) != len(set(self.label_map.values())):
            raise ValueError("label map must be injective")

        mapped_transitions = {
            (
                self.state_map[source_state],
                self.label_map[label],
                self.state_map[target_state],
            )
            for source_state, label, target_state in source.transitions
        }
        if mapped_transitions != set(target.transitions):
            raise ValueError("isomorphism must preserve and reflect transitions")

    def map_history(
        self,
        history: FiniteHistory[StateT, LabelT],
    ) -> FiniteHistory[MappedStateT, MappedLabelT]:
        return FiniteHistory(
            states=tuple(self.state_map[state] for state in history.states),
            labels=tuple(self.label_map[label] for label in history.labels),
        )


def histories_exactly_equal(
    left: FiniteHistory[StateT, LabelT],
    right: FiniteHistory[StateT, LabelT],
) -> bool:
    """Test equality without quotienting states, labels, or order."""

    return left == right


def histories_relabeling_equivalent(
    source: FiniteTransitionSystem[StateT, LabelT],
    target: FiniteTransitionSystem[MappedStateT, MappedLabelT],
    isomorphism: FiniteSystemIsomorphism[
        StateT,
        MappedStateT,
        LabelT,
        MappedLabelT,
    ],
    left: FiniteHistory[StateT, LabelT],
    right: FiniteHistory[MappedStateT, MappedLabelT],
) -> bool:
    """Test history equality after one declared system isomorphism."""

    isomorphism.validate(source, target)
    left.validate(source)
    right.validate(target)
    return isomorphism.map_history(left) == right


def histories_project_to_same_levels(
    left: FiniteHistory[StateT, LabelT],
    left_projection: FiniteProjection[StateT],
    right: FiniteHistory[MappedStateT, MappedLabelT],
    right_projection: FiniteProjection[MappedStateT],
) -> bool:
    """Compare only the declared projection-level sequences."""

    return (
        left.projected_levels(left_projection)
        == right.projected_levels(right_projection)
    )


@dataclass(frozen=True)
class DeclaredIndependence(Generic[LabelT]):
    """A finite symmetric, irreflexive declaration of independent labels."""

    labels: tuple[LabelT, ...]
    pairs: tuple[tuple[LabelT, LabelT], ...]

    def __post_init__(self) -> None:
        if len(self.labels) != len(set(self.labels)):
            raise ValueError("independence labels must be unique")
        retained: set[frozenset[LabelT]] = set()
        for left, right in self.pairs:
            if left not in self.labels or right not in self.labels:
                raise ValueError("independence pair references an unknown label")
            if left == right:
                raise ValueError("independence must be irreflexive")
            key = frozenset((left, right))
            if key in retained:
                raise ValueError("independence pairs must be unique up to symmetry")
            retained.add(key)

    def independent(self, left: LabelT, right: LabelT) -> bool:
        return any(
            (left == declared_left and right == declared_right)
            or (left == declared_right and right == declared_left)
            for declared_left, declared_right in self.pairs
        )


@dataclass(frozen=True)
class CommutingDiamond(Generic[StateT, LabelT]):
    source: StateT
    left_label: LabelT
    right_label: LabelT
    left_state: StateT
    right_state: StateT
    target: StateT

    @property
    def left_history(self) -> FiniteHistory[StateT, LabelT]:
        return FiniteHistory(
            states=(self.source, self.left_state, self.target),
            labels=(self.left_label, self.right_label),
        )

    @property
    def right_history(self) -> FiniteHistory[StateT, LabelT]:
        return FiniteHistory(
            states=(self.source, self.right_state, self.target),
            labels=(self.right_label, self.left_label),
        )


@dataclass(frozen=True)
class DiamondFailure(Generic[StateT, LabelT]):
    source: StateT
    left_label: LabelT
    right_label: LabelT
    left_state: StateT
    right_state: StateT


@dataclass(frozen=True)
class DiamondAudit(Generic[StateT, LabelT]):
    opportunities: int
    diamonds: tuple[CommutingDiamond[StateT, LabelT], ...]
    failures: tuple[DiamondFailure[StateT, LabelT], ...]


def histories_commute_in_audited_diamond(
    left: FiniteHistory[StateT, LabelT],
    right: FiniteHistory[StateT, LabelT],
    audit: DiamondAudit[StateT, LabelT],
) -> bool:
    """Test whether two length-two histories are opposite sides of a diamond."""

    return any(
        (
            left == diamond.left_history
            and right == diamond.right_history
        )
        or (
            left == diamond.right_history
            and right == diamond.left_history
        )
        for diamond in audit.diamonds
    )


def audit_commuting_diamonds(
    system: FiniteTransitionSystem[StateT, LabelT],
    independence: DeclaredIndependence[LabelT],
) -> DiamondAudit[StateT, LabelT]:
    if set(independence.labels) != set(system.labels):
        raise ValueError("independence and system label interfaces must match")

    diamonds: list[CommutingDiamond[StateT, LabelT]] = []
    failures: list[DiamondFailure[StateT, LabelT]] = []
    opportunities = 0
    for source in system.states:
        for left_label, right_label in independence.pairs:
            for left_state in system.successors(source, left_label):
                for right_state in system.successors(source, right_label):
                    opportunities += 1
                    left_targets = set(system.successors(left_state, right_label))
                    right_targets = set(system.successors(right_state, left_label))
                    closing_targets = left_targets & right_targets
                    if not closing_targets:
                        failures.append(
                            DiamondFailure(
                                source=source,
                                left_label=left_label,
                                right_label=right_label,
                                left_state=left_state,
                                right_state=right_state,
                            )
                        )
                    for target in system.states:
                        if target in closing_targets:
                            diamonds.append(
                                CommutingDiamond(
                                    source=source,
                                    left_label=left_label,
                                    right_label=right_label,
                                    left_state=left_state,
                                    right_state=right_state,
                                    target=target,
                                )
                            )
    return DiamondAudit(
        opportunities=opportunities,
        diamonds=tuple(diamonds),
        failures=tuple(failures),
    )


def _recurrent_components(
    system: FiniteTransitionSystem[StateT, LabelT],
) -> tuple[tuple[StateT, ...], ...]:
    components = _strongly_connected_components(system)
    self_loop_states = {
        source
        for source, _label, target in system.transitions
        if source == target
    }
    return tuple(
        component
        for component in components
        if len(component) > 1 or component[0] in self_loop_states
    )


def _extendable_states(
    system: FiniteTransitionSystem[StateT, LabelT],
    horizon: int,
) -> tuple[StateT, ...]:
    if horizon < 0:
        raise ValueError("extendability horizon must be nonnegative")
    retained = set(system.states)
    for _step in range(horizon):
        retained = {
            state
            for state in system.states
            if any(target in retained for target in system.successors(state))
        }
    return tuple(state for state in system.states if state in retained)


def _joinability_failures(
    system: FiniteTransitionSystem[StateT, LabelT],
    *,
    local: bool,
) -> tuple[tuple[StateT, StateT, StateT], ...]:
    reachable = {
        state: set(system.reachable_from(state)) for state in system.states
    }
    failures = []
    for source in system.states:
        candidates = (
            system.successors(source)
            if local
            else system.reachable_from(source)
        )
        for left, right in itertools.combinations(candidates, 2):
            if not (reachable[left] & reachable[right]):
                failures.append((source, left, right))
    return tuple(failures)


@dataclass(frozen=True)
class SectorProfile(Generic[StateT]):
    state_count: int
    transition_count: int
    branching_state_count: int
    source_state_count: int
    sink_state_count: int
    directed_cycle_present: bool
    terminating: bool
    recurrent_components: tuple[tuple[StateT, ...], ...]
    extendability_horizon: int
    extendable_states: tuple[StateT, ...]
    locally_confluent: bool
    globally_confluent: bool
    local_confluence_failures: tuple[tuple[StateT, StateT, StateT], ...]
    global_confluence_failures: tuple[tuple[StateT, StateT, StateT], ...]
    declared_independent_pair_count: int
    commuting_diamond_count: int
    commuting_diamond_failure_count: int

    def as_dict(self) -> dict[str, object]:
        return {
            "state_count": self.state_count,
            "transition_count": self.transition_count,
            "branching_state_count": self.branching_state_count,
            "source_state_count": self.source_state_count,
            "sink_state_count": self.sink_state_count,
            "directed_cycle_present": self.directed_cycle_present,
            "terminating": self.terminating,
            "recurrent_components": [
                [repr(state) for state in component]
                for component in self.recurrent_components
            ],
            "extendability_horizon": self.extendability_horizon,
            "extendable_states": [repr(state) for state in self.extendable_states],
            "locally_confluent": self.locally_confluent,
            "globally_confluent": self.globally_confluent,
            "local_confluence_failure_count": len(self.local_confluence_failures),
            "global_confluence_failure_count": len(self.global_confluence_failures),
            "declared_independent_pair_count": self.declared_independent_pair_count,
            "commuting_diamond_count": self.commuting_diamond_count,
            "commuting_diamond_failure_count": self.commuting_diamond_failure_count,
        }


def sector_profile(
    system: FiniteTransitionSystem[StateT, LabelT],
    *,
    horizon: int,
    independence: DeclaredIndependence[LabelT] | None = None,
) -> SectorProfile[StateT]:
    if independence is None:
        independence = DeclaredIndependence(labels=system.labels, pairs=())
    diamond_audit = audit_commuting_diamonds(system, independence)
    recurrent = _recurrent_components(system)
    local_failures = _joinability_failures(system, local=True)
    global_failures = _joinability_failures(system, local=False)

    return SectorProfile(
        state_count=len(system.states),
        transition_count=len(system.transitions),
        branching_state_count=sum(
            len(system.successors(state)) > 1 for state in system.states
        ),
        source_state_count=sum(not system.incoming(state) for state in system.states),
        sink_state_count=sum(not system.outgoing(state) for state in system.states),
        directed_cycle_present=bool(recurrent),
        terminating=not recurrent,
        recurrent_components=recurrent,
        extendability_horizon=horizon,
        extendable_states=_extendable_states(system, horizon),
        locally_confluent=not local_failures,
        globally_confluent=not global_failures,
        local_confluence_failures=local_failures,
        global_confluence_failures=global_failures,
        declared_independent_pair_count=len(independence.pairs),
        commuting_diamond_count=len(diamond_audit.diamonds),
        commuting_diamond_failure_count=len(diamond_audit.failures),
    )
