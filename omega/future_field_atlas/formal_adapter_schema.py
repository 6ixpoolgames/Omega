"""Shared schema and helper definitions for the FFA formal adapter package."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ADAPTER_ID = "ffa_finite_reachable_frontier_support_v0"
ADAPTER_SCHEMA_VERSION = "0.1.0"
PRESENTATION_TYPE = "finite reachable-future support presentation"
SUBSTRATE_STATUS = "finite-transition / frontier-support adapter"
CLAIM_BOUNDARY = (
    "adapter formalization only; no Omega validation, no proto-valuer detection, "
    "no valuer detection, no compatibility detection, no support/capture/erasure detection"
)
DEFAULT_INPUT_PANEL = Path("results/future_field_atlas/20260603_formal_interface_distinction_panel")
DEFAULT_OUT = Path("results/future_field_atlas/20260603_formal_adapter_conformance_package")
CORE_OPERATOR_LABELS = (
    "product_selector",
    "zero_penalty_joint_rank_prefix",
    "scalar_mismatch_0.020",
    "shared_capacity_v1",
    "rank_order_boundary",
)
DELTA_REFERENCE_BY_TOKEN = {
    "residual_delta_vs_product_positive": "product_selector",
    "residual_delta_vs_zero_penalty_joint_rank_prefix_positive": "zero_penalty_joint_rank_prefix",
    "residual_delta_vs_scalar_0.020_positive": "scalar_mismatch_0.020",
    "residual_delta_vs_shared_capacity_v1_positive": "shared_capacity_v1",
}


@dataclass(frozen=True)
class ContextKey:
    pair_id: str
    operator_id: str
    observable_id: str
    horizon: int

@dataclass(frozen=True)
class TokenKey:
    context_id: str
    distinction_id: str

@dataclass(frozen=True)
class TransportKey:
    unfolding_id: str
    source_context_id: str
    target_context_id: str
    source_distinction_id: str
    target_distinction_id: str

def context_id_for(key: ContextKey) -> str:
    return f"ctx::{key.pair_id}::{safe_id(key.operator_id)}::{safe_id(key.observable_id)}::h{key.horizon}"

def source_row_id(context: dict[str, object], token: str) -> str:
    return f"{context['context_id']}::{token}"

def token_for_delta_reference(reference: str) -> str:
    for token, ref in DELTA_REFERENCE_BY_TOKEN.items():
        if ref == reference:
            return token
    return ""

def csv_artifact_name(logical_name: str, csv_output_mode: str) -> str:
    if csv_output_mode == "gzip" and logical_name.endswith(".csv"):
        return f"{logical_name}.gz"
    return logical_name

def safe_id(value: object) -> str:
    return str(value).replace(" ", "_").replace("/", "_").replace("\\", "_")

def transitive_closure(pairs: set[tuple[str, str]]) -> set[tuple[str, str]]:
    closure = set(pairs)
    changed = True
    while changed:
        changed = False
        for a, b in list(closure):
            for c, d in list(closure):
                if b == c and (a, d) not in closure:
                    closure.add((a, d))
                    changed = True
    return closure

def dedup_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[tuple[tuple[str, str], ...]] = set()
    out = []
    for row in rows:
        key = tuple(sorted((str(k), str(v)) for k, v in row.items()))
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out

def count_by(rows: Iterable[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[str(row.get(field, ""))] += 1
    return dict(counts)

def truthy(row: dict[str, object]) -> bool:
    return str(row.get("truth_value", "")).lower() in ("1", "true")

def floatish(value: object) -> float:
    try:
        if value in ("", None):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def intish(value: object) -> int:
    try:
        if value in ("", None):
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0
