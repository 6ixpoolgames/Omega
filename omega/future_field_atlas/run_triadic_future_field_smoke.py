"""Run a short three-frontier Future Field Atlas infrastructure smoke."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from .contracts import instrument_metadata
from .generator import build_generated_conditions, select_start_states
from .triadic import TriadicProbeTask, scan_triadic_probe
from .util import safe_token, utc_now, write_csv, write_json


TRIADIC_CLAIM_BOUNDARY = (
    "triadic infrastructure smoke only: profile-level product and triadic future-field "
    "frontier counts; no Omega, agency, identity, valuerhood, value, interaction, or causal claim"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a short triadic Future Field Atlas smoke.")
    parser.add_argument("--out", type=Path, default=Path("results/future_field_atlas/triadic_smoke"))
    parser.add_argument("--groups", type=int, default=1)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=1)
    parser.add_argument("--base-seed", type=int, default=71_001)
    parser.add_argument("--field-b-seed-offset", type=int, default=500_000)
    parser.add_argument("--field-c-seed-offset", type=int, default=900_000)
    parser.add_argument("--triple-count", type=int, default=1)
    parser.add_argument("--start-samples", type=int, default=1)
    parser.add_argument("--horizon-max", type=int, default=6)
    parser.add_argument("--macro-invariant-kind", type=str, default="symbol_histogram_distance")
    parser.add_argument("--macro-invariant-beta-list", type=str, default="0.10")
    parser.add_argument("--rank-boundary-k", type=int, default=3)
    parser.add_argument("--selection-operator-a", type=str, default="rank_prefix:m=3")
    parser.add_argument("--selection-operator-b", type=str, default="rank_subset:m=4:retain=1|2|3:remove=4")
    parser.add_argument("--selection-operator-c", type=str, default="rank_prefix:m=3")
    parser.add_argument("--joint-effective-out-degree", type=int, default=6)
    parser.add_argument("--coupling-strength", type=float, default=0.25)
    parser.add_argument("--max-internal-joint-frontier-states", type=int, default=50_000)
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_perf = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    macro_betas = tuple(parse_float_list(args.macro_invariant_beta_list) or [0.10])
    config = {
        **instrument_metadata(),
        "claim_boundary": TRIADIC_CLAIM_BOUNDARY,
        **vars(args),
        "macro_invariant_betas": list(macro_betas),
        "raw_topology_retention": "not_emitted_profile_only_smoke",
    }
    write_json(args.out / "triadic_future_field_smoke_config.json", config)
    conditions_a = build_generated_conditions(
        groups=args.groups,
        fresh_seeds_per_group=args.fresh_seeds_per_group,
        selection_operators=(args.selection_operator_a,),
        macro_invariant_kind=args.macro_invariant_kind,
        macro_invariant_betas=macro_betas,
        rank_boundary_k=args.rank_boundary_k,
        base_seed=args.base_seed,
    )
    conditions_b = build_generated_conditions(
        groups=args.groups,
        fresh_seeds_per_group=args.fresh_seeds_per_group,
        selection_operators=(args.selection_operator_b,),
        macro_invariant_kind=args.macro_invariant_kind,
        macro_invariant_betas=macro_betas,
        rank_boundary_k=args.rank_boundary_k,
        base_seed=args.base_seed + args.field_b_seed_offset,
    )
    conditions_c = build_generated_conditions(
        groups=args.groups,
        fresh_seeds_per_group=args.fresh_seeds_per_group,
        selection_operators=(args.selection_operator_c,),
        macro_invariant_kind=args.macro_invariant_kind,
        macro_invariant_betas=macro_betas,
        rank_boundary_k=args.rank_boundary_k,
        base_seed=args.base_seed + args.field_c_seed_offset,
    )
    tasks = build_triadic_tasks(args, conditions_a, conditions_b, conditions_c)
    results = [scan_triadic_probe(task) for task in tasks]
    profile_rows = [row for result in results for row in result.profile_rows]
    residual_rows = [row for result in results for row in result.residual_rows]
    cap_rows = [row for result in results for row in result.internal_cap_rows]
    write_csv(args.out / "triadic_frontier_profile_by_horizon.csv.gz", profile_rows, gzip_compresslevel=args.gzip_compresslevel)
    write_csv(args.out / "triadic_joint_vs_product_residual_by_horizon.csv.gz", residual_rows, gzip_compresslevel=args.gzip_compresslevel)
    write_csv(args.out / "triadic_internal_frontier_cap_events.csv.gz", cap_rows, gzip_compresslevel=args.gzip_compresslevel)
    status = {
        **instrument_metadata(),
        "claim_boundary": TRIADIC_CLAIM_BOUNDARY,
        "status": "COMPLETED",
        "completed_utc": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - started_perf, 3),
        "triple_count_requested": args.triple_count,
        "triple_count_completed": len(results),
        "horizon_max": args.horizon_max,
        "profile_rows": len(profile_rows),
        "residual_rows": len(residual_rows),
        "internal_cap_events": len(cap_rows),
        "artifact_completeness_statuses": ",".join(sorted({str(row["feature_status"]) for row in profile_rows + residual_rows})),
        "raw_topology_retention": "not_emitted_profile_only_smoke",
    }
    write_json(args.out / "triadic_future_field_smoke_status.json", status)
    write_report(args.out, status, profile_rows, residual_rows)


def build_triadic_tasks(
    args: argparse.Namespace,
    conditions_a: list[object],
    conditions_b: list[object],
    conditions_c: list[object],
) -> list[TriadicProbeTask]:
    tasks: list[TriadicProbeTask] = []
    triple_limit = min(max(1, args.triple_count), len(conditions_a), len(conditions_b), len(conditions_c))
    horizon_schedule = tuple(range(args.horizon_max + 1))
    for triple_index in range(triple_limit):
        field_a = conditions_a[triple_index]
        field_b = conditions_b[triple_index]
        field_c = conditions_c[triple_index]
        starts_a = select_start_states(field_a, args.start_samples)  # type: ignore[arg-type]
        starts_b = select_start_states(field_b, args.start_samples)  # type: ignore[arg-type]
        starts_c = select_start_states(field_c, args.start_samples)  # type: ignore[arg-type]
        for start_index, (start_a, start_b, start_c) in enumerate(zip(starts_a, starts_b, starts_c)):
            triple_id = (
                f"triple{triple_index:03d}__A_{safe_token(field_a.spec.condition_id)}"  # type: ignore[attr-defined]
                f"__B_{safe_token(field_b.spec.condition_id)}"  # type: ignore[attr-defined]
                f"__C_{safe_token(field_c.spec.condition_id)}__start{start_index:02d}"  # type: ignore[attr-defined]
            )
            tasks.append(
                TriadicProbeTask(
                    triple_id=triple_id,
                    field_a=field_a,  # type: ignore[arg-type]
                    field_b=field_b,  # type: ignore[arg-type]
                    field_c=field_c,  # type: ignore[arg-type]
                    start_a=start_a,
                    start_b=start_b,
                    start_c=start_c,
                    horizon_schedule=horizon_schedule,
                    horizon_max=args.horizon_max,
                    joint_effective_out_degree=max(1, args.joint_effective_out_degree),
                    coupling_strength=float(args.coupling_strength),
                    max_internal_joint_frontier_states=max(1, args.max_internal_joint_frontier_states),
                )
            )
    return tasks


def write_report(
    out_dir: Path,
    status: dict[str, object],
    profile_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
) -> None:
    terminal_horizon = max((int(row["horizon"]) for row in profile_rows), default=0)
    terminal_profile = [row for row in profile_rows if int(row["horizon"]) == terminal_horizon]
    terminal_residual = [row for row in residual_rows if int(row["horizon"]) == terminal_horizon]
    lines = [
        "# Triadic Future Field Smoke",
        "",
        f"Status: {status.get('status', '')}",
        f"Elapsed seconds: {status.get('elapsed_seconds', '')}",
        "",
        f"Claim boundary: {TRIADIC_CLAIM_BOUNDARY}",
        "",
        "This is a profile-only infrastructure smoke. It does not emit full raw triadic node or edge topology.",
        "",
        "## Counts",
        "",
        f"- Triples completed: `{status.get('triple_count_completed', '')}` / `{status.get('triple_count_requested', '')}`",
        f"- Horizon max: `{status.get('horizon_max', '')}`",
        f"- Profile rows: `{status.get('profile_rows', '')}`",
        f"- Residual rows: `{status.get('residual_rows', '')}`",
        f"- Internal cap events: `{status.get('internal_cap_events', '')}`",
        f"- Artifact completeness statuses: `{status.get('artifact_completeness_statuses', '')}`",
        "",
        "## Terminal Profile",
        "",
        *[
            (
                f"- `{row['joint_scan_mode']}` H{row['horizon']}: "
                f"{row['joint_frontier_state_count']} joint states, "
                f"density {float(row['joint_density_vs_marginal_product']):.4f}"
            )
            for row in terminal_profile
        ],
        "",
        "## Terminal Residual",
        "",
        *[
            (
                f"- H{row['horizon']}: product {row['product_joint_support_count']}, "
                f"triadic {row['triadic_joint_support_count']}, "
                f"residual {float(row['joint_support_residual_fraction']):.4f}"
            )
            for row in terminal_residual
        ],
    ]
    (out_dir / "triadic_future_field_smoke_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_float_list(raw: str) -> list[float]:
    return [float(item.strip()) for item in str(raw or "").split(",") if item.strip()]


if __name__ == "__main__":
    main()
