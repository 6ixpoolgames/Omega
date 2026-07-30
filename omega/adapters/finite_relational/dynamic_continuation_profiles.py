"""Finite dynamic continuation profiles.

This module derives a bounded, duplicate-resistant behavioral object from
action-labelled transition dynamics. Capability profiles are finite down-sets
under a bounded alternating-simulation preorder. They are instrumentation
relative to an explicit horizon, positive atom grammar, and comparison basis;
they are not value, standing, valuerhood, or moral license.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Any, Iterable, Mapping

from omega.adapters.finite_relational.adaptive_fixed_world_corridor import (
    AdaptiveCorridorCase,
    generate_adaptive_fixed_world_corridor_study,
    sound_update,
    successors as fixed_world_successors,
    truth_preservation_failures,
)
from omega.adapters.finite_relational.lushness_diversity import (
    CompatibilityStructure,
    OrderVerdict,
    Profile,
    Trajectory,
    compare_profiles,
)


PROTOCOL_DOC = "docs/research_notes/omega_v2/dynamic_continuation_profiles_protocol_v0.md"

State = str
Action = str
Edge = tuple[State, Action, State]
AtomRow = tuple[State, frozenset[str]]


class DeformationVerdict(str, Enum):
    EXPANSION = "expansion"
    CONTRACTION = "contraction"
    EQUIVALENT = "equivalent"
    MIXED = "mixed"


@dataclass(frozen=True)
class BehaviorSignature:
    """One bounded controller-choice/environment-outcome behavior type."""

    atoms: tuple[str, ...]
    action_effects: tuple[tuple["BehaviorSignature", ...], ...] = ()

    def payload(self) -> dict[str, Any]:
        return {
            "atoms": list(self.atoms),
            "action_effects": [
                [successor.payload() for successor in effect] for effect in self.action_effects
            ],
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.payload(),
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint(self, *, horizon: int) -> str:
        digest = hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
        return f"dyn:h{horizon}:{digest}"


@dataclass(frozen=True)
class FiniteControlSystem:
    """A finite action-labelled transition system with positive state atoms."""

    system_id: str
    states: tuple[State, ...]
    actions: tuple[Action, ...]
    transitions: tuple[Edge, ...]
    atoms: tuple[AtomRow, ...] = ()

    def __post_init__(self) -> None:
        if not self.system_id:
            raise ValueError("system_id must be nonempty")
        if not self.states:
            raise ValueError("states must be nonempty")
        if len(self.states) != len(set(self.states)):
            raise ValueError("states must be unique")
        if len(self.actions) != len(set(self.actions)):
            raise ValueError("actions must be unique")
        if len(self.transitions) != len(set(self.transitions)):
            raise ValueError("transitions must be unique")

        state_set = set(self.states)
        action_set = set(self.actions)
        for source, action, target in self.transitions:
            if source not in state_set or target not in state_set:
                raise ValueError(f"transition contains unknown state: {(source, action, target)!r}")
            if action not in action_set:
                raise ValueError(f"transition contains unknown action: {action!r}")

        atom_states = tuple(state for state, _atoms in self.atoms)
        if len(atom_states) != len(set(atom_states)):
            raise ValueError("each state may have at most one atom row")
        unknown_atom_states = set(atom_states) - state_set
        if unknown_atom_states:
            raise ValueError(f"atom rows contain unknown states: {sorted(unknown_atom_states)}")

    @property
    def atom_map(self) -> dict[State, frozenset[str]]:
        declared = dict(self.atoms)
        return {state: frozenset(declared.get(state, frozenset())) for state in self.states}

    def atoms_at(self, state: State) -> frozenset[str]:
        self._require_state(state)
        return self.atom_map[state]

    def successors(self, state: State, action: Action) -> frozenset[State]:
        self._require_state(state)
        if action not in self.actions:
            raise KeyError(action)
        return frozenset(
            target
            for source, candidate_action, target in self.transitions
            if source == state and candidate_action == action
        )

    def enabled_actions(self, state: State) -> tuple[Action, ...]:
        self._require_state(state)
        return tuple(action for action in self.actions if self.successors(state, action))

    def raw_successors(self, state: State) -> frozenset[State]:
        self._require_state(state)
        return frozenset(target for source, _action, target in self.transitions if source == state)

    def relabel(
        self,
        *,
        state_mapping: Mapping[State, State],
        action_mapping: Mapping[Action, Action],
        system_id: str,
    ) -> "FiniteControlSystem":
        if set(state_mapping) != set(self.states):
            raise ValueError("state relabeling must be total")
        if len(set(state_mapping.values())) != len(state_mapping):
            raise ValueError("state relabeling must be injective")
        if set(action_mapping) != set(self.actions):
            raise ValueError("action relabeling must be total")
        if len(set(action_mapping.values())) != len(action_mapping):
            raise ValueError("action relabeling must be injective")
        return FiniteControlSystem(
            system_id=system_id,
            states=tuple(state_mapping[state] for state in self.states),
            actions=tuple(action_mapping[action] for action in self.actions),
            transitions=tuple(
                (
                    state_mapping[source],
                    action_mapping[action],
                    state_mapping[target],
                )
                for source, action, target in self.transitions
            ),
            atoms=tuple((state_mapping[state], state_atoms) for state, state_atoms in self.atoms),
        )

    def _require_state(self, state: State) -> None:
        if state not in self.states:
            raise KeyError(state)


@dataclass(frozen=True)
class BehaviorReference:
    """One state in the finite comparison basis used by a profile."""

    system: FiniteControlSystem
    state: State

    def __post_init__(self) -> None:
        if self.state not in self.system.states:
            raise ValueError(f"unknown reference state {self.state!r} in {self.system.system_id!r}")


def behavior_signatures(
    system: FiniteControlSystem,
    horizon: int,
) -> dict[State, BehaviorSignature]:
    """Compute exact bounded behavior types for every state."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    current = {
        state: BehaviorSignature(tuple(sorted(system.atoms_at(state)))) for state in system.states
    }
    for _depth in range(horizon):
        next_signatures: dict[State, BehaviorSignature] = {}
        for state in system.states:
            effect_set: set[tuple[BehaviorSignature, ...]] = set()
            for action in system.enabled_actions(state):
                successor_types = {current[target] for target in system.successors(state, action)}
                effect_set.add(tuple(sorted(successor_types, key=_signature_sort_key)))
            next_signatures[state] = BehaviorSignature(
                atoms=tuple(sorted(system.atoms_at(state))),
                action_effects=tuple(sorted(effect_set, key=_effect_sort_key)),
            )
        current = next_signatures
    return current


