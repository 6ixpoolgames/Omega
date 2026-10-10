# Operational Continuation Comparison Report v0

Status: retained exact finite comparison instrument.

Date: 2026-09-28.

Follow-up: the [termination-control audit](operational_continuation_termination_report_v0.md)
adds mixed-cutoff and costly-terminal fixtures plus targeted mutation checks.
The extended run passes 40 gates and the full suite passes 642 tests. The
original 34-gate results below remain the record of the initial implementation.

Proposed next experiment: [continuation prediction pilot](continuation_prediction_pilot_protocol_v0.md).
This is a draft contract for a candidate, matched baselines, and an independently
evaluated workload; it records no new experimental result.

The first implementation step is now recorded separately in the
[C1 equivalence and control-panel audit](continuation_equivalence_audit_report_v0.md).
The draft pilot remains a proposal for a later independently frozen workload.

- [Definitions and claim boundary](operational_continuation_comparison_v0.md)
- [Acceptance protocol](operational_continuation_comparison_protocol_v0.md),
  committed before implementation at `354be7e`
- Base checkpoint: `506ef363a3f27ec4713617089f4f7f3caf8a7d9c`
- Implementation checkpoint: `0b4d6487a9946cb01b199f8a190be51ed9f89f52`
- [Retained run](../validation_results/operational_continuation_comparison_v0/20260928/)

## Result

All **34 acceptance gates** passed across five finite cases and their controls.
The implementation enforces local observation and memory, a common cost/time
origin, whole-policy budget feasibility, and one source witness across all
hidden inputs. It preserves failure mass and distinguishes an unavailable
catalogue from zero achievement.

The concrete separation is that separately optimized task scores need not
identify the attainable response laws. A deterministic selector achieves
either desired output perfectly, while a fair coin reaches each with probability
1/2. The selector still cannot reproduce the random law unless the declared
apparatus supplies randomness. This is an instrument check under explicit
assumptions, not an empirical discovery about physical lushness.

Each row compares the left context to the right context:

| Contexts and selected targets | Left profile | Right profile | Achievement comparison | Response emulation |
| --- | --- | --- | --- | --- |
| Revealed / hidden bit: correct guess | (1) | (1/2) | Left strictly dominates | Left emulates right only |
| Selector with coin / fixed coin: zero, one | (1,1) | (1/2,1/2) | Left strictly dominates | Left emulates right only |
| Selector without coin / fixed coin: zero, one | (1,1) | (1/2,1/2) | Left strictly dominates | Neither emulates the other |
| Two / one repair tokens: first, second | (1,1) | (1,1) | Equivalent on these tasks | Left emulates right only |
| Two / one repair tokens: first, second, both | (1,1,1) | (1,1,0) | Left strictly dominates | Left emulates right only |
| Build / wait: service | (1) | (0) | Left strictly dominates | Left emulates right only |
| Build / wait: service, zero expenditure | (1,0) | (0,1) | Incomparable | Neither emulates the other |
| Alarm / clear: terminal completion | (1) | (1) | Equivalent on this task | Both emulate endpoint/time/cost |
| Alarm / clear: alarm occurred, clear occurred | (1,0) | (0,1) | Incomparable | Neither emulates full signal history |

The repair response frame always includes the pair of outcomes; this is why
its emulation result detects the joint difference even in the marginal-task
row. The build savings frame includes expenditure. The service-only frame
omits it. Those choices are part of the comparison, not neutral defaults.

## Controls

- Giving the hidden-bit optimizer a separate policy per hidden input produces
  the unsound score 1 instead of the legal 1/2. Actual controller execution does
  not receive that extra information.
- A received bit cannot affect the receiver before transmission arrives.
- Simultaneous repairs with one token retain the collision failure and token
  consumption rather than borrowing the token twice.
- Build at horizon 1 has no completed service. At horizon 2, budget 1 permits
  preparation but no successful use; budget 2 permits service. Budget 0 yields
  an unavailable build-prefix catalogue.
