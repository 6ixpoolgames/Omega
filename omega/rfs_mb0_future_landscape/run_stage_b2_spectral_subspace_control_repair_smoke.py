from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev

from .run_focused_boundary_recurrence import float_or_zero, read_csv, write_csv
from .spectral_contracts import (
    CLAIM_BOUNDARY,
    LOCAL_ONLY_ARTIFACT_POLICY,
    instrument_metadata,
    output_manifest_rows,
    utc_now,
    write_json,
)


SPEC_ID = "docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_SPECTRAL_SUBSPACE_CONTROL_REPAIR_SMOKE_SPEC.md"
RUNNER_MODULE = "omega.rfs_mb0_future_landscape.run_stage_b2_spectral_subspace_control_repair_smoke"
BASE_RUNNER_MODULE = "omega.rfs_mb0_future_landscape.run_stage_b2_laptop_spectral_control_mapping_smoke"

OUTPUTS = (
    "spectral_subspace_repair_run_config.json",
    "spectral_subspace_repair_status.json",
    "spectral_subspace_repair_progress_checkpoints.csv",
    "spectral_subspace_repair_errors.csv",
    "spectral_subspace_repair_output_manifest.json",
    "spectral_subspace_repair_report.md",
    "spectral_subspace_repair_case_manifest.csv",
    "spectral_subspace_repair_case_status.csv",
    "spectral_shuffle_failure_anatomy_v2.csv",
    "spectral_shuffle_failure_by_probe.csv",
    "spectral_shuffle_failure_by_flow_mode.csv",
    "spectral_shuffle_failure_by_condition.csv",
    "spectral_shuffle_failure_by_horizon.csv",
    "spectral_shuffle_failure_by_matrix_family.csv",
    "spectral_shuffle_failure_by_statistic.csv",
    "spectral_shuffle_failure_by_case.csv",
    "spectral_primary_context_recommendation.csv",
    "spectral_subspace_control_alignment_v2.csv",
    "spectral_subspace_distributedness_v2.csv",
    "spectral_subspace_repair_decision.csv",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run laptop-safe RFS-MB0 Stage B-2 spectral subspace control repair sweeps.")
    parser.add_argument("--out", type=Path, default=Path("results/local_runs/20260530_laptop_spectral_subspace_control_repair_sweeps"))
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--phase-b-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls"))
    parser.add_argument("--wall-clock-seconds", type=int, default=14_400)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=900)
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--job-batch-size", type=int, default=2)
    parser.add_argument("--case-runtime-seconds", type=int, default=2400)
    parser.add_argument("--case-shutdown-cushion-seconds", type=int, default=300)
    parser.add_argument("--case-limit", type=int, default=0)
    parser.add_argument("--shuffle-replicates", type=int, default=5)
    parser.add_argument("--subspace-control-replicates", type=int, default=5)
    parser.add_argument("--ablation-random-replicates", type=int, default=2)
    parser.add_argument("--tiny-perturbation-jobs", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    repo_root = Path(__file__).resolve().parents[2]
    args.out.mkdir(parents=True, exist_ok=True)
    metadata = instrument_metadata(SPEC_ID, RUNNER_MODULE, repo_root)
    cases = sweep_cases(args)
    if args.case_limit > 0:
        cases = cases[: args.case_limit]
    write_json(args.out / "spectral_subspace_repair_run_config.json", {
        **metadata,
        **vars(args),
        "base_runner_module": BASE_RUNNER_MODULE,
        "sweep_case_count": len(cases),
        "sweep_cases": cases,
    })
    status: dict[str, object] = {
        **metadata,
        "status": "RUNNING",
        "phase": "rfs_mb0_stage_b2_spectral_subspace_control_repair_smoke",
        "started_utc": utc_now(),
        "out_dir": str(args.out),
        "base_runner_module": BASE_RUNNER_MODULE,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "candidate_promotion_enabled": False,
        "artifact_policy": LOCAL_ONLY_ARTIFACT_POLICY,
        "wall_clock_seconds": args.wall_clock_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "cases_requested": len(cases),
        "cases_completed": 0,
        "cases_failed": 0,
        "cases_skipped_for_time": 0,
    }
    write_json(args.out / "spectral_subspace_repair_status.json", status)
    errors: list[dict[str, object]] = []
    progress: list[dict[str, object]] = []
    case_status: list[dict[str, object]] = []
    for case in cases:
        remaining = args.wall_clock_seconds - (time.perf_counter() - started)
        if remaining <= args.shutdown_cushion_seconds:
            case_status.append({**case, "case_status": "SKIPPED_TIME_CUSHION", "elapsed_seconds": "", "returncode": ""})
            status["cases_skipped_for_time"] = int(status.get("cases_skipped_for_time", 0)) + 1
            break
        if args.dry_run:
            case_status.append({**case, "case_status": "DRY_RUN", "elapsed_seconds": 0, "returncode": ""})
            progress.append({
                "timestamp_utc": utc_now(),
                "case_id": case["case_id"],
                "case_status": "DRY_RUN",
                "cases_completed": status["cases_completed"],
                "cases_failed": status["cases_failed"],
                "elapsed_seconds": round(time.perf_counter() - started, 3),
            })
            continue
        result = run_case(args, case, started)
        case_status.append(result)
        if result["case_status"] == "COMPLETED":
            status["cases_completed"] = int(status.get("cases_completed", 0)) + 1
        else:
            status["cases_failed"] = int(status.get("cases_failed", 0)) + 1
            errors.append({"case_id": case["case_id"], "error": result.get("stderr_tail", result["case_status"])})
        progress.append({
            "timestamp_utc": utc_now(),
            "case_id": case["case_id"],
            "case_status": result["case_status"],
            "cases_completed": status["cases_completed"],
            "cases_failed": status["cases_failed"],
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        })
        write_csv(args.out / "spectral_subspace_repair_progress_checkpoints.csv", progress)
        write_csv(args.out / "spectral_subspace_repair_case_status.csv", case_status)
        write_json(args.out / "spectral_subspace_repair_status.json", {**status, "elapsed_seconds": round(time.perf_counter() - started, 3)})
    write_csv(args.out / "spectral_subspace_repair_case_manifest.csv", cases)
    write_csv(args.out / "spectral_subspace_repair_progress_checkpoints.csv", progress)
    write_csv(args.out / "spectral_subspace_repair_case_status.csv", case_status)
    aggregate_outputs(args.out, cases, case_status)
    decision = decision_rows(args.out, case_status)
    write_csv(args.out / "spectral_subspace_repair_decision.csv", decision)
    status.update(final_status(case_status, errors, started))
    if decision:
        status.update(decision[0])
    write_csv(args.out / "spectral_subspace_repair_errors.csv", errors)
    write_report(args.out, status, cases, case_status)
    write_manifest(args.out)
    write_json(args.out / "spectral_subspace_repair_status.json", status)


def sweep_cases(args: argparse.Namespace) -> list[dict[str, object]]:
    base = {
        "design_groups": 1,
        "fresh_seeds_per_group": 1,
        "start_samples_list": "4",
        "shuffle_replicates": args.shuffle_replicates,
        "subspace_control_replicates": args.subspace_control_replicates,
        "ablation_random_replicates": args.ablation_random_replicates,
        "shuffle_max_matrices": 6,
        "high_loading_top_k_items": 8,
        "high_loading_candidate_pool_multiplier": 6,
        "prep_target_conditions": "baseline_unperturbed:baseline,small_edge_resample_control:p0.02,asymmetric_edge_flip_control:p0.02",
        "prep_target_horizon_bands": "middle",
        "selection_partition_fraction": 0.50,
    }
    specs = [
        ("primary_middle", {}),
        ("horizon_short", {"prep_target_horizon_bands": "short"}),
        ("horizon_downstream", {"prep_target_horizon_bands": "downstream"}),
        ("baseline_only_middle", {"prep_target_conditions": "baseline_unperturbed:baseline"}),
        ("resample_only_middle", {"prep_target_conditions": "small_edge_resample_control:p0.02"}),
        ("asym_only_middle", {"prep_target_conditions": "asymmetric_edge_flip_control:p0.02"}),
        ("lower_item_floor_middle", {"high_loading_top_k_items": 12, "shuffle_max_matrices": 8}),
        ("partition_40_middle", {"selection_partition_fraction": 0.40}),
        ("partition_60_middle", {"selection_partition_fraction": 0.60}),
    ]
    cases: list[dict[str, object]] = []
    for index, (case_id, overrides) in enumerate(specs, start=1):
        payload = {**base, **overrides}
        payload.update({
            "case_index": index,
            "case_id": case_id,
            "case_out_dir": str(args.out / "cases" / f"{index:02d}_{case_id}"),
        })
        cases.append(payload)
    return cases


def run_case(args: argparse.Namespace, case: dict[str, object], started: float) -> dict[str, object]:
    out_dir = Path(str(case["case_out_dir"]))
    command = [
        sys.executable,
        "-m",
        BASE_RUNNER_MODULE,
        "--out", str(out_dir),
        "--selection", str(args.selection),
        "--corrected", str(args.corrected),
        "--source-run", str(args.source_run),
        "--phase-b-dir", str(args.phase_b_dir),
        "--design-groups", str(case["design_groups"]),
        "--fresh-seeds-per-group", str(case["fresh_seeds_per_group"]),
        "--start-samples-list", str(case["start_samples_list"]),
        "--shuffle-replicates", str(case["shuffle_replicates"]),
        "--shuffle-max-matrices", str(case["shuffle_max_matrices"]),
        "--high-loading-top-k-items", str(case["high_loading_top_k_items"]),
        "--high-loading-candidate-pool-multiplier", str(case["high_loading_candidate_pool_multiplier"]),
        "--ablation-random-replicates", str(case["ablation_random_replicates"]),
        "--subspace-control-replicates", str(case["subspace_control_replicates"]),
        "--tiny-perturbation-jobs", str(args.tiny_perturbation_jobs),
        "--prep-target-conditions", str(case["prep_target_conditions"]),
        "--prep-target-horizon-bands", str(case["prep_target_horizon_bands"]),
        "--selection-partition-fraction", str(case["selection_partition_fraction"]),
        "--workers", str(args.workers),
        "--job-batch-size", str(args.job_batch_size),
        "--max-runtime-seconds", str(args.case_runtime_seconds),
        "--shutdown-cushion-seconds", str(args.case_shutdown_cushion_seconds),
    ]
    env = os.environ.copy()
    env.update({
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "NUMBA_NUM_THREADS": "1",
    })
    case_started = time.perf_counter()
    timeout = max(60, min(args.case_runtime_seconds + 180, int(args.wall_clock_seconds - (time.perf_counter() - started))))
    try:
        completed = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parents[2],
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        status_row = read_case_status(out_dir)
        case_status = "COMPLETED" if completed.returncode == 0 else "FAILED_WITH_ERRORS"
        return {
            **case,
            "case_status": case_status,
            "returncode": completed.returncode,
            "elapsed_seconds": round(time.perf_counter() - case_started, 3),
            "stdout_tail": completed.stdout[-1000:],
            "stderr_tail": completed.stderr[-1000:],
            **status_row,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            **case,
            "case_status": "PARTIAL_TIME_LIMIT_REACHED",
            "returncode": "timeout",
            "elapsed_seconds": round(time.perf_counter() - case_started, 3),
            "stdout_tail": (exc.stdout or "")[-1000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-1000:] if isinstance(exc.stderr, str) else "",
        }


def read_case_status(out_dir: Path) -> dict[str, object]:
    path = out_dir / "laptop_spectral_smoke_status.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    fields = (
        "status",
        "finalization_reason",
        "jobs_completed",
        "errors",
        "spectral_shuffle_control_status",
        "blocking_reason",
        "subspace_distributedness_read",
        "subspace_control_alignment_status",
        "next_action_fork",
        "workers",
        "job_batch_size",
    )
    return {f"case_{field}": payload.get(field, "") for field in fields}


