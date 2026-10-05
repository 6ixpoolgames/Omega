"""Descriptive contrasts and tables for the naive-count probe; no fitted score."""

import json

import numpy as np

from omega_v2.validation.naive_causal_count_v0 import GRAPHS, OUT


def main():
    summary = json.loads((OUT / "summary.json").read_text())
    lookup = {(g["panel"], g["regime"], g["barrier"], g["preparation"]): g
              for g in summary["groups"]}
    comparisons = []
    for g in summary["groups"]:
        if g["preparation"] == "equilibrium":
            continue
        base = lookup[g["panel"], g["regime"], g["barrier"], "equilibrium"]
        for graph in GRAPHS:
            for a, b in zip(g["graphs"][graph][1:], base["graphs"][graph][1:], strict=True):
                row = {k: g[k] for k in ("panel", "regime", "barrier", "preparation")}
                row.update({"graph": graph, "time": a["time"], "metrics": {}})
                for metric in a["mean"]:
                    delta = np.array(a["chain_means"][metric]) - b["chain_means"][metric]
                    row["metrics"][metric] = {
                        "difference": float(delta.mean()),
                        "paired_chain_se": float(delta.std(ddof=1) / np.sqrt(len(delta))),
                        "ratio": a["mean"][metric] / b["mean"][metric] if b["mean"][metric] else None}
                row["difference_log2_mean_routes"] = a["log2_mean_routes"] - b["log2_mean_routes"]
                comparisons.append(row)
    (OUT / "comparisons.json").write_text(json.dumps(comparisons, indent=2), encoding="utf-8")
    lines = ["# Complete T=20 preparation contrasts", "",
             "Ratios of native sample means, except route column: difference of mean log2 route count.",
             "Every comparison is dispersed fueled / equilibrium. These preparations do not match free energy.",
             "", "| Panel | Regime | Barrier | Events | Cone sum | Cone sum without fuel edges | Mean log2 routes difference |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for key in sorted(lookup):
        panel, regime, barrier, prep = key
        if prep != "dispersed_fueled":
            continue
        a, b = lookup[key], lookup[panel, regime, barrier, "equilibrium"]
        x, y = a["graphs"]["full"][-1]["mean"], b["graphs"]["full"][-1]["mean"]
        u = a["graphs"]["without_fuel_register"][-1]["mean"]["cone_sum"]
        v = b["graphs"]["without_fuel_register"][-1]["mean"]["cone_sum"]
        lines.append(f"| {panel} | {regime} | {barrier} | {x['events']/y['events']:.3f} | "
                     f"{x['cone_sum']/y['cone_sum']:.3f} | {u/v:.3f} | "
                     f"{x['log2_routes']-y['log2_routes']:+.3f} |")
    (OUT / "all_contrasts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"comparisons": len(comparisons), "table": str(OUT / "all_contrasts.md")}))


if __name__ == "__main__":
    main()
