#!/usr/bin/env python
"""Probe 11: learned predictive kappa for viable propagation.

This probe asks whether a simple learned quotient can discover a propagation
macro-coordinate without being handed COM bins as labels. Training uses only
primitive future viability/progression targets plus quotient simplicity.
Heldout Omega-style propagation metrics remain diagnostics.
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
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score, normalized_mutual_info_score

import probe_08a_multifield_profile_reconciliation as p08a


SEGMENT_COUNT = 6
SMALL_FIBER_MIN_SIZE = 5
ALPHAS_TRAIN = [0.45, 0.50]
ALPHAS_TEST = [0.525]
HORIZONS_TRAIN = [900, 1500]
HORIZONS_TEST = [1500, 2400]
LEARNED_SPECS = [
    ("predictive_kmeans_k5", 5, True),
    ("predictive_kmeans_k8", 8, True),
    ("predictive_kmeans_k13", 13, True),
    ("predictive_kmeans_k21", 21, True),
    ("predictive_kmeans_no_COM_k8", 8, False),
    ("predictive_kmeans_no_COM_k13", 13, False),
]
REGULARIZATION_VARIANTS = {
    "light": {"singleton": 0.10, "small_fiber": 0.05, "imbalance": 0.05},
    "main": {"singleton": 0.25, "small_fiber": 0.10, "imbalance": 0.10},
    "strict": {"singleton": 0.40, "small_fiber": 0.20, "imbalance": 0.15},
}
CONTROL_KAPPAS = [
    "center_of_mass",
    "joint_basin",
    "boundary_v2_regime_sequence",
    "identity_diagnostic",
    "all_one_diagnostic",
]
BOOT_METRICS = [
    "Delta_viable_propagation_vs_product",
    "Delta_viable_propagation_vs_shuffled",
    "Delta_depth_vs_product",
    "Delta_depth_vs_shuffled",
    "component_A_preservation",
    "component_B_preservation",
    "lower_rank_erasure_score",
    "singleton_fraction",
]


@dataclass(frozen=True)
class Perturbation:
    variant_id: str
    family: str
    strength_label: str
    split: str
    noise_multiplier: float = 1.0
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
    seed_count: int
    seed_start: int
    bootstrap_repeats: int
    soft_limit_seconds: float
    hard_limit_seconds: float
    dt: float
    noise: float
    coupling_scale: float
    train_variants_per_family: int
    val_variants_per_family: int
    test_variants_per_family: int
    max_train_samples: int
    sample_per_seed: int
    smoke: bool


@dataclass
class LearnedKappa:
    name: str
    k: int
    include_com: bool
    scaler_mean: np.ndarray
    scaler_std: np.ndarray
    target_mean: np.ndarray
    target_std: np.ndarray
    model: KMeans
    train_label_means: np.ndarray


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_11_learned_predictive_kappa_revised_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "5000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "100")))
    p.add_argument("--seed-start", type=int, default=int(os.environ.get("OMEGA_SEED_START", "0")))
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "300")))
    p.add_argument("--soft-limit-sec", type=float, default=float(os.environ.get("OMEGA_SOFT_LIMIT_SECONDS", "3300")))
    p.add_argument("--hard-limit-sec", type=float, default=float(os.environ.get("OMEGA_HARD_LIMIT_SECONDS", "3600")))
    p.add_argument("--train-variants-per-family", type=int, default=8)
    p.add_argument("--val-variants-per-family", type=int, default=4)
    p.add_argument("--test-variants-per-family", type=int, default=8)
    p.add_argument("--max-train-samples", type=int, default=220_000)
    p.add_argument("--sample-per-seed", type=int, default=220)
    p.add_argument("--dt", type=float, default=0.018)
    p.add_argument("--noise", type=float, default=0.055)
    p.add_argument("--coupling-scale", type=float, default=0.085)
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.n_traj = min(args.n_traj, 700)
        args.seed_count = min(args.seed_count, 6)
        args.bootstrap_repeats = min(args.bootstrap_repeats, 40)
        args.train_variants_per_family = min(args.train_variants_per_family, 2)
        args.val_variants_per_family = min(args.val_variants_per_family, 1)
        args.test_variants_per_family = min(args.test_variants_per_family, 2)
        args.max_train_samples = min(args.max_train_samples, 25_000)
        args.sample_per_seed = min(args.sample_per_seed, 120)
    return Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seed_count=args.seed_count,
        seed_start=args.seed_start,
        bootstrap_repeats=args.bootstrap_repeats,
        soft_limit_seconds=args.soft_limit_sec,
        hard_limit_seconds=args.hard_limit_sec,
        dt=args.dt,
        noise=args.noise,
        coupling_scale=args.coupling_scale,
        train_variants_per_family=args.train_variants_per_family,
        val_variants_per_family=args.val_variants_per_family,
        test_variants_per_family=args.test_variants_per_family,
        max_train_samples=args.max_train_samples,
        sample_per_seed=args.sample_per_seed,
        smoke=args.smoke,
    )


def make_perturbations(cfg: Config) -> list[Perturbation]:
    rng = np.random.default_rng(11_011)
    out = [Perturbation("reference_000", "reference", "reference", "train")]
    specs = [
        ("train", "mild", cfg.train_variants_per_family),
        ("validation", "mild", cfg.val_variants_per_family),
        ("test", "moderate", cfg.test_variants_per_family),
    ]
    for split, strength_label, count in specs:
        for family in ["noise", "potential_shape", "time_discretization"]:
            for i in range(count):
                suffix = f"{split}_{i:03d}"
                if family == "noise":
                    choices = [0.85, 1.15] if strength_label == "mild" else [0.70, 1.30]
                    out.append(Perturbation(f"{family}_{suffix}", family, strength_label, split, noise_multiplier=float(rng.choice(choices))))
                elif family == "potential_shape":
                    strength = 0.05 if strength_label == "mild" else 0.10
                    out.append(Perturbation(
                        f"{family}_{suffix}", family, strength_label, split,
                        drift_scale_f=1.0 + rng.choice([-1, 1]) * strength,
                        drift_scale_t=1.0 + rng.choice([-1, 1]) * strength,
                        center_shift_f=float(rng.uniform(-0.03, 0.03) * (strength / 0.05)),
                        center_shift_t=float(rng.uniform(-0.03, 0.03) * (strength / 0.05)),
                    ))
                else:
                    out.append(Perturbation(f"{family}_{suffix}", family, strength_label, split, dt_multiplier=float(rng.choice([0.8, 1.2]))))
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


def combine_codes(parts: list[np.ndarray], base: int = 4099) -> np.ndarray:
    return p08a.combine_codes(parts, base=base)


def drift_f_perturbed(x: np.ndarray, p: Perturbation) -> np.ndarray:
    return p.drift_scale_f * p08a.drift_f(x - p.center_shift_f)


def drift_t_perturbed(x: np.ndarray, p: Perturbation) -> np.ndarray:
    return p.drift_scale_t * p08a.drift_t(x - p.center_shift_t)


def simulate(alpha: float, horizon: int, seed: int, cfg: Config, perturb: Perturbation, coupled: bool, shuffle: bool) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(111_000 + seed * 1009 + int(round(alpha * 10000)) * 37 + abs(hash((perturb.variant_id, coupled, shuffle))) % 100_000)
    boundaries = np.array([int(round(i * horizon / SEGMENT_COUNT)) for i in range(SEGMENT_COUNT + 1)], dtype=np.int32)
    n = cfg.n_traj
    a = -1.10 + 0.62 * rng.normal(size=n)
    b = 1.12 + 0.18 * rng.normal(size=n)
    if shuffle:
        b = b[rng.permutation(n)]
    rec_a = np.empty((SEGMENT_COUNT + 1, n), dtype=np.float32)
    rec_b = np.empty((SEGMENT_COUNT + 1, n), dtype=np.float32)
    alive_seg = np.empty((SEGMENT_COUNT + 1, n), dtype=bool)
    rec_i = 0
    rec_a[0] = a
    rec_b[0] = b
    energy_a = np.zeros(n, dtype=np.float64)
    energy_b = np.zeros(n, dtype=np.float64)
    alive_a = np.abs(a) < 3.0
    alive_b = np.abs(b) < 3.0
    alive_seg[0] = alive_a & alive_b
    dt = cfg.dt * perturb.dt_multiplier
    noise = cfg.noise * perturb.noise_multiplier
    for t in range(1, horizon + 1):
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
        alive_a &= (np.abs(a) < 3.0) & (energy_a < 0.18 * t * perturb.dt_multiplier + 4.0)
        alive_b &= (np.abs(b) < 3.0) & (energy_b < 0.18 * t * perturb.dt_multiplier + 4.0)
        if rec_i + 1 < len(boundaries) and t == boundaries[rec_i + 1]:
            rec_i += 1
            rec_a[rec_i] = a
            rec_b[rec_i] = b
            alive_seg[rec_i] = alive_a & alive_b
    return {"a": rec_a, "b": rec_b, "alive_seg": alive_seg, "alive_final": alive_seg[-1]}


def feature_target_matrix(block: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    a = block["a"]
    b = block["b"]
    alive_seg = block["alive_seg"]
    n_seg, n = a.shape
    rows = []
    targets = []
    anatomy = {"com_bin": [], "basin": [], "rel_bin": []}
    for seg in range(n_seg - 1):
        aa = a[seg]
        bb = b[seg]
        rel = np.abs(aa - bb)
        signed = aa - bb
        com = (aa + bb) / 2.0
        basin_a = p08a.basin_code(aa)
        basin_b = p08a.basin_code(bb)
        margin = np.minimum(3.0 - np.abs(aa), 3.0 - np.abs(bb))
        future_alive = alive_seg[-1].astype(float)
        future_depth = alive_seg[seg + 1 :].mean(axis=0)
        recovery = np.clip((margin + 0.35) / 1.55, 0.0, 1.0)
        rows.append(np.column_stack([
            aa, bb, np.zeros_like(aa), np.zeros_like(bb), rel, signed,
            3.0 - np.abs(aa), 3.0 - np.abs(bb), basin_a, basin_b,
            (basin_a == basin_b).astype(float), com,
        ]))
        targets.append(np.column_stack([future_alive, recovery, future_depth]))
        anatomy["com_bin"].append(np.rint(com / 0.24).astype(np.int64))
        anatomy["basin"].append((basin_a * 4 + basin_b).astype(np.int64))
        anatomy["rel_bin"].append(np.rint(rel / 0.24).astype(np.int64))
    return np.vstack(rows), np.vstack(targets), {k: np.concatenate(v) for k, v in anatomy.items()}


def row_sample_task(task: tuple[Perturbation, float, int, int, Config]) -> dict[str, object]:
    perturb, alpha, horizon, seed, cfg = task
    block = simulate(alpha, horizon, seed, cfg, perturb, True, False)
    x, y, anatomy = feature_target_matrix(block)
    rng = np.random.default_rng(222_000 + seed + horizon)
    take = min(cfg.sample_per_seed, len(x))
    idx = rng.choice(len(x), take, replace=False)
    return {
        "variant_id": perturb.variant_id,
        "split": perturb.split,
        "alpha": alpha,
        "T": horizon,
        "seed": seed,
        "x": x[idx].astype(np.float32),
        "y": y[idx].astype(np.float32),
        "com_bin": anatomy["com_bin"][idx],
        "basin": anatomy["basin"][idx],
        "rel_bin": anatomy["rel_bin"][idx],
    }


def scaler(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std[std < 1e-8] = 1.0
    return mean, std


def make_phi(x: np.ndarray, y: np.ndarray, include_com: bool, x_mean: np.ndarray, x_std: np.ndarray, y_mean: np.ndarray, y_std: np.ndarray) -> np.ndarray:
    cols = list(range(x.shape[1]))
    if not include_com:
        cols.remove(11)
    xs = (x[:, cols] - x_mean[cols]) / x_std[cols]
    ys = (y - y_mean) / y_std
    return np.column_stack([xs, ys]).astype(np.float64, copy=False)


def simplicity(labels: np.ndarray, k: int) -> dict[str, float]:
    _, counts = np.unique(labels, return_counts=True)
    if counts.size == 0:
        return {"num_label_penalty": 0.0, "singleton_fraction": 1.0, "small_fiber_fraction": 1.0, "label_imbalance": 1.0}
    p = counts / counts.sum()
    h = -float(np.sum(p * np.log(np.maximum(p, 1e-12))))
    return {
        "num_label_penalty": float(k / max(len(labels), 1)),
        "singleton_fraction": float(np.mean(counts == 1)),
        "small_fiber_fraction": float(np.mean(counts < SMALL_FIBER_MIN_SIZE)),
        "label_imbalance": float(1.0 - h / max(math.log(max(k, 2)), 1e-9)),
    }


def fit_learned_kappas(sample_df: dict[str, np.ndarray], cfg: Config) -> tuple[list[LearnedKappa], pd.DataFrame]:
    x_train = sample_df["train_x"]
    y_train = sample_df["train_y"]
    x_val = sample_df["validation_x"]
    y_val = sample_df["validation_y"]
    rng = np.random.default_rng(11_500)
    if len(x_train) > cfg.max_train_samples:
        idx = rng.choice(len(x_train), cfg.max_train_samples, replace=False)
        x_fit = x_train[idx]
        y_fit = y_train[idx]
    else:
        x_fit = x_train
        y_fit = y_train
    x_mean, x_std = scaler(x_fit)
    y_mean, y_std = scaler(y_fit)
    learned: list[LearnedKappa] = []
    rows = []
    for name, k, include_com in LEARNED_SPECS:
        phi = make_phi(x_fit, y_fit, include_com, x_mean, x_std, y_mean, y_std)
        model = KMeans(n_clusters=k, n_init=10, max_iter=100, random_state=11_000 + k + (0 if include_com else 100))
        labels = model.fit_predict(phi)
        label_means = np.zeros((k, y_train.shape[1]), dtype=np.float64)
        global_mean = y_fit.mean(axis=0)
        for j in range(k):
            mask = labels == j
            label_means[j] = y_fit[mask].mean(axis=0) if np.any(mask) else global_mean
        train_pred = label_means[labels]
        train_loss = float(np.mean((y_fit - train_pred) ** 2))
        val_phi = make_phi(x_val, y_val, include_com, x_mean, x_std, y_mean, y_std)
        val_labels = model.predict(val_phi)
        val_pred = label_means[val_labels]
        val_loss = float(np.mean((y_val - val_pred) ** 2))
        simp = simplicity(val_labels, k)
        for reg_name, weights in REGULARIZATION_VARIANTS.items():
            total = (
                val_loss
                + 0.005 * simp["num_label_penalty"]
                + weights["singleton"] * simp["singleton_fraction"]
                + weights["small_fiber"] * simp["small_fiber_fraction"]
                + weights["imbalance"] * simp["label_imbalance"]
            )
            rows.append({
                "kappa": name, "k": k, "include_COM_feature": include_com,
                "regularization": reg_name, "train_predictive_loss": train_loss,
                "validation_predictive_loss": val_loss, **simp,
                "total_validation_loss": float(total),
            })
        learned.append(LearnedKappa(name, k, include_com, x_mean, x_std, y_mean, y_std, model, label_means))
    return learned, pd.DataFrame(rows)


def learned_labels(model: LearnedKappa, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    phi = make_phi(x, y, model.include_com, model.scaler_mean, model.scaler_std, model.target_mean, model.target_std)
    return model.model.predict(phi).astype(np.int64)


def control_labels(name: str, a_path: np.ndarray, b_path: np.ndarray) -> np.ndarray:
    if name == "center_of_mass":
        return np.rint(((a_path + b_path) / 2.0) / 0.24).astype(np.int64)
    if name == "joint_basin":
        return (p08a.basin_code(a_path) * 4 + p08a.basin_code(b_path)).astype(np.int64)
    if name == "boundary_v2_regime_sequence":
        com = (a_path + b_path) / 2.0
        dist = np.abs(a_path - b_path)
        regime = np.zeros(com.shape, dtype=np.int64)
        regime[com > 0.85] = 1
        regime[com < -0.85] = 2
        regime[dist > 2.0] = 3
        regime[(np.abs(a_path) > 2.35) | (np.abs(b_path) > 2.35)] = 4
        return regime
    if name == "identity_diagnostic":
        return (np.rint(a_path / 0.08).astype(np.int64) * 100_003 + np.rint(b_path / 0.08).astype(np.int64))
    if name == "all_one_diagnostic":
        return np.zeros_like(a_path, dtype=np.int64)
    raise KeyError(name)


def entropy(keys: np.ndarray) -> float:
    h, _, _ = p08a.entropy_from_keys(keys.astype(np.int64))
    return h


def graph_metrics(condition: str, alpha: float, horizon: int, kappa: str, seed: int, perturb: Perturbation, block: dict[str, np.ndarray], labels_path: np.ndarray) -> dict[str, object]:
    alive = block["alive_final"]
    n_viable = int(np.sum(alive))
    if n_viable == 0:
        alive = np.ones_like(alive, dtype=bool)
        n_viable = int(len(alive))
    nodes = labels_path[:, alive]
    path_key = combine_codes([nodes])
    _, path_counts = np.unique(path_key, return_counts=True)
    singleton_fraction = float(np.mean(path_counts == 1)) if path_counts.size else 1.0
    small_fiber_fraction = float(np.mean(path_counts < SMALL_FIBER_MIN_SIZE)) if path_counts.size else 1.0
    h_path = entropy(path_key)
    breadth_index = h_path / math.log2(max(n_viable, 2))
    a_path = block["a"][:, alive]
    b_path = block["b"][:, alive]
    ka = combine_codes([p08a.basin_code(a_path), np.rint(a_path / 0.36).astype(np.int16)])
    kb = combine_codes([p08a.basin_code(b_path), np.rint(b_path / 0.36).astype(np.int16)])
    comp_a = min(1.0, entropy(ka) / max(h_path, 1e-9))
    comp_b = min(1.0, entropy(kb) / max(h_path, 1e-9))
    erasure = 1.0 - 0.5 * (comp_a + comp_b)
    certified_nodes: list[set[int]] = []
    for layer in range(SEGMENT_COUNT + 1):
        uniq, counts = np.unique(nodes[layer], return_counts=True)
        certified_nodes.append({int(u) for u, c in zip(uniq, counts) if c / n_viable >= 0.005})
    certified_edge_masks = np.zeros((SEGMENT_COUNT, n_viable), dtype=bool)
    cert_edge_count = 0
    all_edge_count = 0
    for seg in range(SEGMENT_COUNT):
        edge = nodes[seg] * 100_003 + nodes[seg + 1]
        uniq, counts = np.unique(edge, return_counts=True)
        all_edge_count += len(uniq)
        cert_edges = set()
        for e, c in zip(uniq, counts):
            src = int(e // 100_003)
            dst = int(e % 100_003)
            if c / n_viable >= 0.001 and src in certified_nodes[seg] and dst in certified_nodes[seg + 1]:
                cert_edges.add(int(e))
                cert_edge_count += 1
        certified_edge_masks[seg] = np.isin(edge, list(cert_edges)) if cert_edges else False
    prefix = np.ones(n_viable, dtype=bool)
    prefix_survival = []
    for seg in range(SEGMENT_COUNT):
        prefix &= certified_edge_masks[seg]
        prefix_survival.append(float(np.mean(prefix)))
    transport_survival_mean = float(np.mean([np.mean(certified_edge_masks[i]) for i in range(SEGMENT_COUNT)]))
    final_survival = prefix_survival[-1]
    depth = float(np.sum([(i + 1) / SEGMENT_COUNT * s for i, s in enumerate(prefix_survival)]) / np.sum([(i + 1) / SEGMENT_COUNT for i in range(SEGMENT_COUNT)]))
    viable_prop = final_survival * transport_survival_mean * min(comp_a, comp_b) * max(0.0, 1.0 - singleton_fraction)
    return {
        "variant_id": perturb.variant_id, "perturbation_family": perturb.family,
        "perturbation_strength": perturb.strength_label, "split": perturb.split,
        "condition": condition, "alpha": alpha, "T": horizon, "kappa": kappa, "seed": seed,
        "p_viable": float(np.mean(block["alive_final"])),
        "certified_path_mass_survival_to_final_segment": final_survival,
        "multi_step_transport_depth": depth,
        "transport_survival_mean": transport_survival_mean,
        "viable_propagation_index": viable_prop,
        "component_A_preservation": comp_a,
        "component_B_preservation": comp_b,
        "lower_rank_erasure_score": erasure,
        "singleton_fraction": singleton_fraction,
        "small_fiber_fraction": small_fiber_fraction,
        "certified_node_fraction": float(sum(len(x) for x in certified_nodes) / max(sum(len(set(nodes[i])) for i in range(SEGMENT_COUNT + 1)), 1)),
        "viable_fiber_fraction": 1.0,
        "macro_path_entropy": h_path,
        "macro_node_entropy": entropy(nodes.reshape(-1)),
        "breadth_index": breadth_index,
        "certified_transport_density": float(cert_edge_count / max(all_edge_count, 1)),
    }


def eval_task(task: tuple[Perturbation, float, int, int, Config, list[LearnedKappa]]) -> list[dict[str, object]]:
    perturb, alpha, horizon, seed, cfg, learned = task
    blocks = {
        "coupled": simulate(alpha, horizon, seed, cfg, perturb, True, False),
        "product": simulate(0.0, horizon, seed + 20_000, cfg, perturb, False, False),
        "shuffled": simulate(0.0, horizon, seed + 40_000, cfg, perturb, False, True),
    }
    rows = []
    for condition, block in blocks.items():
        x, y, _ = feature_target_matrix(block)
        for model in learned:
            labels_flat = learned_labels(model, x, y)
            labels_path = labels_flat.reshape((SEGMENT_COUNT, cfg.n_traj))
            labels_path = np.vstack([labels_path, labels_path[-1]])
            rows.append(graph_metrics(condition, alpha, horizon, model.name, seed, perturb, block, labels_path))
            rng = np.random.default_rng(333_000 + seed + model.k)
            rand_path = np.vstack([rng.integers(0, model.k, size=cfg.n_traj) for _ in range(SEGMENT_COUNT + 1)]).astype(np.int64)
            rows.append(graph_metrics(condition, alpha, horizon, f"random_matched_{model.name}", seed, perturb, block, rand_path))
        for kappa in CONTROL_KAPPAS:
            labels_path = control_labels(kappa, block["a"], block["b"])
            rows.append(graph_metrics(condition, alpha, horizon, kappa, seed, perturb, block, labels_path))
    return rows


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(11_800)
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


def build_outputs(cfg: Config, learned: list[LearnedKappa], validation: pd.DataFrame, sample_df: dict[str, np.ndarray], perturbations: list[Perturbation], started: float, status: str, gpu_note: str) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_metrics.csv")
    means = raw.groupby(["variant_id", "perturbation_family", "perturbation_strength", "split", "condition", "alpha", "T", "kappa"], as_index=False).mean(numeric_only=True)
    rows = []
    for key, group in means.groupby(["variant_id", "perturbation_family", "perturbation_strength", "split", "alpha", "T", "kappa"]):
        variant_id, family, strength, split, alpha, horizon, kappa = key
        c = group[group["condition"] == "coupled"].iloc[0]
        product = group[group["condition"] == "product"].iloc[0]
        shuffled = group[group["condition"] == "shuffled"].iloc[0]
        row = c.to_dict()
        row.update({
            "Delta_viable_propagation_vs_product": c["viable_propagation_index"] - product["viable_propagation_index"],
            "Delta_viable_propagation_vs_shuffled": c["viable_propagation_index"] - shuffled["viable_propagation_index"],
            "Delta_depth_vs_product": c["certified_path_mass_survival_to_final_segment"] - product["certified_path_mass_survival_to_final_segment"],
            "Delta_depth_vs_shuffled": c["certified_path_mass_survival_to_final_segment"] - shuffled["certified_path_mass_survival_to_final_segment"],
            "Delta_breadth_vs_product": c["breadth_index"] - product["breadth_index"],
            "Delta_breadth_vs_shuffled": c["breadth_index"] - shuffled["breadth_index"],
            "Delta_R": c["macro_path_entropy"] - shuffled["macro_path_entropy"],
            "Delta_H_weighted": c["p_viable"] * c["macro_path_entropy"] - shuffled["p_viable"] * shuffled["macro_path_entropy"],
        })
        rows.append(row)
    deltas = pd.DataFrame(rows)
    seed_rows = []
    for key, group in raw.groupby(["variant_id", "perturbation_family", "perturbation_strength", "split", "alpha", "T", "kappa", "seed"]):
        variant_id, family, strength, split, alpha, horizon, kappa, seed = key
        c = group[group["condition"] == "coupled"].iloc[0]
        product = group[group["condition"] == "product"].iloc[0]
        shuffled = group[group["condition"] == "shuffled"].iloc[0]
        seed_rows.append({
            "variant_id": variant_id, "perturbation_family": family, "perturbation_strength": strength, "split": split,
            "alpha": alpha, "T": horizon, "kappa": kappa, "seed": seed,
            "Delta_viable_propagation_vs_product": c["viable_propagation_index"] - product["viable_propagation_index"],
            "Delta_viable_propagation_vs_shuffled": c["viable_propagation_index"] - shuffled["viable_propagation_index"],
            "Delta_depth_vs_product": c["certified_path_mass_survival_to_final_segment"] - product["certified_path_mass_survival_to_final_segment"],
            "Delta_depth_vs_shuffled": c["certified_path_mass_survival_to_final_segment"] - shuffled["certified_path_mass_survival_to_final_segment"],
            "component_A_preservation": c["component_A_preservation"],
            "component_B_preservation": c["component_B_preservation"],
            "lower_rank_erasure_score": c["lower_rank_erasure_score"],
            "singleton_fraction": c["singleton_fraction"],
        })
    seed_df = pd.DataFrame(seed_rows)
    intervals = bootstrap(seed_df, ["variant_id", "perturbation_family", "perturbation_strength", "split", "alpha", "T", "kappa"], BOOT_METRICS, cfg.bootstrap_repeats)
    intervals.to_csv(out / "bootstrap_intervals.csv", index=False)
    deltas["is_learned"] = deltas["kappa"].isin([m.name for m in learned])
    deltas["is_random_matched"] = deltas["kappa"].str.startswith("random_matched_")
    deltas["propagation_positive"] = (deltas["Delta_viable_propagation_vs_product"] > 0) & (deltas["Delta_viable_propagation_vs_shuffled"] > 0)
    deltas["component_preserving"] = (deltas["component_A_preservation"] >= 0.70) & (deltas["component_B_preservation"] >= 0.70)
    deltas["nonfragmented"] = (deltas["singleton_fraction"] <= 0.65) & (deltas["small_fiber_fraction"] <= 0.75)
    deltas["low_erasure"] = deltas["lower_rank_erasure_score"] <= 0.20
    deltas["learned_candidate"] = deltas["is_learned"] & deltas["propagation_positive"] & deltas["component_preserving"] & deltas["nonfragmented"] & deltas["low_erasure"]
    deltas.to_csv(out / "learned_kappa_test_propagation.csv", index=False)
    deltas[["kappa", "variant_id", "split", "alpha", "T", "singleton_fraction", "small_fiber_fraction", "macro_path_entropy", "macro_node_entropy"]].to_csv(out / "quotient_simplicity_terms.csv", index=False)
    deltas[["kappa", "variant_id", "split", "alpha", "T", "component_A_preservation", "component_B_preservation", "lower_rank_erasure_score"]].to_csv(out / "component_preservation_by_label.csv", index=False)
    validation.to_csv(out / "learned_kappa_validation_loss.csv", index=False)
    validation.to_csv(out / "regularization_sensitivity.csv", index=False)
    main_val = validation[validation["regularization"] == "main"].sort_values("total_validation_loss")
    best_name = str(main_val.iloc[0]["kappa"])
    com = deltas[(deltas["kappa"] == "center_of_mass") & (deltas["split"] == "test")]
    best = deltas[(deltas["kappa"] == best_name) & (deltas["split"] == "test")]
    learned_vs_com = best.merge(com, on=["variant_id", "alpha", "T"], suffixes=("_learned", "_COM"))
    learned_vs_com["viable_propagation_ratio"] = learned_vs_com["Delta_viable_propagation_vs_shuffled_learned"] / learned_vs_com["Delta_viable_propagation_vs_shuffled_COM"].replace(0, np.nan)
    learned_vs_com["depth_ratio"] = learned_vs_com["Delta_depth_vs_shuffled_learned"] / learned_vs_com["Delta_depth_vs_shuffled_COM"].replace(0, np.nan)
    learned_vs_com.to_csv(out / "learned_vs_com_comparison.csv", index=False)
    random_rows = []
    for model in learned:
        l = deltas[(deltas["kappa"] == model.name) & (deltas["split"] == "test")]
        r = deltas[(deltas["kappa"] == f"random_matched_{model.name}") & (deltas["split"] == "test")]
        m = l.merge(r, on=["variant_id", "alpha", "T"], suffixes=("_learned", "_random"))
        m["kappa_base"] = model.name
        m["viable_propagation_advantage"] = m["Delta_viable_propagation_vs_shuffled_learned"] - m["Delta_viable_propagation_vs_shuffled_random"]
        m["fragmentation_advantage"] = m["singleton_fraction_random"] - m["singleton_fraction_learned"]
        random_rows.append(m)
    learned_vs_random = pd.concat(random_rows, ignore_index=True) if random_rows else pd.DataFrame()
    learned_vs_random.to_csv(out / "learned_vs_random_matched.csv", index=False)
    anatomy_rows = []
    for model in learned:
        labels = learned_labels(model, sample_df["test_x"], sample_df["test_y"])
        for key, vals in [("COM", sample_df["test_com_bin"]), ("joint_basin", sample_df["test_basin"]), ("relative_distance", sample_df["test_rel_bin"])]:
            anatomy_rows.append({
                "kappa": model.name, "association_target": key,
                "normalized_mutual_information": float(normalized_mutual_info_score(vals, labels)),
                "adjusted_mutual_information": float(adjusted_mutual_info_score(vals, labels)),
            })
        for label in np.unique(labels):
            mask = labels == label
            anatomy_rows.append({
                "kappa": model.name, "association_target": f"label_{int(label)}_target_mean",
                "normalized_mutual_information": float(np.mean(sample_df["test_y"][mask, 0])),
                "adjusted_mutual_information": float(np.mean(sample_df["test_y"][mask, 2])),
            })
    anatomy = pd.DataFrame(anatomy_rows)
    anatomy.to_csv(out / "learned_label_anatomy.csv", index=False)
    fiber_rows = []
    for model in learned:
        labels = learned_labels(model, sample_df["test_x"], sample_df["test_y"])
        _, counts = np.unique(labels, return_counts=True)
        fiber_rows.append({
            "kappa": model.name, "min_fiber_size": int(np.min(counts)), "median_fiber_size": float(np.median(counts)),
            "max_fiber_size": int(np.max(counts)), **simplicity(labels, model.k),
        })
    pd.DataFrame(fiber_rows).to_csv(out / "label_fiber_summary.csv", index=False)
    make_plots(out, validation, deltas, anatomy, learned_vs_random)
    test = deltas[deltas["split"] == "test"]
    best_test = test[test["kappa"] == best_name]
    learned_candidates = sorted(test[test["learned_candidate"]]["kappa"].unique().tolist())
    com_assoc = anatomy[(anatomy["kappa"] == best_name) & (anatomy["association_target"] == "COM")]["normalized_mutual_information"]
    com_assoc_v = float(com_assoc.iloc[0]) if len(com_assoc) else 0.0
    learned_com_ratio = float(np.nanmean(learned_vs_com["viable_propagation_ratio"])) if len(learned_vs_com) else float("nan")
    categories = {
        "Learned propagation candidates": learned_candidates,
        "COM-recovered": [best_name] if com_assoc_v > 0.7 and learned_com_ratio >= 0.75 else [],
        "New macro-coordinate candidates": [best_name] if com_assoc_v <= 0.7 and learned_com_ratio >= 1.0 else [],
        "Partial learned candidates": [best_name] if learned_com_ratio < 0.75 and best_test["propagation_positive"].mean() > 0.5 else [],
        "Overfit learned quotients": sorted(test[test["is_learned"] & ~test["propagation_positive"]]["kappa"].unique().tolist()),
        "Fragmentation artifacts": sorted(test[test["is_learned"] & ~test["nonfragmented"]]["kappa"].unique().tolist()),
        "Entropy-only pseudo-risk": sorted(test[(test["Delta_R"] > 0) & ~test["propagation_positive"]]["kappa"].unique().tolist()),
    }
    summary = {
        "probe": "11_learned_predictive_kappa_revised",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "workers": cfg.workers,
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "train_val_test_variants": {
            "train": int(sum(p.split == "train" for p in perturbations)),
            "validation": int(sum(p.split == "validation" for p in perturbations)),
            "test": int(sum(p.split == "test" for p in perturbations)),
        },
        "learned_kappas_evaluated": [m.name for m in learned],
        "regularization_variants": sorted(REGULARIZATION_VARIANTS.keys()),
        "best_learned_kappa_by_validation": main_val.iloc[0].to_dict(),
        "test_performance_best_learned_mean": best_test.mean(numeric_only=True).to_dict(),
        "COM_test_mean": com.mean(numeric_only=True).to_dict(),
        "learned_COM_viable_propagation_ratio_mean": learned_com_ratio,
        "best_learned_COM_association": com_assoc_v,
        "categories": categories,
        "gpu_note": gpu_note,
        "interpretation": interpret(best_name, learned_com_ratio, com_assoc_v, learned_candidates, categories),
        "files": sorted(p.name for p in out.glob("*") if not p.name.startswith("_")),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def interpret(best_name: str, ratio: float, com_assoc: float, candidates: list[str], categories: dict[str, list[str]]) -> str:
    if best_name in categories["COM-recovered"]:
        return "A learned predictive quotient recovered a COM-like viable-propagation coordinate on heldout moderate perturbations."
    if best_name in categories["New macro-coordinate candidates"]:
        return "The best learned quotient matched or exceeded COM without strong COM association; inspect label anatomy before interpreting as a new coordinate."
    if candidates:
        return "At least one learned quotient was propagation-positive and nonfragmented, but COM remains the stronger analytic reference."
    if math.isfinite(ratio) and ratio > 0:
        return "The learned quotient retained partial propagation signal but did not satisfy the candidate gate."
    return "The simple learned quotient class did not recover the current COM propagation object under this probe."


def make_plots(out: Path, validation: pd.DataFrame, deltas: pd.DataFrame, anatomy: pd.DataFrame, learned_vs_random: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    main = validation[validation["regularization"] == "main"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(main["kappa"], main["total_validation_loss"])
    ax.set_title("Validation loss by kappa")
    fig.tight_layout()
    fig.savefig(out / "validation_loss_by_k.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(main["validation_predictive_loss"], main["label_imbalance"], s=35)
    for _, r in main.iterrows():
        ax.annotate(r["kappa"], (r["validation_predictive_loss"], r["label_imbalance"]), fontsize=7)
    ax.set_xlabel("predictive loss")
    ax.set_ylabel("label imbalance")
    ax.set_title("Validation loss components")
    fig.tight_layout()
    fig.savefig(out / "validation_loss_components.png", dpi=160)
    plt.close(fig)
    test = deltas[deltas["split"] == "test"]
    fig, ax = plt.subplots(figsize=(9, 5))
    s = test[test["kappa"].isin(["center_of_mass", *LEARNED_NAMES(test)])]
    for k, g in s.groupby("kappa"):
        ax.scatter(g["T"], g["Delta_viable_propagation_vs_shuffled"], label=k, s=14)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("Test viable propagation: learned vs COM")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "test_viable_propagation_learned_vs_com.png", dpi=160)
    plt.close(fig)
    if len(learned_vs_random):
        fig, ax = plt.subplots(figsize=(9, 5))
        learned_vs_random.groupby("kappa_base")["viable_propagation_advantage"].mean().plot(kind="barh", ax=ax)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title("Learned vs random matched")
        fig.tight_layout()
        fig.savefig(out / "learned_vs_random_matched.png", dpi=160)
        plt.close(fig)
    for target, fname in [("COM", "label_anatomy_com_association.png"), ("joint_basin", "label_anatomy_basin_association.png")]:
        fig, ax = plt.subplots(figsize=(9, 5))
        a = anatomy[anatomy["association_target"] == target]
        ax.barh(a["kappa"], a["normalized_mutual_information"])
        ax.set_title(f"Label anatomy: {target} association")
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    for k, g in test.groupby("kappa"):
        if k.startswith("predictive") or k == "center_of_mass":
            ax.scatter(g["singleton_fraction"], g["small_fiber_fraction"], label=k, s=14)
    ax.set_title("Singleton and small-fiber fraction")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "singleton_and_small_fiber_fraction_by_kappa.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    for k, g in test.groupby("kappa"):
        if k.startswith("predictive") or k == "boundary_v2_regime_sequence":
            ax.scatter(g["Delta_R"], g["Delta_viable_propagation_vs_shuffled"], label=k, s=14)
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Entropy vs propagation learned")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "entropy_vs_propagation_learned.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    for reg, g in validation.groupby("regularization"):
        ax.scatter(g["kappa"], g["total_validation_loss"], label=reg)
    ax.tick_params(axis="x", rotation=45)
    ax.set_title("Regularization sensitivity")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "regularization_sensitivity.png", dpi=160)
    plt.close(fig)


def LEARNED_NAMES(df: pd.DataFrame) -> list[str]:
    return sorted(k for k in df["kappa"].unique() if str(k).startswith("predictive_kmeans"))


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    status = "COMPLETE"
    gpu_note = "CuPy installed but CUDA NVRTC runtime is unavailable; Probe 11 used CPU multiprocessing."
    seed_path = cfg.out_dir / "_seed_metrics.csv"
    if seed_path.exists():
        seed_path.unlink()
    perturbations = make_perturbations(cfg)
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    sample_tasks = []
    for p in perturbations:
        alphas = ALPHAS_TRAIN if p.split in {"train", "validation"} else ALPHAS_TEST
        horizons = HORIZONS_TRAIN if p.split in {"train", "validation"} else HORIZONS_TEST
        for alpha in alphas:
            for horizon in horizons:
                for seed in seeds:
                    sample_tasks.append((p, alpha, horizon, seed, cfg))
    samples: dict[str, list[np.ndarray]] = {f"{split}_{field}": [] for split in ["train", "validation", "test"] for field in ["x", "y", "com_bin", "basin", "rel_bin"]}
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(row_sample_task, t) for t in sample_tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            split = str(r["split"])
            for field in ["x", "y", "com_bin", "basin", "rel_bin"]:
                samples[f"{split}_{field}"].append(r[field])
            if i % max(1, cfg.workers) == 0:
                print(json.dumps({"sample_blocks_completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    sample_df = {k: np.concatenate(v, axis=0) if v else np.empty((0,)) for k, v in samples.items()}
    learned, validation = fit_learned_kappas(sample_df, cfg)
    validation.to_csv(cfg.out_dir / "learned_kappa_validation_loss.csv", index=False)
    eval_perturbations = [p for p in perturbations if p.split == "test"]
    eval_tasks = [(p, alpha, horizon, seed, cfg, learned) for p in eval_perturbations for alpha in ALPHAS_TEST for horizon in HORIZONS_TEST for seed in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = []
        for task in eval_tasks:
            if time.monotonic() - started > cfg.soft_limit_seconds:
                status = "PARTIAL_EXIT_SOFT_LIMIT"
                break
            futures.append(pool.submit(eval_task, task))
        for i, fut in enumerate(as_completed(futures), 1):
            if time.monotonic() - started > cfg.hard_limit_seconds:
                status = "PARTIAL_EXIT_HARD_LIMIT"
            append_rows(seed_path, fut.result())
            if i % max(1, cfg.workers) == 0:
                print(json.dumps({"eval_blocks_completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
            if status == "PARTIAL_EXIT_HARD_LIMIT":
                break
    summary = build_outputs(cfg, learned, validation, sample_df, perturbations, started, status, gpu_note)
    print("PROBE 11: LEARNED PREDICTIVE KAPPA - REVISED")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
