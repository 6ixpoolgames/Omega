#!/usr/bin/env python
"""Compact Omega Multifield composite-mode kill-test.

This is the Python version of the smoke harness. It implements the current spec:

- true coupled, independent, shuffled-pair, and perturbed-coupled dynamics
- pre-declared kappa maps: center of mass, relative distance, joint basin
- realization-fiber robustness and viability reporting
- two horizons and two sample counts by default
- a wall-clock timeout

Important: this is still a standalone toy simulator, not the original unpublished
multifield simulator. It is designed to test the object against shuffled nulls.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Regime:
    id: str
    label: str
    type_a: str
    type_b: str
    coupling: str
    alpha: float
    seed: int
    near_enrichment: bool = False


REGIMES = [
    Regime("FT_attractive_alpha_0.3", "(F,T) attractive", "F", "T", "attractive", 0.3, 1101),
    Regime("FF_repulsive_alpha_0.3", "(F,F) repulsive", "F", "F", "repulsive", 0.3, 2202),
    Regime(
        "near_enrichment_repulsive_alpha_0.3",
        "near-enrichment repulsive",
        "F",
        "T",
        "repulsive",
        0.3,
        3303,
        True,
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-sec", type=float, default=300)
    parser.add_argument("--out-dir", type=Path, default=Path("omega_multifield_results_py"))
    parser.add_argument("--horizons", type=int, nargs="+", default=[60, 120])
    parser.add_argument("--samples", type=int, nargs="+", default=[300, 900])
    parser.add_argument("--seed-offset", type=int, default=0)
    return parser.parse_args()


def check_timeout(start: float, timeout_sec: float) -> None:
    if time.monotonic() - start > timeout_sec:
        raise TimeoutError(f"timeout: exceeded {timeout_sec:.1f}s")


def preferred(kind: str, rng: np.random.Generator, near_enrichment: bool) -> float:
    if kind == "T":
        return float(1.15 + 0.1 * rng.normal())
    if near_enrichment:
        return float(-0.35 + 0.5 * rng.normal())
    return float(-1.1 + 0.75 * rng.normal())


def local_drift(x: float, kind: str) -> float:
    if kind == "T":
        return float(-0.11 * (x - 1.15) - 0.02 * (x - 1.15) ** 3)
    return float(-0.035 * (x + 0.9) + 0.018 * math.sin(2.2 * x))


def basin(x: float) -> str:
    if x < -0.45:
        return "L"
    if x > 0.55:
        return "R"
    return "M"


def simulate_pair(
    regime: Regime,
    condition: str,
    horizon: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, bool]:
    noise = 0.09 if condition == "perturbed" else 0.065
    perturb_kick = 0.025 if condition == "perturbed" else 0.0

    x_a = preferred(regime.type_a, rng, regime.near_enrichment)
    x_b = preferred(regime.type_b, rng, regime.near_enrichment)
    a = np.empty(horizon + 1, dtype=np.float64)
    b = np.empty(horizon + 1, dtype=np.float64)
    a[0] = x_a
    b[0] = x_b

    viable = abs(x_a) < 3.0 and abs(x_b) < 3.0
    cost = 0.0

    for t in range(horizon):
        c_a = 0.0
        c_b = 0.0
        if condition in {"coupled", "perturbed"}:
            delta = x_b - x_a
            sign = 1.0 if regime.coupling == "attractive" else -1.0
            c_a = sign * regime.alpha * 0.045 * delta
            c_b = -sign * regime.alpha * 0.045 * delta

        dx_a = (
            local_drift(x_a, regime.type_a)
            + c_a
            + noise * rng.normal()
            + perturb_kick * math.sin(0.17 * t + 1.3)
        )
        dx_b = (
            local_drift(x_b, regime.type_b)
            + c_b
            + noise * rng.normal()
            + perturb_kick * math.cos(0.13 * t + 0.7)
        )
        x_a += dx_a
        x_b += dx_b
        cost += abs(dx_a) + abs(dx_b)

        if abs(x_a) > 3.0 or abs(x_b) > 3.0 or cost > 0.2 * horizon:
            viable = False

        x_a = float(np.clip(x_a, -3.5, 3.5))
        x_b = float(np.clip(x_b, -3.5, 3.5))
        a[t + 1] = x_a
        b[t + 1] = x_b

    return a, b, viable


def simulate(
    regime: Regime,
    condition: str,
    horizon: int,
    sample_count: int,
    seed_offset: int,
) -> list[tuple[np.ndarray, np.ndarray, bool]]:
    rng = np.random.default_rng(regime.seed + seed_offset)
    return [simulate_pair(regime, condition, horizon, rng) for _ in range(sample_count)]


def shuffle_pairs(
    independent: list[tuple[np.ndarray, np.ndarray, bool]],
    seed: int,
) -> list[tuple[np.ndarray, np.ndarray, bool]]:
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(independent))
    out = []
    for i, j in enumerate(perm):
        a, _, viable_a = independent[i]
        _, b, viable_b = independent[j]
        out.append((a, b, bool(viable_a and viable_b)))
    return out


def sample_indexes(length: int, parts: int = 12) -> np.ndarray:
    return np.rint(np.linspace(0, length - 1, parts)).astype(int)


def qbin(x: float, width: float) -> str:
    return str(int(round(x / width)))


def kappa_center_of_mass(tau: tuple[np.ndarray, np.ndarray, bool]) -> str:
    a, b, _ = tau
    idx = sample_indexes(len(a))
    return ".".join(qbin(float((a[i] + b[i]) / 2.0), 0.32) for i in idx)


def kappa_relative_distance(tau: tuple[np.ndarray, np.ndarray, bool]) -> str:
    a, b, _ = tau
    idx = sample_indexes(len(a))
    return ".".join(qbin(float(abs(a[i] - b[i])), 0.25) for i in idx)


def kappa_joint_basin(tau: tuple[np.ndarray, np.ndarray, bool]) -> str:
    a, b, _ = tau
    idx = sample_indexes(len(a))
    return ".".join(f"{basin(float(a[i]))}{basin(float(b[i]))}" for i in idx)


KAPPAS: dict[str, Callable[[tuple[np.ndarray, np.ndarray, bool]], str]] = {
    "center_of_mass": kappa_center_of_mass,
    "relative_distance": kappa_relative_distance,
    "joint_basin": kappa_joint_basin,
}


def metrics(
    trajectories: list[tuple[np.ndarray, np.ndarray, bool]],
    kappa: Callable[[tuple[np.ndarray, np.ndarray, bool]], str],
) -> dict[str, float | int]:
    viable = [tau for tau in trajectories if tau[2]]
    if not viable:
        return {
            "R_bits": 0.0,
            "R_norm": 0.0,
            "H_macro_bits": 0.0,
            "macro_classes": 0,
            "viability": 0.0,
        }

    keys = [kappa(tau) for tau in viable]
    _, counts = np.unique(keys, return_counts=True)
    n = len(viable)
    p = counts / n

    # Aggregate finite-sample estimate of realization-fiber entropy:
    # E_gamma[log2(|fiber_gamma|)], weighted by viable trajectory counts.
    r_bits = float(np.sum(p * np.log2(counts)))
    h_macro_bits = float(-np.sum(p * np.log2(p)))
    r_norm = float(r_bits / np.log2(n)) if n > 1 else 0.0

    return {
        "R_bits": r_bits,
        "R_norm": r_norm,
        "H_macro_bits": h_macro_bits,
        "macro_classes": int(len(counts)),
        "viability": float(n / len(trajectories)),
    }


def round4(x: float) -> float:
    return round(float(x), 4)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Small markdown table formatter to avoid pandas' optional tabulate dependency."""
    if df.empty:
        return "_No rows._"

    str_df = df.astype(str)
    headers = list(str_df.columns)
    rows = str_df.values.tolist()
    widths = [
        max(len(header), *(len(row[i]) for row in rows))
        for i, header in enumerate(headers)
    ]

    def fmt_row(values: list[str]) -> str:
        return "| " + " | ".join(value.ljust(widths[i]) for i, value in enumerate(values)) + " |"

    sep = "| " + " | ".join("-" * width for width in widths) + " |"
    return "\n".join([fmt_row(headers), sep, *(fmt_row(row) for row in rows)])


