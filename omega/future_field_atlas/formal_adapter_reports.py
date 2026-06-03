"""Report and bundle rendering for the FFA formal adapter package."""

from __future__ import annotations

from pathlib import Path

from .formal_adapter_schema import (
    ADAPTER_ID,
    ADAPTER_SCHEMA_VERSION,
    CLAIM_BOUNDARY,
    PRESENTATION_TYPE,
    SUBSTRATE_STATUS,
    count_by,
    csv_artifact_name,
)
from .util import stable_hash, utc_now, write_csv, write_json


def write_blocked_package(
    *,
    input_panel: Path,
    out_dir: Path,
    panel: dict[str, object],
    gate: dict[str, object],
    gzip_compresslevel: int,
    csv_output_mode: str,
    write_report: bool,
) -> dict[str, object]:
    law_summary_path = csv_artifact_name("adapter_law_check_summary.csv", csv_output_mode)
    rows = [
        {
            "adapter_id": ADAPTER_ID,
            "adapter_status": "blocked_input_incomplete",
            "blocked_reasons": ";".join(gate["blocked_reasons"]),
            "input_panel": str(input_panel),
        }
    ]
    write_csv(out_dir / law_summary_path, rows, gzip_compresslevel=gzip_compresslevel)
    report = "\n".join(
        [
            "# Formal Adapter Conformance Package",
            "",
            "## Status",
            "",
            "`blocked_input_incomplete`",
            "",
            "## Blocked Reasons",
            "",
            *[f"- {reason}" for reason in gate["blocked_reasons"]],
            "",
            "No missing empirical structure was patched silently.",
        ]
    )
    (out_dir / "adapter_failure_report.md").write_text(report, encoding="utf-8")
    bundle = build_bundle(
        input_panel=input_panel,
        panel=panel,
        adapter_status="blocked_input_incomplete",
        csv_output_mode=csv_output_mode,
        artifact_paths={"adapter_law_check_summary.csv": law_summary_path},
        output_files=[
            law_summary_path,
            "adapter_failure_report.md",
            "formal_consumption_bundle.json",
        ],
    )
    write_json(out_dir / "formal_consumption_bundle.json", bundle)
    if write_report:
        (out_dir / "formal_adapter_conformance_report.md").write_text(report, encoding="utf-8")
    return bundle

def build_bundle(
    *,
    input_panel: Path,
    panel: dict[str, object],
    adapter_status: str,
    csv_output_mode: str,
    artifact_paths: dict[str, str],
    output_files: list[str],
) -> dict[str, object]:
    manifest = panel.get("manifest", {})
    return {
        "adapter_id": ADAPTER_ID,
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "presentation_type": PRESENTATION_TYPE,
        "substrate_status": SUBSTRATE_STATUS,
        "created_utc": utc_now(),
        "input_panel_path": str(input_panel),
        "input_panel_digest": manifest.get("panel_digest", ""),
        "csv_output_mode": csv_output_mode,
        "context_manifest_path": artifact_paths.get("context_manifest.csv", "context_manifest.csv"),
        "unfolding_manifest_path": artifact_paths.get("unfolding_manifest.csv", "unfolding_manifest.csv"),
        "distinction_fiber_manifest_path": artifact_paths.get("distinction_fiber_manifest.csv", "distinction_fiber_manifest.csv"),
        "distinction_preorder_manifest_path": artifact_paths.get("distinction_preorder_manifest.csv", "distinction_preorder_manifest.csv"),
        "closed_transport_relation_path": artifact_paths.get("closed_transport_relation.csv", "closed_transport_relation.csv"),
        "non_erasure_requirement_manifest_path": artifact_paths.get("non_erasure_requirement_manifest.csv", "non_erasure_requirement_manifest.csv"),
        "adapter_law_check_summary_path": artifact_paths.get("adapter_law_check_summary.csv", "adapter_law_check_summary.csv"),
        "theorem_transfer_summary_path": artifact_paths.get("adapter_theorem_transfer_summary.csv", "adapter_theorem_transfer_summary.csv"),
        "adapter_status": adapter_status,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": output_files,
        "bundle_digest": stable_hash({"adapter": ADAPTER_ID, "panel": manifest.get("panel_digest", ""), "outputs": output_files}, length=24),
    }

