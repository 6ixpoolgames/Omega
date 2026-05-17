#!/usr/bin/env python
"""Probe DA1b: apparent slack vs viable slack diagnostic.

Diagnoses whether DA1's counted slack is load-bearing and future-distinct, or
an artifact of symmetry, lock-in, independent sites, or microstate multiplicity.
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
    perturbation_samples: int
    smoke: bool


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DA1b_apparent_vs_viable_slack_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "5000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "50")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "50,100")))
    p.add_argument("--n-sites", type=int, default=16)
    p.add_argument("--q", type=int, default=4)
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
        args.bootstrap_repeats,
        args.perturbation_samples,
        args.smoke,
    )


def diagnostic_targets() -> list[dict[str, object]]:
    rows = [
        ("da1_extreme_best", 1.0, 1.0, 1.0, "extreme"),
        ("middle_r075_a050_l050", 0.75, 0.50, 0.50, "middle"),
        ("middle_r050_a050_l050", 0.50, 0.50, 0.50, "middle"),
        ("middle_r075_a075_l050", 0.75, 0.75, 0.50, "middle"),
        ("optional_r100_a050_l050", 1.0, 0.50, 0.50, "optional"),
        ("optional_r075_a100_l050", 0.75, 1.0, 0.50, "optional"),
        ("optional_r075_a050_l100", 0.75, 0.50, 1.0, "optional"),
        ("relation_lock_in_control", 1.0, 1.0, 1.0, "control"),
        ("symmetric_transition_control", 0.75, 0.0, 0.50, "control"),
        ("independent_sites_control", 0.0, 0.50, 0.50, "control"),
        ("random_stepwise_relation_control", 0.0, 0.50, 0.50, "control"),
        ("noise_rich_control", 0.0, 0.0, 0.0, "control"),
        ("collapse_attractor_control", 1.0, 1.0, 1.0, "control"),
    ]
    return [
        {
            "target": name,
            "rho_relation_persistence": rho,
            "alpha_asymmetry_strength": alpha,
            "lambda_constraint_pressure": lam,
            "target_kind": kind,
            "control": name if kind == "control" else "",
        }
        for name, rho, alpha, lam, kind in rows
    ]


def append_row(path: Path, row: dict[str, object]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def entropy(codes: np.ndarray) -> float:
    if len(codes) == 0:
        return 0.0
    _, counts = np.unique(codes, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-12))))


def fixed_sources(n: int) -> np.ndarray:
    module = max(4, n // 4)
    src = np.arange(n)
    for i in range(n):
        src[i] = i - 1 if i % module else (i + module - 1) % n
    return src


def row_codes(x: np.ndarray) -> np.ndarray:
    out = np.zeros(x.shape[0], dtype=np.int64)
    for i in range(x.shape[1]):
        out = (out * 1_000_003 + x[:, i].astype(np.int64) + 17 * i) % 9_223_372_036_854_775_123
    return out


def future_signature(states: np.ndarray, initial: np.ndarray, mid: np.ndarray, q: int) -> np.ndarray:
    """Coarse, non-learned future basin signature."""
    counts = np.stack([(states == k).sum(axis=1) for k in range(q)], axis=1).astype(np.int64)
    changed_from_initial = (states != initial).sum(axis=1).astype(np.int64)
    changed_from_mid = (states != mid).sum(axis=1).astype(np.int64)
    parity = np.sum(states * (np.arange(states.shape[1]) + 1), axis=1).astype(np.int64) % max(q, 2)
    sig = counts.copy()
    sig = np.column_stack([sig, changed_from_initial, changed_from_mid, parity])
    return row_codes(sig)


def transition_step(
    x: np.ndarray,
    memory: np.ndarray,
    src: np.ndarray,
    rho: float,
    alpha: float,
    lam: float,
    control: str,
    rng: np.random.Generator,
    q: int,
) -> tuple[np.ndarray, np.ndarray]:
    n = x.shape[1]
    if control in {"independent_sites_control", "noise_rich_control"}:
        src_t = np.arange(n)
    elif control == "random_stepwise_relation_control" or rng.random() > rho:
        src_t = rng.integers(0, n, size=n)
    else:
        keep = rng.random(n) < rho
        src_t = np.where(keep, src, rng.integers(0, n, size=n))
        src = src_t
    neigh = memory[:, src_t]
    if control == "noise_rich_control":
        proposal = rng.integers(0, q, size=x.shape, dtype=np.int16)
    elif control == "collapse_attractor_control":
        proposal = np.where(rng.random(size=x.shape) < 0.25 + 0.55 * lam, 0, x)
    else:
        relation_mix = np.clip(0.25 + 0.65 * rho, 0, 1)
        influence = np.where(rng.random(size=x.shape) < relation_mix, neigh, x)
        a = 0.0 if control == "symmetric_transition_control" else alpha
        p_forward = 0.12 + 0.30 * a
        p_reverse = 0.12 * (1.0 - a)
        p_stay = max(0.05, 1.0 - p_forward - p_reverse)
        step = rng.choice(np.array([-1, 0, 1], dtype=np.int16), size=x.shape, p=[p_reverse, p_stay, p_forward])
        proposal = (influence + step) % q
        stay = 0.92 if control == "relation_lock_in_control" else np.clip(0.15 + 0.72 * lam, 0.05, 0.94)
        proposal = np.where(rng.random(size=x.shape) < stay, influence, proposal)
    return proposal.astype(np.int16), src


def simulate(rho: float, alpha: float, lam: float, T: int, cfg: Config, seed: int, control: str) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(151_000 + seed * 1009 + int(100 * rho) * 31 + int(100 * alpha) * 17 + int(100 * lam) * 13 + T)
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
        x, src = transition_step(x, memory, src, rho, alpha, lam, control, rng, q)
        sources[t] = src
        memory = traj[t]
        traj[t + 1] = x
    return {"traj": traj, "sources": sources}


def continue_from(
    x0: np.ndarray,
    steps: int,
    rho: float,
    alpha: float,
    lam: float,
    cfg: Config,
    seed: int,
    control: str,
) -> np.ndarray:
    rng = np.random.default_rng(199_000 + seed * 1009 + steps * 17 + len(x0))
    x = x0.copy()
    memory = x.copy()
    src = fixed_sources(cfg.n_sites)
    for _ in range(steps):
        x_next, src = transition_step(x, memory, src, rho, alpha, lam, control, rng, cfg.q)
        memory = x
        x = x_next
    return x


def viable_mask(traj: np.ndarray, control: str) -> np.ndarray:
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


def relation_scores(tv: np.ndarray, sources: np.ndarray, seed: int, cfg: Config) -> dict[str, float]:
    rng = np.random.default_rng(152_000 + seed)
    self_scores = []
    rel_scores = []
    shuffle_scores = []
    T = sources.shape[0]
    for t in range(T):
        shuffled = rng.permutation(sources[t])
        for i, j in enumerate(sources[t]):
            target = tv[t + 1, :, i]
            self_key = tv[t, :, i]
            rel_key = self_key.astype(np.int64) * 17 + tv[t, :, j]
            shuffle_key = self_key.astype(np.int64) * 17 + tv[t, :, shuffled[i]]
            self_scores.append(prediction_accuracy(self_key, target))
            rel_scores.append(prediction_accuracy(rel_key, target))
            shuffle_scores.append(prediction_accuracy(shuffle_key, target))
    rel = float(np.mean(rel_scores))
    self_only = float(np.mean(self_scores))
    shuffled = float(np.mean(shuffle_scores))
    return {
        "relation_conditioned_score": rel,
        "self_only_score": self_only,
        "independent_score": shuffled,
        "relation_slack_excess": rel - max(self_only, shuffled),
        "relation_shuffle_delta": rel - shuffled,
    }


def base_metrics(sim: dict[str, np.ndarray], rho: float, alpha: float, lam: float, cfg: Config, seed: int, control: str) -> dict[str, float]:
    traj = sim["traj"]
    sources = sim["sources"]
    viable = viable_mask(traj, control)
    p_viable = float(np.mean(viable))
    collapse_rate = float(np.mean(np.any(np.all(traj == 0, axis=2), axis=0)))
    if not np.any(viable):
        return empty_metrics(p_viable, collapse_rate)
    tv = traj[:, viable]
    T = sources.shape[0]
    mid_t = max(1, T // 2)
    raw_alt = float(len(np.unique(row_codes(tv[mid_t]))))
    future_codes = future_signature(tv[-1], tv[0], tv[mid_t], cfg.q)
    future_distinct = float(len(np.unique(future_codes)))
    future_ratio = float(future_distinct / max(raw_alt, 1.0))
    _, counts = np.unique(future_codes, return_counts=True)
    basin_concentration = float(np.max(counts) / np.sum(counts)) if len(counts) else 1.0
    future_entropy = entropy(future_codes)
    closure_rate = float(np.mean(tv[-1] == tv[mid_t]))
    relation = relation_scores(tv, sources, seed, cfg)
    rng = np.random.default_rng(153_000 + seed)
    sample_count = min(cfg.perturbation_samples, tv.shape[1])
    sample_idx = rng.choice(tv.shape[1], sample_count, replace=False)
    mid = tv[mid_t, sample_idx].copy()
    pert = mid.copy()
    cols = rng.integers(0, cfg.n_sites, size=sample_count)
    pert[np.arange(sample_count), cols] = (pert[np.arange(sample_count), cols] + 1) % cfg.q
    pert_final = continue_from(pert, T - mid_t, rho, alpha, lam, cfg, seed, control)
    orig_final = tv[-1, sample_idx]
    pert_codes = future_signature(pert_final, tv[0, sample_idx], mid, cfg.q)
    orig_codes = future_signature(orig_final, tv[0, sample_idx], mid, cfg.q)
    return_same = float(np.mean(pert_codes == orig_codes))
    post_distinct = float(len(np.unique(pert_codes)) / max(sample_count, 1))
    _, pert_counts = np.unique(pert_codes, return_counts=True)
    attractor_concentration = float(np.max(pert_counts) / np.sum(pert_counts)) if len(pert_counts) else 1.0
    branching_after_recovery = entropy(pert_codes) / max(math.log2(max(sample_count, 2)), 1e-9)
    dynamic_lock = float(np.clip(return_same * attractor_concentration * (1.0 - future_ratio), 0.0, 1.0))
    transition_directionality = directional_score(tv, sources, cfg.q)
    return {
        "p_viable": p_viable,
        "collapse_rate": collapse_rate,
        "closure_rate": closure_rate,
        "raw_alternative_count": raw_alt,
        "future_distinct_alternative_count": future_distinct,
        "future_distinct_ratio": future_ratio,
        "future_basin_concentration": basin_concentration,
        "future_profile_entropy": future_entropy,
        "return_to_same_attractor_rate": return_same,
        "post_perturbation_future_distinctness": post_distinct,
        "branching_after_recovery": branching_after_recovery,
        "attractor_concentration": attractor_concentration,
        "dynamic_lock_in_index": dynamic_lock,
        "transition_directionality_score": transition_directionality,
        **relation,
    }


def empty_metrics(p_viable: float, collapse_rate: float) -> dict[str, float]:
    return {
        "p_viable": p_viable,
        "collapse_rate": collapse_rate,
        "closure_rate": 0.0,
        "raw_alternative_count": 0.0,
        "future_distinct_alternative_count": 0.0,
        "future_distinct_ratio": 0.0,
        "future_basin_concentration": 1.0,
        "future_profile_entropy": 0.0,
        "return_to_same_attractor_rate": 1.0,
        "post_perturbation_future_distinctness": 0.0,
        "branching_after_recovery": 0.0,
        "attractor_concentration": 1.0,
        "dynamic_lock_in_index": 1.0,
        "transition_directionality_score": 0.0,
        "relation_conditioned_score": 0.0,
        "self_only_score": 0.0,
        "independent_score": 0.0,
        "relation_slack_excess": 0.0,
        "relation_shuffle_delta": 0.0,
    }


def directional_score(tv: np.ndarray, sources: np.ndarray, q: int) -> float:
    del sources
    diffs = (tv[1:] - tv[:-1]) % q
    forward = float(np.mean(diffs == 1))
    reverse = float(np.mean(diffs == q - 1))
    return forward - reverse


def diagnostic_task(task_def: tuple[dict[str, object], int, int, Config]) -> dict[str, object]:
    target, T, seed, cfg = task_def
    rho = float(target["rho_relation_persistence"])
    alpha = float(target["alpha_asymmetry_strength"])
    lam = float(target["lambda_constraint_pressure"])
    control = str(target["control"])
    base = simulate(rho, alpha, lam, T, cfg, seed, control)
    sym_control = "symmetric_transition_control" if not control else control
    sym = simulate(rho, 0.0, lam, T, cfg, seed + 40_000, sym_control)
    original = base_metrics(base, rho, alpha, lam, cfg, seed, control)
    sym_metrics = base_metrics(sym, rho, 0.0, lam, cfg, seed + 40_000, sym_control)
    row = {
        **target,
        "T": T,
        "seed": seed,
        **original,
        "asymmetric_slack_delta": original["future_distinct_ratio"] - sym_metrics["future_distinct_ratio"],
        "asymmetric_relation_lineage_delta": original["relation_conditioned_score"] - sym_metrics["relation_conditioned_score"],
        "symmetrized_future_distinct_ratio": sym_metrics["future_distinct_ratio"],
        "symmetrized_relation_score": sym_metrics["relation_conditioned_score"],
    }
    row["classification"] = classify(row)
    return row


def classify(row: dict[str, float]) -> str:
    asymmetry_margin = 0.01
    relation_margin = 0.001
    if row["p_viable"] <= 0.05 or (row["closure_rate"] < 0.12 and row["relation_slack_excess"] <= 0):
        return "underconstrained"
    if row["collapse_rate"] > 0.05 or row["dynamic_lock_in_index"] >= 0.20 or row["future_basin_concentration"] >= 0.50:
        return "lock_in"
    apparent = row["raw_alternative_count"] > 100 and (
        row["asymmetric_slack_delta"] <= asymmetry_margin
        or row["relation_slack_excess"] <= relation_margin
        or row["future_distinct_ratio"] < 0.10
    )
    if apparent:
        return "apparent_slack"
    if row["relation_slack_excess"] > relation_margin and row["asymmetric_slack_delta"] > asymmetry_margin and row["future_distinct_ratio"] >= 0.10 and row["dynamic_lock_in_index"] < 0.20:
        return "viable_slack_candidate"
    if row["raw_alternative_count"] > 100:
        return "apparent_slack"
    return "mixed_or_inconclusive"


def bootstrap(df: pd.DataFrame, metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(160_000)
    rows = []
    for key, group in df.groupby(["target", "T"], dropna=False):
        target, T = key
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            mean = float(np.mean(vals))
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            rows.append({"target": target, "T": T, "metric": metric, "mean": mean, "ci_low": float(lo), "ci_high": float(hi), "n_seeds": int(len(seeds))})
    return pd.DataFrame(rows)


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_rows.csv")
    means = raw.groupby(
        ["target", "target_kind", "control", "rho_relation_persistence", "alpha_asymmetry_strength", "lambda_constraint_pressure", "T"],
        as_index=False,
        dropna=False,
    ).mean(numeric_only=True)
    means["control"] = means["control"].fillna("")
    means["classification"] = means.apply(lambda r: classify(r.to_dict()), axis=1)
    pd.DataFrame(diagnostic_targets()).to_csv(out / "diagnostic_targets.csv", index=False)
    means[["target", "T", "asymmetric_slack_delta", "asymmetric_relation_lineage_delta", "transition_directionality_score", "symmetrized_future_distinct_ratio", "symmetrized_relation_score"]].to_csv(out / "asymmetry_load_bearing.csv", index=False)
    means[["target", "T", "relation_conditioned_score", "self_only_score", "independent_score", "relation_slack_excess", "relation_shuffle_delta"]].to_csv(out / "relation_load_bearing.csv", index=False)
    means[["target", "T", "raw_alternative_count", "future_distinct_alternative_count", "future_distinct_ratio", "future_basin_concentration", "future_profile_entropy"]].to_csv(out / "future_distinct_alternatives.csv", index=False)
    means[["target", "T", "return_to_same_attractor_rate", "post_perturbation_future_distinctness", "branching_after_recovery", "attractor_concentration", "dynamic_lock_in_index"]].to_csv(out / "dynamic_lock_in.csv", index=False)
    profile_cols = [
        "target", "target_kind", "T", "p_viable", "closure_rate", "raw_alternative_count",
        "future_distinct_alternative_count", "future_distinct_ratio", "asymmetric_slack_delta",
        "relation_slack_excess", "relation_shuffle_delta", "dynamic_lock_in_index",
        "post_perturbation_future_distinctness", "classification",
    ]
    means[profile_cols].to_csv(out / "viable_slack_diagnostic_profile.csv", index=False)
    means[["target", "target_kind", "T", "classification"]].to_csv(out / "classification_results.csv", index=False)
    controls = means[means["target_kind"] == "control"].copy()
    controls[["target", "T", "classification", "future_distinct_ratio", "relation_slack_excess", "asymmetric_slack_delta", "dynamic_lock_in_index"]].to_csv(out / "control_rejection.csv", index=False)
    boot_metrics = ["future_distinct_ratio", "asymmetric_slack_delta", "relation_slack_excess", "relation_shuffle_delta", "dynamic_lock_in_index"]
    bootstrap(raw, boot_metrics, cfg.bootstrap_repeats).to_csv(out / "bootstrap_intervals.csv", index=False)
    est = means[["target", "T", "p_viable", "raw_alternative_count", "future_distinct_ratio", "dynamic_lock_in_index", "classification"]].copy()
    est["estimator_warning"] = np.where(est["p_viable"] <= 0.05, "LOW_VIABILITY", "")
    est.to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, means)
    summary = make_summary(cfg, started, means)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def make_summary(cfg: Config, started: float, means: pd.DataFrame) -> dict[str, object]:
    agg = means.groupby(["target", "target_kind", "control", "rho_relation_persistence", "alpha_asymmetry_strength", "lambda_constraint_pressure"], as_index=False, dropna=False).mean(numeric_only=True)
    agg["control"] = agg["control"].fillna("")
    agg["classification"] = agg.apply(lambda r: classify(r.to_dict()), axis=1)
    candidates = agg[agg["target_kind"] != "control"].copy()
    candidates["diagnostic_score"] = (
        candidates["future_distinct_ratio"]
        + 20.0 * candidates["relation_slack_excess"]
        + 2.0 * candidates["asymmetric_slack_delta"]
        - candidates["dynamic_lock_in_index"]
        - 0.25 * candidates["future_basin_concentration"]
    )
    best = candidates.sort_values("diagnostic_score", ascending=False).iloc[0]
    extreme = candidates[candidates["target"] == "da1_extreme_best"].iloc[0]
    control_rows = means[means["target_kind"] == "control"].copy()
    controls = {}
    for name, group in control_rows.groupby("target"):
        labels = set(group["classification"].astype(str))
        controls[str(name)] = "viable_slack_candidate" if "viable_slack_candidate" in labels else str(group["classification"].mode().iloc[0])
    middle = candidates[candidates["target_kind"] == "middle"]
    middle_candidate_beats_extreme = bool(middle["diagnostic_score"].max() > float(extreme["diagnostic_score"]))
    relation_lock_rejected = controls.get("relation_lock_in_control") != "viable_slack_candidate"
    symmetric_rejected = controls.get("symmetric_transition_control") != "viable_slack_candidate"
    pass_all = bool(
        relation_lock_rejected
        and symmetric_rejected
        and middle_candidate_beats_extreme
        and best["relation_slack_excess"] > 0
        and best["asymmetric_slack_delta"] > 0
        and best["dynamic_lock_in_index"] < float(agg.loc[agg["target"] == "relation_lock_in_control", "dynamic_lock_in_index"].mean())
    )
    if pass_all:
        recommendation = "DA1b separates viable slack from apparent slack; proceed to DA2."
        next_probe = "DA2_distinction_lineage_through_viable_slack"
    elif not relation_lock_rejected:
        recommendation = "DA1b still lets lock-in pass; refine future-distinct alternatives before scaling."
        next_probe = "DA1c_future_distinct_lockin_revision"
    elif not symmetric_rejected:
        recommendation = "DA1b still lets symmetric dynamics pass; revise transition or directional filtering."
        next_probe = "DA1c_asymmetry_load_bearing_revision"
    elif not middle_candidate_beats_extreme:
        recommendation = "DA1b rejects controls but the extreme remains strongest; rethink the middle-phase world design."
        next_probe = "DA1_world_revision"
    else:
        recommendation = "DA1b is mixed; inspect diagnostic profiles before scaling."
        next_probe = "DA1b_targeted_followup"
    warnings = sorted(agg.loc[agg["p_viable"] <= 0.05, "target"].unique().tolist())
    return {
        "probe": "DA1b_apparent_vs_viable_slack",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "targets": sorted(agg["target"].unique().tolist()),
        "best_candidate": {
            "name": str(best["target"]),
            "rho_relation_persistence": float(best["rho_relation_persistence"]),
            "alpha_asymmetry_strength": float(best["alpha_asymmetry_strength"]),
            "lambda_constraint_pressure": float(best["lambda_constraint_pressure"]),
            "classification": str(best["classification"]),
        },
        "diagnostic_result": {
            "relation_lock_in_rejected": bool(relation_lock_rejected),
            "symmetric_transition_rejected": bool(symmetric_rejected),
            "middle_candidate_beats_extreme": bool(middle_candidate_beats_extreme),
            "future_distinct_slack_detected": bool(best["future_distinct_ratio"] >= 0.10),
            "relation_slack_excess_positive": bool(best["relation_slack_excess"] > 0),
            "asymmetric_slack_delta_positive": bool(best["asymmetric_slack_delta"] > 0),
        },
        "best_profile": {
            "p_viable": float(best["p_viable"]),
            "closure_rate": float(best["closure_rate"]),
            "raw_alternative_count": float(best["raw_alternative_count"]),
            "future_distinct_alternative_count": float(best["future_distinct_alternative_count"]),
            "future_distinct_ratio": float(best["future_distinct_ratio"]),
            "asymmetric_slack_delta": float(best["asymmetric_slack_delta"]),
            "relation_slack_excess": float(best["relation_slack_excess"]),
            "relation_shuffle_delta": float(best["relation_shuffle_delta"]),
            "dynamic_lock_in_index": float(best["dynamic_lock_in_index"]),
            "post_perturbation_future_distinctness": float(best["post_perturbation_future_distinctness"]),
        },
        "control_results": controls,
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": warnings,
    }


def make_plots(out: Path, means: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    agg = means.groupby(["target", "target_kind"], as_index=False).mean(numeric_only=True)
    labels = agg["target"].str.replace("_control", "").str.replace("middle_", "m_").str.replace("optional_", "o_")
    x = np.arange(len(agg))
    for metric, fname, ylabel in [
        ("future_distinct_ratio", "future_distinct_ratio_by_target.png", "future distinct ratio"),
        ("dynamic_lock_in_index", "dynamic_lock_in_by_target.png", "dynamic lock-in index"),
        ("asymmetric_slack_delta", "asymmetry_slack_delta_by_target.png", "asymmetry slack delta"),
        ("relation_slack_excess", "relation_slack_excess_by_target.png", "relation slack excess"),
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
    ax.scatter(agg["raw_alternative_count"], agg["future_distinct_alternative_count"], c=(agg["target_kind"] == "control").astype(int))
    ax.set_xlabel("raw alternatives")
    ax.set_ylabel("future-distinct alternatives")
    fig.tight_layout()
    fig.savefig(out / "raw_vs_future_distinct_alternatives.png", dpi=160)
    plt.close(fig)
    class_order = {"underconstrained": 0, "apparent_slack": 1, "mixed_or_inconclusive": 2, "lock_in": 3, "viable_slack_candidate": 4}
    heat = means.pivot_table(index="target", columns="T", values="classification", aggfunc=lambda s: class_order.get(str(s.iloc[0]), 2))
    fig, ax = plt.subplots(figsize=(6, 7))
    im = ax.imshow(heat.to_numpy(), aspect="auto")
    fig.colorbar(im, ax=ax)
    ax.set_yticks(np.arange(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=7)
    ax.set_xticks(np.arange(len(heat.columns)))
    ax.set_xticklabels(heat.columns)
    fig.tight_layout()
    fig.savefig(out / "classification_heatmap.png", dpi=160)
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
    tasks = [(target, T, seed, cfg) for target in diagnostic_targets() for T in cfg.horizons for seed in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(diagnostic_task, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            append_row(raw, fut.result())
            if i % max(1, cfg.workers * 5) == 0:
                print(json.dumps({"completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started)
    print("PROBE DA1b: APPARENT VS VIABLE SLACK")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
