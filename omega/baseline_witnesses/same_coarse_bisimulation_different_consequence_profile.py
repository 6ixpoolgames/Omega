"""Same coarse bisimulation, different consequence profile witness.

This exact finite witness compares two declared expanded panels over the same
four-state transition system. Under the coarse observation panel, both views
share the same one-block bisimulation-style partition. Under the declared
expanded panels, the exact merge profiles differ.

It does not claim arbitrary post-hoc panel validity, identity, value, agency,
Omega, or substrate-general bisimulation novelty.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path("results/baseline_witnesses/20260611_same_coarse_bisimulation_different_consequence_profile_v0")
WITNESS_ID = "same_coarse_bisimulation_different_consequence_profile_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_dn_identity_transition"
COARSE_PANEL = "coarse_unit_observation"
D_PANEL = "declared_d_expanded_panel"
N_PANEL = "declared_n_expanded_panel"
STATES = ("00", "01", "10", "11")
EXPANDED_PANELS = (D_PANEL, N_PANEL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same-coarse-bisimulation/different-profile witness.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    state_rows = state_manifest_rows()
    panel_rows = panel_manifest_rows()
    transition_rows = transition_edge_rows()
    coarse_rows = coarse_partition_rows()
    profile_rows = exact_profile_pair_rows()
    baseline_rows = baseline_comparison_rows()
    profile_difference_rows = expanded_profile_difference_rows(profile_rows)
    summary = witness_summary(
        baseline_rows=baseline_rows,
        profile_rows=profile_rows,
        profile_difference_rows=profile_difference_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "panel_manifest": out_dir / "panel_manifest.csv",
        "transition_edges": out_dir / "transition_edges.csv",
        "coarse_partition": out_dir / "coarse_partition.csv",
        "exact_profile_pairs": out_dir / "exact_profile_pairs.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "profile_difference": out_dir / "profile_difference.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["panel_manifest"], panel_rows)
    write_csv(artifacts["transition_edges"], transition_rows)
    write_csv(artifacts["coarse_partition"], coarse_rows)
    write_csv(artifacts["exact_profile_pairs"], profile_rows)
    write_csv(artifacts["baseline_comparison"], baseline_rows)
    write_csv(artifacts["profile_difference"], profile_difference_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def state_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "state_id": state,
            "d": state[0],
            "n": state[1],
        }
        for state in STATES
    ]


def panel_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "panel_id": COARSE_PANEL,
            "panel_role": "coarse_baseline",
            "observation_rule": "all states emit unit observation",
            "declared_before_scoring": 1,
        },
        {
            "witness_id": WITNESS_ID,
            "panel_id": D_PANEL,
            "panel_role": "expanded_profile",
            "observation_rule": "compare declared d coordinate",
            "declared_before_scoring": 1,
        },
        {
            "witness_id": WITNESS_ID,
            "panel_id": N_PANEL,
            "panel_role": "expanded_profile",
            "observation_rule": "compare declared n coordinate",
            "declared_before_scoring": 1,
        },
    ]


def transition_edge_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "source_state": state,
            "target_state": state,
            "transition_rule": "identity_self_loop",
            "coarse_source_observation": "unit",
            "coarse_target_observation": "unit",
        }
        for state in STATES
    ]


def coarse_partition_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "expanded_panel_id": panel,
            "coarse_panel_id": COARSE_PANEL,
            "coarse_partition_id": "unit_block",
            "coarse_block_id": "coarse_all_states",
            "coarse_block_members": ";".join(STATES),
            "coarse_block_count": 1,
            "coarse_block_size_signature": str(len(STATES)),
            "coarse_partition_signature": f"coarse_all_states:{';'.join(STATES)}",
        }
        for panel in EXPANDED_PANELS
    ]


def exact_profile_pair_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for panel in EXPANDED_PANELS:
        for left, right in unordered_pairs(STATES):
            allows = exact_allows_merge(panel, left, right)
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "expanded_panel_id": panel,
                    "left_state": left,
                    "right_state": right,
                    "left_d": left[0],
                    "right_d": right[0],
                    "left_n": left[1],
                    "right_n": right[1],
                    "exact_allows_merge": int(allows),
                    "exact_blocks_merge": int(not allows),
                    "exact_profile_rule": exact_profile_rule(panel),
                }
            )
    return rows


def baseline_comparison_rows() -> list[dict[str, object]]:
    d_metrics = baseline_metrics_for_panel(D_PANEL)
    n_metrics = baseline_metrics_for_panel(N_PANEL)
    return [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "declared_d_panel_value": d_metrics[metric],
            "declared_n_panel_value": n_metrics[metric],
            "matched": int(d_metrics[metric] == n_metrics[metric]),
        }
        for metric in sorted(d_metrics)
    ]


def expanded_profile_difference_rows(profile_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    d_signature = profile_signature(profile_rows, D_PANEL)
    n_signature = profile_signature(profile_rows, N_PANEL)
    return [
        {
            "witness_id": WITNESS_ID,
            "signature_kind": "allowed_pair_signature",
            "declared_d_panel_signature": d_signature["allowed_pair_signature"],
            "declared_n_panel_signature": n_signature["allowed_pair_signature"],
            "matched": int(d_signature["allowed_pair_signature"] == n_signature["allowed_pair_signature"]),
        },
        {
            "witness_id": WITNESS_ID,
            "signature_kind": "blocked_pair_signature",
            "declared_d_panel_signature": d_signature["blocked_pair_signature"],
            "declared_n_panel_signature": n_signature["blocked_pair_signature"],
            "matched": int(d_signature["blocked_pair_signature"] == n_signature["blocked_pair_signature"]),
        },
    ]


def witness_summary(
    *,
    baseline_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    profile_difference_rows: list[dict[str, object]],
) -> dict[str, object]:
    baseline_controls_matched = all(int(row["matched"]) == 1 for row in baseline_rows)
    signatures_differ = all(int(row["matched"]) == 0 for row in profile_difference_rows)
    d_signature = profile_signature(profile_rows, D_PANEL)
    n_signature = profile_signature(profile_rows, N_PANEL)
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "state_count": len(STATES),
        "transition_edge_count": len(STATES),
        "coarse_panel_id": COARSE_PANEL,
        "declared_d_panel_id": D_PANEL,
        "declared_n_panel_id": N_PANEL,
        "coarse_partition_signature": f"coarse_all_states:{';'.join(STATES)}",
        "baseline_controls_matched": baseline_controls_matched,
        "expanded_profile_counts_matched": expanded_profile_counts_matched(profile_rows),
        "expanded_profile_signatures_differ": signatures_differ,
        "declared_d_allowed_pair_signature": d_signature["allowed_pair_signature"],
        "declared_n_allowed_pair_signature": n_signature["allowed_pair_signature"],
        "declared_d_blocked_pair_signature": d_signature["blocked_pair_signature"],
        "declared_n_blocked_pair_signature": n_signature["blocked_pair_signature"],
        "witness_status": (
            "same_coarse_bisimulation_different_consequence_profile"
            if (
                baseline_controls_matched
                and expanded_profile_counts_matched(profile_rows)
                and signatures_differ
            )
            else "witness_failed"
        ),
        "not_claimed": [
            "arbitrary post-hoc panel validity",
            "global identity",
            "bisimulation novelty",
            "value detection",
            "agency detection",
            "Omega validation",
            "substrate-general panel validity",
        ],
        "baseline_rows_digest": stable_hash(baseline_rows, length=24),
        "profile_rows_digest": stable_hash(profile_rows, length=24),
        "profile_difference_rows_digest": stable_hash(profile_difference_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Coarse Bisimulation, Different Consequence Profile Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baseline

```text
state_count: {summary["state_count"]}
transition_edge_count: {summary["transition_edge_count"]}
coarse_panel_id: {summary["coarse_panel_id"]}
coarse_partition_signature: {summary["coarse_partition_signature"]}
baseline_controls_matched: {summary["baseline_controls_matched"]}
expanded_profile_counts_matched: {summary["expanded_profile_counts_matched"]}
```

Both expanded panels share the same transition system and the same one-block
coarse observation partition.

## Expanded Profiles

```text
declared_d_panel_id: {summary["declared_d_panel_id"]}
declared_n_panel_id: {summary["declared_n_panel_id"]}
expanded_profile_signatures_differ: {summary["expanded_profile_signatures_differ"]}
declared_d_allowed_pair_signature: {summary["declared_d_allowed_pair_signature"]}
declared_n_allowed_pair_signature: {summary["declared_n_allowed_pair_signature"]}
declared_d_blocked_pair_signature: {summary["declared_d_blocked_pair_signature"]}
declared_n_blocked_pair_signature: {summary["declared_n_blocked_pair_signature"]}
```

## Read

The same coarse bisimulation-style partition does not determine the exact
consequence profile under a declared expanded panel.

## Not Claimed

```text
arbitrary post-hoc panel validity
global identity
bisimulation novelty
value detection
agency detection
Omega validation
substrate-general panel validity
```
"""


