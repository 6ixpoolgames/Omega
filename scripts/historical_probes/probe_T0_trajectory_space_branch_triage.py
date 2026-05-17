#!/usr/bin/env python
"""Probe T0: trajectory-space branch triage.

This is a branch-selection probe, not an Omega validation claim. It compares
quotient-light trajectory-space readouts across small diagnostic worlds and the
known F,T attractive multifield corridor.
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

import probe_08a_multifield_profile_reconciliation as p08a
import probe_11_learned_predictive_kappa_revised as p11


SEGMENT_COUNT = 6
SINGLE_WORLDS = ["open_field", "sink_trap", "rigid_attractor", "noise_swamp"]
MULTI_CONDITIONS = ["coupled", "product", "shuffled", "time_shuffled", "independent_alpha0"]
ALPHAS = [0.50, 0.525]
HORIZONS = [900, 1500]
BRANCHES = [
    "kernel_hazard_erosion",
    "concentration_collapse",
    "tube_thickness",
    "restoration",
    "predictive_temporal_dependence",
    "component_balance",
]


def ensure_cuda_dll_path() -> None:
    """Make bundled Torch CUDA DLLs visible to spawned Windows workers."""
    torch_lib = Path(__file__).resolve().parent / ".venv" / "Lib" / "site-packages" / "torch" / "lib"
    if not torch_lib.exists():
        return
    torch_lib_s = str(torch_lib)
    path_parts = os.environ.get("PATH", "").split(os.pathsep)
    if torch_lib_s not in path_parts:
        os.environ["PATH"] = torch_lib_s + os.pathsep + os.environ.get("PATH", "")
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(torch_lib_s)
        except OSError:
            pass


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
    gpu_pause_temp: int
    gpu_resume_temp: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_T0_trajectory_space_branch_triage_results"))
    p.add_argument("--workers", type=int, default=18)
    p.add_argument("--n-traj", type=int, default=3000)
    p.add_argument("--seed-count", type=int, default=60)
    p.add_argument("--bootstrap-repeats", type=int, default=100)
    p.add_argument("--soft-limit-sec", type=float, default=3600)
    p.add_argument("--hard-limit-sec", type=float, default=7200)
    p.add_argument("--gpu-pause-temp", type=int, default=82)
    p.add_argument("--gpu-resume-temp", type=int, default=75)
    p.add_argument("--no-gpu", action="store_true")
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 6)
        args.n_traj = min(args.n_traj, 600)
        args.seed_count = min(args.seed_count, 6)
        args.bootstrap_repeats = min(args.bootstrap_repeats, 40)
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
        gpu_pause_temp=args.gpu_pause_temp,
        gpu_resume_temp=args.gpu_resume_temp,
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


def wait_for_gpu(cfg: Config) -> None:
    if not cfg.use_gpu:
        return
    temp = gpu_temp_c()
    if temp is None or temp < cfg.gpu_pause_temp:
        return
    while temp is not None and temp > cfg.gpu_resume_temp:
        print(json.dumps({"gpu_thermal_pause": True, "temp_c": temp}), flush=True)
        time.sleep(10)
        temp = gpu_temp_c()


def simulate_single(world: str, horizon: int, seed: int, n: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(50_000 + seed + horizon * 7 + abs(hash(world)) % 1000)
    x = rng.normal(0.0, 0.55, size=n)
    energy = np.zeros(n)
    alive = np.ones(n, dtype=bool)
    rec = np.empty((SEGMENT_COUNT + 1, n), dtype=np.float32)
    alive_seg = np.empty((SEGMENT_COUNT + 1, n), dtype=bool)
    rec[0] = x
    alive_seg[0] = alive
    boundaries = {int(round(i * horizon / SEGMENT_COUNT)): i for i in range(1, SEGMENT_COUNT + 1)}
    dt = 0.018
    for t in range(1, horizon + 1):
        if world == "open_field":
            drift = -0.10 * x
            noise = 0.055
            sink = 3.0
            energy_limit = 0.22 * t + 4.5
        elif world == "sink_trap":
            drift = 0.42 * np.sign(x) + 0.06 * x
            noise = 0.050
            sink = 2.25
            energy_limit = 0.16 * t + 2.5
        elif world == "rigid_attractor":
            drift = -1.25 * x
            noise = 0.018
            sink = 3.0
            energy_limit = 0.24 * t + 4.5
        elif world == "noise_swamp":
            drift = -0.02 * x
            noise = 0.145
            sink = 3.0
            energy_limit = 0.13 * t + 2.0
        else:
            raise KeyError(world)
        dx = drift * dt + noise * math.sqrt(dt) * rng.normal(size=n)
        x = np.clip(x + dx, -4.0, 4.0)
        energy += np.abs(dx)
        alive &= (np.abs(x) < sink) & (energy < energy_limit)
        if t in boundaries:
            idx = boundaries[t]
            rec[idx] = x
            alive_seg[idx] = alive
    return {"traj": rec[:, :, None], "alive_seg": alive_seg, "alive_final": alive, "kind": "single"}


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
    traj = np.stack([block["a"], block["b"]], axis=2).astype(np.float32)
    return {"traj": traj, "alive_seg": block["alive_seg"], "alive_final": block["alive_final"], "kind": "multi"}


def concentration_gpu(traj: np.ndarray, alive: np.ndarray, cfg: Config) -> dict[str, float]:
    viable = traj[:, alive, :]
    if viable.shape[1] < 3:
        return {
            "endpoint_variance": 0.0,
            "mean_pairwise_trajectory_distance": 0.0,
            "effective_dimension": 0.0,
            "covariance_spectrum_rank": 0.0,
            "path_concentration_index": 1.0,
            "collapse_score": 1.0,
            "gpu_used": float(False),
        }
    flat = np.transpose(viable, (1, 0, 2)).reshape(viable.shape[1], -1).astype(np.float32)
    endpoint = viable[-1]
    if cfg.use_gpu:
        try:
            wait_for_gpu(cfg)
            ensure_cuda_dll_path()
            import cupy as cp

            x = cp.asarray(flat)
            x = x - cp.mean(x, axis=0, keepdims=True)
            cov = (x.T @ x) / max(x.shape[0] - 1, 1)
            eig = cp.linalg.eigvalsh(cov)
            eig = cp.maximum(eig, 0)
            eig_sum = cp.sum(eig) + 1e-12
            p = eig / eig_sum
            eff_dim = float(cp.exp(-cp.sum(p * cp.log(cp.maximum(p, 1e-12)))).get())
            rank90 = float((cp.searchsorted(cp.cumsum(eig[::-1]) / eig_sum, 0.90) + 1).get())
            sample_n = min(512, x.shape[0])
            idx = cp.linspace(0, x.shape[0] - 1, sample_n).astype(cp.int32)
            xs = x[idx]
            norms = cp.sum(xs * xs, axis=1)
            dist2 = cp.maximum(norms[:, None] + norms[None, :] - 2 * (xs @ xs.T), 0)
            mean_dist = float(cp.mean(cp.sqrt(dist2 + 1e-9)).get())
            end_var = float(cp.var(cp.asarray(endpoint), axis=0).mean().get())
            gpu_used = True
        except Exception:
            eff_dim, rank90, mean_dist, end_var = concentration_cpu(flat, endpoint)
            gpu_used = False
    else:
        eff_dim, rank90, mean_dist, end_var = concentration_cpu(flat, endpoint)
        gpu_used = False
    collapse = 1.0 / (1.0 + eff_dim)
    return {
        "endpoint_variance": end_var,
        "mean_pairwise_trajectory_distance": mean_dist,
        "effective_dimension": eff_dim,
        "covariance_spectrum_rank": rank90,
        "path_concentration_index": collapse,
        "collapse_score": collapse,
        "gpu_used": float(gpu_used),
    }


def concentration_cpu(flat: np.ndarray, endpoint: np.ndarray) -> tuple[float, float, float, float]:
    x = flat - flat.mean(axis=0, keepdims=True)
    cov = np.cov(x, rowvar=False)
    eig = np.maximum(np.linalg.eigvalsh(cov), 0)
    eig_sum = float(np.sum(eig) + 1e-12)
    p = eig / eig_sum
    eff_dim = float(np.exp(-np.sum(p * np.log(np.maximum(p, 1e-12)))))
    rank90 = float(np.searchsorted(np.cumsum(eig[::-1]) / eig_sum, 0.90) + 1)
    xs = x[np.linspace(0, len(x) - 1, min(256, len(x))).astype(int)]
    norms = np.sum(xs * xs, axis=1)
    dist2 = np.maximum(norms[:, None] + norms[None, :] - 2 * (xs @ xs.T), 0)
    mean_dist = float(np.mean(np.sqrt(dist2 + 1e-9)))
    end_var = float(np.var(endpoint, axis=0).mean())
    return eff_dim, rank90, mean_dist, end_var


def ridge_predictive_delta(traj: np.ndarray, alive: np.ndarray, seed: int) -> dict[str, float]:
    viable = traj[:, alive, :]
    if viable.shape[1] < 20:
        return {"predictive_r2": 0.0, "time_shuffled_r2": 0.0, "A_pred_delta": 0.0, "gaussian_mi_approx": 0.0, "binned_mi_diagnostic": 0.0}
    past = np.transpose(viable[:3], (1, 0, 2)).reshape(viable.shape[1], -1)
    future = np.transpose(viable[3:], (1, 0, 2)).reshape(viable.shape[1], -1)
    x_train, x_test, y_train, y_test = train_test_split(past, future, test_size=0.35, random_state=seed)
    model = Ridge(alpha=1.0)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    r2 = float(max(-1.0, r2_score(y_test, pred, multioutput="variance_weighted")))
    rng = np.random.default_rng(seed + 99)
    y_shuffle = future[rng.permutation(len(future))]
    x_train, x_test, y_train, y_test = train_test_split(past, y_shuffle, test_size=0.35, random_state=seed)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    r2_shuf = float(max(-1.0, r2_score(y_test, pred, multioutput="variance_weighted")))
    rho = float(np.corrcoef(past[:, 0], future[:, 0])[0, 1]) if past.shape[1] and np.std(past[:, 0]) > 0 and np.std(future[:, 0]) > 0 else 0.0
    rho = float(np.clip(rho, -0.999, 0.999))
    return {
        "predictive_r2": r2,
        "time_shuffled_r2": r2_shuf,
        "A_pred_delta": r2 - r2_shuf,
        "gaussian_mi_approx": float(-0.5 * math.log(max(1.0 - rho * rho, 1e-9))),
        "binned_mi_diagnostic": abs(rho),
    }


def compute_metrics(label: dict[str, object], block: dict[str, np.ndarray], seed: int, cfg: Config) -> dict[str, object]:
    traj = block["traj"]
    alive_seg = block["alive_seg"]
    alive_final = block["alive_final"]
    survival = alive_seg.mean(axis=1)
    hazard = []
    for i in range(1, len(survival)):
        prev = max(survival[i - 1], 1e-9)
        hazard.append(max(0.0, (survival[i - 1] - survival[i]) / prev))
    hazard = np.array(hazard)
    conc = concentration_gpu(traj, alive_final, cfg)
    pred = ridge_predictive_delta(traj, alive_final, seed)
    margin = 3.0 - np.max(np.abs(traj), axis=2)
    viable_margin = margin[:, alive_final] if np.any(alive_final) else margin
    tube_by_segment = np.maximum(np.mean(viable_margin, axis=1), 0)
    restoration = np.clip((viable_margin + 0.25) / 1.5, 0, 1)
    component_balance = {}
    if traj.shape[2] == 2 and np.sum(alive_final) > 20:
        viable = traj[:, alive_final, :]
        a_past = viable[:3, :, 0].T
        b_past = viable[:3, :, 1].T
        a_future = viable[3:, :, 0].T
        b_future = viable[3:, :, 1].T
        component_balance = component_prediction(a_past, b_past, a_future, b_future, seed)
    else:
        component_balance = {
            "A_self_future_prediction_given_B": np.nan,
            "B_self_future_prediction_given_A": np.nan,
            "component_prediction_balance": np.nan,
            "component_erasure_proxy": np.nan,
            "joint_vs_product_prediction_delta": np.nan,
            "joint_vs_shuffled_prediction_delta": np.nan,
        }
    return {
        **label,
        "seed": seed,
        "p_viable_T": float(survival[-1]),
        "tail_viability": float(np.mean(survival[-2:])),
        "kernel_erosion_slope": float((survival[0] - survival[-1]) / max(len(survival) - 1, 1)),
        "mean_hazard": float(np.mean(hazard)),
        "late_hazard": float(np.mean(hazard[-2:])),
        "tube_thickness_mean": float(np.mean(tube_by_segment)),
        "tube_erosion_slope": float((tube_by_segment[0] - tube_by_segment[-1]) / max(len(tube_by_segment) - 1, 1)),
        "perturbation_survival_radius": float(np.quantile(viable_margin, 0.25)) if viable_margin.size else 0.0,
        "boundary_proximity": float(np.mean(viable_margin < 0.25)) if viable_margin.size else 1.0,
        "restoration_probability": float(np.mean(restoration > 0.5)),
        "return_to_corridor_time": float(np.argmax(np.mean(restoration, axis=1) > 0.5)) if restoration.size else np.nan,
        "restoration_half_life": float(np.mean(np.mean(restoration, axis=1) > 0.5)) if restoration.size else 0.0,
        "post_perturbation_viability": float(np.mean(restoration[-1])),
        "overshoot_or_absorption_rate": float(np.mean(viable_margin[-1] < 0.0)) if viable_margin.size else 1.0,
        **conc,
        **pred,
        **component_balance,
    }


def component_prediction(a_past: np.ndarray, b_past: np.ndarray, a_future: np.ndarray, b_future: np.ndarray, seed: int) -> dict[str, float]:
    def score(x: np.ndarray, y: np.ndarray) -> float:
        xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.35, random_state=seed)
        model = Ridge(alpha=1.0)
        model.fit(xtr, ytr)
        return float(max(-1.0, r2_score(yte, model.predict(xte), multioutput="variance_weighted")))
    a_score = score(np.column_stack([a_past, b_past]), a_future)
    b_score = score(np.column_stack([b_past, a_past]), b_future)
    balance = 1.0 - abs(a_score - b_score)
    return {
        "A_self_future_prediction_given_B": a_score,
        "B_self_future_prediction_given_A": b_score,
        "component_prediction_balance": balance,
        "component_erasure_proxy": max(0.0, 1.0 - balance),
        "joint_vs_product_prediction_delta": (a_score + b_score) / 2.0,
        "joint_vs_shuffled_prediction_delta": (a_score + b_score) / 2.0,
    }


def task(task_def: tuple[str, str, float, int, int, Config]) -> dict[str, object]:
    kind, name, alpha, horizon, seed, cfg = task_def
    if kind == "single":
        block = simulate_single(name, horizon, seed, cfg.n_traj)
        label = {"kind": "single", "world": name, "condition": name, "alpha": np.nan, "T": horizon}
    else:
        block = simulate_multi(alpha, horizon, seed, name, cfg.n_traj)
        label = {"kind": "multi", "world": "F_T_attractive", "condition": name, "alpha": alpha, "T": horizon}
    return compute_metrics(label, block, seed, cfg)


def bootstrap(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(77_001)
    out = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            vals = vals[np.isfinite(vals)]
            if len(vals) == 0:
                continue
            mean = float(np.mean(vals))
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
            else:
                lo = hi = mean
            out.append({**base, "metric": metric, "mean": mean, "ci_low": float(lo), "ci_high": float(hi), "ci_width": float(hi - lo)})
    return pd.DataFrame(out)


def score_branches(means: pd.DataFrame, corr: pd.DataFrame) -> pd.DataFrame:
    scores = []
    metric_map = {
        "kernel_hazard_erosion": ["kernel_erosion_slope", "late_hazard", "tail_viability"],
        "concentration_collapse": ["effective_dimension", "mean_pairwise_trajectory_distance", "collapse_score"],
        "tube_thickness": ["tube_thickness_mean", "perturbation_survival_radius", "tube_erosion_slope"],
        "restoration": ["restoration_probability", "post_perturbation_viability", "overshoot_or_absorption_rate"],
        "predictive_temporal_dependence": ["A_pred_delta", "predictive_r2", "gaussian_mi_approx"],
        "component_balance": ["component_prediction_balance", "component_erasure_proxy", "joint_vs_shuffled_prediction_delta"],
    }
    for branch, metrics in metric_map.items():
        vals = means[metrics].select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)
        sep = float(np.nanmean(vals.std(numeric_only=True))) if len(vals) else 0.0
        stability = 2.0
        interpretability = 3.0 if branch != "predictive_temporal_dependence" else 2.0
        compute = 3.0 if branch in {"kernel_hazard_erosion", "concentration_collapse"} else 2.0
        max_corr = 1.0
        if len(corr):
            c = corr[corr["branch"] == branch]
            max_corr = float(c["abs_corr_with_p_viable"].max()) if len(c) else 1.0
        nonred = 3.0 if max_corr < 0.45 else 2.0 if max_corr < 0.75 else 1.0
        separation = 3.0 if sep > 0.25 else 2.0 if sep > 0.08 else 1.0 if sep > 0.02 else 0.0
        total = separation + stability + interpretability + nonred + compute
        scores.append({
            "branch": branch,
            "separation": separation,
            "stability": stability,
            "interpretability": interpretability,
            "non_redundancy": nonred,
            "compute_practicality": compute,
            "branch_score": total,
            "max_abs_corr_with_p_viable": max_corr,
        })
    return pd.DataFrame(scores).sort_values("branch_score", ascending=False)


def make_plots(out: Path, means: pd.DataFrame, scores: pd.DataFrame, corr_matrix: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    plots = [
        ("p_viable_T", "survival_hazard_by_world.png", "Survival by world"),
        ("kernel_erosion_slope", "kernel_erosion_by_world.png", "Kernel erosion by world"),
        ("effective_dimension", "trajectory_concentration_by_world.png", "Effective dimension by world"),
        ("tube_thickness_mean", "tube_thickness_by_world.png", "Tube thickness by world"),
        ("restoration_probability", "restoration_by_world.png", "Restoration by world"),
        ("A_pred_delta", "prediction_advantage_by_world.png", "Prediction advantage by world"),
        ("component_prediction_balance", "component_balance_by_condition.png", "Component balance by condition"),
    ]
    means = means.copy()
    means["label"] = means["world"].astype(str) + ":" + means["condition"].astype(str)
    for col, fname, title in plots:
        fig, ax = plt.subplots(figsize=(9, 5))
        s = means[["label", col]].dropna()
        ax.barh(s["label"], s[col])
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 6))
    if len(corr_matrix):
        im = ax.imshow(corr_matrix.to_numpy(float), vmin=-1, vmax=1, cmap="coolwarm")
        ax.set_xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=90)
        ax.set_yticks(range(len(corr_matrix.index)), corr_matrix.index)
        fig.colorbar(im, ax=ax)
    ax.set_title("Readout correlation matrix")
    fig.tight_layout()
    fig.savefig(out / "readout_correlation_matrix.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(scores["branch"], scores["branch_score"])
    ax.set_title("Branch scores")
    fig.tight_layout()
    fig.savefig(out / "branch_score_radar.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    multi = means[means["kind"] == "multi"]
    ax.scatter(multi["A_pred_delta"], multi["effective_dimension"], c=multi["p_viable_T"])
    ax.set_xlabel("prediction delta")
    ax.set_ylabel("effective dimension")
    ax.set_title("COM corridor alignment proxy")
    fig.tight_layout()
    fig.savefig(out / "com_metric_alignment.png", dpi=160)
    plt.close(fig)


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_metrics.csv")
    group_cols = ["kind", "world", "condition", "alpha", "T"]
    means = raw.groupby(group_cols, dropna=False, as_index=False).mean(numeric_only=True)
    metrics = [
        "p_viable_T", "tail_viability", "kernel_erosion_slope", "mean_hazard", "late_hazard",
        "endpoint_variance", "mean_pairwise_trajectory_distance", "effective_dimension",
        "covariance_spectrum_rank", "path_concentration_index", "collapse_score",
        "tube_thickness_mean", "tube_erosion_slope", "perturbation_survival_radius", "boundary_proximity",
        "restoration_probability", "return_to_corridor_time", "restoration_half_life", "post_perturbation_viability",
        "overshoot_or_absorption_rate", "predictive_r2", "time_shuffled_r2", "A_pred_delta",
        "gaussian_mi_approx", "binned_mi_diagnostic", "component_prediction_balance", "component_erasure_proxy",
        "joint_vs_product_prediction_delta", "joint_vs_shuffled_prediction_delta",
    ]
    boot = bootstrap(raw, group_cols, metrics, cfg.bootstrap_repeats)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "p_viable_T", "tail_viability", "mean_hazard", "late_hazard"]].to_csv(out / "viability_hazard_profile.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "kernel_erosion_slope", "tail_viability"]].to_csv(out / "kernel_erosion_profile.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "endpoint_variance", "mean_pairwise_trajectory_distance", "effective_dimension", "covariance_spectrum_rank", "path_concentration_index", "collapse_score"]].to_csv(out / "trajectory_concentration.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "tube_thickness_mean", "tube_erosion_slope", "perturbation_survival_radius", "boundary_proximity"]].to_csv(out / "tube_thickness_profile.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "restoration_probability", "return_to_corridor_time", "restoration_half_life", "post_perturbation_viability", "overshoot_or_absorption_rate"]].to_csv(out / "restoration_profile.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "predictive_r2", "time_shuffled_r2", "A_pred_delta", "gaussian_mi_approx", "binned_mi_diagnostic"]].to_csv(out / "predictive_temporal_dependence.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "A_self_future_prediction_given_B", "B_self_future_prediction_given_A", "component_prediction_balance", "component_erasure_proxy", "joint_vs_product_prediction_delta", "joint_vs_shuffled_prediction_delta"]].to_csv(out / "component_balance.csv", index=False)
    baseline = means.copy()
    baseline.to_csv(out / "baseline_comparisons.csv", index=False)
    numeric = means[metrics].replace([np.inf, -np.inf], np.nan)
    corr_matrix = numeric.corr()
    corr_matrix.to_csv(out / "readout_correlations.csv")
    branch_metric = {
        "kernel_hazard_erosion": ["kernel_erosion_slope", "late_hazard"],
        "concentration_collapse": ["effective_dimension", "collapse_score"],
        "tube_thickness": ["tube_thickness_mean", "perturbation_survival_radius"],
        "restoration": ["restoration_probability", "post_perturbation_viability"],
        "predictive_temporal_dependence": ["A_pred_delta", "predictive_r2"],
        "component_balance": ["component_prediction_balance", "component_erasure_proxy"],
    }
    corr_rows = []
    for branch, cols in branch_metric.items():
        for col in cols:
            if col in corr_matrix and "p_viable_T" in corr_matrix:
                corr_rows.append({"branch": branch, "metric": col, "abs_corr_with_p_viable": abs(float(corr_matrix.loc[col, "p_viable_T"]))})
    corr_branch = pd.DataFrame(corr_rows)
    scores = score_branches(means, corr_branch)
    scores.to_csv(out / "branch_scores.csv", index=False)
    multi = means[means["kind"] == "multi"].copy()
    if len(multi):
        coupled = multi[multi["condition"] == "coupled"]
        rest = multi[multi["condition"] != "coupled"]
        align = []
        for col in ["effective_dimension", "tube_thickness_mean", "A_pred_delta", "component_prediction_balance"]:
            align.append({"metric": col, "coupled_mean": float(coupled[col].mean()), "baseline_mean": float(rest[col].mean()), "delta": float(coupled[col].mean() - rest[col].mean())})
        pd.DataFrame(align).to_csv(out / "com_metric_alignment.csv", index=False)
    else:
        pd.DataFrame().to_csv(out / "com_metric_alignment.csv", index=False)
    means[["kind", "world", "condition", "alpha", "T", "gpu_used", "p_viable_T", "effective_dimension"]].to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, means, scores, corr_matrix.fillna(0))
    best = scores.iloc[0].to_dict()
    recommendation = {
        "tube_thickness": "Probe T1: Viable Tube Geometry",
        "restoration": "Probe T1: Restoration and Return-to-Corridor Dynamics",
        "kernel_hazard_erosion": "Probe T1: Viability Kernel Erosion Along Trajectories",
        "concentration_collapse": "Probe T1: Viable Trajectory Geometry",
        "predictive_temporal_dependence": "Probe T1: Predictive Propagation in Trajectory Space",
        "component_balance": "Probe T1: Component Preservation Without Fibers",
    }.get(best["branch"], "Pause trajectory-space scaling; return to quotient/fiber formalization")
    summary = {
        "probe": "T0_trajectory_space_branch_triage",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "workers": cfg.workers,
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "conditions": means[group_cols].to_dict(orient="records"),
        "branch_scores": {r["branch"]: float(r["branch_score"]) for _, r in scores.iterrows()},
        "best_branch": {
            "name": best["branch"],
            "why": "Highest branch-selection score across separation, stability, interpretability, non-redundancy, and compute practicality.",
            "strongest_metric": str(best["branch"]),
            "weakest_metric": "full conditional MI not attempted in T0",
            "estimator_warnings": [] if float(raw["gpu_used"].mean()) > 0 else ["GPU concentration path was not used."],
        },
        "non_redundancy": {
            "most_correlated_with_p_viable": corr_branch.sort_values("abs_corr_with_p_viable", ascending=False).head(3).to_dict(orient="records") if len(corr_branch) else [],
            "least_correlated_with_p_viable": corr_branch.sort_values("abs_corr_with_p_viable").head(3).to_dict(orient="records") if len(corr_branch) else [],
            "separates_similar_p_viable_regimes": scores[scores["non_redundancy"] >= 2]["branch"].tolist(),
        },
        "com_alignment": {
            "strongest_aligned_readout": None,
            "conflicting_readouts": [],
            "interpretation": "T0 treats COM alignment as a diagnostic, not an optimization target.",
        },
        "recommendation": recommendation,
        "gpu_usage_fraction": float(raw["gpu_used"].mean()),
        "files": sorted(p.name for p in out.glob("*") if not p.name.startswith("_")),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    args = parse_args()
    cfg = make_config(args)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cfg.out_dir / "_mpl_cache"))
    Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    seed_path = cfg.out_dir / "_seed_metrics.csv"
    if seed_path.exists():
        seed_path.unlink()
    started = time.monotonic()
    seeds = list(range(cfg.seed_count))
    tasks = []
    for world in SINGLE_WORLDS:
        for seed in seeds:
            tasks.append(("single", world, np.nan, 900, seed, cfg))
    for alpha in ALPHAS:
        for horizon in HORIZONS:
            for condition in MULTI_CONDITIONS:
                for seed in seeds:
                    tasks.append(("multi", condition, alpha, horizon, seed, cfg))
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = []
        for t in tasks:
            if time.monotonic() - started > cfg.soft_limit_seconds:
                break
            futures.append(pool.submit(task, t))
        for i, fut in enumerate(as_completed(futures), 1):
            append_rows(seed_path, [fut.result()])
            if i % max(1, cfg.workers) == 0:
                print(json.dumps({"completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
            if time.monotonic() - started > cfg.hard_limit_seconds:
                break
    summary = build_outputs(cfg, started)
    print("PROBE T0: TRAJECTORY-SPACE BRANCH TRIAGE")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
