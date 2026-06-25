"""Prespecified null battery for the operational-causal-diamond pilot."""

from __future__ import annotations

from omega.agency_diamond.model import ControlledSystem, EvaluationCase


MID_SCALE_HORIZONS = (1, 2, 3, 4, 6)


def canonical_battery() -> tuple[ControlledSystem, ...]:
    return (
        passive_attractor(),
        driven_cycle(),
        open_loop_controller(),
        thermostat(),
        adaptive_controller(),
        self_restoring_controller(),
        cooperative_controller(),
        dominant_horizon_controller(),
    )


def midscale_cases() -> tuple[EvaluationCase, ...]:
    cases = []
    for system in canonical_battery():
        for horizon in MID_SCALE_HORIZONS:
            cases.append(
                EvaluationCase(
                    case_id=f"{system.system_id}_h{horizon}",
                    system=system,
                    horizon=horizon,
                )
            )
    return tuple(cases)


def _same_transition(states: tuple[str, ...], actions: tuple[str, ...], next_by_state: dict[str, str]):
    return {state: {action: next_by_state[state] for action in actions} for state in states}


def passive_attractor() -> ControlledSystem:
    states = ("stable",)
    actions = ("idle", "push")
    scenarios = ("nominal", "small_disturbance")
    transition = {
        scenario: _same_transition(states, actions, {"stable": "stable"})
        for scenario in scenarios
    }
    return ControlledSystem(
        system_id="passive_attractor",
        family="passive",
        description="Stable persistence with no actionable control distinction.",
        states=states,
        actions=actions,
        observations=("same",),
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={"nominal": "stable", "small_disturbance": "stable"},
        transition=transition,
        observe={"stable": "same"},
        live_policy={"same": "idle"},
        target_states=frozenset({"stable"}),
        viable_states=frozenset({"stable"}),
        channel_states=frozenset({"stable"}),
    )


def driven_cycle() -> ControlledSystem:
    states = ("a", "b", "c")
    actions = ("idle", "poke")
    scenarios = ("nominal", "phase_shift")
    next_by_state = {"a": "b", "b": "c", "c": "a"}
    transition = {
        scenario: _same_transition(states, actions, next_by_state)
        for scenario in scenarios
    }
    return ControlledSystem(
        system_id="driven_cycle",
        family="driven",
        description="Recurrent cycle whose actions do not affect the cycle.",
        states=states,
        actions=actions,
        observations=states,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={"nominal": "a", "phase_shift": "b"},
        transition=transition,
        observe={state: state for state in states},
        live_policy={state: "idle" for state in states},
        target_states=frozenset(states),
        viable_states=frozenset(states),
        channel_states=frozenset(states),
    )


def open_loop_controller() -> ControlledSystem:
    states = ("start", "needs_left", "needs_right", "good", "bad")
    actions = ("left", "right")
    scenarios = ("nominal", "right_required")
    base = {
        "start": {"left": "good", "right": "bad"},
        "needs_left": {"left": "good", "right": "bad"},
        "needs_right": {"left": "bad", "right": "good"},
        "good": {"left": "good", "right": "good"},
        "bad": {"left": "bad", "right": "bad"},
    }
    return ControlledSystem(
        system_id="open_loop_controller",
        family="open_loop",
        description="Actions matter, but the observation interface cannot select the needed action.",
        states=states,
        actions=actions,
        observations=("constant",),
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={"nominal": "needs_left", "right_required": "needs_right"},
        transition={"nominal": base, "right_required": base},
        observe={state: "constant" for state in states},
        live_policy={"constant": "left"},
        target_states=frozenset({"good"}),
        viable_states=frozenset({"start", "needs_left", "needs_right", "good"}),
        channel_states=frozenset({"start", "needs_left", "needs_right", "good"}),
    )


