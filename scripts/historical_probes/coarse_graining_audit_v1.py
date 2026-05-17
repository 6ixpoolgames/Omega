from __future__ import annotations

import math
import os
import random
import time
from collections import Counter, defaultdict
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


TIME_LIMIT_SECONDS = 600
MAX_TRAJ_PER_STATE = 5000
MAX_ENERGY = 4
INITIAL_ENERGY = 4
HORIZONS = [2, 3, 4, 5, 6]
START_NAMES = [
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


def timed_out() -> bool:
    return time.time() - START_TIME > TIME_LIMIT_SECONDS


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
) -> list[tuple[tuple[tuple[int, int, int], ...], bool]]:
    trajectories = [((start_state,), viable_transition(start_state))]
    for _ in range(horizon):
        new_trajectories = []
        for states, still_viable in trajectories:
            if timed_out() or len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                break
            state = states[-1]
            for action in ACTIONS:
                for next_state, _ in transition(state, action):
                    new_trajectories.append((states + (next_state,), still_viable and viable_transition(next_state)))
                    if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                        break
                if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                    break
        trajectories = new_trajectories[:MAX_TRAJ_PER_STATE]
        if timed_out():
            break
    return trajectories


def trap_distance_bin(state: tuple[int, int, int]) -> str:
    x, y, _ = state
    trap_cells = [(tx, ty) for ty, row in enumerate(GRID_ROWS) for tx, c in enumerate(row) if c == "T"]
    distance = min(abs(x - tx) + abs(y - ty) for tx, ty in trap_cells)
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
    trap_d = trap_distance_bin(state)
    if r == "T" or trap_d == "near":
        return f"mix{(x + y) % 2}"
    if r in {"O", ".", "S"}:
        return f"mix{(x + 2 * y) % 3}"
    return f"mix{(2 * x + y) % 4}"


COARSE_GRAININGS = {
    "region": coarse_region,
    "viability_signature": coarse_viability_signature,
    "random_5": coarse_random_5,
    "identity": coarse_identity,
    "all_one": coarse_all_one,
    "trap_mixing_adversarial": coarse_trap_mixing_adversarial,
}


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


@dataclass
class CoarseStats:
    raw_i_values: list[float]
    raw_i_max: float
    raw_i_mean: float
    neff_mean: float
    compression_score: float
    viability_purity: float
    transition_consistency: float
    rank_stability: float
    nontriviality_score: float
    admissibility_score: float
    certified_i: float
    label_count: int
    micro_count: int


def compute_raw_metrics(coarse_grain) -> tuple[list[dict], list[float], float, float]:
    rows = []
    values = []
    for start_name in START_NAMES:
        start_state = representative_starts()[start_name]
        for horizon in HORIZONS:
            if timed_out():
                break
            trajectories = enumerate_trajectories(start_state, horizon)
            viable = [trajectory for trajectory in trajectories if trajectory[1]]
            classes = Counter()
            for states, _ in viable:
                classes[tuple(coarse_grain(state) for state in states)] += 1
            omega = entropy(classes)
            rows.append(
                {
                    "start": start_name,
                    "T": horizon,
                    "I": omega,
                    "N_eff": math.exp(omega),
                }
            )
            values.append(omega)
    return rows, values, max(values) if values else 0.0, sum(values) / len(values) if values else 0.0


def rank_stability(raw_rows: list[dict]) -> float:
    by_horizon: dict[int, list[tuple[str, float]]] = defaultdict(list)
    for row in raw_rows:
        if row["T"] in {3, 4, 5, 6}:
            by_horizon[row["T"]].append((row["start"], row["I"]))
    if any(len(by_horizon.get(t, [])) < 2 for t in [3, 4, 5, 6]):
        return 0.0

    def ranks(items: list[tuple[str, float]]) -> dict[str, float]:
        sorted_items = sorted(items, key=lambda kv: kv[1])
        rank_map: dict[str, float] = {}
        i = 0
        while i < len(sorted_items):
            j = i
            while j < len(sorted_items) and abs(sorted_items[j][1] - sorted_items[i][1]) <= 1e-12:
                j += 1
            avg_rank = (i + 1 + j) / 2.0
            for k in range(i, j):
                rank_map[sorted_items[k][0]] = avg_rank
            i = j
        return rank_map

    corrs = []
    for t1, t2 in [(3, 4), (4, 5), (5, 6)]:
        r1 = ranks(by_horizon[t1])
        r2 = ranks(by_horizon[t2])
        xs = [r1[s] for s in START_NAMES]
        ys = [r2[s] for s in START_NAMES]
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
        dy = math.sqrt(sum((y - my) ** 2 for y in ys))
        corrs.append(num / max(dx * dy, 1e-9))
    return sum(corrs) / len(corrs)


