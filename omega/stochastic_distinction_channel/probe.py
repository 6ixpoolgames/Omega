"""Run the finite stochastic distinction-channel probe v0."""

from __future__ import annotations

import argparse
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json

from .analysis import (
    asymmetry_summary_by_channel,
    baseline_tables,
    build_composed_channels,
    build_recoverability,
    channel_baseline_summary_for_report,
    composition_recoverability_checks,
    decoder_policy_manifest,
    decoder_totality_audit,
    distinction_partition_audit,
    support_vs_probability_summary,
    theorem_transfer_readiness_summary,
    marginal_joint_diagnostic,
    matrix_rows,
    non_erasure_tables,
    row_stochastic_audit,
    support_rows,
    threshold_application_audit,
)
from .construct import (
    carrier_manifest_rows,
    carriers,
    channel_definitions,
    distinction_specs,
    observation_rows,
    source_priors,
    thresholds,
)
from .schema import CLAIM_BOUNDARY, DEFAULT_OUT, canonical_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run stochastic distinction-channel probe v0.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--csv-output-mode", choices=("plain", "gzip"), default="plain")
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_probe(
        out_dir=args.out,
        csv_output_mode=args.csv_output_mode,
        gzip_compresslevel=args.gzip_compresslevel,
    )
    import json

    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_probe(
    *,
    out_dir: Path,
    csv_output_mode: str = "plain",
    gzip_compresslevel: int = 1,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    carrier_map = carriers()
    distinctions = distinction_specs()
    base_channel_rows, matrices = channel_definitions()
    composition_manifest, composed_channel_rows, composed_matrix_rows, composed_matrices = build_composed_channels(matrices)
    all_channel_rows = base_channel_rows + composed_channel_rows
    matrices = {**matrices, **composed_matrices}
    prior_rows = source_priors(carrier_map)
    threshold_rows = thresholds()
    carrier_rows = carrier_manifest_rows(carrier_map)
    source_obs = observation_rows(carrier_map, distinctions, table_kind="source")
    target_obs = observation_rows(carrier_map, distinctions, table_kind="target")
    chan_matrix_rows = matrix_rows(all_channel_rows, matrices)
    chan_support_rows = support_rows(chan_matrix_rows)
    support_relation_rows = [
        {
            **row,
            "relation_kind": "support_projection",
            "support_projection_rule": "K(y|x) > 0",
        }
        for row in chan_support_rows
    ]
    recoverability_bundle = build_recoverability(
        channel_rows=all_channel_rows,
        matrices=matrices,
        carrier_map=carrier_map,
        distinctions=distinctions,
        prior_rows=prior_rows,
    )
    non_erasure_manifest, non_erasure_rows = non_erasure_tables(recoverability_bundle["recoverability"])
    marginal_joint_rows = marginal_joint_diagnostic(recoverability_bundle["recoverability"])
    decoder_policy_rows = decoder_policy_manifest()
    support_probability_rows = support_vs_probability_summary(
        recoverability_bundle["recoverability"],
        recoverability_bundle["support_recoverability"],
    )
    baseline_manifest, baseline_comparison = baseline_tables(recoverability_bundle["recoverability"])
    asymmetry_summary = asymmetry_summary_by_channel(
        channel_rows=all_channel_rows,
        matrices=matrices,
        recoverability=recoverability_bundle["recoverability"],
    )
    composition_check_rows = composition_recoverability_checks(recoverability_bundle["recoverability"])
    audit_rows = {
        "channel_row_stochastic_audit.csv": row_stochastic_audit(all_channel_rows, matrices),
        "distinction_partition_audit.csv": distinction_partition_audit(carrier_map, distinctions),
        "decoder_totality_audit.csv": decoder_totality_audit(
            recoverability_bundle["decoder_manifest"],
            recoverability_bundle["decoder_table"],
            distinctions,
        ),
        "threshold_application_audit.csv": threshold_application_audit(recoverability_bundle["recoverability"]),
    }
    theorem_readiness_rows = theorem_transfer_readiness_summary(
        audits=audit_rows,
        support_probability=support_probability_rows,
        composition_checks=composition_check_rows,
    )

    csv_outputs: dict[str, list[dict[str, object]]] = {
        "carrier_manifest.csv": carrier_rows,
        "channel_manifest.csv": all_channel_rows,
        "channel_matrix.csv": chan_matrix_rows,
        "channel_support.csv": chan_support_rows,
        "source_prior_manifest.csv": prior_rows,
        "distinction_manifest.csv": distinctions,
        "source_observation_table.csv": source_obs,
        "target_observation_table.csv": target_obs,
        "decoder_manifest.csv": recoverability_bundle["decoder_manifest"],
        "decoder_policy_manifest.csv": decoder_policy_rows,
        "decoder_table.csv": recoverability_bundle["decoder_table"],
        "threshold_manifest.csv": threshold_rows,
        "recoverability_by_distinction.csv": recoverability_bundle["recoverability"],
        "asymmetry_summary_by_channel.csv": asymmetry_summary,
        "confusion_matrix_by_distinction.csv": recoverability_bundle["confusion"],
        "non_erasure_requirement_manifest.csv": non_erasure_manifest,
        "non_erasure_by_channel.csv": non_erasure_rows,
        "marginal_joint_recoverability_diagnostic.csv": marginal_joint_rows,
        "support_vs_probability_summary.csv": support_probability_rows,
        "channel_baseline_manifest.csv": baseline_manifest,
        "channel_baseline_comparison.csv": baseline_comparison,
        "channel_composition_manifest.csv": composition_manifest,
        "composed_channel_matrix.csv": composed_matrix_rows,
        "composition_recoverability_check.csv": composition_check_rows,
        "support_relation.csv": support_relation_rows,
        "support_recoverability.csv": recoverability_bundle["support_recoverability"],
        "theorem_transfer_readiness_summary.csv": theorem_readiness_rows,
        **audit_rows,
    }
    artifact_paths = {name: csv_name(name, csv_output_mode) for name in csv_outputs}
    for name, rows in csv_outputs.items():
        write_csv(out_dir / artifact_paths[name], rows, gzip_compresslevel=gzip_compresslevel)

    probe_manifest = build_probe_manifest(
        all_channel_rows=all_channel_rows,
        distinctions=distinctions,
        artifact_paths=artifact_paths,
        csv_output_mode=csv_output_mode,
    )
    write_json(out_dir / "channel_probe_manifest.json", probe_manifest)
    report = render_report(
        probe_manifest=probe_manifest,
        audits=audit_rows,
        recoverability=recoverability_bundle["recoverability"],
        non_erasure=non_erasure_rows,
        marginal_joint=marginal_joint_rows,
        decoder_policy=decoder_policy_rows,
        support_probability=support_probability_rows,
        baseline_comparison=baseline_comparison,
        composition_checks=composition_check_rows,
        theorem_readiness=theorem_readiness_rows,
    )
    (out_dir / "stochastic_channel_probe_report.md").write_text(report, encoding="utf-8")
    artifact_manifest = build_artifact_manifest(
        out_dir=out_dir,
        artifact_paths=artifact_paths,
        csv_outputs=csv_outputs,
        extra_files=["channel_probe_manifest.json", "stochastic_channel_probe_report.md"],
    )
    write_json(out_dir / "artifact_manifest.json", artifact_manifest)
    formal_bundle = build_formal_consumption_bundle(
        out_dir=out_dir,
        probe_manifest=probe_manifest,
        artifact_manifest=artifact_manifest,
        artifact_paths=artifact_paths,
        audit_rows=audit_rows,
        theorem_readiness=theorem_readiness_rows,
    )
    write_json(out_dir / "formal_channel_consumption_bundle.json", formal_bundle)
    return {
        "probe_id": probe_manifest["probe_id"],
        "out_dir": str(out_dir),
        "channel_count": len(all_channel_rows),
        "recoverability_rows": len(recoverability_bundle["recoverability"]),
        "claim_boundary": CLAIM_BOUNDARY,
        "artifact_manifest_digest": artifact_manifest["artifact_manifest_digest"],
        "formal_consumption_status": formal_bundle["formal_consumption_status"],
    }


def build_probe_manifest(
    *,
    all_channel_rows: list[dict[str, object]],
    distinctions: list[dict[str, object]],
    artifact_paths: dict[str, str],
    csv_output_mode: str,
) -> dict[str, object]:
    payload = {
        "channel_ids": [row["channel_id"] for row in all_channel_rows],
        "distinction_ids": [row["distinction_id"] for row in distinctions],
        "artifact_paths": artifact_paths,
    }
    return {
        "probe_id": "stochastic_distinction_channel_probe_v0",
        "probe_schema_version": "0.1.0",
        "csv_output_mode": csv_output_mode,
        "source_carrier": "X2",
        "primary_target_carrier": "Y2",
        "channel_count": len(all_channel_rows),
        "distinction_count": len(distinctions),
        "tightening_notes": canonical_json(
            {
                "decoder_policy_manifest": True,
                "formal_channel_consumption_bundle": True,
                "observation_scope_explicit": True,
                "exact_vs_probabilistic_recovery_separated": True,
                "exact_support_requires_source_label_coverage": True,
                "normalized_recovery_over_chance": True,
                "selected_target_distinctions_emitted": True,
                "support_vs_probability_summary": True,
                "theorem_transfer_readiness_summary": True,
                "executive_summary_in_report": True,
            }
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "probe_digest": stable_hash(payload, length=24),
    }


def build_formal_consumption_bundle(
    *,
    out_dir: Path,
    probe_manifest: dict[str, object],
    artifact_manifest: dict[str, object],
    artifact_paths: dict[str, str],
    audit_rows: dict[str, list[dict[str, object]]],
    theorem_readiness: list[dict[str, object]],
) -> dict[str, object]:
    audit_failures = sum(1 for rows in audit_rows.values() for row in rows if row.get("status") == "FAIL")
    support_ready = any(
        row["formal_object"] == "support_level_exact_channel_presentation"
        and row["readiness_status"] == "ready_for_formal_support_consumption"
        for row in theorem_readiness
    )
    status = (
        "support_level_ready_probabilistic_measurement_only"
        if support_ready and audit_failures == 0
        else "blocked_audit_failure"
    )
    consumption_artifacts = {
        "channel_probe_manifest": "channel_probe_manifest.json",
        "artifact_manifest": "artifact_manifest.json",
        "carrier_manifest": artifact_paths["carrier_manifest.csv"],
        "channel_manifest": artifact_paths["channel_manifest.csv"],
        "channel_matrix": artifact_paths["channel_matrix.csv"],
        "channel_support": artifact_paths["channel_support.csv"],
        "support_relation": artifact_paths["support_relation.csv"],
        "support_recoverability": artifact_paths["support_recoverability.csv"],
        "distinction_manifest": artifact_paths["distinction_manifest.csv"],
        "source_observation_table": artifact_paths["source_observation_table.csv"],
        "target_observation_table": artifact_paths["target_observation_table.csv"],
        "decoder_policy_manifest": artifact_paths["decoder_policy_manifest.csv"],
        "recoverability_by_distinction": artifact_paths["recoverability_by_distinction.csv"],
        "non_erasure_by_channel": artifact_paths["non_erasure_by_channel.csv"],
        "support_vs_probability_summary": artifact_paths["support_vs_probability_summary.csv"],
        "theorem_transfer_readiness_summary": artifact_paths["theorem_transfer_readiness_summary.csv"],
        "report": "stochastic_channel_probe_report.md",
    }
    payload = {
        "probe_digest": probe_manifest["probe_digest"],
        "artifact_manifest_digest": artifact_manifest["artifact_manifest_digest"],
        "consumption_artifacts": consumption_artifacts,
        "formal_consumption_status": status,
    }
    return {
        "adapter_id": "stochastic_distinction_channel_support_v0",
        "adapter_schema_version": "0.2.0",
        "presentation_type": "finite stochastic channel with support projection and probabilistic recovery layer",
        "probe_id": probe_manifest["probe_id"],
        "probe_digest": probe_manifest["probe_digest"],
        "artifact_manifest_digest": artifact_manifest["artifact_manifest_digest"],
        "output_directory": str(out_dir),
        "consumption_artifacts": consumption_artifacts,
        "formal_consumption_status": status,
        "strict_support_consumption": int(support_ready and audit_failures == 0),
        "probabilistic_consumption": "measurement_only_pending_formal_theorem",
        "claim_boundary": CLAIM_BOUNDARY,
        "bundle_digest": stable_hash(payload, length=24),
    }


def build_artifact_manifest(
    *,
    out_dir: Path,
    artifact_paths: dict[str, str],
    csv_outputs: dict[str, list[dict[str, object]]],
    extra_files: list[str],
) -> dict[str, object]:
    artifacts = []
    for logical, physical in sorted(artifact_paths.items()):
        path = out_dir / physical
        artifacts.append(
            {
                "logical_name": logical,
                "physical_name": physical,
                "row_count": len(csv_outputs[logical]),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    for name in extra_files:
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


def render_report(
    *,
    probe_manifest: dict[str, object],
    audits: dict[str, list[dict[str, object]]],
    recoverability: list[dict[str, object]],
    non_erasure: list[dict[str, object]],
    marginal_joint: list[dict[str, object]],
    decoder_policy: list[dict[str, object]],
    support_probability: list[dict[str, object]],
    baseline_comparison: list[dict[str, object]],
    composition_checks: list[dict[str, object]],
    theorem_readiness: list[dict[str, object]],
) -> str:
    audit_failures = {
        name: sum(1 for row in rows if row.get("status") == "FAIL")
        for name, rows in audits.items()
    }
    exact_identity = selected_success(recoverability, "identity_channel", "D_joint")
    erasure_joint = selected_success(recoverability, "total_erasure_channel", "D_joint")
    mj_class_counts = count_by(marginal_joint, "diagnostic_class")
    return "\n".join(
        [
            "# Stochastic Distinction Channel Probe v0",
            "",
            "## Executive Summary",
            "",
            "A tiny finite stochastic-channel substrate was built with declared carriers, "
            "distinctions, priors, decoders, thresholds, support projections, and "
            "composition checks. Identity recovers the declared joint distinction, total "
            "erasure does not, and nonzero stochastic noise separates support-level exact "
            "recoverability from probabilistic decoder success. This tightened pass adds "
            "formal decoder policies, selected target-observation provenance, support-vs-"
            "probability summaries, and theorem-transfer readiness. The probe is suitable "
            "as a formal-consumption bridge only; it makes no Omega, agency, identity, "
            "value, compatibility, or ethical claim.",
            "",
            "## Summary",
            "",
            f"- probe id: `{probe_manifest['probe_id']}`",
            f"- channel count: {probe_manifest['channel_count']}",
            f"- distinction count: {probe_manifest['distinction_count']}",
            f"- identity joint best success: {exact_identity:.6f}",
            f"- total erasure joint best success: {erasure_joint:.6f}",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## Carriers And Distinctions",
            "",
            "Primary source carrier is `X2 = {00,01,10,11}`. Distinctions include `D_A`, "
            "`D_B`, `D_joint`, `D_parity`, and `D_trivial`. Target observation scope is "
            "explicit in every distinction and recoverability row.",
            "",
            "## Channel Families",
            "",
            "Included identity, total erasure, projection, independent bit-flip, asymmetric "
            "bit noise, asymmetric bit erasure, marginal-preserving joint-degrading, "
            "output-marginal matched, deterministic entropy-matched random-like, and composed "
            "cascade channels.",
            "",
            "## Priors And Decoders",
            "",
            "Uniform source priors are declared for `X2` and `Y2`. Bayes-optimal decoders are "
            "emitted for all distinction pairs; exact decoders are emitted when support-level "
            "exact recovery exists; declared same-label decoders are emitted when label sets match.",
            "",
            "Decoder policies are explicit:",
            "",
            *(f"- `{row['decoder_policy_id']}`: {row['formal_consumption_status']}" for row in decoder_policy),
            "",
            "## Audit Summary",
            "",
            *(f"- `{name}` failures: {count}" for name, count in sorted(audit_failures.items())),
            "",
            "## Exact And Probabilistic Recoverability",
            "",
            "Support-level exact recoverability and probabilistic decoder success are separate "
            "columns. For stochastic channels with full support, exact support recovery can fail "
            "while Bayes success remains above chance. Exact support recovery now requires both "
            "nonambiguous target support and coverage of all positive-prior source labels.",
            "",
            *support_probability_summary_for_report(support_probability),
            "",
            "## Non-Erasure Requirement Sets",
            "",
            *summarize_non_erasure(non_erasure),
            "",
            "## Marginal-Versus-Joint Diagnostic",
            "",
            *(f"- `{key}`: {value}" for key, value in sorted(mj_class_counts.items())),
            "",
            "The diagnostic is finite stochastic-channel structure only. It is not compatibility "
            "or ethical erasure.",
            "",
            "## Baseline Comparisons",
            "",
            *channel_baseline_summary_for_report(baseline_comparison),
            "",
            "## Channel Composition",
            "",
            f"- composition check rows: {len(composition_checks)}",
            "Composition rows report measured composed success and a simple product-success "
            "reference. They are measurement rows, not standalone theorems.",
            "",
            "## Support-Level Export For Lean Root Calculus",
            "",
            "`support_relation.csv` and `support_recoverability.csv` expose `K(y|x) > 0` and "
            "exact support-recoverability candidates so the formal arm can compare support-level "
            "root calculus against probabilistic recovery.",
            "",
            "## Theorem Transfer Readiness",
            "",
            *(f"- `{row['formal_object']}`: {row['readiness_status']}" for row in theorem_readiness),
            "",
            "## Formal Consumption Bundle",
            "",
            "`formal_channel_consumption_bundle.json` identifies the compact artifact set that "
            "the formal arm should consume. Support-level exact rows are separated from "
            "probabilistic measurement rows.",
            "",
            "## Limitations",
            "",
            "The carrier is tiny, thresholds are conventional rather than discovered, and all "
            "distinctions are hand-declared finite labels. This is a clean formal bridge, not a "
            "scientific validation result.",
            "",
            "## Recommended Next Formal Target",
            "",
            "Ask the formal arm to consume the support-level exact rows and the probabilistic "
            "recovery rows separately. If useful, the next empirical repair should add a theorem "
            "or audit for probabilistic composition bounds, not broader channels.",
        ]
    )


def selected_success(recoverability: list[dict[str, object]], channel_id: str, source_distinction_id: str) -> float:
    values = [
        float(row["decoder_success_probability"])
        for row in recoverability
        if row["channel_id"] == channel_id
        and row["source_distinction_id"] == source_distinction_id
        and row["decoder_kind"] == "bayes_optimal_decoder"
    ]
    return max(values) if values else 0.0


def summarize_non_erasure(rows: list[dict[str, object]]) -> list[str]:
    out = []
    for row in rows:
        if row["channel_id"] not in ("identity_channel", "total_erasure_channel", "marginal_joint_degrade_q_0_10"):
            continue
        out.append(
            f"- `{row['channel_id']}` / `{row['requirement_set_id']}`: "
            f"{row['recovered_count']}/{row['required_count']} recovered at `{row['threshold_id']}`"
        )
    return out[:18]


def support_probability_summary_for_report(rows: list[dict[str, object]]) -> list[str]:
    wanted = {
        ("identity_channel", "D_joint"),
        ("total_erasure_channel", "D_joint"),
        ("bit_flip_p_0_05", "D_A"),
        ("bit_flip_p_0_05", "D_joint"),
        ("marginal_joint_degrade_q_0_10", "D_A"),
        ("marginal_joint_degrade_q_0_10", "D_joint"),
    }
    out = []
    for row in rows:
        key = (str(row["channel_id"]), str(row["source_distinction_id"]))
        if key not in wanted:
            continue
        out.append(
            f"- `{row['channel_id']}` / `{row['source_distinction_id']}`: "
            f"{row['support_probability_relation']} "
            f"(best target `{row['best_probability_target_distinction_id']}`, "
            f"success {float(row['best_probability_success']):.6f})"
        )
    return out


def count_by(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get(field, ""))
        counts[key] = counts.get(key, 0) + 1
    return counts


def csv_name(name: str, mode: str) -> str:
    return f"{name}.gz" if mode == "gzip" and name.endswith(".csv") else name


if __name__ == "__main__":
    main()
