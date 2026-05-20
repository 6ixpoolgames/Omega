from __future__ import annotations

import random
from statistics import mean

from .algebra import AlgebraState, TaskAlgebra, apply_task, valid_tasks
from .policies import evaluate_decision
from .reachability import candidate_paths, r0


GEOMETRY_DEPTHS = (1, 2, 4, 8, 16)
CORRIDOR_DEPTHS = (8, 16)


def selected_policy_states(
    algebra: TaskAlgebra,
    state: AlgebraState,
    h: int,
    H: int,
    seed: int,
    sample_size: int,
    max_paths: int,
) -> tuple[dict[str, object], dict[str, AlgebraState | None]]:
    decision = evaluate_decision(
        algebra,
        state,
        h=h,
        H=H,
        seed=seed,
        sample_size=sample_size,
        max_paths=max_paths,
    )
    decision.pop("_paths", None)
    states: dict[str, AlgebraState | None] = {
        "R1": _apply_selected_task(algebra, state, int(decision["R1_chosen_task"])),
        "R0lookahead": _apply_selected_task(algebra, state, int(decision["R0_lookahead_chosen_task"])),
    }
    return decision, states


def geometry_sidecar(
    algebra: TaskAlgebra,
    state: AlgebraState,
    h: int,
    H: int,
    seed: int,
    sample_size: int,
    max_paths: int,
    geometry_samples: int,
    reentry_samples: int,
    theta_depth: float = 0.25,
    theta_corridor: float = 0.50,
) -> dict[str, object]:
    decision, states = selected_policy_states(
        algebra,
        state,
        h=h,
        H=H,
        seed=seed,
        sample_size=sample_size,
        max_paths=max_paths,
    )
    row: dict[str, object] = {
        "geometry_samples": geometry_samples,
        "reentry_samples": reentry_samples,
        "theta_depth": theta_depth,
        "theta_corridor": theta_corridor,
        "R1_R0lookahead_same_choice": decision["R1_R0lookahead_same_choice"],
        "R1_score": decision["R1_score"],
        "R0lookahead_score": decision["R0_lookahead_score"],
        "candidate_future_R0_variance": decision["candidate_future_R0_variance"],
    }
    diagnostics: dict[str, dict[str, float | int]] = {}
    for label, selected_state in states.items():
        diagnostics[label] = (
            score_state_geometry(
                algebra,
                selected_state,
                H=H,
                seed=seed * 1009 + (17 if label == "R1" else 31),
                max_paths=max_paths,
                geometry_samples=geometry_samples,
                reentry_samples=reentry_samples,
                theta_depth=theta_depth,
                theta_corridor=theta_corridor,
            )
            if selected_state is not None
            else _empty_geometry()
        )
        for key, value in diagnostics[label].items():
            row[f"{label}_{key}"] = value

    row["geometry_gap_terminal_depth"] = diagnostics["R1"]["terminal_depth"] - diagnostics["R0lookahead"]["terminal_depth"]
    row["geometry_gap_depth_profile_d16"] = diagnostics["R1"]["depth_profile_d16"] - diagnostics["R0lookahead"]["depth_profile_d16"]
    row["geometry_gap_corridor_width_d8"] = diagnostics["R1"]["corridor_width_d8"] - diagnostics["R0lookahead"]["corridor_width_d8"]
    row["geometry_gap_corridor_width_d16"] = diagnostics["R1"]["corridor_width_d16"] - diagnostics["R0lookahead"]["corridor_width_d16"]
    row["geometry_gap_reentry_score"] = diagnostics["R1"]["reentry_score"] - diagnostics["R0lookahead"]["reentry_score"]
    return row


