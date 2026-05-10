#!/usr/bin/env python
"""Probe 09: robust fiber reachability.

Primary object: viable propagation through certified fibers.
Entropy/breadth are secondary diagnostics.
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
from typing import Iterable

import numpy as np
import pandas as pd

import probe_08a_multifield_profile_reconciliation as p08a


KAPPAS = [
    "center_of_mass",
    "joint_basin",
    "basin_transition_profile",
    "boundary_v2_regime_sequence",
]

THRESHOLDS = {
    "loose": {"node_mass": 0.0025, "edge_mass": 0.0005},
    "main": {"node_mass": 0.005, "edge_mass": 0.001},
    "strict": {"node_mass": 0.01, "edge_mass": 0.002},
}

BOOT_METRICS = [
    "Delta_depth_vs_shuffled",
    "Delta_depth_vs_product",
    "Delta_viable_propagation_vs_shuffled",
    "Delta_viable_propagation_vs_product",
    "Delta_breadth_vs_product",
    "certified_transport_density_advantage",
    "component_B_preservation",
    "lower_rank_erasure_score",
]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seeds: list[int]
    alphas: list[float]
    horizons: list[int]
    bootstrap_repeats: int
    soft_limit_seconds: float
    hard_limit_seconds: float
    dt: float
    noise: float
    coupling_scale: float


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("probe_09_robust_fiber_reachability_results"))
    parser.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    parser.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "10000")))
    parser.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "160")))
    parser.add_argument("--seed-start", type=int, default=int(os.environ.get("OMEGA_SEED_START", "0")))
    parser.add_argument("--alphas", type=parse_csv_floats, default=parse_csv_floats(os.environ.get("OMEGA_ALPHAS", "0.45,0.50,0.525")))
    parser.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "900,1500,2400")))
    parser.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "800")))
    parser.add_argument("--soft-limit-sec", type=float, default=float(os.environ.get("OMEGA_SOFT_LIMIT_SECONDS", "14400")))
    parser.add_argument("--hard-limit-sec", type=float, default=float(os.environ.get("OMEGA_HARD_LIMIT_SECONDS", "21600")))
    parser.add_argument("--dt", type=float, default=0.018)
    parser.add_argument("--noise", type=float, default=0.055)
    parser.add_argument("--coupling-scale", type=float, default=0.085)
    return parser.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    return Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seeds=list(range(args.seed_start, args.seed_start + args.seed_count)),
        alphas=args.alphas,
        horizons=sorted(args.horizons),
        bootstrap_repeats=args.bootstrap_repeats,
        soft_limit_seconds=args.soft_limit_sec,
        hard_limit_seconds=args.hard_limit_sec,
        dt=args.dt,
        noise=args.noise,
        coupling_scale=args.coupling_scale,
    )


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def combine_codes(parts: Iterable[np.ndarray], base: int = 4099) -> np.ndarray:
    return p08a.combine_codes(parts, base=base)


def simulate_union_boundaries(alpha: float, seed: int, cfg: Config, coupled: bool, shuffle: bool) -> dict[str, object]:
    rng = np.random.default_rng(909_009 + seed * 1009 + int(round(alpha * 10000)) * 31 + (0 if coupled else 73))
    max_h = max(cfg.horizons)
    boundaries = sorted({0, *[int(round(i * h / 6)) for h in cfg.horizons for i in range(1, 7)]})
    n = cfg.n_traj
    a = -1.10 + 0.62 * rng.normal(size=n)
    b = 1.12 + 0.18 * rng.normal(size=n)
    if shuffle:
        b = b[rng.permutation(n)]

    rec_a = np.empty((len(boundaries), n), dtype=np.float32)
    rec_b = np.empty((len(boundaries), n), dtype=np.float32)
    rec_i = 0
    rec_a[rec_i] = a
    rec_b[rec_i] = b
    rec_i += 1

    alive_a = np.abs(a) < 3.0
    alive_b = np.abs(b) < 3.0
    energy_a = np.zeros(n, dtype=np.float64)
    energy_b = np.zeros(n, dtype=np.float64)
    alive_by_h: dict[int, np.ndarray] = {}
    alive_a_by_h: dict[int, np.ndarray] = {}
    alive_b_by_h: dict[int, np.ndarray] = {}
    recovery_by_h: dict[int, np.ndarray] = {}

    for t in range(1, max_h + 1):
        delta = b - a
        if coupled:
            ca = alpha * cfg.coupling_scale * delta
            cb = -alpha * cfg.coupling_scale * delta
        else:
            ca = 0.0
            cb = 0.0
        da = (p08a.drift_f(a) + ca) * cfg.dt + cfg.noise * math.sqrt(cfg.dt) * rng.normal(size=n)
        db = (p08a.drift_t(b) + cb) * cfg.dt + cfg.noise * math.sqrt(cfg.dt) * rng.normal(size=n)
        a = np.clip(a + da, -3.8, 3.8)
        b = np.clip(b + db, -3.8, 3.8)
        energy_a += np.abs(da)
        energy_b += np.abs(db)
        alive_a &= (np.abs(a) < 3.0) & (energy_a < 0.18 * t + 4.0)
        alive_b &= (np.abs(b) < 3.0) & (energy_b < 0.18 * t + 4.0)
        if rec_i < len(boundaries) and t == boundaries[rec_i]:
            rec_a[rec_i] = a
            rec_b[rec_i] = b
            rec_i += 1
        if t in cfg.horizons:
            margin = np.minimum(3.0 - np.abs(a), 3.0 - np.abs(b))
            alive_by_h[t] = (alive_a & alive_b).copy()
            alive_a_by_h[t] = alive_a.copy()
            alive_b_by_h[t] = alive_b.copy()
            recovery_by_h[t] = np.clip((margin + 0.35) / 1.55, 0.0, 1.0).astype(np.float64)

    return {
        "boundaries": np.array(boundaries, dtype=np.int32),
        "rec_a": rec_a,
        "rec_b": rec_b,
        "alive": alive_by_h,
        "alive_a": alive_a_by_h,
        "alive_b": alive_b_by_h,
        "recovery": recovery_by_h,
    }


def node_codes(kappa: str, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if kappa == "center_of_mass":
        return np.rint(((a + b) / 2.0) / 0.24).astype(np.int64)
    if kappa == "joint_basin":
        return (p08a.basin_code(a) * 4 + p08a.basin_code(b)).astype(np.int64)
    if kappa == "basin_transition_profile":
        ba = p08a.basin_code(a)
        bb = p08a.basin_code(b)
        pair = ba * 4 + bb
        out = np.empty_like(pair, dtype=np.int64)
        out[0] = pair[0]
        out[1:] = pair[:-1] * 16 + pair[1:]
        return out
    if kappa == "boundary_v2_regime_sequence":
        com = (a + b) / 2.0
        dist = np.abs(a - b)
        regime = np.zeros(com.shape, dtype=np.int64)
        regime[com > 0.85] = 1
        regime[com < -0.85] = 2
        regime[dist > 2.0] = 3
        regime[(np.abs(a) > 2.35) | (np.abs(b) > 2.35)] = 4
        return regime
    raise KeyError(kappa)


def entropy(keys: np.ndarray) -> float:
    h, _, _ = p08a.entropy_from_keys(keys.astype(np.int64))
    return h


def path_keys(nodes: np.ndarray) -> np.ndarray:
    return combine_codes([nodes])


def component_path_keys(a_path: np.ndarray, b_path: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ka = combine_codes([p08a.basin_code(a_path), np.rint(a_path / 0.36).astype(np.int16)])
    kb = combine_codes([p08a.basin_code(b_path), np.rint(b_path / 0.36).astype(np.int16)])
    return ka, kb


def graph_metrics(
    condition: str,
    alpha: float,
    horizon: int,
    kappa: str,
    seed: int,
    block: dict[str, object],
    threshold_name: str,
    node_mass_min: float,
    edge_mass_min: float,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    boundaries = block["boundaries"]
    idx = np.array([np.where(boundaries == int(round(i * horizon / 6)))[0][0] for i in range(7)])
    a_path = block["rec_a"][idx]
    b_path = block["rec_b"][idx]
    alive = block["alive"][horizon]
    n_total = len(alive)
    n_viable = int(np.sum(alive))
    if n_viable == 0:
        raise RuntimeError("no viable trajectories")

    nodes = node_codes(kappa, a_path, b_path)
    nodes_v = nodes[:, alive]
    pkeys = path_keys(nodes_v)
    singleton_fraction = singleton_from_keys(pkeys)
    ka, kb = component_path_keys(a_path, b_path)
    h_joint = max(entropy(pkeys), 1e-9)
    h_a = entropy(ka[alive])
    h_b = entropy(kb[alive])
    comp_a = min(1.0, h_a / h_joint)
    comp_b = min(1.0, h_b / h_joint)
    erasure = 1.0 - 0.5 * (comp_a + comp_b)
    component_factor = min(comp_a, comp_b)
    nonfrag = max(0.0, 1.0 - singleton_fraction)

    node_rows: list[dict[str, object]] = []
    certified_nodes: list[set[int]] = []
    node_masses: list[np.ndarray] = []
    for layer in range(nodes_v.shape[0]):
        uniq, counts = np.unique(nodes_v[layer], return_counts=True)
        masses = counts / n_viable
        cert = set(int(u) for u, m in zip(uniq, masses) if m >= node_mass_min)
        certified_nodes.append(cert)
        node_masses.append(masses)
        for u, c, m in zip(uniq, counts, masses):
            node_rows.append({
                "condition": condition, "alpha": alpha, "T": horizon, "kappa": kappa, "seed": seed,
                "threshold": threshold_name, "segment": layer, "node": int(u), "fiber_count": int(c),
                "fiber_mass": float(m), "certified": bool(int(u) in cert),
            })

    edge_rows: list[dict[str, object]] = []
    certified_edge_masks = np.zeros((6, n_viable), dtype=bool)
    cert_edge_count = 0
    all_edge_count = 0
    survival_by_segment = []
    for seg in range(6):
        edge = nodes_v[seg].astype(np.int64) * 100_003 + nodes_v[seg + 1].astype(np.int64)
        uniq, counts = np.unique(edge, return_counts=True)
        all_edge_count += len(uniq)
        cert_edges: set[int] = set()
        for e, c in zip(uniq, counts):
            src = int(e // 100_003)
            dst = int(e % 100_003)
            mass = c / n_viable
            is_cert = mass >= edge_mass_min and src in certified_nodes[seg] and dst in certified_nodes[seg + 1]
            if is_cert:
                cert_edges.add(int(e))
                cert_edge_count += 1
            edge_rows.append({
                "condition": condition, "alpha": alpha, "T": horizon, "kappa": kappa, "seed": seed,
                "threshold": threshold_name, "segment": seg, "source": src, "target": dst,
                "transport_count": int(c), "transport_mass": float(mass), "certified": bool(is_cert),
            })
        certified_edge_masks[seg] = np.isin(edge, list(cert_edges)) if cert_edges else False
        survival_by_segment.append(float(np.mean(certified_edge_masks[seg])))

    prefix = np.ones(n_viable, dtype=bool)
    prefix_survival = []
    lengths = np.zeros(n_viable, dtype=np.int16)
    active = np.ones(n_viable, dtype=bool)
    for seg in range(6):
        prefix &= certified_edge_masks[seg]
        prefix_survival.append(float(np.mean(prefix)))
        active &= certified_edge_masks[seg]
        lengths += active.astype(np.int16)

    final_survival = prefix_survival[-1]
    depth_weighted = float(np.sum([(i + 1) / 6 * s for i, s in enumerate(prefix_survival)]) / np.sum([(i + 1) / 6 for i in range(6)]))
    node_flat = nodes_v.reshape(-1)
    macro_node_entropy = entropy(node_flat)
    macro_path_entropy = entropy(pkeys)
    breadth_index = macro_path_entropy / math.log2(max(n_viable, 2))
    viable_prop = final_survival * float(np.mean(survival_by_segment)) * component_factor * nonfrag
    metric_row = {
        "condition": condition, "alpha": alpha, "T": horizon, "kappa": kappa, "seed": seed,
        "threshold": threshold_name,
        "p_viable": float(n_viable / n_total),
        "macro_node_count": int(len(np.unique(node_flat))),
        "macro_edge_count": int(all_edge_count),
        "reachable_node_count": int(sum(len(set(nodes_v[layer])) for layer in range(7))),
        "certified_reachable_node_count": int(sum(len(c) for c in certified_nodes)),
        "macro_path_entropy": macro_path_entropy,
        "macro_node_entropy": macro_node_entropy,
        "breadth_index": breadth_index,
        "mean_fiber_mass": float(np.mean(np.concatenate(node_masses))),
        "median_fiber_mass": float(np.median(np.concatenate(node_masses))),
        "fiber_mass_entropy": entropy(node_flat),
        "singleton_fraction": singleton_fraction,
        "certified_node_fraction": float(sum(len(c) for c in certified_nodes) / max(sum(len(set(nodes_v[layer])) for layer in range(7)), 1)),
        "viable_fiber_fraction": 1.0,
        "transport_survival_mean": float(np.mean(survival_by_segment)),
        "transport_survival_median": float(np.median(survival_by_segment)),
        "certified_edge_fraction": float(cert_edge_count / max(all_edge_count, 1)),
        "certified_transport_density": float(cert_edge_count / max(all_edge_count, 1)),
        "max_certified_path_length": int(np.max(lengths)),
        "mean_certified_path_length": float(np.mean(lengths)),
        "certified_path_mass_survival_to_final_segment": final_survival,
        "multi_step_transport_depth": depth_weighted,
        "depth_index": final_survival,
        "collapse_segment_index": int(next((i + 1 for i, s in enumerate(prefix_survival) if s <= 0), 0)),
        "robust_reachability_index": breadth_index * final_survival,
        "viable_propagation_index": viable_prop,
        "component_A_preservation": comp_a,
        "component_B_preservation": comp_b,
        "component_A_entropy": h_a,
        "component_B_entropy": h_b,
        "lower_rank_erasure_score": erasure,
    }
    depth_rows = [
        {
            "condition": condition, "alpha": alpha, "T": horizon, "kappa": kappa, "seed": seed,
            "threshold": threshold_name, "segment_depth": i + 1, "certified_path_mass_survival": s,
            "component_A_preservation": comp_a, "component_B_preservation": comp_b,
        }
        for i, s in enumerate(prefix_survival)
    ]
    return metric_row, node_rows, edge_rows, depth_rows


def singleton_from_keys(keys: np.ndarray) -> float:
    _, counts = np.unique(keys, return_counts=True)
    return float(np.mean(counts == 1)) if counts.size else 1.0


def run_seed_task(task: tuple[float, int, Config]) -> dict[str, list[dict[str, object]]]:
    alpha, seed, cfg = task
    blocks = {
        "coupled": simulate_union_boundaries(alpha, seed, cfg, coupled=True, shuffle=False),
        "product": simulate_union_boundaries(0.0, seed + 20_000, cfg, coupled=False, shuffle=False),
        "shuffled": simulate_union_boundaries(0.0, seed + 40_000, cfg, coupled=False, shuffle=True),
        "independent_alpha0": simulate_union_boundaries(0.0, seed + 60_000, cfg, coupled=False, shuffle=False),
    }
    metric_rows: list[dict[str, object]] = []
    node_rows: list[dict[str, object]] = []
    edge_rows: list[dict[str, object]] = []
    depth_rows: list[dict[str, object]] = []
    for horizon in cfg.horizons:
        for kappa in KAPPAS:
            for condition, block in blocks.items():
                for threshold_name, th in THRESHOLDS.items():
                    m, n, e, d = graph_metrics(condition, alpha, horizon, kappa, seed, block, threshold_name, th["node_mass"], th["edge_mass"])
                    metric_rows.append(m)
                    if threshold_name == "main":
                        node_rows.extend(n)
                        edge_rows.extend(e)
                        depth_rows.extend(d)
    return {"metrics": metric_rows, "nodes": node_rows, "edges": edge_rows, "depth": depth_rows}


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(909_800)
    rows: list[dict[str, object]] = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(dtype=float)
            mean = float(np.mean(vals))
            std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, size=len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            rows.append({
                **base, "metric": metric, "mean": mean, "std": std,
                "se": std / math.sqrt(max(len(vals), 1)), "ci_low": float(lo), "ci_high": float(hi),
                "ci_excludes_zero": bool(lo > 0 or hi < 0), "n_seeds": int(len(seeds)),
            })
    return pd.DataFrame(rows)


def category(row: pd.Series) -> str:
    comp_ok = row["component_A_preservation"] >= 0.70 and row["component_B_preservation"] >= 0.70 and row["lower_rank_erasure_score"] <= 0.20
    if row["singleton_fraction"] > 0.65:
        return "Overfragmented/inconclusive"
    if row["Delta_depth_vs_shuffled"] > 0 and not comp_ok:
        return "Component-erasing transport"
    if row["Delta_viable_propagation_vs_product"] > 0 and row["Delta_viable_propagation_vs_shuffled"] > 0 and comp_ok:
        if row["Delta_breadth_vs_product"] < 0 and row["Delta_depth_vs_product"] > 0:
            return "Narrower-but-deeper / propagation-compressive"
        return "Viable propagation positive"
    if row["certified_transport_density_advantage"] > 0 and row["Delta_depth_vs_shuffled"] <= 0:
        return "Local transport artifact"
    if (row["Delta_breadth_vs_product"] > 0 or row["Delta_R"] > 0) and (row["Delta_depth_vs_shuffled"] <= 0 or row["certified_transport_density_advantage"] <= 0):
        return "Entropy-only pseudo-risk"
    if all(abs(float(row[c])) < 0.03 for c in ["Delta_depth_vs_shuffled", "Delta_viable_propagation_vs_shuffled", "certified_transport_density_advantage"]):
        return "Null-like"
    return "Overfragmented/inconclusive"


def build_outputs(cfg: Config, started: float, status: str) -> dict[str, object]:
    out = cfg.out_dir
    metrics = pd.read_csv(out / "_reachability_seed_metrics.csv")
    main = metrics[metrics["threshold"] == "main"].copy()
    means = main.groupby(["condition", "alpha", "T", "kappa"], as_index=False).mean(numeric_only=True)
    wide = means.pivot(index=["alpha", "T", "kappa"], columns="condition")

    rows: list[dict[str, object]] = []
    for key in sorted(main.groupby(["alpha", "T", "kappa"]).groups):
        alpha, T, kappa = key
        subset = means[(means["alpha"] == alpha) & (means["T"] == T) & (means["kappa"] == kappa)]
        c = subset[subset["condition"] == "coupled"].iloc[0]
        product = subset[subset["condition"] == "product"].iloc[0]
        shuffled = subset[subset["condition"] == "shuffled"].iloc[0]
        row = c.to_dict()
        row.update({
            "baseline": "coupled_vs_product_shuffled",
            "Delta_breadth_vs_product": c["breadth_index"] - product["breadth_index"],
            "Delta_depth_vs_product": c["depth_index"] - product["depth_index"],
            "Delta_robust_reachability_vs_product": c["robust_reachability_index"] - product["robust_reachability_index"],
            "Delta_viable_propagation_vs_product": c["viable_propagation_index"] - product["viable_propagation_index"],
            "Delta_breadth_vs_shuffled": c["breadth_index"] - shuffled["breadth_index"],
            "Delta_depth_vs_shuffled": c["depth_index"] - shuffled["depth_index"],
            "Delta_robust_reachability_vs_shuffled": c["robust_reachability_index"] - shuffled["robust_reachability_index"],
            "Delta_viable_propagation_vs_shuffled": c["viable_propagation_index"] - shuffled["viable_propagation_index"],
            "certified_transport_density_advantage": c["certified_transport_density"] - shuffled["certified_transport_density"],
            "strict_certified_mass_advantage": c["certified_node_fraction"] - shuffled["certified_node_fraction"],
            "Delta_R": c["macro_path_entropy"] - shuffled["macro_path_entropy"],
            "Delta_H_weighted_product": c["p_viable"] * c["macro_path_entropy"] - product["p_viable"] * product["macro_path_entropy"],
        })
        row["category"] = category(pd.Series(row))
        rows.append(row)
    comparisons = pd.DataFrame(rows)
    comparisons.to_csv(out / "baseline_comparisons.csv", index=False)
    comparisons.to_csv(out / "old_new_reconciliation.csv", index=False)

    threshold = metrics.groupby(["threshold", "condition", "alpha", "T", "kappa"], as_index=False).mean(numeric_only=True)
    threshold.to_csv(out / "threshold_sensitivity.csv", index=False)

    boot_seed = []
    for (alpha, T, kappa, seed), group in main.groupby(["alpha", "T", "kappa", "seed"]):
        c = group[group["condition"] == "coupled"].iloc[0]
        product = group[group["condition"] == "product"].iloc[0]
        shuffled = group[group["condition"] == "shuffled"].iloc[0]
        boot_seed.append({
            "alpha": alpha, "T": T, "kappa": kappa, "seed": seed,
            "Delta_depth_vs_shuffled": c["depth_index"] - shuffled["depth_index"],
            "Delta_depth_vs_product": c["depth_index"] - product["depth_index"],
            "Delta_viable_propagation_vs_shuffled": c["viable_propagation_index"] - shuffled["viable_propagation_index"],
            "Delta_viable_propagation_vs_product": c["viable_propagation_index"] - product["viable_propagation_index"],
            "Delta_breadth_vs_product": c["breadth_index"] - product["breadth_index"],
            "certified_transport_density_advantage": c["certified_transport_density"] - shuffled["certified_transport_density"],
            "component_B_preservation": c["component_B_preservation"],
            "lower_rank_erasure_score": c["lower_rank_erasure_score"],
        })
    boot_df = pd.DataFrame(boot_seed)
    intervals = bootstrap(boot_df, ["alpha", "T", "kappa"], BOOT_METRICS, cfg.bootstrap_repeats)
    intervals.to_csv(out / "bootstrap_intervals.csv", index=False)

    vi = comparisons.copy()
    ci_vi = intervals[intervals["metric"] == "Delta_viable_propagation_vs_shuffled"][["alpha", "T", "kappa", "ci_low", "ci_high"]]
    vi = vi.merge(ci_vi, on=["alpha", "T", "kappa"], how="left")
    vi_cols = [
        "alpha", "T", "kappa", "baseline", "certified_path_mass_survival_to_final_segment",
        "transport_survival_mean", "multi_step_transport_depth", "component_A_preservation",
        "component_B_preservation", "singleton_fraction", "viable_propagation_index",
        "Delta_viable_propagation_vs_product", "Delta_viable_propagation_vs_shuffled",
        "ci_low", "ci_high", "category",
    ]
    vi[vi_cols].to_csv(out / "viable_propagation_summary.csv", index=False)

    means.to_csv(out / "robust_reachability_by_condition.csv", index=False)
    comparisons[[
        "alpha", "T", "kappa", "breadth_index", "depth_index", "robust_reachability_index",
        "viable_propagation_index", "Delta_breadth_vs_product", "Delta_depth_vs_product",
        "Delta_viable_propagation_vs_product", "category",
    ]].to_csv(out / "breadth_depth_decomposition.csv", index=False)
    pd.read_csv(out / "_depth_seed_rows.csv").groupby(
        ["condition", "alpha", "T", "kappa", "segment_depth"], as_index=False
    ).mean(numeric_only=True).to_csv(out / "component_preservation_by_depth.csv", index=False)
    pd.read_csv(out / "_graph_nodes.csv").to_csv(out / "fiber_reachability_graph_nodes.csv", index=False)
    pd.read_csv(out / "_graph_edges.csv").to_csv(out / "fiber_reachability_graph_edges.csv", index=False)

    est = main.groupby(["condition", "alpha", "T", "kappa"], as_index=False).agg(
        singleton_fraction=("singleton_fraction", "mean"),
        macro_node_count=("macro_node_count", "mean"),
        macro_edge_count=("macro_edge_count", "mean"),
        p_viable=("p_viable", "mean"),
    )
    est["estimator_warning"] = np.where(est["singleton_fraction"] > 0.65, "HIGH_SINGLETON_FRACTION", "")
    est.to_csv(out / "estimator_report.csv", index=False)

    plot_outputs(out, comparisons, intervals, threshold)

    summary = {
        "probe": "09_robust_fiber_reachability",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "workers": cfg.workers,
        "n_traj": cfg.n_traj,
        "seed_count_requested": len(cfg.seeds),
        "seed_count_completed": int(main["seed"].nunique()),
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "completed_rows": int(len(comparisons)),
        "threshold_variants_completed": sorted(metrics["threshold"].unique().tolist()),
        "category_counts": comparisons["category"].value_counts().to_dict(),
        "primary_question": {
            "viable_propagation_positive_rows": int((comparisons["Delta_viable_propagation_vs_shuffled"] > 0).sum()),
            "multi_step_depth_positive_rows": int((comparisons["Delta_depth_vs_shuffled"] > 0).sum()),
            "component_preservation_ok_rows": int(((comparisons["component_A_preservation"] >= 0.70) & (comparisons["component_B_preservation"] >= 0.70)).sum()),
        },
        "center_of_mass": comparisons[comparisons["kappa"] == "center_of_mass"].to_dict(orient="records"),
        "files": sorted(p.name for p in out.glob("*") if not p.name.startswith("_")),
        "method_note": "Standalone toy multifield simulator inherited from Probe 08/09 local workflow.",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def plot_outputs(out: Path, comp: pd.DataFrame, intervals: pd.DataFrame, threshold: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    for k, g in comp.groupby("kappa"):
        ax.scatter(g["breadth_index"], g["depth_index"], label=k)
    ax.set_xlabel("breadth_index")
    ax.set_ylabel("depth_index")
    ax.set_title("Breadth vs depth by kappa")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "breadth_vs_depth_by_kappa.png", dpi=160)
    plt.close(fig)

    d = intervals[intervals["metric"] == "Delta_depth_vs_shuffled"]
    fig, ax = plt.subplots(figsize=(8, 5))
    for k, g in d.groupby("kappa"):
        g = g.sort_values(["T", "alpha"])
        ax.plot(range(len(g)), g["mean"], marker="o", label=k)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("Depth advantage with CI proxy")
    ax.set_ylabel("Delta depth vs shuffled")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "depth_advantage_with_ci.png", dpi=160)
    plt.close(fig)

    for kappa, filename in [
        ("center_of_mass", "center_of_mass_depth_by_alpha_T.png"),
        ("joint_basin", "joint_basin_depth_by_alpha_T.png"),
        ("basin_transition_profile", "basin_transition_depth_by_alpha_T.png"),
        ("boundary_v2_regime_sequence", "boundary_v2_pseudorisk_control.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 5))
        sub = comp[comp["kappa"] == kappa]
        for T, g in sub.groupby("T"):
            ax.plot(g["alpha"], g["Delta_viable_propagation_vs_shuffled"], marker="o", label=f"T={T}")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_title(kappa)
        ax.set_xlabel("alpha")
        ax.set_ylabel("Delta viable propagation vs shuffled")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out / filename, dpi=160)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for k, g in comp.groupby("kappa"):
        ax.scatter(g["Delta_viable_propagation_vs_product"], g["viable_propagation_index"], label=k)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Robust reachability vs product")
    ax.set_xlabel("Delta viable propagation vs product")
    ax.set_ylabel("viable propagation index")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "robust_reachability_vs_product.png", dpi=160)
    plt.close(fig)

    depth = pd.read_csv(out / "component_preservation_by_depth.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    for k, g in depth[depth["condition"] == "coupled"].groupby("kappa"):
        ax.plot(g["segment_depth"], g["component_B_preservation"], marker="o", label=k)
    ax.axhline(0.70, color="k", lw=0.8)
    ax.set_title("Component preservation by depth")
    ax.set_xlabel("segment depth")
    ax.set_ylabel("component B preservation")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "component_preservation_by_depth.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    coupled = threshold[threshold["condition"] == "coupled"]
    for th, g in coupled.groupby("threshold"):
        ax.scatter(g["certified_path_mass_survival_to_final_segment"], g["viable_propagation_index"], label=th)
    ax.set_title("Threshold sensitivity depth")
    ax.set_xlabel("final certified path survival")
    ax.set_ylabel("viable propagation index")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "threshold_sensitivity_depth.png", dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    status = "COMPLETE"

    for name in ["_reachability_seed_metrics.csv", "_graph_nodes.csv", "_graph_edges.csv", "_depth_seed_rows.csv"]:
        path = cfg.out_dir / name
        if path.exists():
            path.unlink()

    tasks = [(alpha, seed, cfg) for alpha in cfg.alphas for seed in cfg.seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = []
        for task in tasks:
            if time.monotonic() - started > cfg.soft_limit_seconds:
                status = "PARTIAL_EXIT_SOFT_LIMIT"
                break
            futures.append(pool.submit(run_seed_task, task))
        completed = 0
        for fut in as_completed(futures):
            if time.monotonic() - started > cfg.hard_limit_seconds:
                status = "PARTIAL_EXIT_HARD_LIMIT"
            result = fut.result()
            append_rows(cfg.out_dir / "_reachability_seed_metrics.csv", result["metrics"])
            append_rows(cfg.out_dir / "_graph_nodes.csv", result["nodes"])
            append_rows(cfg.out_dir / "_graph_edges.csv", result["edges"])
            append_rows(cfg.out_dir / "_depth_seed_rows.csv", result["depth"])
            completed += 1
            if completed % max(1, cfg.workers) == 0:
                print(json.dumps({"completed_seed_blocks": completed, "total_launched": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
            if status == "PARTIAL_EXIT_HARD_LIMIT":
                break

    summary = build_outputs(cfg, started, status)
    print("PROBE 09: ROBUST FIBER REACHABILITY")
    print(json.dumps(summary, indent=2))
    print("Primary Omega-relevant readout:")
    print("- Did viable propagation improve vs product/shuffled?")
    print("- Was improvement multi-step or only local?")
    print("- Did it preserve both components?")
    print("- Was it non-overfragmented?")
    print("- What did entropy do as a secondary readout?")


if __name__ == "__main__":
    main()
