from __future__ import annotations

from collections import Counter

from .detectors import (
    compression_proxy,
    conditional_entropy_from_joint,
    control_relative_profile_class,
    entropy_from_counts,
    js_divergence,
    motif_reuse,
    mutual_information_from_joint,
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
    null_bundle_counts_by_h: dict[str, dict[int, dict[object, int]]] | None = None,
    null_transition_summaries: dict[str, dict[str, float]] | None = None,
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
    adjacent_similarity = _adjacent_distribution_similarity(distributions)
    conditional_entropy = _conditional_entropy_proxy(entropies, adjacent_similarity)
    transition_summary, transition_rows = transition_information_summary(system, start, probe)
    saturation_horizon = _saturation_horizon(reach_counts)
    collapse = int(saturation_horizon <= 2 and reach_counts[max(HORIZONS)] <= 4)
    cycle = int(_cycle_indicator(exact_by_h))
    js_values = {}
    kl_values = {}
    for h in HORIZONS:
        null_counts = null_counts_by_h.get(h, {}) if null_counts_by_h else {}
        js_values[h] = js_divergence(distributions[h], null_counts) if null_counts else 0.0
        kl_values[h] = smoothed_kl(distributions[h], null_counts) if null_counts else 0.0
    null_bundle = _null_bundle_summary(distributions, null_bundle_counts_by_h or {})
    null_transition = _null_transition_summary(transition_summary, null_transition_summaries or {})
    reach_saturation_fraction = reach_counts[max(HORIZONS)] / max(1, len(system.states))
    exact_saturation_fraction = exact_counts[max(HORIZONS)] / max(1, len(system.states))
    profile = {
        "system_id": system.system_id,
        "family": system.family,
        "start_state_json": str(start),
        "probe_name": probe.name,
        "probe_mode": probe.mode,
        "probe_family": probe.probe_family,
        "probe_arity": probe.arity,
        "reach_H16": reach_counts[max(HORIZONS)],
        "exact_H16": exact_counts[max(HORIZONS)],
        "growth_mean": sum(growth_rates.values()) / max(1, len(growth_rates)),
        "entropy_mean": sum(entropies.values()) / len(entropies),
        "signature_support_mean": sum(support_sizes.values()) / len(support_sizes),
        "recurrence_rate": recurrence,
        "motif_reuse": motif,
        "transition_motif_count_mean": motif * len(distributions),
        "predictive_information": adjacent_similarity,
        "adjacent_distribution_similarity": adjacent_similarity,
        "conditional_entropy_proxy": conditional_entropy,
        "compression_proxy": compression,
        "signature_reuse_fraction": compression,
        "signature_reuse_scaled": motif * len(distributions),
        **transition_summary,
        **null_bundle,
        **null_transition,
        "saturation_horizon": saturation_horizon,
        "reach_saturation_fraction": reach_saturation_fraction,
        "exact_saturation_fraction": exact_saturation_fraction,
        "saturation_dominated": int(reach_saturation_fraction >= 0.95 or exact_saturation_fraction >= 0.75),
        "cycle_indicator": cycle,
        "collapse_indicator": collapse,
        "JS_to_null_mean": sum(js_values.values()) / len(js_values),
        "smoothed_KL_to_null_mean": sum(kl_values.values()) / len(kl_values),
    }
    profile["control_relative_pass_count"] = int(profile["control_relative_pass_count"]) + int(profile["JS_rank_against_nulls"] >= 2) + int(profile["signature_reuse_fraction"] < 0.995)
    profile["heuristic_profile_class_v0"] = profile_class(profile)
    profile["profile_class"] = profile["heuristic_profile_class_v0"]
    profile["control_relative_profile_class_v1"] = control_relative_profile_class(profile)
    profile["local_profile_class_v1_1"] = (
        "local_structured_candidate"
        if profile["control_relative_profile_class_v1"] == "structured_propagation"
        else str(profile["control_relative_profile_class_v1"])
    )
    distribution_rows = []
    profile_rows = []
    for h in HORIZONS:
        profile_rows.append(
            {
                **{k: profile[k] for k in ("system_id", "family", "probe_name", "probe_mode", "probe_family", "profile_class", "control_relative_profile_class_v1")},
                "H": h,
                "row_kind": "future_profile",
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
    return profile, profile_rows + transition_rows, distribution_rows


def transition_information_summary(system: LandscapeSystem, start: State, probe: Probe) -> tuple[dict[str, float], list[dict[str, float | int | str]]]:
    rows = []
    mi_values = []
    conditional_values = []
    grammar_values = []
    motif_values = []
    for h in HORIZONS:
        frontier = exact_frontier(system, start, h)
        joint_counts = _transition_joint_counts(system, frontier, probe)
        mi = mutual_information_from_joint(joint_counts)
        conditional = conditional_entropy_from_joint(joint_counts)
        grammar_size = len(joint_counts)
        motif = _transition_motif_reuse(joint_counts)
        mi_values.append(mi)
        conditional_values.append(conditional)
        grammar_values.append(grammar_size)
        motif_values.append(motif)
        rows.append(
            {
                "system_id": system.system_id,
                "family": system.family,
                "probe_name": probe.name,
                "probe_family": probe.probe_family,
                "H": h,
                "row_kind": "transition_information",
                "signature_transition_MI_by_h": mi,
                "signature_transition_conditional_entropy_by_h": conditional,
                "signature_transition_entropy_rate_proxy_by_h": conditional,
                "signature_transition_grammar_size_by_h": grammar_size,
                "signature_transition_motif_reuse_by_h": motif,
            }
        )
    return (
        {
            "signature_transition_MI_mean": sum(mi_values) / len(mi_values),
            "signature_transition_conditional_entropy_mean": sum(conditional_values) / len(conditional_values),
            "signature_transition_entropy_rate_proxy": sum(conditional_values) / len(conditional_values),
            "signature_transition_grammar_size_mean": sum(grammar_values) / len(grammar_values),
            "signature_transition_motif_reuse_mean": sum(motif_values) / len(motif_values),
        },
        rows,
    )


def _transition_joint_counts(system: LandscapeSystem, frontier: frozenset[State], probe: Probe) -> dict[tuple[object, object], int]:
    counts: Counter[tuple[object, object]] = Counter()
    for state in frontier:
        source_signature = probe.fn(state)
        for target in system.edges[state]:
            counts[(source_signature, probe.fn(target))] += 1
    return dict(counts)


def _transition_motif_reuse(joint_counts: dict[tuple[object, object], int]) -> float:
    total = sum(joint_counts.values())
    if total <= 0:
        return 0.0
    repeated = sum(count for count in joint_counts.values() if count > 1)
    return repeated / total


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


def _null_bundle_summary(distributions: dict[int, dict[object, int]], null_bundle_counts_by_h: dict[str, dict[int, dict[object, int]]]) -> dict[str, float | int]:
    output: dict[str, float | int] = {}
    js_means = []
    kl_means = []
    rank_wins = 0
    for null_name, by_h in sorted(null_bundle_counts_by_h.items()):
        js_values = [js_divergence(distributions[h], by_h.get(h, {})) for h in HORIZONS]
        kl_values = [smoothed_kl(distributions[h], by_h.get(h, {})) for h in HORIZONS]
        js_mean = sum(js_values) / len(js_values)
        kl_mean = sum(kl_values) / len(kl_values)
        output[f"null_JS_{null_name}"] = js_mean
        output[f"null_KL_{null_name}"] = kl_mean
        js_means.append(js_mean)
        kl_means.append(kl_mean)
        if js_mean > 0.05:
            rank_wins += 1
    if js_means:
        output["JS_to_null_bundle_min"] = min(js_means)
        output["JS_to_null_bundle_max"] = max(js_means)
        output["JS_to_null_bundle_mean"] = sum(js_means) / len(js_means)
        output["KL_to_null_bundle_min"] = min(kl_means)
        output["KL_to_null_bundle_max"] = max(kl_means)
        output["KL_to_null_bundle_mean"] = sum(kl_means) / len(kl_means)
    else:
        output["JS_to_null_bundle_min"] = 0.0
        output["JS_to_null_bundle_max"] = 0.0
        output["JS_to_null_bundle_mean"] = 0.0
        output["KL_to_null_bundle_min"] = 0.0
        output["KL_to_null_bundle_max"] = 0.0
        output["KL_to_null_bundle_mean"] = 0.0
    output["JS_rank_against_nulls"] = rank_wins
    output["KL_rank_against_nulls"] = sum(1 for value in kl_means if value > 0.05)
    return output


def _null_transition_summary(transition_summary: dict[str, float], null_transition_summaries: dict[str, dict[str, float]]) -> dict[str, float | int]:
    output: dict[str, float | int] = {}
    if not null_transition_summaries:
        output["null_transition_MI_max"] = 0.0
        output["null_transition_motif_reuse_max"] = 0.0
        output["MI_delta_vs_null"] = 0.0
        output["signature_transition_motif_reuse_delta_vs_null"] = 0.0
        output["control_relative_pass_count"] = 0
        return output
    mi_nulls = [summary.get("signature_transition_MI_mean", 0.0) for summary in null_transition_summaries.values()]
    motif_nulls = [summary.get("signature_transition_motif_reuse_mean", 0.0) for summary in null_transition_summaries.values()]
    recurrence_nulls = [summary.get("recurrence_rate", 0.0) for summary in null_transition_summaries.values()]
    mi_delta = transition_summary["signature_transition_MI_mean"] - max(mi_nulls)
    motif_delta = transition_summary["signature_transition_motif_reuse_mean"] - max(motif_nulls)
    output["null_transition_MI_max"] = max(mi_nulls)
    output["null_transition_motif_reuse_max"] = max(motif_nulls)
    output["MI_delta_vs_null"] = mi_delta
    output["signature_transition_motif_reuse_delta_vs_null"] = motif_delta
    output["recurrence_delta_vs_null"] = -max(recurrence_nulls) if recurrence_nulls else 0.0
    output["control_relative_pass_count"] = int(mi_delta > 0.05) + int(motif_delta > 0.05)
    return output


def _adjacent_distribution_similarity(distributions: dict[int, dict[object, int]]) -> float:
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
