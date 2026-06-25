"""Blind generated discovery for agency-diamond metrics.

The challenge and cross-substrate pilots still use named generator modes.  This
module removes expected class labels from the run surface: a frozen pool of
seeded finite controlled systems is generated from structural knobs, evaluated,
clustered by metric signatures, and then inspected for hierarchy witnesses,
ablation sensitivity, and null/collapse cases.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Any

from omega.agency_diamond.baselines import (
    find_baseline_collisions,
    required_collision_status,
)
from omega.agency_diamond.challenge import (
    CHALLENGE_HORIZONS,
    REQUIRED_HOLDOUT_CLASSES,
    SearchWitness,
    collapse_alerts_for,
)
from omega.agency_diamond.metrics import DiamondMetrics, evaluate_system
from omega.agency_diamond.model import ControlledSystem, State


BLIND_SEEDS = tuple(range(1201, 1261))
BLIND_HORIZONS = CHALLENGE_HORIZONS
ABLATION_HORIZONS = (1, 2, 3, 4)


@dataclass(frozen=True)
class BlindCase:
    seed: int
    system: ControlledSystem
    generator_knobs: dict[str, object]


@dataclass(frozen=True)
class AblationWitness:
    name: str
    passed: bool
    source_case: str | None
    ablated_case: str | None
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "source_case": self.source_case,
            "ablated_case": self.ablated_case,
            "details": self.details,
        }


def blind_cases() -> tuple[BlindCase, ...]:
    return tuple(generate_blind_case(seed=seed) for seed in BLIND_SEEDS)


def evaluate_blind_cases() -> list[DiamondMetrics]:
    metrics: list[DiamondMetrics] = []
    for case in blind_cases():
        for horizon in BLIND_HORIZONS:
            metrics.append(
                evaluate_system(
                    case.system,
                    horizon=horizon,
                    case_id=f"blind__seed{case.seed}_h{horizon}",
                )
            )
    return metrics


def blind_discovery_summary() -> dict[str, Any]:
    cases = blind_cases()
    metrics = evaluate_blind_cases()
    collisions = find_baseline_collisions(metrics)
    collision_status = required_collision_status(collisions)
    search = blind_counterexample_search(metrics)
    collapse_alerts = collapse_alerts_for(metrics)
    clusters = derived_cluster_summary(metrics)
    representatives = representative_summary(metrics)
    ablations = ablation_probe_summary(cases)
    negative = negative_result_retention(metrics)
    class_set = set(metric.classification for metric in metrics)

    gates = {
        "blind_pool_has_no_expected_class_labels": all(
            "expected_class" not in case.generator_knobs for case in cases
        ),
        "multiple_classes_discovered": len(class_set) >= 5,
        "required_classes_discovered": REQUIRED_HOLDOUT_CLASSES <= class_set,
        "required_baseline_collisions_found": all(collision_status.values()),
        "counterexample_search_witnesses_found": all(witness.passed for witness in search),
        "ablation_probes_passed": all(ablations["probe_status"].values()),
        "negative_results_retained": all(negative["retention_status"].values()),
        "collapse_alerts_retained": "collapse_alerts" in negative,
    }

    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "generator": {
            "seed_count": len(BLIND_SEEDS),
            "seeds": list(BLIND_SEEDS),
            "horizons": list(BLIND_HORIZONS),
            "ablation_horizons": list(ABLATION_HORIZONS),
            "surface": (
                "Seeded structural knobs only; expected class labels are not "
                "declared by the pool."
            ),
        },
        "case_counts": {
            "systems": len(cases),
            "metric_cases": len(metrics),
        },
        "classification_counts": _classification_counts(metrics),
        "axis_distribution": axis_distribution(metrics),
        "derived_clusters": clusters,
        "representatives": representatives,
        "required_baseline_collision_status": collision_status,
        "baseline_collision_count": len(collisions),
        "baseline_collision_witnesses": [witness.as_dict() for witness in collisions],
        "counterexample_search": [witness.as_dict() for witness in search],
        "ablation_probes": ablations,
        "negative_result_retention": negative,
        "collapse_alerts": collapse_alerts,
        "decision_gate": gates,
    }


def generate_blind_case(*, seed: int) -> BlindCase:
    rng = random.Random(seed * 2654435761)
    if rng.randrange(7) == 0:
        system, knobs = _action_insensitive_system(seed=seed, rng=rng)
    else:
        system, knobs = _structural_knob_system(seed=seed, rng=rng)
    return BlindCase(seed=seed, system=system, generator_knobs=knobs)


def derived_cluster_summary(metrics: list[DiamondMetrics]) -> dict[str, Any]:
    grouped: dict[str, list[DiamondMetrics]] = defaultdict(list)
    for metric in metrics:
        grouped[_metric_signature(metric)].append(metric)
    clusters = []
    for signature, cases in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        clusters.append(
            {
                "signature": signature,
                "count": len(cases),
                "representative": cases[0].case_id,
                "classifications": dict(
                    sorted(Counter(metric.classification for metric in cases).items())
                ),
            }
        )
    return {
        "cluster_count": len(clusters),
        "clusters": clusters,
    }


def blind_counterexample_search(metrics: list[DiamondMetrics]) -> list[SearchWitness]:
    return [
        _metric_pair_search(
            metrics,
            name="blind_recurrence_does_not_imply_feedback_advantage",
            left_pred=lambda m: m.recurrence_detected and m.feedback_advantage == 0,
            right_pred=lambda m: m.recurrence_detected and m.feedback_advantage > 0,
            details=lambda left, right: {
                "shared_recurrence": True,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _metric_pair_search(
            metrics,
            name="blind_control_does_not_imply_feedback_advantage",
            left_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage == 0,
            right_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage > 0,
            details=lambda left, right: {
                "left_control_reach_count": left.control_reach_count,
                "right_control_reach_count": right.control_reach_count,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _metric_pair_search(
            metrics,
            name="blind_feedback_does_not_imply_reflexive_maintenance",
            left_pred=lambda m: m.feedback_advantage > 0
            and not _positive_optional(m.reflexive_advantage),
            right_pred=lambda m: m.feedback_advantage > 0
            and _positive_optional(m.reflexive_advantage),
            details=lambda left, right: {
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "left_reflexive_advantage": _optional_frac(left.reflexive_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
                "right_reflexive_advantage": _optional_frac(right.reflexive_advantage),
            },
        ),
        _same_live_score_joint_search(metrics),
    ]


def axis_distribution(metrics: list[DiamondMetrics]) -> dict[str, dict[str, int]]:
    return {
        "control": _count_by(metrics, lambda m: "positive" if m.control_reach_count > 0 else "zero"),
        "observable_control": _count_by(
            metrics,
            lambda m: "positive" if m.observable_control_count > 0 else "zero",
        ),
        "feedback": _count_by(metrics, lambda m: _sign(m.feedback_advantage)),
        "reflexive": _count_by(metrics, lambda m: _optional_positive(m.reflexive_advantage)),
        "joint": _count_by(metrics, lambda m: _optional_sign(m.joint_effect_delta)),
        "recurrence": _count_by(metrics, lambda m: str(m.recurrence_detected)),
    }


def representative_summary(metrics: list[DiamondMetrics]) -> dict[str, Any]:
    by_class: dict[str, DiamondMetrics] = {}
    by_signature: dict[str, DiamondMetrics] = {}
    for metric in metrics:
        by_class.setdefault(metric.classification, metric)
        by_signature.setdefault(_metric_signature(metric), metric)
    return {
        "by_class": {
            name: metric.as_dict()
            for name, metric in sorted(by_class.items())
        },
        "by_signature": {
            signature: metric.as_dict()
            for signature, metric in sorted(by_signature.items())
        },
    }


def negative_result_retention(metrics: list[DiamondMetrics]) -> dict[str, Any]:
    passive = _first_metric(metrics, lambda m: m.classification == "passive_persistence")
    no_control = _first_metric(metrics, lambda m: m.control_reach_count == 0)
    no_feedback_with_control = _first_metric(
        metrics,
        lambda m: m.control_reach_count > 0 and m.feedback_advantage == 0,
    )
    no_reflexive_with_feedback = _first_metric(
        metrics,
        lambda m: m.feedback_advantage > 0 and not _positive_optional(m.reflexive_advantage),
    )
    negative_joint = _first_metric(
        metrics,
        lambda m: m.joint_effect_delta is not None and m.joint_effect_delta < 0,
    )
    examples = {
        "passive_persistence": _maybe_metric(passive),
        "no_control": _maybe_metric(no_control),
        "control_without_feedback": _maybe_metric(no_feedback_with_control),
        "feedback_without_reflexive": _maybe_metric(no_reflexive_with_feedback),
        "negative_joint_effect": _maybe_metric(negative_joint),
    }
    return {
        "retention_status": {
            name: value is not None
            for name, value in examples.items()
        },
        "examples": examples,
        "collapse_alerts": collapse_alerts_for(metrics),
    }


def ablation_probe_summary(cases: tuple[BlindCase, ...]) -> dict[str, Any]:
    witnesses = [
        _ablation_search(
            cases,
            name="blind_observation_ablation_reduces_feedback",
            ablation_name="constant_observation",
            transform=constant_observation_ablation,
            predicate=lambda original, ablated: (
                original.feedback_advantage > 0
                and ablated.feedback_advantage < original.feedback_advantage
            ),
            details=lambda original, ablated: {
                "original_feedback": _frac(original.feedback_advantage),
                "ablated_feedback": _frac(ablated.feedback_advantage),
            },
        ),
        _ablation_search(
            cases,
            name="blind_fixed_policy_ablation_reduces_feedback",
            ablation_name="fixed_policy",
            transform=fixed_policy_ablation,
            predicate=lambda original, ablated: (
                original.feedback_advantage > 0
                and ablated.feedback_advantage < original.feedback_advantage
            ),
            details=lambda original, ablated: {
                "original_feedback": _frac(original.feedback_advantage),
                "ablated_feedback": _frac(ablated.feedback_advantage),
            },
        ),
        _ablation_search(
            cases,
            name="blind_action_choice_ablation_removes_control",
            ablation_name="single_action_dynamics",
            transform=single_action_dynamics_ablation,
            predicate=lambda original, ablated: (
                original.control_reach_count > 0 and ablated.control_reach_count == 0
            ),
            details=lambda original, ablated: {
                "original_control_reach_count": original.control_reach_count,
                "ablated_control_reach_count": ablated.control_reach_count,
            },
        ),
        _ablation_search(
            cases,
            name="blind_channel_ablation_reduces_reflexive_maintenance",
            ablation_name="break_channel_repair",
            transform=break_channel_repair_ablation,
            predicate=lambda original, ablated: (
                _positive_optional(original.reflexive_advantage)
                and (
                    ablated.reflexive_advantage is None
                    or ablated.reflexive_advantage < original.reflexive_advantage
                )
            ),
            details=lambda original, ablated: {
                "original_reflexive": _optional_frac(original.reflexive_advantage),
                "ablated_reflexive": _optional_frac(ablated.reflexive_advantage),
            },
        ),
        _ablation_search(
            cases,
            name="blind_joint_ablation_changes_joint_effect",
            ablation_name="neutralize_joint_surface",
            transform=neutralize_joint_surface_ablation,
            predicate=lambda original, ablated: (
                original.joint_effect_delta is not None
                and ablated.joint_effect_delta is not None
                and ablated.joint_effect_delta != original.joint_effect_delta
            ),
            details=lambda original, ablated: {
                "original_joint": _optional_frac(original.joint_effect_delta),
                "ablated_joint": _optional_frac(ablated.joint_effect_delta),
            },
        ),
    ]
    return {
        "probe_status": {witness.name: witness.passed for witness in witnesses},
        "witnesses": [witness.as_dict() for witness in witnesses],
    }


def constant_observation_ablation(system: ControlledSystem) -> ControlledSystem:
    blind = f"{system.system_id}__blind_obs"
    nominal_action = system.live_policy[system.observe[system.scenario_starts[system.nominal_scenario]]]
    return replace(
        system,
        system_id=f"{system.system_id}__constant_observation",
        description=f"Constant-observation ablation of {system.system_id}.",
        observations=(blind,),
        observe={state: blind for state in system.states},
        live_policy={blind: nominal_action},
    )


def fixed_policy_ablation(system: ControlledSystem) -> ControlledSystem:
    nominal_action = system.live_policy[system.observe[system.scenario_starts[system.nominal_scenario]]]
    return replace(
        system,
        system_id=f"{system.system_id}__fixed_policy",
        description=f"Fixed-policy ablation of {system.system_id}.",
        live_policy={observation: nominal_action for observation in system.observations},
    )


def single_action_dynamics_ablation(system: ControlledSystem) -> ControlledSystem:
    fixed_action = system.actions[0]
    transition = {
        scenario: {
            state: {
                action: by_action[fixed_action]
                for action in system.actions
            }
            for state, by_action in by_state.items()
        }
        for scenario, by_state in system.transition.items()
    }
    return replace(
        system,
        system_id=f"{system.system_id}__single_action_dynamics",
        description=f"Single-action-dynamics ablation of {system.system_id}.",
        transition=transition,
    )


def break_channel_repair_ablation(system: ControlledSystem) -> ControlledSystem | None:
    if not system.channel_challenge_scenarios:
        return None
    fail_state = _failure_state(system)
    transition = {
        scenario: {
            state: dict(by_action)
            for state, by_action in by_state.items()
        }
        for scenario, by_state in system.transition.items()
    }
    for scenario in system.channel_challenge_scenarios:
        start = system.scenario_starts[scenario]
        transition[scenario][start] = {action: fail_state for action in system.actions}
    return replace(
        system,
        system_id=f"{system.system_id}__broken_channel",
        description=f"Channel-repair ablation of {system.system_id}.",
        transition=transition,
    )


def neutralize_joint_surface_ablation(system: ControlledSystem) -> ControlledSystem | None:
    if system.joint_safe_states is None:
        return None
    return replace(
        system,
        system_id=f"{system.system_id}__neutral_joint_surface",
        description=f"Joint-surface neutralization of {system.system_id}.",
        joint_safe_states=frozenset(system.viable_states),
    )


def _action_insensitive_system(
    *,
    seed: int,
    rng: random.Random,
) -> tuple[ControlledSystem, dict[str, object]]:
    size = 3 + rng.randrange(3)
    states = tuple(f"blind{seed}_p{index}" for index in range(size))
    actions = tuple(f"u{seed}_{index}" for index in range(3))
    observations = tuple(f"z{seed}_{index}" for index in range(size))
    successor = {state: states[(index + 1) % size] for index, state in enumerate(states)}
    scenarios = ("nominal", "phase_a", "phase_b")
    transition = {
        scenario: {
            state: {action: successor[state] for action in actions}
            for state in states
        }
        for scenario in scenarios
    }
    system = ControlledSystem(
        system_id=f"blind_seed{seed}",
        family="agency_diamond_blind_discovery",
        description="Seeded action-insensitive finite controlled system.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": states[0],
            "phase_a": states[1 % size],
            "phase_b": states[2 % size],
        },
        transition=transition,
        observe={state: observations[index] for index, state in enumerate(states)},
        live_policy={observation: actions[0] for observation in observations},
        target_states=frozenset(states),
        viable_states=frozenset(states),
        channel_states=frozenset(states),
    )
    return system, {
        "state_count": size,
        "action_count": len(actions),
        "action_effective": False,
    }


def _structural_knob_system(
    *,
    seed: int,
    rng: random.Random,
) -> tuple[ControlledSystem, dict[str, object]]:
    demand_visible = rng.random() < 0.56
    channel_enabled = rng.random() < 0.48
    channel_visible = channel_enabled and rng.random() < 0.78
    joint_enabled = rng.random() < 0.42
    joint_capture = joint_enabled and rng.random() < 0.5

    states = (
        f"blind{seed}_q0",
        f"blind{seed}_q1",
        f"blind{seed}_q2",
        f"blind{seed}_q3",
        f"blind{seed}_q4",
        f"blind{seed}_q5",
        f"blind{seed}_q6",
        f"blind{seed}_q7",
    )
    home, need_zero, need_one, good, bad, channel_bad, joint, captured = states
    actions = (f"u{seed}_0", f"u{seed}_1", f"u{seed}_2")
    u0, u1, u2 = actions

    transition = {
        home: {u0: home, u1: home, u2: home},
        need_zero: {u0: good, u1: bad, u2: bad},
        need_one: {u0: bad, u1: good, u2: bad},
        good: {u0: good, u1: good, u2: good},
        bad: {u0: bad, u1: bad, u2: bad},
        channel_bad: {u0: bad, u1: bad, u2: good if channel_enabled else bad},
        joint: _joint_transition(
            u0=u0,
            u1=u1,
            u2=u2,
            good=good,
            bad=bad,
            captured=captured,
            enabled=joint_enabled,
            capture=joint_capture,
        ),
        captured: {u0: captured, u1: captured, u2: captured},
    }
    scenarios = ("nominal", "demand_zero", "demand_one")
    starts = {
        "nominal": home,
        "demand_zero": need_zero,
        "demand_one": need_one,
    }
    if channel_enabled:
        scenarios = scenarios + ("channel_fault",)
        starts["channel_fault"] = channel_bad
    if joint_enabled:
        scenarios = scenarios + ("joint_pressure",)
        starts["joint_pressure"] = joint

    observations = _observations_for(
        seed=seed,
        states=states,
        demand_visible=demand_visible,
        channel_visible=channel_visible,
        joint_enabled=joint_enabled,
    )
    observe = observations["observe"]
    live_policy = {
        observation: u0
        for observation in observations["observations"]
    }
    if demand_visible:
        live_policy[observe[need_zero]] = u0
        live_policy[observe[need_one]] = u1
    if channel_visible:
        live_policy[observe[channel_bad]] = u2
    if joint_enabled:
        live_policy[observe[joint]] = u2 if joint_capture else u1

    target_states = {home, good}
    if joint_enabled:
        target_states.add(captured)
    viable_states = {home, need_zero, need_one, good}
    if channel_enabled:
        viable_states.add(channel_bad)
    if joint_enabled:
        viable_states.update({joint, captured})

    system = ControlledSystem(
        system_id=f"blind_seed{seed}",
        family="agency_diamond_blind_discovery",
        description="Seeded structural-knob finite controlled system.",
        states=states,
        actions=actions,
        observations=observations["observations"],
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts=starts,
        transition={scenario: transition for scenario in scenarios},
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset(target_states),
        viable_states=frozenset(viable_states),
        channel_states=frozenset({home, need_zero, need_one, good, joint}),
        channel_challenge_scenarios=("channel_fault",) if channel_enabled else (),
        joint_safe_states=(
            None
            if not joint_enabled
            else frozenset({home, need_zero, need_one, good, channel_bad, joint})
        ),
    )
    return system, {
        "state_count": len(states),
        "action_count": len(actions),
        "demand_visible": demand_visible,
        "channel_enabled": channel_enabled,
        "channel_visible": channel_visible,
        "joint_enabled": joint_enabled,
        "joint_capture_policy": joint_capture,
    }


def _joint_transition(
    *,
    u0: str,
    u1: str,
    u2: str,
    good: str,
    bad: str,
    captured: str,
    enabled: bool,
    capture: bool,
) -> dict[str, str]:
    if not enabled:
        return {u0: bad, u1: bad, u2: bad}
    if capture:
        return {u0: good, u1: good, u2: captured}
    return {u0: bad, u1: good, u2: captured}


def _observations_for(
    *,
    seed: int,
    states: tuple[State, ...],
    demand_visible: bool,
    channel_visible: bool,
    joint_enabled: bool,
) -> dict[str, Any]:
    home, need_zero, need_one, good, bad, channel_bad, joint, captured = states
    obs_home = f"obs{seed}_home"
    obs_need = f"obs{seed}_need"
    obs_need_zero = f"obs{seed}_need_zero"
    obs_need_one = f"obs{seed}_need_one"
    obs_good = f"obs{seed}_good"
    obs_bad = f"obs{seed}_bad"
    obs_channel = f"obs{seed}_channel"
    obs_joint = f"obs{seed}_joint"
    obs_capture = f"obs{seed}_capture"
    observe = {
        home: obs_home,
        need_zero: obs_need_zero if demand_visible else obs_need,
        need_one: obs_need_one if demand_visible else obs_need,
        good: obs_good,
        bad: obs_bad,
        channel_bad: obs_channel if channel_visible else obs_need,
        joint: obs_joint if joint_enabled else obs_need,
        captured: obs_capture,
    }
    return {
        "observations": tuple(dict.fromkeys(observe.values())),
        "observe": observe,
    }


def _ablation_search(
    cases: tuple[BlindCase, ...],
    *,
    name: str,
    ablation_name: str,
    transform,
    predicate,
    details,
) -> AblationWitness:
    for case in cases:
        ablated_system = transform(case.system)
        if ablated_system is None:
            continue
        for horizon in ABLATION_HORIZONS:
            original = evaluate_system(
                case.system,
                horizon=horizon,
                case_id=f"blind__seed{case.seed}_h{horizon}",
            )
            ablated = evaluate_system(
                ablated_system,
                horizon=horizon,
                case_id=f"blind__seed{case.seed}__{ablation_name}_h{horizon}",
            )
            if predicate(original, ablated):
                return AblationWitness(
                    name=name,
                    passed=True,
                    source_case=original.case_id,
                    ablated_case=ablated.case_id,
                    details=details(original, ablated),
                )
    return AblationWitness(
        name=name,
        passed=False,
        source_case=None,
        ablated_case=None,
        details={},
    )


def _metric_pair_search(
    metrics: list[DiamondMetrics],
    *,
    name: str,
    left_pred,
    right_pred,
    details,
) -> SearchWitness:
    left = next((metric for metric in metrics if left_pred(metric)), None)
    right = next((metric for metric in metrics if right_pred(metric)), None)
    return SearchWitness(
        name=name,
        passed=left is not None and right is not None,
        left_case=None if left is None else left.case_id,
        right_case=None if right is None else right.case_id,
        details={} if left is None or right is None else details(left, right),
    )


def _same_live_score_joint_search(metrics: list[DiamondMetrics]) -> SearchWitness:
    candidates = [
        metric
        for metric in metrics
        if metric.joint_effect_delta is not None
    ]
    for left in candidates:
        if left.joint_effect_delta is None or left.joint_effect_delta <= 0:
            continue
        for right in candidates:
            if (
                right.case_id != left.case_id
                and right.live_maintenance_score == left.live_maintenance_score
                and right.joint_effect_delta is not None
                and right.joint_effect_delta < 0
            ):
                return SearchWitness(
                    name="blind_live_success_scalar_does_not_determine_joint_effect",
                    passed=True,
                    left_case=left.case_id,
                    right_case=right.case_id,
                    details={
                        "shared_live_maintenance": _frac(left.live_maintenance_score),
                        "left_joint_effect": _optional_frac(left.joint_effect_delta),
                        "right_joint_effect": _optional_frac(right.joint_effect_delta),
                    },
                )
    return SearchWitness(
        name="blind_live_success_scalar_does_not_determine_joint_effect",
        passed=False,
        left_case=None,
        right_case=None,
        details={},
    )


def _failure_state(system: ControlledSystem) -> State:
    for state in system.states:
        if state not in system.viable_states:
            return state
    for state in system.states:
        if state not in system.target_states:
            return state
    return system.states[-1]


def _first_metric(metrics: list[DiamondMetrics], predicate) -> DiamondMetrics | None:
    return next((metric for metric in metrics if predicate(metric)), None)


def _maybe_metric(metric: DiamondMetrics | None) -> dict[str, Any] | None:
    return None if metric is None else metric.as_dict()


def _classification_counts(metrics: list[DiamondMetrics]) -> dict[str, int]:
    return dict(sorted(Counter(metric.classification for metric in metrics).items()))


def _count_by(metrics: list[DiamondMetrics], key) -> dict[str, int]:
    return dict(sorted(Counter(key(metric) for metric in metrics).items()))


def _metric_signature(metric: DiamondMetrics) -> str:
    return "|".join(
        (
            f"control={metric.control_reach_count > 0}",
            f"observable={metric.observable_control_count > 0}",
            f"feedback={_sign(metric.feedback_advantage)}",
            f"reflexive={_optional_positive(metric.reflexive_advantage)}",
            f"joint={_optional_sign(metric.joint_effect_delta)}",
            f"recurrence={metric.recurrence_detected}",
        )
    )


def _sign(value: Fraction) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def _optional_sign(value: Fraction | None) -> str:
    return "undeclared" if value is None else _sign(value)


def _optional_positive(value: Fraction | None) -> str:
    if value is None:
        return "not_applicable"
    return "positive" if value > 0 else "not_positive"


def _positive_optional(value: Fraction | None) -> bool:
    return value is not None and value > 0


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _optional_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
