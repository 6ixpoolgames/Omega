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
    null_replicate_counts_by_h: dict[str, list[dict[int, dict[object, int]]]] | None = None,
    null_transition_replicates: dict[str, list[dict[str, float]]] | None = None,
    horizons: tuple[int, ...] = HORIZONS,
) -> tuple[dict[str, float | int | str], list[dict[str, float | int | str]], list[dict[str, float | int | str]]]:
    reach_by_h = {h: reachable(system, start, h) for h in horizons}
    exact_by_h = {h: exact_frontier(system, start, h) for h in horizons}
    distributions = {h: signature_distribution(exact_by_h[h], probe) for h in horizons}
    entropies = {h: entropy_from_counts(distributions[h]) for h in horizons}
    support_sizes = {h: len(distributions[h]) for h in horizons}
    exact_counts = {h: len(exact_by_h[h]) for h in horizons}
    reach_counts = {h: len(reach_by_h[h]) for h in horizons}
    growth_rates = _growth_rates(reach_counts, horizons)
    recurrence = recurrence_rate([frozenset(probe.fn(state) for state in exact_by_h[h]) for h in horizons])
    motif = motif_reuse([distributions[h] for h in horizons])
    compression = compression_proxy([distributions[h] for h in horizons])
    adjacent_similarity = _adjacent_distribution_similarity(distributions, horizons)
    conditional_entropy = _conditional_entropy_proxy(entropies, adjacent_similarity)
    transition_summary, transition_rows = transition_information_summary(system, start, probe, horizons)
    saturation_horizon = _saturation_horizon(reach_counts, horizons)
    max_horizon = max(horizons)
    collapse = int(saturation_horizon <= 2 and reach_counts[max_horizon] <= 4)
    cycle = int(_cycle_indicator(exact_by_h, horizons))
    js_values = {}
    kl_values = {}
    for h in horizons:
        null_counts = null_counts_by_h.get(h, {}) if null_counts_by_h else {}
        js_values[h] = js_divergence(distributions[h], null_counts) if null_counts else 0.0
        kl_values[h] = smoothed_kl(distributions[h], null_counts) if null_counts else 0.0
    null_bundle = _null_bundle_summary(distributions, null_bundle_counts_by_h or {})
    null_transition = _null_transition_summary(transition_summary, null_transition_summaries or {})
    null_replicate_ranks = _null_replicate_rank_summary(
        distributions,
        transition_summary,
        null_bundle_counts_by_h or {},
        null_replicate_counts_by_h or {},
        null_transition_replicates or {},
    )
    reach_saturation_fraction = reach_counts[max_horizon] / max(1, len(system.states))
    exact_saturation_fraction = exact_counts[max_horizon] / max(1, len(system.states))
    profile = {
        "system_id": system.system_id,
        "family": system.family,
        "start_state_json": str(start),
        "probe_name": probe.name,
        "probe_mode": probe.mode,
        "probe_family": probe.probe_family,
        "probe_arity": probe.arity,
        "reach_H16": reach_counts.get(16, reach_counts[max_horizon]),
        "exact_H16": exact_counts.get(16, exact_counts[max_horizon]),
        "reach_Hmax": reach_counts[max_horizon],
        "exact_Hmax": exact_counts[max_horizon],
        "max_horizon": max_horizon,
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
        **null_replicate_ranks,
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
    for h in horizons:
        per_null_h = {}
        for null_name, by_h in sorted((null_bundle_counts_by_h or {}).items()):
            null_counts = by_h.get(h, {})
            per_null_h[f"JS_to_null_{null_name}"] = js_divergence(distributions[h], null_counts) if null_counts else 0.0
            per_null_h[f"KL_to_null_{null_name}"] = smoothed_kl(distributions[h], null_counts) if null_counts else 0.0
            replicate_by_h = (null_replicate_counts_by_h or {}).get(null_name, [])
            if replicate_by_h:
                observed_js = per_null_h[f"JS_to_null_{null_name}"]
                observed_kl = per_null_h[f"KL_to_null_{null_name}"]
                replicate_js = [js_divergence(distributions[h], replicate.get(h, {})) for replicate in replicate_by_h]
                replicate_kl = [smoothed_kl(distributions[h], replicate.get(h, {})) for replicate in replicate_by_h]
                per_null_h[f"JS_rank_against_replicates_{null_name}"] = _rank_fraction(float(observed_js), replicate_js)
                per_null_h[f"KL_rank_against_replicates_{null_name}"] = _rank_fraction(float(observed_kl), replicate_kl)
        per_null_h.update(
            {
                key: value
                for key, value in profile.items()
                if key.startswith(("MI_delta_vs_null_", "motif_delta_vs_null_", "MI_rank_against_replicates_", "motif_rank_against_replicates_"))
            }
        )
        per_null_h["MI_delta_vs_null"] = profile["MI_delta_vs_null"]
        per_null_h["signature_transition_motif_reuse_delta_vs_null"] = profile["signature_transition_motif_reuse_delta_vs_null"]
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
                "reach_saturation_fraction_H": reach_counts[h] / max(1, len(system.states)),
                "exact_saturation_fraction_H": exact_counts[h] / max(1, len(system.states)),
                "signature_entropy_H": entropies[h],
                "signature_support_size_H": support_sizes[h],
                "conditional_entropy_proxy": conditional_entropy,
                "JS_to_null": js_values[h],
                "smoothed_KL_to_null": kl_values[h],
                **per_null_h,
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


def transition_information_summary(system: LandscapeSystem, start: State, probe: Probe, horizons: tuple[int, ...] = HORIZONS) -> tuple[dict[str, float], list[dict[str, float | int | str]]]:
    rows = []
    mi_values = []
    conditional_values = []
    grammar_values = []
    motif_values = []
    for h in horizons:
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


def _growth_rates(reach_counts: dict[int, int], horizons: tuple[int, ...] = HORIZONS) -> dict[int, float]:
    rates = {}
    previous_h = None
    previous_count = None
    for h in horizons:
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
        horizons = tuple(sorted(distributions))
        js_values = [js_divergence(distributions[h], by_h.get(h, {})) for h in horizons]
        kl_values = [smoothed_kl(distributions[h], by_h.get(h, {})) for h in horizons]
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
    mi_nulls = []
    motif_nulls = []
    for null_name, summary in sorted(null_transition_summaries.items()):
        mi_null = summary.get("signature_transition_MI_mean", 0.0)
        motif_null = summary.get("signature_transition_motif_reuse_mean", 0.0)
        mi_nulls.append(mi_null)
        motif_nulls.append(motif_null)
        output[f"MI_delta_vs_null_{null_name}"] = transition_summary["signature_transition_MI_mean"] - mi_null
        output[f"motif_delta_vs_null_{null_name}"] = transition_summary["signature_transition_motif_reuse_mean"] - motif_null
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


def _null_replicate_rank_summary(
    distributions: dict[int, dict[object, int]],
    transition_summary: dict[str, float],
    null_bundle_counts_by_h: dict[str, dict[int, dict[object, int]]],
    null_replicate_counts_by_h: dict[str, list[dict[int, dict[object, int]]]],
    null_transition_replicates: dict[str, list[dict[str, float]]],
) -> dict[str, float | int]:
    output: dict[str, float | int] = {}
    horizons = tuple(sorted(distributions))
    for null_name, primary_by_h in sorted(null_bundle_counts_by_h.items()):
        replicates = null_replicate_counts_by_h.get(null_name, [])
        if not replicates:
            continue
        observed_js = [
            js_divergence(distributions[h], primary_by_h.get(h, {}))
            for h in horizons
        ]
        observed_kl = [
            smoothed_kl(distributions[h], primary_by_h.get(h, {}))
            for h in horizons
        ]
        replicate_js = [
            sum(js_divergence(distributions[h], replicate.get(h, {})) for h in horizons) / len(horizons)
            for replicate in replicates
        ]
        replicate_kl = [
            sum(smoothed_kl(distributions[h], replicate.get(h, {})) for h in horizons) / len(horizons)
            for replicate in replicates
        ]
        output[f"JS_rank_against_replicates_{null_name}"] = _rank_fraction(sum(observed_js) / len(observed_js), replicate_js)
        output[f"KL_rank_against_replicates_{null_name}"] = _rank_fraction(sum(observed_kl) / len(observed_kl), replicate_kl)
        output[f"null_replicate_count_{null_name}"] = len(replicates)
    for null_name, replicates in sorted(null_transition_replicates.items()):
        if not replicates:
            continue
        output[f"MI_rank_against_replicates_{null_name}"] = _rank_fraction(
            transition_summary["signature_transition_MI_mean"],
            [replicate.get("signature_transition_MI_mean", 0.0) for replicate in replicates],
        )
        output[f"motif_rank_against_replicates_{null_name}"] = _rank_fraction(
            transition_summary["signature_transition_motif_reuse_mean"],
            [replicate.get("signature_transition_motif_reuse_mean", 0.0) for replicate in replicates],
        )
    return output


def _rank_fraction(observed: float, replicate_values: list[float]) -> float:
    if not replicate_values:
        return 0.0
    return sum(observed >= value for value in replicate_values) / len(replicate_values)


def _adjacent_distribution_similarity(distributions: dict[int, dict[object, int]], horizons: tuple[int, ...] = HORIZONS) -> float:
    values = []
    prev = None
    for h in horizons:
        current = distributions[h]
        if prev is not None:
            values.append(1.0 - js_divergence(current, prev))
        prev = current
    return sum(values) / len(values) if values else 0.0


def _conditional_entropy_proxy(entropies: dict[int, float], predictive_information: float) -> float:
    entropy_mean = sum(entropies.values()) / len(entropies)
    return max(0.0, entropy_mean - predictive_information)


def _saturation_horizon(reach_counts: dict[int, int], horizons: tuple[int, ...] = HORIZONS) -> int:
    final = reach_counts[max(horizons)]
    for h in horizons:
        if reach_counts[h] == final:
            return h
    return max(horizons)


def _cycle_indicator(exact_by_h: dict[int, frozenset[State]], horizons: tuple[int, ...] = HORIZONS) -> bool:
    seen: dict[frozenset[State], int] = {}
    for h in horizons:
        frontier = exact_by_h[h]
        if frontier in seen and h - seen[frontier] > 0 and len(frontier) <= 8:
            return True
        seen[frontier] = h
    return False
