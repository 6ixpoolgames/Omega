from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable

State = tuple[int, int, int, int, int, int]


@dataclass(frozen=True)
class Transform:
    name: str
    dc: int = 0
    di: int = 0
    dr: int = 0
    do: int = 0
    commit: int | None = None
    mode_delta: int = 0
    requires_repair: bool = False


@dataclass(frozen=True)
class RFSSystem:
    system_id: str
    seed: int
    regime: str
    control_type: str
    is_control: bool
    states: tuple[State, ...]
    edges: dict[State, tuple[State, ...]]
    transforms: tuple[Transform, ...]
    constraint_params: dict[str, int | float | str]
    transform_params: dict[str, int | float | str]


REGIMES = ("balanced", "permissive", "harsh", "repair_rich", "commit_rich", "capacity_tight")
CONTROLS = ("structured", "dense_permissive_control", "dead_control", "random_edge_control", "shuffled_admissibility_control", "no_perturbation_control")


def enumerate_states(include_mode: bool = True) -> tuple[State, ...]:
    modes = range(3) if include_mode else range(1)
    return tuple((c, i, r, o, k, m) for c in range(5) for i in range(5) for r in range(3) for o in range(5) for k in range(2) for m in modes)


def generate_system(seed: int, regime: str, control_type: str = "structured") -> RFSSystem:
    rng = random.Random(seed)
    states = enumerate_states(include_mode=True)
    params = _regime_params(regime, control_type)
    transforms = _transforms_for(params, rng)
    if control_type == "dense_permissive_control":
        transforms = transforms + (
            Transform("free_expand", do=1),
            Transform("free_repair", di=1, dr=1),
            Transform("free_harvest", dc=1),
            Transform("free_reroute", dr=1, mode_delta=1),
        )
    if control_type == "dead_control":
        transforms = (
            Transform("decay_integrity", di=-2),
            Transform("decay_option", do=-2),
            Transform("capacity_drain", dc=-2),
        )
    edges = _build_edges(states, transforms, params)
    if control_type == "random_edge_control":
        edges = _randomized_edges(states, edges, rng)
    system_id = f"{control_type}_{regime}_{seed}"
    return RFSSystem(
        system_id=system_id,
        seed=seed,
        regime=regime,
        control_type=control_type,
        is_control=control_type != "structured",
        states=states,
        edges=edges,
        transforms=transforms,
        constraint_params={k: v for k, v in params.items() if k.startswith("min_") or k.endswith("_threshold") or k == "regime"},
        transform_params={k: v for k, v in params.items() if not (k.startswith("min_") or k.endswith("_threshold"))},
    )


def perturb(state: State, kind: str) -> State:
    c, i, r, o, k, m = state
    if kind == "capacity_loss":
        return (max(0, c - 2), i, r, o, k, m)
    if kind == "integrity_damage":
        return (c, max(0, i - 2), r, o, k, m)
    if kind == "option_loss":
        return (c, i, r, max(0, o - 2), k, m)
    if kind == "repair_loss":
        return (c, i, max(0, r - 1), o, k, m)
    if kind == "commit_flip":
        return (c, i, r, o, 1, m)
    raise ValueError(f"unknown perturbation kind: {kind}")


def _regime_params(regime: str, control_type: str) -> dict[str, int | float | str]:
    base: dict[str, int | float | str] = {
        "regime": regime,
        "min_reach_h4": 5,
        "min_capacity_strict": 1,
        "min_integrity_strict": 2,
        "min_repair_strict": 1,
        "min_option_strict": 1,
        "consume_bias": 1,
        "repair_bonus": 0,
        "decay_load": 1,
        "commit_load": 1,
    }
    if regime == "permissive":
        base.update(min_reach_h4=8, decay_load=0, consume_bias=0, min_capacity_strict=1, min_integrity_strict=1)
    elif regime == "harsh":
        base.update(min_reach_h4=3, decay_load=2, consume_bias=2, min_capacity_strict=2, min_integrity_strict=3)
    elif regime == "repair_rich":
        base.update(repair_bonus=2, min_repair_strict=1)
    elif regime == "commit_rich":
        base.update(commit_load=3)
    elif regime == "capacity_tight":
        base.update(consume_bias=2, min_capacity_strict=2)
    if control_type == "dense_permissive_control":
        base.update(min_reach_h4=12, min_capacity_strict=0, min_integrity_strict=1, min_repair_strict=0, min_option_strict=0, decay_load=0, consume_bias=0)
    elif control_type == "dead_control":
        base.update(min_reach_h4=2, min_capacity_strict=2, min_integrity_strict=3, min_repair_strict=1, min_option_strict=2, decay_load=3)
    elif control_type == "no_perturbation_control":
        base.update(min_repair_strict=0)
    return base


def _transforms_for(params: dict[str, int | float | str], rng: random.Random) -> tuple[Transform, ...]:
    consume = int(params["consume_bias"])
    repair_bonus = int(params["repair_bonus"])
    decay = int(params["decay_load"])
    commit_load = int(params["commit_load"])
    transforms = [
        Transform("expand", dc=-1 - max(0, consume - 1), do=1),
        Transform("maintain", dc=-1, di=1),
        Transform("repair", dc=-1, di=1, dr=1 + min(1, repair_bonus)),
        Transform("harvest", dc=1, di=-1 if decay else 0, do=-1),
        Transform("reroute", dc=-1, do=1, mode_delta=1, requires_repair=True),
        Transform("decay_integrity", di=-decay),
        Transform("decay_option", do=-decay),
    ]
    for index in range(commit_load):
        transforms.append(Transform(f"commit_{index}", dc=1, do=1, commit=1, di=-1 if rng.random() < 0.5 else 0))
    return tuple(transforms)


def _build_edges(states: Iterable[State], transforms: tuple[Transform, ...], params: dict[str, int | float | str]) -> dict[State, tuple[State, ...]]:
    edges: dict[State, tuple[State, ...]] = {}
    for state in states:
        next_states = {_apply_transform(state, transform) for transform in transforms if _valid_transform(state, transform)}
        edges[state] = tuple(sorted(next_states))
    return edges


def _valid_transform(state: State, transform: Transform) -> bool:
    c, _i, r, _o, _k, _m = state
    if transform.requires_repair and r <= 0:
        return False
    if c + transform.dc < 0:
        return False
    return True


def _apply_transform(state: State, transform: Transform) -> State:
    c, i, r, o, k, m = state
    return (
        _clamp(c + transform.dc, 0, 4),
        _clamp(i + transform.di, 0, 4),
        _clamp(r + transform.dr, 0, 2),
        _clamp(o + transform.do, 0, 4),
        k if transform.commit is None else transform.commit,
        (m + transform.mode_delta) % 3,
    )


def _randomized_edges(states: tuple[State, ...], edges: dict[State, tuple[State, ...]], rng: random.Random) -> dict[State, tuple[State, ...]]:
    state_list = list(states)
    out: dict[State, tuple[State, ...]] = {}
    for state, targets in edges.items():
        count = len(targets)
        out[state] = tuple(sorted(rng.sample(state_list, min(count, len(state_list))))) if count else tuple()
    return out


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))
