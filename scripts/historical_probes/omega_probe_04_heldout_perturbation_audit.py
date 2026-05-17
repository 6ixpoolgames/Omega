from __future__ import annotations

import csv
import json
import math
import os
import random
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib-cache"))

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - optional dependency
    plt = None


SOFT_LIMIT_SECONDS = 900
HARD_LIMIT_SECONDS = 1200
N_PERTURB_WORLDS = 40
N_PERTURB_WORLDS_MAX = 80
WORKERS = max(1, min(12, (os.cpu_count() or 4) - 2))
MAX_TRAJ_PER_STATE = 18000
MAX_ENERGY = 4
INITIAL_ENERGY = 4
HORIZONS = [3, 4, 5, 6]
START_LABELS = [
    "open",
    "noise_swamp",
    "bottleneck",
    "loop",
    "resource_corridor",
    "dead_branch",
    "near_trap",
    "rigid_attractor",
]

ACTIONS = ["U", "D", "L", "R", "WAIT"]
BASE_GRID = [
    "OOOOOSSSS",
    "OOOOOSSSS",
    "OOOBBSSSS",
    "LLLBBCCCC",
    "LLLBBCCCC",
    "LLLBBCCCC",
    "DDD..RRRR",
    "DDD..RRRR",
    "TTT..AAAA",
]

COARSE_NAMES = [
    "region",
    "viability_signature",
    "hash_k34_s1206",
    "random_5_fixed",
    "identity",
    "all_one",
    "trap_mixing_adversarial",
    "checkerboard",
    "best_of_10_hashes_per_world",
]

START_TIME = time.time()
STATE_SPACE = [(x, y, e) for y in range(9) for x in range(9) for e in range(MAX_ENERGY + 1)]


def should_continue_block() -> bool:
    return time.time() - START_TIME < SOFT_LIMIT_SECONDS


def should_abort_now() -> bool:
    return time.time() - START_TIME > HARD_LIMIT_SECONDS


def status_code() -> str:
    elapsed = time.time() - START_TIME
    if elapsed > HARD_LIMIT_SECONDS:
        return "PARTIAL_EXIT_HARD_LIMIT"
    if elapsed > SOFT_LIMIT_SECONDS:
        return "PARTIAL_EXIT_SOFT_LIMIT"
    return "COMPLETE"


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    out = 0.0
    for count in counts.values():
        p = count / total
        out -= p * math.log(p)
    return out


def grid_copy(rows: list[str]) -> list[list[str]]:
    return [list(row) for row in rows]


def rows_from_grid(grid: list[list[str]]) -> list[str]:
    return ["".join(row) for row in grid]


def region_xy(grid: list[str], x: int, y: int) -> str:
    if x < 0 or y < 0 or x >= 9 or y >= 9:
        return "#"
    return grid[y][x]


def move_xy(x: int, y: int, action: str) -> tuple[int, int]:
    if action == "U":
        return x, y - 1
    if action == "D":
        return x, y + 1
    if action == "L":
        return x - 1, y
    if action == "R":
        return x + 1, y
    return x, y


@dataclass
class World:
    grid: list[str]
    noise_slip_prob: float
    rigid_mode: str
    seed: int
    perturbations: list[str]


def base_world(seed: int) -> World:
    return World(grid=BASE_GRID[:], noise_slip_prob=0.2, rigid_mode="sticky", seed=seed, perturbations=[])


def reflect_horizontal(grid: list[list[str]]) -> list[list[str]]:
    return [list(reversed(row)) for row in grid]


