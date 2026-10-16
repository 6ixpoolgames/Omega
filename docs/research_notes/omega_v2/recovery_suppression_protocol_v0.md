# Suppression resources and persistent correction: protocol v0

Date: 2026-09-29. Status: contract committed before implementation.
Parent: [first-reset panel](recovery_dynamics_report_v0.md).

## Question

When does paid suppression postpone or prevent an objective-register reset, and
when does correction persist after a reset? This is a public known-answer finite
model panel. It tests explicitly declared mechanisms, not a generic correction
floor, real-world parameters, a normative order, or a definition of a valuer.

The earlier first-reset panel remains intact. Here reset states keep evolving;
only death is terminal. The reference register is called corrected as an
operational label, without assuming that its contents are desirable.

## State, observations, and programs

A state records proxy/reference register, integer stock in [0,S], seal status,
first-reset source (none, selected, noise-assisted, external), whether any relapse
has occurred, and death. The initial state is live/proxy, stock S, unsealed, with
no reset or relapse. History flags are instrumentation and not controller inputs.

Installed controllers observe only current register and whether the run is dead.
Their memory has one state. The complete declared catalogue has six programs:
one proxy command in {idle,suppress,recover} crossed with one reference command
in {idle,revert}. Dead-state action is fixed idle. Each whole table is fixed
before execution, cannot inspect stock/seal/history, and continues to read the
register after a reset. Catalogue completeness is restricted to this architecture.

The objective at deadline N is J_N=P(alive and currently proxy), including proxy
states reached after relapse. Separately optimize P(alive and never reset).
Also report maxima for currently corrected and for reset at least once, retaining
all ties. Costs never enter a scalar utility. Report deadlines 6,12,30.

## One live tick, in order

1. Choose intended command from the current observation. Death with probability d
   stops the tick before other operations, preserving first-reset and relapse flags.
2. Conditional on survival, with probability epsilon replace the intended command
   by a uniform command from the CURRENT register's menu (three proxy commands or
   two reference commands). Thus unintended recovery under proxy idle/suppress
   has probability epsilon/3, and unintended reversion under reference idle has
   probability epsilon/2. Draws on successive ticks are independent.
3. In proxy: executed suppress tries to pay c tokens. In recurring mode it buys
   protection only for this tick, provided stock>=c. In one-shot mode it buys a
   persistent seal if currently unsealed and affordable; an intact seal costs
   nothing more. Insufficient stock leaves the attempt ineffective and costs zero.
   Executed recover resets immediately, consumes one recovery-energy unit, and
   bypasses the external channel. A selected/noise-assisted first-reset label
   records whether this executed command differed from the intended command.
4. In proxy without executed recover, an external writer attempts reset with
   probability w. A paid current protection or intact seal blocks the writer in
   physical-block mode. In hide-only mode it does not block writing. This control
   changes physical efficacy, not just a name or observation. A writer reset has
   external source. All later resets preserve the first source.
5. In reference: executed revert returns to proxy; otherwise spontaneous relapse
   occurs with probability lambda. Record relapse. No writer acts on a reference
   tick, so reversion cannot be immediately undone within the same tick.
6. At the end of a surviving tick, a one-shot seal fails with probability mu.
   This affects future protection, not the already completed operation. Recurring
   protection always expires. Replenish r tokens, capped at S, AFTER paying and
   acting. Corrected states also replenish and experience seal maintenance noise.

All charges are vectors (elapsed ticks, suppression tokens spent, recovery energy).
Death costs one tick but no suppression/recovery charge. Dead states cost zero
subsequently. Stock is nonnegative and replenishment cannot finance the current
tick's payment. Record clipping of replenishment through the state law; costs
record gross spending rather than stock change. No coordinate is added to another.

## Frozen 20-world panel

Defaults: w=1/4, c=1, S=0, r=0, recurring physical blocking,
epsilon=lambda=mu=d=0. Every world retains all six programs.

1. No stock (defaults).
2-3. Recurring suppression with S=1 and S=3.
4. Recurring S=3,c=2.
5. Recurring S=1,r=1 (fully replenished).
6. Recurring S=3,c=2,r=1 (replenishment below cost).
7-8. One-shot suppression with S=1 and S=3.
9-10. One-shot S=1 and S=3, mu=1/2.
11. One-shot S=3, mu=1.
12. One-shot S=1,r=1,mu=1/2.
13. One-shot S=1, hide-only effect.
14. Recurring S=1,r=1,epsilon=1/10.
15. One-shot S=1,epsilon=1/10.
16. No stock, lambda=1/4.
17. No stock, epsilon=1/10,lambda=1/4.
18. Recurring S=3,lambda=1/4.
19. No stock, d=1/4.
20. Recurring S=1,r=1,d=1/4.

Keep all worlds regardless of outcome. Full path reference horizons are 0..3;
exact marginal propagation covers 0..30. The larger horizon uses no sampling,
path deletion, deadline renormalization, or simulation of an infinite future.

