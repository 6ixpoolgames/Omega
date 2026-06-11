"""Parameterized viability-kernel/declaration recovery family.

This module generalizes the retained same-viability-kernel witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares a deterministic one-step system that carries declared bit ``d`` in the
declared recovery bit with systems that carry one nuisance bit ``n_i``.

The finite declared viability-kernel summary is matched while declared recovery
differs.
"""

from __future__ import annotations


System = dict[str, str]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    declared = declared_system(states)
    nuisance = nuisance_system(states, nuisance_index)
    declared_profile = viability_kernel_profile(declared, states)
    nuisance_profile = viability_kernel_profile(nuisance, states)
    declared_recovery = declared_d_recovery(declared, states)
    nuisance_recovery = declared_d_recovery(nuisance, states)

    kernel_signatures_match = (
        declared_profile["viability_kernel_baseline_signature"]
        == nuisance_profile["viability_kernel_baseline_signature"]
    )
    declared_recovers = bool(declared_recovery["exact_declared_recovery"])
    nuisance_recovers = bool(nuisance_recovery["exact_declared_recovery"])

    return {
        "family_id": "same_viability_kernel_different_declared_recovery_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "source_count": len(states),
        "declared_system_id": "kernel_with_declared_d_carried",
        "nuisance_system_id": f"kernel_with_nuisance_n{nuisance_index + 1}_carried",
        "declared_viability_predicate": "state first bit d = 1",
        "declared_kernel_profile": declared_profile,
        "nuisance_kernel_profile": nuisance_profile,
        "kernel_signatures_match": kernel_signatures_match,
        "declared_system_exact_declared_recovery": declared_recovers,
        "nuisance_system_exact_declared_recovery": nuisance_recovers,
        "nuisance_system_ambiguous_observations": nuisance_recovery[
            "ambiguous_target_observations"
        ],
        "family_case_status": (
            "same_viability_kernel_different_declared_recovery"
            if kernel_signatures_match and declared_recovers and not nuisance_recovers
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
    return {source: target_state(source, recovery_bit=source[0]) for source in states}


def nuisance_system(states: tuple[str, ...], nuisance_index: int) -> System:
    if not states:
        raise ValueError("states must be nonempty")
    nuisance_bit_count = len(states[0]) - 1
    if nuisance_index < 0 or nuisance_index >= nuisance_bit_count:
        raise ValueError("nuisance_index out of range")
    coordinate = 1 + nuisance_index
    return {
        source: target_state(source, recovery_bit=source[coordinate])
        for source in states
    }


def target_state(source: str, *, recovery_bit: str) -> str:
    return source[0] + recovery_bit + source[2:]


def viability_kernel_profile(system: System, states: tuple[str, ...]) -> dict[str, object]:
    kernel_sources = [source for source in states if is_viable(system[source])]
    source_to_target_viability = {
        source: int(is_viable(system[source])) for source in states
    }
    source_viability = {source: int(is_viable(source)) for source in states}
    return {
        "source_count": len(states),
        "transition_edge_count": len(states),
        "deterministic_transition": 1,
        "declared_viability_predicate": "state first bit d = 1",
        "viability_kernel_size": len(kernel_sources),
        "viability_kernel_signature": ";".join(kernel_sources),
        "source_to_target_viability_signature": signature(source_to_target_viability),
        "source_viability_signature": signature(source_viability),
        "viability_kernel_baseline_signature": (
            f"N:{len(states)}|"
            f"E:{len(states)}|"
            "deterministic:1|"
            "predicate:state first bit d = 1|"
            f"K_size:{len(kernel_sources)}|"
            f"K:{';'.join(kernel_sources)}|"
            f"source_to_target:{signature(source_to_target_viability)}|"
            f"source_viability:{signature(source_viability)}"
        ),
    }


def declared_d_recovery(system: System, states: tuple[str, ...]) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    for source in states:
        target = system[source]
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


def is_viable(state: str) -> bool:
    return state[0] == "1"


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))
