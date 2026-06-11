"""Finite adversarial search for baseline witness patterns.

This is an external-review helper, not a theorem prover. It searches small
finite channel spaces for cases where a baseline summary matches while declared
recovery differs.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections.abc import Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search for finite baseline witness patterns.")
    parser.add_argument(
        "--match-baseline",
        choices=["mutual_information", "reachability"],
        required=True,
    )
    parser.add_argument(
        "--separate",
        choices=["declared_recovery"],
        default="declared_recovery",
    )
    parser.add_argument("--states", type=int, default=8)
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_search(
        match_baseline=args.match_baseline,
        separate=args.separate,
        states=args.states,
        trials=args.trials,
        seed=args.seed,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def run_search(
    *,
    match_baseline: str,
    separate: str = "declared_recovery",
    states: int = 8,
    trials: int = 10000,
    seed: int = 0,
) -> dict[str, object]:
    if separate != "declared_recovery":
        raise ValueError("only declared_recovery separation is currently supported")
    labels = state_labels(states)
    rng = random.Random(seed)
    if match_baseline == "mutual_information":
        return search_mutual_information(labels=labels, trials=trials, rng=rng, seed=seed)
    if match_baseline == "reachability":
        return search_reachability(labels=labels, trials=trials, rng=rng, seed=seed)
    raise ValueError(f"unsupported baseline: {match_baseline}")


def search_mutual_information(
    *,
    labels: tuple[str, ...],
    trials: int,
    rng: random.Random,
    seed: int,
) -> dict[str, object]:
    declared = {source: source[0] for source in labels}
    declared_baseline = deterministic_binary_information_signature(declared)
    declared_recovery = declared_binary_recovery(declared, labels)

    for trial_index, candidate in enumerate(mutual_information_candidates(labels, trials, rng), start=1):
        candidate_baseline = deterministic_binary_information_signature(candidate)
        candidate_recovery = declared_binary_recovery(candidate, labels)
        if (
            candidate_baseline == declared_baseline
            and declared_recovery["exact_declared_recovery"]
            and not candidate_recovery["exact_declared_recovery"]
        ):
            return {
                "status": "PASS",
                "match_baseline": "mutual_information",
                "separate": "declared_recovery",
                "state_count": len(labels),
                "trials_used": trial_index,
                "seed": seed,
                "declared_baseline": declared_baseline,
                "candidate_baseline": candidate_baseline,
                "declared_recovery": declared_recovery,
                "candidate_recovery": candidate_recovery,
                "candidate_channel": candidate,
                "not_claimed": not_claimed(),
            }

    return failure_result(
        match_baseline="mutual_information",
        state_count=len(labels),
        trials=trials,
        seed=seed,
    )


def search_reachability(
    *,
    labels: tuple[str, ...],
    trials: int,
    rng: random.Random,
    seed: int,
) -> dict[str, object]:
    declared = {
        source: tuple(target for target in labels if target[0] == source[0])
        for source in labels
    }
    declared_baseline = reachability_signature(declared)
    declared_recovery = declared_support_recovery(declared, labels)

    for trial_index, candidate in enumerate(reachability_candidates(labels, trials, rng), start=1):
        candidate_baseline = reachability_signature(candidate)
        candidate_recovery = declared_support_recovery(candidate, labels)
        if (
            candidate_baseline == declared_baseline
            and declared_recovery["exact_declared_recovery"]
            and not candidate_recovery["exact_declared_recovery"]
        ):
            return {
                "status": "PASS",
                "match_baseline": "reachability",
                "separate": "declared_recovery",
                "state_count": len(labels),
                "trials_used": trial_index,
                "seed": seed,
                "declared_baseline": declared_baseline,
                "candidate_baseline": candidate_baseline,
                "declared_recovery": declared_recovery,
                "candidate_recovery": candidate_recovery,
                "candidate_support": {key: list(value) for key, value in candidate.items()},
                "not_claimed": not_claimed(),
            }

    return failure_result(
        match_baseline="reachability",
        state_count=len(labels),
        trials=trials,
        seed=seed,
    )


def mutual_information_candidates(
    labels: tuple[str, ...],
    trials: int,
    rng: random.Random,
) -> Iterable[dict[str, str]]:
    if bit_width(len(labels)) >= 2:
        yield {source: source[1] for source in labels}
    half = len(labels) // 2
    for _ in range(max(0, trials - 1)):
        shuffled = list(labels)
        rng.shuffle(shuffled)
        zero_sources = set(shuffled[:half])
        yield {source: "0" if source in zero_sources else "1" for source in labels}


def reachability_candidates(
    labels: tuple[str, ...],
    trials: int,
    rng: random.Random,
) -> Iterable[dict[str, tuple[str, ...]]]:
    if bit_width(len(labels)) >= 2:
        yield {
            source: tuple(target for target in labels if target[1] == source[1])
            for source in labels
        }
    half = len(labels) // 2
    for _ in range(max(0, trials - 1)):
        candidate = {}
        for source in labels:
            targets = list(labels)
            rng.shuffle(targets)
            candidate[source] = tuple(sorted(targets[:half]))
        yield candidate


def deterministic_binary_information_signature(channel: dict[str, str]) -> dict[str, object]:
    output_weights: dict[str, int] = {}
    for output in channel.values():
        output_weights[output] = output_weights.get(output, 0) + 1
    output_entropy = entropy_from_weights(output_weights.values())
    return {
        "source_count": len(channel),
        "output_support_size": len(output_weights),
        "output_weight_signature": signature(output_weights),
        "conditional_output_entropy_bits": "0.000000",
        "mutual_information_source_output_bits": f"{output_entropy:.6f}",
        "deterministic_output_capacity_bits": f"{math.log2(len(output_weights)):.6f}",
    }


def reachability_signature(channel: dict[str, tuple[str, ...]]) -> dict[str, object]:
    support_counts = {source: len(targets) for source, targets in channel.items()}
    entropies = {source: support_entropy_bits(targets) for source, targets in channel.items()}
    global_support = sorted({target for targets in channel.values() for target in targets})
    return {
        "source_count": len(channel),
        "edge_count": sum(support_counts.values()),
        "global_target_support_size": len(global_support),
        "global_target_support": ";".join(global_support),
        "per_source_reachable_count_signature": signature(support_counts),
        "per_source_entropy_bits_signature": float_signature(entropies),
    }


def declared_binary_recovery(channel: dict[str, str], labels: tuple[str, ...]) -> dict[str, object]:
    output_sources: dict[str, set[str]] = {}
    for source in labels:
        output_sources.setdefault(channel[source], set()).add(source[0])
    ambiguous = {
        output: sorted(source_labels)
        for output, source_labels in output_sources.items()
        if len(source_labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(output_sources) == ["0", "1"],
        "ambiguous_outputs": ambiguity_signature(ambiguous),
        "output_to_source_labels": setmap_signature(output_sources),
    }


def declared_support_recovery(
    channel: dict[str, tuple[str, ...]],
    labels: tuple[str, ...],
) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    for source in labels:
        for target in channel[source]:
            observation_sources.setdefault(target[0], set()).add(source[0])
    ambiguous = {
        observation: sorted(source_labels)
        for observation, source_labels in observation_sources.items()
        if len(source_labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_target_observations": ambiguity_signature(ambiguous),
        "observation_to_source_labels": setmap_signature(observation_sources),
    }


def state_labels(count: int) -> tuple[str, ...]:
    width = bit_width(count)
    if count != 2**width or width < 2:
        raise ValueError("states must be a power of two with at least four states")
    return tuple(f"{value:0{width}b}" for value in range(count))


def bit_width(count: int) -> int:
    if count <= 0:
        raise ValueError("states must be positive")
    return int(math.log2(count))


def entropy_from_weights(weights: Iterable[int]) -> float:
    values = list(weights)
    total = sum(values)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for weight in values:
        probability = weight / total
        entropy -= probability * math.log2(probability)
    return entropy


def support_entropy_bits(support: tuple[str, ...]) -> float:
    if not support:
        return 0.0
    probability = 1.0 / len(support)
    return -sum(probability * math.log2(probability) for _target in support)


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))


def setmap_signature(values: dict[str, set[str]]) -> str:
    return ";".join(
        f"{key}->{{{','.join(sorted(values[key]))}}}" for key in sorted(values)
    )


def ambiguity_signature(values: dict[str, list[str]]) -> str:
    return ";".join(f"{key}->{{{','.join(values[key])}}}" for key in sorted(values))


def failure_result(*, match_baseline: str, state_count: int, trials: int, seed: int) -> dict[str, object]:
    return {
        "status": "FAIL",
        "match_baseline": match_baseline,
        "separate": "declared_recovery",
        "state_count": state_count,
        "trials": trials,
        "seed": seed,
        "not_claimed": not_claimed(),
    }


def not_claimed() -> list[str]:
    return [
        "exhaustive search",
        "infinite-family theorem",
        "Omega validation",
        "value detection",
        "agency detection",
        "identity detection",
        "substrate-general theory validation",
    ]


if __name__ == "__main__":
    main()

