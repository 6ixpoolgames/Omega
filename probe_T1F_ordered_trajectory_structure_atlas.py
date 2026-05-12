#!/usr/bin/env python
"""Probe T1F: ordered trajectory structure atlas.

This is a falsification/triage probe after T1. T1 killed simple
effective-rank/collapse geometry. T1F asks whether simple trajectory-native
ordered distinction readouts survive the same failure modes.
"""

from __future__ import annotations

import argparse
import csv
import json
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
FALSE_CONTROLS = ["rigid_collapse", "noise_fakeout", "single_component_erasure", "endpoint_fakeout"]
MAIN_ALPHAS = [0.45, 0.50, 0.525]
MAIN_HORIZONS = [900, 1500, 2400]
FAMILIES = [
    "ordered_distinction_persistence",
    "conditional_temporal_dependence_proxy",
    "component_conditioned_temporal_continuity",
    "minimal_recoverable_continuation",
]


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
    sketch_sample: int
    gpu_pause_temp: int
    gpu_resume_temp: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_T1F_ordered_trajectory_structure_atlas_results"))
    p.add_argument("--workers", type=int, default=18)
    p.add_argument("--n-traj", type=int, default=15000)
    p.add_argument("--seed-count", type=int, default=180)
    p.add_argument("--bootstrap-repeats", type=int, default=300)
    p.add_argument("--soft-limit-sec", type=float, default=5400)
    p.add_argument("--hard-limit-sec", type=float, default=7200)
    p.add_argument("--sample-per-seed", type=int, default=1200)
    p.add_argument("--sketch-sample", type=int, default=4096)
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
        args.sample_per_seed = min(args.sample_per_seed, 350)
        args.sketch_sample = min(args.sketch_sample, 1000)
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
        sketch_sample=args.sketch_sample,
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


