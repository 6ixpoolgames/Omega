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

try:
    import numpy as np
except Exception:  # pragma: no cover - numpy is expected but keep a fallback
    np = None

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
except Exception:  # pragma: no cover - optional dependency
    KMeans = None
    StandardScaler = None


SOFT_LIMIT_SECONDS = 1800
HARD_LIMIT_SECONDS = 2700
WORKERS = int(os.environ.get("OMEGA_WORKERS", 18))
WORLDS_PER_FAMILY = int(os.environ.get("OMEGA_WORLDS_PER_FAMILY", 50))
WORLDS_PER_FAMILY_MAX = 60
GRID_SIZES = [7, 9]
MAX_TRAJ_PER_STATE = 50000
PREDICTIVE_HORIZON = 4
TRAIN_FRACTION = 0.6
TEST_FRACTION = 0.4
MC_TRAJ_SAMPLES = 5000
MC_REPEATS = 3
ENERGY_CAP = 6
INITIAL_ENERGY_DEFAULT = 4
REPAIR_HORIZON = 3
HORIZONS = [2, 3, 4, 5, 6]
BEHAVIORAL_KS = [5, 8, 13, 21]
PREDICTIVE_KS = [5, 8, 13, 21]
RANDOM_K = 13
STATE_SAMPLE_ROLLOUTS = 6
STATE_FEATURE_HORIZONS = [1, 2, 3, 4]
ACTIONS = ["U", "D", "L", "R", "WAIT"]

