"""Parameterized entropy/recovery-profile family.

This module generalizes the retained same-entropy witness without creating new
retained artifacts. For each nuisance-bit count ``k >= 1``, it compares a
channel preserving declared coordinate ``D_0`` with channels preserving each
nuisance coordinate ``D_i``.

The entropy-style summaries match exactly, while the declared recovery profile
over the coordinate-distinction panel changes.
"""

from __future__ import annotations

import math


Channel = dict[str, tuple[str, ...]]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    control_coordinate = 1 + nuisance_index
    declared = coordinate_keyed_channel(states, coordinate=0)
    control = coordinate_keyed_channel(states, coordinate=control_coordinate)
    declared_entropy = entropy_profile(declared, states)
    control_entropy = entropy_profile(control, states)
    declared_recovery = recovery_profile(declared, states)
    control_recovery = recovery_profile(control, states)

    entropy_signatures_match = (
        declared_entropy["entropy_baseline_signature"]
        == control_entropy["entropy_baseline_signature"]
    )
    recovery_profile_differs = (
        declared_recovery["recovery_profile_signature"]
        != control_recovery["recovery_profile_signature"]
    )

    return {
        "family_id": "same_entropy_different_recovery_profile_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "source_count": len(states),
        "support_count": 2**nuisance_bit_count,
        "declared_channel_id": "preserve_D_0",
        "control_channel_id": f"preserve_D_{control_coordinate}",
        "declared_distinction_panel": ";".join(distinction_id(index) for index in range(len(states[0]))),
        "declared_entropy": declared_entropy,
        "control_entropy": control_entropy,
        "entropy_signatures_match": entropy_signatures_match,
        "declared_recovery": declared_recovery,
        "control_recovery": control_recovery,
        "recovery_profile_differs": recovery_profile_differs,
        "family_case_status": (
            "same_entropy_different_recovery_profile"
            if entropy_signatures_match and recovery_profile_differs
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


def coordinate_keyed_channel(states: tuple[str, ...], *, coordinate: int) -> Channel:
    if not states:
        raise ValueError("states must be nonempty")
    if coordinate < 0 or coordinate >= len(states[0]):
        raise ValueError("coordinate out of range")
    return {
        source: tuple(target for target in states if target[coordinate] == source[coordinate])
        for source in states
    }


def entropy_profile(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    support_counts = {source: len(channel[source]) for source in states}
    entropies = {source: uniform_entropy_bits(len(channel[source])) for source in states}
    global_target_weights = target_weight_counts(channel)
    global_entropy = entropy_from_weights(global_target_weights.values())
    edge_count = sum(support_counts.values())
    return {
        "source_count": len(states),
        "edge_count": edge_count,
        "global_target_support_size": len(global_target_weights),
        "global_target_support": ";".join(sorted(global_target_weights)),
        "global_target_weight_signature": signature(global_target_weights),
        "global_target_entropy_bits": f"{global_entropy:.6f}",
        "per_source_support_count_signature": signature(support_counts),
        "per_source_entropy_bits_signature": float_signature(entropies),
        "min_per_source_entropy_bits": f"{min(entropies.values()):.6f}",
        "max_per_source_entropy_bits": f"{max(entropies.values()):.6f}",
        "entropy_baseline_signature": (
            f"N:{len(states)}|"
            f"E:{edge_count}|"
            f"G:{len(global_target_weights)}|"
            f"W:{signature(global_target_weights)}|"
            f"C:{signature(support_counts)}|"
            f"H:{float_signature(entropies)}|"
            f"H_global:{global_entropy:.6f}"
        ),
    }


def recovery_profile(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    recovered: list[str] = []
    failed: list[str] = []
    for coordinate in range(len(states[0])):
        recovery = recovery_for_coordinate(channel, states, coordinate=coordinate)
        target = recovered if recovery["exact_declared_recovery"] else failed
        target.append(distinction_id(coordinate))

    return {
        "recovered_distinctions": ";".join(recovered),
        "failed_distinctions": ";".join(failed),
        "recovered_distinction_count": len(recovered),
        "failed_distinction_count": len(failed),
        "recovery_profile_signature": (
            f"recovered:{';'.join(recovered)}|failed:{';'.join(failed)}"
        ),
    }


def recovery_for_coordinate(
    channel: Channel, states: tuple[str, ...], *, coordinate: int
) -> dict[str, object]:
    if not states:
        raise ValueError("states must be nonempty")
    if coordinate < 0 or coordinate >= len(states[0]):
        raise ValueError("coordinate out of range")

    observation_sources: dict[str, set[str]] = {}
    for source in states:
        source_label = source[coordinate]
        for target in channel[source]:
            target_observation = target[coordinate]
            observation_sources.setdefault(target_observation, set()).add(source_label)

    ambiguous = {
        observation: sorted(labels)
        for observation, labels in observation_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_observations": ";".join(
            f"{observation}->{{{','.join(labels)}}}"
            for observation, labels in sorted(ambiguous.items())
        ),
        "observation_to_source_labels": ";".join(
            f"{observation}->{{{','.join(sorted(labels))}}}"
            for observation, labels in sorted(observation_sources.items())
        ),
    }


def distinction_id(coordinate: int) -> str:
    return f"D_{coordinate}"


def target_weight_counts(channel: Channel) -> dict[str, int]:
    weights: dict[str, int] = {}
    for support in channel.values():
        for target in support:
            weights[target] = weights.get(target, 0) + 1
    return weights


def uniform_entropy_bits(support_size: int) -> float:
    if support_size <= 0:
        return 0.0
    return math.log2(support_size)


def entropy_from_weights(weights: object) -> float:
    values = list(weights)
    total = sum(values)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for weight in values:
        probability = weight / total
        entropy -= probability * math.log2(probability)
    return entropy


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))
