"""Reproduce the finite comparison audit and retain complete rational evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from omega_v2.experiments.operational_continuation_comparison_v0 import (
    PROTOCOL,
    TERMINATION_PROTOCOL,
    run_experiment,
)
from omega_v2.finite.model import fraction_text
from omega_v2.finite.operational_continuation import team_id
from omega_v2.validation.artifacts import write_json

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    PROTOCOL,
    TERMINATION_PROTOCOL,
    "omega_v2/finite/model.py",
    "omega_v2/finite/controllers.py",
    "omega_v2/finite/operational_continuation.py",
    "omega_v2/experiments/operational_continuation_comparison_v0.py",
    "omega_v2/validation/operational_continuation_comparison_v0.py",
    "tests/test_operational_continuation_comparison.py",
)


def _git(*args):
    result = subprocess.run(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *args],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def provenance():
    return {
        "revision": _git("rev-parse", "HEAD"),
        "python": sys.version,
        "source_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES
        },
    }


def _evidence(evaluated):
    e = evaluated.experiment
    return {
        "name": e.name, "horizon": e.horizon, "budget": e.budget,
        "system_id": e.system.system_id,
        "states": [repr(s) for s in e.system.states],
        "terminals": sorted(repr(s) for s in e.terminals),
        "transitions": [
            {"source": repr(s), "action": repr(a), "target": repr(t),
             "probability": fraction_text(p), "cost": e.costs[s, a, t]}
            for s, a, t, p in e.system.transitions
        ],
        "preparations": {
            q: [{"state": repr(s), "probability": fraction_text(p)} for s, p in law.rows]
            for q, law in e.preparations.items()
        },
        "programs": {
            team_id(team): [
                {"controller_id": c.controller_id, "initial_memory": repr(c.initial_memory),
                 "observations": [[repr(s), repr(o)] for s, o in c.observation_rows],
                 "updates": [[repr(m), repr(o), repr(n)] for m, o, n in c.update_rows],
                 "actions": [[repr(m), repr(o), repr(a)] for m, o, a in c.policy_rows]}
                for c in team
            ] for team in e.teams
        },
        "over_budget": dict(evaluated.rejected),
        "laws": {
            policy: {
                q: [
                    {"probability": fraction_text(p),
                     "states": [repr(s) for s in run.path.states],
                     "actions": [repr(a) for a in run.path.actions],
                     "observations": [[repr(o) for o in h] for h in run.observations],
                     "memories": [[repr(m) for m in h] for h in run.memories],
                     "cost": run.cost, "elapsed": run.elapsed, "censored": run.censored}
                    for run, p in law.rows
                ] for q, law in responses.items()
            } for policy, responses in evaluated.laws.items()
        },
    }


def render_report(summary):
    lines = [
        "# Operational continuation comparison v0",
        "",
        f"Status: {summary['status']}",
        (f"Passing acceptance gates: {sum(g['passed'] for g in summary['gates'])}"
         f"/{len(summary['gates'])}"),
        "",
        "Exact finite acceptance cases, not empirical validation of lushness or value.",
        "Source hashes and revision are in provenance.json; complete paths, local",
        "controller tables, costs and transition laws are in evidence.json.",
        "Emulation witnesses and first differing inputs are in summary.json.",
        "",
        "| Case / response frame | Achievement | Left emulates right | Right emulates left |",
        "| --- | --- | --- | --- |",
    ]
    for name, case in summary["cases"].items():
        lines.append(
            f"| {name} | {case['achievement_order']} | "
            f"{case['left_emulates_right']['status']} | "
            f"{case['right_emulates_left']['status']} |"
        )
    lines += [
        "",
        "## Interpretive limits",
        "",
        "All controller programmes are installed catalogue entries. Costs cover",
        "declared operations, not apparatus manufacture. Output projections are",
        "explicit; output emulation does not imply preservation of omitted costs",
        "or history. No free policy randomization or hidden-input selector exists.",
        "The comparison is finite response emulation, not a general online adapter",
        "or a compositional resource-conversion theorem.",
        "",
        "## Gates",
        "",
    ]
    lines.extend(
        f"- {'PASS' if g['passed'] else 'FAIL'} {g['name']}: "
        f"observed {g['observed']!r}; expected {g['expected']!r}"
        for g in summary["gates"]
    )
    return "\n".join(lines) + "\n"


def retain(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=False)
    complete = run_experiment()
    evidence = {}
    for name, case in complete["cases"].items():
        left, right = case.pop("_evidence")
        evidence[name] = {"left": _evidence(left), "right": _evidence(right)}
    evidence["controls"] = {
        name: _evidence(evaluated)
        for name, evaluated in complete.pop("_control_evidence").items()
    }
    complete["status"] = "PASS" if all(g["passed"] for g in complete["gates"]) else "FAIL"
    write_json(out_dir / "summary.json", complete)
    write_json(out_dir / "evidence.json", evidence)
    write_json(out_dir / "provenance.json", provenance())
    (out_dir / "report.md").write_text(render_report(complete), encoding="utf-8")
    return complete


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    out = args.out_dir or (
        ROOT / "results/local_runs/operational_comparison"
        / datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    )
    result = retain(out)
    print(json.dumps({"status": result["status"], "gates": len(result["gates"]),
                      "output": str(out)}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