def thermostat() -> ControlledSystem:
    states = ("ok", "cold", "hot", "fail")
    actions = ("idle", "heat", "cool")
    transitions = _temperature_transitions()
    return ControlledSystem(
        system_id="thermostat",
        family="feedback",
        description="Thin feedback restores temperature but does not face channel repair.",
        states=states,
        actions=actions,
        observations=("ok", "cold", "hot", "fail"),
        scenarios=("nominal", "cold_start", "hot_start"),
        nominal_scenario="nominal",
        scenario_starts={"nominal": "ok", "cold_start": "cold", "hot_start": "hot"},
        transition={scenario: transitions for scenario in ("nominal", "cold_start", "hot_start")},
        observe={state: state for state in states},
        live_policy={"ok": "idle", "cold": "heat", "hot": "cool", "fail": "idle"},
        target_states=frozenset({"ok"}),
        viable_states=frozenset({"ok", "cold", "hot"}),
        channel_states=frozenset({"ok", "cold", "hot"}),
    )


def adaptive_controller() -> ControlledSystem:
    states = ("ok", "drift_left", "drift_right", "unstable")
    actions = ("idle", "correct_left", "correct_right")
    transition = {
        "ok": {"idle": "ok", "correct_left": "ok", "correct_right": "ok"},
        "drift_left": {
            "idle": "unstable",
            "correct_left": "ok",
            "correct_right": "unstable",
        },
        "drift_right": {
            "idle": "unstable",
            "correct_left": "unstable",
            "correct_right": "ok",
        },
        "unstable": {"idle": "unstable", "correct_left": "unstable", "correct_right": "unstable"},
    }
    scenarios = ("nominal", "left_drift", "right_drift")
    return ControlledSystem(
        system_id="adaptive_controller",
        family="feedback",
        description="Feedback selects correction under perturbation but does not repair its own channel.",
        states=states,
        actions=actions,
        observations=("ok", "left", "right", "unstable"),
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": "ok",
            "left_drift": "drift_left",
            "right_drift": "drift_right",
        },
        transition={scenario: transition for scenario in scenarios},
        observe={
            "ok": "ok",
            "drift_left": "left",
            "drift_right": "right",
            "unstable": "unstable",
        },
        live_policy={
            "ok": "idle",
            "left": "correct_left",
            "right": "correct_right",
            "unstable": "idle",
        },
        target_states=frozenset({"ok"}),
        viable_states=frozenset({"ok", "drift_left", "drift_right"}),
        channel_states=frozenset({"ok", "drift_left", "drift_right"}),
    )


def self_restoring_controller() -> ControlledSystem:
    states = ("ok", "env_bad", "sensor_damaged", "both_bad", "fail")
    actions = ("idle", "correct_env", "repair_sensor")
    transition = {
        "ok": {"idle": "ok", "correct_env": "ok", "repair_sensor": "ok"},
        "env_bad": {"idle": "fail", "correct_env": "ok", "repair_sensor": "env_bad"},
        "sensor_damaged": {
            "idle": "fail",
            "correct_env": "fail",
            "repair_sensor": "ok",
        },
        "both_bad": {
            "idle": "fail",
            "correct_env": "fail",
            "repair_sensor": "env_bad",
        },
        "fail": {"idle": "fail", "correct_env": "fail", "repair_sensor": "fail"},
    }
    scenarios = ("nominal", "env_perturbation", "sensor_damage", "combined_damage")
    return ControlledSystem(
        system_id="self_restoring_controller",
        family="reflexive",
        description="Live feedback can repair the observation channel that enables later correction.",
        states=states,
        actions=actions,
        observations=("ok", "env_bad", "sensor_fail", "fail"),
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": "ok",
            "env_perturbation": "env_bad",
            "sensor_damage": "sensor_damaged",
            "combined_damage": "both_bad",
        },
        transition={scenario: transition for scenario in scenarios},
        observe={
            "ok": "ok",
            "env_bad": "env_bad",
            "sensor_damaged": "sensor_fail",
            "both_bad": "sensor_fail",
            "fail": "fail",
        },
        live_policy={
            "ok": "idle",
            "env_bad": "correct_env",
            "sensor_fail": "repair_sensor",
            "fail": "idle",
        },
        target_states=frozenset({"ok"}),
        viable_states=frozenset({"ok", "env_bad", "sensor_damaged", "both_bad"}),
        channel_states=frozenset({"ok", "env_bad"}),
        channel_challenge_scenarios=("sensor_damage", "combined_damage"),
    )


