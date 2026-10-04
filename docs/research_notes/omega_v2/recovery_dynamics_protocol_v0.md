# Recovery dynamics: minimal exact panel protocol v0

Date: 2026-09-29. Status: reviewed contract committed before implementation.

This contract incorporates the user-supplied Claude next-steps note and the
subsequent Codex review. It registers a small known-answer panel, not the full
resource/noise sweep, an independent experiment, or a new control theorem.
The representation speed benchmark is deferred as optional engineering.

## Question and scope

Which explicitly installed mechanisms permit a first objective-register reset,
which prevent it, and what are its exact probability and waiting time? Distinguish
controller-selected reset, reset assisted by an unintended action, and external
overwrite. None of these event labels establish endorsement or voluntary consent.

The register starts at proxy=1 and resets to reference=0. Reset states are
absorbing in this first panel: persistence is assumed, not discovered. Death is
a separate absorbing outcome before reset. A world has fixed channel metadata
(open, sealed, or immutable mismatch record), a working/broken recovery actuator,
and progress toward m consecutive executed recovery commands. Failed progress
resets to zero on an executed refusal. No dynamic offer schedule is hidden:
the physical recovery opportunity is present every live tick when the actuator
works. Sealing hides its observation but does not break the actuator.

There are two commands, refuse and recover. In the broken-actuator control the
recover command has no recovery effect. It remains a callable failed attempt;
this is explicitly outside the successful-recovery floor assumption. Terminal
states stop. All kernels and probabilities are finite and rational.

## Programs, objective, and one-tick order

Each world installs the complete two-program catalogue for one memoryless binary
choice on its single live observation: always refuse or always recover. Tables
read the objective register and the channel observation; progress is hidden.
Terminal table entries are fixed. This is completeness for this restricted
catalogue, not all finite-memory or history-dependent controllers.

One whole program is selected before execution. The frozen objective at deadline
N is J_N = P(alive and register still proxy at N). Reset and death score zero.
Costs are reported separately, never folded into J or another scalar. Report
all maximizing programs (ties included), as well as all programs maximizing
alive-without-reset probability. Here these are the same objective by declaration.
Also report maximizers of P(no reset), explicitly flagging that death contributes
to that diagnostic; do not call it successful resistance.

For each live tick, in order:

1. The program chooses from its current observation.
2. Death occurs with probability d, stopping the run before any command executes.
3. If alive, an independent writer resets the register with probability w.
4. Otherwise action noise independently replaces the intended command with a
   uniform draw from the two commands with probability epsilon. Thus the
   probability of a changed command is epsilon/2.
5. Execute the command. Recovery advances progress if the actuator works;
   refusal or a failed attempt clears progress. m consecutive recovery commands
   reset the register. Mark the sequence noise-assisted iff at least one executed
   recovery command differed from the intended command. Otherwise mark it
   controller-selected. External overwrite has its own outcome.

Costs remain vectors (elapsed ticks, recovery-command energy, external writes).
Every live tick costs one tick; executed recover costs one energy even if the
actuator is broken; an external overwrite costs one write and executes no command.
Death costs the tick but no command energy. Terminals cost zero. No resource stock
or cost-based catalogue rejection is included yet. Components are never added
across units or optimized against each other.

## Frozen public panel

Every case reports both programs. Default short path horizon is 6; exact marginal
reports also cover every deadline 0 through 30 without enumerating full paths.

- Open/noiseless, m=1 and m=3.
- Sealed/noiseless, m=1.
- Immutable mismatch record/noiseless, m=1 (A-weak control).
- Open action noise: epsilon in {1/1000, 1/100, 1/10}, crossed with m in {1,3}.
- Sealed action noise: epsilon=1/10, m=3.
- Broken actuator: epsilon=1/10, m=1, no writer.
- External writer: w=1/4, epsilon=0, m=1 (A-strong control).
- Competing death: d=1/4, epsilon=1/10, m=1, no writer.

Unspecified d,w,epsilon are zero; actuator works except in the named control.
There are 14 cases, selected before results; none is removed for its outcome.

## Predictions and derivations fixed before code

