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

    stage_b = args.root_out / "5h_stage_b_broad_n5"
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
        completed_or_partial("B", status, completed, partial)

    region_file = args.root_out / "5h_stage_c_selected_parameter_regions.json"
    source_for_regions = stage_b if stage_b.exists() else args.existing_run
    regions = select_middle_regions(source_for_regions, region_file)
    notes.append(f"Selected {len(regions)} Stage C parameter regions from {source_for_regions}.")

    stage_c = args.root_out / "5h_stage_c_targeted_n5"
    if regions and _time_left(started, args.global_wall_clock_seconds) > 900:
        status = _run_stage(
            stage_c,
            [
                "--parameter-region-file", str(region_file),
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
        write_confirmed_middle_regions(stage_c, stage_c / "stage_c_confirmed_middle_regime_regions.csv")
        completed_or_partial("C", status, completed, partial)

    stage_d = args.root_out / "5h_stage_d_targeted_n6"
    if regions and _time_left(started, args.global_wall_clock_seconds) > 3600:
        status = _run_stage(
            stage_d,
            [
                "--parameter-region-file", str(region_file),
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
        notes.append("Stage D skipped or deferred; not enough remaining wall clock or no selected regions.")

    stage_e_dir = args.root_out / "5h_stage_e_window_null_stress"
    stage_e_dir.mkdir(parents=True, exist_ok=True)
    source_for_window = stage_c if stage_c.exists() else stage_b
    write_window_stress(source_for_window, stage_e_dir / "stage_e_window_null_stress_summary.csv", stage_e_dir / "stage_e_window_null_stress_summary.md")
    completed.append("E")

    status = final_summary(args.root_out, started, args.global_wall_clock_seconds, completed, partial, notes)
    (args.root_out / "5h_batch_status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


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


def select_middle_regions(run_dir: Path, out_path: Path, limit: int = 12) -> list[dict[str, object]]:
    rows = write_parameter_trends(run_dir, run_dir / "parameter_trends_for_selection.csv", run_dir / "parameter_trends_for_selection.md")
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
    regions = []
    base = {key: value for key, value in candidate_values.items() if key in {"update_footprint", "out_degree_target", "constraint_density", "constraint_strength"}}
    if base:
        regions.append({"name": "shape_selected_core", "source": str(run_dir), **base})
    for key, value in candidate_values.items():
        regions.append({"name": f"shape_selected_{key}", "source": str(run_dir), key: value})
    regions = regions[:limit]
    out_path.write_text(json.dumps({"regions": regions}, indent=2, sort_keys=True), encoding="utf-8")
    return regions


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


def write_window_stress(run_dir: Path, csv_path: Path, md_path: Path) -> None:
    windows = _read_csv(run_dir / "relation_atlas_window_summary.csv")
    selected = [
        row for row in windows
        if row.get("window") in {"early_window", "pre_saturation_window"}
        and row.get("aggregate_window_class_v1_2") == "structured_candidate_window"
    ][:200]
    rows = []
    for row in selected:
        rows.append(
            {
                "environment_id": row["family"],
                "parameter_set_id": "",
                "window_name": row["window"],
                "probe_family": row["probe_family"],
                "window_local_candidate_fraction": 1.0,
                "degree_null_separation": row["mean_JS_to_null_H"],
                "constraint_shuffled_separation": "",
                "asymmetry_shuffled_separation": "",
                "roughness_resampled_separation": "",
                "frontier_null_separation": "",
                "promote_blocker": "aggregate_gate_not_passed",
            }
        )
    _write_csv(csv_path, rows)
    lines = ["# Stage E Window/Null Stress Summary", "", f"- Structured-candidate windows inspected: {len(rows)}", "- Promotion blocker: aggregate gate not passed.", "", "This stage is exploratory and does not promote window-local candidates."]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def final_summary(root: Path, started: float, global_seconds: int, completed: list[str], partial: list[str], notes: list[str]) -> dict[str, object]:
    stage_dirs = [path for path in root.glob("5h_stage_*") if path.is_dir()]
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
        "recommended_next_step": "Use selected middle-regime parameter regions for confirmatory fresh-seed n=5 and limited n=6 transfer only; do not promote window-local candidates without aggregate support.",
    }
    lines = [
        "# RFS-MB0 Relation Atlas 5-Hour Batch Summary",
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
    (root / "5h_batch_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
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
