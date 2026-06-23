"""Recovery and target-scramble facts."""

from __future__ import annotations

from omega.adapters.finite_relational.model import FiniteRelationalModel, SchemaError

def bounded_recovery_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
    decoders: tuple[str, ...],
    true_label: str = "true",
    false_label: str = "false",
) -> dict[str, object]:
    """Check exact recovery by a declared bounded decoder family.

    The audit is intentionally family-relative: failure means no declared
    decoder recovers the target from the observation, not that no possible
    decoder exists in a richer class.
    """

    if not decoders:
        raise SchemaError("bounded recovery must declare at least one decoder")

    observation_function = model.functions[observation]
    target = model.predicates[target_predicate]
    if target.domain != observation_function.domain:
        raise SchemaError(
            "bounded recovery target predicate and observation function "
            f"must share a domain: {target.domain} != {observation_function.domain}"
        )

    states = model.domain(observation_function.domain)
    missing_states = sorted(set(states) - set(observation_function.mapping))
    if missing_states:
        raise SchemaError(
            f"observation function {observation} is not total on "
            f"{observation_function.domain}: {missing_states}"
        )

    target_members = target.members
    observed_labels = sorted({observation_function.mapping[state] for state in states})
    decoder_results: list[dict[str, object]] = []
    successful_decoders: list[str] = []
    failed_decoders: list[str] = []

    for decoder_name in decoders:
        decoder = model.functions[decoder_name]
        missing_labels = sorted(set(observed_labels) - set(decoder.mapping))
        if missing_labels:
            raise SchemaError(
                f"decoder {decoder_name} is not total on observed labels "
                f"from {observation}: {missing_labels}"
            )
        mismatches = []
        for state in states:
            observed = observation_function.mapping[state]
            predicted = decoder.mapping[observed]
            expected = true_label if state in target_members else false_label
            if predicted != expected:
                mismatches.append(
                    {
                        "state": state,
                        "observation": observed,
                        "predicted": predicted,
                        "expected": expected,
                    }
                )
        succeeds = not mismatches
        if succeeds:
            successful_decoders.append(decoder_name)
        else:
            failed_decoders.append(decoder_name)
        decoder_results.append(
            {
                "decoder": decoder_name,
                "succeeds": succeeds,
                "mismatch_count": len(mismatches),
                "mismatches": mismatches,
            }
        )

    ambiguous_labels = []
    for label in observed_labels:
        preimage = [state for state in states if observation_function.mapping[state] == label]
        target_values = {state in target_members for state in preimage}
        if len(target_values) > 1:
            ambiguous_labels.append(label)

    return {
        "recoverable": bool(successful_decoders),
        "recovery_mode": "declared_decoder_family",
        "state_count": len(states),
        "observed_labels": observed_labels,
        "ambiguous_observation_labels": ambiguous_labels,
        "decoder_count": len(decoders),
        "successful_decoders": successful_decoders,
        "failed_decoders": failed_decoders,
        "decoder_results": decoder_results,
    }


def target_scramble_sensitivity_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
    scrambled_predicate: str,
    decoders: tuple[str, ...],
    true_label: str = "true",
    false_label: str = "false",
) -> dict[str, object]:
    """Check whether scrambling a target changes declared-decoder recovery facts.

    This is an adapter provenance gate, not a semantic target validator. It
    asks whether the supplied target has decoder-relative bite relative to a
    declared observation and decoder family. A target is sensitive here when
    replacing it with the scrambled predicate changes exact recoverability or
    the successful decoder surface.
    """

    target = bounded_recovery_facts(
        model,
        observation=observation,
        target_predicate=target_predicate,
        decoders=decoders,
        true_label=true_label,
        false_label=false_label,
    )
    scrambled = bounded_recovery_facts(
        model,
        observation=observation,
        target_predicate=scrambled_predicate,
        decoders=decoders,
        true_label=true_label,
        false_label=false_label,
    )
    recoverability_changed = bool(target["recoverable"]) != bool(scrambled["recoverable"])
    successful_decoders_changed = target["successful_decoders"] != scrambled["successful_decoders"]
    sensitive = recoverability_changed or successful_decoders_changed
    return {
        "sensitive": sensitive,
        "sensitivity_mode": "decoder_relative",
        "recoverability_changed": recoverability_changed,
        "successful_decoders_changed": successful_decoders_changed,
        "observation": observation,
        "target_predicate": target_predicate,
        "scrambled_predicate": scrambled_predicate,
        "decoders": list(decoders),
        "target_recoverable": target["recoverable"],
        "scrambled_recoverable": scrambled["recoverable"],
        "target_successful_decoders": target["successful_decoders"],
        "scrambled_successful_decoders": scrambled["successful_decoders"],
        "target": target,
        "scrambled": scrambled,
    }


