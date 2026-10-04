"""Retain exact recovery controls, all outcomes, and long-run certificates."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from omega_v2.experiments import recovery_dynamics_v0 as fixtures
from omega_v2.finite import recovery_dynamics as core
from omega_v2.validation.artifacts import write_json
from omega_v2.validation.continuation_equivalence_audit_v0 import encode
from omega_v2.validation.operational_continuation_comparison_v0 import ROOT, _git

F = Fraction
SOURCES = (
    fixtures.PROTOCOL,
    "omega_v2/finite/model.py", "omega_v2/finite/controllers.py",
    "omega_v2/finite/recovery_dynamics.py", "omega_v2/experiments/recovery_dynamics_v0.py",
    "omega_v2/validation/recovery_dynamics_v0.py", "omega_v2/validation/artifacts.py",
    "omega_v2/validation/continuation_equivalence_audit_v0.py",
    "omega_v2/validation/operational_continuation_comparison_v0.py",
    "tests/test_recovery_dynamics.py",
)


def readouts(chain, rows):
    result, cumulative_hazard = [], F(0)
    for n, row in enumerate(rows):
        totals = dict.fromkeys(fixtures.OUTCOMES, F(0))
        for state, p in row["law"].rows:
            kind = chain.outcomes[state]
            totals[kind] += p
        reset = sum((totals[k] for k in fixtures.RESET), F(0))
        hazard = None
        if n and result[-1]["live"]:
            hazard = (reset - result[-1]["reset"]) / result[-1]["live"]
            cumulative_hazard += hazard
        result.append({"deadline": n, **totals, "reset": reset,
                       "no_reset": totals["live"] + totals["dead"],
                       "reset_hazard": hazard, "cumulative_hazard": cumulative_hazard,
                       "risk_set_exhausted": n > 0 and result[-1]["live"] == 0,
                       "expected_cost": row["expected_cost"]})
    return result


def _maximizers(scores):
    best = max(scores.values())
    return {"value": best, "programs": tuple(p for p, score in scores.items() if score == best)}


def run_audit():
    gates, cases, evidence = [], {}, {}

    def gate(name, observed, expected=True):
        gates.append({"name": name, "observed": observed, "expected": expected,
                      "passed": observed == expected})

    for name, world in fixtures.control_panel().items():
        settings = world.settings
        possible = fixtures.possible_recovery(world)
        gate(f"{name}.possible_from_start", fixtures.State() in possible, settings.working)
        programs, raw = {}, {}
        for program in world.programs:
            prefix = f"{name}.{program.controller_id}"
            chain = fixtures.product_chain(world, program)
            propagated = core.propagate(chain, 30)
            measures = readouts(chain, propagated)
            paths = {}
            for n in range(7):
                paths[n] = core.full_paths(chain, n)
                marginal = paths[n].pushforward(lambda path: path.states[-1])
                gate(f"{prefix}.paths_{n}.marginal", propagated[n]["law"].mass_map, marginal.mass_map)
                cost = tuple(sum((p * path.cost[i] for path, p in paths[n].rows), F(0)) for i in range(3))
                gate(f"{prefix}.paths_{n}.cost_vector", propagated[n]["expected_cost"], cost)
                joint = paths[n].pushforward(lambda path: (path.states[-1], path.cost))
                gate(f"{prefix}.paths_{n}.joint_cost_law", core.joint_cost_law(chain, n).mass_map, joint.mass_map)
                gate(f"{prefix}.paths_{n}.stops", all(
                    all(s not in chain.terminals for s in path.states[:-1])
                    and len(path.charges) == len(path.states) - 1
                    for path in paths[n].support
                ))
            targets = frozenset(s for s in chain.states if chain.outcomes[s] in fixtures.RESET)
            eventual = core.hitting_analysis(chain, targets)
            by_cause = {kind: core.hitting_analysis(chain, frozenset(
                s for s in chain.states if chain.outcomes[s] == kind
            )) for kind in (*sorted(fixtures.RESET), "dead")}
            for kind, analysis in {"reset": eventual, **by_cause}.items():
                gate(f"{prefix}.{kind}.equations", all(r == (0, 0) for r in analysis["residuals"].values()))
                gate(f"{prefix}.{kind}.probabilities", all(
                    0 <= r["probability"] <= 1 and r["weighted_time"] >= 0
                    for r in analysis["states"].values()
                ))
            gate(f"{prefix}.eventual_channels", eventual["initial"]["probability"], sum((
                by_cause[k]["initial"]["probability"] for k in fixtures.RESET
            ), F(0)))
            p = settings.epsilon / 2 if program.controller_id == "refuse" else 1 - settings.epsilon / 2
            exposure = F(0)
            for n, row in enumerate(measures):
                gate(f"{prefix}.deadline_{n}.mass", row["live"] + row["reset"] + row["dead"], F(1))
                gate(f"{prefix}.deadline_{n}.no_reset", row["no_reset"], 1 - row["reset"])
                if n:
                    exposure += measures[n - 1]["live"]
                expected_cost = (exposure, exposure * (1 - settings.death) * (1 - settings.writer) * p,
                                 exposure * (1 - settings.death) * settings.writer)
                gate(f"{prefix}.deadline_{n}.cost_coordinates", row["expected_cost"], expected_cost)
                if not settings.death and not settings.writer and settings.working:
                    gate(f"{prefix}.deadline_{n}.block_bound", row["no_reset"] <= (1 - p ** settings.m) ** (n // settings.m))
                if settings.m == 1:
                    reset_rate = (1 - settings.death) * (settings.writer + (1 - settings.writer) * p * settings.working)
                    live_rate = 1 - settings.death - reset_rate
                    gate(f"{prefix}.deadline_{n}.live_formula", row["live"], live_rate ** n)
                    died = settings.death * sum((live_rate ** k for k in range(n)), F(0))
                    gate(f"{prefix}.deadline_{n}.dead_formula", row["dead"], died)
            if not settings.death and not settings.writer:
                probability = F(int(settings.working and p > 0))
                gate(f"{prefix}.eventual_reset", eventual["initial"]["probability"], probability)
                mean = sum((p ** -j for j in range(1, settings.m + 1)), F(0)) if probability else "infinity"
                gate(f"{prefix}.mean_formula", eventual["initial"]["mean"], mean)
                channel = "noise_assisted" if program.controller_id == "refuse" else "selected"
                gate(f"{prefix}.reset_source", by_cause[channel]["initial"]["probability"], probability)
            if name == "external_writer" and program.controller_id == "refuse":
                gate(f"{prefix}.writer_probability", by_cause["external"]["initial"]["probability"], F(1))
                gate(f"{prefix}.writer_mean", eventual["initial"]["mean"], F(4))
                gate(f"{prefix}.writer_survival", [r["no_reset"] for r in measures], [F(3, 4) ** n for n in range(31)])
            if name == "competing_death" and program.controller_id == "refuse":
                gate(f"{prefix}.eventual_reset", eventual["initial"]["probability"], F(3, 23))
                gate(f"{prefix}.eventual_death", by_cause["dead"]["initial"]["probability"], F(20, 23))
                gate(f"{prefix}.unconditional_mean", eventual["initial"]["mean"], "infinity")
                gate(f"{prefix}.conditional_mean", eventual["initial"]["conditional_mean"], F(80, 23))
            programs[program.controller_id] = {"deadlines": measures, "eventual": eventual["initial"],
                "eventual_causes": {k: a["initial"] for k, a in by_cause.items()},
                "almost_sure_region": eventual["almost_sure"]}
            raw[program.controller_id] = {"chain": chain, "short_paths": paths, "marginals": propagated,
                                          "eventual": eventual, "by_cause": by_cause}
        choices = {n: {"objective_J": _maximizers({p: r["deadlines"][n]["live"] for p, r in programs.items()}),
                       "alive_without_reset": _maximizers({p: r["deadlines"][n]["live"] for p, r in programs.items()}),
                       "no_reset_including_death": _maximizers({p: r["deadlines"][n]["no_reset"] for p, r in programs.items()})}
                   for n in (6, 30)}
        cases[name] = {"settings": settings, "programs": programs, "choices": choices,
                       "possible_recovery_region": possible}
        evidence[name] = {"world": world, "programs": raw}
    for sealed, opened in (("sealed_noiseless", "open_noiseless"), ("immutable_record", "open_noiseless"),
                           ("sealed_noise", "open_noise_10_m3")):
        gate(f"{sealed}.channel_pair", cases[sealed]["programs"], cases[opened]["programs"])
    summary = {"status": "PASS" if all(g["passed"] for g in gates) else "FAIL",
               "scope": "public known-answer finite recovery controls; no empirical generalization",
               "cost_coordinates": ("ticks", "recovery_energy", "external_writes"),
               "cases": cases, "gates": gates}
    return summary, evidence


def render_report(summary):
    lines = ["# Minimal recovery dynamics panel v0", "", f"Status: {summary['status']}",
             f"Gates: {sum(g['passed'] for g in summary['gates'])}/{len(summary['gates'])}", "",
             "All 14 public worlds retain both programs. Table shows the refusal program.",
             "Mean is unconditional; infinity includes paths that never reset.", "",
             "| World | P(eventual reset) | Mean ticks to reset | P(live without reset at 30) |",
             "| --- | --- | --- | --- |"]
    for name, case in summary["cases"].items():
        result = case["programs"]["refuse"]
        # Approximate display only; all probabilities remain exact in summary.json.
        live = float(result["deadlines"][30]["live"])
        lines.append(f"| {name} | {result['eventual']['probability']} | {result['eventual']['mean']} | {live:.8g} |")
    lines += ["", "Full exact tables, vector costs, all maximizing ties, and separate reset",
              "mechanisms are in summary.json. Complete chains, short paths and rational",
              "hitting-equation certificates are in evidence.json. Source hashes are in",
              "provenance.json. Reset persistence is assumed by absorbing reset states.", "",
              "This is an instrument and analytic audit of declared mechanisms. It does",
              "not establish a generic recovery floor or real-world recovery times.", "", "## Gates", ""]
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
    out_dir = args.out_dir or ROOT / "results/local_runs/recovery_dynamics" / datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    summary = retain(out_dir)
    print(json.dumps({"status": summary["status"], "cases": len(summary["cases"]), "gates": len(summary["gates"]),
                      "output": str(out_dir)}))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
