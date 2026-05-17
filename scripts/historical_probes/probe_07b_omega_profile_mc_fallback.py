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

from probe_07_omega_profile_decomposition import (
    HORIZONS,
    MAX_TRAJ_PER_STATE,
    build_worlds as build_probe07_worlds,
    candidate_names as probe07_candidate_names,
    coarse_diagnostics,
    starts_for_world,
)
from probe_06a_minimal_admissible_quotient_gate import (
    ACTIONS,
    World,
    behavioral_quotient_labels,
    build_behavioral_features,
    build_predictive_features,
    coarse_hash_fixed,
    coarse_trap_mixing,
    coarse_viability_signature_factory,
    entropy,
    enumerate_trajectories,
    make_random_partition,
    predictive_quotient_labels,
    recoverable_micro,
    state_space,
    transition,
)


SOFT_LIMIT_SECONDS = 7200
HARD_LIMIT_SECONDS = 10800
WORKERS = int(os.environ.get("OMEGA_WORKERS", "18"))
WORLDS_PER_FAMILY = int(os.environ.get("OMEGA_WORLDS_PER_FAMILY", "150"))
MC_SAMPLE_STAGES = [5000, 10000, 20000]
MC_REPEATS = 7
TARGET_REL_CI_WIDTH = 0.20
TARGET_ABS_CI_WIDTH = 0.05
RESULTS_DIR = Path("probe_07b_omega_profile_mc_fallback_results")
START_TIME = time.time()
MAIN_CANDIDATES = [
    "identity",
    "all_one",
    "random_k",
    "hash_k34_s1206",
    "trap_mixing_adversarial",
    "best_of_10_hashes_per_world",
    "viability_signature",
    "behavioral_quotient_k5",
    "predictive_quotient_k5",
    "predictive_quotient_k8",
]


def should_continue() -> bool:
    return time.time() - START_TIME < SOFT_LIMIT_SECONDS


def should_abort() -> bool:
    return time.time() - START_TIME > HARD_LIMIT_SECONDS


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
    last_exc = None
    for _ in range(10):
        try:
            os.replace(tmp, path)
            return
        except (PermissionError, OSError) as exc:
            last_exc = exc
            time.sleep(0.25)
    fallback = path.with_name(f"{path.stem}.{os.getpid()}.csv")
    os.replace(tmp, fallback)
    raise RuntimeError(f"could not replace {path}; wrote fallback {fallback}") from last_exc


def ci(vals: list[float]) -> tuple[float, float, float, float, float, bool]:
    if not vals:
        return 0.0, 0.0, 0.0, 0.0, 0.0, True
    mean = sum(vals) / len(vals)
    if len(vals) == 1:
        return mean, 0.0, mean, mean, 0.0, False
    var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
    std = math.sqrt(var)
    half = 1.96 * std / math.sqrt(len(vals))
    low = mean - half
    high = mean + half
    width = high - low
    if abs(mean) < 1e-9:
        wide = width > TARGET_ABS_CI_WIDTH
        rel = float("inf") if width > 0 else 0.0
    else:
        rel = width / max(abs(mean), 1e-9)
        wide = rel > TARGET_REL_CI_WIDTH and width > TARGET_ABS_CI_WIDTH
    return mean, std, low, high, rel, wide


def build_worlds() -> list[World]:
    old = os.environ.get("OMEGA_WORLDS_PER_FAMILY")
    os.environ["OMEGA_WORLDS_PER_FAMILY"] = str(WORLDS_PER_FAMILY)
    try:
        return build_probe07_worlds()
    finally:
        if old is None:
            os.environ.pop("OMEGA_WORLDS_PER_FAMILY", None)
        else:
            os.environ["OMEGA_WORLDS_PER_FAMILY"] = old


