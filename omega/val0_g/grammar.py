from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class GrammarTask:
    id: int
    enables: frozenset[int] = frozenset()
    obstructs: frozenset[int] = frozenset()
    restores: frozenset[int] = frozenset()
    decays: frozenset[int] = frozenset()
    commits: frozenset[int] = frozenset()
    capacity_delta: int = 0


@dataclass(frozen=True)
class GrammarState:
    enabled: frozenset[int]
    disabled: frozenset[int]
    completed: frozenset[int]
    irreversible: frozenset[int]
    capacity: int
    time: int = 0


@dataclass(frozen=True)
class GrammarWorld:
    family: str
    seed: int
    tasks: tuple[GrammarTask, ...]
    initial_state: GrammarState
    params: dict[str, object]

    @property
    def num_tasks(self) -> int:
        return len(self.tasks)

    def task(self, task_id: int) -> GrammarTask:
        return self.tasks[task_id]


def generate_world(family: str, seed: int, num_tasks: int = 64) -> GrammarWorld:
    rng = random.Random(seed)
    if family == "neutral_grammar_v1":
        return _neutral_grammar_v1(rng, seed, num_tasks)
    if family == "low_resolution_dense":
        return _dense_guardrail(rng, seed, num_tasks)
    if family == "brittle_peak":
        return _brittle_guardrail(rng, seed, num_tasks)
    raise ValueError(f"unknown VAL0-G world family: {family}")


def valid_tasks(world: GrammarWorld, state: GrammarState) -> tuple[int, ...]:
    return tuple(sorted(task for task in state.enabled - state.disabled - state.completed if state.capacity + world.task(task).capacity_delta >= 0))


def apply_task(world: GrammarWorld, state: GrammarState, task_id: int) -> GrammarState:
    if task_id not in valid_tasks(world, state):
        raise ValueError(f"task {task_id} is not available")
    task = world.task(task_id)
    completed = state.completed | {task_id}
    irreversible = state.irreversible | task.commits
    restored = task.restores - irreversible
    disabled = ((state.disabled | task.obstructs | task.decays) - restored) | irreversible
    enabled = (state.enabled | task.enables | restored) - disabled - completed
    return GrammarState(
        enabled=frozenset(enabled),
        disabled=frozenset(disabled),
        completed=frozenset(completed),
        irreversible=frozenset(irreversible),
        capacity=state.capacity + task.capacity_delta,
        time=state.time + 1,
    )


def state_signature(state: GrammarState) -> tuple[frozenset[int], frozenset[int], frozenset[int], int]:
    return state.enabled, state.disabled, state.irreversible, state.capacity


