"""Generated finite-state-controller witness for strict Robust separation."""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping

from omega_v2.finite.controllers import (
    CLOSED_LOOP_ACTION,
    ClosedLoopState,
    DeterministicControllerRun,
    FiniteStateController,
    compile_closed_loop,
    deterministic_controller_rollout,
)
from omega_v2.finite.model import ControlledMarkovSystem
from omega_v2.finite.realization import (
    FiniteOmega,
    FiniteRealizationRelation,
    PolicyEnvironmentRuns,
    RobustRealizationFiber,
    structural_digest,
)


PROTOCOL_DOC = (
    "docs/research_notes/omega_v2/"
    "generated_controller_robust_separation_protocol_v0.md"
)
ACTIONS = ("x", "y", "z")
MEMORY_STATES = ("m0", "m1")
OBSERVATION = "tick"
CANDIDATES = ("A", "B", "C")
FULL_ENVIRONMENTS = ("north", "south")
NORTH_ENVIRONMENTS = ("north",)
SOUTH_ENVIRONMENTS = ("south",)
HORIZON = 2
START = "start"
AFTER_STATES = tuple(f"after:{action}" for action in ACTIONS)
TERMINAL_FACT_SETS = (
    ("A",),
    ("B",),
    ("C",),
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
    ("A", "B", "C"),
)
TERMINAL_STATES = tuple(
    f"terminal:{''.join(facts)}" for facts in TERMINAL_FACT_SETS
)
WORLD_STATES = (START, *AFTER_STATES, *TERMINAL_STATES)
PAIR_CANDIDATES = (("A", "B"), ("A", "C"), ("B", "C"))


@dataclass(frozen=True)
class ControllerEnvironment:
    """One deterministic environment with the shared controller interface."""

    environment_id: str
    system: ControlledMarkovSystem[str, str]
    initial_state: str = START
    horizon: int = HORIZON

    def __post_init__(self) -> None:
        if not self.environment_id:
            raise ValueError("environment_id must be nonempty")
        self.system.require_state(self.initial_state)
        if self.horizon <= 0:
            raise ValueError("environment horizon must be positive")


def _base_fact(action: str) -> str:
    try:
        return {"x": "A", "y": "B", "z": "C"}[action]
    except KeyError as exc:
        raise KeyError(action) from exc


def _terminal_state(facts: Iterable[str]) -> str:
    retained = tuple(
        candidate for candidate in CANDIDATES if candidate in set(facts)
    )
    state = f"terminal:{''.join(retained)}"
    if state not in TERMINAL_STATES:
        raise ValueError("terminal fact set is not declared")
    return state


def terminal_facts(state: str) -> frozenset[str]:
    """Read candidate facts from a terminal state without fixture metadata."""

    if not state.startswith("terminal:"):
        raise ValueError("candidate membership requires a terminal state")
    payload = state.removeprefix("terminal:")
    facts = frozenset(payload)
    if not facts or not facts <= set(CANDIDATES):
        raise ValueError("terminal state contains an unknown candidate fact")
    return facts


def order_environment(
    system_id: str,
    *,
    bonus_orders: Iterable[tuple[str, str]],
) -> ControlledMarkovSystem[str, str]:
    """Build one total deterministic two-action fact-accumulation system."""

    retained_bonus_orders = frozenset(bonus_orders)
    if not retained_bonus_orders <= {
        (left, right) for left in ACTIONS for right in ACTIONS
    }:
        raise ValueError("bonus order references an unknown action")

    transitions = []
    for state in WORLD_STATES:
        for action in ACTIONS:
            if state == START:
                target = f"after:{action}"
            elif state.startswith("after:"):
                first_action = state.removeprefix("after:")
                facts = {_base_fact(first_action), _base_fact(action)}
                if (first_action, action) in retained_bonus_orders:
                    facts.add("C")
                target = _terminal_state(facts)
            else:
                target = state
            transitions.append((state, action, target, Fraction(1)))

    return ControlledMarkovSystem(
        system_id=system_id,
        states=WORLD_STATES,
        actions=ACTIONS,
        transitions=tuple(transitions),
    )