def aggregate_outputs(out_dir: Path, cases: list[dict[str, object]], case_status: list[dict[str, object]]) -> None:
    completed_cases = {row.get("case_id") for row in case_status if row.get("case_status") == "COMPLETED"}
    anatomy: list[dict[str, object]] = []
    shuffle_rows: list[dict[str, object]] = []
    subspace: list[dict[str, object]] = []
    distributed: list[dict[str, object]] = []
    for case in cases:
        case_id = str(case["case_id"])
        if case_id not in completed_cases:
            continue
        case_dir = Path(str(case["case_out_dir"]))
        anatomy.extend(enrich_case_rows(case, read_csv(case_dir / "laptop_spectral_shuffle_failure_anatomy.csv")))
        for name in (
            "laptop_label_shuffle_spectral_smoke.csv",
            "laptop_context_shuffle_spectral_smoke.csv",
            "laptop_horizon_shuffle_spectral_smoke.csv",
        ):
            shuffle_rows.extend(enrich_case_rows(case, read_csv(case_dir / name)))
        subspace.extend(enrich_case_rows(case, read_csv(case_dir / "laptop_subspace_control_alignment.csv")))
        distributed.extend(enrich_case_rows(case, read_csv(case_dir / "laptop_subspace_distributedness_diagnostic.csv")))
    anatomy_v2 = anatomy_v2_rows(shuffle_rows, anatomy)
    subspace_v2 = subspace_control_v2_rows(subspace)
    distributed_v2 = distributedness_v2_rows(distributed, subspace_v2)
    write_csv(out_dir / "spectral_shuffle_failure_anatomy_v2.csv", anatomy_v2)
    write_csv(out_dir / "spectral_subspace_control_alignment_v2.csv", subspace_v2)
    write_csv(out_dir / "spectral_subspace_distributedness_v2.csv", distributed_v2)
    write_csv(out_dir / "spectral_shuffle_failure_by_probe.csv", aggregate_anatomy(anatomy_v2, ("probe_key", "shuffle_family")))
    write_csv(out_dir / "spectral_shuffle_failure_by_flow_mode.csv", aggregate_anatomy(anatomy_v2, ("flow_mode", "shuffle_family")))
    write_csv(out_dir / "spectral_shuffle_failure_by_condition.csv", aggregate_anatomy(anatomy_v2, ("condition_id", "shuffle_family")))
    write_csv(out_dir / "spectral_shuffle_failure_by_horizon.csv", aggregate_anatomy(anatomy_v2, ("horizon_band", "shuffle_family")))
    write_csv(out_dir / "spectral_shuffle_failure_by_matrix_family.csv", aggregate_anatomy(anatomy_v2, ("matrix_family", "shuffle_family")))
    write_csv(out_dir / "spectral_shuffle_failure_by_statistic.csv", aggregate_anatomy(anatomy_v2, ("observed_statistic_name", "shuffle_family")))
    write_csv(out_dir / "spectral_shuffle_failure_by_case.csv", aggregate_anatomy(anatomy_v2, ("case_id", "shuffle_family")))
    write_csv(out_dir / "spectral_primary_context_recommendation.csv", primary_context_rows(anatomy_v2, subspace_v2))


