from __future__ import annotations

import math
import os
import random
import time
from collections import Counter
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib-cache"))

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - optional dependency for this script
    plt = None


TIME_LIMIT_SECONDS = 300
MAX_TRAJ_PER_STATE = 5000
MAX_ENERGY = 4
INITIAL_ENERGY = 4
HORIZONS = [1, 2, 3, 4, 5, 6]
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
START_TIME = time.time()
RNG = random.Random(7)
RANDOM_LABELS = {
    (x, y): f"Q{RNG.randrange(5)}" for y in range(HEIGHT) for x in range(WIDTH)
}


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
        # Rigid/safe attractors preserve life while suppressing macro-diversity.
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
        # Noise swamp: high raw branching, weak controlled reachability.
        if action in {"U", "D"}:
            candidate_actions = [action, "L", "R", "WAIT"]
        elif action in {"L", "R"}:
            candidate_actions = [action, "U", "D", "WAIT"]
        else:
            candidate_actions = ["U", "D", "L", "R", "WAIT"]
    elif current == "D" and action != "WAIT":
        # Dead branches create raw alternatives but burn energy quickly.
        candidate_actions = [action, "WAIT"]

    prob = 1.0 / len(candidate_actions)
    return [(apply_cell_rules(x, y, energy, a), prob) for a in candidate_actions]


def viable_transition(next_state: tuple[int, int, int]) -> bool:
    return next_state[2] > 0 and region(next_state) != "T"


def enumerate_trajectories(
    start_state: tuple[int, int, int], horizon: int
) -> list[tuple[tuple[tuple[int, int, int], ...], tuple[str, ...], bool]]:
    trajectories = [((start_state,), tuple(), viable_transition(start_state))]
    for _ in range(horizon):
        new_trajectories = []
        for states, actions, still_viable in trajectories:
            if timed_out() or len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                break
            state = states[-1]
            for action in ACTIONS:
                for next_state, _ in transition(state, action):
                    viable = still_viable and viable_transition(next_state)
                    new_trajectories.append((states + (next_state,), actions + (action,), viable))
                    if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                        break
                if len(new_trajectories) >= MAX_TRAJ_PER_STATE:
                    break
        trajectories = new_trajectories[:MAX_TRAJ_PER_STATE]
        if timed_out():
            break
    return trajectories


def trap_distance_bin(x: int, y: int) -> str:
    trap_cells = [
        (tx, ty)
        for ty, row in enumerate(GRID_ROWS)
        for tx, label in enumerate(row)
        if label == "T"
    ]
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
    x, y, energy = state
    if energy <= 1:
        energy_bin = "e_low"
    elif energy <= 3:
        energy_bin = "e_med"
    else:
        energy_bin = "e_high"
    return energy_bin, trap_distance_bin(x, y), local_branching_bin(state)


def coarse_random_bad(state: tuple[int, int, int]) -> str:
    x, y, _ = state
    return RANDOM_LABELS[(x, y)]


def metrics_for(
    start_state: tuple[int, int, int],
    horizon: int,
) -> dict[str, float | int]:
    trajectories = enumerate_trajectories(start_state, horizon)
    raw_count = len(trajectories)
    viable = [trajectory for trajectory in trajectories if trajectory[2]]
    viable_count = len(viable)
    terminal_counts = Counter(trajectory[0][-1] for trajectory in trajectories)
    reachable_states = len(terminal_counts)
    reachable_h = entropy(terminal_counts)
    trap_hits = sum(any(region(state) == "T" for state in trajectory[0]) for trajectory in trajectories)

    result: dict[str, float | int] = {
        "raw_count": raw_count,
        "viable_count": viable_count,
        "reachable_state_count": reachable_states,
        "reachable_H": reachable_h,
        "survival_fraction": viable_count / raw_count if raw_count else 0.0,
        "trap_hit_fraction": trap_hits / raw_count if raw_count else 0.0,
    }

    for name, coarse_grain in [
        ("I_region", coarse_region),
        ("I_viab", coarse_viability_signature),
        ("I_random", coarse_random_bad),
    ]:
        classes = Counter()
        for states, _, _ in viable:
            classes[tuple(coarse_grain(state) for state in states)] += 1
        omega = entropy(classes)
        result[name] = omega
        result[f"N_eff_{name}"] = math.exp(omega)
    return result


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


def print_table(rows: list[dict[str, float | int | str]]) -> None:
    headers = [
        "region",
        "T",
        "raw_count",
        "viable_count",
        "survival",
        "reachable_H",
        "I_region",
        "I_viab",
        "I_random",
    ]
    print(" | ".join(headers))
    print(" | ".join("-" * len(header) for header in headers))
    for row in rows:
        print(
            f"{row['region']} | {row['T']} | {row['raw_count']} | {row['viable_count']} | "
            f"{row['survival_fraction']:.3f} | {row['reachable_H']:.3f} | "
            f"{row['I_region']:.3f} | {row['I_viab']:.3f} | {row['I_random']:.3f}"
        )


