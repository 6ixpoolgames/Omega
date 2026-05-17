#!/usr/bin/env python
"""Probe DAX-G5: q3/r1 detector freeze and held-out prediction.

This probe freezes the q3/r1 DAR-persistence detector before held-out sampling,
then tests whether predeclared fertile bands enrich primary positives relative
to matched control/barren bands.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import probe_DAX_G2_persistence_phase_map_minimal_rule_spaces as g2
import probe_DAX_G3_q3r1_guardrailed_phase_map as g3


PROBE = "DAX_G5_q3r1_detector_freeze_heldout_prediction"
OUT_DIR = Path("probe_DAX_G5_q3r1_detector_freeze_heldout_prediction_results")
G3_DIR = Path("probe_DAX_G3_q3r1_guardrailed_phase_map_results")
G4_DIR = Path("probe_DAX_G4_q3r1_motif_ecology_mechanism_results")
FREEZE_NOTE = Path("docs/research_notes/primitive_branch/q3r1_detector_freeze_v1.md")
PREREG_NOTE = Path("docs/research_notes/primitive_branch/q3r1_G5_preregistration.md")


@dataclass(frozen=True)
class Config:
    out_dir: Path
    g3_dir: Path
    g4_dir: Path
    workers: int
    sample_scale: float
    stage1_n_seeds: int
    stage1_T: int
    stage1_ring: int
    stage2_n_seeds: int
    stage2_T: int
    stage2_ring: int
    stage2_cap_per_band: int
    stage2_min_per_band: int
    stratum_nulls: int
    diagram_count: int


BASE_BAND_COUNTS = {
    "F1_G4_top_S1_random_unbiased": 1000,
    "F2_high_relation_asymmetry_structural": 1000,
    "F3_near_validation_PRA_structural": 1000,
    "B1_S7_symmetric_matched": 500,
    "B2_S8_self_only_matched": 500,
    "B3_output_distribution_matched_random": 500,
    "B4_high_chaos_high_frozen_barren": 500,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--g3-dir", type=Path, default=G3_DIR)
    parser.add_argument("--g4-dir", type=Path, default=G4_DIR)
    parser.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    parser.add_argument("--sample-scale", type=float, default=float(os.environ.get("DAX_G5_SAMPLE_SCALE", "1.0")))
    parser.add_argument("--stage1-n-seeds", type=int, default=64)
    parser.add_argument("--stage1-T", type=int, default=256)
    parser.add_argument("--stage1-ring", type=int, default=256)
    parser.add_argument("--stage2-n-seeds", type=int, default=128)
    parser.add_argument("--stage2-T", type=int, default=512)
    parser.add_argument("--stage2-ring", type=int, default=256)
    parser.add_argument("--stage2-cap-per-band", type=int, default=80)
    parser.add_argument("--stage2-min-per-band", type=int, default=10)
    parser.add_argument("--stratum-nulls", type=int, default=10)
    parser.add_argument("--diagram-count", type=int, default=30)
    return parser.parse_args()


def detector_freeze_payload() -> dict[str, object]:
    return {
        "detector_name": "q3r1_DAR_persistence_v1",
        "frozen_before_heldout": True,
        "primary_target": "DAR_persistence",
        "primary_positive_definition": {
            "adjusted_persistence": "> 0",
            "relation_load_bearing_adjusted": "> 0",
            "asymmetry_load_bearing_adjusted": "> 0",
            "local_phase_fakeout_rejected": True,
            "reclassification": "control_adjusted_positive",
        },
        "raw_persistence_score": "recurrence_up_to_shift * motif_material_turnover * background_contrast * (1 - frozen_order_index) * (1 - chaos_index)",
        "adjusted_persistence": "raw_persistence_score - max(center_only_persistence, symbol_phase_only_persistence, output_distribution_matched_persistence, stratum_null_persistence_q90)",
        "relation_load_bearing_adjusted": "raw_persistence_score - max(left_removed_score, right_removed_score, center_only_score)",
        "asymmetry_load_bearing_adjusted": "raw_persistence_score - symmetrized_rule_score",
        "local_phase_fakeout_rejected": "raw_persistence_score > symbol_phase_only_score AND future_distinct_descendant_count_raw > future_distinct_descendant_count_symbol_phase",
        "composition_secondary": {
            "tracked": True,
            "primary_required": False,
            "non_emission_composition_positive_definition": "composition_adjusted_delta > 0 AND dominant_interaction_outcome != emission_only",
        },
        "matched_controls": [
            "center_only_projection",
            "left_removed",
            "right_removed",
            "left_right_symmetrized_rule",
            "symbol_phase_only_control",
            "output_distribution_matched_random_control",
            "stratum_matched_nulls",
        ],
        "heldout_fertile_bands": {
            "F1_G4_top_S1_random_unbiased": "G4 top fertile band; q3/r1 S1 random-unbiased generator.",
            "F2_high_relation_asymmetry_structural": "q3/r1 structurally relation-complete rules with relation_degree=2, depends_center=true, left_right_asymmetry>=0.35, output_entropy in [1.0, 1.585].",
            "F3_near_validation_PRA_structural": "q3/r1 S4/S1-like relation-complete rules with depends_center=true, left_right_asymmetry>=0.20, output_entropy in [0.9, 1.585], not self-only.",
        },
        "heldout_control_bands": {
            "B1_S7_symmetric_matched": "q3/r1 symmetric-control generator with coarse output-entropy/activity matching.",
            "B2_S8_self_only_matched": "q3/r1 self-only-control generator with coarse output-entropy/activity matching.",
            "B3_output_distribution_matched_random": "q3/r1 random tables constrained to G4 fertile-like output entropy.",
            "B4_high_chaos_high_frozen_barren": "q3/r1 high-entropy or quiescent-preserving barren band expected to overproduce chaos/frozen artifacts.",
        },
        "stage1_candidate_criteria": {
            "classification": ["localized_persistence", "transported_identity", "emitter_or_generator", "mixed"],
            "stage1_score": "> 0",
            "selection": "all candidate positives up to frozen per-band cap, with top stage1_score/relation_asymmetry_priority ordering only for runtime cap",
        },
        "success_criteria": {
            "operational_pass": "fertile_primary_positive_rate >= 3x control_primary_positive_rate AND fertile_primary_positive_count >= 5 AND control_leak_count <= 1",
            "strong_pass": "fertile_primary_positive_rate >= 5x control_primary_positive_rate AND fertile_primary_positive_count >= 10 AND control_leak_count == 0 AND at least two fertile bands independently produce positives",
        },
        "forbidden_changes_after_freeze": [
            "metric definitions",
            "thresholds",
            "matched-control construction",
            "candidate promotion criteria",
            "fertile-band labels",
        ],
    }


def write_phase0_artifacts(cfg: Config) -> None:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    freeze = detector_freeze_payload()
    (cfg.out_dir / "detector_freeze.json").write_text(json.dumps(freeze, indent=2), encoding="utf-8")

    FREEZE_NOTE.parent.mkdir(parents=True, exist_ok=True)
    FREEZE_NOTE.write_text(
        """# q3/r1 Detector Freeze v1

