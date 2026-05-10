from __future__ import annotations

import csv
import json
import math
import os
import random
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
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


SOFT_LIMIT_SECONDS = 540
HARD_LIMIT_SECONDS = 600
MAX_TRAJ_PER_STATE = 18000
MAX_ENERGY = 4
INITIAL_ENERGY = 4
STARTS = [
    "open",
    "noise_swamp",
    "bottleneck",
    "loop",
    "resource_corridor",
    "dead_branch",
    "near_trap",
    "rigid_attractor",
]
HORIZONS = [2, 3, 4, 5, 6]
ACTIONS = ["U", "D", "L", "R", "WAIT"]
N_ADVERSARIAL = 50

GRID_ROWS = [
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
WIDTH = len(GRID_ROWS[0])
HEIGHT = len(GRID_ROWS)
STATE_SPACE = [(x, y, e) for y in range(HEIGHT) for x in range(WIDTH) for e in range(MAX_ENERGY + 1)]
START_TIME = time.time()


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


def timed_out() -> bool:
    return should_abort_now()


def region_xy(x: int, y: int) -> str:
    if x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT:
        return "#"
    return GRID_ROWS[y][x]


def region(state: tuple[int, int, int]) -> str:
    x, y, _ = state
    return region_xy(x, y)


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for count in counts.values():
        p = count / total
        h -= p * math.log(p)
    return h


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


def apply_cell_rules(x: int, y: int, energy: int, action: str) -> tuple[int, int, int]:
    current = region_xy(x, y)
    nx, ny = move_xy(x, y, action)
    if region_xy(nx, ny) == "#":
        nx, ny = x, y
    next_region = region_xy(nx, ny)

    if current == "T" or next_region == "T":
        return nx, ny, 0

    if current in {"R", "A"}:
        return x, y, max(1, energy)

    if action == "WAIT":
        cost = 1 if current == "D" else 0
    else:
        cost = 2 if current == "D" else 1

    new_energy = max(0, energy - cost)
    if next_region == "C":
        new_energy = min(MAX_ENERGY, new_energy + 1)
    if next_region in {"R", "A"}:
        new_energy = max(1, new_energy)
    return nx, ny, new_energy


def transition(state: tuple[int, int, int], action: str) -> list[tuple[tuple[int, int, int], float]]:
    x, y, energy = state
    current = region_xy(x, y)
    if current in {"R", "A", "T"}:
        return [(apply_cell_rules(x, y, energy, action), 1.0)]

    candidate_actions = [action]
    if current == "S":
        if action in {"U", "D"}:
            candidate_actions = [action, "L", "R", "WAIT"]
        elif action in {"L", "R"}:
            candidate_actions = [action, "U", "D", "WAIT"]
        else:
            candidate_actions = ["U", "D", "L", "R", "WAIT"]
    elif current == "D" and action != "WAIT":
        candidate_actions = [action, "WAIT"]

    prob = 1.0 / len(candidate_actions)
    return [(apply_cell_rules(x, y, energy, a), prob) for a in candidate_actions]


def viable_transition(next_state: tuple[int, int, int]) -> bool:
    return next_state[2] > 0 and region(next_state) != "T"


def enumerate_trajectories(
    start_state: tuple[int, int, int], horizon: int
) -> tuple[list[tuple[tuple[tuple[int, int, int], ...], bool]], bool]:
    trajectories = [((start_state,), viable_transition(start_state))]
    truncated = False
    for _ in range(horizon):
        new_trajectories = []
        for states, still_viable in trajectories:
            if timed_out() or len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                truncated = truncated or len(new_trajectories) >= MAX_TRAJ_PER_STATE
                break
            state = states[-1]
            for action in ACTIONS:
                for next_state, _ in transition(state, action):
                    new_trajectories.append((states + (next_state,), still_viable and viable_transition(next_state)))
                    if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                        truncated = True
                        break
                if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                    break
        trajectories = new_trajectories[:MAX_TRAJ_PER_STATE]
        if timed_out():
            truncated = True
            break
    return trajectories, truncated


def trap_distance_bin(state: tuple[int, int, int]) -> str:
    x, y, _ = state
    traps = [(tx, ty) for ty, row in enumerate(GRID_ROWS) for tx, c in enumerate(row) if c == "T"]
    distance = min(abs(x - tx) + abs(y - ty) for tx, ty in traps)
    return "near" if distance <= 2 else "far"


def local_branching_bin(state: tuple[int, int, int]) -> str:
    count = 0
    for action in ACTIONS:
        for next_state, _ in transition(state, action):
            if viable_transition(next_state):
                count += 1
    if count <= 2:
        return "low"
    if count <= 6:
        return "med"
    return "high"


def one_step_viable_fraction(state: tuple[int, int, int]) -> float:
    outcomes = []
    for action in ACTIONS:
        for next_state, prob in transition(state, action):
            outcomes.append((viable_transition(next_state), prob))
    total = sum(prob for _, prob in outcomes)
    if total <= 0:
        return 0.0
    return sum(prob for viable, prob in outcomes if viable) / total


def next_macro_distribution(state: tuple[int, int, int], coarse_grain) -> Counter:
    dist = Counter()
    for action in ACTIONS:
        for next_state, prob in transition(state, action):
            dist[coarse_grain(next_state)] += prob
    total = sum(dist.values())
    if total > 0:
        for key in list(dist):
            dist[key] /= total
    return dist


def l1_distance(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)


def find_cell(label: str, preferred: tuple[int, int] | None = None) -> tuple[int, int, int]:
    if preferred is not None and region_xy(*preferred) == label:
        return preferred[0], preferred[1], INITIAL_ENERGY
    for y, row in enumerate(GRID_ROWS):
        for x, cell in enumerate(row):
            if cell == label:
                return x, y, INITIAL_ENERGY
    raise ValueError(f"no cell for {label}")


def representative_starts() -> dict[str, tuple[int, int, int]]:
    return {
        "open": find_cell("O", (2, 1)),
        "noise_swamp": find_cell("S", (6, 1)),
        "bottleneck": find_cell("B", (3, 3)),
        "loop": find_cell("L", (1, 4)),
        "resource_corridor": find_cell("C", (6, 4)),
        "dead_branch": find_cell("D", (1, 6)),
        "near_trap": (1, 7, INITIAL_ENERGY),
        "rigid_attractor": find_cell("R", (6, 6)),
    }


START_STATE_MAP = representative_starts()


def coarse_region(state: tuple[int, int, int]) -> str:
    return region(state)


def coarse_viability_signature(state: tuple[int, int, int]) -> tuple[str, str, str]:
    _, _, energy = state
    if energy <= 1:
        energy_bin = "e_low"
    elif energy <= 3:
        energy_bin = "e_med"
    else:
        energy_bin = "e_high"
    return energy_bin, trap_distance_bin(state), local_branching_bin(state)


RNG = random.Random(7)
RANDOM_LABELS = {(x, y): f"q{RNG.randrange(5)}" for y in range(HEIGHT) for x in range(WIDTH)}


def coarse_random_5(state: tuple[int, int, int]) -> str:
    x, y, _ = state
    return RANDOM_LABELS[(x, y)]


def coarse_identity(state: tuple[int, int, int]) -> tuple[int, int, int]:
    return state


def coarse_all_one(state: tuple[int, int, int]) -> str:
    return "all_one"


def coarse_trap_mixing_adversarial(state: tuple[int, int, int]) -> str:
    x, y, _ = state
    r = region_xy(x, y)
    if r == "T" or trap_distance_bin(state) == "near":
        return f"mix{(x + y) % 2}"
    if r in {"O", ".", "S"}:
        return f"mix{(x + 2 * y) % 3}"
    return f"mix{(2 * x + y) % 4}"


def coarse_checkerboard(state: tuple[int, int, int]) -> int:
    x, y, _ = state
    return (x + y) % 2


def coarse_endpoint_only(states: tuple[tuple[int, int, int], ...]) -> str:
    return region(states[-1])


COARSE_GRAININGS = {
    "region": coarse_region,
    "viability_signature": coarse_viability_signature,
    "random_5": coarse_random_5,
    "identity": coarse_identity,
    "all_one": coarse_all_one,
    "trap_mixing_adversarial": coarse_trap_mixing_adversarial,
    "checkerboard": coarse_checkerboard,
}


def make_random_partition(labels: int, seed: int):
    rng = random.Random(seed)
    mapping = {state: rng.randrange(labels) for state in STATE_SPACE}
    return lambda state: mapping[state]


def make_hash_partition(labels: int, seed: int):
    a = 1 + (seed * 3) % 7
    b = 2 + (seed * 5) % 11
    c = 3 + (seed * 7) % 13
    return lambda state: ((a * state[0] + b * state[1] + c * state[2]) % labels)


def make_overfine_noisy(seed: int):
    rng = random.Random(seed)
    mapping = {}
    for state in STATE_SPACE:
        if rng.random() < 0.8:
            mapping[state] = state
        else:
            mapping[state] = ("n", rng.randrange(4))
    return lambda state: mapping[state]


def make_overbroad_noisy(seed: int):
    rng = random.Random(seed)
    rare = {}
    for state in STATE_SPACE:
        if rng.random() < 0.9:
            rare[state] = 0
        else:
            rare[state] = rng.randrange(5) + 1
    return lambda state: rare[state]


def evaluate_adversarial_candidate(args):
    kind, seed, trajectory_cache = args
    name, fn, _ = candidate_from_spec(kind, seed)
    rows, _ = compute_raw_metrics_for_coarse(name, fn, trajectory_cache)
    stats = compute_audit_stats(name, fn, rows)
    return {
        "coarse_name": name,
        "kind": kind,
        "seed": seed,
        "I_mean": stats["I_mean"],
        "admissibility_v2": stats["admissibility_v2"],
        "certified_I_v2": stats["certified_I_v2"],
        "compression_gate": stats["compression_gate"],
        "fiber_quality": stats["fiber_quality"],
        "viability_purity": stats["viability_purity"],
        "transition_consistency": stats["transition_consistency"],
    }


def smoke_row_job(args):
    coarse_name, start_name, horizon, budget, trajectory_cache = args
    coarse_fn = COARSE_GRAININGS[coarse_name]
    start_state = START_STATE_MAP[start_name]
    exact_i = exact_metric_for_single_case(coarse_name, coarse_fn, start_name, horizon, trajectory_cache)
    estimates = [
        sampled_I(
            start_state,
            horizon,
            coarse_name,
            coarse_fn,
            budget,
            seed=9000 + budget * 11 + rep * 3 + horizon,
        )
        for rep in range(3)
    ]
    mean_i = sum(estimates) / len(estimates)
    std_i = math.sqrt(sum((x - mean_i) ** 2 for x in estimates) / len(estimates))
    return {
        "coarse_name": coarse_name,
        "start": start_name,
        "T": horizon,
        "budget": budget,
        "exact_I": exact_i,
        "mean_I": mean_i,
        "std_I": std_i,
        "cv": std_i / max(mean_i, 1e-9),
    }


def compression_score(num_macro: int, num_micro: int) -> float:
    r = num_macro / max(num_micro, 1)
    if r <= 0.02:
        return 0.1
    if r <= 0.10:
        return 0.5
    if r <= 0.40:
        return 1.0
    if r <= 0.75:
        return 0.5
    return 0.1


def compression_gate(r: float) -> float:
    if r <= 0.01:
        return 0.0
    if r >= 0.75:
        return 0.0
    if 0.05 <= r <= 0.40:
        return 1.0
    if r < 0.05:
        return r / 0.05
    return (0.75 - r) / (0.75 - 0.40)


def rank_stability(raw_rows: list[dict]) -> float:
    by_horizon: dict[int, list[tuple[str, float]]] = defaultdict(list)
    for row in raw_rows:
        if row["T"] in {3, 4, 5, 6}:
            by_horizon[row["T"]].append((row["start"], row["I"]))
    if any(len(by_horizon.get(t, [])) < 2 for t in [3, 4, 5, 6]):
        return 0.0

    def ranks(items: list[tuple[str, float]]) -> dict[str, float]:
        items = sorted(items, key=lambda kv: kv[1])
        rank_map: dict[str, float] = {}
        i = 0
        while i < len(items):
            j = i
            while j < len(items) and abs(items[j][1] - items[i][1]) <= 1e-12:
                j += 1
            avg_rank = (i + 1 + j) / 2.0
            for k in range(i, j):
                rank_map[items[k][0]] = avg_rank
            i = j
        return rank_map

    corrs = []
    for t1, t2 in [(3, 4), (4, 5), (5, 6)]:
        r1 = ranks(by_horizon[t1])
        r2 = ranks(by_horizon[t2])
        xs = [r1[s] for s in STARTS]
        ys = [r2[s] for s in STARTS]
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        dy = math.sqrt(sum((y - my) ** 2 for y in ys))
        corrs.append(num / max(dx * dy, 1e-9))
    return sum(corrs) / len(corrs)


def trajectory_label(states: tuple[tuple[int, int, int], ...], coarse_name: str, coarse_fn) -> object:
    if coarse_name == "endpoint_only":
        return coarse_endpoint_only(states)
    return tuple(coarse_fn(state) for state in states)


def maybe_traj_state_mode(coarse_name: str) -> str:
    return "trajectory" if coarse_name == "endpoint_only" else "state"


def compute_raw_metrics_for_coarse(coarse_name: str, coarse_fn, trajectory_cache: dict) -> tuple[list[dict], bool]:
    rows = []
    truncated_any = False
    for start_name in STARTS:
        for horizon in HORIZONS:
            if timed_out():
                break
            trajectories, truncated = trajectory_cache[(start_name, horizon)]
            truncated_any = truncated_any or truncated
            viable = [tr for tr in trajectories if tr[1]]
            classes = Counter()
            for states, _ in viable:
                classes[trajectory_label(states, coarse_name, coarse_fn)] += 1
            omega = entropy(classes)
            rows.append(
                {
                    "coarse_name": coarse_name,
                    "mode": maybe_traj_state_mode(coarse_name),
                    "start": start_name,
                    "T": horizon,
                    "I": omega,
                    "N_eff": math.exp(omega),
                    "viable_count": len(viable),
                    "raw_count": len(trajectories),
                    "truncated": truncated,
                }
            )
    return rows, truncated_any


def exact_metric_for_single_case(coarse_name: str, coarse_fn, start_name: str, horizon: int, trajectory_cache: dict) -> float:
    trajectories, _ = trajectory_cache[(start_name, horizon)]
    viable = [tr for tr in trajectories if tr[1]]
    classes = Counter()
    for states, _ in viable:
        classes[trajectory_label(states, coarse_name, coarse_fn)] += 1
    return entropy(classes)


def compute_shared_trajectory_cache() -> dict:
    cache = {}
    for start_name in STARTS:
        for horizon in HORIZONS:
            if timed_out():
                break
            cache[(start_name, horizon)] = enumerate_trajectories(START_STATE_MAP[start_name], horizon)
        if timed_out():
            break
    return cache


def compute_audit_stats(coarse_name: str, coarse_fn, raw_rows: list[dict]) -> dict:
    state_mode = coarse_name != "endpoint_only"
    if not state_mode:
        return {
            "I_mean": sum(row["I"] for row in raw_rows) / max(len(raw_rows), 1),
            "I_max": max((row["I"] for row in raw_rows), default=0.0),
            "admissibility_v1": 0.0,
            "certified_I_v1": 0.0,
            "compression_score": 0.0,
            "viability_purity": 0.0,
            "transition_consistency": 0.0,
            "rank_stability": 0.0,
            "nontriviality_score": 0.0,
            "fiber_score": 0.0,
            "singleton_fraction": 0.0,
            "mean_fiber_size": 0.0,
            "fiber_quality": 0.0,
            "compression_gate": 0.0,
            "transport_nontriviality": 0.0,
            "admissibility_v2": 0.0,
            "certified_I_v2": 0.0,
            "label_count": 0,
            "micro_count": len(STATE_SPACE),
        }

    label_map = {coarse_fn(state) for state in STATE_SPACE}
    label_count = len(label_map)
    micro_count = len(STATE_SPACE)
    r = label_count / max(micro_count, 1)
    comp_score = compression_score(label_count, micro_count)
    comp_gate = compression_gate(r)

    groups: dict[object, list[tuple[tuple[int, int, int], float]]] = defaultdict(list)
    for state in STATE_SPACE:
        groups[coarse_fn(state)].append((state, one_step_viable_fraction(state)))

    fibers = [len(items) for items in groups.values()]
    mean_fiber_size = sum(fibers) / max(len(fibers), 1)
    singleton_fraction = sum(1 for x in fibers if x == 1) / max(len(fibers), 1)
    fiber_score = min(1.0, max(0.0, (mean_fiber_size - 1.0) / 4.0))
    fiber_quality = fiber_score * (1.0 - singleton_fraction)

    variances = []
    weights = []
    for _, items in groups.items():
        vals = [v for _, v in items]
        if len(vals) <= 1:
            variance = 0.0
        else:
            mu = sum(vals) / len(vals)
            variance = sum((v - mu) ** 2 for v in vals) / len(vals)
        variances.append(variance)
        weights.append(len(vals))
    weighted_mean_variance = sum(v * w for v, w in zip(variances, weights)) / max(sum(weights), 1)
    viability_purity = 1.0 / (1.0 + weighted_mean_variance)

    pairwise_values = []
    pairwise_weights = []
    for label, items in groups.items():
        if len(items) <= 1:
            pairwise_values.append(0.0)
            pairwise_weights.append(len(items))
            continue
        dists_cache = {state: next_macro_distribution(state, coarse_fn) for state, _ in items}
        dists = [l1_distance(dists_cache[s1], dists_cache[s2]) for (s1, _), (s2, _) in combinations(items, 2)]
        pairwise_values.append(sum(dists) / len(dists) if dists else 0.0)
        pairwise_weights.append(len(items))
    weighted_pairwise = sum(v * w for v, w in zip(pairwise_values, pairwise_weights)) / max(sum(pairwise_weights), 1)
    transition_consistency = 1.0 / (1.0 + weighted_pairwise)

    raw_mean = sum(row["I"] for row in raw_rows) / max(len(raw_rows), 1)
    nontriviality_score = min(1.0, raw_mean / 1.0)
    rank_stab = rank_stability(raw_rows)
    admissibility_v1 = comp_score * viability_purity * transition_consistency * max(rank_stab, 0.0) * nontriviality_score
    certified_v1 = raw_mean * admissibility_v1

    support_counts = []
    max_reasonable = min(8, label_count)
    for label, items in groups.items():
        support = set()
        for state, _ in items:
            for action in ACTIONS:
                for next_state, _ in transition(state, action):
                    if viable_transition(next_state):
                        support.add(coarse_fn(next_state))
        support_counts.append(1 if 1 <= len(support) <= max_reasonable else 0)
    transport_nontriviality = sum(support_counts) / max(len(support_counts), 1)

    structural_quality = viability_purity * transition_consistency * max(rank_stab, 0.0) * nontriviality_score
    admissibility_v2 = structural_quality * comp_gate * fiber_quality
    certified_v2 = raw_mean * admissibility_v2

    return {
        "I_mean": raw_mean,
        "I_max": max((row["I"] for row in raw_rows), default=0.0),
        "admissibility_v1": admissibility_v1,
        "certified_I_v1": certified_v1,
        "compression_score": comp_score,
        "viability_purity": viability_purity,
        "transition_consistency": transition_consistency,
        "rank_stability": rank_stab,
        "nontriviality_score": nontriviality_score,
        "fiber_score": fiber_score,
        "singleton_fraction": singleton_fraction,
        "mean_fiber_size": mean_fiber_size,
        "fiber_quality": fiber_quality,
        "compression_gate": comp_gate,
        "transport_nontriviality": transport_nontriviality,
        "admissibility_v2": admissibility_v2,
        "certified_I_v2": certified_v2,
        "label_count": label_count,
        "micro_count": micro_count,
    }


def print_probe_a(rows_by_name: dict[str, list[dict]], stats: dict[str, dict]) -> bool:
    print("\nPROBE A: certification_v2_anti_identity")
    headers = [
        "C_name",
        "I_mean",
        "I_max",
        "admiss_v1",
        "cert_v1",
        "comp",
        "purity",
        "trans",
        "rank",
        "nontriv",
        "fiber_q",
        "gate",
        "adm_v2",
        "cert_v2",
    ]
    print(" | ".join(headers))
    print(" | ".join("-" * len(h) for h in headers))
    for name in [
        "region",
        "viability_signature",
        "random_5",
        "identity",
        "all_one",
        "trap_mixing_adversarial",
        "endpoint_only",
        "checkerboard",
    ]:
        if name not in stats:
            continue
        s = stats[name]
        print(
            f"{name} | {s['I_mean']:.3f} | {s['I_max']:.3f} | {s['admissibility_v1']:.3f} | {s['certified_I_v1']:.3f} | "
            f"{s['compression_score']:.3f} | {s['viability_purity']:.3f} | {s['transition_consistency']:.3f} | {s['rank_stability']:.3f} | "
            f"{s['nontriviality_score']:.3f} | {s['fiber_quality']:.3f} | {s['compression_gate']:.3f} | {s['admissibility_v2']:.3f} | {s['certified_I_v2']:.3f}"
        )
    ranked = sorted([(n, stats[n]["certified_I_v2"]) for n in stats if n in COARSE_AUDIT_NAMES], key=lambda kv: kv[1], reverse=True)
    print("\nRank by certified_I_v2:")
    for i, (name, _) in enumerate(ranked, 1):
        print(f"{i}. {name}")

    anti_identity_ok = (
        stats["identity"]["certified_I_v2"] <= max(stats["region"]["certified_I_v2"], stats["viability_signature"]["certified_I_v2"]) * 1.05
        and stats["all_one"]["certified_I_v2"] == 0.0
        and stats["random_5"]["certified_I_v2"] < stats["region"]["certified_I_v2"]
        and stats["trap_mixing_adversarial"]["certified_I_v2"] < stats["region"]["certified_I_v2"]
        and max(stats["region"]["certified_I_v2"], stats["viability_signature"]["certified_I_v2"]) >= max(stats["random_5"]["certified_I_v2"], stats["identity"]["certified_I_v2"])
    )
    print(f"\nANTI_IDENTITY_GATE_OK = {str(anti_identity_ok).lower()}")
    return anti_identity_ok


COARSE_AUDIT_NAMES = [
    "region",
    "viability_signature",
    "random_5",
    "identity",
    "all_one",
    "trap_mixing_adversarial",
    "endpoint_only",
    "checkerboard",
]


def candidate_from_spec(kind: str, seed: int):
    if kind == "random":
        k = [2, 3, 5, 8, 13, 21, 34, 55][seed % 8]
        return f"random_k{k}_s{seed}", make_random_partition(k, seed), "state"
    if kind == "hash":
        k = [2, 3, 5, 8, 13, 21, 34, 55][seed % 8]
        return f"hash_k{k}_s{seed}", make_hash_partition(k, seed), "state"
    if kind == "trapmix":
        return f"trapmix_s{seed}", make_trap_mixing_candidate(seed), "state"
    if kind == "overfine":
        return f"overfine_s{seed}", make_overfine_noisy(seed), "state"
    if kind == "overbroad":
        return f"overbroad_s{seed}", make_overbroad_noisy(seed), "state"
    raise ValueError(kind)


def make_trap_mixing_candidate(seed: int):
    rng = random.Random(seed)
    palette = [0, 1, 2, 3]
    mapping = {}
    for state in STATE_SPACE:
        r = region(state)
        if r == "T" or trap_distance_bin(state) == "near":
            mapping[state] = palette[(state[0] + state[1] + seed) % 2]
        elif r in {"O", ".", "S"}:
            mapping[state] = palette[(2 * state[0] + state[1] + seed) % 3]
        else:
            mapping[state] = palette[(state[0] + 2 * state[1] + seed) % 4]
    return lambda state: mapping[state]


def compute_probe_b(trajectory_cache: dict, base_stats: dict) -> list[dict]:
    print("\nPROBE B: adversarial_coarse_graining_sweep")
    candidates = []
    kinds = ["random", "hash", "trapmix", "overfine", "overbroad"]
    per_kind = max(1, math.ceil(N_ADVERSARIAL / len(kinds)))
    jobs = []
    for kind in kinds:
        for i in range(per_kind):
            seed = 1000 + len(jobs) * 17 + i
            jobs.append((kind, seed, trajectory_cache))
            if len(jobs) >= N_ADVERSARIAL:
                break
        if len(jobs) >= N_ADVERSARIAL:
            break

    max_workers = min(8, os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(evaluate_adversarial_candidate, job) for job in jobs]
        for fut in as_completed(futures):
            if timed_out():
                break
            candidates.append(fut.result())

    region_cert = base_stats.get("region_certified_I_v2", 0.0)
    viability_cert = base_stats.get("viability_signature_certified_I_v2", 0.0)
    certs = sorted(c["certified_I_v2"] for c in candidates)
    def percentile(x: float) -> float:
        if not certs:
            return 0.0
        below = sum(1 for c in certs if c <= x)
        return 100.0 * below / len(certs)

    best = max(candidates, key=lambda c: c["certified_I_v2"], default=None)
    region_pct = percentile(region_cert)
    viability_pct = percentile(viability_cert)
    print(f"Candidates completed: {len(candidates)}")
    print(f"Region percentile: {region_pct:.1f}")
    print(f"Viability_signature percentile: {viability_pct:.1f}")
    if best:
        print(
            f"Best adversarial candidate: {best['coarse_name']} "
            f"certified_I_v2={best['certified_I_v2']:.3f} admiss={best['admissibility_v2']:.3f}"
        )
    adversarial_winner = bool(best and best["certified_I_v2"] > max(region_cert, viability_cert))
    print(f"ADVERSARIAL_WINNER_FOUND = {str(adversarial_winner).lower()}")
    return candidates


def sample_trajectories(start_state, horizon, budget, seed):
    rng = random.Random(seed)
    samples = []
    for _ in range(budget):
        states = [start_state]
        viable = viable_transition(start_state)
        state = start_state
        for _ in range(horizon):
            action = rng.choice(ACTIONS)
            outs = transition(state, action)
            next_states = [ns for ns, _ in outs]
            probs = [p for _, p in outs]
            roll = rng.random()
            acc = 0.0
            next_state = next_states[-1]
            for ns, p in zip(next_states, probs):
                acc += p
                if roll <= acc:
                    next_state = ns
                    break
            states.append(next_state)
            viable = viable and viable_transition(next_state)
            state = next_state
        samples.append((tuple(states), viable))
    return samples


def sampled_I(start_state, horizon, coarse_name, coarse_fn, budget, seed):
    if coarse_name == "endpoint_only":
        return 0.0
    samples = sample_trajectories(start_state, horizon, budget, seed)
    classes = Counter()
    for states, viable in samples:
        if viable:
            classes[trajectory_label(states, coarse_name, coarse_fn)] += 1
    return entropy(classes)


def compute_probe_c(base_stats: dict, trajectory_cache: dict) -> list[dict]:
    print("\nPROBE C: estimator_smoke_check")
    budgets = [300, 1000, 3000]
    repeats = 3
    jobs = []
    for coarse_name in ["region", "viability_signature"]:
        for start_name in ["open", "loop", "dead_branch", "rigid_attractor"]:
            for horizon in [3, 4, 5]:
                for budget in budgets:
                    jobs.append((coarse_name, start_name, horizon, budget, trajectory_cache))

    rows = []
    max_workers = min(8, os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(smoke_row_job, job) for job in jobs]
        for fut in as_completed(futures):
            if timed_out():
                break
            rows.append(fut.result())

    rank_rows = []
    for coarse_name in ["region", "viability_signature"]:
        for horizon in [3, 4, 5]:
            per_budget_rank_orders = []
            cv_values = []
            for budget in budgets:
                start_scores = []
                for start_name in ["open", "loop", "dead_branch", "rigid_attractor"]:
                    match_rows = [r for r in rows if r["coarse_name"] == coarse_name and r["T"] == horizon and r["budget"] == budget and r["start"] == start_name]
                    if not match_rows:
                        continue
                    mean_i = sum(r["mean_I"] for r in match_rows) / len(match_rows)
                    start_scores.append((start_name, mean_i))
                    cv_values.extend(r["cv"] for r in match_rows)
                per_budget_rank_orders.append([name for name, _ in sorted(start_scores, key=lambda kv: kv[1], reverse=True)])
            stability_scores = []
            for i in range(len(per_budget_rank_orders) - 1):
                a = per_budget_rank_orders[i]
                b = per_budget_rank_orders[i + 1]
                if len(a) < 4 or len(b) < 4:
                    continue
                order_a = {name: idx + 1 for idx, name in enumerate(a)}
                order_b = {name: idx + 1 for idx, name in enumerate(b)}
                xs = [order_a[n] for n in ["open", "loop", "dead_branch", "rigid_attractor"]]
                ys = [order_b[n] for n in ["open", "loop", "dead_branch", "rigid_attractor"]]
                mx = sum(xs) / len(xs)
                my = sum(ys) / len(ys)
                num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
                dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
                dy = math.sqrt(sum((y - my) ** 2 for y in ys))
                stability_scores.append(num / max(dx * dy, 1e-9))
            rank_rows.append(
                {
                    "coarse_name": coarse_name,
                    "T": horizon,
                    "rank_stability_across_sample_budgets": sum(stability_scores) / max(len(stability_scores), 1),
                    "mean_CV": sum(cv_values) / max(len(cv_values), 1),
                    "completed": True,
                }
            )
    print(f"Probe C rows: {len(rows)}")
    return rows + rank_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in keys})


