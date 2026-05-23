from __future__ import annotations

import itertools
import json
import random
from dataclasses import asdict, dataclass
from math import log2

from .substrate import LandscapeSystem, State


@dataclass(frozen=True)
class RelationParams:
    parameter_set_id: str
    coordinate_count: int
    alphabet_size: int
    neighborhood_radius: int
    update_footprint: int
    out_degree_target: int
    constraint_density: float
    constraint_strength: float
    asymmetry_strength: float
    reversibility_fraction: float
    rewire_probability: float
    roughness_strength: float = 0.01
    constraint_arity: int = 2
    constraint_change_weight: float = 0.35


def sample_parameter_sets(count: int, seed: int) -> list[RelationParams]:
    rng = random.Random(seed)
    grid = list(
        itertools.product(
            (5, 6),
            (3,),
            (1,),
            (1, 2),
            (2, 3, 4),
            (0.10, 0.25, 0.40),
            (0.5, 1.0, 2.0),
            (0.0, 0.25, 0.5),
            (0.0, 0.25, 0.5),
            (0.0, 0.05),
        )
    )
    rng.shuffle(grid)
    out = []
    for index, values in enumerate(grid[:count]):
        n, alphabet, radius, footprint, degree, density, strength, asymmetry, reversibility, rewire = values
        parameter_set_id = (
            f"relgen_n{n}_a{alphabet}_r{radius}_m{footprint}_"
            f"k{degree}_cd{density:.2f}_cs{strength:.2f}_"
            f"as{asymmetry:.2f}_rev{reversibility:.2f}_rw{rewire:.2f}"
        )
        out.append(
            RelationParams(
                parameter_set_id=parameter_set_id,
                coordinate_count=int(n),
                alphabet_size=int(alphabet),
                neighborhood_radius=int(radius),
                update_footprint=int(footprint),
                out_degree_target=int(degree),
                constraint_density=float(density),
                constraint_strength=float(strength),
                asymmetry_strength=float(asymmetry),
                reversibility_fraction=float(reversibility),
                rewire_probability=float(rewire),
                constraint_arity=2 if index % 3 else 3,
            )
        )
    return out


def generate_relation_system(params: RelationParams, seed: int, null_kind: str = "base") -> LandscapeSystem:
    states = _enumerate_states(params.coordinate_count, params.alphabet_size)
    constraints = _generate_constraints(params, seed, null_kind)
    bias_weights = _bias_weights(params, seed, null_kind)
    rough_seed = seed + (17_171 if null_kind == "roughness_resampled" else 0)
    candidates_by_state = {
        state: _candidate_successors(state, params.alphabet_size, params.update_footprint)
        for state in states
    }
    edges = _build_edges(states, candidates_by_state, constraints, bias_weights, params, rough_seed)
    if null_kind == "degree_preserving_rewire":
        edges = _degree_preserving_rewire(states, edges, seed + 81_001)
    elif null_kind == "out_degree_preserving_random":
        edges = _out_degree_random(states, edges, seed + 91_003)
    else:
        edges = _apply_reversibility(states, edges, params.reversibility_fraction, seed + 11_003)
        edges = _apply_rewire(states, edges, candidates_by_state, params.rewire_probability, seed + 19_007)
    environment_id = f"{params.parameter_set_id}_seed{seed}" if null_kind == "base" else f"{params.parameter_set_id}_{null_kind}_seed{seed}"
    metadata = {
        **asdict(params),
        "state_coordinate_count": params.coordinate_count,
        "alphabet_size": params.alphabet_size,
        "state_count": len(states),
        "presentation": "action_generated_relation",
        "generator_kind": null_kind,
        "constraint_json": json.dumps(constraints, sort_keys=True),
        "constraint_hash": _stable_hash(json.dumps(constraints, sort_keys=True)),
    }
    return LandscapeSystem(
        system_id=environment_id,
        seed=seed,
        family=environment_id,
        states=states,
        edges=edges,
        transform_names=("top_k_relation_score",),
        metadata=metadata,
    )


def generated_null_systems(params: RelationParams, seed: int) -> dict[str, LandscapeSystem]:
    return {
        "degree_preserving_rewire": generate_relation_system(params, seed, "degree_preserving_rewire"),
        "out_degree_preserving_random": generate_relation_system(params, seed, "out_degree_preserving_random"),
        "constraint_shuffled": generate_relation_system(params, seed, "constraint_shuffled"),
        "asymmetry_shuffled": generate_relation_system(params, seed, "asymmetry_shuffled"),
        "roughness_resampled": generate_relation_system(params, seed, "roughness_resampled"),
    }