Probe: DAX-G5 q3/r1 detector freeze and held-out prediction.

Frozen detector name:

```text
q3r1_DAR_persistence_v1
```

Primary target:

```text
DAR-persistence motifs in q=3/r=1 cellular rule space.
```

Primary positive definition:

```text
adjusted_persistence > 0
relation_load_bearing_adjusted > 0
asymmetry_load_bearing_adjusted > 0
local_phase_fakeout_rejected = true
reclassification == control_adjusted_positive
```

Composition is tracked but not required for the primary claim.

Frozen held-out fertile bands:

- F1: G4 top fertile band, `S1_random_unbiased`.
- F2: high relation/asymmetry structural band.
- F3: near-validation PRA structural band.

Frozen held-out controls:

- B1: S7 symmetric controls.
- B2: S8 self-only controls.
- B3: output-distribution matched random q3/r1 rules.
- B4: high-chaos/high-frozen barren region.

Forbidden after freeze:

- detector metric changes;
- threshold changes;
- matched-control construction changes;
- candidate promotion changes;
- fertile/control band relabeling.
""",
        encoding="utf-8",
    )

    PREREG_NOTE.write_text(
        """# DAX-G5 Preregistration and Claim Boundary

Probe:

```text
DAX-G5 q3/r1 detector freeze and held-out prediction.
```

Primary target:

```text
DAR-persistence motifs in q=3/r=1 cellular rule space.
```

Primary claim if passed:

```text
A frozen detector predicts held-out q3/r1 DAR-persistence motifs better than matched controls.
```

Explicit non-claims:

- This does not validate Omega.
- This does not demonstrate agency.
- This does not demonstrate value-bearing substrate.
- This does not demonstrate open-ended intelligence.
- This does not establish universal robustness.
- This does not establish composition as primary unless separately supported.

Frozen detector:

```text
adjusted_persistence > 0
relation_load_bearing_adjusted > 0
asymmetry_load_bearing_adjusted > 0
local_phase_fakeout_rejected = true
reclassification == control_adjusted_positive
```

