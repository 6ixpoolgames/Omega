"""Finite component factorizations and process-interface transport audits."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from omega_v2.finite.process_interfaces import (
    PRIMARY_PROCESS_QUERY,
    BinarySynchronousSystem,
    EvidenceMode,
    IdentificationStatus,
    InterfaceQuery,
    ProcessInterfaceProfile,
    profile_process_interface,
)


def _ordered_subset(
    values: Iterable[str],
    order: tuple[str, ...],
) -> tuple[str, ...]:
    selected = set(values)
    unknown = selected - set(order)
    if unknown:
        raise ValueError(f"unknown identifiers: {sorted(unknown)}")
    return tuple(item for item in order if item in selected)


def _nonempty_proper_subsets(
    values: tuple[str, ...],
) -> tuple[tuple[str, ...], ...]:
    return tuple(
        subset
        for size in range(1, len(values))
        for subset in itertools.combinations(values, size)
    )


@dataclass(frozen=True)
class FactorBlock:
    """One named block in a partition of primitive components."""

    block_id: str
    members: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.block_id:
            raise ValueError("block_id must be nonempty")
        if not self.members:
            raise ValueError("factor blocks must be nonempty")
        if len(self.members) != len(set(self.members)):
            raise ValueError("factor block members must be unique")
        if any(not member for member in self.members):
            raise ValueError("primitive component identifiers must be nonempty")


@dataclass(frozen=True)
class ComponentFactorization:
    """A finite partition of a fixed primitive component universe."""

    factorization_id: str
    primitive_ids: tuple[str, ...]
    blocks: tuple[FactorBlock, ...]

    def __post_init__(self) -> None:
        if not self.factorization_id:
            raise ValueError("factorization_id must be nonempty")
        if not self.primitive_ids:
            raise ValueError("primitive_ids must be nonempty")
        if len(self.primitive_ids) != len(set(self.primitive_ids)):
            raise ValueError("primitive_ids must be unique")
        if any(not item for item in self.primitive_ids):
            raise ValueError("primitive identifiers must be nonempty")
        if not self.blocks:
            raise ValueError("a factorization must contain at least one block")
        block_ids = tuple(block.block_id for block in self.blocks)
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("factor block identifiers must be unique")

        primitive_set = set(self.primitive_ids)
        seen: set[str] = set()
        for block in self.blocks:
            members = set(block.members)
            unknown = members - primitive_set
            if unknown:
                raise ValueError(
                    f"factor block contains unknown primitives: {sorted(unknown)}"
                )
            overlap = seen & members
            if overlap:
                raise ValueError(
                    f"factor blocks overlap on primitives: {sorted(overlap)}"
                )
            seen.update(members)
        omitted = primitive_set - seen
        if omitted:
            raise ValueError(
                f"factorization omits primitives: {sorted(omitted)}"
            )

    @classmethod
    def from_mapping(
        cls,
        *,
        factorization_id: str,
        primitive_ids: tuple[str, ...],
        blocks: dict[str, Iterable[str]],
    ) -> ComponentFactorization:
        return cls(
            factorization_id=factorization_id,
            primitive_ids=primitive_ids,
            blocks=tuple(
                FactorBlock(
                    block_id=block_id,
                    members=_ordered_subset(members, primitive_ids),
                )
                for block_id, members in blocks.items()
            ),
        )

    @property
    def block_ids(self) -> tuple[str, ...]:
        return tuple(block.block_id for block in self.blocks)

    @property
    def block_map(self) -> dict[str, FactorBlock]:
        return {block.block_id: block for block in self.blocks}

    @property
    def member_to_block(self) -> dict[str, str]:
        return {
            member: block.block_id
            for block in self.blocks
            for member in block.members
        }

    @property
    def concrete_partition(self) -> tuple[tuple[str, ...], ...]:
        return tuple(
            _ordered_subset(block.members, self.primitive_ids)
            for block in self.blocks
        )

    def concretize(self, block_ids: Iterable[str]) -> tuple[str, ...]:
        selected = _ordered_subset(block_ids, self.block_ids)
        members = {
            member
            for block_id in selected
            for member in self.block_map[block_id].members
        }
        return _ordered_subset(members, self.primitive_ids)

    def represent(self, primitive_members: Iterable[str]) -> tuple[str, ...] | None:
        selected = _ordered_subset(primitive_members, self.primitive_ids)
        selected_set = set(selected)
        represented = tuple(
            block.block_id
            for block in self.blocks
            if set(block.members) <= selected_set
        )
        if set(self.concretize(represented)) != selected_set:
            return None
        return represented

    def saturate(self, primitive_members: Iterable[str]) -> InterfaceSaturation:
        selected = _ordered_subset(primitive_members, self.primitive_ids)
        selected_set = set(selected)
        blocks = tuple(
            block.block_id
            for block in self.blocks
            if set(block.members) & selected_set
        )
        concrete = self.concretize(blocks)
        added = _ordered_subset(set(concrete) - selected_set, self.primitive_ids)
        return InterfaceSaturation(
            requested_members=selected,
            target_blocks=blocks,
            saturated_members=concrete,
            added_members=added,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "factorization_id": self.factorization_id,
            "primitive_ids": list(self.primitive_ids),
            "blocks": [
                {
                    "block_id": block.block_id,
                    "members": list(block.members),
                }
                for block in self.blocks
            ],
        }


@dataclass(frozen=True)
class InterfaceSaturation:
    requested_members: tuple[str, ...]
    target_blocks: tuple[str, ...]
    saturated_members: tuple[str, ...]
    added_members: tuple[str, ...]

    @property
    def exact(self) -> bool:
        return not self.added_members

    def as_dict(self) -> dict[str, object]:
        return {
            "requested_members": list(self.requested_members),
            "target_blocks": list(self.target_blocks),
            "saturated_members": list(self.saturated_members),
            "added_members": list(self.added_members),
            "exact": self.exact,
        }


@dataclass(frozen=True)
class BlockTransport:
    source_block_id: str
    source_members: tuple[str, ...]
    target_block_ids: tuple[str, ...]
    target_members: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "source_block_id": self.source_block_id,
            "source_members": list(self.source_members),
            "target_block_ids": list(self.target_block_ids),
            "target_members": list(self.target_members),
        }


@dataclass(frozen=True)
class BlockTransportFailure:
    source_block_id: str
    source_members: tuple[str, ...]
    overlapping_target_block_ids: tuple[str, ...]
    overlapping_target_members: tuple[str, ...]
    missing_source_members: tuple[str, ...]
    added_target_members: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "source_block_id": self.source_block_id,
            "source_members": list(self.source_members),
            "overlapping_target_block_ids": list(
                self.overlapping_target_block_ids
            ),
            "overlapping_target_members": list(
                self.overlapping_target_members
            ),
            "missing_source_members": list(self.missing_source_members),
            "added_target_members": list(self.added_target_members),
        }


@dataclass(frozen=True)
class InterventionTransportAudit:
    source_factorization_id: str
    target_factorization_id: str
    exact: bool
    transports: tuple[BlockTransport, ...]
    failures: tuple[BlockTransportFailure, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "source_factorization_id": self.source_factorization_id,
            "target_factorization_id": self.target_factorization_id,
            "exact": self.exact,
            "transports": [
                transport.as_dict() for transport in self.transports
            ],
            "failures": [failure.as_dict() for failure in self.failures],
        }


def audit_intervention_transport(
    source: ComponentFactorization,
    target: ComponentFactorization,
) -> InterventionTransportAudit:
    """Check whether each source-block intervention decomposes in the target."""

    if source.primitive_ids != target.primitive_ids:
        raise ValueError(
            "intervention transport requires the same ordered primitive universe"
        )

    transports: list[BlockTransport] = []
    failures: list[BlockTransportFailure] = []
    primitive_order = source.primitive_ids
    for source_block in source.blocks:
        source_members = set(source_block.members)
        contained = tuple(
            block
            for block in target.blocks
            if set(block.members) <= source_members
        )
        contained_members = {
            member for block in contained for member in block.members
        }
        if contained_members == source_members:
            transports.append(
                BlockTransport(
                    source_block_id=source_block.block_id,
                    source_members=_ordered_subset(
                        source_members,
                        primitive_order,
                    ),
                    target_block_ids=tuple(
                        block.block_id for block in contained
                    ),
                    target_members=_ordered_subset(
                        contained_members,
                        primitive_order,
                    ),
                )
            )
            continue

        overlapping = tuple(
            block
            for block in target.blocks
            if set(block.members) & source_members
        )
        overlapping_members = {
            member for block in overlapping for member in block.members
        }
        failures.append(
            BlockTransportFailure(
                source_block_id=source_block.block_id,
                source_members=_ordered_subset(
                    source_members,
                    primitive_order,
                ),
                overlapping_target_block_ids=tuple(
                    block.block_id for block in overlapping
                ),
                overlapping_target_members=_ordered_subset(
                    overlapping_members,
                    primitive_order,
                ),
                missing_source_members=_ordered_subset(
                    source_members - contained_members,
                    primitive_order,
                ),
                added_target_members=_ordered_subset(
                    overlapping_members - source_members,
                    primitive_order,
                ),
            )
        )

    return InterventionTransportAudit(
        source_factorization_id=source.factorization_id,
        target_factorization_id=target.factorization_id,
        exact=not failures,
        transports=tuple(transports),
        failures=tuple(failures),
    )


@dataclass(frozen=True)
class FactorizedInterfaceProfile:
    block_interface: tuple[str, ...]
    primitive_interface: tuple[str, ...]
    profile: ProcessInterfaceProfile

    @property
    def block_interface_id(self) -> str:
        return "{" + ",".join(self.block_interface) + "}"

    def as_dict(self) -> dict[str, object]:
        return {
            "block_interface_id": self.block_interface_id,
            "block_interface": list(self.block_interface),
            "primitive_interface": list(self.primitive_interface),
            **self.profile.as_dict(),
        }


@dataclass(frozen=True)
class FactorizedInterfaceIdentification:
    system_id: str
    substrate_signature: tuple[object, ...]
    factorization: ComponentFactorization
    query: InterfaceQuery
    evidence_mode: EvidenceMode
    horizon: int
    profiles: tuple[FactorizedInterfaceProfile, ...]
    certified_block_interfaces: tuple[tuple[str, ...], ...]
    unresolved_block_interfaces: tuple[tuple[str, ...], ...]
    rejected_block_interfaces: tuple[tuple[str, ...], ...]
    retained_minimal_block_interfaces: tuple[tuple[str, ...], ...]
    retained_minimal_primitive_interfaces: tuple[tuple[str, ...], ...]
    status: IdentificationStatus

    def as_dict(self) -> dict[str, object]:
        return {
            "system_id": self.system_id,
            "factorization_id": self.factorization.factorization_id,
            "query_id": self.query.query_id,
            "required_true": list(self.query.required_true),
            "evidence_mode": self.evidence_mode.value,
            "horizon": self.horizon,
            "status": self.status.value,
            "certified_block_interfaces": [
                list(interface)
                for interface in self.certified_block_interfaces
            ],
            "unresolved_block_interfaces": [
                list(interface)
                for interface in self.unresolved_block_interfaces
            ],
            "rejected_block_interfaces": [
                list(interface)
                for interface in self.rejected_block_interfaces
            ],
            "retained_minimal_block_interfaces": [
                list(interface)
                for interface in self.retained_minimal_block_interfaces
            ],
            "retained_minimal_primitive_interfaces": [
                list(interface)
                for interface in self.retained_minimal_primitive_interfaces
            ],
            "profiles": [profile.as_dict() for profile in self.profiles],
        }


def _substrate_signature(
    system: BinarySynchronousSystem,
) -> tuple[object, ...]:
    return (
        system.component_ids,
        tuple(sorted(system.transition_rows)),
        tuple(sorted(system.initial_states)),
    )


def factorized_interface_profiles(
    system: BinarySynchronousSystem,
    factorization: ComponentFactorization,
    *,
    evidence_mode: EvidenceMode,
    horizon: int,
) -> tuple[FactorizedInterfaceProfile, ...]:
    if system.component_ids != factorization.primitive_ids:
        raise ValueError(
            "factorization primitive order must match system components"
        )
    return tuple(
        FactorizedInterfaceProfile(
            block_interface=block_interface,
            primitive_interface=factorization.concretize(block_interface),
            profile=profile_process_interface(
                system,
                factorization.concretize(block_interface),
                evidence_mode=evidence_mode,
                horizon=horizon,
            ),
        )
        for block_interface in _nonempty_proper_subsets(
            factorization.block_ids
        )
    )


def _minimal_factorized_interfaces(
    interfaces: Iterable[FactorizedInterfaceProfile],
) -> tuple[FactorizedInterfaceProfile, ...]:
    retained = tuple(interfaces)
    concrete = {
        profile.block_interface: frozenset(profile.primitive_interface)
        for profile in retained
    }
    return tuple(
        profile
        for profile in retained
        if not any(
            other_members < concrete[profile.block_interface]
            for other, other_members in concrete.items()
            if other != profile.block_interface
        )
    )


def identify_factorized_interfaces(
    system: BinarySynchronousSystem,
    factorization: ComponentFactorization,
    query: InterfaceQuery = PRIMARY_PROCESS_QUERY,
    *,
    evidence_mode: EvidenceMode,
    horizon: int,
) -> FactorizedInterfaceIdentification:
    """Identify all minimal block interfaces under one declared factorization."""

    profiles = factorized_interface_profiles(
        system,
        factorization,
        evidence_mode=evidence_mode,
        horizon=horizon,
    )
    certified: list[FactorizedInterfaceProfile] = []
    unresolved: list[FactorizedInterfaceProfile] = []
    rejected: list[FactorizedInterfaceProfile] = []
    for profile in profiles:
        values = tuple(
            profile.profile.feature(feature)
            for feature in query.required_true
        )
        if any(value is False for value in values):
            rejected.append(profile)
        elif all(value is True for value in values):
            certified.append(profile)
        else:
            unresolved.append(profile)

    retained = (*certified, *unresolved)
    minimal = _minimal_factorized_interfaces(retained)
    if unresolved:
        status = IdentificationStatus.UNRESOLVED
    elif not certified:
        status = IdentificationStatus.NO_CANDIDATE
    elif len(minimal) == 1:
        status = IdentificationStatus.IDENTIFIED
    else:
        status = IdentificationStatus.SET_IDENTIFIED

    return FactorizedInterfaceIdentification(
        system_id=system.system_id,
        substrate_signature=_substrate_signature(system),
        factorization=factorization,
        query=query,
        evidence_mode=evidence_mode,
        horizon=horizon,
        profiles=profiles,
        certified_block_interfaces=tuple(
            profile.block_interface for profile in certified
        ),
        unresolved_block_interfaces=tuple(
            profile.block_interface for profile in unresolved
        ),
        rejected_block_interfaces=tuple(
            profile.block_interface for profile in rejected
        ),
        retained_minimal_block_interfaces=tuple(
            profile.block_interface for profile in minimal
        ),
        retained_minimal_primitive_interfaces=tuple(
            profile.primitive_interface for profile in minimal
        ),
        status=status,
    )


class InterfaceTransportStatus(str, Enum):
    INVARIANT = "INVARIANT"
    REFINED = "REFINED"
    MERGED = "MERGED"
    OBSTRUCTED = "OBSTRUCTED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class InterfaceFamilyTransport:
    source_factorization_id: str
    target_factorization_id: str
    source_query_id: str
    target_query_id: str
    source_evidence_mode: EvidenceMode
    target_evidence_mode: EvidenceMode
    source_horizon: int
    target_horizon: int
    status: InterfaceTransportStatus
    reason: str
    source_minimal_interfaces: tuple[tuple[str, ...], ...]
    target_minimal_interfaces: tuple[tuple[str, ...], ...]
    forward_intervention_audit: InterventionTransportAudit
    reverse_intervention_audit: InterventionTransportAudit
    target_saturations: tuple[InterfaceSaturation, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "source_factorization_id": self.source_factorization_id,
            "target_factorization_id": self.target_factorization_id,
            "source_query_id": self.source_query_id,
            "target_query_id": self.target_query_id,
            "source_evidence_mode": self.source_evidence_mode.value,
            "target_evidence_mode": self.target_evidence_mode.value,
            "source_horizon": self.source_horizon,
            "target_horizon": self.target_horizon,
            "status": self.status.value,
            "reason": self.reason,
            "source_minimal_interfaces": [
                list(interface) for interface in self.source_minimal_interfaces
            ],
            "target_minimal_interfaces": [
                list(interface) for interface in self.target_minimal_interfaces
            ],
            "forward_intervention_audit": (
                self.forward_intervention_audit.as_dict()
            ),
            "reverse_intervention_audit": (
                self.reverse_intervention_audit.as_dict()
            ),
            "target_saturations": [
                saturation.as_dict()
                for saturation in self.target_saturations
            ],
        }


def _strictly_refines(
    source_interfaces: tuple[tuple[str, ...], ...],
    target_interfaces: tuple[tuple[str, ...], ...],
) -> bool:
    source_sets = tuple(frozenset(interface) for interface in source_interfaces)
    target_sets = tuple(frozenset(interface) for interface in target_interfaces)
    return bool(source_sets and target_sets) and all(
        any(target < source for source in source_sets)
        for target in target_sets
    ) and all(
        any(target < source or target == source for target in target_sets)
        for source in source_sets
    )


def compare_interface_families(
    source: FactorizedInterfaceIdentification,
    target: FactorizedInterfaceIdentification,
) -> InterfaceFamilyTransport:
    """Compare retained minimal families without selecting representatives."""

    forward = audit_intervention_transport(
        source.factorization,
        target.factorization,
    )
    reverse = audit_intervention_transport(
        target.factorization,
        source.factorization,
    )
    source_minima = source.retained_minimal_primitive_interfaces
    target_minima = target.retained_minimal_primitive_interfaces
    saturations = tuple(
        target.factorization.saturate(interface)
        for interface in source_minima
    )

    common = {
        "source_factorization_id": source.factorization.factorization_id,
        "target_factorization_id": target.factorization.factorization_id,
        "source_query_id": source.query.query_id,
        "target_query_id": target.query.query_id,
        "source_evidence_mode": source.evidence_mode,
        "target_evidence_mode": target.evidence_mode,
        "source_horizon": source.horizon,
        "target_horizon": target.horizon,
        "source_minimal_interfaces": source_minima,
        "target_minimal_interfaces": target_minima,
        "forward_intervention_audit": forward,
        "reverse_intervention_audit": reverse,
        "target_saturations": saturations,
    }

    if source.substrate_signature != target.substrate_signature:
        return InterfaceFamilyTransport(
            status=InterfaceTransportStatus.OBSTRUCTED,
            reason="substrate_mismatch",
            **common,
        )
    if source.query != target.query:
        return InterfaceFamilyTransport(
            status=InterfaceTransportStatus.OBSTRUCTED,
            reason="query_mismatch",
            **common,
        )
    if (
        source.evidence_mode != target.evidence_mode
        or source.horizon != target.horizon
    ):
        return InterfaceFamilyTransport(
            status=InterfaceTransportStatus.OBSTRUCTED,
            reason="evidence_contract_mismatch",
            **common,
        )
    if (
        source.status is IdentificationStatus.UNRESOLVED
        or target.status is IdentificationStatus.UNRESOLVED
    ):
        return InterfaceFamilyTransport(
            status=InterfaceTransportStatus.UNRESOLVED,
            reason="causal_features_unknown",
            **common,
        )

    source_set = {frozenset(interface) for interface in source_minima}
    target_set = {frozenset(interface) for interface in target_minima}
    if source_set == target_set and (forward.exact or reverse.exact):
        return InterfaceFamilyTransport(
            status=InterfaceTransportStatus.INVARIANT,
            reason="equal_concrete_minimal_families",
            **common,
        )
    if forward.exact and _strictly_refines(source_minima, target_minima):
        return InterfaceFamilyTransport(
            status=InterfaceTransportStatus.REFINED,
            reason="target_exposes_strictly_smaller_minimal_interfaces",
            **common,
        )
    if reverse.exact and _strictly_refines(target_minima, source_minima):
        return InterfaceFamilyTransport(
            status=InterfaceTransportStatus.MERGED,
            reason="target_merges_source_minimal_interfaces",
            **common,
        )
    return InterfaceFamilyTransport(
        status=InterfaceTransportStatus.OBSTRUCTED,
        reason="no_exact_family_transport",
        **common,
    )