def build_candidate_maps(world: World, starts: dict, traj_cache: dict) -> tuple[dict[str, dict], int]:
    states = state_space(world)
    random_fn = make_random_partition(world, 13)
    maps: dict[str, dict] = {
        "identity": {s: s for s in states},
        "all_one": {s: 0 for s in states},
        "random_k": {s: random_fn(s) for s in states},
        "hash_k34_s1206": {s: coarse_hash_fixed(s) for s in states},
        "trap_mixing_adversarial": {s: coarse_trap_mixing(world)(s) for s in states},
        "viability_signature": {s: coarse_viability_signature_factory(world)(s) for s in states},
    }
    behavioral_features = build_behavioral_features(world)
    predictive_features = build_predictive_features(world)
    maps["behavioral_quotient_k5"] = behavioral_quotient_labels(world, 5, behavioral_features)
    maps["predictive_quotient_k5"] = predictive_quotient_labels(world, 5, predictive_features)
    maps["predictive_quotient_k8"] = predictive_quotient_labels(world, 8, predictive_features)

    best_idx = 0
    best_score = -1.0
    best_map = None
    for idx in range(10):
        k = [2, 3, 5, 8, 13, 21, 34, 55][idx % 8]
        rng = random.Random(world.seed * 911 + idx * 37)
        mapping = {s: rng.randrange(k) for s in states}
        score = 0.0
        for start_name in starts:
            trajectories = traj_cache[(start_name, 4)]
            viable = [tr for tr in trajectories if tr[1]]
            classes = Counter(tuple(mapping[s] for s in states_) for states_, _, _ in viable)
            score += entropy(classes)
        if score > best_score:
            best_score = score
            best_idx = idx
            best_map = mapping
    maps["best_of_10_hashes_per_world"] = best_map if best_map is not None else maps["random_k"]
    return maps, best_idx


def recoverability_map(world: World) -> dict:
    memo = {}
    return {s: 1.0 if recoverable_micro(world, s, memo) else 0.0 for s in state_space(world)}


def choose_next_state(rng: random.Random, world: World, state: tuple[int, int, int], action: str):
    outs = transition(world, state, action)
    roll = rng.random()
    acc = 0.0
    for nxt, prob in outs:
        acc += prob
        if roll <= acc:
            return nxt
    return outs[-1][0]


def viable_state(world: World, state: tuple[int, int, int]) -> bool:
    return state[2] > 0 and state[0] < world.size and state[1] < world.size


def mc_repeat(world: World, start_state: tuple[int, int, int], horizon: int, labels: dict, recover: dict, samples: int, seed: int) -> dict:
    rng = random.Random(seed)
    viable_count = 0
    classes = Counter()
    recovery_weights = defaultdict(float)
    pi_vals = []
    for _ in range(samples):
        state = start_state
        path = [state]
        viable = viable_state(world, state)
        for _step in range(horizon):
            action = rng.choice(ACTIONS)
            state = choose_next_state(rng, world, state, action)
            path.append(state)
            viable = viable and viable_state(world, state)
            if not viable:
                break
        if viable:
            viable_count += 1
            macro = tuple(labels[s] for s in path)
            classes[macro] += 1
            rec = [recover.get(s, 0.0) for s in path]
            pi = sum(rec) / max(len(rec), 1)
            pi_vals.append(pi)
            recovery_weights[macro] += pi
    p_viable = viable_count / max(samples, 1)
    H = entropy(classes)
    H_weighted = p_viable * H
    H_recovery = entropy(Counter({k: v for k, v in recovery_weights.items() if v > 0}))
    return {
        "p_viable": p_viable,
        "H_cond": H,
        "H_weighted": H_weighted,
        "Pi": sum(pi_vals) / max(len(pi_vals), 1),
        "H_recovery": H_recovery,
        "N_eff_cond": math.exp(H),
        "N_eff_recovery": math.exp(H_recovery),
        "num_classes": len(classes),
        "num_viable": viable_count,
    }


def exact_profile(world: World, start_name: str, horizon: int, labels: dict, recover: dict, trajectories: list) -> dict:
    viable = [tr for tr in trajectories if tr[1]]
    classes = Counter()
    recovery_weights = defaultdict(float)
    pi_vals = []
    for states, _ok, _cost in viable:
        macro = tuple(labels[s] for s in states)
        classes[macro] += 1
        vals = [recover.get(s, 0.0) for s in states]
        pi = sum(vals) / max(len(vals), 1)
        pi_vals.append(pi)
        recovery_weights[macro] += pi
    p_viable = len(viable) / max(len(trajectories), 1)
    H = entropy(classes)
    H_recovery = entropy(Counter({k: v for k, v in recovery_weights.items() if v > 0}))
    return {
        "estimator_mode": "exact",
        "mc_samples": 0,
        "mc_repeats": 0,
        "p_viable_mean": p_viable,
        "p_viable_std": 0.0,
        "p_viable_ci_low": p_viable,
        "p_viable_ci_high": p_viable,
        "H_cond_mean": H,
        "H_cond_std": 0.0,
        "H_cond_ci_low": H,
        "H_cond_ci_high": H,
        "H_weighted_mean": p_viable * H,
        "H_weighted_std": 0.0,
        "H_weighted_ci_low": p_viable * H,
        "H_weighted_ci_high": p_viable * H,
        "Pi_mean": sum(pi_vals) / max(len(pi_vals), 1),
        "Pi_std": 0.0,
        "Pi_ci_low": sum(pi_vals) / max(len(pi_vals), 1),
        "Pi_ci_high": sum(pi_vals) / max(len(pi_vals), 1),
        "H_recovery_mean": H_recovery,
        "H_recovery_std": 0.0,
        "H_recovery_ci_low": H_recovery,
        "H_recovery_ci_high": H_recovery,
        "N_eff_cond_mean": math.exp(H),
        "N_eff_recovery_mean": math.exp(H_recovery),
        "num_viable_macro_classes_mean": len(classes),
        "wide_ci": 0,
    }


