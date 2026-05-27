from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


PROBE_ROLES = {
    "coordinate_tuple_k3": "evidence",
    "coordinate_tuple_k4": "evidence",
    "constraint_profile_hash": "evidence",
    "constraint_violation_count_plus_local_tuple": "evidence",
    "existing_low": "diagnostic",
    "relation_role": "diagnostic",
    "full_state_hash": "control",
    "full_state_strict": "control",
}

REQUIRED_BATCH1_OUTPUTS = (
    "anchor_selection_audit.csv",
    "runtime_finalization_audit.csv",
    "checkpoint_audit.csv",
    "saturation_decomposition.csv",
    "probe_role_recurrence_summary.csv",
    "focused_boundary_group_selection.csv",
    "boundary_recurrence_repair_report.md",
    "output_manifest.json",
    "status.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair/report boundary recurrence partial outputs.")
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1"))
    parser.add_argument("--anchors-requested", type=int, default=10)
    parser.add_argument("--top-groups", type=int, default=20)
    parser.add_argument("--saturation-threshold", type=float, default=0.90)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    status = read_json(args.source_run / "status.json")
    anchors = read_csv(args.source_run / "atlas_band_selection.csv")
    band_audit = read_csv(args.source_run / "atlas_band_classification_audit.csv")
    sweep_rows = read_csv(args.source_run / "local_parameter_sweep_results.csv")
    fresh_seed = read_csv(args.source_run / "fresh_seed_recurrence_audit.csv")
    transitions = read_csv(args.source_run / "transition_class_summary.csv")
    transition_graph = read_csv(args.source_run / "phenotype_transition_graph.csv")

    anchor_audit = anchor_selection_audit(args, anchors, band_audit)
    runtime_audit = runtime_finalization_audit(status)
    checkpoint_rows = checkpoint_audit(status)
    saturation_rows = saturation_decomposition(sweep_rows, band_audit, args.saturation_threshold)
    probe_rows = probe_role_recurrence_summary(sweep_rows)
    focused_groups = focused_boundary_group_selection(fresh_seed, transition_graph, sweep_rows, band_audit, args.top_groups)

    write_csv(args.out / "anchor_selection_audit.csv", anchor_audit)
    write_csv(args.out / "runtime_finalization_audit.csv", runtime_audit)
    write_csv(args.out / "checkpoint_audit.csv", checkpoint_rows)
    write_csv(args.out / "saturation_decomposition.csv", saturation_rows)
    write_csv(args.out / "probe_role_recurrence_summary.csv", probe_rows)
    write_csv(args.out / "focused_boundary_group_selection.csv", focused_groups)
    write_report(args.out, args, status, anchor_audit, runtime_audit, saturation_rows, probe_rows, focused_groups)
    write_status(args.out, status, len(sweep_rows), len(focused_groups))
    write_manifest(args.out)


def anchor_selection_audit(args: argparse.Namespace, anchors: list[dict[str, str]], band_audit: list[dict[str, str]]) -> list[dict[str, object]]:
    band_classes = Counter(row.get("band_class", "") for row in band_audit)
    selected_ids = [row.get("anchor_id", "") for row in anchors]
    available = len(anchors)
    return [
        {
            "anchors_requested": args.anchors_requested,
            "anchors_available": available,
            "anchors_selected": available,
            "selection_source": str(args.source_run),
            "selection_mode": "existing_boundary_partial",
            "shortfall_flag": int(available < args.anchors_requested),
            "shortfall_reason": "source run exposed fewer boundary anchors than requested" if available < args.anchors_requested else "",
            "candidate_boundary_anchor_count": sum(1 for row in band_audit if row.get("anchor_class", "").endswith("_candidate")),
            "near_miss_anchor_count": band_classes.get("near_miss_transition_band", 0),
            "saturation_boundary_anchor_count": sum(1 for row in band_audit if float_or_zero(row.get("saturation_boundary_count")) > 0),
            "probe_resolution_boundary_anchor_count": sum(1 for row in band_audit if float_or_zero(row.get("probe_resolution_boundary_count")) > 0),
            "stable_fakeout_anchor_count": band_classes.get("stable_fakeout_band", 0),
            "selected_anchor_ids": json.dumps(selected_ids),
        }
    ]


