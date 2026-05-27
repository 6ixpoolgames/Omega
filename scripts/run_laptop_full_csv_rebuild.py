from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_ROOT = ROOT / "results" / "rfs_mb0_relation_atlas"
STATUS_PATH = RESULT_ROOT / "20260528_laptop_full_csv_rebuild_status.json"
LOG_PATH = RESULT_ROOT / "20260528_laptop_full_csv_rebuild.log"

WORKERS = 7
JOB_BATCH_SIZE = 2
GLOBAL_WALL_SECONDS = 10_800
GLOBAL_CUSHION_SECONDS = 900

RELATION_BATCH = RESULT_ROOT / "20260528_laptop_relation_atlas_batch_rebuild"
PHENOTYPE = RESULT_ROOT / "20260528_laptop_relation_generator_phenotype_repair"
TAXONOMY = RESULT_ROOT / "20260528_laptop_support_distribution_taxonomy"
BOUNDARY_SWEEP = RESULT_ROOT / "20260526_boundary_resolution_sweep"
BOUNDARY_REPAIR = RESULT_ROOT / "20260527_boundary_recurrence_repair_batch1"
CORRECTED = RESULT_ROOT / "20260527_detector_instrumentation_repair_scaled"
PHASE_B = RESULT_ROOT / "20260528_frontier_transform_phase_b_regenerated_full_controls"


