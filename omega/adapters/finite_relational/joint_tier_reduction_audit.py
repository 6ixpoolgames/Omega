"""Finite joint-tier reduction audit.

This module calibrates the recent joint-tier instruments against planted null
coordinates and narrow reduction attempts. It is an audit harness, not a theory
of value, standing, population ethics, plurality, or Omega validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from omega.adapters.finite_relational.colonization_axis import (
    branching_system,
    colonization_axis_summary,
    control_panel,
    profile_summary,
    scalar_shadow_check,
)
from omega.adapters.finite_relational.ensemble_span import (
    ensemble_span_summary,
    marginal_summary,
    orthogonal_ensemble,
    redundant_ensemble,
)
from omega.adapters.finite_relational.joint_recovery_compatibility import (
    compatible_vs_interfering_witness,
    joint_recovery_compatibility_summary,
)
from omega.adapters.finite_relational.relational_composability import (
    compatible_vs_blocked_witness,
    graph_structure_robustness_witness,
)


PROTOCOL_DOC = "docs/research_notes/omega_theory/joint_tier_reduction_audit_protocol_v0.md"


@dataclass(frozen=True)
class PlantedNullResult:
    instrument: str
    planted_coordinate: str
    reduction_basis: str
    verdict: str
    passes: bool
    evidence: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "instrument": self.instrument,
            "planted_coordinate": self.planted_coordinate,
            "reduction_basis": self.reduction_basis,
            "verdict": self.verdict,
            "passes": self.passes,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class ReductionAttemptResult:
    target: str
    hypothesis: str
    verdict: str
    passes: bool
    evidence: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "hypothesis": self.hypothesis,
            "verdict": self.verdict,
            "passes": self.passes,
            "evidence": self.evidence,
        }


def ensemble_span_planted_null() -> PlantedNullResult:
    """A scalar amount coordinate should reduce to the marginal summary."""

    left = marginal_summary(redundant_ensemble())
    right = marginal_summary(orthogonal_ensemble())
    reduces = left.total_l1_amount == right.total_l1_amount
    return PlantedNullResult(
        instrument="ensemble_span",
        planted_coordinate="total_l1_amount",
        reduction_basis="marginal_summary.total_l1_amount",
        verdict="reduces" if reduces else "review",
        passes=reduces,
        evidence={
            "left_total_l1_amount": left.total_l1_amount,
            "right_total_l1_amount": right.total_l1_amount,
            "candidate_span_verdict": ensemble_span_summary()["verdict"],
            "note": "This is a planted reducible scalar, not the ensemble-span axis.",
        },
    )


def relational_edge_count_planted_null() -> PlantedNullResult:
    """An edge-count coordinate should reduce to compatible-pair count."""

    witness = compatible_vs_blocked_witness()
    left_count = witness["left_compatibility_profile"]["compatible_pair_count"]
    right_count = witness["right_compatibility_profile"]["compatible_pair_count"]
    reduces = left_count != right_count and witness["compatibility_separates"]
    return PlantedNullResult(
        instrument="relational_composability",
        planted_coordinate="compatible_pair_count",
        reduction_basis="CompatibilityProfile.compatible_pair_count",
        verdict="reduces" if reduces else "review",
        passes=reduces,
        evidence={
            "left_pair_count": left_count,
            "right_pair_count": right_count,
            "compatibility_separates": witness["compatibility_separates"],
            "note": "This planted coordinate is only edge count; it is not the v0.1 component-structure witness.",
        },
    )


def joint_recovery_missing_count_planted_null() -> PlantedNullResult:
    """A missing-fact-count coordinate should reduce to the recovery profile."""

    witness = compatible_vs_interfering_witness()
    left_missing = len(witness["left_recovery_profile"]["joint_missing_fact_ids"])
    right_missing = len(witness["right_recovery_profile"]["joint_missing_fact_ids"])
    reduces = left_missing != right_missing and witness["joint_recovery_separates"]
    return PlantedNullResult(
        instrument="joint_recovery_compatibility",
        planted_coordinate="joint_missing_fact_count",
        reduction_basis="RecoveryProfile.joint_missing_fact_ids",
        verdict="reduces" if reduces else "review",
        passes=reduces,
        evidence={
            "left_missing_count": left_missing,
            "right_missing_count": right_missing,
            "joint_recovery_separates": witness["joint_recovery_separates"],
            "note": "This planted coordinate is a direct recovery-profile scalar.",
        },
    )


def colonization_control_panel_planted_null() -> PlantedNullResult:
    """A viable-state-count coordinate should reduce to the control panel."""

    system = branching_system()
    panel = control_panel(system)
    profile = profile_summary(system)
    reduces = panel["viable_state_count"] == len(system.viable)
    return PlantedNullResult(
        instrument="colonization_axis",
        planted_coordinate="viable_state_count",
        reduction_basis="colonization control_panel.viable_state_count",
        verdict="reduces" if reduces else "review",
        passes=reduces,
        evidence={
            "system": system.system_id,
            "control_panel_viable_state_count": panel["viable_state_count"],
            "profile_max_chain_depth": profile["max_chain_depth"],
            "note": "This planted coordinate is a declared control-panel quantity, not colonization structure.",
        },
    )


def planted_null_results() -> tuple[PlantedNullResult, ...]:
    return (
        ensemble_span_planted_null(),
        relational_edge_count_planted_null(),
        joint_recovery_missing_count_planted_null(),
        colonization_control_panel_planted_null(),
    )


def relational_composability_reduction_attempt() -> ReductionAttemptResult:
    robustness = graph_structure_robustness_witness()
    survives = (
        robustness["same_compatible_pair_count"]
        and robustness["same_degree_sequence"]
        and robustness["component_structure_separates"]
    )
    return ReductionAttemptResult(
        target="relational_composability",
        hypothesis="reduces to pure span plus edge count or degree sequence",
        verdict="survives_simple_graph_scalar_reduction" if survives else "review",
        passes=survives,
        evidence={
            "same_compatible_pair_count": robustness["same_compatible_pair_count"],
            "same_degree_sequence": robustness["same_degree_sequence"],
            "component_structure_separates": robustness["component_structure_separates"],
            "scope_note": (
                "This does not prove independence from all graph summaries; it blocks "
                "the cheap pair-count and degree-sequence reductions already tested."
            ),
        },
    )


def colonization_reduction_attempt() -> ReductionAttemptResult:
    summary = colonization_axis_summary()
    shadow = scalar_shadow_check()
    survives = (
        summary["candidate_pair"]["control_panel_equal"]
        and shadow["scalar_equal"]
        and shadow["order_separates"]
    )
    return ReductionAttemptResult(
        target="colonization_axis",
        hypothesis="reduces to control panel plus simple scalar chain shadows",
        verdict="survives_scalar_shadow_reduction_lens_debt_open" if survives else "review",
        passes=survives,
        evidence={
            "control_panel_equal": summary["candidate_pair"]["control_panel_equal"],
            "scalar_shadow_equal": shadow["scalar_equal"],
            "scalar_shadow_order_separates": shadow["order_separates"],
            "lens_debt": (
                "Global lens invariance and sound-quotient-lattice reduction remain open."
            ),
        },
    )


def joint_recovery_reduction_attempt() -> ReductionAttemptResult:
    summary = joint_recovery_compatibility_summary()
    candidate = summary["candidate_pair"]
    reduces = (
        candidate["individual_recovery_profiles_equal"]
        and candidate["joint_recovery_separates"]
        and candidate["left_recovery_profile"]["joint_recovery_succeeds"]
        != candidate["right_recovery_profile"]["joint_recovery_succeeds"]
    )
    return ReductionAttemptResult(
        target="joint_recovery_compatibility",
        hypothesis="factors as coupling surface plus registered recovery labels",
        verdict="bridge_not_independent_axis" if reduces else "review",
        passes=reduces,
        evidence={
            "individual_recovery_profiles_equal": candidate["individual_recovery_profiles_equal"],
            "joint_recovery_separates": candidate["joint_recovery_separates"],
            "left_joint_recovery_succeeds": candidate["left_recovery_profile"]["joint_recovery_succeeds"],
            "right_joint_recovery_succeeds": candidate["right_recovery_profile"]["joint_recovery_succeeds"],
            "scope_note": (
                "This supports treating joint-recovery compatibility as a recovery-grounded "
                "bridge instrument, not as a new independent coordinate."
            ),
        },
    )


def reduction_attempt_results() -> tuple[ReductionAttemptResult, ...]:
    return (
        relational_composability_reduction_attempt(),
        colonization_reduction_attempt(),
        joint_recovery_reduction_attempt(),
    )


def joint_tier_reduction_audit_summary() -> dict[str, Any]:
    planted = planted_null_results()
    reductions = reduction_attempt_results()
    planted_pass = all(row.passes and row.verdict == "reduces" for row in planted)
    reductions_pass = all(row.passes for row in reductions)
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "calibrated" if planted_pass and reductions_pass else "review",
        "planted_nulls": [row.as_dict() for row in planted],
        "reduction_attempts": [row.as_dict() for row in reductions],
        "planted_nulls_pass": planted_pass,
        "reduction_attempts_pass": reductions_pass,
        "not_attacked_this_round": [
            "ensemble_span independent-axis reduction",
            "full global lens-invariance theorem",
            "CompensationClaim / NOLP verdicts",
        ],
        "not_claimed": [
            "value",
            "standing",
            "agency",
            "population ethics",
            "plurality theory",
            "aggregation",
            "patienthood",
            "Omega validation",
        ],
    }


def planted_null_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "instrument": row["instrument"],
            "planted_coordinate": row["planted_coordinate"],
            "reduction_basis": row["reduction_basis"],
            "verdict": row["verdict"],
            "passes": row["passes"],
        }
        for row in summary["planted_nulls"]
    ]


def reduction_attempt_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "target": row["target"],
            "hypothesis": row["hypothesis"],
            "verdict": row["verdict"],
            "passes": row["passes"],
        }
        for row in summary["reduction_attempts"]
    ]