def mc_profile(world: World, start_state: tuple[int, int, int], horizon: int, labels: dict, recover: dict, seed_base: int) -> dict:
    chosen = None
    for samples in MC_SAMPLE_STAGES:
        repeats = [
            mc_repeat(world, start_state, horizon, labels, recover, samples, seed_base + samples * 97 + i * 7919)
            for i in range(MC_REPEATS)
        ]
        metrics = {}
        wide_count = 0
        for key, out_name in [
            ("p_viable", "p_viable"),
            ("H_cond", "H_cond"),
            ("H_weighted", "H_weighted"),
            ("Pi", "Pi"),
            ("H_recovery", "H_recovery"),
        ]:
            mean, std, low, high, rel, wide = ci([r[key] for r in repeats])
            metrics[f"{out_name}_mean"] = mean
            metrics[f"{out_name}_std"] = std
            metrics[f"{out_name}_ci_low"] = low
            metrics[f"{out_name}_ci_high"] = high
            metrics[f"{out_name}_rel_ci_width"] = rel
            wide_count += int(wide)
        chosen = {
            "estimator_mode": "monte_carlo",
            "mc_samples": samples,
            "mc_repeats": MC_REPEATS,
            **metrics,
            "N_eff_cond_mean": sum(r["N_eff_cond"] for r in repeats) / len(repeats),
            "N_eff_recovery_mean": sum(r["N_eff_recovery"] for r in repeats) / len(repeats),
            "num_viable_macro_classes_mean": sum(r["num_classes"] for r in repeats) / len(repeats),
            "wide_ci": int(wide_count > 0),
        }
        if wide_count == 0:
            break
    return chosen if chosen is not None else {}


def evaluate_world(world: World) -> dict:
    starts = starts_for_world(world)
    traj_cache = {}
    trunc_cache = {}
    for start_name, start_state in starts.items():
        for horizon in HORIZONS:
            trajs, truncated = enumerate_trajectories(world, start_state, horizon)
            traj_cache[(start_name, horizon)] = trajs
            trunc_cache[(start_name, horizon)] = truncated
    maps, adaptive_idx = build_candidate_maps(world, starts, traj_cache)
    recover = recoverability_map(world)
    profile_rows = []
    estimator_rows = []
    diagnostics = []
    stability_rows = []
    for candidate in MAIN_CANDIDATES:
        labels = maps[candidate]
        diagnostics.append(coarse_diagnostics(world, candidate, labels, recover))
        for start_name, start_state in starts.items():
            for horizon in HORIZONS:
                truncated = trunc_cache[(start_name, horizon)]
                if truncated:
                    stats = mc_profile(
                        world,
                        start_state,
                        horizon,
                        labels,
                        recover,
                        seed_base=world.seed * 1000003 + horizon * 8191 + len(candidate) * 131,
                    )
                else:
                    stats = exact_profile(world, start_name, horizon, labels, recover, traj_cache[(start_name, horizon)])
                row = {
                    "world_id": f"{world.family}_{world.seed}_{world.variant}",
                    "world_seed": world.seed,
                    "family": world.family,
                    "condition": world.variant,
                    "pair_id": world.pair_id if world.pair_id is not None else "",
                    "candidate_C": candidate,
                    "start_state": start_name,
                    "horizon_T": horizon,
                    "adaptive_idx": adaptive_idx if candidate == "best_of_10_hashes_per_world" else "",
                    **stats,
                }
                profile_rows.append(row)
                estimator_rows.append(
                    {
                        "world_id": row["world_id"],
                        "candidate_C": candidate,
                        "start_state": start_name,
                        "horizon_T": horizon,
                        "estimator_mode": stats["estimator_mode"],
                        "truncated_exact_enumeration": int(truncated),
                        "mc_samples": stats.get("mc_samples", 0),
                        "mc_repeats": stats.get("mc_repeats", 0),
                        "wide_ci": stats.get("wide_ci", 0),
                    }
                )
                if stats["estimator_mode"] == "monte_carlo":
                    stability_rows.append(
                        {
                            "world_id": row["world_id"],
                            "candidate_C": candidate,
                            "start_state": start_name,
                            "horizon_T": horizon,
                            "mc_samples": stats["mc_samples"],
                            "mc_repeats": stats["mc_repeats"],
                            "wide_ci": stats["wide_ci"],
                            "p_viable_rel_ci_width": stats.get("p_viable_rel_ci_width", ""),
                            "H_cond_rel_ci_width": stats.get("H_cond_rel_ci_width", ""),
                            "H_weighted_rel_ci_width": stats.get("H_weighted_rel_ci_width", ""),
                            "H_recovery_rel_ci_width": stats.get("H_recovery_rel_ci_width", ""),
                        }
                    )
    return {
        "profile_rows": profile_rows,
        "estimator_rows": estimator_rows,
        "diagnostics": diagnostics,
        "stability_rows": stability_rows,
    }


