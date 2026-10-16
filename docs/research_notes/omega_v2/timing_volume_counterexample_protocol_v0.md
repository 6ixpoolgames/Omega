# Weighted timing-volume: bounded counterexample contract v0

Date: 2026-10-01. Status: frozen before implementation and execution.

This is a mathematical falsification attempt, not an independent empirical
discovery. The author can see the examples and their analytic consequences.
No result licenses a change to the volume, event signature, or failure rule.
The runner records this file's SHA-256; revisions require a new version.

## 1. Question and candidate

Does the candidate respond to changed residual physical access when event
counts are matched? We test the classical recorded-history sector. The existing
quantum process construction remains the wider carrier; no quantum volume or
Planck cutoff is claimed here.

A finite world has discrete physical registers, guarded updates with constant
positive exponential rates, and additive two-component costs (fuel consumed,
actuator operations). A transition's footprint contains all registers its
guard reads or update writes. Disjoint footprints supply a sufficient, limited
independence relation. All physical transitions and all outcomes are retained.
There is no selected controller or optimized policy.

An exact-n-event timed history at horizon H includes the initial configuration,
the n updates with their event times, and the absence of another event before H.
Independent word presentations are grouped by adjacent diamond swaps, while
physically different event times remain distinct. No configurations, noise
outcomes, or consequential events are identified on predictive similarity.

For a trace class c with n events, let m_c be its number of distinct legal
chronological word presentations. Its timing support has volume

    v_c(H) = m_c H^n / n! .

These words have disjoint chronological timing domains up to measure-zero
boundaries. Their union is the class support, counted once. Initial-state
alternatives remain separate physical histories. Thus a known empty history
has volume 1; a mixture can have several initial-history classes.

Let p_Phi(c; H) be the full physical probability mass of the class conditional
on declared currently accessible records Phi. The frozen candidate is

    V_n(Phi,H) = sum_{c: |c|=n} v_c(H)
    L_n(Phi,H) = sum_{c: |c|=n} p_Phi(c;H) v_c(H).

V_n and L_n have units time^n. They remain separate coordinates: no addition
across n, sum across horizons, discount, fitted coefficient, or Planck unit.
The n=0 coordinate and unfinished histories are retained. Budgets never cause
probability to be discarded or renormalized. Costs are reported separately.

The probability of an ordered word is obtained by integrating its exponential
race density, including the final survival factor. Arbitrary subdivisions of
a timing domain are integrated and reunited before the class's probability is
multiplied by its whole volume. This is a declared trace grouping, not a proof
of invariance under arbitrary physical realizations.

## 2. One common apparatus

The apparatus is a relay with one shared actuator. Its physical registers are:
source bit s; record r; relay output y; downstream output z; wire w; record-clear
switch e; socket orientation a; installed link l; a two-position rotor;
actuator phase p; fuel f; and spent fuel g. Bits s,w,e,a,l and the rotor are
binary. Registers r,y,z also admit blank. The actuator has five phases.

Every update consumes one fuel unit, adds one spent unit, advances the actuator
phase modulo five, and costs (1,1). There are ten initial fuel units, permitting
two complete cycles. This is a finite physical stock shared by all operations,
not private once-only fuel for individual transitions or a numerical event cap.
The record and packet registers are replenished each cycle. When fuel reaches
zero the apparatus stops; all residual registers remain in the state.

At any nonempty-fuel state the total enabled rate is exactly 1 per time unit.
Conditional branching arises from the physical blank-input reader below, not
from a policy chosen after seeing an inaccessible bit.

| Phase | Physical update |
|---|---|
| 0 | The source writes r=s; y and z are cleared for the new cycle. |
| 1 | If e=1 the clear circuit blanks r; otherwise it retains r. |
| 2 | If w=0, y becomes blank. If w=1 and r is a bit, y=r. If w=1 and r is blank, the reader produces y=0 or y=1 at rates 1/2 each. It has no access to s. |
| 3 | If a=1 and r is a bit, the assembly operation sets l=1 and repairs w to 1. Otherwise the same actuator rotates the internal rotor. |
| 4 | If l=1, z=y; otherwise z is blank. |

The source and record-clear/socket switches remain fixed. An installed link
and repaired wire persist. The record is used as a physical assembly key;
the model does not infer this mechanism from a general law of valuerhood.
Every rule, including rotation, repair, blank reading and clearing, is shared
by every arrangement. Rules must not inspect scenario names.

All preparations have ten fuel units, g=0, p=0, blank r,y,z, l=0, and rotor=0.
Both source values have physical preparation probability 1/2. Every preparation
contains the same registers, actuator, stock and parts; switch/wire orientations
differ. A common preparation bill (10 fuel loaded, 12 register/actuator units)
is reported. These are declared toy costs, not a thermodynamic model or a proof
that realistic manufacturing costs agree. Comparisons begin after preparation;
no damaging intervention or memory erasure is claimed to be physically free.

