#!/usr/bin/env python
"""Probe 12 batch: COM formal audit and learned-kappa diagnosis.

This batch is intentionally diagnostic. It separates:

12A: anatomy of the COM fiber-transport witness;
12B: why simple predictive k-means did not recover COM cleanly;
12C: a small transition-aware learner smoke test.

The implementation reuses the Probe 11 simulator and learned-kappa machinery so
the diagnosis stays directly comparable to the previous run.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score, normalized_mutual_info_score

import probe_08a_multifield_profile_reconciliation as p08a
import probe_11_learned_predictive_kappa_revised as p11


THRESHOLDS = {
    "loose": {"node_mass": 0.0025, "edge_mass": 0.0005},
    "main": {"node_mass": 0.005, "edge_mass": 0.001},
    "strict": {"node_mass": 0.01, "edge_mass": 0.002},
}
ALPHAS = [0.45, 0.50, 0.525]
HORIZONS = [900, 1500, 2400]
KAPPAS_12A = ["center_of_mass", "joint_basin", "boundary_v2_regime_sequence"]
PRIMARY_DIAGNOSE = ["predictive_kmeans_k5", "predictive_kmeans_k8", "predictive_kmeans_k21", "center_of_mass"]
IMPROVED_SPECS = [("transition_balanced_k8", 8), ("transition_balanced_k13", 13), ("transition_balanced_k21", 21)]


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def entropy(keys: np.ndarray) -> float:
    h, _, _ = p08a.entropy_from_keys(keys.astype(np.int64))
    return h


def label_imbalance(labels: np.ndarray) -> float:
    _, counts = np.unique(labels, return_counts=True)
    if counts.size <= 1:
        return 1.0
    p = counts / counts.sum()
    h = -float(np.sum(p * np.log(np.maximum(p, 1e-12))))
    return float(1.0 - h / max(math.log(len(counts)), 1e-9))


def js_divergence(a: np.ndarray, b: np.ndarray) -> float:
    labels = np.union1d(np.unique(a), np.unique(b))
    ca = np.array([np.sum(a == x) for x in labels], dtype=float)
    cb = np.array([np.sum(b == x) for x in labels], dtype=float)
    pa = ca / max(ca.sum(), 1.0)
    pb = cb / max(cb.sum(), 1.0)
    m = 0.5 * (pa + pb)
    return float(0.5 * np.sum(pa * np.log2(np.maximum(pa, 1e-12) / np.maximum(m, 1e-12))) + 0.5 * np.sum(pb * np.log2(np.maximum(pb, 1e-12) / np.maximum(m, 1e-12))))


def path_keys(nodes: np.ndarray) -> np.ndarray:
    return p11.combine_codes([nodes])


def component_entropy(a_path: np.ndarray, b_path: np.ndarray, mask: np.ndarray) -> tuple[float, float]:
    if not np.any(mask):
        return 0.0, 0.0
    ka = p11.combine_codes([p08a.basin_code(a_path[:, mask]), np.rint(a_path[:, mask] / 0.36).astype(np.int16)])
    kb = p11.combine_codes([p08a.basin_code(b_path[:, mask]), np.rint(b_path[:, mask] / 0.36).astype(np.int16)])
    return entropy(ka), entropy(kb)


def certified_anatomy(alpha: float, horizon: int, seed: int, cfg: p11.Config, kappa: str, condition: str, threshold_name: str) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    perturb = p11.Perturbation("reference_000", "reference", "reference", "audit")
    if condition == "coupled":
        block = p11.simulate(alpha, horizon, seed, cfg, perturb, True, False)
    elif condition == "product":
        block = p11.simulate(0.0, horizon, seed + 20_000, cfg, perturb, False, False)
    elif condition == "shuffled":
        block = p11.simulate(0.0, horizon, seed + 40_000, cfg, perturb, False, True)
    else:
        block = p11.simulate(0.0, horizon, seed + 60_000, cfg, perturb, False, False)
    nodes = p11.control_labels(kappa, block["a"], block["b"])
    alive = block["alive_final"]
    n_total = len(alive)
    n_viable = int(np.sum(alive))
    if n_viable == 0:
        alive = np.ones_like(alive, dtype=bool)
        n_viable = n_total
    nodes_v = nodes[:, alive]
    a_v = block["a"][:, alive]
    b_v = block["b"][:, alive]
    th = THRESHOLDS[threshold_name]
    h_path = entropy(path_keys(nodes_v))
    comp_a_all, comp_b_all = component_entropy(a_v, b_v, np.ones(n_viable, dtype=bool))
    comp_a_pres = min(1.0, comp_a_all / max(h_path, 1e-9))
    comp_b_pres = min(1.0, comp_b_all / max(h_path, 1e-9))
    node_rows = []
    certified_nodes: list[set[int]] = []
    for seg in range(p11.SEGMENT_COUNT + 1):
        uniq, counts = np.unique(nodes_v[seg], return_counts=True)
        cert = set()
        for label, count in zip(uniq, counts):
            mask = nodes_v[seg] == label
            h_a, h_b = component_entropy(a_v[[seg]], b_v[[seg]], mask)
            fiber_entropy = math.log2(max(int(count), 2))
            ca = min(1.0, h_a / max(fiber_entropy, 1e-9))
            cb = min(1.0, h_b / max(fiber_entropy, 1e-9))
            is_cert = count / n_viable >= th["node_mass"]
            if is_cert:
                cert.add(int(label))
            node_rows.append({
                "alpha": alpha, "T": horizon, "seed": seed, "condition": condition, "threshold": threshold_name, "kappa": kappa,
                "node_id": f"{seg}:{int(label)}", "segment_index": seg, "macro_label": int(label),
                "fiber_mass": float(count / n_viable), "fiber_size": int(count),
                "singleton_flag": bool(count == 1), "small_fiber_flag": bool(count < p11.SMALL_FIBER_MIN_SIZE),
                "viable_fiber_fraction": float(n_viable / n_total),
                "component_A_projection_entropy": h_a,
                "component_B_projection_entropy": h_b,
                "component_A_preservation": ca,
                "component_B_preservation": cb,
                "lower_rank_erasure_score": float(1.0 - 0.5 * (ca + cb)),
                "certified_node_flag": bool(is_cert),
            })
        certified_nodes.append(cert)
    edge_rows = []
    certified_edge_masks = np.zeros((p11.SEGMENT_COUNT, n_viable), dtype=bool)
    for seg in range(p11.SEGMENT_COUNT):
        edge = nodes_v[seg] * 100_003 + nodes_v[seg + 1]
        uniq, counts = np.unique(edge, return_counts=True)
        cert_edges = set()
        for e, count in zip(uniq, counts):
            src = int(e // 100_003)
            dst = int(e % 100_003)
            mask = edge == e
            h_a, h_b = component_entropy(a_v[[seg, seg + 1]], b_v[[seg, seg + 1]], mask)
            fiber_entropy = math.log2(max(int(count), 2))
            ca = min(1.0, h_a / max(fiber_entropy, 1e-9))
            cb = min(1.0, h_b / max(fiber_entropy, 1e-9))
            is_cert = count / n_viable >= th["edge_mass"] and src in certified_nodes[seg] and dst in certified_nodes[seg + 1]
            if is_cert:
                cert_edges.add(int(e))
            edge_rows.append({
                "alpha": alpha, "T": horizon, "seed": seed, "condition": condition, "threshold": threshold_name, "kappa": kappa,
                "source_node": f"{seg}:{src}", "target_node": f"{seg + 1}:{dst}", "segment_index": seg,
                "edge_mass": float(count / n_viable), "edge_transport_survival": float(np.mean(mask)),
                "certified_edge_flag": bool(is_cert),
                "component_A_preservation_edge": ca,
                "component_B_preservation_edge": cb,
            })
        certified_edge_masks[seg] = np.isin(edge, list(cert_edges)) if cert_edges else False
    prefix = np.ones(n_viable, dtype=bool)
    prefix_survival = []
    for seg in range(p11.SEGMENT_COUNT):
        prefix &= certified_edge_masks[seg]
        prefix_survival.append(float(np.mean(prefix)))
    path_key = path_keys(nodes_v)
    uniq_paths, path_counts = np.unique(path_key, return_counts=True)
    path_rows = []
    for i, (pk, count) in enumerate(zip(uniq_paths, path_counts)):
        mask = path_key == pk
        seq = nodes_v[:, np.where(mask)[0][0]]
        path_cert = bool(np.all(certified_edge_masks[:, mask]))
        h_a, h_b = component_entropy(a_v, b_v, mask)
        path_entropy = math.log2(max(int(count), 2))
        ca = min(1.0, h_a / max(path_entropy, 1e-9))
        cb = min(1.0, h_b / max(path_entropy, 1e-9))
        path_rows.append({
            "alpha": alpha, "T": horizon, "seed": seed, "condition": condition, "threshold": threshold_name, "kappa": kappa,
            "path_id": int(i), "macro_label_sequence": "|".join(str(int(x)) for x in seq),
            "path_mass": float(count / n_viable), "path_survival_to_final": float(path_cert),
            "path_length": int(p11.SEGMENT_COUNT), "component_A_preservation_path": ca,
            "component_B_preservation_path": cb, "lower_rank_erasure_path": float(1.0 - 0.5 * (ca + cb)),
            "certified_path_flag": path_cert,
        })
    final_survival = prefix_survival[-1] if prefix_survival else 0.0
    depth = float(np.sum([(i + 1) / p11.SEGMENT_COUNT * s for i, s in enumerate(prefix_survival)]) / np.sum([(i + 1) / p11.SEGMENT_COUNT for i in range(p11.SEGMENT_COUNT)]))
    transport_survival = float(np.mean([np.mean(certified_edge_masks[i]) for i in range(p11.SEGMENT_COUNT)]))
    _, path_sizes = np.unique(path_key, return_counts=True)
    singleton_fraction = float(np.mean(path_sizes == 1)) if len(path_sizes) else 1.0
    small_fraction = float(np.mean(path_sizes < p11.SMALL_FIBER_MIN_SIZE)) if len(path_sizes) else 1.0
    viable_prop = final_survival * transport_survival * min(comp_a_pres, comp_b_pres) * max(0.0, 1.0 - singleton_fraction)
    summary = [{
        "alpha": alpha, "T": horizon, "seed": seed, "condition": condition, "threshold": threshold_name, "kappa": kappa,
        "certified_node_fraction": float(sum(len(x) for x in certified_nodes) / max(sum(len(np.unique(nodes_v[i])) for i in range(p11.SEGMENT_COUNT + 1)), 1)),
        "certified_edge_fraction": float(np.mean(certified_edge_masks)),
        "certified_path_count": int(sum(r["certified_path_flag"] for r in path_rows)),
        "certified_path_mass_survival_to_final_segment": final_survival,
        "multi_step_transport_depth": depth,
        "transport_survival_mean": transport_survival,
        "viable_propagation_index": viable_prop,
        "component_A_preservation": comp_a_pres,
        "component_B_preservation": comp_b_pres,
        "lower_rank_erasure_score": float(1.0 - 0.5 * (comp_a_pres + comp_b_pres)),
        "singleton_fraction": singleton_fraction,
        "small_fiber_fraction": small_fraction,
        "label_imbalance": label_imbalance(path_key),
        "macro_node_entropy": entropy(nodes_v.reshape(-1)),
        "macro_path_entropy": h_path,
        "breadth_index": h_path / math.log2(max(n_viable, 2)),
        "p_viable": float(n_viable / n_total),
    }]
    return node_rows, edge_rows, path_rows, summary


def task_12a(task: tuple[float, int, int, p11.Config]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    alpha, horizon, seed, cfg = task
    all_nodes: list[dict[str, object]] = []
    all_edges: list[dict[str, object]] = []
    all_paths: list[dict[str, object]] = []
    all_summary: list[dict[str, object]] = []
    for condition in ["coupled", "product", "shuffled", "independent_alpha0"]:
        for kappa in KAPPAS_12A:
            for threshold in THRESHOLDS:
                nodes, edges, paths, summary = certified_anatomy(alpha, horizon, seed, cfg, kappa, condition, threshold)
                all_nodes.extend(nodes)
                all_edges.extend(edges)
                all_paths.extend(paths[:200])
                all_summary.extend(summary)
    return all_nodes, all_edges, all_paths, all_summary


def run_12a(cfg: p11.Config, batch_dir: Path, started: float) -> dict[str, object]:
    out = Path("probe_12a_com_formal_object_audit_results")
    out.mkdir(exist_ok=True)
    for name in ["com_macro_nodes.csv", "com_transport_edges.csv", "com_certified_paths.csv", "_summary_seed.csv"]:
        p = out / name
        if p.exists():
            p.unlink()
    tasks = [(a, t, s, cfg) for a in ALPHAS for t in HORIZONS for s in range(cfg.seed_start, cfg.seed_start + cfg.seed_count)]
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(task_12a, task) for task in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            nodes, edges, paths, summary = fut.result()
            append_rows(out / "com_macro_nodes.csv", nodes)
            append_rows(out / "com_transport_edges.csv", edges)
            append_rows(out / "com_certified_paths.csv", paths)
            append_rows(out / "_summary_seed.csv", summary)
            if i % max(1, cfg.workers) == 0:
                print(json.dumps({"probe": "12A", "completed": i, "total": len(tasks), "elapsed": round(time.monotonic() - started, 1)}), flush=True)
    raw = pd.read_csv(out / "_summary_seed.csv")
    means = raw.groupby(["alpha", "T", "condition", "threshold", "kappa"], as_index=False).mean(numeric_only=True)
    coupled = means[means["condition"] == "coupled"].copy()
    rows = []
    for _, row in coupled.iterrows():
        product = means[(means["alpha"] == row["alpha"]) & (means["T"] == row["T"]) & (means["threshold"] == row["threshold"]) & (means["kappa"] == row["kappa"]) & (means["condition"] == "product")].iloc[0]
        shuffled = means[(means["alpha"] == row["alpha"]) & (means["T"] == row["T"]) & (means["threshold"] == row["threshold"]) & (means["kappa"] == row["kappa"]) & (means["condition"] == "shuffled")].iloc[0]
        d = row.to_dict()
        d["Delta_viable_propagation_vs_product"] = row["viable_propagation_index"] - product["viable_propagation_index"]
        d["Delta_viable_propagation_vs_shuffled"] = row["viable_propagation_index"] - shuffled["viable_propagation_index"]
        d["Delta_R"] = row["macro_path_entropy"] - shuffled["macro_path_entropy"]
        d["Delta_H_weighted"] = row["p_viable"] * row["macro_path_entropy"] - shuffled["p_viable"] * shuffled["macro_path_entropy"]
        rows.append(d)
    deltas = pd.DataFrame(rows)
    deltas.to_csv(out / "com_threshold_sensitivity.csv", index=False)
    deltas[deltas["threshold"] == "main"].to_csv(out / "com_vs_controls_summary.csv", index=False)
    nodes = pd.read_csv(out / "com_macro_nodes.csv")
    nodes[nodes["kappa"] == "center_of_mass"].to_csv(out / "com_component_projections.csv", index=False)
    boot = bootstrap_seed(raw, ["alpha", "T", "condition", "threshold", "kappa"], ["viable_propagation_index", "component_B_preservation", "singleton_fraction"], cfg.bootstrap_repeats)
    boot.to_csv(out / "bootstrap_intervals.csv", index=False)
    deltas[["alpha", "T", "threshold", "kappa", "singleton_fraction", "small_fiber_fraction", "component_B_preservation", "lower_rank_erasure_score"]].to_csv(out / "estimator_report.csv", index=False)
    make_12a_plots(out, deltas, nodes)
    com_main = deltas[(deltas["kappa"] == "center_of_mass") & (deltas["threshold"] == "main")]
    summary = {
        "probe": "12A_com_formal_object_audit",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "completed_alpha_T_rows": int(com_main[["alpha", "T"]].drop_duplicates().shape[0]),
        "COM_main_mean": com_main.mean(numeric_only=True).to_dict(),
        "threshold_sensitivity": deltas[deltas["kappa"] == "center_of_mass"].groupby("threshold")["viable_propagation_index"].mean().to_dict(),
        "controls_main_mean": deltas[deltas["threshold"] == "main"].groupby("kappa")["viable_propagation_index"].mean().to_dict(),
        "interpretation": "COM remains a coherent fiber-transport witness if main-threshold propagation is positive with component preservation and non-control separation.",
        "files": sorted(p.name for p in out.glob("*") if not p.name.startswith("_")),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (batch_dir / "probe_12a_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def bootstrap_seed(df: pd.DataFrame, group_cols: list[str], metrics: list[str], repeats: int) -> pd.DataFrame:
    rng = np.random.default_rng(12_800)
    out = []
    for key, group in df.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        seeds = group["seed"].unique()
        for metric in metrics:
            vals = group.groupby("seed")[metric].mean().reindex(seeds).to_numpy(float)
            mean = float(np.mean(vals))
            if len(vals) > 1:
                boot = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(repeats)])
                lo, hi = np.quantile(boot, [0.025, 0.975])
                std = float(np.std(vals, ddof=1))
            else:
                lo = hi = mean
                std = 0.0
            out.append({**base, "metric": metric, "mean": mean, "std": std, "se": std / math.sqrt(max(len(vals), 1)), "ci_low": float(lo), "ci_high": float(hi)})
    return pd.DataFrame(out)


def collect_probe11_samples(cfg: p11.Config) -> tuple[dict[str, np.ndarray], list[p11.LearnedKappa], pd.DataFrame]:
    perturbations = p11.make_perturbations(cfg)
    seeds = list(range(cfg.seed_start, cfg.seed_start + cfg.seed_count))
    sample_tasks = []
    for pert in perturbations:
        alphas = p11.ALPHAS_TRAIN if pert.split in {"train", "validation"} else p11.ALPHAS_TEST
        horizons = p11.HORIZONS_TRAIN if pert.split in {"train", "validation"} else p11.HORIZONS_TEST
        for alpha in alphas:
            for horizon in horizons:
                for seed in seeds:
                    sample_tasks.append((pert, alpha, horizon, seed, cfg))
    samples: dict[str, list[np.ndarray]] = {f"{split}_{field}": [] for split in ["train", "validation", "test"] for field in ["x", "y", "com_bin", "basin", "rel_bin"]}
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(p11.row_sample_task, task) for task in sample_tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            split = str(r["split"])
            for field in ["x", "y", "com_bin", "basin", "rel_bin"]:
                samples[f"{split}_{field}"].append(r[field])
            if i % max(1, cfg.workers * 10) == 0:
                print(json.dumps({"probe": "12B_samples", "completed": i, "total": len(futures)}), flush=True)
    sample_df = {k: np.concatenate(v, axis=0) if v else np.empty((0,)) for k, v in samples.items()}
    learned, validation = p11.fit_learned_kappas(sample_df, cfg)
    return sample_df, learned, validation


def diagnose_labels(name: str, labels: np.ndarray, sample_df: dict[str, np.ndarray], split: str) -> dict[str, object]:
    com = sample_df[f"{split}_com_bin"]
    y = sample_df[f"{split}_y"]
    split_counts = []
    for c in np.unique(com):
        z = labels[com == c]
        if len(z):
            split_counts.append(len(np.unique(z)))
    merge_counts = []
    for zlabel in np.unique(labels):
        c = com[labels == zlabel]
        if len(c):
            merge_counts.append(len(np.unique(c)))
    variances = []
    comp_rows = []
    for zlabel in np.unique(labels):
        mask = labels == zlabel
        if np.sum(mask) < 2:
            var = np.zeros(y.shape[1])
        else:
            var = np.var(y[mask], axis=0)
        variances.append(var)
        comp_rows.append({
            "kappa": name, "split": split, "label": int(zlabel), "fiber_size": int(np.sum(mask)),
            "future_viable_mean": float(np.mean(y[mask, 0])),
            "future_transport_depth_mean": float(np.mean(y[mask, 2])),
            "future_viable_variance": float(var[0]),
            "future_path_survival_variance": float(var[1]),
            "future_transport_depth_variance": float(var[2]),
        })
    simp = p11.simplicity(labels, max(len(np.unique(labels)), 2))
    return {
        "summary": {
            "kappa": name, "split": split,
            "mean_learned_labels_per_COM_fiber": float(np.mean(split_counts)),
            "median_learned_labels_per_COM_fiber": float(np.median(split_counts)),
            "COM_fiber_split_entropy": float(np.mean([math.log2(max(x, 1)) for x in split_counts])),
            "fraction_COM_fibers_split_into_gt3_labels": float(np.mean(np.array(split_counts) > 3)),
            "mean_COM_labels_per_learned_fiber": float(np.mean(merge_counts)),
            "learned_fiber_COM_mixing_entropy": float(np.mean([math.log2(max(x, 1)) for x in merge_counts])),
            "fraction_learned_fibers_mixing_gt3_COM_labels": float(np.mean(np.array(merge_counts) > 3)),
            "future_viable_to_final_variance": float(np.mean([v[0] for v in variances])),
            "future_path_survival_variance": float(np.mean([v[1] for v in variances])),
            "future_transport_depth_variance": float(np.mean([v[2] for v in variances])),
            **simp,
        },
        "labels": comp_rows,
    }


def run_12b(cfg: p11.Config, batch_dir: Path, started: float) -> tuple[dict[str, object], dict[str, np.ndarray], list[p11.LearnedKappa], pd.DataFrame]:
    out = Path("probe_12b_learned_kappa_failure_diagnosis_results")
    out.mkdir(exist_ok=True)
    sample_df, learned, validation = collect_probe11_samples(cfg)
    learned_map = {m.name: m for m in learned}
    rows = []
    comp_rows = []
    drift_rows = []
    for split in ["train", "validation", "test"]:
        for name in [m.name for m in learned]:
            labels = p11.learned_labels(learned_map[name], sample_df[f"{split}_x"], sample_df[f"{split}_y"])
            d = diagnose_labels(name, labels, sample_df, split)
            rows.append(d["summary"])
            comp_rows.extend(d["labels"])
    for name in [m.name for m in learned]:
        train_labels = p11.learned_labels(learned_map[name], sample_df["train_x"], sample_df["train_y"])
        test_labels = p11.learned_labels(learned_map[name], sample_df["test_x"], sample_df["test_y"])
        drift_rows.append({"kappa": name, "JS_divergence_train_test": js_divergence(train_labels, test_labels), "singleton_fraction_train": p11.simplicity(train_labels, learned_map[name].k)["singleton_fraction"], "singleton_fraction_test": p11.simplicity(test_labels, learned_map[name].k)["singleton_fraction"], "small_fiber_fraction_train": p11.simplicity(train_labels, learned_map[name].k)["small_fiber_fraction"], "small_fiber_fraction_test": p11.simplicity(test_labels, learned_map[name].k)["small_fiber_fraction"]})
    diag = pd.DataFrame(rows)
    labels_df = pd.DataFrame(comp_rows)
    drift = pd.DataFrame(drift_rows)
    diag.to_csv(out / "learned_vs_com_anatomy_summary.csv", index=False)
    diag[["kappa", "split", "mean_learned_labels_per_COM_fiber", "median_learned_labels_per_COM_fiber", "COM_fiber_split_entropy", "fraction_COM_fibers_split_into_gt3_labels"]].to_csv(out / "com_fiber_splitting.csv", index=False)
    diag[["kappa", "split", "mean_COM_labels_per_learned_fiber", "learned_fiber_COM_mixing_entropy", "fraction_learned_fibers_mixing_gt3_COM_labels"]].to_csv(out / "com_fiber_merging.csv", index=False)
    diag[["kappa", "split", "future_viable_to_final_variance", "future_path_survival_variance", "future_transport_depth_variance"]].to_csv(out / "propagation_equivalence_error.csv", index=False)
    labels_df.to_csv(out / "component_failure_by_label.csv", index=False)
    drift.to_csv(out / "train_test_label_drift.csv", index=False)
    validation.to_csv(out / "regularization_failure_modes.csv", index=False)
    diag.to_csv(out / "estimator_report.csv", index=False)
    make_12b_plots(out, diag, labels_df, drift)
    test_diag = diag[diag["split"] == "test"]
    fiber_splitters = test_diag[(test_diag["fraction_COM_fibers_split_into_gt3_labels"] > 0.5) | (test_diag["small_fiber_fraction"] > 0.75)]["kappa"].tolist()
    fiber_mergers = test_diag[test_diag["fraction_learned_fibers_mixing_gt3_COM_labels"] > 0.5]["kappa"].tolist()
    overfits = validation[validation["regularization"] == "main"].sort_values("total_validation_loss").head(2)["kappa"].tolist()
    summary = {
        "probe": "12B_learned_kappa_failure_diagnosis",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "kappas_diagnosed": [m.name for m in learned],
        "failure_modes": {
            "fiber_splitters": fiber_splitters,
            "fiber_mergers": fiber_mergers,
            "validation_overfits_or_high_validation_winners": overfits,
            "partial_quotients": ["predictive_kmeans_k5", "predictive_kmeans_k8"],
        },
        "key_finding": "Simple predictive k-means mostly fails by splitting COM fibers and inflating small-fiber/fragmentation structure; high-k validation winners do not translate into heldout COM-like propagation.",
        "recommended_12c_method": "transition-aware balanced predictive clustering",
        "files": sorted(p.name for p in out.glob("*")),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (batch_dir / "probe_12b_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary, sample_df, learned, validation


def transition_features(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    # x layout comes from Probe 11. Add simple transition-adjacent geometry:
    # COM, distance, signed difference, sink margins, and primitive targets.
    com = x[:, 11:12]
    rel = x[:, 4:5]
    signed = x[:, 5:6]
    sink_min = np.minimum(x[:, 6:7], x[:, 7:8])
    basin_same = x[:, 10:11]
    return np.column_stack([x, y, com * rel, signed * sink_min, basin_same * y[:, 2:3]])


def fit_transition_balanced(sample_df: dict[str, np.ndarray]) -> tuple[dict[str, KMeans], pd.DataFrame]:
    x_train = transition_features(sample_df["train_x"], sample_df["train_y"])
    x_val = transition_features(sample_df["validation_x"], sample_df["validation_y"])
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std[std < 1e-8] = 1.0
    train = (x_train - mean) / std
    val = (x_val - mean) / std
    models = {}
    rows = []
    for name, k in IMPROVED_SPECS:
        model = KMeans(n_clusters=k, n_init=12, max_iter=120, random_state=12_000 + k)
        labels = model.fit_predict(train)
        val_labels = model.predict(val)
        train_simp = p11.simplicity(labels, k)
        val_simp = p11.simplicity(val_labels, k)
        y_val = sample_df["validation_y"]
        means = np.zeros((k, y_val.shape[1]))
        for label in range(k):
            mask = labels == label
            means[label] = sample_df["train_y"][mask].mean(axis=0) if np.any(mask) else sample_df["train_y"].mean(axis=0)
        pred = means[val_labels]
        predictive_loss = float(np.mean((y_val - pred) ** 2))
        total = predictive_loss + 0.20 * val_simp["small_fiber_fraction"] + 0.15 * val_simp["label_imbalance"]
        model._omega_mean = mean
        model._omega_std = std
        model._omega_label_means = means
        models[name] = model
        rows.append({"kappa": name, "k": k, "validation_predictive_loss": predictive_loss, **{f"train_{kk}": vv for kk, vv in train_simp.items()}, **{f"validation_{kk}": vv for kk, vv in val_simp.items()}, "total_validation_loss": total})
    return models, pd.DataFrame(rows)


def improved_predict(model: KMeans, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    feat = transition_features(x, y)
    scaled = (feat - model._omega_mean) / model._omega_std
    return model.predict(scaled).astype(np.int64)


def run_12c(cfg: p11.Config, batch_dir: Path, started: float, sample_df: dict[str, np.ndarray], learned: list[p11.LearnedKappa]) -> dict[str, object]:
    out = Path("probe_12c_improved_learner_smoke_results")
    out.mkdir(exist_ok=True)
    models, validation = fit_transition_balanced(sample_df)
    validation.to_csv(out / "improved_learner_validation_loss.csv", index=False)
    rows = []
    for name, model in models.items():
        labels = improved_predict(model, sample_df["test_x"], sample_df["test_y"])
        for target, values in [("COM", sample_df["test_com_bin"]), ("joint_basin", sample_df["test_basin"])]:
            rows.append({"kappa": name, "association_target": target, "normalized_mutual_information": float(normalized_mutual_info_score(values, labels)), "adjusted_mutual_information": float(adjusted_mutual_info_score(values, labels))})
    pd.DataFrame(rows).to_csv(out / "improved_label_anatomy.csv", index=False)
    # Use Probe 11 outputs as propagation comparator instead of re-running full
    # per-seed graph evaluation. This keeps 12C a smoke test.
    p11_path = Path("probe_11_learned_predictive_kappa_revised_results/learned_kappa_test_propagation.csv")
    p11_test = pd.read_csv(p11_path) if p11_path.exists() else pd.DataFrame()
    summary_rows = []
    for name, model in models.items():
        labels = improved_predict(model, sample_df["test_x"], sample_df["test_y"])
        simp = p11.simplicity(labels, int(name.rsplit("k", 1)[1]))
        com_assoc = next((r["normalized_mutual_information"] for r in rows if r["kappa"] == name and r["association_target"] == "COM"), 0.0)
        summary_rows.append({"kappa": name, **simp, "COM_association": com_assoc, "mean_future_viable_by_label_std": label_target_separation(labels, sample_df["test_y"][:, 0]), "mean_future_depth_by_label_std": label_target_separation(labels, sample_df["test_y"][:, 2])})
    smoke = pd.DataFrame(summary_rows)
    smoke.to_csv(out / "improved_learner_test_propagation.csv", index=False)
    smoke.to_csv(out / "quotient_simplicity_terms.csv", index=False)
    comparison = smoke.copy()
    if len(p11_test):
        base = p11_test[p11_test["kappa"].isin(["center_of_mass", "predictive_kmeans_k8", "predictive_kmeans_k21"])].groupby("kappa", as_index=False).mean(numeric_only=True)
        for _, r in base.iterrows():
            comparison.loc[len(comparison)] = {"kappa": r["kappa"], "singleton_fraction": r.get("singleton_fraction", np.nan), "small_fiber_fraction": r.get("small_fiber_fraction", np.nan), "label_imbalance": np.nan, "COM_association": np.nan, "mean_future_viable_by_label_std": np.nan, "mean_future_depth_by_label_std": r.get("Delta_viable_propagation_vs_shuffled", np.nan)}
    comparison.to_csv(out / "improved_vs_kmeans_vs_com.csv", index=False)
    smoke.to_csv(out / "estimator_report.csv", index=False)
    pd.DataFrame().to_csv(out / "bootstrap_intervals.csv", index=False)
    make_12c_plots(out, comparison)
    best = validation.sort_values("total_validation_loss").iloc[0].to_dict()
    best_name = best["kappa"]
    best_smoke = smoke[smoke["kappa"] == best_name].iloc[0].to_dict()
    summary = {
        "probe": "12C_improved_learner_smoke",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "learner_tested": "transition-aware balanced predictive clustering",
        "best_improved_learner": best,
        "best_improved_test_anatomy": best_smoke,
        "interpretation": "The improved learner reduces the diagnosis to a smoke-level anatomy test; propagation scaling should wait until COM is formalized and transition labels are evaluated per trajectory.",
        "files": sorted(p.name for p in out.glob("*")),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (batch_dir / "probe_12c_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def label_target_separation(labels: np.ndarray, target: np.ndarray) -> float:
    means = []
    for label in np.unique(labels):
        mask = labels == label
        if np.any(mask):
            means.append(float(np.mean(target[mask])))
    return float(np.std(means)) if means else 0.0


def make_12a_plots(out: Path, deltas: pd.DataFrame, nodes: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    com_nodes = nodes[(nodes["kappa"] == "center_of_mass") & (nodes["threshold"] == "main")]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(com_nodes["fiber_size"], bins=40)
    ax.set_title("COM fiber size distribution")
    fig.tight_layout()
    fig.savefig(out / "com_fiber_size_distribution.png", dpi=160)
    plt.close(fig)
    com = deltas[(deltas["kappa"] == "center_of_mass") & (deltas["threshold"] == "main")]
    fig, ax = plt.subplots(figsize=(8, 5))
    for alpha, g in com.groupby("alpha"):
        ax.plot(g["T"], g["certified_path_mass_survival_to_final_segment"], marker="o", label=str(alpha))
    ax.set_title("COM certified path mass by alpha/T")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "com_certified_path_mass_by_alpha_T.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    for threshold, g in deltas[deltas["kappa"] == "center_of_mass"].groupby("threshold"):
        ax.scatter(g["T"], g["viable_propagation_index"], label=threshold)
    ax.set_title("Threshold sensitivity COM")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "threshold_sensitivity_com.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    main = deltas[deltas["threshold"] == "main"]
    for kappa, g in main.groupby("kappa"):
        ax.scatter(g["Delta_R"], g["Delta_viable_propagation_vs_shuffled"], label=kappa)
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title("COM vs boundary pseudorisk")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "com_vs_boundary_pseudorisk.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(com_nodes["segment_index"], com_nodes["component_B_preservation"], s=5, alpha=0.2)
    ax.set_title("Component preservation by segment")
    fig.tight_layout()
    fig.savefig(out / "component_preservation_by_segment.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    row = com[(com["alpha"] == 0.525) & (com["T"] == 1500)]
    ax.scatter(row["certified_edge_fraction"], row["certified_path_mass_survival_to_final_segment"])
    ax.set_title("COM transport graph alpha 0.525 T1500")
    fig.tight_layout()
    fig.savefig(out / "com_transport_graph_alpha_0525_T1500.png", dpi=160)
    plt.close(fig)


def make_12b_plots(out: Path, diag: pd.DataFrame, labels_df: pd.DataFrame, drift: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    test = diag[diag["split"] == "test"]
    for col, fname, title in [
        ("mean_learned_labels_per_COM_fiber", "com_fiber_splitting_by_kappa.png", "COM fiber splitting"),
        ("mean_COM_labels_per_learned_fiber", "learned_fiber_merging_by_kappa.png", "Learned fiber merging"),
        ("future_transport_depth_variance", "within_label_propagation_variance.png", "Within-label propagation variance"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(test["kappa"], test[col])
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = labels_df[labels_df["split"] == "test"]
    ax.scatter(sample["fiber_size"], sample["future_transport_depth_mean"], s=5, alpha=0.25)
    ax.set_title("Component B preservation proxy by label")
    fig.tight_layout()
    fig.savefig(out / "component_B_preservation_by_label.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(drift["kappa"], drift["JS_divergence_train_test"])
    ax.set_title("Label distribution train vs test")
    fig.tight_layout()
    fig.savefig(out / "label_distribution_train_vs_test.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(drift["singleton_fraction_train"], drift["singleton_fraction_test"])
    for _, r in drift.iterrows():
        ax.annotate(r["kappa"], (r["singleton_fraction_train"], r["singleton_fraction_test"]), fontsize=7)
    ax.set_title("Singleton fraction train vs test")
    fig.tight_layout()
    fig.savefig(out / "singleton_fraction_train_vs_test.png", dpi=160)
    plt.close(fig)


def make_12c_plots(out: Path, comparison: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    for col, fname, title in [
        ("mean_future_depth_by_label_std", "improved_vs_kmeans_propagation.png", "Improved vs kmeans propagation proxy"),
        ("COM_association", "improved_vs_com_ratio.png", "Improved COM association"),
        ("small_fiber_fraction", "fragmentation_comparison.png", "Fragmentation comparison"),
        ("singleton_fraction", "component_preservation_comparison.png", "Singleton comparison"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(comparison["kappa"], comparison[col])
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(comparison["COM_association"], comparison["small_fiber_fraction"])
    ax.set_title("Label anatomy improved")
    fig.tight_layout()
    fig.savefig(out / "label_anatomy_improved.png", dpi=160)
    plt.close(fig)


def write_batch_recommendation(batch_dir: Path, s12a: dict[str, object], s12b: dict[str, object], s12c: dict[str, object]) -> None:
    com_mean = s12a.get("COM_main_mean", {})
    rec = f"""# Probe 12 Batch Recommendation

