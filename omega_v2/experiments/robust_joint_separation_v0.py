"""Strict finite separation of May realization and Robust securability."""

from __future__ import annotations

import json
from typing import Any, Mapping

from omega_v2.finite.realization import (
    FiniteOmega,
    FiniteRealizationRelation,
    PolicyEnvironmentRuns,
    RobustRealizationFiber,
    structural_digest,
)


PROTOCOL_DOC = (
    "docs/research_notes/omega_v2/"
    "robust_joint_separation_protocol_v0.md"
)
CANDIDATES = ("A", "B", "C")
WITNESSES = ("w_ab", "w_ac", "w_bc", "w_abc")
FULL_ENVIRONMENTS = ("north", "south")
NORTH_ENVIRONMENTS = ("north",)
PAIR_CANDIDATES = (("A", "B"), ("A", "C"), ("B", "C"))


def joint_realization_relation(
    *,
    duplicate_candidate: bool = False,
) -> FiniteRealizationRelation:
    candidate_ids = CANDIDATES
    incidence_rows = (
        ("A", "w_ab"),
        ("A", "w_ac"),
        ("A", "w_abc"),
        ("B", "w_ab"),
        ("B", "w_bc"),
        ("B", "w_abc"),
        ("C", "w_ac"),
        ("C", "w_bc"),
        ("C", "w_abc"),
    )
    if duplicate_candidate:
        candidate_ids = (*candidate_ids, "A_copy")
        incidence_rows = (
            *incidence_rows,
            ("A_copy", "w_ab"),
            ("A_copy", "w_ac"),
            ("A_copy", "w_abc"),
        )
    return FiniteRealizationRelation(
        relation_id=(
            "robust_joint_separation_duplicate"
            if duplicate_candidate
            else "robust_joint_separation"
        ),
        candidate_ids=candidate_ids,
        witness_ids=WITNESSES,
        incidence_rows=incidence_rows,
    )


def strict_policy_environment_runs() -> PolicyEnvironmentRuns:
    return PolicyEnvironmentRuns(
        table_id="robust_joint_separation_strict",
        policy_ids=("p_ab", "p_ac", "p_bc", "p_try"),
        environment_ids=FULL_ENVIRONMENTS,
        witness_ids=WITNESSES,
        outcome_rows=(
            ("p_ab", "north", "w_ab"),
            ("p_ab", "south", "w_ab"),
            ("p_ac", "north", "w_ac"),
            ("p_ac", "south", "w_ac"),
            ("p_bc", "north", "w_bc"),
            ("p_bc", "south", "w_bc"),
            ("p_try", "north", "w_abc"),
            ("p_try", "south", "w_ab"),
        ),
    )


def positive_policy_environment_runs() -> PolicyEnvironmentRuns:
    strict = strict_policy_environment_runs()
    return PolicyEnvironmentRuns(
        table_id="robust_joint_separation_positive",
        policy_ids=(*strict.policy_ids, "p_abc"),
        environment_ids=strict.environment_ids,
        witness_ids=strict.witness_ids,
        outcome_rows=(
            *strict.outcome_rows,
            ("p_abc", "north", "w_abc"),
            ("p_abc", "south", "w_abc"),
        ),
    )


def _family(
    omega: FiniteOmega,
    candidates: tuple[str, ...],
) -> tuple[str, ...]:
    return omega.may.quotient_family(candidates)


def _pair_fibers(
    omega: FiniteOmega,
) -> dict[str, RobustRealizationFiber]:
    return {
        "".join(pair): omega.robust_fiber(_family(omega, pair))
        for pair in PAIR_CANDIDATES
    }


