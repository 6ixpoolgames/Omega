from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

from .landscape import exact_frontier
from .probes import Probe, generate_probes
from .relation_generator import RelationParams, _constraint_profile, _constraint_violation, _stable_hash, generate_relation_system
from .substrate import LandscapeSystem, State


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 path metric calibration smoke.")
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_relation_generator_phenotype_repair"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_path_metric_calibration_smoke"))
    parser.add_argument("--candidate-envs", type=int, default=8)
    parser.add_argument("--matched-controls", type=int, default=8)
    parser.add_argument("--start-samples", type=int, default=3)
    parser.add_argument("--path-horizons", type=str, default="4,8")
    parser.add_argument("--sample-paths-per-start", type=int, default=256)
    parser.add_argument("--path-null-replicates", type=int, default=3)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-jobs", type=int, default=288)
    parser.add_argument("--max-runtime-seconds", type=int, default=2400)
    parser.add_argument(
        "--probe-families",
        type=str,
        default=(
            "existing_low,coordinate_tuple_k3,coordinate_tuple_k4,"
            "composite_pair_plus_single,composite_two_pairs,"
            "composite_local_window_plus_constraint_count,constraint_violation_count,"
            "constraint_violation_count_plus_local_tuple,constraint_profile_hash,"
            "relation_role,full_state_hash,full_state_strict"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    horizons = tuple(int(item.strip()) for item in args.path_horizons.split(",") if item.strip())
    probe_keys = tuple(item.strip() for item in args.probe_families.split(",") if item.strip())
    jobs, selection_rows, control_rows = build_jobs(args, horizons, probe_keys)
    jobs = jobs[: args.max_jobs]
    results = []
    errors = []
    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(run_path_job, job): job for job in jobs}
        for future in as_completed(futures, timeout=args.max_runtime_seconds):
            job = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # noqa: BLE001
                errors.append({"job_id": job["job_id"], "error": repr(exc)})
            if time.perf_counter() - started > args.max_runtime_seconds:
                break
    write_outputs(args.out, args, started, jobs, results, selection_rows, control_rows, errors)


def build_jobs(args: argparse.Namespace, horizons: tuple[int, ...], probe_keys: tuple[str, ...]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    phenotype_rows = _read_csv(args.source_run / "candidate_phenotype_summary.csv")
    stage_dir = args.source_run / f"start_samples_{args.start_samples}"
    if not stage_dir.exists():
        stage_dir = args.source_run / "start_samples_3"
    metadata = {row["environment_id"]: row for row in _read_csv(stage_dir / "generated_environment_metadata.csv")}
    windows = _read_csv(stage_dir / "relation_atlas_window_summary.csv")
    window_by_key = {(row["family"], row["probe_family"], row["window"]): row for row in windows}
    candidates = [
        row for row in phenotype_rows
        if row.get("roughness_artifact_flag") == "0"
        and row.get("start_coverage_class") in {"environment_level", "basin_local"}
        and row.get("roughness_strength_profile_class") in {"noise_tolerant", "noise_sensitive_smooth"}
    ]
    candidates.sort(key=lambda row: (row.get("phenotype_class") == "constraint_dominated_roughness_sensitive", row.get("start_coverage_class") == "environment_level"), reverse=True)
    selected = []
    seen_envs = set()
    for row in candidates:
        env = row["environment_id"]
        if env in metadata and env not in seen_envs:
            selected.append(row)
            seen_envs.add(env)
        if len(selected) >= args.candidate_envs:
            break
    control_candidates = [
        row for row in windows
        if row.get("aggregate_window_class_v1_2") != "structured_candidate_window"
        and row.get("family") in metadata
    ]
    jobs = []
    selection_rows = []
    control_rows = []
    for index, candidate in enumerate(selected):
        env = candidate["environment_id"]
        source_probe_family = candidate["probe_family"]
        window = candidate["window_name"]
        matched = match_control(candidate, control_candidates, metadata)
        selection_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "environment_id": env,
                "source_probe_family": source_probe_family,
                "window_name": window,
                "matched_control_environment_id": matched.get("family", ""),
                "matched_control_match_quality": matched.get("match_quality", "none"),
            }
        )
        rows_for_candidate = [
            ("candidate", env, source_probe_family, window, candidate.get("candidate_id", f"candidate_{index}")),
        ]
        if matched:
            control_rows.append(
                {
                    "candidate_environment_id": env,
                    "matched_control_environment_id": matched["family"],
                    "matched_control_probe_family": matched["probe_family"],
                    "matched_control_window": matched["window"],
                    "matched_control_match_quality": matched["match_quality"],
                }
            )
            rows_for_candidate.append(("matched_control", matched["family"], matched["probe_family"], matched["window"], f"control_for_{index}"))
        same_env_controls = [
            row for row in control_candidates
            if row["family"] == env and row["probe_family"] == source_probe_family and row["window"] != window
        ][:1]
        for control in same_env_controls:
            rows_for_candidate.append(("same_environment_window_control", control["family"], control["probe_family"], control["window"], f"same_env_control_for_{index}"))
        for row_kind, row_env, row_probe, row_window, row_id in rows_for_candidate:
            if row_env not in metadata:
                continue
            for probe_key in probe_keys:
                for horizon in horizons:
                    jobs.append(
                        {
                            "job_id": f"{row_kind}_{index}_{probe_key}_{row_window}_H{horizon}",
                            "row_kind": row_kind,
                            "row_id": row_id,
                            "candidate_environment_id": env,
                            "environment_id": row_env,
                            "metadata_json": metadata[row_env]["metadata_json"],
                            "seed": int(metadata[row_env]["seed"]),
                            "source_probe_family": row_probe,
                            "probe_key": probe_key,
                            "window_name": row_window,
                            "path_horizon": horizon,
                            "start_samples": args.start_samples,
                            "sample_paths_per_start": args.sample_paths_per_start,
                            "path_null_replicates": args.path_null_replicates,
                            "window_class": window_by_key.get((row_env, row_probe, row_window), {}).get("aggregate_window_class_v1_2", ""),
                        }
                    )
    return jobs, selection_rows, control_rows


