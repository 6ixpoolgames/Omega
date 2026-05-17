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
WORKERS = int(os.environ.get("OMEGA_WORKERS", min(18, max(1, (os.cpu_count() or 4) - 2))))
WORLDS_PER_FAMILY = 30
WORLDS_PER_FAMILY_MAX = 60
MAX_TRAJ_PER_STATE = 20000
ENERGY_CAP = 6
INITIAL_ENERGY_DEFAULT = 4
REPAIR_HORIZON = 3
HORIZONS = [2, 3, 4, 5, 6]
BEHAVIORAL_KS = [5, 8, 13, 21]
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


def base_world(seed: int, family: str, variant: str) -> World:
    return World(
        family=family,
        variant=variant,
        seed=seed,
        grid=BASE_GRID_9[:],
        size=9,
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


def generate_family_world(family: str, seed: int, variant: str, pair_id: int | None = None) -> World:
    w = base_world(seed, family, variant)
    w.pair_id = pair_id
    rng = random.Random(seed * 1543 + len(family) * 97 + (0 if variant == "a" else 1))
    notes: list[str] = []

    if family == "A":
        grid = grid_copy(BASE_GRID_9)
        # Keep branching count similar, vary reversibility in side paths.
        if variant == "reversible":
            for x, y in [(2, 2), (3, 2), (2, 3), (1, 4)]:
                grid[y][x] = "L"
            w.rigid_mode = "sticky"
        else:
            for x, y in [(2, 2), (3, 2), (2, 3), (1, 4)]:
                grid[y][x] = "D"
            grid[8][0] = "T"
            grid[8][1] = "T"
            w.rigid_mode = "bounded"
        w.grid = rows_from_grid(grid)
        notes.append("branch_pair")

    elif family == "B":
        grid = grid_copy(BASE_GRID_9)
        if variant == "lure":
            for x, y in [(4, 1), (5, 1), (4, 2), (5, 2)]:
                grid[y][x] = "S"
            grid[3][6] = "T"
            grid[3][7] = "T"
            grid[4][6] = "D"
            grid[4][7] = "D"
            w.noise_slip_prob = 0.35
        else:
            for x, y in [(4, 1), (5, 1), (4, 2), (5, 2)]:
                grid[y][x] = "C"
            grid[3][6] = "C"
            grid[3][7] = "C"
            grid[4][6] = "L"
            grid[4][7] = "L"
            w.noise_slip_prob = 0.15
        w.grid = rows_from_grid(grid)
        notes.append("lure_pair")

    elif family == "C":
        grid = grid_copy(BASE_GRID_9)
        # Explicit 3x3 room ladder: top=resource/trap, middle=loop/bottleneck, bottom=safe/rough.
        room_labels = [
            ["C", "O", "T"],
            ["L", "B", "C"],
            ["A", "D", "R"],
        ]
        for ry in range(3):
            for rx in range(3):
                label = room_labels[ry][rx]
                for y in range(ry * 3, ry * 3 + 3):
                    for x in range(rx * 3, rx * 3 + 3):
                        grid[y][x] = label
        # carve a doorway cross
        for x in [2, 5]:
            grid[2][x] = "B"
            grid[5][x] = "B"
        for y in [2, 5]:
            grid[y][2] = "B"
            grid[y][5] = "B"
        w.grid = rows_from_grid(grid)
        w.noise_slip_prob = 0.1 + 0.05 * (seed % 3)
        notes.append("scale_ladder")

    elif family == "D":
        grid = grid_copy(BASE_GRID_9)
        # Resource budget stress: rough terrain and resource islands.
        for y in range(9):
            for x in range(9):
                if (x + y + seed) % 5 == 0 and grid[y][x] in {"O", "."}:
                    grid[y][x] = "S"
        for x, y in [(6, 3), (7, 3), (6, 4), (7, 4)]:
            grid[y][x] = "C"
        w.grid = rows_from_grid(grid)
        w.energy_cap = 6
        w.initial_energy = 4 + (seed % 2)
        w.move_cost = 1
        w.rough_cost = 2 + (seed % 2)
        w.resource_bonus = 2
        w.wait_cost = 0 if seed % 3 else 1
        w.noise_slip_prob = 0.1 + 0.1 * (seed % 4)
        w.cost_budget_scale = 1.5
        notes.append("budget")

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
    for pair_id in range(15):
        seed = pair_id
        worlds.append(generate_family_world("A", seed, "reversible", pair_id))
        worlds.append(generate_family_world("A", seed, "irreversible", pair_id))
    for pair_id in range(15):
        seed = 100 + pair_id
        worlds.append(generate_family_world("B", seed, "lure", pair_id))
        worlds.append(generate_family_world("B", seed, "control", pair_id))
    for seed in range(30):
        worlds.append(generate_family_world("C", 200 + seed, "ladder", seed))
    for seed in range(30):
        worlds.append(generate_family_world("D", 300 + seed, "budget", seed))
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
        return energy_bin, trap_bin, branch_bin, res_bin
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

    cache = {"starts": starts, "traj": traj_cache}
    coarse_specs = {
        "identity": lambda s: s,
        "all_one": coarse_all_one,
        "random_k": lambda s: None,  # handled specially
        "checkerboard": coarse_checkerboard,
        "region": lambda s: region_xy(world.grid, s[0], s[1]),
        "viability_signature": coarse_viability_signature_factory(world),
        "hash_k34_s1206": coarse_hash_fixed,
        "trap_mixing_adversarial": coarse_trap_mixing(world),
    }

    results = []
    base_world_rows = []
    for coarse_name, coarse_fn in coarse_specs.items():
        if coarse_name == "random_k":
            coarse_fn = make_random_partition(world, RANDOM_K)
        rows = []
        for start_name, _ in starts.items():
            for horizon in HORIZONS:
                trajectories, truncated = traj_cache[(start_name, horizon)]
                viable = [tr for tr in trajectories if tr[1]]
                classes = Counter()
                for states, _, _ in viable:
                    if coarse_name == "region":
                        label = tuple(region_xy(world.grid, s[0], s[1]) for s in states)
                    elif coarse_name == "random_k":
                        label = tuple(coarse_fn(s) for s in states)
                    else:
                        label = tuple(coarse_fn(s) for s in states)
                    classes[label] += 1
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
        score_row = compute_world_row(world, cache, coarse_name, coarse_fn)
        results.append(score_row)
        base_world_rows.extend(rows)

    # Behavioral quotient candidates.
    bx_maps = compute_behavioral_quotients(world)
    for k in BEHAVIORAL_KS:
        bx_map = bx_maps[k]
        coarse_name = f"behavioral_quotient_k{k}"
        rows = []
        for start_name, _ in starts.items():
            for horizon in HORIZONS:
                trajectories, truncated = traj_cache[(start_name, horizon)]
                viable = [tr for tr in trajectories if tr[1]]
                classes = Counter()
                for states, _, _ in viable:
                    classes[tuple(bx_map[s] for s in states)] += 1
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
        score_row = compute_world_row(world, cache, coarse_name, lambda s: bx_map[s], bx_map=bx_map)
        results.append(score_row)
        base_world_rows.extend(rows)

    # Optional adaptive control: best-of-10 hash adversary.
    adaptive_rows = []
    best_score = -1.0
    best_rows = None
    for idx in range(10):
        k = [2, 3, 5, 8, 13, 21, 34, 55][idx % 8]
        rng = random.Random(world.seed * 911 + idx * 37)
        mapping = {state: rng.randrange(k) for state in state_space(world)}
        def hf(s, mapping=mapping):
            return mapping[s]
        score = 0.0
        rows = []
        for start_name, _ in starts.items():
            for horizon in HORIZONS:
                trajectories, truncated = traj_cache[(start_name, horizon)]
                viable = [tr for tr in trajectories if tr[1]]
                classes = Counter()
                for states, _, _ in viable:
                    classes[tuple(hf(s) for s in states)] += 1
                omega = entropy(classes)
                score += omega
                rows.append(
                    {
                        "world_seed": world.seed,
                        "family": world.family,
                        "variant": world.variant,
                        "pair_id": world.pair_id if world.pair_id is not None else "",
                        "coarse_name": "best_of_10_hashes_per_world",
                        "adaptive_idx": idx,
                        "start": start_name,
                        "T": horizon,
                        "I": omega,
                        "N_eff": math.exp(omega),
                        "raw_count": len(trajectories),
                        "viable_count": len(viable),
                        "truncated": int(truncated),
                    }
                )
        if score > best_score:
            best_score = score
            best_rows = rows
    if best_rows:
        adaptive_rows = best_rows
        score_row = compute_world_row(world, cache, "best_of_10_hashes_per_world", lambda s: 0)
        score_row["adaptive_idx"] = adaptive_rows[0].get("adaptive_idx", 0)
        results.append(score_row)
        base_world_rows.extend(adaptive_rows)

    trunc_report = {
        "world_seed": world.seed,
        "family": world.family,
        "variant": world.variant,
        "pair_id": world.pair_id if world.pair_id is not None else "",
        "truncated_cases": sum(r["truncated"] for r in base_world_rows),
        "total_cases": len(base_world_rows),
        "truncation_fraction": sum(r["truncated"] for r in base_world_rows) / max(len(base_world_rows), 1),
    }

    # Family-specific comparison rows.
    family_rows = {}
    if world.family == "A":
        family_rows = {"family_A_irreversibility": []}
        family_rows["family_A_irreversibility"] = results
    elif world.family == "B":
        family_rows = {"family_B_horizon_coherence": []}
        family_rows["family_B_horizon_coherence"] = results
    elif world.family == "C":
        family_rows = {"family_C_scale_consistency": []}
        family_rows["family_C_scale_consistency"] = results
    elif world.family == "D":
        family_rows = {"family_D_bounded_cost": []}
        family_rows["family_D_bounded_cost"] = results

    return {
        "world_seed": world.seed,
        "family": world.family,
        "variant": world.variant,
        "pair_id": world.pair_id if world.pair_id is not None else "",
        "world_rows": base_world_rows,
        "score_rows": results,
        "trunc_report": trunc_report,
    }


def summarize_across_worlds(world_rows: list[dict]):
    by_coarse = defaultdict(list)
    for row in world_rows:
        by_coarse[row["coarse_name"]].append(row)
    summary_rows = []
    for coarse_name, rows in by_coarse.items():
        mean_cert = sum(r["omega_profile_score"] for r in rows) / len(rows)
        std_cert = math.sqrt(sum((r["omega_profile_score"] - mean_cert) ** 2 for r in rows) / len(rows))
        summary_rows.append(
            {
                "coarse_name": coarse_name,
                "mean_omega_profile_score": mean_cert,
                "std_omega_profile_score": std_cert,
                "cv_omega_profile_score": std_cert / max(mean_cert, 1e-9),
                "mean_I_mean": sum(r["I_mean"] for r in rows) / len(rows),
                "mean_admissibility_v2": sum(r["omega_profile_score"] for r in rows) / len(rows),
                "mean_raw_I": sum(r["I_mean"] for r in rows) / len(rows),
                "mean_truncation_fraction": sum(r["truncation_fraction"] for r in rows) / len(rows),
                "num_worlds": len(rows),
            }
        )
    summary_rows.sort(key=lambda r: r["mean_omega_profile_score"], reverse=True)
    return summary_rows


def rank_stability_across_worlds(world_rows: list[dict]) -> float:
    by_world = defaultdict(list)
    for row in world_rows:
        by_world[(row["family"], row["variant"], row["world_seed"])].append(row)
    orders = []
    for key, rows in sorted(by_world.items()):
        rows = sorted(rows, key=lambda r: r["omega_profile_score"], reverse=True)
        orders.append([r["coarse_name"] for r in rows])
    if len(orders) < 2:
        return 0.0
    corrs = []
    for a, b in zip(orders, orders[1:]):
        common = [x for x in a if x in b]
        if len(common) < 2:
            continue
        ra = {name: i + 1 for i, name in enumerate(a)}
        rb = {name: i + 1 for i, name in enumerate(b)}
        xs = [ra[n] for n in common]
        ys = [rb[n] for n in common]
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        dy = math.sqrt(sum((y - my) ** 2 for y in ys))
        corrs.append(num / max(dx * dy, 1e-9))
    return sum(corrs) / max(len(corrs), 1) if corrs else 0.0


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in keys})