def strict_joint_fixture(
    *,
    duplicate_candidate: bool = False,
) -> dict[str, Any]:
    relation = joint_realization_relation(
        duplicate_candidate=duplicate_candidate
    )
    runs = strict_policy_environment_runs()
    full = FiniteOmega.from_relation(
        relation,
        runs,
        environment_ids=FULL_ENVIRONMENTS,
    )
    north = FiniteOmega.from_relation(
        relation,
        runs,
        environment_ids=NORTH_ENVIRONMENTS,
    )
    triple_family = _family(full, CANDIDATES)
    return {
        "relation": relation,
        "runs": runs,
        "full": full,
        "north": north,
        "pair_fibers": _pair_fibers(full),
        "triple_family": triple_family,
        "full_triple_fiber": full.robust_fiber(triple_family),
        "north_triple_fiber": north.robust_fiber(triple_family),
        "may_triple_fiber": full.may.fiber(triple_family),
    }


def _complete_run_evidence(
    omega: FiniteOmega,
) -> bool:
    expected = set(omega.environment_ids)
    return all(
        {
            environment_id
            for environment_id, _witness_id in witness.environment_runs
        }
        == expected
        for fiber in omega.robust_fibers
        for witness in fiber.securing_witnesses
    )


def strict_joint_case() -> dict[str, Any]:
    fixture = strict_joint_fixture()
    duplicate = strict_joint_fixture(duplicate_candidate=True)
    full = fixture["full"]
    north = fixture["north"]
    pair_policy_ids = {
        pair: list(fiber.policy_ids)
        for pair, fiber in fixture["pair_fibers"].items()
    }
    full_triple = fixture["full_triple_fiber"]
    north_triple = fixture["north_triple_fiber"]
    may_triple = fixture["may_triple_fiber"]
    return {
        **fixture,
        "pair_policy_ids": pair_policy_ids,
        "all_pairs_robust": all(
            fiber.nonempty for fiber in fixture["pair_fibers"].values()
        ),
        "may_triple_witness_ids": list(may_triple.witness_ids),
        "may_triple_nonempty": may_triple.nonempty,
        "full_triple_robust": full_triple.nonempty,
        "full_triple_policy_ids": list(full_triple.policy_ids),
        "north_triple_robust": north_triple.nonempty,
        "north_triple_policy_ids": list(north_triple.policy_ids),
        "north_triple_runs": [
            witness.as_dict()
            for witness in north_triple.securing_witnesses
        ],
        "robust_maximal_face_count": len(full.robust_maximal_faces()),
        "may_downward_closure_failures": list(
            full.may.downward_closure_failures()
        ),
        "may_restriction_failures": list(
            full.may.restriction_failures()
        ),
        "candidate_antitone_failures": list(
            full.candidate_antitone_failures()
        ),
        "robust_restriction_failures": list(
            full.restriction_failures()
        ),
        "robust_implies_may_failures": [
            list(family) for family in full.robust_implies_may_failures()
        ],
        "environment_antitone_failures": list(
            full.environment_antitone_failures(north)
        ),
        "may_scope_invariant": (
            full.may.structural_payload() == north.may.structural_payload()
        ),
        "complete_full_run_evidence": _complete_run_evidence(full),
        "complete_north_run_evidence": _complete_run_evidence(north),
        "duplicate_raw_candidate_count": len(
            duplicate["relation"].candidate_ids
        ),
        "duplicate_quotient_candidate_count": len(
            duplicate["full"].may.candidate_classes
        ),
        "duplicate_may_invariant": (
            structural_digest(full.may.structural_payload())
            == structural_digest(
                duplicate["full"].may.structural_payload()
            )
        ),
        "duplicate_robust_invariant": (
            structural_digest(full.structural_payload())
            == structural_digest(
                duplicate["full"].structural_payload()
            )
        ),
        "pair_triple_scope_match": (
            {
                fiber.environment_ids
                for fiber in (
                    *fixture["pair_fibers"].values(),
                    full_triple,
                )
            }
            == {FULL_ENVIRONMENTS}
        ),
    }


