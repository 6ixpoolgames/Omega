from __future__ import annotations

import argparse
import csv
import json
import random
import time
from bisect import bisect_right
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev

from .run_focused_boundary_recurrence import float_or_zero, group_by, write_csv
from .run_frontier_transform_b0 import FLOW_MODES, PROBES, WINDOWS, metric_family


REQUIRED_PHASE_B_INPUTS = (
    "phase_b_design_metric_rows.csv",
    "phase_b_directional_effects.csv",
    "phase_b_metric_family_recurrence.csv",
    "phase_b_matched_recurrence_controls.csv",
    "phase_b_recurrence_excess.csv",
    "phase_b_control_quality_audit.csv",
    "phase_b_no_target_audit.csv",
    "phase_b_phase_c_readiness.csv",
)
CONTROL_INPUT_CANDIDATES = (
    "phase_b_stage_a_control_values.csv",
    "phase_b_design_control_rows.csv",
)

OUTPUTS = (
    "syndrome_manifest.json",
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
    "phase_b_syndrome_marginal_preserving_controls.csv",
    "phase_b_syndrome_component_ablation.csv",
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
    parser.add_argument("--marginal-control-replicates", type=int, default=500)
    parser.add_argument("--marginal-control-seed", type=int, default=20260528)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    out_dir = args.out or (args.phase_b_dir / "stage_a_syndrome_audit")
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = syndrome_manifest()
    write_syndrome_manifest(out_dir, manifest)
    missing = [name for name in REQUIRED_PHASE_B_INPUTS if not (args.phase_b_dir / name).exists()]
    if not any((args.phase_b_dir / name).exists() for name in CONTROL_INPUT_CANDIDATES):
        missing.append("phase_b_stage_a_control_values.csv or phase_b_design_control_rows.csv")
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
        "marginal_control_replicates": args.marginal_control_replicates,
        "marginal_control_seed": args.marginal_control_seed,
        "syndrome_manifest_written_before_scoring": 1,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    errors: list[dict[str, object]] = []
    if missing:
        status["status"] = "BLOCKED_MISSING_INPUTS"
        status["missing_input_count"] = len(missing)
        write_missing_outputs(out_dir, status, missing, started)
        return

    metric_rows = read_csv(args.phase_b_dir / "phase_b_design_metric_rows.csv")
    control_source_name, control_rows = read_control_rows(args.phase_b_dir)
    effect_rows = read_csv(args.phase_b_dir / "phase_b_directional_effects.csv")
    recurrence_rows = read_csv(args.phase_b_dir / "phase_b_matched_recurrence_controls.csv")
    control_quality_rows = read_csv(args.phase_b_dir / "phase_b_control_quality_audit.csv")
    readiness_rows = read_csv(args.phase_b_dir / "phase_b_phase_c_readiness.csv")

    control_quality = control_quality_by_name(control_rows, control_quality_rows)
    postmortem_control_decomposition = control_match_decomposition(recurrence_rows)
    top_control_equivalent = top_control_equivalent_rows(recurrence_rows)
    by_control = control_match_by_control_type(recurrence_rows, effect_rows, control_quality)
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
    marginal_controls = marginal_preserving_syndrome_controls(
        component_scores,
        max(100, args.marginal_control_replicates),
        args.marginal_control_seed,
    )
    ablation = syndrome_component_ablation(component_scores, marginal_controls)
    syndrome_controls = syndrome_vs_controls(component_scores, marginal_controls, ablation)
    multiplicity = syndrome_multiplicity_audit(component_scores)
    readiness = syndrome_readiness(
        syndrome_controls,
        ablation,
        readiness_rows,
        control_quality_rows,
        control_quality,
    )

    write_csv(out_dir / "phase_b_postmortem_control_match_decomposition.csv", postmortem_control_decomposition)
    write_csv(out_dir / "phase_b_postmortem_top_control_equivalent_rows.csv", top_control_equivalent)
    write_csv(out_dir / "phase_b_postmortem_control_match_by_control_type.csv", by_control)
    write_csv(out_dir / "phase_b_postmortem_flow_mode_decomposition.csv", by_flow)
    write_csv(out_dir / "phase_b_postmortem_window_decomposition.csv", by_window)
    write_csv(out_dir / "phase_b_postmortem_probe_dependency.csv", by_probe)
    write_csv(out_dir / "phase_b_syndrome_component_scores.csv", component_scores)
    write_csv(out_dir / "phase_b_syndrome_smoke.csv", smoke_rows)
    write_csv(out_dir / "phase_b_syndrome_vs_controls.csv", syndrome_controls)
    write_csv(out_dir / "phase_b_syndrome_marginal_preserving_controls.csv", marginal_controls)
    write_csv(out_dir / "phase_b_syndrome_component_ablation.csv", ablation)
    write_csv(out_dir / "phase_b_syndrome_multiplicity_audit.csv", multiplicity)
    write_csv(out_dir / "phase_b_syndrome_readiness.csv", readiness)
    write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, status, missing, readiness, smoke_rows, top_control_equivalent)
    status["status"] = "COMPLETED"
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["metric_rows"] = len(metric_rows)
    status["control_rows"] = len(control_rows)
    status["control_source"] = control_source_name
    status["syndrome_component_rows"] = len(component_scores)
    status["syndrome_manifest_rows"] = len(manifest)
    status["marginal_preserving_control_rows"] = len(marginal_controls)
    status["component_ablation_rows"] = len(ablation)
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