def strict_environments() -> tuple[ControllerEnvironment, ...]:
    return (
        ControllerEnvironment(
            environment_id="north",
            system=order_environment(
                "generated_order_north",
                bonus_orders=(("x", "y"),),
            ),
        ),
        ControllerEnvironment(
            environment_id="south",
            system=order_environment(
                "generated_order_south",
                bonus_orders=(("y", "x"),),
            ),
        ),
    )


def positive_environments() -> tuple[ControllerEnvironment, ...]:
    return (
        strict_environments()[0],
        ControllerEnvironment(
            environment_id="south",
            system=order_environment(
                "generated_order_south_positive",
                bonus_orders=(("x", "y"), ("y", "x")),
            ),
        ),
    )


def enumerate_bounded_controllers() -> tuple[
    FiniteStateController[str, str, str, str],
    ...,
]:
    """Enumerate the complete declared 2-memory, 1-observation controller class."""

    observation_rows = tuple(
        (state, OBSERVATION) for state in WORLD_STATES
    )
    controllers = []
    for update_targets in itertools.product(MEMORY_STATES, repeat=2):
        for selected_actions in itertools.product(ACTIONS, repeat=2):
            update_code = "".join(
                str(MEMORY_STATES.index(target))
                for target in update_targets
            )
            action_code = "".join(selected_actions)
            controllers.append(
                FiniteStateController(
                    controller_id=f"controller:u{update_code}:a{action_code}",
                    memory_states=MEMORY_STATES,
                    initial_memory="m0",
                    observation_rows=observation_rows,
                    update_rows=tuple(
                        (
                            memory,
                            OBSERVATION,
                            target,
                        )
                        for memory, target in zip(
                            MEMORY_STATES,
                            update_targets,
                            strict=True,
                        )
                    ),
                    policy_rows=tuple(
                        (
                            memory,
                            OBSERVATION,
                            action,
                        )
                        for memory, action in zip(
                            MEMORY_STATES,
                            selected_actions,
                            strict=True,
                        )
                    ),
                )
            )
    return tuple(controllers)


def controller_action_sequence(
    controller: FiniteStateController[str, str, str, str],
) -> tuple[str, str]:
    """Return the two actions generated under the fixed observation stream."""

    memory = controller.initial_memory
    first = controller.action(memory, OBSERVATION)
    memory = controller.update(memory, OBSERVATION)
    second = controller.action(memory, OBSERVATION)
    return first, second


def behavior_classes(
    controllers: Iterable[
        FiniteStateController[str, str, str, str]
    ],
) -> dict[tuple[str, str], tuple[str, ...]]:
    grouped: dict[tuple[str, str], list[str]] = {}
    for controller in controllers:
        grouped.setdefault(
            controller_action_sequence(controller),
            [],
        ).append(controller.controller_id)
    return {
        sequence: tuple(sorted(controller_ids))
        for sequence, controller_ids in sorted(grouped.items())
    }


def behavior_representatives(
    controllers: Iterable[
        FiniteStateController[str, str, str, str]
    ],
) -> tuple[FiniteStateController[str, str, str, str], ...]:
    controller_map = {
        controller.controller_id: controller for controller in controllers
    }
    return tuple(
        controller_map[controller_ids[0]]
        for controller_ids in behavior_classes(controllers).values()
    )


def _run_matches_compiled_closed_loop(
    environment: ControllerEnvironment,
    controller: FiniteStateController[str, str, str, str],
    run: DeterministicControllerRun[str, str, str, str],
) -> bool:
    compiled = compile_closed_loop(environment.system, controller)
    for index in range(run.world_path.horizon):
        source = ClosedLoopState(
            run.world_path.states[index],
            run.memory_states[index],
        )
        target = ClosedLoopState(
            run.world_path.states[index + 1],
            run.memory_states[index + 1],
        )
        distribution = compiled.system.distribution(
            source,
            CLOSED_LOOP_ACTION,
        )
        if distribution.rows != ((target, Fraction(1)),):
            return False
    return True


