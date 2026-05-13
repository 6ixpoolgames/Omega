#!/usr/bin/env python
"""Probe DA0: minimal distinction/asymmetry/relation worlds.

This branch deliberately avoids COM, kappa/fibers, agents, rewards, learned
representations, and path signatures. It asks whether tiny discrete worlds with
distinction, asymmetry, and relation show persistent structured viable futures
that ablations lose.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


WORLD_SPECS = [
    ("W0_null_flat", "none", "symmetric", "independent"),
    ("W1_distinction_only", "low", "symmetric", "independent"),
    ("W2_asymmetry_only", "low", "strong", "independent"),
    ("W3_relation_only", "low", "symmetric", "fixed"),
    ("W4_distinction_asymmetry", "low", "strong", "independent"),
    ("W5_distinction_relation", "low", "symmetric", "fixed"),
    ("W6_asymmetry_relation", "low", "strong", "fixed"),
    ("W7_full_DAR", "rich", "strong", "modular_directed"),
    ("W8_full_random_relation_control", "rich", "strong", "random_stepwise"),
    ("W9_full_symmetric_control", "rich", "symmetric", "modular_directed"),
    ("W10_noise_rich_control", "rich", "noise", "independent"),
    ("W11_collapse_attractor_control", "low", "collapse", "fixed"),
]


@dataclass(frozen=True)
class World:
    name: str
    distinction: str
    asymmetry: str
    relation: str
    q: int


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seed_count: int
    seed_start: int
    horizons: list[int]
    n_sites: list[int]
    bootstrap_repeats: int
    smoke: bool


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DA0_distinction_asymmetry_relation_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "10000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "100")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "50,100,200")))
    p.add_argument("--n-sites", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_N_SITES", "16,32")))
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "300")))
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 8)
        args.n_traj = min(args.n_traj, 2000)
        args.seed_count = min(args.seed_count, 20)
        args.horizons = [50, 100]
        args.n_sites = [16]
        args.bootstrap_repeats = min(args.bootstrap_repeats, 80)
    return Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seed_count=args.seed_count,
        seed_start=args.seed_start,
        horizons=sorted(args.horizons),
        n_sites=sorted(args.n_sites),
        bootstrap_repeats=args.bootstrap_repeats,
        smoke=args.smoke,
    )


def worlds() -> list[World]:
    out = []
    for name, d, a, r in WORLD_SPECS:
        q = 1 if d == "none" else 2 if d == "low" else 4
        out.append(World(name, d, a, r, q))
    return out


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def entropy_from_codes(codes: np.ndarray) -> float:
    if len(codes) == 0:
        return 0.0
    _, counts = np.unique(codes, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-12))))


def row_codes(x: np.ndarray, q: int) -> np.ndarray:
    base = max(q, 2) + 1
    out = np.zeros(x.shape[0], dtype=np.int64)
    # Hash rather than exact base expansion to avoid overflow for q=4,n=32.
    for i in range(x.shape[1]):
        out = (out * 1_000_003 + x[:, i].astype(np.int64) + 17 * i) % 9_223_372_036_854_775_123
    return out


def relation_sources(world: World, n_sites: int, rng: np.random.Generator) -> np.ndarray:
    if world.relation == "independent":
        return np.arange(n_sites)
    if world.relation == "fixed":
        return (np.arange(n_sites) - 1) % n_sites
    if world.relation == "modular_directed":
        src = np.arange(n_sites)
        module = max(4, n_sites // 4)
        for i in range(n_sites):
            if i % module == 0:
                src[i] = (i + module - 1) % n_sites
            else:
                src[i] = i - 1
        return src
    if world.relation == "random_stepwise":
        return rng.integers(0, n_sites, size=n_sites)
    raise KeyError(world.relation)


def simulate(world: World, horizon: int, n_sites: int, n_traj: int, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(71_000 + seed * 1009 + horizon * 31 + n_sites * 7 + abs(hash(world.name)) % 10_000)
    q = world.q
    if q == 1:
        x = np.zeros((n_traj, n_sites), dtype=np.int16)
    else:
        x = rng.integers(0, q, size=(n_traj, n_sites), dtype=np.int16)
    traj = np.empty((horizon + 1, n_traj, n_sites), dtype=np.int16)
    costs = np.zeros(n_traj, dtype=np.float32)
    traj[0] = x
    base_src = relation_sources(world, n_sites, rng)
    for t in range(1, horizon + 1):
        src = relation_sources(world, n_sites, rng) if world.relation == "random_stepwise" else base_src
        neigh = x[:, src]
        proposal = x.copy()
        if world.asymmetry == "noise":
            proposal = rng.integers(0, q, size=x.shape, dtype=np.int16) if q > 1 else proposal
        elif world.asymmetry == "collapse":
            collapse_mask = rng.random(size=x.shape) < 0.18
            proposal = np.where(collapse_mask, 0, x)
        else:
            if world.relation == "independent":
                influence = x
            elif world.asymmetry == "symmetric":
                influence = np.where(rng.random(size=x.shape) < 0.50, x, neigh)
            else:
                influence = np.where(rng.random(size=x.shape) < 0.72, neigh, x)
            if q > 1:
                stay_p = 0.78 if world.asymmetry == "symmetric" else 0.58
                step = rng.choice(np.array([-1, 0, 1], dtype=np.int16), size=x.shape, p=[0.11, 0.78, 0.11] if world.asymmetry == "symmetric" else [0.06, 0.58, 0.36])
                if world.asymmetry == "weak":
                    step = rng.choice(np.array([-1, 0, 1], dtype=np.int16), size=x.shape, p=[0.09, 0.70, 0.21])
                    stay_p = 0.70
                proposal = (influence + step) % q
                proposal = np.where(rng.random(size=x.shape) < stay_p, x, proposal)
        changed = proposal != x
        forward = ((proposal - x) % max(q, 2)) == 1
        reverse = ((x - proposal) % max(q, 2)) == 1
        costs += changed.mean(axis=1).astype(np.float32)
        if world.asymmetry in {"weak", "strong"}:
            costs += (0.04 * reverse.mean(axis=1) - 0.015 * forward.mean(axis=1)).astype(np.float32)
        x = proposal.astype(np.int16)
        traj[t] = x
    return {"traj": traj, "costs": costs}


def viability(traj: np.ndarray, costs: np.ndarray, world: World, horizon: int) -> np.ndarray:
    if world.q <= 1:
        return np.zeros(traj.shape[1], dtype=bool)
    per_traj_distinct = np.array([
        [len(np.unique(traj[t, j])) for j in range(traj.shape[1])]
        for t in range(traj.shape[0])
    ])
    not_all_same = np.all(per_traj_distinct > 1, axis=0)
    not_zero = ~np.any(np.all(traj == 0, axis=2), axis=0)
    budget = 0.50 * horizon if world.asymmetry != "noise" else 0.72 * horizon
    cost_ok = costs <= budget
    floor = 2 if world.q >= 4 else 1
    distinction_ok = np.all(per_traj_distinct > floor, axis=0) if world.q >= 4 else not_all_same
    return not_all_same & not_zero & cost_ok & distinction_ok


def lineage_metrics(traj: np.ndarray, viable: np.ndarray, world: World) -> dict[str, float]:
    if not np.any(viable) or world.q <= 1:
        return {"lineage_survival_depth": 0.0, "lineage_branching_entropy": 0.0, "lineage_merge_rate": 1.0, "lineage_extinction_rate": 1.0}
    tv = traj[:, viable]
    survival = []
    branch_counts = []
    merge_rates = []
    for t in range(1, tv.shape[0]):
        same = tv[t] == tv[0]
        survival.append(float(np.mean(same)))
        pairs = tv[t - 1].astype(np.int64) * max(world.q, 2) + tv[t].astype(np.int64)
        branch_counts.append(entropy_from_codes(pairs.reshape(-1)))
        prev_unique = len(np.unique(tv[t - 1].reshape(-1)))
        curr_unique = len(np.unique(tv[t].reshape(-1)))
        merge_rates.append(float(max(0, prev_unique - curr_unique) / max(prev_unique, 1)))
    return {
        "lineage_survival_depth": float(np.mean(survival)),
        "lineage_branching_entropy": float(np.mean(branch_counts)),
        "lineage_merge_rate": float(np.mean(merge_rates)),
        "lineage_extinction_rate": float(1.0 - np.mean(survival)),
    }


def asymmetry_metrics(traj: np.ndarray, viable: np.ndarray, world: World) -> dict[str, float]:
    if not np.any(viable) or world.q <= 1:
        return {"time_reversal_asymmetry": 0.0, "transition_irreversibility": 0.0, "future_option_gradient": 0.0, "asymmetric_filter_selectivity": 0.0}
    tv = traj[:, viable]
    q = max(world.q, 2)
    fwd = ((tv[1:] - tv[:-1]) % q == 1).mean()
    rev = ((tv[:-1] - tv[1:]) % q == 1).mean()
    stay = (tv[1:] == tv[:-1]).mean()
    early_div = np.mean([len(np.unique(row)) for row in tv[: max(2, tv.shape[0] // 4)].reshape(-1, tv.shape[2])])
    late_div = np.mean([len(np.unique(row)) for row in tv[-max(2, tv.shape[0] // 4) :].reshape(-1, tv.shape[2])])
    return {
        "time_reversal_asymmetry": float(abs(fwd - rev)),
        "transition_irreversibility": float(max(0.0, fwd - rev)),
        "future_option_gradient": float(late_div - early_div),
        "asymmetric_filter_selectivity": float((fwd + 1e-9) / max(rev + stay, 1e-9)),
    }


def relation_metrics(traj: np.ndarray, viable: np.ndarray, world: World) -> dict[str, float]:
    if not np.any(viable) or world.q <= 1:
        return {"mutual_dependence_between_sites": 0.0, "relation_persistence": 0.0, "component_coupling": 0.0, "network_propagation_depth": 0.0, "relational_nonfactorization": 0.0, "relational_excess": 0.0, "relation_shuffle_delta": 0.0}
    tv = traj[:, viable]
    final = tv[-1]
    joint_h = entropy_from_codes(row_codes(final, world.q))
    site_h = float(np.mean([entropy_from_codes(final[:, i]) for i in range(final.shape[1])]))
    sum_site_h = float(np.sum([entropy_from_codes(final[:, i]) for i in range(final.shape[1])]))
    nonfact = float(max(0.0, sum_site_h - joint_h) / max(sum_site_h, 1e-9))
    adjacent_same = np.mean(final == np.roll(final, 1, axis=1))
    random_same = np.mean(final == final[np.random.default_rng(72_500).permutation(len(final))])
    relation_persist = np.mean(tv[1:] == np.roll(tv[:-1], 1, axis=2)) if world.relation != "independent" else 0.0
    return {
        "mutual_dependence_between_sites": nonfact,
        "relation_persistence": float(relation_persist),
        "component_coupling": float(adjacent_same - random_same),
        "network_propagation_depth": float(np.mean([np.mean(tv[t] == np.roll(tv[0], t % final.shape[1], axis=1)) for t in range(1, tv.shape[0])])),
        "relational_nonfactorization": nonfact,
        "relational_excess": float(joint_h - site_h * final.shape[1] / max(final.shape[1], 1)),
        "relation_shuffle_delta": float(max(0.0, adjacent_same - random_same)),
    }


def richness_metrics(traj: np.ndarray, viable: np.ndarray, world: World) -> dict[str, float]:
    if world.q <= 1:
        return {"p_viable": 0.0, "viable_future_entropy": 0.0, "viability_weighted_richness": 0.0, "noncollapse_diversity": 0.0, "state_diversity": 0.0, "distinction_entropy": 0.0, "distinction_survival": 0.0, "nontrivial_future_classes": 0.0}
    final = traj[-1]
    p = float(np.mean(viable))
    final_v = final[viable] if np.any(viable) else final[:0]
    h = entropy_from_codes(row_codes(final_v, world.q)) if len(final_v) else 0.0
    state_div = float(np.mean([len(np.unique(row)) for row in final])) / world.q
    distinction_entropy = float(np.mean([entropy_from_codes(final[:, i]) for i in range(final.shape[1])]))
    distinct0 = np.array([len(np.unique(row)) for row in traj[0]])
    distinctT = np.array([len(np.unique(row)) for row in final])
    survival = float(np.mean(distinctT / np.maximum(distinct0, 1)))
    return {
        "p_viable": p,
        "viable_future_entropy": h,
        "viability_weighted_richness": p * h,
        "noncollapse_diversity": state_div,
        "state_diversity": state_div,
        "distinction_entropy": distinction_entropy,
        "distinction_survival": survival,
        "nontrivial_future_classes": float(len(np.unique(row_codes(final_v, world.q)))) if len(final_v) else 0.0,
    }


def task(task_def: tuple[World, int, int, int, Config]) -> dict[str, object]:
    world, horizon, n_sites, seed, cfg = task_def
    sim = simulate(world, horizon, n_sites, cfg.n_traj, seed)
    traj = sim["traj"]
    viable = viability(traj, sim["costs"], world, horizon)
    row = {
        "world": world.name,
        "distinction": world.distinction,
        "asymmetry": world.asymmetry,
        "relation": world.relation,
        "q": world.q,
        "T": horizon,
        "n_sites": n_sites,
        "seed": seed,
    }
    row.update(richness_metrics(traj, viable, world))
    row.update(lineage_metrics(traj, viable, world))
    row.update(asymmetry_metrics(traj, viable, world))
    row.update(relation_metrics(traj, viable, world))
    row["structured_viable_richness"] = row["viability_weighted_richness"] * (1.0 + row["relational_nonfactorization"]) * (1.0 + row["time_reversal_asymmetry"])
    row["DAR_branch_score"] = row["lineage_survival_depth"] + row["time_reversal_asymmetry"] + row["relational_nonfactorization"] + row["structured_viable_richness"]
    return row


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(73_000)
    rows = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            mean = float(np.mean(vals))
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
                std = float(np.std(vals, ddof=1))
            else:
                lo = hi = mean
                std = 0.0
            rows.append({**base, "metric": metric, "mean": mean, "std": std, "ci_low": float(lo), "ci_high": float(hi), "n_seeds": int(len(seeds))})
    return pd.DataFrame(rows)


def build_outputs(cfg: Config, started: float, status: str) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_rows.csv")
    profiles = raw.groupby(["world", "distinction", "asymmetry", "relation", "q", "T", "n_sites"], as_index=False).mean(numeric_only=True)
    profiles.to_csv(out / "dar_profile_by_world.csv", index=False)
    raw[["world", "T", "n_sites", "seed", "lineage_survival_depth", "lineage_branching_entropy", "lineage_merge_rate", "lineage_extinction_rate"]].to_csv(out / "lineage_metrics.csv", index=False)
    raw[["world", "T", "n_sites", "seed", "time_reversal_asymmetry", "transition_irreversibility", "future_option_gradient", "asymmetric_filter_selectivity"]].to_csv(out / "asymmetry_metrics.csv", index=False)
    raw[["world", "T", "n_sites", "seed", "mutual_dependence_between_sites", "relation_persistence", "component_coupling", "network_propagation_depth", "relational_nonfactorization", "relational_excess", "relation_shuffle_delta"]].to_csv(out / "relation_metrics.csv", index=False)
    raw[["world", "T", "n_sites", "seed", "p_viable", "viable_future_entropy", "viability_weighted_richness", "noncollapse_diversity", "state_diversity", "distinction_entropy", "distinction_survival", "nontrivial_future_classes"]].to_csv(out / "structured_richness.csv", index=False)
    configs = pd.DataFrame([w.__dict__ for w in worlds()])
    configs.to_csv(out / "world_configurations.csv", index=False)
    ablation = build_ablation(profiles)
    ablation.to_csv(out / "ablation_results.csv", index=False)
    controls = build_controls(profiles)
    controls.to_csv(out / "control_rejection.csv", index=False)
    boot = bootstrap(raw, ["world", "T", "n_sites"], ["lineage_survival_depth", "time_reversal_asymmetry", "relational_nonfactorization", "structured_viable_richness", "DAR_branch_score"], cfg.bootstrap_repeats)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    est = profiles[["world", "T", "n_sites", "p_viable", "nontrivial_future_classes", "state_diversity", "DAR_branch_score"]].copy()
    est["estimator_warning"] = np.where(est["p_viable"] <= 0.01, "LOW_VIABILITY", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, profiles, ablation, controls)
    summary = make_summary(cfg, started, status, profiles, ablation, controls, est)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def build_ablation(profiles: pd.DataFrame) -> pd.DataFrame:
    rows = []
    full = profiles[profiles["world"] == "W7_full_DAR"]
    if not len(full):
        return pd.DataFrame()
    full_mean = full.mean(numeric_only=True)
    for world, group in profiles.groupby("world"):
        mean = group.mean(numeric_only=True)
        rows.append({
            "world": world,
            "delta_lineage_vs_full_DAR": float(full_mean["lineage_survival_depth"] - mean["lineage_survival_depth"]),
            "delta_asymmetry_vs_full_DAR": float(full_mean["time_reversal_asymmetry"] - mean["time_reversal_asymmetry"]),
            "delta_relation_vs_full_DAR": float(full_mean["relational_nonfactorization"] - mean["relational_nonfactorization"]),
            "delta_structured_richness_vs_full_DAR": float(full_mean["structured_viable_richness"] - mean["structured_viable_richness"]),
            "full_DAR_beats_world": bool(full_mean["DAR_branch_score"] > mean["DAR_branch_score"]),
        })
    return pd.DataFrame(rows)


def build_controls(profiles: pd.DataFrame) -> pd.DataFrame:
    means = profiles.groupby("world", as_index=False).mean(numeric_only=True)
    full = means[means["world"] == "W7_full_DAR"].iloc[0]
    checks = [
        ("noise_rich_control", "W10_noise_rich_control", "lineage_survival_depth"),
        ("collapse_attractor_control", "W11_collapse_attractor_control", "lineage_survival_depth"),
        ("relation_shuffled_control", "W8_full_random_relation_control", "relational_nonfactorization"),
        ("symmetric_transition_control", "W9_full_symmetric_control", "time_reversal_asymmetry"),
        ("independent_sites_control", "W1_distinction_only", "relational_nonfactorization"),
    ]
    rows = []
    for control, world, metric in checks:
        c = means[means["world"] == world].iloc[0]
        rows.append({
            "control": control,
            "control_world": world,
            "metric": metric,
            "full_DAR_value": float(full[metric]),
            "control_value": float(c[metric]),
            "control_rejected": bool(full[metric] > c[metric]),
        })
    return pd.DataFrame(rows)


def make_summary(cfg: Config, started: float, status: str, profiles: pd.DataFrame, ablation: pd.DataFrame, controls: pd.DataFrame, est: pd.DataFrame) -> dict[str, object]:
    means = profiles.groupby("world", as_index=False).mean(numeric_only=True)
    best = means.sort_values("DAR_branch_score", ascending=False).iloc[0]
    full = means[means["world"] == "W7_full_DAR"].iloc[0]
    rank_metrics = ["lineage_survival_depth", "time_reversal_asymmetry", "relational_nonfactorization", "structured_viable_richness"]
    top_counts = sum(bool(means.sort_values(m, ascending=False).iloc[0]["world"] == "W7_full_DAR") for m in rank_metrics)
    null_top_counts = sum(bool(str(means.sort_values(m, ascending=False).iloc[0]["world"]).startswith(("W8", "W9", "W10", "W11"))) for m in rank_metrics)
    distinction_required = bool(full["lineage_survival_depth"] > means[means["world"].isin(["W0_null_flat", "W2_asymmetry_only"])]["lineage_survival_depth"].max())
    asymmetry_required = bool(full["time_reversal_asymmetry"] > means[means["world"].isin(["W5_distinction_relation", "W9_full_symmetric_control"])]["time_reversal_asymmetry"].max())
    relation_required = bool(full["relational_nonfactorization"] > means[means["world"].isin(["W1_distinction_only", "W4_distinction_asymmetry", "W8_full_random_relation_control"])]["relational_nonfactorization"].max())
    full_best = bool(best["world"] == "W7_full_DAR" or top_counts >= 3)
    promising = bool(top_counts >= 3 and null_top_counts <= 1 and controls["control_rejected"].mean() >= 0.8)
    if promising:
        recommendation = "DAR branch is promising; proceed to DA1 focused on the strongest primitive signal."
        next_probe = "DA1_distinction_lineage_or_relation_deepening"
    else:
        recommendation = "DA0 does not yet show a clean conjunction effect; inspect which primitive/control dominated before scaling."
        next_probe = "DA0_metric_refinement_or_branch_pause"
    return {
        "probe": "DA0_distinction_asymmetry_relation",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "worlds": [w.name for w in worlds()],
        "primitive_ablation_result": {
            "distinction_required": distinction_required,
            "asymmetry_required": asymmetry_required,
            "relation_required": relation_required,
            "full_DAR_best": full_best,
            "full_DAR_top_metric_count": int(top_counts),
            "null_control_top_metric_count": int(null_top_counts),
        },
        "best_world": str(best["world"]),
        "full_DAR_profile": {
            "p_viable": float(full["p_viable"]),
            "lineage_survival_depth": float(full["lineage_survival_depth"]),
            "lineage_branching_entropy": float(full["lineage_branching_entropy"]),
            "time_reversal_asymmetry": float(full["time_reversal_asymmetry"]),
            "relational_excess": float(full["relational_excess"]),
            "relation_shuffle_delta": float(full["relation_shuffle_delta"]),
            "structured_viable_richness": float(full["structured_viable_richness"]),
        },
        "control_results": controls.set_index("control")["control_rejected"].to_dict(),
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": sorted(est.loc[est["estimator_warning"] != "", "world"].unique().tolist()),
    }


def make_plots(out: Path, profiles: pd.DataFrame, ablation: pd.DataFrame, controls: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    means = profiles.groupby("world", as_index=False).mean(numeric_only=True)
    radar_cols = ["p_viable", "lineage_survival_depth", "time_reversal_asymmetry", "relational_nonfactorization", "structured_viable_richness"]
    fig, ax = plt.subplots(figsize=(8, 5))
    full = means[means["world"] == "W7_full_DAR"].iloc[0]
    vals = [float(full[c]) for c in radar_cols]
    ax.plot(range(len(vals)), vals, marker="o")
    ax.set_xticks(range(len(vals)), radar_cols, rotation=30, ha="right")
    ax.set_title("DAR profile radar proxy")
    fig.tight_layout()
    fig.savefig(out / "dar_profile_radar.png", dpi=160)
    plt.close(fig)
    for col, fname, title in [
        ("lineage_survival_depth", "lineage_survival_by_world.png", "Lineage survival by world"),
        ("time_reversal_asymmetry", "asymmetry_by_world.png", "Asymmetry by world"),
        ("relational_nonfactorization", "relational_excess_by_world.png", "Relational nonfactorization by world"),
        ("structured_viable_richness", "viable_richness_by_world.png", "Structured viable richness by world"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 5))
        s = means.sort_values(col)
        ax.barh(s["world"], s[col])
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    mat = ablation[["delta_lineage_vs_full_DAR", "delta_asymmetry_vs_full_DAR", "delta_relation_vs_full_DAR", "delta_structured_richness_vs_full_DAR"]].to_numpy(float)
    im = ax.imshow(mat, aspect="auto")
    ax.set_yticks(range(len(ablation)), ablation["world"])
    ax.set_xticks(range(mat.shape[1]), ["lineage", "asym", "relation", "richness"], rotation=30)
    fig.colorbar(im, ax=ax)
    ax.set_title("Ablation heatmap")
    fig.tight_layout()
    fig.savefig(out / "ablation_heatmap.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    vals = controls.set_index("control")["control_rejected"].astype(float)
    ax.barh(vals.index, vals.values)
    ax.set_title("Control rejection heatmap proxy")
    fig.tight_layout()
    fig.savefig(out / "control_rejection_heatmap.png", dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = cfg.out_dir / "_seed_rows.csv"
    if raw_path.exists():
        raw_path.unlink()
    started = time.monotonic()
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    tasks = [(w, T, n, s, cfg) for w in worlds() for T in cfg.horizons for n in cfg.n_sites for s in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(task, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            append_rows(raw_path, [fut.result()])
            if i % max(1, cfg.workers * 5) == 0:
                print(json.dumps({"completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started, "COMPLETE")
    print("PROBE DA0: DISTINCTION / ASYMMETRY / RELATION")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
