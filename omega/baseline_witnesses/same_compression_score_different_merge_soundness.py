"""Same compression score, different merge soundness witness.

This exact finite witness compares two abstractions with the same simple
compression score against a declared exact merge profile. It shows that a
compact abstraction is not automatically merge-sound.

It does not claim optimal compression, identity, value, agency, Omega, or
substrate-general abstraction validity.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path("results/baseline_witnesses/20260611_same_compression_score_different_merge_soundness_v0")
WITNESS_ID = "same_compression_score_different_merge_soundness_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_ab"
FRAGMENTS = ("00", "01", "10", "11")
SOUND_ABSTRACTION = "classes_by_declared_a"
UNSOUND_ABSTRACTION = "classes_by_nuisance_b"

Assignment = dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same-compression/different-merge-soundness witness.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    abstractions = abstraction_definitions()
    fragment_rows = fragment_manifest_rows()
    exact_profile_rows = exact_profile_pair_rows()
    abstraction_rows = abstraction_manifest_rows(abstractions)
    membership_rows = abstraction_membership_rows(abstractions)
    audit_rows = merge_soundness_audit_rows(abstractions)
    compression_rows = compression_comparison_rows(abstraction_rows)
    summary = witness_summary(
        abstraction_rows=abstraction_rows,
        audit_rows=audit_rows,
        compression_rows=compression_rows,
    )

    artifacts = {
        "fragment_manifest": out_dir / "fragment_manifest.csv",
        "exact_profile_pairs": out_dir / "exact_profile_pairs.csv",
        "abstraction_manifest": out_dir / "abstraction_manifest.csv",
        "abstraction_membership": out_dir / "abstraction_membership.csv",
        "merge_soundness_audit": out_dir / "merge_soundness_audit.csv",
        "compression_comparison": out_dir / "compression_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["fragment_manifest"], fragment_rows)
    write_csv(artifacts["exact_profile_pairs"], exact_profile_rows)
    write_csv(artifacts["abstraction_manifest"], abstraction_rows)
    write_csv(artifacts["abstraction_membership"], membership_rows)
    write_csv(artifacts["merge_soundness_audit"], audit_rows)
    write_csv(artifacts["compression_comparison"], compression_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def abstraction_definitions() -> dict[str, Assignment]:
    return {
        SOUND_ABSTRACTION: {fragment: f"A{fragment[0]}" for fragment in FRAGMENTS},
        UNSOUND_ABSTRACTION: {fragment: f"B{fragment[1]}" for fragment in FRAGMENTS},
    }


def fragment_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "fragment_id": fragment,
            "declared_a": fragment[0],
            "nuisance_b": fragment[1],
        }
        for fragment in FRAGMENTS
    ]


def exact_profile_pair_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for left, right in unordered_pairs(FRAGMENTS):
        exact_allows = left[0] == right[0]
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "left_fragment": left,
                "right_fragment": right,
                "left_declared_a": left[0],
                "right_declared_a": right[0],
                "exact_allows_merge": int(exact_allows),
                "exact_blocks_merge": int(not exact_allows),
                "exact_profile_rule": "same declared_a allows merge; different declared_a blocks merge",
            }
        )
    return rows


def abstraction_manifest_rows(abstractions: dict[str, Assignment]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for abstraction_id, assignment in abstractions.items():
        class_sizes = sorted(class_size_map(assignment).values())
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "abstraction_id": abstraction_id,
                "fragment_count": len(FRAGMENTS),
                "class_count": len(set(assignment.values())),
                "assignment_count": len(assignment),
                "class_size_signature": ";".join(str(size) for size in class_sizes),
                "simple_compression_score": f"classes:{len(set(assignment.values()))};sizes:{';'.join(str(size) for size in class_sizes)}",
                "description": abstraction_description(abstraction_id),
            }
        )
    return rows


def abstraction_description(abstraction_id: str) -> str:
    if abstraction_id == SOUND_ABSTRACTION:
        return "groups fragments by declared a coordinate"
    if abstraction_id == UNSOUND_ABSTRACTION:
        return "groups fragments by nuisance b coordinate"
    raise ValueError(f"unknown abstraction_id: {abstraction_id}")


def abstraction_membership_rows(abstractions: dict[str, Assignment]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for abstraction_id, assignment in abstractions.items():
        for fragment in FRAGMENTS:
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "abstraction_id": abstraction_id,
                    "fragment_id": fragment,
                    "class_id": assignment[fragment],
                    "declared_a": fragment[0],
                    "nuisance_b": fragment[1],
                }
            )
    return rows


def merge_soundness_audit_rows(abstractions: dict[str, Assignment]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for abstraction_id, assignment in abstractions.items():
        for left, right in unordered_pairs(FRAGMENTS):
            same_class = assignment[left] == assignment[right]
            exact_allows = left[0] == right[0]
            unsound_merge = same_class and not exact_allows
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "abstraction_id": abstraction_id,
                    "left_fragment": left,
                    "right_fragment": right,
                    "left_class": assignment[left],
                    "right_class": assignment[right],
                    "same_abstraction_class": int(same_class),
                    "exact_allows_merge": int(exact_allows),
                    "exact_blocks_merge": int(not exact_allows),
                    "unsound_merge": int(unsound_merge),
                    "audit_status": "FAIL" if unsound_merge else "PASS",
                }
            )
    return rows


def compression_comparison_rows(abstraction_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    sound = row_by_abstraction(abstraction_rows, SOUND_ABSTRACTION)
    unsound = row_by_abstraction(abstraction_rows, UNSOUND_ABSTRACTION)
    metrics = [
        "fragment_count",
        "class_count",
        "assignment_count",
        "class_size_signature",
        "simple_compression_score",
    ]
    return [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "sound_value": sound[metric],
            "unsound_value": unsound[metric],
            "matched": int(sound[metric] == unsound[metric]),
        }
        for metric in metrics
    ]


def witness_summary(
    *,
    abstraction_rows: list[dict[str, object]],
    audit_rows: list[dict[str, object]],
    compression_rows: list[dict[str, object]],
) -> dict[str, object]:
    sound_audit = [row for row in audit_rows if row["abstraction_id"] == SOUND_ABSTRACTION]
    unsound_audit = [row for row in audit_rows if row["abstraction_id"] == UNSOUND_ABSTRACTION]
    compression_scores_matched = all(int(row["matched"]) == 1 for row in compression_rows)
    sound_unsound_merge_count = sum(int(row["unsound_merge"]) for row in sound_audit)
    unsound_unsound_merge_count = sum(int(row["unsound_merge"]) for row in unsound_audit)
    sound_merge_sound = sound_unsound_merge_count == 0
    unsound_merge_sound = unsound_unsound_merge_count == 0
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "fragment_count": len(FRAGMENTS),
        "abstraction_count": 2,
        "exact_profile_rule": "same declared_a allows merge; different declared_a blocks merge",
        "compression_scores_matched": compression_scores_matched,
        "sound_abstraction_id": SOUND_ABSTRACTION,
        "unsound_abstraction_id": UNSOUND_ABSTRACTION,
        "sound_abstraction_merge_sound": sound_merge_sound,
        "unsound_abstraction_merge_sound": unsound_merge_sound,
        "sound_abstraction_unsound_merge_count": sound_unsound_merge_count,
        "unsound_abstraction_unsound_merge_count": unsound_unsound_merge_count,
        "witness_status": (
            "same_compression_score_different_merge_soundness"
            if compression_scores_matched and sound_merge_sound and not unsound_merge_sound
            else "witness_failed"
        ),
        "not_claimed": [
            "optimal compression",
            "identity detection",
            "value detection",
            "agency detection",
            "Omega validation",
            "substrate-general abstraction validity",
        ],
        "abstraction_rows_digest": stable_hash(abstraction_rows, length=24),
        "audit_rows_digest": stable_hash(audit_rows, length=24),
        "compression_rows_digest": stable_hash(compression_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Compression Score, Different Merge Soundness Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baseline

```text
compression_scores_matched: {summary["compression_scores_matched"]}
fragment_count: {summary["fragment_count"]}
abstraction_count: {summary["abstraction_count"]}
```

Both abstractions have the same class count and class-size signature.

## Merge Soundness

```text
sound_abstraction_id: {summary["sound_abstraction_id"]}
unsound_abstraction_id: {summary["unsound_abstraction_id"]}
sound_abstraction_merge_sound: {summary["sound_abstraction_merge_sound"]}
unsound_abstraction_merge_sound: {summary["unsound_abstraction_merge_sound"]}
unsound_abstraction_unsound_merge_count: {summary["unsound_abstraction_unsound_merge_count"]}
```

## Read

Same compression score does not determine merge soundness against an exact
consequence profile.

## Not Claimed

```text
optimal compression
identity detection
value detection
agency detection
Omega validation
substrate-general abstraction validity
```
"""


def unordered_pairs(items: tuple[str, ...]) -> list[tuple[str, str]]:
    return list(combinations(items, 2))


def class_size_map(assignment: Assignment) -> dict[str, int]:
    sizes: dict[str, int] = {}
    for class_id in assignment.values():
        sizes[class_id] = sizes.get(class_id, 0) + 1
    return sizes


def row_by_abstraction(rows: list[dict[str, object]], abstraction_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["abstraction_id"] == abstraction_id]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {abstraction_id}, found {len(matches)}")
    return matches[0]


if __name__ == "__main__":
    main()