def runtime_finalization_audit(status: dict[str, object]) -> list[dict[str, object]]:
    raw_status = str(status.get("status", "missing"))
    interrupted = int(raw_status == "RUNNING")
    return [
        {
            "source_status": raw_status,
            "repaired_status": "INTERRUPTED_PARTIAL" if interrupted else raw_status,
            "finalization_reason": "external_wrapper_interrupted_before_final_status" if interrupted else "source_status_final",
            "wall_clock_seconds": status.get("wall_clock_seconds", ""),
            "max_runtime_seconds": status.get("max_runtime_seconds", "not_recorded"),
            "shutdown_cushion_seconds": status.get("shutdown_cushion_seconds", "not_recorded"),
            "jobs_requested": status.get("sweep_jobs_requested", status.get("jobs_requested", "")),
            "jobs_submitted": status.get("sweep_jobs_completed", status.get("jobs_submitted", "")),
            "jobs_completed": status.get("sweep_jobs_completed", status.get("jobs_completed", "")),
            "jobs_cancelled": "unknown_external_interrupt" if interrupted else 0,
            "pending_jobs_remaining": max(0, int(float_or_zero(status.get("sweep_jobs_requested"))) - int(float_or_zero(status.get("sweep_jobs_completed")))),
            "errors": status.get("errors", ""),
            "last_checkpoint_utc": status.get("last_checkpoint_utc", "not_recorded"),
            "final_outputs_written": True,
        }
    ]


def checkpoint_audit(status: dict[str, object]) -> list[dict[str, object]]:
    completed = int(float_or_zero(status.get("sweep_jobs_completed")))
    return [
        {
            "checkpoint_index": 1,
            "checkpoint_kind": "last_observed_source_checkpoint",
            "checkpoint_count": status.get("checkpoint_count", "not_recorded"),
            "completed_jobs": completed,
            "elapsed_seconds": status.get("wall_clock_seconds", ""),
            "last_checkpoint_completed_jobs": status.get("last_checkpoint_completed_jobs", completed),
            "last_checkpoint_elapsed_seconds": status.get("last_checkpoint_elapsed_seconds", status.get("wall_clock_seconds", "")),
            "last_checkpoint_utc": status.get("last_checkpoint_utc", "not_recorded"),
        }
    ]


def saturation_decomposition(rows: list[dict[str, str]], band_audit: list[dict[str, str]], saturation_threshold: float) -> list[dict[str, object]]:
    band_has_saturation = {
        row.get("anchor_id", ""): int(float_or_zero(row.get("saturation_boundary_count")) > 0)
        for row in band_audit
    }
    probe_rates = rate_by(rows, "probe_family", lambda row: saturation_flag(row, saturation_threshold))
    horizon_rates = rate_by(rows, "H", lambda row: saturation_flag(row, saturation_threshold))
    out = []
    for row in rows:
        role = probe_role(row.get("probe_key", ""), row.get("probe_family", ""))
        is_candidate = candidate_like(row)
        row_sat = saturation_flag(row, saturation_threshold)
        band_sat = band_has_saturation.get(row.get("anchor_id", ""), 0)
        out.append(
            {
                "row_id": row_id(row),
                "band_id": row.get("anchor_id", ""),
                "anchor_id": row.get("anchor_id", ""),
                "variant_dimension": row.get("variant_dimension", ""),
                "variant_value": row.get("variant_value", ""),
                "probe_family": row.get("probe_family", ""),
                "probe_role": role,
                "horizon": row.get("H", ""),
                "start_samples": row.get("start_samples", ""),
                "local_primary_class": row.get("local_primary_class", ""),
                "is_local_pre_control_candidate_like": int(is_candidate),
                "row_support_ceiling_flag": int(float_or_zero(row.get("support_ceiling_flag")) > 0),
                "row_state_space_saturation_flag": int(float_or_zero(row.get("reachable_signature_support_fraction")) >= 0.95),
                "row_probe_alphabet_saturation_flag": int(float_or_zero(row.get("observed_signature_support_fraction")) >= 0.95),
                "band_has_saturation_boundary": band_sat,
                "probe_family_saturation_rate": probe_rates.get(row.get("probe_family", ""), 0.0),
                "horizon_saturation_rate": horizon_rates.get(row.get("H", ""), 0.0),
                "candidate_row_saturation_flag": int(is_candidate and row_sat),
                "candidate_band_saturation_contamination_flag": int(is_candidate and band_sat),
                "classification_if_saturation_rows_excluded": "excluded_saturation_row" if row_sat else row.get("local_primary_class", ""),
            }
        )
    return out


