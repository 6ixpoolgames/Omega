"""Plot horizon-transport response spectrograms from a local run directory.

The plots are diagnostic readouts for the current horizon-transport instrument:
they visualize response class, viscosity score, alignment, mass delta, and
saturation by horizon. They do not add scientific claims beyond the CSVs.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

MPL_CACHE_DIR = Path(".matplotlib-cache")
MPL_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR.resolve()))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap


RESPONSE_CLASS_ORDER = (
    "transport_stable",
    "transport_amplified_aligned",
    "transport_weakened",
    "transport_rerouted",
    "transport_reopens",
    "transport_collapses",
    "transport_control_equivalent",
    "transport_resolution_mismatch",
    "transport_response_underpowered",
)
RESPONSE_CLASS_COLORS = (
    "#4C956C",
    "#2F80ED",
    "#F2C94C",
    "#9B51E0",
    "#00A7A7",
    "#D64545",
    "#9E9E9E",
    "#222222",
    "#5A6472",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot horizon-transport response spectrograms from runner CSV outputs.")
    parser.add_argument("--run-dir", type=Path, required=True, help="Run output directory containing horizon_transport_*.csv files.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Figure output directory. Defaults to <run-dir>/figures.")
    parser.add_argument("--max-context-rows", type=int, default=120, help="Maximum context rows per heatmap before truncation for readability.")
    parser.add_argument("--rgb-mass-delta-max", type=float, default=0.60, help="Positive mass-delta value mapped to full red in the RGB spectrogram.")
    parser.add_argument("--rgb-entropy-delta-max", type=float, default=0.30, help="Positive entropy-delta value mapped to full blue in the RGB spectrogram.")
    parser.add_argument("--raw-matrix-max-panels", type=int, default=8, help="Maximum raw transport matrices to plot from horizon_transport_matrix_entries.csv.")
    parser.add_argument("--raw-matrix-max-items", type=int, default=36, help="Maximum source/target items shown per raw transport matrix panel.")
    parser.add_argument("--raw-state-max-contexts", type=int, default=48, help="Maximum raw frontier contexts shown in the substrate-state heatmap.")
    parser.add_argument("--raw-state-max-states", type=int, default=160, help="Maximum raw substrate states shown in the frontier heatmap.")
    parser.add_argument("--dpi", type=int, default=160)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir
    out_dir = args.out_dir or run_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    response_rows = read_csv(run_dir / "horizon_transport_response_classification.csv")
    viscosity_rows = read_csv(run_dir / "horizon_transport_viscosity_summary.csv")
    saturation_rows = read_csv(run_dir / "horizon_transport_saturation_by_horizon_pair.csv")
    threshold_rows = read_csv(run_dir / "horizon_response_threshold_table.csv")
    matrix_entry_rows = read_csv(run_dir / "horizon_transport_matrix_entries.csv")
    raw_state_rows = read_csv(run_dir / "horizon_transport_raw_state_frontier_samples.csv")

    written: list[Path] = []
    if any(row.get("state_id") for row in raw_state_rows):
        written.append(plot_raw_state_frontier_heatmap(raw_state_rows, out_dir, args.raw_state_max_contexts, args.raw_state_max_states, args.dpi))
    if matrix_entry_rows:
        written.append(plot_raw_transport_matrix_atlas(matrix_entry_rows, out_dir, args.raw_matrix_max_panels, args.raw_matrix_max_items, args.dpi))
    if response_rows:
        written.append(plot_response_rgb_spectrogram(response_rows, out_dir, args.max_context_rows, args.dpi, args.rgb_mass_delta_max, args.rgb_entropy_delta_max))
        written.append(plot_response_class_heatmap(response_rows, out_dir, args.max_context_rows, args.dpi))
    if viscosity_rows:
        written.append(plot_numeric_heatmap(
            viscosity_rows,
            out_dir / "transport_viscosity_score_spectrogram.png",
            args.max_context_rows,
            args.dpi,
            "transport_viscosity_score",
            "Transport Viscosity Score by Horizon",
            cmap="viridis",
            vmin=0.0,
            vmax=1.0,
        ))
        written.append(plot_metric_panels(viscosity_rows, out_dir, args.max_context_rows, args.dpi))
    if saturation_rows:
        written.append(plot_saturation_profile(saturation_rows, out_dir, args.dpi))
    if threshold_rows:
        written.append(plot_threshold_ladder(threshold_rows, out_dir, args.dpi))

    write_readme(run_dir, out_dir, written, response_rows, viscosity_rows, saturation_rows, threshold_rows, matrix_entry_rows, raw_state_rows)
    print(f"Wrote {len(written)} figure(s) to {out_dir}")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def plot_raw_state_frontier_heatmap(rows: list[dict[str, str]], out_dir: Path, max_contexts: int, max_states: int, dpi: int) -> Path:
    valid = [row for row in rows if row.get("state_id") and row.get("raw_state_sample_status", "ok") != "error"]
    if not valid:
        raise ValueError("raw state frontier sample rows did not include plottable state_id values")
    contexts = sorted({raw_state_context_key(row) for row in valid}, key=raw_state_context_sort_key)[: max(1, max_contexts)]
    context_set = set(contexts)
    state_counts: Counter[str] = Counter()
    state_indices: dict[str, float] = {}
    counts: Counter[tuple[str, tuple[str, str, str, str, str, str]]] = Counter()
    for row in valid:
        context = raw_state_context_key(row)
        if context not in context_set:
            continue
        state = str(row.get("state_id", ""))
        state_presence = float_or_nan(row.get("state_presence"))
        state_counts[state] += int(state_presence if not math.isnan(state_presence) else 1)
        state_indices[state] = min(state_indices.get(state, math.inf), float_or_nan(row.get("state_index")))
        counts[(state, context)] += 1

    selected_states = sorted(
        state_counts,
        key=lambda state: (-state_counts[state], state_indices.get(state, math.inf), state),
    )[: max(1, max_states)]
    states = sorted(selected_states, key=lambda state: (state_indices.get(state, math.inf), state))
    values = np.zeros((len(states), len(contexts)), dtype=float)
    for row_index, state in enumerate(states):
        for col_index, context in enumerate(contexts):
            values[row_index, col_index] = counts.get((state, context), 0)

    width = max(11.0, min(30.0, 0.42 * len(contexts) + 5.0))
    height = max(7.0, min(32.0, 0.16 * len(states) + 3.0))
    fig, ax = plt.subplots(figsize=(width, height), constrained_layout=True)
    image = ax.imshow(values, aspect="auto", interpolation="nearest", cmap="cividis")
    ax.set_title("Raw Substrate State Frontier Occupancy")
    ax.set_xlabel("Sampled frontier context / horizon")
    ax.set_ylabel("Raw substrate state")
    label_raw_state_axes(ax, contexts, states)
    fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02, label="frontier presence count")
    ax.text(
        0.0,
        1.025,
        "Rows are actual state tuples from X; columns are sampled exact-frontier contexts.",
        transform=ax.transAxes,
        fontsize=9,
        va="bottom",
    )
    out_path = out_dir / "raw_substrate_state_frontier_heatmap.png"
    save(fig, out_path, dpi)
    return out_path


def plot_raw_transport_matrix_atlas(rows: list[dict[str, str]], out_dir: Path, max_panels: int, max_items: int, dpi: int) -> Path:
    matrix_groups = group_rows(rows, "matrix_id")
    selected = sorted(matrix_groups, key=lambda item: raw_matrix_sort_key(item[1]))[: max(1, max_panels)]
    panel_count = len(selected)
    cols = min(2, panel_count)
    plot_rows = math.ceil(panel_count / cols)
    fig, axes = plt.subplots(
        plot_rows,
        cols,
        figsize=(max(9.0, cols * 7.0), max(5.5, plot_rows * 6.0)),
        constrained_layout=True,
    )
    axes_flat = np.atleast_1d(axes).ravel()
    for ax, (_matrix_id, items) in zip(axes_flat, selected):
        matrix, row_labels, col_labels = sparse_matrix_from_entries(items, max_items)
        image = ax.imshow(np.log1p(matrix), aspect="auto", interpolation="nearest", cmap="magma")
        title_row = items[0]
        ax.set_title(raw_matrix_title(title_row), fontsize=9)
        ax.set_xlabel("Target horizon item")
        ax.set_ylabel("Source horizon item")
        label_matrix_axes(ax, row_labels, col_labels)
        fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02, label="log1p transport mass")
    for ax in axes_flat[panel_count:]:
        ax.axis("off")
    out_path = out_dir / "raw_transport_matrix_atlas.png"
    save(fig, out_path, dpi)
    return out_path


def plot_response_class_heatmap(rows: list[dict[str, str]], out_dir: Path, max_context_rows: int, dpi: int) -> Path:
    horizons = horizon_order(rows)
    contexts = limited_context_order(rows, max_context_rows)
    values = np.full((len(contexts), len(horizons)), np.nan)
    grouped: dict[tuple[tuple[str, str, str, str], str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[(context_key(row), horizon_pair(row))][str(row.get("response_class", ""))] += 1
    class_index = {name: index for index, name in enumerate(RESPONSE_CLASS_ORDER)}
    for row_index, context in enumerate(contexts):
        for col_index, horizon in enumerate(horizons):
            counts = grouped.get((context, horizon), Counter())
            if not counts:
                continue
            response_class = sorted(counts, key=lambda name: (-counts[name], class_index.get(name, 999), name))[0]
            values[row_index, col_index] = class_index.get(response_class, len(RESPONSE_CLASS_ORDER) - 1)

    fig, ax = sized_figure(len(horizons), len(contexts))
    cmap = ListedColormap(RESPONSE_CLASS_COLORS)
    norm = BoundaryNorm(np.arange(-0.5, len(RESPONSE_CLASS_ORDER) + 0.5, 1), cmap.N)
    image = ax.imshow(values, aspect="auto", interpolation="nearest", cmap=cmap, norm=norm)
    style_grid_axes(ax, horizons, contexts, "Horizon Pair", "Perturbation / Probe / Flow")
    ax.set_title("Horizon-Transport Response Class Spectrogram")
    cbar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_ticks(range(len(RESPONSE_CLASS_ORDER)))
    cbar.set_ticklabels([short_response_label(name) for name in RESPONSE_CLASS_ORDER])
    out_path = out_dir / "horizon_response_class_spectrogram.png"
    save(fig, out_path, dpi)
    return out_path


def plot_response_rgb_spectrogram(
    rows: list[dict[str, str]],
    out_dir: Path,
    max_context_rows: int,
    dpi: int,
    mass_delta_max: float,
    entropy_delta_max: float,
) -> Path:
    horizons = horizon_order(rows)
    contexts = limited_context_order(rows, max_context_rows)
    red = normalized_grid(rows, contexts, horizons, "spectral_mass_delta_fraction", low=0.0, high=max(1e-9, mass_delta_max), positive_only=True)
    green = normalized_grid(rows, contexts, horizons, "mean_subspace_alignment", low=0.0, high=1.0)
    blue = normalized_grid(rows, contexts, horizons, "transport_entropy_delta", low=0.0, high=max(1e-9, entropy_delta_max), positive_only=True)
    alpha = ~np.isnan(red) | ~np.isnan(green) | ~np.isnan(blue)
    rgb = np.stack([
        np.nan_to_num(red, nan=0.0),
        np.nan_to_num(green, nan=0.0),
        np.nan_to_num(blue, nan=0.0),
    ], axis=2)
    rgb[~alpha] = 1.0

    fig, ax = sized_figure(len(horizons), len(contexts))
    ax.imshow(rgb, aspect="auto", interpolation="nearest", vmin=0.0, vmax=1.0)
    style_grid_axes(ax, horizons, contexts, "Horizon Pair", "Perturbation / Probe / Flow")
    ax.set_title("Horizon-Transport Metric RGB Spectrogram")
    legend = (
        "RGB mapping: red = positive spectral mass delta; "
        "green = subspace alignment; blue = positive entropy delta"
    )
    ax.text(0.0, 1.025, legend, transform=ax.transAxes, fontsize=9, va="bottom")
    out_path = out_dir / "horizon_response_metric_rgb_spectrogram.png"
    save(fig, out_path, dpi)
    return out_path


def plot_numeric_heatmap(
    rows: list[dict[str, str]],
    out_path: Path,
    max_context_rows: int,
    dpi: int,
    field: str,
    title: str,
    *,
    cmap: str,
    vmin: float | None = None,
    vmax: float | None = None,
) -> Path:
    horizons = horizon_order(rows)
    contexts = limited_context_order(rows, max_context_rows)
    values = numeric_grid(rows, contexts, horizons, field)
    fig, ax = sized_figure(len(horizons), len(contexts))
    image = ax.imshow(values, aspect="auto", interpolation="nearest", cmap=cmap, vmin=vmin, vmax=vmax)
    style_grid_axes(ax, horizons, contexts, "Horizon Pair", "Perturbation / Probe / Flow")
    ax.set_title(title)
    fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02)
    save(fig, out_path, dpi)
    return out_path


def plot_metric_panels(rows: list[dict[str, str]], out_dir: Path, max_context_rows: int, dpi: int) -> Path:
    horizons = horizon_order(rows)
    contexts = limited_context_order(rows, max_context_rows)
    fields = (
        ("mean_alignment", "Mean Alignment", "viridis", 0.0, 1.0),
        ("mass_delta_fraction", "Mass Delta Fraction", "coolwarm", None, None),
        ("entropy_delta", "Entropy Delta", "coolwarm", None, None),
    )
    fig_height = max(8.0, min(24.0, 1.8 + 0.26 * max(1, len(contexts)))) * len(fields) / 2.4
    fig, axes = plt.subplots(len(fields), 1, figsize=(max(10.0, 0.72 * len(horizons) + 6.0), fig_height), constrained_layout=True)
    for ax, (field, title, cmap, vmin, vmax) in zip(np.ravel(axes), fields):
        values = numeric_grid(rows, contexts, horizons, field)
        image = ax.imshow(values, aspect="auto", interpolation="nearest", cmap=cmap, vmin=vmin, vmax=vmax)
        style_grid_axes(ax, horizons, contexts, "Horizon Pair", "Perturbation / Probe / Flow")
        ax.set_title(title)
        fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02)
    out_path = out_dir / "alignment_mass_entropy_panels.png"
    save(fig, out_path, dpi)
    return out_path


def plot_saturation_profile(rows: list[dict[str, str]], out_dir: Path, dpi: int) -> Path:
    ordered = sorted(rows, key=horizon_sort_key)
    labels = [horizon_pair(row) for row in ordered]
    terminal = [float_or_nan(row.get("terminal_saturation_fraction")) for row in ordered]
    undercoverage = [float_or_nan(row.get("undercoverage_fraction")) for row in ordered]
    normal = [float_or_nan(row.get("normal_interpretation_fraction")) for row in ordered]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(max(9.0, 0.75 * len(labels) + 4.0), 5.0), constrained_layout=True)
    ax.plot(x, terminal, marker="o", label="terminal saturation")
    ax.plot(x, undercoverage, marker="o", label="undercoverage")
    ax.plot(x, normal, marker="o", label="normal interpretation")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylim(-0.05, 1.05)
    ax.set_ylabel("Fraction")
    ax.set_xlabel("Horizon Pair")
    ax.set_title("Saturation and Coverage by Horizon")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="best")
    out_path = out_dir / "saturation_coverage_profile.png"
    save(fig, out_path, dpi)
    return out_path


def plot_threshold_ladder(rows: list[dict[str, str]], out_dir: Path, dpi: int) -> Path:
    fields = (
        "first_nonstable_horizon",
        "first_amplified_aligned_horizon",
        "first_non_amplified_response_horizon",
        "terminal_saturation_horizon",
        "latest_interpretable_horizon",
    )
    fig, ax = plt.subplots(figsize=(12.0, max(5.0, 0.42 * len(rows) + 2.0)), constrained_layout=True)
    y_labels = [context_label(context_key(row)) for row in rows]
    horizon_values = sorted({value for row in rows for field in fields if (value := row.get(field, ""))}, key=horizon_label_sort_key)
    horizon_index = {label: index for index, label in enumerate(horizon_values)}
    markers = ("o", "s", "^", "x", "D")
    colors = ("#111111", "#2F80ED", "#D64545", "#F2994A", "#4C956C")
    for y, row in enumerate(rows):
        for field, marker, color in zip(fields, markers, colors):
            value = row.get(field, "")
            if not value:
                continue
            ax.scatter(horizon_index[value], y, marker=marker, color=color, label=field if y == 0 else "")
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels, fontsize=8)
    ax.set_xticks(range(len(horizon_values)))
    ax.set_xticklabels(horizon_values, rotation=35, ha="right")
    ax.set_xlabel("Horizon Pair")
    ax.set_title("Response Threshold Ladder")
    ax.grid(axis="x", alpha=0.20)
    ax.legend(loc="upper right", fontsize=8)
    out_path = out_dir / "response_threshold_ladder.png"
    save(fig, out_path, dpi)
    return out_path


def numeric_grid(rows: list[dict[str, str]], contexts: list[tuple[str, str, str, str]], horizons: list[str], field: str) -> np.ndarray:
    grouped: dict[tuple[tuple[str, str, str, str], str], list[float]] = defaultdict(list)
    for row in rows:
        value = float_or_nan(row.get(field))
        if math.isnan(value):
            continue
        grouped[(context_key(row), horizon_pair(row))].append(value)
    values = np.full((len(contexts), len(horizons)), np.nan)
    for row_index, context in enumerate(contexts):
        for col_index, horizon in enumerate(horizons):
            observed = grouped.get((context, horizon), [])
            if observed:
                values[row_index, col_index] = mean(observed)
    return values


def normalized_grid(
    rows: list[dict[str, str]],
    contexts: list[tuple[str, str, str, str]],
    horizons: list[str],
    field: str,
    *,
    low: float,
    high: float,
    positive_only: bool = False,
) -> np.ndarray:
    values = numeric_grid(rows, contexts, horizons, field)
    if positive_only:
        values = np.maximum(values, 0.0)
    normalized = (values - low) / max(1e-12, high - low)
    return np.clip(normalized, 0.0, 1.0)


def group_rows(rows: list[dict[str, str]], field: str) -> list[tuple[str, list[dict[str, str]]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(field, ""))].append(row)
    return list(grouped.items())


def sparse_matrix_from_entries(rows: list[dict[str, str]], max_items: int) -> tuple[np.ndarray, list[str], list[str]]:
    row_masses: Counter[str] = Counter()
    col_masses: Counter[str] = Counter()
    for row in rows:
        mass = float_or_nan(row.get("transport_mass"))
        if math.isnan(mass):
            continue
        row_masses[str(row.get("row_item", ""))] += mass
        col_masses[str(row.get("column_item", ""))] += mass
    row_labels = [item for item, _mass in row_masses.most_common(max(1, max_items))]
    col_labels = [item for item, _mass in col_masses.most_common(max(1, max_items))]
    row_index = {item: index for index, item in enumerate(row_labels)}
    col_index = {item: index for index, item in enumerate(col_labels)}
    matrix = np.zeros((len(row_labels), len(col_labels)), dtype=float)
    for row in rows:
        source = str(row.get("row_item", ""))
        target = str(row.get("column_item", ""))
        if source not in row_index or target not in col_index:
            continue
        mass = float_or_nan(row.get("transport_mass"))
        if not math.isnan(mass):
            matrix[row_index[source], col_index[target]] += mass
    return matrix, row_labels, col_labels


def raw_matrix_sort_key(rows: list[dict[str, str]]) -> tuple[str, float, str, str, float, float]:
    row = rows[0] if rows else {}
    control_sort = "0" if row.get("actual_control_name") == "baseline_control" else "1"
    return (
        control_sort,
        float_or_nan(row.get("mechanism_control_strength")),
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
        float_or_nan(row.get("H_b")),
        float_or_nan(row.get("H_a")),
    )


def raw_matrix_title(row: dict[str, str]) -> str:
    condition = str(row.get("actual_control_name", "")).replace("_control", "").replace("_", " ")
    strength = row.get("mechanism_control_strength", "")
    probe = str(row.get("probe_key", "")).replace("constraint_", "c_").replace("_", " ")
    flow = str(row.get("flow_mode", "")).replace("_", " ")
    horizon = horizon_pair(row)
    return f"{horizon} | {condition} p={strength}\n{probe} / {flow}"


def label_matrix_axes(ax: plt.Axes, row_labels: list[str], col_labels: list[str]) -> None:
    row_step = max(1, math.ceil(len(row_labels) / 12))
    col_step = max(1, math.ceil(len(col_labels) / 12))
    row_ticks = list(range(0, len(row_labels), row_step))
    col_ticks = list(range(0, len(col_labels), col_step))
    ax.set_yticks(row_ticks)
    ax.set_yticklabels([short_item_label(row_labels[index]) for index in row_ticks], fontsize=6)
    ax.set_xticks(col_ticks)
    ax.set_xticklabels([short_item_label(col_labels[index]) for index in col_ticks], fontsize=6, rotation=45, ha="right")


def label_raw_state_axes(ax: plt.Axes, contexts: list[tuple[str, str, str, str, str, str]], states: list[str]) -> None:
    state_step = max(1, math.ceil(len(states) / 28))
    context_step = max(1, math.ceil(len(contexts) / 24))
    state_ticks = list(range(0, len(states), state_step))
    context_ticks = list(range(0, len(contexts), context_step))
    ax.set_yticks(state_ticks)
    ax.set_yticklabels([short_item_label(states[index], 32) for index in state_ticks], fontsize=6)
    ax.set_xticks(context_ticks)
    ax.set_xticklabels([raw_state_context_label(contexts[index]) for index in context_ticks], fontsize=6, rotation=55, ha="right")
    ax.set_xticks(np.arange(-0.5, len(contexts), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(states), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.4, alpha=0.30)
    ax.tick_params(which="minor", bottom=False, left=False)


def raw_state_context_key(row: dict[str, str]) -> tuple[str, str, str, str, str, str]:
    return (
        str(row.get("actual_control_name", "")),
        str(row.get("mechanism_control_strength", "")),
        str(row.get("probe_key", "")),
        str(row.get("seed", "")),
        str(row.get("start_index", "")),
        str(row.get("H", "")),
    )


def raw_state_context_sort_key(key: tuple[str, str, str, str, str, str]) -> tuple[str, float, str, float, float, float]:
    control, strength, probe, seed, start_index, horizon = key
    return (control, float_or_nan(strength), probe, float_or_nan(seed), float_or_nan(start_index), float_or_nan(horizon))


def raw_state_context_label(key: tuple[str, str, str, str, str, str]) -> str:
    control, strength, probe, seed, start_index, horizon = key
    control = control.replace("_control", "").replace("_", " ")
    probe = probe.replace("constraint_", "c_").replace("_", " ")
    return f"{control} p={strength}\n{probe} s{seed} start{start_index} H{horizon}"


def short_item_label(value: str, limit: int = 24) -> str:
    return value if len(value) <= limit else value[: limit - 1] + "..."


def horizon_order(rows: list[dict[str, str]]) -> list[str]:
    return sorted({horizon_pair(row) for row in rows if horizon_pair(row)}, key=horizon_label_sort_key)


def limited_context_order(rows: list[dict[str, str]], max_context_rows: int) -> list[tuple[str, str, str, str]]:
    contexts = sorted({context_key(row) for row in rows}, key=context_sort_key)
    return contexts[: max(1, max_context_rows)]


def context_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    family = row.get("perturbation_family") or row.get("actual_control_name") or ""
    strength = row.get("perturbation_strength") or row.get("mechanism_control_strength") or ""
    return (str(family), str(strength), str(row.get("probe_key", "")), str(row.get("flow_mode", "")))


def context_sort_key(key: tuple[str, str, str, str]) -> tuple[str, float, str, str]:
    family, strength, probe, flow = key
    return (family, float_or_nan(strength), probe, flow)


def context_label(key: tuple[str, str, str, str]) -> str:
    family, strength, probe, flow = key
    family = family.replace("_control", "").replace("_", " ")
    probe = probe.replace("constraint_", "c_").replace("_", " ")
    flow = flow.replace("_", " ")
    return f"{family} p={strength}\n{probe} / {flow}"


def horizon_pair(row: dict[str, str]) -> str:
    return str(row.get("horizon_pair", "") or f"{row.get('H_a', '')}->{row.get('H_b', '')}")


def horizon_sort_key(row: dict[str, str]) -> tuple[float, float, str]:
    return horizon_label_sort_key(horizon_pair(row))


def horizon_label_sort_key(label: str) -> tuple[float, float, str]:
    if "->" in label:
        left, right = label.split("->", 1)
        return (float_or_nan(right), float_or_nan(left), label)
    return (math.inf, math.inf, label)


def float_or_nan(value: object) -> float:
    try:
        if value in (None, ""):
            return math.nan
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return math.nan


def short_response_label(name: str) -> str:
    return name.replace("transport_", "").replace("_aligned", "").replace("_", " ")


def sized_figure(width_count: int, height_count: int) -> tuple[plt.Figure, plt.Axes]:
    width = max(10.0, min(24.0, 0.72 * max(1, width_count) + 6.0))
    height = max(6.0, min(30.0, 0.34 * max(1, height_count) + 2.5))
    return plt.subplots(figsize=(width, height), constrained_layout=True)


def style_grid_axes(ax: plt.Axes, horizons: list[str], contexts: list[tuple[str, str, str, str]], xlabel: str, ylabel: str) -> None:
    ax.set_xticks(range(len(horizons)))
    ax.set_xticklabels(horizons, rotation=35, ha="right")
    ax.set_yticks(range(len(contexts)))
    ax.set_yticklabels([context_label(key) for key in contexts], fontsize=8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(np.arange(-0.5, len(horizons), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(contexts), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8, alpha=0.65)
    ax.tick_params(which="minor", bottom=False, left=False)


def save(fig: plt.Figure, path: Path, dpi: int) -> None:
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def write_readme(
    run_dir: Path,
    out_dir: Path,
    written: list[Path],
    response_rows: list[dict[str, str]],
    viscosity_rows: list[dict[str, str]],
    saturation_rows: list[dict[str, str]],
    threshold_rows: list[dict[str, str]],
    matrix_entry_rows: list[dict[str, str]],
    raw_state_rows: list[dict[str, str]],
) -> None:
    class_counts = Counter(row.get("response_class", "") for row in response_rows if row.get("response_class"))
    viscosity_counts = Counter(row.get("transport_viscosity_read", "") for row in viscosity_rows if row.get("transport_viscosity_read"))
    lines = [
        "# Horizon-Transport Visualization Bundle",
        "",
        f"Source run: `{run_dir}`",
        "",
        "These figures are diagnostic visualizations of local CSV outputs. They do not add claim status.",
        "",
        "## Figures",
        "",
    ]
    for path in written:
        lines.append(f"- `{path.name}`")
    lines.extend([
        "",
        "## RGB Spectrogram Mapping",
        "",
        "`horizon_response_metric_rgb_spectrogram.png` maps measured variables directly:",
        "",
        "- red: positive `spectral_mass_delta_fraction`",
        "- green: `mean_subspace_alignment`",
        "- blue: positive `transport_entropy_delta`",
        "",
        "Stable aligned transport appears mostly green. Amplified-aligned transport appears yellow/orange because mass gain adds red while alignment stays green.",
        "",
        "## Raw Transport Matrix Atlas",
        "",
        "`raw_transport_matrix_atlas.png` uses `horizon_transport_matrix_entries.csv` when available. Rows are source-horizon items, columns are target-horizon items, and color is `log1p(transport_mass)` for retained sparse entries.",
        "",
        "This atlas is instrument-native: its row/column items are probe-signature transport items, not necessarily raw substrate states.",
        "",
        "## Raw Substrate State Frontier Heatmap",
        "",
        "`raw_substrate_state_frontier_heatmap.png` uses `horizon_transport_raw_state_frontier_samples.csv` when available. Rows are actual substrate state tuples from `X`, columns are sampled exact-frontier contexts/horizons, and color is frontier presence count.",
        "",
        "## Row Counts",
        "",
        f"- matrix entry rows: `{len(matrix_entry_rows)}`",
        f"- raw state sample rows: `{len(raw_state_rows)}`",
        f"- response rows: `{len(response_rows)}`",
        f"- viscosity rows: `{len(viscosity_rows)}`",
        f"- saturation rows: `{len(saturation_rows)}`",
        f"- threshold rows: `{len(threshold_rows)}`",
        "",
        "## Response Classes",
        "",
    ])
    for name, count in sorted(class_counts.items()):
        lines.append(f"- {name}: `{count}`")
    lines.extend(["", "## Viscosity Reads", ""])
    for name, count in sorted(viscosity_counts.items()):
        lines.append(f"- {name}: `{count}`")
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