Secondary tracked signals:

- non-emission composition;
- new-motif persistence;
- discovery-leaderboard anomalies.

Pass criteria:

```text
fertile_primary_positive_rate >= 3x control_primary_positive_rate
fertile_primary_positive_count >= 5
control leak count <= 1
```

Strong pass criteria:

```text
fertile_primary_positive_rate >= 5x control_primary_positive_rate
fertile_primary_positive_count >= 10
control leak count == 0
at least two fertile bands independently produce positives
```

Failure interpretation:

```text
If G5 fails, G3/G4 described q3/r1 ecology but did not yield a predictive detector.
Do not modify the detector inside G5 to rescue the result.
```

Discovery lane:

```text
Interesting rejected rules should be preserved for later study,
but not counted as validation evidence.
```
""",
        encoding="utf-8",
    )


def previous_digests(cfg: Config) -> set[str]:
    digests: set[str] = set()
    for path in [
        cfg.g3_dir / "sampled_rule_manifest.csv",
        cfg.g3_dir / "stage2_candidate_manifest.csv",
        cfg.g4_dir / "analyzed_rule_manifest.csv",
    ]:
        if path.exists():
            df = pd.read_csv(path, usecols=lambda c: c in {"table_digest", "rule_table_digest"})
            for col in df.columns:
                digests |= set(df[col].dropna().astype(str))
    return digests


def band_count(cfg: Config, band: str) -> int:
    return max(1, int(round(BASE_BAND_COUNTS[band] * cfg.sample_scale)))


def structural_row(spec: g2.RuleSpec) -> dict[str, object]:
    row = g2.primitive_for_spec(spec)
    counts = np.bincount(np.array(spec.table, dtype=np.uint8), minlength=spec.q)
    total = max(int(counts.sum()), 1)
    row["output_symbol_distribution"] = json.dumps([float(x / total) for x in counts], separators=(",", ":"))
    row["dependency_degree"] = row["relation_degree"]
    row["center_dominance"] = bool(row["depends_center"])
    row["activity_density_estimate"] = float(1.0 - counts[0] / total)
    row["quiescent_preservation"] = bool(spec.table[0] == 0)
    row["rule_table_digest"] = row["table_digest"]
    row["table_json"] = json.dumps(list(spec.table), separators=(",", ":"))
    return row


def accept_band(table: np.ndarray, band: str) -> bool:
    spec = g2.RuleSpec("q3_radius1", "tmp", "tmp", 3, 1, tuple(int(x) for x in table))
    prim = g2.primitive_for_spec(spec)
    ent = float(prim["output_entropy"])
    asym = float(prim["left_right_asymmetry"])
    dep = int(prim["relation_degree"])
    center = bool(prim["depends_center"])
    self_only = bool(prim["self_only"])
    active_density = float(np.mean(table != 0))

    if band == "F1_G4_top_S1_random_unbiased":
        return True
    if band == "F2_high_relation_asymmetry_structural":
        return dep == 2 and center and asym >= 0.35 and 1.0 <= ent <= math.log2(3) + 1e-9 and not self_only
    if band == "F3_near_validation_PRA_structural":
        return dep >= 1 and center and asym >= 0.20 and 0.9 <= ent <= math.log2(3) + 1e-9 and not self_only
    if band == "B1_S7_symmetric_matched":
        return asym <= 0.05 and 0.4 <= active_density <= 0.9
    if band == "B2_S8_self_only_matched":
        return True
    if band == "B3_output_distribution_matched_random":
        return 1.0 <= ent <= math.log2(3) + 1e-9 and 0.35 <= active_density <= 0.9
    if band == "B4_high_chaos_high_frozen_barren":
        return ent >= 1.45 or active_density <= 0.25 or active_density >= 0.9
    raise ValueError(band)


def generator_strata_for_band(band: str) -> list[str]:
    if band == "F1_G4_top_S1_random_unbiased":
        return ["S1_random_unbiased"]
    if band == "F2_high_relation_asymmetry_structural":
        return ["S5_asymmetric_neighbor_dependent", "S6_relation_rich_nonchaotic_bias", "S1_random_unbiased"]
    if band == "F3_near_validation_PRA_structural":
        return ["S4_neighbor_dependent", "S1_random_unbiased", "S3_sparse_active_preserving"]
    if band == "B1_S7_symmetric_matched":
        return ["S7_symmetric_control"]
    if band == "B2_S8_self_only_matched":
        return ["S8_self_only_control"]
    if band == "B3_output_distribution_matched_random":
        return ["S1_random_unbiased"]
    if band == "B4_high_chaos_high_frozen_barren":
        return ["S1_random_unbiased", "S2_quiescent_preserving", "S6_relation_rich_nonchaotic_bias"]
    raise ValueError(band)


def build_heldout_manifest(cfg: Config) -> pd.DataFrame:
    seen = previous_digests(cfg)
    rows: list[dict[str, object]] = []
    band_types = {k: ("fertile" if k.startswith("F") else "control") for k in BASE_BAND_COUNTS}
    for band in BASE_BAND_COUNTS:
        target = band_count(cfg, band)
        strata = generator_strata_for_band(band)
        accepted = 0
        attempts = 0
        while accepted < target:
            attempts += 1
            if attempts > target * 2000:
                raise RuntimeError(f"Could not fill held-out band {band}; accepted {accepted}/{target}")
            stratum = strata[(accepted + attempts) % len(strata)]
            seed = 5_500_000 + len(rows) * 7919 + attempts * 101 + sum(ord(c) for c in band)
            rng = np.random.default_rng(seed)
            table = g2.generate_table(3, 1, stratum, rng)
            digest = g2.table_digest(tuple(int(x) for x in table))
            if digest in seen:
                continue
            if not accept_band(table, band):
                continue
            seen.add(digest)
            rule_id = f"q3g5_{band[:2].lower()}_{accepted:05d}"
            spec = g2.RuleSpec("q3_radius1", rule_id, stratum, 3, 1, tuple(int(x) for x in table))
            row = structural_row(spec)
            row.update(
                {
                    "rule_id": rule_id,
                    "band_id": band,
                    "band_type": band_types[band],
                    "stratum": stratum,
                }
            )
            rows.append(row)
            accepted += 1
        print(f"sampled {band}: {accepted}", flush=True)
    return pd.DataFrame(rows)


def spec_from_row(row: pd.Series) -> g2.RuleSpec:
    return g3.spec_from_row(row)


def run_stage1(cfg: Config, manifest: pd.DataFrame) -> pd.DataFrame:
    gcfg = g3.Config(
        cfg.out_dir,
        Path("probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results"),
        Path("probe_DAX_G2b_control_adjusted_primitive_guardrail_results"),
        cfg.workers,
        1.0,
        cfg.stage1_n_seeds,
        cfg.stage1_T,
        cfg.stage1_ring,
        cfg.stage2_n_seeds,
        cfg.stage2_T,
        cfg.stage2_ring,
        300,
        cfg.stratum_nulls,
        cfg.diagram_count,
    )
    specs = [spec_from_row(row) for _, row in manifest.iterrows()]
    from concurrent.futures import ProcessPoolExecutor, as_completed

    rows: list[dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as ex:
        futures = [ex.submit(g3.eval_stage1, (spec, gcfg)) for spec in specs]
        for i, fut in enumerate(as_completed(futures), 1):
            rows.append(fut.result())
            if i % max(1, len(futures) // 20) == 0:
                print(f"stage1 {i}/{len(futures)}", flush=True)
    stage1 = pd.DataFrame(rows)
    return stage1.merge(manifest[["rule_id", "band_id", "band_type"]], on="rule_id", how="left")


def select_stage2(cfg: Config, stage1: pd.DataFrame, manifest: pd.DataFrame) -> pd.DataFrame:
    candidate_classes = {"localized_persistence", "transported_identity", "emitter_or_generator", "mixed"}
    candidate = stage1[stage1["classification"].isin(candidate_classes) & (stage1["stage1_score"] > 0)].copy()
    selected = []
    for band, group in candidate.groupby("band_id"):
        cap = max(cfg.stage2_min_per_band, int(round(cfg.stage2_cap_per_band * cfg.sample_scale)))
        ordered = group.sort_values(["stage1_score", "relation_asymmetry_priority"], ascending=False)
        selected.append(ordered.head(cap))
    if selected:
        selected_df = pd.concat(selected, ignore_index=True).drop_duplicates("rule_id")
    else:
        selected_df = stage1.sort_values(["stage1_score", "relation_asymmetry_priority"], ascending=False).head(1)
    return manifest[manifest["rule_id"].isin(selected_df["rule_id"])].copy()


def run_stage2_guardrail(cfg: Config, stage2_manifest: pd.DataFrame, manifest: pd.DataFrame, stage1: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    gcfg = g3.Config(
        cfg.out_dir,
        Path("probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results"),
        Path("probe_DAX_G2b_control_adjusted_primitive_guardrail_results"),
        cfg.workers,
        1.0,
        cfg.stage1_n_seeds,
        cfg.stage1_T,
        cfg.stage1_ring,
        cfg.stage2_n_seeds,
        cfg.stage2_T,
        cfg.stage2_ring,
        300,
        cfg.stratum_nulls,
        cfg.diagram_count,
    )
    adjusted, tables = g3.run_guardrail(stage2_manifest, manifest, stage1, gcfg)
    band_cols = manifest[["rule_id", "band_id", "band_type"]]
    adjusted = adjusted.merge(band_cols, on="rule_id", how="left")
    for key in ["raw_metrics", "metrics", "matched_control_metrics", "ic_family_dependence", "motif_mechanism_report", "motif_phase_sequences"]:
        if key in tables and "parent_rule_id" in tables[key].columns:
            tables[key] = tables[key].merge(band_cols.rename(columns={"rule_id": "parent_rule_id"}), on="parent_rule_id", how="left")
    return adjusted, tables


def primary_positive_mask(df: pd.DataFrame) -> pd.Series:
    return (
        (df["adjusted_persistence"] > 0)
        & (df["relation_load_bearing_adjusted"] > 0)
        & (df["asymmetry_load_bearing_adjusted"] > 0)
        & df["local_phase_fakeout_rejected"].fillna(False).astype(bool)
        & df["reclassification"].eq("control_adjusted_positive")
    )


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - half), min(1.0, center + half)


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    try:
        from scipy.stats import fisher_exact

        return float(fisher_exact([[a, b], [c, d]], alternative="greater").pvalue)
    except Exception:
        total = a + b + c + d
        if total == 0:
            return 1.0
        p1 = a / max(a + b, 1)
        p2 = c / max(c + d, 1)
        se = math.sqrt(max(p1 * (1 - p1) / max(a + b, 1) + p2 * (1 - p2) / max(c + d, 1), 1e-12))
        z = (p1 - p2) / se
        return float(0.5 * math.erfc(z / math.sqrt(2)))


def band_enrichment(adjusted: pd.DataFrame, manifest: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = manifest[["rule_id", "band_id", "band_type"]].merge(
        adjusted[["rule_id", "reclassification", "adjusted_persistence", "relation_load_bearing_adjusted", "asymmetry_load_bearing_adjusted", "local_phase_fakeout_rejected", "composition_adjusted_delta", "composition_emission_only_flag"]],
        on="rule_id",
        how="left",
    )
    df["primary_positive"] = False
    matched = df["reclassification"].notna()
    df.loc[matched, "primary_positive"] = primary_positive_mask(df[matched])
    df["stage2_evaluated"] = matched
    df["non_emission_composition_positive"] = (df["composition_adjusted_delta"].fillna(0) > 0) & ~df[
        "composition_emission_only_flag"
    ].fillna(False).astype(bool)

    rows = []
    for band, group in df.groupby("band_id"):
        n = int(len(group))
        k = int(group["primary_positive"].sum())
        lo, hi = wilson_ci(k, n)
        rows.append(
            {
                "band_id": band,
                "band_type": group["band_type"].iloc[0],
                "sampled_rule_count": n,
                "stage2_evaluated_count": int(group["stage2_evaluated"].sum()),
                "primary_positive_count": k,
                "primary_positive_rate": k / max(n, 1),
                "primary_positive_ci_low": lo,
                "primary_positive_ci_high": hi,
                "non_emission_composition_positive_count": int(group["non_emission_composition_positive"].sum()),
            }
        )
    band_df = pd.DataFrame(rows).sort_values(["band_type", "band_id"])

    fertile = df[df["band_type"].eq("fertile")]
    control = df[df["band_type"].eq("control")]
    fk = int(fertile["primary_positive"].sum())
    fn = int(len(fertile))
    ck = int(control["primary_positive"].sum())
    cn = int(len(control))
    tests = pd.DataFrame(
        [
            {
                "comparison": "fertile_vs_control_primary_positive",
                "fertile_positive_count": fk,
                "fertile_negative_count": fn - fk,
                "control_positive_count": ck,
                "control_negative_count": cn - ck,
                "fertile_rate": fk / max(fn, 1),
                "control_rate": ck / max(cn, 1),
                "relative_enrichment": (fk / max(fn, 1)) / max(ck / max(cn, 1), 1 / max(cn, 1)),
                "fisher_exact_greater_p": fisher_exact_two_sided(fk, fn - fk, ck, cn - ck),
            }
        ]
    )
    false_discovery = pd.DataFrame(
        [
            {
                "control_primary_positive_count": ck,
                "control_rule_count": cn,
                "control_primary_positive_rate": ck / max(cn, 1),
                "fertile_primary_positive_count": fk,
                "estimated_false_discovery_fraction": min(1.0, ck / max(fk, 1)),
            }
        ]
    )
    return band_df, tests, false_discovery


def composition_secondary(adjusted: pd.DataFrame) -> pd.DataFrame:
    out = adjusted[["rule_id", "band_id", "band_type", "composition_adjusted_delta", "composition_emission_only_flag", "dominant_interaction_outcome", "reclassification"]].copy()
    out["non_emission_composition_positive"] = (out["composition_adjusted_delta"] > 0) & ~out["composition_emission_only_flag"].fillna(False).astype(bool)
    out["primary_positive"] = primary_positive_mask(adjusted)
    out["new_motif_persistent"] = out["dominant_interaction_outcome"].eq("new_motif") & (adjusted["raw_persistence_score"] > 0.05)
    return out


def leaderboards(adjusted: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    scored = adjusted.copy()
    scored["primary_positive"] = primary_positive_mask(scored)
    scored["validation_score"] = (
        scored["adjusted_persistence"].fillna(0) * 3
        + scored["relation_load_bearing_adjusted"].fillna(0) * 2
        + scored["asymmetry_load_bearing_adjusted"].fillna(0) * 2
        + scored["local_phase_fakeout_rejected"].fillna(False).astype(int)
        + scored["composition_adjusted_delta"].clip(lower=0).fillna(0) * 0.25
    )
    validation = scored[scored["primary_positive"]].sort_values("validation_score", ascending=False)
    scored["discovery_score"] = (
        scored["raw_persistence_score"].fillna(0) * 2
        + scored["future_distinct_descendant_count_raw"].fillna(0) / 64.0
        + scored["composition_adjusted_delta"].clip(lower=0).fillna(0)
        + (~scored["primary_positive"]).astype(int) * 0.25
    )
    discovery = scored[~scored["primary_positive"]].sort_values("discovery_score", ascending=False)
    return validation, discovery


def make_plots(out: Path, adjusted: pd.DataFrame, band_df: pd.DataFrame, comp: pd.DataFrame) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return

    plt.figure(figsize=(11, 5))
    plt.bar(band_df["band_id"], band_df["primary_positive_rate"])
    plt.xticks(rotation=35, ha="right")
    plt.ylabel("primary positive rate")
    plt.tight_layout()
    plt.savefig(out / "heldout_positive_rate_by_band.png", dpi=160)
    plt.close()

    fc = band_df.groupby("band_type").agg(rate=("primary_positive_rate", "mean")).reset_index()
    plt.figure(figsize=(5, 4))
    plt.bar(fc["band_type"], fc["rate"])
    plt.ylabel("mean band positive rate")
    plt.tight_layout()
    plt.savefig(out / "fertile_vs_control_enrichment.png", dpi=160)
    plt.close()

    plt.figure(figsize=(6, 5))
    colors = adjusted["band_type"].map({"fertile": 1, "control": 0}).fillna(0)
    plt.scatter(adjusted["relation_load_bearing_adjusted"], adjusted["asymmetry_load_bearing_adjusted"], c=colors, s=30, alpha=0.75)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.axvline(0, color="black", linewidth=0.8)
    plt.xlabel("relation adjusted")
    plt.ylabel("asymmetry adjusted")
    plt.tight_layout()
    plt.savefig(out / "relation_asymmetry_heldout_scatter.png", dpi=160)
    plt.close()

    plt.figure(figsize=(11, 5))
    adjusted.boxplot(column="adjusted_persistence", by="band_id", rot=35)
    plt.suptitle("")
    plt.title("Adjusted persistence by band")
    plt.tight_layout()
    plt.savefig(out / "adjusted_persistence_heldout_by_band.png", dpi=160)
    plt.close()

    leak_pivot = pd.crosstab(adjusted["band_id"], adjusted["reclassification"])
    plt.figure(figsize=(10, 5))
    plt.imshow(leak_pivot.to_numpy(), aspect="auto", interpolation="nearest")
    plt.xticks(range(len(leak_pivot.columns)), leak_pivot.columns, rotation=45, ha="right")
    plt.yticks(range(len(leak_pivot.index)), leak_pivot.index)
    plt.colorbar(label="count")
    plt.tight_layout()
    plt.savefig(out / "control_leak_heatmap.png", dpi=160)
    plt.close()

    comp_band = comp.groupby("band_id")["non_emission_composition_positive"].mean().reset_index()
    plt.figure(figsize=(11, 5))
    plt.bar(comp_band["band_id"], comp_band["non_emission_composition_positive"])
    plt.xticks(rotation=35, ha="right")
    plt.ylabel("secondary composition positive rate")
    plt.tight_layout()
    plt.savefig(out / "composition_secondary_by_band.png", dpi=160)
    plt.close()


def make_spacetime_examples(cfg: Config, manifest: pd.DataFrame, validation: pd.DataFrame, discovery: pd.DataFrame, leaks: pd.DataFrame) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    d = cfg.out_dir / "spacetime_examples"
    d.mkdir(exist_ok=True)
    selections = [
        ("heldout_positive", validation.head(20)),
        ("heldout_control_leak", leaks),
        ("heldout_discovery", discovery.head(10)),
    ]
    for prefix, group in selections:
        for _, row in group.iterrows():
            mrow = manifest[manifest["rule_id"].eq(row["rule_id"])]
            if mrow.empty:
                continue
            spec = spec_from_row(mrow.iloc[0])
            hist = g2.simulate(spec, "short_random_active_block", 256, 256, 1, salt=701)[:, 0, :]
            plt.figure(figsize=(7, 5))
            plt.imshow(hist, aspect="auto", interpolation="nearest", cmap="viridis", vmin=0, vmax=2)
            plt.title(f"{prefix}: {spec.rule_id}")
            plt.xlabel("site")
            plt.ylabel("t")
            plt.tight_layout()
            plt.savefig(d / f"{prefix}_{spec.rule_id}.png", dpi=140)
            plt.close()


def build_summary(
    cfg: Config,
    t0: float,
    manifest: pd.DataFrame,
    adjusted: pd.DataFrame,
    band_df: pd.DataFrame,
    tests: pd.DataFrame,
    comp: pd.DataFrame,
    validation: pd.DataFrame,
) -> dict[str, object]:
    fertile = band_df[band_df["band_type"].eq("fertile")]
    control = band_df[band_df["band_type"].eq("control")]
    fertile_count = int(fertile["primary_positive_count"].sum())
    control_count = int(control["primary_positive_count"].sum())
    fertile_n = int(fertile["sampled_rule_count"].sum())
    control_n = int(control["sampled_rule_count"].sum())
    fertile_rate = fertile_count / max(fertile_n, 1)
    control_rate = control_count / max(control_n, 1)
    enrichment = fertile_rate / max(control_rate, 1 / max(control_n, 1))
    leak_df = adjusted[adjusted["band_type"].eq("control") & primary_positive_mask(adjusted)]
    bands_with_positives = int((fertile["primary_positive_count"] > 0).sum())
    passed = bool(enrichment >= 3 and fertile_count >= 5 and len(leak_df) <= 1)
    strong = bool(enrichment >= 5 and fertile_count >= 10 and len(leak_df) == 0 and bands_with_positives >= 2)
    recommendation = "G5 failed: G3/G4 ecology did not yield a predictive held-out detector. Return to ecology/anatomy without modifying the frozen detector."
    next_probe = "DAX_G4b_or_detector_rethink"
    if strong:
        recommendation = "G5 strong pass: keep q3/r1_DAR_persistence_v1 frozen and move to cross-seed replication or adjacent-substrate transfer."
        next_probe = "DAX_G6_cross_seed_replication_or_adjacent_transfer"
    elif passed:
        recommendation = "G5 operational pass: repeat held-out q3/r1 with the same frozen detector and larger sample before broader claims."
        next_probe = "DAX_G5b_larger_heldout_replication"

    return {
        "probe": PROBE,
        "status": "COMPLETE",
        "runtime_seconds": round(time.time() - t0, 3),
        "detector_freeze": {
            "written": True,
            "path": "detector_freeze.json",
            "frozen_before_heldout": True,
            "post_freeze_metric_changes": False,
        },
        "preregistration": {
            "written": True,
            "path": str(PREREG_NOTE).replace("\\", "/"),
            "written_before_heldout": True,
            "explicit_non_claims_included": True,
        },
        "heldout_sampling": {
            "total_rules": int(len(manifest)),
            "fertile_rules": int((manifest["band_type"] == "fertile").sum()),
            "control_rules": int((manifest["band_type"] == "control").sum()),
            "bands": band_df.to_dict(orient="records"),
        },
        "primary_result": {
            "heldout_prediction_passed": passed,
            "heldout_prediction_strong_passed": strong,
            "fertile_primary_positive_count": fertile_count,
            "control_primary_positive_count": control_count,
            "fertile_primary_positive_rate": fertile_rate,
            "control_primary_positive_rate": control_rate,
            "fertile_vs_control_enrichment": enrichment,
            "control_leak_count": int(len(leak_df)),
            "bands_with_positives": bands_with_positives,
        },
        "band_results": band_df.to_dict(orient="records"),
        "secondary_composition": {
            "non_emission_composition_positive_count": int(comp["non_emission_composition_positive"].sum()),
            "new_motif_persistent_count": int(comp["new_motif_persistent"].sum()),
            "composition_overlap_with_primary_count": int((comp["non_emission_composition_positive"] & comp["primary_positive"]).sum()),
        },
        "top_heldout_positives": validation.head(20).to_dict(orient="records"),
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": [
            "Stage 2 candidates are capped per band for runtime; unevaluated Stage 1 candidates count as non-positive for rate estimates."
        ],
    }


def main() -> None:
    args = parse_args()
    cfg = Config(
        args.out_dir,
        args.g3_dir,
        args.g4_dir,
        args.workers,
        args.sample_scale,
        args.stage1_n_seeds,
        args.stage1_T,
        args.stage1_ring,
        args.stage2_n_seeds,
        args.stage2_T,
        args.stage2_ring,
        args.stage2_cap_per_band,
        args.stage2_min_per_band,
        args.stratum_nulls,
        args.diagram_count,
    )
    t0 = time.time()
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True)

    write_phase0_artifacts(cfg)
    manifest = build_heldout_manifest(cfg)
    manifest.to_csv(cfg.out_dir / "heldout_rule_manifest.csv", index=False)

    stage1 = run_stage1(cfg, manifest)
    stage1.to_csv(cfg.out_dir / "heldout_stage1_scan_metrics.csv", index=False)
    stage1[["rule_id", "band_id", "band_type", "stratum", "classification", "stage1_score", "relation_asymmetry_priority"]].to_csv(
        cfg.out_dir / "heldout_stage1_classification.csv", index=False
    )

    stage2_manifest = select_stage2(cfg, stage1, manifest)
    stage2_manifest.to_csv(cfg.out_dir / "heldout_stage2_candidate_manifest.csv", index=False)
    adjusted, tables = run_stage2_guardrail(cfg, stage2_manifest, manifest, stage1)
    adjusted.to_csv(cfg.out_dir / "heldout_control_adjusted_metrics.csv", index=False)
    adjusted[["rule_id", "band_id", "band_type", "stratum", "target_role", "reclassification"]].to_csv(
        cfg.out_dir / "heldout_reclassification_results.csv", index=False
    )
    for key, name in [
        ("raw_metrics", "heldout_stage2_raw_metrics.csv"),
        ("matched_control_metrics", "heldout_matched_control_metrics.csv"),
        ("matched_control_manifest", "heldout_matched_control_manifest.csv"),
        ("matched_control_fairness_audit", "heldout_matched_control_fairness_audit.csv"),
        ("ic_family_dependence", "heldout_ic_family_dependence.csv"),
        ("motif_mechanism_report", "heldout_motif_mechanism_report.csv"),
    ]:
        if key in tables:
            tables[key].to_csv(cfg.out_dir / name, index=False)

    comp = composition_secondary(adjusted)
    comp.to_csv(cfg.out_dir / "heldout_composition_secondary.csv", index=False)
    band_df, tests, false_discovery = band_enrichment(adjusted, manifest)
    band_df.to_csv(cfg.out_dir / "heldout_band_enrichment.csv", index=False)
    tests.to_csv(cfg.out_dir / "heldout_statistical_tests.csv", index=False)
    false_discovery.to_csv(cfg.out_dir / "heldout_false_discovery_estimate.csv", index=False)

    control_leaks = adjusted[adjusted["band_type"].eq("control") & primary_positive_mask(adjusted)].copy()
    control_leaks.to_csv(cfg.out_dir / "control_leak_report.csv", index=False)
    validation, discovery = leaderboards(adjusted)
    validation.to_csv(cfg.out_dir / "validation_leaderboard_heldout.csv", index=False)
    discovery.to_csv(cfg.out_dir / "discovery_leaderboard_heldout.csv", index=False)
    pd.DataFrame(
        [
            {
                "warning": "Stage 2 candidates are capped per band for runtime; unevaluated Stage 1 candidates count as non-positive for rate estimates.",
                "workers": cfg.workers,
                "sample_scale": cfg.sample_scale,
                "stage2_candidate_count": int(len(stage2_manifest)),
            }
        ]
    ).to_csv(cfg.out_dir / "estimator_report.csv", index=False)

    make_plots(cfg.out_dir, adjusted, band_df, comp)
    make_spacetime_examples(cfg, manifest, validation, discovery, control_leaks)

    summary = build_summary(cfg, t0, manifest, adjusted, band_df, tests, comp, validation)
    clean = g2.json_sanitize(summary)
    (cfg.out_dir / "summary.json").write_text(json.dumps(clean, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(clean, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
