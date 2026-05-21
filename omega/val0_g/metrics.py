from __future__ import annotations

import random
from collections import deque
from statistics import mean

from .grammar import GrammarState, GrammarWorld, apply_task, state_signature, valid_tasks


DEPTHS = (1, 2, 4, 8, 16)


def geometry_metrics(
    world: GrammarWorld,
    max_states_per_depth: int,
    rollout_samples: int,
    cut_samples: int,
    seed: int,
) -> dict[str, float | int]:
    rng = random.Random(seed)
    states_by_depth = reachable_states_by_depth(world, DEPTHS, max_states_per_depth, rng)
    masses = {depth: len(states_by_depth.get(depth, ())) for depth in DEPTHS}
    nonterminal = {
        depth: sum(1 for state in states_by_depth.get(depth, ()) if valid_tasks(world, state))
        for depth in DEPTHS
    }
    survival_auc = sum(nonterminal[depth] / max(1, masses.get(1, 1)) for depth in DEPTHS) / len(DEPTHS)
    survival_slope = (nonterminal[16] - nonterminal[1]) / 15.0
    terminal_probs = terminal_probabilities(world, rollout_samples, (4, 8, 16), random.Random(seed + 100_000))
    cut_ratio = cut_sensitivity(world, horizon=16, cut_samples=cut_samples, max_states_per_depth=max_states_per_depth, rng=random.Random(seed + 200_000))
    row: dict[str, float | int] = {
        "survival_auc": survival_auc,
        "survival_slope": survival_slope,
        "cut_sensitivity_k1": cut_ratio,
    }
    for depth in DEPTHS:
        row[f"survival_d{depth}"] = nonterminal[depth]
        row[f"descendant_mass_d{depth}"] = masses[depth]
    for left, right in ((1, 2), (2, 4), (4, 8), (8, 16)):
        row[f"branching_B{left}"] = masses[right] / max(1, masses[left])
    for depth, value in terminal_probs.items():
        row[f"P_terminal_d{depth}"] = value
    row["posthoc_class"] = classify_geometry(row)
    return row


def reachable_states_by_depth(
    world: GrammarWorld,
    depths: tuple[int, ...],
    max_states_per_depth: int,
    rng: random.Random,
) -> dict[int, tuple[GrammarState, ...]]:
    target_depths = set(depths)
    max_depth = max(depths)
    states_by_depth: dict[int, list[GrammarState]] = {0: [world.initial_state]}
    signatures_by_depth: dict[int, set[tuple[frozenset[int], frozenset[int], frozenset[int], int]]] = {0: {state_signature(world.initial_state)}}
    for depth in range(1, max_depth + 1):
        previous = states_by_depth.get(depth - 1, [])
        next_states: list[GrammarState] = []
        next_signatures: set[tuple[frozenset[int], frozenset[int], frozenset[int], int]] = set()
        shuffled_previous = list(previous)
        rng.shuffle(shuffled_previous)
        for state in shuffled_previous:
            tasks = list(valid_tasks(world, state))
            rng.shuffle(tasks)
            for task_id in tasks:
                try:
                    next_state = apply_task(world, state, task_id)
                except ValueError:
                    continue
                signature = state_signature(next_state)
                if signature in next_signatures:
                    continue
                next_signatures.add(signature)
                next_states.append(next_state)
                if len(next_states) >= max_states_per_depth:
                    break
            if len(next_states) >= max_states_per_depth:
                break
        states_by_depth[depth] = next_states
        signatures_by_depth[depth] = next_signatures
    return {depth: tuple(states_by_depth.get(depth, [])) for depth in target_depths}


def terminal_probabilities(
    world: GrammarWorld,
    rollout_samples: int,
    depths: tuple[int, ...],
    rng: random.Random,
) -> dict[int, float]:
    terminals = {depth: 0 for depth in depths}
    for _ in range(rollout_samples):
        state = world.initial_state
        terminal_depth = None
        for depth in range(1, max(depths) + 1):
            available = valid_tasks(world, state)
            if not available:
                terminal_depth = depth
                break
            state = apply_task(world, state, rng.choice(available))
        if terminal_depth is None and not valid_tasks(world, state):
            terminal_depth = max(depths)
        if terminal_depth is not None:
            for depth in depths:
                if terminal_depth <= depth:
                    terminals[depth] += 1
    return {depth: terminals[depth] / max(1, rollout_samples) for depth in depths}


def cut_sensitivity(
    world: GrammarWorld,
    horizon: int,
    cut_samples: int,
    max_states_per_depth: int,
    rng: random.Random,
) -> float:
    base_mass = len(reachable_states_by_depth(world, (horizon,), max_states_per_depth, rng).get(horizon, ()))
    candidates = list(valid_tasks(world, world.initial_state))
    if not candidates or base_mass == 0:
        return 0.0
    if len(candidates) > cut_samples:
        candidates = rng.sample(candidates, cut_samples)
    ratios: list[float] = []
    for task_id in candidates:
        cut_state = GrammarState(
            enabled=frozenset(task for task in world.initial_state.enabled if task != task_id),
            disabled=world.initial_state.disabled,
            completed=world.initial_state.completed,
            irreversible=world.initial_state.irreversible,
            capacity=world.initial_state.capacity,
            time=world.initial_state.time,
        )
        cut_world = GrammarWorld(world.family, world.seed, world.tasks, cut_state, world.params)
        cut_mass = len(reachable_states_by_depth(cut_world, (horizon,), max_states_per_depth, rng).get(horizon, ()))
        ratios.append(cut_mass / max(1, base_mass))
    return mean(ratios) if ratios else 0.0


def classify_geometry(row: dict[str, float | int]) -> str:
    d1 = float(row["descendant_mass_d1"])
    d16 = float(row["descendant_mass_d16"])
    auc = float(row["survival_auc"])
    terminal = float(row["P_terminal_d16"])
    cut = float(row["cut_sensitivity_k1"])
    b8 = float(row["branching_B8"])
    if d1 > 24 and abs(d16 - d1) < 8 and terminal < 0.15:
        return "flat_dense"
    if terminal > 0.70 or d16 <= 1:
        return "self_terminating"
    if cut < 0.45 and d16 > 4:
        return "thin_ridge"
    if auc > 20 and cut > 0.75 and terminal < 0.25:
        return "recoverable_basin_like"
    if b8 > 1.25 and terminal < 0.35:
        return "lush_branching_like"
    if d16 > d1 and terminal < 0.45:
        return "deep_corridor_like"
    return "mixed_or_noise"