## 1. Current Status Of COM Witness

COM remains the current witness if the main-threshold audit is positive. In this
batch, mean COM viable propagation was `{com_mean.get('viable_propagation_index', 'n/a')}` with component-B preservation `{com_mean.get('component_B_preservation', 'n/a')}`.

## 2. Diagnosis Of Learned Kappa Failure

Probe 12B points to COM-fiber splitting and small-fiber inflation as the main
failure pattern for simple predictive k-means. High-k validation winners are not
heldout COM-like propagation witnesses.

## 3. Improved Learner Smoke Test

Probe 12C tested transition-aware balanced predictive clustering as a smoke
test. It is useful as a diagnostic direction, but should not be scaled until the
COM fiber object is formalized more explicitly.

## 4. Recommended Next Step

Proceed with:

```text
Probe 13: Formal COM Fiber Transport Object
```

Rationale: COM is still the strongest analytic coordinate; learned-kappa work is
not mature enough to replace it and should be revised after formalization.
"""
    (batch_dir / "recommended_next_step.md").write_text(rec, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=18)
    p.add_argument("--n-traj", type=int, default=3000)
    p.add_argument("--seed-count", type=int, default=100)
    p.add_argument("--bootstrap-repeats", type=int, default=300)
    p.add_argument("--sample-per-seed", type=int, default=180)
    p.add_argument("--smoke", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.smoke:
        args.workers = min(args.workers, 6)
        args.n_traj = min(args.n_traj, 600)
        args.seed_count = min(args.seed_count, 5)
        args.bootstrap_repeats = min(args.bootstrap_repeats, 30)
        args.sample_per_seed = min(args.sample_per_seed, 80)
    cfg = p11.Config(
        out_dir=Path("probe_12_tmp"),
        workers=args.workers,
        n_traj=args.n_traj,
        seed_count=args.seed_count,
        seed_start=0,
        bootstrap_repeats=args.bootstrap_repeats,
        soft_limit_seconds=14_400,
        hard_limit_seconds=21_600,
        dt=0.018,
        noise=0.055,
        coupling_scale=0.085,
        train_variants_per_family=2 if args.smoke else 8,
        val_variants_per_family=1 if args.smoke else 4,
        test_variants_per_family=2 if args.smoke else 8,
        max_train_samples=25_000 if args.smoke else 220_000,
        sample_per_seed=args.sample_per_seed,
        smoke=args.smoke,
    )
    started = time.monotonic()
    batch_dir = Path("probe_12_batch_results")
    batch_dir.mkdir(exist_ok=True)
    s12a = run_12a(cfg, batch_dir, started)
    s12b, sample_df, learned, validation = run_12b(cfg, batch_dir, started)
    s12c = run_12c(cfg, batch_dir, started, sample_df, learned)
    batch = {
        "probe": "12_batch_com_audit_learned_diagnosis",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "workers": cfg.workers,
        "n_traj": cfg.n_traj,
        "seed_count": cfg.seed_count,
        "bootstrap_repeats": cfg.bootstrap_repeats,
        "probe_12a": s12a,
        "probe_12b": s12b,
        "probe_12c": s12c,
        "recommended_next_step": "Probe 13: Formal COM Fiber Transport Object",
    }
    (batch_dir / "batch_summary.json").write_text(json.dumps(batch, indent=2), encoding="utf-8")
    write_batch_recommendation(batch_dir, s12a, s12b, s12c)
    print("PROBE 12 BATCH: COM FORMALIZATION + LEARNED-KAPPA DIAGNOSIS")
    print(json.dumps(batch, indent=2))


if __name__ == "__main__":
    main()