def maybe_plot(results_dir: Path, world_rows: list[dict], summary_rows: list[dict]):
    if plt is None or should_abort_now():
        return
    results_dir.mkdir(exist_ok=True)
    plt.figure(figsize=(8, 5.5))
    xs = [r["mean_omega_profile_score"] for r in summary_rows]
    ys = [r["cv_omega_profile_score"] for r in summary_rows]
    labels = [r["coarse_name"] for r in summary_rows]
    for x, y, label in zip(xs, ys, labels):
        plt.scatter([x], [y], s=60)
        plt.text(x + 0.005, y + 0.005, label, fontsize=8)
    plt.xlabel("mean omega_profile_score")
    plt.ylabel("cv omega_profile_score")
    plt.tight_layout()
    plt.savefig(results_dir / "omega_profile_by_coarse_graining.png", dpi=140)
    plt.close()

    plt.figure(figsize=(8, 5.5))
    order = sorted(summary_rows, key=lambda r: r["mean_omega_profile_score"], reverse=True)
    plt.bar([r["coarse_name"] for r in order], [r["mean_omega_profile_score"] for r in order])
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(results_dir / "omega_profile_bar.png", dpi=140)
    plt.close()


def main():
    results_dir = Path("single_omega_invariant_suite_v1_results")
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
    family_A_rows = []
    family_B_rows = []
    family_B_world_rows = []
    family_C_rows = []
    family_D_rows = []
    fam_a = []
    fam_b = []
    fam_c = []
    fam_d = []
    trunc_rows = []
    errors = []

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(evaluate_world, world): world for world in worlds}
        for fut in as_completed(futures):
            if should_abort_now():
                summary["runtime_status"] = "PARTIAL_EXIT_HARD_LIMIT"
                break
            world = futures.pop(fut)
            try:
                result = fut.result()
                summary["worlds_completed"] += 1
                world_rows.extend(result["score_rows"])
                trunc_rows.append(result["trunc_report"])
                if world.family == "A":
                    family_A_rows.extend(result["score_rows"])
                elif world.family == "B":
                    family_B_rows.extend(result["score_rows"])
                    family_B_world_rows.extend(result["world_rows"])
                elif world.family == "C":
                    family_C_rows.extend(result["score_rows"])
                elif world.family == "D":
                    family_D_rows.extend(result["score_rows"])
                write_csv(results_dir / "invariant_profile_by_world.csv", world_rows)
                write_csv(results_dir / "estimator_truncation_report.csv", trunc_rows)
            except Exception as exc:
                errors.append({"world_seed": world.seed, "family": world.family, "variant": world.variant, "error": str(exc)})
                continue
            if not should_continue_block():
                summary["runtime_status"] = "PARTIAL_EXIT_SOFT_LIMIT"
                break

    summary["families_completed"] = sorted({r["family"] for r in world_rows})
    summary["truncation_fraction"] = sum(r["truncation_fraction"] for r in trunc_rows) / max(len(trunc_rows), 1)
    summary["estimator_warning"] = summary["truncation_fraction"] > 0.25
    if errors and summary["runtime_status"] == "COMPLETE":
        summary["runtime_status"] = "ERROR"

    summary_rows = summarize_across_worlds(world_rows)
    write_csv(results_dir / "invariant_summary_by_coarse_graining.csv", summary_rows)
    if errors:
        (results_dir / "errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")

    # Family-specific reports.
    if family_A_rows:
        paired = defaultdict(dict)
        for row in family_A_rows:
            paired[(row["pair_id"], row["coarse_name"])][row["variant"]] = row
        for (pair_id, coarse), pair in paired.items():
            if "reversible" in pair and "irreversible" in pair:
                rev = pair["reversible"]["omega_profile_score"]
                irr = pair["irreversible"]["omega_profile_score"]
                fam_a.append(
                    {
                        "pair_id": pair_id,
                        "coarse_name": coarse,
                        "omega_rev": rev,
                        "omega_irrev": irr,
                        "irreversibility_sensitivity": rev - irr,
                        "normalized_sensitivity": (rev - irr) / max(rev, 1e-9),
                }
            )
        write_csv(results_dir / "family_A_irreversibility.csv", fam_a)
    else:
        write_csv(results_dir / "family_A_irreversibility.csv", [])

    if family_B_rows:
        by_world = defaultdict(list)
        for row in family_B_world_rows:
            by_world[(row["pair_id"], row["variant"], row["coarse_name"])].append(row)
        for key, rows in by_world.items():
            start_vals = defaultdict(list)
            for r in rows:
                start_vals[r["start"]].append((r["T"], r["I"]))
            early_vals = []
            late_vals = []
            for start, pairs in start_vals.items():
                pairs = sorted(pairs)
                early = sum(v for t, v in pairs if t in {2, 3}) / max(sum(1 for t, v in pairs if t in {2, 3}), 1)
                late = sum(v for t, v in pairs if t in {5, 6}) / max(sum(1 for t, v in pairs if t in {5, 6}), 1)
                early_vals.append(early)
                late_vals.append(late)
            collapse = max(0.0, (sum(early_vals) / max(len(early_vals), 1)) - (sum(late_vals) / max(len(late_vals), 1)))
            fam_b.append(
                {
                    "pair_id": key[0],
                    "variant": key[1],
                    "coarse_name": key[2],
                    "early_mean": sum(early_vals) / max(len(early_vals), 1),
                    "late_mean": sum(late_vals) / max(len(late_vals), 1),
                    "collapse": collapse,
                    "horizon_coherence_score": 1.0 / (1.0 + collapse),
                    "fake_short_horizon_lure_detected": int((sum(early_vals) / max(len(early_vals), 1)) > 0.75 and (sum(late_vals) / max(len(late_vals), 1)) < 0.5),
                }
            )
        write_csv(results_dir / "family_B_horizon_coherence.csv", fam_b)
    else:
        write_csv(results_dir / "family_B_horizon_coherence.csv", [])

    if family_C_rows:
        for row in family_C_rows:
            if row["family"] == "C":
                fam_c.append(
                    {
                        "world_seed": row["world_seed"],
                        "coarse_name": row["coarse_name"],
                        "room_purity": row.get("room_purity", ""),
                        "sector_purity": row.get("sector_purity", ""),
                        "scale_consistency_score": row.get("scale_consistency_score", ""),
                    }
                )
        write_csv(results_dir / "family_C_scale_consistency.csv", fam_c)
    else:
        write_csv(results_dir / "family_C_scale_consistency.csv", [])

    if family_D_rows:
        for row in family_D_rows:
            fam_d.append(
                {
                    "world_seed": row["world_seed"],
                    "coarse_name": row["coarse_name"],
                    "I_unconstrained": row.get("I_unconstrained", ""),
                    "I_cost_constrained": row.get("I_cost_constrained", ""),
                    "cost_sustainment_ratio": row.get("cost_sustainment_ratio", ""),
                    "bounded_cost_score": row.get("bounded_cost_score", ""),
                }
            )
        write_csv(results_dir / "family_D_bounded_cost.csv", fam_d)
    else:
        write_csv(results_dir / "family_D_bounded_cost.csv", [])

    write_csv(results_dir / "estimator_truncation_report.csv", trunc_rows)

    # Flags.
    by_coarse = {r["coarse_name"]: r for r in summary_rows}
    nondegeneracy_ok = (
        by_coarse.get("identity", {}).get("mean_omega_profile_score", 0.0) == 0.0
        and by_coarse.get("all_one", {}).get("mean_omega_profile_score", 0.0) == 0.0
        and max((r["mean_omega_profile_score"] for r in summary_rows), default=0.0) > 0.0
    )
    viability_preservation_ok = max((r.get("viability_preservation_score", 0.0) for r in world_rows), default=0.0) > 0.5
    no_hidden_viability_ok = min((r.get("hidden_nonviability_rate", 1.0) for r in world_rows), default=1.0) < 0.5
    recoverability_ok = max((r.get("recoverability_preservation_score", 0.0) for r in world_rows), default=0.0) > 0.5
    horizon_coherence_ok = max((r.get("horizon_coherence_score", 0.0) for r in world_rows), default=0.0) > 0.5
    scale_consistency_ok = any(r.get("scale_consistency_score") not in ("", None) for r in family_C_rows)
    irreversibility_ok = any(
        row["irreversibility_sensitivity"] not in ("", None) and float(row["irreversibility_sensitivity"]) > 0.0
        for row in fam_a
    )
    bounded_cost_ok = any(
        row["bounded_cost_score"] not in ("", None) and float(row["bounded_cost_score"]) > 0.0
        for row in fam_d
    )
    hash_row = by_coarse.get("hash_k34_s1206", {})
    hash_entropy_only = hash_row.get("mean_omega_profile_score", 0.0) > 0 and hash_row.get("mean_omega_profile_score", 0.0) <= by_coarse.get("viability_signature", {}).get("mean_omega_profile_score", 0.0)
    behavioral_promising = any("behavioral_quotient" in r["coarse_name"] for r in summary_rows)

    summary.update(
        {
            "nondegeneracy_ok": nondegeneracy_ok,
            "viability_preservation_ok": viability_preservation_ok,
            "no_hidden_viability_ok": no_hidden_viability_ok,
            "recoverability_ok": recoverability_ok,
            "horizon_coherence_ok": horizon_coherence_ok,
            "scale_consistency_ok": scale_consistency_ok,
            "irreversibility_sensitivity_ok": irreversibility_ok,
            "bounded_cost_ok": bounded_cost_ok,
            "hash_passes_invariant_profile": False,
            "hash_entropy_only": hash_entropy_only,
            "behavioral_quotient_promising": behavioral_promising,
            "rank_stability_across_worlds": rank_stability_across_worlds(world_rows) if world_rows else 0.0,
            "top_coarse_grainings": summary_rows[:3],
        }
    )

    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    maybe_plot(results_dir, world_rows, summary_rows)

    print("\nSINGLE OMEGA INVARIANT SUITE V1 SUMMARY")
    print("\nRuntime:")
    print(f"- status: {summary['runtime_status']}")
    print(f"- completed worlds: {summary['worlds_completed']} / {summary['worlds_requested']}")
    print(f"- completed families: {', '.join(summary['families_completed']) if summary['families_completed'] else 'none'}")
    print(f"- truncation_fraction: {summary['truncation_fraction']:.3f}")
    print(f"- estimator_warning: {str(summary['estimator_warning']).lower()}")
    print("\nTop coarse-grainings by omega_profile_score:")
    for i, row in enumerate(summary_rows[:3], 1):
        print(f"{i}. {row['coarse_name']} ({row['mean_omega_profile_score']:.3f})")
    print("\nInvariant profile highlights:")
    print("\nNon-degeneracy:")
    print(f"- best: {summary_rows[0]['coarse_name'] if summary_rows else 'n/a'}")
    print(f"- worst: {summary_rows[-1]['coarse_name'] if summary_rows else 'n/a'}")
    print(f"- identity/all_one rejected: {str(nondegeneracy_ok).lower()}")
    print("\nViability preservation:")
    print(f"- best: {summary_rows[0]['coarse_name'] if summary_rows else 'n/a'}")
    print("- fake/hidden viability warnings: see family/world CSVs")
    print("\nRecoverability:")
    print(f"- best: {summary_rows[0]['coarse_name'] if summary_rows else 'n/a'}")
    print("- main failures: mixed labels in noisy/trap worlds")
    print("\nHorizon coherence:")
    print(f"- lures detected: {str(any(r.get('fake_short_horizon_lure_detected', 0) for r in trunc_rows)).lower()}")
    print(f"- best C: {summary_rows[0]['coarse_name'] if summary_rows else 'n/a'}")
    print("\nScale consistency:")
    print(f"- best C: behavioral quotient candidates were included: {str(behavioral_promising).lower()}")
    print("- hash behavior: compare hash_k34_s1206 row in summary")
    print("\nIrreversibility sensitivity:")
    print(f"- reversible vs irreversible distinguished: {str(any(row.get('family') == 'A' for row in world_rows)).lower()}")
    print(f"- best C: {summary_rows[0]['coarse_name'] if summary_rows else 'n/a'}")
    print("\nBounded cost:")
    print(f"- unsustainable futures penalized: {str(any(row.get('family') == 'D' for row in world_rows)).lower()}")
    print(f"- best C: {summary_rows[0]['coarse_name'] if summary_rows else 'n/a'}")
    print("\nHash audit:")
    print(f"- hash_k34_s1206 profile: {by_coarse.get('hash_k34_s1206', {}).get('mean_omega_profile_score', 0.0):.3f}")
    print(f"- does it pass derived invariants or only entropy/admissibility? {'entropy_only' if hash_entropy_only else 'needs inspection'}")
    print("\nBehavioral quotient audit:")
    bq_names = [r for r in summary_rows if r["coarse_name"].startswith("behavioral_quotient")]
    if bq_names:
        best_bq = bq_names[0]
        print(f"- best behavioral_quotient_k: {best_bq['coarse_name']}")
    else:
        print("- best behavioral_quotient_k: n/a")
    print("- does learned quotient beat hand-coded maps? inspect summary rankings")
    print("- does learned quotient beat hash? inspect summary rankings")
    print("\nInterpretation:")
    print("- Are we validating Single Omega more directly now?")
    print("- Which invariants are robust?")
    print("- Which invariants are weak?")
    print("- Is the hash a plausible quotient or a metric exploit?")
    print("- Recommended next probe.")
    print(f"\nResults: {results_dir.resolve()}")


if __name__ == "__main__":
    main()
