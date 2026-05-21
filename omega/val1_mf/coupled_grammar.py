from __future__ import annotations

import random
from dataclasses import dataclass

from omega.val0_g.grammar import GrammarState, GrammarWorld, apply_task, generate_world, valid_tasks


@dataclass(frozen=True)
class CrossEffects:
    enables: frozenset[int] = frozenset()
    obstructs: frozenset[int] = frozenset()
    restores: frozenset[int] = frozenset()
    commits: frozenset[int] = frozenset()
    shared_capacity_delta: int = 0


@dataclass(frozen=True)
class JointState:
    state_A: GrammarState
    state_B: GrammarState
    shared_capacity: int


@dataclass(frozen=True)
class JointWorld:
    seed_pair: int
    world_A: GrammarWorld
    world_B: GrammarWorld
    cross_A_to_B: dict[int, CrossEffects]
    cross_B_to_A: dict[int, CrossEffects]
    params: dict[str, object]
    initial_state: JointState


def generate_joint_world(seed_pair: int, num_tasks: int = 64) -> JointWorld:
    rng = random.Random(seed_pair)
    seed_A = seed_pair * 2 + 11
    seed_B = seed_pair * 2 + 12
    world_A = generate_world("neutral_grammar_v1", seed_A, num_tasks)
    world_B = generate_world("neutral_grammar_v1", seed_B, num_tasks)
    coupling_density = rng.choice(("none", "sparse", "medium"))
    cross_effect_balance = rng.choice(("enable_heavy", "obstruct_heavy", "restore_heavy", "mixed"))
    shared_capacity_pressure = rng.choice(("none", "loose", "tight"))
    cross_commit_probability = rng.choice(("none", "low", "medium"))
    symmetry = rng.choice(("symmetric", "A_heavier", "B_heavier"))
    params = {
        "coupling_density": coupling_density,
        "cross_effect_balance": cross_effect_balance,
        "shared_capacity_pressure": shared_capacity_pressure,
        "cross_commit_probability": cross_commit_probability,
        "symmetry": symmetry,
        "seed_A": seed_A,
        "seed_B": seed_B,
    }
    shared_capacity = {"none": num_tasks, "loose": 12, "tight": 6}[shared_capacity_pressure]
    cross_A_to_B = _sample_cross_effects(rng, num_tasks, coupling_density, cross_effect_balance, cross_commit_probability, _side_scale(symmetry, "A"))
    cross_B_to_A = _sample_cross_effects(rng, num_tasks, coupling_density, cross_effect_balance, cross_commit_probability, _side_scale(symmetry, "B"))
    return JointWorld(
        seed_pair=seed_pair,
        world_A=world_A,
        world_B=world_B,
        cross_A_to_B=cross_A_to_B,
        cross_B_to_A=cross_B_to_A,
        params=params,
        initial_state=JointState(world_A.initial_state, world_B.initial_state, shared_capacity),
    )


def valid_joint_actions(joint: JointWorld, state: JointState) -> tuple[tuple[str, int], ...]:
    actions: list[tuple[str, int]] = []
    for task_id in valid_tasks(joint.world_A, state.state_A):
        effect = joint.cross_A_to_B.get(task_id, CrossEffects())
        if state.shared_capacity + effect.shared_capacity_delta >= 0:
            actions.append(("A", task_id))
    for task_id in valid_tasks(joint.world_B, state.state_B):
        effect = joint.cross_B_to_A.get(task_id, CrossEffects())
        if state.shared_capacity + effect.shared_capacity_delta >= 0:
            actions.append(("B", task_id))
    return tuple(actions)


def apply_joint_action(joint: JointWorld, state: JointState, action: tuple[str, int]) -> JointState:
    side, task_id = action
    if side == "A":
        next_A = apply_task(joint.world_A, state.state_A, task_id)
        effect = joint.cross_A_to_B.get(task_id, CrossEffects())
        next_B = _apply_cross_effect(state.state_B, effect)
    elif side == "B":
        next_B = apply_task(joint.world_B, state.state_B, task_id)
        effect = joint.cross_B_to_A.get(task_id, CrossEffects())
        next_A = _apply_cross_effect(state.state_A, effect)
    else:
        raise ValueError(f"unknown joint action side: {side}")
    return JointState(next_A, next_B, state.shared_capacity + effect.shared_capacity_delta)


