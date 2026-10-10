# C1 equivalence and adversarial control-panel report v0

Date: 2026-09-28. Status: retained development instrument audit.

**Result:** the proposed C1 graph and the conventional bounded probabilistic
quotient induce the same equivalence relation. C1, the quotient, the ordinary
memoized predictor, and the existing full path evaluator agree on every
registered response law and admissibility decision in the public control panel.
This adds a checked implementation of a standard construction, with no distinct
Omega semantics or computational advantage established.

- [Mathematical argument and assumptions](continuation_equivalence_audit_v0.md)
- [Acceptance contract](continuation_equivalence_audit_protocol_v0.md), committed
  before implementation at `4f95e21`
- Implementation revision: `d57b5bd1501fe8f762c3363a828f271129859283`
- [Retained run](../validation_results/continuation_equivalence_audit_v0/20260928/)
- [Exact evidence](../validation_results/continuation_equivalence_audit_v0/20260928/evidence.json)
- [Checks and accounting](../validation_results/continuation_equivalence_audit_v0/20260928/summary.json)
- [Source provenance](../validation_results/continuation_equivalence_audit_v0/20260928/provenance.json)
- [Deliberate-fault results](../validation_results/continuation_equivalence_audit_v0/20260928/mutation_audit.json)

## What was implemented

The compiler interns bounded, cost-labeled probability distributions while
preserving terminal flags, local observations, and registered atom labels.
Its query engine executes installed local controllers on the compiled graph,
without consulting the original kernel. Full histories, failure mass, costs,
deadlines, and controller memories remain available for registered queries.

The conventional reference builds blocks by pairwise mass-vector comparison
and then materializes its quotient. It shares the graph traversal engine with
C1. The ordinary predictor uses a separate recursive suffix-law cache on the
original model. The pre-existing path evaluator supplies the full-model answer
key. Construction diversity and the separate predictor help detect errors;
all new code and controls were authored in this development workflow.

The audit checks partitions at every depth, exact full trace laws, whole-team
budget rejection, known answers, and the claimed controller witnesses.
The graph's partition is sufficient to preserve the registered responses; it
need not be the smallest partition for the installed controller catalogue.
The mathematical equivalence argument is not a checked Lean theorem.

## Observed controls

All **347 gates** passed across **25 public finite cases**. These counts include
correlated checks and repeated expectations across methods; they are not 347
independent scientific observations.

| Control | Observed result |
| --- | --- |
| Live versus replay | Same output on command 0; command 1 separates them |
| Live versus lookup decoy | Commands 0 and 1 agree; public command 2 separates them |
| Equivalent mimic | All full response laws agree despite extra hidden states |
| Seed at horizon 1 | Service probability 0 for both seed and inert control |
| Seed at horizon 2, budget 1 | Service probability 0 for both; activation/use cannot be free |
| Seed at horizon 2, budget 2 | Seed achieves 1; inert control remains at 0 |
| Hidden, transmitted, remembered bit | Best correct-guess probabilities 1/2, 1, and 1 |
| One versus two shared repair tokens | Joint repair probabilities 0 and 1 |
| Stochastic setup | Failure retained; best service probability 1/2 |
| Partial deadline cutoff | Completed mass 1/3; unfinished mass 2/3 |
| Costly terminal self-loop | Stop after one tick at cost 1; later cost 7 is never incurred |
| Equal base labels, different edge costs | Same depth-zero class; distinct depth-one classes |
| Limited knockout evidence | Both models remain compatible; double-knockout range [0,1] |
| Added double-knockout failure | The redundant model is the sole compatible model |
| Evidence contradicting both models | Report inconsistent evidence |

The lookup probe is a public acceptance control. It is not an independently
held-out intervention. The knockout diagnostic operates over two supplied
response tables, not a learned or exhaustive class of possible mechanisms.

Additional tests exhaust all **81** two-state, two-action rational kernels with
transition masses in {0, 1/2, 1}, under four registered atom/terminal variants:
**324 model variants**. At horizon 3, all methods preserve the same laws and
partitions. This small exhaustive census is another correctness check.