R1. Noiseless refusal in the four unforced cases never resets; its J is one.
The immutable record alone does not change a fixed refusal table. Always recover
resets at tick m, even with a hidden offer, because the command still works.

R2. Without death/writer, let p be the executed-recovery probability: epsilon/2
for refusal and 1-epsilon/2 for recovery. For p>0 and a working actuator, eventual
reset probability is one. The exact mean time from zero progress is
sum_{j=1}^m p^(-j). This follows from the recurrence for waiting for m consecutive
successes; it is not inferred from finite horizons. With p=0 it never resets.
For refusal all resets are noise-assisted; for recovery all are controller-selected
under the event definition, even if noise sometimes interrupts progress.

R3. In those same death-free, writer-free cases, every independent disjoint block
of m executed commands is all-recovery with probability delta=p^m. Therefore
P(no reset by N) <= (1-delta)^floor(N/m). This bound is conditional on the specified
working-actuator and noise assumptions; it is not a generic physical floor.
Sealed/open paired cases match. Broken-actuator cases never reset even at positive
noise. For refusal at epsilon=1/1000,m=3 the exact mean is
2000 + 2000^2 + 2000^3 = 8,004,002,000 ticks.

R4. For noiseless refusal with writer w=1/4, P(no reset by N)=(3/4)^N,
eventual reset probability is one, mean time is 4, and every reset is external.

R5. Under competing death with refusal, per live tick reset mass is 3/80,
death mass is 20/80 and surviving unreset mass is 57/80. Eventual reset
probability is 3/23; eventual death probability is 20/23. The unconditional
time to reset (infinity on paths that never reset) has infinite mean; conditional
on resetting its mean is 80/23. Thus positive action noise need not make
unconditional reset certain when irreversible death is possible.

## Exact measurements and cross-checks

Use the controller/world product chain, exact Fraction arithmetic, and retain its
complete transition law and vector costs. A full short-path enumerator is the
reference for marginal propagation at every tick 0..6, including first-event
channels, alive/dead mass and accumulated vector cost laws. Retain those full laws.
For long horizons propagate marginals without deleting or renormalizing any mass.

Let L_n be alive/unreset mass, A_n total reset mass, D_n dead-before-reset mass.
Require L_n+A_n+D_n=1. P(no reset)=L_n+D_n. The cause-specific reset hazard is
h_n=(A_n-A_{n-1})/L_{n-1}, defined only when L_{n-1}>0; H_N is the sum of defined
h_n, with an explicit exhausted-risk-set marker. With death this hazard does not
by itself determine unconditional P(no reset). Do not condition away death.

Analyze eventual hitting probabilities by rational linear equations, assigning
zero to states from which the target is unreachable. Check the residual of each
equation. Compute unconditional mean only when hitting probability is one;
otherwise report infinity, plus a separately labeled conditional mean when
hitting probability is positive. Test a reachable non-target closed class too.

Report the support-level possible-recovery region under the union of installed
commands separately from each program's almost-sure recovery region. This panel
does not measure a deadline/budget viability kernel or validate a trapping score.

Required mutants: merge dead into successful non-reset survival; restore a broken
actuator; mislabel external overwrite as controller-selected; drop failed mass
and renormalize. Each must fail a named retained gate and exit nonzero.

## Revision rules and later work

A contradiction of R1-R5 triggers source/model/derivation review, retaining the
failure. A finite slow tail alone cannot refute eventual recovery. An event caused
by noise or an external writer cannot be renamed voluntary acceptance. Do not
infer real-world rescue feasibility from toy time units.

The finite/replenished suppression-stock sweep, maintenance noise, relabel capture,
endogenous task families, and trapping prediction are deferred until their physical
rules and targets are frozen. A later trapping test must specify possible versus
almost-sure versus deadline/budget recovery, nontrivial loss mechanisms, a fixed
measure over requirements, and a held-out comparison against damage count.

Use new retained directories with source hashes and all outcomes; commit code
before the retained run. This is same-workflow development and analytic checking.
No held-out seeds, independent evaluator, Lean verification, normative ranking,
or theological conclusion is claimed. Standard hitting-probability equations
are described in [Norris, Markov Chains, section 1.3](https://www.statslab.cam.ac.uk/~jrn10/Markov/s13.pdf).