def environment_shape(system: LandscapeSystem, horizons: tuple[int, ...]) -> dict[str, object]:
    from .landscape import exact_frontier, reachable

    out_degrees = [len(targets) for targets in system.edges.values()]
    in_counts = {state: 0 for state in system.states}
    reciprocal = 0
    edge_count = 0
    edge_set = {(source, target) for source, targets in system.edges.items() for target in targets}
    for source, targets in system.edges.items():
        for target in targets:
            edge_count += 1
            in_counts[target] = in_counts.get(target, 0) + 1
            reciprocal += int((target, source) in edge_set)
    starts = _diagnostic_starts(system)
    reach_by_h = {
        h: sum(len(reachable(system, start, h)) for start in starts) / max(1, len(starts))
        for h in horizons
    }
    exact_by_h = {
        h: sum(len(exact_frontier(system, start, h)) for start in starts) / max(1, len(starts))
        for h in horizons
    }
    saturation_onset = next((h for h in horizons if reach_by_h[h] / len(system.states) >= 0.95), "")
    nonsat = [h for h in horizons if reach_by_h[h] / len(system.states) < 0.95]
    frontier_repeat = _frontier_repeat_onset(system, starts[0], horizons)
    scc_count, largest_scc = _scc_summary(system)
    collapse = int(max(exact_by_h.values()) <= 2)
    cycle = int(frontier_repeat != "" and exact_by_h.get(max(horizons), 0) <= 8)
    path_concentration = max((exact_by_h[h] / max(1.0, reach_by_h[h]) for h in horizons), default=0.0)
    bottleneck = 1.0 / max(1.0, min((exact_by_h[h] for h in horizons if h > 0), default=1.0))
    row = {
        "environment_id": system.system_id,
        "parameter_set_id": system.metadata["parameter_set_id"],
        "state_count": len(system.states),
        "edge_count": edge_count,
        "mean_out_degree": sum(out_degrees) / max(1, len(out_degrees)),
        "out_degree_entropy": _entropy(out_degrees),
        "in_degree_entropy": _entropy(list(in_counts.values())),
        "edge_reciprocity_fraction": reciprocal / max(1, edge_count),
        "strongly_connected_component_count": scc_count,
        "largest_scc_fraction": largest_scc / max(1, len(system.states)),
        "reach_saturation_onset_H": saturation_onset,
        "frontier_repeat_onset_H": frontier_repeat,
        "fast_saturation_flag": int(isinstance(saturation_onset, int) and saturation_onset <= 16),
        "nonsaturation_window_length": len(nonsat),
        "collapse_flag": collapse,
        "cycle_onset_proxy": cycle,
        "path_concentration_proxy": path_concentration,
        "bottleneck_proxy": bottleneck,
    }
    for h in horizons:
        row[f"reach_saturation_fraction_H{h}"] = reach_by_h[h] / len(system.states)
        row[f"exact_frontier_size_H{h}"] = exact_by_h[h]
    row["environment_shape_class"] = _environment_shape_class(row)
    return row


def _enumerate_states(coordinate_count: int, alphabet_size: int) -> tuple[State, ...]:
    return tuple(itertools.product(range(alphabet_size), repeat=coordinate_count))


def _generate_constraints(params: RelationParams, seed: int, null_kind: str) -> list[dict[str, object]]:
    rng = random.Random(seed + 37_777)
    count = max(1, round(params.coordinate_count * params.constraint_density * 3))
    constraints = []
    for index in range(count):
        center = rng.randrange(params.coordinate_count)
        neighborhood = [(center + offset) % params.coordinate_count for offset in range(-params.neighborhood_radius, params.neighborhood_radius + 1)]
        if len(neighborhood) < params.constraint_arity:
            neighborhood = list(range(params.coordinate_count))
        coords = sorted(rng.sample(neighborhood, params.constraint_arity))
        if null_kind == "constraint_shuffled":
            coords = sorted(rng.sample(range(params.coordinate_count), params.constraint_arity))
        kind = rng.choice(("local_modular_sum_preference", "local_equality_relation", "local_difference_relation"))
        residue = rng.randrange(params.alphabet_size)
        if null_kind == "constraint_shuffled":
            residue = rng.randrange(params.alphabet_size)
        constraints.append(
            {
                "constraint_type": kind,
                "coordinates": coords,
                "modulus": params.alphabet_size,
                "preferred_residue": residue,
                "weight": params.constraint_strength,
                "index": index,
            }
        )
    return constraints


