from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from omega.rfs_mb0_future_landscape.substrate import State

from .contracts import MappedScan
from .util import state_id


@dataclass(frozen=True)
class SparseMatrixRecord:
    matrix_id: str
    scan_id: str
    condition_id: str
    source_horizon: int
    target_horizon: int
    row_labels: tuple[str, ...]
    column_labels: tuple[str, ...]
    row_indices: tuple[int, ...]
    column_indices: tuple[int, ...]
    values: tuple[float, ...]


def adjacent_transport_matrices(scans: list[MappedScan]) -> list[SparseMatrixRecord]:
    matrices: list[SparseMatrixRecord] = []
    for mapped in scans:
        raw = mapped.raw
        for horizon in range(raw.horizon_max):
            if horizon not in raw.horizon_schedule or horizon + 1 not in raw.horizon_schedule:
                continue
            matrices.append(matrix_from_edges(raw.scan_id, raw.spec.condition_id, horizon, horizon + 1, raw.step_edges.get(horizon, ())))
    return matrices


def multiscale_transport_matrices(scans: list[MappedScan], horizon_pairs: tuple[tuple[int, int], ...]) -> list[SparseMatrixRecord]:
    matrices: list[SparseMatrixRecord] = []
    for mapped in scans:
        raw = mapped.raw
        for source_h, target_h in horizon_pairs:
            if source_h >= target_h or source_h > raw.horizon_max or target_h > raw.horizon_max:
                continue
            entries = reachable_pairs(raw.frontiers[source_h], raw.step_edges, source_h, target_h)
            matrices.append(matrix_from_edges(raw.scan_id, raw.spec.condition_id, source_h, target_h, tuple(entries)))
    return matrices


def matrix_from_edges(
    scan_id: str,
    condition_id: str,
    source_horizon: int,
    target_horizon: int,
    edges: tuple[tuple[State, State], ...],
) -> SparseMatrixRecord:
    rows = tuple(sorted({state_id(source) for source, _target in edges}))
    cols = tuple(sorted({state_id(target) for _source, target in edges}))
    row_index = {label: index for index, label in enumerate(rows)}
    col_index = {label: index for index, label in enumerate(cols)}
    counts: dict[tuple[int, int], float] = {}
    for source, target in edges:
        key = (row_index[state_id(source)], col_index[state_id(target)])
        counts[key] = counts.get(key, 0.0) + 1.0
    ordered = sorted(counts.items())
    return SparseMatrixRecord(
        matrix_id=f"{scan_id}__H{source_horizon}_to_H{target_horizon}",
        scan_id=scan_id,
        condition_id=condition_id,
        source_horizon=source_horizon,
        target_horizon=target_horizon,
        row_labels=rows,
        column_labels=cols,
        row_indices=tuple(indexes[0] for indexes, _value in ordered),
        column_indices=tuple(indexes[1] for indexes, _value in ordered),
        values=tuple(value for _indexes, value in ordered),
    )


def reachable_pairs(
    source_frontier: frozenset[State],
    step_edges: dict[int, tuple[tuple[State, State], ...]],
    source_horizon: int,
    target_horizon: int,
) -> list[tuple[State, State]]:
    active: dict[State, set[State]] = {origin: {origin} for origin in source_frontier}
    for horizon in range(source_horizon, target_horizon):
        outgoing: dict[State, set[State]] = {}
        for source, target in step_edges.get(horizon, ()):
            outgoing.setdefault(source, set()).add(target)
        next_active: dict[State, set[State]] = {origin: set() for origin in active}
        for origin, current_states in active.items():
            for current in current_states:
                next_active[origin].update(outgoing.get(current, set()))
        active = next_active
    return [(origin, target) for origin, targets in active.items() for target in targets]