def robust_positive_case() -> dict[str, Any]:
    relation = joint_realization_relation()
    runs = positive_policy_environment_runs()
    omega = FiniteOmega.from_relation(
        relation,
        runs,
        environment_ids=FULL_ENVIRONMENTS,
    )
    triple_family = _family(omega, CANDIDATES)
    triple = omega.robust_fiber(triple_family)
    return {
        "relation": relation,
        "runs": runs,
        "omega": omega,
        "triple_family": triple_family,
        "triple_fiber": triple,
        "triple_robust": triple.nonempty,
        "triple_policy_ids": list(triple.policy_ids),
        "triple_runs": [
            witness.as_dict() for witness in triple.securing_witnesses
        ],
        "may_payload_matches_strict": (
            omega.may.structural_payload()
            == strict_joint_fixture()["full"].may.structural_payload()
        ),
        "complete_run_evidence": _complete_run_evidence(omega),
    }


def _strict_public(case: Mapping[str, Any]) -> dict[str, object]:
    excluded = {
        "relation",
        "runs",
        "full",
        "north",
        "pair_fibers",
        "triple_family",
        "full_triple_fiber",
        "north_triple_fiber",
        "may_triple_fiber",
    }
    return {
        key: value
        for key, value in case.items()
        if key not in excluded
    }


def _positive_public(case: Mapping[str, Any]) -> dict[str, object]:
    excluded = {
        "relation",
        "runs",
        "omega",
        "triple_family",
        "triple_fiber",
    }
    return {
        key: value
        for key, value in case.items()
        if key not in excluded
    }


def robust_joint_separation_summary() -> dict[str, Any]:
    strict = strict_joint_case()
    positive = robust_positive_case()
    expected_pair_policies = {
        "AB": ["p_ab", "p_try"],
        "AC": ["p_ac"],
        "BC": ["p_bc"],
    }
    structural_failures = (
        strict["may_downward_closure_failures"]
        or strict["may_restriction_failures"]
        or strict["candidate_antitone_failures"]
        or strict["robust_restriction_failures"]
        or strict["robust_implies_may_failures"]
        or strict["environment_antitone_failures"]
    )
    case_results = {
        "may_triple_nonempty": (
            strict["may_triple_nonempty"]
            and strict["may_triple_witness_ids"] == ["w_abc"]
        ),
        "all_pairs_robust": strict["all_pairs_robust"],
        "pair_policy_sets_exact": (
            strict["pair_policy_ids"] == expected_pair_policies
        ),
        "full_triple_not_robust": (
            not strict["full_triple_robust"]
            and strict["full_triple_policy_ids"] == []
        ),
        "north_triple_robust": (
            strict["north_triple_robust"]
            and strict["north_triple_policy_ids"] == ["p_try"]
        ),
        "environment_scope_isolates_failure": (
            strict["may_scope_invariant"]
            and strict["north_triple_robust"]
            and not strict["full_triple_robust"]
        ),
        "positive_control": (
            positive["triple_robust"]
            and positive["triple_policy_ids"] == ["p_abc"]
            and positive["may_payload_matches_strict"]
        ),
        "duplicate_invariance": (
            strict["duplicate_raw_candidate_count"] == 4
            and strict["duplicate_quotient_candidate_count"] == 3
            and strict["duplicate_may_invariant"]
            and strict["duplicate_robust_invariant"]
        ),
        "structural_laws": not structural_failures,
        "complete_run_evidence": (
            strict["complete_full_run_evidence"]
            and strict["complete_north_run_evidence"]
            and positive["complete_run_evidence"]
        ),
        "pair_triple_scope_match": strict["pair_triple_scope_match"],
    }
    kill_conditions = {
        "may_triple_empty": not case_results["may_triple_nonempty"],
        "pair_not_robust": not case_results["all_pairs_robust"],
        "pair_policy_set_changed": not case_results[
            "pair_policy_sets_exact"
        ],
        "full_triple_robust": not case_results[
            "full_triple_not_robust"
        ],
        "north_triple_not_robust": not case_results[
            "north_triple_robust"
        ],
        "scope_failed_to_isolate": not case_results[
            "environment_scope_isolates_failure"
        ],
        "positive_control_failed": not case_results["positive_control"],
        "duplicate_changed_payload": not case_results[
            "duplicate_invariance"
        ],
        "structural_law_failed": not case_results["structural_laws"],
        "run_evidence_discarded": not case_results[
            "complete_run_evidence"
        ],
        "pair_triple_scope_mismatch": not case_results[
            "pair_triple_scope_match"
        ],
    }
    retained = all(case_results.values()) and not any(kill_conditions.values())
    return {
        "status": "retained" if retained else "failed",
        "verdict": (
            "joint_realizability_does_not_imply_joint_robust_securability"
            if retained
            else "strict_robust_separation_failed"
        ),
        "protocol_doc": PROTOCOL_DOC,
        "semantics": {
            "may": "exists_joint_realization_witness",
            "robust": "exists_one_policy_forall_declared_environments",
            "run_model": "total_deterministic_lookup_table",
        },
        "strict": _strict_public(strict),
        "positive": _positive_public(positive),
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "claim_boundary": (
            "Finite deterministic lookup-table separation only; not dynamic "
            "control, empirical robustness, candidate correctness, identity, "
            "agency, valuerhood, standing, value, moral license, or Omega "
            "validation."
        ),
        "_objects": {
            "strict": strict,
            "positive": positive,
        },
    }


