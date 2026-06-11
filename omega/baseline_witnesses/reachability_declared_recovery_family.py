"""Parameterized reachability/declaration recovery family.

This module generalizes the retained same-reachability witness without creating
new retained artifacts. For each nuisance-bit count ``k >= 1``, it compares a
channel whose reachable target support is keyed by declared bit ``d`` with
channels whose support is keyed by one nuisance bit ``n_i``. The reachability
profile is matched while declared recovery differs.
"""

from __future__ import annotations

import math


Channel = dict[str, tuple[str, ...]]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    preserve = preserve_declared_channel(states)
    control = nuisance_keyed_channel(states, nuisance_index)
    preserve_profile = reachability_profile(preserve, states)
    control_profile = reachability_profile(control, states)
    preserve_recovery = declared_d_recovery(preserve, states)
    control_recovery = declared_d_recovery(control, states)

    reachability_profiles_match = (
        preserve_profile["reachability_baseline_signature"]
        == control_profile["reachability_baseline_signature"]
    )
    preserve_recovers = bool(preserve_recovery["exact_declared_recovery"])
    control_recovers = bool(control_recovery["exact_declared_recovery"])

    return {
        "family_id": "same_reachability_different_declared_recovery_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "source_count": len(states),
        "support_count": 2**nuisance_bit_count,
        "preserve_channel_id": "keyed_by_declared_d",
        "control_channel_id": f"keyed_by_nuisance_n{nuisance_index + 1}",
        "preserve_profile": preserve_profile,
        "control_profile": control_profile,
        "reachability_profiles_match": reachability_profiles_match,
        "preserve_channel_exact_declared_recovery": preserve_recovers,
        "control_channel_exact_declared_recovery": control_recovers,
        "control_channel_ambiguous_observations": control_recovery["ambiguous_observations"],
        "family_case_status": (
            "same_reachability_different_declared_recovery"
            if reachability_profiles_match and preserve_recovers and not control_recovers
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


def preserve_declared_channel(states: tuple[str, ...]) -> Channel:
    return {
        source: tuple(target for target in states if target[0] == source[0])
        for source in states
    }


def nuisance_keyed_channel(states: tuple[str, ...], nuisance_index: int) -> Channel:
    if not states:
        raise ValueError("states must be nonempty")
    nuisance_bit_count = len(states[0]) - 1
    if nuisance_index < 0 or nuisance_index >= nuisance_bit_count:
        raise ValueError("nuisance_index out of range")
    coordinate = 1 + nuisance_index
    return {
        source: tuple(target for target in states if target[0] == source[coordinate])
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


def declared_d_recovery(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    for source in states:
        source_label = source[0]
        for target in channel[source]:
            target_observation = target[0]
            observation_sources.setdefault(target_observation, set()).add(source_label)

    ambiguous = {
        observation: sorted(labels)
        for observation, labels in observation_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_observations": ";".join(
            f"{observation}->{{{','.join(labels)}}}" for observation, labels in sorted(ambiguous.items())
        ),
        "observation_to_source_labels": ";".join(
            f"{observation}->{{{','.join(sorted(labels))}}}"
            for observation, labels in sorted(observation_sources.items())
        ),
    }


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
