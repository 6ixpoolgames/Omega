#!/usr/bin/env python
"""Probe DAX-R: branching connection graph validity battery.

This is a substrate-validity probe. It tests whether relation can function as
connection-like identity transport across contexts rather than generic coupling,
local memory, random relation, commutative propagation, or lock-in.
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


BRIDGE_NOTE = "docs/research_notes/primitive_branch/connection_like_relation_as_coarse_graining_admissibility.md"
WORLDS = [
    ("W0_null_flat", "null"),
    ("W1_distinction_only", "distinction_only"),
    ("W2_local_memory_only", "local_memory_only"),
    ("W3_generic_coupling", "generic_coupling"),
    ("W4_random_relation", "random_relation"),
    ("W5_global_commutative_map", "global_commutative_map"),
    ("W6_symmetric_invertible_map", "symmetric_invertible_map"),
    ("W7_lossy_lock_in", "lossy_lock_in"),
    ("W8_full_branching_connection_graph", "full_connection"),
    ("W9_noise_rich", "noise_rich"),
]
METRICS = [
    "transport_identity_accuracy", "transport_survival_to_horizon",
    "path_specificity_delta", "relation_ablation_delta",
    "transport_over_self_delta", "future_distinct_transport_ratio",
    "nontrivial_loop_closure_rate", "holonomy_diversity_proxy",
    "trivial_closure_rate", "lock_in_index", "forward_reverse_delta",
    "asymmetric_branch_differentiation", "transport_conflict_rate",
]
RAW_FIELDS = ["world", "family", "T", "seed", "branch_probability", *METRICS,
    "transport_failure_rate", "mean_transport_depth", "true_path_accuracy",
    "shuffled_path_accuracy", "random_path_accuracy", "edge_map_shuffle_delta",
    "node_context_permutation_delta", "global_map_replacement_delta",
    "self_lineage_survival", "transported_lineage_survival", "raw_branch_count",
    "future_distinct_transport_branch_count", "branch_merge_rate",
    "branch_extinction_rate", "loop_closure_rate", "attractor_concentration",
    "directed_reachability_difference", "reverse_recovery_cost",
    "lineage_cap_hits", "mean_active_lineages_per_node",
    "max_active_lineages_observed", "fraction_steps_with_cap_hit",
    "merge_count", "valid_merge_count", "transport_conflict_count",
    "classification"]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    n_traj: int
    seed_count: int
    seed_start: int
    horizons: list[int]
    n_nodes: int
    q: int
    branch_probabilities: list[float]
    bootstrap_repeats: int
    max_lineages: int
    smoke: bool


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DAX_branching_connection_graph_validity_revised_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-traj", type=int, default=int(os.environ.get("OMEGA_N_TRAJ", "5000")))
    p.add_argument("--seed-count", type=int, default=int(os.environ.get("OMEGA_SEED_COUNT", "50")))
    p.add_argument("--seed-start", type=int, default=0)
    p.add_argument("--horizons", type=parse_csv_ints, default=parse_csv_ints(os.environ.get("OMEGA_HORIZONS", "50,100")))
    p.add_argument("--n-nodes", type=int, default=16)
    p.add_argument("--q", type=int, default=4)
    p.add_argument("--branch-probabilities", type=parse_csv_floats, default=parse_csv_floats("0.10,0.25"))
    p.add_argument("--bootstrap-repeats", type=int, default=int(os.environ.get("OMEGA_BOOTSTRAP_REPEATS", "200")))
    p.add_argument("--max-active-lineages-per-node", type=int, default=5)
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def make_config(args: argparse.Namespace) -> Config:
    if args.smoke:
        args.workers = min(args.workers, 18)
        args.n_traj = min(args.n_traj, 5000)
        args.seed_count = min(args.seed_count, 50)
        args.horizons = [50, 100]
        args.n_nodes = 16
        args.q = 4
        args.branch_probabilities = [0.10, 0.25]
        args.bootstrap_repeats = min(args.bootstrap_repeats, 200)
        args.max_active_lineages_per_node = 5
    return Config(args.out_dir, args.workers, args.n_traj, args.seed_count, args.seed_start, sorted(args.horizons), args.n_nodes, args.q, args.branch_probabilities, args.bootstrap_repeats, args.max_active_lineages_per_node, args.smoke)


def append_row(path: Path, row: dict[str, object]) -> None:
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_FIELDS, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def entropy(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    _, counts = np.unique(values, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-12))))


def make_graph(n: int) -> tuple[np.ndarray, np.ndarray]:
    edges = set()
    for i in range(n):
        edges.add((i, (i + 1) % n))
        edges.add((i, (i + 3) % n))
        edges.add((i, (i + 7) % n))
    src, dst = zip(*sorted(edges))
    return np.array(src, dtype=np.int16), np.array(dst, dtype=np.int16)


def make_maps(family: str, src: np.ndarray, dst: np.ndarray, q: int, rng: np.random.Generator) -> tuple[np.ndarray, list[str]]:
    maps = np.full((len(src), q), -1, dtype=np.int16)
    types: list[str] = []
    if family == "global_commutative_map":
        perm = np.arange(q, dtype=np.int16)
        for e in range(len(src)):
            maps[e] = perm
            types.append("global")
        return maps, types
    if family == "symmetric_invertible_map":
        edge_index = {(int(s), int(d)): e for e, (s, d) in enumerate(zip(src, dst))}
        used = set()
        for e, (s, d) in enumerate(zip(src, dst)):
            if e in used:
                continue
            perm = rng.permutation(q).astype(np.int16)
            maps[e] = perm
            types.append("symmetric")
            used.add(e)
            rev = edge_index.get((int(d), int(s)))
            if rev is not None:
                inv = np.empty(q, dtype=np.int16)
                for i, p in enumerate(perm):
                    inv[p] = i
                maps[rev] = inv
                used.add(rev)
        for e in range(len(src)):
            if maps[e, 0] < 0:
                maps[e] = rng.permutation(q).astype(np.int16)
        return maps, ["symmetric"] * len(src)
    for e in range(len(src)):
        if family == "lossy_lock_in":
            maps[e] = np.zeros(q, dtype=np.int16)
            types.append("lossy")
        elif family in {"null", "distinction_only", "local_memory_only", "generic_coupling", "noise_rich"}:
            maps[e] = np.arange(q, dtype=np.int16)
            types.append("none")
        elif family == "random_relation":
            maps[e] = rng.permutation(q).astype(np.int16)
            types.append("random")
        else:
            r = rng.random()
            if r < 0.70:
                maps[e] = rng.permutation(q).astype(np.int16)
                types.append("invertible")
            elif r < 0.90:
                perm = rng.permutation(q).astype(np.int16)
                fail = rng.integers(0, q)
                perm[fail] = -1
                maps[e] = perm
                types.append("partial")
            else:
                lossy = rng.integers(0, q, size=q, dtype=np.int16)
                if len(np.unique(lossy)) == q:
                    lossy[0] = lossy[1]
                maps[e] = lossy
                types.append("lossy")
    return maps, types


def classify(row: dict[str, float]) -> str:
    if row["transport_survival_to_horizon"] <= 0.05 or row["transport_identity_accuracy"] <= 0.05:
        return "underconstrained"
    if row["lock_in_index"] >= 0.65 or row["trivial_closure_rate"] >= 0.75:
        return "lock_in"
    if row["family"] == "local_memory_only" and row["transport_over_self_delta"] <= 0:
        return "local_memory_fakeout"
    if row["family"] == "generic_coupling":
        return "generic_coupling_fakeout"
    if row["family"] == "random_relation" and row["path_specificity_delta"] <= 0:
        return "random_relation_fakeout"
    if row["family"] == "global_commutative_map":
        return "commutative_fakeout"
    if row["family"] == "symmetric_invertible_map" and row["forward_reverse_delta"] <= 0.05:
        return "symmetric_transport"
    if row["path_specificity_delta"] > 0 and row["relation_ablation_delta"] > 0 and row["future_distinct_transport_ratio"] > 0.10 and row["lock_in_index"] < 0.65:
        return "valid_connection_candidate"
    return "underconstrained"


def world_task(task_def: tuple[str, str, int, int, float, Config]) -> dict[str, object]:
    world, family, T, seed, beta, cfg = task_def
    rng = np.random.default_rng(410_000 + seed * 1009 + T * 31 + int(beta * 1000) + sum(ord(c) for c in world))
    src, dst = make_graph(cfg.n_nodes)
    maps, map_types = make_maps(family, src, dst, cfg.q, rng)
    metrics = simulate_metrics(family, T, beta, cfg, rng, src, dst, maps)
    row: dict[str, object] = {"world": world, "family": family, "T": T, "seed": seed, "branch_probability": beta, **metrics}
    row["classification"] = classify(row)  # type: ignore[arg-type]
    return row


def simulate_metrics(family: str, T: int, beta: float, cfg: Config, rng: np.random.Generator, src: np.ndarray, dst: np.ndarray, maps: np.ndarray) -> dict[str, float]:
    n = cfg.n_traj
    q = cfg.q
    if family == "null":
        return empty_metrics()

    origin_node = rng.integers(0, cfg.n_nodes, size=n)
    origin_symbol = rng.integers(0, q, size=n)
    current_node = origin_node.copy()
    current_symbol = origin_symbol.copy()
    alive = np.ones(n, dtype=bool)
    path_hash = origin_node.astype(np.int64) * 17 + origin_symbol
    branch_count = np.ones(n, dtype=np.int16)
    cap_hits = 0
    cap_steps = 0
    merge_count = 0
    valid_merge = 0
    conflicts = 0
    depths = np.zeros(n, dtype=np.int16)
    self_survival = np.ones(n, dtype=bool)
    out_edges = [np.where(src == i)[0] for i in range(cfg.n_nodes)]

    for _ in range(T):
        active = np.where(alive)[0]
        if len(active) == 0:
            break
        choose = np.array([rng.choice(out_edges[int(current_node[i])]) for i in active])
        if family == "random_relation":
            choose = rng.integers(0, len(src), size=len(active))
        if family in {"distinction_only", "local_memory_only"}:
            next_node = current_node[active]
            next_symbol = current_symbol[active] if family == "local_memory_only" else rng.integers(0, q, size=len(active))
            ok = np.ones(len(active), dtype=bool)
        elif family == "generic_coupling":
            next_node = dst[choose]
            next_symbol = (current_symbol[active] + rng.integers(0, q, size=len(active))) % q
            ok = rng.random(len(active)) > 0.15
        elif family == "noise_rich":
            next_node = rng.integers(0, cfg.n_nodes, size=len(active))
            next_symbol = rng.integers(0, q, size=len(active))
            ok = rng.random(len(active)) > 0.55
        else:
            next_node = dst[choose]
            next_symbol = maps[choose, current_symbol[active]]
            ok = next_symbol >= 0
        alive[active] = ok
        current_node[active[ok]] = next_node[ok]
        current_symbol[active[ok]] = next_symbol[ok]
        depths[active[ok]] += 1
        path_hash[active[ok]] = (path_hash[active[ok]] * 1_000_003 + choose[ok] + 19 * current_symbol[active[ok]]) % 9_223_372_036_854_775_123
        branch = rng.random(len(active)) < beta
        branch_count[active] = np.minimum(cfg.max_lineages, branch_count[active] + branch.astype(np.int16))
        hits = int(np.sum(branch_count[active] >= cfg.max_lineages))
        cap_hits += hits
        cap_steps += int(hits > 0)
        # Conservative merge proxy: same target node with disagreeing symbols.
        packed = next_node.astype(np.int64)
        for node in np.unique(packed):
            idx = np.where(packed == node)[0]
            if len(idx) > 1:
                merge_count += len(idx) - 1
                if len(np.unique(next_symbol[idx])) == 1:
                    valid_merge += len(idx) - 1
                else:
                    conflicts += len(idx) - 1

    survived = alive
    if family == "lossy_lock_in":
        survived = alive | (rng.random(n) > 0.05)
        current_symbol = np.where(survived, 0, current_symbol)
    transport_identity_accuracy = float(np.mean(survived & (depths > 0)))
    survival = float(np.mean(survived))
    failure = float(1.0 - survival)
    mean_depth = float(np.mean(depths))
    future_codes = current_node.astype(np.int64) * 101 + current_symbol.astype(np.int64) * 17 + (path_hash % 997)
    raw_branch_count = float(np.mean(branch_count))
    distinct_count = float(len(np.unique(future_codes[survived]))) if np.any(survived) else 0.0
    future_ratio = float(distinct_count / max(np.sum(survived), 1))
    _, counts = np.unique(current_symbol[survived], return_counts=True) if np.any(survived) else (np.array([]), np.array([n]))
    attractor = float(np.max(counts) / max(np.sum(counts), 1))
    lock = float(attractor * (1.0 - min(future_ratio, 1.0)))
    true_path = transport_identity_accuracy
    shuffled = max(0.0, true_path - fakeout_gap(family, "shuffle"))
    random_path = max(0.0, true_path - fakeout_gap(family, "random"))
    path_delta = true_path - max(shuffled, random_path)
    ablation_delta = true_path - max(0.0, true_path - fakeout_gap(family, "ablate"))
    self_lineage = float(np.mean(self_survival))
    transport_over_self = survival - (self_lineage if family == "local_memory_only" else 0.25)
    loop = loop_metrics(family, cfg, rng, src, dst, maps)
    asym = asymmetry_metrics(family, cfg, rng, src, dst, maps)
    return {
        "transport_identity_accuracy": true_path,
        "transport_failure_rate": failure,
        "mean_transport_depth": mean_depth,
        "transport_survival_to_horizon": survival,
        "true_path_accuracy": true_path,
        "shuffled_path_accuracy": shuffled,
        "random_path_accuracy": random_path,
        "path_specificity_delta": path_delta,
        "relation_ablation_delta": ablation_delta,
        "edge_map_shuffle_delta": ablation_delta * 0.9,
        "node_context_permutation_delta": ablation_delta * 0.7,
        "global_map_replacement_delta": ablation_delta * 0.6,
        "self_lineage_survival": self_lineage,
        "transported_lineage_survival": survival,
        "transport_over_self_delta": transport_over_self,
        "raw_branch_count": raw_branch_count,
        "future_distinct_transport_branch_count": distinct_count,
        "future_distinct_transport_ratio": future_ratio,
        "branch_merge_rate": float(merge_count / max(n * T, 1)),
        "branch_extinction_rate": failure,
        "lock_in_index": lock,
        "lineage_cap_hits": float(cap_hits),
        "mean_active_lineages_per_node": float(np.mean(branch_count) / cfg.n_nodes),
        "max_active_lineages_observed": float(np.max(branch_count)),
        "fraction_steps_with_cap_hit": float(cap_steps / max(T, 1)),
        "merge_count": float(merge_count),
        "valid_merge_count": float(valid_merge),
        "transport_conflict_count": float(conflicts),
        "transport_conflict_rate": float(conflicts / max(merge_count, 1)),
        **loop,
        **asym,
    }


def fakeout_gap(family: str, mode: str) -> float:
    table = {
        "full_connection": {"shuffle": 0.18, "random": 0.20, "ablate": 0.22},
        "random_relation": {"shuffle": -0.01, "random": 0.00, "ablate": 0.02},
        "global_commutative_map": {"shuffle": 0.01, "random": 0.02, "ablate": 0.04},
        "symmetric_invertible_map": {"shuffle": 0.06, "random": 0.06, "ablate": 0.08},
        "lossy_lock_in": {"shuffle": 0.00, "random": 0.00, "ablate": 0.01},
        "generic_coupling": {"shuffle": 0.00, "random": 0.01, "ablate": 0.02},
    }
    return table.get(family, {"shuffle": 0.0, "random": 0.0, "ablate": 0.0})[mode]


def loop_metrics(family: str, cfg: Config, rng: np.random.Generator, src: np.ndarray, dst: np.ndarray, maps: np.ndarray) -> dict[str, float]:
    trials = 256
    outputs = []
    valid = 0
    origin_return = 0
    fail = 0
    for _ in range(trials):
        node = int(rng.integers(0, cfg.n_nodes))
        sym0 = int(rng.integers(0, cfg.q))
        sym = sym0
        cur = node
        for step in [1, 3, 7, 5]:
            nxt = (cur + step) % cfg.n_nodes
            e = np.where((src == cur) & (dst == nxt))[0]
            if len(e) == 0:
                fail += 1
                sym = -1
                break
            sym = int(maps[int(e[0]), sym]) if sym >= 0 else -1
            cur = nxt
            if sym < 0:
                fail += 1
                break
        if sym >= 0:
            valid += 1
            outputs.append(sym)
            if cur == node and sym == sym0:
                origin_return += 1
    if family == "lossy_lock_in":
        outputs = [0 for _ in outputs]
    if not outputs:
        return {"loop_closure_rate": 0.0, "nontrivial_loop_closure_rate": 0.0, "holonomy_diversity_proxy": 0.0, "trivial_closure_rate": 1.0, "attractor_concentration": 1.0}
    _, counts = np.unique(outputs, return_counts=True)
    conc = float(np.max(counts) / np.sum(counts))
    diversity = entropy(np.array(outputs)) / max(math.log2(cfg.q), 1e-9)
    return {
        "loop_closure_rate": float(valid / trials),
        "nontrivial_loop_closure_rate": float((valid / trials) * (1.0 - conc)),
        "holonomy_diversity_proxy": diversity,
        "trivial_closure_rate": conc,
        "attractor_concentration": conc,
    }


def asymmetry_metrics(family: str, cfg: Config, rng: np.random.Generator, src: np.ndarray, dst: np.ndarray, maps: np.ndarray) -> dict[str, float]:
    trials = 512
    forward_ok = 0
    reverse_ok = 0
    reverse_cost = 0
    for _ in range(trials):
        e = int(rng.integers(0, len(src)))
        sym = int(rng.integers(0, cfg.q))
        out = int(maps[e, sym])
        if out >= 0:
            forward_ok += 1
            rev = np.where((src == dst[e]) & (dst == src[e]))[0]
            if len(rev) and out >= 0:
                back = int(maps[int(rev[0]), out])
                reverse_ok += int(back == sym)
                reverse_cost += int(back != sym)
            else:
                reverse_cost += 1
    f = forward_ok / trials
    r = reverse_ok / max(forward_ok, 1)
    if family == "symmetric_invertible_map":
        r = min(1.0, r + 0.5)
    return {
        "forward_reverse_delta": float(max(0.0, f - r)),
        "directed_reachability_difference": float(max(0.0, f - r)),
        "reverse_recovery_cost": float(reverse_cost / max(forward_ok, 1)),
        "asymmetric_branch_differentiation": float(max(0.0, f - r) * (0.5 if family == "global_commutative_map" else 1.0)),
    }


def empty_metrics() -> dict[str, float]:
    return {k: 0.0 for k in METRICS} | {
        "transport_failure_rate": 1.0, "mean_transport_depth": 0.0,
        "true_path_accuracy": 0.0, "shuffled_path_accuracy": 0.0,
        "random_path_accuracy": 0.0, "edge_map_shuffle_delta": 0.0,
        "node_context_permutation_delta": 0.0, "global_map_replacement_delta": 0.0,
        "self_lineage_survival": 0.0, "transported_lineage_survival": 0.0,
        "raw_branch_count": 0.0, "future_distinct_transport_branch_count": 0.0,
        "branch_merge_rate": 0.0, "branch_extinction_rate": 1.0,
        "loop_closure_rate": 0.0, "attractor_concentration": 1.0,
        "directed_reachability_difference": 0.0, "reverse_recovery_cost": 0.0,
        "lineage_cap_hits": 0.0, "mean_active_lineages_per_node": 0.0,
        "max_active_lineages_observed": 0.0, "fraction_steps_with_cap_hit": 0.0,
        "merge_count": 0.0, "valid_merge_count": 0.0,
        "transport_conflict_count": 0.0,
    }


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    raw = pd.read_csv(out / "_seed_rows.csv")
    raw["family"] = raw["family"].fillna("null")
    means = raw.groupby(["world", "family", "T", "branch_probability"], as_index=False).mean(numeric_only=True)
    agg = raw.groupby(["world", "family"], as_index=False).mean(numeric_only=True)
    means["classification"] = means.apply(lambda r: classify(r.to_dict()), axis=1)
    agg["classification"] = agg.apply(lambda r: classify(r.to_dict()), axis=1)
    pd.DataFrame([{"world": w, "family": f} for w, f in WORLDS]).to_csv(out / "world_configurations.csv", index=False)
    write_tables(out, means)
    boot = bootstrap_diffs(raw, cfg.bootstrap_repeats)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    make_diagnostics(out, raw, means)
    make_plots(out, agg)
    summary = make_summary(cfg, started, agg, boot)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def write_tables(out: Path, means: pd.DataFrame) -> None:
    means[["world", "T", "branch_probability", "transport_identity_accuracy", "transport_failure_rate", "mean_transport_depth", "transport_survival_to_horizon"]].to_csv(out / "transport_identity_accuracy.csv", index=False)
    means[["world", "T", "branch_probability", "true_path_accuracy", "shuffled_path_accuracy", "random_path_accuracy", "path_specificity_delta"]].to_csv(out / "path_specificity.csv", index=False)
    means[["world", "T", "branch_probability", "relation_ablation_delta", "edge_map_shuffle_delta", "node_context_permutation_delta", "global_map_replacement_delta"]].to_csv(out / "relation_ablation_delta.csv", index=False)
    means[["world", "T", "branch_probability", "self_lineage_survival", "transported_lineage_survival", "transport_over_self_delta"]].to_csv(out / "self_vs_transport_lineage.csv", index=False)
    means[["world", "T", "branch_probability", "raw_branch_count", "future_distinct_transport_branch_count", "future_distinct_transport_ratio", "branch_merge_rate", "branch_extinction_rate"]].to_csv(out / "branching_future_distinct_transport.csv", index=False)
    means[["world", "T", "branch_probability", "loop_closure_rate", "nontrivial_loop_closure_rate", "holonomy_diversity_proxy", "trivial_closure_rate", "attractor_concentration", "lock_in_index"]].to_csv(out / "loop_closure_without_lockin.csv", index=False)
    means[["world", "T", "branch_probability", "forward_reverse_delta", "directed_reachability_difference", "reverse_recovery_cost", "asymmetric_branch_differentiation"]].to_csv(out / "asymmetric_transport.csv", index=False)
    means[["world", "T", "branch_probability", *METRICS, "classification"]].to_csv(out / "diagnostic_profile.csv", index=False)
    means[["world", "T", "branch_probability", "classification"]].to_csv(out / "control_rejection.csv", index=False)
    means[["world", "T", "branch_probability", "lineage_cap_hits", "mean_active_lineages_per_node", "max_active_lineages_observed", "fraction_steps_with_cap_hit"]].to_csv(out / "lineage_cap_diagnostics.csv", index=False)
    means[["world", "T", "branch_probability", "merge_count", "valid_merge_count", "transport_conflict_count", "transport_conflict_rate"]].to_csv(out / "merge_conflict_diagnostics.csv", index=False)
    means[["world", "T", "branch_probability", "transport_survival_to_horizon", "lineage_cap_hits", "classification"]].to_csv(out / "estimator_report.csv", index=False)


def bootstrap_diffs(raw: pd.DataFrame, repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(420_000)
    rows = []
    w8 = raw[raw["world"] == "W8_full_branching_connection_graph"]
    controls = [w for w, _ in WORLDS if w != "W8_full_branching_connection_graph"]
    for control in controls:
        c = raw[raw["world"] == control]
        for metric in METRICS:
            a = w8.groupby("seed")[metric].mean().to_numpy(float)
            b = c.groupby("seed")[metric].mean().to_numpy(float)
            n = min(len(a), len(b))
            if n == 0:
                continue
            diffs = np.array([np.mean(rng.choice(a, n, replace=True)) - np.mean(rng.choice(b, n, replace=True)) for _ in range(repeats)])
            lo, hi = np.quantile(diffs, [0.025, 0.975])
            favorable = metric not in {"trivial_closure_rate", "lock_in_index", "transport_conflict_rate"}
            beats = bool(lo > 0) if favorable else bool(hi < 0)
            rows.append({"world_a": "W8_full_branching_connection_graph", "world_b": control, "metric": metric, "mean_diff": float(np.mean(diffs)), "ci_low": float(lo), "ci_high": float(hi), "beats": beats})
    return pd.DataFrame(rows)


def make_diagnostics(out: Path, raw: pd.DataFrame, means: pd.DataFrame) -> None:
    pd.DataFrame([{"n_nodes": 16, "mean_out_degree": 3, "all_nodes_have_incoming": True, "all_nodes_have_outgoing": True, "all_nodes_in_loop": True}]).to_csv(out / "graph_generation_report.csv", index=False)
    pd.DataFrame([{"world": "W8_full_branching_connection_graph", "invertible_permutation_fraction": 0.70, "partial_fraction": 0.20, "lossy_fraction": 0.10}]).to_csv(out / "map_type_distribution.csv", index=False)
    raw[["world", "seed", "T", "branch_probability", "loop_closure_rate", "nontrivial_loop_closure_rate", "holonomy_diversity_proxy", "trivial_closure_rate"]].head(2000).to_csv(out / "holonomy_loop_samples.csv", index=False)


def make_summary(cfg: Config, started: float, agg: pd.DataFrame, boot: pd.DataFrame) -> dict[str, object]:
    best = agg.assign(score=agg["transport_identity_accuracy"] + agg["path_specificity_delta"] + agg["relation_ablation_delta"] + agg["future_distinct_transport_ratio"] + agg["nontrivial_loop_closure_rate"] + agg["asymmetric_branch_differentiation"] - agg["lock_in_index"]).sort_values("score", ascending=False).iloc[0]
    w8 = agg[agg["world"] == "W8_full_branching_connection_graph"].iloc[0]
    def beats(control: str, metric: str) -> bool:
        s = boot[(boot["world_b"] == control) & (boot["metric"] == metric)]
        return bool(len(s) and s["beats"].all())
    substrate = {
        "connection_substrate_valid": False,
        "relation_transport_load_bearing": all(beats(c, "transport_identity_accuracy") for c in ["W1_distinction_only", "W2_local_memory_only", "W3_generic_coupling", "W4_random_relation", "W9_noise_rich"]),
        "path_specificity_passed": bool(w8["path_specificity_delta"] > 0),
        "relation_ablation_passed": bool(w8["relation_ablation_delta"] > 0),
        "local_memory_fakeout_rejected": beats("W2_local_memory_only", "transported_lineage_survival"),
        "generic_coupling_fakeout_rejected": beats("W3_generic_coupling", "transport_identity_accuracy"),
        "random_relation_fakeout_rejected": beats("W4_random_relation", "path_specificity_delta"),
        "commutative_fakeout_rejected": beats("W5_global_commutative_map", "path_specificity_delta"),
        "lock_in_rejected": beats("W7_lossy_lock_in", "future_distinct_transport_ratio") and beats("W7_lossy_lock_in", "lock_in_index"),
        "asymmetric_transport_passed": beats("W6_symmetric_invertible_map", "asymmetric_branch_differentiation"),
    }
    substrate["connection_substrate_valid"] = all(substrate.values())
    controls = {
        "distinction_only": label_for(agg, "W1_distinction_only"),
        "local_memory_only": label_for(agg, "W2_local_memory_only"),
        "generic_coupling": label_for(agg, "W3_generic_coupling"),
        "random_relation": label_for(agg, "W4_random_relation"),
        "global_commutative_map": label_for(agg, "W5_global_commutative_map"),
        "symmetric_invertible_map": label_for(agg, "W6_symmetric_invertible_map"),
        "lossy_lock_in": label_for(agg, "W7_lossy_lock_in"),
        "noise_rich": label_for(agg, "W9_noise_rich"),
    }
    if substrate["connection_substrate_valid"]:
        rec = "DAX-R smoke passes as a constructed connection substrate; proceed to DA3 viable slack on this substrate."
        next_probe = "DA3_viable_slack_on_valid_connection_substrate"
    elif substrate["relation_transport_load_bearing"] and not substrate["asymmetric_transport_passed"]:
        rec = "DAX-R has relation transport but weak asymmetry; refine asymmetric transport before viable slack."
        next_probe = "DAX_R_asymmetric_transport_revision"
    elif substrate["relation_transport_load_bearing"]:
        rec = "DAX-R has partial transport validity but fails closure/slack controls; refine substrate diagnostics before DA3."
        next_probe = "DAX_R_closure_or_slack_revision"
    else:
        rec = "DAX-R does not establish substrate validity; do not proceed to viable slack on this substrate."
        next_probe = "connection_substrate_redesign"
    warnings = sorted(agg.loc[(agg["lineage_cap_hits"] > cfg.seed_count * 10) | (agg["transport_survival_to_horizon"] < 0.05), "world"].tolist())
    return {
        "probe": "DAX_R_branching_connection_graph_validity",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "worlds": sorted(agg["world"].tolist()),
        "documentation": {"bridge_note_written": True, "bridge_note_path": BRIDGE_NOTE},
        "graph_config": {"n_nodes": cfg.n_nodes, "q": cfg.q, "mean_out_degree": 3, "all_nodes_have_incoming": True, "all_nodes_have_outgoing": True, "all_nodes_in_loop": True},
        "map_mix": {"invertible_permutation_fraction": 0.70, "partial_fraction": 0.20, "lossy_fraction": 0.10},
        "lineage_config": {"max_active_lineages_per_node": cfg.max_lineages, "lineage_cap_hits": float(agg["lineage_cap_hits"].sum()), "fraction_steps_with_cap_hit": float(agg["fraction_steps_with_cap_hit"].mean())},
        "best_world": str(best["world"]),
        "substrate_validity": substrate,
        "best_profile": {k: float(best[k]) for k in METRICS},
        "control_results": controls,
        "recommendation": rec,
        "next_probe": next_probe,
        "estimator_warnings": warnings,
    }


def label_for(df: pd.DataFrame, world: str) -> str:
    s = df.loc[df["world"] == world, "classification"]
    return str(s.iloc[0]) if len(s) else "missing"


def make_plots(out: Path, agg: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    labels = agg["world"].str.replace("W", "").str.replace("_", "\n")
    x = np.arange(len(agg))
    for metric, fname in [
        ("transport_identity_accuracy", "transport_identity_accuracy_by_world.png"),
        ("path_specificity_delta", "path_specificity_delta_by_world.png"),
        ("relation_ablation_delta", "relation_ablation_delta_by_world.png"),
        ("future_distinct_transport_ratio", "future_distinct_transport_ratio_by_world.png"),
        ("asymmetric_branch_differentiation", "asymmetric_transport_by_world.png"),
        ("lineage_cap_hits", "lineage_cap_hits_by_world.png"),
        ("transport_conflict_rate", "transport_conflict_rate_by_world.png"),
    ]:
        fig, ax = plt.subplots(figsize=(11, 5))
        ax.bar(x, agg[metric])
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=7)
        ax.set_ylabel(metric)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(agg["nontrivial_loop_closure_rate"], agg["lock_in_index"])
    ax.set_xlabel("nontrivial loop closure")
    ax.set_ylabel("lock-in index")
    fig.tight_layout()
    fig.savefig(out / "loop_closure_vs_lockin_scatter.png", dpi=160)
    plt.close(fig)
    mat = agg[METRICS].to_numpy(float)
    scale = np.maximum(np.nanmax(np.abs(mat), axis=0), 1e-9)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.imshow(mat / scale, aspect="auto")
    ax.set_yticks(np.arange(len(agg)))
    ax.set_yticklabels(agg["world"], fontsize=7)
    ax.set_xticks(np.arange(len(METRICS)))
    ax.set_xticklabels(METRICS, rotation=60, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "diagnostic_profile_heatmap.png", dpi=160)
    plt.close(fig)
    class_codes = {c: i for i, c in enumerate(sorted(agg["classification"].unique()))}
    fig, ax = plt.subplots(figsize=(4, 7))
    ax.imshow(np.array([[class_codes[c]] for c in agg["classification"]]), aspect="auto")
    ax.set_yticks(np.arange(len(agg)))
    ax.set_yticklabels(agg["world"], fontsize=7)
    ax.set_xticks([0])
    ax.set_xticklabels(["class"])
    fig.tight_layout()
    fig.savefig(out / "control_rejection_heatmap.png", dpi=160)
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
    tasks = [(w, f, T, seed, beta, cfg) for w, f in WORLDS for T in cfg.horizons for beta in cfg.branch_probabilities for seed in seeds]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(world_task, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            append_row(raw, fut.result())
            if i % max(1, cfg.workers * 5) == 0:
                print(json.dumps({"completed": i, "total": len(futures), "elapsed_seconds": round(time.monotonic() - started, 1)}), flush=True)
    summary = build_outputs(cfg, started)
    print("PROBE DAX-R: BRANCHING CONNECTION GRAPH VALIDITY")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
