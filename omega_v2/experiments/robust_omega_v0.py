"""Finite fixtures for witness-retaining May and Robust Omega."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping

from omega_v2.finite.model import (
    ControlledMarkovSystem,
    DeterministicPolicy,
    FinitePath,
)
from omega_v2.finite.realization import (
    FiniteOmega,
    FiniteRealizationRelation,
    PolicyEnvironmentRuns,
    structural_digest,
)


PROTOCOL_DOC = "docs/research_notes/omega_v2/robust_omega_protocol_v0.md"
LEGACY_MAY_STRUCTURAL_DIGEST = (
    "b79cd2f3be3a4b98047055a0776bfe4411109ca0502678d75d14bc00560e8e28"
)


@dataclass(frozen=True)
class DeterministicEnvironmentScenario:
    """One total deterministic finite environment model and rollout boundary."""

    environment_id: str
    system: ControlledMarkovSystem[str, str]
    initial_state: str
    horizon: int

    def __post_init__(self) -> None:
        if not self.environment_id:
            raise ValueError("environment_id must be nonempty")
        self.system.require_state(self.initial_state)
        if self.horizon <= 0:
            raise ValueError("environment horizon must be positive")


def deterministic_rollout(
    scenario: DeterministicEnvironmentScenario,
    policy: DeterministicPolicy[str, str],
) -> FinitePath[str, str]:
    """Run one policy in a scenario whose selected rows are point masses."""

    policy.validate(scenario.system)
    states = [scenario.initial_state]
    actions = []
    current = scenario.initial_state
    for _step in range(scenario.horizon):
        action = policy.action_at(current)
        distribution = scenario.system.distribution(current, action)
        if len(distribution.rows) != 1 or distribution.rows[0][1] != 1:
            raise ValueError(
                "deterministic environment rollout requires point-mass rows"
            )
        target = distribution.rows[0][0]
        actions.append(action)
        states.append(target)
        current = target
    return FinitePath(states=tuple(states), actions=tuple(actions))


def generate_policy_environment_runs(
    fixture_id: str,
    scenarios: Iterable[DeterministicEnvironmentScenario],
    policies: Iterable[DeterministicPolicy[str, str]],
) -> tuple[PolicyEnvironmentRuns, dict[str, FinitePath[str, str]]]:
    """Generate a total outcome table and retain every concrete finite path."""

    retained_scenarios = tuple(scenarios)
    retained_policies = tuple(policies)
    if not fixture_id:
        raise ValueError("fixture_id must be nonempty")
    if not retained_scenarios:
        raise ValueError("at least one environment scenario is required")
    if not retained_policies:
        raise ValueError("at least one policy is required")

    first = retained_scenarios[0].system
    if any(
        scenario.system.states != first.states
        or scenario.system.actions != first.actions
        or scenario.horizon != retained_scenarios[0].horizon
        for scenario in retained_scenarios[1:]
    ):
        raise ValueError(
            "environment scenarios must share states, actions, and horizon"
        )

    witness_paths: dict[str, FinitePath[str, str]] = {}
    rows = []
    for policy in retained_policies:
        for scenario in retained_scenarios:
            witness_id = (
                f"run:{fixture_id}:{policy.policy_id}:{scenario.environment_id}"
            )
            witness_paths[witness_id] = deterministic_rollout(scenario, policy)
            rows.append((policy.policy_id, scenario.environment_id, witness_id))

    runs = PolicyEnvironmentRuns(
        table_id=f"runs:{fixture_id}",
        policy_ids=tuple(policy.policy_id for policy in retained_policies),
        environment_ids=tuple(
            scenario.environment_id for scenario in retained_scenarios
        ),
        witness_ids=tuple(witness_paths),
        outcome_rows=tuple(rows),
    )
    return runs, witness_paths


def audit_generated_runs(
    scenarios: Iterable[DeterministicEnvironmentScenario],
    policies: Iterable[DeterministicPolicy[str, str]],
    runs: PolicyEnvironmentRuns,
    witness_paths: Mapping[str, FinitePath[str, str]],
) -> bool:
    """Re-run every policy/environment case and compare it with the table."""

    scenario_map = {
        scenario.environment_id: scenario for scenario in scenarios
    }
    policy_map = {policy.policy_id: policy for policy in policies}
    return all(
        witness_paths[witness_id]
        == deterministic_rollout(
            scenario_map[environment_id],
            policy_map[policy_id],
        )
        for policy_id, environment_id, witness_id in runs.outcome_rows
    )


def relation_from_terminal_membership(
    relation_id: str,
    runs: PolicyEnvironmentRuns,
    witness_paths: Mapping[str, FinitePath[str, str]],
    terminal_membership: Mapping[str, Iterable[str]],
    *,
    duplicate_candidate: str | None = None,
) -> FiniteRealizationRelation:
    """Build candidate incidence from the terminal states of generated runs."""

    retained_membership = {
        state: frozenset(candidates)
        for state, candidates in terminal_membership.items()
    }
    candidate_ids = tuple(
        sorted(
            {
                candidate
                for candidates in retained_membership.values()
                for candidate in candidates
            }
        )
    )
    incidence_rows = [
        (candidate, witness_id)
        for witness_id, path in witness_paths.items()
        for candidate in retained_membership.get(path.end, frozenset())
    ]
    if duplicate_candidate is not None:
        if duplicate_candidate not in candidate_ids:
            raise ValueError("duplicate candidate must name a retained candidate")
        duplicate_id = f"{duplicate_candidate}_copy"
        candidate_ids = (*candidate_ids, duplicate_id)
        incidence_rows.extend(
            (duplicate_id, witness_id)
            for candidate, witness_id in tuple(incidence_rows)
            if candidate == duplicate_candidate
        )
    return FiniteRealizationRelation(
        relation_id=relation_id,
        candidate_ids=candidate_ids,
        witness_ids=runs.witness_ids,
        incidence_rows=tuple(incidence_rows),
    )


def _deterministic_choice_system(
    system_id: str,
    *,
    states: tuple[str, ...],
    actions: tuple[str, ...],
    start_targets: Mapping[str, str],
) -> ControlledMarkovSystem[str, str]:
    transitions = []
    for state in states:
        for action in actions:
            target = start_targets[action] if state == "start" else state
            transitions.append((state, action, target, Fraction(1)))
    return ControlledMarkovSystem(
        system_id=system_id,
        states=states,
        actions=actions,
        transitions=tuple(transitions),
    )


def _constant_choice_policy(
    system: ControlledMarkovSystem[str, str],
    action: str,
    *,
    policy_id: str,
) -> DeterministicPolicy[str, str]:
    return DeterministicPolicy(
        policy_id=policy_id,
        rows=tuple((state, action) for state in system.states),
    )


def may_hollow_triangle_relation(
    *,
    duplicate_candidate: bool = False,
) -> FiniteRealizationRelation:
    candidate_ids = ("A", "B", "C")
    incidence_rows = (
        ("A", "history:a0"),
        ("A", "history:a1"),
        ("B", "history:a0"),
        ("B", "history:a2"),
        ("C", "history:a1"),
        ("C", "history:a2"),
    )
    if duplicate_candidate:
        candidate_ids = (*candidate_ids, "A_copy")
        incidence_rows = (
            *incidence_rows,
            ("A_copy", "history:a0"),
            ("A_copy", "history:a1"),
        )
    return FiniteRealizationRelation(
        relation_id=(
            "may_hollow_triangle_duplicate"
            if duplicate_candidate
            else "may_hollow_triangle"
        ),
        candidate_ids=candidate_ids,
        witness_ids=(
            "history:a0",
            "history:a1",
            "history:a2",
            "history:a3",
        ),
        incidence_rows=incidence_rows,
    )


def may_migration_case() -> dict[str, Any]:
    relation = may_hollow_triangle_relation()
    duplicate_relation = may_hollow_triangle_relation(duplicate_candidate=True)
    omega = relation.may_omega()
    duplicate_omega = duplicate_relation.may_omega()

    pair_fibers = {
        f"{left}{right}": list(
            omega.fiber(omega.quotient_family((left, right))).witness_ids
        )
        for left, right in (("A", "B"), ("A", "C"), ("B", "C"))
    }
    triple = omega.fiber(omega.quotient_family(("A", "B", "C")))
    payload_digest = structural_digest(omega.structural_payload())
    duplicate_digest = structural_digest(duplicate_omega.structural_payload())
    return {
        "relation": relation,
        "omega": omega,
        "duplicate_relation": duplicate_relation,
        "duplicate_omega": duplicate_omega,
        "pair_fibers": pair_fibers,
        "triple_witness_ids": list(triple.witness_ids),
        "raw_candidate_count": len(relation.candidate_ids),
        "duplicate_raw_candidate_count": len(duplicate_relation.candidate_ids),
        "quotient_candidate_count": len(omega.candidate_classes),
        "duplicate_quotient_candidate_count": len(
            duplicate_omega.candidate_classes
        ),
        "maximal_face_count": len(omega.maximal_faces()),
        "greatest_face_exists": omega.greatest_face() is not None,
        "downward_closure_failures": list(
            omega.downward_closure_failures()
        ),
        "restriction_failures": list(omega.restriction_failures()),
        "structural_digest": payload_digest,
        "legacy_structural_digest": LEGACY_MAY_STRUCTURAL_DIGEST,
        "legacy_parity": payload_digest == LEGACY_MAY_STRUCTURAL_DIGEST,
        "duplicate_structural_digest": duplicate_digest,
        "duplicate_invariant": payload_digest == duplicate_digest,
    }


def _environment_sensitivity_fixture() -> dict[str, Any]:
    states = ("start", "ab", "a")
    actions = ("fragile",)
    calm_system = _deterministic_choice_system(
        "fragile_calm",
        states=states,
        actions=actions,
        start_targets={"fragile": "ab"},
    )
    stress_system = _deterministic_choice_system(
        "fragile_stress",
        states=states,
        actions=actions,
        start_targets={"fragile": "a"},
    )
    scenarios = (
        DeterministicEnvironmentScenario("calm", calm_system, "start", 1),
        DeterministicEnvironmentScenario("stress", stress_system, "start", 1),
    )
    policy = _constant_choice_policy(
        calm_system,
        "fragile",
        policy_id="policy_fragile",
    )
    policies = (policy,)
    runs, paths = generate_policy_environment_runs(
        "environment_sensitivity",
        scenarios,
        policies,
    )
    relation = relation_from_terminal_membership(
        "environment_sensitivity",
        runs,
        paths,
        {
            "ab": ("A", "B"),
            "a": ("A",),
        },
    )
    full = FiniteOmega.from_relation(relation, runs)
    calm = FiniteOmega.from_relation(
        relation,
        runs,
        environment_ids=("calm",),
    )
    family = full.may.quotient_family(("A", "B"))
    return {
        "relation": relation,
        "runs": runs,
        "paths": paths,
        "scenarios": scenarios,
        "policies": policies,
        "full": full,
        "calm": calm,
        "family": family,
        "generated_runs_match": audit_generated_runs(
            scenarios,
            policies,
            runs,
            paths,
        ),
        "may_compatible": full.may.fiber(family).nonempty,
        "robust_calm": calm.robust_fiber(family).nonempty,
        "robust_full": full.robust_fiber(family).nonempty,
        "calm_policy_ids": list(calm.robust_fiber(family).policy_ids),
        "full_policy_ids": list(full.robust_fiber(family).policy_ids),
        "environment_antitone_failures": list(
            full.environment_antitone_failures(calm)
        ),
        "candidate_classes_stable": (
            full.may.structural_payload() == calm.may.structural_payload()
        ),
    }


def _hollow_triangle_fixture(
    *,
    include_triple_policy: bool,
    duplicate_candidate: bool = False,
) -> dict[str, Any]:
    states = ("start", "ab", "ac", "bc", "abc")
    actions = ("choose_ab", "choose_ac", "choose_bc", "choose_abc")
    start_targets = {
        "choose_ab": "ab",
        "choose_ac": "ac",
        "choose_bc": "bc",
        "choose_abc": "abc",
    }
    north = _deterministic_choice_system(
        "hollow_north",
        states=states,
        actions=actions,
        start_targets=start_targets,
    )
    south = _deterministic_choice_system(
        "hollow_south",
        states=states,
        actions=actions,
        start_targets=start_targets,
    )
    scenarios = (
        DeterministicEnvironmentScenario("north", north, "start", 1),
        DeterministicEnvironmentScenario("south", south, "start", 1),
    )
    policy_specs = [
        ("policy_ab", "choose_ab"),
        ("policy_ac", "choose_ac"),
        ("policy_bc", "choose_bc"),
    ]
    if include_triple_policy:
        policy_specs.append(("policy_abc", "choose_abc"))
    policies = tuple(
        _constant_choice_policy(north, action, policy_id=policy_id)
        for policy_id, action in policy_specs
    )
    fixture_id = (
        "robust_triangle_positive"
        if include_triple_policy
        else "robust_hollow_triangle"
    )
    runs, paths = generate_policy_environment_runs(
        fixture_id,
        scenarios,
        policies,
    )
    relation = relation_from_terminal_membership(
        fixture_id + ("_duplicate" if duplicate_candidate else ""),
        runs,
        paths,
        {
            "ab": ("A", "B"),
            "ac": ("A", "C"),
            "bc": ("B", "C"),
            "abc": ("A", "B", "C"),
        },
        duplicate_candidate="A" if duplicate_candidate else None,
    )
    omega = FiniteOmega.from_relation(relation, runs)
    pair_fibers = {
        f"{left}{right}": omega.robust_fiber(
            omega.may.quotient_family((left, right))
        )
        for left, right in (("A", "B"), ("A", "C"), ("B", "C"))
    }
    triple = omega.robust_fiber(
        omega.may.quotient_family(("A", "B", "C"))
    )
    return {
        "relation": relation,
        "runs": runs,
        "paths": paths,
        "scenarios": scenarios,
        "policies": policies,
        "omega": omega,
        "pair_fibers": pair_fibers,
        "triple_fiber": triple,
        "generated_runs_match": audit_generated_runs(
            scenarios,
            policies,
            runs,
            paths,
        ),
    }


def robust_hollow_triangle_case() -> dict[str, Any]:
    fixture = _hollow_triangle_fixture(include_triple_policy=False)
    duplicate = _hollow_triangle_fixture(
        include_triple_policy=False,
        duplicate_candidate=True,
    )
    omega = fixture["omega"]
    duplicate_omega = duplicate["omega"]
    pair_policy_ids = {
        pair: list(fiber.policy_ids)
        for pair, fiber in fixture["pair_fibers"].items()
    }
    return {
        **fixture,
        "all_pairs_robust": all(
            fiber.nonempty for fiber in fixture["pair_fibers"].values()
        ),
        "triple_robust": fixture["triple_fiber"].nonempty,
        "pair_policy_ids": pair_policy_ids,
        "triple_policy_ids": list(fixture["triple_fiber"].policy_ids),
        "robust_maximal_face_count": len(omega.robust_maximal_faces()),
        "candidate_antitone_failures": list(
            omega.candidate_antitone_failures()
        ),
        "restriction_failures": list(omega.restriction_failures()),
        "robust_implies_may_failures": [
            list(family) for family in omega.robust_implies_may_failures()
        ],
        "duplicate_raw_candidate_count": len(
            duplicate["relation"].candidate_ids
        ),
        "duplicate_quotient_candidate_count": len(
            duplicate_omega.may.candidate_classes
        ),
        "duplicate_invariant": (
            structural_digest(omega.structural_payload())
            == structural_digest(duplicate_omega.structural_payload())
        ),
    }


def robust_positive_control_case() -> dict[str, Any]:
    fixture = _hollow_triangle_fixture(include_triple_policy=True)
    triple = fixture["triple_fiber"]
    return {
        **fixture,
        "triple_robust": triple.nonempty,
        "triple_policy_ids": list(triple.policy_ids),
        "triple_environment_runs": [
            item.as_dict() for item in triple.securing_witnesses
        ],
    }


def _outcome_contract_controls(
    sensitivity: Mapping[str, Any],
) -> dict[str, bool]:
    try:
        FiniteOmega.from_relation(
            sensitivity["relation"],
            sensitivity["runs"],
            environment_ids=(),
        )
    except ValueError:
        empty_scope_rejected = True
    else:
        empty_scope_rejected = False

    try:
        PolicyEnvironmentRuns(
            table_id="partial_control",
            policy_ids=("p0",),
            environment_ids=("e0", "e1"),
            witness_ids=("w0",),
            outcome_rows=(("p0", "e0", "w0"),),
        )
    except ValueError:
        partial_table_rejected = True
    else:
        partial_table_rejected = False

    try:
        PolicyEnvironmentRuns(
            table_id="multivalued_control",
            policy_ids=("p0",),
            environment_ids=("e0",),
            witness_ids=("w0", "w1"),
            outcome_rows=(
                ("p0", "e0", "w0"),
                ("p0", "e0", "w1"),
            ),
        )
    except ValueError:
        multivalued_table_rejected = True
    else:
        multivalued_table_rejected = False

    return {
        "empty_environment_scope_rejected": empty_scope_rejected,
        "partial_outcome_table_rejected": partial_table_rejected,
        "multivalued_outcome_table_rejected": multivalued_table_rejected,
    }


def robust_omega_summary() -> dict[str, Any]:
    may = may_migration_case()
    sensitivity = _environment_sensitivity_fixture()
    hollow = robust_hollow_triangle_case()
    positive = robust_positive_control_case()
    outcome_controls = _outcome_contract_controls(sensitivity)

    case_results = {
        "legacy_may_parity": (
            may["legacy_parity"]
            and may["pair_fibers"]
            == {
                "AB": ["history:a0"],
                "AC": ["history:a1"],
                "BC": ["history:a2"],
            }
            and may["triple_witness_ids"] == []
            and may["maximal_face_count"] == 3
            and not may["greatest_face_exists"]
        ),
        "may_duplicate_invariance": may["duplicate_invariant"],
        "may_but_not_robust": (
            sensitivity["may_compatible"]
            and not sensitivity["robust_full"]
        ),
        "environment_sensitivity": (
            sensitivity["robust_calm"]
            and not sensitivity["robust_full"]
            and sensitivity["candidate_classes_stable"]
        ),
        "robust_hollow_triangle": (
            hollow["all_pairs_robust"]
            and not hollow["triple_robust"]
            and hollow["robust_maximal_face_count"] == 3
        ),
        "robust_positive_control": positive["triple_robust"],
        "robust_duplicate_invariance": hollow["duplicate_invariant"],
        "generated_run_crosscheck": (
            sensitivity["generated_runs_match"]
            and hollow["generated_runs_match"]
            and positive["generated_runs_match"]
        ),
        "candidate_antitonicity": (
            not hollow["candidate_antitone_failures"]
        ),
        "environment_antitonicity": (
            not sensitivity["environment_antitone_failures"]
        ),
        "robust_implies_may": (
            not hollow["robust_implies_may_failures"]
        ),
        "restriction_laws": (
            not may["restriction_failures"]
            and not hollow["restriction_failures"]
        ),
        **outcome_controls,
    }
    kill_conditions = {
        "legacy_may_parity_failed": not case_results["legacy_may_parity"],
        "empty_environment_scope_admitted": not outcome_controls[
            "empty_environment_scope_rejected"
        ],
        "partial_outcome_table_admitted": not outcome_controls[
            "partial_outcome_table_rejected"
        ],
        "multivalued_outcome_table_admitted": not outcome_controls[
            "multivalued_outcome_table_rejected"
        ],
        "generated_run_table_mismatch": not case_results[
            "generated_run_crosscheck"
        ],
        "candidate_antitonicity_failed": not case_results[
            "candidate_antitonicity"
        ],
        "environment_antitonicity_failed": not case_results[
            "environment_antitonicity"
        ],
        "robust_without_may": not case_results["robust_implies_may"],
        "candidate_duplicate_changed_payload": not (
            case_results["may_duplicate_invariance"]
            and case_results["robust_duplicate_invariance"]
        ),
        "robust_witnesses_discarded": not all(
            fiber.securing_witnesses
            and all(
                {
                    environment_id
                    for environment_id, _witness_id in witness.environment_runs
                }
                == set(hollow["omega"].environment_ids)
                for witness in fiber.securing_witnesses
            )
            for fiber in hollow["pair_fibers"].values()
        ),
        "pair_triple_scope_mismatch": len(
            {
                fiber.environment_ids
                for fiber in (
                    *hollow["pair_fibers"].values(),
                    hollow["triple_fiber"],
                )
            }
        )
        != 1,
    }
    retained = all(case_results.values()) and not any(kill_conditions.values())
    return {
        "status": "retained" if retained else "failed",
        "verdict": (
            "finite_may_and_robust_realization_core_retained"
            if retained
            else "construction_contract_failed"
        ),
        "protocol_doc": PROTOCOL_DOC,
        "semantics": {
            "policy_quantifier": "exists",
            "environment_quantifier": "forall",
            "run_semantics": "one_deterministic_finite_run_per_policy_environment",
            "environment_scope_nonempty": True,
        },
        "may_migration": {
            key: value
            for key, value in may.items()
            if key
            not in {
                "relation",
                "omega",
                "duplicate_relation",
                "duplicate_omega",
            }
        },
        "environment_sensitivity": {
            key: value
            for key, value in sensitivity.items()
            if key
            not in {
                "relation",
                "runs",
                "paths",
                "scenarios",
                "policies",
                "full",
                "calm",
                "family",
            }
        },
        "robust_hollow_triangle": {
            "all_pairs_robust": hollow["all_pairs_robust"],
            "triple_robust": hollow["triple_robust"],
            "pair_policy_ids": hollow["pair_policy_ids"],
            "triple_policy_ids": hollow["triple_policy_ids"],
            "environment_ids": list(hollow["omega"].environment_ids),
            "robust_maximal_face_count": hollow[
                "robust_maximal_face_count"
            ],
            "candidate_antitone_failures": hollow[
                "candidate_antitone_failures"
            ],
            "restriction_failures": hollow["restriction_failures"],
            "robust_implies_may_failures": hollow[
                "robust_implies_may_failures"
            ],
            "duplicate_invariant": hollow["duplicate_invariant"],
            "generated_runs_match": hollow["generated_runs_match"],
        },
        "robust_positive_control": {
            "triple_robust": positive["triple_robust"],
            "triple_policy_ids": positive["triple_policy_ids"],
            "triple_environment_runs": positive[
                "triple_environment_runs"
            ],
            "generated_runs_match": positive["generated_runs_match"],
        },
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "claim_boundary": (
            "Finite deterministic May/Robust realization only; not candidate "
            "correctness, empirical robustness, identity, agency, valuerhood, "
            "standing, value, moral license, universal Omega, or selection of "
            "a maximal face."
        ),
        "_objects": {
            "may": may,
            "sensitivity": sensitivity,
            "hollow": hollow,
            "positive": positive,
        },
    }


def case_result_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    return [
        {"case": case, "passed": passed}
        for case, passed in summary["case_results"].items()
    ]


def candidate_class_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    objects = summary["_objects"]
    cases = {
        "may_hollow_triangle": objects["may"]["omega"],
        "environment_sensitivity": objects["sensitivity"]["full"].may,
        "robust_hollow_triangle": objects["hollow"]["omega"].may,
        "robust_positive_control": objects["positive"]["omega"].may,
    }
    return [
        {
            "case": case,
            "class_id": item.class_id,
            "members": "|".join(item.members),
            "witness_ids": "|".join(item.witness_ids),
        }
        for case, omega in cases.items()
        for item in omega.candidate_classes
    ]


def may_fiber_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    objects = summary["_objects"]
    cases = {
        "may_hollow_triangle": objects["may"]["omega"],
        "environment_sensitivity": objects["sensitivity"]["full"].may,
        "robust_hollow_triangle": objects["hollow"]["omega"].may,
        "robust_positive_control": objects["positive"]["omega"].may,
    }
    return [
        {
            "case": case,
            "family": "|".join(fiber.family),
            "witness_ids": "|".join(fiber.witness_ids),
            "nonempty": fiber.nonempty,
        }
        for case, omega in cases.items()
        for fiber in omega.fibers
    ]


def robust_fiber_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    objects = summary["_objects"]
    cases = {
        "environment_sensitivity_full": objects["sensitivity"]["full"],
        "environment_sensitivity_calm": objects["sensitivity"]["calm"],
        "robust_hollow_triangle": objects["hollow"]["omega"],
        "robust_positive_control": objects["positive"]["omega"],
    }
    return [
        {
            "case": case,
            "environment_ids": "|".join(omega.environment_ids),
            "family": "|".join(fiber.family),
            "policy_ids": "|".join(fiber.policy_ids),
            "run_witnesses": "|".join(
                f"{item.policy_id}:"
                + ",".join(
                    f"{environment_id}={witness_id}"
                    for environment_id, witness_id in item.environment_runs
                )
                for item in fiber.securing_witnesses
            ),
            "nonempty": fiber.nonempty,
        }
        for case, omega in cases.items()
        for fiber in omega.robust_fibers
    ]


def policy_environment_run_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    objects = summary["_objects"]
    cases = {
        "environment_sensitivity": objects["sensitivity"],
        "robust_hollow_triangle": objects["hollow"],
        "robust_positive_control": objects["positive"],
    }
    return [
        {
            "case": case,
            "policy_id": policy_id,
            "environment_id": environment_id,
            "witness_id": witness_id,
            "path_states": "->".join(fixture["paths"][witness_id].states),
            "path_actions": "->".join(fixture["paths"][witness_id].actions),
        }
        for case, fixture in cases.items()
        for policy_id, environment_id, witness_id in fixture[
            "runs"
        ].outcome_rows
    ]


def environment_sensitivity_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    sensitivity = summary["_objects"]["sensitivity"]
    return [
        {
            "scope": scope,
            "environment_ids": "|".join(omega.environment_ids),
            "family": "|".join(sensitivity["family"]),
            "may_compatible": omega.may.fiber(
                sensitivity["family"]
            ).nonempty,
            "robust_compatible": omega.robust_fiber(
                sensitivity["family"]
            ).nonempty,
            "policy_ids": "|".join(
                omega.robust_fiber(sensitivity["family"]).policy_ids
            ),
        }
        for scope, omega in (
            ("calm", sensitivity["calm"]),
            ("full", sensitivity["full"]),
        )
    ]