def generate_controller_environment_runs(
    fixture_id: str,
    environments: Iterable[ControllerEnvironment],
    controllers: Iterable[
        FiniteStateController[str, str, str, str]
    ],
) -> tuple[
    PolicyEnvironmentRuns,
    dict[str, DeterministicControllerRun[str, str, str, str]],
]:
    """Generate and retain every controller/environment trajectory."""

    retained_environments = tuple(environments)
    retained_controllers = tuple(controllers)
    if not fixture_id:
        raise ValueError("fixture_id must be nonempty")
    if not retained_environments:
        raise ValueError("at least one environment is required")
    if not retained_controllers:
        raise ValueError("at least one controller is required")

    first_environment = retained_environments[0]
    if any(
        environment.system.states != first_environment.system.states
        or environment.system.actions != first_environment.system.actions
        or environment.horizon != first_environment.horizon
        for environment in retained_environments[1:]
    ):
        raise ValueError(
            "environments must share state, action, and horizon interfaces"
        )

    trajectories = {}
    outcome_rows = []
    for controller in retained_controllers:
        for environment in retained_environments:
            witness_id = (
                f"run:{fixture_id}:{controller.controller_id}:"
                f"{environment.environment_id}"
            )
            trajectories[witness_id] = deterministic_controller_rollout(
                environment.system,
                controller,
                initial_state=environment.initial_state,
                horizon=environment.horizon,
            )
            outcome_rows.append(
                (
                    controller.controller_id,
                    environment.environment_id,
                    witness_id,
                )
            )

    runs = PolicyEnvironmentRuns(
        table_id=f"runs:{fixture_id}",
        policy_ids=tuple(
            controller.controller_id for controller in retained_controllers
        ),
        environment_ids=tuple(
            environment.environment_id
            for environment in retained_environments
        ),
        witness_ids=tuple(trajectories),
        outcome_rows=tuple(outcome_rows),
    )
    return runs, trajectories


def relation_from_generated_trajectories(
    relation_id: str,
    runs: PolicyEnvironmentRuns,
    trajectories: Mapping[
        str,
        DeterministicControllerRun[str, str, str, str],
    ],
) -> FiniteRealizationRelation:
    """Derive candidate incidence solely from terminal trajectory facts."""

    if set(trajectories) != set(runs.witness_ids):
        raise ValueError("trajectory map must cover the run witness universe")
    incidence_rows = tuple(
        (candidate, witness_id)
        for witness_id in runs.witness_ids
        for candidate in CANDIDATES
        if candidate in terminal_facts(
            trajectories[witness_id].world_path.end
        )
    )
    return FiniteRealizationRelation(
        relation_id=relation_id,
        candidate_ids=CANDIDATES,
        witness_ids=runs.witness_ids,
        incidence_rows=incidence_rows,
    )


def audit_generated_runs(
    environments: Iterable[ControllerEnvironment],
    controllers: Iterable[
        FiniteStateController[str, str, str, str]
    ],
    runs: PolicyEnvironmentRuns,
    trajectories: Mapping[
        str,
        DeterministicControllerRun[str, str, str, str],
    ],
) -> tuple[bool, bool]:
    environment_map = {
        environment.environment_id: environment
        for environment in environments
    }
    controller_map = {
        controller.controller_id: controller for controller in controllers
    }
    fresh_match = True
    compiled_match = True
    for controller_id, environment_id, witness_id in runs.outcome_rows:
        environment = environment_map[environment_id]
        controller = controller_map[controller_id]
        retained = trajectories[witness_id]
        fresh = deterministic_controller_rollout(
            environment.system,
            controller,
            initial_state=environment.initial_state,
            horizon=environment.horizon,
        )
        fresh_match = fresh_match and retained == fresh
        compiled_match = compiled_match and _run_matches_compiled_closed_loop(
            environment,
            controller,
            retained,
        )
    return fresh_match, compiled_match


def _family(
    omega: FiniteOmega,
    candidates: Iterable[str],
) -> tuple[str, ...]:
    return omega.may.quotient_family(candidates)


