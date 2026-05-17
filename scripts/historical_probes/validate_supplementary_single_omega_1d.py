from __future__ import annotations

import csv
import json
import math
import os
import random
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


WORKERS = int(os.environ.get("OMEGA_WORKERS", "18"))
RESULTS_DIR = Path("supplementary_single_omega_1d_validation_results")
SINK_X = 3.5
DT = 0.01
STEPS = 650
TRAJ_PER_BATCH = 900
BATCHES_PER_CONDITION = 10
NOISE_LEVELS = [0.05, 0.075, 0.1, 0.15, 0.2]
STARTS = {
    "D_degenerate": -5.0,
    "T_trap": -1.5,
    "F_flexible": 1.65,
    "S_sink_adjacent": 3.2,
}
FEATURE_MAPS = ["basin_aware", "geometric", "temporal", "state_marginal"]


def drift(x: float) -> float:
    # Piecewise smooth-ish surrogate for the supplementary 1D potential:
    # deep frozen basin near -5, rigid trap basin near -1.5, shallow flexible
    # shelf near 1.7, and a right-side sink boundary.
    if x < -3.25:
        return -1.05 * (x + 5.0)
    if x < -0.35:
        return -5.0 * (x + 1.5)
    if x < 2.65:
        return -0.22 * (x - 1.65) + 0.08 * math.sin(3.0 * x)
    return 0.65 + 0.35 * (x - 2.65)


def region_label(x: float) -> str:
    if x >= SINK_X:
        return "sink"
    if x < -3.25:
        return "D"
    if x < -0.35:
        return "T"
    if x < 2.65:
        return "F"
    return "edge"


def basin_label(x: float) -> str:
    if x >= SINK_X:
        return "sink"
    if x < -3.25:
        if x < -5.25:
            return "D_left"
        if x > -4.75:
            return "D_right"
        return "D_center"
    if x < -0.35:
        return "T_rigid"
    if x < 2.65:
        if x < 1.0:
            return "F_left"
        if x > 2.1:
            return "F_edge"
        return "F_center"
    return "edge"


def simulate_batch(seed: int, start_name: str, x0: float, noise: float, batch_id: int) -> list[dict]:
    rng = random.Random(seed * 100003 + batch_id * 9176)
    out = []
    sigma = math.sqrt(2.0 * noise * DT)
    for i in range(TRAJ_PER_BATCH):
        x = x0
        xs = [x]
        hit_sink = False
        for _ in range(STEPS):
            x = x + drift(x) * DT + sigma * rng.gauss(0.0, 1.0)
            xs.append(x)
            if x >= SINK_X:
                hit_sink = True
                break
        out.append(
            {
                "start": start_name,
                "noise": noise,
                "viable": not hit_sink,
                "xs": xs,
            }
        )
    return out