def baseline_metrics_for_panel(panel: str) -> dict[str, object]:
    signature = profile_signature(exact_profile_pair_rows(), panel)
    return {
        "state_count": len(STATES),
        "transition_edge_count": len(STATES),
        "coarse_block_count": 1,
        "coarse_block_size_signature": str(len(STATES)),
        "coarse_partition_signature": f"coarse_all_states:{';'.join(STATES)}",
        "expanded_pair_count": signature["pair_count"],
        "expanded_allowed_pair_count": signature["allowed_pair_count"],
        "expanded_blocked_pair_count": signature["blocked_pair_count"],
    }


def profile_signature(rows: list[dict[str, object]], panel: str) -> dict[str, object]:
    panel_rows = [row for row in rows if row["expanded_panel_id"] == panel]
    allowed_pairs = [
        f"{row['left_state']},{row['right_state']}"
        for row in panel_rows
        if int(row["exact_allows_merge"]) == 1
    ]
    blocked_pairs = [
        f"{row['left_state']},{row['right_state']}"
        for row in panel_rows
        if int(row["exact_blocks_merge"]) == 1
    ]
    return {
        "pair_count": len(panel_rows),
        "allowed_pair_count": len(allowed_pairs),
        "blocked_pair_count": len(blocked_pairs),
        "allowed_pair_signature": ";".join(allowed_pairs),
        "blocked_pair_signature": ";".join(blocked_pairs),
    }


def expanded_profile_counts_matched(profile_rows: list[dict[str, object]]) -> bool:
    d_signature = profile_signature(profile_rows, D_PANEL)
    n_signature = profile_signature(profile_rows, N_PANEL)
    return (
        d_signature["pair_count"] == n_signature["pair_count"]
        and d_signature["allowed_pair_count"] == n_signature["allowed_pair_count"]
        and d_signature["blocked_pair_count"] == n_signature["blocked_pair_count"]
    )


def exact_allows_merge(panel: str, left: str, right: str) -> bool:
    if panel == D_PANEL:
        return left[0] == right[0]
    if panel == N_PANEL:
        return left[1] == right[1]
    raise ValueError(f"unknown expanded panel: {panel}")


def exact_profile_rule(panel: str) -> str:
    if panel == D_PANEL:
        return "same declared d allows merge; different declared d blocks merge"
    if panel == N_PANEL:
        return "same declared n allows merge; different declared n blocks merge"
    raise ValueError(f"unknown expanded panel: {panel}")


def unordered_pairs(items: tuple[str, ...]) -> list[tuple[str, str]]:
    return list(combinations(items, 2))


if __name__ == "__main__":
    main()
