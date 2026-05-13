#!/usr/bin/env python
"""Probe I0b: invariant threshold and dropout audit.

This is an analysis-only follow-up to Probe I0. It does not add invariants and
does not rerun simulation when the I0 estimator table is available.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


I0_DIR = Path("probe_I0_invariant_stack_audit_results")
INVARIANTS = {
    "I1_viability": "viability_gate",
    "I2_ordered_distinction_persistence": "ordered_persistence",
    "I3_component_non_erasure": "component_non_erasure",
    "I4_counterfactual_affordance_relevance": "counterfactual_affordance",
    "I5_minimal_recoverability": "minimal_recoverability",
    "I6_horizon_coherence": "horizon_coherence",
}
STACKS = {
    "S1": ["I1_viability"],
    "S2": ["I1_viability", "I2_ordered_distinction_persistence"],
    "S3": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure"],
    "S4": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure", "I4_counterfactual_affordance_relevance"],
    "S5": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure", "I4_counterfactual_affordance_relevance", "I5_minimal_recoverability"],
    "S6": ["I1_viability", "I2_ordered_distinction_persistence", "I3_component_non_erasure", "I4_counterfactual_affordance_relevance", "I5_minimal_recoverability", "I6_horizon_coherence"],
}
KNOWN_CONTROLS = ["rigid_collapse", "noise_fakeout", "single_component_erasure", "endpoint_fakeout"]
HOLDOUT_CONTROLS = ["delayed_trap", "component_swap_fakeout"]
CONTROL_COL = "control"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_I0b_invariant_threshold_dropout_audit_results"))
    p.add_argument("--i0-dir", type=Path, default=I0_DIR)
    return p.parse_args()


def load_i0(i0_dir: Path) -> tuple[pd.DataFrame, bool]:
    path = i0_dir / "estimator_report.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; rerun Probe I0 first.")
    df = pd.read_csv(path)
    df[CONTROL_COL] = df[CONTROL_COL].fillna("none")
    return df, True


def split_frames(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    coupled = df[df[CONTROL_COL] == "none"].copy()
    known = df[df[CONTROL_COL].isin(KNOWN_CONTROLS)].copy()
    holdout = df[df[CONTROL_COL].isin(HOLDOUT_CONTROLS)].copy()
    return coupled, known, holdout


def threshold_original(coupled: pd.DataFrame, known: pd.DataFrame) -> dict[str, float]:
    out = {}
    for inv, metric in INVARIANTS.items():
        cmed = coupled[metric].median()
        kq90 = known[metric].quantile(0.90)
        out[inv] = float(np.clip((cmed + kq90) / 2.0, 0.0, 1.0))
    return out


def threshold_families(coupled: pd.DataFrame, known: pd.DataFrame) -> dict[str, dict[str, float]]:
    original = threshold_original(coupled, known)
    families = {"original": original}
    for name, source, q in [
        ("control_q95", known, 0.95),
        ("control_q90", known, 0.90),
        ("control_q75", known, 0.75),
        ("coupled_q25", coupled, 0.25),
        ("coupled_q10", coupled, 0.10),
    ]:
        families[name] = {inv: float(np.clip(source[metric].quantile(q), 0.0, 1.0)) for inv, metric in INVARIANTS.items()}
    for scale in [0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20]:
        families[f"sensitivity_scale_{scale:.2f}"] = {inv: float(np.clip(th * scale, 0.0, 1.0)) for inv, th in original.items()}
    return families


def stack_mask(df: pd.DataFrame, invariants: list[str], thresholds: dict[str, float]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for inv in invariants:
        mask &= df[INVARIANTS[inv]] >= thresholds[inv]
    return mask


def retention_rejection(coupled: pd.DataFrame, known: pd.DataFrame, holdout: pd.DataFrame, mask_fn) -> tuple[float, float, float]:
    c = float(mask_fn(coupled).mean()) if len(coupled) else 0.0
    k = float(1.0 - mask_fn(known).mean()) if len(known) else 0.0
    h = float(1.0 - mask_fn(holdout).mean()) if len(holdout) else 0.0
    return c, k, h


def build_dropout(coupled: pd.DataFrame, known: pd.DataFrame, holdout: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
    rows = []
    prev_retention = None
    prev_stack = None
    for stack, invs in STACKS.items():
        fn = lambda d, invs=invs: stack_mask(d, invs, thresholds)
        c, k, h = retention_rejection(coupled, known, holdout, fn)
        added = invs[-1]
        rows.append({
            "stack": stack,
            "invariants": "+".join(invs),
            "added_invariant": added,
            "coupled_retention": c,
            "known_control_rejection": k,
            "holdout_rejection": h,
            "marginal_dropout_from_previous": 0.0 if prev_retention is None else prev_retention - c,
            "previous_stack": prev_stack,
        })
        prev_retention = c
        prev_stack = stack
    return pd.DataFrame(rows)


def distribution_summary(df: pd.DataFrame, coupled: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for inv, metric in INVARIANTS.items():
        cvals = coupled[metric].to_numpy(float)
        for control, group in df.groupby(CONTROL_COL):
            vals = group[metric].to_numpy(float)
            rows.append({
                "invariant": inv,
                "metric": metric,
                "control": control,
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "q10": float(np.quantile(vals, 0.10)),
                "q25": float(np.quantile(vals, 0.25)),
                "q75": float(np.quantile(vals, 0.75)),
                "q90": float(np.quantile(vals, 0.90)),
                "overlap_with_coupled": distribution_overlap(cvals, vals),
                "effect_size_vs_coupled": effect_size(cvals, vals),
            })
    return pd.DataFrame(rows)


def distribution_overlap(a: np.ndarray, b: np.ndarray) -> float:
    lo = max(float(np.min(a)), float(np.min(b)))
    hi = min(float(np.max(a)), float(np.max(b)))
    if hi < lo:
        return 0.0
    union = max(float(np.max(a)), float(np.max(b))) - min(float(np.min(a)), float(np.min(b)))
    return float((hi - lo) / max(union, 1e-12))


def effect_size(coupled: np.ndarray, other: np.ndarray) -> float:
    pooled = math.sqrt((float(np.var(coupled, ddof=1)) + float(np.var(other, ddof=1))) / 2.0)
    return float((np.mean(coupled) - np.mean(other)) / max(pooled, 1e-12))


def auc_table(coupled: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for inv, metric in INVARIANTS.items():
        for control, group in controls.groupby(CONTROL_COL):
            y = np.r_[np.ones(len(coupled)), np.zeros(len(group))]
            x = np.r_[coupled[metric].to_numpy(float), group[metric].to_numpy(float)]
            try:
                auc = float(roc_auc_score(y, x))
            except ValueError:
                auc = float("nan")
            rows.append({"invariant": inv, "metric": metric, "control": control, "auc_coupled_vs_control": auc})
    return pd.DataFrame(rows)


def threshold_sensitivity(coupled: pd.DataFrame, known: pd.DataFrame, holdout: pd.DataFrame, families: dict[str, dict[str, float]]) -> pd.DataFrame:
    rows = []
    for family, thresholds in families.items():
        for stack, invs in STACKS.items():
            fn = lambda d, invs=invs, thresholds=thresholds: stack_mask(d, invs, thresholds)
            c, k, h = retention_rejection(coupled, known, holdout, fn)
            rows.append({
                "threshold_family": family,
                "stack": stack,
                "invariants": "+".join(invs),
                "coupled_retention": c,
                "known_false_positive_rejection_rate": k,
                "holdout_rejection_rate": h,
                "balanced_score": c * k * h,
            })
    return pd.DataFrame(rows)


def soft_stacks(coupled: pd.DataFrame, known: pd.DataFrame, holdout: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
    rows = []
    optional = ["I2_ordered_distinction_persistence", "I4_counterfactual_affordance_relevance", "I5_minimal_recoverability", "I6_horizon_coherence"]
    for k in [1, 2, 3]:
        def mask(d: pd.DataFrame, k=k) -> pd.Series:
            mandatory = d[INVARIANTS["I3_component_non_erasure"]] >= thresholds["I3_component_non_erasure"]
            count = sum((d[INVARIANTS[inv]] >= thresholds[inv]).astype(int) for inv in optional)
            return mandatory & (count >= k)
        c, kr, h = retention_rejection(coupled, known, holdout, mask)
        rows.append({
            "rule": f"I3_mandatory_plus_{k}_of_I2_I4_I5_I6",
            "coupled_retention": c,
            "known_rejection": kr,
            "holdout_rejection": h,
            "balanced_score": c * kr * h,
        })
    ranks = rank_profile(pd.concat([coupled, known, holdout], ignore_index=True))
    for control, group in ranks.groupby(CONTROL_COL):
        rows.append({
            "rule": f"rank_profile_mean_{control}",
            "coupled_retention": float(group["mean_invariant_rank"].mean()),
            "known_rejection": np.nan,
            "holdout_rejection": np.nan,
            "balanced_score": np.nan,
        })
    return pd.DataFrame(rows)


def rank_profile(df: pd.DataFrame) -> pd.DataFrame:
    out = df[[CONTROL_COL, "alpha", "T"]].copy()
    rank_cols = []
    for inv, metric in INVARIANTS.items():
        col = f"rank_{inv}"
        out[col] = df[metric].rank(pct=True)
        rank_cols.append(col)
    out["mean_invariant_rank"] = out[rank_cols].mean(axis=1)
    return out


def pareto(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [INVARIANTS[i] for i in ["I2_ordered_distinction_persistence", "I3_component_non_erasure", "I4_counterfactual_affordance_relevance", "I5_minimal_recoverability", "I6_horizon_coherence"]]
    rows = []
    arr = df[metrics].to_numpy(float)
    controls = df[CONTROL_COL].to_numpy()
    for i, row in df.iterrows():
        dominated_by_control = False
        dominates_control = 0
        for j in range(len(df)):
            if i == df.index[j]:
                continue
            ge = np.all(arr[j] >= arr[df.index.get_loc(i)])
            gt = np.any(arr[j] > arr[df.index.get_loc(i)])
            if controls[j] != "none" and ge and gt:
                dominated_by_control = True
            if row[CONTROL_COL] == "none" and controls[j] != "none":
                ge2 = np.all(arr[df.index.get_loc(i)] >= arr[j])
                gt2 = np.any(arr[df.index.get_loc(i)] > arr[j])
                dominates_control += int(ge2 and gt2)
        rows.append({
            "control": row[CONTROL_COL],
            "alpha": row["alpha"],
            "T": row["T"],
            "dominated_by_control": dominated_by_control,
            "dominates_control_count": dominates_control,
            "pareto_region": "coupled_candidate" if row[CONTROL_COL] == "none" and not dominated_by_control else "overlap_or_control",
        })
    return pd.DataFrame(rows)


def i5_audit(df: pd.DataFrame, auc: pd.DataFrame) -> pd.DataFrame:
    corr = float(df["minimal_recoverability"].corr(df["p_viable_T"]))
    rows = []
    i5_auc = auc[auc["invariant"] == "I5_minimal_recoverability"]
    for _, r in i5_auc.iterrows():
        rows.append({
            "control": r["control"],
            "auc_coupled_vs_control": r["auc_coupled_vs_control"],
            "correlation_with_p_viable_T": corr,
            "duplicates_viability": bool(abs(corr) >= 0.70),
            "gate_ready": bool(r["auc_coupled_vs_control"] >= 0.75 and abs(corr) < 0.70),
        })
    return pd.DataFrame(rows)


def i6_audit(df: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
    rows = []
    th = thresholds["I6_horizon_coherence"]
    for control, group in df.groupby(CONTROL_COL):
        for T, gt in group.groupby("T"):
            rows.append({
                "control": control,
                "T": T,
                "mean_horizon_coherence": float(gt["horizon_coherence"].mean()),
                "retention_at_original_threshold": float((gt["horizon_coherence"] >= th).mean()),
                "overstrict": bool(control == "none" and (gt["horizon_coherence"] >= th).mean() < 0.30),
                "gate_ready": bool(control == "none" and (gt["horizon_coherence"] >= th).mean() >= 0.30),
            })
    return pd.DataFrame(rows)


def metric_correlations(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["p_viable_T", *INVARIANTS.values()]
    corr = df[cols].corr()
    return corr.reset_index().rename(columns={"index": "metric"})


def write_plots(out: Path, dropout: pd.DataFrame, dist: pd.DataFrame, thresh: pd.DataFrame, soft: pd.DataFrame, pareto_df: pd.DataFrame, i5: pd.DataFrame, i6: pd.DataFrame, corr: pd.DataFrame, df: pd.DataFrame) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(dropout["stack"], dropout["coupled_retention"])
    ax.set_title("Dropout waterfall")
    ax.set_ylabel("coupled retention")
    fig.tight_layout()
    fig.savefig(out / "dropout_waterfall.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    labels = list(INVARIANTS.keys())
    data = [df[INVARIANTS[i]].to_numpy(float) for i in labels]
    ax.violinplot(data, showmeans=True)
    ax.set_xticks(range(1, len(labels) + 1), labels, rotation=35, ha="right")
    ax.set_title("Invariant distribution violin")
    fig.tight_layout()
    fig.savefig(out / "invariant_distribution_violin.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    for stack, g in thresh.groupby("stack"):
        g = g[g["threshold_family"].str.startswith("sensitivity")]
        ax.plot(range(len(g)), g["balanced_score"], marker="o", label=stack)
    ax.set_title("Threshold retention/rejection curves")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "threshold_retention_rejection_curves.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ss = soft[soft["rule"].str.startswith("I3_")]
    ax.scatter(ss["coupled_retention"], ss["known_rejection"], s=80)
    for _, r in ss.iterrows():
        ax.annotate(r["rule"], (r["coupled_retention"], r["known_rejection"]), fontsize=7)
    ax.set_xlabel("coupled retention")
    ax.set_ylabel("known rejection")
    ax.set_title("Soft stack tradeoff")
    fig.tight_layout()
    fig.savefig(out / "soft_stack_tradeoff.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = np.where(df[CONTROL_COL] == "none", "tab:blue", "tab:orange")
    ax.scatter(df["ordered_persistence"], df["component_non_erasure"], c=colors)
    ax.set_xlabel("I2 ordered persistence")
    ax.set_ylabel("I3 component non-erasure")
    ax.set_title("Pareto profile scatter")
    fig.tight_layout()
    fig.savefig(out / "pareto_profile_scatter.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["p_viable_T"], df["minimal_recoverability"], c=colors)
    ax.set_xlabel("p_viable_T")
    ax.set_ylabel("I5 minimal recoverability")
    ax.set_title("I5 vs viability")
    fig.tight_layout()
    fig.savefig(out / "i5_vs_viability.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for control, g in i6.groupby("control"):
        ax.plot(g["T"], g["retention_at_original_threshold"], marker="o", label=control)
    ax.set_title("I6 horizon retention")
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(out / "i6_horizon_retention.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6))
    mat = corr.drop(columns=["metric"]).to_numpy(float)
    im = ax.imshow(mat, vmin=-1, vmax=1)
    ax.set_xticks(range(mat.shape[1]), corr.columns[1:], rotation=45, ha="right")
    ax.set_yticks(range(len(corr)), corr["metric"])
    fig.colorbar(im, ax=ax)
    ax.set_title("Metric correlation matrix")
    fig.tight_layout()
    fig.savefig(out / "metric_correlation_matrix.png", dpi=160)
    plt.close(fig)


def build_summary(started: float, used_existing: bool, dropout: pd.DataFrame, thresh: pd.DataFrame, soft: pd.DataFrame, pareto_df: pd.DataFrame, i5: pd.DataFrame, i6: pd.DataFrame, auc: pd.DataFrame) -> dict[str, object]:
    best_hard = thresh.sort_values("balanced_score", ascending=False).iloc[0].to_dict()
    soft_real = soft[soft["rule"].str.startswith("I3_")].sort_values("balanced_score", ascending=False)
    best_soft = soft_real.iloc[0].to_dict() if len(soft_real) else {}
    zero = dropout[dropout["coupled_retention"] <= 0]
    first_zero = zero.iloc[0]["stack"] if len(zero) else None
    main_drop = dropout.sort_values("marginal_dropout_from_previous", ascending=False).iloc[0]["added_invariant"]
    coupled_pareto = pareto_df[pareto_df["control"] == "none"]
    control_overlap = float(coupled_pareto["dominated_by_control"].mean()) if len(coupled_pareto) else 1.0
    strong_auc = auc[(auc["control"].isin(KNOWN_CONTROLS)) & (auc["auc_coupled_vs_control"] >= 0.75)].groupby("invariant").size()
    reopen = bool(
        best_soft.get("coupled_retention", 0) >= 0.30
        and best_soft.get("known_rejection", 0) >= 0.80
        and best_soft.get("holdout_rejection", 0) >= 0.50
        and len(strong_auc[strong_auc >= 2]) >= 2
        and control_overlap < 0.50
    )
    i5_dup = bool(i5["duplicates_viability"].mean() > 0.5) if len(i5) else True
    i5_gate = bool(i5["gate_ready"].mean() > 0.5) if len(i5) else False
    i6_over = bool(i6["overstrict"].mean() > 0.3) if len(i6) else True
    i6_gate = bool(i6["gate_ready"].mean() > 0.5) if len(i6) else False
    recommendation = "Close trajectory-native invariant branch for now; proceed with Probe 13 formal fiber-transport audit."
    if reopen:
        recommendation = "Reopen trajectory-native branch cautiously with a frozen soft-stack confirmation on new controls."
    return {
        "probe": "I0b_invariant_threshold_dropout_audit",
        "status": "COMPLETE",
        "used_existing_I0_outputs": used_existing,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "best_hard_stack": {
            "threshold_family": best_hard.get("threshold_family"),
            "stack": best_hard.get("stack"),
            "coupled_retention": best_hard.get("coupled_retention"),
            "known_rejection": best_hard.get("known_false_positive_rejection_rate"),
            "holdout_rejection": best_hard.get("holdout_rejection_rate"),
            "balanced_score": best_hard.get("balanced_score"),
        },
        "best_soft_stack": {
            "rule": best_soft.get("rule"),
            "coupled_retention": best_soft.get("coupled_retention"),
            "known_rejection": best_soft.get("known_rejection"),
            "holdout_rejection": best_soft.get("holdout_rejection"),
            "balanced_score": best_soft.get("balanced_score"),
        },
        "pareto_result": {
            "coupled_distinct_region": bool(control_overlap < 0.50),
            "control_overlap": control_overlap,
            "interpretation": "controls heavily overlap coupled profiles" if control_overlap >= 0.50 else "coupled profiles show partial Pareto separation",
        },
        "dropout": {
            "first_zero_retention_stack": first_zero,
            "main_dropout_invariant": main_drop,
        },
        "i5_recoverability": {
            "gate_ready": i5_gate,
            "duplicates_viability": i5_dup,
            "interpretation": "diagnostic only, not gate-ready" if not i5_gate else "potentially gate-ready",
        },
        "i6_horizon_coherence": {
            "gate_ready": i6_gate,
            "overstrict": i6_over,
            "interpretation": "diagnostic only, not gate-ready" if not i6_gate else "potentially gate-ready",
        },
        "trajectory_branch_reopened": reopen,
        "recommendation": recommendation,
        "next_probe": "Probe 13 formal fiber-transport audit",
    }


def main() -> None:
    args = parse_args()
    started = time.monotonic()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    df, used_existing = load_i0(args.i0_dir)
    coupled, known, holdout = split_frames(df)
    families = threshold_families(coupled, known)
    original = families["original"]
    dropout = build_dropout(coupled, known, holdout, original)
    dist = distribution_summary(df, coupled)
    auc = auc_table(coupled, pd.concat([known, holdout], ignore_index=True))
    thresh = threshold_sensitivity(coupled, known, holdout, families)
    soft = soft_stacks(coupled, known, holdout, original)
    pareto_df = pareto(pd.concat([coupled, known, holdout], ignore_index=True).reset_index(drop=True))
    i5 = i5_audit(pd.concat([coupled, known, holdout], ignore_index=True), auc)
    i6 = i6_audit(pd.concat([coupled, known, holdout], ignore_index=True), original)
    corr = metric_correlations(pd.concat([coupled, known, holdout], ignore_index=True))
    dropout.to_csv(args.out_dir / "dropout_by_invariant.csv", index=False)
    dist.to_csv(args.out_dir / "invariant_distribution_summary.csv", index=False)
    auc.to_csv(args.out_dir / "coupled_vs_control_auc.csv", index=False)
    thresh.to_csv(args.out_dir / "threshold_family_sensitivity.csv", index=False)
    soft.to_csv(args.out_dir / "soft_stack_results.csv", index=False)
    pareto_df.to_csv(args.out_dir / "pareto_profile_results.csv", index=False)
    i5.to_csv(args.out_dir / "i5_recoverability_audit.csv", index=False)
    i6.to_csv(args.out_dir / "i6_horizon_coherence_audit.csv", index=False)
    corr.to_csv(args.out_dir / "metric_correlations.csv", index=False)
    df.to_csv(args.out_dir / "estimator_report.csv", index=False)
    summary = build_summary(started, used_existing, dropout, thresh, soft, pareto_df, i5, i6, auc)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    closure = f"""# Probe I0b Closure Recommendation

