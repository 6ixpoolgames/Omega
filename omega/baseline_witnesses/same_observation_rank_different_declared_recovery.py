"""Same observation rank, different declared recovery witness.

This exact finite witness compares two deterministic one-bit observers over the
same four-state carrier. Both observers have the same finite observation-rank
summary and the same observation partition shape. Only one recovers the
declared source distinction.

It does not claim full linear observability, control synthesis, semantic
recovery, value, agency, identity, Omega, or substrate-general transfer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path(
    "results/baseline_witnesses/20260611_same_observation_rank_different_declared_recovery_v0"
)
WITNESS_ID = "same_observation_rank_different_declared_recovery_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_dn_observation_panel"
STATES = ("00", "01", "10", "11")
OUTPUTS = ("0", "1")
DECLARED_OBSERVER = "observe_declared_d"
NUISANCE_OBSERVER = "observe_nuisance_n"

Observer = dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the same-observation-rank/different-declared-recovery witness."
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    observers = observer_definitions()
    state_rows = state_manifest_rows()
    observer_rows = observer_manifest_rows()
    output_rows = output_manifest_rows()
    observation_rows = observation_mapping_rows(observers)
    baseline_rows = observability_baseline_rows(observers)
    recovery_rows = declared_recovery_rows(observers)
    comparison_rows = baseline_comparison_rows(baseline_rows, recovery_rows)
    summary = witness_summary(
        baseline_rows=baseline_rows,
        recovery_rows=recovery_rows,
        comparison_rows=comparison_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "observer_manifest": out_dir / "observer_manifest.csv",
        "output_manifest": out_dir / "output_manifest.csv",
        "observation_mapping": out_dir / "observation_mapping.csv",
        "observability_baseline_by_observer": out_dir / "observability_baseline_by_observer.csv",
        "declared_recovery_by_observer": out_dir / "declared_recovery_by_observer.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["observer_manifest"], observer_rows)
    write_csv(artifacts["output_manifest"], output_rows)
    write_csv(artifacts["observation_mapping"], observation_rows)
    write_csv(artifacts["observability_baseline_by_observer"], baseline_rows)
    write_csv(artifacts["declared_recovery_by_observer"], recovery_rows)
    write_csv(artifacts["baseline_comparison"], comparison_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def observer_definitions() -> dict[str, Observer]:
    return {
        DECLARED_OBSERVER: {state: state[0] for state in STATES},
        NUISANCE_OBSERVER: {state: state[1] for state in STATES},
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


def observer_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "observer_id": DECLARED_OBSERVER,
            "observer_role": "declared_recovery_positive",
            "observation_rule": "emit source coordinate d",
        },
        {
            "witness_id": WITNESS_ID,
            "observer_id": NUISANCE_OBSERVER,
            "observer_role": "matched_observation_rank_control",
            "observation_rule": "emit source coordinate n",
        },
    ]


def output_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "output_id": output,
            "description": "binary observer output",
        }
        for output in OUTPUTS
    ]


def observation_mapping_rows(observers: dict[str, Observer]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for observer_id, observer in observers.items():
        for state in STATES:
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "observer_id": observer_id,
                    "state_id": state,
                    "state_d": state[0],
                    "state_n": state[1],
                    "output_id": observer[state],
                }
            )
    return rows


def observability_baseline_rows(observers: dict[str, Observer]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for observer_id, observer in observers.items():
        blocks = output_blocks(observer)
        block_sizes = sorted(len(members) for members in blocks.values())
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "observer_id": observer_id,
                "state_count": len(STATES),
                "output_support_size": len(blocks),
                "output_support": ";".join(sorted(blocks)),
                "finite_observation_rank": 1,
                "observation_block_count": len(blocks),
                "observation_block_size_signature": ";".join(str(size) for size in block_sizes),
                "output_to_state_count_signature": signature(
                    {output: len(members) for output, members in blocks.items()}
                ),
                "deterministic_observer": 1,
            }
        )
    return rows


def declared_recovery_rows(observers: dict[str, Observer]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for observer_id, observer in observers.items():
        recovery = declared_d_recovery(observer)
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "observer_id": observer_id,
                "declared_source_distinction_id": "D_d",
                "declared_observation_contract": "binary output must recover source coordinate d",
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


def baseline_comparison_rows(
    baseline_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    declared = row_by_observer(baseline_rows, DECLARED_OBSERVER)
    nuisance = row_by_observer(baseline_rows, NUISANCE_OBSERVER)
    matched_metrics = [
        "state_count",
        "output_support_size",
        "output_support",
        "finite_observation_rank",
        "observation_block_count",
        "observation_block_size_signature",
        "output_to_state_count_signature",
        "deterministic_observer",
    ]
    rows = [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "declared_observer_value": declared[metric],
            "nuisance_observer_value": nuisance[metric],
            "expected_relation": "matched",
            "relation_holds": int(declared[metric] == nuisance[metric]),
        }
        for metric in matched_metrics
    ]
    rows.append(
        {
            "witness_id": WITNESS_ID,
            "metric": "declared_recovery_signature",
            "declared_observer_value": recovery_signature(recovery_rows, DECLARED_OBSERVER),
            "nuisance_observer_value": recovery_signature(recovery_rows, NUISANCE_OBSERVER),
            "expected_relation": "different",
            "relation_holds": int(
                recovery_signature(recovery_rows, DECLARED_OBSERVER)
                != recovery_signature(recovery_rows, NUISANCE_OBSERVER)
            ),
        }
    )
    return rows


def witness_summary(
    *,
    baseline_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
) -> dict[str, object]:
    baseline_controls_hold = all(
        int(row["relation_holds"]) == 1
        for row in comparison_rows
        if row["expected_relation"] == "matched"
    )
    recovery = {row["observer_id"]: row for row in recovery_rows}
    declared_recovers = bool(int(recovery[DECLARED_OBSERVER]["exact_declared_recovery"]))
    nuisance_recovers = bool(int(recovery[NUISANCE_OBSERVER]["exact_declared_recovery"]))
    all_expected_relations_hold = all(int(row["relation_holds"]) == 1 for row in comparison_rows)

    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "state_count": len(STATES),
        "observer_count": 2,
        "declared_source_distinction_id": "D_d",
        "baseline_controls_hold": baseline_controls_hold,
        "all_expected_relations_hold": all_expected_relations_hold,
        "declared_observer_id": DECLARED_OBSERVER,
        "nuisance_observer_id": NUISANCE_OBSERVER,
        "finite_observation_rank": 1,
        "declared_observer_exact_declared_recovery": declared_recovers,
        "nuisance_observer_exact_declared_recovery": nuisance_recovers,
        "witness_status": (
            "same_observation_rank_different_declared_recovery"
            if (
                baseline_controls_hold
                and declared_recovers
                and not nuisance_recovers
                and all_expected_relations_hold
            )
            else "witness_failed"
        ),
        "not_claimed": [
            "full linear observability",
            "control synthesis",
            "semantic recovery",
            "value detection",
            "agency detection",
            "identity detection",
            "Omega validation",
            "substrate-general theory validation",
        ],
        "baseline_rows_digest": stable_hash(baseline_rows, length=24),
        "recovery_rows_digest": stable_hash(recovery_rows, length=24),
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Observation Rank, Different Declared Recovery Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Observation Baseline

```text
state_count: {summary["state_count"]}
observer_count: {summary["observer_count"]}
finite_observation_rank: {summary["finite_observation_rank"]}
baseline_controls_hold: {summary["baseline_controls_hold"]}
all_expected_relations_hold: {summary["all_expected_relations_hold"]}
```

Both observers are deterministic one-bit observers with the same output support,
same observation block count, and same block-size signature.

## Declared Recovery

```text
declared_source_distinction_id: {summary["declared_source_distinction_id"]}
declared_observer_id: {summary["declared_observer_id"]}
nuisance_observer_id: {summary["nuisance_observer_id"]}
declared_observer_exact_declared_recovery: {summary["declared_observer_exact_declared_recovery"]}
nuisance_observer_exact_declared_recovery: {summary["nuisance_observer_exact_declared_recovery"]}
```

## Read

Finite observation-rank and partition-shape summaries do not determine declared
distinction recovery.

## Not Claimed

```text
full linear observability
control synthesis
semantic recovery
value detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
"""


def output_blocks(observer: Observer) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    for state, output in observer.items():
        blocks.setdefault(output, []).append(state)
    return blocks


def declared_d_recovery(observer: Observer) -> dict[str, object]:
    output_sources: dict[str, set[str]] = {}
    for state, output in observer.items():
        output_sources.setdefault(output, set()).add(state[0])

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


def row_by_observer(rows: list[dict[str, object]], observer_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["observer_id"] == observer_id]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {observer_id}, found {len(matches)}")
    return matches[0]


def recovery_signature(rows: list[dict[str, object]], observer_id: str) -> str:
    row = row_by_observer(rows, observer_id)
    return f"{observer_id}:{row['exact_declared_recovery']}:{row['output_to_source_labels']}"


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


if __name__ == "__main__":
    main()
