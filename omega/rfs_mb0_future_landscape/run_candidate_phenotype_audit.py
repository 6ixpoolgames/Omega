from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path
from statistics import mean

from .relation_generator import (
    RelationParams,
    _bias,
    _bias_weights,
    _build_edges,
    _candidate_successors,
    _constraint_profile,
    _constraint_violation,
    _generate_constraints,
    _relation_score,
    _stable_hash,
    generate_relation_system,
)


TRIVIALITY_NULLS = (
    "frontier_size_only",
    "probe_marginal_only",
    "frontier_size_plus_probe_marginal",
)
SUPPORT_NULLS = (
    "signature_support_matched",
    "horizon_local_frontier_matched",
    "window_local_frontier_matched",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a small RFS-MB0 candidate phenotype audit.")
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_candidate_phenotype_audit_sanity"))
    parser.add_argument("--parameter-region-file", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_breadth_null_repair_ranked_real/confirmatory_regions_preregistered.json"))
    parser.add_argument("--parameter-samples", type=int, default=8)
    parser.add_argument("--seeds-per-parameter-set", type=int, default=1)
    parser.add_argument("--start-samples-list", type=str, default="1,3,8")
    parser.add_argument("--null-replicates", type=int, default=1)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=3300)
    parser.add_argument("--per-stage-runtime-seconds", type=int, default=900)
    parser.add_argument("--stress-sample-count", type=int, default=80)
    parser.add_argument("--score-edge-sample", type=int, default=160)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    start_counts = [int(item.strip()) for item in args.start_samples_list.split(",") if item.strip()]
    stage_dirs = []
    notes = []
    for start_count in start_counts:
        remaining = args.max_runtime_seconds - (time.perf_counter() - started)
        if remaining < 180:
            notes.append(f"Skipped start_samples={start_count}; remaining wall clock too small.")
            continue
        stage_dir = args.out / f"start_samples_{start_count}"
        stage_dirs.append(stage_dir)
        status = _run_atlas_stage(args, stage_dir, start_count, min(args.per_stage_runtime_seconds, int(remaining) - 60))
        notes.append(f"start_samples={start_count}: {status.get('status', 'missing_status')} jobs={status.get('jobs_completed', 0)}/{status.get('jobs_created', 0)}")
    phenotype_rows = write_candidate_phenotypes(stage_dirs, args.out / "candidate_phenotype_summary.csv", args.stress_sample_count)
    write_phenotype_reproducibility(phenotype_rows, args.out / "phenotype_reproducibility_summary.csv")
    write_score_term_decomposition(stage_dirs, args.out, args.score_edge_sample)
    write_summary(args.out, started, args, stage_dirs, phenotype_rows, notes)


def _run_atlas_stage(args: argparse.Namespace, stage_dir: Path, start_count: int, runtime_seconds: int) -> dict[str, object]:
    stage_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "omega.rfs_mb0_future_landscape.run_relation_atlas",
        "--out",
        str(stage_dir),
        "--parameter-region-file",
        str(args.parameter_region_file),
        "--parameter-region-mode",
        "core_only",
        "--parameter-samples",
        str(args.parameter_samples),
        "--seeds-per-parameter-set",
        str(args.seeds_per_parameter_set),
        "--coordinate-counts",
        "5",
        "--max-state-count",
        "300",
        "--horizon-grid",
        "long_5x",
        "--workers",
        str(args.workers),
        "--start-samples",
        str(start_count),
        "--null-replicates",
        str(args.null_replicates),
        "--max-runtime-seconds",
        str(max(60, runtime_seconds)),
    ]
    result = subprocess.run(command, cwd=Path.cwd(), check=False)
    status_path = stage_dir / "relation_atlas_status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {"status": "MISSING_STATUS"}
    status["subprocess_returncode"] = result.returncode
    return status


