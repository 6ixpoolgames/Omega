#!/usr/bin/env python
"""Probe 08b: transport-dominant multifield validation.

This runner reuses the Probe 08a standalone toy simulator and focuses compute
on the narrow F,T attractive corridor that survived reconciliation.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

import probe_08a_multifield_profile_reconciliation as p08a


KAPPAS_08B = [
    "center_of_mass",
    "joint_basin",
    "basin_transition_profile",
    "boundary_v2_regime_sequence",
]

MAIN_METRICS = [
    "Delta_R",
    "Delta_H_cond_product",
    "Delta_H_weighted_product",
    "Delta_H_recovery_product",
    "strict_certified_mass_advantage",
    "certified_transport_density_advantage",
    "component_A_preservation",
    "component_B_preservation",
    "lower_rank_erasure_score",
    "singleton_fraction",
]


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("probe_08b_transport_dominant_multifield_validation_results"))
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--n-traj", type=int, default=5000)
    parser.add_argument("--seed-count", type=int, default=120)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--alphas", type=parse_csv_floats, default=parse_csv_floats("0.45,0.50,0.525"))
    parser.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints("900,1500,2400"))
    parser.add_argument("--bootstrap-repeats", type=int, default=500)
    parser.add_argument("--soft-limit-sec", type=float, default=1500)
    parser.add_argument("--hard-limit-sec", type=float, default=1800)
    parser.add_argument("--sample-points", type=int, default=13)
    parser.add_argument("--dt", type=float, default=0.018)
    parser.add_argument("--noise", type=float, default=0.055)
    parser.add_argument("--coupling-scale", type=float, default=0.085)
    return parser.parse_args()


def make_config(args: argparse.Namespace) -> p08a.Config:
    return p08a.Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seeds=list(range(args.seed_start, args.seed_start + args.seed_count)),
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


def run_seed_task_08b(task: tuple[float, int, p08a.Config]) -> dict[str, list[dict[str, object]]]:
    p08a.KAPPAS = KAPPAS_08B
    return p08a.run_seed_task(task)


def ci_table(seed_df: pd.DataFrame, group_cols: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(808_200)
    rows: list[dict[str, object]] = []
    for key, group in seed_df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in MAIN_METRICS:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(dtype=float)
            mean = float(np.mean(vals))
            std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, size=len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            width = float(hi - lo)
            rows.append({
                **base,
                "metric": metric,
                "mean": mean,
                "std": std,
                "se": std / math.sqrt(max(len(vals), 1)),
                "ci_low": float(lo),
                "ci_high": float(hi),
                "ci_width": width,
                "ci_excludes_zero": bool(lo > 0 or hi < 0),
                "n_seeds": int(len(vals)),
            })
    return pd.DataFrame(rows)


def wide_ci(metric_mean: float, ci_width: float) -> bool:
    return bool(ci_width > 0.30 * max(abs(metric_mean), 1e-9))


def categorize(row: pd.Series) -> str:
    if row["singleton_fraction"] >= 0.65:
        return "Overfragmented/inconclusive"
    if row["component_A_preservation"] < 0.70 or row["component_B_preservation"] < 0.70 or row["lower_rank_erasure_score"] > 0.20:
        return "Component-erasing candidate"
    if row["transport_ci_positive"] and row["component_preservation_ok"]:
        return "Transport-dominant candidate"
    if row["Delta_H_weighted_product"] < 0 and row["certified_transport_density_advantage"] > 0 and row["component_preservation_ok"]:
        return "Stabilizing compression"
    if (row["Delta_R"] > 0 or row["Delta_H_cond_product"] > 0) and (
        row["certified_transport_density_advantage"] <= 0 or row["strict_certified_mass_advantage"] <= 0
    ):
        return "Entropy-only pseudo-risk"
    if all(abs(float(row[c])) < 0.03 for c in ["Delta_R", "Delta_H_weighted_product", "certified_transport_density_advantage", "strict_certified_mass_advantage"]):
        return "Null-like"
    return "Estimator-limited inconclusive"


def build_outputs(cfg: p08a.Config, started: float, status: str) -> dict[str, object]:
    out = cfg.out_dir
    joint = pd.read_csv(out / "_joint_seed_blocks.csv")
    fiber = pd.read_csv(out / "_fiber_seed_blocks.csv")
    component = pd.read_csv(out / "_component_seed_blocks.csv")
    transport = pd.read_csv(out / "_transport_seed_blocks.csv")
    estimator = pd.read_csv(out / "_estimator_seed_blocks.csv")
    product = pd.read_csv(out / "_product_seed_blocks.csv")
    shuffled = pd.read_csv(out / "_shuffled_seed_blocks.csv")

    group_cols = ["alpha", "T", "kappa"]
    joint_mean = joint.groupby(group_cols, as_index=False).mean(numeric_only=True)
    fiber_mean = fiber.groupby(group_cols, as_index=False).mean(numeric_only=True)
    comp_mean = component.groupby(group_cols, as_index=False).mean(numeric_only=True)
    trans_mean = transport.groupby(group_cols, as_index=False).mean(numeric_only=True)
    product_mean = product.groupby(group_cols, as_index=False).mean(numeric_only=True)
    shuffled_mean = shuffled.groupby(group_cols, as_index=False).mean(numeric_only=True)

    merged_seed = joint.merge(component, on=group_cols + ["seed"], suffixes=("", "_component"))
    intervals = ci_table(merged_seed, group_cols, cfg.bootstrap_repeats)
    intervals.to_csv(out / "bootstrap_intervals.csv", index=False)

    ci_wide = intervals.pivot(index=group_cols, columns="metric", values=["ci_low", "ci_high", "ci_width", "mean"]).reset_index()
    ci_wide.columns = ["_".join([str(x) for x in col if str(x)]) for col in ci_wide.columns.to_flat_index()]

    primary = joint_mean.merge(fiber_mean, on=group_cols, suffixes=("", "_fiber"))
    primary = primary.merge(comp_mean, on=group_cols, suffixes=("", "_component"))
    primary = primary.merge(trans_mean, on=group_cols, suffixes=("", "_transport"))
    primary = primary.merge(ci_wide, on=group_cols, how="left")

    primary["transport_ci_positive"] = primary["ci_low_certified_transport_density_advantage"] > 0
    primary["mass_ci_positive"] = primary["ci_low_strict_certified_mass_advantage"] > 0
    primary["entropy_ci_positive"] = primary["ci_low_Delta_H_weighted_product"] > 0
    primary["entropy_ci_negative"] = primary["ci_high_Delta_H_weighted_product"] < 0
    primary["component_preservation_ok"] = (
        (primary["component_A_preservation"] >= 0.70)
        & (primary["component_B_preservation"] >= 0.70)
        & (primary["lower_rank_erasure_score"] <= 0.20)
    )
    primary["overfragmented"] = primary["singleton_fraction"] >= 0.65
    primary["estimator_stable"] = ~primary.apply(
        lambda r: wide_ci(r["mean_certified_transport_density_advantage"], r["ci_width_certified_transport_density_advantage"]),
        axis=1,
    )
    primary["uncertainty_status"] = np.where(primary["estimator_stable"], "stable", "wide_transport_ci")
    primary["category"] = primary.apply(categorize, axis=1)

    table_cols = [
        "alpha", "T", "kappa", "Delta_R", "Delta_H_weighted_product",
        "certified_transport_density_advantage", "strict_certified_mass_advantage",
        "singleton_fraction", "component_A_preservation", "component_B_preservation",
        "lower_rank_erasure_score", "transport_ci_positive", "mass_ci_positive",
        "entropy_ci_positive", "entropy_ci_negative", "component_preservation_ok",
        "overfragmented", "estimator_stable", "category", "uncertainty_status",
    ]
    primary[table_cols].to_csv(out / "primary_regime_table.csv", index=False)

    omega_cols = [
        "alpha", "T", "kappa", "p_viable_AB", "p_viable_shuffled",
        "Delta_p_viable_product", "Delta_p_viable_shuffled", "H_cond_AB",
        "H_cond_shuffled", "Delta_H_cond_product", "Delta_H_cond_shuffled",
        "H_weighted_AB", "H_weighted_shuffled", "Delta_H_weighted_product",
        "Delta_H_weighted_shuffled", "H_recovery_AB", "H_recovery_shuffled",
        "Delta_H_recovery_product", "Delta_H_recovery_shuffled",
    ]
    joint_mean[omega_cols].to_csv(out / "omega_profile_deltas.csv", index=False)

    tf = fiber_mean.merge(trans_mean, on=group_cols, suffixes=("", "_transport"))
    tf.to_csv(out / "transport_fiber_metrics.csv", index=False)
    comp_mean.to_csv(out / "component_preservation.csv", index=False)
    primary[primary["T"] == 2400][table_cols].to_csv(out / "horizon_stress_T2400.csv", index=False)

    est = estimator.groupby(group_cols, as_index=False).agg(
        n_traj=("n_traj", "mean"),
        macro_classes=("macro_classes", "mean"),
        singleton_fraction=("singleton_fraction", "mean"),
        estimator_warning=("estimator_warning", lambda s: ";".join(sorted({str(x) for x in s if pd.notna(x) and str(x) and str(x) != "nan"}))),
    )
    est.to_csv(out / "estimator_report.csv", index=False)

    product_mean.to_csv(out / "product_baseline_profiles.csv", index=False)
    shuffled_mean.to_csv(out / "shuffled_baseline_profiles.csv", index=False)

    corridor = primary[(primary["kappa"] == "center_of_mass") & (primary["T"].isin([900, 1500]))]
    summary = {
        "probe": "08b_transport_dominant_multifield_validation",
        "status": status,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "workers": cfg.workers,
        "n_traj": cfg.n_traj,
        "seed_count_requested": len(cfg.seeds),
        "seed_count_completed": int(joint["seed"].nunique()),
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "completed_alpha_T_kappa_rows": int(len(primary)),
        "alphas_completed": sorted(float(x) for x in joint["alpha"].unique()),
        "horizons_completed": sorted(int(x) for x in joint["T"].unique()),
        "kappas_completed": sorted(joint["kappa"].unique().tolist()),
        "estimator_warnings": estimator["estimator_warning"].fillna("").value_counts().to_dict(),
        "primary_corridor_center_of_mass": corridor[table_cols].to_dict(orient="records"),
        "category_counts": primary["category"].value_counts().to_dict(),
        "transport_dominant_candidates": primary[primary["category"] == "Transport-dominant candidate"][table_cols].to_dict(orient="records"),
        "pseudo_risk_candidates": primary[primary["category"] == "Entropy-only pseudo-risk"][table_cols].to_dict(orient="records"),
        "files": sorted(p.name for p in out.glob("*") if not p.name.startswith("_")),
        "method_note": "Standalone toy multifield simulator inherited from Probe 08a; not the original unpublished simulator.",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    status = "COMPLETE"

    p08a.KAPPAS = KAPPAS_08B
    for name in [
        "_joint_seed_blocks.csv", "_product_seed_blocks.csv", "_shuffled_seed_blocks.csv",
        "_fiber_seed_blocks.csv", "_transport_seed_blocks.csv", "_component_seed_blocks.csv",
        "_estimator_seed_blocks.csv",
    ]:
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
            futures.append(pool.submit(run_seed_task_08b, task))

        completed = 0
        for fut in as_completed(futures):
            elapsed = time.monotonic() - started
            if elapsed > cfg.hard_limit_seconds:
                status = "PARTIAL_EXIT_HARD_LIMIT"
            result = fut.result()
            p08a.append_rows(cfg.out_dir / "_joint_seed_blocks.csv", result["joint"])
            p08a.append_rows(cfg.out_dir / "_product_seed_blocks.csv", result["product"])
            p08a.append_rows(cfg.out_dir / "_shuffled_seed_blocks.csv", result["shuffled"])
            p08a.append_rows(cfg.out_dir / "_fiber_seed_blocks.csv", result["fiber"])
            p08a.append_rows(cfg.out_dir / "_transport_seed_blocks.csv", result["transport"])
            p08a.append_rows(cfg.out_dir / "_component_seed_blocks.csv", result["component"])
            p08a.append_rows(cfg.out_dir / "_estimator_seed_blocks.csv", result["estimator"])
            completed += 1
            if completed % max(1, cfg.workers) == 0:
                print(json.dumps({"completed_seed_blocks": completed, "total_launched": len(futures), "elapsed_seconds": round(elapsed, 1)}), flush=True)
            if status == "PARTIAL_EXIT_HARD_LIMIT":
                break

    summary = build_outputs(cfg, started, status)
    print("PROBE 08B: TRANSPORT-DOMINANT MULTIFIELD VALIDATION")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