def _pair_fibers(
    omega: FiniteOmega,
) -> dict[str, RobustRealizationFiber]:
    return {
        "".join(pair): omega.robust_fiber(_family(omega, pair))
        for pair in PAIR_CANDIDATES
    }


def _complete_run_evidence(omega: FiniteOmega) -> bool:
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


def _securing_sequences(
    fiber: RobustRealizationFiber,
    controllers: Mapping[
        str,
        FiniteStateController[str, str, str, str],
    ],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                "".join(controller_action_sequence(
                    controllers[policy_id]
                ))
                for policy_id in fiber.policy_ids
            }
        )
    )


def _raw_support(
    omega: FiniteOmega,
    *,
    robust: bool,
) -> dict[str, bool]:
    support = {}
    for size in range(len(CANDIDATES) + 1):
        for family in itertools.combinations(CANDIDATES, size):
            quotient_family = _family(omega, family)
            fiber = (
                omega.robust_fiber(quotient_family)
                if robust
                else omega.may.fiber(quotient_family)
            )
            support["".join(family) or "empty"] = fiber.nonempty
    return support


def _build_case(
    fixture_id: str,
    environments: tuple[ControllerEnvironment, ...],
    controllers: tuple[
        FiniteStateController[str, str, str, str],
        ...,
    ],
) -> dict[str, Any]:
    runs, trajectories = generate_controller_environment_runs(
        fixture_id,
        environments,
        controllers,
    )
    relation = relation_from_generated_trajectories(
        f"relation:{fixture_id}",
        runs,
        trajectories,
    )
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
    south = FiniteOmega.from_relation(
        relation,
        runs,
        environment_ids=SOUTH_ENVIRONMENTS,
    )
    return {
        "environments": environments,
        "controllers": controllers,
        "controller_map": {
            controller.controller_id: controller
            for controller in controllers
        },
        "runs": runs,
        "trajectories": trajectories,
        "relation": relation,
        "full": full,
        "north": north,
        "south": south,
    }


