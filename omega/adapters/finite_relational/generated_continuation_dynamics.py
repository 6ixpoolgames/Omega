"""Generated finite continuation dynamics.

This module supports two post-freeze audits:

* compatibility complexes derived from shared-action continuation kernels;
* deformation distributions over declared exhaustive finite-system classes.

The outputs are finite structural evidence. They are not thermodynamic,
normative, or substrate-independent distributions.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from itertools import combinations, product
from typing import Any, Iterable, Iterator, Mapping

from omega.adapters.finite_relational.bounded_behavioral_logic import (
    signature_refines,
)
from omega.adapters.finite_relational.dynamic_continuation_profiles import (
    BehaviorSignature,
    DeformationVerdict,
    FiniteControlSystem,
    behavior_signatures,
    deformation_witness,
)
from omega.adapters.finite_relational.lushness_diversity import (
    CompatibilityStructure,
    Trajectory,
)


PROTOCOL_DOC = "docs/research_notes/omega_v2/generated_continuation_dynamics_protocol_v0.md"

COMPONENTS = ("A", "B", "C")
SHARED_ACTIONS = ("a0", "a1", "a2", "a3")
WORLD_STATES = ("s0", "s1", "s2")
WORLD_ACTIONS = ("a0", "a1")
HORIZONS = (0, 1, 2)
VERDICTS = tuple(verdict.value for verdict in DeformationVerdict)

Family = frozenset[str]


class GeneratorClass(str, Enum):
    COMPLETE = "complete"
    REVERSIBLE = "reversible"
    ABSORBING = "absorbing"


@dataclass(frozen=True)
class SharedActionAssignment:
    """One generated assignment of live-preserving actions to components."""

    allowed_rows: tuple[tuple[str, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        components = tuple(component for component, _allowed in self.allowed_rows)
        if components != COMPONENTS:
            raise ValueError(f"allowed rows must be ordered as {COMPONENTS!r}")
        for component, allowed in self.allowed_rows:
            if len(allowed) != len(set(allowed)):
                raise ValueError(f"duplicate allowed action for {component}")
            if tuple(sorted(allowed)) != allowed:
                raise ValueError("allowed actions must be sorted")
            unknown = set(allowed) - set(SHARED_ACTIONS)
            if unknown:
                raise ValueError(f"unknown allowed actions: {sorted(unknown)}")

    @property
    def assignment_id(self) -> str:
        encoded = "__".join(
            f"{component}_{'-'.join(allowed) if allowed else 'none'}"
            for component, allowed in self.allowed_rows
        )
        return f"shared_{encoded}"

    @property
    def allowed_map(self) -> dict[str, frozenset[str]]:
        return {component: frozenset(allowed) for component, allowed in self.allowed_rows}

    def allowed_for(self, component: str) -> frozenset[str]:
        try:
            return self.allowed_map[component]
        except KeyError as exc:
            raise KeyError(component) from exc

    def relabel(
        self,
        *,
        component_mapping: Mapping[str, str],
        action_mapping: Mapping[str, str],
    ) -> "SharedActionAssignment":
        if set(component_mapping) != set(COMPONENTS):
            raise ValueError("component mapping must be total")
        if set(component_mapping.values()) != set(COMPONENTS):
            raise ValueError("component mapping must be bijective")
        if set(action_mapping) != set(SHARED_ACTIONS):
            raise ValueError("action mapping must be total")
        if set(action_mapping.values()) != set(SHARED_ACTIONS):
            raise ValueError("action mapping must be bijective")
        transported = {
            component_mapping[component]: tuple(
                sorted(action_mapping[action] for action in allowed)
            )
            for component, allowed in self.allowed_rows
        }
        return SharedActionAssignment(
            tuple((component, transported[component]) for component in COMPONENTS)
        )


@dataclass(frozen=True)
class ProductSystem:
    """One exact shared- or independent-action component product."""

    family: tuple[str, ...]
    system: FiniteControlSystem
    safe_states: frozenset[str]
    initial_state: str


@dataclass(frozen=True)
class GeneratedSystemRecord:
    """One member of the exhaustive deformation-system manifest."""

    table_index: int
    atom_mask: int
    transition_table: tuple[int, ...]
    system: FiniteControlSystem
    reversible: bool
    absorbing: bool

    @property
    def system_id(self) -> str:
        return self.system.system_id


def shared_action_assignments() -> tuple[SharedActionAssignment, ...]:
    options = tuple(combinations(SHARED_ACTIONS, 2))
    return tuple(
        SharedActionAssignment(
            tuple(
                (component, tuple(allowed))
                for component, allowed in zip(COMPONENTS, selected, strict=True)
            )
        )
        for selected in product(options, repeat=len(COMPONENTS))
    )


def _state_name(
    family: tuple[str, ...],
    statuses: tuple[str, ...],
) -> str:
    return "|".join(
        f"{component}:{status}" for component, status in zip(family, statuses, strict=True)
    )


def component_system(
    component: str,
    allowed_actions: Iterable[str],
) -> FiniteControlSystem:
    allowed = frozenset(allowed_actions)
    if not allowed <= set(SHARED_ACTIONS):
        raise ValueError("component allowed set contains an unknown action")
    return FiniteControlSystem(
        system_id=f"component_{component}_{'-'.join(sorted(allowed)) or 'none'}",
        states=("live", "dead"),
        actions=SHARED_ACTIONS,
        transitions=tuple(
            [
                (
                    "live",
                    action,
                    "live" if action in allowed else "dead",
                )
                for action in SHARED_ACTIONS
            ]
            + [("dead", action, "dead") for action in SHARED_ACTIONS]
        ),
        atoms=(
            ("live", frozenset({"safe"})),
            ("dead", frozenset()),
        ),
    )


def shared_action_product(
    assignment: SharedActionAssignment,
    family: Family,
    *,
    independent_actions: bool = False,
) -> ProductSystem:
    if not family:
        raise ValueError("the empty family is handled by convention")
    if not family <= set(COMPONENTS):
        raise ValueError("family contains an unknown component")
    ordered_family = tuple(component for component in COMPONENTS if component in family)
    status_rows = tuple(product(("live", "dead"), repeat=len(ordered_family)))
    states = tuple(_state_name(ordered_family, statuses) for statuses in status_rows)
    status_by_state = {_state_name(ordered_family, statuses): statuses for statuses in status_rows}

    if independent_actions:
        action_vectors = tuple(product(SHARED_ACTIONS, repeat=len(ordered_family)))
        actions = tuple(
            "|".join(
                f"{component}={action}"
                for component, action in zip(
                    ordered_family,
                    action_vector,
                    strict=True,
                )
            )
            for action_vector in action_vectors
        )
        vector_by_action = dict(zip(actions, action_vectors, strict=True))
    else:
        actions = SHARED_ACTIONS
        vector_by_action = {
            action: tuple(action for _component in ordered_family) for action in SHARED_ACTIONS
        }

    transitions: list[tuple[str, str, str]] = []
    for source in states:
        statuses = status_by_state[source]
        for action in actions:
            action_vector = vector_by_action[action]
            next_statuses = tuple(
                (
                    "dead"
                    if status == "dead"
                    else "live"
                    if component_action in assignment.allowed_for(component)
                    else "dead"
                )
                for component, status, component_action in zip(
                    ordered_family,
                    statuses,
                    action_vector,
                    strict=True,
                )
            )
            transitions.append(
                (
                    source,
                    action,
                    _state_name(ordered_family, next_statuses),
                )
            )

    initial = _state_name(
        ordered_family,
        tuple("live" for _component in ordered_family),
    )
    safe_states = frozenset({initial})
    system = FiniteControlSystem(
        system_id=(
            f"{'independent' if independent_actions else 'shared'}_product_"
            f"{assignment.assignment_id}_{'-'.join(ordered_family)}"
        ),
        states=states,
        actions=actions,
        transitions=tuple(transitions),
        atoms=tuple(
            (
                state,
                frozenset({"joint_safe"}) if state in safe_states else frozenset(),
            )
            for state in states
        ),
    )
    return ProductSystem(
        family=ordered_family,
        system=system,
        safe_states=safe_states,
        initial_state=initial,
    )


def robust_safe_kernel(
    system: FiniteControlSystem,
    safe_states: Iterable[str],
) -> frozenset[str]:
    kernel = set(safe_states)
    while True:
        next_kernel = {
            state
            for state in kernel
            if any(
                system.successors(state, action) and system.successors(state, action) <= kernel
                for action in system.enabled_actions(state)
            )
        }
        if next_kernel == kernel:
            return frozenset(kernel)
        kernel = next_kernel


def powerset_components() -> tuple[Family, ...]:
    return tuple(
        frozenset(candidate)
        for size in range(len(COMPONENTS) + 1)
        for candidate in combinations(COMPONENTS, size)
    )


def family_kernel(
    assignment: SharedActionAssignment,
    family: Family,
    *,
    independent_actions: bool = False,
) -> frozenset[str]:
    if not family:
        return frozenset({"empty"})
    product_system = shared_action_product(
        assignment,
        family,
        independent_actions=independent_actions,
    )
    return robust_safe_kernel(
        product_system.system,
        product_system.safe_states,
    )


def jointly_realizable(
    assignment: SharedActionAssignment,
    family: Family,
    *,
    independent_actions: bool = False,
) -> bool:
    if not family:
        return True
    product_system = shared_action_product(
        assignment,
        family,
        independent_actions=independent_actions,
    )
    return product_system.initial_state in robust_safe_kernel(
        product_system.system, product_system.safe_states
    )


def realizable_families(
    assignment: SharedActionAssignment,
    *,
    independent_actions: bool = False,
) -> tuple[Family, ...]:
    return tuple(
        family
        for family in powerset_components()
        if jointly_realizable(
            assignment,
            family,
            independent_actions=independent_actions,
        )
    )


def maximal_faces(families: Iterable[Family]) -> tuple[Family, ...]:
    retained = tuple(sorted(set(families), key=_family_sort_key))
    nonempty = tuple(family for family in retained if family)
    return tuple(family for family in nonempty if not any(family < other for other in nonempty))


def downward_closure_failures(
    assignment: SharedActionAssignment,
) -> tuple[dict[str, Any], ...]:
    retained = set(realizable_families(assignment))
    failures = []
    for family in retained:
        for candidate in powerset_components():
            if candidate <= family and candidate not in retained:
                failures.append(
                    {
                        "assignment_id": assignment.assignment_id,
                        "family": sorted(family),
                        "missing_subset": sorted(candidate),
                    }
                )
    return tuple(failures)


def compatibility_structure_from_dynamics(
    assignment: SharedActionAssignment,
) -> CompatibilityStructure:
    faces = maximal_faces(realizable_families(assignment))
    return CompatibilityStructure(
        structure_id=f"derived_{assignment.assignment_id}",
        trajectories=tuple(
            Trajectory(component, frozenset({f"continuation:{component}"}))
            for component in COMPONENTS
        ),
        maximal_faces=faces,
    )


def compatibility_control_panel(
    assignment: SharedActionAssignment,
) -> dict[str, Any]:
    singletons = tuple(frozenset({component}) for component in COMPONENTS)
    pairs = tuple(frozenset(pair) for pair in combinations(COMPONENTS, 2))
    structure = compatibility_structure_from_dynamics(assignment)
    return {
        "action_alphabet_size": len(SHARED_ACTIONS),
        "component_count": len(COMPONENTS),
        "allowed_action_counts": sorted(
            len(assignment.allowed_for(component)) for component in COMPONENTS
        ),
        "pairwise_common_action_counts": sorted(
            len(assignment.allowed_for(left) & assignment.allowed_for(right))
            for left, right in combinations(COMPONENTS, 2)
        ),
        "singleton_kernel_sizes": sorted(
            len(family_kernel(assignment, singleton)) for singleton in singletons
        ),
        "pair_kernel_sizes": sorted(len(family_kernel(assignment, pair)) for pair in pairs),
        "one_skeleton": [list(edge) for edge in structure.one_skeleton()],
    }


def _compatibility_search_cached() -> dict[str, Any]:
    assignments = shared_action_assignments()
    all_families = powerset_components()
    triple = frozenset(COMPONENTS)
    pairs = tuple(frozenset(pair) for pair in combinations(COMPONENTS, 2))
    rows: list[dict[str, Any]] = []
    closure_failures: list[dict[str, Any]] = []
    intersection_correspondence_failures: list[dict[str, Any]] = []
    hollow_assignments: list[SharedActionAssignment] = []
    filled_assignments: list[SharedActionAssignment] = []

    for assignment in assignments:
        compatible = set(realizable_families(assignment))
        failures = downward_closure_failures(assignment)
        closure_failures.extend(failures)
        for family in all_families:
            common_actions = (
                set(SHARED_ACTIONS)
                if not family
                else set.intersection(
                    *(set(assignment.allowed_for(component)) for component in family)
                )
            )
            expected = not family or bool(common_actions)
            observed = family in compatible
            if expected != observed:
                intersection_correspondence_failures.append(
                    {
                        "assignment_id": assignment.assignment_id,
                        "family": sorted(family),
                        "common_actions": sorted(common_actions),
                        "expected": expected,
                        "observed": observed,
                    }
                )
        all_pairs = all(pair in compatible for pair in pairs)
        triple_realizable = triple in compatible
        hollow = all_pairs and not triple_realizable
        filled = all_pairs and triple_realizable
        if hollow:
            hollow_assignments.append(assignment)
        if filled:
            filled_assignments.append(assignment)
        structure = compatibility_structure_from_dynamics(assignment)
        rows.append(
            {
                "assignment_id": assignment.assignment_id,
                "allowed_A": sorted(assignment.allowed_for("A")),
                "allowed_B": sorted(assignment.allowed_for("B")),
                "allowed_C": sorted(assignment.allowed_for("C")),
                "realizable_family_count": len(compatible),
                "all_singletons_realizable": all(
                    frozenset({component}) in compatible for component in COMPONENTS
                ),
                "all_pairs_realizable": all_pairs,
                "triple_realizable": triple_realizable,
                "is_hollow": hollow,
                "is_filled": filled,
                "is_flag": structure.is_flag(),
                "maximal_faces": [sorted(face) for face in structure.maximal_faces],
                "downward_closure_failure_count": len(failures),
            }
        )

    if not hollow_assignments:
        raise RuntimeError("preregistered manifest contains no hollow assignment")
    hollow = hollow_assignments[0]
    hollow_panel = compatibility_control_panel(hollow)
    matched_filled = tuple(
        assignment
        for assignment in filled_assignments
        if compatibility_control_panel(assignment) == hollow_panel
    )
    if not matched_filled:
        raise RuntimeError("preregistered manifest contains no matched filled control")
    filled = matched_filled[0]

    hollow_structure = compatibility_structure_from_dynamics(hollow)
    filled_structure = compatibility_structure_from_dynamics(filled)
    independent_triple = jointly_realizable(
        hollow,
        triple,
        independent_actions=True,
    )

    component_mapping = {"A": "C", "B": "A", "C": "B"}
    action_mapping = {"a0": "a2", "a1": "a0", "a2": "a3", "a3": "a1"}
    relabeled = hollow.relabel(
        component_mapping=component_mapping,
        action_mapping=action_mapping,
    )
    original_families = set(realizable_families(hollow))
    expected_relabelled = {
        frozenset(component_mapping[component] for component in family)
        for family in original_families
    }
    relabelled_families = set(realizable_families(relabeled))

    deadlock_assignment = SharedActionAssignment(
        (
            ("A", ()),
            ("B", ("a0", "a1")),
            ("C", ("a2", "a3")),
        )
    )
    deadlock_singleton = frozenset({"A"})

    bridge_faces_equal = tuple(hollow_structure.maximal_faces) == maximal_faces(
        realizable_families(hollow)
    )
    cases = {
        "GN1_manifest": len(assignments) == 216,
        "GN2_downward_closure": (not closure_failures and not intersection_correspondence_failures),
        "GN3_generated_nonflag": (
            all(jointly_realizable(hollow, pair) for pair in pairs)
            and not jointly_realizable(hollow, triple)
            and not hollow_structure.is_flag()
        ),
        "GN4_matched_filled_control": (
            compatibility_control_panel(filled) == hollow_panel
            and jointly_realizable(filled, triple)
            and filled_structure.is_flag()
        ),
        "GN5_independent_action_negative_control": independent_triple,
        "GN6_relabeling": relabelled_families == expected_relabelled,
        "GN7_deadlock": not jointly_realizable(
            deadlock_assignment,
            deadlock_singleton,
        ),
        "GN8_lushness_bridge": bridge_faces_equal,
    }
    return {
        "assignment_count": len(assignments),
        "all_family_count": len(all_families),
        "hollow_assignment_count": len(hollow_assignments),
        "filled_assignment_count": len(filled_assignments),
        "matched_filled_count": len(matched_filled),
        "downward_closure_failures": closure_failures,
        "intersection_correspondence_failures": (intersection_correspondence_failures),
        "search_rows": rows,
        "hollow": _assignment_result(hollow),
        "filled": _assignment_result(filled),
        "matched_control_panel": hollow_panel,
        "independent_action_triple_realizable": independent_triple,
        "relabeling_preserved": relabelled_families == expected_relabelled,
        "deadlock_singleton_realizable": jointly_realizable(
            deadlock_assignment,
            deadlock_singleton,
        ),
        "bridge_faces_equal": bridge_faces_equal,
        "cases": cases,
    }


@lru_cache(maxsize=1)
def compatibility_search() -> dict[str, Any]:
    return _compatibility_search_cached()


def _assignment_result(
    assignment: SharedActionAssignment,
) -> dict[str, Any]:
    structure = compatibility_structure_from_dynamics(assignment)
    families = realizable_families(assignment)
    kernel_sizes = {
        _family_id(family): len(family_kernel(assignment, family))
        for family in powerset_components()
    }
    return {
        "assignment_id": assignment.assignment_id,
        "allowed_actions": {
            component: sorted(assignment.allowed_for(component)) for component in COMPONENTS
        },
        "realizable_families": [sorted(family) for family in families],
        "maximal_faces": [sorted(face) for face in structure.maximal_faces],
        "one_skeleton": [list(edge) for edge in structure.one_skeleton()],
        "is_flag": structure.is_flag(),
        "kernel_sizes": kernel_sizes,
    }


def generated_system_records() -> Iterator[GeneratedSystemRecord]:
    table_index = 0
    for transition_table in product(range(len(WORLD_STATES)), repeat=6):
        reversible = _table_is_reversible(transition_table)
        absorbing = _table_is_absorbing(transition_table)
        for atom_mask in range(2 ** len(WORLD_STATES)):
            transitions = tuple(
                (
                    state,
                    action,
                    WORLD_STATES[transition_table[state_index * len(WORLD_ACTIONS) + action_index]],
                )
                for state_index, state in enumerate(WORLD_STATES)
                for action_index, action in enumerate(WORLD_ACTIONS)
            )
            atoms = tuple(
                (
                    state,
                    frozenset({"p"}) if atom_mask & (1 << state_index) else frozenset(),
                )
                for state_index, state in enumerate(WORLD_STATES)
            )
            system = FiniteControlSystem(
                system_id=f"generated_t{table_index:03d}_m{atom_mask}",
                states=WORLD_STATES,
                actions=WORLD_ACTIONS,
                transitions=transitions,
                atoms=atoms,
            )
            yield GeneratedSystemRecord(
                table_index=table_index,
                atom_mask=atom_mask,
                transition_table=transition_table,
                system=system,
                reversible=reversible,
                absorbing=absorbing,
            )
        table_index += 1


def _table_is_reversible(table: tuple[int, ...]) -> bool:
    expected = list(range(len(WORLD_STATES)))
    return all(
        sorted(
            table[state_index * len(WORLD_ACTIONS) + action_index]
            for state_index in range(len(WORLD_STATES))
        )
        == expected
        for action_index in range(len(WORLD_ACTIONS))
    )


def _table_is_absorbing(table: tuple[int, ...]) -> bool:
    sink_index = len(WORLD_STATES) - 1
    if any(
        table[sink_index * len(WORLD_ACTIONS) + action_index] != sink_index
        for action_index in range(len(WORLD_ACTIONS))
    ):
        return False
    adjacency = {
        state_index: {
            table[state_index * len(WORLD_ACTIONS) + action_index]
            for action_index in range(len(WORLD_ACTIONS))
        }
        for state_index in range(len(WORLD_STATES))
    }
    return all(
        _can_reach(state_index, sink_index, adjacency) for state_index in range(len(WORLD_STATES))
    )


def _can_reach(
    source: int,
    target: int,
    adjacency: Mapping[int, set[int]],
) -> bool:
    seen: set[int] = set()
    frontier = [source]
    while frontier:
        current = frontier.pop()
        if current == target:
            return True
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(adjacency[current] - seen)
    return False


def signature_deformation(
    source: BehaviorSignature,
    target: BehaviorSignature,
) -> DeformationVerdict:
    target_refines_source = signature_refines(source, target)
    source_refines_target = signature_refines(target, source)
    if target_refines_source and source_refines_target:
        return DeformationVerdict.EQUIVALENT
    if target_refines_source:
        return DeformationVerdict.EXPANSION
    if source_refines_target:
        return DeformationVerdict.CONTRACTION
    return DeformationVerdict.MIXED


def _system_deformation(
    record: GeneratedSystemRecord,
    *,
    horizon: int,
) -> dict[str, Any]:
    signatures = behavior_signatures(record.system, horizon)
    structural_pairs = tuple(
        sorted({(source, target) for source, _action, target in record.system.transitions})
    )
    verdict_by_pair = {
        pair: signature_deformation(
            signatures[pair[0]],
            signatures[pair[1]],
        ).value
        for pair in structural_pairs
    }
    structural_counts = Counter(verdict_by_pair.values())
    action_counts = Counter(
        verdict_by_pair[(source, target)] for source, _action, target in record.system.transitions
    )
    return {
        "system_id": record.system_id,
        "table_index": record.table_index,
        "atom_mask": record.atom_mask,
        "reversible": record.reversible,
        "absorbing": record.absorbing,
        "horizon": horizon,
        "structural_edge_count": len(structural_pairs),
        "action_edge_count": len(record.system.transitions),
        "structural_counts": {verdict: structural_counts[verdict] for verdict in VERDICTS},
        "action_counts": {verdict: action_counts[verdict] for verdict in VERDICTS},
        "verdict_by_pair": verdict_by_pair,
    }


def _record_classes(
    record: GeneratedSystemRecord,
) -> tuple[GeneratorClass, ...]:
    classes = [GeneratorClass.COMPLETE]
    if record.reversible:
        classes.append(GeneratorClass.REVERSIBLE)
    if record.absorbing:
        classes.append(GeneratorClass.ABSORBING)
    return tuple(classes)


def _deformation_study_uncached() -> dict[str, Any]:
    aggregate: dict[tuple[str, int], dict[str, Any]] = {}
    for generator_class in GeneratorClass:
        for horizon in HORIZONS:
            aggregate[(generator_class.value, horizon)] = {
                "system_count": 0,
                "structural_edge_count": 0,
                "action_edge_count": 0,
                "structural_counts": Counter(),
                "action_counts": Counter(),
                "system_share_sums": Counter(),
                "systems_with": Counter(),
            }

    system_rows: list[dict[str, Any]] = []
    manifest_hasher = hashlib.sha256()
    complete_count = 0
    reversible_count = 0
    absorbing_count = 0

    for record in generated_system_records():
        manifest_hasher.update(
            json.dumps(
                {
                    "table_index": record.table_index,
                    "atom_mask": record.atom_mask,
                    "table": record.transition_table,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        complete_count += 1
        reversible_count += int(record.reversible)
        absorbing_count += int(record.absorbing)
        record_classes = _record_classes(record)
        for horizon in HORIZONS:
            result = _system_deformation(record, horizon=horizon)
            row = {
                "system_id": record.system_id,
                "table_index": record.table_index,
                "atom_mask": record.atom_mask,
                "reversible": record.reversible,
                "absorbing": record.absorbing,
                "horizon": horizon,
                "structural_edge_count": result["structural_edge_count"],
                "action_edge_count": result["action_edge_count"],
            }
            for verdict in VERDICTS:
                row[f"structural_{verdict}"] = result["structural_counts"][verdict]
                row[f"action_{verdict}"] = result["action_counts"][verdict]
            system_rows.append(row)

            for generator_class in record_classes:
                target = aggregate[(generator_class.value, horizon)]
                target["system_count"] += 1
                target["structural_edge_count"] += result["structural_edge_count"]
                target["action_edge_count"] += result["action_edge_count"]
                target["structural_counts"].update(result["structural_counts"])
                target["action_counts"].update(result["action_counts"])
                for verdict in VERDICTS:
                    target["system_share_sums"][verdict] += (
                        result["structural_counts"][verdict] / result["structural_edge_count"]
                    )
                    target["systems_with"][verdict] += int(result["structural_counts"][verdict] > 0)

    distribution_rows = []
    for generator_class in GeneratorClass:
        for horizon in HORIZONS:
            target = aggregate[(generator_class.value, horizon)]
            row: dict[str, Any] = {
                "generator_class": generator_class.value,
                "horizon": horizon,
                "system_count": target["system_count"],
                "structural_edge_count": target["structural_edge_count"],
                "action_edge_count": target["action_edge_count"],
            }
            for verdict in VERDICTS:
                row[f"structural_{verdict}_count"] = target["structural_counts"][verdict]
                row[f"structural_{verdict}_share"] = (
                    target["structural_counts"][verdict] / target["structural_edge_count"]
                )
                row[f"mean_system_{verdict}_share"] = (
                    target["system_share_sums"][verdict] / target["system_count"]
                )
                row[f"action_{verdict}_count"] = target["action_counts"][verdict]
                row[f"action_{verdict}_share"] = (
                    target["action_counts"][verdict] / target["action_edge_count"]
                )
                row[f"systems_with_{verdict}"] = target["systems_with"][verdict]
            distribution_rows.append(row)

    duplicate = _duplicate_action_sensitivity()
    relabeling = _deformation_relabeling_control()
    reverse_edge = _reverse_edge_control()
    retained_control = deformation_witness(horizon=1)
    retained_verdicts = set(retained_control["verdicts"].values())
    class_counts = {
        GeneratorClass.COMPLETE.value: complete_count,
        GeneratorClass.REVERSIBLE.value: reversible_count,
        GeneratorClass.ABSORBING.value: absorbing_count,
    }
    expected_complete = len(WORLD_STATES) ** (len(WORLD_STATES) * len(WORLD_ACTIONS)) * 2 ** len(
        WORLD_STATES
    )
    cases = {
        "DD1_manifest": (
            complete_count == expected_complete and reversible_count > 0 and absorbing_count > 0
        ),
        "DD2_distributions": all(
            row["system_count"] > 0
            and sum(row[f"structural_{verdict}_count"] for verdict in VERDICTS)
            == row["structural_edge_count"]
            for row in distribution_rows
        ),
        "DD3_relabeling": relabeling["preserved"],
        "DD4_duplicate_weighting": (
            duplicate["structural_verdicts_preserved"] and duplicate["action_weight_changed"]
        ),
        "DD5_classifier_controls": retained_verdicts == set(VERDICTS),
        "DD6_horizon_rows": {row["horizon"] for row in distribution_rows} == set(HORIZONS),
        "DD7_no_synthetic_reverse_edges": reverse_edge["synthetic_reverse_excluded"],
    }
    return {
        "manifest": {
            "state_count": len(WORLD_STATES),
            "action_count": len(WORLD_ACTIONS),
            "atom_mask_count": 2 ** len(WORLD_STATES),
            "transition_table_count": len(WORLD_STATES) ** (len(WORLD_STATES) * len(WORLD_ACTIONS)),
            "class_counts": class_counts,
            "manifest_digest": manifest_hasher.hexdigest(),
        },
        "distribution_rows": distribution_rows,
        "system_rows": system_rows,
        "duplicate_action_control": duplicate,
        "relabeling_control": relabeling,
        "reverse_edge_control": reverse_edge,
        "retained_classifier_verdicts": sorted(retained_verdicts),
        "cases": cases,
    }


@lru_cache(maxsize=1)
def deformation_distribution_study() -> dict[str, Any]:
    return _deformation_study_uncached()


def _duplicate_action_sensitivity() -> dict[str, Any]:
    for record in generated_system_records():
        result = _system_deformation(record, horizon=2)
        if len({verdict for verdict, count in result["structural_counts"].items() if count}) < 2:
            continue
        signatures = behavior_signatures(record.system, 2)
        verdict_by_pair = result["verdict_by_pair"]
        selected_counts = Counter(
            verdict_by_pair[(source, target)]
            for source, action, target in record.system.transitions
            if action == "a0"
        )
        baseline_counts = Counter(result["action_counts"])
        duplicated_counts = baseline_counts + selected_counts
        baseline_total = sum(baseline_counts.values())
        duplicated_total = sum(duplicated_counts.values())
        normalized_changed = any(
            baseline_counts[verdict] / baseline_total
            != duplicated_counts[verdict] / duplicated_total
            for verdict in VERDICTS
        )
        if not normalized_changed:
            continue
        duplicate = FiniteControlSystem(
            system_id=f"{record.system_id}_duplicate_a0",
            states=record.system.states,
            actions=("a0", "a1", "a0_copy"),
            transitions=tuple(
                list(record.system.transitions)
                + [
                    (source, "a0_copy", target)
                    for source, action, target in record.system.transitions
                    if action == "a0"
                ]
            ),
            atoms=record.system.atoms,
        )
        duplicate_signatures = behavior_signatures(duplicate, 2)
        structural_preserved = all(
            signatures[state] == duplicate_signatures[state] for state in WORLD_STATES
        )
        return {
            "system_id": record.system_id,
            "horizon": 2,
            "structural_verdicts_preserved": structural_preserved,
            "baseline_action_counts": {verdict: baseline_counts[verdict] for verdict in VERDICTS},
            "duplicated_action_counts": {
                verdict: duplicated_counts[verdict] for verdict in VERDICTS
            },
            "action_weight_changed": normalized_changed,
        }
    raise RuntimeError("no duplicate-action sensitivity witness found")


def _deformation_relabeling_control() -> dict[str, Any]:
    record = next(
        candidate
        for candidate in generated_system_records()
        if candidate.atom_mask == 1
        and len(set(_system_deformation(candidate, horizon=2)["verdict_by_pair"].values())) > 1
    )
    state_mapping = {"s0": "u2", "s1": "u0", "s2": "u1"}
    action_mapping = {"a0": "b1", "a1": "b0"}
    relabeled = record.system.relabel(
        state_mapping=state_mapping,
        action_mapping=action_mapping,
        system_id=f"{record.system_id}_relabeled",
    )
    failures = []
    for horizon in HORIZONS:
        original_signatures = behavior_signatures(record.system, horizon)
        relabeled_signatures = behavior_signatures(relabeled, horizon)
        for source, target in {
            (edge_source, edge_target)
            for edge_source, _action, edge_target in record.system.transitions
        }:
            original = signature_deformation(
                original_signatures[source],
                original_signatures[target],
            )
            transported = signature_deformation(
                relabeled_signatures[state_mapping[source]],
                relabeled_signatures[state_mapping[target]],
            )
            if original is not transported:
                failures.append(
                    {
                        "horizon": horizon,
                        "source": source,
                        "target": target,
                        "original": original.value,
                        "transported": transported.value,
                    }
                )
    return {
        "system_id": record.system_id,
        "failures": failures,
        "preserved": not failures,
    }


def _reverse_edge_control() -> dict[str, Any]:
    record = next(
        candidate
        for candidate in generated_system_records()
        if any(
            (target, source)
            not in {
                (edge_source, edge_target)
                for edge_source, _action, edge_target in candidate.system.transitions
            }
            for source, _action, target in candidate.system.transitions
            if source != target
        )
    )
    exact_pairs = {(source, target) for source, _action, target in record.system.transitions}
    result = _system_deformation(record, horizon=2)
    audited_pairs = set(result["verdict_by_pair"])
    missing_reverse = next(
        (target, source)
        for source, target in sorted(exact_pairs)
        if source != target and (target, source) not in exact_pairs
    )
    return {
        "system_id": record.system_id,
        "exact_pairs_equal_audited_pairs": exact_pairs == audited_pairs,
        "missing_reverse_pair": list(missing_reverse),
        "missing_reverse_not_classified": missing_reverse not in audited_pairs,
        "synthetic_reverse_excluded": (
            exact_pairs == audited_pairs and missing_reverse not in audited_pairs
        ),
    }


def generated_continuation_dynamics_summary() -> dict[str, Any]:
    compatibility = compatibility_search()
    deformation = deformation_distribution_study()
    cases = {
        **compatibility["cases"],
        **deformation["cases"],
    }
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "retained" if all(cases.values()) else "review",
        "case_results": cases,
        "compatibility": {
            key: value
            for key, value in compatibility.items()
            if key not in {"search_rows", "cases"}
        },
        "deformation": {
            key: value for key, value in deformation.items() if key not in {"system_rows", "cases"}
        },
        "evidence_classification": {
            "generator_correctness": [
                "GN1_manifest",
                "GN2_downward_closure",
                "GN5_independent_action_negative_control",
                "GN6_relabeling",
                "GN7_deadlock",
                "GN8_lushness_bridge",
                "DD1_manifest",
                "DD3_relabeling",
                "DD4_duplicate_weighting",
                "DD5_classifier_controls",
                "DD6_horizon_rows",
                "DD7_no_synthetic_reverse_edges",
            ],
            "constructive_strictness": [
                "GN3_generated_nonflag",
                "GN4_matched_filled_control",
            ],
            "risky_generated_result": [
                "DD2_distributions",
            ],
        },
        "not_claimed": [
            "thermodynamic arrow",
            "entropy production",
            "physical degrees of freedom",
            "universal deformation probabilities",
            "value",
            "valuerhood",
            "agency",
            "standing",
            "identity",
            "moral license",
            "lushness",
            "Omega validation",
        ],
    }


def case_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    evidence_by_case = {
        case: evidence_class
        for evidence_class, cases in summary["evidence_classification"].items()
        for case in cases
    }
    return [
        {
            "case": case,
            "passes": passes,
            "evidence_class": evidence_by_case.get(case, "unclassified"),
        }
        for case, passes in summary["case_results"].items()
    ]


def generator_manifest_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = summary["deformation"]["manifest"]
    return [
        {
            "generator": "shared_action_assignments",
            "member_count": summary["compatibility"]["assignment_count"],
            "parameters": "3 components; 4 actions; 2 allowed per component",
            "digest": "",
        },
        {
            "generator": "complete_deterministic",
            "member_count": manifest["class_counts"]["complete"],
            "parameters": "3 states; 2 actions; 1 binary atom",
            "digest": manifest["manifest_digest"],
        },
        {
            "generator": "reversible_subset",
            "member_count": manifest["class_counts"]["reversible"],
            "parameters": "each action is a state permutation",
            "digest": manifest["manifest_digest"],
        },
        {
            "generator": "absorbing_subset",
            "member_count": manifest["class_counts"]["absorbing"],
            "parameters": "s2 fixed; every state reaches s2",
            "digest": manifest["manifest_digest"],
        },
    ]


def nonflag_search_rows() -> list[dict[str, Any]]:
    return compatibility_search()["search_rows"]


def deformation_distribution_rows() -> list[dict[str, Any]]:
    return deformation_distribution_study()["distribution_rows"]


def deformation_system_rows() -> list[dict[str, Any]]:
    return deformation_distribution_study()["system_rows"]


def sensitivity_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    compatibility = summary["compatibility"]
    deformation = summary["deformation"]
    return [
        {
            "control": "compatibility_relabeling",
            "passes": compatibility["relabeling_preserved"],
            "details": "",
        },
        {
            "control": "independent_action_negative_control",
            "passes": compatibility["independent_action_triple_realizable"],
            "details": "invalid component-specific actions fill the hollow triple",
        },
        {
            "control": "deadlock_singleton",
            "passes": not compatibility["deadlock_singleton_realizable"],
            "details": "component with no safe action is excluded",
        },
        {
            "control": "deformation_relabeling",
            "passes": deformation["relabeling_control"]["preserved"],
            "details": deformation["relabeling_control"]["system_id"],
        },
        {
            "control": "duplicate_action_structural",
            "passes": deformation["duplicate_action_control"]["structural_verdicts_preserved"],
            "details": deformation["duplicate_action_control"]["system_id"],
        },
        {
            "control": "duplicate_action_weight",
            "passes": deformation["duplicate_action_control"]["action_weight_changed"],
            "details": "diagnostic action-edge distribution changed",
        },
        {
            "control": "no_synthetic_reverse_edge",
            "passes": deformation["reverse_edge_control"]["synthetic_reverse_excluded"],
            "details": deformation["reverse_edge_control"]["system_id"],
        },
    ]


def _family_sort_key(family: Family) -> tuple[int, tuple[str, ...]]:
    return (len(family), tuple(sorted(family)))


def _family_id(family: Family) -> str:
    return "empty" if not family else "+".join(sorted(family))