def match_control(candidate: dict[str, str], controls: list[dict[str, str]], metadata: dict[str, dict[str, str]]) -> dict[str, str]:
    candidate_meta = json.loads(metadata[candidate["environment_id"]]["metadata_json"])
    best = None
    best_score = -1
    for control in controls:
        if control["family"] == candidate["environment_id"]:
            continue
        control_meta = json.loads(metadata[control["family"]]["metadata_json"])
        score = 0
        for key in ("out_degree_target", "constraint_density", "constraint_strength", "asymmetry_strength", "reversibility_fraction", "roughness_strength"):
            score += int(str(candidate_meta.get(key)) == str(control_meta.get(key)))
        if score > best_score:
            best = dict(control)
            best_score = score
    if best is None:
        return {}
    best["match_quality"] = "strong" if best_score >= 4 else "weak"
    return best


def run_path_job(job: dict[str, object]) -> dict[str, object]:
    params = params_from_metadata(json.loads(str(job["metadata_json"])))
    system = generate_relation_system(params, int(job["seed"]))
    probe, alphabet_size, probe_group = build_probe(system, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [system.states[(system.seed + i * 17) % len(system.states)] for i in range(int(job["start_samples"]))]
    sequences = []
    rng = random.Random(system.seed + int(job["path_horizon"]) * 1009 + len(str(job["probe_key"])))
    for start in starts:
        sequences.extend(sample_signature_paths(system, probe, start, int(job["path_horizon"]), int(job["sample_paths_per_start"]), rng))
    low_outdegree = low_outdegree_diagnostics(system, starts, int(job["path_horizon"]), sequences)
    metrics = path_metrics(sequences, probe, len(system.states), alphabet_size)
    endpoint_nulls = []
    unigram_nulls = []
    for replicate in range(int(job["path_null_replicates"])):
        null_rng = random.Random(system.seed + replicate * 7919 + int(job["path_horizon"]))
        endpoint_nulls.append(path_metrics(endpoint_support_randomized(sequences, null_rng), probe, len(system.states), alphabet_size))
        unigram_nulls.append(path_metrics(unigram_shuffled(sequences, null_rng), probe, len(system.states), alphabet_size))
    result = {
        **{key: job[key] for key in ("job_id", "row_kind", "row_id", "candidate_environment_id", "environment_id", "probe_key", "source_probe_family", "window_name", "path_horizon", "window_class")},
        "probe_family": probe.probe_family,
        "probe_name": probe.name,
        "probe_group": probe_group,
        **metrics,
        **low_outdegree,
        "endpoint_bigram_mi_rank": rank_metric(metrics["bigram_mutual_information"], [row["bigram_mutual_information"] for row in endpoint_nulls]),
        "endpoint_trigram_gain_rank": rank_metric(metrics["predictive_gain_bigram_context"], [row["predictive_gain_bigram_context"] for row in endpoint_nulls]),
        "unigram_bigram_mi_rank": rank_metric(metrics["bigram_mutual_information"], [row["bigram_mutual_information"] for row in unigram_nulls]),
        "unigram_trigram_gain_rank": rank_metric(metrics["predictive_gain_bigram_context"], [row["predictive_gain_bigram_context"] for row in unigram_nulls]),
        "path_null_replicates": int(job["path_null_replicates"]),
    }
    result.update(fakeout_flags(result))
    result["path_evidence_level"] = evidence_level(result)
    result["would_promote_if_enabled"] = int(result["path_evidence_level"] == "provisional_path_process_blocked_by_calibration_policy")
    result["promotion_blocked_by_probe_resolution_policy"] = result["would_promote_if_enabled"]
    return result


def sample_signature_paths(system: object, probe: Probe, start: tuple[int, ...], horizon: int, count: int, rng: random.Random) -> list[tuple[object, ...]]:
    paths = []
    for _ in range(count):
        state = start
        signatures = [probe.fn(state)]
        for _step in range(horizon):
            targets = list(system.edges.get(state, ()))  # type: ignore[attr-defined]
            if not targets:
                break
            state = rng.choice(targets)
            signatures.append(probe.fn(state))
        paths.append(tuple(signatures))
    return paths


def build_probe(system: LandscapeSystem, probe_key: str, source_probe_family: str) -> tuple[Probe, int, str]:
    modulus = int(system.metadata.get("alphabet_size", 3))
    coordinate_count = len(system.states[0])
    constraints = json.loads(str(system.metadata.get("constraint_json", "[]")))
    in_degree = {state: 0 for state in system.states}
    edge_set = {(source, target) for source, targets in system.edges.items() for target in targets}
    for _source, targets in system.edges.items():
        for target in targets:
            in_degree[target] = in_degree.get(target, 0) + 1

    def bucket(value: int) -> int:
        if value <= 1:
            return value
        if value <= 3:
            return 2
        return 3

    def quantile_rank_map(values_by_state: dict[State, float], bins: int) -> dict[State, int]:
        values = sorted(values_by_state.values())
        if not values:
            return {state: 0 for state in system.states}
        out: dict[State, int] = {}
        for state, value in values_by_state.items():
            lower_count = sum(1 for item in values if item < value)
            out[state] = min(bins - 1, int(bins * lower_count / max(1, len(values))))
        return out

    if probe_key == "existing_low":
        probes = [probe for probe in generate_probes(system, 2) if probe.probe_family == source_probe_family]
        if not probes:
            probes = [probe for probe in generate_probes(system, 2) if probe.probe_family == "pairwise_ordered_projection"]
        if not probes:
            raise ValueError(f"no existing probe for family {source_probe_family}")
        probe = probes[0]
        return Probe(f"existing_low_{probe.name}", probe.mode, probe.fn, f"existing_low__{probe.probe_family}", probe.arity), max(1, modulus ** max(1, probe.arity)), "existing_low"

    if probe_key == "coordinate_tuple_k3":
        coords = tuple(range(min(3, coordinate_count)))
        return Probe("coordinate_tuple_k3_0", "coordinate_tuple", lambda s, coords=coords: tuple(s[index] for index in coords), "coordinate_tuple_k3", len(coords)), modulus ** len(coords), "coordinate_tuple"

    if probe_key == "coordinate_tuple_k4":
        coords = tuple(range(min(4, coordinate_count)))
        return Probe("coordinate_tuple_k4_0", "coordinate_tuple", lambda s, coords=coords: tuple(s[index] for index in coords), "coordinate_tuple_k4", len(coords)), modulus ** len(coords), "coordinate_tuple"

    if probe_key == "composite_pair_plus_single":
        coords = (0, 1, min(2, coordinate_count - 1))
        return Probe("composite_pair_plus_single_0", "composite", lambda s, coords=coords: (s[coords[0]], s[coords[1]], s[coords[2]]), "composite_pair_plus_single", 3), modulus ** 3, "composite"

    if probe_key == "composite_two_pairs":
        coords = (0, 1, min(2, coordinate_count - 1), min(3, coordinate_count - 1))
        return Probe("composite_two_pairs_0", "composite", lambda s, coords=coords: (s[coords[0]], s[coords[1]], s[coords[2]], s[coords[3]]), "composite_two_pairs", 4), modulus ** 4, "composite"

    if probe_key == "composite_local_window_plus_constraint_count":
        coords = tuple(range(min(2, coordinate_count)))
        max_count = len(constraints) + 1
        return (
            Probe(
                "composite_local_window_plus_constraint_count_0",
                "composite_constraint",
                lambda s, coords=coords, constraints=constraints: tuple(s[index] for index in coords) + (int(round(_constraint_violation(s, constraints))),),
                "composite_local_window_plus_constraint_count",
                len(coords) + 1,
            ),
            (modulus ** len(coords)) * max_count,
            "constraint_profile",
        )

    if probe_key == "constraint_violation_count":
        max_count = len(constraints) + 1
        return Probe("constraint_violation_count", "constraint_profile", lambda s, constraints=constraints: (int(round(_constraint_violation(s, constraints))),), "constraint_violation_count", 1), max_count, "constraint_profile"

    if probe_key == "constraint_violation_count_plus_local_tuple":
        coords = tuple(range(min(2, coordinate_count)))
        max_count = len(constraints) + 1
        return (
            Probe(
                "constraint_violation_count_plus_local_tuple_0",
                "constraint_profile",
                lambda s, coords=coords, constraints=constraints: (int(round(_constraint_violation(s, constraints))),) + tuple(s[index] for index in coords),
                "constraint_violation_count_plus_local_tuple",
                len(coords) + 1,
            ),
            max_count * (modulus ** len(coords)),
            "constraint_profile",
        )

    if probe_key == "constraint_profile_hash":
        buckets = min(256, max(16, 2 ** min(8, max(1, len(constraints)))))
        return Probe("constraint_profile_hash", "constraint_profile", lambda s, constraints=constraints, buckets=buckets: (_stable_hash(str(_constraint_profile(s, constraints))) % buckets,), "constraint_profile_hash", 1), buckets, "constraint_profile"

    if probe_key == "relation_role":
        def relation_role(s: State) -> tuple[int, ...]:
            out_degree = len(system.edges.get(s, ()))
            reciprocal = sum(int((target, s) in edge_set) for target in system.edges.get(s, ()))
            depth_1 = len(set(system.edges.get(s, ())))
            depth_2_states = {item for target in system.edges.get(s, ()) for item in system.edges.get(target, ())}
            return (bucket(out_degree), bucket(in_degree.get(s, 0)), bucket(reciprocal), bucket(depth_1), bucket(len(depth_2_states)))

        return Probe("relation_role_buckets", "relation_role", relation_role, "relation_role", 5), 4 ** 5, "relation_role"

    if probe_key == "constraint_neighborhood_histogram":
        def constraint_neighborhood_histogram(s: State) -> tuple[int, ...]:
            targets = tuple(system.edges.get(s, ()))
            neighborhood = (s,) + targets[: min(4, max(1, len(targets)))]
            counts = Counter(bucket(int(round(_constraint_violation(state, constraints)))) for state in neighborhood)
            return tuple(counts.get(index, 0) for index in range(4))

        return Probe("constraint_neighborhood_histogram", "quotient_constraint_neighborhood", constraint_neighborhood_histogram, "constraint_neighborhood_histogram", 4), 5 ** 4, "constraint_neighborhood"

    if probe_key == "relation_neighborhood_degree_asymmetry_histogram":
        def relation_neighborhood_degree_asymmetry_histogram(s: State) -> tuple[int, ...]:
            targets = tuple(system.edges.get(s, ()))
            reciprocal = sum(int((target, s) in edge_set) for target in targets)
            asymmetry = max(0, len(targets) - reciprocal)
            successor_out = sum(len(system.edges.get(target, ())) for target in targets)
            return (bucket(len(targets)), bucket(in_degree.get(s, 0)), bucket(reciprocal), bucket(asymmetry), bucket(successor_out))

        return Probe("relation_neighborhood_degree_asymmetry_histogram", "quotient_relation_geometry", relation_neighborhood_degree_asymmetry_histogram, "relation_neighborhood_degree_asymmetry_histogram", 5), 4 ** 5, "relation_geometry"

    if probe_key == "frontier_response_bucket":
        def frontier_response_bucket(s: State) -> tuple[int, ...]:
            h1 = set(system.edges.get(s, ()))
            h2 = {item for target in h1 for item in system.edges.get(target, ())}
            h3 = {item for target in h2 for item in system.edges.get(target, ())}
            growth_12 = len(h2) - len(h1)
            growth_23 = len(h3) - len(h2)
            return (bucket(len(h1)), bucket(max(0, growth_12)), bucket(max(0, growth_23)))

        return Probe("frontier_response_bucket", "quotient_frontier_response", frontier_response_bucket, "frontier_response_bucket", 3), 4 ** 3, "frontier_response"

    if probe_key == "motif_count_bucket":
        def motif_count_bucket(s: State) -> tuple[int, ...]:
            targets = tuple(system.edges.get(s, ()))
            reciprocal = sum(int((target, s) in edge_set) for target in targets)
            two_step_return = 0
            feed_forward = 0
            target_set = set(targets)
            for target in targets:
                target_targets = set(system.edges.get(target, ()))
                two_step_return += int(s in target_targets)
                feed_forward += len(target_set.intersection(target_targets))
            return (bucket(reciprocal), bucket(two_step_return), bucket(feed_forward))

        return Probe("motif_count_bucket", "quotient_relation_motif", motif_count_bucket, "motif_count_bucket", 3), 4 ** 3, "relation_motif"

    if probe_key == "multi_scale_support_region_bucket":
        def multi_scale_support_region_bucket(s: State) -> tuple[int, ...]:
            h1 = set(system.edges.get(s, ()))
            h2 = {item for target in h1 for item in system.edges.get(target, ())}
            h3 = {item for target in h2 for item in system.edges.get(target, ())}
            constraint_bucket = bucket(int(round(_constraint_violation(s, constraints))))
            return (bucket(len(h1)), bucket(len(h2)), bucket(len(h3)), constraint_bucket)

        return Probe("multi_scale_support_region_bucket", "quotient_support_growth", multi_scale_support_region_bucket, "multi_scale_support_region_bucket", 4), 4 ** 4, "support_growth"

    if probe_key == "degree_profile_rank":
        out_rank = quantile_rank_map({state: float(len(system.edges.get(state, ()))) for state in system.states}, 4)
        in_rank = quantile_rank_map({state: float(in_degree.get(state, 0)) for state in system.states}, 4)
        return Probe("degree_profile_rank", "degree_rank_profile", lambda s, out_rank=out_rank, in_rank=in_rank: (out_rank[s], in_rank[s]), "degree_profile_rank", 2), 16, "degree_rank"

    if probe_key == "constraint_cross_degree_rank":
        out_rank = quantile_rank_map({state: float(len(system.edges.get(state, ()))) for state in system.states}, 4)
        levels = max(3, min(6, len(constraints) + 1))

        def constraint_cross_degree_rank(s: State, out_rank=out_rank, constraints=constraints, levels=levels) -> tuple[int, int]:
            violation = min(levels - 1, int(round(_constraint_violation(s, constraints))))
            return (violation, out_rank[s])

        return Probe("constraint_cross_degree_rank", "cross_constraint_degree", constraint_cross_degree_rank, "constraint_cross_degree_rank", 2), levels * 4, "cross_constraint_degree"

    if probe_key == "constraint_gradient_class":
        levels = max(3, min(6, len(constraints) + 1))

        def constraint_gradient_class(s: State, constraints=constraints, levels=levels) -> tuple[int, int]:
            self_violation = _constraint_violation(s, constraints)
            targets = tuple(system.edges.get(s, ()))
            if not targets:
                return (min(levels - 1, int(round(self_violation))), 0)
            neighbor_mean = mean(_constraint_violation(target, constraints) for target in targets)
            delta = neighbor_mean - self_violation
            if delta > 0.3:
                gradient = 1
            elif delta < -0.3:
                gradient = 2
            else:
                gradient = 0
            return (min(levels - 1, int(round(self_violation))), gradient)

        return Probe("constraint_gradient_class", "constraint_gradient", constraint_gradient_class, "constraint_gradient_class", 2), levels * 3, "constraint_gradient"

    if probe_key == "horizon_growth_contrast_v2":
        h1 = {state: set(system.edges.get(state, ())) for state in system.states}
        h2 = {state: {item for target in h1[state] for item in system.edges.get(target, ())} for state in system.states}
        h4 = {state: {item for target in h2[state] for item in h2.get(target, set())} for state in system.states}
        ratio_12 = {state: len(h2[state]) / max(1, len(h1[state])) for state in system.states}
        ratio_24 = {state: len(h4[state]) / max(1, len(h2[state])) for state in system.states}
        rank_12 = quantile_rank_map(ratio_12, 4)
        rank_24 = quantile_rank_map(ratio_24, 4)

        def horizon_growth_contrast_v2(s: State, rank_12=rank_12, rank_24=rank_24, h1=h1, h2=h2) -> tuple[int, int, int]:
            dead_or_floor = int(len(h1[s]) == 0 or len(h2[s]) <= 1)
            return (rank_12[s], rank_24[s], dead_or_floor)

        return Probe("horizon_growth_contrast_v2", "frontier_dynamics", horizon_growth_contrast_v2, "horizon_growth_contrast_v2", 3), 32, "frontier_dynamics"

    if probe_key == "wiring_role_class_v2":
        out_rank = quantile_rank_map({state: float(len(system.edges.get(state, ()))) for state in system.states}, 4)
        in_rank = quantile_rank_map({state: float(in_degree.get(state, 0)) for state in system.states}, 4)
        reciprocity_rank = quantile_rank_map(
            {
                state: float(sum(int((target, state) in edge_set) for target in system.edges.get(state, ())))
                for state in system.states
            },
            4,
        )

        def wiring_role_class_v2(s: State, out_rank=out_rank, in_rank=in_rank, reciprocity_rank=reciprocity_rank) -> tuple[int, int, int]:
            return (out_rank[s], in_rank[s], reciprocity_rank[s])

        return Probe("wiring_role_class_v2", "wiring_role", wiring_role_class_v2, "wiring_role_class_v2", 3), 64, "wiring_role"

    if probe_key == "self_recurrence_horizon_v2":
        h1 = {state: set(system.edges.get(state, ())) for state in system.states}
        h2 = {state: {item for target in h1[state] for item in h1.get(target, set())} for state in system.states}
        h4 = {state: {item for target in h2[state] for item in h2.get(target, set())} for state in system.states}
        h8 = {state: {item for target in h4[state] for item in h4.get(target, set())} for state in system.states}
        return_counts = {
            state: int(state in h1[state]) + int(state in h2[state]) + int(state in h4[state]) + int(state in h8[state])
            for state in system.states
        }
        return_rank = quantile_rank_map({state: float(count) for state, count in return_counts.items()}, 4)

        def self_recurrence_horizon_v2(s: State, h1=h1, h2=h2, h4=h4, h8=h8, return_rank=return_rank) -> tuple[int, int]:
            if s in h1[s]:
                earliest = 1
            elif s in h2[s]:
                earliest = 2
            elif s in h4[s]:
                earliest = 3
            elif s in h8[s]:
                earliest = 4
            else:
                earliest = 0
            return (earliest, return_rank[s])

        return Probe("self_recurrence_horizon_v2", "cycle_structure", self_recurrence_horizon_v2, "self_recurrence_horizon_v2", 2), 20, "cycle_structure"

    if probe_key == "full_state_hash":
        buckets = max(32, min(2048, len(system.states) * 2))
        return Probe("full_state_hash", "strict_state_control", lambda s, buckets=buckets: (_stable_hash(str(s)) % buckets,), "full_state_hash", 1), buckets, "strict_state_control"

    if probe_key == "full_state_strict":
        return Probe("full_state_strict", "strict_state_control", lambda s: tuple(s), "full_state_strict", coordinate_count), len(system.states), "strict_state_control"

    raise ValueError(f"unknown probe key {probe_key}")


def low_outdegree_diagnostics(system: LandscapeSystem, starts: list[State], horizon: int, sequences: list[tuple[object, ...]]) -> dict[str, object]:
    out_degrees = [len(system.edges.get(state, ())) for state in system.states]
    frontier_sizes = [len(exact_frontier(system, start, horizon)) for start in starts]
    return {
        "effective_branch_factor": mean(out_degrees) if out_degrees else 0.0,
        "sampled_path_count": len(sequences),
        "unique_path_count_proxy": len(set(sequences)),
        "frontier_size_by_H": mean(frontier_sizes) if frontier_sizes else 0.0,
        "low_outdegree_path_fakeout_flag": int((mean(out_degrees) if out_degrees else 0.0) <= 2.0),
        "path_count_matched_control_id": "",
        "path_count_match_quality": "not_separately_matched_mean_outdegree_reported",
    }


def path_metrics(sequences: list[tuple[object, ...]], probe: Probe, state_count: int, alphabet_size: int | None = None) -> dict[str, object]:
    unigrams = Counter(item for sequence in sequences for item in sequence)
    bigrams = Counter((sequence[i], sequence[i + 1]) for sequence in sequences for i in range(len(sequence) - 1))
    trigrams = Counter((sequence[i], sequence[i + 1], sequence[i + 2]) for sequence in sequences for i in range(len(sequence) - 2))
    support = len(unigrams)
    alphabet = max(1, int(alphabet_size or (3 ** max(1, probe.arity))))
    unigram_entropy = entropy(unigrams)
    entropy_ceiling = math.log2(max(1, alphabet))
    effective_signature_count = 2 ** unigram_entropy
    support_fraction = support / alphabet
    collision_rate = max(0.0, 1.0 - support / max(1, state_count))
    return {
        "path_count": len(sequences),
        "probe_signature_alphabet_size": alphabet,
        "observed_signature_support_size": support,
        "observed_signature_support_fraction": support_fraction,
        "probe_collision_rate": collision_rate,
        "effective_signature_count": effective_signature_count,
        "unigram_entropy_ceiling": entropy_ceiling,
        "unigram_entropy": unigram_entropy,
        "entropy_ceiling_fraction": unigram_entropy / max(1e-9, entropy_ceiling),
        "probe_resolution_class": probe_resolution_class(collision_rate, support_fraction, effective_signature_count, state_count, probe.probe_family),
        "bigram_entropy": entropy(bigrams),
        "trigram_entropy": entropy(trigrams),
        "bigram_mutual_information": mutual_information_bigrams(bigrams),
        "trigram_context_mutual_information": trigram_context_mi(trigrams),
        "predictive_gain_bigram_context": trigram_context_mi(trigrams) - mutual_information_bigrams(bigrams),
        "path_motif_reuse_rate": repeated_fraction(bigrams),
        "repeated_bigram_fraction": repeated_fraction(bigrams),
        "repeated_trigram_fraction": repeated_fraction(trigrams),
        "bigram_possible_count": alphabet * alphabet,
        "bigram_observed_count": len(bigrams),
        "bigram_observed_fraction": len(bigrams) / max(1, alphabet * alphabet),
        "trigram_possible_count": alphabet * alphabet * alphabet,
        "trigram_observed_count": len(trigrams),
        "trigram_observed_fraction": len(trigrams) / max(1, alphabet * alphabet * alphabet),
        "ngram_compression_proxy": (len(bigrams) + len(trigrams)) / max(1, sum(bigrams.values()) + sum(trigrams.values())),
    }


def endpoint_support_randomized(sequences: list[tuple[object, ...]], rng: random.Random) -> list[tuple[object, ...]]:
    support = sorted({item for sequence in sequences for item in sequence}, key=str)
    if not support:
        return sequences
    return [tuple(rng.choice(support) for _ in sequence) for sequence in sequences]


def unigram_shuffled(sequences: list[tuple[object, ...]], rng: random.Random) -> list[tuple[object, ...]]:
    out = []
    for sequence in sequences:
        items = list(sequence)
        rng.shuffle(items)
        out.append(tuple(items))
    return out


def fakeout_flags(row: dict[str, object]) -> dict[str, object]:
    probe_collision = float(row["probe_collision_rate"]) > 0.90
    low_alphabet = int(row["probe_signature_alphabet_size"]) <= 3
    support_ceiling = float(row["observed_signature_support_fraction"]) >= 0.90 or float(row["observed_signature_support_fraction"]) <= 0.20
    low_outdegree = bool(int(row.get("low_outdegree_path_fakeout_flag", 0)))
    endpoint_fake = float(row["endpoint_bigram_mi_rank"]) < 0.80
    unigram_fake = float(row["unigram_bigram_mi_rank"]) < 0.80
    fakeouts = []
    if probe_collision:
        fakeouts.append("probe_collision_fakeout")
    if low_alphabet:
        fakeouts.append("low_alphabet_fakeout")
    if support_ceiling:
        fakeouts.append("support_ceiling_fakeout")
    if endpoint_fake:
        fakeouts.append("endpoint_support_fakeout")
    if unigram_fake:
        fakeouts.append("unigram_marginal_fakeout")
    if low_outdegree:
        fakeouts.append("low_outdegree_path_fakeout")
    if not fakeouts:
        fakeouts.append("underdetermined_path_metric")
    return {
        "probe_collision_fakeout_flag": int(probe_collision),
        "low_alphabet_fakeout_flag": int(low_alphabet),
        "support_ceiling_fakeout_flag": int(support_ceiling),
        "endpoint_support_fakeout_flag": int(endpoint_fake),
        "unigram_marginal_fakeout_flag": int(unigram_fake),
        "low_outdegree_path_fakeout_flag": int(low_outdegree),
        "fakeout_class": ";".join(fakeouts),
    }


def evidence_level(row: dict[str, object]) -> str:
    if row["row_kind"] != "candidate":
        return "matched_control"
    if row.get("matched_control_environment_id", "") == "":
        return "probe_resolution_descriptive"
    if row.get("probe_resolution_class") in {"identity_like_control", "overfit_or_identity_like"}:
        return "probe_resolution_identity_like_only"
    if int(row["probe_collision_fakeout_flag"]) or int(row["low_alphabet_fakeout_flag"]):
        return "probe_resolution_fail_collision"
    if int(row["support_ceiling_fakeout_flag"]):
        return "probe_resolution_fail_support_ceiling"
    if int(row["endpoint_support_fakeout_flag"]):
        return "path_descriptive"
    if int(row["unigram_marginal_fakeout_flag"]):
        return "path_above_endpoint"
    if float(row["endpoint_bigram_mi_rank"]) >= 0.80 and float(row["unigram_bigram_mi_rank"]) >= 0.80:
        return "probe_resolution_pass"
    return "underdetermined"


def probe_resolution_class(collision_rate: float, support_fraction: float, effective_signature_count: float, state_count: int, probe_family: str) -> str:
    if probe_family in {"full_state_hash", "full_state_strict"}:
        return "identity_like_control"
    if collision_rate < 0.10 or effective_signature_count >= 0.85 * max(1, state_count):
        return "identity_like_control"
    if collision_rate >= 0.90 or effective_signature_count < 4:
        return "too_coarse"
    if support_fraction >= 0.95:
        return "overfit_or_identity_like"
    if 0.75 <= collision_rate < 0.90:
        return "usable_low_resolution"
    if 0.40 <= collision_rate < 0.75:
        return "usable_medium_resolution"
    if 0.10 <= collision_rate < 0.40:
        return "high_resolution_control"
    return "underdetermined"


def write_outputs(
    out_dir: Path,
    args: argparse.Namespace,
    started: float,
    jobs: list[dict[str, object]],
    results: list[dict[str, object]],
    selection_rows: list[dict[str, object]],
    control_rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    control_metric_by_candidate = {}
    for row in results:
        if row["row_kind"] == "matched_control":
            control_metric_by_candidate.setdefault((row["candidate_environment_id"], row["probe_key"], row["path_horizon"]), row)
    for row in results:
        if row["row_kind"] != "candidate":
            row["matched_control_environment_id"] = ""
            row["matched_control_match_quality"] = ""
            continue
        control = control_metric_by_candidate.get((row["candidate_environment_id"], row["probe_key"], row["path_horizon"]), {})
        row["matched_control_environment_id"] = control.get("environment_id", "")
        row["matched_control_match_quality"] = "available" if control else "none"
        row["candidate_metric"] = row["bigram_mutual_information"]
        row["matched_control_metric"] = control.get("bigram_mutual_information", "")
        if control:
            delta = float(row["bigram_mutual_information"]) - float(control["bigram_mutual_information"])
            row["candidate_minus_control"] = delta
            row["candidate_control_effect_size"] = delta / max(1e-9, abs(float(control["bigram_mutual_information"])))
            row["candidate_control_rank"] = int(float(row["bigram_mutual_information"]) >= float(control["bigram_mutual_information"]))
            if row["candidate_control_rank"] == 0:
                row["fakeout_class"] = str(row["fakeout_class"]) + ";matched_control_also_passes"
        else:
            row["candidate_minus_control"] = ""
            row["candidate_control_effect_size"] = ""
            row["candidate_control_rank"] = ""
            row["path_evidence_level"] = "probe_resolution_descriptive"
            row["fakeout_class"] = str(row["fakeout_class"]) + ";descriptive_only_no_matched_control"
        if control and row.get("path_evidence_level") == "probe_resolution_descriptive":
            row["path_evidence_level"] = evidence_level(row)
        if control and row.get("candidate_control_rank") == 0 and row.get("path_evidence_level") == "probe_resolution_pass":
            row["path_evidence_level"] = "probe_resolution_pass_but_control_also_passes"
        row["would_promote_if_enabled"] = int(row["path_evidence_level"] == "probe_resolution_pass")
        row["promotion_blocked_by_probe_resolution_policy"] = row["would_promote_if_enabled"]
    _write_csv(out_dir / "path_metric_calibration_summary.csv", results)
    _write_csv(out_dir / "path_metric_by_probe_family.csv", results)
    _write_csv(out_dir / "probe_collision_diagnostics.csv", probe_collision_rows(results))
    _write_csv(out_dir / "matched_non_candidate_path_controls.csv", control_rows)
    _write_csv(out_dir / "path_null_rank_summary.csv", null_rank_rows(results))
    _write_csv(out_dir / "path_metric_effect_sizes.csv", effect_size_rows(results))
    _write_csv(out_dir / "path_fakeout_summary.csv", fakeout_summary(results))
    _write_csv(out_dir / "probe_fakeout_summary.csv", fakeout_summary(results))
    _write_csv(out_dir / "probe_resolution_by_family.csv", probe_resolution_by_family(results))
    _write_csv(out_dir / "candidate_control_probe_matrix.csv", candidate_control_probe_matrix(results))
    _write_csv(out_dir / "probe_resolution_curves.csv", probe_resolution_curves(results))
    _write_csv(out_dir / "low_outdegree_path_count_controls.csv", low_outdegree_rows(results))
    _write_csv(out_dir / "strict_state_control_summary.csv", group_summary([row for row in results if row.get("probe_group") == "strict_state_control"], "probe_family"))
    _write_csv(out_dir / "constraint_profile_probe_summary.csv", group_summary([row for row in results if row.get("probe_group") == "constraint_profile"], "probe_family"))
    _write_csv(out_dir / "relation_role_probe_summary.csv", group_summary([row for row in results if row.get("probe_group") == "relation_role"], "probe_family"))
    _write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, args, started, jobs, results, errors)
    status = {
        "status": "COMPLETED",
        "wall_clock_seconds": time.perf_counter() - started,
        "jobs_requested": len(jobs),
        "jobs_completed": len(results),
        "errors": len(errors),
        "promotion_enabled": False,
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


def write_report(out_dir: Path, args: argparse.Namespace, started: float, jobs: list[dict[str, object]], results: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    fakeouts = fakeout_summary(results)
    levels = _counts(row.get("path_evidence_level", "") for row in results if row.get("row_kind") == "candidate")
    family_rows = probe_resolution_by_family(results)
    usable_medium = [row for row in results if row.get("probe_resolution_class") == "usable_medium_resolution"]
    non_identity_passes = [
        row for row in results
        if row.get("row_kind") == "candidate"
        and row.get("path_evidence_level") == "probe_resolution_pass"
        and row.get("probe_resolution_class") not in {"identity_like_control", "overfit_or_identity_like"}
    ]
    identity_only = not non_identity_passes and any(row.get("probe_resolution_class") == "identity_like_control" for row in results)
    medium_candidate_rows = [
        row for row in results
        if row.get("row_kind") == "candidate"
        and row.get("probe_resolution_class") == "usable_medium_resolution"
    ]
    medium_positive = [row for row in medium_candidate_rows if row.get("candidate_control_rank") == 1 and row.get("path_evidence_level") == "probe_resolution_pass"]
    medium_control_also = [row for row in medium_candidate_rows if row.get("path_evidence_level") == "probe_resolution_pass_but_control_also_passes"]
    fakeout_total = sum(int(row["n_rows"]) for row in fakeouts if row["fakeout_class"] != "underdetermined_path_metric")
    fakeout_dominant = fakeout_total > max(1, len(results) // 2)
    decision = (
        "A"
        if usable_medium and non_identity_passes and len(medium_positive) > len(medium_control_also) and not fakeout_dominant
        else ("C" if identity_only and not usable_medium else "B")
    )
    recommendation = {
        "A": "Continue path calibration v2 with the medium-resolution probes that separated from controls.",
        "B": "Downgrade path-process for now and focus on support/distribution deformation taxonomy.",
        "C": "Pause this empirical path-process branch and write a measurement-limits note.",
    }[decision]
    lines = [
        "# RFS-MB0 Probe Resolution Calibration Report",
        "",
        "Promotion disabled: this is a probe-resolution calibration smoke, not a path-process detection run.",
        "",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {args.workers}",
        f"- Jobs queued: {len(jobs)}",
        f"- Jobs completed: {len(results)}",
        f"- Errors: {len(errors)}",
        f"- Branch recommendation: {decision}. {recommendation}",
        "",
        "## Probe Family Resolution",
        "",
        "| probe_family | n | mean_collision | mean_support_fraction | mean_effect_size | dominant_resolution_class |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in family_rows:
        lines.append(
            f"| {row['probe_family']} | {row['n_rows']} | {float(row['mean_probe_collision_rate']):.3f} | "
            f"{float(row['mean_observed_signature_support_fraction']):.3f} | {row['mean_candidate_control_effect_size']} | {row['dominant_probe_resolution_class']} |"
        )
    lines.extend(
        [
            "",
            "## Fakeout Counts",
            "",
            "| fakeout | n |",
            "|---|---:|",
        ]
    )
    for row in fakeouts:
        lines.append(f"| {row['fakeout_class']} | {row['n_rows']} |")
    lines.extend(["", "## Candidate Evidence Levels", "", "| level | n |", "|---|---:|"])
    for level, count in sorted(levels.items()):
        lines.append(f"| {level} | {count} |")
    candidate_rows = [row for row in results if row.get("row_kind") == "candidate"]
    matched = [row for row in candidate_rows if row.get("matched_control_environment_id")]
    too_collision = sorted({str(row.get("probe_family")) for row in results if row.get("probe_resolution_class") == "too_coarse"})
    identity_controls = sorted({str(row.get("probe_family")) for row in results if row.get("probe_resolution_class") == "identity_like_control"})
    medium = sorted({str(row.get("probe_family")) for row in usable_medium})
    lines.extend(
        [
            "",
            "## Required Answers",
            "",
            f"- Too collision-prone families: {', '.join(too_collision) if too_collision else 'none observed'}",
            f"- Identity-like controls: {', '.join(identity_controls) if identity_controls else 'none observed'}",
            f"- Usable medium-resolution probes: {', '.join(medium) if medium else 'none observed'}",
            f"- Candidate rows: {len(candidate_rows)}",
            f"- Candidate rows with matched controls: {len(matched)}",
            f"- Path-count caveat: low-outdegree/path-count diagnostics are written to low_outdegree_path_count_controls.csv.",
            f"- Recommended branch: {decision}. {recommendation}",
            "",
            "## Claim Boundary",
            "",
            "This smoke calibrates probe resolution and path metrics against fakeout controls. It does not promote path-process candidates or claim Omega validation.",
        ]
    )
    text = "\n".join(lines) + "\n"
    (out_dir / "probe_resolution_calibration_report.md").write_text(text, encoding="utf-8")
    (out_dir / "path_metric_calibration_report.md").write_text(text, encoding="utf-8")


def probe_resolution_by_family(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for family in sorted({str(row.get("probe_family", "")) for row in rows}):
        group = [row for row in rows if str(row.get("probe_family", "")) == family]
        effects = [_float(row.get("candidate_control_effect_size")) for row in group if _float(row.get("candidate_control_effect_size")) is not None]
        classes = _counts(row.get("probe_resolution_class", "") for row in group)
        dominant = max(classes.items(), key=lambda item: item[1])[0] if classes else ""
        out.append(
            {
                "probe_family": family,
                "probe_group": next((row.get("probe_group", "") for row in group), ""),
                "n_rows": len(group),
                "mean_probe_collision_rate": _mean_float(row.get("probe_collision_rate") for row in group),
                "mean_observed_signature_support_fraction": _mean_float(row.get("observed_signature_support_fraction") for row in group),
                "mean_effective_signature_count": _mean_float(row.get("effective_signature_count") for row in group),
                "mean_entropy_ceiling_fraction": _mean_float(row.get("entropy_ceiling_fraction") for row in group),
                "mean_candidate_control_effect_size": mean(effects) if effects else "",
                "dominant_probe_resolution_class": dominant,
                "probe_resolution_class_counts": json.dumps(classes, sort_keys=True),
            }
        )
    return out


def candidate_control_probe_matrix(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = (
        "candidate_environment_id",
        "environment_id",
        "probe_family",
        "probe_group",
        "path_horizon",
        "probe_resolution_class",
        "candidate_metric",
        "matched_control_metric",
        "candidate_minus_control",
        "candidate_control_effect_size",
        "candidate_control_rank",
        "endpoint_bigram_mi_rank",
        "unigram_bigram_mi_rank",
        "fakeout_class",
        "path_evidence_level",
    )
    return [{key: row.get(key, "") for key in keys} for row in rows if row.get("row_kind") == "candidate"]


def probe_resolution_curves(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = (
        "candidate_environment_id",
        "probe_key",
        "probe_family",
        "probe_group",
        "path_horizon",
        "probe_collision_rate",
        "observed_signature_support_fraction",
        "candidate_minus_control",
        "candidate_control_effect_size",
        "endpoint_bigram_mi_rank",
        "unigram_bigram_mi_rank",
        "fakeout_class",
        "path_evidence_level",
    )
    return [{key: row.get(key, "") for key in keys} for row in rows if row.get("row_kind") == "candidate"]


def low_outdegree_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = (
        "job_id",
        "row_kind",
        "environment_id",
        "probe_family",
        "path_horizon",
        "effective_branch_factor",
        "sampled_path_count",
        "unique_path_count_proxy",
        "frontier_size_by_H",
        "low_outdegree_path_fakeout_flag",
        "path_count_matched_control_id",
        "path_count_match_quality",
    )
    return [{key: row.get(key, "") for key in keys} for row in rows]


def group_summary(rows: list[dict[str, object]], group_key: str) -> list[dict[str, object]]:
    out = []
    for value in sorted({str(row.get(group_key, "")) for row in rows}):
        group = [row for row in rows if str(row.get(group_key, "")) == value]
        out.append(
            {
                group_key: value,
                "n_rows": len(group),
                "mean_probe_collision_rate": _mean_float(row.get("probe_collision_rate") for row in group),
                "mean_observed_signature_support_fraction": _mean_float(row.get("observed_signature_support_fraction") for row in group),
                "mean_bigram_mutual_information": _mean_float(row.get("bigram_mutual_information") for row in group),
                "resolution_class_counts": json.dumps(_counts(row.get("probe_resolution_class", "") for row in group), sort_keys=True),
            }
        )
    return out


def _float(value: object) -> float | None:
    try:
        if value == "":
            return None
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _mean_float(values: object) -> float | str:
    numbers = [_float(value) for value in values]  # type: ignore[union-attr]
    clean = [value for value in numbers if value is not None]
    return mean(clean) if clean else ""


def probe_collision_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = (
        "job_id",
        "row_kind",
        "environment_id",
        "probe_family",
        "path_horizon",
        "probe_signature_alphabet_size",
        "observed_signature_support_size",
        "observed_signature_support_fraction",
        "probe_collision_rate",
        "unigram_entropy_ceiling",
        "bigram_possible_count",
        "bigram_observed_count",
        "bigram_observed_fraction",
        "trigram_possible_count",
        "trigram_observed_count",
        "trigram_observed_fraction",
        "probe_collision_fakeout_flag",
        "low_alphabet_fakeout_flag",
        "support_ceiling_fakeout_flag",
    )
    return [{key: row.get(key, "") for key in keys} for row in rows]


def null_rank_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "job_id": row["job_id"],
            "row_kind": row["row_kind"],
            "environment_id": row["environment_id"],
            "probe_family": row["probe_family"],
            "path_horizon": row["path_horizon"],
            "endpoint_bigram_mi_rank": row["endpoint_bigram_mi_rank"],
            "endpoint_trigram_gain_rank": row["endpoint_trigram_gain_rank"],
            "unigram_bigram_mi_rank": row["unigram_bigram_mi_rank"],
            "unigram_trigram_gain_rank": row["unigram_trigram_gain_rank"],
            "path_null_replicates": row["path_null_replicates"],
        }
        for row in rows
    ]


def effect_size_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "job_id": row["job_id"],
            "environment_id": row["environment_id"],
            "matched_control_environment_id": row.get("matched_control_environment_id", ""),
            "candidate_metric": row.get("candidate_metric", ""),
            "matched_control_metric": row.get("matched_control_metric", ""),
            "candidate_minus_control": row.get("candidate_minus_control", ""),
            "candidate_control_effect_size": row.get("candidate_control_effect_size", ""),
            "candidate_control_rank": row.get("candidate_control_rank", ""),
        }
        for row in rows
        if row.get("row_kind") == "candidate"
    ]


def fakeout_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter()
    for row in rows:
        for klass in str(row.get("fakeout_class", "underdetermined_path_metric")).split(";"):
            if klass:
                counts[klass] += 1
    return [{"fakeout_class": klass, "n_rows": count} for klass, count in sorted(counts.items())]


def entropy(counts: Counter[object]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counts.values() if count)


def mutual_information_bigrams(bigrams: Counter[tuple[object, object]]) -> float:
    total = sum(bigrams.values())
    if total <= 0:
        return 0.0
    left = Counter()
    right = Counter()
    for (a, b), count in bigrams.items():
        left[a] += count
        right[b] += count
    mi = 0.0
    for (a, b), count in bigrams.items():
        p = count / total
        pa = left[a] / total
        pb = right[b] / total
        mi += p * math.log2(p / max(1e-12, pa * pb))
    return mi


def trigram_context_mi(trigrams: Counter[tuple[object, object, object]]) -> float:
    total = sum(trigrams.values())
    if total <= 0:
        return 0.0
    context = Counter()
    nxt = Counter()
    for (a, b, c), count in trigrams.items():
        context[(a, b)] += count
        nxt[c] += count
    mi = 0.0
    for (a, b, c), count in trigrams.items():
        p = count / total
        pc = context[(a, b)] / total
        pn = nxt[c] / total
        mi += p * math.log2(p / max(1e-12, pc * pn))
    return mi


def repeated_fraction(counts: Counter[object]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return sum(count for count in counts.values() if count > 1) / total


def rank_metric(observed: float, null_values: list[float]) -> float:
    if not null_values:
        return 0.0
    return sum(observed >= value for value in null_values) / len(null_values)


def params_from_metadata(metadata: dict[str, object]) -> RelationParams:
    return RelationParams(
        parameter_set_id=str(metadata["parameter_set_id"]),
        coordinate_count=int(metadata["coordinate_count"]),
        alphabet_size=int(metadata["alphabet_size"]),
        neighborhood_radius=int(metadata["neighborhood_radius"]),
        update_footprint=int(metadata["update_footprint"]),
        out_degree_target=int(metadata["out_degree_target"]),
        constraint_density=float(metadata["constraint_density"]),
        constraint_strength=float(metadata["constraint_strength"]),
        asymmetry_strength=float(metadata["asymmetry_strength"]),
        reversibility_fraction=float(metadata["reversibility_fraction"]),
        rewire_probability=float(metadata["rewire_probability"]),
        roughness_strength=float(metadata.get("roughness_strength", 0.01)),
        constraint_arity=int(metadata.get("constraint_arity", 2)),
        constraint_change_weight=float(metadata.get("constraint_change_weight", 0.35)),
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _counts(values: object) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:  # type: ignore[union-attr]
        out[str(value)] = out.get(str(value), 0) + 1
    return out


if __name__ == "__main__":
    main()