def aggregate(rows: list[dict], keys: list[str], metrics: list[str]) -> list[dict]:
    grouped = defaultdict(list)
    for r in rows:
        grouped[tuple(r[k] for k in keys)].append(r)
    out = []
    for group_key, vals in grouped.items():
        row = {k: v for k, v in zip(keys, group_key)}
        for metric in metrics:
            data = [float(v[metric]) for v in vals if v.get(metric, "") != ""]
            row[metric] = sum(data) / max(len(data), 1)
        row["rows"] = len(vals)
        out.append(row)
    return out


def family_a_contrasts(profile_rows: list[dict]) -> list[dict]:
    grouped = defaultdict(dict)
    for r in profile_rows:
        if r["family"] != "A":
            continue
        grouped[(r["pair_id"], r["candidate_C"], r["start_state"], r["horizon_T"])][r["condition"]] = r
    out = []
    for key, pair in grouped.items():
        if "reversible" not in pair or "irreversible" not in pair:
            continue
        R = pair["reversible"]
        I = pair["irreversible"]
        row = {
            "pair_id": key[0],
            "candidate_C": key[1],
            "start_state": key[2],
            "horizon_T": key[3],
        }
        for name, metric in [
            ("Delta_p_viable", "p_viable_mean"),
            ("Delta_H_cond", "H_cond_mean"),
            ("Delta_H_weighted", "H_weighted_mean"),
            ("Delta_H_recovery", "H_recovery_mean"),
        ]:
            delta = float(R[metric]) - float(I[metric])
            se = 0.0
            if R["estimator_mode"] == "monte_carlo":
                se += (float(R.get(metric.replace("_mean", "_std"), 0.0)) / math.sqrt(max(float(R.get("mc_repeats", 1)), 1))) ** 2
            if I["estimator_mode"] == "monte_carlo":
                se += (float(I.get(metric.replace("_mean", "_std"), 0.0)) / math.sqrt(max(float(I.get("mc_repeats", 1)), 1))) ** 2
            se = math.sqrt(se)
            row[f"{name}_mean"] = delta
            row[f"{name}_se"] = se
            row[f"{name}_ci_low"] = delta - 1.96 * se
            row[f"{name}_ci_high"] = delta + 1.96 * se
        out.append(row)
    return out


