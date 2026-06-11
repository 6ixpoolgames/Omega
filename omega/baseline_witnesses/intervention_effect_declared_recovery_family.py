"""Parameterized intervention-effect/declaration recovery family.

This module generalizes the retained same-intervention-effect witness without
creating new retained artifacts. For each nuisance-bit count ``k >= 1``, it
compares a deterministic intervention system that carries declared bit ``d``
after the intervention with systems that carry one nuisance bit ``n_i``. The
declared intervention-effect profile is matched while declared recovery
differs.
"""

from __future__ import annotations


INTERVENTIONS = ("set_effect_0", "set_effect_1")
System = dict[tuple[str, str], str]


def run_family_case(*, nuisance_bit_count: int, nuisance_index: int) -> dict[str, object]:
    states = state_space(nuisance_bit_count)
    declared = declared_system(states)
    nuisance = nuisance_system(states, nuisance_index)
    declared_profile = intervention_effect_profile(declared, states)
    nuisance_profile = intervention_effect_profile(nuisance, states)
    declared_recovery = declared_d_recovery(declared, states)
    nuisance_recovery = declared_d_recovery(nuisance, states)

    intervention_signatures_match = (
        declared_profile["intervention_effect_baseline_signature"]
        == nuisance_profile["intervention_effect_baseline_signature"]
    )
    declared_recovers = bool(declared_recovery["exact_declared_recovery"])
    nuisance_recovers = bool(nuisance_recovery["exact_declared_recovery"])

    return {
        "family_id": "same_intervention_effect_different_declared_recovery_family",
        "nuisance_bit_count": nuisance_bit_count,
        "nuisance_index": nuisance_index,
        "source_count": len(states),
        "declared_system_id": "effect_with_declared_d_carried",
        "nuisance_system_id": f"effect_with_nuisance_n{nuisance_index + 1}_carried",
        "declared_intervention_profile": declared_profile,
        "nuisance_intervention_profile": nuisance_profile,
        "intervention_signatures_match": intervention_signatures_match,
        "declared_system_exact_declared_recovery": declared_recovers,
        "nuisance_system_exact_declared_recovery": nuisance_recovers,
        "nuisance_system_ambiguous_observations": nuisance_recovery[
            "ambiguous_target_observations"
        ],
        "family_case_status": (
            "same_intervention_effect_different_declared_recovery"
            if intervention_signatures_match and declared_recovers and not nuisance_recovers
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
        (source, intervention): intervention_effect(intervention) + source[0]
        for source in states
        for intervention in INTERVENTIONS
    }


def nuisance_system(states: tuple[str, ...], nuisance_index: int) -> System:
    if not states:
        raise ValueError("states must be nonempty")
    nuisance_bit_count = len(states[0]) - 1
    if nuisance_index < 0 or nuisance_index >= nuisance_bit_count:
        raise ValueError("nuisance_index out of range")
    coordinate = 1 + nuisance_index
    return {
        (source, intervention): intervention_effect(intervention) + source[coordinate]
        for source in states
        for intervention in INTERVENTIONS
    }


def intervention_effect_profile(system: System, states: tuple[str, ...]) -> dict[str, object]:
    return {
        "source_count": len(states),
        "intervention_count": len(INTERVENTIONS),
        "transition_edge_count": len(states) * len(INTERVENTIONS),
        "deterministic_transition": 1,
        "target_support_size": len({target for target in system.values()}),
        "target_support": ";".join(sorted(set(system.values()))),
        "effect_by_intervention_signature": effect_by_intervention_signature(system, states),
        "target_support_by_intervention_signature": target_support_by_intervention(
            system, states
        ),
        "target_count_by_intervention_signature": target_count_by_intervention(system, states),
        "intervention_effect_baseline_signature": (
            f"effects:{effect_by_intervention_signature(system, states)}|"
            f"support:{target_support_by_intervention(system, states)}|"
            f"counts:{target_count_by_intervention(system, states)}"
        ),
    }


def declared_d_recovery(system: System, states: tuple[str, ...]) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    for source in states:
        for intervention in INTERVENTIONS:
            target = system[(source, intervention)]
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


def effect_by_intervention_signature(system: System, states: tuple[str, ...]) -> str:
    values = {
        intervention: ",".join(
            sorted({system[(source, intervention)][0] for source in states})
        )
        for intervention in INTERVENTIONS
    }
    return signature(values)


def target_support_by_intervention(system: System, states: tuple[str, ...]) -> str:
    values = {
        intervention: ",".join(
            sorted({system[(source, intervention)] for source in states})
        )
        for intervention in INTERVENTIONS
    }
    return signature(values)


def target_count_by_intervention(system: System, states: tuple[str, ...]) -> str:
    values = {
        intervention: len({system[(source, intervention)] for source in states})
        for intervention in INTERVENTIONS
    }
    return signature(values)


def intervention_effect(intervention_id: str) -> str:
    if intervention_id == "set_effect_0":
        return "0"
    if intervention_id == "set_effect_1":
        return "1"
    raise ValueError(f"unknown intervention_id: {intervention_id}")


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))
