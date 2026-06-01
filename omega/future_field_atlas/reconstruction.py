from __future__ import annotations

from collections import defaultdict

from .transport import SparseMatrixRecord


FLOAT_TOLERANCE = 1e-9


def reconstruction_audit_rows(
    *,
    node_rows: list[dict[str, object]],
    edge_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    rank_boundary_rows: list[dict[str, object]],
    adjacent_manifest_rows: list[dict[str, object]],
    adjacent_matrices: list[SparseMatrixRecord],
    operator_geometry_rows: list[dict[str, object]],
    condition_identity_rows: list[dict[str, object]],
    scan_manifest_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [
        audit_condition_identity_traceability(
            all_rows=[node_rows, edge_rows, profile_rows, rank_boundary_rows, operator_geometry_rows],
            condition_identity_rows=condition_identity_rows,
            scan_manifest_rows=scan_manifest_rows,
        ),
        audit_frontier_profile_reconstruction(node_rows, edge_rows, profile_rows),
        audit_rank_boundary_reconstruction(edge_rows, rank_boundary_rows),
        audit_adjacent_matrix_reconstruction(edge_rows, adjacent_manifest_rows, adjacent_matrices),
        audit_operator_geometry_reconstruction(rank_boundary_rows, operator_geometry_rows),
    ]


def audit_condition_identity_traceability(
    *,
    all_rows: list[list[dict[str, object]]],
    condition_identity_rows: list[dict[str, object]],
    scan_manifest_rows: list[dict[str, object]],
) -> dict[str, object]:
    by_condition = {str(row["condition_id"]): row for row in condition_identity_rows}
    by_scan = {str(row["scan_id"]): row for row in scan_manifest_rows}
    checked = 0
    failed = 0
    for rows in all_rows:
        for row in rows:
            condition_id = str(row.get("condition_id", ""))
            if not condition_id:
                continue
            checked += 1
            scan_identity = by_scan.get(str(row.get("scan_id", "")))
            identity = scan_identity or by_condition.get(condition_id)
            if identity is None:
                failed += 1
                continue
            if scan_identity is not None and condition_id != str(scan_identity.get("condition_id", "")):
                failed += 1
                continue
            for field in ("state_space_id", "law_id", "selection_operator_id", "observable_set_id", "frontier_scan_id"):
                if field in row and str(row.get(field, "")) != str(identity.get(field, "")):
                    failed += 1
                    break
    return audit_result(
        "condition_identity_traceability",
        checked,
        failed,
        "condition_id plus formal spec ids",
    )


def audit_frontier_profile_reconstruction(
    node_rows: list[dict[str, object]],
    edge_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
) -> dict[str, object]:
    nodes_by_scan_h: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    edges_by_scan_h: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in node_rows:
        nodes_by_scan_h[(str(row["scan_id"]), int(row["horizon"]))].append(row)
    for row in edge_rows:
        edges_by_scan_h[(str(row["scan_id"]), int(row["source_horizon"]))].append(row)
    checked = 0
    failed = 0
    skipped = 0
    for row in profile_rows:
        scan_id = str(row["scan_id"])
        horizon = int(row["horizon"])
        if row.get("node_artifact_status") != "complete" or row.get("edge_artifact_status") != "complete":
            skipped += 1
            continue
        checked += 1
        node_count = len(nodes_by_scan_h.get((scan_id, horizon), []))
        step_edges = edges_by_scan_h.get((scan_id, horizon), [])
        component_count, largest_fraction = component_summary_from_rows(
            nodes_by_scan_h.get((scan_id, horizon), []),
            step_edges,
        )
        if int(row["frontier_state_count"]) != node_count:
            failed += 1
            continue
        if int(row["frontier_edge_count"]) != len(step_edges):
            failed += 1
            continue
        if int(row["frontier_component_count"]) != component_count:
            failed += 1
            continue
        if not float_close(row["largest_component_fraction"], largest_fraction):
            failed += 1
    return audit_result(
        "frontier_profile_reconstructs_from_node_and_edge_rows",
        checked,
        failed,
        "skipped rows had non-complete artifact status",
        skipped,
    )


def audit_rank_boundary_reconstruction(
    edge_rows: list[dict[str, object]],
    rank_boundary_rows: list[dict[str, object]],
) -> dict[str, object]:
    edges_by_scan_target_h: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in edge_rows:
        edges_by_scan_target_h[(str(row["scan_id"]), int(row["target_horizon"]))].append(row)
    checked = 0
    failed = 0
    for row in rank_boundary_rows:
        checked += 1
        edges = edges_by_scan_target_h.get((str(row["scan_id"]), int(row["horizon"])), [])
        reconstructed = rank_boundary_metrics(edges, int(row["rank_boundary_k"]))
        for field, value in reconstructed.items():
            if not float_close(row.get(field, ""), value):
                failed += 1
                break
    return audit_result(
        "rank_boundary_geometry_reconstructs_from_edge_rows",
        checked,
        failed,
        "edge rows carry candidate rank, energy, and rank-boundary flags",
    )


def audit_adjacent_matrix_reconstruction(
    edge_rows: list[dict[str, object]],
    adjacent_manifest_rows: list[dict[str, object]],
    adjacent_matrices: list[SparseMatrixRecord],
) -> dict[str, object]:
    edges_by_matrix_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in edge_rows:
        matrix_id = f"{row['scan_id']}__H{row['source_horizon']}_to_H{row['target_horizon']}"
        edges_by_matrix_id[matrix_id].append(row)
    matrices_by_id = {matrix.matrix_id: matrix for matrix in adjacent_matrices}
    checked = 0
    failed = 0
    for manifest_row in adjacent_manifest_rows:
        checked += 1
        matrix_id = str(manifest_row["matrix_id"])
        edges = edges_by_matrix_id.get(matrix_id, [])
        matrix = matrices_by_id.get(matrix_id)
        if matrix is None:
            failed += 1
            continue
        rows = {str(row["source_state_id"]) for row in edges}
        cols = {str(row["target_state_id"]) for row in edges}
        nonzeros = {(str(row["source_state_id"]), str(row["target_state_id"])) for row in edges}
        if int(manifest_row["row_item_count"]) != len(rows):
            failed += 1
            continue
        if int(manifest_row["column_item_count"]) != len(cols):
            failed += 1
            continue
        if int(manifest_row["nonzero_count"]) != len(nonzeros):
            failed += 1
            continue
        if int(manifest_row["nonzero_count"]) != len(matrix.values):
            failed += 1
            continue
        if not float_close(manifest_row["matrix_value_total"], float(len(edges))):
            failed += 1
    return audit_result(
        "adjacent_transport_matrices_reconstruct_from_edge_rows",
        checked,
        failed,
        "matrix values are path_count_or_edge_multiplicity for adjacent steps",
    )


def audit_operator_geometry_reconstruction(
    rank_boundary_rows: list[dict[str, object]],
    operator_geometry_rows: list[dict[str, object]],
) -> dict[str, object]:
    boundary_by_condition: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rank_boundary_rows:
        boundary_by_condition[str(row["condition_id"])].append(row)
    checked = 0
    failed = 0
    for row in operator_geometry_rows:
        checked += 1
        rows = [
            item for item in boundary_by_condition.get(str(row["condition_id"]), [])
            if int(item.get("inside_rank_boundary_edge_count", 0) or 0)
            + int(item.get("outside_rank_boundary_edge_count", 0) or 0) > 0
        ]
        if not rows:
            rows = boundary_by_condition.get(str(row["condition_id"]), [])
        inside_mean = mean_float([item["selected_inside_rank_boundary_fraction"] for item in rows])
        outside_mean = mean_float([item["selected_outside_rank_boundary_fraction"] for item in rows])
        rank_distance = rank_set_distance(row.get("retained_rank_set", ""), int(row["rank_boundary_k"]))
        operator_distance = "" if rank_distance == "" else (
            abs(1.0 - inside_mean) + abs(outside_mean) + float(rank_distance)
        ) / 3.0
        if not float_close(row["mean_selected_inside_rank_boundary_fraction"], inside_mean):
            failed += 1
            continue
        if not float_close(row["mean_selected_outside_rank_boundary_fraction"], outside_mean):
            failed += 1
            continue
        if not float_close(row["operator_rank_boundary_distance"], operator_distance):
            failed += 1
    return audit_result(
        "selection_operator_geometry_reconstructs_from_rank_boundary_rows",
        checked,
        failed,
        "rank-set distance comes from operator and observable parameters",
    )


def component_summary_from_rows(
    node_rows: list[dict[str, object]],
    edge_rows: list[dict[str, object]],
) -> tuple[int, float]:
    states = {str(row["state_id"]) for row in node_rows}
    if not states:
        return 0, 0.0
    adjacency: dict[str, set[str]] = {state: set() for state in states}
    sources_by_target: dict[str, list[str]] = defaultdict(list)
    for row in edge_rows:
        source = str(row["source_state_id"])
        if source in adjacency:
            sources_by_target[str(row["target_state_id"])].append(source)
    for sources in sources_by_target.values():
        for left in sources:
            for right in sources:
                if left != right:
                    adjacency[left].add(right)
    seen: set[str] = set()
    sizes: list[int] = []
    for state in sorted(states):
        if state in seen:
            continue
        stack = [state]
        seen.add(state)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        sizes.append(size)
    return len(sizes), max(sizes) / max(1, len(states))


def rank_boundary_metrics(edges: list[dict[str, object]], rank_boundary_k: int) -> dict[str, object]:
    inside = 0
    outside = 0
    boundary = 0
    inside_energies: list[float] = []
    outside_energies: list[float] = []
    for row in edges:
        candidate_rank = int(row["candidate_rank"])
        if int(row["inside_rank_boundary_flag"]):
            inside += 1
            inside_energies.append(float(row["candidate_energy"]))
        if int(row["outside_rank_boundary_flag"]):
            outside += 1
            outside_energies.append(float(row["candidate_energy"]))
        boundary += int(candidate_rank in {rank_boundary_k, rank_boundary_k + 1})
    weakest_inside = max(inside_energies) if inside_energies else ""
    strongest_outside = min(outside_energies) if outside_energies else ""
    gap = (float(strongest_outside) - float(weakest_inside)) if strongest_outside != "" and weakest_inside != "" else ""
    total = max(1, inside + outside)
    return {
        "inside_rank_boundary_edge_count": inside,
        "outside_rank_boundary_edge_count": outside,
        "rank_boundary_edge_count": boundary,
        "weakest_inside_rank_boundary_energy": weakest_inside,
        "strongest_outside_rank_boundary_energy": strongest_outside,
        "rank_boundary_energy_gap": gap,
        "selected_inside_rank_boundary_fraction": inside / total,
        "selected_outside_rank_boundary_fraction": outside / total,
    }


def rank_set_distance(raw: object, rank_boundary_k: int) -> object:
    retained = {int(token) for token in str(raw or "").split(";") if token.strip()}
    if not retained:
        return ""
    target = set(range(1, rank_boundary_k + 1))
    return 1.0 - len(retained & target) / max(1, len(retained | target))


def audit_result(
    audit_name: str,
    checked: int,
    failed: int,
    detail: str,
    skipped: int = 0,
) -> dict[str, object]:
    return {
        "audit_name": audit_name,
        "status": "PASS" if failed == 0 else "FAIL",
        "checked_items": checked,
        "failed_items": failed,
        "skipped_items": skipped,
        "detail": detail,
    }


def mean_float(values: list[object]) -> float:
    numeric = [float(value) for value in values if value != ""]
    return sum(numeric) / len(numeric) if numeric else 0.0


def float_close(left: object, right: object) -> bool:
    if left == "" or right == "":
        return left == right
    return abs(float(left) - float(right)) <= FLOAT_TOLERANCE