def main() -> int:
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    status: dict[str, object] = {
        "status": "RUNNING",
        "machine_role": "laptop",
        "hardware_profile": {
            "cpu": "Intel Core i7-1165G7",
            "logical_processors": 8,
            "gpu": "Intel Iris Xe integrated",
            "cuda_available": False,
            "workers": WORKERS,
            "job_batch_size": JOB_BATCH_SIZE,
            "thread_caps": 1,
        },
        "claim_boundary": "Laptop-local upstream provenance rebuild plus full-control Phase B CSV regeneration.",
        "global_wall_seconds": GLOBAL_WALL_SECONDS,
        "global_cushion_seconds": GLOBAL_CUSHION_SECONDS,
        "stages": [],
        "outputs": {
            "relation_batch": str(RELATION_BATCH.relative_to(ROOT)),
            "phenotype": str(PHENOTYPE.relative_to(ROOT)),
            "taxonomy": str(TAXONOMY.relative_to(ROOT)),
            "boundary_sweep": str(BOUNDARY_SWEEP.relative_to(ROOT)),
            "boundary_repair": str(BOUNDARY_REPAIR.relative_to(ROOT)),
            "corrected": str(CORRECTED.relative_to(ROOT)),
            "phase_b": str(PHASE_B.relative_to(ROOT)),
        },
    }
    write_status(status, started)

    env = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_MAX_THREADS", "NUMBA_NUM_THREADS"):
        env[key] = "1"

    LOG_PATH.write_text("", encoding="utf-8")

    stage_plan = [
        (
            "relation_atlas_batch_seed",
            [
                sys.executable,
                "-m",
                "omega.rfs_mb0_future_landscape.run_relation_atlas_batch",
                "--root-out",
                str(RELATION_BATCH),
                "--global-wall-clock-seconds",
                "2400",
                "--workers",
                str(WORKERS),
                "--stage-b-samples",
                "80",
                "--stage-c-samples",
                "60",
                "--stage-c-seeds",
                "1",
                "--stage-d-samples",
                "20",
                "--start-samples",
                "3",
                "--stress-sample-count",
                "80",
                "--null-replicates",
                "0",
            ],
            RELATION_BATCH / "confirmatory_regions_preregistered.json",
            2400,
        ),
        (
            "candidate_phenotype_repair",
            [
                sys.executable,
                "-m",
                "omega.rfs_mb0_future_landscape.run_candidate_phenotype_audit",
                "--out",
                str(PHENOTYPE),
                "--parameter-region-file",
                str(RELATION_BATCH / "confirmatory_regions_preregistered.json"),
                "--parameter-samples",
                "24",
                "--seeds-per-parameter-set",
                "1",
                "--start-samples-list",
                "1,3,8",
                "--null-replicates",
                "0",
                "--workers",
                str(WORKERS),
                "--max-runtime-seconds",
                "1500",
                "--per-stage-runtime-seconds",
                "450",
                "--stress-sample-count",
                "80",
            ],
            PHENOTYPE / "candidate_phenotype_summary.csv",
            1500,
        ),
        (
            "support_distribution_taxonomy",
            [
                sys.executable,
                "-m",
                "omega.rfs_mb0_future_landscape.run_support_distribution_taxonomy",
                "--source-run",
                str(PHENOTYPE),
                "--out",
                str(TAXONOMY),
                "--candidate-envs",
                "24",
                "--start-samples-list",
                "3,8",
                "--horizons",
                "0,1,2,4,8,12,16",
                "--workers",
                str(WORKERS),
                "--max-jobs",
                "720",
                "--checkpoint-every",
                "72",
                "--max-runtime-seconds",
                "1500",
            ],
            TAXONOMY / "support_distribution_metric_by_horizon.csv",
            1500,
        ),
        (
            "boundary_resolution_sweep",
            [
                sys.executable,
                "-m",
                "omega.rfs_mb0_future_landscape.run_deformation_detector_sweep",
                "--source-run",
                str(TAXONOMY),
                "--out",
                str(BOUNDARY_SWEEP),
                "--anchors",
                "12",
                "--fresh-seeds-per-variant",
                "2",
                "--start-samples-list",
                "3,8",
                "--horizons",
                "0,1,2,4,8,12,16,24",
                "--workers",
                str(WORKERS),
                "--max-sweep-jobs",
                "288",
                "--checkpoint-every",
                "36",
                "--max-runtime-seconds",
                "1800",
            ],
            BOUNDARY_SWEEP / "atlas_band_selection.csv",
            1800,
        ),
        (
            "boundary_recurrence_repair",
            [
                sys.executable,
                "-m",
                "omega.rfs_mb0_future_landscape.run_boundary_recurrence_repair",
                "--source-run",
                str(BOUNDARY_SWEEP),
                "--out",
                str(BOUNDARY_REPAIR),
                "--anchors-requested",
                "10",
                "--top-groups",
                "20",
            ],
            BOUNDARY_REPAIR / "focused_boundary_group_selection.csv",
            300,
        ),
        (
            "detector_instrumentation_repair_scaled",
            [
                sys.executable,
                "-m",
                "omega.rfs_mb0_future_landscape.run_focused_boundary_recurrence",
                "--selection",
                str(BOUNDARY_REPAIR / "focused_boundary_group_selection.csv"),
                "--source-run",
                str(BOUNDARY_SWEEP),
                "--out",
                str(CORRECTED),
                "--groups",
                "20",
                "--fresh-seeds-per-group",
                "4",
                "--start-samples-list",
                "3,8",
                "--probe-families",
                "coordinate_tuple_k3,coordinate_tuple_k4,constraint_profile_hash,constraint_violation_count_plus_local_tuple,existing_low,full_state_hash",
                "--workers",
                str(WORKERS),
                "--max-runtime-seconds",
                "1800",
                "--shutdown-cushion-seconds",
                "300",
            ],
            CORRECTED / "corrected_group_classification.csv",
            1800,
        ),
    ]

    try:
        for name, command, required_path, stage_budget in stage_plan:
            if not enough_time_left(started, min(stage_budget, 1200)):
                append_stage(status, name, "SKIPPED_TIME_LIMIT", started, required_path=required_path)
                break
            run_stage(status, started, name, command, required_path, env)
            if not required_path.exists():
                status["status"] = "BLOCKED"
                status["blocked_reason"] = f"required output missing after {name}: {required_path}"
                write_status(status, started)
                return 2

        phase_b_required_inputs = [
            BOUNDARY_REPAIR / "focused_boundary_group_selection.csv",
            CORRECTED / "corrected_group_classification.csv",
            BOUNDARY_SWEEP / "atlas_band_selection.csv",
        ]
        missing = [str(path.relative_to(ROOT)) for path in phase_b_required_inputs if not path.exists()]
        if missing:
            status["status"] = "BLOCKED"
            status["blocked_reason"] = "phase_b_inputs_missing"
            status["missing_phase_b_inputs"] = missing
            write_status(status, started)
            return 2

        remaining = int(GLOBAL_WALL_SECONDS - (time.perf_counter() - started))
        if remaining <= GLOBAL_CUSHION_SECONDS + 600:
            status["status"] = "PARTIAL_TIME_LIMIT_REACHED"
            status["finalization_reason"] = "phase_b_not_started_due_global_cushion"
            write_status(status, started)
            return 0

        phase_b_runtime = max(1200, remaining)
        phase_b_command = [
            sys.executable,
            "-m",
            "omega.rfs_mb0_future_landscape.run_frontier_transform_phase_b",
            "--selection",
            str(BOUNDARY_REPAIR / "focused_boundary_group_selection.csv"),
            "--corrected",
            str(CORRECTED / "corrected_group_classification.csv"),
            "--source-run",
            str(BOUNDARY_SWEEP),
            "--out",
            str(PHASE_B),
            "--groups",
            "20",
            "--design-groups",
            "10",
            "--fakeout-groups",
            "4",
            "--neutral-anchors",
            "6",
            "--fresh-seeds-per-group",
            "8",
            "--start-samples-list",
            "4,8,16",
            "--probes",
            "constraint_profile_hash,constraint_violation_count_plus_local_tuple,existing_low,full_state_hash",
            "--workers",
            str(WORKERS),
            "--job-batch-size",
            str(JOB_BATCH_SIZE),
            "--checkpoint-every-jobs",
            "120",
            "--max-runtime-seconds",
            str(phase_b_runtime),
            "--shutdown-cushion-seconds",
            str(GLOBAL_CUSHION_SECONDS),
            "--skip-row-level-effect-csv",
        ]
        run_stage(status, started, "frontier_transform_phase_b_full_controls", phase_b_command, PHASE_B / "phase_b_design_control_rows.csv", env)
        phase_b_csv = PHASE_B / "phase_b_design_control_rows.csv"
        if phase_b_csv.exists() and phase_b_csv.stat().st_size > 100:
            status["status"] = "COMPLETED"
            status["finalization_reason"] = "phase_b_full_control_csv_written"
        else:
            status["status"] = "PARTIAL_TIME_LIMIT_REACHED"
            status["finalization_reason"] = "phase_b_full_control_csv_missing_or_sentinel"
        write_status(status, started)
        return 0
    except KeyboardInterrupt:
        status["status"] = "PARTIAL_INTERRUPTED"
        status["finalization_reason"] = "keyboard_interrupt"
        write_status(status, started)
        return 130


