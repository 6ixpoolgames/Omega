"""Same mutual information, different declared recovery witness.

This exact finite witness controls generic source-output information transfer
while changing declared registry recovery. It does not claim semantic recovery,
value, agency, identity, Omega validation, or substrate-general transfer.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path(
    "results/baseline_witnesses/20260611_same_mutual_information_different_declared_recovery_v0"
)
WITNESS_ID = "same_mutual_information_different_declared_recovery_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_dn"
STATES = ("00", "01", "10", "11")
OUTPUTS = ("0", "1")
DECLARED_CHANNEL = "transmit_declared_d"
NUISANCE_CHANNEL = "transmit_nuisance_n"

Channel = dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the same-mutual-information/different-declared-recovery witness."
    )
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
    output_rows = output_manifest_rows()
    kernel_rows = channel_kernel_rows(channels)
    information_rows = information_baseline_rows(channels)
    recovery_rows = declared_recovery_rows(channels)
    comparison_rows = baseline_comparison_rows(information_rows, recovery_rows)
    summary = witness_summary(
        information_rows=information_rows,
        recovery_rows=recovery_rows,
        comparison_rows=comparison_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "channel_manifest": out_dir / "channel_manifest.csv",
        "output_manifest": out_dir / "output_manifest.csv",
        "channel_kernel": out_dir / "channel_kernel.csv",
        "information_baseline_by_channel": out_dir / "information_baseline_by_channel.csv",
        "declared_recovery_by_channel": out_dir / "declared_recovery_by_channel.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["channel_manifest"], channel_rows)
    write_csv(artifacts["output_manifest"], output_rows)
    write_csv(artifacts["channel_kernel"], kernel_rows)
    write_csv(artifacts["information_baseline_by_channel"], information_rows)
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
        DECLARED_CHANNEL: {source: source[0] for source in STATES},
        NUISANCE_CHANNEL: {source: source[1] for source in STATES},
    }


def state_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "state_id": state,
            "d": state[0],
            "n": state[1],
            "source_prior": "1/4",
        }
        for state in STATES
    ]


def channel_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "channel_id": DECLARED_CHANNEL,
            "channel_role": "declared_registry_recovery_positive",
            "description": "deterministically transmits declared source bit d",
        },
        {
            "channel_id": NUISANCE_CHANNEL,
            "channel_role": "matched_information_control",
            "description": "deterministically transmits nuisance source bit n",
        },
    ]


def output_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "output_id": output,
            "declared_target_observation_id": "O_y",
            "description": "binary channel output",
        }
        for output in OUTPUTS
    ]


def channel_kernel_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        for source in STATES:
            output = channel[source]
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "channel_id": channel_id,
                    "source_state": source,
                    "source_d": source[0],
                    "source_n": source[1],
                    "output_id": output,
                    "kernel_weight": 1,
                    "kernel_probability": "1",
                }
            )
    return rows


def information_baseline_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        output_weights = output_weight_counts(channel)
        conditional_entropy = conditional_output_entropy_bits(channel)
        output_entropy = entropy_from_weights(output_weights.values())
        mutual_information = output_entropy - conditional_entropy
        capacity = deterministic_output_capacity_bits(channel)
        per_source_output_counts = {source: 1 for source in STATES}
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "source_count": len(STATES),
                "output_support_size": len(output_weights),
                "output_support": ";".join(sorted(output_weights)),
                "source_entropy_bits": "2.000000",
                "output_entropy_bits": f"{output_entropy:.6f}",
                "conditional_output_entropy_bits": f"{conditional_entropy:.6f}",
                "mutual_information_source_output_bits": f"{mutual_information:.6f}",
                "deterministic_output_capacity_bits": f"{capacity:.6f}",
                "output_weight_signature": signature(output_weights),
                "per_source_output_count_signature": signature(per_source_output_counts),
                "information_baseline_signature": (
                    f"I:{mutual_information:.6f}|"
                    f"C:{capacity:.6f}|"
                    f"H_Y:{output_entropy:.6f}|"
                    f"H_Y_given_X:{conditional_entropy:.6f}"
                ),
            }
        )
    return rows


def declared_recovery_rows(channels: dict[str, Channel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for channel_id, channel in channels.items():
        recovery = declared_d_recovery(channel)
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "channel_id": channel_id,
                "declared_source_distinction_id": "D_d",
                "declared_target_observation_id": "O_y",
                "declared_contract": "binary output y must recover source bit d",
                "exact_declared_recovery": int(recovery["exact_declared_recovery"]),
                "ambiguous_outputs": recovery["ambiguous_outputs"],
                "output_to_source_labels": recovery["output_to_source_labels"],
                "recovery_status": (
                    "declared_recovery_pass"
                    if recovery["exact_declared_recovery"]
                    else "declared_recovery_fail"
                ),
            }
        )
    return rows


def declared_d_recovery(channel: Channel) -> dict[str, object]:
    output_sources: dict[str, set[str]] = {}
    for source in STATES:
        output = channel[source]
        output_sources.setdefault(output, set()).add(source[0])

    ambiguous = {
        output: sorted(labels)
        for output, labels in output_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(output_sources) == ["0", "1"],
        "ambiguous_outputs": ";".join(
            f"{output}->{{{','.join(labels)}}}" for output, labels in sorted(ambiguous.items())
        ),
        "output_to_source_labels": ";".join(
            f"{output}->{{{','.join(sorted(labels))}}}"
            for output, labels in sorted(output_sources.items())
        ),
    }


def baseline_comparison_rows(
    information_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    declared_info = row_by_channel(information_rows, DECLARED_CHANNEL)
    nuisance_info = row_by_channel(information_rows, NUISANCE_CHANNEL)
    matched_metrics = [
        "source_count",
        "output_support_size",
        "output_support",
        "source_entropy_bits",
        "output_entropy_bits",
        "conditional_output_entropy_bits",
        "mutual_information_source_output_bits",
        "deterministic_output_capacity_bits",
        "output_weight_signature",
        "per_source_output_count_signature",
        "information_baseline_signature",
    ]
    rows = [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "declared_channel_value": declared_info[metric],
            "nuisance_channel_value": nuisance_info[metric],
            "expected_relation": "matched",
            "relation_holds": int(declared_info[metric] == nuisance_info[metric]),
        }
        for metric in matched_metrics
    ]
    rows.append(
        {
            "witness_id": WITNESS_ID,
            "metric": "declared_recovery_signature",
            "declared_channel_value": recovery_signature(recovery_rows, DECLARED_CHANNEL),
            "nuisance_channel_value": recovery_signature(recovery_rows, NUISANCE_CHANNEL),
            "expected_relation": "different",
            "relation_holds": int(
                recovery_signature(recovery_rows, DECLARED_CHANNEL)
                != recovery_signature(recovery_rows, NUISANCE_CHANNEL)
            ),
        }
    )
    return rows


def witness_summary(
    *,
    information_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
) -> dict[str, object]:
    information = {row["channel_id"]: row for row in information_rows}
    recovery = {row["channel_id"]: row for row in recovery_rows}
    information_controls_hold = all(
        int(row["relation_holds"]) == 1
        for row in comparison_rows
        if row["expected_relation"] == "matched"
    )
    declared_recovers = bool(int(recovery[DECLARED_CHANNEL]["exact_declared_recovery"]))
    nuisance_recovers = bool(int(recovery[NUISANCE_CHANNEL]["exact_declared_recovery"]))
    declared_recovery_differs = declared_recovers != nuisance_recovers
    all_expected_relations_hold = all(int(row["relation_holds"]) == 1 for row in comparison_rows)

    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "source_count": len(STATES),
        "channel_count": 2,
        "declared_source_distinction_id": "D_d",
        "declared_target_observation_id": "O_y",
        "information_controls_hold": information_controls_hold,
        "declared_recovery_differs": declared_recovery_differs,
        "all_expected_relations_hold": all_expected_relations_hold,
        "declared_channel_mutual_information_bits": information[DECLARED_CHANNEL][
            "mutual_information_source_output_bits"
        ],
        "nuisance_channel_mutual_information_bits": information[NUISANCE_CHANNEL][
            "mutual_information_source_output_bits"
        ],
        "declared_channel_capacity_bits": information[DECLARED_CHANNEL][
            "deterministic_output_capacity_bits"
        ],
        "nuisance_channel_capacity_bits": information[NUISANCE_CHANNEL][
            "deterministic_output_capacity_bits"
        ],
        "declared_channel_exact_declared_recovery": declared_recovers,
        "nuisance_channel_exact_declared_recovery": nuisance_recovers,
        "witness_status": (
            "same_mutual_information_different_declared_recovery"
            if (
                information_controls_hold
                and declared_recovers
                and not nuisance_recovers
                and all_expected_relations_hold
            )
            else "witness_failed"
        ),
        "not_claimed": [
            "semantic recovery",
            "value detection",
            "valuer detection",
            "agency detection",
            "identity detection",
            "Omega validation",
            "substrate-general theory validation",
        ],
        "information_rows_digest": stable_hash(information_rows, length=24),
        "recovery_rows_digest": stable_hash(recovery_rows, length=24),
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Mutual Information, Different Declared Recovery Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Information Baseline

```text
information_controls_hold: {summary["information_controls_hold"]}
all_expected_relations_hold: {summary["all_expected_relations_hold"]}
declared_channel_mutual_information_bits: {summary["declared_channel_mutual_information_bits"]}
nuisance_channel_mutual_information_bits: {summary["nuisance_channel_mutual_information_bits"]}
declared_channel_capacity_bits: {summary["declared_channel_capacity_bits"]}
nuisance_channel_capacity_bits: {summary["nuisance_channel_capacity_bits"]}
```

Both channels are deterministic binary-output channels over the same uniform
two-bit source. Each transmits exactly one bit of source information and has the
same deterministic binary-output capacity.

## Declared Registry Recovery

```text
declared_source_distinction_id: {summary["declared_source_distinction_id"]}
declared_target_observation_id: {summary["declared_target_observation_id"]}
declared_channel_exact_declared_recovery: {summary["declared_channel_exact_declared_recovery"]}
nuisance_channel_exact_declared_recovery: {summary["nuisance_channel_exact_declared_recovery"]}
```

## Read

Generic source-output mutual information and deterministic output capacity do
not determine declared registry recovery. The matched control transmits a
nuisance bit with the same information score while failing the declared
distinction contract.

## Not Claimed

```text
semantic recovery
value detection
valuer detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
"""


def output_weight_counts(channel: Channel) -> dict[str, int]:
    weights: dict[str, int] = {}
    for output in channel.values():
        weights[output] = weights.get(output, 0) + 1
    return weights


def conditional_output_entropy_bits(channel: Channel) -> float:
    return sum(0.25 * entropy_from_weights([1]) for _source in channel)


def deterministic_output_capacity_bits(channel: Channel) -> float:
    image_size = len(set(channel.values()))
    if image_size <= 0:
        return 0.0
    return math.log2(image_size)


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


def recovery_signature(rows: list[dict[str, object]], channel_id: str) -> str:
    row = row_by_channel(rows, channel_id)
    return f"{channel_id}:{row['exact_declared_recovery']}:{row['output_to_source_labels']}"


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


if __name__ == "__main__":
    main()
