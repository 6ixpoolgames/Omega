"""Compile small finite grid sources into finite relational adapter models."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.derived_graph import compile_derived_graph
from omega.adapters.finite_relational.model import SchemaError, load_model
from omega.adapters.finite_relational.source_contract import assert_no_reserved_ir_fields


def load_finite_grid_path(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_finite_grid_path(path: Path) -> dict[str, Any]:
    return compile_finite_grid(load_finite_grid_path(path))


def compile_finite_grid(raw: dict[str, Any]) -> dict[str, Any]:
    """Compile a finite rectangular grid source through the relational IR."""

    assert_no_reserved_ir_fields(raw, source_kind="finite grid")
    model_id = str(raw.get("model_id", "finite_grid"))
    width = _positive_int(raw.get("width"), "width")
    height = _positive_int(raw.get("height"), "height")
    blocked = set(_coordinate_list(raw.get("blocked", []), width=width, height=height, label="blocked"))
    cells = [cell for cell in _grid_cells(width, height) if cell not in blocked]
    cell_set = set(cells)
    movement_rule = str(raw.get("movement_rule", "orthogonal"))
    observations = _total_mappings(raw.get("observations", {}), cell_set, "observation")
    presentations = _total_mappings(raw.get("presentations", {}), cell_set, "presentation")
    safety = _safety(raw.get("safety", "all"), cell_set)
    provenance = _dict(raw.get("provenance", {}), "provenance")
    graph_source = {
        "model_id": model_id,
        "nodes": cells,
        "edges": [list(edge) for edge in _movement_edges(cells, movement_rule)],
        "observations": observations,
        "presentations": presentations,
        "presentation_expectations": _dict(
            raw.get("presentation_expectations", {}),
            "presentation_expectations",
        ),
        "safety": safety,
        "provenance": provenance
        | {
            "source_compiler": "finite_grid",
            "grid_digest": _digest_json(raw),
        },
    }
    compiled = compile_derived_graph(graph_source)
    compiled["model_id"] = f"compiled_{model_id}"
    compiled["provenance"] = compiled["provenance"] | {
        "compiled_from": "finite_grid",
        "intermediate_compiler": "derived_graph",
        "source_model_id": model_id,
        "grid_width": width,
        "grid_height": height,
        "movement_rule": movement_rule,
        "blocked": sorted(blocked),
        "grid_derivation_rules": [
            "cells=rectangular_grid_minus_blocked",
            f"edges=movement_rule:{movement_rule}",
            "then=derived_graph_rules",
        ],
    }
    load_model(compiled)
    return compiled


def _movement_edges(cells: list[str], movement_rule: str) -> list[tuple[str, str]]:
    cell_set = set(cells)
    if movement_rule == "orthogonal":
        deltas = ((1, 0), (-1, 0), (0, 1), (0, -1))
    elif movement_rule == "east":
        deltas = ((1, 0),)
    elif movement_rule == "east_south":
        deltas = ((1, 0), (0, 1))
    else:
        raise SchemaError(f"unknown finite grid movement_rule: {movement_rule}")
    edges = []
    for cell in cells:
        x, y = _parse_coord(cell)
        for dx, dy in deltas:
            target = _coord(x + dx, y + dy)
            if target in cell_set:
                edges.append((cell, target))
    return sorted(edges)


def _grid_cells(width: int, height: int) -> list[str]:
    return [_coord(x, y) for y in range(height) for x in range(width)]


def _coord(x: int, y: int) -> str:
    return f"{x},{y}"


def _parse_coord(value: str) -> tuple[int, int]:
    try:
        x_raw, y_raw = value.split(",", maxsplit=1)
        return int(x_raw), int(y_raw)
    except ValueError as exc:
        raise SchemaError(f"invalid finite grid coordinate: {value!r}") from exc


def _coordinate_list(value: Any, *, width: int, height: int, label: str) -> list[str]:
    if not isinstance(value, list):
        raise SchemaError(f"{label} must be a list")
    coords = [str(item) for item in value]
    for coord in coords:
        x, y = _parse_coord(coord)
        if x < 0 or y < 0 or x >= width or y >= height:
            raise SchemaError(f"{label} coordinate is outside grid: {coord}")
    if len(set(coords)) != len(coords):
        raise SchemaError(f"{label} must not contain duplicates")
    return coords


def _safety(value: Any, cells: set[str]) -> str | list[str]:
    if value == "all":
        return "all"
    safety = [str(item) for item in _list(value, "safety")]
    bad = sorted(set(safety) - cells)
    if bad:
        raise SchemaError(f"safety references cells outside active grid: {bad}")
    return safety


def _total_mappings(value: Any, cells: set[str], label: str) -> dict[str, dict[str, str]]:
    raw = _dict(value, f"{label}s")
    mappings = {}
    for name, mapping_value in raw.items():
        mapping = {str(key): str(target) for key, target in _dict(mapping_value, f"{label} {name}").items()}
        missing = sorted(cells - set(mapping))
        extra = sorted(set(mapping) - cells)
        if missing:
            raise SchemaError(f"{label} {name} is missing active cells: {missing}")
        if extra:
            raise SchemaError(f"{label} {name} has cells outside active grid: {extra}")
        mappings[str(name)] = mapping
    return mappings


def _positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise SchemaError(f"{label} must be a positive integer")
    return value


def _dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise SchemaError(f"{label} must be a list")
    return value


def _digest_json(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()
