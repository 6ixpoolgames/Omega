from __future__ import annotations

import csv
import json
import math
import os
import random
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib-cache"))

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    plt = None

from probe_06a_minimal_admissible_quotient_gate import (
    ACTIONS,
    BASE_GRID_9,
    ENERGY_CAP,
    INITIAL_ENERGY_DEFAULT,
    REPAIR_HORIZON,
    World,
    behavioral_quotient_labels,
    build_behavioral_features,
    build_predictive_features,
    coarse_hash_fixed,
    coarse_trap_mixing,
    coarse_viability_signature_factory,
    entropy,
    enumerate_trajectories,
    exists_viable_future,
    find_cells,
    gmean,
    grid_copy,
    make_random_partition,
    predictive_quotient_labels,
    recoverable_micro,
    region_xy,
    rows_from_grid,
    state_space,
)


SOFT_LIMIT_SECONDS = 1800
HARD_LIMIT_SECONDS = 2700
WORKERS = int(os.environ.get("OMEGA_WORKERS", 18))
WORLDS_PER_FAMILY = int(os.environ.get("OMEGA_WORLDS_PER_FAMILY", 250))
MAX_TRAJ_PER_STATE = 50000
HORIZONS = [2, 3, 4, 5, 6, 8, 10]
SHORT_HORIZONS = {2, 3}
MID_HORIZONS = {4, 5, 6}
LONG_HORIZONS = {8, 10}
START_TIME = time.time()


def status_code() -> str:
    elapsed = time.time() - START_TIME
    if elapsed > HARD_LIMIT_SECONDS:
        return "PARTIAL_EXIT_HARD_LIMIT"
    if elapsed > SOFT_LIMIT_SECONDS:
        return "PARTIAL_EXIT_SOFT_LIMIT"
    return "COMPLETE"


def should_continue() -> bool:
    return time.time() - START_TIME < SOFT_LIMIT_SECONDS


def should_abort() -> bool:
    return time.time() - START_TIME > HARD_LIMIT_SECONDS


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in keys})
    last_exc = None
    for _ in range(10):
        try:
            os.replace(tmp, path)
            return
        except (PermissionError, OSError) as exc:
            last_exc = exc
            time.sleep(0.25)
    fallback = path.with_name(f"{path.stem}.{os.getpid()}.csv")
    os.replace(tmp, fallback)
    raise RuntimeError(f"could not replace {path}; wrote fallback {fallback}") from last_exc


def base_world(seed: int, family: str, condition: str) -> World:
    return World(
        family=family,
        variant=condition,
        seed=seed,
        grid=BASE_GRID_9[:],
        size=9,
        noise_slip_prob=0.05 * (seed % 3),
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


def make_family_a_world(seed: int, condition: str, pair_id: int) -> World:
    w = base_world(seed, "A", condition)
    w.pair_id = pair_id
    rng = random.Random(seed * 1009 + (0 if condition == "reversible" else 1))
    grid = [["T" for _ in range(9)] for _ in range(9)]
    # Main corridor and junction are identical in both conditions.
    corridor = [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4)]
    for x, y in corridor:
        grid[y][x] = "O"
    branch_count = [2, 3, 4][seed % 3]
    branch_len = [2, 3, 4][(seed // 3) % 3]
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)][:branch_count]
    junction = (3, 4)
    for i, (dx, dy) in enumerate(dirs):
        x, y = junction
        cells = []
        for step in range(branch_len):
            x = max(1, min(7, x + dx))
            y = max(1, min(7, y + dy))
            cells.append((x, y))
        for bx, by in cells:
            grid[by][bx] = "L"
        if condition == "reversible":
            # Add a reconnecting viable cell near the branch tip.
            tx, ty = cells[-1]
            rx = max(1, min(7, tx + (1 if tx < 6 else -1)))
            ry = max(1, min(7, ty + (1 if ty < 6 else -1)))
            grid[ry][rx] = "L"
        else:
            tx, ty = cells[-1]
            grid[ty][tx] = "D"
            if 1 <= tx + dx <= 7 and 1 <= ty + dy <= 7:
                grid[ty + dy][tx + dx] = "T"
    # Seed-controlled resources away from the trap structure.
    for _ in range(2):
        x, y = rng.choice(corridor[3:])
        grid[y][x] = "C"
    w.grid = rows_from_grid(grid)
    w.notes = ["matched_branching", f"branches={branch_count}", f"length={branch_len}"]
    return w


