from __future__ import annotations

import random
from collections import defaultdict
from statistics import mean, pvariance

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
    decision = evaluate_decision(algebra, state, h, H, seed, sample_size, max_paths)
    paths = decision.pop("_paths")
    if policy == "random":
        task_id = rng.choice(available)
        return task_id, {**decision, "score": 0.0, "reason": "random"}
    if policy == "R0":
        task_id, info = _choose_best_path(algebra, state, paths, h, "near_r0", max_paths)
        return task_id, {**decision, **info}
    if policy == "R0_lookahead":
        return int(decision["R0_lookahead_chosen_task"]), {**decision, "score": decision["R0_lookahead_score"], "reason": "future_r0"}
    if policy == "R1":
        return int(decision["R1_chosen_task"]), {**decision, "score": decision["R1_score"], "r1_fraction": decision["R1_fraction"], "reason": "r1_mean_future_r0"}
    if policy == "pseudo_omega":
        task_id, info = _choose_pseudo_omega(algebra, state, available, H, max_paths)
        return task_id, {**decision, **info}
    raise ValueError(f"unknown policy: {policy}")


def evaluate_decision(
    algebra: TaskAlgebra,
    state: AlgebraState,
    h: int,
    H: int,
    seed: int,
    sample_size: int,
    max_paths: int,
) -> dict[str, object]:
    rng = random.Random(seed)
    paths = list(candidate_paths(algebra, state, h, max_paths=max_paths, rng=random.Random(seed)))
    if len(paths) > sample_size:
        paths = rng.sample(paths, sample_size)
    if not paths:
        return {
            "_paths": [],
            "R1_chosen_task": -1,
            "R0_lookahead_chosen_task": -1,
            "R1_R0lookahead_same_choice": 1,
            "R1_R0lookahead_score_gap": 0.0,
            "R1_score": 0.0,
            "R0_lookahead_score": 0.0,
            "R1_fraction": 0.0,
            "candidate_future_R0_max": 0,
            "candidate_future_R0_mean": 0.0,
            "candidate_future_R0_variance": 0.0,
            "candidate_future_R0_range": 0,
            "candidate_R1_fraction": 0.0,
            "candidate_obstruction_mean": 0.0,
            "candidate_obstruction_variance": 0.0,
            "R1_chosen_obstruction_count": 0,
            "R0_lookahead_chosen_obstruction_count": 0,
        }
    initial_r0 = r0(algebra, state, H, max_paths=max_paths).count
    threshold = max(1.0, 0.50 * initial_r0)
    future_by_path: list[tuple[tuple[int, ...], int, int]] = []
    grouped: dict[int, list[int]] = defaultdict(list)
    obstruction_by_first: dict[int, list[int]] = defaultdict(list)
    for path in paths:
        next_state = apply_path(algebra, state, path)
        future = r0(algebra, next_state, H, max_paths=max_paths).count
        obstruction = sum(len(algebra.task(task_id).obstructs) for task_id in path)
        future_by_path.append((path, future, obstruction))
        grouped[path[0]].append(future)
        obstruction_by_first[path[0]].append(obstruction)
    values = [future for _, future, _ in future_by_path]
    obstructions = [obstruction for _, _, obstruction in future_by_path]
    r0_path, r0_score, r0_obstruction = max(future_by_path, key=lambda item: (item[1], -item[2], -item[0][0]))
    best_task = -1
    best_score = (-1.0, -1.0)
    for task_id, group_values in grouped.items():
        mean_future = sum(group_values) / max(1, len(group_values))
        positive_fraction = sum(value >= threshold for value in group_values) / max(1, len(group_values))
        score = (mean_future, positive_fraction)
        if score > best_score:
            best_score = score
            best_task = task_id
    return {
        "_paths": paths,
        "R1_chosen_task": best_task,
        "R0_lookahead_chosen_task": r0_path[0],
        "R1_R0lookahead_same_choice": int(best_task == r0_path[0]),
        "R1_R0lookahead_score_gap": float(best_score[0] - r0_score),
        "R1_score": float(best_score[0]),
        "R0_lookahead_score": float(r0_score),
        "R1_fraction": float(best_score[1]),
        "candidate_future_R0_max": max(values),
        "candidate_future_R0_mean": mean(values),
        "candidate_future_R0_variance": pvariance(values) if len(values) > 1 else 0.0,
        "candidate_future_R0_range": max(values) - min(values),
        "candidate_R1_fraction": sum(value >= threshold for value in values) / max(1, len(values)),
        "candidate_obstruction_mean": mean(obstructions),
        "candidate_obstruction_variance": pvariance(obstructions) if len(obstructions) > 1 else 0.0,
        "R1_chosen_obstruction_count": mean(obstruction_by_first[best_task]) if best_task in obstruction_by_first else 0.0,
        "R0_lookahead_chosen_obstruction_count": r0_obstruction,
    }


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
