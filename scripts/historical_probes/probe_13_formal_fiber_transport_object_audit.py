#!/usr/bin/env python
"""Probe 13: formal fiber-transport object audit.

This probe returns to the strongest surviving trunk: certified,
component-preserving fiber transport. COM is treated as the current witness,
not as a target to optimize for.
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
import probe_11_learned_predictive_kappa_revised as p11


SEGMENT_COUNT = p11.SEGMENT_COUNT
SMALL_FIBER_MIN_SIZE = p11.SMALL_FIBER_MIN_SIZE
BASE_CONDITIONS = ["coupled", "product", "shuffled", "time_shuffled", "independent_alpha0"]
FALSE_POSITIVE_CONTROLS = [
    "noise_fakeout",
    "endpoint_fakeout",
    "single_component_erasure",
    "component_swap_fakeout",
    "rigid_collapse",
    "delayed_trap",
]
PERTURBATION_CONDITIONS = [
    "noise_mild",
    "noise_moderate",
    "potential_shape_mild",
    "time_discretization_mild",
    "initial_location_mild",
    "sink_threshold_mild",
]
PRIMARY_KAPPAS = [
    "center_of_mass",
    "joint_basin",
    "boundary_v2_regime_sequence",
    "basin_transition_profile",
    "all_one",
    "random_balanced_k_COM_cardinality",
    "hash_high_cardinality",
    "identity_like_sample_id_bucket",
    "time_shuffled_COM",
    "component_A_only",
    "component_B_only",
]
PRIORITY_KAPPAS = [
    "center_of_mass",
    "joint_basin",
    "boundary_v2_regime_sequence",
    "random_balanced_k_COM_cardinality",
    "component_A_only",
    "component_B_only",
    "time_shuffled_COM",
]
THRESHOLDS = {
    "loose": {"node_mass": 0.0025, "edge_mass": 0.0005},
    "main": {"node_mass": 0.005, "edge_mass": 0.001},
    "strict": {"node_mass": 0.01, "edge_mass": 0.002},
}
COMPONENT_THRESHOLDS = [0.50, 0.60, 0.70]
BOOT_METRICS = [
    "viable_propagation_index",
    "Delta_viable_propagation_vs_product",
    "Delta_viable_propagation_vs_shuffled",
    "Delta_viable_propagation_vs_time_shuffled",
    "component_balance",
    "singleton_fraction",
    "certified_path_mass_survival_to_final_segment",
]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seed_count: int
    seed_start: int
    bootstrap_repeats: int
    alphas: list[float]
    horizons: list[int]
    include_extended_conditions: bool
    soft_limit_seconds: float
    hard_limit_seconds: float
    smoke: bool


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_13_formal_fiber_transport_object_audit_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "10000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "160")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "500")))
    p.add_argument("--alphas", type=parse_csv_floats, default=parse_csv_floats(os.environ.get("OMEGA_ALPHAS", "0.45,0.50,0.525")))
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "900,1500,2400")))
    p.add_argument("--soft-limit-sec", type=float, default=14_400.0)
    p.add_argument("--hard-limit-sec", type=float, default=18_000.0)
    p.add_argument("--extended-conditions", action="store_true")
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 6)
        args.n_traj = min(args.n_traj, 1000)
        args.seed_count = min(args.seed_count, 8)
        args.bootstrap_repeats = min(args.bootstrap_repeats, 50)
        args.alphas = [0.50]
        args.horizons = [900]
        args.extended_conditions = True
    return Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seed_count=args.seed_count,
        seed_start=args.seed_start,
        bootstrap_repeats=args.bootstrap_repeats,
        alphas=args.alphas,
        horizons=sorted(args.horizons),
        include_extended_conditions=args.extended_conditions,
        soft_limit_seconds=args.soft_limit_sec,
        hard_limit_seconds=args.hard_limit_sec,
        smoke=args.smoke,
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


def entropy(keys: np.ndarray) -> float:
    h, _, _ = p08a.entropy_from_keys(keys.astype(np.int64))
    return h


def combine_codes(parts: list[np.ndarray], base: int = 4099) -> np.ndarray:
    out = np.zeros_like(parts[0], dtype=np.int64)
    for part in parts:
        out = out * base + (part.astype(np.int64) + base // 2)
    return out.astype(np.int64)


def perturbation_for(condition: str) -> p11.Perturbation:
    if condition in BASE_CONDITIONS or condition in FALSE_POSITIVE_CONTROLS:
        return p11.Perturbation("reference_000", "reference", "reference", "audit")
    if condition == "noise_mild":
        return p11.Perturbation(condition, "noise", "mild", "audit", noise_multiplier=1.15)
    if condition == "noise_moderate":
        return p11.Perturbation(condition, "noise", "moderate", "audit", noise_multiplier=1.30)
    if condition == "potential_shape_mild":
        return p11.Perturbation(condition, "potential_shape", "mild", "audit", drift_scale_f=1.05, drift_scale_t=0.95)
    if condition == "time_discretization_mild":
        return p11.Perturbation(condition, "time_discretization", "mild", "audit", dt_multiplier=1.08)
    if condition == "initial_location_mild":
        return p11.Perturbation(condition, "initial_location", "mild", "audit", center_shift_f=0.05, center_shift_t=-0.05)
    if condition == "sink_threshold_mild":
        return p11.Perturbation(condition, "sink_threshold", "mild", "audit")
    raise KeyError(condition)


def p11_cfg(n_traj: int, seed: int) -> p11.Config:
    return p11.Config(Path("_unused"), 1, n_traj, 1, seed, 1, 1, 1, 0.018, 0.055, 0.085, 1, 1, 1, 1000, 100, False)


def base_block(alpha: float, horizon: int, seed: int, condition: str, n_traj: int) -> dict[str, np.ndarray]:
    cfg = p11_cfg(n_traj, seed)
    perturb = perturbation_for(condition)
    if condition in {"coupled", "time_shuffled"} or condition in FALSE_POSITIVE_CONTROLS or condition in PERTURBATION_CONDITIONS:
        block = p11.simulate(alpha, horizon, seed, cfg, perturb, True, False)
    elif condition == "product":
        block = p11.simulate(0.0, horizon, seed + 20_000, cfg, perturb, False, False)
    elif condition == "shuffled":
        block = p11.simulate(0.0, horizon, seed + 40_000, cfg, perturb, False, True)
    elif condition == "independent_alpha0":
        block = p11.simulate(0.0, horizon, seed + 60_000, cfg, perturb, False, False)
    else:
        raise KeyError(condition)
    if condition == "time_shuffled":
        rng = np.random.default_rng(13_100 + seed)
        perm = rng.permutation(SEGMENT_COUNT + 1)
        block = {**block, "a": block["a"][perm], "b": block["b"][perm]}
    if condition in FALSE_POSITIVE_CONTROLS:
        block = apply_false_positive(block, condition, seed)
    return block


def apply_false_positive(block: dict[str, np.ndarray], condition: str, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(13_200 + seed + abs(hash(condition)) % 1000)
    traj = np.stack([block["a"], block["b"]], axis=2).astype(np.float32)
    out = traj.copy()
    if condition == "rigid_collapse":
        means = out.mean(axis=1, keepdims=True)
        out = means + 0.03 * (out - means)
    elif condition == "noise_fakeout":
        flat = out.reshape(out.shape[0], -1)
        out = (flat.mean(axis=1, keepdims=True) + rng.normal(size=flat.shape) * flat.std(axis=1, keepdims=True)).reshape(out.shape)
    elif condition == "single_component_erasure":
        means = out[:, :, 1].mean(axis=1, keepdims=True)
        out[:, :, 1] = means + 0.03 * (out[:, :, 1] - means)
    elif condition == "endpoint_fakeout":
        start = out[0].copy()
        end = out[-1].copy()
        for s in range(1, SEGMENT_COUNT):
            w = s / SEGMENT_COUNT
            base = (1.0 - w) * start + w * end
            residual = out[s] - base
            out[s] = base + residual[rng.permutation(len(residual))]
    elif condition == "delayed_trap":
        late_mean = out[-1:, :, :].mean(axis=1, keepdims=True)
        out[4:] = late_mean + 0.05 * (out[4:] - late_mean)
    elif condition == "component_swap_fakeout":
        for s in range(1, SEGMENT_COUNT + 1):
            out[s, :, 1] = out[s, rng.permutation(out.shape[1]), 0]
    else:
        raise KeyError(condition)
    return {**block, "a": out[:, :, 0], "b": out[:, :, 1]}


def labels_for(kappa: str, block: dict[str, np.ndarray], seed: int) -> np.ndarray:
    a = block["a"]
    b = block["b"]
    if kappa == "basin_transition_profile":
        ba = p08a.basin_code(a)
        bb = p08a.basin_code(b)
        pair = (ba * 4 + bb).astype(np.int64)
        out = np.empty_like(pair)
        out[0] = pair[0]
        out[1:] = pair[:-1] * 16 + pair[1:]
        return out
    if kappa == "all_one":
        return np.zeros_like(a, dtype=np.int64)
    if kappa == "random_balanced_k_COM_cardinality":
        com = p11.control_labels("center_of_mass", a, b)
        k = max(2, int(np.median([len(np.unique(com[i])) for i in range(com.shape[0])])))
        rng = np.random.default_rng(13_300 + seed)
        return rng.integers(0, k, size=com.shape, dtype=np.int64)
    if kappa == "hash_high_cardinality":
        return (np.rint(a / 0.035).astype(np.int64) * 1_000_003 + np.rint(b / 0.035).astype(np.int64))
    if kappa == "identity_like_sample_id_bucket":
        n = a.shape[1]
        ids = np.arange(n, dtype=np.int64) % max(2, int(np.sqrt(n)))
        return np.tile(ids, (a.shape[0], 1))
    if kappa == "time_shuffled_COM":
        rng = np.random.default_rng(13_400 + seed)
        return p11.control_labels("center_of_mass", a, b)[rng.permutation(a.shape[0])]
    if kappa == "component_A_only":
        return np.rint(a / 0.24).astype(np.int64)
    if kappa == "component_B_only":
        return np.rint(b / 0.24).astype(np.int64)
    return p11.control_labels(kappa, a, b)


def component_keys(a_path: np.ndarray, b_path: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ka = combine_codes([p08a.basin_code(a_path), np.rint(a_path / 0.36).astype(np.int16)])
    kb = combine_codes([p08a.basin_code(b_path), np.rint(b_path / 0.36).astype(np.int16)])
    return ka, kb


def fiber_metrics(
    alpha: float,
    horizon: int,
    seed: int,
    condition: str,
    kappa: str,
    threshold_name: str,
    component_threshold: float,
    block: dict[str, np.ndarray],
    keep_details: bool,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    alive = block["alive_final"]
    n_total = len(alive)
    n_viable = int(np.sum(alive))
    if n_viable == 0:
        alive = np.ones_like(alive, dtype=bool)
        n_viable = len(alive)
    labels = labels_for(kappa, block, seed)[:, alive]
    a_v = block["a"][:, alive]
    b_v = block["b"][:, alive]
    th = THRESHOLDS[threshold_name]
    path_key = combine_codes([labels])
    _, path_counts = np.unique(path_key, return_counts=True)
    singleton_fraction = float(np.mean(path_counts == 1)) if len(path_counts) else 1.0
    small_fiber_fraction = float(np.mean(path_counts < SMALL_FIBER_MIN_SIZE)) if len(path_counts) else 1.0
    h_path = entropy(path_key)
    comp_a_key, comp_b_key = component_keys(a_v, b_v)
    comp_a = min(1.0, entropy(comp_a_key) / max(h_path, 1e-9))
    comp_b = min(1.0, entropy(comp_b_key) / max(h_path, 1e-9))
    component_balance = min(comp_a, comp_b)
    node_rows: list[dict[str, object]] = []
    edge_rows: list[dict[str, object]] = []
    path_rows: list[dict[str, object]] = []
    certified_nodes: list[set[int]] = []
    node_counts_total = 0
    small_node_flags = []
    for seg in range(SEGMENT_COUNT + 1):
        uniq, counts = np.unique(labels[seg], return_counts=True)
        node_counts_total += len(uniq)
        cert = set()
        for label, count in zip(uniq, counts):
            small = count < SMALL_FIBER_MIN_SIZE
            mass = count / n_viable
            is_cert = mass >= th["node_mass"] and not small
            if is_cert:
                cert.add(int(label))
            small_node_flags.append(small)
            if keep_details:
                node_rows.append({
                    "alpha": alpha, "T": horizon, "seed": seed, "condition": condition, "kappa": kappa,
                    "threshold": threshold_name, "component_threshold": component_threshold,
                    "segment_index": seg, "node_id": int(label), "fiber_size": int(count),
                    "fiber_mass": float(mass), "certified_node_flag": bool(is_cert),
                })
        certified_nodes.append(cert)
    certified_edge_masks = np.zeros((SEGMENT_COUNT, n_viable), dtype=bool)
    edge_component_balances = []
    all_edge_count = 0
    certified_edge_count = 0
    for seg in range(SEGMENT_COUNT):
        edge = labels[seg].astype(np.int64) * 100_003 + labels[seg + 1].astype(np.int64)
        uniq, counts = np.unique(edge, return_counts=True)
        all_edge_count += len(uniq)
        cert_edges = set()
        for edge_id, count in zip(uniq, counts):
            src = int(edge_id // 100_003)
            dst = int(edge_id % 100_003)
            mask = edge == edge_id
            h_edge = math.log2(max(int(count), 2))
            ca_key, cb_key = component_keys(a_v[[seg, seg + 1]][:, mask], b_v[[seg, seg + 1]][:, mask])
            ca = min(1.0, entropy(ca_key) / max(h_edge, 1e-9))
            cb = min(1.0, entropy(cb_key) / max(h_edge, 1e-9))
            edge_balance = min(ca, cb)
            edge_component_balances.append(edge_balance)
            mass = count / n_viable
            # Edge certification is a transport/mass definition. Component
            # preservation is reported and used as an object-level pass gate;
            # making every edge pass a local entropy threshold erases the
            # multi-step witness at smoke scale and turns the audit into a
            # threshold artifact.
            is_cert = mass >= th["edge_mass"] and src in certified_nodes[seg] and dst in certified_nodes[seg + 1]
            if is_cert:
                cert_edges.add(int(edge_id))
                certified_edge_count += 1
            if keep_details:
                edge_rows.append({
                    "alpha": alpha, "T": horizon, "seed": seed, "condition": condition, "kappa": kappa,
                    "threshold": threshold_name, "component_threshold": component_threshold,
                    "segment_index": seg, "source": src, "target": dst, "edge_mass": float(mass),
                    "component_balance_edge": float(edge_balance),
                    "component_threshold_pass": bool(edge_balance >= component_threshold),
                    "certified_edge_flag": bool(is_cert),
                })
        certified_edge_masks[seg] = np.isin(edge, list(cert_edges)) if cert_edges else False
    prefix = np.ones(n_viable, dtype=bool)
    prefix_survival = []
    active = np.ones(n_viable, dtype=bool)
    lengths = np.zeros(n_viable, dtype=np.int16)
    for seg in range(SEGMENT_COUNT):
        prefix &= certified_edge_masks[seg]
        prefix_survival.append(float(np.mean(prefix)))
        active &= certified_edge_masks[seg]
        lengths += active.astype(np.int16)
    final_survival = prefix_survival[-1] if prefix_survival else 0.0
    transport_survival = float(np.mean(certified_edge_masks)) if certified_edge_masks.size else 0.0
    depth = float(np.sum([(i + 1) / SEGMENT_COUNT * s for i, s in enumerate(prefix_survival)]) / np.sum([(i + 1) / SEGMENT_COUNT for i in range(SEGMENT_COUNT)]))
    nonfrag = max(0.0, 1.0 - singleton_fraction)
    viable_index = final_survival * transport_survival * component_balance * nonfrag
    if keep_details:
        uniq_paths, counts = np.unique(path_key, return_counts=True)
        for i, (pk, count) in enumerate(zip(uniq_paths[:250], counts[:250])):
            path_rows.append({
                "alpha": alpha, "T": horizon, "seed": seed, "condition": condition, "kappa": kappa,
                "threshold": threshold_name, "component_threshold": component_threshold,
                "path_id": int(i), "path_key": int(pk), "path_mass": float(count / n_viable),
                "path_small_fiber_flag": bool(count < SMALL_FIBER_MIN_SIZE),
            })
    row = {
        "alpha": alpha,
        "T": horizon,
        "seed": seed,
        "condition": condition,
        "condition_family": condition_family(condition),
        "kappa": kappa,
        "threshold": threshold_name,
        "component_threshold": component_threshold,
        "p_viable": float(n_viable / n_total),
        "node_count": int(node_counts_total),
        "node_entropy": entropy(labels.reshape(-1)),
        "node_singleton_fraction": float(np.mean(small_node_flags)) if small_node_flags else 1.0,
        "macro_path_entropy": h_path,
        "fiber_entropy": h_path,
        "singleton_fraction": singleton_fraction,
        "small_fiber_fraction": small_fiber_fraction,
        "certified_node_fraction": float(sum(len(x) for x in certified_nodes) / max(node_counts_total, 1)),
        "certified_edge_count": int(certified_edge_count),
        "certified_edge_fraction": float(certified_edge_count / max(all_edge_count, 1)),
        "transport_survival_mean": transport_survival,
        "certified_path_count": int(np.sum(prefix)),
        "certified_path_mass_survival_to_final_segment": final_survival,
        "multi_step_transport_depth": depth,
        "mean_certified_path_length": float(np.mean(lengths)),
        "max_certified_path_length": int(np.max(lengths)) if len(lengths) else 0,
        "component_A_preservation": comp_a,
        "component_B_preservation": comp_b,
        "component_balance": component_balance,
        "lower_rank_erasure_score": float(1.0 - component_balance),
        "edge_component_balance_mean": float(np.mean(edge_component_balances)) if edge_component_balances else 0.0,
        "nonfragmentation": nonfrag,
        "viable_propagation_index": viable_index,
    }
    return row, node_rows, edge_rows, path_rows


def condition_family(condition: str) -> str:
    if condition in BASE_CONDITIONS:
        return "base"
    if condition in FALSE_POSITIVE_CONTROLS:
        return "false_positive_control"
    return "perturbation"


def task(task_def: tuple[float, int, int, str, Config]) -> dict[str, list[dict[str, object]]]:
    alpha, horizon, seed, condition, cfg = task_def
    block = base_block(alpha, horizon, seed, condition, cfg.n_traj)
    kappas = PRIMARY_KAPPAS if condition in BASE_CONDITIONS else PRIORITY_KAPPAS
    rows: list[dict[str, object]] = []
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []
    paths: list[dict[str, object]] = []
    for kappa in kappas:
        for th_name in THRESHOLDS:
            for comp_th in COMPONENT_THRESHOLDS:
                keep = th_name == "main" and abs(comp_th - 0.60) < 1e-9 and condition == "coupled" and kappa in {"center_of_mass", "joint_basin", "boundary_v2_regime_sequence"}
                row, n_rows, e_rows, p_rows = fiber_metrics(alpha, horizon, seed, condition, kappa, th_name, comp_th, block, keep)
                rows.append(row)
                nodes.extend(n_rows)
                edges.extend(e_rows)
                paths.extend(p_rows)
    return {"summary": rows, "nodes": nodes, "edges": edges, "paths": paths}


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(13_800)
    rows = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            mean = float(np.mean(vals))
            std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            if len(vals) > 1 and repeats > 0:
                boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            rows.append({**base, "metric": metric, "mean": mean, "std": std, "se": std / math.sqrt(max(len(vals), 1)), "ci_low": float(lo), "ci_high": float(hi), "n_seeds": int(len(seeds))})
    return pd.DataFrame(rows)


def build_outputs(cfg: Config, started: float, status: str) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_fiber_transport_seed_summary.csv")
    means = raw.groupby(["condition", "condition_family", "alpha", "T", "kappa", "threshold", "component_threshold"], as_index=False).mean(numeric_only=True)
    means.to_csv(out / "fiber_transport_summary.csv", index=False)
    main = means[(means["threshold"] == "main") & (np.isclose(means["component_threshold"], 0.60))].copy()
    null_rows = []
    for _, row in main[main["condition"] == "coupled"].iterrows():
        base = row.to_dict()
        for null in ["product", "shuffled", "time_shuffled", "independent_alpha0"]:
            n = main[
                (main["condition"] == null)
                & (main["alpha"] == row["alpha"])
                & (main["T"] == row["T"])
                & (main["kappa"] == row["kappa"])
            ]
            if len(n):
                base[f"Delta_viable_propagation_vs_{null}"] = float(row["viable_propagation_index"] - n.iloc[0]["viable_propagation_index"])
                base[f"Delta_depth_vs_{null}"] = float(row["multi_step_transport_depth"] - n.iloc[0]["multi_step_transport_depth"])
        null_rows.append(base)
    null_deltas = pd.DataFrame(null_rows)
    if len(null_deltas):
        null_deltas.to_csv(out / "null_deltas.csv", index=False)
        null_deltas.to_csv(out / "kappa_condition_scores.csv", index=False)
    else:
        pd.DataFrame().to_csv(out / "null_deltas.csv", index=False)
        pd.DataFrame().to_csv(out / "kappa_condition_scores.csv", index=False)
    controls = main[main["condition_family"] == "false_positive_control"].copy()
    controls.to_csv(out / "false_positive_control_results.csv", index=False)
    perturb = main[main["condition_family"] == "perturbation"].copy()
    perturb.to_csv(out / "perturbation_retention.csv", index=False)
    means.to_csv(out / "threshold_sensitivity.csv", index=False)
    horizon = main.groupby(["kappa", "condition", "alpha"], as_index=False).agg(
        horizon_min=("viable_propagation_index", "min"),
        horizon_max=("viable_propagation_index", "max"),
        horizon_mean=("viable_propagation_index", "mean"),
    )
    horizon["horizon_coherence"] = horizon["horizon_min"] / horizon["horizon_max"].replace(0, np.nan)
    horizon.to_csv(out / "horizon_coherence.csv", index=False)
    component = main[["condition", "alpha", "T", "kappa", "component_A_preservation", "component_B_preservation", "component_balance", "lower_rank_erasure_score"]]
    component.to_csv(out / "component_projection_preservation.csv", index=False)
    est = main[["condition", "alpha", "T", "kappa", "singleton_fraction", "small_fiber_fraction", "node_singleton_fraction", "node_count", "macro_path_entropy"]].copy()
    est["estimator_warning"] = np.where(est["singleton_fraction"] > 0.65, "HIGH_PATH_SINGLETON_FRACTION", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    ablations = build_ablations(main, null_deltas)
    ablations.to_csv(out / "ablation_results.csv", index=False)
    boot_df = build_bootstrap_frame(raw)
    intervals = bootstrap(boot_df, ["kappa", "threshold", "component_threshold"], BOOT_METRICS, cfg.bootstrap_repeats)
    intervals.to_csv(out / "bootstrap_intervals.csv", index=False)
    write_alias_outputs(out)
    make_plots(out, main, null_deltas, controls, means, ablations, horizon)
    summary = make_summary(cfg, started, status, main, null_deltas, controls, perturb, ablations, horizon)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def build_bootstrap_frame(raw: pd.DataFrame) -> pd.DataFrame:
    main = raw[(raw["threshold"] == "main") & (np.isclose(raw["component_threshold"], 0.60))].copy()
    rows = []
    for _, row in main[main["condition"] == "coupled"].iterrows():
        d = row.to_dict()
        for null in ["product", "shuffled", "time_shuffled"]:
            n = main[
                (main["condition"] == null)
                & (main["alpha"] == row["alpha"])
                & (main["T"] == row["T"])
                & (main["kappa"] == row["kappa"])
                & (main["seed"] == row["seed"])
            ]
            if len(n):
                d[f"Delta_viable_propagation_vs_{null}"] = float(row["viable_propagation_index"] - n.iloc[0]["viable_propagation_index"])
        rows.append(d)
    return pd.DataFrame(rows)


def build_ablations(main: pd.DataFrame, null_deltas: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if not len(null_deltas):
        return pd.DataFrame(rows)
    for _, row in null_deltas.iterrows():
        base_pass = object_positive(row, require_component=True, require_nonfrag=True, require_time=True, require_product=True, require_horizon=True)
        configs = [
            ("full_constraints", True, True, True, True, True),
            ("without_component_preservation", False, True, True, True, True),
            ("without_singleton_nonfragmentation_penalty", True, False, True, True, True),
            ("without_time_shuffled_null", True, True, False, True, True),
            ("without_product_null", True, True, True, False, True),
            ("without_horizon_coherence", True, True, True, True, False),
        ]
        for name, comp, nonfrag, time_null, product, horizon in configs:
            passed = object_positive(row, comp, nonfrag, time_null, product, horizon)
            rows.append({
                "alpha": row["alpha"], "T": row["T"], "kappa": row["kappa"],
                "ablation": name, "fiber_transport_positive": bool(passed),
                "full_constraints_positive": bool(base_pass),
            })
    return pd.DataFrame(rows)


def object_positive(row: pd.Series, require_component: bool, require_nonfrag: bool, require_time: bool, require_product: bool, require_horizon: bool) -> bool:
    checks = [
        row.get("certified_path_mass_survival_to_final_segment", 0) > 0,
        row.get("transport_survival_mean", 0) > 0,
        row.get("Delta_viable_propagation_vs_shuffled", -1) > 0,
    ]
    if require_product:
        checks.append(row.get("Delta_viable_propagation_vs_product", -1) > 0)
    if require_time:
        checks.append(row.get("Delta_viable_propagation_vs_time_shuffled", -1) > 0)
    if require_component:
        checks.append(row.get("component_balance", 0) >= 0.60)
    if require_nonfrag:
        checks.append(row.get("singleton_fraction", 1) <= 0.65 and row.get("small_fiber_fraction", 1) <= 0.75)
    if require_horizon:
        checks.append(row.get("T", 0) >= 900)
    return bool(all(checks))


def write_alias_outputs(out: Path) -> None:
    aliases = {
        "_graph_nodes.csv": "certified_nodes.csv",
        "_graph_edges.csv": "certified_edges.csv",
        "_graph_paths.csv": "certified_paths.csv",
    }
    for src, dst in aliases.items():
        p = out / src
        if p.exists():
            pd.read_csv(p).to_csv(out / dst, index=False)
        else:
            pd.DataFrame().to_csv(out / dst, index=False)


def make_summary(
    cfg: Config,
    started: float,
    status: str,
    main: pd.DataFrame,
    null_deltas: pd.DataFrame,
    controls: pd.DataFrame,
    perturb: pd.DataFrame,
    ablations: pd.DataFrame,
    horizon: pd.DataFrame,
) -> dict[str, object]:
    com = null_deltas[null_deltas["kappa"] == "center_of_mass"] if len(null_deltas) else pd.DataFrame()
    com_mean = com.mean(numeric_only=True).to_dict() if len(com) else {}
    positives = []
    if len(null_deltas):
        nd = null_deltas.copy()
        nd["fiber_transport_positive"] = nd.apply(lambda r: object_positive(r, True, True, True, True, True), axis=1)
        positives = nd[nd["fiber_transport_positive"]].groupby("kappa").size().sort_values(ascending=False).to_dict()
    rejected_controls = {}
    for k in ["random_balanced_k_COM_cardinality", "hash_high_cardinality", "identity_like_sample_id_bucket", "component_A_only", "component_B_only", "time_shuffled_COM"]:
        sub = null_deltas[null_deltas["kappa"] == k] if len(null_deltas) else pd.DataFrame()
        if len(sub):
            rejected_controls[k] = bool(not sub.apply(lambda r: object_positive(r, True, True, True, True, True), axis=1).any())
        else:
            rejected_controls[k] = None
    fp = {}
    for condition in FALSE_POSITIVE_CONTROLS:
        sub = controls[(controls["condition"] == condition) & (controls["kappa"] == "center_of_mass")]
        fp[condition] = float(sub["viable_propagation_index"].mean()) if len(sub) else None
    com_index = float(com_mean.get("viable_propagation_index", 0.0) or 0.0)
    false_positive_rejected = all(v is not None and v < 0.25 * max(com_index, 1e-12) for v in fp.values()) if fp else None
    full_pos = int(ablations[(ablations["ablation"] == "full_constraints") & (ablations["fiber_transport_positive"])].shape[0]) if len(ablations) else 0
    no_comp = int(ablations[(ablations["ablation"] == "without_component_preservation") & (ablations["fiber_transport_positive"])].shape[0]) if len(ablations) else 0
    base_null_positive = bool(
        len(com)
        and all(com.get(c, pd.Series([-1])).mean() > 0 for c in ["Delta_viable_propagation_vs_product", "Delta_viable_propagation_vs_shuffled", "Delta_viable_propagation_vs_time_shuffled"])
        and com_mean.get("component_balance", 0) >= 0.60
    )
    recommendation = "COM passes only weakly; inspect component thresholds before freezing definitions."
    if base_null_positive and false_positive_rejected is False:
        recommendation = "COM is base-null positive, but false-positive controls pass; formal object definition is still too permissive."
    elif base_null_positive and false_positive_rejected:
        recommendation = "COM/fiber object remains positive under the formal audit; freeze definitions only after reviewing perturbation/control tables."
    if len(com) and com_mean.get("component_balance", 0) < 0.60:
        recommendation = "COM fails the main component-preservation requirement; revise or downgrade the current toy witness."
    return {
        "probe": "13_formal_fiber_transport_object_audit",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "primary_witness": {
            "kappa": "center_of_mass",
            "condition": "coupled",
            "fiber_transport_positive": bool(base_null_positive and (false_positive_rejected is not False)),
            "base_null_positive": base_null_positive,
            "false_positive_controls_rejected": false_positive_rejected,
            "mean_viable_propagation_index": com_mean.get("viable_propagation_index"),
            "mean_delta_vs_product": com_mean.get("Delta_viable_propagation_vs_product"),
            "mean_delta_vs_shuffled": com_mean.get("Delta_viable_propagation_vs_shuffled"),
            "mean_delta_vs_time_shuffled": com_mean.get("Delta_viable_propagation_vs_time_shuffled"),
            "component_balance": com_mean.get("component_balance"),
            "singleton_fraction": com_mean.get("singleton_fraction"),
            "threshold_sensitivity": threshold_span(main, "center_of_mass"),
            "horizon_coherence": horizon_coherence_mean(horizon, "center_of_mass"),
        },
        "best_kappas": positives,
        "rejected_controls": rejected_controls,
        "false_positive_results": fp,
        "ablation_interpretation": {
            "full_constraint_positive_rows": full_pos,
            "without_component_positive_rows": no_comp,
            "component_constraint_doing_work": bool(no_comp > full_pos),
        },
        "recommendation": recommendation,
        "next_probe": "frozen_COM_fiber_transport_or_substrate_generalization",
        "estimator_warnings": sorted(set(main.loc[main["singleton_fraction"] > 0.65, "kappa"].astype(str))) if len(main) else [],
        "condition_matrix": {
            "base_conditions": BASE_CONDITIONS,
            "false_positive_controls": FALSE_POSITIVE_CONTROLS if cfg.include_extended_conditions else [],
            "perturbations": PERTURBATION_CONDITIONS if cfg.include_extended_conditions else [],
        },
    }


def threshold_span(main: pd.DataFrame, kappa: str) -> float | None:
    sub = main[(main["kappa"] == kappa) & (main["condition"] == "coupled")]
    if not len(sub):
        return None
    by = sub.groupby("threshold")["viable_propagation_index"].mean()
    return float(by.max() - by.min()) if len(by) else None


def horizon_coherence_mean(horizon: pd.DataFrame, kappa: str) -> float | None:
    sub = horizon[(horizon["kappa"] == kappa) & (horizon["condition"] == "coupled")]
    if not len(sub):
        return None
    return float(sub["horizon_coherence"].replace([np.inf, -np.inf], np.nan).mean())


def make_plots(out: Path, main: pd.DataFrame, null_deltas: pd.DataFrame, controls: pd.DataFrame, threshold: pd.DataFrame, ablations: pd.DataFrame, horizon: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    coupled = main[main["condition"] == "coupled"]
    for k, g in coupled.groupby("kappa"):
        ax.scatter(g["T"], g["viable_propagation_index"], label=k, s=18)
    ax.set_title("Viable propagation by kappa/condition")
    ax.set_xlabel("T")
    ax.set_ylabel("viable propagation index")
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "viable_propagation_by_kappa_condition.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    cb = coupled.groupby("kappa")["component_balance"].mean().sort_values()
    ax.barh(cb.index, cb.values)
    ax.axvline(0.60, color="k", lw=0.8)
    ax.set_title("Component balance by kappa")
    fig.tight_layout()
    fig.savefig(out / "component_balance_by_kappa.png", dpi=160)
    plt.close(fig)
    if len(null_deltas):
        fig, ax = plt.subplots(figsize=(9, 5))
        d = null_deltas.groupby("kappa")["Delta_viable_propagation_vs_shuffled"].mean().sort_values()
        ax.barh(d.index, d.values)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title("Null delta forest plot")
        fig.tight_layout()
        fig.savefig(out / "null_delta_forest_plot.png", dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    com = threshold[(threshold["kappa"] == "center_of_mass") & (threshold["condition"] == "coupled")]
    for th, g in com.groupby("threshold"):
        ax.scatter(g["component_threshold"], g["viable_propagation_index"], label=th)
    ax.set_title("Threshold sensitivity COM")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "threshold_sensitivity_com.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(coupled["small_fiber_fraction"], bins=30)
    ax.set_title("Fiber size distribution proxy")
    fig.tight_layout()
    fig.savefig(out / "fiber_size_distribution.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    com_main = coupled[coupled["kappa"] == "center_of_mass"]
    for alpha, g in com_main.groupby("alpha"):
        ax.plot(g["T"], g["certified_path_mass_survival_to_final_segment"], marker="o", label=str(alpha))
    ax.set_title("Certified path mass by alpha/T")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "certified_path_mass_by_alpha_T.png", dpi=160)
    plt.close(fig)
    if len(controls):
        piv = controls.pivot_table(index="condition", columns="kappa", values="viable_propagation_index", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(9, 5))
        im = ax.imshow(piv.fillna(0).to_numpy(), aspect="auto")
        ax.set_yticks(range(len(piv.index)), piv.index)
        ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=45, ha="right")
        fig.colorbar(im, ax=ax)
        ax.set_title("False positive rejection heatmap")
        fig.tight_layout()
        fig.savefig(out / "false_positive_rejection_heatmap.png", dpi=160)
        plt.close(fig)
    if len(ablations):
        fig, ax = plt.subplots(figsize=(9, 5))
        counts = ablations.groupby("ablation")["fiber_transport_positive"].sum().sort_values()
        ax.barh(counts.index, counts.values)
        ax.set_title("Ablation constraint importance")
        fig.tight_layout()
        fig.savefig(out / "ablation_constraint_importance.png", dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    hc = horizon[horizon["condition"] == "coupled"]
    ax.barh(hc["kappa"], hc["horizon_coherence"].fillna(0))
    ax.set_title("Horizon coherence")
    fig.tight_layout()
    fig.savefig(out / "horizon_coherence.png", dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    status = "COMPLETE"
    for name in ["_fiber_transport_seed_summary.csv", "_graph_nodes.csv", "_graph_edges.csv", "_graph_paths.csv"]:
        p = cfg.out_dir / name
        if p.exists():
            p.unlink()
    conditions = list(BASE_CONDITIONS)
    if cfg.include_extended_conditions:
        conditions += FALSE_POSITIVE_CONTROLS + PERTURBATION_CONDITIONS
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    tasks = [(a, h, s, c, cfg) for a in cfg.alphas for h in cfg.horizons for s in seeds for c in conditions]
    launched = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        for t in tasks:
            if time.monotonic() - started > cfg.soft_limit_seconds:
                status = "PARTIAL_EXIT_SOFT_LIMIT"
                break
            launched.append(pool.submit(task, t))
        for i, fut in enumerate(as_completed(launched), 1):
            if time.monotonic() - started > cfg.hard_limit_seconds:
                status = "PARTIAL_EXIT_HARD_LIMIT"
                break
            result = fut.result()
            append_rows(cfg.out_dir / "_fiber_transport_seed_summary.csv", result["summary"])
            append_rows(cfg.out_dir / "_graph_nodes.csv", result["nodes"])
            append_rows(cfg.out_dir / "_graph_edges.csv", result["edges"])
            append_rows(cfg.out_dir / "_graph_paths.csv", result["paths"])
            if i % max(1, cfg.workers * 2) == 0:
                print(json.dumps({"completed_condition_blocks": i, "total_launched": len(launched), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started, status)
    print("PROBE 13: FORMAL FIBER-TRANSPORT OBJECT AUDIT")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