def perturb_world(seed: int) -> World:
    rng = random.Random(seed)
    grid = grid_copy(BASE_GRID)
    perturbations = []

    n = rng.randint(2, 4)
    perturb_choices = [
        "trap_shift",
        "corridor_variation",
        "noise_variation",
        "bottleneck_width",
        "rigid_variation",
        "symmetry_transform",
    ]
    chosen = rng.sample(perturb_choices, k=n)

    for choice in chosen:
        perturbations.append(choice)
        if choice == "trap_shift":
            candidates = [(x, y) for y in range(9) for x in range(9) if grid[y][x] in {"T", "D", "."}]
            if candidates:
                x, y = rng.choice(candidates)
                nx, ny = max(0, min(8, x + rng.choice([-1, 0, 1]))), max(0, min(8, y + rng.choice([-1, 0, 1])))
                grid[y][x], grid[ny][nx] = grid[ny][nx], grid[y][x]
        elif choice == "corridor_variation":
            corridor = [(x, y) for y in range(3, 6) for x in range(4, 9)]
            for _ in range(rng.randint(1, 3)):
                x, y = rng.choice(corridor)
                grid[y][x] = "C" if grid[y][x] != "C" else rng.choice([".", "O", "B"])
        elif choice == "noise_variation":
            pass
        elif choice == "bottleneck_width":
            cells = [(x, y) for y in range(2, 5) for x in range(2, 5)]
            x, y = rng.choice(cells)
            grid[y][x] = "B" if grid[y][x] != "B" else rng.choice(["O", "."])
        elif choice == "rigid_variation":
            rigid = [(x, y) for y in range(6, 9) for x in range(5, 9) if grid[y][x] in {"R", "A", "."}]
            if rigid:
                x, y = rng.choice(rigid)
                grid[y][x] = rng.choice(["R", "A"])
            rigid_mode = "bounded" if rng.random() < 0.5 else "sticky"
        elif choice == "symmetry_transform" and rng.random() < 0.15:
            if rng.random() < 0.5:
                grid = reflect_horizontal(grid)
            else:
                grid = [list(row) for row in rows_from_grid(grid)[::-1]]

    if "rigid_mode" not in locals():
        rigid_mode = "sticky"
    noise_slip_prob = rng.choice([0.1, 0.2, 0.3, 0.4])
    return World(grid=rows_from_grid(grid), noise_slip_prob=noise_slip_prob, rigid_mode=rigid_mode, seed=seed, perturbations=perturbations)


def select_starts(grid: list[str]) -> dict[str, tuple[int, int, int]]:
    mapping = {}
    target_labels = {
        "open": "O",
        "noise_swamp": "S",
        "bottleneck": "B",
        "loop": "L",
        "resource_corridor": "C",
        "dead_branch": "D",
        "near_trap": "T",
        "rigid_attractor": "R",
    }
    for name, label in target_labels.items():
        found = None
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == label:
                    found = (x, y, INITIAL_ENERGY)
                    break
            if found:
                break
        if found:
            mapping[name] = found
    if "near_trap" not in mapping:
        # use a cell adjacent to T when possible
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell == "T":
                    for nx, ny in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                        if 0 <= nx < 9 and 0 <= ny < 9 and grid[ny][nx] != "T":
                            mapping["near_trap"] = (nx, ny, INITIAL_ENERGY)
                            break
                    if "near_trap" in mapping:
                        break
            if "near_trap" in mapping:
                break
    return mapping


def coarse_region(state: tuple[int, int, int], grid: list[str]) -> str:
    return region_xy(grid, state[0], state[1])


def trap_distance_bin(state: tuple[int, int, int], grid: list[str]) -> str:
    x, y, _ = state
    traps = [(tx, ty) for ty, row in enumerate(grid) for tx, c in enumerate(row) if c == "T"]
    if not traps:
        return "far"
    distance = min(abs(x - tx) + abs(y - ty) for tx, ty in traps)
    return "near" if distance <= 2 else "far"


def local_branching_bin(state: tuple[int, int, int], world: World) -> str:
    count = 0
    for action in ACTIONS:
        for next_state, _ in transition(state, action, world):
            if viable_transition(next_state, world.grid):
                count += 1
    if count <= 2:
        return "low"
    if count <= 6:
        return "med"
    return "high"


def coarse_viability_signature(state: tuple[int, int, int], world: World) -> tuple[str, str, str]:
    _, _, energy = state
    if energy <= 1:
        energy_bin = "e_low"
    elif energy <= 3:
        energy_bin = "e_med"
    else:
        energy_bin = "e_high"
    return energy_bin, trap_distance_bin(state, world.grid), local_branching_bin(state, world)


RNG = random.Random(7)
RANDOM_LABELS = {(x, y): f"q{RNG.randrange(5)}" for y in range(9) for x in range(9)}


def coarse_random_5_fixed(state: tuple[int, int, int], world: World) -> str:
    return RANDOM_LABELS[(state[0], state[1])]


def coarse_identity(state: tuple[int, int, int], world: World) -> tuple[int, int, int]:
    return state


def coarse_all_one(state: tuple[int, int, int], world: World) -> str:
    return "all_one"


