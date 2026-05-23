from __future__ import annotations

from collections import Counter

from .detectors import (
    compression_proxy,
    entropy_from_counts,
    js_divergence,
    motif_reuse,
    profile_class,
    recurrence_rate,
    smoothed_kl,
)
from .probes import Probe
from .substrate import LandscapeSystem, State

HORIZONS = (0, 1, 2, 4, 8, 12, 16)


def reachable(system: LandscapeSystem, start: State, horizon: int) -> frozenset[State]:
    seen = {start}
    frontier = {start}
    for _ in range(horizon):
        next_frontier = {target for state in frontier for target in system.edges[state]}
        next_frontier -= seen
        if not next_frontier:
            break
        seen.update(next_frontier)
        frontier = next_frontier
    return frozenset(seen)


def exact_frontier(system: LandscapeSystem, start: State, horizon: int) -> frozenset[State]:
    frontier = {start}
    for _ in range(horizon):
        next_frontier = {target for state in frontier for target in system.edges[state]}
        frontier = next_frontier
        if not frontier:
            break
    return frozenset(frontier)


def signature_distribution(states: frozenset[State], probe: Probe) -> dict[object, int]:
    return dict(Counter(probe.fn(state) for state in states))


def future_profile(
    system: LandscapeSystem,
    start: State,
    probe: Probe,
    null_counts_by_h: dict[int, dict[object, int]] | None = None,
) -> tuple[dict[str, float | int | str], list[dict[str, float | int | str]], list[dict[str, float | int | str]]]:
    reach_by_h = {h: reachable(system, start, h) for h in HORIZONS}
    exact_by_h = {h: exact_frontier(system, start, h) for h in HORIZONS}
    distributions = {h: signature_distribution(exact_by_h[h], probe) for h in HORIZONS}
    entropies = {h: entropy_from_counts(distributions[h]) for h in HORIZONS}
    support_sizes = {h: len(distributions[h]) for h in HORIZONS}
    exact_counts = {h: len(exact_by_h[h]) for h in HORIZONS}
    reach_counts = {h: len(reach_by_h[h]) for h in HORIZONS}
    growth_rates = _growth_rates(reach_counts)
    recurrence = recurrence_rate([frozenset(probe.fn(state) for state in exact_by_h[h]) for h in HORIZONS])
    motif = motif_reuse([distributions[h] for h in HORIZONS])
    compression = compression_proxy([distributions[h] for h in HORIZONS])
    predictive = _predictive_information(distributions)
    conditional_entropy = _conditional_entropy_proxy(entropies, predictive)
    saturation_horizon = _saturation_horizon(reach_counts)
    collapse = int(saturation_horizon <= 2 and reach_counts[max(HORIZONS)] <= 4)
    cycle = int(_cycle_indicator(exact_by_h))
    js_values = {}
    kl_values = {}
    for h in HORIZONS:
        null_counts = null_counts_by_h.get(h, {}) if null_counts_by_h else {}
        js_values[h] = js_divergence(distributions[h], null_counts) if null_counts else 0.0
        kl_values[h] = smoothed_kl(distributions[h], null_counts) if null_counts else 0.0
    profile = {
        "system_id": system.system_id,
        "family": system.family,
        "start_state_json": str(start),
        "probe_name": probe.name,
        "probe_mode": probe.mode,
        "reach_H16": reach_counts[max(HORIZONS)],
        "exact_H16": exact_counts[max(HORIZONS)],
        "growth_mean": sum(growth_rates.values()) / max(1, len(growth_rates)),
        "entropy_mean": sum(entropies.values()) / len(entropies),
        "signature_support_mean": sum(support_sizes.values()) / len(support_sizes),
        "recurrence_rate": recurrence,
        "motif_reuse": motif,
        "transition_motif_count_mean": motif * len(distributions),
        "predictive_information": predictive,
        "conditional_entropy_proxy": conditional_entropy,
        "compression_proxy": compression,
        "saturation_horizon": saturation_horizon,
        "cycle_indicator": cycle,
        "collapse_indicator": collapse,
        "JS_to_null_mean": sum(js_values.values()) / len(js_values),
        "smoothed_KL_to_null_mean": sum(kl_values.values()) / len(kl_values),
    }
    profile["profile_class"] = profile_class(profile)
    distribution_rows = []
    profile_rows = []
    for h in HORIZONS:
        profile_rows.append(
            {
                **{k: profile[k] for k in ("system_id", "family", "probe_name", "probe_mode", "profile_class")},
                "H": h,
                "reach_count": reach_counts[h],
                "exact_count": exact_counts[h],
                "growth_rate": growth_rates.get(h, 0.0),
                "signature_entropy": entropies[h],
                "signature_support_size": support_sizes[h],
                "conditional_entropy_proxy": conditional_entropy,
                "JS_to_null": js_values[h],
                "smoothed_KL_to_null": kl_values[h],
            }
        )
        total = sum(distributions[h].values())
        for signature, count in sorted(distributions[h].items(), key=lambda item: str(item[0])):
            distribution_rows.append(
                {
                    "system_id": system.system_id,
                    "family": system.family,
                    "probe_name": probe.name,
                    "H": h,
                    "signature": str(signature),
                    "count": count,
                    "probability": count / max(1, total),
                }
            )
    return profile, profile_rows, distribution_rows