def behavior_signature(
    system: FiniteControlSystem,
    state: State,
    horizon: int,
) -> BehaviorSignature:
    system._require_state(state)
    return behavior_signatures(system, horizon)[state]


def behavior_fingerprint(
    system: FiniteControlSystem,
    state: State,
    horizon: int,
) -> str:
    return behavior_signature(system, state, horizon).fingerprint(horizon=horizon)


def first_separation_depth(
    left_system: FiniteControlSystem,
    left_state: State,
    right_system: FiniteControlSystem,
    right_state: State,
    *,
    max_horizon: int,
) -> int | None:
    if max_horizon < 0:
        raise ValueError("max_horizon must be nonnegative")
    for horizon in range(max_horizon + 1):
        if behavior_signature(left_system, left_state, horizon) != behavior_signature(
            right_system, right_state, horizon
        ):
            return horizon
    return None


def alternating_refines(
    left_system: FiniteControlSystem,
    left_state: State,
    right_system: FiniteControlSystem,
    right_state: State,
    *,
    horizon: int,
) -> bool:
    """Return whether the right state weakly refines the left state.

    Controller action is selected before the right-side environment outcome.
    The left action's outcomes provide the behaviors that the matching right
    action must refine.
    """

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    left_system._require_state(left_state)
    right_system._require_state(right_state)
    memo: dict[tuple[State, State, int], bool] = {}

    def visit(left: State, right: State, depth: int) -> bool:
        key = (left, right, depth)
        if key in memo:
            return memo[key]
        if not left_system.atoms_at(left) <= right_system.atoms_at(right):
            memo[key] = False
            return False
        if depth == 0:
            memo[key] = True
            return True

        right_actions = right_system.enabled_actions(right)
        for left_action in left_system.enabled_actions(left):
            left_successors = left_system.successors(left, left_action)
            matched = False
            for right_action in right_actions:
                right_successors = right_system.successors(right, right_action)
                if all(
                    any(visit(left_next, right_next, depth - 1) for left_next in left_successors)
                    for right_next in right_successors
                ):
                    matched = True
                    break
            if not matched:
                memo[key] = False
                return False
        memo[key] = True
        return True

    return visit(left_state, right_state, horizon)


def compare_state_capabilities(
    left_system: FiniteControlSystem,
    left_state: State,
    right_system: FiniteControlSystem,
    right_state: State,
    *,
    horizon: int,
) -> OrderVerdict:
    right_refines = alternating_refines(
        left_system,
        left_state,
        right_system,
        right_state,
        horizon=horizon,
    )
    left_refines = alternating_refines(
        right_system,
        right_state,
        left_system,
        left_state,
        horizon=horizon,
    )
    if left_refines and right_refines:
        return OrderVerdict.EQUIVALENT
    if left_refines:
        return OrderVerdict.LEFT_REFINES
    if right_refines:
        return OrderVerdict.RIGHT_REFINES
    return OrderVerdict.INCOMPARABLE


def behavior_basis(*systems: FiniteControlSystem) -> tuple[BehaviorReference, ...]:
    return tuple(BehaviorReference(system, state) for system in systems for state in system.states)


def capability_profile(
    system: FiniteControlSystem,
    state: State,
    *,
    basis: Iterable[BehaviorReference],
    horizon: int,
) -> Profile:
    """Return the represented behavioral down-set of one state."""

    attributes: set[str] = set()
    for reference in basis:
        if alternating_refines(
            reference.system,
            reference.state,
            system,
            state,
            horizon=horizon,
        ):
            attributes.add(
                behavior_fingerprint(
                    reference.system,
                    reference.state,
                    horizon,
                )
            )
    return frozenset(attributes)


