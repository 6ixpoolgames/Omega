"""Retain paid-suppression and nonabsorbing-correction audits."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

from omega_v2.experiments import recovery_suppression_v0 as fixtures
from omega_v2.finite import recovery_dynamics as core
from omega_v2.finite.recovery_persistence import permanent_membership
from omega_v2.validation.continuation_equivalence_audit_v0 import encode
from omega_v2.validation.operational_continuation_comparison_v0 import ROOT, _git

F = Fraction
CATEGORIES = ("never_reset", "corrected", "proxy_after", "dead_before", "dead_after")
SOURCES = (
    fixtures.PROTOCOL, "omega_v2/finite/model.py", "omega_v2/finite/controllers.py",
    "omega_v2/finite/recovery_dynamics.py", "omega_v2/finite/recovery_persistence.py",
    "omega_v2/experiments/recovery_suppression_v0.py", "omega_v2/validation/recovery_suppression_v0.py",
    "omega_v2/validation/continuation_equivalence_audit_v0.py",
    "omega_v2/validation/operational_continuation_comparison_v0.py",
    "tests/test_recovery_suppression.py",
)


def readouts(chain, rows):
    output, cumulative = [], F(0)
    for n, row in enumerate(rows):
        categories = dict.fromkeys(CATEGORIES, F(0))
        sources = dict.fromkeys(("selected", "noise_assisted", "external"), F(0))
        stock, sealed, relapsed = {}, F(0), F(0)
        for (state, memory), p in row["law"].rows:
            categories[chain.outcomes[state, memory]] += p
            if state.first != "none":
                sources[state.first] += p
            stock[state.stock] = stock.get(state.stock, F(0)) + p
            sealed += p * state.sealed
            relapsed += p * state.relapsed
        first = sum(sources.values(), F(0))
        risk = output[-1]["never_reset"] if n else None
        hazard = (first - output[-1]["ever_reset"]) / risk if risk else None
        if hazard is not None:
            cumulative += hazard
        output.append({"deadline": n, **categories, "ever_reset": first, "first_sources": sources,
                       "ever_relapsed": relapsed, "stock_law": stock, "sealed_mass": sealed,
                       "expected_cost": row["expected_cost"], "first_reset_risk_set": risk,
                       "first_reset_hazard": hazard, "cumulative_hazard": cumulative,
                       "risk_set_exhausted": n > 0 and risk == 0})
    return output


def _maximizers(scores):
    value = max(scores.values())
    return {"value": value, "programs": tuple(p for p, score in scores.items() if score == value)}


def run_audit():
    gates, cases, evidence = [], {}, {}

    def gate(name, observed, expected=True):
        gates.append({"name": name, "observed": observed, "expected": expected, "passed": observed == expected})

    for name, world in fixtures.control_panel().items():
        cfg = world.settings
        edges = [(s, t, cost) for (s, _a), law in world.kernels.items() for (t, cost), _p in law.rows]
        gate(f"{name}.stock_bounds", all(0 <= s.stock <= cfg.capacity for s in world.states))
        gate(f"{name}.stock_balance", all(
            t.stock == (s.stock if t.dead else min(cfg.capacity, s.stock - cost[1] + cfg.replenish))
            for s, t, cost in edges
        ))
        gate(f"{name}.affordable_spending", all(cost[1] in (0, cfg.price) and cost[1] <= s.stock for s, _t, cost in edges))
        gate(f"{name}.history_preserved", all(s.first == "none" or s.first == t.first for s, t, _c in edges))
        gate(f"{name}.relapse_history", all(not s.relapsed or t.relapsed for s, t, _c in edges))
        programs, raw = {}, {}
        for program in world.programs:
            prefix = f"{name}.{program.controller_id}"
            chain = fixtures.product_chain(world, program)
            propagated = core.propagate(chain, 30)
            rows = readouts(chain, propagated)
            paths = {}
            for n in range(4):
                paths[n] = core.full_paths(chain, n)
                law = paths[n]
                gate(f"{prefix}.paths_{n}.marginal", law.pushforward(lambda p: p.states[-1]).mass_map == propagated[n]["law"].mass_map)
                vector = tuple(sum((p * path.cost[i] for path, p in law.rows), F(0)) for i in range(3))
                gate(f"{prefix}.paths_{n}.cost", vector, propagated[n]["expected_cost"])
                gate(f"{prefix}.paths_{n}.joint", law.pushforward(lambda p: (p.states[-1], p.cost)).mass_map
                     == core.joint_cost_law(chain, n).mass_map)
                gate(f"{prefix}.paths_{n}.stopping", all(
                    all(s not in chain.terminals for s in p.states[:-1]) for p in law.support
                ))
            first = core.hitting_analysis(chain, frozenset(s for s in chain.states if s[0].first != "none"))
            death = core.hitting_analysis(chain, chain.terminals)
            safe = frozenset(s for s in chain.states if s[0].reference and not s[0].dead)
            permanent = permanent_membership(chain, safe)
            spell_exit = core.hitting_analysis(chain, frozenset(set(chain.states) - safe))
            proxy, reference = program.controller_id.split("/")
            stay = (1 - cfg.death) * (1 - cfg.relapse) * (1 - cfg.epsilon / 2 if reference == "idle" else cfg.epsilon / 2)
            spell_mean = 1 / (1 - stay) if stay < 1 else "infinity"
            gate(f"{prefix}.spell_means", all(spell_exit["states"][s]["mean"] == spell_mean for s in safe))
            gate(f"{prefix}.spell_step_survival", all(
                sum((p for (t, _c), p in chain.rows[s].rows if t in safe), F(0)) == stay for s in safe
            ))
            gate(f"{prefix}.permanence_formula", permanent["hitting"]["initial"]["probability"],
                 first["initial"]["probability"] if stay == 1 else F(0))
            gate(f"{prefix}.closed_safe", all(set(chain.transition(s).support) <= permanent["closed_safe"]
                 for s in permanent["closed_safe"]))
            for kind, result in (("first", first), ("death", death), ("permanent", permanent["hitting"]), ("spell", spell_exit)):
                gate(f"{prefix}.{kind}.residuals", all(r == (0, 0) for r in result["residuals"].values()))
                gate(f"{prefix}.{kind}.probabilities", all(0 <= r["probability"] <= 1 for r in result["states"].values()))
            gate(f"{prefix}.partition_mass", all(sum((r[k] for k in CATEGORIES), F(0)) == 1 for r in rows))
            gate(f"{prefix}.first_mass", all(r["ever_reset"] == r["corrected"] + r["proxy_after"] + r["dead_after"] for r in rows))
            gate(f"{prefix}.history_monotonic", all(a["ever_reset"] <= b["ever_reset"] for a, b in pairwise(rows)))
            gate(f"{prefix}.hazard_bounds", all(r["first_reset_hazard"] is None or 0 <= r["first_reset_hazard"] <= 1 for r in rows))
            gate(f"{prefix}.live_time_cost", all(r["expected_cost"][0] == sum(((1 - cfg.death) ** k for k in range(n)), F(0))
                 for n, r in enumerate(rows)))
            gate(f"{prefix}.finite_first_bounded_by_eventual", all(r["ever_reset"] <= first["initial"]["probability"] for r in rows))
            if cfg.epsilon and not cfg.death:
                gate(f"{prefix}.noise_eventual", first["initial"]["probability"], F(1))
                gate(f"{prefix}.noise_mean_bound", first["initial"]["mean"] <= 3 / cfg.epsilon)
                gate(f"{prefix}.noise_deadline_bound", all(1 - r["ever_reset"] <= (1 - cfg.epsilon / 3) ** n for n, r in enumerate(rows)))
            if cfg.death:
                gate(f"{prefix}.eventual_death", death["initial"]["probability"], F(1))
                gate(f"{prefix}.death_deadlines", all(r["dead_before"] + r["dead_after"] == 1 - (1 - cfg.death) ** n for n, r in enumerate(rows)))
            if not cfg.epsilon and not cfg.death and proxy == "recover":
                gate(f"{prefix}.immediate_reset", first["initial"]["mean"], F(1))
                if reference == "revert":
                    gate(f"{prefix}.alternating_reference", [r["corrected"] for r in rows], [F(n % 2) for n in range(31)])
            if name == "spontaneous_relapse" and program.controller_id == "idle/idle":
                gate(f"{prefix}.occupancy_formula", [r["corrected"] for r in rows], [F(1, 2) * (1 - F(1, 2) ** n) for n in range(31)])
                gate(f"{prefix}.first_mean", first["initial"]["mean"], F(4))
            if name == "competing_death" and program.controller_id == "idle/idle":
                gate(f"{prefix}.first_probability", first["initial"]["probability"], F(3, 7))
                gate(f"{prefix}.death_after_recorded", rows[30]["dead_after"] > 0)
            programs[program.controller_id] = {"deadlines": rows, "first": first["initial"],
                "death": death["initial"], "permanent_probability": permanent["hitting"]["initial"]["probability"],
                "closed_safe_size": len(permanent["closed_safe"]), "corrected_states_checked": len(safe),
                "corrected_step_survival": stay, "corrected_spell_mean": spell_mean}
            raw[program.controller_id] = {"chain": chain, "paths": paths, "propagated": propagated,
                "first": first, "death": death, "permanent": permanent, "spell_exit": spell_exit}
        suppress = programs["suppress/idle"]
        expected_means = {"no_stock": 4, "recurring_s1": 5, "recurring_s3": 7, "recurring_cost2": 5,
            "recurring_underfunded": 9, "seal_failure_s1": 6, "seal_failure_s3": 10,
            "seal_failure_certain": 7, "hide_only": 4, "recurring_noise": 24,
            "spontaneous_relapse": 4, "finite_stock_relapse": 7}
        if name in expected_means:
            gate(f"{name}.suppress.first_mean", suppress["first"]["mean"], F(expected_means[name]))
        for key in ("recurring_replenished", "one_shot_s1", "one_shot_s3", "seal_replenished", "replenished_death"):
            if name == key:
                gate(f"{name}.suppress.never_reset", suppress["first"]["probability"], F(0))
        if name in ("no_stock", "recurring_s1", "recurring_s3", "recurring_cost2", "finite_stock_relapse"):
            delay = cfg.capacity // cfg.price
            gate(f"{name}.suppress.stock_delay", [1 - r["ever_reset"] for r in suppress["deadlines"]],
                 [(1 - cfg.writer) ** max(n - delay, 0) for n in range(31)])
        if name == "recurring_underfunded":
            gate(f"{name}.suppress.exposed_ticks", [1 - r["ever_reset"] for r in suppress["deadlines"]],
                 [(1 - cfg.writer) ** max(0, (n - 1) // 2) for n in range(31)])
        if name == "recurring_noise":
            gate(f"{name}.suppress.noise_hazard", [1 - r["ever_reset"] for r in suppress["deadlines"]],
                 [F(23, 24) ** n for n in range(31)])
        choices = {n: {criterion: _maximizers({p: score(r["deadlines"][n]) for p, r in programs.items()})
                       for criterion, score in {
                           "objective_J": lambda r: r["never_reset"] + r["proxy_after"],
                           "alive_never_reset": lambda r: r["never_reset"],
                           "current_correction": lambda r: r["corrected"],
                           "ever_reset": lambda r: r["ever_reset"],
                       }.items()} for n in (6, 12, 30)}
        cases[name] = {"settings": cfg, "programs": programs, "choices": choices}
        evidence[name] = {"world": world, "programs": raw}
    gate("maintenance_one.matches_recurring", cases["seal_failure_certain"]["programs"]["suppress/idle"]["deadlines"],
         cases["recurring_s3"]["programs"]["suppress/idle"]["deadlines"])
    return {"status": "PASS" if all(g["passed"] for g in gates) else "FAIL",
            "scope": "registered finite mechanisms; same-workflow known-answer audit",
            "cost_coordinates": ("ticks", "suppression_tokens", "recovery_energy"),
            "cases": cases, "gates": gates}, evidence


def render_report(summary):
    lines = ["# Suppression and correction persistence v0", "", f"Status: {summary['status']}",
             f"Gates: {sum(g['passed'] for g in summary['gates'])}/{len(summary['gates'])}", "",
             "Exact results for suppress/idle. All six programs per world are retained.", "",
             "| World | Eventual first reset | Mean first-reset ticks | Permanent correction |",
             "| --- | --- | --- | --- |"]
    for name, case in summary["cases"].items():
        p = case["programs"]["suppress/idle"]
        lines.append(f"| {name} | {p['first']['probability']} | {p['first']['mean']} | {p['permanent_probability']} |")
    lines += ["", "Permanence means eventual residence forever in live corrected states of the",
              "fixed-program finite chain. Mean first-reset time is unconditional, hence",
              "infinite whenever reset has positive probability of never occurring.", "",
              "The source contract fixes costs, event ordering, controls and known answers.",
              "No empirical generalization, generic recovery floor or real-time calibration.", "", "## Gates", ""]
    lines.extend(f"- {'PASS' if g['passed'] else 'FAIL'} {g['name']}" for g in summary["gates"])
    return "\n".join(lines) + "\n"


def _compact_mapping(path, mapping):
    path.write_text("{\n" + ",\n".join(
        "  " + json.dumps(k) + ": " + json.dumps(encode(v), sort_keys=True, separators=(",", ":"))
        for k, v in mapping.items()
    ) + "\n}\n", encoding="utf-8")


def retain(out_dir):
    out_dir.mkdir(parents=True, exist_ok=False)
    summary, evidence = run_audit()
    # Compact exact JSON avoids repeating huge pretty-printed state/cost maps.
    _compact_mapping(out_dir / "summary.json", summary)
    _compact_mapping(out_dir / "evidence.json", evidence)
    _compact_mapping(out_dir / "provenance.json", {
        "revision": _git("rev-parse", "HEAD"), "python": sys.version,
        "source_git_status": _git("status", "--porcelain", "--", *SOURCES),
        "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES},
    })
    (out_dir / "report.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    output = args.out_dir or ROOT / "results/local_runs/recovery_suppression" / datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    summary = retain(output)
    print(json.dumps({"status": summary["status"], "worlds": len(summary["cases"]),
                      "gates": len(summary["gates"]), "output": str(output)}))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
