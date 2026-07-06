"""Finite relational-composability instrument.

This module implements the v0 coupling pilot. It checks whether a finite
compatibility relation can separate ensembles after the individual vector
census and marginal scalar summaries are held fixed. It is not a theory of
value, standing, plurality, aggregation, population ethics, agency, or Omega
validation.
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


PROTOCOL_DOC = "docs/research_notes/omega_theory/relational_composability_protocol_v0.md"


@dataclass(frozen=True)
class CoupledEnsemble:
    ensemble_id: str
    axes: tuple[Axis, ...]
    vectors: tuple[ValuerVector, ...]
    compatible_pairs: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        width = len(self.axes)
        ids = {vector.vector_id for vector in self.vectors}
        if len(ids) != len(self.vectors):
            raise ValueError("vector ids must be unique")
        for vector in self.vectors:
            if len(vector.coordinates) != width:
                raise ValueError(
                    f"vector {vector.vector_id!r} has width {len(vector.coordinates)}, expected {width}"
                )
        normalized = tuple(sorted(normalized_pair(left, right) for left, right in self.compatible_pairs))
        if normalized != self.compatible_pairs:
            raise ValueError("compatible pairs must be normalized and sorted")
        for left, right in self.compatible_pairs:
            if left == right:
                raise ValueError("self-compatibility pairs are not represented")
            if left not in ids or right not in ids:
                raise ValueError(f"unknown compatible pair ({left!r}, {right!r})")

    def as_individual_ensemble(self) -> Ensemble:
        return Ensemble(
            ensemble_id=f"{self.ensemble_id}_individual_surface",
            axes=self.axes,
            vectors=self.vectors,
        )


@dataclass(frozen=True)
class CompatibilityProfile:
    compatible_pairs: tuple[tuple[str, str], ...]
    compatible_pair_count: int
    degree_sequence: tuple[int, ...]
    component_sizes: tuple[int, ...]
    max_compatible_component_size: int
    isolated_valuer_count: int
    all_vectors_jointly_compatible: bool
    coupling_matrix: tuple[tuple[int, ...], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "compatible_pairs": [list(pair) for pair in self.compatible_pairs],
            "compatible_pair_count": self.compatible_pair_count,
            "degree_sequence": list(self.degree_sequence),
            "component_sizes": list(self.component_sizes),
            "max_compatible_component_size": self.max_compatible_component_size,
            "isolated_valuer_count": self.isolated_valuer_count,
            "all_vectors_jointly_compatible": self.all_vectors_jointly_compatible,
            "coupling_matrix": [list(row) for row in self.coupling_matrix],
        }


def normalized_pair(left: str, right: str) -> tuple[str, str]:
    if left <= right:
        return (left, right)
    return (right, left)


def normalized_pairs(pairs: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(normalized_pair(left, right) for left, right in pairs))


def compatible_pair_ensemble() -> CoupledEnsemble:
    axes = axes_ab()
    return CoupledEnsemble(
        ensemble_id="compatible_pair_AB",
        axes=axes,
        vectors=(
            ValuerVector("vA", (1, 0)),
            ValuerVector("vB", (0, 1)),
        ),
        compatible_pairs=(("vA", "vB"),),
    )


def blocked_pair_ensemble() -> CoupledEnsemble:
    axes = axes_ab()
    return CoupledEnsemble(
        ensemble_id="blocked_pair_AB",
        axes=axes,
        vectors=(
            ValuerVector("vA", (1, 0)),
            ValuerVector("vB", (0, 1)),
        ),
        compatible_pairs=(),
    )


def duplicate_compatible_pair_ensemble() -> CoupledEnsemble:
    axes = axes_ab()
    return CoupledEnsemble(
        ensemble_id="duplicate_compatible_pair_AB",
        axes=axes,
        vectors=(
            ValuerVector("vA", (1, 0)),
            ValuerVector("vB", (0, 1)),
        ),
        compatible_pairs=(("vA", "vB"),),
    )


def six_vector_surface() -> tuple[ValuerVector, ...]:
    return (
        ValuerVector("v0", (1, 0)),
        ValuerVector("v1", (0, 1)),
        ValuerVector("v2", (1, 1)),
        ValuerVector("v3", (1, 0)),
        ValuerVector("v4", (0, 1)),
        ValuerVector("v5", (1, 1)),
    )


def two_triangles_ensemble() -> CoupledEnsemble:
    axes = axes_ab()
    return CoupledEnsemble(
        ensemble_id="two_triangles_same_degree",
        axes=axes,
        vectors=six_vector_surface(),
        compatible_pairs=normalized_pairs(
            (
                ("v0", "v1"),
                ("v0", "v2"),
                ("v1", "v2"),
                ("v3", "v4"),
                ("v3", "v5"),
                ("v4", "v5"),
            )
        ),
    )


def six_cycle_ensemble() -> CoupledEnsemble:
    axes = axes_ab()
    return CoupledEnsemble(
        ensemble_id="six_cycle_same_degree",
        axes=axes,
        vectors=six_vector_surface(),
        compatible_pairs=normalized_pairs(
            (
                ("v0", "v1"),
                ("v1", "v2"),
                ("v2", "v3"),
                ("v3", "v4"),
                ("v4", "v5"),
                ("v5", "v0"),
            )
        ),
    )


def compatibility_profile(ensemble: CoupledEnsemble) -> CompatibilityProfile:
    ids = tuple(vector.vector_id for vector in ensemble.vectors)
    adjacency = {vector_id: set() for vector_id in ids}
    for left, right in ensemble.compatible_pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)

    seen: set[str] = set()
    sizes: list[int] = []
    for vector_id in ids:
        if vector_id in seen:
            continue
        stack = [vector_id]
        seen.add(vector_id)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        sizes.append(size)

    pair_set = set(ensemble.compatible_pairs)
    matrix = tuple(
        tuple(1 if row == col or normalized_pair(row, col) in pair_set else 0 for col in ids)
        for row in ids
    )
    required_pair_count = len(ids) * (len(ids) - 1) // 2
    component_sizes = tuple(sorted(sizes, reverse=True))
    isolated = sum(1 for size in component_sizes if size == 1)
    degree_sequence = tuple(sorted((len(adjacency[vector_id]) for vector_id in ids), reverse=True))
    return CompatibilityProfile(
        compatible_pairs=ensemble.compatible_pairs,
        compatible_pair_count=len(ensemble.compatible_pairs),
        degree_sequence=degree_sequence,
        component_sizes=component_sizes,
        max_compatible_component_size=max(component_sizes, default=0),
        isolated_valuer_count=isolated,
        all_vectors_jointly_compatible=len(ensemble.compatible_pairs) == required_pair_count,
        coupling_matrix=matrix,
    )


def compatibility_profiles_equal(left: CoupledEnsemble, right: CoupledEnsemble) -> bool:
    return compatibility_profile(left) == compatibility_profile(right)


def compare_coupled_ensembles(left: CoupledEnsemble, right: CoupledEnsemble) -> dict[str, Any]:
    left_individual = left.as_individual_ensemble()
    right_individual = right.as_individual_ensemble()
    left_compatibility = compatibility_profile(left)
    right_compatibility = compatibility_profile(right)
    span_comparison = compare_ensembles(left_individual, right_individual)
    return {
        "left": left.ensemble_id,
        "right": right.ensemble_id,
        "marginal_scalar_controls_equal": marginal_summary(left_individual) == marginal_summary(right_individual),
        "full_vector_census_equal": full_vector_census(left_individual) == full_vector_census(right_individual),
        "span_equivalent": span_equivalent(left_individual, right_individual),
        "left_span_profile": span_profile(left_individual).as_dict(),
        "right_span_profile": span_profile(right_individual).as_dict(),
        "left_compatibility_profile": left_compatibility.as_dict(),
        "right_compatibility_profile": right_compatibility.as_dict(),
        "compatibility_profiles_equal": left_compatibility == right_compatibility,
        "compatibility_separates": left_compatibility != right_compatibility,
        "span_rank_separates": span_comparison["rank_separates"],
    }


def compatible_vs_blocked_witness() -> dict[str, Any]:
    comparison = compare_coupled_ensembles(compatible_pair_ensemble(), blocked_pair_ensemble())
    return {
        **comparison,
        "read": (
            "same individual vector census and pure span; different declared compatibility relation"
        ),
    }


def identical_coupling_control() -> dict[str, Any]:
    comparison = compare_coupled_ensembles(compatible_pair_ensemble(), duplicate_compatible_pair_ensemble())
    return {
        **comparison,
        "full_vectors_and_coupling_determine_profile": (
            comparison["full_vector_census_equal"]
            and comparison["compatibility_profiles_equal"]
            and comparison["span_equivalent"]
        ),
        "read": "same full vector census and same coupling cannot be separated by this instrument",
    }


def graph_structure_robustness_witness() -> dict[str, Any]:
    comparison = compare_coupled_ensembles(two_triangles_ensemble(), six_cycle_ensemble())
    left_profile = comparison["left_compatibility_profile"]
    right_profile = comparison["right_compatibility_profile"]
    return {
        **comparison,
        "same_compatible_pair_count": (
            left_profile["compatible_pair_count"] == right_profile["compatible_pair_count"]
        ),
        "same_degree_sequence": left_profile["degree_sequence"] == right_profile["degree_sequence"],
        "component_structure_separates": left_profile["component_sizes"] != right_profile["component_sizes"],
        "read": (
            "same full vector census, pure span, edge count, and degree sequence; "
            "different compatibility component structure"
        ),
    }


def relational_composability_summary() -> dict[str, Any]:
    candidate = compatible_vs_blocked_witness()
    robustness = graph_structure_robustness_witness()
    control = identical_coupling_control()
    negative_controls_pass = control["full_vectors_and_coupling_determine_profile"]
    separated = (
        candidate["marginal_scalar_controls_equal"]
        and candidate["full_vector_census_equal"]
        and candidate["span_equivalent"]
        and not candidate["span_rank_separates"]
        and candidate["compatibility_separates"]
        and robustness["marginal_scalar_controls_equal"]
        and robustness["full_vector_census_equal"]
        and robustness["span_equivalent"]
        and not robustness["span_rank_separates"]
        and robustness["same_compatible_pair_count"]
        and robustness["same_degree_sequence"]
        and robustness["component_structure_separates"]
        and negative_controls_pass
    )
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "separated" if separated else "reduces-or-ill-posed",
        "candidate_pair": candidate,
        "graph_structure_robustness": robustness,
        "negative_controls": {
            "identical_coupling": control,
            "negative_controls_pass": negative_controls_pass,
        },
        "not_claimed": [
            "value",
            "standing",
            "agency",
            "plurality theory",
            "population ethics",
            "aggregation",
            "population optimum",
            "Omega validation",
        ],
    }


def relational_control_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
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
            "metric": "compatibility_separates",
            "left": candidate["left"],
            "right": candidate["right"],
            "holds": candidate["compatibility_separates"],
        },
    ]


def compatibility_profile_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = summary["candidate_pair"]
    robustness = summary["graph_structure_robustness"]
    return [
        {
            "ensemble_id": candidate["left"],
            **candidate["left_compatibility_profile"],
        },
        {
            "ensemble_id": candidate["right"],
            **candidate["right_compatibility_profile"],
        },
        {
            "ensemble_id": robustness["left"],
            **robustness["left_compatibility_profile"],
        },
        {
            "ensemble_id": robustness["right"],
            **robustness["right_compatibility_profile"],
        },
    ]
