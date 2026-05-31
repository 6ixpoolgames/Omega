from __future__ import annotations

import itertools
import json
import math
from dataclasses import asdict
from statistics import mean, pstdev

from .relation_generator import RelationParams, generate_relation_system
from .substrate import LandscapeSystem, State


CONSTRAINT_TEMPLATE_CURRENT = "constraint_template_current"
LOCALITY_ONLY = "locality_only"
SMOOTH_RANDOM_POTENTIAL = "smooth_random_potential"
BUDGET_CONSERVATION = "budget_conservation"
DIRECTIONAL_ASYMMETRY = "directional_asymmetry"
PRESERVATION_ASYMMETRY = "preservation_asymmetry"
COMBINED_ASYMMETRY = "combined_asymmetry"
MACRO_INVARIANT_ALIASES = {
    "macro_invariant": BUDGET_CONSERVATION,
    "macro-invariant": BUDGET_CONSERVATION,
    "macro_asymmetry_constrained": BUDGET_CONSERVATION,
    "asymmetry_constrained": BUDGET_CONSERVATION,
    "asymmetry-constrained": BUDGET_CONSERVATION,
    "asymmetry_constrained_transition_energy": BUDGET_CONSERVATION,
    "asymmetry-constrained_transition_energy": BUDGET_CONSERVATION,
    "conserved_distinction": BUDGET_CONSERVATION,
    "invariant_constrained": BUDGET_CONSERVATION,
    "asymmetry_preservation": PRESERVATION_ASYMMETRY,
    "asymmetry-preservation": PRESERVATION_ASYMMETRY,
    "macro_invariant_preservation": PRESERVATION_ASYMMETRY,
    "macro-invariant-preservation": PRESERVATION_ASYMMETRY,
    "directional_asymmetry_field": DIRECTIONAL_ASYMMETRY,
    "combined_directional_preservation": COMBINED_ASYMMETRY,
}
TRANSITION_ENERGY_FAMILIES = (
    CONSTRAINT_TEMPLATE_CURRENT,
    LOCALITY_ONLY,
    SMOOTH_RANDOM_POTENTIAL,
    BUDGET_CONSERVATION,
    DIRECTIONAL_ASYMMETRY,
    PRESERVATION_ASYMMETRY,
    COMBINED_ASYMMETRY,
)


def generate_job_baseline_system(job: dict[str, object], params: RelationParams, seed: int) -> LandscapeSystem:
    family = canonical_transition_energy_family(str(job.get("substrate_family", CONSTRAINT_TEMPLATE_CURRENT) or CONSTRAINT_TEMPLATE_CURRENT))
    if family == CONSTRAINT_TEMPLATE_CURRENT:
        system = generate_relation_system(params, seed)
        return with_substrate_metadata(system, family, {})
    return generate_transition_energy_system(params, seed, job, family)


def canonical_transition_energy_family(family: str) -> str:
    return MACRO_INVARIANT_ALIASES.get(str(family), str(family))


def generate_transition_energy_system(
    params: RelationParams,
    seed: int,
    job: dict[str, object],
    family: str,
) -> LandscapeSystem:
    if family not in TRANSITION_ENERGY_FAMILIES:
        raise ValueError(f"unknown transition-energy substrate family: {family}")
    states = enumerate_states(params.coordinate_count, params.alphabet_size)
    candidates_by_state = {
        state: candidate_successors(state, params.alphabet_size, params.update_footprint)
        for state in states
    }
    potential = potential_field(states, params, seed, job) if family == SMOOTH_RANDOM_POTENTIAL else {}
    asymmetry = asymmetry_field(states, params, seed, job) if family in {DIRECTIONAL_ASYMMETRY, COMBINED_ASYMMETRY} else {}
    budget = budget_field(states, params, job) if family in {BUDGET_CONSERVATION, PRESERVATION_ASYMMETRY, COMBINED_ASYMMETRY} else {}
    edges: dict[State, tuple[State, ...]] = {}
    diagnostics: list[float] = []
    roughness_strength = transition_float(job, "transition_roughness_strength", params.roughness_strength)
    for source in states:
        scored = [
            (
                transition_energy(
                    source,
                    target,
                    family,
                    params,
                    seed,
                    roughness_strength,
                    potential,
                    asymmetry,
                    budget,
                    job,
                ),
                target,
            )
            for target in candidates_by_state[source]
        ]
        scored.sort(key=lambda item: (item[0], item[1]))
        selected = scored[: max(1, params.out_degree_target)]
        diagnostics.extend(score for score, _target in selected)
        edges[source] = tuple(target for _score, target in selected)
    edges = apply_reversibility(states, edges, params.reversibility_fraction, seed + 11_003)
    metadata = transition_metadata(params, seed, family, states, edges, diagnostics, potential, asymmetry, budget, job)
    return LandscapeSystem(
        system_id=f"{params.parameter_set_id}_{family}_seed{seed}",
        seed=seed,
        family=f"{params.parameter_set_id}_{family}",
        states=states,
        edges=edges,
        transform_names=("top_m_transition_energy",),
        metadata=metadata,
    )


