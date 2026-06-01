"""Run a small coupled Future Field Atlas infrastructure probe."""

from __future__ import annotations

import argparse
import signal
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

from .contracts import instrument_metadata, spec_digest
from .coupled import (
    CoupledProbeResult,
    CoupledProbeTask,
    build_coupled_operator_spec,
    coupled_operator_canonical_json,
    coupled_operator_digest,
    scan_coupled_probe,
)
from .generator import build_generated_conditions, select_start_states
from .util import csv_row_count, safe_token, utc_now, write_csv, write_json


STOP_REQUESTED = False
COUPLED_CLAIM_BOUNDARY = (
    "coupled infrastructure probe only: scans product and coupled future-field topology; "
    "no Omega, agency, identity, valuerhood, value, candidate-promotion, holdout, or causal claim"
)
CONDITION_PAIRING_POLICY = "index_matched"
START_PAIRING_POLICY = "zip_selected_starts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run coupled Future Field Atlas infrastructure probe.")
    parser.add_argument("--out", type=Path, default=Path("results/future_field_atlas/coupled_smoke"))
    parser.add_argument("--groups", type=int, default=1)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=1)
    parser.add_argument("--base-seed", type=int, default=61_001)
    parser.add_argument("--field-b-seed-offset", type=int, default=500_000)
    parser.add_argument("--pair-count", type=int, default=1)
    parser.add_argument("--start-samples", type=int, default=1)
    parser.add_argument("--horizon-max", type=int, default=16)
    parser.add_argument("--horizon-schedule", type=str, default="dense")
    parser.add_argument("--macro-invariant-kind", type=str, default="symbol_histogram_distance")
    parser.add_argument("--macro-invariant-beta-list", type=str, default="0.10")
    parser.add_argument("--rank-boundary-k", type=int, default=3)
    parser.add_argument("--selection-operator-a", type=str, default="rank_prefix:m=3")
    parser.add_argument("--selection-operator-b", type=str, default="rank_subset:m=4:retain=1|2|3:remove=4")
    parser.add_argument(
        "--joint-selection-family",
        choices=("joint_energy_rank_prefix", "product"),
        default="joint_energy_rank_prefix",
    )
    parser.add_argument("--joint-effective-out-degree", type=int, default=4)
    parser.add_argument("--coupling-strength", type=float, default=0.25)
    parser.add_argument("--max-joint-frontier-nodes-per-horizon", type=int, default=2048)
    parser.add_argument("--max-joint-edges-per-step", type=int, default=8192)
    parser.add_argument("--max-internal-joint-frontier-states", type=int, default=20_000)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--checkpoint-every-pairs", type=int, default=1)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=20)
    parser.add_argument("--csv-output-mode", choices=("plain", "gzip", "both"), default="gzip")
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_signal_handlers()
    started_perf = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    horizon_schedule = parse_horizon_schedule(args.horizon_schedule, args.horizon_max)
    macro_betas = tuple(parse_float_list(args.macro_invariant_beta_list) or [0.10])
    config = {
        **instrument_metadata(),
        "claim_boundary": COUPLED_CLAIM_BOUNDARY,
        **vars(args),
        "horizon_schedule_resolved": list(horizon_schedule),
        "macro_invariant_betas": list(macro_betas),
        "condition_pairing_policy": CONDITION_PAIRING_POLICY,
        "start_pairing_policy": START_PAIRING_POLICY,
    }
    write_json(args.out / "coupled_future_field_atlas_run_config.json", config)
    conditions_a = build_generated_conditions(
        groups=args.groups,
        fresh_seeds_per_group=args.fresh_seeds_per_group,
        selection_operators=(args.selection_operator_a,),
        macro_invariant_kind=args.macro_invariant_kind,
        macro_invariant_betas=macro_betas,
        rank_boundary_k=args.rank_boundary_k,
        base_seed=args.base_seed,
    )
    conditions_b = build_generated_conditions(
        groups=args.groups,
        fresh_seeds_per_group=args.fresh_seeds_per_group,
        selection_operators=(args.selection_operator_b,),
        macro_invariant_kind=args.macro_invariant_kind,
        macro_invariant_betas=macro_betas,
        rank_boundary_k=args.rank_boundary_k,
        base_seed=args.base_seed + args.field_b_seed_offset,
    )
    tasks = build_coupled_tasks(args, conditions_a, conditions_b, horizon_schedule)
    status: dict[str, object] = {
        **instrument_metadata(),
        "claim_boundary": COUPLED_CLAIM_BOUNDARY,
        "status": "RUNNING",
        "started_utc": utc_now(),
        "out_dir": str(args.out),
        "field_A_conditions": len(conditions_a),
        "field_B_conditions": len(conditions_b),
        "condition_pairing_policy": CONDITION_PAIRING_POLICY,
        "start_pairing_policy": START_PAIRING_POLICY,
        "pair_count_requested": args.pair_count,
        "pair_count_realized": len(tasks),
        "coupled_pairs_requested": len(tasks),
        "coupled_pairs_submitted": 0,
        "coupled_pairs_completed": 0,
        "coupled_pairs_cancelled": 0,
        "workers": max(1, args.workers),
    }
    write_json(args.out / "coupled_future_field_atlas_status.json", status)
    completed, errors, progress = run_tasks(args, tasks, status, started_perf)
    write_outputs(args, completed, errors, progress, status, tasks, started_perf)