def may_fiber_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    strict = summary["_objects"]["strict"]
    return [
        {
            "family": "|".join(fiber.family),
            "witness_ids": "|".join(fiber.witness_ids),
            "nonempty": fiber.nonempty,
        }
        for fiber in strict["full"].may.fibers
    ]


def robust_fiber_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    strict = summary["_objects"]["strict"]
    positive = summary["_objects"]["positive"]
    cases = {
        "strict_full": strict["full"],
        "strict_north": strict["north"],
        "positive_full": positive["omega"],
    }
    return [
        {
            "case": case,
            "environment_ids": "|".join(omega.environment_ids),
            "family": "|".join(fiber.family),
            "policy_ids": "|".join(fiber.policy_ids),
            "run_witnesses": "|".join(
                f"{witness.policy_id}:"
                + ",".join(
                    f"{environment_id}={witness_id}"
                    for environment_id, witness_id in witness.environment_runs
                )
                for witness in fiber.securing_witnesses
            ),
            "nonempty": fiber.nonempty,
        }
        for case, omega in cases.items()
        for fiber in omega.robust_fibers
    ]


def policy_environment_run_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    strict = summary["_objects"]["strict"]
    positive = summary["_objects"]["positive"]
    return [
        {
            "case": case,
            "policy_id": policy_id,
            "environment_id": environment_id,
            "witness_id": witness_id,
        }
        for case, runs in (
            ("strict", strict["runs"]),
            ("positive", positive["runs"]),
        )
        for policy_id, environment_id, witness_id in runs.outcome_rows
    ]


def environment_scope_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    strict = summary["_objects"]["strict"]
    return [
        {
            "scope": scope,
            "environment_ids": "|".join(omega.environment_ids),
            "may_triple_witness_ids": "|".join(
                omega.may.fiber(strict["triple_family"]).witness_ids
            ),
            "robust_triple": omega.robust_fiber(
                strict["triple_family"]
            ).nonempty,
            "triple_policy_ids": "|".join(
                omega.robust_fiber(strict["triple_family"]).policy_ids
            ),
        }
        for scope, omega in (
            ("north", strict["north"]),
            ("full", strict["full"]),
        )
    ]


def structural_control_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    return [
        {"control": case, "passed": passed}
        for case, passed in summary["case_results"].items()
    ] + [
        {
            "control": f"kill::{condition}",
            "passed": not fired,
        }
        for condition, fired in summary["kill_conditions"].items()
    ]


def summary_digest(summary: Mapping[str, Any]) -> str:
    public = {key: value for key, value in summary.items() if key != "_objects"}
    return structural_digest(json.loads(json.dumps(public, sort_keys=True)))