def joint_signature(state: JointState) -> tuple[object, ...]:
    return (
        state.state_A.enabled,
        state.state_A.disabled,
        state.state_A.completed,
        state.state_A.irreversible,
        state.state_A.capacity,
        state.state_B.enabled,
        state.state_B.disabled,
        state.state_B.completed,
        state.state_B.irreversible,
        state.state_B.capacity,
        state.shared_capacity,
    )


def cross_edge_counts(joint: JointWorld) -> dict[str, int]:
    return {
        "cross_enable_edges_A_to_B": sum(len(effect.enables) for effect in joint.cross_A_to_B.values()),
        "cross_enable_edges_B_to_A": sum(len(effect.enables) for effect in joint.cross_B_to_A.values()),
        "cross_obstruct_edges_A_to_B": sum(len(effect.obstructs) for effect in joint.cross_A_to_B.values()),
        "cross_obstruct_edges_B_to_A": sum(len(effect.obstructs) for effect in joint.cross_B_to_A.values()),
        "cross_restore_edges_A_to_B": sum(len(effect.restores) for effect in joint.cross_A_to_B.values()),
        "cross_restore_edges_B_to_A": sum(len(effect.restores) for effect in joint.cross_B_to_A.values()),
        "cross_commit_edges_A_to_B": sum(len(effect.commits) for effect in joint.cross_A_to_B.values()),
        "cross_commit_edges_B_to_A": sum(len(effect.commits) for effect in joint.cross_B_to_A.values()),
    }


def _sample_cross_effects(
    rng: random.Random,
    num_tasks: int,
    coupling_density: str,
    cross_effect_balance: str,
    cross_commit_probability: str,
    side_scale: float,
) -> dict[int, CrossEffects]:
    base_p = {"none": 0.0, "sparse": 0.10, "medium": 0.22}[coupling_density] * side_scale
    commit_p = {"none": 0.0, "low": 0.08, "medium": 0.18}[cross_commit_probability]
    weights = {
        "enable_heavy": (0.55, 0.20, 0.20),
        "obstruct_heavy": (0.18, 0.58, 0.16),
        "restore_heavy": (0.20, 0.18, 0.55),
        "mixed": (0.34, 0.33, 0.25),
    }[cross_effect_balance]
    effects: dict[int, CrossEffects] = {}
    for task_id in range(num_tasks):
        if rng.random() >= base_p:
            continue
        enables: set[int] = set()
        obstructs: set[int] = set()
        restores: set[int] = set()
        if rng.random() < weights[0]:
            enables = _sample_ids(rng, num_tasks, rng.randint(1, 3))
        if rng.random() < weights[1]:
            obstructs = _sample_ids(rng, num_tasks, rng.randint(1, 3))
        if rng.random() < weights[2]:
            restores = _sample_ids(rng, num_tasks, rng.randint(1, 2))
        commits = set(obstructs) if obstructs and rng.random() < commit_p else set()
        shared_delta = rng.choice((-1, 0, 0, 1)) if rng.random() < base_p else 0
        effects[task_id] = CrossEffects(
            frozenset(enables),
            frozenset(obstructs),
            frozenset(restores),
            frozenset(commits),
            shared_delta,
        )
    return effects


def _apply_cross_effect(state: GrammarState, effect: CrossEffects) -> GrammarState:
    irreversible = state.irreversible | effect.commits
    restored = effect.restores - irreversible
    disabled = ((state.disabled | effect.obstructs) - restored) | irreversible
    enabled = (state.enabled | effect.enables | restored) - disabled - state.completed
    return GrammarState(
        enabled=frozenset(enabled),
        disabled=frozenset(disabled),
        completed=state.completed,
        irreversible=frozenset(irreversible),
        capacity=state.capacity,
        time=state.time,
    )


def _sample_ids(rng: random.Random, num_tasks: int, count: int) -> set[int]:
    return set(rng.sample(range(num_tasks), min(num_tasks, count)))


def _side_scale(symmetry: str, side: str) -> float:
    if symmetry == "symmetric":
        return 1.0
    if symmetry == "A_heavier":
        return 1.35 if side == "A" else 0.75
    if symmetry == "B_heavier":
        return 1.35 if side == "B" else 0.75
    return 1.0
