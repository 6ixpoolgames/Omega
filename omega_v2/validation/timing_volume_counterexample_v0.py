"""Reproduce the frozen timing-volume counterexample and retain its evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from math import factorial
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import poisson

from omega_v2.experiments.timing_volume_counterexample_v0 import (
    BOUNDARIES,
    FUEL,
    HORIZONS,
    PREPARATION_BILL,
    PROTOCOL,
    PROTOCOL_SHA256,
    calibration_nets,
    preparations,
    relay_net,
)
from omega_v2.finite.timed_execution import (
    closed_region,
    condition_on,
    endpoint_from_matrix,
    endpoint_from_paths,
    enumerate_paths,
    hitting_probability,
    jump_law,
    marginal,
    path_probability,
    reachable_states,
    timing_profile,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    PROTOCOL,
    "omega_v2/finite/timed_execution.py",
    "omega_v2/experiments/timing_volume_counterexample_v0.py",
    "omega_v2/validation/timing_volume_counterexample_v0.py",
    "tests/test_timing_volume_counterexample.py",
)
DEFAULT_OUTPUT = "docs/research_notes/validation_results/timing_volume_counterexample_v0/20261001"
REPORT = "docs/research_notes/omega_v2/timing_volume_counterexample_report_v0.md"
TOLERANCE = 2e-11


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol_digest(path):
    """A checkout's LF/CRLF conversion is not a revision of the contract."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def fraction(p):
    return [p.numerator, p.denominator]


def marginal_rows(law, registers):
    return [{"values": key, "mass": fraction(p)} for key, p in sorted(marginal(law, registers).items())]


