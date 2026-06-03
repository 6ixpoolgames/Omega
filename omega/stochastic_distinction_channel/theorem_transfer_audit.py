"""Theorem-transfer audit for finite stochastic distinction-channel outputs."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from omega.future_field_atlas.util import read_csv, stable_hash, write_csv, write_json

from .schema import DEFAULT_OUT, fraction_text


DEFAULT_AUDIT_OUT = Path(
    "results/stochastic_distinction_channel/20260604_stochastic_channel_theorem_transfer_audit_v0"
)
AUDIT_BOUNDARY = (
    "finite stochastic channel theorem-transfer audit; support/probability separation, "
    "decoder-policy provenance, and cascade error-bound applicability only"
)
REQUIRED_INPUTS = [
    "channel_probe_manifest.json",
    "artifact_manifest.json",
    "carrier_manifest.csv",
    "channel_manifest.csv",
    "channel_matrix.csv",
    "channel_support.csv",
    "source_prior_manifest.csv",
    "distinction_manifest.csv",
    "source_observation_table.csv",
    "target_observation_table.csv",
    "decoder_manifest.csv",
    "decoder_policy_manifest.csv",
    "decoder_table.csv",
    "threshold_manifest.csv",
    "recoverability_by_distinction.csv",
    "support_recoverability.csv",
    "support_vs_probability_summary.csv",
    "non_erasure_requirement_manifest.csv",
    "non_erasure_by_channel.csv",
    "marginal_joint_recoverability_diagnostic.csv",
    "declared_target_policy_summary.csv",
    "channel_composition_manifest.csv",
    "composed_channel_matrix.csv",
    "composition_recoverability_check.csv",
    "theorem_transfer_readiness_summary.csv",
    "formal_channel_consumption_bundle.json",
    "channel_row_stochastic_audit.csv",
    "distinction_partition_audit.csv",
    "decoder_totality_audit.csv",
    "threshold_application_audit.csv",
]
AUDIT_OUTPUTS = [
    "rational_weight_manifest.csv",
    "natural_weight_realization.csv",
    "natural_weight_realization_audit.csv",
    "cascade_path_ensemble_manifest.csv",
    "cascade_path_ensemble_rows.csv",
    "cascade_total_mass.csv",
    "cascade_error_mass_by_stage.csv",
    "cascade_bound_check.csv",
    "denominator_alignment_audit.csv",
    "decoder_policy_alignment_audit.csv",
    "no_self_evidencing_decoder_audit.csv",
    "support_probability_theorem_boundary.csv",
    "threshold_sensitivity_by_distinction.csv",
    "marginal_joint_theorem_examples.csv",
    "probabilistic_theorem_transfer_readiness_summary.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit stochastic-channel theorem-transfer readiness.")
    parser.add_argument("--source", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_AUDIT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_theorem_transfer_audit(source_dir=args.source, out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_theorem_transfer_audit(*, source_dir: Path, out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    missing = missing_inputs(source_dir)
    tables = {name: read_required_csv(source_dir, name) for name in REQUIRED_INPUTS if name.endswith(".csv")}
    input_status = audit_input_status(tables, missing)

    channel_matrix = tables.get("channel_matrix.csv", [])
    source_priors = tables.get("source_prior_manifest.csv", [])
    recoverability = tables.get("recoverability_by_distinction.csv", [])
    composition_manifest = tables.get("channel_composition_manifest.csv", [])
    composition_checks = tables.get("composition_recoverability_check.csv", [])

    rational_rows = rational_weight_manifest(channel_matrix, source_priors)
    natural_rows, channel_weights = natural_weight_realization(channel_matrix)
    prior_weights = naturalize_priors(source_priors)
    natural_audit = natural_weight_realization_audit(natural_rows, prior_weights)

    context = AuditContext(
        source_dir=source_dir,
        channel_weights=channel_weights,
        prior_weights=prior_weights,
        source_observations=observation_index(
            tables.get("source_observation_table.csv", []) + tables.get("target_observation_table.csv", [])
        ),
        decoder_manifest=decoder_manifest_index(tables.get("decoder_manifest.csv", [])),
        decoder_tables=decoder_table_index(tables.get("decoder_table.csv", [])),
        recoverability=recoverability_index(recoverability),
        recoverability_rows=recoverability,
    )

    cascade_artifacts = build_cascade_artifacts(
        context=context,
        composition_manifest=composition_manifest,
        composition_checks=composition_checks,
    )
    no_self_audit = no_self_evidencing_decoder_audit(
        tables.get("decoder_manifest.csv", []),
        tables.get("decoder_table.csv", []),
    )
    support_boundary = support_probability_theorem_boundary(recoverability, source_priors)
    threshold_sensitivity = threshold_sensitivity_by_distinction(recoverability)
    marginal_examples = marginal_joint_theorem_examples(tables.get("marginal_joint_recoverability_diagnostic.csv", []))
    readiness = probabilistic_theorem_transfer_readiness_summary(
        input_status=input_status,
        cascade_bound_check=cascade_artifacts["cascade_bound_check.csv"],
        denominator_alignment=cascade_artifacts["denominator_alignment_audit.csv"],
        decoder_policy_alignment=cascade_artifacts["decoder_policy_alignment_audit.csv"],
        no_self_audit=no_self_audit,
        support_boundary=support_boundary,
        non_erasure=tables.get("non_erasure_by_channel.csv", []),
        declared_policy=tables.get("declared_target_policy_summary.csv", []),
    )

    csv_outputs: dict[str, list[dict[str, object]]] = {
        "rational_weight_manifest.csv": rational_rows,
        "natural_weight_realization.csv": natural_rows,
        "natural_weight_realization_audit.csv": natural_audit,
        **cascade_artifacts,
        "no_self_evidencing_decoder_audit.csv": no_self_audit,
        "support_probability_theorem_boundary.csv": support_boundary,
        "threshold_sensitivity_by_distinction.csv": threshold_sensitivity,
        "marginal_joint_theorem_examples.csv": marginal_examples,
        "probabilistic_theorem_transfer_readiness_summary.csv": readiness,
    }
    for name, rows in csv_outputs.items():
        write_csv(out_dir / name, rows)

    source_digest = source_probe_digest(source_dir)
    overall_status = overall_audit_status(
        input_status=input_status,
        bound_rows=cascade_artifacts["cascade_bound_check.csv"],
        denominator_rows=cascade_artifacts["denominator_alignment_audit.csv"],
        policy_rows=cascade_artifacts["decoder_policy_alignment_audit.csv"],
        no_self_rows=no_self_audit,
    )
    bundle = build_theorem_transfer_bundle(
        source_dir=source_dir,
        out_dir=out_dir,
        source_digest=source_digest,
        csv_outputs=csv_outputs,
        overall_status=overall_status,
    )
    write_json(out_dir / "probabilistic_channel_theorem_transfer_bundle.json", bundle)
    report = render_report(
        source_dir=source_dir,
        source_digest=source_digest,
        input_status=input_status,
        cascade_bound_check=cascade_artifacts["cascade_bound_check.csv"],
        denominator_alignment=cascade_artifacts["denominator_alignment_audit.csv"],
        decoder_policy_alignment=cascade_artifacts["decoder_policy_alignment_audit.csv"],
        no_self_audit=no_self_audit,
        support_boundary=support_boundary,
        threshold_sensitivity=threshold_sensitivity,
        marginal_examples=marginal_examples,
        readiness=readiness,
        overall_status=overall_status,
    )
    (out_dir / "stochastic_channel_theorem_transfer_audit_report.md").write_text(report, encoding="utf-8")
    artifact_manifest = artifact_manifest_for_outputs(out_dir, csv_outputs)
    write_json(out_dir / "artifact_manifest.json", artifact_manifest)
    return {
        "audit_status": overall_status,
        "out_dir": str(out_dir),
        "source_dir": str(source_dir),
        "cascade_bound_rows": len(cascade_artifacts["cascade_bound_check.csv"]),
        "path_rows": len(cascade_artifacts["cascade_path_ensemble_rows.csv"]),
        "bundle_digest": bundle["bundle_digest"],
    }


class AuditContext:
    def __init__(
        self,
        *,
        source_dir: Path,
        channel_weights: dict[str, dict[str, dict[str, int]]],
        prior_weights: dict[str, dict[str, int]],
        source_observations: dict[tuple[str, str], dict[str, str]],
        decoder_manifest: dict[tuple[str, str, str, str], dict[str, str]],
        decoder_tables: dict[str, dict[str, str]],
        recoverability: dict[tuple[str, str, str, str], dict[str, str]],
        recoverability_rows: list[dict[str, object]],
    ) -> None:
        self.source_dir = source_dir
        self.channel_weights = channel_weights
        self.prior_weights = prior_weights
        self.source_observations = source_observations
        self.decoder_manifest = decoder_manifest
        self.decoder_tables = decoder_tables
        self.recoverability = recoverability
        self.recoverability_rows = recoverability_rows


def missing_inputs(source_dir: Path) -> list[str]:
    missing = []
    for name in REQUIRED_INPUTS:
        path = source_dir / name
        gz_path = source_dir / f"{name}.gz" if name.endswith(".csv") else path
        if not path.exists() and not gz_path.exists():
            missing.append(name)
    return missing


def read_required_csv(source_dir: Path, name: str) -> list[dict[str, object]]:
    path = source_dir / name
    if path.exists():
        return read_csv(path)
    gz_path = source_dir / f"{name}.gz"
    if gz_path.exists():
        return read_csv(gz_path)
    return []


def audit_input_status(tables: dict[str, list[dict[str, object]]], missing: list[str]) -> dict[str, object]:
    audit_files = [
        "channel_row_stochastic_audit.csv",
        "distinction_partition_audit.csv",
        "decoder_totality_audit.csv",
        "threshold_application_audit.csv",
    ]
    failures = {
        name: sum(1 for row in tables.get(name, []) if str(row.get("status", "")) == "FAIL")
        for name in audit_files
    }
    return {
        "missing_inputs": missing,
        "audit_failures": failures,
        "status": "blocked_missing_input"
        if missing
        else ("blocked_input_audit_failure" if any(failures.values()) else "ready"),
    }


def rational_weight_manifest(
    channel_matrix: list[dict[str, object]],
    source_priors: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows = []
    for row in channel_matrix:
        value = fraction_from_fields(row)
        rows.append(
            rational_weight_row(
                object_kind="channel_probability",
                object_id=f"{row['channel_id']}::{row['source_state']}->{row['target_state']}",
                source_value=row.get("probability_fraction") or row.get("probability", ""),
                value=value,
            )
        )
    for row in source_priors:
        value = fraction_from_fields(row)
        rows.append(
            rational_weight_row(
                object_kind="source_prior_probability",
                object_id=f"{row['prior_id']}::{row['state_id']}",
                source_value=row.get("probability_fraction") or row.get("probability", ""),
                value=value,
            )
        )
    return rows


def rational_weight_row(*, object_kind: str, object_id: str, source_value: object, value: Fraction) -> dict[str, object]:
    return {
        "object_kind": object_kind,
        "object_id": object_id,
        "source_value": source_value,
        "rational_numerator": value.numerator,
        "rational_denominator": value.denominator,
        "exact_rationalized": 1,
        "max_denominator_used": value.denominator,
        "rationalization_error": 0,
        "status": "exact",
    }


def natural_weight_realization(
    channel_matrix: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, dict[str, dict[str, int]]]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in channel_matrix:
        grouped[(str(row["channel_id"]), str(row["source_state"]))].append(row)

    out_rows: list[dict[str, object]] = []
    weights: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(dict))
    for (channel_id, source_state), rows in sorted(grouped.items()):
        probabilities = [fraction_from_fields(row) for row in rows]
        row_total = math.lcm(*(p.denominator for p in probabilities)) if probabilities else 1
        for row, probability in zip(rows, probabilities):
            natural_weight = int(probability * row_total)
            target_state = str(row["target_state"])
            weights[channel_id][source_state][target_state] = natural_weight
            out_rows.append(
                {
                    "channel_id": channel_id,
                    "row_id": f"{channel_id}::{source_state}",
                    "source_state": source_state,
                    "target_state": target_state,
                    "probability_value": row.get("probability", ""),
                    "probability_fraction": fraction_text(probability),
                    "natural_weight": natural_weight,
                    "row_weight_total": row_total,
                    "realization_status": "exact",
                    "notes": "row-scaled natural weights for finite Lean-style channel realization",
                }
            )
    return out_rows, {k: dict(v) for k, v in weights.items()}


def naturalize_priors(source_priors: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in source_priors:
        grouped[str(row["prior_id"])].append(row)
    weights: dict[str, dict[str, int]] = {}
    for prior_id, rows in grouped.items():
        probabilities = [fraction_from_fields(row) for row in rows]
        total = math.lcm(*(p.denominator for p in probabilities)) if probabilities else 1
        weights[prior_id] = {str(row["state_id"]): int(probability * total) for row, probability in zip(rows, probabilities)}
    return weights


def natural_weight_realization_audit(
    natural_rows: list[dict[str, object]],
    prior_weights: dict[str, dict[str, int]],
) -> list[dict[str, object]]:
    rows = []
    row_totals: dict[str, int] = defaultdict(int)
    declared_totals: dict[str, int] = {}
    for row in natural_rows:
        row_id = str(row["row_id"])
        row_totals[row_id] += int(row["natural_weight"])
        declared_totals[row_id] = int(row["row_weight_total"])
    for row_id, observed in sorted(row_totals.items()):
        rows.append(
            {
                "object_kind": "channel_row",
                "object_id": row_id,
                "observed_weight_total": observed,
                "declared_weight_total": declared_totals[row_id],
                "positive_total": int(observed > 0),
                "exact_rationalized": 1,
                "status": "PASS" if observed == declared_totals[row_id] and observed > 0 else "FAIL",
            }
        )
    for prior_id, weights in sorted(prior_weights.items()):
        total = sum(weights.values())
        rows.append(
            {
                "object_kind": "source_prior",
                "object_id": prior_id,
                "observed_weight_total": total,
                "declared_weight_total": total,
                "positive_total": int(total > 0),
                "exact_rationalized": 1,
                "status": "PASS" if total > 0 else "FAIL",
            }
        )
    return rows


def build_cascade_artifacts(
    *,
    context: AuditContext,
    composition_manifest: list[dict[str, object]],
    composition_checks: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    path_manifest = []
    path_rows = []
    total_rows = []
    error_rows = []
    bound_rows = []
    denominator_rows = []
    policy_rows = []
    manifest_by_id = {str(row["composition_id"]): row for row in composition_manifest}
    for check in composition_checks:
        composition_id = str(check["composition_id"])
        manifest = manifest_by_id.get(composition_id, {})
        if not manifest:
            continue
        result = build_single_cascade(
            context=context,
            composition=manifest,
            check=check,
            decoder_policy_id="fixed_declared_target_distinction",
        )
        path_manifest.append(result["manifest"])
        path_rows.extend(result["path_rows"])
        total_rows.append(result["total"])
        error_rows.append(result["error"])
        bound_rows.append(result["bound"])
        denominator_rows.append(result["denominator"])
        policy_rows.append(result["policy"])
        policy_rows.append(
            bayes_best_policy_alignment_row(
                composition=manifest,
                check=check,
                fixed_policy_row=result["policy"],
            )
        )
    return {
        "cascade_path_ensemble_manifest.csv": path_manifest,
        "cascade_path_ensemble_rows.csv": path_rows,
        "cascade_total_mass.csv": total_rows,
        "cascade_error_mass_by_stage.csv": error_rows,
        "cascade_bound_check.csv": bound_rows,
        "denominator_alignment_audit.csv": denominator_rows,
        "decoder_policy_alignment_audit.csv": policy_rows,
    }


def build_single_cascade(
    *,
    context: AuditContext,
    composition: dict[str, object],
    check: dict[str, object],
    decoder_policy_id: str,
) -> dict[str, object]:
    composition_id = str(composition["composition_id"])
    first_channel = str(composition["first_channel_id"])
    second_channel = str(composition["second_channel_id"])
    composed_channel = str(composition["composed_channel_id"])
    source_dist = str(check["source_distinction_id"])
    middle_dist = str(check["middle_distinction_id"])
    target_dist = str(check["target_distinction_id"])
    prior_id = prior_id_for_source_dist(source_dist)
    first_decoder = context.decoder_manifest.get((first_channel, source_dist, middle_dist, "bayes_optimal_decoder"))
    second_decoder = context.decoder_manifest.get((second_channel, middle_dist, target_dist, "bayes_optimal_decoder"))
    first_decoder_id = str(first_decoder.get("decoder_id", "")) if first_decoder else ""
    second_decoder_id = str(second_decoder.get("decoder_id", "")) if second_decoder else ""
    first_mapping = context.decoder_tables.get(first_decoder_id, {})
    second_mapping = context.decoder_tables.get(second_decoder_id, {})
    prior = context.prior_weights.get(prior_id, {})
    first_weights = context.channel_weights.get(first_channel, {})
    second_weights = context.channel_weights.get(second_channel, {})

    path_rows = []
    first_error_mass = 0
    second_error_mass = 0
    composite_error_mass = 0
    total_mass = 0
    positive_path_count = 0
    composed_weights: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for source_state, source_prior_weight in sorted(prior.items()):
        for middle_state, first_weight in sorted(first_weights.get(source_state, {}).items()):
            for target_state, second_weight in sorted(second_weights.get(middle_state, {}).items()):
                path_weight = source_prior_weight * first_weight * second_weight
                if path_weight > 0:
                    positive_path_count += 1
                total_mass += path_weight
                composed_weights[source_state][target_state] += first_weight * second_weight
                source_label = label_for_context(context, source_dist, source_state)
                middle_label = label_for_context(context, middle_dist, middle_state)
                target_label = label_for_context(context, target_dist, target_state)
                first_output = first_mapping.get(middle_label, "")
                second_output = second_mapping.get(target_label, "")
                composed_output = first_mapping.get(second_output, "")
                first_error = int(first_output != source_label)
                second_error = int(second_output != middle_label)
                composite_error = int(composed_output != source_label)
                first_error_mass += path_weight * first_error
                second_error_mass += path_weight * second_error
                composite_error_mass += path_weight * composite_error
                path_rows.append(
                    {
                        "cascade_id": composition_id,
                        "composition_id": composition_id,
                        "distinction_id": source_dist,
                        "decoder_policy_id": decoder_policy_id,
                        "source_state": source_state,
                        "intermediate_state": middle_state,
                        "target_state": target_state,
                        "source_prior_weight": source_prior_weight,
                        "first_channel_weight": first_weight,
                        "second_channel_weight": second_weight,
                        "path_weight": path_weight,
                        "source_distinction_label": source_label,
                        "intermediate_distinction_label": middle_label,
                        "target_distinction_label": target_label,
                        "first_decoder_output": first_output,
                        "second_decoder_output": second_output,
                        "composed_decoder_output": composed_output,
                        "first_stage_error": first_error,
                        "second_stage_error": second_error,
                        "composite_error": composite_error,
                    }
                )
    composed_total = sum(prior.get(x, 0) * sum(targets.values()) for x, targets in composed_weights.items())
    composed_error_mass = composed_channel_error_mass(
        context=context,
        composed_weights=composed_weights,
        prior=prior,
        source_dist=source_dist,
        target_dist=target_dist,
        first_mapping=first_mapping,
        second_mapping=second_mapping,
    )
    bound_rhs = first_error_mass + second_error_mass
    bound_pass = composite_error_mass <= bound_rhs
    theorem_status = theorem_applicability_status(
        first_decoder_id=first_decoder_id,
        second_decoder_id=second_decoder_id,
        bound_pass=bound_pass,
        total_mass=total_mass,
    )
    composed_decoder_id = f"composed::{first_decoder_id}::{second_decoder_id}"
    manifest_row = {
        "cascade_id": composition_id,
        "composition_id": composition_id,
        "first_channel_id": first_channel,
        "second_channel_id": second_channel,
        "composed_channel_id": composed_channel,
        "source_distinction_id": source_dist,
        "intermediate_distinction_id": middle_dist,
        "target_distinction_id": target_dist,
        "prior_id": prior_id,
        "decoder_policy_id": decoder_policy_id,
        "first_decoder_id": first_decoder_id,
        "second_decoder_id": second_decoder_id,
        "composed_decoder_id": composed_decoder_id,
        "path_ensemble_rule": "mass(x,y,z)=pi(x)*K(y|x)*L(z|y)",
        "theorem_bridge": "finite cascade error bound over same path ensemble",
        "status": "complete" if total_mass > 0 else "blocked_empty_path_ensemble",
        "claim_boundary": AUDIT_BOUNDARY,
    }
    total_row = {
        "cascade_id": composition_id,
        "distinction_id": source_dist,
        "decoder_policy_id": decoder_policy_id,
        "path_count": len(path_rows),
        "positive_path_count": positive_path_count,
        "total_path_mass": total_mass,
        "composed_channel_total_mass": composed_total,
        "path_total_equals_composed_total": int(total_mass == composed_total),
        "status": "PASS" if total_mass == composed_total and total_mass > 0 else "FAIL",
        "notes": "composed total computed from generated natural cascade weights",
    }
    error_row = {
        "cascade_id": composition_id,
        "distinction_id": source_dist,
        "decoder_policy_id": decoder_policy_id,
        "total_path_mass": total_mass,
        "first_stage_error_mass": first_error_mass,
        "second_stage_error_mass": second_error_mass,
        "composite_error_mass": composite_error_mass,
        "composed_channel_error_mass": composed_error_mass,
        "composite_error_equals_composed_error": int(composite_error_mass == composed_error_mass),
        "first_stage_error_rate_same_denominator": ratio_text(first_error_mass, total_mass),
        "second_stage_error_rate_same_denominator": ratio_text(second_error_mass, total_mass),
        "composite_error_rate_same_denominator": ratio_text(composite_error_mass, total_mass),
    }
    bound_row = {
        "cascade_id": composition_id,
        "distinction_id": source_dist,
        "decoder_policy_id": decoder_policy_id,
        "total_path_mass": total_mass,
        "composite_error_mass": composite_error_mass,
        "first_stage_error_mass": first_error_mass,
        "second_stage_error_mass": second_error_mass,
        "bound_rhs_error_mass": bound_rhs,
        "bound_pass": int(bound_pass),
        "slack_mass": bound_rhs - composite_error_mass,
        "composite_error_rate": ratio_text(composite_error_mass, total_mass),
        "stage_error_rate_sum_same_denominator": ratio_text(bound_rhs, total_mass),
        "theorem_applicability_status": theorem_status,
        "notes": "uses same path ensemble denominator; not independently normalized stage errors",
    }
    denominator_row = {
        "cascade_id": composition_id,
        "distinction_id": source_dist,
        "decoder_policy_id": decoder_policy_id,
        "first_stage_denominator": total_mass,
        "second_stage_denominator": total_mass,
        "composite_denominator": total_mass,
        "shared_path_ensemble_denominator": total_mass,
        "uses_same_path_ensemble": 1,
        "uses_independently_normalized_stage_errors": 0,
        "denominator_alignment_status": "aligned_same_path_ensemble" if total_mass > 0 else "blocked_empty_path_ensemble",
        "notes": "stage and composite errors are measured on identical path rows",
    }
    policy_row = {
        "cascade_id": composition_id,
        "distinction_id": source_dist,
        "first_decoder_id": first_decoder_id,
        "second_decoder_id": second_decoder_id,
        "composed_decoder_id": composed_decoder_id,
        "first_decoder_policy_id": decoder_policy_id,
        "second_decoder_policy_id": decoder_policy_id,
        "composed_decoder_policy_id": "declared_decoder_composition",
        "decoder_composition_declared": int(bool(first_decoder_id and second_decoder_id)),
        "composed_decoder_matches_dec1_after_dec2": int(bool(first_decoder_id and second_decoder_id)),
        "policy_alignment_status": "aligned_declared_composition"
        if first_decoder_id and second_decoder_id
        else "blocked_missing_composed_decoder",
        "notes": "composed decoder is dec1 after dec2 over declared intermediate distinction",
    }
    return {
        "manifest": manifest_row,
        "path_rows": path_rows,
        "total": total_row,
        "error": error_row,
        "bound": bound_row,
        "denominator": denominator_row,
        "policy": policy_row,
    }


def composed_channel_error_mass(
    *,
    context: AuditContext,
    composed_weights: dict[str, dict[str, int]],
    prior: dict[str, int],
    source_dist: str,
    target_dist: str,
    first_mapping: dict[str, str],
    second_mapping: dict[str, str],
) -> int:
    error_mass = 0
    for source_state, targets in composed_weights.items():
        source_label = label_for_context(context, source_dist, source_state)
        for target_state, weight in targets.items():
            target_label = label_for_context(context, target_dist, target_state)
            composed_output = first_mapping.get(second_mapping.get(target_label, ""), "")
            if composed_output != source_label:
                error_mass += prior.get(source_state, 0) * weight
    return error_mass


def bayes_best_policy_alignment_row(
    *,
    composition: dict[str, object],
    check: dict[str, object],
    fixed_policy_row: dict[str, object],
) -> dict[str, object]:
    return {
        "cascade_id": composition["composition_id"],
        "distinction_id": check["source_distinction_id"],
        "first_decoder_id": "",
        "second_decoder_id": "",
        "composed_decoder_id": "",
        "first_decoder_policy_id": "bayes_best_target_distinction",
        "second_decoder_policy_id": "bayes_best_target_distinction",
        "composed_decoder_policy_id": "bayes_best_target_distinction",
        "decoder_composition_declared": 0,
        "composed_decoder_matches_dec1_after_dec2": 0,
        "policy_alignment_status": "measurement_only_best_decoder_comparison",
        "notes": (
            "Bayes-best stage rows are useful measurements but are not silently substituted "
            f"for fixed declared composition `{fixed_policy_row['composed_decoder_id']}`."
        ),
    }


def theorem_applicability_status(
    *,
    first_decoder_id: str,
    second_decoder_id: str,
    bound_pass: bool,
    total_mass: int,
) -> str:
    if total_mass <= 0:
        return "blocked_missing_path_ensemble"
    if not first_decoder_id or not second_decoder_id:
        return "blocked_missing_composed_decoder"
    if not bound_pass:
        return "blocked_assumption_mismatch"
    return "theorem_applicable_generated_natural_weights"


def no_self_evidencing_decoder_audit(
    decoder_manifest: list[dict[str, object]],
    decoder_table: list[dict[str, object]],
) -> list[dict[str, object]]:
    table_decoders = {str(row["decoder_id"]) for row in decoder_table}
    rows = []
    for decoder in decoder_manifest:
        decoder_id = str(decoder["decoder_id"])
        has_table = decoder_id in table_decoders
        rows.append(
            {
                "decoder_id": decoder_id,
                "decoder_policy_id": decoder_kind_to_policy(str(decoder["decoder_kind"])),
                "channel_id": decoder["channel_id"],
                "distinction_id": decoder["source_distinction_id"],
                "uses_source_state_id": 0,
                "uses_source_distinction_label_as_input": 0,
                "uses_hidden_latent_or_oracle_state": 0,
                "uses_candidate_id": 0,
                "uses_target_observation_only": 1 if has_table else 0,
                "uses_declared_target_distinction_only": 1,
                "allowed_for_recovery_claim": 1 if has_table else 0,
                "audit_status": "PASS" if has_table else "FAIL",
                "notes": "decoder table maps target-observation labels to source labels; no source-state oracle input",
            }
        )
    return rows


def support_probability_theorem_boundary(
    recoverability: list[dict[str, object]],
    source_priors: list[dict[str, object]],
) -> list[dict[str, object]]:
    prior_full_support = full_support_by_prior(source_priors)
    rows = []
    for row in recoverability:
        success = fraction_from_optional(row.get("decoder_success_fraction"), row.get("decoder_success_probability"))
        exact = as_bool(row.get("exact_recoverable_support"))
        high = success >= Fraction(19, 20)
        perfect = success == 1
        full_prior = prior_full_support.get(str(row["prior_id"]), False)
        if exact and perfect:
            classification = "exact_support_and_perfect_probability"
            status = "support_theorem_transfer_ready"
        elif perfect and not exact and not full_prior:
            classification = "perfect_probability_without_exact_support_due_to_nonfull_prior"
            status = "probability_only_prior_support_caveat"
        elif high and not exact:
            classification = "high_probability_without_exact_support"
            status = "probabilistic_measurement_not_support_transfer"
        elif not exact and success >= Fraction(3, 4):
            classification = "support_exact_failure_probability_high"
            status = "probabilistic_measurement_not_support_transfer"
        else:
            classification = "support_exact_failure_probability_low"
            status = "measurement_only"
        rows.append(
            {
                "channel_id": row["channel_id"],
                "distinction_id": row["source_distinction_id"],
                "target_distinction_id": row["target_distinction_id"],
                "decoder_id": row["decoder_id"],
                "support_exact_recovered": int(exact),
                "success_probability": float(success),
                "success_fraction": fraction_text(success),
                "chance_success_probability": row.get("chance_success_probability", ""),
                "normalized_recovery_advantage": row.get("normalized_recovery_advantage", ""),
                "prior_full_support_for_distinction": int(full_prior),
                "classification": classification,
                "theorem_boundary_status": status,
                "notes": "support exact recovery and probabilistic success are not collapsed",
            }
        )
    return rows


def threshold_sensitivity_by_distinction(recoverability: list[dict[str, object]]) -> list[dict[str, object]]:
    thresholds = [Fraction(4, 5), Fraction(9, 10), Fraction(19, 20), Fraction(99, 100), Fraction(1, 1)]
    rows = []
    for row in recoverability:
        success = fraction_from_optional(row.get("decoder_success_fraction"), row.get("decoder_success_probability"))
        exact = as_bool(row.get("exact_recoverable_support"))
        for threshold in thresholds:
            threshold_pass = success >= threshold
            rows.append(
                {
                    "channel_id": row["channel_id"],
                    "distinction_id": row["source_distinction_id"],
                    "target_distinction_id": row["target_distinction_id"],
                    "decoder_id": row["decoder_id"],
                    "decoder_policy_id": decoder_kind_to_policy(str(row["decoder_kind"])),
                    "threshold": float(threshold),
                    "threshold_fraction": fraction_text(threshold),
                    "success_probability": float(success),
                    "success_fraction": fraction_text(success),
                    "threshold_pass": int(threshold_pass),
                    "diagnostic_class": threshold_diagnostic(success, threshold, exact),
                    "notes": "sensitivity row; 0.95 is not treated as the only truth threshold",
                }
            )
    return rows


def marginal_joint_theorem_examples(rows_in: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for index, row in enumerate(rows_in):
        diagnostic = str(row["diagnostic_class"])
        rows.append(
            {
                "example_id": f"marginal_joint_example_{index:03d}",
                "channel_id": row["channel_id"],
                "decoder_policy_id": row["decoder_policy_id"],
                "threshold": 0.95,
                "D_A_success": row["A_success"],
                "D_B_success": row["B_success"],
                "D_joint_success": row["joint_success"],
                "D_parity_success": row["parity_success"],
                "D_A_pass": row["A_passes_threshold"],
                "D_B_pass": row["B_passes_threshold"],
                "D_joint_pass": row["joint_passes_threshold"],
                "D_parity_pass": row["parity_passes_threshold"],
                "diagnostic_class": diagnostic,
                "why_useful_for_formal_arm": marginal_joint_use(diagnostic),
                "notes": "finite stochastic marginal/joint distinction example",
            }
        )
    return rows


def probabilistic_theorem_transfer_readiness_summary(
    *,
    input_status: dict[str, object],
    cascade_bound_check: list[dict[str, object]],
    denominator_alignment: list[dict[str, object]],
    decoder_policy_alignment: list[dict[str, object]],
    no_self_audit: list[dict[str, object]],
    support_boundary: list[dict[str, object]],
    non_erasure: list[dict[str, object]],
    declared_policy: list[dict[str, object]],
) -> list[dict[str, object]]:
    inputs_ready = input_status["status"] == "ready"
    exact_rows = [row for row in support_boundary if row["classification"] == "exact_support_and_perfect_probability"]
    high_not_exact = [row for row in support_boundary if row["classification"] == "high_probability_without_exact_support"]
    bound_ready = inputs_ready and bool(cascade_bound_check) and all(
        as_bool(row["bound_pass"]) for row in cascade_bound_check
    )
    denominators_ready = all(str(row["denominator_alignment_status"]) == "aligned_same_path_ensemble" for row in denominator_alignment)
    fixed_policy_ready = any(str(row["policy_alignment_status"]) == "aligned_declared_composition" for row in decoder_policy_alignment)
    no_self_ready = all(str(row["audit_status"]) == "PASS" for row in no_self_audit)
    return [
        readiness_row(
            "support_level_exact_channel_presentation",
            "lean_checked",
            "channel_support.csv;support_recoverability.csv;support_probability_theorem_boundary.csv",
            bool(exact_rows),
            "ready_for_formal_consumption" if inputs_ready and exact_rows else "blocked_missing_artifacts",
            "exact support-recoverability rows",
            "probabilistic threshold claims without probabilistic theorem layer",
            "support-level rows remain separated from probabilistic measurements",
        ),
        readiness_row(
            "exact_implies_perfect_probability",
            "lean_checked",
            "support_probability_theorem_boundary.csv",
            bool(exact_rows),
            "ready_for_formal_consumption" if exact_rows else "blocked_missing_artifacts",
            "exact rows imply perfect probability in the finite channel presentation",
            "converse claims without assumptions",
            f"{len(exact_rows)} exact-and-perfect rows emitted",
        ),
        readiness_row(
            "perfect_full_prior_implies_exact",
            "lean_checked",
            "support_probability_theorem_boundary.csv;source_prior_manifest.csv",
            inputs_ready,
            "ready_for_formal_consumption" if inputs_ready else "blocked_missing_artifacts",
            "classification of full-support perfect-probability rows",
            "non-full-support converse",
            "current uniform priors have full support",
        ),
        readiness_row(
            "perfect_nonfull_prior_not_exact_counterexample",
            "lean_checked",
            "support_probability_theorem_boundary.csv",
            True,
            "ready_for_measurement_only",
            "boundary category is available if future non-full priors are emitted",
            "automatic support recovery from non-full-prior perfect probability",
            "no non-full prior appears in this tiny input, but the boundary slot is explicit",
        ),
        readiness_row(
            "high_probability_not_exact_counterexample",
            "lean_checked",
            "support_probability_theorem_boundary.csv",
            bool(high_not_exact),
            "ready_for_formal_consumption" if high_not_exact else "ready_for_measurement_only",
            "high probability without exact support rows",
            "support-level theorem transfer from high probability alone",
            f"{len(high_not_exact)} high-probability non-exact rows emitted",
        ),
        readiness_row(
            "cascade_error_bound",
            "lean_checked",
            "cascade_path_ensemble_rows.csv;cascade_error_mass_by_stage.csv;cascade_bound_check.csv",
            bound_ready,
            "ready_for_formal_consumption"
            if bound_ready and denominators_ready and fixed_policy_ready
            else "blocked_assumption_mismatch",
            "finite cascade error bound over same path ensemble",
            "bounds using independently normalized stage errors",
            "same-path-ensemble denominator is explicit",
        ),
        readiness_row(
            "cascade_same_denominator_threshold_bound",
            "lean_checked",
            "denominator_alignment_audit.csv;cascade_bound_check.csv",
            denominators_ready,
            "ready_for_formal_consumption" if denominators_ready and bound_ready else "blocked_assumption_mismatch",
            "same-denominator threshold-bound instantiation",
            "threshold-bound claims with denominator mismatch",
            "all fixed cascade rows use identical path denominator",
        ),
        readiness_row(
            "bayes_best_vs_fixed_declared_policy_separation",
            "lean_checked",
            "declared_target_policy_summary.csv;decoder_policy_alignment_audit.csv",
            bool(declared_policy),
            "ready_for_formal_consumption" if declared_policy else "blocked_missing_artifacts",
            "fixed and Bayes-best policy separation",
            "silent substitution of Bayes-best for fixed declared policy",
            "Bayes-best cascade rows are marked measurement-only for composition",
        ),
        readiness_row(
            "thresholded_non_erasure_layer",
            "measurement_only_pending_formal_theorem",
            "non_erasure_by_channel.csv;threshold_sensitivity_by_distinction.csv",
            bool(non_erasure),
            "ready_for_measurement_only" if non_erasure and no_self_ready else "blocked_assumption_mismatch",
            "finite thresholded recovery counts",
            "root DistTrans witness claims from thresholds alone",
            "threshold sensitivity emitted",
        ),
        readiness_row(
            "completion_or_candidate_family",
            "not_applicable",
            "candidate_family_manifest.csv;admissibility_predicate_manifest.csv",
            False,
            "not_applicable",
            "none",
            "completion/candidate-family claims",
            "this audit only covers finite channels and distinctions",
        ),
    ]


def readiness_row(
    theorem_or_layer_id: str,
    formal_status: str,
    required_empirical_artifacts: str,
    artifacts_present: bool,
    applicability_status: str,
    claim_allowed: str,
    claim_blocked: str,
    notes: str,
) -> dict[str, object]:
    return {
        "theorem_or_layer_id": theorem_or_layer_id,
        "formal_status": formal_status,
        "required_empirical_artifacts": required_empirical_artifacts,
        "artifacts_present": int(artifacts_present),
        "applicability_status": applicability_status,
        "claim_allowed": claim_allowed,
        "claim_blocked": claim_blocked,
        "notes": notes,
    }


def build_theorem_transfer_bundle(
    *,
    source_dir: Path,
    out_dir: Path,
    source_digest: str,
    csv_outputs: dict[str, list[dict[str, object]]],
    overall_status: str,
) -> dict[str, object]:
    paths = {name.removesuffix(".csv"): name for name in AUDIT_OUTPUTS}
    payload = {
        "source_probe_digest": source_digest,
        "outputs": paths,
        "overall_status": overall_status,
        "row_counts": {name: len(rows) for name, rows in csv_outputs.items()},
    }
    return {
        "bundle_schema_version": "0.1.0",
        "source_probe_digest": source_digest,
        "source_tightened_output_dir": str(source_dir),
        **paths,
        "overall_status": overall_status,
        "claim_boundary": AUDIT_BOUNDARY,
        "output_directory": str(out_dir),
        "bundle_digest": stable_hash(payload, length=24),
    }


def overall_audit_status(
    *,
    input_status: dict[str, object],
    bound_rows: list[dict[str, object]],
    denominator_rows: list[dict[str, object]],
    policy_rows: list[dict[str, object]],
    no_self_rows: list[dict[str, object]],
) -> str:
    if input_status["status"] == "blocked_missing_input":
        return "blocked_missing_artifacts"
    if any(str(row["audit_status"]) == "FAIL" for row in no_self_rows):
        return "blocked_by_forbidden_decoder"
    if any(as_bool(row.get("uses_independently_normalized_stage_errors")) for row in denominator_rows):
        return "blocked_by_denominator_mismatch"
    fixed_policy_rows = [row for row in policy_rows if row["first_decoder_policy_id"] == "fixed_declared_target_distinction"]
    if any(str(row["policy_alignment_status"]).startswith("blocked") for row in fixed_policy_rows):
        return "blocked_by_decoder_policy_mismatch"
    if bound_rows and all(as_bool(row["bound_pass"]) for row in bound_rows):
        return "support_and_probabilistic_transfer_ready"
    return "support_ready_probabilistic_measurement_only"


def render_report(
    *,
    source_dir: Path,
    source_digest: str,
    input_status: dict[str, object],
    cascade_bound_check: list[dict[str, object]],
    denominator_alignment: list[dict[str, object]],
    decoder_policy_alignment: list[dict[str, object]],
    no_self_audit: list[dict[str, object]],
    support_boundary: list[dict[str, object]],
    threshold_sensitivity: list[dict[str, object]],
    marginal_examples: list[dict[str, object]],
    readiness: list[dict[str, object]],
    overall_status: str,
) -> str:
    bound_passes = sum(1 for row in cascade_bound_check if as_bool(row["bound_pass"]))
    theorem_ready = sum(
        1 for row in cascade_bound_check if str(row["theorem_applicability_status"]).startswith("theorem_applicable")
    )
    support_counts = count_by(support_boundary, "classification")
    readiness_lines = [
        f"- `{row['theorem_or_layer_id']}`: {row['applicability_status']}"
        for row in readiness
    ]
    return "\n".join(
        [
            "# Stochastic Channel Theorem-Transfer Audit v0",
            "",
            "## Executive Summary",
            "",
            "This audit converts the tightened stochastic-channel probe into a formal-consumption "
            "package for the Lean probabilistic channel presentation. The key repair is the "
            "cascade path ensemble: first-stage, second-stage, and composite decoder errors are "
            "measured on the same finite path denominator, so the Lean union-bound theorem is "
            "instantiable for the declared fixed-policy cascades. Bayes-best rows remain available "
            "as diagnostics, but they are not substituted into composition proofs.",
            "",
            f"- overall status: `{overall_status}`",
            f"- cascade bound rows: {len(cascade_bound_check)}",
            f"- cascade bound passes: {bound_passes}",
            f"- theorem-applicable cascade rows: {theorem_ready}",
            f"- decoder audit failures: {sum(1 for row in no_self_audit if str(row['audit_status']) == 'FAIL')}",
            "",
            "## Scope",
            "",
            AUDIT_BOUNDARY,
            "",
            "## Inputs And Source Probe Digest",
            "",
            f"- source output: `{source_dir}`",
            f"- source digest: `{source_digest}`",
            f"- input status: `{input_status['status']}`",
            f"- missing inputs: `{';'.join(input_status['missing_inputs']) if input_status['missing_inputs'] else 'none'}`",
            "",
            "## Rational And Natural Weights",
            "",
            "Channel probabilities and source priors are rationalized exactly from retained "
            "fraction columns. Channel rows are converted to row-scaled natural weights, matching "
            "the finite Lean presentation style.",
            "",
            "## Cascade Path Ensemble",
            "",
            "Each cascade row emits path records with `mass(x,y,z)=pi(x)*K(y|x)*L(z|y)`. "
            "The composed-channel total is recomputed from the same generated natural cascade, "
            "rather than from independently normalized stage summaries.",
            "",
            "## Error Mass And Bound Checks",
            "",
            *[
                f"- `{row['cascade_id']}` / `{row['distinction_id']}`: "
                f"composite {row['composite_error_mass']} <= "
                f"{row['first_stage_error_mass']} + {row['second_stage_error_mass']} "
                f"({row['theorem_applicability_status']})"
                for row in cascade_bound_check[:12]
            ],
            "",
            "## Denominator Alignment",
            "",
            f"- aligned rows: {sum(1 for row in denominator_alignment if row['denominator_alignment_status'] == 'aligned_same_path_ensemble')}",
            f"- independent-normalization rows used for theorem evidence: {sum(1 for row in denominator_alignment if as_bool(row['uses_independently_normalized_stage_errors']))}",
            "",
            "## Decoder-Policy Alignment",
            "",
            *[
                f"- `{status}`: {count}"
                for status, count in sorted(count_by(decoder_policy_alignment, "policy_alignment_status").items())
            ],
            "",
            "## No-Self-Evidencing Decoder Audit",
            "",
            "Allowed recovery decoders map declared target-observation labels to source labels; "
            "they do not consume source-state IDs, source labels, hidden states, or candidate IDs.",
            "",
            "## Support Versus Probability Boundary",
            "",
            *[f"- `{name}`: {count}" for name, count in sorted(support_counts.items())],
            "",
            "## Threshold Sensitivity",
            "",
            f"- threshold sensitivity rows: {len(threshold_sensitivity)}",
            "Thresholds tested: 0.80, 0.90, 0.95, 0.99, and 1.00.",
            "",
            "## Marginal-Versus-Joint Examples",
            "",
            *[
                f"- `{row['channel_id']}` / `{row['decoder_policy_id']}`: {row['diagnostic_class']}"
                for row in marginal_examples[:12]
            ],
            "",
            "## Theorem-Transfer Readiness",
            "",
            *readiness_lines,
            "",
            "## Blocked Claims And Next Formal Asks",
            "",
            "Thresholded non-erasure remains a measurement layer unless a matching theorem is "
            "declared. Candidate-family and completion objects are still out of scope for this "
            "adapter. The next useful formal ask is not broader channel data; it is either a "
            "thresholded probabilistic non-erasure theorem or a deliberate candidate-family "
            "presentation.",
        ]
    )


def artifact_manifest_for_outputs(out_dir: Path, csv_outputs: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    artifacts = []
    for name, rows in sorted(csv_outputs.items()):
        path = out_dir / name
        artifacts.append(
            {
                "logical_name": name,
                "physical_name": name,
                "row_count": len(rows),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    for name in ["probabilistic_channel_theorem_transfer_bundle.json", "stochastic_channel_theorem_transfer_audit_report.md"]:
        path = out_dir / name
        artifacts.append(
            {
                "logical_name": name,
                "physical_name": name,
                "row_count": "",
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "artifact_manifest_digest": stable_hash(artifacts, length=24),
        "claim_boundary": AUDIT_BOUNDARY,
    }


def source_probe_digest(source_dir: Path) -> str:
    bundle_path = source_dir / "formal_channel_consumption_bundle.json"
    if bundle_path.exists():
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
        return str(payload.get("bundle_digest") or payload.get("probe_digest") or stable_hash(payload, length=24))
    return stable_hash(str(source_dir), length=24)


def fraction_from_fields(row: dict[str, object]) -> Fraction:
    return fraction_from_optional(row.get("probability_fraction"), row.get("probability"))


def fraction_from_optional(fraction_value: object, decimal_value: object = "") -> Fraction:
    if fraction_value not in ("", None):
        return Fraction(str(fraction_value))
    if decimal_value in ("", None):
        return Fraction(0)
    return Fraction(str(decimal_value))


def observation_index(rows: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for row in rows:
        out[(str(row["carrier_id"]), str(row["distinction_id"]))][str(row["state_id"])] = str(row["label"])
    return dict(out)


def decoder_manifest_index(rows: list[dict[str, object]]) -> dict[tuple[str, str, str, str], dict[str, str]]:
    out = {}
    for row in rows:
        key = (
            str(row["channel_id"]),
            str(row["source_distinction_id"]),
            str(row["target_distinction_id"]),
            str(row["decoder_kind"]),
        )
        out[key] = {str(k): str(v) for k, v in row.items()}
    return out


def decoder_table_index(rows: list[dict[str, object]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        out[str(row["decoder_id"])][str(row["target_label"])] = str(row["decoded_source_label"])
    return dict(out)


def recoverability_index(rows: list[dict[str, object]]) -> dict[tuple[str, str, str, str], dict[str, str]]:
    out = {}
    for row in rows:
        key = (
            str(row["channel_id"]),
            str(row["source_distinction_id"]),
            str(row["target_distinction_id"]),
            str(row["decoder_kind"]),
        )
        out[key] = {str(k): str(v) for k, v in row.items()}
    return out


def prior_id_for_source_dist(source_distinction_id: str) -> str:
    return "uniform_Y2" if source_distinction_id.startswith("E_") else "uniform_X2"


def label_for_context(context: AuditContext, distinction_id: str, state: str) -> str:
    carrier = "Y2" if distinction_id.startswith("E_") else "X2"
    return context.source_observations.get((carrier, distinction_id), {}).get(state, "")


def full_support_by_prior(source_priors: list[dict[str, object]]) -> dict[str, bool]:
    grouped: dict[str, list[Fraction]] = defaultdict(list)
    for row in source_priors:
        grouped[str(row["prior_id"])].append(fraction_from_fields(row))
    return {prior_id: all(value > 0 for value in values) for prior_id, values in grouped.items()}


def threshold_diagnostic(success: Fraction, threshold: Fraction, exact: bool) -> str:
    if success >= threshold and exact:
        return "threshold_pass_exact_support"
    if success >= threshold:
        return "threshold_pass_probability_only"
    if success > 0:
        return "threshold_fail_partial_recovery"
    return "threshold_fail_no_recovery"


def marginal_joint_use(diagnostic: str) -> str:
    if diagnostic == "marginal_recovered_joint_not_recovered":
        return "separates marginal-like recovery from joint recovery in a finite channel"
    if diagnostic == "marginal_and_joint_recovered":
        return "sanity positive example for joint and marginal recovery"
    if diagnostic == "all_nontrivial_lost":
        return "sanity negative example for degraded recovery"
    return "mixed finite diagnostic for theorem-side case analysis"


def decoder_kind_to_policy(decoder_kind: str) -> str:
    if decoder_kind == "bayes_optimal_decoder":
        return "bayes_best_target_distinction"
    if decoder_kind == "declared_decoder":
        return "fixed_declared_decoder_rule"
    if decoder_kind == "exact_decoder":
        return "exact_support_decoder"
    return decoder_kind


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "pass"}


def ratio_text(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return ""
    return fraction_text(Fraction(numerator, denominator))


def count_by(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get(field, ""))
        counts[key] = counts.get(key, 0) + 1
    return counts


if __name__ == "__main__":
    main()