def strict_generated_case() -> dict[str, Any]:
    controllers = enumerate_bounded_controllers()
    fixture = _build_case(
        "generated_controller_strict",
        strict_environments(),
        controllers,
    )
    representatives = behavior_representatives(controllers)
    representative_fixture = _build_case(
        "generated_controller_strict_representatives",
        strict_environments(),
        representatives,
    )
    full = fixture["full"]
    north = fixture["north"]
    south = fixture["south"]
    triple = _family(full, CANDIDATES)
    pair_fibers = _pair_fibers(full)
    controller_map = fixture["controller_map"]
    fresh_match, compiled_match = audit_generated_runs(
        fixture["environments"],
        controllers,
        fixture["runs"],
        fixture["trajectories"],
    )
    return {
        **fixture,
        "representative_fixture": representative_fixture,
        "representatives": representatives,
        "triple_family": triple,
        "pair_fibers": pair_fibers,
        "full_triple_fiber": full.robust_fiber(triple),
        "north_triple_fiber": north.robust_fiber(triple),
        "south_triple_fiber": south.robust_fiber(triple),
        "may_triple_fiber": full.may.fiber(triple),
        "may_triple_witness_count": len(
            full.may.fiber(triple).witness_ids
        ),
        "controller_count": len(controllers),
        "behavior_class_count": len(behavior_classes(controllers)),
        "pair_sequences": {
            pair: list(_securing_sequences(fiber, controller_map))
            for pair, fiber in pair_fibers.items()
        },
        "full_triple_sequences": list(
            _securing_sequences(
                full.robust_fiber(triple),
                controller_map,
            )
        ),
        "north_triple_sequences": list(
            _securing_sequences(
                north.robust_fiber(triple),
                controller_map,
            )
        ),
        "south_triple_sequences": list(
            _securing_sequences(
                south.robust_fiber(triple),
                controller_map,
            )
        ),
        "fresh_rollout_match": fresh_match,
        "compiled_rollout_match": compiled_match,
        "same_action_sequence_across_environments": all(
            fixture["trajectories"][
                fixture["runs"].witness_for(
                    controller.controller_id,
                    "north",
                )
            ].action_sequence
            == fixture["trajectories"][
                fixture["runs"].witness_for(
                    controller.controller_id,
                    "south",
                )
            ].action_sequence
            for controller in controllers
        ),
        "shared_observation_stream": all(
            run.observations == (OBSERVATION,) * HORIZON
            for run in fixture["trajectories"].values()
        ),
        "candidate_membership_extensional": all(
            terminal_facts(left.world_path.end)
            == terminal_facts(right.world_path.end)
            for left in fixture["trajectories"].values()
            for right in fixture["trajectories"].values()
            if left.world_path.end == right.world_path.end
        ),
        "may_support": _raw_support(full, robust=False),
        "robust_support": _raw_support(full, robust=True),
        "north_robust_support": _raw_support(north, robust=True),
        "south_robust_support": _raw_support(south, robust=True),
        "behavior_reduction_may_invariant": (
            _raw_support(full, robust=False)
            == _raw_support(
                representative_fixture["full"],
                robust=False,
            )
        ),
        "behavior_reduction_robust_invariant": (
            _raw_support(full, robust=True)
            == _raw_support(
                representative_fixture["full"],
                robust=True,
            )
        ),
        "behavior_reduction_north_robust_invariant": (
            _raw_support(north, robust=True)
            == _raw_support(
                representative_fixture["north"],
                robust=True,
            )
        ),
        "behavior_reduction_south_robust_invariant": (
            _raw_support(south, robust=True)
            == _raw_support(
                representative_fixture["south"],
                robust=True,
            )
        ),
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
        "north_environment_antitone_failures": list(
            full.environment_antitone_failures(north)
        ),
        "south_environment_antitone_failures": list(
            full.environment_antitone_failures(south)
        ),
        "complete_run_evidence": (
            _complete_run_evidence(full)
            and _complete_run_evidence(north)
            and _complete_run_evidence(south)
        ),
        "pair_triple_scope_match": (
            {
                fiber.environment_ids
                for fiber in (*pair_fibers.values(), full.robust_fiber(triple))
            }
            == {FULL_ENVIRONMENTS}
        ),
    }


def positive_generated_case() -> dict[str, Any]:
    controllers = enumerate_bounded_controllers()
    fixture = _build_case(
        "generated_controller_positive",
        positive_environments(),
        controllers,
    )
    representative_fixture = _build_case(
        "generated_controller_positive_representatives",
        positive_environments(),
        behavior_representatives(controllers),
    )
    full = fixture["full"]
    triple = _family(full, CANDIDATES)
    triple_fiber = full.robust_fiber(triple)
    fresh_match, compiled_match = audit_generated_runs(
        fixture["environments"],
        controllers,
        fixture["runs"],
        fixture["trajectories"],
    )
    return {
        **fixture,
        "triple_family": triple,
        "triple_fiber": triple_fiber,
        "representative_fixture": representative_fixture,
        "triple_sequences": list(
            _securing_sequences(
                triple_fiber,
                fixture["controller_map"],
            )
        ),
        "may_support": _raw_support(full, robust=False),
        "robust_support": _raw_support(full, robust=True),
        "fresh_rollout_match": fresh_match,
        "compiled_rollout_match": compiled_match,
        "complete_run_evidence": _complete_run_evidence(full),
        "behavior_reduction_may_invariant": (
            _raw_support(full, robust=False)
            == _raw_support(
                representative_fixture["full"],
                robust=False,
            )
        ),
        "behavior_reduction_robust_invariant": (
            _raw_support(full, robust=True)
            == _raw_support(
                representative_fixture["full"],
                robust=True,
            )
        ),
    }


