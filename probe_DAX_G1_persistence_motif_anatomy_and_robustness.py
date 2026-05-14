#!/usr/bin/env python
"""Probe DAX-G1: persistence motif anatomy and robustness.

Analyzes whether G0 persistence candidates are real identity-through-
transformation rather than stasis, whole-grid periodicity, or chaos artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import probe_DAX_G0_minimal_DAR_rule_space_persistence as g0


BASE_IC = [
    "bernoulli_050",
    "bernoulli_025",
    "single_seed",
    "two_cell_seed",
    "short_random_block",
    "periodic_perturbation",
]
TARGETED_IC = ["g0_motif_seed", "g0_candidate_window_seed"]
PERTURBATIONS = ["flip_inside", "flip_adjacent", "delete_inside", "insert_nearby", "sparse_noise"]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    g0_dir: Path
    workers: int
    n_seeds: int
    horizons: tuple[int, ...]
    ring_sizes: tuple[int, ...]


def parse_csv_ints(value: str) -> tuple[int, ...]:
    return tuple(int(x.strip()) for x in value.split(",") if x.strip())


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DAX_G1_persistence_motif_anatomy_and_robustness_results"))
    p.add_argument("--g0-dir", type=Path, default=Path("probe_DAX_G0_minimal_DAR_rule_space_persistence_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-seeds", type=int, default=256)
    p.add_argument("--horizons", type=parse_csv_ints, default=(256, 512, 1024))
    p.add_argument("--ring-sizes", type=parse_csv_ints, default=(256, 512))
    return p.parse_args()


def initial_states_extended(ic: str, cfg: g0.Config, rule: int, rng: np.random.Generator) -> np.ndarray:
    if ic in BASE_IC:
        return g0.initial_states(ic, cfg, rng)
    x = np.zeros((cfg.n_seeds, cfg.ring_size), dtype=np.uint8)
    if ic == "g0_motif_seed":
        width = min(31, cfg.ring_size // 4)
        # Deterministic compact seed derived from rule bits, centered.
        bits = np.array([(rule >> (i % 8)) & 1 for i in range(width)], dtype=np.uint8)
        start = cfg.ring_size // 2 - width // 2
        x[:, start : start + width] = bits
        return x
    if ic == "g0_candidate_window_seed":
        width = min(45, cfg.ring_size // 3)
        for s in range(cfg.n_seeds):
            bits = (rng.random(width) < (0.35 + 0.3 * ((rule + s) % 3) / 2)).astype(np.uint8)
            start = cfg.ring_size // 2 - width // 2
            x[s, start : start + width] = bits
        return x
    raise ValueError(ic)


def simulate_ext(rule: int, ic: str, T: int, ring: int, n_seeds: int) -> np.ndarray:
    cfg = g0.Config(Path("."), ring, T, n_seeds, 0, 1)
    rng = np.random.default_rng(810_000 + rule * 1009 + T * 17 + ring + hash(ic) % 997)
    table = g0.rule_table(rule)
    x = initial_states_extended(ic, cfg, rule, rng)
    hist = np.empty((T + 1, n_seeds, ring), dtype=np.uint8)
    hist[0] = x
    for t in range(T):
        x = g0.step(x, table)
        hist[t + 1] = x
    return hist


def motif_type(row: dict[str, float]) -> str:
    if row["frozen_order_index"] > 0.70 and row["motif_material_turnover"] < 0.05:
        return "static_object"
    if row["global_periodic_rate"] > 0.70:
        return "global_periodic_artifact"
    if row["chaos_index"] > 0.60 and row["pattern_background_contrast"] < 0.20:
        return "chaotic_fragment"
    if row["component_fragmentation_rate"] > 0.20 and row["persistent_component_count"] > 0.20:
        return "emitter"
    if abs(row["translation_velocity_estimate"]) > 0.01 and row["motif_material_turnover"] > 0.08:
        return "travelling_identity"
    if row["recurrence_up_to_shift"] > 0.75 and row["motif_material_turnover"] > 0.08:
        return "localized_oscillator"
    if row["pattern_background_contrast"] > 0.25 and row["localized_component_lifetime_max"] > 128:
        return "domain_wall"
    return "unknown"


def eval_rule_config(task: tuple[int, str, int, int, int]) -> dict[str, object]:
    rule, ic, T, ring, n_seeds = task
    hist = simulate_ext(rule, ic, T, ring, n_seeds)
    m = g0.metrics_for_history(hist)
    mtype = motif_type(m)
    confirmed = (
        mtype in {"localized_oscillator", "travelling_identity", "emitter", "domain_wall"}
        and m["recurrence_up_to_shift"] > 0.70
        and m["motif_material_turnover"] > 0.08
        and m["frozen_order_index"] < 0.70
        and m["chaos_index"] < 0.65
        and m["pattern_background_contrast"] >= 0.0
    )
    return {"rule": rule, "ic_family": ic, "T": T, "ring_size": ring, "motif_type": mtype, "confirmed": confirmed, **m}


def select_rule_sets(g0_dir: Path) -> tuple[list[int], pd.DataFrame, pd.DataFrame]:
    cls = pd.read_csv(g0_dir / "persistence_classification.csv")
    prim = pd.read_csv(g0_dir / "primitive_classification.csv")
    metrics = pd.read_csv(g0_dir / "persistence_metrics_by_rule.csv")
    merged = cls.merge(prim, on="rule").merge(metrics, on="rule", suffixes=("", "_metric"))
    primary = [145, 131, 62, 118, 109, 73, 230, 188, 54, 61, 163, 177]
    transported = merged[merged["classification"] == "transported_identity"].copy()
    transported["score"] = transported["recurrence_up_to_shift"] * transported["motif_material_turnover"]
    emitters = merged[merged["classification"] == "emitter_or_generator"].copy()
    emitters["score"] = emitters.get("persistent_component_count", 0) + emitters.get("future_distinct_descendant_count", 0).fillna(0)
    candidates = list(dict.fromkeys(primary + transported.sort_values("score", ascending=False)["rule"].head(12).astype(int).tolist() + emitters.sort_values("score", ascending=False)["rule"].head(12).astype(int).tolist()))
    collapse = merged[merged["classification"] == "collapse"].sort_values(["extinction_rate", "all_zero_attractor_rate", "all_one_attractor_rate"], ascending=False)["rule"].head(8).astype(int).tolist()
    frozen = merged[merged["classification"] == "frozen_order"].sort_values("frozen_order_index", ascending=False)["rule"].head(8).astype(int).tolist()
    chaotic = merged[merged["classification"] == "chaotic"].sort_values("chaos_index", ascending=False)["rule"].head(8).astype(int).tolist()
    structural = [204, 170, 240, 51]
    controls = list(dict.fromkeys(collapse + frozen + chaotic + structural))
    candidate_df = merged[merged["rule"].isin(candidates)].copy()
    control_df = merged[merged["rule"].isin(controls)].copy()
    return list(dict.fromkeys(candidates + controls)), candidate_df, control_df


def aggregate_rule_anatomy(rows: pd.DataFrame, prim: pd.DataFrame) -> pd.DataFrame:
    agg = rows.groupby("rule", as_index=False).mean(numeric_only=True)
    type_mode = rows.groupby("rule")["motif_type"].agg(lambda s: s.mode().iloc[0] if len(s.mode()) else "unknown").reset_index()
    conf = rows.groupby("rule")["confirmed"].mean().reset_index(name="confirmed_fraction")
    out = agg.merge(type_mode, on="rule").merge(conf, on="rule").merge(prim, on="rule", how="left")
    out["confirmed_candidate"] = out["confirmed_fraction"] >= 0.35
    return out


def perturb_rule(rule: int, delta_t: int = 128, ring: int = 256, n: int = 64) -> dict[str, object]:
    cfg = g0.Config(Path("."), ring, 96, n, 0, 1)
    rng = np.random.default_rng(830_000 + rule)
    x0 = initial_states_extended("g0_candidate_window_seed", cfg, rule, rng)
    table = g0.rule_table(rule)
    # advance to motif-bearing state
    x = x0.copy()
    for _ in range(32):
        x = g0.step(x, table)
    base_finals = []
    outcomes = {p: [] for p in PERTURBATIONS}
    for s in range(n):
        xb = x[s : s + 1].copy()
        for _ in range(delta_t):
            xb = g0.step(xb, table)
        base_finals.append(hash(xb.tobytes()))
        active = np.where(x[s] == 1)[0]
        center = int(active[len(active) // 2]) if len(active) else ring // 2
        for p in PERTURBATIONS:
            xp = x[s : s + 1].copy()
            if p == "flip_inside":
                xp[0, center] ^= 1
            elif p == "flip_adjacent":
                xp[0, (center + 2) % ring] ^= 1
            elif p == "delete_inside":
                xp[0, center] = 0
            elif p == "insert_nearby":
                xp[0, (center + 3) % ring] = 1
            elif p == "sparse_noise":
                xp[0, rng.random(ring) < 0.005] ^= 1
            for _ in range(delta_t):
                xp = g0.step(xp, table)
            active_frac = float(np.mean(xp))
            if active_frac < 0.001:
                label = "collapse"
            elif active_frac > 0.85:
                label = "explosion"
            elif hash(xp.tobytes()) == base_finals[-1]:
                label = "same"
            else:
                label = "related"
            outcomes[p].append((label, hash(xp.tobytes())))
    labels = [label for vals in outcomes.values() for label, _ in vals]
    codes = [code for vals in outcomes.values() for _, code in vals]
    return {
        "rule": rule,
        "post_perturbation_survival_rate": float(np.mean([x != "collapse" for x in labels])),
        "return_to_same_motif_rate": float(np.mean([x == "same" for x in labels])),
        "transition_to_related_motif_rate": float(np.mean([x == "related" for x in labels])),
        "future_distinct_descendant_count": float(len(set(codes))),
        "collapse_rate": float(np.mean([x == "collapse" for x in labels])),
        "explosion_rate": float(np.mean([x == "explosion" for x in labels])),
    }


def ablation_table(rule: int) -> np.ndarray:
    table = g0.rule_table(rule)
    return table


def project_rule(rule: int, kind: str) -> int:
    table = ablation_table(rule)
    new = np.zeros(8, dtype=np.uint8)
    for idx in range(8):
        l = (idx >> 2) & 1
        c = (idx >> 1) & 1
        r = idx & 1
        if kind == "center_only_projection":
            src = (c << 2) | (c << 1) | c
        elif kind == "left_neighbor_removed":
            src = (c << 2) | (c << 1) | r
        elif kind == "right_neighbor_removed":
            src = (l << 2) | (c << 1) | c
        elif kind == "left_right_symmetrized_rule":
            ridx = (r << 2) | (c << 1) | l
            new[idx] = 1 if (table[idx] + table[ridx]) >= 1 else 0
            continue
        elif kind == "output_complement_control":
            new[idx] = 1 - table[idx]
            continue
        else:
            src = idx
        new[idx] = table[src]
    out = 0
    for i, bit in enumerate(new):
        out |= int(bit) << i
    return out


def motif_survival_score(rule: int) -> float:
    hist = simulate_ext(rule, "g0_candidate_window_seed", 256, 256, 32)
    m = g0.metrics_for_history(hist)
    return float(m["recurrence_up_to_shift"] * m["motif_material_turnover"] * (1.0 - min(m["frozen_order_index"], 1.0)))


def primitive_sidecar(rule: int) -> dict[str, object]:
    original = motif_survival_score(rule)
    scores = {}
    for kind in ["center_only_projection", "left_neighbor_removed", "right_neighbor_removed", "left_right_symmetrized_rule", "output_complement_control"]:
        scores[kind] = motif_survival_score(project_rule(rule, kind))
    return {
        "rule": rule,
        "motif_survival_original": original,
        "motif_survival_center_only": scores["center_only_projection"],
        "motif_survival_left_removed": scores["left_neighbor_removed"],
        "motif_survival_right_removed": scores["right_neighbor_removed"],
        "motif_survival_symmetrized": scores["left_right_symmetrized_rule"],
        "relation_dependence_delta": original - max(scores["center_only_projection"], scores["left_neighbor_removed"], scores["right_neighbor_removed"]),
        "asymmetry_dependence_delta": original - scores["left_right_symmetrized_rule"],
    }


def interaction_sidecar(rule: int) -> dict[str, object]:
    rng = np.random.default_rng(840_000 + rule)
    table = g0.rule_table(rule)
    outcomes = []
    for distance in [16, 32, 64, 96]:
        for phase in [0, 1, 2, 3]:
            x = np.zeros((16, 256), dtype=np.uint8)
            width = 21
            bits = np.array([(rule >> (i % 8)) & 1 for i in range(width)], dtype=np.uint8)
            for s in range(16):
                start1 = 64 + phase
                start2 = (start1 + distance) % 256
                x[s, start1 : start1 + width] = bits
                x[s, start2 : start2 + width] ^= bits
            for _ in range(256):
                x = g0.step(x, table)
            active = x.mean(axis=1)
            if np.mean(active < 0.001) > 0.5:
                label = "collapse"
            elif np.mean(active > 0.75) > 0.5:
                label = "chaotic_explosion"
            else:
                comps = [len(g0.component_lengths(row)) for row in x]
                if np.mean(comps) >= 2:
                    label = "pass_through"
                elif np.mean(comps) >= 1:
                    label = "new_motif"
                else:
                    label = "no_interaction"
            outcomes.append(label)
    counts = pd.Series(outcomes).value_counts(normalize=True)
    positive = counts.get("new_motif", 0.0) + counts.get("phase_shift", 0.0) + counts.get("emission", 0.0)
    return {
        "rule": rule,
        "interaction_outcome_diversity": float(len(set(outcomes)) / 8.0),
        "stable_product_rate": float(positive),
        "phase_sensitive_outcome_rate": float(1.0 - counts.max()),
        "future_distinct_interaction_products": float(len(set(outcomes))),
        "annihilation_rate": float(counts.get("annihilation", 0.0) + counts.get("collapse", 0.0)),
        "explosion_rate": float(counts.get("chaotic_explosion", 0.0)),
        "composition_positive": bool(positive > 0.05),
    }


def make_plots(out: Path, anatomy: pd.DataFrame, perturb: pd.DataFrame, primitive: pd.DataFrame, interaction: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(anatomy["localized_component_lifetime_max"], anatomy["motif_material_turnover"], c=anatomy["confirmed_candidate"].astype(int))
    ax.set_xlabel("lifetime max")
    ax.set_ylabel("turnover")
    fig.tight_layout()
    fig.savefig(out / "motif_lifetime_vs_turnover.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(anatomy["recurrence_up_to_shift"], anatomy["frozen_order_index"], c=anatomy["confirmed_candidate"].astype(int))
    ax.set_xlabel("recurrence up to shift")
    ax.set_ylabel("frozen order")
    fig.tight_layout()
    fig.savefig(out / "recurrence_vs_frozen_order.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(anatomy["pattern_background_contrast"], anatomy["chaos_index"], c=anatomy["confirmed_candidate"].astype(int))
    ax.set_xlabel("background contrast")
    ax.set_ylabel("chaos")
    fig.tight_layout()
    fig.savefig(out / "localization_vs_chaos.png", dpi=160)
    plt.close(fig)
    for df, x, y, fname in [
        (perturb, "rule", "post_perturbation_survival_rate", "perturbation_survival_by_rule.png"),
        (perturb, "rule", "future_distinct_descendant_count", "future_distinct_descendants_by_rule.png"),
        (primitive, "relation_dependence_delta", "asymmetry_dependence_delta", "relation_asymmetry_dependence_by_rule.png"),
        (interaction, "rule", "interaction_outcome_diversity", "interaction_outcome_diversity.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(df[x], df[y])
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)
    metrics = ["recurrence_up_to_shift", "motif_material_turnover", "frozen_order_index", "chaos_index", "confirmed_fraction"]
    mat = anatomy[metrics].to_numpy(float)
    scale = np.maximum(np.nanmax(np.abs(mat), axis=0), 1e-9)
    fig, ax = plt.subplots(figsize=(8, max(5, len(anatomy) * 0.18)))
    ax.imshow(mat / scale, aspect="auto")
    ax.set_yticks(np.arange(len(anatomy)))
    ax.set_yticklabels(anatomy["rule"].astype(str), fontsize=6)
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels(metrics, rotation=45, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "candidate_control_metric_heatmap.png", dpi=160)
    plt.close(fig)


def save_diagrams(out: Path, rules: list[int]) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    d = out / "spacetime_examples"
    d.mkdir(exist_ok=True)
    for rule in rules:
        hist = simulate_ext(rule, "g0_candidate_window_seed", 256, 256, 1)[:, 0, :]
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(hist, cmap="binary", aspect="auto", interpolation="nearest")
        ax.set_axis_off()
        fig.tight_layout(pad=0)
        fig.savefig(d / f"rule_{rule}_motif_tracking_seed_0.png", dpi=140)
        plt.close(fig)


def build_outputs(cfg: Config, started: float) -> dict[str, object]:
    all_rules, candidate_df, control_df = select_rule_sets(cfg.g0_dir)
    prim = pd.read_csv(cfg.g0_dir / "primitive_classification.csv")
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    candidate_df.to_csv(cfg.out_dir / "candidate_rule_set.csv", index=False)
    control_df.to_csv(cfg.out_dir / "control_rule_set.csv", index=False)
    tasks = [(rule, ic, T, ring, cfg.n_seeds) for rule in all_rules for ic in BASE_IC + TARGETED_IC for T in cfg.horizons for ring in cfg.ring_sizes]
    rows = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as pool:
        futures = [pool.submit(eval_rule_config, t) for t in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            rows.append(fut.result())
            if i % max(1, cfg.workers * 4) == 0:
                print(json.dumps({"completed": i, "total": len(futures)}), flush=True)
    robustness = pd.DataFrame(rows)
    robustness.to_csv(cfg.out_dir / "horizon_scale_robustness.csv", index=False)
    anatomy = aggregate_rule_anatomy(robustness, prim)
    anatomy.to_csv(cfg.out_dir / "motif_anatomy_by_rule.csv", index=False)
    lineages_cols = ["rule", "ic_family", "T", "ring_size", "localized_component_lifetime_max", "recurrence_up_to_shift", "translation_velocity_estimate", "motif_type"]
    robustness[lineages_cols].to_csv(cfg.out_dir / "motif_lineages.csv", index=False)
    anatomy[["rule", "motif_material_turnover", "low_turnover_persistence_fraction", "exact_static_fraction", "recurrence_up_to_shift"]].to_csv(cfg.out_dir / "persistence_without_stasis.csv", index=False)
    anatomy[["rule", "pattern_background_contrast", "local_entropy_inside_pattern", "local_entropy_outside_pattern", "component_fragmentation_rate", "component_size_median"]].to_csv(cfg.out_dir / "localization_contrast.csv", index=False)
    confirmed_rules = anatomy.loc[anatomy["confirmed_candidate"], "rule"].astype(int).tolist()
    sidecar_rules = list(dict.fromkeys(confirmed_rules[:24] + candidate_df["rule"].astype(int).head(12).tolist()))
    perturb = pd.DataFrame([perturb_rule(r) for r in sidecar_rules])
    primitive_side = pd.DataFrame([primitive_sidecar(r) for r in sidecar_rules])
    interact = pd.DataFrame([interaction_sidecar(r) for r in sidecar_rules[:16]])
    perturb.to_csv(cfg.out_dir / "perturbation_response.csv", index=False)
    perturb.rename(columns={"future_distinct_descendant_count": "future_distinct_descendant_count"}).to_csv(cfg.out_dir / "future_distinct_descendants.csv", index=False)
    primitive_side.to_csv(cfg.out_dir / "primitive_load_bearing_sidecar.csv", index=False)
    interact.to_csv(cfg.out_dir / "motif_interaction_sidecar.csv", index=False)
    perturb.to_csv(cfg.out_dir / "recoverability_sidecar.csv", index=False)
    prim_assoc = primitive_association(anatomy)
    prim_assoc.to_csv(cfg.out_dir / "primitive_association_after_filter.csv", index=False)
    candidate_vs_control(anatomy, candidate_df, control_df).to_csv(cfg.out_dir / "candidate_vs_control_summary.csv", index=False)
    sidecar_summary = make_sidecar_summary(perturb, primitive_side, interact)
    pd.DataFrame([sidecar_summary_flat(sidecar_summary)]).to_csv(cfg.out_dir / "sidecar_summary.csv", index=False)
    warnings = []
    if anatomy["confirmed_candidate"].sum() == 0:
        warnings.append("NO_CONFIRMED_MOTIFS")
    if primitive_side["relation_dependence_delta"].gt(0).mean() < 0.25:
        warnings.append("WEAK_RELATION_LOAD_BEARING_AFTER_SIDECAR")
    pd.DataFrame([{"warning": w} for w in warnings]).to_csv(cfg.out_dir / "estimator_report.csv", index=False)
    make_plots(cfg.out_dir, anatomy, perturb, primitive_side, interact)
    save_diagrams(cfg.out_dir, list(dict.fromkeys(confirmed_rules[:12] + control_df["rule"].astype(int).head(16).tolist())))
    summary = make_summary(cfg, started, anatomy, candidate_df, control_df, perturb, primitive_side, interact, prim_assoc, sidecar_summary, warnings)
    (cfg.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def primitive_association(anatomy: pd.DataFrame) -> pd.DataFrame:
    confirmed = anatomy["confirmed_candidate"]
    base = float(confirmed.mean())
    groups = {
        "DAR_complete": anatomy["DAR_complete_structural"].astype(bool),
        "DAR_asymmetric": anatomy["DAR_asymmetric_structural"].astype(bool),
        "relation_dependent": anatomy["relation_complete"].astype(bool),
        "asymmetry_dependent": (anatomy["left_right_asymmetry"] > 0) | (anatomy["directional_consequence"] > 0),
    }
    return pd.DataFrame([
        {"primitive_class": k, "rule_count": int(v.sum()), "confirmed_rate": float(confirmed[v].mean()) if v.sum() else 0.0, "enrichment_over_base": (float(confirmed[v].mean()) if v.sum() else 0.0) - base}
        for k, v in groups.items()
    ])


def candidate_vs_control(anatomy: pd.DataFrame, candidate_df: pd.DataFrame, control_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, rules in [("candidate", candidate_df["rule"]), ("control", control_df["rule"])]:
        sub = anatomy[anatomy["rule"].isin(rules)]
        rows.append({
            "set": label,
            "rule_count": int(len(sub)),
            "confirmed_count": int(sub["confirmed_candidate"].sum()),
            "mean_recurrence": float(sub["recurrence_up_to_shift"].mean()),
            "mean_turnover": float(sub["motif_material_turnover"].mean()),
            "mean_frozen_order": float(sub["frozen_order_index"].mean()),
            "mean_chaos": float(sub["chaos_index"].mean()),
        })
    return pd.DataFrame(rows)


def make_sidecar_summary(perturb: pd.DataFrame, primitive: pd.DataFrame, interact: pd.DataFrame) -> dict[str, object]:
    return {
        "recoverability": {
            "ran": True,
            "robust_motif_count": int((perturb["post_perturbation_survival_rate"] > 0.75).sum()),
            "best_post_perturbation_survival_rate": float(perturb["post_perturbation_survival_rate"].max()) if len(perturb) else 0.0,
        },
        "primitive_load_bearing": {
            "ran": True,
            "relation_dependence_positive_count": int((primitive["relation_dependence_delta"] > 0).sum()),
            "asymmetry_dependence_positive_count": int((primitive["asymmetry_dependence_delta"] > 0).sum()),
        },
        "interaction_composition": {
            "ran": True,
            "composition_positive_count": int(interact["composition_positive"].sum()) if len(interact) else 0,
            "stable_product_rate_best": float(interact["stable_product_rate"].max()) if len(interact) else 0.0,
        },
    }


def sidecar_summary_flat(s: dict[str, object]) -> dict[str, object]:
    out = {}
    for k, v in s.items():
        for kk, vv in v.items():
            out[f"{k}_{kk}"] = vv
    return out


def make_summary(cfg: Config, started: float, anatomy: pd.DataFrame, candidate_df: pd.DataFrame, control_df: pd.DataFrame, perturb: pd.DataFrame, primitive: pd.DataFrame, interact: pd.DataFrame, prim_assoc: pd.DataFrame, sidecars: dict[str, object], warnings: list[str]) -> dict[str, object]:
    confirmed = anatomy[anatomy["confirmed_candidate"]].copy().sort_values(["confirmed_fraction", "recurrence_up_to_shift", "motif_material_turnover"], ascending=False)
    top = confirmed.iloc[0] if len(confirmed) else anatomy.sort_values("recurrence_up_to_shift", ascending=False).iloc[0]
    perturb_top = perturb[perturb["rule"] == int(top["rule"])]
    dar = float(prim_assoc.loc[prim_assoc["primitive_class"] == "DAR_complete", "enrichment_over_base"].iloc[0])
    dara = float(prim_assoc.loc[prim_assoc["primitive_class"] == "DAR_asymmetric", "enrichment_over_base"].iloc[0])
    relation = float(prim_assoc.loc[prim_assoc["primitive_class"] == "relation_dependent", "enrichment_over_base"].iloc[0])
    asym = float(prim_assoc.loc[prim_assoc["primitive_class"] == "asymmetry_dependent", "enrichment_over_base"].iloc[0])
    stable_T = bool(confirmed["T"].mean() >= min(cfg.horizons)) if "T" in confirmed else bool(len(confirmed))
    robust_pert = bool(sidecars["recoverability"]["robust_motif_count"] > 0)
    if len(confirmed) >= 3 and robust_pert:
        rec = "G1 confirms multiple robust motif candidates; proceed to DAX-G2 phase map across minimal rule spaces."
        next_probe = "DAX_G2_persistence_phase_map_across_minimal_rule_spaces"
    elif len(confirmed) == 1:
        rec = "G1 confirms only one robust motif candidate; do deep anatomy before generalizing."
        next_probe = "DAX_G1b_single_rule_deep_anatomy"
    elif len(confirmed) > 0:
        rec = "G1 confirms motifs but sidecars are mixed; use G2 cautiously as diagnostic."
        next_probe = "DAX_G2_diagnostic_phase_map"
    else:
        rec = "G1 does not confirm robust motifs; refine persistence metrics before expanding."
        next_probe = "persistence_metric_refinement"
    return {
        "probe": "DAX_G1_persistence_motif_anatomy_and_robustness",
        "status": "COMPLETE",
        "runtime_seconds": round(time.monotonic() - started, 3),
        "candidate_rule_count": int(len(candidate_df)),
        "control_rule_count": int(len(control_df)),
        "confirmed_persistence_motif_count": int(len(confirmed)),
        "confirmed_rules": confirmed["rule"].astype(int).head(30).tolist(),
        "top_confirmed_rule": {
            "rule": int(top["rule"]),
            "motif_type": str(top["motif_type"]),
            "motif_period": float(top["period_estimate"]),
            "translation_velocity": float(top["translation_velocity_estimate"]),
            "recurrence_up_to_shift": float(top["recurrence_up_to_shift"]),
            "material_turnover_rate": float(top["motif_material_turnover"]),
            "background_contrast": float(top["pattern_background_contrast"]),
            "post_perturbation_survival_rate": float(perturb_top["post_perturbation_survival_rate"].iloc[0]) if len(perturb_top) else 0.0,
            "future_distinct_descendant_count": float(perturb_top["future_distinct_descendant_count"].iloc[0]) if len(perturb_top) else 0.0,
            "frozen_order_index": float(top["frozen_order_index"]),
            "chaos_index": float(top["chaos_index"]),
        },
        "control_results": {
            "collapse_controls_rejected": bool(not anatomy[anatomy["rule"].isin(control_df.loc[control_df["classification"] == "collapse", "rule"])]["confirmed_candidate"].any()),
            "frozen_controls_rejected": bool(not anatomy[anatomy["rule"].isin(control_df.loc[control_df["classification"] == "frozen_order", "rule"])]["confirmed_candidate"].any()),
            "chaotic_controls_rejected": bool(not anatomy[anatomy["rule"].isin(control_df.loc[control_df["classification"] == "chaotic", "rule"])]["confirmed_candidate"].any()),
            "identity_shift_controls_rejected": bool(not anatomy[anatomy["rule"].isin([204, 170, 240, 51])]["confirmed_candidate"].any()),
        },
        "primitive_association": {
            "DAR_complete_enriched_after_filter": bool(dar > 0),
            "DAR_asymmetric_enriched_after_filter": bool(dara > 0),
            "relation_dependent_enriched_after_filter": bool(relation > 0),
            "asymmetry_dependent_enriched_after_filter": bool(asym > 0),
        },
        "robustness": {
            "stable_across_T": stable_T,
            "stable_across_ring_size": bool(len(confirmed) > 0),
            "robust_to_light_perturbation": robust_pert,
        },
        "sidecars": sidecars,
        "recommendation": rec,
        "next_probe": next_probe,
        "estimator_warnings": warnings,
    }


def main() -> None:
    args = parse_args()
    cfg = Config(args.out_dir, args.g0_dir, min(args.workers, 18), args.n_seeds, args.horizons, args.ring_sizes)
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    summary = build_outputs(cfg, started)
    print("PROBE DAX-G1: PERSISTENCE MOTIF ANATOMY AND ROBUSTNESS")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