def transition_energy(
    source: State,
    target: State,
    family: str,
    params: RelationParams,
    seed: int,
    roughness_strength: float,
    potential: dict[State, float],
    asymmetry: dict[State, float],
    budget: dict[State, float],
    job: dict[str, object],
) -> float:
    distance = hamming(source, target)
    roughness = roughness_strength * stable_unit(f"{seed}:{source}:{target}:roughness")
    if family == LOCALITY_ONLY:
        return distance + roughness
    if family == SMOOTH_RANDOM_POTENTIAL:
        beta = transition_float(job, "potential_beta", max(0.25, params.asymmetry_strength or 0.5))
        return distance + beta * (potential[target] - potential[source]) + roughness
    if family == BUDGET_CONSERVATION:
        weight = transition_float(job, "budget_weight", max(0.25, params.constraint_strength))
        return distance + weight * abs(budget[target] - budget[source]) + roughness
    if family == DIRECTIONAL_ASYMMETRY:
        alpha = transition_float(job, "asymmetry_alpha", max(0.25, params.asymmetry_strength or 0.5))
        return distance + alpha * (asymmetry[target] - asymmetry[source]) + roughness
    if family == PRESERVATION_ASYMMETRY:
        beta = macro_invariant_beta(job, params)
        return distance + beta * abs(budget[target] - budget[source]) + roughness
    if family == COMBINED_ASYMMETRY:
        alpha = transition_float(job, "asymmetry_alpha", max(0.25, params.asymmetry_strength or 0.5))
        beta = macro_invariant_beta(job, params)
        return distance + alpha * (asymmetry[target] - asymmetry[source]) + beta * abs(budget[target] - budget[source]) + roughness
    raise ValueError(f"unsupported transition-energy family: {family}")


def enumerate_states(coordinate_count: int, alphabet_size: int) -> tuple[State, ...]:
    return tuple(itertools.product(range(alphabet_size), repeat=coordinate_count))


def candidate_successors(state: State, alphabet_size: int, footprint: int) -> tuple[State, ...]:
    out: set[State] = set()
    coords = range(len(state))
    for size in range(1, max(1, footprint) + 1):
        for selected in itertools.combinations(coords, size):
            choices = [[value for value in range(alphabet_size) if value != state[coord]] for coord in selected]
            for replacements in itertools.product(*choices):
                values = list(state)
                for coord, value in zip(selected, replacements):
                    values[coord] = value
                out.add(tuple(values))
    return tuple(sorted(out))


def potential_field(states: tuple[State, ...], params: RelationParams, seed: int, job: dict[str, object]) -> dict[State, float]:
    potential_seed = int(transition_float(job, "potential_seed", seed + 71_003))
    smoothness = max(0.0, min(1.0, transition_float(job, "potential_smoothness", 0.85)))
    scale = transition_float(job, "potential_scale", 1.0)
    return smooth_state_field(states, params, potential_seed, smoothness, scale)


def asymmetry_field(states: tuple[State, ...], params: RelationParams, seed: int, job: dict[str, object]) -> dict[State, float]:
    field_seed = int(transition_float(job, "asymmetry_field_seed", seed + 73_001))
    smoothness = max(0.0, min(1.0, transition_float(job, "asymmetry_field_smoothness", 0.65)))
    scale = transition_float(job, "asymmetry_field_scale", 1.0)
    return smooth_state_field(states, params, field_seed, smoothness, scale)


def smooth_state_field(
    states: tuple[State, ...],
    params: RelationParams,
    field_seed: int,
    smoothness: float,
    scale: float,
) -> dict[State, float]:
    coordinate_weights = {
        (coord, value): 2.0 * stable_unit(f"{field_seed}:coord:{coord}:{value}") - 1.0
        for coord in range(params.coordinate_count)
        for value in range(params.alphabet_size)
    }
    raw = {}
    for state in states:
        additive = sum(coordinate_weights[(coord, value)] for coord, value in enumerate(state)) / max(1, len(state))
        local_noise = 2.0 * stable_unit(f"{field_seed}:state:{state}") - 1.0
        raw[state] = scale * (smoothness * additive + (1.0 - smoothness) * local_noise)
    avg = mean(raw.values()) if raw else 0.0
    return {state: value - avg for state, value in raw.items()}


