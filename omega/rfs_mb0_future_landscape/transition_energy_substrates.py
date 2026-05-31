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
SOFTMAX_PRESERVATION = "softmax_preservation_asymmetry"
MAX_ENTROPY_LOCAL = "max_entropy_local"
MAX_ENTROPY_MACRO_INVARIANT = "max_entropy_macro_invariant"
RANK_CONDITIONED_MAX_ENTROPY = "rank_conditioned_max_entropy"
MAX_ENTROPY_FAMILIES = frozenset({MAX_ENTROPY_LOCAL, MAX_ENTROPY_MACRO_INVARIANT, RANK_CONDITIONED_MAX_ENTROPY})
TOP_M_GEOMETRY_AUDIT_FAMILIES = frozenset({
    PRESERVATION_ASYMMETRY,
    SOFTMAX_PRESERVATION,
    RANK_CONDITIONED_MAX_ENTROPY,
    MAX_ENTROPY_MACRO_INVARIANT,
})
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
    "gibbs_preservation_asymmetry": SOFTMAX_PRESERVATION,
    "gibbs-preservation-asymmetry": SOFTMAX_PRESERVATION,
    "softmax_preservation": SOFTMAX_PRESERVATION,
    "softmax-preservation": SOFTMAX_PRESERVATION,
    "directional_asymmetry_field": DIRECTIONAL_ASYMMETRY,
    "combined_directional_preservation": COMBINED_ASYMMETRY,
    "max_entropy_local_transition": MAX_ENTROPY_LOCAL,
    "max-entropy-local-transition": MAX_ENTROPY_LOCAL,
    "max_entropy_macro_invariant_transition": MAX_ENTROPY_MACRO_INVARIANT,
    "max-entropy-macro-invariant-transition": MAX_ENTROPY_MACRO_INVARIANT,
    "max_entropy_preservation": MAX_ENTROPY_MACRO_INVARIANT,
    "max-entropy-preservation": MAX_ENTROPY_MACRO_INVARIANT,
    "rank_conditioned_maxent": RANK_CONDITIONED_MAX_ENTROPY,
    "rank-conditioned-maxent": RANK_CONDITIONED_MAX_ENTROPY,
    "local_rank_bucket_matched": RANK_CONDITIONED_MAX_ENTROPY,
    "local-rank-bucket-matched": RANK_CONDITIONED_MAX_ENTROPY,
}
TRANSITION_ENERGY_FAMILIES = (
    CONSTRAINT_TEMPLATE_CURRENT,
    LOCALITY_ONLY,
    SMOOTH_RANDOM_POTENTIAL,
    BUDGET_CONSERVATION,
    DIRECTIONAL_ASYMMETRY,
    PRESERVATION_ASYMMETRY,
    COMBINED_ASYMMETRY,
    SOFTMAX_PRESERVATION,
    MAX_ENTROPY_LOCAL,
    MAX_ENTROPY_MACRO_INVARIANT,
    RANK_CONDITIONED_MAX_ENTROPY,
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
    if family == SOFTMAX_PRESERVATION:
        return generate_softmax_preservation_system(params, seed, job, family)
    if family in MAX_ENTROPY_FAMILIES:
        return generate_max_entropy_system(params, seed, job, family)
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
    edges, diagnostics = top_m_transition_edges(states, candidates_by_state, family, params, seed, roughness_strength, potential, asymmetry, budget, job)
    if transition_bool(job, "apply_reversibility", True):
        edges = apply_reversibility(states, edges, params.reversibility_fraction, seed + 11_003)
    metadata = transition_metadata(params, seed, family, states, edges, diagnostics, potential, asymmetry, budget, job)
    if family == PRESERVATION_ASYMMETRY:
        calibration_job = deterministic_preservation_job(job, macro_invariant_beta(job, params))
        scored_by_source = preservation_scored_candidates(states, candidates_by_state, params, seed, roughness_strength, budget, calibration_job)
        calibration_edges = top_m_edges_from_scores(scored_by_source, params)
        metadata.update({
            "sampler_family": sampler_family_label(family),
            "probabilistic_sampling_used": 0,
            "max_entropy_calibration_family": PRESERVATION_ASYMMETRY,
            "max_entropy_calibration_edge_count": sum(len(targets) for targets in calibration_edges.values()),
            **top_m_sampler_audit_metadata(edges, calibration_edges, scored_by_source, params, job),
        })
    return LandscapeSystem(
        system_id=transition_system_id(params, family, seed, job),
        seed=seed,
        family=f"{params.parameter_set_id}_{family}",
        states=states,
        edges=edges,
        transform_names=("top_m_transition_energy",),
        metadata=metadata,
    )


def top_m_transition_edges(
    states: tuple[State, ...],
    candidates_by_state: dict[State, tuple[State, ...]],
    family: str,
    params: RelationParams,
    seed: int,
    roughness_strength: float,
    potential: dict[State, float],
    asymmetry: dict[State, float],
    budget: dict[State, float],
    job: dict[str, object],
) -> tuple[dict[State, tuple[State, ...]], list[float]]:
    edges: dict[State, tuple[State, ...]] = {}
    diagnostics: list[float] = []
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
    return edges, diagnostics


def generate_max_entropy_system(
    params: RelationParams,
    seed: int,
    job: dict[str, object],
    family: str,
) -> LandscapeSystem:
    states = enumerate_states(params.coordinate_count, params.alphabet_size)
    candidates_by_state = {
        state: candidate_successors(state, params.alphabet_size, params.update_footprint)
        for state in states
    }
    budget = budget_field(states, params, job)
    roughness_strength = transition_float(job, "transition_roughness_strength", params.roughness_strength)
    sampler_draws = max(1, int(transition_float(job, "max_entropy_sampler_draws", 16)))
    equivalent_beta = max_entropy_equivalent_beta(job, params)
    calibration_job = deterministic_preservation_job(job, equivalent_beta)
    scored_by_source = preservation_scored_candidates(states, candidates_by_state, params, seed, roughness_strength, budget, calibration_job)
    calibration_edges = top_m_edges_from_scores(scored_by_source, params)
    calibration_edge_count = sum(len(targets) for targets in calibration_edges.values())
    target_counts: dict[str, int] = {}
    if family in {MAX_ENTROPY_MACRO_INVARIANT, RANK_CONDITIONED_MAX_ENTROPY}:
        target_counts = edge_delta_counts(calibration_edges, budget)

    if family == MAX_ENTROPY_MACRO_INVARIANT:
        edges, sampler = matched_delta_max_entropy_edges(
            states,
            candidates_by_state,
            budget,
            target_counts,
            params,
            seed,
            job,
            sampler_draws,
        )
    elif family == RANK_CONDITIONED_MAX_ENTROPY:
        edges, sampler = rank_conditioned_max_entropy_edges(scored_by_source, params, seed, job)
    else:
        edges = uniform_max_entropy_edges(states, candidates_by_state, params, seed, job)
        observed_counts = edge_delta_counts(edges, budget)
        sampler = {
            "status": "ok",
            "draws": 1,
            "best_draw_index": 0,
            "match_error": "",
            "target_counts": {},
            "observed_counts": observed_counts,
            "target_marginal_applied": 0,
            "weight_iterations": 0,
        }
    out_degrees = [len(edges.get(state, ())) for state in states]
    out_degree_violations = sum(int(value != max(1, params.out_degree_target)) for value in out_degrees)
    empty_successors = sum(int(not candidates_by_state.get(state)) for state in states)
    observed_counts = edge_delta_counts(edges, budget)
    target_counts = dict(sampler.get("target_counts", target_counts)) if isinstance(sampler.get("target_counts", {}), dict) else target_counts
    match_error = sampler.get("match_error", "")
    metadata = transition_metadata(params, seed, family, states, edges, [], {}, {}, budget, job)
    sampler_audit = top_m_sampler_audit_metadata(edges, calibration_edges, scored_by_source, params, job)
    selection_rule = "uniform_local_without_macro_constraint"
    constraint_profile = "locality_plus_exact_out_degree"
    if family == MAX_ENTROPY_MACRO_INVARIANT:
        selection_rule = "maximum_entropy_local_matched_macro_invariant_delta"
        constraint_profile = "locality_plus_exact_out_degree_plus_macro_delta_marginal"
    elif family == RANK_CONDITIONED_MAX_ENTROPY:
        selection_rule = "rank_conditioned_local_sampling"
        constraint_profile = "locality_plus_exact_out_degree_plus_local_rank_bucket"
    metadata.update({
        "transition_energy_form": transition_energy_form(family),
        "selection_rule": selection_rule,
        "transform_names": "max_entropy_local_transition",
        "probabilistic_sampling_used": 1,
        "sampler_family": sampler_family_label(family),
        "max_entropy_family": family,
        "max_entropy_constraint_profile": constraint_profile,
        "max_entropy_sampler_status": sampler.get("status", "ok"),
        "max_entropy_sampler_draws": sampler.get("draws", sampler_draws),
        "max_entropy_sampler_best_draw_index": sampler.get("best_draw_index", ""),
        "max_entropy_sampler_weight_iterations": sampler.get("weight_iterations", ""),
        "rank_bucket_multiplier": sampler.get("rank_bucket_multiplier", ""),
        "rank_condition_window_mean": sampler.get("rank_condition_window_mean", ""),
        "max_entropy_equivalent_beta_target": equivalent_beta,
        "equivalent_beta_target": equivalent_beta,
        "macro_invariant_beta": equivalent_beta,
        "budget_weight": equivalent_beta,
        "max_entropy_target_marginal_applied": int(family == MAX_ENTROPY_MACRO_INVARIANT),
        "max_entropy_calibration_family": PRESERVATION_ASYMMETRY if family == MAX_ENTROPY_MACRO_INVARIANT else "",
        "max_entropy_calibration_edge_count": calibration_edge_count,
        "macro_invariant_delta_match_metric": "total_variation_over_rounded_delta_buckets" if family == MAX_ENTROPY_MACRO_INVARIANT else "",
        "macro_invariant_delta_match_error": match_error,
        "macro_invariant_delta_match_tolerance": transition_float(job, "max_entropy_delta_match_error_max", 0.10),
        "macro_invariant_delta_target_distribution": normalized_distribution_json(target_counts),
        "macro_invariant_delta_observed_distribution": normalized_distribution_json(observed_counts),
        "max_entropy_locality_violation_count": 0,
        "max_entropy_out_degree_violation_count": out_degree_violations,
        "max_entropy_empty_successor_source_count": empty_successors,
        "max_entropy_reversibility_fraction_requested": params.reversibility_fraction,
        "max_entropy_reversibility_fraction_applied": 0.0,
        **sampler_audit,
    })
    return LandscapeSystem(
        system_id=transition_system_id(params, family, seed, job),
        seed=seed,
        family=f"{params.parameter_set_id}_{family}",
        states=states,
        edges=edges,
        transform_names=("max_entropy_local_transition",),
        metadata=metadata,
    )


def generate_softmax_preservation_system(
    params: RelationParams,
    seed: int,
    job: dict[str, object],
    family: str,
) -> LandscapeSystem:
    states = enumerate_states(params.coordinate_count, params.alphabet_size)
    candidates_by_state = {
        state: candidate_successors(state, params.alphabet_size, params.update_footprint)
        for state in states
    }
    budget = budget_field(states, params, job)
    roughness_strength = transition_float(job, "transition_roughness_strength", params.roughness_strength)
    beta = macro_invariant_beta(job, params)
    temperature = max(1e-6, transition_float(job, "sampler_temperature", 0.05))
    calibration_job = deterministic_preservation_job(job, beta)
    scored_by_source = preservation_scored_candidates(states, candidates_by_state, params, seed, roughness_strength, budget, calibration_job)
    calibration_edges = top_m_edges_from_scores(scored_by_source, params)
    edges = softmax_sample_edges(scored_by_source, params, seed, job, temperature)
    selected_scores = [score for source, targets in edges.items() for score, target in scored_by_source[source] if target in targets]
    metadata = transition_metadata(params, seed, family, states, edges, selected_scores, {}, {}, budget, job)
    metadata.update({
        "transition_energy_form": transition_energy_form(family),
        "selection_rule": "softmax_gibbs_without_replacement_over_preservation_energy",
        "transform_names": "softmax_preservation_transition_energy",
        "probabilistic_sampling_used": 1,
        "sampler_family": sampler_family_label(family),
        "sampler_temperature": temperature,
        "softmax_temperature": temperature,
        "max_entropy_equivalent_beta_target": beta,
        "equivalent_beta_target": beta,
        "macro_invariant_beta": beta,
        "budget_weight": beta,
        "max_entropy_calibration_family": PRESERVATION_ASYMMETRY,
        "max_entropy_calibration_edge_count": sum(len(targets) for targets in calibration_edges.values()),
        "max_entropy_reversibility_fraction_requested": params.reversibility_fraction,
        "max_entropy_reversibility_fraction_applied": 0.0,
        **top_m_sampler_audit_metadata(edges, calibration_edges, scored_by_source, params, job),
    })
    return LandscapeSystem(
        system_id=transition_system_id(params, family, seed, job),
        seed=seed,
        family=f"{params.parameter_set_id}_{family}",
        states=states,
        edges=edges,
        transform_names=("softmax_preservation_transition_energy",),
        metadata=metadata,
    )


def deterministic_preservation_job(job: dict[str, object], beta: float) -> dict[str, object]:
    out = dict(job)
    out.update({
        "substrate_family": PRESERVATION_ASYMMETRY,
        "transition_energy_family": PRESERVATION_ASYMMETRY,
        "macro_invariant_beta": beta,
        "budget_weight": beta,
        "apply_reversibility": False,
    })
    return out


def preservation_scored_candidates(
    states: tuple[State, ...],
    candidates_by_state: dict[State, tuple[State, ...]],
    params: RelationParams,
    seed: int,
    roughness_strength: float,
    budget: dict[State, float],
    job: dict[str, object],
) -> dict[State, list[tuple[float, State]]]:
    scored_by_source: dict[State, list[tuple[float, State]]] = {}
    for source in states:
        scored = [
            (
                transition_energy(source, target, PRESERVATION_ASYMMETRY, params, seed, roughness_strength, {}, {}, budget, job),
                target,
            )
            for target in candidates_by_state[source]
        ]
        scored.sort(key=lambda item: (item[0], item[1]))
        scored_by_source[source] = scored
    return scored_by_source


def top_m_edges_from_scores(
    scored_by_source: dict[State, list[tuple[float, State]]],
    params: RelationParams,
) -> dict[State, tuple[State, ...]]:
    k = max(1, params.out_degree_target)
    return {
        source: tuple(target for _score, target in scored[:k])
        for source, scored in scored_by_source.items()
    }


def softmax_sample_edges(
    scored_by_source: dict[State, list[tuple[float, State]]],
    params: RelationParams,
    seed: int,
    job: dict[str, object],
    temperature: float,
) -> dict[State, tuple[State, ...]]:
    k = max(1, params.out_degree_target)
    salt = str(job.get("substrate_variant", job.get("job_id", "")))
    edges: dict[State, tuple[State, ...]] = {}
    for source, scored in scored_by_source.items():
        if not scored:
            edges[source] = tuple()
            continue
        min_score = min(score for score, _target in scored)
        ranked = []
        for score, target in scored:
            exponent = -max(-80.0, min(80.0, (score - min_score) / max(1e-6, temperature)))
            weight = max(1e-12, math.exp(exponent))
            unit = max(1e-12, stable_unit(f"{seed}:{salt}:{temperature:g}:{source}:{target}:softmax"))
            key = -math.log(unit) / weight
            ranked.append((key, target))
        ranked.sort(key=lambda item: (item[0], item[1]))
        edges[source] = tuple(sorted(target for _key, target in ranked[:k]))
    return edges


def rank_conditioned_max_entropy_edges(
    scored_by_source: dict[State, list[tuple[float, State]]],
    params: RelationParams,
    seed: int,
    job: dict[str, object],
) -> tuple[dict[State, tuple[State, ...]], dict[str, object]]:
    k = max(1, params.out_degree_target)
    multiplier = max(1.0, transition_float(job, "rank_bucket_multiplier", 2.0))
    salt = str(job.get("substrate_variant", job.get("job_id", "")))
    windows: list[int] = []
    edges: dict[State, tuple[State, ...]] = {}
    for source, scored in scored_by_source.items():
        window = min(len(scored), max(k, int(math.ceil(k * multiplier))))
        windows.append(window)
        pool = scored[:window]
        ranked = sorted(
            pool,
            key=lambda item: (
                stable_unit(f"{seed}:{salt}:{multiplier:g}:{source}:{item[1]}:rank_conditioned"),
                item[1],
            ),
        )
        edges[source] = tuple(sorted(target for _score, target in ranked[:k]))
    return edges, {
        "status": "ok",
        "draws": 1,
        "best_draw_index": 0,
        "match_error": "",
        "target_counts": {},
        "observed_counts": {},
        "target_marginal_applied": 0,
        "weight_iterations": 0,
        "rank_bucket_multiplier": multiplier,
        "rank_condition_window_mean": mean(windows) if windows else 0.0,
    }


def top_m_sampler_audit_metadata(
    edges: dict[State, tuple[State, ...]],
    calibration_edges: dict[State, tuple[State, ...]],
    scored_by_source: dict[State, list[tuple[float, State]]],
    params: RelationParams,
    job: dict[str, object],
) -> dict[str, object]:
    rank_by_edge: dict[tuple[State, State], int] = {}
    energy_by_edge: dict[tuple[State, State], float] = {}
    for source, scored in scored_by_source.items():
        for index, (score, target) in enumerate(scored, start=1):
            rank_by_edge[(source, target)] = index
            energy_by_edge[(source, target)] = score
    selected_edge_set = {(source, target) for source, targets in edges.items() for target in targets}
    calibration_edge_set = {(source, target) for source, targets in calibration_edges.items() for target in targets}
    intersection = len(selected_edge_set & calibration_edge_set)
    union = len(selected_edge_set | calibration_edge_set)
    selected_ranks = [rank_by_edge[item] for item in selected_edge_set if item in rank_by_edge]
    calibration_ranks = [rank_by_edge[item] for item in calibration_edge_set if item in rank_by_edge]
    selected_energies = [energy_by_edge[item] for item in selected_edge_set if item in energy_by_edge]
    calibration_energies = [energy_by_edge[item] for item in calibration_edge_set if item in energy_by_edge]
    selected_rank_counts = count_rank_buckets(selected_ranks, params)
    calibration_rank_counts = count_rank_buckets(calibration_ranks, params)
    selected_energy_counts = count_energy_buckets(selected_energies)
    calibration_energy_counts = count_energy_buckets(calibration_energies)
    per_state_errors = []
    for source in scored_by_source:
        selected_source_ranks = [rank_by_edge[(source, target)] for target in edges.get(source, ()) if (source, target) in rank_by_edge]
        calibration_source_ranks = [rank_by_edge[(source, target)] for target in calibration_edges.get(source, ()) if (source, target) in rank_by_edge]
        per_state_errors.append(distribution_total_variation(count_rank_buckets(calibration_source_ranks, params), count_rank_buckets(selected_source_ranks, params)))
    return {
        "sampler_family": sampler_family_label(str(job.get("substrate_family", ""))),
        "top_m_calibration_edge_count": len(calibration_edge_set),
        "edge_jaccard_vs_top_m_calibration": intersection / max(1, union),
        "selected_edge_overlap_fraction_vs_top_m_calibration": intersection / max(1, len(calibration_edge_set)),
        "selected_edge_retention_fraction_vs_top_m_calibration": intersection / max(1, len(selected_edge_set)),
        "selected_edge_symmetric_difference_fraction_vs_top_m": (union - intersection) / max(1, union),
        "selected_rank_mean": mean(selected_ranks) if selected_ranks else "",
        "calibration_rank_mean": mean(calibration_ranks) if calibration_ranks else "",
        "rank_distribution_match_error": distribution_total_variation(calibration_rank_counts, selected_rank_counts),
        "rank_bucket_distribution": normalized_distribution_json(selected_rank_counts),
        "calibration_rank_bucket_distribution": normalized_distribution_json(calibration_rank_counts),
        "selected_energy_mean": mean(selected_energies) if selected_energies else "",
        "calibration_energy_mean": mean(calibration_energies) if calibration_energies else "",
        "energy_mean_delta_vs_top_m": (mean(selected_energies) - mean(calibration_energies)) if selected_energies and calibration_energies else "",
        "energy_distribution_match_error": distribution_total_variation(calibration_energy_counts, selected_energy_counts),
        "energy_bucket_distribution": normalized_distribution_json(selected_energy_counts),
        "calibration_energy_bucket_distribution": normalized_distribution_json(calibration_energy_counts),
        "per_state_rank_bucket_match_error_mean": mean(per_state_errors) if per_state_errors else "",
        "per_state_rank_bucket_match_error_max": max(per_state_errors) if per_state_errors else "",
    }


def count_rank_buckets(ranks: list[int], params: RelationParams) -> dict[str, int]:
    counts: dict[str, int] = {}
    k = max(1, params.out_degree_target)
    for rank in ranks:
        if rank <= k:
            bucket = "top_m"
        elif rank <= 2 * k:
            bucket = "near_top_2m"
        elif rank <= 4 * k:
            bucket = "mid_4m"
        else:
            bucket = "tail"
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def count_energy_buckets(values: list[float]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        bucket = f"{round(float(value), 3):.3f}"
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def sampler_family_label(family: str) -> str:
    canonical = canonical_transition_energy_family(family)
    if canonical == PRESERVATION_ASYMMETRY:
        return "deterministic_top_m"
    if canonical == SOFTMAX_PRESERVATION:
        return "softmax_gibbs_energy"
    if canonical == RANK_CONDITIONED_MAX_ENTROPY:
        return "rank_conditioned_local"
    if canonical == MAX_ENTROPY_MACRO_INVARIANT:
        return "max_entropy_macro_marginal"
    if canonical == MAX_ENTROPY_LOCAL:
        return "max_entropy_local"
    return canonical


def transition_system_id(params: RelationParams, family: str, seed: int, job: dict[str, object]) -> str:
    variant = str(job.get("substrate_variant", "") or "").strip()
    suffix = f"_{safe_system_id_token(variant)}" if variant else ""
    return f"{params.parameter_set_id}_{family}{suffix}_seed{seed}"


def safe_system_id_token(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value).strip("_")


def uniform_max_entropy_edges(
    states: tuple[State, ...],
    candidates_by_state: dict[State, tuple[State, ...]],
    params: RelationParams,
    seed: int,
    job: dict[str, object],
) -> dict[State, tuple[State, ...]]:
    k = max(1, params.out_degree_target)
    salt = str(job.get("substrate_variant", job.get("job_id", "")))
    edges: dict[State, tuple[State, ...]] = {}
    for source in states:
        candidates = candidates_by_state[source]
        selected = sorted(candidates, key=lambda target: stable_unit(f"{seed}:{salt}:{source}:{target}:max_entropy_uniform"))[:k]
        edges[source] = tuple(sorted(selected))
    return edges


def matched_delta_max_entropy_edges(
    states: tuple[State, ...],
    candidates_by_state: dict[State, tuple[State, ...]],
    budget: dict[State, float],
    target_counts: dict[str, int],
    params: RelationParams,
    seed: int,
    job: dict[str, object],
    sampler_draws: int,
) -> tuple[dict[State, tuple[State, ...]], dict[str, object]]:
    weights, expected_counts, iterations = fit_delta_bucket_weights(states, candidates_by_state, budget, target_counts, params)
    best_edges: dict[State, tuple[State, ...]] | None = None
    best_counts: dict[str, int] = {}
    best_error = float("inf")
    best_draw = 0
    for draw_index in range(max(1, sampler_draws)):
        edges = weighted_max_entropy_edges(states, candidates_by_state, budget, weights, params, seed, job, draw_index)
        counts = edge_delta_counts(edges, budget)
        error = distribution_total_variation(target_counts, counts)
        if error < best_error:
            best_edges = edges
            best_counts = counts
            best_error = error
            best_draw = draw_index
    if best_edges is None:
        best_edges = uniform_max_entropy_edges(states, candidates_by_state, params, seed, job)
        best_counts = edge_delta_counts(best_edges, budget)
        best_error = distribution_total_variation(target_counts, best_counts)
    return best_edges, {
        "status": "ok",
        "draws": max(1, sampler_draws),
        "best_draw_index": best_draw,
        "match_error": best_error,
        "target_counts": target_counts,
        "observed_counts": best_counts,
        "expected_counts": expected_counts,
        "target_marginal_applied": 1,
        "weight_iterations": iterations,
    }


def fit_delta_bucket_weights(
    states: tuple[State, ...],
    candidates_by_state: dict[State, tuple[State, ...]],
    budget: dict[State, float],
    target_counts: dict[str, int],
    params: RelationParams,
) -> tuple[dict[str, float], dict[str, float], int]:
    buckets = sorted(set(target_counts) | {
        delta_bucket(abs(budget[target] - budget[source]))
        for source in states
        for target in candidates_by_state[source]
    })
    weights = {bucket: 1.0 for bucket in buckets}
    target_total = max(1.0, float(sum(target_counts.values())))
    k = max(1, params.out_degree_target)
    expected: dict[str, float] = {bucket: 0.0 for bucket in buckets}
    epsilon = 1e-9
    iterations = 40
    for _iteration in range(iterations):
        expected = {bucket: 0.0 for bucket in buckets}
        for source in states:
            candidates = candidates_by_state[source]
            denom = sum(weights[delta_bucket(abs(budget[target] - budget[source]))] for target in candidates)
            if denom <= 0:
                continue
            for target in candidates:
                bucket = delta_bucket(abs(budget[target] - budget[source]))
                expected[bucket] += k * weights[bucket] / denom
        expected_total = max(1.0, sum(expected.values()))
        for bucket in buckets:
            target_share = (float(target_counts.get(bucket, 0)) + epsilon) / target_total
            expected_share = (expected.get(bucket, 0.0) + epsilon) / expected_total
            weights[bucket] *= math.sqrt(target_share / expected_share)
            weights[bucket] = min(max(weights[bucket], 1e-6), 1e6)
    return weights, expected, iterations


def weighted_max_entropy_edges(
    states: tuple[State, ...],
    candidates_by_state: dict[State, tuple[State, ...]],
    budget: dict[State, float],
    weights: dict[str, float],
    params: RelationParams,
    seed: int,
    job: dict[str, object],
    draw_index: int,
) -> dict[State, tuple[State, ...]]:
    k = max(1, params.out_degree_target)
    salt = str(job.get("substrate_variant", job.get("job_id", "")))
    edges: dict[State, tuple[State, ...]] = {}
    for source in states:
        scored = []
        for target in candidates_by_state[source]:
            bucket = delta_bucket(abs(budget[target] - budget[source]))
            weight = max(1e-9, weights.get(bucket, 1e-9))
            unit = max(1e-12, stable_unit(f"{seed}:{salt}:{draw_index}:{source}:{target}:max_entropy_weighted"))
            key = -math.log(unit) / weight
            scored.append((key, target))
        scored.sort(key=lambda item: (item[0], item[1]))
        edges[source] = tuple(sorted(target for _key, target in scored[:k]))
    return edges


def edge_delta_counts(edges: dict[State, tuple[State, ...]], budget: dict[State, float]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for source, targets in edges.items():
        for target in targets:
            bucket = delta_bucket(abs(budget[target] - budget[source]))
            counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def delta_bucket(value: float) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".") or "0"


def normalized_distribution_json(counts: dict[str, int] | dict[str, float]) -> str:
    total = float(sum(float(value) for value in counts.values()))
    if total <= 0:
        return "{}"
    return json.dumps({str(key): float(value) / total for key, value in sorted(counts.items())}, sort_keys=True)


def distribution_total_variation(left: dict[str, int], right: dict[str, int]) -> float:
    keys = set(left) | set(right)
    left_total = max(1.0, float(sum(left.values())))
    right_total = max(1.0, float(sum(right.values())))
    return 0.5 * sum(abs(float(left.get(key, 0)) / left_total - float(right.get(key, 0)) / right_total) for key in keys)


def max_entropy_equivalent_beta(job: dict[str, object], params: RelationParams) -> float:
    return transition_float(job, "equivalent_beta_target", macro_invariant_beta(job, params))


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
    if family == SOFTMAX_PRESERVATION:
        return "softmax_gibbs_without_replacement_over_preservation_energy"
    if family == MAX_ENTROPY_LOCAL:
        return "maximum_entropy_sample_over_local_candidate_edges_with_exact_out_degree"
    if family == MAX_ENTROPY_MACRO_INVARIANT:
        return "maximum_entropy_sample_over_local_edges_matched_to_macro_invariant_delta_marginal"
    if family == RANK_CONDITIONED_MAX_ENTROPY:
        return "maximum_entropy_sample_over_local_rank_conditioned_candidate_window"
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


def transition_bool(job: dict[str, object], key: str, default: bool) -> bool:
    value = job.get(key, default)
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return default
    return str(value).strip().lower() not in {"0", "false", "no", "off"}


def stable_unit(text: str) -> float:
    value = 2166136261
    for char in text:
        value ^= ord(char)
        value = (value * 16777619) % 2**32
    return value / 2**32
