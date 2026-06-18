"""Exact finite stochastic channel recovery characterization.

This module deliberately uses rational arithmetic and finite enumeration. It is
the first stochastic bridge after the deterministic recovery layer: characterize
the recovery surface before choosing any thresholded success criterion.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product


Channel = dict[str, dict[str, Fraction]]
Observation = dict[str, str]
TargetFunction = dict[str, str]
Decoder = dict[str, str]


@dataclass(frozen=True)
class OptimizedDecoderResult:
    """Best deterministic decoder for a finite worst-case recovery objective."""

    decoder: Decoder
    per_source_success: dict[str, Fraction]
    worst_case_success: Fraction


@dataclass(frozen=True)
class SupportAmbiguity:
    """One observation label reachable from multiple declared target classes."""

    observation_label: str
    sources: tuple[str, ...]
    target_values: tuple[str, ...]


@dataclass(frozen=True)
class StochasticRecoveryFamily:
    """One finite stochastic recovery characterization family."""

    family_id: str
    description: str
    metrics: dict[str, object]


def generate_stochastic_recovery_study() -> tuple[StochasticRecoveryFamily, ...]:
    """Generate exact finite stochastic channel characterization cases."""

    return (
        _support_exact_vs_high_confidence_family(),
        _same_support_different_probabilities_family(),
        _declared_vs_optimized_decoder_gap_family(),
        _coarsening_non_improvement_family(),
        _coarse_decoder_simulable_by_fine_family(),
        _same_worst_case_different_failure_localization_family(),
    )


def stochastic_recovery_summary() -> dict[str, object]:
    families = generate_stochastic_recovery_study()
    return {
        "status": "PASS",
        "family_count": len(families),
        "families": [_family_as_dict(family) for family in families],
    }


def validate_channel(
    states: tuple[str, ...],
    outputs: tuple[str, ...],
    channel: Channel,
) -> None:
    """Require a total finite rational channel whose rows sum to one."""

    missing_states = sorted(set(states) - set(channel))
    if missing_states:
        raise ValueError(f"channel is missing states: {missing_states}")
    for state in states:
        row = channel[state]
        missing_outputs = sorted(set(outputs) - set(row))
        if missing_outputs:
            raise ValueError(f"channel row {state!r} is missing outputs: {missing_outputs}")
        negative = {output: weight for output, weight in row.items() if weight < 0}
        if negative:
            raise ValueError(f"channel row {state!r} has negative weights: {negative}")
        total = sum((row[output] for output in outputs), start=Fraction(0))
        if total != 1:
            raise ValueError(f"channel row {state!r} sums to {total}, not 1")


def support_ambiguities(
    states: tuple[str, ...],
    outputs: tuple[str, ...],
    channel: Channel,
    observation: Observation,
    target: TargetFunction,
) -> tuple[SupportAmbiguity, ...]:
    """Observation labels whose positive-probability support mixes target values."""

    _assert_total(outputs, observation, "observation")
    _assert_total(states, target, "target")
    validate_channel(states, outputs, channel)
    by_observation: dict[str, set[str]] = {}
    sources_by_observation: dict[str, set[str]] = {}
    for state in states:
        for output in outputs:
            if channel[state][output] > 0:
                label = observation[output]
                by_observation.setdefault(label, set()).add(target[state])
                sources_by_observation.setdefault(label, set()).add(state)
    return tuple(
        SupportAmbiguity(
            observation_label=label,
            sources=tuple(sorted(sources_by_observation[label])),
            target_values=tuple(sorted(target_values)),
        )
        for label, target_values in sorted(by_observation.items())
        if len(target_values) > 1
    )


def support_exact_recoverable(
    states: tuple[str, ...],
    outputs: tuple[str, ...],
    channel: Channel,
    observation: Observation,
    target: TargetFunction,
) -> bool:
    """Exact support recovery holds iff no observation label mixes target values."""

    return not support_ambiguities(states, outputs, channel, observation, target)


def all_deterministic_decoders(
    observation_labels: tuple[str, ...],
    target_values: tuple[str, ...],
) -> tuple[Decoder, ...]:
    """Enumerate total deterministic decoders from observations to target values."""

    return tuple(
        {
            label: value
            for label, value in zip(observation_labels, assignment, strict=True)
        }
        for assignment in product(target_values, repeat=len(observation_labels))
    )


def success_by_source(
    states: tuple[str, ...],
    outputs: tuple[str, ...],
    channel: Channel,
    observation: Observation,
    target: TargetFunction,
    decoder: Decoder,
) -> dict[str, Fraction]:
    """Per-source success probabilities for a declared deterministic decoder."""

    _assert_total(outputs, observation, "observation")
    _assert_total(states, target, "target")
    _assert_decoder_total(observation, decoder)
    validate_channel(states, outputs, channel)
    return {
        state: sum(
            (
                channel[state][output]
                for output in outputs
                if decoder[observation[output]] == target[state]
            ),
            start=Fraction(0),
        )
        for state in states
    }


def worst_case_success(per_source_success: dict[str, Fraction]) -> Fraction:
    if not per_source_success:
        raise ValueError("per_source_success must be nonempty")
    return min(per_source_success.values())


def optimized_worst_case_decoder(
    states: tuple[str, ...],
    outputs: tuple[str, ...],
    channel: Channel,
    observation: Observation,
    target: TargetFunction,
) -> OptimizedDecoderResult:
    """Best worst-case recovery over all deterministic decoders."""

    observation_labels = tuple(sorted(set(observation.values())))
    target_values = tuple(sorted(set(target.values())))
    best: OptimizedDecoderResult | None = None
    for decoder in all_deterministic_decoders(observation_labels, target_values):
        per_source = success_by_source(states, outputs, channel, observation, target, decoder)
        worst_case = worst_case_success(per_source)
        candidate = OptimizedDecoderResult(
            decoder=decoder,
            per_source_success=per_source,
            worst_case_success=worst_case,
        )
        if best is None or (
            candidate.worst_case_success,
            _decoder_sort_key(candidate.decoder),
        ) > (
            best.worst_case_success,
            _decoder_sort_key(best.decoder),
        ):
            best = candidate
    if best is None:
        raise ValueError("no deterministic decoders were generated")
    return best


def coarsen_observation(
    outputs: tuple[str, ...],
    fine_observation: Observation,
    garbling: dict[str, str],
) -> Observation:
    """Post-process a fine observation through a deterministic garbling."""

    _assert_total(outputs, fine_observation, "fine_observation")
    fine_labels = set(fine_observation.values())
    missing = sorted(fine_labels - set(garbling))
    if missing:
        raise ValueError(f"garbling is missing fine labels: {missing}")
    return {output: garbling[fine_observation[output]] for output in outputs}


def observation_refines_outputs(
    outputs: tuple[str, ...],
    finer: Observation,
    coarser: Observation,
) -> bool:
    """`finer` refines `coarser` over finite outputs."""

    _assert_total(outputs, finer, "finer")
    _assert_total(outputs, coarser, "coarser")
    return all(
        coarser[left] == coarser[right]
        for left, right in product(outputs, outputs)
        if finer[left] == finer[right]
    )


def compose_coarse_decoder_through_fine(
    outputs: tuple[str, ...],
    fine_observation: Observation,
    coarse_observation: Observation,
    coarse_decoder: Decoder,
) -> Decoder:
    """Simulate a coarse decoder using the finer observation it factors through."""

    if not observation_refines_outputs(outputs, fine_observation, coarse_observation):
        raise ValueError("fine_observation does not refine coarse_observation")
    _assert_decoder_total(coarse_observation, coarse_decoder)
    fine_to_coarse: dict[str, str] = {}
    for output in outputs:
        fine_label = fine_observation[output]
        coarse_label = coarse_observation[output]
        existing = fine_to_coarse.setdefault(fine_label, coarse_label)
        if existing != coarse_label:
            raise ValueError("fine label maps to multiple coarse labels")
    return {
        fine_label: coarse_decoder[coarse_label]
        for fine_label, coarse_label in sorted(fine_to_coarse.items())
    }


def fraction_to_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _support_exact_vs_high_confidence_family() -> StochasticRecoveryFamily:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    target = {"x0": "false", "x1": "true"}
    observation = {"y0": "left", "y1": "right"}
    exact_channel = {
        "x0": {"y0": Fraction(1), "y1": Fraction(0)},
        "x1": {"y0": Fraction(0), "y1": Fraction(1)},
    }
    noisy_channel = {
        "x0": {"y0": Fraction(99, 100), "y1": Fraction(1, 100)},
        "x1": {"y0": Fraction(1, 100), "y1": Fraction(99, 100)},
    }
    exact = optimized_worst_case_decoder(states, outputs, exact_channel, observation, target)
    noisy = optimized_worst_case_decoder(states, outputs, noisy_channel, observation, target)

    return StochasticRecoveryFamily(
        family_id="support_exact_vs_high_confidence",
        description=(
            "A high-confidence noisy channel can have excellent worst-case recovery "
            "while failing exact support recovery."
        ),
        metrics={
            "exact_support_recoverable": support_exact_recoverable(
                states,
                outputs,
                exact_channel,
                observation,
                target,
            ),
            "noisy_support_recoverable": support_exact_recoverable(
                states,
                outputs,
                noisy_channel,
                observation,
                target,
            ),
            "exact_best_worst_case_success": fraction_to_text(exact.worst_case_success),
            "noisy_best_worst_case_success": fraction_to_text(noisy.worst_case_success),
            "noisy_support_ambiguity_count": len(
                support_ambiguities(states, outputs, noisy_channel, observation, target)
            ),
        },
    )


def _same_support_different_probabilities_family() -> StochasticRecoveryFamily:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    target = {"x0": "false", "x1": "true"}
    observation = {"y0": "left", "y1": "right"}
    high_confidence = {
        "x0": {"y0": Fraction(9, 10), "y1": Fraction(1, 10)},
        "x1": {"y0": Fraction(1, 10), "y1": Fraction(9, 10)},
    }
    lower_confidence = {
        "x0": {"y0": Fraction(3, 5), "y1": Fraction(2, 5)},
        "x1": {"y0": Fraction(2, 5), "y1": Fraction(3, 5)},
    }
    high = optimized_worst_case_decoder(states, outputs, high_confidence, observation, target)
    low = optimized_worst_case_decoder(states, outputs, lower_confidence, observation, target)

    return StochasticRecoveryFamily(
        family_id="same_support_different_probabilities",
        description=(
            "Two channels have the same positive-probability support and the same "
            "support ambiguity, but different optimized worst-case recovery."
        ),
        metrics={
            "same_positive_support": _positive_support_signature(states, outputs, high_confidence)
            == _positive_support_signature(states, outputs, lower_confidence),
            "high_support_recoverable": support_exact_recoverable(
                states,
                outputs,
                high_confidence,
                observation,
                target,
            ),
            "low_support_recoverable": support_exact_recoverable(
                states,
                outputs,
                lower_confidence,
                observation,
                target,
            ),
            "high_best_worst_case_success": fraction_to_text(high.worst_case_success),
            "low_best_worst_case_success": fraction_to_text(low.worst_case_success),
            "support_ambiguity_count": len(
                support_ambiguities(states, outputs, high_confidence, observation, target)
            ),
        },
    )


def _declared_vs_optimized_decoder_gap_family() -> StochasticRecoveryFamily:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    target = {"x0": "false", "x1": "true"}
    observation = {"y0": "left", "y1": "right"}
    channel = {
        "x0": {"y0": Fraction(9, 10), "y1": Fraction(1, 10)},
        "x1": {"y0": Fraction(1, 10), "y1": Fraction(9, 10)},
    }
    declared_decoder = {"left": "true", "right": "false"}
    declared_success = success_by_source(
        states,
        outputs,
        channel,
        observation,
        target,
        declared_decoder,
    )
    optimized = optimized_worst_case_decoder(states, outputs, channel, observation, target)

    return StochasticRecoveryFamily(
        family_id="declared_vs_optimized_decoder_gap",
        description=(
            "A declared decoder can perform badly even when an optimized "
            "deterministic decoder has high worst-case recovery."
        ),
        metrics={
            "declared_decoder": declared_decoder,
            "declared_worst_case_success": fraction_to_text(worst_case_success(declared_success)),
            "optimized_decoder": optimized.decoder,
            "optimized_worst_case_success": fraction_to_text(optimized.worst_case_success),
            "declared_per_source_success": _fraction_map_to_text(declared_success),
            "optimized_per_source_success": _fraction_map_to_text(optimized.per_source_success),
        },
    )


def _coarsening_non_improvement_family() -> StochasticRecoveryFamily:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    target = {"x0": "false", "x1": "true"}
    fine = {"y0": "left", "y1": "right"}
    coarse = {"y0": "same", "y1": "same"}
    channel = {
        "x0": {"y0": Fraction(1), "y1": Fraction(0)},
        "x1": {"y0": Fraction(0), "y1": Fraction(1)},
    }
    fine_result = optimized_worst_case_decoder(states, outputs, channel, fine, target)
    coarse_result = optimized_worst_case_decoder(states, outputs, channel, coarse, target)

    return StochasticRecoveryFamily(
        family_id="coarsening_non_improvement",
        description=(
            "A deterministic coarsening of an available observation cannot improve "
            "optimized worst-case recovery over unrestricted deterministic decoders."
        ),
        metrics={
            "fine_refines_coarse": observation_refines_outputs(outputs, fine, coarse),
            "fine_support_recoverable": support_exact_recoverable(
                states,
                outputs,
                channel,
                fine,
                target,
            ),
            "coarse_support_recoverable": support_exact_recoverable(
                states,
                outputs,
                channel,
                coarse,
                target,
            ),
            "fine_best_worst_case_success": fraction_to_text(fine_result.worst_case_success),
            "coarse_best_worst_case_success": fraction_to_text(coarse_result.worst_case_success),
            "coarse_best_no_greater_than_fine_best": (
                coarse_result.worst_case_success <= fine_result.worst_case_success
            ),
        },
    )


def _coarse_decoder_simulable_by_fine_family() -> StochasticRecoveryFamily:
    states = ("x0", "x1")
    outputs = ("a0", "a1", "b0", "b1")
    target = {"x0": "false", "x1": "true"}
    fine = {"a0": "a0", "a1": "a1", "b0": "b0", "b1": "b1"}
    coarse = {"a0": "a", "a1": "a", "b0": "b", "b1": "b"}
    channel = {
        "x0": {"a0": Fraction(1, 2), "a1": Fraction(1, 2), "b0": Fraction(0), "b1": Fraction(0)},
        "x1": {"a0": Fraction(0), "a1": Fraction(0), "b0": Fraction(1, 2), "b1": Fraction(1, 2)},
    }
    coarse_decoder = {"a": "false", "b": "true"}
    fine_decoder = compose_coarse_decoder_through_fine(outputs, fine, coarse, coarse_decoder)
    coarse_success = success_by_source(states, outputs, channel, coarse, target, coarse_decoder)
    fine_success = success_by_source(states, outputs, channel, fine, target, fine_decoder)

    return StochasticRecoveryFamily(
        family_id="coarse_decoder_simulable_by_fine",
        description=(
            "A target-aligned coarse decoder can be useful and legible, but the "
            "available fine observation can simulate it when the coarse view factors "
            "through the fine view."
        ),
        metrics={
            "fine_refines_coarse": observation_refines_outputs(outputs, fine, coarse),
            "coarse_decoder": coarse_decoder,
            "composed_fine_decoder": fine_decoder,
            "coarse_per_source_success": _fraction_map_to_text(coarse_success),
            "fine_composed_per_source_success": _fraction_map_to_text(fine_success),
            "same_success_after_composition": coarse_success == fine_success,
        },
    )


def _same_worst_case_different_failure_localization_family() -> StochasticRecoveryFamily:
    states = ("x0", "x1")
    outputs = ("y0", "y1")
    target = {"x0": "false", "x1": "true"}
    observation = {"y0": "left", "y1": "right"}
    balanced = {
        "x0": {"y0": Fraction(4, 5), "y1": Fraction(1, 5)},
        "x1": {"y0": Fraction(1, 5), "y1": Fraction(4, 5)},
    }
    localized = {
        "x0": {"y0": Fraction(1), "y1": Fraction(0)},
        "x1": {"y0": Fraction(1, 5), "y1": Fraction(4, 5)},
    }
    balanced_result = optimized_worst_case_decoder(states, outputs, balanced, observation, target)
    localized_result = optimized_worst_case_decoder(states, outputs, localized, observation, target)

    return StochasticRecoveryFamily(
        family_id="same_worst_case_different_failure_localization",
        description=(
            "The same optimized worst-case score can hide different per-source "
            "failure localization, so the characterization surface records the vector."
        ),
        metrics={
            "balanced_worst_case_success": fraction_to_text(balanced_result.worst_case_success),
            "localized_worst_case_success": fraction_to_text(localized_result.worst_case_success),
            "same_worst_case_success": (
                balanced_result.worst_case_success == localized_result.worst_case_success
            ),
            "balanced_per_source_success": _fraction_map_to_text(
                balanced_result.per_source_success
            ),
            "localized_per_source_success": _fraction_map_to_text(
                localized_result.per_source_success
            ),
            "same_per_source_success_vector": (
                balanced_result.per_source_success == localized_result.per_source_success
            ),
        },
    )


def _positive_support_signature(
    states: tuple[str, ...],
    outputs: tuple[str, ...],
    channel: Channel,
) -> tuple[tuple[str, str], ...]:
    validate_channel(states, outputs, channel)
    return tuple(
        (state, output)
        for state in states
        for output in outputs
        if channel[state][output] > 0
    )


def _assert_total(keys: tuple[str, ...], mapping: dict[str, str], label: str) -> None:
    missing = sorted(set(keys) - set(mapping))
    if missing:
        raise ValueError(f"{label} is missing keys: {missing}")


def _assert_decoder_total(observation: Observation, decoder: Decoder) -> None:
    labels = set(observation.values())
    missing = sorted(labels - set(decoder))
    if missing:
        raise ValueError(f"decoder is missing observation labels: {missing}")


def _decoder_sort_key(decoder: Decoder) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(decoder.items()))


def _fraction_map_to_text(values: dict[str, Fraction]) -> dict[str, str]:
    return {key: fraction_to_text(value) for key, value in sorted(values.items())}


def _family_as_dict(family: StochasticRecoveryFamily) -> dict[str, object]:
    return {
        "family_id": family.family_id,
        "description": family.description,
        "metrics": family.metrics,
    }
