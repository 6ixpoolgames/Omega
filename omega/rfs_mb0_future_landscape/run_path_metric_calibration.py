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

from .probes import Probe, generate_probes
from .relation_generator import RelationParams, generate_relation_system


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
    parser.add_argument("--max-jobs", type=int, default=72)
    parser.add_argument("--max-runtime-seconds", type=int, default=2400)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    horizons = tuple(int(item.strip()) for item in args.path_horizons.split(",") if item.strip())
    jobs, selection_rows, control_rows = build_jobs(args, horizons)
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


def build_jobs(args: argparse.Namespace, horizons: tuple[int, ...]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
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
        probe_family = candidate["probe_family"]
        window = candidate["window_name"]
        matched = match_control(candidate, control_candidates, metadata)
        selection_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "environment_id": env,
                "probe_family": probe_family,
                "window_name": window,
                "matched_control_environment_id": matched.get("family", ""),
                "matched_control_match_quality": matched.get("match_quality", "none"),
            }
        )
        rows_for_candidate = [
            ("candidate", env, probe_family, window, candidate.get("candidate_id", f"candidate_{index}")),
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
            if row["family"] == env and row["probe_family"] == probe_family and row["window"] != window
        ][:1]
        for control in same_env_controls:
            rows_for_candidate.append(("same_environment_window_control", control["family"], control["probe_family"], control["window"], f"same_env_control_for_{index}"))
        for row_kind, row_env, row_probe, row_window, row_id in rows_for_candidate:
            if row_env not in metadata:
                continue
            for horizon in horizons:
                jobs.append(
                    {
                        "job_id": f"{row_kind}_{index}_{row_probe}_{row_window}_H{horizon}",
                        "row_kind": row_kind,
                        "row_id": row_id,
                        "candidate_environment_id": env,
                        "environment_id": row_env,
                        "metadata_json": metadata[row_env]["metadata_json"],
                        "seed": int(metadata[row_env]["seed"]),
                        "probe_family": row_probe,
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
        if control["probe_family"] != candidate["probe_family"]:
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
    probes = [probe for probe in generate_probes(system, 2) if probe.probe_family == job["probe_family"]]
    if not probes:
        raise ValueError(f"no probe for family {job['probe_family']}")
    probe = probes[0]
    starts = [system.states[(system.seed + i * 17) % len(system.states)] for i in range(int(job["start_samples"]))]
    sequences = []
    rng = random.Random(system.seed + int(job["path_horizon"]) * 1009 + len(str(job["probe_family"])))
    for start in starts:
        sequences.extend(sample_signature_paths(system, probe, start, int(job["path_horizon"]), int(job["sample_paths_per_start"]), rng))
    metrics = path_metrics(sequences, probe, len(system.states))
    endpoint_nulls = []
    unigram_nulls = []
    for replicate in range(int(job["path_null_replicates"])):
        null_rng = random.Random(system.seed + replicate * 7919 + int(job["path_horizon"]))
        endpoint_nulls.append(path_metrics(endpoint_support_randomized(sequences, null_rng), probe, len(system.states)))
        unigram_nulls.append(path_metrics(unigram_shuffled(sequences, null_rng), probe, len(system.states)))
    result = {
        **{key: job[key] for key in ("job_id", "row_kind", "row_id", "candidate_environment_id", "environment_id", "probe_family", "window_name", "path_horizon", "window_class")},
        **metrics,
        "endpoint_bigram_mi_rank": rank_metric(metrics["bigram_mutual_information"], [row["bigram_mutual_information"] for row in endpoint_nulls]),
        "endpoint_trigram_gain_rank": rank_metric(metrics["predictive_gain_bigram_context"], [row["predictive_gain_bigram_context"] for row in endpoint_nulls]),
        "unigram_bigram_mi_rank": rank_metric(metrics["bigram_mutual_information"], [row["bigram_mutual_information"] for row in unigram_nulls]),
        "unigram_trigram_gain_rank": rank_metric(metrics["predictive_gain_bigram_context"], [row["predictive_gain_bigram_context"] for row in unigram_nulls]),
        "path_null_replicates": int(job["path_null_replicates"]),
    }
    result.update(fakeout_flags(result))
    result["path_evidence_level"] = evidence_level(result)
    result["would_promote_if_enabled"] = int(result["path_evidence_level"] == "provisional_path_process_blocked_by_calibration_policy")
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


def path_metrics(sequences: list[tuple[object, ...]], probe: Probe, state_count: int) -> dict[str, object]:
    unigrams = Counter(item for sequence in sequences for item in sequence)
    bigrams = Counter((sequence[i], sequence[i + 1]) for sequence in sequences for i in range(len(sequence) - 1))
    trigrams = Counter((sequence[i], sequence[i + 1], sequence[i + 2]) for sequence in sequences for i in range(len(sequence) - 2))
    support = len(unigrams)
    alphabet = max(1, 3 ** max(1, probe.arity))
    return {
        "path_count": len(sequences),
        "probe_signature_alphabet_size": alphabet,
        "observed_signature_support_size": support,
        "observed_signature_support_fraction": support / alphabet,
        "probe_collision_rate": max(0.0, 1.0 - support / max(1, state_count)),
        "unigram_entropy_ceiling": math.log2(max(1, alphabet)),
        "unigram_entropy": entropy(unigrams),
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
    low_outdegree = False
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
        "fakeout_class": ";".join(fakeouts),
    }


def evidence_level(row: dict[str, object]) -> str:
    if row["row_kind"] != "candidate":
        return "matched_control"
    if row.get("matched_control_environment_id", "") == "":
        return "path_descriptive"
    if int(row["probe_collision_fakeout_flag"]) or int(row["low_alphabet_fakeout_flag"]):
        return "path_fakeout"
    if int(row["endpoint_support_fakeout_flag"]):
        return "path_descriptive"
    if int(row["unigram_marginal_fakeout_flag"]):
        return "path_above_endpoint"
    if float(row["endpoint_bigram_mi_rank"]) >= 0.80 and float(row["unigram_bigram_mi_rank"]) >= 0.80:
        return "provisional_path_process_blocked_by_calibration_policy"
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
            control_metric_by_candidate.setdefault((row["candidate_environment_id"], row["probe_family"], row["path_horizon"]), row)
    for row in results:
        if row["row_kind"] != "candidate":
            row["matched_control_environment_id"] = ""
            row["matched_control_match_quality"] = ""
            continue
        control = control_metric_by_candidate.get((row["candidate_environment_id"], row["probe_family"], row["path_horizon"]), {})
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
            row["path_evidence_level"] = "path_descriptive"
            row["fakeout_class"] = str(row["fakeout_class"]) + ";descriptive_only_no_matched_control"
    _write_csv(out_dir / "path_metric_calibration_summary.csv", results)
    _write_csv(out_dir / "probe_collision_diagnostics.csv", probe_collision_rows(results))
    _write_csv(out_dir / "matched_non_candidate_path_controls.csv", control_rows)
    _write_csv(out_dir / "path_null_rank_summary.csv", null_rank_rows(results))
    _write_csv(out_dir / "path_metric_effect_sizes.csv", effect_size_rows(results))
    _write_csv(out_dir / "path_fakeout_summary.csv", fakeout_summary(results))
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
    lines = [
        "# RFS-MB0 Path Metric Calibration Report",
        "",
        "Promotion disabled: this is a calibration smoke, not a path-process detection run.",
        "",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {args.workers}",
        f"- Jobs queued: {len(jobs)}",
        f"- Jobs completed: {len(results)}",
        f"- Errors: {len(errors)}",
        "",
        "## Fakeout Counts",
        "",
        "| fakeout | n |",
        "|---|---:|",
    ]
    for row in fakeouts:
        lines.append(f"| {row['fakeout_class']} | {row['n_rows']} |")
    lines.extend(["", "## Candidate Evidence Levels", "", "| level | n |", "|---|---:|"])
    for level, count in sorted(levels.items()):
        lines.append(f"| {level} | {count} |")
    candidate_rows = [row for row in results if row.get("row_kind") == "candidate"]
    matched = [row for row in candidate_rows if row.get("matched_control_environment_id")]
    lines.extend(
        [
            "",
            "## Matched Controls",
            "",
            f"- Candidate rows: {len(candidate_rows)}",
            f"- Candidate rows with matched controls: {len(matched)}",
            "",
            "## Claim Boundary",
            "",
            "This smoke calibrates path metrics against fakeout controls. It does not promote path-process candidates or claim Omega validation.",
        ]
    )
    (out_dir / "path_metric_calibration_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
