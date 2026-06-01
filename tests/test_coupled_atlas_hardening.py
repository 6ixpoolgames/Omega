from __future__ import annotations

from types import SimpleNamespace

from omega.future_field_atlas.coupled import (
    build_coupled_operator_spec,
    coupled_operator_digest,
    scan_coupled_probe,
)
from omega.future_field_atlas.generator import build_generated_conditions
from omega.future_field_atlas.run_coupled_future_field_atlas import (
    audit_result,
    build_coupled_tasks,
    coupled_condition_manifest_rows,
    coupled_scan_manifest_rows,
    write_raw_topology_shards,
)
from omega.future_field_atlas.util import csv_row_count


def test_cap_poison_propagates_to_descendant_rows() -> None:
    task = build_test_tasks(
        horizon_max=3,
        max_internal_joint_frontier_states=1,
        max_joint_frontier_nodes_per_horizon=10_000,
        max_joint_edges_per_step=10_000,
    )[0]

    result = scan_coupled_probe(task)
    assert result.internal_cap_rows

    poisoned_profiles = [
        row
        for row in result.profile_rows
        if int(row["horizon"]) >= 1
    ]
    assert poisoned_profiles
    assert {row["feature_status"] for row in poisoned_profiles} == {"truncated_noninterpretable"}

    poisoned_marginal_rows = [
        row
        for row in result.marginal_rows
        if int(row["horizon"]) >= 1
    ]
    assert poisoned_marginal_rows
    assert {row["feature_status"] for row in poisoned_marginal_rows} == {"truncated_noninterpretable"}


def test_audit_statuses_distinguish_skipped_only_and_mixed_rows() -> None:
    assert audit_result("all_good", checked=2, failed=0, skipped=0)["status"] == "PASS"
    assert audit_result("mixed", checked=2, failed=0, skipped=3)["status"] == "PASS_WITH_SKIPS"
    assert audit_result("skipped_only", checked=0, failed=0, skipped=3)["status"] == "NO_COMPLETE_ROWS"
    assert audit_result("failed", checked=2, failed=1, skipped=3)["status"] == "FAIL"


def test_coupled_operator_digest_is_stable() -> None:
    left = build_coupled_operator_spec(
        joint_selection_family="joint_energy_rank_prefix",
        joint_effective_out_degree=4,
        coupling_strength=0.25,
    )
    right = build_coupled_operator_spec(
        joint_selection_family="joint_energy_rank_prefix",
        joint_effective_out_degree=4,
        coupling_strength=0.25,
    )
    assert left == right
    assert coupled_operator_digest(left) == coupled_operator_digest(right)


def test_pairing_policy_and_operator_identity_appear_in_manifests() -> None:
    task = build_test_tasks(horizon_max=1)[0]
    condition_rows = coupled_condition_manifest_rows([task])
    scan_rows = coupled_scan_manifest_rows([task])

    assert condition_rows[0]["condition_pairing_policy"] == "index_matched"
    assert condition_rows[0]["start_pairing_policy"] == "zip_selected_starts"
    assert condition_rows[0]["coupled_operator_id"] == task.coupled_operator.coupled_operator_id
    assert condition_rows[0]["coupled_operator_digest"] == coupled_operator_digest(task.coupled_operator)
    assert scan_rows[0]["condition_pairing_policy"] == "index_matched"
    assert scan_rows[0]["start_pairing_policy"] == "zip_selected_starts"


def test_marginal_projection_rows_do_not_claim_causality() -> None:
    task = build_test_tasks(horizon_max=1)[0]
    result = scan_coupled_probe(task)

    assert result.marginal_projection_rows
    assert {
        row["projection_semantics"]
        for row in result.marginal_projection_rows
    } == {"product_vs_coupled_marginal_set_delta"}
    assert {row["causal_interpretation"] for row in result.marginal_projection_rows} == {"none"}


def test_coupled_raw_topology_shards_are_manifest_backed(tmp_path) -> None:
    task = build_test_tasks(horizon_max=1)[0]
    result = scan_coupled_probe(task)

    node_manifest, edge_manifest = write_raw_topology_shards(
        out_dir=tmp_path,
        results=[result],
        csv_output_mode="gzip",
        shard_pair_count=1,
        gzip_compresslevel=1,
        artifact_write_workers=2,
    )

    assert len(node_manifest) == 1
    assert len(edge_manifest) == 1
    node_file = tmp_path / str(node_manifest[0]["physical_artifact_name"])
    edge_file = tmp_path / str(edge_manifest[0]["physical_artifact_name"])
    assert node_file.exists()
    assert edge_file.exists()
    assert csv_row_count(node_file) == len(result.node_rows)
    assert csv_row_count(edge_file) == len(result.edge_rows)
    assert node_manifest[0]["logical_artifact_name"] == "coupled_joint_frontier_nodes_by_horizon.csv"
    assert edge_manifest[0]["logical_artifact_name"] == "coupled_joint_frontier_edges_by_step.csv"


def build_test_tasks(
    *,
    horizon_max: int,
    max_internal_joint_frontier_states: int = 20_000,
    max_joint_frontier_nodes_per_horizon: int = 2048,
    max_joint_edges_per_step: int = 8192,
):
    conditions_a = build_generated_conditions(
        groups=1,
        fresh_seeds_per_group=1,
        selection_operators=("rank_prefix:m=3",),
        macro_invariant_kind="symbol_histogram_distance",
        macro_invariant_betas=(0.10,),
        rank_boundary_k=3,
        base_seed=61_001,
    )
    conditions_b = build_generated_conditions(
        groups=1,
        fresh_seeds_per_group=1,
        selection_operators=("rank_subset:m=4:retain=1|2|3:remove=4",),
        macro_invariant_kind="symbol_histogram_distance",
        macro_invariant_betas=(0.10,),
        rank_boundary_k=3,
        base_seed=561_001,
    )
    args = SimpleNamespace(
        pair_count=1,
        start_samples=1,
        horizon_max=horizon_max,
        joint_selection_family="joint_energy_rank_prefix",
        joint_effective_out_degree=4,
        coupling_strength=0.25,
        max_joint_frontier_nodes_per_horizon=max_joint_frontier_nodes_per_horizon,
        max_joint_edges_per_step=max_joint_edges_per_step,
        max_internal_joint_frontier_states=max_internal_joint_frontier_states,
    )
    return build_coupled_tasks(args, conditions_a, conditions_b, tuple(range(horizon_max + 1)))
