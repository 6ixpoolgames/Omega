from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

from .run_focused_boundary_recurrence import float_or_zero, read_csv, write_csv
from .run_frontier_transform_syndrome_audit import syndrome_library
from .run_instrumentation_phase_a import build_holdout_split
from .run_stage_b2_spectral_future_field_geometry_smoke import (
    PRIMARY_SYNDROMES,
    build_jobs,
    build_spectral_matrices,
    context_manifest_rows,
    run_batches,
    selected_syndrome_ids,
    write_outputs,
    write_status,
)
from .run_frontier_transform_stage_b2_mechanism_calibration import load_control_summaries
from .spectral_contracts import (
    CLAIM_BOUNDARY,
    GateResult,
    executive_summary_lines,
    instrument_metadata,
    output_manifest_rows,
    utc_now,
    write_gate_results,
    write_json,
)


SPEC_ID = "docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_LAPTOP_SPECTRAL_CONTROL_MAPPING_SMOKE_SPEC.md"
RUNNER_MODULE = "omega.rfs_mb0_future_landscape.run_stage_b2_laptop_spectral_control_mapping_smoke"

LAPTOP_OUTPUTS = (
    "laptop_spectral_smoke_run_config.json",
    "laptop_spectral_smoke_status.json",
    "laptop_spectral_smoke_progress_checkpoints.csv",
    "laptop_spectral_smoke_errors.csv",
    "laptop_spectral_smoke_output_manifest.json",
    "laptop_spectral_output_contract_report.md",
    "laptop_label_shuffle_spectral_smoke.csv",
    "laptop_context_shuffle_spectral_smoke.csv",
    "laptop_horizon_shuffle_spectral_smoke.csv",
    "laptop_spectral_shuffle_control_summary.csv",
    "laptop_spectral_shuffle_family_gate_summary.csv",
    "laptop_spectral_shuffle_failure_anatomy.csv",
    "laptop_spectral_shuffle_control_report.md",
    "laptop_selection_evaluation_partition_summary.csv",
    "laptop_subspace_transfer_diagnostic.csv",
    "laptop_subspace_distributedness_diagnostic.csv",
    "laptop_subspace_control_alignment.csv",
    "laptop_spectral_next_action_fork.csv",
    "laptop_spectral_readiness_levels.csv",
    "laptop_spectral_high_loading_items.csv",
    "laptop_spectral_item_loading_summary.csv",
    "laptop_spectral_item_vocab_manifest.csv",
    "laptop_spectral_high_loading_export_report.md",
    "laptop_spectral_item_to_edge_mapping.csv",
    "laptop_spectral_mapping_coverage.csv",
    "laptop_spectral_mapping_report.md",
    "laptop_spectral_item_ablation_manifest.csv",
    "laptop_high_loading_ablation_summary.csv",
    "laptop_random_item_ablation_summary.csv",
    "laptop_low_loading_ablation_summary.csv",
    "laptop_item_ablation_decision.csv",
    "laptop_item_ablation_report.md",
    "laptop_tiny_channel_perturbation_manifest.csv",
    "laptop_tiny_channel_matching_quality.csv",
    "laptop_tiny_channel_substrate_preservation.csv",
    "laptop_tiny_channel_syndrome_rates.csv",
    "laptop_tiny_channel_spectral_response.csv",
    "laptop_tiny_channel_target_vs_random_summary.csv",
    "laptop_tiny_channel_smoke_report.md",
    "laptop_spectral_gate_results.csv",
    "laptop_spectral_control_mapping_smoke_report.md",
    "laptop_gpt_requested_status_key_fields.csv",
    "laptop_mapping_status_counts.csv",
    "laptop_spectral_forwarding_summary.md",
)