def basin_feature(xs: list[float]) -> tuple:
    stride = max(1, len(xs) // 8)
    sampled = [basin_label(x) for x in xs[::stride][:8]]
    labels = tuple(sorted(set(sampled)))
    terminal = basin_label(xs[-1])
    return labels + (terminal, region_label(xs[-1]))


def geometric_feature(xs: list[float]) -> tuple:
    mn = min(xs)
    mx = max(xs)
    terminal = xs[-1]
    span_bin = int(min(12, max(0, math.floor((mx - mn) / 0.35))))
    max_bin = int(min(16, max(0, math.floor((mx + 6.0) / 0.55))))
    min_bin = int(min(16, max(0, math.floor((mn + 6.0) / 0.55))))
    terminal_bin = int(min(16, max(0, math.floor((terminal + 6.0) / 0.55))))
    return span_bin, min_bin, max_bin, terminal_bin


def temporal_feature(xs: list[float]) -> tuple:
    if len(xs) < 4:
        return ("short",)
    chunks = []
    points = [xs[int((len(xs) - 1) * q / 5)] for q in range(6)]
    for a, b in zip(points, points[1:]):
        delta = b - a
        if delta > 0.25:
            chunks.append("up")
        elif delta < -0.25:
            chunks.append("down")
        else:
            chunks.append("flat")
    return tuple(chunks)


def state_marginal_feature(xs: list[float]) -> tuple:
    return (region_label(xs[-1]),)


def feature(xs: list[float], fmap: str) -> tuple:
    if fmap == "basin_aware":
        return basin_feature(xs)
    if fmap == "geometric":
        return geometric_feature(xs)
    if fmap == "temporal":
        return temporal_feature(xs)
    if fmap == "state_marginal":
        return state_marginal_feature(xs)
    raise ValueError(f"unknown feature map: {fmap}")


def entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    acc = 0.0
    for count in counter.values():
        p = count / total
        acc -= p * math.log(p)
    return acc


def evaluate_condition(start_name: str, x0: float, noise: float, seed: int) -> dict:
    trajectories = []
    for batch in range(BATCHES_PER_CONDITION):
        trajectories.extend(simulate_batch(seed, start_name, x0, noise, batch))
    viable = [tr for tr in trajectories if tr["viable"]]
    rows = []
    terminal_all = Counter(region_label(tr["xs"][-1]) for tr in trajectories)
    state_marginal_entropy_all = entropy(terminal_all)
    for fmap in FEATURE_MAPS:
        classes = Counter(feature(tr["xs"], fmap) for tr in viable)
        H = entropy(classes)
        rows.append(
            {
                "start": start_name,
                "x0": x0,
                "noise": noise,
                "feature_map": fmap,
                "num_trajectories": len(trajectories),
                "num_viable": len(viable),
                "p_viable": len(viable) / max(len(trajectories), 1),
                "H_cond_viable": H,
                "N_eff_cond": math.exp(H),
                "H_viability_weighted": H * len(viable) / max(len(trajectories), 1),
                "num_classes": len(classes),
                "terminal_state_marginal_entropy_all": state_marginal_entropy_all,
            }
        )
    return {"rows": rows}


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in keys})
    os.replace(tmp, path)


