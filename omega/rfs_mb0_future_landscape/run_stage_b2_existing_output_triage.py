from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean

from .run_focused_boundary_recurrence import float_or_zero, read_csv, write_csv


OUTPUTS = (
    "existing_stage_ab_syndrome_concentration.csv",
    "existing_stage_ab_syndrome_by_window.csv",
    "existing_stage_ab_syndrome_by_probe.csv",
    "existing_stage_ab_syndrome_by_flow_mode.csv",
    "existing_stage_ab_syndrome_by_start_seed.csv",
    "existing_stage_ab_parameter_family_summary.csv",
    "existing_stage_a_component_driver_audit.csv",
    "existing_stage_ab_triage_report.md",
    "status.json",
    "errors.csv",
    "output_manifest.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Triage existing desktop Stage A/B syndrome outputs before Stage B-2 scale.")
    parser.add_argument("--stage-a-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_a_regenerated_full_controls"))
    parser.add_argument("--stage-b-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_b_mechanism_smoke"))
    parser.add_argument("--phase-b-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_phase_b_regenerated_full_controls"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_stage_b2_existing_output_triage"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    errors: list[dict[str, object]] = []
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "rfs_mb0_stage_b2_existing_output_triage",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stage_a_dir": str(args.stage_a_dir),
        "stage_b_dir": str(args.stage_b_dir),
        "phase_b_dir": str(args.phase_b_dir),
        "out_dir": str(args.out),
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "candidate_promotion_enabled": False,
    }
    try:
        smoke = read_csv(args.stage_a_dir / "phase_b_syndrome_smoke.csv")
        ablation = read_csv(args.stage_a_dir / "phase_b_syndrome_component_ablation.csv")
        mechanism_rates = read_csv(args.stage_b_dir / "mechanism_control_syndrome_rates.csv")
        job_manifest = read_csv(args.phase_b_dir / "phase_b_job_manifest.csv")
        concentration = concentration_rows(smoke, mechanism_rates)
        by_window = aggregate_rows(smoke, ("syndrome_id", "window"))
        by_probe = aggregate_rows(smoke, ("syndrome_id", "probe_key"))
        by_flow = aggregate_rows(smoke, ("syndrome_id", "flow_mode"))
        by_start_seed = aggregate_rows(smoke, ("syndrome_id", "seed", "start_index"))
        parameter_family = parameter_family_rows(smoke, job_manifest)
        drivers = component_driver_rows(ablation)
        write_csv(args.out / "existing_stage_ab_syndrome_concentration.csv", concentration)
        write_csv(args.out / "existing_stage_ab_syndrome_by_window.csv", by_window)
        write_csv(args.out / "existing_stage_ab_syndrome_by_probe.csv", by_probe)
        write_csv(args.out / "existing_stage_ab_syndrome_by_flow_mode.csv", by_flow)
        write_csv(args.out / "existing_stage_ab_syndrome_by_start_seed.csv", by_start_seed)
        write_csv(args.out / "existing_stage_ab_parameter_family_summary.csv", parameter_family)
        write_csv(args.out / "existing_stage_a_component_driver_audit.csv", drivers)
        write_report(args.out, concentration, by_window, by_probe, by_flow, parameter_family, drivers)
        status.update({
            "status": "COMPLETED",
            "finalization_reason": "all_existing_outputs_triaged",
            "stage_a_syndrome_smoke_rows": len(smoke),
            "stage_b_mechanism_rate_rows": len(mechanism_rates),
            "concentration_rows": len(concentration),
            "errors": 0,
        })
    except Exception as exc:  # noqa: BLE001
        errors.append({"error": repr(exc)})
        status.update({"status": "FAILED_WITH_ERRORS", "finalization_reason": "triage_exception", "errors": len(errors)})
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    write_csv(args.out / "errors.csv", errors)
    (args.out / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(args.out)


def concentration_rows(smoke: list[dict[str, str]], mechanism_rates: list[dict[str, str]]) -> list[dict[str, object]]:
    rows = []
    for (syndrome_id,), items in group_by(smoke, ("syndrome_id",)).items():
        joint_rates = [float_or_zero(row.get("syndrome_joint_pass")) for row in items]
        partial_rates = [float_or_zero(row.get("syndrome_component_pass_fraction")) for row in items]
        mechanism_items = [row for row in mechanism_rates if row.get("syndrome_id") == syndrome_id]
        mechanism_rates_values = [float_or_zero(row.get("syndrome_rate")) for row in mechanism_items]
        rows.append({
            "syndrome_id": syndrome_id,
            "stage_a_rows": len(items),
            "stage_a_joint_pass_rate": mean(joint_rates) if joint_rates else 0.0,
            "stage_a_component_pass_fraction_mean": mean(partial_rates) if partial_rates else 0.0,
            "stage_b_mechanism_rate_mean": mean(mechanism_rates_values) if mechanism_rates_values else "",
            "stage_b_mechanism_rate_max": max(mechanism_rates_values) if mechanism_rates_values else "",
            "triage_read": triage_read(syndrome_id, joint_rates, mechanism_rates_values),
        })
    return rows


def aggregate_rows(rows: list[dict[str, str]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    out = []
    for key, items in group_by(rows, keys).items():
        joint = [float_or_zero(row.get("syndrome_joint_pass")) for row in items]
        partial = [float_or_zero(row.get("syndrome_component_pass_fraction")) for row in items]
        signed = [float_or_zero(row.get("syndrome_signed_score_mean")) for row in items]
        out.append({
            **{field: value for field, value in zip(keys, key)},
            "rows": len(items),
            "joint_pass_rate": mean(joint) if joint else 0.0,
            "component_pass_fraction_mean": mean(partial) if partial else 0.0,
            "signed_score_mean": mean(signed) if signed else 0.0,
        })
    return out


def parameter_family_rows(smoke: list[dict[str, str]], manifest: list[dict[str, str]]) -> list[dict[str, object]]:
    by_seed_probe_start = {
        (row.get("seed"), row.get("probe_key"), row.get("start_samples")): row
        for row in manifest
    }
    enriched = []
    for row in smoke:
        manifest_row = by_seed_probe_start.get((row.get("seed"), row.get("probe_key"), "4")) or by_seed_probe_start.get((row.get("seed"), row.get("probe_key"), "8")) or {}
        group_id = row.get("group_id") or manifest_row.get("group_id", "")
        family = group_id.split("|", 1)[1] if "|" in group_id else group_id
        enriched.append({**row, "parameter_family": family})
    return aggregate_rows(enriched, ("syndrome_id", "parameter_family"))


def component_driver_rows(ablation: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for key, items in group_by(ablation, ("syndrome_id", "component_removed")).items():
        fractions = [float_or_zero(row.get("single_component_explained_fraction")) for row in items]
        full_scores = [float_or_zero(row.get("full_syndrome_score")) for row in items]
        out.append({
            "syndrome_id": key[0],
            "component_removed": key[1],
            "rows": len(items),
            "single_component_explained_fraction_mean": mean(fractions) if fractions else 0.0,
            "full_syndrome_score_mean": mean(full_scores) if full_scores else 0.0,
            "driver_read": "single_component_risk" if fractions and mean(fractions) >= 0.90 else "joint_not_single_component_dominated",
        })
    return out


def triage_read(syndrome_id: object, stage_a_joint: list[float], mechanism_rates: list[float]) -> str:
    joint_rate = mean(stage_a_joint) if stage_a_joint else 0.0
    mechanism_max = max(mechanism_rates) if mechanism_rates else 0.0
    if "SYN_A" in str(syndrome_id) or "SYN_C" in str(syndrome_id):
        return "prioritize_stabilizing_channel_syndrome" if joint_rate > 0 else "primary_syndrome_sparse"
    if mechanism_max > 0.05:
        return "retain_turnover_diffusion_contrast"
    return "secondary_contrast_low_priority"


def write_report(
    out_dir: Path,
    concentration: list[dict[str, object]],
    by_window: list[dict[str, object]],
    by_probe: list[dict[str, object]],
    by_flow: list[dict[str, object]],
    parameter_family: list[dict[str, object]],
    drivers: list[dict[str, object]],
) -> None:
    top_windows = sorted(by_window, key=lambda row: float_or_zero(row.get("joint_pass_rate")), reverse=True)[:8]
    top_families = sorted(parameter_family, key=lambda row: float_or_zero(row.get("joint_pass_rate")), reverse=True)[:8]
    lines = [
        "# Existing Stage A/B Syndrome Triage",
        "",
        "Claim boundary: existing-output triage only. No holdout scoring, candidate promotion, Omega detection, agency detection, identity detection, or value detection.",
        "",
        "## Concentration Read",
        "",
        "| syndrome_id | stage_a_joint_pass_rate | stage_b_rate_max | triage_read |",
        "|---|---:|---:|---|",
    ]
    for row in concentration:
        lines.append(f"| {row.get('syndrome_id', '')} | {float_or_zero(row.get('stage_a_joint_pass_rate')):.6f} | {float_or_zero(row.get('stage_b_mechanism_rate_max')):.6f} | {row.get('triage_read', '')} |")
    lines.extend(["", "## Top Windows", "", "| syndrome_id | window | joint_pass_rate |", "|---|---|---:|"])
    for row in top_windows:
        lines.append(f"| {row.get('syndrome_id', '')} | {row.get('window', '')} | {float_or_zero(row.get('joint_pass_rate')):.6f} |")
    lines.extend(["", "## Top Parameter Families", "", "| syndrome_id | parameter_family | joint_pass_rate |", "|---|---|---:|"])
    for row in top_families:
        lines.append(f"| {row.get('syndrome_id', '')} | {row.get('parameter_family', '')} | {float_or_zero(row.get('joint_pass_rate')):.6f} |")
    lines.extend(["", "## Recommendation", "", "Prioritize SYN_A/SYN_C as stabilizing-channel syndromes; retain SYN_B/SYN_D as secondary turnover/diffusion contrasts. Continue mechanism controls and gauge overlay, but do not open holdout.", ""])
    (out_dir / "existing_stage_ab_triage_report.md").write_text("\n".join(lines), encoding="utf-8")


def group_by(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    out: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[tuple(row.get(key, "") for key in keys)].append(row)
    return out


def write_manifest(out_dir: Path) -> None:
    rows = []
    for name in OUTPUTS:
        path = out_dir / name
        rows.append({"file": name, "exists": path.exists() or name == "output_manifest.json", "status": "present" if path.exists() or name == "output_manifest.json" else "missing", "row_count": csv_row_count(path) if path.suffix == ".csv" else ""})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.suffix != ".csv":
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        count = sum(1 for _ in handle)
    return max(0, count - 1)


if __name__ == "__main__":
    main()
