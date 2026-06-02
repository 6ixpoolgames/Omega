"""Visualization helpers for retained coupled Future Field Atlas outputs.

The figures produced here are compact-topology views. They use retained
summaries and horizon tables, not deleted raw node/edge spools.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib_cache").resolve()))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_MORPHOLOGY_DIR = Path("results/future_field_atlas/20260602_substrate_morphology_atlas_summary")
DEFAULT_RESULTS_ROOT = Path("results/future_field_atlas")
DEFAULT_FIGURE_DIR = Path(
    "docs/research_notes/validation_results/figures/future_field_atlas_rank_order_boundary"
)
DEFAULT_EXEMPLARS = ["pair005", "pair012", "pair014", "pair026"]
DEFAULT_CONTROLS = ["pair000", "pair001", "pair002", "pair045"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize retained coupled Future Field Atlas morphology summaries."
    )
    parser.add_argument("--morphology-dir", type=Path, default=DEFAULT_MORPHOLOGY_DIR)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_FIGURE_DIR)
    parser.add_argument(
        "--exemplars",
        default=",".join(DEFAULT_EXEMPLARS),
        help="Comma-separated high-yield pair IDs to highlight.",
    )
    parser.add_argument(
        "--controls",
        default=",".join(DEFAULT_CONTROLS),
        help="Comma-separated typical/control pair IDs to include.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    exemplars = split_ids(args.exemplars)
    controls = split_ids(args.controls)

    pair_df = pd.read_csv(args.morphology_dir / "pair_morphology_summary.csv")
    write_landscape_scatter(pair_df, args.out, exemplars=exemplars, controls=controls)
    write_metric_heatmap(pair_df, args.out, exemplars=exemplars, controls=controls)
    write_horizon_traces(args.results_root, args.out, exemplars=exemplars, controls=controls)
    write_visualization_note(args.out, exemplars=exemplars, controls=controls)


def split_ids(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def write_landscape_scatter(
    pair_df: pd.DataFrame, out_dir: Path, *, exemplars: list[str], controls: list[str]
) -> None:
    rank_df = pair_df[
        (pair_df["joint_selection_family"] == "rank_order_boundary")
        & (pair_df["artifact_completeness_status"] == "complete")
        & (pair_df["reconstruction_audit_status"] == "PASS")
    ].copy()
    rank_df["is_h128"] = rank_df["horizon_max"].astype(int).eq(128).astype(int)
    rank_df = (
        rank_df.sort_values(
            ["pair_id", "is_h128", "joint_support_residual_final", "horizon_max"],
            ascending=[True, False, False, False],
        )
        .drop_duplicates("pair_id", keep="first")
        .copy()
    )
    rank_df["log_product_support"] = np.log10(rank_df["product_joint_support_final"].clip(lower=1))

    fig, ax = plt.subplots(figsize=(10.5, 6.5), constrained_layout=True)
    colors = {
        "marginal_preserving": "#2f6f9f",
        "marginal_loss_B": "#c87533",
        "marginal_loss_both": "#8f3f71",
    }
    for cls, group in rank_df.groupby("marginal_retention_class"):
        ax.scatter(
            group["log_product_support"],
            group["joint_support_residual_final"],
            s=42,
            alpha=0.55,
            label=cls,
            color=colors.get(cls, "#6f6f6f"),
            edgecolor="none",
        )

    highlight = rank_df[rank_df["pair_id"].isin(exemplars + controls)].copy()
    label_offsets = {
        "pair005": (8, 9),
        "pair012": (8, -13),
        "pair014": (8, 9),
        "pair026": (8, -13),
        "pair000": (8, 7),
        "pair001": (8, -13),
        "pair002": (8, 7),
        "pair045": (8, 7),
    }
    for _idx, row in highlight.iterrows():
        is_exemplar = row["pair_id"] in exemplars
        ax.scatter(
            row["log_product_support"],
            row["joint_support_residual_final"],
            s=160 if is_exemplar else 100,
            facecolor="none",
            edgecolor="#111111" if is_exemplar else "#777777",
            linewidth=2.1 if is_exemplar else 1.3,
            zorder=5,
        )
        offset = label_offsets.get(str(row["pair_id"]), (5, 5))
        ax.annotate(
            str(row["pair_id"]),
            (row["log_product_support"], row["joint_support_residual_final"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=9,
            color="#111111" if is_exemplar else "#555555",
        )

    ax.axhline(0.5, color="#444444", linestyle="--", linewidth=1.0, alpha=0.7)
    ax.set_title("Rank-Order Boundary Landscape: Exemplars vs Typical Pairs")
    ax.set_xlabel("log10(product joint support at final horizon)")
    ax.set_ylabel("joint support residual at final horizon")
    ax.set_ylim(-0.02, min(1.02, max(0.9, rank_df["joint_support_residual_final"].max() + 0.08)))
    ax.grid(True, alpha=0.22, linewidth=0.7)
    ax.legend(title="marginal class", loc="upper right", frameon=False)
    savefig(fig, out_dir / "rank_order_boundary_landscape_scatter.png")


def write_metric_heatmap(
    pair_df: pd.DataFrame, out_dir: Path, *, exemplars: list[str], controls: list[str]
) -> None:
    rows = []
    selected_pairs = exemplars + controls
    for pair_id in selected_pairs:
        row = choose_representative_row(pair_df, pair_id)
        if row is not None:
            rows.append(row)
    if not rows:
        return
    selected = pd.DataFrame(rows)
    metrics = [
        "joint_support_residual_final",
        "joint_retention_final",
        "A_marginal_retention_final",
        "B_marginal_retention_final",
        "joint_density_vs_marginal_product_final",
    ]
    matrix = selected[metrics].astype(float).to_numpy()

    fig, ax = plt.subplots(figsize=(9.5, 4.8), constrained_layout=True)
    image = ax.imshow(matrix, aspect="auto", vmin=0.0, vmax=1.0, cmap="viridis")
    ax.set_title("Compact Topology Metrics: Exemplars vs Controls")
    ax.set_yticks(np.arange(len(selected)))
    ax.set_yticklabels(
        [
            f"{row.pair_id} H{int(row.horizon_max)}"
            for row in selected.itertuples(index=False)
        ]
    )
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels(
        [
            "residual",
            "joint retention",
            "A retention",
            "B retention",
            "density",
        ],
        rotation=35,
        ha="right",
    )
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            value = matrix[y, x]
            ax.text(
                x,
                y,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if value < 0.45 else "black",
            )
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    savefig(fig, out_dir / "rank_order_boundary_exemplar_metric_heatmap.png")


def choose_representative_row(pair_df: pd.DataFrame, pair_id: str) -> pd.Series | None:
    subset = pair_df[
        (pair_df["pair_id"] == pair_id)
        & (pair_df["joint_selection_family"] == "rank_order_boundary")
        & (pair_df["artifact_completeness_status"] == "complete")
        & (pair_df["reconstruction_audit_status"] == "PASS")
    ].copy()
    if subset.empty:
        return None
    subset["is_h128"] = subset["horizon_max"].astype(int).eq(128).astype(int)
    subset = subset.sort_values(
        ["is_h128", "joint_support_residual_final", "horizon_max"],
        ascending=[False, False, False],
    )
    return subset.iloc[0]


def write_horizon_traces(
    results_root: Path, out_dir: Path, *, exemplars: list[str], controls: list[str]
) -> None:
    run_dirs = [
        results_root / "20260602_rank_order_boundary_h128_pair005_depth",
        results_root / "20260602_rank_order_boundary_h128_neighbor_targets",
        results_root / "20260602_rank_order_boundary_h128_pair026_depth",
        results_root / "20260602_rank_order_boundary_h64_pair8_medium",
        results_root / "20260602_rank_order_boundary_h64_class_expansion_p24_47",
    ]
    frames: list[pd.DataFrame] = []
    for run_dir in run_dirs:
        path = run_dir / "coupled_joint_vs_product_residual_by_horizon.csv.gz"
        if path.exists():
            frame = pd.read_csv(path)
            frame["run_id"] = run_dir.name
            frame["short_pair_id"] = frame["pair_id"].astype(str).str.extract(r"^(pair\d+)", expand=False)
            frames.append(frame)
    if not frames:
        return
    data = pd.concat(frames, ignore_index=True)
    wanted = set(exemplars + controls)
    data = data[data["short_pair_id"].isin(wanted)].copy()
    if data.empty:
        return

    fig, ax = plt.subplots(figsize=(11, 6.8), constrained_layout=True)
    palette = {
        "pair005": "#9b2f2f",
        "pair012": "#6d3fa0",
        "pair014": "#c06f1f",
        "pair026": "#1f7f5f",
        "pair000": "#4f6f8f",
        "pair001": "#6f6f6f",
        "pair002": "#8a8a8a",
        "pair045": "#487c9f",
    }
    plotted: set[str] = set()
    for pair_id in exemplars + controls:
        subset = choose_trace(data, pair_id)
        if subset is None:
            continue
        is_exemplar = pair_id in exemplars
        ax.plot(
            subset["horizon"].astype(int),
            subset["joint_support_residual_fraction"].astype(float),
            label=pair_id,
            color=palette.get(pair_id, None),
            linewidth=2.4 if is_exemplar else 1.5,
            alpha=0.95 if is_exemplar else 0.65,
            linestyle="-" if is_exemplar else "--",
        )
        plotted.add(pair_id)
    if not plotted:
        return

    ax.axhline(0.5, color="#444444", linestyle="--", linewidth=1.0, alpha=0.7)
    ax.set_title("Joint Residual by Horizon: High-Yield Exemplars vs Typical Controls")
    ax.set_xlabel("horizon")
    ax.set_ylabel("joint support residual fraction")
    ax.set_ylim(-0.02, 0.9)
    ax.grid(True, alpha=0.22, linewidth=0.7)
    ax.legend(ncol=2, frameon=False)
    savefig(fig, out_dir / "rank_order_boundary_horizon_residual_traces.png")


def choose_trace(data: pd.DataFrame, pair_id: str) -> pd.DataFrame | None:
    subset = data[data["short_pair_id"] == pair_id].copy()
    if subset.empty:
        return None
    subset["horizon_max"] = subset.groupby("run_id")["horizon"].transform("max")
    max_horizon = subset["horizon_max"].max()
    best_runs = subset[subset["horizon_max"] == max_horizon]["run_id"].drop_duplicates().tolist()
    best_run = best_runs[0]
    return subset[subset["run_id"] == best_run].sort_values("horizon")


def write_visualization_note(out_dir: Path, *, exemplars: list[str], controls: list[str]) -> None:
    note = out_dir / "README.md"
    note.write_text(
        "\n".join(
            [
                "# Future Field Atlas Rank-Order Boundary Visualizations",
                "",
                "These figures visualize retained compact topology summaries, not deleted raw",
                "joint edge/node spools.",
                "",
                "Exemplars:",
                "",
                "```text",
                *exemplars,
                "```",
                "",
                "Typical/control comparisons:",
                "",
                "```text",
                *controls,
                "```",
                "",
                "Figures:",
                "",
                "- `rank_order_boundary_landscape_scatter.png`: final-horizon landscape scatter.",
                "- `rank_order_boundary_horizon_residual_traces.png`: residual-by-horizon traces.",
                "- `rank_order_boundary_exemplar_metric_heatmap.png`: compact metric heatmap.",
                "",
                "Claim boundary: visualization only; no Omega, agency, value, compatibility,",
                "support, capture, erasure, or interaction claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def savefig(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