def coarse_trap_mixing_adversarial(state: tuple[int, int, int], world: World) -> str:
    x, y, _ = state
    r = region_xy(world.grid, x, y)
    if r == "T" or trap_distance_bin(state, world.grid) == "near":
        return f"mix{(x + y) % 2}"
    if r in {"O", ".", "S"}:
        return f"mix{(x + 2 * y) % 3}"
    return f"mix{(2 * x + y) % 4}"


def coarse_checkerboard(state: tuple[int, int, int], world: World) -> int:
    x, y, _ = state
    return (x + y) % 2


def hash_partition_factory(k: int, seed: int):
    a = 1 + (seed * 3) % 7
    b = 2 + (seed * 5) % 11
    c = 3 + (seed * 7) % 13
    return lambda state: (a * state[0] + b * state[1] + c * state[2]) % k


def transition(state: tuple[int, int, int], action: str, world: World) -> list[tuple[tuple[int, int, int], float]]:
    x, y, energy = state
    current = region_xy(world.grid, x, y)
    if current in {"R", "A", "T"}:
        return [(apply_rules(x, y, energy, action, world), 1.0)]

    candidate_actions = [action]
    if current == "S":
        if rng_from_state(state, world.seed).random() < world.noise_slip_prob:
            candidate_actions = ACTIONS
        elif action in {"U", "D"}:
            candidate_actions = [action, "L", "R", "WAIT"]
        elif action in {"L", "R"}:
            candidate_actions = [action, "U", "D", "WAIT"]
    elif current == "D" and action != "WAIT":
        candidate_actions = [action, "WAIT"]
    prob = 1.0 / len(candidate_actions)
    return [(apply_rules(x, y, energy, a, world), prob) for a in candidate_actions]


def rng_from_state(state: tuple[int, int, int], seed: int) -> random.Random:
    return random.Random(seed * 7919 + state[0] * 97 + state[1] * 193 + state[2] * 389)


def apply_rules(x: int, y: int, energy: int, action: str, world: World) -> tuple[int, int, int]:
    current = region_xy(world.grid, x, y)
    nx, ny = move_xy(x, y, action)
    if region_xy(world.grid, nx, ny) == "#":
        nx, ny = x, y
    next_region = region_xy(world.grid, nx, ny)

    if current == "T" or next_region == "T":
        return nx, ny, 0

    if current in {"R", "A"}:
        if world.rigid_mode == "bounded" and action != "WAIT":
            return x, y, max(1, energy - 1)
        return x, y, max(1, energy)

    cost = 1 if action == "WAIT" and current != "D" else 2 if current == "D" and action != "WAIT" else 1 if action != "WAIT" else 0
    new_energy = max(0, energy - cost)
    if next_region == "C":
        new_energy = min(MAX_ENERGY, new_energy + 1)
    if next_region in {"R", "A"}:
        new_energy = max(1, new_energy)
    return nx, ny, new_energy


def viable_transition(next_state: tuple[int, int, int], grid: list[str]) -> bool:
    return next_state[2] > 0 and region_xy(grid, next_state[0], next_state[1]) != "T"


def enumerate_trajectories(start_state: tuple[int, int, int], horizon: int, world: World):
    trajectories = [((start_state,), viable_transition(start_state, world.grid))]
    truncated = False
    for _ in range(horizon):
        new_trajectories = []
        for states, still_viable in trajectories:
            if should_abort_now() or len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                truncated = truncated or len(new_trajectories) >= MAX_TRAJ_PER_STATE
                break
            state = states[-1]
            for action in ACTIONS:
                for next_state, _ in transition(state, action, world):
                    new_trajectories.append((states + (next_state,), still_viable and viable_transition(next_state, world.grid)))
                    if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                        truncated = True
                        break
                if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                    break
        trajectories = new_trajectories[:MAX_TRAJ_PER_STATE]
        if should_abort_now():
            truncated = True
            break
    return trajectories, truncated


def trajectory_label(states: tuple[tuple[int, int, int], ...], coarse_name: str, coarse_fn, world: World):
    if coarse_name == "region":
        return tuple(coarse_region(state, world.grid) for state in states)
    if coarse_name == "endpoint_only":
        return region_xy(world.grid, states[-1][0], states[-1][1])
    return tuple(coarse_fn(state, world) for state in states)


def compute_one_step_viable_fraction(state: tuple[int, int, int], world: World) -> float:
    total = 0.0
    viable = 0.0
    for action in ACTIONS:
        for next_state, prob in transition(state, action, world):
            total += prob
            if viable_transition(next_state, world.grid):
                viable += prob
    return viable / max(total, 1e-9)


