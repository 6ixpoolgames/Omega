from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Iterable

State = tuple[int, int, int, int]
Transform = Callable[[State], set[State]]

MODULUS = 4

FAMILIES = (
    "expanding_relation",
    "contracting_relation",
    "cyclic_relation",
    "structured_relation",
    "random_relation_control",
    "degree_preserving_control",
    "coordinate_permutation_control",
    "phase_cycle_control",
    "fixed_point_control",
    "permissive_probe_control",
    "strict_probe_control",
)


@dataclass(frozen=True)
class LandscapeSystem:
    system_id: str
    seed: int
    family: str
    states: tuple[State, ...]
    edges: dict[State, tuple[State, ...]]
    transform_names: tuple[str, ...]
    metadata: dict[str, int | str]


def enumerate_states() -> tuple[State, ...]:
    return tuple(
        (q0, q1, q2, phase)
        for q0 in range(MODULUS)
        for q1 in range(MODULUS)
        for q2 in range(MODULUS)
        for phase in range(MODULUS)
    )


def generate_system(seed: int, family: str) -> LandscapeSystem:
    if family not in FAMILIES:
        raise ValueError(f"unknown family: {family}")
    states = enumerate_states()
    base_family = _base_family(family)
    specs = _transform_specs(base_family)
    base_edges = _build_edges(states, specs)
    rng = random.Random(seed)
    if family == "random_relation_control":
        edges = _randomized_edges(states, base_edges, rng)
        transform_names = ("random_relation_matched",)
    elif family == "degree_preserving_control":
        edges = _degree_preserving_edges(states, base_edges, seed)
        transform_names = ("degree_preserving_scramble",)
    elif family == "coordinate_permutation_control":
        edges = _coordinate_permutation_edges(states, base_edges)
        transform_names = ("coordinate_permutation",)
    else:
        edges = base_edges
        transform_names = tuple(name for name, _transform in specs)
    return LandscapeSystem(
        system_id=f"{family}_{seed}",
        seed=seed,
        family=family,
        states=states,
        edges=edges,
        transform_names=transform_names,
        metadata={
            "state_coordinate_count": 4,
            "modulus": MODULUS,
            "state_count": len(states),
            "presentation": "finite_coordinate_relation",
        },
    )


def _base_family(family: str) -> str:
    if family in {
        "random_relation_control",
        "degree_preserving_control",
        "coordinate_permutation_control",
        "permissive_probe_control",
        "strict_probe_control",
    }:
        return "structured_relation"
    return family


def _transform_specs(family: str) -> tuple[tuple[str, Transform], ...]:
    if family == "expanding_relation":
        return (
            ("shift_0(+1)", lambda s: {_shift(s, 0, 1)}),
            ("shift_1(+1)", lambda s: {_shift(s, 1, 1)}),
            ("shift_2(+1)", lambda s: {_shift(s, 2, 1)}),
            ("copy_0_to_1", lambda s: {_copy(s, 0, 1)}),
            ("phase_advance", lambda s: {_phase(s)}),
        )
    if family == "contracting_relation":
        return (
            ("project_0_to_0", lambda s: {_set_coord(s, 0, 0)}),
            ("project_1_to_1", lambda s: {_set_coord(s, 1, 1)}),
            ("project_2_to_2", lambda s: {_set_coord(s, 2, 2)}),
            ("phase_advance", lambda s: {_phase(s)}),
        )
    if family == "cyclic_relation":
        return (
            ("rotate_0_1_2", lambda s: {_rotate012(s)}),
            ("phase_advance", lambda s: {_phase(s)}),
        )
    if family == "phase_cycle_control":
        return (("phase_advance", lambda s: {_phase(s)}),)
    if family == "fixed_point_control":
        return (
            ("project_to_zero", lambda _s: {(0, 0, 0, 0)}),
            ("project_to_mid", lambda _s: {(1, 1, 1, 1)}),
        )
    if family == "structured_relation":
        return (
            ("couple_0_1(+1)", lambda s: {_couple01(s, 1)}),
            ("couple_0_1(-1)", lambda s: {_couple01(s, -1)}),
            ("anti_couple_1_2(+1)", lambda s: {_anti_couple12(s, 1)}),
            ("copy_0_to_2", lambda s: {_copy(s, 0, 2)}),
            ("swap_0_2", lambda s: {_swap(s, 0, 2)}),
            ("phase_advance", lambda s: {_phase(s)}),
        )
    raise ValueError(f"unhandled family: {family}")


def _build_edges(states: Iterable[State], specs: tuple[tuple[str, Transform], ...]) -> dict[State, tuple[State, ...]]:
    edges: dict[State, tuple[State, ...]] = {}
    for state in states:
        targets: set[State] = set()
        for _name, transform in specs:
            targets.update(transform(state))
        edges[state] = tuple(sorted(targets))
    return edges


def _randomized_edges(states: tuple[State, ...], edges: dict[State, tuple[State, ...]], rng: random.Random) -> dict[State, tuple[State, ...]]:
    state_list = list(states)
    return {
        state: tuple(sorted(rng.sample(state_list, min(len(targets), len(state_list)))))
        if targets
        else tuple()
        for state, targets in edges.items()
    }


def _degree_preserving_edges(states: tuple[State, ...], edges: dict[State, tuple[State, ...]], seed: int) -> dict[State, tuple[State, ...]]:
    ordered = sorted(states, key=lambda state: (_stable_bucket(state, seed), state))
    return {
        state: tuple(ordered[(_stable_bucket(state, seed + 31) + i) % len(ordered)] for i in range(len(targets)))
        for state, targets in edges.items()
    }


def _coordinate_permutation_edges(states: tuple[State, ...], edges: dict[State, tuple[State, ...]]) -> dict[State, tuple[State, ...]]:
    out: dict[State, tuple[State, ...]] = {}
    for state in states:
        p_state = _permute(state)
        p_targets = edges[p_state]
        out[state] = tuple(sorted(_permute_back(target) for target in p_targets))
    return out


def _shift(state: State, coord: int, delta: int) -> State:
    values = list(state)
    values[coord] = (values[coord] + delta) % MODULUS
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _set_coord(state: State, coord: int, value: int) -> State:
    values = list(state)
    values[coord] = value % MODULUS
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _copy(state: State, source: int, target: int) -> State:
    values = list(state)
    values[target] = values[source]
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _swap(state: State, left: int, right: int) -> State:
    values = list(state)
    values[left], values[right] = values[right], values[left]
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _rotate012(state: State) -> State:
    q0, q1, q2, phase = state
    return (q2, q0, q1, (phase + 1) % MODULUS)


def _couple01(state: State, delta: int) -> State:
    q0, q1, q2, phase = state
    return ((q0 + delta) % MODULUS, (q1 + delta) % MODULUS, q2, (phase + 1) % MODULUS)


def _anti_couple12(state: State, delta: int) -> State:
    q0, q1, q2, phase = state
    return (q0, (q1 + delta) % MODULUS, (q2 - delta) % MODULUS, (phase + 1) % MODULUS)


def _phase(state: State) -> State:
    q0, q1, q2, phase = state
    return (q0, q1, q2, (phase + 1) % MODULUS)


def _permute(state: State) -> State:
    q0, q1, q2, phase = state
    return (q1, q2, q0, phase)


def _permute_back(state: State) -> State:
    q1, q2, q0, phase = state
    return (q0, q1, q2, phase)


def _stable_bucket(state: State, seed: int) -> int:
    total = seed * 113
    for index, value in enumerate(state):
        total += (index + 7) * (value + 13) * 71
    return total % 997
