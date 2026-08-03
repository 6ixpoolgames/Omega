"""Retained validation runner for process-interface identifiability v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.process_interface_identifiability_v0 import (
    identification_result_rows,
    independence_census_rows,
    independence_witness_rows,
    influence_edge_rows,
    interface_profile_rows,
    memory_injectivity_rows,
    negative_control_rows,
    process_interface_identifiability_summary,
)
from omega_v2.validation.artifacts import (
    timestamped_output_dir,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite process-interface identifiability v0."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/process_interface_identifiability_v0"),
    )
    return parser.parse_args()


def run_process_interface_identifiability_v0(
    *,
    out_root: Path = Path(".tmp/process_interface_identifiability_v0"),
) -> dict[str, Any]:
    return retain_process_interface_identifiability_v0(
        timestamped_output_dir(out_root)
    )


def retain_process_interface_identifiability_v0(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    complete_summary = process_interface_identifiability_summary()
    public_summary = {
        key: value
        for key, value in complete_summary.items()
        if key != "_objects"
    }
    result = {"run_root": str(out_dir), **public_summary}

    write_json(out_dir / "summary.json", result)
    write_csv(
        out_dir / "interface_profiles.csv",
        interface_profile_rows(complete_summary),
    )
    write_csv(
        out_dir / "identification_results.csv",
        identification_result_rows(complete_summary),
    )
    write_csv(
        out_dir / "influence_edges.csv",
        influence_edge_rows(complete_summary),
    )
    write_csv(
        out_dir / "independence_census.csv",
        independence_census_rows(complete_summary),
    )
    write_csv(
        out_dir / "independence_witnesses.csv",
        independence_witness_rows(complete_summary),
    )
    write_csv(
        out_dir / "negative_controls.csv",
        negative_control_rows(complete_summary),
    )
    write_csv(
        out_dir / "memory_injectivity.csv",
        memory_injectivity_rows(complete_summary),
    )
    (out_dir / "report.md").write_text(
        render_report(result),
        encoding="utf-8",
    )
    return result


def render_report(result: dict[str, Any]) -> str:
    identification = result["identification"]
    nonidentifiability = result["observational_nonidentifiability"]
    census = result["independence_census"]
    memory = result["memory_injectivity"]
    lines = [
        "# Omega v2 Process Interface Identifiability v0 Validation",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        f"Horizon: {result['horizon']}",
        "",
        "## Primary Query",
        "",
        f"- Query: {result['primary_query']['query_id']}",
        (
            "- Required features: "
            + ", ".join(result["primary_query"]["required_true"])
        ),
        "",
        "## Identification Controls",
        "",
        (
            "- Observational status: "
            f"{identification['observational_result']['status']}"
        ),
        (
            "- Interventional status: "
            f"{identification['identified_result']['status']}"
        ),
        (
            "- Interventional minimal interfaces: "
            f"{identification['identified_result']['retained_minimal_interfaces']}"
        ),
        (
            "- Symmetric status: "
            f"{identification['set_identified_result']['status']}"
        ),
        (
            "- Symmetric minimal interfaces: "
            f"{identification['set_identified_result']['retained_minimal_interfaces']}"
        ),
        (
            "- Annotation invariant: "
            f"{identification['annotation_invariant']}"
        ),
        (
            "- Component-renaming covariant: "
            f"{identification['renaming_covariant']}"
        ),
        f"- Feature dependent: {identification['feature_dependent']}",
        "",
        "## Negative Controls",
        "",
        (
            "- Common-driver descendants correlated: "
            f"{result['common_driver']['descendants_correlated']}"
        ),
        (
            "- Common-driver descendant edge absent: "
            f"{result['common_driver']['descendant_edge_absent']}"
        ),
        (
            "- Copied record tracks source update: "
            f"{result['copied_record']['copy_tracks_source_update']}"
        ),
        (
            "- Copied record has outgoing influence: "
            f"{result['copied_record']['copy_outgoing_influence']}"
        ),
        (
            "- Copied record primary-certified: "
            f"{result['copied_record']['copy_primary_certified']}"
        ),
        "",
        "## Observational Non-identifiability",
        "",
        (
            "- Observationally equivalent: "
            f"{nonidentifiability['observationally_equivalent']}"
        ),
        (
            "- Interventionally equivalent: "
            f"{nonidentifiability['interventionally_equivalent']}"
        ),
        (
            "- Left observational status: "
            f"{nonidentifiability['observational_status_left']}"
        ),
        (
            "- Right observational status: "
            f"{nonidentifiability['observational_status_right']}"
        ),
        (
            "- Interventional inside profiles differ: "
            f"{nonidentifiability['inside_interventional_profiles_differ']}"
        ),
        "",
        "## Exact Independence Census",
        "",
        (
            "- Enumerated systems: "
            f"{census['enumerated_rule_count']}/"
            f"{census['expected_rule_count']}"
        ),
        f"- Joint signatures: {census['joint_signature_count']}",
        (
            "- Record-acquisition conjunction holds: "
            f"{census['record_acquisition_composite_holds']}"
        ),
        f"- Manifest digest: `{census['manifest_digest']}`",
        "",
    ]
    lines.extend(
        (
            f"- {feature}: {details['verdict']} "
            f"(true={details['true_count']}, "
            f"false={details['false_count']}, "
            f"witness={details['witness_codes']})"
        )
        for feature, details in census["feature_results"].items()
    )
    lines.extend(
        [
            "",
            "## Memory Injectivity",
            "",
            (
                "- Copy update conditionally injective: "
                f"{memory['copy_update']['conditionally_injective']}"
            ),
            (
                "- Copy closed-loop image: "
                f"{memory['copy_closed_loop']['image_size']}/"
                f"{memory['copy_closed_loop']['state_count']}"
            ),
            (
                "- XOR update conditionally injective: "
                f"{memory['xor_update']['conditionally_injective']}"
            ),
            (
                "- XOR closed-loop image: "
                f"{memory['xor_closed_loop']['image_size']}/"
                f"{memory['xor_closed_loop']['state_count']}"
            ),
            "",
            "## Case Results",
            "",
        ]
    )
    lines.extend(
        f"- {case}: {passed}"
        for case, passed in result["case_results"].items()
    )
    lines.extend(["", "## Kill Conditions", ""])
    lines.extend(
        f"- {condition}: {fired}"
        for condition, fired in result["kill_conditions"].items()
    )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
            "",
            (
                "These are finite, feature-relative interface results. The "
                "analyzer does not classify an interface as an agent, valuer, "
                "patient, or morally licensed object."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_process_interface_identifiability_v0(
        out_root=args.out_root
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