def render_failure_report(
    *,
    gate: dict[str, object],
    law_summary_rows: list[dict[str, object]],
    theorem_transfer_rows: list[dict[str, object]],
    preorder_open_questions: list[dict[str, object]],
    closure: list[dict[str, object]],
    non_erasure_rows: list[dict[str, object]],
) -> str:
    closure_derived = sum(1 for row in closure if str(row.get("support_kind")) != "raw_observed")
    theorem_blocked = [
        row for row in theorem_transfer_rows if str(row.get("transfer_status", "")).startswith("blocked")
    ]
    not_recovered = [row for row in non_erasure_rows if int(row.get("not_recovered_count", 0)) > 0]
    return "\n".join(
        [
            "# Adapter Failure Report",
            "",
            "Failure and limitation reporting is formal information, not embarrassment.",
            "",
            "## Input Gate",
            "",
            f"- status: `{gate['adapter_status']}`",
            f"- blocked reasons: `{';'.join(gate['blocked_reasons']) if gate['blocked_reasons'] else 'none'}`",
            "",
            "## Law Checks",
            "",
            *[
                f"- {row['law_check']}: status={row['status']}, raw={row['raw_pass_count']}/{row['row_count']}, closed={row['closed_pass_count']}/{row['row_count']}"
                for row in law_summary_rows
            ],
            "",
            "## Closure Burden",
            "",
            f"- closure-derived transport rows: {closure_derived}",
            "",
            "## Preorder Open Questions",
            "",
            *(f"- {row['context_id']}: {row['candidate_relation']} ({row['reason']})" for row in preorder_open_questions[:50]),
            "",
            "## Non-Erasure Gaps",
            "",
            *(f"- {row['requirement_set_id']} {row['unfolding_id']}: not_recovered={row['not_recovered_count']}" for row in not_recovered[:50]),
            "",
            "## Blocked Theorems",
            "",
            *(f"- {row['theorem_id']}: {row['transfer_status']} ({row['notes']})" for row in theorem_blocked),
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
        ]
    )

def render_conformance_report(
    *,
    bundle: dict[str, object],
    gate: dict[str, object],
    contexts: list[dict[str, object]],
    unfoldings: list[dict[str, object]],
    fibers: list[dict[str, object]],
    preorder_rows: list[dict[str, object]],
    raw_witnesses: list[dict[str, object]],
    closure: list[dict[str, object]],
    law_summary_rows: list[dict[str, object]],
    non_erasure_rows: list[dict[str, object]],
    marginal_joint_rows: list[dict[str, object]],
    theorem_transfer_rows: list[dict[str, object]],
) -> str:
    closure_by_kind = count_by(closure, "support_kind")
    diagnostic_by_class = count_by(marginal_joint_rows, "diagnostic_class")
    theorem_by_status = count_by(theorem_transfer_rows, "transfer_status")
    return "\n".join(
        [
            "# Future Field Atlas Formal Adapter Conformance Package",
            "",
            "## Summary",
            "",
            f"- adapter id: `{bundle['adapter_id']}`",
            f"- adapter status: `{bundle['adapter_status']}`",
            f"- input panel digest: `{bundle.get('input_panel_digest', '')}`",
            f"- csv output mode: `{bundle.get('csv_output_mode', '')}`",
            f"- contexts: {len(contexts)}",
            f"- unfoldings: {len(unfoldings)}",
            f"- distinction fiber rows: {len(fibers)}",
            f"- preorder rows: {len(preorder_rows)}",
            f"- raw witnesses: {len(raw_witnesses)}",
            f"- closed transport rows: {len(closure)}",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## Inputs",
            "",
            f"- gate status: `{gate['adapter_status']}`",
            f"- requested cells: {gate.get('requested_cells', '')}",
            f"- available cells: {gate.get('available_cells', '')}",
            f"- missing or blocked cells: {gate.get('missing_or_blocked_cells', '')}",
            "",
            "## Closed Transport Relation",
            "",
            *(f"- {key}: {value}" for key, value in sorted(closure_by_kind.items())),
            "",
            "## Root Law Checks",
            "",
            *[
                f"- {row['law_check']}: {row['status']} (raw {row['raw_pass_count']}/{row['row_count']}; closed {row['closed_pass_count']}/{row['row_count']})"
                for row in law_summary_rows
            ],
            "",
            "## Non-Erasure Requirements",
            "",
            f"- rows: {len(non_erasure_rows)}",
            f"- closed non-erasing rows: {sum(int(row.get('non_erasing_closed', 0)) for row in non_erasure_rows)}",
            f"- raw non-erasing rows: {sum(int(row.get('non_erasing_raw', 0)) for row in non_erasure_rows)}",
            "",
            "## Marginal-Versus-Joint Diagnostic",
            "",
            *(f"- {key}: {value}" for key, value in sorted(diagnostic_by_class.items())),
            "",
            "## Theorem Transfer Summary",
            "",
            *(f"- {key}: {value}" for key, value in sorted(theorem_by_status.items())),
            "",
            "## Interpretation",
            "",
            "This package exposes retained FFA finite-measure artifacts as a candidate "
            "formal adapter package. The generated closed presentation may support "
            "root-law theorem transfer even where the raw empirical relation does not. "
            "That distinction is mandatory and is reported in the law tables.",
            "",
            "This is not Omega validation and not a semantic detection result.",
        ]
    )
