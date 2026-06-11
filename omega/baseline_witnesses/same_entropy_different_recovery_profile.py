"""Same entropy, different declared recovery profile witness.

This exact finite witness controls entropy-style summaries while changing which
declared distinction is recoverable. It does not claim semantic recovery,
identity, value, agency, Omega, or substrate-general theory validation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path("results/baseline_witnesses/20260611_same_entropy_different_recovery_profile_v0")
WITNESS_ID = "same_entropy_different_recovery_profile_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_ab"
STATES = ("00", "01", "10", "11")
PRESERVE_A_CHANNEL = "preserve_a_scramble_b"
PRESERVE_B_CHANNEL = "preserve_b_scramble_a"
DISTINCTIONS = ("D_A", "D_B")

Channel = dict[str, tuple[str, ...]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same-entropy/different-recovery-profile witness.")
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
    entropy_rows = entropy_baseline_rows(channels)
    recovery_rows = declared_recovery_rows(channels)
    profile_rows = recovery_profile_rows(recovery_rows)
    comparison_rows = baseline_comparison_rows(entropy_rows, profile_rows)
    summary = witness_summary(
        entropy_rows=entropy_rows,
        profile_rows=profile_rows,
        comparison_rows=comparison_rows,
        recovery_rows=recovery_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "channel_manifest": out_dir / "channel_manifest.csv",
        "support_edges": out_dir / "support_edges.csv",
        "entropy_baseline_by_channel": out_dir / "entropy_baseline_by_channel.csv",
        "declared_recovery_by_distinction": out_dir / "declared_recovery_by_distinction.csv",
        "recovery_profile_by_channel": out_dir / "recovery_profile_by_channel.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["channel_manifest"], channel_rows)
    write_csv(artifacts["support_edges"], support_rows)
    write_csv(artifacts["entropy_baseline_by_channel"], entropy_rows)
    write_csv(artifacts["declared_recovery_by_distinction"], recovery_rows)
    write_csv(artifacts["recovery_profile_by_channel"], profile_rows)
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
        PRESERVE_A_CHANNEL: {
            source: tuple(target for target in STATES if target[0] == source[0])
            for source in STATES
        },
        PRESERVE_B_CHANNEL: {
            source: tuple(target for target in STATES if target[1] == source[1])
            for source in STATES
        },
    }


def state_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "state_id": state,
            "a": state[0],
            "b": state[1],
        }
        for state in STATES
    ]


def channel_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "channel_id": PRESERVE_A_CHANNEL,
            "channel_role": "entropy_matched_A_profile",
            "description": "preserves declared A while scrambling B",
        },
        {
            "channel_id": PRESERVE_B_CHANNEL,
            "channel_role": "entropy_matched_B_profile",
            "description": "preserves declared B while scrambling A",
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
                        "source_a": source[0],
                        "source_b": source[1],
                        "target_a": target[0],
                        "target_b": target[1],
                        "edge_weight": 1,
                        "edge_probability": f"1/{len(support)}",
                        "per_source_support_count": len(support),
                    }
                )
    return rows


def entropy_baseline_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        support_counts = {source: len(channel[source]) for source in STATES}
        per_source_entropy = {source: uniform_entropy_bits(len(channel[source])) for source in STATES}
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
                "per_source_entropy_bits_signature": float_signature(per_source_entropy),
                "min_per_source_entropy_bits": f"{min(per_source_entropy.values()):.6f}",
                "max_per_source_entropy_bits": f"{max(per_source_entropy.values()):.6f}",
            }
        )
    return rows


def declared_recovery_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        for distinction_id in DISTINCTIONS:
            recovery = recovery_for_distinction(channel, distinction_id)
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "channel_id": channel_id,
                    "source_distinction_id": distinction_id,
                    "target_observation_id": observation_for_distinction(distinction_id),
                    "declared_contract": "matching target coordinate must recover matching source coordinate over support",
                    "exact_declared_recovery": int(recovery["exact_declared_recovery"]),
                    "ambiguous_target_observations": recovery["ambiguous_target_observations"],
                    "observation_to_source_labels": recovery["observation_to_source_labels"],
                    "recovery_status": (
                        "declared_recovery_pass"
                        if recovery["exact_declared_recovery"]
                        else "declared_recovery_fail"
                    ),
                }
            )
    return rows


def recovery_for_distinction(channel: Channel, distinction_id: str) -> dict[str, object]:
    coordinate = coordinate_for_distinction(distinction_id)
    observation_sources: dict[str, set[str]] = {}
    for source in STATES:
        source_label = source[coordinate]
        for target in channel[source]:
            target_observation = target[coordinate]
            observation_sources.setdefault(target_observation, set()).add(source_label)

    ambiguous = {
        observation: sorted(labels)
        for observation, labels in observation_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_target_observations": ";".join(
            f"{observation}->{{{','.join(labels)}}}" for observation, labels in sorted(ambiguous.items())
        ),
        "observation_to_source_labels": ";".join(
            f"{observation}->{{{','.join(sorted(labels))}}}"
            for observation, labels in sorted(observation_sources.items())
        ),
    }


def recovery_profile_rows(recovery_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id in (PRESERVE_A_CHANNEL, PRESERVE_B_CHANNEL):
        channel_rows = [row for row in recovery_rows if row["channel_id"] == channel_id]
        recovered = sorted(
            str(row["source_distinction_id"])
            for row in channel_rows
            if int(row["exact_declared_recovery"]) == 1
        )
        failed = sorted(
            str(row["source_distinction_id"])
            for row in channel_rows
            if int(row["exact_declared_recovery"]) == 0
        )
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "declared_distinction_panel": ";".join(DISTINCTIONS),
                "recovered_distinctions": ";".join(recovered),
                "failed_distinctions": ";".join(failed),
                "recovered_distinction_count": len(recovered),
                "recovery_profile_signature": f"recovered:{';'.join(recovered)}|failed:{';'.join(failed)}",
            }
        )
    return rows


def baseline_comparison_rows(
    entropy_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    left_entropy = row_by_channel(entropy_rows, PRESERVE_A_CHANNEL)
    right_entropy = row_by_channel(entropy_rows, PRESERVE_B_CHANNEL)
    left_profile = row_by_channel(profile_rows, PRESERVE_A_CHANNEL)
    right_profile = row_by_channel(profile_rows, PRESERVE_B_CHANNEL)
    matched_metrics = [
        "source_count",
        "edge_count",
        "global_target_support_size",
        "global_target_support",
        "global_target_weight_signature",
        "global_target_entropy_bits",
        "per_source_support_count_signature",
        "per_source_entropy_bits_signature",
        "min_per_source_entropy_bits",
        "max_per_source_entropy_bits",
    ]
    rows = [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "preserve_a_value": left_entropy[metric],
            "preserve_b_value": right_entropy[metric],
            "expected_relation": "matched",
            "relation_holds": int(left_entropy[metric] == right_entropy[metric]),
        }
        for metric in matched_metrics
    ]
    rows.append(
        {
            "witness_id": WITNESS_ID,
            "metric": "recovery_profile_signature",
            "preserve_a_value": left_profile["recovery_profile_signature"],
            "preserve_b_value": right_profile["recovery_profile_signature"],
            "expected_relation": "different",
            "relation_holds": int(
                left_profile["recovery_profile_signature"] != right_profile["recovery_profile_signature"]
            ),
        }
    )
    return rows


def witness_summary(
    *,
    entropy_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
) -> dict[str, object]:
    preserve_a = row_by_channel(profile_rows, PRESERVE_A_CHANNEL)
    preserve_b = row_by_channel(profile_rows, PRESERVE_B_CHANNEL)
    controls_hold = all(int(row["relation_holds"]) == 1 for row in comparison_rows)
    entropy_controls_hold = all(
        int(row["relation_holds"]) == 1
        for row in comparison_rows
        if row["expected_relation"] == "matched"
    )
    profile_differs = (
        preserve_a["recovery_profile_signature"] != preserve_b["recovery_profile_signature"]
    )
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "source_count": len(STATES),
        "channel_count": 2,
        "declared_distinction_panel": ";".join(DISTINCTIONS),
        "entropy_controls_hold": entropy_controls_hold,
        "recovery_profile_differs": profile_differs,
        "all_expected_relations_hold": controls_hold,
        "preserve_a_recovery_profile": preserve_a["recovery_profile_signature"],
        "preserve_b_recovery_profile": preserve_b["recovery_profile_signature"],
        "witness_status": (
            "same_entropy_different_recovery_profile"
            if entropy_controls_hold and profile_differs and controls_hold
            else "witness_failed"
        ),
        "not_claimed": [
            "semantic recovery",
            "identity detection",
            "value detection",
            "valuer detection",
            "agency detection",
            "Omega validation",
            "substrate-general theory validation",
        ],
        "entropy_rows_digest": stable_hash(entropy_rows, length=24),
        "profile_rows_digest": stable_hash(profile_rows, length=24),
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
        "recovery_rows_digest": stable_hash(recovery_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Entropy, Different Declared Recovery Profile Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baseline

```text
entropy_controls_hold: {summary["entropy_controls_hold"]}
all_expected_relations_hold: {summary["all_expected_relations_hold"]}
```

The two channels have matched per-source support count, per-source entropy,
global target support, global target weights, and global output entropy.

## Recovery Profile Difference

```text
preserve_a_recovery_profile: {summary["preserve_a_recovery_profile"]}
preserve_b_recovery_profile: {summary["preserve_b_recovery_profile"]}
```

## Read

Matched entropy summaries do not determine which declared distinction is
recoverable.

## Not Claimed

```text
semantic recovery
identity detection
value detection
valuer detection
agency detection
Omega validation
substrate-general theory validation
```
"""


def coordinate_for_distinction(distinction_id: str) -> int:
    if distinction_id == "D_A":
        return 0
    if distinction_id == "D_B":
        return 1
    raise ValueError(f"unknown distinction_id: {distinction_id}")


def observation_for_distinction(distinction_id: str) -> str:
    if distinction_id == "D_A":
        return "O_A"
    if distinction_id == "D_B":
        return "O_B"
    raise ValueError(f"unknown distinction_id: {distinction_id}")


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


def row_by_channel(rows: list[dict[str, object]], channel_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["channel_id"] == channel_id]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {channel_id}, found {len(matches)}")
    return matches[0]


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))


if __name__ == "__main__":
    main()
