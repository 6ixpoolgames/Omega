#!/usr/bin/env python
"""Probe DAX-G0: minimal DAR rule-space persistence audit.

Enumerates elementary cellular automata and audits whether nontrivial compact
persistence appears preferentially in DAR-complete rule classes.
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


IC_FAMILIES = [
    "bernoulli_050",
    "bernoulli_025",
    "single_seed",
    "two_cell_seed",
    "short_random_block",
    "periodic_perturbation",
]
CONTROL_RULES = {
    "identity": [204],
    "left_shift": [170],
    "right_shift": [240],
    "complement": [51],
    "known_complex_reference": [30, 54, 90, 110],
}


@dataclass(frozen=True)
class Config:
    out_dir: Path
    ring_size: int
    T: int
    n_seeds: int
    diagram_count: int
    workers: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DAX_G0_minimal_DAR_rule_space_persistence_results"))
    p.add_argument("--ring-size", type=int, default=int(os.environ.get("DAX_G0_RING_SIZE", "256")))
    p.add_argument("--T", type=int, default=int(os.environ.get("DAX_G0_T", "256")))
    p.add_argument("--n-seeds", type=int, default=int(os.environ.get("DAX_G0_N_SEEDS", "64")))
    p.add_argument("--diagram-count", type=int, default=10)
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    return p.parse_args()


def rule_table(rule: int) -> np.ndarray:
    return np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)


def step(x: np.ndarray, table: np.ndarray) -> np.ndarray:
    left = np.roll(x, 1, axis=1)
    right = np.roll(x, -1, axis=1)
    idx = (left << 2) | (x << 1) | right
    return table[idx]


def initial_states(ic: str, cfg: Config, rng: np.random.Generator) -> np.ndarray:
    n, L = cfg.n_seeds, cfg.ring_size
    x = np.zeros((n, L), dtype=np.uint8)
    if ic == "bernoulli_050":
        return (rng.random((n, L)) < 0.50).astype(np.uint8)
    if ic == "bernoulli_025":
        return (rng.random((n, L)) < 0.25).astype(np.uint8)
    if ic == "single_seed":
        x[:, L // 2] = 1
        return x
    if ic == "two_cell_seed":
        x[:, L // 2] = 1
        x[:, L // 2 + 1] = 1
        return x
    if ic == "short_random_block":
        for s in range(n):
            width = rng.integers(8, 25)
            start = L // 2 - width // 2
            x[s, start : start + width] = (rng.random(width) < 0.5).astype(np.uint8)
        return x
    if ic == "periodic_perturbation":
        x[:, ::2] = 1
        for s in range(n):
            center = L // 2 + rng.integers(-8, 9)
            x[s, center - 2 : center + 3] ^= 1
        return x
    raise ValueError(ic)


def simulate(rule: int, ic: str, cfg: Config, seed_offset: int = 0) -> np.ndarray:
    rng = np.random.default_rng(710_000 + rule * 1009 + seed_offset * 17 + IC_FAMILIES.index(ic))
    table = rule_table(rule)
    x = initial_states(ic, cfg, rng)
    hist = np.empty((cfg.T + 1, cfg.n_seeds, cfg.ring_size), dtype=np.uint8)
    hist[0] = x
    for t in range(cfg.T):
        x = step(x, table)
        hist[t + 1] = x
    return hist


def primitive_classification(rule: int) -> dict[str, object]:
    table = rule_table(rule)
    depends = []
    for bit in [2, 1, 0]:
        dep = False
        for idx in range(8):
            j = idx ^ (1 << bit)
            if table[idx] != table[j]:
                dep = True
                break
        depends.append(dep)
    depends_left, depends_center, depends_right = depends
    reflected = np.zeros(8, dtype=np.uint8)
    for l in [0, 1]:
        for c in [0, 1]:
            for r in [0, 1]:
                idx = (l << 2) | (c << 1) | r
                ridx = (r << 2) | (c << 1) | l
                reflected[idx] = table[ridx]
    lr_asym = float(np.mean(table != reflected))
    ones = int(np.sum(table))
    preimage_compression = float(1.0 - min(ones, 8 - ones) / 4.0)
    directional = float(abs(int(depends_left) - int(depends_right)))
    relation_degree = int(depends_left) + int(depends_right)
    return {
        "rule": rule,
        "depends_left": depends_left,
        "depends_center": depends_center,
        "depends_right": depends_right,
        "relation_degree": relation_degree,
        "relation_complete": relation_degree > 0,
        "self_only": bool(depends_center and not depends_left and not depends_right),
        "no_local_self_relation": bool((not depends_center) and relation_degree > 0),
        "left_right_asymmetry": lr_asym,
        "temporal_irreversibility_proxy": preimage_compression,
        "directional_consequence": directional,
        "DAR_complete_structural": bool(relation_degree > 0 and preimage_compression > 0),
        "DAR_asymmetric_structural": bool(relation_degree > 0 and preimage_compression > 0 and (lr_asym > 0 or directional > 0)),
    }


def binary_entropy(p: np.ndarray | float) -> np.ndarray | float:
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def entropy_from_values(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    _, counts = np.unique(values, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(np.maximum(p, 1e-12))))


def component_lengths(row: np.ndarray) -> list[int]:
    idx = np.where(row == 1)[0]
    if len(idx) == 0:
        return []
    # Break periodic components at the largest zero gap.
    L = len(row)
    padded = np.r_[row, row]
    if np.all(row == 1):
        return [L]
    lengths = []
    seen = 0
    i = 0
    while i < L:
        if row[i] == 0:
            i += 1
            continue
        j = i
        while j < L and row[j] == 1:
            j += 1
        lengths.append(j - i)
        i = j
        seen += 1
    if row[0] == 1 and row[-1] == 1 and len(lengths) > 1:
        lengths[0] += lengths.pop()
    return lengths


def shifted_overlap(a: np.ndarray, b: np.ndarray, max_shift: int = 8) -> tuple[float, int]:
    best = -1.0
    best_shift = 0
    for s in range(-max_shift, max_shift + 1):
        score = float(np.mean(a == np.roll(b, s)))
        if score > best:
            best = score
            best_shift = s
    return best, best_shift


def estimate_period(series: np.ndarray) -> int:
    tail = series[-64:]
    for p in range(1, 33):
        if len(tail) > p and np.mean(tail[p:] == tail[:-p]) > 0.995:
            return p
    return 0


def metrics_for_history(hist: np.ndarray) -> dict[str, float]:
    T, n, L = hist.shape[0] - 1, hist.shape[1], hist.shape[2]
    active = hist.mean(axis=2)
    entropy_mean = float(np.mean(binary_entropy(active)))
    active_mean = float(np.mean(active))
    active_final = float(np.mean(active[-1]))
    extinction = float(np.mean(np.all(hist[-1] == 0, axis=1)))
    all_zero = extinction
    all_one = float(np.mean(np.all(hist[-1] == 1, axis=1)))
    fixed = float(np.mean(np.all(hist[-1] == hist[-2], axis=1)))
    period_flags = []
    comp_lifetimes = []
    comp_sizes = []
    recurrence_scores = []
    shifts = []
    turnover = []
    contrast = []
    fragmentation = []
    damage = []
    compress = []
    for s in range(n):
        h = hist[:, s]
        period_flags.append(estimate_period(h) > 0)
        centers = []
        prev_center = None
        lifetime = 0
        max_life = 0
        for t in range(0, T + 1, 4):
            lengths = component_lengths(h[t])
            good = [x for x in lengths if 1 <= x <= L // 4]
            comp_sizes.extend(good)
            fragmentation.append(len(good) / max(np.sum(h[t]), 1))
            if good:
                coords = np.where(h[t] == 1)[0]
                center = int(np.round(np.mean(coords)))
                centers.append(center)
                if prev_center is None or abs(center - prev_center) <= 12:
                    lifetime += 4
                else:
                    max_life = max(max_life, lifetime)
                    lifetime = 4
                prev_center = center
            else:
                max_life = max(max_life, lifetime)
                lifetime = 0
                prev_center = None
        comp_lifetimes.append(max(max_life, lifetime))
        a = h[max(0, T // 2)]
        b = h[-1]
        rec, sh = shifted_overlap(a, b)
        recurrence_scores.append(rec)
        shifts.append(sh / max(T // 2, 1))
        turnover.append(float(np.mean(a != b)))
        inside = b == 1
        if np.any(inside) and np.any(~inside):
            contrast.append(abs(float(np.mean(b[inside])) - float(np.mean(b[~inside]))))
        else:
            contrast.append(0.0)
        damage.append(float(np.mean(hist[-1, s] != np.roll(hist[-1, s], 1))))
        # simple run-length proxy: fewer transitions means more compressible
        transitions = np.sum(hist[-1, s] != np.roll(hist[-1, s], 1))
        compress.append(1.0 - transitions / L)
    sizes = np.array(comp_sizes if comp_sizes else [0])
    lifetimes = np.array(comp_lifetimes)
    recurrence = float(np.mean(recurrence_scores))
    material_turnover = float(np.mean(turnover))
    frozen = float(0.65 * fixed + 0.35 * np.mean(np.array(turnover) < 0.02))
    chaos = float(np.mean(binary_entropy(active[-64:].mean(axis=0))) * np.mean(damage))
    persistent_count = float(np.mean(lifetimes >= 32))
    localized_life_mean = float(np.mean(lifetimes))
    localized_life_max = float(np.max(lifetimes))
    signal_bg = float(np.mean(contrast) / max(np.std(active[-64:]) + 1e-9, 1e-9))
    return {
        "active_fraction_mean": active_mean,
        "active_fraction_final": active_final,
        "symbol_entropy_mean": entropy_mean,
        "extinction_rate": extinction,
        "all_zero_attractor_rate": all_zero,
        "all_one_attractor_rate": all_one,
        "global_fixed_point_rate": fixed,
        "global_periodic_rate": float(np.mean(period_flags)),
        "localized_component_lifetime_mean": localized_life_mean,
        "localized_component_lifetime_max": localized_life_max,
        "component_size_median": float(np.median(sizes)),
        "component_size_entropy": entropy_from_values(sizes),
        "persistent_component_count": persistent_count,
        "recurrence_up_to_shift": recurrence,
        "motif_survival_depth": localized_life_max / max(T, 1),
        "motif_material_turnover": material_turnover,
        "translation_velocity_estimate": float(np.mean(shifts)),
        "period_estimate": float(np.median([estimate_period(hist[:, s]) for s in range(n)])),
        "pattern_background_contrast": float(np.mean(contrast)),
        "local_entropy_inside_pattern": active_mean,
        "local_entropy_outside_pattern": 1.0 - active_mean,
        "signal_to_background_ratio": signal_bg,
        "exact_static_fraction": fixed,
        "global_period_fraction": float(np.mean(period_flags)),
        "low_turnover_persistence_fraction": float(np.mean(np.array(turnover) < 0.02)),
        "frozen_order_index": frozen,
        "activity_entropy": entropy_mean,
        "damage_spreading_rate": float(np.mean(damage)),
        "compressibility_proxy": float(np.mean(compress)),
        "component_fragmentation_rate": float(np.mean(fragmentation)),
        "chaos_index": chaos,
    }


def perturbation_diagnostic(rule: int, cfg: Config) -> dict[str, float]:
    small_cfg = Config(cfg.out_dir, cfg.ring_size, 96, min(16, cfg.n_seeds), cfg.diagram_count, 1)
    hist = simulate(rule, "short_random_block", small_cfg, seed_offset=99)
    rng = np.random.default_rng(730_000 + rule)
    mid = hist[32].copy()
    pert_codes = []
    base_codes = []
    survived = []
    returned = []
    for s in range(mid.shape[0]):
        x = mid[s : s + 1].copy()
        active = np.where(x[0] == 1)[0]
        pos = int(rng.choice(active)) if len(active) else small_cfg.ring_size // 2
        xp = x.copy()
        xp[0, pos] ^= 1
        table = rule_table(rule)
        xb = x.copy()
        for _ in range(64):
            x = step(x, table)
            xp = step(xp, table)
        base_codes.append(hash(xb.tobytes()))
        pert_codes.append(hash(xp.tobytes()))
        survived.append(np.any(xp))
        returned.append(float(np.mean(x == xp)) > 0.98)
    return {
        "rule": rule,
        "future_distinct_descendant_count": float(len(set(pert_codes))),
        "post_perturbation_survival_rate": float(np.mean(survived)),
        "return_to_same_pattern_rate": float(np.mean(returned)),
        "branching_without_explosion": float(len(set(pert_codes)) / max(len(pert_codes), 1)),
    }


def classify_persistence(row: dict[str, float]) -> str:
    if row["extinction_rate"] > 0.65 or row["all_zero_attractor_rate"] + row["all_one_attractor_rate"] > 0.65:
        return "collapse"
    if row["frozen_order_index"] > 0.65 and row["motif_material_turnover"] < 0.08:
        return "frozen_order"
    if row["global_periodic_rate"] > 0.65 and row["persistent_component_count"] < 0.35:
        return "global_periodic"
    if row["chaos_index"] > 0.55 and row["recurrence_up_to_shift"] < 0.80:
        return "chaotic"
    transported = (
        row["persistent_component_count"] > 0.20
        and row["localized_component_lifetime_max"] >= 48
        and row["recurrence_up_to_shift"] > 0.72
        and row["motif_material_turnover"] > 0.08
        and row["frozen_order_index"] < 0.70
    )
    if transported and abs(row["translation_velocity_estimate"]) > 0.01:
        return "transported_identity"
    if transported:
        return "localized_persistence"
    if row["persistent_component_count"] > 0.25 and row["component_fragmentation_rate"] > 0.10:
        return "emitter_or_generator"
    return "mixed"


def evaluate_rule(rule: int, cfg: Config) -> tuple[dict[str, float], list[dict[str, object]]]:
    ic_rows = []
    metric_rows = []
    for ic in IC_FAMILIES:
        hist = simulate(rule, ic, cfg)
        m = metrics_for_history(hist)
        metric_rows.append(m)
        ic_rows.append({"rule": rule, "ic_family": ic, **m})
    keys = metric_rows[0].keys()
    agg = {"rule": rule}
    for k in keys:
        agg[k] = float(np.mean([m[k] for m in metric_rows]))
    return agg, ic_rows


def evaluate_rule_worker(args: tuple[int, Config]) -> tuple[dict[str, float], list[dict[str, object]]]:
    return evaluate_rule(*args)


def make_plots(out: Path, rules: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    xs = np.arange(256)
    class_code = {c: i for i, c in enumerate(sorted(rules["classification"].unique()))}
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.scatter(xs, rules["localized_component_lifetime_max"], c=rules["classification"].map(class_code), s=18)
    ax.set_xlabel("ECA rule")
    ax.set_ylabel("localized lifetime max")
    fig.tight_layout()
    fig.savefig(out / "rule_space_persistence_map.png", dpi=160)
    plt.close(fig)
    counts = rules["classification"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(counts.index, counts.values)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "persistence_class_counts.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(rules["localized_component_lifetime_max"], rules["motif_material_turnover"], c=rules["frozen_order_index"])
    ax.set_xlabel("localized lifetime max")
    ax.set_ylabel("material turnover")
    fig.tight_layout()
    fig.savefig(out / "localized_lifetime_vs_turnover.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(rules["chaos_index"], rules["persistent_component_count"], c=rules["recurrence_up_to_shift"])
    ax.set_xlabel("chaos index")
    ax.set_ylabel("persistent component count")
    fig.tight_layout()
    fig.savefig(out / "chaos_vs_persistence_scatter.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(rules["frozen_order_index"], rules["motif_material_turnover"], c=rules["localized_component_lifetime_max"])
    ax.set_xlabel("frozen order index")
    ax.set_ylabel("material turnover")
    fig.tight_layout()
    fig.savefig(out / "frozen_vs_transported_identity_scatter.png", dpi=160)
    plt.close(fig)


def save_diagrams(out: Path, candidates: list[int], cfg: Config) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    d = out / "example_spacetime_diagrams"
    d.mkdir(exist_ok=True)
    small_cfg = Config(cfg.out_dir, 160, 160, 1, cfg.diagram_count, 1)
    for rule in candidates:
        hist = simulate(rule, "short_random_block", small_cfg)[..., :][..., :]
        img = hist[:, 0, :]
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(img, cmap="binary", interpolation="nearest", aspect="auto")
        ax.set_axis_off()
        fig.tight_layout(pad=0)
        fig.savefig(d / f"rule_{rule}_spacetime.png", dpi=140)
        plt.close(fig)


def enrichment_table(rules: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = {
        "self_only_rules": rules["self_only"],
        "neighbor_dependent_symmetric_rules": (rules["relation_complete"]) & (rules["left_right_asymmetry"] == 0),
        "neighbor_dependent_asymmetric_rules": (rules["relation_complete"]) & (rules["left_right_asymmetry"] > 0),
        "irreversible_neighbor_dependent_rules": (rules["relation_complete"]) & (rules["temporal_irreversibility_proxy"] > 0),
        "DAR_complete_rules": rules["DAR_complete"],
        "DAR_asymmetric_rules": rules["DAR_asymmetric"],
    }
    nontrivial = rules["classification"].isin(["localized_persistence", "transported_identity", "emitter_or_generator"])
    base = float(nontrivial.mean())
    for name, mask in groups.items():
        sub = rules[mask]
        rate = float(nontrivial[mask].mean()) if len(sub) else 0.0
        rows.append({"primitive_class": name, "rule_count": int(len(sub)), "nontrivial_persistence_rate": rate, "enrichment_over_base": rate - base})
    return pd.DataFrame(rows)


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    out = cfg.out_dir
    prim = pd.DataFrame([primitive_classification(r) for r in range(256)])
    metric_rows = []
    ic_rows = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(evaluate_rule_worker, (rule, cfg)) for rule in range(256)]
        for i, fut in enumerate(as_completed(futures), 1):
            agg, by_ic = fut.result()
            metric_rows.append(agg)
            ic_rows.extend(by_ic)
            if i % max(1, cfg.workers) == 0:
                print(json.dumps({"completed_rules": i, "total_rules": 256}), flush=True)
    metrics = pd.DataFrame(metric_rows)
    rules = prim.merge(metrics, on="rule")
    rules["distinction_survival"] = 1.0 - rules["extinction_rate"]
    rules["DAR_complete"] = (rules["distinction_survival"] > 0.10) & rules["relation_complete"] & (rules["temporal_irreversibility_proxy"] > 0) & (rules["extinction_rate"] < 0.90)
    rules["DAR_asymmetric"] = rules["DAR_complete"] & ((rules["left_right_asymmetry"] > 0) | (rules["directional_consequence"] > 0))
    rules["classification"] = rules.apply(lambda r: classify_persistence(r.to_dict()), axis=1)
    perturb = pd.DataFrame([perturbation_diagnostic(int(r), cfg) for r in rules["rule"]])
    rules = rules.merge(perturb, on="rule", how="left")
    rules[["rule"]].assign(rule_binary=[format(r, "08b") for r in range(256)]).to_csv(out / "rule_table.csv", index=False)
    prim.to_csv(out / "primitive_classification.csv", index=False)
    rules.to_csv(out / "persistence_metrics_by_rule.csv", index=False)
    rules[["rule", "classification", "DAR_complete", "DAR_asymmetric", "localized_component_lifetime_max", "recurrence_up_to_shift", "motif_material_turnover", "frozen_order_index", "chaos_index"]].to_csv(out / "persistence_classification.csv", index=False)
    enrich = enrichment_table(rules)
    enrich.to_csv(out / "primitive_class_enrichment.csv", index=False)
    pd.DataFrame(ic_rows).to_csv(out / "initial_condition_sensitivity.csv", index=False)
    motif_cols = ["rule", "classification", "localized_component_lifetime_max", "recurrence_up_to_shift", "motif_material_turnover", "translation_velocity_estimate", "pattern_background_contrast"]
    rules.sort_values(["localized_component_lifetime_max", "motif_material_turnover"], ascending=False)[motif_cols].head(50).to_csv(out / "motif_examples.csv", index=False)
    perturb.to_csv(out / "perturbation_diagnostics.csv", index=False)
    control_rows = []
    for label, rs in CONTROL_RULES.items():
        sub = rules[rules["rule"].isin(rs)]
        control_rows.append({"control_family": label, "rules": " ".join(map(str, rs)), "mean_lifetime_max": float(sub["localized_component_lifetime_max"].mean()), "classifications": " ".join(sorted(sub["classification"].unique()))})
    pd.DataFrame(control_rows).to_csv(out / "control_rule_summary.csv", index=False)
    warnings = []
    if rules["classification"].isin(["localized_persistence", "transported_identity"]).sum() == 0:
        warnings.append("NO_LOCALIZED_OR_TRANSPORTED_RULES_DETECTED")
    if rules.loc[rules["classification"].isin(["localized_persistence", "transported_identity"]), "frozen_order_index"].mean(skipna=True) > 0.6:
        warnings.append("PERSISTENCE_MAY_BE_FROZEN")
    pd.DataFrame([{"warning": w} for w in warnings]).to_csv(out / "estimator_report.csv", index=False)
    make_plots(out, rules)
    top_rules = rules.sort_values(["localized_component_lifetime_max", "motif_material_turnover"], ascending=False)["rule"].head(cfg.diagram_count).astype(int).tolist()
    control_diagrams = [0, 204, 170, 240, 30, 90]
    save_diagrams(out, sorted(set(top_rules + control_diagrams)), cfg)
    fig_enrichment(out, enrich)
    fig_ic(out, pd.DataFrame(ic_rows))
    summary = make_summary(cfg, started, rules, enrich, warnings)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def fig_enrichment(out: Path, enrich: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(enrich["primitive_class"], enrich["enrichment_over_base"])
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("nontrivial persistence enrichment")
    fig.tight_layout()
    fig.savefig(out / "primitive_class_enrichment.png", dpi=160)
    plt.close(fig)


def fig_ic(out: Path, ic: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    g = ic.groupby("ic_family")["localized_component_lifetime_max"].mean()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(g.index, g.values)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "initial_condition_sensitivity.png", dpi=160)
    plt.close(fig)


def make_summary(cfg: Config, started: float, rules: pd.DataFrame, enrich: pd.DataFrame, warnings: list[str]) -> dict[str, object]:
    nontriv = rules["classification"].isin(["localized_persistence", "transported_identity", "emitter_or_generator"])
    localized = int((rules["classification"] == "localized_persistence").sum())
    transported = int((rules["classification"] == "transported_identity").sum())
    emitter = int((rules["classification"] == "emitter_or_generator").sum())
    dar_enrich = float(enrich.loc[enrich["primitive_class"] == "DAR_complete_rules", "enrichment_over_base"].iloc[0])
    dara_enrich = float(enrich.loc[enrich["primitive_class"] == "DAR_asymmetric_rules", "enrichment_over_base"].iloc[0])
    static_or_chaos = bool(
        rules.sort_values("localized_component_lifetime_max", ascending=False).head(20)["classification"].isin(["frozen_order", "chaotic", "global_periodic"]).mean() > 0.6
    )
    candidates = rules[nontriv].sort_values(["localized_component_lifetime_max", "motif_material_turnover"], ascending=False)
    best = candidates.iloc[0] if len(candidates) else rules.sort_values("localized_component_lifetime_max", ascending=False).iloc[0]
    if transported > 0 and dar_enrich > 0:
        rec = "G0 found transported identity enriched in DAR-complete rules; proceed to G1 motif anatomy."
        next_probe = "DAX_G1_persistence_motif_anatomy_and_robustness"
    elif localized + transported + emitter > 0 and not static_or_chaos:
        rec = "G0 found nontrivial persistence but enrichment is weak; use G1 diagnostically, not as validation."
        next_probe = "DAX_G1_diagnostic_motif_anatomy"
    elif static_or_chaos:
        rec = "G0 metrics mostly select frozen or chaotic controls; calibrate identity-through-transformation detection."
        next_probe = "persistence_metric_calibration"
    else:
        rec = "G0 found no nontrivial persistence under current detector; expand to q=3/r=1 sampled rules or calibrate detector."
        next_probe = "DAX_G0b_q3_or_detector_calibration"
    return {
        "probe": "DAX_G0_minimal_DAR_rule_space_persistence",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "rule_space": {"q": 2, "radius": 1, "rule_count": 256, "ring_size": cfg.ring_size, "T": cfg.T, "n_seeds_per_ic": cfg.n_seeds},
        "primary_result": {
            "nontrivial_persistence_found": bool(localized + transported + emitter > 0),
            "localized_persistence_rule_count": localized,
            "transported_identity_rule_count": transported,
            "emitter_or_generator_rule_count": emitter,
            "DAR_complete_enriched": bool(dar_enrich > 0),
            "DAR_asymmetric_enriched": bool(dara_enrich > 0),
            "metrics_select_static_or_chaos": static_or_chaos,
        },
        "top_candidate_rules": candidates["rule"].head(12).astype(int).tolist(),
        "control_rule_results": {
            "collapse_rules": int((rules["classification"] == "collapse").sum()),
            "frozen_order_rules": int((rules["classification"] == "frozen_order").sum()),
            "global_periodic_rules": int((rules["classification"] == "global_periodic").sum()),
            "chaotic_rules": int((rules["classification"] == "chaotic").sum()),
        },
        "best_candidate_profile": {
            "rule": int(best["rule"]),
            "classification": str(best["classification"]),
            "localized_component_lifetime_max": float(best["localized_component_lifetime_max"]),
            "recurrence_up_to_shift": float(best["recurrence_up_to_shift"]),
            "motif_material_turnover": float(best["motif_material_turnover"]),
            "translation_velocity_estimate": float(best["translation_velocity_estimate"]),
            "future_distinct_descendant_count": float(best.get("future_distinct_descendant_count", 0.0) if not pd.isna(best.get("future_distinct_descendant_count", np.nan)) else 0.0),
            "frozen_order_index": float(best["frozen_order_index"]),
            "chaos_index": float(best["chaos_index"]),
        },
        "recommendation": rec,
        "next_probe": next_probe,
        "estimator_warnings": warnings,
    }


def main() -> None:
    args = parse_args()
    cfg = Config(args.out_dir, args.ring_size, args.T, args.n_seeds, args.diagram_count, min(args.workers, 18))
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    summary = build_outputs(cfg, started)
    print("PROBE DAX-G0: MINIMAL DAR RULE-SPACE PERSISTENCE")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
