"""State-presentation transport probes for agency-diamond pilots."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from omega.agency_diamond.examples import MID_SCALE_HORIZONS, open_loop_controller, thermostat
from omega.agency_diamond.metrics import evaluate_system
from omega.agency_diamond.model import ControlledSystem, State, validate_system


@dataclass(frozen=True)
class PresentationReport:
    case_id: str
    system_id: str
    total: bool
    observation_compatible: bool
    target_saturated: bool
    viable_saturated: bool
    channel_saturated: bool
    joint_saturated: bool
    transition_congruent: bool
    quotient_constructible: bool
    profile_preserved: bool | None
    profile_preservation_details: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "system_id": self.system_id,
            "total": self.total,
            "observation_compatible": self.observation_compatible,
            "target_saturated": self.target_saturated,
            "viable_saturated": self.viable_saturated,
            "channel_saturated": self.channel_saturated,
            "joint_saturated": self.joint_saturated,
            "transition_congruent": self.transition_congruent,
            "quotient_constructible": self.quotient_constructible,
            "profile_preserved": self.profile_preserved,
            "profile_preservation_details": self.profile_preservation_details,
        }


def presentation_report(
    system: ControlledSystem,
    presentation: Mapping[State, str],
    *,
    case_id: str,
) -> PresentationReport:
    validate_system(system)
    flags = _compatibility_flags(system, presentation)
    quotient_constructible = all(flags.values())

    details: dict[str, object] = {}
    profile_preserved: bool | None = None
    if quotient_constructible:
        quotient = quotient_system(system, presentation, system_id=f"{system.system_id}__quotient")
        exact_profile = tuple(
            evaluate_system(system, horizon=horizon).classification
            for horizon in MID_SCALE_HORIZONS
        )
        abstract_profile = tuple(
            evaluate_system(quotient, horizon=horizon).classification
            for horizon in MID_SCALE_HORIZONS
        )
        profile_preserved = exact_profile == abstract_profile
        details = {
            "exact_profile": list(exact_profile),
            "abstract_profile": list(abstract_profile),
            "abstract_state_count": len(quotient.states),
            "exact_state_count": len(system.states),
        }

    return PresentationReport(
        case_id=case_id,
        system_id=system.system_id,
        total=flags["total"],
        observation_compatible=flags["observation_compatible"],
        target_saturated=flags["target_saturated"],
        viable_saturated=flags["viable_saturated"],
        channel_saturated=flags["channel_saturated"],
        joint_saturated=flags["joint_saturated"],
        transition_congruent=flags["transition_congruent"],
        quotient_constructible=quotient_constructible,
        profile_preserved=profile_preserved,
        profile_preservation_details=details,
    )


def quotient_system(
    system: ControlledSystem,
    presentation: Mapping[State, str],
    *,
    system_id: str,
) -> ControlledSystem:
    flags = _compatibility_flags(system, presentation)
    if not all(flags.values()):
        raise ValueError(f"presentation is not quotient-constructible: {flags}")

    blocks = tuple(dict.fromkeys(presentation[state] for state in system.states))
    representative = {
        block: next(state for state in system.states if presentation[state] == block)
        for block in blocks
    }
    transition = {}
    for scenario in system.scenarios:
        transition[scenario] = {
            block: {
                action: presentation[system.transition[scenario][representative[block]][action]]
                for action in system.actions
            }
            for block in blocks
        }
    observe = {
        block: system.observe[representative[block]]
        for block in blocks
    }

    return replace(
        system,
        system_id=system_id,
        description=f"Quotient presentation of {system.system_id}.",
        states=blocks,
        scenario_starts={
            scenario: presentation[state]
            for scenario, state in system.scenario_starts.items()
        },
        transition=transition,
        observe=observe,
        target_states=frozenset(
            block for block in blocks if representative[block] in system.target_states
        ),
        viable_states=frozenset(
            block for block in blocks if representative[block] in system.viable_states
        ),
        channel_states=frozenset(
            block for block in blocks if representative[block] in system.channel_states
        ),
        joint_safe_states=(
            None
            if system.joint_safe_states is None
            else frozenset(
                block for block in blocks if representative[block] in system.joint_safe_states
            )
        ),
    )


def transport_pilot() -> dict[str, object]:
    open_loop = open_loop_controller()
    thermostat_system = thermostat()

    positive = presentation_report(
        open_loop,
        {
            "start": "pre_left",
            "needs_left": "pre_left",
            "needs_right": "needs_right",
            "good": "good",
            "bad": "bad",
        },
        case_id="open_loop_sound_merge_start_needs_left",
    )
    bad_transition = presentation_report(
        open_loop,
        {
            "start": "start",
            "needs_left": "need",
            "needs_right": "need",
            "good": "good",
            "bad": "bad",
        },
        case_id="open_loop_unsound_merge_incompatible_needs",
    )
    bad_observation = presentation_report(
        thermostat_system,
        {
            "ok": "ok",
            "cold": "temperature_error",
            "hot": "temperature_error",
            "fail": "fail",
        },
        case_id="thermostat_unsound_merge_cold_hot",
    )
    reports = (positive, bad_transition, bad_observation)
    checks = {
        "positive_quotient_constructible": positive.quotient_constructible,
        "positive_profile_preserved": positive.profile_preserved is True,
        "incompatible_need_merge_rejected": not bad_transition.quotient_constructible,
        "cold_hot_merge_rejected": not bad_observation.quotient_constructible,
    }
    return {
        "reports": [report.as_dict() for report in reports],
        "checks": checks,
        "all_transport_checks_passed": all(checks.values()),
    }


def _compatibility_flags(
    system: ControlledSystem,
    presentation: Mapping[State, str],
) -> dict[str, bool]:
    total = set(presentation) == set(system.states)
    observation_compatible = total and _fiber_constant(system.states, presentation, system.observe)
    target_saturated = total and _fiber_saturated(system.states, presentation, system.target_states)
    viable_saturated = total and _fiber_saturated(system.states, presentation, system.viable_states)
    channel_saturated = total and _fiber_saturated(system.states, presentation, system.channel_states)
    joint_saturated = (
        True
        if system.joint_safe_states is None
        else total and _fiber_saturated(system.states, presentation, system.joint_safe_states)
    )
    transition_congruent = total and _transition_congruent(system, presentation)
    return {
        "total": total,
        "observation_compatible": observation_compatible,
        "target_saturated": target_saturated,
        "viable_saturated": viable_saturated,
        "channel_saturated": channel_saturated,
        "joint_saturated": joint_saturated,
        "transition_congruent": transition_congruent,
    }


def _fiber_constant(
    states: tuple[State, ...],
    presentation: Mapping[State, str],
    values: Mapping[State, str],
) -> bool:
    seen: dict[str, str] = {}
    for state in states:
        block = presentation[state]
        value = values[state]
        if block in seen and seen[block] != value:
            return False
        seen[block] = value
    return True


def _fiber_saturated(
    states: tuple[State, ...],
    presentation: Mapping[State, str],
    subset: frozenset[State],
) -> bool:
    seen: dict[str, bool] = {}
    for state in states:
        block = presentation[state]
        value = state in subset
        if block in seen and seen[block] != value:
            return False
        seen[block] = value
    return True


def _transition_congruent(
    system: ControlledSystem,
    presentation: Mapping[State, str],
) -> bool:
    representatives: dict[tuple[str, str, str], str] = {}
    for scenario in system.scenarios:
        for state in system.states:
            block = presentation[state]
            for action in system.actions:
                key = (scenario, block, action)
                target_block = presentation[system.transition[scenario][state][action]]
                if key in representatives and representatives[key] != target_block:
                    return False
                representatives[key] = target_block
    return True