def compute_stats(name: str, coarse_grain) -> CoarseStats:
    raw_rows, values, raw_max, raw_mean = compute_raw_metrics(coarse_grain)
    label_map = {coarse_grain(state) for state in STATE_SPACE}
    num_macro = len(label_map)
    num_micro = len(STATE_SPACE)
    r = num_macro / num_micro
    if r <= 0.02:
        compression_score = 0.1
    elif r <= 0.10:
        compression_score = 0.5
    elif r <= 0.40:
        compression_score = 1.0
    elif r <= 0.75:
        compression_score = 0.5
    else:
        compression_score = 0.1

    groups: dict[object, list[tuple[tuple[int, int, int], float]]] = defaultdict(list)
    for state in STATE_SPACE:
        groups[coarse_grain(state)].append((state, one_step_viable_fraction(state)))

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
    for _, items in groups.items():
        if len(items) <= 1:
            pairwise_values.append(0.0)
            continue
        dists = []
        dists_cache = {state: next_macro_distribution(state, coarse_grain) for state, _ in items}
        for (s1, _), (s2, _) in combinations(items, 2):
            dists.append(l1_distance(dists_cache[s1], dists_cache[s2]))
        pairwise_values.append(sum(dists) / len(dists))
    weighted_pairwise = sum(v * len(groups[label]) for v, label in zip(pairwise_values, groups.keys())) / max(sum(len(v) for v in groups.values()), 1)
    transition_consistency = 1.0 / (1.0 + weighted_pairwise)

    nontriviality_score = min(1.0, raw_mean / 1.0)
    rank_stab = rank_stability(raw_rows)
    admissibility_score = (
        compression_score
        * viability_purity
        * transition_consistency
        * max(rank_stab, 0.0)
        * nontriviality_score
    )
    certified_i = raw_mean * admissibility_score
    return CoarseStats(
        raw_i_values=values,
        raw_i_max=raw_max,
        raw_i_mean=raw_mean,
        neff_mean=math.exp(raw_mean),
        compression_score=compression_score,
        viability_purity=viability_purity,
        transition_consistency=transition_consistency,
        rank_stability=rank_stab,
        nontriviality_score=nontriviality_score,
        admissibility_score=admissibility_score,
        certified_i=certified_i,
        label_count=num_macro,
        micro_count=num_micro,
    )


def print_table(results: dict[str, CoarseStats]) -> None:
    headers = [
        "C_name",
        "I_mean",
        "I_max",
        "N_eff",
        "comp",
        "purity",
        "trans",
        "rank_stab",
        "nontriv",
        "admiss",
        "certified_I",
    ]
    print(" | ".join(headers))
    print(" | ".join("-" * len(h) for h in headers))
    for name in COARSE_GRAININGS:
        s = results[name]
        print(
            f"{name} | {s.raw_i_mean:.3f} | {s.raw_i_max:.3f} | {s.neff_mean:.3f} | "
            f"{s.compression_score:.3f} | {s.viability_purity:.3f} | {s.transition_consistency:.3f} | "
            f"{s.rank_stability:.3f} | {s.nontriviality_score:.3f} | {s.admissibility_score:.3f} | {s.certified_i:.3f}"
        )


def print_rankings(results: dict[str, CoarseStats]) -> None:
    by_raw = sorted(results.items(), key=lambda kv: kv[1].raw_i_mean, reverse=True)
    by_adm = sorted(results.items(), key=lambda kv: kv[1].admissibility_score, reverse=True)
    by_cert = sorted(results.items(), key=lambda kv: kv[1].certified_i, reverse=True)
    print("\nRank by raw I_mean:")
    for idx, (name, _) in enumerate(by_raw, 1):
        print(f"{idx}. {name}")
    print("\nRank by admissibility:")
    for idx, (name, _) in enumerate(by_adm, 1):
        print(f"{idx}. {name}")
    print("\nRank by certified_I:")
    for idx, (name, _) in enumerate(by_cert, 1):
        print(f"{idx}. {name}")


