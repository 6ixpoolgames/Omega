from __future__ import annotations

from .util import safe_token, stable_hash


def lossless_topology_blocks(
    rows: list[dict[str, object]],
    *,
    logical_artifact_name: str,
    row_kind: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if row_kind not in {"nodes", "edges"}:
        raise ValueError(f"unsupported lossless topology row kind: {row_kind}")
    horizon_field = "horizon" if row_kind == "nodes" else "source_horizon"
    grouped: dict[tuple[str, str], dict[int, list[dict[str, object]]]] = {}
    for row in rows:
        key = (str(row["pair_id"]), str(row["joint_scan_mode"]))
        horizon = int(row[horizon_field])
        grouped.setdefault(key, {}).setdefault(horizon, []).append(row)

    block_rows: list[dict[str, object]] = []
    manifest_rows: list[dict[str, object]] = []
    block_index = 0
    for (pair_id, mode), by_horizon in sorted(grouped.items()):
        active_start: int | None = None
        active_end: int | None = None
        active_signature = ""
        active_rows: list[dict[str, object]] = []
        for horizon in sorted(by_horizon):
            representative_rows = by_horizon[horizon]
            signature = topology_block_signature(representative_rows, row_kind)
            if active_start is None:
                active_start = horizon
                active_end = horizon
                active_signature = signature
                active_rows = representative_rows
                continue
            if horizon == int(active_end) + 1 and signature == active_signature:
                active_end = horizon
                continue
            block_index = append_lossless_topology_block(
                block_rows=block_rows,
                manifest_rows=manifest_rows,
                block_index=block_index,
                logical_artifact_name=logical_artifact_name,
                row_kind=row_kind,
                pair_id=pair_id,
                mode=mode,
                horizon_start=int(active_start),
                horizon_end=int(active_end),
                representative_rows=active_rows,
                signature=active_signature,
            )
            active_start = horizon
            active_end = horizon
            active_signature = signature
            active_rows = representative_rows
        if active_start is not None and active_end is not None:
            block_index = append_lossless_topology_block(
                block_rows=block_rows,
                manifest_rows=manifest_rows,
                block_index=block_index,
                logical_artifact_name=logical_artifact_name,
                row_kind=row_kind,
                pair_id=pair_id,
                mode=mode,
                horizon_start=int(active_start),
                horizon_end=int(active_end),
                representative_rows=active_rows,
                signature=active_signature,
            )
    return block_rows, manifest_rows


def expand_lossless_topology_blocks(
    block_rows: list[dict[str, object]],
    *,
    row_kind: str,
) -> list[dict[str, object]]:
    expanded: list[dict[str, object]] = []
    for row in block_rows:
        horizon_start = int(row["horizon_start"])
        horizon_end = int(row["horizon_end"])
        for horizon in range(horizon_start, horizon_end + 1):
            logical_row = {
                key: value
                for key, value in row.items()
                if key not in lossless_block_metadata_fields()
            }
            if row_kind == "nodes":
                logical_row["horizon"] = horizon
            elif row_kind == "edges":
                logical_row["source_horizon"] = horizon
                logical_row["target_horizon"] = horizon + 1
            else:
                raise ValueError(f"unsupported lossless topology row kind: {row_kind}")
            expanded.append(logical_row)
    return expanded


def physical_raw_row_count(
    raw_topology_output_mode: str,
    logical_rows: list[dict[str, object]],
    shard_manifest: list[dict[str, object]],
    block_rows: list[dict[str, object]],
) -> int:
    if raw_topology_output_mode == "lossless_blocks":
        return len(block_rows)
    if raw_topology_output_mode in {"sharded", "both"}:
        return sum(int(row["row_count"]) for row in shard_manifest)
    return len(logical_rows)


def compression_ratio(*, logical_rows: int, physical_rows: int) -> float:
    if physical_rows <= 0:
        return 0.0
    return round(logical_rows / physical_rows, 3)


def topology_block_signature(rows: list[dict[str, object]], row_kind: str) -> str:
    excluded = {"horizon"} if row_kind == "nodes" else {"source_horizon", "target_horizon"}
    normalized = [
        {key: value for key, value in row.items() if key not in excluded}
        for row in rows
    ]
    return stable_hash(normalized, length=20)


def append_lossless_topology_block(
    *,
    block_rows: list[dict[str, object]],
    manifest_rows: list[dict[str, object]],
    block_index: int,
    logical_artifact_name: str,
    row_kind: str,
    pair_id: str,
    mode: str,
    horizon_start: int,
    horizon_end: int,
    representative_rows: list[dict[str, object]],
    signature: str,
) -> int:
    horizon_count = horizon_end - horizon_start + 1
    block_id = (
        f"{safe_token(logical_artifact_name)}__{safe_token(pair_id)}"
        f"__{mode}__b{block_index:06d}"
    )
    for row in representative_rows:
        block_row = dict(row)
        block_row.update({
            "lossless_block_id": block_id,
            "lossless_block_index": block_index,
            "artifact_storage_kind": "lossless_repeated_horizon_block_csv",
            "storage_artifact_status": "lossless_compressed",
            "horizon_start": horizon_start,
            "horizon_end": horizon_end,
            "horizon_count": horizon_count,
            "logical_row_repeat_count": horizon_count,
            "block_signature": signature,
        })
        if row_kind == "edges":
            block_row.update({
                "source_horizon_start": horizon_start,
                "source_horizon_end": horizon_end,
                "target_horizon_start": horizon_start + 1,
                "target_horizon_end": horizon_end + 1,
            })
        block_rows.append(block_row)
    manifest_rows.append({
        "logical_artifact_name": logical_artifact_name,
        "artifact_storage_kind": "lossless_repeated_horizon_block_csv",
        "storage_artifact_status": "lossless_compressed",
        "lossless_block_id": block_id,
        "lossless_block_index": block_index,
        "pair_id": pair_id,
        "joint_scan_mode": mode,
        "row_kind": row_kind,
        "horizon_start": horizon_start,
        "horizon_end": horizon_end,
        "horizon_count": horizon_count,
        "stored_row_count": len(representative_rows),
        "logical_row_count": len(representative_rows) * horizon_count,
        "block_signature": signature,
        "reconstruction_rule": reconstruction_rule_for_row_kind(row_kind),
    })
    return block_index + 1


def lossless_block_metadata_fields() -> set[str]:
    return {
        "lossless_block_id",
        "lossless_block_index",
        "artifact_storage_kind",
        "storage_artifact_status",
        "horizon_start",
        "horizon_end",
        "horizon_count",
        "logical_row_repeat_count",
        "block_signature",
        "source_horizon_start",
        "source_horizon_end",
        "target_horizon_start",
        "target_horizon_end",
    }


def reconstruction_rule_for_row_kind(row_kind: str) -> str:
    if row_kind == "nodes":
        return "expand block rows over each integer horizon in [horizon_start,horizon_end]"
    if row_kind == "edges":
        return (
            "expand block rows over each integer source_horizon in "
            "[horizon_start,horizon_end] and set target_horizon=source_horizon+1"
        )
    raise ValueError(f"unsupported lossless topology row kind: {row_kind}")