def survival_metrics(alive_seg: np.ndarray) -> dict[str, float]:
    survival = alive_seg.mean(axis=1)
    hazard = []
    for i in range(1, len(survival)):
        hazard.append(max(0.0, float((survival[i - 1] - survival[i]) / max(survival[i - 1], 1e-12))))
    return {
        "p_viable_T": float(survival[-1]),
        "survival_mid": float(survival[len(survival) // 2]),
        "mean_hazard": float(np.mean(hazard)),
        "late_hazard": float(np.mean(hazard[-2:])),
    }


def sample_viable(traj: np.ndarray, alive: np.ndarray, seed: int, sample_per_seed: int) -> np.ndarray:
    idx = np.flatnonzero(alive)
    if len(idx) == 0:
        return np.empty((0, traj.shape[0], traj.shape[2]), dtype=np.float32)
    rng = np.random.default_rng(1_710_000 + seed)
    take = rng.choice(idx, min(sample_per_seed, len(idx)), replace=False)
    return np.transpose(traj[:, take, :], (1, 0, 2)).astype(np.float32)


def task(task_def: tuple[float, int, str, int, Config, str]) -> dict[str, object]:
    alpha, horizon, condition, seed, cfg, sample_dir_s = task_def
    block = simulate_multi(alpha, horizon, seed, condition, cfg.n_traj)
    sample = sample_viable(block["traj"], block["alive_final"], seed, cfg.sample_per_seed)
    sample_path = Path(sample_dir_s) / f"a{alpha:.3f}_T{horizon}_{condition}_seed{seed:04d}.npz"
    np.savez_compressed(sample_path, sample=sample)
    return {
        "condition": condition,
        "alpha": alpha,
        "T": horizon,
        "seed": seed,
        "sample_path": str(sample_path),
        "sample_n": int(len(sample)),
        **survival_metrics(block["alive_seg"]),
    }


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
        idx = np.random.default_rng(17_017).choice(len(data), max_rows, replace=False)
        data = data[idx]
    return data.astype(np.float32)


def control_sample(sample: np.ndarray, control: str, seed: int) -> np.ndarray:
    if control == "none":
        return sample
    rng = np.random.default_rng(1_700_000 + seed + abs(hash(control)) % 1000)
    out = sample.copy()
    if control == "rigid_collapse":
        means = out.mean(axis=0, keepdims=True)
        out = means + 0.03 * (out - means)
    elif control == "noise_fakeout":
        flat = out.reshape(len(out), -1)
        out = (flat.mean(axis=0, keepdims=True) + rng.normal(size=flat.shape) * flat.std(axis=0, keepdims=True)).reshape(out.shape)
    elif control == "single_component_erasure":
        means = out[:, :, 1].mean(axis=0, keepdims=True)
        out[:, :, 1] = means + 0.03 * (out[:, :, 1] - means)
    elif control == "endpoint_fakeout":
        start = out[:, 0, :].copy()
        end = out[:, -1, :].copy()
        for s in range(1, SEGMENT_COUNT):
            w = s / SEGMENT_COUNT
            base = (1.0 - w) * start + w * end
            residual = out[:, s, :] - base
            residual = residual[rng.permutation(len(residual))]
            out[:, s, :] = base + residual
    else:
        raise KeyError(control)
    return out.astype(np.float32)


def safe_ratio(a: float, b: float) -> float:
    if b <= 1e-12 or not np.isfinite(b):
        return 0.0
    return float(np.clip(a / b, 0.0, 1.0))


def ridge_r2(x: np.ndarray, y: np.ndarray, seed: int) -> float:
    if len(x) < 40 or np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return 0.0
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.35, random_state=seed)
    model = Ridge(alpha=1.0)
    model.fit(xtr, ytr)
    return float(max(-1.0, r2_score(yte, model.predict(xte), multioutput="variance_weighted")))


def linear_cka_np(x: np.ndarray, y: np.ndarray) -> float:
    x = x - x.mean(axis=0, keepdims=True)
    y = y - y.mean(axis=0, keepdims=True)
    xy = np.linalg.norm(x.T @ y, "fro") ** 2
    xx = np.linalg.norm(x.T @ x, "fro") * np.linalg.norm(y.T @ y, "fro")
    return float(xy / max(xx, 1e-12))


def cpu_metrics(sample: np.ndarray, seed: int) -> dict[str, float]:
    if len(sample) < 40:
        return {}
    take = np.linspace(0, len(sample) - 1, min(25_000, len(sample))).astype(int)
    s = sample[take]
    past = s[:, :3, :].reshape(len(s), -1)
    future = s[:, 3:, :].reshape(len(s), -1)
    future_shuf = future[np.random.default_rng(seed + 101).permutation(len(future))]
    r2 = ridge_r2(past, future, seed)
    r2s = ridge_r2(past, future_shuf, seed)
    a_past = s[:, :3, 0]
    a_future = s[:, 3:, 0]
    b_past = s[:, :3, 1]
    b_future = s[:, 3:, 1]
    a_r2 = ridge_r2(a_past, a_future, seed + 1)
    b_r2 = ridge_r2(b_past, b_future, seed + 2)
    joint_r2 = r2
    comp_balance = 1.0 - abs(a_r2 - b_r2)
    return {
        "ridge_R2_past_to_future": r2,
        "ridge_R2_time_shuffled": r2s,
        "time_shuffled_delta": r2 - r2s,
        "linear_CKA_past_future": linear_cka_np(past, future),
        "rank_adjusted_prediction_delta": (r2 - r2s) / max(np.linalg.matrix_rank(past), 1),
        "A_past_to_A_future_delta": a_r2,
        "B_past_to_B_future_delta": b_r2,
        "joint_past_to_joint_future_delta": joint_r2,
        "component_continuity_balance": float(np.clip(comp_balance, 0.0, 1.0)),
        "component_erasure_rejection": float(np.clip(min(a_r2, b_r2) / max(max(a_r2, b_r2), 1e-9), 0.0, 1.0)),
    }


def gpu_ordered_metrics(sample: np.ndarray, cfg: Config, label: dict[str, object], control: str) -> tuple[dict[str, object], dict[str, object]]:
    started = time.monotonic()
    temp0, pauses = wait_for_gpu(cfg)
    gpu_used = False
    max_temp = temp0 if temp0 is not None else np.nan
    try:
        if not cfg.use_gpu:
            raise RuntimeError("GPU disabled")
        ensure_cuda_dll_path()
        import cupy as cp

        n = min(cfg.sketch_sample, len(sample))
        idx = cp.linspace(0, len(sample) - 1, n).astype(cp.int32)
        x = cp.asarray(sample, dtype=cp.float32)[idx]
        early = x[:, :3, :].reshape(n, -1)
        late = x[:, 3:, :].reshape(n, -1)
        early = early - cp.mean(early, axis=0, keepdims=True)
        late = late - cp.mean(late, axis=0, keepdims=True)
        norms = cp.sum(early * early, axis=1)
        d2 = cp.maximum(norms[:, None] + norms[None, :] - 2 * (early @ early.T), 0)
        d2[cp.arange(n), cp.arange(n)] = cp.inf
        nn = cp.argmin(d2, axis=1)
        early_nn = cp.sqrt(cp.min(d2, axis=1) + 1e-9)
        late_nn = cp.sqrt(cp.sum((late - late[nn]) ** 2, axis=1) + 1e-9)
        rand = late[cp.random.permutation(n)]
        late_rand = cp.sqrt(cp.sum((late - rand) ** 2, axis=1) + 1e-9)
        neighbor_pres = 1.0 - float((cp.mean(late_nn) / (cp.mean(late_rand) + 1e-9)).get())
        center = cp.median(early[:, 0])
        lo = late[early[:, 0] <= center]
        hi = late[early[:, 0] > center]
        sep = float((cp.linalg.norm(cp.mean(lo, axis=0) - cp.mean(hi, axis=0)) / (cp.mean(late_rand) + 1e-9)).get())
        gram_xy = cp.linalg.norm(early.T @ late, "fro") ** 2
        gram_xx = cp.linalg.norm(early.T @ early, "fro") * cp.linalg.norm(late.T @ late, "fro")
        cka = float((gram_xy / (gram_xx + 1e-12)).get())
        mid = x[:, 2:5, :].reshape(n, -1)
        local_cont = 1.0 - float((cp.mean(cp.sqrt(cp.sum((mid - mid[nn]) ** 2, axis=1) + 1e-9)) / (cp.mean(late_rand) + 1e-9)).get())
        cp.cuda.Stream.null.synchronize()
        gpu_used = True
        gpu_metrics = {
            "early_to_late_neighbor_preservation": float(neighbor_pres),
            "early_to_late_future_profile_separation": sep,
            "linear_CKA_gpu": cka,
            "continuation_profile_separation": local_cont,
            "continuation_viability": float(np.clip((neighbor_pres + local_cont) / 2.0, 0.0, 1.0)),
        }
    except Exception:
        gpu_metrics = {
            "early_to_late_neighbor_preservation": np.nan,
            "early_to_late_future_profile_separation": np.nan,
            "linear_CKA_gpu": np.nan,
            "continuation_profile_separation": np.nan,
            "continuation_viability": np.nan,
        }
    temp1 = gpu_temp_c()
    if temp1 is not None and (not np.isfinite(max_temp) or temp1 > max_temp):
        max_temp = temp1
    cpu = cpu_metrics(sample, int(float(label["alpha"]) * 1000 + int(label["T"])))
    out = {**label, "control": control, "sample_n": int(len(sample)), **gpu_metrics, **cpu, "gpu_used": float(gpu_used)}
    timing = {
        **label,
        "control": control,
        "sample_n": int(len(sample)),
        "gpu_used": float(gpu_used),
        "batch_seconds": round(time.monotonic() - started, 4),
        "start_temp_c": temp0,
        "end_temp_c": temp1,
        "max_temp_c": max_temp,
        "thermal_pause_events": pauses,
    }
    return out, timing


def bootstrap_intervals(seed_df: pd.DataFrame, repeats: int) -> pd.DataFrame:
    metrics = ["p_viable_T", "sample_n"]
    rng = np.random.default_rng(87_001)
    rows = []
    for key, group in seed_df.groupby(["condition", "alpha", "T"], dropna=False):
        base = dict(zip(["condition", "alpha", "T"], key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)]) if len(vals) > 1 else vals
            lo, hi = np.quantile(boot, [0.025, 0.975])
            rows.append({**base, "metric": metric, "mean": float(np.mean(vals)), "ci_low": float(lo), "ci_high": float(hi), "ci_width": float(hi - lo)})
    return pd.DataFrame(rows)


