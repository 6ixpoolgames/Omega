"""Finite causal profiling and set identification for process interfaces."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, Mapping

from omega_v2.finite.controllers import (
    FiniteStateController,
    compile_closed_loop,
)
from omega_v2.finite.model import ControlledMarkovSystem


Bit = int
BinaryState = tuple[Bit, ...]


def _binary_states(width: int) -> tuple[BinaryState, ...]:
    return tuple(itertools.product((0, 1), repeat=width))


def _component_subsets(
    component_ids: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    return tuple(
        subset
        for size in range(1, len(component_ids))
        for subset in itertools.combinations(component_ids, size)
    )


def _projection(
    state: BinaryState,
    indices: tuple[int, ...],
) -> tuple[Bit, ...]:
    return tuple(state[index] for index in indices)


@dataclass(frozen=True)
class BinarySynchronousSystem:
    """A total deterministic synchronous map over a complete Boolean product."""

    system_id: str
    component_ids: tuple[str, ...]
    transition_rows: tuple[tuple[BinaryState, BinaryState], ...]
    initial_states: tuple[BinaryState, ...]
    state_atoms: tuple[tuple[BinaryState, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.system_id:
            raise ValueError("system_id must be nonempty")
        if len(self.component_ids) < 2 or len(self.component_ids) != len(
            set(self.component_ids)
        ):
            raise ValueError(
                "component identifiers must contain at least two unique values"
            )
        if any(not component for component in self.component_ids):
            raise ValueError("component identifiers must be nonempty")

        states = set(self.states)
        sources = tuple(source for source, _target in self.transition_rows)
        if len(sources) != len(set(sources)) or set(sources) != states:
            raise ValueError(
                "transition rows must be total and functional on the Boolean product"
            )
        if any(target not in states for _source, target in self.transition_rows):
            raise ValueError("transition rows contain a malformed target state")
        if not self.initial_states or len(self.initial_states) != len(
            set(self.initial_states)
        ):
            raise ValueError("initial states must be nonempty and unique")
        if not set(self.initial_states) <= states:
            raise ValueError("initial support contains a malformed state")
        if len(self.state_atoms) != len(set(self.state_atoms)):
            raise ValueError("state annotations must be unique")
        if any(
            state not in states or not atom
            for state, atom in self.state_atoms
        ):
            raise ValueError("state annotations must reference known states")

    @classmethod
    def from_update_function(
        cls,
        *,
        system_id: str,
        component_ids: tuple[str, ...],
        update: Callable[[BinaryState], BinaryState],
        initial_states: Iterable[BinaryState],
        state_atoms: Iterable[tuple[BinaryState, str]] = (),
    ) -> BinarySynchronousSystem:
        states = _binary_states(len(component_ids))
        return cls(
            system_id=system_id,
            component_ids=component_ids,
            transition_rows=tuple((state, update(state)) for state in states),
            initial_states=tuple(initial_states),
            state_atoms=tuple(state_atoms),
        )

    @property
    def states(self) -> tuple[BinaryState, ...]:
        return _binary_states(len(self.component_ids))

    @property
    def transition_map(self) -> dict[BinaryState, BinaryState]:
        return dict(self.transition_rows)

    @property
    def component_index(self) -> dict[str, int]:
        return {
            component: index
            for index, component in enumerate(self.component_ids)
        }

    def step(self, state: BinaryState) -> BinaryState:
        try:
            return self.transition_map[state]
        except KeyError as exc:
            raise KeyError(state) from exc

    def intervene_source(
        self,
        state: BinaryState,
        component: str,
        value: Bit,
    ) -> BinaryState:
        if value not in (0, 1):
            raise ValueError("intervention values must be Boolean")
        try:
            index = self.component_index[component]
        except KeyError as exc:
            raise KeyError(component) from exc
        values = list(state)
        values[index] = value
        return tuple(values)

    def states_by_depth(self, horizon: int) -> tuple[frozenset[BinaryState], ...]:
        if horizon <= 0:
            raise ValueError("horizon must be positive")
        levels = [frozenset(self.initial_states)]
        for _depth in range(horizon):
            levels.append(frozenset(self.step(state) for state in levels[-1]))
        return tuple(levels)

    def reachable_states(self) -> frozenset[BinaryState]:
        reached = set(self.initial_states)
        frontier = list(self.initial_states)
        while frontier:
            state = frontier.pop()
            target = self.step(state)
            if target not in reached:
                reached.add(target)
                frontier.append(target)
        return frozenset(reached)

    def reachable_recurrent_states(self) -> frozenset[BinaryState]:
        reached = self.reachable_states()
        recurrent: set[BinaryState] = set()
        for start in reached:
            path: list[BinaryState] = []
            first_index: dict[BinaryState, int] = {}
            current = start
            while current not in first_index:
                first_index[current] = len(path)
                path.append(current)
                current = self.step(current)
            recurrent.update(path[first_index[current] :])
        return frozenset(recurrent)

    def rename_components(
        self,
        renaming: Mapping[str, str],
        *,
        system_id: str | None = None,
    ) -> BinarySynchronousSystem:
        if set(renaming) != set(self.component_ids):
            raise ValueError("renaming must cover every component")
        renamed = tuple(renaming[item] for item in self.component_ids)
        if len(renamed) != len(set(renamed)) or any(not item for item in renamed):
            raise ValueError("renaming targets must be nonempty and unique")
        return BinarySynchronousSystem(
            system_id=system_id or f"{self.system_id}__renamed",
            component_ids=renamed,
            transition_rows=self.transition_rows,
            initial_states=self.initial_states,
            state_atoms=self.state_atoms,
        )

    def with_state_atom(
        self,
        atom: str,
        *,
        states: Iterable[BinaryState] | None = None,
        system_id: str | None = None,
    ) -> BinarySynchronousSystem:
        selected = self.states if states is None else tuple(states)
        return BinarySynchronousSystem(
            system_id=system_id or f"{self.system_id}__annotated",
            component_ids=self.component_ids,
            transition_rows=self.transition_rows,
            initial_states=self.initial_states,
            state_atoms=(
                *self.state_atoms,
                *((state, atom) for state in selected),
            ),
        )


@dataclass(frozen=True)
class InfluenceWitness:
    source_component: str
    target_component: str
    source_state: BinaryState
    intervened_state: BinaryState
    source_next_value: Bit
    intervened_next_value: Bit

    def as_dict(self) -> dict[str, object]:
        return {
            "source_component": self.source_component,
            "target_component": self.target_component,
            "source_state": list(self.source_state),
            "intervened_state": list(self.intervened_state),
            "source_next_value": self.source_next_value,
            "intervened_next_value": self.intervened_next_value,
        }


def coordinate_influence_witnesses(
    system: BinarySynchronousSystem,
) -> tuple[InfluenceWitness, ...]:
    """Return one exact source-intervention witness per influence edge."""

    witnesses: list[InfluenceWitness] = []
    for source_component in system.component_ids:
        source_index = system.component_index[source_component]
        for target_component in system.component_ids:
            target_index = system.component_index[target_component]
            retained: InfluenceWitness | None = None
            for state in system.states:
                intervened = system.intervene_source(
                    state,
                    source_component,
                    1 - state[source_index],
                )
                source_value = system.step(state)[target_index]
                intervened_value = system.step(intervened)[target_index]
                if source_value != intervened_value:
                    retained = InfluenceWitness(
                        source_component=source_component,
                        target_component=target_component,
                        source_state=state,
                        intervened_state=intervened,
                        source_next_value=source_value,
                        intervened_next_value=intervened_value,
                    )
                    break
            if retained is not None:
                witnesses.append(retained)
    return tuple(witnesses)


@dataclass(frozen=True)
class ContinuationInfluenceWitness:
    interface: tuple[str, ...]
    component: str
    source_state: BinaryState
    intervened_state: BinaryState
    baseline_outside_trace: tuple[tuple[Bit, ...], ...]
    intervened_outside_trace: tuple[tuple[Bit, ...], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "interface": list(self.interface),
            "component": self.component,
            "source_state": list(self.source_state),
            "intervened_state": list(self.intervened_state),
            "baseline_outside_trace": [
                list(state) for state in self.baseline_outside_trace
            ],
            "intervened_outside_trace": [
                list(state) for state in self.intervened_outside_trace
            ],
        }


class EvidenceMode(str, Enum):
    OBSERVATIONAL = "observational"
    INTERVENTIONAL = "interventional"


FEATURE_FIELDS = (
    "persistent_variation",
    "internal_influence",
    "incoming_influence",
    "outgoing_influence",
    "latent_state_multiplicity",
    "record_acquisition",
    "record_sensitive_outflow",
    "continuation_influence",
)


@dataclass(frozen=True)
class ProcessInterfaceProfile:
    """Feature profile for one component subset under one evidence mode."""

    interface: tuple[str, ...]
    outside: tuple[str, ...]
    evidence_mode: EvidenceMode
    persistent_variation: bool
    internal_influence: bool | None
    incoming_influence: bool | None
    outgoing_influence: bool | None
    latent_state_multiplicity: bool
    record_acquisition: bool | None
    record_sensitive_outflow: bool | None
    continuation_influence: bool | None
    continuation_witness: ContinuationInfluenceWitness | None

    @property
    def interface_id(self) -> str:
        return "{" + ",".join(self.interface) + "}"

    def feature(self, name: str) -> bool | None:
        if name not in FEATURE_FIELDS:
            raise KeyError(name)
        value = getattr(self, name)
        if not isinstance(value, bool) and value is not None:
            raise TypeError(f"{name} is not a truth-valued feature")
        return value

    def structural_signature(self) -> tuple[bool | None, ...]:
        return tuple(self.feature(name) for name in FEATURE_FIELDS)

    def as_dict(self) -> dict[str, object]:
        return {
            "interface_id": self.interface_id,
            "interface": list(self.interface),
            "outside": list(self.outside),
            "evidence_mode": self.evidence_mode.value,
            **{
                name: (
                    "UNKNOWN"
                    if self.feature(name) is None
                    else self.feature(name)
                )
                for name in FEATURE_FIELDS
            },
            "continuation_witness": (
                self.continuation_witness.as_dict()
                if self.continuation_witness is not None
                else None
            ),
        }


def _interface_indices(
    system: BinarySynchronousSystem,
    interface: Iterable[str],
) -> tuple[tuple[str, ...], tuple[int, ...], tuple[str, ...], tuple[int, ...]]:
    retained = tuple(sorted(set(interface), key=system.component_ids.index))
    if not retained or not set(retained) < set(system.component_ids):
        raise ValueError("an interface must be a nonempty proper component subset")
    inside_indices = tuple(system.component_index[item] for item in retained)
    outside = tuple(
        item for item in system.component_ids if item not in retained
    )
    outside_indices = tuple(system.component_index[item] for item in outside)
    return retained, inside_indices, outside, outside_indices


def _has_latent_state_multiplicity(
    system: BinarySynchronousSystem,
    inside_indices: tuple[int, ...],
    outside_indices: tuple[int, ...],
    *,
    horizon: int,
) -> bool:
    reached_after_update = set().union(*system.states_by_depth(horizon)[1:])
    by_outside: dict[tuple[Bit, ...], set[tuple[Bit, ...]]] = {}
    for state in reached_after_update:
        by_outside.setdefault(
            _projection(state, outside_indices),
            set(),
        ).add(_projection(state, inside_indices))
    return any(len(inside_values) > 1 for inside_values in by_outside.values())


def _has_record_sensitive_outflow(
    system: BinarySynchronousSystem,
    inside_indices: tuple[int, ...],
    outside_indices: tuple[int, ...],
    *,
    horizon: int,
) -> bool:
    reached_after_update = tuple(
        set().union(*system.states_by_depth(horizon)[1:])
    )
    for left, right in itertools.combinations(reached_after_update, 2):
        if _projection(left, outside_indices) != _projection(
            right,
            outside_indices,
        ):
            continue
        if _projection(left, inside_indices) == _projection(
            right,
            inside_indices,
        ):
            continue
        if _projection(system.step(left), outside_indices) != _projection(
            system.step(right),
            outside_indices,
        ):
            return True
    return False


def _outside_trace(
    system: BinarySynchronousSystem,
    state: BinaryState,
    outside_indices: tuple[int, ...],
    *,
    horizon: int,
) -> tuple[tuple[Bit, ...], ...]:
    trace = []
    current = state
    for _step in range(horizon):
        current = system.step(current)
        trace.append(_projection(current, outside_indices))
    return tuple(trace)


def _continuation_influence_witness(
    system: BinarySynchronousSystem,
    interface: tuple[str, ...],
    outside_indices: tuple[int, ...],
    *,
    horizon: int,
) -> ContinuationInfluenceWitness | None:
    for source in sorted(system.reachable_states()):
        for component in interface:
            index = system.component_index[component]
            intervened = system.intervene_source(
                source,
                component,
                1 - source[index],
            )
            baseline_trace = _outside_trace(
                system,
                source,
                outside_indices,
                horizon=horizon,
            )
            intervened_trace = _outside_trace(
                system,
                intervened,
                outside_indices,
                horizon=horizon,
            )
            if baseline_trace != intervened_trace:
                return ContinuationInfluenceWitness(
                    interface=interface,
                    component=component,
                    source_state=source,
                    intervened_state=intervened,
                    baseline_outside_trace=baseline_trace,
                    intervened_outside_trace=intervened_trace,
                )
    return None


def profile_process_interface(
    system: BinarySynchronousSystem,
    interface: Iterable[str],
    *,
    evidence_mode: EvidenceMode,
    horizon: int,
) -> ProcessInterfaceProfile:
    """Profile one candidate without selecting it as the process boundary."""

    if horizon <= 0:
        raise ValueError("horizon must be positive")
    retained, inside_indices, outside, outside_indices = _interface_indices(
        system,
        interface,
    )
    recurrent_projections = {
        _projection(state, inside_indices)
        for state in system.reachable_recurrent_states()
    }
    persistent_variation = len(recurrent_projections) > 1
    latent_state_multiplicity = _has_latent_state_multiplicity(
        system,
        inside_indices,
        outside_indices,
        horizon=horizon,
    )

    if evidence_mode is EvidenceMode.OBSERVATIONAL:
        return ProcessInterfaceProfile(
            interface=retained,
            outside=outside,
            evidence_mode=evidence_mode,
            persistent_variation=persistent_variation,
            internal_influence=None,
            incoming_influence=None,
            outgoing_influence=None,
            latent_state_multiplicity=latent_state_multiplicity,
            record_acquisition=None,
            record_sensitive_outflow=None,
            continuation_influence=None,
            continuation_witness=None,
        )

    influence_edges = {
        (witness.source_component, witness.target_component)
        for witness in coordinate_influence_witnesses(system)
    }
    inside = set(retained)
    outside_set = set(outside)
    internal_influence = any(
        source in inside and target in inside
        for source, target in influence_edges
    )
    incoming_influence = any(
        source in outside_set and target in inside
        for source, target in influence_edges
    )
    outgoing_influence = any(
        source in inside and target in outside_set
        for source, target in influence_edges
    )
    record_sensitive_outflow = _has_record_sensitive_outflow(
        system,
        inside_indices,
        outside_indices,
        horizon=horizon,
    )
    continuation_witness = _continuation_influence_witness(
        system,
        retained,
        outside_indices,
        horizon=horizon,
    )
    return ProcessInterfaceProfile(
        interface=retained,
        outside=outside,
        evidence_mode=evidence_mode,
        persistent_variation=persistent_variation,
        internal_influence=internal_influence,
        incoming_influence=incoming_influence,
        outgoing_influence=outgoing_influence,
        latent_state_multiplicity=latent_state_multiplicity,
        record_acquisition=(
            incoming_influence and latent_state_multiplicity
        ),
        record_sensitive_outflow=record_sensitive_outflow,
        continuation_influence=continuation_witness is not None,
        continuation_witness=continuation_witness,
    )


@dataclass(frozen=True)
class InterfaceQuery:
    query_id: str
    required_true: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.query_id:
            raise ValueError("query_id must be nonempty")
        if not self.required_true or len(self.required_true) != len(
            set(self.required_true)
        ):
            raise ValueError("required features must be nonempty and unique")
        unknown = set(self.required_true) - set(FEATURE_FIELDS)
        if unknown:
            raise ValueError(f"query contains unknown features: {unknown}")


PRIMARY_PROCESS_QUERY = InterfaceQuery(
    query_id="record_bearing_continuation_interface",
    required_true=(
        "persistent_variation",
        "record_acquisition",
        "record_sensitive_outflow",
        "continuation_influence",
    ),
)


class IdentificationStatus(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    SET_IDENTIFIED = "SET_IDENTIFIED"
    UNRESOLVED = "UNRESOLVED"
    NO_CANDIDATE = "NO_CANDIDATE"


@dataclass(frozen=True)
class InterfaceIdentification:
    system_id: str
    query: InterfaceQuery
    evidence_mode: EvidenceMode
    profiles: tuple[ProcessInterfaceProfile, ...]
    certified_interfaces: tuple[tuple[str, ...], ...]
    unresolved_interfaces: tuple[tuple[str, ...], ...]
    rejected_interfaces: tuple[tuple[str, ...], ...]
    retained_minimal_interfaces: tuple[tuple[str, ...], ...]
    status: IdentificationStatus

    def as_dict(self) -> dict[str, object]:
        return {
            "system_id": self.system_id,
            "query_id": self.query.query_id,
            "required_true": list(self.query.required_true),
            "evidence_mode": self.evidence_mode.value,
            "status": self.status.value,
            "certified_interfaces": [
                list(interface) for interface in self.certified_interfaces
            ],
            "unresolved_interfaces": [
                list(interface) for interface in self.unresolved_interfaces
            ],
            "rejected_interfaces": [
                list(interface) for interface in self.rejected_interfaces
            ],
            "retained_minimal_interfaces": [
                list(interface)
                for interface in self.retained_minimal_interfaces
            ],
            "profiles": [profile.as_dict() for profile in self.profiles],
        }


def _minimal_interfaces(
    interfaces: Iterable[tuple[str, ...]],
) -> tuple[tuple[str, ...], ...]:
    retained = tuple(sorted(set(interfaces)))
    sets = {interface: frozenset(interface) for interface in retained}
    return tuple(
        interface
        for interface in retained
        if not any(
            other_set < sets[interface]
            for other, other_set in sets.items()
            if other != interface
        )
    )


def identify_process_interfaces(
    system: BinarySynchronousSystem,
    query: InterfaceQuery = PRIMARY_PROCESS_QUERY,
    *,
    evidence_mode: EvidenceMode,
    horizon: int,
) -> InterfaceIdentification:
    """Retain the complete query fiber and every inclusion-minimal candidate."""

    profiles = tuple(
        profile_process_interface(
            system,
            interface,
            evidence_mode=evidence_mode,
            horizon=horizon,
        )
        for interface in _component_subsets(system.component_ids)
    )
    certified = []
    unresolved = []
    rejected = []
    for profile in profiles:
        values = tuple(profile.feature(name) for name in query.required_true)
        if any(value is False for value in values):
            rejected.append(profile.interface)
        elif all(value is True for value in values):
            certified.append(profile.interface)
        else:
            unresolved.append(profile.interface)

    retained = (*certified, *unresolved)
    minimal = _minimal_interfaces(retained)
    if unresolved:
        status = IdentificationStatus.UNRESOLVED
    elif not certified:
        status = IdentificationStatus.NO_CANDIDATE
    elif len(minimal) == 1:
        status = IdentificationStatus.IDENTIFIED
    else:
        status = IdentificationStatus.SET_IDENTIFIED
    return InterfaceIdentification(
        system_id=system.system_id,
        query=query,
        evidence_mode=evidence_mode,
        profiles=profiles,
        certified_interfaces=tuple(certified),
        unresolved_interfaces=tuple(unresolved),
        rejected_interfaces=tuple(rejected),
        retained_minimal_interfaces=minimal,
        status=status,
    )


def observational_signature(
    system: BinarySynchronousSystem,
    *,
    horizon: int,
) -> tuple[object, ...]:
    levels = system.states_by_depth(horizon)
    observed_states = sorted(set().union(*levels))
    return (
        system.component_ids,
        tuple(sorted(system.initial_states)),
        tuple((state, system.step(state)) for state in observed_states),
    )


def intervention_signature(
    system: BinarySynchronousSystem,
) -> tuple[object, ...]:
    return (
        system.component_ids,
        tuple(
            (
                state,
                component,
                1 - state[system.component_index[component]],
                system.step(
                    system.intervene_source(
                        state,
                        component,
                        1 - state[system.component_index[component]],
                    )
                ),
            )
            for state in system.states
            for component in system.component_ids
        ),
    )


def observationally_equivalent(
    left: BinarySynchronousSystem,
    right: BinarySynchronousSystem,
    *,
    horizon: int,
) -> bool:
    return observational_signature(left, horizon=horizon) == observational_signature(
        right,
        horizon=horizon,
    )


def interventionally_equivalent(
    left: BinarySynchronousSystem,
    right: BinarySynchronousSystem,
) -> bool:
    return intervention_signature(left) == intervention_signature(right)


@dataclass(frozen=True)
class UpdateCollision:
    observation: object
    left_memory: object
    right_memory: object
    target_memory: object

    def as_dict(self) -> dict[str, str]:
        return {
            "observation": repr(self.observation),
            "left_memory": repr(self.left_memory),
            "right_memory": repr(self.right_memory),
            "target_memory": repr(self.target_memory),
        }


@dataclass(frozen=True)
class MemoryInjectivityAudit:
    controller_id: str
    conditionally_injective: bool
    collisions: tuple[UpdateCollision, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "controller_id": self.controller_id,
            "conditionally_injective": self.conditionally_injective,
            "collision_count": len(self.collisions),
            "collisions": [collision.as_dict() for collision in self.collisions],
        }


def audit_memory_update_injectivity(
    controller: FiniteStateController,
) -> MemoryInjectivityAudit:
    """Check injectivity of memory -> next-memory at each observation."""

    observations = tuple(
        dict.fromkeys(
            observation
            for _state, observation in controller.observation_rows
        )
    )
    collisions = []
    for observation in observations:
        for left_index, left_memory in enumerate(controller.memory_states):
            for right_memory in controller.memory_states[left_index + 1 :]:
                left_target = controller.update(left_memory, observation)
                right_target = controller.update(right_memory, observation)
                if left_target == right_target:
                    collisions.append(
                        UpdateCollision(
                            observation=observation,
                            left_memory=left_memory,
                            right_memory=right_memory,
                            target_memory=left_target,
                        )
                    )
    return MemoryInjectivityAudit(
        controller_id=controller.controller_id,
        conditionally_injective=not collisions,
        collisions=tuple(collisions),
    )


@dataclass(frozen=True)
class ClosedLoopMapAudit:
    controller_id: str
    state_count: int
    image_size: int
    injective: bool
    collisions: tuple[tuple[str, str, str], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "controller_id": self.controller_id,
            "state_count": self.state_count,
            "image_size": self.image_size,
            "injective": self.injective,
            "collision_count": len(self.collisions),
            "collisions": [list(collision) for collision in self.collisions],
        }


def audit_deterministic_closed_loop_map(
    system: ControlledMarkovSystem,
    controller: FiniteStateController,
) -> ClosedLoopMapAudit:
    """Audit functional injectivity of a deterministic compiled closed loop."""

    compiled = compile_closed_loop(system, controller)
    target_to_sources: dict[object, list[object]] = {}
    for source in compiled.system.states:
        distribution = compiled.system.distribution(source, "step")
        if len(distribution.rows) != 1 or distribution.rows[0][1] != 1:
            raise ValueError("closed-loop map audit requires deterministic rows")
        target = distribution.rows[0][0]
        target_to_sources.setdefault(target, []).append(source)
    collisions = tuple(
        (
            repr(sources[0]),
            repr(sources[1]),
            repr(target),
        )
        for target, sources in target_to_sources.items()
        if len(sources) > 1
    )
    return ClosedLoopMapAudit(
        controller_id=controller.controller_id,
        state_count=len(compiled.system.states),
        image_size=len(target_to_sources),
        injective=not collisions,
        collisions=collisions,
    )
