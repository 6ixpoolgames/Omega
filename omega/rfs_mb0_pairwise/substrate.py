from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

Status = int
State = tuple[Status, Status, int, int, int, int]

ALIVE = 0
STRAINED = 1
DAMAGED = 2
LOST = 3
CAPTURED = 4

CONTINUOUS = frozenset({ALIVE, STRAINED, DAMAGED})
DISCONTINUOUS = frozenset({LOST, CAPTURED})

REGIMES = (
    "mutual_support",
    "independent_parallel",
    "pairwise_incompatible",
    "capture_A_over_B",
    "capture_B_over_A",
    "terminal_lockin",
    "random_branching_control",
    "clock_control",
    "stasis_control",
)
CONTROLS = (
    "structured",
    "random_edge_control",
    "degree_preserving_control",
    "identity_shuffle_control",
    "no_interaction_control",
    "dead_control",
    "permissive_control",
)


@dataclass(frozen=True)
class MB0System:
    system_id: str
    seed: int
    regime: str
    control_type: str
    is_control: bool
    states: tuple[State, ...]
    edges: dict[State, tuple[State, ...]]
    initial_state: State
    generator_params: dict[str, int | float | str]


def enumerate_states() -> tuple[State, ...]:
    return tuple(
        (a, b, shared, hazard, repair, phase)
        for a in range(5)
        for b in range(5)
        for shared in range(3)
        for hazard in range(3)
        for repair in range(2)
        for phase in range(3)
    )


def generate_system(seed: int, regime: str, control_type: str = "structured") -> MB0System:
    if regime not in REGIMES:
        raise ValueError(f"unknown regime: {regime}")
    if control_type not in CONTROLS:
        raise ValueError(f"unknown control_type: {control_type}")
    rng = random.Random(seed)
    states = enumerate_states()
    base_edges = _build_edges(states, regime, control_type)
    edges = _apply_control(states, base_edges, seed, regime, control_type, rng)
    initial_state = (ALIVE, ALIVE, 1, 1, 1, 0)
    system_id = f"{control_type}_{regime}_{seed}"
    return MB0System(
        system_id=system_id,
        seed=seed,
        regime=regime,
        control_type=control_type,
        is_control=control_type != "structured" or regime.endswith("_control"),
        states=states,
        edges=edges,
        initial_state=initial_state,
        generator_params={
            "status_encoding": "0 alive, 1 strained, 2 damaged, 3 lost, 4 captured",
            "continuity": "token status in {alive,strained,damaged}",
            "shared_levels": 3,
            "hazard_levels": 3,
            "repair_levels": 2,
            "phase_levels": 3,
        },
    )


def a_continuous(state: State) -> bool:
    return state[0] in CONTINUOUS


def b_continuous(state: State) -> bool:
    return state[1] in CONTINUOUS


def shuffled_a_continuous(state: State, seed: int) -> bool:
    return _stable_bucket(state, seed, salt=11) < 3


def shuffled_b_continuous(state: State, seed: int) -> bool:
    return _stable_bucket(state, seed, salt=29) < 3


def _build_edges(
    states: Iterable[State], regime: str, control_type: str
) -> dict[State, tuple[State, ...]]:
    if control_type == "dead_control":
        return {state: (_advance(state, _worse(state[0]), _worse(state[1]), -1, 1, -1),) for state in states}
    if control_type == "permissive_control":
        return _permissive_edges(states)
    if regime == "stasis_control":
        return {state: (state,) for state in states}
    if regime == "clock_control":
        return {state: (_advance(state, state[0], state[1], 0, 0, 0),) for state in states}

    out: dict[State, tuple[State, ...]] = {}
    for state in states:
        candidates: set[State] = set()
        candidates.add(_advance(state, state[0], state[1], 0, 0, 0))
        if regime == "mutual_support":
            candidates.update(_mutual_support_next(state))
        elif regime == "independent_parallel":
            candidates.update(_independent_next(state))
        elif regime == "pairwise_incompatible":
            candidates.update(_pairwise_incompatible_next(state))
        elif regime == "capture_A_over_B":
            candidates.update(_capture_next(state, captor="A"))
        elif regime == "capture_B_over_A":
            candidates.update(_capture_next(state, captor="B"))
        elif regime == "terminal_lockin":
            candidates.update(_terminal_lockin_next(state))
        elif regime == "random_branching_control":
            candidates.update(_randomish_branch_next(state))
        else:
            raise ValueError(f"unhandled regime: {regime}")
        out[state] = tuple(sorted(candidates))
    if control_type == "no_interaction_control":
        return _remove_interaction(states)
    return out


def _mutual_support_next(state: State) -> set[State]:
    a, b, shared, hazard, repair, _phase = state
    out = {
        _advance(state, _better(a), b, -1, -1, 0),
        _advance(state, a, _better(b), -1, -1, 0),
        _advance(state, _better(a), _better(b), 1, -1, 0),
    }
    if repair:
        out.add(_advance(state, _better(a), _better(b), 0, -1, 0))
    if shared == 0:
        out.add(_advance(state, _worse(a), _worse(b), 0, 1, 0))
    return out


