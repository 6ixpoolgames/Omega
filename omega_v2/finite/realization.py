"""Finite witness-retaining May and Robust realization structures."""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from typing import Any, Iterable


def _powerset(values: Iterable[str]) -> tuple[tuple[str, ...], ...]:
    retained = tuple(sorted(set(values)))
    return tuple(
        combination
        for size in range(len(retained) + 1)
        for combination in itertools.combinations(retained, size)
    )


@dataclass(frozen=True)
class CandidateRealizationClass:
    """Candidates with the same complete finite realization signature."""

    class_id: str
    members: tuple[str, ...]
    witness_ids: tuple[str, ...]

    def structural_payload(self) -> dict[str, object]:
        return {
            "class_id": self.class_id,
            "witness_ids": list(self.witness_ids),
        }


@dataclass(frozen=True)
class MayRealizationFiber:
    """One candidate family and every witness jointly realizing it."""

    family: tuple[str, ...]
    witness_ids: tuple[str, ...]

    @property
    def nonempty(self) -> bool:
        return bool(self.witness_ids)

    def as_dict(self) -> dict[str, object]:
        return {
            "family": list(self.family),
            "witness_ids": list(self.witness_ids),
            "nonempty": self.nonempty,
        }


@dataclass(frozen=True)
class FiniteRealizationRelation:
    """A finite witness-to-candidate incidence relation."""

    relation_id: str
    candidate_ids: tuple[str, ...]
    witness_ids: tuple[str, ...]
    incidence_rows: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.relation_id:
            raise ValueError("relation_id must be nonempty")
        if not self.candidate_ids or len(self.candidate_ids) != len(
            set(self.candidate_ids)
        ):
            raise ValueError("candidate identifiers must be nonempty and unique")
        if not self.witness_ids or len(self.witness_ids) != len(set(self.witness_ids)):
            raise ValueError("witness identifiers must be nonempty and unique")
        if len(self.incidence_rows) != len(set(self.incidence_rows)):
            raise ValueError("incidence rows must be unique")

        candidate_set = set(self.candidate_ids)
        witness_set = set(self.witness_ids)
        unknown_candidates = {
            candidate for candidate, _witness in self.incidence_rows
        } - candidate_set
        unknown_witnesses = {
            witness for _candidate, witness in self.incidence_rows
        } - witness_set
        if unknown_candidates:
            raise ValueError(
                f"incidence references unknown candidates: {unknown_candidates}"
            )
        if unknown_witnesses:
            raise ValueError(
                f"incidence references unknown witnesses: {unknown_witnesses}"
            )

    def witnesses_for(self, candidate_id: str) -> frozenset[str]:
        if candidate_id not in self.candidate_ids:
            raise KeyError(candidate_id)
        return frozenset(
            witness
            for candidate, witness in self.incidence_rows
            if candidate == candidate_id
        )

    def candidate_classes(self) -> tuple[CandidateRealizationClass, ...]:
        grouped: dict[tuple[str, ...], list[str]] = {}
        for candidate in self.candidate_ids:
            signature = tuple(sorted(self.witnesses_for(candidate)))
            grouped.setdefault(signature, []).append(candidate)

        classes = []
        for witness_ids, members in grouped.items():
            payload = json.dumps(
                {"witness_ids": witness_ids},
                sort_keys=True,
                separators=(",", ":"),
            )
            class_id = (
                "candidate:"
                + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
            )
            classes.append(
                CandidateRealizationClass(
                    class_id=class_id,
                    members=tuple(sorted(members)),
                    witness_ids=witness_ids,
                )
            )
        return tuple(sorted(classes, key=lambda item: item.class_id))

    def may_omega(self) -> FiniteMayOmega:
        return FiniteMayOmega.from_relation(self)