def write_candidate_phenotypes(stage_dirs: list[Path], out_path: Path, limit: int) -> list[dict[str, object]]:
    raw_rows = []
    for stage_dir in stage_dirs:
        start_count = int(stage_dir.name.rsplit("_", 1)[-1])
        windows = _read_csv(stage_dir / "relation_atlas_window_summary.csv")
        profiles = _read_csv(stage_dir / "horizon_local_profiles.csv")
        transitions = _read_csv(stage_dir / "transition_information.csv")
        metrics = _window_metric_lookup(profiles, transitions)
        candidates = [
            row for row in windows
            if row.get("aggregate_window_class_v1_2") == "structured_candidate_window"
            and row.get("window") in {"early_window", "pre_saturation_window"}
        ]
        candidates.sort(key=lambda row: float(row.get("mean_transition_MI_H", 0.0)) + float(row.get("mean_JS_to_null_H", 0.0)), reverse=True)
        for row in candidates[:limit]:
            key = (row["family"], row["probe_family"], row["window"])
            metric = metrics.get(key, {})
            raw_rows.append(_phenotype_row(row, metric, start_count))
    recurrence = _candidate_recurrence(raw_rows)
    for row in raw_rows:
        row["start_coverage_class"] = recurrence.get(str(row["candidate_key"]), "start_local")
        row["phenotype_class"] = _phenotype_class(row)
        row["phenotype_confidence"] = _phenotype_confidence(row)
        row["recommended_followup"] = _recommended_followup(row)
    _write_csv(out_path, raw_rows)
    return raw_rows


def _phenotype_row(row: dict[str, str], metric: dict[str, object], start_count: int) -> dict[str, object]:
    candidate_key = f"{row['family']}|{row['probe_family']}|{row['window']}"
    trivial_frontier = _control_result(metric, "frontier_size_only")
    trivial_probe = _control_result(metric, "probe_marginal_only")
    trivial_plus = _control_result(metric, "frontier_size_plus_probe_marginal")
    support = _support_result(metric)
    constraint = _dependency_class(metric, "constraint_shuffled")
    asymmetry = _dependency_class(metric, "asymmetry_shuffled")
    roughness = _roughness_class(metric)
    path_class = _path_process_class(row, metric)
    near_tie = int(float(metric.get("mean_transition_MI_H", row.get("mean_transition_MI_H", 0.0))) > 0.25 and support == "support_deformation")
    return {
        "candidate_id": f"{candidate_key}|starts{start_count}",
        "candidate_key": candidate_key,
        "environment_id": row["family"],
        "parameter_set_id": metric.get("parameter_set_id", ""),
        "start_id": f"aggregate_start_samples_{start_count}",
        "start_samples": start_count,
        "window_name": row["window"],
        "probe_family": row["probe_family"],
        "horizon_range": row["window"],
        "triviality_frontier_size_result": trivial_frontier,
        "triviality_probe_marginal_result": trivial_probe,
        "triviality_frontier_plus_probe_result": trivial_plus,
        "support_matched_result": support,
        "constraint_dependency_class": constraint,
        "asymmetry_dependency_class": asymmetry,
        "roughness_response_class": roughness,
        "start_coverage_class": "",
        "path_process_class": path_class,
        "degree_outdegree_ablation_result": _degree_result(metric),
        "shuffle_survivor_audit_required": int(constraint == "shuffle_survivor" or asymmetry == "shuffle_survivor"),
        "roughness_brittle_flag": int(roughness == "roughness_brittle"),
        "near_tie_dominated_flag": near_tie,
        "lockin_prone_flag": int(float(row.get("saturation_fraction", 0.0)) > 0.25),
        "phenotype_class": "",
        "phenotype_confidence": "",
        "recommended_followup": "",
    }


def _control_result(metric: dict[str, object], null_name: str) -> str:
    js_rank = float(metric.get(f"JS_rank_against_replicates_{null_name}", 0.0))
    mi_rank = float(metric.get(f"MI_rank_against_replicates_{null_name}", 0.0))
    motif_rank = float(metric.get(f"motif_rank_against_replicates_{null_name}", 0.0))
    if max(js_rank, mi_rank, motif_rank) > 0:
        return "survives_ranked" if js_rank >= 0.8 and mi_rank >= 0.8 and motif_rank >= 0.8 else "explained_or_weak_rank"
    js = float(metric.get(f"JS_to_null_{null_name}", 0.0))
    mi = float(metric.get(f"MI_delta_vs_null_{null_name}", 0.0))
    motif = float(metric.get(f"motif_delta_vs_null_{null_name}", 0.0))
    return "survives_threshold" if js > 0.05 and mi > 0 and motif > 0 else "explained_or_weak_threshold"