def syndrome_manifest() -> list[dict[str, object]]:
    windows = [f"{left}->{right}" for left, right in WINDOWS]
    eligible_probes = [probe for probe in PROBES if probe not in DIAGNOSTIC_PROBES]
    out = []
    for (syndrome_id,), components in group_by(syndrome_library(), ("syndrome_id",)).items():
        component_rows = sorted(components, key=lambda row: str(row["syndrome_component_id"]))
        out.append(
            {
                "syndrome_id": syndrome_id,
                "selection_mode": "preregistered",
                "readiness_allowed": True,
                "component_count": len(component_rows),
                "metric_components": [
                    {
                        "component_id": row["syndrome_component_id"],
                        "metric_name": row["metric_name"],
                        "metric_family": row["metric_family"],
                    }
                    for row in component_rows
                ],
                "allowed_windows": windows,
                "allowed_window_relation": "canonical_phase_b_windows_only",
                "allowed_flow_modes": list(FLOW_MODES),
                "allowed_probes": eligible_probes,
                "excluded_positive_probes": sorted(DIAGNOSTIC_PROBES),
                "component_signs": {
                    str(row["syndrome_component_id"]): int(row["direction"])
                    for row in component_rows
                },
                "component_threshold_rule": "signed_z >= component_z_threshold",
                "minimum_component_pass_count": len(component_rows),
                "joint_pass_rule": "all_scored_components_pass_and_at_least_two_scored_components",
                "informal_name_optional": informal_name(str(syndrome_id)),
                "informal_interpretation": informal_interpretation(str(syndrome_id)),
            }
        )
    return out


