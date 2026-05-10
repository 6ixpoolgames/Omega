from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


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

ACTIONS = ["U", "D", "L", "R", "WAIT"]
MAX_ENERGY = 5
INITIAL_ENERGY = 5
REGIONS = ["O", "S", "B", "L", "C", "D", "R", "A", "."]


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for count in counts.values():
        p = count / total
        h -= p * math.log(p)
    return h


def mutate_grid(seed: int, mutation_rate: float) -> list[str]:
    rng = random.Random(seed)
    rows = [list(row) for row in BASE_GRID]
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if cell == "T":
                continue
            if rng.random() < mutation_rate:
                row[x] = rng.choice(REGIONS)
    return ["".join(row) for row in rows]


def find_first(grid: list[str], label: str) -> tuple[int, int] | None:
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == label:
                return x, y
    return None


def representative_starts(grid: list[str]) -> dict[str, tuple[int, int, int]]:
    wanted = {
        "open": "O",
        "noise_swamp": "S",
        "bottleneck": "B",
        "loop": "L",
        "resource_corridor": "C",
        "dead_branch": "D",
        "rigid_attractor": "R",
    }
    starts: dict[str, tuple[int, int, int]] = {}
    for name, label in wanted.items():
        cell = find_first(grid, label)
        if cell is not None:
            starts[name] = (cell[0], cell[1], INITIAL_ENERGY)

    trap = find_first(grid, "T")
    if trap is not None:
        tx, ty = trap
        candidates = [(tx, ty - 1), (tx + 1, ty), (tx, ty + 1), (tx - 1, ty)]
        for x, y in candidates:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] != "T":
                starts["near_trap"] = (x, y, INITIAL_ENERGY)
                break
    return starts


def run_world(
    seed: int,
    horizons: tuple[int, ...],
    max_traj: int,
    mutation_rate: float,
) -> dict:
    started = time.perf_counter()
    pid = os.getpid()
    grid = mutate_grid(seed, mutation_rate)
    width = len(grid[0])
    height = len(grid)
    rng = random.Random(seed + 10_000)
    random_labels = {(x, y): f"Q{rng.randrange(7)}" for y in range(height) for x in range(width)}

    trap_cells = [
        (x, y)
        for y, row in enumerate(grid)
        for x, label in enumerate(row)
        if label == "T"
    ]

    def region_xy(x: int, y: int) -> str:
        if x < 0 or y < 0 or x >= width or y >= height:
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
            new_energy = min(MAX_ENERGY, new_energy + 2)
        if next_region in {"R", "A"}:
            new_energy = max(1, new_energy)
        return nx, ny, new_energy

    def transition(state: tuple[int, int, int], action: str) -> list[tuple[int, int, int]]:
        x, y, energy = state
        current = region_xy(x, y)
        if current in {"R", "A", "T"}:
            return [apply_cell_rules(x, y, energy, action)]

        candidate_actions = [action]
        if current == "S":
            candidate_actions = ACTIONS
        elif current == "D" and action != "WAIT":
            candidate_actions = [action, "WAIT"]
        elif current == "B" and action != "WAIT":
            candidate_actions = [action, action, "WAIT"]
        return [apply_cell_rules(x, y, energy, a) for a in candidate_actions]

    def viable(next_state: tuple[int, int, int]) -> bool:
        x, y, energy = next_state
        return energy > 0 and region_xy(x, y) != "T"

    def enumerate_trajectories(
        start_state: tuple[int, int, int], horizon: int
    ) -> list[tuple[tuple[tuple[int, int, int], ...], bool]]:
        trajectories = [((start_state,), viable(start_state))]
        for _ in range(horizon):
            new_trajectories = []
            for states, still_viable in trajectories:
                state = states[-1]
                for action in ACTIONS:
                    for next_state in transition(state, action):
                        new_trajectories.append(
                            (states + (next_state,), still_viable and viable(next_state))
                        )
                        if len(new_trajectories) >= max_traj:
                            break
                    if len(new_trajectories) >= max_traj:
                        break
                if len(new_trajectories) >= max_traj:
                    break
            trajectories = new_trajectories
        return trajectories

    def trap_distance_bin(x: int, y: int) -> str:
        if not trap_cells:
            return "far"
        distance = min(abs(x - tx) + abs(y - ty) for tx, ty in trap_cells)
        return "near" if distance <= 2 else "far"

    def local_branching_bin(state: tuple[int, int, int]) -> str:
        count = 0
        for action in ACTIONS:
            for next_state in transition(state, action):
                if viable(next_state):
                    count += 1
        if count <= 2:
            return "low"
        if count <= 7:
            return "med"
        return "high"

    def coarse_region(state: tuple[int, int, int]) -> str:
        x, y, _ = state
        return region_xy(x, y)

    def coarse_viability(state: tuple[int, int, int]) -> tuple[str, str, str]:
        x, y, energy = state
        if energy <= 1:
            energy_bin = "e_low"
        elif energy <= 3:
            energy_bin = "e_med"
        else:
            energy_bin = "e_high"
        return energy_bin, trap_distance_bin(x, y), local_branching_bin(state)

    def coarse_random(state: tuple[int, int, int]) -> str:
        x, y, _ = state
        return random_labels[(x, y)]

    rows = []
    for name, start_state in representative_starts(grid).items():
        for horizon in horizons:
            trajectories = enumerate_trajectories(start_state, horizon)
            raw_count = len(trajectories)
            viable_trajectories = [trajectory for trajectory in trajectories if trajectory[1]]
            viable_count = len(viable_trajectories)
            terminal_counts = Counter(trajectory[0][-1] for trajectory in trajectories)
            trap_hits = sum(
                any(region_xy(state[0], state[1]) == "T" for state in trajectory[0])
                for trajectory in trajectories
            )

            row = {
                "seed": seed,
                "pid": pid,
                "start": name,
                "T": horizon,
                "raw_count": raw_count,
                "viable_count": viable_count,
                "survival_fraction": viable_count / raw_count if raw_count else 0.0,
                "trap_hit_fraction": trap_hits / raw_count if raw_count else 0.0,
                "reachable_H": entropy(terminal_counts),
            }
            for label, coarse in [
                ("I_region", coarse_region),
                ("I_viab", coarse_viability),
                ("I_random", coarse_random),
            ]:
                classes = Counter()
                for states, _ in viable_trajectories:
                    classes[tuple(coarse(state) for state in states)] += 1
                row[label] = entropy(classes)
            rows.append(row)

    elapsed = time.perf_counter() - started
    return {"seed": seed, "pid": pid, "elapsed": elapsed, "rows": rows, "grid": grid}


