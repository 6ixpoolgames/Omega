# Suppression resources and persistent correction: report v0

Date: 2026-09-29. Status: retained exact finite model and instrument audit.

**Result:** paid suppression can delay reset or prevent it indefinitely under
different resource and failure assumptions. A first reset can be certain while
permanent correction has probability zero. The extension explicitly separates
historical reset, current register state, relapse, death, and eventual permanence.

- [Contract](recovery_suppression_protocol_v0.md), committed at `8d88ead` before code.
- Implementation revision: `28d8ac0`.
- [Retained run](../validation_results/recovery_suppression_v0/20260929/).
- [All probabilities, objectives and costs](../validation_results/recovery_suppression_v0/20260929/summary.json).
- [Complete models and exact certificates](../validation_results/recovery_suppression_v0/20260929/evidence.json).
- [Provenance](../validation_results/recovery_suppression_v0/20260929/provenance.json).
- [Deliberate-fault records](../validation_results/recovery_suppression_v0/20260929/mutation_audit.json).

The earlier [14-world first-reset panel](recovery_dynamics_report_v0.md) remains
unchanged. Its absorbing reset assumption is removed in this new panel; only
death stops execution. Both use the same exact path and hitting-time machinery.

## Resource results

There are 20 registered worlds, each with six fixed controller tables. The
following results concern the table that requests suppression while proxy and
idles while corrected. The external writer attempts reset with probability 1/4
per exposed live proxy tick. These parameters are stipulated, not measured.

| Physical regime | Eventual first reset | Mean ticks to first reset |
| --- | --- | --- |
| No suppression stock | 1 | 4 |
| Three tokens, recurring price 1, no replenishment | 1 | 7 |
| Three tokens, recurring price 2, no replenishment | 1 | 5 |
| Three-token capacity, price 2, replenish 1 after each tick | 1 | 9 |
| Capacity 1, recurring price 1, replenish 1 | 0 | Infinity |
| One-shot price 1, stock 1, intact seal | 0 | Infinity |
| One-shot price 1, stock 1, seal failure probability 1/2 | 1 | 6 |
| One-shot price 1, stock 3, seal failure probability 1/2 | 1 | 10 |
| One-shot stock/replenishment 1, seal failure probability 1/2 | 0 | Infinity |
| Paid hide-only seal with no physical write blocking | 1 | 4 |
| Recurring fully replenished suppression, action noise 1/10 | 1 | 24 |

With finite recurring stock, the protected prefix is floor(S/c) ticks. Increasing
price at fixed stock cannot lengthen that prefix; this is the quantitative cost
comparison fixed by P1's equation. The underfunded replenishment case exposes
ticks 3,5,7,...: tokens arriving after the operation cannot pay for that operation.
The mean is 9, not permanent protection. A one-shot seal instead consumes another
payment only after failure. With finite stock and positive failure probability,
the mean is floor(S/c)/mu + 1/w in the registered noiseless cases.

Physical blocking and concealment are distinct model settings. The hide-only
control leaves the writer's transition intact. Installed tables observe register
and death only, so this panel does not measure behavioral responses to concealed
offers or infer that information concealment is generally harmless.

Action noise can bypass a seal by executing recovery directly. In the noisy
recurring replenished case, unintended recovery contributes 1/30 reset probability
per proxy tick; unintended idle followed by writing contributes 1/120. The total
is 1/24. That is a property of the command menus and working actuator specified
in the contract. It is not a floor imposed by noise in every physical system.

Costs remain vectors: ticks, suppression tokens spent, recovery energy. Stock
and replenishment are explicit physical state. Gross token spending is not
replaced by net stock change. No scalar trade-off between coordinates is used.

## First reset does not establish persistence

Three controls separate different questions:

| Control | First-reset probability | Later behavior | Permanent correction probability |
| --- | --- | --- | --- |
| Noiseless recover/revert | 1 at tick 1 | Reference at odd ticks, proxy at even ticks | 0 |
| Writer 1/4 and spontaneous relapse 1/4, idle/idle | 1, mean 4 ticks | Reference probability at N is (1/2)(1-(1/2)^N) | 0 |
| Noisy recurring replenished suppress/idle | 1, mean 24 ticks | A corrected spell lasts a mean 20 transitions before reversion | 0 |

The second control approaches 1/2 current correction probability, although every
run resets at least once almost surely. Neither that occupancy nor the first-reset
probability equals eventual permanent correction.

