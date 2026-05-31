"""Stable contracts for the horizon-transport instrumentation runner.

This module intentionally avoids importing the heavy simulation runner. It is
the small, auditable surface for spec IDs, output filenames, horizon-pair
defaults, and run-kind naming. Keeping these strings together reduces drift
between reports, manifests, and downstream scripts.
"""

from __future__ import annotations

PARENT_SPEC_ID = "docs/RFS_MB0_HORIZON_TRANSPORT_SPECTRAL_RESPONSE_REPAIR_SPEC.md"
MATCHED_NULL_SPEC_ID = "docs/RFS_MB0_HORIZON_TRANSPORT_MATCHED_NULL_AND_FIXTURE_SMOKE_SPEC.md"
EXPANSION_SPEC_ID = "docs/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md"
H128_SPEC_ID = "docs/RFS_MB0_HORIZON_TRANSPORT_RESPONSE_SURFACE_H128_SCALEUP_SPEC.md"
VISCOSITY_SWEEP_SPEC_ID = "docs/RFS_MB0_HORIZON_TRANSPORT_VISCOSITY_HORIZON_BREADTH_SWEEP_SPEC.md"
SUBSTRATE_UNTETHERING_SPEC_ID = "docs/RFS_MB0_SUBSTRATE_UNTETHERING_TRANSITION_ENERGY_SWEEP_SPEC.md"
TRANSITION_ENERGY_CHARACTERIZATION_SPEC_ID = "docs/RFS_MB0_TRANSITION_ENERGY_SUBSTRATE_CHARACTERIZATION_RUN_SPEC.md"
ASYMMETRY_LADDER_SPEC_ID = "docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md"
MAX_ENTROPY_PREFLIGHT_SPEC_ID = "docs/RFS_MB0_MAX_ENTROPY_LOCAL_TRANSITION_PREFLIGHT_SPEC.md"
TOP_M_GEOMETRY_AUDIT_SPEC_ID = "docs/RFS_MB0_TOP_M_GEOMETRY_AUDIT_SPEC.md"
RUNNER_MODULE = "omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair"

DEFAULT_HORIZON_PAIRS = ((0, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 24), (24, 32))
H128_HORIZON_PAIRS = (*DEFAULT_HORIZON_PAIRS, (32, 48), (48, 64), (64, 96), (96, 128))
HORIZON_10X_PAIRS = ((16, 24), (24, 32), (64, 96), (96, 128), (128, 256), (256, 512), (512, 1024), (1024, 1280))
VISCOSITY_LADDER_HORIZON_PAIRS = ((4, 8), (8, 16), (16, 24), (24, 32), (64, 96), (96, 128))
BREADTH_HORIZON_CROSS_PAIRS = ((96, 128), (128, 256), (256, 512), (512, 1024))
TRANSITION_ENERGY_CHARACTERIZATION = "transition_energy_characterization"
ASYMMETRY_LADDER = "asymmetry_ladder"
MAX_ENTROPY_PREFLIGHT = "max_entropy_preflight"
TOP_M_GEOMETRY_AUDIT = "top_m_geometry_audit"
SWEEP_KINDS = frozenset({"horizon_10x", "breadth", "viscosity_ladder", "breadth_horizon_cross", "substrate_untethering", TRANSITION_ENERGY_CHARACTERIZATION, ASYMMETRY_LADDER, MAX_ENTROPY_PREFLIGHT, TOP_M_GEOMETRY_AUDIT})

