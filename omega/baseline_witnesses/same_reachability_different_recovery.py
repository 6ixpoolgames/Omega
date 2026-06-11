"""Same reachability, different declared recovery witness.

This module is intentionally tiny and exact. It does not try to detect Omega,
value, agency, identity, or substrate-general recovery. It only demonstrates a
finite baseline separation:

same per-source reachable count, same global target support, and same uniform
per-source entropy can still differ on declared distinction recovery.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path("results/baseline_witnesses/20260611_same_reachability_different_recovery_v0")
WITNESS_ID = "same_reachability_different_recovery_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_dn"
STATES = ("00", "01", "10", "11")
PRESERVE_CHANNEL = "preserve_d_scramble_n"
ERASE_CHANNEL = "erase_d_preserve_n"

Channel = dict[str, tuple[str, ...]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same-reachability/different-recovery witness.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    channels = channel_definitions()
    support_rows = support_edge_rows(channels)
    baseline_rows = reachability_baseline_rows(channels)
    recovery_rows = declared_recovery_rows(channels)
    comparison_rows = baseline_comparison_rows(baseline_rows)
    state_rows = state_manifest_rows()
    channel_rows = channel_manifest_rows()

    summary = witness_summary(
        baseline_rows=baseline_rows,
        recovery_rows=recovery_rows,
        comparison_rows=comparison_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "channel_manifest": out_dir / "channel_manifest.csv",
        "support_edges": out_dir / "support_edges.csv",
        "reachability_baseline_by_channel": out_dir / "reachability_baseline_by_channel.csv",
        "declared_recovery_by_channel": out_dir / "declared_recovery_by_channel.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["channel_manifest"], channel_rows)
    write_csv(artifacts["support_edges"], support_rows)
    write_csv(artifacts["reachability_baseline_by_channel"], baseline_rows)
    write_csv(artifacts["declared_recovery_by_channel"], recovery_rows)
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
        PRESERVE_CHANNEL: {
            source: tuple(target for target in STATES if target[0] == source[0])
            for source in STATES
        },
        ERASE_CHANNEL: {
            source: tuple(target for target in STATES if target[1] == source[1])
            for source in STATES
        },
    }


def state_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "carrier_id": CARRIER_ID,
            "state_id": state,
            "d": state[0],
            "n": state[1],
        }
        for state in STATES
    ]


def channel_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "channel_id": PRESERVE_CHANNEL,
            "channel_role": "positive_witness",
            "description": "preserves declared d while scrambling nuisance coordinate n",
        },
        {
            "channel_id": ERASE_CHANNEL,
            "channel_role": "matched_reachability_control",
            "description": "erases declared d while preserving nuisance coordinate n",
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
                        "source_d": source[0],
                        "source_n": source[1],
                        "target_d": target[0],
                        "target_n": target[1],
                        "edge_weight": 1,
                        "edge_probability": f"1/{len(support)}",
                        "per_source_support_count": len(support),
                    }
                )
    return rows


def reachability_baseline_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        support_counts = {source: len(channel[source]) for source in STATES}
        entropies = {source: support_entropy_bits(channel[source]) for source in STATES}
        global_support = sorted({target for source in STATES for target in channel[source]})
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "state_count": len(STATES),
                "source_count": len(STATES),
                "edge_count": sum(support_counts.values()),
                "global_target_support_size": len(global_support),
                "global_target_support": ";".join(global_support),
                "per_source_reachable_count_signature": signature(support_counts),
                "min_per_source_reachable_count": min(support_counts.values()),
                "max_per_source_reachable_count": max(support_counts.values()),
                "per_source_entropy_bits_signature": float_signature(entropies),
                "min_per_source_entropy_bits": f"{min(entropies.values()):.6f}",
                "max_per_source_entropy_bits": f"{max(entropies.values()):.6f}",
            }
        )
    return rows


def declared_recovery_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "channel_id": channel_id,
            "declared_source_distinction_id": "D_d",
            "declared_target_observation_id": "O_d",
            "declared_contract": "target first bit must recover source first bit over support",
            "exact_declared_recovery": int(recovery["exact_declared_recovery"]),
            "ambiguous_target_observations": recovery["ambiguous_target_observations"],
            "observation_to_source_labels": recovery["observation_to_source_labels"],
            "recovery_status": (
                "declared_recovery_pass"
                if recovery["exact_declared_recovery"]
                else "declared_recovery_fail"
            ),
        }
        for channel_id, recovery in (
            (channel_id, declared_d_recovery(channel)) for channel_id, channel in channels.items()
        )
    ]


def declared_d_recovery(channel: Channel) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    for source in STATES:
        source_label = source[0]
        for target in channel[source]:
            target_observation = target[0]
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


def baseline_comparison_rows(baseline_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    left = row_by_channel(baseline_rows, PRESERVE_CHANNEL)
    right = row_by_channel(baseline_rows, ERASE_CHANNEL)
    metrics = [
        "state_count",
        "source_count",
        "edge_count",
        "global_target_support_size",
        "global_target_support",
        "per_source_reachable_count_signature",
        "min_per_source_reachable_count",
        "max_per_source_reachable_count",
        "per_source_entropy_bits_signature",
        "min_per_source_entropy_bits",
        "max_per_source_entropy_bits",
    ]
    return [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "preserve_d_value": left[metric],
            "erase_d_value": right[metric],
            "matched": int(left[metric] == right[metric]),
        }
        for metric in metrics
    ]


def witness_summary(
    *,
    baseline_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
) -> dict[str, object]:
    recovery = {row["channel_id"]: row for row in recovery_rows}
    baseline_controls_matched = all(int(row["matched"]) == 1 for row in comparison_rows)
    preserve_recovers = bool(int(recovery[PRESERVE_CHANNEL]["exact_declared_recovery"]))
    erase_recovers = bool(int(recovery[ERASE_CHANNEL]["exact_declared_recovery"]))
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "state_count": len(STATES),
        "channel_count": 2,
        "declared_source_distinction_id": "D_d",
        "declared_target_observation_id": "O_d",
        "baseline_controls_matched": baseline_controls_matched,
        "preserve_channel_exact_declared_recovery": preserve_recovers,
        "erase_channel_exact_declared_recovery": erase_recovers,
        "witness_status": (
            "same_reachability_different_declared_recovery"
            if baseline_controls_matched and preserve_recovers and not erase_recovers
            else "witness_failed"
        ),
        "not_claimed": [
            "Omega validation",
            "value detection",
            "valuer detection",
            "agency detection",
            "identity detection",
            "substrate-general theory validation",
        ],
        "baseline_rows_digest": stable_hash(baseline_rows, length=24),
        "recovery_rows_digest": stable_hash(recovery_rows, length=24),
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Reachability, Different Declared Recovery Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baselines

```text
state_count: {summary["state_count"]}
channel_count: {summary["channel_count"]}
baseline_controls_matched: {summary["baseline_controls_matched"]}
```

The two channels have the same per-source reachable count, same total edge
count, same global target support, and same uniform per-source entropy.

## Declared Recovery

```text
declared_source_distinction_id: {summary["declared_source_distinction_id"]}
declared_target_observation_id: {summary["declared_target_observation_id"]}
preserve_channel_exact_declared_recovery: {summary["preserve_channel_exact_declared_recovery"]}
erase_channel_exact_declared_recovery: {summary["erase_channel_exact_declared_recovery"]}
```

## Read

Reachability count and global reachable support are insufficient for declared
distinction recovery in this finite witness.

## Not Claimed

```text
Omega validation
value detection
valuer detection
agency detection
identity detection
substrate-general theory validation
```
"""


def row_by_channel(rows: list[dict[str, object]], channel_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["channel_id"] == channel_id]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {channel_id}, found {len(matches)}")
    return matches[0]


def support_entropy_bits(support: tuple[str, ...]) -> float:
    if not support:
        return 0.0
    probability = 1.0 / len(support)
    return -sum(probability * math.log2(probability) for _target in support)


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))


if __name__ == "__main__":
    main()
