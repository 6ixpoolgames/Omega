"""Same marginal success, different joint success witness.

This exact finite witness controls a weaker but common marginal baseline:
Bayes-best recovery success for each single-bit marginal. It then shows that
the matched marginal-success vector does not determine joint recovery success.

It does not claim exact marginal preservation, value, agency, identity, Omega,
or substrate-general recovery.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Callable

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path("results/baseline_witnesses/20260611_same_marginal_success_different_joint_success_v0")
WITNESS_ID = "same_marginal_success_different_joint_success_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_ab"
STATES = ("00", "01", "10", "11")
CORRELATED_CHANNEL = "correlated_both_or_none"
INDEPENDENT_CHANNEL = "independent_bit_masks"
DISTINCTIONS = ("D_A", "D_B", "D_joint")

WeightedChannel = dict[str, dict[str, int]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the same-marginal-success/different-joint-success witness.")
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
    baseline_rows = channel_baseline_rows(channels)
    recovery_rows = bayes_recovery_rows(channels)
    marginal_rows = marginal_success_rows(recovery_rows)
    joint_rows = joint_success_rows(recovery_rows)
    comparison_rows = comparison_rows_for_witness(baseline_rows, marginal_rows, joint_rows)
    summary = witness_summary(
        comparison_rows=comparison_rows,
        marginal_rows=marginal_rows,
        joint_rows=joint_rows,
        recovery_rows=recovery_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "channel_manifest": out_dir / "channel_manifest.csv",
        "support_edges": out_dir / "support_edges.csv",
        "channel_baseline_by_channel": out_dir / "channel_baseline_by_channel.csv",
        "bayes_recovery_by_distinction": out_dir / "bayes_recovery_by_distinction.csv",
        "marginal_success_by_channel": out_dir / "marginal_success_by_channel.csv",
        "joint_success_by_channel": out_dir / "joint_success_by_channel.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["channel_manifest"], channel_rows)
    write_csv(artifacts["support_edges"], support_rows)
    write_csv(artifacts["channel_baseline_by_channel"], baseline_rows)
    write_csv(artifacts["bayes_recovery_by_distinction"], recovery_rows)
    write_csv(artifacts["marginal_success_by_channel"], marginal_rows)
    write_csv(artifacts["joint_success_by_channel"], joint_rows)
    write_csv(artifacts["baseline_comparison"], comparison_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def channel_definitions() -> dict[str, WeightedChannel]:
    return {
        CORRELATED_CHANNEL: {
            source: {
                f"both0:{source}": 1,
                f"both1:{source}": 1,
                "none0": 1,
                "none1": 1,
            }
            for source in STATES
        },
        INDEPENDENT_CHANNEL: {
            source: {
                f"both:{source}": 1,
                f"a_only:{source[0]}": 1,
                f"b_only:{source[1]}": 1,
                "none": 1,
            }
            for source in STATES
        },
    }


def state_manifest_rows() -> list[dict[str, object]]:
    return [
        {
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
            "channel_id": CORRELATED_CHANNEL,
            "channel_role": "joint_success_positive",
            "description": "reveals both bits together or neither bit",
        },
        {
            "channel_id": INDEPENDENT_CHANNEL,
            "channel_role": "matched_marginal_control",
            "description": "reveals each bit through independent reveal masks",
        },
    ]


def support_edge_rows(channels: dict[str, WeightedChannel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        for source in STATES:
            total = sum(channel[source].values())
            for target, weight in sorted(channel[source].items()):
                rows.append(
                    {
                        "witness_id": WITNESS_ID,
                        "carrier_id": CARRIER_ID,
                        "channel_id": channel_id,
                        "source_state": source,
                        "target_observation": target,
                        "source_a": source[0],
                        "source_b": source[1],
                        "edge_weight": weight,
                        "edge_probability": fraction_text(Fraction(weight, total)),
                        "per_source_support_count": len(channel[source]),
                        "per_source_weight_total": total,
                    }
                )
    return rows


def channel_baseline_rows(channels: dict[str, WeightedChannel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        support_counts = {source: len(channel[source]) for source in STATES}
        weight_totals = {source: sum(channel[source].values()) for source in STATES}
        entropies = {source: support_entropy_bits(channel[source]) for source in STATES}
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "source_count": len(STATES),
                "edge_count": sum(support_counts.values()),
                "per_source_support_count_signature": signature(support_counts),
                "per_source_weight_total_signature": signature(weight_totals),
                "per_source_entropy_bits_signature": float_signature(entropies),
                "min_per_source_entropy_bits": f"{min(entropies.values()):.6f}",
                "max_per_source_entropy_bits": f"{max(entropies.values()):.6f}",
            }
        )
    return rows


def bayes_recovery_rows(channels: dict[str, WeightedChannel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        for distinction_id in DISTINCTIONS:
            result = bayes_success(channel, labeler_for_distinction(distinction_id))
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "channel_id": channel_id,
                    "source_distinction_id": distinction_id,
                    "bayes_success_fraction": fraction_text(result["success"]),
                    "bayes_success_float": f"{float(result['success']):.6f}",
                    "success_weight": result["success_weight"],
                    "total_weight": result["total_weight"],
                    "target_count": result["target_count"],
                    "target_best_label_table": result["target_best_label_table"],
                }
            )
    return rows


def bayes_success(channel: WeightedChannel, labeler: Callable[[str], str]) -> dict[str, object]:
    target_label_weights: dict[str, dict[str, int]] = {}
    total_weight = 0
    for source in STATES:
        label = labeler(source)
        for target, weight in channel[source].items():
            target_label_weights.setdefault(target, {})
            target_label_weights[target][label] = target_label_weights[target].get(label, 0) + weight
            total_weight += weight

    success_weight = sum(max(label_weights.values()) for label_weights in target_label_weights.values())
    best_table = ";".join(
        f"{target}->{best_label(target_label_weights[target])}"
        for target in sorted(target_label_weights)
    )
    return {
        "success": Fraction(success_weight, total_weight),
        "success_weight": success_weight,
        "total_weight": total_weight,
        "target_count": len(target_label_weights),
        "target_best_label_table": best_table,
    }


def best_label(label_weights: dict[str, int]) -> str:
    max_weight = max(label_weights.values())
    labels = sorted(label for label, weight in label_weights.items() if weight == max_weight)
    return "{" + ",".join(labels) + "}"


def labeler_for_distinction(distinction_id: str) -> Callable[[str], str]:
    if distinction_id == "D_A":
        return lambda state: state[0]
    if distinction_id == "D_B":
        return lambda state: state[1]
    if distinction_id == "D_joint":
        return lambda state: state
    raise ValueError(f"unknown distinction_id: {distinction_id}")


def marginal_success_rows(recovery_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id in (CORRELATED_CHANNEL, INDEPENDENT_CHANNEL):
        by_distinction = {
            row["source_distinction_id"]: row
            for row in recovery_rows
            if row["channel_id"] == channel_id
        }
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "marginal_distinctions": "D_A;D_B",
                "D_A_bayes_success_fraction": by_distinction["D_A"]["bayes_success_fraction"],
                "D_B_bayes_success_fraction": by_distinction["D_B"]["bayes_success_fraction"],
                "marginal_success_vector": (
                    f"D_A:{by_distinction['D_A']['bayes_success_fraction']};"
                    f"D_B:{by_distinction['D_B']['bayes_success_fraction']}"
                ),
            }
        )
    return rows


def joint_success_rows(recovery_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id in (CORRELATED_CHANNEL, INDEPENDENT_CHANNEL):
        joint = [
            row for row in recovery_rows
            if row["channel_id"] == channel_id and row["source_distinction_id"] == "D_joint"
        ][0]
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "joint_distinction": "D_joint",
                "joint_bayes_success_fraction": joint["bayes_success_fraction"],
                "joint_bayes_success_float": joint["bayes_success_float"],
            }
        )
    return rows


def comparison_rows_for_witness(
    baseline_rows: list[dict[str, object]],
    marginal_rows: list[dict[str, object]],
    joint_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    left_base = row_by_channel(baseline_rows, CORRELATED_CHANNEL)
    right_base = row_by_channel(baseline_rows, INDEPENDENT_CHANNEL)
    left_marginal = row_by_channel(marginal_rows, CORRELATED_CHANNEL)
    right_marginal = row_by_channel(marginal_rows, INDEPENDENT_CHANNEL)
    left_joint = row_by_channel(joint_rows, CORRELATED_CHANNEL)
    right_joint = row_by_channel(joint_rows, INDEPENDENT_CHANNEL)
    matched_metrics = [
        "source_count",
        "edge_count",
        "per_source_support_count_signature",
        "per_source_weight_total_signature",
        "per_source_entropy_bits_signature",
    ]
    rows = [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "correlated_value": left_base[metric],
            "independent_value": right_base[metric],
            "expected_relation": "matched",
            "relation_holds": int(left_base[metric] == right_base[metric]),
        }
        for metric in matched_metrics
    ]
    rows.append(
        {
            "witness_id": WITNESS_ID,
            "metric": "marginal_success_vector",
            "correlated_value": left_marginal["marginal_success_vector"],
            "independent_value": right_marginal["marginal_success_vector"],
            "expected_relation": "matched",
            "relation_holds": int(
                left_marginal["marginal_success_vector"] == right_marginal["marginal_success_vector"]
            ),
        }
    )
    rows.append(
        {
            "witness_id": WITNESS_ID,
            "metric": "joint_bayes_success_fraction",
            "correlated_value": left_joint["joint_bayes_success_fraction"],
            "independent_value": right_joint["joint_bayes_success_fraction"],
            "expected_relation": "different",
            "relation_holds": int(
                left_joint["joint_bayes_success_fraction"] != right_joint["joint_bayes_success_fraction"]
            ),
        }
    )
    return rows


def witness_summary(
    *,
    comparison_rows: list[dict[str, object]],
    marginal_rows: list[dict[str, object]],
    joint_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
) -> dict[str, object]:
    left_marginal = row_by_channel(marginal_rows, CORRELATED_CHANNEL)
    right_marginal = row_by_channel(marginal_rows, INDEPENDENT_CHANNEL)
    left_joint = row_by_channel(joint_rows, CORRELATED_CHANNEL)
    right_joint = row_by_channel(joint_rows, INDEPENDENT_CHANNEL)
    controls_hold = all(int(row["relation_holds"]) == 1 for row in comparison_rows)
    same_marginal_success = (
        left_marginal["marginal_success_vector"] == right_marginal["marginal_success_vector"]
    )
    different_joint_success = (
        left_joint["joint_bayes_success_fraction"] != right_joint["joint_bayes_success_fraction"]
    )
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "source_count": len(STATES),
        "channel_count": 2,
        "marginal_distinctions": "D_A;D_B",
        "joint_distinction": "D_joint",
        "controls_hold": controls_hold,
        "same_marginal_success": same_marginal_success,
        "different_joint_success": different_joint_success,
        "correlated_marginal_success_vector": left_marginal["marginal_success_vector"],
        "independent_marginal_success_vector": right_marginal["marginal_success_vector"],
        "correlated_joint_success_fraction": left_joint["joint_bayes_success_fraction"],
        "independent_joint_success_fraction": right_joint["joint_bayes_success_fraction"],
        "witness_status": (
            "same_marginal_success_different_joint_success"
            if controls_hold and same_marginal_success and different_joint_success
            else "witness_failed"
        ),
        "not_claimed": [
            "exact marginal preservation",
            "Omega validation",
            "value detection",
            "valuer detection",
            "agency detection",
            "identity detection",
            "semantic recovery",
            "substrate-general theory validation",
        ],
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
        "marginal_rows_digest": stable_hash(marginal_rows, length=24),
        "joint_rows_digest": stable_hash(joint_rows, length=24),
        "recovery_rows_digest": stable_hash(recovery_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Marginal Success, Different Joint Success Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Baseline

```text
controls_hold: {summary["controls_hold"]}
same_marginal_success: {summary["same_marginal_success"]}
correlated_marginal_success_vector: {summary["correlated_marginal_success_vector"]}
independent_marginal_success_vector: {summary["independent_marginal_success_vector"]}
```

The controlled marginal baseline is Bayes-best single-bit recovery success for
`D_A` and `D_B`, not exact marginal preservation.

## Joint Difference

```text
correlated_joint_success_fraction: {summary["correlated_joint_success_fraction"]}
independent_joint_success_fraction: {summary["independent_joint_success_fraction"]}
```

## Read

Matched marginal diagnostic success does not determine joint recovery success.

## Not Claimed

```text
exact marginal preservation
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


def support_entropy_bits(weights_by_target: dict[str, int]) -> float:
    import math

    total = sum(weights_by_target.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for weight in weights_by_target.values():
        probability = weight / total
        entropy -= probability * math.log2(probability)
    return entropy


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


def float_signature(values: dict[str, float]) -> str:
    return ";".join(f"{key}:{values[key]:.6f}" for key in sorted(values))


if __name__ == "__main__":
    main()