def _bias_weights(params: RelationParams, seed: int, null_kind: str) -> tuple[float, ...]:
    rng = random.Random(seed + (63_001 if null_kind == "asymmetry_shuffled" else 61_001))
    return tuple(rng.uniform(-1.0, 1.0) for _ in range(params.coordinate_count))


def _candidate_successors(state: State, alphabet_size: int, footprint: int) -> tuple[State, ...]:
    out: set[State] = set()
    coords = range(len(state))
    for size in range(1, footprint + 1):
        for selected in itertools.combinations(coords, size):
            choices = [[value for value in range(alphabet_size) if value != state[coord]] for coord in selected]
            for replacements in itertools.product(*choices):
                values = list(state)
                for coord, value in zip(selected, replacements):
                    values[coord] = value
                out.add(tuple(values))
    return tuple(sorted(out))


def _build_edges(
    states: tuple[State, ...],
    candidates_by_state: dict[State, tuple[State, ...]],
    constraints: list[dict[str, object]],
    bias_weights: tuple[float, ...],
    params: RelationParams,
    rough_seed: int,
) -> dict[State, tuple[State, ...]]:
    edges = {}
    for state in states:
        scored = [
            (_relation_score(state, target, constraints, bias_weights, params, rough_seed), target)
            for target in candidates_by_state[state]
        ]
        scored.sort(key=lambda item: (item[0], item[1]))
        edges[state] = tuple(target for _score, target in scored[: params.out_degree_target])
    return edges


def _relation_score(
    source: State,
    target: State,
    constraints: list[dict[str, object]],
    bias_weights: tuple[float, ...],
    params: RelationParams,
    rough_seed: int,
) -> float:
    change = sum(int(left != right) for left, right in zip(source, target))
    violation = _constraint_violation(target, constraints)
    source_profile = _constraint_profile(source, constraints)
    target_profile = _constraint_profile(target, constraints)
    profile_change = sum(abs(left - right) for left, right in zip(source_profile, target_profile))
    asymmetry = _bias(target, bias_weights) - _bias(source, bias_weights)
    roughness = (_stable_hash(f"{rough_seed}:{source}:{target}") % 10_000) / 10_000.0
    return (
        change
        + violation
        + params.constraint_change_weight * profile_change
        + params.asymmetry_strength * asymmetry
        + params.roughness_strength * roughness
    )


def _constraint_profile(state: State, constraints: list[dict[str, object]]) -> tuple[int, ...]:
    return tuple(int(_constraint_violation_one(state, constraint) > 0) for constraint in constraints)


def _constraint_violation(state: State, constraints: list[dict[str, object]]) -> float:
    return sum(float(constraint["weight"]) * _constraint_violation_one(state, constraint) for constraint in constraints)


def _constraint_violation_one(state: State, constraint: dict[str, object]) -> int:
    coords = list(constraint["coordinates"])  # type: ignore[arg-type]
    values = [state[int(coord)] for coord in coords]
    modulus = int(constraint["modulus"])
    residue = int(constraint["preferred_residue"])
    kind = str(constraint["constraint_type"])
    if kind == "local_modular_sum_preference":
        return int(sum(values) % modulus != residue)
    if kind == "local_equality_relation":
        return int((len(set(values)) == 1) != bool(residue % 2))
    if kind == "local_difference_relation":
        return int((values[0] - values[-1]) % modulus != residue)
    return 0


def _bias(state: State, weights: tuple[float, ...]) -> float:
    return sum(value * weight for value, weight in zip(state, weights)) / max(1, len(state))


def _apply_reversibility(states: tuple[State, ...], edges: dict[State, tuple[State, ...]], fraction: float, seed: int) -> dict[State, tuple[State, ...]]:
    if fraction <= 0:
        return edges
    out = {state: set(targets) for state, targets in edges.items()}
    for source, targets in edges.items():
        for target in targets:
            if (_stable_hash(f"{seed}:{source}:{target}") % 10_000) / 10_000.0 <= fraction:
                out.setdefault(target, set()).add(source)
    return {state: tuple(sorted(out.get(state, set()))) for state in states}


