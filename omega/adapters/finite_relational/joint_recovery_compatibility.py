"""Finite joint-recovery compatibility instrument.

This module implements the v0 bridge from registered coupling profiles to
recovery-grounded compatibility. It checks whether individual recovery profiles
and individual vector/span surfaces can be held fixed while joint recovery
under coupling separates. It is not a theory of value, standing, plurality,
moral aggregation, patienthood, or Omega validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from omega.adapters.finite_relational.ensemble_span import (
    Axis,
    Ensemble,
    ValuerVector,
    axes_ab,
    compare_ensembles,
    full_vector_census,
    marginal_summary,
    span_equivalent,
    span_profile,
)


PROTOCOL_DOC = "docs/research_notes/omega_theory/joint_recovery_compatibility_protocol_v0.md"


@dataclass(frozen=True)
class RecoveryFact:
    fact_id: str


@dataclass(frozen=True)
class ParticipantRecovery:
    participant_id: str
    required_facts: tuple[RecoveryFact, ...]
    individually_recovered: tuple[RecoveryFact, ...]

    def required_ids(self) -> tuple[str, ...]:
        return tuple(sorted(fact.fact_id for fact in self.required_facts))

    def recovered_ids(self) -> tuple[str, ...]:
        return tuple(sorted(fact.fact_id for fact in self.individually_recovered))

    def individually_succeeds(self) -> bool:
        return set(self.required_ids()).issubset(self.recovered_ids())

    def as_dict(self) -> dict[str, Any]:
        return {
            "participant_id": self.participant_id,
            "required_facts": list(self.required_ids()),
            "individually_recovered": list(self.recovered_ids()),
            "individually_succeeds": self.individually_succeeds(),
        }


@dataclass(frozen=True)
class CouplingMode:
    mode_id: str
    joint_recovered: tuple[RecoveryFact, ...]

    def recovered_ids(self) -> tuple[str, ...]:
        return tuple(sorted(fact.fact_id for fact in self.joint_recovered))


@dataclass(frozen=True)
class JointRecoveryCase:
    case_id: str
    axes: tuple[Axis, ...]
    vectors: tuple[ValuerVector, ...]
    participants: tuple[ParticipantRecovery, ...]
    coupling: CouplingMode

    def __post_init__(self) -> None:
        width = len(self.axes)
        vector_ids = {vector.vector_id for vector in self.vectors}
        participant_ids = {participant.participant_id for participant in self.participants}
        if len(vector_ids) != len(self.vectors):
            raise ValueError("vector ids must be unique")
        if vector_ids != participant_ids:
            raise ValueError("participant ids must match vector ids")
        for vector in self.vectors:
            if len(vector.coordinates) != width:
                raise ValueError(
                    f"vector {vector.vector_id!r} has width {len(vector.coordinates)}, expected {width}"
                )

    def as_individual_ensemble(self) -> Ensemble:
        return Ensemble(
            ensemble_id=f"{self.case_id}_individual_surface",
            axes=self.axes,
            vectors=self.vectors,
        )


@dataclass(frozen=True)
class RecoveryProfile:
    participant_profiles: tuple[dict[str, Any], ...]
    required_fact_ids: tuple[str, ...]
    individually_recovered_fact_ids: tuple[str, ...]
    all_individual_recovery_succeeds: bool
    joint_recovered_fact_ids: tuple[str, ...]
    joint_recovery_succeeds: bool
    joint_missing_fact_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "participant_profiles": list(self.participant_profiles),
            "required_fact_ids": list(self.required_fact_ids),
            "individually_recovered_fact_ids": list(self.individually_recovered_fact_ids),
            "all_individual_recovery_succeeds": self.all_individual_recovery_succeeds,
            "joint_recovered_fact_ids": list(self.joint_recovered_fact_ids),
            "joint_recovery_succeeds": self.joint_recovery_succeeds,
            "joint_missing_fact_ids": list(self.joint_missing_fact_ids),
        }


def fact_a() -> RecoveryFact:
    return RecoveryFact("A_recovery_fact")


def fact_b() -> RecoveryFact:
    return RecoveryFact("B_recovery_fact")


def participant_a() -> ParticipantRecovery:
    fact = fact_a()
    return ParticipantRecovery(
        participant_id="vA",
        required_facts=(fact,),
        individually_recovered=(fact,),
    )


def participant_b() -> ParticipantRecovery:
    fact = fact_b()
    return ParticipantRecovery(
        participant_id="vB",
        required_facts=(fact,),
        individually_recovered=(fact,),
    )


def participant_b_unrecovered() -> ParticipantRecovery:
    return ParticipantRecovery(
        participant_id="vB",
        required_facts=(fact_b(),),
        individually_recovered=(),
    )


def vector_surface() -> tuple[ValuerVector, ...]:
    return (
        ValuerVector("vA", (1, 0)),
        ValuerVector("vB", (0, 1)),
    )


def compatible_joint_recovery_case() -> JointRecoveryCase:
    return JointRecoveryCase(
        case_id="compatible_joint_recovery",
        axes=axes_ab(),
        vectors=vector_surface(),
        participants=(participant_a(), participant_b()),
        coupling=CouplingMode(
            mode_id="joint_recovers_both",
            joint_recovered=(fact_a(), fact_b()),
        ),
    )


def interfering_joint_recovery_case() -> JointRecoveryCase:
    return JointRecoveryCase(
        case_id="interfering_joint_recovery",
        axes=axes_ab(),
        vectors=vector_surface(),
        participants=(participant_a(), participant_b()),
        coupling=CouplingMode(
            mode_id="joint_drops_b",
            joint_recovered=(fact_a(),),
        ),
    )


def duplicate_compatible_joint_recovery_case() -> JointRecoveryCase:
    return JointRecoveryCase(
        case_id="duplicate_compatible_joint_recovery",
        axes=axes_ab(),
        vectors=vector_surface(),
        participants=(participant_a(), participant_b()),
        coupling=CouplingMode(
            mode_id="joint_recovers_both_duplicate",
            joint_recovered=(fact_a(), fact_b()),
        ),
    )


def individual_failure_case() -> JointRecoveryCase:
    return JointRecoveryCase(
        case_id="individual_failure_not_joint_only",
        axes=axes_ab(),
        vectors=vector_surface(),
        participants=(participant_a(), participant_b_unrecovered()),
        coupling=CouplingMode(
            mode_id="joint_drops_b_with_individual_failure",
            joint_recovered=(fact_a(),),
        ),
    )


def individual_recovery_signature(case: JointRecoveryCase) -> tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...]:
    return tuple(
        sorted(
            (
                participant.participant_id,
                participant.required_ids(),
                participant.recovered_ids(),
            )
            for participant in case.participants
        )
    )


def recovery_profile(case: JointRecoveryCase) -> RecoveryProfile:
    required = tuple(sorted({fact_id for participant in case.participants for fact_id in participant.required_ids()}))
    individually_recovered = tuple(
        sorted({fact_id for participant in case.participants for fact_id in participant.recovered_ids()})
    )
    joint_recovered = case.coupling.recovered_ids()
    missing = tuple(sorted(set(required).difference(joint_recovered)))
    return RecoveryProfile(
        participant_profiles=tuple(participant.as_dict() for participant in case.participants),
        required_fact_ids=required,
        individually_recovered_fact_ids=individually_recovered,
        all_individual_recovery_succeeds=all(
            participant.individually_succeeds() for participant in case.participants
        ),
        joint_recovered_fact_ids=joint_recovered,
        joint_recovery_succeeds=not missing,
        joint_missing_fact_ids=missing,
    )


def joint_recovery_compatible(case: JointRecoveryCase) -> bool:
    return recovery_profile(case).joint_recovery_succeeds


def compare_joint_recovery_cases(left: JointRecoveryCase, right: JointRecoveryCase) -> dict[str, Any]:
    left_individual = left.as_individual_ensemble()
    right_individual = right.as_individual_ensemble()
    left_recovery = recovery_profile(left)
    right_recovery = recovery_profile(right)
    span_comparison = compare_ensembles(left_individual, right_individual)
    return {
        "left": left.case_id,
        "right": right.case_id,
        "marginal_scalar_controls_equal": marginal_summary(left_individual) == marginal_summary(right_individual),
        "full_vector_census_equal": full_vector_census(left_individual) == full_vector_census(right_individual),
        "span_equivalent": span_equivalent(left_individual, right_individual),
        "span_rank_separates": span_comparison["rank_separates"],
        "individual_recovery_profiles_equal": individual_recovery_signature(left)
        == individual_recovery_signature(right),
        "left_span_profile": span_profile(left_individual).as_dict(),
        "right_span_profile": span_profile(right_individual).as_dict(),
        "left_recovery_profile": left_recovery.as_dict(),
        "right_recovery_profile": right_recovery.as_dict(),
        "left_joint_recovery_compatible": left_recovery.joint_recovery_succeeds,
        "right_joint_recovery_compatible": right_recovery.joint_recovery_succeeds,
        "joint_recovery_separates": (
            left_recovery.joint_recovery_succeeds != right_recovery.joint_recovery_succeeds
        ),
    }


def compatible_vs_interfering_witness() -> dict[str, Any]:
    comparison = compare_joint_recovery_cases(
        compatible_joint_recovery_case(),
        interfering_joint_recovery_case(),
    )
    return {
        **comparison,
        "read": (
            "same individual recovery profiles and vector/span surface; "
            "different joint recovery under coupling"
        ),
    }


def identical_joint_recovery_control() -> dict[str, Any]:
    comparison = compare_joint_recovery_cases(
        compatible_joint_recovery_case(),
        duplicate_compatible_joint_recovery_case(),
    )
    return {
        **comparison,
        "same_individual_and_joint_recovery_determine_profile": (
            comparison["individual_recovery_profiles_equal"]
            and not comparison["joint_recovery_separates"]
            and comparison["span_equivalent"]
        ),
        "read": "same individual recovery and same joint recovery cannot be separated by this instrument",
    }


def individual_difference_control() -> dict[str, Any]:
    comparison = compare_joint_recovery_cases(
        interfering_joint_recovery_case(),
        individual_failure_case(),
    )
    return {
        **comparison,
        "not_credited_as_joint_only": not comparison["individual_recovery_profiles_equal"],
        "read": "if individual recovery differs, separation is not credited as joint-only",
    }


def joint_recovery_compatibility_summary() -> dict[str, Any]:
    candidate = compatible_vs_interfering_witness()
    identical_control = identical_joint_recovery_control()
    individual_control = individual_difference_control()
    negative_controls_pass = (
        identical_control["same_individual_and_joint_recovery_determine_profile"]
        and individual_control["not_credited_as_joint_only"]
    )
    separated = (
        candidate["marginal_scalar_controls_equal"]
        and candidate["full_vector_census_equal"]
        and candidate["span_equivalent"]
        and not candidate["span_rank_separates"]
        and candidate["individual_recovery_profiles_equal"]
        and candidate["left_joint_recovery_compatible"]
        and not candidate["right_joint_recovery_compatible"]
        and candidate["joint_recovery_separates"]
        and negative_controls_pass
    )
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "separated" if separated else "reduces-or-ill-posed",
        "candidate_pair": candidate,
        "negative_controls": {
            "identical_joint_recovery": identical_control,
            "individual_difference": individual_control,
            "negative_controls_pass": negative_controls_pass,
        },
        "not_claimed": [
            "value",
            "standing",
            "agency",
            "plurality theory",
            "moral aggregation",
            "patienthood",
            "population optimum",
            "Omega validation",
        ],
    }


def joint_recovery_control_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = summary["candidate_pair"]
    return [
        {
            "metric": "marginal_scalar_controls_equal",
            "left": candidate["left"],
            "right": candidate["right"],
            "holds": candidate["marginal_scalar_controls_equal"],
        },
        {
            "metric": "full_vector_census_equal",
            "left": candidate["left"],
            "right": candidate["right"],
            "holds": candidate["full_vector_census_equal"],
        },
        {
            "metric": "span_equivalent",
            "left": candidate["left"],
            "right": candidate["right"],
            "holds": candidate["span_equivalent"],
        },
        {
            "metric": "individual_recovery_profiles_equal",
            "left": candidate["left"],
            "right": candidate["right"],
            "holds": candidate["individual_recovery_profiles_equal"],
        },
        {
            "metric": "joint_recovery_separates",
            "left": candidate["left"],
            "right": candidate["right"],
            "holds": candidate["joint_recovery_separates"],
        },
    ]


def joint_recovery_profile_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = summary["candidate_pair"]
    return [
        {
            "case_id": candidate["left"],
            **candidate["left_recovery_profile"],
        },
        {
            "case_id": candidate["right"],
            **candidate["right_recovery_profile"],
        },
    ]
