"""Recoverability, non-erasure, diagnostics, and theorem-transfer summaries."""

from __future__ import annotations

from collections import defaultdict

from .formal_adapter_schema import TokenKey, TransportKey, floatish
from .formal_adapter_transport import build_law_summary_rows


def build_requirement_manifest(fibers: list[dict[str, object]]) -> list[dict[str, object]]:
    token_set = {str(row["distinction_id"]) for row in fibers}
    specs = [
        ("req_marginal_preservation", "marginal preservation finite-measure set", ["A_marginal_preserving", "B_marginal_preserving"]),
        ("req_joint_restriction_signature", "joint restriction finite-measure set", ["joint_restrictive"]),
        ("req_high_yield_signature", "high-yield finite-measure signature", ["marginal_preserving_joint_restrictive"]),
        ("req_operator_delta_signature", "operator residual-delta finite-measure signature", ["residual_delta_vs_product_positive"]),
    ]
    rows = []
    for req_id, name, tokens in specs:
        rows.append(
            {
                "requirement_set_id": req_id,
                "requirement_set_name": name,
                "distinction_ids": ";".join(token for token in tokens if token in token_set),
                "declaration_rule": "declared finite threshold token set",
                "claim_scope": "adapter_conformance_v0",
                "semantic_status": "finite_measure_only",
                "notes": "tokens absent from the current fiber universe are omitted",
            }
        )
    return rows