def next_macro_distribution(state: tuple[int, int, int], coarse_name: str, coarse_fn, world: World) -> Counter:
    dist = Counter()
    for action in ACTIONS:
        for next_state, prob in transition(state, action, world):
            if coarse_name == "region":
                label = coarse_region(next_state, world.grid)
            elif coarse_name == "endpoint_only":
                label = region_xy(world.grid, next_state[0], next_state[1])
            else:
                label = coarse_fn(next_state, world)
            dist[label] += prob
    total = sum(dist.values())
    if total > 0:
        for key in list(dist):
            dist[key] /= total
    return dist


def l1_distance(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)


def exact_metric_for_case(start_name: str, horizon: int, coarse_name: str, coarse_fn, world: World, cache):
    trajectories, truncated = cache[(start_name, horizon)]
    viable = [tr for tr in trajectories if tr[1]]
    classes = Counter()
    for states, _ in viable:
        classes[trajectory_label(states, coarse_name, coarse_fn, world)] += 1
    return entropy(classes), truncated


def compute_world_metrics(world: World) -> list[dict]:
    starts = select_starts(world.grid)
    cache = {}
    trunc_flags = []
    for start_name, start_state in starts.items():
        for horizon in HORIZONS:
            cache[(start_name, horizon)] = enumerate_trajectories(start_state, horizon, world)
            trunc_flags.append(cache[(start_name, horizon)][1])

    rows = []
    coarse_fns = {
        "region": coarse_region,
        "viability_signature": coarse_viability_signature,
        "hash_k34_s1206": lambda state, world: hash_partition_factory(34, 1206)(state),
        "random_5_fixed": coarse_random_5_fixed,
        "identity": coarse_identity,
        "all_one": coarse_all_one,
        "trap_mixing_adversarial": coarse_trap_mixing_adversarial,
        "checkerboard": coarse_checkerboard,
    }

    hash_best_rows = []
    for coarse_name, coarse_fn in coarse_fns.items():
        raw_rows = []
        for start_name in starts:
            for horizon in HORIZONS:
                omega, truncated = exact_metric_for_case(start_name, horizon, coarse_name, coarse_fn, world, cache)
                trajectories, _ = cache[(start_name, horizon)]
                viable = [tr for tr in trajectories if tr[1]]
                raw_rows.append(
                    {
                        "world_seed": world.seed,
                        "coarse_name": coarse_name,
                        "start": start_name,
                        "T": horizon,
                        "I": omega,
                        "N_eff": math.exp(omega),
                        "viable_count": len(viable),
                        "raw_count": len(trajectories),
                        "truncated": int(truncated),
                    }
                )

        if coarse_name == "best_of_10_hashes_per_world":
            # Adaptive control: evaluate 10 hashes and keep the best score per world.
            best_rows = []
            for i in range(10):
                candidate_fn = hash_partition_factory([2, 3, 5, 8, 13, 21, 34, 55][i], world.seed * 31 + i)
                candidate_score = 0.0
                candidate_rows = []
                for start_name in starts:
                    for horizon in HORIZONS:
                        omega, truncated = exact_metric_for_case(start_name, horizon, "hash_k34_s1206", candidate_fn, world, cache)
                        trajectories, _ = cache[(start_name, horizon)]
                        viable = [tr for tr in trajectories if tr[1]]
                        candidate_rows.append(
                            {
                                "world_seed": world.seed,
                                "coarse_name": "best_of_10_hashes_per_world",
                                "start": start_name,
                                "T": horizon,
                                "candidate_id": i,
                                "I": omega,
                                "N_eff": math.exp(omega),
                                "viable_count": len(viable),
                                "raw_count": len(trajectories),
                                "truncated": int(truncated),
                            }
                        )
                        candidate_score += omega
                best_rows.append((candidate_score, candidate_rows))
            if best_rows:
                hash_best_rows = max(best_rows, key=lambda item: item[0])[1]
            continue

        # Coarse metrics for this world.
        label_map = {coarse_fn(state, world) if coarse_name not in {"region", "endpoint_only"} else (
            coarse_region(state, world.grid) if coarse_name == "region" else region_xy(world.grid, state[0], state[1])
        ) for state in STATE_SPACE}
        num_macro = len(label_map)
        num_micro = len(STATE_SPACE)
        r = num_macro / max(num_micro, 1)
        if r <= 0.02:
            comp_gate = 0.0
        elif r >= 0.75:
            comp_gate = 0.0
        elif 0.05 <= r <= 0.40:
            comp_gate = 1.0
        elif r < 0.05:
            comp_gate = r / 0.05
        else:
            comp_gate = (0.75 - r) / (0.75 - 0.40)

        fiber_sizes = []
        groups = defaultdict(list)
        if coarse_name == "region":
            for state in STATE_SPACE:
                groups[coarse_region(state, world.grid)].append(state)
        elif coarse_name == "endpoint_only":
            for state in STATE_SPACE:
                groups[region_xy(world.grid, state[0], state[1])].append(state)
        else:
            for state in STATE_SPACE:
                groups[coarse_fn(state, world)].append(state)

        for items in groups.values():
            fiber_sizes.append(len(items))
        mean_fiber_size = sum(fiber_sizes) / max(len(fiber_sizes), 1)
        singleton_fraction = sum(1 for x in fiber_sizes if x == 1) / max(len(fiber_sizes), 1)
        fiber_score = min(1.0, max(0.0, (mean_fiber_size - 1.0) / 4.0))
        fiber_quality = fiber_score * (1.0 - singleton_fraction)

        variances = []
        weights = []
        support_nontrivial = []
        for label, items in groups.items():
            vals = [compute_one_step_viable_fraction(state, world) for state in items]
            mu = sum(vals) / max(len(vals), 1)
            var = sum((v - mu) ** 2 for v in vals) / max(len(vals), 1)
            variances.append(var)
            weights.append(len(vals))
            support = set()
            for state in items:
                for action in ACTIONS:
                    for next_state, _ in transition(state, action, world):
                        if viable_transition(next_state, world.grid):
                            if coarse_name == "region":
                                support.add(coarse_region(next_state, world.grid))
                            elif coarse_name == "endpoint_only":
                                support.add(region_xy(world.grid, next_state[0], next_state[1]))
                            else:
                                support.add(coarse_fn(next_state, world))
            support_nontrivial.append(1 if 1 <= len(support) <= min(8, num_macro) else 0)
        weighted_mean_variance = sum(v * w for v, w in zip(variances, weights)) / max(sum(weights), 1)
        viability_purity = 1.0 / (1.0 + weighted_mean_variance)
        support_nontriviality = sum(support_nontrivial) / max(len(support_nontrivial), 1)

        pairwise_values = []
        pairwise_weights = []
        for label, items in groups.items():
            if len(items) <= 1:
                pairwise_values.append(0.0)
                pairwise_weights.append(len(items))
                continue
            dists_cache = {state: next_macro_distribution(state, coarse_name, coarse_fn, world) for state in items}
            dists = [l1_distance(dists_cache[s1], dists_cache[s2]) for (s1, s2) in combinations(items, 2)]
            pairwise_values.append(sum(dists) / max(len(dists), 1))
            pairwise_weights.append(len(items))
        weighted_pairwise = sum(v * w for v, w in zip(pairwise_values, pairwise_weights)) / max(sum(pairwise_weights), 1)
        transition_consistency = 1.0 / (1.0 + weighted_pairwise)

        start_rows = []
        trunc_count = 0
        total_cases = 0
        for start_name in starts:
            for horizon in HORIZONS:
                omega, truncated = exact_metric_for_case(start_name, horizon, coarse_name, coarse_fn, world, cache)
                start_rows.append((start_name, horizon, omega))
                trunc_count += int(truncated)
                total_cases += 1
        raw_vals = [row[2] for row in start_rows]
        raw_mean = sum(raw_vals) / max(len(raw_vals), 1)
        raw_max = max(raw_vals) if raw_vals else 0.0
        nontriviality_score = min(1.0, raw_mean / 1.0)

        # Rank stability across horizons.
        by_h = defaultdict(list)
        for start_name, horizon, omega in start_rows:
            if horizon in {3, 4, 5, 6}:
                by_h[horizon].append((start_name, omega))
        rank_corrs = []
        horizons_present = [h for h in [3, 4, 5, 6] if h in by_h]
        for h1, h2 in zip(horizons_present, horizons_present[1:]):
            items1 = sorted(by_h[h1], key=lambda kv: kv[1])
            items2 = sorted(by_h[h2], key=lambda kv: kv[1])
            order1 = {name: i + 1 for i, (name, _) in enumerate(items1)}
            order2 = {name: i + 1 for i, (name, _) in enumerate(items2)}
            xs = [order1.get(name, 0) for name in START_LABELS if name in order1 and name in order2]
            ys = [order2.get(name, 0) for name in START_LABELS if name in order1 and name in order2]
            if len(xs) < 2:
                continue
            mx = sum(xs) / len(xs)
            my = sum(ys) / len(ys)
            num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
            dy = math.sqrt(sum((y - my) ** 2 for y in ys))
            rank_corrs.append(num / max(dx * dy, 1e-9))
        rank_stability = sum(rank_corrs) / max(len(rank_corrs), 1) if rank_corrs else 0.0

        admissibility_v2 = viability_purity * transition_consistency * max(rank_stability, 0.0) * nontriviality_score * comp_gate * fiber_quality
        certified_v2 = raw_mean * admissibility_v2
        rows.append(
            {
                "world_seed": world.seed,
                "coarse_name": coarse_name,
                "noise_slip_prob": world.noise_slip_prob,
                "rigid_mode": world.rigid_mode,
                "perturbations": ";".join(world.perturbations),
                "I_mean": raw_mean,
                "I_max": raw_max,
                "admissibility_v2": admissibility_v2,
                "certified_I_v2": certified_v2,
                "compression_gate": comp_gate,
                "fiber_quality": fiber_quality,
                "viability_purity": viability_purity,
                "transition_consistency": transition_consistency,
                "rank_stability": rank_stability,
                "nontriviality_score": nontriviality_score,
                "num_macro_labels": num_macro,
                "mean_fiber_size": mean_fiber_size,
                "singleton_fraction": singleton_fraction,
                "truncation_fraction": trunc_count / max(total_cases, 1),
            }
        )
    rows.extend(hash_best_rows)
    return rows


