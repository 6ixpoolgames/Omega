from __future__ import annotations

import random
from collections import defaultdict

from .algebra import AlgebraState, TaskAlgebra, apply_path, family_counts, valid_tasks
from .reachability import candidate_paths, r0


POLICIES = ("random", "R0", "R0_lookahead", "R1", "pseudo_omega")


def choose_task(
    algebra: TaskAlgebra,
    state: AlgebraState,
    policy: str,
    h: int,
    H: int,
    seed: int,
    sample_size: int,
    max_paths: int,
) -> tuple[int | None, dict[str, float | int | str]]:
    rng = random.Random(seed)
    available = valid_tasks(algebra, state)
    if not available:
        return None, {"score": 0.0, "reason": "no_available_tasks"}
    paths = list(candidate_paths(algebra, state, h, max_paths=max_paths, rng=random.Random(seed)))
    if len(paths) > sample_size:
        paths = rng.sample(paths, sample_size)
    if policy == "random":
        task_id = rng.choice(available)
        return task_id, {"score": 0.0, "reason": "random"}
    if policy == "R0":
        return _choose_best_path(algebra, state, paths, h, "near_r0", max_paths)
    if policy == "R0_lookahead":
        return _choose_best_path(algebra, state, paths, H, "future_r0", max_paths)
    if policy == "R1":
        return _choose_r1(algebra, state, paths, H, max_paths)
    if policy == "pseudo_omega":
        return _choose_pseudo_omega(algebra, state, available, H, max_paths)
    raise ValueError(f"unknown policy: {policy}")


def _choose_best_path(
    algebra: TaskAlgebra,
    state: AlgebraState,
    paths: list[tuple[int, ...]],
    horizon: int,
    label: str,
    max_paths: int,
) -> tuple[int | None, dict[str, float | int | str]]:
    best_task = None
    best_score = -1
    for path in paths:
        next_state = apply_path(algebra, state, path)
        score = r0(algebra, next_state, horizon, max_paths=max_paths).count
        if score > best_score:
            best_score = score
            best_task = path[0]
    return best_task, {"score": float(best_score), "reason": label}


def _choose_r1(
    algebra: TaskAlgebra,
    state: AlgebraState,
    paths: list[tuple[int, ...]],
    H: int,
    max_paths: int,
) -> tuple[int | None, dict[str, float | int | str]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    initial_r0 = r0(algebra, state, H, max_paths=max_paths).count
    threshold = max(1.0, 0.50 * initial_r0)
    for path in paths:
        next_state = apply_path(algebra, state, path)
        grouped[path[0]].append(r0(algebra, next_state, H, max_paths=max_paths).count)
    best_task = None
    best_score = (-1.0, -1.0)
    for task_id, values in grouped.items():
        mean_future = sum(values) / max(1, len(values))
        positive_fraction = sum(value >= threshold for value in values) / max(1, len(values))
        score = (mean_future, positive_fraction)
        if score > best_score:
            best_score = score
            best_task = task_id
    return best_task, {"score": best_score[0], "r1_fraction": best_score[1], "reason": "r1_mean_future_r0"}


def _choose_pseudo_omega(
    algebra: TaskAlgebra,
    state: AlgebraState,
    available: tuple[int, ...],
    H: int,
    max_paths: int,
) -> tuple[int | None, dict[str, float | int | str]]:
    best_task = None
    best_score = -10_000.0
    for task_id in available:
        task = algebra.task(task_id)
        next_state = apply_path(algebra, state, (task_id,))
        counts = family_counts(algebra, next_state.enabled)
        lock_score = counts.get("lock_in", 0)
        global_score = r0(algebra, next_state, H, max_paths=max_paths).count
        obstruction_score = len(task.obstructs)
        family_bonus = 10 if task.family == "lock_in" else 0
        score = family_bonus + lock_score + obstruction_score - 0.25 * global_score
        if score > best_score:
            best_score = score
            best_task = task_id
    return best_task, {"score": best_score, "reason": "local_lock_in_global_degradation"}
