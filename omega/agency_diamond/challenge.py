"""Non-handcrafted challenge generation for agency-diamond pilots."""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from omega.agency_diamond.baselines import (
    find_baseline_collisions,
    required_collision_status,
)
from omega.agency_diamond.examples import MID_SCALE_HORIZONS
from omega.agency_diamond.generated import relabel_with_decoys
from omega.agency_diamond.metrics import DiamondMetrics, evaluate_system
from omega.agency_diamond.model import ControlledSystem
from omega.agency_diamond.transport import presentation_report, transport_pilot


GRAMMARS = (
    "cycle",
    "open_loop",
    "feedback",
    "reflexive",
    "joint_positive",
    "joint_negative",
)
TRAIN_SEEDS = (101, 103, 107)
HOLDOUT_SEEDS = (401, 409, 419, 431)
CHALLENGE_HORIZONS = MID_SCALE_HORIZONS
REQUIRED_HOLDOUT_CLASSES = {
    "passive_or_driven_recurrence",
    "control_without_feedback_advantage",
    "feedback_advantage",
    "reflexive_maintenance",
    "dominant_joint_contraction",
}


@dataclass(frozen=True)
class ChallengeCase:
    split: str
    grammar: str
    seed: int
    system: ControlledSystem


@dataclass(frozen=True)
class SearchWitness:
    name: str
    passed: bool
    left_case: str | None
    right_case: str | None
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "left_case": self.left_case,
            "right_case": self.right_case,
            "details": self.details,
        }


def challenge_cases() -> tuple[ChallengeCase, ...]:
    cases: list[ChallengeCase] = []
    for split, seeds in (("train", TRAIN_SEEDS), ("holdout", HOLDOUT_SEEDS)):
        for grammar in GRAMMARS:
            for seed in seeds:
                cases.append(
                    ChallengeCase(
                        split=split,
                        grammar=grammar,
                        seed=seed,
                        system=generate_system(grammar=grammar, seed=seed),
                    )
                )
    return tuple(cases)


def evaluate_challenge_cases() -> list[DiamondMetrics]:
    metrics: list[DiamondMetrics] = []
    for case in challenge_cases():
        for horizon in CHALLENGE_HORIZONS:
            metrics.append(
                evaluate_system(
                    case.system,
                    horizon=horizon,
                    case_id=f"{case.split}__{case.grammar}__seed{case.seed}_h{horizon}",
                )
            )
    return metrics


def challenge_summary() -> dict[str, Any]:
    metrics = evaluate_challenge_cases()
    holdout = [metric for metric in metrics if metric.case_id.startswith("holdout__")]
    train = [metric for metric in metrics if metric.case_id.startswith("train__")]
    collisions = find_baseline_collisions(holdout)
    collision_status = required_collision_status(collisions)
    search = counterexample_search(holdout)
    collapse_alerts = collapse_alerts_for(holdout)
    transport = transport_challenge(holdout)
    holdout_classes = set(metric.classification for metric in holdout)

    gates = {
        "holdout_classes_cover_required": REQUIRED_HOLDOUT_CLASSES <= holdout_classes,
        "required_baseline_collisions_found": all(collision_status.values()),
        "counterexample_search_witnesses_found": all(witness.passed for witness in search),
        "no_collapse_alerts": not collapse_alerts,
        "transport_invariance_passed": bool(transport["all_transport_checks_passed"]),
    }

    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "generator": {
            "grammars": list(GRAMMARS),
            "train_seeds": list(TRAIN_SEEDS),
            "holdout_seeds": list(HOLDOUT_SEEDS),
            "horizons": list(CHALLENGE_HORIZONS),
        },
        "case_counts": {
            "systems": len(challenge_cases()),
            "metric_cases": len(metrics),
            "train_metric_cases": len(train),
            "holdout_metric_cases": len(holdout),
        },
        "train_classification_counts": _classification_counts(train),
        "holdout_classification_counts": _classification_counts(holdout),
        "holdout_required_classes": sorted(REQUIRED_HOLDOUT_CLASSES),
        "required_baseline_collision_status": collision_status,
        "baseline_collision_count": len(collisions),
        "baseline_collision_witnesses": [witness.as_dict() for witness in collisions],
        "counterexample_search": [witness.as_dict() for witness in search],
        "collapse_alerts": collapse_alerts,
        "transport": transport,
        "decision_gate": gates,
    }