BASE_GRID_9 = [
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

BASE_GRID_7 = [
    "OOOSSSS",
    "OOLBBCC",
    "OOLBBCC",
    "DDL.BCC",
    "DDL.RRR",
    "TTT.AAA",
    "TTT.AAA",
]

START_TIME = time.time()
RANDOM_LABELS_9 = { (x, y): f"q{random.Random(7).randrange(13)}" for y in range(9) for x in range(9) }


@dataclass
class World:
    family: str
    variant: str
    seed: int
    grid: list[str]
    size: int
    noise_slip_prob: float
    energy_cap: int
    initial_energy: int
    move_cost: int
    rough_cost: int
    resource_bonus: int
    wait_cost: int
    rigid_mode: str
    cost_budget_scale: float
    pair_id: int | None = None
    notes: list[str] | None = None


def status_code() -> str:
    elapsed = time.time() - START_TIME
    if elapsed > HARD_LIMIT_SECONDS:
        return "PARTIAL_EXIT_HARD_LIMIT"
    if elapsed > SOFT_LIMIT_SECONDS:
        return "PARTIAL_EXIT_SOFT_LIMIT"
    return "COMPLETE"


def should_continue_block() -> bool:
    return time.time() - START_TIME < SOFT_LIMIT_SECONDS


def should_abort_now() -> bool:
    return time.time() - START_TIME > HARD_LIMIT_SECONDS


def gmean(values: list[float]) -> float:
    vals = [max(0.0, v) for v in values if v is not None]
    vals = [v for v in vals if v > 0]
    if not vals:
        return 0.0
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    out = 0.0
    for count in counter.values():
        p = count / total
        out -= p * math.log(p)
    return out


def normalize_columns(mat):
    if np is None:
        return mat
    arr = np.asarray(mat, dtype=float)
    mean = arr.mean(axis=0)
    std = arr.std(axis=0)
    std[std == 0] = 1.0
    return (arr - mean) / std


def region_xy(grid: list[str], x: int, y: int) -> str:
    if x < 0 or y < 0 or x >= len(grid[0]) or y >= len(grid):
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


def grid_copy(rows: list[str]) -> list[list[str]]:
    return [list(r) for r in rows]


def rows_from_grid(grid: list[list[str]]) -> list[str]:
    return ["".join(r) for r in grid]


def reflect_h(grid: list[list[str]]) -> list[list[str]]:
    return [list(reversed(r)) for r in grid]


def rotate_180(grid: list[list[str]]) -> list[list[str]]:
    return [list(reversed(r)) for r in grid[::-1]]


def find_cells(grid: list[str], label: str) -> list[tuple[int, int]]:
    out = []
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == label:
                out.append((x, y))
    return out


def select_start(grid: list[str], label: str) -> tuple[int, int, int] | None:
    cells = find_cells(grid, label)
    if cells:
        x, y = cells[0]
        return x, y, INITIAL_ENERGY_DEFAULT
    if label == "near_trap":
        traps = find_cells(grid, "T")
        for tx, ty in traps:
            for nx, ny in [(tx - 1, ty), (tx + 1, ty), (tx, ty - 1), (tx, ty + 1)]:
                if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != "T":
                    return nx, ny, INITIAL_ENERGY_DEFAULT
    return None


def base_world(seed: int, family: str, variant: str, size: int = 9) -> World:
    grid = BASE_GRID_9 if size == 9 else BASE_GRID_7
    return World(
        family=family,
        variant=variant,
        seed=seed,
        grid=grid[:],
        size=size,
        noise_slip_prob=0.2,
        energy_cap=ENERGY_CAP,
        initial_energy=INITIAL_ENERGY_DEFAULT,
        move_cost=1,
        rough_cost=2,
        resource_bonus=2,
        wait_cost=0,
        rigid_mode="sticky",
        cost_budget_scale=1.0,
        pair_id=None,
        notes=[],
    )


def generate_family_world(family: str, seed: int, variant: str, pair_id: int | None = None, size: int = 9) -> World:
    w = base_world(seed, family, variant, size=size)
    w.pair_id = pair_id
    rng = random.Random(seed * 1543 + len(family) * 97 + (0 if variant == "a" else 1))
    notes: list[str] = []

    if family == "A":
        grid = grid_copy(BASE_GRID_9 if size == 9 else BASE_GRID_7)
        corridor = [(2, 2), (3, 2), (4, 2), (4, 3), (4, 4), (3, 4), (2, 4)]
        if variant == "reversible":
            for x, y in corridor:
                grid[y][x] = "L"
            grid[6][2] = "L"
            grid[6][3] = "L"
            w.rigid_mode = "sticky"
        else:
            for x, y in corridor:
                grid[y][x] = "D"
            grid[6][2] = "T"
            grid[6][3] = "T"
            grid[6][4] = "T"
            w.rigid_mode = "bounded"
        w.grid = rows_from_grid(grid)
        notes.append("branch_pair")

    elif family == "B":
        grid = grid_copy(BASE_GRID_9 if size == 9 else BASE_GRID_7)
        if variant == "lure":
            for x, y in [(4, 1), (5, 1), (4, 2), (5, 2)]:
                grid[y][x] = "S"
            grid[3][5] = "T"
            grid[3][6] = "T"
            grid[4][5] = "D"
            grid[4][6] = "D"
            grid[5][5] = "D"
            grid[5][6] = "D"
            w.noise_slip_prob = 0.35
        else:
            for x, y in [(4, 1), (5, 1), (4, 2), (5, 2)]:
                grid[y][x] = "C"
            grid[3][5] = "C"
            grid[3][6] = "C"
            grid[4][5] = "L"
            grid[4][6] = "L"
            grid[5][5] = "L"
            grid[5][6] = "L"
            w.noise_slip_prob = 0.15
        w.grid = rows_from_grid(grid)
        notes.append("lure_pair")

    elif family == "C":
        grid = grid_copy(BASE_GRID_9 if size == 9 else BASE_GRID_7)
        # Resource budget stress.
        for y in range(size):
            for x in range(size):
                if (x + y + seed) % 4 == 0 and grid[y][x] in {"O", "."}:
                    grid[y][x] = "S"
                if (x * 2 + y + seed) % 11 == 0:
                    grid[y][x] = "C"
        if size == 9:
            coords = [(6, 2), (7, 2), (6, 3), (7, 3), (6, 4), (7, 4)]
        else:
            coords = [(3, 1), (4, 1), (3, 2), (4, 2), (3, 3), (4, 3)]
        for x, y in coords:
            grid[y][x] = "C"
        w.grid = rows_from_grid(grid)
        w.noise_slip_prob = 0.1 + 0.05 * (seed % 3)
        w.energy_cap = 6
        w.initial_energy = 4 + (seed % 2)
        w.move_cost = 1
        w.rough_cost = 2 + (seed % 2)
        w.resource_bonus = 2
        w.wait_cost = 0 if seed % 3 else 1
        w.cost_budget_scale = 1.5
        notes.append("budget")

    elif family == "D":
        grid = grid_copy(BASE_GRID_9 if size == 9 else BASE_GRID_7)
        # Interleaved viable and nonviable cells that look macro-similar.
        for y in range(size):
            for x in range(size):
                if (x + 2 * y + seed) % 3 == 0:
                    grid[y][x] = "C"
                elif (x + y + seed) % 4 == 0:
                    grid[y][x] = "S"
                elif (x * y + seed) % 7 == 0:
                    grid[y][x] = "T"
        if size == 9:
            fixed = [(2, 2, "C"), (2, 3, "S"), (3, 2, "S"), (3, 3, "T"), (5, 5, "C"), (5, 6, "S")]
        else:
            fixed = [(1, 1, "C"), (1, 2, "S"), (2, 1, "S"), (2, 2, "T"), (4, 4, "C"), (4, 5, "S")]
        for x, y, lab in fixed:
            grid[y][x] = lab
        w.grid = rows_from_grid(grid)
        w.energy_cap = 6
        w.initial_energy = 3 + (seed % 3)
        w.move_cost = 1
        w.rough_cost = 2
        w.resource_bonus = 2
        w.wait_cost = 1 if seed % 2 == 0 else 0
        w.noise_slip_prob = 0.2 + 0.05 * (seed % 4)
        w.cost_budget_scale = 1.0
        notes.append("hidden_fake_viability")

    # Small generic perturbations so worlds aren't all identical.
    if rng.random() < 0.2:
        grid = grid_copy(w.grid)
        if rng.random() < 0.5:
            grid = reflect_h(grid)
            notes.append("reflect")
        else:
            grid = rotate_180(grid)
            notes.append("rotate180")
        w.grid = rows_from_grid(grid)

    w.notes = notes
    return w


def build_worlds() -> list[World]:
    worlds: list[World] = []
    # Families A/B use paired variants.
    for pair_id in range(WORLDS_PER_FAMILY // 2):
        seed = pair_id
        worlds.append(generate_family_world("A", seed, "reversible", pair_id, size=9 if pair_id % 2 == 0 else 7))
        worlds.append(generate_family_world("A", seed, "irreversible", pair_id, size=9 if pair_id % 2 == 0 else 7))
    for pair_id in range(WORLDS_PER_FAMILY // 2):
        seed = 100 + pair_id
        worlds.append(generate_family_world("B", seed, "lure", pair_id, size=9 if pair_id % 2 == 0 else 7))
        worlds.append(generate_family_world("B", seed, "control", pair_id, size=9 if pair_id % 2 == 0 else 7))
    for seed in range(WORLDS_PER_FAMILY):
        worlds.append(generate_family_world("C", 200 + seed, "budget", seed, size=9 if seed % 2 == 0 else 7))
    for seed in range(WORLDS_PER_FAMILY):
        worlds.append(generate_family_world("D", 300 + seed, "hidden", seed, size=9 if seed % 2 == 0 else 7))
    return worlds


def state_space(world: World) -> list[tuple[int, int, int]]:
    return [(x, y, e) for y in range(world.size) for x in range(world.size) for e in range(world.energy_cap + 1)]


def rng_from_state(state: tuple[int, int, int], seed: int) -> random.Random:
    return random.Random(seed * 7919 + state[0] * 97 + state[1] * 193 + state[2] * 389)


def apply_rules(world: World, x: int, y: int, energy: int, action: str) -> tuple[int, int, int]:
    grid = world.grid
    current = region_xy(grid, x, y)
    nx, ny = move_xy(x, y, action)
    if region_xy(grid, nx, ny) == "#":
        nx, ny = x, y
    nxt = region_xy(grid, nx, ny)

    if current == "T" or nxt == "T":
        return nx, ny, 0

    if current in {"R", "A"}:
        if world.rigid_mode == "bounded" and action != "WAIT":
            return x, y, max(1, energy - 1)
        return x, y, max(1, energy)

    if current == "S":
        cost = world.rough_cost
    elif current == "D":
        cost = world.rough_cost + 1
    elif action == "WAIT":
        cost = world.wait_cost
    else:
        cost = world.move_cost

    new_energy = max(0, energy - cost)
    if nxt == "C":
        new_energy = min(world.energy_cap, new_energy + world.resource_bonus)
    if nxt in {"R", "A"}:
        new_energy = max(1, new_energy)
    return nx, ny, new_energy


def transition(world: World, state: tuple[int, int, int], action: str) -> list[tuple[tuple[int, int, int], float]]:
    x, y, energy = state
    current = region_xy(world.grid, x, y)
    if current in {"R", "A", "T"}:
        return [(apply_rules(world, x, y, energy, action), 1.0)]

    candidate_actions = [action]
    if current == "S" and rng_from_state(state, world.seed).random() < world.noise_slip_prob:
        candidate_actions = ACTIONS
    elif current == "S":
        if action in {"U", "D"}:
            candidate_actions = [action, "L", "R", "WAIT"]
        elif action in {"L", "R"}:
            candidate_actions = [action, "U", "D", "WAIT"]
    elif current == "D" and action != "WAIT":
        candidate_actions = [action, "WAIT"]
    elif current == "B" and action != "WAIT":
        candidate_actions = [action, "WAIT"]

    prob = 1.0 / len(candidate_actions)
    return [(apply_rules(world, x, y, energy, a), prob) for a in candidate_actions]


def viable_transition(world: World, next_state: tuple[int, int, int]) -> bool:
    return next_state[2] > 0 and region_xy(world.grid, next_state[0], next_state[1]) != "T"


def enumerate_trajectories(world: World, start_state: tuple[int, int, int], horizon: int):
    trajectories = [((start_state,), True, 0)]
    truncated = False
    for _ in range(horizon):
        new_trajs = []
        for states, viable, cost in trajectories:
            if should_abort_now() or len(new_trajs) >= MAX_TRAJ_PER_STATE:
                truncated = truncated or len(new_trajs) >= MAX_TRAJ_PER_STATE
                break
            state = states[-1]
            for action in ACTIONS:
                for next_state, _ in transition(world, state, action):
                    ncost = cost + (world.wait_cost if action == "WAIT" else world.move_cost)
                    new_viable = viable and viable_transition(world, next_state)
                    new_trajs.append((states + (next_state,), new_viable, ncost))
                    if len(new_trajs) >= MAX_TRAJ_PER_STATE:
                        truncated = True
                        break
                if len(new_trajs) >= MAX_TRAJ_PER_STATE:
                    break
        trajectories = new_trajs[:MAX_TRAJ_PER_STATE]
        if should_abort_now():
            truncated = True
            break
    return trajectories, truncated


def exists_viable_future(world: World, state: tuple[int, int, int], depth: int, memo: dict) -> bool:
    key = (state, depth)
    if key in memo:
        return memo[key]
    if depth <= 0:
        memo[key] = viable_transition(world, state)
        return memo[key]
    for action in ACTIONS:
        for nxt, _ in transition(world, state, action):
            if viable_transition(world, nxt) and exists_viable_future(world, nxt, depth - 1, memo):
                memo[key] = True
                return True
    memo[key] = False
    return False


def perturb_state_toward_trap(world: World, state: tuple[int, int, int]) -> tuple[int, int, int]:
    x, y, e = state
    traps = find_cells(world.grid, "T")
    if traps:
        tx, ty = min(traps, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
        dx = 1 if tx > x else -1 if tx < x else 0
        dy = 1 if ty > y else -1 if ty < y else 0
        nx, ny = max(0, min(world.size - 1, x + dx)), max(0, min(world.size - 1, y + dy))
    else:
        nx, ny = x, y
    return nx, ny, max(0, e - 1)


def recoverable_micro(world: World, state: tuple[int, int, int], memo: dict) -> bool:
    perturbed_variants = [
        perturb_state_toward_trap(world, state),
        (state[0], state[1], max(0, state[2] - 1)),
    ]
    for p in perturbed_variants:
        if exists_viable_future(world, p, REPAIR_HORIZON, memo):
            return True
    return False


def one_step_viable_fraction(world: World, state: tuple[int, int, int]) -> float:
    total = 0.0
    good = 0.0
    for action in ACTIONS:
        for nxt, prob in transition(world, state, action):
            total += prob
            if viable_transition(world, nxt):
                good += prob
    return good / max(total, 1e-9)


def sample_rollouts(world: World, start_state: tuple[int, int, int], horizon: int, samples: int, seed: int):
    rng = random.Random(seed)
    rollouts = []
    for _ in range(samples):
        state = start_state
        path = [state]
        viable = viable_transition(world, state)
        cost = 0
        trap_hit = region_xy(world.grid, state[0], state[1]) == "T"
        resource_hit = region_xy(world.grid, state[0], state[1]) == "C"
        for _ in range(horizon):
            action = rng.choice(ACTIONS)
            outs = transition(world, state, action)
            roll = rng.random()
            acc = 0.0
            nxt = outs[-1][0]
            for candidate, prob in outs:
                acc += prob
                if roll <= acc:
                    nxt = candidate
                    break
            cost += world.wait_cost if action == "WAIT" else world.move_cost
            trap_hit = trap_hit or region_xy(world.grid, nxt[0], nxt[1]) == "T"
            resource_hit = resource_hit or region_xy(world.grid, nxt[0], nxt[1]) == "C" or nxt[2] > state[2]
            viable = viable and viable_transition(world, nxt)
            path.append(nxt)
            state = nxt
        rollouts.append((tuple(path), viable, cost, trap_hit, resource_hit))
    return rollouts


def label_of_state(world: World, state: tuple[int, int, int], coarse_name: str, coarse_fn):
    if coarse_name == "region":
        return region_xy(world.grid, state[0], state[1])
    if coarse_name == "identity":
        return state
    if coarse_name == "all_one":
        return "all_one"
    if coarse_name == "checkerboard":
        return (state[0] + state[1]) % 2
    if coarse_name == "random_k":
        return random_label_map(world)[(state[0], state[1], state[2])]
    if coarse_name.startswith("behavioral_quotient_"):
        return coarse_fn(state)
    return coarse_fn(state)


def random_label_map(world: World) -> dict[tuple[int, int, int], int]:
    rng = random.Random(world.seed * 101 + 13)
    k = RANDOM_K
    return {(x, y, e): rng.randrange(k) for x, y, e in state_space(world)}


def coarse_viability_signature_factory(world: World):
    memo = {}
    def fn(state):
        x, y, e = state
        energy_bin = "e_low" if e <= 1 else "e_med" if e <= 3 else "e_high"
        trap_cells = find_cells(world.grid, "T")
        if trap_cells:
            dist = min(abs(x - tx) + abs(y - ty) for tx, ty in trap_cells)
            trap_bin = "near" if dist <= 2 else "far"
        else:
            trap_bin = "far"
        branching = 0
        for action in ACTIONS:
            for nxt, _ in transition(world, state, action):
                if viable_transition(world, nxt):
                    branching += 1
        branch_bin = "low" if branching <= 2 else "med" if branching <= 6 else "high"
        resource_cells = find_cells(world.grid, "C")
        if resource_cells:
            dist_r = min(abs(x - rx) + abs(y - ry) for rx, ry in resource_cells)
            res_bin = "near" if dist_r <= 2 else "far"
        else:
            res_bin = "far"
        recover_bin = "recoverable" if recoverable_micro(world, state, memo) else "fragile"
        return energy_bin, trap_bin, branch_bin, res_bin, recover_bin
    return fn


def coarse_hash_fixed(state: tuple[int, int, int]) -> int:
    x, y, e = state
    return (1 * x + 5 * y + 7 * e) % 34


def coarse_checkerboard(state: tuple[int, int, int]) -> int:
    return (state[0] + state[1]) % 2


def coarse_all_one(state: tuple[int, int, int]) -> int:
    return 0


def coarse_trap_mixing(world: World):
    def fn(state):
        x, y, _ = state
        r = region_xy(world.grid, x, y)
        if r == "T" or r == "D":
            return f"m{(x + y) % 2}"
        if r in {"O", ".", "S"}:
            return f"m{(2 * x + y) % 3}"
        return f"m{(x + 2 * y) % 4}"
    return fn


def make_random_partition(world: World, k: int):
    rng = random.Random(world.seed * 17 + k)
    mapping = {state: rng.randrange(k) for state in state_space(world)}
    return lambda state: mapping[state]


def build_behavioral_features(world: World):
    memo_future = {}
    features = {}
    for state in state_space(world):
        vec = []
        for horizon in STATE_FEATURE_HORIZONS:
            rollouts = sample_rollouts(world, state, horizon, STATE_SAMPLE_ROLLOUTS, seed=world.seed + horizon * 31 + state[0] * 7 + state[1] * 11 + state[2] * 13)
            viable_flags = [1.0 if r[1] else 0.0 for r in rollouts]
            terminal_positions = [(r[0][-1][0], r[0][-1][1]) for r in rollouts]
            trap_flags = [1.0 if r[3] else 0.0 for r in rollouts]
            resource_flags = [1.0 if r[4] else 0.0 for r in rollouts]
            position_counts = Counter(terminal_positions)
            vec.append(sum(viable_flags) / len(viable_flags))
            vec.append(entropy(position_counts))
            vec.append(sum(trap_flags) / len(trap_flags))
            vec.append(sum(resource_flags) / len(resource_flags))
        vec.append(one_step_viable_fraction(world, state))
        local_dist = Counter()
        for action in ACTIONS:
            for nxt, _ in transition(world, state, action):
                local_dist[(nxt[0], nxt[1], nxt[2])] += 1
        vec.append(entropy(local_dist))
        vec.append(1.0 if recoverable_micro(world, state, memo_future) else 0.0)
        features[state] = vec
    return features


def behavioral_quotient_labels(world: World, k: int, state_features: dict[tuple[int, int, int], list[float]]):
    states = list(state_features.keys())
    X = [state_features[s] for s in states]
    Xn = normalize_columns(X)
    if np is None:
        # simple numpy-less fallback
        rng = random.Random(world.seed + k * 19)
        centroids = [Xn[rng.randrange(len(Xn))] for _ in range(k)]
        labels = [0] * len(Xn)
        for _ in range(20):
            for i, row in enumerate(Xn):
                dists = [sum((a - b) ** 2 for a, b in zip(row, c)) for c in centroids]
                labels[i] = dists.index(min(dists))
            new_centroids = []
            for j in range(k):
                group = [Xn[i] for i, lab in enumerate(labels) if lab == j]
                if not group:
                    new_centroids.append(Xn[rng.randrange(len(Xn))])
                else:
                    new_centroids.append([sum(vals) / len(vals) for vals in zip(*group)])
            centroids = new_centroids
        return {states[i]: int(labels[i]) for i in range(len(states))}
    arr = np.asarray(Xn, dtype=float)
    if KMeans is not None:
        model = KMeans(n_clusters=k, random_state=world.seed + k, n_init=5)
        labels = model.fit_predict(arr)
    else:
        rng = np.random.default_rng(world.seed + k)
        centroids = arr[rng.choice(len(arr), size=k, replace=False)]
        labels = np.zeros(len(arr), dtype=int)
        for _ in range(20):
            dists = ((arr[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
            labels = dists.argmin(axis=1)
            new_centroids = []
            for j in range(k):
                group = arr[labels == j]
                if len(group) == 0:
                    new_centroids.append(arr[rng.integers(0, len(arr))])
                else:
                    new_centroids.append(group.mean(axis=0))
            centroids = np.asarray(new_centroids)
    return {states[i]: int(labels[i]) for i in range(len(states))}


def trajectory_label(world: World, states: tuple[tuple[int, int, int], ...], coarse_name: str, coarse_fn, bx_map=None):
    if coarse_name == "endpoint_only":
        return region_xy(world.grid, states[-1][0], states[-1][1])
    if coarse_name == "random_k":
        return random_label_map(world)[states[-1]]
    if coarse_name.startswith("behavioral_quotient_"):
        return bx_map[states[-1]]
    return tuple(label_of_state(world, st, coarse_name, coarse_fn) for st in states)


def compute_coarse_metrics(world: World, cache: dict, coarse_name: str, coarse_fn, bx_map=None):
    rows = []
    all_truncated = []
    for start_name, start_state in cache["starts"].items():
        for horizon in HORIZONS:
            trajectories, truncated = cache["traj"][(start_name, horizon)]
            viable = [tr for tr in trajectories if tr[1]]
            classes = Counter()
            for states, _, _ in viable:
                classes[trajectory_label(world, states, coarse_name, coarse_fn, bx_map)] += 1
            omega = entropy(classes)
            rows.append(
                {
                    "world_seed": world.seed,
                    "family": world.family,
                    "variant": world.variant,
                    "pair_id": world.pair_id if world.pair_id is not None else "",
                    "coarse_name": coarse_name,
                    "start": start_name,
                    "T": horizon,
                    "I": omega,
                    "N_eff": math.exp(omega),
                    "raw_count": len(trajectories),
                    "viable_count": len(viable),
                    "truncated": int(truncated),
                }
            )
            all_truncated.append(int(truncated))
    return rows, all_truncated


def viability_sets(world: World, cache: dict, coarse_name: str, coarse_fn, bx_map=None):
    state_viable = {}
    memo = {}
    for state in state_space(world):
        state_viable[state] = exists_viable_future(world, state, 2, memo)
    label_members = defaultdict(list)
    for state in state_space(world):
        if coarse_name == "region":
            label = region_xy(world.grid, state[0], state[1])
        elif coarse_name == "random_k":
            label = random_label_map(world)[state]
        elif coarse_name.startswith("behavioral_quotient_"):
            label = bx_map[state]
        else:
            label = coarse_fn(state)
        label_members[label].append(state)
    label_viable = {label: any(state_viable[s] for s in states) for label, states in label_members.items()}
    label_recoverable = {}
    for label, states in label_members.items():
        vals = [1.0 if recoverable_micro(world, s, memo) else 0.0 for s in states]
        label_recoverable[label] = (sum(vals) / len(vals)) if vals else 0.0
    return state_viable, label_members, label_viable, label_recoverable


def compute_world_row(world: World, cache: dict, coarse_name: str, coarse_fn, bx_map=None):
    rows, truncs = compute_coarse_metrics(world, cache, coarse_name, coarse_fn, bx_map)
    I_vals = [r["I"] for r in rows]
    I_mean = sum(I_vals) / max(len(I_vals), 1)
    I_max = max(I_vals) if I_vals else 0.0

    state_viable, label_members, label_viable, label_recoverable = viability_sets(world, cache, coarse_name, coarse_fn, bx_map)
    num_macro = len(label_members)
    num_micro = len(state_space(world))
    compression_ratio = num_macro / max(num_micro, 1)
    singleton_fraction = sum(1 for states in label_members.values() if len(states) == 1) / max(num_macro, 1)
    label_entropy = entropy(Counter({label: len(states) for label, states in label_members.items()}))

    # Compression gate
    if compression_ratio <= 0.01 or compression_ratio >= 0.75:
        compression_gate = 0.0
    elif 0.05 <= compression_ratio <= 0.40:
        compression_gate = 1.0
    elif compression_ratio < 0.05:
        compression_gate = compression_ratio / 0.05
    else:
        compression_gate = (0.75 - compression_ratio) / (0.75 - 0.40)

    viable_states = [s for s, ok in state_viable.items() if ok]
    viable_with_label = sum(1 for s in viable_states if label_viable[next(label for label, states in label_members.items() if s in states)])
    viability_preservation_score = viable_with_label / max(len(viable_states), 1)

    mixed_labels = 0
    viable_fracs = []
    for label, states in label_members.items():
        if not states:
            continue
        vfrac = sum(1 for s in states if state_viable[s]) / len(states)
        viable_fracs.append(vfrac)
        if 0.0 < vfrac < 1.0:
            mixed_labels += 1
    mixed_viability_label_fraction = mixed_labels / max(len(label_members), 1)
    macro_viability_purity = sum(max(vf, 1.0 - vf) for vf in viable_fracs) / max(len(viable_fracs), 1)
    hidden_nonviability_rate = sum(1 for vf in viable_fracs if vf < 0.5) / max(len(viable_fracs), 1)
    fake_viability_rate = sum(1 for vf in viable_fracs if vf > 0.5) / max(len(viable_fracs), 1)

    recoverability_purity = sum(max(rv, 1.0 - rv) for rv in label_recoverable.values()) / max(len(label_recoverable), 1)
    recoverability_preservation_score = 1.0 / (1.0 + (1.0 - recoverability_purity))

    # Horizon coherence.
    start_values = defaultdict(list)
    for r in rows:
        start_values[r["start"]].append((r["T"], r["I"]))
    coherence_scores = []
    lure_flags = []
    for start_name, pairs in start_values.items():
        pairs = sorted(pairs)
        if not pairs:
            continue
        early = sum(v for t, v in pairs if t in {2, 3}) / max(sum(1 for t, v in pairs if t in {2, 3}), 1)
        late = sum(v for t, v in pairs if t in {5, 6}) / max(sum(1 for t, v in pairs if t in {5, 6}), 1)
        collapse = max(0.0, early - late)
        coherence_scores.append(1.0 / (1.0 + collapse))
        lure_flags.append(1 if early > 0.75 and late < 0.5 else 0)
    horizon_coherence_score = sum(coherence_scores) / max(len(coherence_scores), 1)
    fake_short_horizon_lure_detected = any(lure_flags)

    # Generic nondegeneracy.
    nondegeneracy_score = compression_gate * (1.0 - singleton_fraction) * min(1.0, I_mean / 1.0)

    # Family-specific metrics.
    scale_consistency_score = None
    room_purity = None
    sector_purity = None
    irreversibility_sensitivity = None
    bounded_cost_score = None
    cost_sustainment_ratio = None
    I_unconstrained = None
    I_cost_constrained = None

    if world.family == "C":
        room_map = {}
        sector_map = {}
        for y in range(world.size):
            for x in range(world.size):
                room_map[(x, y)] = f"r{x//3}{y//3}"
                sector_map[(x, y)] = f"s{y//3}"
        room_labels = defaultdict(list)
        sector_labels = defaultdict(list)
        for state in state_space(world):
            room_labels[room_map[(state[0], state[1])]].append(state)
            sector_labels[sector_map[(state[0], state[1])]].append(state)
        room_purity = sum(
            max(
                sum(1 for s in states if label_viable[next(label for label, mem in label_members.items() if s in mem)]) / len(states),
                1.0 - sum(1 for s in states if label_viable[next(label for label, mem in label_members.items() if s in mem)]) / len(states),
            )
            for states in room_labels.values()
        ) / max(len(room_labels), 1)
        sector_purity = sum(
            max(
                sum(1 for s in states if label_viable[next(label for label, mem in label_members.items() if s in mem)]) / len(states),
                1.0 - sum(1 for s in states if label_viable[next(label for label, mem in label_members.items() if s in mem)]) / len(states),
            )
            for states in sector_labels.values()
        ) / max(len(sector_labels), 1)
        micro_to_room_agreement = sum(1 for s in state_viable if state_viable[s] and label_viable[next(label for label, states in label_members.items() if s in states)]) / max(len(viable_states), 1)
        room_to_sector_agreement = (room_purity + sector_purity) / 2.0
        scale_consistency_score = (room_purity + sector_purity + micro_to_room_agreement + room_to_sector_agreement) / 4.0

    if world.family == "A":
        irreversibility_sensitivity = None  # filled in by pairing stage

    if world.family == "D":
        # Cost constrained I versus unconstrained I.
        Fmax = {T: 1.5 * T + 2 for T in HORIZONS}
        unconstrained_vals = []
        constrained_vals = []
        for r in rows:
            unconstrained_vals.append(r["I"])
            if r["T"] in Fmax:
                trajectories, _ = cache["traj"][(r["start"], r["T"])]
                viable = [tr for tr in trajectories if tr[1] and tr[2] <= Fmax[r["T"]]]
                classes = Counter()
                for states, _, _ in viable:
                    classes[trajectory_label(world, states, coarse_name, coarse_fn, bx_map)] += 1
                constrained_vals.append(entropy(classes))
        I_unconstrained = sum(unconstrained_vals) / max(len(unconstrained_vals), 1)
        I_cost_constrained = sum(constrained_vals) / max(len(constrained_vals), 1) if constrained_vals else 0.0
        bounded_cost_score = I_cost_constrained / max(I_unconstrained, 1e-9)
        cost_sustainment_ratio = bounded_cost_score

    applicable = [
        nondegeneracy_score,
        viability_preservation_score,
        macro_viability_purity,
        recoverability_preservation_score,
        horizon_coherence_score,
    ]
    if scale_consistency_score is not None:
        applicable.append(scale_consistency_score)
    if irreversibility_sensitivity is not None:
        applicable.append(max(0.0, irreversibility_sensitivity))
    if bounded_cost_score is not None:
        applicable.append(bounded_cost_score)
    omega_profile_score = gmean(applicable)

    return {
        "world_seed": world.seed,
        "family": world.family,
        "variant": world.variant,
        "pair_id": world.pair_id if world.pair_id is not None else "",
        "coarse_name": coarse_name,
        "I_mean": I_mean,
        "I_max": I_max,
        "N_eff_mean": math.exp(I_mean),
        "raw_I_nonzero": 1 if I_mean > 0 else 0,
        "compression_ratio": compression_ratio,
        "compression_gate": compression_gate,
        "singleton_fraction": singleton_fraction,
        "label_entropy": label_entropy,
        "viability_preservation_score": viability_preservation_score,
        "mixed_viability_label_fraction": mixed_viability_label_fraction,
        "macro_viability_purity": macro_viability_purity,
        "fake_viability_rate": fake_viability_rate,
        "hidden_nonviability_rate": hidden_nonviability_rate,
        "recoverability_preservation_score": recoverability_preservation_score,
        "recoverability_purity": recoverability_purity,
        "horizon_coherence_score": horizon_coherence_score,
        "fake_short_horizon_lure_detected": int(fake_short_horizon_lure_detected),
        "scale_consistency_score": scale_consistency_score if scale_consistency_score is not None else "",
        "room_purity": room_purity if room_purity is not None else "",
        "sector_purity": sector_purity if sector_purity is not None else "",
        "irreversibility_sensitivity": irreversibility_sensitivity if irreversibility_sensitivity is not None else "",
        "bounded_cost_score": bounded_cost_score if bounded_cost_score is not None else "",
        "I_unconstrained": I_unconstrained if I_unconstrained is not None else "",
        "I_cost_constrained": I_cost_constrained if I_cost_constrained is not None else "",
        "cost_sustainment_ratio": cost_sustainment_ratio if cost_sustainment_ratio is not None else "",
        "omega_profile_score": omega_profile_score,
        "truncated_cases": sum(truncs),
        "total_cases": len(truncs),
        "truncation_fraction": sum(truncs) / max(len(truncs), 1),
        "nondegeneracy_score": nondegeneracy_score,
        "estimator_warning": int(sum(truncs) / max(len(truncs), 1) > 0.25),
    }


def compute_behavioral_quotients(world: World):
    features = build_behavioral_features(world)
    labels_by_k = {}
    for k in BEHAVIORAL_KS:
        labels_by_k[k] = behavioral_quotient_labels(world, k, features)
    return labels_by_k


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    tmp_path = path.with_name(path.name + ".tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in keys})
    os.replace(tmp_path, path)


def build_predictive_features(world: World):
    memo = {}
    features = {}
    for state in state_space(world):
        vec = []
        for horizon in [1, 2, 3, 4]:
            rollouts = sample_rollouts(
                world,
                state,
                horizon,
                STATE_SAMPLE_ROLLOUTS,
                seed=world.seed + horizon * 71 + state[0] * 11 + state[1] * 13 + state[2] * 17,
            )
            viable_flags = [1.0 if r[1] else 0.0 for r in rollouts]
            terminal_positions = [(r[0][-1][0], r[0][-1][1]) for r in rollouts]
            trap_flags = [1.0 if r[3] else 0.0 for r in rollouts]
            resource_flags = [1.0 if r[4] else 0.0 for r in rollouts]
            vec.extend(
                [
                    sum(viable_flags) / max(len(viable_flags), 1),
                    entropy(Counter(terminal_positions)),
                    sum(trap_flags) / max(len(trap_flags), 1),
                    sum(resource_flags) / max(len(resource_flags), 1),
                ]
            )
        vec.append(one_step_viable_fraction(world, state))
        local_dist = Counter()
        for action in ACTIONS:
            for nxt, _ in transition(world, state, action):
                local_dist[(nxt[0], nxt[1], nxt[2])] += 1
        vec.append(entropy(local_dist))
        vec.append(1.0 if recoverable_micro(world, state, memo) else 0.0)
        features[state] = vec
    return features


def predictive_quotient_labels(world: World, k: int, state_features: dict[tuple[int, int, int], list[float]]):
    return behavioral_quotient_labels(world, k, state_features)


def candidate_category(name: str) -> str:
    if name in {"identity", "all_one"}:
        return "DIAGNOSTIC_ONLY"
    if name == "best_of_10_hashes_per_world":
        return "ADAPTIVE_HASH"
    if name in {"random_k", "hash_k34_s1206", "checkerboard", "trap_mixing_adversarial"}:
        return "ADVERSARIAL"
    return "THEORY_INFORMED"


def candidate_names() -> list[str]:
    return [
        "identity",
        "all_one",
        "random_k",
        "hash_k34_s1206",
        "best_of_10_hashes_per_world",
        "checkerboard",
        "trap_mixing_adversarial",
        "viability_signature",
        "behavioral_quotient_k5",
        "behavioral_quotient_k8",
        "behavioral_quotient_k13",
        "behavioral_quotient_k21",
        "predictive_quotient_k5",
        "predictive_quotient_k8",
        "predictive_quotient_k13",
        "predictive_quotient_k21",
    ]


def build_label_maps(world: World):
    state_features_behavioral = build_behavioral_features(world)
    state_features_predictive = build_predictive_features(world)
    behavioral_maps = {k: behavioral_quotient_labels(world, k, state_features_behavioral) for k in BEHAVIORAL_KS}
    predictive_maps = {k: predictive_quotient_labels(world, k, state_features_predictive) for k in PREDICTIVE_KS}
    random_map_fn = make_random_partition(world, RANDOM_K)
    return {
        "identity": {s: s for s in state_space(world)},
        "all_one": {s: 0 for s in state_space(world)},
        "random_k": {s: random_map_fn(s) for s in state_space(world)},
        "hash_k34_s1206": {s: coarse_hash_fixed(s) for s in state_space(world)},
        "checkerboard": {s: coarse_checkerboard(s) for s in state_space(world)},
        "trap_mixing_adversarial": {s: coarse_trap_mixing(world)(s) for s in state_space(world)},
        "viability_signature": {s: coarse_viability_signature_factory(world)(s) for s in state_space(world)},
    }, behavioral_maps, predictive_maps


def quotient_gate_metrics(world: World, labels: dict[tuple[int, int, int], object]) -> dict:
    states = state_space(world)
    label_counts = Counter(labels[s] for s in states)
    num_micro = len(states)
    num_macro = len(label_counts)
    compression_ratio = num_macro / max(num_micro, 1)
    mean_fiber_size = num_micro / max(num_macro, 1)
    singleton_fraction = sum(1 for c in label_counts.values() if c == 1) / max(num_macro, 1)
    label_ent = entropy(label_counts)
    identity_like = compression_ratio > 0.75 or singleton_fraction > 0.50
    all_one_like = num_macro <= 1 or label_ent < 0.05
    fiber_too_small = mean_fiber_size < 2.0
    quotient_gate_pass = not (identity_like or all_one_like or fiber_too_small)
    return {
        "num_micro": num_micro,
        "num_macro": num_macro,
        "compression_ratio": compression_ratio,
        "mean_fiber_size": mean_fiber_size,
        "singleton_fraction": singleton_fraction,
        "label_entropy": label_ent,
        "identity_like": int(identity_like),
        "all_one_like": int(all_one_like),
        "fiber_too_small": int(fiber_too_small),
        "quotient_gate_pass": int(quotient_gate_pass),
    }


def macrotrajectory_records(world: World, start_state: tuple[int, int, int], horizon: int, labels: dict) -> tuple[list[tuple], bool, int]:
    trajectories, truncated = enumerate_trajectories(world, start_state, horizon)
    records = []
    for states, viable, _cost in trajectories:
        if viable:
            records.append(tuple(labels[s] for s in states))
    return records, truncated, len(trajectories)


def heldout_predictive_sufficiency(world: World, candidate: str, labels: dict, starts: dict, traj_cache: dict) -> dict:
    records = []
    truncated_any = 0
    raw_counts = 0
    for start_name, start_state in starts.items():
        trajs, truncated = traj_cache[(start_name, PREDICTIVE_HORIZON)]
        truncated_any += int(truncated)
        raw_counts += len(trajs)
        for states, viable, _cost in trajs:
            if viable:
                records.append(
                    {
                        "start_name": start_name,
                        "macro_start": labels[states[0]],
                        "macro_traj": tuple(labels[s] for s in states),
                    }
                )
    if not records:
        return {
            "heldout_nll": float("inf"),
            "heldout_l1_loss": 1.0,
            "heldout_predictive_quality": 0.0,
            "train_records": 0,
            "test_records": 0,
            "truncated": int(truncated_any > 0),
            "raw_count": raw_counts,
            "mc_fallback_used": 0,
        }
    rng = random.Random(world.seed * 10007 + hash(candidate) % 1000)
    rng.shuffle(records)
    split = max(1, int(len(records) * TRAIN_FRACTION))
    train = records[:split]
    test = records[split:] if split < len(records) else records[:1]
    alpha = 1e-3
    train_by_start = defaultdict(Counter)
    train_start_totals = Counter()
    test_by_start = defaultdict(Counter)
    for r in train:
        train_by_start[r["macro_start"]][r["macro_traj"]] += 1
        train_start_totals[r["macro_start"]] += 1
    for r in test:
        test_by_start[r["macro_start"]][r["macro_traj"]] += 1
    nlls = []
    l1s = []
    for r in test:
        start = r["macro_start"]
        dist = train_by_start[start]
        support = len(dist) if len(dist) > 0 else 1
        denom = train_start_totals[start] + alpha * support
        prob = (dist[r["macro_traj"]] + alpha) / max(denom, 1e-9)
        nlls.append(-math.log(max(prob, 1e-12)))
    for start, test_counts in test_by_start.items():
        train_counts = train_by_start[start]
        support = set(train_counts) | set(test_counts)
        if not support:
            continue
        train_total = sum(train_counts.values())
        test_total = sum(test_counts.values())
        tv = 0.0
        for traj in support:
            pt = train_counts[traj] / max(train_total, 1)
            q = test_counts[traj] / max(test_total, 1)
            tv += abs(pt - q)
        l1s.append(0.5 * tv)
    heldout_nll = sum(nlls) / max(len(nlls), 1)
    heldout_l1_loss = sum(l1s) / max(len(l1s), 1) if l1s else 1.0
    return {
        "heldout_nll": heldout_nll,
        "heldout_l1_loss": heldout_l1_loss,
        "heldout_predictive_quality": 1.0 / (1.0 + heldout_nll),
        "train_records": len(train),
        "test_records": len(test),
        "truncated": int(truncated_any > 0),
        "raw_count": raw_counts,
        "mc_fallback_used": 0,
    }


def raw_future_entropy(world: World, labels: dict, starts: dict, traj_cache: dict) -> tuple[float, list[dict]]:
    rows = []
    values = []
    for start_name in starts:
        start_vals = []
        for horizon in HORIZONS:
            trajectories, truncated = traj_cache[(start_name, horizon)]
            viable = [tr for tr in trajectories if tr[1]]
            classes = Counter()
            for states, _, _ in viable:
                classes[tuple(labels[s] for s in states)] += 1
            I = entropy(classes)
            start_vals.append((horizon, I))
            values.append(I)
            rows.append(
                {
                    "start_name": start_name,
                    "T": horizon,
                    "I": I,
                    "raw_count": len(trajectories),
                    "viable_count": len(viable),
                    "truncated": int(truncated),
                }
            )
        rows[-len(HORIZONS):]
    return (sum(values) / max(len(values), 1), rows)


def recoverability_metrics(world: World, labels: dict) -> tuple[float, dict, float]:
    memo = {}
    state_recoverable = {state: 1.0 if recoverable_micro(world, state, memo) else 0.0 for state in state_space(world)}
    label_groups = defaultdict(list)
    for state, lab in labels.items():
        label_groups[lab].append(state_recoverable[state])
    label_vars = []
    label_purity = []
    for vals in label_groups.values():
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        label_vars.append(var)
        label_purity.append(max(mean, 1.0 - mean))
    weighted_var = sum(label_vars) / max(len(label_vars), 1)
    return 1.0 / (1.0 + weighted_var), state_recoverable, sum(label_purity) / max(len(label_purity), 1)


def hidden_viability_metrics(world: World, labels: dict, state_recoverable: dict) -> dict:
    state_viable = {}
    memo = {}
    for state in state_space(world):
        state_viable[state] = 1.0 if exists_viable_future(world, state, PREDICTIVE_HORIZON, memo) else 0.0
    label_groups = defaultdict(list)
    for state, lab in labels.items():
        label_groups[lab].append(state_viable[state])
    purities = []
    mixed = 0
    fake = 0
    hidden = 0
    for vals in label_groups.values():
        if not vals:
            continue
        vfrac = sum(vals) / len(vals)
        purities.append(max(vfrac, 1.0 - vfrac))
        if 0.0 < vfrac < 1.0:
            mixed += 1
        if 0.5 < vfrac < 1.0:
            fake += 1
        if 0.0 < vfrac < 0.5:
            hidden += 1
    return {
        "macro_viability_purity": sum(purities) / max(len(purities), 1),
        "mixed_viability_label_fraction": mixed / max(len(label_groups), 1),
        "fake_viability_rate": fake / max(len(label_groups), 1),
        "hidden_nonviability_rate": hidden / max(len(label_groups), 1),
    }


def horizon_coherence_metrics(world: World, labels: dict, starts: dict, traj_cache: dict) -> tuple[float, dict]:
    start_rows = []
    coherence_scores = []
    lure_detected = 0
    for start_name in starts:
        vals = []
        for horizon in HORIZONS:
            trajectories, truncated = traj_cache[(start_name, horizon)]
            viable = [tr for tr in trajectories if tr[1]]
            classes = Counter()
            for states, _, _ in viable:
                classes[tuple(labels[s] for s in states)] += 1
            vals.append((horizon, entropy(classes)))
        early = sum(v for t, v in vals if t in {2, 3}) / max(sum(1 for t, v in vals if t in {2, 3}), 1)
        late = sum(v for t, v in vals if t in {5, 6}) / max(sum(1 for t, v in vals if t in {5, 6}), 1)
        collapse = max(0.0, early - late)
        coherence = 1.0 / (1.0 + collapse)
        coherence_scores.append(coherence)
        lure_detected = lure_detected or (early > 0.75 and late < 0.5)
        start_rows.append(
            {
                "start_name": start_name,
                "early_mean": early,
                "late_mean": late,
                "collapse": collapse,
                "horizon_coherence_score": coherence,
                "lure_detected": int(early > 0.75 and late < 0.5),
            }
        )
    return sum(coherence_scores) / max(len(coherence_scores), 1), {"rows": start_rows, "lure_detected": int(lure_detected)}


def choose_best_adaptive_hash(world: World, starts: dict, traj_cache: dict) -> tuple[dict, int]:
    best_map = None
    best_idx = 0
    best_score = -1.0
    for idx in range(10):
        k = [2, 3, 5, 8, 13, 21, 34, 55][idx % 8]
        rng = random.Random(world.seed * 911 + idx * 37)
        mapping = {state: rng.randrange(k) for state in state_space(world)}
        score_row = heldout_predictive_sufficiency(world, "best_of_10_hashes_per_world", mapping, starts, traj_cache)
        score = score_row["heldout_predictive_quality"]
        if score > best_score:
            best_score = score
            best_idx = idx
            best_map = mapping
    return best_map if best_map is not None else make_random_partition(world, 5), best_idx


def evaluate_world(world: World) -> dict:
    starts = {}
    for label in ["open", "noise_swamp", "bottleneck", "loop", "resource_corridor", "dead_branch", "near_trap", "rigid_attractor"]:
        st = select_start(world.grid, label)
        if st is not None:
            starts[label] = st
    if not starts:
        starts["open"] = (0, 0, world.initial_energy)

    traj_cache = {}
    for start_name, start_state in starts.items():
        for horizon in HORIZONS:
            traj_cache[(start_name, horizon)] = enumerate_trajectories(world, start_state, horizon)

    base_label_maps, behavioral_maps, predictive_maps = build_label_maps(world)
    candidate_maps = dict(base_label_maps)
    candidate_maps["behavioral_quotient_k5"] = behavioral_maps[5]
    candidate_maps["behavioral_quotient_k8"] = behavioral_maps[8]
    candidate_maps["behavioral_quotient_k13"] = behavioral_maps[13]
    candidate_maps["behavioral_quotient_k21"] = behavioral_maps[21]
    candidate_maps["predictive_quotient_k5"] = predictive_maps[5]
    candidate_maps["predictive_quotient_k8"] = predictive_maps[8]
    candidate_maps["predictive_quotient_k13"] = predictive_maps[13]
    candidate_maps["predictive_quotient_k21"] = predictive_maps[21]
    adaptive_map, adaptive_idx = choose_best_adaptive_hash(world, starts, traj_cache)
    candidate_maps["best_of_10_hashes_per_world"] = adaptive_map

    state_recoverability_score, state_recoverable, state_recoverability_purity = recoverability_metrics(world, base_label_maps["viability_signature"])

    rows = []
    heldout_rows = []
    quotient_rows = []
    estimator_rows = []
    family_A_rows = []
    family_B_rows = []
    family_C_rows = []
    family_D_rows = []

    random_baseline_quality = None
    for candidate in candidate_names():
        labels = candidate_maps[candidate]
        gate = quotient_gate_metrics(world, labels)
        raw_I_mean, raw_rows = raw_future_entropy(world, labels, starts, traj_cache)
        held = heldout_predictive_sufficiency(world, candidate, labels, starts, traj_cache)
        recoverability_preservation, _, recoverability_purity = recoverability_metrics(world, labels)
        horizon_coherence, horizon_detail = horizon_coherence_metrics(world, labels, starts, traj_cache)
        hidden_metrics = hidden_viability_metrics(world, labels, state_recoverable)
        candidate_row = {
            "world_seed": world.seed,
            "family": world.family,
            "variant": world.variant,
            "pair_id": world.pair_id if world.pair_id is not None else "",
            "candidate": candidate,
            "candidate_category": candidate_category(candidate),
            "raw_I_mean": raw_I_mean,
            "compression_ratio": gate["compression_ratio"],
            "mean_fiber_size": gate["mean_fiber_size"],
            "singleton_fraction": gate["singleton_fraction"],
            "label_entropy": gate["label_entropy"],
            "quotient_gate_pass": gate["quotient_gate_pass"],
            "heldout_nll": held["heldout_nll"],
            "heldout_l1_loss": held["heldout_l1_loss"],
            "heldout_predictive_quality": held["heldout_predictive_quality"],
            "recoverability_preservation": recoverability_preservation,
            "recoverability_purity": recoverability_purity,
            "horizon_coherence": horizon_coherence,
            "irreversibility_sensitivity": "",
            "norm_irrev_sensitivity": "",
            "bounded_cost_sustainment": "",
            "unsustainable_branch_penalty": "",
            "fake_viability_rejection_score": 1.0 - hidden_metrics["fake_viability_rate"],
            "macro_viability_purity": hidden_metrics["macro_viability_purity"],
            "mixed_viability_label_fraction": hidden_metrics["mixed_viability_label_fraction"],
            "fake_viability_rate": hidden_metrics["fake_viability_rate"],
            "hidden_nonviability_rate": hidden_metrics["hidden_nonviability_rate"],
            "truncated": 0,
            "truncation_fraction": 0.0,
            "mc_fallback_used": int(held["mc_fallback_used"]),
            "adaptive_idx": adaptive_idx if candidate == "best_of_10_hashes_per_world" else "",
        }

        if candidate == "random_k":
            random_baseline_quality = held["heldout_predictive_quality"]

        if world.family == "A":
            family_A_rows.extend(raw_rows)
        if world.family == "B":
            family_B_rows.extend(raw_rows)
        if world.family == "C":
            # Cost constrained comparison.
            Fmax = {T: 1.5 * T + 2 for T in HORIZONS}
            unconstrained = raw_I_mean
            constrained_vals = []
            for start_name, start_state in starts.items():
                trajectories, truncated = traj_cache[(start_name, PREDICTIVE_HORIZON)]
                viable = [tr for tr in trajectories if tr[1] and tr[2] <= Fmax[PREDICTIVE_HORIZON]]
                classes = Counter()
                for states, _, _ in viable:
                    classes[tuple(labels[s] for s in states)] += 1
                constrained_vals.append(entropy(classes))
            constrained = sum(constrained_vals) / max(len(constrained_vals), 1)
            candidate_row["bounded_cost_sustainment"] = constrained / max(unconstrained, 1e-9)
            candidate_row["unsustainable_branch_penalty"] = max(0.0, unconstrained - constrained)
            family_C_rows.append(
                {
                    "world_seed": world.seed,
                    "family": world.family,
                    "variant": world.variant,
                    "pair_id": world.pair_id if world.pair_id is not None else "",
                    "candidate": candidate,
                    "candidate_category": candidate_category(candidate),
                    "I_unconstrained": unconstrained,
                    "I_cost_constrained": constrained,
                    "cost_sustainment_ratio": candidate_row["bounded_cost_sustainment"],
                    "unsustainable_branch_penalty": candidate_row["unsustainable_branch_penalty"],
                }
            )
        if world.family == "D":
            family_D_rows.append(
                {
                    "world_seed": world.seed,
                    "family": world.family,
                    "variant": world.variant,
                    "pair_id": world.pair_id if world.pair_id is not None else "",
                    "candidate": candidate,
                    "candidate_category": candidate_category(candidate),
                    **hidden_metrics,
                }
            )
        if world.family == "A":
            # Pairwise irreversibility handled in aggregation; keep the raw rows.
            candidate_row["irreversibility_sensitivity"] = raw_I_mean
        rows.append(candidate_row)
        heldout_rows.append(
            {
                "world_seed": world.seed,
                "family": world.family,
                "variant": world.variant,
                "pair_id": world.pair_id if world.pair_id is not None else "",
                "candidate": candidate,
                "candidate_category": candidate_category(candidate),
                **held,
            }
        )
        quotient_rows.append(
            {
                "world_seed": world.seed,
                "family": world.family,
                "variant": world.variant,
                "pair_id": world.pair_id if world.pair_id is not None else "",
                "candidate": candidate,
                "candidate_category": candidate_category(candidate),
                **gate,
            }
        )
        estimator_rows.append(
            {
                "world_seed": world.seed,
                "family": world.family,
                "variant": world.variant,
                "pair_id": world.pair_id if world.pair_id is not None else "",
                "candidate": candidate,
                "candidate_category": candidate_category(candidate),
                "truncated": int(any(tr[1] and len(tr[0]) >= 0 for _name in starts for tr in [traj_cache[(_name, PREDICTIVE_HORIZON)]])),
                "raw_count": held["raw_count"],
                "train_records": held["train_records"],
                "test_records": held["test_records"],
                "mc_fallback_used": held["mc_fallback_used"],
            }
        )

    # Compute family A/B diagnostic rows from raw horizon rows.
    raw_by_candidate = defaultdict(list)
    for r in rows:
        raw_by_candidate[r["candidate"]].append(r)
    raw_family_rows = []
    for candidate in candidate_names():
        labels = candidate_maps[candidate]
        if world.family == "A":
            vals = []
            for start_name in starts:
                start_vals = []
                for horizon in HORIZONS:
                    trajectories, truncated = traj_cache[(start_name, horizon)]
                    viable = [tr for tr in trajectories if tr[1]]
                    classes = Counter()
                    for states, _, _ in viable:
                        classes[tuple(labels[s] for s in states)] += 1
                    start_vals.append((horizon, entropy(classes)))
                    raw_family_rows.append(
                        {
                            "world_seed": world.seed,
                            "family": world.family,
                            "variant": world.variant,
                            "pair_id": world.pair_id if world.pair_id is not None else "",
                            "candidate": candidate,
                            "start_name": start_name,
                            "T": horizon,
                            "I": start_vals[-1][1],
                            "truncated": int(truncated),
                        }
                    )
                early = sum(v for t, v in start_vals if t in {2, 3}) / max(sum(1 for t, v in start_vals if t in {2, 3}), 1)
                late = sum(v for t, v in start_vals if t in {5, 6}) / max(sum(1 for t, v in start_vals if t in {5, 6}), 1)
                vals.append(early - late)
            candidate_row = next(r for r in rows if r["candidate"] == candidate)
            candidate_row["irreversibility_sensitivity"] = sum(vals) / max(len(vals), 1)
            candidate_row["norm_irrev_sensitivity"] = candidate_row["irreversibility_sensitivity"] / max(abs(candidate_row["raw_I_mean"]), 1e-9)
        elif world.family == "B":
            for start_name in starts:
                start_vals = []
                for horizon in HORIZONS:
                    trajectories, truncated = traj_cache[(start_name, horizon)]
                    viable = [tr for tr in trajectories if tr[1]]
                    classes = Counter()
                    for states, _, _ in viable:
                        classes[tuple(labels[s] for s in states)] += 1
                    start_vals.append((horizon, entropy(classes)))
                    raw_family_rows.append(
                        {
                            "world_seed": world.seed,
                            "family": world.family,
                            "variant": world.variant,
                            "pair_id": world.pair_id if world.pair_id is not None else "",
                            "candidate": candidate,
                            "start_name": start_name,
                            "T": horizon,
                            "I": start_vals[-1][1],
                            "truncated": int(truncated),
                        }
                    )
        elif world.family == "C":
            pass
        elif world.family == "D":
            pass

    return {
        "world_seed": world.seed,
        "family": world.family,
        "variant": world.variant,
        "pair_id": world.pair_id if world.pair_id is not None else "",
        "world_rows": rows,
        "heldout_rows": heldout_rows,
        "quotient_rows": quotient_rows,
        "family_A_rows": raw_family_rows if world.family == "A" else [],
        "family_B_rows": raw_family_rows if world.family == "B" else [],
        "family_C_rows": family_C_rows,
        "family_D_rows": family_D_rows,
        "estimator_rows": estimator_rows,
    }


def aggregate_candidate_summary(world_rows: list[dict], heldout_rows: list[dict], quotient_rows: list[dict]) -> list[dict]:
    by_candidate = defaultdict(list)
    for row in world_rows:
        by_candidate[row["candidate"]].append(row)
    held_by_candidate = defaultdict(list)
    for row in heldout_rows:
        held_by_candidate[row["candidate"]].append(row)
    gate_by_candidate = defaultdict(list)
    for row in quotient_rows:
        gate_by_candidate[row["candidate"]].append(row)

    baseline_random = sum(r["heldout_predictive_quality"] for r in held_by_candidate.get("random_k", [])) / max(len(held_by_candidate.get("random_k", [])), 1)
    summary_rows = []
    for candidate, rows in by_candidate.items():
        held = held_by_candidate.get(candidate, [])
        gates = gate_by_candidate.get(candidate, [])
        quotient_gate_pass_rate = sum(r["quotient_gate_pass"] for r in gates) / max(len(gates), 1)
        heldout_predictive_quality = sum(r["heldout_predictive_quality"] for r in held) / max(len(held), 1)
        heldout_l1_loss = sum(r["heldout_l1_loss"] for r in held) / max(len(held), 1)
        rec = sum(r["recoverability_preservation"] for r in rows) / max(len(rows), 1)
        horizon = sum(r["horizon_coherence"] for r in rows) / max(len(rows), 1)
        irrev = sum(float(r["irreversibility_sensitivity"]) for r in rows if r["irreversibility_sensitivity"] not in ("", None)) / max(
            sum(1 for r in rows if r["irreversibility_sensitivity"] not in ("", None)), 1
        )
        cost = sum(float(r["bounded_cost_sustainment"]) for r in rows if r["bounded_cost_sustainment"] not in ("", None)) / max(
            sum(1 for r in rows if r["bounded_cost_sustainment"] not in ("", None)), 1
        )
        fake_rej = sum(r["fake_viability_rejection_score"] for r in rows) / max(len(rows), 1)
        nondeg = sum(r["quotient_gate_pass"] for r in rows) / max(len(rows), 1)
        admissible = (
            quotient_gate_pass_rate >= 0.8
            and heldout_predictive_quality > baseline_random
            and sum(
                [
                    rec > baseline_random,
                    horizon > baseline_random,
                    irrev > 0.0,
                    cost > 0.0,
                    fake_rej > baseline_random,
                ]
            )
            >= 4
        )
        bucket = "DIAGNOSTIC_ONLY" if candidate in {"identity", "all_one"} else (
            "INELIGIBLE_QUOTIENT" if quotient_gate_pass_rate < 0.8 else (
                "FAILED_HELDOUT" if heldout_predictive_quality <= baseline_random else (
                    "FAILED_INVARIANT_PROFILE" if sum(
                        [
                            rec > baseline_random,
                            horizon > baseline_random,
                            irrev > 0.0,
                            cost > 0.0,
                            fake_rej > baseline_random,
                        ]
                    ) < 4 else "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE"
                )
            )
        )
        summary_rows.append(
            {
                "candidate": candidate,
                "candidate_category": candidate_category(candidate),
                "bucket": bucket,
                "quotient_gate_pass_rate": quotient_gate_pass_rate,
                "heldout_predictive_quality": heldout_predictive_quality,
                "baseline_random_predictive_quality": baseline_random,
                "heldout_l1_loss": heldout_l1_loss,
                "recoverability_preservation": rec,
                "horizon_coherence": horizon,
                "irreversibility_sensitivity": irrev,
                "bounded_cost_sustainment": cost,
                "fake_viability_rejection_score": fake_rej,
                "nondegeneracy_score": nondeg,
                "admissible_single_omega_score": gmean([heldout_predictive_quality, rec, horizon, max(irrev, 0.0), max(cost, 0.0), max(fake_rej, 0.0)]),
                "worlds": len(rows),
                "passed_invariant_families": sum(
                    [
                        rec > baseline_random,
                        horizon > baseline_random,
                        irrev > 0.0,
                        cost > 0.0,
                        fake_rej > baseline_random,
                    ]
                ),
                "admissible": int(admissible),
            }
        )
    summary_rows.sort(key=lambda r: (r["bucket"] != "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE", -r["heldout_predictive_quality"], -r["admissible_single_omega_score"]))
    return summary_rows


def maybe_plot(results_dir: Path, summary_rows: list[dict], quotient_rows: list[dict], world_rows: list[dict]):
    if plt is None or should_abort_now():
        return
    results_dir.mkdir(exist_ok=True)
    counts = Counter(r["bucket"] for r in summary_rows)
    plt.figure(figsize=(8, 5))
    plt.bar(list(counts.keys()), list(counts.values()))
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(results_dir / "candidate_bucket_counts.png", dpi=140)
    plt.close()

    plt.figure(figsize=(8, 5))
    xs = [r["quotient_gate_pass_rate"] for r in summary_rows]
    ys = [r["heldout_predictive_quality"] for r in summary_rows]
    plt.scatter(xs, ys, s=60)
    for x, y, r in zip(xs, ys, summary_rows):
        plt.text(x + 0.005, y + 0.005, r["candidate"], fontsize=7)
    plt.xlabel("quotient_gate_pass_rate")
    plt.ylabel("heldout_predictive_quality")
    plt.tight_layout()
    plt.savefig(results_dir / "admissible_candidates_scatter.png", dpi=140)
    plt.close()


def flush_outputs(
    results_dir: Path,
    world_rows: list[dict],
    heldout_rows: list[dict],
    quotient_rows: list[dict],
):
    write_csv(results_dir / "invariant_profile_by_world.csv", world_rows)
    write_csv(results_dir / "heldout_predictive_sufficiency.csv", heldout_rows)
    write_csv(results_dir / "quotient_gate_report.csv", quotient_rows)


def main():
    results_dir = Path("probe_06a_minimal_admissible_quotient_gate_results")
    results_dir.mkdir(exist_ok=True)
    summary = {
        "runtime_status": status_code(),
        "soft_limit_seconds": SOFT_LIMIT_SECONDS,
        "hard_limit_seconds": HARD_LIMIT_SECONDS,
        "workers": WORKERS,
        "worlds_requested": 0,
        "worlds_completed": 0,
        "families_completed": [],
        "truncation_fraction": 0.0,
        "estimator_warning": False,
    }

    worlds = build_worlds()
    summary["worlds_requested"] = len(worlds)

    world_rows = []
    heldout_rows = []
    quotient_rows = []
    family_A_rows = []
    family_B_rows = []
    family_C_rows = []
    family_D_rows = []
    estimator_rows = []
    errors = []

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(evaluate_world, world): world for world in worlds}
        for fut in as_completed(futures):
            world = futures.pop(fut)
            try:
                result = fut.result()
                summary["worlds_completed"] += 1
                world_rows.extend(result["world_rows"])
                heldout_rows.extend(result["heldout_rows"])
                quotient_rows.extend(result["quotient_rows"])
                estimator_rows.extend(result["estimator_rows"])
                family_A_rows.extend(result["family_A_rows"])
                family_B_rows.extend(result["family_B_rows"])
                family_C_rows.extend(result["family_C_rows"])
                family_D_rows.extend(result["family_D_rows"])
            except Exception as exc:
                errors.append({"world_seed": world.seed, "family": world.family, "variant": world.variant, "error": str(exc)})
                summary["runtime_status"] = "ERROR"
                continue
            if summary["worlds_completed"] % 20 == 0:
                flush_outputs(results_dir, world_rows, heldout_rows, quotient_rows)
            if should_abort_now():
                summary["runtime_status"] = "PARTIAL_EXIT_HARD_LIMIT"
                break
            if not should_continue_block():
                summary["runtime_status"] = "PARTIAL_EXIT_SOFT_LIMIT"
                break

    summary["families_completed"] = sorted({r["family"] for r in world_rows})
    summary["truncation_fraction"] = sum(r["truncated"] for r in estimator_rows) / max(len(estimator_rows), 1)
    summary["estimator_warning"] = summary["truncation_fraction"] > 0.25
    if errors and summary["runtime_status"] == "COMPLETE":
        summary["runtime_status"] = "ERROR"

    flush_outputs(results_dir, world_rows, heldout_rows, quotient_rows)
    write_csv(results_dir / "estimator_report.csv", estimator_rows)
    summary_rows = aggregate_candidate_summary(world_rows, heldout_rows, quotient_rows)
    write_csv(results_dir / "invariant_summary_by_candidate.csv", summary_rows)

    # Family reports.
    if family_A_rows:
        paired = defaultdict(list)
        for row in family_A_rows:
            paired[(row["pair_id"], row["candidate"], row["start_name"])].append(row)
        fam_a = []
        for (pair_id, candidate, start_name), rows in paired.items():
            if len(rows) >= 2:
                rows = sorted(rows, key=lambda r: r["T"])
                early = sum(r["I"] for r in rows if r["T"] in {2, 3}) / max(sum(1 for r in rows if r["T"] in {2, 3}), 1)
                late = sum(r["I"] for r in rows if r["T"] in {5, 6}) / max(sum(1 for r in rows if r["T"] in {5, 6}), 1)
                fam_a.append(
                    {
                        "pair_id": pair_id,
                        "candidate": candidate,
                        "start_name": start_name,
                        "early_mean": early,
                        "late_mean": late,
                        "irreversibility_sensitivity": early - late,
                        "norm_irrev_sensitivity": (early - late) / max(abs(early), 1e-9),
                    }
                )
        write_csv(results_dir / "family_A_irreversibility.csv", fam_a)
    if family_B_rows:
        fam_b = []
        by_world = defaultdict(list)
        for row in family_B_rows:
            by_world[(row["pair_id"], row["candidate"], row["start_name"])].append(row)
        for (pair_id, candidate, start_name), rows in by_world.items():
            rows = sorted(rows, key=lambda r: r["T"])
            early = sum(r["I"] for r in rows if r["T"] in {2, 3}) / max(sum(1 for r in rows if r["T"] in {2, 3}), 1)
            late = sum(r["I"] for r in rows if r["T"] in {5, 6}) / max(sum(1 for r in rows if r["T"] in {5, 6}), 1)
            fam_b.append(
                {
                    "pair_id": pair_id,
                    "candidate": candidate,
                    "start_name": start_name,
                    "early_mean": early,
                    "late_mean": late,
                    "collapse": max(0.0, early - late),
                    "horizon_coherence_score": 1.0 / (1.0 + max(0.0, early - late)),
                    "lure_detected": int(early > 0.75 and late < 0.5),
                }
            )
        write_csv(results_dir / "family_B_horizon_coherence.csv", fam_b)
    if family_C_rows:
        write_csv(results_dir / "family_C_bounded_cost.csv", family_C_rows)
    if family_D_rows:
        write_csv(results_dir / "family_D_hidden_fake_viability.csv", family_D_rows)

    bucket_counts = Counter(r["bucket"] for r in summary_rows)
    baseline_random = next((r["heldout_predictive_quality"] for r in summary_rows if r["candidate"] == "random_k"), 0.0)
    best_admissible = [r for r in summary_rows if r["bucket"] == "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE"]
    identity_row = next((r for r in summary_rows if r["candidate"] == "identity"), {})
    all_one_row = next((r for r in summary_rows if r["candidate"] == "all_one"), {})
    hash_row = next((r for r in summary_rows if r["candidate"] == "hash_k34_s1206"), {})
    adaptive_row = next((r for r in summary_rows if r["candidate"] == "best_of_10_hashes_per_world"), {})

    flags = {
        "QUOTIENT_GATE_WORKING": any(r["candidate"] not in {"identity", "all_one"} and r["quotient_gate_pass_rate"] >= 0.8 for r in summary_rows),
        "HELDOUT_PREDICTIVE_GATE_WORKING": any(r["candidate"] not in {"identity", "all_one"} and r["heldout_predictive_quality"] > baseline_random for r in summary_rows),
        "IDENTITY_REJECTED_AS_QUOTIENT": identity_row.get("bucket") in {"DIAGNOSTIC_ONLY", "INELIGIBLE_QUOTIENT"},
        "ALL_ONE_REJECTED_AS_QUOTIENT": all_one_row.get("bucket") in {"DIAGNOSTIC_ONLY", "INELIGIBLE_QUOTIENT"},
        "RANDOM_BASELINE_DEMOTED": next((r["bucket"] for r in summary_rows if r["candidate"] == "random_k"), "") != "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE",
        "ADAPTIVE_HASH_DEMOTED": next((r["bucket"] for r in summary_rows if r["candidate"] == "best_of_10_hashes_per_world"), "") != "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE",
        "HASH_K34_STILL_ADMISSIBLE": hash_row.get("bucket") == "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE",
        "BEHAVIORAL_QUOTIENT_PROMISING": any(r["candidate"].startswith("behavioral_quotient") and r["bucket"] == "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE" for r in summary_rows),
        "PREDICTIVE_QUOTIENT_PROMISING": any(r["candidate"].startswith("predictive_quotient") and r["bucket"] == "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE" for r in summary_rows),
        "INVARIANTS_DISCRIMINATIVE": (max(r["admissible_single_omega_score"] for r in summary_rows) - min(r["admissible_single_omega_score"] for r in summary_rows)) > 0.05 if summary_rows else False,
        "ESTIMATOR_WARNING": summary["estimator_warning"],
        "READY_FOR_LARGER_STRESS": False,
    }
    flags["READY_FOR_LARGER_STRESS"] = (
        flags["QUOTIENT_GATE_WORKING"]
        and flags["HELDOUT_PREDICTIVE_GATE_WORKING"]
        and flags["INVARIANTS_DISCRIMINATIVE"]
        and not flags["ESTIMATOR_WARNING"]
    )

    summary.update(
        {
            "bucket_counts": dict(bucket_counts),
            "flags": flags,
            "top_admissible_candidates": best_admissible[:3],
            "identity_row": identity_row,
            "all_one_row": all_one_row,
            "hash_row": hash_row,
            "adaptive_row": adaptive_row,
            "baseline_random_predictive_quality": baseline_random,
        }
    )
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (results_dir / "errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")

    maybe_plot(results_dir, summary_rows, quotient_rows, world_rows)

    print("\nPROBE 06A: MINIMAL ADMISSIBLE QUOTIENT GATE")
    print("\nRuntime:")
    print(f"- status: {summary['runtime_status']}")
    print(f"- workers: {summary['workers']}")
    print(f"- worlds completed / requested: {summary['worlds_completed']} / {summary['worlds_requested']}")
    print(f"- truncation fraction: {summary['truncation_fraction']:.3f}")
    print(f"- estimator warning: {str(summary['estimator_warning']).lower()}")
    print("\nCandidate buckets:")
    for bucket in ["DIAGNOSTIC_ONLY", "INELIGIBLE_QUOTIENT", "FAILED_HELDOUT", "FAILED_INVARIANT_PROFILE", "ADMISSIBLE_SINGLE_OMEGA_CANDIDATE"]:
        print(f"- {bucket}: {bucket_counts.get(bucket, 0)}")
    print("\nTop admissible candidates:")
    for i, row in enumerate(best_admissible[:3], 1):
        print(f"{i}. {row['candidate']} ({row['heldout_predictive_quality']:.3f})")
    print("\nKey controls:")
    print(f"- identity diagnostic raw I: {identity_row.get('raw_I_mean', 0.0):.3f}")
    print(f"- identity quotient eligible: {str(identity_row.get('bucket') == 'ADMISSIBLE_SINGLE_OMEGA_CANDIDATE').lower()}")
    print(f"- all_one quotient eligible: {str(all_one_row.get('bucket') == 'ADMISSIBLE_SINGLE_OMEGA_CANDIDATE').lower()}")
    print(f"- random_k bucket: {next((r['bucket'] for r in summary_rows if r['candidate'] == 'random_k'), 'n/a')}")
    print(f"- best_of_10_hashes bucket: {adaptive_row.get('bucket', 'n/a')}")
    print(f"- hash_k34_s1206 bucket: {hash_row.get('bucket', 'n/a')}")
    print("\nInvariant checks:")
    print(f"- recoverability preservation: {max((r['recoverability_preservation'] for r in summary_rows), default=0.0):.3f}")
    print(f"- horizon coherence: {max((r['horizon_coherence'] for r in summary_rows), default=0.0):.3f}")
    print(f"- irreversibility sensitivity: {max((r.get('irreversibility_sensitivity', 0.0) if isinstance(r.get('irreversibility_sensitivity', 0.0), float) else 0.0 for r in summary_rows), default=0.0):.3f}")
    print(f"- bounded cost: {max((r.get('bounded_cost_sustainment', 0.0) if isinstance(r.get('bounded_cost_sustainment', 0.0), float) else 0.0 for r in summary_rows), default=0.0):.3f}")
    print(f"- hidden/fake viability rejection: {max((r['fake_viability_rejection_score'] for r in summary_rows), default=0.0):.3f}")
    print("\nInterpretation:")
    print("- Did non-hand-tuned quotients pass?")
    print("- Did adversarial hashes survive heldout prediction?")
    print("- Did derived invariants distinguish candidates?")
    print("- Is Single Omega operationalization improving?")
    print("- Recommended next step.")
    print(f"\nResults: {results_dir.resolve()}")


if __name__ == "__main__":
    main()