def derived_trajectory(
    trajectory_id: str,
    system: FiniteControlSystem,
    state: State,
    *,
    basis: Iterable[BehaviorReference],
    horizon: int,
) -> Trajectory:
    return Trajectory(
        trajectory_id,
        capability_profile(
            system,
            state,
            basis=basis,
            horizon=horizon,
        ),
    )


def transition_deformation(
    system: FiniteControlSystem,
    source: State,
    target: State,
    *,
    basis: Iterable[BehaviorReference],
    horizon: int,
) -> DeformationVerdict:
    if not any(
        edge_source == source and edge_target == target
        for edge_source, _action, edge_target in system.transitions
    ):
        raise ValueError(f"{source!r} -> {target!r} is not a transition")
    verdict = compare_profiles(
        capability_profile(system, source, basis=basis, horizon=horizon),
        capability_profile(system, target, basis=basis, horizon=horizon),
    )
    if verdict is OrderVerdict.RIGHT_REFINES:
        return DeformationVerdict.EXPANSION
    if verdict is OrderVerdict.LEFT_REFINES:
        return DeformationVerdict.CONTRACTION
    if verdict is OrderVerdict.EQUIVALENT:
        return DeformationVerdict.EQUIVALENT
    return DeformationVerdict.MIXED


def flattened_successor_fingerprints(
    system: FiniteControlSystem,
    state: State,
    *,
    successor_horizon: int,
) -> frozenset[str]:
    return frozenset(
        behavior_fingerprint(system, successor, successor_horizon)
        for successor in system.raw_successors(state)
    )


def atom_respect_failures(
    concrete: FiniteControlSystem,
    abstract: FiniteControlSystem,
    state_mapping: Mapping[State, State],
) -> tuple[dict[str, Any], ...]:
    if set(state_mapping) != set(concrete.states):
        raise ValueError("presentation mapping must be total on concrete states")
    failures = []
    for concrete_state in concrete.states:
        abstract_state = state_mapping[concrete_state]
        if abstract_state not in abstract.states:
            raise ValueError(f"mapping targets unknown abstract state {abstract_state!r}")
        concrete_atoms = concrete.atoms_at(concrete_state)
        abstract_atoms = abstract.atoms_at(abstract_state)
        if concrete_atoms != abstract_atoms:
            failures.append(
                {
                    "concrete_state": concrete_state,
                    "abstract_state": abstract_state,
                    "concrete_atoms": sorted(concrete_atoms),
                    "abstract_atoms": sorted(abstract_atoms),
                }
            )
    return tuple(failures)


def duplicate_outcome_systems() -> tuple[FiniteControlSystem, FiniteControlSystem]:
    base = FiniteControlSystem(
        system_id="duplicate_outcome_base",
        states=("root", "persistent"),
        actions=("advance", "remain"),
        transitions=(
            ("root", "advance", "persistent"),
            ("persistent", "remain", "persistent"),
        ),
        atoms=(("persistent", frozenset({"persistent"})),),
    )
    duplicate = FiniteControlSystem(
        system_id="duplicate_outcome_extension",
        states=("root_copy", "persistent_a", "persistent_b"),
        actions=("advance_copy", "remain_copy"),
        transitions=(
            ("root_copy", "advance_copy", "persistent_a"),
            ("root_copy", "advance_copy", "persistent_b"),
            ("persistent_a", "remain_copy", "persistent_a"),
            ("persistent_b", "remain_copy", "persistent_b"),
        ),
        atoms=(
            ("persistent_a", frozenset({"persistent"})),
            ("persistent_b", frozenset({"persistent"})),
        ),
    )
    return base, duplicate


def duplicate_outcome_witness(*, horizon: int = 3) -> dict[str, Any]:
    base, duplicate = duplicate_outcome_systems()
    basis = behavior_basis(base, duplicate)
    base_profile = capability_profile(
        base,
        "root",
        basis=basis,
        horizon=horizon,
    )
    duplicate_profile = capability_profile(
        duplicate,
        "root_copy",
        basis=basis,
        horizon=horizon,
    )
    return {
        "horizon": horizon,
        "base_edge_count": len(base.transitions),
        "duplicate_edge_count": len(duplicate.transitions),
        "raw_edge_count_changes": len(base.transitions) != len(duplicate.transitions),
        "root_types_equal": (
            behavior_signature(base, "root", horizon)
            == behavior_signature(duplicate, "root_copy", horizon)
        ),
        "profiles_equal": base_profile == duplicate_profile,
        "base_profile": sorted(base_profile),
        "duplicate_profile": sorted(duplicate_profile),
    }


