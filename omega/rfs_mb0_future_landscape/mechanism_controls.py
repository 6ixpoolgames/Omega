from __future__ import annotations

import json
import random
from dataclasses import replace
from statistics import mean

from .relation_generator import RelationParams, generate_relation_system
from .substrate import LandscapeSystem, State


MECHANISM_CONTROL_NAMES = (
    "roughness_resampled_transform_control",
    "asymmetry_flip_sweep_control",
    "constraint_resampled_generation_control",
)


def make_mechanism_control_system(
    system: LandscapeSystem,
    control_name: str,
    seed: int,
    strength: float,
    params: RelationParams | None = None,
) -> LandscapeSystem:
    if control_name == "roughness_resampled_transform_control":
        return roughness_resampled_transform_control(system, seed, strength)
    if control_name == "asymmetry_flip_sweep_control":
        return asymmetry_flip_sweep_control(system, seed, strength)
    if control_name == "constraint_resampled_generation_control":
        if params is None:
            params = params_from_system_metadata(system)
        if params is None:
            return unavailable_control_system(system, control_name, "missing_relation_params")
        return constraint_resampled_generation_control(system, params, seed, strength)
    return unavailable_control_system(system, control_name, "unknown_mechanism_control")


def roughness_resampled_transform_control(system: LandscapeSystem, seed: int, strength: float) -> LandscapeSystem:
    rng = random.Random(seed)
    p = clamp_probability(strength)
    states = tuple(system.states)
    out: dict[State, tuple[State, ...]] = {}
    edge_resample_count = 0
    for source in states:
        targets = list(system.edges.get(source, ()))
        used = set(targets)
        for index, target in enumerate(targets):
            if rng.random() > p:
                continue
            used.discard(target)
            candidates = [state for state in states if state not in used]
            replacement = rng.choice(candidates) if candidates else target
            targets[index] = replacement
            used.add(replacement)
            edge_resample_count += 1
        out[source] = tuple(sorted(targets))
    metadata = mechanism_metadata(system, "roughness_resampled_transform_control", strength)
    metadata.update({
        "roughness_p": p,
        "edge_resample_count": edge_resample_count,
        "out_degree_preserved_flag": int(out_degree_sequence(system.edges, states) == out_degree_sequence(out, states)),
        **edge_delta_metadata(system, out),
    })
    return replace(system, system_id=f"{system.system_id}_roughness_p{p:.3f}_seed{seed}", edges=out, metadata=metadata)


def asymmetry_flip_sweep_control(system: LandscapeSystem, seed: int, strength: float) -> LandscapeSystem:
    rng = random.Random(seed)
    p = clamp_probability(strength)
    states = tuple(system.states)
    out = {state: set(system.edges.get(state, ())) for state in states}
    edge_set = {(source, target) for source, targets in system.edges.items() for target in targets}
    asymmetric = [(source, target) for source, target in edge_set if (target, source) not in edge_set]
    rng.shuffle(asymmetric)
    flip_target = round(len(asymmetric) * p)
    flipped = 0
    for source, target in asymmetric[:flip_target]:
        if target not in out.get(source, set()):
            continue
        out[source].discard(target)
        out.setdefault(target, set()).add(source)
        flipped += 1
    edges = {state: tuple(sorted(out.get(state, set()))) for state in states}
    metadata = mechanism_metadata(system, "asymmetry_flip_sweep_control", strength)
    metadata.update({
        "asymmetry_p": p,
        "flipped_edge_count": flipped,
        **edge_delta_metadata(system, edges),
    })
    return replace(system, system_id=f"{system.system_id}_asymflip_p{p:.3f}_seed{seed}", edges=edges, metadata=metadata)


def constraint_resampled_generation_control(
    system: LandscapeSystem,
    params: RelationParams,
    seed: int,
    strength: float,
) -> LandscapeSystem:
    # This is an honestly named generation-level proxy, not an assignment shuffle
    # of an already materialized system.
    adjusted = replace(params, constraint_density=params.constraint_density, constraint_strength=params.constraint_strength)
    control_seed = seed + round(100_000 * clamp_probability(strength))
    control = generate_relation_system(adjusted, control_seed, null_kind="constraint_shuffled")
    metadata = mechanism_metadata(system, "constraint_resampled_generation_control", strength)
    metadata.update({
        **control.metadata,
        "constraint_control_type": "constraint_resampled_generation_control",
        "constraint_metadata_available": int(bool(system.metadata.get("constraint_json"))),
        "baseline_system_id": system.system_id,
        **edge_delta_metadata(system, control.edges),
    })
    return replace(control, system_id=f"{system.system_id}_constraint_resampled_seed{control_seed}", metadata=metadata)