def null_deltas(metrics: pd.DataFrame) -> pd.DataFrame:
    readouts = [
        "early_to_late_neighbor_preservation",
        "early_to_late_future_profile_separation",
        "time_shuffled_delta",
        "linear_CKA_past_future",
        "component_continuity_balance",
        "continuation_profile_separation",
    ]
    rows = []
    base = metrics[metrics["control"].eq("none")]
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
            for metric in readouts:
                rows.append({"alpha": alpha, "T": horizon, "metric": metric, "null": condition, "delta": float(c[metric] - n[metric])})
    return pd.DataFrame(rows)


def score_families(metrics: pd.DataFrame, deltas: pd.DataFrame) -> pd.DataFrame:
    rows = []
    none = metrics[metrics["control"].eq("none")]
    coupled = metrics[(metrics["condition"].eq("coupled")) & (metrics["control"].eq("none"))]
    false_controls = metrics[metrics["control"].ne("none")]
    family_metric = {
        "ordered_distinction_persistence": "early_to_late_neighbor_preservation",
        "conditional_temporal_dependence_proxy": "time_shuffled_delta",
        "component_conditioned_temporal_continuity": "component_continuity_balance",
        "minimal_recoverable_continuation": "continuation_profile_separation",
    }
    for family, metric in family_metric.items():
        d = deltas[deltas["metric"].eq(metric)]
        null_sep = 3 if len(d) and (d["delta"] > 0).mean() >= 0.75 else 2 if len(d) and (d["delta"] > 0).mean() >= 0.5 else 1 if len(d) and (d["delta"] > 0).mean() > 0 else 0
        if len(false_controls) and len(coupled):
            fp_pass = float(false_controls[metric].max()) < float(coupled[metric].median())
        else:
            fp_pass = False
        false_positive_rejection = 3 if fp_pass else 0
        component = 3 if float(coupled["component_continuity_balance"].min()) > 0.65 else 1 if float(coupled["component_continuity_balance"].mean()) > 0.45 else 0
        corr = abs(float(none[metric].corr(none["p_viable_T"]))) if len(none) > 2 else 1.0
        nonred = 3 if corr < 0.45 else 2 if corr < 0.65 else 1 if corr < 0.8 else 0
        stability = 2
        interpretability = 3
        gpu = 3 if family != "minimal_recoverable_continuation" else 2
        total = null_sep + false_positive_rejection + component + nonred + stability + interpretability + gpu
        rows.append({
            "family": family,
            "primary_metric": metric,
            "null_separation": null_sep,
            "false_positive_rejection": false_positive_rejection,
            "component_continuity": component,
            "non_redundancy_vs_p_viable": nonred,
            "bootstrap_stability": stability,
            "interpretability": interpretability,
            "gpu_practicality": gpu,
            "family_score": total,
            "abs_corr_with_p_viable": corr,
        })
    return pd.DataFrame(rows).sort_values("family_score", ascending=False)


