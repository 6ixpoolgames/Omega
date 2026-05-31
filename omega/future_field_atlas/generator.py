from __future__ import annotations

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

from .contracts import ConditionSpec, EdgeAnatomy, GeneratedCondition
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
                    family, base_m, effective_m, role = boundary_control_spec(control, core_rank_k)
                    params = relation_params(group_index, base_m)
                    condition_id = (
                        f"g{group_index:02d}_s{fresh_index:02d}_"
                        f"beta{safe_token(f'{beta:g}')}_{safe_token(control)}"
                    )
                    job = {
                        "job_id": condition_id,
                        "condition_id": condition_id,
                        "substrate_family": family,
                        "transition_energy_family": family,
                        "substrate_variant": control,
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
                        substrate_family=family,
                        substrate_variant=control,
                        substrate_id=system.system_id,
                        boundary_control=control,
                        role=role,
                        base_m=base_m,
                        effective_m=effective_m,
                        core_rank_k=core_rank_k,
                        macro_invariant_kind=macro_invariant_kind,
                        macro_invariant_beta=beta,
                        perturbation_family="none" if role == "baseline" else control,
                        perturbation_strength=0.0 if role == "baseline" else 1.0,
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


def boundary_control_spec(control: str, core_rank_k: int) -> tuple[str, int, int, str]:
    if control == "baseline_m3":
        return PRESERVATION_ASYMMETRY, 3, 3, "baseline"
    if control == "baseline_m4":
        return PRESERVATION_ASYMMETRY, 4, 4, "baseline"
    if control == "baseline_m5":
        return PRESERVATION_ASYMMETRY, 5, 5, "baseline"
    if control == "drop_weakest_m4_to_core3":
        return TOP_M_DROP_WEAKEST_FROM_TOP_M, 4, max(1, 4 - 1), "weakest_edge_pruning"
    if control == "drop_two_weakest_m5_to_core3":
        return TOP_M_DROP_TWO_WEAKEST_FROM_TOP_M, 5, max(1, 5 - 2), "weakest_edge_pruning"
    if control == "random_delete_one_m4_to_core3":
        return TOP_M_RANDOM_DELETE_ONE_FROM_TOP_M, 4, max(1, 4 - 1), "random_top_m_pruning_control"
    if control == "random_delete_two_m5_to_core3":
        return TOP_M_RANDOM_DELETE_TWO_FROM_TOP_M, 5, max(1, 5 - 2), "random_top_m_pruning_control"
    if control == "drop_strongest_m4_to_m3":
        return TOP_M_DROP_STRONGEST_FROM_TOP_M, 4, max(1, 4 - 1), "strongest_edge_pruning_control"
    if control.startswith("baseline_m"):
        value = int(control.removeprefix("baseline_m"))
        return PRESERVATION_ASYMMETRY, value, value, "baseline"
    raise ValueError(f"unknown boundary control: {control}")


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
                core_flag=int(rank_index <= core_rank_k),
                fringe_flag=int(rank_index > core_rank_k),
                baseline_selected_flag=baseline_selected,
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

