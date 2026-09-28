# Operational continuation termination controls: protocol v0

Date: 2026-09-28.

Status: review-driven acceptance extension, specified before implementation.

The review supplied by the user identified two missing combinations in the
original five-case audit: mixed completed/censored outcomes, and a terminal
state with nonzero outgoing cost. These checks strengthen implementation
coverage. Their expected answers are known from the declared models; they
are not independent empirical evidence for lushness.

The original protocol, 34 gates, and retained run remain as historical evidence.
This supplement adds two fixtures and six gates without changing the evaluator's
semantics or relabeling the original run as having covered these combinations.

## Mixed completion and cutoff

One installed controller always issues `step`. From `start`, the world reaches
terminal `done` with probability 1/3 or `slow1` with probability 2/3. The slow
route is `slow1 -> slow2 -> done`. Every nonterminal transition costs one token;
the total kernel includes a zero-cost self-loop at `done`.

At horizon 2 and budget 2, retain exactly:

- Probability 1/3: `start -> done`, elapsed 1, cost 1, not censored.
- Probability 2/3: `start -> slow1 -> slow2`, elapsed 2, cost 2, censored.

The four gates check total mass 1, completed mass 1/3, censored mass 2/3,
and the joint endpoint/probability/time/cost/censoring rows. Tests also check
the exact paths and local histories. At horizon 3 and budget 3, the slow route
must complete at its original probability 2/3.

## Terminal stopping with a costly outgoing law

One installed controller issues `step`. The kernel has `start -> done` at
cost 1 and `done -> done` at cost 7. `done` is terminal. At horizon 3 and
budget 1, the only actual run stops after its first tick, costs 1, and remains
admissible. No observation, memory update, action, or charge occurs after it
stops. The two gates check that run's joint row and one admitted controller.

Removing terminal stopping would instead execute three ticks and cost 15,
making the controller inadmissible. The outgoing kernel row is a deliberate
tripwire for incorrect execution after the declared endpoint.

## Targeted mutation checks

Mutate isolated in-memory copies of the evaluator, never the checked-in source:

1. Whenever a run law has at least one completed outcome, discard censored
   outcomes and renormalize the completed ones. Leave wholly censored laws
   unchanged, so this fault specifically targets the original mixed-law gap.
2. Remove the terminal-state stopping guard and continue transitions until H.

Each mutation must leave the original 34 gates passing but cause at least one
specified new gate to fail. Run the real validation CLI entry point under each
mutation and require nonzero exit with a retained FAIL report. These two checks
do not reproduce or certify the reviewer's entire reported 15-mutation audit.

Retain the extended exact evidence in a new directory, plus a follow-up report
with source provenance, test results, and the scope of the two mutation checks.
