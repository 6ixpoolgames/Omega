"""Deterministic recovery facts that set up later stochastic audits."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations, product

from omega.adapters.finite_relational.facts import reachable_pairs


Observation = dict[str, str]
Target = frozenset[str]


@dataclass(frozen=True)
class DeterministicLayerFamily:
    """One finite deterministic pre-stochastic check family."""

    family_id: str
    description: str
    metrics: dict[str, object]


def generate_deterministic_layer_study() -> tuple[DeterministicLayerFamily, ...]:
    """Generate deterministic checks used before stochastic/approximate recovery."""

    return (
        _joint_bounded_recovery_family(),
        _decoder_class_strictness_family(),
        _observation_refinement_family(),
        _garbling_non_improvement_family(),
        _minimal_sufficient_observation_family(),
        _reflected_vs_stale_hidden_loss_family(),
    )


def deterministic_layer_summary() -> dict[str, object]:
    families = generate_deterministic_layer_study()
    return {
        "status": "PASS",
        "family_count": len(families),
        "families": [_family_as_dict(family) for family in families],
    }


def target_recoverable_from_observation(
    states: tuple[str, ...],
    observation: Observation,
    target: Target,
) -> bool:
    """An exact binary target is recoverable iff each observation fiber is pure."""

    return function_recoverable_from_observation(
        states,
        observation,
        {state: str(state in target).lower() for state in states},
    )


def function_recoverable_from_observation(
    states: tuple[str, ...],
    observation: Observation,
    target_function: dict[str, str],
) -> bool:
    """A finite function is recoverable iff it is constant on observation fibers."""

    _assert_total(states, observation, "observation")
    _assert_total(states, target_function, "target_function")
    for fiber in _fibers(states, observation).values():
        values = {target_function[state] for state in fiber}
        if len(values) > 1:
            return False
    return True


def observation_refines(
    states: tuple[str, ...],
    finer: Observation,
    coarser: Observation,
) -> bool:
    """`finer` refines `coarser` iff every finer fiber is inside a coarser fiber."""

    _assert_total(states, finer, "finer")
    _assert_total(states, coarser, "coarser")
    return all(
        coarser[left] == coarser[right]
        for left, right in product(states, states)
        if finer[left] == finer[right]
    )


def recoverable_targets(states: tuple[str, ...], observation: Observation) -> tuple[Target, ...]:
    """All binary targets recoverable from an observation."""

    return tuple(
        target
        for target in all_binary_targets(states)
        if target_recoverable_from_observation(states, observation, target)
    )


def minimal_sufficient_observation(states: tuple[str, ...], target: Target) -> Observation:
    """The coarsest binary observation that exactly recovers a binary target."""

    return {state: ("true" if state in target else "false") for state in states}


def all_binary_targets(states: tuple[str, ...]) -> tuple[Target, ...]:
    targets = []
    for size in range(len(states) + 1):
        for subset in combinations(states, size):
            targets.append(frozenset(subset))
    return tuple(targets)


def all_observations(states: tuple[str, ...], labels: tuple[str, ...]) -> tuple[Observation, ...]:
    return tuple(
        {state: label for state, label in zip(states, label_assignment, strict=True)}
        for label_assignment in product(labels, repeat=len(states))
    )


def _joint_bounded_recovery_family() -> DeterministicLayerFamily:
    states = ("00", "01", "10", "11")
    first_observation = {state: state[0] for state in states}
    second_observation = {state: state[1] for state in states}
    target_first = frozenset(state for state in states if state[0] == "1")
    target_second = frozenset(state for state in states if state[1] == "1")
    joint_target = {state: f"first={state[0]};second={state[1]}" for state in states}

    first_recovers_first = target_recoverable_from_observation(
        states,
        first_observation,
        target_first,
    )
    second_recovers_second = target_recoverable_from_observation(
        states,
        second_observation,
        target_second,
    )
    joint_from_first = function_recoverable_from_observation(
        states,
        first_observation,
        joint_target,
    )
    joint_from_second = function_recoverable_from_observation(
        states,
        second_observation,
        joint_target,
    )

    return DeterministicLayerFamily(
        family_id="joint_bounded_recovery_panel_failure",
        description=(
            "Two binary targets are each recoverable from a declared observation, "
            "but neither observation alone recovers the joint target."
        ),
        metrics={
            "target_first_recoverable_from_first_observation": first_recovers_first,
            "target_second_recoverable_from_second_observation": second_recovers_second,
            "joint_recoverable_from_first_observation": joint_from_first,
            "joint_recoverable_from_second_observation": joint_from_second,
            "individual_recovery_implies_joint_recovery": False,
        },
    )


def _decoder_class_strictness_family() -> DeterministicLayerFamily:
    states = ("s0", "s1", "s2", "s3")
    observation = {"s0": "red", "s1": "red", "s2": "blue", "s3": "blue"}
    target = frozenset({"s2", "s3"})
    weak_decoders = (
        {"red": "false", "blue": "false"},
        {"red": "true", "blue": "true"},
    )
    rich_decoders = weak_decoders + (
        {"red": "false", "blue": "true"},
        {"red": "true", "blue": "false"},
    )

    return DeterministicLayerFamily(
        family_id="decoder_class_strictness",
        description=(
            "The same observation/target pair can be unrecoverable for a weak "
            "constant-decoder class and recoverable for a richer Boolean class."
        ),
        metrics={
            "recoverable_by_weak_class": _any_decoder_recovers(
                states,
                observation,
                target,
                weak_decoders,
            ),
            "recoverable_by_rich_class": _any_decoder_recovers(
                states,
                observation,
                target,
                rich_decoders,
            ),
            "weak_decoder_count": len(weak_decoders),
            "rich_decoder_count": len(rich_decoders),
        },
    )


def _observation_refinement_family() -> DeterministicLayerFamily:
    states = ("00", "01", "10", "11")
    coarse = {state: state[0] for state in states}
    finer = {state: state for state in states}
    coarse_targets = set(recoverable_targets(states, coarse))
    finer_targets = set(recoverable_targets(states, finer))

    return DeterministicLayerFamily(
        family_id="observation_refinement_monotonicity",
        description=(
            "Identity observation refines first-bit observation; every target "
            "recoverable from the coarser observation remains recoverable from "
            "the finer observation."
        ),
        metrics={
            "finer_refines_coarse": observation_refines(states, finer, coarse),
            "coarse_recoverable_target_count": len(coarse_targets),
            "finer_recoverable_target_count": len(finer_targets),
            "coarse_targets_subset_of_finer_targets": coarse_targets <= finer_targets,
        },
    )


def _garbling_non_improvement_family() -> DeterministicLayerFamily:
    states = ("00", "01", "10", "11")
    source_observation = {state: state for state in states}
    garbled_observation = {state: state[0] for state in states}
    source_targets = set(recoverable_targets(states, source_observation))
    garbled_targets = set(recoverable_targets(states, garbled_observation))

    return DeterministicLayerFamily(
        family_id="deterministic_garbling_non_improvement",
        description=(
            "First-bit observation is a garbling of identity observation; it "
            "recovers a subset of the exact binary targets recoverable from the "
            "source observation."
        ),
        metrics={
            "source_refines_garbled": observation_refines(
                states,
                source_observation,
                garbled_observation,
            ),
            "source_recoverable_target_count": len(source_targets),
            "garbled_recoverable_target_count": len(garbled_targets),
            "garbled_targets_subset_of_source_targets": garbled_targets <= source_targets,
        },
    )


def _minimal_sufficient_observation_family() -> DeterministicLayerFamily:
    states = ("00", "01", "10", "11")
    target = frozenset(state for state in states if state[0] == "1")
    minimal = minimal_sufficient_observation(states, target)
    observations = all_observations(states, ("l0", "l1", "l2", "l3"))
    recovering_observations = [
        observation
        for observation in observations
        if target_recoverable_from_observation(states, observation, target)
    ]

    return DeterministicLayerFamily(
        family_id="minimal_sufficient_observation",
        description=(
            "The target-fiber observation recovers the target, and every "
            "enumerated observation that recovers the target refines it."
        ),
        metrics={
            "minimal_recovers_target": target_recoverable_from_observation(
                states,
                minimal,
                target,
            ),
            "enumerated_observation_count": len(observations),
            "recovering_observation_count": len(recovering_observations),
            "all_recovering_observations_refine_minimal": all(
                observation_refines(states, observation, minimal)
                for observation in recovering_observations
            ),
        },
    )


def _reflected_vs_stale_hidden_loss_family() -> DeterministicLayerFamily:
    states = ("a", "b", "c")
    before_edges = {("a", "b"), ("b", "c")}
    after_edges = {("a", "b")}
    source = "a"
    target = "c"
    before_path = (source, target) in reachable_pairs(set(states), before_edges)
    after_path = (source, target) in reachable_pairs(set(states), after_edges)
    stale_abstract_path = (source, target) in reachable_pairs(set(states), before_edges)
    reflected_abstract_path = (source, target) in reachable_pairs(set(states), after_edges)

    return DeterministicLayerFamily(
        family_id="reflected_vs_stale_hidden_loss",
        description=(
            "A stale abstraction hides exact reachability loss, while a reflected "
            "abstraction that tracks the after-transition does not report the lost path."
        ),
        metrics={
            "before_path": before_path,
            "after_path": after_path,
            "stale_abstraction_hidden_loss": before_path and not after_path and stale_abstract_path,
            "reflected_abstraction_hidden_loss": (
                before_path and not after_path and reflected_abstract_path
            ),
            "reflected_abstraction_reports_lost_path": reflected_abstract_path,
        },
    )


def _any_decoder_recovers(
    states: tuple[str, ...],
    observation: Observation,
    target: Target,
    decoders: tuple[dict[str, str], ...],
) -> bool:
    return any(_decoder_recovers(states, observation, target, decoder) for decoder in decoders)


def _decoder_recovers(
    states: tuple[str, ...],
    observation: Observation,
    target: Target,
    decoder: dict[str, str],
) -> bool:
    _assert_total(states, observation, "observation")
    for state in states:
        expected = "true" if state in target else "false"
        observed = observation[state]
        if decoder.get(observed) != expected:
            return False
    return True


def _fibers(states: tuple[str, ...], observation: Observation) -> dict[str, list[str]]:
    fibers: dict[str, list[str]] = defaultdict(list)
    for state in states:
        fibers[observation[state]].append(state)
    return dict(fibers)


def _assert_total(states: tuple[str, ...], mapping: dict[str, str], label: str) -> None:
    missing = sorted(set(states) - set(mapping))
    if missing:
        raise ValueError(f"{label} is missing states: {missing}")


def _family_as_dict(family: DeterministicLayerFamily) -> dict[str, object]:
    return {
        "family_id": family.family_id,
        "description": family.description,
        "metrics": family.metrics,
    }
