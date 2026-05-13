#!/usr/bin/env python
"""Probe DA1c: non-commutative relational history.

Tests whether asymmetry becomes load-bearing when it is implemented as
order-dependent relational history rather than directional transition bias.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


RAW_FIELDS = [
    "world", "family", "T", "seed", "p_viable", "collapse_rate", "closure_rate",
    "raw_alternative_count", "future_distinct_alternative_count",
    "future_distinct_ratio", "recoverable_alternative_count",
    "future_basin_concentration", "post_perturbation_future_distinctness",
    "return_to_same_attractor_rate", "attractor_concentration",
    "branching_after_recovery", "dynamic_lock_in_index",
    "relation_conditioned_lineage", "self_only_lineage",
    "independent_lineage", "history_mark_predictive_score",
    "relation_lineage_excess_local", "history_mark_predictive_gain",
    "order_sensitivity", "reachable_set_difference",
    "future_distinctness_order_delta", "order_to_future_predictive_gain",
    "history_erasure_delta", "history_shuffle_delta",
    "history_persistence_depth", "random_order_future_distinct_ratio",
    "BA_future_distinct_ratio", "classification",
]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seed_count: int
    seed_start: int
    horizons: list[int]
    n_sites: int
    q: int
    m: int
    bootstrap_repeats: int
    perturbation_samples: int
    smoke: bool


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DA1c_noncommutative_relational_history_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "5000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "50")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "50,100")))
    p.add_argument("--n-sites", type=int, default=16)
    p.add_argument("--q", type=int, default=4)
    p.add_argument("--memory-states", type=int, default=4)
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "200")))
    p.add_argument("--perturbation-samples", type=int, default=500)
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 18)
        args.n_traj = min(args.n_traj, 5000)
        args.seed_count = min(args.seed_count, 50)
        args.horizons = [50, 100]
        args.n_sites = 16
        args.q = 4
        args.memory_states = 4
        args.bootstrap_repeats = min(args.bootstrap_repeats, 200)
        args.perturbation_samples = min(args.perturbation_samples, 500)
    return Config(
        args.out_dir,
        args.workers,
        args.n_traj,
        args.seed_count,
        args.seed_start,
        sorted(args.horizons),
        args.n_sites,
        args.q,
        args.memory_states,
        args.bootstrap_repeats,
        args.perturbation_samples,
        args.smoke,
    )


def world_configurations() -> list[dict[str, object]]:
    rows = [
        ("W0_null_flat", "null", False, False, False, False, False, False, False),
        ("W1_distinction_only", "distinction", False, False, False, False, False, False, False),
        ("W2_relation_without_history", "relation", True, False, False, False, False, False, False),
        ("W3_bias_asymmetry_only", "bias", False, False, True, False, False, False, False),
        ("W4_commutative_relation_history", "commutative", True, True, False, True, False, False, False),
        ("W5_noncommutative_relation_history", "noncommutative", True, True, True, False, False, False, False),
        ("W6_noncommutative_no_relation_control", "no_relation_nc", False, True, True, False, False, False, False),
        ("W7_reversible_history_control", "reversible", True, True, True, False, True, False, False),
        ("W8_random_order_history_control", "random_order", True, True, True, False, False, True, False),
        ("W9_lock_in_history_control", "lock_in", True, True, True, False, False, False, True),
        ("W10_noise_rich_control", "noise", False, False, False, False, False, False, False),
        ("W11_collapse_attractor_control", "collapse", True, True, True, False, False, False, True),
    ]
    keys = ["world", "family", "stable_relation", "history_enabled", "noncommutative", "commutative", "reversible", "random_order", "lock_in"]
    return [dict(zip(keys, row)) for row in rows]


def append_row(path: Path, row: dict[str, object]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def entropy(codes: np.ndarray) -> float:
    if len(codes) == 0:
        return 0.0
    _, counts = np.unique(codes, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-12))))


def row_codes(x: np.ndarray) -> np.ndarray:
    out = np.zeros(x.shape[0], dtype=np.int64)
    for i in range(x.shape[1]):
        out = (out * 1_000_003 + x[:, i].astype(np.int64) + 17 * i) % 9_223_372_036_854_775_123
    return out


def fixed_sources(n: int) -> np.ndarray:
    src = np.arange(n)
    for i in range(n):
        src[i] = (i - 1) % n if i % 2 else (i + 1) % n
    return src


def operator_A(x: np.ndarray, h: np.ndarray, src: np.ndarray, cfg: Config, world: dict[str, object], rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    q = cfg.q
    m = cfg.m
    neigh = x[:, src]
    hist = h[:, src]
    if world["family"] == "collapse":
        return np.zeros_like(x), np.zeros_like(h)
    if world["family"] == "noise":
        return rng.integers(0, q, size=x.shape, dtype=np.int16), rng.integers(0, m, size=h.shape, dtype=np.int16)
    if world["family"] == "null":
        return np.zeros_like(x), np.zeros_like(h)
    if world["commutative"]:
        x2 = (x + neigh + hist) % q
        h2 = (h + neigh) % m
    elif world["noncommutative"]:
        x2 = (x + neigh + h) % q
        h2 = (2 * h + neigh + 1) % m
    elif world["family"] == "bias":
        x2 = (x + 1) % q
        h2 = h
    elif world["history_enabled"]:
        x2 = (x + neigh) % q
        h2 = (h + neigh) % m
    elif world["stable_relation"]:
        x2 = np.where(rng.random(size=x.shape) < 0.72, neigh, x)
        h2 = h
    else:
        x2 = (x + rng.integers(0, q, size=x.shape)) % q
        h2 = h
    if world["lock_in"]:
        x2 = np.where(rng.random(size=x.shape) < 0.82, neigh, x2)
        h2 = np.where(rng.random(size=h.shape) < 0.82, hist, h2)
    if world["reversible"]:
        h2 = np.where(rng.random(size=h.shape) < 0.45, 0, h2)
    return x2.astype(np.int16), h2.astype(np.int16)


def operator_B(x: np.ndarray, h: np.ndarray, src: np.ndarray, cfg: Config, world: dict[str, object], rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    q = cfg.q
    m = cfg.m
    neigh = x[:, src]
    hist = h[:, src]
    if world["family"] == "collapse":
        return np.zeros_like(x), np.zeros_like(h)
    if world["family"] == "noise":
        return rng.integers(0, q, size=x.shape, dtype=np.int16), rng.integers(0, m, size=h.shape, dtype=np.int16)
    if world["family"] == "null":
        return np.zeros_like(x), np.zeros_like(h)
    if world["commutative"]:
        x2 = (x + neigh + hist) % q
        h2 = (h + neigh) % m
    elif world["noncommutative"]:
        gate = (h + hist) % q
        x2 = (x + 2 * neigh + gate) % q
        h2 = (h + x + 2) % m
    elif world["family"] == "bias":
        x2 = (x + 2) % q
        h2 = h
    elif world["history_enabled"]:
        x2 = (x + neigh) % q
        h2 = (h + x) % m
    elif world["stable_relation"]:
        x2 = np.where(rng.random(size=x.shape) < 0.72, (x + neigh) % q, x)
        h2 = h
    else:
        x2 = (x + rng.integers(0, q, size=x.shape)) % q
        h2 = h
    if world["lock_in"]:
        x2 = np.where(rng.random(size=x.shape) < 0.82, neigh, x2)
        h2 = np.where(rng.random(size=h.shape) < 0.82, hist, h2)
    if world["reversible"]:
        h2 = np.where(rng.random(size=h.shape) < 0.45, 0, h2)
    return x2.astype(np.int16), h2.astype(np.int16)


def transition(x: np.ndarray, h: np.ndarray, src: np.ndarray, cfg: Config, world: dict[str, object], rng: np.random.Generator, order: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = cfg.n_sites
    if not world["stable_relation"]:
        src = np.arange(n) if world["family"] in {"distinction", "bias", "no_relation_nc"} else rng.integers(0, n, size=n)
    elif world["random_order"]:
        src = rng.permutation(src)
    if order == "random":
        order = "AB" if rng.random() < 0.5 else "BA"
    if order == "AB":
        x, h = operator_A(x, h, src, cfg, world, rng)
        x, h = operator_B(x, h, src, cfg, world, rng)
    else:
        x, h = operator_B(x, h, src, cfg, world, rng)
        x, h = operator_A(x, h, src, cfg, world, rng)
    return x, h, src


def simulate(world: dict[str, object], T: int, cfg: Config, seed: int, order: str = "AB", erase_history: bool = False, shuffle_history: bool = False) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(241_000 + seed * 1009 + T * 31 + sum(ord(c) for c in str(world["world"])) + (17 if order == "BA" else 0))
    n = cfg.n_sites
    if world["family"] == "null":
        x = np.zeros((cfg.n_traj, n), dtype=np.int16)
    else:
        x = rng.integers(0, cfg.q, size=(cfg.n_traj, n), dtype=np.int16)
    h = rng.integers(0, cfg.m, size=(cfg.n_traj, n), dtype=np.int16) if world["history_enabled"] else np.zeros((cfg.n_traj, n), dtype=np.int16)
    xs = np.empty((T + 1, cfg.n_traj, n), dtype=np.int16)
    hs = np.empty((T + 1, cfg.n_traj, n), dtype=np.int16)
    sources = np.empty((T, n), dtype=np.int16)
    xs[0] = x
    hs[0] = h
    src = fixed_sources(n)
    for t in range(T):
        x, h, src = transition(x, h, src, cfg, world, rng, order)
        if erase_history:
            h = np.zeros_like(h)
        elif shuffle_history:
            h = h[:, rng.permutation(n)]
        xs[t + 1] = x
        hs[t + 1] = h
        sources[t] = src
    return {"x": xs, "h": hs, "sources": sources}


def future_signature(x: np.ndarray, h: np.ndarray, x0: np.ndarray, xm: np.ndarray, cfg: Config) -> np.ndarray:
    x_counts = np.stack([(x == k).sum(axis=1) for k in range(cfg.q)], axis=1)
    h_counts = np.stack([(h == k).sum(axis=1) for k in range(cfg.m)], axis=1)
    changed_initial = (x != x0).sum(axis=1)
    changed_mid = (x != xm).sum(axis=1)
    sig = np.column_stack([x_counts, h_counts, changed_initial, changed_mid])
    return row_codes(sig.astype(np.int64))


def viable_mask(xs: np.ndarray, hs: np.ndarray, world: dict[str, object]) -> np.ndarray:
    del hs
    distinct = np.array([[len(np.unique(xs[t, j])) for j in range(xs.shape[1])] for t in range(xs.shape[0])])
    not_zero = ~np.any(np.all(xs == 0, axis=2), axis=0)
    if world["family"] == "noise":
        return np.all(distinct > 1, axis=0) & not_zero
    return np.all(distinct > 2, axis=0) & not_zero


def prediction_accuracy(keys: np.ndarray, target: np.ndarray) -> float:
    correct = 0
    total = 0
    for k in np.unique(keys):
        mask = keys == k
        _, counts = np.unique(target[mask], return_counts=True)
        correct += int(np.max(counts))
        total += int(np.sum(counts))
    return float(correct / max(total, 1))


def relation_lineage(tvx: np.ndarray, tvh: np.ndarray, sources: np.ndarray, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(251_000 + seed)
    rel_scores, self_scores, indep_scores, hist_scores = [], [], [], []
    for t in range(sources.shape[0]):
        shuffled = rng.permutation(sources[t])
        for i, j in enumerate(sources[t]):
            target = tvx[t + 1, :, i]
            self_key = tvx[t, :, i]
            rel_key = self_key.astype(np.int64) * 17 + tvx[t, :, j] + 31 * tvh[t, :, j]
            indep_key = self_key.astype(np.int64) * 17 + tvx[t, :, shuffled[i]] + 31 * tvh[t, :, shuffled[i]]
            hist_key = self_key.astype(np.int64) * 17 + tvh[t, :, i]
            self_scores.append(prediction_accuracy(self_key, target))
            rel_scores.append(prediction_accuracy(rel_key, target))
            indep_scores.append(prediction_accuracy(indep_key, target))
            hist_scores.append(prediction_accuracy(hist_key, target))
    rel = float(np.mean(rel_scores))
    self_only = float(np.mean(self_scores))
    independent = float(np.mean(indep_scores))
    hist = float(np.mean(hist_scores))
    return {
        "relation_conditioned_lineage": rel,
        "self_only_lineage": self_only,
        "independent_lineage": independent,
        "history_mark_predictive_score": hist,
        "relation_lineage_excess_local": rel - max(self_only, independent),
        "history_mark_predictive_gain": hist - self_only,
    }


def metric_block(sim: dict[str, np.ndarray], world: dict[str, object], cfg: Config, seed: int) -> dict[str, float]:
    xs = sim["x"]
    hs = sim["h"]
    viable = viable_mask(xs, hs, world)
    p_viable = float(np.mean(viable))
    collapse_rate = float(np.mean(np.any(np.all(xs == 0, axis=2), axis=0)))
    if not np.any(viable):
        return empty_metrics(p_viable, collapse_rate)
    tvx = xs[:, viable]
    tvh = hs[:, viable]
    T = xs.shape[0] - 1
    mid = max(1, T // 2)
    raw_alt = float(len(np.unique(row_codes(np.column_stack([tvx[mid], tvh[mid]])))))
    future_codes = future_signature(tvx[-1], tvh[-1], tvx[0], tvx[mid], cfg)
    future_distinct = float(len(np.unique(future_codes)))
    future_ratio = float(future_distinct / max(raw_alt, future_distinct, 1.0))
    _, counts = np.unique(future_codes, return_counts=True)
    concentration = float(np.max(counts) / np.sum(counts)) if len(counts) else 1.0
    closure = float(np.mean((tvx[-1] == tvx[mid]) & (tvh[-1] == tvh[mid])))
    line = relation_lineage(tvx, tvh, sim["sources"], seed)
    rng = np.random.default_rng(252_000 + seed)
    sample_count = min(cfg.perturbation_samples, tvx.shape[1])
    idx = rng.choice(tvx.shape[1], sample_count, replace=False)
    x_mid = tvx[mid, idx].copy()
    h_mid = tvh[mid, idx].copy()
    cols = rng.integers(0, cfg.n_sites, size=sample_count)
    x_pert = x_mid.copy()
    x_pert[np.arange(sample_count), cols] = (x_pert[np.arange(sample_count), cols] + 1) % cfg.q
    pert_sim = continue_from(x_pert, h_mid, world, T - mid, cfg, seed)
    pert_codes = future_signature(pert_sim["x"], pert_sim["h"], tvx[0, idx], x_mid, cfg)
    orig_codes = future_signature(tvx[-1, idx], tvh[-1, idx], tvx[0, idx], x_mid, cfg)
    return_same = float(np.mean(pert_codes == orig_codes))
    post_distinct = float(len(np.unique(pert_codes)) / max(sample_count, 1))
    _, pert_counts = np.unique(pert_codes, return_counts=True)
    attractor_conc = float(np.max(pert_counts) / np.sum(pert_counts)) if len(pert_counts) else 1.0
    branching = entropy(pert_codes) / max(math.log2(max(sample_count, 2)), 1e-9)
    dynamic_lock = float(np.clip(return_same * attractor_conc * (1.0 - future_ratio), 0.0, 1.0))
    return {
        "p_viable": p_viable,
        "collapse_rate": collapse_rate,
        "closure_rate": closure,
        "raw_alternative_count": raw_alt,
        "future_distinct_alternative_count": future_distinct,
        "future_distinct_ratio": future_ratio,
        "recoverable_alternative_count": future_distinct,
        "future_basin_concentration": concentration,
        "post_perturbation_future_distinctness": post_distinct,
        "return_to_same_attractor_rate": return_same,
        "attractor_concentration": attractor_conc,
        "branching_after_recovery": branching,
        "dynamic_lock_in_index": dynamic_lock,
        **line,
    }


def empty_metrics(p_viable: float, collapse_rate: float) -> dict[str, float]:
    keys = [
        "closure_rate", "raw_alternative_count", "future_distinct_alternative_count",
        "future_distinct_ratio", "recoverable_alternative_count", "future_basin_concentration",
        "post_perturbation_future_distinctness", "return_to_same_attractor_rate",
        "attractor_concentration", "branching_after_recovery", "dynamic_lock_in_index",
        "relation_conditioned_lineage", "self_only_lineage", "independent_lineage",
        "history_mark_predictive_score", "relation_lineage_excess_local",
        "history_mark_predictive_gain",
    ]
    out = {k: 0.0 for k in keys}
    out["p_viable"] = p_viable
    out["collapse_rate"] = collapse_rate
    out["future_basin_concentration"] = 1.0
    out["return_to_same_attractor_rate"] = 1.0
    out["attractor_concentration"] = 1.0
    out["dynamic_lock_in_index"] = 1.0
    return out


def coarse_future_ratio(sim: dict[str, np.ndarray], world: dict[str, object], cfg: Config) -> float:
    xs = sim["x"]
    hs = sim["h"]
    viable = viable_mask(xs, hs, world)
    if not np.any(viable):
        return 0.0
    tvx = xs[:, viable]
    tvh = hs[:, viable]
    mid = max(1, (xs.shape[0] - 1) // 2)
    raw_alt = float(len(np.unique(row_codes(np.column_stack([tvx[mid], tvh[mid]])))))
    future_codes = future_signature(tvx[-1], tvh[-1], tvx[0], tvx[mid], cfg)
    future_distinct = float(len(np.unique(future_codes)))
    return float(future_distinct / max(raw_alt, future_distinct, 1.0))


def continue_from(x0: np.ndarray, h0: np.ndarray, world: dict[str, object], steps: int, cfg: Config, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(253_000 + seed * 1009 + steps)
    x = x0.copy()
    h = h0.copy()
    src = fixed_sources(cfg.n_sites)
    for _ in range(steps):
        x, h, src = transition(x, h, src, cfg, world, rng, "AB")
    return {"x": x, "h": h}


def distance_between_profiles(a: dict[str, np.ndarray], b: dict[str, np.ndarray], cfg: Config) -> float:
    ac = future_signature(a["x"][-1], a["h"][-1], a["x"][0], a["x"][len(a["x"]) // 2], cfg)
    bc = future_signature(b["x"][-1], b["h"][-1], b["x"][0], b["x"][len(b["x"]) // 2], cfg)
    n = min(len(ac), len(bc))
    if n == 0:
        return 0.0
    return float(np.mean(ac[:n] != bc[:n]))


def task(task_def: tuple[dict[str, object], int, int, Config]) -> dict[str, object]:
    world, T, seed, cfg = task_def
    diag_cfg = Config(
        cfg.out_dir,
        1,
        min(700, cfg.n_traj),
        cfg.seed_count,
        cfg.seed_start,
        cfg.horizons,
        cfg.n_sites,
        cfg.q,
        cfg.m,
        cfg.bootstrap_repeats,
        min(120, cfg.perturbation_samples),
        cfg.smoke,
    )
    base = simulate(world, T, cfg, seed, "AB")
    ba = simulate(world, T, diag_cfg, seed, "BA")
    random_order = simulate(world, T, diag_cfg, seed, "random")
    erased = simulate(world, T, diag_cfg, seed, "AB", erase_history=True)
    shuffled = simulate(world, T, diag_cfg, seed, "AB", shuffle_history=True)
    row = {"world": world["world"], "family": world["family"], "T": T, "seed": seed}
    row.update(metric_block(base, world, cfg, seed))
    row["order_sensitivity"] = distance_between_profiles(base, ba, cfg)
    row["reachable_set_difference"] = row["order_sensitivity"]
    row["future_distinctness_order_delta"] = row["future_distinct_ratio"] - coarse_future_ratio(ba, world, diag_cfg)
    row["order_to_future_predictive_gain"] = max(0.0, row["order_sensitivity"] - distance_between_profiles(base, random_order, cfg))
    row["history_erasure_delta"] = row["future_distinct_ratio"] - coarse_future_ratio(erased, world, diag_cfg)
    row["history_shuffle_delta"] = row["future_distinct_ratio"] - coarse_future_ratio(shuffled, world, diag_cfg)
    row["history_persistence_depth"] = float(np.mean(base["h"][-1] == base["h"][0]))
    row["random_order_future_distinct_ratio"] = coarse_future_ratio(random_order, world, diag_cfg)
    row["BA_future_distinct_ratio"] = coarse_future_ratio(ba, world, diag_cfg)
    row["classification"] = classify(row)
    return row


def classify(row: dict[str, float]) -> str:
    if row["p_viable"] <= 0.05 or row["closure_rate"] < 0.05:
        return "underconstrained"
    if row["dynamic_lock_in_index"] >= 0.20 or row["future_basin_concentration"] >= 0.55 or row["collapse_rate"] > 0.05:
        return "lock_in"
    if row["history_erasure_delta"] <= 0.01 or row["history_shuffle_delta"] <= 0.01:
        return "history_fakeout"
    if row["raw_alternative_count"] > 100 and (row["order_sensitivity"] <= 0.05 or row["relation_lineage_excess_local"] <= 0.001):
        return "apparent_slack"
    if row["order_sensitivity"] > 0.05 and row["history_mark_predictive_gain"] > 0 and row["relation_lineage_excess_local"] > 0.001 and row["future_distinct_ratio"] > 0.10 and row["dynamic_lock_in_index"] < 0.20:
        return "primitive_pass_candidate"
    if row["raw_alternative_count"] > 100:
        return "apparent_slack"
    return "mixed_or_inconclusive"


def bootstrap(df: pd.DataFrame, metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(260_000)
    rows = []
    for key, group in df.groupby(["world", "T"], dropna=False):
        world, T = key
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            mean = float(np.mean(vals))
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            rows.append({"world": world, "T": T, "metric": metric, "mean": mean, "ci_low": float(lo), "ci_high": float(hi), "n_seeds": int(len(seeds))})
    return pd.DataFrame(rows)


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_rows.csv")
    raw["family"] = raw["family"].fillna("null")
    denom = np.maximum.reduce([
        raw["raw_alternative_count"].to_numpy(float),
        raw["future_distinct_alternative_count"].to_numpy(float),
        np.ones(len(raw), dtype=float),
    ])
    raw["future_distinct_ratio"] = raw["future_distinct_alternative_count"].to_numpy(float) / denom
    means = raw.groupby(["world", "family", "T"], as_index=False).mean(numeric_only=True)
    agg = raw.groupby(["world", "family"], as_index=False).mean(numeric_only=True)
    worlds = pd.DataFrame(world_configurations())
    worlds.to_csv(out / "world_configurations.csv", index=False)
    add_comparative_metrics(means)
    add_comparative_metrics(agg)
    means["classification"] = means.apply(lambda r: classify(r.to_dict()), axis=1)
    agg["classification"] = agg.apply(lambda r: classify(r.to_dict()), axis=1)
    means[["world", "T", "order_sensitivity", "reachable_set_difference", "future_distinctness_order_delta", "order_to_future_predictive_gain"]].to_csv(out / "order_sensitivity.csv", index=False)
    means[["world", "T", "history_mark_predictive_gain", "history_erasure_delta", "history_shuffle_delta", "history_persistence_depth"]].to_csv(out / "history_mark_load_bearing.csv", index=False)
    means[["world", "T", "relation_conditioned_lineage", "self_only_lineage", "independent_lineage", "noncommutative_relation_lineage_excess", "commutative_delta", "random_order_delta"]].to_csv(out / "relation_conditioned_noncommutative_lineage.csv", index=False)
    means[["world", "T", "asymmetric_slack_delta", "noncommutative_asymmetry_delta", "history_consequence_delta"]].to_csv(out / "asymmetry_load_bearing.csv", index=False)
    means[["world", "T", "p_viable", "closure_rate", "raw_alternative_count", "future_distinct_alternative_count", "future_distinct_ratio", "post_perturbation_future_distinctness", "recoverable_alternative_count"]].to_csv(out / "future_distinct_viable_slack.csv", index=False)
    means[["world", "T", "return_to_same_attractor_rate", "attractor_concentration", "branching_after_recovery", "dynamic_lock_in_index"]].to_csv(out / "dynamic_lock_in.csv", index=False)
    profile_cols = ["world", "family", "T", "p_viable", "order_sensitivity", "history_mark_predictive_gain", "history_erasure_delta", "noncommutative_relation_lineage_excess", "commutative_delta", "random_order_delta", "asymmetric_slack_delta", "future_distinct_ratio", "recoverable_alternative_count", "dynamic_lock_in_index", "classification"]
    means[profile_cols].to_csv(out / "diagnostic_profile.csv", index=False)
    controls = means[means["world"] != "W5_noncommutative_relation_history"]
    controls[["world", "T", "classification", "order_sensitivity", "history_mark_predictive_gain", "asymmetric_slack_delta", "dynamic_lock_in_index"]].to_csv(out / "control_rejection.csv", index=False)
    boot_metrics = ["order_sensitivity", "history_mark_predictive_gain", "history_erasure_delta", "relation_lineage_excess_local", "future_distinct_ratio", "dynamic_lock_in_index"]
    bootstrap(raw, boot_metrics, cfg.bootstrap_repeats).to_csv(out / "bootstrap_intervals.csv", index=False)
    est = means[["world", "T", "p_viable", "raw_alternative_count", "future_distinct_ratio", "dynamic_lock_in_index", "classification"]].copy()
    est["estimator_warning"] = np.where(est["p_viable"] <= 0.05, "LOW_VIABILITY", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, means)
    summary = make_summary(cfg, started, agg)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def add_comparative_metrics(df: pd.DataFrame) -> None:
    def metric(world: str, col: str) -> float:
        s = df.loc[df["world"] == world, col]
        return float(s.mean()) if len(s) else 0.0
    w4_line = metric("W4_commutative_relation_history", "relation_conditioned_lineage")
    w6_line = metric("W6_noncommutative_no_relation_control", "relation_conditioned_lineage")
    w8_line = metric("W8_random_order_history_control", "relation_conditioned_lineage")
    w4_slack = metric("W4_commutative_relation_history", "future_distinct_ratio")
    w7_order = metric("W7_reversible_history_control", "reachable_set_difference")
    for idx, row in df.iterrows():
        df.loc[idx, "noncommutative_relation_lineage_excess"] = row["relation_conditioned_lineage"] - max(row["self_only_lineage"], row["independent_lineage"], w6_line)
        df.loc[idx, "commutative_delta"] = row["relation_conditioned_lineage"] - w4_line
        df.loc[idx, "random_order_delta"] = row["relation_conditioned_lineage"] - w8_line
        df.loc[idx, "asymmetric_slack_delta"] = row["future_distinct_ratio"] - max(w4_slack, metric("W7_reversible_history_control", "future_distinct_ratio"))
        df.loc[idx, "noncommutative_asymmetry_delta"] = row["future_distinct_ratio"] - w4_slack
        df.loc[idx, "history_consequence_delta"] = row["reachable_set_difference"] - w7_order


def make_summary(cfg: Config, started: float, agg: pd.DataFrame) -> dict[str, object]:
    agg = agg.copy()
    add_comparative_metrics(agg)
    agg["classification"] = agg.apply(lambda r: classify(r.to_dict()), axis=1)
    viable_gate = (agg["p_viable"] > 0.05).astype(float)
    agg["candidate_score"] = viable_gate * (
        agg["order_sensitivity"]
        + agg["history_mark_predictive_gain"]
        + 20.0 * agg["noncommutative_relation_lineage_excess"]
        + agg["asymmetric_slack_delta"]
        + agg["future_distinct_ratio"]
        - agg["dynamic_lock_in_index"]
    ) - (1.0 - viable_gate)
    best = agg.sort_values("candidate_score", ascending=False).iloc[0]
    w5 = agg[agg["world"] == "W5_noncommutative_relation_history"].iloc[0]
    w9_lock = float(agg.loc[agg["world"] == "W9_lock_in_history_control", "dynamic_lock_in_index"].mean())
    controls = {
        "commutative_relation_history": label_for(agg, "W4_commutative_relation_history"),
        "bias_asymmetry_only": label_for(agg, "W3_bias_asymmetry_only"),
        "noncommutative_no_relation_control": label_for(agg, "W6_noncommutative_no_relation_control"),
        "reversible_history_control": label_for(agg, "W7_reversible_history_control"),
        "random_order_history_control": label_for(agg, "W8_random_order_history_control"),
        "lock_in_history_control": label_for(agg, "W9_lock_in_history_control"),
        "noise_rich_control": label_for(agg, "W10_noise_rich_control"),
        "collapse_attractor_control": label_for(agg, "W11_collapse_attractor_control"),
    }
    asym = bool(w5["asymmetric_slack_delta"] > 0)
    relation = bool(w5["noncommutative_relation_lineage_excess"] > 0)
    hist = bool(w5["history_mark_predictive_gain"] > 0 and w5["history_erasure_delta"] > 0 and w5["history_shuffle_delta"] > 0)
    future = bool(w5["future_distinct_ratio"] > 0.10 and w5["post_perturbation_future_distinctness"] > 0)
    lock_rejected = bool(label_for(agg, "W9_lock_in_history_control") != "primitive_pass_candidate" and w5["dynamic_lock_in_index"] < w9_lock)
    passed = bool(best["world"] == "W5_noncommutative_relation_history" and asym and relation and hist and future and lock_rejected and controls["bias_asymmetry_only"] != "primitive_pass_candidate")
    if passed:
        rec = "DA1c smoke supports non-commutative relational history; proceed to DA2."
        next_probe = "DA2_viable_slack_in_noncommutative_relational_histories"
    elif not asym:
        rec = "DA1c shows no load-bearing asymmetry; do not scale this DAR world family."
        next_probe = "DAR_world_family_pause_or_redesign"
    elif controls["bias_asymmetry_only"] == "primitive_pass_candidate":
        rec = "Bias-only asymmetry still passes; asymmetry remains reducible to a cheap knob."
        next_probe = "DA1c_bias_control_revision"
    elif not relation or not hist:
        rec = "History/order signal is insufficiently relation-conditioned; revise relational memory dynamics."
        next_probe = "DA1c_relation_history_revision"
    else:
        rec = "DA1c is mixed; inspect profiles before any main-scale run."
        next_probe = "DA1c_targeted_followup"
    return {
        "probe": "DA1c_noncommutative_relational_history",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "worlds": sorted(agg["world"].unique().tolist()),
        "best_world": str(best["world"]),
        "primitive_definition_update_written": True,
        "primary_result": {
            "noncommutative_history_passed": passed,
            "asymmetry_load_bearing": asym,
            "relation_load_bearing": relation,
            "history_marks_load_bearing": hist,
            "future_distinct_slack_detected": future,
            "lock_in_rejected": lock_rejected,
        },
        "best_profile": {
            "p_viable": float(best["p_viable"]),
            "order_sensitivity": float(best["order_sensitivity"]),
            "history_mark_predictive_gain": float(best["history_mark_predictive_gain"]),
            "history_erasure_delta": float(best["history_erasure_delta"]),
            "noncommutative_relation_lineage_excess": float(best["noncommutative_relation_lineage_excess"]),
            "commutative_delta": float(best["commutative_delta"]),
            "random_order_delta": float(best["random_order_delta"]),
            "asymmetric_slack_delta": float(best["asymmetric_slack_delta"]),
            "future_distinct_ratio": float(best["future_distinct_ratio"]),
            "recoverable_alternative_count": float(best["recoverable_alternative_count"]),
            "dynamic_lock_in_index": float(best["dynamic_lock_in_index"]),
        },
        "control_results": controls,
        "recommendation": rec,
        "next_probe": next_probe,
        "estimator_warnings": sorted(agg.loc[agg["p_viable"] <= 0.05, "world"].unique().tolist()),
    }


def label_for(df: pd.DataFrame, world: str) -> str:
    s = df.loc[df["world"] == world, "classification"]
    return str(s.iloc[0]) if len(s) else "missing"


def make_plots(out: Path, means: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    agg = means.groupby("world", as_index=False).mean(numeric_only=True)
    add_comparative_metrics(agg)
    labels = agg["world"].str.replace("W", "").str.replace("_", "\n")
    x = np.arange(len(agg))
    for metric, fname, ylabel in [
        ("order_sensitivity", "order_sensitivity_by_world.png", "order sensitivity"),
        ("history_mark_predictive_gain", "history_mark_predictive_gain_by_world.png", "history predictive gain"),
        ("noncommutative_relation_lineage_excess", "noncommutative_lineage_excess_by_world.png", "noncommutative lineage excess"),
        ("asymmetric_slack_delta", "asymmetric_slack_delta_by_world.png", "asymmetric slack delta"),
    ]:
        fig, ax = plt.subplots(figsize=(11, 5))
        ax.bar(x, agg[metric])
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=7)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(agg["future_distinct_ratio"], agg["dynamic_lock_in_index"])
    for _, r in agg.iterrows():
        ax.annotate(str(r["world"]).split("_")[0], (r["future_distinct_ratio"], r["dynamic_lock_in_index"]), fontsize=7)
    ax.set_xlabel("future_distinct_ratio")
    ax.set_ylabel("dynamic_lock_in_index")
    fig.tight_layout()
    fig.savefig(out / "future_distinct_vs_lockin_scatter.png", dpi=160)
    plt.close(fig)
    metrics = ["order_sensitivity", "history_mark_predictive_gain", "noncommutative_relation_lineage_excess", "asymmetric_slack_delta", "future_distinct_ratio", "dynamic_lock_in_index"]
    mat = agg[metrics].to_numpy(float)
    scale = np.maximum(np.nanmax(np.abs(mat), axis=0), 1e-9)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mat / scale, aspect="auto")
    fig.colorbar(im, ax=ax)
    ax.set_yticks(np.arange(len(agg)))
    ax.set_yticklabels(agg["world"], fontsize=7)
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels(metrics, rotation=60, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "diagnostic_profile_heatmap.png", dpi=160)
    plt.close(fig)
    class_order = {"underconstrained": 0, "apparent_slack": 1, "history_fakeout": 2, "mixed_or_inconclusive": 3, "lock_in": 4, "primitive_pass_candidate": 5}
    tmp = means.copy()
    tmp["class_code"] = tmp["classification"].map(class_order).fillna(3)
    heat = tmp.pivot_table(index="world", columns="T", values="class_code", aggfunc="first")
    fig, ax = plt.subplots(figsize=(5, 7))
    im = ax.imshow(heat.to_numpy(), aspect="auto")
    fig.colorbar(im, ax=ax)
    ax.set_yticks(np.arange(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=7)
    ax.set_xticks(np.arange(len(heat.columns)))
    ax.set_xticklabels(heat.columns)
    fig.tight_layout()
    fig.savefig(out / "control_rejection_heatmap.png", dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    raw = cfg.out_dir / "_seed_rows.csv"
    started = time.monotonic()
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    tasks = [(world, T, seed, cfg) for world in world_configurations() for T in cfg.horizons for seed in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(task, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            append_row(raw, fut.result())
            if i % max(1, cfg.workers * 5) == 0:
                print(json.dumps({"completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started)
    print("PROBE DA1c: NON-COMMUTATIVE RELATIONAL HISTORY")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