def matrix_manifest_rows(matrices: list[SparseMatrixRecord]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        total = sum(matrix.values)
        rows.append({
            "matrix_id": matrix.matrix_id,
            "scan_id": matrix.scan_id,
            "condition_id": matrix.condition_id,
            "source_horizon": matrix.source_horizon,
            "target_horizon": matrix.target_horizon,
            "row_item_count": len(matrix.row_labels),
            "column_item_count": len(matrix.column_labels),
            "nonzero_count": len(matrix.values),
            "matrix_value_semantics": "path_count_or_edge_multiplicity",
            "matrix_value_total": total,
            "dropped_entry_count_due_to_artifact_policy": 0,
        })
    return rows


def flow_composition_residual_rows(matrices: list[SparseMatrixRecord]) -> list[dict[str, object]]:
    by_key = {(m.scan_id, m.condition_id, m.source_horizon, m.target_horizon): m for m in matrices}
    rows: list[dict[str, object]] = []
    horizons_by_scan: dict[tuple[str, str], set[int]] = {}
    for matrix in matrices:
        horizons_by_scan.setdefault((matrix.scan_id, matrix.condition_id), set()).update(
            {matrix.source_horizon, matrix.target_horizon}
        )
    for scan_key, horizons in sorted(horizons_by_scan.items()):
        ordered = sorted(horizons)
        for source_h in ordered:
            for mid_h in ordered:
                for target_h in ordered:
                    if not source_h < mid_h < target_h:
                        continue
                    direct = by_key.get((*scan_key, source_h, target_h))
                    left = by_key.get((*scan_key, source_h, mid_h))
                    right = by_key.get((*scan_key, mid_h, target_h))
                    if direct is None or left is None or right is None:
                        continue
                    residual = composition_residual(direct, left, right)
                    rows.append({
                        "scan_id": scan_key[0],
                        "condition_id": scan_key[1],
                        "source_horizon": source_h,
                        "mid_horizon": mid_h,
                        "target_horizon": target_h,
                        "direct_matrix_id": direct.matrix_id,
                        "left_matrix_id": left.matrix_id,
                        "right_matrix_id": right.matrix_id,
                        **residual,
                    })
    return rows


def composition_residual(
    direct: SparseMatrixRecord,
    left: SparseMatrixRecord,
    right: SparseMatrixRecord,
) -> dict[str, object]:
    direct_rows = list(direct.row_labels)
    direct_cols = list(direct.column_labels)
    left_rows = list(left.row_labels)
    left_cols = list(left.column_labels)
    right_rows = list(right.row_labels)
    right_cols = list(right.column_labels)
    status = "ok"
    if direct_rows != left_rows or direct_cols != right_cols:
        status = "label_mismatch_union_aligned"
    source_labels = sorted(set(direct_rows) | set(left_rows))
    target_labels = sorted(set(direct_cols) | set(right_cols))
    mid_labels = sorted(set(left_cols) | set(right_rows))
    left_dense = dense_matrix(left, source_labels, mid_labels)
    right_dense = dense_matrix(right, mid_labels, target_labels)
    direct_dense = dense_matrix(direct, source_labels, target_labels)
    composed_path_count = left_dense @ right_dense
    composed = composed_path_count > 0
    direct_bool = direct_dense > 0
    support_diff = direct_bool.astype(float) - composed.astype(float)
    support_residual_l1 = float(np.abs(support_diff).sum())
    support_residual_fro = float(np.sqrt((support_diff * support_diff).sum()))
    direct_support_weight = float(direct_bool.sum())
    path_count_diff = direct_dense - composed_path_count
    path_count_residual_l1 = float(np.abs(path_count_diff).sum())
    path_count_residual_fro = float(np.sqrt((path_count_diff * path_count_diff).sum()))
    direct_weight = float(direct_dense.sum())
    return {
        "composition_status": status,
        "composition_kind": "support_and_path_count_unit_edge_weight",
        "support_composition_status": status,
        "support_composition_residual_l1": support_residual_l1,
        "support_composition_residual_frobenius": support_residual_fro,
        "support_composition_residual_fraction": support_residual_l1 / max(1.0, direct_support_weight),
        "support_rank_direct": int(np.linalg.matrix_rank(direct_bool)),
        "support_rank_composed": int(np.linalg.matrix_rank(composed)),
        "path_count_composition_status": status,
        "path_count_composition_residual_l1": path_count_residual_l1,
        "path_count_composition_residual_frobenius": path_count_residual_fro,
        "path_count_composition_residual_fraction": path_count_residual_l1 / max(1.0, direct_weight),
        "path_count_rank_direct": int(np.linalg.matrix_rank(direct_dense)),
        "path_count_rank_composed": int(np.linalg.matrix_rank(composed_path_count)),
        "weighted_flow_composition_status": "not_defined_unit_edge_weights_only",
        "weighted_flow_composition_residual_l1": "",
        "weighted_flow_composition_residual_frobenius": "",
        "weighted_flow_composition_residual_fraction": "",
    }


def dense_matrix(matrix: SparseMatrixRecord, row_labels: list[str], col_labels: list[str]) -> np.ndarray:
    row_index = {label: index for index, label in enumerate(row_labels)}
    col_index = {label: index for index, label in enumerate(col_labels)}
    out = np.zeros((len(row_labels), len(col_labels)), dtype=float)
    for row_i, col_i, value in zip(matrix.row_indices, matrix.column_indices, matrix.values):
        row_label = matrix.row_labels[row_i]
        col_label = matrix.column_labels[col_i]
        if row_label in row_index and col_label in col_index:
            out[row_index[row_label], col_index[col_label]] += value
    return out


def write_sparse_npz(path: Path, matrices: list[SparseMatrixRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    matrix_ids: list[str] = []
    entry_matrix_index: list[int] = []
    row_indices: list[int] = []
    col_indices: list[int] = []
    values: list[float] = []
    row_label_matrix_index: list[int] = []
    row_labels: list[str] = []
    col_label_matrix_index: list[int] = []
    col_labels: list[str] = []
    for matrix_index, matrix in enumerate(matrices):
        matrix_ids.append(matrix.matrix_id)
        for row_label in matrix.row_labels:
            row_label_matrix_index.append(matrix_index)
            row_labels.append(row_label)
        for col_label in matrix.column_labels:
            col_label_matrix_index.append(matrix_index)
            col_labels.append(col_label)
        for row_i, col_i, value in zip(matrix.row_indices, matrix.column_indices, matrix.values):
            entry_matrix_index.append(matrix_index)
            row_indices.append(row_i)
            col_indices.append(col_i)
            values.append(value)
    np.savez_compressed(
        path,
        matrix_ids=np.array(matrix_ids, dtype=str),
        entry_matrix_index=np.array(entry_matrix_index, dtype=np.int64),
        row_indices=np.array(row_indices, dtype=np.int64),
        col_indices=np.array(col_indices, dtype=np.int64),
        values=np.array(values, dtype=float),
        row_label_matrix_index=np.array(row_label_matrix_index, dtype=np.int64),
        row_labels=np.array(row_labels, dtype=str),
        col_label_matrix_index=np.array(col_label_matrix_index, dtype=np.int64),
        col_labels=np.array(col_labels, dtype=str),
    )
