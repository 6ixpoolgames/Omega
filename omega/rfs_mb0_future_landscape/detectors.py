from __future__ import annotations

import math
from collections import Counter


def entropy_from_counts(counts: dict[object, int]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    output = 0.0
    for count in counts.values():
        if count:
            p = count / total
            output -= p * math.log2(p)
    return output


def js_divergence(p_counts: dict[object, int], q_counts: dict[object, int]) -> float:
    keys = set(p_counts) | set(q_counts)
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    if p_total <= 0 or q_total <= 0:
        return 0.0
    p = {key: p_counts.get(key, 0) / p_total for key in keys}
    q = {key: q_counts.get(key, 0) / q_total for key in keys}
    m = {key: 0.5 * (p[key] + q[key]) for key in keys}
    return 0.5 * _kl_probs(p, m) + 0.5 * _kl_probs(q, m)


def smoothed_kl(p_counts: dict[object, int], q_counts: dict[object, int], alpha: float = 0.5) -> float:
    keys = set(p_counts) | set(q_counts)
    if not keys:
        return 0.0
    p_total = sum(p_counts.values()) + alpha * len(keys)
    q_total = sum(q_counts.values()) + alpha * len(keys)
    p = {key: (p_counts.get(key, 0) + alpha) / p_total for key in keys}
    q = {key: (q_counts.get(key, 0) + alpha) / q_total for key in keys}
    return _kl_probs(p, q)


def compression_proxy(signature_counts_by_h: list[dict[object, int]]) -> float:
    total_tokens = sum(sum(counts.values()) for counts in signature_counts_by_h)
    if total_tokens <= 0:
        return 0.0
    unique = len(set().union(*(set(counts) for counts in signature_counts_by_h)))
    repeated = total_tokens - unique
    return repeated / total_tokens


def recurrence_rate(exact_sets_by_h: list[frozenset[object]]) -> float:
    if len(exact_sets_by_h) < 2:
        return 0.0
    rates = []
    previous: set[object] = set()
    for exact_set in exact_sets_by_h:
        current = set(exact_set)
        if current:
            rates.append(len(current & previous) / len(current))
        previous |= current
    return sum(rates) / len(rates) if rates else 0.0


def motif_reuse(signature_counts_by_h: list[dict[object, int]]) -> float:
    if not signature_counts_by_h:
        return 0.0
    appearances: Counter[object] = Counter()
    for counts in signature_counts_by_h:
        appearances.update(set(counts))
    reusable = sum(1 for count in appearances.values() if count > 1)
    return reusable / max(1, len(appearances))


def profile_class(row: dict[str, float | int | str]) -> str:
    if str(row.get("probe_mode", "")) == "permissive":
        return "permissive_blur"
    if str(row.get("probe_mode", "")) == "strict":
        return "strict_fragmentation"
    if int(row["collapse_indicator"]):
        return "collapse_like"
    if int(row["cycle_indicator"]):
        return "cycle_like"
    if float(row["entropy_mean"]) > 1.2 and float(row["predictive_information"]) < 0.08 and float(row["recurrence_rate"]) < 0.15:
        return "noise_like"
    if (
        float(row["entropy_mean"]) > 0.3
        and float(row["predictive_information"]) >= 0.08
        and float(row["motif_reuse"]) >= 0.25
        and int(row["collapse_indicator"]) == 0
        and int(row["cycle_indicator"]) == 0
    ):
        return "structured_propagation"
    return "underdetermined"


def _kl_probs(p: dict[object, float], q: dict[object, float]) -> float:
    output = 0.0
    for key, p_value in p.items():
        q_value = q.get(key, 0.0)
        if p_value > 0 and q_value > 0:
            output += p_value * math.log2(p_value / q_value)
    return output