def substrate_preservation_audit(baseline: LandscapeSystem, control: LandscapeSystem) -> dict[str, int | float | str]:
    baseline_edges = edge_set(baseline.edges)
    control_edges = edge_set(control.edges)
    baseline_out = out_degree_sequence(baseline.edges, baseline.states)
    control_out = out_degree_sequence(control.edges, baseline.states)
    baseline_in = in_degree_sequence(baseline.edges, baseline.states)
    control_in = in_degree_sequence(control.edges, baseline.states)
    state_count_delta = len(control.states) - len(baseline.states)
    edge_count_delta = len(control_edges) - len(baseline_edges)
    mean_out_delta = mean(control_out) - mean(baseline_out) if baseline_out else 0.0
    mean_in_delta = mean(control_in) - mean(baseline_in) if baseline_in else 0.0
    edge_jaccard = jaccard(baseline_edges, control_edges)
    destructiveness = (
        min(1.0, abs(state_count_delta) / max(1, len(baseline.states)))
        + min(1.0, abs(edge_count_delta) / max(1, len(baseline_edges)))
        + (1.0 - edge_jaccard)
    ) / 3.0
    return {
        "baseline_system_id": baseline.system_id,
        "control_system_id": control.system_id,
        "control_name": control.metadata.get("mechanism_control_name", ""),
        "state_count_delta": state_count_delta,
        "edge_count_delta": edge_count_delta,
        "mean_out_degree_delta": mean_out_delta,
        "mean_in_degree_delta": mean_in_delta,
        "reciprocity_delta": reciprocity(control.edges) - reciprocity(baseline.edges),
        "edge_jaccard_vs_baseline": edge_jaccard,
        "control_destructiveness_score": destructiveness,
        "control_too_destructive": int(destructiveness > 0.50),
        "constraint_count_delta_if_available": constraint_count(control) - constraint_count(baseline),
    }


def unavailable_control_system(system: LandscapeSystem, control_name: str, reason: str) -> LandscapeSystem:
    metadata = mechanism_metadata(system, control_name, 0.0)
    metadata.update({
        "mechanism_control_status": "not_available",
        "mechanism_control_unavailable_reason": reason,
    })
    return replace(system, system_id=f"{system.system_id}_{control_name}_not_available", metadata=metadata)


def params_from_system_metadata(system: LandscapeSystem) -> RelationParams | None:
    required = (
        "parameter_set_id",
        "state_coordinate_count",
        "alphabet_size",
        "neighborhood_radius",
        "update_footprint",
        "out_degree_target",
        "constraint_density",
        "constraint_strength",
        "asymmetry_strength",
        "reversibility_fraction",
        "rewire_probability",
    )
    if any(key not in system.metadata for key in required):
        return None
    return RelationParams(
        parameter_set_id=str(system.metadata["parameter_set_id"]),
        coordinate_count=int(system.metadata["state_coordinate_count"]),
        alphabet_size=int(system.metadata["alphabet_size"]),
        neighborhood_radius=int(system.metadata["neighborhood_radius"]),
        update_footprint=int(system.metadata["update_footprint"]),
        out_degree_target=int(system.metadata["out_degree_target"]),
        constraint_density=float(system.metadata["constraint_density"]),
        constraint_strength=float(system.metadata["constraint_strength"]),
        asymmetry_strength=float(system.metadata["asymmetry_strength"]),
        reversibility_fraction=float(system.metadata["reversibility_fraction"]),
        rewire_probability=float(system.metadata["rewire_probability"]),
        roughness_strength=float(system.metadata.get("roughness_strength", 0.01)),
        constraint_arity=int(system.metadata.get("constraint_arity", 2)),
        constraint_change_weight=float(system.metadata.get("constraint_change_weight", 0.35)),
    )


def mechanism_metadata(system: LandscapeSystem, control_name: str, strength: float) -> dict[str, object]:
    return {
        **system.metadata,
        "mechanism_control_name": control_name,
        "mechanism_control_strength": strength,
        "mechanism_control_status": "computed",
        "baseline_system_id": system.system_id,
    }


def edge_delta_metadata(system: LandscapeSystem, edges: dict[State, tuple[State, ...]]) -> dict[str, int | float]:
    baseline_edges = edge_set(system.edges)
    control_edges = edge_set(edges)
    states = tuple(system.states)
    baseline_out = out_degree_sequence(system.edges, states)
    control_out = out_degree_sequence(edges, states)
    baseline_in = in_degree_sequence(system.edges, states)
    control_in = in_degree_sequence(edges, states)
    return {
        "edge_count_delta": len(control_edges) - len(baseline_edges),
        "mean_out_degree_delta": mean(control_out) - mean(baseline_out) if baseline_out else 0.0,
        "mean_in_degree_delta": mean(control_in) - mean(baseline_in) if baseline_in else 0.0,
        "reciprocity_delta": reciprocity(edges) - reciprocity(system.edges),
        "edge_jaccard_vs_baseline": jaccard(baseline_edges, control_edges),
    }


def edge_set(edges: dict[State, tuple[State, ...]]) -> set[tuple[State, State]]:
    return {(source, target) for source, targets in edges.items() for target in targets}


def out_degree_sequence(edges: dict[State, tuple[State, ...]], states: tuple[State, ...]) -> list[int]:
    return [len(edges.get(state, ())) for state in states]


def in_degree_sequence(edges: dict[State, tuple[State, ...]], states: tuple[State, ...]) -> list[int]:
    counts = {state: 0 for state in states}
    for targets in edges.values():
        for target in targets:
            counts[target] = counts.get(target, 0) + 1
    return [counts.get(state, 0) for state in states]


def reciprocity(edges: dict[State, tuple[State, ...]]) -> float:
    edgeset = edge_set(edges)
    if not edgeset:
        return 0.0
    return sum(int((target, source) in edgeset) for source, target in edgeset) / len(edgeset)


def constraint_count(system: LandscapeSystem) -> int:
    raw = system.metadata.get("constraint_json", "[]")
    try:
        return len(json.loads(str(raw)))
    except json.JSONDecodeError:
        return 0


def jaccard(left: set[object], right: set[object]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / max(1, len(left | right))


def clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