def budget_field(states: tuple[State, ...], params: RelationParams, job: dict[str, object]) -> dict[State, float]:
    budget_kind = str(job.get("macro_invariant_kind", job.get("budget_kind", "total_coordinate_mass")) or "total_coordinate_mass")
    normalizer = max(1.0, params.coordinate_count * max(1, params.alphabet_size - 1))
    if budget_kind in {"hamming_weight", "hamming_weight_or_nonzero_count", "nonzero_count"}:
        return {state: sum(int(value != 0) for value in state) / max(1, len(state)) for state in states}
    if budget_kind in {"symbol_histogram_l2", "symbol_histogram_distance"}:
        uniform = 1.0 / max(1, params.alphabet_size)
        out = {}
        for state in states:
            counts = [state.count(symbol) / max(1, len(state)) for symbol in range(params.alphabet_size)]
            out[state] = math.sqrt(sum((count - uniform) ** 2 for count in counts))
        return out
    return {state: sum(state) / normalizer for state in states}


def apply_reversibility(
    states: tuple[State, ...],
    edges: dict[State, tuple[State, ...]],
    fraction: float,
    seed: int,
) -> dict[State, tuple[State, ...]]:
    if fraction <= 0:
        return edges
    out = {state: set(targets) for state, targets in edges.items()}
    for source, targets in edges.items():
        for target in targets:
            if stable_unit(f"{seed}:{source}:{target}:reverse") <= fraction:
                out.setdefault(target, set()).add(source)
    return {state: tuple(sorted(out.get(state, set()))) for state in states}


def transition_metadata(
    params: RelationParams,
    seed: int,
    family: str,
    states: tuple[State, ...],
    edges: dict[State, tuple[State, ...]],
    selected_scores: list[float],
    potential: dict[State, float],
    asymmetry: dict[State, float],
    budget: dict[State, float],
    job: dict[str, object],
) -> dict[str, object]:
    out_degrees = [len(edges.get(state, ())) for state in states]
    metadata: dict[str, object] = {
        **asdict(params),
        "state_coordinate_count": params.coordinate_count,
        "alphabet_size": params.alphabet_size,
        "state_count": len(states),
        "edge_count": sum(out_degrees),
        "mean_out_degree": mean(out_degrees) if out_degrees else 0.0,
        "substrate_family": family,
        "transition_energy_family": family,
        "transition_energy_form": transition_energy_form(family),
        "proposal_kernel": "hamming_ball_without_self",
        "selection_rule": "top_m_lowest_energy_candidates",
        "roughness_strength": transition_float(job, "transition_roughness_strength", params.roughness_strength),
        "reversibility_fraction": params.reversibility_fraction,
        "rewire_probability": 0.0,
        "constraint_json": "[]",
        "constraint_template_count": 0,
        "presentation": "transition_energy_relation",
        "selected_energy_mean": mean(selected_scores) if selected_scores else 0.0,
        "selected_energy_std": pstdev(selected_scores) if len(selected_scores) > 1 else 0.0,
    }
    if potential:
        values = list(potential.values())
        metadata.update({
            "potential_seed": int(transition_float(job, "potential_seed", seed + 71_003)),
            "potential_smoothness": transition_float(job, "potential_smoothness", 0.85),
            "potential_scale": transition_float(job, "potential_scale", 1.0),
            "potential_mean": mean(values),
            "potential_std": pstdev(values) if len(values) > 1 else 0.0,
            "potential_min": min(values),
            "potential_max": max(values),
            "potential_neighbor_correlation": neighbor_correlation(states, edges, potential),
        })
    if asymmetry:
        values = list(asymmetry.values())
        deltas = [asymmetry[target] - asymmetry[source] for source, targets in edges.items() for target in targets]
        metadata.update({
            "asymmetry_field_seed": int(transition_float(job, "asymmetry_field_seed", seed + 73_001)),
            "asymmetry_field_smoothness": transition_float(job, "asymmetry_field_smoothness", 0.65),
            "asymmetry_field_scale": transition_float(job, "asymmetry_field_scale", 1.0),
            "asymmetry_alpha": transition_float(job, "asymmetry_alpha", max(0.25, params.asymmetry_strength or 0.5)),
            "asymmetry_field_mean": mean(values),
            "asymmetry_field_std": pstdev(values) if len(values) > 1 else 0.0,
            "asymmetry_field_min": min(values),
            "asymmetry_field_max": max(values),
            "asymmetry_delta_mean": mean(deltas) if deltas else 0.0,
            "asymmetry_delta_distribution": json.dumps(distribution_summary(deltas), sort_keys=True),
            "asymmetry_neighbor_correlation": neighbor_correlation(states, edges, asymmetry),
        })
    if budget:
        values = list(budget.values())
        deltas = [abs(budget[target] - budget[source]) for source, targets in edges.items() for target in targets]
        budget_kind = str(job.get("macro_invariant_kind", job.get("budget_kind", "total_coordinate_mass")) or "total_coordinate_mass")
        beta = macro_invariant_beta(job, params)
        metadata.update({
            "budget_kind": budget_kind,
            "budget_weight": transition_float(job, "budget_weight", max(0.25, params.constraint_strength)),
            "budget_mean": mean(values),
            "budget_std": pstdev(values) if len(values) > 1 else 0.0,
            "budget_min": min(values),
            "budget_max": max(values),
            "budget_delta_mean": mean(deltas) if deltas else 0.0,
            "macro_invariant_kind": budget_kind,
            "macro_invariant_beta": beta,
            "macro_invariant_mean": mean(values),
            "macro_invariant_std": pstdev(values) if len(values) > 1 else 0.0,
            "macro_invariant_min": min(values),
            "macro_invariant_max": max(values),
            "macro_invariant_delta_mean": mean(deltas) if deltas else 0.0,
            "macro_invariant_value_distribution": json.dumps(distribution_summary(values), sort_keys=True),
            "macro_invariant_delta_distribution": json.dumps(distribution_summary(deltas), sort_keys=True),
        })
    if family == COMBINED_ASYMMETRY:
        metadata.update({
            "alpha_beta_pair": f"{metadata.get('asymmetry_alpha', '')}:{metadata.get('macro_invariant_beta', '')}",
            "interaction_read": "directional_plus_preservation_transition_energy",
        })
    return metadata