- Half-successful setup retains service probability 1/2. The tests separately
  reject a whole policy whose costly failure exceeds its worst-case budget,
  even though its expected cost fits.
- Complement-complete event comparison of 21 passive binary laws gives 21 ties
  and 420 incomparable ordered pairs. This is not a collapse theorem for
  controlled achievement envelopes.
- Tests check private memory, witness correctness, matched-frame preorder
  behavior, consistent state/action relabeling, duplicate program aliases,
  repeated artifact generation, and nonzero exit on a failed acceptance gate.

## Retained evidence

The retained run contains:

- [summary.json](../validation_results/operational_continuation_comparison_v0/20260928/summary.json):
  exact rational profiles and response laws, target-to-source witnesses,
  counterexample inputs, boundary summaries, and every expected/observed gate.
- [evidence.json](../validation_results/operational_continuation_comparison_v0/20260928/evidence.json):
  world kernels, preparations, costs, installed controller tables, and all
  admitted run laws, including local observations/memories, failures, and
  censoring. Rejected teams retain their maximum cost; their paths can be
  reconstructed from the retained kernel and controller tables. Boundary and
  probabilistic-setup controls retain their underlying models and laws too.
- [provenance.json](../validation_results/operational_continuation_comparison_v0/20260928/provenance.json):
  source revision, Python version, and SHA-256 hashes of the source files used.
  These are hashes of working-file bytes, including checkout line endings.
- [report.md](../validation_results/operational_continuation_comparison_v0/20260928/report.md):
  generated verdict table and acceptance gates.

The implementation commit precedes the artifact commit so the provenance
identifies committed executable sources without a self-referential hash.

## Reproduction and validation

From the repository root with Python 3.11-3.13 and its test dependencies:

```powershell
python -m omega_v2.validation.operational_continuation_comparison_v0
python -m pytest -q tests
python -m omega.validation.baseline_witness_smoke --out-root results/local_runs/operational_comparison_smoke --skip-pytest
python -m omega.validation.baseline_witness_family_smoke --out-root results/local_runs/operational_comparison_family_smoke --skip-pytest
python -m ruff check omega_v2/finite/operational_continuation.py omega_v2/experiments/operational_continuation_comparison_v0.py omega_v2/validation/operational_continuation_comparison_v0.py tests/test_operational_continuation_comparison.py
git diff --check
```

The default evidence output goes to a new timestamped directory beneath ignored
`results/local_runs/operational_comparison`. An explicit `--out-dir` must name a
new directory; the runner refuses to overwrite retained evidence. Compare the
parsed result and evidence JSON when reproducing on another checkout; revision,
runtime metadata, and source-byte hashes may differ.

Validation on Windows with Python 3.12.14:

| Check | Result |
| --- | --- |
| New test file | 14 passed |
| New tests plus four directly related predecessor files | 78 passed |
| Full `tests/` regression suite | 638 passed |
| Acceptance runner | PASS, 34/34 gates |
| Baseline witness smoke | PASS, 13 witnesses; retained digests match |
| Baseline family smoke | PASS, 13 families / 165 cases |
| Ruff on the four new Python files | Passed |
| Diff whitespace | Passed |

Test counts overlap; they must not be added. Smoke commands skip their internal
pytest calls because those tests already passed in the full suite. The new
evaluator and runner use only the Python standard library and existing v2
primitives. No Lean changes or proof-assistant validation are claimed.

## Assessment and remaining gap

This implements a bounded version of the proposed next step: the comparisons
are explicit, hidden-input policy switching is excluded, and the five examples
are reproducible. Incomparability survives where the declared tasks or response
laws conflict.

The next mathematical gap is a resource-accounted online adapter and a
substitution theorem for connected systems. Finite response emulation does not
yet establish that theorem. The theory's choices of task/readout, real-world
measurement, extraction and preparation cost, and normative interpretation
also remain open.
