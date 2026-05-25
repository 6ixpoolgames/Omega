from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean

PARAMETERS = (
    "update_footprint",
    "out_degree_target",
    "constraint_density",
    "constraint_strength",
    "asymmetry_strength",
    "reversibility_fraction",
    "rewire_probability",
    "constraint_arity",
)

INTERACTIONS = (
    ("out_degree_target", "constraint_density"),
    ("out_degree_target", "reversibility_fraction"),
    ("update_footprint", "constraint_strength"),
    ("constraint_density", "constraint_strength"),
    ("asymmetry_strength", "reversibility_fraction"),
    ("rewire_probability", "constraint_strength"),
    ("constraint_arity", "constraint_density"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run staged RFS-MB0 relation-atlas batch.")
    parser.add_argument("--root-out", type=Path, default=Path("results/rfs_mb0_relation_atlas"))
    parser.add_argument("--existing-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260523_action_generated_v0_n5_calibration"))
    parser.add_argument("--global-wall-clock-seconds", type=int, default=17_400)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--stage-b-samples", type=int, default=200)
    parser.add_argument("--stage-c-samples", type=int, default=150)
    parser.add_argument("--stage-c-seeds", type=int, default=2)
    parser.add_argument("--stage-d-samples", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.root_out.mkdir(parents=True, exist_ok=True)
    completed: list[str] = []
    partial: list[str] = []
    notes: list[str] = []

    stage_a_dir = args.root_out / "5h_stage_a_existing_trends"
    stage_a_dir.mkdir(parents=True, exist_ok=True)
    if args.existing_run.exists():
        write_parameter_trends(args.existing_run, stage_a_dir / "parameter_trends_existing.csv", stage_a_dir / "parameter_trends_existing.md")
        completed.append("A")
    else:
        notes.append(f"Stage A skipped; existing run not found: {args.existing_run}")
        partial.append("A")

    stage_b = args.root_out / "repair_stage_b_broad_n5"
    if _time_left(started, args.global_wall_clock_seconds) > 900:
        status = _run_stage(
            stage_b,
            [
                "--parameter-samples", str(args.stage_b_samples),
                "--seeds-per-parameter-set", "1",
                "--coordinate-counts", "5",
                "--max-state-count", "300",
                "--horizon-grid", "long_10x",
                "--workers", str(args.workers),
                "--max-runtime-seconds", str(min(5400, _time_left(started, args.global_wall_clock_seconds) - 900)),
            ],
        )
        _copy_stage_outputs(stage_b, "stage_b")
        write_parameter_trends(stage_b, stage_b / "stage_b_parameter_trends.csv", stage_b / "stage_b_parameter_trends.md")
        write_interaction_trends(stage_b, stage_b / "parameter_interaction_trends.csv", stage_b / "parameter_interaction_trends.md")
        completed_or_partial("B", status, completed, partial)

    core_region_file = args.root_out / "repair_stage_c_core_regions.json"
    broad_region_file = args.root_out / "repair_stage_c_broad_regions.json"
    source_for_regions = stage_b if stage_b.exists() else args.existing_run
    core_regions, broad_regions = select_middle_regions(source_for_regions, core_region_file, broad_region_file)
    notes.append(f"Selected {len(core_regions)} core and {len(broad_regions)} broad Stage C parameter regions from {source_for_regions}.")

    stage_c = args.root_out / "repair_stage_c_core_n5"
    if core_regions and _time_left(started, args.global_wall_clock_seconds) > 900:
        status = _run_stage(
            stage_c,
            [
                "--parameter-region-file", str(core_region_file),
                "--parameter-region-mode", "core_only",
                "--parameter-samples", str(args.stage_c_samples),
                "--seeds-per-parameter-set", str(args.stage_c_seeds),
                "--coordinate-counts", "5",
                "--max-state-count", "300",
                "--horizon-grid", "long_10x",
                "--workers", str(args.workers),
                "--max-runtime-seconds", str(min(5400, _time_left(started, args.global_wall_clock_seconds) - 900)),
                "--parameter-seed", "20260524",
            ],
        )
        _copy_stage_outputs(stage_c, "stage_c")
        write_parameter_trends(stage_c, stage_c / "stage_c_parameter_trends.csv", stage_c / "stage_c_parameter_trends.md")
        write_interaction_trends(stage_c, stage_c / "parameter_interaction_trends.csv", stage_c / "parameter_interaction_trends.md")
        write_confirmed_middle_regions(stage_c, stage_c / "stage_c_confirmed_middle_regime_regions.csv")
        completed_or_partial("C", status, completed, partial)

    stage_d = args.root_out / "repair_stage_d_core_n6"
    if core_regions and _time_left(started, args.global_wall_clock_seconds) > 3600:
        status = _run_stage(
            stage_d,
            [
                "--parameter-region-file", str(core_region_file),
                "--parameter-region-mode", "core_only",
                "--parameter-samples", str(args.stage_d_samples),
                "--seeds-per-parameter-set", "1",
                "--coordinate-counts", "6",
                "--max-state-count", "1000",
                "--horizon-grid", "long_5x",
                "--workers", str(args.workers),
                "--max-runtime-seconds", str(min(3600, _time_left(started, args.global_wall_clock_seconds) - 900)),
                "--parameter-seed", "20260525",
            ],
        )
        write_n6_transfer_summary(stage_c, stage_d, stage_d / "stage_d_n6_transfer_summary.md")
        completed_or_partial("D", status, completed, partial)
    else:
        notes.append("Stage D skipped or deferred; not enough remaining wall clock or no selected core regions.")

    stage_e_dir = args.root_out / "repair_stage_e_window_null_stress"
    stage_e_dir.mkdir(parents=True, exist_ok=True)
    source_for_window = stage_c if stage_c.exists() else stage_b
    kill_rows = write_window_stress(source_for_window, stage_e_dir / "window_null_kill_table.csv", stage_e_dir / "stage_e_window_null_stress_summary.md")
    write_localized_reproducibility(kill_rows, stage_e_dir / "localized_candidate_reproducibility.csv", stage_e_dir / "localized_candidate_reproducibility.md")
    completed.append("E")

    status = final_summary(args.root_out, started, args.global_wall_clock_seconds, completed, partial, notes)
    (args.root_out / "repaired_batch_status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


def _run_stage(out_dir: Path, extra_args: list[str]) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "omega.rfs_mb0_future_landscape.run_relation_atlas",
        "--out",
        str(out_dir),
        *extra_args,
    ]
    started = time.perf_counter()
    result = subprocess.run(command, cwd=Path.cwd(), check=False)
    status_path = out_dir / "relation_atlas_status.json"
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {"status": "MISSING_STATUS"}
    status["subprocess_returncode"] = result.returncode
    status["stage_elapsed_seconds"] = time.perf_counter() - started
    return status


def write_parameter_trends(run_dir: Path, csv_path: Path, md_path: Path) -> list[dict[str, object]]:
    shapes = _read_csv(run_dir / "environment_shape_summary.csv")
    detector = {row["environment_id"]: row for row in _read_csv(run_dir / "relation_atlas_detector_summary.csv")}
    metadata = {row["environment_id"]: row for row in _read_csv(run_dir / "generated_environment_metadata.csv")}
    merged = []
    for row in shapes:
        env_id = row["environment_id"]
        merged.append({**metadata.get(env_id, {}), **row, **detector.get(env_id, {})})
    rows = []
    for parameter in PARAMETERS:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in merged:
            value = str(_metadata_value(row, parameter))
            grouped.setdefault(value, []).append(row)
        for value, items in sorted(grouped.items()):
            rows.append(_trend_row(parameter, value, items))
    _write_csv(csv_path, rows)
    lines = ["# Parameter Trends", "", "| parameter | value | n | middle | saturation | underconnected | cycle | local | MI delta | motif delta |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            "| {parameter_name} | {parameter_value} | {n_environments} | {middle_regime_rate:.3f} | {fast_saturation_rate:.3f} | {underconnected_rate:.3f} | {cycle_rate:.3f} | {local_candidate_rate:.3f} | {mean_MI_delta_vs_null:.3f} | {mean_motif_delta_vs_null:.3f} |".format(**row)
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def write_interaction_trends(run_dir: Path, csv_path: Path, md_path: Path) -> list[dict[str, object]]:
    shapes = _read_csv(run_dir / "environment_shape_summary.csv")
    detector = {row["environment_id"]: row for row in _read_csv(run_dir / "relation_atlas_detector_summary.csv")}
    metadata = {row["environment_id"]: row for row in _read_csv(run_dir / "generated_environment_metadata.csv")}
    windows = _read_csv(run_dir / "relation_atlas_window_summary.csv")
    window_candidate_envs = {
        row["family"]
        for row in windows
        if row.get("aggregate_window_class_v1_2") == "structured_candidate_window"
    }
    merged = []
    for row in shapes:
        env_id = row["environment_id"]
        merged.append({**metadata.get(env_id, {}), **row, **detector.get(env_id, {}), "has_window_candidate": str(env_id in window_candidate_envs)})
    out = []
    for left, right in INTERACTIONS:
        grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
        for row in merged:
            grouped.setdefault((str(_metadata_value(row, left)), str(_metadata_value(row, right))), []).append(row)
        for (left_value, right_value), items in sorted(grouped.items()):
            trend = _trend_row(f"{left} x {right}", f"{left_value} x {right_value}", items)
            trend.update(
                {
                    "parameter_left": left,
                    "value_left": left_value,
                    "parameter_right": right,
                    "value_right": right_value,
                    "window_candidate_rate": sum(row.get("has_window_candidate") == "True" for row in items) / max(1, len(items)),
                }
            )
            out.append(trend)
    _write_csv(csv_path, out)
    lines = ["# Parameter Interaction Trends", "", "| interaction | values | n | middle | saturation | underconnected | cycle | window candidates | MI delta | motif delta |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in out:
        lines.append(
            "| {parameter_name} | {parameter_value} | {n_environments} | {middle_regime_rate:.3f} | {fast_saturation_rate:.3f} | {underconnected_rate:.3f} | {cycle_rate:.3f} | {window_candidate_rate:.3f} | {mean_MI_delta_vs_null:.3f} | {mean_motif_delta_vs_null:.3f} |".format(**row)
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def select_middle_regions(run_dir: Path, core_path: Path, broad_path: Path, limit: int = 12) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = write_parameter_trends(run_dir, run_dir / "parameter_trends_for_selection.csv", run_dir / "parameter_trends_for_selection.md")
    interactions = write_interaction_trends(run_dir, run_dir / "parameter_interaction_trends_for_selection.csv", run_dir / "parameter_interaction_trends_for_selection.md")
    candidate_values: dict[str, list[object]] = {}
    for parameter in PARAMETERS:
        values = [
            row
            for row in rows
            if row["parameter_name"] == parameter
            and row["n_environments"] >= 3
            and row["middle_regime_rate"] >= 0.50
            and row["fast_saturation_rate"] <= 0.50
            and row["underconnected_rate"] <= 0.50
            and row["cycle_rate"] <= 0.30
        ]
        values.sort(key=lambda row: (row["middle_regime_rate"], row["mean_nonsaturation_window_length"]), reverse=True)
        if values:
            candidate_values[parameter] = [_coerce_value(values[0]["parameter_value"])]
    broad_regions = []
    base = {key: value for key, value in candidate_values.items() if key in {"update_footprint", "out_degree_target", "constraint_density", "constraint_strength"}}
    core_regions = []
    best_interactions = [
        row for row in interactions
        if row["n_environments"] >= 3
        and row["middle_regime_rate"] >= 0.60
        and row["fast_saturation_rate"] <= 0.25
        and row["underconnected_rate"] <= 0.30
        and row["cycle_rate"] <= 0.30
    ]
    best_interactions.sort(key=lambda row: (row["middle_regime_rate"], row["mean_nonsaturation_window_length"]), reverse=True)
    if base:
        core_regions.append({"name": "shape_selected_core", "core": True, "source": str(run_dir), **base})
    for index, row in enumerate(best_interactions[:3]):
        core_regions.append(
            {
                "name": f"shape_selected_core_{index}",
                "core": True,
                "source": "interaction_trends",
                row["parameter_left"]: [_coerce_value(row["value_left"])],
                row["parameter_right"]: [_coerce_value(row["value_right"])],
            }
        )
    for key, value in candidate_values.items():
        broad_regions.append({"name": f"shape_selected_{key}", "source": str(run_dir), "exploratory": True, key: value})
    core_regions = core_regions[:limit]
    broad_regions = broad_regions[:limit]
    core_path.write_text(json.dumps({"regions": core_regions}, indent=2, sort_keys=True), encoding="utf-8")
    broad_path.write_text(json.dumps({"regions": broad_regions}, indent=2, sort_keys=True), encoding="utf-8")
    return core_regions, broad_regions


def write_confirmed_middle_regions(run_dir: Path, out_path: Path) -> None:
    shapes = _read_csv(run_dir / "environment_shape_summary.csv")
    detector = {row["environment_id"]: row for row in _read_csv(run_dir / "relation_atlas_detector_summary.csv")}
    rows = []
    for row in shapes:
        if row.get("environment_shape_class") == "middle_regime_environment":
            rows.append(
                {
                    "environment_id": row["environment_id"],
                    "parameter_set_id": row["parameter_set_id"],
                    "nonsaturation_window_length": row["nonsaturation_window_length"],
                    "largest_scc_fraction": row["largest_scc_fraction"],
                    "edge_reciprocity_fraction": row["edge_reciprocity_fraction"],
                    "atlas_gate_class": detector.get(row["environment_id"], {}).get("atlas_gate_class", ""),
                }
            )
    _write_csv(out_path, rows)


def write_n6_transfer_summary(stage_c: Path, stage_d: Path, out_path: Path) -> None:
    c_shapes = _read_csv(stage_c / "environment_shape_summary.csv") if stage_c.exists() else []
    d_shapes = _read_csv(stage_d / "environment_shape_summary.csv") if stage_d.exists() else []
    lines = ["# Stage D n=6 Transfer Summary", "", f"- Stage C environments: {len(c_shapes)}", f"- Stage D environments: {len(d_shapes)}", ""]
    lines.extend(["## n=6 Shape Classes", "", "| class | n |", "|---|---:|"])
    for klass, count in sorted(_counts(row["environment_shape_class"] for row in d_shapes).items()):
        lines.append(f"| {klass} | {count} |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_window_stress(run_dir: Path, csv_path: Path, md_path: Path) -> list[dict[str, object]]:
    windows = _read_csv(run_dir / "relation_atlas_window_summary.csv")
    detector = {row["environment_id"]: row for row in _read_csv(run_dir / "relation_atlas_detector_summary.csv")}
    profiles = _read_csv(run_dir / "horizon_local_profiles.csv")
    transitions = _read_csv(run_dir / "transition_information.csv")
    profile_lookup = _window_metric_lookup(profiles, transitions)
    selected = [
        row for row in windows
        if row.get("window") in {"early_window", "pre_saturation_window"}
        and row.get("aggregate_window_class_v1_2") == "structured_candidate_window"
    ][:200]
    rows = []
    nulls = (
        "degree_preserving_rewire",
        "out_degree_preserving_random",
        "constraint_shuffled",
        "asymmetry_shuffled",
        "roughness_resampled",
        "frontier_or_probe_marginal",
    )
    for row in selected:
        env = row["family"]
        probe = row["probe_family"]
        window = row["window"]
        metrics = profile_lookup.get((env, probe, window), {})
        aggregate_gate_passed = detector.get(env, {}).get("atlas_gate_class") == "structured_propagation"
        for null_name in nulls:
            js = float(metrics.get(f"JS_to_null_{null_name}", metrics.get("JS_to_null", row.get("mean_JS_to_null_H", 0.0))))
            kl = float(metrics.get(f"KL_to_null_{null_name}", metrics.get("smoothed_KL_to_null", 0.0)))
            mi_delta = float(metrics.get(f"MI_delta_vs_null_{null_name}", metrics.get("MI_delta_vs_null", 0.0)))
            motif_delta = float(metrics.get(f"motif_delta_vs_null_{null_name}", metrics.get("signature_transition_motif_reuse_delta_vs_null", 0.0)))
            survives = js > 0 and mi_delta > 0 and motif_delta > 0
            rows.append(
                {
                    "environment_id": env,
                    "parameter_set_id": metrics.get("parameter_set_id", ""),
                    "window_name": window,
                    "probe_family": probe,
                    "candidate_window_class": row["aggregate_window_class_v1_2"],
                    "null_name": null_name,
                    "JS_to_null_window": js,
                    "KL_to_null_window": kl,
                    "MI_delta_vs_null_window": mi_delta,
                    "motif_delta_vs_null_window": motif_delta,
                    "candidate_survives_null": int(survives),
                    "kill_reason": _kill_reason(null_name, survives, aggregate_gate_passed, row),
                }
            )
    _write_csv(csv_path, rows)
    counts = _counts(row["kill_reason"] for row in rows)
    lines = ["# Stage E Window/Null Stress Summary", "", f"- Candidate windows selected: {len(selected)}", f"- Null-specific rows: {len(rows)}", "- Promotion blocker: aggregate gate not passed unless already supported by aggregate class.", "", "## Kill Reasons", "", "| reason | n |", "|---|---:|"]
    for reason, count in sorted(counts.items()):
        lines.append(f"| {reason} | {count} |")
    lines.extend(["", "This stage is exploratory and does not promote window-local candidates."])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def write_localized_reproducibility(kill_rows: list[dict[str, object]], csv_path: Path, md_path: Path) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in kill_rows:
        region = _region_id(str(row.get("parameter_set_id", row["environment_id"])))
        grouped.setdefault((region, str(row["window_name"]), str(row["probe_family"])), []).append(row)
    out = []
    for (region, window, probe), items in sorted(grouped.items()):
        envs = {str(row["environment_id"]) for row in items}
        candidate_rows = [row for row in items if str(row["candidate_window_class"]) == "structured_candidate_window"]
        n_candidates = len({str(row["environment_id"]) for row in candidate_rows})
        null_names = {str(row["null_name"]) for row in items}
        rates = {
            null_name: _null_survival_rate(items, null_name)
            for null_name in null_names
        }
        dominant = _dominant_kill(items)
        localized = int(
            len(envs) >= 3
            and n_candidates / max(1, len(envs)) >= 0.25
            and rates.get("degree_preserving_rewire", 0.0) >= 0.50
            and rates.get("out_degree_preserving_random", 0.0) >= 0.50
        )
        out.append(
            {
                "parameter_region_id": region,
                "window_name": window,
                "probe_family": probe,
                "n_environments": len(envs),
                "candidate_window_count": n_candidates,
                "candidate_window_rate": n_candidates / max(1, len(envs)),
                "survives_degree_rate": rates.get("degree_preserving_rewire", 0.0),
                "survives_out_degree_random_rate": rates.get("out_degree_preserving_random", 0.0),
                "survives_constraint_shuffle_rate": rates.get("constraint_shuffled", 0.0),
                "survives_asymmetry_shuffle_rate": rates.get("asymmetry_shuffled", 0.0),
                "survives_roughness_resample_rate": rates.get("roughness_resampled", 0.0),
                "localized_reproducible_candidate": localized,
                "dominant_kill_reason": dominant,
            }
        )
    _write_csv(csv_path, out)
    lines = ["# Localized Candidate Reproducibility", "", "| region | window | probe family | envs | candidate rate | degree survive | out-degree survive | localized | dominant kill |", "|---|---|---|---:|---:|---:|---:|---:|---|"]
    for row in out[:120]:
        lines.append(
            "| {parameter_region_id} | {window_name} | {probe_family} | {n_environments} | {candidate_window_rate:.3f} | {survives_degree_rate:.3f} | {survives_out_degree_random_rate:.3f} | {localized_reproducible_candidate} | {dominant_kill_reason} |".format(**row)
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def final_summary(root: Path, started: float, global_seconds: int, completed: list[str], partial: list[str], notes: list[str]) -> dict[str, object]:
    stage_dirs = [path for path in root.glob("repair_stage_*") if path.is_dir()]
    statuses = []
    total_env = 0
    total_middle = 0
    total_pass = 0
    for stage in stage_dirs:
        status_path = stage / "relation_atlas_status.json"
        if status_path.exists():
            status = json.loads(status_path.read_text(encoding="utf-8"))
            statuses.append((stage.name, status))
            total_env += int(status.get("generated_environments_completed", 0))
            total_middle += int(status.get("middle_regime_environments", 0))
            total_pass += int(status.get("atlas_gate_pass_count", 0))
    wall = time.perf_counter() - started
    status = {
        "status": "COMPLETED_OR_PARTIAL",
        "wall_clock_seconds": wall,
        "wall_clock_budget_seconds": global_seconds,
        "stages_completed": completed,
        "stages_partial": partial,
        "total_generated_environments": total_env,
        "total_middle_regime_environments": total_middle,
        "atlas_gate_pass_count": total_pass,
        "control_aggregate_pass_count": 0,
        "recommended_next_step": "Use repaired null-kill and reproducibility diagnostics to decide whether current zero-pass result is driven by null artifacts, probe mismatch, or aggregation; do not promote window-local candidates without aggregate support.",
    }
    lines = [
        "# RFS-MB0 Relation Atlas Repaired Batch Summary",
        "",
        f"- Wall clock used: {wall:.1f} seconds",
        f"- Stages completed: {', '.join(completed) if completed else 'none'}",
        f"- Stages partial/skipped: {', '.join(partial) if partial else 'none'}",
        f"- Total generated environments: {total_env}",
        f"- Total middle-regime environments: {total_middle}",
        f"- Atlas gate pass count: {total_pass}",
        "",
        "## Stage Status",
        "",
        "| stage | status | environments | middle | gate passes | elapsed |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name, stage_status in statuses:
        lines.append(
            "| {name} | {status} | {env} | {middle} | {passes} | {elapsed:.1f} |".format(
                name=name,
                status=stage_status.get("status", ""),
                env=stage_status.get("generated_environments_completed", 0),
                middle=stage_status.get("middle_regime_environments", 0),
                passes=stage_status.get("atlas_gate_pass_count", 0),
                elapsed=float(stage_status.get("elapsed_seconds", 0.0)),
            )
        )
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Claim Boundary", "", "This is relation-atlas environment calibration, not Omega validation. No agent, identity, valuer, viability, or scientific-gate-positive claim is made."])
    (root / "repaired_batch_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return status


def completed_or_partial(stage: str, status: dict[str, object], completed: list[str], partial: list[str]) -> None:
    if status.get("status") == "COMPLETED" and int(status.get("subprocess_returncode", 1)) == 0:
        completed.append(stage)
    else:
        partial.append(stage)


def _copy_stage_outputs(stage: Path, prefix: str) -> None:
    copies = {
        "summary.md": f"{prefix}_summary.md",
        "relation_atlas_status.json": f"{prefix}_status.json",
        "environment_shape_classes.csv": f"{prefix}_environment_shape_classes.csv",
    }
    for src_name, dst_name in copies.items():
        src = stage / src_name
        if src.exists():
            (stage / dst_name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _trend_row(parameter: str, value: str, items: list[dict[str, str]]) -> dict[str, object]:
    n = len(items)
    return {
        "parameter_name": parameter,
        "parameter_value": value,
        "n_environments": n,
        "middle_regime_rate": _rate(items, "environment_shape_class", "middle_regime_environment"),
        "fast_saturation_rate": _rate(items, "environment_shape_class", "fast_saturation_environment"),
        "underconnected_rate": _rate(items, "environment_shape_class", "underconnected_environment"),
        "cycle_rate": _rate(items, "environment_shape_class", "cycle_dominated_environment"),
        "underdetermined_rate": _rate(items, "environment_shape_class", "underdetermined_environment"),
        "local_candidate_rate": mean(float(row.get("local_candidate_fraction", 0.0)) > 0 for row in items),
        "mean_nonsaturation_window_length": _mean(row.get("nonsaturation_window_length", "") for row in items),
        "mean_saturation_onset_H": _mean(row.get("reach_saturation_onset_H", "") for row in items),
        "mean_largest_scc_fraction": _mean(row.get("largest_scc_fraction", "") for row in items),
        "mean_edge_reciprocity_fraction": _mean(row.get("edge_reciprocity_fraction", "") for row in items),
        "mean_MI_delta_vs_null": _mean(row.get("mean_MI_delta_vs_null", "") for row in items),
        "mean_motif_delta_vs_null": _mean(row.get("mean_motif_delta_vs_null", "") for row in items),
        "mean_JS_bundle": _mean(row.get("mean_JS_bundle", "") for row in items),
        "atlas_gate_pass_rate": _rate(items, "atlas_gate_class", "structured_propagation"),
    }


def _window_metric_lookup(profile_rows: list[dict[str, str]], transition_rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, object]]:
    transition_by_key = {
        (row["environment_id"], row["probe_name"], row["H"]): row
        for row in transition_rows
    }
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in profile_rows:
        h = int(row["H"])
        for window in _windows_for_row(row, h):
            key = (row["environment_id"], row["probe_family"], window)
            merged = {**row, **transition_by_key.get((row["environment_id"], row["probe_name"], row["H"]), {})}
            grouped.setdefault(key, []).append(merged)
    out: dict[tuple[str, str, str], dict[str, object]] = {}
    for key, items in grouped.items():
        metrics: dict[str, object] = {
            "parameter_set_id": items[0].get("parameter_set_id", ""),
            "JS_to_null": _mean(row.get("JS_to_null", "") for row in items),
            "smoothed_KL_to_null": _mean(row.get("smoothed_KL_to_null", "") for row in items),
        }
        metric_keys = sorted({metric for row in items for metric in row if metric.startswith(("JS_to_null_", "KL_to_null_", "MI_delta_vs_null_", "motif_delta_vs_null_"))})
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


def _kill_reason(null_name: str, survives: bool, aggregate_gate_passed: bool, row: dict[str, str]) -> str:
    if float(row.get("saturation_fraction", 0.0)) >= 0.50:
        return "saturation_window"
    if not survives:
        return {
            "degree_preserving_rewire": "failed_degree_null",
            "out_degree_preserving_random": "failed_out_degree_random_null",
            "constraint_shuffled": "failed_constraint_shuffle",
            "asymmetry_shuffled": "failed_asymmetry_shuffle",
            "roughness_resampled": "failed_roughness_resample",
            "frontier_or_probe_marginal": "failed_frontier_probe_marginal",
        }.get(null_name, f"failed_{null_name}")
    if not aggregate_gate_passed:
        return "aggregate_gate_not_passed"
    return "survived_diagnostic_null"


def _region_id(parameter_set_id: str) -> str:
    parts = parameter_set_id.split("_")
    keep = [part for part in parts if part.startswith(("m", "k", "cd", "cs", "as", "rev", "rw"))]
    return "_".join(keep) if keep else parameter_set_id


def _null_survival_rate(items: list[dict[str, object]], null_name: str) -> float:
    rows = [row for row in items if row["null_name"] == null_name]
    return sum(int(row["candidate_survives_null"]) for row in rows) / max(1, len(rows))


def _dominant_kill(items: list[dict[str, object]]) -> str:
    counts = _counts(row["kill_reason"] for row in items)
    if not counts:
        return ""
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[0][0]


def _metadata_value(row: dict[str, str], key: str) -> str:
    metadata = json.loads(row.get("metadata_json", "{}")) if row.get("metadata_json") else {}
    return str(row.get(key) or metadata.get(key, ""))


def _rate(items: list[dict[str, str]], key: str, value: str) -> float:
    return sum(row.get(key) == value for row in items) / max(1, len(items))


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


def _coerce_value(value: object) -> object:
    text = str(value)
    try:
        number = float(text)
    except ValueError:
        return text
    if number.is_integer():
        return int(number)
    return number


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
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


def _time_left(started: float, global_seconds: int) -> int:
    return max(0, int(global_seconds - (time.perf_counter() - started)))


if __name__ == "__main__":
    main()
