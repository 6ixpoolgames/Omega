from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_aggregate_csv(path: Path, rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, int, int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["family"]), str(row["policy"]), int(row["h"]), int(row["H"]), int(row["T"]))].append(row)
    aggregate: list[dict[str, object]] = []
    for (family, policy, h, H, T), items in sorted(groups.items()):
        aggregate.append(
            {
                "family": family,
                "policy": policy,
                "near_horizon": h,
                "continuation_horizon": H,
                "T": T,
                "n": len(items),
                "mean_global_lhr": mean(float(item["global_lhr"]) for item in items),
                "mean_local_lhr": mean(float(item["local_lhr"]) for item in items),
                "mean_divergence": mean(float(item["local_global_divergence"]) for item in items),
                "pseudo_omega_rate": mean(1.0 if item["pseudo_omega_flag"] else 0.0 for item in items),
                "mean_r0_initial": mean(float(item["r0_initial"]) for item in items),
                "mean_r0_final": mean(float(item["r0_final"]) for item in items),
                "mean_r1_fraction": mean(float(item["initial_r1"]["r1_fraction"]) for item in items),
                "mean_r1_future_r0": mean(float(item["initial_r1"]["mean_future_r0"]) for item in items),
                "mean_same_choice_rate": mean(float(item["R1_R0lookahead_same_choice_rate"]) for item in items),
                "mean_score_gap": mean(float(item["R1_R0lookahead_score_gap"]) for item in items),
                "mean_candidate_future_R0_variance": mean(float(item["candidate_future_R0_variance_mean"]) for item in items),
                "mean_candidate_R1_fraction": mean(float(item["candidate_R1_fraction_mean"]) for item in items),
                "mean_local_global_divergence": mean(float(item["local_global_divergence"]) for item in items),
                "mean_P_family_reachability_delta": mean(float(item["P_family_reachability_delta"]) for item in items),
            }
        )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0].keys()) if aggregate else [])
        if aggregate:
            writer.writeheader()
            writer.writerows(aggregate)
    return aggregate


def write_summary(path: Path, config: dict[str, object], aggregate: list[dict[str, object]]) -> None:
    by_family_policy: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in aggregate:
        by_family_policy[(str(row["family"]), str(row["policy"]))].append(row)

    lines = [
        "# VAL0-CT Smoke Summary",
        "",
        "This is a harness and workflow validation run for the VAL0-CT constructor task algebra probe.",
        "It is not evidence for full Omega.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps(config, indent=2, sort_keys=True),
        "```",
        "",
        "## Policy Means",
        "",
        "| family | policy | mean global LHR | mean local LHR | pseudo-Omega rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for (family, policy), rows in sorted(by_family_policy.items()):
        lines.append(
            "| {family} | {policy} | {global_lhr:.3f} | {local_lhr:.3f} | {pseudo:.3f} |".format(
                family=family,
                policy=policy,
                global_lhr=mean(float(row["mean_global_lhr"]) for row in rows),
                local_lhr=mean(float(row["mean_local_lhr"]) for row in rows),
                pseudo=mean(float(row["pseudo_omega_rate"]) for row in rows),
            )
        )
    lines.extend(
        [
            "",
            "## R1 / R0-Lookahead Diagnostics",
            "",
            "| family | policy | same-choice rate | score gap | candidate variance |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for (family, policy), rows in sorted(by_family_policy.items()):
        lines.append(
            "| {family} | {policy} | {same:.3f} | {gap:.3f} | {var:.3f} |".format(
                family=family,
                policy=policy,
                same=mean(float(row["mean_same_choice_rate"]) for row in rows),
                gap=mean(float(row["mean_score_gap"]) for row in rows),
                var=mean(float(row["mean_candidate_future_R0_variance"]) for row in rows),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- `low_resolution_dense` is expected to blur R0/R1 differences; that is diagnostic, not a theory failure.",
            "- `structured_asymmetric` is the first place R1 should begin to matter if the operationalization is useful.",
            "- `lock_in_seeded` is a negative diagnostic: local persistence can rise while global reachability falls.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
