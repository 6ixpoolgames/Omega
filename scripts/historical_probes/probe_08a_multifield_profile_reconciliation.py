#!/usr/bin/env python
"""Probe 08a: focused multifield profile reconciliation.

This is a standalone toy multifield simulator. It is not claimed to be the
original unpublished multifield simulator. The purpose is to stress the local
workflow and reconcile the old fiber/richness diagnostics with the newer
Single Omega profile tuple under product and shuffled baselines.
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


KAPPAS = [
    "center_of_mass",
    "relative_distance",
    "joint_basin",
    "basin_transition_profile",
    "boundary_v2_regime_sequence",
    "random_kappa_matched",
    "identity_like_diagnostic",
    "all_one_diagnostic",
]

MAIN_DELTAS = [
    "Delta_R",
    "Delta_p_viable_product",
    "Delta_H_cond_product",
    "Delta_H_weighted_product",
    "Delta_H_recovery_product",
    "strict_certified_mass_advantage",
    "certified_transport_density_advantage",
]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seeds: list[int]
    alphas: list[float]
    horizons: list[int]
    soft_limit_seconds: float
    hard_limit_seconds: float
    bootstrap_repeats: int
    sample_points: int
    dt: float
    noise: float
    coupling_scale: float


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("probe_08a_multifield_profile_reconciliation_results"))
    parser.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    parser.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "500")))
    parser.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "80")))
    parser.add_argument("--seed-start", type=int, default=int(os.environ.get("OMEGA_SEED_START", "0")))
    parser.add_argument(
        "--alphas",
        type=parse_csv_floats,
        default=parse_csv_floats(os.environ.get("OMEGA_ALPHAS", "0.40,0.45,0.50,0.525,0.55,0.60")),
    )
    parser.add_argument(
        "--horizons",
        type=parse_csv_ints,
        default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "900,1500,2400,3600")),
    )
    parser.add_argument("--soft-limit-sec", type=float, default=float(os.environ.get("OMEGA_SOFT_LIMIT_SECONDS", "10800")))
    parser.add_argument("--hard-limit-sec", type=float, default=float(os.environ.get("OMEGA_HARD_LIMIT_SECONDS", "14400")))
    parser.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "200")))
    parser.add_argument("--sample-points", type=int, default=int(os.environ.get("OMEGA_SAMPLE_POINTS", "13")))
    parser.add_argument("--dt", type=float, default=float(os.environ.get("OMEGA_DT", "0.018")))
    parser.add_argument("--noise", type=float, default=float(os.environ.get("OMEGA_NOISE", "0.055")))
    parser.add_argument("--coupling-scale", type=float, default=float(os.environ.get("OMEGA_COUPLING_SCALE", "0.085")))
    return parser.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    seeds = list(range(args.seed_start, args.seed_start + args.seed_count))
    return Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seeds=seeds,
        alphas=args.alphas,
        horizons=sorted(args.horizons),
        soft_limit_seconds=args.soft_limit_sec,
        hard_limit_seconds=args.hard_limit_sec,
        bootstrap_repeats=args.bootstrap_repeats,
        sample_points=args.sample_points,
        dt=args.dt,
        noise=args.noise,
        coupling_scale=args.coupling_scale,
    )


def drift_f(x: np.ndarray) -> np.ndarray:
    return -0.034 * (x + 0.95) + 0.016 * np.sin(2.35 * x) - 0.0025 * x**3


def drift_t(x: np.ndarray) -> np.ndarray:
    return -0.095 * (x - 1.10) - 0.014 * (x - 1.10) ** 3


def basin_code(x: np.ndarray) -> np.ndarray:
    out = np.full(x.shape, 1, dtype=np.int16)
    out[x < -0.45] = 0
    out[x > 0.55] = 2
    return out


def entropy_from_counts(counts: np.ndarray) -> float:
    counts = counts[counts > 0].astype(np.float64)
    if counts.size == 0:
        return 0.0
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(p)))


def entropy_from_keys(keys: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    if keys.size == 0:
        return 0.0, np.array([], dtype=np.int64), np.array([], dtype=np.int64)
    uniq, counts = np.unique(keys, return_counts=True)
    return entropy_from_counts(counts), uniq, counts


def weighted_entropy(keys: np.ndarray, weights: np.ndarray) -> float:
    if keys.size == 0:
        return 0.0
    uniq, inv = np.unique(keys, return_inverse=True)
    sums = np.bincount(inv, weights=weights, minlength=len(uniq)).astype(np.float64)
    total = sums.sum()
    if total <= 0:
        return 0.0
    p = sums[sums > 0] / total
    return float(-np.sum(p * np.log2(p)))


def combine_codes(parts: Iterable[np.ndarray], base: int = 4099) -> np.ndarray:
    out: np.ndarray | None = None
    for part in parts:
        p = part.astype(np.int64) + 2048
        if p.ndim == 1:
            seq = [p]
        elif p.ndim == 2:
            seq = [p[i] for i in range(p.shape[0])]
        else:
            raise ValueError(f"unsupported key part shape: {p.shape}")
        for item in seq:
            out = item.copy() if out is None else out * base + item
    if out is None:
        raise ValueError("empty key parts")
    return out


def simulate_pair_block(
    alpha: float,
    seed: int,
    n_traj: int,
    horizons: list[int],
    sample_points: int,
    dt: float,
    noise: float,
    coupling_scale: float,
    coupled: bool,
    shuffle: bool = False,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(810_017 + seed * 1009 + int(round(alpha * 10000)) * 17 + (0 if coupled else 53))
    max_h = max(horizons)
    sample_idx = np.unique(np.rint(np.linspace(0, max_h, sample_points)).astype(int))

    a = -1.10 + 0.62 * rng.normal(size=n_traj)
    b = 1.12 + 0.18 * rng.normal(size=n_traj)
    if shuffle:
        b = b[rng.permutation(n_traj)]

    rec_a = np.empty((len(sample_idx), n_traj), dtype=np.float32)
    rec_b = np.empty((len(sample_idx), n_traj), dtype=np.float32)
    rec_i = 0
    rec_a[rec_i] = a
    rec_b[rec_i] = b
    rec_i += 1

    alive_a = np.abs(a) < 3.0
    alive_b = np.abs(b) < 3.0
    energy_a = np.zeros(n_traj, dtype=np.float64)
    energy_b = np.zeros(n_traj, dtype=np.float64)
    horizon_alive: dict[int, np.ndarray] = {}
    horizon_alive_a: dict[int, np.ndarray] = {}
    horizon_alive_b: dict[int, np.ndarray] = {}
    horizon_recovery: dict[int, np.ndarray] = {}
    horizon_recovery_a: dict[int, np.ndarray] = {}
    horizon_recovery_b: dict[int, np.ndarray] = {}

    for t in range(1, max_h + 1):
        delta = b - a
        if coupled:
            ca = alpha * coupling_scale * delta
            cb = -alpha * coupling_scale * delta
        else:
            ca = 0.0
            cb = 0.0

        da = (drift_f(a) + ca) * dt + noise * math.sqrt(dt) * rng.normal(size=n_traj)
        db = (drift_t(b) + cb) * dt + noise * math.sqrt(dt) * rng.normal(size=n_traj)
        a = np.clip(a + da, -3.8, 3.8)
        b = np.clip(b + db, -3.8, 3.8)
        energy_a += np.abs(da)
        energy_b += np.abs(db)
        alive_a &= (np.abs(a) < 3.0) & (energy_a < 0.18 * t + 4.0)
        alive_b &= (np.abs(b) < 3.0) & (energy_b < 0.18 * t + 4.0)

        if rec_i < len(sample_idx) and t == sample_idx[rec_i]:
            rec_a[rec_i] = a
            rec_b[rec_i] = b
            rec_i += 1
        if t in horizons:
            margin_a = 3.0 - np.abs(a)
            margin_b = 3.0 - np.abs(b)
            recovery_a = np.clip((margin_a + 0.35) / 1.55, 0.0, 1.0)
            recovery_b = np.clip((margin_b + 0.35) / 1.55, 0.0, 1.0)
            recovery = np.minimum(recovery_a, recovery_b)
            horizon_alive[t] = (alive_a & alive_b).copy()
            horizon_alive_a[t] = alive_a.copy()
            horizon_alive_b[t] = alive_b.copy()
            horizon_recovery[t] = recovery.astype(np.float64)
            horizon_recovery_a[t] = recovery_a.astype(np.float64)
            horizon_recovery_b[t] = recovery_b.astype(np.float64)

    return {
        "sample_idx": sample_idx,
        "rec_a": rec_a,
        "rec_b": rec_b,
        "alive": horizon_alive,
        "alive_a": horizon_alive_a,
        "alive_b": horizon_alive_b,
        "recovery": horizon_recovery,
        "recovery_a": horizon_recovery_a,
        "recovery_b": horizon_recovery_b,
    }


def horizon_slice(block: dict[str, np.ndarray], horizon: int) -> tuple[np.ndarray, np.ndarray]:
    idx = block["sample_idx"] <= horizon
    return block["rec_a"][idx], block["rec_b"][idx]


def kappa_keys(name: str, a_path: np.ndarray, b_path: np.ndarray, seed: int) -> np.ndarray:
    a_final = a_path[-1]
    b_final = b_path[-1]
    if name == "center_of_mass":
        return combine_codes([np.rint(((a_path + b_path) / 2.0) / 0.24).astype(np.int16)])
    if name == "relative_distance":
        return combine_codes([np.rint(np.abs(a_path - b_path) / 0.18).astype(np.int16)])
    if name == "joint_basin":
        return combine_codes([basin_code(a_path) * 4 + basin_code(b_path)])
    if name == "basin_transition_profile":
        ba = basin_code(a_path)
        bb = basin_code(b_path)
        pair = ba * 4 + bb
        transitions = np.sum(pair[1:] != pair[:-1], axis=0).astype(np.int16)
        return combine_codes([pair[0], pair[-1], transitions])
    if name == "boundary_v2_regime_sequence":
        com = (a_path + b_path) / 2.0
        dist = np.abs(a_path - b_path)
        regime = np.zeros(com.shape, dtype=np.int16)
        regime[com > 0.85] = 1
        regime[com < -0.85] = 2
        regime[dist > 2.0] = 3
        regime[(np.abs(a_path) > 2.35) | (np.abs(b_path) > 2.35)] = 4
        return combine_codes([regime])
    if name == "random_kappa_matched":
        coarse = combine_codes([
            np.rint(((a_path + b_path) / 2.0) / 0.34).astype(np.int16),
            np.rint(np.abs(a_path - b_path) / 0.26).astype(np.int16),
        ])
        return ((coarse * 1_103_515_245 + 12_345 + seed * 97) % 251).astype(np.int64)
    if name == "identity_like_diagnostic":
        return combine_codes([
            np.rint(a_path / 0.08).astype(np.int16),
            np.rint(b_path / 0.08).astype(np.int16),
        ])
    if name == "all_one_diagnostic":
        return np.zeros(a_final.shape, dtype=np.int64)
    raise KeyError(name)


def component_keys(a_path: np.ndarray, b_path: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ka = combine_codes([basin_code(a_path), np.rint(a_path / 0.36).astype(np.int16)])
    kb = combine_codes([basin_code(b_path), np.rint(b_path / 0.36).astype(np.int16)])
    return ka, kb


def profile_for_keys(keys: np.ndarray, alive: np.ndarray, recovery: np.ndarray) -> dict[str, float]:
    n = len(keys)
    viable_keys = keys[alive]
    p_viable = float(np.mean(alive)) if n else 0.0
    h_cond, uniq, counts = entropy_from_keys(viable_keys)
    h_weighted = p_viable * h_cond
    h_recovery = weighted_entropy(keys, recovery)
    r_bits = float(np.sum((counts / counts.sum()) * np.log2(counts))) if counts.sum() > 0 else 0.0
    singleton = float(np.mean(counts == 1)) if counts.size else 1.0
    return {
        "p_viable": p_viable,
        "H_cond": h_cond,
        "H_weighted": h_weighted,
        "H_recovery": h_recovery,
        "R_bits": r_bits,
        "macro_classes": float(len(uniq)),
        "singleton_fraction": singleton,
    }


def fiber_metrics(keys: np.ndarray, alive: np.ndarray, recovery: np.ndarray, ka: np.ndarray, kb: np.ndarray) -> dict[str, float]:
    uniq, inv, counts = np.unique(keys, return_inverse=True, return_counts=True)
    if len(uniq) == 0:
        return {}
    viable_sum = np.bincount(inv, weights=alive.astype(float), minlength=len(uniq))
    rec_sum = np.bincount(inv, weights=recovery, minlength=len(uniq))
    fiber_viability = viable_sum / counts
    fiber_recovery = rec_sum / counts
    h_a, _, _ = entropy_from_keys(ka[alive])
    h_b, _, _ = entropy_from_keys(kb[alive])
    h_joint, _, _ = entropy_from_keys(keys[alive])
    denom = max(h_joint, 1e-9)
    comp_a = min(1.0, h_a / denom)
    comp_b = min(1.0, h_b / denom)
    return {
        "mean_fiber_size": float(np.mean(counts)),
        "median_fiber_size": float(np.median(counts)),
        "fiber_entropy_mean": entropy_from_counts(counts),
        "fiber_entropy_weighted": float(np.sum((counts / counts.sum()) * np.log2(counts))),
        "singleton_fraction": float(np.mean(counts == 1)),
        "viable_fiber_fraction": float(np.mean(viable_sum > 0)),
        "fiber_viability_mixing": float(np.mean((fiber_viability > 0.05) & (fiber_viability < 0.95))),
        "fiber_recoverability_mixing": float(np.mean((fiber_recovery > 0.05) & (fiber_recovery < 0.95))),
        "projected_A_entropy": h_a,
        "projected_B_entropy": h_b,
        "component_A_preservation": comp_a,
        "component_B_preservation": comp_b,
        "lower_rank_erasure_score": float(1.0 - 0.5 * (comp_a + comp_b)),
    }


def transport_metrics(keys: np.ndarray, alive: np.ndarray, shuffled_keys: np.ndarray) -> dict[str, float]:
    survival = float(np.mean(alive))
    h_all, _, _ = entropy_from_keys(keys)
    h_live, _, _ = entropy_from_keys(keys[alive])
    transitions = np.stack([keys[:-1], keys[1:]], axis=0) if len(keys) > 1 else np.empty((2, 0), dtype=np.int64)
    shuf_transitions = (
        np.stack([shuffled_keys[:-1], shuffled_keys[1:]], axis=0)
        if len(shuffled_keys) > 1
        else np.empty((2, 0), dtype=np.int64)
    )
    density = float(np.unique(transitions, axis=1).shape[1] / max(len(keys) - 1, 1))
    shuf_density = float(np.unique(shuf_transitions, axis=1).shape[1] / max(len(shuffled_keys) - 1, 1))
    return {
        "transport_survival": survival,
        "transport_entropy_change": h_live - h_all,
        "certified_transport_density": density,
        "transport_advantage_vs_shuffled": density - shuf_density,
    }


def run_seed_task(args: tuple[float, int, Config]) -> dict[str, list[dict[str, object]]]:
    alpha, seed, cfg = args
    coupled = simulate_pair_block(alpha, seed, cfg.n_traj, cfg.horizons, cfg.sample_points, cfg.dt, cfg.noise, cfg.coupling_scale, True)
    independent = simulate_pair_block(0.0, seed + 20_000, cfg.n_traj, cfg.horizons, cfg.sample_points, cfg.dt, cfg.noise, cfg.coupling_scale, False)
    shuffled = simulate_pair_block(0.0, seed + 40_000, cfg.n_traj, cfg.horizons, cfg.sample_points, cfg.dt, cfg.noise, cfg.coupling_scale, False, True)

    joint_rows: list[dict[str, object]] = []
    product_rows: list[dict[str, object]] = []
    shuffled_rows: list[dict[str, object]] = []
    fiber_rows: list[dict[str, object]] = []
    transport_rows: list[dict[str, object]] = []
    component_rows: list[dict[str, object]] = []
    estimator_rows: list[dict[str, object]] = []

    for horizon in cfg.horizons:
        a_c, b_c = horizon_slice(coupled, horizon)
        a_i, b_i = horizon_slice(independent, horizon)
        a_s, b_s = horizon_slice(shuffled, horizon)
        alive_c = coupled["alive"][horizon]
        alive_i = independent["alive"][horizon]
        alive_s = shuffled["alive"][horizon]
        rec_c = coupled["recovery"][horizon]
        rec_i = independent["recovery"][horizon]
        rec_s = shuffled["recovery"][horizon]
        alive_a_i = independent["alive_a"][horizon]
        alive_b_i = independent["alive_b"][horizon]
        rec_a_i = independent["recovery_a"][horizon]
        rec_b_i = independent["recovery_b"][horizon]
        ka_c, kb_c = component_keys(a_c, b_c)
        ka_i, kb_i = component_keys(a_i, b_i)
        h_a, _, _ = entropy_from_keys(ka_i[alive_a_i])
        h_b, _, _ = entropy_from_keys(kb_i[alive_b_i])
        p_a = float(np.mean(alive_a_i))
        p_b = float(np.mean(alive_b_i))
        h_recovery_prod = weighted_entropy(ka_i, rec_a_i) + weighted_entropy(kb_i, rec_b_i)

        for kappa in KAPPAS:
            keys_c = kappa_keys(kappa, a_c, b_c, seed)
            keys_i = kappa_keys(kappa, a_i, b_i, seed)
            keys_s = kappa_keys(kappa, a_s, b_s, seed)
            prof_c = profile_for_keys(keys_c, alive_c, rec_c)
            prof_i = profile_for_keys(keys_i, alive_i, rec_i)
            prof_s = profile_for_keys(keys_s, alive_s, rec_s)
            p_prod = p_a * p_b
            h_prod = h_a + h_b
            hw_prod = p_prod * h_prod
            delta_r = prof_c["R_bits"] - prof_s["R_bits"]
            strict_mass_adv = prof_c["p_viable"] - prof_s["p_viable"]
            t = transport_metrics(keys_c, alive_c, keys_s)
            f = fiber_metrics(keys_c, alive_c, rec_c, ka_c, kb_c)
            heldout = heldout_stability(keys_c, alive_c)
            warn = estimator_warning(prof_c, cfg.n_traj)

            base = {"alpha": alpha, "T": horizon, "kappa": kappa, "seed": seed}
            joint_rows.append({
                **base,
                "p_viable_AB": prof_c["p_viable"],
                "p_viable_independent": prof_i["p_viable"],
                "p_viable_shuffled": prof_s["p_viable"],
                "H_cond_AB": prof_c["H_cond"],
                "H_cond_independent": prof_i["H_cond"],
                "H_cond_shuffled": prof_s["H_cond"],
                "H_weighted_AB": prof_c["H_weighted"],
                "H_weighted_independent": prof_i["H_weighted"],
                "H_weighted_shuffled": prof_s["H_weighted"],
                "H_recovery_AB": prof_c["H_recovery"],
                "H_recovery_independent": prof_i["H_recovery"],
                "H_recovery_shuffled": prof_s["H_recovery"],
                "Delta_R": delta_r,
                "Delta_p_viable_product": prof_c["p_viable"] - p_prod,
                "Delta_H_cond_product": prof_c["H_cond"] - h_prod,
                "Delta_H_weighted_product": prof_c["H_weighted"] - hw_prod,
                "Delta_H_recovery_product": prof_c["H_recovery"] - h_recovery_prod,
                "Delta_p_viable_shuffled": prof_c["p_viable"] - prof_s["p_viable"],
                "Delta_H_cond_shuffled": prof_c["H_cond"] - prof_s["H_cond"],
                "Delta_H_weighted_shuffled": prof_c["H_weighted"] - prof_s["H_weighted"],
                "Delta_H_recovery_shuffled": prof_c["H_recovery"] - prof_s["H_recovery"],
                "strict_certified_mass_advantage": strict_mass_adv,
                "certified_transport_density_advantage": t["transport_advantage_vs_shuffled"],
                "singleton_fraction": prof_c["singleton_fraction"],
                "overfragmented_flag": bool(prof_c["singleton_fraction"] > 0.55),
                "heldout_stability": heldout,
                "status_label_old_style": old_style_label(delta_r, strict_mass_adv, t["transport_advantage_vs_shuffled"], prof_c["singleton_fraction"]),
                "estimator_warning": warn,
                "estimator_mode": "vectorized_seed_block",
            })
            product_rows.append({
                **base,
                "p_viable_product": p_prod,
                "H_cond_product": h_prod,
                "H_weighted_product": hw_prod,
                "H_recovery_product": h_recovery_prod,
                "component_estimator_note": "H_A+H_B from basin/geometric component projections",
            })
            shuffled_rows.append({**base, **{f"{k}_shuffled": v for k, v in prof_s.items()}})
            fiber_rows.append({**base, **f})
            component_rows.append({
                **base,
                "projected_A_entropy": f["projected_A_entropy"],
                "projected_B_entropy": f["projected_B_entropy"],
                "component_A_preservation": f["component_A_preservation"],
                "component_B_preservation": f["component_B_preservation"],
                "lower_rank_erasure_score": f["lower_rank_erasure_score"],
            })
            transport_rows.append({**base, **t})
            estimator_rows.append({
                **base,
                "n_traj": cfg.n_traj,
                "macro_classes": prof_c["macro_classes"],
                "singleton_fraction": prof_c["singleton_fraction"],
                "estimator_warning": warn,
            })

    return {
        "joint": joint_rows,
        "product": product_rows,
        "shuffled": shuffled_rows,
        "fiber": fiber_rows,
        "transport": transport_rows,
        "component": component_rows,
        "estimator": estimator_rows,
    }


def heldout_stability(keys: np.ndarray, alive: np.ndarray) -> float:
    live = keys[alive]
    if live.size < 4:
        return 0.0
    a = live[::2]
    b = live[1::2]
    ua, ca = np.unique(a, return_counts=True)
    ub, cb = np.unique(b, return_counts=True)
    all_u = np.union1d(ua, ub)
    pa = np.zeros(len(all_u), dtype=np.float64)
    pb = np.zeros(len(all_u), dtype=np.float64)
    pa[np.searchsorted(all_u, ua)] = ca / ca.sum()
    pb[np.searchsorted(all_u, ub)] = cb / cb.sum()
    return float(1.0 - 0.5 * np.abs(pa - pb).sum())


def estimator_warning(profile: dict[str, float], n_traj: int) -> str:
    if profile["p_viable"] < 0.05:
        return "LOW_VIABILITY"
    if profile["singleton_fraction"] > 0.65:
        return "HIGH_SINGLETON_FRACTION"
    if profile["macro_classes"] > 0.6 * n_traj:
        return "NEAR_IDENTITY_FRAGMENTATION"
    return ""


def old_style_label(delta_r: float, mass_adv: float, transport_adv: float, singleton: float) -> str:
    if singleton > 0.65 and delta_r > 0:
        return "pseudo_risk_fragmented"
    if mass_adv > 0 and transport_adv > 0:
        return "candidate"
    if delta_r > 0:
        return "richness_only"
    if mass_adv > 0 or transport_adv > 0:
        return "weak_transport_or_mass"
    return "null_or_negative"


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def bootstrap_summary(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int, seed: int = 90210) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        seeds = group["seed"].unique()
        base = dict(zip(group_cols, key))
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(dtype=float)
            mean = float(np.mean(vals))
            std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            if len(vals) > 1 and repeats > 0:
                boot = np.empty(repeats, dtype=float)
                for i in range(repeats):
                    boot[i] = np.mean(rng.choice(vals, size=len(vals), replace=True))
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            rows.append({**base, "metric": metric, "mean": mean, "std": std, "se": std / math.sqrt(max(len(vals), 1)), "ci_low": float(lo), "ci_high": float(hi), "n_seeds": len(vals)})
    return pd.DataFrame(rows)


def horizon_stability(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metrics = ["Delta_R", "Delta_p_viable_product", "Delta_H_cond_product", "Delta_H_weighted_product", "Delta_H_recovery_product"]
    for (alpha, kappa), group in df.groupby(["alpha", "kappa"]):
        by_t = group.groupby("T")[metrics].mean().sort_index()
        row: dict[str, object] = {"alpha": alpha, "kappa": kappa}
        scores = []
        for metric in metrics:
            vals = by_t[metric].to_numpy(dtype=float)
            signs = np.sign(vals)
            sign_changes = int(np.sum(signs[1:] * signs[:-1] < 0)) if len(signs) > 1 else 0
            row[f"{metric}_early_to_late_delta"] = float(vals[-1] - vals[0]) if len(vals) else 0.0
            row[f"{metric}_sign_changes"] = sign_changes
            scale = float(np.mean(np.abs(vals)) + 1e-9)
            scores.append(float(1.0 / (1.0 + np.std(vals) / scale)))
        row["horizon_stability_score"] = float(np.mean(scores))
        rows.append(row)
    return pd.DataFrame(rows)


def interpretation(row: pd.Series) -> str:
    near_zero = all(abs(float(row[c])) < 0.03 for c in ["Delta_p_viable_product", "Delta_H_weighted_product", "strict_certified_mass_advantage", "certified_transport_density_advantage"])
    if near_zero:
        return "Null-like"
    if row.get("estimator_warning", ""):
        return "Inconclusive"
    if (row["strict_certified_mass_advantage"] > 0 or row["certified_transport_density_advantage"] > 0) and row["lower_rank_erasure_score"] < 0.45 and row["singleton_fraction"] < 0.55:
        return "Profile-consistent bundle candidate"
    if row["Delta_R"] > 0 and (row["strict_certified_mass_advantage"] <= 0 or row["certified_transport_density_advantage"] <= 0 or row["singleton_fraction"] > 0.55):
        return "Entropy-only / pseudo-risk"
    if row["Delta_H_cond_product"] <= 0 and (row["Delta_p_viable_product"] > 0 or row["Delta_H_recovery_product"] > 0) and row["lower_rank_erasure_score"] < 0.55:
        return "Stabilizing coupling"
    if row["Delta_H_cond_product"] > 0 and (row["Delta_H_weighted_product"] <= 0 or row["Delta_H_recovery_product"] <= 0 or row["lower_rank_erasure_score"] >= 0.55):
        return "Fragile richness"
    return "Inconclusive"


def build_final_outputs(cfg: Config, started: float, status: str) -> dict[str, object]:
    out = cfg.out_dir
    joint = pd.read_csv(out / "joint_profile_by_alpha_T_kappa.csv")
    fiber = pd.read_csv(out / "fiber_profile_summary.csv")
    component = pd.read_csv(out / "component_preservation.csv")
    transport = pd.read_csv(out / "transport_summary.csv")
    estimator = pd.read_csv(out / "estimator_report.csv")

    group_cols = ["alpha", "T", "kappa"]
    joint_mean = joint.groupby(group_cols, as_index=False).mean(numeric_only=True)
    fiber_mean = fiber.groupby(group_cols, as_index=False).mean(numeric_only=True)
    comp_mean = component.groupby(group_cols, as_index=False).mean(numeric_only=True)
    trans_mean = transport.groupby(group_cols, as_index=False).mean(numeric_only=True)
    est_mode = estimator.groupby(group_cols)["estimator_warning"].agg(
        lambda s: ";".join(
            sorted({str(x) for x in s if pd.notna(x) and str(x) and str(x) != "nan"})
        )
    ).reset_index()
    stab = horizon_stability(joint)
    stab.to_csv(out / "horizon_stability_summary.csv", index=False)

    recon = joint_mean.merge(fiber_mean, on=group_cols, suffixes=("", "_fiber"))
    recon = recon.merge(comp_mean, on=group_cols, suffixes=("", "_component"))
    recon = recon.merge(trans_mean, on=group_cols, suffixes=("", "_transport"))
    recon = recon.merge(stab[["alpha", "kappa", "horizon_stability_score"]], on=["alpha", "kappa"], how="left")
    recon = recon.merge(est_mode, on=group_cols, how="left")
    recon["category"] = recon.apply(interpretation, axis=1)
    recon_cols = [
        "alpha", "T", "kappa", "Delta_R", "Delta_p_viable_product", "Delta_H_cond_product",
        "Delta_H_weighted_product", "Delta_H_recovery_product", "strict_certified_mass_advantage",
        "certified_transport_density_advantage", "singleton_fraction", "component_A_preservation",
        "component_B_preservation", "lower_rank_erasure_score", "horizon_stability_score",
        "estimator_warning", "category",
    ]
    recon[recon_cols].to_csv(out / "reconciliation_table.csv", index=False)

    ci = bootstrap_summary(joint, group_cols, [m for m in MAIN_DELTAS if m in joint.columns], cfg.bootstrap_repeats)
    ci.to_csv(out / "bootstrap_main_deltas.csv", index=False)

    corridor = recon[(recon["kappa"] == "center_of_mass") & (recon["alpha"].isin([0.45, 0.525]))]
    best = recon[recon["category"] == "Profile-consistent bundle candidate"].sort_values(
        ["strict_certified_mass_advantage", "certified_transport_density_advantage"], ascending=False
    ).head(5)
    pseudo = recon[recon["category"] == "Entropy-only / pseudo-risk"].sort_values("Delta_R", ascending=False).head(5)
    summary = {
        "probe": "08a_multifield_profile_reconciliation",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "workers": cfg.workers,
        "n_traj": cfg.n_traj,
        "seed_count_requested": len(cfg.seeds),
        "seed_count_completed": int(joint["seed"].nunique()),
        "alphas_completed": sorted(float(x) for x in joint["alpha"].unique()),
        "horizons_completed": sorted(int(x) for x in joint["T"].unique()),
        "kappas_completed": sorted(joint["kappa"].unique().tolist()),
        "estimator_warnings": estimator["estimator_warning"].fillna("").value_counts().to_dict(),
        "old_candidate_corridor": corridor[recon_cols].to_dict(orient="records"),
        "best_profile_consistent_candidates": best[recon_cols].to_dict(orient="records"),
        "pseudo_risk_candidates": pseudo[recon_cols].to_dict(orient="records"),
        "interpretation_counts": recon["category"].value_counts().to_dict(),
        "files": sorted(p.name for p in out.glob("*")),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()

    for name in [
        "joint_profile_by_alpha_T_kappa.csv",
        "product_baseline_profiles.csv",
        "shuffled_baseline_profiles.csv",
        "fiber_profile_summary.csv",
        "transport_summary.csv",
        "component_preservation.csv",
        "estimator_report.csv",
    ]:
        path = cfg.out_dir / name
        if path.exists():
            path.unlink()

    tasks = [(alpha, seed, cfg) for alpha in cfg.alphas for seed in cfg.seeds]
    status = "COMPLETE"
    completed = 0
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = []
        for task in tasks:
            elapsed = time.monotonic() - started
            if elapsed > cfg.soft_limit_seconds:
                status = "PARTIAL_EXIT_SOFT_LIMIT"
                break
            futures.append(pool.submit(run_seed_task, task))

        for fut in as_completed(futures):
            elapsed = time.monotonic() - started
            if elapsed > cfg.hard_limit_seconds:
                status = "PARTIAL_EXIT_HARD_LIMIT"
            result = fut.result()
            append_rows(cfg.out_dir / "joint_profile_by_alpha_T_kappa.csv", result["joint"])
            append_rows(cfg.out_dir / "product_baseline_profiles.csv", result["product"])
            append_rows(cfg.out_dir / "shuffled_baseline_profiles.csv", result["shuffled"])
            append_rows(cfg.out_dir / "fiber_profile_summary.csv", result["fiber"])
            append_rows(cfg.out_dir / "transport_summary.csv", result["transport"])
            append_rows(cfg.out_dir / "component_preservation.csv", result["component"])
            append_rows(cfg.out_dir / "estimator_report.csv", result["estimator"])
            completed += 1
            if completed % max(1, cfg.workers) == 0:
                print(json.dumps({"completed_seed_blocks": completed, "total_launched": len(futures), "elapsed_seconds": round(elapsed, 1)}), flush=True)
            if status == "PARTIAL_EXIT_HARD_LIMIT":
                break

    summary = build_final_outputs(cfg, started, status)
    print("PROBE 08A: MULTIFIELD PROFILE RECONCILIATION")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
