"""Transport witness, closure, and law-check construction."""

from __future__ import annotations

from collections import defaultdict

from .formal_adapter_schema import ADAPTER_ID, TokenKey, TransportKey, dedup_rows, truthy
from .util import stable_hash


def build_raw_witnesses(
    *,
    unfoldings: list[dict[str, object]],
    token_lookup: dict[TokenKey, dict[str, object]],
    preorder_by_context: dict[str, set[tuple[str, str]]],
    persistence_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    persistence_index = {
        (str(row["pair_id"]), str(row["operator_label"])): row
        for row in persistence_rows
        if row.get("window_id") == "full_window"
    }
    rows: list[dict[str, object]] = []
    for unfolding in unfoldings:
        if unfolding["unfolding_kind"] == "identity":
            continue
        source_context = str(unfolding["source_context_id"])
        target_context = str(unfolding["target_context_id"])
        source_tokens = {
            key.distinction_id: row
            for key, row in token_lookup.items()
            if key.context_id == source_context
        }
        target_tokens = {
            key.distinction_id: row
            for key, row in token_lookup.items()
            if key.context_id == target_context
        }
        for token, source_row in source_tokens.items():
            target_row = target_tokens.get(token)
            if target_row and truthy(source_row) and truthy(target_row):
                rows.append(
                    raw_witness_row(
                        unfolding=unfolding,
                        source_row=source_row,
                        target_row=target_row,
                        witness_kind="same_token_persistence",
                        evidence_rule="same finite-measure token true at source and target",
                    )
                )
        target_preorder = preorder_by_context.get(target_context, set())
        for source_token, source_row in source_tokens.items():
            if not truthy(source_row):
                continue
            for coarser, finer in target_preorder:
                if coarser != source_token or finer == source_token:
                    continue
                target_row = target_tokens.get(finer)
                if target_row and truthy(target_row):
                    rows.append(
                        raw_witness_row(
                            unfolding=unfolding,
                            source_row=source_row,
                            target_row=target_row,
                            witness_kind="refinement_persistence",
                            evidence_rule="source token true and declared finer target token true",
                        )
                    )
        if unfolding["unfolding_kind"] == "horizon_to_final":
            pkey = (str(unfolding["pair_id"]), str(unfolding["operator_id"]))
            persistence = persistence_index.get(pkey)
            if persistence and str(persistence.get("final_signature_status")) == "marginal_preserving_joint_restrictive":
                source_row = source_tokens.get("marginal_preserving_joint_restrictive")
                target_row = target_tokens.get("high_yield_signature")
                if source_row and target_row and truthy(source_row) and truthy(target_row):
                    rows.append(
                        raw_witness_row(
                            unfolding=unfolding,
                            source_row=source_row,
                            target_row=target_row,
                            witness_kind="horizon_signature_persistence",
                            evidence_rule="backed by horizon_signature_persistence.csv full_window/final status",
                        )
                    )
    # Stable de-duplication.
    dedup: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for row in rows:
        key = (
            str(row["unfolding_id"]),
            str(row["source_distinction_id"]),
            str(row["target_distinction_id"]),
            str(row["witness_kind"]),
        )
        dedup.setdefault(key, row)
    return [
        {**row, "witness_id": f"wit::{stable_hash(key, length=20)}"}
        for key, row in sorted(dedup.items())
    ]

def raw_witness_row(
    *,
    unfolding: dict[str, object],
    source_row: dict[str, object],
    target_row: dict[str, object],
    witness_kind: str,
    evidence_rule: str,
) -> dict[str, object]:
    return {
        "witness_id": "",
        "adapter_id": ADAPTER_ID,
        "unfolding_id": unfolding["unfolding_id"],
        "source_context_id": unfolding["source_context_id"],
        "target_context_id": unfolding["target_context_id"],
        "source_distinction_id": source_row["distinction_id"],
        "target_distinction_id": target_row["distinction_id"],
        "witness_kind": witness_kind,
        "witness_strength": 1,
        "source_truth_value": source_row["truth_value"],
        "target_truth_value": target_row["truth_value"],
        "source_numeric_value": source_row["numeric_value"],
        "target_numeric_value": target_row["numeric_value"],
        "source_horizon": unfolding["source_horizon"],
        "target_horizon": unfolding["target_horizon"],
        "source_artifact": source_row["source_table"],
        "target_artifact": target_row["source_table"],
        "evidence_rule": evidence_rule,
        "observed_or_derived": "observed_from_retained_panel",
        "notes": "finite_measure_only",
    }

def build_closed_transport(
    *,
    unfoldings: list[dict[str, object]],
    fibers: list[dict[str, object]],
    preorder_by_context: dict[str, set[tuple[str, str]]],
    raw_witnesses: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: dict[TransportKey, dict[str, object]] = {}

    def add_transport(
        key: TransportKey,
        *,
        support_kind: str,
        raw_witness_id: str = "",
        closure_reason: str,
        closure_depth: int,
        notes: str = "",
    ) -> None:
        if key in rows:
            return
        rows[key] = {
            "transport_id": f"tr::{stable_hash(key, length=24)}",
            "adapter_id": ADAPTER_ID,
            "unfolding_id": key.unfolding_id,
            "source_context_id": key.source_context_id,
            "target_context_id": key.target_context_id,
            "source_distinction_id": key.source_distinction_id,
            "target_distinction_id": key.target_distinction_id,
            "support_kind": support_kind,
            "raw_witness_id": raw_witness_id,
            "closure_reason": closure_reason,
            "closure_depth": closure_depth,
            "notes": notes,
        }

    for unfolding in unfoldings:
        if unfolding["unfolding_kind"] != "identity":
            continue
        context_id = str(unfolding["source_context_id"])
        for coarser, finer in preorder_by_context.get(context_id, set()):
            add_transport(
                TransportKey(
                    str(unfolding["unfolding_id"]),
                    context_id,
                    context_id,
                    coarser,
                    finer,
                ),
                support_kind="derived_identity",
                closure_reason="identity transport generated from declared preorder",
                closure_depth=0,
            )

    raw_by_unfolding: dict[str, list[dict[str, object]]] = defaultdict(list)
    for raw in raw_witnesses:
        raw_by_unfolding[str(raw["unfolding_id"])].append(raw)
        add_transport(
            TransportKey(
                str(raw["unfolding_id"]),
                str(raw["source_context_id"]),
                str(raw["target_context_id"]),
                str(raw["source_distinction_id"]),
                str(raw["target_distinction_id"]),
            ),
            support_kind="raw_observed",
            raw_witness_id=str(raw["witness_id"]),
            closure_reason="raw empirical witness",
            closure_depth=0,
        )

    # Source weakening / target strengthening closure.
    changed = True
    while changed:
        changed = False
        snapshot = list(rows.items())
        for key, row in snapshot:
            source_pairs = preorder_by_context.get(key.source_context_id, set())
            target_pairs = preorder_by_context.get(key.target_context_id, set())
            weaker_sources = [a for a, b in source_pairs if b == key.source_distinction_id]
            stronger_targets = [b for a, b in target_pairs if a == key.target_distinction_id]
            for weaker in weaker_sources:
                for stronger in stronger_targets:
                    new_key = TransportKey(
                        key.unfolding_id,
                        key.source_context_id,
                        key.target_context_id,
                        weaker,
                        stronger,
                    )
                    if new_key not in rows:
                        source_changed = weaker != key.source_distinction_id
                        target_changed = stronger != key.target_distinction_id
                        if source_changed and target_changed:
                            support_kind = "derived_source_weakening_and_target_strengthening"
                        elif source_changed:
                            support_kind = "derived_source_weakening"
                        elif target_changed:
                            support_kind = "derived_target_strengthening"
                        else:
                            continue
                        add_transport(
                            new_key,
                            support_kind=support_kind,
                            raw_witness_id=str(row.get("raw_witness_id", "")),
                            closure_reason=f"DistTrans closure from {row['transport_id']}",
                            closure_depth=int(row["closure_depth"]) + 1,
                        )
                        changed = True

    # One scoped normal-lax generation pass for step then horizon_to_final.
    triplets = composition_triplets(unfoldings)
    for first, second, composite in triplets:
        first_rows = [row for row in rows.values() if row["unfolding_id"] == first["unfolding_id"]]
        second_rows = [row for row in rows.values() if row["unfolding_id"] == second["unfolding_id"]]
        second_by_source: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in second_rows:
            second_by_source[str(row["source_distinction_id"])].append(row)
        for first_row in first_rows:
            for second_row in second_by_source.get(str(first_row["target_distinction_id"]), []):
                key = TransportKey(
                    str(composite["unfolding_id"]),
                    str(composite["source_context_id"]),
                    str(composite["target_context_id"]),
                    str(first_row["source_distinction_id"]),
                    str(second_row["target_distinction_id"]),
                )
                add_transport(
                    key,
                    support_kind="derived_composition_laxity",
                    closure_reason=(
                        f"normal-lax composition from {first_row['transport_id']} "
                        f"and {second_row['transport_id']}"
                    ),
                    closure_depth=max(int(first_row["closure_depth"]), int(second_row["closure_depth"])) + 1,
                )

    return sorted(rows.values(), key=lambda row: str(row["transport_id"]))

def build_law_checks(
    *,
    unfoldings: list[dict[str, object]],
    preorder_rows: list[dict[str, object]],
    raw_witnesses: list[dict[str, object]],
    closed_rows: list[dict[str, object]],
    preorder_by_context: dict[str, set[tuple[str, str]]],
) -> dict[str, list[dict[str, object]]]:
    raw_keys = {
        TransportKey(
            str(row["unfolding_id"]),
            str(row["source_context_id"]),
            str(row["target_context_id"]),
            str(row["source_distinction_id"]),
            str(row["target_distinction_id"]),
        )
        for row in raw_witnesses
    }
    closed_keys = {
        TransportKey(
            str(row["unfolding_id"]),
            str(row["source_context_id"]),
            str(row["target_context_id"]),
            str(row["source_distinction_id"]),
            str(row["target_distinction_id"]),
        )
        for row in closed_rows
    }
    identity_unfolding_by_context = {
        str(row["source_context_id"]): row
        for row in unfoldings
        if row["unfolding_kind"] == "identity"
    }
    identity_rows: list[dict[str, object]] = []
    for preorder in preorder_rows:
        context_id = str(preorder["context_id"])
        unfolding = identity_unfolding_by_context.get(context_id)
        if not unfolding:
            continue
        key = TransportKey(
            str(unfolding["unfolding_id"]),
            context_id,
            context_id,
            str(preorder["coarser_distinction_id"]),
            str(preorder["finer_distinction_id"]),
        )
        identity_rows.append(
            {
                "context_id": context_id,
                "source_distinction_id": key.source_distinction_id,
                "target_distinction_id": key.target_distinction_id,
                "required_by_preorder": 1,
                "present_in_closed_transport": int(key in closed_keys),
                "present_in_raw_transport": int(key in raw_keys),
                "status": "PASS" if key in closed_keys else "FAIL",
                "notes": "raw identity is not expected unless explicitly observed",
            }
        )

    source_rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    for row in closed_rows:
        unfolding_id = str(row["unfolding_id"])
        source_context = str(row["source_context_id"])
        target_context = str(row["target_context_id"])
        source = str(row["source_distinction_id"])
        target = str(row["target_distinction_id"])
        for weaker, stronger in preorder_by_context.get(source_context, set()):
            if stronger != source:
                continue
            key = TransportKey(unfolding_id, source_context, target_context, weaker, target)
            source_rows.append(
                {
                    "unfolding_id": unfolding_id,
                    "original_source_distinction_id": source,
                    "weaker_source_distinction_id": weaker,
                    "target_distinction_id": target,
                    "required_transport": 1,
                    "present_in_closed_transport": int(key in closed_keys),
                    "present_in_raw_transport": int(key in raw_keys),
                    "status": "PASS" if key in closed_keys else "FAIL",
                    "notes": "",
                }
            )
        for weaker_target, stronger_target in preorder_by_context.get(target_context, set()):
            if weaker_target != target:
                continue
            key = TransportKey(unfolding_id, source_context, target_context, source, stronger_target)
            target_rows.append(
                {
                    "unfolding_id": unfolding_id,
                    "source_distinction_id": source,
                    "original_target_distinction_id": target,
                    "stronger_target_distinction_id": stronger_target,
                    "required_transport": 1,
                    "present_in_closed_transport": int(key in closed_keys),
                    "present_in_raw_transport": int(key in raw_keys),
                    "status": "PASS" if key in closed_keys else "FAIL",
                    "notes": "",
                }
            )

    lax_rows: list[dict[str, object]] = []
    for first, second, composite in composition_triplets(unfoldings):
        first_rows = [row for row in closed_rows if row["unfolding_id"] == first["unfolding_id"]]
        second_rows = [row for row in closed_rows if row["unfolding_id"] == second["unfolding_id"]]
        second_by_source: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in second_rows:
            second_by_source[str(row["source_distinction_id"])].append(row)
        for first_row in first_rows:
            for second_row in second_by_source.get(str(first_row["target_distinction_id"]), []):
                key = TransportKey(
                    str(composite["unfolding_id"]),
                    str(composite["source_context_id"]),
                    str(composite["target_context_id"]),
                    str(first_row["source_distinction_id"]),
                    str(second_row["target_distinction_id"]),
                )
                lax_rows.append(
                    {
                        "first_unfolding_id": first["unfolding_id"],
                        "second_unfolding_id": second["unfolding_id"],
                        "composite_unfolding_id": composite["unfolding_id"],
                        "source_distinction_id": key.source_distinction_id,
                        "intermediate_distinction_id": first_row["target_distinction_id"],
                        "target_distinction_id": key.target_distinction_id,
                        "required_composite_transport": 1,
                        "present_in_closed_transport": int(key in closed_keys),
                        "present_in_raw_transport": int(key in raw_keys),
                        "status": "PASS" if key in closed_keys else "FAIL",
                        "notes": "",
                    }
                )
    return {
        "identity_transport_check": dedup_rows(identity_rows),
        "source_weakening_check": dedup_rows(source_rows),
        "target_strengthening_check": dedup_rows(target_rows),
        "lax_composition_check": dedup_rows(lax_rows),
    }

def build_law_summary_rows(law_tables: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for table_name, rows_in in law_tables.items():
        total = len(rows_in)
        closed_pass = sum(1 for row in rows_in if row.get("present_in_closed_transport") in (1, "1"))
        raw_pass = sum(1 for row in rows_in if row.get("present_in_raw_transport") in (1, "1"))
        fail = sum(1 for row in rows_in if row.get("status") != "PASS")
        rows.append(
            {
                "law_check": table_name.replace("_check", ""),
                "row_count": total,
                "raw_pass_count": raw_pass,
                "closed_pass_count": closed_pass,
                "fail_count": fail,
                "raw_conformance": int(total > 0 and raw_pass == total),
                "closed_conformance": int(total > 0 and fail == 0),
                "status": "PASS" if total > 0 and fail == 0 else "FAIL",
                "notes": "closed relation is the formal generated presentation; raw relation is empirical witness table",
            }
        )
    return rows

def composition_triplets(unfoldings: list[dict[str, object]]) -> list[tuple[dict[str, object], dict[str, object], dict[str, object]]]:
    by_key = {(row["unfolding_kind"], row["source_context_id"], row["target_context_id"]): row for row in unfoldings}
    horizon_to_final_by_source = {
        row["source_context_id"]: row for row in unfoldings if row["unfolding_kind"] == "horizon_to_final"
    }
    triplets = []
    for first in unfoldings:
        if first["unfolding_kind"] != "horizon_step":
            continue
        second = horizon_to_final_by_source.get(first["target_context_id"])
        if not second:
            continue
        composite = by_key.get(("horizon_to_final", first["source_context_id"], second["target_context_id"]))
        if composite:
            triplets.append((first, second, composite))
    return triplets
