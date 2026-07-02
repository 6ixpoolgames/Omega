"""Compatibility-thickness kernels for finite continuation profiles."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Mapping


@dataclass(frozen=True)
class ContinuationProfile:
    """A finite profile represented by certified continuation atoms."""

    name: str
    atoms: frozenset[str]


@dataclass(frozen=True)
class OverlapKernel:
    """A PSD-by-construction compatibility-thickness kernel.

    The diagonal is profile thickness. The off-diagonal is shared certified
    overlap. This is a finite Gram kernel over weighted indicator vectors.
    """

    profiles: tuple[ContinuationProfile, ...]
    atom_weights: Mapping[str, Fraction]

    def matrix(self) -> tuple[tuple[Fraction, ...], ...]:
        return tuple(
            tuple(self.overlap(left, right) for right in self.profiles)
            for left in self.profiles
        )

    def overlap(
        self,
        left: ContinuationProfile,
        right: ContinuationProfile,
    ) -> Fraction:
        return sum(
            self.atom_weights[atom]
            for atom in sorted(left.atoms & right.atoms)
        )

    def thickness(self, profile: ContinuationProfile) -> Fraction:
        return self.overlap(profile, profile)


def declared_kernel_report(
    *,
    name: str,
    labels: tuple[str, ...],
    matrix: tuple[tuple[Fraction, ...], ...],
    interpretation: str,
) -> dict[str, object]:
    symmetric = is_symmetric(matrix)
    principal_minors = principal_minor_report(matrix)
    psd = symmetric and all(minor["determinant"] >= Fraction(0) for minor in principal_minors)
    return {
        "name": name,
        "labels": list(labels),
        "matrix": matrix_to_json(matrix),
        "interpretation": interpretation,
        "symmetric": symmetric,
        "nonnegative_diagonal": all(matrix[i][i] >= 0 for i in range(len(matrix))),
        "principal_minors": [
            {
                "indices": list(minor["indices"]),
                "determinant": str(minor["determinant"]),
            }
            for minor in principal_minors
        ],
        "psd": psd,
        "rank": rank(matrix) if symmetric else None,
    }


def overlap_kernel_report(
    *,
    name: str,
    kernel: OverlapKernel,
    interpretation: str,
) -> dict[str, object]:
    matrix = kernel.matrix()
    report = declared_kernel_report(
        name=name,
        labels=tuple(profile.name for profile in kernel.profiles),
        matrix=matrix,
        interpretation=interpretation,
    )
    report["profiles"] = [
        {
            "name": profile.name,
            "atoms": sorted(profile.atoms),
            "thickness": str(kernel.thickness(profile)),
        }
        for profile in kernel.profiles
    ]
    report["atom_weights"] = {
        atom: str(weight) for atom, weight in sorted(kernel.atom_weights.items())
    }
    report["construction"] = "certified_overlap_gram_kernel"
    return report


def kernel_deformation_report(
    *,
    name: str,
    before: OverlapKernel,
    after: OverlapKernel,
    interpretation: str,
) -> dict[str, object]:
    before_matrix = before.matrix()
    after_matrix = after.matrix()
    labels = tuple(profile.name for profile in before.profiles)
    if labels != tuple(profile.name for profile in after.profiles):
        raise ValueError("kernel deformation requires matching profile labels")
    diagonal_changes: list[dict[str, str]] = []
    off_diagonal_changes: list[dict[str, str]] = []
    for i, label in enumerate(labels):
        if before_matrix[i][i] != after_matrix[i][i]:
            diagonal_changes.append(
                {
                    "profile": label,
                    "before": str(before_matrix[i][i]),
                    "after": str(after_matrix[i][i]),
                    "delta": str(after_matrix[i][i] - before_matrix[i][i]),
                }
            )
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            if before_matrix[i][j] != after_matrix[i][j]:
                off_diagonal_changes.append(
                    {
                        "left": labels[i],
                        "right": labels[j],
                        "before": str(before_matrix[i][j]),
                        "after": str(after_matrix[i][j]),
                        "delta": str(after_matrix[i][j] - before_matrix[i][j]),
                    }
                )
    before_report = overlap_kernel_report(
        name=f"{name}_before",
        kernel=before,
        interpretation="before deformation",
    )
    after_report = overlap_kernel_report(
        name=f"{name}_after",
        kernel=after,
        interpretation="after deformation",
    )
    return {
        "name": name,
        "interpretation": interpretation,
        "labels": list(labels),
        "before": before_report,
        "after": after_report,
        "diagonal_preserved": not diagonal_changes,
        "off_diagonal_preserved": not off_diagonal_changes,
        "diagonal_changes": diagonal_changes,
        "off_diagonal_changes": off_diagonal_changes,
        "psd_preserved": bool(before_report["psd"] and after_report["psd"]),
    }


def is_symmetric(matrix: tuple[tuple[Fraction, ...], ...]) -> bool:
    return all(
        matrix[i][j] == matrix[j][i]
        for i in range(len(matrix))
        for j in range(len(matrix))
    )


def principal_minor_report(
    matrix: tuple[tuple[Fraction, ...], ...],
) -> list[dict[str, object]]:
    reports: list[dict[str, object]] = []
    n = len(matrix)
    for size in range(1, n + 1):
        for indices in combinations(range(n), size):
            submatrix = tuple(tuple(matrix[i][j] for j in indices) for i in indices)
            reports.append({"indices": indices, "determinant": determinant(submatrix)})
    return reports


def determinant(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    n = len(matrix)
    if n == 0:
        return Fraction(1)
    rows = [list(row) for row in matrix]
    sign = Fraction(1)
    det = Fraction(1)
    for col in range(n):
        pivot = next((row for row in range(col, n) if rows[row][col] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            sign *= -1
        pivot_value = rows[col][col]
        det *= pivot_value
        for row in range(col + 1, n):
            factor = rows[row][col] / pivot_value
            for k in range(col, n):
                rows[row][k] -= factor * rows[col][k]
    return sign * det


def rank(matrix: tuple[tuple[Fraction, ...], ...]) -> int:
    if not matrix:
        return 0
    rows = [list(row) for row in matrix]
    row_count = len(rows)
    col_count = len(rows[0])
    pivot_row = 0
    for col in range(col_count):
        pivot = next((row for row in range(pivot_row, row_count) if rows[row][col] != 0), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][col]
        rows[pivot_row] = [value / pivot_value for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = rows[row][col]
            if factor == 0:
                continue
            rows[row] = [
                value - factor * pivot_entry
                for value, pivot_entry in zip(rows[row], rows[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def matrix_to_json(matrix: tuple[tuple[Fraction, ...], ...]) -> list[list[str]]:
    return [[str(value) for value in row] for row in matrix]