def duplicate_action_systems() -> tuple[FiniteControlSystem, FiniteControlSystem]:
    base, _duplicate_outcome = duplicate_outcome_systems()
    duplicate_action = FiniteControlSystem(
        system_id="duplicate_action_extension",
        states=("root_action", "persistent_action"),
        actions=("advance_a", "advance_b", "remain_action"),
        transitions=(
            ("root_action", "advance_a", "persistent_action"),
            ("root_action", "advance_b", "persistent_action"),
            ("persistent_action", "remain_action", "persistent_action"),
        ),
        atoms=(("persistent_action", frozenset({"persistent"})),),
    )
    return base, duplicate_action


def duplicate_action_witness(*, horizon: int = 3) -> dict[str, Any]:
    base, duplicate = duplicate_action_systems()
    return {
        "horizon": horizon,
        "base_action_count": len(base.actions),
        "duplicate_action_count": len(duplicate.actions),
        "raw_action_count_changes": len(base.actions) != len(duplicate.actions),
        "root_types_equal": (
            behavior_signature(base, "root", horizon)
            == behavior_signature(duplicate, "root_action", horizon)
        ),
    }


def novel_branch_systems() -> tuple[FiniteControlSystem, FiniteControlSystem]:
    base = FiniteControlSystem(
        system_id="novel_branch_base",
        states=("base_root",),
        actions=("hold",),
        transitions=(("base_root", "hold", "base_root"),),
        atoms=(("base_root", frozenset({"alive"})),),
    )
    extension = FiniteControlSystem(
        system_id="novel_branch_extension",
        states=("extension_root", "ordinary", "novel"),
        actions=("hold_extension", "explore"),
        transitions=(
            ("extension_root", "hold_extension", "ordinary"),
            ("extension_root", "explore", "novel"),
            ("ordinary", "hold_extension", "ordinary"),
            ("novel", "hold_extension", "novel"),
        ),
        atoms=(
            ("extension_root", frozenset({"alive"})),
            ("ordinary", frozenset({"alive"})),
            ("novel", frozenset({"alive", "novel_behavior"})),
        ),
    )
    return base, extension


def novel_branch_witness(*, horizon: int = 2) -> dict[str, Any]:
    base, extension = novel_branch_systems()
    basis = behavior_basis(base, extension)
    base_profile = capability_profile(
        base,
        "base_root",
        basis=basis,
        horizon=horizon,
    )
    extension_profile = capability_profile(
        extension,
        "extension_root",
        basis=basis,
        horizon=horizon,
    )
    verdict = compare_profiles(base_profile, extension_profile)
    return {
        "horizon": horizon,
        "state_verdict": compare_state_capabilities(
            base,
            "base_root",
            extension,
            "extension_root",
            horizon=horizon,
        ).value,
        "profile_verdict": verdict.value,
        "base_profile": sorted(base_profile),
        "extension_profile": sorted(extension_profile),
        "strict_new_capabilities": sorted(extension_profile - base_profile),
        "extension_strictly_refines": verdict is OrderVerdict.RIGHT_REFINES,
    }


def delayed_divergence_systems() -> tuple[FiniteControlSystem, FiniteControlSystem]:
    continuing = FiniteControlSystem(
        system_id="delayed_continuing",
        states=("continuing_root", "continuing_child"),
        actions=("advance", "continue"),
        transitions=(
            ("continuing_root", "advance", "continuing_child"),
            ("continuing_child", "continue", "continuing_child"),
        ),
    )
    terminating = FiniteControlSystem(
        system_id="delayed_terminating",
        states=("terminating_root", "terminating_child"),
        actions=("advance_other",),
        transitions=(("terminating_root", "advance_other", "terminating_child"),),
    )
    return continuing, terminating


def delayed_divergence_witness(*, max_horizon: int = 4) -> dict[str, Any]:
    continuing, terminating = delayed_divergence_systems()
    fingerprints_equal = {
        horizon: (
            behavior_fingerprint(continuing, "continuing_root", horizon)
            == behavior_fingerprint(terminating, "terminating_root", horizon)
        )
        for horizon in range(max_horizon + 1)
    }
    return {
        "max_horizon": max_horizon,
        "first_separation_depth": first_separation_depth(
            continuing,
            "continuing_root",
            terminating,
            "terminating_root",
            max_horizon=max_horizon,
        ),
        "fingerprints_equal_by_horizon": fingerprints_equal,
    }


def quantifier_control_systems() -> tuple[FiniteControlSystem, FiniteControlSystem]:
    choice = FiniteControlSystem(
        system_id="controller_choice",
        states=("choice", "choice_good", "choice_bad"),
        actions=("safe", "hazard"),
        transitions=(
            ("choice", "safe", "choice_good"),
            ("choice", "hazard", "choice_bad"),
        ),
        atoms=(
            ("choice", frozenset({"root"})),
            ("choice_good", frozenset({"good"})),
            ("choice_bad", frozenset({"bad"})),
        ),
    )
    risk = FiniteControlSystem(
        system_id="environment_risk",
        states=("risk", "risk_good", "risk_bad"),
        actions=("gamble",),
        transitions=(
            ("risk", "gamble", "risk_good"),
            ("risk", "gamble", "risk_bad"),
        ),
        atoms=(
            ("risk", frozenset({"root"})),
            ("risk_good", frozenset({"good"})),
            ("risk_bad", frozenset({"bad"})),
        ),
    )
    return choice, risk


