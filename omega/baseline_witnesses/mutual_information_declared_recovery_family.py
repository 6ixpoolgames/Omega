"""Parameterized mutual-information/declaration recovery family.

This module generalizes the retained same-mutual-information witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares a deterministic channel that outputs declared bit ``d`` with channels
that output one nuisance bit ``n_i``. The information profile is matched while
declared recovery differs.
"""

from __future__ import annotations

import math


Channel = dict[str, str]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    declared = declared_channel(states)
    nuisance = nuisance_channel(states, nuisance_index)
    declared_information = information_profile(declared, states)
    nuisance_information = information_profile(nuisance, states)
    declared_recovery = declared_d_recovery(declared, states)
    nuisance_recovery = declared_d_recovery(nuisance, states)

    information_signatures_match = (
        declared_information["information_baseline_signature"]
        == nuisance_information["information_baseline_signature"]
    )
    declared_recovers = bool(declared_recovery["exact_declared_recovery"])
    nuisance_recovers = bool(nuisance_recovery["exact_declared_recovery"])

    return {
        "family_id": "same_mutual_information_different_declared_recovery_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "source_count": len(states),
        "declared_channel_id": "transmit_declared_d",
        "nuisance_channel_id": f"transmit_nuisance_n{nuisance_index + 1}",
        "declared_information": declared_information,
        "nuisance_information": nuisance_information,
        "information_signatures_match": information_signatures_match,
        "declared_channel_exact_declared_recovery": declared_recovers,
        "nuisance_channel_exact_declared_recovery": nuisance_recovers,
        "nuisance_channel_ambiguous_outputs": nuisance_recovery["ambiguous_outputs"],
        "family_case_status": (
            "same_mutual_information_different_declared_recovery"
            if information_signatures_match and declared_recovers and not nuisance_recovers
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


def declared_channel(states: tuple[str, ...]) -> Channel:
    return {source: source[0] for source in states}


def nuisance_channel(states: tuple[str, ...], nuisance_index: int) -> Channel:
    if not states:
        raise ValueError("states must be nonempty")
    nuisance_bit_count = len(states[0]) - 1
    if nuisance_index < 0 or nuisance_index >= nuisance_bit_count:
        raise ValueError("nuisance_index out of range")
    coordinate = 1 + nuisance_index
    return {source: source[coordinate] for source in states}


def information_profile(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    output_weights = output_weight_counts(channel)
    conditional_entropy = 0.0
    output_entropy = entropy_from_weights(output_weights.values())
    mutual_information = output_entropy - conditional_entropy
    capacity = deterministic_output_capacity_bits(channel)
    source_entropy = math.log2(len(states))
    return {
        "source_count": len(states),
        "source_entropy_bits": f"{source_entropy:.6f}",
        "output_support_size": len(output_weights),
        "output_support": ";".join(sorted(output_weights)),
        "output_weight_signature": signature(output_weights),
        "output_entropy_bits": f"{output_entropy:.6f}",
        "conditional_output_entropy_bits": f"{conditional_entropy:.6f}",
        "mutual_information_source_output_bits": f"{mutual_information:.6f}",
        "deterministic_output_capacity_bits": f"{capacity:.6f}",
        "information_baseline_signature": (
            f"I:{mutual_information:.6f}|"
            f"C:{capacity:.6f}|"
            f"H_Y:{output_entropy:.6f}|"
            f"H_Y_given_X:{conditional_entropy:.6f}"
        ),
    }


def declared_d_recovery(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    output_sources: dict[str, set[str]] = {}
    for source in states:
        output_sources.setdefault(channel[source], set()).add(source[0])

    ambiguous = {
        output: sorted(labels)
        for output, labels in output_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(output_sources) == ["0", "1"],
        "ambiguous_outputs": ";".join(
            f"{output}->{{{','.join(labels)}}}" for output, labels in sorted(ambiguous.items())
        ),
        "output_to_source_labels": ";".join(
            f"{output}->{{{','.join(sorted(labels))}}}"
            for output, labels in sorted(output_sources.items())
        ),
    }


def output_weight_counts(channel: Channel) -> dict[str, int]:
    weights: dict[str, int] = {}
    for output in channel.values():
        weights[output] = weights.get(output, 0) + 1
    return weights


def deterministic_output_capacity_bits(channel: Channel) -> float:
    image_size = len(set(channel.values()))
    if image_size <= 0:
        return 0.0
    return math.log2(image_size)


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