def evaluate_diagnostics(rows: list[dict[str, float | int | str]]) -> list[tuple[str, bool, str]]:
    by_region_t = {(row["region"], row["T"]): row for row in rows}
    t_final = max(HORIZONS)

    open_final = by_region_t[("open", t_final)]
    trap_final = by_region_t[("near_trap", t_final)]
    dead_final = by_region_t[("dead_branch", t_final)]
    noise_final = by_region_t[("noise_swamp", t_final)]
    rigid_final = by_region_t[("rigid_attractor", t_final)]
    loop_rows = [row for row in rows if row["region"] == "loop"]

    diagnostics = [
        (
            "Open field has higher Omega invariant than trap-adjacent.",
            open_final["I_region"] > trap_final["I_region"],
            f"open={open_final['I_region']:.3f}, near_trap={trap_final['I_region']:.3f}",
        ),
        (
            "Dead branch has higher raw count than trap-adjacent but low viable Omega.",
            dead_final["raw_count"] >= trap_final["raw_count"]
            and dead_final["I_region"] <= open_final["I_region"] * 0.5,
            (
                f"dead raw={dead_final['raw_count']}, trap raw={trap_final['raw_count']}, "
                f"dead I={dead_final['I_region']:.3f}, open I={open_final['I_region']:.3f}"
            ),
        ),
        (
            "Noise swamp reachable entropy exceeds its Omega invariant.",
            noise_final["reachable_H"] > noise_final["I_region"],
            f"reachable_H={noise_final['reachable_H']:.3f}, I_region={noise_final['I_region']:.3f}",
        ),
        (
            "Rigid attractor survival is high but Omega invariant is low.",
            rigid_final["survival_fraction"] >= 0.9 and rigid_final["I_region"] <= 0.25,
            f"survival={rigid_final['survival_fraction']:.3f}, I_region={rigid_final['I_region']:.3f}",
        ),
        (
            "Reversible loop maintains nonzero Omega across horizons.",
            all(row["I_region"] > 0 for row in loop_rows),
            "min loop I={:.3f}".format(min(float(row["I_region"]) for row in loop_rows)),
        ),
        (
            "Meaningful coarse-grainings are more stable/interpretable than random.",
            abs(open_final["I_region"] - open_final["I_viab"]) < abs(
                open_final["I_region"] - open_final["I_random"]
            )
            or abs(trap_final["I_region"] - trap_final["I_viab"]) < abs(
                trap_final["I_region"] - trap_final["I_random"]
            ),
            (
                f"open I_region={open_final['I_region']:.3f}, "
                f"I_viab={open_final['I_viab']:.3f}, I_random={open_final['I_random']:.3f}"
            ),
        ),
    ]
    return diagnostics


def maybe_plot(rows: list[dict[str, float | int | str]]) -> None:
    if plt is None or timed_out():
        return
    out_dir = Path("omega_5min_results")
    out_dir.mkdir(exist_ok=True)

    regions = list(representative_starts())
    for key in ["I_region", "I_viab", "I_random"]:
        plt.figure(figsize=(9, 5))
        for region_name in regions:
            region_rows = [row for row in rows if row["region"] == region_name]
            plt.plot(
                [row["T"] for row in region_rows],
                [row[key] for row in region_rows],
                marker="o",
                label=region_name,
            )
        plt.xlabel("horizon T")
        plt.ylabel(key)
        plt.title(f"{key} vs horizon")
        plt.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        plt.savefig(out_dir / f"{key}_vs_T.png", dpi=140)
        plt.close()

    plt.figure(figsize=(6, 5))
    plt.scatter(
        [row["reachable_H"] for row in rows],
        [row["I_region"] for row in rows],
        alpha=0.75,
    )
    plt.xlabel("reachable state entropy")
    plt.ylabel("Omega I_region")
    plt.title("Raw reachability entropy vs Omega invariant")
    plt.tight_layout()
    plt.savefig(out_dir / "reachable_entropy_vs_omega.png", dpi=140)
    plt.close()


def main() -> None:
    starts = representative_starts()
    rows: list[dict[str, float | int | str]] = []

    for name, start_state in starts.items():
        for horizon in HORIZONS:
            if timed_out():
                break
            row = metrics_for(start_state, horizon)
            row["region"] = name
            row["T"] = horizon
            rows.append(row)
        if timed_out():
            break

    print_table(rows)
    diagnostics = evaluate_diagnostics(rows)
    passed = sum(ok for _, ok, _ in diagnostics)

    print("\nPASS/FAIL diagnostics")
    for label, ok, detail in diagnostics:
        status = "PASS" if ok else "WARN"
        print(f"{status}: {label} ({detail})")

    final_status = "PASS" if passed >= 4 and not timed_out() else "FAIL/WARNING"
    print(f"\nOverall: {final_status} ({passed}/6 diagnostics passed)")
    print(f"Runtime: {time.time() - START_TIME:.2f}s / {TIME_LIMIT_SECONDS}s")

    print("\nInitial validation result:")
    print("- Does Omega distinguish viable structured futures from raw reachability?")
    print("  Partially: compare reachable_H against I_region/I_viab in the table.")
    print("- Does it distinguish survival from future diversity?")
    print("  Yes if rigid_attractor shows high survival and low Omega invariant.")
    print("- Does it reject noise-only entropy?")
    print("  Yes if noise_swamp reachable_H exceeds its Omega invariant.")
    print("- Does coarse-graining choice dominate the result?")
    print("  Warning if I_random tracks meaningful coarse-grainings too closely.")
    print("- What broke?")
    print("  This is still a hand-designed finite world; transition rules carry the test assumptions.")
    print("- What should be tested next?")
    print("  Replace hand-picked coarse-grainings with learned/admissibility-tested coarse-grainings.")

    maybe_plot(rows)


if __name__ == "__main__":
    main()
