"""Same frontier morphology, different declared loss profile witness.

This exact finite witness controls coarse frontier morphology summaries while
changing the declared horizon-local loss profile for currently viable sources.
It does not claim real-world viability, real irreversibility, value, agency,
identity, Omega, or substrate-general theory validation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path("results/baseline_witnesses/20260611_same_frontier_morphology_different_loss_profile_v0")
WITNESS_ID = "same_frontier_morphology_different_loss_profile_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_vn"
STATES = ("00", "01", "10", "11")
PRESERVE_V_CHANNEL = "preserve_declared_v"
FLIP_V_CHANNEL = "flip_declared_v"

Channel = dict[str, tuple[str, ...]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same-frontier-morphology/different-loss-profile witness.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    channels = channel_definitions()
    state_rows = state_manifest_rows()
    channel_rows = channel_manifest_rows()
    support_rows = support_edge_rows(channels)
    morphology_rows = frontier_morphology_rows(channels)
    loss_rows = loss_profile_rows(channels)
    comparison_rows = baseline_comparison_rows(morphology_rows, loss_rows)
    summary = witness_summary(
        morphology_rows=morphology_rows,
        loss_rows=loss_rows,
        comparison_rows=comparison_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "channel_manifest": out_dir / "channel_manifest.csv",
        "support_edges": out_dir / "support_edges.csv",
        "frontier_morphology_by_channel": out_dir / "frontier_morphology_by_channel.csv",
        "loss_profile_by_source": out_dir / "loss_profile_by_source.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["channel_manifest"], channel_rows)
    write_csv(artifacts["support_edges"], support_rows)
    write_csv(artifacts["frontier_morphology_by_channel"], morphology_rows)
    write_csv(artifacts["loss_profile_by_source"], loss_rows)
    write_csv(artifacts["baseline_comparison"], comparison_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def channel_definitions() -> dict[str, Channel]:
    return {
        PRESERVE_V_CHANNEL: {
            source: tuple(target for target in STATES if target[0] == source[0])
            for source in STATES
        },
        FLIP_V_CHANNEL: {
            source: tuple(target for target in STATES if target[0] != source[0])
            for source in STATES
        },
    }


def state_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "state_id": state,
            "declared_v": state[0],
            "nuisance_n": state[1],
            "declared_viable": int(is_viable(state)),
        }
        for state in STATES
    ]


def channel_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "channel_id": PRESERVE_V_CHANNEL,
            "channel_role": "loss_profile_negative",
            "description": "preserves declared viability bit over the one-step frontier",
        },
        {
            "channel_id": FLIP_V_CHANNEL,
            "channel_role": "loss_profile_positive",
            "description": "flips declared viability bit over the one-step frontier",
        },
    ]


def support_edge_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        for source in STATES:
            support = channel[source]
            for target in support:
                rows.append(
                    {
                        "witness_id": WITNESS_ID,
                        "carrier_id": CARRIER_ID,
                        "channel_id": channel_id,
                        "source_state": source,
                        "target_state": target,
                        "source_declared_viable": int(is_viable(source)),
                        "target_declared_viable": int(is_viable(target)),
                        "edge_weight": 1,
                        "edge_probability": f"1/{len(support)}",
                        "per_source_support_count": len(support),
                    }
                )
    return rows


def frontier_morphology_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        support_counts = {source: len(channel[source]) for source in STATES}
        entropies = {source: uniform_entropy_bits(len(channel[source])) for source in STATES}
        viable_target_counts = {source: sum(int(is_viable(target)) for target in channel[source]) for source in STATES}
        global_target_weights = target_weights(channel)
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "source_count": len(STATES),
                "edge_count": sum(support_counts.values()),
                "global_target_support_size": len(global_target_weights),
                "global_target_support": ";".join(sorted(global_target_weights)),
                "global_target_weight_signature": signature(global_target_weights),
                "global_target_entropy_bits": f"{entropy_from_weights(global_target_weights.values()):.6f}",
                "per_source_support_count_signature": signature(support_counts),
                "per_source_entropy_bits_signature": float_signature(entropies),
                "viable_target_count_multiset": multiset_signature(viable_target_counts.values()),
                "frontier_morphology_signature": (
                    f"support:{signature(support_counts)}|"
                    f"entropy:{float_signature(entropies)}|"
                    f"viable_target_multiset:{multiset_signature(viable_target_counts.values())}"
                ),
            }
        )
    return rows


def loss_profile_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        for source in STATES:
            source_viable = is_viable(source)
            viable_targets = [target for target in channel[source] if is_viable(target)]
            loss = source_viable and not viable_targets
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "channel_id": channel_id,
                    "source_state": source,
                    "source_declared_viable": int(source_viable),
                    "target_support": ";".join(channel[source]),
                    "viable_target_count": len(viable_targets),
                    "declared_horizon_loss": int(loss),
                    "loss_rule": "source viable and no viable target in declared one-step support",
                }
            )
    return rows


def baseline_comparison_rows(
    morphology_rows: list[dict[str, object]],
    loss_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    left_morphology = row_by_channel(morphology_rows, PRESERVE_V_CHANNEL)
    right_morphology = row_by_channel(morphology_rows, FLIP_V_CHANNEL)
    matched_metrics = [
        "source_count",
        "edge_count",
        "global_target_support_size",
        "global_target_support",
        "global_target_weight_signature",
        "global_target_entropy_bits",
        "per_source_support_count_signature",
        "per_source_entropy_bits_signature",
        "viable_target_count_multiset",
        "frontier_morphology_signature",
    ]
    rows = [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "preserve_value": left_morphology[metric],
            "flip_value": right_morphology[metric],
            "expected_relation": "matched",
            "relation_holds": int(left_morphology[metric] == right_morphology[metric]),
        }
        for metric in matched_metrics
    ]
    preserve_loss_signature = loss_signature(loss_rows, PRESERVE_V_CHANNEL)
    flip_loss_signature = loss_signature(loss_rows, FLIP_V_CHANNEL)
    rows.append(
        {
            "witness_id": WITNESS_ID,
            "metric": "declared_horizon_loss_signature",
            "preserve_value": preserve_loss_signature,
            "flip_value": flip_loss_signature,
            "expected_relation": "different",
            "relation_holds": int(preserve_loss_signature != flip_loss_signature),
        }
    )
    return rows


def witness_summary(
    *,
    morphology_rows: list[dict[str, object]],
    loss_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
) -> dict[str, object]:
    morphology_controls_hold = all(
        int(row["relation_holds"]) == 1
        for row in comparison_rows
        if row["expected_relation"] == "matched"
    )
    loss_profile_differs = loss_signature(loss_rows, PRESERVE_V_CHANNEL) != loss_signature(loss_rows, FLIP_V_CHANNEL)
    all_expected_relations_hold = all(int(row["relation_holds"]) == 1 for row in comparison_rows)
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "source_count": len(STATES),
        "channel_count": 2,
        "declared_viability_predicate": "state first bit v = 1",
        "loss_rule": "source viable and no viable target in declared one-step support",
        "morphology_controls_hold": morphology_controls_hold,
        "loss_profile_differs": loss_profile_differs,
        "all_expected_relations_hold": all_expected_relations_hold,
        "preserve_loss_signature": loss_signature(loss_rows, PRESERVE_V_CHANNEL),
        "flip_loss_signature": loss_signature(loss_rows, FLIP_V_CHANNEL),
        "preserve_loss_count": loss_count(loss_rows, PRESERVE_V_CHANNEL),
        "flip_loss_count": loss_count(loss_rows, FLIP_V_CHANNEL),
        "witness_status": (
            "same_frontier_morphology_different_declared_loss_profile"
            if morphology_controls_hold and loss_profile_differs and all_expected_relations_hold
            else "witness_failed"
        ),
        "not_claimed": [
            "real-world viability",
            "real irreversibility",
            "value detection",
            "valuer detection",
            "agency detection",
            "identity detection",
            "Omega validation",
            "substrate-general theory validation",
        ],
        "morphology_rows_digest": stable_hash(morphology_rows, length=24),
        "loss_rows_digest": stable_hash(loss_rows, length=24),
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Frontier Morphology, Different Declared Loss Profile Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baseline

```text
morphology_controls_hold: {summary["morphology_controls_hold"]}
all_expected_relations_hold: {summary["all_expected_relations_hold"]}
```

The two channels match coarse one-step frontier morphology summaries, including
support count, global target support, entropy, and viable-target-count multiset.

## Declared Loss Profile

```text
declared_viability_predicate: {summary["declared_viability_predicate"]}
loss_rule: {summary["loss_rule"]}
preserve_loss_signature: {summary["preserve_loss_signature"]}
flip_loss_signature: {summary["flip_loss_signature"]}
preserve_loss_count: {summary["preserve_loss_count"]}
flip_loss_count: {summary["flip_loss_count"]}
```

## Read

Matched frontier morphology summaries do not determine the declared
horizon-local loss profile.

## Not Claimed

```text
real-world viability
real irreversibility
value detection
valuer detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
"""


