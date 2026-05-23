from __future__ import annotations

from collections import Counter

from .landscape import HORIZONS, exact_frontier, signature_distribution
from .probes import Probe
from .substrate import LandscapeSystem, generate_system


def null_distribution_by_h(system: LandscapeSystem, probe: Probe) -> dict[int, dict[object, int]]:
    return null_bundle_distribution_by_h(system, probe, system.states[(system.seed + len(probe.name)) % len(system.states)])["degree"]


def null_bundle_distribution_by_h(system: LandscapeSystem, probe: Probe, start: tuple[int, int, int, int]) -> dict[str, dict[int, dict[object, int]]]:
    degree_system = generate_system(system.seed + 919_191, "degree_preserving_control")
    random_system = generate_system(system.seed + 272_101, "random_relation_control")
    return {
        "degree": _system_distribution_by_h(degree_system, probe, start),
        "random": _system_distribution_by_h(random_system, probe, start),
        "probe_marginal": _probe_marginal_distribution_by_h(system, probe, start),
        "frontier_size": _probe_marginal_distribution_by_h(system, probe, start),
    }


def _system_distribution_by_h(null_system: LandscapeSystem, probe: Probe, start: tuple[int, int, int, int]) -> dict[int, dict[object, int]]:
    if start not in null_system.edges:
        start = null_system.states[0]
    return {h: signature_distribution(exact_frontier(null_system, start, h), probe) for h in HORIZONS}


def _probe_marginal_distribution_by_h(system: LandscapeSystem, probe: Probe, start: tuple[int, int, int, int]) -> dict[int, dict[object, int]]:
    full_counts = Counter(probe.fn(state) for state in system.states)
    signatures = sorted(full_counts, key=str)
    total = sum(full_counts.values())
    out = {}
    for h in HORIZONS:
        observed_size = len(exact_frontier(system, start, h))
        if observed_size <= 0 or total <= 0:
            out[h] = {}
            continue
        expected = {signature: max(0, round(observed_size * full_counts[signature] / total)) for signature in signatures}
        drift = observed_size - sum(expected.values())
        index = 0
        while drift != 0 and signatures:
            signature = signatures[index % len(signatures)]
            if drift > 0:
                expected[signature] += 1
                drift -= 1
            elif expected[signature] > 0:
                expected[signature] -= 1
                drift += 1
            index += 1
        out[h] = {signature: count for signature, count in expected.items() if count > 0}
    return out


def null_systems(system: LandscapeSystem) -> dict[str, LandscapeSystem]:
    return {
        "degree": generate_system(system.seed + 919_191, "degree_preserving_control"),
        "random": generate_system(system.seed + 272_101, "random_relation_control"),
    }


def null_transition_metrics(system: LandscapeSystem, probe: Probe, start: tuple[int, int, int, int]) -> dict[str, dict[str, float]]:
    from .landscape import transition_information_summary

    out = {}
    for null_name, null_system in null_systems(system).items():
        null_start = start if start in null_system.edges else null_system.states[0]
        summary, _rows = transition_information_summary(null_system, null_start, probe)
        out[null_name] = summary
    marginal_mi = 0.0
    out["probe_marginal"] = {
        "signature_transition_MI_mean": marginal_mi,
        "signature_transition_conditional_entropy_mean": 0.0,
        "signature_transition_entropy_rate_proxy": 0.0,
        "signature_transition_grammar_size_mean": 0.0,
        "signature_transition_motif_reuse_mean": 0.0,
    }
    out["frontier_size"] = dict(out["probe_marginal"])
    return out
