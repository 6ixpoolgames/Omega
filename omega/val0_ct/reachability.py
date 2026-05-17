from __future__ import annotations

import random
from dataclasses import dataclass

from .algebra import AlgebraState, TaskAlgebra, apply_path, apply_task, valid_tasks


@dataclass(frozen=True)
class R0Result:
    reachable_tasks: frozenset[int]
    candidate_paths: tuple[tuple[int, ...], ...]
    truncated: bool

    @property
    def count(self) -> int:
        return len(self.reachable_tasks)


@dataclass(frozen=True)
class R1Result:
    candidate_count: int
    coverage_fraction: float
    r1_count: int
    r1_fraction: float
    mean_future_r0: float
    topk_future_r0: float
    best_future_r0: int
    threshold_025_fraction: float
    threshold_050_fraction: float
    threshold_075_fraction: float
    future_r0_values: tuple[int, ...]


def candidate_paths(
    algebra: TaskAlgebra,
    state: AlgebraState,
    horizon: int,
    max_paths: int = 4096,
    rng: random.Random | None = None,
) -> tuple[tuple[int, ...], ...]:
    paths: list[tuple[int, ...]] = []
    stack: list[tuple[AlgebraState, tuple[int, ...]]] = [(state, ())]
    truncated = False
    while stack:
        current_state, prefix = stack.pop()
        if 0 < len(prefix) <= horizon:
            paths.append(prefix)
            if len(paths) >= max_paths:
                truncated = True
                break
        if len(prefix) >= horizon:
            continue
        available = list(valid_tasks(algebra, current_state))
        if rng is not None:
            rng.shuffle(available)
        for task_id in reversed(available):
            try:
                next_state = apply_task(algebra, current_state, task_id)
            except ValueError:
                continue
            stack.append((next_state, prefix + (task_id,)))
    setattr(candidate_paths, "last_truncated", truncated)
    return tuple(paths)


def r0(
    algebra: TaskAlgebra,
    state: AlgebraState,
    horizon: int,
    max_paths: int = 4096,
    rng: random.Random | None = None,
) -> R0Result:
    paths = candidate_paths(algebra, state, horizon, max_paths=max_paths, rng=rng)
    reachable = {task_id for path in paths for task_id in path}
    return R0Result(
        reachable_tasks=frozenset(reachable),
        candidate_paths=paths,
        truncated=bool(getattr(candidate_paths, "last_truncated", False)),
    )


def r1(
    algebra: TaskAlgebra,
    state: AlgebraState,
    h: int,
    H: int,
    sample_size: int,
    seed: int,
    max_paths: int = 4096,
) -> R1Result:
    rng = random.Random(seed)
    all_paths = list(candidate_paths(algebra, state, h, max_paths=max_paths, rng=random.Random(seed)))
    if not all_paths:
        return R1Result(0, 1.0, 0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, ())
    if len(all_paths) > sample_size:
        sample = rng.sample(all_paths, sample_size)
    else:
        sample = all_paths
    initial_r0 = r0(algebra, state, H, max_paths=max_paths).count
    thresholds = {
        0.25: max(1.0, 0.25 * initial_r0),
        0.50: max(1.0, 0.50 * initial_r0),
        0.75: max(1.0, 0.75 * initial_r0),
    }
    future_values: list[int] = []
    for path in sample:
        future_state = apply_path(algebra, state, path)
        future_values.append(r0(algebra, future_state, H, max_paths=max_paths).count)
    values = sorted(future_values, reverse=True)
    topk = values[: max(1, min(10, len(values)))]
    primary_count = sum(value >= thresholds[0.50] for value in future_values)
    return R1Result(
        candidate_count=len(all_paths),
        coverage_fraction=len(sample) / max(1, len(all_paths)),
        r1_count=primary_count,
        r1_fraction=primary_count / max(1, len(sample)),
        mean_future_r0=sum(future_values) / max(1, len(future_values)),
        topk_future_r0=sum(topk) / max(1, len(topk)),
        best_future_r0=max(future_values) if future_values else 0,
        threshold_025_fraction=sum(value >= thresholds[0.25] for value in future_values) / max(1, len(sample)),
        threshold_050_fraction=primary_count / max(1, len(sample)),
        threshold_075_fraction=sum(value >= thresholds[0.75] for value in future_values) / max(1, len(sample)),
        future_r0_values=tuple(future_values),
    )

