# Frame information and memory audit: report v0

Date: 2026-09-29. Status: retained finite instrument audit.

The full evaluator, C1 graph, conventional quotient, and memoized predictor
agree on all seven memory/access cases. No erased-information leak was found
in these existing predictors. The new contract distinguishes the analyst's
history from the controller's currently accessible records; the new controls
guard that distinction without changing the predictor semantics.

- [Contract](frame_information_audit_protocol_v0.md), committed before code at `6c16e80`
- [Definitions, mathematical clarification, and limits](frame_information_audit_v0.md)
- Implementation revision: `9d2ac37343524be676d3d95d8bfb26f5948169e1`
- [Retained run](../validation_results/frame_information_audit_v0/20260929/)
- [Exact models, predictions, and frame evidence](../validation_results/frame_information_audit_v0/20260929/evidence.json)
- [Checks and controller witnesses](../validation_results/frame_information_audit_v0/20260929/summary.json)
- [Source hashes and revision](../validation_results/frame_information_audit_v0/20260929/provenance.json)
- [Deliberate-fault failures](../validation_results/frame_information_audit_v0/20260929/mutation_audit.json)

## Results

All **352 checks** passed. Each case has sixteen installed programs, chosen
before the fair input bit is prepared. The figures below are the best
probability of a completed correct guess; all four predictors give these values.

| Apparatus | Horizon | Budget | Best probability |
| --- | --- | --- | --- |
| Memory preserved, no archive | 5 | 6 | 1 |
| Memory erased, no archive | 5 | 6 | 1/2 |
| Memory erased, sealed archive | 5 | 6 | 1/2 |
| Memory erased, permitted archive read | 5 | 6 | 1 |
| Permitted archive, short deadline | 4 | 6 | 1/2 |
| Permitted archive, insufficient retrieval budget | 5 | 5 | 1/2 |
| Permitted archive, zero budget | 5 | 0 | unavailable |

Skipping retrieval takes four ticks and four tokens. Retrieving takes five
ticks and six tokens, including when access is denied or the archive is absent.
At horizon four, retrieving programs have spent five tokens and remain
unfinished; their full probability mass is retained. With budget five and
horizon five, all eight retrieving programs are rejected at cost six, while
the eight skipping programs remain available. Zero budget admits no program.

The comparisons include exact complete histories, memory updates, observation
histories, cost, censoring, rejected-program costs, all-depth quotient
partitions, and full-model checks of the claimed optimal program witnesses.
Matching the best score alone would be a weaker test.

## What the frame audit establishes

After erasure, an analyst looking at the historical observation knows the bit,
but a controller looking at its current observation and reset memory does not.
The historical posterior for bit=1 remains 0 or 1. The controller-accessible
posterior is 1/2. The two hidden input histories have identical accessible
records, giving an explicit counterexample to later-information refinement.

The historical tower identity holds. The forward accessible-information
identity fails across erasure by +1/2 on the old bit-0 cell and -1/2 on the old
bit-1 cell. The reverse coarsening identity still holds. Retaining the bit
preserves the forward identity, and a permitted archive read provides a new
refinement from the blank frame to an informed frame. A sealed archive leaves
the accessible posterior at 1/2.

These conclusions concern fixed readouts under a fixed program and input law.
They do not establish a dynamic-programming theorem for arbitrary restricted
controller catalogues. The linked note specifies the additional assumptions
required for that claim and explains why a correctly specified earlier optimum
already accounts for a mandatory future erasure.

The conditioning utility was also checked on all 256 pairs of binary
information maps on four positive-mass atoms. Using each of the four indicator
readouts confirms the finite relation between refinement and the tower identity
for all those readouts. A separate constant-readout control shows why agreement
on one readout is insufficient to infer refinement.

## Deliberate faults

All three mutations produce a nonzero runner exit and retained FAIL evidence.
The compact failure record includes the exact source replacement and hashes,
expected failing check, actual failed checks, and exit code.

| Fault | Representative failed check |
| --- | --- |
| Query old memory history at the guess after erasure | `erased.c1.best_guess` |
| Bypass the apparatus's mandatory reset | `erased.reference.best_guess` |
| Remove the extra retrieval-request charge | `low_budget.reference.best_guess` |

The first fault alters graph execution. The other two alter the declared
apparatus contract. In those cases all predictors can agree on a wrongly
constructed fixture, so the advance known-answer expectations are necessary.
The quotient and C1 share a traversal engine; their construction is separate.
The full evaluator and recursive memoized predictor provide additional checks.
This is same-workflow instrument testing, not independent validation.

## Validation and reproduction

Validation used Windows and Python 3.12.14:

| Check | Result |
| --- | --- |
| Full regression suite | 705 tests passed |
| New focused file | 20 tests passed |
| Retained acceptance run | 352/352 checks passed |
| Deliberate faults | 3/3 caught |
| Focused Ruff checks | Passed |
| Branch whitespace checks | Passed |

These counts overlap. The source files were committed and clean before the
retained run. No existing predictor or Lean source changed. Historical evidence
from the operational, termination, and C1 audits remains unchanged.

```powershell
python -m omega_v2.validation.frame_information_audit_v0
python -m pytest -q tests/test_frame_information_audit.py
python -m pytest -q
python -m ruff check omega_v2/finite/information_frames.py omega_v2/experiments/frame_information_audit_v0.py omega_v2/validation/frame_information_audit_v0.py tests/test_frame_information_audit.py
```

The runner uses a new timestamped directory under
`results/local_runs/frame_information` by default. An explicit `--out-dir`
must not already exist. The exact evidence is valid tagged JSON with one whole
case per line, retaining the data while limiting generated diff lines. Source
hashes and revision metadata may differ between checkouts; the exact laws and
check results should reproduce. The focused mutation subset can be rerun with
`-k targeted_mutants` on the new test file.

## Claim boundary and next step

This resolves the information-definition issue for the finite repo model and
provides a regression instrument. It does not revise the Drive manuscripts,
prove physical information destruction, establish the new notes' normative or
theological readings, or change the C1 equivalence finding.

The next engineering task remains a public generated-world development workload
with a defined query language and practical baselines. An independently frozen
evaluation is still required before claiming a computational advantage. This
audit contributes information-access controls to that later workload.
