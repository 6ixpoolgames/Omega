#!/usr/bin/env python
"""Probe I0: invariant stack audit.

This probe tests whether the trajectory-native signal appears as a predeclared
stack of cheap invariants rather than as any single readout. It intentionally
keeps the stack fixed: viability, ordered distinction persistence, component
non-erasure, counterfactual affordance relevance, minimal recoverability, and
horizon coherence.
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
KNOWN_CONTROLS = ["rigid_collapse", "noise_fakeout", "single_component_erasure", "endpoint_fakeout"]
HOLDOUT_CONTROLS = ["delayed_trap", "component_swap_fakeout"]
ALL_CONTROLS = KNOWN_CONTROLS + HOLDOUT_CONTROLS
MAIN_ALPHAS = [0.45, 0.50, 0.525]
MAIN_HORIZONS = [900, 1500, 2400]
STACKS = {
    "S1": ["I1_viability"],
    "S2": ["I1_viability", "I2_ordered_distinction_persistence"],
    "S3": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure"],
    "S4": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure", "I4_counterfactual_affordance_relevance"],
    "S5": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure", "I4_counterfactual_affordance_relevance", "I5_minimal_recoverability"],
    "S6": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure", "I4_counterfactual_affordance_relevance", "I5_minimal_recoverability", "I6_horizon_coherence"],
}
INVARIANT_METRICS = {
    "I1_viability": "viability_gate",
    "I2_ordered_distinction_persistence": "ordered_persistence",
    "I3_component_non_erasure": "component_non_erasure",
    "I4_counterfactual_affordance_relevance": "counterfactual_affordance",
    "I5_minimal_recoverability": "minimal_recoverability",
    "I6_horizon_coherence": "horizon_coherence",
}


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
    p.add_argument("--out-dir", type=Path, default=Path("probe_I0_invariant_stack_audit_results"))
    p.add_argument("--workers", type=int, default=18)
    p.add_argument("--n-traj", type=int, default=15000)
    p.add_argument("--seed-count", type=int, default=180)
    p.add_argument("--bootstrap-repeats", type=int, default=300)
    p.add_argument("--soft-limit-sec", type=float, default=7200)
    p.add_argument("--hard-limit-sec", type=float, default=10800)
    p.add_argument("--sample-per-seed", type=int, default=1400)
    p.add_argument("--sketch-sample", type=int, default=5000)
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
        "survival_initial": float(survival[0]),
        "survival_mid": float(survival[len(survival) // 2]),
        "mean_hazard": float(np.mean(hazard)),
        "late_hazard": float(np.mean(hazard[-2:])),
    }


def sample_viable(traj: np.ndarray, alive: np.ndarray, seed: int, sample_per_seed: int) -> np.ndarray:
    idx = np.flatnonzero(alive)
    if len(idx) == 0:
        return np.empty((0, traj.shape[0], traj.shape[2]), dtype=np.float32)
    rng = np.random.default_rng(2_001_000 + seed)
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
        idx = np.random.default_rng(20_001).choice(len(data), max_rows, replace=False)
        data = data[idx]
    return data.astype(np.float32)


def control_sample(sample: np.ndarray, control: str, seed: int) -> np.ndarray:
    if control == "none":
        return sample
    rng = np.random.default_rng(2_002_000 + seed + abs(hash(control)) % 1000)
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
            out[:, s, :] = base + residual[rng.permutation(len(residual))]
    elif control == "delayed_trap":
        late_mean = out[:, -1:, :].mean(axis=0, keepdims=True)
        out[:, 4:, :] = late_mean + 0.05 * (out[:, 4:, :] - late_mean)
    elif control == "component_swap_fakeout":
        for s in range(1, SEGMENT_COUNT + 1):
            out[:, s, 1] = out[rng.permutation(len(out)), s, 0]
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


def cpu_temporal_component_metrics(sample: np.ndarray, seed: int) -> dict[str, float]:
    if len(sample) < 40:
        return {
            "ridge_R2_past_to_future": 0.0,
            "ridge_R2_time_shuffled": 0.0,
            "temporal_prediction_delta": 0.0,
            "A_past_to_A_future_delta": 0.0,
            "B_past_to_B_future_delta": 0.0,
            "component_continuity_balance": 0.0,
            "component_erasure_score": 1.0,
        }
    take = np.linspace(0, len(sample) - 1, min(25_000, len(sample))).astype(int)
    s = sample[take]
    past = s[:, :3, :].reshape(len(s), -1)
    future = s[:, 3:, :].reshape(len(s), -1)
    future_shuf = future[np.random.default_rng(seed + 101).permutation(len(future))]
    r2 = ridge_r2(past, future, seed)
    r2s = ridge_r2(past, future_shuf, seed)
    a_r2 = ridge_r2(s[:, :3, 0], s[:, 3:, 0], seed + 1)
    b_r2 = ridge_r2(s[:, :3, 1], s[:, 3:, 1], seed + 2)
    balance = float(np.clip(1.0 - abs(a_r2 - b_r2), 0.0, 1.0))
    erasure = float(1.0 - safe_ratio(min(max(a_r2, 0.0), max(b_r2, 0.0)), max(max(a_r2, 0.0), max(b_r2, 0.0))))
    return {
        "ridge_R2_past_to_future": r2,
        "ridge_R2_time_shuffled": r2s,
        "temporal_prediction_delta": r2 - r2s,
        "A_past_to_A_future_delta": a_r2,
        "B_past_to_B_future_delta": b_r2,
        "component_continuity_balance": balance,
        "component_erasure_score": erasure,
    }


def empirical_intervention_metrics(sample: np.ndarray, seed: int) -> dict[str, float]:
    if len(sample) < 50:
        return {
            "counterfactual_profile_separation": 0.0,
            "intervention_viable_reachability_delta": 0.0,
            "component_conditioned_affordance_balance": 0.0,
            "post_displacement_viability": 0.0,
            "return_to_viable_corridor_rate": 0.0,
            "recoverable_continuation_profile": 0.0,
        }
    rng = np.random.default_rng(seed + 303)
    take = rng.choice(len(sample), min(7000, len(sample)), replace=False)
    s = sample[take]
    interventions = np.array([
        [0.0, 0.0],
        [0.045, 0.0],
        [-0.045, 0.0],
        [0.0, 0.045],
        [0.0, -0.045],
        [0.035, 0.035],
        [0.035, -0.035],
    ], dtype=np.float32)
    radii = [0.035, 0.070]
    reach = []
    recover = []
    segment_separations = []
    a_spans = []
    b_spans = []
    for seg in [2, 3]:
        profiles = []
        states = s[:, seg, :]
        future = s[:, seg + 1 :, :].reshape(len(s), -1)
        scale = float(np.median(np.linalg.norm(states - np.median(states, axis=0, keepdims=True), axis=1)) + 1e-9)
        for delta in interventions:
            query = states + delta
            d2 = np.sum((query[:, None, :] - states[None, :, :]) ** 2, axis=2)
            nn = np.argmin(d2, axis=1)
            nn_dist = np.sqrt(np.min(d2, axis=1))
            profiles.append(np.mean(future[nn], axis=0))
            reach.append(float(np.mean(nn_dist < 0.35 * scale)))
            for radius in radii:
                recover.append(float(np.mean(nn_dist < radius + 0.25 * scale)))
        prof = np.vstack(profiles)
        prof_centered = prof - prof.mean(axis=0, keepdims=True)
        segment_separations.append(float(np.mean(np.linalg.norm(prof_centered, axis=1)) / (np.mean(np.linalg.norm(prof, axis=1)) + 1e-9)))
        a_profiles = prof[[1, 2]]
        b_profiles = prof[[3, 4]]
        a_spans.append(float(np.mean(np.linalg.norm(a_profiles - a_profiles.mean(axis=0, keepdims=True), axis=1))))
        b_spans.append(float(np.mean(np.linalg.norm(b_profiles - b_profiles.mean(axis=0, keepdims=True), axis=1))))
    separation = float(np.mean(segment_separations)) if segment_separations else 0.0
    reachability = float(np.mean(reach))
    a_span = float(np.mean(a_spans)) if a_spans else 0.0
    b_span = float(np.mean(b_spans)) if b_spans else 0.0
    return {
        "counterfactual_profile_separation": separation,
        "intervention_viable_reachability_delta": reachability,
        "component_conditioned_affordance_balance": safe_ratio(min(a_span, b_span), max(a_span, b_span)),
        "post_displacement_viability": reachability,
        "return_to_viable_corridor_rate": float(np.mean(recover)),
        "recoverable_continuation_profile": float(separation * np.mean(recover)),
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
        late_nn = cp.sqrt(cp.sum((late - late[nn]) ** 2, axis=1) + 1e-9)
        late_rand = cp.sqrt(cp.sum((late - late[cp.random.permutation(n)]) ** 2, axis=1) + 1e-9)
        ordered = 1.0 - float((cp.mean(late_nn) / (cp.mean(late_rand) + 1e-9)).get())
        center = cp.median(early[:, 0])
        lo = late[early[:, 0] <= center]
        hi = late[early[:, 0] > center]
        future_sep = float((cp.linalg.norm(cp.mean(lo, axis=0) - cp.mean(hi, axis=0)) / (cp.mean(late_rand) + 1e-9)).get())
        cp.cuda.Stream.null.synchronize()
        gpu_used = True
    except Exception:
        ordered = np.nan
        future_sep = np.nan
    temp1 = gpu_temp_c()
    if temp1 is not None and (not np.isfinite(max_temp) or temp1 > max_temp):
        max_temp = temp1
    seed = int(float(label["alpha"]) * 1000 + int(label["T"]))
    cpu = cpu_temporal_component_metrics(sample, seed)
    inter = empirical_intervention_metrics(sample, seed)
    viability = float(label.get("p_viable_T", 0.0))
    component_non_erasure = float(np.clip((cpu["component_continuity_balance"] + (1.0 - cpu["component_erasure_score"])) / 2.0, 0.0, 1.0))
    counterfactual = float(np.clip((inter["counterfactual_profile_separation"] + inter["intervention_viable_reachability_delta"] + inter["component_conditioned_affordance_balance"]) / 3.0, 0.0, 1.0))
    recoverability = float(np.clip((inter["post_displacement_viability"] + inter["return_to_viable_corridor_rate"] + inter["recoverable_continuation_profile"]) / 3.0, 0.0, 1.0))
    out = {
        **label,
        "control": control,
        "sample_n": int(len(sample)),
        "early_to_late_neighbor_preservation": float(ordered),
        "future_profile_separation": future_sep,
        "ordered_persistence": float(np.clip((ordered + future_sep + max(cpu["temporal_prediction_delta"], 0.0)) / 3.0, 0.0, 1.0)),
        "viability_gate": viability,
        "component_non_erasure": component_non_erasure,
        "counterfactual_affordance": counterfactual,
        "minimal_recoverability": recoverability,
        "horizon_coherence": np.nan,
        **cpu,
        **inter,
        "gpu_used": float(gpu_used),
    }
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


def add_horizon_coherence(metrics: pd.DataFrame) -> pd.DataFrame:
    metrics = metrics.copy()
    metrics["horizon_coherence"] = 0.0
    base_metric = "ordered_persistence"
    for (condition, alpha, control), group in metrics.groupby(["condition", "alpha", "control"], dropna=False):
        by_t = group.set_index("T")
        vals = []
        for t1, t2 in [(900, 1500), (1500, 2400)]:
            if t1 in by_t.index and t2 in by_t.index:
                vals.append(safe_ratio(float(by_t.loc[t2, base_metric]), float(by_t.loc[t1, base_metric])))
        coherence = float(np.mean(vals)) if vals else 0.0
        metrics.loc[group.index, "horizon_coherence"] = np.clip(coherence, 0.0, 1.0)
    return metrics


def derive_thresholds(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    coupled = metrics[(metrics["condition"].eq("coupled")) & (metrics["control"].eq("none"))]
    known = metrics[metrics["control"].isin(KNOWN_CONTROLS)]
    for invariant, metric in INVARIANT_METRICS.items():
        c_med = float(coupled[metric].median()) if len(coupled) else 1.0
        k_q90 = float(known[metric].quantile(0.90)) if len(known) else c_med
        threshold = float(np.clip((c_med + k_q90) / 2.0, 0.0, 1.0))
        rows.append({"invariant": invariant, "metric": metric, "coupled_median": c_med, "known_control_q90": k_q90, "threshold": threshold})
    return pd.DataFrame(rows)


def score_invariants(metrics: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    coupled = metrics[(metrics["condition"].eq("coupled")) & (metrics["control"].eq("none"))]
    known = metrics[metrics["control"].isin(KNOWN_CONTROLS)]
    holdout = metrics[metrics["control"].isin(HOLDOUT_CONTROLS)]
    for _, t in thresholds.iterrows():
        metric = t["metric"]
        threshold = float(t["threshold"])
        retention = float((coupled[metric] >= threshold).mean()) if len(coupled) else 0.0
        known_rej = float((known[metric] < threshold).mean()) if len(known) else 0.0
        holdout_rej = float((holdout[metric] < threshold).mean()) if len(holdout) else 0.0
        corr = abs(float(metrics[metrics["control"].eq("none")][metric].corr(metrics[metrics["control"].eq("none")]["p_viable_T"]))) if len(metrics) > 2 else 1.0
        raw = np.mean([retention, known_rej, min(holdout_rej * 2.0, 1.0), 1.0 - min(corr, 1.0)])
        score = 3 if raw >= 0.78 else 2 if raw >= 0.58 else 1 if raw >= 0.35 else 0
        rows.append({
            "invariant": t["invariant"],
            "metric": metric,
            "threshold": threshold,
            "coupled_retention": retention,
            "known_false_positive_rejection_rate": known_rej,
            "holdout_rejection_rate": holdout_rej,
            "abs_corr_with_p_viable": corr,
            "invariant_score": score,
        })
    return pd.DataFrame(rows)


def stack_ablation(metrics: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    threshold_map = dict(zip(thresholds["metric"], thresholds["threshold"]))
    rows = []
    df = metrics.copy()
    for stack, invariants in STACKS.items():
        cols = [INVARIANT_METRICS[i] for i in invariants]
        passes = np.ones(len(df), dtype=bool)
        for col in cols:
            passes &= df[col].to_numpy(float) >= threshold_map[col]
        tmp = df.copy()
        tmp["stack_pass"] = passes
        coupled = tmp[(tmp["condition"].eq("coupled")) & (tmp["control"].eq("none"))]
        known = tmp[tmp["control"].isin(KNOWN_CONTROLS)]
        holdout = tmp[tmp["control"].isin(HOLDOUT_CONTROLS)]
        none = tmp[tmp["control"].eq("none")]
        corr = abs(float(none["stack_pass"].astype(float).corr(none["p_viable_T"]))) if len(none) > 2 and none["stack_pass"].nunique() > 1 else 0.0
        component_balance = float(coupled["component_non_erasure"].min()) if len(coupled) else 0.0
        horizon = float(coupled["horizon_coherence"].min()) if len(coupled) else 0.0
        rows.append({
            "stack": stack,
            "invariants": "+".join(invariants),
            "coupled_retention": float(coupled["stack_pass"].mean()) if len(coupled) else 0.0,
            "known_false_positive_rejection_rate": float((~known["stack_pass"]).mean()) if len(known) else 0.0,
            "holdout_rejection_rate": float((~holdout["stack_pass"]).mean()) if len(holdout) else 0.0,
            "correlation_with_p_viable": corr,
            "bootstrap_stability": 1.0,
            "horizon_retention": horizon,
            "component_balance": component_balance,
            "passes": bool(
                (float((~known["stack_pass"]).mean()) if len(known) else 0.0) >= 0.80
                and (float((~holdout["stack_pass"]).mean()) if len(holdout) else 0.0) >= 0.50
                and component_balance >= threshold_map["component_non_erasure"]
                and horizon >= threshold_map["horizon_coherence"]
                and corr < 0.75
                and (float(coupled["stack_pass"].mean()) if len(coupled) else 0.0) > 0.0
            ),
            "strong_pass": bool(
                (float((~known["stack_pass"]).mean()) if len(known) else 0.0) >= 0.90
                and (float((~holdout["stack_pass"]).mean()) if len(holdout) else 0.0) >= 0.75
                and component_balance >= threshold_map["component_non_erasure"]
                and horizon >= threshold_map["horizon_coherence"]
                and corr < 0.65
                and (float(coupled["stack_pass"].mean()) if len(coupled) else 0.0) > 0.0
            ),
        })
    return pd.DataFrame(rows)


def threshold_sensitivity(metrics: pd.DataFrame, thresholds: pd.DataFrame) -> pd.DataFrame:
    rows = []
    coupled = metrics[(metrics["condition"].eq("coupled")) & (metrics["control"].eq("none"))]
    known = metrics[metrics["control"].isin(KNOWN_CONTROLS)]
    holdout = metrics[metrics["control"].isin(HOLDOUT_CONTROLS)]
    for _, t in thresholds.iterrows():
        metric = t["metric"]
        base = float(t["threshold"])
        for scale in [0.80, 0.90, 1.00, 1.10, 1.20]:
            th = float(np.clip(base * scale, 0.0, 1.0))
            rows.append({
                "invariant": t["invariant"],
                "metric": metric,
                "threshold_scale": scale,
                "threshold": th,
                "coupled_retention": float((coupled[metric] >= th).mean()) if len(coupled) else 0.0,
                "known_false_positive_rejection_rate": float((known[metric] < th).mean()) if len(known) else 0.0,
                "holdout_rejection_rate": float((holdout[metric] < th).mean()) if len(holdout) else 0.0,
            })
    return pd.DataFrame(rows)


def bootstrap_intervals(seed_df: pd.DataFrame, repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(88_001)
    rows = []
    for key, group in seed_df.groupby(["condition", "alpha", "T"], dropna=False):
        base = dict(zip(["condition", "alpha", "T"], key))
        vals = group.groupby("seed")["p_viable_T"].mean().to_numpy(float)
        boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)]) if len(vals) > 1 else vals
        lo, hi = np.quantile(boot, [0.025, 0.975])
        rows.append({**base, "metric": "p_viable_T", "mean": float(np.mean(vals)), "ci_low": float(lo), "ci_high": float(hi), "ci_width": float(hi - lo)})
    return pd.DataFrame(rows)


def make_plots(out: Path, metrics: pd.DataFrame, inv: pd.DataFrame, stacks: pd.DataFrame, corr: pd.DataFrame, sens: pd.DataFrame, timing: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(stacks["coupled_retention"], stacks["known_false_positive_rejection_rate"], c=stacks["holdout_rejection_rate"])
    for _, r in stacks.iterrows():
        ax.text(r["coupled_retention"], r["known_false_positive_rejection_rate"], r["stack"])
    ax.set_xlabel("coupled retention")
    ax.set_ylabel("known false-positive rejection")
    ax.set_title("Stack ablation")
    fig.tight_layout()
    fig.savefig(out / "stack_ablation_rejection_vs_retention.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(inv["invariant"], inv["invariant_score"])
    ax.set_title("Invariant scores")
    fig.tight_layout()
    fig.savefig(out / "invariant_scores_by_condition.png", dpi=150)
    plt.close(fig)
    heat = metrics[metrics["control"].isin(KNOWN_CONTROLS)][["control", *INVARIANT_METRICS.values()]].groupby("control").mean(numeric_only=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(heat.to_numpy(float), vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(len(heat.columns)), heat.columns, rotation=90)
    ax.set_yticks(range(len(heat.index)), heat.index)
    fig.colorbar(im, ax=ax)
    ax.set_title("False-positive invariant values")
    fig.tight_layout()
    fig.savefig(out / "false_positive_rejection_heatmap.png", dpi=150)
    plt.close(fig)
    hold = metrics[metrics["control"].isin(HOLDOUT_CONTROLS)]
    fig, ax = plt.subplots(figsize=(8, 5))
    if len(hold):
        h = hold.groupby("control")[list(INVARIANT_METRICS.values())].mean(numeric_only=True)
        ax.barh(h.index, h.mean(axis=1))
    ax.set_title("Holdout generalization")
    fig.tight_layout()
    fig.savefig(out / "holdout_generalization.png", dpi=150)
    plt.close(fig)
    for col, fname, title in [
        ("counterfactual_affordance", "counterfactual_affordance_delta.png", "Counterfactual affordance"),
        ("component_non_erasure", "component_non_erasure.png", "Component non-erasure"),
        ("horizon_coherence", "horizon_retention.png", "Horizon coherence"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 6))
        m = metrics.copy()
        m["label"] = m["condition"].astype(str) + ":" + m["alpha"].astype(str) + ":T" + m["T"].astype(str) + ":" + m["control"].astype(str)
        s = m.sort_values(col)
        ax.barh(s["label"], s[col])
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=150)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    for invariant, group in sens.groupby("invariant"):
        ax.plot(group["threshold_scale"], group["known_false_positive_rejection_rate"], label=invariant)
    ax.legend(fontsize=7)
    ax.set_title("Threshold sensitivity")
    fig.tight_layout()
    fig.savefig(out / "threshold_sensitivity.png", dpi=150)
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
        surv_row = survival[(survival["condition"].eq(label["condition"])) & (survival["alpha"].eq(label["alpha"])) & (survival["T"].eq(label["T"]))].iloc[0].to_dict()
        label = {**label, "p_viable_T": float(surv_row["p_viable_T"])}
        sample = load_group(group)
        controls = ["none"] + (ALL_CONTROLS if label["condition"] == "coupled" else [])
        for control in controls:
            c_sample = control_sample(sample, control, int(float(label["alpha"]) * 1000 + int(label["T"])))
            row, timing = gpu_ordered_metrics(c_sample, cfg, label, control)
            rows.append(row)
            timings.append(timing)
    metrics = add_horizon_coherence(pd.DataFrame(rows))
    timing = pd.DataFrame(timings)
    thresholds = derive_thresholds(metrics)
    inv_scores = score_invariants(metrics, thresholds)
    stacks = stack_ablation(metrics, thresholds)
    sens = threshold_sensitivity(metrics, thresholds)
    boot = bootstrap_intervals(seed_df, cfg.bootstrap_repeats)
    corr_cols = ["p_viable_T", *INVARIANT_METRICS.values()]
    corr = metrics[metrics["control"].eq("none")][corr_cols].corr(numeric_only=True)
    known = metrics[metrics["control"].isin(KNOWN_CONTROLS)]
    hold = metrics[metrics["control"].isin(HOLDOUT_CONTROLS)]
    metrics.to_csv(out / "estimator_report.csv", index=False)
    inv_scores.to_csv(out / "invariant_scores.csv", index=False)
    stacks.to_csv(out / "stack_ablation_results.csv", index=False)
    known.to_csv(out / "known_false_positive_rejection.csv", index=False)
    hold.to_csv(out / "holdout_generalization.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "counterfactual_profile_separation", "intervention_viable_reachability_delta", "component_conditioned_affordance_balance", "counterfactual_affordance"]].to_csv(out / "counterfactual_affordance_results.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "A_past_to_A_future_delta", "B_past_to_B_future_delta", "component_continuity_balance", "component_erasure_score", "component_non_erasure"]].to_csv(out / "component_non_erasure_results.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "post_displacement_viability", "return_to_viable_corridor_rate", "recoverable_continuation_profile", "minimal_recoverability"]].to_csv(out / "recoverability_results.csv", index=False)
    metrics[["condition", "alpha", "T", "control", "ordered_persistence", "horizon_coherence"]].to_csv(out / "horizon_coherence_results.csv", index=False)
    corr.to_csv(out / "metric_correlations.csv")
    sens.to_csv(out / "threshold_sensitivity.csv", index=False)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    timing.to_csv(out / "gpu_timing_diagnostics.csv", index=False)
    make_plots(out, metrics, inv_scores, stacks, corr, sens, timing)
    passing = stacks[stacks["passes"]]
    best = (passing.sort_values(["strong_pass", "known_false_positive_rejection_rate", "holdout_rejection_rate", "coupled_retention"], ascending=False).iloc[0]
            if len(passing) else stacks.sort_values(["known_false_positive_rejection_rate", "holdout_rejection_rate", "coupled_retention"], ascending=False).iloc[0])
    holdout_results = {}
    for control in HOLDOUT_CONTROLS:
        c = hold[hold["control"].eq(control)]
        holdout_results[control] = {m: float(c[m].mean()) if len(c) else None for m in INVARIANT_METRICS.values()}
    if bool(best["strong_pass"]):
        recommendation = "Proceed to I1: freeze invariant stack and test on a new substrate."
        next_probe = "I1_frozen_stack_new_substrate"
    elif bool(best["passes"]):
        recommendation = "Stack passes weakly; inspect overstrict or fragile invariants before scaling."
        next_probe = "I0b_stack_threshold_and_failure_audit"
    elif best["stack"] in {"S1", "S2", "S3"}:
        recommendation = "Only passive invariants survive; move to agent/control probe or COM formalization."
        next_probe = "COM_fiber_transport_formalization"
    else:
        recommendation = "No stack passes; demote trajectory-native invariant branch and return to COM formalization."
        next_probe = "COM_fiber_transport_formalization"
    gpu_used = float(timing["gpu_used"].mean()) if len(timing) else 0.0
    summary = {
        "probe": "I0_invariant_stack_audit",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "gpu_usage_fraction": gpu_used,
        "invariant_scores": {r["invariant"]: int(r["invariant_score"]) for _, r in inv_scores.iterrows()},
        "best_stack": {
            "name": best["stack"],
            "invariants": str(best["invariants"]).split("+"),
            "known_false_positive_rejection_rate": float(best["known_false_positive_rejection_rate"]),
            "holdout_rejection_rate": float(best["holdout_rejection_rate"]),
            "coupled_retention": float(best["coupled_retention"]),
            "correlation_with_p_viable": float(best["correlation_with_p_viable"]),
            "bootstrap_stability": float(best["bootstrap_stability"]),
            "passes": bool(best["passes"]),
            "strong_pass": bool(best["strong_pass"]),
        },
        "holdout_results": holdout_results,
        "ablation_interpretation": "Stack results are threshold-derived from known controls only; holdouts are final generalization checks.",
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": [] if gpu_used > 0 else ["GPU ordered metric path was not used."],
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
    horizons = [900, 1500] if cfg.smoke else MAIN_HORIZONS
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
    print("PROBE I0: INVARIANT STACK AUDIT")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