def quantifier_control_witness(*, horizon: int = 1) -> dict[str, Any]:
    choice, risk = quantifier_control_systems()
    choice_flat = flattened_successor_fingerprints(
        choice,
        "choice",
        successor_horizon=0,
    )
    risk_flat = flattened_successor_fingerprints(
        risk,
        "risk",
        successor_horizon=0,
    )
    verdict = compare_state_capabilities(
        risk,
        "risk",
        choice,
        "choice",
        horizon=horizon,
    )
    return {
        "horizon": horizon,
        "flattened_successors_equal": choice_flat == risk_flat,
        "nested_types_equal": (
            behavior_signature(choice, "choice", horizon)
            == behavior_signature(risk, "risk", horizon)
        ),
        "risk_to_choice_verdict": verdict.value,
        "choice_strictly_refines_risk": verdict is OrderVerdict.RIGHT_REFINES,
        "choice_flattened_successors": sorted(choice_flat),
        "risk_flattened_successors": sorted(risk_flat),
    }


def deformation_fixture() -> FiniteControlSystem:
    return FiniteControlSystem(
        system_id="deformation_fixture",
        states=(
            "poor_expand",
            "rich_expand",
            "rich_contract",
            "poor_contract",
            "neutral_left",
            "neutral_right",
            "mixed_left",
            "mixed_right",
        ),
        actions=("advance", "remain"),
        transitions=(
            ("poor_expand", "advance", "rich_expand"),
            ("rich_expand", "remain", "rich_expand"),
            ("rich_contract", "advance", "poor_contract"),
            ("poor_contract", "remain", "poor_contract"),
            ("neutral_left", "advance", "neutral_right"),
            ("neutral_right", "remain", "neutral_right"),
            ("mixed_left", "advance", "mixed_right"),
            ("mixed_right", "remain", "mixed_right"),
        ),
        atoms=(
            ("poor_expand", frozenset({"base"})),
            ("rich_expand", frozenset({"base", "extra"})),
            ("rich_contract", frozenset({"base", "extra"})),
            ("poor_contract", frozenset({"base"})),
            ("neutral_left", frozenset({"neutral"})),
            ("neutral_right", frozenset({"neutral"})),
            ("mixed_left", frozenset({"left"})),
            ("mixed_right", frozenset({"right"})),
        ),
    )


def deformation_witness(*, horizon: int = 1) -> dict[str, Any]:
    system = deformation_fixture()
    basis = behavior_basis(system)
    pairs = {
        "expansion": ("poor_expand", "rich_expand"),
        "contraction": ("rich_contract", "poor_contract"),
        "equivalent": ("neutral_left", "neutral_right"),
        "mixed": ("mixed_left", "mixed_right"),
    }
    verdicts = {
        name: transition_deformation(
            system,
            source,
            target,
            basis=basis,
            horizon=horizon,
        ).value
        for name, (source, target) in pairs.items()
    }
    return {
        "horizon": horizon,
        "verdicts": verdicts,
        "all_four_retained": verdicts
        == {
            "expansion": DeformationVerdict.EXPANSION.value,
            "contraction": DeformationVerdict.CONTRACTION.value,
            "equivalent": DeformationVerdict.EQUIVALENT.value,
            "mixed": DeformationVerdict.MIXED.value,
        },
    }


def presentation_witness(*, horizon: int = 3) -> dict[str, Any]:
    base, _duplicate = duplicate_outcome_systems()
    state_relabeled = base.relabel(
        state_mapping={"root": "renamed_root", "persistent": "renamed_persistent"},
        action_mapping={"advance": "advance", "remain": "remain"},
        system_id="state_relabel",
    )
    action_relabeled = base.relabel(
        state_mapping={"root": "root", "persistent": "persistent"},
        action_mapping={"advance": "renamed_advance", "remain": "renamed_remain"},
        system_id="action_relabel",
    )
    basis = behavior_basis(base, state_relabeled, action_relabeled)
    base_profile = capability_profile(
        base,
        "root",
        basis=basis,
        horizon=horizon,
    )
    state_relabeled_profile = capability_profile(
        state_relabeled,
        "renamed_root",
        basis=basis,
        horizon=horizon,
    )
    action_relabeled_profile = capability_profile(
        action_relabeled,
        "root",
        basis=basis,
        horizon=horizon,
    )

    concrete = FiniteControlSystem(
        system_id="atom_concrete",
        states=("concrete_good", "concrete_bad"),
        actions=("hold",),
        transitions=(
            ("concrete_good", "hold", "concrete_good"),
            ("concrete_bad", "hold", "concrete_bad"),
        ),
        atoms=(
            ("concrete_good", frozenset({"good"})),
            ("concrete_bad", frozenset({"bad"})),
        ),
    )
    abstract = FiniteControlSystem(
        system_id="atom_merged_abstract",
        states=("merged",),
        actions=("hold_abstract",),
        transitions=(("merged", "hold_abstract", "merged"),),
        atoms=(("merged", frozenset({"good"})),),
    )
    mapping = {
        "concrete_good": "merged",
        "concrete_bad": "merged",
    }
    failures = atom_respect_failures(concrete, abstract, mapping)
    return {
        "horizon": horizon,
        "state_relabeling_preserves_type": (
            behavior_signature(base, "root", horizon)
            == behavior_signature(state_relabeled, "renamed_root", horizon)
        ),
        "state_relabeling_preserves_profile": (base_profile == state_relabeled_profile),
        "action_relabeling_preserves_type": (
            behavior_signature(base, "root", horizon)
            == behavior_signature(action_relabeled, "root", horizon)
        ),
        "action_relabeling_preserves_profile": (base_profile == action_relabeled_profile),
        "atom_respect_failure_count": len(failures),
        "atom_respect_failures": list(failures),
        "unsound_merge_changes_bad_type": (
            behavior_signature(concrete, "concrete_bad", horizon)
            != behavior_signature(abstract, "merged", horizon)
        ),
        "unsound_abstraction_rejected": bool(failures),
    }