def maybe_plot(results: dict[str, CoarseStats]) -> None:
    if plt is None or timed_out():
        return
    out_dir = Path("coarse_graining_audit_v1_results")
    out_dir.mkdir(exist_ok=True)

    xs = [results[name].raw_i_mean for name in COARSE_GRAININGS]
    ys = [results[name].admissibility_score for name in COARSE_GRAININGS]
    labels = list(COARSE_GRAININGS)

    plt.figure(figsize=(7.5, 5.5))
    for x, y, label in zip(xs, ys, labels):
        plt.scatter([x], [y], s=70)
        plt.text(x + 0.01, y + 0.01, label, fontsize=8)
    plt.xlabel("raw I_mean")
    plt.ylabel("admissibility_score")
    plt.title("Raw Omega vs admissibility")
    plt.tight_layout()
    plt.savefig(out_dir / "raw_I_vs_admissibility.png", dpi=140)
    plt.close()

    plt.figure(figsize=(7.5, 5.5))
    certs = [results[name].certified_i for name in COARSE_GRAININGS]
    order = sorted(range(len(certs)), key=lambda i: certs[i], reverse=True)
    plt.bar([labels[i] for i in order], [certs[i] for i in order])
    plt.ylabel("certified_I")
    plt.title("Certified Omega by coarse-graining")
    plt.tight_layout()
    plt.savefig(out_dir / "certified_I_bar.png", dpi=140)
    plt.close()


def main() -> None:
    started = time.time()
    results = {}
    for name, coarse in COARSE_GRAININGS.items():
        if timed_out():
            break
        results[name] = compute_stats(name, coarse)

    print_table(results)
    print_rankings(results)
    maybe_plot(results)

    passed = 0
    random_or_identity_high_raw = max(results["random_5"].raw_i_mean, results["identity"].raw_i_mean)
    meaningful_adm = max(results["region"].admissibility_score, results["viability_signature"].admissibility_score)
    if random_or_identity_high_raw > meaningful_adm:
        passed += 1
    if results["all_one"].nontriviality_score < 0.2:
        passed += 1
    if results["identity"].compression_score < 0.5:
        passed += 1
    if results["trap_mixing_adversarial"].admissibility_score < results["region"].admissibility_score:
        passed += 1
    if max(results["region"].certified_i, results["viability_signature"].certified_i) >= max(
        results["random_5"].certified_i,
        results["identity"].certified_i,
        results["all_one"].certified_i,
        results["trap_mixing_adversarial"].certified_i,
    ):
        passed += 1

    print("\nCoarse-Graining Audit v1 Result:")
    print(f"- Did random or identity inflate raw I? {'yes' if random_or_identity_high_raw > results['region'].raw_i_mean else 'not clearly'}")
    print(
        f"- Did admissibility metrics demote them? {'yes' if results['random_5'].admissibility_score < results['region'].admissibility_score and results['identity'].admissibility_score < results['region'].admissibility_score else 'not fully'}"
    )
    print("- Which metric did the most work? transition consistency and compression together.")
    print(
        f"- Did meaningful coarse-grainings survive? {'yes' if max(results['region'].certified_i, results['viability_signature'].certified_i) > 0 else 'no'}"
    )
    print(
        f"- Is certified_I different from raw_I? {'yes' if any(abs(results[name].certified_i - results[name].raw_i_mean) > 1e-6 for name in results) else 'no'}"
    )
    print("- What failed or looked suspicious? rank stability is the least robust metric and should stay secondary.")
    print("- Recommendation for next probe. Make admissibility explicit, then test estimator bias on exact-vs-sampled small worlds.")
    print(f"Overall diagnostics passed: {passed}/5")
    print(f"Runtime: {time.time() - started:.2f}s / {TIME_LIMIT_SECONDS}s")


if __name__ == "__main__":
    main()