COMMON_OUTPUTS = (
    "horizon_transport_matrix_manifest.csv",
    "horizon_transport_matrix_entries.csv",
    "horizon_transport_matrix_sparse.npz",
    "horizon_transport_raw_state_frontier_samples.csv",
    "horizon_transport_raw_state_frontier_sparse.npz",
    "substrate_family_manifest.csv",
    "substrate_family_variant_manifest.csv",
    "transition_energy_family_summary.csv",
    "transition_energy_parameter_summary.csv",
    "substrate_capacity_by_family.csv",
    "substrate_capacity_by_family_variant.csv",
    "substrate_generation_diagnostics.csv",
    "horizon_transport_row_item_manifest.csv",
    "horizon_transport_column_item_manifest.csv",
    "horizon_transport_coverage.csv",
    "horizon_transport_matrix_summary.csv",
    "horizon_transport_svd_summary.csv",
    "horizon_transport_subspace_alignment.csv",
    "horizon_transport_participation_summary.csv",
    "horizon_transport_entropy_summary.csv",
    "horizon_transport_detector_null_summary.csv",
    "horizon_transport_detector_null_anatomy.csv",
    "horizon_transport_detector_null_gate_results.csv",
    "horizon_transport_matched_marginal_summary.csv",
    "horizon_transport_fixture_results.csv",
    "horizon_transport_perturbation_manifest.csv",
    "horizon_transport_response_profile_summary.csv",
    "horizon_transport_response_classification.csv",
    "horizon_transport_response_flags.csv",
    "response_class_by_strength_and_horizon_pair.csv",
    "horizon_response_threshold_table.csv",
    "horizon_transport_terminal_saturation_summary.csv",
    "horizon_transport_saturation_by_horizon_pair.csv",
    "horizon_transport_response_fixture_summary.csv",
    "horizon_transport_viscosity_summary.csv",
    "horizon_transport_response_diversity_summary.csv",
    "horizon_transport_by_probe_summary.csv",
    "horizon_transport_by_flow_mode_summary.csv",
    "horizon_transport_by_horizon_pair_summary.csv",
    "horizon_transport_context_recommendation.csv",
    "horizon_transport_by_substrate_family_summary.csv",
    "horizon_transport_by_substrate_family_variant_summary.csv",
    "response_by_substrate_family.csv",
    "response_by_substrate_family_variant.csv",
    "response_by_budget_kind.csv",
    "response_by_potential_smoothness.csv",
    "response_by_potential_beta.csv",
    "response_by_asymmetry_family.csv",
    "response_by_asymmetry_variant.csv",
    "response_by_directional_alpha.csv",
    "response_by_asymmetry_field_smoothness.csv",
    "response_by_macro_invariant_kind.csv",
    "response_by_macro_invariant_beta.csv",
    "selected_edge_overlap_by_beta.csv",
    "response_by_alpha_beta_pair.csv",
    "matched_null_pass_by_asymmetry_family.csv",
    "matched_null_pass_by_asymmetry_variant.csv",
    "aligned_amplification_by_substrate_family.csv",
    "response_diversity_by_substrate_family.csv",
    "response_diversity_by_substrate_family_variant.csv",
    "transport_viscosity_by_substrate_family.csv",
    "transport_viscosity_by_substrate_family_variant.csv",
    "matched_null_pass_by_substrate_family.csv",
    "matched_null_pass_by_substrate_family_variant.csv",
    "max_entropy_constraint_manifest.csv",
    "max_entropy_marginal_match_summary.csv",
    "max_entropy_sampler_diagnostics.csv",
    "max_entropy_edge_match_to_calibration.csv",
    "response_by_max_entropy_family.csv",
    "response_by_equivalent_beta_target.csv",
    "paired_baseline_availability_by_max_entropy_variant.csv",
    "top_m_geometry_sampler_diagnostics.csv",
    "top_m_geometry_rank_energy_match_summary.csv",
    "top_m_geometry_per_state_rank_bucket_match_summary.csv",
    "top_m_geometry_edge_match_to_calibration.csv",
    "response_by_sampler_family.csv",
    "response_by_beta_or_temperature.csv",
)

STRUCTURE_DESTROYING_NULL_FAMILIES = (
    "context_shuffle_transport_null",
    "horizon_pair_shuffle_transport_null",
)
MARGINAL_MATCHED_NULL_FAMILIES = (
    "row_marginal_matched_transport_null",
    "column_marginal_matched_transport_null",
    "row_column_marginal_matched_transport_null",
)
INTERPRETATION_CONTROL_FAMILIES = (
    "label_shuffle_transport_interpretation_control",
)
DETECTOR_NULL_FAMILIES = (
    *STRUCTURE_DESTROYING_NULL_FAMILIES,
    *MARGINAL_MATCHED_NULL_FAMILIES,
    *INTERPRETATION_CONTROL_FAMILIES,
)
DETECTOR_STATISTICS = (
    "positive_or_nonzero_spectral_mass",
    "singular_spectral_mass",
    "effective_rank",
    "singular_effective_rank",
    "transport_concentration",
    "marginal_residual_fraction",
)


