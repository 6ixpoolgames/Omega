"""Same viability kernel, different declared recovery witness.

This exact finite witness compares two deterministic one-step systems over the
same four-state carrier. Both systems have the same declared finite viability
kernel and the same source-to-target viability signature. Only one recovers the
declared source distinction from the declared recovery observation.

It does not claim real-world viability, optimal control, control synthesis,
semantic recovery, value, agency, identity, Omega, or substrate-general
transfer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from omega.future_field_atlas.util import stable_hash, write_csv, write_json


DEFAULT_OUT = Path(
    "results/baseline_witnesses/20260611_same_viability_kernel_different_declared_recovery_v0"
)
WITNESS_ID = "same_viability_kernel_different_declared_recovery_v0"
SCHEMA_VERSION = "0.1.0"
CARRIER_ID = "X2_dn_viability_kernel"
STATES = ("00", "01", "10", "11")
DECLARED_SYSTEM = "kernel_with_declared_d_carried"
NUISANCE_SYSTEM = "kernel_with_nuisance_n_carried"

System = dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the same-viability-kernel/different-declared-recovery witness."
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_witness(out_dir=args.out)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_witness(*, out_dir: Path = DEFAULT_OUT) -> dict[str, object]:
    systems = system_definitions()
    state_rows = state_manifest_rows()
    system_rows = system_manifest_rows()
    transition_rows = transition_rows_by_system(systems)
    kernel_rows = viability_kernel_rows(systems)
    recovery_rows = declared_recovery_rows(systems)
    comparison_rows = baseline_comparison_rows(kernel_rows, recovery_rows)
    summary = witness_summary(
        kernel_rows=kernel_rows,
        recovery_rows=recovery_rows,
        comparison_rows=comparison_rows,
    )

    artifacts = {
        "state_manifest": out_dir / "state_manifest.csv",
        "system_manifest": out_dir / "system_manifest.csv",
        "transition_edges": out_dir / "transition_edges.csv",
        "viability_kernel_by_system": out_dir / "viability_kernel_by_system.csv",
        "declared_recovery_by_system": out_dir / "declared_recovery_by_system.csv",
        "baseline_comparison": out_dir / "baseline_comparison.csv",
        "witness_summary": out_dir / "witness_summary.json",
        "witness_report": out_dir / "witness_report.md",
    }

    write_csv(artifacts["state_manifest"], state_rows)
    write_csv(artifacts["system_manifest"], system_rows)
    write_csv(artifacts["transition_edges"], transition_rows)
    write_csv(artifacts["viability_kernel_by_system"], kernel_rows)
    write_csv(artifacts["declared_recovery_by_system"], recovery_rows)
    write_csv(artifacts["baseline_comparison"], comparison_rows)
    write_json(artifacts["witness_summary"], summary)
    artifacts["witness_report"].write_text(report_text(summary), encoding="utf-8")

    return {
        **summary,
        "out_dir": str(out_dir),
        "artifact_paths": {key: str(path) for key, path in artifacts.items()},
    }


def system_definitions() -> dict[str, System]:
    return {
        DECLARED_SYSTEM: {source: source[0] + source[0] for source in STATES},
        NUISANCE_SYSTEM: {source: source[0] + source[1] for source in STATES},
    }


def state_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "carrier_id": CARRIER_ID,
            "state_id": state,
            "d": state[0],
            "n": state[1],
            "declared_viable": int(is_viable(state)),
        }
        for state in STATES
    ]


def system_manifest_rows() -> list[dict[str, object]]:
    return [
        {
            "witness_id": WITNESS_ID,
            "system_id": DECLARED_SYSTEM,
            "system_role": "declared_recovery_positive",
            "transition_rule": "target viability bit = source d; target recovery bit = source d",
        },
        {
            "witness_id": WITNESS_ID,
            "system_id": NUISANCE_SYSTEM,
            "system_role": "matched_viability_kernel_control",
            "transition_rule": "target viability bit = source d; target recovery bit = source n",
        },
    ]


def transition_rows_by_system(systems: dict[str, System]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for system_id, system in systems.items():
        for source in STATES:
            target = system[source]
            rows.append(
                {
                    "witness_id": WITNESS_ID,
                    "carrier_id": CARRIER_ID,
                    "system_id": system_id,
                    "source_state": source,
                    "target_state": target,
                    "source_d": source[0],
                    "source_n": source[1],
                    "source_declared_viable": int(is_viable(source)),
                    "target_declared_viable": int(is_viable(target)),
                    "target_recovery_bit": target[1],
                    "edge_weight": 1,
                }
            )
    return rows


def viability_kernel_rows(systems: dict[str, System]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for system_id, system in systems.items():
        kernel_sources = [source for source in STATES if is_viable(system[source])]
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "system_id": system_id,
                "source_count": len(STATES),
                "transition_edge_count": len(STATES),
                "deterministic_transition": 1,
                "declared_viability_predicate": "state first bit d = 1",
                "viability_kernel_size": len(kernel_sources),
                "viability_kernel_signature": ";".join(kernel_sources),
                "source_to_target_viability_signature": source_to_target_viability(system),
                "source_viability_signature": source_viability_signature(),
            }
        )
    return rows


def declared_recovery_rows(systems: dict[str, System]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for system_id, system in systems.items():
        recovery = declared_d_recovery(system)
        rows.append(
            {
                "witness_id": WITNESS_ID,
                "carrier_id": CARRIER_ID,
                "system_id": system_id,
                "declared_source_distinction_id": "D_d",
                "declared_target_observation_id": "target_recovery_bit",
                "declared_contract": "target recovery bit must recover source coordinate d",
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


def baseline_comparison_rows(
    kernel_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    declared = row_by_system(kernel_rows, DECLARED_SYSTEM)
    nuisance = row_by_system(kernel_rows, NUISANCE_SYSTEM)
    matched_metrics = [
        "source_count",
        "transition_edge_count",
        "deterministic_transition",
        "declared_viability_predicate",
        "viability_kernel_size",
        "viability_kernel_signature",
        "source_to_target_viability_signature",
        "source_viability_signature",
    ]
    rows = [
        {
            "witness_id": WITNESS_ID,
            "metric": metric,
            "declared_system_value": declared[metric],
            "nuisance_system_value": nuisance[metric],
            "expected_relation": "matched",
            "relation_holds": int(declared[metric] == nuisance[metric]),
        }
        for metric in matched_metrics
    ]
    rows.append(
        {
            "witness_id": WITNESS_ID,
            "metric": "declared_recovery_signature",
            "declared_system_value": recovery_signature(recovery_rows, DECLARED_SYSTEM),
            "nuisance_system_value": recovery_signature(recovery_rows, NUISANCE_SYSTEM),
            "expected_relation": "different",
            "relation_holds": int(
                recovery_signature(recovery_rows, DECLARED_SYSTEM)
                != recovery_signature(recovery_rows, NUISANCE_SYSTEM)
            ),
        }
    )
    return rows


def witness_summary(
    *,
    kernel_rows: list[dict[str, object]],
    recovery_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
) -> dict[str, object]:
    kernel_controls_hold = all(
        int(row["relation_holds"]) == 1
        for row in comparison_rows
        if row["expected_relation"] == "matched"
    )
    recovery = {row["system_id"]: row for row in recovery_rows}
    declared_recovers = bool(int(recovery[DECLARED_SYSTEM]["exact_declared_recovery"]))
    nuisance_recovers = bool(int(recovery[NUISANCE_SYSTEM]["exact_declared_recovery"]))
    all_expected_relations_hold = all(int(row["relation_holds"]) == 1 for row in comparison_rows)
    summary_payload = {
        "witness_id": WITNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "carrier_id": CARRIER_ID,
        "source_count": len(STATES),
        "system_count": 2,
        "declared_viability_predicate": "state first bit d = 1",
        "declared_source_distinction_id": "D_d",
        "declared_recovery_observation_id": "target_recovery_bit",
        "kernel_controls_hold": kernel_controls_hold,
        "all_expected_relations_hold": all_expected_relations_hold,
        "declared_system_id": DECLARED_SYSTEM,
        "nuisance_system_id": NUISANCE_SYSTEM,
        "viability_kernel_size": 2,
        "viability_kernel_signature": "10;11",
        "declared_system_exact_declared_recovery": declared_recovers,
        "nuisance_system_exact_declared_recovery": nuisance_recovers,
        "witness_status": (
            "same_viability_kernel_different_declared_recovery"
            if (
                kernel_controls_hold
                and declared_recovers
                and not nuisance_recovers
                and all_expected_relations_hold
            )
            else "witness_failed"
        ),
        "not_claimed": [
            "real-world viability",
            "optimal control",
            "control synthesis",
            "semantic recovery",
            "value detection",
            "agency detection",
            "identity detection",
            "Omega validation",
            "substrate-general theory validation",
        ],
        "kernel_rows_digest": stable_hash(kernel_rows, length=24),
        "recovery_rows_digest": stable_hash(recovery_rows, length=24),
        "comparison_rows_digest": stable_hash(comparison_rows, length=24),
    }
    summary_payload["summary_digest"] = stable_hash(summary_payload, length=24)
    return summary_payload


def report_text(summary: dict[str, object]) -> str:
    return f"""# Same Viability Kernel, Different Declared Recovery Witness

