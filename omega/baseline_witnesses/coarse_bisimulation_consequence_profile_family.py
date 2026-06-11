"""Parameterized coarse-bisimulation/consequence-profile family.

This module generalizes the retained same-coarse-bisimulation witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares an expanded panel keyed by declared bit ``d`` against expanded panels
keyed by each nuisance bit ``n_i``.

The coarse unit-observation partition and exact profile counts match. The
actual allowed/blocked pair signatures differ.
"""

from __future__ import annotations

from itertools import combinations


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    declared_profile = profile_signature(states, coordinate=0)
    nuisance_profile = profile_signature(states, coordinate=1 + nuisance_index)
    baseline_controls_match = baseline_metrics(states, declared_profile) == baseline_metrics(
        states,
        nuisance_profile,
    )
    profile_counts_match = profile_counts(declared_profile) == profile_counts(nuisance_profile)
    profile_signatures_differ = (
        declared_profile["allowed_pair_signature"] != nuisance_profile["allowed_pair_signature"]
        and declared_profile["blocked_pair_signature"] != nuisance_profile["blocked_pair_signature"]
    )

    return {
        "family_id": "same_coarse_bisimulation_different_consequence_profile_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "state_count": len(states),
        "transition_edge_count": len(states),
        "coarse_panel_id": "coarse_unit_observation",
        "declared_panel_id": "declared_d_expanded_panel",
        "nuisance_panel_id": f"declared_n{nuisance_index + 1}_expanded_panel",
        "baseline_controls_match": baseline_controls_match,
        "profile_counts_match": profile_counts_match,
        "profile_signatures_differ": profile_signatures_differ,
        "declared_profile": declared_profile,
        "nuisance_profile": nuisance_profile,
        "family_case_status": (
            "same_coarse_bisimulation_different_consequence_profile"
            if baseline_controls_match and profile_counts_match and profile_signatures_differ
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


def baseline_metrics(states: tuple[str, ...], profile: dict[str, object]) -> dict[str, object]:
    return {
        "state_count": len(states),
        "transition_edge_count": len(states),
        "coarse_block_count": 1,
        "coarse_block_size_signature": str(len(states)),
        "expanded_pair_count": profile["pair_count"],
        "expanded_allowed_pair_count": profile["allowed_pair_count"],
        "expanded_blocked_pair_count": profile["blocked_pair_count"],
    }


def profile_signature(states: tuple[str, ...], *, coordinate: int) -> dict[str, object]:
    if not states:
        raise ValueError("states must be nonempty")
    if coordinate < 0 or coordinate >= len(states[0]):
        raise ValueError("coordinate out of range")

    allowed_pairs: list[str] = []
    blocked_pairs: list[str] = []
    for left, right in unordered_pairs(states):
        if left[coordinate] == right[coordinate]:
            allowed_pairs.append(f"{left},{right}")
        else:
            blocked_pairs.append(f"{left},{right}")

    return {
        "pair_count": len(allowed_pairs) + len(blocked_pairs),
        "allowed_pair_count": len(allowed_pairs),
        "blocked_pair_count": len(blocked_pairs),
        "allowed_pair_signature": ";".join(allowed_pairs),
        "blocked_pair_signature": ";".join(blocked_pairs),
    }


def profile_counts(profile: dict[str, object]) -> tuple[object, object, object]:
    return (
        profile["pair_count"],
        profile["allowed_pair_count"],
        profile["blocked_pair_count"],
    )


def unordered_pairs(items: tuple[str, ...]) -> list[tuple[str, str]]:
    return list(combinations(items, 2))