Probe I0b reused the existing Probe I0 estimator table and did not rerun
simulation.

## Result

Trajectory branch reopened: `{summary['trajectory_branch_reopened']}`

Recommendation:

```text
{summary['recommendation']}
```

## Why

- Best hard stack: `{summary['best_hard_stack']['stack']}` under
  `{summary['best_hard_stack']['threshold_family']}`, balanced score
  `{summary['best_hard_stack']['balanced_score']}`.
- Best soft stack: `{summary['best_soft_stack']['rule']}`, balanced score
  `{summary['best_soft_stack']['balanced_score']}`.
- First zero-retention hard stack: `{summary['dropout']['first_zero_retention_stack']}`.
- Main dropout invariant: `{summary['dropout']['main_dropout_invariant']}`.
- Pareto interpretation: `{summary['pareto_result']['interpretation']}`.
- I5: `{summary['i5_recoverability']['interpretation']}`.
- I6: `{summary['i6_horizon_coherence']['interpretation']}`.
"""
    (args.out_dir / "closure_recommendation.md").write_text(closure, encoding="utf-8")
    write_plots(args.out_dir, dropout, dist, thresh, soft, pareto_df, i5, i6, corr, pd.concat([coupled, known, holdout], ignore_index=True))
    print("PROBE I0b: INVARIANT THRESHOLD AND DROPOUT AUDIT")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
