#!/usr/bin/env python
"""Probe DA1: viable slack phase sweep.

Tests whether distinction + asymmetry + persistent relation has a middle phase
between noisy underconstraint and frozen overconstraint.
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
    bootstrap_repeats: int
    smoke: bool
    full_grid: bool


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DA1_viable_slack_phase_sweep_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "10000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "100")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "50,100,200")))
    p.add_argument("--n-sites", type=int, default=16)
    p.add_argument("--q", type=int, default=4)
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "300")))
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full-grid", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 18)
        args.n_traj = min(args.n_traj, 3000)
        args.seed_count = min(args.seed_count, 30)
        args.horizons = [50, 100]
        args.n_sites = 16
        args.q = 4
        args.bootstrap_repeats = min(args.bootstrap_repeats, 100)
    return Config(args.out_dir, args.workers, args.n_traj, args.seed_count, args.seed_start, sorted(args.horizons), args.n_sites, args.q, args.bootstrap_repeats, args.smoke, args.full_grid)


def phase_points(full_grid: bool) -> list[tuple[float, float, float]]:
    vals = [0.0, 0.25, 0.50, 0.75, 1.0]
    if full_grid:
        return [(r, a, l) for r in vals for a in vals for l in vals]
    pts = {
        (0.0, 0.0, 0.0),
        (0.0, 0.5, 0.5),
        (0.5, 0.0, 0.5),
        (0.5, 0.5, 0.0),
        (0.5, 0.5, 0.5),
        (0.5, 0.5, 1.0),
        (0.5, 1.0, 0.5),
        (1.0, 0.5, 0.5),
        (1.0, 1.0, 1.0),
    }
    pts.update((r, 0.5, 0.5) for r in vals)
    pts.update((0.75, a, 0.5) for a in vals)
    pts.update((0.75, 0.5, l) for l in vals)
    return sorted(pts)


def control_points() -> list[tuple[str, float, float, float]]:
    return [
        ("noise_rich_control", 0.0, 0.0, 0.0),
        ("collapse_attractor_control", 1.0, 1.0, 1.0),
        ("independent_sites_control", 0.0, 0.5, 0.5),
        ("symmetric_transition_control", 0.75, 0.0, 0.5),
        ("random_stepwise_relation_control", 0.0, 0.5, 0.5),
        ("relation_lock_in_control", 1.0, 1.0, 1.0),
    ]


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


def row_codes(x: np.ndarray) -> np.ndarray:
    out = np.zeros(x.shape[0], dtype=np.int64)
    for i in range(x.shape[1]):
        out = (out * 1_000_003 + x[:, i].astype(np.int64) + 17 * i) % 9_223_372_036_854_775_123
    return out


def fixed_sources(n: int) -> np.ndarray:
    module = max(4, n // 4)
    src = np.arange(n)
    for i in range(n):
        src[i] = i - 1 if i % module else (i + module - 1) % n
    return src


def simulate(rho: float, alpha: float, lam: float, T: int, cfg: Config, seed: int, control: str | None) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(91_000 + seed * 1009 + int(100 * rho) * 31 + int(100 * alpha) * 17 + int(100 * lam) * 13 + T)
    n = cfg.n_sites
    q = cfg.q
    x = rng.integers(0, q, size=(cfg.n_traj, n), dtype=np.int16)
    if control == "collapse_attractor_control":
        x = rng.integers(0, 2, size=(cfg.n_traj, n), dtype=np.int16)
    traj = np.empty((T + 1, cfg.n_traj, n), dtype=np.int16)
    sources = np.empty((T, n), dtype=np.int16)
    traj[0] = x
    src = fixed_sources(n)
    memory = x.copy()
    for t in range(T):
        if control in {"independent_sites_control", "noise_rich_control"}:
            src_t = np.arange(n)
        elif control == "random_stepwise_relation_control" or rng.random() > rho:
            src_t = rng.integers(0, n, size=n)
        else:
            keep = rng.random(n) < rho
            src_t = np.where(keep, src, rng.integers(0, n, size=n))
            src = src_t
        sources[t] = src_t
        neigh = memory[:, src_t]
        if control == "noise_rich_control":
            proposal = rng.integers(0, q, size=x.shape, dtype=np.int16)
        elif control == "collapse_attractor_control":
            proposal = np.where(rng.random(size=x.shape) < 0.25 + 0.55 * lam, 0, x)
        else:
            relation_mix = np.clip(0.25 + 0.65 * rho, 0, 1)
            influence = np.where(rng.random(size=x.shape) < relation_mix, neigh, x)
            if control == "symmetric_transition_control":
                a = 0.0
            else:
                a = alpha
            p_forward = 0.12 + 0.30 * a
            p_reverse = 0.12 * (1.0 - a)
            p_stay = max(0.05, 1.0 - p_forward - p_reverse)
            step = rng.choice(np.array([-1, 0, 1], dtype=np.int16), size=x.shape, p=[p_reverse, p_stay, p_forward])
            proposal = (influence + step) % q
            if control == "relation_lock_in_control":
                stay = 0.92
            else:
                stay = np.clip(0.15 + 0.72 * lam, 0.05, 0.94)
            proposal = np.where(rng.random(size=x.shape) < stay, influence, proposal)
        memory = x.copy()
        x = proposal.astype(np.int16)
        traj[t + 1] = x
    return {"traj": traj, "sources": sources}


def viable_mask(traj: np.ndarray, control: str | None) -> np.ndarray:
    distinct = np.array([[len(np.unique(traj[t, j])) for j in range(traj.shape[1])] for t in range(traj.shape[0])])
    not_all_same = np.all(distinct > 1, axis=0)
    not_zero = ~np.any(np.all(traj == 0, axis=2), axis=0)
    if control == "noise_rich_control":
        return not_all_same & not_zero
    return not_all_same & not_zero & np.all(distinct > 2, axis=0)


def prediction_accuracy(keys: np.ndarray, target: np.ndarray) -> float:
    correct = 0
    total = 0
    for k in np.unique(keys):
        mask = keys == k
        _, counts = np.unique(target[mask], return_counts=True)
        correct += int(np.max(counts))
        total += int(np.sum(counts))
    return float(correct / max(total, 1))


def metrics(traj: np.ndarray, sources: np.ndarray, viable: np.ndarray, cfg: Config, seed: int) -> dict[str, float]:
    q = cfg.q
    T = sources.shape[0]
    tv = traj[:, viable] if np.any(viable) else traj[:, :0]
    p_viable = float(np.mean(viable))
    collapse_rate = float(1.0 - np.mean(~np.any(np.all(traj == 0, axis=2), axis=0)))
    if tv.shape[1] == 0:
        return empty_metrics(p_viable, collapse_rate)
    lineage = float(np.mean(tv[-1] == tv[0]))
    branch_ent = float(np.mean([entropy(tv[t].reshape(-1)) for t in range(tv.shape[0])]))
    merge = float(max(0, len(np.unique(tv[0])) - len(np.unique(tv[-1]))) / max(len(np.unique(tv[0])), 1))
    extinction = 1.0 - lineage
    self_scores = []
    rel_scores = []
    indep_scores = []
    rng = np.random.default_rng(92_000 + seed)
    for t in range(T):
        indep_src = rng.permutation(sources[t])
        for i, j in enumerate(sources[t]):
            target = tv[t + 1, :, i]
            self_key = tv[t, :, i]
            rel_key = self_key.astype(np.int64) * 17 + tv[t, :, j]
            indep_key = self_key.astype(np.int64) * 17 + tv[t, :, indep_src[i]]
            self_scores.append(prediction_accuracy(self_key, target))
            rel_scores.append(prediction_accuracy(rel_key, target))
            indep_scores.append(prediction_accuracy(indep_key, target))
    relation_lineage = float(np.mean(rel_scores))
    self_only = float(np.mean(self_scores))
    independent = float(np.mean(indep_scores))
    relation_excess = relation_lineage - max(self_only, independent)
    mid = tv.shape[0] // 2
    closure = float(np.mean(tv[-1] == tv[mid]))
    recurrence = float(np.mean([np.mean(tv[t] == tv[0]) for t in range(mid, tv.shape[0])]))
    final_codes = row_codes(tv[-1])
    _, counts = np.unique(final_codes, return_counts=True)
    concentration = float(np.max(counts) / np.sum(counts)) if len(counts) else 1.0
    alternatives = float(len(counts))
    branching_after = entropy(tv[-1].reshape(-1)) / max(math.log2(q), 1e-9)
    # Lightweight perturbation: flip one site at early/mid and ask whether final
    # class still remains in the observed viable support.
    observed = set(final_codes.tolist())
    sample_idx = rng.choice(tv.shape[1], min(300, tv.shape[1]), replace=False)
    cont = []
    for t0 in [max(1, T // 4), max(1, T // 2)]:
        pert = tv[t0, sample_idx].copy()
        cols = rng.integers(0, cfg.n_sites, size=len(sample_idx))
        pert[np.arange(len(sample_idx)), cols] = (pert[np.arange(len(sample_idx)), cols] + 1) % q
        cont.append(float(np.mean([c in observed for c in row_codes(pert)])))
    post_pert = float(np.mean(cont))
    transition_determinism = float(np.mean(np.array(rel_scores) - 1.0 / q))
    state_concentration = concentration
    relation_rigidity = float(np.mean([np.mean(sources[t] == sources[0]) for t in range(T)]))
    branching_collapse = float(1.0 - min(branching_after, 1.0))
    lock = np.clip(max(0, transition_determinism) * state_concentration * (1.0 - min(branching_after, 1.0) + 0.05 * relation_rigidity), 0.0, 1.0)
    return {
        "p_viable": p_viable,
        "survival_depth": p_viable,
        "collapse_rate": collapse_rate,
        "lineage_survival_depth": lineage,
        "lineage_branching_entropy": branch_ent,
        "lineage_merge_rate": merge,
        "lineage_extinction_rate": extinction,
        "relation_lineage": relation_lineage,
        "self_only_lineage": self_only,
        "independent_lineage_baseline": independent,
        "relation_lineage_excess": relation_excess,
        "closure_rate": closure,
        "lineage_recurrence_rate": recurrence,
        "cycle_or_return_rate": recurrence,
        "recoverable_alternative_count": alternatives,
        "branching_after_closure": branching_after,
        "post_perturbation_continuation_rate": post_pert,
        "transition_determinism": transition_determinism,
        "state_concentration": state_concentration,
        "relation_rigidity": relation_rigidity,
        "branching_collapse": branching_collapse,
        "lock_in_index": float(lock),
    }


def empty_metrics(p_viable: float, collapse_rate: float) -> dict[str, float]:
    keys = [
        "survival_depth", "lineage_survival_depth", "lineage_branching_entropy", "lineage_merge_rate", "lineage_extinction_rate",
        "relation_lineage", "self_only_lineage", "independent_lineage_baseline", "relation_lineage_excess",
        "closure_rate", "lineage_recurrence_rate", "cycle_or_return_rate", "recoverable_alternative_count",
        "branching_after_closure", "post_perturbation_continuation_rate", "transition_determinism",
        "state_concentration", "relation_rigidity", "branching_collapse", "lock_in_index",
    ]
    out = {k: 0.0 for k in keys}
    out["p_viable"] = p_viable
    out["collapse_rate"] = collapse_rate
    out["lineage_extinction_rate"] = 1.0
    out["lock_in_index"] = 1.0
    return out


def classify(row: dict[str, float]) -> str:
    if row["closure_rate"] < 0.15 and row["relation_lineage_excess"] <= 0:
        return "underconstrained"
    if row["closure_rate"] >= 0.35 and row["lock_in_index"] >= 0.25 and row["recoverable_alternative_count"] < 0.25 * 3000:
        return "overconstrained"
    if row["relation_lineage_excess"] > 0 and row["closure_rate"] >= 0.15 and row["recoverable_alternative_count"] > 100 and row["lock_in_index"] < 0.25:
        return "viable_slack_candidate"
    return "mixed_or_inconclusive"


def task(task_def: tuple[str, float, float, float, int, int, Config]) -> dict[str, object]:
    label, rho, alpha, lam, T, seed, cfg = task_def
    control = label if label.endswith("_control") else None
    sim = simulate(rho, alpha, lam, T, cfg, seed, control)
    viable = viable_mask(sim["traj"], control)
    row = {
        "point_id": label,
        "rho_relation_persistence": rho,
        "alpha_asymmetry_strength": alpha,
        "lambda_constraint_pressure": lam,
        "T": T,
        "seed": seed,
        "is_control": bool(control),
        "control": control or "",
    }
    row.update(metrics(sim["traj"], sim["sources"], viable, cfg, seed))
    row["classification"] = classify(row)
    return row


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics_: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(93_000)
    rows = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in metrics_:
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
    raw["control"] = raw["control"].fillna("")
    means = raw.groupby(["point_id", "rho_relation_persistence", "alpha_asymmetry_strength", "lambda_constraint_pressure", "T", "is_control", "control"], as_index=False).mean(numeric_only=True)
    class_rows = []
    for _, r in means.iterrows():
        d = r.to_dict()
        d["classification"] = classify(d)
        class_rows.append(d)
    classified = pd.DataFrame(class_rows)
    pd.DataFrame([{"rho_relation_persistence": r, "alpha_asymmetry_strength": a, "lambda_constraint_pressure": l} for r, a, l in phase_points(cfg.full_grid)]).to_csv(out / "phase_points.csv", index=False)
    raw[["point_id", "T", "seed", "p_viable", "survival_depth", "collapse_rate"]].to_csv(out / "viability_metrics.csv", index=False)
    raw[["point_id", "T", "seed", "lineage_survival_depth", "lineage_branching_entropy", "lineage_merge_rate", "lineage_extinction_rate"]].to_csv(out / "distinction_lineage.csv", index=False)
    raw[["point_id", "T", "seed", "relation_lineage", "self_only_lineage", "independent_lineage_baseline", "relation_lineage_excess"]].to_csv(out / "relation_lineage_excess.csv", index=False)
    raw[["point_id", "T", "seed", "closure_rate", "lineage_recurrence_rate", "cycle_or_return_rate"]].to_csv(out / "closure_metrics.csv", index=False)
    raw[["point_id", "T", "seed", "recoverable_alternative_count", "branching_after_closure", "post_perturbation_continuation_rate"]].to_csv(out / "recoverable_alternatives.csv", index=False)
    raw[["point_id", "T", "seed", "transition_determinism", "state_concentration", "relation_rigidity", "branching_collapse", "lock_in_index"]].to_csv(out / "lock_in_metrics.csv", index=False)
    classified.to_csv(out / "phase_classification.csv", index=False)
    controls = classified[classified["is_control"]].copy()
    controls.to_csv(out / "control_positions.csv", index=False)
    boot = bootstrap(raw, ["point_id", "T"], ["p_viable", "relation_lineage_excess", "closure_rate", "recoverable_alternative_count", "lock_in_index"], cfg.bootstrap_repeats)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    est = classified[["point_id", "T", "p_viable", "collapse_rate", "recoverable_alternative_count", "lock_in_index", "classification"]].copy()
    est["estimator_warning"] = np.where(est["p_viable"] <= 0.01, "LOW_VIABILITY", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, classified)
    summary = make_summary(cfg, started, classified)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def make_summary(cfg: Config, started: float, df: pd.DataFrame) -> dict[str, object]:
    non_controls = df[~df["is_control"]].copy()
    controls = df[df["is_control"]].copy()
    noise_p = control_mean(controls, "noise_rich_control", "p_viable")
    collapse_p = control_mean(controls, "collapse_attractor_control", "p_viable")
    lock = control_mean(controls, "relation_lock_in_control", "lock_in_index")
    non_controls["candidate_score"] = (
        (non_controls["p_viable"] > max(noise_p, collapse_p)).astype(float)
        + (non_controls["relation_lineage_excess"] > 0).astype(float)
        + non_controls["closure_rate"]
        + np.log1p(non_controls["recoverable_alternative_count"]) / 8.0
        + (non_controls["lock_in_index"] < lock).astype(float)
    )
    best = non_controls.sort_values("candidate_score", ascending=False).iloc[0]
    best_extreme = any(abs(float(best[c]) - e) < 1e-9 for c in ["rho_relation_persistence", "alpha_asymmetry_strength", "lambda_constraint_pressure"] for e in [0.0, 1.0])
    middle_detected = bool(best["classification"] == "viable_slack_candidate" and not best_extreme)
    controls_regions = {
        row["control"]: row["classification"] for _, row in controls.groupby("control", as_index=False).first().iterrows()
    }
    controls_expected = (
        controls_regions.get("noise_rich_control") in {"underconstrained", "mixed_or_inconclusive"}
        and controls_regions.get("collapse_attractor_control") in {"overconstrained", "mixed_or_inconclusive"}
        and controls_regions.get("relation_lock_in_control") in {"overconstrained", "mixed_or_inconclusive"}
    )
    rec = "DA1 smoke shows a middle viable-slack candidate; consider main grid." if middle_detected and controls_expected else "DA1 smoke does not yet establish a clean viable-slack phase; inspect phase map before scaling."
    return {
        "probe": "DA1_viable_slack_phase_sweep",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "phase_points": int(non_controls[["rho_relation_persistence", "alpha_asymmetry_strength", "lambda_constraint_pressure"]].drop_duplicates().shape[0]),
        "best_phase_point": {
            "rho_relation_persistence": float(best["rho_relation_persistence"]),
            "alpha_asymmetry_strength": float(best["alpha_asymmetry_strength"]),
            "lambda_constraint_pressure": float(best["lambda_constraint_pressure"]),
            "classification": str(best["classification"]),
        },
        "phase_hypothesis_result": {
            "middle_regime_detected": middle_detected,
            "best_point_is_extreme": bool(best_extreme),
            "relation_lineage_excess_positive": bool(best["relation_lineage_excess"] > 0),
            "closure_without_lockin_detected": bool(best["closure_rate"] > 0.15 and best["lock_in_index"] < lock),
            "controls_in_expected_regions": bool(controls_expected),
        },
        "best_profile": {
            "p_viable": float(best["p_viable"]),
            "lineage_survival_depth": float(best["lineage_survival_depth"]),
            "relation_lineage_excess": float(best["relation_lineage_excess"]),
            "closure_rate": float(best["closure_rate"]),
            "recoverable_alternative_count": float(best["recoverable_alternative_count"]),
            "lock_in_index": float(best["lock_in_index"]),
        },
        "control_results": controls_regions,
        "recommendation": rec,
        "next_probe": "DA1_main_grid_or_DA2_lineage" if middle_detected and controls_expected else "DA1_metric_or_world_revision",
        "estimator_warnings": sorted(df.loc[df["p_viable"] <= 0.01, "point_id"].unique().tolist()),
    }


def control_mean(controls: pd.DataFrame, name: str, metric: str) -> float:
    sub = controls[controls["control"] == name]
    return float(sub[metric].mean()) if len(sub) else 0.0


def make_plots(out: Path, df: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    non = df[~df["is_control"]]
    for x, y, fname in [
        ("rho_relation_persistence", "lambda_constraint_pressure", "phase_map_relation_vs_constraint.png"),
        ("alpha_asymmetry_strength", "lambda_constraint_pressure", "phase_map_asymmetry_vs_constraint.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7, 5))
        sc = ax.scatter(non[x], non[y], c=non["relation_lineage_excess"], s=80)
        fig.colorbar(sc, ax=ax, label="relation_lineage_excess")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(range(len(non)), non.sort_values("relation_lineage_excess")["relation_lineage_excess"])
    ax.set_title("Relation lineage excess by phase")
    fig.tight_layout()
    fig.savefig(out / "relation_lineage_excess_by_phase.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df["lock_in_index"], df["closure_rate"], c=df["is_control"].astype(int))
    ax.set_xlabel("lock_in_index")
    ax.set_ylabel("closure_rate")
    fig.tight_layout()
    fig.savefig(out / "closure_vs_lockin_scatter.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(range(len(non)), non.sort_values("recoverable_alternative_count")["recoverable_alternative_count"])
    ax.set_title("Recoverable alternatives by phase")
    fig.tight_layout()
    fig.savefig(out / "recoverable_alternatives_by_phase.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    candidates = (non["classification"] == "viable_slack_candidate").astype(float)
    sc = ax.scatter(non["rho_relation_persistence"], non["alpha_asymmetry_strength"], c=candidates, s=90)
    fig.colorbar(sc, ax=ax)
    ax.set_title("Viable slack candidate map")
    fig.tight_layout()
    fig.savefig(out / "viable_slack_candidate_map.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    controls = df[df["is_control"]]
    ax.scatter(controls["lock_in_index"], controls["relation_lineage_excess"])
    for _, r in controls.iterrows():
        ax.annotate(str(r["control"]).replace("_control", ""), (r["lock_in_index"], r["relation_lineage_excess"]), fontsize=7)
    ax.set_xlabel("lock_in_index")
    ax.set_ylabel("relation_lineage_excess")
    fig.tight_layout()
    fig.savefig(out / "control_positions_phase_space.png", dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    raw = cfg.out_dir / "_seed_rows.csv"
    if raw.exists():
        raw.unlink()
    started = time.monotonic()
    base = [(f"phase_{i:03d}", r, a, l) for i, (r, a, l) in enumerate(phase_points(cfg.full_grid))]
    points = base + control_points()
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    tasks = [(label, r, a, l, T, seed, cfg) for label, r, a, l in points for T in cfg.horizons for seed in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(task, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            append_rows(raw, [fut.result()])
            if i % max(1, cfg.workers * 5) == 0:
                print(json.dumps({"completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started)
    print("PROBE DA1: VIABLE SLACK PHASE SWEEP")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
