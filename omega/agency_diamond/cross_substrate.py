"""Cross-substrate generated pilots for agency-diamond metrics.

This module keeps the operational-causal-diamond pilot exploratory.  The goal
is not to detect agency; it is to test whether the current finite profile keeps
its hierarchy and counterexample structure across several small source
grammars rather than only within the original challenge grammar.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
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
    counterexample_search,
)
from omega.agency_diamond.generated import relabel_with_decoys
from omega.agency_diamond.metrics import DiamondMetrics, evaluate_system
from omega.agency_diamond.model import ControlledSystem
from omega.agency_diamond.transport import presentation_report, transport_pilot


SUBSTRATES = ("boolean", "grid", "resource")
MODES_BY_SUBSTRATE = {
    "boolean": ("cycle", "feedback", "reflexive"),
    "grid": ("open_loop", "feedback", "reflexive"),
    "resource": ("joint_positive", "joint_negative"),
}
TRAIN_SEEDS = (211, 223)
HOLDOUT_SEEDS = (601, 607, 613)
CROSS_SUBSTRATE_HORIZONS = CHALLENGE_HORIZONS


@dataclass(frozen=True)
class CrossSubstrateCase:
    split: str
    substrate: str
    mode: str
    seed: int
    system: ControlledSystem


def cross_substrate_cases() -> tuple[CrossSubstrateCase, ...]:
    cases: list[CrossSubstrateCase] = []
    for split, seeds in (("train", TRAIN_SEEDS), ("holdout", HOLDOUT_SEEDS)):
        for substrate in SUBSTRATES:
            for mode in MODES_BY_SUBSTRATE[substrate]:
                for seed in seeds:
                    cases.append(
                        CrossSubstrateCase(
                            split=split,
                            substrate=substrate,
                            mode=mode,
                            seed=seed,
                            system=generate_cross_substrate_system(
                                substrate=substrate,
                                mode=mode,
                                seed=seed,
                            ),
                        )
                    )
    return tuple(cases)


def evaluate_cross_substrate_cases() -> list[DiamondMetrics]:
    metrics: list[DiamondMetrics] = []
    for case in cross_substrate_cases():
        for horizon in CROSS_SUBSTRATE_HORIZONS:
            metrics.append(
                evaluate_system(
                    case.system,
                    horizon=horizon,
                    case_id=(
                        f"{case.split}__{case.substrate}__{case.mode}"
                        f"__seed{case.seed}_h{horizon}"
                    ),
                )
            )
    return metrics


def cross_substrate_summary() -> dict[str, Any]:
    cases = cross_substrate_cases()
    metrics = evaluate_cross_substrate_cases()
    train = [metric for metric in metrics if metric.case_id.startswith("train__")]
    holdout = [metric for metric in metrics if metric.case_id.startswith("holdout__")]

    collisions = find_baseline_collisions(holdout)
    collision_status = required_collision_status(collisions)
    search = counterexample_search(holdout)
    collapse_alerts = collapse_alerts_for(holdout)
    adversarial = adversarial_probe_summary(holdout)
    transport = transport_cross_substrate()
    holdout_classes = set(metric.classification for metric in holdout)
    holdout_substrates = _substrates_by_split(cases, split="holdout")

    gates = {
        "multiple_substrates_tested": len(holdout_substrates) >= 3,
        "holdout_classes_cover_required": REQUIRED_HOLDOUT_CLASSES <= holdout_classes,
        "required_baseline_collisions_found": all(collision_status.values()),
        "counterexample_search_witnesses_found": all(witness.passed for witness in search),
        "adversarial_probes_found": all(adversarial["probe_status"].values()),
        "no_collapse_alerts": not collapse_alerts,
        "transport_invariance_passed": bool(transport["all_transport_checks_passed"]),
    }

    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "generator": {
            "substrates": list(SUBSTRATES),
            "modes_by_substrate": {
                substrate: list(modes)
                for substrate, modes in MODES_BY_SUBSTRATE.items()
            },
            "train_seeds": list(TRAIN_SEEDS),
            "holdout_seeds": list(HOLDOUT_SEEDS),
            "horizons": list(CROSS_SUBSTRATE_HORIZONS),
        },
        "case_counts": {
            "systems": len(cases),
            "metric_cases": len(metrics),
            "train_metric_cases": len(train),
            "holdout_metric_cases": len(holdout),
        },
        "train_classification_counts": _classification_counts(train),
        "holdout_classification_counts": _classification_counts(holdout),
        "holdout_classification_by_substrate": _classification_by_substrate(holdout),
        "holdout_required_classes": sorted(REQUIRED_HOLDOUT_CLASSES),
        "required_baseline_collision_status": collision_status,
        "baseline_collision_count": len(collisions),
        "baseline_collision_witnesses": [witness.as_dict() for witness in collisions],
        "counterexample_search": [witness.as_dict() for witness in search],
        "adversarial": adversarial,
        "collapse_alerts": collapse_alerts,
        "transport": transport,
        "decision_gate": gates,
    }


def generate_cross_substrate_system(
    *,
    substrate: str,
    mode: str,
    seed: int,
) -> ControlledSystem:
    rng = random.Random((seed * 104729) + sum(ord(ch) for ch in substrate + mode))
    if substrate == "boolean":
        return _boolean_system(mode=mode, seed=seed, rng=rng)
    if substrate == "grid":
        return _grid_system(mode=mode, seed=seed, rng=rng)
    if substrate == "resource":
        return _resource_system(mode=mode, seed=seed, rng=rng)
    raise ValueError(f"unknown cross-substrate source: {substrate}")


def adversarial_probe_summary(metrics: list[DiamondMetrics]) -> dict[str, Any]:
    """Report non-handpicked collapse probes over held-out metric outcomes."""

    witnesses = [
        _pair_search(
            metrics,
            name="cross_substrate_same_substrate_separates_feedback",
            left_pred=lambda m: m.feedback_advantage == 0,
            right_pred=lambda m: m.feedback_advantage > 0,
            same_substrate=True,
            details=lambda left, right: {
                "substrate": _substrate_of(left),
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="cross_substrate_control_without_feedback_found",
            left_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage == 0,
            right_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage > 0,
            same_substrate=False,
            details=lambda left, right: {
                "left_control_reach_count": left.control_reach_count,
                "right_control_reach_count": right.control_reach_count,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="cross_substrate_feedback_without_reflexive_found",
            left_pred=lambda m: m.feedback_advantage > 0 and not _positive_optional(m.reflexive_advantage),
            right_pred=lambda m: m.feedback_advantage > 0 and _positive_optional(m.reflexive_advantage),
            same_substrate=False,
            details=lambda left, right: {
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "left_reflexive_advantage": _optional_frac(left.reflexive_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
                "right_reflexive_advantage": _optional_frac(right.reflexive_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="cross_substrate_joint_sign_not_live_success",
            left_pred=lambda m: m.live_maintenance_score == 1
            and m.joint_effect_delta is not None
            and m.joint_effect_delta > 0,
            right_pred=lambda m: m.live_maintenance_score == 1
            and m.joint_effect_delta is not None
            and m.joint_effect_delta < 0,
            same_substrate=True,
            details=lambda left, right: {
                "substrate": _substrate_of(left),
                "shared_live_maintenance": _frac(left.live_maintenance_score),
                "left_joint_effect": _optional_frac(left.joint_effect_delta),
                "right_joint_effect": _optional_frac(right.joint_effect_delta),
            },
        ),
        _pair_search(
            metrics,
            name="cross_substrate_recurrence_not_feedback",
            left_pred=lambda m: m.recurrence_detected and m.feedback_advantage == 0,
            right_pred=lambda m: m.recurrence_detected and m.feedback_advantage > 0,
            same_substrate=False,
            details=lambda left, right: {
                "left_recurrence": left.recurrence_detected,
                "right_recurrence": right.recurrence_detected,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
    ]
    substrate_class_counts = _classification_by_substrate(metrics)
    probe_status = {
        witness.name: witness.passed
        for witness in witnesses
    }
    probe_status["each_substrate_has_multiple_classifications"] = all(
        len(counts) >= 2 for counts in substrate_class_counts.values()
    )
    return {
        "probe_status": probe_status,
        "witnesses": [witness.as_dict() for witness in witnesses],
        "classification_by_substrate": substrate_class_counts,
    }


def transport_cross_substrate() -> dict[str, Any]:
    systems = [
        case.system
        for case in cross_substrate_cases()
        if case.split == "holdout"
    ]
    sample = systems[:18]
    relabel_reports = []
    identity_reports = []
    for index, system in enumerate(sample):
        relabeled = relabel_with_decoys(system, seed=11000 + index)
        exact_profile = tuple(
            evaluate_system(system, horizon=horizon).classification
            for horizon in CROSS_SUBSTRATE_HORIZONS
        )
        relabeled_profile = tuple(
            evaluate_system(relabeled, horizon=horizon).classification
            for horizon in CROSS_SUBSTRATE_HORIZONS
        )
        relabel_reports.append(
            {
                "system_id": system.system_id,
                "relabeled_system_id": relabeled.system_id,
                "profile_preserved": exact_profile == relabeled_profile,
            }
        )
        identity_reports.append(
            presentation_report(
                system,
                {state: state for state in system.states},
                case_id=f"{system.system_id}__identity",
            ).as_dict()
        )

    quotient_controls = transport_pilot()
    checks = {
        "relabel_profiles_preserved": all(
            report["profile_preserved"] for report in relabel_reports
        ),
        "identity_presentations_preserve_profiles": all(
            report["quotient_constructible"] and report["profile_preserved"] is True
            for report in identity_reports
        ),
        "quotient_controls_passed": bool(
            quotient_controls["all_transport_checks_passed"]
        ),
    }
    return {
        "checks": checks,
        "all_transport_checks_passed": all(checks.values()),
        "relabel_reports": relabel_reports,
        "identity_report_count": len(identity_reports),
        "quotient_controls": quotient_controls,
    }


def _boolean_system(*, mode: str, seed: int, rng: random.Random) -> ControlledSystem:
    if mode == "cycle":
        return _boolean_cycle(seed=seed, rng=rng)
    if mode == "feedback":
        return _boolean_route(seed=seed, observable=True)
    if mode == "reflexive":
        return _boolean_reflexive(seed=seed)
    raise ValueError(f"unsupported boolean mode: {mode}")


def _grid_system(*, mode: str, seed: int, rng: random.Random) -> ControlledSystem:
    del rng
    if mode == "open_loop":
        return _grid_route(seed=seed, observable=False)
    if mode == "feedback":
        return _grid_route(seed=seed, observable=True)
    if mode == "reflexive":
        return _grid_reflexive(seed=seed)
    raise ValueError(f"unsupported grid mode: {mode}")


def _resource_system(*, mode: str, seed: int, rng: random.Random) -> ControlledSystem:
    del rng
    if mode == "joint_positive":
        return _resource_corridor(seed=seed, cooperative=True)
    if mode == "joint_negative":
        return _resource_corridor(seed=seed, cooperative=False)
    raise ValueError(f"unsupported resource mode: {mode}")


def _boolean_cycle(*, seed: int, rng: random.Random) -> ControlledSystem:
    states = tuple(f"b{seed}_{index:02b}" for index in range(4))
    actions = (f"hold{seed}", f"flip{seed}")
    scenarios = ("nominal", "phase_a", "phase_b")
    order = list(states)
    rng.shuffle(order)
    successor = {state: order[(index + 1) % len(order)] for index, state in enumerate(order)}
    transition = {
        scenario: {
            state: {action: successor[state] for action in actions}
            for state in states
        }
        for scenario in scenarios
    }
    observations = tuple(f"bit_obs{seed}_{index}" for index in range(len(states)))
    observe = {state: observations[index] for index, state in enumerate(states)}
    starts = {
        "nominal": order[0],
        "phase_a": order[1],
        "phase_b": order[2],
    }
    return ControlledSystem(
        system_id=f"cross_boolean_cycle_seed{seed}",
        family="agency_diamond_cross_substrate",
        description="Boolean-encoded action-insensitive recurrent substrate.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts=starts,
        transition=transition,
        observe=observe,
        live_policy={observation: actions[0] for observation in observations},
        target_states=frozenset(states),
        viable_states=frozenset(states),
        channel_states=frozenset(states),
    )


def _boolean_route(*, seed: int, observable: bool) -> ControlledSystem:
    states = (
        f"b{seed}_00_need_zero",
        f"b{seed}_01_need_one",
        f"b{seed}_10_good",
        f"b{seed}_11_bad",
    )
    need_zero, need_one, good, bad = states
    actions = (f"set0_{seed}", f"set1_{seed}")
    set_zero, set_one = actions
    transition = {
        need_zero: {set_zero: good, set_one: bad},
        need_one: {set_zero: bad, set_one: good},
        good: {set_zero: good, set_one: good},
        bad: {set_zero: bad, set_one: bad},
    }
    scenarios = ("nominal", "need_zero", "need_one")
    if observable:
        observations = (
            f"see_zero_{seed}",
            f"see_one_{seed}",
            f"see_good_{seed}",
            f"see_bad_{seed}",
        )
        observe = {
            need_zero: observations[0],
            need_one: observations[1],
            good: observations[2],
            bad: observations[3],
        }
        live_policy = {
            observations[0]: set_zero,
            observations[1]: set_one,
            observations[2]: set_zero,
            observations[3]: set_zero,
        }
    else:
        observations = (f"blind_bits_{seed}",)
        observe = {state: observations[0] for state in states}
        live_policy = {observations[0]: set_zero}
    return ControlledSystem(
        system_id=f"cross_boolean_{'feedback' if observable else 'open'}_seed{seed}",
        family="agency_diamond_cross_substrate",
        description="Boolean-bit route-selection substrate.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": need_zero,
            "need_zero": need_zero,
            "need_one": need_one,
        },
        transition={scenario: transition for scenario in scenarios},
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset({good}),
        viable_states=frozenset({need_zero, need_one, good}),
        channel_states=frozenset({need_zero, need_one, good}),
    )


def _boolean_reflexive(*, seed: int) -> ControlledSystem:
    states = (
        f"b{seed}_000_ok",
        f"b{seed}_001_env",
        f"b{seed}_010_sensor",
        f"b{seed}_011_both",
        f"b{seed}_111_fail",
    )
    ok, env_bad, sensor_bad, both_bad, fail = states
    actions = (f"noop_{seed}", f"correct_{seed}", f"repair_sensor_{seed}")
    noop, correct, repair = actions
    transition = {
        ok: {noop: ok, correct: ok, repair: ok},
        env_bad: {noop: fail, correct: ok, repair: env_bad},
        sensor_bad: {noop: fail, correct: fail, repair: ok},
        both_bad: {noop: fail, correct: fail, repair: env_bad},
        fail: {noop: fail, correct: fail, repair: fail},
    }
    observations = (
        f"bit_ok_{seed}",
        f"bit_env_{seed}",
        f"bit_sensor_{seed}",
        f"bit_fail_{seed}",
    )
    observe = {
        ok: observations[0],
        env_bad: observations[1],
        sensor_bad: observations[2],
        both_bad: observations[2],
        fail: observations[3],
    }
    return ControlledSystem(
        system_id=f"cross_boolean_reflexive_seed{seed}",
        family="agency_diamond_cross_substrate",
        description="Boolean-bit self-channel repair substrate.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=("nominal", "env", "sensor", "both"),
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": ok,
            "env": env_bad,
            "sensor": sensor_bad,
            "both": both_bad,
        },
        transition={scenario: transition for scenario in ("nominal", "env", "sensor", "both")},
        observe=observe,
        live_policy={
            observations[0]: noop,
            observations[1]: correct,
            observations[2]: repair,
            observations[3]: noop,
        },
        target_states=frozenset({ok}),
        viable_states=frozenset({ok, env_bad, sensor_bad, both_bad}),
        channel_states=frozenset({ok, env_bad}),
        channel_challenge_scenarios=("sensor", "both"),
    )


def _grid_route(*, seed: int, observable: bool) -> ControlledSystem:
    states = (
        f"g{seed}_home",
        f"g{seed}_left_gate",
        f"g{seed}_right_gate",
        f"g{seed}_goal",
        f"g{seed}_pit",
    )
    home, left_gate, right_gate, goal, pit = states
    actions = (f"west_{seed}", f"east_{seed}", f"wait_{seed}")
    west, east, wait = actions
    transition = {
        home: {west: goal, east: goal, wait: home},
        left_gate: {west: goal, east: pit, wait: pit},
        right_gate: {west: pit, east: goal, wait: pit},
        goal: {west: goal, east: goal, wait: goal},
        pit: {west: pit, east: pit, wait: pit},
    }
    scenarios = ("nominal", "left_storm", "right_storm")
    if observable:
        observations = (
            f"grid_home_{seed}",
            f"grid_left_{seed}",
            f"grid_right_{seed}",
            f"grid_goal_{seed}",
            f"grid_pit_{seed}",
        )
        observe = {
            home: observations[0],
            left_gate: observations[1],
            right_gate: observations[2],
            goal: observations[3],
            pit: observations[4],
        }
        live_policy = {
            observations[0]: wait,
            observations[1]: west,
            observations[2]: east,
            observations[3]: wait,
            observations[4]: wait,
        }
    else:
        observations = (f"grid_blind_{seed}",)
        observe = {state: observations[0] for state in states}
        live_policy = {observations[0]: west}
    return ControlledSystem(
        system_id=f"cross_grid_{'feedback' if observable else 'open'}_seed{seed}",
        family="agency_diamond_cross_substrate",
        description="Grid-gate route substrate.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": home,
            "left_storm": left_gate,
            "right_storm": right_gate,
        },
        transition={scenario: transition for scenario in scenarios},
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset({home, goal}),
        viable_states=frozenset({home, left_gate, right_gate, goal}),
        channel_states=frozenset({home, left_gate, right_gate, goal}),
    )


def _grid_reflexive(*, seed: int) -> ControlledSystem:
    states = (
        f"g{seed}_station",
        f"g{seed}_track_blocked",
        f"g{seed}_sensor_cut",
        f"g{seed}_both_faults",
        f"g{seed}_sink",
    )
    station, blocked, sensor_cut, both_faults, sink = states
    actions = (f"wait_{seed}", f"clear_track_{seed}", f"restore_sensor_{seed}")
    wait, clear, restore = actions
    transition = {
        station: {wait: station, clear: station, restore: station},
        blocked: {wait: sink, clear: station, restore: blocked},
        sensor_cut: {wait: sink, clear: sink, restore: station},
        both_faults: {wait: sink, clear: sink, restore: blocked},
        sink: {wait: sink, clear: sink, restore: sink},
    }
    scenarios = ("nominal", "blocked", "sensor", "both")
    observations = (
        f"grid_station_{seed}",
        f"grid_blocked_{seed}",
        f"grid_sensor_{seed}",
        f"grid_sink_{seed}",
    )
    observe = {
        station: observations[0],
        blocked: observations[1],
        sensor_cut: observations[2],
        both_faults: observations[2],
        sink: observations[3],
    }
    return ControlledSystem(
        system_id=f"cross_grid_reflexive_seed{seed}",
        family="agency_diamond_cross_substrate",
        description="Grid maintenance channel-repair substrate.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": station,
            "blocked": blocked,
            "sensor": sensor_cut,
            "both": both_faults,
        },
        transition={scenario: transition for scenario in scenarios},
        observe=observe,
        live_policy={
            observations[0]: wait,
            observations[1]: clear,
            observations[2]: restore,
            observations[3]: wait,
        },
        target_states=frozenset({station}),
        viable_states=frozenset({station, blocked, sensor_cut, both_faults}),
        channel_states=frozenset({station, blocked}),
        channel_challenge_scenarios=("sensor", "both"),
    )


def _resource_corridor(*, seed: int, cooperative: bool) -> ControlledSystem:
    states = (
        f"r{seed}_common",
        f"r{seed}_scarcity",
        f"r{seed}_shared_repair",
        f"r{seed}_captured",
        f"r{seed}_collapse",
    )
    common, scarcity, shared_repair, captured, collapse = states
    actions = (f"wait_{seed}", f"share_{seed}", f"capture_{seed}")
    wait, share, capture = actions
    scarcity_wait = collapse if cooperative else shared_repair
    transition = {
        common: {wait: common, share: common, capture: captured},
        scarcity: {wait: scarcity_wait, share: shared_repair, capture: captured},
        shared_repair: {wait: shared_repair, share: shared_repair, capture: captured},
        captured: {wait: captured, share: captured, capture: captured},
        collapse: {wait: collapse, share: collapse, capture: collapse},
    }
    observations = tuple(f"resource_obs_{seed}_{index}" for index in range(len(states)))
    observe = {state: observations[index] for index, state in enumerate(states)}
    live_policy = {
        observe[common]: wait,
        observe[scarcity]: share if cooperative else capture,
        observe[shared_repair]: wait,
        observe[captured]: wait,
        observe[collapse]: wait,
    }
    return ControlledSystem(
        system_id=f"cross_resource_{'positive' if cooperative else 'negative'}_seed{seed}",
        family="agency_diamond_cross_substrate",
        description="Resource-corridor joint-continuation substrate.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=("nominal", "scarcity"),
        nominal_scenario="nominal",
        scenario_starts={"nominal": common, "scarcity": scarcity},
        transition={scenario: transition for scenario in ("nominal", "scarcity")},
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset({common, shared_repair, captured}),
        viable_states=frozenset({common, scarcity, shared_repair, captured}),
        channel_states=frozenset({common, scarcity, shared_repair, captured}),
        joint_safe_states=frozenset({common, scarcity, shared_repair}),
    )


def _pair_search(
    metrics: list[DiamondMetrics],
    *,
    name: str,
    left_pred,
    right_pred,
    same_substrate: bool,
    details,
) -> SearchWitness:
    for left in metrics:
        if not left_pred(left):
            continue
        for right in metrics:
            if left.case_id == right.case_id or not right_pred(right):
                continue
            if same_substrate and _substrate_of(left) != _substrate_of(right):
                continue
            return SearchWitness(
                name=name,
                passed=True,
                left_case=left.case_id,
                right_case=right.case_id,
                details=details(left, right),
            )
    return SearchWitness(name=name, passed=False, left_case=None, right_case=None, details={})


def _substrates_by_split(
    cases: tuple[CrossSubstrateCase, ...],
    *,
    split: str,
) -> set[str]:
    return {case.substrate for case in cases if case.split == split}


def _substrate_of(metric: DiamondMetrics) -> str:
    parts = metric.case_id.split("__")
    if len(parts) < 3:
        return "unknown"
    return parts[1]


def _classification_counts(metrics: list[DiamondMetrics]) -> dict[str, int]:
    return dict(sorted(Counter(metric.classification for metric in metrics).items()))


def _classification_by_substrate(metrics: list[DiamondMetrics]) -> dict[str, dict[str, int]]:
    by_substrate: dict[str, Counter[str]] = defaultdict(Counter)
    for metric in metrics:
        by_substrate[_substrate_of(metric)][metric.classification] += 1
    return {
        substrate: dict(sorted(counts.items()))
        for substrate, counts in sorted(by_substrate.items())
    }


def _positive_optional(value: Fraction | None) -> bool:
    return value is not None and value > 0


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _optional_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