def maybe_plot(results_dir: Path, probe_a_rows: list[dict], probe_b_rows: list[dict]) -> None:
    if plt is None or should_abort_now():
        return
    results_dir.mkdir(parents=True, exist_ok=True)
    xs = [r["I_mean"] for r in probe_a_rows if r["coarse_name"] in COARSE_AUDIT_NAMES]
    ys = [r["admissibility_v2"] for r in probe_a_rows if r["coarse_name"] in COARSE_AUDIT_NAMES]
    labels = [r["coarse_name"] for r in probe_a_rows if r["coarse_name"] in COARSE_AUDIT_NAMES]
    plt.figure(figsize=(7.5, 5.5))
    for x, y, label in zip(xs, ys, labels):
        plt.scatter([x], [y], s=65)
        plt.text(x + 0.01, y + 0.01, label, fontsize=8)
    plt.xlabel("raw I_mean")
    plt.ylabel("admissibility_v2")
    plt.tight_layout()
    plt.savefig(results_dir / "raw_I_vs_admissibility_v2.png", dpi=140)
    plt.close()

    plt.figure(figsize=(7.5, 5.5))
    order = sorted([r for r in probe_a_rows if r["coarse_name"] in COARSE_AUDIT_NAMES], key=lambda r: r["certified_I_v2"], reverse=True)
    plt.bar([r["coarse_name"] for r in order], [r["certified_I_v1"] for r in order], alpha=0.6, label="v1")
    plt.bar([r["coarse_name"] for r in order], [r["certified_I_v2"] for r in order], alpha=0.6, label="v2")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("certified_I")
    plt.legend()
    plt.tight_layout()
    plt.savefig(results_dir / "certified_I_v1_vs_v2.png", dpi=140)
    plt.close()

    if probe_b_rows:
        plt.figure(figsize=(7.5, 5.5))
        xs = [r["I_mean"] for r in probe_b_rows]
        ys = [r["certified_I_v2"] for r in probe_b_rows]
        cs = [r["kind"] for r in probe_b_rows]
        color_map = {"random": "tab:blue", "hash": "tab:orange", "trapmix": "tab:red", "overfine": "tab:green", "overbroad": "tab:purple"}
        for x, y, kind in zip(xs, ys, cs):
            plt.scatter([x], [y], color=color_map.get(kind, "black"), s=40, alpha=0.85)
        plt.xlabel("raw I_mean")
        plt.ylabel("certified_I_v2")
        plt.tight_layout()
        plt.savefig(results_dir / "adversarial_sweep_scatter.png", dpi=140)
        plt.close()


