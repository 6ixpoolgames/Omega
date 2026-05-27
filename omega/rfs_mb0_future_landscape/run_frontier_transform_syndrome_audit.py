from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev

from .run_focused_boundary_recurrence import float_or_zero, group_by, write_csv
from .run_frontier_transform_b0 import metric_family


REQUIRED_PHASE_B_INPUTS = (
    "phase_b_design_metric_rows.csv",
    "phase_b_design_control_rows.csv",
    "phase_b_directional_effects.csv",
    "phase_b_metric_family_recurrence.csv",
    "phase_b_matched_recurrence_controls.csv",
    "phase_b_recurrence_excess.csv",
    "phase_b_control_quality_audit.csv",
    "phase_b_no_target_audit.csv",
    "phase_b_phase_c_readiness.csv",
)

OUTPUTS = (
    "phase_b_postmortem_control_match_decomposition.csv",
    "phase_b_postmortem_top_control_equivalent_rows.csv",
    "phase_b_postmortem_control_match_by_control_type.csv",
    "phase_b_postmortem_flow_mode_decomposition.csv",
    "phase_b_postmortem_window_decomposition.csv",
    "phase_b_postmortem_probe_dependency.csv",
    "phase_b_postmortem_report.md",
    "phase_b_syndrome_component_scores.csv",
    "phase_b_syndrome_smoke.csv",
    "phase_b_syndrome_vs_controls.csv",
    "phase_b_syndrome_multiplicity_audit.csv",
    "phase_b_syndrome_readiness.csv",
    "errors.csv",
    "status.json",
    "output_manifest.json",
)