def unrestricted_exact_recovery_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
) -> dict[str, object]:
    """Check exact deterministic recoverability by any observation decoder."""

    observation_function = model.functions[observation]
    target = model.predicates[target_predicate]
    if target.domain != observation_function.domain:
        raise SchemaError(
            "unrestricted recovery target predicate and observation function "
            f"must share a domain: {target.domain} != {observation_function.domain}"
        )

    states = model.domain(observation_function.domain)
    missing_states = sorted(set(states) - set(observation_function.mapping))
    if missing_states:
        raise SchemaError(
            f"observation function {observation} is not total on "
            f"{observation_function.domain}: {missing_states}"
        )

    target_members = target.members
    observed_labels = sorted({observation_function.mapping[state] for state in states})
    ambiguous_labels = []
    label_profiles = []
    for label in observed_labels:
        preimage = [state for state in states if observation_function.mapping[state] == label]
        true_states = sorted(state for state in preimage if state in target_members)
        false_states = sorted(state for state in preimage if state not in target_members)
        target_values = []
        if false_states:
            target_values.append("false")
        if true_states:
            target_values.append("true")
        ambiguous = bool(true_states and false_states)
        if ambiguous:
            ambiguous_labels.append(label)
        label_profiles.append(
            {
                "label": label,
                "states": sorted(preimage),
                "target_values": target_values,
                "true_states": true_states,
                "false_states": false_states,
                "ambiguous": ambiguous,
            }
        )

    return {
        "recoverable": not ambiguous_labels,
        "recovery_mode": "unrestricted_deterministic_decoder",
        "observation": observation,
        "target_predicate": target_predicate,
        "state_count": len(states),
        "target_member_count": len(target_members),
        "observed_labels": observed_labels,
        "ambiguous_observation_labels": ambiguous_labels,
        "label_profiles": label_profiles,
    }


def target_scramble_capacity_sensitivity_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
    scrambled_predicate: str,
) -> dict[str, object]:
    """Check whether scrambling changes unrestricted exact recovery capacity."""

    target_domain = model.predicates[target_predicate].domain
    scrambled_domain = model.predicates[scrambled_predicate].domain
    if target_domain != scrambled_domain:
        raise SchemaError(
            "target scramble capacity sensitivity requires predicates over the same domain: "
            f"{target_domain} != {scrambled_domain}"
        )
    target = unrestricted_exact_recovery_facts(
        model,
        observation=observation,
        target_predicate=target_predicate,
    )
    scrambled = unrestricted_exact_recovery_facts(
        model,
        observation=observation,
        target_predicate=scrambled_predicate,
    )
    states = set(model.domain(target_domain))
    target_members = set(model.predicate_members(target_predicate))
    scrambled_members = set(model.predicate_members(scrambled_predicate))
    recoverability_changed = bool(target["recoverable"]) != bool(scrambled["recoverable"])
    return {
        "capacity_sensitive": recoverability_changed,
        "sensitivity_mode": "unrestricted_exact_recovery_capacity",
        "recoverability_changed": recoverability_changed,
        "same_prevalence": len(target_members) == len(scrambled_members),
        "complement_scramble": scrambled_members == states - target_members,
        "observation": observation,
        "target_predicate": target_predicate,
        "scrambled_predicate": scrambled_predicate,
        "target_recoverable": target["recoverable"],
        "scrambled_recoverable": scrambled["recoverable"],
        "target_member_count": len(target_members),
        "scrambled_member_count": len(scrambled_members),
        "target_ambiguous_observation_labels": target["ambiguous_observation_labels"],
        "scrambled_ambiguous_observation_labels": scrambled[
            "ambiguous_observation_labels"
        ],
        "target": target,
        "scrambled": scrambled,
    }