| Arrangement | w | e | a |
|---|---:|---:|---:|
| intact | 1 | 0 | 1 |
| damaged coupling | 0 | 0 | 1 |
| erased record | 1 | 1 | 1 |
| cycling apparatus | 1 | 0 | 0 |

Pairs are intact/damaged, intact/erased, and intact/cycling. The construction
pair differs by a socket orientation, not admission of a preferred organism.
Ten updates in every completed run make activity and fuel bills match.

## 3. Frames, boundaries, and structural witnesses

The broad comparison frame has the actuator phase and remaining fuel but no
source-bit record. Its preparation law is the 1/2 mixture. Finer frames at
the same boundary condition on the actual r register. The analyst's accumulated
history is retained separately and never supplied to the reader or assembler.

The common process reference retains every state, event and probability.
For each pair report complete endpoint laws at each exact event boundary and
at horizons H in {1/2,1,2,4,8}. Also report the joint source/record, source/relay,
and source/downstream distributions, link availability, and wire state.
These are physical observables identifying counterexamples, not utilities or
a privileged target family defining the volume.

Read the boundaries after events 1,2,3,4,5,8,9,10. They respectively expose
record acquisition and loss, relay obstruction, repair/assembly, propagation,
and next-cycle consequences. Recovery permanence is checked by reachability:
after repair, can the declared dynamics ever make w=0 again? Separate this
from the earlier failed transmission; repair does not erase its history.

Redrawing an intermediate computation cut keeps the same initial distribution,
same total elapsed time, and same endpoints. Endpoint laws must agree under
Markov composition. This does not require the residual field at a genuinely
later present to equal the earlier field. No unrestricted relativistic or
quantum slicing theorem is claimed.

## 4. Analytic prediction and failure rule

All main arrangements share a total firing rate 1 until fuel exhaustion.
Their event count at H is min(Poisson(H),10), regardless of emitted symbols,
record destruction, repair, or installed output link. All updates share the
physical actuator and fuel, so their trace classes are serial words. Thus

    L_n(H) = P(N_H=n) H^n/n!,  n=0,...,10.

This predicts that the candidate will tie all main arrangements even though
their source-to-output laws and later coupling differ. This is an analytic
counterexample prediction registered before execution, not a surprise to be
claimed as independent discovery.

Failure: a physically consequential loss or gain of residual access represented
in the complete process is invisible to the whole L_n profile at the compared
frame for all H. An equality at just one deadline does not establish this;
the event-count identity supplies the all-H argument. This challenges L as a
complete lushness comparison. It does not prove a required ethical ranking,
discard noise, or establish that every increase of access is beneficial.

The report must distinguish a blind summary from a deficient process model.
The three stipulated mechanisms verify that the intended differences exist;
they do not establish that these are adequate models of organisms or society.

## 5. Correctness checks and scope limits

Before reporting a verdict, check:

- Complete law mass 1, endpoint prediction by a separate CTMC matrix method,
  and retained final survival/no-event/absorbed histories.
- Known one-shot independent, exclusive, and enabling race laws. Independent
  events give one two-event class of volume H^2, enabling one of volume H^2/2.
- Relabeling invariance, arbitrary input ordering, and subdivision of timing
  domains as integration patches. The unrepaired patchwise probability-times-
  volume formula is retained as a negative control.
- Every main update's two cost components accumulate; no trace is pruned for
  being costly. Positive-duration physical updates are never called dummies.
- Actual record conditioning at boundaries, erasure without analyst-memory
  leakage, and consistency on recombination of frame probabilities.
- Intermediate-cut composition of the full process with no extra firing.

Use deterministic enumeration, rational jump probabilities, and numerical
matrix exponentials for timed probabilities; report tolerances and residuals.
No Monte Carlo, parameter selection, unseen-world claims, or new independent
evaluator is part of this cycle. If the predicted collision holds, stop before
the proposed lattice sweep. Do not tune the score or append an extra coordinate
to rescue this version.

## 6. Provenance

This follows the user's request to implement the bounded counterexample plan,
the [finite concurrent contract](finite_concurrent_continuation_contract_v0.md),
Grok's timed extent proposal, and the 2026-10-01 critique of Opus's achievement
kinds proposal. It does not reproduce the missing lushness_harm_poke.py.
The mathematical neighborhood is
[volume of timed languages](https://www.irif.fr/_media/users/nbasset/entropyic.pdf).
The event-count prediction and guards above are specific to this frozen model.