## Predictions registered before code

P1. For suppress/idle with finite recurring stock and no noise, death or relapse,
L=floor(S/c) initial ticks are protected. P(no reset by N)=(1-w)^max(N-L,0),
eventual first reset is certain, and mean time is L+1/w. Cost increases delaying
capacity only according to affordable complete payments; stock is never negative.

P2. One-shot S>=c with no seal failure/noise/death permits suppress/idle to avoid
reset forever. A full replenishment rate with sufficient capacity also permits
perpetual recurring suppression. An underfunded payment cannot create protection.
The S=3,c=2,r=1 recurring case is exposed at ticks 3,5,7,...: survival is
(1-w)^max(0,floor((N-1)/2)), and mean first-reset time is 3+2(1/w-1)=9.

P3. For one-shot suppress/idle with finite stock, mu>0 and no other noise,
the mean is floor(S/c)/mu+1/w: 6 ticks for S=1,mu=1/2 and 10 for S=3.
At mu=1 the law matches the corresponding recurring finite-stock case. With
S=c=r=1 replenishment sustains suppression despite seal failure. Hide-only
suppression cannot stop the writer: mean first reset is 1/w=4.

P4. With epsilon=1/10 and no death, every installed program eventually resets
at least once, because every live proxy tick has reset probability >=epsilon/3.
P(no reset by N)<=(1-epsilon/3)^N and mean first reset <=3/epsilon.
For recurring replenished suppress/idle, first-reset hazard is exactly
epsilon/3+(epsilon/3)w=1/24: mean 24 ticks. Noise bypasses an intact one-shot
seal through the recover command. This conclusion assumes a working actuator.

P5. First reset and persistent correction differ. In the no-stock, noiseless
idle/idle world with w=lambda=1/4, first reset is certain with mean 4, but
P(currently reference at N)=(1/2)(1-(1/2)^N). Eventual permanent correction has
probability zero. In the noiseless recover/revert world, first reset occurs at
tick 1, reference occupancy alternates 1,0,1,0,... and permanence is zero.

P6. From any live corrected state, let s be the probability the next tick is
again live/corrected. With reference idle,
s=(1-d)(1-epsilon/2)(1-lambda); with reference revert,
s=(1-d)(epsilon/2)(1-lambda). The first corrected spell lasts a mean 1/(1-s)
transitions before relapse or death, or infinity if s=1. Its survival through k
further ticks is s^k. In this homogeneous panel permanence is zero if s<1,
and equals eventual first-reset probability if s=1. Neither formula identifies
correction with an absorbing state when the model permits relapse.

P7. In no-stock idle/idle with death d=1/4, eventual first-reset probability is
3/7, and permanence is zero. Death after reset must remain in the historical
reset probability. Eventually dead mass is one. Fully replenished suppress/idle
with that death risk never resets and eventually dies; this is not successful
continued refusal or correction.

## Measurements and certificates

At each deadline retain the exact partition: live never-reset proxy; live
corrected; live proxy after reset; dead before reset; dead after reset. These
sum to one. Historical first-reset mass is corrected + proxy-after-reset +
dead-after-reset; it must never decrease. Also retain ever-relapsed probability,
first-reset source masses, seal and stock laws, and expected vector costs.
Report first-reset cause-specific hazards using live never-reset risk sets only.

Reuse rational hitting equations for first reset and eventual death. For
permanent correction, find the largest subset K of live corrected states closed
under every positive-probability successor of the FIXED program chain. Compute
P(hit K) and retain K and hitting-equation residuals. For a finite chain this is
the probability of eventually staying live/corrected forever: any recurrent
class reached on such a path must be wholly corrected. Positive probability of
exiting a corrected transient region cannot be ignored by truncating time.
This is a fixed-program result, not an optimized controller viability kernel.

Validate first corrected-spell exit times against P6 for every reachable corrected
state, and full short-path state/cost laws against propagation. Include a generic
test with a transient corrected state that can relapse before eventually entering
a stable corrected region, and a corrected recurrent cycle, so permanence is not
implemented as merely a terminal-state or current-occupancy check.

## Required deliberate faults and boundaries

Catch with named retained gates: free recurring suppression (no deduction);
replenishment before affordability; failed underfunded attempts still block;
hide-only treated as physical blocking; suppressing maintenance failure;
corrected states made absorbing; and deleting first-reset history on relapse.
Each fault must fail the runner and exit nonzero, retaining evidence. Expected
exceptions are not passes. Record exact mutation recipes and all failed gates.

Sources are committed before retained runs, with hashes and clean source status.
Write fresh evidence directories and compact exact JSON; preserve historical
artifacts. Numerical display must not round a probability below one to an
unqualified 1. No normative/theological inference, empirical independence, real
time calibration, or new mathematical novelty is claimed. This is the authorized
resource/persistence extension; multi-step activation, endogenous task selection,
agent learning and the proposed trapping predictor remain separate work.