def main() -> None:
    args = parse_args()
    start = time.monotonic()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []

    for regime in REGIMES:
        for horizon in args.horizons:
            for sample_count in args.samples:
                check_timeout(start, args.timeout_sec)

                coupled = simulate(
                    regime,
                    "coupled",
                    horizon,
                    sample_count,
                    args.seed_offset + 10 + horizon + sample_count,
                )
                independent = simulate(
                    regime,
                    "independent",
                    horizon,
                    sample_count,
                    args.seed_offset + 20 + horizon + sample_count,
                )
                shuffled = shuffle_pairs(
                    independent,
                    regime.seed + args.seed_offset + 999 + horizon + sample_count,
                )
                perturbed = simulate(
                    regime,
                    "perturbed",
                    horizon,
                    sample_count,
                    args.seed_offset + 30 + horizon + sample_count,
                )

                for kappa_name, kappa_fn in KAPPAS.items():
                    m_c = metrics(coupled, kappa_fn)
                    m_i = metrics(independent, kappa_fn)
                    m_s = metrics(shuffled, kappa_fn)
                    m_p = metrics(perturbed, kappa_fn)

                    delta_s = float(m_c["R_bits"]) - float(m_s["R_bits"])
                    delta_i = float(m_c["R_bits"]) - float(m_i["R_bits"])
                    retention = (
                        float(m_p["R_bits"]) / float(m_c["R_bits"])
                        if float(m_c["R_bits"]) > 1e-9
                        else 0.0
                    )

                    rows.append(
                        {
                            "regime": regime.label,
                            "regime_id": regime.id,
                            "coupling_type": regime.coupling,
                            "alpha": regime.alpha,
                            "kappa": kappa_name,
                            "horizon": horizon,
                            "sample_count": sample_count,
                            "R_coupled": round4(m_c["R_bits"]),
                            "R_independent": round4(m_i["R_bits"]),
                            "R_shuffled": round4(m_s["R_bits"]),
                            "R_perturbed": round4(m_p["R_bits"]),
                            "Rn_coupled": round4(m_c["R_norm"]),
                            "Rn_shuffled": round4(m_s["R_norm"]),
                            "Hmacro_coupled": round4(m_c["H_macro_bits"]),
                            "Hmacro_shuffled": round4(m_s["H_macro_bits"]),
                            "Delta_R_coupled_minus_shuffled": round4(delta_s),
                            "Delta_R_coupled_minus_independent": round4(delta_i),
                            "viability_coupled": round4(m_c["viability"]),
                            "viability_independent": round4(m_i["viability"]),
                            "viability_shuffled": round4(m_s["viability"]),
                            "viability_perturbed": round4(m_p["viability"]),
                            "perturbation_retention": round4(retention),
                            "macro_classes_coupled": m_c["macro_classes"],
                            "macro_classes_shuffled": m_s["macro_classes"],
                        }
                    )

    df = pd.DataFrame(rows)
    summaries = []
    for regime in REGIMES:
        for kappa_name in KAPPAS:
            subset = df[(df["regime_id"] == regime.id) & (df["kappa"] == kappa_name)]
            mean_delta = float(subset["Delta_R_coupled_minus_shuffled"].mean())
            mean_viability = float(subset["viability_coupled"].mean())
            mean_retention = float(subset["perturbation_retention"].mean())
            positives = int((subset["Delta_R_coupled_minus_shuffled"] > 0).sum())

            status = "fail"
            reason = "coupled realization robustness did not beat shuffled null consistently"
            if positives >= 3 and mean_delta > 0 and mean_viability >= 0.8 and mean_retention >= 0.7:
                status = "pass"
                reason = "coupled beats shuffled in most horizon/sample checks with viability retained"
            elif positives >= 2 and mean_delta > 0 and mean_viability >= 0.8:
                status = "weak"
                reason = "partial positive signal, but not robust across all checks"

            summaries.append(
                {
                    "regime": regime.label,
                    "kappa": kappa_name,
                    "status": status,
                    "mean_delta_R": round4(mean_delta),
                    "mean_viability_coupled": round4(mean_viability),
                    "mean_perturbation_retention": round4(mean_retention),
                    "reason": reason,
                }
            )

    summary_df = pd.DataFrame(summaries)
    result_csv = args.out_dir / "omega_multifield_kill_test_results.csv"
    summary_csv = args.out_dir / "omega_multifield_kill_test_summary.csv"
    report_md = args.out_dir / "omega_multifield_kill_test_report.md"

    df.to_csv(result_csv, index=False)
    summary_df.to_csv(summary_csv, index=False)

    report = "\n".join(
        [
            "# Omega Multifield Compact Kill-Test Report",
            "",
            f"Runtime: {time.monotonic() - start:.2f}s",
            f"Horizons: {args.horizons}",
            f"Sample counts: {args.samples}",
            "",
            "Estimator: `R_bits = E_gamma[log2(|fiber_gamma|)]` over viable observed trajectories, weighted by viable trajectory counts. This estimates aggregate realization-fiber support, not macro-class entropy. `Hmacro_*` is reported separately.",
            "",
            "Important limitation: this is a standalone toy simulator because no prior multifield code was present in the workspace.",
            "",
            "## Summary",
            "",
            dataframe_to_markdown(summary_df),
            "",
            "## Largest Positive Delta_R Rows",
            "",
            dataframe_to_markdown(
                df.sort_values("Delta_R_coupled_minus_shuffled", ascending=False).head(12)
            ),
            "",
        ]
    )
    report_md.write_text(report, encoding="utf-8")

    print(
        json.dumps(
            {
                "result_csv": str(result_csv),
                "summary_csv": str(summary_csv),
                "report_md": str(report_md),
                "summaries": summaries,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