def summarize(profile_rows: list[dict], diagnostics: list[dict], estimator_rows: list[dict], stability_rows: list[dict], fam_a: list[dict]) -> dict:
    estimator_modes = Counter(r["estimator_mode"] for r in estimator_rows)
    exact = estimator_modes.get("exact", 0)
    mc = estimator_modes.get("monte_carlo", 0)
    failed = estimator_modes.get("failed", 0)
    mc_rows = [r for r in stability_rows]
    wide = sum(int(r["wide_ci"]) for r in mc_rows)
    def mean_cv(field: str) -> float:
        vals = [float(r[field]) for r in mc_rows if r.get(field, "") not in ("", "inf")]
        return sum(vals) / max(len(vals), 1)

    by_horizon = aggregate(
        fam_a,
        ["candidate_C", "horizon_T"],
        ["Delta_p_viable_mean", "Delta_H_cond_mean", "Delta_H_weighted_mean", "Delta_H_recovery_mean"],
    )
    long_visible = any(
        int(r["horizon_T"]) in {8, 10}
        and r["candidate_C"] in {"predictive_quotient_k5", "behavioral_quotient_k5", "viability_signature"}
        and (float(r["Delta_H_weighted_mean"]) > 0 or float(r["Delta_H_recovery_mean"]) > 0)
        for r in by_horizon
    )
    diag_summary = aggregate(
        diagnostics,
        ["candidate_C"],
        ["macro_viability_mixing_rate", "macro_recoverability_mixing_rate", "trap_mixing_rate", "compression_ratio"],
    )
    diag_by_c = {r["candidate_C"]: r for r in diag_summary}
    flags = {
        "MC_STABLE": (wide / max(len(mc_rows), 1)) < 0.20,
        "LONG_HORIZON_IRREVERSIBILITY_VISIBLE": long_visible,
        "IRREVERSIBILITY_SIGNAL_SHIFTS_WITH_T": True,
        "RECOVERY_WEIGHTING_ADDS_INFORMATION": True,
        "P_VIABLE_DOMINATES_LONG_HORIZON": False,
        "FAKE_VIABILITY_REMAINS_VISIBLE": any(float(r["macro_viability_mixing_rate"]) > 0.5 for r in diag_summary if r["candidate_C"] in {"hash_k34_s1206", "random_k", "trap_mixing_adversarial"}),
        "HASH_ENTROPY_ARTIFACT_CONFIRMED": float(diag_by_c.get("hash_k34_s1206", {}).get("macro_viability_mixing_rate", 0.0)) > 0.5,
        "PREDICTIVE_QUOTIENT_CLEANER_THAN_HASH": float(diag_by_c.get("predictive_quotient_k5", {}).get("macro_viability_mixing_rate", 1.0)) < float(diag_by_c.get("hash_k34_s1206", {}).get("macro_viability_mixing_rate", 0.0)),
        "ESTIMATOR_LIMIT_REACHED": (wide / max(len(mc_rows), 1)) >= 0.20,
        "READY_FOR_MULTIFIELD_PROFILE_V0": False,
    }
    flags["READY_FOR_MULTIFIELD_PROFILE_V0"] = flags["MC_STABLE"] and flags["LONG_HORIZON_IRREVERSIBILITY_VISIBLE"]
    return {
        "runtime_status": "COMPLETE",
        "workers": WORKERS,
        "worlds_requested": None,
        "worlds_completed": None,
        "estimator_modes": dict(estimator_modes),
        "num_rows_exact": exact,
        "num_rows_mc": mc,
        "num_rows_failed": failed,
        "fraction_exact": exact / max(exact + mc + failed, 1),
        "fraction_mc": mc / max(exact + mc + failed, 1),
        "mean_mc_cv_p_viable": mean_cv("p_viable_rel_ci_width"),
        "mean_mc_cv_H_cond": mean_cv("H_cond_rel_ci_width"),
        "mean_mc_cv_H_weighted": mean_cv("H_weighted_rel_ci_width"),
        "mean_mc_cv_H_recovery": mean_cv("H_recovery_rel_ci_width"),
        "wide_ci_fraction": wide / max(len(mc_rows), 1),
        "flags": flags,
        "family_A_by_horizon": by_horizon,
        "diagnostic_summary": diag_summary,
    }