Witness ID: `{summary["witness_id"]}`

Status: `{summary["witness_status"]}`

## Controlled Viability-Kernel Baseline

```text
source_count: {summary["source_count"]}
system_count: {summary["system_count"]}
declared_viability_predicate: {summary["declared_viability_predicate"]}
viability_kernel_size: {summary["viability_kernel_size"]}
viability_kernel_signature: {summary["viability_kernel_signature"]}
kernel_controls_hold: {summary["kernel_controls_hold"]}
all_expected_relations_hold: {summary["all_expected_relations_hold"]}
```

Both systems have the same finite declared viability kernel and the same
source-to-target viability signature.

## Declared Recovery

```text
declared_source_distinction_id: {summary["declared_source_distinction_id"]}
declared_recovery_observation_id: {summary["declared_recovery_observation_id"]}
declared_system_id: {summary["declared_system_id"]}
nuisance_system_id: {summary["nuisance_system_id"]}
declared_system_exact_declared_recovery: {summary["declared_system_exact_declared_recovery"]}
nuisance_system_exact_declared_recovery: {summary["nuisance_system_exact_declared_recovery"]}
```

## Read

A matched finite viability-kernel summary does not determine declared recovery.

## Not Claimed

```text
real-world viability
optimal control
control synthesis
semantic recovery
value detection
agency detection
identity detection
Omega validation
substrate-general theory validation
```
"""


def declared_d_recovery(system: System) -> dict[str, object]:
    observation_sources: dict[str, set[str]] = {}
    for source in STATES:
        target = system[source]
        observation_sources.setdefault(target[1], set()).add(source[0])

    ambiguous = {
        observation: sorted(labels)
        for observation, labels in observation_sources.items()
        if len(labels) != 1
    }
    return {
        "exact_declared_recovery": not ambiguous and sorted(observation_sources) == ["0", "1"],
        "ambiguous_target_observations": ";".join(
            f"{observation}->{{{','.join(labels)}}}"
            for observation, labels in sorted(ambiguous.items())
        ),
        "observation_to_source_labels": ";".join(
            f"{observation}->{{{','.join(sorted(labels))}}}"
            for observation, labels in sorted(observation_sources.items())
        ),
    }


def is_viable(state: str) -> bool:
    return state[0] == "1"


def source_to_target_viability(system: System) -> str:
    values = {source: int(is_viable(system[source])) for source in STATES}
    return signature(values)


def source_viability_signature() -> str:
    values = {source: int(is_viable(source)) for source in STATES}
    return signature(values)


def row_by_system(rows: list[dict[str, object]], system_id: str) -> dict[str, object]:
    matches = [row for row in rows if row["system_id"] == system_id]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {system_id}, found {len(matches)}")
    return matches[0]


def recovery_signature(rows: list[dict[str, object]], system_id: str) -> str:
    row = row_by_system(rows, system_id)
    return f"{system_id}:{row['exact_declared_recovery']}:{row['observation_to_source_labels']}"


def signature(values: dict[str, object]) -> str:
    return ";".join(f"{key}:{values[key]}" for key in sorted(values))


if __name__ == "__main__":
    main()