def build_recoverability_rows(
    *,
    requirement_manifest: list[dict[str, object]],
    unfoldings: list[dict[str, object]],
    token_lookup: dict[TokenKey, dict[str, object]],
    raw_witnesses: list[dict[str, object]],
    closed_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    raw_by_key = {
        TransportKey(
            str(row["unfolding_id"]),
            str(row["source_context_id"]),
            str(row["target_context_id"]),
            str(row["source_distinction_id"]),
            str(row["target_distinction_id"]),
        ): row
        for row in raw_witnesses
    }
    closed_by_source: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in closed_rows:
        closed_by_source[
            (str(row["unfolding_id"]), str(row["source_context_id"]), str(row["source_distinction_id"]))
        ].append(row)
    rows: list[dict[str, object]] = []
    for req in requirement_manifest:
        req_tokens = [token for token in str(req.get("distinction_ids", "")).split(";") if token]
        for unfolding in unfoldings:
            if unfolding["unfolding_kind"] == "identity":
                continue
            for token in req_tokens:
                source_key = TokenKey(str(unfolding["source_context_id"]), token)
                if source_key not in token_lookup:
                    status = "blocked_missing_distinction"
                    matches: list[dict[str, object]] = []
                else:
                    matches = closed_by_source.get(
                        (str(unfolding["unfolding_id"]), str(unfolding["source_context_id"]), token),
                        [],
                    )
                    status = "not_recovered"
                    if matches:
                        raw_match = next(
                            (
                                match
                                for match in matches
                                if TransportKey(
                                    str(match["unfolding_id"]),
                                    str(match["source_context_id"]),
                                    str(match["target_context_id"]),
                                    str(match["source_distinction_id"]),
                                    str(match["target_distinction_id"]),
                                )
                                in raw_by_key
                            ),
                            None,
                        )
                        status = "recovered_raw" if raw_match else "recovered_by_closure"
                if matches:
                    for match in matches[:1]:
                        key = TransportKey(
                            str(match["unfolding_id"]),
                            str(match["source_context_id"]),
                            str(match["target_context_id"]),
                            str(match["source_distinction_id"]),
                            str(match["target_distinction_id"]),
                        )
                        raw = raw_by_key.get(key, {})
                        rows.append(
                            {
                                "requirement_set_id": req["requirement_set_id"],
                                "unfolding_id": unfolding["unfolding_id"],
                                "source_context_id": unfolding["source_context_id"],
                                "target_context_id": unfolding["target_context_id"],
                                "required_distinction_id": token,
                                "recovering_distinction_id": match["target_distinction_id"],
                                "recoverability_status": status,
                                "support_kind": match["support_kind"],
                                "raw_witness_id": raw.get("witness_id", match.get("raw_witness_id", "")),
                                "closure_transport_id": match["transport_id"],
                                "notes": "",
                            }
                        )
                else:
                    rows.append(
                        {
                            "requirement_set_id": req["requirement_set_id"],
                            "unfolding_id": unfolding["unfolding_id"],
                            "source_context_id": unfolding["source_context_id"],
                            "target_context_id": unfolding["target_context_id"],
                            "required_distinction_id": token,
                            "recovering_distinction_id": "",
                            "recoverability_status": status,
                            "support_kind": "",
                            "raw_witness_id": "",
                            "closure_transport_id": "",
                            "notes": "",
                        }
                    )
    return rows

def build_non_erasure_rows(recoverability_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in recoverability_rows:
        grouped[
            (
                str(row["requirement_set_id"]),
                str(row["unfolding_id"]),
                str(row["source_context_id"]),
                str(row["target_context_id"]),
            )
        ].append(row)
    rows: list[dict[str, object]] = []
    for (req_id, unfolding_id, source_context, target_context), req_rows in grouped.items():
        required = {str(row["required_distinction_id"]) for row in req_rows}
        recovered_raw = {
            str(row["required_distinction_id"])
            for row in req_rows
            if row["recoverability_status"] == "recovered_raw"
        }
        recovered_closed = {
            str(row["required_distinction_id"])
            for row in req_rows
            if row["recoverability_status"] in ("recovered_raw", "recovered_by_closure")
        }
        blocked = [
            row
            for row in req_rows
            if str(row["recoverability_status"]).startswith("blocked")
        ]
        rows.append(
            {
                "requirement_set_id": req_id,
                "unfolding_id": unfolding_id,
                "source_context_id": source_context,
                "target_context_id": target_context,
                "required_count": len(required),
                "recovered_raw_count": len(recovered_raw),
                "recovered_by_closure_count": len(recovered_closed - recovered_raw),
                "not_recovered_count": len(required - recovered_closed),
                "non_erasing_raw": int(bool(required) and recovered_raw == required),
                "non_erasing_closed": int(bool(required) and recovered_closed == required),
                "status": "blocked" if blocked else ("PASS" if recovered_closed == required else "PARTIAL"),
                "notes": "",
            }
        )
    return rows

def build_marginal_joint_diagnostic(panel: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in panel["retention_rows"]:  # type: ignore[index]
        a = floatish(row.get("A_marginal_retention"))
        b = floatish(row.get("B_marginal_retention"))
        density = floatish(row.get("joint_density_vs_marginal_product"))
        residual = floatish(row.get("joint_support_residual_fraction"))
        marginal = a >= 0.99 and b >= 0.99
        joint_restricted = density <= 0.50
        if marginal and joint_restricted:
            klass = "marginal_preserved_joint_restricted"
        elif marginal:
            klass = "marginal_and_joint_preserved"
        elif joint_restricted:
            klass = "marginal_loss_joint_restrictive"
        else:
            klass = "marginal_loss_product_dense"
        rows.append(
            {
                "pair_id": row["pair_id"],
                "operator_id": row["operator_label"],
                "observable_id": row.get("observable_id", "coupled_future_field_joint_vs_marginal_geometry"),
                "horizon": row["horizon"],
                "marginal_requirement_status": "non_erasing_measure_true" if marginal else "not_non_erasing_measure",
                "joint_requirement_status": "joint_restricted_measure_true" if joint_restricted else "joint_dense_measure",
                "A_marginal_retention": a,
                "B_marginal_retention": b,
                "joint_density_vs_marginal_product": density,
                "joint_support_residual": residual,
                "diagnostic_class": klass,
                "notes": "finite_measure_only; no compatibility or erasure claim",
            }
        )
    return rows

def build_theorem_transfer_summary(
    law_tables: dict[str, list[dict[str, object]]],
    non_erasure_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    law_summary = build_law_summary_rows(law_tables)
    law_status = {row["law_check"]: row for row in law_summary}

    def transfer_for(required: list[str]) -> str:
        rows = [law_status.get(name) for name in required]
        if any(row is None for row in rows):
            return "blocked_missing_artifacts"
        if all(int(row["raw_conformance"]) == 1 for row in rows if row):
            return "transfers_to_raw_relation"
        if all(int(row["closed_conformance"]) == 1 for row in rows if row):
            return "transfers_to_closed_presentation"
        return "blocked_law_failure"

    non_erasure_available = any(int(row.get("non_erasing_closed", 0)) == 1 for row in non_erasure_rows)
    specs = [
        ("disttrans_identity", "Identity transport", ["identity_transport"], "identity_transport_check.csv"),
        ("disttrans_source_weakening", "Recoverability source weakening", ["source_weakening"], "source_weakening_check.csv"),
        ("disttrans_target_strengthening", "Recoverability target strengthening", ["target_strengthening"], "target_strengthening_check.csv"),
        ("compositional_recoverability", "Compositional recoverability", ["lax_composition"], "lax_composition_check.csv"),
        ("non_erasure_monotonicity", "Non-erasure monotonicity", ["source_weakening", "target_strengthening"], "non_erasure_by_unfolding.csv"),
        ("finite_chain_recurrent_recoverability", "Finite-chain recurrent recoverability", ["lax_composition"], "lax_composition_check.csv"),
    ]
    rows = []
    for theorem_id, name, laws, artifacts in specs:
        status = transfer_for(laws)
        if theorem_id == "non_erasure_monotonicity" and not non_erasure_available:
            status = "partial_transfer"
        rows.append(
            {
                "theorem_id": theorem_id,
                "theorem_name": name,
                "required_laws": ";".join(laws),
                "required_artifacts": artifacts,
                "law_check_status": status,
                "artifact_status": "available",
                "transfer_status": status,
                "claim_allowed": "finite adapter theorem-transfer status",
                "claim_blocked": "Omega/value/valuerhood/compatibility semantics",
                "notes": "",
            }
        )
    rows.append(
        {
            "theorem_id": "marginal_non_erasure_not_joint_non_erasure",
            "theorem_name": "Marginal-like non-erasure not joint non-erasure",
            "required_laws": "distinction_transport_measure_tokens",
            "required_artifacts": "marginal_joint_non_erasure_diagnostic.csv",
            "law_check_status": "diagnostic_available",
            "artifact_status": "available",
            "transfer_status": "partial_transfer",
            "claim_allowed": "finite-measure diagnostic only",
            "claim_blocked": "compatibility/support/capture/erasure detection",
            "notes": "diagnostic mirrors root separation but is not a formal proof of FFA semantics",
        }
    )
    rows.append(
        {
            "theorem_id": "finite_completion_existence",
            "theorem_name": "Finite maximal completion existence",
            "required_laws": "candidate_family_space;admissibility_predicate",
            "required_artifacts": "",
            "law_check_status": "not_applicable",
            "artifact_status": "not_declared",
            "transfer_status": "not_applicable",
            "claim_allowed": "none in adapter v0",
            "claim_blocked": "completion existence over FFA candidates",
            "notes": "candidate family spaces and admissibility predicates are not declared in this package",
        }
    )
    return rows

def classify_adapter_status(
    law_summary_rows: list[dict[str, object]],
    gate: dict[str, object],
) -> str:
    if gate["adapter_status"] != "input_complete":
        return "blocked_input_incomplete"
    if all(int(row["raw_conformance"]) == 1 for row in law_summary_rows):
        return "strict_raw_conformance"
    if all(int(row["closed_conformance"]) == 1 for row in law_summary_rows):
        return "generated_presentation_conformance"
    if any(int(row["closed_conformance"]) == 1 for row in law_summary_rows):
        return "partial_conformance"
    return "failed_conformance"