def enrich_case_rows(case: dict[str, object], rows: list[dict[str, str]]) -> list[dict[str, object]]:
    return [
        {
            "case_id": case["case_id"],
            "case_index": case["case_index"],
            "sweep_horizon_bands": case["prep_target_horizon_bands"],
            "sweep_conditions": case["prep_target_conditions"],
            "sweep_partition_fraction": case["selection_partition_fraction"],
            "sweep_shuffle_replicates": case["shuffle_replicates"],
            "sweep_subspace_control_replicates": case["subspace_control_replicates"],
            **row,
        }
        for row in rows
    ]


def anatomy_v2_rows(shuffle_rows: list[dict[str, object]], anatomy_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    meta_by_case_matrix_family = {
        (row.get("case_id"), row.get("matrix_id"), row.get("shuffle_family")): row
        for row in anatomy_rows
    }
    out: list[dict[str, object]] = []
    statistics = (
        ("positive_spectral_mass", "observed_positive_spectral_mass", "shuffle_positive_spectral_mass"),
        ("effective_rank", "observed_effective_rank", "shuffle_effective_rank"),
        ("participation_ratio", "observed_top1_participation", "shuffle_top1_participation"),
        ("top_k_subspace_alignment_to_baseline", "observed_topk_alignment", "shuffle_topk_alignment"),
    )
    for key, items in group_by(shuffle_rows, ("case_id", "matrix_id", "shuffle_kind")).items():
        case_id, matrix_id, family = key
        first = items[0] if items else {}
        meta = meta_by_case_matrix_family.get((case_id, matrix_id, family), {})
        threshold = shuffle_threshold(family)
        catastrophic_floor = 0.50
        for statistic_name, observed_field, shuffle_field in statistics:
            observed_values = [row.get(observed_field, "") for row in items if row.get(observed_field, "") != ""]
            shuffle_values = [float_or_zero(row.get(shuffle_field)) for row in items if row.get(shuffle_field, "") != "" and str(row.get("shuffle_status", "computed")) == "computed"]
            if not observed_values or not shuffle_values:
                percentile = 0.0
                observed = ""
                margin = -threshold
                passed = 0
                catastrophic = 1
            else:
                observed = float_or_zero(observed_values[0])
                percentile = sum(value <= observed for value in shuffle_values) / len(shuffle_values)
                margin = percentile - threshold
                passed = int(percentile >= threshold)
                catastrophic = int(percentile < catastrophic_floor)
            row = {
                **key_subset_for_output(first),
                "matrix_id": matrix_id,
                "shuffle_family": family,
                "shuffle_control_category": shuffle_category(family),
                "family_required_for_control_gate": int(shuffle_category(family) == "structure_destroying_control"),
                "observed_statistic_name": statistic_name,
                "observed_statistic_value": observed,
                "shuffle_mean": mean(shuffle_values) if shuffle_values else "",
                "shuffle_std": pstdev(shuffle_values) if len(shuffle_values) > 1 else 0.0 if shuffle_values else "",
                "shuffle_min": min(shuffle_values) if shuffle_values else "",
                "shuffle_max": max(shuffle_values) if shuffle_values else "",
                "observed_percentile_vs_shuffle": percentile,
                "expected_direction": "observed_high_tail_separation_from_structure_destroyed_null",
                "separation_margin": margin,
                "matrix_shuffle_passed": passed,
                "catastrophic_fail_flag": catastrophic,
                "item_count": meta.get("item_count", ""),
                "coverage": meta.get("coverage", ""),
                "positive_spectral_mass": meta.get("positive_spectral_mass", ""),
                "effective_rank": meta.get("effective_rank", ""),
                "participation_ratio": first.get("observed_top1_participation", ""),
                "blocking_reason": "" if passed else "primary_context_below_catastrophic_floor" if catastrophic else "percentile_below_threshold",
            }
            row["failure_interpretation"] = failure_interpretation(row, passed, catastrophic, percentile, margin, catastrophic_floor)
            out.append(row)
    return out


def failure_interpretation(
    row: dict[str, object],
    passed: int,
    catastrophic: int,
    percentile: float,
    margin: float,
    catastrophic_floor: float,
) -> str:
    if passed:
        return "passed"
    if float_or_zero(row.get("coverage")) < 0.50 or float_or_zero(row.get("item_count")) < 2:
        return "insufficient_matrix_coverage"
    if int(float_or_zero(row.get("sweep_shuffle_replicates"))) < 3:
        return "underpowered_replicates"
    if catastrophic or percentile < catastrophic_floor:
        return "true_control_equivalence"
    if margin < 0:
        return "statistic_mismatch"
    return "gate_too_coarse"


def shuffle_threshold(family: object) -> float:
    return 0.80


def shuffle_category(family: object) -> str:
    if str(family) == "label_shuffle":
        return "label_interpretation_control"
    return "structure_destroying_control"


def key_subset_for_output(row: dict[str, object]) -> dict[str, object]:
    fields = (
        "case_id",
        "case_index",
        "sweep_horizon_bands",
        "sweep_conditions",
        "sweep_partition_fraction",
        "sweep_shuffle_replicates",
        "sweep_subspace_control_replicates",
        "matrix_family",
        "condition_id",
        "actual_control_name",
        "proxy_level",
        "probe_key",
        "flow_mode",
        "horizon_band",
    )
    return {field: row.get(field, "") for field in fields}


def subspace_control_v2_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        actual = float_or_zero(row.get("actual_selection_evaluation_alignment"))
        control_mean = float_or_zero(row.get("control_alignment_mean"))
        control_max = float_or_zero(row.get("control_alignment_max"))
        control_std = float_or_zero(row.get("control_alignment_std"))
        above_max = actual > control_max if row.get("actual_selection_evaluation_alignment") != "" and row.get("control_alignment_max") != "" else False
        above_std = actual >= control_mean + control_std if row.get("actual_selection_evaluation_alignment") != "" and row.get("control_alignment_mean") != "" else False
        if int(float_or_zero(row.get("control_computed_replicates"))) <= 1:
            read = "subspace_transfer_underpowered"
        elif above_max or above_std:
            read = "subspace_transfer_above_controls"
        else:
            read = "subspace_transfer_control_equivalent"
        out.append({
            **row,
            "alignment_margin_vs_control_mean": actual - control_mean if row.get("control_alignment_mean") != "" else "",
            "alignment_margin_vs_control_max": actual - control_max if row.get("control_alignment_max") != "" else "",
            "subspace_control_read": read,
        })
    return out


def distributedness_v2_rows(rows: list[dict[str, object]], subspace_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    subspace_by_matrix = defaultdict(list)
    for row in subspace_rows:
        subspace_by_matrix[(row.get("case_id"), row.get("matrix_id"))].append(row)
    out: list[dict[str, object]] = []
    for row in rows:
        controls = subspace_by_matrix.get((row.get("case_id"), row.get("matrix_id")), [])
        above = any(item.get("subspace_control_read") == "subspace_transfer_above_controls" for item in controls if item.get("control_category") == "structure_destroying_control")
        equivalent = controls and not above
        original = str(row.get("distributedness_read", ""))
        if equivalent:
            read = "control_equivalent"
        elif original in {"item_local", "cluster_local", "distributed", "diffuse_noise_like"}:
            read = original
        else:
            read = "underpowered"
        out.append({
            **row,
            "subspace_control_read": "subspace_transfer_above_controls" if above else "subspace_transfer_control_equivalent" if equivalent else "subspace_control_alignment_not_computed",
            "item_ablation_specificity_status": "",
            "distributedness_read_v2": read,
        })
    return out


def aggregate_anatomy(rows: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for key, items in group_by(rows, keys).items():
        percentiles = [float_or_zero(row.get("observed_percentile_vs_shuffle")) for row in items]
        margins = [float_or_zero(row.get("separation_margin")) for row in items]
        passed = [int(float_or_zero(row.get("matrix_shuffle_passed"))) for row in items]
        catastrophic = [int(float_or_zero(row.get("catastrophic_fail_flag"))) for row in items]
        out.append({
            **{field: value for field, value in zip(keys, key)},
            "row_count": len(items),
            "matrix_count": len({row.get("matrix_id") for row in items}),
            "pass_fraction": mean(passed) if passed else 0.0,
            "catastrophic_fraction": mean(catastrophic) if catastrophic else 0.0,
            "median_observed_percentile": median(percentiles) if percentiles else 0.0,
            "min_observed_percentile": min(percentiles) if percentiles else 0.0,
            "mean_separation_margin": mean(margins) if margins else 0.0,
            "failure_interpretations": ";".join(sorted({str(row.get("failure_interpretation", "")) for row in items if row.get("failure_interpretation")})),
        })
    return out


def primary_context_rows(anatomy: list[dict[str, object]], subspace: list[dict[str, object]]) -> list[dict[str, object]]:
    subspace_by_context = defaultdict(list)
    context_keys = ("probe_key", "flow_mode", "condition_id", "horizon_band", "matrix_family")
    for row in subspace:
        subspace_by_context[tuple(row.get(key, "") for key in context_keys)].append(row)
    out: list[dict[str, object]] = []
    for key, items in group_by(anatomy, (*context_keys, "shuffle_family")).items():
        context = key[: len(context_keys)]
        passed = [int(float_or_zero(row.get("matrix_shuffle_passed"))) for row in items]
        catastrophic = [int(float_or_zero(row.get("catastrophic_fail_flag"))) for row in items]
        pass_fraction = mean(passed) if passed else 0.0
        catastrophic_fraction = mean(catastrophic) if catastrophic else 0.0
        control_reads = [row.get("subspace_control_read") for row in subspace_by_context.get(context, [])]
        if len(items) < 3:
            recommendation = "needs_more_replicates"
        elif pass_fraction >= 0.50 and "subspace_transfer_above_controls" in control_reads:
            recommendation = "keep_primary"
        elif catastrophic_fraction >= 0.50:
            recommendation = "drop_for_now_due_to_control_equivalence"
        elif pass_fraction == 0:
            recommendation = "make_secondary"
        else:
            recommendation = "needs_more_replicates"
        out.append({
            **{field: value for field, value in zip((*context_keys, "shuffle_family"), key)},
            "row_count": len(items),
            "pass_fraction": pass_fraction,
            "catastrophic_fraction": catastrophic_fraction,
            "subspace_control_reads": ";".join(sorted({str(value) for value in control_reads if value})),
            "primary_context_recommendation": recommendation,
        })
    return out


def decision_rows(out_dir: Path, case_status: list[dict[str, object]]) -> list[dict[str, object]]:
    anatomy = read_csv(out_dir / "spectral_shuffle_failure_anatomy_v2.csv")
    recommendations = read_csv(out_dir / "spectral_primary_context_recommendation.csv")
    subspace = read_csv(out_dir / "spectral_subspace_control_alignment_v2.csv")
    distributed = read_csv(out_dir / "spectral_subspace_distributedness_v2.csv")
    structure = [row for row in anatomy if row.get("shuffle_control_category") == "structure_destroying_control"]
    pass_fraction = mean([int(float_or_zero(row.get("matrix_shuffle_passed"))) for row in structure]) if structure else 0.0
    catastrophic_fraction = mean([int(float_or_zero(row.get("catastrophic_fail_flag"))) for row in structure]) if structure else 0.0
    above_fraction = mean([int(row.get("subspace_control_read") == "subspace_transfer_above_controls") for row in subspace]) if subspace else 0.0
    reads = {row.get("distributedness_read_v2", row.get("distributedness_read", "")) for row in distributed}
    recs = {row.get("primary_context_recommendation", "") for row in recommendations}
    if pass_fraction < 0.50 and {"make_secondary", "drop_for_now_due_to_control_equivalence", "needs_more_replicates"} & recs:
        next_action = "run_primary_context_narrowing_smoke" if "make_secondary" in recs else "repair_shuffle_controls"
        decision = "primary_context_refinement_needed" if "make_secondary" in recs else "not_ready_repair_required"
    elif "keep_primary" in recs and "make_secondary" in recs:
        next_action = "run_primary_context_narrowing_smoke"
        decision = "primary_context_refinement_needed"
    elif pass_fraction >= 0.50 and above_fraction > 0 and ({"distributed", "cluster_local"} & reads):
        next_action = "run_subspace_ablation_smoke"
        decision = "distributed_subspace_candidate"
    elif catastrophic_fraction >= 0.50 and above_fraction == 0:
        next_action = "write_spectral_measurement_limits_note"
        decision = "structure_shuffle_controls_control_equivalent"
    elif pass_fraction < 0.50:
        next_action = "repair_shuffle_controls"
        decision = "not_ready_repair_required"
    else:
        next_action = "repair_shuffle_controls"
        decision = "shuffle_gate_too_coarse"
    return [{
        "decision_class": decision,
        "next_action_fork": next_action,
        "completed_case_count": sum(1 for row in case_status if row.get("case_status") == "COMPLETED"),
        "structure_shuffle_matrix_pass_fraction": pass_fraction,
        "structure_shuffle_catastrophic_fraction": catastrophic_fraction,
        "subspace_above_control_fraction": above_fraction,
        "distributedness_reads": ";".join(sorted(str(item) for item in reads if item)),
        "primary_context_recommendations": ";".join(sorted(str(item) for item in recs if item)),
    }]


def final_status(case_status: list[dict[str, object]], errors: list[dict[str, object]], started: float) -> dict[str, object]:
    completed = sum(1 for row in case_status if row.get("case_status") == "COMPLETED")
    skipped = sum(1 for row in case_status if row.get("case_status") == "SKIPPED_TIME_CUSHION")
    failed = sum(1 for row in case_status if row.get("case_status") not in {"COMPLETED", "SKIPPED_TIME_CUSHION", "DRY_RUN"})
    if failed:
        status = "FAILED_WITH_ERRORS" if completed == 0 else "PARTIAL_TIME_LIMIT_REACHED"
    elif skipped:
        status = "PARTIAL_TIME_LIMIT_REACHED"
    else:
        status = "COMPLETED"
    return {
        "status": status,
        "finalization_reason": "all_cases_completed" if status == "COMPLETED" else "partial_or_failed_cases",
        "finished_utc": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "cases_completed": completed,
        "cases_failed": failed,
        "cases_skipped_for_time": skipped,
        "errors": len(errors),
    }


def write_report(out_dir: Path, status: dict[str, object], cases: list[dict[str, object]], case_status: list[dict[str, object]]) -> None:
    decision = (read_csv(out_dir / "spectral_subspace_repair_decision.csv") or [{}])[0]
    by_horizon = read_csv(out_dir / "spectral_shuffle_failure_by_horizon.csv")
    by_statistic = read_csv(out_dir / "spectral_shuffle_failure_by_statistic.csv")
    by_probe = read_csv(out_dir / "spectral_shuffle_failure_by_probe.csv")
    recommendations = read_csv(out_dir / "spectral_primary_context_recommendation.csv")
    lines = [
        "# Executive Summary",
        "",
        f"Decision: `{decision.get('decision_class', '')}`.",
        "",
        f"Next action: `{decision.get('next_action_fork', '')}`.",
        "",
        f"Completed `{status.get('cases_completed', 0)}` of `{len(cases)}` requested sweep cases with `{status.get('errors', 0)}` errors.",
        "",
        f"Structure shuffle matrix pass fraction: `{decision.get('structure_shuffle_matrix_pass_fraction', '')}`.",
        "",
        f"Subspace above-control fraction: `{decision.get('subspace_above_control_fraction', '')}`.",
        "",
        f"Distributedness reads: `{decision.get('distributedness_reads', '')}`.",
        "",
        f"Artifact policy: {LOCAL_ONLY_ARTIFACT_POLICY}",
        "",
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Runtime And Hardware Profile",
        "",
        f"Workers: `{case_status[0].get('case_workers', '') if case_status else ''}`. Outputs are local-only under `{out_dir}`.",
        "",
        "## Case Status",
        "",
        "| case_id | status | jobs_completed | shuffle_status | blocker | next_action |",
        "|---|---|---:|---|---|---|",
    ]
    for row in case_status:
        lines.append(f"| {row.get('case_id', '')} | {row.get('case_status', '')} | {row.get('case_jobs_completed', '')} | {row.get('case_spectral_shuffle_control_status', '')} | {row.get('case_blocking_reason', '')} | {row.get('case_next_action_fork', '')} |")
    lines.extend(["", "## Shuffle Failure Anatomy", "", "| horizon | family | rows | pass_fraction | catastrophic_fraction | interpretations |", "|---|---|---:|---:|---:|---|"])
    for row in by_horizon:
        lines.append(f"| {row.get('horizon_band', '')} | {row.get('shuffle_family', '')} | {row.get('row_count', '')} | {row.get('pass_fraction', '')} | {row.get('catastrophic_fraction', '')} | {row.get('failure_interpretations', '')} |")
    lines.extend(["", "## Statistic View", "", "| statistic | family | rows | pass_fraction | catastrophic_fraction | median_percentile |", "|---|---|---:|---:|---:|---:|"])
    for row in by_statistic:
        lines.append(f"| {row.get('observed_statistic_name', '')} | {row.get('shuffle_family', '')} | {row.get('row_count', '')} | {row.get('pass_fraction', '')} | {row.get('catastrophic_fraction', '')} | {row.get('median_observed_percentile', '')} |")
    lines.extend(["", "## Primary Context Refinement", "", "| probe | flow | condition | horizon | family | recommendation | pass_fraction |", "|---|---|---|---|---|---|---:|"])
    for row in recommendations[:24]:
        lines.append(f"| {row.get('probe_key', '')} | {row.get('flow_mode', '')} | {row.get('condition_id', '')} | {row.get('horizon_band', '')} | {row.get('shuffle_family', '')} | {row.get('primary_context_recommendation', '')} | {row.get('pass_fraction', '')} |")
    lines.extend(["", "## Probe View", "", "| probe | family | rows | pass_fraction | catastrophic_fraction |", "|---|---|---:|---:|---:|"])
    for row in by_probe:
        lines.append(f"| {row.get('probe_key', '')} | {row.get('shuffle_family', '')} | {row.get('row_count', '')} | {row.get('pass_fraction', '')} | {row.get('catastrophic_fraction', '')} |")
    lines.extend(["", "## Output Manifest", "", "See `spectral_subspace_repair_output_manifest.json`.", ""])
    (out_dir / "spectral_subspace_repair_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(out_dir: Path) -> None:
    rows = output_manifest_rows(list(OUTPUTS), out_dir)
    for row in rows:
        if row.get("file") == "spectral_subspace_repair_output_manifest.json":
            row["exists"] = True
            row["status"] = "present"
    write_json(out_dir / "spectral_subspace_repair_output_manifest.json", rows)


def group_by(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(key, "") for key in keys)].append(row)
    return grouped


if __name__ == "__main__":
    main()
