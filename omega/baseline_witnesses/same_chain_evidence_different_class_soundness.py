"""Same chain evidence, different class soundness witness.

This exact finite witness compares two proposed classes that both pass the
same declared adjacent-chain checks. One class is a full compatible clique; the
other is only chain-connected and contains a blocked endpoint pair.

It does not claim identity, transitivity, value, agency, Omega, or
substrate-general class validity.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path("results/baseline_witnesses/20260611_same_chain_evidence_different_class_soundness_v0")
WITNESS_ID = "same_chain_evidence_different_class_soundness_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "chain_vs_clique_triples"
VALID_CLASS = "valid_triangle_class"
INVALID_CLASS = "invalid_chain_class"

CLASS_MEMBERS: dict[str, tuple[str, ...]] = {
    VALID_CLASS: ("v0", "v1", "v2"),
    INVALID_CLASS: ("i0", "i1", "i2"),
}

DECLARED_CHAIN_EDGES: dict[str, tuple[tuple[str, str], ...]] = {
    VALID_CLASS: (("v0", "v1"), ("v1", "v2")),
    INVALID_CLASS: (("i0", "i1"), ("i1", "i2")),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same-chain/different-class-soundness witness.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    fragment_rows = fragment_manifest_rows()
    profile_rows = exact_profile_pair_rows()
    class_rows = class_manifest_rows()
    chain_rows = declared_chain_edge_rows()
    soundness_rows = class_soundness_audit_rows()
    comparison_rows = baseline_comparison_rows(class_rows)
    summary = witness_summary(
        chain_rows=chain_rows,
        soundness_rows=soundness_rows,
        comparison_rows=comparison_rows,
    )

    artifacts = {
        "fragment_manifest": out_dir / "fragment_manifest.csv",
        "exact_profile_pairs": out_dir / "exact_profile_pairs.csv",
        "class_manifest": out_dir / "class_manifest.csv",
        "declared_chain_edges": out_dir / "declared_chain_edges.csv",
        "class_soundness_audit": out_dir / "class_soundness_audit.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["fragment_manifest"], fragment_rows)
    write_csv(artifacts["exact_profile_pairs"], profile_rows)
    write_csv(artifacts["class_manifest"], class_rows)
    write_csv(artifacts["declared_chain_edges"], chain_rows)
    write_csv(artifacts["class_soundness_audit"], soundness_rows)
    write_csv(artifacts["baseline_comparison"], comparison_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def fragment_manifest_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for class_id, members in CLASS_MEMBERS.items():
        for position, fragment in enumerate(members):
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "fragment_id": fragment,
                    "proposed_class_id": class_id,
                    "chain_position": position,
                }
            )
    return rows


def exact_profile_pair_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for left, right in unordered_pairs(all_fragments()):
        allows = exact_allows_merge(left, right)
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "left_fragment": left,
                "right_fragment": right,
                "left_class": class_of(left),
                "right_class": class_of(right),
                "exact_allows_merge": int(allows),
                "exact_blocks_merge": int(not allows),
                "exact_profile_rule": exact_profile_rule(),
            }
        )
    return rows


def class_manifest_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for class_id, members in CLASS_MEMBERS.items():
        chain_edges = DECLARED_CHAIN_EDGES[class_id]
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "proposed_class_id": class_id,
                "class_role": class_role(class_id),
                "member_count": len(members),
                "member_signature": ";".join(members),
                "declared_chain_edge_count": len(chain_edges),
                "declared_chain_edge_signature": ";".join(
                    f"{left}-{right}" for left, right in chain_edges
                ),
                "internal_pair_count": len(unordered_pairs(members)),
                "chain_connected": 1,
            }
        )
    return rows


def declared_chain_edge_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for class_id, chain_edges in DECLARED_CHAIN_EDGES.items():
        for left, right in chain_edges:
            allows = exact_allows_merge(left, right)
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "proposed_class_id": class_id,
                    "left_fragment": left,
                    "right_fragment": right,
                    "exact_allows_merge": int(allows),
                    "chain_edge_status": "PASS" if allows else "FAIL",
                }
            )
    return rows


def class_soundness_audit_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for class_id, members in CLASS_MEMBERS.items():
        for left, right in unordered_pairs(members):
            allows = exact_allows_merge(left, right)
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "proposed_class_id": class_id,
                    "left_fragment": left,
                    "right_fragment": right,
                    "exact_allows_merge": int(allows),
                    "exact_blocks_merge": int(not allows),
                    "class_soundness_status": "PASS" if allows else "FAIL",
                }
            )
    return rows


def baseline_comparison_rows(class_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    valid = row_by_class(class_rows, VALID_CLASS)
    invalid = row_by_class(class_rows, INVALID_CLASS)
    metrics = [
        "member_count",
        "declared_chain_edge_count",
        "internal_pair_count",
        "chain_connected",
    ]
    return [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "valid_class_value": valid[metric],
            "invalid_class_value": invalid[metric],
            "matched": int(valid[metric] == invalid[metric]),
        }
        for metric in metrics
    ]


def witness_summary(
    *,
    chain_rows: list[dict[str, object]],
    soundness_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
) -> dict[str, object]:
    chain_by_class = rows_by_class(chain_rows)
    soundness_by_class = rows_by_class(soundness_rows)
    baseline_controls_matched = all(int(row["matched"]) == 1 for row in comparison_rows)
    valid_chain_pass = all(row["chain_edge_status"] == "PASS" for row in chain_by_class[VALID_CLASS])
    invalid_chain_pass = all(row["chain_edge_status"] == "PASS" for row in chain_by_class[INVALID_CLASS])
    valid_unsound_pairs = [
        row for row in soundness_by_class[VALID_CLASS]
        if row["class_soundness_status"] == "FAIL"
    ]
    invalid_unsound_pairs = [
        row for row in soundness_by_class[INVALID_CLASS]
        if row["class_soundness_status"] == "FAIL"
    ]
    valid_class_sound = not valid_unsound_pairs
    invalid_class_sound = not invalid_unsound_pairs
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "proposed_class_count": len(CLASS_MEMBERS),
        "fragment_count": len(all_fragments()),
        "valid_class_id": VALID_CLASS,
        "invalid_class_id": INVALID_CLASS,
        "exact_profile_rule": exact_profile_rule(),
        "baseline_controls_matched": baseline_controls_matched,
        "valid_class_declared_chain_edges_pass": valid_chain_pass,
        "invalid_class_declared_chain_edges_pass": invalid_chain_pass,
        "valid_class_sound": valid_class_sound,
        "invalid_class_sound": invalid_class_sound,
        "valid_class_unsound_pair_count": len(valid_unsound_pairs),
        "invalid_class_unsound_pair_count": len(invalid_unsound_pairs),
        "witness_status": (
            "same_chain_evidence_different_class_soundness"
            if (
                baseline_controls_matched
                and valid_chain_pass
                and invalid_chain_pass
                and valid_class_sound
                and not invalid_class_sound
            )
            else "witness_failed"
        ),
        "not_claimed": [
            "transitivity",
            "identity detection",
            "cluster validity",
            "value detection",
            "agency detection",
            "Omega validation",
            "substrate-general class validity",
        ],
        "chain_rows_digest": stable_hash(chain_rows, length=24),
        "soundness_rows_digest": stable_hash(soundness_rows, length=24),
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Chain Evidence, Different Class Soundness Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baseline

```text
baseline_controls_matched: {summary["baseline_controls_matched"]}
proposed_class_count: {summary["proposed_class_count"]}
fragment_count: {summary["fragment_count"]}
```

Both proposed classes have the same member count, the same declared adjacent
chain-edge count, the same internal-pair count, and a declared connected chain.

## Class Soundness

```text
valid_class_id: {summary["valid_class_id"]}
invalid_class_id: {summary["invalid_class_id"]}
valid_class_declared_chain_edges_pass: {summary["valid_class_declared_chain_edges_pass"]}
invalid_class_declared_chain_edges_pass: {summary["invalid_class_declared_chain_edges_pass"]}
valid_class_sound: {summary["valid_class_sound"]}
invalid_class_sound: {summary["invalid_class_sound"]}
invalid_class_unsound_pair_count: {summary["invalid_class_unsound_pair_count"]}
```

## Read

Declared chain evidence does not determine full class soundness against an
exact merge profile. Connectedness is not a substitute for pairwise
consequence compatibility.

## Not Claimed

```text
transitivity
identity detection
cluster validity
value detection
agency detection
Omega validation
substrate-general class validity
```
"""


