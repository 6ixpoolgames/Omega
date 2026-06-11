"""Same optimized success, different declared recovery witness.

This exact finite witness separates optimized diagnostic recovery from declared
instrument recovery. It does not try to detect Omega, value, agency, identity,
or semantic recovery.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path(
    "results/baseline_witnesses/20260611_same_optimized_success_different_declared_recovery_v0"
)
WITNESS_ID = "same_optimized_success_different_declared_recovery_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_dn"
STATES = ("00", "01", "10", "11")
DECLARED_CHANNEL = "declared_d_in_target_first"
SHIFTED_CHANNEL = "shifted_d_in_target_second"
DECLARED_OBSERVATION = "O_first"
OPTIMIZED_PANEL = ("O_first", "O_second")

Channel = dict[str, tuple[str, ...]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the same-optimized-success/different-declared-recovery witness."
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    channels = channel_definitions()
    baseline_rows = reachability_baseline_rows(channels)
    declared_rows = declared_recovery_rows(channels)
    optimized_panel_rows = optimized_panel_recovery_rows(channels)
    optimized_summary_rows = optimized_recovery_rows(optimized_panel_rows)
    comparison_rows = baseline_comparison_rows(baseline_rows)
    state_rows = state_manifest_rows()
    channel_rows = channel_manifest_rows()
    observation_rows = observation_manifest_rows()
    support_rows = support_edge_rows(channels)

    summary = witness_summary(
        comparison_rows=comparison_rows,
        declared_rows=declared_rows,
        optimized_rows=optimized_summary_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "channel_manifest": out_dir / "channel_manifest.csv",
        "observation_manifest": out_dir / "observation_manifest.csv",
        "support_edges": out_dir / "support_edges.csv",
        "reachability_baseline_by_channel": out_dir / "reachability_baseline_by_channel.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "declared_recovery_by_channel": out_dir / "declared_recovery_by_channel.csv",
        "optimized_panel_recovery_by_observation": out_dir / "optimized_panel_recovery_by_observation.csv",
        "optimized_recovery_by_channel": out_dir / "optimized_recovery_by_channel.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["channel_manifest"], channel_rows)
    write_csv(artifacts["observation_manifest"], observation_rows)
    write_csv(artifacts["support_edges"], support_rows)
    write_csv(artifacts["reachability_baseline_by_channel"], baseline_rows)
    write_csv(artifacts["baseline_comparison"], comparison_rows)
    write_csv(artifacts["declared_recovery_by_channel"], declared_rows)
    write_csv(artifacts["optimized_panel_recovery_by_observation"], optimized_panel_rows)
    write_csv(artifacts["optimized_recovery_by_channel"], optimized_summary_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def channel_definitions() -> dict[str, Channel]:
    return {
        DECLARED_CHANNEL: {
            source: tuple(target for target in STATES if target[0] == source[0])
            for source in STATES
        },
        SHIFTED_CHANNEL: {
            source: tuple(target for target in STATES if target[1] == source[0])
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
            "channel_id": DECLARED_CHANNEL,
            "channel_role": "declared_recovery_positive",
            "description": "source d appears in declared target observation O_first",
        },
        {
            "channel_id": SHIFTED_CHANNEL,
            "channel_role": "optimized_only_control",
            "description": "source d appears only in nondeclared optimized observation O_second",
        },
    ]


def observation_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "observation_id": "O_first",
            "target_coordinate": 0,
            "observation_role": "declared_and_optimized",
            "description": "target first bit",
        },
        {
            "observation_id": "O_second",
            "target_coordinate": 1,
            "observation_role": "optimized_only",
            "description": "target second bit",
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
                        "target_first": target[0],
                        "target_second": target[1],
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
            "declared_target_observation_id": DECLARED_OBSERVATION,
            "declared_contract": "target first bit must recover source first bit over support",
            "exact_declared_recovery": int(recovery["exact_recovery"]),
            "ambiguous_target_observations": recovery["ambiguous_target_observations"],
            "observation_to_source_labels": recovery["observation_to_source_labels"],
            "recovery_status": (
                "declared_recovery_pass"
                if recovery["exact_recovery"]
                else "declared_recovery_fail"
            ),
        }
        for channel_id, recovery in (
            (channel_id, recovery_for_observation(channel, DECLARED_OBSERVATION))
            for channel_id, channel in channels.items()
        )
    ]


def optimized_panel_recovery_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        for observation_id in OPTIMIZED_PANEL:
            recovery = recovery_for_observation(channel, observation_id)
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "channel_id": channel_id,
                    "source_distinction_id": "D_d",
                    "candidate_target_observation_id": observation_id,
                    "exact_recovery": int(recovery["exact_recovery"]),
                    "ambiguous_target_observations": recovery["ambiguous_target_observations"],
                    "observation_to_source_labels": recovery["observation_to_source_labels"],
                }
            )
    return rows


def optimized_recovery_rows(panel_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id in (DECLARED_CHANNEL, SHIFTED_CHANNEL):
        candidates = [row for row in panel_rows if row["channel_id"] == channel_id]
        exact_candidates = [
            str(row["candidate_target_observation_id"])
            for row in candidates
            if int(row["exact_recovery"]) == 1
        ]
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "source_distinction_id": "D_d",
                "optimized_candidate_panel": ";".join(OPTIMIZED_PANEL),
                "exact_optimized_recovery": int(bool(exact_candidates)),
                "best_observation_id": exact_candidates[0] if exact_candidates else "",
                "all_exact_observations": ";".join(exact_candidates),
                "optimized_status": (
                    "optimized_recovery_pass"
                    if exact_candidates
                    else "optimized_recovery_fail"
                ),
            }
        )
    return rows


def recovery_for_observation(channel: Channel, observation_id: str) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    coordinate = observation_coordinate(observation_id)
    for source in STATES:
        source_label = source[0]
        for target in channel[source]:
            target_observation = target[coordinate]
            observation_sources.setdefault(target_observation, set()).add(source_label)

    ambiguous = {
        observation: sorted(labels)
        for observation, labels in observation_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_target_observations": ";".join(
            f"{observation}->{{{','.join(labels)}}}" for observation, labels in sorted(ambiguous.items())
        ),
        "observation_to_source_labels": ";".join(
            f"{observation}->{{{','.join(sorted(labels))}}}"
            for observation, labels in sorted(observation_sources.items())
        ),
    }


def observation_coordinate(observation_id: str) -> int:
    if observation_id == "O_first":
        return 0
    if observation_id == "O_second":
        return 1
    raise ValueError(f"unknown observation_id: {observation_id}")


def baseline_comparison_rows(baseline_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    left = row_by_channel(baseline_rows, DECLARED_CHANNEL)
    right = row_by_channel(baseline_rows, SHIFTED_CHANNEL)
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
            "declared_channel_value": left[metric],
            "shifted_channel_value": right[metric],
            "matched": int(left[metric] == right[metric]),
        }
        for metric in metrics
    ]


def witness_summary(
    *,
    comparison_rows: list[dict[str, object]],
    declared_rows: list[dict[str, object]],
    optimized_rows: list[dict[str, object]],
) -> dict[str, object]:
    declared = {row["channel_id"]: row for row in declared_rows}
    optimized = {row["channel_id"]: row for row in optimized_rows}
    baseline_controls_matched = all(int(row["matched"]) == 1 for row in comparison_rows)
    declared_channel_recovers = bool(int(declared[DECLARED_CHANNEL]["exact_declared_recovery"]))
    shifted_channel_recovers_declared = bool(int(declared[SHIFTED_CHANNEL]["exact_declared_recovery"]))
    declared_channel_optimized = bool(int(optimized[DECLARED_CHANNEL]["exact_optimized_recovery"]))
    shifted_channel_optimized = bool(int(optimized[SHIFTED_CHANNEL]["exact_optimized_recovery"]))
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "state_count": len(STATES),
        "channel_count": 2,
        "declared_source_distinction_id": "D_d",
        "declared_target_observation_id": DECLARED_OBSERVATION,
        "optimized_candidate_panel": ";".join(OPTIMIZED_PANEL),
        "baseline_controls_matched": baseline_controls_matched,
        "same_optimized_success": declared_channel_optimized and shifted_channel_optimized,
        "declared_channel_exact_declared_recovery": declared_channel_recovers,
        "shifted_channel_exact_declared_recovery": shifted_channel_recovers_declared,
        "declared_channel_exact_optimized_recovery": declared_channel_optimized,
        "shifted_channel_exact_optimized_recovery": shifted_channel_optimized,
        "declared_channel_best_observation_id": optimized[DECLARED_CHANNEL]["best_observation_id"],
        "shifted_channel_best_observation_id": optimized[SHIFTED_CHANNEL]["best_observation_id"],
        "witness_status": (
            "same_optimized_success_different_declared_recovery"
            if (
                baseline_controls_matched
                and declared_channel_recovers
                and not shifted_channel_recovers_declared
                and declared_channel_optimized
                and shifted_channel_optimized
            )
            else "witness_failed"
        ),
        "not_claimed": [
            "Omega validation",
            "value detection",
            "valuer detection",
            "agency detection",
            "identity detection",
            "semantic recovery",
            "substrate-general theory validation",
        ],
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
        "declared_rows_digest": stable_hash(declared_rows, length=24),
        "optimized_rows_digest": stable_hash(optimized_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Optimized Success, Different Declared Recovery Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baselines

```text
state_count: {summary["state_count"]}
channel_count: {summary["channel_count"]}
baseline_controls_matched: {summary["baseline_controls_matched"]}
same_optimized_success: {summary["same_optimized_success"]}
```

The two channels have the same reachability and entropy controls. Both are
exactly recoverable by an optimized choice over the observation panel.

## Declared Versus Optimized Recovery

```text
declared_target_observation_id: {summary["declared_target_observation_id"]}
optimized_candidate_panel: {summary["optimized_candidate_panel"]}
declared_channel_exact_declared_recovery: {summary["declared_channel_exact_declared_recovery"]}
shifted_channel_exact_declared_recovery: {summary["shifted_channel_exact_declared_recovery"]}
declared_channel_best_observation_id: {summary["declared_channel_best_observation_id"]}
shifted_channel_best_observation_id: {summary["shifted_channel_best_observation_id"]}
```

## Read

Optimized recovery success is insufficient for declared theorem-transfer
readiness. The shifted channel recovers the source distinction only after
substituting a nondeclared observation.

## Not Claimed

```text
Omega validation
value detection
valuer detection
agency detection
identity detection
semantic recovery
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