def git(*args):
    result = subprocess.run(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *args], cwd=ROOT,
        text=True, capture_output=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def run():
    observed_hash = protocol_digest(ROOT / PROTOCOL)
    if observed_hash != PROTOCOL_SHA256:
        raise RuntimeError("frozen protocol hash changed; make a new version instead")
    net, initial = relay_net(), preparations()
    evidence, maximum = {}, {"mass": 0.0, "matrix_agreement": 0.0,
                             "cut_composition": 0.0, "poisson_profile": 0.0}
    representation_gates = []

    for name, law in initial.items():
        paths = enumerate_paths(net, law, FUEL)
        states = reachable_states(net, law)
        ids = {s: i for i, s in enumerate(states)}
        unit_exit = all(net.exit_rate(s) == (1 if dict(s)["fuel"] else 0) for s in states)
        wire_closed = closed_region(net, states, lambda s: dict(s)["wire"] == 1)
        representation_gates.extend([
            {"name": f"{name}.unit_exit_until_fuel_exhaustion", "passed": unit_exit},
            {"name": f"{name}.wire_correction_is_permanent", "passed": wire_closed},
            {"name": f"{name}.fuel_and_cost_conservation", "passed": all(
                dict(p.states[-1])["fuel"] + dict(p.states[-1])["spent"] == FUEL
                and p.cost == (len(p.events), len(p.events)) for p in paths)},
        ])
        horizons, boundaries, frames = [], [], []
        for horizon in HORIZONS:
            profile = timing_profile(net, paths, horizon)
            endpoint = endpoint_from_paths(net, paths, horizon)
            matrix = endpoint_from_matrix(net, law, horizon)
            cut = endpoint_from_matrix(net, law, horizon, cut=horizon/3)
            expected_count = list(poisson.pmf(np.arange(FUEL), horizon)) + [poisson.sf(FUEL-1, horizon)]
            expected_L = [p*horizon**n/factorial(n) for n, p in enumerate(expected_count)]
            maximum["mass"] = max(maximum["mass"], abs(profile["mass"]-1))
            maximum["matrix_agreement"] = max(maximum["matrix_agreement"],
                                               max(abs(endpoint.get(s, 0)-p) for s, p in matrix.items()))
            maximum["cut_composition"] = max(maximum["cut_composition"],
                                              max(abs(cut[s]-p) for s, p in matrix.items()))
            maximum["poisson_profile"] = max(maximum["poisson_profile"],
                                              max(abs(a-b) for a, b in zip(profile["L"], expected_L)))
            expected_cost = sum(n*p for n, p in enumerate(profile["count_law"]))
            horizons.append({
                **{k: profile[k] for k in ("H", "V", "L", "count_law", "mass")},
                "endpoint_law": [{"state": ids[s], "mass": p} for s, p in sorted(endpoint.items())],
                "expected_cost": [expected_cost, expected_cost],
                "first_nonblank_downstream_probability": hitting_probability(
                    net, paths, horizon, lambda s: dict(s)["downstream"] != -1),
                "corrected_by_deadline_probability": hitting_probability(
                    net, paths, horizon, lambda s: dict(s)["wire"] == 1),
            })
        for n in BOUNDARIES:
            at_cut = jump_law(net, law, n)
            boundaries.append({
                "event_boundary": n,
                "law": [{"state": ids[s], "mass": fraction(p)} for s, p in sorted(at_cut.items())],
                "source_record": marginal_rows(at_cut, ("source", "record")),
                "source_relay": marginal_rows(at_cut, ("source", "relay")),
                "source_downstream": marginal_rows(at_cut, ("source", "downstream")),
                "link": marginal_rows(at_cut, ("link",)),
                "wire": marginal_rows(at_cut, ("wire",)),
            })
        for record, (mass, conditioned) in condition_on(jump_law(net, law, 2), ("record",)).items():
            frames.append({"record": record, "mass": fraction(mass),
                           "source_posterior": marginal_rows(conditioned, ("source",))})
        evidence[name] = {
            "states": [dict(s) for s in states],
            "initial_law": [{"state": ids[s], "mass": fraction(p)} for s, p in sorted(law.items())],
            "paths": [{"states": [ids[s] for s in p.states],
                       "events": [t.name for t in p.events], "cost": p.cost,
                       "masses_by_horizon": [path_probability(net, p, h) for h in HORIZONS]}
                      for p in paths],
            "horizons": horizons, "boundaries": boundaries, "current_record_frames_after_2": frames,
        }

    calibrations = {}
    for name, (control_net, law, bound) in calibration_nets().items():
        calibrations[name] = timing_profile(control_net, enumerate_paths(control_net, law, bound), 1)
    profile_disagreement = max(
        abs(a-b)
        for candidate in evidence.values()
        for base, other in zip(evidence["intact"]["horizons"], candidate["horizons"])
        for a, b in zip(base["L"], other["L"])
    )
    source_relation = {(0, 0): Fraction(1, 2), (1, 1): Fraction(1, 2)}
    blank_relation = {(0, -1): Fraction(1, 2), (1, -1): Fraction(1, 2)}
    for name in ("damaged", "erased", "cycling"):
        witness = marginal(jump_law(net, initial[name], 5), ("source", "downstream"))
        representation_gates.append({"name": f"{name}.downstream_obstruction_at_5", "passed": witness == blank_relation})
    representation_gates.extend([
        {"name": "intact.downstream_channel_at_5", "passed": marginal(
            jump_law(net, initial["intact"], 5), ("source", "downstream")) == source_relation},
        {"name": "damaged.downstream_recovery_at_10", "passed": marginal(
            jump_law(net, initial["damaged"], 10), ("source", "downstream")) == source_relation},
    ])
    maximum = {key: float(value) for key, value in maximum.items()}
    machinery_passes = bool(all(row["passed"] for row in representation_gates)
                            and max(maximum.values()) < TOLERANCE)
    collision = bool(profile_disagreement < TOLERANCE)
    return {
        "metadata": {
            "utc": datetime.now(UTC).isoformat(), "python": platform.python_version(),
            "numpy": np.__version__, "scipy": scipy.__version__,
            "git_head": git("rev-parse", "HEAD"), "git_branch": git("branch", "--show-current"),
            "git_status": git("status", "--short"),
            "protocol_sha256_before_implementation": PROTOCOL_SHA256,
            "protocol_hash_encoding": "UTF-8 with LF newlines; matches original frozen bytes",
            "source_sha256": {path: sha256(ROOT/path) for path in SOURCES},
            "tolerance": TOLERANCE,
            "scope": "analytic finite-model counterexample; no Monte Carlo or independent empirical claim",
        },
        "candidate_status": "rejected_as_complete_comparison" if machinery_passes and collision else "investigate",
        "machinery_passes": machinery_passes,
        "maximum_numerical_residuals": maximum,
        "maximum_pairwise_L_difference": profile_disagreement,
        "representation_gates": representation_gates,
        "preparation_bill": PREPARATION_BILL,
        "rule_table": [{"name": t.name, "guard": dict(t.guard), "writes": dict(t.writes),
                        "rate": fraction(t.rate), "cost": t.cost} for t in net.transitions],
        "calibrations_at_H1": calibrations,
        "arrangements": evidence,
    }


