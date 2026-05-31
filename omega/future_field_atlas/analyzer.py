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
        effective_m = int(first["effective_out_degree"])
        core_rank_k = int(first["core_rank_k"])
        rank_metrics = target_core_rank_set_metrics(first)
        calibration_distance = distance_to_target_core(
            selected_core_fraction=selected_core_fraction,
            selected_fringe_fraction=selected_fringe_fraction,
            core_retention=core_retention,
            rank_set_distance=rank_metrics["distance_to_target_rank_core"],
        )
        rows.append({
            "condition_id": condition_id,
            "selection_operator_id": first["selection_operator_id"],
            "selection_operator_family": first["selection_operator_family"],
            "selection_operator_params_json": first["selection_operator_params_json"],
            "human_label": first["human_label"],
            "legacy_boundary_control_alias": first["legacy_boundary_control_alias"],
            "legacy_role_alias": first["legacy_role_alias"],
            "group_id": first["group_id"],
            "macro_invariant_beta": first["macro_invariant_beta"],
            "base_out_degree": first["base_out_degree"],
            "effective_out_degree": effective_m,
            "core_rank_k": core_rank_k,
            "retained_rank_set": first["retained_rank_set"],
            "removed_rank_set": first["removed_rank_set"],
            "stochastic_selection_flag": first["stochastic_selection_flag"],
            **rank_metrics,
            "mean_selected_core_fraction": selected_core_fraction,
            "mean_selected_fringe_fraction": selected_fringe_fraction,
            "mean_core_retention_fraction_vs_baseline": core_retention,
            "mean_fringe_retention_fraction_vs_baseline": fringe_retention if fringe_retention_values else "",
            "distance_to_target_core_geometry": calibration_distance,
            "mean_frontier_state_count": mean([float(row["frontier_state_count"]) for row in profiles]),
            "mean_frontier_component_count": mean([float(row["frontier_component_count"]) for row in profiles]),
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
            "selection_operator_id": first["selection_operator_id"],
            "selection_operator_family": first["selection_operator_family"],
            "human_label": first["human_label"],
            "legacy_boundary_control_alias": first["legacy_boundary_control_alias"],
            "group_id": first["group_id"],
            "horizon": first["horizon"],
            "base_out_degree": first["base_out_degree"],
            "effective_out_degree": first["effective_out_degree"],
            "core_rank_k": first["core_rank_k"],
            "retained_rank_set": first["retained_rank_set"],
            "removed_rank_set": first["removed_rank_set"],
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
                "selection_operator_id": scan.raw.spec.selection_operator.selection_operator_id,
                "selection_operator_family": scan.raw.spec.selection_operator.operator_family,
                "human_label": scan.raw.spec.human_label,
                "legacy_boundary_control_alias": scan.raw.spec.legacy_boundary_control_alias,
                "group_id": scan.raw.spec.group_id,
                "source_horizon": left,
                "target_horizon": right,
                "core_fraction_delta": float(end["selected_core_fraction"]) - float(start["selected_core_fraction"]),
                "fringe_fraction_delta": float(end["selected_fringe_fraction"]) - float(start["selected_fringe_fraction"]),
                "core_retention_target": end["core_retention_fraction_vs_baseline"],
                "fringe_retention_target": end["fringe_retention_fraction_vs_baseline"],
            })
    return rows


def target_core_rank_set_metrics(row: dict[str, object]) -> dict[str, object]:
    core_rank_k = int(row["core_rank_k"])
    target = set(range(1, core_rank_k + 1))
    retained = parse_rank_set(row.get("retained_rank_set", ""))
    if not retained:
        return {
            "target_core_rank_set": rank_set_text(tuple(sorted(target))),
            "rank_set_jaccard_to_target_core": "",
            "rank_set_precision_to_target_core": "",
            "rank_set_recall_to_target_core": "",
            "distance_to_target_rank_core": "",
        }
    intersection = retained & target
    union = retained | target
    jaccard = len(intersection) / max(1, len(union))
    precision = len(intersection) / max(1, len(retained))
    recall = len(intersection) / max(1, len(target))
    return {
        "target_core_rank_set": rank_set_text(tuple(sorted(target))),
        "rank_set_jaccard_to_target_core": jaccard,
        "rank_set_precision_to_target_core": precision,
        "rank_set_recall_to_target_core": recall,
        "distance_to_target_rank_core": 1.0 - jaccard,
    }


def distance_to_target_core(
    *,
    selected_core_fraction: float,
    selected_fringe_fraction: float,
    core_retention: float,
    rank_set_distance: object,
) -> object:
    if rank_set_distance == "":
        return ""
    return (
        abs(1.0 - selected_core_fraction)
        + abs(selected_fringe_fraction)
        + abs(1.0 - core_retention)
        + float(rank_set_distance)
    ) / 4.0


def parse_rank_set(raw: object) -> set[int]:
    text = str(raw or "").strip()
    if not text:
        return set()
    return {int(token) for token in text.split(";") if token.strip()}


def rank_set_text(values: tuple[int, ...]) -> str:
    return ";".join(str(value) for value in values)