def score_state_geometry(
    algebra: TaskAlgebra,
    state: AlgebraState,
    H: int,
    seed: int,
    max_paths: int,
    geometry_samples: int,
    reentry_samples: int,
    theta_depth: float,
    theta_corridor: float,
) -> dict[str, float | int]:
    profile = {
        depth: r0(algebra, state, depth, max_paths=max_paths, rng=random.Random(seed + depth)).count
        for depth in GEOMETRY_DEPTHS
    }
    d1_base = max(1, profile[1])
    terminal_depth = max((depth for depth, count in profile.items() if count >= theta_depth * d1_base), default=0)
    base_future = r0(algebra, state, H, max_paths=max_paths, rng=random.Random(seed + 101)).reachable_tasks
    base_count = len(base_future)
    corridor = {
        depth: _corridor_width(
            algebra,
            state,
            depth=depth,
            H=H,
            base_r0=max(1, base_count),
            threshold=theta_corridor,
            seed=seed + 10_000 + depth,
            max_paths=max_paths,
            geometry_samples=geometry_samples,
        )
        for depth in CORRIDOR_DEPTHS
    }
    reentry = _reentry_score(
        algebra,
        state,
        H=H,
        base_reachable=base_future,
        seed=seed + 20_000,
        max_paths=max_paths,
        reentry_samples=reentry_samples,
    )
    return {
        "depth_profile_d1": profile[1],
        "depth_profile_d2": profile[2],
        "depth_profile_d4": profile[4],
        "depth_profile_d8": profile[8],
        "depth_profile_d16": profile[16],
        "terminal_depth": terminal_depth,
        "corridor_width_d8": corridor[8],
        "corridor_width_d16": corridor[16],
        "reentry_score": reentry,
    }


def _corridor_width(
    algebra: TaskAlgebra,
    state: AlgebraState,
    depth: int,
    H: int,
    base_r0: int,
    threshold: float,
    seed: int,
    max_paths: int,
    geometry_samples: int,
) -> int:
    rng = random.Random(seed)
    paths = list(candidate_paths(algebra, state, depth, max_paths=max_paths, rng=random.Random(seed)))
    exact_depth_paths = [path for path in paths if len(path) == depth]
    if len(exact_depth_paths) > geometry_samples:
        exact_depth_paths = rng.sample(exact_depth_paths, geometry_samples)
    viable = 0
    for path in exact_depth_paths:
        next_state = state
        for task_id in path:
            if task_id not in valid_tasks(algebra, next_state):
                next_state = None
                break
            next_state = apply_task(algebra, next_state, task_id)
        if next_state is None:
            continue
        future = r0(algebra, next_state, H, max_paths=max_paths).count
        if future >= threshold * base_r0:
            viable += 1
    return viable


def _reentry_score(
    algebra: TaskAlgebra,
    state: AlgebraState,
    H: int,
    base_reachable: frozenset[int],
    seed: int,
    max_paths: int,
    reentry_samples: int,
) -> float:
    if not base_reachable:
        return 0.0
    rng = random.Random(seed)
    retentions: list[float] = []
    enabled = list(state.enabled - state.completed - state.obstructed)
    reachable = list(base_reachable)
    for _ in range(reentry_samples):
        if enabled:
            dropped = rng.choice(enabled)
            stressed = AlgebraState(
                enabled=frozenset(task for task in state.enabled if task != dropped),
                obstructed=state.obstructed,
                completed=state.completed,
                time=state.time,
            )
            retentions.append(_overlap_fraction(algebra, stressed, H, base_reachable, max_paths))
        if reachable:
            obstructed = rng.choice(reachable)
            stressed = AlgebraState(
                enabled=state.enabled,
                obstructed=frozenset(set(state.obstructed) | {obstructed}),
                completed=state.completed,
                time=state.time,
            )
            retentions.append(_overlap_fraction(algebra, stressed, H, base_reachable, max_paths))
    return mean(retentions) if retentions else 0.0


def _overlap_fraction(
    algebra: TaskAlgebra,
    state: AlgebraState,
    H: int,
    base_reachable: frozenset[int],
    max_paths: int,
) -> float:
    stressed_reachable = r0(algebra, state, H, max_paths=max_paths).reachable_tasks
    return len(base_reachable & stressed_reachable) / max(1, len(base_reachable))


def _apply_selected_task(algebra: TaskAlgebra, state: AlgebraState, task_id: int) -> AlgebraState | None:
    if task_id < 0 or task_id not in valid_tasks(algebra, state):
        return None
    return apply_task(algebra, state, task_id)


def _empty_geometry() -> dict[str, float | int]:
    return {
        "depth_profile_d1": 0,
        "depth_profile_d2": 0,
        "depth_profile_d4": 0,
        "depth_profile_d8": 0,
        "depth_profile_d16": 0,
        "terminal_depth": 0,
        "corridor_width_d8": 0,
        "corridor_width_d16": 0,
        "reentry_score": 0.0,
    }