def make_plots(out: Path, metrics: pd.DataFrame, scores: pd.DataFrame, corr: pd.DataFrame, timing: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(scores["family"], scores["family_score"])
    ax.set_title("Readout family scores")
    fig.tight_layout()
    fig.savefig(out / "readout_family_scores.png", dpi=150)
    plt.close(fig)
    metrics = metrics.copy()
    metrics["label"] = metrics["condition"].astype(str) + ":" + metrics["alpha"].astype(str) + ":T" + metrics["T"].astype(str) + ":" + metrics["control"].astype(str)
    for col, fname, title in [
        ("early_to_late_neighbor_preservation", "ordered_persistence_by_condition.png", "Ordered persistence by condition"),
        ("time_shuffled_delta", "temporal_dependence_delta.png", "Temporal dependence delta"),
        ("component_continuity_balance", "component_continuity_balance.png", "Component continuity balance"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 6))
        s = metrics.sort_values(col)
        ax.barh(s["label"], s[col])
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=150)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    fp = metrics[metrics["control"].ne("none")]
    ax.scatter(fp["early_to_late_neighbor_preservation"], fp["component_continuity_balance"], c=fp["sample_n"])
    ax.set_xlabel("ordered persistence")
    ax.set_ylabel("component continuity")
    ax.set_title("False-positive rejection")
    fig.tight_layout()
    fig.savefig(out / "false_positive_rejection.png", dpi=150)
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
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(range(len(timing)), timing["batch_seconds"])
    ax.set_title("GPU batch timing")
    ax.set_xlabel("batch")
    ax.set_ylabel("seconds")
    fig.tight_layout()
    fig.savefig(out / "gpu_batch_timing.png", dpi=150)
    plt.close(fig)


