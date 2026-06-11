"""Parameterized control-reach/declaration recovery family.

This module generalizes the retained same-control-reach witness without creating
new retained artifacts. For each nuisance-bit count ``k >= 1``, it compares a
deterministic controlled one-step system that carries declared bit ``d`` in the
declared recovery bit with systems that carry one nuisance bit ``n_i``.

The finite control-reach summary is matched while declared recovery differs.
"""

from __future__ import annotations


CONTROLS = ("drive_0", "drive_1")
System = dict[tuple[str, str], str]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    declared = declared_system(states)
    nuisance = nuisance_system(states, nuisance_index)
    declared_profile = control_reach_profile(declared, states)
    nuisance_profile = control_reach_profile(nuisance, states)
    declared_recovery = declared_d_recovery(declared, states)
    nuisance_recovery = declared_d_recovery(nuisance, states)

    control_reach_signatures_match = (
        declared_profile["control_reach_baseline_signature"]
        == nuisance_profile["control_reach_baseline_signature"]
    )
    declared_recovers = bool(declared_recovery["exact_declared_recovery"])
    nuisance_recovers = bool(nuisance_recovery["exact_declared_recovery"])

    return {
        "family_id": "same_control_reach_different_declared_recovery_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "source_count": len(states),
        "declared_system_id": "control_with_declared_d_carried",
        "nuisance_system_id": f"control_with_nuisance_n{nuisance_index + 1}_carried",
        "declared_control_reach_profile": declared_profile,
        "nuisance_control_reach_profile": nuisance_profile,
        "control_reach_signatures_match": control_reach_signatures_match,
        "declared_system_exact_declared_recovery": declared_recovers,
        "nuisance_system_exact_declared_recovery": nuisance_recovers,
        "nuisance_system_ambiguous_observations": nuisance_recovery[
            "ambiguous_target_observations"
        ],
        "family_case_status": (
            "same_control_reach_different_declared_recovery"
            if control_reach_signatures_match and declared_recovers and not nuisance_recovers
            else "family_case_failed"
        ),
    }


def run_family(*, max_nuisance_bits: int) -> list[dict[str, object]]:
    if max_nuisance_bits < 1:
        raise ValueError("max_nuisance_bits must be >= 1")
    return [
        run_family_case(nuisance_bit_count=count, nuisance_index=index)
        for count in range(1, max_nuisance_bits + 1)
        for index in range(count)
    ]


def state_space(nuisance_bit_count: int) -> tuple[str, ...]:
    if nuisance_bit_count < 1:
        raise ValueError("nuisance_bit_count must be >= 1")
    bit_count = 1 + nuisance_bit_count
    return tuple(format(value, f"0{bit_count}b") for value in range(2**bit_count))


def declared_system(states: tuple[str, ...]) -> System:
    return {
        (source, control): control_bit(control) + source[0]
        for source in states
        for control in CONTROLS
    }


def nuisance_system(states: tuple[str, ...], nuisance_index: int) -> System:
    if not states:
        raise ValueError("states must be nonempty")
    nuisance_bit_count = len(states[0]) - 1
    if nuisance_index < 0 or nuisance_index >= nuisance_bit_count:
        raise ValueError("nuisance_index out of range")
    coordinate = 1 + nuisance_index
    return {
        (source, control): control_bit(control) + source[coordinate]
        for source in states
        for control in CONTROLS
    }


def control_reach_profile(system: System, states: tuple[str, ...]) -> dict[str, object]:
    global_support = sorted(set(system.values()))
    target_count_by_source = {
        source: len({system[(source, control)] for control in CONTROLS})
        for source in states
    }
    target_count_by_control = {
        control: len({system[(source, control)] for source in states})
        for control in CONTROLS
    }
    target_control_bits_by_control = {
        control: ",".join(sorted({system[(source, control)][0] for source in states}))
        for control in CONTROLS
    }
    return {
        "source_count": len(states),
        "control_count": len(CONTROLS),
        "transition_edge_count": len(states) * len(CONTROLS),
        "deterministic_transition": 1,
        "global_target_support_size": len(global_support),
        "global_target_support": ";".join(global_support),
        "per_source_reachable_target_count_signature": signature(target_count_by_source),
        "target_count_by_control_signature": signature(target_count_by_control),
        "target_control_bits_by_control_signature": signature(
            target_control_bits_by_control
        ),
        "control_reach_baseline_signature": (
            f"N:{len(states)}|"
            f"C:{len(CONTROLS)}|"
            f"E:{len(states) * len(CONTROLS)}|"
            "deterministic:1|"
            f"G:{len(global_support)}|"
            f"support:{';'.join(global_support)}|"
            f"per_source:{signature(target_count_by_source)}|"
            f"per_control:{signature(target_count_by_control)}|"
            f"control_bits:{signature(target_control_bits_by_control)}"
        ),
    }


def declared_d_recovery(system: System, states: tuple[str, ...]) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    for source in states:
        for control in CONTROLS:
            target = system[(source, control)]
            observation_sources.setdefault(target[1], set()).add(source[0])

    ambiguous = {
        observation: sorted(labels)
        for observation, labels in observation_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_target_observations": ";".join(
            f"{observation}->{{{','.join(labels)}}}"
            for observation, labels in sorted(ambiguous.items())
        ),
        "observation_to_source_labels": ";".join(
            f"{observation}->{{{','.join(sorted(labels))}}}"
            for observation, labels in sorted(observation_sources.items())
        ),
    }


def control_bit(control_id: str) -> str:
    if control_id == "drive_0":
        return "0"
    if control_id == "drive_1":
        return "1"
    raise ValueError(f"unknown control_id: {control_id}")


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))
