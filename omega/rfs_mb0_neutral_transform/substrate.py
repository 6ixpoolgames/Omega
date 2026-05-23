from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Iterable

State = tuple[int, int, int, int, int, int]
Transform = Callable[[State], set[State]]

MODULUS = 3
NONPHASE_COORDS = 5

FAMILIES = (
    "independent_block_transforms",
    "coupled_block_transforms",
    "anti_correlated_block_transforms",
    "shared_constraint_conflict",
    "phase_cycle_control",
    "fixed_point_control",
    "random_transform_control",
    "degree_preserving_transform_control",
    "equivalence_permissive_control",
    "equivalence_strict_control",
)


@dataclass(frozen=True)
class NeutralSystem:
    system_id: str
    seed: int
    family: str
    states: tuple[State, ...]
    edges: dict[State, tuple[State, ...]]
    initial_state: State
    transform_names: tuple[str, ...]
    extractor_mode: str
    metadata: dict[str, int | str]


def enumerate_states() -> tuple[State, ...]:
    return tuple(
        (q0, q1, q2, q3, q4, phase)
        for q0 in range(MODULUS)
        for q1 in range(MODULUS)
        for q2 in range(MODULUS)
        for q3 in range(MODULUS)
        for q4 in range(MODULUS)
        for phase in range(MODULUS)
    )


def generate_system(seed: int, family: str) -> NeutralSystem:
    if family not in FAMILIES:
        raise ValueError(f"unknown family: {family}")
    rng = random.Random(seed)
    states = enumerate_states()
    initial_state = (1, 1, 1, 1, 1, 0)
    base_family = _base_family(family)
    transform_specs = _transform_specs(base_family)
    base_edges = _build_edges(states, transform_specs)
    if family == "random_transform_control":
        edges = _randomized_edges(states, base_edges, rng)
        transform_names = ("random_target_matched",)
    elif family == "degree_preserving_transform_control":
        edges = _degree_preserving_edges(states, base_edges, seed)
        transform_names = ("degree_sequence_scramble",)
    else:
        edges = base_edges
        transform_names = tuple(name for name, _transform in transform_specs)
    extractor_mode = "permissive" if family == "equivalence_permissive_control" else "strict" if family == "equivalence_strict_control" else "block_relation"
    return NeutralSystem(
        system_id=f"{family}_{seed}",
        seed=seed,
        family=family,
        states=states,
        edges=edges,
        initial_state=initial_state,
        transform_names=transform_names,
        extractor_mode=extractor_mode,
        metadata={
            "coordinate_count": len(initial_state),
            "nonphase_coordinate_count": NONPHASE_COORDS,
            "modulus": MODULUS,
            "initial_state": str(initial_state),
        },
    )


def block_relation_mu(state: State) -> tuple[int, bool]:
    return ((state[0] - state[1]) % MODULUS, state[4] in {0, 1})


def block_relation_nu(state: State) -> tuple[int, bool]:
    return ((state[2] - state[3]) % MODULUS, state[4] in {1, 2})


def relation_mu_changed(initial: State, endpoint: State) -> bool:
    return block_relation_mu(initial) != block_relation_mu(endpoint)


def relation_nu_changed(initial: State, endpoint: State) -> bool:
    return block_relation_nu(initial) != block_relation_nu(endpoint)


def block_relation_changed(initial: State, endpoint: State) -> bool:
    return relation_mu_changed(initial, endpoint) or relation_nu_changed(initial, endpoint)


def _base_family(family: str) -> str:
    if family in {
        "random_transform_control",
        "degree_preserving_transform_control",
        "equivalence_permissive_control",
        "equivalence_strict_control",
    }:
        return "independent_block_transforms"
    return family


