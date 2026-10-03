"""Small exact exploratory aggregation run; no stochastic simulation sweep."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from omega_v2.finite.frame_aggregation import (
    INPUTS,
    SOURCES,
    content_frontiers,
    enumerate_routes,
    envelope,
    information,
    native_frames,
)

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "docs/research_notes/omega_v2/frame_aggregation_v0"


def cases():
    s, a, b = SOURCES
    u, v = (a ^ 255) & (b ^ 255), s ^ 255
    banks = {
        "copies": ((s, s, s), [3, 0]),
        "plural": ((s, a, b), [3, 0]),
        "access_A": ((s ^ a, 0, s ^ 255), [3, 2]),
        "access_B": ((0, s, a), [3, 2]),
        "repair_A": ((u, u & v, v), [3, 3]),
        "repair_B": ((u, u, v), [3, 3]),
    }
    result = {}
    for name, (records, prep) in banks.items():
        result[name] = {
            "records": records,
            "preparation_bill": prep,
            "bath": (0, 0, 0),
            "loss_bill": [0, 0],
        }
    for name in ("repair_A", "repair_B", "copies", "plural"):
        records, prep = banks[name]
        for lost in range(3):
            remaining = list(records)
            remaining[lost] = 0
            bath = [0, 0, 0]
            bath[lost] = records[lost]
            result[f"{name}_loss{lost}"] = {
                "records": tuple(remaining),
                "bath": tuple(bath),
                "lost": lost,
                "repair_target": records[lost],
                "preparation_bill": prep,
                "loss_bill": [3, 0],
            }
    return result


def laws():
    return {
        "fair": [1 / 8] * 8,
        "biased_0.2": [0.2 ** sum(x) * 0.8 ** (3 - sum(x)) for x in INPUTS],
        "common_bit": [0.5, 0, 0, 0, 0, 0, 0, 0.5],
    }


def response_steps(routes, query):
    return min((r.steps for r in routes if r.outputs[0] == query), default=None)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    outputs = {}
    catalog = {}
    for name, case in cases().items():
        records = case["records"]
        gates, routes = enumerate_routes(records)
        fronts = content_frontiers(routes)
        catalog[name] = {
            "case": case,
            "gates": gates,
            "routes": [asdict(r) for r in routes],
            "content_frontiers": fronts,
        }
        outputs[name] = {
            "states_searched": len(routes),
            "content_partitions": len(fronts),
            "not_f1_steps": response_steps(routes, SOURCES[1] ^ 255),
            "repair_steps": response_steps(routes, case["repair_target"])
            if "repair_target" in case
            else None,
            "laws": {},
        }
        for law, weights in laws().items():
            frames = native_frames(records, weights)
            outputs[name]["laws"][law] = {
                "bank": information(records, weights),
                "native_frames": frames,
                "raw_subset_tally_bits": sum(f["bits"] for f in frames),
                "profile": envelope(routes, weights, nrecords=3, depth=2),
                "whole_retained": information(SOURCES + records + case["bath"], weights),
            }
    catalog_path = DEST / "routes.json"
    catalog_path.write_text(json.dumps(catalog, separators=(",", ":")) + "\n", encoding="utf-8")
    result = {
        "version": "joint_content_envelope_v0",
        "choice": "One feasible joint delivery; count its information once; retain partition access frontiers. Max-envelope is a compression, not an all-location tally.",
        "source_laws": laws(),
        "inputs": INPUTS,
        "hardware": {
            "record_registers": 3,
            "blank_outputs": 2,
            "bath_registers": 3,
            "depth": 2,
            "gate_bill": ["serial_steps", "two_control_gates"],
            "controls": "either polarity; at most two; records read-only",
        },
        "access": "Original sources and loss bath retained, inaccessible to decoder. Mathematical frames are not extra apparatus. No uniform law on searched programs.",
        "source_hashes": {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__), ROOT / "omega_v2/finite/frame_aggregation.py"]
        },
        "cases": outputs,
    }
    (DEST / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    followup = {}
    for name in ("access_A", "access_B"):
        case = cases()[name]
        gates, routes = enumerate_routes(case["records"], depth=3)
        followup[name] = {
            "case": case,
            "gates": gates,
            "routes": [asdict(r) for r in routes],
            "not_f1_steps": response_steps(routes, SOURCES[1] ^ 255),
            "profiles": {
                law: envelope(routes, w, nrecords=3, depth=3) for law, w in laws().items()
            },
        }
    (DEST / "depth3_followup.json").write_text(
        json.dumps(followup, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    write_report(outputs, followup)
    compact = {name: {k: v for k, v in row.items() if k != "laws"} for name, row in outputs.items()}
    print(json.dumps(compact, indent=2))


def at_budget(case, law, budget):
    return next(r for r in case["laws"][law]["profile"] if r["budget"] == budget)


def write_report(data, followup):
    lines = [
        "# Frame aggregation prototype v0",
        "",
        "3 October 2026 · exploratory finite implementation",
        "",
        "## Executable choice",
        "",
        (
            "This is the first bounded interpretation of the adopted count-once access proposal. "
            "For each jointly executable output bundle, use I(X;Y)=H(Y), then V=2^(H(Y)-H(X)). "
            "Information-equivalent output partitions have one catalog entry with Pareto access routes. "
            "The underlying physical programs, wire positions and residual records are retained, not quotiented away."
        ),
        "",
        (
            "At each input-frame-size/step/Toffoli budget, report the largest jointly deliverable information "
            "and a witness. This maximum is an explicit exploratory choice: an existential content envelope, "
            "not actual chooser behavior or a sum of the access distributed across the world. It is one narrow "
            "implementation of cheapest access, not a complete realization of Opus's all-frame aggregation. "
            "The complete partition/route catalog stays alongside it so losses from compression remain visible."
        ),
        "",
        (
            "Two blank destination registers are allocated in every arrangement. One execution must deliver "
            "both outputs within the shared budget. Alternative programs are never pooled into fictitious "
            "joint information. Preparation and loss bills are reported separately from remaining decoder "
            "budget; these are exhibited gate bills, not thermodynamic or globally minimal costs."
        ),
        "",
        (
            "The language contains X, CNOT and Toffoli with either control polarity; controls may read the "
            "three record positions or the other output. Outputs start blank; inputs are read-only. "
            "Search is exhaustive only to two gates in this language. Equivalent restart states are cached. "
            "A null repair cost means no decoder inside this bound, not physical impossibility."
        ),
        "",
        "## Initial preparations",
        "",
        "Three retained source bits s,a,b supply eight assignments. With u=(NOT a) AND (NOT b) and v=NOT s:",
        "",
        "- copies=(s,s,s), plural=(s,a,b): three-CNOT preparations each.",
        "- access_A=(s XOR a,0,NOT s), access_B=(0,s,a): existing three-step/two-Toffoli witnesses.",
        "- repair_A=(u,u AND v,v), repair_B=(u,u,v): existing three-Toffoli witnesses.",
        "",
        (
            "For each loss variant, one record is swapped into an allocated inaccessible bath position "
            "at three additional CNOT steps. Sources, remaining records, bath and output residual are retained. "
            "The entire source law is available in summary.json; no physical noise is removed. "
            "Common-bit inputs deliberately include dependence. No loss-location distribution is assumed."
        ),
        "",
        "## Readouts at two steps, two two-control gates, up to three input registers",
        "",
        "| Preparation / law | Bank bits | Syn | Raw subset tally (bits) | Jointly delivered bits | Normalized V |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in ("copies", "plural", "access_A", "access_B", "repair_A", "repair_B"):
        for law in ("fair", "biased_0.2", "common_bit"):
            row = data[name]["laws"][law]
            cell = at_budget(data[name], law, [3, 2, 2])
            lines.append(
                f"| {name} / {law} | {row['bank']['bits']:.6f} | {row['bank']['syn']:.6f} | "
                f"{row['raw_subset_tally_bits']:.6f} | {cell['bits']:.6f} | {cell['volume']:.6f} |"
            )
    lines += [
        "",
        (
            "At biased inputs, outputs (NOT s AND NOT a, NOT s AND NOT b) deliver "
            "1.742733 bits versus 1.443856 for two direct copies. Both take two steps, "
            "but the composed route uses two Toffolis rather than two CNOTs. "
            "The vector budget preserves that difference; all three input positions are used."
        ),
        "",
        (
            "Normalized volumes compare preparations under one encompassing source law. "
            "Changing that law also changes the normalization; rows from different laws "
            "are sensitivity cases, not a single ranking of worlds."
        ),
        "",
        "## Checks on what the aggregation loses",
        "",
    ]
    for law in laws():
        a = [p["bits"] for p in data["access_A"]["laws"][law]["profile"]]
        b = [p["bits"] for p in data["access_B"]["laws"][law]["profile"]]
        lines.append(
            f"- access_A versus access_B, {law}: {sum(abs(x - y) > 1e-12 for x, y in zip(a, b, strict=True))} "
            f"of {len(a)} profile cells differ."
        )
    lines += [
        (
            f"- The specific response NOT a still costs {data['access_A']['not_f1_steps']} versus "
            f"{data['access_B']['not_f1_steps']} steps. Equal envelope cells do not imply identical response access."
        ),
        (
            "- With fair plural inputs, one step delivers at most one bit; two CNOT steps deliver two. "
            "Separately available one-step responses do not become a two-bit one-step delivery."
        ),
        (
            "- With fully correlated sources, a perfect record has Syn=-2 and V=1. "
            "Signed Syn is reported, not used as an aggregation bonus or penalty."
        ),
        "",
        "## Local loss and bounded repair",
        "",
        "| Preparation | Loss 0: repair steps | Loss 1: repair steps | Loss 2: repair steps |",
        "|---|---:|---:|---:|",
    ]
    for name in ("copies", "plural", "repair_A", "repair_B"):
        vals = [data[f"{name}_loss{i}"]["repair_steps"] for i in range(3)]
        lines.append(
            f"| {name} | "
            + " | ".join(str(v) if v is not None else ">2 or impossible" for v in vals)
            + " |"
        )
    lines += ["", "## Targeted depth-three follow-up", ""]
    for law in laws():
        a = [p["bits"] for p in followup["access_A"]["profiles"][law]]
        b = [p["bits"] for p in followup["access_B"]["profiles"][law]]
        differences = sum(abs(x - y) > 1e-12 for x, y in zip(a, b, strict=True))
        lines.append(
            f"- {law}: {differences} of {len(a)} envelope cells differ at the extended bound."
        )
    lines += [
        (
            f"The response NOT a still costs {followup['access_A']['not_f1_steps']} versus "
            f"{followup['access_B']['not_f1_steps']} steps. A surviving tie is not resolved "
            "merely by this extra decoding step. All new routes and profiles are in "
            "[the follow-up evidence](frame_aggregation_v0/depth3_followup.json)."
        ),
        "",
        (
            "The loss-conditioned profiles are retained in the evidence, without an arbitrary average "
            "over faults. Additional copies can preserve access after loss even when they add no distinct source content. "
            "This is a consequence of routing and residual dynamics, not an assigned redundancy reward."
        ),
        "",
        "## Scope and reproduction",
        "",
        (
            "These are exact finite diagnostic calculations (floating-point entropy), not a gas experiment, "
            "quantum interference run, endogenous generativity test or completed lushness invariant. "
            "The envelope deliberately leaves location distribution, recurrence and the arbitration of "
            "crossing profiles unresolved. The prototype makes those limitations inspectable instead of "
            "fitting coefficients to preferred outcomes."
        ),
        "",
        "Run from the repository root:",
        "",
        "    .venv/Scripts/python.exe -m omega_v2.validation.frame_aggregation_v0",
        "",
        (
            "Evidence: [summary and profiles](frame_aggregation_v0/summary.json), "
            "[programs, physical residuals and content frontiers](frame_aggregation_v0/routes.json)."
        ),
        "",
    ]
    (DEST.parent / "frame_aggregation_report_v0.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