@dataclass(frozen=True)
class FiniteMayOmega:
    """The complete finite May-realization object after exact duplicate quotient."""

    omega_id: str
    candidate_classes: tuple[CandidateRealizationClass, ...]
    witness_ids: tuple[str, ...]
    fibers: tuple[MayRealizationFiber, ...]

    @classmethod
    def from_relation(
        cls,
        relation: FiniteRealizationRelation,
    ) -> FiniteMayOmega:
        candidate_classes = relation.candidate_classes()
        class_ids = tuple(item.class_id for item in candidate_classes)
        signatures = {
            item.class_id: frozenset(item.witness_ids) for item in candidate_classes
        }
        fibers = []
        for family in _powerset(class_ids):
            witnesses = set(relation.witness_ids)
            for candidate_class in family:
                witnesses.intersection_update(signatures[candidate_class])
            fibers.append(
                MayRealizationFiber(
                    family=family,
                    witness_ids=tuple(sorted(witnesses)),
                )
            )
        return cls(
            omega_id=f"may:{relation.relation_id}",
            candidate_classes=candidate_classes,
            witness_ids=relation.witness_ids,
            fibers=tuple(fibers),
        )

    @property
    def class_ids(self) -> tuple[str, ...]:
        return tuple(item.class_id for item in self.candidate_classes)

    def class_for_member(self, candidate_id: str) -> CandidateRealizationClass:
        try:
            return next(
                item
                for item in self.candidate_classes
                if candidate_id in item.members
            )
        except StopIteration as exc:
            raise KeyError(candidate_id) from exc

    def quotient_family(self, candidate_ids: Iterable[str]) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    self.class_for_member(candidate_id).class_id
                    for candidate_id in candidate_ids
                }
            )
        )

    def fiber(self, family: Iterable[str]) -> MayRealizationFiber:
        normalized = tuple(sorted(set(family)))
        if not set(normalized) <= set(self.class_ids):
            raise ValueError("family contains an unknown candidate class")
        try:
            return next(item for item in self.fibers if item.family == normalized)
        except StopIteration as exc:
            raise AssertionError("complete May fiber table is missing a family") from exc

    def compatible_families(self) -> tuple[tuple[str, ...], ...]:
        return tuple(item.family for item in self.fibers if item.nonempty)

    def maximal_faces(self) -> tuple[tuple[str, ...], ...]:
        compatible = tuple(
            frozenset(family)
            for family in self.compatible_families()
            if family
        )
        maximal = tuple(
            family
            for family in compatible
            if not any(family < other for other in compatible)
        )
        return tuple(sorted(tuple(sorted(face)) for face in maximal))

    def greatest_face(self) -> tuple[str, ...] | None:
        maximal = self.maximal_faces()
        return maximal[0] if len(maximal) == 1 else None

    def downward_closure_failures(self) -> tuple[dict[str, object], ...]:
        compatible = set(self.compatible_families())
        failures = []
        for family in compatible:
            for subset in _powerset(family):
                if subset not in compatible:
                    failures.append(
                        {
                            "family": list(family),
                            "missing_subset": list(subset),
                        }
                    )
        return tuple(failures)

    def restriction_failures(self) -> tuple[dict[str, object], ...]:
        failures = []
        families = tuple(frozenset(item.family) for item in self.fibers)
        for small in families:
            small_witnesses = set(self.fiber(small).witness_ids)
            for large in families:
                if not small <= large:
                    continue
                large_witnesses = set(self.fiber(large).witness_ids)
                if not large_witnesses <= small_witnesses:
                    failures.append(
                        {
                            "kind": "antitone",
                            "small": sorted(small),
                            "large": sorted(large),
                        }
                    )
                for largest in families:
                    if not large <= largest:
                        continue
                    largest_witnesses = set(self.fiber(largest).witness_ids)
                    direct = largest_witnesses & small_witnesses
                    via_large = largest_witnesses & large_witnesses & small_witnesses
                    if direct != via_large:
                        failures.append(
                            {
                                "kind": "composition",
                                "small": sorted(small),
                                "large": sorted(large),
                                "largest": sorted(largest),
                            }
                        )
        return tuple(failures)

    def structural_payload(self) -> dict[str, object]:
        return {
            "candidate_classes": [
                item.structural_payload() for item in self.candidate_classes
            ],
            "witness_ids": list(self.witness_ids),
            "fibers": [item.as_dict() for item in self.fibers],
            "maximal_faces": [list(face) for face in self.maximal_faces()],
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "omega_id": self.omega_id,
            "candidate_classes": [
                {
                    **item.structural_payload(),
                    "members": list(item.members),
                }
                for item in self.candidate_classes
            ],
            "witness_ids": list(self.witness_ids),
            "fibers": [item.as_dict() for item in self.fibers],
            "compatible_families": [
                list(family) for family in self.compatible_families()
            ],
            "maximal_faces": [list(face) for face in self.maximal_faces()],
            "greatest_face": (
                list(self.greatest_face()) if self.greatest_face() is not None else None
            ),
            "downward_closure_failures": list(self.downward_closure_failures()),
            "restriction_failures": list(self.restriction_failures()),
        }