def summarize(rows: list[dict]) -> dict:
    final_rows = [row for row in rows if row["T"] == max(row["T"] for row in rows)]
    by_start: dict[str, list[dict]] = {}
    for row in final_rows:
        by_start.setdefault(row["start"], []).append(row)

    summary = {}
    for start, group in sorted(by_start.items()):
        summary[start] = {
            "n": len(group),
            "mean_raw_count": sum(row["raw_count"] for row in group) / len(group),
            "mean_survival": sum(row["survival_fraction"] for row in group) / len(group),
            "mean_reachable_H": sum(row["reachable_H"] for row in group) / len(group),
            "mean_I_region": sum(row["I_region"] for row in group) / len(group),
            "mean_I_viab": sum(row["I_viab"] for row in group) / len(group),
            "mean_I_random": sum(row["I_random"] for row in group) / len(group),
        }
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parallel CPU Omega environment validation pass.")
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    parser.add_argument("--worlds", type=int, default=96)
    parser.add_argument("--max-traj", type=int, default=25000)
    parser.add_argument("--horizons", type=str, default="4,5,6,7,8")
    parser.add_argument("--mutation-rate", type=float, default=0.10)
    parser.add_argument("--out-dir", type=Path, default=Path("omega_cpu_validation_results"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    horizons = tuple(int(item) for item in args.horizons.split(",") if item.strip())
    args.out_dir.mkdir(exist_ok=True)

    started = time.perf_counter()
    print(
        f"Running {args.worlds} randomized worlds with {args.workers} workers, "
        f"horizons={horizons}, max_traj={args.max_traj}"
    )

    all_rows: list[dict] = []
    worker_times = []
    example_grids = {}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(run_world, seed, horizons, args.max_traj, args.mutation_rate)
            for seed in range(args.worlds)
        ]
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            completed += 1
            all_rows.extend(result["rows"])
            worker_times.append({"seed": result["seed"], "pid": result["pid"], "elapsed": result["elapsed"]})
            if len(example_grids) < 5:
                example_grids[str(result["seed"])] = result["grid"]
            if completed % max(1, args.workers) == 0:
                print(f"completed {completed}/{args.worlds} worlds")

    elapsed = time.perf_counter() - started

    csv_path = args.out_dir / "larger_omega_cpu_validation_results.csv"
    fieldnames = [
        "seed",
        "pid",
        "start",
        "T",
        "raw_count",
        "viable_count",
        "survival_fraction",
        "trap_hit_fraction",
        "reachable_H",
        "I_region",
        "I_viab",
        "I_random",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    summary = {
        "config": {
            "workers": args.workers,
            "worlds": args.worlds,
            "horizons": horizons,
            "max_traj": args.max_traj,
            "mutation_rate": args.mutation_rate,
            "logical_cpus_seen": os.cpu_count(),
        },
        "elapsed_seconds": elapsed,
        "rows": len(all_rows),
        "unique_worker_pids": sorted({item["pid"] for item in worker_times}),
        "worker_times": worker_times,
        "by_start_final_horizon": summarize(all_rows),
        "example_grids": example_grids,
    }
    summary_path = args.out_dir / "larger_omega_cpu_validation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nElapsed: {elapsed:.2f}s")
    print(f"Rows: {len(all_rows)}")
    print(f"Unique worker PIDs: {len(summary['unique_worker_pids'])}")
    print(f"CSV: {csv_path}")
    print(f"Summary: {summary_path}")
    print("\nFinal-horizon aggregate means:")
    for start, values in summary["by_start_final_horizon"].items():
        print(
            f"{start:18s} n={values['n']:3d} "
            f"survival={values['mean_survival']:.3f} "
            f"reachable_H={values['mean_reachable_H']:.3f} "
            f"I_region={values['mean_I_region']:.3f} "
            f"I_viab={values['mean_I_viab']:.3f} "
            f"I_random={values['mean_I_random']:.3f}"
        )


if __name__ == "__main__":
    main()

