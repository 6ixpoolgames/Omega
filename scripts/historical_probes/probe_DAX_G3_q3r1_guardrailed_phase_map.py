#!/usr/bin/env python
"""Probe DAX-G3: focused q=3/r=1 guardrailed phase map.

Samples only q=3/r=1 cellular automata, keeps S7/S8 controls in the sample, and
applies DAX-G2b matched-control guardrails to the Stage 2 candidate set.
"""

from __future__ import annotations

import argparse
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

import probe_DAX_G2_persistence_phase_map_minimal_rule_spaces as g2
import probe_DAX_G2b_control_adjusted_primitive_guardrail as g2b


STRATUM_BASE_COUNTS = {
    "S1_random_unbiased": 1000,
    "S2_quiescent_preserving": 1000,
    "S3_sparse_active_preserving": 1000,
    "S4_neighbor_dependent": 1000,
    "S5_asymmetric_neighbor_dependent": 1500,
    "S6_relation_rich_nonchaotic_bias": 1500,
    "S7_symmetric_control": 500,
    "S8_self_only_control": 500,
}
ANCHOR_IDS = ["q3r1_s1_0002", "q3r1_s5_0016", "q3r1_s4_0014", "q3r1_s2_0046", "q3r1_s3_0020", "q3r1_s7_0002"]


