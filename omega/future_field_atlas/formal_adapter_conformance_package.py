"""Compile retained Future Field Atlas outputs into a formal adapter package.

This module does not run new empirical scans. It reads the retained
formal-interface distinction panel and emits a primitive-calculus-facing
adapter package: contexts, unfoldings, distinction fibers, preorder rows,
transport witnesses, closure, law checks, non-erasure checks, theorem-transfer
status, and reports.

Claim boundary: adapter formalization only. No Omega validation, no valuerhood,
no compatibility detection, and no support/capture/erasure claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .formal_adapter_analysis import (
    build_marginal_joint_diagnostic,
    build_non_erasure_rows,
    build_recoverability_rows,
    build_requirement_manifest,
    build_theorem_transfer_summary,
    classify_adapter_status,
)
from .formal_adapter_geometry import (
    build_contexts,
    build_distinction_fibers,
    build_preorder,
    build_unfoldings,
)
from .formal_adapter_panel import input_gate, load_panel
from .formal_adapter_reports import (
    build_bundle,
    render_conformance_report,
    render_failure_report,
    write_blocked_package,
)
from .formal_adapter_schema import DEFAULT_INPUT_PANEL, DEFAULT_OUT, csv_artifact_name
from .formal_adapter_transport import (
    build_closed_transport,
    build_law_checks,
    build_law_summary_rows,
    build_raw_witnesses,
)
from .util import write_csv, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a formal adapter conformance package from retained FFA panel outputs."
    )
    parser.add_argument("--input-panel", type=Path, default=DEFAULT_INPUT_PANEL)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    parser.add_argument("--csv-output-mode", choices=("gzip", "plain"), default="gzip")
    parser.add_argument("--write-report", action="store_true", default=True)
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    result = build_package(
        input_panel=args.input_panel,
        out_dir=args.out,
        gzip_compresslevel=args.gzip_compresslevel,
        csv_output_mode=args.csv_output_mode,
        write_report=bool(args.write_report),
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))

def build_package(
    *,
    input_panel: Path,
    out_dir: Path,
    gzip_compresslevel: int = 1,
    csv_output_mode: str = "gzip",
    write_report: bool = True,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    panel = load_panel(input_panel)
    gate = input_gate(panel)
    if gate["adapter_status"] == "blocked_input_incomplete":
        return write_blocked_package(
            input_panel=input_panel,
            out_dir=out_dir,
            panel=panel,
            gate=gate,
            gzip_compresslevel=gzip_compresslevel,
            csv_output_mode=csv_output_mode,
            write_report=write_report,
        )

    contexts = build_contexts(panel)
    unfoldings = build_unfoldings(contexts)
    fibers, token_lookup = build_distinction_fibers(panel, contexts)
    preorder_rows, preorder_open_questions, preorder_checks, preorder_by_context = build_preorder(
        fibers
    )
    raw_witnesses = build_raw_witnesses(
        unfoldings=unfoldings,
        token_lookup=token_lookup,
        preorder_by_context=preorder_by_context,
        persistence_rows=panel["persistence_rows"],
    )
    closure = build_closed_transport(
        unfoldings=unfoldings,
        fibers=fibers,
        preorder_by_context=preorder_by_context,
        raw_witnesses=raw_witnesses,
    )
    law_tables = build_law_checks(
        unfoldings=unfoldings,
        preorder_rows=preorder_rows,
        raw_witnesses=raw_witnesses,
        closed_rows=closure,
        preorder_by_context=preorder_by_context,
    )
    requirement_manifest = build_requirement_manifest(fibers)
    recoverability_rows = build_recoverability_rows(
        requirement_manifest=requirement_manifest,
        unfoldings=unfoldings,
        token_lookup=token_lookup,
        raw_witnesses=raw_witnesses,
        closed_rows=closure,
    )
    non_erasure_rows = build_non_erasure_rows(recoverability_rows)
    marginal_joint_rows = build_marginal_joint_diagnostic(panel)
    theorem_transfer_rows = build_theorem_transfer_summary(law_tables, non_erasure_rows)
    law_summary_rows = build_law_summary_rows(law_tables)
    adapter_status = classify_adapter_status(law_summary_rows, gate)

    csv_outputs: dict[str, list[dict[str, object]]] = {
        "context_manifest.csv": contexts,
        "unfolding_manifest.csv": unfoldings,
        "distinction_fiber_manifest.csv": fibers,
        "distinction_preorder_manifest.csv": preorder_rows,
        "preorder_open_questions.csv": preorder_open_questions,
        "distinction_preorder_check.csv": preorder_checks,
        "raw_transport_witnesses.csv": raw_witnesses,
        "closed_transport_relation.csv": closure,
        "adapter_law_check_summary.csv": law_summary_rows,
        "identity_transport_check.csv": law_tables["identity_transport_check"],
        "source_weakening_check.csv": law_tables["source_weakening_check"],
        "target_strengthening_check.csv": law_tables["target_strengthening_check"],
        "lax_composition_check.csv": law_tables["lax_composition_check"],
        "recoverability_witness_by_requirement.csv": recoverability_rows,
        "non_erasure_requirement_manifest.csv": requirement_manifest,
        "non_erasure_by_unfolding.csv": non_erasure_rows,
        "marginal_joint_non_erasure_diagnostic.csv": marginal_joint_rows,
        "adapter_theorem_transfer_summary.csv": theorem_transfer_rows,
    }
    artifact_paths = {
        logical_name: csv_artifact_name(logical_name, csv_output_mode)
        for logical_name in csv_outputs
    }
    for logical_name, rows in csv_outputs.items():
        write_csv(
            out_dir / artifact_paths[logical_name],
            rows,
            gzip_compresslevel=gzip_compresslevel,
        )

    failure_report = render_failure_report(
        gate=gate,
        law_summary_rows=law_summary_rows,
        theorem_transfer_rows=theorem_transfer_rows,
        preorder_open_questions=preorder_open_questions,
        closure=closure,
        non_erasure_rows=non_erasure_rows,
    )
    (out_dir / "adapter_failure_report.md").write_text(failure_report, encoding="utf-8")

    bundle = build_bundle(
        input_panel=input_panel,
        panel=panel,
        adapter_status=adapter_status,
        csv_output_mode=csv_output_mode,
        artifact_paths=artifact_paths,
        output_files=sorted(artifact_paths.values()) + [
            "adapter_failure_report.md",
            "formal_consumption_bundle.json",
            "formal_adapter_conformance_report.md",
        ],
    )
    write_json(out_dir / "formal_consumption_bundle.json", bundle)
    if write_report:
        report = render_conformance_report(
            bundle=bundle,
            gate=gate,
            contexts=contexts,
            unfoldings=unfoldings,
            fibers=fibers,
            preorder_rows=preorder_rows,
            raw_witnesses=raw_witnesses,
            closure=closure,
            law_summary_rows=law_summary_rows,
            non_erasure_rows=non_erasure_rows,
            marginal_joint_rows=marginal_joint_rows,
            theorem_transfer_rows=theorem_transfer_rows,
        )
        (out_dir / "formal_adapter_conformance_report.md").write_text(
            report, encoding="utf-8"
        )

    return bundle


if __name__ == "__main__":
    main()
