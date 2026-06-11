"""Parameterized observation-rank/declaration recovery family.

This module generalizes the retained same-observation-rank witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares a deterministic observer that emits declared bit ``d`` with observers
that emit one nuisance bit ``n_i``. The finite observation-rank and partition
profile are matched while declared recovery differs.
"""

from __future__ import annotations


Observer = dict[str, str]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    declared = declared_observer(states)
    nuisance = nuisance_observer(states, nuisance_index)
    declared_profile = observation_profile(declared, states)
    nuisance_profile = observation_profile(nuisance, states)
    declared_recovery = declared_d_recovery(declared, states)
    nuisance_recovery = declared_d_recovery(nuisance, states)

    observation_signatures_match = (
        declared_profile["observation_baseline_signature"]
        == nuisance_profile["observation_baseline_signature"]
    )
    declared_recovers = bool(declared_recovery["exact_declared_recovery"])
    nuisance_recovers = bool(nuisance_recovery["exact_declared_recovery"])

    return {
        "family_id": "same_observation_rank_different_declared_recovery_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "state_count": len(states),
        "declared_observer_id": "observe_declared_d",
        "nuisance_observer_id": f"observe_nuisance_n{nuisance_index + 1}",
        "declared_observation_profile": declared_profile,
        "nuisance_observation_profile": nuisance_profile,
        "observation_signatures_match": observation_signatures_match,
        "declared_observer_exact_declared_recovery": declared_recovers,
        "nuisance_observer_exact_declared_recovery": nuisance_recovers,
        "nuisance_observer_ambiguous_outputs": nuisance_recovery["ambiguous_outputs"],
        "family_case_status": (
            "same_observation_rank_different_declared_recovery"
            if observation_signatures_match and declared_recovers and not nuisance_recovers
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


def declared_observer(states: tuple[str, ...]) -> Observer:
    return {state: state[0] for state in states}


def nuisance_observer(states: tuple[str, ...], nuisance_index: int) -> Observer:
    if not states:
        raise ValueError("states must be nonempty")
    nuisance_bit_count = len(states[0]) - 1
    if nuisance_index < 0 or nuisance_index >= nuisance_bit_count:
        raise ValueError("nuisance_index out of range")
    coordinate = 1 + nuisance_index
    return {state: state[coordinate] for state in states}


def observation_profile(observer: Observer, states: tuple[str, ...]) -> dict[str, object]:
    blocks = output_blocks(observer)
    block_sizes = sorted(len(members) for members in blocks.values())
    return {
        "state_count": len(states),
        "output_support_size": len(blocks),
        "output_support": ";".join(sorted(blocks)),
        "finite_observation_rank": 1,
        "observation_block_count": len(blocks),
        "observation_block_size_signature": ";".join(str(size) for size in block_sizes),
        "output_to_state_count_signature": signature(
            {output: len(members) for output, members in blocks.items()}
        ),
        "deterministic_observer": 1,
        "observation_baseline_signature": (
            f"rank:1|"
            f"support:{';'.join(sorted(blocks))}|"
            f"blocks:{len(blocks)}|"
            f"sizes:{';'.join(str(size) for size in block_sizes)}|"
            f"counts:{signature({output: len(members) for output, members in blocks.items()})}"
        ),
    }


def declared_d_recovery(observer: Observer, states: tuple[str, ...]) -> dict[str, object]:
    output_sources: dict[str, set[str]] = {}
    for state in states:
        output_sources.setdefault(observer[state], set()).add(state[0])

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


def output_blocks(observer: Observer) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    for state, output in observer.items():
        blocks.setdefault(output, []).append(state)
    return blocks


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))
