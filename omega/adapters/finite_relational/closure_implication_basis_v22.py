"""Closure v2.2 guarded implication-basis extraction.

This module consumes Closure v2.1.5 guard attribution. It does not add new
facts or run a larger graph sweep. It records, for each retained surplus fact,
the minimal seed antecedent and minimal guard antecedent currently verified in
the generated finite presentation universe.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations

from omega.adapters.finite_relational.closure_attribution_v21 import (
    ClosureAttribution,
    ClosureAttributionCase,
    ClosureAttributionFamily,
    closure_v2_facts_entail,
    generate_closure_attribution_v21,
)


@dataclass(frozen=True)
class ClosureImplication:
    """One guard-accounted implication row for a surplus fact."""

    consequent_fact: str
    seed_antecedent_facts: tuple[str, ...]
    guard_antecedent_facts: tuple[str, ...]
    bucket: str
    theorem_id: str | None
    proof_status: str
    basis_kind: str

    def summary(self) -> dict[str, object]:
        return {
            "consequent_fact": self.consequent_fact,
            "seed_antecedent_facts": list(self.seed_antecedent_facts),
            "guard_antecedent_facts": list(self.guard_antecedent_facts),
            "bucket": self.bucket,
            "theorem_id": self.theorem_id,
            "proof_status": self.proof_status,
            "basis_kind": self.basis_kind,
        }


@dataclass(frozen=True)
class ClosureImplicationCase:
    """One attributed Closure v2 case with minimal implication rows."""

    attribution_case: ClosureAttributionCase
    implications: tuple[ClosureImplication, ...]

    @property
    def classifier_only(self) -> tuple[ClosureImplication, ...]:
        return tuple(
            implication
            for implication in self.implications
            if implication.proof_status == "classifier_only"
        )

    @property
    def residual(self) -> tuple[ClosureImplication, ...]:
        return tuple(
            implication
            for implication in self.implications
            if implication.basis_kind == "residual"
        )

    def summary(self) -> dict[str, object]:
        return {
            "case_id": self.attribution_case.case.case_id,
            "state_count": len(self.attribution_case.case.states),
            "edge_count": len(self.attribution_case.case.edges),
            "seed_fact_keys": list(self.attribution_case.case.seed_fact_keys),
            "implication_count": len(self.implications),
            "classifier_only_count": len(self.classifier_only),
            "residual_count": len(self.residual),
            "basis_kind_counts": _count(
                implication.basis_kind for implication in self.implications
            ),
            "theorem_counts": _count(
                implication.theorem_id
                for implication in self.implications
                if implication.theorem_id is not None
            ),
            "seed_antecedent_size_counts": _count(
                str(len(implication.seed_antecedent_facts))
                for implication in self.implications
            ),
            "guard_antecedent_size_counts": _count(
                str(len(implication.guard_antecedent_facts))
                for implication in self.implications
            ),
            "implications": [implication.summary() for implication in self.implications],
        }


@dataclass(frozen=True)
class ClosureImplicationFamily:
    """Guarded implication basis for one Closure v2.1 family."""

    family_id: str
    description: str
    search_space: dict[str, object]
    cases: tuple[ClosureImplicationCase, ...]

    @property
    def representative_cases(self) -> tuple[ClosureImplicationCase, ...]:
        representatives: list[ClosureImplicationCase] = []
        residual_cases = [case for case in self.cases if case.residual]
        if residual_cases:
            representatives.append(residual_cases[0])
        process_cases = [
            case
            for case in self.cases
            if any(
                implication.basis_kind == "process_coherence_profile_guard"
                for implication in case.implications
            )
        ]
        if process_cases and process_cases[0] not in representatives:
            representatives.append(process_cases[0])
        global_cases = [
            case
            for case in self.cases
            if any(
                implication.basis_kind == "globally_valid"
                for implication in case.implications
            )
        ]
        if global_cases and global_cases[0] not in representatives:
            representatives.append(global_cases[0])
        return tuple(representatives)

    def summary(self) -> dict[str, object]:
        aggregate = _aggregate_implication_cases(self.cases)
        return {
            "family_id": self.family_id,
            "description": self.description,
            "search_space": self.search_space,
            "case_count": len(self.cases),
            "representative_case_count": len(self.representative_cases),
            "representative_cases": [
                case.summary() for case in self.representative_cases
            ],
            "aggregate": aggregate,
        }


def generate_closure_implication_basis_v22() -> tuple[ClosureImplicationFamily, ...]:
    """Generate a guard-accounted implication basis over v2.1 families."""

    return tuple(
        _implication_family_from_attribution_family(family)
        for family in generate_closure_attribution_v21()
    )


def closure_implication_basis_v22_summary() -> dict[str, object]:
    families = generate_closure_implication_basis_v22()
    all_cases = tuple(case for family in families for case in family.cases)
    aggregate = _aggregate_implication_cases(all_cases)
    return {
        "family_count": len(families),
        "case_count": len(all_cases),
        "aggregate": aggregate,
        "families": [family.summary() for family in families],
    }


def _implication_family_from_attribution_family(
    family: ClosureAttributionFamily,
) -> ClosureImplicationFamily:
    cases = tuple(
        _implication_case_from_attribution_case(case) for case in family.cases
    )
    return ClosureImplicationFamily(
        family_id=family.family_id,
        description=(
            f"Guard-accounted implication basis for {family.family_id}; "
            "no new fact language or graph sweep is introduced."
        ),
        search_space=family.search_space
        | {
            "source_family": family.family_id,
            "guard_accounted": True,
            "version": "v2.2",
        },
        cases=cases,
    )


def _implication_case_from_attribution_case(
    case: ClosureAttributionCase,
) -> ClosureImplicationCase:
    implications = tuple(
        _implication_from_attribution(case, attribution)
        for attribution in case.attributions
    )
    return ClosureImplicationCase(attribution_case=case, implications=implications)


def _implication_from_attribution(
    case: ClosureAttributionCase,
    attribution: ClosureAttribution,
) -> ClosureImplication:
    seed_antecedent = _minimal_entailing_subset(
        case,
        case.case.seed_fact_keys,
        attribution.fact_key,
    )
    guard_antecedent = _minimal_entailing_subset(
        case,
        attribution.hypothesis_facts,
        attribution.fact_key,
    )
    return ClosureImplication(
        consequent_fact=attribution.fact_key,
        seed_antecedent_facts=seed_antecedent,
        guard_antecedent_facts=guard_antecedent,
        bucket=attribution.bucket,
        theorem_id=attribution.theorem_id,
        proof_status=attribution.proof_status,
        basis_kind=_basis_kind(attribution),
    )


def _minimal_entailing_subset(
    case: ClosureAttributionCase,
    candidates: tuple[str, ...],
    consequent_fact: str,
) -> tuple[str, ...]:
    ordered_candidates = tuple(dict.fromkeys(candidates))
    for size in range(len(ordered_candidates) + 1):
        for subset in combinations(ordered_candidates, size):
            antecedent = tuple(sorted(subset))
            if closure_v2_facts_entail(case.case, antecedent, consequent_fact):
                return antecedent
    return tuple(sorted(ordered_candidates))


def _basis_kind(attribution: ClosureAttribution) -> str:
    if attribution.bucket == "residual":
        return "residual"
    if attribution.proof_status == "classifier_only":
        return "classifier_only"
    if attribution.bucket == "globally_valid":
        return "globally_valid"
    if attribution.bucket in {"seed_profile_separation", "profile_fiber_separation"}:
        return "profile_fiber_visibility_guard"
    if attribution.bucket == "seed_determined_profile":
        return "seed_profile_functionality_guard"
    if attribution.bucket == "step_implies_path_lifting":
        return "step_to_path_guard"
    if attribution.bucket == "bounded_process_coherence_invariance":
        return "process_coherence_profile_guard"
    if attribution.bucket in {"seed_forced_structural", "process_coherence_separation"}:
        return "process_coherence_structural_guard"
    return "guard_accounted_other"


def _aggregate_implication_cases(
    cases: tuple[ClosureImplicationCase, ...],
) -> dict[str, object]:
    implications = tuple(
        implication for case in cases for implication in case.implications
    )
    theorem_counts = _count(
        implication.theorem_id
        for implication in implications
        if implication.theorem_id is not None
    )
    proof_status_counts = _count(
        implication.proof_status for implication in implications
    )
    return {
        "case_count": len(cases),
        "implication_count": len(implications),
        "guard_accounted_implication_count": sum(
            count
            for status, count in proof_status_counts.items()
            if status == "guard_verified"
        ),
        "classifier_only_implication_count": proof_status_counts.get(
            "classifier_only", 0
        ),
        "residual_implication_count": sum(
            1 for implication in implications if implication.basis_kind == "residual"
        ),
        "basis_kind_counts": _count(
            implication.basis_kind for implication in implications
        ),
        "bucket_counts": _count(implication.bucket for implication in implications),
        "theorem_counts": theorem_counts,
        "proof_status_counts": proof_status_counts,
        "seed_antecedent_size_counts": _count(
            str(len(implication.seed_antecedent_facts))
            for implication in implications
        ),
        "guard_antecedent_size_counts": _count(
            str(len(implication.guard_antecedent_facts))
            for implication in implications
        ),
        "unique_seed_implication_count": len(
            {
                (implication.seed_antecedent_facts, implication.consequent_fact)
                for implication in implications
            }
        ),
        "unique_guard_implication_count": len(
            {
                (
                    implication.guard_antecedent_facts,
                    implication.consequent_fact,
                    implication.theorem_id,
                )
                for implication in implications
            }
        ),
    }


def _count(values: object) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))