def report_text(result, output_dir):
    paths = result["arrangements"]
    comparison_rows = []
    for index, horizon in enumerate(HORIZONS):
        probabilities = [paths[name]["horizons"][index]["first_nonblank_downstream_probability"]
                         for name in ("intact", "damaged", "erased", "cycling")]
        comparison_rows.append(f"| {horizon:g} | " + " | ".join(f"{p:.9g}" for p in probabilities) + " |")
    profile_rows = []
    for n, p in enumerate(paths["intact"]["horizons"][3]["L"]):
        profile_rows.append(f"| {n} | {p:.12g} |")
    residuals = result["maximum_numerical_residuals"]
    return f"""# Weighted timing-volume counterexample report v0

Date: 2026-10-01. Status: **candidate rejected as a complete lushness comparison**.
This is a reproducible mathematical counterexample in a declared finite model,
not an independent empirical finding or a cosmology result.

## Result

The frozen probability-weighted timing-volume profile ties four arrangements
at every horizon, although their records, downstream access, and recovery
trajectories differ. The full process represents the differences. Its summary
loses them. No coefficient, event exclusion, alternative partition, or added
coordinate was fitted after observing this result.

The [contract](timing_volume_counterexample_protocol_v0.md) was written before
the implementation and numerical run. Its SHA-256 (UTF-8, LF newlines) is
`{PROTOCOL_SHA256}`. The all-horizon collision was an explicit analytic
prediction in that contract. Checking it is not independent discovery.

## Frozen comparison

An exact-n-event trace class c has timing volume v_c(H)=m_c H^n/n!, where m_c
counts its disjoint chronological domains after independent presentations are
grouped. The candidate is L_n=sum_c p_Phi(c;H) v_c(H), with ordinary physical
conditional probabilities, including no-event and unfinished histories.
Coordinates retain their time^n units; neither dimensions nor horizons are
summed. This report rejects this particular functional, not all possible
probability-weighted volumes.

The reference is one common guarded physical update table: record acquisition,
retention/erasure, relay, record-keyed assembly/repair, then downstream forwarding.
One shared actuator serializes updates. Each uses one unit of a ten-unit fuel
stock and incurs one actuator operation. The packet registers replenish in
the second cycle; this is not the earlier private-fuel once-only class.
Only initial wire/switch/socket orientations differ. The preparation bill is
declared and equal; no realistic thermodynamic equivalence is asserted.

## Why the tie holds for every horizon

All reachable nonabsorbed states have total firing rate 1. Ten firings exhaust
the physical stock. Consequently N_H=min(Poisson(H),10), in every arrangement.
All updates share the actuator and fuel, so every trace class here is one
serial word with timing volume H^n/n!. Therefore

    L_n(H) = P(N_H=n) H^n/n!,  n=0,...,10.

Only the number of firings survives this aggregation. Their physical effects,
the location of accessible records, and the future couplings they establish
do not. This is a class-wide identity for serial constant-total-rate models
with this stopping stock, not an inference from five sampled deadlines.

For n<10 the count probability is exp(-H) H^n/n!; n=10 retains the entire
Poisson upper tail. It is not dropped or renormalized. At H=0 the known empty
history is the sole positive-probability event-count sector.

All four profiles at H=4 (separate units time^n):

| n | L_n, each arrangement |
|---:|---:|
{chr(10).join(profile_rows)}

## Structural differences retained by the process

The source is a fair physical bit. The reference records joint laws, not a
selected utility or an optimized achievement target.

| Arrangement | After event 3 | After event 4 | After event 5 | After event 10 |
|---|---|---|---|---|
| Intact | Relay carries source bit | Link installed | Downstream carries source bit | Downstream carries source bit |
| Damaged coupling | Relay is blank | Wire repaired and link installed | Earlier obstruction still leaves downstream blank | Next cycle transmits source bit |
| Erased record | Relay is an independent fair bit | No record key; link absent | Downstream blank | Downstream blank |
| Cycling apparatus | Relay carries source bit | Rotor turns; link absent | Downstream blank | Downstream blank |

At the first boundary, all preparations physically record the source. At the
second, the erased preparation has r=blank and source posterior (1/2,1/2) from
that accessible register. The other preparations retain the bit. The analyst's
full histories still include the old record; the physical reader never sees
those histories. Every blank-reader outcome remains in the law and volume.

Wire repair occurs at the fourth firing in the damaged preparation and is
permanent under these rules: the corrected region w=1 is closed. This does not
restore the already missed first-cycle transmission. The first nonblank
downstream output occurs at event 5 for intact and event 10 for damaged; it
never occurs for erased or cycling. Thus their deadline probabilities are
P(Poisson(H)>=5), P(Poisson(H)>=10), 0, and 0 respectively:

| H | Intact | Damaged | Erased | Cycling |
|---:|---:|---:|---:|---:|
{chr(10).join(comparison_rows)}

These are witnesses of propagating obstruction and generated access within
the full process. They do not define lushness by a favored task. Construction
is an explicit new coupling under fixed rules; nothing requires a new law or
an outcome unpredictable from the complete initial dynamics.

## Verification and reproducibility

The engine enumerates every physically possible finite history. Jump-boundary
probabilities use exact rational arithmetic. Timed probabilities use numerical
matrix exponentials and are checked against a separate state-space CTMC
calculation and the analytic count law. No trajectories are sampled.

Maximum numerical residuals in this run:

- Total probability: {residuals['mass']:.3g}.
- Path enumeration versus state-space CTMC: {residuals['matrix_agreement']:.3g}.
- Intermediate-cut composition: {residuals['cut_composition']:.3g}.
- Profile versus analytic Poisson certificate: {residuals['poisson_profile']:.3g}.
- Difference between paired profiles: {result['maximum_pairwise_L_difference']:.3g}.

Tolerance: {TOLERANCE:g}. Machinery gates passed: {result['machinery_passes']}.
The companion tests separately check independent/exclusive/enabling race laws,
three-way diamond grouping, relabeling, subdivision as integration, positive
duration, physical fuel/cost accounting, record erasure, conditioning, repair
persistence and composition-generated access. Passing these verifies the
implementation; the candidate's substantive result is failure.

Run from the repository root:

```text
python -m pytest tests/test_timing_volume_counterexample.py -q
python -m omega_v2.validation.timing_volume_counterexample_v0
```

[Machine-readable evidence](../validation_results/timing_volume_counterexample_v0/20261001/evidence.json)
contains the common rule table, full paths, endpoint laws, record-conditioned
frames, costs, calibrations, versions, source hashes and repository state.
The output directory for this run is `{output_dir.as_posix()}`.

## Consequence and limits

Keep the complete weighted continuation process and these counterexamples.
Retire L_n as the proposed complete comparison. Do not proceed to the large
lattice sweep with this volume, or append a bonus to rescue its rankings.
Any successor must explain how it uses causal incidence and residual coupling
that the present functional discards. That is a new mathematical obligation,
not a completed replacement measure.

The model's physical mechanisms are stipulated. The collision refutes a
completeness claim for this summary; it does not prove a universal moral order,
establish a noise filter, reject the substrate motivation, or establish the
adequacy of the quantum object. No quantum-volume extension, Planck cutoff,
cosmology release, unseen-world evaluation, or push accompanies this report.
The collision concerns L_n at the stated comparison frame. It does not show
that an atlas retaining the occurrence, weights and relationships of all frames
is identical between arrangements. Those relationships remain in the process;
no complete volume functional on that richer atlas has been supplied here.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(DEFAULT_OUTPUT))
    parser.add_argument("--report", type=Path, default=Path(REPORT))
    args = parser.parse_args(argv)
    result = run()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    report = args.report if args.report.is_absolute() else ROOT / args.report
    output.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    (output / "evidence.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
    report.write_text(report_text(result, args.output), encoding="utf-8")
    print(json.dumps({"candidate_status": result["candidate_status"],
                      "machinery_passes": result["machinery_passes"],
                      "maximum_numerical_residuals": result["maximum_numerical_residuals"],
                      "report": str(report), "evidence": str(output / "evidence.json")}, indent=2))
    return 0 if result["machinery_passes"] and result["candidate_status"] == "rejected_as_complete_comparison" else 1


if __name__ == "__main__":
    raise SystemExit(main())