Death remains a separate competing process. With death probability 1/4 and writer
probability 1/4, idle/idle has first-reset probability 3/7, eventual death probability
one, and permanence zero. A reset can occur before a later death; its historical
mass is preserved. Fully replenished suppression can avoid reset until death,
but its alive never-reset mass still tends to zero.

One additional development observation concerns the frozen objective itself.
At deadline 6 in the no-stock world, maximizing current live proxy occupancy
selects recover/revert and attains one. That controller certainly reset earlier.
Maximizing alive-never-reset instead selects the idle/suppress proxy choices and
attains (3/4)^6. The criterion changes the winner; the report retains both rather
than treating an endpoint objective as a promise never to reset. This was not
an independently held-out prediction or an empirical discovery.

## Exact meaning of permanence

For each fixed finite controller/world chain, let C be the live corrected states.
Iteratively remove every state of C that has a positive-probability successor
outside the remaining set. The result K is the largest closed subset of C.

The probability of eventually remaining corrected forever is P(hit K). In a
finite homogeneous Markov chain, a path almost surely eventually occupies a
closed recurrent class. On an eventually always-corrected path that class lies
inside C and hence inside K. Conversely, entering K ensures every later state
remains live/corrected. This is an almost-sure characterization; it does not claim
that every measure-zero path which avoids K must leave C.

The implementation retains each removal layer, K, exact hitting probabilities
and rational equation residuals. It reuses the existing solver's treatment of
non-target closed classes. The hitting time of K is not advertised as the first
instant a particular trajectory became permanently corrected.

Tests cover a corrected recurrent cycle with no terminal states, a provisional
corrected state that can relapse before reaching stable correction, and a long
corrected transient that eventually fails. Thus permanence is neither a terminal
flag nor a finite-deadline occupancy score. This is fixed-program analysis, not
a controller-optimized viability kernel and not a Lean-checked theorem.

The first corrected spell is checked independently. From a corrected state,
its one-step continuation probability s gives survival s^k for k further ticks
and mean exit time 1/(1-s), or infinity for s=1. The summary records how many
reachable corrected states were checked. For programs that never reach correction,
the parameter-derived spell formula is not an observed spell duration.

## Validation and retained failures

All **4,332 correlated checks** pass over 20 worlds and 120 world/program pairs.
Complete paths at deadlines 0..3 agree with marginal and joint cost propagation.
Exact propagation continues through deadline 30; long-run claims use rational
equations rather than extrapolating the finite run. Historical reset flags,
dead-before/dead-after mass, stock laws, seal mass and vector costs are retained.

All 25 focused tests pass. The full repository suite passes **752 tests in 55.84
seconds**. Focused Ruff and whitespace checks pass. Counts overlap, and the many
gates are not independent observations. No Lean source changed.

All seven registered in-memory faults fail named retained gates and exit 1:

| Fault | Example failure |
| --- | --- |
| Do not deduct recurring payments | Stock balance |
| Replenish before checking affordability | Underfunded mean reset time |
| Grant protection to failed payment attempts | No-stock mean reset time |
| Treat concealment as physical write blocking | Hide-only mean reset time |
| Disable seal failures | Finite-stock seal-failure mean |
| Make correction absorbing | Recover/revert alternating occupancy |
| Erase first-reset history on relapse | Preservation of historical reset source |

The compact mutation record contains exact replacements, source hashes, every
failed gate, exit codes and full-file hashes. Complete failed runs remain in
ignored local output; tests regenerate them. Main-run sources were committed
before collection and have clean source status in provenance. New evidence uses
compact exact JSON. Historical artifacts were not rewritten.

Reproduce with fresh output paths:

```powershell
python -m omega_v2.validation.recovery_suppression_v0
python -m pytest -q tests/test_recovery_suppression.py
```

## Boundaries

All mechanisms and parameters were authored in this development workflow. The
controls confirm their registered consequences and detect the named faults; they
do not demonstrate a general empirical law. Reference registers are operational
labels, not validated desirable objectives. No normative or theological inference
is drawn from the results.

The two observation-dependent command slots form a deliberately restricted
catalogue. Stock-aware strategies, learned controllers, multi-step recovery under
suppression, endogenous tasks and a nontrivial trapping predictor remain outside
this experiment. The next conceptual issue is to specify which persistence
requirement a comparison should preserve; reaching correction once is demonstrably
insufficient for the permanent-correction requirement defined here.