def cooperative_controller() -> ControlledSystem:
    states = ("neutral", "threat", "repaired", "fail")
    transition = {
        "neutral": {"idle": "neutral", "help": "neutral", "exploit": "fail"},
        "threat": {"idle": "fail", "help": "repaired", "exploit": "fail"},
        "repaired": {"idle": "repaired", "help": "repaired", "exploit": "fail"},
        "fail": {"idle": "fail", "help": "fail", "exploit": "fail"},
    }
    scenarios = ("nominal", "shared_threat")
    return ControlledSystem(
        system_id="cooperative_controller",
        family="joint_positive",
        description="Feedback preserves own and joint continuation under shared threat.",
        states=states,
        actions=("idle", "help", "exploit"),
        observations=("neutral", "threat", "repaired", "fail"),
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={"nominal": "neutral", "shared_threat": "threat"},
        transition={scenario: transition for scenario in scenarios},
        observe={state: state for state in states},
        live_policy={
            "neutral": "idle",
            "threat": "help",
            "repaired": "idle",
            "fail": "idle",
        },
        target_states=frozenset({"neutral", "repaired"}),
        viable_states=frozenset({"neutral", "threat", "repaired"}),
        channel_states=frozenset({"neutral", "threat", "repaired"}),
        joint_safe_states=frozenset({"neutral", "threat", "repaired"}),
    )


def dominant_horizon_controller() -> ControlledSystem:
    states = ("neutral", "threat", "captured", "protected", "collapse")
    actions = ("idle", "protect", "capture")
    transition = {
        "neutral": {"idle": "neutral", "protect": "neutral", "capture": "captured"},
        "threat": {"idle": "protected", "protect": "protected", "capture": "captured"},
        "captured": {"idle": "captured", "protect": "captured", "capture": "captured"},
        "protected": {"idle": "protected", "protect": "protected", "capture": "captured"},
        "collapse": {"idle": "collapse", "protect": "collapse", "capture": "collapse"},
    }
    scenarios = ("nominal", "external_threat")
    return ControlledSystem(
        system_id="dominant_horizon_controller",
        family="joint_negative",
        description="Feedback selects a high-leverage capture action that preserves own target but contracts joint continuation.",
        states=states,
        actions=actions,
        observations=("neutral", "threat", "captured", "protected", "collapse"),
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={"nominal": "neutral", "external_threat": "threat"},
        transition={scenario: transition for scenario in scenarios},
        observe={state: state for state in states},
        live_policy={
            "neutral": "idle",
            "threat": "capture",
            "captured": "idle",
            "protected": "idle",
            "collapse": "idle",
        },
        target_states=frozenset({"neutral", "captured", "protected"}),
        viable_states=frozenset({"neutral", "threat", "captured", "protected"}),
        channel_states=frozenset({"neutral", "threat", "captured", "protected"}),
        joint_safe_states=frozenset({"neutral", "threat", "protected"}),
    )


def _temperature_transitions() -> dict[str, dict[str, str]]:
    return {
        "ok": {"idle": "ok", "heat": "hot", "cool": "cold"},
        "cold": {"idle": "fail", "heat": "ok", "cool": "fail"},
        "hot": {"idle": "fail", "heat": "fail", "cool": "ok"},
        "fail": {"idle": "fail", "heat": "fail", "cool": "fail"},
    }
