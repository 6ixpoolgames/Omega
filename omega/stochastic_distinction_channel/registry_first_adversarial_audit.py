"""Adversarial provenance audit for registry-first stochastic-channel outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from omega.future_field_atlas.util import read_csv, stable_hash, write_csv, write_json


REQUIRED_FILES = [
    "registry_digest.json",
    "manifest_digest_chain.json",
    "registry_first_probe_manifest.json",
    "registry_first_formal_consumption_bundle.json",
    "registry_manifest.csv",
    "declared_decoder_registry.csv",
    "requirement_set_manifest.csv",
    "threshold_manifest.csv",
    "registered_recovery_by_distinction.csv",
    "existence_recovery_by_distinction.csv",
    "optimized_recovery_diagnostic.csv",
    "provenance_gap_by_distinction.csv",
    "path_ensemble_rows.csv",
    "cascade_evidence_summary.csv",
    "theorem_transfer_readiness.csv",
]

SCORED_FILES_WITH_DIGESTS = [
    "registered_recovery_by_distinction.csv",
    "existence_recovery_by_distinction.csv",
    "optimized_recovery_diagnostic.csv",
    "provenance_gap_by_distinction.csv",
    "path_ensemble_rows.csv",
    "cascade_evidence_summary.csv",
    "theorem_transfer_readiness.csv",
    "channel_matrix.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit registry-first stochastic-channel provenance.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = audit_registry_first_output(source_dir=args.source, out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def audit_registry_first_output(*, source_dir: Path, out_dir: Path | None = None) -> dict[str, object]:
    rows: list[dict[str, object]] = []

    for name in REQUIRED_FILES:
        rows.append(
            audit_row(
                "required_file_present",
                "PASS" if (source_dir / name).exists() else "FAIL",
                name,
            )
        )

    registry_digest = read_json(source_dir / "registry_digest.json")
    digest_chain = read_json(source_dir / "manifest_digest_chain.json")
    bundle = read_json(source_dir / "registry_first_formal_consumption_bundle.json")

    expected_registry_digest = str(registry_digest.get("registry_digest", ""))
    expected_manifest_digest = str(registry_digest.get("manifest_bundle_digest", ""))

    rows.extend(audit_digest_chain(source_dir=source_dir, digest_chain=digest_chain))
    rows.extend(
        audit_scored_row_digests(
            source_dir=source_dir,
            registry_digest=expected_registry_digest,
            manifest_bundle_digest=expected_manifest_digest,
        )
    )
    rows.extend(audit_policy_boundaries(source_dir=source_dir))
    rows.extend(audit_cascade_evidence(source_dir=source_dir))
    rows.extend(audit_overall_status(bundle=bundle))

    failures = [row for row in rows if row["status"] == "FAIL"]
    overall_status = "PASS" if not failures else "FAIL_BLOCK_THEOREM_TRANSFER"
    summary = {
        "source_dir": str(source_dir),
        "overall_status": overall_status,
        "audit_rows": len(rows),
        "failure_count": len(failures),
        "failed_audits": sorted({str(row["audit_id"]) for row in failures}),
    }

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        write_csv(out_dir / "registry_first_adversarial_audit.csv", rows)
        write_json(out_dir / "registry_first_adversarial_audit_summary.json", summary)

    return summary


def audit_digest_chain(*, source_dir: Path, digest_chain: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for section in ["pre_score_artifact_digests", "scored_artifact_digests"]:
        expected = digest_chain.get(section, {})
        if not isinstance(expected, dict):
            rows.append(audit_row("digest_chain_section_present", "FAIL", section))
            continue
        rows.append(audit_row("digest_chain_section_present", "PASS", section))
        for name, expected_digest in sorted(expected.items()):
            path = source_dir / str(name)
            actual_digest = row_digest(read_csv(path)) if path.exists() else ""
            rows.append(
                audit_row(
                    "artifact_digest_matches",
                    "PASS" if actual_digest == str(expected_digest) else "FAIL",
                    str(name),
                    expected=str(expected_digest),
                    actual=actual_digest,
                )
            )
    return rows


def audit_scored_row_digests(
    *,
    source_dir: Path,
    registry_digest: str,
    manifest_bundle_digest: str,
) -> list[dict[str, object]]:
    rows = []
    for name in SCORED_FILES_WITH_DIGESTS:
        table = read_csv(source_dir / name)
        if not table:
            rows.append(audit_row("scored_file_nonempty", "FAIL", name))
            continue
        rows.append(audit_row("scored_file_nonempty", "PASS", name))
        if any("registry_digest" in row for row in table):
            bad = [row for row in table if str(row.get("registry_digest", "")) != registry_digest]
            rows.append(
                audit_row(
                    "scored_registry_digest_consistent",
                    "PASS" if not bad else "FAIL",
                    name,
                    mismatch_count=len(bad),
                )
            )
        if any("manifest_bundle_digest" in row for row in table):
            bad = [row for row in table if str(row.get("manifest_bundle_digest", "")) != manifest_bundle_digest]
            rows.append(
                audit_row(
                    "scored_manifest_bundle_digest_consistent",
                    "PASS" if not bad else "FAIL",
                    name,
                    mismatch_count=len(bad),
                )
            )
    return rows


def audit_policy_boundaries(*, source_dir: Path) -> list[dict[str, object]]:
    rows = []
    optimized = read_csv(source_dir / "optimized_recovery_diagnostic.csv")
    optimized_bad = [
        row
        for row in optimized
        if row.get("theorem_transfer_class") != "optimized_diagnostic_only"
        or row.get("recovery_provenance_class") != "optimized_diagnostic"
    ]
    rows.append(
        audit_row(
            "optimized_rows_diagnostic_only",
            "PASS" if optimized and not optimized_bad else "FAIL",
            "optimized_recovery_diagnostic.csv",
            mismatch_count=len(optimized_bad),
        )
    )

    gaps = read_csv(source_dir / "provenance_gap_by_distinction.csv")
    optimized_promoted = [
        row
        for row in gaps
        if str(row.get("theorem_transfer_class", "")) == "optimized_diagnostic_only"
        and str(row.get("recovery_provenance_class", "")) != "optimized_diagnostic"
    ]
    rows.append(
        audit_row(
            "optimized_gap_rows_not_promoted",
            "PASS" if not optimized_promoted else "FAIL",
            "provenance_gap_by_distinction.csv",
            mismatch_count=len(optimized_promoted),
        )
    )
    return rows


def audit_cascade_evidence(*, source_dir: Path) -> list[dict[str, object]]:
    rows = []
    path_rows = read_csv(source_dir / "path_ensemble_rows.csv")
    cascade = read_csv(source_dir / "cascade_evidence_summary.csv")
    readiness = read_csv(source_dir / "theorem_transfer_readiness.csv")
    cascade_ready = any(
        row.get("readiness_axis") == "cascade_union_bound_ready"
        and row.get("status") == "ready"
        for row in readiness
    )
    rows.append(
        audit_row(
            "cascade_ready_has_path_rows",
            "PASS" if (not cascade_ready or path_rows) else "FAIL",
            "path_ensemble_rows.csv",
            path_row_count=len(path_rows),
        )
    )
    bad_summary = [
        row
        for row in cascade
        if row.get("cascade_evidence_status") not in {"path_rows_retained", "losslessly_reconstructible"}
        or str(row.get("bound_pass", "")) != "1"
    ]
    rows.append(
        audit_row(
            "cascade_summary_theorem_eligible",
            "PASS" if cascade and not bad_summary else "FAIL",
            "cascade_evidence_summary.csv",
            mismatch_count=len(bad_summary),
        )
    )
    return rows


def audit_overall_status(*, bundle: dict[str, object]) -> list[dict[str, object]]:
    overall_status = str(bundle.get("overall_status", ""))
    return [
        audit_row(
            "overall_status_not_only_evidence",
            "PASS" if overall_status != "registry_first_theorem_transfer_ready" or bundle.get("theorem_transfer_readiness") else "FAIL",
            "registry_first_formal_consumption_bundle.json",
            overall_status=overall_status,
        )
    ]


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def row_digest(rows: list[dict[str, object]]) -> str:
    normalized = [
        {str(key): str(value) for key, value in sorted(row.items())}
        for row in rows
    ]
    return stable_hash(normalized, length=24)


def audit_row(audit_id: str, status: str, artifact: str, **extra: object) -> dict[str, object]:
    return {
        "audit_id": audit_id,
        "status": status,
        "artifact": artifact,
        **extra,
    }


if __name__ == "__main__":
    main()
