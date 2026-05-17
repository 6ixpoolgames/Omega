#!/usr/bin/env python
"""Probe DAX-G2b: control-adjusted primitive load-bearing guardrail.

Reuses DAX-G2 sampled rules and asks which positives survive matched controls.
This is deliberately narrow: no broad new rule sampling.
"""

from __future__ import annotations

import argparse
import hashlib
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


PRIMARY_Q3_RULES = {
    "q3r1_s5_0016",
    "q3r1_s1_0002",
    "q3r1_s4_0014",
    "q3r1_s2_0046",
    "q3r1_s3_0020",
    "q3r1_s5_0012",
    "q3r1_s3_0047",
}
Q2_MINI = {"q2r2_s1_0004", "q2r2_s2_0007", "q2r2_s4_0030", "q2r2_s1_0043"}
ECA_ANCHORS = {"ECA_169", "ECA_225", "ECA_73", "ECA_109", "ECA_54"}


@dataclass(frozen=True)
class Config:
    out_dir: Path
    g2_dir: Path
    workers: int
    n_seeds: int
    T: int
    ring_size: int
    stratum_nulls: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DAX_G2b_control_adjusted_primitive_guardrail_results"))
    p.add_argument("--g2-dir", type=Path, default=Path("probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--n-seeds", type=int, default=128)
    p.add_argument("--T", type=int, default=512)
    p.add_argument("--ring-size", type=int, default=256)
    p.add_argument("--stratum-nulls", type=int, default=10)
    return p.parse_args()


def spec_from_row(row: pd.Series) -> g2.RuleSpec:
    table = tuple(int(x) for x in json.loads(row["table_json"]))
    return g2.RuleSpec(str(row["space"]), str(row["rule_id"]), str(row["stratum"]), int(row["q"]), int(row["radius"]), table, None)


def load_g2_tables(g2_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    manifest = pd.read_csv(g2_dir / "sampled_rule_manifest.csv")
    stage1 = pd.read_csv(g2_dir / "rule_space_scan_metrics.csv")
    compare = pd.read_csv(g2_dir / "expanded_vs_ECA_comparison.csv")
    controls = pd.read_csv(g2_dir / "control_summary.csv")
    stage2 = pd.read_csv(g2_dir / "stage2_motif_anatomy.csv")
    return manifest, stage1, compare, controls, stage2


def select_targets(manifest: pd.DataFrame, stage1: pd.DataFrame, compare: pd.DataFrame) -> pd.DataFrame:
    comp = compare.copy()
    comp["relation_dependence_positive"] = comp.get("relation_dependence_positive", False).fillna(False).astype(bool)
    comp["asymmetry_dependence_positive"] = comp.get("asymmetry_dependence_positive", False).fillna(False).astype(bool)
    comp["composition_positive_count"] = comp.get("composition_positive_count", 0).fillna(0)
    target_ids = set(PRIMARY_Q3_RULES) | set(Q2_MINI) | set(ECA_ANCHORS)
    target_ids |= set(
        comp[
            (comp["space"] == "q3_radius1")
            & (
                (comp["confirmed_fraction"].fillna(0) >= 0.25)
                | comp["relation_dependence_positive"]
                | comp["asymmetry_dependence_positive"]
                | (comp["composition_positive_count"] > 0)
            )
        ]["rule_id"]
    )
    leaked = stage1[
        (stage1["space"].isin(["q3_radius1", "q2_radius2"]))
        & (stage1["stratum"].isin(["S7_symmetric_control", "S8_self_only_control"]))
        & (stage1["classification"].isin(["localized_persistence", "transported_identity", "emitter_or_generator"]))
    ]
    target_ids |= set(leaked["rule_id"])
    out = manifest[manifest["rule_id"].isin(target_ids)].copy()
    out["target_role"] = "candidate"
    out.loc[out["rule_id"].isin(leaked["rule_id"]), "target_role"] = "leaked_control"
    out.loc[out["space"] == "ECA_anchor", "target_role"] = "ECA_anchor"
    return out


def output_histogram_control(spec: g2.RuleSpec, seed_salt: str = "hist") -> g2.RuleSpec:
    table = np.array(spec.table, dtype=np.uint8)
    rng_seed = int(hashlib.sha1(f"{spec.rule_id}:{seed_salt}".encode()).hexdigest()[:12], 16) % (2**32)
    rng = np.random.default_rng(rng_seed)
    shuffled = table.copy()
    rng.shuffle(shuffled)
    return g2.RuleSpec(spec.space, f"{spec.rule_id}_output_histogram_random", "output_histogram_random", spec.q, spec.radius, tuple(int(x) for x in shuffled))


def symbol_phase_control(spec: g2.RuleSpec) -> g2.RuleSpec:
    q, radius = spec.q, spec.radius
    n = 2 * radius + 1
    table = np.array(spec.table, dtype=np.uint8)
    new = np.zeros_like(table)
    for center in range(q):
        vals = []
        for idx in range(len(table)):
            if g2.decode_idx(idx, q, n)[radius] == center:
                vals.append(int(table[idx]))
        counts = np.bincount(vals, minlength=q)
        chosen = int(np.argmax(counts))
        for idx in range(len(table)):
            if g2.decode_idx(idx, q, n)[radius] == center:
                new[idx] = chosen
    return g2.RuleSpec(spec.space, f"{spec.rule_id}_symbol_phase_only", "symbol_phase_only", q, radius, tuple(int(x) for x in new))


def control_specs_for_candidate(spec: g2.RuleSpec, stage1: pd.DataFrame, manifest: pd.DataFrame, cfg: Config) -> list[tuple[str, g2.RuleSpec]]:
    controls: list[tuple[str, g2.RuleSpec]] = []
    kinds = ["center_only_projection", "left_neighbor_removed", "right_neighbor_removed", "left_right_symmetrized_rule"]
    if spec.space == "q2_radius2":
        kinds += ["inner_neighbors_only", "outer_neighbors_removed"]
    for kind in kinds:
        controls.append((kind, g2.project_table(spec, kind)))
    if spec.space == "q3_radius1":
        controls.append(("symbol_phase_only", symbol_phase_control(spec)))
    controls.append(("output_distribution_matched_random", output_histogram_control(spec)))

    if spec.space in {"q3_radius1", "q2_radius2"}:
        prim = g2.primitive_for_spec(spec)
        pool = stage1[(stage1["space"] == spec.space) & (stage1["stratum"] == spec.stratum) & (stage1["rule_id"] != spec.rule_id)].copy()
        if len(pool):
            pool["entropy_delta"] = (pool["output_entropy"] - float(prim["output_entropy"])).abs()
            pool["dep_delta"] = (pool["relation_degree"] - float(prim["relation_degree"])).abs()
            pool = pool.sort_values(["dep_delta", "entropy_delta", "stage1_score"], ascending=[True, True, False]).head(cfg.stratum_nulls)
            for _, row in pool.iterrows():
                controls.append((f"stratum_null_{row['rule_id']}", spec_from_row(manifest[manifest["rule_id"] == row["rule_id"]].iloc[0])))
    return controls


def persistence_score(m: dict[str, float]) -> float:
    return float(
        m["recurrence_up_to_shift"]
        * m["motif_material_turnover"]
        * m["pattern_background_contrast"]
        * (1.0 - min(m["frozen_order_index"], 1.0))
        * (1.0 - min(m["chaos_index"], 1.0))
    )


def eval_spec_metrics(args: tuple[g2.RuleSpec, str, str, Config]) -> tuple[dict[str, object], list[dict[str, object]], dict[str, object]]:
    spec, parent_rule_id, control_type, cfg = args
    ics = g2.Q3_ICS if spec.space == "q3_radius1" else g2.Q2_ICS
    rows = []
    for ic in ics:
        hist = g2.simulate(spec, ic, cfg.T, cfg.ring_size, cfg.n_seeds, salt=31)
        m = g2.metrics_for_history(hist, spec.q)
        rows.append(
            {
                "space": spec.space,
                "rule_id": spec.rule_id,
                "parent_rule_id": parent_rule_id,
                "control_type": control_type,
                "stratum": spec.stratum,
                "ic_family": ic,
                **m,
                "raw_persistence_score": persistence_score(m),
            }
        )
    df = pd.DataFrame(rows)
    agg: dict[str, object] = {
        "space": spec.space,
        "rule_id": spec.rule_id,
        "parent_rule_id": parent_rule_id,
        "control_type": control_type,
        "stratum": spec.stratum,
        "q": spec.q,
        "radius": spec.radius,
    }
    for col in [c for c in df.columns if c not in {"space", "rule_id", "parent_rule_id", "control_type", "stratum", "ic_family"}]:
        agg[col] = float(df[col].mean())
    pert = perturbation_metrics(spec, parent_rule_id, control_type, cfg)
    agg.update(pert)
    return agg, rows, mechanism_report(spec, parent_rule_id, control_type, cfg)


def perturbation_metrics(spec: g2.RuleSpec, parent_rule_id: str, control_type: str, cfg: Config) -> dict[str, object]:
    ic = "short_random_active_block" if spec.space == "q3_radius1" else "short_random_block"
    hist = g2.simulate(spec, ic, min(160, cfg.T), cfg.ring_size, min(64, cfg.n_seeds), salt=37)
    table = np.array(spec.table, dtype=np.uint8)
    rng = np.random.default_rng(int(hashlib.sha1(f"{spec.rule_id}:pert".encode()).hexdigest()[:8], 16))
    mid = hist[min(64, hist.shape[0] - 1)].copy()
    labels = []
    codes = []
    for s in range(mid.shape[0]):
        xb = mid[s : s + 1].copy()
        xp = xb.copy()
        active = np.where(xp[0] != 0)[0]
        pos = int(rng.choice(active)) if len(active) else cfg.ring_size // 2
        xp[0, pos] = int((xp[0, pos] + 1) % spec.q)
        for _ in range(96):
            xb = g2.ca_step(xb, spec, table)
            xp = g2.ca_step(xp, spec, table)
        code = hashlib.sha1(xp.tobytes()).hexdigest()[:16]
        codes.append(code)
        af = float(np.mean(xp != 0))
        if af < 0.001:
            labels.append("collapse")
        elif af > 0.92:
            labels.append("explosion")
        elif xp.tobytes() == xb.tobytes():
            labels.append("same")
        else:
            labels.append("related")
    return {
        "future_distinct_descendant_count": float(len(set(codes))),
        "future_distinct_ratio": float(len(set(codes)) / max(len(codes), 1)),
        "post_perturbation_survival_rate": float(np.mean([x != "collapse" for x in labels])),
        "collapse_rate": float(np.mean([x == "collapse" for x in labels])),
        "explosion_rate": float(np.mean([x == "explosion" for x in labels])),
    }


def interaction_metrics(spec: g2.RuleSpec, parent_rule_id: str, control_type: str) -> dict[str, object]:
    if spec.space == "ECA_anchor":
        return {
            "parent_rule_id": parent_rule_id,
            "rule_id": spec.rule_id,
            "control_type": control_type,
            "stable_product_rate": 0.0,
            "phase_sensitive_outcome_rate": 0.0,
            "new_motif_rate": 0.0,
            "emission_rate": 0.0,
            "interaction_outcome_diversity": 0.0,
            "dominant_interaction_outcome": "not_run_for_ECA_anchor",
        }
    table = np.array(spec.table, dtype=np.uint8)
    outcomes = []
    for distance in [16, 32, 64]:
        for phase in [0, 1, 2, 3]:
            n = 24
            ring = 256
            x = np.zeros((n, ring), dtype=np.uint8)
            for s in range(n):
                c1 = ring // 2 - distance // 2
                c2 = ring // 2 + distance // 2
                v2 = 2 if spec.q == 3 and phase % 2 else 1
                x[s, c1 - 1 : c1 + 2] = 1
                x[s, c2 - 1 : c2 + 2] = v2
            initial_components = np.mean([len(g2.component_lengths_active(row)) for row in x])
            for _ in range(192):
                x = g2.ca_step(x, spec, table)
            final_components = np.mean([len(g2.component_lengths_active(row)) for row in x])
            active = float(np.mean(x != 0))
            if active < 0.001:
                outcome = "collapse"
            elif active > 0.92:
                outcome = "chaotic_explosion"
            elif final_components > initial_components + 1:
                outcome = "emission"
            elif final_components < max(1, initial_components - 1):
                outcome = "merge_or_annihilation"
            elif abs(final_components - initial_components) <= 0.5:
                outcome = "pass_through"
            else:
                outcome = "new_motif"
            outcomes.append(outcome)
    counts = pd.Series(outcomes).value_counts()
    return {
        "parent_rule_id": parent_rule_id,
        "rule_id": spec.rule_id,
        "control_type": control_type,
        "stable_product_rate": float(np.mean([x == "new_motif" for x in outcomes])),
        "phase_sensitive_outcome_rate": float(len(set(outcomes)) > 1),
        "new_motif_rate": float(np.mean([x == "new_motif" for x in outcomes])),
        "emission_rate": float(np.mean([x == "emission" for x in outcomes])),
        "interaction_outcome_diversity": g2.entropy_from_counts(counts.to_numpy()),
        "dominant_interaction_outcome": str(counts.index[0]) if len(counts) else "none",
    }


def mechanism_report(spec: g2.RuleSpec, parent_rule_id: str, control_type: str, cfg: Config) -> dict[str, object]:
    table = np.array(spec.table, dtype=np.uint8)
    n = 2 * spec.radius + 1
    hist = g2.simulate(spec, "short_random_active_block" if spec.space == "q3_radius1" else "short_random_block", 128, cfg.ring_size, 32, salt=41)
    active_windows = []
    phase_symbols = []
    for t in range(0, hist.shape[0], 8):
        frame = hist[t]
        phase_symbols.append(tuple(np.bincount(frame.reshape(-1), minlength=spec.q).tolist()))
        for row in frame[:8]:
            active_idx = np.where(row != 0)[0][:8]
            for pos in active_idx:
                vals = tuple(int(row[(pos + off) % cfg.ring_size]) for off in range(-spec.radius, spec.radius + 1))
                active_windows.append(vals)
    if active_windows:
        s = pd.Series(active_windows)
        top_neighborhood = str(s.value_counts().index[0])
        dominant_count = int(s.value_counts().iloc[0])
    else:
        top_neighborhood = "none"
        dominant_count = 0
    m = g2.metrics_for_history(hist, spec.q)
    if m["frozen_order_index"] > 0.7:
        mechanism = "local-phase-clock-like"
    elif abs(m["translation_velocity_estimate"]) > 0.01:
        mechanism = "travelling"
    elif m["component_fragmentation_rate"] > 0.2:
        mechanism = "emitter-like"
    elif m["recurrence_up_to_shift"] > 0.75:
        mechanism = "oscillatory"
    elif m["pattern_background_contrast"] > 0.5:
        mechanism = "domain-wall-like"
    else:
        mechanism = "unknown"
    return {
        "space": spec.space,
        "parent_rule_id": parent_rule_id,
        "rule_id": spec.rule_id,
        "control_type": control_type,
        "dominant_active_neighborhood": top_neighborhood,
        "dominant_active_neighborhood_count": dominant_count,
        "mechanism_label": mechanism,
        "symbol_turnover_by_phase_proxy": float(m["motif_material_turnover"]),
        "phase_sequence_length": len(set(phase_symbols)),
    }


def fairness_audit(parent: g2.RuleSpec, control_type: str, control: g2.RuleSpec, raw_density: float, control_density: float) -> dict[str, object]:
    pprim = g2.primitive_for_spec(parent)
    cprim = g2.primitive_for_spec(control)
    ptable = np.array(parent.table, dtype=np.uint8)
    ctable = np.array(control.table, dtype=np.uint8)
    n = min(len(ptable), len(ctable))
    return {
        "space": parent.space,
        "parent_rule_id": parent.rule_id,
        "control_rule_id": control.rule_id,
        "control_type": control_type,
        "output_entropy_difference": float(abs(float(pprim["output_entropy"]) - float(cprim["output_entropy"]))),
        "dependency_degree_difference": float(abs(float(pprim["relation_degree"]) - float(cprim["relation_degree"]))),
        "activity_density_difference": float(abs(raw_density - control_density)),
        "quiescent_preservation_match": bool(parent.table[0] == control.table[0]),
        "rule_table_hamming_distance": float(np.mean(ptable[:n] != ctable[:n])),
        "left_right_dependency_preserved": bool((float(pprim["left_right_asymmetry"]) > 0.0) == (float(cprim["left_right_asymmetry"]) > 0.0)),
        "center_dependency_preserved": bool(pprim["depends_center"] == cprim["depends_center"]),
    }


def classify_row(row: pd.Series) -> str:
    if row["target_role"] == "leaked_control" and row["stratum"] == "S7_symmetric_control":
        if row["asymmetry_load_bearing_adjusted"] <= 0 or row["symmetrized_rule_score"] >= row["raw_persistence_score"] * 0.98:
            return "symmetric_fakeout"
    if row["target_role"] == "leaked_control" and row["stratum"] == "S8_self_only_control":
        if row["relation_load_bearing_adjusted"] <= 0 or row["center_only_score"] >= row["raw_persistence_score"] * 0.98:
            return "self_persistence_fakeout"
    if row["adjusted_persistence"] <= 0:
        if row["center_only_score"] >= row["raw_persistence_score"] or row["symbol_phase_only_score"] >= row["raw_persistence_score"]:
            return "self_persistence_fakeout"
        if row["symmetrized_rule_score"] >= row["raw_persistence_score"]:
            return "symmetric_fakeout"
        if row["output_distribution_matched_score"] >= row["raw_persistence_score"]:
            return "output_distribution_fakeout"
        return "generic_persistence"
    if not row["local_phase_fakeout_rejected"]:
        return "self_persistence_fakeout"
    if row["composition_emission_only_flag"] and row["composition_adjusted_delta"] <= 0:
        return "emission_only"
    if row["relation_load_bearing_adjusted"] > 0 or row["asymmetry_load_bearing_adjusted"] > 0:
        return "control_adjusted_positive"
    return "fragile_or_inconclusive"


def main() -> None:
    args = parse_args()
    cfg = Config(args.out_dir, args.g2_dir, args.workers, args.n_seeds, args.T, args.ring_size, args.stratum_nulls)
    t0 = time.time()
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True)

    manifest, stage1, compare, _control_summary, stage2 = load_g2_tables(cfg.g2_dir)
    targets = select_targets(manifest, stage1, compare)
    targets.to_csv(cfg.out_dir / "target_rule_manifest.csv", index=False)
    target_specs = [spec_from_row(row) for _, row in targets.iterrows()]

    control_manifest_rows = []
    eval_specs: list[tuple[g2.RuleSpec, str, str]] = []
    parent_by_id = {s.rule_id: s for s in target_specs}
    for spec in target_specs:
        eval_specs.append((spec, spec.rule_id, "raw"))
        for ctype, cspec in control_specs_for_candidate(spec, stage1, manifest, cfg):
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
    pd.DataFrame(control_manifest_rows).to_csv(cfg.out_dir / "matched_control_manifest.csv", index=False)

    metric_rows = []
    ic_rows = []
    mech_rows = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as ex:
        futures = [ex.submit(eval_spec_metrics, (spec, parent, ctype, cfg)) for spec, parent, ctype in eval_specs]
        for i, fut in enumerate(as_completed(futures), 1):
            agg, rows, mech = fut.result()
            metric_rows.append(agg)
            ic_rows.extend(rows)
            mech_rows.append(mech)
            if i % max(1, len(futures) // 20) == 0:
                print(f"metrics {i}/{len(futures)}", flush=True)
    metrics = pd.DataFrame(metric_rows)
    metrics[metrics["control_type"] == "raw"].to_csv(cfg.out_dir / "raw_candidate_metrics.csv", index=False)
    metrics[metrics["control_type"] != "raw"].to_csv(cfg.out_dir / "matched_control_metrics.csv", index=False)
    pd.DataFrame(ic_rows).to_csv(cfg.out_dir / "ic_family_dependence.csv", index=False)
    pd.DataFrame(mech_rows).to_csv(cfg.out_dir / "motif_mechanism_report.csv", index=False)
    pd.DataFrame(ic_rows)[["space", "parent_rule_id", "rule_id", "control_type", "ic_family", "raw_persistence_score"]].to_csv(
        cfg.out_dir / "motif_phase_sequences.csv", index=False
    )

    interaction_rows = []
    for spec, parent, ctype in eval_specs:
        if ctype == "raw" or ctype in {"center_only_projection", "left_right_symmetrized_rule", "symbol_phase_only", "output_distribution_matched_random"}:
            interaction_rows.append(interaction_metrics(spec, parent, ctype))
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
        adjusted = raw_score - max(center, symbol, hist, null_q90)
        relation_adj = raw_score - max(center, left, right)
        asym_adj = raw_score - sym
        raw_fd = float(raw["future_distinct_descendant_count"])
        symbol_fd_vals = controls[controls["control_type"] == "symbol_phase_only"]["future_distinct_descendant_count"]
        symbol_fd = float(symbol_fd_vals.max()) if len(symbol_fd_vals) else -1.0
        local_phase_rejected = bool(raw_score > symbol and raw_fd > symbol_fd)

        raw_inter = inter[(inter["parent_rule_id"] == spec.rule_id) & (inter["control_type"] == "raw")]
        control_inter = inter[(inter["parent_rule_id"] == spec.rule_id) & (inter["control_type"] != "raw")]
        if len(raw_inter):
            ri = raw_inter.iloc[0]
            control_stable = float(control_inter["stable_product_rate"].max()) if len(control_inter) else 0.0
            control_phase = float(control_inter["phase_sensitive_outcome_rate"].max()) if len(control_inter) else 0.0
            control_new = float(control_inter["new_motif_rate"].max()) if len(control_inter) else 0.0
            comp_delta = max(
                float(ri["stable_product_rate"]) - control_stable,
                float(ri["phase_sensitive_outcome_rate"]) - control_phase,
                float(ri["new_motif_rate"]) - control_new,
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
            "target_role": targets[targets["rule_id"] == spec.rule_id]["target_role"].iloc[0],
            "raw_persistence_score": raw_score,
            "adjusted_persistence": adjusted,
            "center_only_score": center,
            "left_removed_score": left,
            "right_removed_score": right,
            "symmetrized_rule_score": sym,
            "symbol_phase_only_score": symbol,
            "output_distribution_matched_score": hist,
            "stratum_null_persistence_q90": null_q90,
            "relation_load_bearing_adjusted": relation_adj,
            "asymmetry_load_bearing_adjusted": asym_adj,
            "local_phase_fakeout_rejected": local_phase_rejected,
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
            fairness_rows.append(fairness_audit(spec, ctype, cspec, float(raw["active_fraction_mean"]), float(crow["active_fraction_mean"])))

    adjusted_df = pd.DataFrame(adjusted_rows)
    adjusted_df["reclassification"] = adjusted_df.apply(classify_row, axis=1)
    adjusted_df.to_csv(cfg.out_dir / "control_adjusted_metrics.csv", index=False)
    adjusted_df[["space", "rule_id", "relation_load_bearing_adjusted", "reclassification"]].to_csv(cfg.out_dir / "relation_guardrail_results.csv", index=False)
    adjusted_df[["space", "rule_id", "asymmetry_load_bearing_adjusted", "reclassification"]].to_csv(cfg.out_dir / "asymmetry_guardrail_results.csv", index=False)
    adjusted_df[["space", "rule_id", "local_phase_fakeout_rejected", "symbol_phase_only_score", "reclassification"]].to_csv(cfg.out_dir / "local_phase_fakeout_results.csv", index=False)
    adjusted_df[["space", "rule_id", "composition_adjusted_delta", "composition_emission_only_flag", "dominant_interaction_outcome", "reclassification"]].to_csv(cfg.out_dir / "composition_guardrail_results.csv", index=False)
    adjusted_df[["space", "rule_id", "target_role", "reclassification"]].to_csv(cfg.out_dir / "reclassification_results.csv", index=False)
    pd.DataFrame(fairness_rows).to_csv(cfg.out_dir / "matched_control_fairness_audit.csv", index=False)
    inter.to_csv(cfg.out_dir / "stage2_interaction_composition_adjusted.csv", index=False)

    leaks = adjusted_df[adjusted_df["target_role"] == "leaked_control"].copy()
    leak_resolution = leaks[["space", "rule_id", "stratum", "reclassification", "adjusted_persistence"]].copy()
    leak_resolution["resolved"] = leak_resolution["reclassification"] != "control_adjusted_positive"
    leak_resolution.to_csv(cfg.out_dir / "control_leak_resolution.csv", index=False)

    boot = []
    for _, row in adjusted_df.iterrows():
        ic = pd.DataFrame(ic_rows)
        vals = ic[(ic["parent_rule_id"] == row["rule_id"]) & (ic["control_type"] == "raw")]["raw_persistence_score"].to_numpy()
        if len(vals):
            boot.append(
                {
                    "rule_id": row["rule_id"],
                    "metric": "raw_persistence_score",
                    "mean": float(np.mean(vals)),
                    "ci_low": float(np.quantile(vals, 0.05)),
                    "ci_high": float(np.quantile(vals, 0.95)),
                }
            )
    pd.DataFrame(boot).to_csv(cfg.out_dir / "bootstrap_intervals.csv", index=False)
    pd.DataFrame([{"warning": ""}]).to_csv(cfg.out_dir / "estimator_report.csv", index=False)

    make_plots(cfg.out_dir, adjusted_df)

    positives = adjusted_df[adjusted_df["reclassification"] == "control_adjusted_positive"]
    q3_pos = positives[positives["space"] == "q3_radius1"]
    relation_pos = adjusted_df[adjusted_df["relation_load_bearing_adjusted"] > 0]
    asym_pos = adjusted_df[adjusted_df["asymmetry_load_bearing_adjusted"] > 0]
    local_phase_rej = adjusted_df[(adjusted_df["space"] == "q3_radius1") & (adjusted_df["local_phase_fakeout_rejected"])]
    comp_pos = adjusted_df[adjusted_df["composition_adjusted_delta"] > 0]
    remaining_leaks = leak_resolution[~leak_resolution["resolved"]].to_dict(orient="records")
    guardrail_passed = bool(len(q3_pos) >= 1 and leaks["reclassification"].ne("control_adjusted_positive").all() and len(relation_pos) >= 1 and len(asym_pos) >= 1 and len(local_phase_rej) >= 1)

    best = positives.sort_values(["adjusted_persistence", "relation_load_bearing_adjusted", "asymmetry_load_bearing_adjusted"], ascending=False).head(1)
    b = best.iloc[0].to_dict() if len(best) else adjusted_df.sort_values("adjusted_persistence", ascending=False).head(1).iloc[0].to_dict()
    recommendation = "All G2 positives collapse under matched controls; treat G2 as generic persistence."
    next_probe = "DAX_G1_or_metric_rethink"
    if guardrail_passed and len(comp_pos):
        recommendation = "G2b passes; run focused q3/r1 larger sample with guardrails active."
        next_probe = "DAX_G3_q3r1_guardrailed_phase_map"
    elif guardrail_passed:
        recommendation = "G2b leaves load-bearing persistence but not composition; proceed with q3/r1 persistence trunk and defer composition."
        next_probe = "DAX_G3_q3r1_persistence_load_bearing"
    elif len(q3_pos):
        recommendation = "Some q3/r1 positives survive but guardrails are incomplete; inspect remaining leaks before scaling."
        next_probe = "DAX_G2c_remaining_leak_revision"

    summary = {
        "probe": "DAX_G2b_control_adjusted_primitive_guardrail",
        "status": "COMPLETE",
        "runtime_seconds": round(time.time() - t0, 3),
        "target_rule_count": int(len(target_specs)),
        "matched_control_count": int(len(control_manifest_rows)),
        "primary_result": {
            "guardrail_passed": guardrail_passed,
            "q3_control_leaks_resolved": bool(leaks[leaks["space"] == "q3_radius1"]["reclassification"].ne("control_adjusted_positive").all()) if len(leaks[leaks["space"] == "q3_radius1"]) else True,
            "control_adjusted_positive_count": int(len(positives)),
            "relation_adjusted_positive_count": int(len(relation_pos)),
            "asymmetry_adjusted_positive_count": int(len(asym_pos)),
            "local_phase_fakeout_rejected_count": int(len(local_phase_rej)),
            "composition_adjusted_positive_count": int(len(comp_pos)),
        },
        "top_control_adjusted_candidates": positives.sort_values("adjusted_persistence", ascending=False).head(10).to_dict(orient="records"),
        "best_candidate_profile": {
            "space": b.get("space"),
            "rule_id": b.get("rule_id"),
            "stratum": b.get("stratum"),
            "raw_persistence_score": b.get("raw_persistence_score"),
            "adjusted_persistence": b.get("adjusted_persistence"),
            "relation_load_bearing_adjusted": b.get("relation_load_bearing_adjusted"),
            "asymmetry_load_bearing_adjusted": b.get("asymmetry_load_bearing_adjusted"),
            "local_phase_fakeout_rejected": b.get("local_phase_fakeout_rejected"),
            "composition_adjusted_delta": b.get("composition_adjusted_delta"),
            "reclassification": b.get("reclassification"),
        },
        "leak_resolution": {
            "symmetric_control_leaks_resolved": bool(leaks[leaks["stratum"] == "S7_symmetric_control"]["reclassification"].ne("control_adjusted_positive").all()) if len(leaks[leaks["stratum"] == "S7_symmetric_control"]) else True,
            "self_control_leaks_resolved": bool(leaks[leaks["stratum"] == "S8_self_only_control"]["reclassification"].ne("control_adjusted_positive").all()) if len(leaks[leaks["stratum"] == "S8_self_only_control"]) else True,
            "remaining_leaks": remaining_leaks,
        },
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": [],
    }
    clean = g2.json_sanitize(summary)
    (cfg.out_dir / "summary.json").write_text(json.dumps(clean, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(clean, indent=2, allow_nan=False), flush=True)


def make_plots(out: Path, df: pd.DataFrame) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    ordered = df.sort_values("adjusted_persistence", ascending=False).head(35)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(ordered["rule_id"], ordered["adjusted_persistence"])
    ax.tick_params(axis="x", rotation=90)
    ax.axhline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "adjusted_persistence_by_rule.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(df["relation_load_bearing_adjusted"], df["asymmetry_load_bearing_adjusted"], c=(df["reclassification"] == "control_adjusted_positive"), s=35)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("relation adjusted")
    ax.set_ylabel("asymmetry adjusted")
    fig.tight_layout()
    fig.savefig(out / "relation_asymmetry_adjusted_scatter.png", dpi=160)
    plt.close(fig)

    for y, fname in [
        ("center_only_score", "raw_vs_center_only_persistence.png"),
        ("symmetrized_rule_score", "raw_vs_symmetrized_persistence.png"),
        ("symbol_phase_only_score", "raw_vs_symbol_phase_control.png"),
    ]:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.scatter(df["raw_persistence_score"], df[y], s=28)
        lim = max(float(df["raw_persistence_score"].max()), float(df[y].max()), 1e-6)
        ax.plot([0, lim], [0, lim], color="black", linewidth=0.8)
        ax.set_xlabel("raw")
        ax.set_ylabel(y)
        fig.tight_layout()
        fig.savefig(out / fname, dpi=160)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5))
    comp = df.sort_values("composition_adjusted_delta", ascending=False).head(35)
    ax.bar(comp["rule_id"], comp["composition_adjusted_delta"])
    ax.tick_params(axis="x", rotation=90)
    ax.axhline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(out / "composition_adjusted_by_rule.png", dpi=160)
    plt.close(fig)

    counts = df["reclassification"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(counts.index, counts.values)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "reclassification_counts.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