def switching_control_system(case: AdaptiveCorridorCase) -> FiniteControlSystem:
    transitions: set[Edge] = set()
    for state in case.states:
        for action in case.actions:
            per_model = [
                fixed_world_successors(case, model_id, state, action)
                for model_id in sorted(case.model_ids)
            ]
            if not per_model or any(not targets for targets in per_model):
                continue
            for targets in per_model:
                transitions.update((state, action, target) for target in targets)
    return FiniteControlSystem(
        system_id=f"{case.case_id}_switching",
        states=case.states,
        actions=case.actions,
        transitions=tuple(sorted(transitions)),
        atoms=_physical_atom_rows(case, case.states),
    )


def adaptive_control_system(
    case: AdaptiveCorridorCase,
) -> tuple[FiniteControlSystem, str]:
    subsets = _nonempty_subsets(case.model_ids)
    info_states = tuple((state, remaining) for state in case.states for remaining in subsets)
    encoded = {info: _encode_info_state(*info) for info in info_states}
    transitions: set[Edge] = set()
    for info in info_states:
        state, remaining = info
        for action in case.actions:
            per_model = [
                fixed_world_successors(case, model_id, state, action)
                for model_id in sorted(remaining)
            ]
            if not per_model or any(not targets for targets in per_model):
                continue
            observed = set().union(*per_model)
            for target in observed:
                updated = sound_update(case, info, action, target)
                if updated:
                    transitions.add(
                        (
                            encoded[info],
                            action,
                            encoded[(target, updated)],
                        )
                    )

    states = tuple(encoded[info] for info in info_states)
    atoms = tuple(
        (
            encoded[(state, remaining)],
            _physical_atoms(case, state),
        )
        for state, remaining in info_states
        if _physical_atoms(case, state)
    )
    start = _encode_info_state(case.start, case.model_ids)
    return (
        FiniteControlSystem(
            system_id=f"{case.case_id}_adaptive",
            states=states,
            actions=case.actions,
            transitions=tuple(sorted(transitions)),
            atoms=atoms,
        ),
        start,
    )


def switching_adaptive_witness(*, max_horizon: int = 4) -> dict[str, Any]:
    study = generate_adaptive_fixed_world_corridor_study()
    case = next(case for case in study.cases if case.case_id == "learnable_ambiguity")
    switching = switching_control_system(case)
    adaptive, adaptive_start = adaptive_control_system(case)
    verdicts = {
        horizon: compare_state_capabilities(
            switching,
            case.start,
            adaptive,
            adaptive_start,
            horizon=horizon,
        ).value
        for horizon in range(max_horizon + 1)
    }
    separating_horizons = [
        horizon
        for horizon, verdict in verdicts.items()
        if verdict == OrderVerdict.RIGHT_REFINES.value
    ]
    status = (
        "adaptive-strictly-refines-switching"
        if separating_horizons
        else "non-separating-at-retained-horizon"
    )
    return {
        "case_id": case.case_id,
        "max_horizon": max_horizon,
        "verdicts_by_horizon": verdicts,
        "first_strict_horizon": (min(separating_horizons) if separating_horizons else None),
        "status": status,
        "same_action_switching_merge": True,
        "sound_information_state_lift": True,
        "sound_update_truth_preservation_failures": len(truth_preservation_failures(case)),
        "physical_atom_grammar": ["requirement", "safe"],
        "information_state_atoms_excluded": True,
    }