def build_coupled_tasks(
    args: argparse.Namespace,
    conditions_a: list[object],
    conditions_b: list[object],
    horizon_schedule: tuple[int, ...],
) -> list[CoupledProbeTask]:
    tasks: list[CoupledProbeTask] = []
    pair_limit = min(max(1, args.pair_count), len(conditions_a), len(conditions_b))
    coupled_operator = build_coupled_operator_spec(
        joint_selection_family=args.joint_selection_family,
        joint_effective_out_degree=max(1, args.joint_effective_out_degree),
        coupling_strength=float(args.coupling_strength),
    )
    for pair_index in range(pair_limit):
        field_a = conditions_a[pair_index]
        field_b = conditions_b[pair_index]
        starts_a = select_start_states(field_a, args.start_samples)  # type: ignore[arg-type]
        starts_b = select_start_states(field_b, args.start_samples)  # type: ignore[arg-type]
        for start_index, (start_a, start_b) in enumerate(zip(starts_a, starts_b)):
            pair_id = (
                f"pair{pair_index:03d}__A_{safe_token(field_a.spec.condition_id)}"  # type: ignore[attr-defined]
                f"__B_{safe_token(field_b.spec.condition_id)}__start{start_index:02d}"  # type: ignore[attr-defined]
            )
            tasks.append(
                CoupledProbeTask(
                    pair_id=pair_id,
                    field_a=field_a,  # type: ignore[arg-type]
                    field_b=field_b,  # type: ignore[arg-type]
                    start_index=start_index,
                    start_a=start_a,
                    start_b=start_b,
                    horizon_schedule=horizon_schedule,
                    horizon_max=args.horizon_max,
                    joint_selection_family=args.joint_selection_family,
                    joint_effective_out_degree=max(1, args.joint_effective_out_degree),
                    coupling_strength=float(args.coupling_strength),
                    coupled_operator=coupled_operator,
                    max_joint_frontier_nodes_per_horizon=max(1, args.max_joint_frontier_nodes_per_horizon),
                    max_joint_edges_per_step=max(1, args.max_joint_edges_per_step),
                    max_internal_joint_frontier_states=max(1, args.max_internal_joint_frontier_states),
                )
            )
    return tasks


def run_one(task: CoupledProbeTask) -> tuple[CoupledProbeResult | None, list[dict[str, object]]]:
    try:
        return scan_coupled_probe(task), []
    except Exception as exc:  # noqa: BLE001
        return None, [{
            "pair_id": task.pair_id,
            "A_condition_id": task.field_a.spec.condition_id,
            "B_condition_id": task.field_b.spec.condition_id,
            "error": repr(exc),
        }]


