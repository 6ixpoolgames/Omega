"""Finite CompensationClaim / NOLP v0 harness.

This module implements a narrow same-frame compensation object. It is not a
theory of value, standing, aggregation, population ethics, patienthood, or
Omega validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PROTOCOL_DOC = "docs/research_notes/omega_theory/compensation_claim_protocol_v0.md"


@dataclass(frozen=True)
class FactFrame:
    frame_id: str
    facts: tuple[str, ...]
    leq_pairs: frozenset[tuple[str, str]]

    def __post_init__(self) -> None:
        fact_set = set(self.facts)
        for fact in self.facts:
            if (fact, fact) not in self.leq_pairs:
                raise ValueError(f"frame {self.frame_id!r} missing reflexive pair for {fact!r}")
        for left, right in self.leq_pairs:
            if left not in fact_set or right not in fact_set:
                raise ValueError(f"frame {self.frame_id!r} has unknown order pair ({left!r}, {right!r})")

    def leq(self, left: str, right: str) -> bool:
        return (left, right) in self.leq_pairs


@dataclass(frozen=True)
class Profile:
    profile_id: str
    facts: frozenset[str]


@dataclass(frozen=True)
class CompensationClaim:
    claim_id: str
    contraction: Profile
    expansion: Profile
    cover_pairs: frozenset[tuple[str, str]]
    certified: bool
    frame_scope: str = "same_frame"

    def covers(self, lost_fact: str) -> bool:
        return any(left == lost_fact and right in self.expansion.facts for left, right in self.cover_pairs)


@dataclass(frozen=True)
class CompensationVerdict:
    claim_id: str
    complete_cover: bool
    certified: bool
    certified_compensation: bool
    nolp_refuses_contraction: bool
    uncovered_facts: tuple[str, ...]
    stability_label: str
    frame_scope: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "complete_cover": self.complete_cover,
            "certified": self.certified,
            "certified_compensation": self.certified_compensation,
            "nolp_refuses_contraction": self.nolp_refuses_contraction,
            "uncovered_facts": list(self.uncovered_facts),
            "stability_label": self.stability_label,
            "frame_scope": self.frame_scope,
        }


def same_frame() -> FactFrame:
    facts = ("repair_capacity", "revision_capacity", "task_capacity")
    return FactFrame(
        frame_id="same_recovery_frame",
        facts=facts,
        leq_pairs=frozenset((fact, fact) for fact in facts),
    )


def down_closed(profile: Profile, frame: FactFrame) -> frozenset[str]:
    return frozenset(
        fact
        for fact in frame.facts
        if any(profile_fact in profile.facts and frame.leq(fact, profile_fact) for profile_fact in frame.facts)
    )


def evaluate_compensation_claim(
    claim: CompensationClaim,
    frame: FactFrame,
    *,
    stability_label: str = "not_sampled",
) -> CompensationVerdict:
    lost_facts = down_closed(claim.contraction, frame)
    uncovered = tuple(sorted(fact for fact in lost_facts if not claim.covers(fact)))
    complete = not uncovered
    certified_compensation = complete and claim.certified
    return CompensationVerdict(
        claim_id=claim.claim_id,
        complete_cover=complete,
        certified=claim.certified,
        certified_compensation=certified_compensation,
        nolp_refuses_contraction=not certified_compensation,
        uncovered_facts=uncovered,
        stability_label=stability_label,
        frame_scope=claim.frame_scope,
    )


def certified_same_frame_claim() -> CompensationClaim:
    contraction = Profile("contract_repair", frozenset({"repair_capacity"}))
    expansion = Profile("expand_revision_and_repair", frozenset({"repair_capacity", "revision_capacity"}))
    return CompensationClaim(
        claim_id="certified_same_frame_cover",
        contraction=contraction,
        expansion=expansion,
        cover_pairs=frozenset({("repair_capacity", "repair_capacity")}),
        certified=True,
    )


def uncertified_claim() -> CompensationClaim:
    base = certified_same_frame_claim()
    return CompensationClaim(
        claim_id="uncertified_same_frame_cover",
        contraction=base.contraction,
        expansion=base.expansion,
        cover_pairs=base.cover_pairs,
        certified=False,
    )


def incomplete_claim() -> CompensationClaim:
    contraction = Profile("contract_repair", frozenset({"repair_capacity"}))
    expansion = Profile("expand_task_only", frozenset({"task_capacity"}))
    return CompensationClaim(
        claim_id="incomplete_task_cover",
        contraction=contraction,
        expansion=expansion,
        cover_pairs=frozenset(),
        certified=True,
    )


def believed_phantom_claim() -> CompensationClaim:
    contraction = Profile("contract_repair", frozenset({"repair_capacity"}))
    expansion = Profile("believed_expand_repair", frozenset({"repair_capacity"}))
    return CompensationClaim(
        claim_id="believed_phantom_cover",
        contraction=contraction,
        expansion=expansion,
        cover_pairs=frozenset({("repair_capacity", "repair_capacity")}),
        certified=True,
    )


def true_uncovered_claim() -> CompensationClaim:
    contraction = Profile("contract_repair", frozenset({"repair_capacity"}))
    expansion = Profile("true_expand_task_only", frozenset({"task_capacity"}))
    return CompensationClaim(
        claim_id="true_uncovered_cover",
        contraction=contraction,
        expansion=expansion,
        cover_pairs=frozenset(),
        certified=True,
    )


def certified_compensation_witness() -> dict[str, Any]:
    frame = same_frame()
    verdict = evaluate_compensation_claim(certified_same_frame_claim(), frame)
    return {
        "frame": frame.frame_id,
        "verdict": verdict.as_dict(),
        "read": "same-frame contraction has a complete certified cover",
    }


def uncertified_compensation_witness() -> dict[str, Any]:
    frame = same_frame()
    verdict = evaluate_compensation_claim(uncertified_claim(), frame)
    return {
        "frame": frame.frame_id,
        "verdict": verdict.as_dict(),
        "read": "complete but uncertified cover does not defeat NOLP refusal",
    }


def incomplete_compensation_witness() -> dict[str, Any]:
    frame = same_frame()
    verdict = evaluate_compensation_claim(incomplete_claim(), frame)
    return {
        "frame": frame.frame_id,
        "verdict": verdict.as_dict(),
        "read": "certified but incomplete cover does not defeat NOLP refusal",
    }


def phantom_compensation_witness() -> dict[str, Any]:
    frame = same_frame()
    believed = evaluate_compensation_claim(believed_phantom_claim(), frame)
    true = evaluate_compensation_claim(true_uncovered_claim(), frame)
    diverges = (
        believed.certified_compensation
        and not believed.nolp_refuses_contraction
        and true.nolp_refuses_contraction
    )
    return {
        "frame": frame.frame_id,
        "believed_verdict": believed.as_dict(),
        "true_verdict": true.as_dict(),
        "phantom_compensation_diverges": diverges,
        "read": "believed cover certifies compensation while true frame has an uncovered contraction",
    }


def kill_conditions(
    certified: dict[str, Any],
    uncertified: dict[str, Any],
    incomplete: dict[str, Any],
    phantom: dict[str, Any],
) -> dict[str, bool]:
    verdicts = [
        certified["verdict"],
        uncertified["verdict"],
        incomplete["verdict"],
        phantom["believed_verdict"],
        phantom["true_verdict"],
    ]
    return {
        "incomplete_cover_refused": incomplete["verdict"]["nolp_refuses_contraction"],
        "uncertified_cover_refused": uncertified["verdict"]["nolp_refuses_contraction"],
        "phantom_compensation_diverges": phantom["phantom_compensation_diverges"],
        "same_frame_only": all(verdict["frame_scope"] == "same_frame" for verdict in verdicts),
    }


def compensation_claim_summary() -> dict[str, Any]:
    certified = certified_compensation_witness()
    uncertified = uncertified_compensation_witness()
    incomplete = incomplete_compensation_witness()
    phantom = phantom_compensation_witness()
    kills = kill_conditions(certified, uncertified, incomplete, phantom)
    passes = (
        certified["verdict"]["certified_compensation"]
        and not certified["verdict"]["nolp_refuses_contraction"]
        and not uncertified["verdict"]["certified_compensation"]
        and uncertified["verdict"]["nolp_refuses_contraction"]
        and not incomplete["verdict"]["certified_compensation"]
        and incomplete["verdict"]["nolp_refuses_contraction"]
        and phantom["phantom_compensation_diverges"]
        and all(kills.values())
    )
    return {
        "protocol_doc": PROTOCOL_DOC,
        "verdict": "retained" if passes else "review",
        "certified_same_frame_cover": certified,
        "uncertified_cover": uncertified,
        "incomplete_cover": incomplete,
        "phantom_compensation": phantom,
        "kill_conditions": kills,
        "kill_conditions_pass": all(kills.values()),
        "nolp_v0_read": (
            "same-frame nonrecoverable contraction is refused unless a complete "
            "certified compensation cover is registered"
        ),
        "not_claimed": [
            "value",
            "standing",
            "aggregation",
            "population ethics",
            "patienthood",
            "cross-valuer compensation",
            "correct compensation order",
            "Omega validation",
        ],
    }


def compensation_verdict_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key in ("certified_same_frame_cover", "uncertified_cover", "incomplete_cover"):
        row = summary[key]["verdict"]
        rows.append({"case": key, **row})
    rows.append({"case": "phantom_believed", **summary["phantom_compensation"]["believed_verdict"]})
    rows.append({"case": "phantom_true", **summary["phantom_compensation"]["true_verdict"]})
    return rows
