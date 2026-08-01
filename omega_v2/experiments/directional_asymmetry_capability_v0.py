"""Finite tests of directional asymmetry against operational capability features."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from typing import Any, Iterable

from omega_v2.finite.controllers import (
    CLOSED_LOOP_ACTION,
    ClosedLoopState,
    FiniteStateController,
    audit_operational_features,
    closed_loop_initial_distribution,
    compile_closed_loop,
)
from omega_v2.finite.model import (
    ControlledMarkovSystem,
    DeterministicPolicy,
    FiniteDistribution,
    FinitePath,
    fraction_text,
)
from omega_v2.finite.path_laws import (
    ActionInvolution,
    compare_laws,
    event_probability,
    finite_path_law,
    pull_back_reversed_path_law,
    total_variation_distance,
)


PROTOCOL_DOC = (
    "docs/research_notes/omega_v2/"
    "directional_asymmetry_capability_protocol_v0.md"
)

WorldState = tuple[str, int]


def _uniform_distribution(outcomes: Iterable[Any]) -> FiniteDistribution[Any]:
    values = tuple(outcomes)
    if not values:
        raise ValueError("uniform distribution requires nonempty support")
    mass = Fraction(1, len(values))
    return FiniteDistribution(rows=tuple((value, mass) for value in values))


def _constant_policy(
    system: ControlledMarkovSystem[Any, str],
    action: str,
    *,
    policy_id: str,
) -> DeterministicPolicy[Any, str]:
    return DeterministicPolicy(
        policy_id=policy_id,
        rows=tuple((state, action) for state in system.states),
    )


def _self_reversal_summary(
    system: ControlledMarkovSystem[Any, str],
    policy: DeterministicPolicy[Any, str],
    initial: FiniteDistribution[Any],
    involution: ActionInvolution[str],
    *,
    horizon: int,
) -> dict[str, object]:
    forward = finite_path_law(system, policy, initial, horizon=horizon)
    reversed_on_forward_coordinates = pull_back_reversed_path_law(
        forward,
        involution,
    )
    return {
        "comparison": compare_laws(
            forward,
            reversed_on_forward_coordinates,
        ).as_dict(),
        "forward_path_count": len(forward.support),
        "reverse_path_count": len(reversed_on_forward_coordinates.support),
    }


def passive_biased_cycle_fixture() -> tuple[
    ControlledMarkovSystem[str, str],
    FiniteStateController[str, str, str, str],
    FiniteDistribution[str],
]:
    """A reciprocal-support biased cycle with no available action choice."""

    states = ("p0", "p1", "p2")
    transitions: list[tuple[str, str, str, Fraction]] = []
    for index, state in enumerate(states):
        transitions.extend(
            (
                (state, "advance", states[(index + 1) % 3], Fraction(3, 4)),
                (state, "advance", states[(index - 1) % 3], Fraction(1, 4)),
            )
        )
    system = ControlledMarkovSystem(
        system_id="passive_biased_cycle",
        states=states,
        actions=("advance",),
        transitions=tuple(transitions),
    )
    controller = FiniteStateController(
        controller_id="passive_singleton",
        memory_states=("m",),
        initial_memory="m",
        observation_rows=tuple((state, "present") for state in states),
        update_rows=(("m", "present", "m"),),
        policy_rows=(("m", "present", "advance"),),
    )
    return system, controller, _uniform_distribution(states)


def passive_asymmetry_case(*, horizon: int) -> dict[str, object]:
    system, controller, initial = passive_biased_cycle_fixture()
    policy = _constant_policy(
        system,
        "advance",
        policy_id="passive_advance",
    )
    directionality = _self_reversal_summary(
        system,
        policy,
        initial,
        ActionInvolution(rows=(("advance", "advance"),)),
        horizon=horizon,
    )
    features = audit_operational_features(system, controller, initial)
    return {
        "system_id": system.system_id,
        "horizon": horizon,
        "directionality": directionality,
        "features": features.as_dict(),
    }


def _permutation_inverse(
    permutation: tuple[int, ...],
) -> tuple[int, ...]:
    inverse = [0] * len(permutation)
    for source, target in enumerate(permutation):
        inverse[target] = source
    return tuple(inverse)


def _flatten_transition_rows(
    rows: Iterable[
        tuple[
            tuple[int, str, int, Fraction],
            tuple[int, str, int, Fraction],
        ]
    ],
) -> tuple[tuple[int, str, int, Fraction], ...]:
    return tuple(row for pair in rows for row in pair)


def _permutation_system(
    permutation: tuple[int, ...],
) -> ControlledMarkovSystem[int, str]:
    inverse = _permutation_inverse(permutation)
    states = tuple(range(len(permutation)))
    transitions = _flatten_transition_rows(
        (
            (state, "forward", permutation[state], Fraction(1)),
            (state, "reverse", inverse[state], Fraction(1)),
        )
        for state in states
    )
    return ControlledMarkovSystem(
        system_id="permutation_" + "".join(str(target) for target in permutation),
        states=states,
        actions=("forward", "reverse"),
        transitions=transitions,
    )


def _reversal_contract_holds(
    system: ControlledMarkovSystem[int, str],
) -> bool:
    return all(
        system.distribution(source, "forward").probability(target)
        == system.distribution(target, "reverse").probability(source)
        for source in system.states
        for target in system.states
    )


def reversible_action_census(*, horizon: int) -> dict[str, object]:
    """Exhaust the three-state inverse-permutation action class and its policies."""

    states = (0, 1, 2)
    initial = _uniform_distribution(states)
    involution = ActionInvolution(
        rows=(("forward", "reverse"), ("reverse", "forward"))
    )
    rows: list[dict[str, object]] = []
    permutation_summaries: list[dict[str, object]] = []

    for permutation in itertools.permutations(states):
        system = _permutation_system(permutation)
        inverse = _permutation_inverse(permutation)
        forward_policy = _constant_policy(
            system,
            "forward",
            policy_id=f"{system.system_id}__forward",
        )
        reverse_policy = _constant_policy(
            system,
            "reverse",
            policy_id=f"{system.system_id}__reverse",
        )
        forward_law = finite_path_law(
            system,
            forward_policy,
            initial,
            horizon=horizon,
        )
        reverse_law = finite_path_law(
            system,
            reverse_policy,
            initial,
            horizon=horizon,
        )
        reversed_on_forward_coordinates = pull_back_reversed_path_law(
            reverse_law,
            involution,
        )
        reverse_pair_tv = total_variation_distance(
            forward_law,
            reversed_on_forward_coordinates,
        )
        action_targets_are_bijective = (
            len(set(permutation)) == len(states)
            and len(set(inverse)) == len(states)
        )
        reversal_contract = _reversal_contract_holds(system)

        permutation_summaries.append(
            {
                "permutation_id": system.system_id,
                "permutation": list(permutation),
                "inverse": list(inverse),
                "action_targets_are_bijective": action_targets_are_bijective,
                "reversal_contract_holds": reversal_contract,
                "reverse_pair_total_variation": fraction_text(reverse_pair_tv),
            }
        )

        for assignment in itertools.product(system.actions, repeat=len(states)):
            action_map = dict(zip(states, assignment, strict=True))
            targets = tuple(
                system.distribution(state, action_map[state]).support[0]
                for state in states
            )
            actions_have_distinct_effects = any(
                system.distribution(state, "forward")
                != system.distribution(state, "reverse")
                for state in states
            )
            uses_both_actions = len(set(assignment)) == 2
            image_size = len(set(targets))
            rows.append(
                {
                    "permutation_id": system.system_id,
                    "permutation": "".join(str(target) for target in permutation),
                    "policy": "|".join(assignment),
                    "uses_both_actions": uses_both_actions,
                    "actions_have_distinct_effects": actions_have_distinct_effects,
                    "primitive_actions_bijective": action_targets_are_bijective,
                    "reversal_contract_holds": reversal_contract,
                    "reverse_pair_total_variation": fraction_text(reverse_pair_tv),
                    "closed_loop_targets": "|".join(str(target) for target in targets),
                    "closed_loop_image_size": image_size,
                    "closed_loop_injective": image_size == len(states),
                    "qualifying_noninvertible_selector": (
                        uses_both_actions
                        and actions_have_distinct_effects
                        and image_size < len(states)
                    ),
                }
            )

    canonical_rows = json.dumps(
        rows,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    witnesses = tuple(
        row for row in rows if row["qualifying_noninvertible_selector"]
    )
    return {
        "state_count": len(states),
        "permutation_count": len(permutation_summaries),
        "policy_count": len(rows),
        "expected_permutation_count": 6,
        "expected_policy_count": 48,
        "manifest_digest": hashlib.sha256(canonical_rows).hexdigest(),
        "all_primitive_actions_bijective": all(
            bool(row["action_targets_are_bijective"])
            for row in permutation_summaries
        ),
        "all_reversal_contracts_hold": all(
            bool(row["reversal_contract_holds"])
            for row in permutation_summaries
        ),
        "all_reverse_pair_distances_zero": all(
            row["reverse_pair_total_variation"] == "0"
            for row in permutation_summaries
        ),
        "qualifying_witness_count": len(witnesses),
        "first_qualifying_witness": witnesses[0] if witnesses else None,
        "permutations": permutation_summaries,
        "rows": rows,
    }


def _world_target(world: str, action: str) -> str:
    if action == "swap_a":
        return {"A": "H", "H": "A", "B": "B"}[world]
    if action == "swap_b":
        return {"B": "H", "H": "B", "A": "A"}[world]
    if action == "hold":
        return world
    raise KeyError(action)


def record_selector_world(
    *,
    clockwise_probability: Fraction,
) -> ControlledMarkovSystem[WorldState, str]:
    """Product of self-inverse world actions and an independent phase cycle."""

    if not 0 < clockwise_probability < 1:
        raise ValueError("phase probability must be strictly between zero and one")
    worlds = ("A", "B", "H")
    phases = (0, 1, 2)
    states = tuple((world, phase) for world in worlds for phase in phases)
    actions = ("swap_a", "swap_b", "hold")
    counterclockwise_probability = 1 - clockwise_probability
    transitions: list[tuple[WorldState, str, WorldState, Fraction]] = []
    for world, phase in states:
        for action in actions:
            target_world = _world_target(world, action)
            transitions.extend(
                (
                    (
                        (world, phase),
                        action,
                        (target_world, (phase + 1) % 3),
                        clockwise_probability,
                    ),
                    (
                        (world, phase),
                        action,
                        (target_world, (phase - 1) % 3),
                        counterclockwise_probability,
                    ),
                )
            )
    bias_id = fraction_text(clockwise_probability).replace("/", "_")
    return ControlledMarkovSystem(
        system_id=f"record_selector_phase_{bias_id}",
        states=states,
        actions=actions,
        transitions=tuple(transitions),
    )


def _record_update_rows() -> tuple[tuple[str, str, str], ...]:
    memories = ("neutral", "saw_a", "saw_b")
    observations = ("A", "B", "H")
    return tuple(
        (
            memory,
            observation,
            "saw_a"
            if observation == "A"
            else "saw_b"
            if observation == "B"
            else memory,
        )
        for memory in memories
        for observation in observations
    )


def record_selector_controller(
    system: ControlledMarkovSystem[WorldState, str],
    *,
    use_record: bool,
) -> FiniteStateController[WorldState, str, str, str]:
    """Return matched controllers that differ only in decision-state record use."""

    memories = ("neutral", "saw_a", "saw_b")
    observations = ("A", "B", "H")
    policy_rows: list[tuple[str, str, str]] = []
    for memory in memories:
        for observation in observations:
            if observation == "A":
                action = "swap_a"
            elif observation == "B":
                action = "swap_b"
            elif use_record and memory == "saw_b":
                action = "swap_b"
            elif use_record and memory == "saw_a":
                action = "swap_a"
            else:
                action = "swap_a"
            policy_rows.append((memory, observation, action))
    return FiniteStateController(
        controller_id=(
            "record_sensitive_selector"
            if use_record
            else "record_ignoring_selector"
        ),
        memory_states=memories,
        initial_memory="neutral",
        observation_rows=tuple((state, state[0]) for state in system.states),
        update_rows=_record_update_rows(),
        policy_rows=tuple(policy_rows),
    )


def _closed_loop_path_law(
    system: ControlledMarkovSystem[WorldState, str],
    controller: FiniteStateController[WorldState, str, str, str],
    initial_world: FiniteDistribution[WorldState],
    *,
    horizon: int,
) -> FiniteDistribution[FinitePath[ClosedLoopState[WorldState, str], str]]:
    compiled = compile_closed_loop(system, controller)
    return finite_path_law(
        compiled.system,
        compiled.policy,
        closed_loop_initial_distribution(initial_world, controller),
        horizon=horizon,
    )


def _branch_fidelity(
    law: FiniteDistribution[FinitePath[ClosedLoopState[WorldState, str], str]],
) -> Fraction:
    return event_probability(
        law,
        lambda path: (
            path.start.world_state[0] in {"A", "B"}
            and path.end.world_state[0] == path.start.world_state[0]
        ),
    )


def _operational_signature(profile: dict[str, object]) -> tuple[object, ...]:
    return (
        profile["reachable_state_count"],
        profile["reachable_memory_count"],
        profile["selected_action_count"],
        profile["causal_action_influence"],
        profile["record_sensitive_selection"],
        profile["closed_loop_persistence"],
    )


def _matched_surface_signature(
    system: ControlledMarkovSystem[WorldState, str],
    selector: FiniteStateController[WorldState, str, str, str],
    baseline: FiniteStateController[WorldState, str, str, str],
    initial_world: FiniteDistribution[WorldState],
    *,
    capability_horizon: int,
) -> dict[str, object]:
    def controller_signature(
        controller: FiniteStateController[WorldState, str, str, str],
    ) -> dict[str, object]:
        return {
            "memory_states": list(controller.memory_states),
            "initial_memory": controller.initial_memory,
            "observation_rows": [
                [repr(state), observation]
                for state, observation in controller.observation_rows
            ],
            "update_rows": [list(row) for row in controller.update_rows],
            "policy_rows": [list(row) for row in controller.policy_rows],
        }

    return {
        "states": [repr(state) for state in system.states],
        "actions": list(system.actions),
        "transition_support": [
            [repr(source), action, repr(target)]
            for source, action, target, _probability in system.transitions
        ],
        "selector_controller": controller_signature(selector),
        "baseline_controller": controller_signature(baseline),
        "initial_world_rows": [
            [repr(state), fraction_text(mass)]
            for state, mass in initial_world.rows
        ],
        "capability_horizon": capability_horizon,
        "branch_fidelity_event": "initial_world_branch_equals_final_world_branch",
    }


def record_selector_case(
    *,
    clockwise_probability: Fraction,
    directionality_horizon: int,
    capability_horizon: int = 2,
) -> dict[str, object]:
    system = record_selector_world(
        clockwise_probability=clockwise_probability,
    )
    selector = record_selector_controller(system, use_record=True)
    baseline = record_selector_controller(system, use_record=False)
    operational_initial = FiniteDistribution(
        rows=(
            (("A", 0), Fraction(1, 2)),
            (("B", 0), Fraction(1, 2)),
        )
    )
    selector_profile = audit_operational_features(
        system,
        selector,
        operational_initial,
    ).as_dict()
    baseline_profile = audit_operational_features(
        system,
        baseline,
        operational_initial,
    ).as_dict()
    selector_law = _closed_loop_path_law(
        system,
        selector,
        operational_initial,
        horizon=capability_horizon,
    )
    baseline_law = _closed_loop_path_law(
        system,
        baseline,
        operational_initial,
        horizon=capability_horizon,
    )

    reference_initial = _uniform_distribution(system.states)
    reference_policy = _constant_policy(
        system,
        "hold",
        policy_id=f"{system.system_id}__reference_hold",
    )
    directionality = _self_reversal_summary(
        system,
        reference_policy,
        reference_initial,
        ActionInvolution(
            rows=(
                ("swap_a", "swap_a"),
                ("swap_b", "swap_b"),
                ("hold", "hold"),
            )
        ),
        horizon=directionality_horizon,
    )
    selector_fidelity = _branch_fidelity(selector_law)
    baseline_fidelity = _branch_fidelity(baseline_law)
    deformation_tv = total_variation_distance(selector_law, baseline_law)
    closed_loop_involution = ActionInvolution(
        rows=((CLOSED_LOOP_ACTION, CLOSED_LOOP_ACTION),)
    )
    selector_closed_loop_reverse = pull_back_reversed_path_law(
        selector_law,
        closed_loop_involution,
    )
    baseline_closed_loop_reverse = pull_back_reversed_path_law(
        baseline_law,
        closed_loop_involution,
    )
    return {
        "system_id": system.system_id,
        "clockwise_probability": fraction_text(clockwise_probability),
        "counterclockwise_probability": fraction_text(
            1 - clockwise_probability
        ),
        "directionality_horizon": directionality_horizon,
        "capability_horizon": capability_horizon,
        "directionality": directionality,
        "selector_profile": selector_profile,
        "baseline_profile": baseline_profile,
        "selector_branch_fidelity": fraction_text(selector_fidelity),
        "baseline_branch_fidelity": fraction_text(baseline_fidelity),
        "branch_fidelity_advantage": fraction_text(
            selector_fidelity - baseline_fidelity
        ),
        "policy_deformation_total_variation": fraction_text(deformation_tv),
        "selector_closed_loop_directionality": compare_laws(
            selector_law,
            selector_closed_loop_reverse,
        ).as_dict(),
        "baseline_closed_loop_directionality": compare_laws(
            baseline_law,
            baseline_closed_loop_reverse,
        ).as_dict(),
        "operational_signature": list(_operational_signature(selector_profile)),
        "matched_surface_signature": _matched_surface_signature(
            system,
            selector,
            baseline,
            operational_initial,
            capability_horizon=capability_horizon,
        ),
    }


def matched_record_selector_study(*, horizon: int) -> dict[str, object]:
    balanced = record_selector_case(
        clockwise_probability=Fraction(1, 2),
        directionality_horizon=horizon,
    )
    biased = record_selector_case(
        clockwise_probability=Fraction(3, 4),
        directionality_horizon=horizon,
    )
    balanced_surface = balanced["matched_surface_signature"]
    biased_surface = biased["matched_surface_signature"]
    matched_surface = {
        "state_space_equal": balanced_surface["states"] == biased_surface["states"],
        "actions_equal": balanced_surface["actions"] == biased_surface["actions"],
        "transition_support_equal": (
            balanced_surface["transition_support"]
            == biased_surface["transition_support"]
        ),
        "selector_controller_equal": (
            balanced_surface["selector_controller"]
            == biased_surface["selector_controller"]
        ),
        "baseline_controller_equal": (
            balanced_surface["baseline_controller"]
            == biased_surface["baseline_controller"]
        ),
        "initial_world_record_law_equal": (
            balanced_surface["initial_world_rows"]
            == biased_surface["initial_world_rows"]
        ),
        "branch_fidelity_event_equal": (
            balanced_surface["branch_fidelity_event"]
            == biased_surface["branch_fidelity_event"]
            and balanced_surface["capability_horizon"]
            == biased_surface["capability_horizon"]
        ),
        "phase_probabilities_differ": (
            balanced["clockwise_probability"] != biased["clockwise_probability"]
        ),
    }
    return {
        "balanced": balanced,
        "biased": biased,
        "matched_surface": matched_surface,
        "all_matched_controls_hold": all(matched_surface.values()),
        "balanced_directionally_null": (
            balanced["directionality"]["comparison"]["total_variation"] == "0"
        ),
        "biased_directionally_nonzero": (
            biased["directionality"]["comparison"]["total_variation"] != "0"
        ),
        "operational_signature_unchanged": (
            balanced["operational_signature"] == biased["operational_signature"]
        ),
        "branch_fidelity_unchanged": (
            balanced["selector_branch_fidelity"]
            == biased["selector_branch_fidelity"]
            and balanced["branch_fidelity_advantage"]
            == biased["branch_fidelity_advantage"]
        ),
        "policy_deformation_unchanged": (
            balanced["policy_deformation_total_variation"]
            == biased["policy_deformation_total_variation"]
        ),
    }


def directional_asymmetry_capability_summary(
    *,
    horizon: int = 3,
) -> dict[str, object]:
    if horizon < 1:
        raise ValueError("horizon must be positive")
    passive = passive_asymmetry_case(horizon=horizon)
    census = reversible_action_census(horizon=horizon)
    matched = matched_record_selector_study(horizon=horizon)

    passive_separates = (
        passive["directionality"]["comparison"]["total_variation"] != "0"
        and passive["features"]["causal_action_influence"] is False
        and passive["features"]["record_sensitive_selection"] is False
    )
    necessity_counterexample = (
        census["all_primitive_actions_bijective"]
        and census["all_reversal_contracts_hold"]
        and census["all_reverse_pair_distances_zero"]
        and census["qualifying_witness_count"] > 0
        and matched["balanced_directionally_null"]
        and matched["balanced"]["selector_profile"]["record_sensitive_selection"]
        is True
        and matched["balanced"]["selector_profile"]["causal_action_influence"]
        is True
        and matched["balanced"]["selector_profile"]["closed_loop_persistence"]
        is True
        and matched["balanced"]["branch_fidelity_advantage"] != "0"
    )
    independent_enabling_null = (
        matched["all_matched_controls_hold"]
        and matched["balanced_directionally_null"]
        and matched["biased_directionally_nonzero"]
        and matched["operational_signature_unchanged"]
        and matched["branch_fidelity_unchanged"]
        and matched["policy_deformation_unchanged"]
    )

    case_results = {
        "DA1_passive_asymmetry_not_sufficient": passive_separates,
        "DA2_reversal_paired_census_complete": (
            census["permutation_count"] == census["expected_permutation_count"]
            and census["policy_count"] == census["expected_policy_count"]
        ),
        "DA3_reversible_primitives_allow_functional_noninvertibility": (
            necessity_counterexample
        ),
        "DA4_matched_record_selector_control": matched[
            "all_matched_controls_hold"
        ],
        "DA5_independent_bias_does_not_change_profile": independent_enabling_null,
    }
    kill_conditions = {
        "passive_control_has_synthetic_selection": not passive_separates,
        "census_not_exhaustive": not case_results[
            "DA2_reversal_paired_census_complete"
        ],
        "primitive_reversal_contract_fails": not (
            census["all_primitive_actions_bijective"]
            and census["all_reversal_contracts_hold"]
            and census["all_reverse_pair_distances_zero"]
        ),
        "matched_surface_changes_beyond_phase_bias": not matched[
            "all_matched_controls_hold"
        ],
        "directionality_control_does_not_separate": not (
            matched["balanced_directionally_null"]
            and matched["biased_directionally_nonzero"]
        ),
        "feature_vector_changes_under_independent_product": not (
            matched["operational_signature_unchanged"]
            and matched["branch_fidelity_unchanged"]
            and matched["policy_deformation_unchanged"]
        ),
    }
    retained = all(case_results.values()) and not any(kill_conditions.values())
    return {
        "status": "retained" if retained else "failed",
        "verdict": (
            "asymmetry_not_sufficient_and_preexisting_bias_not_necessary"
            if retained
            else "protocol_failure"
        ),
        "protocol_doc": PROTOCOL_DOC,
        "horizon": horizon,
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "hypothesis_verdicts": {
            "directional_asymmetry_sufficiency": (
                "rejected" if passive_separates else "unresolved"
            ),
            "preexisting_substrate_bias_necessity": (
                "rejected_for_declared_operational_features"
                if necessity_counterexample
                else "unresolved"
            ),
            "process_level_asymmetry_necessity": "unresolved",
            "independent_directional_bias_enabling": (
                "rejected_in_matched_product_control"
                if independent_enabling_null
                else "unresolved"
            ),
            "coupled_directional_resource_enabling": "unresolved",
        },
        "dependencies": {
            "model": [
                "finite states",
                "finite actions",
                "exact transition kernel",
            ],
            "experiment": [
                "initial law",
                "controller",
                "finite horizon",
            ],
            "measurement": [
                "action involution",
                "path reversal",
                "branch-fidelity event",
            ],
            "interpretation": [
                "operational feature definitions",
            ],
        },
        "passive_asymmetry": passive,
        "reversible_action_census": census,
        "matched_record_selector": matched,
        "claim_boundary": (
            "Finite operational countermodels only; not Alpha, valuerhood, "
            "agency, standing, value, moral license, Omega compatibility, or "
            "a physical arrow-of-time result."
        ),
    }


def case_result_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    return [
        {"case": case, "passed": passed}
        for case, passed in summary["case_results"].items()
    ]


def passive_asymmetry_rows(
    summary: dict[str, object],
) -> list[dict[str, object]]:
    case = summary["passive_asymmetry"]
    return [
        {
            "system_id": case["system_id"],
            "horizon": case["horizon"],
            "directional_total_variation": case["directionality"]["comparison"][
                "total_variation"
            ],
            "support_equal": case["directionality"]["comparison"]["support_equal"],
            "causal_action_influence": case["features"][
                "causal_action_influence"
            ],
            "record_sensitive_selection": case["features"][
                "record_sensitive_selection"
            ],
            "closed_loop_persistence": case["features"][
                "closed_loop_persistence"
            ],
        }
    ]


def reversible_action_rows(
    summary: dict[str, object],
) -> list[dict[str, object]]:
    return list(summary["reversible_action_census"]["rows"])


def record_selector_rows(
    summary: dict[str, object],
) -> list[dict[str, object]]:
    study = summary["matched_record_selector"]
    return [
        {
            "case": case_name,
            "clockwise_probability": case["clockwise_probability"],
            "directional_total_variation": case["directionality"]["comparison"][
                "total_variation"
            ],
            "causal_action_influence": case["selector_profile"][
                "causal_action_influence"
            ],
            "record_sensitive_selection": case["selector_profile"][
                "record_sensitive_selection"
            ],
            "closed_loop_persistence": case["selector_profile"][
                "closed_loop_persistence"
            ],
            "selector_branch_fidelity": case["selector_branch_fidelity"],
            "baseline_branch_fidelity": case["baseline_branch_fidelity"],
            "branch_fidelity_advantage": case["branch_fidelity_advantage"],
            "policy_deformation_total_variation": case[
                "policy_deformation_total_variation"
            ],
            "selector_closed_loop_directional_total_variation": case[
                "selector_closed_loop_directionality"
            ]["total_variation"],
            "selector_closed_loop_support_equal": case[
                "selector_closed_loop_directionality"
            ]["support_equal"],
        }
        for case_name, case in (
            ("balanced", study["balanced"]),
            ("biased", study["biased"]),
        )
    ]
