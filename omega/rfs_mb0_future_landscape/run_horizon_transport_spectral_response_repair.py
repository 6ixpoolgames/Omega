"""Run horizon-transport response-surface instrumentation.

The runner builds directional horizon transport matrices from the Stage B-2
future-field substrate, applies matched detector nulls, classifies perturbation
responses, and writes machine-readable audit artifacts. It is not a promotion
or detection script for Omega, agency, identity, or value.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import signal
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median, pstdev

import numpy as np

from .landscape import exact_frontier
from .run_deformation_detector_sweep import stable_seed
from .run_focused_boundary_recurrence import float_or_zero, read_csv, write_csv
from .run_frontier_transform_stage_b2_mechanism_calibration import BASELINE_CONTROL, make_stage_b2_control_system
from .run_instrumentation_phase_a import build_holdout_split
from .run_stage_b2_spectral_future_field_geometry_smoke import (
    build_jobs,
    effective_rank,
    group_by,
    parse_float_list,
    run_batch,
    spectral_gap,
)
from .horizon_transport_contracts import (
    ASYMMETRY_LADDER,
    COMMON_OUTPUTS,
    DETECTOR_NULL_FAMILIES,
    DETECTOR_STATISTICS,
    INTERPRETATION_CONTROL_FAMILIES,
    MARGINAL_MATCHED_NULL_FAMILIES,
    MATCHED_NULL_SPEC_ID,
    MAX_ENTROPY_PREFLIGHT,
    PARENT_SPEC_ID,
    RUNNER_MODULE,
    STRUCTURE_DESTROYING_NULL_FAMILIES,
    SWEEP_KINDS,
    TRANSITION_ENERGY_CHARACTERIZATION,
    active_spec_id,
    artifact_prefix,
    attach_horizon_pairs,
    errors_filename,
    manifest_filename,
    parse_horizon_pairs,
    progress_filename,
    report_filename,
    run_config_filename,
    run_kind,
    run_phase,
    status_filename,
    status_run_kind,
)
from .horizon_transport_response_taxonomy import (
    MEASUREMENT_LIMIT_RESPONSE_CLASSES,
    RESPONSE_CLASS_AMPLIFIED_ALIGNED,
    RESPONSE_CLASS_COLLAPSES,
    RESPONSE_CLASS_CONTROL_EQUIVALENT,
    RESPONSE_CLASS_REOPENS,
    RESPONSE_CLASS_REROUTED,
    RESPONSE_CLASS_STABLE,
    RESPONSE_CLASS_WEAKENED,
    classify_response,
    is_interpretable_response,
    response_flags,
)
from .spectral_contracts import (
    CLAIM_BOUNDARY,
    LOCAL_ONLY_ARTIFACT_POLICY,
    instrument_metadata,
    output_manifest_rows,
    utc_now,
    write_json,
)
from .transition_energy_substrates import (
    BUDGET_CONSERVATION,
    COMBINED_ASYMMETRY,
    CONSTRAINT_TEMPLATE_CURRENT,
    DIRECTIONAL_ASYMMETRY,
    LOCALITY_ONLY,
    MAX_ENTROPY_FAMILIES,
    MAX_ENTROPY_LOCAL,
    MAX_ENTROPY_MACRO_INVARIANT,
    PRESERVATION_ASYMMETRY,
    SMOOTH_RANDOM_POTENTIAL,
    TRANSITION_ENERGY_FAMILIES,
    canonical_transition_energy_family,
    generate_job_baseline_system,
)


STOP_REQUESTED = False


@dataclass(frozen=True)
class TransportKey:
    condition_id: str
    actual_control_name: str
    mechanism_control_strength: float
    probe_key: str
    flow_mode: str
    source_horizon_band: str
    target_horizon_band: str
    H_a: int
    H_b: int


@dataclass
class TransportMatrix:
    key: TransportKey
    matrix_id: str
    row_items: list[str]
    column_items: list[str]
    matrix: np.ndarray
    transport_context_count: int
    transport_mass_total: float
    retained_transport_mass: float
    dropped_transport_mass: float
    raw_row_item_count: int
    raw_column_item_count: int
    singular_values: np.ndarray
    left_vectors: np.ndarray
    right_vectors: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 horizon-transport spectral response repair smoke.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/local_runs/20260530_horizon_transport_spectral_response_repair"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=1)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=1)
    parser.add_argument("--start-samples-list", type=str, default="4")
    parser.add_argument("--probes", type=str, default="constraint_profile_hash,constraint_violation_count_plus_local_tuple")
    parser.add_argument("--roughness-seed-replicates", type=int, default=0)
    parser.add_argument("--small-edge-resample-strengths", type=str, default="0.0025,0.005")
    parser.add_argument("--asymmetry-multipliers", type=str, default="")
    parser.add_argument("--asymmetric-edge-flip-strengths", type=str, default="0.0025,0.005")
    parser.add_argument("--constraint-proxy-strengths", type=str, default="")
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--job-batch-size", type=int, default=2)
    parser.add_argument("--checkpoint-every-jobs", type=int, default=20)
    parser.add_argument("--max-runtime-seconds", type=int, default=7200)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=600)
    parser.add_argument("--max-items-per-context", type=int, default=64)
    parser.add_argument("--max-items-per-side", type=int, default=128)
    parser.add_argument("--matrix-entry-top-k", type=int, default=256, help="Maximum nonzero transport entries retained per matrix for raw structure visualization.")
    parser.add_argument("--raw-state-sample-jobs", type=int, default=0, help="Number of built jobs to sample for raw substrate state frontier heatmaps. Zero disables this local diagnostic.")
    parser.add_argument("--raw-state-sample-starts", type=int, default=1, help="Start states per sampled job for raw substrate state frontier diagnostics.")
    parser.add_argument("--raw-state-sample-states", type=int, default=256, help="Maximum raw substrate states retained per sampled frontier.")
    parser.add_argument("--selected-edge-overlap-sample-jobs", type=int, default=64, help="Number of unique substrate jobs sampled for selected-edge overlap by beta. Zero disables this audit.")
    parser.add_argument("--min-item-count", type=int, default=1)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--null-replicates", type=int, default=5)
    parser.add_argument("--detector-null-min-pass-fraction", type=float, default=0.50)
    parser.add_argument("--detector-null-min-percentile", type=float, default=0.80)
    parser.add_argument("--fixture-smoke", action="store_true", help="Run synthetic horizon-transport fixtures instead of empirical jobs.")
    parser.add_argument("--expansion-smoke", action="store_true", help="Write expansion-smoke outputs and readiness labels.")
    parser.add_argument("--h128-scaleup", action="store_true", help="Write H128 response-surface outputs and readiness labels.")
    parser.add_argument("--sweep-kind", choices=("", *sorted(SWEEP_KINDS)), default="", help="Optional viscosity/horizon/breadth/substrate sweep mode with sweep-specific defaults and report names.")
    parser.add_argument("--horizon-pairs", type=str, default="", help="Comma-separated horizon pairs like 0->1,1->2. Defaults to H128 pairs when --h128-scaleup is set, otherwise H32 pairs.")
    parser.add_argument("--substrate-families", type=str, default=CONSTRAINT_TEMPLATE_CURRENT, help="Comma-separated substrate families. Use transition-energy families for untethering smokes.")
    parser.add_argument("--potential-beta", type=float, default=0.5, help="Smooth-potential transition-energy beta for transition-energy substrates.")
    parser.add_argument("--potential-smoothness", type=float, default=0.85, help="Additive smoothness of the random potential field.")
    parser.add_argument("--potential-scale", type=float, default=1.0, help="Scale of the smooth random potential field.")
    parser.add_argument("--budget-kind", type=str, default="total_coordinate_mass", help="Implementation name for invariant statistic in macro-invariant substrates.")
    parser.add_argument("--invariant-kind", dest="budget_kind", type=str, help="Public alias for --budget-kind.")
    parser.add_argument("--macro-invariant-kind", dest="budget_kind", type=str, help="Public alias for --budget-kind.")
    parser.add_argument("--budget-weight", type=float, default=1.0, help="Implementation name for invariant penalty weight in macro-invariant substrates.")
    parser.add_argument("--invariant-weight", "--asymmetry-penalty-weight", dest="budget_weight", type=float, help="Public/theory alias for --budget-weight.")
    parser.add_argument("--macro-invariant-beta", type=float, default=None, help="Public beta for preservation-asymmetry transition-energy substrates.")
    parser.add_argument("--asymmetry-alpha", type=float, default=0.5, help="Directional-asymmetry alpha for transition-energy substrates.")
    parser.add_argument("--asymmetry-field-smoothness", type=float, default=0.65, help="Smoothness for the directional asymmetry field.")
    parser.add_argument("--asymmetry-field-scale", type=float, default=1.0, help="Scale for the directional asymmetry field.")
    parser.add_argument("--transition-roughness-strength", type=float, default=-1.0, help="Override transition-energy roughness strength. Negative uses RelationParams roughness_strength.")
    parser.add_argument("--locality-roughness-strengths", type=str, default="", help="Characterization roughness variants for locality_only. Use comma-separated floats plus optional current.")
    parser.add_argument("--potential-smoothness-list", type=str, default="", help="Characterization smooth-potential smoothness variants.")
    parser.add_argument("--potential-beta-list", type=str, default="", help="Characterization smooth-potential beta variants.")
    parser.add_argument("--budget-kinds", type=str, default="", help="Characterization invariant variants; retained implementation name.")
    parser.add_argument("--invariant-kinds", dest="budget_kinds", type=str, help="Public alias for --budget-kinds.")
    parser.add_argument("--macro-invariant-kinds", dest="budget_kinds", type=str, help="Public alias for --budget-kinds.")
    parser.add_argument("--budget-weights", type=str, default="", help="Characterization invariant-weight variants; retained implementation name.")
    parser.add_argument("--invariant-weights", "--asymmetry-penalty-weights", dest="budget_weights", type=str, help="Public/theory alias for --budget-weights.")
    parser.add_argument("--macro-invariant-beta-list", type=str, default="", help="Preservation-asymmetry beta variants.")
    parser.add_argument("--equivalent-beta-target-list", type=str, default="", help="MaxEnt calibration beta targets for deterministic preservation-asymmetry edge-marginal matching.")
    parser.add_argument("--max-entropy-sampler-draws", type=int, default=16, help="Deterministic weighted sampling draws per MaxEnt macro-invariant substrate job.")
    parser.add_argument("--max-entropy-delta-match-error-max", type=float, default=0.10, help="Total-variation tolerance for MaxEnt macro-invariant delta marginal matching.")
    parser.add_argument("--asymmetry-alpha-list", type=str, default="", help="Directional-asymmetry alpha variants.")
    parser.add_argument("--asymmetry-field-smoothness-list", type=str, default="", help="Directional-asymmetry field-smoothness variants.")
    parser.add_argument("--combined-alpha-beta-pairs", type=str, default="", help="Sparse combined-asymmetry pairs like 0.25:0.5,0.5:1.0.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_signal_handlers()
    started = time.perf_counter()
    repo_root = Path(__file__).resolve().parents[2]
    args.out.mkdir(parents=True, exist_ok=True)
    kind = run_kind(args)
    metadata = {
        **instrument_metadata(active_spec_id(args), RUNNER_MODULE, repo_root),
        "parent_spec_id": PARENT_SPEC_ID,
        "matched_null_spec_id": MATCHED_NULL_SPEC_ID,
    }
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    starts = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    horizon_pairs = parse_horizon_pairs(args.horizon_pairs, use_h128=args.h128_scaleup, sweep_kind=args.sweep_kind)
    if args.fixture_smoke:
        jobs: list[dict[str, object]] = []
    else:
        groups, split_rows = build_holdout_split(args)
        anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
        jobs = build_jobs(args, groups, split_rows, anchors, probes, starts)
        attach_horizon_pairs(jobs, horizon_pairs)
        jobs = expand_jobs_for_substrate_families(jobs, args)
    write_json(args.out / run_config_filename(kind), {
        **metadata,
        **vars(args),
        "job_count": len(jobs),
        "run_kind": kind,
        "horizon_pairs": [f"{left}->{right}" for left, right in horizon_pairs],
        "substrate_families": substrate_families(args),
        "substrate_family_variants": substrate_family_variants(args),
        "raw_state_sample_requested_jobs": int(args.raw_state_sample_jobs),
        "claim_boundary": CLAIM_BOUNDARY,
    })
    status: dict[str, object] = {
        **metadata,
        "status": "RUNNING",
        "phase": run_phase(kind),
        "run_kind": kind,
        "artifact_prefix": artifact_prefix(kind),
        "report_file": report_filename(kind),
        "started_utc": utc_now(),
        "out_dir": str(args.out),
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "workers": args.workers,
        "job_batch_size": args.job_batch_size,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "candidate_promotion_enabled": False,
        "artifact_policy": LOCAL_ONLY_ARTIFACT_POLICY,
        "fixture_smoke_enabled": bool(args.fixture_smoke),
        "expansion_smoke_enabled": bool(args.expansion_smoke),
        "h128_scaleup_enabled": bool(args.h128_scaleup),
        "sweep_kind": args.sweep_kind,
        "horizon_pairs": [f"{left}->{right}" for left, right in horizon_pairs],
        "substrate_families": substrate_families(args),
        "substrate_family_variant_count": len(substrate_family_variants(args)),
        "raw_state_sample_requested_jobs": int(args.raw_state_sample_jobs),
        "raw_state_sample_enabled": int(args.raw_state_sample_jobs > 0 and not args.fixture_smoke),
        "selected_edge_overlap_sample_jobs": int(args.selected_edge_overlap_sample_jobs),
    }
    write_json(args.out / status_filename(kind), status)
    raw_state_samples = raw_state_frontier_sample_rows(jobs, horizon_pairs, args) if not args.fixture_smoke else []
    status["raw_state_sample_rows"] = len(raw_state_samples)
    write_json(args.out / status_filename(kind), status)
    if args.fixture_smoke:
        rows: list[dict[str, object]] = []
        errors: list[dict[str, object]] = []
        checkpoints = [checkpoint_row(status, started, 0, 0)]
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "fixture_smoke_completed"
        matrices = build_fixture_matrices()
    else:
        rows, errors, checkpoints = run_jobs(args, jobs, status, started)
        matrices = build_transport_matrices(rows, args)
    outputs = compute_outputs(matrices, rows, raw_state_samples, jobs, args)
    write_outputs(args.out, outputs, matrices, errors, checkpoints, status, started)


def handle_stop(_signum: int, _frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def install_signal_handlers() -> None:
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, handle_stop)


def substrate_families(args: argparse.Namespace) -> list[str]:
    families = [canonical_transition_energy_family(item.strip()) for item in str(args.substrate_families).split(",") if item.strip()]
    unknown = [family for family in families if family not in TRANSITION_ENERGY_FAMILIES]
    if unknown:
        raise ValueError(f"unknown substrate family/families: {', '.join(unknown)}")
    return families or [CONSTRAINT_TEMPLATE_CURRENT]


def substrate_family_variants(args: argparse.Namespace) -> list[dict[str, object]]:
    variants: list[dict[str, object]] = []
    characterization = run_kind(args) in {TRANSITION_ENERGY_CHARACTERIZATION, ASYMMETRY_LADDER, MAX_ENTROPY_PREFLIGHT}
    for family in substrate_families(args):
        if not characterization:
            variants.append(default_substrate_variant(family, args))
            continue
        if family == CONSTRAINT_TEMPLATE_CURRENT:
            variants.append({
                "substrate_family": family,
                "substrate_variant": "current_comparator",
                "variant_role": "constraint_template_comparator",
            })
        elif family == LOCALITY_ONLY:
            for token, value in roughness_variant_values(args):
                row = {
                    "substrate_family": family,
                    "substrate_variant": f"roughness_{token}",
                    "variant_role": "locality_roughness_sweep",
                }
                if value is not None:
                    row["transition_roughness_strength"] = value
                variants.append(row)
        elif family == SMOOTH_RANDOM_POTENTIAL:
            for smoothness in list_or_default(args.potential_smoothness_list, (0.25, 0.65, 0.90)):
                for beta in list_or_default(args.potential_beta_list, (0.25, 0.50, 1.00)):
                    variants.append({
                        "substrate_family": family,
                        "substrate_variant": f"smoothness_{float_label(smoothness)}__beta_{float_label(beta)}",
                        "variant_role": "smooth_potential_smoothness_beta_sweep",
                        "potential_smoothness": smoothness,
                        "potential_beta": beta,
                        "potential_scale": args.potential_scale,
                    })
        elif family == BUDGET_CONSERVATION:
            budget_kinds = string_list_or_default(args.budget_kinds, ("total_coordinate_mass", "symbol_histogram_distance", "hamming_weight_or_nonzero_count"))
            for budget_kind in budget_kinds:
                for weight in list_or_default(args.budget_weights, (0.25, 1.00, 2.00)):
                    variants.append({
                        "substrate_family": family,
                        "substrate_variant": f"budget_{safe_id(budget_kind)}__weight_{float_label(weight)}",
                        "variant_role": "budget_kind_weight_sweep",
                        "budget_kind": budget_kind,
                        "budget_weight": weight,
                    })
        elif family == DIRECTIONAL_ASYMMETRY:
            for smoothness in list_or_default(args.asymmetry_field_smoothness_list, (0.65,)):
                for alpha in list_or_default(args.asymmetry_alpha_list, (0.25, 0.50, 1.00)):
                    variants.append({
                        "substrate_family": family,
                        "substrate_variant": f"alpha_{float_label(alpha)}__smoothness_{float_label(smoothness)}",
                        "variant_role": "directional_asymmetry_alpha_smoothness_sweep",
                        "asymmetry_alpha": alpha,
                        "asymmetry_field_smoothness": smoothness,
                        "asymmetry_field_scale": args.asymmetry_field_scale,
                    })
        elif family == PRESERVATION_ASYMMETRY:
            invariant_kinds = string_list_or_default(args.budget_kinds, ("total_coordinate_mass", "symbol_histogram_distance", "hamming_weight_or_nonzero_count"))
            for invariant_kind in invariant_kinds:
                for beta in list_or_default(args.macro_invariant_beta_list or args.budget_weights, (0.25, 1.00, 2.00)):
                    variants.append({
                        "substrate_family": family,
                        "substrate_variant": f"invariant_{safe_id(invariant_kind)}__beta_{float_label(beta)}",
                        "variant_role": "preservation_asymmetry_invariant_beta_sweep",
                        "budget_kind": invariant_kind,
                        "budget_weight": beta,
                        "macro_invariant_kind": invariant_kind,
                        "macro_invariant_beta": beta,
                    })
        elif family == COMBINED_ASYMMETRY:
            invariant_kinds = string_list_or_default(args.budget_kinds, ("hamming_weight_or_nonzero_count", "total_coordinate_mass"))
            for invariant_kind in invariant_kinds:
                for alpha, beta in combined_alpha_beta_pairs(args):
                    variants.append({
                        "substrate_family": family,
                        "substrate_variant": f"alpha_{float_label(alpha)}__beta_{float_label(beta)}__invariant_{safe_id(invariant_kind)}__smoothness_{float_label(args.asymmetry_field_smoothness)}",
                        "variant_role": "combined_asymmetry_sparse_alpha_beta_sweep",
                        "asymmetry_alpha": alpha,
                        "asymmetry_field_smoothness": args.asymmetry_field_smoothness,
                        "asymmetry_field_scale": args.asymmetry_field_scale,
                        "budget_kind": invariant_kind,
                        "budget_weight": beta,
                        "macro_invariant_kind": invariant_kind,
                        "macro_invariant_beta": beta,
                        "alpha_beta_pair": f"{float_label(alpha)}:{float_label(beta)}",
                    })
        elif family == MAX_ENTROPY_LOCAL:
            invariant_kinds = string_list_or_default(args.budget_kinds, ("symbol_histogram_distance",))
            for invariant_kind in invariant_kinds:
                for beta in equivalent_beta_targets(args):
                    variants.append({
                        "substrate_family": family,
                        "substrate_variant": f"equivalent_beta_{float_label(beta)}__invariant_{safe_id(invariant_kind)}",
                        "variant_role": "max_entropy_local_beta_axis_comparator",
                        "budget_kind": invariant_kind,
                        "macro_invariant_kind": invariant_kind,
                        "budget_weight": beta,
                        "macro_invariant_beta": beta,
                        "equivalent_beta_target": beta,
                        "max_entropy_sampler_draws": args.max_entropy_sampler_draws,
                        "max_entropy_delta_match_error_max": args.max_entropy_delta_match_error_max,
                    })
        elif family == MAX_ENTROPY_MACRO_INVARIANT:
            invariant_kinds = string_list_or_default(args.budget_kinds, ("symbol_histogram_distance",))
            for invariant_kind in invariant_kinds:
                for beta in equivalent_beta_targets(args):
                    variants.append({
                        "substrate_family": family,
                        "substrate_variant": f"equivalent_beta_{float_label(beta)}__invariant_{safe_id(invariant_kind)}",
                        "variant_role": "max_entropy_macro_invariant_delta_marginal_sweep",
                        "budget_kind": invariant_kind,
                        "macro_invariant_kind": invariant_kind,
                        "budget_weight": beta,
                        "macro_invariant_beta": beta,
                        "equivalent_beta_target": beta,
                        "max_entropy_sampler_draws": args.max_entropy_sampler_draws,
                        "max_entropy_delta_match_error_max": args.max_entropy_delta_match_error_max,
                    })
    return variants


def default_substrate_variant(family: str, args: argparse.Namespace) -> dict[str, object]:
    row: dict[str, object] = {
        "substrate_family": family,
        "substrate_variant": "default",
        "variant_role": "single_setting",
    }
    if family == SMOOTH_RANDOM_POTENTIAL:
        row.update({
            "potential_beta": args.potential_beta,
            "potential_smoothness": args.potential_smoothness,
            "potential_scale": args.potential_scale,
        })
    if family == BUDGET_CONSERVATION:
        row.update({
            "budget_kind": args.budget_kind,
            "budget_weight": args.budget_weight,
        })
    if family == DIRECTIONAL_ASYMMETRY:
        row.update({
            "asymmetry_alpha": args.asymmetry_alpha,
            "asymmetry_field_smoothness": args.asymmetry_field_smoothness,
            "asymmetry_field_scale": args.asymmetry_field_scale,
        })
    if family == PRESERVATION_ASYMMETRY:
        beta = macro_invariant_beta_default(args)
        row.update({
            "budget_kind": args.budget_kind,
            "budget_weight": beta,
            "macro_invariant_kind": args.budget_kind,
            "macro_invariant_beta": beta,
        })
    if family == COMBINED_ASYMMETRY:
        beta = macro_invariant_beta_default(args)
        row.update({
            "asymmetry_alpha": args.asymmetry_alpha,
            "asymmetry_field_smoothness": args.asymmetry_field_smoothness,
            "asymmetry_field_scale": args.asymmetry_field_scale,
            "budget_kind": args.budget_kind,
            "budget_weight": beta,
            "macro_invariant_kind": args.budget_kind,
            "macro_invariant_beta": beta,
            "alpha_beta_pair": f"{float_label(args.asymmetry_alpha)}:{float_label(beta)}",
        })
    if family in MAX_ENTROPY_FAMILIES:
        beta = equivalent_beta_targets(args)[0]
        row.update({
            "budget_kind": args.budget_kind,
            "budget_weight": beta,
            "macro_invariant_kind": args.budget_kind,
            "macro_invariant_beta": beta,
            "equivalent_beta_target": beta,
            "max_entropy_sampler_draws": args.max_entropy_sampler_draws,
            "max_entropy_delta_match_error_max": args.max_entropy_delta_match_error_max,
        })
    if args.transition_roughness_strength >= 0:
        row["transition_roughness_strength"] = args.transition_roughness_strength
    return row


def roughness_variant_values(args: argparse.Namespace) -> list[tuple[str, float | None]]:
    raw = str(args.locality_roughness_strengths or "").strip()
    tokens = [item.strip() for item in raw.split(",") if item.strip()] if raw else ["low", "current", "high"]
    values: list[tuple[str, float | None]] = []
    for token in tokens:
        lowered = token.lower()
        if lowered == "current":
            values.append(("current", None))
        elif lowered == "low":
            values.append(("low", 0.0025))
        elif lowered == "high":
            values.append(("high", 0.05))
        else:
            value = float(token)
            values.append((float_label(value), value))
    return values


def list_or_default(raw: str, default: tuple[float, ...]) -> tuple[float, ...]:
    values = parse_float_list(raw) if str(raw or "").strip() else tuple()
    return values or default


def string_list_or_default(raw: str, default: tuple[str, ...]) -> tuple[str, ...]:
    values = tuple(item.strip() for item in str(raw or "").split(",") if item.strip())
    return values or default


def macro_invariant_beta_default(args: argparse.Namespace) -> float:
    value = getattr(args, "macro_invariant_beta", None)
    return float(value) if value is not None else float(args.budget_weight)


def equivalent_beta_targets(args: argparse.Namespace) -> tuple[float, ...]:
    return list_or_default(args.equivalent_beta_target_list or args.macro_invariant_beta_list, (0.05, 0.10))


def combined_alpha_beta_pairs(args: argparse.Namespace) -> tuple[tuple[float, float], ...]:
    raw = str(getattr(args, "combined_alpha_beta_pairs", "") or "").strip()
    if raw:
        pairs: list[tuple[float, float]] = []
        for token in raw.split(","):
            value = token.strip()
            if not value:
                continue
            if ":" in value:
                left, right = value.split(":", 1)
            elif "/" in value:
                left, right = value.split("/", 1)
            else:
                raise ValueError(f"combined alpha/beta pair must use ':' or '/': {value}")
            pairs.append((float(left.strip()), float(right.strip())))
        return tuple(pairs)
    return (
        (0.25, 0.25),
        (0.25, 1.00),
        (0.50, 0.25),
        (0.50, 1.00),
        (1.00, 1.00),
        (0.50, 2.00),
    )


def float_label(value: float) -> str:
    return f"{float(value):g}".replace("-", "m").replace(".", "p")


def safe_id(value: object) -> str:
    return "".join(char if char.isalnum() else "_" for char in str(value)).strip("_")


def expand_jobs_for_substrate_families(jobs: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    variants = substrate_family_variants(args)
    if len(variants) == 1 and variants[0].get("substrate_family") == CONSTRAINT_TEMPLATE_CURRENT:
        for job in jobs:
            job["substrate_family"] = CONSTRAINT_TEMPLATE_CURRENT
            job["substrate_variant"] = variants[0].get("substrate_variant", "default")
        return jobs
    expanded: list[dict[str, object]] = []
    for variant in variants:
        family = str(variant["substrate_family"])
        variant_id = str(variant["substrate_variant"])
        for job in jobs:
            item = dict(job)
            original_condition = str(item.get("condition_id", ""))
            original_job_id = str(item.get("job_id", ""))
            item["substrate_family"] = family
            item["substrate_variant"] = variant_id
            item["substrate_base_condition_id"] = original_condition
            item["substrate_base_job_id"] = original_job_id
            item["condition_id"] = f"{family}::{variant_id}::{original_condition}"
            item["job_id"] = f"{family}::{variant_id}::{item.get('job_id', '')}"
            item["transition_energy_family"] = family
            item["transition_energy_form"] = transition_energy_form_label(family)
            item["potential_beta"] = variant.get("potential_beta", args.potential_beta)
            item["potential_seed"] = int(item.get("seed", 0)) + 71_003
            item["potential_smoothness"] = variant.get("potential_smoothness", args.potential_smoothness)
            item["potential_scale"] = variant.get("potential_scale", args.potential_scale)
            item["budget_kind"] = variant.get("budget_kind", args.budget_kind)
            item["budget_weight"] = variant.get("budget_weight", args.budget_weight)
            item["macro_invariant_kind"] = variant.get("macro_invariant_kind", item["budget_kind"])
            item["macro_invariant_beta"] = variant.get("macro_invariant_beta", macro_invariant_beta_default(args))
            item["equivalent_beta_target"] = variant.get("equivalent_beta_target", item["macro_invariant_beta"])
            item["max_entropy_sampler_draws"] = variant.get("max_entropy_sampler_draws", args.max_entropy_sampler_draws)
            item["max_entropy_delta_match_error_max"] = variant.get("max_entropy_delta_match_error_max", args.max_entropy_delta_match_error_max)
            item["asymmetry_alpha"] = variant.get("asymmetry_alpha", args.asymmetry_alpha)
            item["asymmetry_field_seed"] = int(item.get("seed", 0)) + 73_001
            item["asymmetry_field_smoothness"] = variant.get("asymmetry_field_smoothness", args.asymmetry_field_smoothness)
            item["asymmetry_field_scale"] = variant.get("asymmetry_field_scale", args.asymmetry_field_scale)
            item["alpha_beta_pair"] = variant.get("alpha_beta_pair", "")
            if "transition_roughness_strength" in variant:
                item["transition_roughness_strength"] = variant["transition_roughness_strength"]
            elif args.transition_roughness_strength >= 0:
                item["transition_roughness_strength"] = args.transition_roughness_strength
            expanded.append(item)
    return expanded


def transition_energy_form_label(family: str) -> str:
    if family == LOCALITY_ONLY:
        return "hamming_distance_plus_seeded_roughness"
    if family == SMOOTH_RANDOM_POTENTIAL:
        return "hamming_distance_plus_beta_potential_delta_plus_seeded_roughness"
    if family == BUDGET_CONSERVATION:
        return "hamming_distance_plus_budget_delta_penalty_plus_seeded_roughness"
    if family == DIRECTIONAL_ASYMMETRY:
        return "hamming_distance_plus_alpha_directional_asymmetry_delta_plus_seeded_roughness"
    if family == PRESERVATION_ASYMMETRY:
        return "hamming_distance_plus_beta_macro_invariant_delta_penalty_plus_seeded_roughness"
    if family == COMBINED_ASYMMETRY:
        return "hamming_distance_plus_alpha_directional_delta_plus_beta_macro_invariant_delta_plus_seeded_roughness"
    if family == MAX_ENTROPY_LOCAL:
        return "maximum_entropy_sample_over_local_candidate_edges_with_exact_out_degree"
    if family == MAX_ENTROPY_MACRO_INVARIANT:
        return "maximum_entropy_sample_over_local_edges_matched_to_macro_invariant_delta_marginal"
    return "current_constraint_template_scored_relation"


def raw_state_frontier_sample_rows(
    jobs: list[dict[str, object]],
    horizon_pairs: tuple[tuple[int, int], ...],
    args: argparse.Namespace,
) -> list[dict[str, object]]:
    if args.raw_state_sample_jobs <= 0:
        return []
    horizons = sorted({horizon for pair in horizon_pairs for horizon in pair})
    selected = jobs[: max(0, args.raw_state_sample_jobs)]
    rows: list[dict[str, object]] = []
    for job in selected:
        if STOP_REQUESTED:
            break
        try:
            seed = int(job["seed"])
            params = job["params"]
            baseline = generate_job_baseline_system(job, params, seed)  # type: ignore[arg-type]
            system = make_stage_b2_control_system(baseline, job, seed, params)  # type: ignore[arg-type]
            starts = [system.states[(seed + i * 17) % len(system.states)] for i in range(min(int(job["start_samples"]), max(1, args.raw_state_sample_starts)))]
            state_index = {state: index for index, state in enumerate(system.states)}
            for start_index, start in enumerate(starts):
                if STOP_REQUESTED:
                    break
                for horizon in horizons:
                    if STOP_REQUESTED:
                        break
                    frontier = sorted(exact_frontier(system, start, horizon))
                    frontier_size = len(frontier)
                    for rank, state in enumerate(frontier[: max(1, args.raw_state_sample_states)], start=1):
                        state_tuple = tuple(state) if isinstance(state, tuple) else (state,)
                        row = {
                            "raw_state_view": "exact_frontier_sample",
                            "raw_state_sample_status": "ok",
                            "condition_id": job.get("condition_id", ""),
                            "substrate_family": job.get("substrate_family", CONSTRAINT_TEMPLATE_CURRENT),
                            "actual_control_name": job.get("actual_control_name", ""),
                            "mechanism_control_strength": job.get("mechanism_control_strength", ""),
                            "probe_key": job.get("probe_key", ""),
                            "flow_mode": "raw_exact_frontier",
                            "job_id": job.get("job_id", ""),
                            "group_id": job.get("group_id", ""),
                            "seed": seed,
                            "baseline_system_id": baseline.system_id,
                            "control_system_id": system.system_id,
                            "start_index": start_index,
                            "start_state": raw_state_id(start),
                            "H": horizon,
                            "state_id": raw_state_id(state),
                            "state_index": state_index.get(state, ""),
                            "frontier_rank": rank,
                            "frontier_size": frontier_size,
                            "frontier_sample_limit": args.raw_state_sample_states,
                            "frontier_sample_truncated": int(frontier_size > args.raw_state_sample_states),
                            "state_presence": 1,
                        }
                        for coord_index, value in enumerate(state_tuple):
                            row[f"state_coord_{coord_index}"] = value
                        rows.append(row)
        except Exception as exc:  # noqa: BLE001
            rows.append({
                "condition_id": job.get("condition_id", ""),
                "job_id": job.get("job_id", ""),
                "raw_state_sample_status": "error",
                "error": repr(exc),
            })
    return rows


def raw_state_id(state: object) -> str:
    if isinstance(state, tuple):
        return "(" + ",".join(str(part) for part in state) + ")"
    return str(state)


def run_jobs(
    args: argparse.Namespace,
    jobs: list[dict[str, object]],
    status: dict[str, object],
    started: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    pending = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []
    last_checkpoint = 0
    futures = {}
    cancelled_job_count = 0
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    try:
        while pending or futures:
            if STOP_REQUESTED:
                status["status"] = "PARTIAL_INTERRUPTED"
                status["finalization_reason"] = "signal_stop_requested"
                break
            remaining = args.max_runtime_seconds - (time.perf_counter() - started)
            if remaining <= args.shutdown_cushion_seconds:
                status["status"] = "PARTIAL_TIME_LIMIT_REACHED"
                status["finalization_reason"] = "shutdown_cushion_reached"
                break
            while pending and len(futures) < max(1, args.workers):
                batch = pending.pop(0)
                futures[executor.submit(run_batch, batch, args.max_items_per_context)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            status["pending_jobs_remaining"] = sum(len(batch) for batch in pending) + sum(len(batch) for batch in futures.values())
            done, _pending_futures = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch = futures.pop(future)
                try:
                    _contexts, metric_rows, batch_errors, completed = future.result()
                except Exception as exc:  # noqa: BLE001
                    metric_rows = []
                    batch_errors = [{"job_id": ",".join(str(job.get("job_id", "")) for job in batch), "error": repr(exc)}]
                    completed = len(batch)
                rows.extend(metric_rows)
                errors.extend(batch_errors)
                status["jobs_completed"] = int(status["jobs_completed"]) + completed
                status["pending_jobs_remaining"] = sum(len(batch) for batch in pending) + sum(len(batch) for batch in futures.values())
                if int(status["jobs_completed"]) - last_checkpoint >= max(1, args.checkpoint_every_jobs):
                    checkpoints.append(checkpoint_row(status, started, len(rows), len(errors)))
                    last_checkpoint = int(status["jobs_completed"])
                    write_partial(args.out, status, started, checkpoints, errors)
    finally:
        if futures:
            cancelled_job_count = sum(len(batch) for batch in futures.values())
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = cancelled_job_count
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = sum(len(batch) for batch in pending) + cancelled_job_count
    if status.get("status") == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    checkpoints.append(checkpoint_row(status, started, len(rows), len(errors)))
    write_partial(args.out, status, started, checkpoints, errors)
    return rows, errors, checkpoints


def checkpoint_row(status: dict[str, object], started: float, row_count: int, error_count: int) -> dict[str, object]:
    return {
        "timestamp_utc": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "status": status.get("status", ""),
        "jobs_submitted": status.get("jobs_submitted", 0),
        "jobs_completed": status.get("jobs_completed", 0),
        "jobs_cancelled": status.get("jobs_cancelled", 0),
        "pending_jobs_remaining": status.get("pending_jobs_remaining", 0),
        "transport_metric_rows": row_count,
        "errors": error_count,
    }


def write_partial(out_dir: Path, status: dict[str, object], started: float, checkpoints: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    kind = status_run_kind(status)
    write_json(out_dir / status_filename(kind), status)
    write_csv(out_dir / progress_filename(kind), checkpoints)
    write_csv(out_dir / errors_filename(kind), errors)


def build_transport_matrices(rows: list[dict[str, object]], args: argparse.Namespace) -> list[TransportMatrix]:
    accumulators: dict[TransportKey, Counter[tuple[str, str]]] = defaultdict(Counter)
    context_counts: Counter[TransportKey] = Counter()
    row_counts: dict[TransportKey, Counter[str]] = defaultdict(Counter)
    col_counts: dict[TransportKey, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if row.get("row_kind") not in {"baseline", "mechanism_control"}:
            continue
        try:
            ha = int(float_or_zero(row.get("H_a")))
            hb = int(float_or_zero(row.get("H_b")))
        except ValueError:
            continue
        key = TransportKey(
            condition_id=str(row.get("condition_id", "")),
            actual_control_name=str(row.get("actual_control_name", "")),
            mechanism_control_strength=float_or_zero(row.get("mechanism_control_strength")),
            probe_key=str(row.get("probe_key", "")),
            flow_mode=str(row.get("flow_mode", "")),
            source_horizon_band=horizon_point_band(ha),
            target_horizon_band=horizon_point_band(hb),
            H_a=ha,
            H_b=hb,
        )
        transitions = parse_transition_distribution(row.get("transition_distribution_json", "{}"))
        if not transitions:
            continue
        context_counts[key] += 1
        for (left, right), count in transitions.items():
            accumulators[key][(left, right)] += count
            row_counts[key][left] += count
            col_counts[key][right] += count
    matrices: list[TransportMatrix] = []
    for key, counts in accumulators.items():
        retained_rows = [item for item, count in row_counts[key].most_common(args.max_items_per_side) if count >= args.min_item_count]
        retained_cols = [item for item, count in col_counts[key].most_common(args.max_items_per_side) if count >= args.min_item_count]
        if len(retained_rows) < 2 or len(retained_cols) < 2:
            continue
        row_index = {item: index for index, item in enumerate(retained_rows)}
        col_index = {item: index for index, item in enumerate(retained_cols)}
        matrix = np.zeros((len(retained_rows), len(retained_cols)), dtype=np.float64)
        total_mass = float(sum(counts.values()))
        retained_mass = 0.0
        for (left, right), count in counts.items():
            if left not in row_index or right not in col_index:
                continue
            matrix[row_index[left], col_index[right]] += float(count)
            retained_mass += float(count)
        if retained_mass <= 0:
            continue
        left_vectors, singular_values, right_t = np.linalg.svd(matrix, full_matrices=False)
        matrices.append(TransportMatrix(
            key=key,
            matrix_id=transport_matrix_id(key),
            row_items=retained_rows,
            column_items=retained_cols,
            matrix=matrix,
            transport_context_count=context_counts[key],
            transport_mass_total=total_mass,
            retained_transport_mass=retained_mass,
            dropped_transport_mass=max(0.0, total_mass - retained_mass),
            raw_row_item_count=len(row_counts[key]),
            raw_column_item_count=len(col_counts[key]),
            singular_values=singular_values,
            left_vectors=left_vectors,
            right_vectors=right_t.T,
        ))
    return matrices


def parse_transition_distribution(raw: object) -> Counter[tuple[str, str]]:
    out: Counter[tuple[str, str]] = Counter()
    try:
        payload = json.loads(str(raw))
    except json.JSONDecodeError:
        return out
    if not isinstance(payload, dict):
        return out
    for key, value in payload.items():
        if "->" not in str(key):
            continue
        left, right = str(key).split("->", 1)
        out[(left, right)] += int(float_or_zero(value))
    return out


def build_fixture_matrices() -> list[TransportMatrix]:
    row_items = ["route_A0", "route_A1", "route_B0", "route_B1"]
    column_items = ["dest_A0", "dest_A1", "dest_B0", "dest_B1"]
    corridor_rows = ["corridor_open", "corridor_side", "corridor_reentry", "corridor_sink"]
    corridor_cols = ["stable_open", "stable_side", "stable_reentry", "stable_sink"]
    trap_rows = ["trap_entry", "trap_loop", "trap_exit", "trap_recovery"]
    trap_cols = ["downstream_entry", "downstream_loop", "downstream_exit", "downstream_recovery"]
    response_rows = [f"r{i}" for i in range(8)]
    response_cols = [f"c{i}" for i in range(8)]
    fixtures = [
        (
            TransportKey("fixture_block_transport_signal", BASELINE_CONTROL, 0.0, "fixture_block_probe", "fixture_flow", "middle", "middle", 4, 16),
            row_items,
            column_items,
            np.asarray([
                [12, 8, 0, 0],
                [8, 12, 0, 0],
                [0, 0, 12, 8],
                [0, 0, 8, 12],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_marginal_fakeout", BASELINE_CONTROL, 0.0, "fixture_fakeout_probe", "fixture_flow", "middle", "middle", 4, 16),
            row_items,
            column_items,
            np.asarray([
                [16, 12, 8, 4],
                [12, 9, 6, 3],
                [8, 6, 4, 2],
                [4, 3, 2, 1],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_corridor_baseline", BASELINE_CONTROL, 0.0, "fixture_corridor_probe", "fixture_flow", "middle", "middle", 4, 16),
            corridor_rows,
            corridor_cols,
            np.asarray([
                [18, 2, 1, 0],
                [2, 15, 2, 1],
                [1, 2, 14, 2],
                [0, 1, 2, 12],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_corridor_stable_response", "fixture_nonlethal_corridor_jitter", 0.05, "fixture_corridor_probe", "fixture_flow", "middle", "middle", 4, 16),
            corridor_rows,
            corridor_cols,
            np.asarray([
                [18, 2, 1, 0],
                [2, 14, 3, 1],
                [1, 2, 14, 2],
                [0, 1, 2, 12],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_trap_baseline", BASELINE_CONTROL, 0.0, "fixture_trap_probe", "fixture_flow", "middle", "middle", 4, 16),
            trap_rows,
            trap_cols,
            np.asarray([
                [16, 3, 1, 0],
                [3, 18, 2, 0],
                [1, 2, 12, 3],
                [0, 0, 3, 10],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_trap_collapse_response", "fixture_nonlethal_trap_collapse", 0.80, "fixture_trap_probe", "fixture_flow", "middle", "middle", 4, 16),
            trap_rows,
            trap_cols,
            np.asarray([
                [3.2, 0.6, 0.2, 0],
                [0.6, 3.6, 0.4, 0],
                [0.2, 0.4, 2.4, 0.6],
                [0, 0, 0.6, 2.0],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_amplified_aligned_baseline", BASELINE_CONTROL, 0.0, "fixture_amplified_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [12, 2, 1, 0, 0, 0, 0, 0],
                [2, 10, 1, 0, 0, 0, 0, 0],
                [1, 1, 8, 1, 0, 0, 0, 0],
                [0, 0, 1, 6, 1, 0, 0, 0],
                [0, 0, 0, 1, 5, 1, 0, 0],
                [0, 0, 0, 0, 1, 4, 1, 0],
                [0, 0, 0, 0, 0, 1, 3, 1],
                [0, 0, 0, 0, 0, 0, 1, 2],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_amplified_aligned_response", "fixture_nonlethal_amplify", 0.20, "fixture_amplified_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [15.6, 2.6, 1.3, 0, 0, 0, 0, 0],
                [2.6, 13.0, 1.3, 0, 0, 0, 0, 0],
                [1.3, 1.3, 10.4, 1.3, 0, 0, 0, 0],
                [0, 0, 1.3, 7.8, 1.3, 0, 0, 0],
                [0, 0, 0, 1.3, 6.5, 1.3, 0, 0],
                [0, 0, 0, 0, 1.3, 5.2, 1.3, 0],
                [0, 0, 0, 0, 0, 1.3, 3.9, 1.3],
                [0, 0, 0, 0, 0, 0, 1.3, 2.6],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_weakened_baseline", BASELINE_CONTROL, 0.0, "fixture_weakened_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [12, 2, 1, 0, 0, 0, 0, 0],
                [2, 10, 1, 0, 0, 0, 0, 0],
                [1, 1, 8, 1, 0, 0, 0, 0],
                [0, 0, 1, 6, 1, 0, 0, 0],
                [0, 0, 0, 1, 5, 1, 0, 0],
                [0, 0, 0, 0, 1, 4, 1, 0],
                [0, 0, 0, 0, 0, 1, 3, 1],
                [0, 0, 0, 0, 0, 0, 1, 2],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_weakened_response", "fixture_nonlethal_weaken", 0.30, "fixture_weakened_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [8.4, 1.4, 0.7, 0, 0, 0, 0, 0],
                [1.4, 7.0, 0.7, 0, 0, 0, 0, 0],
                [0.7, 0.7, 5.6, 0.7, 0, 0, 0, 0],
                [0, 0, 0.7, 4.2, 0.7, 0, 0, 0],
                [0, 0, 0, 0.7, 3.5, 0.7, 0, 0],
                [0, 0, 0, 0, 0.7, 2.8, 0.7, 0],
                [0, 0, 0, 0, 0, 0.7, 2.1, 0.7],
                [0, 0, 0, 0, 0, 0, 0.7, 1.4],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_rerouted_baseline", BASELINE_CONTROL, 0.0, "fixture_rerouted_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [40, 1, 0, 0, 0, 0, 0, 0],
                [1, 34, 1, 0, 0, 0, 0, 0],
                [0, 1, 28, 1, 0, 0, 0, 0],
                [0, 0, 1, 22, 1, 0, 0, 0],
                [0, 0, 0, 1, 16, 1, 0, 0],
                [0, 0, 0, 0, 1, 10, 1, 0],
                [0, 0, 0, 0, 0, 1, 6, 1],
                [0, 0, 0, 0, 0, 0, 1, 4],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_rerouted_response", "fixture_nonlethal_reroute", 0.20, "fixture_rerouted_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [0, 0, 0, 0, 0, 0, 1, 40],
                [0, 0, 0, 0, 0, 1, 34, 1],
                [0, 0, 0, 0, 1, 28, 1, 0],
                [0, 0, 0, 1, 22, 1, 0, 0],
                [0, 0, 1, 16, 1, 0, 0, 0],
                [0, 1, 10, 1, 0, 0, 0, 0],
                [1, 6, 1, 0, 0, 0, 0, 0],
                [4, 1, 0, 0, 0, 0, 0, 0],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_reopens_baseline", BASELINE_CONTROL, 0.0, "fixture_reopens_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [44, 0, 0, 0, 0, 0, 0, 0],
                [0, 12, 0, 0, 0, 0, 0, 0],
                [0, 0, 8, 0, 0, 0, 0, 0],
                [0, 0, 0, 4, 0, 0, 0, 0],
                [0, 0, 0, 0, 2, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_reopens_response", "fixture_nonlethal_reopens", 0.20, "fixture_reopens_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [8, 3, 3, 3, 3, 2, 2, 2],
                [3, 8, 3, 3, 3, 2, 2, 2],
                [3, 3, 8, 3, 3, 2, 2, 2],
                [3, 3, 3, 8, 3, 2, 2, 2],
                [3, 3, 3, 3, 8, 2, 2, 2],
                [2, 2, 2, 2, 2, 6, 2, 2],
                [2, 2, 2, 2, 2, 2, 6, 2],
                [2, 2, 2, 2, 2, 2, 2, 6],
            ], dtype=np.float64) * 1.3,
        ),
    ]
    return [fixture_transport_matrix(key, rows, cols, values) for key, rows, cols, values in fixtures]


def fixture_transport_matrix(key: TransportKey, rows: list[str], cols: list[str], values: np.ndarray) -> TransportMatrix:
    left_vectors, singular_values, right_t = np.linalg.svd(values, full_matrices=False)
    total = float(np.sum(values))
    return TransportMatrix(
        key=key,
        matrix_id=transport_matrix_id(key),
        row_items=list(rows),
        column_items=list(cols),
        matrix=values,
        transport_context_count=1,
        transport_mass_total=total,
        retained_transport_mass=total,
        dropped_transport_mass=0.0,
        raw_row_item_count=len(rows),
        raw_column_item_count=len(cols),
        singular_values=singular_values,
        left_vectors=left_vectors,
        right_vectors=right_t.T,
    )


def compute_outputs(
    matrices: list[TransportMatrix],
    rows: list[dict[str, object]],
    raw_state_samples: list[dict[str, object]],
    jobs: list[dict[str, object]],
    args: argparse.Namespace,
) -> dict[str, list[dict[str, object]]]:
    manifest = matrix_manifest_rows(matrices)
    matrix_entries = matrix_entry_rows(matrices, args)
    substrate_manifest = substrate_family_manifest_rows(matrices, args)
    substrate_variant_manifest = substrate_family_variant_manifest_rows(matrices, args)
    transition_family_summary = transition_energy_family_summary_rows(args)
    transition_parameter_summary = transition_energy_parameter_summary_rows(args)
    substrate_capacity = substrate_capacity_by_family_rows(matrices)
    substrate_capacity_variant = substrate_capacity_by_family_variant_rows(matrices)
    substrate_generation = substrate_generation_diagnostics_rows(rows)
    row_items = row_item_manifest_rows(matrices)
    column_items = column_item_manifest_rows(matrices)
    coverage = coverage_rows(matrices)
    summary = matrix_summary_rows(matrices, args)
    svd = svd_rows(matrices, args)
    participation = participation_rows(matrices, args)
    entropy = entropy_rows(matrices)
    null_anatomy = detector_null_anatomy_rows(matrices, args)
    null_summary = detector_null_summary_rows(null_anatomy, args)
    preliminary_null_gates = detector_null_gate_rows(null_summary, matrices, args, [])
    perturb_manifest, response_summary, response_classification = perturbation_response_rows(matrices, preliminary_null_gates, args)
    fixture_results = fixture_result_rows(null_anatomy, response_classification)
    response_fixture_summary: list[dict[str, object]] = []
    if (args.h128_scaleup or args.sweep_kind) and not args.fixture_smoke:
        fixture_matrices = build_fixture_matrices()
        fixture_null_anatomy = detector_null_anatomy_rows(fixture_matrices, args)
        fixture_null_summary = detector_null_summary_rows(fixture_null_anatomy, args)
        fixture_gates = detector_null_gate_rows(fixture_null_summary, fixture_matrices, args, [])
        _fixture_manifest, fixture_response_summary, fixture_response_classification = perturbation_response_rows(fixture_matrices, fixture_gates, args)
        fixture_results = fixture_result_rows(fixture_null_anatomy, fixture_response_classification)
        response_fixture_summary = fixture_response_classification
    elif args.fixture_smoke:
        response_fixture_summary = response_classification
    null_gates = detector_null_gate_rows(null_summary, matrices, args, fixture_results)
    subspace_alignment = horizon_pair_alignment_rows(matrices, args)
    matched_marginal = matched_marginal_summary_rows(null_anatomy, args)
    saturation = terminal_saturation_rows(matrices)
    saturation_by_horizon_pair = saturation_by_horizon_pair_rows(saturation)
    response_flags = response_flag_rows(response_classification, saturation)
    response_by_strength_horizon = response_class_by_strength_and_horizon_rows(response_classification)
    threshold_table = horizon_response_threshold_rows(response_classification, saturation)
    response_diversity = response_diversity_rows(response_classification, saturation)
    viscosity = transport_viscosity_rows(response_classification, response_diversity, saturation)
    context_recommendation = context_recommendation_rows(summary, matched_marginal, response_classification)
    by_substrate = horizon_transport_by_substrate_family_rows(context_recommendation)
    by_substrate_variant = horizon_transport_by_substrate_family_variant_rows(context_recommendation)
    response_by_substrate = response_by_group_rows(response_classification, ("substrate_family",))
    response_by_substrate_variant = response_by_group_rows(response_classification, ("substrate_family", "substrate_variant"))
    response_by_budget = response_by_group_rows([row for row in response_classification if row.get("budget_kind")], ("budget_kind",))
    response_by_potential_smoothness = response_by_group_rows([row for row in response_classification if row.get("potential_smoothness") not in (None, "")], ("potential_smoothness",))
    response_by_potential_beta = response_by_group_rows([row for row in response_classification if row.get("potential_beta") not in (None, "")], ("potential_beta",))
    response_by_macro_invariant_kind = response_by_group_rows([row for row in response_classification if row.get("macro_invariant_kind")], ("macro_invariant_kind",))
    response_by_macro_invariant_beta = response_by_group_rows([row for row in response_classification if row.get("macro_invariant_beta") not in (None, "")], ("macro_invariant_beta",))
    selected_edge_overlap_by_beta = selected_edge_overlap_by_beta_rows(jobs, args)
    max_entropy_constraint_manifest = max_entropy_constraint_manifest_rows(rows)
    max_entropy_marginal_match_summary = max_entropy_marginal_match_summary_rows(rows)
    max_entropy_sampler_diagnostics = max_entropy_sampler_diagnostics_rows(rows)
    max_entropy_edge_match_to_calibration = max_entropy_edge_match_to_calibration_rows(jobs, args)
    response_by_max_entropy_family = response_by_group_rows([row for row in response_classification if row.get("substrate_family") in MAX_ENTROPY_FAMILIES], ("substrate_family",))
    response_by_equivalent_beta_target = response_by_group_rows([row for row in response_classification if row.get("equivalent_beta_target") not in (None, "")], ("equivalent_beta_target",))
    paired_baseline_availability_by_max_entropy_variant = paired_baseline_availability_by_max_entropy_variant_rows(response_classification)
    response_by_directional_alpha = response_by_group_rows([row for row in response_classification if row.get("asymmetry_alpha") not in (None, "")], ("asymmetry_alpha",))
    response_by_asymmetry_field_smoothness = response_by_group_rows([row for row in response_classification if row.get("asymmetry_field_smoothness") not in (None, "")], ("asymmetry_field_smoothness",))
    response_by_alpha_beta_pair = response_by_group_rows([row for row in response_classification if row.get("alpha_beta_pair")], ("alpha_beta_pair",))
    aligned_by_substrate = aligned_amplification_by_substrate_family_rows(response_classification)
    diversity_by_substrate = response_diversity_by_substrate_family_rows(response_diversity)
    diversity_by_substrate_variant = response_diversity_by_substrate_family_variant_rows(response_diversity)
    viscosity_by_substrate = transport_viscosity_by_substrate_family_rows(viscosity)
    viscosity_by_substrate_variant = transport_viscosity_by_substrate_family_variant_rows(viscosity)
    matched_by_substrate = matched_null_pass_by_substrate_family_rows(matched_marginal)
    matched_by_substrate_variant = matched_null_pass_by_substrate_family_variant_rows(matched_marginal)
    by_probe = aggregate_context_summary_rows(context_recommendation, ("probe_key",), "probe_key")
    by_flow_mode = aggregate_context_summary_rows(context_recommendation, ("flow_mode",), "flow_mode")
    by_horizon_pair = aggregate_context_summary_rows(context_recommendation, ("source_horizon_band", "target_horizon_band", "H_a", "H_b"), "horizon_pair")
    return {
        "manifest": manifest,
        "matrix_entries": matrix_entries,
        "raw_state_samples": raw_state_samples,
        "substrate_manifest": substrate_manifest,
        "substrate_variant_manifest": substrate_variant_manifest,
        "transition_family_summary": transition_family_summary,
        "transition_parameter_summary": transition_parameter_summary,
        "substrate_capacity": substrate_capacity,
        "substrate_capacity_variant": substrate_capacity_variant,
        "substrate_generation": substrate_generation,
        "row_items": row_items,
        "column_items": column_items,
        "coverage": coverage,
        "summary": summary,
        "svd": svd,
        "participation": participation,
        "entropy": entropy,
        "null_anatomy": null_anatomy,
        "null_summary": null_summary,
        "null_gates": null_gates,
        "matched_marginal": matched_marginal,
        "fixture_results": fixture_results,
        "perturb_manifest": perturb_manifest,
        "response_summary": response_summary,
        "response_classification": response_classification,
        "response_flags": response_flags,
        "response_by_strength_horizon": response_by_strength_horizon,
        "threshold_table": threshold_table,
        "response_diversity": response_diversity,
        "viscosity": viscosity,
        "saturation": saturation,
        "saturation_by_horizon_pair": saturation_by_horizon_pair,
        "response_fixture_summary": response_fixture_summary,
        "subspace_alignment": subspace_alignment,
        "by_probe": by_probe,
        "by_flow_mode": by_flow_mode,
        "by_horizon_pair": by_horizon_pair,
        "by_substrate": by_substrate,
        "by_substrate_variant": by_substrate_variant,
        "response_by_substrate": response_by_substrate,
        "response_by_substrate_variant": response_by_substrate_variant,
        "response_by_budget": response_by_budget,
        "response_by_potential_smoothness": response_by_potential_smoothness,
        "response_by_potential_beta": response_by_potential_beta,
        "response_by_macro_invariant_kind": response_by_macro_invariant_kind,
        "response_by_macro_invariant_beta": response_by_macro_invariant_beta,
        "selected_edge_overlap_by_beta": selected_edge_overlap_by_beta,
        "max_entropy_constraint_manifest": max_entropy_constraint_manifest,
        "max_entropy_marginal_match_summary": max_entropy_marginal_match_summary,
        "max_entropy_sampler_diagnostics": max_entropy_sampler_diagnostics,
        "max_entropy_edge_match_to_calibration": max_entropy_edge_match_to_calibration,
        "response_by_max_entropy_family": response_by_max_entropy_family,
        "response_by_equivalent_beta_target": response_by_equivalent_beta_target,
        "paired_baseline_availability_by_max_entropy_variant": paired_baseline_availability_by_max_entropy_variant,
        "response_by_directional_alpha": response_by_directional_alpha,
        "response_by_asymmetry_field_smoothness": response_by_asymmetry_field_smoothness,
        "response_by_alpha_beta_pair": response_by_alpha_beta_pair,
        "aligned_by_substrate": aligned_by_substrate,
        "diversity_by_substrate": diversity_by_substrate,
        "diversity_by_substrate_variant": diversity_by_substrate_variant,
        "viscosity_by_substrate": viscosity_by_substrate,
        "viscosity_by_substrate_variant": viscosity_by_substrate_variant,
        "matched_by_substrate": matched_by_substrate,
        "matched_by_substrate_variant": matched_by_substrate_variant,
        "context_recommendation": context_recommendation,
    }


def selected_edge_overlap_by_beta_rows(jobs: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    sample_limit = max(0, int(getattr(args, "selected_edge_overlap_sample_jobs", 0)))
    if sample_limit <= 0 or not jobs:
        return []
    by_group: dict[tuple[str, str, str, str, str], dict[float, dict[str, object]]] = defaultdict(dict)
    for job in jobs:
        family = canonical_transition_energy_family(str(job.get("substrate_family", "") or ""))
        if family not in {PRESERVATION_ASYMMETRY, COMBINED_ASYMMETRY}:
            continue
        invariant_kind = str(job.get("macro_invariant_kind", job.get("budget_kind", "")) or "")
        if not invariant_kind:
            continue
        beta = float_or_zero(job.get("macro_invariant_beta"))
        base_job_id = str(job.get("substrate_base_job_id", job.get("job_id", "")) or "")
        group_key = (
            family,
            invariant_kind,
            str(job.get("asymmetry_alpha", "")) if family == COMBINED_ASYMMETRY else "",
            str(job.get("asymmetry_field_smoothness", "")) if family == COMBINED_ASYMMETRY else "",
            base_job_id,
        )
        by_group[group_key].setdefault(beta, job)
    if not by_group:
        return []

    bucketed_keys: dict[tuple[str, str, str, str], list[tuple[str, str, str, str, str]]] = defaultdict(list)
    for key in sorted(by_group):
        bucketed_keys[key[:4]].append(key)
    selected_keys: list[tuple[str, str, str, str, str]] = []
    while len(selected_keys) < sample_limit and any(bucketed_keys.values()):
        for bucket in sorted(bucketed_keys):
            if len(selected_keys) >= sample_limit:
                break
            if bucketed_keys[bucket]:
                selected_keys.append(bucketed_keys[bucket].pop(0))

    observations: list[dict[str, object]] = []
    for key in selected_keys:
        beta_jobs = by_group[key]
        family, invariant_kind, alpha, smoothness, base_job_id = key
        reference_job = beta_jobs.get(0.0)
        synthetic_reference = 0
        if reference_job is None:
            reference_job = dict(beta_jobs[sorted(beta_jobs)[0]])
            reference_job["macro_invariant_beta"] = 0.0
            reference_job["budget_weight"] = 0.0
            synthetic_reference = 1
        try:
            reference_edges = selected_edge_set(reference_job)
        except Exception as exc:  # noqa: BLE001
            observations.append({
                "substrate_family": family,
                "macro_invariant_kind": invariant_kind,
                "macro_invariant_beta": "",
                "asymmetry_alpha": alpha,
                "asymmetry_field_smoothness": smoothness,
                "sample_status": "reference_error",
                "sample_error": repr(exc),
                "sample_count": 1,
                "synthetic_beta0_reference_count": synthetic_reference,
                "base_job_id": base_job_id,
            })
            continue
        for beta in sorted(beta_jobs):
            job = beta_jobs[beta]
            try:
                edges = selected_edge_set(job)
                intersection = len(reference_edges & edges)
                union = len(reference_edges | edges)
                reference_count = len(reference_edges)
                edge_count = len(edges)
                observations.append({
                    "substrate_family": family,
                    "macro_invariant_kind": invariant_kind,
                    "macro_invariant_beta": beta,
                    "asymmetry_alpha": alpha,
                    "asymmetry_field_smoothness": smoothness,
                    "sample_status": "ok",
                    "sample_error": "",
                    "edge_jaccard_vs_beta0": intersection / max(1, union),
                    "selected_edge_overlap_fraction_vs_beta0": intersection / max(1, reference_count),
                    "selected_edge_retention_fraction_vs_beta0": intersection / max(1, edge_count),
                    "selected_edge_symmetric_difference_fraction": (union - intersection) / max(1, union),
                    "edge_count_delta_vs_beta0": edge_count - reference_count,
                    "reference_edge_count": reference_count,
                    "edge_count": edge_count,
                    "sample_count": 1,
                    "synthetic_beta0_reference_count": synthetic_reference,
                    "base_job_id": base_job_id,
                })
            except Exception as exc:  # noqa: BLE001
                observations.append({
                    "substrate_family": family,
                    "macro_invariant_kind": invariant_kind,
                    "macro_invariant_beta": beta,
                    "asymmetry_alpha": alpha,
                    "asymmetry_field_smoothness": smoothness,
                    "sample_status": "target_error",
                    "sample_error": repr(exc),
                    "sample_count": 1,
                    "synthetic_beta0_reference_count": synthetic_reference,
                    "base_job_id": base_job_id,
                })
    return aggregate_selected_edge_overlap_observations(observations)


def selected_edge_set(job: dict[str, object]) -> set[tuple[object, object]]:
    params = job["params"]
    seed = int(job["seed"])
    system = generate_job_baseline_system(job, params, seed)  # type: ignore[arg-type]
    return {(source, target) for source, targets in system.edges.items() for target in targets}


def aggregate_selected_edge_overlap_observations(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(
            str(row.get("substrate_family", "")),
            str(row.get("macro_invariant_kind", "")),
            str(row.get("macro_invariant_beta", "")),
            str(row.get("asymmetry_alpha", "")),
            str(row.get("asymmetry_field_smoothness", "")),
        )].append(row)
    out: list[dict[str, object]] = []
    for key, items in sorted(groups.items(), key=lambda item: selected_edge_overlap_sort_key(item[0])):
        family, invariant_kind, beta, alpha, smoothness = key
        ok_items = [row for row in items if row.get("sample_status") == "ok"]
        jaccards = [float_or_zero(row.get("edge_jaccard_vs_beta0")) for row in ok_items]
        overlaps = [float_or_zero(row.get("selected_edge_overlap_fraction_vs_beta0")) for row in ok_items]
        retentions = [float_or_zero(row.get("selected_edge_retention_fraction_vs_beta0")) for row in ok_items]
        symdiffs = [float_or_zero(row.get("selected_edge_symmetric_difference_fraction")) for row in ok_items]
        edge_deltas = [float_or_zero(row.get("edge_count_delta_vs_beta0")) for row in ok_items]
        out.append({
            "substrate_family": family,
            "macro_invariant_kind": invariant_kind,
            "macro_invariant_beta": beta,
            "asymmetry_alpha": alpha,
            "asymmetry_field_smoothness": smoothness,
            "sample_count": len(items),
            "ok_sample_count": len(ok_items),
            "error_sample_count": len(items) - len(ok_items),
            "synthetic_beta0_reference_count": sum(int(float_or_zero(row.get("synthetic_beta0_reference_count"))) for row in items),
            "edge_jaccard_vs_beta0_mean": mean(jaccards) if jaccards else 0.0,
            "edge_jaccard_vs_beta0_min": min(jaccards) if jaccards else 0.0,
            "edge_jaccard_vs_beta0_median": median(jaccards) if jaccards else 0.0,
            "selected_edge_overlap_fraction_vs_beta0_mean": mean(overlaps) if overlaps else 0.0,
            "selected_edge_retention_fraction_vs_beta0_mean": mean(retentions) if retentions else 0.0,
            "selected_edge_symmetric_difference_fraction_mean": mean(symdiffs) if symdiffs else 0.0,
            "edge_count_delta_vs_beta0_mean": mean(edge_deltas) if edge_deltas else 0.0,
            "sample_status": "ok" if len(ok_items) == len(items) else "partial_error",
        })
    return out


def unique_max_entropy_baseline_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    out: list[dict[str, object]] = []
    for row in rows:
        family = canonical_transition_energy_family(str(row.get("substrate_family", "") or substrate_family_from_condition_id(row.get("condition_id", ""))))
        if family not in MAX_ENTROPY_FAMILIES or row.get("actual_control_name") != BASELINE_CONTROL:
            continue
        key = str(row.get("baseline_system_id", row.get("condition_id", "")))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def max_entropy_constraint_manifest_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in unique_max_entropy_baseline_rows(rows):
        out.append({
            "baseline_system_id": row.get("baseline_system_id", ""),
            "condition_id": row.get("condition_id", ""),
            "substrate_family": row.get("substrate_family", ""),
            "substrate_variant": row.get("substrate_variant", ""),
            "max_entropy_family": row.get("max_entropy_family", row.get("substrate_family", "")),
            "constraint_profile": row.get("max_entropy_constraint_profile", ""),
            "proposal_kernel": "hamming_ball_without_self",
            "locality_constraint_exact": int(float_or_zero(row.get("max_entropy_locality_violation_count")) == 0),
            "out_degree_constraint_exact": int(float_or_zero(row.get("max_entropy_out_degree_violation_count")) == 0),
            "target_marginal_applied": row.get("max_entropy_target_marginal_applied", ""),
            "equivalent_beta_target": row.get("equivalent_beta_target", row.get("max_entropy_equivalent_beta_target", "")),
            "macro_invariant_kind": row.get("macro_invariant_kind", ""),
            "macro_invariant_delta_match_tolerance": row.get("macro_invariant_delta_match_tolerance", ""),
            "macro_invariant_delta_match_metric": row.get("macro_invariant_delta_match_metric", ""),
            "macro_invariant_delta_target_distribution": row.get("macro_invariant_delta_target_distribution", ""),
        })
    return out


def max_entropy_marginal_match_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in unique_max_entropy_baseline_rows(rows):
        grouped[(
            str(row.get("substrate_family", "")),
            str(row.get("substrate_variant", "")),
            str(row.get("macro_invariant_kind", "")),
            str(row.get("equivalent_beta_target", row.get("max_entropy_equivalent_beta_target", ""))),
        )].append(row)
    out: list[dict[str, object]] = []
    for (family, variant, invariant_kind, beta), items in sorted(grouped.items()):
        errors = [float_or_zero(row.get("macro_invariant_delta_match_error")) for row in items if row.get("macro_invariant_delta_match_error") not in (None, "")]
        tolerances = [float_or_zero(row.get("macro_invariant_delta_match_tolerance")) for row in items if row.get("macro_invariant_delta_match_tolerance") not in (None, "")]
        target_applied = sum(int(float_or_zero(row.get("max_entropy_target_marginal_applied"))) for row in items)
        tolerance = max(tolerances) if tolerances else 0.0
        out.append({
            "substrate_family": family,
            "substrate_variant": variant,
            "macro_invariant_kind": invariant_kind,
            "equivalent_beta_target": beta,
            "baseline_system_count": len(items),
            "target_marginal_applied_count": target_applied,
            "macro_invariant_delta_match_error_mean": mean(errors) if errors else "",
            "macro_invariant_delta_match_error_max": max(errors) if errors else "",
            "macro_invariant_delta_match_tolerance": tolerance if tolerances else "",
            "macro_invariant_delta_match_pass_fraction": sum(int(value <= tolerance) for value in errors) / max(1, len(errors)) if errors and tolerance else "",
            "marginal_match_status": "not_applicable" if target_applied == 0 else "ok" if errors and max(errors) <= tolerance else "repair_required",
        })
    return out


def max_entropy_sampler_diagnostics_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in unique_max_entropy_baseline_rows(rows):
        out.append({
            "baseline_system_id": row.get("baseline_system_id", ""),
            "condition_id": row.get("condition_id", ""),
            "substrate_family": row.get("substrate_family", ""),
            "substrate_variant": row.get("substrate_variant", ""),
            "equivalent_beta_target": row.get("equivalent_beta_target", row.get("max_entropy_equivalent_beta_target", "")),
            "macro_invariant_kind": row.get("macro_invariant_kind", ""),
            "max_entropy_sampler_status": row.get("max_entropy_sampler_status", ""),
            "max_entropy_sampler_draws": row.get("max_entropy_sampler_draws", ""),
            "max_entropy_sampler_best_draw_index": row.get("max_entropy_sampler_best_draw_index", ""),
            "max_entropy_sampler_weight_iterations": row.get("max_entropy_sampler_weight_iterations", ""),
            "max_entropy_calibration_family": row.get("max_entropy_calibration_family", ""),
            "max_entropy_calibration_edge_count": row.get("max_entropy_calibration_edge_count", ""),
            "edge_count": row.get("edge_count", ""),
            "mean_out_degree": row.get("mean_out_degree", ""),
            "max_entropy_locality_violation_count": row.get("max_entropy_locality_violation_count", ""),
            "max_entropy_out_degree_violation_count": row.get("max_entropy_out_degree_violation_count", ""),
            "max_entropy_empty_successor_source_count": row.get("max_entropy_empty_successor_source_count", ""),
            "macro_invariant_delta_match_error": row.get("macro_invariant_delta_match_error", ""),
            "macro_invariant_delta_match_tolerance": row.get("macro_invariant_delta_match_tolerance", ""),
            "macro_invariant_delta_observed_distribution": row.get("macro_invariant_delta_observed_distribution", ""),
        })
    return out


def max_entropy_edge_match_to_calibration_rows(jobs: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    sample_limit = max(0, int(getattr(args, "selected_edge_overlap_sample_jobs", 0)))
    if sample_limit <= 0:
        return []
    candidates = [
        job for job in jobs
        if canonical_transition_energy_family(str(job.get("substrate_family", "") or "")) in MAX_ENTROPY_FAMILIES
    ]
    buckets: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for job in candidates:
        family = canonical_transition_energy_family(str(job.get("substrate_family", "") or ""))
        invariant_kind = str(job.get("macro_invariant_kind", job.get("budget_kind", "")) or "")
        beta = str(job.get("equivalent_beta_target", job.get("macro_invariant_beta", "")) or "")
        buckets[(family, invariant_kind, beta)].append(job)
    selected: list[dict[str, object]] = []
    while len(selected) < sample_limit and any(buckets.values()):
        for key in sorted(buckets, key=lambda item: (item[0], item[1], float_or_zero(item[2]))):
            if len(selected) >= sample_limit:
                break
            if buckets[key]:
                selected.append(buckets[key].pop(0))
    observations: list[dict[str, object]] = []
    for job in selected:
        family = canonical_transition_energy_family(str(job.get("substrate_family", "") or ""))
        invariant_kind = str(job.get("macro_invariant_kind", job.get("budget_kind", "")) or "")
        beta = float_or_zero(job.get("equivalent_beta_target", job.get("macro_invariant_beta", "")))
        calibration_job = dict(job)
        calibration_job.update({
            "substrate_family": PRESERVATION_ASYMMETRY,
            "transition_energy_family": PRESERVATION_ASYMMETRY,
            "macro_invariant_beta": beta,
            "budget_weight": beta,
            "apply_reversibility": False,
        })
        try:
            calibration_edges = selected_edge_set(calibration_job)
            sampled_edges = selected_edge_set(job)
            intersection = len(calibration_edges & sampled_edges)
            union = len(calibration_edges | sampled_edges)
            observations.append({
                "substrate_family": family,
                "substrate_variant": job.get("substrate_variant", ""),
                "macro_invariant_kind": invariant_kind,
                "equivalent_beta_target": beta,
                "sample_status": "ok",
                "sample_error": "",
                "edge_jaccard_vs_calibration": intersection / max(1, union),
                "selected_edge_overlap_fraction_vs_calibration": intersection / max(1, len(calibration_edges)),
                "selected_edge_retention_fraction_vs_calibration": intersection / max(1, len(sampled_edges)),
                "selected_edge_symmetric_difference_fraction": (union - intersection) / max(1, union),
                "calibration_edge_count": len(calibration_edges),
                "sampled_edge_count": len(sampled_edges),
            })
        except Exception as exc:  # noqa: BLE001
            observations.append({
                "substrate_family": family,
                "substrate_variant": job.get("substrate_variant", ""),
                "macro_invariant_kind": invariant_kind,
                "equivalent_beta_target": beta,
                "sample_status": "error",
                "sample_error": repr(exc),
            })
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in observations:
        grouped[(
            str(row.get("substrate_family", "")),
            str(row.get("macro_invariant_kind", "")),
            str(row.get("equivalent_beta_target", "")),
        )].append(row)
    out: list[dict[str, object]] = []
    for (family, invariant_kind, beta), items in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1], float_or_zero(item[0][2]))):
        ok_items = [row for row in items if row.get("sample_status") == "ok"]
        out.append({
            "substrate_family": family,
            "macro_invariant_kind": invariant_kind,
            "equivalent_beta_target": beta,
            "sample_count": len(items),
            "ok_sample_count": len(ok_items),
            "error_sample_count": len(items) - len(ok_items),
            "edge_jaccard_vs_calibration_mean": mean([float_or_zero(row.get("edge_jaccard_vs_calibration")) for row in ok_items]) if ok_items else 0.0,
            "selected_edge_overlap_fraction_vs_calibration_mean": mean([float_or_zero(row.get("selected_edge_overlap_fraction_vs_calibration")) for row in ok_items]) if ok_items else 0.0,
            "selected_edge_retention_fraction_vs_calibration_mean": mean([float_or_zero(row.get("selected_edge_retention_fraction_vs_calibration")) for row in ok_items]) if ok_items else 0.0,
            "selected_edge_symmetric_difference_fraction_mean": mean([float_or_zero(row.get("selected_edge_symmetric_difference_fraction")) for row in ok_items]) if ok_items else 0.0,
            "sample_status": "ok" if len(ok_items) == len(items) else "partial_error",
        })
    return out


def paired_baseline_availability_by_max_entropy_variant_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        family = str(row.get("substrate_family", ""))
        if family not in MAX_ENTROPY_FAMILIES:
            continue
        grouped[(family, str(row.get("substrate_variant", "")), str(row.get("equivalent_beta_target", "")))].append(row)
    out: list[dict[str, object]] = []
    for (family, variant, beta), items in sorted(grouped.items()):
        missing = [row for row in items if row.get("response_status") == "baseline_missing" or row.get("response_class") == "transport_baseline_missing"]
        out.append({
            "substrate_family": family,
            "substrate_variant": variant,
            "equivalent_beta_target": beta,
            "response_rows": len(items),
            "paired_baseline_available_rows": len(items) - len(missing),
            "paired_baseline_missing_rows": len(missing),
            "paired_baseline_available_fraction": (len(items) - len(missing)) / max(1, len(items)),
            "paired_baseline_status": "ok" if not missing else "response_baseline_missing",
        })
    return out


def selected_edge_overlap_sort_key(key: tuple[str, str, str, str, str]) -> tuple[str, str, float, str, str]:
    family, invariant_kind, beta, alpha, smoothness = key
    return (family, invariant_kind, float_or_zero(beta), alpha, smoothness)


def matrix_manifest_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    return [{
        **key_row(matrix.key),
        "matrix_id": matrix.matrix_id,
        "matrix_family": "horizon_transport",
        "row_item_count": len(matrix.row_items),
        "column_item_count": len(matrix.column_items),
        "transport_context_count": matrix.transport_context_count,
        "transport_mass_total": matrix.transport_mass_total,
        "coverage": matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total),
        "normalization_kind": "transport_count",
        **intervention_taxonomy(matrix.key),
    } for matrix in matrices]


def matrix_entry_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    top_k = max(0, int(getattr(args, "matrix_entry_top_k", 0)))
    if top_k == 0:
        return rows
    for matrix in matrices:
        nonzero = np.argwhere(matrix.matrix > 0)
        entries = [
            (int(row_index), int(column_index), float(matrix.matrix[row_index, column_index]))
            for row_index, column_index in nonzero
        ]
        entries.sort(key=lambda item: item[2], reverse=True)
        total = max(1.0, float(matrix.matrix.sum()))
        for rank, (row_index, column_index, mass) in enumerate(entries[:top_k], start=1):
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "entry_rank": rank,
                "row_item": matrix.row_items[row_index],
                "row_item_index": row_index,
                "column_item": matrix.column_items[column_index],
                "column_item_index": column_index,
                "transport_mass": mass,
                "transport_mass_share": mass / total,
                "matrix_entry_retention": f"top_{top_k}_nonzero_entries_by_mass",
            })
    return rows


def substrate_family_manifest_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    families = substrate_families(args)
    matrix_counts = Counter(substrate_family_from_condition_id(matrix.key.condition_id) for matrix in matrices)
    return [
        {
            "substrate_family": family,
            "transition_energy_family": family,
            "substrate_role": "current_comparator" if family == CONSTRAINT_TEMPLATE_CURRENT else "transition_energy_untethering_family",
            "matrix_count": matrix_counts.get(family, 0),
            "uses_hand_built_constraint_templates": int(family == CONSTRAINT_TEMPLATE_CURRENT),
            "proposal_kernel": "current_relation_generator" if family == CONSTRAINT_TEMPLATE_CURRENT else "hamming_ball_without_self",
            "selection_rule": substrate_selection_rule(family),
        }
        for family in families
    ]


def substrate_family_variant_manifest_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    matrix_counts = Counter(
        (substrate_family_from_condition_id(matrix.key.condition_id), substrate_variant_from_condition_id(matrix.key.condition_id))
        for matrix in matrices
    )
    rows: list[dict[str, object]] = []
    for variant in substrate_family_variants(args):
        family = str(variant.get("substrate_family", ""))
        variant_id = str(variant.get("substrate_variant", ""))
        rows.append({
            **variant,
            "matrix_count": matrix_counts.get((family, variant_id), 0),
            "uses_hand_built_constraint_templates": int(family == CONSTRAINT_TEMPLATE_CURRENT),
            "proposal_kernel": "current_relation_generator" if family == CONSTRAINT_TEMPLATE_CURRENT else "hamming_ball_without_self",
            "selection_rule": substrate_selection_rule(family),
        })
    return rows


def substrate_selection_rule(family: str) -> str:
    if family == CONSTRAINT_TEMPLATE_CURRENT:
        return "current_constraint_scored_top_m"
    if family == MAX_ENTROPY_LOCAL:
        return "uniform_local_without_macro_constraint"
    if family == MAX_ENTROPY_MACRO_INVARIANT:
        return "maximum_entropy_local_matched_macro_invariant_delta"
    return "top_m_lowest_energy_candidates"


def transition_energy_family_summary_rows(args: argparse.Namespace) -> list[dict[str, object]]:
    rows = []
    for family in substrate_families(args):
        rows.append({
            "substrate_family": family,
            "transition_energy_form": transition_energy_form_label(family),
            "hand_built_constraint_vocabulary_removed": int(family != CONSTRAINT_TEMPLATE_CURRENT),
            "probabilistic_sampling_used": int(family in MAX_ENTROPY_FAMILIES),
        })
    return rows


def transition_energy_parameter_summary_rows(args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for variant in substrate_family_variants(args):
        family = str(variant.get("substrate_family", ""))
        rows.append({
            "substrate_family": family,
            "substrate_variant": variant.get("substrate_variant", ""),
            "variant_role": variant.get("variant_role", ""),
            "transition_energy_form": transition_energy_form_label(family),
            "potential_beta": variant.get("potential_beta", "") if family == SMOOTH_RANDOM_POTENTIAL else "",
            "potential_smoothness": variant.get("potential_smoothness", "") if family == SMOOTH_RANDOM_POTENTIAL else "",
            "potential_scale": variant.get("potential_scale", "") if family == SMOOTH_RANDOM_POTENTIAL else "",
            "budget_kind": variant.get("budget_kind", "") if family == BUDGET_CONSERVATION else "",
            "budget_weight": variant.get("budget_weight", "") if family == BUDGET_CONSERVATION else "",
            "macro_invariant_kind": variant.get("macro_invariant_kind", "") if family in {PRESERVATION_ASYMMETRY, COMBINED_ASYMMETRY, *MAX_ENTROPY_FAMILIES} else "",
            "macro_invariant_beta": variant.get("macro_invariant_beta", "") if family in {PRESERVATION_ASYMMETRY, COMBINED_ASYMMETRY, *MAX_ENTROPY_FAMILIES} else "",
            "equivalent_beta_target": variant.get("equivalent_beta_target", "") if family in MAX_ENTROPY_FAMILIES else "",
            "max_entropy_sampler_draws": variant.get("max_entropy_sampler_draws", "") if family in MAX_ENTROPY_FAMILIES else "",
            "max_entropy_delta_match_error_max": variant.get("max_entropy_delta_match_error_max", "") if family in MAX_ENTROPY_FAMILIES else "",
            "asymmetry_alpha": variant.get("asymmetry_alpha", "") if family in {DIRECTIONAL_ASYMMETRY, COMBINED_ASYMMETRY} else "",
            "asymmetry_field_smoothness": variant.get("asymmetry_field_smoothness", "") if family in {DIRECTIONAL_ASYMMETRY, COMBINED_ASYMMETRY} else "",
            "asymmetry_field_scale": variant.get("asymmetry_field_scale", "") if family in {DIRECTIONAL_ASYMMETRY, COMBINED_ASYMMETRY} else "",
            "alpha_beta_pair": variant.get("alpha_beta_pair", "") if family == COMBINED_ASYMMETRY else "",
            "transition_roughness_strength_override": variant.get("transition_roughness_strength", ""),
        })
    return rows


def substrate_capacity_by_family_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    grouped: dict[str, list[TransportMatrix]] = defaultdict(list)
    for matrix in matrices:
        grouped[substrate_family_from_condition_id(matrix.key.condition_id)].append(matrix)
    rows: list[dict[str, object]] = []
    for family, items in sorted(grouped.items()):
        coverages = [matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) for matrix in items]
        row_counts = [matrix.raw_row_item_count for matrix in items]
        col_counts = [matrix.raw_column_item_count for matrix in items]
        rows.append({
            "substrate_family": family,
            "matrix_count": len(items),
            "coverage_mean": mean(coverages) if coverages else 0.0,
            "raw_row_item_count_mean": mean(row_counts) if row_counts else 0.0,
            "raw_column_item_count_mean": mean(col_counts) if col_counts else 0.0,
            "capacity_read": "substrate_capacity_low" if items and (mean(row_counts) < 2 or mean(col_counts) < 2) else "substrate_capacity_available",
        })
    return rows


def substrate_capacity_by_family_variant_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[TransportMatrix]] = defaultdict(list)
    for matrix in matrices:
        grouped[(substrate_family_from_condition_id(matrix.key.condition_id), substrate_variant_from_condition_id(matrix.key.condition_id))].append(matrix)
    rows: list[dict[str, object]] = []
    for (family, variant), items in sorted(grouped.items()):
        coverages = [matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) for matrix in items]
        row_counts = [matrix.raw_row_item_count for matrix in items]
        col_counts = [matrix.raw_column_item_count for matrix in items]
        rows.append({
            "substrate_family": family,
            "substrate_variant": variant,
            "matrix_count": len(items),
            "coverage_mean": mean(coverages) if coverages else 0.0,
            "coverage_min": min(coverages) if coverages else 0.0,
            "raw_row_item_count_mean": mean(row_counts) if row_counts else 0.0,
            "raw_column_item_count_mean": mean(col_counts) if col_counts else 0.0,
            "capacity_read": "substrate_capacity_low" if items and (mean(row_counts) < 2 or mean(col_counts) < 2) else "substrate_capacity_available",
        })
    return rows


def substrate_generation_diagnostics_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))))].append(row)
    out: list[dict[str, object]] = []
    for family, items in sorted(grouped.items()):
        fa_counts = [float_or_zero(row.get("fa_state_count")) for row in items if row.get("fa_state_count", "") != ""]
        fb_counts = [float_or_zero(row.get("fb_state_count")) for row in items if row.get("fb_state_count", "") != ""]
        out.append({
            "substrate_family": family,
            "metric_row_count": len(items),
            "fa_state_count_mean": mean(fa_counts) if fa_counts else 0.0,
            "fb_state_count_mean": mean(fb_counts) if fb_counts else 0.0,
            "baseline_rows": sum(int(row.get("actual_control_name") == BASELINE_CONTROL) for row in items),
            "mechanism_control_rows": sum(int(row.get("actual_control_name") != BASELINE_CONTROL) for row in items),
            "potential_neighbor_correlation_mean": optional_mean(items, "potential_neighbor_correlation"),
            "budget_delta_mean": optional_mean(items, "budget_delta_mean"),
            "asymmetry_neighbor_correlation_mean": optional_mean(items, "asymmetry_neighbor_correlation"),
            "asymmetry_delta_mean": optional_mean(items, "asymmetry_delta_mean"),
            "macro_invariant_delta_mean": optional_mean(items, "macro_invariant_delta_mean"),
            "selected_energy_mean": optional_mean(items, "selected_energy_mean"),
        })
    return out


def optional_mean(rows: list[dict[str, object]], field: str) -> object:
    values = [float_or_zero(row.get(field)) for row in rows if row.get(field) not in (None, "")]
    return mean(values) if values else ""


def horizon_transport_by_substrate_family_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))))].append(row)
    out: list[dict[str, object]] = []
    for family, items in sorted(grouped.items()):
        matched = [row for row in items if row.get("context_read") == "matched_marginal_separates_interpretable"]
        out.append({
            "substrate_family": family,
            "context_count": len(items),
            "matched_marginal_separates_interpretable_count": len(matched),
            "context_read_mode": Counter(str(row.get("context_read", "")) for row in items).most_common(1)[0][0] if items else "",
        })
    return out


def horizon_transport_by_substrate_family_variant_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(
            str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", "")))),
            str(row.get("substrate_variant", substrate_variant_from_condition_id(row.get("condition_id", "")))),
        )].append(row)
    out: list[dict[str, object]] = []
    for (family, variant), items in sorted(grouped.items()):
        matched = [row for row in items if row.get("context_read") == "matched_marginal_separates_interpretable"]
        coverages = [float_or_zero(row.get("coverage_min")) for row in items]
        out.append({
            "substrate_family": family,
            "substrate_variant": variant,
            "context_count": len(items),
            "matched_marginal_separates_interpretable_count": len(matched),
            "matched_interpretable_context_fraction": len(matched) / max(1, len(items)),
            "matrix_coverage_min": min(coverages) if coverages else 0.0,
            "context_read_mode": Counter(str(row.get("context_read", "")) for row in items).most_common(1)[0][0] if items else "",
        })
    return out


def aligned_amplification_by_substrate_family_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))))].append(row)
    out: list[dict[str, object]] = []
    for family, items in sorted(grouped.items()):
        interpretable = [row for row in items if is_interpretable_response(row.get("response_class"))]
        aligned = [row for row in interpretable if row.get("response_class") == RESPONSE_CLASS_AMPLIFIED_ALIGNED]
        interpretable_counts = Counter(str(row.get("response_class", "")) for row in interpretable)
        out.append({
            "substrate_family": family,
            "response_rows": len(items),
            "aligned_amplification_rows": len(aligned),
            "interpretable_response_rows": len(interpretable),
            "measurement_limit_response_rows": len(items) - len(interpretable),
            "aligned_amplification_fraction": len(aligned) / max(1, len(interpretable)),
            "aligned_amplification_fraction_all_rows": len(aligned) / max(1, len(items)),
            "dominant_response_class": interpretable_counts.most_common(1)[0][0] if interpretable_counts else "",
        })
    return out


def response_by_group_rows(rows: list[dict[str, object]], fields: tuple[str, ...]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(field, "") for field in fields)].append(row)
    out: list[dict[str, object]] = []
    response_classes = (
        RESPONSE_CLASS_STABLE,
        RESPONSE_CLASS_AMPLIFIED_ALIGNED,
        RESPONSE_CLASS_WEAKENED,
        RESPONSE_CLASS_REROUTED,
        RESPONSE_CLASS_REOPENS,
        RESPONSE_CLASS_COLLAPSES,
        RESPONSE_CLASS_CONTROL_EQUIVALENT,
        *MEASUREMENT_LIMIT_RESPONSE_CLASSES,
    )
    for key, items in sorted(grouped.items(), key=lambda item: tuple(str(part) for part in item[0])):
        counts = Counter(str(row.get("response_class", "")) for row in items)
        interpretable_items = [item for item in items if is_interpretable_response(item.get("response_class"))]
        interpretable_counts = Counter(str(row.get("response_class", "")) for row in interpretable_items)
        out_row = {field: key[index] for index, field in enumerate(fields)}
        out_row.update({
            "response_rows": len(items),
            "interpretable_response_rows": len(interpretable_items),
            "measurement_limit_response_rows": len(items) - len(interpretable_items),
            "dominant_response_class": interpretable_counts.most_common(1)[0][0] if interpretable_counts else "",
            "aligned_amplification_fraction": interpretable_counts.get(RESPONSE_CLASS_AMPLIFIED_ALIGNED, 0) / max(1, len(interpretable_items)),
            "aligned_amplification_fraction_all_rows": counts.get(RESPONSE_CLASS_AMPLIFIED_ALIGNED, 0) / max(1, len(items)),
        })
        for response_class in response_classes:
            out_row[f"{response_class}_count"] = counts.get(response_class, 0)
        out.append(out_row)
    return out


def response_diversity_by_substrate_family_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))))].append(row)
    out = []
    for family, items in sorted(grouped.items()):
        values = [float_or_zero(row.get("response_diversity_score")) for row in items]
        out.append({
            "substrate_family": family,
            "response_diversity_rows": len(items),
            "response_diversity_score_mean": mean(values) if values else 0.0,
            "response_diversity_read_mode": Counter(str(row.get("response_diversity_read", "")) for row in items).most_common(1)[0][0] if items else "",
        })
    return out


def response_diversity_by_substrate_family_variant_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(
            str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", "")))),
            str(row.get("substrate_variant", substrate_variant_from_condition_id(row.get("condition_id", "")))),
        )].append(row)
    out = []
    for (family, variant), items in sorted(grouped.items()):
        values = [float_or_zero(row.get("response_diversity_score")) for row in items]
        out.append({
            "substrate_family": family,
            "substrate_variant": variant,
            "response_diversity_rows": len(items),
            "response_diversity_score_mean": mean(values) if values else 0.0,
            "response_diversity_read_mode": Counter(str(row.get("response_diversity_read", "")) for row in items).most_common(1)[0][0] if items else "",
        })
    return out


def transport_viscosity_by_substrate_family_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))))].append(row)
    out = []
    for family, items in sorted(grouped.items()):
        values = [float_or_zero(row.get("transport_viscosity_score")) for row in items]
        out.append({
            "substrate_family": family,
            "transport_viscosity_rows": len(items),
            "transport_viscosity_score_mean": mean(values) if values else 0.0,
            "transport_viscosity_read_mode": Counter(str(row.get("transport_viscosity_read", "")) for row in items).most_common(1)[0][0] if items else "",
        })
    return out


def transport_viscosity_by_substrate_family_variant_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(
            str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", "")))),
            str(row.get("substrate_variant", substrate_variant_from_condition_id(row.get("condition_id", "")))),
        )].append(row)
    out = []
    for (family, variant), items in sorted(grouped.items()):
        values = [float_or_zero(row.get("transport_viscosity_score")) for row in items]
        out.append({
            "substrate_family": family,
            "substrate_variant": variant,
            "transport_viscosity_rows": len(items),
            "transport_viscosity_score_mean": mean(values) if values else 0.0,
            "transport_viscosity_read_mode": Counter(str(row.get("transport_viscosity_read", "")) for row in items).most_common(1)[0][0] if items else "",
        })
    return out


def matched_null_pass_by_substrate_family_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))))].append(row)
    out = []
    for family, items in sorted(grouped.items()):
        pass_values = [float_or_zero(row.get("pass_fraction")) for row in items]
        percentile_values = [float_or_zero(row.get("min_observed_percentile_vs_null")) for row in items]
        out.append({
            "substrate_family": family,
            "matched_null_rows": len(items),
            "pass_fraction_mean": mean(pass_values) if pass_values else 0.0,
            "min_observed_percentile_mean": mean(percentile_values) if percentile_values else 0.0,
        })
    return out


def matched_null_pass_by_substrate_family_variant_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(
            str(row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", "")))),
            str(row.get("substrate_variant", substrate_variant_from_condition_id(row.get("condition_id", "")))),
        )].append(row)
    out = []
    for (family, variant), items in sorted(grouped.items()):
        pass_values = [float_or_zero(row.get("pass_fraction")) for row in items]
        percentile_values = [float_or_zero(row.get("min_observed_percentile_vs_null")) for row in items]
        out.append({
            "substrate_family": family,
            "substrate_variant": variant,
            "matched_null_rows": len(items),
            "pass_fraction_mean": mean(pass_values) if pass_values else 0.0,
            "min_observed_percentile_mean": mean(percentile_values) if percentile_values else 0.0,
        })
    return out


def row_item_manifest_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        row_mass = matrix.matrix.sum(axis=1)
        total = float(row_mass.sum())
        for index, item in enumerate(matrix.row_items):
            rows.append({**key_row(matrix.key), "matrix_id": matrix.matrix_id, "row_item": item, "row_item_index": index, "row_transport_mass": float(row_mass[index]), "row_mass_share": float(row_mass[index]) / max(1.0, total)})
    return rows


def column_item_manifest_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        col_mass = matrix.matrix.sum(axis=0)
        total = float(col_mass.sum())
        for index, item in enumerate(matrix.column_items):
            rows.append({**key_row(matrix.key), "matrix_id": matrix.matrix_id, "column_item": item, "column_item_index": index, "column_transport_mass": float(col_mass[index]), "column_mass_share": float(col_mass[index]) / max(1.0, total)})
    return rows


def coverage_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    return [{
        **key_row(matrix.key),
        "matrix_id": matrix.matrix_id,
        "raw_row_item_count": matrix.raw_row_item_count,
        "raw_column_item_count": matrix.raw_column_item_count,
        "retained_row_item_count": len(matrix.row_items),
        "retained_column_item_count": len(matrix.column_items),
        "transport_mass_total": matrix.transport_mass_total,
        "retained_transport_mass": matrix.retained_transport_mass,
        "dropped_transport_mass": matrix.dropped_transport_mass,
        "coverage": matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total),
    } for matrix in matrices]


def matrix_summary_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows = []
    for matrix in matrices:
        singular = matrix.singular_values
        row_mass = matrix.matrix.sum(axis=1)
        col_mass = matrix.matrix.sum(axis=0)
        rows.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "matrix_family": "horizon_transport",
            "row_item_count": len(matrix.row_items),
            "column_item_count": len(matrix.column_items),
            "transport_context_count": matrix.transport_context_count,
            "transport_mass_total": matrix.transport_mass_total,
            "positive_or_nonzero_spectral_mass": float(np.sum(singular)),
            "effective_rank": effective_rank(singular),
            "spectral_gap_k": spectral_gap(singular, args.top_k),
            "left_subspace_participation": vector_participation(matrix.left_vectors[:, 0]) if matrix.left_vectors.size else 0.0,
            "right_subspace_participation": vector_participation(matrix.right_vectors[:, 0]) if matrix.right_vectors.size else 0.0,
            "left_loading_entropy": entropy_from_values(row_mass),
            "right_loading_entropy": entropy_from_values(col_mass),
            "left_top_item_mass_share": top_share(row_mass, 1),
            "right_top_item_mass_share": top_share(col_mass, 1),
            "transport_entropy": entropy_from_values(matrix.matrix.flatten()),
            "transport_concentration": top_share(matrix.matrix.flatten(), 1),
            "marginal_residual_fraction": marginal_residual_fraction(matrix.matrix),
            "coverage": matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total),
            "normalization_kind": "transport_count",
            **intervention_taxonomy(matrix.key),
        })
    return rows


def svd_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        for rank, value in enumerate(matrix.singular_values[: args.top_k], start=1):
            rows.append({**key_row(matrix.key), "matrix_id": matrix.matrix_id, "rank": rank, "singular_value": float(value), "singular_value_share": float(value) / max(1e-12, float(np.sum(matrix.singular_values)))})
    return rows


def participation_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        for rank in range(min(args.top_k, len(matrix.singular_values))):
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "rank": rank + 1,
                "left_participation_ratio": vector_participation(matrix.left_vectors[:, rank]),
                "right_participation_ratio": vector_participation(matrix.right_vectors[:, rank]),
                "singular_value": float(matrix.singular_values[rank]),
            })
    return rows


def entropy_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    return [{
        **key_row(matrix.key),
        "matrix_id": matrix.matrix_id,
        "transport_entropy": entropy_from_values(matrix.matrix.flatten()),
        "row_entropy": entropy_from_values(matrix.matrix.sum(axis=1)),
        "column_entropy": entropy_from_values(matrix.matrix.sum(axis=0)),
        "transport_concentration": top_share(matrix.matrix.flatten(), 1),
        "top_5_transport_share": top_share(matrix.matrix.flatten(), 5),
    } for matrix in matrices]


def detector_null_anatomy_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    baseline = [matrix for matrix in matrices if matrix.key.actual_control_name == BASELINE_CONTROL]
    pool_by_probe_flow = group_matrices(baseline, ("probe_key", "flow_mode"))
    rows: list[dict[str, object]] = []
    for matrix in baseline:
        for null_family in DETECTOR_NULL_FAMILIES:
            null_values_by_stat: dict[str, list[float]] = defaultdict(list)
            for replicate in range(max(1, args.null_replicates)):
                rng = random.Random(stable_seed(f"horizon_transport_null|{matrix.matrix_id}|{null_family}|{replicate}"))
                null_matrix = make_null_matrix(matrix, null_family, pool_by_probe_flow, rng)
                for stat in DETECTOR_STATISTICS:
                    null_values_by_stat[stat].append(transport_stat(null_matrix, stat))
            for stat in DETECTOR_STATISTICS:
                observed = transport_stat(matrix.matrix, stat)
                null_values = null_values_by_stat[stat]
                percentile = sum(value <= observed for value in null_values) / max(1, len(null_values))
                threshold = float(args.detector_null_min_percentile)
                passed = percentile >= threshold
                category = null_category(null_family)
                rows.append({
                    **key_row(matrix.key),
                    "matrix_id": matrix.matrix_id,
                    "null_family": null_family,
                    "null_category": category,
                    "observed_statistic": stat,
                    "observed_statistic_value": observed,
                    "null_mean": mean(null_values) if null_values else "",
                    "null_std": pstdev(null_values) if len(null_values) > 1 else 0.0 if null_values else "",
                    "null_max": max(null_values) if null_values else "",
                    "observed_percentile_vs_null": percentile,
                    "expected_direction": expected_null_direction(category),
                    "separation_margin": percentile - threshold,
                    "null_gate_passed": int(passed),
                    "failure_interpretation": null_failure_interpretation(matrix, category, percentile, threshold, len(null_values)),
                })
    return rows


def make_null_matrix(
    matrix: TransportMatrix,
    null_family: str,
    pool_by_probe_flow: dict[tuple[object, ...], list[TransportMatrix]],
    rng: random.Random,
) -> np.ndarray:
    values = np.asarray(matrix.matrix, dtype=np.float64)
    if null_family == "row_marginal_matched_transport_null":
        return row_marginal_matched_matrix(values, rng)
    if null_family == "column_marginal_matched_transport_null":
        return column_marginal_matched_matrix(values, rng)
    if null_family == "row_column_marginal_matched_transport_null":
        return row_column_marginal_matched_matrix(values, rng)
    if null_family == "label_shuffle_transport_interpretation_control":
        row_order = list(range(values.shape[0]))
        col_order = list(range(values.shape[1]))
        rng.shuffle(row_order)
        rng.shuffle(col_order)
        return values[row_order, :][:, col_order]
    if null_family == "horizon_pair_shuffle_transport_null":
        pool = [
            item for item in pool_by_probe_flow.get((matrix.key.probe_key, matrix.key.flow_mode), [])
            if item.matrix_id != matrix.matrix_id and item.matrix.shape == matrix.matrix.shape
        ]
        if pool:
            return np.asarray(rng.choice(pool).matrix, dtype=np.float64)
    flat = list(values.flatten())
    rng.shuffle(flat)
    return np.asarray(flat, dtype=np.float64).reshape(values.shape)


def row_marginal_matched_matrix(values: np.ndarray, rng: random.Random) -> np.ndarray:
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    total = float(col_sums.sum())
    if total <= 0:
        return np.zeros_like(values, dtype=np.float64)
    probs = np.asarray(col_sums, dtype=np.float64) / total
    np_rng = np.random.default_rng(rng.randrange(0, 2**32 - 1))
    out = np.zeros_like(values, dtype=np.float64)
    for index, row_total in enumerate(row_sums):
        count = max(0, int(round(float(row_total))))
        if count <= 0:
            continue
        sample = np_rng.multinomial(count, probs)
        out[index, :] = sample
        if abs(float(row_total) - count) > 1e-9:
            out[index, :] *= float(row_total) / max(1.0, float(count))
    return out


def column_marginal_matched_matrix(values: np.ndarray, rng: random.Random) -> np.ndarray:
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    total = float(row_sums.sum())
    if total <= 0:
        return np.zeros_like(values, dtype=np.float64)
    probs = np.asarray(row_sums, dtype=np.float64) / total
    np_rng = np.random.default_rng(rng.randrange(0, 2**32 - 1))
    out = np.zeros_like(values, dtype=np.float64)
    for index, col_total in enumerate(col_sums):
        count = max(0, int(round(float(col_total))))
        if count <= 0:
            continue
        sample = np_rng.multinomial(count, probs)
        out[:, index] = sample
        if abs(float(col_total) - count) > 1e-9:
            out[:, index] *= float(col_total) / max(1.0, float(count))
    return out


def row_column_marginal_matched_matrix(values: np.ndarray, rng: random.Random) -> np.ndarray:
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    total = float(row_sums.sum())
    if total <= 0:
        return np.zeros_like(values, dtype=np.float64)
    np_rng = np.random.default_rng(rng.randrange(0, 2**32 - 1))
    out = np_rng.random(values.shape) + 1e-6
    for _ in range(80):
        current_rows = out.sum(axis=1)
        out *= np.divide(row_sums, current_rows, out=np.zeros_like(row_sums), where=current_rows > 0)[:, None]
        current_cols = out.sum(axis=0)
        out *= np.divide(col_sums, current_cols, out=np.zeros_like(col_sums), where=current_cols > 0)[None, :]
    return out


def null_category(null_family: str) -> str:
    if null_family in INTERPRETATION_CONTROL_FAMILIES:
        return "label_interpretation_control"
    if null_family in MARGINAL_MATCHED_NULL_FAMILIES:
        return "marginal_matched_detector_null"
    return "structure_destroying_detector_null"


def expected_null_direction(category: str) -> str:
    if category == "label_interpretation_control":
        return "label_permutation_interpretation_only"
    if category == "marginal_matched_detector_null":
        return "observed_above_marginal_matched_null"
    return "observed_above_detector_null"


def detector_null_summary_rows(anatomy: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, items in group_by(anatomy, ("null_family", "null_category", "observed_statistic")).items():
        passed = [int(float_or_zero(row.get("null_gate_passed"))) for row in items]
        percentiles = [float_or_zero(row.get("observed_percentile_vs_null")) for row in items]
        if key[1] == "label_interpretation_control":
            summary_read = "interpretation_control_only"
        else:
            summary_read = "detector_null_separates" if passed and mean(passed) >= args.detector_null_min_pass_fraction else "detector_null_control_equivalent"
        rows.append({
            "null_family": key[0],
            "null_category": key[1],
            "observed_statistic": key[2],
            "matrix_count": len({row.get("matrix_id") for row in items}),
            "row_count": len(items),
            "pass_fraction": mean(passed) if passed else 0.0,
            "median_observed_percentile_vs_null": median(percentiles) if percentiles else 0.0,
            "min_observed_percentile_vs_null": min(percentiles) if percentiles else 0.0,
            "required_pass_fraction": args.detector_null_min_pass_fraction,
            "summary_read": summary_read,
        })
    return rows


def matched_marginal_summary_rows(anatomy: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    wanted = [
        row for row in anatomy
        if row.get("null_category") == "marginal_matched_detector_null"
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    keys = ("probe_key", "flow_mode", "source_horizon_band", "target_horizon_band", "H_a", "H_b", "condition_id", "null_family")
    for key, items in group_by(wanted, keys).items():
        passed = [int(float_or_zero(row.get("null_gate_passed"))) for row in items]
        percentiles = [float_or_zero(row.get("observed_percentile_vs_null")) for row in items]
        pass_fraction = mean(passed) if passed else 0.0
        rows.append({
            "probe_key": key[0],
            "flow_mode": key[1],
            "source_horizon_band": key[2],
            "target_horizon_band": key[3],
            "H_a": key[4],
            "H_b": key[5],
            "horizon_pair": f"{key[4]}->{key[5]}",
            "substrate_family": substrate_family_from_condition_id(key[6]),
            "substrate_variant": substrate_variant_from_condition_id(key[6]),
            "condition_id": key[6],
            "null_family": key[7],
            "observed_statistic": "marginal_residual_fraction",
            "matrix_count": len({row.get("matrix_id") for row in items}),
            "row_count": len(items),
            "pass_fraction": pass_fraction,
            "median_observed_percentile_vs_null": median(percentiles) if percentiles else 0.0,
            "min_observed_percentile_vs_null": min(percentiles) if percentiles else 0.0,
            "required_pass_fraction": args.detector_null_min_pass_fraction,
            "summary_read": "detector_null_separates" if pass_fraction >= args.detector_null_min_pass_fraction else "detector_null_control_equivalent",
        })
    return rows


def terminal_saturation_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    grouped = group_matrices(matrices, ("condition_id", "actual_control_name", "mechanism_control_strength", "probe_key", "flow_mode"))
    rows: list[dict[str, object]] = []
    for _key, items in grouped.items():
        previous_entropy = None
        previous_support = None
        for matrix in sorted(items, key=lambda item: (item.key.H_b, item.key.H_a)):
            values = matrix.matrix
            total = float(values.sum())
            flat = values.flatten()
            row_mass = values.sum(axis=1)
            col_mass = values.sum(axis=0)
            largest_entry_share = float(np.max(flat)) / max(1.0, total) if flat.size else 0.0
            row_max_share = float(np.max(row_mass)) / max(1.0, total) if row_mass.size else 0.0
            column_max_share = float(np.max(col_mass)) / max(1.0, total) if col_mass.size else 0.0
            entropy = entropy_from_values(flat)
            max_entropy = math.log2(max(2, int(np.count_nonzero(flat))))
            entropy_fraction = entropy / max(1e-12, max_entropy)
            support_total = matrix.raw_row_item_count + matrix.raw_column_item_count
            coverage = matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total)
            row_support_saturation = matrix.raw_row_item_count <= 2 or row_max_share >= 0.95
            column_support_saturation = matrix.raw_column_item_count <= 2 or column_max_share >= 0.95
            row_column_support_saturation = row_support_saturation and column_support_saturation
            mass_concentration_saturation = largest_entry_share >= 0.80 or row_max_share >= 0.95 or column_max_share >= 0.95
            transport_entropy_saturation = entropy_fraction <= 0.15
            frontier_support_saturation = row_support_saturation or column_support_saturation
            undercovered = coverage < 0.80 or len(matrix.row_items) < 2 or len(matrix.column_items) < 2
            terminal = (
                matrix.key.H_b >= 96
                and (frontier_support_saturation or transport_entropy_saturation or mass_concentration_saturation)
            )
            if undercovered:
                allowed = "undercovered_diagnostic_only"
            elif terminal:
                allowed = "terminal_saturation_diagnostic_only"
            else:
                allowed = "normal_horizon_response"
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "terminal_saturation_flag": int(terminal),
                "frontier_support_saturation": int(frontier_support_saturation),
                "transport_entropy_saturation": int(transport_entropy_saturation),
                "row_support_saturation": int(row_support_saturation),
                "column_support_saturation": int(column_support_saturation),
                "row_column_support_saturation": int(row_column_support_saturation),
                "mass_concentration_saturation": int(mass_concentration_saturation),
                "largest_entry_mass_share": largest_entry_share,
                "row_max_mass_share": row_max_share,
                "column_max_mass_share": column_max_share,
                "transport_entropy": entropy,
                "transport_entropy_fraction_of_nonzero_max": entropy_fraction,
                "transport_entropy_delta_vs_previous_horizon": "" if previous_entropy is None else entropy - previous_entropy,
                "support_delta_vs_previous_horizon": "" if previous_support is None else support_total - previous_support,
                "horizon_pair_undercoverage_flag": int(undercovered),
                "coverage": coverage,
                "allowed_interpretation_level": allowed,
            })
            previous_entropy = entropy
            previous_support = support_total
    return rows


def saturation_by_horizon_pair_rows(saturation: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, items in group_by(saturation, ("horizon_pair", "H_a", "H_b")).items():
        terminal = [int(float_or_zero(row.get("terminal_saturation_flag"))) for row in items]
        undercovered = [int(float_or_zero(row.get("horizon_pair_undercoverage_flag"))) for row in items]
        normal = [1 if row.get("allowed_interpretation_level") == "normal_horizon_response" else 0 for row in items]
        rows.append({
            "horizon_pair": key[0],
            "H_a": key[1],
            "H_b": key[2],
            "matrix_count": len(items),
            "terminal_saturation_fraction": mean(terminal) if terminal else 0.0,
            "undercoverage_fraction": mean(undercovered) if undercovered else 0.0,
            "normal_interpretation_fraction": mean(normal) if normal else 0.0,
            "largest_entry_mass_share_mean": mean([float_or_zero(row.get("largest_entry_mass_share")) for row in items]) if items else 0.0,
            "row_max_mass_share_mean": mean([float_or_zero(row.get("row_max_mass_share")) for row in items]) if items else 0.0,
            "column_max_mass_share_mean": mean([float_or_zero(row.get("column_max_mass_share")) for row in items]) if items else 0.0,
            "transport_entropy_mean": mean([float_or_zero(row.get("transport_entropy")) for row in items]) if items else 0.0,
        })
    return sorted(rows, key=lambda row: (float_or_zero(row.get("H_b")), float_or_zero(row.get("H_a"))))


def response_flag_rows(response_classification: list[dict[str, object]], saturation: list[dict[str, object]]) -> list[dict[str, object]]:
    saturation_by_matrix = {str(row.get("matrix_id", "")): row for row in saturation}
    rows: list[dict[str, object]] = []
    for row in response_classification:
        sat = saturation_by_matrix.get(str(row.get("matrix_id", "")), {})
        rows.append({
            "substrate_family": row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))),
            "substrate_variant": row.get("substrate_variant", substrate_variant_from_condition_id(row.get("condition_id", ""))),
            "condition_id": row.get("condition_id", ""),
            "actual_control_name": row.get("actual_control_name", ""),
            "mechanism_control_strength": row.get("mechanism_control_strength", ""),
            "probe_key": row.get("probe_key", ""),
            "flow_mode": row.get("flow_mode", ""),
            "horizon_pair": row.get("horizon_pair", ""),
            "response_class": row.get("response_class", ""),
            "response_flags": row.get("response_flags", ""),
            "mean_subspace_alignment": row.get("mean_subspace_alignment", ""),
            "spectral_mass_delta_fraction": row.get("spectral_mass_delta_fraction", ""),
            "transport_entropy_delta": row.get("transport_entropy_delta", ""),
            "perturbation_response_magnitude": row.get("perturbation_response_magnitude", ""),
            "allowed_interpretation_level": sat.get("allowed_interpretation_level", ""),
            "terminal_saturation_flag": sat.get("terminal_saturation_flag", ""),
        })
    return rows


def response_class_by_strength_and_horizon_rows(response_classification: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = ("substrate_family", "substrate_variant", "actual_control_name", "mechanism_control_strength", "probe_key", "flow_mode", "horizon_pair", "H_a", "H_b", "response_class")
    rows: list[dict[str, object]] = []
    for key, items in group_by(response_classification, keys).items():
        rows.append({
            "substrate_family": key[0],
            "substrate_variant": key[1],
            "perturbation_family": key[2],
            "perturbation_strength": key[3],
            "probe_key": key[4],
            "flow_mode": key[5],
            "horizon_pair": key[6],
            "H_a": key[7],
            "H_b": key[8],
            "response_class": key[9],
            "row_count": len(items),
            "mean_subspace_alignment_mean": mean([float_or_zero(row.get("mean_subspace_alignment")) for row in items]) if items else 0.0,
            "spectral_mass_delta_fraction_mean": mean([float_or_zero(row.get("spectral_mass_delta_fraction")) for row in items]) if items else 0.0,
            "transport_entropy_delta_mean": mean([float_or_zero(row.get("transport_entropy_delta")) for row in items]) if items else 0.0,
            "perturbation_response_magnitude_mean": mean([float_or_zero(row.get("perturbation_response_magnitude")) for row in items]) if items else 0.0,
        })
    return sorted(rows, key=lambda row: (
        str(row.get("substrate_family", "")),
        str(row.get("substrate_variant", "")),
        str(row.get("perturbation_family", "")),
        float_or_zero(row.get("perturbation_strength")),
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
        float_or_zero(row.get("H_b")),
        str(row.get("response_class", "")),
    ))


def horizon_response_threshold_rows(response_classification: list[dict[str, object]], saturation: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    keys = ("substrate_family", "substrate_variant", "actual_control_name", "mechanism_control_strength", "probe_key", "flow_mode")
    for key, items in group_by(response_classification, keys).items():
        ordered = sorted(items, key=lambda row: (float_or_zero(row.get("H_b")), float_or_zero(row.get("H_a"))))
        sat_items = sorted(
            [
                row for row in saturation
                if row.get("substrate_family") == key[0]
                and row.get("substrate_variant") == key[1]
                and row.get("actual_control_name") == key[2]
                and str(row.get("mechanism_control_strength")) == str(key[3])
                and row.get("probe_key") == key[4]
                and row.get("flow_mode") == key[5]
            ],
            key=lambda row: (float_or_zero(row.get("H_b")), float_or_zero(row.get("H_a"))),
        )
        rows.append({
            "substrate_family": key[0],
            "substrate_variant": key[1],
            "perturbation_family": key[2],
            "perturbation_strength": key[3],
            "probe_key": key[4],
            "flow_mode": key[5],
            "first_nonstable_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") != RESPONSE_CLASS_STABLE),
            "first_amplified_aligned_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_AMPLIFIED_ALIGNED),
            "first_weakened_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_WEAKENED),
            "first_rerouted_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_REROUTED),
            "first_reopened_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_REOPENS),
            "first_collapsed_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_COLLAPSES),
            "terminal_saturation_horizon": first_response_horizon(sat_items, lambda row: int(float_or_zero(row.get("terminal_saturation_flag"))) == 1),
            "latest_interpretable_horizon": latest_response_horizon(sat_items, lambda row: row.get("allowed_interpretation_level") == "normal_horizon_response"),
        })
    return sorted(rows, key=lambda row: (
        str(row.get("substrate_family", "")),
        str(row.get("substrate_variant", "")),
        str(row.get("perturbation_family", "")),
        float_or_zero(row.get("perturbation_strength")),
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
    ))


def response_diversity_rows(response_classification: list[dict[str, object]], saturation: list[dict[str, object]]) -> list[dict[str, object]]:
    context_keys = ("substrate_family", "substrate_variant", "actual_control_name", "mechanism_control_strength", "probe_key", "flow_mode")
    saturation_by_context = group_by(saturation, context_keys)
    rows: list[dict[str, object]] = []
    for key, items in group_by(response_classification, context_keys).items():
        interpretable = [row for row in items if is_interpretable_response(row.get("response_class"))]
        class_counts = Counter(str(row.get("response_class", "")) for row in interpretable if row.get("response_class"))
        class_set = set(class_counts)
        ordered = sorted(interpretable, key=lambda row: (float_or_zero(row.get("H_b")), float_or_zero(row.get("H_a"))))
        sat_items = saturation_by_context.get(key, [])
        terminal_flags = [int(float_or_zero(row.get("terminal_saturation_flag"))) for row in sat_items]
        undercoverage_flags = [int(float_or_zero(row.get("horizon_pair_undercoverage_flag"))) for row in sat_items]
        normal_rows = [row for row in sat_items if row.get("allowed_interpretation_level") == "normal_horizon_response"]
        diversity_score = response_diversity_score(class_set)
        rows.append({
            "substrate_family": key[0],
            "substrate_variant": key[1],
            "perturbation_family": key[2],
            "perturbation_strength": key[3],
            "probe_key": key[4],
            "flow_mode": key[5],
            "response_row_count": len(items),
            "interpretable_response_row_count": len(interpretable),
            "response_class_diversity_by_context": len(class_set),
            "response_class_counts_json": json.dumps(dict(sorted(class_counts.items())), sort_keys=True),
            "response_diversity_score": diversity_score,
            "first_nonstable_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") != RESPONSE_CLASS_STABLE),
            "first_amplified_aligned_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_AMPLIFIED_ALIGNED),
            "first_non_amplified_response_horizon": first_response_horizon(
                ordered,
                lambda row: row.get("response_class") not in {RESPONSE_CLASS_STABLE, RESPONSE_CLASS_AMPLIFIED_ALIGNED},
            ),
            "latest_interpretable_horizon": latest_response_horizon(normal_rows, lambda row: True),
            "terminal_saturation_fraction": mean(terminal_flags) if terminal_flags else 0.0,
            "undercoverage_fraction": mean(undercoverage_flags) if undercoverage_flags else 0.0,
            "dominant_response_class": class_counts.most_common(1)[0][0] if class_counts else "",
            "transport_viscosity_score": context_viscosity_score(interpretable, class_set),
            "transport_viscosity_read": context_viscosity_read(interpretable, class_set, terminal_flags, undercoverage_flags),
        })
    return sorted(rows, key=lambda row: (
        str(row.get("substrate_family")),
        str(row.get("substrate_variant")),
        str(row.get("perturbation_family")),
        float_or_zero(row.get("perturbation_strength")),
        str(row.get("probe_key")),
        str(row.get("flow_mode")),
    ))


def transport_viscosity_rows(
    response_classification: list[dict[str, object]],
    response_diversity: list[dict[str, object]],
    saturation: list[dict[str, object]],
) -> list[dict[str, object]]:
    diversity_by_context = {
        (row.get("substrate_family"), row.get("substrate_variant"), row.get("perturbation_family"), row.get("perturbation_strength"), row.get("probe_key"), row.get("flow_mode")): row
        for row in response_diversity
    }
    saturation_by_matrix = {str(row.get("matrix_id", "")): row for row in saturation}
    rows: list[dict[str, object]] = []
    for row in response_classification:
        context = diversity_by_context.get((
            row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))),
            row.get("substrate_variant", substrate_variant_from_condition_id(row.get("condition_id", ""))),
            row.get("actual_control_name"),
            row.get("mechanism_control_strength"),
            row.get("probe_key"),
            row.get("flow_mode"),
        ), {})
        sat = saturation_by_matrix.get(str(row.get("matrix_id", "")), {})
        alignment = float_or_zero(row.get("mean_subspace_alignment"))
        mass_delta = float_or_zero(row.get("spectral_mass_delta_fraction"))
        entropy_delta = float_or_zero(row.get("transport_entropy_delta"))
        subspace_rotation = max(0.0, 1.0 - alignment)
        score = row_viscosity_score(
            alignment=alignment,
            subspace_rotation=subspace_rotation,
            entropy_delta=entropy_delta,
            response_class=str(row.get("response_class", "")),
            context_diversity_score=float_or_zero(context.get("response_diversity_score")),
        )
        if int(float_or_zero(sat.get("terminal_saturation_flag"))):
            read = "terminal_saturation_limited"
        elif int(float_or_zero(sat.get("horizon_pair_undercoverage_flag"))) or not is_interpretable_response(row.get("response_class")):
            read = "underpowered_or_unresolved"
        elif str(row.get("response_class", "")) in DIFFERENTIATED_RESPONSE_CLASSES:
            read = "medium_viscosity_response_threshold" if score >= 0.35 else "low_viscosity_unstable_response"
        elif str(row.get("response_class", "")) in LOW_COMPLEXITY_RESPONSE_CLASSES and score >= 0.65:
            read = "high_viscosity_aligned_amplifier"
        else:
            read = "underpowered_or_unresolved"
        rows.append({
            "substrate_family": row.get("substrate_family", substrate_family_from_condition_id(row.get("condition_id", ""))),
            "substrate_variant": row.get("substrate_variant", substrate_variant_from_condition_id(row.get("condition_id", ""))),
            "condition_id": row.get("condition_id", ""),
            "probe_key": row.get("probe_key", ""),
            "flow_mode": row.get("flow_mode", ""),
            "horizon_pair": row.get("horizon_pair", ""),
            "H_a": row.get("H_a", ""),
            "H_b": row.get("H_b", ""),
            "perturbation_family": row.get("actual_control_name", ""),
            "perturbation_strength": row.get("mechanism_control_strength", ""),
            "mean_alignment": alignment,
            "mass_delta_fraction": mass_delta,
            "entropy_delta": entropy_delta,
            "subspace_rotation": subspace_rotation,
            "response_class": row.get("response_class", ""),
            "response_class_diversity_by_context": context.get("response_class_diversity_by_context", ""),
            "response_diversity_score": context.get("response_diversity_score", ""),
            "first_nonstable_horizon": context.get("first_nonstable_horizon", ""),
            "first_non_amplified_response_horizon": context.get("first_non_amplified_response_horizon", ""),
            "latest_interpretable_horizon": context.get("latest_interpretable_horizon", ""),
            "terminal_saturation_flag": sat.get("terminal_saturation_flag", ""),
            "horizon_pair_undercoverage_flag": sat.get("horizon_pair_undercoverage_flag", ""),
            "transport_viscosity_score": score,
            "transport_viscosity_read": read,
        })
    return rows


DIFFERENTIATED_RESPONSE_CLASSES = frozenset({
    RESPONSE_CLASS_COLLAPSES,
    RESPONSE_CLASS_WEAKENED,
    RESPONSE_CLASS_REROUTED,
    RESPONSE_CLASS_REOPENS,
})
LOW_COMPLEXITY_RESPONSE_CLASSES = frozenset({
    RESPONSE_CLASS_STABLE,
    RESPONSE_CLASS_AMPLIFIED_ALIGNED,
})


def response_diversity_score(response_classes: set[str]) -> float:
    interpretable = {value for value in response_classes if value and value not in MEASUREMENT_LIMIT_RESPONSE_CLASSES}
    if not interpretable:
        return 0.0
    return clamp01((len(interpretable) - 1) / 4.0)


def context_viscosity_score(items: list[dict[str, object]], response_classes: set[str]) -> float:
    if not items:
        return 0.0
    alignments = [float_or_zero(row.get("mean_subspace_alignment")) for row in items]
    entropy_pressure = [min(1.0, abs(float_or_zero(row.get("transport_entropy_delta"))) / 0.5) for row in items]
    differentiated_fraction = sum(1 for row in items if str(row.get("response_class", "")) in DIFFERENTIATED_RESPONSE_CLASSES) / max(1, len(items))
    diversity = response_diversity_score(response_classes)
    return clamp01(
        0.45 * mean(alignments)
        + 0.25 * (1.0 - diversity)
        + 0.15 * (1.0 - mean(entropy_pressure))
        + 0.15 * (1.0 - differentiated_fraction)
    )


def context_viscosity_read(
    items: list[dict[str, object]],
    response_classes: set[str],
    terminal_flags: list[int],
    undercoverage_flags: list[int],
) -> str:
    if terminal_flags and mean(terminal_flags) >= 0.50:
        return "terminal_saturation_limited"
    if undercoverage_flags and mean(undercoverage_flags) >= 0.50:
        return "underpowered_or_unresolved"
    if not items:
        return "underpowered_or_unresolved"
    interpretable = {value for value in response_classes if value and value not in MEASUREMENT_LIMIT_RESPONSE_CLASSES}
    if not interpretable:
        return "underpowered_or_unresolved"
    differentiated = interpretable & DIFFERENTIATED_RESPONSE_CLASSES
    if not differentiated and interpretable <= LOW_COMPLEXITY_RESPONSE_CLASSES:
        return "high_viscosity_aligned_amplifier"
    if RESPONSE_CLASS_AMPLIFIED_ALIGNED in interpretable and differentiated:
        return "medium_viscosity_response_threshold"
    if len(differentiated) >= 2 or len(interpretable) >= 4:
        return "low_viscosity_unstable_response"
    if RESPONSE_CLASS_CONTROL_EQUIVALENT in interpretable and len(interpretable) <= 2:
        return "underpowered_or_unresolved"
    return "medium_viscosity_response_threshold"


def row_viscosity_score(
    *,
    alignment: float,
    subspace_rotation: float,
    entropy_delta: float,
    response_class: str,
    context_diversity_score: float,
) -> float:
    entropy_component = 1.0 - min(1.0, abs(entropy_delta) / 0.5)
    differentiated_component = 0.0 if response_class in DIFFERENTIATED_RESPONSE_CLASSES else 1.0
    return clamp01(
        0.45 * alignment
        + 0.20 * (1.0 - clamp01(subspace_rotation))
        + 0.15 * entropy_component
        + 0.10 * (1.0 - clamp01(context_diversity_score))
        + 0.10 * differentiated_component
    )


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def first_response_horizon(rows: list[dict[str, object]], predicate: object) -> str:
    for row in rows:
        if predicate(row):  # type: ignore[operator]
            return str(row.get("horizon_pair", ""))
    return ""


def latest_response_horizon(rows: list[dict[str, object]], predicate: object) -> str:
    out = ""
    for row in rows:
        if predicate(row):  # type: ignore[operator]
            out = str(row.get("horizon_pair", ""))
    return out


def context_recommendation_rows(
    summary: list[dict[str, object]],
    matched_marginal: list[dict[str, object]],
    response_classification: list[dict[str, object]],
) -> list[dict[str, object]]:
    context_keys = ("substrate_family", "substrate_variant", "probe_key", "flow_mode", "source_horizon_band", "target_horizon_band", "H_a", "H_b")
    summary_by_context = group_by(summary, context_keys)
    marginal_by_context = group_by(matched_marginal, context_keys)
    response_by_context = group_by(response_classification, context_keys)
    all_contexts = set(summary_by_context) | set(marginal_by_context) | set(response_by_context)
    rows: list[dict[str, object]] = []
    for key in sorted(all_contexts, key=lambda item: tuple(str(part) for part in item)):
        matrix_rows = summary_by_context.get(key, [])
        marginal_rows = marginal_by_context.get(key, [])
        response_rows = response_by_context.get(key, [])
        coverage_values = [float_or_zero(row.get("coverage")) for row in matrix_rows]
        interpretable_responses = [
            row for row in response_rows
            if is_interpretable_response(row.get("response_class"))
        ]
        response_counts = Counter(str(row.get("response_class", "")) for row in interpretable_responses)
        passed_families = {
            str(row.get("null_family", ""))
            for row in marginal_rows
            if row.get("summary_read") == "detector_null_separates"
        }
        required_families = set(MARGINAL_MATCHED_NULL_FAMILIES)
        matched_all = required_families <= passed_families
        coverage_min = min(coverage_values) if coverage_values else 0.0
        coverage_mean = mean(coverage_values) if coverage_values else 0.0
        dominant_response = response_counts.most_common(1)[0][0] if response_counts else ""
        if coverage_min < 0.80:
            context_read = "transport_matrix_undercovered"
            recommendation = "repair_or_reduce_matrix_resolution"
        elif matched_all and interpretable_responses:
            context_read = "matched_marginal_separates_interpretable"
            recommendation = "candidate_for_context_narrowing"
        elif passed_families:
            context_read = "matched_marginal_mixed"
            recommendation = "inspect_context_before_scaling"
        elif response_rows:
            context_read = "response_only_no_matched_marginal_separation"
            recommendation = "measurement_limits_or_fixture_expansion"
        else:
            context_read = "context_underpowered"
            recommendation = "increase_context_rows_or_repair"
        rows.append({
            "substrate_family": key[0],
            "substrate_variant": key[1],
            "probe_key": key[2],
            "flow_mode": key[3],
            "source_horizon_band": key[4],
            "target_horizon_band": key[5],
            "H_a": key[6],
            "H_b": key[7],
            "horizon_pair": f"{key[6]}->{key[7]}",
            "matrix_count": len(matrix_rows),
            "coverage_mean": coverage_mean,
            "coverage_min": coverage_min,
            "matched_marginal_families_passed": len(required_families & passed_families),
            "matched_marginal_families_required": len(required_families),
            "matched_marginal_all_families_passed": int(matched_all),
            "response_rows": len(response_rows),
            "response_interpretable_rows": len(interpretable_responses),
            "dominant_response_class": dominant_response,
            "context_read": context_read,
            "context_recommendation": recommendation,
            "context_priority_score": context_priority_score(coverage_mean, matched_all, len(required_families & passed_families), len(interpretable_responses)),
        })
    return sorted(rows, key=lambda row: float_or_zero(row.get("context_priority_score")), reverse=True)


def aggregate_context_summary_rows(rows: list[dict[str, object]], fields: tuple[str, ...], label: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for key, items in group_by(rows, fields).items():
        coverage = [float_or_zero(row.get("coverage_min")) for row in items]
        full_pass = [int(float_or_zero(row.get("matched_marginal_all_families_passed"))) for row in items]
        any_pass = [1 if float_or_zero(row.get("matched_marginal_families_passed")) > 0 else 0 for row in items]
        interpretable = [1 if float_or_zero(row.get("response_interpretable_rows")) > 0 else 0 for row in items]
        response_counts = Counter(str(row.get("dominant_response_class", "")) for row in items if row.get("dominant_response_class"))
        summary_read = "mixed_or_control_equivalent"
        if full_pass and sum(full_pass) == len(items) and any(interpretable):
            summary_read = "matched_marginal_separates"
        elif any(full_pass):
            summary_read = "context_specific_separation"
        elif any(any_pass):
            summary_read = "partial_matched_marginal_separation"
        out.append({
            label: "|".join(str(part) for part in key),
            "context_count": len(items),
            "coverage_min": min(coverage) if coverage else 0.0,
            "coverage_mean": mean(coverage) if coverage else 0.0,
            "matched_marginal_full_pass_contexts": sum(full_pass),
            "matched_marginal_any_pass_contexts": sum(any_pass),
            "response_interpretable_contexts": sum(interpretable),
            "dominant_response_class": response_counts.most_common(1)[0][0] if response_counts else "",
            "summary_read": summary_read,
        })
    return sorted(out, key=lambda row: (float_or_zero(row.get("matched_marginal_full_pass_contexts")), float_or_zero(row.get("coverage_mean"))), reverse=True)


def context_priority_score(coverage_mean: float, matched_all: bool, marginal_family_count: int, interpretable_count: int) -> float:
    return coverage_mean + (10.0 if matched_all else 0.0) + marginal_family_count + min(5, interpretable_count) / 10.0


def detector_null_gate_rows(summary: list[dict[str, object]], matrices: list[TransportMatrix], args: argparse.Namespace, fixture_results: list[dict[str, object]]) -> list[dict[str, object]]:
    structure_required = [
        row for row in summary
        if row.get("null_category") == "structure_destroying_detector_null"
        and row.get("observed_statistic") in set(DETECTOR_STATISTICS)
    ]
    marginal_required = [
        row for row in summary
        if row.get("null_category") == "marginal_matched_detector_null"
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    replicate_powered = args.null_replicates >= 3
    structure_pass = any(row.get("summary_read") == "detector_null_separates" for row in structure_required)
    required_marginal_families = set(MARGINAL_MATCHED_NULL_FAMILIES)
    marginal_families_passed = {
        str(row.get("null_family", ""))
        for row in marginal_required
        if row.get("summary_read") == "detector_null_separates"
    }
    marginal_pass = required_marginal_families <= marginal_families_passed
    marginal_observed = f"{len(required_marginal_families & marginal_families_passed)}/{len(required_marginal_families)} families_passed"
    fixture_required = bool(fixture_results)
    fixture_pass = bool(fixture_results) and all(int(float_or_zero(row.get("passed"))) for row in fixture_results)
    adequate_coverage = any(
        matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) >= 0.80
        for matrix in matrices
    )
    return [
        {
            "gate_id": "G0",
            "gate_name": "horizon_transport_matrix_coverage",
            "required": 1,
            "passed": int(adequate_coverage),
            "threshold": "any matrix coverage >= 0.80",
            "observed": max((matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) for matrix in matrices), default=0.0),
            "blocking_reason": "" if adequate_coverage else "transport_matrix_undercovered",
        },
        {
            "gate_id": "G1",
            "gate_name": "detector_null_sections_separate",
            "required": 1,
            "passed": 1,
            "threshold": "detector null outputs separate from perturbation outputs",
            "observed": "separate_outputs_written",
            "blocking_reason": "",
        },
        {
            "gate_id": "G2",
            "gate_name": "structure_detector_null_separation",
            "required": 1,
            "passed": int(structure_pass and replicate_powered),
            "threshold": f"at least one required structure null statistic pass_fraction >= {args.detector_null_min_pass_fraction}",
            "observed": "passed" if structure_pass and replicate_powered else "underpowered" if structure_pass and not replicate_powered else "control_equivalent",
            "blocking_reason": "" if structure_pass and replicate_powered else "detector_null_replicates_underpowered" if structure_pass and not replicate_powered else "transport_detector_nulls_control_equivalent",
        },
        {
            "gate_id": "G3",
            "gate_name": "detector_null_replicate_power",
            "required": 1,
            "passed": int(replicate_powered),
            "threshold": "null_replicates >= 3",
            "observed": args.null_replicates,
            "blocking_reason": "" if replicate_powered else "detector_null_replicates_underpowered",
        },
        {
            "gate_id": "G4",
            "gate_name": "matched_marginal_detector_null_separation",
            "required": 1,
            "passed": int(marginal_pass and replicate_powered),
            "threshold": "marginal_residual_fraction separates from row, column, and bimarginal matched null families",
            "observed": marginal_observed if replicate_powered else "underpowered",
            "blocking_reason": "" if marginal_pass and replicate_powered else "detector_null_replicates_underpowered" if marginal_pass and not replicate_powered else "marginal_matched_nulls_control_equivalent",
        },
        {
            "gate_id": "G5",
            "gate_name": "synthetic_fixture_contract",
            "required": int(fixture_required),
            "passed": int(fixture_pass),
            "threshold": "all fixture expectations pass when fixture smoke is enabled",
            "observed": f"{sum(int(float_or_zero(row.get('passed'))) for row in fixture_results)}/{len(fixture_results)}" if fixture_required else "not_run",
            "blocking_reason": "" if fixture_pass or not fixture_required else "synthetic_fixture_contract_failed",
        },
    ]


def perturbation_response_rows(
    matrices: list[TransportMatrix],
    null_gates: list[dict[str, object]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    baseline_by_view = {
        response_view_key(matrix): matrix
        for matrix in matrices
        if matrix.key.actual_control_name == BASELINE_CONTROL
    }
    detector_null_status = "detector_nulls_passed" if required_detector_gates_passed(null_gates) else "detector_nulls_not_passed"
    manifest: list[dict[str, object]] = []
    summary: list[dict[str, object]] = []
    classes: list[dict[str, object]] = []
    for matrix in matrices:
        if matrix.key.actual_control_name == BASELINE_CONTROL:
            continue
        baseline = baseline_by_view.get(response_view_key(matrix))
        tax = intervention_taxonomy(matrix.key)
        manifest.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            **tax,
            "perturbation_status": "baseline_available" if baseline else "baseline_missing",
        })
        response = response_payload(baseline, matrix, args)
        response_class = classify_response(response)
        common = {**key_row(matrix.key), "matrix_id": matrix.matrix_id, **tax, **response, "detector_null_status": detector_null_status}
        summary.append(common)
        classes.append({**common, "response_class": response_class, "allowed_claim_level": tax["allowed_claim_level"]})
    return manifest, summary, classes


def required_detector_gates_passed(null_gates: list[dict[str, object]]) -> bool:
    required = {
        "structure_detector_null_separation",
        "detector_null_replicate_power",
        "matched_marginal_detector_null_separation",
    }
    passed = {
        str(row.get("gate_name", ""))
        for row in null_gates
        if int(float_or_zero(row.get("passed")))
    }
    return required <= passed


def fixture_result_rows(null_anatomy: list[dict[str, object]], response_classification: list[dict[str, object]]) -> list[dict[str, object]]:
    fixture_nulls = [row for row in null_anatomy if str(row.get("condition_id", "")).startswith("fixture_")]
    fixture_responses = [row for row in response_classification if str(row.get("condition_id", "")).startswith("fixture_")]
    if not fixture_nulls and not fixture_responses:
        return []

    block_rows = [
        row for row in fixture_nulls
        if row.get("condition_id") == "fixture_block_transport_signal"
        and row.get("null_family") in MARGINAL_MATCHED_NULL_FAMILIES
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    fakeout_rows = [
        row for row in fixture_nulls
        if row.get("condition_id") == "fixture_marginal_fakeout"
        and row.get("null_family") == "row_column_marginal_matched_transport_null"
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    corridor_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_corridor_stable_response"
    ]
    trap_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_trap_collapse_response"
    ]
    amplified_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_amplified_aligned_response"
    ]
    weakened_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_weakened_response"
    ]
    rerouted_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_rerouted_response"
    ]
    reopens_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_reopens_response"
    ]

    block_pass = any(int(float_or_zero(row.get("null_gate_passed"))) for row in block_rows)
    fakeout_pass = bool(fakeout_rows) and not any(int(float_or_zero(row.get("null_gate_passed"))) for row in fakeout_rows)
    corridor_pass = any(row.get("response_class") == RESPONSE_CLASS_STABLE for row in corridor_rows)
    trap_pass = any(row.get("response_class") == RESPONSE_CLASS_COLLAPSES for row in trap_rows)
    amplified_pass = any(row.get("response_class") == RESPONSE_CLASS_AMPLIFIED_ALIGNED for row in amplified_rows)
    weakened_pass = any(row.get("response_class") == RESPONSE_CLASS_WEAKENED for row in weakened_rows)
    rerouted_pass = any(row.get("response_class") == RESPONSE_CLASS_REROUTED for row in rerouted_rows)
    reopens_pass = any(row.get("response_class") == RESPONSE_CLASS_REOPENS for row in reopens_rows)

    return [
        {
            "fixture_id": "block_transport_signal",
            "fixture_question": "does true association beyond marginals separate from matched marginal nulls",
            "expected_behavior": "marginal_residual_fraction passes at least one matched marginal null",
            "observed": observed_fixture_read(block_rows, "null_gate_passed"),
            "passed": int(block_pass),
            "source_table": "horizon_transport_detector_null_anatomy.csv",
        },
        {
            "fixture_id": "marginal_fakeout",
            "fixture_question": "does a pure row/column mass fakeout fail the bimarginal matched null",
            "expected_behavior": "marginal_residual_fraction does not pass row_column_marginal_matched_transport_null",
            "observed": observed_fixture_read(fakeout_rows, "null_gate_passed"),
            "passed": int(fakeout_pass),
            "source_table": "horizon_transport_detector_null_anatomy.csv",
        },
        {
            "fixture_id": "corridor_stable_response",
            "fixture_question": "does a tiny corridor perturbation stay in the stable response class",
            "expected_behavior": RESPONSE_CLASS_STABLE,
            "observed": observed_fixture_read(corridor_rows, "response_class"),
            "passed": int(corridor_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "trap_collapse_response",
            "fixture_question": "does a trap collapse perturbation enter the collapse response class",
            "expected_behavior": RESPONSE_CLASS_COLLAPSES,
            "observed": observed_fixture_read(trap_rows, "response_class"),
            "passed": int(trap_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "amplified_aligned_response",
            "fixture_question": "does aligned mass growth enter the amplified-aligned response class",
            "expected_behavior": RESPONSE_CLASS_AMPLIFIED_ALIGNED,
            "observed": observed_fixture_read(amplified_rows, "response_class"),
            "passed": int(amplified_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "weakened_response",
            "fixture_question": "does non-collapsing mass loss enter the weakened response class",
            "expected_behavior": RESPONSE_CLASS_WEAKENED,
            "observed": observed_fixture_read(weakened_rows, "response_class"),
            "passed": int(weakened_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "rerouted_response",
            "fixture_question": "does low-alignment transport reorganization enter the rerouted response class",
            "expected_behavior": RESPONSE_CLASS_REROUTED,
            "observed": observed_fixture_read(rerouted_rows, "response_class"),
            "passed": int(rerouted_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "reopens_response",
            "fixture_question": "does entropy-increasing transport spread enter the reopens response class",
            "expected_behavior": RESPONSE_CLASS_REOPENS,
            "observed": observed_fixture_read(reopens_rows, "response_class"),
            "passed": int(reopens_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
    ]


def observed_fixture_read(rows: list[dict[str, object]], field: str) -> str:
    if not rows:
        return "missing"
    counts = Counter(str(row.get(field, "")) for row in rows)
    return "; ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


def response_payload(baseline: TransportMatrix | None, matrix: TransportMatrix, args: argparse.Namespace) -> dict[str, object]:
    if baseline is None:
        return {"response_status": "baseline_missing"}
    common_rows = sorted(set(baseline.row_items) & set(matrix.row_items))
    common_cols = sorted(set(baseline.column_items) & set(matrix.column_items))
    if len(common_rows) < 2 or len(common_cols) < 2:
        return {"response_status": "insufficient_common_transport_items", "common_row_items": len(common_rows), "common_column_items": len(common_cols)}
    base_sub = sub_transport_matrix(baseline, common_rows, common_cols)
    pert_sub = sub_transport_matrix(matrix, common_rows, common_cols)
    b_u, b_s, b_v = svd_parts(base_sub)
    p_u, p_s, p_v = svd_parts(pert_sub)
    k = min(args.top_k, b_u.shape[1], p_u.shape[1], b_v.shape[1], p_v.shape[1])
    left_alignment = subspace_alignment(b_u[:, :k], p_u[:, :k]) if k else 0.0
    right_alignment = subspace_alignment(b_v[:, :k], p_v[:, :k]) if k else 0.0
    base_mass = float(np.sum(b_s))
    pert_mass = float(np.sum(p_s))
    return {
        "response_status": "computed",
        "common_row_items": len(common_rows),
        "common_column_items": len(common_cols),
        "left_subspace_alignment": left_alignment,
        "right_subspace_alignment": right_alignment,
        "mean_subspace_alignment": (left_alignment + right_alignment) / 2.0,
        "baseline_spectral_mass": base_mass,
        "perturbation_spectral_mass": pert_mass,
        "spectral_mass_delta_fraction": (pert_mass - base_mass) / max(1e-12, base_mass),
        "baseline_transport_entropy": entropy_from_values(base_sub.flatten()),
        "perturbation_transport_entropy": entropy_from_values(pert_sub.flatten()),
        "transport_entropy_delta": entropy_from_values(pert_sub.flatten()) - entropy_from_values(base_sub.flatten()),
        "perturbation_response_magnitude": float(np.linalg.norm(pert_sub - base_sub) / max(1e-12, np.linalg.norm(base_sub))),
        "response_flags": response_flags(
            left_alignment,
            right_alignment,
            (pert_mass - base_mass) / max(1e-12, base_mass),
            entropy_from_values(pert_sub.flatten()) - entropy_from_values(base_sub.flatten()),
            float(np.linalg.norm(pert_sub - base_sub) / max(1e-12, np.linalg.norm(base_sub))),
        ),
    }


def horizon_pair_alignment_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    baseline = [matrix for matrix in matrices if matrix.key.actual_control_name == BASELINE_CONTROL]
    rows: list[dict[str, object]] = []
    for key, items in group_matrices(baseline, ("probe_key", "flow_mode")).items():
        for left in items:
            for right in items:
                if left.matrix_id >= right.matrix_id:
                    continue
                common_rows = sorted(set(left.row_items) & set(right.row_items))
                common_cols = sorted(set(left.column_items) & set(right.column_items))
                if len(common_rows) < 2 or len(common_cols) < 2:
                    continue
                left_sub = sub_transport_matrix(left, common_rows, common_cols)
                right_sub = sub_transport_matrix(right, common_rows, common_cols)
                l_u, _l_s, l_v = svd_parts(left_sub)
                r_u, _r_s, r_v = svd_parts(right_sub)
                k = min(args.top_k, l_u.shape[1], r_u.shape[1], l_v.shape[1], r_v.shape[1])
                rows.append({
                    "probe_key": key[0],
                    "flow_mode": key[1],
                    "left_matrix_id": left.matrix_id,
                    "right_matrix_id": right.matrix_id,
                    "left_horizon_pair": f"{left.key.H_a}->{left.key.H_b}",
                    "right_horizon_pair": f"{right.key.H_a}->{right.key.H_b}",
                    "left_source_horizon_band": left.key.source_horizon_band,
                    "left_target_horizon_band": left.key.target_horizon_band,
                    "right_source_horizon_band": right.key.source_horizon_band,
                    "right_target_horizon_band": right.key.target_horizon_band,
                    "left_subspace_alignment": subspace_alignment(l_u[:, :k], r_u[:, :k]) if k else 0.0,
                    "right_subspace_alignment": subspace_alignment(l_v[:, :k], r_v[:, :k]) if k else 0.0,
                    "aligned_row_items": len(common_rows),
                    "aligned_column_items": len(common_cols),
                })
    return rows


def write_sparse_transport_matrix_npz(path: Path, matrices: list[TransportMatrix]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    matrix_index_parts: list[np.ndarray] = []
    row_index_parts: list[np.ndarray] = []
    column_index_parts: list[np.ndarray] = []
    mass_parts: list[np.ndarray] = []
    matrix_ids: list[str] = []
    row_counts: list[int] = []
    column_counts: list[int] = []
    for matrix_number, matrix in enumerate(matrices):
        matrix_ids.append(matrix.matrix_id)
        row_counts.append(len(matrix.row_items))
        column_counts.append(len(matrix.column_items))
        row_indices, column_indices = np.nonzero(matrix.matrix > 0)
        if row_indices.size == 0:
            continue
        matrix_index_parts.append(np.full(row_indices.size, matrix_number, dtype=np.int32))
        row_index_parts.append(row_indices.astype(np.int32, copy=False))
        column_index_parts.append(column_indices.astype(np.int32, copy=False))
        mass_parts.append(matrix.matrix[row_indices, column_indices].astype(np.float64, copy=False))
    np.savez_compressed(
        path,
        encoding_version=string_array(["horizon_transport_sparse_v1"]),
        matrix_id=string_array(matrix_ids),
        row_count=np.asarray(row_counts, dtype=np.int32),
        column_count=np.asarray(column_counts, dtype=np.int32),
        matrix_index=concat_or_empty(matrix_index_parts, np.int32),
        row_index=concat_or_empty(row_index_parts, np.int32),
        column_index=concat_or_empty(column_index_parts, np.int32),
        transport_mass=concat_or_empty(mass_parts, np.float64),
    )


def write_sparse_raw_state_frontier_npz(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    valid = [
        row for row in rows
        if row.get("state_id") not in (None, "") and row.get("raw_state_sample_status", "ok") != "error"
    ]
    context_keys = sorted({raw_state_sparse_context_key(row) for row in valid}, key=raw_state_sparse_context_sort_key)
    state_ordinals: dict[str, int] = {}
    for row in valid:
        state = str(row.get("state_id", ""))
        state_ordinals[state] = min(state_ordinals.get(state, 1_000_000_000), int_or_default(row.get("state_index"), 1_000_000_000))
    state_ids = sorted(state_ordinals, key=lambda state: (state_ordinals[state], state))
    context_index = {key: index for index, key in enumerate(context_keys)}
    state_index = {state: index for index, state in enumerate(state_ids)}
    counts: Counter[tuple[int, int]] = Counter()
    frontier_sizes: dict[tuple[int, int], int] = {}
    for row in valid:
        key = raw_state_sparse_context_key(row)
        state = str(row.get("state_id", ""))
        item_key = (state_index[state], context_index[key])
        counts[item_key] += 1
        frontier_sizes[item_key] = max(frontier_sizes.get(item_key, 0), int_or_default(row.get("frontier_size"), 0))
    state_parts: list[int] = []
    context_parts: list[int] = []
    count_parts: list[int] = []
    frontier_size_parts: list[int] = []
    for (state_number, context_number), count in sorted(counts.items(), key=lambda item: (item[0][1], item[0][0])):
        state_parts.append(state_number)
        context_parts.append(context_number)
        count_parts.append(count)
        frontier_size_parts.append(frontier_sizes.get((state_number, context_number), 0))
    np.savez_compressed(
        path,
        encoding_version=string_array(["raw_state_frontier_sparse_v1"]),
        state_id=string_array(state_ids),
        state_ordinal=np.asarray([state_ordinals[state] for state in state_ids], dtype=np.int32),
        context_label=string_array([raw_state_sparse_context_label(key) for key in context_keys]),
        context_condition_id=string_array([key[0] for key in context_keys]),
        context_actual_control_name=string_array([key[1] for key in context_keys]),
        context_mechanism_control_strength=string_array([key[2] for key in context_keys]),
        context_probe_key=string_array([key[3] for key in context_keys]),
        context_job_id=string_array([key[4] for key in context_keys]),
        context_seed=np.asarray([int_or_default(key[5], 0) for key in context_keys], dtype=np.int64),
        context_start_index=np.asarray([int_or_default(key[6], 0) for key in context_keys], dtype=np.int32),
        context_horizon=np.asarray([int_or_default(key[7], 0) for key in context_keys], dtype=np.int32),
        state_index=np.asarray(state_parts, dtype=np.int32),
        context_index=np.asarray(context_parts, dtype=np.int32),
        state_presence_count=np.asarray(count_parts, dtype=np.int32),
        frontier_size=np.asarray(frontier_size_parts, dtype=np.int32),
    )


def raw_state_sparse_context_key(row: dict[str, object]) -> tuple[str, str, str, str, str, str, str, str]:
    return (
        str(row.get("condition_id", "")),
        str(row.get("actual_control_name", "")),
        str(row.get("mechanism_control_strength", "")),
        str(row.get("probe_key", "")),
        str(row.get("job_id", "")),
        str(row.get("seed", "")),
        str(row.get("start_index", "")),
        str(row.get("H", "")),
    )


def raw_state_sparse_context_sort_key(key: tuple[str, str, str, str, str, str, str, str]) -> tuple[str, float, str, str, int, int]:
    return (key[1], float_or_zero(key[2]), key[3], key[4], int_or_default(key[6], 0), int_or_default(key[7], 0))


def raw_state_sparse_context_label(key: tuple[str, str, str, str, str, str, str, str]) -> str:
    return "|".join((key[1], key[2], key[3], f"seed{key[5]}", f"start{key[6]}", f"H{key[7]}"))


def concat_or_empty(parts: list[np.ndarray], dtype: object) -> np.ndarray:
    if not parts:
        return np.asarray([], dtype=dtype)
    return np.concatenate(parts).astype(dtype, copy=False)


def string_array(values: list[str]) -> np.ndarray:
    lengths = [len(str(value)) for value in values]
    width = max([1, *lengths])
    return np.asarray([str(value) for value in values], dtype=f"<U{width}")


def int_or_default(value: object, default: int) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def write_outputs(
    out_dir: Path,
    outputs: dict[str, list[dict[str, object]]],
    matrices: list[TransportMatrix],
    errors: list[dict[str, object]],
    checkpoints: list[dict[str, object]],
    status: dict[str, object],
    started: float,
) -> None:
    write_csv(out_dir / "horizon_transport_matrix_manifest.csv", outputs["manifest"])
    write_csv(out_dir / "horizon_transport_matrix_entries.csv", outputs["matrix_entries"])
    matrix_sparse_path = out_dir / "horizon_transport_matrix_sparse.npz"
    write_sparse_transport_matrix_npz(matrix_sparse_path, matrices)
    write_csv(out_dir / "horizon_transport_raw_state_frontier_samples.csv", outputs["raw_state_samples"])
    raw_state_sparse_path = out_dir / "horizon_transport_raw_state_frontier_sparse.npz"
    write_sparse_raw_state_frontier_npz(raw_state_sparse_path, outputs["raw_state_samples"])
    write_csv(out_dir / "substrate_family_manifest.csv", outputs["substrate_manifest"])
    write_csv(out_dir / "substrate_family_variant_manifest.csv", outputs["substrate_variant_manifest"])
    write_csv(out_dir / "transition_energy_family_summary.csv", outputs["transition_family_summary"])
    write_csv(out_dir / "transition_energy_parameter_summary.csv", outputs["transition_parameter_summary"])
    write_csv(out_dir / "substrate_capacity_by_family.csv", outputs["substrate_capacity"])
    write_csv(out_dir / "substrate_capacity_by_family_variant.csv", outputs["substrate_capacity_variant"])
    write_csv(out_dir / "substrate_generation_diagnostics.csv", outputs["substrate_generation"])
    write_csv(out_dir / "horizon_transport_row_item_manifest.csv", outputs["row_items"])
    write_csv(out_dir / "horizon_transport_column_item_manifest.csv", outputs["column_items"])
    write_csv(out_dir / "horizon_transport_coverage.csv", outputs["coverage"])
    write_csv(out_dir / "horizon_transport_matrix_summary.csv", outputs["summary"])
    write_csv(out_dir / "horizon_transport_svd_summary.csv", outputs["svd"])
    write_csv(out_dir / "horizon_transport_subspace_alignment.csv", outputs["subspace_alignment"])
    write_csv(out_dir / "horizon_transport_participation_summary.csv", outputs["participation"])
    write_csv(out_dir / "horizon_transport_entropy_summary.csv", outputs["entropy"])
    write_csv(out_dir / "horizon_transport_detector_null_summary.csv", outputs["null_summary"])
    write_csv(out_dir / "horizon_transport_detector_null_anatomy.csv", outputs["null_anatomy"])
    write_csv(out_dir / "horizon_transport_detector_null_gate_results.csv", outputs["null_gates"])
    write_csv(out_dir / "horizon_transport_matched_marginal_summary.csv", outputs["matched_marginal"])
    write_csv(out_dir / "horizon_transport_fixture_results.csv", outputs["fixture_results"])
    write_csv(out_dir / "horizon_transport_perturbation_manifest.csv", outputs["perturb_manifest"])
    write_csv(out_dir / "horizon_transport_response_profile_summary.csv", outputs["response_summary"])
    write_csv(out_dir / "horizon_transport_response_classification.csv", outputs["response_classification"])
    write_csv(out_dir / "horizon_transport_response_flags.csv", outputs["response_flags"])
    write_csv(out_dir / "response_class_by_strength_and_horizon_pair.csv", outputs["response_by_strength_horizon"])
    write_csv(out_dir / "horizon_response_threshold_table.csv", outputs["threshold_table"])
    write_csv(out_dir / "horizon_transport_terminal_saturation_summary.csv", outputs["saturation"])
    write_csv(out_dir / "horizon_transport_saturation_by_horizon_pair.csv", outputs["saturation_by_horizon_pair"])
    write_csv(out_dir / "horizon_transport_response_fixture_summary.csv", outputs["response_fixture_summary"])
    write_csv(out_dir / "horizon_transport_viscosity_summary.csv", outputs["viscosity"])
    write_csv(out_dir / "horizon_transport_response_diversity_summary.csv", outputs["response_diversity"])
    write_csv(out_dir / "horizon_transport_by_probe_summary.csv", outputs["by_probe"])
    write_csv(out_dir / "horizon_transport_by_flow_mode_summary.csv", outputs["by_flow_mode"])
    write_csv(out_dir / "horizon_transport_by_horizon_pair_summary.csv", outputs["by_horizon_pair"])
    write_csv(out_dir / "horizon_transport_by_substrate_family_summary.csv", outputs["by_substrate"])
    write_csv(out_dir / "horizon_transport_by_substrate_family_variant_summary.csv", outputs["by_substrate_variant"])
    write_csv(out_dir / "response_by_substrate_family.csv", outputs["response_by_substrate"])
    write_csv(out_dir / "response_by_substrate_family_variant.csv", outputs["response_by_substrate_variant"])
    write_csv(out_dir / "response_by_budget_kind.csv", outputs["response_by_budget"])
    write_csv(out_dir / "response_by_potential_smoothness.csv", outputs["response_by_potential_smoothness"])
    write_csv(out_dir / "response_by_potential_beta.csv", outputs["response_by_potential_beta"])
    write_csv(out_dir / "response_by_asymmetry_family.csv", outputs["response_by_substrate"])
    write_csv(out_dir / "response_by_asymmetry_variant.csv", outputs["response_by_substrate_variant"])
    write_csv(out_dir / "response_by_directional_alpha.csv", outputs["response_by_directional_alpha"])
    write_csv(out_dir / "response_by_asymmetry_field_smoothness.csv", outputs["response_by_asymmetry_field_smoothness"])
    write_csv(out_dir / "response_by_macro_invariant_kind.csv", outputs["response_by_macro_invariant_kind"])
    write_csv(out_dir / "response_by_macro_invariant_beta.csv", outputs["response_by_macro_invariant_beta"])
    write_csv(out_dir / "selected_edge_overlap_by_beta.csv", outputs["selected_edge_overlap_by_beta"])
    write_csv(out_dir / "max_entropy_constraint_manifest.csv", outputs["max_entropy_constraint_manifest"])
    write_csv(out_dir / "max_entropy_marginal_match_summary.csv", outputs["max_entropy_marginal_match_summary"])
    write_csv(out_dir / "max_entropy_sampler_diagnostics.csv", outputs["max_entropy_sampler_diagnostics"])
    write_csv(out_dir / "max_entropy_edge_match_to_calibration.csv", outputs["max_entropy_edge_match_to_calibration"])
    write_csv(out_dir / "response_by_max_entropy_family.csv", outputs["response_by_max_entropy_family"])
    write_csv(out_dir / "response_by_equivalent_beta_target.csv", outputs["response_by_equivalent_beta_target"])
    write_csv(out_dir / "paired_baseline_availability_by_max_entropy_variant.csv", outputs["paired_baseline_availability_by_max_entropy_variant"])
    write_csv(out_dir / "response_by_alpha_beta_pair.csv", outputs["response_by_alpha_beta_pair"])
    write_csv(out_dir / "matched_null_pass_by_asymmetry_family.csv", outputs["matched_by_substrate"])
    write_csv(out_dir / "matched_null_pass_by_asymmetry_variant.csv", outputs["matched_by_substrate_variant"])
    write_csv(out_dir / "aligned_amplification_by_substrate_family.csv", outputs["aligned_by_substrate"])
    write_csv(out_dir / "response_diversity_by_substrate_family.csv", outputs["diversity_by_substrate"])
    write_csv(out_dir / "response_diversity_by_substrate_family_variant.csv", outputs["diversity_by_substrate_variant"])
    write_csv(out_dir / "transport_viscosity_by_substrate_family.csv", outputs["viscosity_by_substrate"])
    write_csv(out_dir / "transport_viscosity_by_substrate_family_variant.csv", outputs["viscosity_by_substrate_variant"])
    write_csv(out_dir / "matched_null_pass_by_substrate_family.csv", outputs["matched_by_substrate"])
    write_csv(out_dir / "matched_null_pass_by_substrate_family_variant.csv", outputs["matched_by_substrate_variant"])
    write_csv(out_dir / "horizon_transport_context_recommendation.csv", outputs["context_recommendation"])
    status.update(decision_fields(outputs, status))
    status["matrix_count"] = len(outputs["manifest"])
    status["matrix_entry_rows"] = len(outputs["matrix_entries"])
    status["matrix_sparse_npz_bytes"] = matrix_sparse_path.stat().st_size if matrix_sparse_path.exists() else 0
    status["raw_state_sample_rows"] = len(outputs["raw_state_samples"])
    status["raw_state_sparse_npz_bytes"] = raw_state_sparse_path.stat().st_size if raw_state_sparse_path.exists() else 0
    status["detector_null_rows"] = len(outputs["null_anatomy"])
    status["matched_marginal_summary_rows"] = len(outputs["matched_marginal"])
    status["context_recommendation_rows"] = len(outputs["context_recommendation"])
    status["substrate_family_variant_count"] = len(outputs["substrate_variant_manifest"])
    status["response_by_substrate_family_variant_rows"] = len(outputs["response_by_substrate_variant"])
    status["selected_edge_overlap_by_beta_rows"] = len(outputs["selected_edge_overlap_by_beta"])
    status["max_entropy_constraint_manifest_rows"] = len(outputs["max_entropy_constraint_manifest"])
    status["max_entropy_marginal_match_summary_rows"] = len(outputs["max_entropy_marginal_match_summary"])
    status["max_entropy_sampler_diagnostics_rows"] = len(outputs["max_entropy_sampler_diagnostics"])
    status["max_entropy_edge_match_to_calibration_rows"] = len(outputs["max_entropy_edge_match_to_calibration"])
    status["paired_baseline_availability_by_max_entropy_variant_rows"] = len(outputs["paired_baseline_availability_by_max_entropy_variant"])
    status["fixture_result_rows"] = len(outputs["fixture_results"])
    status["perturbation_response_rows"] = len(outputs["response_classification"])
    status["response_flag_rows"] = len(outputs["response_flags"])
    status["horizon_response_threshold_rows"] = len(outputs["threshold_table"])
    status["terminal_saturation_rows"] = len(outputs["saturation"])
    status["terminal_saturation_flagged_rows"] = sum(int(float_or_zero(row.get("terminal_saturation_flag"))) for row in outputs["saturation"])
    status["response_fixture_summary_rows"] = len(outputs["response_fixture_summary"])
    status["transport_viscosity_rows"] = len(outputs["viscosity"])
    status["response_diversity_rows"] = len(outputs["response_diversity"])
    viscosity_reads = Counter(str(row.get("transport_viscosity_read", "")) for row in outputs["viscosity"] if row.get("transport_viscosity_read"))
    status["dominant_transport_viscosity_read"] = viscosity_reads.most_common(1)[0][0] if viscosity_reads else ""
    status["response_diversity_score_mean"] = round(mean([float_or_zero(row.get("response_diversity_score")) for row in outputs["response_diversity"]]), 6) if outputs["response_diversity"] else 0.0
    status["errors"] = len(errors)
    status["finished_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    kind = status_run_kind(status)
    write_csv(out_dir / errors_filename(kind), errors)
    write_csv(out_dir / progress_filename(kind), checkpoints)
    write_report(out_dir, status, outputs)
    write_manifest(out_dir, status)
    write_json(out_dir / status_filename(kind), status)


def decision_fields(outputs: dict[str, list[dict[str, object]]], status: dict[str, object]) -> dict[str, object]:
    gates = outputs["null_gates"]
    matrix_gate = any(row.get("gate_name") == "horizon_transport_matrix_coverage" and int(float_or_zero(row.get("passed"))) for row in gates)
    null_gate = any(row.get("gate_name") == "structure_detector_null_separation" and int(float_or_zero(row.get("passed"))) for row in gates)
    null_power_gate = any(row.get("gate_name") == "detector_null_replicate_power" and int(float_or_zero(row.get("passed"))) for row in gates)
    matched_marginal_gate = any(row.get("gate_name") == "matched_marginal_detector_null_separation" and int(float_or_zero(row.get("passed"))) for row in gates)
    fixture_rows = outputs["fixture_results"]
    fixture_required = bool(fixture_rows)
    fixture_gate = (not fixture_required) or all(int(float_or_zero(row.get("passed"))) for row in fixture_rows)
    response_rows = [row for row in outputs["response_classification"] if is_interpretable_response(row.get("response_class"))]
    response_interpretable = bool(response_rows)
    kind = status_run_kind(status)
    if kind == TRANSITION_ENERGY_CHARACTERIZATION:
        readiness, next_action = transition_characterization_decision(outputs, status, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable, fixture_gate)
    elif kind == MAX_ENTROPY_PREFLIGHT:
        readiness, next_action = max_entropy_preflight_decision(outputs, status, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable, fixture_gate)
    elif kind == "substrate_untethering":
        readiness, next_action = substrate_untethering_decision(outputs, status, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable, fixture_gate)
    elif kind == ASYMMETRY_LADDER:
        readiness, next_action = asymmetry_ladder_decision(outputs, status, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable, fixture_gate)
    elif kind in SWEEP_KINDS:
        readiness, next_action = sweep_decision(outputs, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable, fixture_gate, kind)
    elif kind == "h128":
        readiness, next_action = h128_decision(outputs, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable, fixture_gate)
    elif kind == "expansion":
        readiness, next_action = expansion_decision(outputs, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable)
    elif fixture_required and matrix_gate and null_gate and matched_marginal_gate and null_power_gate and response_interpretable and fixture_gate:
        readiness = "fixture_contract_passed"
        next_action = "run_empirical_matched_null_plumbing_smoke"
    elif matrix_gate and null_gate and matched_marginal_gate and null_power_gate and response_interpretable and fixture_gate:
        readiness = "ready_for_horizon_transport_smoke_expansion"
        next_action = "expand_horizon_transport_smoke"
    elif matrix_gate and not null_power_gate:
        readiness = "not_ready_repair_required"
        next_action = "repair_transport_null_controls"
    elif matrix_gate and null_gate and not matched_marginal_gate:
        readiness = "not_ready_repair_required"
        next_action = "repair_marginal_matched_transport_nulls"
    elif matrix_gate and null_gate and matched_marginal_gate and not fixture_gate:
        readiness = "not_ready_repair_required"
        next_action = "repair_horizon_transport_fixtures"
    elif matrix_gate and not null_gate:
        readiness = "ready_for_fixture_horizon_transport_tests"
        next_action = "build_horizon_transport_fixtures"
    else:
        readiness = "not_ready_repair_required"
        next_action = "repair_transport_null_controls"
    return {
        "readiness_level": readiness,
        "next_action_fork": next_action,
        "ready_for_horizon_transport_smoke_expansion": int(readiness == "ready_for_horizon_transport_smoke_expansion"),
        "ready_for_horizon_transport_scaleup": int(readiness == "ready_for_horizon_transport_scaleup"),
        "ready_for_horizon_transport_context_narrowing": int(readiness == "ready_for_horizon_transport_context_narrowing"),
        "ready_for_horizon_transport_fixture_expansion": int(readiness == "ready_for_horizon_transport_fixture_expansion"),
        "ready_for_response_fixture_repair": int(readiness == "ready_for_response_fixture_repair"),
        "ready_for_horizon_transport_theory_note": int(readiness == "ready_for_horizon_transport_theory_note"),
        "measurement_limits_note_recommended": int(readiness == "measurement_limits_note_recommended"),
        "fixture_contract_passed": int(fixture_required and fixture_gate),
        "ready_for_fixture_horizon_transport_tests": int(readiness == "ready_for_fixture_horizon_transport_tests"),
        "ready_for_direct_channel_diagnostics": int(readiness == "ready_for_direct_channel_diagnostics"),
        "not_ready_repair_required": int(readiness == "not_ready_repair_required"),
        "horizon_transport_generalizes_beyond_constraint_vocabulary": int(readiness == "horizon_transport_generalizes_beyond_constraint_vocabulary"),
        "constraint_template_specific_signal": int(readiness == "constraint_template_specific_signal"),
        "generic_smooth_landscape_sufficient": int(readiness == "generic_smooth_landscape_sufficient"),
        "budget_invariant_needed": int(readiness == "budget_invariant_needed"),
        "locality_only_trivial_baseline": int(readiness == "locality_only_trivial_baseline"),
        "untethering_underpowered": int(readiness == "untethering_underpowered"),
        "transition_energy_substrates_characterized": int(readiness == "transition_energy_substrates_characterized"),
        "budget_conservation_loadbearing": int(readiness == "budget_conservation_loadbearing"),
        "smooth_potential_loadbearing": int(readiness == "smooth_potential_loadbearing"),
        "asymmetry_ladder_characterized": int(readiness == "asymmetry_ladder_characterized"),
        "directional_asymmetry_loadbearing": int(readiness == "directional_asymmetry_loadbearing"),
        "preservation_asymmetry_loadbearing": int(readiness == "preservation_asymmetry_loadbearing"),
        "combined_asymmetry_loadbearing": int(readiness == "combined_asymmetry_loadbearing"),
        "combined_asymmetry_not_yet_clean": int(readiness == "combined_asymmetry_not_yet_clean"),
        "max_entropy_asymmetry_ready": int(readiness == "max_entropy_asymmetry_ready"),
        "max_entropy_preflight_smoke_completed": int(readiness == "max_entropy_preflight_smoke_completed"),
        "max_entropy_preflight_completed": int(readiness == "max_entropy_preflight_completed"),
        "max_entropy_local_response_bearing": int(readiness == "max_entropy_local_response_bearing"),
        "locality_only_baseline_confirmed": int(readiness == "locality_only_baseline_confirmed"),
        "locality_only_response_bearing": int(readiness == "locality_only_response_bearing"),
        "constraint_template_no_longer_primary": int(readiness == "constraint_template_no_longer_primary"),
        "max_entropy_transition_ready": int(readiness == "max_entropy_transition_ready"),
        "substrate_characterization_underpowered": int(readiness == "substrate_characterization_underpowered"),
        "coverage_repair_required": int(readiness == "coverage_repair_required"),
        "detector_null_gate_passed": int(null_gate),
        "detector_null_replicate_powered": int(null_power_gate),
        "matched_marginal_detector_null_gate_passed": int(matched_marginal_gate),
        "synthetic_fixture_contract_passed": int(fixture_required and fixture_gate),
        "synthetic_fixture_contract_required": int(fixture_required),
        "synthetic_fixture_contract_not_run": int(not fixture_required),
        "perturbation_response_interpretable": int(response_interpretable),
    }


def substrate_untethering_decision(
    outputs: dict[str, list[dict[str, object]]],
    status: dict[str, object],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
    fixture_gate: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_gate or not null_power_gate or not matched_marginal_gate or not fixture_gate:
        return "not_ready_repair_required", "repair_transition_energy_generator"
    if not response_interpretable:
        return "instrument_resolution_limit_possible", "repair_transition_energy_generator"
    jobs_requested = int(float_or_zero(status.get("jobs_requested")))
    response_rows = len(outputs.get("response_classification", []))
    if jobs_requested < 512 or response_rows < 500:
        return "untethering_underpowered", "continue_transition_energy_substrates"
    aligned = {
        str(row.get("substrate_family", "")): float_or_zero(row.get("aligned_amplification_rows"))
        for row in outputs.get("aligned_by_substrate", [])
    }
    matched = {
        str(row.get("substrate_family", "")): float_or_zero(row.get("pass_fraction_mean"))
        for row in outputs.get("matched_by_substrate", [])
    }
    non_constraint = [family for family in aligned if family != CONSTRAINT_TEMPLATE_CURRENT]
    non_constraint_aligned = [family for family in non_constraint if aligned.get(family, 0.0) > 0 and matched.get(family, 0.0) >= 0.50]
    smooth = "smooth_random_potential" in non_constraint_aligned
    budget = "budget_conservation" in non_constraint_aligned
    locality = "locality_only" in non_constraint_aligned
    if smooth and budget:
        return "horizon_transport_generalizes_beyond_constraint_vocabulary", "continue_transition_energy_substrates"
    if smooth:
        return "generic_smooth_landscape_sufficient", "expand_smooth_potential_sweep"
    if budget:
        return "budget_invariant_needed", "expand_budget_conservation_sweep"
    if locality:
        return "locality_only_trivial_baseline", "implement_max_entropy_transition_ensemble"
    if aligned.get(CONSTRAINT_TEMPLATE_CURRENT, 0.0) > 0:
        return "constraint_template_specific_signal", "write_substrate_artifact_risk_note"
    return "untethering_underpowered", "continue_transition_energy_substrates"


def max_entropy_preflight_decision(
    outputs: dict[str, list[dict[str, object]]],
    status: dict[str, object],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
    fixture_gate: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_gate or not null_power_gate or not fixture_gate:
        return "not_ready_repair_required", "repair_max_entropy_preflight_plumbing"
    if not matched_marginal_gate:
        return "coverage_repair_required", "repair_max_entropy_paired_baselines"
    match_rows = [
        row for row in outputs.get("max_entropy_marginal_match_summary", [])
        if int(float_or_zero(row.get("target_marginal_applied_count"))) > 0
    ]
    if any(row.get("marginal_match_status") != "ok" for row in match_rows):
        return "not_ready_repair_required", "repair_max_entropy_sampler"
    if not response_interpretable:
        return "max_entropy_preflight_smoke_completed", "continue_max_entropy_preflight"

    response_by_family = {
        str(row.get("substrate_family", "")): row
        for row in outputs.get("response_by_max_entropy_family", [])
    }
    local = response_by_family.get(MAX_ENTROPY_LOCAL, {})
    macro = response_by_family.get(MAX_ENTROPY_MACRO_INVARIANT, {})
    local_aligned = float_or_zero(local.get("aligned_amplification_fraction"))
    macro_aligned = float_or_zero(macro.get("aligned_amplification_fraction"))
    jobs_requested = int(float_or_zero(status.get("jobs_requested")))
    response_rows = len(outputs.get("response_classification", []))
    if jobs_requested < 256 or response_rows < 250:
        return "max_entropy_preflight_smoke_completed", "run_max_entropy_phase1_preflight"
    if macro_aligned > 0.0 and local_aligned == 0.0:
        return "max_entropy_transition_ready", "expand_max_entropy_macro_invariant_family"
    if local_aligned > 0.0:
        return "max_entropy_local_response_bearing", "demote_or_repair_max_entropy_macro_invariant_claim"
    return "max_entropy_preflight_completed", "continue_max_entropy_preflight"


def asymmetry_ladder_decision(
    outputs: dict[str, list[dict[str, object]]],
    status: dict[str, object],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
    fixture_gate: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_gate or not null_power_gate or not fixture_gate:
        return "not_ready_repair_required", "continue_asymmetry_ladder_characterization"
    if not matched_marginal_gate:
        return "coverage_repair_required", "repair_preservation_asymmetry_coverage"
    if not response_interpretable:
        return "asymmetry_ladder_underpowered", "continue_asymmetry_ladder_characterization"
    jobs_requested = int(float_or_zero(status.get("jobs_requested")))
    response_rows = len(outputs.get("response_classification", []))
    if jobs_requested < 512 or response_rows < 500:
        return "asymmetry_ladder_underpowered", "continue_asymmetry_ladder_characterization"

    response_by_family = {
        str(row.get("substrate_family", "")): row
        for row in outputs.get("response_by_substrate", [])
    }
    matched_by_family = {
        str(row.get("substrate_family", "")): float_or_zero(row.get("pass_fraction_mean"))
        for row in outputs.get("matched_by_substrate", [])
    }
    preservation = response_by_family.get(PRESERVATION_ASYMMETRY, {})
    directional = response_by_family.get(DIRECTIONAL_ASYMMETRY, {})
    combined = response_by_family.get(COMBINED_ASYMMETRY, {})
    locality = response_by_family.get(LOCALITY_ONLY, {})
    preservation_aligned = float_or_zero(preservation.get("aligned_amplification_fraction"))
    combined_aligned = float_or_zero(combined.get("aligned_amplification_fraction"))
    locality_aligned = float_or_zero(locality.get("aligned_amplification_fraction"))
    directional_differentiated = sum(
        float_or_zero(directional.get(f"{name}_count"))
        for name in (RESPONSE_CLASS_REROUTED, RESPONSE_CLASS_REOPENS, RESPONSE_CLASS_WEAKENED, RESPONSE_CLASS_COLLAPSES)
    )
    combined_differentiated = sum(
        float_or_zero(combined.get(f"{name}_count"))
        for name in (RESPONSE_CLASS_REROUTED, RESPONSE_CLASS_REOPENS, RESPONSE_CLASS_WEAKENED, RESPONSE_CLASS_COLLAPSES)
    )
    preservation_pass = matched_by_family.get(PRESERVATION_ASYMMETRY, 0.0) >= 0.75
    directional_pass = matched_by_family.get(DIRECTIONAL_ASYMMETRY, 0.0) >= 0.75
    combined_pass = matched_by_family.get(COMBINED_ASYMMETRY, 0.0) >= 0.75
    locality_pass = matched_by_family.get(LOCALITY_ONLY, 0.0) >= 0.75
    if combined_pass and combined_aligned >= max(preservation_aligned, 0.05) and combined_differentiated > 0:
        return "combined_asymmetry_loadbearing", "expand_combined_asymmetry_family"
    if preservation_pass and preservation_aligned >= 0.05:
        return "preservation_asymmetry_loadbearing", "expand_preservation_asymmetry_family"
    if directional_pass and directional_differentiated > 0:
        return "directional_asymmetry_loadbearing", "expand_directional_asymmetry_family"
    if combined and (not combined_pass or combined_aligned < preservation_aligned):
        return "combined_asymmetry_not_yet_clean", "continue_asymmetry_ladder_characterization"
    if locality_pass and locality_aligned == 0.0 and (preservation_aligned > 0.0 or directional_differentiated > 0):
        return "locality_only_baseline_confirmed", "write_asymmetry_ladder_theory_note"
    if preservation_pass and directional_pass and combined_pass:
        return "asymmetry_ladder_characterized", "implement_max_entropy_asymmetry_ensemble"
    return "asymmetry_ladder_characterized", "continue_asymmetry_ladder_characterization"


def transition_characterization_decision(
    outputs: dict[str, list[dict[str, object]]],
    status: dict[str, object],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
    fixture_gate: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_gate or not null_power_gate or not fixture_gate:
        return "not_ready_repair_required", "pause_substrate_untethering"
    if not matched_marginal_gate:
        return "coverage_repair_required", "continue_transition_energy_characterization"
    if not response_interpretable:
        return "not_ready_repair_required", "pause_substrate_untethering"
    jobs_requested = int(float_or_zero(status.get("jobs_requested")))
    response_rows = len(outputs.get("response_classification", []))
    variant_count = len(outputs.get("substrate_variant_manifest", []))
    if jobs_requested < 4096 or response_rows < 2000 or variant_count < 8:
        return "substrate_characterization_underpowered", "continue_transition_energy_characterization"

    response_by_family = {
        str(row.get("substrate_family", "")): row
        for row in outputs.get("response_by_substrate", [])
    }
    matched_by_family = {
        str(row.get("substrate_family", "")): float_or_zero(row.get("pass_fraction_mean"))
        for row in outputs.get("matched_by_substrate", [])
    }
    budget = response_by_family.get("budget_conservation", {})
    smooth = response_by_family.get("smooth_random_potential", {})
    locality = response_by_family.get("locality_only", {})
    constraint = response_by_family.get(CONSTRAINT_TEMPLATE_CURRENT, {})
    budget_aligned = float_or_zero(budget.get("aligned_amplification_fraction"))
    smooth_aligned = float_or_zero(smooth.get("aligned_amplification_fraction"))
    locality_aligned = float_or_zero(locality.get("aligned_amplification_fraction"))
    constraint_aligned = float_or_zero(constraint.get("aligned_amplification_fraction"))
    budget_pass = matched_by_family.get("budget_conservation", 0.0) >= 0.75
    smooth_pass = matched_by_family.get("smooth_random_potential", 0.0) >= 0.75
    locality_pass = matched_by_family.get("locality_only", 0.0) >= 0.75

    non_template_signal = max(budget_aligned, smooth_aligned, locality_aligned) >= constraint_aligned
    if budget_pass and budget_aligned >= max(smooth_aligned, locality_aligned, constraint_aligned, 0.05):
        return "budget_conservation_loadbearing", "expand_budget_conservation_family"
    if smooth_pass and smooth_aligned >= max(budget_aligned, locality_aligned, constraint_aligned, 0.05):
        return "smooth_potential_loadbearing", "expand_smooth_potential_family"
    if locality_pass and locality_aligned >= 0.05:
        return "locality_only_response_bearing", "continue_transition_energy_characterization"
    if locality_pass and locality_aligned == 0.0 and (budget_aligned > 0.0 or smooth_aligned > 0.0):
        return "locality_only_baseline_confirmed", "write_transition_energy_substrate_atlas_note"
    if non_template_signal and budget_pass and smooth_pass:
        return "constraint_template_no_longer_primary", "write_transition_energy_substrate_atlas_note"
    if budget_pass and smooth_pass and locality_pass:
        return "transition_energy_substrates_characterized", "implement_max_entropy_local_transition"
    return "transition_energy_substrates_characterized", "write_transition_energy_substrate_atlas_note"


def sweep_decision(
    outputs: dict[str, list[dict[str, object]]],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
    fixture_gate: bool,
    kind: str,
) -> tuple[str, str]:
    if not matrix_gate or not null_gate or not null_power_gate or not matched_marginal_gate or not fixture_gate:
        return "not_ready_repair_required", "repair_detector_or_response_taxonomy"
    if not response_interpretable:
        return "measurement_limits_note_recommended", "write_measurement_limits_note"
    saturation_rows = outputs.get("saturation", [])
    terminal_fraction = (
        mean([int(float_or_zero(row.get("terminal_saturation_flag"))) for row in saturation_rows])
        if saturation_rows else 0.0
    )
    if terminal_fraction >= 0.50:
        return "measurement_limits_note_recommended", "write_measurement_limits_note"
    classes = {
        str(row.get("response_class", ""))
        for row in outputs.get("response_classification", [])
        if is_interpretable_response(row.get("response_class"))
    }
    differentiated = classes & DIFFERENTIATED_RESPONSE_CLASSES
    if differentiated:
        return "ready_for_horizon_transport_context_narrowing", "probe_viscosity_boundary"
    viscosity_reads = Counter(str(row.get("transport_viscosity_read", "")) for row in outputs.get("viscosity", []))
    high_viscosity_count = viscosity_reads.get("high_viscosity_aligned_amplifier", 0)
    if high_viscosity_count and high_viscosity_count >= max(1, sum(viscosity_reads.values()) // 2):
        return "ready_for_horizon_transport_theory_note", "write_low_complexity_amplifier_note"
    if kind == "horizon_10x":
        return "ready_for_horizon_transport_context_narrowing", "extend_horizon_scale"
    if kind == "breadth":
        return "ready_for_horizon_transport_context_narrowing", "expand_substrate_breadth"
    if kind == "viscosity_ladder":
        return "ready_for_horizon_transport_context_narrowing", "probe_viscosity_boundary"
    return "ready_for_horizon_transport_context_narrowing", "compare_resolution_views"


def h128_decision(
    outputs: dict[str, list[dict[str, object]]],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
    fixture_gate: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_gate or not null_power_gate or not matched_marginal_gate:
        return "not_ready_repair_required", "extend_or_trim_horizon_range"
    if not fixture_gate:
        return "ready_for_response_fixture_repair", "repair_response_taxonomy_fixtures"
    saturation_rows = outputs.get("saturation", [])
    decisive = [
        row for row in saturation_rows
        if str(row.get("horizon_pair", "")) in {"64->96", "96->128"}
    ]
    if decisive and mean([int(float_or_zero(row.get("terminal_saturation_flag"))) for row in decisive]) >= 0.50:
        return "measurement_limits_note_recommended", "write_horizon_transport_measurement_limits_note"
    classes = {
        str(row.get("response_class", ""))
        for row in outputs.get("response_classification", [])
    }
    nonstable = classes - {"", RESPONSE_CLASS_STABLE} - set(MEASUREMENT_LIMIT_RESPONSE_CLASSES)
    if RESPONSE_CLASS_AMPLIFIED_ALIGNED in nonstable and len(nonstable) >= 1:
        return "ready_for_horizon_transport_theory_note", "write_horizon_transport_theory_note"
    if response_interpretable and nonstable:
        return "ready_for_horizon_transport_context_narrowing", "narrow_to_horizon_response_context"
    if response_interpretable:
        return "measurement_limits_note_recommended", "write_horizon_transport_measurement_limits_note"
    return "not_ready_repair_required", "extend_or_trim_horizon_range"


def expansion_decision(
    outputs: dict[str, list[dict[str, object]]],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_power_gate:
        return "not_ready_repair_required", "repair_transport_null_controls"
    promising = [
        row for row in outputs["context_recommendation"]
        if row.get("context_read") == "matched_marginal_separates_interpretable"
    ]
    partial = [
        row for row in outputs["context_recommendation"]
        if row.get("context_read") in {"matched_marginal_separates_interpretable", "matched_marginal_mixed"}
    ]
    if matched_marginal_gate and null_gate and response_interpretable and len(promising) >= 4:
        return "ready_for_horizon_transport_scaleup", "expand_horizon_transport_scale"
    if partial:
        return "ready_for_horizon_transport_context_narrowing", "narrow_to_best_horizon_transport_context"
    if null_gate and response_interpretable:
        return "ready_for_horizon_transport_fixture_expansion", "build_more_horizon_transport_fixtures"
    if matrix_gate and null_power_gate:
        return "measurement_limits_note_recommended", "write_horizon_transport_measurement_limits_note"
    return "not_ready_repair_required", "repair_transport_null_controls"


def write_report(out_dir: Path, status: dict[str, object], outputs: dict[str, list[dict[str, object]]]) -> None:
    gates = outputs["null_gates"]
    response_counts = Counter(str(row.get("response_class", "")) for row in outputs["response_classification"])
    best_context = outputs["context_recommendation"][0] if outputs["context_recommendation"] else {}
    lines = [
        "# Executive Summary",
        "",
        f"Decision: `{status.get('readiness_level', '')}`.",
        "",
        f"Next action: `{status.get('next_action_fork', '')}`.",
        "",
        f"Run kind: `{status.get('run_kind', '')}`.",
        "",
        f"Horizon-transport matrices built: `{status.get('matrix_count', 0)}`.",
        "",
        f"Detector-null gate passed: `{status.get('detector_null_gate_passed', 0)}`.",
        "",
        f"Detector-null replicate powered: `{status.get('detector_null_replicate_powered', 0)}`.",
        "",
        f"Matched marginal null gate passed: `{status.get('matched_marginal_detector_null_gate_passed', 0)}`.",
        "",
        f"Synthetic fixture contract: `{fixture_status_text(status)}`.",
        "",
        f"Perturbation response interpretable: `{status.get('perturbation_response_interpretable', 0)}`.",
        "",
        f"Best context: `{context_label(best_context)}`.",
        "",
        "Detector-null controls and candidate perturbation responses were written to separate outputs.",
        "",
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Run Shape and Local Artifact Policy",
        "",
        f"Jobs requested: `{status.get('jobs_requested', 0)}`.",
        f"Jobs completed: `{status.get('jobs_completed', 0)}`.",
        f"Workers: `{status.get('workers', '')}`.",
        f"Substrate families: `{', '.join(str(row.get('substrate_family', '')) for row in outputs.get('substrate_manifest', []))}`.",
        f"Finalization reason: `{status.get('finalization_reason', '')}`.",
        f"Compact transport matrix NPZ bytes: `{status.get('matrix_sparse_npz_bytes', 0)}`.",
        f"Raw substrate state sample rows: `{status.get('raw_state_sample_rows', 0)}`.",
        f"Compact raw frontier NPZ bytes: `{status.get('raw_state_sparse_npz_bytes', 0)}`.",
        f"Artifact policy: {LOCAL_ONLY_ARTIFACT_POLICY}",
        "",
        "## Matrix Coverage",
        "",
        f"Matrix count: `{len(outputs['manifest'])}`.",
        f"Coverage rows: `{len(outputs['coverage'])}`.",
        f"Minimum context coverage: `{min((float_or_zero(row.get('coverage_min')) for row in outputs['context_recommendation']), default=0.0):.3f}`.",
        "",
        "## Substrate Family Summary",
        "",
        "| substrate_family | matrices | capacity_read | aligned amplification rows | viscosity read |",
        "|---|---:|---|---:|---|",
    ]
    capacity_by_family = {row.get("substrate_family"): row for row in outputs.get("substrate_capacity", [])}
    aligned_by_family = {row.get("substrate_family"): row for row in outputs.get("aligned_by_substrate", [])}
    viscosity_by_family = {row.get("substrate_family"): row for row in outputs.get("viscosity_by_substrate", [])}
    for row in outputs.get("substrate_manifest", []):
        family = row.get("substrate_family", "")
        capacity = capacity_by_family.get(family, {})
        aligned = aligned_by_family.get(family, {})
        viscosity = viscosity_by_family.get(family, {})
        lines.append(
            f"| {markdown_cell(family)} | {row.get('matrix_count', 0)} | "
            f"{markdown_cell(capacity.get('capacity_read', ''))} | "
            f"{aligned.get('aligned_amplification_rows', 0)} | "
            f"{markdown_cell(viscosity.get('transport_viscosity_read_mode', ''))} |"
        )
    if status.get("run_kind") == TRANSITION_ENERGY_CHARACTERIZATION:
        lines.extend([
            "",
            "## Substrate Family Variants",
            "",
            "| substrate_family | substrate_variant | matrices | capacity read | matched fraction | dominant response | aligned fraction |",
            "|---|---|---:|---|---:|---|---:|",
        ])
        capacity_by_variant = {
            (row.get("substrate_family"), row.get("substrate_variant")): row
            for row in outputs.get("substrate_capacity_variant", [])
        }
        matched_by_variant = {
            (row.get("substrate_family"), row.get("substrate_variant")): row
            for row in outputs.get("matched_by_substrate_variant", [])
        }
        response_by_variant = {
            (row.get("substrate_family"), row.get("substrate_variant")): row
            for row in outputs.get("response_by_substrate_variant", [])
        }
        for row in outputs.get("substrate_variant_manifest", [])[:80]:
            key = (row.get("substrate_family"), row.get("substrate_variant"))
            capacity = capacity_by_variant.get(key, {})
            matched = matched_by_variant.get(key, {})
            response = response_by_variant.get(key, {})
            lines.append(
                f"| {markdown_cell(row.get('substrate_family', ''))} | {markdown_cell(row.get('substrate_variant', ''))} | "
                f"{row.get('matrix_count', 0)} | {markdown_cell(capacity.get('capacity_read', ''))} | "
                f"{float_or_zero(matched.get('pass_fraction_mean')):.3f} | "
                f"{markdown_cell(response.get('dominant_response_class', ''))} | "
                f"{float_or_zero(response.get('aligned_amplification_fraction')):.3f} |"
            )
        lines.extend([
            "",
            "## Budget-Conservation Analysis",
            "",
            "| budget_kind | response rows | dominant response | aligned fraction |",
            "|---|---:|---|---:|",
        ])
        for row in outputs.get("response_by_budget", []):
            lines.append(
                f"| {markdown_cell(row.get('budget_kind', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | "
                f"{float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
        lines.extend([
            "",
            "## Smooth-Potential Analysis",
            "",
            "| parameter | value | response rows | dominant response | aligned fraction |",
            "|---|---|---:|---|---:|",
        ])
        for row in outputs.get("response_by_potential_smoothness", []):
            lines.append(
                f"| potential_smoothness | {markdown_cell(row.get('potential_smoothness', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | {float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
        for row in outputs.get("response_by_potential_beta", []):
            lines.append(
                f"| potential_beta | {markdown_cell(row.get('potential_beta', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | {float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
        lines.extend([
            "",
            "## Asymmetry-Ladder Parameter Analysis",
            "",
            "| parameter | value | response rows | dominant response | aligned fraction |",
            "|---|---|---:|---|---:|",
        ])
        for row in outputs.get("response_by_directional_alpha", []):
            lines.append(
                f"| asymmetry_alpha | {markdown_cell(row.get('asymmetry_alpha', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | {float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
        for row in outputs.get("response_by_asymmetry_field_smoothness", []):
            lines.append(
                f"| asymmetry_field_smoothness | {markdown_cell(row.get('asymmetry_field_smoothness', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | {float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
        for row in outputs.get("response_by_macro_invariant_kind", []):
            lines.append(
                f"| macro_invariant_kind | {markdown_cell(row.get('macro_invariant_kind', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | {float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
        for row in outputs.get("response_by_macro_invariant_beta", []):
            lines.append(
                f"| macro_invariant_beta | {markdown_cell(row.get('macro_invariant_beta', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | {float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
        if outputs.get("selected_edge_overlap_by_beta"):
            lines.extend([
                "",
                "## Selected-Edge Overlap By Beta",
                "",
                "| family | invariant | beta | samples | mean Jaccard vs beta0 | min Jaccard | mean symmetric difference |",
                "|---|---|---:|---:|---:|---:|---:|",
            ])
            for row in outputs.get("selected_edge_overlap_by_beta", []):
                lines.append(
                    f"| {markdown_cell(row.get('substrate_family', ''))} | {markdown_cell(row.get('macro_invariant_kind', ''))} | "
                    f"{markdown_cell(row.get('macro_invariant_beta', ''))} | {row.get('ok_sample_count', '')} | "
                    f"{float_or_zero(row.get('edge_jaccard_vs_beta0_mean')):.3f} | "
                    f"{float_or_zero(row.get('edge_jaccard_vs_beta0_min')):.3f} | "
                    f"{float_or_zero(row.get('selected_edge_symmetric_difference_fraction_mean')):.3f} |"
                )
        for row in outputs.get("response_by_alpha_beta_pair", []):
            lines.append(
                f"| alpha_beta_pair | {markdown_cell(row.get('alpha_beta_pair', ''))} | {row.get('response_rows', '')} | "
                f"{markdown_cell(row.get('dominant_response_class', ''))} | {float_or_zero(row.get('aligned_amplification_fraction')):.3f} |"
            )
    lines.extend([
        "",
        "## Control Taxonomy Compliance",
        "",
        "Every matrix and response row includes intervention class, family, name, strength, interpretation role, and allowed claim level.",
        "",
        "## Horizon-Transport Matrix Construction",
        "",
        "Matrix family: `horizon_transport`; spectral method: `SVD`.",
        "",
        "## Detector-Null Results",
        "",
        "| gate | passed | observed | blocker |",
        "|---|---:|---|---|",
    ])
    for row in gates:
        lines.append(
            f"| {markdown_cell(row.get('gate_name', ''))} | {row.get('passed', '')} | "
            f"{markdown_cell(row.get('observed', ''))} | {markdown_cell(row.get('blocking_reason', ''))} |"
        )
    lines.extend([
        "",
        "## Matched Marginal Null Results",
        "",
        "| null_family | contexts | mean pass_fraction | min percentile |",
        "|---|---:|---:|---:|",
    ])
    for family, items in group_by(outputs["matched_marginal"], ("null_family",)).items():
        pass_fractions = [float_or_zero(row.get("pass_fraction")) for row in items]
        min_percentiles = [float_or_zero(row.get("min_observed_percentile_vs_null")) for row in items]
        lines.append(
            f"| {markdown_cell(family[0])} | {len(items)} | "
            f"{mean(pass_fractions) if pass_fractions else 0.0:.3f} | {min(min_percentiles) if min_percentiles else 0.0:.3f} |"
        )
    lines.extend([
        "",
        "## Fixture Results",
        "",
        "| fixture | passed | observed |",
        "|---|---:|---|",
    ])
    for row in outputs["fixture_results"]:
        lines.append(
            f"| {markdown_cell(row.get('fixture_id', ''))} | {row.get('passed', '')} | "
            f"{markdown_cell(row.get('observed', ''))} |"
        )
    if not outputs["fixture_results"]:
        lines.append("| not_run |  | fixture smoke disabled |")
    lines.extend([
        "",
        "## Perturbation-Response Results",
        "",
        "| response_class | count |",
        "|---|---:|",
    ])
    for name, count in sorted(response_counts.items()):
        lines.append(f"| {markdown_cell(name)} | {count} |")
    lines.extend([
        "",
        "## Terminal Saturation Diagnostics",
        "",
        "| horizon_pair | matrices | terminal fraction | undercoverage fraction | normal fraction |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in outputs.get("saturation_by_horizon_pair", []):
        lines.append(
            f"| {markdown_cell(row.get('horizon_pair', ''))} | {row.get('matrix_count', '')} | "
            f"{float_or_zero(row.get('terminal_saturation_fraction')):.3f} | "
            f"{float_or_zero(row.get('undercoverage_fraction')):.3f} | "
            f"{float_or_zero(row.get('normal_interpretation_fraction')):.3f} |"
        )
    lines.extend([
        "",
        "## Response Class by Strength and Horizon Pair",
        "",
        "| perturbation | strength | probe | flow | horizon_pair | response_class | count |",
        "|---|---:|---|---|---|---|---:|",
    ])
    for row in outputs.get("response_by_strength_horizon", [])[:80]:
        lines.append(
            f"| {markdown_cell(row.get('perturbation_family', ''))} | {row.get('perturbation_strength', '')} | "
            f"{markdown_cell(row.get('probe_key', ''))} | {markdown_cell(row.get('flow_mode', ''))} | "
            f"{markdown_cell(row.get('horizon_pair', ''))} | {markdown_cell(row.get('response_class', ''))} | "
            f"{row.get('row_count', '')} |"
        )
    lines.extend([
        "",
        "## Horizon Response Threshold Table",
        "",
        "| perturbation | strength | probe | flow | first nonstable | first amplified | first weakened | first rerouted | first reopened | first collapsed | terminal saturation | latest interpretable |",
        "|---|---:|---|---|---|---|---|---|---|---|---|---|",
    ])
    for row in outputs.get("threshold_table", []):
        lines.append(
            f"| {markdown_cell(row.get('perturbation_family', ''))} | {row.get('perturbation_strength', '')} | "
            f"{markdown_cell(row.get('probe_key', ''))} | {markdown_cell(row.get('flow_mode', ''))} | "
            f"{markdown_cell(row.get('first_nonstable_horizon', ''))} | "
            f"{markdown_cell(row.get('first_amplified_aligned_horizon', ''))} | "
            f"{markdown_cell(row.get('first_weakened_horizon', ''))} | "
            f"{markdown_cell(row.get('first_rerouted_horizon', ''))} | "
            f"{markdown_cell(row.get('first_reopened_horizon', ''))} | "
            f"{markdown_cell(row.get('first_collapsed_horizon', ''))} | "
            f"{markdown_cell(row.get('terminal_saturation_horizon', ''))} | "
            f"{markdown_cell(row.get('latest_interpretable_horizon', ''))} |"
        )
    lines.extend([
        "",
        "## Transport Viscosity Summary",
        "",
        f"Dominant viscosity read: `{status.get('dominant_transport_viscosity_read', '')}`.",
        "",
        f"Mean response diversity score: `{float_or_zero(status.get('response_diversity_score_mean')):.3f}`.",
        "",
        "| perturbation | strength | probe | flow | class diversity | diversity score | viscosity score | viscosity read | first non-amplified | latest interpretable |",
        "|---|---:|---|---|---:|---:|---:|---|---|---|",
    ])
    for row in outputs.get("response_diversity", [])[:80]:
        lines.append(
            f"| {markdown_cell(row.get('perturbation_family', ''))} | {row.get('perturbation_strength', '')} | "
            f"{markdown_cell(row.get('probe_key', ''))} | {markdown_cell(row.get('flow_mode', ''))} | "
            f"{row.get('response_class_diversity_by_context', '')} | "
            f"{float_or_zero(row.get('response_diversity_score')):.3f} | "
            f"{float_or_zero(row.get('transport_viscosity_score')):.3f} | "
            f"{markdown_cell(row.get('transport_viscosity_read', ''))} | "
            f"{markdown_cell(row.get('first_non_amplified_response_horizon', ''))} | "
            f"{markdown_cell(row.get('latest_interpretable_horizon', ''))} |"
        )
    lines.extend([
        "",
        "## Probe / Flow / Horizon-Pair Context Summary",
        "",
        "### By Probe",
        "",
        "| probe | contexts | full matched pass | response contexts | read |",
        "|---|---:|---:|---:|---|",
    ])
    for row in outputs["by_probe"]:
        lines.append(
            f"| {markdown_cell(row.get('probe_key', ''))} | {row.get('context_count', '')} | "
            f"{row.get('matched_marginal_full_pass_contexts', '')} | {row.get('response_interpretable_contexts', '')} | "
            f"{markdown_cell(row.get('summary_read', ''))} |"
        )
    lines.extend([
        "",
        "### By Flow Mode",
        "",
        "| flow_mode | contexts | full matched pass | response contexts | read |",
        "|---|---:|---:|---:|---|",
    ])
    for row in outputs["by_flow_mode"]:
        lines.append(
            f"| {markdown_cell(row.get('flow_mode', ''))} | {row.get('context_count', '')} | "
            f"{row.get('matched_marginal_full_pass_contexts', '')} | {row.get('response_interpretable_contexts', '')} | "
            f"{markdown_cell(row.get('summary_read', ''))} |"
        )
    lines.extend([
        "",
        "### By Horizon Pair",
        "",
        "| horizon_pair | contexts | full matched pass | response contexts | read |",
        "|---|---:|---:|---:|---|",
    ])
    for row in outputs["by_horizon_pair"]:
        lines.append(
            f"| {markdown_cell(row.get('horizon_pair', ''))} | {row.get('context_count', '')} | "
            f"{row.get('matched_marginal_full_pass_contexts', '')} | {row.get('response_interpretable_contexts', '')} | "
            f"{markdown_cell(row.get('summary_read', ''))} |"
        )
    lines.extend([
        "",
        "## Context Recommendation",
        "",
        "| context | read | recommendation | score |",
        "|---|---|---|---:|",
    ])
    for row in outputs["context_recommendation"][:10]:
        lines.append(
            f"| {markdown_cell(context_label(row))} | {markdown_cell(row.get('context_read', ''))} | "
            f"{markdown_cell(row.get('context_recommendation', ''))} | {float_or_zero(row.get('context_priority_score')):.3f} |"
        )
    lines.extend([
        "",
        "## Horizon-Pair Comparison",
        "",
        f"Subspace alignment rows: `{len(outputs['subspace_alignment'])}`.",
        "",
        "## Readiness Levels",
        "",
        f"- ready_for_horizon_transport_smoke_expansion: `{status.get('ready_for_horizon_transport_smoke_expansion', 0)}`",
        f"- ready_for_horizon_transport_scaleup: `{status.get('ready_for_horizon_transport_scaleup', 0)}`",
        f"- ready_for_horizon_transport_context_narrowing: `{status.get('ready_for_horizon_transport_context_narrowing', 0)}`",
        f"- ready_for_horizon_transport_fixture_expansion: `{status.get('ready_for_horizon_transport_fixture_expansion', 0)}`",
        f"- ready_for_response_fixture_repair: `{status.get('ready_for_response_fixture_repair', 0)}`",
        f"- ready_for_horizon_transport_theory_note: `{status.get('ready_for_horizon_transport_theory_note', 0)}`",
        f"- measurement_limits_note_recommended: `{status.get('measurement_limits_note_recommended', 0)}`",
        f"- fixture_contract_passed: `{status.get('fixture_contract_passed', 0)}`",
        f"- ready_for_fixture_horizon_transport_tests: `{status.get('ready_for_fixture_horizon_transport_tests', 0)}`",
        f"- ready_for_direct_channel_diagnostics: `{status.get('ready_for_direct_channel_diagnostics', 0)}`",
        f"- not_ready_repair_required: `{status.get('not_ready_repair_required', 0)}`",
        "",
        "## Next-Action Fork",
        "",
        f"`{status.get('next_action_fork', '')}`",
        "",
        "## Output Manifest",
        "",
        f"See `{manifest_filename(status_run_kind(status))}`.",
        "",
    ])
    (out_dir / report_filename(status_run_kind(status))).write_text("\n".join(lines), encoding="utf-8")


def fixture_status_text(status: dict[str, object]) -> str:
    if int(float_or_zero(status.get("synthetic_fixture_contract_required"))) == 0:
        return "not_run"
    if int(float_or_zero(status.get("synthetic_fixture_contract_passed"))):
        return "passed"
    return "failed"


def context_label(row: dict[str, object]) -> str:
    if not row:
        return "none"
    pieces = []
    substrate_family = str(row.get("substrate_family", ""))
    if substrate_family:
        pieces.append(substrate_family)
    pieces.extend([
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
        f"{row.get('H_a', '')}->{row.get('H_b', '')}",
    ])
    return "|".join(pieces)


def markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def output_files(kind: str) -> list[str]:
    return [
        run_config_filename(kind),
        status_filename(kind),
        progress_filename(kind),
        errors_filename(kind),
        manifest_filename(kind),
        *COMMON_OUTPUTS,
        report_filename(kind),
    ]


def write_manifest(out_dir: Path, status: dict[str, object]) -> None:
    kind = status_run_kind(status)
    rows = output_manifest_rows(output_files(kind), out_dir)
    for row in rows:
        if row.get("file") == manifest_filename(kind):
            row["exists"] = True
            row["status"] = "present"
    write_json(out_dir / manifest_filename(kind), rows)


def transport_matrix_id(key: TransportKey) -> str:
    return "|".join([
        "horizon_transport",
        key.condition_id,
        key.probe_key,
        key.flow_mode,
        f"{key.H_a}->{key.H_b}",
    ])


def key_row(key: TransportKey) -> dict[str, object]:
    family = substrate_family_from_condition_id(key.condition_id)
    variant = substrate_variant_from_condition_id(key.condition_id)
    macro_beta = variant_parameter(variant, "beta") if family in {PRESERVATION_ASYMMETRY, COMBINED_ASYMMETRY} else ""
    equivalent_beta = variant_parameter(variant, "equivalent_beta") if family in MAX_ENTROPY_FAMILIES else ""
    asymmetry_alpha = variant_parameter(variant, "alpha") if family in {DIRECTIONAL_ASYMMETRY, COMBINED_ASYMMETRY} else ""
    asymmetry_smoothness = variant_parameter(variant, "smoothness") if family in {DIRECTIONAL_ASYMMETRY, COMBINED_ASYMMETRY} else ""
    return {
        "matrix_family": "horizon_transport",
        "substrate_family": family,
        "substrate_variant": variant,
        "potential_smoothness": variant_parameter(variant, "smoothness") if family == SMOOTH_RANDOM_POTENTIAL else "",
        "potential_beta": variant_parameter(variant, "beta") if family == SMOOTH_RANDOM_POTENTIAL else "",
        "budget_kind": budget_kind_from_variant(variant) if family == BUDGET_CONSERVATION else "",
        "budget_weight": variant_parameter(variant, "weight") if family == BUDGET_CONSERVATION else "",
        "macro_invariant_kind": invariant_kind_from_variant(variant) if family in {PRESERVATION_ASYMMETRY, COMBINED_ASYMMETRY, *MAX_ENTROPY_FAMILIES} else "",
        "macro_invariant_beta": macro_beta or equivalent_beta,
        "equivalent_beta_target": equivalent_beta,
        "asymmetry_alpha": asymmetry_alpha,
        "asymmetry_field_smoothness": asymmetry_smoothness,
        "alpha_beta_pair": f"{asymmetry_alpha}:{macro_beta}" if asymmetry_alpha and macro_beta else "",
        "condition_id": key.condition_id,
        "actual_control_name": key.actual_control_name,
        "mechanism_control_strength": key.mechanism_control_strength,
        "probe_key": key.probe_key,
        "flow_mode": key.flow_mode,
        "source_horizon_band": key.source_horizon_band,
        "target_horizon_band": key.target_horizon_band,
        "H_a": key.H_a,
        "H_b": key.H_b,
        "horizon_pair": f"{key.H_a}->{key.H_b}",
    }


def substrate_family_from_condition_id(condition_id: object) -> str:
    value = str(condition_id)
    if "::" in value:
        family, _rest = value.split("::", 1)
        if family in TRANSITION_ENERGY_FAMILIES:
            return family
    if value.startswith("fixture_"):
        return "synthetic_fixture"
    return CONSTRAINT_TEMPLATE_CURRENT


def substrate_variant_from_condition_id(condition_id: object) -> str:
    value = str(condition_id)
    parts = value.split("::")
    if len(parts) >= 3 and parts[0] in TRANSITION_ENERGY_FAMILIES:
        return parts[1]
    if len(parts) == 2 and parts[0] in TRANSITION_ENERGY_FAMILIES:
        return "default"
    if value.startswith("fixture_"):
        return "synthetic_fixture"
    return "default"


def variant_parameter(variant: str, field: str) -> str:
    prefix = f"{field}_"
    for part in str(variant).split("__"):
        if part.startswith(prefix):
            return part[len(prefix):].replace("p", ".").replace("m", "-")
    return ""


def budget_kind_from_variant(variant: str) -> str:
    if not str(variant).startswith("budget_"):
        return ""
    head = str(variant).split("__", 1)[0]
    return head[len("budget_"):]


def invariant_kind_from_variant(variant: str) -> str:
    for part in str(variant).split("__"):
        if part.startswith("invariant_"):
            return part[len("invariant_"):]
    if str(variant).startswith("budget_"):
        return budget_kind_from_variant(variant)
    return ""


def intervention_taxonomy(key: TransportKey) -> dict[str, object]:
    if key.actual_control_name == BASELINE_CONTROL:
        intervention_class = "baseline"
        interpretation_role = "instrumentation_only"
        allowed_claim_level = "instrumentation_only"
    else:
        intervention_class = "nonlethal_perturbation"
        interpretation_role = "candidate_response_profile"
        allowed_claim_level = "response_profile_only"
    return {
        "intervention_class": intervention_class,
        "intervention_family": "baseline" if key.actual_control_name == BASELINE_CONTROL else key.actual_control_name,
        "intervention_name": key.actual_control_name,
        "intervention_strength": key.mechanism_control_strength,
        "interpretation_role": interpretation_role,
        "allowed_claim_level": allowed_claim_level,
    }


def horizon_point_band(horizon: int) -> str:
    if horizon <= 2:
        return "short"
    if horizon <= 16:
        return "middle"
    return "downstream"


def transport_stat(matrix: TransportMatrix | np.ndarray, stat: str) -> float:
    values = matrix.matrix if isinstance(matrix, TransportMatrix) else matrix
    singular = np.linalg.svd(values, compute_uv=False)
    if stat in {"positive_or_nonzero_spectral_mass", "singular_spectral_mass"}:
        return float(np.sum(singular))
    if stat in {"effective_rank", "singular_effective_rank"}:
        return effective_rank(singular)
    if stat == "transport_concentration":
        return top_share(values.flatten(), 1)
    if stat == "marginal_residual_fraction":
        return marginal_residual_fraction(values)
    return 0.0


def null_failure_interpretation(matrix: TransportMatrix, category: str, percentile: float, threshold: float, replicates: int) -> str:
    if category == "label_interpretation_control":
        return "passed"
    if matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) < 0.50:
        return "insufficient_coverage"
    if replicates < 3:
        return "underpowered_replicates"
    if percentile >= threshold:
        return "passed"
    if category == "marginal_matched_detector_null":
        return "marginal_mass_geometry_explains_statistic"
    if percentile <= 0.50:
        return "true_control_equivalence"
    return "statistic_mismatch"


def response_view_key(matrix: TransportMatrix) -> tuple[object, ...]:
    return (
        substrate_family_from_condition_id(matrix.key.condition_id),
        substrate_variant_from_condition_id(matrix.key.condition_id),
        matrix.key.probe_key,
        matrix.key.flow_mode,
        matrix.key.H_a,
        matrix.key.H_b,
    )


def sub_transport_matrix(matrix: TransportMatrix, rows: list[str], cols: list[str]) -> np.ndarray:
    row_index = {item: index for index, item in enumerate(matrix.row_items)}
    col_index = {item: index for index, item in enumerate(matrix.column_items)}
    out = np.zeros((len(rows), len(cols)), dtype=np.float64)
    for i, item in enumerate(rows):
        for j, col in enumerate(cols):
            out[i, j] = matrix.matrix[row_index[item], col_index[col]]
    return out


def svd_parts(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u, s, vt = np.linalg.svd(matrix, full_matrices=False)
    return u, s, vt.T


def subspace_alignment(left: np.ndarray, right: np.ndarray) -> float:
    if left.size == 0 or right.size == 0:
        return 0.0
    k = min(left.shape[1], right.shape[1])
    return float(np.linalg.norm(left[:, :k].T @ right[:, :k], ord="fro") ** 2 / max(1, k))


def group_matrices(matrices: list[TransportMatrix], fields: tuple[str, ...]) -> dict[tuple[object, ...], list[TransportMatrix]]:
    grouped: dict[tuple[object, ...], list[TransportMatrix]] = defaultdict(list)
    for matrix in matrices:
        values = []
        for field in fields:
            values.append(getattr(matrix.key, field))
        grouped[tuple(values)].append(matrix)
    return grouped


def marginal_residual_fraction(values: np.ndarray) -> float:
    total = float(np.sum(values))
    if total <= 0:
        return 0.0
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    expected = np.outer(row_sums, col_sums) / total
    denom = float(np.linalg.norm(values))
    if denom <= 1e-12:
        return 0.0
    return float(np.linalg.norm(values - expected) / denom)


def entropy_from_values(values: np.ndarray) -> float:
    total = float(np.sum(values))
    if total <= 0:
        return 0.0
    probs = [float(value) / total for value in values if value > 0]
    return -sum(prob * math.log(prob) for prob in probs)


def top_share(values: np.ndarray, k: int) -> float:
    total = float(np.sum(values))
    if total <= 0:
        return 0.0
    ordered = sorted((float(value) for value in values if value > 0), reverse=True)
    return sum(ordered[:k]) / total


def vector_participation(vector: np.ndarray) -> float:
    weights = np.asarray(vector, dtype=np.float64) ** 2
    denom = float(np.sum(weights ** 2))
    return 1.0 / denom if denom > 1e-12 else 0.0


if __name__ == "__main__":
    main()
