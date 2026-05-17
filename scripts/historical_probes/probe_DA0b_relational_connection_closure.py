#!/usr/bin/env python
"""Probe DA0b: relational connection and closure.

DA0 found that generic relation metrics were too cheap. DA0b tests relation as
persistent causal-history dependence: stable channels should carry predictive
history and closure without being mimicked by random-stepwise relation.
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
    ("W7_full_DAR", "rich", "strong", "modular_directed"),
    ("W8_full_random_relation_control", "rich", "strong", "random_stepwise"),
    ("W9_full_symmetric_control", "rich", "symmetric", "modular_directed"),
    ("W10_noise_rich_control", "rich", "noise", "independent"),
    ("W11_collapse_attractor_control", "low", "collapse", "fixed"),
    ("W12_stable_relation_weak_asymmetry", "rich", "weak", "modular_directed"),
    ("W13_stable_relation_strong_asymmetry", "rich", "strong", "modular_directed"),
    ("W14_random_stepwise_relation_weak_asymmetry", "rich", "weak", "random_stepwise"),
    ("W15_random_stepwise_relation_strong_asymmetry", "rich", "strong", "random_stepwise"),
    ("W16_fixed_but_permuted_relation", "rich", "strong", "fixed_permuted"),
    ("W17_delayed_relation_memory", "rich", "strong", "delayed_memory"),
    ("W18_relation_lock_in", "rich", "lock_in", "modular_directed"),
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
    n_sites: int
    bootstrap_repeats: int
    smoke: bool


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DA0b_relational_connection_closure_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "12000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "120")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "50,100,200")))
    p.add_argument("--n-sites", type=int, default=16)
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "400")))
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 18)
        args.n_traj = min(args.n_traj, 3000)
        args.seed_count = min(args.seed_count, 30)
        args.horizons = [50, 100]
        args.bootstrap_repeats = min(args.bootstrap_repeats, 100)
    return Config(args.out_dir, args.workers, args.n_traj, args.seed_count, args.seed_start, sorted(args.horizons), args.n_sites, args.bootstrap_repeats, args.smoke)


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


def entropy(codes: np.ndarray) -> float:
    if len(codes) == 0:
        return 0.0
    _, counts = np.unique(codes, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-12))))


def sources_for(relation: str, n: int, rng: np.random.Generator, episode_perm: np.ndarray | None = None) -> np.ndarray:
    if relation == "independent":
        return np.arange(n)
    if relation == "fixed":
        return (np.arange(n) - 1) % n
    if relation in {"modular_directed", "delayed_memory"}:
        module = max(4, n // 4)
        src = np.arange(n)
        for i in range(n):
            src[i] = (i - 1) if i % module else (i + module - 1) % n
        return src
    if relation == "random_stepwise":
        return rng.integers(0, n, size=n)
    if relation == "fixed_permuted":
        base = (np.arange(n) - 1) % n
        if episode_perm is None:
            return base
        inv = np.empty_like(episode_perm)
        inv[episode_perm] = np.arange(n)
        return episode_perm[base[inv]]
    raise KeyError(relation)


def simulate(world: World, horizon: int, n_sites: int, n_traj: int, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(80_000 + seed * 1009 + horizon * 31 + abs(hash(world.name)) % 10_000)
    q = world.q
    x = np.zeros((n_traj, n_sites), dtype=np.int16) if q == 1 else rng.integers(0, q, size=(n_traj, n_sites), dtype=np.int16)
    traj = np.empty((horizon + 1, n_traj, n_sites), dtype=np.int16)
    source_hist = np.empty((horizon, n_sites), dtype=np.int16)
    traj[0] = x
    memory = x.copy()
    episode_perm = rng.permutation(n_sites) if world.relation == "fixed_permuted" else None
    fixed_src = sources_for(world.relation, n_sites, rng, episode_perm)
    for t in range(horizon):
        src = sources_for(world.relation, n_sites, rng, episode_perm) if world.relation == "random_stepwise" else fixed_src
        source_hist[t] = src
        neigh = memory[:, src] if world.relation == "delayed_memory" else x[:, src]
        if q == 1:
            proposal = x
        elif world.asymmetry == "noise":
            proposal = rng.integers(0, q, size=x.shape, dtype=np.int16)
        elif world.asymmetry == "collapse":
            proposal = np.where(rng.random(size=x.shape) < 0.20, 0, x)
        elif world.asymmetry == "lock_in":
            proposal = np.where(rng.random(size=x.shape) < 0.82, neigh, x)
        else:
            if world.relation == "independent":
                influence = x
            elif world.asymmetry == "symmetric":
                influence = np.where(rng.random(size=x.shape) < 0.50, x, neigh)
            else:
                influence = np.where(rng.random(size=x.shape) < 0.70, neigh, x)
            probs = [0.09, 0.70, 0.21] if world.asymmetry == "weak" else [0.05, 0.58, 0.37]
            if world.asymmetry == "symmetric":
                probs = [0.11, 0.78, 0.11]
            step = rng.choice(np.array([-1, 0, 1], dtype=np.int16), size=x.shape, p=probs)
            proposal = (influence + step) % q
            stay_p = 0.72 if world.asymmetry == "weak" else 0.56
            if world.asymmetry == "symmetric":
                stay_p = 0.78
            proposal = np.where(rng.random(size=x.shape) < stay_p, x, proposal)
        memory = x.copy()
        x = proposal.astype(np.int16)
        traj[t + 1] = x
    return {"traj": traj, "sources": source_hist}


def viable_mask(traj: np.ndarray, world: World) -> np.ndarray:
    if world.q <= 1:
        return np.zeros(traj.shape[1], dtype=bool)
    distinct = np.array([[len(np.unique(traj[t, j])) for j in range(traj.shape[1])] for t in range(traj.shape[0])])
    not_all_same = np.all(distinct > 1, axis=0)
    not_zero = ~np.any(np.all(traj == 0, axis=2), axis=0)
    floor = 2 if world.q >= 4 else 1
    distinction_ok = np.all(distinct > floor, axis=0) if world.q >= 4 else not_all_same
    return not_all_same & not_zero & distinction_ok


def prediction_accuracy(keys: np.ndarray, target: np.ndarray) -> float:
    if len(keys) == 0:
        return 0.0
    correct = 0
    total = 0
    for k in np.unique(keys):
        mask = keys == k
        vals, counts = np.unique(target[mask], return_counts=True)
        correct += int(np.max(counts))
        total += int(np.sum(counts))
    return float(correct / max(total, 1))


def segment_slices(T: int) -> list[slice]:
    a = max(1, T // 3)
    return [slice(0, a), slice(a, 2 * a), slice(2 * a, T)]


def influence_by_segment(traj: np.ndarray, sources: np.ndarray, viable: np.ndarray, world: World) -> tuple[list[float], float]:
    if not np.any(viable) or world.q <= 1:
        return [0.0, 0.0, 0.0], 0.0
    tv = traj[:, viable]
    gains = []
    ranks = []
    for sl in segment_slices(sources.shape[0]):
        edge_gains = []
        for t in range(sl.start, sl.stop):
            for i, j in enumerate(sources[t]):
                self_key = tv[t, :, i]
                pair_key = self_key.astype(np.int64) * 17 + tv[t, :, j]
                target = tv[t + 1, :, i]
                edge_gains.append(prediction_accuracy(pair_key, target) - prediction_accuracy(self_key, target))
        gains.append(float(np.mean(edge_gains)) if edge_gains else 0.0)
        ranks.append(np.array(edge_gains, dtype=float))
    common = min(len(ranks[0]), len(ranks[-1]))
    if common > 2 and np.std(ranks[0][:common]) > 1e-12 and np.std(ranks[-1][:common]) > 1e-12:
        corr = float(np.corrcoef(ranks[0][:common], ranks[-1][:common])[0, 1])
    else:
        corr = 0.0
    return gains, corr


def connection_predictivity(traj: np.ndarray, sources: np.ndarray, viable: np.ndarray, world: World, seed: int) -> dict[str, float]:
    if not np.any(viable) or world.q <= 1:
        return {"future_prediction_self_only": 0.0, "future_prediction_self_plus_true_relation": 0.0, "future_prediction_self_plus_shuffled_relation": 0.0, "connection_predictive_gain": 0.0, "relation_shuffle_delta": 0.0}
    rng = np.random.default_rng(81_000 + seed)
    tv = traj[:, viable]
    self_acc = []
    true_acc = []
    shuf_acc = []
    for t in range(sources.shape[0]):
        shuf_src = rng.permutation(sources[t])
        for i, j in enumerate(sources[t]):
            target = tv[t + 1, :, i]
            self_key = tv[t, :, i]
            true_key = self_key.astype(np.int64) * 17 + tv[t, :, j]
            shuf_key = self_key.astype(np.int64) * 17 + tv[t, :, shuf_src[i]]
            self_acc.append(prediction_accuracy(self_key, target))
            true_acc.append(prediction_accuracy(true_key, target))
            shuf_acc.append(prediction_accuracy(shuf_key, target))
    s = float(np.mean(self_acc))
    tr = float(np.mean(true_acc))
    sh = float(np.mean(shuf_acc))
    return {
        "future_prediction_self_only": s,
        "future_prediction_self_plus_true_relation": tr,
        "future_prediction_self_plus_shuffled_relation": sh,
        "connection_predictive_gain": tr - s,
        "relation_shuffle_delta": tr - sh,
    }


def relation_lineage(traj: np.ndarray, sources: np.ndarray, viable: np.ndarray, world: World, seed: int) -> dict[str, float]:
    if not np.any(viable) or world.q <= 1:
        return {"relation_lineage_survival_depth": 0.0, "relation_lineage_branching_entropy": 0.0, "relation_lineage_extinction_rate": 1.0, "relation_lineage_merge_rate": 1.0, "relation_lineage_shuffle_delta": 0.0}
    rng = np.random.default_rng(82_000 + seed)
    tv = traj[:, viable]
    surv = []
    shuf_surv = []
    branch = []
    merge = []
    for t in range(sources.shape[0]):
        src = sources[t]
        shuf = rng.permutation(src)
        pred = tv[t][:, src]
        real = tv[t + 1]
        shpred = tv[t][:, shuf]
        surv.append(float(np.mean(pred == real)))
        shuf_surv.append(float(np.mean(shpred == real)))
        pairs = pred.astype(np.int64) * max(world.q, 2) + real
        branch.append(entropy(pairs.reshape(-1)))
        merge.append(float(max(0, len(np.unique(pred)) - len(np.unique(real))) / max(len(np.unique(pred)), 1)))
    m = float(np.mean(surv))
    return {
        "relation_lineage_survival_depth": m,
        "relation_lineage_branching_entropy": float(np.mean(branch)),
        "relation_lineage_extinction_rate": 1.0 - m,
        "relation_lineage_merge_rate": float(np.mean(merge)),
        "relation_lineage_shuffle_delta": m - float(np.mean(shuf_surv)),
    }


def closure_metrics(traj: np.ndarray, viable: np.ndarray, world: World) -> dict[str, float]:
    if not np.any(viable) or world.q <= 1:
        return {"closure_rate": 0.0, "lineage_recurrence_rate": 0.0, "recoverable_alternative_count": 0.0, "branching_after_closure": 0.0, "lock_in_index": 1.0, "closure_without_lock_in": 0.0}
    tv = traj[:, viable]
    mid = tv.shape[0] // 2
    closure = np.mean(tv[-1] == tv[mid])
    recur = np.mean([np.any(np.all(tv[t] == tv[0], axis=1)) for t in range(mid, tv.shape[0])])
    final_rows = np.ascontiguousarray(tv[-1])
    _, counts = np.unique(final_rows, axis=0, return_counts=True)
    lock = float(np.max(counts) / np.sum(counts)) if len(counts) else 1.0
    alt = float(len(counts))
    branch = entropy(tv[-1].reshape(-1)) / max(math.log2(max(world.q, 2)), 1e-9)
    cwl = float(closure * branch * (1.0 - lock))
    return {
        "closure_rate": float(closure),
        "lineage_recurrence_rate": float(recur),
        "recoverable_alternative_count": alt,
        "branching_after_closure": float(branch),
        "lock_in_index": lock,
        "closure_without_lock_in": cwl,
    }


def task(task_def: tuple[World, int, int, Config]) -> dict[str, object]:
    world, T, seed, cfg = task_def
    sim = simulate(world, T, cfg.n_sites, cfg.n_traj, seed)
    traj = sim["traj"]
    sources = sim["sources"]
    viable = viable_mask(traj, world)
    gains, rank_corr = influence_by_segment(traj, sources, viable, world)
    row = {
        "world": world.name,
        "distinction": world.distinction,
        "asymmetry": world.asymmetry,
        "relation": world.relation,
        "q": world.q,
        "T": T,
        "seed": seed,
        "p_viable": float(np.mean(viable)),
        "edge_influence_early": gains[0],
        "edge_influence_middle": gains[1],
        "edge_influence_late": gains[2],
        "edge_influence_rank_correlation_early_late": rank_corr,
        "relation_identity_persistence": float(max(0.0, np.mean(gains) * max(rank_corr, 0.0))),
    }
    row.update(connection_predictivity(traj, sources, viable, world, seed))
    row.update(relation_lineage(traj, sources, viable, world, seed))
    row.update(closure_metrics(traj, viable, world))
    row["viable_slack_score"] = row["relation_identity_persistence"] + row["relation_shuffle_delta"] + row["relation_lineage_survival_depth"] + row["closure_without_lock_in"]
    return row


def append_bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(83_000)
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
            else:
                lo = hi = mean
            rows.append({**base, "metric": metric, "mean": mean, "ci_low": float(lo), "ci_high": float(hi), "n_seeds": int(len(seeds))})
    return pd.DataFrame(rows)


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_rows.csv")
    means = raw.groupby(["world", "distinction", "asymmetry", "relation", "q", "T"], as_index=False).mean(numeric_only=True)
    means.to_csv(out / "viable_slack_profile.csv", index=False)
    raw[["world", "T", "seed", "edge_influence_early", "edge_influence_middle", "edge_influence_late", "edge_influence_rank_correlation_early_late", "relation_identity_persistence"]].to_csv(out / "relation_identity_persistence.csv", index=False)
    raw[["world", "T", "seed", "future_prediction_self_only", "future_prediction_self_plus_true_relation", "future_prediction_self_plus_shuffled_relation", "connection_predictive_gain", "relation_shuffle_delta"]].to_csv(out / "connection_predictivity.csv", index=False)
    raw[["world", "T", "seed", "relation_lineage_survival_depth", "relation_lineage_branching_entropy", "relation_lineage_extinction_rate", "relation_lineage_merge_rate", "relation_lineage_shuffle_delta"]].to_csv(out / "relation_conditioned_lineage.csv", index=False)
    raw[["world", "T", "seed", "closure_rate", "lineage_recurrence_rate", "recoverable_alternative_count", "branching_after_closure", "lock_in_index", "closure_without_lock_in"]].to_csv(out / "closure_without_lockin.csv", index=False)
    rankings = means.groupby("world", as_index=False).mean(numeric_only=True).sort_values("viable_slack_score", ascending=False)
    rankings.to_csv(out / "world_rankings.csv", index=False)
    controls = control_rejection(rankings)
    controls.to_csv(out / "control_rejection.csv", index=False)
    boot = append_bootstrap(raw, ["world", "T"], ["relation_identity_persistence", "connection_predictive_gain", "relation_shuffle_delta", "relation_lineage_survival_depth", "closure_without_lock_in", "viable_slack_score"], cfg.bootstrap_repeats)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    est = means[["world", "T", "p_viable", "recoverable_alternative_count", "lock_in_index", "viable_slack_score"]].copy()
    est["estimator_warning"] = np.where(est["p_viable"] <= 0.01, "LOW_VIABILITY", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, rankings, controls)
    summary = make_summary(cfg, started, rankings, controls, est)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def val(rankings: pd.DataFrame, world: str, metric: str) -> float:
    sub = rankings[rankings["world"] == world]
    return float(sub.iloc[0][metric]) if len(sub) else 0.0


def control_rejection(rankings: pd.DataFrame) -> pd.DataFrame:
    full = "W7_full_DAR"
    stable = max(val(rankings, "W12_stable_relation_weak_asymmetry", "viable_slack_score"), val(rankings, "W13_stable_relation_strong_asymmetry", "viable_slack_score"), val(rankings, full, "viable_slack_score"))
    checks = [
        ("random_stepwise_relation", max(val(rankings, "W14_random_stepwise_relation_weak_asymmetry", "viable_slack_score"), val(rankings, "W15_random_stepwise_relation_strong_asymmetry", "viable_slack_score"), val(rankings, "W8_full_random_relation_control", "viable_slack_score")), stable),
        ("fixed_but_permuted_relation", val(rankings, "W16_fixed_but_permuted_relation", "viable_slack_score"), stable),
        ("relation_lock_in", val(rankings, "W18_relation_lock_in", "closure_without_lock_in"), val(rankings, full, "closure_without_lock_in")),
        ("noise_rich_control", val(rankings, "W10_noise_rich_control", "viable_slack_score"), stable),
        ("collapse_attractor_control", val(rankings, "W11_collapse_attractor_control", "viable_slack_score"), stable),
        ("symmetric_transition_control", val(rankings, "W9_full_symmetric_control", "relation_identity_persistence"), val(rankings, full, "relation_identity_persistence")),
        ("independent_sites_control", val(rankings, "W1_distinction_only", "viable_slack_score"), stable),
    ]
    return pd.DataFrame([{"control": c, "control_value": cv, "reference_value": rv, "control_rejected": bool(rv > cv)} for c, cv, rv in checks])


def make_summary(cfg: Config, started: float, rankings: pd.DataFrame, controls: pd.DataFrame, est: pd.DataFrame) -> dict[str, object]:
    best = rankings.iloc[0]
    full = rankings[rankings["world"] == "W7_full_DAR"].iloc[0]
    metrics = ["relation_identity_persistence", "connection_predictive_gain", "relation_lineage_survival_depth", "closure_without_lock_in"]
    full_top = sum(bool(rankings.sort_values(m, ascending=False).iloc[0]["world"] == "W7_full_DAR") for m in metrics)
    null_worlds = {"W8_full_random_relation_control", "W10_noise_rich_control", "W11_collapse_attractor_control", "W18_relation_lock_in"}
    null_top = sum(bool(rankings.sort_values(m, ascending=False).iloc[0]["world"] in null_worlds) for m in metrics)
    control_map = controls.set_index("control")["control_rejected"].to_dict()
    stable_adv = max(val(rankings, "W7_full_DAR", "viable_slack_score"), val(rankings, "W13_stable_relation_strong_asymmetry", "viable_slack_score")) - max(val(rankings, "W8_full_random_relation_control", "viable_slack_score"), val(rankings, "W15_random_stepwise_relation_strong_asymmetry", "viable_slack_score"))
    passes = bool(control_map.get("random_stepwise_relation") and control_map.get("relation_lock_in") and full_top >= 2 and null_top <= 1)
    rec = "DA0b relation refinement passes smoke; proceed to DA1 viable slack phase sweep." if passes else "DA0b does not yet cleanly isolate persistent relation; inspect controls before scaling."
    return {
        "probe": "DA0b_relational_connection_closure",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "worlds": [w.name for w in worlds()],
        "best_world": str(best["world"]),
        "relation_refinement_result": {
            "relation_shuffled_rejected": bool(control_map.get("random_stepwise_relation")),
            "random_stepwise_rejected": bool(control_map.get("random_stepwise_relation")),
            "stable_relation_advantage": float(stable_adv),
            "full_DAR_top_metric_count": int(full_top),
            "null_control_top_metric_count": int(null_top),
        },
        "full_DAR_profile": {
            "p_viable": float(full["p_viable"]),
            "relation_identity_persistence": float(full["relation_identity_persistence"]),
            "connection_predictive_gain": float(full["connection_predictive_gain"]),
            "relation_shuffle_delta": float(full["relation_shuffle_delta"]),
            "relation_lineage_survival_depth": float(full["relation_lineage_survival_depth"]),
            "closure_rate": float(full["closure_rate"]),
            "recoverable_alternative_count": float(full["recoverable_alternative_count"]),
            "lock_in_index": float(full["lock_in_index"]),
            "closure_without_lock_in": float(full["closure_without_lock_in"]),
        },
        "control_results": control_map,
        "recommendation": rec,
        "next_probe": "DA1_viable_slack_phase_sweep" if passes else "DA0b_relation_metric_revision_or_branch_pause",
        "estimator_warnings": sorted(est.loc[est["estimator_warning"] != "", "world"].unique().tolist()),
    }


def make_plots(out: Path, rankings: pd.DataFrame, controls: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    plots = [
        ("relation_identity_persistence", "relation_identity_persistence_by_world.png"),
        ("connection_predictive_gain", "connection_predictive_gain_by_world.png"),
        ("relation_shuffle_delta", "relation_shuffle_delta_by_world.png"),
        ("relation_lineage_survival_depth", "relation_lineage_survival_by_world.png"),
    ]
    for metric, fname in plots:
        fig, ax = plt.subplots(figsize=(10, 5))
        s = rankings.sort_values(metric)
        ax.barh(s["world"], s[metric])
        ax.set_title(metric)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(rankings["lock_in_index"], rankings["closure_rate"])
    for _, r in rankings.iterrows():
        ax.annotate(r["world"].split("_")[0], (r["lock_in_index"], r["closure_rate"]), fontsize=7)
    ax.set_xlabel("lock_in_index")
    ax.set_ylabel("closure_rate")
    ax.set_title("Closure vs lock-in")
    fig.tight_layout()
    fig.savefig(out / "closure_vs_lockin_scatter.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    full = rankings[rankings["world"] == "W7_full_DAR"].iloc[0]
    cols = ["p_viable", "relation_identity_persistence", "connection_predictive_gain", "relation_lineage_survival_depth", "closure_without_lock_in"]
    ax.plot(range(len(cols)), [full[c] for c in cols], marker="o")
    ax.set_xticks(range(len(cols)), cols, rotation=30, ha="right")
    ax.set_title("Viable slack profile radar proxy")
    fig.tight_layout()
    fig.savefig(out / "viable_slack_profile_radar.png", dpi=160)
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
    raw = cfg.out_dir / "_seed_rows.csv"
    if raw.exists():
        raw.unlink()
    started = time.monotonic()
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    tasks = [(w, T, s, cfg) for w in worlds() for T in cfg.horizons for s in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(task, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            append_rows(raw, [fut.result()])
            if i % max(1, cfg.workers * 5) == 0:
                print(json.dumps({"completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started)
    print("PROBE DA0b: RELATIONAL CONNECTION AND CLOSURE")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