def worker_job(seed: int):
    world = perturb_world(seed)
    rows = compute_world_metrics(world)
    return {"seed": seed, "rows": rows, "world": world}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in keys})


def rank_correlation(order_a: list[str], order_b: list[str]) -> float:
    common = [x for x in order_a if x in order_b]
    if len(common) < 2:
        return 0.0
    ra = {name: i + 1 for i, name in enumerate(order_a)}
    rb = {name: i + 1 for i, name in enumerate(order_b)}
    xs = [ra[n] for n in common]
    ys = [rb[n] for n in common]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / max(dx * dy, 1e-9)


def main() -> None:
    results_dir = Path("omega_probe_04_perturbation_audit_results")
    results_dir.mkdir(exist_ok=True)

    requested = N_PERTURB_WORLDS
    completed_worlds = []
    all_rows = []
    status = status_code()

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {}
        for seed in range(requested):
            if should_abort_now() or not should_continue_block():
                break
            fut = pool.submit(worker_job, seed)
            futures[fut] = seed

        while futures:
            done = next(as_completed(list(futures.keys())))
            seed = futures.pop(done)
            if should_abort_now():
                status = "PARTIAL_EXIT_HARD_LIMIT"
                break
            try:
                result = done.result()
                completed_worlds.append(seed)
                all_rows.extend(result["rows"])
                write_csv(results_dir / "perturbation_world_results.csv", all_rows)
            except Exception as exc:
                status = "ERROR"
                all_rows.append({"world_seed": seed, "error": str(exc)})
                break

            if len(completed_worlds) == requested and should_continue_block() and requested < N_PERTURB_WORLDS_MAX:
                extension = min(EXTENSION_WORLDS := 40, N_PERTURB_WORLDS_MAX - requested)
                for seed in range(requested, requested + extension):
                    if should_abort_now() or not should_continue_block():
                        break
                    fut = pool.submit(worker_job, seed)
                    futures[fut] = seed
                requested += extension

            if not should_continue_block() and status == "COMPLETE":
                status = "PARTIAL_EXIT_SOFT_LIMIT"
                break

    if status == "COMPLETE" and len(completed_worlds) < requested:
        status = "PARTIAL_EXIT_SOFT_LIMIT"

    completed_rows = [r for r in all_rows if "error" not in r and r.get("coarse_name") not in {None, "best_of_10_hashes_per_world"}]
    adaptive_rows = [r for r in all_rows if r.get("coarse_name") == "best_of_10_hashes_per_world"]

    by_coarse: dict[str, list[dict]] = defaultdict(list)
    for row in completed_rows:
        by_coarse[row["coarse_name"]].append(row)

    summary_rows = []
    for coarse_name in COARSE_NAMES:
        rows = by_coarse.get(coarse_name, [])
        if not rows:
            continue
        mean_cert = sum(r["certified_I_v2"] for r in rows) / len(rows)
        std_cert = math.sqrt(sum((r["certified_I_v2"] - mean_cert) ** 2 for r in rows) / len(rows))
        perturb_stability = mean_cert / (mean_cert + std_cert + 1e-9)
        cert_v3 = mean_cert * perturb_stability
        mean_adm = sum(r["admissibility_v2"] for r in rows) / len(rows)
        mean_raw = sum(r["I_mean"] for r in rows) / len(rows)
        trunc_frac = sum(r.get("truncation_fraction", 0.0) for r in rows) / len(rows)
        summary_rows.append(
            {
                "coarse_name": coarse_name,
                "mean_cert_v2": mean_cert,
                "std_cert_v2": std_cert,
                "perturb_stability": perturb_stability,
                "certified_I_v3": cert_v3,
                "mean_admiss": mean_adm,
                "mean_raw_I": mean_raw,
                "trunc_frac": trunc_frac,
                "num_worlds": len(rows),
            }
        )

    summary_rows = sorted(summary_rows, key=lambda r: r["certified_I_v3"], reverse=True)

    world_orders = []
    for seed in completed_worlds:
        wrows = [r for r in completed_rows if r["world_seed"] == seed]
        if not wrows:
            continue
        order = sorted(wrows, key=lambda r: r["certified_I_v2"], reverse=True)
        world_orders.append([r["coarse_name"] for r in order])

    pairwise_rank_corrs = []
    for a, b in zip(world_orders, world_orders[1:]):
        pairwise_rank_corrs.append(rank_correlation(a, b))
    rank_stability_across_worlds = sum(pairwise_rank_corrs) / max(len(pairwise_rank_corrs), 1) if pairwise_rank_corrs else 0.0

    mean_cert_by_coarse = {r["coarse_name"]: r["mean_cert_v2"] for r in summary_rows}
    perturb_stability_by_coarse = {r["coarse_name"]: r["perturb_stability"] for r in summary_rows}
    cert_v3_by_coarse = {r["coarse_name"]: r["certified_I_v3"] for r in summary_rows}

    good_gate = mean_cert_by_coarse.get("viability_signature", 0.0) > mean_cert_by_coarse.get("hash_k34_s1206", 0.0) or mean_cert_by_coarse.get("region", 0.0) > mean_cert_by_coarse.get("hash_k34_s1206", 0.0)
    hash_strong = mean_cert_by_coarse.get("hash_k34_s1206", 0.0) >= max(mean_cert_by_coarse.get("region", 0.0), mean_cert_by_coarse.get("viability_signature", 0.0))
    metric_gameable = max(mean_cert_by_coarse.get("random_5_fixed", 0.0), mean_cert_by_coarse.get("checkerboard", 0.0), mean_cert_by_coarse.get("trap_mixing_adversarial", 0.0)) > max(mean_cert_by_coarse.get("region", 0.0), mean_cert_by_coarse.get("viability_signature", 0.0))
    estimator_warning = any(r["trunc_frac"] > 0.25 for r in summary_rows)

    write_csv(results_dir / "perturbation_world_results.csv", completed_rows + adaptive_rows)
    write_csv(results_dir / "coarse_graining_summary.csv", summary_rows)

    summary = {
        "runtime_status": status,
        "requested_worlds": requested,
        "completed_worlds": len(completed_worlds),
        "workers": WORKERS,
        "truncation_fraction": sum(r.get("truncation_fraction", 0.0) for r in completed_rows) / max(len(completed_rows), 1),
        "rank_stability_across_worlds": rank_stability_across_worlds,
        "good_generalization_gate_ok": good_gate,
        "hash_still_strong": hash_strong,
        "metric_still_gameable": metric_gameable,
        "estimator_warning": estimator_warning,
        "top_by_mean_cert_v2": summary_rows[:3],
        "top_by_cert_v3": summary_rows[:3],
        "hash_audit": {
            "mean_cert_v2": mean_cert_by_coarse.get("hash_k34_s1206", 0.0),
            "perturb_stability": perturb_stability_by_coarse.get("hash_k34_s1206", 0.0),
            "cert_v3": cert_v3_by_coarse.get("hash_k34_s1206", 0.0),
        },
        "region": {
            "cert_v3": cert_v3_by_coarse.get("region", 0.0),
            "mean_cert_v2": mean_cert_by_coarse.get("region", 0.0),
        },
        "viability_signature": {
            "cert_v3": cert_v3_by_coarse.get("viability_signature", 0.0),
            "mean_cert_v2": mean_cert_by_coarse.get("viability_signature", 0.0),
        },
        "adaptive_control_rows": len(adaptive_rows),
    }
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if plt is not None and not should_abort_now():
        xs = [r["mean_cert_v2"] for r in summary_rows]
        ys = [r["perturb_stability"] for r in summary_rows]
        labels = [r["coarse_name"] for r in summary_rows]
        plt.figure(figsize=(8, 5.5))
        for x, y, label in zip(xs, ys, labels):
            plt.scatter([x], [y], s=60)
            plt.text(x + 0.01, y + 0.01, label, fontsize=8)
        plt.xlabel("mean certified_I_v2")
        plt.ylabel("perturb_stability")
        plt.tight_layout()
        plt.savefig(results_dir / "mean_cert_v2_vs_stability.png", dpi=140)
        plt.close()

        plt.figure(figsize=(8, 5.5))
        order = sorted(summary_rows, key=lambda r: r["certified_I_v3"], reverse=True)
        plt.bar([r["coarse_name"] for r in order], [r["certified_I_v3"] for r in order])
        plt.xticks(rotation=25, ha="right")
        plt.ylabel("certified_I_v3")
        plt.tight_layout()
        plt.savefig(results_dir / "cert_v3_bar.png", dpi=140)
        plt.close()

        plt.figure(figsize=(8, 5.5))
        by_world = defaultdict(list)
        for row in completed_rows:
            by_world[row["world_seed"]].append(row)
        for coarse_name in ["region", "viability_signature", "hash_k34_s1206"]:
            pts = []
            for seed, rows in by_world.items():
                match = next((r for r in rows if r["coarse_name"] == coarse_name), None)
                if match:
                    pts.append((seed, match["certified_I_v2"]))
            if pts:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                plt.plot(xs, ys, marker="o", label=coarse_name)
        plt.xlabel("world_seed")
        plt.ylabel("certified_I_v2")
        plt.legend()
        plt.tight_layout()
        plt.savefig(results_dir / "cert_v2_by_world.png", dpi=140)
        plt.close()

    print("\nOMEGA PROBE 04: HELDOUT PERTURBATION AUDIT")
    print("\nRuntime status:")
    print(f"- {status}")
    print("\nWorlds completed:")
    print(f"- {len(completed_worlds)} / {requested}")
    print("\nTruncation:")
    print(f"- truncation_fraction = {summary['truncation_fraction']:.3f}")
    print("\nTop by mean certified_I_v2:")
    for i, row in enumerate(summary_rows[:3], 1):
        print(f"{i}. {row['coarse_name']} ({row['mean_cert_v2']:.3f})")
    print("\nTop by certified_I_v3:")
    for i, row in enumerate(summary_rows[:3], 1):
        print(f"{i}. {row['coarse_name']} ({row['certified_I_v3']:.3f})")
    print("\nHash audit:")
    print(f"- hash_k34_s1206 mean_cert_v2 = {summary['hash_audit']['mean_cert_v2']:.3f}")
    print(f"- hash_k34_s1206 perturb_stability = {summary['hash_audit']['perturb_stability']:.3f}")
    print(f"- hash_k34_s1206 cert_v3 = {summary['hash_audit']['cert_v3']:.3f}")
    print("\nMeaningful coarse-grainings:")
    print(f"- region cert_v3 = {summary['region']['cert_v3']:.3f}")
    print(f"- viability_signature cert_v3 = {summary['viability_signature']['cert_v3']:.3f}")
    print("\nFlags:")
    print(f"- GOOD_GENERALIZATION_GATE_OK: {str(good_gate).lower()}")
    print(f"- HASH_STILL_STRONG: {str(hash_strong).lower()}")
    print(f"- METRIC_STILL_GAMEABLE: {str(metric_gameable).lower()}")
    print(f"- ESTIMATOR_WARNING: {str(estimator_warning).lower()}")
    print("\nInterpretation:")
    print("- Did the adversarial hash generalize?")
    print("- Did meaningful coarse-grainings survive perturbation?")
    print("- Is v3 meaningfully different from v2?")
    print("- Should we inspect the hash or proceed to small world-family sweep?")
    print(f"\nResults: {results_dir.resolve()}")


if __name__ == "__main__":
    main()
