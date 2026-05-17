from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Task:
    id: int
    family: str
    cost: float = 1.0
    reliability: float = 1.0
    enabled_by_default: bool = False
    constructor_mask: tuple[int, ...] = ()
    enables: frozenset[int] = frozenset()
    obstructs: frozenset[int] = frozenset()


@dataclass(frozen=True)
class Constructor:
    id: int
    initial_tasks: frozenset[int]
    capacity: float = 1.0


@dataclass(frozen=True)
class AlgebraState:
    enabled: frozenset[int]
    obstructed: frozenset[int]
    completed: frozenset[int]
    time: int = 0


@dataclass(frozen=True)
class TaskAlgebra:
    family: str
    seed: int
    tasks: tuple[Task, ...]
    constructors: tuple[Constructor, ...]
    initial_state: AlgebraState

    @property
    def num_tasks(self) -> int:
        return len(self.tasks)

    def task(self, task_id: int) -> Task:
        return self.tasks[task_id]


def valid_tasks(algebra: TaskAlgebra, state: AlgebraState) -> tuple[int, ...]:
    return tuple(sorted(state.enabled - state.obstructed - state.completed))


def apply_task(algebra: TaskAlgebra, state: AlgebraState, task_id: int) -> AlgebraState:
    if task_id not in valid_tasks(algebra, state):
        raise ValueError(f"task {task_id} is not available")
    task = algebra.task(task_id)
    completed = state.completed | {task_id}
    obstructed = state.obstructed | task.obstructs
    enabled = (state.enabled | task.enables) - obstructed - completed
    return AlgebraState(
        enabled=frozenset(enabled),
        obstructed=frozenset(obstructed),
        completed=frozenset(completed),
        time=state.time + 1,
    )


def apply_path(algebra: TaskAlgebra, state: AlgebraState, path: Iterable[int]) -> AlgebraState:
    next_state = state
    for task_id in path:
        if task_id not in valid_tasks(algebra, next_state):
            break
        next_state = apply_task(algebra, next_state, task_id)
    return next_state


def family_counts(algebra: TaskAlgebra, task_ids: Iterable[int]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task_id in task_ids:
        family = algebra.task(task_id).family
        counts[family] = counts.get(family, 0) + 1
    return counts


def algebra_diagnostics(algebra: TaskAlgebra) -> dict[str, float | int | bool]:
    initial_enabled = len(algebra.initial_state.enabled)
    enable_edges = sum(len(task.enables) for task in algebra.tasks)
    obstruct_edges = sum(len(task.obstructs) for task in algebra.tasks)
    edge_total = max(1, enable_edges + obstruct_edges)
    return {
        "num_tasks": algebra.num_tasks,
        "num_constructors": len(algebra.constructors),
        "initial_enabled_count": initial_enabled,
        "initial_enabled_fraction": initial_enabled / max(1, algebra.num_tasks),
        "too_dense_initial": initial_enabled / max(1, algebra.num_tasks) > 0.35,
        "enable_edges": enable_edges,
        "obstruct_edges": obstruct_edges,
        "obstruct_fraction": obstruct_edges / edge_total,
    }