def edge_deformations(system: LandscapeSystem, probe: Probe) -> list[dict[str, float | int | str]]:
    rows = []
    sample_edges = []
    for source, targets in system.edges.items():
        for target in targets:
            sample_edges.append((source, target))
            if len(sample_edges) >= 64:
                break
        if len(sample_edges) >= 64:
            break
    for source, target in sample_edges:
        source_profile, _source_rows, _source_dist = future_profile(system, source, probe)
        target_profile, _target_rows, _target_dist = future_profile(system, target, probe)
        rows.append(
            {
                "system_id": system.system_id,
                "family": system.family,
                "probe_name": probe.name,
                "future_entropy_delta": float(target_profile["entropy_mean"]) - float(source_profile["entropy_mean"]),
                "reach_growth_delta": float(target_profile["growth_mean"]) - float(source_profile["growth_mean"]),
                "predictive_information_delta": float(target_profile["predictive_information"]) - float(source_profile["predictive_information"]),
                "conditional_entropy_delta": float(target_profile["conditional_entropy_proxy"]) - float(source_profile["conditional_entropy_proxy"]),
                "recurrence_delta": float(target_profile["recurrence_rate"]) - float(source_profile["recurrence_rate"]),
                "compression_delta": float(target_profile["compression_proxy"]) - float(source_profile["compression_proxy"]),
                "collapse_indicator_delta": int(target_profile["collapse_indicator"]) - int(source_profile["collapse_indicator"]),
                "cycle_indicator_delta": int(target_profile["cycle_indicator"]) - int(source_profile["cycle_indicator"]),
                "JS_to_null_delta": float(target_profile["JS_to_null_mean"]) - float(source_profile["JS_to_null_mean"]),
            }
        )
    return rows


def _growth_rates(reach_counts: dict[int, int]) -> dict[int, float]:
    rates = {}
    previous_h = None
    previous_count = None
    for h in HORIZONS:
        if previous_h is not None and previous_count is not None:
            rates[h] = (reach_counts[h] - previous_count) / max(1, h - previous_h)
        previous_h = h
        previous_count = reach_counts[h]
    return rates


def _predictive_information(distributions: dict[int, dict[object, int]]) -> float:
    values = []
    prev = None
    for h in HORIZONS:
        current = distributions[h]
        if prev is not None:
            values.append(1.0 - js_divergence(current, prev))
        prev = current
    return sum(values) / len(values) if values else 0.0


def _conditional_entropy_proxy(entropies: dict[int, float], predictive_information: float) -> float:
    entropy_mean = sum(entropies.values()) / len(entropies)
    return max(0.0, entropy_mean - predictive_information)


def _saturation_horizon(reach_counts: dict[int, int]) -> int:
    final = reach_counts[max(HORIZONS)]
    for h in HORIZONS:
        if reach_counts[h] == final:
            return h
    return max(HORIZONS)


def _cycle_indicator(exact_by_h: dict[int, frozenset[State]]) -> bool:
    seen: dict[frozenset[State], int] = {}
    for h in HORIZONS:
        frontier = exact_by_h[h]
        if frontier in seen and h - seen[frontier] > 0 and len(frontier) <= 8:
            return True
        seen[frontier] = h
    return False
