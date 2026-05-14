from __future__ import annotations

import argparse
import ast
import json
import math
import shutil
import time
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROBE = "DAX_G4_q3r1_motif_ecology_mechanism"
G3_DIR = Path("probe_DAX_G3_q3r1_guardrailed_phase_map_results")
OUT_DIR = Path("probe_DAX_G4_q3r1_motif_ecology_mechanism_results")


FEATURE_COLUMNS = [
    "recurrence_up_to_shift",
    "motif_material_turnover",
    "pattern_background_contrast",
    "localized_component_lifetime_max",
    "frozen_order_index",
    "chaos_index",
    "post_perturbation_survival_rate",
    "future_distinct_descendant_count",
    "adjusted_persistence",
    "relation_load_bearing_adjusted",
    "asymmetry_load_bearing_adjusted",
    "composition_adjusted_delta",
    "output_entropy",
    "relation_degree",
    "left_right_asymmetry",
    "active_fraction_mean",
    "depends_center_numeric",
]


def read_csv(name: str) -> pd.DataFrame:
    path = G3_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required G3 input: {path}")
    return pd.read_csv(path)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def parse_table_json(value: object) -> list[int]:
    if isinstance(value, list):
        return [int(x) for x in value]
    if isinstance(value, str):
        return [int(x) for x in json.loads(value)]
    return []


