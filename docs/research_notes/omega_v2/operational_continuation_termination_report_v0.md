# Operational continuation termination controls: report v0

Date: 2026-09-28.

Status: both review-identified coverage gaps reproduced and covered.

- [Supplemental protocol](operational_continuation_termination_protocol_v0.md),
  committed before these changes at `2a8e5cb`
- Implementation checkpoint: `15e7e3c`
- [Extended retained run](../validation_results/operational_continuation_comparison_v0/20260928_termination/)
- [Original report and 34-gate run](operational_continuation_comparison_report_v0.md)

## Finding

The review supplied by the user correctly identified that the original fixtures
did not distinguish the correct evaluator from two specific faults: conditioning
a mixed completed/censored law on completion, and continuing to execute after
reaching a terminal state. The evaluator already had the intended semantics.
The missing pieces were discriminating fixtures and regression checks.

The two new fixtures pass without changing the core evaluator. The extended
runner passes all **40 gates**. Its first 34 gate records match the original
retained run exactly, including expected and observed values. The original
protocol and artifacts remain unchanged.

## New fixtures

| Fixture | Exact required result | Fault exposed |
| --- | --- | --- |
| Partial cutoff, horizon 2 / budget 2 | Completed run: probability 1/3, one tick, cost 1. Unfinished run: probability 2/3, two ticks, cost 2. Total mass remains 1. | Discarding unfinished runs and inflating completed probability to 1 |
| Terminal stopping, horizon 3 / budget 1 | The run reaches `done` after one tick at cost 1 and stays admissible. Its declared outgoing self-loop costs 7 but is never executed. | Continuing for three ticks, charging 15, and incorrectly rejecting the controller |

The partial-cutoff fixture's slow route completes after three ticks when the
horizon and budget both increase to 3. Its probability remains 2/3. Tests check
the full paths, action histories where relevant, local observations, memory
histories, elapsed time, cost, censoring flags, and task probabilities.

The terminal fixture checks that no extra action, observation, memory update,
or charge occurs after stopping. The costly self-loop is present in the total
world kernel so an erroneous extra step has a visible feasibility consequence.

## Targeted mutation checks

The tests compile isolated in-memory copies of the inspected evaluator with
one fixed modification each. They do not edit the checked-in evaluator.

| Mutation | Original 34 gates | New distinguishing gate | CLI result |
| --- | --- | --- | --- |
| Drop censored outcomes and renormalize whenever completed outcomes exist | All pass | `partial_cutoff.completed_mass` fails | Exit 1, retained status FAIL |
| Remove terminal stopping and execute until the horizon | All pass | `terminal_stop.admissible` fails | Exit 1, retained status FAIL |

Other new gates can fail under the same mutations. Each test requires the
named failure, verifies all original gates still pass, and checks that the
actual validation entry point writes a FAIL summary and returns nonzero.
For the first mutation, wholly censored laws are left unchanged; this isolates
the mixed-law gap and avoids an unrelated empty-distribution error.

This reproduces the two actionable gaps from the supplied review. It does not
independently certify the reviewer's complete reported set of 15 mutations.

## Validation and evidence

| Check | Result |
| --- | --- |
| Focused test file, including two targeted mutations | 18 passed |
| Full repository pytest run | 642 passed |
| Extended acceptance runner | PASS, 40/40 gates |
| Original gate records versus the retained original run | Identical |
| Ruff on changed Python files | Passed |
| Diff whitespace | Passed |

Counts overlap. The two mutation tests pass by detecting the deliberately
incorrect behavior and requiring a failed validation result.

```powershell
python -m pytest -q tests/test_operational_continuation_comparison.py
python -m pytest -q
python -m omega_v2.validation.operational_continuation_comparison_v0
```

The [summary](../validation_results/operational_continuation_comparison_v0/20260928_termination/summary.json)
contains the six new gates and joint outcome rows. The
[evidence](../validation_results/operational_continuation_comparison_v0/20260928_termination/evidence.json)
includes both full models and their admitted laws under `controls`. The
[provenance](../validation_results/operational_continuation_comparison_v0/20260928_termination/provenance.json)
records the committed implementation, both protocols, tests, runtime, and source
hashes. The runner retains ordinary unmutated evidence; the mutation definitions
and their required failures are executable in the test file.

## Interpretation

These are known-answer acceptance checks that make implementation defects easier
to detect. They supply no independent evidence for physical lushness or value.
A future toy-world study could test specified predictions under its declared
assumptions if it includes genuine failure criteria and competing explanations.
It would still need a separate justification for claims about real systems.