def is_viable(state: str) -> bool:
    return state[0] == "1"


def target_weights(channel: Channel) -> dict[str, int]:
    weights: dict[str, int] = {}
    for support in channel.values():
        for target in support:
            weights[target] = weights.get(target, 0) + 1
    return weights


def uniform_entropy_bits(support_size: int) -> float:
    if support_size <= 0:
        return 0.0
    return math.log2(support_size)


def entropy_from_weights(weights: object) -> float:
    values = list(weights)
    total = sum(values)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for weight in values:
        probability = weight / total
        entropy -= probability * math.log2(probability)
    return entropy


def loss_signature(loss_rows: list[dict[str, object]], channel_id: str) -> str:
    rows = [row for row in loss_rows if row["channel_id"] == channel_id and int(row["source_declared_viable"]) == 1]
    return ";".join(f"{row['source_state']}:{row['declared_horizon_loss']}" for row in sorted(rows, key=lambda item: str(item["source_state"])))


def loss_count(loss_rows: list[dict[str, object]], channel_id: str) -> int:
    return sum(
        int(row["declared_horizon_loss"])
        for row in loss_rows
        if row["channel_id"] == channel_id and int(row["source_declared_viable"]) == 1
    )


def row_by_channel(rows: list[dict[str, object]], channel_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["channel_id"] == channel_id]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {channel_id}, found {len(matches)}")
    return matches[0]


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))


def multiset_signature(values: object) -> str:
    return ";".join(str(value) for value in sorted(values))


if __name__ == "__main__":
    main()
