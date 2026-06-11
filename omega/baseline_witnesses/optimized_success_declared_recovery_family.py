"""Parameterized optimized-success/declaration recovery family.

This module generalizes the retained optimized-success witness without creating
new retained artifacts. For each nuisance-bit count ``k >= 1``, it compares a
channel whose target coordinate 0 carries declared bit ``d`` with channels
whose target coordinate ``i`` carries ``d`` for each nuisance coordinate.

Both channels are exactly recoverable by an optimized observation over the full
coordinate panel. Only the coordinate-0 channel is recoverable by the declared
observation.
"""

from __future__ import annotations

import math


Channel = dict[str, tuple[str, ...]]


def run_family_case(*, nuisance_bit_count: int, shifted_coordinate: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    declared = coordinate_keyed_channel(states, coordinate=0)
    shifted = coordinate_keyed_channel(states, coordinate=shifted_coordinate)
    declared_profile = reachability_profile(declared, states)
    shifted_profile = reachability_profile(shifted, states)
    declared_recovery = recovery_for_observation(declared, states, observation_coordinate=0)
    shifted_declared_recovery = recovery_for_observation(shifted, states, observation_coordinate=0)
    declared_optimized = optimized_recovery(declared, states)
    shifted_optimized = optimized_recovery(shifted, states)

    baseline_profiles_match = (
        declared_profile["reachability_baseline_signature"]
        == shifted_profile["reachability_baseline_signature"]
    )
    same_optimized_success = (
        declared_optimized["exact_optimized_recovery"]
        and shifted_optimized["exact_optimized_recovery"]
    )

    return {
        "family_id": "same_optimized_success_different_declared_recovery_family",
        "nuisance_bit_count": nuisance_bit_count,
        "shifted_coordinate": shifted_coordinate,
        "source_count": len(states),
        "support_count": 2**nuisance_bit_count,
        "declared_channel_id": "d_in_target_coordinate_0",
        "shifted_channel_id": f"d_in_target_coordinate_{shifted_coordinate}",
        "declared_observation_id": "O_0",
        "optimized_candidate_panel": ";".join(observation_id(index) for index in range(len(states[0]))),
        "declared_profile": declared_profile,
        "shifted_profile": shifted_profile,
        "baseline_profiles_match": baseline_profiles_match,
        "same_optimized_success": same_optimized_success,
        "declared_channel_exact_declared_recovery": declared_recovery["exact_recovery"],
        "shifted_channel_exact_declared_recovery": shifted_declared_recovery["exact_recovery"],
        "declared_channel_exact_optimized_recovery": declared_optimized["exact_optimized_recovery"],
        "shifted_channel_exact_optimized_recovery": shifted_optimized["exact_optimized_recovery"],
        "declared_channel_best_observation_id": declared_optimized["best_observation_id"],
        "shifted_channel_best_observation_id": shifted_optimized["best_observation_id"],
        "shifted_channel_declared_ambiguous_observations": shifted_declared_recovery[
            "ambiguous_observations"
        ],
        "family_case_status": (
            "same_optimized_success_different_declared_recovery"
            if (
                baseline_profiles_match
                and same_optimized_success
                and declared_recovery["exact_recovery"]
                and not shifted_declared_recovery["exact_recovery"]
            )
            else "family_case_failed"
        ),
    }


def run_family(*, max_nuisance_bits: int) -> list[dict[str, object]]:
    if max_nuisance_bits < 1:
        raise ValueError("max_nuisance_bits must be >= 1")
    return [
        run_family_case(nuisance_bit_count=count, shifted_coordinate=coordinate)
        for count in range(1, max_nuisance_bits + 1)
        for coordinate in range(1, count + 1)
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
        source: tuple(target for target in states if target[coordinate] == source[0])
        for source in states
    }


def reachability_profile(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    support_counts = {source: len(channel[source]) for source in states}
    entropies = {source: support_entropy_bits(channel[source]) for source in states}
    global_support = sorted({target for support in channel.values() for target in support})
    target_weights = target_weight_counts(channel)
    edge_count = sum(support_counts.values())
    return {
        "source_count": len(states),
        "edge_count": edge_count,
        "global_target_support_size": len(global_support),
        "global_target_support": ";".join(global_support),
        "target_weight_signature": signature(target_weights),
        "per_source_reachable_count_signature": signature(support_counts),
        "min_per_source_reachable_count": min(support_counts.values()),
        "max_per_source_reachable_count": max(support_counts.values()),
        "per_source_entropy_bits_signature": float_signature(entropies),
        "min_per_source_entropy_bits": f"{min(entropies.values()):.6f}",
        "max_per_source_entropy_bits": f"{max(entropies.values()):.6f}",
        "reachability_baseline_signature": (
            f"N:{len(states)}|"
            f"E:{edge_count}|"
            f"G:{len(global_support)}|"
            f"W:{signature(target_weights)}|"
            f"C:{signature(support_counts)}|"
            f"H:{float_signature(entropies)}"
        ),
    }


def optimized_recovery(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    exact_observations = [
        observation_id(coordinate)
        for coordinate in range(len(states[0]))
        if recovery_for_observation(
            channel, states, observation_coordinate=coordinate
        )["exact_recovery"]
    ]
    return {
        "exact_optimized_recovery": bool(exact_observations),
        "best_observation_id": exact_observations[0] if exact_observations else "",
        "all_exact_observations": ";".join(exact_observations),
    }


def recovery_for_observation(
    channel: Channel, states: tuple[str, ...], *, observation_coordinate: int
) -> dict[str, object]:
    if not states:
        raise ValueError("states must be nonempty")
    if observation_coordinate < 0 or observation_coordinate >= len(states[0]):
        raise ValueError("observation_coordinate out of range")

    observation_sources: dict[str, set[str]] = {}
    for source in states:
        source_label = source[0]
        for target in channel[source]:
            target_observation = target[observation_coordinate]
            observation_sources.setdefault(target_observation, set()).add(source_label)

    ambiguous = {
        observation: sorted(labels)
        for observation, labels in observation_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_observations": ";".join(
            f"{observation}->{{{','.join(labels)}}}"
            for observation, labels in sorted(ambiguous.items())
        ),
        "observation_to_source_labels": ";".join(
            f"{observation}->{{{','.join(sorted(labels))}}}"
            for observation, labels in sorted(observation_sources.items())
        ),
    }


def observation_id(coordinate: int) -> str:
    return f"O_{coordinate}"


def target_weight_counts(channel: Channel) -> dict[str, int]:
    weights: dict[str, int] = {}
    for support in channel.values():
        for target in support:
            weights[target] = weights.get(target, 0) + 1
    return weights


def support_entropy_bits(support: tuple[str, ...]) -> float:
    if not support:
        return 0.0
    probability = 1.0 / len(support)
    return -sum(probability * math.log2(probability) for _target in support)


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))