def _strict_public(case: Mapping[str, Any]) -> dict[str, object]:
    excluded = {
        "environments",
        "controllers",
        "controller_map",
        "runs",
        "trajectories",
        "relation",
        "full",
        "north",
        "south",
        "representative_fixture",
        "representatives",
        "triple_family",
        "pair_fibers",
        "full_triple_fiber",
        "north_triple_fiber",
        "south_triple_fiber",
        "may_triple_fiber",
    }
    return {
        key: value for key, value in case.items() if key not in excluded
    }


def _positive_public(case: Mapping[str, Any]) -> dict[str, object]:
    excluded = {
        "environments",
        "controllers",
        "controller_map",
        "runs",
        "trajectories",
        "relation",
        "full",
        "north",
        "south",
        "triple_family",
        "triple_fiber",
        "representative_fixture",
    }
    return {
        key: value for key, value in case.items() if key not in excluded
    }


def generated_controller_robust_separation_summary() -> dict[str, Any]:
    strict = strict_generated_case()
    positive = positive_generated_case()
    strict_full_triple = strict["full_triple_fiber"]
    strict_north_triple = strict["north_triple_fiber"]
    strict_south_triple = strict["south_triple_fiber"]
    positive_triple = positive["triple_fiber"]
    expected_pair_sequences = {
        "AB": ["xy", "yx"],
        "AC": ["xz", "zx"],
        "BC": ["yz", "zy"],
    }
    strict_positive_may_support_match = (
        strict["may_support"] == positive["may_support"]
    )
    controller_enumeration_complete = (
        strict["controller_count"] == 36
        and len(
            {
                (
                    controller.update_rows,
                    controller.policy_rows,
                )
                for controller in strict["controllers"]
            }
        )
        == 36
    )
    structural_laws_pass = not any(
        (
            strict["may_downward_closure_failures"],
            strict["may_restriction_failures"],
            strict["candidate_antitone_failures"],
            strict["robust_restriction_failures"],
            strict["robust_implies_may_failures"],
            strict["north_environment_antitone_failures"],
            strict["south_environment_antitone_failures"],
        )
    )
    case_results = {
        "controller_enumeration_complete": controller_enumeration_complete,
        "behavior_classes_complete": strict["behavior_class_count"] == 9,
        "generated_runs_match_fresh_rollout": (
            strict["fresh_rollout_match"]
            and positive["fresh_rollout_match"]
        ),
        "generated_runs_match_compiled_closed_loop": (
            strict["compiled_rollout_match"]
            and positive["compiled_rollout_match"]
        ),
        "strict_observation_stream_shared": (
            strict["shared_observation_stream"]
        ),
        "strict_action_sequence_shared": (
            strict["same_action_sequence_across_environments"]
        ),
        "candidate_membership_trajectory_extensional": (
            strict["candidate_membership_extensional"]
        ),
        "strict_may_triple_nonempty": (
            strict["may_triple_fiber"].nonempty
        ),
        "strict_each_environment_triple": (
            strict_north_triple.nonempty
            and strict_south_triple.nonempty
        ),
        "strict_pairwise_robust": all(
            fiber.nonempty for fiber in strict["pair_fibers"].values()
        ),
        "strict_pair_sequences_match": (
            strict["pair_sequences"] == expected_pair_sequences
        ),
        "strict_full_triple_not_robust": (
            not strict_full_triple.nonempty
        ),
        "strict_singleton_scopes_restore_triple": (
            strict["north_triple_sequences"] == ["xy"]
            and strict["south_triple_sequences"] == ["yx"]
        ),
        "strict_pair_triple_scope_match": (
            strict["pair_triple_scope_match"]
        ),
        "positive_full_triple_robust": (
            positive_triple.nonempty
            and positive["triple_sequences"] == ["xy"]
        ),
        "strict_positive_may_support_match": (
            strict_positive_may_support_match
        ),
        "behavior_reduction_preserves_verdicts": (
            strict["behavior_reduction_may_invariant"]
            and strict["behavior_reduction_robust_invariant"]
            and strict["behavior_reduction_north_robust_invariant"]
            and strict["behavior_reduction_south_robust_invariant"]
            and positive["behavior_reduction_may_invariant"]
            and positive["behavior_reduction_robust_invariant"]
        ),
        "structural_laws_pass": structural_laws_pass,
        "complete_run_evidence": (
            strict["complete_run_evidence"]
            and positive["complete_run_evidence"]
        ),
    }
    kill_conditions = {
        "controller_enumeration_partial": (
            not case_results["controller_enumeration_complete"]
        ),
        "controller_count_mismatch": strict["controller_count"] != 36,
        "behavior_class_count_mismatch": (
            strict["behavior_class_count"] != 9
        ),
        "generated_run_table_mismatch": (
            not case_results["generated_runs_match_fresh_rollout"]
        ),
        "closed_loop_compilation_mismatch": (
            not case_results["generated_runs_match_compiled_closed_loop"]
        ),
        "observation_stream_differs": (
            not case_results["strict_observation_stream_shared"]
        ),
        "action_sequence_differs_across_environments": (
            not case_results["strict_action_sequence_shared"]
        ),
        "candidate_membership_not_trajectory_extensional": (
            not case_results["candidate_membership_trajectory_extensional"]
        ),
        "strict_environment_triple_missing": (
            not case_results["strict_each_environment_triple"]
        ),
        "strict_pair_not_robust": (
            not case_results["strict_pairwise_robust"]
        ),
        "strict_full_triple_robust": strict_full_triple.nonempty,
        "strict_singleton_scope_failed": (
            not case_results["strict_singleton_scopes_restore_triple"]
        ),
        "positive_control_failed": (
            not case_results["positive_full_triple_robust"]
        ),
        "behavior_reduction_changed_verdict": (
            not case_results["behavior_reduction_preserves_verdicts"]
        ),
        "pair_triple_scope_mismatch": (
            not case_results["strict_pair_triple_scope_match"]
        ),
        "structural_law_failed": (
            not case_results["structural_laws_pass"]
        ),
        "run_evidence_discarded": (
            not case_results["complete_run_evidence"]
        ),
    }
    status = (
        "retained"
        if all(case_results.values()) and not any(kill_conditions.values())
        else "failed"
    )
    summary = {
        "status": status,
        "verdict": (
            "generated_controller_joint_realizability_does_not_imply_"
            "joint_robust_securability"
            if status == "retained"
            else "generated_controller_separation_not_retained"
        ),
        "protocol_doc": PROTOCOL_DOC,
        "semantics": {
            "controller_quantifier": "exists",
            "environment_quantifier": "forall",
            "controller_class": (
                "all total deterministic controllers over two memory states, "
                "one observation, and three actions"
            ),
            "candidate_semantics": "terminal trajectory fact membership",
            "horizon": HORIZON,
        },
        "strict": _strict_public(strict),
        "positive": _positive_public(positive),
        "strict_positive_may_support_match": (
            strict_positive_may_support_match
        ),
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "claim_boundary": (
            "Finite exact separation under a completely enumerated bounded "
            "deterministic controller class. Not a claim about the correct "
            "controller, environment, or candidate classes; partial "
            "observation in general; stochastic or empirical robustness; "
            "identity; agency; valuerhood; standing; value; moral "
            "compatibility; or universal Omega."
        ),
        "_objects": {
            "strict": strict,
            "positive": positive,
        },
    }
    return summary