def enough_time_left(started: float, needed: int) -> bool:
    return GLOBAL_WALL_SECONDS - (time.perf_counter() - started) > GLOBAL_CUSHION_SECONDS + needed


def run_stage(
    status: dict[str, object],
    started: float,
    name: str,
    command: list[str],
    required_path: Path,
    env: dict[str, str],
) -> None:
    stage = {
        "name": name,
        "status": "RUNNING",
        "started_elapsed_seconds": round(time.perf_counter() - started, 3),
        "required_output": str(required_path.relative_to(ROOT)),
        "command": command,
    }
    status["stages"].append(stage)
    write_status(status, started)
    with LOG_PATH.open("a", encoding="utf-8") as log:
        log.write(f"\n\n=== {name} ===\n")
        log.write(" ".join(command) + "\n")
        log.flush()
        proc = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=False)
    stage["returncode"] = proc.returncode
    stage["completed_elapsed_seconds"] = round(time.perf_counter() - started, 3)
    stage["required_output_exists"] = required_path.exists()
    if required_path.exists():
        stage["required_output_bytes"] = required_path.stat().st_size
    stage["status"] = "COMPLETED" if proc.returncode == 0 and required_path.exists() else "FAILED"
    write_status(status, started)


def append_stage(
    status: dict[str, object],
    name: str,
    stage_status: str,
    started: float,
    required_path: Path,
) -> None:
    status["stages"].append(
        {
            "name": name,
            "status": stage_status,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "required_output": str(required_path.relative_to(ROOT)),
            "required_output_exists": required_path.exists(),
        }
    )
    write_status(status, started)


def write_status(status: dict[str, object], started: float) -> None:
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    STATUS_PATH.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