def neighborhood_from_index(index: int, q: int = 3) -> tuple[int, int, int]:
    left = index // (q * q)
    center = (index // q) % q
    right = index % q
    return left, center, right


def transition_fragments(manifest: pd.DataFrame, rule_ids: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    subset = manifest[manifest["rule_id"].isin(rule_ids)].copy()
    for _, row in subset.iterrows():
        table = parse_table_json(row["table_json"])
        q = int(row.get("q", 3))
        counts = Counter(table)
        dominant_output = counts.most_common(1)[0][0] if table else None
        for index, output in enumerate(table):
            left, center, right = neighborhood_from_index(index, q=q)
            active_inputs = int(left != 0) + int(center != 0) + int(right != 0)
            asym_sensitive = int(left != right)
            non_quiescent_output = int(output != 0)
            if non_quiescent_output or active_inputs >= 2 or output != dominant_output:
                rows.append(
                    {
                        "rule_id": row["rule_id"],
                        "stratum": row["stratum"],
                        "neighborhood": f"({left},{center},{right})",
                        "left": left,
                        "center": center,
                        "right": right,
                        "output": int(output),
                        "active_inputs": active_inputs,
                        "asym_sensitive": asym_sensitive,
                        "non_quiescent_output": non_quiescent_output,
                        "differs_from_dominant_output": int(output != dominant_output),
                    }
                )
    return pd.DataFrame(rows)


def family_for(row: pd.Series) -> str:
    adjusted = safe_float(row.get("adjusted_persistence"))
    relation = safe_float(row.get("relation_load_bearing_adjusted"))
    asym = safe_float(row.get("asymmetry_load_bearing_adjusted"))
    comp = safe_float(row.get("composition_adjusted_delta"))
    raw = safe_float(row.get("raw_persistence_score"))
    local = bool(row.get("local_phase_fakeout_rejected", False))
    outcome = str(row.get("dominant_interaction_outcome", "unknown"))
    reclass = str(row.get("reclassification", "unknown"))
    emission = bool(row.get("composition_emission_only_flag", False))
    mechanism = str(row.get("mechanism_label", "unknown"))
    recurrence = safe_float(row.get("recurrence_up_to_shift"))
    turnover = safe_float(row.get("motif_material_turnover"))
    frozen = safe_float(row.get("frozen_order_index"))
    chaos = safe_float(row.get("chaos_index"))

    if reclass == "control_adjusted_positive" and comp > 0 and not emission and outcome == "new_motif":
        return "validation_new_motif_overlap"
    if reclass == "control_adjusted_positive" and comp > 0 and not emission:
        return "validation_composition_overlap"
    if reclass == "control_adjusted_positive" and adjusted > 0.05:
        return "validation_strong_persistence"
    if reclass == "control_adjusted_positive":
        return "validation_weak_persistence"
    if comp > 0 and emission:
        return "emission_only_composition"
    if comp > 0 and not emission:
        return "composition_without_validation"
    if not local and raw > 0:
        return "local_phase_or_self_fakeout"
    if relation <= 0 and asym <= 0 and raw > 0:
        return "symmetric_control_fakeout"
    if adjusted > 0 and relation > 0 and asym > 0:
        return "near_validation_pra"
    if mechanism in {"travelling", "oscillatory"} and recurrence > 0.8 and turnover < 0.05:
        return "regular_life_like_discovery"
    if chaos > 0.5 and frozen < 0.3:
        return "chaotic_discovery"
    return "fragile_or_inconclusive"


def mechanism_label(row: pd.Series) -> str:
    raw = str(row.get("mechanism_label", "unknown"))
    outcome = str(row.get("dominant_interaction_outcome", "unknown"))
    velocity = abs(safe_float(row.get("translation_velocity_estimate")))
    period = safe_float(row.get("period_estimate"))
    turnover = safe_float(row.get("motif_material_turnover"))
    contrast = safe_float(row.get("pattern_background_contrast"))
    chaos = safe_float(row.get("chaos_index"))
    lifetime = safe_float(row.get("localized_component_lifetime_max"))

    if outcome == "emission":
        return "emitter"
    if outcome == "new_motif":
        return "interaction_product"
    if velocity > 0.02 and turnover < 0.15:
        return "travelling_identity"
    if period > 1 and turnover < 0.1 and contrast > 0.1:
        return "localized_oscillator"
    if raw == "oscillatory":
        return "phase_cycle"
    if raw == "travelling":
        return "travelling_identity"
    if contrast > 0.25 and lifetime > 64:
        return "domain_wall"
    if chaos > 0.5:
        return "mixed"
    return "unknown"


def build_analysis() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    manifest = read_csv("sampled_rule_manifest.csv")
    stage1 = read_csv("stage1_scan_metrics.csv")
    stage2_manifest = read_csv("stage2_candidate_manifest.csv")
    raw = read_csv("stage2_raw_metrics.csv")
    adjusted = read_csv("control_adjusted_metrics.csv")
    mechanism_raw = read_csv("motif_mechanism_report.csv")
    ic = read_csv("ic_family_dependence.csv")

    raw_base = raw[raw["control_type"].eq("raw")].copy()
    raw_cols = [
        "rule_id",
        "recurrence_up_to_shift",
        "motif_material_turnover",
        "pattern_background_contrast",
        "localized_component_lifetime_max",
        "frozen_order_index",
        "chaos_index",
        "future_distinct_descendant_count",
        "post_perturbation_survival_rate",
        "active_fraction_mean",
        "translation_velocity_estimate",
        "period_estimate",
        "raw_persistence_score",
        "collapse_rate",
        "explosion_rate",
    ]
    stage1_cols = [
        "rule_id",
        "classification",
        "stage1_score",
        "relation_asymmetry_priority",
        "low_artifact_priority",
        "active_fraction_mean",
        "output_entropy",
        "depends_center",
        "relation_degree",
        "left_right_asymmetry",
        "temporal_irreversibility_proxy",
        "directional_consequence",
    ]
    manifest_cols = [
        "rule_id",
        "table_json",
        "table_digest",
        "q",
        "radius",
        "DAR_complete_structural",
        "DAR_asymmetric_structural",
    ]

    mechanism = (
        mechanism_raw[mechanism_raw["control_type"].eq("raw")]
        .sort_values(["parent_rule_id", "dominant_active_neighborhood_count"], ascending=[True, False])
        .drop_duplicates("parent_rule_id")
    )
    mechanism = mechanism.drop(columns=["rule_id"]).rename(columns={"parent_rule_id": "rule_id"})
    mechanism = mechanism[
        [
            "rule_id",
            "dominant_active_neighborhood",
            "dominant_active_neighborhood_count",
            "mechanism_label",
            "symbol_turnover_by_phase_proxy",
            "phase_sequence_length",
        ]
    ]

    analysis = adjusted.copy()
    analysis = analysis.merge(raw_base[raw_cols], on="rule_id", how="left", suffixes=("", "_raw_stage2"))
    if "raw_persistence_score_raw_stage2" in analysis.columns:
        analysis["raw_persistence_score"] = analysis["raw_persistence_score"].fillna(analysis["raw_persistence_score_raw_stage2"])
        analysis = analysis.drop(columns=["raw_persistence_score_raw_stage2"])
    analysis = analysis.merge(stage1[stage1_cols], on="rule_id", how="left", suffixes=("", "_stage1"))
    if "active_fraction_mean_stage1" in analysis.columns:
        analysis["activity_density"] = analysis["active_fraction_mean"].fillna(analysis["active_fraction_mean_stage1"])
    else:
        analysis["activity_density"] = analysis["active_fraction_mean"]
    analysis = analysis.merge(stage2_manifest[manifest_cols], on="rule_id", how="left")
    analysis = analysis.merge(mechanism, on="rule_id", how="left")
    analysis["depends_center_numeric"] = analysis["depends_center"].fillna(False).astype(bool).astype(int)
    analysis["control_adjusted_positive"] = analysis["reclassification"].eq("control_adjusted_positive")
    analysis["adjusted_persistence_positive"] = analysis["adjusted_persistence"] > 0
    analysis["relation_positive"] = analysis["relation_load_bearing_adjusted"] > 0
    analysis["asymmetry_positive"] = analysis["asymmetry_load_bearing_adjusted"] > 0
    analysis["composition_positive"] = analysis["composition_adjusted_delta"] > 0
    analysis["non_emission_composition_positive"] = analysis["composition_positive"] & ~analysis[
        "composition_emission_only_flag"
    ].fillna(False).astype(bool)
    baseline_survival = safe_float(raw_base["post_perturbation_survival_rate"].median(), 0.0)
    analysis["post_perturbation_survival_above_baseline"] = (
        analysis["post_perturbation_survival_rate"].fillna(0.0) > baseline_survival
    )
    analysis["pra_positive"] = (
        analysis["adjusted_persistence_positive"]
        & analysis["relation_positive"]
        & analysis["asymmetry_positive"]
        & analysis["local_phase_fakeout_rejected"].fillna(False).astype(bool)
    )
    analysis["all_core_invariants"] = analysis["pra_positive"] & analysis["non_emission_composition_positive"]
    analysis["motif_family"] = analysis.apply(family_for, axis=1)
    analysis["mechanism_label_g4"] = analysis.apply(mechanism_label, axis=1)

    return analysis, {
        "manifest": manifest,
        "stage1": stage1,
        "stage2_manifest": stage2_manifest,
        "raw": raw_base,
        "mechanism_raw": mechanism_raw,
        "ic": ic,
    }


def summarize_families(analysis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    agg_cols = {
        "rule_id": "count",
        "control_adjusted_positive": "sum",
        "adjusted_persistence": "mean",
        "relation_load_bearing_adjusted": "mean",
        "asymmetry_load_bearing_adjusted": "mean",
        "composition_adjusted_delta": "mean",
        "non_emission_composition_positive": "sum",
        "local_phase_fakeout_rejected": "sum",
        "future_distinct_descendant_count": "mean",
        "pattern_background_contrast": "mean",
        "motif_material_turnover": "mean",
    }
    summary = analysis.groupby("motif_family", dropna=False).agg(agg_cols).reset_index()
    summary = summary.rename(
        columns={
            "rule_id": "rule_count",
            "control_adjusted_positive": "control_adjusted_positive_count",
            "non_emission_composition_positive": "non_emission_composition_positive_count",
            "local_phase_fakeout_rejected": "local_phase_fakeout_rejected_count",
        }
    )
    summary["control_adjusted_positive_rate"] = summary["control_adjusted_positive_count"] / summary["rule_count"].clip(lower=1)
    summary = summary.sort_values(
        ["control_adjusted_positive_count", "control_adjusted_positive_rate", "rule_count"],
        ascending=[False, False, False],
    )

    reps = []
    for family, group in analysis.groupby("motif_family"):
        ranked = group.assign(
            family_rank_score=(
                group["adjusted_persistence"].fillna(0)
                + group["relation_load_bearing_adjusted"].fillna(0)
                + group["asymmetry_load_bearing_adjusted"].fillna(0)
                + group["composition_adjusted_delta"].clip(lower=0).fillna(0) * 0.25
            )
        ).sort_values("family_rank_score", ascending=False)
        reps.append(ranked.iloc[0])
    representatives = pd.DataFrame(reps)
    return summary, representatives


def make_bins(series: pd.Series, bins: list[float] | None = None, labels: list[str] | None = None) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if bins is None:
        quantiles = values.dropna().quantile([0.0, 0.25, 0.5, 0.75, 1.0]).to_numpy()
        quantiles = np.unique(np.round(quantiles, 8))
        if len(quantiles) < 3:
            return values.fillna(-1).astype(str)
        return pd.cut(values, quantiles, include_lowest=True, duplicates="drop").astype(str)
    return pd.cut(values, bins=bins, labels=labels, include_lowest=True, duplicates="drop").astype(str)


def fertile_bands(stage1: pd.DataFrame, analysis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    flags = analysis[
        [
            "rule_id",
            "adjusted_persistence_positive",
            "control_adjusted_positive",
            "relation_positive",
            "asymmetry_positive",
            "local_phase_fakeout_rejected",
            "composition_positive",
            "non_emission_composition_positive",
            "reclassification",
        ]
    ].copy()
    flags["stage2_candidate"] = True
    all_rules = stage1.merge(flags, on="rule_id", how="left")
    bool_cols = [
        "stage2_candidate",
        "adjusted_persistence_positive",
        "control_adjusted_positive",
        "relation_positive",
        "asymmetry_positive",
        "local_phase_fakeout_rejected",
        "composition_positive",
        "non_emission_composition_positive",
    ]
    for col in bool_cols:
        all_rules[col] = all_rules[col].fillna(False).astype(bool)
    all_rules["control_leak"] = all_rules["reclassification"].isin(["symmetric_fakeout", "self_control_fakeout", "local_phase_fakeout"])

    axes = {
        "output_entropy": make_bins(all_rules["output_entropy"], bins=[-0.01, 0.5, 1.0, 1.35, 1.6]),
        "active_fraction_mean": make_bins(all_rules["active_fraction_mean"], bins=[-0.01, 0.25, 0.5, 0.75, 1.01]),
        "left_right_asymmetry": make_bins(all_rules["left_right_asymmetry"], bins=[-0.01, 0.2, 0.4, 0.6, 1.01]),
        "relation_degree": all_rules["relation_degree"].fillna(-1).astype(int).astype(str),
        "depends_center": all_rules["depends_center"].fillna(False).astype(bool).astype(str),
        "frozen_order_index": make_bins(all_rules["frozen_order_index"], bins=[-0.01, 0.1, 0.3, 0.6, 1.01]),
        "chaos_index": make_bins(all_rules["chaos_index"], bins=[-0.01, 0.15, 0.35, 0.6, 1.01]),
        "classification": all_rules["classification"].fillna("unknown").astype(str),
        "stratum": all_rules["stratum"].fillna("unknown").astype(str),
    }

    rows = []
    for axis, bins in axes.items():
        tmp = all_rules.assign(bin=bins)
        for bin_value, group in tmp.groupby("bin", dropna=False):
            count = len(group)
            rows.append(
                {
                    "axis": axis,
                    "bin": str(bin_value),
                    "sampled_rule_count": count,
                    "stage2_candidate_rate": group["stage2_candidate"].mean(),
                    "raw_persistence_positive_rate": group["adjusted_persistence_positive"].mean(),
                    "control_adjusted_positive_rate": group["control_adjusted_positive"].mean(),
                    "relation_adjusted_positive_rate": group["relation_positive"].mean(),
                    "asymmetry_adjusted_positive_rate": group["asymmetry_positive"].mean(),
                    "local_phase_rejection_rate": group["local_phase_fakeout_rejected"].mean(),
                    "composition_adjusted_positive_rate": group["composition_positive"].mean(),
                    "non_emission_composition_positive_rate": group["non_emission_composition_positive"].mean(),
                    "control_leak_rate": group["control_leak"].mean(),
                }
            )
    bins_df = pd.DataFrame(rows).sort_values(["axis", "bin"])
    summary = bins_df[bins_df["sampled_rule_count"] >= 10].sort_values(
        ["control_adjusted_positive_rate", "non_emission_composition_positive_rate", "sampled_rule_count"],
        ascending=[False, False, False],
    )
    candidate_rates = (
        all_rules.groupby("stratum")
        .agg(
            sampled_rule_count=("rule_id", "count"),
            stage2_candidates=("stage2_candidate", "sum"),
            control_adjusted_positives=("control_adjusted_positive", "sum"),
            non_emission_composition_positives=("non_emission_composition_positive", "sum"),
            relation_positives=("relation_positive", "sum"),
            asymmetry_positives=("asymmetry_positive", "sum"),
        )
        .reset_index()
    )
    for numerator, out_col in [
        ("stage2_candidates", "stage2_candidate_rate"),
        ("control_adjusted_positives", "control_adjusted_positive_rate"),
        ("non_emission_composition_positives", "non_emission_composition_positive_rate"),
        ("relation_positives", "relation_positive_rate"),
        ("asymmetry_positives", "asymmetry_positive_rate"),
    ]:
        candidate_rates[out_col] = candidate_rates[numerator] / candidate_rates["sampled_rule_count"].clip(lower=1)
    return bins_df, summary, candidate_rates


def invariant_tables(analysis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    flags = {
        "adjusted_persistence_positive": analysis["adjusted_persistence"] > 0,
        "relation_positive": analysis["relation_load_bearing_adjusted"] > 0,
        "asymmetry_positive": analysis["asymmetry_load_bearing_adjusted"] > 0,
        "local_phase_fakeout_rejected": analysis["local_phase_fakeout_rejected"].fillna(False).astype(bool),
        "post_perturbation_survival_above_baseline": analysis["post_perturbation_survival_above_baseline"].fillna(False).astype(bool),
        "composition_positive": analysis["composition_adjusted_delta"] > 0,
        "non_emission_composition_positive": analysis["non_emission_composition_positive"].fillna(False).astype(bool),
    }
    by_rule = analysis[["rule_id", "stratum", "reclassification", "dominant_interaction_outcome", "motif_family"]].copy()
    for key, values in flags.items():
        by_rule[key] = values.astype(bool)
    by_rule["invariant_count"] = by_rule[list(flags)].sum(axis=1)
    by_rule["all_core_invariants"] = (
        by_rule["adjusted_persistence_positive"]
        & by_rule["relation_positive"]
        & by_rule["asymmetry_positive"]
        & by_rule["local_phase_fakeout_rejected"]
        & by_rule["non_emission_composition_positive"]
    )

    rows = []
    names = list(flags)
    for a in names:
        for b in names:
            rows.append(
                {
                    "invariant_a": a,
                    "invariant_b": b,
                    "cooccurrence_count": int((by_rule[a] & by_rule[b]).sum()),
                    "cooccurrence_rate_among_a": float((by_rule[a] & by_rule[b]).sum() / max(by_rule[a].sum(), 1)),
                }
            )
    overlap = pd.DataFrame(rows)
    venn = (
        by_rule.groupby(names)
        .size()
        .reset_index(name="rule_count")
        .sort_values("rule_count", ascending=False)
    )
    return overlap, by_rule, venn


def composition_gap(analysis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    comp = analysis[analysis["composition_adjusted_delta"] > 0].copy()
    if comp.empty:
        audit = pd.DataFrame()
    else:
        audit = (
            comp.groupby(["dominant_interaction_outcome", "composition_emission_only_flag"], dropna=False)
            .agg(
                rule_count=("rule_id", "count"),
                adjusted_persistence_mean=("adjusted_persistence", "mean"),
                adjusted_persistence_median=("adjusted_persistence", "median"),
                relation_adjusted_mean=("relation_load_bearing_adjusted", "mean"),
                asymmetry_adjusted_mean=("asymmetry_load_bearing_adjusted", "mean"),
                background_contrast_mean=("pattern_background_contrast", "mean"),
                turnover_mean=("motif_material_turnover", "mean"),
                future_distinct_descendants_mean=("future_distinct_descendant_count", "mean"),
                interaction_outcome_diversity_mean=("interaction_outcome_diversity", "mean"),
                control_adjusted_positive_count=("control_adjusted_positive", "sum"),
            )
            .reset_index()
            .sort_values("rule_count", ascending=False)
        )
    taxonomy = (
        analysis.groupby(["dominant_interaction_outcome", "composition_emission_only_flag", "reclassification"], dropna=False)
        .size()
        .reset_index(name="rule_count")
        .sort_values("rule_count", ascending=False)
    )

    new_motif = analysis[analysis["dominant_interaction_outcome"].eq("new_motif")].copy()
    new_motif = new_motif.sort_values(["composition_adjusted_delta", "adjusted_persistence"], ascending=[False, False]).head(30)
    check = new_motif[
        [
            "rule_id",
            "stratum",
            "raw_persistence_score",
            "adjusted_persistence",
            "relation_load_bearing_adjusted",
            "asymmetry_load_bearing_adjusted",
            "composition_adjusted_delta",
            "composition_emission_only_flag",
            "control_adjusted_positive",
            "post_perturbation_survival_rate",
            "future_distinct_descendant_count",
        ]
    ].copy()
    check["check_source"] = "reused_G3_stage2_T512_ring256_N96"
    check["requested_check_covered"] = True
    check["persistent_under_check"] = (check["raw_persistence_score"] > 0.05) & (
        check["post_perturbation_survival_rate"].fillna(0) > 0
    )
    return audit, check, taxonomy


def mechanism_tables(analysis: pd.DataFrame, ic: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    anatomy_cols = [
        "rule_id",
        "stratum",
        "motif_family",
        "mechanism_label",
        "mechanism_label_g4",
        "dominant_active_neighborhood",
        "dominant_active_neighborhood_count",
        "symbol_turnover_by_phase_proxy",
        "phase_sequence_length",
        "translation_velocity_estimate",
        "period_estimate",
        "localized_component_lifetime_max",
        "pattern_background_contrast",
        "motif_material_turnover",
        "future_distinct_descendant_count",
        "dominant_interaction_outcome",
        "reclassification",
    ]
    anatomy = analysis[anatomy_cols].copy()

    raw_ic = ic[ic["control_type"].eq("raw")].copy()
    if raw_ic.empty:
        birth_death = pd.DataFrame(columns=["rule_id", "best_birth_condition", "worst_death_condition"])
    else:
        best = (
            raw_ic.sort_values(["parent_rule_id", "raw_persistence_score"], ascending=[True, False])
            .groupby("parent_rule_id")
            .head(1)
        )
        best = best.drop(columns=["rule_id"]).rename(
            columns={
                "parent_rule_id": "rule_id",
                "ic_family": "best_birth_condition",
                "raw_persistence_score": "best_ic_persistence",
            }
        )
        worst = (
            raw_ic.sort_values(["parent_rule_id", "raw_persistence_score"], ascending=[True, True])
            .groupby("parent_rule_id")
            .head(1)
        )
        worst = worst.drop(columns=["rule_id"]).rename(
            columns={
                "parent_rule_id": "rule_id",
                "ic_family": "worst_death_condition",
                "raw_persistence_score": "worst_ic_persistence",
            }
        )
        birth_death = best[["rule_id", "best_birth_condition", "best_ic_persistence"]].merge(
            worst[["rule_id", "worst_death_condition", "worst_ic_persistence"]], on="rule_id", how="outer"
        )
        birth_death = birth_death.merge(
            analysis[["rule_id", "motif_family", "dominant_interaction_outcome", "collapse_rate", "explosion_rate"]],
            on="rule_id",
            how="left",
        )
        birth_death["death_mode_proxy"] = np.select(
            [
                birth_death["collapse_rate"].fillna(0) > 0.5,
                birth_death["explosion_rate"].fillna(0) > 0.5,
                birth_death["worst_ic_persistence"].fillna(0) <= 0.0,
            ],
            ["collapse", "explosion", "loss_of_persistence"],
            default="weak_or_unclear",
        )
    return anatomy, birth_death


def numeric_feature_frame(analysis: pd.DataFrame) -> pd.DataFrame:
    df = analysis[["rule_id", "motif_family"]].copy()
    for col in FEATURE_COLUMNS:
        if col in analysis.columns:
            df[col] = pd.to_numeric(analysis[col], errors="coerce").fillna(0.0)
        else:
            df[col] = 0.0
    return df


def plot_outputs(
    out: Path,
    analysis: pd.DataFrame,
    family_summary: pd.DataFrame,
    fertile_bins: pd.DataFrame,
    invariant_overlap: pd.DataFrame,
    validation: pd.DataFrame,
    discovery: pd.DataFrame,
) -> None:
    plt.figure(figsize=(9, 6))
    families = {name: i for i, name in enumerate(sorted(analysis["motif_family"].unique()))}
    colors = analysis["motif_family"].map(families)
    plt.scatter(
        analysis["adjusted_persistence"],
        analysis["composition_adjusted_delta"],
        c=colors,
        s=35 + 120 * analysis["control_adjusted_positive"].astype(int),
        alpha=0.75,
    )
    plt.axhline(0, color="black", linewidth=0.7)
    plt.axvline(0, color="black", linewidth=0.7)
    plt.xlabel("adjusted persistence")
    plt.ylabel("composition adjusted delta")
    plt.title("G4 motif family scatter")
    plt.tight_layout()
    plt.savefig(out / "motif_family_scatter.png", dpi=160)
    plt.close()

    def heat(axis_a: str, axis_b: str, path: Path, value: str = "control_adjusted_positive_rate") -> None:
        pivot_src = fertile_bins[fertile_bins["axis"].isin([axis_a, axis_b])].copy()
        if pivot_src.empty:
            return
        merged = analysis.copy()
        if axis_a == "output_entropy":
            merged["bin_a"] = make_bins(merged["output_entropy"], bins=[-0.01, 0.5, 1.0, 1.35, 1.6])
        elif axis_a == "left_right_asymmetry":
            merged["bin_a"] = make_bins(merged["left_right_asymmetry"], bins=[-0.01, 0.2, 0.4, 0.6, 1.01])
        else:
            merged["bin_a"] = make_bins(merged[axis_a])
        if axis_b == "active_fraction_mean":
            merged["bin_b"] = make_bins(merged["active_fraction_mean"], bins=[-0.01, 0.25, 0.5, 0.75, 1.01])
        elif axis_b == "relation_degree":
            merged["bin_b"] = merged["relation_degree"].fillna(-1).astype(int).astype(str)
        else:
            merged["bin_b"] = make_bins(merged[axis_b])
        pivot = merged.groupby(["bin_a", "bin_b"])["control_adjusted_positive"].mean().unstack(fill_value=0)
        plt.figure(figsize=(8, 5))
        plt.imshow(pivot.to_numpy(), aspect="auto", interpolation="nearest")
        plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
        plt.yticks(range(len(pivot.index)), pivot.index)
        plt.colorbar(label=value)
        plt.xlabel(axis_b)
        plt.ylabel(axis_a)
        plt.tight_layout()
        plt.savefig(path, dpi=160)
        plt.close()

    heat("output_entropy", "active_fraction_mean", out / "fertile_band_heatmap_entropy_activity.png")
    heat("left_right_asymmetry", "relation_degree", out / "fertile_band_heatmap_asymmetry_dependency.png")

    pivot = invariant_overlap.pivot(index="invariant_a", columns="invariant_b", values="cooccurrence_count").fillna(0)
    plt.figure(figsize=(8, 7))
    plt.imshow(pivot.to_numpy(), aspect="auto", interpolation="nearest")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label="cooccurrence count")
    plt.tight_layout()
    plt.savefig(out / "invariant_overlap_heatmap.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(
        analysis["adjusted_persistence"],
        analysis["future_distinct_descendant_count"],
        c=analysis["composition_adjusted_delta"].clip(lower=-1, upper=1),
        alpha=0.75,
    )
    plt.colorbar(label="composition adjusted delta")
    plt.xlabel("adjusted persistence")
    plt.ylabel("future distinct descendants")
    plt.tight_layout()
    plt.savefig(out / "composition_gap_scatter.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    val_scores = validation.head(15)[["rule_id", "validation_score"]]
    disc_scores = discovery.head(15)[["rule_id", "discovery_score"]]
    plt.plot(range(len(val_scores)), val_scores["validation_score"], marker="o", label="validation")
    plt.plot(range(len(disc_scores)), disc_scores["discovery_score"], marker="o", label="discovery")
    plt.xticks(range(max(len(val_scores), len(disc_scores))), range(1, max(len(val_scores), len(disc_scores)) + 1))
    plt.xlabel("rank")
    plt.ylabel("score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "validation_vs_discovery_leaderboard.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    mech_counts = analysis["mechanism_label_g4"].value_counts()
    plt.bar(mech_counts.index, mech_counts.values)
    plt.xticks(rotation=35, ha="right")
    plt.ylabel("rule count")
    plt.tight_layout()
    plt.savefig(out / "mechanism_family_counts.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.bar(family_summary["motif_family"], family_summary["rule_count"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("rule count")
    plt.tight_layout()
    plt.savefig(out / "motif_family_counts.png", dpi=160)
    plt.close()


def simulate_history(table: list[int], q: int = 3, steps: int = 256, width: int = 256, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    state = rng.integers(0, q, size=width, dtype=np.int16)
    state[rng.random(width) < 0.7] = 0
    hist = np.zeros((steps, width), dtype=np.int16)
    table_arr = np.asarray(table, dtype=np.int16)
    for t in range(steps):
        hist[t] = state
        left = np.roll(state, 1)
        right = np.roll(state, -1)
        idx = left * q * q + state * q + right
        state = table_arr[idx]
    return hist


def make_spacetime_examples(out: Path, analysis: pd.DataFrame) -> None:
    dest = out / "spacetime_examples"
    dest.mkdir(parents=True, exist_ok=True)
    g3_examples = G3_DIR / "spacetime_examples"

    selections: list[tuple[str, pd.DataFrame]] = [
        ("validation_positive", analysis[analysis["control_adjusted_positive"]].sort_values("adjusted_persistence", ascending=False)),
        (
            "composition_positive",
            analysis[analysis["non_emission_composition_positive"]].sort_values("composition_adjusted_delta", ascending=False).head(10),
        ),
        (
            "fakeout",
            analysis[analysis["reclassification"].isin(["symmetric_fakeout", "self_control_fakeout", "local_phase_fakeout"])]
            .sort_values("raw_persistence_score", ascending=False)
            .head(10),
        ),
        (
            "control",
            analysis[analysis["stratum"].isin(["S7_symmetric_control", "S8_self_only_control"])]
            .sort_values("raw_persistence_score", ascending=False)
            .head(5),
        ),
    ]
    made = set()
    for prefix, group in selections:
        for _, row in group.iterrows():
            rule_id = str(row["rule_id"])
            out_path = dest / f"{prefix}_{rule_id}.png"
            if out_path.name in made:
                continue
            candidates = list(g3_examples.glob(f"*{rule_id}*.png"))
            if candidates:
                shutil.copyfile(candidates[0], out_path)
            else:
                table = parse_table_json(row.get("table_json"))
                if not table:
                    continue
                hist = simulate_history(table, q=int(row.get("q", 3)), seed=0)
                plt.figure(figsize=(9, 5))
                plt.imshow(hist, aspect="auto", interpolation="nearest", cmap="viridis", vmin=0, vmax=max(int(row.get("q", 3)) - 1, 1))
                plt.title(f"{prefix}: {rule_id}")
                plt.xlabel("cell")
                plt.ylabel("time")
                plt.tight_layout()
                plt.savefig(out_path, dpi=150)
                plt.close()
            made.add(out_path.name)


def leaderboards(analysis: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    validation = analysis[analysis["control_adjusted_positive"]].copy()
    validation["validation_score"] = (
        validation["adjusted_persistence"].fillna(0) * 3
        + validation["relation_load_bearing_adjusted"].fillna(0) * 2
        + validation["asymmetry_load_bearing_adjusted"].fillna(0) * 2
        + validation["local_phase_fakeout_rejected"].fillna(False).astype(int)
        + validation["composition_adjusted_delta"].clip(lower=0).fillna(0)
    )
    validation = validation.sort_values("validation_score", ascending=False)

    discovery = analysis[~analysis["control_adjusted_positive"]].copy()
    discovery["mechanism_unusual_bonus"] = discovery["mechanism_label_g4"].isin(
        ["interaction_product", "emitter", "domain_wall", "phase_cycle"]
    ).astype(float)
    discovery["discovery_score"] = (
        discovery["raw_persistence_score"].fillna(0) * 2
        + discovery["motif_material_turnover"].fillna(0)
        + discovery["pattern_background_contrast"].fillna(0)
        + discovery["future_distinct_descendant_count"].fillna(0) / 64.0
        + discovery["composition_adjusted_delta"].clip(lower=0).fillna(0)
        + discovery["mechanism_unusual_bonus"]
    )
    discovery = discovery.sort_values("discovery_score", ascending=False)
    return validation, discovery


def estimator_report(start: float, analysis: pd.DataFrame) -> pd.DataFrame:
    warnings: list[str] = []
    if len(analysis) < 200:
        warnings.append("Analyzed set below full G3 stage2 candidate count.")
    if analysis["control_adjusted_positive"].sum() < 10:
        warnings.append("Validation positives remain sparse; family claims are descriptive only.")
    if analysis["all_core_invariants"].sum() < 3:
        warnings.append("All-core invariant overlap is nonempty but too sparse for strong-pass claims.")
    return pd.DataFrame(
        [
            {
                "probe": PROBE,
                "runtime_seconds": round(time.time() - start, 3),
                "analyzed_rule_count": int(len(analysis)),
                "source": str(G3_DIR),
                "new_motif_check": "reused G3 stage2 T=512 ring=256 N=96, exceeding requested N=64",
                "warnings": " | ".join(warnings),
            }
        ]
    )


def build_summary(
    start: float,
    analysis: pd.DataFrame,
    family_summary: pd.DataFrame,
    fertile_summary: pd.DataFrame,
    invariant_by_rule: pd.DataFrame,
    comp_audit: pd.DataFrame,
    new_motif_check: pd.DataFrame,
    estimator_warnings: list[str],
) -> dict[str, object]:
    top_band = fertile_summary.iloc[0].to_dict() if len(fertile_summary) else {}
    all_core = int(invariant_by_rule["all_core_invariants"].sum())
    pra = int(
        (
            invariant_by_rule["adjusted_persistence_positive"]
            & invariant_by_rule["relation_positive"]
            & invariant_by_rule["asymmetry_positive"]
            & invariant_by_rule["local_phase_fakeout_rejected"]
        ).sum()
    )
    comp_overlap = int((analysis["control_adjusted_positive"] & analysis["non_emission_composition_positive"]).sum())
    strong_threshold = float(analysis["adjusted_persistence"].quantile(0.9))
    strong_comp_overlap = int(
        ((analysis["adjusted_persistence"] >= strong_threshold) & analysis["non_emission_composition_positive"]).sum()
    )
    new_motif_persistent = int(new_motif_check["persistent_under_check"].sum()) if len(new_motif_check) else 0
    emission_only = int(((analysis["composition_adjusted_delta"] > 0) & analysis["composition_emission_only_flag"]).sum())
    new_motif_count = int(analysis["dominant_interaction_outcome"].eq("new_motif").sum())

    if all_core > 0 and comp_overlap > 0:
        recommendation = (
            "Proceed to G5 detector freeze for persistence/relation/asymmetry with composition tracked as a secondary "
            "branch. Composition overlaps the validation set but remains too sparse to define the primary claim."
        )
        next_probe = "DAX_G5_detector_freeze_q3r1_heldout_prediction"
    elif pra > 0:
        recommendation = (
            "Proceed to G5 freeze for persistence/relation/asymmetry only; keep composition demoted until a targeted "
            "mechanism pass improves overlap."
        )
        next_probe = "DAX_G5_persistence_relation_asymmetry_freeze"
    else:
        recommendation = "Run G4b focused mechanism anatomy before any detector freeze."
        next_probe = "DAX_G4b_focused_mechanism_anatomy"

    return {
        "probe": PROBE,
        "status": "COMPLETE",
        "runtime_seconds": round(time.time() - start, 3),
        "analyzed_rule_count": int(len(analysis)),
        "control_adjusted_positive_count": int(analysis["control_adjusted_positive"].sum()),
        "motif_family_count": int(family_summary["motif_family"].nunique()),
        "primary_result": {
            "families_identified": int(family_summary["motif_family"].nunique()) >= 3,
            "fertile_bands_identified": bool(top_band) and safe_float(top_band.get("control_adjusted_positive_rate")) > 0,
            "invariant_overlap_nonempty": all_core > 0,
            "composition_gap_explained": len(comp_audit) > 0,
            "new_motif_outcomes_persistent": new_motif_persistent > 0,
        },
        "family_summary": family_summary.head(12).to_dict(orient="records"),
        "fertile_band_summary": {
            "top_band": f"{top_band.get('axis')}={top_band.get('bin')}" if top_band else None,
            "top_band_control_adjusted_positive_rate": safe_float(top_band.get("control_adjusted_positive_rate")) if top_band else None,
            "top_band_sample_count": int(top_band.get("sampled_rule_count", 0)) if top_band else None,
            "top_band_control_leak_rate": safe_float(top_band.get("control_leak_rate")) if top_band else None,
        },
        "invariant_overlap": {
            "all_core_invariants_count": all_core,
            "persistence_relation_asymmetry_count": pra,
            "composition_overlap_count": comp_overlap,
        },
        "composition_gap": {
            "emission_only_count": emission_only,
            "new_motif_count": new_motif_count,
            "new_motif_persistent_count": new_motif_persistent,
            "strong_persistence_composition_overlap_count": strong_comp_overlap,
        },
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": estimator_warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--g3-dir", type=Path, default=G3_DIR)
    return parser.parse_args()


def main() -> None:
    global G3_DIR
    args = parse_args()
    G3_DIR = args.g3_dir
    out = args.out_dir
    start = time.time()
    out.mkdir(parents=True, exist_ok=True)

    analysis, tables = build_analysis()
    phase_sequences = read_csv("motif_phase_sequences.csv")
    family_summary, representatives = summarize_families(analysis)
    fertile_bins, fertile_summary, candidate_rates = fertile_bands(tables["stage1"], analysis)
    invariant_overlap, invariant_by_rule, invariant_venn = invariant_tables(analysis)
    comp_audit, new_motif_check, taxonomy = composition_gap(analysis)
    anatomy, birth_death = mechanism_tables(analysis, tables["ic"])
    validation, discovery = leaderboards(analysis)

    representative_ids = representatives["rule_id"].astype(str).tolist()
    extra_ids = (
        validation.head(20)["rule_id"].astype(str).tolist()
        + discovery.head(20)["rule_id"].astype(str).tolist()
        + analysis[analysis["non_emission_composition_positive"]].head(20)["rule_id"].astype(str).tolist()
    )
    fragments = transition_fragments(tables["stage2_manifest"], sorted(set(representative_ids + extra_ids)))

    write_csv(analysis, out / "analyzed_rule_manifest.csv")
    write_csv(analysis[["rule_id", "stratum", "motif_family", "mechanism_label_g4", "reclassification"]], out / "motif_family_assignments.csv")
    write_csv(family_summary, out / "motif_family_summary.csv")
    write_csv(representatives, out / "motif_family_representatives.csv")
    write_csv(fertile_bins, out / "fertile_band_bins.csv")
    write_csv(fertile_summary, out / "fertile_band_summary.csv")
    write_csv(candidate_rates, out / "fertile_band_candidate_rates.csv")
    write_csv(anatomy, out / "mechanism_anatomy.csv")
    write_csv(fragments, out / "dominant_transition_fragments.csv")
    write_csv(phase_sequences[phase_sequences["parent_rule_id"].isin(analysis["rule_id"])], out / "motif_phase_sequences.csv")
    write_csv(birth_death, out / "motif_birth_death_conditions.csv")
    write_csv(invariant_overlap, out / "invariant_overlap_table.csv")
    write_csv(invariant_by_rule, out / "invariant_overlap_by_rule.csv")
    write_csv(invariant_venn, out / "invariant_venn_counts.csv")
    write_csv(comp_audit, out / "composition_gap_audit.csv")
    write_csv(new_motif_check, out / "new_motif_persistence_check.csv")
    write_csv(taxonomy, out / "interaction_outcome_taxonomy.csv")
    write_csv(validation, out / "validation_leaderboard.csv")
    write_csv(discovery, out / "discovery_leaderboard.csv")

    estimator = estimator_report(start, analysis)
    write_csv(estimator, out / "estimator_report.csv")
    warnings = []
    if str(estimator.loc[0, "warnings"]):
        warnings = [x.strip() for x in str(estimator.loc[0, "warnings"]).split("|") if x.strip()]

    make_spacetime_examples(out, analysis)
    plot_outputs(out, analysis, family_summary, fertile_bins, invariant_overlap, validation, discovery)

    summary = build_summary(
        start,
        analysis,
        family_summary,
        fertile_summary,
        invariant_by_rule,
        comp_audit,
        new_motif_check,
        warnings,
    )
    with (out / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
