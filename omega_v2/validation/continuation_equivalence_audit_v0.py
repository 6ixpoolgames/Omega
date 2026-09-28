"""Retain the development equivalence audit, exact controls, and complete costs."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import fields, is_dataclass, replace
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter_ns, process_time_ns

from omega_v2.experiments.continuation_equivalence_audit_v0 import (
    PROTOCOL,
    control_panel,
    known_answer_gates,
)
from omega_v2.finite import continuation_prediction as predictor
from omega_v2.validation.artifacts import write_json
from omega_v2.validation.operational_continuation_comparison_v0 import ROOT, _git

SOURCES = (
    PROTOCOL,
    "docs/research_notes/omega_v2/continuation_audit_followup_protocol_v0.md",
    "docs/research_notes/omega_v2/continuation_prediction_pilot_protocol_v0.md",
    "omega_v2/finite/model.py", "omega_v2/finite/controllers.py",
    "omega_v2/finite/operational_continuation.py",
    "omega_v2/finite/continuation_prediction.py",
    "omega_v2/experiments/operational_continuation_comparison_v0.py",
    "omega_v2/experiments/continuation_equivalence_audit_v0.py",
    "omega_v2/validation/artifacts.py",
    "omega_v2/validation/operational_continuation_comparison_v0.py",
    "omega_v2/validation/continuation_equivalence_audit_v0.py",
    "tests/test_continuation_equivalence_audit.py",
)


def encode(value):
    """Lossless tagged JSON for the concrete primitive/dataclass panel vocabulary.

    Reject unsupported opaque objects instead of pretending repr is a codec.
    Tags distinguish tuples, sets, rational values, and non-string map keys.
    """
    if isinstance(value, Fraction):
        return {"rational": [value.numerator, value.denominator]}
    if is_dataclass(value):
        return {"type": type(value).__name__, **{f.name: encode(getattr(value, f.name)) for f in fields(value)}}
    if isinstance(value, tuple):
        return {"tuple": [encode(v) for v in value]}
    if isinstance(value, frozenset):
        return {"frozenset": sorted((encode(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))}
    if isinstance(value, dict):
        if all(isinstance(k, str) for k in value):
            return {k: encode(v) for k, v in value.items()}
        return {"mapping": [[encode(k), encode(v)] for k, v in value.items()]}
    if isinstance(value, list):
        return [encode(v) for v in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"no evidence codec for {type(value).__name__}")


def serialized_bytes(value):
    return len(json.dumps(encode(value), sort_keys=True, separators=(",", ":")).encode("utf-8"))


def measured(function, *args):
    wall, cpu = perf_counter_ns(), process_time_ns()
    value = function(*args)
    return value, process_time_ns() - cpu, perf_counter_ns() - wall


def run_audit():
    panel = control_panel()
    predictions = {name: {} for name in ("reference", "c1", "quotient", "memoized")}
    gates, evidence, cases = [], {}, {}

    def gate(name, observed, expected=True):
        gates.append({"name": name, "observed": observed, "expected": expected, "passed": observed == expected})

    for name, fixture in panel.items():
        e, interface = fixture.experiment, fixture.interface
        reference, reference_cpu, reference_wall = measured(predictor.reference_prediction, e, interface)
        predictions["reference"][name] = reference
        graphs, costs = {}, {}
        for method, builder in (("c1", predictor.build_c1), ("quotient", predictor.build_quotient)):
            graph, build_cpu, build_wall = measured(builder, e, interface)
            prediction, query_cpu, query_wall = measured(predictor.predict_graph, graph)
            predictions[method][name] = prediction
            graphs[method] = graph
            costs[method] = {
                **predictor.cost_record(build_cpu, query_cpu),
                "extraction_wall_ns": build_wall, "prediction_wall_ns": query_wall,
                "total_wall_ns": build_wall + query_wall,
                "representation_bytes": serialized_bytes(graph),
                "result_bytes": serialized_bytes(prediction),
            }
            gate(f"{name}.{method}_exact", predictor.same_predictions(reference, prediction))
            gate(f"{name}.{method}_accounting", costs[method]["total_cpu_ns"] == build_cpu + query_cpu)
        memoized, memo_cpu, memo_wall = measured(predictor.predict_memoized, e, interface)
        predictions["memoized"][name] = memoized
        costs["memoized"] = {**predictor.cost_record(0, memo_cpu), "total_wall_ns": memo_wall,
                             "cache_entries": memoized.cache_entries, "result_bytes": serialized_bytes(memoized)}
        gate(f"{name}.memoized_exact", predictor.same_predictions(reference, memoized))
        gate(f"{name}.partitions", predictor.same_partitions(graphs["c1"].decoding, graphs["quotient"].decoding))
        cases[name] = {"states": len(e.system.states), "teams": len(e.teams), "horizon": e.horizon,
                       "budget": e.budget, "input_bytes": serialized_bytes(fixture),
                       "layer_class_counts": [len(layer) for layer in graphs["c1"].layers],
                       "reference_cpu_ns": reference_cpu, "reference_wall_ns": reference_wall,
                       "costs": costs}
        evidence[name] = {"fixture": fixture, "graphs": graphs,
                          "predictions": {method: rows[name] for method, rows in predictions.items()}}
    for method, rows in predictions.items():
        controls, certificates = known_answer_gates(rows)
        gates.extend({**g, "name": f"{method}.{g['name']}"} for g in controls)
        evidence[f"{method}_certificates"] = certificates
        for extended, original in (("equivalent_mimic", "live"), ("nuisance_partial_cutoff", "partial_cutoff")):
            gate(f"{method}.{extended}_full_invariance", predictor.same_predictions(rows[extended], rows[original]))
    gate("cost_accounting.synthetic_nonzero_extraction", predictor.cost_record(7, 11)["total_cpu_ns"], 18)
    costs = evidence["cost_distinction"]["graphs"]["c1"].decoding
    gate("edge_cost.base_equal", costs[0]["cheap"] == costs[0]["dear"])
    gate("edge_cost.depth_one_separates", costs[1]["cheap"] != costs[1]["dear"])
    for extended, original in (("equivalent_mimic", "live"), ("nuisance_partial_cutoff", "partial_cutoff")):
        graph = evidence[extended]["graphs"]["c1"]
        base = evidence[original]["graphs"]["c1"]
        pulled_back = tuple({(s, bit): layer[s] for s in layer for bit in (0, 1)} for layer in base.decoding)
        gate(f"{extended}.partition_invariance", predictor.same_partitions(graph.decoding, pulled_back))
    fixture = panel["live"]
    e, interface = fixture.experiment, fixture.interface
    incompatible = replace(e.teams[0][0], observation_rows=tuple((s, "ready") for s in e.system.states),
                           policy_rows=((0, "ready", 0),), update_rows=((0, "ready", 0),))
    invalid = replace(e, teams=((incompatible,),))
    failures = {}
    for method, function in (("c1", predictor.build_c1), ("quotient", predictor.build_quotient),
                             ("reference", predictor.reference_prediction), ("memoized", predictor.predict_memoized)):
        try:
            function(invalid, interface)
        except ValueError as error:
            failures[method] = str(error)
        else:
            failures[method] = None
        gate(f"interface.{method}.reject_incompatible", failures[method] is not None
             and "share" in failures[method])
    evidence["invalid_shared_interface"] = {"experiment": invalid, "interface": interface,
                                            "rejections": failures}
    summary = {"status": "PASS" if all(g["passed"] for g in gates) else "FAIL",
               "scope": "public development controls; no held-out or efficiency claim",
               "cases": cases, "gates": gates}
    return summary, evidence


def render_report(summary):
    lines = ["# Bounded continuation graph equivalence audit v0", "", f"Status: {summary['status']}",
             f"Gates: {sum(g['passed'] for g in summary['gates'])}/{len(summary['gates'])}", "",
             "Public development controls. No independent experiment, novelty, efficiency,",
             "or lushness result. Exact predictions, models, graphs, and certificates are",
             "in evidence.json. Timings and whole-representation bytes are in summary.json.", "",
             "| Case | States | Horizon | Classes by depth |", "| --- | --- | --- | --- |"]
    for name, case in summary["cases"].items():
        lines.append(f"| {name} | {case['states']} | {case['horizon']} | {case['layer_class_counts']} |")
    lines += ["", "One unreplicated timing per method/case; CPU clock resolution may report zero.",
              "Extraction and prediction are charged; serialization, grading, and writing",
              "evidence are outside method timings. Cache entry counts are not peak memory.",
              "No primary baseline, hardware cap, task workload, or independent test set is frozen.", "", "## Gates", ""]
    lines.extend(f"- {'PASS' if g['passed'] else 'FAIL'} {g['name']}" for g in summary["gates"])
    return "\n".join(lines) + "\n"


def retain(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=False)
    summary, evidence = run_audit()
    write_json(out_dir / "summary.json", encode(summary))
    (out_dir / "evidence.json").write_text("{\n" + ",\n".join(
        "  " + json.dumps(name) + ": " + json.dumps(encode(evidence[name]), sort_keys=True, separators=(",", ":"))
        for name in sorted(evidence)
    ) + "\n}\n", encoding="utf-8")
    write_json(out_dir / "provenance.json", {
        "revision": _git("rev-parse", "HEAD"), "git_status": _git("status", "--porcelain"),
        "source_git_status": _git("status", "--porcelain", "--", *SOURCES),
        "python": sys.version, "platform": platform.platform(), "processor": platform.processor(),
        "source_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES},
    })
    (out_dir / "report.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    out_dir = args.out_dir or ROOT / "results/local_runs/continuation_equivalence" / datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    summary = retain(out_dir)
    print(json.dumps({"status": summary["status"], "gates": len(summary["gates"]), "output": str(out_dir)}))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