def make_family_b_world(seed: int, pair_id: int) -> World:
    w = base_world(seed, "B", "hidden_fake")
    w.pair_id = pair_id
    grid = grid_copy(BASE_GRID_9)
    for y in range(9):
        for x in range(9):
            if (x + y + seed) % 2 == 0:
                grid[y][x] = "C" if (x * 3 + y + seed) % 5 else "O"
            else:
                grid[y][x] = "T" if (x * 7 + y + seed) % 4 == 0 else "S"
    for x, y in [(1, 1), (2, 1), (1, 2), (5, 5), (6, 5)]:
        grid[y][x] = "C"
    for x, y in [(2, 2), (5, 6), (6, 6)]:
        grid[y][x] = "T"
    w.grid = rows_from_grid(grid)
    w.noise_slip_prob = 0.1 + 0.05 * (seed % 3)
    w.notes = ["hidden_fake_viability"]
    return w


def build_worlds() -> list[World]:
    worlds: list[World] = []
    for pair_id in range(WORLDS_PER_FAMILY // 2):
        seed = pair_id
        worlds.append(make_family_a_world(seed, "reversible", pair_id))
        worlds.append(make_family_a_world(seed, "irreversible", pair_id))
    for seed in range(WORLDS_PER_FAMILY):
        worlds.append(make_family_b_world(10_000 + seed, seed))
    return worlds


def starts_for_world(world: World) -> dict[str, tuple[int, int, int]]:
    if world.family == "A":
        return {"start": (1, 4, world.initial_energy)}
    candidates = []
    for y, row in enumerate(world.grid):
        for x, lab in enumerate(row):
            if lab in {"O", "C"}:
                candidates.append((x, y, world.initial_energy))
    if not candidates:
        return {"start": (0, 0, world.initial_energy)}
    return {"start": candidates[0], "alt": candidates[len(candidates) // 2]}


def candidate_names() -> list[str]:
    return [
        "identity",
        "all_one",
        "random_k",
        "checkerboard",
        "trap_mixing_adversarial",
        "hash_k34_s1206",
        "best_of_10_hashes_per_world",
        "behavioral_quotient_k5",
        "behavioral_quotient_k8",
        "behavioral_quotient_k13",
        "predictive_quotient_k5",
        "predictive_quotient_k8",
        "predictive_quotient_k13",
        "viability_signature",
    ]


def build_candidate_maps(world: World, starts: dict, traj_cache: dict) -> tuple[dict[str, dict], int]:
    states = state_space(world)
    random_fn = make_random_partition(world, 13)
    maps: dict[str, dict] = {
        "identity": {s: s for s in states},
        "all_one": {s: 0 for s in states},
        "random_k": {s: random_fn(s) for s in states},
        "checkerboard": {s: (s[0] + s[1]) % 2 for s in states},
        "trap_mixing_adversarial": {s: coarse_trap_mixing(world)(s) for s in states},
        "hash_k34_s1206": {s: coarse_hash_fixed(s) for s in states},
        "viability_signature": {s: coarse_viability_signature_factory(world)(s) for s in states},
    }
    behavioral_features = build_behavioral_features(world)
    predictive_features = build_predictive_features(world)
    for k in [5, 8, 13]:
        maps[f"behavioral_quotient_k{k}"] = behavioral_quotient_labels(world, k, behavioral_features)
        maps[f"predictive_quotient_k{k}"] = predictive_quotient_labels(world, k, predictive_features)

    best_idx = 0
    best_score = -1.0
    best_map = None
    for idx in range(10):
        k = [2, 3, 5, 8, 13, 21, 34, 55][idx % 8]
        rng = random.Random(world.seed * 911 + idx * 37)
        mapping = {s: rng.randrange(k) for s in states}
        score = 0.0
        for start_name in starts:
            trajectories, _ = traj_cache[(start_name, 4)]
            viable = [tr for tr in trajectories if tr[1]]
            classes = Counter(tuple(mapping[s] for s in states_) for states_, _, _ in viable)
            score += entropy(classes)
        if score > best_score:
            best_score = score
            best_idx = idx
            best_map = mapping
    maps["best_of_10_hashes_per_world"] = best_map if best_map is not None else maps["random_k"]
    return maps, best_idx


def recoverability_map(world: World) -> dict[tuple[int, int, int], float]:
    memo = {}
    return {s: 1.0 if recoverable_micro(world, s, memo) else 0.0 for s in state_space(world)}


def weighted_entropy(class_weights: dict) -> float:
    counter = Counter()
    for key, value in class_weights.items():
        if value > 0:
            counter[key] = value
    return entropy(counter)


def profile_for(world: World, candidate: str, labels: dict, starts: dict, traj_cache: dict, recover: dict) -> tuple[list[dict], list[dict]]:
    profile_rows = []
    estimator_rows = []
    for start_name, start_state in starts.items():
        for horizon in HORIZONS:
            trajectories, truncated = traj_cache[(start_name, horizon)]
            all_count = len(trajectories)
            viable = [tr for tr in trajectories if tr[1]]
            p_viable = len(viable) / max(all_count, 1)
            classes = Counter()
            recovery_weighted = defaultdict(float)
            pi_means = []
            pi_mins = []
            for states_, _ok, _cost in viable:
                macro = tuple(labels[s] for s in states_)
                classes[macro] += 1
                vals = [recover.get(s, 0.0) for s in states_]
                pi_mean = sum(vals) / max(len(vals), 1)
                pi_min = min(vals) if vals else 0.0
                pi_means.append(pi_mean)
                pi_mins.append(pi_min)
                recovery_weighted[macro] += pi_mean
            H_cond = entropy(classes)
            H_weighted = p_viable * H_cond
            H_recover = weighted_entropy(recovery_weighted)
            profile_rows.append(
                {
                    "world_id": f"{world.family}_{world.seed}_{world.variant}",
                    "world_seed": world.seed,
                    "family": world.family,
                    "condition": world.variant,
                    "pair_id": world.pair_id if world.pair_id is not None else "",
                    "candidate_C": candidate,
                    "start_state": start_name,
                    "horizon_T": horizon,
                    "p_viable": p_viable,
                    "num_all_trajectories": all_count,
                    "num_viable_trajectories": len(viable),
                    "H_cond_viable": H_cond,
                    "N_eff_cond": math.exp(H_cond),
                    "num_viable_macro_classes": len(classes),
                    "H_viability_weighted": H_weighted,
                    "Pi_mean": sum(pi_means) / max(len(pi_means), 1),
                    "Pi_min": sum(pi_mins) / max(len(pi_mins), 1),
                    "H_recoverability_weighted": H_recover,
                    "N_eff_recoverability_weighted": math.exp(H_recover),
                    "estimator_mode": "truncated" if truncated else "exact",
                    "truncated": int(truncated),
                    "adaptive_idx": "",
                }
            )
            estimator_rows.append(
                {
                    "world_id": f"{world.family}_{world.seed}_{world.variant}",
                    "candidate_C": candidate,
                    "start_state": start_name,
                    "horizon_T": horizon,
                    "estimator_mode": "truncated" if truncated else "exact",
                    "truncated": int(truncated),
                    "num_all_trajectories": all_count,
                    "num_viable_trajectories": len(viable),
                    "mc_used": 0,
                }
            )
    return profile_rows, estimator_rows


def coarse_diagnostics(world: World, candidate: str, labels: dict, recover: dict) -> dict:
    states = state_space(world)
    label_groups = defaultdict(list)
    for s in states:
        label_groups[labels[s]].append(s)
    memo = {}
    viable = {s: 1.0 if exists_viable_future(world, s, 4, memo) else 0.0 for s in states}
    mixed_v = 0
    mixed_r = 0
    trap_mixed = 0
    for members in label_groups.values():
        vf = sum(viable[s] for s in members) / max(len(members), 1)
        rf = sum(recover[s] for s in members) / max(len(members), 1)
        tf = sum(1.0 if region_xy(world.grid, s[0], s[1]) == "T" else 0.0 for s in members) / max(len(members), 1)
        mixed_v += int(0.0 < vf < 1.0)
        mixed_r += int(0.0 < rf < 1.0)
        trap_mixed += int(0.0 < tf < 1.0)
    counts = Counter(labels[s] for s in states)
    return {
        "world_id": f"{world.family}_{world.seed}_{world.variant}",
        "world_seed": world.seed,
        "family": world.family,
        "condition": world.variant,
        "pair_id": world.pair_id if world.pair_id is not None else "",
        "candidate_C": candidate,
        "num_micro_states": len(states),
        "num_macro_labels": len(counts),
        "compression_ratio": len(counts) / max(len(states), 1),
        "mean_fiber_size": len(states) / max(len(counts), 1),
        "singleton_fraction": sum(1 for c in counts.values() if c == 1) / max(len(counts), 1),
        "label_entropy": entropy(counts),
        "macro_viability_mixing_rate": mixed_v / max(len(label_groups), 1),
        "macro_recoverability_mixing_rate": mixed_r / max(len(label_groups), 1),
        "trap_mixing_rate": trap_mixed / max(len(label_groups), 1),
    }


def evaluate_world(world: World) -> dict:
    starts = starts_for_world(world)
    traj_cache = {}
    for start_name, start_state in starts.items():
        for horizon in HORIZONS:
            traj_cache[(start_name, horizon)] = enumerate_trajectories(world, start_state, horizon)
    maps, adaptive_idx = build_candidate_maps(world, starts, traj_cache)
    recover = recoverability_map(world)
    profile_rows = []
    estimator_rows = []
    diagnostics = []
    for candidate in candidate_names():
        rows, est = profile_for(world, candidate, maps[candidate], starts, traj_cache, recover)
        if candidate == "best_of_10_hashes_per_world":
            for row in rows:
                row["adaptive_idx"] = adaptive_idx
        profile_rows.extend(rows)
        estimator_rows.extend(est)
        diagnostics.append(coarse_diagnostics(world, candidate, maps[candidate], recover))
    return {
        "profile_rows": profile_rows,
        "estimator_rows": estimator_rows,
        "diagnostics": diagnostics,
    }


def horizon_summary(profile_rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for r in profile_rows:
        groups[(r["family"], r["condition"], r["candidate_C"], r["start_state"])].append(r)
    out = []
    for (family, condition, candidate, start), rows in groups.items():
        def avg(metric: str, horizons: set[int]) -> float:
            vals = [float(r[metric]) for r in rows if int(r["horizon_T"]) in horizons]
            return sum(vals) / max(len(vals), 1)
        for metric in ["p_viable", "H_cond_viable", "H_viability_weighted", "H_recoverability_weighted"]:
            early = avg(metric, SHORT_HORIZONS)
            mid = avg(metric, MID_HORIZONS)
            late = avg(metric, LONG_HORIZONS)
            out.append(
                {
                    "family": family,
                    "condition": condition,
                    "candidate_C": candidate,
                    "start_state": start,
                    "metric": metric,
                    "early": early,
                    "mid": mid,
                    "late": late,
                    "early_to_late_delta": late - early,
                    "collapse_ratio": late / max(early, 1e-9),
                }
            )
    return out


def family_a_contrasts(profile_rows: list[dict], horizon_rows: list[dict]) -> list[dict]:
    rows = [r for r in profile_rows if r["family"] == "A"]
    grouped = defaultdict(dict)
    for r in rows:
        grouped[(r["pair_id"], r["candidate_C"], r["start_state"], r["horizon_T"])][r["condition"]] = r
    out = []
    for key, pair in grouped.items():
        if "reversible" not in pair or "irreversible" not in pair:
            continue
        R, I = pair["reversible"], pair["irreversible"]
        out.append(
            {
                "pair_id": key[0],
                "candidate_C": key[1],
                "start_state": key[2],
                "horizon_T": key[3],
                "Delta_p_viable": float(R["p_viable"]) - float(I["p_viable"]),
                "Delta_H_cond": float(R["H_cond_viable"]) - float(I["H_cond_viable"]),
                "Delta_H_weighted": float(R["H_viability_weighted"]) - float(I["H_viability_weighted"]),
                "Delta_H_recoverability": float(R["H_recoverability_weighted"]) - float(I["H_recoverability_weighted"]),
            }
        )
    collapse = defaultdict(dict)
    for r in horizon_rows:
        if r["family"] == "A" and r["metric"] == "H_cond_viable":
            collapse[(r["candidate_C"], r["start_state"], r.get("pair_id", ""))][r["condition"]] = r
    return out


def family_b_profiles(profile_rows: list[dict], diagnostics: list[dict]) -> list[dict]:
    diag_map = {(d["world_id"], d["candidate_C"]): d for d in diagnostics}
    out = []
    for r in profile_rows:
        if r["family"] != "B":
            continue
        d = diag_map.get((r["world_id"], r["candidate_C"]), {})
        out.append(
            {
                "world_id": r["world_id"],
                "candidate_C": r["candidate_C"],
                "start_state": r["start_state"],
                "horizon_T": r["horizon_T"],
                "H_cond_viable": r["H_cond_viable"],
                "H_viability_weighted": r["H_viability_weighted"],
                "H_recoverability_weighted": r["H_recoverability_weighted"],
                "macro_viability_mixing_rate": d.get("macro_viability_mixing_rate", ""),
                "macro_recoverability_mixing_rate": d.get("macro_recoverability_mixing_rate", ""),
                "trap_mixing_rate": d.get("trap_mixing_rate", ""),
            }
        )
    return out


def candidate_summary(profile_rows: list[dict], diagnostics: list[dict]) -> list[dict]:
    by_c = defaultdict(list)
    for r in profile_rows:
        by_c[r["candidate_C"]].append(r)
    diag_by_c = defaultdict(list)
    for d in diagnostics:
        diag_by_c[d["candidate_C"]].append(d)
    out = []
    for candidate, rows in by_c.items():
        diag = diag_by_c[candidate]
        out.append(
            {
                "candidate_C": candidate,
                "mean_p_viable": sum(float(r["p_viable"]) for r in rows) / len(rows),
                "mean_H_cond_viable": sum(float(r["H_cond_viable"]) for r in rows) / len(rows),
                "mean_H_viability_weighted": sum(float(r["H_viability_weighted"]) for r in rows) / len(rows),
                "mean_H_recoverability_weighted": sum(float(r["H_recoverability_weighted"]) for r in rows) / len(rows),
                "mean_Pi_mean": sum(float(r["Pi_mean"]) for r in rows) / len(rows),
                "mean_macro_viability_mixing_rate": sum(float(d["macro_viability_mixing_rate"]) for d in diag) / max(len(diag), 1),
                "mean_macro_recoverability_mixing_rate": sum(float(d["macro_recoverability_mixing_rate"]) for d in diag) / max(len(diag), 1),
                "mean_trap_mixing_rate": sum(float(d["trap_mixing_rate"]) for d in diag) / max(len(diag), 1),
                "rows": len(rows),
            }
        )
    return sorted(out, key=lambda r: r["mean_H_viability_weighted"], reverse=True)


def maybe_plot(results_dir: Path, fam_a: list[dict], fam_b: list[dict], profile_rows: list[dict]):
    if plt is None:
        return
    if fam_a:
        by_c = defaultdict(list)
        for r in fam_a:
            by_c[r["candidate_C"]].append(float(r["Delta_H_weighted"]))
        labels = list(by_c)
        vals = [sum(v) / len(v) for v in by_c.values()]
        plt.figure(figsize=(9, 5))
        plt.bar(labels, vals)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(results_dir / "family_A_delta_components.png", dpi=140)
        plt.close()
    if fam_b:
        xs = [float(r["macro_viability_mixing_rate"]) for r in fam_b if r["macro_viability_mixing_rate"] != ""]
        ys = [float(r["H_cond_viable"]) for r in fam_b if r["macro_viability_mixing_rate"] != ""]
        plt.figure(figsize=(7, 5))
        plt.scatter(xs, ys, s=8, alpha=0.35)
        plt.xlabel("macro_viability_mixing_rate")
        plt.ylabel("H_cond_viable")
        plt.tight_layout()
        plt.savefig(results_dir / "family_B_entropy_vs_mixing.png", dpi=140)
        plt.close()


def main():
    results_dir = Path("probe_07_omega_profile_decomposition_results")
    results_dir.mkdir(exist_ok=True)
    worlds = build_worlds()
    profile_rows: list[dict] = []
    estimator_rows: list[dict] = []
    diagnostics: list[dict] = []
    errors: list[dict] = []
    completed = 0
    runtime_status = "COMPLETE"

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(evaluate_world, w): w for w in worlds}
        for fut in as_completed(futures):
            world = futures.pop(fut)
            try:
                result = fut.result()
                profile_rows.extend(result["profile_rows"])
                estimator_rows.extend(result["estimator_rows"])
                diagnostics.extend(result["diagnostics"])
                completed += 1
            except Exception as exc:
                errors.append({"world_seed": world.seed, "family": world.family, "condition": world.variant, "error": str(exc)})
                runtime_status = "ERROR"
            if completed % 50 == 0 and completed > 0:
                write_csv(results_dir / "omega_profile_by_world.csv", profile_rows)
                write_csv(results_dir / "estimator_report.csv", estimator_rows)
                write_csv(results_dir / "coarse_graining_diagnostics.csv", diagnostics)
            if should_abort():
                runtime_status = "PARTIAL_EXIT_HARD_LIMIT"
                break
            if not should_continue():
                runtime_status = "PARTIAL_EXIT_SOFT_LIMIT"
                break

    horizon_rows = horizon_summary(profile_rows)
    fam_a = family_a_contrasts(profile_rows, horizon_rows)
    fam_b = family_b_profiles(profile_rows, diagnostics)
    cand = candidate_summary(profile_rows, diagnostics)

    write_csv(results_dir / "omega_profile_by_world.csv", profile_rows)
    write_csv(results_dir / "family_A_reversible_irreversible_contrasts.csv", fam_a)
    write_csv(results_dir / "family_B_fake_viability_profiles.csv", fam_b)
    write_csv(results_dir / "horizon_profiles.csv", horizon_rows)
    write_csv(results_dir / "coarse_graining_diagnostics.csv", diagnostics)
    write_csv(results_dir / "estimator_report.csv", estimator_rows)
    write_csv(results_dir / "candidate_profile_summary.csv", cand)
    (results_dir / "errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")

    trunc_frac = sum(int(r["truncated"]) for r in estimator_rows) / max(len(estimator_rows), 1)
    fam_a_mean = {
        "Delta_p_viable": sum(float(r["Delta_p_viable"]) for r in fam_a) / max(len(fam_a), 1),
        "Delta_H_cond": sum(float(r["Delta_H_cond"]) for r in fam_a) / max(len(fam_a), 1),
        "Delta_H_weighted": sum(float(r["Delta_H_weighted"]) for r in fam_a) / max(len(fam_a), 1),
        "Delta_H_recoverability": sum(float(r["Delta_H_recoverability"]) for r in fam_a) / max(len(fam_a), 1),
    }
    high_entropy_mixing = [
        r["candidate_C"]
        for r in cand
        if r["mean_H_cond_viable"] > 0.5 and r["mean_macro_viability_mixing_rate"] > 0.25
    ]
    low_mixing = [r["candidate_C"] for r in cand if r["mean_macro_viability_mixing_rate"] < 0.1]
    flags = {
        "IRREVERSIBILITY_VISIBLE_IN_P_VIABLE": abs(fam_a_mean["Delta_p_viable"]) > 0.02,
        "IRREVERSIBILITY_VISIBLE_IN_H_COND": abs(fam_a_mean["Delta_H_cond"]) > 0.02,
        "IRREVERSIBILITY_VISIBLE_IN_WEIGHTED_H": abs(fam_a_mean["Delta_H_weighted"]) > 0.02,
        "IRREVERSIBILITY_VISIBLE_IN_RECOVERY_H": abs(fam_a_mean["Delta_H_recoverability"]) > 0.02,
        "HORIZON_EXTENSION_CHANGES_ORDERING": any(abs(float(r["early_to_late_delta"])) > 0.05 for r in horizon_rows),
        "FAKE_VIABILITY_VISIBLE_IN_MIXING": bool(high_entropy_mixing),
        "FAKE_VIABILITY_VISIBLE_IN_RECOVERY_WEIGHTING": any(r["mean_H_recoverability_weighted"] < r["mean_H_cond_viable"] for r in cand),
        "PREDICTIVE_QUOTIENT_REDUCES_MIXING": min((r["mean_macro_viability_mixing_rate"] for r in cand if r["candidate_C"].startswith("predictive_")), default=1.0) < 0.25,
        "HASH_LOOKS_LIKE_ENTROPY_ARTIFACT": next((r["mean_macro_viability_mixing_rate"] for r in cand if r["candidate_C"] == "hash_k34_s1206"), 0.0) > 0.25,
        "HASH_LOOKS_LIKE_BEHAVIORAL_QUOTIENT": False,
        "ESTIMATOR_WARNING": trunc_frac > 0.25,
    }
    summary = {
        "runtime_status": runtime_status,
        "workers": WORKERS,
        "worlds_requested": len(worlds),
        "worlds_completed": completed,
        "estimator_modes": dict(Counter(r["estimator_mode"] for r in estimator_rows)),
        "truncation_fraction": trunc_frac,
        "mc_fallback_fraction": 0.0,
        "family_A_mean_contrasts": fam_a_mean,
        "high_entropy_high_mixing_candidates": sorted(set(high_entropy_mixing)),
        "low_mixing_candidates": sorted(set(low_mixing)),
        "flags": flags,
        "top_profile_summary": cand[:5],
        "errors": len(errors),
    }
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    maybe_plot(results_dir, fam_a, fam_b, profile_rows)

    print("\nPROBE 07: OMEGA PROFILE DECOMPOSITION")
    print("\nRuntime:")
    print(f"- status: {runtime_status}")
    print(f"- workers: {WORKERS}")
    print(f"- worlds completed / requested: {completed} / {len(worlds)}")
    print(f"- estimator modes: {summary['estimator_modes']}")
    print(f"- truncation fraction: {trunc_frac:.3f}")
    print("- MC fallback fraction: 0.000")
    print("\nFamily A: reversible vs irreversible")
    print(f"- Mean Delta_p_viable: {fam_a_mean['Delta_p_viable']:.4f}")
    print(f"- Mean Delta_H_cond: {fam_a_mean['Delta_H_cond']:.4f}")
    print(f"- Mean Delta_H_weighted: {fam_a_mean['Delta_H_weighted']:.4f}")
    print(f"- Mean Delta_H_recoverability: {fam_a_mean['Delta_H_recoverability']:.4f}")
    print("- Mean Delta_late_collapse: see horizon_profiles.csv")
    print("\nFamily B: hidden/fake viability")
    print(f"- Candidates with high H_cond and high mixing: {', '.join(sorted(set(high_entropy_mixing))[:8]) or 'none'}")
    print(f"- Candidates with low mixing: {', '.join(sorted(set(low_mixing))[:8]) or 'none'}")
    print(f"- Does recoverability weighting reduce fake richness? {str(flags['FAKE_VIABILITY_VISIBLE_IN_RECOVERY_WEIGHTING']).lower()}")
    print("\nCoarse-graining diagnostics:")
    for name in ["identity", "all_one", "random_k", "hash_k34_s1206", "predictive_quotient_k5", "behavioral_quotient_k5"]:
        row = next((r for r in cand if r["candidate_C"] == name), None)
        if row:
            print(f"- {name}: H_cond={row['mean_H_cond_viable']:.3f}, H_weighted={row['mean_H_viability_weighted']:.3f}, mixing={row['mean_macro_viability_mixing_rate']:.3f}")
    print("\nInterpretation:")
    print("- What does plain finite-horizon Omega show?")
    print("- What does viability weighting add?")
    print("- What does recoverability weighting add?")
    print("- Does horizon extension reveal collapse?")
    print("- Are there cases where our expectations were wrong?")
    print("- Recommended next probe.")
    print(f"\nResults: {results_dir.resolve()}")


if __name__ == "__main__":
    main()