def _support_result(metric: dict[str, object]) -> str:
    survived = sum(_control_result(metric, null_name).startswith("survives") for null_name in SUPPORT_NULLS)
    if survived == len(SUPPORT_NULLS):
        return "beyond_support_matched"
    if survived > 0:
        return "mixed_support_deformation"
    return "support_deformation"


def _dependency_class(metric: dict[str, object], null_name: str) -> str:
    result = _control_result(metric, null_name)
    return "shuffle_survivor" if result.startswith("survives") else "mechanism_dependent"


def _roughness_class(metric: dict[str, object]) -> str:
    result = _control_result(metric, "roughness_resampled")
    if result.startswith("survives"):
        return "noise_tolerant"
    return "roughness_brittle"


def _degree_result(metric: dict[str, object]) -> str:
    degree = _control_result(metric, "degree_preserving_rewire")
    out_degree = _control_result(metric, "out_degree_preserving_random")
    if degree.startswith("survives") and out_degree.startswith("survives"):
        return "survives_out_degree_ablations"
    if degree.startswith("survives") or out_degree.startswith("survives"):
        return "mixed_out_degree_ablation"
    return "killed_by_out_degree_ablation"


def _path_process_class(row: dict[str, str], metric: dict[str, object]) -> str:
    mi = float(row.get("mean_transition_MI_H", metric.get("mean_transition_MI_H", 0.0)))
    motif = float(row.get("mean_transition_motif_reuse_H", metric.get("mean_transition_motif_reuse_H", 0.0)))
    if mi > 0.35 and motif > 0.25:
        return "transition_process_candidate"
    if mi > 0.25:
        return "distribution_deformation_candidate"
    return "support_deformation_candidate"


def _candidate_recurrence(rows: list[dict[str, object]]) -> dict[str, str]:
    grouped: dict[str, set[int]] = {}
    for row in rows:
        grouped.setdefault(str(row["candidate_key"]), set()).add(int(row["start_samples"]))
    out = {}
    for key, starts in grouped.items():
        if {1, 3, 8}.issubset(starts):
            out[key] = "environment_level"
        elif len(starts) >= 2:
            out[key] = "basin_local"
        elif 1 in starts:
            out[key] = "start_fragile"
        else:
            out[key] = "start_local"
    return out


def _phenotype_class(row: dict[str, object]) -> str:
    if row["roughness_response_class"] == "roughness_brittle":
        return "roughness_brittle_artifact"
    if row["degree_outdegree_ablation_result"] == "killed_by_out_degree_ablation":
        return "generic_branching_artifact"
    if row["support_matched_result"] == "support_deformation":
        return f"support_only_{row['start_coverage_class']}"
    if row["constraint_dependency_class"] == "mechanism_dependent":
        return f"constraint_dependent_{row['start_coverage_class']}"
    if row["asymmetry_dependency_class"] == "mechanism_dependent":
        return f"asymmetry_dependent_{row['start_coverage_class']}"
    if row["path_process_class"] == "transition_process_candidate":
        return "path_process_candidate"
    return "underdetermined"


def _phenotype_confidence(row: dict[str, object]) -> str:
    if row["start_coverage_class"] == "environment_level" and not int(row["roughness_brittle_flag"]):
        return "medium"
    if row["start_coverage_class"] in {"basin_local", "environment_level"}:
        return "low_medium"
    return "low"


def _recommended_followup(row: dict[str, object]) -> str:
    if row["roughness_brittle_flag"]:
        return "inspect top-k margins and roughness-decisive edges"
    if row["start_coverage_class"] == "start_fragile":
        return "increase starts before interpreting phenotype"
    if row["support_matched_result"] == "support_deformation":
        return "test path/process diagnostics on same environment"
    return "repeat with roughness strength sweep"


def write_phenotype_reproducibility(rows: list[dict[str, object]], out_path: Path) -> None:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        region = _region_id(str(row.get("parameter_set_id", "")))
        grouped.setdefault((region, str(row["phenotype_class"])), []).append(row)
    out = []
    for (region, phenotype), items in sorted(grouped.items()):
        out.append(
            {
                "parameter_region_id": region,
                "phenotype_class": phenotype,
                "n_candidate_rows": len(items),
                "n_environments": len({str(row["environment_id"]) for row in items}),
                "phenotype_recurrence_rate_across_starts": mean(int(row["start_coverage_class"] in {"basin_local", "environment_level"}) for row in items),
                "phenotype_recurrence_rate_across_probe_families": len({str(row["probe_family"]) for row in items}) / 3.0,
                "roughness_brittle_rate": mean(int(row["roughness_brittle_flag"]) for row in items),
                "path_process_rate": mean(int(row["path_process_class"] == "transition_process_candidate") for row in items),
            }
        )
    _write_csv(out_path, out)


