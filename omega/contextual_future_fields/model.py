"""Small finite structures for contextual future-field pilots."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterable, Mapping

Value = int
Assignment = dict[str, Value]
RestrictedAssignment = tuple[tuple[str, Value], ...]


@dataclass(frozen=True)
class Context:
    """A finite local context with allowed local assignments."""

    name: str
    variables: tuple[str, ...]
    allowed: tuple[tuple[Value, ...], ...]
    weights: Mapping[tuple[Value, ...], Fraction] | None = None

    def assignments(self) -> tuple[Assignment, ...]:
        return tuple(
            dict(zip(self.variables, values, strict=True)) for values in self.allowed
        )

    def restrict_support(self, variables: Iterable[str]) -> frozenset[RestrictedAssignment]:
        overlap = tuple(variables)
        return frozenset(restrict_assignment(assignment, overlap) for assignment in self.assignments())

    def restrict_distribution(
        self, variables: Iterable[str]
    ) -> dict[RestrictedAssignment, Fraction]:
        overlap = tuple(variables)
        weights = self.weights or uniform_weights(self.allowed)
        distribution: dict[RestrictedAssignment, Fraction] = {}
        for values, mass in weights.items():
            assignment = dict(zip(self.variables, values, strict=True))
            key = restrict_assignment(assignment, overlap)
            distribution[key] = distribution.get(key, Fraction(0)) + mass
        return distribution


@dataclass(frozen=True)
class Transport:
    """A partial linear coordinate transport for finite profiles."""

    name: str
    source: str
    target: str
    coordinate_map: Mapping[str, str | None]

    def apply(self, profile: Mapping[str, Fraction]) -> dict[str, Fraction]:
        transported: dict[str, Fraction] = {}
        for coordinate, weight in profile.items():
            target_coordinate = self.coordinate_map.get(coordinate)
            if target_coordinate is None:
                continue
            transported[target_coordinate] = transported.get(target_coordinate, Fraction(0)) + weight
        return transported


def restrict_assignment(
    assignment: Mapping[str, Value],
    variables: Iterable[str],
) -> RestrictedAssignment:
    return tuple((variable, assignment[variable]) for variable in variables)


def overlap(left: Context, right: Context) -> tuple[str, ...]:
    right_variables = set(right.variables)
    return tuple(variable for variable in left.variables if variable in right_variables)


def overlap_supports_agree(left: Context, right: Context) -> bool:
    shared = overlap(left, right)
    return left.restrict_support(shared) == right.restrict_support(shared)


def overlap_distributions_agree(left: Context, right: Context) -> bool:
    shared = overlap(left, right)
    return left.restrict_distribution(shared) == right.restrict_distribution(shared)


def all_global_assignments(
    contexts: tuple[Context, ...],
    *,
    variables: tuple[str, ...],
    values: tuple[Value, ...],
) -> list[Assignment]:
    valid: list[Assignment] = []
    for candidate_values in product(values, repeat=len(variables)):
        assignment = dict(zip(variables, candidate_values, strict=True))
        if all(context_accepts(context, assignment) for context in contexts):
            valid.append(assignment)
    return valid


def context_accepts(context: Context, global_assignment: Mapping[str, Value]) -> bool:
    projected = tuple(global_assignment[variable] for variable in context.variables)
    return projected in context.allowed


def uniform_weights(allowed: tuple[tuple[Value, ...], ...]) -> dict[tuple[Value, ...], Fraction]:
    if not allowed:
        return {}
    mass = Fraction(1, len(allowed))
    return {values: mass for values in allowed}


def apply_transport_loop(
    profile: Mapping[str, Fraction],
    transports: tuple[Transport, ...],
) -> dict[str, Fraction]:
    current = dict(profile)
    for transport in transports:
        current = transport.apply(current)
    return current


def project_profile(
    profile: Mapping[str, Fraction],
    coordinates: Iterable[str],
) -> dict[str, str]:
    selected = tuple(coordinates)
    return {coordinate: str(profile.get(coordinate, Fraction(0))) for coordinate in selected}


def fraction_dict(profile: Mapping[str, Fraction]) -> dict[str, str]:
    return {key: str(value) for key, value in sorted(profile.items())}


def support_to_json(support: Iterable[RestrictedAssignment]) -> list[dict[str, Value]]:
    return [dict(item) for item in sorted(support)]


def distribution_to_json(
    distribution: Mapping[RestrictedAssignment, Fraction],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, mass in sorted(distribution.items()):
        rows.append({"assignment": dict(key), "mass": str(mass)})
    return rows