def main() -> None:
    results_dir = Path("omega_probe_batch_03_results")
    results_dir.mkdir(exist_ok=True)
    overall_status = status_code()
    blocks_completed = []
    blocks_skipped = []
    probe_a_rows = []
    probe_b_rows = []
    probe_c_rows = []
    summary = {
        "runtime_status": overall_status,
        "soft_limit_seconds": SOFT_LIMIT_SECONDS,
        "hard_limit_seconds": HARD_LIMIT_SECONDS,
        "blocks_completed": [],
        "blocks_skipped": [],
        "probe_a": {},
        "probe_b": {},
        "probe_c": {},
    }
    try:
        trajectory_cache = compute_shared_trajectory_cache()
        if should_continue_block() and not should_abort_now():
            raw_rows_by_name = {}
            stats = {}
            # Probe A
            probe_a_specs = {
                "region": coarse_region,
                "viability_signature": coarse_viability_signature,
                "random_5": coarse_random_5,
                "identity": coarse_identity,
                "all_one": coarse_all_one,
                "trap_mixing_adversarial": coarse_trap_mixing_adversarial,
                "endpoint_only": coarse_region,
                "checkerboard": coarse_checkerboard,
            }
            for name, fn in probe_a_specs.items():
                if should_abort_now():
                    break
                if name == "endpoint_only":
                    rows = []
                    for start_name in STARTS:
                        for horizon in HORIZONS:
                            trajectories, truncated = trajectory_cache[(start_name, horizon)]
                            viable = [tr for tr in trajectories if tr[1]]
                            classes = Counter(coarse_endpoint_only(states) for states, _ in viable)
                            rows.append(
                                {
                                    "coarse_name": name,
                                    "mode": "trajectory",
                                    "start": start_name,
                                    "T": horizon,
                                    "I": entropy(classes),
                                    "N_eff": math.exp(entropy(classes)),
                                    "viable_count": len(viable),
                                    "raw_count": len(trajectories),
                                    "truncated": truncated,
                                }
                            )
                    raw_rows_by_name[name] = rows
                    stats[name] = compute_audit_stats(name, fn, rows)
                    continue
                rows, _ = compute_raw_metrics_for_coarse(name, fn, trajectory_cache)
                raw_rows_by_name[name] = rows
                stats[name] = compute_audit_stats(name, fn, rows)
            probe_a_rows = [dict({"coarse_name": k}, **stats[k]) for k in stats]
            blocks_completed.append("A")
            summary["probe_a"] = {
                "completed": True,
                "anti_identity_gate_ok": print_probe_a(raw_rows_by_name, stats),
                "top_certified_I_v2": sorted(
                    ((name, stats[name]["certified_I_v2"]) for name in stats if name in COARSE_AUDIT_NAMES),
                    key=lambda kv: kv[1],
                    reverse=True,
                )[:3],
                "identity_raw_I": stats["identity"]["I_mean"],
                "identity_certified_I_v2": stats["identity"]["certified_I_v2"],
                "region_certified_I_v2": stats["region"]["certified_I_v2"],
                "viability_signature_certified_I_v2": stats["viability_signature"]["certified_I_v2"],
            }
        else:
            blocks_skipped.append("A")

        if should_continue_block() and not should_abort_now():
            probe_b_rows = compute_probe_b(trajectory_cache, summary.get("probe_a", {}))
            blocks_completed.append("B")
            region_cert = summary["probe_a"].get("region_certified_I_v2", 0.0)
            viability_cert = summary["probe_a"].get("viability_signature_certified_I_v2", 0.0)
            def percentile(value: float) -> float:
                return 100.0 * sum(1 for r in probe_b_rows if r["certified_I_v2"] <= value) / max(len(probe_b_rows), 1)
            best_adv = max(probe_b_rows, key=lambda r: r["certified_I_v2"], default=None)
            summary["probe_b"] = {
                "completed": True,
                "candidates_completed": len(probe_b_rows),
                "best_adversarial_certified_I_v2": best_adv["certified_I_v2"] if best_adv else 0.0,
                "region_percentile": percentile(region_cert),
                "viability_signature_percentile": percentile(viability_cert),
                "adversarial_winner_found": bool(best_adv and best_adv["certified_I_v2"] > max(region_cert, viability_cert)),
                "best_candidate": best_adv,
            }
        else:
            blocks_skipped.append("B")

        if should_continue_block() and not should_abort_now():
            probe_c_rows = compute_probe_c(summary.get("probe_a", {}), trajectory_cache)
            blocks_completed.append("C")
            c_smoke = [r for r in probe_c_rows if "rank_stability_across_sample_budgets" in r]
            summary["probe_c"] = {
                "completed": True,
                "mean_cv": sum(r["mean_CV"] for r in c_smoke) / max(len(c_smoke), 1),
                "rank_stability_across_sample_budgets": sum(r["rank_stability_across_sample_budgets"] for r in c_smoke) / max(len(c_smoke), 1),
            }
        else:
            blocks_skipped.append("C")
    except Exception as exc:
        overall_status = "ERROR"
        summary["error"] = str(exc)
    finally:
        summary["runtime_status"] = overall_status
        summary["blocks_completed"] = blocks_completed
        summary["blocks_skipped"] = blocks_skipped

        probe_a_csv = probe_a_rows
        probe_b_csv = probe_b_rows
        probe_c_csv = probe_c_rows
        write_csv(results_dir / "probe_A_certification_v2.csv", probe_a_csv)
        write_csv(results_dir / "probe_B_adversarial_sweep.csv", probe_b_csv)
        write_csv(results_dir / "probe_C_estimator_smoke.csv", probe_c_csv)
        (results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        maybe_plot(results_dir, probe_a_rows, probe_b_rows)

        print("\nOMEGA PROBE BATCH 03 SUMMARY")
        print("\nRuntime status:")
        print(f"- {summary['runtime_status']}")
        print("\nProbe A:")
        print(f"- ANTI_IDENTITY_GATE_OK: {summary.get('probe_a', {}).get('anti_identity_gate_ok')}")
        top_a = summary.get("probe_a", {}).get("top_certified_I_v2", [])
        print("- Top certified_I_v2 coarse-grainings:")
        for i, item in enumerate(top_a, 1):
            print(f"  {i}. {item[0]} ({item[1]:.3f})")
        print(f"- Identity raw_I: {summary.get('probe_a', {}).get('identity_raw_I', 0.0):.3f}")
        print(f"- Identity certified_I_v2: {summary.get('probe_a', {}).get('identity_certified_I_v2', 0.0):.3f}")
        print("\nProbe B:")
        print(f"- Number adversarial candidates completed: {summary.get('probe_b', {}).get('candidates_completed', 0)}")
        print(f"- Best adversarial certified_I_v2: {summary.get('probe_b', {}).get('best_adversarial_certified_I_v2', 0.0):.3f}")
        print(f"- Region percentile: {summary.get('probe_b', {}).get('region_percentile', 0.0):.1f}")
        print(f"- Viability_signature percentile: {summary.get('probe_b', {}).get('viability_signature_percentile', 0.0):.1f}")
        print(f"- ADVERSARIAL_WINNER_FOUND: {summary.get('probe_b', {}).get('adversarial_winner_found', False)}")
        print("\nProbe C:")
        print(f"- Completed: {summary.get('probe_c', {}).get('completed', False)}")
        print(f"- Mean CV: {summary.get('probe_c', {}).get('mean_cv', 0.0):.3f}")
        print(f"- Rank stability across budgets: {summary.get('probe_c', {}).get('rank_stability_across_sample_budgets', 0.0):.3f}")
        print("\nInterpretation:")
        print("- Did v2 certification demote overfine partitions?")
        print("- Did adversarial partitions find a loophole?")
        print("- Is estimator behavior stable enough for next small sweep?")
        print("- Recommended next probe.")
        print(f"\nBlocks completed: {blocks_completed}")
        print(f"Blocks skipped: {blocks_skipped}")
        print(f"Runtime: {time.time() - START_TIME:.2f}s / {HARD_LIMIT_SECONDS}s hard limit")


if __name__ == "__main__":
    main()
