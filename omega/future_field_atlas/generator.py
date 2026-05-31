from __future__ import annotations

import json
from dataclasses import replace

from omega.rfs_mb0_future_landscape.relation_generator import RelationParams
from omega.rfs_mb0_future_landscape.substrate import State
from omega.rfs_mb0_future_landscape.transition_energy_substrates import (
    PRESERVATION_ASYMMETRY,
    TOP_M_DROP_STRONGEST_FROM_TOP_M,
    TOP_M_DROP_TWO_WEAKEST_FROM_TOP_M,
    TOP_M_DROP_WEAKEST_FROM_TOP_M,
    TOP_M_RANDOM_DELETE_ONE_FROM_TOP_M,
    TOP_M_RANDOM_DELETE_TWO_FROM_TOP_M,
    budget_field,
    candidate_successors,
    deterministic_preservation_job,
    enumerate_states,
    generate_job_baseline_system,
    preservation_scored_candidates,
)

from .contracts import (
    ConditionSpec,
    EdgeAnatomy,
    GeneratedCondition,
    ObservableSpec,
    SelectionOperatorSpec,
    StateSpaceSpec,
    TransformationLawSpec,
)
from .util import safe_token


DEFAULT_SELECTION_OPERATORS = (
    "rank_prefix:m=3",
    "rank_prefix:m=4",
    "rank_prefix:m=5",
    "rank_subset:m=4:retain=1|2|3:remove=4",
    "rank_subset:m=5:retain=1|2|3:remove=4|5",
    "stochastic_rank_subset:m=4:effective=3",
    "stochastic_rank_subset:m=5:effective=3",
    "rank_subset:m=4:retain=2|3|4:remove=1",
)


def build_generated_conditions(
    *,
    groups: int,
    fresh_seeds_per_group: int,
    selection_operators: tuple[str, ...],
    macro_invariant_kind: str,
    macro_invariant_betas: tuple[float, ...],
    rank_boundary_k: int,
    base_seed: int,
) -> list[GeneratedCondition]:
    out: list[GeneratedCondition] = []
    operator_texts = selection_operators or DEFAULT_SELECTION_OPERATORS
    for group_index in range(max(1, groups)):
        for fresh_index in range(max(1, fresh_seeds_per_group)):
            seed = base_seed + group_index * 10_000 + fresh_index * 101
            for beta in macro_invariant_betas:
                for operator_text in operator_texts:
                    operator = parse_selection_operator(operator_text)
                    params = relation_params(group_index, operator.base_out_degree)
                    condition_id = (
                        f"g{group_index:02d}_s{fresh_index:02d}_"
                        f"beta{safe_token(f'{beta:g}')}_{safe_token(operator.selection_operator_id)}"
                    )
                    job = {
                        "job_id": condition_id,
                        "condition_id": condition_id,
                        "substrate_family": operator.implementation_family,
                        "transition_energy_family": operator.implementation_family,
                        "substrate_variant": operator.selection_operator_id,
                        "macro_invariant_kind": macro_invariant_kind,
                        "budget_kind": macro_invariant_kind,
                        "macro_invariant_beta": beta,
                        "budget_weight": beta,
                        "apply_reversibility": False,
                        "sampler_postprocess_policy": "future_field_atlas_no_reversibility",
                    }
                    system = generate_job_baseline_system(job, params, seed)
                    spec = ConditionSpec(
                        condition_id=condition_id,
                        group_id=f"group_{group_index:02d}",
                        seed=seed,
                        substrate_id=system.system_id,
                        state_space=StateSpaceSpec(
                            state_space_id=f"Z{params.alphabet_size}^{params.coordinate_count}",
                            coordinate_set_id=f"coordinate_index_set__n{params.coordinate_count}",
                            coordinate_count=params.coordinate_count,
                            symbol_domain_id=f"integer_symbols_0_to_{params.alphabet_size - 1}",
                            alphabet_size=params.alphabet_size,
                            state_count=len(system.states),
                            state_id_schema="tuple_coordinate_payload",
                            metric_id="hamming_distance",
                            adjacency_rule_id=(
                                f"hamming_ball_without_self__radius_{params.neighborhood_radius}"
                                f"__footprint_{params.update_footprint}"
                            ),
                        ),
                        transformation_law=TransformationLawSpec(
                            law_id=f"{operator.implementation_family}__{macro_invariant_kind}__beta_{beta:g}",
                            law_family=operator.implementation_family,
                            candidate_successor_rule_id=(
                                f"hamming_ball_without_self__alphabet_{params.alphabet_size}"
                                f"__footprint_{params.update_footprint}"
                            ),
                            candidate_successor_params_json=json.dumps(
                                {
                                    "alphabet_size": params.alphabet_size,
                                    "update_footprint": params.update_footprint,
                                    "neighborhood_radius": params.neighborhood_radius,
                                },
                                sort_keys=True,
                            ),
                            energy_function_id="hamming_plus_macro_invariant_delta_plus_seeded_roughness",
                            energy_params_json=json.dumps(
                                {
                                    "macro_invariant_kind": macro_invariant_kind,
                                    "macro_invariant_beta": beta,
                                    "roughness_strength": params.roughness_strength,
                                },
                                sort_keys=True,
                            ),
                            admissibility_predicate_id="candidate_successor_in_local_hamming_ball",
                            stochastic_flag=operator.stochastic_flag,
                            law_params_json=json.dumps(
                                {
                                    "macro_invariant_kind": macro_invariant_kind,
                                    "macro_invariant_beta": beta,
                                    "roughness_strength": params.roughness_strength,
                                    "apply_reversibility": False,
                                },
                                sort_keys=True,
                            ),
                            macro_invariant_kind=macro_invariant_kind,
                            macro_invariant_beta=beta,
                        ),
                        selection_operator=operator,
                        observable=ObservableSpec(
                            observable_set_id=f"rank_boundary_k{rank_boundary_k}__{macro_invariant_kind}",
                            observable_family="rank_boundary_and_frontier_topology",
                            rank_boundary_k=rank_boundary_k,
                            feature_map_ids=(
                                "frontier_topology_by_horizon",
                                "rank_boundary_geometry_by_horizon",
                                "transport_composition_residuals",
                                "selection_operator_geometry_summary",
                            ),
                            observable_params_json=json.dumps(
                                {"rank_boundary_k": rank_boundary_k, "macro_invariant_kind": macro_invariant_kind},
                                sort_keys=True,
                            ),
                        ),
                    )
                    candidate_anatomy, selected, reference = edge_anatomy_for_condition(
                        system_edges=system.edges,
                        params=params,
                        seed=seed,
                        job=job,
                        rank_boundary_k=rank_boundary_k,
                        reference_operator=operator.operator_family == "rank_prefix",
                    )
                    out.append(
                        GeneratedCondition(
                            spec=spec,
                            system=system,
                            candidate_anatomy=candidate_anatomy,
                            selected_edge_keys=frozenset(selected),
                            reference_edge_keys=frozenset(reference),
                        )
                    )
    return out


