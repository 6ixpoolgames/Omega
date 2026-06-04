"""Thresholded probabilistic non-erasure compiler for stochastic channel outputs."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from omega.future_field_atlas.util import read_csv, stable_hash, write_csv, write_json

from .schema import DEFAULT_OUT, fraction_text
from .theorem_transfer_audit import (
    DEFAULT_AUDIT_OUT,
    as_bool,
    fraction_from_optional,
)


DEFAULT_OUT_DIR = Path("results/stochastic_distinction_channel/20260604_thresholded_prob_non_erasure_v0")
CLAIM_BOUNDARY = (
    "finite thresholded probabilistic non-erasure measurement and formal-consumption preparation only"
)
FIXED_POLICY = "fixed_declared_target_policy"
BAYES_POLICY = "bayes_best_target_policy"
THRESHOLDS = [
    ("threshold_0_80", Fraction(4, 5)),
    ("threshold_0_90", Fraction(9, 10)),
    ("threshold_0_95", Fraction(19, 20)),
    ("threshold_0_99", Fraction(99, 100)),
    ("threshold_1_00", Fraction(1, 1)),
]
REQUIREMENTS = [
    ("req_A", "A distinction", ["D_A"]),
    ("req_B", "B distinction", ["D_B"]),
    ("req_marginals", "A and B marginal distinctions", ["D_A", "D_B"]),
    ("req_joint", "joint pair distinction", ["D_joint"]),
    ("req_parity", "parity distinction", ["D_parity"]),
    ("req_joint_and_parity", "joint and parity distinctions", ["D_joint", "D_parity"]),
    ("req_all_nontrivial", "all declared nontrivial distinctions", ["D_A", "D_B", "D_joint", "D_parity"]),
]
AUDIT_INPUTS = [
    "probabilistic_channel_theorem_transfer_bundle.json",
    "no_self_evidencing_decoder_audit.csv",
    "support_probability_theorem_boundary.csv",
    "probabilistic_theorem_transfer_readiness_summary.csv",
]
SOURCE_INPUTS = [
    "channel_probe_manifest.json",
    "artifact_manifest.json",
    "channel_manifest.csv",
    "distinction_manifest.csv",
    "decoder_manifest.csv",
    "decoder_policy_manifest.csv",
    "decoder_table.csv",
    "threshold_manifest.csv",
    "recoverability_by_distinction.csv",
    "non_erasure_requirement_manifest.csv",
    "non_erasure_by_channel.csv",
    "marginal_joint_recoverability_diagnostic.csv",
    "declared_target_policy_summary.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile thresholded probabilistic non-erasure artifacts.")
    parser.add_argument("--audit-source", type=Path, default=DEFAULT_AUDIT_OUT)
    parser.add_argument("--probe-source", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_thresholded_non_erasure(
        audit_source=args.audit_source,
        probe_source=args.probe_source,
        out_dir=args.out,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_thresholded_non_erasure(*, audit_source: Path, probe_source: Path, out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_tables = {name: read_input_csv(audit_source, name) for name in AUDIT_INPUTS if name.endswith(".csv")}
    probe_tables = {name: read_input_csv(probe_source, name) for name in SOURCE_INPUTS if name.endswith(".csv")}
    missing_inputs = missing_input_files(audit_source, AUDIT_INPUTS) + missing_input_files(probe_source, SOURCE_INPUTS)
    input_status = "blocked_missing_input" if missing_inputs else "ready"

    requirement_rows = probabilistic_requirement_manifest()
    subset_rows = requirement_subset_manifest(requirement_rows)
    threshold_rows = probabilistic_threshold_manifest()
    context = ThresholdContext(
        probe_source=probe_source,
        audit_source=audit_source,
        channel_rows=probe_tables.get("channel_manifest.csv", []),
        recoverability_rows=probe_tables.get("recoverability_by_distinction.csv", []),
        declared_policy_rows=probe_tables.get("declared_target_policy_summary.csv", []),
        decoder_manifest_rows=probe_tables.get("decoder_manifest.csv", []),
        no_self_rows=audit_tables.get("no_self_evidencing_decoder_audit.csv", []),
        support_boundary_rows=audit_tables.get("support_probability_theorem_boundary.csv", []),
    )
    eligibility_rows = prob_non_erasure_decoder_eligibility(context)
    recovery_rows = thresholded_prob_recovery_by_distinction(context, eligibility_rows)
    non_erasure_rows = thresholded_prob_non_erasure_by_channel(
        context=context,
        requirement_rows=requirement_rows,
        recovery_rows=recovery_rows,
    )
    monotonicity_rows = prob_non_erasure_monotonicity_check(
        subset_rows=subset_rows,
        non_erasure_rows=non_erasure_rows,
    )
    threshold_sensitivity_rows = threshold_sensitivity_by_requirement(non_erasure_rows)
    marginal_joint_rows = thresholded_marginal_joint_summary(
        recovery_rows=recovery_rows,
        non_erasure_rows=non_erasure_rows,
    )
    support_boundary_rows = thresholded_support_probability_boundary(
        requirement_rows=requirement_rows,
        recovery_rows=recovery_rows,
        non_erasure_rows=non_erasure_rows,
    )
    theorem_summary_rows = probabilistic_non_erasure_theorem_transfer_summary(
        input_status=input_status,
        non_erasure_rows=non_erasure_rows,
        monotonicity_rows=monotonicity_rows,
        support_boundary_rows=support_boundary_rows,
    )
    status = overall_status(
        input_status=input_status,
        eligibility_rows=eligibility_rows,
        monotonicity_rows=monotonicity_rows,
    )

    csv_outputs: dict[str, list[dict[str, object]]] = {
        "probabilistic_requirement_manifest.csv": requirement_rows,
        "requirement_subset_manifest.csv": subset_rows,
        "probabilistic_threshold_manifest.csv": threshold_rows,
        "prob_non_erasure_decoder_eligibility.csv": eligibility_rows,
        "thresholded_prob_recovery_by_distinction.csv": recovery_rows,
        "thresholded_prob_non_erasure_by_channel.csv": non_erasure_rows,
        "prob_non_erasure_monotonicity_check.csv": monotonicity_rows,
        "threshold_sensitivity_by_requirement.csv": threshold_sensitivity_rows,
        "thresholded_marginal_joint_summary.csv": marginal_joint_rows,
        "thresholded_support_probability_boundary.csv": support_boundary_rows,
        "probabilistic_non_erasure_theorem_transfer_summary.csv": theorem_summary_rows,
    }
    for name, rows in csv_outputs.items():
        write_csv(out_dir / name, rows)

    audit_digest = source_digest(audit_source / "probabilistic_channel_theorem_transfer_bundle.json")
    probe_digest = source_digest(probe_source / "formal_channel_consumption_bundle.json")
    bundle = formal_bundle(
        out_dir=out_dir,
        audit_digest=audit_digest,
        probe_digest=probe_digest,
        status=status,
    )
    write_json(out_dir / "thresholded_prob_non_erasure_bundle.json", bundle)
    report = render_report(
        audit_source=audit_source,
        probe_source=probe_source,
        status=status,
        missing_inputs=missing_inputs,
        non_erasure_rows=non_erasure_rows,
        monotonicity_rows=monotonicity_rows,
        support_boundary_rows=support_boundary_rows,
        theorem_summary_rows=theorem_summary_rows,
    )
    (out_dir / "thresholded_prob_non_erasure_report.md").write_text(report, encoding="utf-8")
    artifact_manifest_payload = artifact_manifest(out_dir, csv_outputs)
    write_json(out_dir / "artifact_manifest.json", artifact_manifest_payload)
    return {
        "overall_status": status,
        "out_dir": str(out_dir),
        "non_erasure_rows": len(non_erasure_rows),
        "monotonicity_rows": len(monotonicity_rows),
        "bundle_digest": bundle["bundle_digest"],
    }


class ThresholdContext:
    def __init__(
        self,
        *,
        probe_source: Path,
        audit_source: Path,
        channel_rows: list[dict[str, object]],
        recoverability_rows: list[dict[str, object]],
        declared_policy_rows: list[dict[str, object]],
        decoder_manifest_rows: list[dict[str, object]],
        no_self_rows: list[dict[str, object]],
        support_boundary_rows: list[dict[str, object]],
    ) -> None:
        self.probe_source = probe_source
        self.audit_source = audit_source
        self.channel_rows = channel_rows
        self.recoverability_rows = recoverability_rows
        self.declared_policy_rows = declared_policy_rows
        self.decoder_manifest_rows = decoder_manifest_rows
        self.no_self_rows = no_self_rows
        self.support_boundary_rows = support_boundary_rows
        self.source_channel_ids = sorted(
            {
                str(row["channel_id"])
                for row in channel_rows
                if str(row.get("source_carrier_id", "")) == "X2"
            }
        )
        self.recoverability_by_decoder = {
            str(row["decoder_id"]): row for row in recoverability_rows
        }
        self.fixed_policy_by_channel_dist = {
            (str(row["channel_id"]), str(row["source_distinction_id"])): row
            for row in declared_policy_rows
        }
        self.best_bayes_by_channel_dist = best_bayes_index(recoverability_rows)
        self.no_self_by_decoder = {str(row["decoder_id"]): row for row in no_self_rows}
        self.decoder_manifest_by_id = {str(row["decoder_id"]): row for row in decoder_manifest_rows}


def missing_input_files(base: Path, names: list[str]) -> list[str]:
    missing = []
    for name in names:
        path = base / name
        gz_path = base / f"{name}.gz" if name.endswith(".csv") else path
        if not path.exists() and not gz_path.exists():
            missing.append(str(path))
    return missing


def read_input_csv(base: Path, name: str) -> list[dict[str, object]]:
    path = base / name
    if path.exists():
        return read_csv(path)
    gz_path = base / f"{name}.gz"
    if gz_path.exists():
        return read_csv(gz_path)
    return []


def probabilistic_requirement_manifest() -> list[dict[str, object]]:
    return [
        {
            "requirement_set_id": req_id,
            "requirement_set_name": name,
            "source_distinction_ids": ";".join(distinctions),
            "requirement_count": len(distinctions),
            "declaration_rule": "predeclared finite source-distinction requirement set",
            "semantic_status": "finite_distinction_requirement_only",
            "notes": "formal requirement set over declared source distinctions",
        }
        for req_id, name, distinctions in REQUIREMENTS
    ]


def requirement_subset_manifest(requirements: list[dict[str, object]]) -> list[dict[str, object]]:
    sets = {
        str(row["requirement_set_id"]): set(str(row["source_distinction_ids"]).split(";"))
        for row in requirements
    }
    rows = []
    for smaller_id, smaller in sorted(sets.items()):
        for larger_id, larger in sorted(sets.items()):
            if smaller_id == larger_id:
                continue
            if not smaller.issubset(larger):
                continue
            rows.append(
                {
                    "smaller_requirement_set_id": smaller_id,
                    "larger_requirement_set_id": larger_id,
                    "smaller_distinction_ids": ";".join(sorted(smaller)),
                    "larger_distinction_ids": ";".join(sorted(larger)),
                    "is_declared_subset": 1,
                    "subset_rule": "set inclusion over declared source_distinction_ids",
                }
            )
    return rows


def probabilistic_threshold_manifest() -> list[dict[str, object]]:
    return [
        {
            "threshold_id": threshold_id,
            "threshold_value": float(threshold),
            "threshold_fraction": fraction_text(threshold),
            "threshold_semantics": "probabilistic decoder success threshold",
            "comparison_rule": "success_probability >= threshold",
            "predeclared": 1,
            "notes": "formal probe threshold; not treated as the only truth threshold",
        }
        for threshold_id, threshold in THRESHOLDS
    ]


def prob_non_erasure_decoder_eligibility(context: ThresholdContext) -> list[dict[str, object]]:
    fixed_decoder_ids = {
        str(row.get("fixed_decoder_id", ""))
        for row in context.declared_policy_rows
        if as_bool(row.get("fixed_target_available"))
    }
    rows = []
    for audit in context.no_self_rows:
        decoder_id = str(audit["decoder_id"])
        manifest = context.decoder_manifest_by_id.get(decoder_id, {})
        base_allowed = as_bool(audit.get("allowed_for_recovery_claim")) and str(audit.get("audit_status")) == "PASS"
        if not base_allowed:
            status = "blocked_non_target_evidence"
            allowed = 0
        elif decoder_id in fixed_decoder_ids:
            status = "eligible_fixed_declared"
            allowed = 1
        elif str(audit.get("decoder_policy_id")) == "bayes_best_target_distinction":
            status = "eligible_bayes_best_measurement"
            allowed = 0
        else:
            status = "blocked_policy_mismatch"
            allowed = 0
        rows.append(
            {
                "decoder_id": decoder_id,
                "decoder_policy_id": audit.get("decoder_policy_id", ""),
                "distinction_id": audit.get("distinction_id", manifest.get("source_distinction_id", "")),
                "target_distinction_id": manifest.get("target_distinction_id", ""),
                "uses_source_state_id": audit.get("uses_source_state_id", ""),
                "uses_source_distinction_label_as_input": audit.get("uses_source_distinction_label_as_input", ""),
                "uses_hidden_oracle_state": audit.get("uses_hidden_latent_or_oracle_state", ""),
                "uses_candidate_id": audit.get("uses_candidate_id", ""),
                "uses_target_observation_only": audit.get("uses_target_observation_only", ""),
                "allowed_for_prob_non_erasure": allowed,
                "eligibility_status": status,
                "notes": eligibility_note(status),
            }
        )
    return rows


def thresholded_prob_recovery_by_distinction(
    context: ThresholdContext,
    eligibility_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    eligibility = {str(row["decoder_id"]): row for row in eligibility_rows}
    rows = []
    for channel_id in context.source_channel_ids:
        for distinction_id in ["D_A", "D_B", "D_joint", "D_parity"]:
            fixed = fixed_policy_candidate(context, channel_id, distinction_id)
            bayes = bayes_policy_candidate(context, channel_id, distinction_id)
            for policy_id, candidate in [(FIXED_POLICY, fixed), (BAYES_POLICY, bayes)]:
                for threshold_id, threshold in THRESHOLDS:
                    rows.append(
                        recovery_row_for_candidate(
                            policy_id=policy_id,
                            channel_id=channel_id,
                            distinction_id=distinction_id,
                            threshold_id=threshold_id,
                            threshold=threshold,
                            candidate=candidate,
                            eligibility=eligibility,
                        )
                    )
    return rows


def fixed_policy_candidate(context: ThresholdContext, channel_id: str, distinction_id: str) -> dict[str, object]:
    fixed = context.fixed_policy_by_channel_dist.get((channel_id, distinction_id))
    if not fixed:
        return {"candidate_status": "blocked_missing_fixed_target"}
    if not as_bool(fixed.get("fixed_target_available")):
        return {
            "candidate_status": "blocked_missing_fixed_target",
            "target_distinction_id": fixed.get("fixed_target_distinction_id", ""),
            "decoder_id": fixed.get("fixed_decoder_id", ""),
        }
    decoder_id = str(fixed.get("fixed_decoder_id", ""))
    recoverability = context.recoverability_by_decoder.get(decoder_id)
    if not recoverability:
        return {
            "candidate_status": "blocked_missing_recoverability",
            "target_distinction_id": fixed.get("fixed_target_distinction_id", ""),
            "decoder_id": decoder_id,
        }
    return {"candidate_status": "ok", **recoverability}


def bayes_policy_candidate(context: ThresholdContext, channel_id: str, distinction_id: str) -> dict[str, object]:
    row = context.best_bayes_by_channel_dist.get((channel_id, distinction_id))
    if not row:
        return {"candidate_status": "blocked_missing_recoverability"}
    return {"candidate_status": "ok", **row}


def recovery_row_for_candidate(
    *,
    policy_id: str,
    channel_id: str,
    distinction_id: str,
    threshold_id: str,
    threshold: Fraction,
    candidate: dict[str, object],
    eligibility: dict[str, dict[str, object]],
) -> dict[str, object]:
    decoder_id = str(candidate.get("decoder_id", ""))
    target_distinction_id = str(candidate.get("target_distinction_id", ""))
    eligibility_row = eligibility.get(decoder_id, {})
    success = fraction_from_optional(candidate.get("decoder_success_fraction"), candidate.get("decoder_success_probability"))
    recovered = success >= threshold
    exact_support = as_bool(candidate.get("exact_recoverable_support"))
    candidate_status = str(candidate.get("candidate_status", "ok"))
    allowed = as_bool(eligibility_row.get("allowed_for_prob_non_erasure"))
    if candidate_status != "ok":
        status = candidate_status
    elif not eligibility_row:
        status = "blocked_missing_audit"
    elif str(eligibility_row.get("eligibility_status", "")).startswith("blocked"):
        status = str(eligibility_row["eligibility_status"])
    elif policy_id == BAYES_POLICY:
        status = "recovered_bayes_best_diagnostic" if recovered else "not_recovered_below_threshold"
    elif recovered and allowed:
        status = "recovered_fixed_declared"
    elif recovered and not allowed:
        status = "blocked_policy_mismatch"
    else:
        status = "not_recovered_below_threshold"
    return {
        "channel_id": channel_id,
        "distinction_id": distinction_id,
        "target_distinction_id": target_distinction_id,
        "decoder_id": decoder_id,
        "decoder_policy_id": policy_id,
        "threshold_id": threshold_id,
        "threshold_value": float(threshold),
        "threshold_fraction": fraction_text(threshold),
        "success_probability": float(success) if candidate_status == "ok" else "",
        "success_fraction": fraction_text(success) if candidate_status == "ok" else "",
        "chance_success_probability": candidate.get("chance_success_probability", ""),
        "excess_success_over_chance": candidate.get("excess_success_over_chance", ""),
        "normalized_recovery_advantage": candidate.get("normalized_recovery_advantage", ""),
        "support_exact_recovered": int(exact_support),
        "probabilistic_recovered": int(recovered and candidate_status == "ok"),
        "allowed_for_prob_non_erasure": int(allowed),
        "recovery_status": status,
        "notes": recovery_note(policy_id, status),
    }


def thresholded_prob_non_erasure_by_channel(
    *,
    context: ThresholdContext,
    requirement_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    recovery_index = {
        (
            str(row["channel_id"]),
            str(row["distinction_id"]),
            str(row["threshold_id"]),
            str(row["decoder_policy_id"]),
        ): row
        for row in recovery_rows
    }
    rows = []
    for channel_id in context.source_channel_ids:
        for req in requirement_rows:
            distinctions = split_ids(req["source_distinction_ids"])
            for threshold_id, threshold in THRESHOLDS:
                for policy_id in [FIXED_POLICY, BAYES_POLICY]:
                    selected = [
                        recovery_index.get((channel_id, distinction_id, threshold_id, policy_id))
                        for distinction_id in distinctions
                    ]
                    rows.append(
                        non_erasure_row(
                            channel_id=channel_id,
                            requirement=req,
                            threshold_id=threshold_id,
                            threshold=threshold,
                            policy_id=policy_id,
                            selected=selected,
                        )
                    )
    return rows


def non_erasure_row(
    *,
    channel_id: str,
    requirement: dict[str, object],
    threshold_id: str,
    threshold: Fraction,
    policy_id: str,
    selected: list[dict[str, object] | None],
) -> dict[str, object]:
    required_count = len(selected)
    present = [row for row in selected if row is not None]
    recovered_rows = [row for row in present if as_bool(row.get("probabilistic_recovered"))]
    blocked_rows = [row for row in present if str(row.get("recovery_status", "")).startswith("blocked")]
    missing_count = required_count - len(present)
    all_recovered = len(recovered_rows) == required_count and missing_count == 0
    formal_allowed = policy_id == FIXED_POLICY and all(
        as_bool(row.get("allowed_for_prob_non_erasure")) for row in present
    )
    prob_non_erasing = all_recovered and formal_allowed and not blocked_rows
    status = non_erasure_status(
        policy_id=policy_id,
        all_recovered=all_recovered,
        prob_non_erasing=prob_non_erasing,
        blocked_rows=blocked_rows,
        missing_count=missing_count,
    )
    successes = [fraction_from_optional(row.get("success_fraction"), row.get("success_probability")) for row in present if row.get("success_probability") not in ("", None)]
    advantages = [
        float(row.get("normalized_recovery_advantage"))
        for row in present
        if row.get("normalized_recovery_advantage") not in ("", None)
    ]
    return {
        "channel_id": channel_id,
        "requirement_set_id": requirement["requirement_set_id"],
        "requirement_set_name": requirement["requirement_set_name"],
        "threshold_id": threshold_id,
        "threshold_value": float(threshold),
        "threshold_fraction": fraction_text(threshold),
        "decoder_policy_id": policy_id,
        "required_count": required_count,
        "recovered_count": len(recovered_rows),
        "not_recovered_count": required_count - len(recovered_rows) - len(blocked_rows) - missing_count,
        "blocked_count": len(blocked_rows) + missing_count,
        "all_required_recovered": int(all_recovered),
        "prob_non_erasing": int(prob_non_erasing),
        "non_erasure_status": status,
        "selected_decoder_ids": ";".join(str(row.get("decoder_id", "")) for row in present),
        "selected_target_distinction_ids": ";".join(str(row.get("target_distinction_id", "")) for row in present),
        "min_success_probability": float(min(successes)) if successes else "",
        "mean_success_probability": float(sum(successes, Fraction(0)) / len(successes)) if successes else "",
        "min_normalized_recovery_advantage": min(advantages) if advantages else "",
        "notes": non_erasure_note(policy_id, status),
    }


def prob_non_erasure_monotonicity_check(
    *,
    subset_rows: list[dict[str, object]],
    non_erasure_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    fixed_rows = {
        (
            str(row["channel_id"]),
            str(row["threshold_id"]),
            str(row["decoder_policy_id"]),
            str(row["requirement_set_id"]),
        ): row
        for row in non_erasure_rows
        if str(row["decoder_policy_id"]) == FIXED_POLICY
    }
    rows = []
    channels = sorted({key[0] for key in fixed_rows})
    thresholds = [threshold_id for threshold_id, _threshold in THRESHOLDS]
    for channel_id in channels:
        for threshold_id in thresholds:
            for subset in subset_rows:
                larger_id = str(subset["larger_requirement_set_id"])
                smaller_id = str(subset["smaller_requirement_set_id"])
                larger = fixed_rows.get((channel_id, threshold_id, FIXED_POLICY, larger_id))
                smaller = fixed_rows.get((channel_id, threshold_id, FIXED_POLICY, smaller_id))
                larger_ok = bool(larger and as_bool(larger.get("prob_non_erasing")))
                smaller_ok = bool(smaller and as_bool(smaller.get("prob_non_erasing")))
                expected = larger_ok
                observed = (not larger_ok) or smaller_ok
                if not larger:
                    status = "blocked_missing_larger"
                elif not smaller:
                    status = "blocked_missing_smaller"
                else:
                    status = "pass" if observed else "fail"
                rows.append(
                    {
                        "channel_id": channel_id,
                        "threshold_id": threshold_id,
                        "decoder_policy_id": FIXED_POLICY,
                        "larger_requirement_set_id": larger_id,
                        "smaller_requirement_set_id": smaller_id,
                        "is_declared_subset": subset["is_declared_subset"],
                        "larger_prob_non_erasing": int(larger_ok),
                        "smaller_prob_non_erasing": int(smaller_ok),
                        "monotonicity_expected": int(expected),
                        "monotonicity_observed": int(observed),
                        "status": status,
                        "notes": "monotonicity checked over fixed-declared target policy rows",
                    }
                )
    return rows


def threshold_sensitivity_by_requirement(non_erasure_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], dict[str, dict[str, object]]] = defaultdict(dict)
    for row in non_erasure_rows:
        key = (str(row["channel_id"]), str(row["requirement_set_id"]), str(row["decoder_policy_id"]))
        grouped[key][str(row["threshold_id"])] = row
    rows = []
    threshold_ids = [threshold_id for threshold_id, _threshold in THRESHOLDS]
    for (channel_id, requirement_set_id, policy_id), by_threshold in sorted(grouped.items()):
        passes = [
            threshold_id
            for threshold_id in threshold_ids
            if threshold_diagnostic_pass(by_threshold.get(threshold_id, {}), policy_id)
        ]
        fails = [threshold_id for threshold_id in threshold_ids if threshold_id not in passes]
        rows.append(
            {
                "channel_id": channel_id,
                "requirement_set_id": requirement_set_id,
                "decoder_policy_id": policy_id,
                "threshold_0_80_status": status_for_threshold(by_threshold, "threshold_0_80"),
                "threshold_0_90_status": status_for_threshold(by_threshold, "threshold_0_90"),
                "threshold_0_95_status": status_for_threshold(by_threshold, "threshold_0_95"),
                "threshold_0_99_status": status_for_threshold(by_threshold, "threshold_0_99"),
                "threshold_1_00_status": status_for_threshold(by_threshold, "threshold_1_00"),
                "highest_threshold_passed": passes[-1] if passes else "",
                "lowest_threshold_failed": fails[0] if fails else "",
                "threshold_fragility_class": threshold_fragility_class(passes, by_threshold),
                "notes": "diagnostic pass uses all_required_recovered for Bayes-best and prob_non_erasing for fixed policy",
            }
        )
    return rows


def thresholded_marginal_joint_summary(
    *,
    recovery_rows: list[dict[str, object]],
    non_erasure_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    non_erasure_index = {
        (
            str(row["channel_id"]),
            str(row["threshold_id"]),
            str(row["decoder_policy_id"]),
            str(row["requirement_set_id"]),
        ): row
        for row in non_erasure_rows
    }
    recovery_index = {
        (
            str(row["channel_id"]),
            str(row["threshold_id"]),
            str(row["decoder_policy_id"]),
            str(row["distinction_id"]),
        ): row
        for row in recovery_rows
    }
    rows = []
    channels = sorted({row["channel_id"] for row in non_erasure_rows})
    for channel_id in channels:
        for threshold_id, _threshold in THRESHOLDS:
            for policy_id in [FIXED_POLICY, BAYES_POLICY]:
                req_marginals = non_erasure_index.get((str(channel_id), threshold_id, policy_id, "req_marginals"), {})
                req_joint = non_erasure_index.get((str(channel_id), threshold_id, policy_id, "req_joint"), {})
                req_parity = non_erasure_index.get((str(channel_id), threshold_id, policy_id, "req_parity"), {})
                req_all = non_erasure_index.get((str(channel_id), threshold_id, policy_id, "req_all_nontrivial"), {})
                a = recovery_index.get((str(channel_id), threshold_id, policy_id, "D_A"), {})
                b = recovery_index.get((str(channel_id), threshold_id, policy_id, "D_B"), {})
                joint = recovery_index.get((str(channel_id), threshold_id, policy_id, "D_joint"), {})
                parity = recovery_index.get((str(channel_id), threshold_id, policy_id, "D_parity"), {})
                rows.append(
                    {
                        "channel_id": channel_id,
                        "threshold_id": threshold_id,
                        "decoder_policy_id": policy_id,
                        "req_marginals_status": req_marginals.get("non_erasure_status", ""),
                        "req_joint_status": req_joint.get("non_erasure_status", ""),
                        "req_parity_status": req_parity.get("non_erasure_status", ""),
                        "req_all_nontrivial_status": req_all.get("non_erasure_status", ""),
                        "D_A_success": a.get("success_probability", ""),
                        "D_B_success": b.get("success_probability", ""),
                        "D_joint_success": joint.get("success_probability", ""),
                        "D_parity_success": parity.get("success_probability", ""),
                        "diagnostic_class": marginal_joint_class(req_marginals, req_joint, req_parity, req_all, policy_id),
                        "notes": "finite stochastic thresholded recovery diagnostic only",
                    }
                )
    return rows


def thresholded_support_probability_boundary(
    *,
    requirement_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
    non_erasure_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    recovery_index = {
        (
            str(row["channel_id"]),
            str(row["threshold_id"]),
            str(row["decoder_policy_id"]),
            str(row["distinction_id"]),
        ): row
        for row in recovery_rows
    }
    requirement_index = {str(row["requirement_set_id"]): split_ids(row["source_distinction_ids"]) for row in requirement_rows}
    rows = []
    for row in non_erasure_rows:
        distinctions = requirement_index[str(row["requirement_set_id"])]
        selected = [
            recovery_index.get((str(row["channel_id"]), str(row["threshold_id"]), str(row["decoder_policy_id"]), distinction_id))
            for distinction_id in distinctions
        ]
        present = [selected_row for selected_row in selected if selected_row]
        support_count = sum(1 for selected_row in present if as_bool(selected_row.get("support_exact_recovered")))
        prob_count = sum(1 for selected_row in present if as_bool(selected_row.get("probabilistic_recovered")))
        requirement_count = len(distinctions)
        all_support = support_count == requirement_count and len(present) == requirement_count
        all_prob = prob_count == requirement_count and len(present) == requirement_count
        relation = support_probability_relation(all_support, all_prob, support_count, prob_count, requirement_count, len(present))
        rows.append(
            {
                "channel_id": row["channel_id"],
                "requirement_set_id": row["requirement_set_id"],
                "threshold_id": row["threshold_id"],
                "decoder_policy_id": row["decoder_policy_id"],
                "all_required_support_exact": int(all_support),
                "all_required_prob_recovered": int(all_prob),
                "support_probability_relation": relation,
                "support_exact_count": support_count,
                "prob_recovered_count": prob_count,
                "requirement_count": requirement_count,
                "notes": "exact support and probabilistic threshold recovery are reported separately",
            }
        )
    return rows


def probabilistic_non_erasure_theorem_transfer_summary(
    *,
    input_status: str,
    non_erasure_rows: list[dict[str, object]],
    monotonicity_rows: list[dict[str, object]],
    support_boundary_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    monotonicity_pass = bool(monotonicity_rows) and all(str(row["status"]) == "pass" for row in monotonicity_rows)
    prob_without_support = any(
        str(row["support_probability_relation"]) == "prob_recovered_without_support_exact"
        for row in support_boundary_rows
    )
    non_erasure_present = bool(non_erasure_rows)
    return [
        theorem_row(
            "thresholded_prob_non_erasure_definition",
            "measurement_ready_pending_lean_definition",
            "thresholded_prob_non_erasure_by_channel.csv",
            non_erasure_present,
            "ready_for_measurement_only" if input_status == "ready" and non_erasure_present else "blocked_missing_artifacts",
            "finite thresholded requirement-set recovery measurements",
            "root theorem transfer until Lean definition is added",
            "defines the empirical target for ProbNonErasing",
        ),
        theorem_row(
            "prob_non_erasure_monotonicity",
            "measurement_ready_pending_lean_theorem",
            "requirement_subset_manifest.csv;prob_non_erasure_monotonicity_check.csv",
            monotonicity_pass,
            "ready_for_measurement_only" if monotonicity_pass else "blocked_requirement_inconsistency",
            "empirical monotonicity audit over declared subset pairs",
            "formal monotonicity theorem transfer until Lean theorem is added",
            "all fixed-policy declared subset checks pass" if monotonicity_pass else "monotonicity issue found",
        ),
        theorem_row(
            "support_exact_implies_prob_recovery",
            "lean_checked_and_empirically_auditable",
            "thresholded_support_probability_boundary.csv",
            True,
            "ready_for_formal_consumption",
            "support-exact rows are separated from thresholded probabilistic rows",
            "converse claims without assumptions",
            "reuses probabilistic channel Lean result",
        ),
        theorem_row(
            "prob_recovery_without_support_exact_boundary",
            "lean_checked_and_empirically_auditable",
            "thresholded_support_probability_boundary.csv",
            prob_without_support,
            "ready_for_formal_consumption" if prob_without_support else "ready_for_measurement_only",
            "probability-only recovery boundary cases",
            "support-level recovery claims from probability alone",
            "noisy examples expose probability without support exactness",
        ),
        theorem_row(
            "cascade_error_bound_relevance",
            "lean_checked_and_empirically_auditable",
            "cascade_bound_check.csv;thresholded_prob_non_erasure_by_channel.csv",
            True,
            "ready_for_formal_consumption",
            "cascade theorem remains available for future composition of thresholded objects",
            "thresholded composition theorem by itself",
            "composition-bound audit is upstream of this package",
        ),
        theorem_row(
            "thresholded_non_erasure_composition",
            "pending_formal_theorem",
            "thresholded_prob_non_erasure_by_channel.csv;cascade_bound_check.csv",
            True,
            "ready_for_measurement_only",
            "empirical inputs for a future theorem",
            "composition transfer for thresholded non-erasure",
            "requires formal theorem connecting thresholds with cascade bounds",
        ),
        theorem_row(
            "candidate_family_completion",
            "not_applicable",
            "candidate_family_manifest.csv;admissibility_predicate_manifest.csv",
            False,
            "not_applicable",
            "none",
            "completion/candidate-family claims",
            "no candidate-family object is declared here",
        ),
    ]


def theorem_row(
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


def overall_status(
    *,
    input_status: str,
    eligibility_rows: list[dict[str, object]],
    monotonicity_rows: list[dict[str, object]],
) -> str:
    if input_status != "ready":
        return "blocked_missing_inputs"
    if any(str(row["eligibility_status"]) == "forbidden_oracle" for row in eligibility_rows):
        return "blocked_decoder_audit"
    if any(str(row["status"]) == "fail" for row in monotonicity_rows):
        return "blocked_requirement_inconsistency"
    return "thresholded_prob_non_erasure_measurement_ready"


def formal_bundle(
    *,
    out_dir: Path,
    audit_digest: str,
    probe_digest: str,
    status: str,
) -> dict[str, object]:
    payload = {
        "source_theorem_transfer_audit_digest": audit_digest,
        "source_fixed_policy_probe_digest": probe_digest,
        "overall_status": status,
    }
    return {
        "bundle_schema_version": "0.1.0",
        "source_theorem_transfer_audit_digest": audit_digest,
        "source_fixed_policy_probe_digest": probe_digest,
        "probabilistic_requirement_manifest": "probabilistic_requirement_manifest.csv",
        "probabilistic_threshold_manifest": "probabilistic_threshold_manifest.csv",
        "prob_non_erasure_decoder_eligibility": "prob_non_erasure_decoder_eligibility.csv",
        "thresholded_prob_recovery_by_distinction": "thresholded_prob_recovery_by_distinction.csv",
        "thresholded_prob_non_erasure_by_channel": "thresholded_prob_non_erasure_by_channel.csv",
        "prob_non_erasure_monotonicity_check": "prob_non_erasure_monotonicity_check.csv",
        "threshold_sensitivity_by_requirement": "threshold_sensitivity_by_requirement.csv",
        "thresholded_marginal_joint_summary": "thresholded_marginal_joint_summary.csv",
        "thresholded_support_probability_boundary": "thresholded_support_probability_boundary.csv",
        "probabilistic_non_erasure_theorem_transfer_summary": "probabilistic_non_erasure_theorem_transfer_summary.csv",
        "overall_status": status,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_directory": str(out_dir),
        "bundle_digest": stable_hash(payload, length=24),
    }


def render_report(
    *,
    audit_source: Path,
    probe_source: Path,
    status: str,
    missing_inputs: list[str],
    non_erasure_rows: list[dict[str, object]],
    monotonicity_rows: list[dict[str, object]],
    support_boundary_rows: list[dict[str, object]],
    theorem_summary_rows: list[dict[str, object]],
) -> str:
    fixed_passes = sum(1 for row in non_erasure_rows if as_bool(row["prob_non_erasing"]))
    bayes_measurements = sum(
        1 for row in non_erasure_rows if str(row["non_erasure_status"]) == "measurement_only_bayes_best"
    )
    support_counts = count_by(support_boundary_rows, "support_probability_relation")
    monotonicity_failures = sum(1 for row in monotonicity_rows if str(row["status"]) == "fail")
    return "\n".join(
        [
            "# Thresholded Probabilistic Non-Erasure v0",
            "",
            "## Executive Summary",
            "",
            "This pass compiles thresholded probabilistic recovery into finite "
            "requirement-set non-erasure measurements. It keeps fixed-declared target "
            "policy separate from Bayes-best diagnostics, preserves the exact-support "
            "versus probabilistic-recovery boundary, and checks requirement-set "
            "monotonicity for the declared fixed-policy rows.",
            "",
            f"- overall status: `{status}`",
            f"- fixed-policy non-erasing rows: {fixed_passes}",
            f"- Bayes-best diagnostic rows: {bayes_measurements}",
            f"- monotonicity failures: {monotonicity_failures}",
            "",
            "## Scope",
            "",
            CLAIM_BOUNDARY,
            "",
            "## Inputs",
            "",
            f"- theorem-transfer audit: `{audit_source}`",
            f"- fixed-policy probe: `{probe_source}`",
            f"- missing inputs: `{';'.join(missing_inputs) if missing_inputs else 'none'}`",
            "",
            "## Requirement Sets And Thresholds",
            "",
            "Requirement sets range from single distinctions (`req_A`, `req_B`) through "
            "`req_marginals`, `req_joint`, `req_parity`, and `req_all_nontrivial`. "
            "Thresholds are 0.80, 0.90, 0.95, 0.99, and 1.00.",
            "",
            "## Decoder Eligibility",
            "",
            "Fixed-declared target policy is the default theorem-transfer target. Bayes-best "
            "rows are emitted as diagnostics and are not silently substituted into fixed "
            "policy non-erasure claims.",
            "",
            "## Non-Erasure Measurements",
            "",
            f"- total non-erasure rows: {len(non_erasure_rows)}",
            f"- fixed-policy rows with `prob_non_erasing=1`: {fixed_passes}",
            f"- Bayes-best measurement-only rows: {bayes_measurements}",
            "",
            "## Monotonicity",
            "",
            f"- monotonicity rows: {len(monotonicity_rows)}",
            f"- failures: {monotonicity_failures}",
            "",
            "## Support/Probability Boundary",
            "",
            *[f"- `{name}`: {count}" for name, count in sorted(support_counts.items())],
            "",
            "## Theorem-Transfer Status",
            "",
            *[
                f"- `{row['theorem_or_layer_id']}`: {row['applicability_status']}"
                for row in theorem_summary_rows
            ],
            "",
            "## Next Formal Ask",
            "",
            "The formal arm can now define `ProbNonErasing(K, pi, Req, threshold, policy)` "
            "and prove monotonicity under requirement-set weakening. Composition of "
            "thresholded non-erasure remains a separate theorem target because it must connect "
            "thresholds to the existing cascade error-bound layer.",
        ]
    )


def artifact_manifest(out_dir: Path, csv_outputs: dict[str, list[dict[str, object]]]) -> dict[str, object]:
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
    for name in ["thresholded_prob_non_erasure_bundle.json", "thresholded_prob_non_erasure_report.md"]:
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
        "claim_boundary": CLAIM_BOUNDARY,
    }


def best_bayes_index(rows: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    best: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        if str(row.get("decoder_kind")) != "bayes_optimal_decoder":
            continue
        source_dist = str(row.get("source_distinction_id"))
        if not source_dist.startswith("D_"):
            continue
        key = (str(row["channel_id"]), source_dist)
        success = fraction_from_optional(row.get("decoder_success_fraction"), row.get("decoder_success_probability"))
        current = best.get(key)
        if current is None:
            best[key] = row
            continue
        current_success = fraction_from_optional(
            current.get("decoder_success_fraction"),
            current.get("decoder_success_probability"),
        )
        if (success, str(row.get("target_distinction_id"))) > (
            current_success,
            str(current.get("target_distinction_id")),
        ):
            best[key] = row
    return best


def split_ids(value: object) -> list[str]:
    return [part for part in str(value).split(";") if part]


def non_erasure_status(
    *,
    policy_id: str,
    all_recovered: bool,
    prob_non_erasing: bool,
    blocked_rows: list[dict[str, object]],
    missing_count: int,
) -> str:
    if missing_count:
        return "blocked_missing_recoverability"
    if blocked_rows:
        statuses = {str(row.get("recovery_status")) for row in blocked_rows}
        if "blocked_missing_fixed_target" in statuses:
            return "blocked_missing_fixed_target"
        if "blocked_non_target_evidence" in statuses:
            return "blocked_forbidden_decoder"
        if "blocked_policy_mismatch" in statuses:
            return "blocked_policy_mismatch"
        return sorted(statuses)[0]
    if policy_id == BAYES_POLICY:
        return "measurement_only_bayes_best"
    if prob_non_erasing:
        return "prob_non_erasing"
    if not all_recovered:
        return "not_non_erasing_below_threshold"
    return "blocked_policy_mismatch"


def threshold_diagnostic_pass(row: dict[str, object], policy_id: str) -> bool:
    if not row:
        return False
    if policy_id == FIXED_POLICY:
        return as_bool(row.get("prob_non_erasing"))
    return as_bool(row.get("all_required_recovered"))


def status_for_threshold(by_threshold: dict[str, dict[str, object]], threshold_id: str) -> str:
    return str(by_threshold.get(threshold_id, {}).get("non_erasure_status", "blocked"))


def threshold_fragility_class(passes: list[str], by_threshold: dict[str, dict[str, object]]) -> str:
    if any(str(row.get("non_erasure_status", "")).startswith("blocked") for row in by_threshold.values()):
        return "blocked"
    if len(passes) == 5:
        return "stable_all_thresholds"
    if passes and passes[-1] in ("threshold_0_99", "threshold_1_00"):
        return "stable_high_threshold"
    if passes and passes[-1] in ("threshold_0_90", "threshold_0_95"):
        return "moderate_only"
    if passes and passes[-1] == "threshold_0_80":
        return "low_only"
    if passes:
        return "threshold_fragile"
    return "never_recovered"


def marginal_joint_class(
    req_marginals: dict[str, object],
    req_joint: dict[str, object],
    req_parity: dict[str, object],
    req_all: dict[str, object],
    policy_id: str,
) -> str:
    if not req_marginals or not req_joint or not req_parity or not req_all:
        return "blocked"
    marginal = threshold_diagnostic_pass(req_marginals, policy_id)
    joint = threshold_diagnostic_pass(req_joint, policy_id)
    parity = threshold_diagnostic_pass(req_parity, policy_id)
    all_nontrivial = threshold_diagnostic_pass(req_all, policy_id)
    if marginal and joint:
        return "marginal_and_joint_recovered"
    if marginal and not joint:
        return "marginal_recovered_joint_not_recovered"
    if joint and not marginal:
        return "joint_recovered_marginal_failed"
    if not marginal and not joint and not parity and not all_nontrivial:
        return "all_nontrivial_lost"
    return "mixed_or_partial"


def support_probability_relation(
    all_support: bool,
    all_prob: bool,
    support_count: int,
    prob_count: int,
    requirement_count: int,
    present_count: int,
) -> str:
    if present_count < requirement_count:
        return "blocked"
    if all_support and all_prob:
        return "support_exact_and_prob_recovered"
    if all_prob and not all_support:
        return "prob_recovered_without_support_exact"
    if all_support and not all_prob:
        return "support_exact_missing_prob_below_threshold"
    if support_count == 0 and prob_count == 0:
        return "neither"
    return "mixed"


def eligibility_note(status: str) -> str:
    if status == "eligible_fixed_declared":
        return "eligible for default fixed-declared target-policy non-erasure measurement"
    if status == "eligible_bayes_best_measurement":
        return "diagnostic Bayes-best measurement; not default theorem-transfer policy"
    return "not eligible for default thresholded non-erasure measurement"


def recovery_note(policy_id: str, status: str) -> str:
    if policy_id == BAYES_POLICY:
        return "Bayes-best target policy diagnostic; fixed policy remains default formal target"
    if status == "recovered_fixed_declared":
        return "fixed-declared target policy recovers this distinction at threshold"
    return "fixed-declared target policy does not recover this distinction at threshold"


def non_erasure_note(policy_id: str, status: str) -> str:
    if policy_id == BAYES_POLICY:
        return "Bayes-best requirement-set result is diagnostic unless formalized as its own policy object"
    return f"fixed-declared target-policy status: {status}"


def source_digest(path: Path) -> str:
    if not path.exists():
        return ""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str(payload.get("bundle_digest") or payload.get("probe_digest") or stable_hash(payload, length=24))


def count_by(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get(field, ""))
        counts[key] = counts.get(key, 0) + 1
    return counts


if __name__ == "__main__":
    main()