DIAGNOSTIC_PROBES = {"existing_low", "full_state_hash"}
PLACEHOLDER_CONTROLS = {"probe_marginal_window_control"}
NOT_AVAILABLE_CONTROLS = {
    "constraint_shuffled_transform_control",
    "asymmetry_shuffled_transform_control",
    "roughness_resampled_transform_control",
}
MECHANISM_CONTROL_FAMILIES = {
    "roughness": {"roughness_resampled_transform_control"},
    "asymmetry": {"asymmetry_flip_sweep_control", "asymmetry_shuffled_transform_control"},
    "constraint": {
        "constraint_assignment_shuffle_control",
        "constraint_resampled_generation_control",
        "constraint_shuffled_transform_control",
    },
}
WEAK_CONTROL_QUALITIES = {"placeholder", "not_available", "missing"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only Stage A frontier-transform syndrome audit.")
    parser.add_argument("--phase-b-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--component-z-threshold", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    out_dir = args.out or (args.phase_b_dir / "stage_a_syndrome_audit")
    out_dir.mkdir(parents=True, exist_ok=True)
    missing = [name for name in REQUIRED_PHASE_B_INPUTS if not (args.phase_b_dir / name).exists()]
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "frontier_transform_syndrome_audit_stage_a_read_only",
        "phase_b_dir": str(args.phase_b_dir),
        "out_dir": str(out_dir),
        "new_systems_generated": 0,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "component_z_threshold": args.component_z_threshold,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    errors: list[dict[str, object]] = []
    if missing:
        status["status"] = "BLOCKED_MISSING_INPUTS"
        status["missing_input_count"] = len(missing)
        write_missing_outputs(out_dir, status, missing, started)
        return

    metric_rows = read_csv(args.phase_b_dir / "phase_b_design_metric_rows.csv")
    control_rows = read_csv(args.phase_b_dir / "phase_b_design_control_rows.csv")
    effect_rows = read_csv(args.phase_b_dir / "phase_b_directional_effects.csv")
    recurrence_rows = read_csv(args.phase_b_dir / "phase_b_matched_recurrence_controls.csv")
    control_quality_rows = read_csv(args.phase_b_dir / "phase_b_control_quality_audit.csv")
    readiness_rows = read_csv(args.phase_b_dir / "phase_b_phase_c_readiness.csv")

    control_quality = control_quality_by_name(control_rows, control_quality_rows)
    postmortem_control_decomposition = control_match_decomposition(recurrence_rows)
    top_control_equivalent = top_control_equivalent_rows(recurrence_rows)
    by_control = control_match_by_control_type(control_rows, control_quality)
    by_flow = flow_mode_decomposition(metric_rows, effect_rows)
    by_window = window_decomposition(metric_rows, control_rows)
    by_probe = probe_dependency(metric_rows, effect_rows, recurrence_rows)
    component_scores = syndrome_component_scores(
        metric_rows,
        control_rows,
        control_quality,
        args.component_z_threshold,
    )
    smoke_rows = syndrome_smoke(component_scores)
    syndrome_controls = syndrome_vs_controls(component_scores)
    multiplicity = syndrome_multiplicity_audit(component_scores)
    readiness = syndrome_readiness(smoke_rows, readiness_rows, control_quality_rows, control_quality)

    write_csv(out_dir / "phase_b_postmortem_control_match_decomposition.csv", postmortem_control_decomposition)
    write_csv(out_dir / "phase_b_postmortem_top_control_equivalent_rows.csv", top_control_equivalent)
    write_csv(out_dir / "phase_b_postmortem_control_match_by_control_type.csv", by_control)
    write_csv(out_dir / "phase_b_postmortem_flow_mode_decomposition.csv", by_flow)
    write_csv(out_dir / "phase_b_postmortem_window_decomposition.csv", by_window)
    write_csv(out_dir / "phase_b_postmortem_probe_dependency.csv", by_probe)
    write_csv(out_dir / "phase_b_syndrome_component_scores.csv", component_scores)
    write_csv(out_dir / "phase_b_syndrome_smoke.csv", smoke_rows)
    write_csv(out_dir / "phase_b_syndrome_vs_controls.csv", syndrome_controls)
    write_csv(out_dir / "phase_b_syndrome_multiplicity_audit.csv", multiplicity)
    write_csv(out_dir / "phase_b_syndrome_readiness.csv", readiness)
    write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, status, missing, readiness, smoke_rows, top_control_equivalent)
    status["status"] = "COMPLETED"
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["metric_rows"] = len(metric_rows)
    status["control_rows"] = len(control_rows)
    status["syndrome_component_rows"] = len(component_scores)
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(out_dir)


def write_missing_outputs(out_dir: Path, status: dict[str, object], missing: list[str], started: float) -> None:
    rows = [{"file": name, "status": "missing"} for name in missing]
    write_csv(out_dir / "errors.csv", [{"error": "missing_required_phase_b_inputs", "missing_files": json.dumps(missing)}])
    for name in OUTPUTS:
        if name.endswith(".csv") and name != "errors.csv":
            write_csv(out_dir / name, rows if name == "phase_b_postmortem_control_match_decomposition.csv" else [])
    write_report(out_dir, status, missing, [], [], [])
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(out_dir)


def syndrome_library() -> list[dict[str, object]]:
    return [
        component("stabilizing_boundary_syndrome", "growth_low", "frontier_growth_ratio", -1),
        component("stabilizing_boundary_syndrome", "turnover_low", "support_turnover_rate", -1),
        component("stabilizing_boundary_syndrome", "offdiag_low", "off_diagonal_transform_mass", -1),
        component("stabilizing_boundary_syndrome", "bottleneck_high", "frontier_bottleneck_index", 1),
        component("stabilizing_boundary_syndrome", "window_stability_low", "window_metric_vector_l2_distance_to_next", -1),
        component("transition_boundary_syndrome", "turnover_high", "support_turnover_rate", 1),
        component("transition_boundary_syndrome", "offdiag_high", "off_diagonal_transform_mass", 1),
        component("transition_boundary_syndrome", "window_change_high", "window_metric_vector_l2_distance_to_next", 1),
        component("transition_boundary_syndrome", "bottleneck_high", "frontier_bottleneck_index", 1),
        component("compression_funnel_syndrome", "growth_low", "frontier_growth_ratio", -1),
        component("compression_funnel_syndrome", "transition_entropy_low", "transition_matrix_entropy", -1),
        component("compression_funnel_syndrome", "bottleneck_high", "frontier_bottleneck_index", 1),
        component("compression_funnel_syndrome", "lost_signature_high", "lost_signature_rate", 1),
        component("compression_funnel_syndrome", "new_signature_low", "new_signature_rate", -1),
        component("diffusive_noise_syndrome", "turnover_high", "support_turnover_rate", 1),
        component("diffusive_noise_syndrome", "offdiag_high", "off_diagonal_transform_mass", 1),
        component("diffusive_noise_syndrome", "transition_entropy_high", "transition_matrix_entropy", 1),
        component("diffusive_noise_syndrome", "bottleneck_low", "frontier_bottleneck_index", -1),
        component("diffusive_noise_syndrome", "window_change_high", "window_metric_vector_l2_distance_to_next", 1),
        component("recurrence_cascade_syndrome", "signature_js_next_low", "signature_distribution_js_to_next_window", -1),
        component("recurrence_cascade_syndrome", "diagonal_persistence_high", "diagonal_persistence_mass", 1),
        component("recurrence_cascade_syndrome", "flow_concentration_high", "top_k_flow_concentration", 1),
    ]


def component(syndrome_id: str, component_id: str, metric_name: str, direction: int) -> dict[str, object]:
    return {
        "syndrome_id": syndrome_id,
        "syndrome_component_id": component_id,
        "metric_name": metric_name,
        "metric_family": metric_family(metric_name),
        "direction": direction,
        "selection_mode": "preregistered",
    }


def syndrome_component_scores(
    metric_rows: list[dict[str, str]],
    control_rows: list[dict[str, str]],
    control_quality: dict[str, str],
    threshold: float,
) -> list[dict[str, object]]:
    control_values = control_values_by_context(control_rows, control_quality)
    out = []
    for row in metric_rows:
        if row.get("preflight_context") != "design_recurrent_boundary":
            continue
        if row.get("probe_key") in DIAGNOSTIC_PROBES:
            continue
        for comp in syndrome_library():
            metric = str(comp["metric_name"])
            if row.get(metric, "") == "":
                out.append(component_score_row(row, comp, threshold, "unavailable_metric"))
                continue
            key = control_context_key(row, metric)
            controls = control_values.get(key, [])
            if not controls:
                out.append(component_score_row(row, comp, threshold, "unavailable_control"))
                continue
            observed = float_or_zero(row.get(metric))
            control_mean = mean(controls)
            control_std = pstdev(controls) if len(controls) > 1 else 0.0
            signed_delta = int(comp["direction"]) * (observed - control_mean)
            signed_z = signed_delta / control_std if control_std > 1e-12 else signed_delta
            item = component_score_row(row, comp, threshold, "scored")
            item.update({
                "observed_value": observed,
                "control_mean": control_mean,
                "control_std": control_std,
                "signed_z": signed_z,
                "control_percentile": percentile(observed, controls),
                "component_pass": int(signed_z >= threshold),
                "control_count": len(controls),
            })
            out.append(item)
    return out


def component_score_row(row: dict[str, str], comp: dict[str, object], threshold: float, status: str) -> dict[str, object]:
    return {
        "syndrome_id": comp["syndrome_id"],
        "syndrome_component_id": comp["syndrome_component_id"],
        "syndrome_selection_mode": comp["selection_mode"],
        "metric_family": comp["metric_family"],
        "metric_name": comp["metric_name"],
        "window": row.get("window", ""),
        "H_a": row.get("H_a", ""),
        "H_b": row.get("H_b", ""),
        "flow_mode": row.get("flow_mode", ""),
        "probe_key": row.get("probe_key", ""),
        "direction": comp["direction"],
        "group_id": row.get("group_id", ""),
        "seed": row.get("seed", ""),
        "fresh_seed_index": row.get("fresh_seed_index", ""),
        "start_index": row.get("start_index", ""),
        "start_samples": row.get("start_samples", ""),
        "component_status": status,
        "component_threshold": threshold,
        "observed_value": "",
        "control_mean": "",
        "control_std": "",
        "signed_z": "",
        "control_percentile": "",
        "component_pass": 0,
        "control_count": 0,
    }


def control_values_by_context(control_rows: list[dict[str, str]], control_quality: dict[str, str]) -> dict[tuple[str, str, str, str], list[float]]:
    out: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in control_rows:
        name = row.get("control_name", "")
        if control_quality.get(name, "computed") in {"placeholder", "not_available"}:
            continue
        if name in PLACEHOLDER_CONTROLS or name in NOT_AVAILABLE_CONTROLS:
            continue
        metric = row.get("metric_name", "")
        if not metric:
            continue
        key = (
            metric,
            row.get("probe_key", ""),
            row.get("flow_mode", ""),
            row.get("true_window", row.get("window", "")),
        )
        out[key].append(float_or_zero(row.get("control_value")))
    return out


def control_context_key(row: dict[str, str], metric: str) -> tuple[str, str, str, str]:
    return (metric, row.get("probe_key", ""), row.get("flow_mode", ""), row.get("window", ""))


def control_quality_by_name(control_rows: list[dict[str, str]], quality_rows: list[dict[str, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in control_rows:
        name = row.get("control_name", "")
        if not name:
            continue
        out[name] = row.get("control_quality") or row.get("control_status") or "computed"
    for row in quality_rows:
        name = row.get("control_name", "")
        if not name:
            continue
        out[name] = row.get("control_quality") or row.get("control_status") or out.get(name, "computed")
    for name in PLACEHOLDER_CONTROLS:
        out[name] = "placeholder"
    for name in NOT_AVAILABLE_CONTROLS:
        out[name] = "not_available"
    return out


def syndrome_smoke(component_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    keys = ("syndrome_id", "probe_key", "flow_mode", "group_id", "seed", "start_index", "window")
    for key, items in group_by(component_rows, keys).items():
        scored = [item for item in items if item.get("component_status") == "scored"]
        passes = [item for item in scored if int(item.get("component_pass", 0))]
        component_count = len({item.get("syndrome_component_id") for item in items})
        scored_count = len({item.get("syndrome_component_id") for item in scored})
        signed_scores = [float_or_zero(item.get("signed_z")) for item in scored]
        row = {field: value for field, value in zip(keys, key)}
        row.update({
            "component_count": component_count,
            "scored_component_count": scored_count,
            "component_pass_count": len(passes),
            "syndrome_component_pass_fraction": len(passes) / max(1, scored_count),
            "syndrome_joint_pass": int(scored_count >= 2 and len(passes) == scored_count),
            "syndrome_signed_score_mean": mean(signed_scores) if signed_scores else "",
            "syndrome_signed_score_min": min(signed_scores) if signed_scores else "",
            "syndrome_window_coherence_score": len(passes) / max(1, component_count),
            "syndrome_direction_stability": direction_stability(scored),
            "decision_hint": syndrome_decision_hint(scored_count, len(passes)),
        })
        out.append(row)
    return out


def syndrome_vs_controls(component_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (syndrome_id, probe, flow), items in group_by(component_rows, ("syndrome_id", "probe_key", "flow_mode")).items():
        scored = [item for item in items if item.get("component_status") == "scored"]
        passed = [item for item in scored if int(item.get("component_pass", 0))]
        out.append({
            "syndrome_id": syndrome_id,
            "probe_key": probe,
            "flow_mode": flow,
            "component_rows": len(items),
            "scored_component_rows": len(scored),
            "component_pass_rows": len(passed),
            "component_pass_rate": len(passed) / max(1, len(scored)),
            "mean_signed_z": mean(float_or_zero(item.get("signed_z")) for item in scored) if scored else "",
            "control_equivalence_read": "not_control_equivalent_smoke" if passed and len(passed) / max(1, len(scored)) >= 0.5 else "control_equivalent_or_insufficient",
        })
    return out


def syndrome_multiplicity_audit(component_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    syndromes = {row.get("syndrome_id") for row in component_rows}
    components = {row.get("syndrome_component_id") for row in component_rows}
    windows = {row.get("window") for row in component_rows}
    return [{
        "syndrome_selection_mode": "preregistered",
        "syndrome_multiplicity_count": len(syndromes),
        "component_count": len(components),
        "window_pattern_count": len(windows),
        "false_discovery_risk_note": "preregistered_library_scored_first; exploratory_syndromes_not_enabled",
    }]


def syndrome_readiness(
    smoke_rows: list[dict[str, object]],
    phase_b_readiness: list[dict[str, str]],
    control_quality_rows: list[dict[str, str]],
    control_quality: dict[str, str],
) -> list[dict[str, object]]:
    positive = [
        row for row in smoke_rows
        if int(row.get("syndrome_joint_pass", 0)) and row.get("probe_key") not in DIAGNOSTIC_PROBES
    ]
    selected = sorted({str(row.get("syndrome_id")) for row in positive})
    missing_families = missing_mechanism_control_families(control_quality_rows, control_quality)
    missing_mechanism_controls = bool(missing_families)
    decision = "syndrome_smoke_control_equivalent"
    if selected:
        decision = "syndrome_smoke_positive_above_controls"
    elif missing_mechanism_controls:
        decision = "syndrome_smoke_insufficient_data"
    return [{
        "decision_class": decision,
        "stage_b_allowed": int(bool(selected) or missing_mechanism_controls),
        "selected_syndrome_ids": json.dumps(selected),
        "selection_mode": "preregistered",
        "selection_reason": readiness_reason(selected, missing_families),
        "excluded_positive_probes": json.dumps(sorted(DIAGNOSTIC_PROBES)),
        "excluded_positive_controls": json.dumps(sorted(PLACEHOLDER_CONTROLS | NOT_AVAILABLE_CONTROLS)),
        "missing_mechanism_control_families": json.dumps(missing_families),
        "phase_b_prior_decision": phase_b_readiness[0].get("decision_class", "") if phase_b_readiness else "",
        "holdout_scoring_count": 0,
    }]


def missing_mechanism_control_families(
    quality_rows: list[dict[str, str]],
    control_quality: dict[str, str],
) -> list[str]:
    row_quality = {
        str(row.get("control_name", "")): str(row.get("control_quality") or row.get("control_status") or "")
        for row in quality_rows
        if row.get("control_name")
    }
    missing = []
    for family, aliases in MECHANISM_CONTROL_FAMILIES.items():
        qualities = [
            row_quality.get(name) or control_quality.get(name, "missing")
            for name in aliases
            if name in row_quality or name in control_quality
        ]
        if not qualities or all(quality in WEAK_CONTROL_QUALITIES for quality in qualities):
            missing.append(family)
    return sorted(missing)


def readiness_reason(selected: list[str], missing_families: list[str]) -> str:
    if selected:
        return "joint_pass_in_stage_a"
    if missing_families:
        return "missing_mechanism_controls_dominate_uncertainty"
    return "no_preregistered_syndrome_above_controls"


def control_match_decomposition(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        out.append({
            "metric_family": row.get("metric_family", ""),
            "metric_name": row.get("metric_name", ""),
            "probe_key": row.get("probe_key", ""),
            "flow_mode": row.get("flow_mode", ""),
            "observed_recurrence_rate": row.get("observed_recurrence_rate", ""),
            "control_recurrence_mean": row.get("control_recurrence_mean", ""),
            "recurrence_excess": row.get("recurrence_excess", ""),
            "control_count": row.get("control_count", ""),
            "weak_control_flag": row.get("weak_control_flag", ""),
            "control_match_class": control_match_class(row),
        })
    return out


def top_control_equivalent_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    eligible = [row for row in rows if float_or_zero(row.get("observed_recurrence_rate")) > 0]
    eligible.sort(key=lambda row: (float_or_zero(row.get("observed_recurrence_rate")), -abs(float_or_zero(row.get("recurrence_excess")))), reverse=True)
    return [{**row, "control_match_class": control_match_class(row)} for row in eligible[:50]]


def control_match_by_control_type(rows: list[dict[str, str]], control_quality: dict[str, str]) -> list[dict[str, object]]:
    out = []
    for (name,), items in group_by(rows, ("control_name",)).items():
        values = [float_or_zero(row.get("absolute_delta")) for row in items if row.get("absolute_delta", "") != ""]
        out.append({
            "control_name": name,
            "control_quality": control_quality.get(str(name), "computed"),
            "rows": len(items),
            "mean_absolute_delta": mean(values) if values else "",
            "metric_count": len({row.get("metric_name") for row in items}),
            "probe_count": len({row.get("probe_key") for row in items}),
        })
    return out


def flow_mode_decomposition(metric_rows: list[dict[str, str]], effect_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for (flow,), items in group_by(metric_rows, ("flow_mode",)).items():
        effects = [row for row in effect_rows if row.get("flow_mode") == flow]
        out.append({
            "flow_mode": flow,
            "metric_rows": len(items),
            "effect_rows": len(effects),
            "mean_no_window_target_rate": mean(float_or_zero(row.get("no_window_target_rate")) for row in items) if items else "",
            "non_equivalent_effect_rate": sum(int(row.get("effect_direction") != "control_equivalent") for row in effects) / max(1, len(effects)),
        })
    return out


def window_decomposition(metric_rows: list[dict[str, str]], control_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for (window,), items in group_by(metric_rows, ("window",)).items():
        controls = [row for row in control_rows if row.get("true_window") == window or row.get("window") == window]
        out.append({
            "window": window,
            "metric_rows": len(items),
            "control_rows": len(controls),
            "mean_frontier_size_a": mean(float_or_zero(row.get("frontier_size_a")) for row in items) if items else "",
            "mean_frontier_size_b": mean(float_or_zero(row.get("frontier_size_b")) for row in items) if items else "",
        })
    return out


def probe_dependency(metric_rows: list[dict[str, str]], effect_rows: list[dict[str, str]], recurrence_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for (probe,), items in group_by(metric_rows, ("probe_key",)).items():
        effects = [row for row in effect_rows if row.get("probe_key") == probe]
        recurrence = [row for row in recurrence_rows if row.get("probe_key") == probe]
        out.append({
            "probe_key": probe,
            "probe_role": "diagnostic_or_identity_control" if probe in DIAGNOSTIC_PROBES else "eligible_design_probe",
            "metric_rows": len(items),
            "effect_rows": len(effects),
            "recurrence_rows": len(recurrence),
            "max_observed_recurrence_rate": max((float_or_zero(row.get("observed_recurrence_rate")) for row in recurrence), default=0.0),
        })
    return out


def control_match_class(row: dict[str, str]) -> str:
    excess = float_or_zero(row.get("recurrence_excess"))
    observed = float_or_zero(row.get("observed_recurrence_rate"))
    weak = int(float_or_zero(row.get("weak_control_flag")))
    if weak:
        return "weak_control"
    if observed <= 0:
        return "no_observed_recurrence"
    if excess > 0:
        return "observed_above_controls"
    return "control_equivalent"


def direction_stability(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "insufficient_data"
    signs = Counter("positive" if float_or_zero(row.get("signed_z")) >= 0 else "negative" for row in rows)
    _direction, count = signs.most_common(1)[0]
    return "stable_direction" if count / len(rows) >= 0.70 else "mixed_direction"


def syndrome_decision_hint(scored_count: int, pass_count: int) -> str:
    if scored_count < 2:
        return "insufficient_components"
    if pass_count == scored_count:
        return "joint_pass"
    if pass_count:
        return "partial_component_pass"
    return "no_component_pass"


def percentile(value: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return sum(int(value >= item) for item in controls) / len(controls)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_report(
    out_dir: Path,
    status: dict[str, object],
    missing: list[str],
    readiness: list[dict[str, object]],
    smoke_rows: list[dict[str, object]],
    top_rows: list[dict[str, object]],
) -> None:
    lines = [
        "# Frontier-Transform Syndrome Mechanism Audit: Stage A",
        "",
        "## Claim Boundary",
        "",
        "Read-only Stage A audit. No systems generated, no holdout scoring, no n=6, no alphabet expansion.",
        "",
    ]
    if missing:
        lines.extend([
            "## Missing Inputs",
            "",
            "The Phase B CSV directory is incomplete. Required missing files:",
            "",
            *[f"- `{name}`" for name in missing],
            "",
        ])
    else:
        decision = readiness[0] if readiness else {}
        lines.extend([
            "## Decision",
            "",
            f"Decision class: `{decision.get('decision_class', 'unknown')}`",
            f"Stage B allowed: `{decision.get('stage_b_allowed', 0)}`",
            f"Selected syndromes: `{decision.get('selected_syndrome_ids', '[]')}`",
            "",
            "## Syndrome Smoke",
            "",
            f"Syndrome smoke rows: `{len(smoke_rows)}`",
            "",
            "## Top Control-Equivalent Rows",
            "",
            f"Rows summarized: `{len(top_rows)}`",
            "",
        ])
    lines.extend([
        "## Output Manifest",
        "",
        "See `output_manifest.json`.",
        "",
    ])
    (out_dir / "phase_b_postmortem_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(out_dir: Path) -> None:
    rows = []
    for name in OUTPUTS:
        path = out_dir / name
        rows.append({"file": name, "exists": path.exists(), "status": "present" if path.exists() else "missing"})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