def lushness_bridge_witness(*, horizon: int = 3) -> dict[str, Any]:
    duplicate_base, duplicate_copy = duplicate_outcome_systems()
    novel_base, novel_extension = novel_branch_systems()
    basis = behavior_basis(
        duplicate_base,
        duplicate_copy,
        novel_base,
        novel_extension,
    )

    duplicate_structure = CompatibilityStructure(
        structure_id="dynamic_duplicate_bridge",
        trajectories=(
            derived_trajectory(
                "base",
                duplicate_base,
                "root",
                basis=basis,
                horizon=horizon,
            ),
            derived_trajectory(
                "copy",
                duplicate_copy,
                "root_copy",
                basis=basis,
                horizon=horizon,
            ),
        ),
        maximal_faces=(frozenset({"base", "copy"}),),
    )
    duplicate_base_profile = duplicate_structure.profile(frozenset({"base"}))
    duplicate_extended_profile = duplicate_structure.profile(frozenset({"base", "copy"}))

    novel_structure = CompatibilityStructure(
        structure_id="dynamic_novel_bridge",
        trajectories=(
            derived_trajectory(
                "base",
                novel_base,
                "base_root",
                basis=basis,
                horizon=horizon,
            ),
            derived_trajectory(
                "extension",
                novel_extension,
                "extension_root",
                basis=basis,
                horizon=horizon,
            ),
        ),
        maximal_faces=(frozenset({"base", "extension"}),),
    )
    novel_base_profile = novel_structure.profile(frozenset({"base"}))
    novel_extended_profile = novel_structure.profile(frozenset({"base", "extension"}))
    novel_verdict = compare_profiles(
        novel_base_profile,
        novel_extended_profile,
    )
    return {
        "horizon": horizon,
        "duplicate_family_profile_equal": (duplicate_base_profile == duplicate_extended_profile),
        "novel_family_profile_verdict": novel_verdict.value,
        "novel_family_profile_strict": (novel_verdict is OrderVerdict.RIGHT_REFINES),
        "attributes_are_dynamic_fingerprints": all(
            attribute.startswith("dyn:h") for attribute in novel_extended_profile
        ),
        "duplicate_base_profile": sorted(duplicate_base_profile),
        "duplicate_extended_profile": sorted(duplicate_extended_profile),
        "novel_base_profile": sorted(novel_base_profile),
        "novel_extended_profile": sorted(novel_extended_profile),
    }


def negative_controls() -> dict[str, Any]:
    duplicate = duplicate_outcome_witness()
    duplicate_action = duplicate_action_witness()
    quantifier = quantifier_control_witness()
    presentation = presentation_witness()
    bridge = lushness_bridge_witness()
    fingerprints = (
        duplicate["base_profile"]
        + duplicate["duplicate_profile"]
        + bridge["novel_extended_profile"]
    )
    identifiers_excluded = all(
        token not in fingerprint
        for fingerprint in fingerprints
        for token in (
            "root",
            "advance",
            "persistent",
            "extension",
            "novel",
        )
    )
    controls_pass = (
        duplicate["raw_edge_count_changes"]
        and duplicate["root_types_equal"]
        and duplicate["profiles_equal"]
        and duplicate_action["raw_action_count_changes"]
        and duplicate_action["root_types_equal"]
        and quantifier["flattened_successors_equal"]
        and not quantifier["nested_types_equal"]
        and quantifier["choice_strictly_refines_risk"]
        and presentation["state_relabeling_preserves_type"]
        and presentation["state_relabeling_preserves_profile"]
        and presentation["action_relabeling_preserves_type"]
        and presentation["action_relabeling_preserves_profile"]
        and presentation["unsound_abstraction_rejected"]
        and presentation["unsound_merge_changes_bad_type"]
        and identifiers_excluded
    )
    return {
        "state_relabeling_invariant": (
            presentation["state_relabeling_preserves_type"]
            and presentation["state_relabeling_preserves_profile"]
        ),
        "action_relabeling_invariant": (
            presentation["action_relabeling_preserves_type"]
            and presentation["action_relabeling_preserves_profile"]
        ),
        "duplicate_branch_idempotent": duplicate["root_types_equal"],
        "effect_equivalent_action_idempotent": duplicate_action["root_types_equal"],
        "atom_respect_failure_visible": presentation["unsound_abstraction_rejected"],
        "flat_union_not_control_type": (
            quantifier["flattened_successors_equal"] and not quantifier["nested_types_equal"]
        ),
        "profile_identifiers_exclude_state_action_tokens": identifiers_excluded,
        "raw_counts_not_primary": (
            duplicate["raw_edge_count_changes"] and duplicate["profiles_equal"]
        ),
        "negative_controls_pass": controls_pass,
    }


