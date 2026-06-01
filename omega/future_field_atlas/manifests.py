from __future__ import annotations

from .contracts import MappedScan, spec_canonical_json, spec_digest
from .util import canonical_json, stable_hash


def formal_spec_manifest_rows(scans: list[MappedScan]) -> list[dict[str, object]]:
    seen: set[tuple[str, str]] = set()
    rows: list[dict[str, object]] = []
    for scan in scans:
        spec = scan.raw.spec
        frontier_scan = scan.raw.frontier_scan
        for spec_type, spec_id, spec_obj, params_json in (
            ("state_space", spec.state_space.state_space_id, spec.state_space, spec.state_space.state_space_params_json),
            ("transformation_law", spec.transformation_law.law_id, spec.transformation_law, spec.transformation_law.law_params_json),
            ("selection_operator", spec.selection_operator.selection_operator_id, spec.selection_operator, spec.selection_operator.operator_params_json),
            ("observable", spec.observable.observable_set_id, spec.observable, spec.observable.observable_params_json),
            ("frontier_scan", frontier_scan.frontier_scan_id, frontier_scan, frontier_scan.frontier_scan_params_json),
        ):
            key = (spec_type, spec_id)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "spec_type": spec_type,
                "spec_id": spec_id,
                "spec_digest": spec_digest(spec_obj),
                "params_json": params_json,
                "canonical_json": spec_canonical_json(spec_obj),
            })
    return sorted(rows, key=lambda row: (str(row["spec_type"]), str(row["spec_id"])))


def condition_identity_manifest_rows(scans: list[MappedScan]) -> list[dict[str, object]]:
    seen: set[str] = set()
    rows: list[dict[str, object]] = []
    for scan in scans:
        spec = scan.raw.spec
        if spec.condition_id in seen:
            continue
        seen.add(spec.condition_id)
        payload = {
            "condition_id": spec.condition_id,
            "group_id": spec.group_id,
            "seed": spec.seed,
            "seed_policy": spec.transformation_law.seed_policy,
            "substrate_id": spec.substrate_id,
            "state_space_id": spec.state_space.state_space_id,
            "state_space_digest": spec_digest(spec.state_space),
            "law_id": spec.transformation_law.law_id,
            "law_digest": spec_digest(spec.transformation_law),
            "selection_operator_id": spec.selection_operator.selection_operator_id,
            "selection_operator_digest": spec_digest(spec.selection_operator),
            "observable_set_id": spec.observable.observable_set_id,
            "observable_digest": spec_digest(spec.observable),
            "frontier_scan_id": scan.raw.frontier_scan.frontier_scan_id,
            "frontier_scan_digest": spec_digest(scan.raw.frontier_scan),
        }
        identity_json = canonical_json(payload)
        rows.append({
            **payload,
            "condition_identity_digest": stable_hash(identity_json, length=20),
            "condition_identity_json": identity_json,
        })
    return sorted(rows, key=lambda row: str(row["condition_id"]))