Consistent state/action relabeling and an independent hidden-bit extension
preserve the declared laws. For example, the live system has four states and
its extended mimic has eight, but both have four behavioral classes at each
tested depth. Decoding and controller tables are still included in storage.

## Checks that reject deliberate faults

Each of five in-memory source mutations triggered a nonzero validation exit
and a retained FAIL result. The compact retained record includes the exact
source replacement, hashes, exit code, and every failed gate; the pytest cases
reproduce the checks and verify that failed evidence is written.

| Fault | Example failing gate |
| --- | --- |
| Select the program after seeing the hidden input | `c1.hidden_bit` |
| Grant both repairs despite the joint constraint | `repair_1.c1_exact` |
| Discard incomplete paths and renormalize | `partial_cutoff.c1_exact` |
| Omit extraction from total CPU cost | `cost_accounting.synthetic_nonzero_extraction` |
| Erase transition costs while merging | `cost_distinction.partitions` |

These demonstrate sensitivity to the named faults, not exhaustive freedom from
bugs. The original operational and termination audit artifacts remain intact.

## Accounting and validation

The retained summary separates extraction CPU time from prediction CPU time
and checks their sum. It also records wall time, whole-graph serialized bytes,
input bytes, result bytes, and memoization cache entry counts. Graph bytes
include every layer, edge probability, preparation, decoding map, atom label,
local observation, installed controller table, action alphabet, and budget.
Direct memoized prediction includes building and using its cache in its timing.

There is only one development timing per method/case. Clock granularity can
give zero CPU durations for these tiny examples. Serialization, grading, and
evidence writing are outside method timings. Cache counts are not peak memory;
serialized bytes are not resident memory. No timing ratio, statistical
advantage, general storage saving, or break-even claim is made. Some whole
graphs exceed the size of their supplied models because depth layers and
decoding tables also cost space.

Validation on Windows, Python 3.12.14:

| Check | Result |
| --- | --- |
| Full regression suite | 685 tests passed |
| New focused file, including mutation checks | 43 tests passed |
| Retained acceptance run | 347/347 gates passed |
| Targeted deliberate faults | 5/5 caught |
| Focused Ruff checks | Passed |
| Whitespace checks | Passed |

Counts overlap and must not be added. The focused suite was rerun after adding
explicit certificate checks and source-cleanliness provenance. No Lean source
was changed. Source files were committed before the retained run; its only
untracked output at capture time was the newly created evidence directory.

Reproduce from the repository root in its Python environment:

```powershell
python -m omega_v2.validation.continuation_equivalence_audit_v0
python -m pytest -q tests/test_continuation_equivalence_audit.py
python -m pytest -q
python -m ruff check omega_v2/finite/continuation_prediction.py omega_v2/experiments/continuation_equivalence_audit_v0.py omega_v2/validation/continuation_equivalence_audit_v0.py tests/test_continuation_equivalence_audit.py
```

The runner defaults to a fresh ignored directory below
`results/local_runs/continuation_equivalence`. An explicit `--out-dir` must not
exist already. Exact evidence and checks are reproducible; timing, platform,
revision, and source-byte hashes can vary between checkouts. The mutation test
reproduction command is:

```powershell
python -m pytest -q tests/test_continuation_equivalence_audit.py -k targeted_mutants
```

## Remaining experiment

The [draft prediction pilot](continuation_prediction_pilot_protocol_v0.md)
remains unrun. It still needs a public development-world generator and task
grammar, task-specific practical baselines and capped simulation, a measured
workload with repeated timing and memory accounting, and a frozen independent
test/evaluator arrangement. No test seeds have been sealed and no independent
roles have been assigned by this audit.

The useful next question is whether this conventional representation earns its
construction cost on that declared workload. A later advantage would be an
engineering result for the tested models and tasks. It would not establish a
general measure of lushness, an ethical choice rule, or the cosmological theory.