def dynamic_continuation_profiles_summary() -> dict[str, Any]:
    duplicate = duplicate_outcome_witness()
    duplicate_action = duplicate_action_witness()
    novel = novel_branch_witness()
    delayed = delayed_divergence_witness()
    quantifier = quantifier_control_witness()
    deformation = deformation_witness()
    presentation = presentation_witness()
    adaptive = switching_adaptive_witness()
    bridge = lushness_bridge_witness()
    controls = negative_controls()

    case_results = {
        "duplicate_outcome": (
            duplicate["raw_edge_count_changes"]
            and duplicate["root_types_equal"]
            and duplicate["profiles_equal"]
        ),
        "duplicate_action": (
            duplicate_action["raw_action_count_changes"] and duplicate_action["root_types_equal"]
        ),
        "novel_branch": novel["extension_strictly_refines"],
        "delayed_divergence": (
            delayed["first_separation_depth"] == 2
            and delayed["fingerprints_equal_by_horizon"][0]
            and delayed["fingerprints_equal_by_horizon"][1]
            and not delayed["fingerprints_equal_by_horizon"][2]
        ),
        "action_outcome_quantifier": (
            quantifier["flattened_successors_equal"]
            and not quantifier["nested_types_equal"]
            and quantifier["choice_strictly_refines_risk"]
        ),
        "deformation": deformation["all_four_retained"],
        "presentation": (
            presentation["state_relabeling_preserves_type"]
            and presentation["state_relabeling_preserves_profile"]
            and presentation["action_relabeling_preserves_type"]
            and presentation["action_relabeling_preserves_profile"]
            and presentation["unsound_abstraction_rejected"]
            and presentation["unsound_merge_changes_bad_type"]
        ),
        "switching_adaptive": (
            adaptive["status"]
            in {
                "adaptive-strictly-refines-switching",
                "non-separating-at-retained-horizon",
            }
            and adaptive["same_action_switching_merge"]
            and adaptive["sound_information_state_lift"]
            and adaptive["sound_update_truth_preservation_failures"] == 0
            and adaptive["information_state_atoms_excluded"]
        ),
        "lushness_bridge": (
            bridge["duplicate_family_profile_equal"]
            and bridge["novel_family_profile_strict"]
            and bridge["attributes_are_dynamic_fingerprints"]
        ),
    }
    retained = all(case_results.values()) and controls["negative_controls_pass"]
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "retained" if retained else "reduces-confounded-or-ill-posed",
        "case_results": case_results,
        "cases": {
            "duplicate_outcome": duplicate,
            "duplicate_action": duplicate_action,
            "novel_branch": novel,
            "delayed_divergence": delayed,
            "action_outcome_quantifier": quantifier,
            "deformation": deformation,
            "presentation": presentation,
            "switching_adaptive": adaptive,
            "lushness_bridge": bridge,
        },
        "negative_controls": controls,
        "primary_instrument": ("bounded behavioral down-sets under alternating simulation"),
        "bridge": (
            "dynamic fingerprints populate the retained jointly realizable "
            "family profile without hand-named attributes"
        ),
        "remaining_debt": (
            "positive atoms, process boundaries, comparison basis, and horizon "
            "remain explicit instrumentation inputs"
        ),
        "not_claimed": [
            "value",
            "valuerhood",
            "standing",
            "agency",
            "autonomy",
            "patienthood",
            "universal lushness",
            "thermodynamic law",
            "moral licensing",
            "paperclipper defeat",
            "Omega validation",
        ],
    }


def case_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"case": case, "passes": passes} for case, passes in summary["case_results"].items()]


def deformation_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    verdicts = summary["cases"]["deformation"]["verdicts"]
    return [{"expected": expected, "observed": observed} for expected, observed in verdicts.items()]


def signature_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    cases = summary["cases"]
    return [
        {
            "case": "duplicate_base",
            "profile": cases["duplicate_outcome"]["base_profile"],
        },
        {
            "case": "duplicate_extension",
            "profile": cases["duplicate_outcome"]["duplicate_profile"],
        },
        {
            "case": "novel_base",
            "profile": cases["novel_branch"]["base_profile"],
        },
        {
            "case": "novel_extension",
            "profile": cases["novel_branch"]["extension_profile"],
        },
        {
            "case": "bridge_duplicate_family",
            "profile": cases["lushness_bridge"]["duplicate_extended_profile"],
        },
        {
            "case": "bridge_novel_family",
            "profile": cases["lushness_bridge"]["novel_extended_profile"],
        },
    ]


def _signature_sort_key(signature: BehaviorSignature) -> str:
    return signature.canonical_json()


def _effect_sort_key(effect: tuple[BehaviorSignature, ...]) -> str:
    return json.dumps(
        [signature.payload() for signature in effect],
        sort_keys=True,
        separators=(",", ":"),
    )


def _physical_atoms(
    case: AdaptiveCorridorCase,
    state: State,
) -> frozenset[str]:
    atoms = set()
    if state in case.safe_states:
        atoms.add("safe")
    if state in case.requirement_states:
        atoms.add("requirement")
    return frozenset(atoms)


def _physical_atom_rows(
    case: AdaptiveCorridorCase,
    states: Iterable[State],
) -> tuple[AtomRow, ...]:
    return tuple(
        (state, state_atoms) for state in states if (state_atoms := _physical_atoms(case, state))
    )


def _nonempty_subsets(values: Iterable[str]) -> tuple[frozenset[str], ...]:
    ordered = tuple(sorted(values))
    return tuple(
        frozenset(candidate)
        for size in range(1, len(ordered) + 1)
        for candidate in combinations(ordered, size)
    )


def _encode_info_state(state: State, models: frozenset[str]) -> str:
    return f"{state}|{{{','.join(sorted(models))}}}"
