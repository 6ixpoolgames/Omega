# C1 equivalence audit and adversarial controls v0

Date: 2026-09-28. Development acceptance contract, committed before implementation.

This is the first deliverable of the [draft prediction pilot](continuation_prediction_pilot_protocol_v0.md).
It is not the proposed 24/96-world experiment, a sealed evaluation, or a test of
ethical value. The implementer also authors these known-answer controls.

## Claim and common interface

Implement C1 by bottom-up interning of cost-labeled probability distributions.
Independently implement the conventional quotient by pairwise partition
refinement. Compare the equivalence relation at every depth, not numeric node
identifiers. The expected result is equality, not a novel Omega construction.
Give the induction argument and state its limits.

Require one declared local-observation interface shared by all installed teams,
and a total registered atom map. Controller i sees only observation i; the
extractor may inspect the full supplied kernel. Compare complete atom/action/
local-observation/memory histories, elapsed time, accumulated cost, and censoring.
Raw state names are not observables unless explicitly registered as atoms.
Never discard over-budget branches: reject the entire team across every input.

The exact path evaluator is the reference. C1 executes its compressed graph.
The conventional quotient must also execute its quotient, and an ordinary
memoized predictor must execute the original model. The latter caches complete
suffix laws, retaining all costs; it need not key by remaining budget because it
never prunes by budget. This is a strong exact full-history baseline, not yet the
task-monitor-specific baseline or capped simulation of the future pilot.

## Known answers

1. Live command response and passive replay agree on command 0 but differ on 1.
2. A lookup decoy agrees with live on development commands 0 and 1, but differs
   on public control command 2. This command is not independently held out.
3. A duplicate-state mimic with identical laws for every allowed command remains
   equivalent. Relabeling and an independent, unobserved nuisance bit preserve
   responses and classes after mapping to the original states.
4. Dormant seed and inert control both fail service at horizon 1; at horizon 2
   with budget 2, the seed can build then serve and the inert control cannot.
   Budget 1 blocks that service. Construction costs and time are included.
5. An always-working model and a redundant A-or-B model agree under baseline
   and either single knockout. The double-knockout success range is [0,1].
   Adding its result identifies the matching member of this two-model class.
   Empty compatibility is inconsistent evidence, not a confident prediction.
6. Reuse hidden/transmitted bit, scarce joint repair, stochastic failed setup,
   transient history, partial cutoff, and costly terminal controls as regressions.
   Include horizon zero, empty admissible catalogue, and actual memory use.

Exact full laws, all-depth partitions, admissibility, and controller witnesses
must agree. Assertions must catch merging distinct transition costs, permitting
hidden-input program selection, losing joint-resource constraints, renormalizing
away incomplete probability mass, and omitting extraction from total CPU cost.
Mutations are development tests of the checking instrument, not discoveries.

## Evidence and accounting

Retain the complete finite models, controllers, atom maps, partitions, exact
predictions, expected answers, failed checks, source hashes, and revision. Record
extraction, prediction, and their sum separately for C1 and the conventional
quotient; direct prediction includes its cache construction. Serialize the whole
graph including preparations, decoding maps, controller tables, and budget.
Retain serialized input and result sizes separately; neither substitutes for
peak resident memory. One development timing sample is descriptive only, with
no speedup, significance, coverage, or break-even claim. Do not compare a cached
query-only cost with a competitor's construction-plus-query cost.

The runner exits nonzero and preserves evidence on a failed gate. Historical
artifacts remain unchanged. A subsequent report records what actually ran and
what remains before the independently frozen pilot.
