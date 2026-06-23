"""Gridworld obstacle-insertion studies for finite relational audits."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import json
from hashlib import sha256
from typing import Any

from omega.adapters.finite_relational.audits import AuditResult, run_declared_audits
from omega.adapters.finite_relational.facts import Pair, reachable_pairs
from omega.adapters.finite_relational.model import SchemaError, load_model, model_digest


@dataclass(frozen=True)
class GridObstacleCase:
    """A generated grid source, compiled IR model, and audit results."""

    case_id: str
    source: dict[str, Any]
    compiled_model: dict[str, Any]
    audit_results: tuple[AuditResult, ...]

    @property
    def all_passed(self) -> bool:
        return all(result.passed for result in self.audit_results)

    def summary(self) -> dict[str, object]:
        model = load_model(self.compiled_model)
        return {
            "case_id": self.case_id,
            "source_digest": digest_json(self.source),
            "compiled_model_id": model.model_id,
            "compiled_model_digest": model_digest(model),
            "audit_count": len(self.audit_results),
            "passed_count": sum(1 for result in self.audit_results if result.passed),
            "all_passed": self.all_passed,
            "findings": [result.finding for result in self.audit_results],
        }


@dataclass(frozen=True)
class GridObstacleStudy:
    """A controlled grid obstacle-insertion study."""

    study_id: str
    description: str
    search_space: dict[str, object]
    metrics: dict[str, object]
    representative_cases: tuple[GridObstacleCase, ...]

    @property
    def all_passed(self) -> bool:
        return all(case.all_passed for case in self.representative_cases)

    def summary(self) -> dict[str, object]:
        return {
            "study_id": self.study_id,
            "description": self.description,
            "search_space": self.search_space,
            "metrics": self.metrics,
            "representative_case_count": len(self.representative_cases),
            "all_passed": self.all_passed,
            "representative_cases": [case.summary() for case in self.representative_cases],
        }


def generate_grid_obstacle_study() -> GridObstacleStudy:
    """Generate a small obstacle-insertion study over a declared 3x3 grid."""

    width = 3
    height = 3
    movement_rule = "orthogonal"
    source = "0,1"
    target = "2,1"
    before_blocked: tuple[str, ...] = ()
    candidates = tuple(
        cell for cell in _grid_cells(width, height) if cell not in {source, target}
    )
    obstacle_sets = tuple(
        subset
        for size in range(0, 4)
        for subset in combinations(candidates, size)
    )

    hidden_loss_sets = []
    no_loss_sets = []
    before_edges = _movement_edges(width, height, movement_rule, before_blocked)
    before_path = (source, target) in reachable_pairs(set(_grid_cells(width, height)), before_edges)
    if not before_path:
        raise AssertionError("declared before-grid must have a source-target path")

    for after_blocked in obstacle_sets:
        after_edges = _movement_edges(width, height, movement_rule, after_blocked)
        after_path = (source, target) in reachable_pairs(set(_grid_cells(width, height)), after_edges)
        if after_path:
            no_loss_sets.append(after_blocked)
        else:
            hidden_loss_sets.append(after_blocked)

    hidden_case_source = _grid_obstacle_source(
        model_id="grid_obstacle_vertical_barrier_hidden_loss",
        width=width,
        height=height,
        movement_rule=movement_rule,
        before_blocked=before_blocked,
        after_blocked=("1,0", "1,1", "1,2"),
        source=source,
        target=target,
        expectation="hidden_loss",
        include_reachability_closure_audits=True,
        claim_boundary=(
            "Generated gridworld obstacle insertion case: a vertical barrier removes "
            "the exact source-target path while the stale abstraction still reports it."
        ),
    )
    no_loss_case_source = _grid_obstacle_source(
        model_id="grid_obstacle_single_obstacle_no_hidden_loss",
        width=width,
        height=height,
        movement_rule=movement_rule,
        before_blocked=before_blocked,
        after_blocked=("1,0",),
        source=source,
        target=target,
        expectation="no_hidden_loss",
        include_reachability_closure_audits=True,
        claim_boundary=(
            "Generated gridworld obstacle insertion control: a single obstacle leaves "
            "an alternate exact source-target path, so hidden loss is not observed."
        ),
    )

    return GridObstacleStudy(
        study_id="grid_obstacle_insertion_hidden_loss",
        description=(
            "Enumerates obstacle insertions on a 3x3 orthogonal grid. Before dynamics "
            "uses the unobstructed grid; after dynamics removes cells; abstract "
            "dynamics is stale and still uses the before grid."
        ),
        search_space={
            "width": width,
            "height": height,
            "movement_rule": movement_rule,
            "source": source,
            "target": target,
            "candidate_obstacle_count": len(candidates),
            "obstacle_set_count": len(obstacle_sets),
            "max_obstacle_count": 3,
        },
        metrics={
            "before_path": before_path,
            "hidden_loss_set_count": len(hidden_loss_sets),
            "no_loss_set_count": len(no_loss_sets),
            "hidden_loss_fraction": f"{len(hidden_loss_sets)}/{len(obstacle_sets)}",
        },
        representative_cases=(
            _validated_case("grid_obstacle_hidden_loss", hidden_case_source),
            _validated_case("grid_obstacle_no_hidden_loss_control", no_loss_case_source),
        ),
    )


def compile_grid_obstacle_source(raw: dict[str, Any]) -> dict[str, Any]:
    """Compile a grid obstacle-insertion source into finite relational IR."""

    width = _positive_int(raw.get("width"), "width")
    height = _positive_int(raw.get("height"), "height")
    movement_rule = str(raw.get("movement_rule", "orthogonal"))
    source = str(raw.get("source"))
    target = str(raw.get("target"))
    cells = tuple(_grid_cells(width, height))
    if source not in cells or target not in cells:
        raise SchemaError("grid obstacle source/target must be grid cells")
    before_blocked = tuple(
        _coordinate_list(raw.get("before_blocked", []), width=width, height=height, label="before_blocked")
    )
    after_blocked = tuple(
        _coordinate_list(raw.get("after_blocked", []), width=width, height=height, label="after_blocked")
    )
    if source in after_blocked or target in after_blocked:
        raise SchemaError("after_blocked must not remove source or target")
    if source in before_blocked or target in before_blocked:
        raise SchemaError("before_blocked must not remove source or target")

    before_edges = _movement_edges(width, height, movement_rule, before_blocked)
    after_edges = _movement_edges(width, height, movement_rule, after_blocked)
    before_reachable = _reachable_from_source(cells, before_edges, source)
    after_reachable = _reachable_from_source(cells, after_edges, source)
    provenance = _dict(raw.get("provenance", {}), "provenance")
    audits: list[dict[str, Any]] = [
        {
            "id": "stale_grid_abstraction_hidden_loss",
            "kind": "hidden_reachability_loss",
            "before_transition": "before_next",
            "after_transition": "after_next",
            "abstract_transition": "abstract_next",
            "source": source,
            "target": target,
            "expect": str(raw.get("expect", "hidden_loss")),
        }
    ]
    if raw.get("include_reachability_closure_audits") is True:
        audits.extend(
            [
                {
                    "id": "reflected_grid_status_preserves_after_source_reachability",
                    "kind": "presentation_fact_closure",
                    "presentations": ["reflected_source_reach_status"],
                    "target_predicates": ["after_reachable_from_source", "all_states"],
                    "expected_common_target_predicates": [
                        "after_reachable_from_source",
                        "all_states",
                    ],
                    "expect": "closure_ok",
                },
                {
                    "id": "stale_reflected_grid_status_drops_after_source_reachability",
                    "kind": "presentation_fact_closure",
                    "presentations": [
                        "stale_source_reach_status",
                        "reflected_source_reach_status",
                    ],
                    "target_predicates": ["after_reachable_from_source", "all_states"],
                    "expected_common_target_predicates": ["all_states"],
                    "expected_absent_target_predicates": ["after_reachable_from_source"],
                    "expect": "closure_ok",
                },
            ]
        )
    model = {
        "model_id": f"compiled_{raw.get('model_id', 'grid_obstacle')}",
        "schema_version": "0.1.0",
        "carrier": list(cells),
        "predicates": {
            "before_active": [cell for cell in cells if cell not in before_blocked],
            "after_active": [cell for cell in cells if cell not in after_blocked],
            "before_reachable_from_source": sorted(before_reachable),
            "after_reachable_from_source": sorted(after_reachable),
            "all_states": list(cells),
        },
        "relations": {
            "before_next": [list(edge) for edge in sorted(before_edges)],
            "after_next": [list(edge) for edge in sorted(after_edges)],
            "abstract_next": [list(edge) for edge in sorted(before_edges)],
        },
        "functions": {
            "stale_source_reach_status": {
                cell: ("reachable_from_source" if cell in before_reachable else "unreachable_from_source")
                for cell in cells
            },
            "reflected_source_reach_status": {
                cell: ("reachable_from_source" if cell in after_reachable else "unreachable_from_source")
                for cell in cells
            },
        },
        "audits": audits,
        "provenance": provenance
        | {
            "compiled_from": "grid_obstacle_insertion",
            "source_model_id": str(raw.get("model_id", "grid_obstacle")),
            "source_digest": digest_json(raw),
            "grid_width": width,
            "grid_height": height,
            "movement_rule": movement_rule,
            "before_blocked": list(before_blocked),
            "after_blocked": list(after_blocked),
            "derivation_rules": [
                "before_next=grid_movement_minus_before_blocked",
                "after_next=grid_movement_minus_after_blocked",
                "abstract_next=before_next_stale_abstraction",
                "audit=hidden_reachability_loss(source,target)",
                "source_reach_status=transitive_reachability_from_declared_source",
                "optional_audits=presentation_fact_closure(stale,reflected)",
            ],
        },
    }
    load_model(model)
    return model


def digest_json(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _validated_case(case_id: str, source: dict[str, Any]) -> GridObstacleCase:
    compiled = compile_grid_obstacle_source(source)
    model = load_model(compiled)
    audit_results = tuple(run_declared_audits(model))
    if not audit_results:
        raise AssertionError(f"{case_id} generated no audits")
    if not all(result.passed for result in audit_results):
        failures = [result.as_dict() for result in audit_results if not result.passed]
        raise AssertionError(f"{case_id} generated failing audits: {failures}")
    return GridObstacleCase(
        case_id=case_id,
        source=source,
        compiled_model=compiled,
        audit_results=audit_results,
    )


def _grid_obstacle_source(
    *,
    model_id: str,
    width: int,
    height: int,
    movement_rule: str,
    before_blocked: tuple[str, ...],
    after_blocked: tuple[str, ...],
    source: str,
    target: str,
    expectation: str,
    include_reachability_closure_audits: bool,
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "width": width,
        "height": height,
        "movement_rule": movement_rule,
        "before_blocked": list(before_blocked),
        "after_blocked": list(after_blocked),
        "source": source,
        "target": target,
        "expect": expectation,
        "include_reachability_closure_audits": include_reachability_closure_audits,
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.grid_obstacle_experiment",
            "claim_boundary": claim_boundary,
            "fixture_intent": "controlled gridworld obstacle insertion pilot",
        },
    }


def _movement_edges(
    width: int,
    height: int,
    movement_rule: str,
    blocked: tuple[str, ...],
) -> set[Pair]:
    active = set(_grid_cells(width, height)) - set(blocked)
    if movement_rule == "orthogonal":
        deltas = ((1, 0), (-1, 0), (0, 1), (0, -1))
    elif movement_rule == "east":
        deltas = ((1, 0),)
    elif movement_rule == "east_south":
        deltas = ((1, 0), (0, 1))
    else:
        raise SchemaError(f"unknown grid obstacle movement_rule: {movement_rule}")
    edges = set()
    for cell in active:
        x, y = _parse_coord(cell)
        for dx, dy in deltas:
            target = _coord(x + dx, y + dy)
            if target in active:
                edges.add((cell, target))
    return edges


def _reachable_from_source(
    cells: tuple[str, ...],
    edges: set[Pair],
    source: str,
) -> set[str]:
    return {
        target
        for start, target in reachable_pairs(set(cells), edges)
        if start == source
    }


def _grid_cells(width: int, height: int) -> list[str]:
    return [_coord(x, y) for y in range(height) for x in range(width)]


def _coord(x: int, y: int) -> str:
    return f"{x},{y}"


def _parse_coord(value: str) -> tuple[int, int]:
    try:
        x_raw, y_raw = value.split(",", maxsplit=1)
        return int(x_raw), int(y_raw)
    except ValueError as exc:
        raise SchemaError(f"invalid grid obstacle coordinate: {value!r}") from exc


def _coordinate_list(value: Any, *, width: int, height: int, label: str) -> list[str]:
    if not isinstance(value, list):
        raise SchemaError(f"{label} must be a list")
    coords = [str(item) for item in value]
    if len(set(coords)) != len(coords):
        raise SchemaError(f"{label} must not contain duplicates")
    for coord in coords:
        x, y = _parse_coord(coord)
        if x < 0 or y < 0 or x >= width or y >= height:
            raise SchemaError(f"{label} coordinate is outside grid: {coord}")
    return coords


def _positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise SchemaError(f"{label} must be a positive integer")
    return value


def _dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object")
    return value