def controller_rows(summary: Mapping[str, Any]) -> list[dict[str, object]]:
    strict = summary["_objects"]["strict"]
    classes = behavior_classes(strict["controllers"])
    class_id_by_controller = {
        controller_id: "".join(sequence)
        for sequence, controller_ids in classes.items()
        for controller_id in controller_ids
    }
    return [
        {
            "controller_id": controller.controller_id,
            "initial_memory": controller.initial_memory,
            "update_m0": controller.update("m0", OBSERVATION),
            "update_m1": controller.update("m1", OBSERVATION),
            "action_m0": controller.action("m0", OBSERVATION),
            "action_m1": controller.action("m1", OBSERVATION),
            "generated_sequence": "".join(
                controller_action_sequence(controller)
            ),
            "behavior_class": class_id_by_controller[
                controller.controller_id
            ],
        }
        for controller in strict["controllers"]
    ]


def behavior_class_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    strict = summary["_objects"]["strict"]
    return [
        {
            "action_sequence": "".join(sequence),
            "controller_count": len(controller_ids),
            "representative_controller_id": controller_ids[0],
            "controller_ids": "|".join(controller_ids),
        }
        for sequence, controller_ids in behavior_classes(
            strict["controllers"]
        ).items()
    ]


def generated_run_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    rows = []
    for case_name in ("strict", "positive"):
        case = summary["_objects"][case_name]
        for controller_id, environment_id, witness_id in (
            case["runs"].outcome_rows
        ):
            run = case["trajectories"][witness_id]
            rows.append(
                {
                    "case": case_name,
                    "controller_id": controller_id,
                    "environment_id": environment_id,
                    "witness_id": witness_id,
                    "actions": "".join(run.action_sequence),
                    "world_states": "|".join(run.world_path.states),
                    "observations": "|".join(run.observations),
                    "memory_states": "|".join(run.memory_states),
                    "terminal_facts": "".join(
                        sorted(terminal_facts(run.world_path.end))
                    ),
                }
            )
    return rows


