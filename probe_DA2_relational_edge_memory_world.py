#!/usr/bin/env python
"""Probe DA2: relational edge-memory world.

Tests whether future-distinct viable slack persists only when causal history is
stored on persistent directed relations rather than local node memory.
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
    "world", "family", "T", "seed", "p_viable", "collapse_rate",
    "active_edge_memory_fraction", "edge_memory_entropy",
    "cross_node_support_balance", "largest_component_support_fraction",
    "closure_rate", "raw_alternative_count",
    "future_distinct_alternative_count", "future_distinct_ratio",
    "recoverable_alternative_count", "post_perturbation_future_distinctness",
    "return_to_same_attractor_rate", "attractor_concentration",
    "branching_after_recovery", "dynamic_lock_in_index",
    "edge_memory_predictive_gain", "edge_memory_erasure_delta",
    "edge_memory_shuffle_delta", "edge_memory_persistence_depth",
    "edge_memory_to_future_distinctness", "relation_conditioned_alternative_count",
    "self_only_alternative_count", "local_memory_alternative_count",
    "independent_alternative_count", "relation_slack_excess",
    "order_sensitivity", "reachable_set_difference",
    "future_distinctness_order_delta", "order_to_future_predictive_gain",
    "classification",
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
    revision: bool


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DA2_relational_edge_memory_world_results"))
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
    p.add_argument("--revision", action="store_true", help="Run the single documented revision variant.")
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
        args.perturbation_samples = min(args.perturbation_samples, 160)
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
        args.revision,
    )


def world_configurations() -> list[dict[str, object]]:
    rows = [
        ("W0_null_flat", "null"),
        ("W1_distinction_only", "distinction"),
        ("W2_no_relation", "no_relation"),
        ("W3_local_memory_only", "local_memory"),
        ("W4_relation_without_memory", "relation_no_memory"),
        ("W5_random_stepwise_relation_memory", "random_relation_memory"),
        ("W6_commutative_edge_memory", "commutative_edge"),
        ("W7_reversible_edge_memory", "reversible_edge"),
        ("W8_full_relational_edge_memory", "full_edge"),
        ("W9_edge_memory_lock_in", "edge_lock_in"),
        ("W10_noise_rich_control", "noise"),
        ("W11_collapse_attractor_control", "collapse"),
    ]
    return [{"world": w, "family": f} for w, f in rows]


def append_row(path: Path, row: dict[str, object]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def edge_list(n: int) -> tuple[np.ndarray, np.ndarray]:
    src = []
    dst = []
    for j in range(n):
        src.extend([(j - 1) % n, (j - 3) % n])
        dst.extend([j, j])
    return np.array(src, dtype=np.int16), np.array(dst, dtype=np.int16)


def row_codes(x: np.ndarray) -> np.ndarray:
    out = np.zeros(x.shape[0], dtype=np.int64)
    for i in range(x.shape[1]):
        out = (out * 1_000_003 + x[:, i].astype(np.int64) + 17 * i) % 9_223_372_036_854_775_123
    return out


def entropy_from_values(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    _, counts = np.unique(values, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-12))))


def prediction_accuracy(keys: np.ndarray, target: np.ndarray) -> float:
    correct = 0
    total = 0
    for k in np.unique(keys):
        mask = keys == k
        _, counts = np.unique(target[mask], return_counts=True)
        correct += int(np.max(counts))
        total += int(np.sum(counts))
    return float(correct / max(total, 1))


def transition(
    x: np.ndarray,
    edge_mem: np.ndarray,
    local_mem: np.ndarray,
    src: np.ndarray,
    dst: np.ndarray,
    cfg: Config,
    world: dict[str, object],
    rng: np.random.Generator,
    order: str,
    erase_edges: bool = False,
    shuffle_edges: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    family = str(world["family"])
    q = cfg.q
    m = cfg.m
    n = cfg.n_sites
    e_count = len(src)
    if family == "null":
        return np.zeros_like(x), np.zeros_like(edge_mem), np.zeros_like(local_mem)
    if family == "collapse":
        return np.zeros_like(x), np.zeros_like(edge_mem), np.zeros_like(local_mem)
    if family == "noise":
        x2 = rng.integers(0, q, size=x.shape, dtype=np.int16)
        edge2 = rng.integers(0, m, size=edge_mem.shape, dtype=np.int16)
        return x2, edge2, local_mem
    if family == "distinction":
        return ((x + rng.integers(0, q, size=x.shape)) % q).astype(np.int16), edge_mem, local_mem
    if family == "no_relation":
        local2 = (2 * local_mem + x + 1) % m
        x2 = (x + local2 + rng.integers(0, 2, size=x.shape)) % q
        return x2.astype(np.int16), np.zeros_like(edge_mem), local2.astype(np.int16)
    if family == "local_memory":
        local2 = (local_mem + x + 1) % m
        x2 = (x + local2) % q
        return x2.astype(np.int16), np.zeros_like(edge_mem), local2.astype(np.int16)

    if family == "random_relation_memory":
        perm = rng.permutation(n)
        src_t = perm[src]
        dst_t = dst
    else:
        src_t = src
        dst_t = dst
    if order == "reverse":
        edge_order = np.arange(e_count - 1, -1, -1)
    elif order == "random":
        edge_order = rng.permutation(e_count)
    else:
        edge_order = np.arange(e_count)

    x2 = x.copy()
    edge2 = edge_mem.copy()
    local2 = local_mem.copy()
    if family == "relation_no_memory":
        incoming = np.zeros_like(x)
        for e in edge_order:
            incoming[:, dst_t[e]] = (incoming[:, dst_t[e]] + x[:, src_t[e]]) % q
        x2 = np.where(rng.random(size=x.shape) < 0.65, incoming, x)
        return x2.astype(np.int16), np.zeros_like(edge_mem), local2

    for e in edge_order:
        i = int(src_t[e])
        j = int(dst_t[e])
        h = edge2[:, e]
        source = x2[:, i]
        target = x2[:, j]
        if family == "commutative_edge":
            proposal = (target + source + h) % q
            h2 = (h + source) % m
        elif family == "reversible_edge":
            proposal = (target + source + h) % q
            h2 = np.where(rng.random(x.shape[0]) < 0.45, 0, (h + source + 1) % m)
        else:
            # Non-commutative: earlier incoming updates alter target and edge
            # memory before later edges see the same destination.
            gate = (h + target) % q
            proposal = (target + source + gate + 1) % q
            h2 = (2 * h + source + target + e % m) % m
        if cfg.revision and family == "full_edge":
            # Revision: require two-edge relational support by injecting a
            # second stable incoming edge into the same target update.
            sibling = e - 1 if e % 2 else min(e + 1, e_count - 1)
            proposal = (proposal + x2[:, int(src_t[sibling])] + edge2[:, sibling]) % q
            h2 = (h2 + edge2[:, sibling]) % m
        if family == "edge_lock_in":
            proposal = np.where(rng.random(x.shape[0]) < 0.90, source, proposal)
            h2 = np.where(rng.random(x.shape[0]) < 0.90, h, h2)
        x2[:, j] = proposal.astype(np.int16)
        edge2[:, e] = h2.astype(np.int16)
    if erase_edges:
        edge2 = np.zeros_like(edge2)
    if shuffle_edges:
        edge2 = edge2[:, rng.permutation(e_count)]
    return x2.astype(np.int16), edge2.astype(np.int16), local2.astype(np.int16)


def simulate(world: dict[str, object], T: int, cfg: Config, seed: int, order: str = "forward", erase_edges: bool = False, shuffle_edges: bool = False) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(310_000 + seed * 1009 + T * 31 + sum(ord(c) for c in str(world["world"])) + (19 if order == "reverse" else 0))
    src, dst = edge_list(cfg.n_sites)
    e_count = len(src)
    x = np.zeros((cfg.n_traj, cfg.n_sites), dtype=np.int16) if world["family"] == "null" else rng.integers(0, cfg.q, size=(cfg.n_traj, cfg.n_sites), dtype=np.int16)
    edge_mem = rng.integers(0, cfg.m, size=(cfg.n_traj, e_count), dtype=np.int16) if str(world["family"]) not in {"null", "distinction", "no_relation", "local_memory", "relation_no_memory"} else np.zeros((cfg.n_traj, e_count), dtype=np.int16)
    local_mem = rng.integers(0, cfg.m, size=(cfg.n_traj, cfg.n_sites), dtype=np.int16) if str(world["family"]) in {"no_relation", "local_memory"} else np.zeros((cfg.n_traj, cfg.n_sites), dtype=np.int16)
    xs = np.empty((T + 1, cfg.n_traj, cfg.n_sites), dtype=np.int16)
    hs = np.empty((T + 1, cfg.n_traj, e_count), dtype=np.int16)
    ls = np.empty((T + 1, cfg.n_traj, cfg.n_sites), dtype=np.int16)
    xs[0], hs[0], ls[0] = x, edge_mem, local_mem
    for t in range(T):
        x, edge_mem, local_mem = transition(x, edge_mem, local_mem, src, dst, cfg, world, rng, order, erase_edges, shuffle_edges)
        xs[t + 1], hs[t + 1], ls[t + 1] = x, edge_mem, local_mem
    return {"x": xs, "h": hs, "local": ls, "src": src, "dst": dst}


def support_factors(xs: np.ndarray, hs: np.ndarray, cfg: Config) -> dict[str, np.ndarray | float]:
    active = hs != 0
    active_fraction = np.mean(active, axis=(0, 2))
    edge_ent = np.array([entropy_from_values(hs[:, j, :].reshape(-1)) / max(math.log2(cfg.m), 1e-9) for j in range(hs.shape[1])])
    node_support = np.zeros((hs.shape[1], cfg.n_sites), dtype=float)
    _, dst = edge_list(cfg.n_sites)
    for node in range(cfg.n_sites):
        node_support[:, node] = np.mean(active[:, :, dst == node], axis=(0, 2))
    total = np.sum(node_support, axis=1)
    largest = np.max(node_support, axis=1) / np.maximum(total, 1e-9)
    visible_distinct = np.array([np.mean([len(np.unique(xs[:, j, i])) > 2 for i in range(cfg.n_sites)]) for j in range(xs.shape[1])])
    viable = (active_fraction > 0.20) & (edge_ent > 0.25) & (largest < 0.65) & (visible_distinct > 0.50)
    return {
        "viable": viable,
        "active_edge_memory_fraction": float(np.mean(active_fraction)),
        "edge_memory_entropy": float(np.mean(edge_ent)),
        "cross_node_support_balance": float(np.mean(1.0 - largest)),
        "largest_component_support_fraction": float(np.mean(largest)),
    }


def future_signature(x: np.ndarray, h: np.ndarray, local: np.ndarray, x0: np.ndarray, xm: np.ndarray, cfg: Config) -> np.ndarray:
    x_counts = np.stack([(x == k).sum(axis=1) for k in range(cfg.q)], axis=1)
    h_counts = np.stack([(h == k).sum(axis=1) for k in range(cfg.m)], axis=1)
    changed_initial = (x != x0).sum(axis=1)
    changed_mid = (x != xm).sum(axis=1)
    local_sum = np.sum(local, axis=1) % cfg.m
    return row_codes(np.column_stack([x_counts, h_counts, changed_initial, changed_mid, local_sum]).astype(np.int64))


def metric_block(sim: dict[str, np.ndarray], world: dict[str, object], cfg: Config, seed: int) -> dict[str, float]:
    xs, hs, ls = sim["x"], sim["h"], sim["local"]
    support = support_factors(xs, hs, cfg)
    viable = support["viable"]
    p_viable = float(np.mean(viable))
    collapse_rate = float(np.mean(np.any(np.all(xs == 0, axis=2), axis=0)))
    out = {
        "p_viable": p_viable,
        "collapse_rate": collapse_rate,
        "active_edge_memory_fraction": support["active_edge_memory_fraction"],
        "edge_memory_entropy": support["edge_memory_entropy"],
        "cross_node_support_balance": support["cross_node_support_balance"],
        "largest_component_support_fraction": support["largest_component_support_fraction"],
    }
    if not np.any(viable):
        out.update(empty_dynamic())
        return out
    tvx, tvh, tvl = xs[:, viable], hs[:, viable], ls[:, viable]
    T = xs.shape[0] - 1
    mid = max(1, T // 2)
    raw_codes = row_codes(np.column_stack([tvx[mid], tvh[mid], tvl[mid]]))
    raw_alt = float(len(np.unique(raw_codes)))
    future_codes = future_signature(tvx[-1], tvh[-1], tvl[-1], tvx[0], tvx[mid], cfg)
    future_distinct = float(len(np.unique(future_codes)))
    future_ratio = float(future_distinct / max(raw_alt, future_distinct, 1.0))
    _, counts = np.unique(future_codes, return_counts=True)
    concentration = float(np.max(counts) / np.sum(counts)) if len(counts) else 1.0
    closure = float(np.mean(tvx[-1] == tvx[mid]))
    relation = relation_metrics(tvx, tvh, tvl, sim["src"], sim["dst"], seed)
    perturb = perturbation_metrics(tvx, tvh, tvl, world, cfg, seed, mid)
    out.update({
        "closure_rate": closure,
        "raw_alternative_count": raw_alt,
        "future_distinct_alternative_count": future_distinct,
        "future_distinct_ratio": future_ratio,
        "recoverable_alternative_count": future_distinct,
        "attractor_concentration": concentration,
        **relation,
        **perturb,
    })
    out["dynamic_lock_in_index"] = float(np.clip(out["return_to_same_attractor_rate"] * out["attractor_concentration"] * (1.0 - out["future_distinct_ratio"]), 0.0, 1.0))
    return out


def empty_dynamic() -> dict[str, float]:
    return {
        "closure_rate": 0.0, "raw_alternative_count": 0.0,
        "future_distinct_alternative_count": 0.0, "future_distinct_ratio": 0.0,
        "recoverable_alternative_count": 0.0, "post_perturbation_future_distinctness": 0.0,
        "return_to_same_attractor_rate": 1.0, "attractor_concentration": 1.0,
        "branching_after_recovery": 0.0, "dynamic_lock_in_index": 1.0,
        "edge_memory_predictive_gain": 0.0, "relation_conditioned_alternative_count": 0.0,
        "self_only_alternative_count": 0.0, "local_memory_alternative_count": 0.0,
        "independent_alternative_count": 0.0, "relation_slack_excess": 0.0,
    }


def relation_metrics(tvx: np.ndarray, tvh: np.ndarray, tvl: np.ndarray, src: np.ndarray, dst: np.ndarray, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(320_000 + seed)
    if tvx.shape[1] > 900:
        idx = rng.choice(tvx.shape[1], 900, replace=False)
        tvx = tvx[:, idx]
        tvh = tvh[:, idx]
        tvl = tvl[:, idx]
    rel_scores, self_scores, local_scores, indep_scores = [], [], [], []
    edge_gain = []
    T = tvx.shape[0] - 1
    time_points = range(0, T, max(1, T // 12))
    edge_points = range(0, len(src), 2)
    for t in time_points:
        shuf = rng.permutation(len(src))
        for e in edge_points:
            i, j = int(src[e]), int(dst[e])
            target = tvx[t + 1, :, j]
            self_key = tvx[t, :, j]
            local_key = self_key.astype(np.int64) * 17 + tvl[t, :, j]
            rel_key = self_key.astype(np.int64) * 17 + tvx[t, :, i] * 31 + tvh[t, :, e]
            indep_key = self_key.astype(np.int64) * 17 + tvx[t, :, src[shuf[e]]] * 31 + tvh[t, :, shuf[e]]
            self_acc = prediction_accuracy(self_key, target)
            rel_acc = prediction_accuracy(rel_key, target)
            self_scores.append(self_acc)
            local_scores.append(prediction_accuracy(local_key, target))
            rel_scores.append(rel_acc)
            indep_scores.append(prediction_accuracy(indep_key, target))
            edge_gain.append(rel_acc - self_acc)
    rel = float(np.mean(rel_scores))
    self_only = float(np.mean(self_scores))
    local = float(np.mean(local_scores))
    indep = float(np.mean(indep_scores))
    return {
        "relation_conditioned_alternative_count": rel,
        "self_only_alternative_count": self_only,
        "local_memory_alternative_count": local,
        "independent_alternative_count": indep,
        "relation_slack_excess": rel - max(self_only, local, indep),
        "edge_memory_predictive_gain": float(np.mean(edge_gain)),
    }


def perturbation_metrics(tvx: np.ndarray, tvh: np.ndarray, tvl: np.ndarray, world: dict[str, object], cfg: Config, seed: int, mid: int) -> dict[str, float]:
    rng = np.random.default_rng(330_000 + seed)
    sample_count = min(cfg.perturbation_samples, tvx.shape[1])
    idx = rng.choice(tvx.shape[1], sample_count, replace=False)
    x_mid, h_mid, l_mid = tvx[mid, idx].copy(), tvh[mid, idx].copy(), tvl[mid, idx].copy()
    cols = rng.integers(0, cfg.n_sites, size=sample_count)
    x_pert = x_mid.copy()
    x_pert[np.arange(sample_count), cols] = (x_pert[np.arange(sample_count), cols] + 1) % cfg.q
    future = continue_from(x_pert, h_mid, l_mid, world, tvx.shape[0] - 1 - mid, cfg, seed)
    pert_codes = future_signature(future["x"], future["h"], future["local"], tvx[0, idx], x_mid, cfg)
    orig_codes = future_signature(tvx[-1, idx], tvh[-1, idx], tvl[-1, idx], tvx[0, idx], x_mid, cfg)
    _, counts = np.unique(pert_codes, return_counts=True)
    concentration = float(np.max(counts) / np.sum(counts)) if len(counts) else 1.0
    return {
        "return_to_same_attractor_rate": float(np.mean(pert_codes == orig_codes)),
        "post_perturbation_future_distinctness": float(len(np.unique(pert_codes)) / max(sample_count, 1)),
        "branching_after_recovery": entropy_from_values(pert_codes) / max(math.log2(max(sample_count, 2)), 1e-9),
        "attractor_concentration": concentration,
    }


def continue_from(x: np.ndarray, h: np.ndarray, local: np.ndarray, world: dict[str, object], steps: int, cfg: Config, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(340_000 + seed * 1009 + steps)
    src, dst = edge_list(cfg.n_sites)
    for _ in range(steps):
        x, h, local = transition(x, h, local, src, dst, cfg, world, rng, "forward")
    return {"x": x, "h": h, "local": local}


def future_ratio(sim: dict[str, np.ndarray], world: dict[str, object], cfg: Config) -> float:
    xs, hs, ls = sim["x"], sim["h"], sim["local"]
    support = support_factors(xs, hs, cfg)
    viable = support["viable"]
    if not np.any(viable):
        return 0.0
    tvx, tvh, tvl = xs[:, viable], hs[:, viable], ls[:, viable]
    mid = max(1, (xs.shape[0] - 1) // 2)
    raw_codes = row_codes(np.column_stack([tvx[mid], tvh[mid], tvl[mid]]))
    raw_alt = float(len(np.unique(raw_codes)))
    future_codes = future_signature(tvx[-1], tvh[-1], tvl[-1], tvx[0], tvx[mid], cfg)
    future_distinct = float(len(np.unique(future_codes)))
    return float(future_distinct / max(raw_alt, future_distinct, 1.0))


def profile_distance(a: dict[str, np.ndarray], b: dict[str, np.ndarray], cfg: Config) -> float:
    ac = future_signature(a["x"][-1], a["h"][-1], a["local"][-1], a["x"][0], a["x"][len(a["x"]) // 2], cfg)
    bc = future_signature(b["x"][-1], b["h"][-1], b["local"][-1], b["x"][0], b["x"][len(b["x"]) // 2], cfg)
    n = min(len(ac), len(bc))
    return float(np.mean(ac[:n] != bc[:n])) if n else 0.0


def task(task_def: tuple[dict[str, object], int, int, Config]) -> dict[str, object]:
    world, T, seed, cfg = task_def
    diag = Config(cfg.out_dir, 1, min(700, cfg.n_traj), cfg.seed_count, cfg.seed_start, cfg.horizons, cfg.n_sites, cfg.q, cfg.m, cfg.bootstrap_repeats, min(120, cfg.perturbation_samples), cfg.smoke, cfg.revision)
    base = simulate(world, T, cfg, seed)
    rev = simulate(world, T, diag, seed, "reverse")
    rnd = simulate(world, T, diag, seed, "random")
    erased = simulate(world, T, diag, seed, erase_edges=True)
    shuffled = simulate(world, T, diag, seed, shuffle_edges=True)
    row = {"world": world["world"], "family": world["family"], "T": T, "seed": seed}
    row.update(metric_block(base, world, cfg, seed))
    row["edge_memory_erasure_delta"] = row["future_distinct_ratio"] - future_ratio(erased, world, diag)
    row["edge_memory_shuffle_delta"] = row["future_distinct_ratio"] - future_ratio(shuffled, world, diag)
    row["edge_memory_persistence_depth"] = float(np.mean(base["h"][-1] == base["h"][0]))
    row["edge_memory_to_future_distinctness"] = row["future_distinct_ratio"] * max(row["edge_memory_predictive_gain"], 0.0)
    row["order_sensitivity"] = profile_distance(base, rev, diag)
    row["reachable_set_difference"] = row["order_sensitivity"]
    row["future_distinctness_order_delta"] = row["future_distinct_ratio"] - future_ratio(rev, world, diag)
    row["order_to_future_predictive_gain"] = max(0.0, row["order_sensitivity"] - profile_distance(base, rnd, diag))
    row["classification"] = classify(row)
    return row


def classify(row: dict[str, float]) -> str:
    if row["p_viable"] <= 0.05 or row["collapse_rate"] > 0.20:
        return "underconstrained"
    if row["dynamic_lock_in_index"] >= 0.20 or row["attractor_concentration"] >= 0.55:
        return "lock_in"
    if row["relation_slack_excess"] <= 0.001 and row["family"] in {"no_relation", "local_memory"}:
        return "local_history_fakeout"
    if row["edge_memory_predictive_gain"] <= 0.001 or row["edge_memory_erasure_delta"] <= 0.01 or row["edge_memory_shuffle_delta"] <= 0.01:
        return "history_fakeout"
    if row["order_sensitivity"] <= 0.05 or row["future_distinctness_order_delta"] <= 0:
        return "commutative_fakeout"
    if row["relation_slack_excess"] <= 0.001:
        return "generic_coupling_fakeout"
    if row["future_distinct_ratio"] > 0.10 and row["post_perturbation_future_distinctness"] > 0.10:
        return "primitive_pass_candidate"
    return "apparent_slack"


def add_comparative_metrics(df: pd.DataFrame) -> None:
    def val(world: str, col: str) -> float:
        s = df.loc[df["world"] == world, col]
        return float(s.mean()) if len(s) else 0.0
    w8_fd = val("W8_full_relational_edge_memory", "future_distinct_ratio")
    for idx, row in df.iterrows():
        df.loc[idx, "noncommutative_asymmetry_delta"] = row["future_distinct_ratio"] - val("W6_commutative_edge_memory", "future_distinct_ratio")
        df.loc[idx, "full_world_delta"] = w8_fd - row["future_distinct_ratio"]


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_rows.csv")
    raw["family"] = raw["family"].fillna("null")
    means = raw.groupby(["world", "family", "T"], as_index=False).mean(numeric_only=True)
    agg = raw.groupby(["world", "family"], as_index=False).mean(numeric_only=True)
    add_comparative_metrics(means)
    add_comparative_metrics(agg)
    means["classification"] = means.apply(lambda r: classify(r.to_dict()), axis=1)
    agg["classification"] = agg.apply(lambda r: classify(r.to_dict()), axis=1)
    pd.DataFrame(world_configurations()).to_csv(out / "world_configurations.csv", index=False)
    means[["world", "T", "edge_memory_predictive_gain", "edge_memory_erasure_delta", "edge_memory_shuffle_delta", "edge_memory_persistence_depth", "edge_memory_to_future_distinctness"]].to_csv(out / "edge_memory_load_bearing.csv", index=False)
    means[["world", "T", "relation_conditioned_alternative_count", "self_only_alternative_count", "local_memory_alternative_count", "independent_alternative_count", "relation_slack_excess"]].to_csv(out / "relation_load_bearing.csv", index=False)
    means[["world", "T", "order_sensitivity", "reachable_set_difference", "future_distinctness_order_delta", "order_to_future_predictive_gain", "noncommutative_asymmetry_delta"]].to_csv(out / "noncommutative_asymmetry_load_bearing.csv", index=False)
    means[["world", "T", "p_viable", "closure_rate", "raw_alternative_count", "future_distinct_alternative_count", "future_distinct_ratio", "post_perturbation_future_distinctness", "recoverable_alternative_count"]].to_csv(out / "future_distinct_viable_slack.csv", index=False)
    means[["world", "T", "return_to_same_attractor_rate", "attractor_concentration", "branching_after_recovery", "dynamic_lock_in_index"]].to_csv(out / "dynamic_lock_in.csv", index=False)
    primitive = primitive_table(agg)
    primitive.to_csv(out / "primitive_mutual_necessity.csv", index=False)
    profile_cols = ["world", "family", "T", "p_viable", "edge_memory_predictive_gain", "edge_memory_erasure_delta", "edge_memory_shuffle_delta", "relation_slack_excess", "order_sensitivity", "noncommutative_asymmetry_delta", "future_distinct_ratio", "recoverable_alternative_count", "dynamic_lock_in_index", "branching_after_recovery", "classification"]
    means[profile_cols].to_csv(out / "diagnostic_profile.csv", index=False)
    means[means["world"] != "W8_full_relational_edge_memory"][["world", "T", "classification", "relation_slack_excess", "future_distinct_ratio", "dynamic_lock_in_index"]].to_csv(out / "control_rejection.csv", index=False)
    bootstrap(raw, ["edge_memory_predictive_gain", "edge_memory_erasure_delta", "relation_slack_excess", "order_sensitivity", "future_distinct_ratio", "dynamic_lock_in_index"], cfg.bootstrap_repeats).to_csv(out / "bootstrap_intervals.csv", index=False)
    est = means[["world", "T", "p_viable", "active_edge_memory_fraction", "edge_memory_entropy", "future_distinct_ratio", "classification"]].copy()
    est["estimator_warning"] = np.where(est["p_viable"] <= 0.05, "LOW_VIABILITY", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, means, primitive)
    summary = make_summary(cfg, started, agg, primitive)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def primitive_table(agg: pd.DataFrame) -> pd.DataFrame:
    def v(world: str, col: str) -> float:
        s = agg.loc[agg["world"] == world, col]
        return float(s.mean()) if len(s) else 0.0
    w8 = "W8_full_relational_edge_memory"
    rows = []
    comparisons = {
        "distinction_required": ["W0_null_flat"],
        "relation_required": ["W2_no_relation", "W3_local_memory_only"],
        "edge_memory_required": ["W4_relation_without_memory"],
        "persistent_relation_required": ["W5_random_stepwise_relation_memory"],
        "asymmetry_required": ["W6_commutative_edge_memory", "W7_reversible_edge_memory"],
        "lock_in_rejected": ["W9_edge_memory_lock_in"],
    }
    for name, worlds in comparisons.items():
        rows.append({
            "criterion": name,
            "w8_future_distinct_ratio": v(w8, "future_distinct_ratio"),
            "best_control_future_distinct_ratio": max(v(w, "future_distinct_ratio") for w in worlds),
            "w8_relation_slack_excess": v(w8, "relation_slack_excess"),
            "best_control_relation_slack_excess": max(v(w, "relation_slack_excess") for w in worlds),
            "passed": v(w8, "future_distinct_ratio") > max(v(w, "future_distinct_ratio") for w in worlds) and v(w8, "relation_slack_excess") > max(v(w, "relation_slack_excess") for w in worlds),
        })
    return pd.DataFrame(rows)


def bootstrap(df: pd.DataFrame, metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(350_000)
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


def make_summary(cfg: Config, started: float, agg: pd.DataFrame, primitive: pd.DataFrame) -> dict[str, object]:
    agg = agg.copy()
    add_comparative_metrics(agg)
    agg["classification"] = agg.apply(lambda r: classify(r.to_dict()), axis=1)
    agg["score"] = (agg["p_viable"] > 0.05).astype(float) * (
        agg["edge_memory_predictive_gain"]
        + agg["edge_memory_erasure_delta"]
        + 20 * agg["relation_slack_excess"]
        + agg["order_sensitivity"]
        + agg["noncommutative_asymmetry_delta"]
        + agg["future_distinct_ratio"]
        - agg["dynamic_lock_in_index"]
    )
    best = agg.sort_values("score", ascending=False).iloc[0]
    w8 = agg[agg["world"] == "W8_full_relational_edge_memory"].iloc[0]
    controls = {
        "no_relation": label_for(agg, "W2_no_relation"),
        "local_memory_only": label_for(agg, "W3_local_memory_only"),
        "relation_without_memory": label_for(agg, "W4_relation_without_memory"),
        "random_stepwise_relation_memory": label_for(agg, "W5_random_stepwise_relation_memory"),
        "commutative_edge_memory": label_for(agg, "W6_commutative_edge_memory"),
        "reversible_edge_memory": label_for(agg, "W7_reversible_edge_memory"),
        "edge_memory_lock_in": label_for(agg, "W9_edge_memory_lock_in"),
        "noise_rich": label_for(agg, "W10_noise_rich_control"),
        "collapse_attractor": label_for(agg, "W11_collapse_attractor_control"),
    }
    primitive_pass = {str(r["criterion"]): bool(r["passed"]) for _, r in primitive.iterrows()}
    local_rejected = bool(w8["future_distinct_ratio"] > max(val(agg, "W2_no_relation", "future_distinct_ratio"), val(agg, "W3_local_memory_only", "future_distinct_ratio")))
    comm_rejected = bool(w8["future_distinct_ratio"] > val(agg, "W6_commutative_edge_memory", "future_distinct_ratio"))
    random_rejected = bool(w8["future_distinct_ratio"] > val(agg, "W5_random_stepwise_relation_memory", "future_distinct_ratio"))
    lock_rejected = bool(w8["dynamic_lock_in_index"] < val(agg, "W9_edge_memory_lock_in", "dynamic_lock_in_index") and controls["edge_memory_lock_in"] != "primitive_pass_candidate")
    full_pass = bool(
        best["world"] == "W8_full_relational_edge_memory"
        and w8["relation_slack_excess"] > 0
        and w8["noncommutative_asymmetry_delta"] > 0
        and w8["edge_memory_erasure_delta"] > 0
        and local_rejected and comm_rejected and random_rejected and lock_rejected
    )
    if full_pass:
        rec = "DA2 smoke passes; proceed to DA3 scale and phase map."
        next_probe = "DA3_scale_relational_edge_memory_viable_slack"
    elif not local_rejected:
        rec = "Local/no-relation history still competes with W8; pause or redesign DAR edge-memory world."
        next_probe = "DAR_branch_pause_or_edge_memory_revision"
    elif w8["relation_slack_excess"] <= 0:
        rec = "Edge memory is not relation-load-bearing; revise relation dependence before scaling."
        next_probe = "DA2_relation_dependence_revision"
    elif w8["noncommutative_asymmetry_delta"] <= 0:
        rec = "Relation may help, but non-commutative asymmetry is not load-bearing; revise edge order dynamics."
        next_probe = "DA2_asymmetry_revision"
    else:
        rec = "DA2 is mixed; inspect profiles before any main run."
        next_probe = "DA2_targeted_followup"
    return {
        "probe": "DA2_relational_edge_memory_world",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "revision": cfg.revision,
        "worlds": sorted(agg["world"].unique().tolist()),
        "best_world": str(best["world"]),
        "primary_result": {
            "full_relational_edge_memory_passed": full_pass,
            "distinction_required": primitive_pass.get("distinction_required", False),
            "relation_required": primitive_pass.get("relation_required", False),
            "edge_memory_required": primitive_pass.get("edge_memory_required", False),
            "asymmetry_required": primitive_pass.get("asymmetry_required", False),
            "local_history_fakeout_rejected": local_rejected,
            "commutative_fakeout_rejected": comm_rejected,
            "random_relation_fakeout_rejected": random_rejected,
            "lock_in_rejected": lock_rejected,
        },
        "best_profile": {
            "p_viable": float(best["p_viable"]),
            "edge_memory_predictive_gain": float(best["edge_memory_predictive_gain"]),
            "edge_memory_erasure_delta": float(best["edge_memory_erasure_delta"]),
            "edge_memory_shuffle_delta": float(best["edge_memory_shuffle_delta"]),
            "relation_slack_excess": float(best["relation_slack_excess"]),
            "order_sensitivity": float(best["order_sensitivity"]),
            "noncommutative_asymmetry_delta": float(best["noncommutative_asymmetry_delta"]),
            "future_distinct_ratio": float(best["future_distinct_ratio"]),
            "recoverable_alternative_count": float(best["recoverable_alternative_count"]),
            "dynamic_lock_in_index": float(best["dynamic_lock_in_index"]),
            "branching_after_recovery": float(best["branching_after_recovery"]),
        },
        "control_results": controls,
        "recommendation": rec,
        "next_probe": next_probe,
        "estimator_warnings": sorted(agg.loc[agg["p_viable"] <= 0.05, "world"].unique().tolist()),
    }


def val(df: pd.DataFrame, world: str, col: str) -> float:
    s = df.loc[df["world"] == world, col]
    return float(s.mean()) if len(s) else 0.0


def label_for(df: pd.DataFrame, world: str) -> str:
    s = df.loc[df["world"] == world, "classification"]
    return str(s.iloc[0]) if len(s) else "missing"


def make_plots(out: Path, means: pd.DataFrame, primitive: pd.DataFrame) -> None:
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
        ("edge_memory_predictive_gain", "edge_memory_predictive_gain_by_world.png", "edge memory predictive gain"),
        ("relation_slack_excess", "relation_slack_excess_by_world.png", "relation slack excess"),
        ("order_sensitivity", "order_sensitivity_by_world.png", "order sensitivity"),
        ("noncommutative_asymmetry_delta", "noncommutative_asymmetry_delta_by_world.png", "noncommutative asymmetry delta"),
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
    ax.set_xlabel("future distinct ratio")
    ax.set_ylabel("dynamic lock-in index")
    fig.tight_layout()
    fig.savefig(out / "future_distinct_vs_lockin_scatter.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    mat = primitive[["passed"]].astype(int).to_numpy()
    ax.imshow(mat, aspect="auto")
    ax.set_yticks(np.arange(len(primitive)))
    ax.set_yticklabels(primitive["criterion"], fontsize=8)
    ax.set_xticks([0])
    ax.set_xticklabels(["passed"])
    fig.tight_layout()
    fig.savefig(out / "primitive_mutual_necessity_heatmap.png", dpi=160)
    plt.close(fig)
    metrics = ["edge_memory_predictive_gain", "relation_slack_excess", "order_sensitivity", "noncommutative_asymmetry_delta", "future_distinct_ratio", "dynamic_lock_in_index"]
    mat = agg[metrics].to_numpy(float)
    scale = np.maximum(np.nanmax(np.abs(mat), axis=0), 1e-9)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(mat / scale, aspect="auto")
    ax.set_yticks(np.arange(len(agg)))
    ax.set_yticklabels(agg["world"], fontsize=7)
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels(metrics, rotation=60, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "diagnostic_profile_heatmap.png", dpi=160)
    plt.close(fig)
    codes = means.copy()
    order = {"underconstrained": 0, "local_history_fakeout": 1, "generic_coupling_fakeout": 2, "commutative_fakeout": 3, "history_fakeout": 4, "lock_in": 5, "primitive_pass_candidate": 6}
    codes["code"] = codes["classification"].map(order).fillna(2)
    heat = codes.pivot_table(index="world", columns="T", values="code", aggfunc="first")
    fig, ax = plt.subplots(figsize=(5, 7))
    ax.imshow(heat.to_numpy(), aspect="auto")
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
    print("PROBE DA2: RELATIONAL EDGE-MEMORY WORLD")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