@dataclass(frozen=True)
class PolicyEnvironmentRuns:
    """A total deterministic policy/environment-to-witness table."""

    table_id: str
    policy_ids: tuple[str, ...]
    environment_ids: tuple[str, ...]
    witness_ids: tuple[str, ...]
    outcome_rows: tuple[tuple[str, str, str], ...]

    def __post_init__(self) -> None:
        if not self.table_id:
            raise ValueError("table_id must be nonempty")
        if not self.policy_ids or len(self.policy_ids) != len(set(self.policy_ids)):
            raise ValueError("policy identifiers must be nonempty and unique")
        if not self.environment_ids or len(self.environment_ids) != len(
            set(self.environment_ids)
        ):
            raise ValueError("environment identifiers must be nonempty and unique")
        if not self.witness_ids or len(self.witness_ids) != len(set(self.witness_ids)):
            raise ValueError("witness identifiers must be nonempty and unique")

        keys = tuple(
            (policy_id, environment_id)
            for policy_id, environment_id, _witness_id in self.outcome_rows
        )
        required = {
            (policy_id, environment_id)
            for policy_id in self.policy_ids
            for environment_id in self.environment_ids
        }
        if len(keys) != len(set(keys)):
            raise ValueError("policy/environment outcome rows must be functional")
        if set(keys) != required:
            raise ValueError(
                "policy/environment outcome rows must be total on the product"
            )
        unknown_witnesses = {
            witness_id
            for _policy_id, _environment_id, witness_id in self.outcome_rows
            if witness_id not in self.witness_ids
        }
        if unknown_witnesses:
            raise ValueError(
                f"outcome rows reference unknown witnesses: {unknown_witnesses}"
            )

    @property
    def outcome_map(self) -> dict[tuple[str, str], str]:
        return {
            (policy_id, environment_id): witness_id
            for policy_id, environment_id, witness_id in self.outcome_rows
        }

    def witness_for(self, policy_id: str, environment_id: str) -> str:
        try:
            return self.outcome_map[(policy_id, environment_id)]
        except KeyError as exc:
            raise KeyError((policy_id, environment_id)) from exc

    def normalize_scope(
        self,
        environment_ids: Iterable[str] | None = None,
    ) -> tuple[str, ...]:
        selected = (
            self.environment_ids
            if environment_ids is None
            else tuple(sorted(set(environment_ids)))
        )
        if not selected:
            raise ValueError("a Robust environment scope must be nonempty")
        if not set(selected) <= set(self.environment_ids):
            raise ValueError("environment scope contains an unknown environment")
        return selected


@dataclass(frozen=True)
class SecuringPolicyWitness:
    """One policy and all environment-indexed runs securing a family."""

    policy_id: str
    environment_runs: tuple[tuple[str, str], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "policy_id": self.policy_id,
            "environment_runs": [
                {
                    "environment_id": environment_id,
                    "witness_id": witness_id,
                }
                for environment_id, witness_id in self.environment_runs
            ],
        }


@dataclass(frozen=True)
class RobustRealizationFiber:
    """One candidate family and every policy securing it over a scope."""

    family: tuple[str, ...]
    environment_ids: tuple[str, ...]
    securing_witnesses: tuple[SecuringPolicyWitness, ...]

    @property
    def nonempty(self) -> bool:
        return bool(self.securing_witnesses)

    @property
    def policy_ids(self) -> tuple[str, ...]:
        return tuple(item.policy_id for item in self.securing_witnesses)

    def as_dict(self) -> dict[str, object]:
        return {
            "family": list(self.family),
            "environment_ids": list(self.environment_ids),
            "securing_witnesses": [
                item.as_dict() for item in self.securing_witnesses
            ],
            "policy_ids": list(self.policy_ids),
            "nonempty": self.nonempty,
        }


