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


DEFAULT_BOUNDARY_CONTROLS = (
    "baseline_m3",
    "baseline_m4",
    "baseline_m5",
    "drop_weakest_m4_to_core3",
    "drop_two_weakest_m5_to_core3",
    "random_delete_one_m4_to_core3",
    "random_delete_two_m5_to_core3",
    "drop_strongest_m4_to_m3",
)


def build_generated_conditions(
    *,
    groups: int,
    fresh_seeds_per_group: int,
    boundary_controls: tuple[str, ...],
    macro_invariant_kind: str,
    macro_invariant_betas: tuple[float, ...],
    core_rank_k: int,
    base_seed: int,
) -> list[GeneratedCondition]:
    out: list[GeneratedCondition] = []
    controls = boundary_controls or DEFAULT_BOUNDARY_CONTROLS
    for group_index in range(max(1, groups)):
        for fresh_index in range(max(1, fresh_seeds_per_group)):
            seed = base_seed + group_index * 10_000 + fresh_index * 101
            for beta in macro_invariant_betas:
                for control in controls:
                    operator, role = selection_operator_from_alias(control, core_rank_k)
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
                            coordinate_count=params.coordinate_count,
                            alphabet_size=params.alphabet_size,
                            state_count=len(system.states),
                        ),
                        transformation_law=TransformationLawSpec(
                            law_id=f"{operator.implementation_family}__{macro_invariant_kind}__beta_{beta:g}",
                            law_family=operator.implementation_family,
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
                            observable_set_id=f"rank_core_k{core_rank_k}__{macro_invariant_kind}",
                            observable_family="rank_core_fringe_and_frontier_topology",
                            observable_params_json=json.dumps(
                                {"core_rank_k": core_rank_k, "macro_invariant_kind": macro_invariant_kind},
                                sort_keys=True,
                            ),
                        ),
                        human_label=control,
                        legacy_boundary_control_alias=control,
                        legacy_role_alias=role,
                    )
                    candidate_anatomy, selected, baseline = edge_anatomy_for_condition(
                        system_edges=system.edges,
                        params=params,
                        seed=seed,
                        job=job,
                        core_rank_k=core_rank_k,
                        condition_role=role,
                    )
                    out.append(
                        GeneratedCondition(
                            spec=spec,
                            system=system,
                            candidate_anatomy=candidate_anatomy,
                            selected_edge_keys=frozenset(selected),
                            baseline_edge_keys=frozenset(baseline),
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


def selection_operator_from_alias(control: str, core_rank_k: int) -> tuple[SelectionOperatorSpec, str]:
    if control in {"baseline_m3", "rank_prefix_m3"}:
        return rank_prefix_operator(3, core_rank_k, control, PRESERVATION_ASYMMETRY), "baseline"
    if control in {"baseline_m4", "rank_prefix_m4"}:
        return rank_prefix_operator(4, core_rank_k, control, PRESERVATION_ASYMMETRY), "baseline"
    if control in {"baseline_m5", "rank_prefix_m5"}:
        return rank_prefix_operator(5, core_rank_k, control, PRESERVATION_ASYMMETRY), "baseline"
    if control in {"drop_weakest_m4_to_core3", "rank_subset_m4_keep_1_2_3"}:
        return rank_subset_operator(4, (1, 2, 3), (4,), core_rank_k, control, TOP_M_DROP_WEAKEST_FROM_TOP_M), "weakest_edge_pruning"
    if control in {"drop_two_weakest_m5_to_core3", "rank_subset_m5_keep_1_2_3"}:
        return rank_subset_operator(5, (1, 2, 3), (4, 5), core_rank_k, control, TOP_M_DROP_TWO_WEAKEST_FROM_TOP_M), "weakest_edge_pruning"
    if control in {"random_delete_one_m4_to_core3", "stochastic_rank_subset_m4_to_3_from_top_m"}:
        return stochastic_rank_subset_operator(4, 3, core_rank_k, control, TOP_M_RANDOM_DELETE_ONE_FROM_TOP_M), "random_top_m_pruning_control"
    if control in {"random_delete_two_m5_to_core3", "stochastic_rank_subset_m5_to_3_from_top_m"}:
        return stochastic_rank_subset_operator(5, 3, core_rank_k, control, TOP_M_RANDOM_DELETE_TWO_FROM_TOP_M), "random_top_m_pruning_control"
    if control in {"drop_strongest_m4_to_m3", "rank_subset_m4_keep_2_3_4"}:
        return rank_subset_operator(4, (2, 3, 4), (1,), core_rank_k, control, TOP_M_DROP_STRONGEST_FROM_TOP_M), "strongest_edge_pruning_control"
    if control.startswith("baseline_m"):
        value = int(control.removeprefix("baseline_m"))
        return rank_prefix_operator(value, core_rank_k, control, PRESERVATION_ASYMMETRY), "baseline"
    raise ValueError(f"unknown boundary control: {control}")


def rank_prefix_operator(base_m: int, core_rank_k: int, alias: str, family: str) -> SelectionOperatorSpec:
    retained = tuple(range(1, base_m + 1))
    return selection_operator(
        operator_family="rank_prefix",
        base_out_degree=base_m,
        effective_out_degree=base_m,
        core_rank_k=core_rank_k,
        retained_rank_set=retained,
        removed_rank_set=tuple(),
        stochastic_flag=0,
        seed_policy="deterministic_rank_order",
        implementation_family=family,
        alias=alias,
    )


def rank_subset_operator(
    base_m: int,
    retained_rank_set: tuple[int, ...],
    removed_rank_set: tuple[int, ...],
    core_rank_k: int,
    alias: str,
    family: str,
) -> SelectionOperatorSpec:
    return selection_operator(
        operator_family="rank_subset",
        base_out_degree=base_m,
        effective_out_degree=len(retained_rank_set),
        core_rank_k=core_rank_k,
        retained_rank_set=retained_rank_set,
        removed_rank_set=removed_rank_set,
        stochastic_flag=0,
        seed_policy="deterministic_rank_order",
        implementation_family=family,
        alias=alias,
    )


def stochastic_rank_subset_operator(
    base_m: int,
    effective_m: int,
    core_rank_k: int,
    alias: str,
    family: str,
) -> SelectionOperatorSpec:
    return selection_operator(
        operator_family="stochastic_rank_subset",
        base_out_degree=base_m,
        effective_out_degree=effective_m,
        core_rank_k=core_rank_k,
        retained_rank_set=tuple(),
        removed_rank_set=tuple(),
        stochastic_flag=1,
        seed_policy="stable_ranked_sample_from_top_m",
        implementation_family=family,
        alias=alias,
    )


def selection_operator(
    *,
    operator_family: str,
    base_out_degree: int,
    effective_out_degree: int,
    core_rank_k: int,
    retained_rank_set: tuple[int, ...],
    removed_rank_set: tuple[int, ...],
    stochastic_flag: int,
    seed_policy: str,
    implementation_family: str,
    alias: str,
) -> SelectionOperatorSpec:
    params = {
        "operator_family": operator_family,
        "base_out_degree": base_out_degree,
        "effective_out_degree": effective_out_degree,
        "core_rank_k": core_rank_k,
        "retained_rank_set": list(retained_rank_set),
        "removed_rank_set": list(removed_rank_set),
        "stochastic_flag": stochastic_flag,
        "seed_policy": seed_policy,
        "implementation_family": implementation_family,
        "legacy_alias": alias,
    }
    retained_token = "sampled" if stochastic_flag else "_".join(str(rank) for rank in retained_rank_set)
    removed_token = "sampled" if stochastic_flag else ("none" if not removed_rank_set else "_".join(str(rank) for rank in removed_rank_set))
    return SelectionOperatorSpec(
        selection_operator_id=(
            f"{operator_family}__m{base_out_degree}_to_{effective_out_degree}"
            f"__k{core_rank_k}__retain_{retained_token}__remove_{removed_token}"
        ),
        operator_family=operator_family,
        operator_params_json=json.dumps(params, sort_keys=True),
        base_out_degree=base_out_degree,
        effective_out_degree=effective_out_degree,
        core_rank_k=core_rank_k,
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
    core_rank_k: int,
    condition_role: str,
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
    baseline_edge_keys: set[tuple[State, State]] = set()
    selected_edge_keys = {
        (source, target)
        for source, targets in system_edges.items()
        for target in targets
    }
    anatomy: dict[tuple[State, State], EdgeAnatomy] = {}
    for source, scored in scored_by_source.items():
        baseline_targets = {target for _energy, target in scored[: max(1, params.out_degree_target)]}
        baseline_edge_keys.update((source, target) for target in baseline_targets)
        for rank_index, (energy, target) in enumerate(scored, start=1):
            selected = int((source, target) in selected_edge_keys)
            baseline_selected = int(target in baseline_targets)
            anatomy[(source, target)] = EdgeAnatomy(
                source_state=source,
                target_state=target,
                candidate_rank=rank_index,
                candidate_energy=float(energy),
                selected_flag=selected,
                baseline_selected_flag=baseline_selected,
                rank_offset_from_core_boundary=rank_index - core_rank_k,
                perturbation_changed_flag=int(
                    condition_role != "baseline" and selected and not baseline_selected
                ),
            )
    return anatomy, selected_edge_keys, baseline_edge_keys


def select_start_states(condition: GeneratedCondition, start_samples: int) -> tuple[State, ...]:
    states = condition.system.states
    count = max(1, min(start_samples, len(states)))
    offset = condition.spec.seed % len(states)
    return tuple(states[(offset + index * 17) % len(states)] for index in range(count))