def _independent_next(state: State) -> set[State]:
    a, b, _shared, _hazard, repair, _phase = state
    out = {
        _advance(state, _better(a), b, -1, 0, 0),
        _advance(state, a, _better(b), -1, 0, 0),
        _advance(state, _worse(a), b, 1, 0, 0),
        _advance(state, a, _worse(b), 1, 0, 0),
    }
    if repair:
        out.add(_advance(state, _better(a), _better(b), 0, 0, 0))
    return out


def _pairwise_incompatible_next(state: State) -> set[State]:
    a, b, shared, hazard, _repair, _phase = state
    out = {
        _advance(state, _better(a), _worse(b), -1, 0, 0),
        _advance(state, _worse(a), _better(b), -1, 0, 0),
    }
    if shared <= 1 or hazard >= 1:
        out.update(
            {
                _advance(state, _better(a), LOST, -1, 1, -1),
                _advance(state, LOST, _better(b), -1, 1, -1),
            }
        )
    return out


def _capture_next(state: State, captor: str) -> set[State]:
    a, b, _shared, hazard, repair, _phase = state
    if captor == "A":
        out = {
            _advance(state, _better(a), _worse(b), 0, 0, 0),
            _advance(state, _better(a), CAPTURED, -1, 1, -1),
            _advance(state, _better(a), LOST if hazard == 2 else _worse(b), 0, 1, 0),
        }
        if repair:
            out.add(_advance(state, _better(a), b, 0, 0, -1))
        return out
    out = {
        _advance(state, _worse(a), _better(b), 0, 0, 0),
        _advance(state, CAPTURED, _better(b), -1, 1, -1),
        _advance(state, LOST if hazard == 2 else _worse(a), _better(b), 0, 1, 0),
    }
    if repair:
        out.add(_advance(state, a, _better(b), 0, 0, -1))
    return out


def _terminal_lockin_next(state: State) -> set[State]:
    a, b, _shared, _hazard, _repair, _phase = state
    return {
        _advance(state, a, b, -1, -1, -1),
        _advance(state, ALIVE if a in CONTINUOUS else a, ALIVE if b in CONTINUOUS else b, -1, -1, -1),
    }


def _randomish_branch_next(state: State) -> set[State]:
    a, b, shared, hazard, repair, phase = state
    return {
        _advance(state, (a + phase + 1) % 5, b, 1, 0, 0),
        _advance(state, a, (b + shared + 1) % 5, 0, 1, 0),
        _advance(state, (a + hazard + 2) % 5, (b + repair + 2) % 5, -1, -1, 0),
    }


def _remove_interaction(states: Iterable[State]) -> dict[State, tuple[State, ...]]:
    out: dict[State, tuple[State, ...]] = {}
    for state in states:
        a, b, _shared, _hazard, _repair, _phase = state
        out[state] = tuple(
            sorted(
                {
                    _advance(state, _better(a), b, 0, 0, 0),
                    _advance(state, _worse(a), b, 0, 0, 0),
                    _advance(state, a, _better(b), 0, 0, 0),
                    _advance(state, a, _worse(b), 0, 0, 0),
                }
            )
        )
    return out


def _permissive_edges(states: Iterable[State]) -> dict[State, tuple[State, ...]]:
    out: dict[State, tuple[State, ...]] = {}
    for state in states:
        out[state] = tuple(
            sorted(
                {
                    _advance(state, a, b, ds, dh, dr)
                    for a in CONTINUOUS
                    for b in CONTINUOUS
                    for ds in (-1, 0, 1)
                    for dh in (-1, 0, 1)
                    for dr in (-1, 0, 1)
                }
            )
        )
    return out


def _apply_control(
    states: tuple[State, ...],
    edges: dict[State, tuple[State, ...]],
    seed: int,
    regime: str,
    control_type: str,
    rng: random.Random,
) -> dict[State, tuple[State, ...]]:
    if control_type == "random_edge_control":
        state_list = list(states)
        return {
            state: tuple(sorted(rng.sample(state_list, min(len(targets), len(state_list)))))
            if targets
            else tuple()
            for state, targets in edges.items()
        }
    if control_type == "degree_preserving_control":
        state_list = sorted(states, key=lambda s: (_stable_bucket(s, seed, salt=len(regime)), s))
        return {
            state: tuple(state_list[(_stable_bucket(state, seed, salt=7) + i) % len(state_list)] for i in range(len(targets)))
            for state, targets in edges.items()
        }
    return edges


def _advance(state: State, a: int, b: int, shared_delta: int, hazard_delta: int, repair_delta: int) -> State:
    _old_a, _old_b, shared, hazard, repair, phase = state
    return (
        _clamp(a, 0, 4),
        _clamp(b, 0, 4),
        _clamp(shared + shared_delta, 0, 2),
        _clamp(hazard + hazard_delta, 0, 2),
        _clamp(repair + repair_delta, 0, 1),
        (phase + 1) % 3,
    )


def _better(status: int) -> int:
    if status in DISCONTINUOUS:
        return status
    return max(ALIVE, status - 1)


def _worse(status: int) -> int:
    if status in DISCONTINUOUS:
        return status
    return min(DAMAGED, status + 1)


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def _stable_bucket(state: State, seed: int, salt: int) -> int:
    total = seed + salt * 101
    for index, value in enumerate(state):
        total += (index + 3) * (value + 7) * 97
    return total % 5