def run_kind(args: object) -> str:
    sweep_kind = str(getattr(args, "sweep_kind", "") or "")
    if sweep_kind:
        return sweep_kind
    if bool(getattr(args, "h128_scaleup", False)):
        return "h128"
    if bool(getattr(args, "expansion_smoke", False)):
        return "expansion"
    return "repair"


def active_spec_id(args: object) -> str:
    if str(getattr(args, "sweep_kind", "") or "") == TOP_M_GEOMETRY_AUDIT:
        return TOP_M_GEOMETRY_AUDIT_SPEC_ID
    if str(getattr(args, "sweep_kind", "") or "") == MAX_ENTROPY_PREFLIGHT:
        return MAX_ENTROPY_PREFLIGHT_SPEC_ID
    if str(getattr(args, "sweep_kind", "") or "") == ASYMMETRY_LADDER:
        return ASYMMETRY_LADDER_SPEC_ID
    if str(getattr(args, "sweep_kind", "") or "") == TRANSITION_ENERGY_CHARACTERIZATION:
        return TRANSITION_ENERGY_CHARACTERIZATION_SPEC_ID
    if str(getattr(args, "sweep_kind", "") or "") == "substrate_untethering":
        return SUBSTRATE_UNTETHERING_SPEC_ID
    if str(getattr(args, "sweep_kind", "") or ""):
        return VISCOSITY_SWEEP_SPEC_ID
    if bool(getattr(args, "h128_scaleup", False)):
        return H128_SPEC_ID
    if bool(getattr(args, "expansion_smoke", False)):
        return EXPANSION_SPEC_ID
    return MATCHED_NULL_SPEC_ID


def artifact_prefix(kind: str) -> str:
    if kind == "horizon_10x":
        return "horizon_transport_10x_horizon"
    if kind == "breadth":
        return "horizon_transport_breadth"
    if kind == "viscosity_ladder":
        return "horizon_transport_viscosity_ladder"
    if kind == "breadth_horizon_cross":
        return "horizon_transport_breadth_horizon_cross"
    if kind == "substrate_untethering":
        return "substrate_untethering"
    if kind == TRANSITION_ENERGY_CHARACTERIZATION:
        return "transition_energy_characterization"
    if kind == ASYMMETRY_LADDER:
        return "asymmetry_ladder"
    if kind == MAX_ENTROPY_PREFLIGHT:
        return "max_entropy_preflight"
    if kind == TOP_M_GEOMETRY_AUDIT:
        return "top_m_geometry_audit"
    if kind == "h128":
        return "horizon_transport_h128"
    return "horizon_transport_expansion" if kind == "expansion" else "horizon_transport_repair"


def run_phase(kind: str) -> str:
    if kind == "horizon_10x":
        return "rfs_mb0_horizon_transport_10x_horizon_sweep"
    if kind == "breadth":
        return "rfs_mb0_horizon_transport_breadth_sweep"
    if kind == "viscosity_ladder":
        return "rfs_mb0_horizon_transport_viscosity_ladder"
    if kind == "breadth_horizon_cross":
        return "rfs_mb0_horizon_transport_breadth_horizon_cross_mini"
    if kind == "substrate_untethering":
        return "rfs_mb0_substrate_untethering_transition_energy_sweep"
    if kind == TRANSITION_ENERGY_CHARACTERIZATION:
        return "rfs_mb0_transition_energy_substrate_characterization"
    if kind == ASYMMETRY_LADDER:
        return "rfs_mb0_asymmetry_ladder_transition_energy"
    if kind == MAX_ENTROPY_PREFLIGHT:
        return "rfs_mb0_max_entropy_local_transition_preflight"
    if kind == TOP_M_GEOMETRY_AUDIT:
        return "rfs_mb0_top_m_geometry_audit"
    if kind == "h128":
        return "rfs_mb0_horizon_transport_response_surface_h128_scaleup"
    return "rfs_mb0_horizon_transport_expansion_smoke" if kind == "expansion" else "rfs_mb0_horizon_transport_spectral_response_repair"


