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
    if family == "brittle_peak":
        return _brittle_peak(rng, seed, num_tasks, num_constructors)
    if family == "structured_asymmetric_v2":
        return _structured_asymmetric_v2(rng, seed, num_tasks, num_constructors)
    if family == "low_resolution_dense":
        return _low_resolution_dense(rng, seed, num_tasks, num_constructors)
    if family == "structured_asymmetric":
        return _structured_asymmetric(rng, seed, num_tasks, num_constructors)
    if family == "lock_in_seeded":
        return _lock_in_seeded(rng, seed, num_tasks, num_constructors)
    if family == "case_brittle_peak":
        return _case_brittle_peak(num_tasks, num_constructors)
    if family == "case_flat":
        return _case_flat(num_tasks, num_constructors)
    if family == "case_lock_in":
        return _lock_in_seeded(random.Random(7), seed, num_tasks, num_constructors)
    if family == "case_sparse_collapse":
        return _case_sparse_collapse(num_tasks, num_constructors)
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


def _brittle_peak(
    rng: random.Random,
    seed: int,
    num_tasks: int,
    num_constructors: int,
) -> TaskAlgebra:
    initial = {0, 1}
    brittle_start = 2
    robust_start = max(18, int(num_tasks * 0.42))
    sink_start = max(robust_start + 14, int(num_tasks * 0.72))
    tasks: list[Task] = []
    for task_id in range(num_tasks):
        if task_id == 0:
            family = "brittle_root"
            enables = set(range(brittle_start, min(robust_start, brittle_start + 14)))
            obstructs: set[int] = set()
        elif task_id == 1:
            family = "robust_root"
            enables = set(range(robust_start, min(sink_start, robust_start + 7)))
            obstructs = set()
        elif brittle_start <= task_id < robust_start:
            family = "brittle"
            local_pool = list(range(brittle_start, robust_start))
            sink_pool = list(range(sink_start, num_tasks))
            enables = set(rng.sample(local_pool, min(len(local_pool), rng.randint(1, 4)))) - {task_id}
            enables |= set(rng.sample(sink_pool, min(len(sink_pool), rng.randint(0, 2))))
            obstruct_pool = [x for x in range(robust_start, sink_start) if x != task_id]
            obstructs = set(rng.sample(obstruct_pool, min(len(obstruct_pool), rng.randint(4, 9))))
            if rng.random() < 0.55:
                obstructs |= set(rng.sample(local_pool, min(len(local_pool), rng.randint(2, 5))))
                obstructs.discard(task_id)
        elif robust_start <= task_id < sink_start:
            family = "robust"
            forward = [x for x in range(task_id + 1, min(sink_start, task_id + 6))]
            siblings = list(range(robust_start, sink_start))
            enables = set(rng.sample(forward, min(len(forward), rng.randint(1, 3)))) if forward else set()
            if rng.random() < 0.45:
                enables.add(rng.choice(siblings))
            enables.discard(task_id)
            obstructs = set(rng.sample(range(sink_start, num_tasks), 1)) if rng.random() < 0.08 and sink_start < num_tasks else set()
        else:
            family = "sink"
            enables = set()
            obstructs = set()
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
        family="brittle_peak",
        seed=seed,
        tasks=tuple(tasks),
        constructors=_constructors(num_tasks, num_constructors, initial),
        initial_state=AlgebraState(frozenset(initial), frozenset(), frozenset()),
    )


def _structured_asymmetric_v2(
    rng: random.Random,
    seed: int,
    num_tasks: int,
    num_constructors: int,
) -> TaskAlgebra:
    base = _brittle_peak(rng, seed, num_tasks, num_constructors)
    tasks: list[Task] = []
    for task in base.tasks:
        family = "structured" if task.family in {"brittle_root", "robust_root"} else task.family
        enables = set(task.enables)
        obstructs = set(task.obstructs)
        if family == "brittle" and rng.random() < 0.45:
            obstructs = set(rng.sample(list(obstructs), max(0, len(obstructs) // 2))) if obstructs else set()
        if family == "robust" and rng.random() < 0.25:
            later = [x for x in range(task.id + 1, min(base.num_tasks, task.id + 8))]
            if later:
                enables.add(rng.choice(later))
        tasks.append(
            Task(
                id=task.id,
                family=family,
                cost=task.cost,
                reliability=task.reliability,
                enabled_by_default=task.enabled_by_default,
                constructor_mask=task.constructor_mask,
                enables=frozenset(enables),
                obstructs=frozenset(obstructs),
            )
        )
    return TaskAlgebra(
        family="structured_asymmetric_v2",
        seed=seed,
        tasks=tuple(tasks),
        constructors=base.constructors,
        initial_state=base.initial_state,
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


def _case_brittle_peak(num_tasks: int, num_constructors: int) -> TaskAlgebra:
    num_tasks = max(num_tasks, 32)
    initial = {0, 1}
    tasks: list[Task] = []
    for task_id in range(num_tasks):
        family = "filler"
        enables: set[int] = set()
        obstructs: set[int] = set()
        if task_id == 0:
            family = "brittle_root"
            enables = set(range(2, 14))
        elif task_id == 1:
            family = "robust_root"
            enables = set(range(14, min(num_tasks, 22)))
        elif 2 <= task_id < 14:
            family = "brittle"
            enables = set(range(2, 14)) - {task_id}
            obstructs = set(range(14, num_tasks))
        elif 14 <= task_id < num_tasks:
            family = "robust"
            enables = {x for x in (task_id + 1, task_id + 2, task_id + 3) if x < num_tasks}
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
        family="case_brittle_peak",
        seed=0,
        tasks=tuple(tasks),
        constructors=_constructors(num_tasks, num_constructors, initial),
        initial_state=AlgebraState(frozenset(initial), frozenset(), frozenset()),
    )


def _case_flat(num_tasks: int, num_constructors: int) -> TaskAlgebra:
    num_tasks = max(num_tasks, 32)
    initial = {0, 1, 2, 3}
    tasks: list[Task] = []
    for task_id in range(num_tasks):
        enables = {x for x in (task_id + 4, task_id + 8) if x < num_tasks}
        tasks.append(
            Task(
                id=task_id,
                family="flat",
                enabled_by_default=task_id in initial,
                constructor_mask=tuple(range(num_constructors)),
                enables=frozenset(enables),
                obstructs=frozenset(),
            )
        )
    return TaskAlgebra(
        family="case_flat",
        seed=0,
        tasks=tuple(tasks),
        constructors=_constructors(num_tasks, num_constructors, initial),
        initial_state=AlgebraState(frozenset(initial), frozenset(), frozenset()),
    )


def _case_sparse_collapse(num_tasks: int, num_constructors: int) -> TaskAlgebra:
    num_tasks = max(num_tasks, 32)
    initial = {0, 1}
    tasks: list[Task] = []
    for task_id in range(num_tasks):
        if task_id == 0:
            enables = {2}
        elif task_id == 1:
            enables = {3}
        else:
            enables = set()
        tasks.append(
            Task(
                id=task_id,
                family="sparse",
                enabled_by_default=task_id in initial,
                constructor_mask=tuple(range(num_constructors)),
                enables=frozenset(enables),
                obstructs=frozenset(),
            )
        )
    return TaskAlgebra(
        family="case_sparse_collapse",
        seed=0,
        tasks=tuple(tasks),
        constructors=_constructors(num_tasks, num_constructors, initial),
        initial_state=AlgebraState(frozenset(initial), frozenset(), frozenset()),
    )

