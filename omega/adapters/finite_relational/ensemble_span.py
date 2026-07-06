"""Finite ensemble-span instrument.

This module implements the v0 joint-tier span pilot. It checks whether
ensemble orientation can separate finite ensembles after marginal scalar
summaries are matched. It is not a theory of value, standing, population
ethics, aggregation, relational surplus, or Omega validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any


PROTOCOL_DOC = "docs/research_notes/omega_theory/ensemble_span_protocol_v0.md"


@dataclass(frozen=True)
class Axis:
    name: str


@dataclass(frozen=True)
class ValuerVector:
    vector_id: str
    coordinates: tuple[int, ...]

    def l1_norm(self) -> int:
        return sum(abs(value) for value in self.coordinates)


@dataclass(frozen=True)
class Ensemble:
    ensemble_id: str
    axes: tuple[Axis, ...]
    vectors: tuple[ValuerVector, ...]

    def __post_init__(self) -> None:
        width = len(self.axes)
        for vector in self.vectors:
            if len(vector.coordinates) != width:
                raise ValueError(
                    f"vector {vector.vector_id!r} has width {len(vector.coordinates)}, expected {width}"
                )


@dataclass(frozen=True)
class MarginalSummary:
    valuer_count: int
    vector_dimension: int
    per_valuer_l1_norms: tuple[int, ...]
    total_l1_amount: int
    max_individual_l1_norm: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "valuer_count": self.valuer_count,
            "vector_dimension": self.vector_dimension,
            "per_valuer_l1_norms": list(self.per_valuer_l1_norms),
            "total_l1_amount": self.total_l1_amount,
            "max_individual_l1_norm": self.max_individual_l1_norm,
        }


@dataclass(frozen=True)
class SpanProfile:
    rank: int
    gram_matrix: tuple[tuple[int, ...], ...]
    gram_determinant: int
    axis_supports: dict[str, int]
    full_vector_census: tuple[tuple[int, ...], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "gram_matrix": [list(row) for row in self.gram_matrix],
            "gram_determinant": self.gram_determinant,
            "logdet_proxy": logdet_proxy(self.gram_determinant),
            "axis_supports": self.axis_supports,
            "full_vector_census": [list(row) for row in self.full_vector_census],
        }


def axes_ab() -> tuple[Axis, Axis]:
    return (Axis("A"), Axis("B"))


def axes_abc() -> tuple[Axis, Axis, Axis]:
    return (Axis("A"), Axis("B"), Axis("C"))


def redundant_ensemble() -> Ensemble:
    axes = axes_ab()
    return Ensemble(
        ensemble_id="redundant_AA",
        axes=axes,
        vectors=(
            ValuerVector("r1", (1, 0)),
            ValuerVector("r2", (1, 0)),
        ),
    )


def orthogonal_ensemble() -> Ensemble:
    axes = axes_ab()
    return Ensemble(
        ensemble_id="orthogonal_AB",
        axes=axes,
        vectors=(
            ValuerVector("o1", (1, 0)),
            ValuerVector("o2", (0, 1)),
        ),
    )


def base_ensemble() -> Ensemble:
    axes = axes_ab()
    return Ensemble(
        ensemble_id="base_A",
        axes=axes,
        vectors=(ValuerVector("b1", (1, 0)),),
    )


def correlated_addition_ensemble() -> Ensemble:
    axes = axes_ab()
    return Ensemble(
        ensemble_id="correlated_A_plus_A",
        axes=axes,
        vectors=(
            ValuerVector("c1", (1, 0)),
            ValuerVector("c2", (1, 0)),
        ),
    )


def orthogonal_addition_ensemble() -> Ensemble:
    axes = axes_ab()
    return Ensemble(
        ensemble_id="orthogonal_A_plus_B",
        axes=axes,
        vectors=(
            ValuerVector("d1", (1, 0)),
            ValuerVector("d2", (0, 1)),
        ),
    )


def coplanar_rank2_ensemble() -> Ensemble:
    axes = axes_abc()
    return Ensemble(
        ensemble_id="coplanar_rank2_AB_AplusB",
        axes=axes,
        vectors=(
            ValuerVector("p1", (1, 0, 0)),
            ValuerVector("p2", (0, 1, 0)),
            ValuerVector("p3", (1, 1, 0)),
        ),
    )


def full_rank3_ensemble() -> Ensemble:
    axes = axes_abc()
    return Ensemble(
        ensemble_id="full_rank3_AB_2C",
        axes=axes,
        vectors=(
            ValuerVector("f1", (1, 0, 0)),
            ValuerVector("f2", (0, 1, 0)),
            ValuerVector("f3", (0, 0, 2)),
        ),
    )


def marginal_summary(ensemble: Ensemble) -> MarginalSummary:
    norms = tuple(sorted(vector.l1_norm() for vector in ensemble.vectors))
    return MarginalSummary(
        valuer_count=len(ensemble.vectors),
        vector_dimension=len(ensemble.axes),
        per_valuer_l1_norms=norms,
        total_l1_amount=sum(norms),
        max_individual_l1_norm=max(norms, default=0),
    )


def marginal_controls_match(left: Ensemble, right: Ensemble) -> bool:
    return marginal_summary(left) == marginal_summary(right)


def vector_rows(ensemble: Ensemble) -> tuple[tuple[int, ...], ...]:
    return tuple(vector.coordinates for vector in ensemble.vectors)


def full_vector_census(ensemble: Ensemble) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted(vector_rows(ensemble)))


def gram_matrix(ensemble: Ensemble) -> tuple[tuple[int, ...], ...]:
    rows = vector_rows(ensemble)
    return tuple(
        tuple(dot(left, right) for right in rows)
        for left in rows
    )


def dot(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return sum(a * b for a, b in zip(left, right))


def axis_supports(ensemble: Ensemble) -> dict[str, int]:
    supports: dict[str, int] = {}
    for idx, axis in enumerate(ensemble.axes):
        supports[axis.name] = sum(1 for vector in ensemble.vectors if vector.coordinates[idx] != 0)
    return supports


def span_profile(ensemble: Ensemble) -> SpanProfile:
    gram = gram_matrix(ensemble)
    return SpanProfile(
        rank=span_rank(ensemble),
        gram_matrix=gram,
        gram_determinant=determinant(gram),
        axis_supports=axis_supports(ensemble),
        full_vector_census=full_vector_census(ensemble),
    )


def span_rank(ensemble: Ensemble) -> int:
    return matrix_rank(vector_rows(ensemble))


def span_includes(left: Ensemble, right: Ensemble) -> bool:
    """Return true when span(left) includes span(right)."""
    combined_rows = vector_rows(left) + vector_rows(right)
    return matrix_rank(vector_rows(left)) == matrix_rank(combined_rows)


def span_equivalent(left: Ensemble, right: Ensemble) -> bool:
    return span_includes(left, right) and span_includes(right, left)


def rank_gain(base: Ensemble, expanded: Ensemble) -> int:
    return span_rank(expanded) - span_rank(base)


def matrix_rank(rows: tuple[tuple[int, ...], ...]) -> int:
    if not rows:
        return 0
    matrix = [[Fraction(value) for value in row] for row in rows]
    row_count = len(matrix)
    col_count = len(matrix[0])
    rank = 0
    pivot_row = 0
    for col in range(col_count):
        pivot = None
        for row in range(pivot_row, row_count):
            if matrix[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        pivot_value = matrix[pivot_row][col]
        matrix[pivot_row] = [value / pivot_value for value in matrix[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or matrix[row][col] == 0:
                continue
            factor = matrix[row][col]
            matrix[row] = [
                value - factor * pivot_component
                for value, pivot_component in zip(matrix[row], matrix[pivot_row])
            ]
        rank += 1
        pivot_row += 1
        if pivot_row == row_count:
            break
    return rank


def determinant(matrix: tuple[tuple[int, ...], ...]) -> int:
    if not matrix:
        return 1
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    work = [[Fraction(value) for value in row] for row in matrix]
    sign = 1
    det = Fraction(1)
    for col in range(size):
        pivot = None
        for row in range(col, size):
            if work[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign *= -1
        pivot_value = work[col][col]
        det *= pivot_value
        for row in range(col + 1, size):
            factor = work[row][col] / pivot_value
            for inner_col in range(col, size):
                work[row][inner_col] -= factor * work[col][inner_col]
    result = det * sign
    if result.denominator != 1:
        raise ValueError("integer matrix determinant unexpectedly non-integral")
    return result.numerator


def logdet_proxy(det: int) -> str:
    if det <= 0:
        return "singular"
    return f"{math.log(det):.6f}"


def compare_ensembles(left: Ensemble, right: Ensemble) -> dict[str, Any]:
    left_summary = marginal_summary(left)
    right_summary = marginal_summary(right)
    left_profile = span_profile(left)
    right_profile = span_profile(right)
    return {
        "left": left.ensemble_id,
        "right": right.ensemble_id,
        "marginal_scalar_controls_equal": left_summary == right_summary,
        "left_marginal_summary": left_summary.as_dict(),
        "right_marginal_summary": right_summary.as_dict(),
        "left_span_profile": left_profile.as_dict(),
        "right_span_profile": right_profile.as_dict(),
        "left_span_includes_right": span_includes(left, right),
        "right_span_includes_left": span_includes(right, left),
        "span_equivalent": span_equivalent(left, right),
        "rank_separates": left_profile.rank != right_profile.rank,
        "full_vector_census_equal": left_profile.full_vector_census == right_profile.full_vector_census,
    }


def redundant_vs_orthogonal_witness() -> dict[str, Any]:
    redundant = redundant_ensemble()
    orthogonal = orthogonal_ensemble()
    comparison = compare_ensembles(redundant, orthogonal)
    return {
        **comparison,
        "read": (
            "same marginal scalar census; different ensemble orientation and span rank"
        ),
    }


def larger_rank_robustness_witness() -> dict[str, Any]:
    coplanar = coplanar_rank2_ensemble()
    full_rank = full_rank3_ensemble()
    comparison = compare_ensembles(coplanar, full_rank)
    return {
        **comparison,
        "read": (
            "three-axis robustness case: same marginal scalar census; "
            "rank-2 coplanar ensemble differs from rank-3 ensemble"
        ),
    }


def diminishing_returns_witness() -> dict[str, Any]:
    base = base_ensemble()
    correlated = correlated_addition_ensemble()
    orthogonal = orthogonal_addition_ensemble()
    return {
        "base": base.ensemble_id,
        "correlated_addition": correlated.ensemble_id,
        "orthogonal_addition": orthogonal.ensemble_id,
        "added_vector_l1_norms_equal": (
            correlated.vectors[-1].l1_norm() == orthogonal.vectors[-1].l1_norm()
        ),
        "base_rank": span_rank(base),
        "correlated_rank": span_rank(correlated),
        "orthogonal_rank": span_rank(orthogonal),
        "correlated_rank_gain": rank_gain(base, correlated),
        "orthogonal_rank_gain": rank_gain(base, orthogonal),
        "read": "correlated addition has no rank gain; orthogonal addition has positive rank gain",
    }


def identical_vectors_control() -> dict[str, Any]:
    ensemble = redundant_ensemble()
    profile = span_profile(ensemble)
    return {
        "ensemble": ensemble.ensemble_id,
        "all_vectors_identical": len(set(vector_rows(ensemble))) == 1,
        "rank": profile.rank,
        "rank_reduces_to_singleton_orientation": profile.rank == 1,
        "read": "identical vectors reduce span to one orientation",
    }


def full_vector_census_control() -> dict[str, Any]:
    axes = axes_ab()
    left = Ensemble(
        ensemble_id="full_census_left_AB",
        axes=axes,
        vectors=(
            ValuerVector("l1", (1, 0)),
            ValuerVector("l2", (0, 1)),
        ),
    )
    right = Ensemble(
        ensemble_id="full_census_right_BA",
        axes=axes,
        vectors=(
            ValuerVector("r1", (0, 1)),
            ValuerVector("r2", (1, 0)),
        ),
    )
    comparison = compare_ensembles(left, right)
    return {
        **comparison,
        "full_vector_census_determines_pure_span": (
            comparison["full_vector_census_equal"] and comparison["span_equivalent"]
        ),
        "read": "same full vector census cannot be separated by pure span",
    }


def ensemble_span_summary() -> dict[str, Any]:
    candidate = redundant_vs_orthogonal_witness()
    robustness = larger_rank_robustness_witness()
    diminishing = diminishing_returns_witness()
    identical_control = identical_vectors_control()
    census_control = full_vector_census_control()
    negative_controls_pass = (
        identical_control["rank_reduces_to_singleton_orientation"]
        and census_control["full_vector_census_determines_pure_span"]
    )
    separated = (
        candidate["marginal_scalar_controls_equal"]
        and candidate["rank_separates"]
        and candidate["right_span_includes_left"]
        and not candidate["left_span_includes_right"]
        and not candidate["full_vector_census_equal"]
        and diminishing["correlated_rank_gain"] == 0
        and diminishing["orthogonal_rank_gain"] > 0
        and robustness["marginal_scalar_controls_equal"]
        and robustness["rank_separates"]
        and robustness["right_span_includes_left"]
        and not robustness["left_span_includes_right"]
        and negative_controls_pass
    )
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "separated" if separated else "reduces-or-ill-posed",
        "candidate_pair": candidate,
        "larger_rank_robustness": robustness,
        "diminishing_returns": diminishing,
        "negative_controls": {
            "identical_vectors": identical_control,
            "full_vector_census": census_control,
            "negative_controls_pass": negative_controls_pass,
        },
        "not_claimed": [
            "value",
            "standing",
            "agency",
            "population ethics",
            "aggregation",
            "relational surplus",
            "population optimum",
            "Omega validation",
        ],
    }


def marginal_control_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = summary["candidate_pair"]
    left = candidate["left_marginal_summary"]
    right = candidate["right_marginal_summary"]
    return [
        {
            "metric": key,
            "left": left[key],
            "right": right[key],
            "relation": "equal",
            "holds": left[key] == right[key],
        }
        for key in left
    ]


def span_profile_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = summary["candidate_pair"]
    left = candidate["left_span_profile"]
    right = candidate["right_span_profile"]
    return [
        {
            "ensemble_id": candidate["left"],
            **left,
        },
        {
            "ensemble_id": candidate["right"],
            **right,
        },
    ]