def run_config_filename(kind: str) -> str:
    return f"{artifact_prefix(kind)}_run_config.json"


def status_filename(kind: str) -> str:
    return f"{artifact_prefix(kind)}_status.json"


def progress_filename(kind: str) -> str:
    return f"{artifact_prefix(kind)}_progress_checkpoints.csv"


def errors_filename(kind: str) -> str:
    return f"{artifact_prefix(kind)}_errors.csv"


def manifest_filename(kind: str) -> str:
    return f"{artifact_prefix(kind)}_output_manifest.json"


def report_filename(kind: str) -> str:
    if kind == "horizon_10x":
        return "rfs_mb0_horizon_transport_10x_horizon_sweep_result.md"
    if kind == "breadth":
        return "rfs_mb0_horizon_transport_breadth_sweep_result.md"
    if kind == "viscosity_ladder":
        return "rfs_mb0_horizon_transport_viscosity_ladder_result.md"
    if kind == "breadth_horizon_cross":
        return "rfs_mb0_horizon_transport_breadth_horizon_cross_mini_result.md"
    if kind == "substrate_untethering":
        return "rfs_mb0_substrate_untethering_transition_energy_sweep_result.md"
    if kind == TRANSITION_ENERGY_CHARACTERIZATION:
        return "rfs_mb0_transition_energy_substrate_characterization_result.md"
    if kind == ASYMMETRY_LADDER:
        return "rfs_mb0_asymmetry_ladder_transition_energy_result.md"
    if kind == MAX_ENTROPY_PREFLIGHT:
        return "rfs_mb0_max_entropy_local_transition_preflight_result.md"
    if kind == TOP_M_GEOMETRY_AUDIT:
        return "rfs_mb0_top_m_geometry_audit_result.md"
    if kind == "h128":
        return "rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md"
    if kind == "expansion":
        return "rfs_mb0_horizon_transport_expansion_smoke_result.md"
    return "rfs_mb0_horizon_transport_spectral_response_repair_result.md"


def status_run_kind(status: dict[str, object]) -> str:
    return str(status.get("run_kind", "repair"))


def parse_horizon_pairs(raw: str, *, use_h128: bool, sweep_kind: str = "") -> tuple[tuple[int, int], ...]:
    if not raw.strip():
        return default_horizon_pairs(use_h128=use_h128, sweep_kind=sweep_kind)
    pairs: list[tuple[int, int]] = []
    for item in raw.split(","):
        value = item.strip()
        if not value:
            continue
        left, right = value.split("->", 1)
        pairs.append((int(left.strip()), int(right.strip())))
    return tuple(pairs) or default_horizon_pairs(use_h128=use_h128, sweep_kind=sweep_kind)


def default_horizon_pairs(*, use_h128: bool, sweep_kind: str = "") -> tuple[tuple[int, int], ...]:
    if sweep_kind == "horizon_10x":
        return HORIZON_10X_PAIRS
    if sweep_kind == "viscosity_ladder":
        return VISCOSITY_LADDER_HORIZON_PAIRS
    if sweep_kind == "breadth_horizon_cross":
        return BREADTH_HORIZON_CROSS_PAIRS
    if sweep_kind in {"substrate_untethering", TRANSITION_ENERGY_CHARACTERIZATION, ASYMMETRY_LADDER, MAX_ENTROPY_PREFLIGHT, TOP_M_GEOMETRY_AUDIT}:
        return H128_HORIZON_PAIRS
    if sweep_kind == "breadth":
        return H128_HORIZON_PAIRS
    return H128_HORIZON_PAIRS if use_h128 else DEFAULT_HORIZON_PAIRS


def attach_horizon_pairs(jobs: list[dict[str, object]], horizon_pairs: tuple[tuple[int, int], ...]) -> None:
    serializable_pairs = tuple((int(left), int(right)) for left, right in horizon_pairs)
    for job in jobs:
        job["horizon_pairs"] = serializable_pairs