@dataclass(frozen=True)
class FiniteOmega:
    """Complete May and scope-indexed Robust fibers over one candidate quotient."""

    omega_id: str
    may: FiniteMayOmega
    runs: PolicyEnvironmentRuns
    environment_ids: tuple[str, ...]
    robust_fibers: tuple[RobustRealizationFiber, ...]

    @classmethod
    def from_relation(
        cls,
        relation: FiniteRealizationRelation,
        runs: PolicyEnvironmentRuns,
        *,
        environment_ids: Iterable[str] | None = None,
    ) -> FiniteOmega:
        if not set(runs.witness_ids) <= set(relation.witness_ids):
            raise ValueError("run table contains witnesses outside the realization relation")
        scope = runs.normalize_scope(environment_ids)
        may = relation.may_omega()
        robust_fibers = []
        for may_fiber in may.fibers:
            realizing_witnesses = set(may_fiber.witness_ids)
            securing = []
            for policy_id in runs.policy_ids:
                environment_runs = tuple(
                    (
                        environment_id,
                        runs.witness_for(policy_id, environment_id),
                    )
                    for environment_id in scope
                )
                if all(
                    witness_id in realizing_witnesses
                    for _environment_id, witness_id in environment_runs
                ):
                    securing.append(
                        SecuringPolicyWitness(
                            policy_id=policy_id,
                            environment_runs=environment_runs,
                        )
                    )
            robust_fibers.append(
                RobustRealizationFiber(
                    family=may_fiber.family,
                    environment_ids=scope,
                    securing_witnesses=tuple(securing),
                )
            )
        return cls(
            omega_id=f"omega:{relation.relation_id}:{','.join(scope)}",
            may=may,
            runs=runs,
            environment_ids=scope,
            robust_fibers=tuple(robust_fibers),
        )

    def robust_fiber(self, family: Iterable[str]) -> RobustRealizationFiber:
        normalized = tuple(sorted(set(family)))
        if not set(normalized) <= set(self.may.class_ids):
            raise ValueError("family contains an unknown candidate class")
        try:
            return next(
                item for item in self.robust_fibers if item.family == normalized
            )
        except StopIteration as exc:
            raise AssertionError(
                "complete Robust fiber table is missing a family"
            ) from exc

    def robust_compatible_families(self) -> tuple[tuple[str, ...], ...]:
        return tuple(item.family for item in self.robust_fibers if item.nonempty)

    def robust_maximal_faces(self) -> tuple[tuple[str, ...], ...]:
        compatible = tuple(
            frozenset(family)
            for family in self.robust_compatible_families()
            if family
        )
        maximal = tuple(
            family
            for family in compatible
            if not any(family < other for other in compatible)
        )
        return tuple(sorted(tuple(sorted(face)) for face in maximal))

    def candidate_antitone_failures(self) -> tuple[dict[str, object], ...]:
        failures = []
        families = tuple(frozenset(item.family) for item in self.robust_fibers)
        for small in families:
            small_policies = set(self.robust_fiber(small).policy_ids)
            for large in families:
                if not small <= large:
                    continue
                large_policies = set(self.robust_fiber(large).policy_ids)
                if not large_policies <= small_policies:
                    failures.append(
                        {
                            "small": sorted(small),
                            "large": sorted(large),
                            "unexpected_policies": sorted(
                                large_policies - small_policies
                            ),
                        }
                    )
        return tuple(failures)

    def restriction_failures(self) -> tuple[dict[str, object], ...]:
        failures = []
        families = tuple(frozenset(item.family) for item in self.robust_fibers)
        for small in families:
            small_witnesses = {
                item.policy_id: item.environment_runs
                for item in self.robust_fiber(small).securing_witnesses
            }
            for large in families:
                if not small <= large:
                    continue
                for witness in self.robust_fiber(large).securing_witnesses:
                    if small_witnesses.get(witness.policy_id) != witness.environment_runs:
                        failures.append(
                            {
                                "small": sorted(small),
                                "large": sorted(large),
                                "policy_id": witness.policy_id,
                            }
                        )
        return tuple(failures)

    def robust_implies_may_failures(self) -> tuple[tuple[str, ...], ...]:
        may_compatible = set(self.may.compatible_families())
        return tuple(
            item.family
            for item in self.robust_fibers
            if item.nonempty and item.family not in may_compatible
        )

    def environment_antitone_failures(
        self,
        smaller: FiniteOmega,
    ) -> tuple[dict[str, object], ...]:
        if self.may.structural_payload() != smaller.may.structural_payload():
            raise ValueError("environment comparison requires the same May object")
        if self.runs != smaller.runs:
            raise ValueError("environment comparison requires the same run table")
        if not set(smaller.environment_ids) <= set(self.environment_ids):
            raise ValueError("the comparison scope is not a subset")

        failures = []
        for family in (item.family for item in self.robust_fibers):
            large_policies = set(self.robust_fiber(family).policy_ids)
            small_policies = set(smaller.robust_fiber(family).policy_ids)
            if not large_policies <= small_policies:
                failures.append(
                    {
                        "family": list(family),
                        "larger_environment_ids": list(self.environment_ids),
                        "smaller_environment_ids": list(smaller.environment_ids),
                        "unexpected_policies": sorted(
                            large_policies - small_policies
                        ),
                    }
                )
        return tuple(failures)

    def structural_payload(self) -> dict[str, object]:
        return {
            "may": self.may.structural_payload(),
            "environment_ids": list(self.environment_ids),
            "robust_fibers": [item.as_dict() for item in self.robust_fibers],
            "robust_maximal_faces": [
                list(face) for face in self.robust_maximal_faces()
            ],
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "omega_id": self.omega_id,
            "may": self.may.as_dict(),
            "policy_ids": list(self.runs.policy_ids),
            "environment_ids": list(self.environment_ids),
            "robust_fibers": [item.as_dict() for item in self.robust_fibers],
            "robust_compatible_families": [
                list(family) for family in self.robust_compatible_families()
            ],
            "robust_maximal_faces": [
                list(face) for face in self.robust_maximal_faces()
            ],
            "candidate_antitone_failures": list(
                self.candidate_antitone_failures()
            ),
            "restriction_failures": list(self.restriction_failures()),
            "robust_implies_may_failures": [
                list(family) for family in self.robust_implies_may_failures()
            ],
        }


def structural_digest(payload: Any) -> str:
    """Return a stable digest for a JSON-serializable structural payload."""

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