def probe_role_recurrence_summary(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for key, items in group_by(rows, ("anchor_id", "variant_dimension", "variant_value")).items():
        counts_by_role: dict[str, set[str]] = defaultdict(set)
        candidate_by_role: dict[str, set[str]] = defaultdict(set)
        for row in items:
            role = probe_role(row.get("probe_key", ""), row.get("probe_family", ""))
            family = row.get("probe_family", "")
            counts_by_role[role].add(family)
            if candidate_like(row):
                candidate_by_role[role].add(family)
        evidence_total = len(counts_by_role.get("evidence", set()))
        evidence_count = len(candidate_by_role.get("evidence", set()))
        diagnostic_total = len(counts_by_role.get("diagnostic", set()))
        control_total = len(counts_by_role.get("control", set()))
        out.append(
            {
                "band_id": key[0],
                "anchor_id": key[0],
                "variant_dimension": key[1],
                "variant_value": key[2],
                "probe_recurrence_all_probes_min": min_role_fraction(candidate_by_role, counts_by_role),
                "probe_recurrence_evidence_probe_min": 1.0 if evidence_total and evidence_count == evidence_total else 0.0,
                "probe_recurrence_evidence_probe_fraction": evidence_count / max(1, evidence_total),
                "probe_recurrence_evidence_probe_count": evidence_count,
                "probe_recurrence_diagnostic_probe_fraction": len(candidate_by_role.get("diagnostic", set())) / max(1, diagnostic_total),
                "probe_recurrence_control_probe_fraction": len(candidate_by_role.get("control", set())) / max(1, control_total),
                "probe_local_only_flag": int(evidence_count <= 1),
                "cross_probe_recurrent_evidence_flag": int(evidence_count >= 2),
            }
        )
    return out


def focused_boundary_group_selection(
    fresh_seed: list[dict[str, str]],
    transition_graph: list[dict[str, str]],
    sweep_rows: list[dict[str, str]],
    band_audit: list[dict[str, str]],
    top_groups: int,
) -> list[dict[str, object]]:
    transition_by_group = Counter(
        (row.get("anchor_id", ""), row.get("variant_dimension", ""), row.get("variant_value", ""), row.get("transition_class", ""))
        for row in transition_graph
    )
    rows_by_group = group_by(sweep_rows, ("anchor_id", "variant_dimension", "variant_value"))
    stable_bands = {row.get("anchor_id", "") for row in band_audit if int(float_or_zero(row.get("eligible_for_stable_candidate_band"))) > 0}
    candidates = []
    for row in fresh_seed:
        klass = row.get("fresh_seed_recurrence_class", "")
        if klass not in {"seed_recurrent_candidate_like", "seed_mixed_or_boundary"}:
            continue
        variant_dimension, variant_value = parse_parameter_variant(row.get("parameter_variant_id", ""))
        key = (row.get("anchor_id", ""), variant_dimension, variant_value)
        if key[0] in stable_bands:
            continue
        items = rows_by_group.get(key, [])
        local_count = sum(int(candidate_like(item)) for item in items)
        nonsat_count = sum(int(candidate_like(item) and not saturation_flag(item, 0.90)) for item in items)
        transition_counts = {
            transition: count
            for (anchor, dim, value, transition), count in transition_by_group.items()
            if (anchor, dim, value) == key
        }
        if not (local_count or transition_counts.get("fakeout_to_candidate_transition", 0) or transition_counts.get("candidate_stable_region", 0)):
            continue
        probe_families = sorted({item.get("probe_family", "") for item in items if candidate_like(item)})
        horizons = sorted({item.get("H", "") for item in items if candidate_like(item)}, key=lambda value: float_or_zero(value))
        candidates.append(
            {
                "group_id": f"{key[0]}|{key[1]}={key[2]}",
                "source_band_id": key[0],
                "source_anchor_id": key[0],
                "parameter_variant_id": row.get("parameter_variant_id", f"{key[1]}={key[2]}"),
                "variant_dimension": key[1],
                "variant_value": key[2],
                "fresh_seed_count": row.get("fresh_seed_count", ""),
                "fresh_seed_candidate_count": row.get("fresh_seed_candidate_count", ""),
                "fresh_seed_recurrence_class": klass,
                "transition_class_counts": json.dumps(transition_counts, sort_keys=True),
                "local_pre_control_candidate_like_count": local_count,
                "non_saturation_local_candidate_like_count": nonsat_count,
                "probe_families_with_candidate_like": json.dumps(probe_families),
                "horizons_with_candidate_like": json.dumps(horizons),
                "saturation_contamination_summary": json.dumps(Counter(str(saturation_flag(item, 0.90)) for item in items if candidate_like(item)), sort_keys=True),
                "probe_resolution_contamination_summary": json.dumps(Counter(item.get("probe_resolution_class", "") for item in items if candidate_like(item)), sort_keys=True),
                "selection_reason": selection_reason(transition_counts, nonsat_count, klass),
            }
        )
    candidates.sort(
        key=lambda item: (
            "fakeout_to_candidate" not in str(item["selection_reason"]),
            -int(item["non_saturation_local_candidate_like_count"]),
            -int(float_or_zero(item["fresh_seed_candidate_count"])),
        )
    )
    return candidates[:top_groups]


def write_report(
    out_dir: Path,
    args: argparse.Namespace,
    source_status: dict[str, object],
    anchor_audit: list[dict[str, object]],
    runtime_audit: list[dict[str, object]],
    saturation_rows: list[dict[str, object]],
    probe_rows: list[dict[str, object]],
    focused_groups: list[dict[str, object]],
) -> None:
    local_candidates = sum(int(row["is_local_pre_control_candidate_like"]) for row in saturation_rows)
    saturated_candidates = sum(int(row["candidate_row_saturation_flag"]) for row in saturation_rows)
    cross_probe_groups = sum(int(row["cross_probe_recurrent_evidence_flag"]) for row in probe_rows)
    lines = [
        "# RFS-MB0 Boundary Recurrence Repair Report",
        "",
        "Batch 1 is reporting/repair only. It reads the interrupted boundary sweep and writes explicit audit tables before any new large compute pass.",
        "",
        "## 1. Run Status And Partial Handling",
        "",
        f"- Source status: {source_status.get('status', '')}",
        f"- Repaired status: {runtime_audit[0].get('repaired_status', '') if runtime_audit else ''}",
        f"- Source jobs completed: {source_status.get('sweep_jobs_completed', '')} / {source_status.get('sweep_jobs_requested', '')}",
        "",
        "## 2. Anchor Selection Audit",
        "",
        f"- Anchors requested: {anchor_audit[0].get('anchors_requested', '') if anchor_audit else ''}",
        f"- Anchors selected: {anchor_audit[0].get('anchors_selected', '') if anchor_audit else ''}",
        f"- Shortfall: {anchor_audit[0].get('shortfall_flag', '') if anchor_audit else ''}",
        "",
        "## 3. Candidate-Like Terminology Audit",
        "",
        f"- local_pre_control_candidate_like_rows: {local_candidates}",
        "- matched_control_candidate_like_rows: not_computed_in_local_sweep",
        "- band_level_candidate_like_rows: see `probe_role_recurrence_summary.csv` and `focused_boundary_group_selection.csv`",
        f"- local_candidate_like_rows_that_are_saturated: {saturated_candidates}",
        f"- local_candidate_like_rows_non_saturated: {local_candidates - saturated_candidates}",
        "",
        "## 4. Fresh-Seed Recurrent Group Selection",
        "",
        f"- focused groups selected: {len(focused_groups)}",
        "",
        "## 5. Probe-Role Recurrence Summary",
        "",
        f"- groups with evidence cross-probe recurrence: {cross_probe_groups}",
        "",
        "## 6. Cross-Probe Recurrence Results",
        "",
        "No new focused compute was run in Batch 1. Batch 2 should evaluate the selected groups with 18 workers.",
        "",
        "## 7. Saturation Decomposition",
        "",
        f"- saturation decomposition rows: {len(saturation_rows)}",
        "",
        "## 8. Probe-Resolution Decomposition",
        "",
        "Probe resolution classes are included per row in `saturation_decomposition.csv` and aggregated by role in `probe_role_recurrence_summary.csv`.",
        "",
        "## 9. Stable Candidate Blockers",
        "",
        "Stable candidate bands remain blocked until evidence-probe recurrence and non-saturation recurrence are both shown.",
        "",
        "## 10. Decision Gate Result",
        "",
        "Proceed to Batch 2 focused cross-probe smoke. Do not run n=6.",
        "",
        "## 11. Claim Boundary",
        "",
        "This report repairs measurement language and audit surfaces. It does not claim Omega, agency, value, identity, viability, path-process detection, or scientific-gate passage.",
        "",
        "## 12. Output Manifest",
        "",
        "See `output_manifest.json`.",
    ]
    (out_dir / "boundary_recurrence_repair_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_status(out_dir: Path, source_status: dict[str, object], source_rows: int, focused_groups: int) -> None:
    status = {
        "status": "COMPLETED",
        "batch": "batch1_reporting_repair",
        "source_status": source_status.get("status", ""),
        "source_sweep_rows": source_rows,
        "focused_groups_selected": focused_groups,
        "final_outputs_written": True,
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


def selection_reason(transition_counts: dict[str, int], nonsat_count: int, klass: str) -> str:
    reasons = []
    if transition_counts.get("fakeout_to_candidate_transition", 0):
        reasons.append("fakeout_to_candidate_transition")
    if transition_counts.get("candidate_stable_region", 0):
        reasons.append("candidate_stable_region")
    if nonsat_count:
        reasons.append("non_saturation_local_candidate_like")
    reasons.append(klass)
    return ";".join(reasons)


def probe_role(probe_key: str, probe_family: str) -> str:
    return PROBE_ROLES.get(probe_key) or PROBE_ROLES.get(probe_family) or "unknown_diagnostic"


def candidate_like(row: dict[str, str]) -> bool:
    return str(row.get("local_primary_class", "")).endswith("_candidate")


def saturation_flag(row: dict[str, str], threshold: float) -> bool:
    return (
        float_or_zero(row.get("support_ceiling_flag")) > 0
        or float_or_zero(row.get("reachable_signature_support_fraction")) >= threshold
        or "ceiling" in str(row.get("local_primary_class", ""))
    )


def row_id(row: dict[str, str]) -> str:
    return "|".join(str(row.get(key, "")) for key in ("job_id", "start_index", "H"))


def rate_by(rows: list[dict[str, str]], key: str, predicate: object) -> dict[str, float]:
    counts: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        counts[row.get(key, "")].append(int(predicate(row)))  # type: ignore[operator]
    return {item: sum(values) / max(1, len(values)) for item, values in counts.items()}


def min_role_fraction(candidate_by_role: dict[str, set[str]], counts_by_role: dict[str, set[str]]) -> float:
    fractions = []
    for role, families in counts_by_role.items():
        if not families:
            continue
        fractions.append(len(candidate_by_role.get(role, set())) / len(families))
    return min(fractions) if fractions else 0.0


def group_by(rows: list[dict[str, str]], keys: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, str]]]:
    out: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[tuple(row.get(key, "") for key in keys)].append(row)
    return out


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("empty\n", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_manifest(out_dir: Path) -> None:
    rows = []
    for name in REQUIRED_BATCH1_OUTPUTS:
        path = out_dir / name
        exists = True if name == "output_manifest.json" else path.exists()
        rows.append({"file": name, "exists": exists, "status": "present" if exists else "missing", "row_count": csv_row_count(path) if path.suffix == ".csv" else ""})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def parse_parameter_variant(value: str) -> tuple[str, str]:
    if "=" not in value:
        return "", ""
    left, right = value.split("=", 1)
    return left, right


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.suffix != ".csv":
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows or rows[0] == ["empty"]:
        return 0
    return max(0, len(rows) - 1)


def float_or_zero(value: object) -> float:
    try:
        if value == "":
            return 0.0
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    main()