def write_syndrome_manifest(out_dir: Path, manifest: list[dict[str, object]]) -> None:
    (out_dir / "syndrome_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def syndrome_library() -> list[dict[str, object]]:
    return [
        component("SYN_A_low_growth_high_bottleneck_low_offdiag", "growth_low", "frontier_growth_ratio", -1),
        component("SYN_A_low_growth_high_bottleneck_low_offdiag", "bottleneck_high", "frontier_bottleneck_index", 1),
        component("SYN_A_low_growth_high_bottleneck_low_offdiag", "offdiag_low", "off_diagonal_transform_mass", -1),
        component("SYN_B_high_turnover_high_offdiag_high_window_delta", "turnover_high", "support_turnover_rate", 1),
        component("SYN_B_high_turnover_high_offdiag_high_window_delta", "offdiag_high", "off_diagonal_transform_mass", 1),
        component("SYN_B_high_turnover_high_offdiag_high_window_delta", "window_delta_high", "window_metric_vector_l2_distance_to_next", 1),
        component("SYN_C_low_growth_high_concentration_low_entropy", "growth_low", "frontier_growth_ratio", -1),
        component("SYN_C_low_growth_high_concentration_low_entropy", "concentration_high", "top_k_flow_concentration", 1),
        component("SYN_C_low_growth_high_concentration_low_entropy", "transition_entropy_low", "transition_matrix_entropy", -1),
        component("SYN_D_high_turnover_high_entropy_low_bottleneck_control", "turnover_high", "support_turnover_rate", 1),
        component("SYN_D_high_turnover_high_entropy_low_bottleneck_control", "transition_entropy_high", "transition_matrix_entropy", 1),
        component("SYN_D_high_turnover_high_entropy_low_bottleneck_control", "bottleneck_low", "frontier_bottleneck_index", -1),
        component("SYN_E_transition_then_persistence_cascade", "signature_js_next_low", "signature_distribution_js_to_next_window", -1),
        component("SYN_E_transition_then_persistence_cascade", "diagonal_persistence_high", "diagonal_persistence_mass", 1),
        component("SYN_E_transition_then_persistence_cascade", "flow_concentration_high", "top_k_flow_concentration", 1),
    ]


def informal_name(syndrome_id: str) -> str:
    return {
        "SYN_A_low_growth_high_bottleneck_low_offdiag": "stabilizing_boundary_syndrome",
        "SYN_B_high_turnover_high_offdiag_high_window_delta": "transition_boundary_syndrome",
        "SYN_C_low_growth_high_concentration_low_entropy": "compression_funnel_syndrome",
        "SYN_D_high_turnover_high_entropy_low_bottleneck_control": "diffusive_noise_syndrome",
        "SYN_E_transition_then_persistence_cascade": "recurrence_cascade_syndrome",
    }.get(syndrome_id, "")


def informal_interpretation(syndrome_id: str) -> str:
    return {
        "SYN_A_low_growth_high_bottleneck_low_offdiag": "low growth with bottlenecking and reduced off-diagonal transform mass",
        "SYN_B_high_turnover_high_offdiag_high_window_delta": "high support turnover with high off-diagonal mass and window change",
        "SYN_C_low_growth_high_concentration_low_entropy": "low growth with concentrated low-entropy transition flow",
        "SYN_D_high_turnover_high_entropy_low_bottleneck_control": "high turnover and entropy without bottleneck concentration",
        "SYN_E_transition_then_persistence_cascade": "low next-window signature divergence with persistence and flow concentration",
    }.get(syndrome_id, "")


def read_control_rows(phase_b_dir: Path) -> tuple[str, list[dict[str, str]]]:
    for name in CONTROL_INPUT_CANDIDATES:
        path = phase_b_dir / name
        if path.exists():
            return name, read_csv(path)
    return "", []


def component(syndrome_id: str, component_id: str, metric_name: str, direction: int) -> dict[str, object]:
    return {
        "syndrome_id": syndrome_id,
        "syndrome_component_id": component_id,
        "metric_name": metric_name,
        "metric_family": metric_family(metric_name),
        "direction": direction,
        "selection_mode": "preregistered",
        "readiness_allowed": True,
    }


def syndrome_component_scores(
    metric_rows: list[dict[str, str]],
    control_rows: list[dict[str, str]],
    control_quality: dict[str, str],
    threshold: float,
) -> list[dict[str, object]]:
    control_summaries = control_summaries_by_context(control_rows, control_quality)
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
            summary = control_summaries.get(key)
            if summary is None:
                out.append(component_score_row(row, comp, threshold, "unavailable_control"))
                continue
            observed = float_or_zero(row.get(metric))
            control_mean = float(summary["mean"])
            control_std = float(summary["std"])
            signed_delta = int(comp["direction"]) * (observed - control_mean)
            signed_z = signed_delta / control_std if control_std > 1e-12 else signed_delta
            item = component_score_row(row, comp, threshold, "scored")
            item.update({
                "observed_value": observed,
                "control_mean": control_mean,
                "control_std": control_std,
                "signed_z": signed_z,
                "control_percentile": percentile_from_sorted(observed, summary["sorted_values"]),
                "component_pass": int(signed_z >= threshold),
                "control_count": summary["count"],
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
        "mechanism_condition": row.get("mechanism_condition", ""),
        "mechanism_control_name": row.get("mechanism_control_name", ""),
        "mechanism_control_strength": row.get("mechanism_control_strength", ""),
        "mechanism_strength_label": row.get("mechanism_strength_label", ""),
        "baseline_system_id": row.get("baseline_system_id", ""),
        "control_system_id": row.get("control_system_id", ""),
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


def control_summaries_by_context(control_rows: list[dict[str, str]], control_quality: dict[str, str]) -> dict[tuple[str, str, str, str], dict[str, object]]:
    out: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    syndrome_metrics = {str(component["metric_name"]) for component in syndrome_library()}
    for row in control_rows:
        name = row.get("control_name", "")
        if control_quality.get(name, "computed") in {"placeholder", "not_available"}:
            continue
        if name in PLACEHOLDER_CONTROLS or name in NOT_AVAILABLE_CONTROLS:
            continue
        metric = row.get("metric_name", "")
        if not metric:
            continue
        if metric not in syndrome_metrics:
            continue
        key = (
            metric,
            row.get("probe_key", ""),
            row.get("flow_mode", ""),
            row.get("true_window", row.get("window", "")),
        )
        out[key].append(float_or_zero(row.get("control_value")))
    summaries: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for key, values in out.items():
        sorted_values = sorted(values)
        summaries[key] = {
            "count": len(values),
            "mean": mean(values),
            "std": pstdev(values) if len(values) > 1 else 0.0,
            "sorted_values": sorted_values,
        }
    return summaries


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


def marginal_preserving_syndrome_controls(
    component_rows: list[dict[str, object]],
    replicates: int,
    seed: int,
) -> list[dict[str, object]]:
    out = []
    for context in component_contexts(component_rows):
        rng = random.Random(stable_context_seed(seed, context["syndrome_id"], context["probe_key"], context["flow_mode"]))
        controls = []
        vectors = context["component_vectors"]
        component_ids = list(vectors)
        for _replicate_id in range(replicates):
            shuffled: dict[str, list[int]] = {}
            for component_id, vector in vectors.items():
                copied = list(vector)
                rng.shuffle(copied)
                shuffled[component_id] = copied
            controls.append(joint_rate(shuffled.values()))
        observed = float(context["observed_joint_rate"])
        control_mean = mean(controls) if controls else 0.0
        percentile_value = percentile(observed, controls)
        for replicate_id, control_rate in enumerate(controls):
            for component_id in component_ids:
                out.append(
                    {
                        "syndrome_id": context["syndrome_id"],
                        "probe_key": context["probe_key"],
                        "flow_mode": context["flow_mode"],
                        "replicate_id": replicate_id,
                        "component_id": component_id,
                        "component_marginal_rate": context["component_marginal_rates"][component_id],
                        "observed_joint_rate": observed,
                        "control_joint_rate": control_rate,
                        "control_joint_rate_mean": control_mean,
                        "joint_rate_excess": observed - control_mean,
                        "joint_rate_percentile": percentile_value,
                        "replicate_count": replicates,
                        "complete_unit_count": context["complete_unit_count"],
                        "control_family": "component_marginal_preserving_syndrome_control",
                    }
                )
    return out


def syndrome_component_ablation(
    component_rows: list[dict[str, object]],
    marginal_controls: list[dict[str, object]],
) -> list[dict[str, object]]:
    control_summary = marginal_control_summary(marginal_controls)
    out = []
    for context in component_contexts(component_rows):
        key = (context["syndrome_id"], context["probe_key"], context["flow_mode"])
        controls = control_summary.get(key, {})
        vectors = context["component_vectors"]
        component_ids = list(vectors)
        full_score = float(context["observed_joint_rate"])
        best_single = max((context["component_marginal_rates"][component_id] for component_id in component_ids), default=0.0)
        pair_scores = [
            joint_rate(vectors[component_id] for component_id in pair)
            for pair in combinations(component_ids, 2)
        ]
        best_pair = max(pair_scores, default=0.0)
        full_excess = float(controls.get("joint_rate_excess", 0.0) or 0.0)
        single_component_driven = int(full_excess > 0 and best_single >= 0.90 and best_pair <= full_score + 1e-12)
        decision = "single_component_driven_not_joint_syndrome" if single_component_driven else "joint_syndrome_not_single_component_driven"
        for removed in component_ids:
            kept = [component_id for component_id in component_ids if component_id != removed]
            leave_one_out = joint_rate(vectors[component_id] for component_id in kept)
            out.append(
                {
                    "syndrome_id": context["syndrome_id"],
                    "probe_key": context["probe_key"],
                    "flow_mode": context["flow_mode"],
                    "ablation_kind": "leave_one_component_out",
                    "component_removed": removed,
                    "component_subset_json": json.dumps(kept),
                    "full_syndrome_score": full_score,
                    "ablated_score": leave_one_out,
                    "best_single_component_score": best_single,
                    "best_pair_score": best_pair,
                    "single_component_explained_fraction": best_single / full_score if full_score > 0 else 0.0,
                    "joint_rate_excess": full_excess,
                    "joint_rate_percentile": controls.get("joint_rate_percentile", ""),
                    "decision_class": decision,
                    "complete_unit_count": context["complete_unit_count"],
                }
            )
    return out


def syndrome_vs_controls(
    component_rows: list[dict[str, object]],
    marginal_controls: list[dict[str, object]],
    ablation_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    marginal_summary = marginal_control_summary(marginal_controls)
    ablation_summary = ablation_by_context(ablation_rows)
    out = []
    for (syndrome_id, probe, flow), items in group_by(component_rows, ("syndrome_id", "probe_key", "flow_mode")).items():
        scored = [item for item in items if item.get("component_status") == "scored"]
        passed = [item for item in scored if int(item.get("component_pass", 0))]
        key = (str(syndrome_id), str(probe), str(flow))
        controls = marginal_summary.get(key, {})
        observed_joint = float_or_zero(controls.get("observed_joint_rate"))
        control_mean = float_or_zero(controls.get("control_joint_rate_mean"))
        percentile_value = float_or_zero(controls.get("joint_rate_percentile"))
        ablation = ablation_summary.get(key, {})
        marginal_available = bool(controls)
        apparent_joint_positive = (
            marginal_available
            and
            observed_joint > control_mean
            and percentile_value >= 0.80
            and str(probe) not in DIAGNOSTIC_PROBES
        )
        out.append({
            "syndrome_id": syndrome_id,
            "probe_key": probe,
            "flow_mode": flow,
            "selection_mode": "preregistered",
            "readiness_allowed": int(str(probe) not in DIAGNOSTIC_PROBES),
            "component_rows": len(items),
            "scored_component_rows": len(scored),
            "component_pass_rows": len(passed),
            "component_pass_rate": len(passed) / max(1, len(scored)),
            "mean_signed_z": mean(float_or_zero(item.get("signed_z")) for item in scored) if scored else "",
            "observed_joint_rate": observed_joint,
            "component_marginal_preserving_control_mean": control_mean,
            "joint_rate_excess": observed_joint - control_mean,
            "joint_rate_percentile": percentile_value,
            "marginal_control_replicates": controls.get("replicate_count", ""),
            "single_component_ablation_decision": ablation.get("decision_class", ""),
            "control_equivalence_read": control_equivalence_read(apparent_joint_positive, marginal_available),
            "stage_a_decision_class": syndrome_stage_a_decision(apparent_joint_positive, ablation, marginal_available),
        })
    return out


def component_contexts(component_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    library_components = {
        syndrome_id: [str(row["syndrome_component_id"]) for row in sorted(items, key=lambda item: str(item["syndrome_component_id"]))]
        for (syndrome_id,), items in group_by(syndrome_library(), ("syndrome_id",)).items()
    }
    contexts = []
    for (syndrome_id, probe, flow), items in group_by(component_rows, ("syndrome_id", "probe_key", "flow_mode")).items():
        expected_components = library_components.get(str(syndrome_id), [])
        units: dict[tuple[object, ...], dict[str, int]] = defaultdict(dict)
        for item in items:
            if item.get("component_status") != "scored":
                continue
            unit_key = (
                item.get("group_id"),
                item.get("seed"),
                item.get("start_index"),
                item.get("start_samples"),
                item.get("window"),
            )
            units[unit_key][str(item.get("syndrome_component_id"))] = int(item.get("component_pass", 0))
        complete_units = [
            unit for unit in units.values()
            if all(component_id in unit for component_id in expected_components)
        ]
        if not complete_units or not expected_components:
            continue
        vectors = {
            component_id: [int(unit[component_id]) for unit in complete_units]
            for component_id in expected_components
        }
        contexts.append(
            {
                "syndrome_id": str(syndrome_id),
                "probe_key": str(probe),
                "flow_mode": str(flow),
                "component_vectors": vectors,
                "component_marginal_rates": {
                    component_id: mean(vector) if vector else 0.0
                    for component_id, vector in vectors.items()
                },
                "observed_joint_rate": joint_rate(vectors.values()),
                "complete_unit_count": len(complete_units),
            }
        )
    return contexts


def joint_rate(vectors: object) -> float:
    vector_list = [list(vector) for vector in vectors]
    if not vector_list or not vector_list[0]:
        return 0.0
    count = min(len(vector) for vector in vector_list)
    if count == 0:
        return 0.0
    return sum(int(all(vector[index] for vector in vector_list)) for index in range(count)) / count


def stable_context_seed(base_seed: int, syndrome_id: object, probe: object, flow: object) -> int:
    text = f"{base_seed}|{syndrome_id}|{probe}|{flow}"
    value = 0
    for char in text:
        value = (value * 131 + ord(char)) % (2**32)
    return value


def marginal_control_summary(rows: list[dict[str, object]]) -> dict[tuple[str, str, str], dict[str, object]]:
    grouped = group_by(rows, ("syndrome_id", "probe_key", "flow_mode"))
    out: dict[tuple[str, str, str], dict[str, object]] = {}
    for key, items in grouped.items():
        controls_by_replicate = {
            int(float_or_zero(item.get("replicate_id"))): float_or_zero(item.get("control_joint_rate"))
            for item in items
        }
        controls = list(controls_by_replicate.values())
        first = items[0] if items else {}
        out[(str(key[0]), str(key[1]), str(key[2]))] = {
            "observed_joint_rate": float_or_zero(first.get("observed_joint_rate")),
            "control_joint_rate_mean": mean(controls) if controls else 0.0,
            "joint_rate_excess": float_or_zero(first.get("observed_joint_rate")) - (mean(controls) if controls else 0.0),
            "joint_rate_percentile": float_or_zero(first.get("joint_rate_percentile")),
            "replicate_count": int(float_or_zero(first.get("replicate_count"))),
            "complete_unit_count": int(float_or_zero(first.get("complete_unit_count"))),
        }
    return out


def ablation_by_context(rows: list[dict[str, object]]) -> dict[tuple[str, str, str], dict[str, object]]:
    out = {}
    for (syndrome_id, probe, flow), items in group_by(rows, ("syndrome_id", "probe_key", "flow_mode")).items():
        if items:
            out[(str(syndrome_id), str(probe), str(flow))] = dict(items[0])
    return out


def control_equivalence_read(apparent_joint_positive: bool, marginal_available: bool) -> str:
    if not marginal_available:
        return "underdetermined_missing_marginal_preserving_control"
    if apparent_joint_positive:
        return "above_marginal_preserving_controls"
    return "marginal_control_equivalent_or_insufficient"


def syndrome_stage_a_decision(apparent_joint_positive: bool, ablation: dict[str, object], marginal_available: bool) -> str:
    if not marginal_available:
        return "syndrome_smoke_insufficient_data"
    if not apparent_joint_positive:
        return "syndrome_smoke_control_equivalent"
    if ablation.get("decision_class") == "single_component_driven_not_joint_syndrome":
        return "syndrome_smoke_single_component_driven"
    return "syndrome_smoke_joint_positive_above_marginal_controls"


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
    syndrome_controls: list[dict[str, object]],
    ablation_rows: list[dict[str, object]],
    phase_b_readiness: list[dict[str, str]],
    control_quality_rows: list[dict[str, str]],
    control_quality: dict[str, str],
) -> list[dict[str, object]]:
    missing_families = missing_mechanism_control_families(control_quality_rows, control_quality)
    ablation_summary = ablation_by_context(ablation_rows)
    eligible = []
    single_component = []
    apparent_positive = []
    insufficient = []
    for row in syndrome_controls:
        if str(row.get("selection_mode")) != "preregistered":
            continue
        if not int(float_or_zero(row.get("readiness_allowed"))):
            continue
        if row.get("probe_key") in DIAGNOSTIC_PROBES:
            continue
        if row.get("stage_a_decision_class") == "syndrome_smoke_insufficient_data":
            insufficient.append(row)
            continue
        joint_positive = (
            float_or_zero(row.get("observed_joint_rate")) > float_or_zero(row.get("component_marginal_preserving_control_mean"))
            and float_or_zero(row.get("joint_rate_percentile")) >= 0.80
        )
        if not joint_positive:
            continue
        apparent_positive.append(row)
        key = (str(row.get("syndrome_id")), str(row.get("probe_key")), str(row.get("flow_mode")))
        ablation = ablation_summary.get(key, {})
        if ablation.get("decision_class") == "single_component_driven_not_joint_syndrome":
            single_component.append(row)
            continue
        eligible.append(row)
    selected = sorted({str(row.get("syndrome_id")) for row in eligible})
    if selected:
        decision = "syndrome_smoke_joint_positive_above_marginal_controls"
    elif single_component:
        decision = "syndrome_smoke_single_component_driven"
    elif apparent_positive:
        decision = "syndrome_smoke_insufficient_data"
    elif syndrome_controls:
        decision = "syndrome_smoke_control_equivalent"
    else:
        decision = "syndrome_smoke_insufficient_data"
    return [{
        "decision_class": decision,
        "stage_b_allowed": int(bool(selected)),
        "selected_syndrome_ids": json.dumps(selected),
        "selection_mode": "preregistered",
        "selection_reason": readiness_reason(selected, missing_families, decision),
        "excluded_positive_probes": json.dumps(sorted(DIAGNOSTIC_PROBES)),
        "excluded_positive_controls": json.dumps(sorted(PLACEHOLDER_CONTROLS | NOT_AVAILABLE_CONTROLS)),
        "missing_mechanism_control_families": json.dumps(missing_families),
        "apparent_positive_contexts": len(apparent_positive),
        "single_component_driven_contexts": len(single_component),
        "insufficient_marginal_control_contexts": len(insufficient),
        "marginal_control_minimum_replicates_met": int(marginal_replicate_minimum_met(syndrome_controls)),
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


def readiness_reason(selected: list[str], missing_families: list[str], decision: str) -> str:
    if selected:
        return "joint_rate_above_marginal_preserving_controls_and_not_single_component_driven"
    if decision == "syndrome_smoke_single_component_driven":
        return "apparent_joint_positive_explained_by_component_ablation"
    if missing_families:
        return "missing_mechanism_controls_remain_but_stage_a_joint_control_gate_not_met"
    return "no_preregistered_syndrome_above_marginal_preserving_controls"


def marginal_replicate_minimum_met(rows: list[dict[str, object]]) -> bool:
    available = [
        row for row in rows
        if row.get("marginal_control_replicates", "") != ""
    ]
    return bool(available) and all(float_or_zero(row.get("marginal_control_replicates")) >= 100 for row in available)


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


def control_match_by_control_type(
    recurrence_rows: list[dict[str, str]],
    effect_rows: list[dict[str, str]],
    control_quality: dict[str, str],
) -> list[dict[str, object]]:
    out = []
    recurrence_by_key = {
        (row.get("metric_family", ""), row.get("metric_name", ""), row.get("probe_key", ""), row.get("flow_mode", "")): row
        for row in recurrence_rows
    }
    for row in effect_rows:
        metric = row.get("metric_name", "")
        if not metric:
            continue
        key = (row.get("metric_family", ""), metric, row.get("probe_key", ""), row.get("flow_mode", ""))
        recurrence = recurrence_by_key.get(key, {})
        observed = float_or_zero(recurrence.get("observed_recurrence_rate"))
        control_recurrence = int(
            float_or_zero(row.get("absolute_effect_size")) >= 0.10
            and row.get("effect_direction") != "control_equivalent"
            and row.get("control_quality") == "computed"
        )
        excess = observed - control_recurrence
        out.append(
            {
                "metric_family": row.get("metric_family", ""),
                "metric_name": metric,
                "probe_key": row.get("probe_key", ""),
                "flow_mode": row.get("flow_mode", ""),
                "window": "all_windows",
                "observed_recurrence_rate": observed,
                "control_name": row.get("control_name", ""),
                "control_quality": control_quality.get(str(row.get("control_name", "")), row.get("control_quality", "")),
                "control_recurrence_mean": control_recurrence,
                "recurrence_excess_vs_this_control": excess,
                "control_match_flag": int(excess <= 0),
                "effect_direction": row.get("effect_direction", ""),
                "absolute_effect_size": row.get("absolute_effect_size", ""),
                "comparison_count": row.get("comparison_count", ""),
            }
        )
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


def percentile_from_sorted(value: float, controls: object) -> float:
    sorted_controls = controls if isinstance(controls, list) else []
    if not sorted_controls:
        return 0.0
    return bisect_right(sorted_controls, value) / len(sorted_controls)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
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
            "## Addendum Controls",
            "",
            "The preregistered metric-native syndrome manifest was written before scoring.",
            "Marginal-preserving controls and component ablations were emitted before readiness.",
            "",
            f"Apparent positive contexts: `{decision.get('apparent_positive_contexts', 0)}`",
            f"Single-component driven contexts: `{decision.get('single_component_driven_contexts', 0)}`",
            f"Insufficient marginal-control contexts: `{decision.get('insufficient_marginal_control_contexts', 0)}`",
            f"Marginal replicate minimum met: `{decision.get('marginal_control_minimum_replicates_met', 0)}`",
            "",
            "Diagnostic probes excluded from readiness:",
            "",
            f"`{decision.get('excluded_positive_probes', '[]')}`",
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
        exists = path.exists() or name == "output_manifest.json"
        rows.append({"file": name, "exists": exists, "status": "present" if exists else "missing"})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
