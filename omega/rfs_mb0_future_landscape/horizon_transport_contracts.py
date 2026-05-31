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
RUNNER_MODULE = "omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair"

DEFAULT_HORIZON_PAIRS = ((0, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 24), (24, 32))
H128_HORIZON_PAIRS = (*DEFAULT_HORIZON_PAIRS, (32, 48), (48, 64), (64, 96), (96, 128))

COMMON_OUTPUTS = (
    "horizon_transport_matrix_manifest.csv",
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
    "horizon_transport_by_probe_summary.csv",
    "horizon_transport_by_flow_mode_summary.csv",
    "horizon_transport_by_horizon_pair_summary.csv",
    "horizon_transport_context_recommendation.csv",
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
    if bool(getattr(args, "h128_scaleup", False)):
        return "h128"
    if bool(getattr(args, "expansion_smoke", False)):
        return "expansion"
    return "repair"


def active_spec_id(args: object) -> str:
    if bool(getattr(args, "h128_scaleup", False)):
        return H128_SPEC_ID
    if bool(getattr(args, "expansion_smoke", False)):
        return EXPANSION_SPEC_ID
    return MATCHED_NULL_SPEC_ID


def artifact_prefix(kind: str) -> str:
    if kind == "h128":
        return "horizon_transport_h128"
    return "horizon_transport_expansion" if kind == "expansion" else "horizon_transport_repair"


def run_phase(kind: str) -> str:
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
    if kind == "h128":
        return "rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md"
    if kind == "expansion":
        return "rfs_mb0_horizon_transport_expansion_smoke_result.md"
    return "rfs_mb0_horizon_transport_spectral_response_repair_result.md"


def status_run_kind(status: dict[str, object]) -> str:
    return str(status.get("run_kind", "repair"))


def parse_horizon_pairs(raw: str, *, use_h128: bool) -> tuple[tuple[int, int], ...]:
    if not raw.strip():
        return H128_HORIZON_PAIRS if use_h128 else DEFAULT_HORIZON_PAIRS
    pairs: list[tuple[int, int]] = []
    for item in raw.split(","):
        value = item.strip()
        if not value:
            continue
        left, right = value.split("->", 1)
        pairs.append((int(left.strip()), int(right.strip())))
    return tuple(pairs) or (H128_HORIZON_PAIRS if use_h128 else DEFAULT_HORIZON_PAIRS)


def attach_horizon_pairs(jobs: list[dict[str, object]], horizon_pairs: tuple[tuple[int, int], ...]) -> None:
    serializable_pairs = tuple((int(left), int(right)) for left, right in horizon_pairs)
    for job in jobs:
        job["horizon_pairs"] = serializable_pairs