def _apply_rewire(
    states: tuple[State, ...],
    edges: dict[State, tuple[State, ...]],
    candidates_by_state: dict[State, tuple[State, ...]],
    probability: float,
    seed: int,
) -> dict[State, tuple[State, ...]]:
    if probability <= 0:
        return edges
    rng = random.Random(seed)
    out = {}
    for source in states:
        targets = list(edges[source])
        candidates = list(candidates_by_state[source])
        for index, target in enumerate(targets):
            if candidates and rng.random() <= probability:
                targets[index] = rng.choice(candidates)
            else:
                targets[index] = target
        out[source] = tuple(sorted(set(targets)))
    return out


def _degree_preserving_rewire(states: tuple[State, ...], edges: dict[State, tuple[State, ...]], seed: int) -> dict[State, tuple[State, ...]]:
    rng = random.Random(seed)
    state_list = list(states)
    return {
        state: tuple(sorted(rng.sample(state_list, min(len(targets), len(state_list)))))
        for state, targets in edges.items()
    }


def _out_degree_random(states: tuple[State, ...], edges: dict[State, tuple[State, ...]], seed: int) -> dict[State, tuple[State, ...]]:
    rng = random.Random(seed)
    state_list = list(states)
    return {
        state: tuple(sorted(rng.choice(state_list) for _ in range(len(targets))))
        for state, targets in edges.items()
    }


def _diagnostic_starts(system: LandscapeSystem) -> tuple[State, ...]:
    if len(system.states) <= 4:
        return system.states
    return tuple(system.states[(system.seed + i * 31) % len(system.states)] for i in range(4))


def _frontier_repeat_onset(system: LandscapeSystem, start: State, horizons: tuple[int, ...]) -> int | str:
    from .landscape import exact_frontier

    seen: dict[frozenset[State], int] = {}
    for h in horizons:
        frontier = exact_frontier(system, start, h)
        if frontier in seen:
            return h
        seen[frontier] = h
    return ""


def _scc_summary(system: LandscapeSystem) -> tuple[int, int]:
    index = 0
    stack: list[State] = []
    indices: dict[State, int] = {}
    lowlinks: dict[State, int] = {}
    on_stack: set[State] = set()
    sizes: list[int] = []

    def strongconnect(state: State) -> None:
        nonlocal index
        indices[state] = index
        lowlinks[state] = index
        index += 1
        stack.append(state)
        on_stack.add(state)
        for target in system.edges[state]:
            if target not in indices:
                strongconnect(target)
                lowlinks[state] = min(lowlinks[state], lowlinks[target])
            elif target in on_stack:
                lowlinks[state] = min(lowlinks[state], indices[target])
        if lowlinks[state] == indices[state]:
            size = 0
            while True:
                item = stack.pop()
                on_stack.remove(item)
                size += 1
                if item == state:
                    break
            sizes.append(size)

    for state in system.states:
        if state not in indices:
            strongconnect(state)
    return len(sizes), max(sizes, default=0)


def _environment_shape_class(row: dict[str, object]) -> str:
    if int(row["collapse_flag"]):
        return "fast_collapse_environment"
    if int(row["cycle_onset_proxy"]) and float(row["largest_scc_fraction"]) < 0.25:
        return "cycle_dominated_environment"
    if int(row["fast_saturation_flag"]):
        return "fast_saturation_environment"
    if float(row["largest_scc_fraction"]) < 0.05:
        return "underconnected_environment"
    if float(row["largest_scc_fraction"]) > 0.90 and float(row["edge_reciprocity_fraction"]) < 0.05:
        return "random_mixing_environment"
    if int(row["nonsaturation_window_length"]) >= 6 and 0.05 <= float(row["largest_scc_fraction"]) <= 0.90:
        return "middle_regime_environment"
    return "underdetermined_environment"


def _entropy(values: list[int]) -> float:
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return -sum((count / total) * log2(count / total) for count in counts.values() if count)


def _stable_hash(text: str) -> int:
    total = 0
    for index, char in enumerate(text):
        total = (total * 131 + (index + 17) * ord(char)) % 2_147_483_647
    return total