def _transform_specs(family: str) -> tuple[tuple[str, Transform], ...]:
    if family == "independent_block_transforms":
        return (
            ("shift_block0(+1)", lambda state: {_shift_block(state, (0, 1), 1)}),
            ("shift_block0(-1)", lambda state: {_shift_block(state, (0, 1), -1)}),
            ("shift_block1(+1)", lambda state: {_shift_block(state, (2, 3), 1)}),
            ("shift_block1(-1)", lambda state: {_shift_block(state, (2, 3), -1)}),
            ("shift_coordinate4(+1)", lambda state: {_shift_coord(state, 4, 1)}),
            ("shift_coordinate4(-1)", lambda state: {_shift_coord(state, 4, -1)}),
            ("phase_advance", lambda state: {_phase_advance(state)}),
        )
    if family == "coupled_block_transforms":
        return (
            ("shift_blocks(+1,+1)", lambda state: {_shift_blocks(state, 1, 1)}),
            ("shift_blocks(-1,-1)", lambda state: {_shift_blocks(state, -1, -1)}),
            ("swap_blocks", lambda state: {_swap_blocks(state)}),
            ("coordinate4_to_mid", lambda state: {_set_coord(state, 4, 1)}),
            ("phase_advance", lambda state: {_phase_advance(state)}),
        )
    if family == "anti_correlated_block_transforms":
        return (
            ("block0_constant_block1_delta(+1)", lambda state: {_block0_constant_block1_delta(state, 1, 0)}),
            ("block0_constant_block1_delta(-1)", lambda state: {_block0_constant_block1_delta(state, -1, 0)}),
            ("block1_constant_block0_delta(+1)", lambda state: {_block1_constant_block0_delta(state, 1, 2)}),
            ("block1_constant_block0_delta(-1)", lambda state: {_block1_constant_block0_delta(state, -1, 2)}),
            ("phase_advance", lambda state: {_phase_advance(state)}),
        )
    if family == "shared_constraint_conflict":
        return (
            ("block0_preserve_coordinate4_low", lambda state: {_set_coord(_shift_block(state, (0, 1), 1), 4, 0)}),
            ("block0_preserve_coordinate4_low_alt", lambda state: {_set_coord(_shift_block(state, (0, 1), -1), 4, 0)}),
            ("block1_preserve_coordinate4_high", lambda state: {_set_coord(_shift_block(state, (2, 3), 1), 4, 2)}),
            ("block1_preserve_coordinate4_high_alt", lambda state: {_set_coord(_shift_block(state, (2, 3), -1), 4, 2)}),
        )
    if family == "phase_cycle_control":
        return (("phase_advance", lambda state: {_phase_advance(state)}),)
    if family == "fixed_point_control":
        return (
            ("project_to_origin", lambda _state: {(0, 0, 0, 0, 0, 0)}),
            ("project_to_midpoint", lambda _state: {(1, 1, 1, 1, 1, 1)}),
        )
    raise ValueError(f"unhandled transform family: {family}")


def _build_edges(
    states: Iterable[State], transform_specs: tuple[tuple[str, Transform], ...]
) -> dict[State, tuple[State, ...]]:
    edges: dict[State, tuple[State, ...]] = {}
    for state in states:
        targets: set[State] = set()
        for _name, transform in transform_specs:
            targets.update(transform(state))
        edges[state] = tuple(sorted(targets))
    return edges


def _randomized_edges(
    states: tuple[State, ...], edges: dict[State, tuple[State, ...]], rng: random.Random
) -> dict[State, tuple[State, ...]]:
    state_list = list(states)
    return {
        state: tuple(sorted(rng.sample(state_list, min(len(targets), len(state_list)))))
        if targets
        else tuple()
        for state, targets in edges.items()
    }


def _degree_preserving_edges(
    states: tuple[State, ...], edges: dict[State, tuple[State, ...]], seed: int
) -> dict[State, tuple[State, ...]]:
    state_list = sorted(states, key=lambda state: (_stable_bucket(state, seed), state))
    return {
        state: tuple(
            state_list[(_stable_bucket(state, seed + 17) + index) % len(state_list)]
            for index in range(len(targets))
        )
        for state, targets in edges.items()
    }


def _shift_coord(state: State, coord: int, delta: int) -> State:
    values = list(state)
    values[coord] = (values[coord] + delta) % MODULUS
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _set_coord(state: State, coord: int, value: int) -> State:
    values = list(state)
    values[coord] = value % MODULUS
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _shift_block(state: State, coords: tuple[int, int], delta: int) -> State:
    values = list(state)
    for coord in coords:
        values[coord] = (values[coord] + delta) % MODULUS
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _shift_blocks(state: State, delta0: int, delta1: int) -> State:
    return _shift_block(_shift_block(state, (0, 1), delta0), (2, 3), delta1)


def _swap_blocks(state: State) -> State:
    q0, q1, q2, q3, q4, phase = state
    return (q2, q3, q0, q1, q4, (phase + 1) % MODULUS)


def _block0_constant_block1_delta(state: State, delta: int, coord4: int) -> State:
    values = list(state)
    values[2] = (values[2] + delta) % MODULUS
    values[4] = coord4
    values[5] = (values[5] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _block1_constant_block0_delta(state: State, delta: int, coord4: int) -> State:
    values = list(state)
    values[0] = (values[0] + delta) % MODULUS
    values[4] = coord4
    values[5] = (values[5] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _phase_advance(state: State) -> State:
    values = list(state)
    values[-1] = (values[-1] + 1) % MODULUS
    return tuple(values)  # type: ignore[return-value]


def _stable_bucket(state: State, seed: int) -> int:
    total = seed * 131
    for index, value in enumerate(state):
        total += (index + 5) * (value + 11) * 89
    return total % 997