def _neutral_grammar_v1(rng: random.Random, seed: int, num_tasks: int) -> GrammarWorld:
    density_regime = rng.choice(("low", "medium", "high"))
    obstruction_regime = rng.choice(("low", "medium", "high"))
    restore_regime = rng.choice(("none", "low", "medium"))
    commit_regime = rng.choice(("none", "low", "medium"))
    decay_regime = rng.choice(("none", "low", "medium"))
    substitute_regime = rng.choice(("low", "medium"))
    capacity_regime = rng.choice(("none", "loose", "tight"))

    enable_range = {"low": (0, 1), "medium": (1, 3), "high": (2, 5)}[density_regime]
    obstruct_p = {"low": 0.16, "medium": 0.32, "high": 0.50}[obstruction_regime]
    restore_p = {"none": 0.0, "low": 0.08, "medium": 0.18}[restore_regime]
    commit_p = {"none": 0.0, "low": 0.06, "medium": 0.14}[commit_regime]
    decay_p = {"none": 0.0, "low": 0.12, "medium": 0.28}[decay_regime]
    substitute_bonus = {"low": 0, "medium": 2}[substitute_regime]
    capacity_start = {"none": num_tasks, "loose": 8, "tight": 4}[capacity_regime]

    initial_count = rng.randint(1, max(2, num_tasks // 12))
    initial = set(rng.sample(range(num_tasks), initial_count))
    tasks: list[GrammarTask] = []
    for task_id in range(num_tasks):
        enable_n = rng.randint(*enable_range) + (substitute_bonus if rng.random() < 0.20 else 0)
        enables = _sample_without(rng, range(num_tasks), task_id, enable_n)
        obstructs = _sample_without(rng, range(num_tasks), task_id, rng.randint(1, 4)) if rng.random() < obstruct_p else set()
        restores = _sample_without(rng, range(num_tasks), task_id, rng.randint(1, 3)) if rng.random() < restore_p else set()
        decays = _sample_without(rng, range(num_tasks), task_id, rng.randint(1, 3)) if rng.random() < decay_p else set()
        commits = set(obstructs) if obstructs and rng.random() < commit_p else set()
        if capacity_regime == "none":
            capacity_delta = 0
        elif capacity_regime == "loose":
            capacity_delta = rng.choice((-1, -1, 0, 0, 1))
        else:
            capacity_delta = rng.choice((-2, -1, -1, 0, 1))
        tasks.append(
            GrammarTask(
                id=task_id,
                enables=frozenset(enables),
                obstructs=frozenset(obstructs),
                restores=frozenset(restores),
                decays=frozenset(decays),
                commits=frozenset(commits),
                capacity_delta=capacity_delta,
            )
        )
    params = {
        "density_regime": density_regime,
        "obstruction_regime": obstruction_regime,
        "restore_regime": restore_regime,
        "commit_regime": commit_regime,
        "decay_regime": decay_regime,
        "substitute_regime": substitute_regime,
        "capacity_regime": capacity_regime,
        "initial_count": initial_count,
    }
    return GrammarWorld(
        family="neutral_grammar_v1",
        seed=seed,
        tasks=tuple(tasks),
        initial_state=GrammarState(frozenset(initial), frozenset(), frozenset(), frozenset(), capacity_start),
        params=params,
    )


def _dense_guardrail(rng: random.Random, seed: int, num_tasks: int) -> GrammarWorld:
    initial = set(rng.sample(range(num_tasks), max(1, int(num_tasks * 0.42))))
    tasks = [
        GrammarTask(
            id=task_id,
            enables=frozenset(_sample_without(rng, range(num_tasks), task_id, rng.randint(2, 6))),
            obstructs=frozenset(_sample_without(rng, range(num_tasks), task_id, 1)) if rng.random() < 0.05 else frozenset(),
        )
        for task_id in range(num_tasks)
    ]
    return GrammarWorld(
        family="low_resolution_dense",
        seed=seed,
        tasks=tuple(tasks),
        initial_state=GrammarState(frozenset(initial), frozenset(), frozenset(), frozenset(), num_tasks),
        params={"guardrail": "flat_dense", "initial_count": len(initial)},
    )


def _brittle_guardrail(rng: random.Random, seed: int, num_tasks: int) -> GrammarWorld:
    initial = {0, 1}
    brittle_start = 2
    robust_start = max(18, int(num_tasks * 0.42))
    sink_start = max(robust_start + 14, int(num_tasks * 0.72))
    tasks: list[GrammarTask] = []
    for task_id in range(num_tasks):
        if task_id == 0:
            enables = set(range(brittle_start, min(robust_start, brittle_start + 14)))
            obstructs: set[int] = set()
        elif task_id == 1:
            enables = set(range(robust_start, min(sink_start, robust_start + 7)))
            obstructs = set()
        elif brittle_start <= task_id < robust_start:
            enables = _sample_without(rng, range(brittle_start, robust_start), task_id, rng.randint(1, 4))
            enables |= set(rng.sample(range(sink_start, num_tasks), min(max(0, num_tasks - sink_start), rng.randint(0, 2))))
            obstructs = set(rng.sample(range(robust_start, sink_start), min(max(0, sink_start - robust_start), rng.randint(4, 9))))
        elif robust_start <= task_id < sink_start:
            enables = set(range(task_id + 1, min(sink_start, task_id + rng.randint(2, 5))))
            if rng.random() < 0.35:
                enables.add(rng.randrange(robust_start, sink_start))
            enables.discard(task_id)
            obstructs = set()
        else:
            enables = set()
            obstructs = set()
        tasks.append(GrammarTask(id=task_id, enables=frozenset(enables), obstructs=frozenset(obstructs)))
    return GrammarWorld(
        family="brittle_peak",
        seed=seed,
        tasks=tuple(tasks),
        initial_state=GrammarState(frozenset(initial), frozenset(), frozenset(), frozenset(), num_tasks),
        params={"guardrail": "thin_ridge_brittle_peak", "initial_count": len(initial)},
    )


def _sample_without(rng: random.Random, population: range, excluded: int, count: int) -> set[int]:
    items = [item for item in population if item != excluded]
    if not items or count <= 0:
        return set()
    return set(rng.sample(items, min(len(items), count)))
