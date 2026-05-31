from __future__ import annotations

from collections import defaultdict

from .contracts import MappedScan
from .util import mean


def known_mechanism_recovery_summary(scans: list[MappedScan]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    profile_grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for scan in scans:
        for row in scan.boundary_rows:
            grouped[str(row["condition_id"])].append(row)
        for row in scan.profile_rows:
            profile_grouped[str(row["condition_id"])].append(row)
    rows: list[dict[str, object]] = []
    for condition_id, boundary_rows in sorted(grouped.items()):
        first = boundary_rows[0]
        evaluable_rows = [
            row for row in boundary_rows
            if int(row.get("baseline_core_edge_count", 0) or 0) > 0
            and (int(row.get("core_edge_count", 0) or 0) + int(row.get("fringe_edge_count", 0) or 0)) > 0
        ] or boundary_rows
        profiles = profile_grouped.get(condition_id, [])
        selected_core_fraction = mean([float(row["selected_core_fraction"]) for row in evaluable_rows])
        selected_fringe_fraction = mean([float(row["selected_fringe_fraction"]) for row in evaluable_rows])
        core_retention = mean([float(row["core_retention_fraction_vs_baseline"]) for row in evaluable_rows if row["core_retention_fraction_vs_baseline"] != ""])
        fringe_retention_values = [float(row["fringe_retention_fraction_vs_baseline"]) for row in evaluable_rows if row["fringe_retention_fraction_vs_baseline"] != ""]
        fringe_retention = mean(fringe_retention_values)
        effective_m = int(first["effective_m"])
        core_rank_k = int(first["core_rank_k"])
        recovered_top3_core = int(
            effective_m == core_rank_k
            and selected_core_fraction >= 0.95
            and selected_fringe_fraction <= 0.05
            and core_retention >= 0.95
        )
        rows.append({
            "condition_id": condition_id,
            "boundary_control": first["boundary_control"],
            "condition_role": first["condition_role"],
            "group_id": first["group_id"],
            "macro_invariant_beta": first["macro_invariant_beta"],
            "base_m": first["base_m"],
            "effective_m": effective_m,
            "core_rank_k": core_rank_k,
            "mean_selected_core_fraction": selected_core_fraction,
            "mean_selected_fringe_fraction": selected_fringe_fraction,
            "mean_core_retention_fraction_vs_baseline": core_retention,
            "mean_fringe_retention_fraction_vs_baseline": fringe_retention if fringe_retention_values else "",
            "mean_frontier_state_count": mean([float(row["frontier_state_count"]) for row in profiles]),
            "mean_frontier_component_count": mean([float(row["frontier_component_count"]) for row in profiles]),
            "raw_topology_recovers_retained_core3": recovered_top3_core,
            "recovery_read": recovery_read(str(first["boundary_control"]), recovered_top3_core, selected_fringe_fraction),
        })
    return rows


def rank_core_recovery_by_horizon(scans: list[MappedScan]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for scan in scans:
        for row in scan.boundary_rows:
            grouped[(str(row["condition_id"]), int(row["horizon"]))].append(row)
    out: list[dict[str, object]] = []
    for (_condition_id, _horizon), rows in sorted(grouped.items()):
        first = rows[0]
        out.append({
            "condition_id": first["condition_id"],
            "boundary_control": first["boundary_control"],
            "group_id": first["group_id"],
            "horizon": first["horizon"],
            "base_m": first["base_m"],
            "effective_m": first["effective_m"],
            "core_rank_k": first["core_rank_k"],
            "selected_core_fraction": mean([float(row["selected_core_fraction"]) for row in rows]),
            "selected_fringe_fraction": mean([float(row["selected_fringe_fraction"]) for row in rows]),
            "core_retention_fraction_vs_baseline": mean([float(row["core_retention_fraction_vs_baseline"]) for row in rows if row["core_retention_fraction_vs_baseline"] != ""]),
            "fringe_retention_fraction_vs_baseline": mean([float(row["fringe_retention_fraction_vs_baseline"]) for row in rows if row["fringe_retention_fraction_vs_baseline"] != ""]),
            "core_edge_count": mean([float(row["core_edge_count"]) for row in rows]),
            "fringe_edge_count": mean([float(row["fringe_edge_count"]) for row in rows]),
        })
    return out


def boundary_recovery_by_horizon_pair(scans: list[MappedScan], horizon_pairs: tuple[tuple[int, int], ...]) -> list[dict[str, object]]:
    by_scan_h: dict[tuple[str, int], dict[str, object]] = {}
    for scan in scans:
        for row in scan.boundary_rows:
            by_scan_h[(str(row["scan_id"]), int(row["horizon"]))] = row
    rows: list[dict[str, object]] = []
    for scan in scans:
        for left, right in horizon_pairs:
            start = by_scan_h.get((scan.raw.scan_id, left))
            end = by_scan_h.get((scan.raw.scan_id, right))
            if start is None or end is None:
                continue
            rows.append({
                "scan_id": scan.raw.scan_id,
                "condition_id": scan.raw.spec.condition_id,
                "boundary_control": scan.raw.spec.boundary_control,
                "group_id": scan.raw.spec.group_id,
                "source_horizon": left,
                "target_horizon": right,
                "core_fraction_delta": float(end["selected_core_fraction"]) - float(start["selected_core_fraction"]),
                "fringe_fraction_delta": float(end["selected_fringe_fraction"]) - float(start["selected_fringe_fraction"]),
                "core_retention_target": end["core_retention_fraction_vs_baseline"],
                "fringe_retention_target": end["fringe_retention_fraction_vs_baseline"],
            })
    return rows


def recovery_read(boundary_control: str, recovered_top3_core: int, selected_fringe_fraction: float) -> str:
    if recovered_top3_core:
        return "raw_topology_identifies_retained_low_rank_core"
    if boundary_control.startswith("baseline") and selected_fringe_fraction > 0.05:
        return "baseline_contains_fringe_boundary_edges"
    if "random" in boundary_control:
        return "random_pruning_control_not_expected_to_match_core"
    if "strongest" in boundary_control:
        return "strongest_edge_pruning_control_breaks_core"
    return "raw_topology_does_not_identify_core3"