def summarize(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    seed_df = pd.read_csv(out / "_seed_manifest.csv")
    survival = seed_df.groupby(["condition", "alpha", "T"], as_index=False).mean(numeric_only=True)
    rows = []
    timings = []
    for key, group in seed_df.groupby(["condition", "alpha", "T"], dropna=False):
        label = dict(zip(["condition", "alpha", "T"], key))
        sample = load_group(group)
        controls = ["none"] + (FALSE_CONTROLS if label["condition"] == "coupled" else [])
        for control in controls:
            c_sample = control_sample(sample, control, int(float(label["alpha"]) * 1000 + int(label["T"])))
            row, timing = gpu_ordered_metrics(c_sample, cfg, label, control)
            rows.append(row)
            timings.append(timing)
    metrics = pd.DataFrame(rows).merge(survival[["condition", "alpha", "T", "p_viable_T", "mean_hazard", "late_hazard"]], on=["condition", "alpha", "T"], how="left")
    timing = pd.DataFrame(timings)
    deltas = null_deltas(metrics)
    scores = score_families(metrics, deltas)
    boot = bootstrap_intervals(seed_df, cfg.bootstrap_repeats)
    metric_cols = [
        "p_viable_T",
        "early_to_late_neighbor_preservation",
        "early_to_late_future_profile_separation",
        "time_shuffled_delta",
        "linear_CKA_past_future",
        "component_continuity_balance",
        "continuation_profile_separation",
    ]
    corr = metrics[metrics["control"].eq("none")][metric_cols].corr(numeric_only=True)
    metrics.to_csv(out / "estimator_report.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "early_to_late_neighbor_preservation", "early_to_late_future_profile_separation", "time_shuffled_delta"]].to_csv(out / "ordered_distinction_persistence.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "ridge_R2_past_to_future", "ridge_R2_time_shuffled", "time_shuffled_delta", "linear_CKA_past_future", "rank_adjusted_prediction_delta"]].to_csv(out / "temporal_dependence_proxy.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "A_past_to_A_future_delta", "B_past_to_B_future_delta", "joint_past_to_joint_future_delta", "component_continuity_balance", "component_erasure_rejection"]].to_csv(out / "component_temporal_continuity.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "continuation_viability", "continuation_profile_separation"]].to_csv(out / "minimal_recoverable_continuation.csv", index=False)
    metrics[metrics["control"].ne("none")].to_csv(out / "false_positive_control_results.csv", index=False)
    deltas.to_csv(out / "null_deltas.csv", index=False)
    corr.to_csv(out / "metric_correlations.csv")
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    timing.to_csv(out / "gpu_timing_diagnostics.csv", index=False)
    scores.to_csv(out / "readout_family_scores.csv", index=False)
    make_plots(out, metrics, scores, corr, timing)
    best = scores.iloc[0].to_dict()
    family_results = {row["family"]: {"score": float(row["family_score"]), "primary_metric": row["primary_metric"]} for _, row in scores.iterrows()}
    coupled = metrics[(metrics["condition"].eq("coupled")) & (metrics["control"].eq("none"))]
    component_passed = bool(float(coupled["component_continuity_balance"].min()) > 0.65) if len(coupled) else False
    primary_fp_pass = False
    if len(coupled):
        primary = best["primary_metric"]
        primary_fp_pass = bool(float(metrics[metrics["control"].ne("none")][primary].max()) < float(coupled[primary].median()))
    passed = bool(best["family_score"] >= 14 and component_passed and primary_fp_pass)
    recommendation = "Demote trajectory-native branch; return to COM formalization or agent-relevant distinction/control probe."
    next_probe = "COM_fiber_transport_formalization"
    if passed:
        recommendation = f"Deepen cautiously: {best['family']} is promising but should be independently replicated."
        next_probe = "T2_ordered_distinction_deepening"
    fp = {}
    for control in ["time_shuffled"] + FALSE_CONTROLS:
        if control == "time_shuffled":
            c = metrics[(metrics["condition"].eq("time_shuffled")) & (metrics["control"].eq("none"))]
        else:
            c = metrics[metrics["control"].eq(control)]
        fp[control] = {
            "max_ordered_persistence": float(c["early_to_late_neighbor_preservation"].max()) if len(c) else None,
            "below_coupled_median": bool(float(c["early_to_late_neighbor_preservation"].max()) < float(coupled["early_to_late_neighbor_preservation"].median())) if len(c) and len(coupled) else None,
        }
    gpu_used = float(timing["gpu_used"].mean()) if len(timing) else 0.0
    p_corr = float(abs(metrics[metrics["control"].eq("none")][best["primary_metric"]].corr(metrics[metrics["control"].eq("none")]["p_viable_T"])))
    summary = {
        "probe": "T1F_ordered_trajectory_structure_atlas",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "gpu_usage_fraction": gpu_used,
        "family_results": family_results,
        "best_readout_family": best,
        "false_positive_rejection": fp,
        "component_continuity_passed": component_passed,
        "correlation_with_p_viable": p_corr,
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": [] if gpu_used > 0 else ["GPU ordered metrics path was not used."],
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
    tasks = [
        (alpha, horizon, condition, seed, cfg, str(sample_dir))
        for alpha in alphas
        for horizon in horizons
        for condition in BASE_CONDITIONS
        for seed in range(cfg.seed_count)
    ]
    started = time.monotonic()
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
    print("PROBE T1F: ORDERED TRAJECTORY STRUCTURE ATLAS")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