def summarize(rows: list[dict]) -> tuple[list[dict], dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["start"], row["feature_map"])].append(row)
    summary_rows = []
    for (start, fmap), vals in grouped.items():
        summary_rows.append(
            {
                "start": start,
                "feature_map": fmap,
                "mean_p_viable": sum(float(v["p_viable"]) for v in vals) / len(vals),
                "mean_H_cond_viable": sum(float(v["H_cond_viable"]) for v in vals) / len(vals),
                "mean_H_viability_weighted": sum(float(v["H_viability_weighted"]) for v in vals) / len(vals),
                "mean_N_eff_cond": sum(float(v["N_eff_cond"]) for v in vals) / len(vals),
                "noise_levels": len(vals),
            }
        )
    by_fmap = defaultdict(dict)
    for row in summary_rows:
        by_fmap[row["feature_map"]][row["start"]] = row
    ordering_checks = {}
    for fmap, starts in by_fmap.items():
        F = starts.get("F_flexible", {}).get("mean_H_cond_viable", -1)
        D = starts.get("D_degenerate", {}).get("mean_H_cond_viable", -1)
        T = starts.get("T_trap", {}).get("mean_H_cond_viable", -1)
        ordering_checks[fmap] = {
            "F_gt_D": F > D,
            "D_gt_T": D > T,
            "F_gt_D_gt_T": F > D > T,
            "F": F,
            "D": D,
            "T": T,
        }
    survival = {
        start: sum(float(r["p_viable"]) for r in vals) / len(vals)
        for start, vals in defaultdict(list, {k: [r for r in rows if r["start"] == k and r["feature_map"] == "basin_aware"] for k in STARTS}).items()
    }
    traj_ranges = []
    for fmap in ["basin_aware", "geometric", "temporal"]:
        vals = ordering_checks[fmap]
        traj_ranges.append(max(vals["F"], vals["D"], vals["T"]) - min(vals["F"], vals["D"], vals["T"]))
    state_vals = ordering_checks["state_marginal"]
    state_range = max(state_vals["F"], state_vals["D"], state_vals["T"]) - min(state_vals["F"], state_vals["D"], state_vals["T"])
    sink_state_entropy = next(
        (
            float(r["H_cond_viable"])
            for r in rows
            if r["start"] == "S_sink_adjacent" and r["feature_map"] == "state_marginal" and r["noise"] == NOISE_LEVELS[len(NOISE_LEVELS) // 2]
        ),
        0.0,
    )
    state_marginal_poor = state_range < 0.25 * (sum(traj_ranges) / len(traj_ranges)) or sink_state_entropy >= state_vals["F"]
    flags = {
        "irreversible_sink_filtering_reproduced": survival.get("S_sink_adjacent", 1.0) < survival.get("D_degenerate", 0.0),
        "survival_insufficient_reproduced": abs(survival.get("D_degenerate", 0.0) - survival.get("T_trap", 0.0)) < 0.1
        and any(ordering_checks[f]["D"] > ordering_checks[f]["T"] for f in ["basin_aware", "geometric", "temporal"]),
        "trajectory_feature_ordering_reproduced": all(ordering_checks[f]["F_gt_D_gt_T"] for f in ["basin_aware", "geometric", "temporal"]),
        "noise_robustness_reproduced": True,
        "state_marginal_poor_proxy_reproduced": state_marginal_poor,
        "feature_map_robustness_reproduced": all(ordering_checks[f]["F_gt_D_gt_T"] for f in ["basin_aware", "geometric", "temporal"]),
    }
    # Noise robustness: require F>D>T at each noise for at least two trajectory maps.
    for noise in NOISE_LEVELS:
        ok_maps = 0
        for fmap in ["basin_aware", "geometric", "temporal"]:
            vals = {r["start"]: float(r["H_cond_viable"]) for r in rows if r["noise"] == noise and r["feature_map"] == fmap}
            ok_maps += int(vals.get("F_flexible", -1) > vals.get("D_degenerate", -1) > vals.get("T_trap", -1))
        if ok_maps < 2:
            flags["noise_robustness_reproduced"] = False
    return summary_rows, {"ordering_checks": ordering_checks, "survival": survival, "flags": flags}


def main() -> int:
    start = time.time()
    RESULTS_DIR.mkdir(exist_ok=True)
    futures = []
    rows = []
    seed = int(os.environ.get("OMEGA_VALIDATION_SEED", "20260510"))
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for start_name, x0 in STARTS.items():
            for noise in NOISE_LEVELS:
                futures.append(pool.submit(evaluate_condition, start_name, x0, noise, seed))
        for fut in as_completed(futures):
            rows.extend(fut.result()["rows"])
    summary_rows, summary = summarize(rows)
    summary.update(
        {
            "runtime_seconds": time.time() - start,
            "workers": WORKERS,
            "dt": DT,
            "steps": STEPS,
            "trajectory_horizon": DT * STEPS,
            "trajectories_per_condition": TRAJ_PER_BATCH * BATCHES_PER_CONDITION,
            "noise_levels": NOISE_LEVELS,
            "starts": STARTS,
            "seed": seed,
            "reconstruction_note": "Sanity-check reconstruction from supplementary text; exact original potential/code was not available.",
        }
    )
    write_csv(RESULTS_DIR / "condition_feature_metrics.csv", rows)
    write_csv(RESULTS_DIR / "summary_by_start_and_feature.csv", summary_rows)
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nSUPPLEMENTARY SINGLE OMEGA 1D VALIDATION")
    print(f"- runtime: {summary['runtime_seconds']:.2f}s")
    print(f"- workers: {WORKERS}")
    print(f"- trajectories per start/noise: {summary['trajectories_per_condition']}")
    for key, value in summary["flags"].items():
        print(f"- {key}: {str(value).lower()}")
    print(f"- results: {RESULTS_DIR.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
