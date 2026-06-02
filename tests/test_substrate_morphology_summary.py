from __future__ import annotations

import json
from pathlib import Path

from omega.future_field_atlas.substrate_morphology_summary import RunRef, build_substrate_morphology_summary
from omega.future_field_atlas.util import read_csv, write_csv, write_json


def test_substrate_morphology_summary_emits_required_tables(tmp_path: Path) -> None:
    product = make_fake_coupled_run(tmp_path, "product_run", "product", 0.0, residual_final=0.0)
    zero = make_fake_coupled_run(tmp_path, "zero_run", "joint_energy_rank_prefix", 0.0, residual_final=0.25)
    positive = make_fake_coupled_run(tmp_path, "positive_run", "joint_energy_rank_prefix", 0.02, residual_final=0.75)

    out = tmp_path / "morphology"
    manifest = build_substrate_morphology_summary(
        out_dir=out,
        run_refs=[
            RunRef("product", product),
            RunRef("zero", zero),
            RunRef("positive", positive),
        ],
        include_existing_retention_summaries=True,
        write_report=True,
    )

    assert manifest["source_run_count"] == 3
    assert (out / "substrate_morphology_manifest.json").exists()
    assert (out / "substrate_morphology_report.md").exists()
    assert read_csv(out / "field_morphology_summary.csv")
    assert read_csv(out / "pair_morphology_summary.csv")
    assert read_csv(out / "operator_sensitivity_summary.csv")
    observable = read_csv(out / "observable_geometry_summary.csv")
    assert observable[0]["notes"].startswith("single_observable_only")
    targets = read_csv(out / "morphology_next_targets.csv")
    assert {row["target_type"] for row in targets} >= {"shared_capacity_candidate", "observable_extension"}


def make_fake_coupled_run(
    tmp_path: Path,
    name: str,
    joint_selection_family: str,
    coupling_strength: float,
    *,
    residual_final: float,
) -> Path:
    run = tmp_path / name
    run.mkdir()
    pair_id = "pair005__fake"
    write_json(
        run / "coupled_future_field_atlas_status.json",
        {
            "status": "COMPLETED",
            "coupled_pairs_failed": 0,
            "internal_cap_events": 0,
            "artifact_completeness_statuses": "complete",
            "reconstruction_audit_clean_pass": 1,
            "pair_count_realized": 1,
            "joint_edge_rows": 20,
            "joint_node_rows": 10,
        },
    )
    write_json(
        run / "coupled_future_field_atlas_run_config.json",
        {
            "horizon_max": 2,
            "joint_selection_family": joint_selection_family,
            "coupling_strength": coupling_strength,
            "macro_invariant_kind": "symbol_histogram_distance",
        },
    )
    write_csv(
        run / "coupled_operator_manifest.csv.gz",
        [
            {
                "coupled_operator_id": f"{joint_selection_family}_{coupling_strength}",
                "coupled_operator_family": "rank_boundary_mismatch_penalized_joint_selector",
                "coupling_strength": coupling_strength,
                "joint_selection_family": joint_selection_family,
            }
        ],
    )
    write_csv(
        run / "coupled_pair_spool_manifest.csv.gz",
        [{"pair_id": pair_id, "node_rows": 10, "edge_rows": 20}],
    )
    write_csv(
        run / "coupled_reconstruction_audit_summary.csv.gz",
        [{"audit_name": "profile", "status": "PASS", "checked_items": 2, "failed_items": 0, "skipped_items": 0}],
    )
    write_csv(
        run / "coupled_artifact_completeness_summary.csv.gz",
        [{"artifact_name": "profile", "artifact_status": "complete", "row_count": 2}],
    )
    write_csv(
        run / "coupled_joint_vs_product_residual_by_horizon.csv.gz",
        [
            residual_row(pair_id, 0, 0.0),
            residual_row(pair_id, 1, residual_final / 2),
            residual_row(pair_id, 2, residual_final),
        ],
    )
    write_csv(
        run / "coupled_marginal_retention_by_horizon.csv.gz",
        [
            marginal_row(pair_id, 0, 1.0),
            marginal_row(pair_id, 1, 0.8),
            marginal_row(pair_id, 2, 1.0 - residual_final),
        ],
    )
    write_csv(
        run / "coupled_joint_frontier_profile_by_horizon.csv.gz",
        [
            profile_row(pair_id, "product_baseline", 0, 1, 1.0),
            profile_row(pair_id, "product_baseline", 1, 2, 1.0),
            profile_row(pair_id, "product_baseline", 2, 4, 1.0),
            profile_row(pair_id, "coupled", 0, 1, 1.0),
            profile_row(pair_id, "coupled", 1, 2, 0.8),
            profile_row(pair_id, "coupled", 2, 3, 0.25),
        ],
    )
    retention = run / "_retention_summary"
    retention.mkdir()
    (retention / "retained_run_summary.json").write_text(json.dumps({"total_output_size_gib": 0.001}), encoding="utf-8")
    write_csv(retention / "retained_pair_skew.csv.gz", [{"pair_id": pair_id, "spool_size_gib": 0.001}])
    return run


def residual_row(pair_id: str, horizon: int, residual: float) -> dict[str, object]:
    return {
        "pair_id": pair_id,
        "horizon": horizon,
        "feature_status": "complete",
        "product_joint_support_count": 100,
        "coupled_joint_support_count": int(100 * (1 - residual)),
        "joint_support_residual_fraction": residual,
    }


def marginal_row(pair_id: str, horizon: int, retention: float) -> dict[str, object]:
    return {
        "pair_id": pair_id,
        "horizon": horizon,
        "feature_status": "complete",
        "A_marginal_retention_fraction": 1.0,
        "B_marginal_retention_fraction": 1.0,
        "joint_retention_fraction": retention,
        "joint_product_state_count": 100,
        "joint_coupled_state_count": int(100 * retention),
    }


def profile_row(pair_id: str, mode: str, horizon: int, count: int, density: float) -> dict[str, object]:
    return {
        "pair_id": pair_id,
        "joint_scan_mode": mode,
        "horizon": horizon,
        "feature_status": "complete",
        "A_condition_id": "A",
        "B_condition_id": "B",
        "A_substrate_id": "AX",
        "B_substrate_id": "BX",
        "A_law_id": "law",
        "B_law_id": "law",
        "A_selection_operator_id": "rank_prefix",
        "B_selection_operator_id": "rank_subset",
        "start_index": 0,
        "joint_frontier_state_count": count,
        "joint_frontier_edge_count": count * 2,
        "A_marginal_state_count": count,
        "B_marginal_state_count": count,
        "marginal_product_state_count": count * count,
        "joint_density_vs_marginal_product": density,
    }
