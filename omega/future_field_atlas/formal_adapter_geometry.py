"""Context, unfolding, distinction-fiber, and preorder construction."""

from __future__ import annotations

from collections import defaultdict

from .formal_adapter_schema import (
    ADAPTER_ID,
    ContextKey,
    TokenKey,
    context_id_for,
    floatish,
    intish,
    source_row_id,
    token_for_delta_reference,
    transitive_closure,
)


def build_contexts(panel: dict[str, object]) -> list[dict[str, object]]:
    condition_by_cell = {
        (str(row["pair_id"]), str(row["operator_label"])): row
        for row in panel["condition_rows"]  # type: ignore[index]
    }
    seen: set[ContextKey] = set()
    contexts: list[dict[str, object]] = []
    for row in panel["retention_rows"]:  # type: ignore[index]
        pair_id = str(row["pair_id"])
        operator_id = str(row["operator_label"])
        observable_id = "coupled_future_field_joint_vs_marginal_geometry"
        horizon = intish(row.get("horizon"))
        key = ContextKey(pair_id, operator_id, observable_id, horizon)
        if key in seen:
            continue
        seen.add(key)
        condition = condition_by_cell.get((pair_id, operator_id), {})
        context_id = context_id_for(key)
        contexts.append(
            {
                "context_id": context_id,
                "adapter_id": ADAPTER_ID,
                "pair_id": pair_id,
                "operator_id": operator_id,
                "observable_id": observable_id,
                "horizon": horizon,
                "run_id": row.get("run_id", condition.get("run_id", "")),
                "condition_id": condition.get("condition_panel_id", f"{pair_id}__{operator_id}"),
                "source_artifact": row.get("source_artifact", condition.get("source_artifact", "")),
                "artifact_completeness_status": row.get(
                    "artifact_completeness_status",
                    condition.get("artifact_completeness_status", ""),
                ),
                "reconstruction_audit_status": row.get(
                    "reconstruction_audit_status",
                    condition.get("reconstruction_audit_status", ""),
                ),
                "internal_cap_events": condition.get("internal_cap_events", 0),
                "source_git_commit": condition.get("source_git_commit", ""),
                "source_git_dirty": condition.get("source_git_dirty", ""),
                "notes": "finite FFA condition-horizon locus",
            }
        )
    return sorted(contexts, key=lambda row: (row["pair_id"], row["operator_id"], int(row["horizon"])))

def build_unfoldings(contexts: list[dict[str, object]]) -> list[dict[str, object]]:
    by_cell: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in contexts:
        by_cell[(str(row["pair_id"]), str(row["operator_id"]), str(row["observable_id"]))].append(row)
    unfoldings: list[dict[str, object]] = []
    for rows in by_cell.values():
        rows = sorted(rows, key=lambda row: int(row["horizon"]))
        row_by_h = {int(row["horizon"]): row for row in rows}
        horizons = sorted(row_by_h)
        if not horizons:
            continue
        final_horizon = max(horizons)
        for horizon in horizons:
            source = row_by_h[horizon]
            unfoldings.append(
                unfolding_row(
                    kind="identity",
                    source=source,
                    target=source,
                    semantics="identity context relation",
                )
            )
            if horizon + 1 in row_by_h:
                unfoldings.append(
                    unfolding_row(
                        kind="horizon_step",
                        source=source,
                        target=row_by_h[horizon + 1],
                        semantics="adjacent retained horizon support relation",
                    )
                )
            if horizon < final_horizon:
                unfoldings.append(
                    unfolding_row(
                        kind="horizon_to_final",
                        source=source,
                        target=row_by_h[final_horizon],
                        semantics="retained horizon-to-final support relation",
                    )
                )
    return sorted(unfoldings, key=lambda row: str(row["unfolding_id"]))