def relation_params(group_index: int, out_degree_target: int) -> RelationParams:
    density_values = (0.10, 0.25, 0.40)
    strength_values = (0.5, 1.0, 2.0)
    asymmetry_values = (0.0, 0.25, 0.5)
    density = density_values[group_index % len(density_values)]
    strength = strength_values[(group_index // len(density_values)) % len(strength_values)]
    asymmetry = asymmetry_values[(group_index // (len(density_values) * len(strength_values))) % len(asymmetry_values)]
    base = RelationParams(
        parameter_set_id=(
            f"ffa_relgen_g{group_index:02d}_n5_a3_u1_k{out_degree_target}_"
            f"cd{density:.2f}_cs{strength:.2f}_as{asymmetry:.2f}"
        ),
        coordinate_count=5,
        alphabet_size=3,
        neighborhood_radius=1,
        update_footprint=1,
        out_degree_target=out_degree_target,
        constraint_density=density,
        constraint_strength=strength,
        asymmetry_strength=asymmetry,
        reversibility_fraction=0.0,
        rewire_probability=0.0,
        roughness_strength=0.01,
        constraint_arity=2,
    )
    return replace(base, out_degree_target=out_degree_target)


def parse_selection_operator(raw: str) -> SelectionOperatorSpec:
    operator_family, options = parse_operator_text(raw)
    if operator_family == "rank_prefix":
        base_out_degree = required_int(options, "m", raw)
        return rank_prefix_operator(base_out_degree, PRESERVATION_ASYMMETRY)
    if operator_family == "rank_subset":
        base_out_degree = required_int(options, "m", raw)
        retained = parse_rank_set(required_text(options, "retain", raw))
        removed = parse_rank_set(options.get("remove", ""))
        if not removed:
            removed = tuple(rank for rank in range(1, base_out_degree + 1) if rank not in set(retained))
        implementation_family = rank_subset_implementation_family(base_out_degree, retained, removed, raw)
        return rank_subset_operator(base_out_degree, retained, removed, implementation_family)
    if operator_family == "stochastic_rank_subset":
        base_out_degree = required_int(options, "m", raw)
        effective_out_degree = required_int(options, "effective", raw)
        implementation_family = stochastic_rank_subset_implementation_family(base_out_degree, effective_out_degree, raw)
        return stochastic_rank_subset_operator(base_out_degree, effective_out_degree, implementation_family)
    raise ValueError(
        f"unknown selection operator family in {raw!r}; expected rank_prefix, "
        "rank_subset, or stochastic_rank_subset"
    )


def parse_operator_text(raw: str) -> tuple[str, dict[str, str]]:
    text = str(raw or "").strip()
    if not text:
        raise ValueError("empty selection operator")
    if ":" not in text and "_" in text:
        raise ValueError(
            f"legacy selection operator token {text!r} is not accepted by the clean atlas runtime; "
            "use operator syntax such as rank_prefix:m=3 or "
            "rank_subset:m=4:retain=1|2|3:remove=4"
        )
    parts = text.split(":")
    family = parts[0].strip()
    options: dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            raise ValueError(f"selection operator option {part!r} in {text!r} is missing '='")
        key, value = part.split("=", 1)
        options[key.strip()] = value.strip()
    return family, options


def required_text(options: dict[str, str], key: str, raw: str) -> str:
    value = options.get(key, "").strip()
    if not value:
        raise ValueError(f"selection operator {raw!r} is missing required option {key!r}")
    return value


def required_int(options: dict[str, str], key: str, raw: str) -> int:
    return int(required_text(options, key, raw))


def parse_rank_set(raw: str) -> tuple[int, ...]:
    text = str(raw or "").strip()
    if not text:
        return tuple()
    for delimiter in ("|", ";", "_"):
        text = text.replace(delimiter, ",")
    ranks = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    if len(set(ranks)) != len(ranks):
        raise ValueError(f"rank set contains duplicates: {raw!r}")
    return tuple(sorted(ranks))


def rank_subset_implementation_family(
    base_out_degree: int,
    retained_rank_set: tuple[int, ...],
    removed_rank_set: tuple[int, ...],
    raw: str,
) -> str:
    if base_out_degree == 4 and retained_rank_set == (1, 2, 3) and removed_rank_set == (4,):
        return TOP_M_DROP_WEAKEST_FROM_TOP_M
    if base_out_degree == 5 and retained_rank_set == (1, 2, 3) and removed_rank_set == (4, 5):
        return TOP_M_DROP_TWO_WEAKEST_FROM_TOP_M
    if base_out_degree == 4 and retained_rank_set == (2, 3, 4) and removed_rank_set == (1,):
        return TOP_M_DROP_STRONGEST_FROM_TOP_M
    raise ValueError(
        f"selection operator {raw!r} has no calibration generator implementation. "
        "The clean atlas runtime only accepts mathematically named operators, but "
        "the current Phase 0/1 generator still supports a narrow audited calibration subset."
    )


def stochastic_rank_subset_implementation_family(
    base_out_degree: int,
    effective_out_degree: int,
    raw: str,
) -> str:
    if base_out_degree == 4 and effective_out_degree == 3:
        return TOP_M_RANDOM_DELETE_ONE_FROM_TOP_M
    if base_out_degree == 5 and effective_out_degree == 3:
        return TOP_M_RANDOM_DELETE_TWO_FROM_TOP_M
    raise ValueError(
        f"selection operator {raw!r} has no calibration generator implementation. "
        "Supported stochastic calibration operators are m=4,effective=3 and m=5,effective=3."
    )


def rank_prefix_operator(base_out_degree: int, family: str) -> SelectionOperatorSpec:
    retained = tuple(range(1, base_out_degree + 1))
    return selection_operator(
        operator_family="rank_prefix",
        base_out_degree=base_out_degree,
        effective_out_degree=base_out_degree,
        retained_rank_set=retained,
        removed_rank_set=tuple(),
        stochastic_flag=0,
        seed_policy="deterministic_rank_order",
        implementation_family=family,
    )


def rank_subset_operator(
    base_out_degree: int,
    retained_rank_set: tuple[int, ...],
    removed_rank_set: tuple[int, ...],
    family: str,
) -> SelectionOperatorSpec:
    return selection_operator(
        operator_family="rank_subset",
        base_out_degree=base_out_degree,
        effective_out_degree=len(retained_rank_set),
        retained_rank_set=retained_rank_set,
        removed_rank_set=removed_rank_set,
        stochastic_flag=0,
        seed_policy="deterministic_rank_order",
        implementation_family=family,
    )


def stochastic_rank_subset_operator(
    base_out_degree: int,
    effective_out_degree: int,
    family: str,
) -> SelectionOperatorSpec:
    return selection_operator(
        operator_family="stochastic_rank_subset",
        base_out_degree=base_out_degree,
        effective_out_degree=effective_out_degree,
        retained_rank_set=tuple(),
        removed_rank_set=tuple(),
        stochastic_flag=1,
        seed_policy="stable_ranked_sample_from_top_m",
        implementation_family=family,
    )


def selection_operator(
    *,
    operator_family: str,
    base_out_degree: int,
    effective_out_degree: int,
    retained_rank_set: tuple[int, ...],
    removed_rank_set: tuple[int, ...],
    stochastic_flag: int,
    seed_policy: str,
    implementation_family: str,
) -> SelectionOperatorSpec:
    params = {
        "operator_family": operator_family,
        "base_out_degree": base_out_degree,
        "effective_out_degree": effective_out_degree,
        "retained_rank_set": list(retained_rank_set),
        "removed_rank_set": list(removed_rank_set),
        "stochastic_flag": stochastic_flag,
        "seed_policy": seed_policy,
        "implementation_family": implementation_family,
    }
    retained_token = "sampled" if stochastic_flag else "_".join(str(rank) for rank in retained_rank_set)
    removed_token = "sampled" if stochastic_flag else ("none" if not removed_rank_set else "_".join(str(rank) for rank in removed_rank_set))
    return SelectionOperatorSpec(
        selection_operator_id=(
            f"{operator_family}__m{base_out_degree}_to_{effective_out_degree}"
            f"__retain_{retained_token}__remove_{removed_token}"
        ),
        operator_family=operator_family,
        operator_params_json=json.dumps(params, sort_keys=True),
        base_out_degree=base_out_degree,
        effective_out_degree=effective_out_degree,
        retained_rank_set=retained_rank_set,
        removed_rank_set=removed_rank_set,
        stochastic_flag=stochastic_flag,
        seed_policy=seed_policy,
        implementation_family=implementation_family,
    )


def edge_anatomy_for_condition(
    *,
    system_edges: dict[State, tuple[State, ...]],
    params: RelationParams,
    seed: int,
    job: dict[str, object],
    rank_boundary_k: int,
    reference_operator: bool,
) -> tuple[dict[tuple[State, State], EdgeAnatomy], set[tuple[State, State]], set[tuple[State, State]]]:
    states = enumerate_states(params.coordinate_count, params.alphabet_size)
    candidates_by_state = {
        state: candidate_successors(state, params.alphabet_size, params.update_footprint)
        for state in states
    }
    budget = budget_field(states, params, job)
    beta = float(job.get("macro_invariant_beta", job.get("budget_weight", 1.0)))
    calibration_job = deterministic_preservation_job(job, beta)
    scored_by_source = preservation_scored_candidates(
        states,
        candidates_by_state,
        params,
        seed,
        float(params.roughness_strength),
        budget,
        calibration_job,
    )
    reference_edge_keys: set[tuple[State, State]] = set()
    selected_edge_keys = {
        (source, target)
        for source, targets in system_edges.items()
        for target in targets
    }
    anatomy: dict[tuple[State, State], EdgeAnatomy] = {}
    for source, scored in scored_by_source.items():
        reference_targets = {target for _energy, target in scored[: max(1, params.out_degree_target)]}
        reference_edge_keys.update((source, target) for target in reference_targets)
        for rank_index, (energy, target) in enumerate(scored, start=1):
            selected = int((source, target) in selected_edge_keys)
            reference_selected = int(target in reference_targets)
            anatomy[(source, target)] = EdgeAnatomy(
                source_state=source,
                target_state=target,
                candidate_rank=rank_index,
                candidate_energy=float(energy),
                selected_flag=selected,
                reference_selected_flag=reference_selected,
                rank_offset_from_boundary=rank_index - rank_boundary_k,
                perturbation_changed_flag=int(not reference_operator and selected != reference_selected),
            )
    return anatomy, selected_edge_keys, reference_edge_keys


def select_start_states(condition: GeneratedCondition, start_samples: int) -> tuple[State, ...]:
    states = condition.system.states
    count = max(1, min(start_samples, len(states)))
    offset = condition.spec.seed % len(states)
    return tuple(states[(offset + index * 17) % len(states)] for index in range(count))
