"""Parameterized marginal-success/joint-success family.

This module generalizes the retained same-marginal-success witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares two weighted observation channels over sources ``abn...``. Both
channels match Bayes-best recovery success for declared single-bit distinctions
``A`` and ``B`` while differing on declared joint distinction ``AB``.

The nuisance bits are present in the source carrier but are not part of the
declared joint distinction scored here.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from fractions import Fraction


WeightedChannel = dict[str, dict[str, int]]


def run_family_case(*, nuisance_bit_count: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    correlated = correlated_channel(states)
    independent = independent_channel(states)
    correlated_baseline = channel_baseline(correlated, states)
    independent_baseline = channel_baseline(independent, states)
    correlated_recovery = recovery_profile(correlated, states)
    independent_recovery = recovery_profile(independent, states)

    baseline_signatures_match = (
        correlated_baseline["channel_baseline_signature"]
        == independent_baseline["channel_baseline_signature"]
    )
    same_marginal_success = (
        correlated_recovery["marginal_success_vector"]
        == independent_recovery["marginal_success_vector"]
    )
    different_joint_success = (
        correlated_recovery["D_AB_bayes_success_fraction"]
        != independent_recovery["D_AB_bayes_success_fraction"]
    )

    return {
        "family_id": "same_marginal_success_different_joint_success_family",
        "nuisance_bit_count": nuisance_bit_count,
        "source_count": len(states),
        "correlated_channel_id": "correlated_both_or_none",
        "independent_channel_id": "independent_bit_masks",
        "declared_marginal_distinctions": "D_A;D_B",
        "declared_joint_distinction": "D_AB",
        "correlated_baseline": correlated_baseline,
        "independent_baseline": independent_baseline,
        "baseline_signatures_match": baseline_signatures_match,
        "correlated_recovery": correlated_recovery,
        "independent_recovery": independent_recovery,
        "same_marginal_success": same_marginal_success,
        "different_joint_success": different_joint_success,
        "family_case_status": (
            "same_marginal_success_different_joint_success"
            if baseline_signatures_match and same_marginal_success and different_joint_success
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
    if nuisance_bit_count < 0:
        raise ValueError("nuisance_bit_count must be >= 0")
    bit_count = 2 + nuisance_bit_count
    return tuple(format(value, f"0{bit_count}b") for value in range(2**bit_count))


def correlated_channel(states: tuple[str, ...]) -> WeightedChannel:
    return {
        source: {
            f"both0:{declared_pair(source)}": 1,
            f"both1:{declared_pair(source)}": 1,
            "none0": 1,
            "none1": 1,
        }
        for source in states
    }


def independent_channel(states: tuple[str, ...]) -> WeightedChannel:
    return {
        source: {
            f"both:{declared_pair(source)}": 1,
            f"a_only:{source[0]}": 1,
            f"b_only:{source[1]}": 1,
            "none": 1,
        }
        for source in states
    }


def channel_baseline(channel: WeightedChannel, states: tuple[str, ...]) -> dict[str, object]:
    support_counts = {source: len(channel[source]) for source in states}
    weight_totals = {source: sum(channel[source].values()) for source in states}
    entropies = {source: support_entropy_bits(channel[source]) for source in states}
    edge_count = sum(support_counts.values())
    return {
        "source_count": len(states),
        "edge_count": edge_count,
        "per_source_support_count_signature": signature(support_counts),
        "per_source_weight_total_signature": signature(weight_totals),
        "per_source_entropy_bits_signature": float_signature(entropies),
        "min_per_source_entropy_bits": f"{min(entropies.values()):.6f}",
        "max_per_source_entropy_bits": f"{max(entropies.values()):.6f}",
        "channel_baseline_signature": (
            f"N:{len(states)}|"
            f"E:{edge_count}|"
            f"C:{signature(support_counts)}|"
            f"W:{signature(weight_totals)}|"
            f"H:{float_signature(entropies)}"
        ),
    }


def recovery_profile(channel: WeightedChannel, states: tuple[str, ...]) -> dict[str, object]:
    a_success = bayes_success(channel, states, lambda state: state[0])
    b_success = bayes_success(channel, states, lambda state: state[1])
    joint_success = bayes_success(channel, states, declared_pair)
    return {
        "D_A_bayes_success_fraction": fraction_text(a_success["success"]),
        "D_B_bayes_success_fraction": fraction_text(b_success["success"]),
        "D_AB_bayes_success_fraction": fraction_text(joint_success["success"]),
        "D_A_success_weight": a_success["success_weight"],
        "D_B_success_weight": b_success["success_weight"],
        "D_AB_success_weight": joint_success["success_weight"],
        "total_weight": a_success["total_weight"],
        "marginal_success_vector": (
            f"D_A:{fraction_text(a_success['success'])};"
            f"D_B:{fraction_text(b_success['success'])}"
        ),
    }


def bayes_success(
    channel: WeightedChannel,
    states: tuple[str, ...],
    labeler: Callable[[str], str],
) -> dict[str, object]:
    target_label_weights: dict[str, dict[str, int]] = {}
    total_weight = 0
    for source in states:
        label = labeler(source)
        for target, weight in channel[source].items():
            target_label_weights.setdefault(target, {})
            target_label_weights[target][label] = (
                target_label_weights[target].get(label, 0) + weight
            )
            total_weight += weight

    success_weight = sum(max(label_weights.values()) for label_weights in target_label_weights.values())
    return {
        "success": Fraction(success_weight, total_weight),
        "success_weight": success_weight,
        "total_weight": total_weight,
        "target_count": len(target_label_weights),
    }


def declared_pair(state: str) -> str:
    return state[:2]


def support_entropy_bits(weights_by_target: dict[str, int]) -> float:
    total = sum(weights_by_target.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for weight in weights_by_target.values():
        probability = weight / total
        entropy -= probability * math.log2(probability)
    return entropy


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))