def unfolding_row(
    *,
    kind: str,
    source: dict[str, object],
    target: dict[str, object],
    semantics: str,
) -> dict[str, object]:
    source_h = int(source["horizon"])
    target_h = int(target["horizon"])
    unfolding_id = f"unf::{kind}::{source['context_id']}::to::{target['context_id']}"
    return {
        "unfolding_id": unfolding_id,
        "adapter_id": ADAPTER_ID,
        "unfolding_kind": kind,
        "source_context_id": source["context_id"],
        "target_context_id": target["context_id"],
        "pair_id": source["pair_id"],
        "operator_id": source["operator_id"],
        "observable_id": source["observable_id"],
        "source_horizon": source_h,
        "target_horizon": target_h,
        "horizon_delta": target_h - source_h,
        "source_artifact": source.get("source_artifact", ""),
        "declared_relation_semantics": semantics,
        "notes": "core law-check unfolding" if kind != "identity" else "formal identity unfolding",
    }

def build_distinction_fibers(
    panel: dict[str, object],
    contexts: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[TokenKey, dict[str, object]]]:
    retention_by_context: dict[str, dict[str, object]] = {}
    for row in panel["retention_rows"]:  # type: ignore[index]
        key = ContextKey(
            str(row["pair_id"]),
            str(row["operator_label"]),
            "coupled_future_field_joint_vs_marginal_geometry",
            intish(row.get("horizon")),
        )
        retention_by_context[context_id_for(key)] = row

    indicator_by_context: dict[str, dict[str, object]] = {}
    for row in panel["measure_rows"]:  # type: ignore[index]
        if row.get("measure_id") != "marginal_preserving_joint_restrictive_indicator":
            continue
        key = ContextKey(
            str(row["pair_id"]),
            str(row["operator_label"]),
            str(row.get("observable_id") or "coupled_future_field_joint_vs_marginal_geometry"),
            intish(row.get("horizon")),
        )
        indicator_by_context[context_id_for(key)] = row

    delta_by_context: dict[tuple[str, str], dict[str, object]] = {}
    for row in panel["delta_rows"]:  # type: ignore[index]
        if row.get("metric_name") != "joint_support_residual_fraction":
            continue
        if str(row.get("both_cells_available")) != "1":
            continue
        token = token_for_delta_reference(str(row.get("right_operator", "")))
        if not token:
            continue
        key = ContextKey(
            str(row["pair_id"]),
            str(row["left_operator"]),
            "coupled_future_field_joint_vs_marginal_geometry",
            intish(row.get("horizon")),
        )
        delta_by_context[(context_id_for(key), token)] = row

    rows: list[dict[str, object]] = []
    lookup: dict[TokenKey, dict[str, object]] = {}
    for context in contexts:
        context_id = str(context["context_id"])
        retention = retention_by_context.get(context_id)
        if not retention:
            continue
        indicator = indicator_by_context.get(context_id, {})
        base_tokens = base_token_rows(context, retention, indicator)
        delta_tokens = [
            delta_token_row(context, token, delta_row)
            for (delta_context_id, token), delta_row in delta_by_context.items()
            if delta_context_id == context_id
        ]
        for row in base_tokens + delta_tokens:
            rows.append(row)
            lookup[TokenKey(context_id, str(row["distinction_id"]))] = row
    return sorted(rows, key=lambda row: (str(row["context_id"]), str(row["distinction_id"]))), lookup