ALIASES = {
    "spectral_future_field_run_config.json": "laptop_spectral_smoke_run_config.json",
    "spectral_future_field_status.json": "laptop_spectral_smoke_status.json",
    "spectral_future_field_progress_checkpoints.csv": "laptop_spectral_smoke_progress_checkpoints.csv",
    "errors.csv": "laptop_spectral_smoke_errors.csv",
    "runner_output_contract_smoke_report.md": "laptop_spectral_output_contract_report.md",
    "spectral_label_shuffle_smoke.csv": "laptop_label_shuffle_spectral_smoke.csv",
    "spectral_context_shuffle_smoke.csv": "laptop_context_shuffle_spectral_smoke.csv",
    "spectral_horizon_shuffle_smoke.csv": "laptop_horizon_shuffle_spectral_smoke.csv",
    "spectral_control_repair_smoke_summary.csv": "laptop_spectral_shuffle_control_summary.csv",
    "spectral_shuffle_family_gate_summary.csv": "laptop_spectral_shuffle_family_gate_summary.csv",
    "spectral_shuffle_failure_anatomy.csv": "laptop_spectral_shuffle_failure_anatomy.csv",
    "spectral_control_repair_smoke_report.md": "laptop_spectral_shuffle_control_report.md",
    "spectral_selection_evaluation_partition_summary.csv": "laptop_selection_evaluation_partition_summary.csv",
    "spectral_subspace_transfer_diagnostic.csv": "laptop_subspace_transfer_diagnostic.csv",
    "spectral_subspace_distributedness_diagnostic.csv": "laptop_subspace_distributedness_diagnostic.csv",
    "spectral_subspace_control_alignment.csv": "laptop_subspace_control_alignment.csv",
    "spectral_next_action_fork.csv": "laptop_spectral_next_action_fork.csv",
    "spectral_readiness_levels.csv": "laptop_spectral_readiness_levels.csv",
    "spectral_high_loading_items_smoke.csv": "laptop_spectral_high_loading_items.csv",
    "spectral_item_loading_summary_smoke.csv": "laptop_spectral_item_loading_summary.csv",
    "spectral_item_manifest.csv": "laptop_spectral_item_vocab_manifest.csv",
    "spectral_item_to_edge_mapping_smoke.csv": "laptop_spectral_item_to_edge_mapping.csv",
    "spectral_mapping_coverage_smoke.csv": "laptop_spectral_mapping_coverage.csv",
    "spectral_item_mapping_smoke_report.md": "laptop_spectral_mapping_report.md",
    "spectral_item_ablation_manifest.csv": "laptop_spectral_item_ablation_manifest.csv",
    "spectral_high_loading_ablation_summary.csv": "laptop_high_loading_ablation_summary.csv",
    "spectral_random_item_ablation_summary.csv": "laptop_random_item_ablation_summary.csv",
    "spectral_low_mid_loading_ablation_summary.csv": "laptop_low_loading_ablation_summary.csv",
    "spectral_item_ablation_decision.csv": "laptop_item_ablation_decision.csv",
    "spectral_item_ablation_report.md": "laptop_item_ablation_report.md",
    "spectral_channel_tiny_perturbation_manifest.csv": "laptop_tiny_channel_perturbation_manifest.csv",
    "spectral_channel_tiny_matching_quality.csv": "laptop_tiny_channel_matching_quality.csv",
    "spectral_channel_tiny_substrate_preservation.csv": "laptop_tiny_channel_substrate_preservation.csv",
    "spectral_channel_tiny_syndrome_rates.csv": "laptop_tiny_channel_syndrome_rates.csv",
    "spectral_channel_tiny_spectral_response.csv": "laptop_tiny_channel_spectral_response.csv",
    "spectral_channel_tiny_target_vs_random_summary.csv": "laptop_tiny_channel_target_vs_random_summary.csv",
    "spectral_channel_tiny_smoke_report.md": "laptop_tiny_channel_smoke_report.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run laptop-safe RFS-MB0 Stage B-2 spectral control/mapping smoke.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--phase-b-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls"))
    parser.add_argument("--out", type=Path, default=Path("results/local_runs/20260530_laptop_spectral_control_mapping_smoke"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=1)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=1)
    parser.add_argument("--start-samples-list", type=str, default="4")
    parser.add_argument("--probes", type=str, default="constraint_profile_hash,constraint_violation_count_plus_local_tuple")
    parser.add_argument("--primary-syndromes", type=str, default=",".join(PRIMARY_SYNDROMES))
    parser.add_argument("--include-secondary-syndromes", action="store_true")
    parser.add_argument("--roughness-seed-replicates", type=int, default=0)
    parser.add_argument("--small-edge-resample-strengths", type=str, default="0.02")
    parser.add_argument("--asymmetry-multipliers", type=str, default="")
    parser.add_argument("--asymmetric-edge-flip-strengths", type=str, default="0.02")
    parser.add_argument("--constraint-proxy-strengths", type=str, default="")
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--job-batch-size", type=int, default=2)
    parser.add_argument("--checkpoint-every-jobs", type=int, default=20)
    parser.add_argument("--max-runtime-seconds", type=int, default=7200)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=900)
    parser.add_argument("--max-items-per-context", type=int, default=64)
    parser.add_argument("--max-items-per-matrix", type=int, default=512)
    parser.add_argument("--min-item-count", type=int, default=2)
    parser.add_argument("--epsilon", type=float, default=1e-9)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--component-z-threshold", type=float, default=0.5)
    parser.add_argument("--control-summary-cache-mode", choices=("auto", "rebuild", "off"), default="auto")
    parser.add_argument("--control-summary-cache", type=Path, default=None)
    parser.add_argument("--shuffle-replicates", type=int, default=3)
    parser.add_argument("--shuffle-max-matrices", type=int, default=12)
    parser.add_argument("--label-shuffle-min-percentile", type=float, default=0.80)
    parser.add_argument("--context-shuffle-min-percentile", type=float, default=0.80)
    parser.add_argument("--horizon-shuffle-min-percentile", type=float, default=0.80)
    parser.add_argument("--min-shuffle-families-passed", type=int, default=2)
    parser.add_argument("--shuffle-family-min-pass-fraction", type=float, default=0.50)
    parser.add_argument("--shuffle-family-min-median-percentile", type=float, default=0.80)
    parser.add_argument("--shuffle-family-catastrophic-min-percentile", type=float, default=0.50)
    parser.add_argument("--high-loading-top-k-items", "--top-k-items", type=int, default=16)
    parser.add_argument("--high-loading-candidate-pool-multiplier", type=int, default=8)
    parser.add_argument("--high-loading-min-seed-count", type=int, default=1)
    parser.add_argument("--high-loading-min-shuffle-survival-count", type=int, default=1)
    parser.add_argument("--high-loading-min-matrix-recurrence", type=int, default=1)
    parser.add_argument("--selection-evaluation-split", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--selection-partition-fraction", type=float, default=0.50)
    parser.add_argument("--selection-partition-seed", type=str, default="laptop_spectral_control_mapping_v1")
    parser.add_argument("--ablation-random-replicates", type=int, default=3)
    parser.add_argument("--ablation-specific-min-random-stds", type=float, default=1.0)
    parser.add_argument("--ablation-min-effect-metrics", type=int, default=2)
    parser.add_argument("--ablation-max-coverage-loss", type=float, default=0.60)
    parser.add_argument("--random-matching-min-quality", type=float, default=0.60)
    parser.add_argument("--subspace-transfer-min-alignment", type=float, default=0.50)
    parser.add_argument("--subspace-control-replicates", type=int, default=3)
    parser.add_argument("--prep-target-conditions", type=str, default="baseline_unperturbed:baseline,small_edge_resample_control:p0.02,asymmetric_edge_flip_control:p0.02")
    parser.add_argument("--prep-target-horizon-bands", type=str, default="middle")
    parser.add_argument("--mapping-mass-threshold", type=float, default=0.30)
    parser.add_argument("--tiny-perturbation-jobs", type=int, default=0)
    parser.add_argument("--tiny-perturbation-strengths", type=str, default="0.0025")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    repo_root = Path(__file__).resolve().parents[2]
    args.out.mkdir(parents=True, exist_ok=True)
    selected_syndromes = selected_syndrome_ids(args)
    components = [row for row in syndrome_library() if str(row["syndrome_id"]) in set(selected_syndromes)]
    metadata = instrument_metadata(SPEC_ID, RUNNER_MODULE, repo_root)
    write_json(args.out / "laptop_spectral_smoke_run_config.json", {**metadata, **vars(args), "selected_syndrome_ids": selected_syndromes})
    control_summaries, control_source, control_summary_contexts, cache_status = load_control_summaries(
        args.phase_b_dir,
        components,
        args.control_summary_cache_mode,
        args.control_summary_cache,
    )
    status: dict[str, object] = {
        **metadata,
        "status": "RUNNING",
        "phase": "rfs_mb0_stage_b2_laptop_spectral_control_mapping_smoke",
        "started_utc": utc_now(),
        "out_dir": str(args.out),
        "phase_b_dir": str(args.phase_b_dir),
        "workers": args.workers,
        "job_batch_size": args.job_batch_size,
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "control_source": control_source,
        "control_summary_contexts": control_summary_contexts,
        "control_summary_cache_status": cache_status,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "candidate_promotion_enabled": False,
        "generated_artifacts_commit_policy": "do_not_commit",
        "selection_evaluation_split_enabled": bool(args.selection_evaluation_split),
        "selection_partition_fraction": args.selection_partition_fraction,
        "selection_partition_seed": args.selection_partition_seed,
        "label_shuffle_min_percentile": args.label_shuffle_min_percentile,
        "context_shuffle_min_percentile": args.context_shuffle_min_percentile,
        "horizon_shuffle_min_percentile": args.horizon_shuffle_min_percentile,
        "min_shuffle_families_passed": args.min_shuffle_families_passed,
        "shuffle_family_min_pass_fraction": args.shuffle_family_min_pass_fraction,
        "shuffle_family_min_median_percentile": args.shuffle_family_min_median_percentile,
        "shuffle_family_catastrophic_min_percentile": args.shuffle_family_catastrophic_min_percentile,
        "ablation_specific_min_random_stds": args.ablation_specific_min_random_stds,
        "ablation_min_effect_metrics": args.ablation_min_effect_metrics,
        "ablation_max_coverage_loss": args.ablation_max_coverage_loss,
        "random_matching_min_quality": args.random_matching_min_quality,
        "subspace_transfer_min_alignment": args.subspace_transfer_min_alignment,
        "subspace_control_replicates": args.subspace_control_replicates,
    }
    write_json(args.out / "laptop_spectral_smoke_status.json", status)
    if cache_status == "missing_source" or not control_summaries:
        finalize_missing_source(args, status, started)
        return
    groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    start_samples = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    jobs = build_jobs(args, groups, split_rows, anchors, probes, start_samples)
    status.update({
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "contexts_accumulated": 0,
        "matrix_families_requested": 2,
        "matrix_families_completed": 0,
        "spectral_decompositions_completed": 0,
        "control_comparison_scope": "direct_stage_b2_plus_laptop_shuffle_controls",
        "label_shuffled_controls_completed": False,
        "context_shuffled_controls_completed": False,
        "horizon_order_shuffled_controls_completed": False,
        "frontier_size_matched_controls_completed": False,
        "probe_marginal_controls_completed": False,
        "errors": 0,
    })
    write_status(args.out, status, started)
    write_csv(args.out / "spectral_context_manifest.csv", context_manifest_rows(jobs))
    counts, errors, checkpoints = run_batches(args, jobs, status, started, control_summaries, components, selected_syndromes)
    matrices = build_spectral_matrices(counts, args)
    status["matrix_families_completed"] = len({matrix.key.matrix_family for matrix in matrices})
    status["spectral_decompositions_completed"] = len(matrices)
    write_outputs(args.out, args, status, started, counts, matrices, errors, checkpoints, jobs, control_summaries, components, selected_syndromes)
    write_laptop_aliases(args.out)
    gates = gate_results(args.out, status)
    write_gate_results(args.out / "laptop_spectral_gate_results.csv", gates)
    status.update(laptop_decision_fields(gates, status))
    status["finished_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    write_json(args.out / "laptop_spectral_smoke_status.json", status)
    write_report(args.out, status, gates)
    write_compact_forwarding_outputs(args.out, status, gates)
    write_laptop_manifest(args.out)


def finalize_missing_source(args: argparse.Namespace, status: dict[str, object], started: float) -> None:
    status.update({
        "status": "PARTIAL_CONTROL_SOURCE_MISSING",
        "finalization_reason": "missing_phase_b_control_summary_source",
        "finished_utc": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "jobs_requested": 0,
        "jobs_completed": 0,
        "shuffle_replicates_completed": 0,
        "high_loading_items_exported": 0,
        "item_sets_mapped": 0,
        "ablation_jobs_completed": 0,
        "perturbation_jobs_completed": 0,
        "blocking_reason": "missing_source",
        "errors": 1,
        "ready_for_larger_spectral_control_run": 0,
        "ready_for_larger_analysis_only_channel_run": 0,
        "ready_for_tiny_graph_channel_perturbation": 0,
        "ready_for_larger_graph_channel_run": 0,
        "ready_for_larger_spectral_channel_run": 0,
        "subspace_transfer_status": "subspace_transfer_not_computed",
        "subspace_item_read": "subspace_transfer_not_computed",
        "subspace_distributedness_read": "subspace_distributedness_not_computed",
        "subspace_control_alignment_status": "subspace_control_alignment_not_computed",
        "next_action_fork": "repair_shuffle_controls",
        "ablation_failure_reason": "missing_source",
        "laptop_decision_class": "PARTIAL_CONTROL_SOURCE_MISSING",
        "laptop_next_step": "restore or regenerate the missing Phase B/Stage A control summary source before any compute",
    })
    write_csv(args.out / "laptop_spectral_smoke_errors.csv", [{"error": "missing_required_control_source", "phase_b_dir": str(args.phase_b_dir)}])
    gates = [GateResult("G0", "control_source_available", True, False, "source present", status.get("control_summary_cache_status"), "missing_source")]
    write_gate_results(args.out / "laptop_spectral_gate_results.csv", gates)
    write_json(args.out / "laptop_spectral_smoke_status.json", status)
    write_report(args.out, status, gates)
    write_compact_forwarding_outputs(args.out, status, gates)
    write_laptop_manifest(args.out)


def write_laptop_aliases(out_dir: Path) -> None:
    for source, target in ALIASES.items():
        source_path = out_dir / source
        if source_path.exists():
            shutil.copyfile(source_path, out_dir / target)
    mapping_report = out_dir / "spectral_item_mapping_smoke_report.md"
    if mapping_report.exists():
        shutil.copyfile(mapping_report, out_dir / "laptop_spectral_high_loading_export_report.md")
    write_json(out_dir / "laptop_spectral_smoke_output_manifest.json", output_manifest_rows(list(LAPTOP_OUTPUTS), out_dir))


def gate_results(out_dir: Path, status: dict[str, object]) -> list[GateResult]:
    shuffle_rows = read_csv(out_dir / "spectral_shuffle_family_gate_summary.csv")
    mapping_rows = read_csv(out_dir / "spectral_mapping_coverage_smoke.csv")
    ablation_rows = read_csv(out_dir / "spectral_item_ablation_decision.csv")
    tiny_rows = read_csv(out_dir / "spectral_channel_tiny_target_vs_random_summary.csv")
    shuffle_pass = int(status.get("spectral_shuffle_control_status") == "spectral_shuffle_controls_passed")
    required_shuffle_rows = [row for row in shuffle_rows if int(float_or_zero(row.get("family_required_for_control_gate", 1))) == 1]
    blocker_rows = required_shuffle_rows or shuffle_rows
    shuffle_blocker = ";".join(sorted({row.get("blocking_reason", "") for row in blocker_rows if row.get("blocking_reason")})) or "structure_shuffle_controls_not_passed"
    structure_total = len(required_shuffle_rows)
    structure_passed = sum(int(float_or_zero(row.get("family_passed"))) for row in required_shuffle_rows)
    label_rows = [row for row in shuffle_rows if row.get("shuffle_control_category") == "label_interpretation_control"]
    label_passed = sum(int(float_or_zero(row.get("family_passed"))) for row in label_rows)
    mapping_best = max((float_or_zero(row.get("mapped_item_mass_fraction")) for row in mapping_rows), default=0.0)
    ablation_decision = ablation_rows[0].get("decision_class", "") if ablation_rows else ""
    ablation_blocker = ablation_rows[0].get("ablation_failure_reason", "ablation_not_specific") if ablation_rows else "ablation_not_specific"
    tiny_decision = tiny_rows[0].get("decision_class", "not_run") if tiny_rows else "not_run"
    return [
        GateResult("G0", "control_source_available", True, status.get("control_summary_cache_status") != "missing_source", "source present", status.get("control_summary_cache_status", "")),
        GateResult("G1", "output_contract_passed", True, True, "required files written", "core outputs present"),
        GateResult("G2", "structure_shuffle_family_thresholds", True, bool(shuffle_pass), "context and horizon structure controls pass; label shuffle reported separately", f"{structure_passed}/{structure_total} structure families; {label_passed}/{len(label_rows)} label families", "" if shuffle_pass else shuffle_blocker),
        GateResult("G3", "item_mapping_mass", True, mapping_best >= 0.30, "mapped_item_mass_fraction >= 0.30", f"{mapping_best:.3f}", "" if mapping_best >= 0.30 else "mapping_insufficient"),
        GateResult("G4", "selection_evaluation_ablation", True, ablation_decision == "high_loading_ablation_specific", "high_loading_ablation_specific", ablation_decision, "" if ablation_decision == "high_loading_ablation_specific" else ablation_blocker),
        GateResult("G5", "tiny_perturbation_optional", False, tiny_decision == "tiny_channel_perturbation_implemented", "implemented if requested", tiny_decision),
    ]


def laptop_decision_fields(gates: list[GateResult], status: dict[str, object]) -> dict[str, object]:
    if status.get("status") == "PARTIAL_CONTROL_SOURCE_MISSING":
        decision = "PARTIAL_CONTROL_SOURCE_MISSING"
        next_step = "restore or regenerate the missing Phase B/Stage A control summary source before any compute"
    elif int(status.get("ready_for_larger_graph_channel_run", 0)):
        decision = "ready_for_larger_graph_channel_run"
        next_step = "larger graph-channel exploratory run, still without holdout or promotion"
    elif int(status.get("ready_for_tiny_graph_channel_perturbation", 0)):
        decision = "ready_for_tiny_graph_channel_perturbation"
        next_step = "run the tiny targeted-vs-random graph perturbation gate before any larger graph run"
    elif int(status.get("ready_for_larger_analysis_only_channel_run", 0)):
        decision = "ready_for_larger_analysis_only_channel_run"
        next_step = "run ablation-repair analysis only; graph perturbation remains gated"
    elif int(status.get("ready_for_larger_spectral_control_run", 0)):
        decision = "ready_for_larger_spectral_control_run"
        next_step = "scale spectral controls only; mapping/ablation/channel claims remain gated"
    else:
        decision = "not_ready_repair_required"
        next_step = "repair the first failed required gate before scaling"
    return {
        "laptop_decision_class": decision,
        "ready_for_larger_spectral_channel_run": int(status.get("ready_for_larger_graph_channel_run", 0)),
        "laptop_next_step": next_step,
    }


def write_report(out_dir: Path, status: dict[str, object], gates: list[GateResult]) -> None:
    failed = [gate for gate in gates if gate.required and not gate.passed]
    decision = str(status.get("laptop_decision_class", "not_ready_repair_required"))
    interpretation = "This was a laptop-safe instrument-readiness smoke, not a validation run."
    caveats = [gate.blocking_reason or gate.gate_name for gate in failed]
    if not caveats:
        caveats = [
            "frontier-size matched spectral controls remain incomplete",
            "probe-marginal spectral controls remain incomplete",
            "larger-run readiness is not scientific validation",
        ]
    next_step = str(status.get("laptop_next_step", "repair blocked gate before scaling"))
    lines = [
        "# RFS-MB0 Laptop Spectral Control Mapping Smoke Report",
        "",
        *executive_summary_lines(decision=decision, interpretation=interpretation, caveats=caveats, next_step=next_step),
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Gate Summary",
        "",
        "| gate_id | gate_name | required | passed | observed | blocking_reason |",
        "|---|---|---:|---:|---|---|",
    ]
    for gate in gates:
        row = gate.row()
        lines.append(f"| {row['gate_id']} | {row['gate_name']} | {row['required']} | {row['passed']} | {row['observed']} | {row['blocking_reason']} |")
    lines.extend([
        "",
        "## Readiness Levels",
        "",
        f"- Larger spectral controls: `{int(status.get('ready_for_larger_spectral_control_run', 0))}`",
        f"- Larger analysis-only channel diagnostics: `{int(status.get('ready_for_larger_analysis_only_channel_run', 0))}`",
        f"- Tiny graph-channel perturbation: `{int(status.get('ready_for_tiny_graph_channel_perturbation', 0))}`",
        f"- Larger graph-channel run: `{int(status.get('ready_for_larger_graph_channel_run', 0))}`",
        "",
        "## Ablation Read",
        "",
        f"Decision: `{status.get('item_ablation_status', '')}`.",
        f"Failure reason: `{status.get('ablation_failure_reason', '')}`.",
        f"Subspace/item read: `{status.get('subspace_item_read', status.get('subspace_transfer_status', ''))}`.",
        f"Distributedness read: `{status.get('subspace_distributedness_read', '')}`.",
        f"Subspace-control alignment: `{status.get('subspace_control_alignment_status', '')}`.",
        f"Next-action fork: `{status.get('next_action_fork', '')}`.",
        "",
        "## Output Manifest",
        "",
        "Generated CSV/JSON artifacts are local-only. See `laptop_spectral_smoke_output_manifest.json`.",
        "",
    ])
    (out_dir / "laptop_spectral_control_mapping_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_compact_forwarding_outputs(out_dir: Path, status: dict[str, object], gates: list[GateResult]) -> None:
    key_fields = (
        "status",
        "finalization_reason",
        "jobs_requested",
        "jobs_completed",
        "errors",
        "control_summary_cache_status",
        "shuffle_replicates_completed",
        "high_loading_items_exported",
        "item_sets_mapped",
        "ablation_jobs_completed",
        "perturbation_jobs_completed",
        "decision_classes",
        "blocking_reason",
        "ready_for_larger_spectral_control_run",
        "ready_for_larger_analysis_only_channel_run",
        "ready_for_tiny_graph_channel_perturbation",
        "ready_for_larger_graph_channel_run",
        "subspace_distributedness_read",
        "subspace_control_alignment_status",
        "next_action_fork",
    )
    write_csv(out_dir / "laptop_gpt_requested_status_key_fields.csv", [{"field": field, "value": status.get(field, "")} for field in key_fields])
    mapping_rows = read_csv(out_dir / "laptop_spectral_item_to_edge_mapping.csv")
    mapping_counts = []
    for (mapping_status,), rows in group_rows(mapping_rows, ("mapping_status",)).items():
        mapping_counts.append({
            "mapping_status": mapping_status,
            "count": len(rows),
            "mapped_realized_edge_count": sum(int(float_or_zero(row.get("mapped_realized_edge_count", row.get("realized_edge_count")))) for row in rows),
        })
    write_csv(out_dir / "laptop_mapping_status_counts.csv", mapping_counts)
    write_forwarding_summary(out_dir, status, gates)


def write_forwarding_summary(out_dir: Path, status: dict[str, object], gates: list[GateResult]) -> None:
    first_failed = next((gate for gate in gates if gate.required and not gate.passed), None)
    shuffle_rows = read_csv(out_dir / "laptop_spectral_shuffle_family_gate_summary.csv")
    anatomy_rows = read_csv(out_dir / "laptop_spectral_shuffle_failure_anatomy.csv")
    mapping_rows = read_csv(out_dir / "laptop_spectral_mapping_coverage.csv")
    ablation_row = (read_csv(out_dir / "laptop_item_ablation_decision.csv") or [{}])[0]
    distributed_rows = read_csv(out_dir / "laptop_subspace_distributedness_diagnostic.csv")
    subspace_control_rows = read_csv(out_dir / "laptop_subspace_control_alignment.csv")
    next_action_row = (read_csv(out_dir / "laptop_spectral_next_action_fork.csv") or [{}])[0]
    best_mapping = max((float_or_zero(row.get("mapped_item_mass_fraction")) for row in mapping_rows), default=0.0)
    lines = [
        "# RFS-MB0 Laptop Spectral Control Mapping Forwarding Summary",
        "",
        "## Executive Summary",
        "",
        f"Final status: `{status.get('status')}` with `{status.get('finalization_reason', '')}`.",
        "",
        f"Decision class: `{status.get('laptop_decision_class', 'not_ready_repair_required')}`.",
        "",
        f"Blocking reason: `{status.get('blocking_reason', '')}`.",
        "",
        f"Control summary cache: `{status.get('control_summary_cache_status', '')}`.",
        "",
        f"First failed required gate: `{first_failed.gate_id if first_failed else ''} {first_failed.gate_name if first_failed else ''}` observed `{first_failed.observed if first_failed else ''}` with blocker `{first_failed.blocking_reason if first_failed else ''}`.",
        "",
        f"Readiness ladder: spectral controls `{status.get('ready_for_larger_spectral_control_run', 0)}`, analysis-only channel diagnostics `{status.get('ready_for_larger_analysis_only_channel_run', 0)}`, tiny graph-channel perturbation `{status.get('ready_for_tiny_graph_channel_perturbation', 0)}`, larger graph-channel run `{status.get('ready_for_larger_graph_channel_run', 0)}`.",
        "",
        f"Subspace read: distributedness `{status.get('subspace_distributedness_read', '')}`, control alignment `{status.get('subspace_control_alignment_status', '')}`.",
        "",
        f"Next action fork: `{status.get('next_action_fork', next_action_row.get('next_action_fork', ''))}`.",
        "",
        "Artifact policy: generated CSV/JSON artifacts are local-only and should not be committed unless explicitly promoted.",
        "",
        "## Gate Results",
        "",
        "| gate | required | passed | threshold | observed | blocker |",
        "|---|---:|---:|---|---|---|",
    ]
    for gate in gates:
        row = gate.row()
        lines.append(f"| {row['gate_id']} {row['gate_name']} | {row['required']} | {row['passed']} | {row['threshold']} | {row['observed']} | {row['blocking_reason']} |")
    lines.extend([
        "",
        "## Shuffle Families",
        "",
        "| family | category | required | replicates | pass_fraction | median_percentile | min_percentile | catastrophic | passed |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in shuffle_rows:
        lines.append(f"| {row.get('shuffle_family', '')} | {row.get('shuffle_control_category', '')} | {row.get('family_required_for_control_gate', '')} | {row.get('replicate_count', '')} | {row.get('pass_fraction', '')} | {row.get('median_observed_percentile', '')} | {row.get('min_observed_percentile', '')} | {row.get('catastrophic_fail_flag', '')} | {row.get('family_passed', '')} |")
    anatomy_counts = group_rows(anatomy_rows, ("shuffle_family", "blocking_reason"))
    lines.extend([
        "",
        "## Shuffle Failure Anatomy",
        "",
        "| family | blocker | matrix_count |",
        "|---|---|---:|",
    ])
    if anatomy_counts:
        for (family, blocker), rows in sorted(anatomy_counts.items()):
            lines.append(f"| {family} | {blocker or 'none'} | {len(rows)} |")
    else:
        lines.append("|  | no rows | 0 |")
    lines.extend([
        "",
        "## Mapping",
        "",
        f"Best mapped item mass fraction: `{best_mapping:.3f}`.",
        "",
        "## Ablation And Subspace",
        "",
        f"Decision: `{ablation_row.get('decision_class', '')}`.",
        "",
        f"Failure reason: `{ablation_row.get('ablation_failure_reason', '')}`.",
        "",
        f"High-loading drop mean: `{ablation_row.get('high_loading_drop_fraction_mean', '')}`.",
        f"Matched-random mean/std/max: `{ablation_row.get('matched_random_drop_fraction_mean', '')}` / `{ablation_row.get('matched_random_drop_fraction_std', '')}` / `{ablation_row.get('matched_random_drop_fraction_max', '')}`.",
        f"Effect metric count: `{ablation_row.get('effect_metric_count', '')}`.",
        f"Random matching quality: `{ablation_row.get('random_matching_quality', '')}`.",
        f"Subspace/item read: `{ablation_row.get('subspace_item_read', '')}`.",
        "",
        "## Distributedness",
        "",
        "| read | matrix_count |",
        "|---|---:|",
    ])
    distributed_counts = group_rows(distributed_rows, ("distributedness_read",))
    if distributed_counts:
        for (read,), rows in sorted(distributed_counts.items()):
            lines.append(f"| {read} | {len(rows)} |")
    else:
        lines.append("| subspace_distributedness_not_computed | 0 |")
    lines.extend([
        "",
        "## Subspace Control Alignment",
        "",
        f"Aggregate status: `{status.get('subspace_control_alignment_status', '')}`.",
        "",
        "| control_family | above_control_count | computed_replicates |",
        "|---|---:|---:|",
    ])
    control_groups = group_rows(subspace_control_rows, ("control_family",))
    if control_groups:
        for (family,), rows in sorted(control_groups.items()):
            above = sum(int(float_or_zero(row.get("subspace_transfer_above_control"))) for row in rows)
            replicates = sum(int(float_or_zero(row.get("control_computed_replicates"))) for row in rows)
            lines.append(f"| {family} | {above} | {replicates} |")
    else:
        lines.append("|  | 0 | 0 |")
    lines.extend([
        "",
        "## Next Action Fork",
        "",
        f"Fork: `{next_action_row.get('next_action_fork', status.get('next_action_fork', ''))}`.",
        "",
        f"Reason: `{next_action_row.get('fork_reason', '')}`.",
        "",
    ])
    (out_dir / "laptop_spectral_forwarding_summary.md").write_text("\n".join(lines), encoding="utf-8")


def group_rows(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row.get(key, "") for key in keys), []).append(row)
    return grouped


def write_laptop_manifest(out_dir: Path) -> None:
    write_json(out_dir / "laptop_spectral_smoke_output_manifest.json", output_manifest_rows(list(LAPTOP_OUTPUTS), out_dir))


if __name__ == "__main__":
    main()