def generate_system(*, grammar: str, seed: int) -> ControlledSystem:
    rng = random.Random((seed * 7919) + sum(ord(ch) for ch in grammar))
    if grammar == "cycle":
        return _cycle(seed=seed, rng=rng)
    if grammar == "open_loop":
        return _open_loop(seed=seed, rng=rng, observable=False)
    if grammar == "feedback":
        return _open_loop(seed=seed, rng=rng, observable=True)
    if grammar == "reflexive":
        return _reflexive(seed=seed, rng=rng)
    if grammar == "joint_positive":
        return _joint(seed=seed, rng=rng, cooperative=True)
    if grammar == "joint_negative":
        return _joint(seed=seed, rng=rng, cooperative=False)
    raise ValueError(f"unknown challenge grammar: {grammar}")


def counterexample_search(metrics: list[DiamondMetrics]) -> list[SearchWitness]:
    return [
        _pair_search(
            metrics,
            name="generated_recurrence_does_not_imply_feedback_advantage",
            left_pred=lambda m: m.recurrence_detected and m.feedback_advantage == 0,
            right_pred=lambda m: m.recurrence_detected and m.feedback_advantage > 0,
            details=lambda left, right: {
                "shared_recurrence": True,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="generated_control_does_not_imply_feedback_advantage",
            left_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage == 0,
            right_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage > 0,
            details=lambda left, right: {
                "left_control_reach_count": left.control_reach_count,
                "right_control_reach_count": right.control_reach_count,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="generated_feedback_does_not_imply_reflexive_maintenance",
            left_pred=lambda m: m.feedback_advantage > 0 and not _positive_optional(m.reflexive_advantage),
            right_pred=lambda m: m.feedback_advantage > 0 and _positive_optional(m.reflexive_advantage),
            details=lambda left, right: {
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "left_reflexive_advantage": _optional_frac(left.reflexive_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
                "right_reflexive_advantage": _optional_frac(right.reflexive_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="generated_live_success_does_not_determine_joint_effect",
            left_pred=lambda m: m.live_maintenance_score == 1
            and m.joint_effect_delta is not None
            and m.joint_effect_delta > 0,
            right_pred=lambda m: m.live_maintenance_score == 1
            and m.joint_effect_delta is not None
            and m.joint_effect_delta < 0,
            details=lambda left, right: {
                "shared_live_maintenance": _frac(left.live_maintenance_score),
                "left_joint_effect": _optional_frac(left.joint_effect_delta),
                "right_joint_effect": _optional_frac(right.joint_effect_delta),
            },
        ),
    ]


def collapse_alerts_for(metrics: list[DiamondMetrics]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for metric in metrics:
        if _positive_optional(metric.reflexive_advantage) and metric.feedback_advantage <= 0:
            alerts.append(_alert(metric, "reflexive_without_feedback_advantage"))
        if _positive_optional(metric.reflexive_advantage) and metric.observable_control_count == 0:
            alerts.append(_alert(metric, "reflexive_without_observable_control"))
        if metric.feedback_advantage > 0 and metric.observable_control_count == 0:
            alerts.append(_alert(metric, "feedback_without_observable_control"))
        if metric.classification == "dominant_joint_contraction" and not (
            metric.joint_effect_delta is not None and metric.joint_effect_delta < 0
        ):
            alerts.append(_alert(metric, "dominant_class_without_negative_joint_effect"))
    return alerts


def transport_challenge(metrics: list[DiamondMetrics]) -> dict[str, Any]:
    cases = challenge_cases()
    holdout_systems = [case.system for case in cases if case.split == "holdout"]
    sample = holdout_systems[:12]
    relabel_reports = []
    for index, system in enumerate(sample):
        relabeled = relabel_with_decoys(system, seed=9000 + index)
        exact_profile = tuple(
            evaluate_system(system, horizon=horizon).classification
            for horizon in CHALLENGE_HORIZONS
        )
        relabeled_profile = tuple(
            evaluate_system(relabeled, horizon=horizon).classification
            for horizon in CHALLENGE_HORIZONS
        )
        relabel_reports.append(
            {
                "system_id": system.system_id,
                "relabeled_system_id": relabeled.system_id,
                "profile_preserved": exact_profile == relabeled_profile,
            }
        )

    identity_reports = []
    for system in sample:
        presentation = {state: state for state in system.states}
        identity_reports.append(
            presentation_report(
                system,
                presentation,
                case_id=f"{system.system_id}__identity_presentation",
            ).as_dict()
        )

    quotient_controls = transport_pilot()
    checks = {
        "relabel_profiles_preserved": all(report["profile_preserved"] for report in relabel_reports),
        "identity_presentations_preserve_profiles": all(
            report["quotient_constructible"] and report["profile_preserved"] is True
            for report in identity_reports
        ),
        "quotient_controls_passed": bool(quotient_controls["all_transport_checks_passed"]),
    }
    return {
        "checks": checks,
        "all_transport_checks_passed": all(checks.values()),
        "relabel_reports": relabel_reports,
        "identity_report_count": len(identity_reports),
        "quotient_controls": quotient_controls,
    }


def _cycle(*, seed: int, rng: random.Random) -> ControlledSystem:
    n = 3 + (seed % 3)
    states = tuple(f"c{seed}_{i}" for i in range(n))
    actions = tuple(f"a{seed}_{i}" for i in range(2 + (seed % 2)))
    scenarios = ("nominal", "phase_shift", "late_phase")
    next_by_state = {state: states[(index + 1) % n] for index, state in enumerate(states)}
    transition = {
        scenario: {state: {action: next_by_state[state] for action in actions} for state in states}
        for scenario in scenarios
    }
    observations = tuple(f"obs{seed}_{i}" for i in range(n))
    observe = {state: observations[index] for index, state in enumerate(states)}
    live_policy = {observation: actions[0] for observation in observations}
    starts = {
        "nominal": states[0],
        "phase_shift": states[rng.randrange(n)],
        "late_phase": states[rng.randrange(n)],
    }
    return ControlledSystem(
        system_id=f"challenge_cycle_seed{seed}",
        family="challenge",
        description="Generated action-insensitive recurrent system.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts=starts,
        transition=transition,
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset(states),
        viable_states=frozenset(states),
        channel_states=frozenset(states),
    )


def _open_loop(*, seed: int, rng: random.Random, observable: bool) -> ControlledSystem:
    need_count = 2 + (seed % 2)
    actions = tuple(f"route{seed}_{i}" for i in range(need_count))
    needs = tuple(f"need{seed}_{i}" for i in range(need_count))
    states = needs + (f"good{seed}", f"bad{seed}")
    good = states[-2]
    bad = states[-1]
    scenarios = ("nominal",) + tuple(f"need_scenario_{i}" for i in range(need_count))
    transition = {}
    for scenario in scenarios:
        by_state = {}
        for index, need in enumerate(needs):
            by_state[need] = {
                action: (good if action == actions[index] else bad)
                for action in actions
            }
        by_state[good] = {action: good for action in actions}
        by_state[bad] = {action: bad for action in actions}
        transition[scenario] = by_state

    if observable:
        observations = tuple(f"see_need{seed}_{i}" for i in range(need_count)) + (
            f"see_good{seed}",
            f"see_bad{seed}",
        )
        observe = {
            **{need: observations[index] for index, need in enumerate(needs)},
            good: observations[-2],
            bad: observations[-1],
        }
        live_policy = {
            **{observations[index]: actions[index] for index in range(need_count)},
            observations[-2]: actions[0],
            observations[-1]: actions[0],
        }
    else:
        observations = (f"blind{seed}",)
        observe = {state: observations[0] for state in states}
        live_policy = {observations[0]: actions[0]}

    starts = {"nominal": needs[0]}
    starts.update({f"need_scenario_{i}": need for i, need in enumerate(needs)})
    return ControlledSystem(
        system_id=f"challenge_{'feedback' if observable else 'open_loop'}_seed{seed}",
        family="challenge",
        description="Generated route-selection system.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts=starts,
        transition=transition,
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset({good}),
        viable_states=frozenset(needs + (good,)),
        channel_states=frozenset(needs + (good,)),
    )


def _reflexive(*, seed: int, rng: random.Random) -> ControlledSystem:
    del rng
    states = (
        f"ok{seed}",
        f"env_bad{seed}",
        f"sensor_bad{seed}",
        f"both_bad{seed}",
        f"fail{seed}",
    )
    ok, env_bad, sensor_bad, both_bad, fail = states
    actions = (f"idle{seed}", f"correct{seed}", f"repair{seed}")
    idle, correct, repair = actions
    transition = {
        ok: {idle: ok, correct: ok, repair: ok},
        env_bad: {idle: fail, correct: ok, repair: env_bad},
        sensor_bad: {idle: fail, correct: fail, repair: ok},
        both_bad: {idle: fail, correct: fail, repair: env_bad},
        fail: {idle: fail, correct: fail, repair: fail},
    }
    scenarios = ("nominal", "env", "sensor", "both")
    observations = (f"obs_ok{seed}", f"obs_env{seed}", f"obs_sensor{seed}", f"obs_fail{seed}")
    observe = {
        ok: observations[0],
        env_bad: observations[1],
        sensor_bad: observations[2],
        both_bad: observations[2],
        fail: observations[3],
    }
    return ControlledSystem(
        system_id=f"challenge_reflexive_seed{seed}",
        family="challenge",
        description="Generated reflexive channel-repair system.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={"nominal": ok, "env": env_bad, "sensor": sensor_bad, "both": both_bad},
        transition={scenario: transition for scenario in scenarios},
        observe=observe,
        live_policy={
            observations[0]: idle,
            observations[1]: correct,
            observations[2]: repair,
            observations[3]: idle,
        },
        target_states=frozenset({ok}),
        viable_states=frozenset({ok, env_bad, sensor_bad, both_bad}),
        channel_states=frozenset({ok, env_bad}),
        channel_challenge_scenarios=("sensor", "both"),
    )


def _joint(*, seed: int, rng: random.Random, cooperative: bool) -> ControlledSystem:
    del rng
    states = (f"neutral{seed}", f"threat{seed}", f"repair{seed}", f"capture{seed}", f"fail{seed}")
    neutral, threat, repair, capture, fail = states
    actions = (f"idle{seed}", f"help{seed}", f"capture{seed}")
    idle, help_action, capture_action = actions
    threat_idle_target = fail if cooperative else repair
    transition = {
        neutral: {idle: neutral, help_action: neutral, capture_action: capture},
        threat: {idle: threat_idle_target, help_action: repair, capture_action: capture},
        repair: {idle: repair, help_action: repair, capture_action: capture},
        capture: {idle: capture, help_action: capture, capture_action: capture},
        fail: {idle: fail, help_action: fail, capture_action: fail},
    }
    observations = tuple(f"j_obs_{seed}_{i}" for i in range(len(states)))
    observe = {state: observations[index] for index, state in enumerate(states)}
    live_policy = {
        observe[neutral]: idle,
        observe[threat]: help_action if cooperative else capture_action,
        observe[repair]: idle,
        observe[capture]: idle,
        observe[fail]: idle,
    }
    scenarios = ("nominal", "threat")
    return ControlledSystem(
        system_id=f"challenge_joint_{'positive' if cooperative else 'negative'}_seed{seed}",
        family="challenge",
        description="Generated joint-continuation effect system.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={"nominal": neutral, "threat": threat},
        transition={scenario: transition for scenario in scenarios},
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset({neutral, repair, capture}),
        viable_states=frozenset({neutral, threat, repair, capture}),
        channel_states=frozenset({neutral, threat, repair, capture}),
        joint_safe_states=frozenset({neutral, threat, repair}),
    )


def _pair_search(
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


def _classification_counts(metrics: list[DiamondMetrics]) -> dict[str, int]:
    return dict(sorted(Counter(metric.classification for metric in metrics).items()))


def _alert(metric: DiamondMetrics, kind: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "case_id": metric.case_id,
        "classification": metric.classification,
        "feedback_advantage": _frac(metric.feedback_advantage),
        "reflexive_advantage": _optional_frac(metric.reflexive_advantage),
        "observable_control_count": metric.observable_control_count,
        "joint_effect_delta": _optional_frac(metric.joint_effect_delta),
    }


def _positive_optional(value: Fraction | None) -> bool:
    return value is not None and value > 0


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _optional_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
