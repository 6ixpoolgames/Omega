#!/usr/bin/env python
"""Probe T1: viable trajectory geometry.

This probe tests the T0-selected trajectory-geometry branch. It asks whether
viable trajectories retain non-degenerate, temporally structured,
component-preserving geometry that is not just survival, endpoint spread, noise,
or one-component erasure.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

import probe_11_learned_predictive_kappa_revised as p11


SEGMENT_COUNT = 6
BASE_CONDITIONS = ["coupled", "product", "shuffled", "time_shuffled", "independent_alpha0"]
FALSE_CONTROLS = ["rigid_collapse", "noise_fakeout", "single_component_erasure"]
MAIN_ALPHAS = [0.45, 0.50, 0.525]
MAIN_HORIZONS = [900, 1500, 2400]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seed_count: int
    bootstrap_repeats: int
    soft_limit_seconds: float
    hard_limit_seconds: float
    use_gpu: bool
    smoke: bool
    sample_per_seed: int
    pairwise_sample: int
    gpu_pause_temp: int
    gpu_resume_temp: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_T1_viable_trajectory_geometry_results"))
    p.add_argument("--workers", type=int, default=18)
    p.add_argument("--n-traj", type=int, default=15000)
    p.add_argument("--seed-count", type=int, default=180)
    p.add_argument("--bootstrap-repeats", type=int, default=300)
    p.add_argument("--soft-limit-sec", type=float, default=5400)
    p.add_argument("--hard-limit-sec", type=float, default=7200)
    p.add_argument("--sample-per-seed", type=int, default=1500)
    p.add_argument("--pairwise-sample", type=int, default=4096)
    p.add_argument("--gpu-pause-temp", type=int, default=82)
    p.add_argument("--gpu-resume-temp", type=int, default=75)
    p.add_argument("--no-gpu", action="store_true")
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 6)
        args.n_traj = min(args.n_traj, 1000)
        args.seed_count = min(args.seed_count, 8)
        args.bootstrap_repeats = min(args.bootstrap_repeats, 50)
        args.sample_per_seed = min(args.sample_per_seed, 400)
        args.pairwise_sample = min(args.pairwise_sample, 1200)
    return Config(
        out_dir=args.out_dir,
        workers=args.workers,
        n_traj=args.n_traj,
        seed_count=args.seed_count,
        bootstrap_repeats=args.bootstrap_repeats,
        soft_limit_seconds=args.soft_limit_sec,
        hard_limit_seconds=args.hard_limit_sec,
        use_gpu=not args.no_gpu,
        smoke=args.smoke,
        sample_per_seed=args.sample_per_seed,
        pairwise_sample=args.pairwise_sample,
        gpu_pause_temp=args.gpu_pause_temp,
        gpu_resume_temp=args.gpu_resume_temp,
    )


def ensure_cuda_dll_path() -> None:
    torch_lib = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages" / "torch" / "lib"
    if not torch_lib.exists():
        return
    torch_lib_s = str(torch_lib)
    if torch_lib_s not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = torch_lib_s + os.pathsep + os.environ.get("PATH", "")
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(torch_lib_s)
        except OSError:
            pass


def gpu_temp_c() -> int | None:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return int(out.strip().splitlines()[0])
    except Exception:
        return None


def wait_for_gpu(cfg: Config) -> tuple[int | None, int]:
    pauses = 0
    temp = gpu_temp_c()
    if not cfg.use_gpu or temp is None or temp < cfg.gpu_pause_temp:
        return temp, pauses
    while temp is not None and temp > cfg.gpu_resume_temp:
        pauses += 1
        print(json.dumps({"gpu_thermal_pause": True, "temp_c": temp}), flush=True)
        time.sleep(10)
        temp = gpu_temp_c()
    return temp, pauses


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def simulate_multi(alpha: float, horizon: int, seed: int, condition: str, n: int) -> dict[str, np.ndarray]:
    cfg = p11.Config(Path("_unused"), 1, n, 1, seed, 1, 1, 1, 0.018, 0.055, 0.085, 1, 1, 1, 1000, 100, False)
    perturb = p11.Perturbation("reference_000", "reference", "reference", "test")
    if condition == "coupled":
        block = p11.simulate(alpha, horizon, seed, cfg, perturb, True, False)
    elif condition == "product":
        block = p11.simulate(0.0, horizon, seed + 20_000, cfg, perturb, False, False)
    elif condition == "shuffled":
        block = p11.simulate(0.0, horizon, seed + 40_000, cfg, perturb, False, True)
    elif condition == "independent_alpha0":
        block = p11.simulate(0.0, horizon, seed + 60_000, cfg, perturb, False, False)
    elif condition == "time_shuffled":
        block = p11.simulate(alpha, horizon, seed + 80_000, cfg, perturb, True, False)
        perm = np.random.default_rng(80_000 + seed).permutation(SEGMENT_COUNT + 1)
        block = {**block, "a": block["a"][perm], "b": block["b"][perm]}
    else:
        raise KeyError(condition)
    return {
        "traj": np.stack([block["a"], block["b"]], axis=2).astype(np.float32),
        "alive_seg": block["alive_seg"],
        "alive_final": block["alive_final"],
    }


def sample_viable(traj: np.ndarray, alive: np.ndarray, seed: int, sample_per_seed: int) -> np.ndarray:
    idx = np.flatnonzero(alive)
    if len(idx) == 0:
        return np.empty((0, traj.shape[0], traj.shape[2]), dtype=np.float32)
    rng = np.random.default_rng(910_000 + seed)
    take = rng.choice(idx, size=min(sample_per_seed, len(idx)), replace=False)
    return np.transpose(traj[:, take, :], (1, 0, 2)).astype(np.float32)


def survival_metrics(alive_seg: np.ndarray) -> dict[str, float]:
    survival = alive_seg.mean(axis=1)
    hazard = []
    for i in range(1, len(survival)):
        prev = max(float(survival[i - 1]), 1e-12)
        hazard.append(max(0.0, float((survival[i - 1] - survival[i]) / prev)))
    return {
        "p_viable_T": float(survival[-1]),
        "survival_initial": float(survival[0]),
        "survival_mid": float(survival[len(survival) // 2]),
        "mean_hazard": float(np.mean(hazard)),
        "late_hazard": float(np.mean(hazard[-2:])),
    }


def cheap_seed_geometry(sample: np.ndarray) -> dict[str, float]:
    if len(sample) < 4:
        return {
            "seed_effective_rank": 0.0,
            "seed_distance": 0.0,
            "seed_component_rank_balance": 0.0,
            "seed_component_distance_balance": 0.0,
        }
    flat = sample.reshape(len(sample), -1)
    eff, _, dist = cpu_geometry(flat, min(256, len(sample)))
    a = sample[:, :, 0]
    b = sample[:, :, 1]
    eff_a, _, dist_a = cpu_geometry(a, min(256, len(a)))
    eff_b, _, dist_b = cpu_geometry(b, min(256, len(b)))
    return {
        "seed_effective_rank": eff,
        "seed_distance": dist,
        "seed_component_rank_balance": safe_ratio(min(eff_a, eff_b), max(eff_a, eff_b)),
        "seed_component_distance_balance": safe_ratio(min(dist_a, dist_b), max(dist_a, dist_b)),
    }


def cpu_geometry(flat: np.ndarray, pairwise_sample: int) -> tuple[float, float, float]:
    x = flat.astype(np.float64)
    x = x - x.mean(axis=0, keepdims=True)
    cov = (x.T @ x) / max(len(x) - 1, 1)
    eig = np.maximum(np.linalg.eigvalsh(cov), 0.0)
    total = float(eig.sum() + 1e-12)
    p = eig / total
    eff = float(np.exp(-np.sum(p * np.log(np.maximum(p, 1e-12)))))
    top_frac = float(eig[-1] / total) if len(eig) else 0.0
    take = np.linspace(0, len(x) - 1, min(pairwise_sample, len(x))).astype(int)
    xs = x[take]
    norms = np.sum(xs * xs, axis=1)
    dist2 = np.maximum(norms[:, None] + norms[None, :] - 2 * (xs @ xs.T), 0.0)
    dist = np.sqrt(dist2 + 1e-9)
    mean_dist = float(np.mean(dist))
    return eff, top_frac, mean_dist


def task(task_def: tuple[float, int, str, int, Config, str]) -> dict[str, object]:
    alpha, horizon, condition, seed, cfg, sample_dir_s = task_def
    block = simulate_multi(alpha, horizon, seed, condition, cfg.n_traj)
    sample = sample_viable(block["traj"], block["alive_final"], seed, cfg.sample_per_seed)
    sample_path = Path(sample_dir_s) / f"a{alpha:.3f}_T{horizon}_{condition}_seed{seed:04d}.npz"
    np.savez_compressed(sample_path, sample=sample)
    row = {
        "world": "F_T_attractive",
        "condition": condition,
        "alpha": alpha,
        "T": horizon,
        "seed": seed,
        "sample_path": str(sample_path),
        "sample_n": int(len(sample)),
        **survival_metrics(block["alive_seg"]),
        **cheap_seed_geometry(sample),
    }
    return row


def control_sample(sample: np.ndarray, control: str, seed: int) -> np.ndarray:
    if len(sample) == 0:
        return sample
    rng = np.random.default_rng(1_300_000 + seed + abs(hash(control)) % 1000)
    out = sample.copy()
    if control == "rigid_collapse":
        means = out.mean(axis=0, keepdims=True)
        out = means + 0.03 * (out - means)
    elif control == "noise_fakeout":
        flat = out.reshape(len(out), -1)
        std = flat.std(axis=0, keepdims=True)
        mean = flat.mean(axis=0, keepdims=True)
        out = (mean + rng.normal(size=flat.shape) * std).reshape(out.shape).astype(np.float32)
    elif control == "single_component_erasure":
        means = out[:, :, 1].mean(axis=0, keepdims=True)
        out[:, :, 1] = means + 0.03 * (out[:, :, 1] - means)
    else:
        raise KeyError(control)
    return out.astype(np.float32)


def load_group(seed_rows: pd.DataFrame, max_rows: int | None = None) -> np.ndarray:
    chunks = []
    for _, row in seed_rows.iterrows():
        arr = np.load(row["sample_path"])["sample"]
        if len(arr):
            chunks.append(arr)
    if not chunks:
        return np.empty((0, SEGMENT_COUNT + 1, 2), dtype=np.float32)
    data = np.concatenate(chunks, axis=0)
    if max_rows and len(data) > max_rows:
        idx = np.random.default_rng(70_707).choice(len(data), max_rows, replace=False)
        data = data[idx]
    return data.astype(np.float32)


def safe_ratio(a: float, b: float) -> float:
    if b <= 1e-12:
        return 0.0
    return float(np.clip(a / b, 0.0, 1.0))


def gpu_geometry(sample: np.ndarray, cfg: Config, label: dict[str, object], control: str | None) -> tuple[dict[str, float], dict[str, object]]:
    started = time.monotonic()
    temp0, pauses = wait_for_gpu(cfg)
    gpu_used = False
    max_temp = temp0 if temp0 is not None else np.nan
    try:
        if not cfg.use_gpu:
            raise RuntimeError("GPU disabled")
        ensure_cuda_dll_path()
        import cupy as cp

        x = cp.asarray(sample.reshape(len(sample), -1), dtype=cp.float32)
        metrics = geometry_from_gpu_matrix(cp, x, cfg.pairwise_sample, "full")
        early = cp.asarray(sample[:, :3, :].reshape(len(sample), -1), dtype=cp.float32)
        middle = cp.asarray(sample[:, 2:5, :].reshape(len(sample), -1), dtype=cp.float32)
        late = cp.asarray(sample[:, 4:, :].reshape(len(sample), -1), dtype=cp.float32)
        ge = geometry_from_gpu_matrix(cp, early, cfg.pairwise_sample, "early")
        gm = geometry_from_gpu_matrix(cp, middle, cfg.pairwise_sample, "middle")
        gl = geometry_from_gpu_matrix(cp, late, cfg.pairwise_sample, "late")
        ga = geometry_from_gpu_matrix(cp, cp.asarray(sample[:, :, 0], dtype=cp.float32), cfg.pairwise_sample, "A")
        gb = geometry_from_gpu_matrix(cp, cp.asarray(sample[:, :, 1], dtype=cp.float32), cfg.pairwise_sample, "B")
        cp.cuda.Stream.null.synchronize()
        gpu_used = True
    except Exception:
        metrics = geometry_from_cpu_matrix(sample.reshape(len(sample), -1), cfg.pairwise_sample, "full")
        ge = geometry_from_cpu_matrix(sample[:, :3, :].reshape(len(sample), -1), cfg.pairwise_sample, "early")
        gm = geometry_from_cpu_matrix(sample[:, 2:5, :].reshape(len(sample), -1), cfg.pairwise_sample, "middle")
        gl = geometry_from_cpu_matrix(sample[:, 4:, :].reshape(len(sample), -1), cfg.pairwise_sample, "late")
        ga = geometry_from_cpu_matrix(sample[:, :, 0], cfg.pairwise_sample, "A")
        gb = geometry_from_cpu_matrix(sample[:, :, 1], cfg.pairwise_sample, "B")
    temp1 = gpu_temp_c()
    if temp1 is not None and (not np.isfinite(max_temp) or temp1 > max_temp):
        max_temp = temp1
    component_rank_balance = safe_ratio(min(ga["effective_rank_A"], gb["effective_rank_B"]), max(ga["effective_rank_A"], gb["effective_rank_B"]))
    component_distance_balance = safe_ratio(
        min(ga["mean_pairwise_distance_sketch_A"], gb["mean_pairwise_distance_sketch_B"]),
        max(ga["mean_pairwise_distance_sketch_A"], gb["mean_pairwise_distance_sketch_B"]),
    )
    out = {
        **label,
        "control": control or "none",
        "sample_n": int(len(sample)),
        **metrics,
        **ge,
        **gm,
        **gl,
        **ga,
        **gb,
        "rank_retention_late_over_early": safe_ratio(gl["effective_rank_late"], ge["effective_rank_early"]),
        "segment_geometry_drift": float(abs(gl["effective_rank_late"] - ge["effective_rank_early"])),
        "component_rank_balance": component_rank_balance,
        "component_distance_balance": component_distance_balance,
        "component_erasure_score": 1.0 - min(component_rank_balance, component_distance_balance),
        "gpu_used": float(gpu_used),
    }
    timing = {
        **label,
        "control": control or "none",
        "sample_n": int(len(sample)),
        "gpu_used": float(gpu_used),
        "batch_seconds": round(time.monotonic() - started, 4),
        "start_temp_c": temp0,
        "end_temp_c": temp1,
        "max_temp_c": max_temp,
        "thermal_pause_events": pauses,
    }
    return out, timing


def geometry_from_gpu_matrix(cp, matrix, pairwise_sample: int, suffix: str) -> dict[str, float]:
    if int(matrix.shape[0]) < 3:
        key = suffix if suffix != "full" else ""
        return metric_names(key, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)
    x = matrix - cp.mean(matrix, axis=0, keepdims=True)
    cov = (x.T @ x) / max(int(x.shape[0]) - 1, 1)
    eig = cp.maximum(cp.linalg.eigvalsh(cov), 0)
    total = cp.sum(eig) + 1e-12
    p = eig / total
    eff = float(cp.exp(-cp.sum(p * cp.log(cp.maximum(p, 1e-12)))).get())
    entropy = float((-cp.sum(p * cp.log(cp.maximum(p, 1e-12)))).get())
    top_frac = float((eig[-1] / total).get())
    sample_n = min(pairwise_sample, int(x.shape[0]))
    idx = cp.linspace(0, int(x.shape[0]) - 1, sample_n).astype(cp.int32)
    xs = x[idx]
    norms = cp.sum(xs * xs, axis=1)
    dist2 = cp.maximum(norms[:, None] + norms[None, :] - 2 * (xs @ xs.T), 0)
    dist = cp.sqrt(dist2 + 1e-9)
    dist = dist.copy()
    dist[cp.arange(sample_n), cp.arange(sample_n)] = cp.nan
    key = suffix if suffix != "full" else ""
    return metric_names(key, eff, entropy, top_frac, float(cp.nanmean(dist).get()), float(cp.nanmedian(dist).get()), float(cp.nanmin(dist, axis=1).mean().get()))


def geometry_from_cpu_matrix(matrix: np.ndarray, pairwise_sample: int, suffix: str) -> dict[str, float]:
    if len(matrix) < 3:
        key = suffix if suffix != "full" else ""
        return metric_names(key, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)
    x = matrix.astype(np.float64)
    x = x - x.mean(axis=0, keepdims=True)
    cov = (x.T @ x) / max(len(x) - 1, 1)
    eig = np.maximum(np.linalg.eigvalsh(cov), 0)
    total = float(eig.sum() + 1e-12)
    p = eig / total
    eff = float(np.exp(-np.sum(p * np.log(np.maximum(p, 1e-12)))))
    entropy = float(-np.sum(p * np.log(np.maximum(p, 1e-12))))
    top_frac = float(eig[-1] / total) if len(eig) else 0.0
    idx = np.linspace(0, len(x) - 1, min(pairwise_sample, len(x))).astype(int)
    xs = x[idx]
    norms = np.sum(xs * xs, axis=1)
    dist2 = np.maximum(norms[:, None] + norms[None, :] - 2 * (xs @ xs.T), 0)
    dist = np.sqrt(dist2 + 1e-9)
    np.fill_diagonal(dist, np.nan)
    key = suffix if suffix != "full" else ""
    return metric_names(key, eff, entropy, top_frac, float(np.nanmean(dist)), float(np.nanmedian(dist)), float(np.nanmean(np.nanmin(dist, axis=1))))


def metric_names(suffix: str, eff: float, entropy: float, top_frac: float, mean_dist: float, median_dist: float, nn_dist: float) -> dict[str, float]:
    s = f"_{suffix}" if suffix else ""
    return {
        f"effective_rank{s}": eff,
        f"covariance_spectrum_entropy{s}": entropy,
        f"top_eigenvalue_fraction{s}": top_frac,
        f"mean_pairwise_distance_sketch{s}": mean_dist,
        f"median_pairwise_distance_sketch{s}": median_dist,
        f"nearest_neighbor_distance_sketch{s}": nn_dist,
        f"collapse_score{s}": 1.0 / (1.0 + eff),
    }


def predictive_check(sample: np.ndarray, seed: int) -> dict[str, float]:
    if len(sample) < 40:
        return {"ridge_R2_real": 0.0, "ridge_R2_time_shuffled": 0.0, "predictive_delta": 0.0}
    x = sample[:, :3, :].reshape(len(sample), -1)
    y = sample[:, 3:, :].reshape(len(sample), -1)
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.35, random_state=seed)
    model = Ridge(alpha=1.0)
    model.fit(xtr, ytr)
    r2 = float(max(-1.0, r2_score(yte, model.predict(xte), multioutput="variance_weighted")))
    y_shuf = y[np.random.default_rng(seed + 700).permutation(len(y))]
    xtr, xte, ytr, yte = train_test_split(x, y_shuf, test_size=0.35, random_state=seed)
    model.fit(xtr, ytr)
    r2s = float(max(-1.0, r2_score(yte, model.predict(xte), multioutput="variance_weighted")))
    return {"ridge_R2_real": r2, "ridge_R2_time_shuffled": r2s, "predictive_delta": r2 - r2s}


def bootstrap_intervals(seed_df: pd.DataFrame, repeats: int) -> pd.DataFrame:
    metrics = ["p_viable_T", "seed_effective_rank", "seed_distance", "seed_component_rank_balance", "seed_component_distance_balance"]
    rng = np.random.default_rng(81_001)
    out = []
    groups = ["condition", "alpha", "T"]
    for key, group in seed_df.groupby(groups, dropna=False):
        base = dict(zip(groups, key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            vals = vals[np.isfinite(vals)]
            if len(vals) == 0:
                continue
            boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)]) if len(vals) > 1 else np.array([float(vals[0])])
            lo, hi = np.quantile(boot, [0.025, 0.975])
            out.append({**base, "metric": metric, "mean": float(np.mean(vals)), "ci_low": float(lo), "ci_high": float(hi), "ci_width": float(hi - lo)})
    return pd.DataFrame(out)


def null_deltas(geom: pd.DataFrame) -> pd.DataFrame:
    metrics = ["effective_rank", "covariance_spectrum_entropy", "mean_pairwise_distance_sketch", "collapse_score", "component_rank_balance", "component_distance_balance"]
    rows = []
    base = geom[geom["control"].eq("none")]
    for (alpha, horizon), group in base.groupby(["alpha", "T"], dropna=False):
        coupled = group[group["condition"].eq("coupled")]
        if coupled.empty:
            continue
        c = coupled.iloc[0]
        for condition in ["product", "shuffled", "time_shuffled", "independent_alpha0"]:
            n = group[group["condition"].eq(condition)]
            if n.empty:
                continue
            n = n.iloc[0]
            for metric in metrics:
                rows.append({"alpha": alpha, "T": horizon, "metric": metric, "null": condition, "delta": float(c[metric] - n[metric])})
    return pd.DataFrame(rows)


def make_plots(out: Path, geom: pd.DataFrame, corr: pd.DataFrame, deltas: pd.DataFrame, timing: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    plot_df = geom.copy()
    plot_df["label"] = plot_df["condition"].astype(str) + ":" + plot_df["alpha"].astype(str) + ":T" + plot_df["T"].astype(str) + ":" + plot_df["control"].astype(str)
    for metric, fname, title in [
        ("effective_rank", "effective_rank_by_condition.png", "Effective rank by condition"),
        ("collapse_score", "collapse_score_by_condition.png", "Collapse score by condition"),
        ("rank_retention_late_over_early", "temporal_rank_retention.png", "Temporal rank retention"),
        ("component_rank_balance", "component_balance_by_condition.png", "Component balance"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 6))
        s = plot_df[plot_df["control"].isin(["none", *FALSE_CONTROLS])].sort_values(metric)
        ax.barh(s["label"], s[metric])
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=150)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    none = plot_df[plot_df["control"].eq("none")]
    ax.scatter(none["p_viable_T"], none["effective_rank"], c=none["component_rank_balance"])
    ax.set_xlabel("p_viable_T")
    ax.set_ylabel("effective_rank")
    ax.set_title("Geometry vs viability")
    fig.tight_layout()
    fig.savefig(out / "geometry_vs_viability_scatter.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 6))
    if len(corr):
        im = ax.imshow(corr.to_numpy(float), vmin=-1, vmax=1, cmap="coolwarm")
        ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=90)
        ax.set_yticks(range(len(corr.index)), corr.index)
        fig.colorbar(im, ax=ax)
    ax.set_title("Metric correlation matrix")
    fig.tight_layout()
    fig.savefig(out / "metric_correlation_matrix.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    if len(deltas):
        s = deltas[deltas["metric"].eq("effective_rank")]
        ax.barh(s["null"].astype(str) + ":T" + s["T"].astype(str) + ":" + s["alpha"].astype(str), s["delta"])
    ax.set_title("Null delta forest plot: effective rank")
    fig.tight_layout()
    fig.savefig(out / "null_delta_forest_plot.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(timing)), timing["batch_seconds"])
    ax.set_xlabel("GPU batch")
    ax.set_ylabel("seconds")
    ax.set_title("GPU batch timing")
    fig.tight_layout()
    fig.savefig(out / "gpu_batch_timing.png", dpi=150)
    plt.close(fig)


def summarize(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    seed_df = pd.read_csv(out / "_seed_manifest.csv")
    group_cols = ["condition", "alpha", "T"]
    survival = seed_df.groupby(group_cols, as_index=False).mean(numeric_only=True)
    geom_rows = []
    timing_rows = []
    pred_rows = []
    for key, group in seed_df.groupby(group_cols, dropna=False):
        label = dict(zip(group_cols, key))
        sample = load_group(group)
        geom, timing = gpu_geometry(sample, cfg, label, None)
        geom_rows.append(geom)
        timing_rows.append(timing)
        pred_rows.append({**label, "control": "none", **predictive_check(sample[np.linspace(0, len(sample) - 1, min(25_000, len(sample))).astype(int)] if len(sample) else sample, int(key[1] * 1000 + key[2]))})
        if label["condition"] == "coupled":
            for control in FALSE_CONTROLS:
                c_sample = control_sample(sample, control, int(label["alpha"] * 1000 + label["T"]))
                geom, timing = gpu_geometry(c_sample, cfg, label, control)
                geom_rows.append(geom)
                timing_rows.append(timing)
    geom = pd.DataFrame(geom_rows).merge(survival[group_cols + ["p_viable_T", "mean_hazard", "late_hazard"]], on=group_cols, how="left")
    timing = pd.DataFrame(timing_rows)
    pred = pd.DataFrame(pred_rows)
    boot = bootstrap_intervals(seed_df, cfg.bootstrap_repeats)
    deltas = null_deltas(geom)
    metric_cols = [
        "p_viable_T", "effective_rank", "covariance_spectrum_entropy", "top_eigenvalue_fraction",
        "mean_pairwise_distance_sketch", "collapse_score", "rank_retention_late_over_early",
        "component_rank_balance", "component_distance_balance", "component_erasure_score",
    ]
    corr = geom[geom["control"].eq("none")][metric_cols].corr(numeric_only=True)
    geom.to_csv(out / "geometry_metrics.csv", index=False)
    geom[["condition", "alpha", "T", "control", "effective_rank_early", "effective_rank_middle", "effective_rank_late", "rank_retention_late_over_early", "segment_geometry_drift"]].to_csv(out / "temporal_geometry.csv", index=False)
    geom[["condition", "alpha", "T", "control", "effective_rank_A", "effective_rank_B", "mean_pairwise_distance_sketch_A", "mean_pairwise_distance_sketch_B", "component_rank_balance", "component_distance_balance", "component_erasure_score"]].to_csv(out / "component_balance.csv", index=False)
    deltas.to_csv(out / "null_deltas.csv", index=False)
    corr.to_csv(out / "metric_correlations.csv")
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    timing.to_csv(out / "gpu_timing_diagnostics.csv", index=False)
    pred.to_csv(out / "predictive_check.csv", index=False)
    geom[["condition", "alpha", "T", "control", "sample_n", "gpu_used", "effective_rank", "component_rank_balance", "rank_retention_late_over_early", "p_viable_T"]].to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, geom, corr, deltas, timing)
    none = geom[geom["control"].eq("none")]
    false = geom[geom["control"].ne("none")]
    coupled = none[none["condition"].eq("coupled")]
    p_corr = float(abs(none["effective_rank"].corr(none["p_viable_T"]))) if len(none) > 2 else np.nan
    component_pass = bool((coupled["component_rank_balance"].min() > 0.65) and (coupled["component_distance_balance"].min() > 0.65))
    temporal_pass = bool((coupled["rank_retention_late_over_early"].min() > 0.70) and (false[false["control"].eq("rigid_collapse")]["effective_rank"].max() < coupled["effective_rank"].median()))
    false_scores = {}
    for control in FALSE_CONTROLS:
        c = false[false["control"].eq(control)]
        false_scores[control] = {
            "max_effective_rank": float(c["effective_rank"].max()) if len(c) else None,
            "max_component_erasure_score": float(c["component_erasure_score"].max()) if len(c) else None,
            "scores_below_coupled_median": bool(float(c["effective_rank"].max()) < float(coupled["effective_rank"].median())) if len(c) and len(coupled) else None,
        }
    positive_nulls = deltas[(deltas["metric"].eq("effective_rank")) & (deltas["delta"] > 0)]
    strongest = None if positive_nulls.empty else positive_nulls.sort_values("delta", ascending=False).iloc[0].to_dict()
    geometry_supported = bool(
        len(positive_nulls) >= max(1, len(deltas[deltas["metric"].eq("effective_rank")]) // 2)
        and p_corr < 0.75
        and component_pass
        and temporal_pass
        and all(v["scores_below_coupled_median"] for v in false_scores.values() if v["scores_below_coupled_median"] is not None)
    )
    if geometry_supported:
        recommendation = "Proceed to T2: trajectory geometry across substrates."
        next_probe = "T2_trajectory_geometry_across_substrates"
    elif p_corr >= 0.75:
        recommendation = "Demote geometry to diagnostic until it separates from raw viability."
        next_probe = "failure_mode_atlas"
    elif not component_pass:
        recommendation = "Investigate lower-rank erasure before calling geometry positive."
        next_probe = "component_erasure_atlas"
    else:
        recommendation = "Build failure-mode atlas before scaling trajectory geometry."
        next_probe = "trajectory_geometry_failure_mode_atlas"
    gpu_used = float(timing["gpu_used"].mean()) if len(timing) else 0.0
    summary = {
        "probe": "T1_viable_trajectory_geometry",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "gpu_usage_fraction": gpu_used,
        "lead_result": {
            "geometry_branch_supported": geometry_supported,
            "best_geometry_metric": "effective_rank",
            "strongest_null_delta": strongest,
            "correlation_with_p_viable": p_corr,
            "component_balance_passed": component_pass,
            "temporal_fakeout_passed": temporal_pass,
        },
        "false_positive_controls": false_scores,
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": [] if gpu_used > 0 else ["GPU geometry path was not used."],
        "gpu_diagnostics": {
            "gpu_metric_batches": int(len(timing)),
            "mean_gpu_batch_seconds": float(timing["batch_seconds"].mean()) if len(timing) else None,
            "max_gpu_temp_c": float(timing["max_temp_c"].max()) if len(timing) else None,
            "thermal_throttle_events": int(timing["thermal_pause_events"].sum()) if len(timing) else 0,
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cfg.out_dir / "_mpl_cache"))
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    sample_dir = cfg.out_dir / "_trajectory_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)
    manifest = cfg.out_dir / "_seed_manifest.csv"
    if manifest.exists():
        manifest.unlink()
    alphas = [0.50] if cfg.smoke else MAIN_ALPHAS
    horizons = [900] if cfg.smoke else MAIN_HORIZONS
    started = time.monotonic()
    tasks = [
        (alpha, horizon, condition, seed, cfg, str(sample_dir))
        for alpha in alphas
        for horizon in horizons
        for condition in BASE_CONDITIONS
        for seed in range(cfg.seed_count)
    ]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = []
        for t in tasks:
            if time.monotonic() - started > cfg.soft_limit_seconds:
                break
            futures.append(pool.submit(task, t))
        for i, fut in enumerate(as_completed(futures), 1):
            append_rows(manifest, [fut.result()])
            if i % max(1, cfg.workers) == 0:
                print(json.dumps({"stage": "simulate", "completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
            if time.monotonic() - started > cfg.hard_limit_seconds:
                break
    summary = summarize(cfg, started)
    print("PROBE T1: VIABLE TRAJECTORY GEOMETRY")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