def with_substrate_metadata(system: LandscapeSystem, family: str, extra: dict[str, object]) -> LandscapeSystem:
    from dataclasses import replace

    metadata = {
        **system.metadata,
        "substrate_family": family,
        "transition_energy_family": family,
        "transition_energy_form": "current_constraint_template_scored_relation",
        "constraint_template_count": len(json.loads(str(system.metadata.get("constraint_json", "[]")))),
        **extra,
    }
    return replace(system, metadata=metadata)


def transition_energy_form(family: str) -> str:
    if family == LOCALITY_ONLY:
        return "hamming_distance_plus_seeded_roughness"
    if family == SMOOTH_RANDOM_POTENTIAL:
        return "hamming_distance_plus_beta_potential_delta_plus_seeded_roughness"
    if family == BUDGET_CONSERVATION:
        return "hamming_distance_plus_budget_delta_penalty_plus_seeded_roughness"
    if family == DIRECTIONAL_ASYMMETRY:
        return "hamming_distance_plus_alpha_directional_asymmetry_delta_plus_seeded_roughness"
    if family == PRESERVATION_ASYMMETRY:
        return "hamming_distance_plus_beta_macro_invariant_delta_penalty_plus_seeded_roughness"
    if family == COMBINED_ASYMMETRY:
        return "hamming_distance_plus_alpha_directional_delta_plus_beta_macro_invariant_delta_plus_seeded_roughness"
    return "current_constraint_template_scored_relation"


def macro_invariant_beta(job: dict[str, object], params: RelationParams) -> float:
    fallback = transition_float(job, "budget_weight", max(0.25, params.constraint_strength))
    return transition_float(job, "macro_invariant_beta", fallback)


def distribution_summary(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0.0, "mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    return {
        "count": float(len(values)),
        "mean": mean(values),
        "std": pstdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def neighbor_correlation(states: tuple[State, ...], edges: dict[State, tuple[State, ...]], values: dict[State, float]) -> float:
    pairs = [(values[source], values[target]) for source in states for target in edges.get(source, ())]
    if len(pairs) < 2:
        return 0.0
    left = [item[0] for item in pairs]
    right = [item[1] for item in pairs]
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in pairs)
    left_var = sum((a - left_mean) ** 2 for a in left)
    right_var = sum((b - right_mean) ** 2 for b in right)
    denom = math.sqrt(left_var * right_var)
    return numerator / denom if denom else 0.0


def hamming(left: State, right: State) -> int:
    return sum(int(a != b) for a, b in zip(left, right))


def transition_float(job: dict[str, object], key: str, default: float) -> float:
    try:
        value = job.get(key, default)
        if value in (None, ""):
            return float(default)
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return float(default)


def stable_unit(text: str) -> float:
    value = 2166136261
    for char in text:
        value ^= ord(char)
        value = (value * 16777619) % 2**32
    return value / 2**32