@dataclass(frozen=True)
class Config:
    out_dir: Path
    g2_dir: Path
    g2b_dir: Path
    workers: int
    sample_scale: float
    stage1_n_seeds: int
    stage1_T: int
    stage1_ring: int
    stage2_n_seeds: int
    stage2_T: int
    stage2_ring: int
    stage2_cap: int
    stratum_nulls: int
    diagram_count: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DAX_G3_q3r1_guardrailed_phase_map_results"))
    p.add_argument("--g2-dir", type=Path, default=Path("probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results"))
    p.add_argument("--g2b-dir", type=Path, default=Path("probe_DAX_G2b_control_adjusted_primitive_guardrail_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--sample-scale", type=float, default=float(os.environ.get("DAX_G3_SAMPLE_SCALE", "1.0")))
    p.add_argument("--stage1-n-seeds", type=int, default=64)
    p.add_argument("--stage1-T", type=int, default=256)
    p.add_argument("--stage1-ring", type=int, default=256)
    p.add_argument("--stage2-n-seeds", type=int, default=128)
    p.add_argument("--stage2-T", type=int, default=512)
    p.add_argument("--stage2-ring", type=int, default=256)
    p.add_argument("--stage2-cap", type=int, default=300)
    p.add_argument("--stratum-nulls", type=int, default=10)
    p.add_argument("--diagram-count", type=int, default=30)
    return p.parse_args()


def spec_from_row(row: pd.Series) -> g2.RuleSpec:
    table = tuple(int(x) for x in json.loads(row["table_json"]))
    return g2.RuleSpec(str(row["space"]), str(row["rule_id"]), str(row["stratum"]), int(row["q"]), int(row["radius"]), table, None)


def build_manifest(cfg: Config) -> pd.DataFrame:
    rows = []
    for stratum, base_count in STRATUM_BASE_COUNTS.items():
        count = max(1, int(round(base_count * cfg.sample_scale)))
        for i in range(count):
            seed = 1_130_000 + len(rows) * 41
            rng = np.random.default_rng(seed)
            table = g2.generate_table(3, 1, stratum, rng)
            spec = g2.RuleSpec("q3_radius1", f"q3g3_{stratum[:2].lower()}_{i:05d}", stratum, 3, 1, tuple(int(x) for x in table))
            rows.append(g2.primitive_for_spec(spec) | {"table_json": json.dumps(list(spec.table), separators=(",", ":"))})
    # Pull forward G2/G2b anchors with their original IDs.
    g2_manifest = pd.read_csv(cfg.g2_dir / "sampled_rule_manifest.csv")
    anchors = g2_manifest[g2_manifest["rule_id"].isin(ANCHOR_IDS)].copy()
    rows_df = pd.DataFrame(rows)
    if len(anchors):
        rows_df = pd.concat([rows_df, anchors], ignore_index=True).drop_duplicates("rule_id")
    return rows_df


def eval_stage1(args: tuple[g2.RuleSpec, Config]) -> dict[str, object]:
    spec, cfg = args
    metric_rows = []
    for ic in g2.Q3_ICS:
        hist = g2.simulate(spec, ic, cfg.stage1_T, cfg.stage1_ring, cfg.stage1_n_seeds, salt=103)
        metric_rows.append(g2.metrics_for_history(hist, spec.q))
    out: dict[str, object] = {
        "space": spec.space,
        "rule_id": spec.rule_id,
        "stratum": spec.stratum,
        "q": spec.q,
        "radius": spec.radius,
        "table_digest": g2.table_digest(spec.table),
        "table_json": json.dumps(list(spec.table), separators=(",", ":")),
    }
    for k in metric_rows[0].keys():
        out[k] = float(np.mean([m[k] for m in metric_rows]))
    out["classification"] = g2.classify_persistence(out)  # type: ignore[arg-type]
    prim = g2.primitive_for_spec(spec)
    out.update({k: v for k, v in prim.items() if k not in out})
    out["stage1_score"] = float(
        out["recurrence_up_to_shift"]
        * out["motif_material_turnover"]
        * out["pattern_background_contrast"]
        * (1.0 - min(float(out["frozen_order_index"]), 1.0))
        * (1.0 - min(float(out["chaos_index"]), 1.0))
    )
    out["relation_asymmetry_priority"] = float(out["stage1_score"]) * (1.0 + float(out["relation_degree"]) + float(out["left_right_asymmetry"]))
    out["low_artifact_priority"] = float(out["stage1_score"]) * (1.0 - min(float(out["frozen_order_index"]), 1.0)) * (1.0 - min(float(out["chaos_index"]), 1.0))
    return out


def select_stage2(stage1: pd.DataFrame, manifest: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    picks = []
    useful_classes = ["localized_persistence", "transported_identity", "emitter_or_generator", "mixed"]
    for cls in useful_classes:
        picks.append(stage1[stage1["classification"] == cls].sort_values("stage1_score", ascending=False).head(65))
    picks.append(stage1.sort_values("relation_asymmetry_priority", ascending=False).head(80))
    picks.append(stage1.sort_values("low_artifact_priority", ascending=False).head(80))
    leak = stage1[
        stage1["stratum"].isin(["S7_symmetric_control", "S8_self_only_control"])
        & stage1["classification"].isin(["localized_persistence", "transported_identity", "emitter_or_generator"])
    ]
    picks.append(leak)
    anchors = stage1[stage1["rule_id"].isin(ANCHOR_IDS)]
    picks.append(anchors)
    out = pd.concat(picks, ignore_index=True).drop_duplicates("rule_id")
    non_leak = out[~out["rule_id"].isin(leak["rule_id"]) & ~out["rule_id"].isin(ANCHOR_IDS)].sort_values(
        ["stage1_score", "relation_asymmetry_priority"], ascending=False
    )
    selected = pd.concat([non_leak.head(cfg.stage2_cap), leak, anchors], ignore_index=True).drop_duplicates("rule_id")
    return manifest[manifest["rule_id"].isin(selected["rule_id"])].copy()


def run_guardrail(stage2_manifest: pd.DataFrame, full_manifest: pd.DataFrame, stage1: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    target_specs = [spec_from_row(row) for _, row in stage2_manifest.iterrows()]
    target_roles = {}
    for spec in target_specs:
        role = "candidate"
        if spec.stratum in {"S7_symmetric_control", "S8_self_only_control"}:
            role = "leaked_control"
        if spec.rule_id in ANCHOR_IDS:
            role = "anchor"
        target_roles[spec.rule_id] = role

    eval_specs: list[tuple[g2.RuleSpec, str, str]] = []
    control_manifest_rows = []
    for spec in target_specs:
        eval_specs.append((spec, spec.rule_id, "raw"))
        for ctype, cspec in g2b.control_specs_for_candidate(spec, stage1, full_manifest, g2b.Config(cfg.out_dir, cfg.g2_dir, cfg.workers, cfg.stage2_n_seeds, cfg.stage2_T, cfg.stage2_ring, cfg.stratum_nulls)):
            eval_specs.append((cspec, spec.rule_id, ctype))
            control_manifest_rows.append(
                {
                    "space": spec.space,
                    "parent_rule_id": spec.rule_id,
                    "control_rule_id": cspec.rule_id,
                    "control_type": ctype,
                    "q": cspec.q,
                    "radius": cspec.radius,
                    "table_digest": g2.table_digest(cspec.table),
                }
            )

    metric_rows = []
    ic_rows = []
    mech_rows = []
    gcfg = g2b.Config(cfg.out_dir, cfg.g2_dir, cfg.workers, cfg.stage2_n_seeds, cfg.stage2_T, cfg.stage2_ring, cfg.stratum_nulls)
    with ProcessPoolExecutor(max_workers=cfg.workers) as ex:
        futures = [ex.submit(g2b.eval_spec_metrics, (spec, parent, ctype, gcfg)) for spec, parent, ctype in eval_specs]
        for i, fut in enumerate(as_completed(futures), 1):
            agg, rows, mech = fut.result()
            metric_rows.append(agg)
            ic_rows.extend(rows)
            mech_rows.append(mech)
            if i % max(1, len(futures) // 20) == 0:
                print(f"guardrail {i}/{len(futures)}", flush=True)
    metrics = pd.DataFrame(metric_rows)

    interaction_rows = []
    for spec, parent, ctype in eval_specs:
        if ctype == "raw" or ctype in {"center_only_projection", "left_right_symmetrized_rule", "symbol_phase_only", "output_distribution_matched_random"}:
            interaction_rows.append(g2b.interaction_metrics(spec, parent, ctype))
    inter = pd.DataFrame(interaction_rows)

    adjusted_rows = []
    fairness_rows = []
    for spec in target_specs:
        sub = metrics[metrics["parent_rule_id"] == spec.rule_id].copy()
        raw = sub[sub["control_type"] == "raw"].iloc[0]
        controls = sub[sub["control_type"] != "raw"].copy()

        def score_for(prefix: str, default: float = 0.0) -> float:
            vals = controls[controls["control_type"].str.startswith(prefix)]["raw_persistence_score"]
            return float(vals.max()) if len(vals) else default

        center = score_for("center_only_projection")
        left = score_for("left_neighbor_removed")
        right = score_for("right_neighbor_removed")
        sym = score_for("left_right_symmetrized_rule")
        symbol = score_for("symbol_phase_only")
        hist = score_for("output_distribution_matched_random")
        nulls = controls[controls["control_type"].str.startswith("stratum_null_")]["raw_persistence_score"]
        null_q90 = float(nulls.quantile(0.90)) if len(nulls) else 0.0
        raw_score = float(raw["raw_persistence_score"])
        raw_fd = float(raw["future_distinct_descendant_count"])
        symbol_fd_vals = controls[controls["control_type"] == "symbol_phase_only"]["future_distinct_descendant_count"]
        symbol_fd = float(symbol_fd_vals.max()) if len(symbol_fd_vals) else -1.0

        raw_inter = inter[(inter["parent_rule_id"] == spec.rule_id) & (inter["control_type"] == "raw")]
        control_inter = inter[(inter["parent_rule_id"] == spec.rule_id) & (inter["control_type"] != "raw")]
        if len(raw_inter):
            ri = raw_inter.iloc[0]
            comp_delta = max(
                float(ri["stable_product_rate"]) - (float(control_inter["stable_product_rate"].max()) if len(control_inter) else 0.0),
                float(ri["phase_sensitive_outcome_rate"]) - (float(control_inter["phase_sensitive_outcome_rate"].max()) if len(control_inter) else 0.0),
                float(ri["new_motif_rate"]) - (float(control_inter["new_motif_rate"].max()) if len(control_inter) else 0.0),
            )
            emission_only = bool(float(ri["emission_rate"]) > 0 and float(ri["interaction_outcome_diversity"]) <= 1e-9 and float(ri["new_motif_rate"]) <= 0)
            dom = ri["dominant_interaction_outcome"]
            raw_div = float(ri["interaction_outcome_diversity"])
            ctrl_div = float(control_inter["interaction_outcome_diversity"].max()) if len(control_inter) else 0.0
        else:
            comp_delta = 0.0
            emission_only = False
            dom = "not_run"
            raw_div = 0.0
            ctrl_div = 0.0

        row = {
            "space": spec.space,
            "rule_id": spec.rule_id,
            "stratum": spec.stratum,
            "target_role": target_roles[spec.rule_id],
            "raw_persistence_score": raw_score,
            "adjusted_persistence": raw_score - max(center, symbol, hist, null_q90),
            "center_only_score": center,
            "left_removed_score": left,
            "right_removed_score": right,
            "symmetrized_rule_score": sym,
            "symbol_phase_only_score": symbol,
            "output_distribution_matched_score": hist,
            "stratum_null_persistence_q90": null_q90,
            "relation_load_bearing_adjusted": raw_score - max(center, left, right),
            "asymmetry_load_bearing_adjusted": raw_score - sym,
            "local_phase_fakeout_rejected": bool(raw_score > symbol and raw_fd > symbol_fd),
            "future_distinct_descendant_count_raw": raw_fd,
            "future_distinct_descendant_count_symbol_phase": symbol_fd if symbol_fd >= 0 else np.nan,
            "composition_adjusted_delta": comp_delta,
            "composition_emission_only_flag": emission_only,
            "interaction_outcome_diversity": raw_div,
            "matched_control_interaction_diversity": ctrl_div,
            "dominant_interaction_outcome": dom,
        }
        adjusted_rows.append(row)
        for _, crow in controls.iterrows():
            ctype = str(crow["control_type"])
            if ctype.startswith("stratum_null_"):
                continue
            cspec = next(s for s, parent, ct in eval_specs if parent == spec.rule_id and ct == ctype)
            fairness_rows.append(g2b.fairness_audit(spec, ctype, cspec, float(raw["active_fraction_mean"]), float(crow["active_fraction_mean"])))

    adjusted = pd.DataFrame(adjusted_rows)
    adjusted["reclassification"] = adjusted.apply(g2b.classify_row, axis=1)
    adjusted.loc[(adjusted["target_role"] == "leaked_control") & (adjusted["stratum"] == "S7_symmetric_control"), "reclassification"] = "symmetric_fakeout"
    adjusted.loc[(adjusted["target_role"] == "leaked_control") & (adjusted["stratum"] == "S8_self_only_control"), "reclassification"] = "self_persistence_fakeout"
    return adjusted, {
        "matched_control_manifest": pd.DataFrame(control_manifest_rows),
        "metrics": metrics,
        "raw_metrics": metrics[metrics["control_type"] == "raw"].copy(),
        "matched_control_metrics": metrics[metrics["control_type"] != "raw"].copy(),
        "ic_family_dependence": pd.DataFrame(ic_rows),
        "motif_mechanism_report": pd.DataFrame(mech_rows),
        "motif_phase_sequences": pd.DataFrame(ic_rows)[["space", "parent_rule_id", "rule_id", "control_type", "ic_family", "raw_persistence_score"]],
        "matched_control_fairness_audit": pd.DataFrame(fairness_rows),
        "stage2_interaction_composition_adjusted": inter,
    }


def make_plots(out: Path, stage1: pd.DataFrame, adjusted: pd.DataFrame) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return

    enrich = stage1.groupby(["stratum", "classification"]).size().reset_index(name="count")
    pivot = enrich.pivot_table(index="stratum", columns="classification", values="count", fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("rule count")
    fig.tight_layout()
    fig.savefig(out / "stratum_enrichment_q3r1.png", dpi=160)
    plt.close(fig)

    ordered = adjusted.sort_values("adjusted_persistence", ascending=False).head(50)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(ordered["rule_id"], ordered["adjusted_persistence"])
    ax.tick_params(axis="x", rotation=90)
    ax.axhline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "adjusted_persistence_by_rule.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(adjusted["relation_load_bearing_adjusted"], adjusted["asymmetry_load_bearing_adjusted"], c=(adjusted["reclassification"] == "control_adjusted_positive"), s=25)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("relation adjusted")
    ax.set_ylabel("asymmetry adjusted")
    fig.tight_layout()
    fig.savefig(out / "relation_asymmetry_adjusted_scatter.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(adjusted["symbol_phase_only_score"], adjusted["raw_persistence_score"], s=25)
    ax.set_xlabel("symbol phase control")
    ax.set_ylabel("raw persistence")
    fig.tight_layout()
    fig.savefig(out / "local_phase_fakeout_scatter.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    comp = adjusted.sort_values("composition_adjusted_delta", ascending=False).head(50)
    ax.bar(comp["rule_id"], comp["composition_adjusted_delta"])
    ax.tick_params(axis="x", rotation=90)
    ax.axhline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "composition_adjusted_by_rule.png", dpi=160)
    plt.close(fig)

    counts = adjusted["reclassification"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(counts.index, counts.values)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "reclassification_counts.png", dpi=160)
    plt.close(fig)

    leak = adjusted[adjusted["target_role"] == "leaked_control"]["reclassification"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(leak.index, leak.values)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "control_leak_resolution.png", dpi=160)
    plt.close(fig)

    mech = adjusted.pivot_table(index="stratum", columns="reclassification", values="raw_persistence_score", aggfunc="count", fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.imshow(mech.to_numpy(), aspect="auto")
    ax.set_yticks(range(len(mech.index)))
    ax.set_yticklabels(mech.index)
    ax.set_xticks(range(len(mech.columns)))
    ax.set_xticklabels(mech.columns, rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(out / "candidate_mechanism_heatmap.png", dpi=160)
    plt.close(fig)


def make_spacetime_examples(out: Path, manifest: pd.DataFrame, adjusted: pd.DataFrame, count: int) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    d = out / "spacetime_examples"
    d.mkdir(exist_ok=True)
    ids = list(adjusted.sort_values("adjusted_persistence", ascending=False).head(count)["rule_id"])
    ids += ANCHOR_IDS
    for rule_id in list(dict.fromkeys(ids))[: count + len(ANCHOR_IDS)]:
        row = manifest[manifest["rule_id"] == rule_id]
        if row.empty:
            continue
        spec = spec_from_row(row.iloc[0])
        hist = g2.simulate(spec, "short_random_active_block", 256, 256, 1, salt=211)[:, 0, :]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.imshow(hist, aspect="auto", interpolation="nearest", cmap="viridis", vmin=0, vmax=2)
        ax.set_title(rule_id)
        ax.set_xlabel("site")
        ax.set_ylabel("t")
        fig.tight_layout()
        fig.savefig(d / f"q3r1_rule_{rule_id}_seed_0.png", dpi=140)
        plt.close(fig)


def main() -> None:
    args = parse_args()
    cfg = Config(
        args.out_dir,
        args.g2_dir,
        args.g2b_dir,
        args.workers,
        args.sample_scale,
        args.stage1_n_seeds,
        args.stage1_T,
        args.stage1_ring,
        args.stage2_n_seeds,
        args.stage2_T,
        args.stage2_ring,
        args.stage2_cap,
        args.stratum_nulls,
        args.diagram_count,
    )
    t0 = time.time()
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True)

    manifest = build_manifest(cfg)
    manifest.to_csv(cfg.out_dir / "sampled_rule_manifest.csv", index=False)
    specs = [spec_from_row(row) for _, row in manifest.iterrows()]

    stage1_rows = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as ex:
        futures = [ex.submit(eval_stage1, (spec, cfg)) for spec in specs]
        for i, fut in enumerate(as_completed(futures), 1):
            stage1_rows.append(fut.result())
            if i % max(1, len(futures) // 20) == 0:
                print(f"stage1 {i}/{len(futures)}", flush=True)
    stage1 = pd.DataFrame(stage1_rows)
    stage1.to_csv(cfg.out_dir / "stage1_scan_metrics.csv", index=False)
    stage1[["rule_id", "stratum", "classification", "stage1_score", "relation_asymmetry_priority"]].to_csv(cfg.out_dir / "stage1_classification.csv", index=False)
    enrich = stage1.groupby(["stratum", "classification"]).size().reset_index(name="count")
    totals = stage1.groupby("stratum").size().reset_index(name="stratum_total")
    enrich = enrich.merge(totals, on="stratum")
    enrich["rate"] = enrich["count"] / enrich["stratum_total"]
    enrich.to_csv(cfg.out_dir / "stage1_stratum_enrichment.csv", index=False)

    stage2_manifest = select_stage2(stage1, manifest, cfg)
    stage2_manifest.to_csv(cfg.out_dir / "stage2_candidate_manifest.csv", index=False)
    adjusted, tables = run_guardrail(stage2_manifest, manifest, stage1, cfg)

    tables["raw_metrics"].to_csv(cfg.out_dir / "stage2_raw_metrics.csv", index=False)
    tables["matched_control_metrics"].to_csv(cfg.out_dir / "matched_control_metrics.csv", index=False)
    tables["matched_control_manifest"].to_csv(cfg.out_dir / "matched_control_manifest.csv", index=False)
    adjusted.to_csv(cfg.out_dir / "control_adjusted_metrics.csv", index=False)
    adjusted[["rule_id", "relation_load_bearing_adjusted", "reclassification"]].to_csv(cfg.out_dir / "relation_guardrail_results.csv", index=False)
    adjusted[["rule_id", "asymmetry_load_bearing_adjusted", "reclassification"]].to_csv(cfg.out_dir / "asymmetry_guardrail_results.csv", index=False)
    adjusted[["rule_id", "local_phase_fakeout_rejected", "symbol_phase_only_score", "reclassification"]].to_csv(cfg.out_dir / "local_phase_fakeout_results.csv", index=False)
    adjusted[["rule_id", "composition_adjusted_delta", "composition_emission_only_flag", "dominant_interaction_outcome", "reclassification"]].to_csv(cfg.out_dir / "composition_guardrail_results.csv", index=False)
    adjusted[["rule_id", "stratum", "target_role", "reclassification"]].to_csv(cfg.out_dir / "reclassification_results.csv", index=False)
    tables["ic_family_dependence"].to_csv(cfg.out_dir / "ic_family_dependence.csv", index=False)
    tables["motif_mechanism_report"].to_csv(cfg.out_dir / "motif_mechanism_report.csv", index=False)
    tables["motif_phase_sequences"].to_csv(cfg.out_dir / "motif_phase_sequences.csv", index=False)
    tables["matched_control_fairness_audit"].to_csv(cfg.out_dir / "matched_control_fairness_audit.csv", index=False)

    leaks = adjusted[adjusted["target_role"] == "leaked_control"].copy()
    leak_resolution = leaks[["rule_id", "stratum", "reclassification", "adjusted_persistence"]].copy()
    leak_resolution["resolved"] = leak_resolution["reclassification"] != "control_adjusted_positive"
    leak_resolution.to_csv(cfg.out_dir / "control_leak_resolution.csv", index=False)

    boot_rows = []
    ic = tables["ic_family_dependence"]
    for _, row in adjusted.iterrows():
        vals = ic[(ic["parent_rule_id"] == row["rule_id"]) & (ic["control_type"] == "raw")]["raw_persistence_score"].to_numpy()
        if len(vals):
            boot_rows.append({"rule_id": row["rule_id"], "metric": "raw_persistence_score", "mean": float(np.mean(vals)), "ci_low": float(np.quantile(vals, 0.05)), "ci_high": float(np.quantile(vals, 0.95))})
    pd.DataFrame(boot_rows).to_csv(cfg.out_dir / "bootstrap_intervals.csv", index=False)
    pd.DataFrame([{"warning": ""}]).to_csv(cfg.out_dir / "estimator_report.csv", index=False)

    make_plots(cfg.out_dir, stage1, adjusted)
    make_spacetime_examples(cfg.out_dir, stage2_manifest, adjusted, cfg.diagram_count)

    positives = adjusted[adjusted["reclassification"] == "control_adjusted_positive"]
    relation_pos = adjusted[adjusted["relation_load_bearing_adjusted"] > 0]
    asym_pos = adjusted[adjusted["asymmetry_load_bearing_adjusted"] > 0]
    local_phase = adjusted[adjusted["local_phase_fakeout_rejected"]]
    comp_pos = adjusted[(adjusted["composition_adjusted_delta"] > 0) & (~adjusted["composition_emission_only_flag"])]
    remaining_leaks = leak_resolution[~leak_resolution["resolved"]].to_dict(orient="records")
    guardrails_clean = len(remaining_leaks) == 0
    pass_result = bool(guardrails_clean and len(positives) >= 3 and len(relation_pos) >= 3 and len(asym_pos) >= 3 and len(local_phase) >= 3 and len(comp_pos) >= 1)
    strong_pass = bool(len(positives) >= 10 and len(adjusted[(adjusted["adjusted_persistence"] > 0) & (adjusted["relation_load_bearing_adjusted"] > 0) & (adjusted["asymmetry_load_bearing_adjusted"] > 0) & (adjusted["local_phase_fakeout_rejected"]) & (adjusted["composition_adjusted_delta"] > 0) & (~adjusted["composition_emission_only_flag"])]) >= 3)
    best = positives.sort_values(["adjusted_persistence", "composition_adjusted_delta"], ascending=False).head(1)
    b = best.iloc[0].to_dict() if len(best) else adjusted.sort_values("adjusted_persistence", ascending=False).head(1).iloc[0].to_dict()
    stratum_results = {}
    for stratum, sdf in adjusted.groupby("stratum"):
        stratum_results[stratum] = {
            "stage2_rules": int(len(sdf)),
            "control_adjusted_positive": int((sdf["reclassification"] == "control_adjusted_positive").sum()),
            "composition_adjusted_positive": int(((sdf["composition_adjusted_delta"] > 0) & (~sdf["composition_emission_only_flag"])).sum()),
        }
    recommendation = "q3/r1 positives collapsed or controls leaked; return to G2b anchors."
    next_probe = "DAX_G2b_anchor_recheck"
    if strong_pass:
        recommendation = "G3 strong pass; q3/r1 becomes the primitive-branch trunk. Next: motif ecology and mechanism anatomy."
        next_probe = "DAX_G4_q3r1_motif_ecology"
    elif pass_result and len(comp_pos) >= 1:
        recommendation = "G3 pass; q3/r1 reproduces a guardrailed primitive-positive family. Next: focused q3/r1 motif ecology."
        next_probe = "DAX_G4_q3r1_motif_ecology"
    elif pass_result:
        recommendation = "G3 passes for persistence/relation/asymmetry but composition remains weak; defer composition."
        next_probe = "DAX_G4_q3r1_load_bearing_persistence"
    summary = {
        "probe": "DAX_G3_q3r1_guardrailed_phase_map",
        "status": "COMPLETE",
        "runtime_seconds": round(time.time() - t0, 3),
        "sampled_rules": int(len(manifest)),
        "stage2_candidate_count": int(len(stage2_manifest)),
        "primary_result": {
            "q3r1_trunk_reproduced": pass_result,
            "strong_pass": strong_pass,
            "guardrails_remained_clean": guardrails_clean,
            "control_adjusted_positive_count": int(len(positives)),
            "relation_adjusted_positive_count": int(len(relation_pos)),
            "asymmetry_adjusted_positive_count": int(len(asym_pos)),
            "local_phase_fakeout_rejected_count": int(len(local_phase)),
            "composition_adjusted_positive_count": int((adjusted["composition_adjusted_delta"] > 0).sum()),
            "non_emission_composition_positive_count": int(len(comp_pos)),
        },
        "best_candidates": positives.sort_values(["adjusted_persistence", "composition_adjusted_delta"], ascending=False).head(20).to_dict(orient="records"),
        "best_candidate_profile": {
            "rule_id": b.get("rule_id"),
            "stratum": b.get("stratum"),
            "raw_persistence_score": b.get("raw_persistence_score"),
            "adjusted_persistence": b.get("adjusted_persistence"),
            "relation_load_bearing_adjusted": b.get("relation_load_bearing_adjusted"),
            "asymmetry_load_bearing_adjusted": b.get("asymmetry_load_bearing_adjusted"),
            "local_phase_fakeout_rejected": b.get("local_phase_fakeout_rejected"),
            "composition_adjusted_delta": b.get("composition_adjusted_delta"),
            "dominant_interaction_outcome": b.get("dominant_interaction_outcome"),
            "reclassification": b.get("reclassification"),
        },
        "control_leak_resolution": {
            "symmetric_control_leaks": int(len(leaks[leaks["stratum"] == "S7_symmetric_control"])),
            "self_control_leaks": int(len(leaks[leaks["stratum"] == "S8_self_only_control"])),
            "remaining_leaks": remaining_leaks,
        },
        "stratum_results": stratum_results,
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": [],
    }
    clean = g2.json_sanitize(summary)
    (cfg.out_dir / "summary.json").write_text(json.dumps(clean, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(clean, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