def base_token_rows(
    context: dict[str, object],
    retention: dict[str, object],
    indicator: dict[str, object],
) -> list[dict[str, object]]:
    a_ret = floatish(retention.get("A_marginal_retention"))
    b_ret = floatish(retention.get("B_marginal_retention"))
    density = floatish(retention.get("joint_density_vs_marginal_product"))
    residual = floatish(retention.get("joint_support_residual_fraction"))
    marginal = a_ret >= 0.99 and b_ret >= 0.99
    joint_restrictive = density <= 0.50
    high_residual = residual >= 0.40
    product_dense = str(retention.get("product_dense_over_surviving_marginals_flag")) == "1"
    marginal_loss = not marginal
    indicator_true = str(indicator.get("binary_status", "")).lower() == "true"
    retention_table = "joint_vs_marginal_distinction_retention.csv"
    measure_table = "distinction_measure_by_horizon.csv"
    token_specs = [
        ("A_marginal_preserving", "A_marginal_retention", a_ret, a_ret >= 0.99, "threshold_A_marginal_retention_gte_0_99", 0.99, retention_table),
        ("B_marginal_preserving", "B_marginal_retention", b_ret, b_ret >= 0.99, "threshold_B_marginal_retention_gte_0_99", 0.99, retention_table),
        ("marginal_preserving", "A_and_B_marginal_retention", min(a_ret, b_ret), marginal, "threshold_both_marginal_retention_gte_0_99", 0.99, retention_table),
        ("joint_restrictive", "joint_density_vs_marginal_product", density, joint_restrictive, "threshold_joint_density_lte_0_50", 0.50, retention_table),
        ("high_residual", "joint_support_residual_fraction", residual, high_residual, "threshold_joint_residual_gte_0_40", 0.40, retention_table),
        ("product_dense", "joint_density_vs_marginal_product", density, product_dense, "threshold_product_dense_flag", 1, retention_table),
        ("marginal_loss", "A_and_B_marginal_retention", min(a_ret, b_ret), marginal_loss, "threshold_any_marginal_retention_lt_0_99", 0.99, retention_table),
        ("marginal_preserving_joint_restrictive", "marginal_preserving_joint_restrictive_indicator", float(indicator_true), indicator_true, "threshold_marginal_preserving_and_joint_density_lte_0_50", 1, measure_table),
        ("high_yield_signature", "marginal_preserving_joint_restrictive_indicator", float(indicator_true), indicator_true, "threshold_high_yield_signature_indicator_true", 1, measure_table),
    ]
    return [
        token_row(
            context=context,
            distinction_id=token,
            measure_id=measure_id,
            token_family=token,
            truth=truth,
            numeric=value,
            threshold_id=threshold_id,
            threshold_value=threshold_value,
            source_table=source_table,
            source_row_id=source_row_id(context, token),
            derivation_rule=f"{token} finite_measure_threshold",
        )
        for token, measure_id, value, truth, threshold_id, threshold_value, source_table in token_specs
    ]

def delta_token_row(
    context: dict[str, object],
    token: str,
    delta_row: dict[str, object],
) -> dict[str, object]:
    delta = floatish(delta_row.get("delta"))
    return token_row(
        context=context,
        distinction_id=token,
        measure_id=token.replace("_positive", ""),
        token_family=token,
        truth=delta > 0.0,
        numeric=delta,
        threshold_id="threshold_residual_delta_gt_0",
        threshold_value=0,
        source_table="operator_reference_delta_by_horizon.csv",
        source_row_id=source_row_id(context, token),
        derivation_rule=f"{token}: joint_support_residual_fraction delta > 0",
    )

def token_row(
    *,
    context: dict[str, object],
    distinction_id: str,
    measure_id: str,
    token_family: str,
    truth: bool,
    numeric: float,
    threshold_id: str,
    threshold_value: object,
    source_table: str,
    source_row_id: str,
    derivation_rule: str,
) -> dict[str, object]:
    return {
        "context_id": context["context_id"],
        "distinction_id": distinction_id,
        "measure_id": measure_id,
        "token_family": token_family,
        "token_value": "true" if truth else "false",
        "truth_value": int(bool(truth)),
        "numeric_value": numeric,
        "threshold_id": threshold_id,
        "threshold_value": threshold_value,
        "source_table": source_table,
        "source_row_id": source_row_id,
        "derivation_rule": derivation_rule,
        "notes": "finite_measure_only; no semantic promotion",
    }

