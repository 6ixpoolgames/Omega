"""Compare all predictors on explicit memory loss and costly archive access."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from omega_v2.experiments import frame_information_audit_v0 as fixtures
from omega_v2.finite import continuation_prediction as predictor
from omega_v2.validation.artifacts import write_json
from omega_v2.validation.continuation_equivalence_audit_v0 import encode
from omega_v2.validation.operational_continuation_comparison_v0 import ROOT, _git

F = Fraction
SOURCES = (
    fixtures.PROTOCOL,
    "docs/research_notes/omega_v2/frame_information_audit_v0.md",
    "omega_v2/finite/model.py", "omega_v2/finite/controllers.py",
    "omega_v2/finite/operational_continuation.py", "omega_v2/finite/continuation_prediction.py",
    "omega_v2/finite/information_frames.py",
    "omega_v2/experiments/operational_continuation_comparison_v0.py",
    "omega_v2/experiments/frame_information_audit_v0.py",
    "omega_v2/validation/artifacts.py",
    "omega_v2/validation/operational_continuation_comparison_v0.py",
    "omega_v2/validation/continuation_equivalence_audit_v0.py",
    "omega_v2/validation/frame_information_audit_v0.py",
    "tests/test_frame_information_audit.py",
)


def _score(laws):
    return sum((weight * p for q, weight in fixtures.WEIGHTS.rows
                for trace, p in laws[q].rows if fixtures.correct_guess(q, trace)), F(0))


def _route_support(prediction, route):
    return sorted({(trace.elapsed, trace.cost, trace.censored)
                   for policy, laws in prediction.laws.items() if policy.startswith(route + ":")
                   for law in laws.values() for trace in law.support})


def _means(cells):
    return sorted({cell["mean"] for cell in cells.values()})


def run_audit():
    cases, evidence, gates = {}, {}, []

    def gate(name, observed, expected=True):
        gates.append({"name": name, "observed": observed, "expected": expected,
                      "passed": observed == expected})

    expected_scores = {"remember": F(1), "erased": F(1, 2), "sealed": F(1, 2), "retrieve": F(1),
                       "short_deadline": F(1, 2), "low_budget": F(1, 2), "zero_budget": None}
    for name, fixture in fixtures.control_panel().items():
        e, interface = fixture.experiment, fixture.interface
        c1, quotient = predictor.build_c1(e, interface), predictor.build_quotient(e, interface)
        predictions = {"reference": predictor.reference_prediction(e, interface),
                       "c1": predictor.predict_graph(c1), "quotient": predictor.predict_graph(quotient),
                       "memoized": predictor.predict_memoized(e, interface)}
        reference = predictions["reference"]
        gate(f"{name}.partitions", predictor.same_partitions(c1.decoding, quotient.decoding))
        results, frames = {}, {}
        for method, prediction in predictions.items():
            prefix = f"{name}.{method}"
            if method != "reference":
                gate(f"{prefix}.exact_laws", predictor.same_predictions(prediction, reference))
            score, witness = predictor.best_probability(prediction, fixtures.WEIGHTS, fixtures.correct_guess)
            gate(f"{prefix}.best_guess", score, expected_scores[name])
            valid = (score is None and witness is None and not reference.laws) or (
                witness in reference.laws and score == _score(reference.laws[witness])
            )
            gate(f"{prefix}.reference_witness", valid)
            rejected = 16 if name == "zero_budget" else 8 if name == "low_budget" else 0
            gate(f"{prefix}.rejected_count", len(prediction.rejected), rejected)
            if name == "low_budget":
                gate(f"{prefix}.rejected_read_costs", prediction.rejected,
                     {f"retrieve:{a}{b}{c}": 6 for a in (0, 1) for b in (0, 1) for c in (0, 1)})
            skip_support, read_support = (_route_support(prediction, route) for route in ("skip", "retrieve"))
            gate(f"{prefix}.skip_time_cost", skip_support, [] if name == "zero_budget" else [(4, 4, False)])
            gate(f"{prefix}.read_time_cost", read_support, [] if name in ("zero_budget", "low_budget") else (
                [(4, 5, True)] if name == "short_deadline" else [(5, 6, False)]
            ))
            if name == "short_deadline":
                gate(f"{prefix}.read_censored_mass", sorted({sum((p for t, p in law.rows if t.censored), F(0))
                     for policy, laws in prediction.laws.items() if policy.startswith("retrieve:")
                     for law in laws.values()}), [F(1)])
            results[method] = {"best_guess": score, "witness": witness, "admitted": len(prediction.laws),
                               "rejected": dict(prediction.rejected),
                               "skip_support": skip_support, "read_support": read_support}
            if name in ("remember", "erased", "sealed", "retrieve"):
                frame = fixtures.frame_diagnostics(prediction)
                read = fixtures.read_diagnostics(prediction)
                frames[method] = {"erasure": frame, "retrieval": read}
                for kind in ("history_forward", "accessible_reverse"):
                    gate(f"{prefix}.{kind}.refinement", frame[kind]["after_refines_before"])
                    gate(f"{prefix}.{kind}.tower", frame[kind]["tower_holds_for_readout"])
                for property_name in ("after_refines_before", "tower_holds_for_readout"):
                    gate(f"{prefix}.accessible_forward.{property_name}",
                         frame["accessible_forward"][property_name], name == "remember")
                gate(f"{prefix}.historical_posterior", _means(frame["history_after"]), [F(0), F(1)])
                gate(f"{prefix}.accessible_posterior", _means(frame["accessible_after"]),
                     [F(0), F(1)] if name == "remember" else [F(1, 2)])
                gate(f"{prefix}.after_read_posterior", _means(read["after_read"]),
                     [F(0), F(1)] if name in ("remember", "retrieve") else [F(1, 2)])
                gate(f"{prefix}.read_refinement", read["read_refinement"]["after_refines_before"])
                gate(f"{prefix}.read_tower", read["read_refinement"]["tower_holds_for_readout"])
        cases[name] = {"states": len(e.system.states), "programs": len(e.teams), "horizon": e.horizon,
                       "budget": e.budget, "classes_by_depth": [len(layer) for layer in c1.layers],
                       "methods": results}
        evidence[name] = {"fixture": fixture, "c1_graph": c1, "quotient_partitions": quotient.decoding,
                          "predictions": predictions, "frame_diagnostics": frames}
    summary = {"status": "PASS" if all(g["passed"] for g in gates) else "FAIL",
               "scope": "known-answer frame and controller information audit",
               "input_weights": fixtures.WEIGHTS, "cases": cases, "gates": gates}
    return summary, evidence


def render_report(summary):
    lines = ["# Frame information audit v0", "", f"Status: {summary['status']}",
             f"Gates: {sum(g['passed'] for g in summary['gates'])}/{len(summary['gates'])}", "",
             "Exact finite controls; no empirical, normative, or C1 novelty claim.", "",
             "| Case | Horizon | Budget | Full | C1 | Quotient | Memoized |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for name, case in summary["cases"].items():
        scores = " | ".join(str(case["methods"][m]["best_guess"])
                            for m in ("reference", "c1", "quotient", "memoized"))
        lines.append(f"| {name} | {case['horizon']} | {case['budget']} | {scores} |")
    lines += ["", "None means no admissible program. Source hashes are in provenance.json.",
              "Evidence is exact tagged JSON, with one complete case per line to keep the",
              "generated diff compact. It includes models, program tables, predictions,",
              "information-cell posteriors, and refinement counterexamples.", "", "## Gates", ""]
    lines.extend(f"- {'PASS' if g['passed'] else 'FAIL'} {g['name']}" for g in summary["gates"])
    return "\n".join(lines) + "\n"


def retain(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=False)
    summary, evidence = run_audit()
    write_json(out_dir / "summary.json", encode(summary))
    # Complete JSON, not lossy repr or an abridged probability summary.
    (out_dir / "evidence.json").write_text("{\n" + ",\n".join(
        "  " + json.dumps(name) + ": " + json.dumps(encode(evidence[name]), sort_keys=True, separators=(",", ":"))
        for name in sorted(evidence)
    ) + "\n}\n", encoding="utf-8")
    write_json(out_dir / "provenance.json", {
        "revision": _git("rev-parse", "HEAD"), "python": sys.version,
        "source_git_status": _git("status", "--porcelain", "--", *SOURCES),
        "source_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES},
    })
    (out_dir / "report.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    out_dir = args.out_dir or ROOT / "results/local_runs/frame_information" / datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    summary = retain(out_dir)
    print(json.dumps({"status": summary["status"], "gates": len(summary["gates"]), "output": str(out_dir)}))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
