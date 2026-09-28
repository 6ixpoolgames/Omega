# Frame information and memory audit: protocol v0

Date: 2026-09-29. Public known-answer instrument audit, specified before code.

Parent: [C1 equivalence audit](continuation_equivalence_audit_report_v0.md).
Motivation: the new [present-frame note](https://drive.google.com/file/d/1S7WvGHXOn_Sa1JJfkKA7tRbOhVdwrYWW/view)
uses accumulated record histories while its erasure discussion concerns records
currently accessible. This audit separates those objects. It does not assume
that the existing predictors have an information leak.

## Contract

The analyst may retain the whole run for verification. At decision step t the
controller sees only its declared observation O_t and current finite memory M_t.
Past observations, earlier memories, the input identifier, hidden world state,
and predictor cache keys are not extra controller inputs. History H_t includes
all observations so far; accessible information A_t=(O_t,M_t) need not retain
H_t. Erasure is an explicit mandatory memory update in every installed program.

For one fixed program and one declared input law, compute exact conditional
expectations of a registered readout under these different information maps.
Check whether the later map refines the earlier map and whether the tower
identity holds for that readout. Equality for one readout does not by itself
prove refinement. Give the mathematical assumptions in a separate note.

## Finite fixture and known answers

A fair hidden target bit is shown to one controller. The next step either
preserves its memory or mandatorily resets it. The target remains available to
the grader, with no controller observation channel. An optional archive stores
the bit; a separate permission determines whether it can be read. No claim of
global physical destruction of information is intended.

The installed program family has one fixed skip/retrieve choice and each of
the eight binary guess tables over memory states blank, 0, 1: 16 programs.
All pre-erasure actions are identical, eliminating an action-based side channel.
The updates and observation maps are shared within a case; program selection
precedes the input. This is a complete catalogue for those declared choices,
not a universal controller-synthesis claim.

Skipping retrieval reaches the final guess in four ticks at cost four tokens.
Requesting retrieval inserts a read step: five ticks at cost six tokens. A
failed or denied read takes the same time and cost; it does not reveal the bit.
These are model token charges, not a thermodynamic account of erasure.

| Case | Horizon | Budget | Expected best completed correct guess |
| --- | --- | --- | --- |
| Memory preserved, no archive | 5 | 6 | 1 |
| Memory erased, no archive | 5 | 6 | 1/2 |
| Memory erased, sealed archive | 5 | 6 | 1/2 |
| Memory erased, readable archive | 5 | 6 | 1 |
| Readable archive, short deadline | 4 | 6 | 1/2, by skipping; reads unfinished |
| Readable archive, insufficient budget for retrieval | 5 | 5 | 1/2, by skipping; reads rejected |
| Readable archive, zero budget | 5 | 0 | unavailable |

At the post-erasure decision, the historical posterior for bit=1 is 0 or 1,
while the accessible posterior is 1/2. With memory retained it stays 0 or 1.
A successful read restores the accessible posterior to 0 or 1. Sealed or absent
archives do not. The full history remains informative even when the actor is
unable to use it; the best legitimate guess remains 1/2 in that case.

History refinement and its tower identity must hold. Forward accessible-frame
refinement and the corresponding martingale identity must fail across erasure;
the reverse coarsening identity must still hold. Under perfect recall the
forward identity holds. All claims concern one common law and a fixed readout.

## Verification and retention

Compare exact complete trace laws, whole-program budget rejection, best scores,
and checked program witnesses across the full evaluator, C1 graph, conventional
quotient, and memoized predictor. Compare graph partitions at every depth.
Retain failures and censored paths without renormalization. Verify cost and
deadline boundaries explicitly, including denied reads.

Add focused deliberate faults that recover erased information from a predictor
history, bypass the mandatory reset, or omit a retrieval charge. At least one
registered gate must reject each fault; exercise nonzero runner exit and FAIL
retention. Also check that current-information refinement cannot be inferred
from an accidentally constant readout.

Keep original evaluator semantics unchanged unless this audit finds a defect.
Commit source before the retained run. Save the finite fixtures, exact results,
frame partitions/posteriors and counterexamples, source hashes, and report in
a new evidence directory. Existing evidence is immutable. This audit supplies
no independent empirical evidence, new C1 semantics, normative ordering, or
claim of practical efficiency.