def write_score_term_decomposition(stage_dirs: list[Path], out_dir: Path, edge_sample: int) -> None:
    metadata_rows = []
    for stage_dir in stage_dirs:
        metadata_rows.extend(_read_csv(stage_dir / "generated_environment_metadata.csv"))
    seen = set()
    rows = []
    for metadata in metadata_rows:
        env_id = metadata["environment_id"]
        if env_id in seen:
            continue
        seen.add(env_id)
        params = _params_from_metadata(metadata)
        system = generate_relation_system(params, int(metadata["seed"]))
        rows.extend(_score_rows_for_system(system, params, edge_sample // max(1, len(metadata_rows))))
        if len(rows) >= edge_sample:
            break
    rows = rows[:edge_sample]
    _write_csv(out_dir / "score_term_decomposition.csv", rows)
    _write_csv(out_dir / "top_k_margin_summary.csv", _top_k_margin_summary(rows))
    _write_csv(out_dir / "roughness_decisive_edges.csv", [row for row in rows if int(row["roughness_decisive_flag"])])
    _write_csv(out_dir / "constraint_vs_asymmetry_dominance.csv", _dominance_summary(rows))
    _write_csv(out_dir / "constraint_profile_summary.csv", _constraint_profile_summary(rows))
    _write_csv(out_dir / "constraint_scope_overlap_summary.csv", [{"status": "not_implemented_in_sanity_sweep", "n_score_rows": len(rows)}])


def _score_rows_for_system(system: object, params: RelationParams, per_system_limit: int) -> list[dict[str, object]]:
    constraints = json.loads(str(system.metadata["constraint_json"]))  # type: ignore[attr-defined]
    bias_weights = _bias_weights(params, int(system.seed), "base")  # type: ignore[attr-defined]
    rough_seed = int(system.seed)  # type: ignore[attr-defined]
    rows = []
    for source in list(system.states)[: max(1, per_system_limit)]:  # type: ignore[attr-defined]
        candidates = _candidate_successors(source, params.alphabet_size, params.update_footprint)
        scored = [_score_terms(source, target, constraints, bias_weights, params, rough_seed) for target in candidates]
        scored.sort(key=lambda item: (float(item["total_score"]), str(item["target_state"])))
        cutoff_index = min(params.out_degree_target - 1, len(scored) - 1)
        cutoff = float(scored[cutoff_index]["total_score"]) if scored else 0.0
        next_score = float(scored[params.out_degree_target]["total_score"]) if len(scored) > params.out_degree_target else cutoff
        selected = set(system.edges[source])  # type: ignore[attr-defined]
        for rank, term_row in enumerate(scored[: params.out_degree_target + 2]):
            total = float(term_row["total_score"])
            row = {
                "environment_id": system.system_id,  # type: ignore[attr-defined]
                "parameter_set_id": params.parameter_set_id,
                "source_state": str(source),
                "target_state": str(term_row["target_state"]),
                "selected_edge": int(term_row["target_state"] in selected),
                "candidate_rank": rank,
                "score_margin_to_next": float(scored[rank + 1]["total_score"]) - total if rank + 1 < len(scored) else 0.0,
                "score_margin_to_cutoff": cutoff - total,
                "near_tie_flag": int(abs(next_score - cutoff) <= max(0.001, params.roughness_strength)),
                "roughness_decisive_flag": int(abs(next_score - cutoff) <= abs(float(term_row["roughness_term"]))),
                **{key: value for key, value in term_row.items() if key != "target_state"},
            }
            rows.append(row)
    return rows


def _score_terms(source: tuple[int, ...], target: tuple[int, ...], constraints: list[dict[str, object]], bias_weights: tuple[float, ...], params: RelationParams, rough_seed: int) -> dict[str, object]:
    change = sum(int(left != right) for left, right in zip(source, target))
    violation = _constraint_violation(target, constraints)
    source_profile = _constraint_profile(source, constraints)
    target_profile = _constraint_profile(target, constraints)
    profile_change = sum(abs(left - right) for left, right in zip(source_profile, target_profile))
    asymmetry_raw = _bias(target, bias_weights) - _bias(source, bias_weights)
    roughness_raw = (_stable_hash(f"{rough_seed}:{source}:{target}") % 10_000) / 10_000.0
    return {
        "target_state": target,
        "total_score": _relation_score(source, target, constraints, bias_weights, params, rough_seed),
        "change_term": change,
        "constraint_violation_term": violation,
        "constraint_change_term": params.constraint_change_weight * profile_change,
        "asymmetry_term": params.asymmetry_strength * asymmetry_raw,
        "roughness_term": params.roughness_strength * roughness_raw,
    }


def _top_k_margin_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = [row for row in rows if int(row["selected_edge"])]
    return [
        {
            "n_selected_edges": len(selected),
            "near_tie_rate": mean(int(row["near_tie_flag"]) for row in selected) if selected else 0.0,
            "roughness_decisive_edge_fraction": mean(int(row["roughness_decisive_flag"]) for row in selected) if selected else 0.0,
            "mean_score_margin_to_next": mean(float(row["score_margin_to_next"]) for row in selected) if selected else 0.0,
            "mean_score_margin_to_cutoff": mean(float(row["score_margin_to_cutoff"]) for row in selected) if selected else 0.0,
        }
    ]


def _dominance_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = [row for row in rows if int(row["selected_edge"])]
    if not selected:
        return []
    return [
        {
            "constraint_term_dominance": mean(abs(float(row["constraint_violation_term"])) + abs(float(row["constraint_change_term"])) for row in selected),
            "asymmetry_term_dominance": mean(abs(float(row["asymmetry_term"])) for row in selected),
            "roughness_term_dominance": mean(abs(float(row["roughness_term"])) for row in selected),
            "dominance_class": _dominance_class(selected),
        }
    ]


def _dominance_class(rows: list[dict[str, object]]) -> str:
    constraint = mean(abs(float(row["constraint_violation_term"])) + abs(float(row["constraint_change_term"])) for row in rows)
    asymmetry = mean(abs(float(row["asymmetry_term"])) for row in rows)
    roughness = mean(abs(float(row["roughness_term"])) for row in rows)
    if roughness >= max(constraint, asymmetry):
        return "roughness_dominated"
    if asymmetry >= constraint:
        return "asymmetry_dominated"
    return "constraint_dominated"


def _constraint_profile_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = [row for row in rows if int(row["selected_edge"])]
    return [
        {
            "n_selected_edges": len(selected),
            "mean_constraint_violation_term": mean(float(row["constraint_violation_term"]) for row in selected) if selected else 0.0,
            "mean_constraint_change_term": mean(float(row["constraint_change_term"]) for row in selected) if selected else 0.0,
            "constraint_conflict_proxy_rate": mean(float(row["constraint_violation_term"]) > 0 for row in selected) if selected else 0.0,
        }
    ]


def write_summary(out_dir: Path, started: float, args: argparse.Namespace, stage_dirs: list[Path], phenotype_rows: list[dict[str, object]], notes: list[str]) -> None:
    status_rows = []
    for stage_dir in stage_dirs:
        status_path = stage_dir / "relation_atlas_status.json"
        if status_path.exists():
            status_rows.append((stage_dir.name, json.loads(status_path.read_text(encoding="utf-8"))))
    phenotype_counts = _counts(row["phenotype_class"] for row in phenotype_rows)
    start_counts = _counts(row["start_coverage_class"] for row in phenotype_rows)
    lines = [
        "# RFS-MB0 Candidate Phenotype Audit Sanity Sweep",
        "",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Parameter samples per start pass: {args.parameter_samples}",
        f"- Null replicates: {args.null_replicates}",
        f"- Candidate phenotype rows: {len(phenotype_rows)}",
        "",
        "## Stage Status",
        "",
        "| stage | status | jobs | environments | middle | gate passes |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name, status in status_rows:
        lines.append(f"| {name} | {status.get('status', '')} | {status.get('jobs_completed', 0)}/{status.get('jobs_created', 0)} | {status.get('generated_environments_completed', 0)} | {status.get('middle_regime_environments', 0)} | {status.get('atlas_gate_pass_count', 0)} |")
    lines.extend(["", "## Start Coverage", "", "| class | n |", "|---|---:|"])
    for key, count in sorted(start_counts.items()):
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Phenotype Classes", "", "| class | n |", "|---|---:|"])
    for key, count in sorted(phenotype_counts.items()):
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Claim Boundary", "", "This is a tiny sanity audit of candidate phenotypes, not a scientific gate pass."])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "status.json").write_text(json.dumps({"status": "COMPLETED", "wall_clock_seconds": time.perf_counter() - started, "candidate_phenotype_rows": len(phenotype_rows)}, indent=2), encoding="utf-8")


def _window_metric_lookup(profile_rows: list[dict[str, str]], transition_rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, object]]:
    transition_by_key = {(row["environment_id"], row["probe_name"], row["H"]): row for row in transition_rows}
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in profile_rows:
        h = int(row["H"])
        for window in _windows_for_row(row, h):
            merged = {**row, **transition_by_key.get((row["environment_id"], row["probe_name"], row["H"]), {})}
            grouped.setdefault((row["environment_id"], row["probe_family"], window), []).append(merged)
    out: dict[tuple[str, str, str], dict[str, object]] = {}
    for key, items in grouped.items():
        metrics: dict[str, object] = {"parameter_set_id": items[0].get("parameter_set_id", "")}
        metric_keys = sorted({metric for row in items for metric in row if metric.startswith(("JS_to_null_", "KL_to_null_", "MI_delta_vs_null_", "motif_delta_vs_null_", "JS_rank_against_replicates_", "KL_rank_against_replicates_", "MI_rank_against_replicates_", "motif_rank_against_replicates_"))})
        metric_keys.extend(["signature_transition_MI_by_h", "signature_transition_motif_reuse_by_h"])
        for metric in metric_keys:
            metrics[metric] = _mean(row.get(metric, "") for row in items)
        out[key] = metrics
    return out


def _windows_for_row(row: dict[str, str], h: int) -> list[str]:
    reach_sat = float(row.get("reach_saturation_fraction_H", 0.0))
    windows = []
    if h <= 4:
        windows.append("early_window")
    if reach_sat < 0.95:
        windows.append("pre_saturation_window")
    if 0.75 <= reach_sat < 0.95:
        windows.append("near_saturation_window")
    if reach_sat >= 0.95:
        windows.append("post_saturation_window")
    return windows or ["undetermined_window"]


def _params_from_metadata(row: dict[str, str]) -> RelationParams:
    metadata = json.loads(row["metadata_json"])
    params = RelationParams(
        parameter_set_id=str(metadata["parameter_set_id"]),
        coordinate_count=int(metadata["coordinate_count"]),
        alphabet_size=int(metadata["alphabet_size"]),
        neighborhood_radius=int(metadata["neighborhood_radius"]),
        update_footprint=int(metadata["update_footprint"]),
        out_degree_target=int(metadata["out_degree_target"]),
        constraint_density=float(metadata["constraint_density"]),
        constraint_strength=float(metadata["constraint_strength"]),
        asymmetry_strength=float(metadata["asymmetry_strength"]),
        reversibility_fraction=float(metadata["reversibility_fraction"]),
        rewire_probability=float(metadata["rewire_probability"]),
        roughness_strength=float(metadata.get("roughness_strength", 0.01)),
        constraint_arity=int(metadata.get("constraint_arity", 2)),
        constraint_change_weight=float(metadata.get("constraint_change_weight", 0.35)),
    )
    return replace(params, parameter_set_id=str(row.get("parameter_set_id", params.parameter_set_id)))


def _region_id(parameter_set_id: str) -> str:
    parts = parameter_set_id.split("_")
    keep = [part for part in parts if part.startswith(("m", "k", "cd", "cs", "as", "rev", "rw"))]
    return "_".join(keep) if keep else parameter_set_id


def _mean(values: object) -> float:
    nums = []
    for value in values:  # type: ignore[union-attr]
        if value in {"", None}:
            continue
        nums.append(float(value))
    return mean(nums) if nums else 0.0


def _counts(values: object) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:  # type: ignore[union-attr]
        out[str(value)] = out.get(str(value), 0) + 1
    return out


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