def may_fiber_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    rows = []
    for case_name in ("strict", "positive"):
        omega = summary["_objects"][case_name]["full"]
        for size in range(len(CANDIDATES) + 1):
            for family in itertools.combinations(CANDIDATES, size):
                fiber = omega.may.fiber(_family(omega, family))
                rows.append(
                    {
                        "case": case_name,
                        "family": "".join(family),
                        "nonempty": fiber.nonempty,
                        "witness_count": len(fiber.witness_ids),
                        "witness_ids": "|".join(fiber.witness_ids),
                    }
                )
    return rows


def robust_fiber_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    rows = []
    scopes = (
        ("strict_full", summary["_objects"]["strict"]["full"]),
        ("strict_north", summary["_objects"]["strict"]["north"]),
        ("strict_south", summary["_objects"]["strict"]["south"]),
        ("positive_full", summary["_objects"]["positive"]["full"]),
    )
    for scope_name, omega in scopes:
        for size in range(len(CANDIDATES) + 1):
            for family in itertools.combinations(CANDIDATES, size):
                fiber = omega.robust_fiber(_family(omega, family))
                rows.append(
                    {
                        "scope": scope_name,
                        "environment_ids": "|".join(
                            fiber.environment_ids
                        ),
                        "family": "".join(family),
                        "nonempty": fiber.nonempty,
                        "policy_count": len(fiber.policy_ids),
                        "policy_ids": "|".join(fiber.policy_ids),
                    }
                )
    return rows


def environment_scope_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    strict = summary["_objects"]["strict"]
    positive = summary["_objects"]["positive"]
    return [
        {
            "scope": "strict_north",
            "environment_ids": "north",
            "triple_robust": strict["north_triple_fiber"].nonempty,
            "triple_sequences": "|".join(
                strict["north_triple_sequences"]
            ),
        },
        {
            "scope": "strict_south",
            "environment_ids": "south",
            "triple_robust": strict["south_triple_fiber"].nonempty,
            "triple_sequences": "|".join(
                strict["south_triple_sequences"]
            ),
        },
        {
            "scope": "strict_full",
            "environment_ids": "north|south",
            "triple_robust": strict["full_triple_fiber"].nonempty,
            "triple_sequences": "|".join(
                strict["full_triple_sequences"]
            ),
        },
        {
            "scope": "positive_full",
            "environment_ids": "north|south",
            "triple_robust": positive["triple_fiber"].nonempty,
            "triple_sequences": "|".join(
                positive["triple_sequences"]
            ),
        },
    ]


def structural_control_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    return [
        {"control": name, "passed": passed}
        for name, passed in summary["case_results"].items()
    ]


def summary_digest(summary: Mapping[str, Any]) -> str:
    public = {
        key: value for key, value in summary.items() if key != "_objects"
    }
    return structural_digest(json.loads(json.dumps(public, sort_keys=True)))
