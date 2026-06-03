"""Summarize the raw/closed gap in an FFA formal adapter package.

This is a compact audit postprocessor. It reads a completed formal adapter
conformance package and reports where theorem transfer depends on generated
closure rather than direct raw witness rows.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from .formal_adapter_schema import csv_artifact_name, floatish, intish
from .util import read_csv, stable_hash, write_csv, write_json


DEFAULT_INPUT = Path("results/future_field_atlas/20260603_formal_adapter_conformance_package")
DEFAULT_OUT = Path("results/future_field_atlas/20260603_formal_adapter_raw_closed_gap_report")
CLAIM_BOUNDARY = (
    "raw/closed adapter-gap audit only; no Omega validation, no compatibility "
    "detection, no proto-valuer / valuer detection, no support/capture/erasure detection"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a compact raw/closed gap report.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    parser.add_argument("--csv-output-mode", choices=("gzip", "plain"), default="gzip")
    parser.add_argument("--sample-limit", type=int, default=250)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_gap_report(
        input_dir=args.input,
        out_dir=args.out,
        gzip_compresslevel=args.gzip_compresslevel,
        csv_output_mode=args.csv_output_mode,
        sample_limit=args.sample_limit,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def build_gap_report(
    *,
    input_dir: Path,
    out_dir: Path,
    gzip_compresslevel: int = 1,
    csv_output_mode: str = "gzip",
    sample_limit: int = 250,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    package = load_package(input_dir)
    law_gap_rows = build_law_gap_summary(package["law_summary"])
    closure_support_rows = build_closure_support_summary(package["closed_transport"])
    closure_depth_rows = build_closure_depth_summary(package["closed_transport"])
    law_detail_rows = build_law_detail_gap_summary(package)
    law_sample_rows = build_law_gap_samples(package, sample_limit=sample_limit)
    token_pair_rows = build_closure_token_pair_summary(package)
    theorem_rows = build_theorem_closure_dependency(package["theorem_transfer"], law_gap_rows)
    non_erasure_rows = build_non_erasure_gap_summary(package["non_erasure"])
    recommendation_rows = build_raw_witness_recommendations(law_gap_rows, closure_support_rows)

    csv_outputs: dict[str, list[dict[str, object]]] = {
        "law_raw_closed_gap_summary.csv": law_gap_rows,
        "closure_support_kind_summary.csv": closure_support_rows,
        "closure_depth_summary.csv": closure_depth_rows,
        "law_detail_gap_by_cell.csv": law_detail_rows,
        "closure_only_law_gap_examples.csv": law_sample_rows,
        "closure_only_token_pair_summary.csv": token_pair_rows,
        "theorem_transfer_closure_dependency.csv": theorem_rows,
        "non_erasure_raw_closed_gap_summary.csv": non_erasure_rows,
        "raw_witness_recommendations.csv": recommendation_rows,
    }
    artifact_paths = {
        logical: csv_artifact_name(logical, csv_output_mode)
        for logical in csv_outputs
    }
    for logical, rows in csv_outputs.items():
        write_csv(out_dir / artifact_paths[logical], rows, gzip_compresslevel=gzip_compresslevel)

    report = render_report(
        input_dir=input_dir,
        bundle=package["bundle"],
        law_gap_rows=law_gap_rows,
        closure_support_rows=closure_support_rows,
        theorem_rows=theorem_rows,
        non_erasure_rows=non_erasure_rows,
        recommendation_rows=recommendation_rows,
    )
    (out_dir / "formal_adapter_raw_closed_gap_report.md").write_text(report, encoding="utf-8")
    bundle = {
        "gap_report_id": "ffa_adapter_raw_closed_gap_report_v0",
        "input_adapter_bundle_digest": package["bundle"].get("bundle_digest", ""),
        "input_adapter_status": package["bundle"].get("adapter_status", ""),
        "csv_output_mode": csv_output_mode,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": sorted(artifact_paths.values()) + ["formal_adapter_raw_closed_gap_report.md"],
        "report_digest": stable_hash(
            {
                "input": package["bundle"].get("bundle_digest", ""),
                "outputs": sorted(artifact_paths.values()),
                "law_gap": law_gap_rows,
            },
            length=24,
        ),
    }
    write_json(out_dir / "formal_adapter_raw_closed_gap_bundle.json", bundle)
    return bundle


def load_package(input_dir: Path) -> dict[str, object]:
    bundle_path = input_dir / "formal_consumption_bundle.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

    def rows(path_key: str, fallback: str) -> list[dict[str, object]]:
        return read_csv(input_dir / str(bundle.get(path_key, fallback)))

    return {
        "bundle": bundle,
        "law_summary": rows("adapter_law_check_summary_path", "adapter_law_check_summary.csv.gz"),
        "theorem_transfer": rows("theorem_transfer_summary_path", "adapter_theorem_transfer_summary.csv.gz"),
        "closed_transport": rows("closed_transport_relation_path", "closed_transport_relation.csv.gz"),
        "unfoldings": rows("unfolding_manifest_path", "unfolding_manifest.csv.gz"),
        "contexts": rows("context_manifest_path", "context_manifest.csv.gz"),
        "non_erasure": read_csv(input_dir / "non_erasure_by_unfolding.csv.gz"),
        "identity": read_csv(input_dir / "identity_transport_check.csv.gz"),
        "source_weakening": read_csv(input_dir / "source_weakening_check.csv.gz"),
        "target_strengthening": read_csv(input_dir / "target_strengthening_check.csv.gz"),
        "lax_composition": read_csv(input_dir / "lax_composition_check.csv.gz"),
    }


def build_law_gap_summary(law_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in law_rows:
        total = intish(row.get("row_count"))
        raw_pass = intish(row.get("raw_pass_count"))
        closed_pass = intish(row.get("closed_pass_count"))
        raw_gap = max(0, closed_pass - raw_pass)
        if raw_gap == 0:
            dependency = "none"
        elif raw_pass == 0:
            dependency = "full_generated_closure"
        else:
            dependency = "partial_generated_closure"
        rows.append(
            {
                "law_check": row.get("law_check", ""),
                "row_count": total,
                "raw_pass_count": raw_pass,
                "closed_pass_count": closed_pass,
                "raw_gap_count": raw_gap,
                "raw_gap_fraction": ratio(raw_gap, total),
                "raw_conformance": row.get("raw_conformance", ""),
                "closed_conformance": row.get("closed_conformance", ""),
                "closure_dependency": dependency,
                "status": row.get("status", ""),
            }
        )
    return rows


def build_closure_support_summary(closed_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total = len(closed_rows)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in closed_rows:
        grouped[str(row.get("support_kind", ""))].append(row)
    rows = []
    for support_kind, items in sorted(grouped.items()):
        rows.append(
            {
                "support_kind": support_kind,
                "row_count": len(items),
                "fraction_of_closed_relation": ratio(len(items), total),
                "closure_derived": int(support_kind != "raw_observed"),
                "min_closure_depth": min(intish(row.get("closure_depth")) for row in items),
                "max_closure_depth": max(intish(row.get("closure_depth")) for row in items),
            }
        )
    return rows


def build_closure_depth_summary(closed_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], int] = defaultdict(int)
    for row in closed_rows:
        grouped[(str(row.get("support_kind", "")), intish(row.get("closure_depth")))] += 1
    return [
        {
            "support_kind": support_kind,
            "closure_depth": depth,
            "row_count": count,
        }
        for (support_kind, depth), count in sorted(grouped.items())
    ]


def build_law_detail_gap_summary(package: dict[str, object]) -> list[dict[str, object]]:
    contexts = {str(row["context_id"]): row for row in package["contexts"]}  # type: ignore[index]
    unfoldings = {str(row["unfolding_id"]): row for row in package["unfoldings"]}  # type: ignore[index]
    tables = [
        ("identity_transport", package["identity"], "context_id"),
        ("source_weakening", package["source_weakening"], "unfolding_id"),
        ("target_strengthening", package["target_strengthening"], "unfolding_id"),
        ("lax_composition", package["lax_composition"], "composite_unfolding_id"),
    ]
    grouped: dict[tuple[str, str, str, str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for law, rows, id_field in tables:
        for row in rows:  # type: ignore[assignment]
            if law == "identity_transport":
                meta = contexts.get(str(row.get(id_field, "")), {})
                unfolding_kind = "identity"
                source_horizon = target_horizon = str(meta.get("horizon", ""))
            else:
                meta = unfoldings.get(str(row.get(id_field, "")), {})
                unfolding_kind = str(meta.get("unfolding_kind", ""))
                source_horizon = str(meta.get("source_horizon", ""))
                target_horizon = str(meta.get("target_horizon", ""))
            key = (
                law,
                str(meta.get("pair_id", "")),
                str(meta.get("operator_id", "")),
                unfolding_kind,
                f"{source_horizon}->{target_horizon}",
            )
            grouped[key]["row_count"] += 1
            if str(row.get("present_in_raw_transport", "0")) in ("1", "true", "True"):
                grouped[key]["raw_pass_count"] += 1
            if str(row.get("present_in_closed_transport", "0")) in ("1", "true", "True"):
                grouped[key]["closed_pass_count"] += 1
    out = []
    for (law, pair_id, operator_id, unfolding_kind, horizon_span), counts in sorted(grouped.items()):
        row_count = counts["row_count"]
        raw_pass = counts["raw_pass_count"]
        closed_pass = counts["closed_pass_count"]
        out.append(
            {
                "law_check": law,
                "pair_id": pair_id,
                "operator_id": operator_id,
                "unfolding_kind": unfolding_kind,
                "horizon_span": horizon_span,
                "row_count": row_count,
                "raw_pass_count": raw_pass,
                "closed_pass_count": closed_pass,
                "raw_gap_count": max(0, closed_pass - raw_pass),
                "raw_gap_fraction": ratio(max(0, closed_pass - raw_pass), row_count),
            }
        )
    return out


def build_law_gap_samples(package: dict[str, object], *, sample_limit: int) -> list[dict[str, object]]:
    tables = [
        ("identity_transport", package["identity"]),
        ("source_weakening", package["source_weakening"]),
        ("target_strengthening", package["target_strengthening"]),
        ("lax_composition", package["lax_composition"]),
    ]
    rows = []
    per_law_limit = max(1, sample_limit // len(tables))
    for law, table in tables:
        added = 0
        for row in table:  # type: ignore[assignment]
            if str(row.get("present_in_closed_transport", "0")) != "1":
                continue
            if str(row.get("present_in_raw_transport", "0")) == "1":
                continue
            sample = {"law_check": law}
            for key in sorted(row):
                sample[key] = row[key]
            rows.append(sample)
            added += 1
            if added >= per_law_limit:
                break
    return rows


def build_closure_token_pair_summary(package: dict[str, object]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], int] = defaultdict(int)
    for row in package["closed_transport"]:  # type: ignore[index]
        support_kind = str(row.get("support_kind", ""))
        if support_kind == "raw_observed":
            continue
        key = (
            support_kind,
            str(row.get("source_distinction_id", "")),
            str(row.get("target_distinction_id", "")),
        )
        grouped[key] += 1
    rows = [
        {
            "support_kind": support_kind,
            "source_distinction_id": source,
            "target_distinction_id": target,
            "row_count": count,
        }
        for (support_kind, source, target), count in grouped.items()
    ]
    return sorted(rows, key=lambda row: (-int(row["row_count"]), row["support_kind"], row["source_distinction_id"]))[:200]


def build_theorem_closure_dependency(
    theorem_rows: list[dict[str, object]],
    law_gap_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    law_by_name = {str(row["law_check"]): row for row in law_gap_rows}
    rows = []
    for theorem in theorem_rows:
        laws = [law for law in str(theorem.get("required_laws", "")).split(";") if law]
        law_gaps = [law_by_name[law] for law in laws if law in law_by_name]
        raw_gap_count = sum(intish(row.get("raw_gap_count")) for row in law_gaps)
        row_count = sum(intish(row.get("row_count")) for row in law_gaps)
        closure_dependency = "not_law_based_or_not_applicable"
        if law_gaps:
            closure_dependency = "none" if raw_gap_count == 0 else "depends_on_generated_closure"
        rows.append(
            {
                "theorem_id": theorem.get("theorem_id", ""),
                "transfer_status": theorem.get("transfer_status", ""),
                "required_laws": theorem.get("required_laws", ""),
                "required_law_row_count": row_count,
                "required_law_raw_gap_count": raw_gap_count,
                "required_law_raw_gap_fraction": ratio(raw_gap_count, row_count),
                "closure_dependency": closure_dependency,
                "claim_blocked": theorem.get("claim_blocked", ""),
            }
        )
    return rows


def build_non_erasure_gap_summary(non_erasure_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in non_erasure_rows:
        req = str(row.get("requirement_set_id", ""))
        grouped[req]["row_count"] += 1
        grouped[req]["closed_non_erasing_count"] += intish(row.get("non_erasing_closed"))
        grouped[req]["raw_non_erasing_count"] += intish(row.get("non_erasing_raw"))
        if intish(row.get("non_erasing_closed")) and not intish(row.get("non_erasing_raw")):
            grouped[req]["closure_only_non_erasing_count"] += 1
        if intish(row.get("not_recovered_count")):
            grouped[req]["not_recovered_row_count"] += 1
    return [
        {
            "requirement_set_id": req,
            "row_count": counts["row_count"],
            "raw_non_erasing_count": counts["raw_non_erasing_count"],
            "closed_non_erasing_count": counts["closed_non_erasing_count"],
            "closure_only_non_erasing_count": counts["closure_only_non_erasing_count"],
            "not_recovered_row_count": counts["not_recovered_row_count"],
            "closure_only_non_erasing_fraction": ratio(
                counts["closure_only_non_erasing_count"], counts["row_count"]
            ),
        }
        for req, counts in sorted(grouped.items())
    ]


def build_raw_witness_recommendations(
    law_gap_rows: list[dict[str, object]],
    closure_support_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    support_count = {str(row["support_kind"]): intish(row["row_count"]) for row in closure_support_rows}
    by_law = {str(row["law_check"]): row for row in law_gap_rows}
    return [
        {
            "target": "identity_transport",
            "gap_count": by_law.get("identity_transport", {}).get("raw_gap_count", ""),
            "recommendation": "Emit explicit raw identity witnesses only if strict raw model status is a goal; generated identity is mathematically ordinary for presentations.",
            "priority": "low_for_generated_presentation_high_for_strict_raw_model",
        },
        {
            "target": "target_strengthening",
            "gap_count": by_law.get("target_strengthening", {}).get("raw_gap_count", ""),
            "recommendation": "Add an explicit derived-raw witness table for target strengthening from observed witnesses and declared preorder before changing the empirical substrate.",
            "priority": "highest_gap_count",
        },
        {
            "target": "source_weakening",
            "gap_count": by_law.get("source_weakening", {}).get("raw_gap_count", ""),
            "recommendation": "Add an explicit derived-raw witness table for source weakening if the formal arm wants raw-closure rows materialized as evidence artifacts.",
            "priority": "high",
        },
        {
            "target": "lax_composition",
            "gap_count": by_law.get("lax_composition", {}).get("raw_gap_count", ""),
            "recommendation": "Materialize composite witness provenance linking step, horizon-to-final, and composite transports; do not run broader FFA until this provenance is audited.",
            "priority": "medium_high",
        },
        {
            "target": "closed_transport_support_kind",
            "gap_count": sum(v for k, v in support_count.items() if k != "raw_observed"),
            "recommendation": "Keep generated closure explicit. Do not collapse raw_observed and closure-derived rows in future reports.",
            "priority": "mandatory_reporting_invariant",
        },
    ]


def render_report(
    *,
    input_dir: Path,
    bundle: dict[str, object],
    law_gap_rows: list[dict[str, object]],
    closure_support_rows: list[dict[str, object]],
    theorem_rows: list[dict[str, object]],
    non_erasure_rows: list[dict[str, object]],
    recommendation_rows: list[dict[str, object]],
) -> str:
    lines = [
        "# FFA Formal Adapter Raw/Closed Gap Report",
        "",
        "## Summary",
        "",
        f"- input adapter status: `{bundle.get('adapter_status', '')}`",
        f"- input bundle digest: `{bundle.get('bundle_digest', '')}`",
        f"- input directory: `{input_dir}`",
        "",
        "This is a compact A-lite audit over the existing adapter package. It does not run a new empirical sweep.",
        "",
        "## Law Gap Summary",
        "",
        "| Law | Raw pass | Closed pass | Gap | Gap fraction | Dependency |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in law_gap_rows:
        lines.append(
            f"| `{row['law_check']}` | {row['raw_pass_count']} | {row['closed_pass_count']} | "
            f"{row['raw_gap_count']} | {floatish(row['raw_gap_fraction']):.6f} | `{row['closure_dependency']}` |"
        )
    lines.extend(
        [
            "",
            "## Closed Transport Support",
            "",
            "| Support kind | Rows | Fraction |",
            "|---|---:|---:|",
        ]
    )
    for row in closure_support_rows:
        lines.append(
            f"| `{row['support_kind']}` | {row['row_count']} | {floatish(row['fraction_of_closed_relation']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Theorem Transfer Dependency",
            "",
            "| Theorem | Transfer | Closure dependency | Raw gap fraction |",
            "|---|---|---|---:|",
        ]
    )
    for row in theorem_rows:
        lines.append(
            f"| `{row['theorem_id']}` | `{row['transfer_status']}` | `{row['closure_dependency']}` | "
            f"{floatish(row['required_law_raw_gap_fraction']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Non-Erasure Gap",
            "",
            "| Requirement | Raw non-erasing | Closed non-erasing | Closure-only |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in non_erasure_rows:
        lines.append(
            f"| `{row['requirement_set_id']}` | {row['raw_non_erasing_count']} | "
            f"{row['closed_non_erasing_count']} | {row['closure_only_non_erasing_count']} |"
        )
    lines.extend(
        [
            "",
            "## Recommendations",
            "",
        ]
    )
    for row in recommendation_rows:
        lines.append(f"- `{row['target']}`: {row['recommendation']}")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "The formal adapter remains safe to consume as a generated closed presentation. "
            "The raw empirical witness relation remains below strict raw conformance. "
            "The next repair, if requested, should materialize explicit raw/derived witness "
            "provenance for target strengthening, source weakening, and composition before "
            "adding candidate-family or admissibility machinery.",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
        ]
    )
    return "\n".join(lines)


def ratio(numerator: int | float, denominator: int | float) -> float:
    denominator = float(denominator)
    return float(numerator) / denominator if denominator else 0.0


if __name__ == "__main__":
    main()
