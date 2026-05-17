#!/usr/bin/env python
"""Probe 10: COM viable propagation robustness.

Tests whether the Probe 09 center_of_mass viable propagation channel survives
small substrate perturbations. This is still the local toy substrate, not a
claim about the full theory.
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

import probe_08a_multifield_profile_reconciliation as p08a


KAPPAS = ["center_of_mass", "joint_basin", "boundary_v2_regime_sequence"]
THRESHOLDS = {
    "loose": {"node_mass": 0.0025, "edge_mass": 0.0005},
    "main": {"node_mass": 0.005, "edge_mass": 0.001},
    "strict": {"node_mass": 0.01, "edge_mass": 0.002},
}
BOOT_METRICS = [
    "Delta_viable_propagation_vs_shuffled",
    "Delta_viable_propagation_vs_product",
    "Delta_depth_vs_shuffled",
    "Delta_depth_vs_product",
    "Delta_robust_reachability_vs_shuffled",
    "Delta_robust_reachability_vs_product",
    "component_B_preservation",
    "lower_rank_erasure_score",
    "singleton_fraction",
]


@dataclass(frozen=True)
class Perturbation:
    variant_id: str
    family: str
    strength_label: str
    strength: float
    noise_multiplier: float = 1.0
    sink_shift: float = 0.0
    initial_shift_a: float = 0.0
    initial_shift_b: float = 0.0
    dt_multiplier: float = 1.0
    drift_scale_f: float = 1.0
    drift_scale_t: float = 1.0
    center_shift_f: float = 0.0
    center_shift_t: float = 0.0


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seeds: list[int]
    alphas: list[float]
    horizons: list[int]
    bootstrap_repeats: int
    perturbations_per_family: int
    soft_limit_seconds: float
    hard_limit_seconds: float
    dt: float
    noise: float
    coupling_scale: float


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_strings(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("probe_10_com_viable_propagation_robustness_results"))
    parser.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    parser.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "7500")))
    parser.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "80")))
    parser.add_argument("--seed-start", type=int, default=int(os.environ.get("OMEGA_SEED_START", "0")))
    parser.add_argument("--alphas", type=parse_csv_floats, default=parse_csv_floats(os.environ.get("OMEGA_ALPHAS", "0.45,0.50,0.525")))
    parser.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "900,1500,2400")))
    parser.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "500")))
    parser.add_argument("--perturbations-per-family", type=int, default=int(os.environ.get("OMEGA_PERTURBATIONS_PER_FAMILY", "2")))
    parser.add_argument("--kappas", type=parse_csv_strings, default=parse_csv_strings(os.environ.get("OMEGA_KAPPAS", ",".join(KAPPAS))))
    parser.add_argument("--families", type=parse_csv_strings, default=parse_csv_strings(os.environ.get("OMEGA_FAMILIES", "")))
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
        perturbations_per_family=args.perturbations_per_family,
        soft_limit_seconds=args.soft_limit_sec,
        hard_limit_seconds=args.hard_limit_sec,
        dt=args.dt,
        noise=args.noise,
        coupling_scale=args.coupling_scale,
    )


def make_perturbations(count_per_family: int) -> list[Perturbation]:
    rng = np.random.default_rng(10_010)
    out = [Perturbation("reference_000", "reference", "reference", 0.0)]
    families = [
        "potential_shape",
        "noise",
        "sink_threshold",
        "initial_location",
        "time_discretization",
    ]
    for family in families:
        for i in range(count_per_family):
            strength_label = "mild" if i % 2 == 0 else "moderate"
            strength = 0.05 if strength_label == "mild" else 0.10
            if family == "potential_shape":
                out.append(Perturbation(
                    f"{family}_{i:03d}", family, strength_label, strength,
                    drift_scale_f=1.0 + rng.choice([-1, 1]) * strength,
                    drift_scale_t=1.0 + rng.choice([-1, 1]) * strength,
                    center_shift_f=rng.uniform(-0.03, 0.03) * (strength / 0.05),
                    center_shift_t=rng.uniform(-0.03, 0.03) * (strength / 0.05),
                ))
            elif family == "noise":
                mult = rng.choice([0.85, 1.15]) if strength_label == "mild" else rng.choice([0.70, 1.30])
                out.append(Perturbation(f"{family}_{i:03d}", family, strength_label, strength, noise_multiplier=float(mult)))
            elif family == "sink_threshold":
                shift = rng.choice([-1, 1]) * (0.05 if strength_label == "mild" else 0.10)
                out.append(Perturbation(f"{family}_{i:03d}", family, strength_label, strength, sink_shift=float(shift)))
            elif family == "initial_location":
                amp = 0.03 if strength_label == "mild" else 0.07
                out.append(Perturbation(f"{family}_{i:03d}", family, strength_label, strength, initial_shift_a=float(rng.uniform(-amp, amp)), initial_shift_b=float(rng.uniform(-amp, amp))))
            elif family == "time_discretization":
                mult = rng.choice([0.8, 1.2])
                out.append(Perturbation(f"{family}_{i:03d}", family, strength_label, strength, dt_multiplier=float(mult)))
    out.extend([
        Perturbation("threshold_loose_reference", "certification_threshold", "loose", 0.0),
        Perturbation("threshold_strict_reference", "certification_threshold", "strict", 0.0),
    ])
    return out


def drift_f_perturbed(x: np.ndarray, p: Perturbation) -> np.ndarray:
    return p.drift_scale_f * p08a.drift_f(x - p.center_shift_f)


def drift_t_perturbed(x: np.ndarray, p: Perturbation) -> np.ndarray:
    return p.drift_scale_t * p08a.drift_t(x - p.center_shift_t)


def simulate(alpha: float, seed: int, cfg: Config, perturb: Perturbation, coupled: bool, shuffle: bool) -> dict[str, object]:
    rng = np.random.default_rng(10_100 + seed * 1009 + int(round(alpha * 10000)) * 31 + abs(hash(perturb.variant_id)) % 100_000 + (0 if coupled else 77))
    max_h = max(cfg.horizons)
    boundaries = sorted({0, *[int(round(i * h / 6)) for h in cfg.horizons for i in range(1, 7)]})
    n = cfg.n_traj
    a = -1.10 + perturb.initial_shift_a + 0.62 * rng.normal(size=n)
    b = 1.12 + perturb.initial_shift_b + 0.18 * rng.normal(size=n)
    if shuffle:
        b = b[rng.permutation(n)]
    rec_a = np.empty((len(boundaries), n), dtype=np.float32)
    rec_b = np.empty((len(boundaries), n), dtype=np.float32)
    rec_i = 0
    rec_a[rec_i] = a
    rec_b[rec_i] = b
    rec_i += 1
    sink = 3.0 + perturb.sink_shift
    alive_a = np.abs(a) < sink
    alive_b = np.abs(b) < sink
    energy_a = np.zeros(n)
    energy_b = np.zeros(n)
    alive_by_h: dict[int, np.ndarray] = {}

    dt = cfg.dt * perturb.dt_multiplier
    noise = cfg.noise * perturb.noise_multiplier
    for t in range(1, max_h + 1):
        delta = b - a
        if coupled:
            ca = alpha * cfg.coupling_scale * delta
            cb = -alpha * cfg.coupling_scale * delta
        else:
            ca = cb = 0.0
        da = (drift_f_perturbed(a, perturb) + ca) * dt + noise * math.sqrt(dt) * rng.normal(size=n)
        db = (drift_t_perturbed(b, perturb) + cb) * dt + noise * math.sqrt(dt) * rng.normal(size=n)
        a = np.clip(a + da, -3.8, 3.8)
        b = np.clip(b + db, -3.8, 3.8)
        energy_a += np.abs(da)
        energy_b += np.abs(db)
        alive_a &= (np.abs(a) < sink) & (energy_a < 0.18 * t * perturb.dt_multiplier + 4.0)
        alive_b &= (np.abs(b) < sink) & (energy_b < 0.18 * t * perturb.dt_multiplier + 4.0)
        if rec_i < len(boundaries) and t == boundaries[rec_i]:
            rec_a[rec_i] = a
            rec_b[rec_i] = b
            rec_i += 1
        if t in cfg.horizons:
            alive_by_h[t] = (alive_a & alive_b).copy()
    return {"boundaries": np.array(boundaries), "rec_a": rec_a, "rec_b": rec_b, "alive": alive_by_h}


def combine_codes(parts):
    return p08a.combine_codes(parts)


def node_codes(kappa: str, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if kappa == "center_of_mass":
        return np.rint(((a + b) / 2.0) / 0.24).astype(np.int64)
    if kappa == "joint_basin":
        return (p08a.basin_code(a) * 4 + p08a.basin_code(b)).astype(np.int64)
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


def graph_metrics(condition: str, alpha: float, horizon: int, kappa: str, seed: int, perturb: Perturbation, block: dict[str, object], threshold: str) -> dict[str, object]:
    th = THRESHOLDS[threshold]
    boundaries = block["boundaries"]
    idx = np.array([np.where(boundaries == int(round(i * horizon / 6)))[0][0] for i in range(7)])
    a_path = block["rec_a"][idx]
    b_path = block["rec_b"][idx]
    alive = block["alive"][horizon]
    n_viable = int(np.sum(alive))
    if n_viable == 0:
        n_viable = 1
        alive = np.ones_like(alive, dtype=bool)
    nodes = node_codes(kappa, a_path, b_path)[:, alive]
    path_key = combine_codes([nodes])
    _, path_counts = np.unique(path_key, return_counts=True)
    singleton_fraction = float(np.mean(path_counts == 1)) if path_counts.size else 1.0
    h_path = entropy(path_key)
    breadth_index = h_path / math.log2(max(n_viable, 2))
    ka = combine_codes([p08a.basin_code(a_path), np.rint(a_path / 0.36).astype(np.int16)])[alive]
    kb = combine_codes([p08a.basin_code(b_path), np.rint(b_path / 0.36).astype(np.int16)])[alive]
    comp_a = min(1.0, entropy(ka) / max(h_path, 1e-9))
    comp_b = min(1.0, entropy(kb) / max(h_path, 1e-9))
    erasure = 1.0 - 0.5 * (comp_a + comp_b)
    certified_nodes: list[set[int]] = []
    for layer in range(7):
        uniq, counts = np.unique(nodes[layer], return_counts=True)
        certified_nodes.append({int(u) for u, c in zip(uniq, counts) if c / n_viable >= th["node_mass"]})
    certified_edge_masks = np.zeros((6, n_viable), dtype=bool)
    cert_edge_count = 0
    all_edge_count = 0
    for seg in range(6):
        edge = nodes[seg] * 100_003 + nodes[seg + 1]
        uniq, counts = np.unique(edge, return_counts=True)
        all_edge_count += len(uniq)
        cert_edges = set()
        for e, c in zip(uniq, counts):
            src = int(e // 100_003)
            dst = int(e % 100_003)
            if c / n_viable >= th["edge_mass"] and src in certified_nodes[seg] and dst in certified_nodes[seg + 1]:
                cert_edges.add(int(e))
                cert_edge_count += 1
        certified_edge_masks[seg] = np.isin(edge, list(cert_edges)) if cert_edges else False
    prefix = np.ones(n_viable, dtype=bool)
    prefix_survival = []
    for seg in range(6):
        prefix &= certified_edge_masks[seg]
        prefix_survival.append(float(np.mean(prefix)))
    transport_survival_mean = float(np.mean([np.mean(certified_edge_masks[i]) for i in range(6)]))
    final_survival = prefix_survival[-1]
    depth = float(np.sum([(i + 1) / 6 * s for i, s in enumerate(prefix_survival)]) / np.sum([(i + 1) / 6 for i in range(6)]))
    viable_prop = final_survival * transport_survival_mean * min(comp_a, comp_b) * max(0.0, 1.0 - singleton_fraction)
    return {
        "variant_id": perturb.variant_id,
        "perturbation_family": perturb.family,
        "perturbation_strength": perturb.strength_label,
        "condition": condition,
        "alpha": alpha,
        "T": horizon,
        "kappa": kappa,
        "seed": seed,
        "threshold": threshold,
        "p_viable": float(np.mean(alive)),
        "certified_path_mass_survival_to_final_segment": final_survival,
        "multi_step_transport_depth": depth,
        "transport_survival_mean": transport_survival_mean,
        "certified_transport_density": float(cert_edge_count / max(all_edge_count, 1)),
        "viable_propagation_index": viable_prop,
        "component_A_preservation": comp_a,
        "component_B_preservation": comp_b,
        "lower_rank_erasure_score": erasure,
        "singleton_fraction": singleton_fraction,
        "certified_node_fraction": float(sum(len(x) for x in certified_nodes) / max(sum(len(set(nodes[i])) for i in range(7)), 1)),
        "viable_fiber_fraction": 1.0,
        "macro_path_entropy": h_path,
        "macro_node_entropy": entropy(nodes.reshape(-1)),
        "breadth_index": breadth_index,
    }


def run_seed_task(task: tuple[Perturbation, float, int, Config, tuple[str, ...]]) -> list[dict[str, object]]:
    perturb, alpha, seed, cfg, kappas = task
    blocks = {
        "coupled": simulate(alpha, seed, cfg, perturb, True, False),
        "product": simulate(0.0, seed + 20_000, cfg, perturb, False, False),
        "shuffled": simulate(0.0, seed + 40_000, cfg, perturb, False, True),
        "independent_alpha0": simulate(0.0, seed + 60_000, cfg, perturb, False, False),
    }
    rows = []
    thresholds = ["main"]
    if perturb.family == "reference" or perturb.family == "certification_threshold":
        thresholds = ["loose", "main", "strict"]
    for horizon in cfg.horizons:
        for kappa in kappas:
            for threshold in thresholds:
                if perturb.variant_id == "threshold_loose_reference" and threshold != "loose":
                    continue
                if perturb.variant_id == "threshold_strict_reference" and threshold != "strict":
                    continue
                for condition, block in blocks.items():
                    rows.append(graph_metrics(condition, alpha, horizon, kappa, seed, perturb, block, threshold))
    return rows


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(10_800)
    out = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            mean = float(np.mean(vals))
            std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            out.append({**base, "metric": metric, "mean": mean, "std": std, "se": std / math.sqrt(max(len(vals), 1)), "ci_low": float(lo), "ci_high": float(hi), "ci_width": float(hi - lo), "ci_excludes_zero": bool(lo > 0 or hi < 0)})
    return pd.DataFrame(out)


def categorize(row: pd.Series, ref_strength: float) -> str:
    stable = bool(row["estimator_stable"])
    positive = row["Delta_viable_propagation_vs_shuffled"] > 0 and row["Delta_viable_propagation_vs_product"] > 0
    comp_ok = row["component_B_preservation"] >= 0.70 and row["lower_rank_erasure_score"] <= 0.20
    if row["singleton_fraction"] > 0.65:
        return "Overfragmented"
    if positive and not comp_ok:
        return "Component-erasing"
    if not stable:
        return "Estimator-limited"
    if positive and comp_ok:
        if ref_strength > 0 and row["Delta_viable_propagation_vs_shuffled"] < 0.5 * ref_strength:
            return "Propagation weakened but positive"
        return "Robust propagation retained"
    if row["Delta_R"] > 0 or row["Delta_breadth_vs_shuffled"] > 0:
        return "Entropy-only pseudo-risk"
    return "Propagation lost"


def build_outputs(cfg: Config, perturbations: list[Perturbation], started: float, status: str) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_metrics.csv")
    main = raw[raw["threshold"] == "main"].copy()
    means = main.groupby(["variant_id", "perturbation_family", "perturbation_strength", "condition", "alpha", "T", "kappa"], as_index=False).mean(numeric_only=True)
    rows = []
    for key, group in means.groupby(["variant_id", "perturbation_family", "perturbation_strength", "alpha", "T", "kappa"]):
        variant_id, family, strength, alpha, T, kappa = key
        c = group[group["condition"] == "coupled"].iloc[0]
        product = group[group["condition"] == "product"].iloc[0]
        shuffled = group[group["condition"] == "shuffled"].iloc[0]
        row = c.to_dict()
        row.update({
            "Delta_viable_propagation_vs_product": c["viable_propagation_index"] - product["viable_propagation_index"],
            "Delta_viable_propagation_vs_shuffled": c["viable_propagation_index"] - shuffled["viable_propagation_index"],
            "Delta_depth_vs_product": c["certified_path_mass_survival_to_final_segment"] - product["certified_path_mass_survival_to_final_segment"],
            "Delta_depth_vs_shuffled": c["certified_path_mass_survival_to_final_segment"] - shuffled["certified_path_mass_survival_to_final_segment"],
            "Delta_robust_reachability_vs_product": c["breadth_index"] * c["certified_path_mass_survival_to_final_segment"] - product["breadth_index"] * product["certified_path_mass_survival_to_final_segment"],
            "Delta_robust_reachability_vs_shuffled": c["breadth_index"] * c["certified_path_mass_survival_to_final_segment"] - shuffled["breadth_index"] * shuffled["certified_path_mass_survival_to_final_segment"],
            "Delta_breadth_vs_product": c["breadth_index"] - product["breadth_index"],
            "Delta_breadth_vs_shuffled": c["breadth_index"] - shuffled["breadth_index"],
            "Delta_R": c["macro_path_entropy"] - shuffled["macro_path_entropy"],
            "Delta_H_weighted_product": c["p_viable"] * c["macro_path_entropy"] - product["p_viable"] * product["macro_path_entropy"],
        })
        rows.append(row)
    deltas = pd.DataFrame(rows)
    seed_rows = []
    for key, group in main.groupby(["variant_id", "perturbation_family", "perturbation_strength", "alpha", "T", "kappa", "seed"]):
        variant_id, family, strength, alpha, T, kappa, seed = key
        c = group[group["condition"] == "coupled"].iloc[0]
        product = group[group["condition"] == "product"].iloc[0]
        shuffled = group[group["condition"] == "shuffled"].iloc[0]
        seed_rows.append({
            "variant_id": variant_id, "perturbation_family": family, "perturbation_strength": strength,
            "alpha": alpha, "T": T, "kappa": kappa, "seed": seed,
            "Delta_viable_propagation_vs_shuffled": c["viable_propagation_index"] - shuffled["viable_propagation_index"],
            "Delta_viable_propagation_vs_product": c["viable_propagation_index"] - product["viable_propagation_index"],
            "Delta_depth_vs_shuffled": c["certified_path_mass_survival_to_final_segment"] - shuffled["certified_path_mass_survival_to_final_segment"],
            "Delta_depth_vs_product": c["certified_path_mass_survival_to_final_segment"] - product["certified_path_mass_survival_to_final_segment"],
            "Delta_robust_reachability_vs_shuffled": c["breadth_index"] * c["certified_path_mass_survival_to_final_segment"] - shuffled["breadth_index"] * shuffled["certified_path_mass_survival_to_final_segment"],
            "Delta_robust_reachability_vs_product": c["breadth_index"] * c["certified_path_mass_survival_to_final_segment"] - product["breadth_index"] * product["certified_path_mass_survival_to_final_segment"],
            "component_B_preservation": c["component_B_preservation"],
            "lower_rank_erasure_score": c["lower_rank_erasure_score"],
            "singleton_fraction": c["singleton_fraction"],
        })
    seed_df = pd.DataFrame(seed_rows)
    intervals = bootstrap(seed_df, ["variant_id", "perturbation_family", "perturbation_strength", "alpha", "T", "kappa"], BOOT_METRICS, cfg.bootstrap_repeats)
    intervals.to_csv(out / "bootstrap_intervals.csv", index=False)
    stability = intervals[intervals["metric"] == "Delta_viable_propagation_vs_shuffled"][["variant_id", "alpha", "T", "kappa", "ci_low", "ci_high", "ci_width"]]
    deltas = deltas.merge(stability, on=["variant_id", "alpha", "T", "kappa"], how="left")
    deltas["estimator_stable"] = (deltas["ci_width"] <= np.maximum(0.02, 0.30 * np.abs(deltas["Delta_viable_propagation_vs_shuffled"])))
    ref = deltas[(deltas["variant_id"] == "reference_000") & (deltas["kappa"] == "center_of_mass")].groupby(["alpha", "T"])["Delta_viable_propagation_vs_shuffled"].mean().to_dict()
    deltas["category"] = deltas.apply(lambda r: categorize(r, ref.get((r["alpha"], r["T"]), 0.0)), axis=1)
    deltas["propagation_retained"] = (
        (deltas["Delta_viable_propagation_vs_shuffled"] > 0)
        & (deltas["Delta_viable_propagation_vs_product"] > 0)
        & (deltas["component_B_preservation"] >= 0.70)
        & (deltas["lower_rank_erasure_score"] <= 0.20)
        & (deltas["singleton_fraction"] <= 0.65)
        & deltas["estimator_stable"]
    )
    deltas.to_csv(out / "propagation_deltas.csv", index=False)
    deltas.to_csv(out / "robustness_by_variant.csv", index=False)
    deltas[["variant_id", "perturbation_family", "perturbation_strength", "alpha", "T", "kappa", "component_A_preservation", "component_B_preservation", "lower_rank_erasure_score", "singleton_fraction"]].to_csv(out / "component_preservation.csv", index=False)
    deltas[["variant_id", "perturbation_family", "perturbation_strength", "alpha", "T", "kappa", "Delta_R", "Delta_H_weighted_product", "Delta_breadth_vs_product", "Delta_breadth_vs_shuffled", "macro_path_entropy", "macro_node_entropy", "breadth_index"]].to_csv(out / "secondary_entropy_diagnostics.csv", index=False)
    raw.groupby(["variant_id", "perturbation_family", "perturbation_strength", "threshold", "condition", "alpha", "T", "kappa"], as_index=False).mean(numeric_only=True).to_csv(out / "threshold_sensitivity.csv", index=False)
    ref_rows = deltas[deltas["variant_id"] == "reference_000"]
    ref_rows.to_csv(out / "reference_reproduction.csv", index=False)
    est = deltas[["variant_id", "perturbation_family", "perturbation_strength", "alpha", "T", "kappa", "singleton_fraction", "estimator_stable", "ci_width", "category"]]
    est.to_csv(out / "estimator_report.csv", index=False)
    metadata = pd.DataFrame([p.__dict__ for p in perturbations])
    metadata.to_csv(out / "perturbation_metadata.csv", index=False)
    family = deltas.groupby(["perturbation_family", "perturbation_strength", "kappa"], as_index=False).agg(
        fraction_positive_vs_product=("Delta_viable_propagation_vs_product", lambda s: float(np.mean(s > 0))),
        fraction_positive_vs_shuffled=("Delta_viable_propagation_vs_shuffled", lambda s: float(np.mean(s > 0))),
        fraction_component_preserving=("component_B_preservation", lambda s: float(np.mean(s >= 0.70))),
        fraction_non_overfragmented=("singleton_fraction", lambda s: float(np.mean(s <= 0.65))),
        fraction_estimator_stable=("estimator_stable", "mean"),
        retention_rate=("propagation_retained", "mean"),
        median_Delta_viable_propagation_vs_shuffled=("Delta_viable_propagation_vs_shuffled", "median"),
        median_Delta_depth_vs_shuffled=("Delta_depth_vs_shuffled", "median"),
    )
    family.to_csv(out / "robustness_by_family.csv", index=False)
    make_plots(out, deltas, family)
    com = deltas[deltas["kappa"] == "center_of_mass"]
    summary = {
        "probe": "10_com_viable_propagation_robustness",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "workers": cfg.workers,
        "n_traj": cfg.n_traj,
        "seed_count": len(cfg.seeds),
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "perturbation_families_completed": sorted(deltas["perturbation_family"].unique().tolist()),
        "variants_completed": int(deltas["variant_id"].nunique()),
        "rows_completed": int(len(deltas)),
        "reference_reproduction": ref_rows[["alpha", "T", "kappa", "Delta_viable_propagation_vs_shuffled", "category"]].to_dict(orient="records"),
        "COM_overall_retention_rate": float(com["propagation_retained"].mean()),
        "COM_retention_rate_by_family": com.groupby("perturbation_family")["propagation_retained"].mean().to_dict(),
        "category_counts": deltas["category"].value_counts().to_dict(),
        "files": sorted(p.name for p in out.glob("*") if not p.name.startswith("_")),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def make_plots(out: Path, deltas: pd.DataFrame, family: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    com_family = family[family["kappa"] == "center_of_mass"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(com_family["perturbation_family"] + ":" + com_family["perturbation_strength"], com_family["retention_rate"])
    ax.set_xlim(0, 1)
    ax.set_title("COM retention rate by family")
    fig.tight_layout()
    fig.savefig(out / "com_retention_rate_by_family.png", dpi=160)
    plt.close(fig)
    for col, filename, title in [
        ("Delta_viable_propagation_vs_shuffled", "delta_viable_propagation_by_perturbation.png", "Delta viable propagation by perturbation"),
        ("Delta_depth_vs_shuffled", "delta_depth_by_perturbation.png", "Delta depth by perturbation"),
        ("component_B_preservation", "component_preservation_by_perturbation.png", "Component preservation by perturbation"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 5))
        for k, g in deltas.groupby("kappa"):
            ax.scatter(range(len(g)), g[col], label=k, s=12)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_title(title)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out / filename, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    s = deltas[deltas["perturbation_family"].isin(["sink_threshold", "noise"])]
    ax.scatter(s["Delta_viable_propagation_vs_shuffled"], s["Delta_depth_vs_shuffled"], c=s["alpha"])
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Sink/noise sensitivity")
    fig.tight_layout()
    fig.savefig(out / "sink_noise_sensitivity.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    t = deltas[deltas["perturbation_family"].isin(["reference", "certification_threshold"])]
    ax.scatter(t["variant_id"], t["Delta_viable_propagation_vs_shuffled"])
    ax.tick_params(axis="x", rotation=45)
    ax.set_title("Threshold sensitivity")
    fig.tight_layout()
    fig.savefig(out / "threshold_sensitivity.png", dpi=160)
    plt.close(fig)
    ref = deltas[deltas["variant_id"] == "reference_000"]
    pert = deltas[deltas["variant_id"] != "reference_000"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(ref["T"], ref["Delta_viable_propagation_vs_shuffled"], label="reference")
    ax.scatter(pert["T"], pert["Delta_viable_propagation_vs_shuffled"], alpha=0.25, label="perturbed")
    ax.set_title("Reference vs perturbed COM/control")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "reference_vs_perturbed_com.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    for k, g in deltas.groupby("kappa"):
        ax.scatter(g["Delta_R"], g["Delta_viable_propagation_vs_shuffled"], label=k, s=12)
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Entropy vs propagation")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "entropy_vs_propagation_scatter.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    for k, g in deltas.groupby("kappa"):
        ax.scatter(g["T"], g["Delta_viable_propagation_vs_shuffled"], label=k, s=12)
    ax.set_title("Control kappa comparison")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "control_kappa_comparison.png", dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    status = "COMPLETE"
    seed_path = cfg.out_dir / "_seed_metrics.csv"
    if seed_path.exists():
        seed_path.unlink()
    perturbations = make_perturbations(cfg.perturbations_per_family)
    if args.families:
        keep = set(args.families)
        perturbations = [p for p in perturbations if p.family in keep or p.family == "reference"]
    kappas = tuple(args.kappas)
    tasks = [(p, alpha, seed, cfg, kappas) for p in perturbations for alpha in cfg.alphas for seed in cfg.seeds]
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
            append_rows(seed_path, fut.result())
            completed += 1
            if completed % max(1, cfg.workers) == 0:
                print(json.dumps({"completed_seed_blocks": completed, "total_launched": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
            if status == "PARTIAL_EXIT_HARD_LIMIT":
                break
    summary = build_outputs(cfg, perturbations, started, status)
    print("PROBE 10: COM VIABLE PROPAGATION ROBUSTNESS")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
