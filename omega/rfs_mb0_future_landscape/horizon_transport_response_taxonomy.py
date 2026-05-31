"""Fixture-backed response taxonomy for horizon-transport perturbations.

The taxonomy is deliberately neutral: it classifies how a transport matrix
changes under a candidate perturbation. It does not classify agents, values,
identity, or Omega-compatible structure.
"""

from __future__ import annotations

ALIGNMENT_STABLE_MIN = 0.80
ALIGNMENT_LOW_MAX = 0.50
MASS_COLLAPSE_MAX_DELTA = -0.50
MASS_WEAKENED_MAX_DELTA = -0.15
MASS_AMPLIFIED_MIN_DELTA = 0.15
ENTROPY_REOPENED_MIN_DELTA = 0.20
LARGE_ENTRY_RESPONSE_MIN_MAGNITUDE = 0.25

RESPONSE_CLASS_RESOLUTION_MISMATCH = "transport_resolution_mismatch"
RESPONSE_CLASS_BASELINE_MISSING = "transport_baseline_missing"
RESPONSE_CLASS_INSUFFICIENT_COMMON_ITEMS = "transport_insufficient_common_items"
RESPONSE_CLASS_RESPONSE_UNDERPOWERED = "transport_response_underpowered"
RESPONSE_CLASS_COLLAPSES = "transport_collapses"
RESPONSE_CLASS_WEAKENED = "transport_weakened"
RESPONSE_CLASS_REOPENS = "transport_reopens"
RESPONSE_CLASS_REROUTED = "transport_rerouted"
RESPONSE_CLASS_AMPLIFIED_ALIGNED = "transport_amplified_aligned"
RESPONSE_CLASS_STABLE = "transport_stable"
RESPONSE_CLASS_CONTROL_EQUIVALENT = "transport_control_equivalent"

MEASUREMENT_LIMIT_RESPONSE_CLASSES = frozenset({
    RESPONSE_CLASS_RESOLUTION_MISMATCH,
    RESPONSE_CLASS_BASELINE_MISSING,
    RESPONSE_CLASS_INSUFFICIENT_COMMON_ITEMS,
    RESPONSE_CLASS_RESPONSE_UNDERPOWERED,
})
INTERPRETABLE_RESPONSE_CLASSES = frozenset({
    RESPONSE_CLASS_COLLAPSES,
    RESPONSE_CLASS_WEAKENED,
    RESPONSE_CLASS_REOPENS,
    RESPONSE_CLASS_REROUTED,
    RESPONSE_CLASS_AMPLIFIED_ALIGNED,
    RESPONSE_CLASS_STABLE,
    RESPONSE_CLASS_CONTROL_EQUIVALENT,
})

RESPONSE_CLASS_DESCRIPTIONS = {
    RESPONSE_CLASS_RESOLUTION_MISMATCH: "baseline and perturbation did not share enough row/column support",
    RESPONSE_CLASS_BASELINE_MISSING: "paired baseline matrix was unavailable for this perturbation context",
    RESPONSE_CLASS_INSUFFICIENT_COMMON_ITEMS: "paired baseline and perturbation shared too little row/column support",
    RESPONSE_CLASS_RESPONSE_UNDERPOWERED: "response statistics were insufficient for classification",
    RESPONSE_CLASS_COLLAPSES: "transport mass collapsed relative to baseline",
    RESPONSE_CLASS_WEAKENED: "transport mass weakened without full collapse",
    RESPONSE_CLASS_REOPENS: "transport entropy reopened enough to dominate the response",
    RESPONSE_CLASS_REROUTED: "transport subspace shifted without mass collapse",
    RESPONSE_CLASS_AMPLIFIED_ALIGNED: "transport mass grew while baseline/perturbation subspaces stayed aligned",
    RESPONSE_CLASS_STABLE: "transport stayed aligned with only small mass change",
    RESPONSE_CLASS_CONTROL_EQUIVALENT: "response did not meet a sharper interpretable class",
}


def response_flags(left_alignment: float, right_alignment: float, mass_delta: float, entropy_delta: float, magnitude: float) -> str:
    flags = []
    mean_alignment = (left_alignment + right_alignment) / 2.0
    if mean_alignment >= ALIGNMENT_STABLE_MIN:
        flags.append("aligned")
    if mean_alignment < ALIGNMENT_STABLE_MIN:
        flags.append("subspace_shifted")
    if mean_alignment < ALIGNMENT_LOW_MAX:
        flags.append("low_alignment")
    if mass_delta <= MASS_COLLAPSE_MAX_DELTA:
        flags.append("mass_collapse")
    elif mass_delta <= MASS_WEAKENED_MAX_DELTA:
        flags.append("mass_weakened")
    elif mass_delta >= MASS_AMPLIFIED_MIN_DELTA:
        flags.append("mass_amplified")
    if entropy_delta >= ENTROPY_REOPENED_MIN_DELTA:
        flags.append("entropy_reopened")
    if magnitude >= LARGE_ENTRY_RESPONSE_MIN_MAGNITUDE:
        flags.append("large_entry_response")
    return ",".join(flags) if flags else "none"


def classify_response(row: dict[str, object]) -> str:
    """Classify a perturbation response.

    The ordering is part of the fixture contract. Collapse/weakening dominate
    before entropy reopening; reroute requires subspace shift without collapse;
    aligned amplification is intentionally distinct from control equivalence.
    """
    response_status = str(row.get("response_status", ""))
    if response_status == "baseline_missing":
        return RESPONSE_CLASS_BASELINE_MISSING
    if response_status == "insufficient_common_transport_items":
        return RESPONSE_CLASS_INSUFFICIENT_COMMON_ITEMS
    if response_status != "computed":
        return RESPONSE_CLASS_RESOLUTION_MISMATCH
    alignment = _float_or_zero(row.get("mean_subspace_alignment"))
    mass_delta = _float_or_zero(row.get("spectral_mass_delta_fraction"))
    entropy_delta = _float_or_zero(row.get("transport_entropy_delta"))
    if mass_delta <= MASS_COLLAPSE_MAX_DELTA:
        return RESPONSE_CLASS_COLLAPSES
    if mass_delta <= MASS_WEAKENED_MAX_DELTA:
        return RESPONSE_CLASS_WEAKENED
    if entropy_delta >= ENTROPY_REOPENED_MIN_DELTA:
        return RESPONSE_CLASS_REOPENS
    if alignment < ALIGNMENT_STABLE_MIN and mass_delta > MASS_WEAKENED_MAX_DELTA:
        return RESPONSE_CLASS_REROUTED
    if alignment >= ALIGNMENT_STABLE_MIN and mass_delta >= MASS_AMPLIFIED_MIN_DELTA:
        return RESPONSE_CLASS_AMPLIFIED_ALIGNED
    if alignment >= ALIGNMENT_STABLE_MIN and abs(mass_delta) <= MASS_AMPLIFIED_MIN_DELTA:
        return RESPONSE_CLASS_STABLE
    return RESPONSE_CLASS_CONTROL_EQUIVALENT


def is_interpretable_response(response_class: object) -> bool:
    return str(response_class) not in MEASUREMENT_LIMIT_RESPONSE_CLASSES


def _float_or_zero(value: object) -> float:
    try:
        if value == "":
            return 0.0
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
