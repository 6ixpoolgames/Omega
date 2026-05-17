#!/usr/bin/env python
"""Probe 13b: fiber-transport false-positive refinement.

This probe tests four minimal refinements forced by Probe 13 smoke failures:
component necessity, temporal edge-order integrity, within-fiber
nondegeneracy, and late-horizon transport retention.
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

import probe_13_formal_fiber_transport_object_audit as p13


SEGMENT_COUNT = p13.SEGMENT_COUNT
THRESHOLD = "main"
COMPONENT_THRESHOLD = 0.60
BASE_CONDITIONS = ["coupled", "product", "shuffled", "time_shuffled", "independent_alpha0"]
PRIORITY_FALSE_POSITIVES = [
    "endpoint_fakeout",
    "rigid_collapse",
    "delayed_trap",
]
SECONDARY_FALSE_POSITIVES = [
    "noise_fakeout",
    "component_swap_fakeout",
]
KAPPAS = [
    "center_of_mass",
    "component_A_only",
    "component_B_only",
    "time_shuffled_COM",
    "random_balanced_k_COM_cardinality",
    "hash_high_cardinality",
    "joint_basin",
    "boundary_v2_regime_sequence",
    "basin_transition_profile",
]
BOOT_METRICS = [
    "component_necessity_min",
    "edge_order_integrity",
    "within_fiber_nondegeneracy",
    "late_horizon_retention",
    "refined_positive",
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
    smoke: bool
    include_optional_kappas: bool
    include_secondary_false_positives: bool


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_13b_fiber_transport_false_positive_refinement_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "10000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "160")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "500")))
    p.add_argument("--alphas", type=parse_csv_floats, default=parse_csv_floats(os.environ.get("OMEGA_ALPHAS", "0.45,0.50,0.525")))
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "900,1500,2400")))
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--optional-kappas", action="store_true")
    p.add_argument("--secondary-false-positives", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 6)
        args.n_traj = min(args.n_traj, 1000)
        args.seed_count = min(args.seed_count, 8)
        args.bootstrap_repeats = min(args.bootstrap_repeats, 50)
        args.alphas = [0.50]
        args.horizons = [900]
        args.secondary_false_positives = True
        args.optional_kappas = True
    return Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seed_count=args.seed_count,
        seed_start=args.seed_start,
        bootstrap_repeats=args.bootstrap_repeats,
        alphas=args.alphas,
        horizons=sorted(args.horizons),
        smoke=args.smoke,
        include_optional_kappas=args.optional_kappas,
        include_secondary_false_positives=args.secondary_false_positives,
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


def fiber_state(alpha: float, horizon: int, seed: int, condition: str, kappa: str, cfg: Config) -> dict[str, object]:
    block = p13.base_block(alpha, horizon, seed, condition, cfg.n_traj)
    row, _, _, _ = p13.fiber_metrics(alpha, horizon, seed, condition, kappa, THRESHOLD, COMPONENT_THRESHOLD, block, False)
    alive = block["alive_final"]
    if not np.any(alive):
        alive = np.ones_like(alive, dtype=bool)
    labels = p13.labels_for(kappa, block, seed)[:, alive]
    a_v = block["a"][:, alive]
    b_v = block["b"][:, alive]
    return {"row": row, "labels": labels, "a": a_v, "b": b_v}


def certified_edge_masks(labels: np.ndarray, n_viable: int) -> np.ndarray:
    th = p13.THRESHOLDS[THRESHOLD]
    certified_nodes: list[set[int]] = []
    for seg in range(SEGMENT_COUNT + 1):
        uniq, counts = np.unique(labels[seg], return_counts=True)
        certified_nodes.append({int(u) for u, c in zip(uniq, counts) if c / n_viable >= th["node_mass"] and c >= p13.SMALL_FIBER_MIN_SIZE})
    masks = np.zeros((SEGMENT_COUNT, n_viable), dtype=bool)
    for seg in range(SEGMENT_COUNT):
        edge = labels[seg].astype(np.int64) * 100_003 + labels[seg + 1].astype(np.int64)
        uniq, counts = np.unique(edge, return_counts=True)
        cert = []
        for e, c in zip(uniq, counts):
            src = int(e // 100_003)
            dst = int(e % 100_003)
            if c / n_viable >= th["edge_mass"] and src in certified_nodes[seg] and dst in certified_nodes[seg + 1]:
                cert.append(int(e))
        masks[seg] = np.isin(edge, cert) if cert else False
    return masks


def edge_predictivity(labels: np.ndarray) -> float:
    vals = []
    for seg in range(SEGMENT_COUNT):
        src = labels[seg]
        dst = labels[seg + 1]
        for s in np.unique(src):
            mask = src == s
            if np.sum(mask) < 3:
                continue
            _, counts = np.unique(dst[mask], return_counts=True)
            vals.append(float(np.max(counts) / np.sum(counts)))
    return float(np.mean(vals)) if vals else 0.0


def within_fiber_diversity(labels: np.ndarray, a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    path = path_keys(labels)
    a_vals = []
    b_vals = []
    radii = []
    global_a = float(np.var(a)) + 1e-12
    global_b = float(np.var(b)) + 1e-12
    global_radius = float(np.var(np.stack([a, b], axis=2).reshape(len(a), -1))) + 1e-12
    for pk in np.unique(path):
        mask = path == pk
        if np.sum(mask) < p13.SMALL_FIBER_MIN_SIZE:
            continue
        aa = a[:, mask]
        bb = b[:, mask]
        a_vals.append(float(np.var(aa) / global_a))
        b_vals.append(float(np.var(bb) / global_b))
        both = np.stack([aa, bb], axis=2).reshape(aa.shape[1], -1)
        radii.append(float(np.var(both) / global_radius))
    a_div = float(np.median(a_vals)) if a_vals else 0.0
    b_div = float(np.median(b_vals)) if b_vals else 0.0
    radius = float(np.median(radii)) if radii else 0.0
    return {
        "within_fiber_A_diversity": a_div,
        "within_fiber_B_diversity": b_div,
        "within_fiber_component_balance": min(a_div, b_div),
        "within_fiber_effective_radius": radius,
    }


def path_keys(labels: np.ndarray) -> np.ndarray:
    out = np.zeros(labels.shape[1], dtype=np.int64)
    for seg in range(labels.shape[0]):
        out = out * 4099 + (labels[seg].astype(np.int64) + 2049)
    return out


def late_retention(labels: np.ndarray) -> dict[str, float]:
    n = labels.shape[1]
    masks = certified_edge_masks(labels, n)
    edge_survival = masks.mean(axis=1)
    early = float(np.mean(edge_survival[:2]))
    middle = float(np.mean(edge_survival[2:4]))
    late = float(np.mean(edge_survival[4:]))
    return {
        "early_edge_survival": early,
        "middle_edge_survival": middle,
        "late_edge_survival": late,
        "late_to_early_transport_ratio": float(late / max(early, 1e-12)),
        "final_segment_certified_mass": float(edge_survival[-1]) if len(edge_survival) else 0.0,
    }


def task(task_def: tuple[float, int, int, Config]) -> list[dict[str, object]]:
    alpha, horizon, seed, cfg = task_def
    conditions = list(BASE_CONDITIONS) + PRIORITY_FALSE_POSITIVES
    if cfg.include_secondary_false_positives:
        conditions += SECONDARY_FALSE_POSITIVES
    kappas = KAPPAS if cfg.include_optional_kappas else KAPPAS[:6]
    states: dict[tuple[str, str], dict[str, object]] = {}
    rows = []
    for condition in conditions:
        for kappa in kappas:
            states[(condition, kappa)] = fiber_state(alpha, horizon, seed, condition, kappa, cfg)
    ref = states[("coupled", "center_of_mass")]
    product = states[("product", "center_of_mass")]["row"]["viable_propagation_index"]
    shuffled = states[("shuffled", "center_of_mass")]["row"]["viable_propagation_index"]
    time_shuffled = states[("time_shuffled", "center_of_mass")]["row"]["viable_propagation_index"]
    endpoint = states[("endpoint_fakeout", "center_of_mass")]
    rigid = states[("rigid_collapse", "center_of_mass")]
    delayed = states[("delayed_trap", "center_of_mass")]
    full_vpi = float(ref["row"]["viable_propagation_index"])
    a_only_vpi = float(states[("coupled", "component_A_only")]["row"]["viable_propagation_index"])
    b_only_vpi = float(states[("coupled", "component_B_only")]["row"]["viable_propagation_index"])
    edge_real = edge_predictivity(ref["labels"])
    edge_time = edge_predictivity(states[("time_shuffled", "center_of_mass")]["labels"])
    edge_endpoint = edge_predictivity(endpoint["labels"])
    div_real = within_fiber_diversity(ref["labels"], ref["a"], ref["b"])
    div_rigid = within_fiber_diversity(rigid["labels"], rigid["a"], rigid["b"])
    late_real = late_retention(ref["labels"])
    late_delayed = late_retention(delayed["labels"])
    ref_row = {
        "alpha": alpha,
        "T": horizon,
        "seed": seed,
        "condition": "coupled",
        "kappa": "center_of_mass",
        **ref["row"],
        "delta_vs_product": full_vpi - float(product),
        "delta_vs_shuffled": full_vpi - float(shuffled),
        "delta_vs_time_shuffled": full_vpi - float(time_shuffled),
        "component_necessity_A": full_vpi - b_only_vpi,
        "component_necessity_B": full_vpi - a_only_vpi,
        "component_necessity_min": min(full_vpi - b_only_vpi, full_vpi - a_only_vpi),
        "ordered_edge_predictivity": edge_real,
        "edge_order_delta_vs_time_shuffled": edge_real - edge_time,
        "edge_order_delta_vs_endpoint_fakeout": edge_real - edge_endpoint,
        "local_edge_survival_min": float(np.min(certified_edge_masks(ref["labels"], ref["labels"].shape[1]).mean(axis=1))),
        "edge_transition_consistency": edge_real,
        **div_real,
        "rigid_collapse_diversity_delta": div_real["within_fiber_component_balance"] - div_rigid["within_fiber_component_balance"],
        **late_real,
        "delayed_trap_late_delta": late_real["late_edge_survival"] - late_delayed["late_edge_survival"],
    }
    ref_row.update(pass_flags(ref_row))
    rows.append(ref_row)
    for condition in conditions:
        for kappa in kappas:
            st = states[(condition, kappa)]
            row = {
                "alpha": alpha,
                "T": horizon,
                "seed": seed,
                "condition": condition,
                "kappa": kappa,
                **st["row"],
            }
            row["base_signal_positive"] = bool(row["viable_propagation_index"] > 0)
            rows.append(row)
    return rows


def pass_flags(row: dict[str, object]) -> dict[str, object]:
    base = (
        row["viable_propagation_index"] > 0
        and row["delta_vs_product"] > 0
        and row["delta_vs_shuffled"] > 0
        and row["delta_vs_time_shuffled"] > 0
        and row["component_balance"] >= 0.60
        and row["singleton_fraction"] <= 0.65
    )
    r1 = row["component_necessity_min"] > 0
    r2 = row["edge_order_delta_vs_time_shuffled"] > 0 and row["edge_order_delta_vs_endpoint_fakeout"] > 0 and row["local_edge_survival_min"] > 0
    r3 = row["rigid_collapse_diversity_delta"] > 0 and row["within_fiber_component_balance"] > 0
    r4 = row["late_to_early_transport_ratio"] >= 0.50 and row["delayed_trap_late_delta"] > 0
    return {
        "base_signal_positive": bool(base),
        "R1_component_necessity_pass": bool(r1),
        "R2_edge_order_pass": bool(r2),
        "R3_nondegeneracy_pass": bool(r3),
        "R4_late_retention_pass": bool(r4),
        "refined_positive": bool(base and r1 and r2 and r3 and r4),
    }


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(13_980)
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
    raw = pd.read_csv(out / "_seed_refinement_rows.csv")
    refined = raw[(raw["condition"] == "coupled") & (raw["kappa"] == "center_of_mass") & raw["refined_positive"].notna()].copy()
    refined["edge_order_integrity"] = refined["edge_order_delta_vs_time_shuffled"]
    refined["within_fiber_nondegeneracy"] = refined["rigid_collapse_diversity_delta"]
    refined["late_horizon_retention"] = refined["late_to_early_transport_ratio"]
    summary_df = raw.groupby(["condition", "kappa", "alpha", "T"], as_index=False).mean(numeric_only=True)
    refined_mean = refined.groupby(["alpha", "T"], as_index=False).mean(numeric_only=True)
    summary_df.to_csv(out / "refined_fiber_transport_summary.csv", index=False)
    refined[["alpha", "T", "seed", "component_necessity_A", "component_necessity_B", "component_necessity_min"]].to_csv(out / "component_necessity_results.csv", index=False)
    refined[["alpha", "T", "seed", "ordered_edge_predictivity", "edge_order_delta_vs_time_shuffled", "edge_order_delta_vs_endpoint_fakeout", "local_edge_survival_min", "edge_transition_consistency"]].to_csv(out / "temporal_edge_order_integrity.csv", index=False)
    refined[["alpha", "T", "seed", "within_fiber_A_diversity", "within_fiber_B_diversity", "within_fiber_component_balance", "within_fiber_effective_radius", "rigid_collapse_diversity_delta"]].to_csv(out / "within_fiber_diversity.csv", index=False)
    refined[["alpha", "T", "seed", "early_edge_survival", "middle_edge_survival", "late_edge_survival", "late_to_early_transport_ratio", "delayed_trap_late_delta", "final_segment_certified_mass"]].to_csv(out / "late_horizon_transport_retention.csv", index=False)
    priority = raw[raw["condition"].isin(PRIORITY_FALSE_POSITIVES + SECONDARY_FALSE_POSITIVES) | raw["kappa"].isin(["component_A_only", "component_B_only", "time_shuffled_COM", "random_balanced_k_COM_cardinality", "hash_high_cardinality"])].copy()
    priority.to_csv(out / "priority_false_positive_results.csv", index=False)
    summary_df.to_csv(out / "kappa_condition_scores.csv", index=False)
    threshold_sensitivity = refined_mean.copy()
    threshold_sensitivity["threshold"] = THRESHOLD
    threshold_sensitivity["component_threshold"] = COMPONENT_THRESHOLD
    threshold_sensitivity.to_csv(out / "threshold_sensitivity.csv", index=False)
    null = refined_mean[["alpha", "T", "delta_vs_product", "delta_vs_shuffled", "delta_vs_time_shuffled"]].copy()
    null.to_csv(out / "null_deltas.csv", index=False)
    ablation = build_ablation(refined)
    ablation.to_csv(out / "ablation_results.csv", index=False)
    boot = bootstrap(refined, ["alpha", "T"], BOOT_METRICS, cfg.bootstrap_repeats)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    est = raw[["condition", "kappa", "alpha", "T", "seed", "singleton_fraction", "small_fiber_fraction", "component_balance", "viable_propagation_index"]].copy()
    est["estimator_warning"] = np.where(est["singleton_fraction"] > 0.65, "HIGH_SINGLETON_FRACTION", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, refined, priority, ablation, summary_df)
    summary = make_summary(cfg, started, status, refined, priority, ablation)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def build_ablation(refined: pd.DataFrame) -> pd.DataFrame:
    rows = []
    defs = [
        ("base_definition_only", []),
        ("base_plus_R1_component_necessity", ["R1_component_necessity_pass"]),
        ("base_plus_R2_temporal_edge_order", ["R2_edge_order_pass"]),
        ("base_plus_R3_within_fiber_nondegeneracy", ["R3_nondegeneracy_pass"]),
        ("base_plus_R4_late_retention", ["R4_late_retention_pass"]),
        ("base_plus_R1_R2", ["R1_component_necessity_pass", "R2_edge_order_pass"]),
        ("base_plus_R1_R2_R3", ["R1_component_necessity_pass", "R2_edge_order_pass", "R3_nondegeneracy_pass"]),
        ("base_plus_R1_R2_R3_R4", ["R1_component_necessity_pass", "R2_edge_order_pass", "R3_nondegeneracy_pass", "R4_late_retention_pass"]),
    ]
    for name, checks in defs:
        mask = refined["base_signal_positive"].astype(bool)
        for c in checks:
            mask &= refined[c].astype(bool)
        rows.append({
            "ablation": name,
            "COM_coupled_retention": float(mask.mean()),
            "priority_false_positive_rejection": np.nan,
            "kills_false_positive": ",".join(checks),
        })
    return pd.DataFrame(rows)


def make_summary(cfg: Config, started: float, status: str, refined: pd.DataFrame, priority: pd.DataFrame, ablation: pd.DataFrame) -> dict[str, object]:
    mean = refined.mean(numeric_only=True).to_dict()
    fp = {}
    for key in ["component_A_only", "component_B_only", "time_shuffled_COM"]:
        sub = priority[(priority["condition"] == "coupled") & (priority["kappa"] == key)]
        fp[key] = float(sub["viable_propagation_index"].mean()) if len(sub) else None
    for key in PRIORITY_FALSE_POSITIVES:
        sub = priority[(priority["condition"] == key) & (priority["kappa"] == "center_of_mass")]
        fp[key] = float(sub["viable_propagation_index"].mean()) if len(sub) else None
    refined_positive = bool(refined["refined_positive"].mean() >= 0.50) if len(refined) else False
    blockers = []
    pass_rates = {}
    for col, name in [
        ("R1_component_necessity_pass", "R1_component_necessity"),
        ("R2_edge_order_pass", "R2_temporal_edge_order"),
        ("R3_nondegeneracy_pass", "R3_within_fiber_nondegeneracy"),
        ("R4_late_retention_pass", "R4_late_horizon_retention"),
    ]:
        rate = float(refined[col].astype(float).mean()) if len(refined) and col in refined else 0.0
        pass_rates[col] = rate
        if rate < 0.50:
            blockers.append(name)
    if refined_positive:
        rec = "Freeze refined fiber-transport candidate only after a full main run confirms smoke behavior."
        next_probe = "main_scale_13b_or_new_substrate"
    else:
        rec = "COM base signal remains useful, but refined pass fails at smoke scale; inspect blockers before any main run."
        next_probe = "distinction_adjudication_or_targeted_refinement"
    return {
        "probe": "13b_fiber_transport_false_positive_refinement",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "primary_witness": {
            "kappa": "center_of_mass",
            "condition": "coupled",
            "base_signal_positive": bool(mean.get("base_signal_positive", 0) >= 0.50),
            "refined_fiber_transport_positive": refined_positive,
            "mean_viable_propagation_index": mean.get("viable_propagation_index"),
            "delta_vs_product": mean.get("delta_vs_product"),
            "delta_vs_shuffled": mean.get("delta_vs_shuffled"),
            "delta_vs_time_shuffled": mean.get("delta_vs_time_shuffled"),
            "component_balance": mean.get("component_balance"),
            "component_necessity_min": mean.get("component_necessity_min"),
            "edge_order_integrity": mean.get("edge_order_delta_vs_time_shuffled"),
            "within_fiber_nondegeneracy": mean.get("rigid_collapse_diversity_delta"),
            "late_horizon_retention": mean.get("late_to_early_transport_ratio"),
        },
        "priority_false_positives": fp,
        "refinement_interpretation": {
            "blockers": blockers,
            "R1_pass_rate": pass_rates["R1_component_necessity_pass"],
            "R2_pass_rate": pass_rates["R2_edge_order_pass"],
            "R3_pass_rate": pass_rates["R3_nondegeneracy_pass"],
            "R4_pass_rate": pass_rates["R4_late_retention_pass"],
        },
        "recommendation": rec,
        "next_probe": next_probe,
        "estimator_warnings": sorted(set(priority.loc[priority["singleton_fraction"] > 0.65, "kappa"].dropna().astype(str).tolist())),
    }


def make_plots(out: Path, refined: pd.DataFrame, priority: pd.DataFrame, ablation: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    g = refined.groupby(["alpha", "T"])["component_necessity_min"].mean().reset_index()
    ax.scatter(g["T"], g["component_necessity_min"], c=g["alpha"])
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("Component necessity by alpha/T")
    fig.tight_layout()
    fig.savefig(out / "component_necessity_by_alpha_T.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    vals = refined[["edge_order_delta_vs_time_shuffled", "edge_order_delta_vs_endpoint_fakeout"]].mean()
    ax.barh(vals.index, vals.values)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Edge order delta forest plot")
    fig.tight_layout()
    fig.savefig(out / "edge_order_delta_forest_plot.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(refined["within_fiber_component_balance"], refined["rigid_collapse_diversity_delta"])
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("Within-fiber diversity vs rigid collapse")
    fig.tight_layout()
    fig.savefig(out / "within_fiber_diversity_vs_rigid_collapse.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(refined["T"], refined["late_to_early_transport_ratio"])
    ax.axhline(0.50, color="k", lw=0.8)
    ax.set_title("Late transport retention")
    fig.tight_layout()
    fig.savefig(out / "late_transport_retention.png", dpi=160)
    plt.close(fig)
    piv = priority.pivot_table(index="condition", columns="kappa", values="viable_propagation_index", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(piv.fillna(0).to_numpy(), aspect="auto")
    ax.set_yticks(range(len(piv.index)), piv.index)
    ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=45, ha="right")
    fig.colorbar(im, ax=ax)
    ax.set_title("Priority false-positive heatmap")
    fig.tight_layout()
    fig.savefig(out / "priority_false_positive_heatmap.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    counts = ablation.set_index("ablation")["COM_coupled_retention"]
    ax.barh(counts.index, counts.values)
    ax.set_title("Refined pass by kappa/condition")
    fig.tight_layout()
    fig.savefig(out / "refined_pass_by_kappa_condition.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    com = summary_df[(summary_df["condition"] == "coupled") & (summary_df["kappa"] == "center_of_mass")]
    ax.scatter(com["T"], com["viable_propagation_index"])
    ax.set_title("Threshold sensitivity")
    fig.tight_layout()
    fig.savefig(out / "threshold_sensitivity.png", dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    status = "COMPLETE"
    raw_path = cfg.out_dir / "_seed_refinement_rows.csv"
    if raw_path.exists():
        raw_path.unlink()
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    tasks = [(a, h, s, cfg) for a in cfg.alphas for h in cfg.horizons for s in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(task, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            append_rows(raw_path, fut.result())
            if i % max(1, cfg.workers) == 0:
                print(json.dumps({"completed_seed_blocks": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started, status)
    print("PROBE 13b: FIBER TRANSPORT FALSE-POSITIVE REFINEMENT")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
