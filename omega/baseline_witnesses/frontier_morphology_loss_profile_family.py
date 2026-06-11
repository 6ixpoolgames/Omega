"""Parameterized frontier-morphology/loss-profile family.

This module generalizes the retained same-frontier-morphology witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares a channel preserving declared viability bit ``v`` with a channel
flipping ``v``.

The coarse one-step frontier morphology summaries match exactly. The declared
horizon-local loss profile over currently viable sources differs.
"""

from __future__ import annotations

import math


Channel = dict[str, tuple[str, ...]]


def run_family_case(*, nuisance_bit_count: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    preserve = preserve_declared_channel(states)
    flip = flip_declared_channel(states)
    preserve_morphology = frontier_morphology_profile(preserve, states)
    flip_morphology = frontier_morphology_profile(flip, states)
    preserve_loss = loss_profile(preserve, states)
    flip_loss = loss_profile(flip, states)

    morphology_signatures_match = (
        preserve_morphology["frontier_morphology_signature"]
        == flip_morphology["frontier_morphology_signature"]
    )
    loss_profile_differs = preserve_loss["loss_signature"] != flip_loss["loss_signature"]

    return {
        "family_id": "same_frontier_morphology_different_declared_loss_profile_family",
        "nuisance_bit_count": nuisance_bit_count,
        "source_count": len(states),
        "support_count": 2**nuisance_bit_count,
        "preserve_channel_id": "preserve_declared_v",
        "flip_channel_id": "flip_declared_v",
        "declared_viability_predicate": "state first bit v = 1",
        "loss_rule": "source viable and no viable target in declared one-step support",
        "preserve_morphology": preserve_morphology,
        "flip_morphology": flip_morphology,
        "morphology_signatures_match": morphology_signatures_match,
        "preserve_loss": preserve_loss,
        "flip_loss": flip_loss,
        "loss_profile_differs": loss_profile_differs,
        "family_case_status": (
            "same_frontier_morphology_different_declared_loss_profile"
            if morphology_signatures_match and loss_profile_differs
            else "family_case_failed"
        ),
    }


def run_family(*, max_nuisance_bits: int) -> list[dict[str, object]]:
    if max_nuisance_bits < 1:
        raise ValueError("max_nuisance_bits must be >= 1")
    return [
        run_family_case(nuisance_bit_count=count)
        for count in range(1, max_nuisance_bits + 1)
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


def flip_declared_channel(states: tuple[str, ...]) -> Channel:
    return {
        source: tuple(target for target in states if target[0] != source[0])
        for source in states
    }


def frontier_morphology_profile(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    support_counts = {source: len(channel[source]) for source in states}
    entropies = {source: uniform_entropy_bits(len(channel[source])) for source in states}
    viable_target_counts = {
        source: sum(int(is_viable(target)) for target in channel[source])
        for source in states
    }
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
        "viable_target_count_multiset": multiset_signature(viable_target_counts.values()),
        "frontier_morphology_signature": (
            f"N:{len(states)}|"
            f"E:{edge_count}|"
            f"G:{len(global_target_weights)}|"
            f"W:{signature(global_target_weights)}|"
            f"C:{signature(support_counts)}|"
            f"H:{float_signature(entropies)}|"
            f"V:{multiset_signature(viable_target_counts.values())}|"
            f"H_global:{global_entropy:.6f}"
        ),
    }


def loss_profile(channel: Channel, states: tuple[str, ...]) -> dict[str, object]:
    viable_sources = [source for source in states if is_viable(source)]
    losses = {
        source: int(not any(is_viable(target) for target in channel[source]))
        for source in viable_sources
    }
    return {
        "viable_source_count": len(viable_sources),
        "loss_count": sum(losses.values()),
        "loss_signature": signature(losses),
    }


def is_viable(state: str) -> bool:
    return state[0] == "1"


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


def multiset_signature(values: object) -> str:
    return ";".join(str(value) for value in sorted(values))