def build_preorder(
    fibers: list[dict[str, object]]
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, set[tuple[str, str]]]]:
    tokens_by_context: dict[str, set[str]] = defaultdict(set)
    for row in fibers:
        tokens_by_context[str(row["context_id"])].add(str(row["distinction_id"]))
    rule_pairs = [
        ("A_marginal_preserving", "marginal_preserving", "marginal_preserving refines A_marginal_preserving"),
        ("B_marginal_preserving", "marginal_preserving", "marginal_preserving refines B_marginal_preserving"),
        ("marginal_preserving", "marginal_preserving_joint_restrictive", "marginal_preserving_joint_restrictive refines marginal_preserving"),
        ("joint_restrictive", "marginal_preserving_joint_restrictive", "marginal_preserving_joint_restrictive refines joint_restrictive"),
        ("marginal_preserving_joint_restrictive", "high_yield_signature", "high_yield_signature refines marginal_preserving_joint_restrictive"),
    ]
    rows: list[dict[str, object]] = []
    open_questions: list[dict[str, object]] = []
    preorder_by_context: dict[str, set[tuple[str, str]]] = {}
    for context_id, tokens in tokens_by_context.items():
        pairs: set[tuple[str, str]] = set()
        for token in sorted(tokens):
            pairs.add((token, token))
            rows.append(preorder_row(context_id, token, token, "reflexive", "d <= d"))
        for coarser, finer, note in rule_pairs:
            if coarser in tokens and finer in tokens:
                pairs.add((coarser, finer))
                rows.append(preorder_row(context_id, coarser, finer, "declared_token_refinement", note))
        if "high_residual" in tokens and "joint_restrictive" in tokens:
            open_questions.append(
                {
                    "context_id": context_id,
                    "candidate_relation": "joint_restrictive <= high_residual",
                    "reason": "high_residual threshold does not imply joint_density_lte_0_50 for all rows",
                    "status": "omitted",
                }
            )
        preorder_by_context[context_id] = transitive_closure(pairs)
    # Add explicit transitive rows not already present.
    existing = {(str(r["context_id"]), str(r["coarser_distinction_id"]), str(r["finer_distinction_id"])) for r in rows}
    for context_id, pairs in preorder_by_context.items():
        for coarser, finer in sorted(pairs):
            key = (context_id, coarser, finer)
            if key not in existing:
                rows.append(preorder_row(context_id, coarser, finer, "transitive_generated", "preorder transitive closure"))
                existing.add(key)
    checks = preorder_check_rows(preorder_by_context)
    return sorted(rows, key=lambda row: (row["context_id"], row["coarser_distinction_id"], row["finer_distinction_id"])), open_questions, checks, preorder_by_context

def preorder_row(context_id: str, coarser: str, finer: str, rule: str, notes: str) -> dict[str, object]:
    return {
        "context_id": context_id,
        "coarser_distinction_id": coarser,
        "finer_distinction_id": finer,
        "preorder_relation_id": f"pre::{context_id}::{coarser}::le::{finer}",
        "preorder_rule": rule,
        "source": "adapter_declared_threshold_token_rules",
        "notes": notes,
    }

def preorder_check_rows(preorder_by_context: dict[str, set[tuple[str, str]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for context_id, pairs in preorder_by_context.items():
        tokens = {a for a, _b in pairs} | {b for _a, b in pairs}
        reflexive_failures = [token for token in tokens if (token, token) not in pairs]
        transitive_failures = []
        for a, b in pairs:
            for c, d in pairs:
                if b == c and (a, d) not in pairs:
                    transitive_failures.append(f"{a}<={b}<={d}")
        rows.append(
            {
                "context_id": context_id,
                "reflexivity_status": "PASS" if not reflexive_failures else "FAIL",
                "transitivity_status": "PASS" if not transitive_failures else "FAIL",
                "reflexive_failure_count": len(reflexive_failures),
                "transitive_failure_count": len(transitive_failures),
                "status": "PASS" if not reflexive_failures and not transitive_failures else "FAIL",
                "notes": ";".join(transitive_failures[:5] + reflexive_failures[:5]),
            }
        )
    return rows
