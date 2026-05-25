from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from collections import Counter
from pathlib import Path

from .landscape import exact_frontier, future_profile, signature_distribution, transition_information_summary
from .probes import generate_probes
from .relation_generator import (
    RelationParams,
    environment_shape,
    generate_relation_system,
    generated_null_systems,
    sample_parameter_sets,
)
from .run_smoke import (
    HORIZON_GRIDS,
    _aggregate_family_classes,
    _aggregate_probe_family_classes,
    _horizon_local_nulls,
    _horizon_window_summary,
    _matched_null_summary,
    _saturation_onset_by_family,
    _viscosity_diagnostics,
    _write_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 action-generated relation atlas.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--parameter-samples", type=int, default=20)
    parser.add_argument("--seeds-per-parameter-set", type=int, default=1)
    parser.add_argument("--parameter-seed", type=int, default=20260523)
    parser.add_argument("--coordinate-counts", type=str, default="5,6")
    parser.add_argument("--max-state-count", type=int, default=1000)
    parser.add_argument("--parameter-region-file", type=Path, default=None)
    parser.add_argument("--parameter-region-mode", choices=("any", "core_only", "all"), default="any")
    parser.add_argument("--sigma", type=int, default=2)
    parser.add_argument("--start-samples", type=int, default=3)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
    parser.add_argument("--checkpoint-every", type=int, default=4)
    parser.add_argument("--horizon-grid", choices=sorted(HORIZON_GRIDS), default="long_5x")
    parser.add_argument("--horizons", type=str, default="")
    parser.add_argument("--null-replicates", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    horizons = _resolve_horizons(args)
    jobs, selection = _jobs(args)
    if not jobs:
        config = {
            "parameter_samples": args.parameter_samples,
            "seeds_per_parameter_set": args.seeds_per_parameter_set,
            "parameter_seed": args.parameter_seed,
            "sigma": args.sigma,
            "start_samples": args.start_samples,
            "workers": args.workers,
            "max_runtime_seconds": args.max_runtime_seconds,
            "checkpoint_every": args.checkpoint_every,
            "horizon_grid": args.horizon_grid,
            "resolved_horizons": list(horizons),
            "null_replicates": args.null_replicates,
            "job_count": 0,
            **selection,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "started_perf_counter": started,
            "status": "NO_JOBS",
        }
        (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
        _write_outputs(out_dir, config, [], [], [], [], [], [], [{"job": "parameter_selection", "error": "no jobs matched filters"}])
        return
    config = {
        "parameter_samples": args.parameter_samples,
        "seeds_per_parameter_set": args.seeds_per_parameter_set,
        "parameter_seed": args.parameter_seed,
        "sigma": args.sigma,
        "start_samples": args.start_samples,
        "workers": args.workers,
        "max_runtime_seconds": args.max_runtime_seconds,
        "checkpoint_every": args.checkpoint_every,
        "horizon_grid": args.horizon_grid,
        "resolved_horizons": list(horizons),
        "null_replicates": args.null_replicates,
        "job_count": len(jobs),
        **selection,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "started_perf_counter": started,
        "status": "RUNNING",
    }
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    systems: list[dict[str, object]] = []
    shapes: list[dict[str, object]] = []
    profiles: list[dict[str, object]] = []
    profile_rows: list[dict[str, object]] = []
    transition_rows: list[dict[str, object]] = []
    distributions: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending_jobs = list(jobs)
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    futures = {}
    timed_out = False
    try:
        while pending_jobs or futures:
            while pending_jobs and len(futures) < max(1, args.workers):
                job = pending_jobs.pop(0)
                futures[executor.submit(_run_one, job)] = job
            remaining = args.max_runtime_seconds - (time.perf_counter() - started)
            if remaining <= 0:
                config["status"] = "TIME_LIMIT_REACHED"
                timed_out = True
                break
            done, _pending = wait(futures, timeout=max(0.1, min(2.0, remaining)), return_when=FIRST_COMPLETED)
            for future in done:
                job = futures.pop(future)
                try:
                    result = future.result()
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job": json.dumps(_jsonable_job(job), sort_keys=True), "error": repr(exc)})
                    continue
                systems.append(result["system"])
                shapes.append(result["environment_shape"])
                profiles.extend(result["profiles"])
                profile_rows.extend(result["profile_rows"])
                transition_rows.extend(result["transition_rows"])
                distributions.extend(result["distributions"])
            if len(systems) and len(systems) % max(1, args.checkpoint_every) == 0:
                _write_outputs(out_dir, config, systems, shapes, profiles, profile_rows, transition_rows, distributions, errors)
    finally:
        if timed_out:
            for future in futures:
                future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    if config["status"] == "RUNNING":
        config["status"] = "COMPLETED"
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    _write_outputs(out_dir, config, systems, shapes, profiles, profile_rows, transition_rows, distributions, errors)


def _jobs(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    coordinate_counts = {int(item.strip()) for item in args.coordinate_counts.split(",") if item.strip()}
    regions = _load_parameter_regions(args.parameter_region_file)
    raw_parameter_sets = sample_parameter_sets(max(args.parameter_samples * 20, 500), args.parameter_seed)
    parameter_sets = [
        params
        for params in raw_parameter_sets
        if params.coordinate_count in coordinate_counts
        and params.alphabet_size ** params.coordinate_count <= args.max_state_count
        and _matches_regions(params, regions, args.parameter_region_mode)
    ][: args.parameter_samples]
    horizons = _resolve_horizons(args)
    jobs = []
    for params in parameter_sets:
        base_seed = _seed_for_params(params, args.parameter_seed)
        for seed_index in range(args.seeds_per_parameter_set):
            jobs.append(
                {
                    "params": params,
                    "seed": base_seed + seed_index,
                    "sigma": args.sigma,
                    "start_samples": args.start_samples,
                    "null_replicates": args.null_replicates,
                    "horizons": horizons,
                }
            )
    selection = {
        "parameter_region_mode": args.parameter_region_mode,
        "raw_parameter_candidates": len(raw_parameter_sets),
        "filtered_parameter_sets": len(parameter_sets),
        "jobs_created": len(jobs),
        "requested_parameter_samples": args.parameter_samples,
    }
    return jobs, selection


def _load_parameter_regions(path: Path | None) -> list[dict[str, object]]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        regions = payload.get("regions", [])
    else:
        regions = payload
    if not isinstance(regions, list):
        raise ValueError("parameter region file must contain a list or {'regions': [...]}")
    return [region for region in regions if isinstance(region, dict)]


def _matches_regions(params: RelationParams, regions: list[dict[str, object]], mode: str = "any") -> bool:
    if not regions:
        return True
    if mode == "core_only":
        regions = [region for region in regions if region.get("core") is True or region.get("name") == "shape_selected_core" or str(region.get("name", "")).startswith("shape_selected_core_")]
        if not regions:
            return False
    if mode == "all":
        constraints: dict[str, set[object]] = {}
        for region in regions:
            for key, allowed in region.items():
                if key in {"name", "source", "score", "n_environments", "middle_regime_rate", "core"}:
                    continue
                constraints.setdefault(key, set()).update(allowed if isinstance(allowed, list) else [allowed])
        values = params.__dict__
        return all(values.get(key) in allowed for key, allowed in constraints.items())
    values = params.__dict__
    for region in regions:
        matched = True
        for key, allowed in region.items():
            if key in {"name", "source", "score", "n_environments", "middle_regime_rate", "core"}:
                continue
            value = values.get(key)
            if isinstance(allowed, list):
                if value not in allowed:
                    matched = False
                    break
            elif value != allowed:
                matched = False
                break
        if matched:
            return True
    return False


def _resolve_horizons(args: argparse.Namespace) -> tuple[int, ...]:
    if args.horizons.strip():
        values = tuple(sorted({int(item.strip()) for item in args.horizons.split(",") if item.strip()}))
    else:
        values = HORIZON_GRIDS[args.horizon_grid]
    if not values or values[0] != 0:
        raise ValueError("horizon grid must include 0")
    return values


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    params = job["params"]
    if not isinstance(params, RelationParams):
        raise TypeError("job params must be RelationParams")
    seed = int(job["seed"])
    horizons = tuple(int(value) for value in job["horizons"])
    system = generate_relation_system(params, seed)
    null_systems = generated_null_systems(params, seed)
    probes = generate_probes(system, int(job["sigma"]))
    starts = [system.states[(seed + i * 17) % len(system.states)] for i in range(int(job["start_samples"]))]
    profiles = []
    profile_rows = []
    transition_rows = []
    distributions = []
    for probe in probes:
        for start in starts:
            null_bundle_by_h = _generated_null_bundle(system, null_systems, probe, start, horizons)
            null_transitions = _generated_null_transitions(null_systems, probe, start, horizons)
            replicate_bundle_by_h, replicate_transitions = _generated_null_replicates(params, seed, system, probe, start, horizons, int(job.get("null_replicates", 0)))
            profile, rows, dist_rows = future_profile(
                system,
                start,
                probe,
                null_bundle_by_h.get("degree_preserving_rewire", {}),
                null_bundle_by_h,
                null_transitions,
                replicate_bundle_by_h,
                replicate_transitions,
                horizons,
            )
            profile["parameter_set_id"] = params.parameter_set_id
            profile["environment_id"] = system.system_id
            profiles.append(profile)
            for row in rows:
                row["parameter_set_id"] = params.parameter_set_id
                row["environment_id"] = system.system_id
                if row.get("row_kind") == "transition_information":
                    transition_rows.append(row)
                else:
                    profile_rows.append(row)
            for row in dist_rows:
                row["parameter_set_id"] = params.parameter_set_id
                row["environment_id"] = system.system_id
            distributions.extend(dist_rows)
    shape = environment_shape(system, horizons)
    system_row = {
        "environment_id": system.system_id,
        "system_id": system.system_id,
        "seed": seed,
        "family": system.family,
        "parameter_set_id": params.parameter_set_id,
        "n_states": len(system.states),
        "n_edges": sum(len(targets) for targets in system.edges.values()),
        "probe_count": len(probes),
        "sigma": int(job["sigma"]),
        "start_count": len(starts),
        "null_replicates": int(job.get("null_replicates", 0)),
        "horizons_json": json.dumps(horizons),
        "metadata_json": json.dumps(system.metadata, sort_keys=True),
        "job_elapsed_seconds": time.perf_counter() - started,
    }
    return {
        "system": system_row,
        "environment_shape": shape,
        "profiles": profiles,
        "profile_rows": profile_rows,
        "transition_rows": transition_rows,
        "distributions": distributions,
    }


def _generated_null_bundle(system: object, null_systems: dict[str, object], probe: object, start: tuple[int, ...], horizons: tuple[int, ...]) -> dict[str, dict[int, dict[object, int]]]:
    out = {}
    for null_name, null_system in null_systems.items():
        out[null_name] = {
            h: signature_distribution(exact_frontier(null_system, start, h), probe)  # type: ignore[arg-type]
            for h in horizons
        }
    out.update(_frontier_probe_diagnostic_nulls(system, probe, start, horizons))  # type: ignore[arg-type]
    return out


def _generated_null_transitions(null_systems: dict[str, object], probe: object, start: tuple[int, ...], horizons: tuple[int, ...]) -> dict[str, dict[str, float]]:
    out = {}
    for null_name, null_system in null_systems.items():
        summary, _rows = transition_information_summary(null_system, start, probe, horizons)  # type: ignore[arg-type]
        out[null_name] = summary
    for null_name in (
        "frontier_size_only",
        "probe_marginal_only",
        "frontier_size_plus_probe_marginal",
        "signature_support_matched",
        "horizon_local_frontier_matched",
        "window_local_frontier_matched",
    ):
        out[null_name] = {
            "signature_transition_MI_mean": 0.0,
            "signature_transition_conditional_entropy_mean": 0.0,
            "signature_transition_entropy_rate_proxy": 0.0,
            "signature_transition_grammar_size_mean": 0.0,
            "signature_transition_motif_reuse_mean": 0.0,
        }
    return out


def _generated_null_replicates(
    params: RelationParams,
    seed: int,
    system: object,
    probe: object,
    start: tuple[int, ...],
    horizons: tuple[int, ...],
    replicate_count: int,
) -> tuple[dict[str, list[dict[int, dict[object, int]]]], dict[str, list[dict[str, float]]]]:
    if replicate_count <= 0:
        return {}, {}
    bundle: dict[str, list[dict[int, dict[object, int]]]] = {}
    transitions: dict[str, list[dict[str, float]]] = {}
    for replicate_index in range(replicate_count):
        replicate_seed = seed + 1_000_003 + replicate_index * 10_007
        replicate_nulls = generated_null_systems(params, replicate_seed)
        for null_name, null_system in replicate_nulls.items():
            by_h = {
                h: signature_distribution(exact_frontier(null_system, start, h), probe)  # type: ignore[arg-type]
                for h in horizons
            }
            bundle.setdefault(null_name, []).append(by_h)
            summary, _rows = transition_information_summary(null_system, start, probe, horizons)  # type: ignore[arg-type]
            transitions.setdefault(null_name, []).append(summary)
        diagnostic_replicates = _frontier_probe_diagnostic_nulls(system, probe, start, horizons, replicate_seed=replicate_seed)  # type: ignore[arg-type]
        for null_name, by_h in diagnostic_replicates.items():
            bundle.setdefault(null_name, []).append(by_h)
            transitions.setdefault(null_name, []).append(
                {
                    "signature_transition_MI_mean": 0.0,
                    "signature_transition_conditional_entropy_mean": 0.0,
                    "signature_transition_entropy_rate_proxy": 0.0,
                    "signature_transition_grammar_size_mean": 0.0,
                    "signature_transition_motif_reuse_mean": 0.0,
                }
            )
    return bundle, transitions


def _frontier_probe_diagnostic_nulls(system: object, probe: object, start: tuple[int, ...], horizons: tuple[int, ...], replicate_seed: int | None = None) -> dict[str, dict[int, dict[object, int]]]:
    import random

    rng = random.Random(replicate_seed) if replicate_seed is not None else None
    states = list(system.states)  # type: ignore[attr-defined]
    full_counts = Counter(probe.fn(state) for state in states)  # type: ignore[attr-defined]
    signatures = sorted(full_counts, key=str)
    out = {
        "frontier_size_only": {},
        "probe_marginal_only": {},
        "frontier_size_plus_probe_marginal": {},
        "signature_support_matched": {},
        "horizon_local_frontier_matched": {},
        "window_local_frontier_matched": {},
    }
    for h in horizons:
        observed = signature_distribution(exact_frontier(system, start, h), probe)  # type: ignore[arg-type]
        frontier_size = max(1, sum(observed.values()))
        support = sorted(observed, key=str) or signatures[:1]
        out["frontier_size_only"][h] = _uniform_counts(signatures, frontier_size, rng)
        out["probe_marginal_only"][h] = dict(full_counts)
        out["frontier_size_plus_probe_marginal"][h] = _scaled_counts(full_counts, frontier_size, rng)
        out["signature_support_matched"][h] = _uniform_counts(support, frontier_size, rng)
        out["horizon_local_frontier_matched"][h] = _scaled_counts(full_counts, frontier_size, rng)
        out["window_local_frontier_matched"][h] = _scaled_counts(full_counts, frontier_size, rng)
    return out


def _uniform_counts(signatures: list[object], total: int, rng: object | None = None) -> dict[object, int]:
    if not signatures or total <= 0:
        return {}
    counts = {signature: total // len(signatures) for signature in signatures}
    remaining = total - sum(counts.values())
    if rng is not None:
        for _ in range(remaining):
            counts[rng.choice(signatures)] += 1  # type: ignore[attr-defined]
    else:
        for index in range(remaining):
            counts[signatures[index % len(signatures)]] += 1
    return {signature: count for signature, count in counts.items() if count > 0}


def _scaled_counts(counts: Counter[object], total: int, rng: object | None = None) -> dict[object, int]:
    source_total = sum(counts.values())
    if source_total <= 0 or total <= 0:
        return {}
    signatures = sorted(counts, key=str)
    scaled = {signature: max(0, round(total * counts[signature] / source_total)) for signature in signatures}
    drift = total - sum(scaled.values())
    index = 0
    while drift != 0 and signatures:
        signature = rng.choice(signatures) if rng is not None else signatures[index % len(signatures)]  # type: ignore[attr-defined]
        if drift > 0:
            scaled[signature] += 1
            drift -= 1
        elif scaled[signature] > 0:
            scaled[signature] -= 1
            drift += 1
        index += 1
    return {signature: count for signature, count in scaled.items() if count > 0}


def _write_outputs(
    out_dir: Path,
    config: dict[str, object],
    systems: list[dict[str, object]],
    shapes: list[dict[str, object]],
    profiles: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    transition_rows: list[dict[str, object]],
    distributions: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    aggregate_probe = _aggregate_probe_family_classes(profiles)
    aggregate_family = _aggregate_family_classes(profiles, aggregate_probe)
    matched_nulls = _matched_null_summary(profiles)
    horizon_nulls = _horizon_local_nulls(profile_rows)
    window_summary = _horizon_window_summary(profile_rows, transition_rows)
    saturation_onset = _saturation_onset_by_family(profile_rows)
    viscosity = _viscosity_diagnostics(profile_rows, transition_rows)
    detector_summary = _relation_atlas_detector_summary(aggregate_family, shapes)
    shape_classes = _shape_class_counts(shapes)
    middle = [row for row in shapes if row["environment_shape_class"] == "middle_regime_environment"]
    _write_csv(out_dir / "generated_environment_metadata.csv", systems)
    _write_csv(out_dir / "environment_shape_summary.csv", shapes)
    _write_csv(out_dir / "environment_shape_classes.csv", shape_classes)
    _write_csv(out_dir / "relation_parameter_sweep.csv", _parameter_rows(systems))
    _write_csv(out_dir / "relation_atlas_detector_summary.csv", detector_summary)
    _write_csv(out_dir / "relation_atlas_probe_family_summary.csv", aggregate_probe)
    _write_csv(out_dir / "relation_atlas_null_summary.csv", matched_nulls)
    _write_csv(out_dir / "relation_atlas_window_summary.csv", window_summary)
    _write_csv(out_dir / "horizon_local_profiles.csv", profile_rows)
    _write_csv(out_dir / "horizon_local_nulls.csv", horizon_nulls)
    _write_csv(out_dir / "transition_information.csv", transition_rows)
    _write_csv(out_dir / "signature_distributions.csv", distributions)
    _write_csv(out_dir / "saturation_onset_by_family.csv", saturation_onset)
    _write_csv(out_dir / "viscosity_diagnostics.csv", viscosity)
    _write_csv(out_dir / "errors.csv", errors)
    status = {
        "status": config.get("status", "RUNNING"),
        "generated_environments_completed": len(systems),
        "middle_regime_environments": len(middle),
        "profiles_completed": len(profiles),
        "errors": len(errors),
        "atlas_gate_pass_count": sum(1 for row in detector_summary if row["atlas_gate_class"] == "structured_propagation"),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
        "parameter_region_mode": config.get("parameter_region_mode", "any"),
        "raw_parameter_candidates": config.get("raw_parameter_candidates", 0),
        "filtered_parameter_sets": config.get("filtered_parameter_sets", 0),
        "jobs_created": config.get("jobs_created", 0),
        "jobs_completed": len(systems),
        "requested_parameter_samples": config.get("requested_parameter_samples", 0),
    }
    (out_dir / "relation_atlas_status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, status, shape_classes, middle, detector_summary, matched_nulls, window_summary, errors)


def _relation_atlas_detector_summary(aggregate_family: list[dict[str, object]], shapes: list[dict[str, object]]) -> list[dict[str, object]]:
    shape_by_id = {str(row["environment_id"]): row for row in shapes}
    out = []
    for row in aggregate_family:
        env_id = str(row["family"])
        shape = shape_by_id.get(env_id, {})
        shape_class = str(shape.get("environment_shape_class", "missing_shape"))
        aggregate_class = str(row["aggregate_family_class_v1_1"])
        atlas_gate_class = aggregate_class if shape_class == "middle_regime_environment" else shape_class
        out.append({**row, "environment_id": env_id, "environment_shape_class": shape_class, "atlas_gate_class": atlas_gate_class})
    return out


def _shape_class_counts(shapes: list[dict[str, object]]) -> list[dict[str, object]]:
    counts: dict[str, int] = {}
    for row in shapes:
        klass = str(row["environment_shape_class"])
        counts[klass] = counts.get(klass, 0) + 1
    return [{"environment_shape_class": klass, "n": count} for klass, count in sorted(counts.items())]


def _parameter_rows(systems: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for system in systems:
        metadata = json.loads(str(system["metadata_json"]))
        rows.append(
            {
                key: metadata.get(key, "")
                for key in (
                    "parameter_set_id",
                    "coordinate_count",
                    "alphabet_size",
                    "neighborhood_radius",
                    "update_footprint",
                    "out_degree_target",
                    "constraint_density",
                    "constraint_strength",
                    "asymmetry_strength",
                    "reversibility_fraction",
                    "rewire_probability",
                    "roughness_strength",
                    "constraint_arity",
                    "constraint_hash",
                )
            }
            | {"environment_id": system["environment_id"], "seed": system["seed"]}
        )
    return rows


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    status: dict[str, object],
    shape_classes: list[dict[str, object]],
    middle: list[dict[str, object]],
    detector_summary: list[dict[str, object]],
    matched_nulls: list[dict[str, object]],
    window_summary: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# RFS-MB0 Action-Generated Relation Atlas",
        "",
        "Environment/substrate calibration pass for neutral generated relation systems.",
        "",
        "## Run Shape",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        f"- Generated environments completed: {status['generated_environments_completed']}",
        f"- Middle-regime environments: {status['middle_regime_environments']}",
        f"- Profiles completed: {status['profiles_completed']}",
        f"- Errors: {status['errors']}",
        f"- Atlas gate passes: {status['atlas_gate_pass_count']}",
        "",
        "## Environment Shape Classes",
        "",
        "| class | n |",
        "|---|---:|",
    ]
    for row in shape_classes:
        lines.append(f"| {row['environment_shape_class']} | {row['n']} |")
    lines.extend(["", "## Middle-Regime Candidates", "", "| environment | parameter set | nonsaturation windows | saturation onset | largest SCC | reciprocity |", "|---|---|---:|---:|---:|---:|"])
    for row in middle[:80]:
        lines.append(
            "| {env} | {param} | {window} | {sat} | {scc:.3f} | {recip:.3f} |".format(
                env=row["environment_id"],
                param=row["parameter_set_id"],
                window=row["nonsaturation_window_length"],
                sat=row["reach_saturation_onset_H"],
                scc=float(row["largest_scc_fraction"]),
                recip=float(row["edge_reciprocity_fraction"]),
            )
        )
    lines.extend(["", "## Detector Results", "", "| environment | shape class | atlas gate | aggregate class | local candidates | saturation | MI delta | motif delta | passing probe families |", "|---|---|---|---|---:|---:|---:|---:|---:|"])
    for row in detector_summary[:120]:
        lines.append(
            "| {env} | {shape} | {gate} | {agg} | {local:.3f} | {sat:.3f} | {mi:.3f} | {motif:.3f} | {passing} |".format(
                env=row["environment_id"],
                shape=row["environment_shape_class"],
                gate=row["atlas_gate_class"],
                agg=row["aggregate_family_class_v1_1"],
                local=float(row["local_candidate_fraction"]),
                sat=float(row["saturation_dominated_fraction"]),
                mi=float(row["mean_MI_delta_vs_null"]),
                motif=float(row["mean_motif_delta_vs_null"]),
                passing=row["passing_probe_family_count"],
            )
        )
    lines.extend(["", "## Null/Control Summary", "", "| environment | null | JS | KL | MI delta | motif delta |", "|---|---|---:|---:|---:|---:|"])
    for row in matched_nulls[:120]:
        lines.append(
            "| {family} | {null} | {js:.3f} | {kl:.3f} | {mi:.3f} | {motif:.3f} |".format(
                family=row["family"],
                null=row["null_name"],
                js=float(row["mean_JS"]),
                kl=float(row["mean_KL"]),
                mi=float(row["mean_MI_delta"]),
                motif=float(row["mean_motif_delta"]),
            )
        )
    lines.extend(["", "## Window Summary", "", "| environment | probe family | window | class | n | MI | JS | saturation |", "|---|---|---|---|---:|---:|---:|---:|"])
    for row in window_summary[:120]:
        lines.append(
            "| {family} | {probe} | {window} | {klass} | {n} | {mi:.3f} | {js:.3f} | {sat:.3f} |".format(
                family=row["family"],
                probe=row["probe_family"],
                window=row["window"],
                klass=row["aggregate_window_class_v1_2"],
                n=row["n"],
                mi=float(row["mean_transition_MI_H"]),
                js=float(row["mean_JS_to_null_H"]),
                sat=float(row["saturation_fraction"]),
            )
        )
    lines.extend(["", "## Parameter Trends", "", "This first runner reports raw parameter rows and environment classes. Treat apparent trends as exploratory until the atlas is large enough for a stable cross-parameter read.", "", "## Claim Boundary", "", "This is environment calibration, not Omega validation. Generated relation environments are neutral parameterized substrates. No agents, identities, viable paths, or value-bearing structures are claimed."])
    if errors:
        lines.extend(["", "## Errors", "", "```json", json.dumps(errors[:20], indent=2, sort_keys=True), "```"])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_for_params(params: RelationParams, seed: int) -> int:
    text = f"{params.parameter_set_id}:{seed}"
    total = 0
    for index, char in enumerate(text):
        total += (index + 1) * ord(char)
    return total * 97


def _jsonable_job(job: dict[str, object]) -> dict[str, object]:
    return {
        key: (value.parameter_set_id if isinstance(value, RelationParams) else value)
        for key, value in job.items()
        if key != "horizons"
    }


if __name__ == "__main__":
    main()
