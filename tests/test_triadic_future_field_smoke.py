from __future__ import annotations

from types import SimpleNamespace

from omega.future_field_atlas.generator import build_generated_conditions
from omega.future_field_atlas.run_triadic_future_field_smoke import build_triadic_tasks
from omega.future_field_atlas.triadic import scan_triadic_probe


def test_triadic_profile_smoke_completes() -> None:
    conditions_a = build_conditions("rank_prefix:m=3", 71_001)
    conditions_b = build_conditions("rank_subset:m=4:retain=1|2|3:remove=4", 571_001)
    conditions_c = build_conditions("rank_prefix:m=3", 971_001)
    args = SimpleNamespace(
        triple_count=1,
        start_samples=1,
        horizon_max=2,
        joint_effective_out_degree=6,
        coupling_strength=0.25,
        max_internal_joint_frontier_states=50_000,
    )

    task = build_triadic_tasks(args, conditions_a, conditions_b, conditions_c)[0]
    result = scan_triadic_probe(task)

    assert result.profile_rows
    assert result.residual_rows
    assert not result.internal_cap_rows
    assert {row["joint_scan_mode"] for row in result.profile_rows} == {"product_baseline", "triadic"}


def build_conditions(selection_operator: str, base_seed: int):
    return build_generated_conditions(
        groups=1,
        fresh_seeds_per_group=1,
        selection_operators=(selection_operator,),
        macro_invariant_kind="symbol_histogram_distance",
        macro_invariant_betas=(0.10,),
        rank_boundary_k=3,
        base_seed=base_seed,
    )
