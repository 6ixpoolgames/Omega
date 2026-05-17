from __future__ import annotations

import random

from .algebra import AlgebraState, Constructor, Task, TaskAlgebra


def generate_algebra(
    family: str,
    seed: int,
    num_tasks: int = 64,
    num_constructors: int = 2,
) -> TaskAlgebra:
    rng = random.Random(seed)
    if family == "low_resolution_dense":
        return _low_resolution_dense(rng, seed, num_tasks, num_constructors)
    if family == "structured_asymmetric":
        return _structured_asymmetric(rng, seed, num_tasks, num_constructors)
    if family == "lock_in_seeded":
        return _lock_in_seeded(rng, seed, num_tasks, num_constructors)
    raise ValueError(f"unknown generator family: {family}")


def _constructors(num_tasks: int, num_constructors: int, initial: set[int]) -> tuple[Constructor, ...]:
    chunks = [set() for _ in range(num_constructors)]
    for i, task_id in enumerate(sorted(initial)):
        chunks[i % num_constructors].add(task_id)
    return tuple(Constructor(id=i, initial_tasks=frozenset(chunks[i])) for i in range(num_constructors))


def _low_resolution_dense(
    rng: random.Random,
    seed: int,
    num_tasks: int,
    num_constructors: int,
) -> TaskAlgebra:
    initial = set(rng.sample(range(num_tasks), max(1, int(num_tasks * 0.42))))
    tasks: list[Task] = []
    for task_id in range(num_tasks):
        enables = set(rng.sample(range(num_tasks), rng.randint(1, 4))) - {task_id}
        obstructs = set(rng.sample(range(num_tasks), 1)) - {task_id} if rng.random() < 0.08 else set()
        tasks.append(
            Task(
                id=task_id,
                family="dense",
                enabled_by_default=task_id in initial,
                constructor_mask=tuple(range(num_constructors)),
                enables=frozenset(enables),
                obstructs=frozenset(obstructs),
            )
        )
    return TaskAlgebra(
        family="low_resolution_dense",
        seed=seed,
        tasks=tuple(tasks),
        constructors=_constructors(num_tasks, num_constructors, initial),
        initial_state=AlgebraState(frozenset(initial), frozenset(), frozenset()),
    )


def _structured_asymmetric(
    rng: random.Random,
    seed: int,
    num_tasks: int,
    num_constructors: int,
) -> TaskAlgebra:
    initial_count = max(4, num_tasks // 10)
    initial = set(range(initial_count))
    tasks: list[Task] = []
    destructive_start = int(num_tasks * 0.72)
    for task_id in range(num_tasks):
        if task_id < destructive_start:
            family = "structured"
            forward = [x for x in range(task_id + 1, min(num_tasks, task_id + 8)) if x < destructive_start]
            enables = set(rng.sample(forward, min(len(forward), rng.randint(1, 3)))) if forward else set()
            if task_id < num_tasks // 2 and rng.random() < 0.35:
                enables.add(rng.randrange(num_tasks // 2, destructive_start))
            obstructs = set(rng.sample(range(destructive_start, num_tasks), 1)) if rng.random() < 0.18 else set()
        else:
            family = "trap"
            enables = set(rng.sample(range(destructive_start, num_tasks), min(3, num_tasks - destructive_start))) - {task_id}
            obstruct_pool = list(range(initial_count, destructive_start))
            obstructs = set(rng.sample(obstruct_pool, min(len(obstruct_pool), rng.randint(2, 5))))
        tasks.append(
            Task(
                id=task_id,
                family=family,
                enabled_by_default=task_id in initial,
                constructor_mask=tuple(range(num_constructors)),
                enables=frozenset(enables),
                obstructs=frozenset(obstructs),
            )
        )
    return TaskAlgebra(
        family="structured_asymmetric",
        seed=seed,
        tasks=tuple(tasks),
        constructors=_constructors(num_tasks, num_constructors, initial),
        initial_state=AlgebraState(frozenset(initial), frozenset(), frozenset()),
    )


def _lock_in_seeded(
    rng: random.Random,
    seed: int,
    num_tasks: int,
    num_constructors: int,
) -> TaskAlgebra:
    lock_start = int(num_tasks * 0.65)
    initial = set(range(max(4, num_tasks // 12)))
    initial.add(lock_start)
    tasks: list[Task] = []
    for task_id in range(num_tasks):
        if task_id >= lock_start:
            family = "lock_in"
            lock_pool = list(range(lock_start, num_tasks))
            enables = set(rng.sample(lock_pool, min(len(lock_pool), rng.randint(2, 5)))) - {task_id}
            global_pool = list(range(max(4, num_tasks // 12), lock_start))
            obstructs = set(rng.sample(global_pool, min(len(global_pool), rng.randint(3, 7))))
        else:
            family = "structured"
            forward = [x for x in range(task_id + 1, min(lock_start, task_id + 7))]
            enables = set(rng.sample(forward, min(len(forward), rng.randint(1, 3)))) if forward else set()
            obstructs = set(rng.sample(range(lock_start, num_tasks), 1)) if rng.random() < 0.10 else set()
        tasks.append(
            Task(
                id=task_id,
                family=family,
                enabled_by_default=task_id in initial,
                constructor_mask=tuple(range(num_constructors)),
                enables=frozenset(enables),
                obstructs=frozenset(obstructs),
            )
        )
    return TaskAlgebra(
        family="lock_in_seeded",
        seed=seed,
        tasks=tuple(tasks),
        constructors=_constructors(num_tasks, num_constructors, initial),
        initial_state=AlgebraState(frozenset(initial), frozenset(), frozenset()),
    )