def exact_allows_merge(left: str, right: str) -> bool:
    if class_of(left) == VALID_CLASS and class_of(right) == VALID_CLASS:
        return True
    if class_of(left) == INVALID_CLASS and class_of(right) == INVALID_CLASS:
        return {left, right} != {"i0", "i2"}
    return False


def exact_profile_rule() -> str:
    return (
        "valid triangle allows all internal pairs; invalid chain allows only "
        "adjacent chain pairs and blocks its endpoint pair"
    )


def class_role(class_id: str) -> str:
    if class_id == VALID_CLASS:
        return "full_pairwise_compatible_control"
    if class_id == INVALID_CLASS:
        return "chain_connected_unsound_class"
    raise ValueError(f"unknown class_id: {class_id}")


def class_of(fragment: str) -> str:
    for class_id, members in CLASS_MEMBERS.items():
        if fragment in members:
            return class_id
    raise ValueError(f"unknown fragment: {fragment}")


def all_fragments() -> tuple[str, ...]:
    return tuple(fragment for members in CLASS_MEMBERS.values() for fragment in members)


def unordered_pairs(items: tuple[str, ...]) -> list[tuple[str, str]]:
    return list(combinations(items, 2))


def row_by_class(rows: list[dict[str, object]], class_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["proposed_class_id"] == class_id]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {class_id}, found {len(matches)}")
    return matches[0]


def rows_by_class(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {class_id: [] for class_id in CLASS_MEMBERS}
    for row in rows:
        grouped[str(row["proposed_class_id"])].append(row)
    return grouped


if __name__ == "__main__":
    main()