def run_tasks(
    args: argparse.Namespace,
    tasks: list[CoupledProbeTask],
    status: dict[str, object],
    started_perf: float,
) -> tuple[list[CoupledProbeResult], list[dict[str, object]], list[dict[str, object]]]:
    completed: list[CoupledProbeResult] = []
    errors: list[dict[str, object]] = []
    progress: list[dict[str, object]] = []
    pending = list(tasks)
    last_checkpoint = 0
    if max(1, args.workers) == 1:
        for task in pending:
            if should_stop(args, started_perf):
                status["status"] = "PARTIAL_TIME_LIMIT_REACHED" if not STOP_REQUESTED else "PARTIAL_INTERRUPTED"
                status["finalization_reason"] = "shutdown_cushion_or_signal"
                break
            result, task_errors = run_one(task)
            if result is not None:
                completed.append(result)
            errors.extend(task_errors)
            status["coupled_pairs_submitted"] = int(status["coupled_pairs_submitted"]) + 1
            status["coupled_pairs_completed"] = len(completed)
            if len(completed) - last_checkpoint >= max(1, args.checkpoint_every_pairs):
                progress.append(progress_row(status, completed, errors, started_perf))
                last_checkpoint = len(completed)
                write_partial(args.out, status, progress, errors, started_perf)
        if status.get("status") == "RUNNING":
            status["status"] = "COMPLETED"
            status["finalization_reason"] = "all_pairs_completed"
        progress.append(progress_row(status, completed, errors, started_perf))
        write_partial(args.out, status, progress, errors, started_perf)
        return completed, errors, progress

    futures = {}
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    try:
        while pending or futures:
            if should_stop(args, started_perf):
                status["status"] = "PARTIAL_TIME_LIMIT_REACHED" if not STOP_REQUESTED else "PARTIAL_INTERRUPTED"
                status["finalization_reason"] = "shutdown_cushion_or_signal"
                break
            while pending and len(futures) < max(1, args.workers):
                task = pending.pop(0)
                futures[executor.submit(run_one, task)] = task
                status["coupled_pairs_submitted"] = int(status["coupled_pairs_submitted"]) + 1
            done, _not_done = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                task = futures.pop(future)
                try:
                    result, task_errors = future.result()
                except Exception as exc:  # noqa: BLE001
                    result = None
                    task_errors = [{"pair_id": task.pair_id, "error": repr(exc)}]
                if result is not None:
                    completed.append(result)
                errors.extend(task_errors)
                status["coupled_pairs_completed"] = len(completed)
                if len(completed) - last_checkpoint >= max(1, args.checkpoint_every_pairs):
                    progress.append(progress_row(status, completed, errors, started_perf))
                    last_checkpoint = len(completed)
                    write_partial(args.out, status, progress, errors, started_perf)
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["coupled_pairs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    if status.get("status") == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_pairs_completed"
    progress.append(progress_row(status, completed, errors, started_perf))
    write_partial(args.out, status, progress, errors, started_perf)
    return completed, errors, progress


def write_outputs(
    args: argparse.Namespace,
    results: list[CoupledProbeResult],
    errors: list[dict[str, object]],
    progress: list[dict[str, object]],
    status: dict[str, object],
    tasks: list[CoupledProbeTask],
    started_perf: float,
) -> None:
    finalization_started = time.perf_counter()
    node_rows = [row for result in results for row in result.node_rows]
    edge_rows = [row for result in results for row in result.edge_rows]
    profile_rows = [row for result in results for row in result.profile_rows]
    marginal_rows = [row for result in results for row in result.marginal_rows]
    residual_rows = [row for result in results for row in result.residual_rows]
    marginal_projection_rows = [row for result in results for row in result.marginal_projection_rows]
    internal_cap_rows = [row for result in results for row in result.internal_cap_rows]
    condition_manifest = coupled_condition_manifest_rows(tasks)
    scan_manifest = coupled_scan_manifest_rows(tasks)
    coupled_operator_manifest = coupled_operator_manifest_rows(tasks)
    completeness_rows = artifact_completeness_rows(
        node_rows,
        edge_rows,
        profile_rows,
        marginal_rows,
        residual_rows,
        marginal_projection_rows,
        internal_cap_rows,
    )
    reconstruction_rows = reconstruction_audit_rows(node_rows, profile_rows, marginal_rows, residual_rows)
    readiness_rows = medium_scale_readiness_rows(completeness_rows, reconstruction_rows, internal_cap_rows)
    csv_jobs = [
        ("coupled_operator_manifest.csv", coupled_operator_manifest),
        ("coupled_condition_manifest.csv", condition_manifest),
        ("coupled_scan_manifest.csv", scan_manifest),
        ("coupled_joint_frontier_nodes_by_horizon.csv", node_rows),
        ("coupled_joint_frontier_edges_by_step.csv", edge_rows),
        ("coupled_joint_frontier_profile_by_horizon.csv", profile_rows),
        ("coupled_marginal_retention_by_horizon.csv", marginal_rows),
        ("coupled_joint_vs_product_residual_by_horizon.csv", residual_rows),
        ("coupled_marginal_projection_delta_by_horizon.csv", marginal_projection_rows),
        ("coupled_internal_frontier_cap_events.csv", internal_cap_rows),
        ("coupled_reconstruction_audit_summary.csv", reconstruction_rows),
        ("coupled_artifact_completeness_summary.csv", completeness_rows),
        ("coupled_medium_scale_readiness_summary.csv", readiness_rows),
    ]
    for logical_name, rows in csv_jobs:
        write_csv_artifact(args.out, logical_name, rows, args.csv_output_mode, args.gzip_compresslevel)
    status["completed_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started_perf, 3)
    status["joint_node_rows"] = len(node_rows)
    status["joint_edge_rows"] = len(edge_rows)
    status["profile_rows"] = len(profile_rows)
    status["marginal_rows"] = len(marginal_rows)
    status["residual_rows"] = len(residual_rows)
    status["marginal_projection_rows"] = len(marginal_projection_rows)
    status["internal_cap_events"] = len(internal_cap_rows)
    status["reconstruction_audit_clean_pass"] = int(all(row.get("status") == "PASS" for row in reconstruction_rows))
    status["reconstruction_audit_interpretable_pass"] = int(
        all(row.get("status") in {"PASS", "PASS_WITH_SKIPS"} for row in reconstruction_rows)
    )
    status["reconstruction_audit_passed"] = status["reconstruction_audit_clean_pass"]
    status["artifact_completeness_statuses"] = ",".join(sorted({str(row["artifact_status"]) for row in completeness_rows}))
    status["audit_status_counts_json"] = audit_status_counts(reconstruction_rows)
    status["medium_sweep_interpretation_allowed"] = readiness_rows[0]["medium_sweep_interpretation_allowed"] if readiness_rows else 0
    status["csv_output_mode"] = args.csv_output_mode
    status["gzip_compresslevel"] = args.gzip_compresslevel
    status["finalization_seconds"] = round(time.perf_counter() - finalization_started, 3)
    write_partial(args.out, status, progress, errors, started_perf)
    output_files = [
        "coupled_future_field_atlas_manifest.json",
        "coupled_future_field_atlas_run_config.json",
        "coupled_future_field_atlas_status.json",
        "coupled_future_field_atlas_progress.csv",
        "coupled_future_field_atlas_errors.csv",
        "coupled_future_field_atlas_report.md",
        *expand_csv_output_files([name for name, _rows in csv_jobs], args.csv_output_mode),
    ]
    row_counts = {name: len(rows) for name, rows in csv_jobs}
    manifest = {
        **instrument_metadata(),
        "claim_boundary": COUPLED_CLAIM_BOUNDARY,
        "run_status": status.get("status"),
        "started_utc": status.get("started_utc"),
        "completed_utc": status.get("completed_utc"),
        "horizon_max": args.horizon_max,
        "horizon_schedule": parse_horizon_schedule(args.horizon_schedule, args.horizon_max),
        "condition_pairing_policy": CONDITION_PAIRING_POLICY,
        "start_pairing_policy": START_PAIRING_POLICY,
        "pair_count_requested": args.pair_count,
        "pair_count_realized": len(tasks),
        "field_A_condition_count": len({task.field_a.spec.condition_id for task in tasks}),
        "field_B_condition_count": len({task.field_b.spec.condition_id for task in tasks}),
        "joint_selection_family": args.joint_selection_family,
        "joint_effective_out_degree": args.joint_effective_out_degree,
        "coupling_strength": args.coupling_strength,
        "output_files": [
            {
                "file": name,
                "exists": True if name == "coupled_future_field_atlas_manifest.json" else (args.out / name).exists(),
                "row_count": output_row_count(args.out, name, row_counts),
            }
            for name in output_files
        ],
    }
    write_json(args.out / "coupled_future_field_atlas_manifest.json", manifest)
    write_report(args.out, status, reconstruction_rows, completeness_rows, readiness_rows)


def coupled_condition_manifest_rows(tasks: list[CoupledProbeTask]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for task in tasks:
        if task.pair_id in seen:
            continue
        seen.add(task.pair_id)
        rows.append({
            "pair_id": task.pair_id,
            "condition_pairing_policy": CONDITION_PAIRING_POLICY,
            "start_pairing_policy": START_PAIRING_POLICY,
            "A_condition_id": task.field_a.spec.condition_id,
            "B_condition_id": task.field_b.spec.condition_id,
            "A_state_space_id": task.field_a.spec.state_space.state_space_id,
            "B_state_space_id": task.field_b.spec.state_space.state_space_id,
            "A_law_id": task.field_a.spec.transformation_law.law_id,
            "B_law_id": task.field_b.spec.transformation_law.law_id,
            "A_selection_operator_id": task.field_a.spec.selection_operator.selection_operator_id,
            "B_selection_operator_id": task.field_b.spec.selection_operator.selection_operator_id,
            "A_condition_digest": spec_digest(task.field_a.spec),
            "B_condition_digest": spec_digest(task.field_b.spec),
            "coupled_operator_id": task.coupled_operator.coupled_operator_id,
            "coupled_operator_family": task.coupled_operator.coupled_operator_family,
            "coupled_operator_digest": coupled_operator_digest(task.coupled_operator),
            "coupled_operator_canonical_json": coupled_operator_canonical_json(task.coupled_operator),
            "joint_selection_family": task.joint_selection_family,
            "joint_effective_out_degree": task.joint_effective_out_degree,
            "coupling_strength": task.coupling_strength,
            "coupled_operator_params_json": coupled_operator_params_json(task),
        })
    return rows


def coupled_operator_manifest_rows(tasks: list[CoupledProbeTask]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for task in tasks:
        spec = task.coupled_operator
        if spec.coupled_operator_id in seen:
            continue
        seen.add(spec.coupled_operator_id)
        rows.append({
            "spec_type": "coupled_operator",
            "coupled_operator_id": spec.coupled_operator_id,
            "coupled_operator_family": spec.coupled_operator_family,
            "coupled_operator_digest": coupled_operator_digest(spec),
            "product_baseline_definition": spec.product_baseline_definition,
            "joint_candidate_set_definition": spec.joint_candidate_set_definition,
            "joint_energy_function_id": spec.joint_energy_function_id,
            "joint_energy_params_json": spec.joint_energy_params_json,
            "coupling_term_id": spec.coupling_term_id,
            "coupling_strength": spec.coupling_strength,
            "joint_selection_family": spec.joint_selection_family,
            "joint_effective_out_degree": spec.joint_effective_out_degree,
            "stochastic_flag": spec.stochastic_flag,
            "seed_policy": spec.seed_policy,
            "canonical_json": coupled_operator_canonical_json(spec),
        })
    return sorted(rows, key=lambda row: str(row["coupled_operator_id"]))


def coupled_scan_manifest_rows(tasks: list[CoupledProbeTask]) -> list[dict[str, object]]:
    return [
        {
            "pair_id": task.pair_id,
            "condition_pairing_policy": CONDITION_PAIRING_POLICY,
            "start_pairing_policy": START_PAIRING_POLICY,
            "A_condition_id": task.field_a.spec.condition_id,
            "B_condition_id": task.field_b.spec.condition_id,
            "start_index": task.start_index,
            "A_start_state_id": state_id_safe(task.start_a),
            "B_start_state_id": state_id_safe(task.start_b),
            "horizon_max": task.horizon_max,
            "horizon_schedule": ";".join(str(value) for value in task.horizon_schedule),
            "joint_selection_family": task.joint_selection_family,
            "joint_effective_out_degree": task.joint_effective_out_degree,
            "coupled_operator_id": task.coupled_operator.coupled_operator_id,
            "coupled_operator_digest": coupled_operator_digest(task.coupled_operator),
            "coupling_strength": task.coupling_strength,
        }
        for task in tasks
    ]


def coupled_operator_params_json(task: CoupledProbeTask) -> str:
    from .util import canonical_json

    return canonical_json({
        "joint_selection_family": task.joint_selection_family,
        "joint_effective_out_degree": task.joint_effective_out_degree,
        "coupling_strength": task.coupling_strength,
        "coupling_energy_term": "coupling_strength * abs(A_rank_offset_from_boundary - B_rank_offset_from_boundary)",
        "product_baseline": "cartesian_product_of_component_selected_successors",
    })


def reconstruction_audit_rows(
    node_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    marginal_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [
        audit_profile_reconstructs_from_nodes(node_rows, profile_rows),
        audit_marginal_retention_reconstructs_from_nodes(node_rows, marginal_rows),
        audit_joint_residual_reconstructs_from_nodes(node_rows, residual_rows),
    ]


def audit_profile_reconstructs_from_nodes(
    node_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
) -> dict[str, object]:
    grouped: dict[tuple[str, str, int], list[dict[str, object]]] = {}
    for row in node_rows:
        key = (str(row["pair_id"]), str(row["joint_scan_mode"]), int(row["horizon"]))
        grouped.setdefault(key, []).append(row)
    checked = 0
    failed = 0
    skipped = 0
    for row in profile_rows:
        if row.get("feature_status") != "complete":
            skipped += 1
            continue
        checked += 1
        key = (str(row["pair_id"]), str(row["joint_scan_mode"]), int(row["horizon"]))
        nodes = grouped.get(key, [])
        if len(nodes) != int(row["joint_frontier_state_count"]):
            failed += 1
            continue
        if len({str(item["A_state_id"]) for item in nodes}) != int(row["A_marginal_state_count"]):
            failed += 1
            continue
        if len({str(item["B_state_id"]) for item in nodes}) != int(row["B_marginal_state_count"]):
            failed += 1
    return audit_result("coupled_profile_reconstructs_from_node_rows", checked, failed, skipped)


def audit_marginal_retention_reconstructs_from_nodes(
    node_rows: list[dict[str, object]],
    marginal_rows: list[dict[str, object]],
) -> dict[str, object]:
    grouped = nodes_by_pair_mode_horizon(node_rows)
    checked = 0
    failed = 0
    skipped = 0
    for row in marginal_rows:
        if row.get("feature_status") != "complete":
            skipped += 1
            continue
        checked += 1
        product = grouped.get((str(row["pair_id"]), "product_baseline", int(row["horizon"])), [])
        coupled = grouped.get((str(row["pair_id"]), "coupled", int(row["horizon"])), [])
        product_a = {str(item["A_state_id"]) for item in product}
        coupled_a = {str(item["A_state_id"]) for item in coupled}
        product_b = {str(item["B_state_id"]) for item in product}
        coupled_b = {str(item["B_state_id"]) for item in coupled}
        if len(product_a) != int(row["A_product_marginal_count"]):
            failed += 1
            continue
        if len(coupled_a) != int(row["A_coupled_marginal_count"]):
            failed += 1
            continue
        if len(product_b) != int(row["B_product_marginal_count"]):
            failed += 1
            continue
        if len(coupled_b) != int(row["B_coupled_marginal_count"]):
            failed += 1
    return audit_result("coupled_marginal_retention_reconstructs_from_node_rows", checked, failed, skipped)


def audit_joint_residual_reconstructs_from_nodes(
    node_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
) -> dict[str, object]:
    grouped = nodes_by_pair_mode_horizon(node_rows)
    checked = 0
    failed = 0
    skipped = 0
    for row in residual_rows:
        if row.get("feature_status") != "complete":
            skipped += 1
            continue
        checked += 1
        product = {
            str(item["joint_state_id"])
            for item in grouped.get((str(row["pair_id"]), "product_baseline", int(row["horizon"])), [])
        }
        coupled = {
            str(item["joint_state_id"])
            for item in grouped.get((str(row["pair_id"]), "coupled", int(row["horizon"])), [])
        }
        if len(product) != int(row["product_joint_support_count"]):
            failed += 1
            continue
        if len(coupled) != int(row["coupled_joint_support_count"]):
            failed += 1
            continue
        if len(product & coupled) != int(row["joint_support_intersection_count"]):
            failed += 1
    return audit_result("coupled_joint_residual_reconstructs_from_node_rows", checked, failed, skipped)


def nodes_by_pair_mode_horizon(
    node_rows: list[dict[str, object]],
) -> dict[tuple[str, str, int], list[dict[str, object]]]:
    grouped: dict[tuple[str, str, int], list[dict[str, object]]] = {}
    for row in node_rows:
        key = (str(row["pair_id"]), str(row["joint_scan_mode"]), int(row["horizon"]))
        grouped.setdefault(key, []).append(row)
    return grouped


def audit_result(audit_name: str, checked: int, failed: int, skipped: int) -> dict[str, object]:
    if failed > 0:
        status = "FAIL"
    elif checked == 0 and skipped > 0:
        status = "NO_COMPLETE_ROWS"
    elif skipped > 0:
        status = "PASS_WITH_SKIPS"
    else:
        status = "PASS"
    return {
        "audit_name": audit_name,
        "status": status,
        "checked_items": checked,
        "failed_items": failed,
        "skipped_items": skipped,
    }


def audit_status_counts(reconstruction_rows: list[dict[str, object]]) -> dict[str, int]:
    counts = {"PASS": 0, "PASS_WITH_SKIPS": 0, "NO_COMPLETE_ROWS": 0, "FAIL": 0}
    for row in reconstruction_rows:
        status = str(row.get("status", ""))
        if status not in counts:
            counts[status] = 0
        counts[status] += 1
    return counts


def medium_scale_readiness_rows(
    completeness_rows: list[dict[str, object]],
    reconstruction_rows: list[dict[str, object]],
    internal_cap_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    artifact_counts: dict[str, int] = {"complete": 0, "sampled": 0, "truncated_noninterpretable": 0}
    for row in completeness_rows:
        status = str(row.get("artifact_status", ""))
        artifact_counts[status] = artifact_counts.get(status, 0) + int(row.get("row_count", 0) or 0)
    audit_counts = audit_status_counts(reconstruction_rows)
    primary_comparison_no_complete = any(
        row.get("status") == "NO_COMPLETE_ROWS"
        for row in reconstruction_rows
        if row.get("audit_name") in {
            "coupled_marginal_retention_reconstructs_from_node_rows",
            "coupled_joint_residual_reconstructs_from_node_rows",
        }
    )
    has_fail = audit_counts.get("FAIL", 0) > 0
    has_skips = audit_counts.get("PASS_WITH_SKIPS", 0) > 0
    interpretation_allowed = int(not has_fail and not primary_comparison_no_complete and not internal_cap_rows)
    if primary_comparison_no_complete:
        recommendation = "do_not_interpret_coupled_geometry_no_complete_primary_comparison_rows"
    elif has_fail:
        recommendation = "repair_failed_reconstruction_audits_before_medium_sweep"
    elif internal_cap_rows:
        recommendation = "medium_sweep_allowed_only_as_operational_probe_or_after_cap_limit_adjustment"
    elif has_skips:
        recommendation = "interpret_complete_rows_only"
    else:
        recommendation = "medium_sweep_infrastructure_ready"
    return [{
        "complete_rows": artifact_counts.get("complete", 0),
        "sampled_rows": artifact_counts.get("sampled", 0),
        "truncated_noninterpretable_rows": artifact_counts.get("truncated_noninterpretable", 0),
        "internal_cap_events": len(internal_cap_rows),
        "audits_PASS": audit_counts.get("PASS", 0),
        "audits_PASS_WITH_SKIPS": audit_counts.get("PASS_WITH_SKIPS", 0),
        "audits_NO_COMPLETE_ROWS": audit_counts.get("NO_COMPLETE_ROWS", 0),
        "audits_FAIL": audit_counts.get("FAIL", 0),
        "medium_sweep_interpretation_allowed": interpretation_allowed,
        "interpretation_scope": "complete_rows_only" if has_skips else "all_primary_rows_complete",
        "recommendation": recommendation,
    }]


def artifact_completeness_rows(
    node_rows: list[dict[str, object]],
    edge_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    marginal_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
    marginal_projection_rows: list[dict[str, object]],
    internal_cap_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for artifact_name, artifact_rows, status_field in (
        ("coupled_joint_frontier_nodes_by_horizon.csv", node_rows, "node_artifact_status"),
        ("coupled_joint_frontier_edges_by_step.csv", edge_rows, "edge_artifact_status"),
        ("coupled_joint_frontier_profile_by_horizon.csv", profile_rows, "feature_status"),
        ("coupled_marginal_retention_by_horizon.csv", marginal_rows, "feature_status"),
        ("coupled_joint_vs_product_residual_by_horizon.csv", residual_rows, "feature_status"),
        ("coupled_marginal_projection_delta_by_horizon.csv", marginal_projection_rows, "feature_status"),
        ("coupled_internal_frontier_cap_events.csv", internal_cap_rows, "artifact_status"),
    ):
        counts: dict[str, int] = {}
        for row in artifact_rows:
            status = str(row.get(status_field, "complete") or "complete")
            counts[status] = counts.get(status, 0) + 1
        if not counts:
            counts["complete"] = 0
        for artifact_status, count in sorted(counts.items()):
            rows.append({
                "artifact_name": artifact_name,
                "status_field": status_field,
                "artifact_status": artifact_status,
                "row_count": count,
            })
    return rows


def write_partial(
    out_dir: Path,
    status: dict[str, object],
    progress: list[dict[str, object]],
    errors: list[dict[str, object]],
    started_perf: float,
) -> None:
    status["elapsed_seconds"] = round(time.perf_counter() - started_perf, 3)
    write_json(out_dir / "coupled_future_field_atlas_status.json", status)
    write_csv(out_dir / "coupled_future_field_atlas_progress.csv", progress, gzip_compresslevel=1)
    write_csv(out_dir / "coupled_future_field_atlas_errors.csv", errors, gzip_compresslevel=1)


def write_report(
    out_dir: Path,
    status: dict[str, object],
    reconstruction_rows: list[dict[str, object]],
    completeness_rows: list[dict[str, object]],
    readiness_rows: list[dict[str, object]],
) -> None:
    readiness = readiness_rows[0] if readiness_rows else {}
    lines = [
        "# Coupled Future Field Atlas Smoke",
        "",
        f"Status: {status.get('status', '')}",
        f"Elapsed seconds: {status.get('elapsed_seconds', '')}",
        "",
        f"Claim boundary: {COUPLED_CLAIM_BOUNDARY}",
        "",
        "## Scope",
        "",
        "This is an infrastructure probe. It compares product-baseline joint frontier topology with a coupled joint selector over product successors.",
        "",
        "## Counts",
        "",
        f"- Coupled pairs completed: `{status.get('coupled_pairs_completed', '')}` / `{status.get('coupled_pairs_requested', '')}`",
        f"- Joint node rows: `{status.get('joint_node_rows', '')}`",
        f"- Joint edge rows: `{status.get('joint_edge_rows', '')}`",
        f"- Internal cap events: `{status.get('internal_cap_events', '')}`",
        f"- Artifact completeness statuses: `{status.get('artifact_completeness_statuses', '')}`",
        f"- Reconstruction clean pass: `{status.get('reconstruction_audit_clean_pass', '')}`",
        f"- Reconstruction interpretable pass: `{status.get('reconstruction_audit_interpretable_pass', '')}`",
        f"- Medium-sweep interpretation allowed: `{status.get('medium_sweep_interpretation_allowed', '')}`",
        "",
        "## Reconstruction Audits",
        "",
        *[
            f"- `{row['audit_name']}`: {row['status']} ({row['checked_items']} checked, {row['failed_items']} failed, {row['skipped_items']} skipped)"
            for row in reconstruction_rows
        ],
        "",
        "## Artifact Completeness",
        "",
        *[
            f"- `{row['artifact_name']}` / `{row['artifact_status']}`: {row['row_count']} rows"
            for row in completeness_rows
        ],
        "",
        "## Medium-Scale Readiness Guard",
        "",
        *[
            f"- `{key}`: {value}"
            for key, value in readiness.items()
        ],
        "",
        "## Primary Artifacts",
        "",
        "- `coupled_operator_manifest.csv[.gz]`",
        "- `coupled_condition_manifest.csv[.gz]`",
        "- `coupled_scan_manifest.csv[.gz]`",
        "- `coupled_joint_frontier_nodes_by_horizon.csv[.gz]`",
        "- `coupled_joint_frontier_edges_by_step.csv[.gz]`",
        "- `coupled_joint_frontier_profile_by_horizon.csv[.gz]`",
        "- `coupled_marginal_retention_by_horizon.csv[.gz]`",
        "- `coupled_joint_vs_product_residual_by_horizon.csv[.gz]`",
        "- `coupled_marginal_projection_delta_by_horizon.csv[.gz]`",
        "- `coupled_reconstruction_audit_summary.csv[.gz]`",
        "- `coupled_artifact_completeness_summary.csv[.gz]`",
        "- `coupled_medium_scale_readiness_summary.csv[.gz]`",
    ]
    (out_dir / "coupled_future_field_atlas_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv_artifact(
    out_dir: Path,
    logical_name: str,
    rows: list[dict[str, object]],
    csv_output_mode: str,
    gzip_compresslevel: int,
) -> None:
    for name in expand_csv_output_files([logical_name], csv_output_mode):
        write_csv(out_dir / name, rows, gzip_compresslevel=gzip_compresslevel)


def expand_csv_output_files(logical_names: list[str], csv_output_mode: str) -> list[str]:
    if csv_output_mode == "plain":
        return list(logical_names)
    if csv_output_mode == "gzip":
        return [f"{name}.gz" for name in logical_names]
    if csv_output_mode == "both":
        return [item for name in logical_names for item in (name, f"{name}.gz")]
    raise ValueError(f"unknown csv output mode: {csv_output_mode}")


def output_row_count(out_dir: Path, name: str, csv_row_counts: dict[str, int]) -> int | str:
    if name in csv_row_counts:
        return csv_row_counts[name]
    logical_name = name.removesuffix(".gz") if name.endswith(".csv.gz") else name
    if logical_name in csv_row_counts:
        return csv_row_counts[logical_name]
    if name.endswith((".csv", ".csv.gz")):
        return csv_row_count(out_dir / name)
    return ""


def progress_row(
    status: dict[str, object],
    completed: list[CoupledProbeResult],
    errors: list[dict[str, object]],
    started_perf: float,
) -> dict[str, object]:
    return {
        "timestamp_utc": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - started_perf, 3),
        "status": status.get("status", ""),
        "coupled_pairs_submitted": status.get("coupled_pairs_submitted", 0),
        "coupled_pairs_completed": len(completed),
        "errors": len(errors),
    }


def parse_horizon_schedule(raw: str, horizon_max: int) -> tuple[int, ...]:
    token = str(raw or "").strip()
    if token in {"", "dense"}:
        return tuple(range(0, horizon_max + 1))
    if token == "dense_to_16_plus_h64":
        values = list(range(0, min(16, horizon_max) + 1))
        values.extend([24, 32, 48, 64])
        return tuple(sorted({value for value in values if value <= horizon_max}))
    return tuple(sorted({int(item.strip()) for item in token.split(",") if item.strip() and int(item.strip()) <= horizon_max}))


def parse_float_list(raw: str) -> list[float]:
    return [float(item.strip()) for item in str(raw or "").split(",") if item.strip()]


def should_stop(args: argparse.Namespace, started_perf: float) -> bool:
    if STOP_REQUESTED:
        return True
    elapsed = time.perf_counter() - started_perf
    return elapsed >= max(0, args.max_runtime_seconds - args.shutdown_cushion_seconds)


def state_id_safe(state: object) -> str:
    from .util import state_id

    return state_id(state)  # type: ignore[arg-type]


def handle_stop(_signum: int, _frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def install_signal_handlers() -> None:
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, handle_stop)


if __name__ == "__main__":
    main()
