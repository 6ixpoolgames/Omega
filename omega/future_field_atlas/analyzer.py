from __future__ import annotations

from collections import defaultdict

from .contracts import MappedScan
from .util import mean


def selection_operator_geometry_summary(scans: list[MappedScan]) -> list[dict[str, object]]:
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
            if (
                int(row.get("inside_rank_boundary_edge_count", 0) or 0)
                + int(row.get("outside_rank_boundary_edge_count", 0) or 0)
            ) > 0
        ] or boundary_rows
        profiles = profile_grouped.get(condition_id, [])
        inside_fraction = mean([float(row["selected_inside_rank_boundary_fraction"]) for row in evaluable_rows])
        outside_fraction = mean([float(row["selected_outside_rank_boundary_fraction"]) for row in evaluable_rows])
        rank_boundary_k = int(first["rank_boundary_k"])
        rank_metrics = observable_prefix_rank_set_metrics(first)
        boundary_distance = rank_boundary_distance(
            selected_inside_fraction=inside_fraction,
            selected_outside_fraction=outside_fraction,
            rank_set_distance=rank_metrics["rank_set_distance_to_observable_prefix"],
        )
        rows.append({
            "condition_id": condition_id,
            "selection_operator_id": first["selection_operator_id"],
            "selection_operator_family": first["selection_operator_family"],
            "selection_operator_params_json": first["selection_operator_params_json"],
            "group_id": first["group_id"],
            "macro_invariant_beta": first["macro_invariant_beta"],
            "base_out_degree": first["base_out_degree"],
            "effective_out_degree": first["effective_out_degree"],
            "rank_boundary_k": rank_boundary_k,
            "retained_rank_set": first["retained_rank_set"],
            "removed_rank_set": first["removed_rank_set"],
            "stochastic_selection_flag": first["stochastic_selection_flag"],
            **rank_metrics,
            "mean_selected_inside_rank_boundary_fraction": inside_fraction,
            "mean_selected_outside_rank_boundary_fraction": outside_fraction,
            "operator_rank_boundary_distance": boundary_distance,
            "mean_frontier_state_count": mean([float(row["frontier_state_count"]) for row in profiles]),
            "mean_frontier_component_count": mean([float(row["frontier_component_count"]) for row in profiles]),
        })
    return rows


def rank_boundary_geometry_by_horizon(scans: list[MappedScan]) -> list[dict[str, object]]:
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
            "group_id": first["group_id"],
            "horizon": first["horizon"],
            "base_out_degree": first["base_out_degree"],
            "effective_out_degree": first["effective_out_degree"],
            "rank_boundary_k": first["rank_boundary_k"],
            "retained_rank_set": first["retained_rank_set"],
            "removed_rank_set": first["removed_rank_set"],
            "selected_inside_rank_boundary_fraction": mean([
                float(row["selected_inside_rank_boundary_fraction"]) for row in rows
            ]),
            "selected_outside_rank_boundary_fraction": mean([
                float(row["selected_outside_rank_boundary_fraction"]) for row in rows
            ]),
            "inside_rank_boundary_edge_count": mean([float(row["inside_rank_boundary_edge_count"]) for row in rows]),
            "outside_rank_boundary_edge_count": mean([float(row["outside_rank_boundary_edge_count"]) for row in rows]),
        })
    return out


def rank_boundary_geometry_by_horizon_pair(
    scans: list[MappedScan],
    horizon_pairs: tuple[tuple[int, int], ...],
) -> list[dict[str, object]]:
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
                "group_id": scan.raw.spec.group_id,
                "source_horizon": left,
                "target_horizon": right,
                "inside_rank_boundary_fraction_delta": (
                    float(end["selected_inside_rank_boundary_fraction"])
                    - float(start["selected_inside_rank_boundary_fraction"])
                ),
                "outside_rank_boundary_fraction_delta": (
                    float(end["selected_outside_rank_boundary_fraction"])
                    - float(start["selected_outside_rank_boundary_fraction"])
                ),
            })
    return rows


def observable_prefix_rank_set_metrics(row: dict[str, object]) -> dict[str, object]:
    rank_boundary_k = int(row["rank_boundary_k"])
    observable_prefix = set(range(1, rank_boundary_k + 1))
    retained = parse_rank_set(row.get("retained_rank_set", ""))
    if not retained:
        return {
            "observable_prefix_rank_set": rank_set_text(tuple(sorted(observable_prefix))),
            "rank_set_jaccard_to_observable_prefix": "",
            "rank_set_precision_to_observable_prefix": "",
            "rank_set_recall_to_observable_prefix": "",
            "rank_set_symmetric_difference_from_observable_prefix": "",
            "rank_set_distance_to_observable_prefix": "",
        }
    intersection = retained & observable_prefix
    union = retained | observable_prefix
    symmetric_difference = retained ^ observable_prefix
    jaccard = len(intersection) / max(1, len(union))
    precision = len(intersection) / max(1, len(retained))
    recall = len(intersection) / max(1, len(observable_prefix))
    return {
        "observable_prefix_rank_set": rank_set_text(tuple(sorted(observable_prefix))),
        "rank_set_jaccard_to_observable_prefix": jaccard,
        "rank_set_precision_to_observable_prefix": precision,
        "rank_set_recall_to_observable_prefix": recall,
        "rank_set_symmetric_difference_from_observable_prefix": rank_set_text(tuple(sorted(symmetric_difference))),
        "rank_set_distance_to_observable_prefix": 1.0 - jaccard,
    }


def rank_boundary_distance(
    *,
    selected_inside_fraction: float,
    selected_outside_fraction: float,
    rank_set_distance: object,
) -> object:
    if rank_set_distance == "":
        return ""
    return (
        abs(1.0 - selected_inside_fraction)
        + abs(selected_outside_fraction)
        + float(rank_set_distance)
    ) / 3.0


def parse_rank_set(raw: object) -> set[int]:
    text = str(raw or "").strip()
    if not text:
        return set()
    return {int(token) for token in text.split(";") if token.strip()}


def rank_set_text(values: tuple[int, ...]) -> str:
    return ";".join(str(value) for value in values)