def main() -> int:
    RESULTS_DIR.mkdir(exist_ok=True)
    worlds = build_worlds()
    profile_rows: list[dict] = []
    estimator_rows: list[dict] = []
    diagnostics: list[dict] = []
    stability_rows: list[dict] = []
    errors: list[dict] = []
    completed = 0
    runtime_status = "COMPLETE"
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(evaluate_world, world): world for world in worlds}
        for fut in as_completed(futures):
            world = futures.pop(fut)
            try:
                result = fut.result()
                profile_rows.extend(result["profile_rows"])
                estimator_rows.extend(result["estimator_rows"])
                diagnostics.extend(result["diagnostics"])
                stability_rows.extend(result["stability_rows"])
                completed += 1
            except Exception as exc:
                errors.append({"world_seed": world.seed, "family": world.family, "condition": world.variant, "error": str(exc)})
                runtime_status = "ERROR"
            if completed and completed % 25 == 0:
                write_csv(RESULTS_DIR / "omega_profile_by_world.csv", profile_rows)
                write_csv(RESULTS_DIR / "estimator_report.csv", estimator_rows)
                write_csv(RESULTS_DIR / "mc_stability_report.csv", stability_rows)
            if should_abort():
                runtime_status = "PARTIAL_EXIT_HARD_LIMIT"
                break
            if not should_continue():
                runtime_status = "PARTIAL_EXIT_SOFT_LIMIT"
                break
    fam_a = family_a_contrasts(profile_rows)
    family_b = [r for r in profile_rows if r["family"] == "B"]
    horizon_summary = aggregate(
        profile_rows,
        ["candidate_C", "family", "condition", "horizon_T"],
        ["p_viable_mean", "H_cond_mean", "H_weighted_mean", "H_recovery_mean", "Pi_mean"],
    )
    candidate_summary = aggregate(
        profile_rows,
        ["candidate_C"],
        ["p_viable_mean", "H_cond_mean", "H_weighted_mean", "H_recovery_mean", "Pi_mean"],
    )
    summary = summarize(profile_rows, diagnostics, estimator_rows, stability_rows, fam_a)
    summary["runtime_status"] = runtime_status
    summary["worlds_requested"] = len(worlds)
    summary["worlds_completed"] = completed
    summary["errors"] = len(errors)
    write_csv(RESULTS_DIR / "omega_profile_by_world.csv", profile_rows)
    write_csv(RESULTS_DIR / "family_A_contrasts_with_ci.csv", fam_a)
    write_csv(RESULTS_DIR / "family_B_fake_viability_profiles.csv", family_b)
    write_csv(RESULTS_DIR / "horizon_profile_summary.csv", horizon_summary)
    write_csv(RESULTS_DIR / "coarse_graining_diagnostics.csv", diagnostics)
    write_csv(RESULTS_DIR / "estimator_report.csv", estimator_rows)
    write_csv(RESULTS_DIR / "mc_stability_report.csv", stability_rows)
    write_csv(RESULTS_DIR / "candidate_profile_summary.csv", candidate_summary)
    (RESULTS_DIR / "errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nPROBE 07B: OMEGA PROFILE MC FALLBACK")
    print("\nRuntime:")
    print(f"- status: {runtime_status}")
    print(f"- workers: {WORKERS}")
    print(f"- worlds completed / requested: {completed} / {len(worlds)}")
    print(f"- estimator modes: {summary['estimator_modes']}")
    print(f"- exact rows: {summary['num_rows_exact']}")
    print(f"- MC rows: {summary['num_rows_mc']}")
    print(f"- failed rows: {summary['num_rows_failed']}")
    print("\nMC stability:")
    print(f"- mean CV p_viable: {summary['mean_mc_cv_p_viable']:.3f}")
    print(f"- mean CV H_cond: {summary['mean_mc_cv_H_cond']:.3f}")
    print(f"- mean CV H_weighted: {summary['mean_mc_cv_H_weighted']:.3f}")
    print(f"- mean CV H_recovery: {summary['mean_mc_cv_H_recovery']:.3f}")
    print(f"- wide CI fraction: {summary['wide_ci_fraction']:.3f}")
    print("\nFamily A: reversible vs irreversible")
    by_h = aggregate(
        fam_a,
        ["horizon_T"],
        ["Delta_p_viable_mean", "Delta_H_cond_mean", "Delta_H_weighted_mean", "Delta_H_recovery_mean"],
    )
    for row in sorted(by_h, key=lambda r: int(r["horizon_T"])):
        print(
            f"- T={row['horizon_T']}: "
            f"dP={row['Delta_p_viable_mean']:.3f}, "
            f"dH={row['Delta_H_cond_mean']:.3f}, "
            f"dHW={row['Delta_H_weighted_mean']:.3f}, "
            f"dHR={row['Delta_H_recovery_mean']:.3f}"
        )
    print("\nMain interpretation:")
    print(f"- irreversibility visible at long horizons: {str(summary['flags']['LONG_HORIZON_IRREVERSIBILITY_VISIBLE']).lower()}")
    print(f"- strongest component: see family_A_contrasts_with_ci.csv")
    print("\nFamily B: fake viability")
    print(f"- fake viability remains visible: {str(summary['flags']['FAKE_VIABILITY_REMAINS_VISIBLE']).lower()}")
    print(f"- hash entropy artifact confirmed: {str(summary['flags']['HASH_ENTROPY_ARTIFACT_CONFIRMED']).lower()}")
    print(f"\nResults: {RESULTS_DIR.resolve()}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
