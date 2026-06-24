<div align="center">

# Finite Recovery Under Observation, Coarsening, and Ambiguity

## A Source-Indexed Calculus for Finite Channels

Technical Internal Review Draft

S. Poole

June 24, 2026

</div>

---

## Abstract

This paper develops a finite, machine-checked recovery calculus for declared
targets observed through finite channels. The central object is not exact
support recovery, not a scalar channel score, and not an optimized capacity
number. It is the source-indexed recovery profile

```text
Rec_delta(x) = Pr[delta(observe(Y)) = target(x) | X = x].
```

For a finite channel, declared target, observation map, and decoder, this
profile records which source classes are recoverable and at what confidence.
Support-exact recovery appears as the threshold-one endpoint of this profile:
it is zero-error recovery, not the general recovery object. This lets the same
formal surface distinguish exact recovery, high-confidence non-exact recovery,
decoder-class restrictions, randomized decoding, prior-relative performance,
robust recovery under ambiguity, observation refinement, target coarsening,
joint recovery, and finite-horizon policy-conditioned continuation.

The contribution is a small theorem spine, checked in Lean, for reasoning about
when observations, summaries, priors, ambiguity sets, and decoder classes
preserve or fail to preserve declared recovery facts. The paper is motivated by
alignment and abstraction-integrity questions, but it does not claim value,
agency, identity, valuerhood, or Omega. It supplies a disciplined recovery layer
that later alignment-facing work can use without pretending that support-exact
recovery is the whole story.

## 1. Introduction

Many safety and alignment arguments depend on recovery claims. A model is said
to preserve a distinction, an evaluation is said to reveal a capability, a
coarse measurement is said to retain the relevant signal, or a policy is said
to keep a target reachable. These claims are often stated as if recovery were a
single fact:

```text
recoverable / not recoverable
```

or as if a single scalar score were enough:

```text
high score / low score.
```

Both compressions are unsafe. A target can be perfectly recoverable in the
zero-error support sense, approximately recoverable at high confidence,
recoverable only for some source classes, recoverable only under a prior that
hides bad cases, recoverable by a randomized decoder but not a deterministic
one, recoverable from a fine observation but not a coarsening, or recoverable
under one channel in an ambiguity set but not robustly across the set.

This paper isolates the finite structure behind those distinctions. We work
with exact rational finite channels so the statements are small enough to check
directly. The point is not to replace information theory, Blackwell comparison
of experiments, zero-error communication, statistical decision theory, or
robust Markov decision processes. The point is to expose a narrow recovery
surface that is useful for abstraction integrity:

```text
Given a declared target and observation, what recovery facts survive the
available decoder class, coarsenings, priors, randomized decoders, ambiguity
sets, and finite continuation horizons?
```

The answer is not a single number. The stable object is a family of recovery
profiles and monotonicity laws.

### 1.1 Why This Matters for the Larger Project

The larger Omega project studies when finite presentations, summaries, and
abstractions are allowed to stand in for future-facing structure. The recovery
layer is one of the cleanest external-facing pieces of that program because the
problem is immediately legible:

```text
Can the declared target be recovered from the observation we actually retain?
```

In alignment terms, this is an anti-Goodhart and anti-smuggling question. If an
evaluation, representation, benchmark, observation channel, or summary is used
as evidence for a target, then the target should factor through that retained
surface at the claimed recovery level. If it does not, then the retained surface
is not enough to certify the target.

This is also where the project's caution about exactness becomes important.
Support-exact recovery is useful, but too brittle to be the only formal object.
Many real channels are full-support or noisy, so zero-error recovery fails even
when high-confidence recovery is available. The correct finite object is the
source-indexed profile, with the zero-error case recovered as one boundary.

## 2. Relation to Existing Work

This paper sits near several established frameworks.

Blackwell's comparison of experiments studies when one information structure
is at least as informative as another for every decision problem. In the finite
setting, deterministic observation refinement and coarsening are the local form
we need: a decoder available from a coarse observation can be lifted to a finer
observation, while failure at the finer level persists under deterministic
coarsening.

Shannon's zero-error communication theory gives the classical context for
zero-error recoverability. Our support-exact bridge says that support-exact
recovery is exactly the threshold-one point of the finite recovery profile.
This is deliberately narrower than channel capacity: we do not optimize block
codes or asymptotic rates. We ask whether a declared target is recoverable from
a declared observation by a declared decoder class.

Statistical decision theory and robust Markov decision processes provide the
decision-theoretic and uncertainty-aware background. The robust recovery layer
uses an ambiguity set of finite channels and asks for one decoder that meets a
threshold across every channel in that set. The policy-continuation layer uses
finite rational action kernels and horizon-indexed hit profiles, but it does
not define value or optimal policy.

Recent work on useful information for bounded observers is also relevant. The
point here is compatible with that direction: "information" for this paper is
target-relative, observation-relative, and decoder-class-relative. A
deterministic coarsening cannot create recovery capacity for an unrestricted
decoder class, but a coarsening may still be a useful semantic representation
for a different task, observer, or model class. The theorem spine is about
declared recovery, not about all possible notions of usefulness.

## 3. Formal Setup

Let:

```text
X  = finite or arbitrary source states
Y  = finite output states
D  = declared target labels
O  = observation labels
C  = finite rational channel P(y | x)
d  : X -> D
o  : Y -> O
delta : O -> D
```

The channel is represented in Lean by:

```lean
structure RatChannel (X : Type u) (Y : Type v) [Fintype Y] where
  prob : X -> Y -> Rat
  nonneg : forall x y, 0 <= prob x y
  row_sum_one : forall x, (Finset.univ.sum fun y => prob x y) = 1
```

Positive support is:

```text
PositiveSupport C x y := 0 < C.prob x y.
```

The success mass of a decoder at a source state is:

```text
Success(C,d,o,delta,x)
  = sum_y if delta(o(y)) = d(x) then C(y | x) else 0.
```

The failure mass is the complementary sum over wrong decoded labels. The first
formal laws are:

```text
0 <= Success
0 <= FailureMass
Success + FailureMass = 1
Success <= 1
Success = 1 iff FailureMass = 0
```

The source-indexed recovery profile is:

```text
RecoveryProfile(delta)(x) = Success(C,d,o,delta,x).
```

Threshold recovery is worst-case over source states:

```text
DeclaredRecoveryAt(tau, delta)
  := forall x, tau <= Success(C,d,o,delta,x).

RecoveryExistsAt(tau)
  := exists delta, DeclaredRecoveryAt(tau, delta).
```

The decoder-class explicit version is:

```text
RecoveryExistsInAt(Allowed, tau)
  := exists delta, Allowed(delta) and DeclaredRecoveryAt(tau, delta).
```

The unrestricted version is recovered by taking `Allowed` to be every
deterministic decoder.

## 4. Theorem Spine

### 4.1 Profile Laws

The finite profile obeys elementary but important mass laws:

```text
success_nonneg
failureMass_nonneg
success_add_failureMass
success_le_one
success_eq_one_iff_failureMass_eq_zero
```

These are the bookkeeping lemmas that let the exact-support endpoint and the
approximate threshold layer live in one formal object.

Lean source:

```text
formal/lean/OmegaProper/Recovery/FiniteChannel.lean
```

### 4.2 Threshold Recovery

Threshold recovery is monotone in the threshold:

```text
tau1 <= tau2 and RecoveryExistsAt(tau2)
implies RecoveryExistsAt(tau1).
```

The same law holds for decoder-class-restricted recovery:

```text
tau1 <= tau2 and RecoveryExistsInAt(Allowed,tau2)
implies RecoveryExistsInAt(Allowed,tau1).
```

The unrestricted recovery predicate is the specialization of the restricted
one to the universal decoder class.

Lean source:

```text
formal/lean/OmegaProper/Recovery/Deterministic.lean
```

Representative theorem names:

```text
recoveryAt_mono_threshold
recoveryInAt_mono_threshold
recoveryExistsAt_iff_recoveryExistsInAt_unrestricted
```

### 4.3 Support-Exact Recovery Is the Threshold-One Endpoint

The exact support theorem from the earlier baseline-witness layer says that a
decoder is exact when every positive-support output decodes to the declared
source label. The recovery profile bridge proves:

```text
ExactDecoder(PositiveSupport C,d,o,delta)
iff
forall x, Success(C,d,o,delta,x) = 1.
```

Consequently:

```text
support-exact recovery exists
iff
RecoveryExistsAt(1).
```

This is the central rebase of the paper. Support exactness is zero-error
recovery. It is not the general recovery notion.

Lean source:

```text
formal/lean/OmegaProper/Recovery/Deterministic.lean
formal/lean/OmegaProper/BaselineWitnesses/ExactRecoverySupport.lean
```

Representative theorem names:

```text
exactDecoder_iff_success_one
supportExactRecovery_iff_recoveryAt_one
```

### 4.4 Strictness: High Confidence Without Support Exactness

A binary symmetric channel with 99/100 correct mass and 1/100 wrong mass has
full positive support. It is therefore not support-exact recoverable. But the
identity decoder reaches threshold 99/100 for every source.

This proves that:

```text
high-confidence recovery does not imply support-exact recovery.
```

Lean source:

```text
formal/lean/OmegaProper/Recovery/Examples.lean
```

Representative theorem names:

```text
highConfidence_recoveryAt_99_100
highConfidence_not_supportExact
```

### 4.5 Strictness: Positive Support Does Not Determine Approximate Recovery

Two binary full-support channels can have the same positive-support relation
while supporting different recovery thresholds. The high channel has 9/10
correct mass and 1/10 wrong mass. The low channel has 3/5 correct mass and 2/5
wrong mass. They agree on which outputs are possible, but not on how much
probability those outputs carry.

The Lean witness proves:

```text
same PositiveSupport relation
high channel has RecoveryExistsAt(9/10)
low channel does not have RecoveryExistsAt(4/5).
```

Thus support is enough for zero-error possibility, but not enough for graded
confidence.

Lean source:

```text
formal/lean/OmegaProper/Recovery/Examples.lean
```

Representative theorem names:

```text
high_low_same_positiveSupport
highFullSupport_recoveryAt_9_10
lowFullSupport_not_recoveryAt_4_5
```

### 4.6 Observation Refinement and Coarsening

If a coarse observation factors through a fine observation, every coarse
decoder can be lifted to a fine decoder:

```text
coarse = g o fine
lift(delta)(fine_y) = delta(g(fine_y)).
```

The lifted decoder has the same success mass as the original coarse decoder.
Therefore recovery from the coarse observation implies recovery from the fine
observation:

```text
RecoveryExistsAt(coarse,tau)
implies
RecoveryExistsAt(fine,tau).
```

The support-exact version is also monotone under refinement.

Lean source:

```text
formal/lean/OmegaProper/Recovery/ObservationRefinement.lean
```

Representative theorem names:

```text
lifted_decoder_success_eq
recoveryAt_mono_observation_refinement
supportExact_mono_observation_refinement
```

The corresponding permanence results say that failures at the fine level
persist under deterministic coarsening. This is the finite recovery version of
the anti-smuggling slogan:

```text
a deterministic coarsening of an already available observation cannot create
recovery capacity for an unrestricted decoder class.
```

Lean source:

```text
formal/lean/OmegaProper/Recovery/CoarseningPermanence.lean
```

Representative theorem names:

```text
recoveryAt_failure_persists_under_coarsening
recoveryInAt_failure_persists_under_coarsening
supportExact_failure_persists_under_coarsening
robustRecoveryAt_failure_persists_under_coarsening
randomizedRecoveryAt_failure_persists_under_coarsening
```

### 4.7 Target Postprocessing

Recovering a finer target implies recovery of any deterministic coarsening of
that target. If:

```text
h : D -> E
```

then a decoder for `d : X -> D` induces a decoder for `h o d : X -> E`. The
success mass for the postprocessed target is at least the success mass for the
fine target:

```text
Success(C,h o d,o,h o delta,x)
>=
Success(C,d,o,delta,x).
```

Exact recovery and threshold recovery transport along the same postprocessing.
The joint-to-marginal recovery facts are instances of this principle, with
`Prod.fst` and `Prod.snd` as target postprocessings.

Lean source:

```text
formal/lean/OmegaProper/Recovery/TargetPostprocessing.lean
```

Representative theorem names:

```text
success_le_targetPostprocess
declaredRecoveryAt_targetPostprocess
recoveryAt_targetPostprocess
recoveryInAt_targetPostprocess
exactDecoder_targetPostprocess
exactRecovery_targetPostprocess
```

### 4.8 Confusion Bounds

When two source states with different declared targets can produce the same
observation label, a deterministic decoder must be wrong for at least one of
them. The confusion-bound module turns shared observation mass into an upper
bound on recoverability:

```text
shared wrong-observation mass <= FailureMass
```

and therefore blocks threshold recovery above the remaining mass.

Lean source:

```text
formal/lean/OmegaProper/Recovery/ConfusionBound.lean
```

Representative theorem names:

```text
wrong_observation_mass_le_failureMass
shared_observation_mass_blocks_recoveryAt
```

### 4.9 Randomized Decoders

Randomized decoders choose target labels according to a rational distribution
conditioned on the observation:

```text
R.prob(o,d) = Pr[randomized decoder outputs d | observation o].
```

Deterministic decoders embed into randomized decoders as point masses. The
randomized success profile agrees with the deterministic profile under this
embedding:

```text
RandomizedSuccess(ofDeterministic(delta),x)
=
Success(delta,x).
```

So deterministic recovery implies randomized recovery. The strictness witness
uses one observation label and two source labels: no deterministic decoder
recovers both labels at threshold 1/2, while the uniform randomized decoder
does.

Lean source:

```text
formal/lean/OmegaProper/Recovery/Randomized.lean
formal/lean/OmegaProper/Recovery/Examples.lean
```

Representative theorem names:

```text
randomizedSuccess_nonneg
randomizedSuccess_le_one
randomizedSuccess_ofDeterministic
recoveryAt_implies_randomizedRecoveryAt
randomizedRecoveryAt_mono_threshold
constantObservation_not_recoveryAt_half
constantObservation_randomizedRecoveryAt_half
```

The family version makes decoder registries explicit by representing an
allowed randomized family as the image of a finite index set.

Lean source:

```text
formal/lean/OmegaProper/Recovery/RandomizedFamily.lean
```

Representative theorem names:

```text
randomizedFamilyRecoveryAt_iff_randomizedRecoveryInAt_image
robustRandomizedFamilyRecoveryAt_iff_robustRandomizedRecoveryInAt_image
```

### 4.10 Robust Ambiguity

Robust recovery replaces one exact channel with an ambiguity set:

```text
Gamma : Set (RatChannel X Y).
```

Recovery at threshold `tau` is robust when one decoder meets the threshold for
every channel in `Gamma`:

```text
exists delta, forall C in Gamma, forall x,
  tau <= Success(C,d,o,delta,x).
```

The theorem spine proves threshold monotonicity, ambiguity monotonicity,
singleton reduction to ordinary recovery, and observation-refinement
monotonicity. The randomized robust layer repeats the same shape for
randomized decoders and includes deterministic-to-randomized embedding.

Lean source:

```text
formal/lean/OmegaProper/Recovery/Robust.lean
formal/lean/OmegaProper/Recovery/RobustRandomized.lean
```

Representative theorem names:

```text
robustRecoveryAt_mono_threshold
robustRecoveryAt_mono_ambiguity
singleton_ambiguity_reduces_to_recoveryAt
robustRecoveryAt_mono_observation_refinement
robustRandomizedRecoveryAt_mono_threshold
singleton_ambiguity_reduces_to_randomizedRecoveryAt
robustRecoveryAt_implies_robustRandomizedRecoveryAt
```

Strictness witness:

```text
identity channel is exactly recoverable;
flip channel is exactly recoverable;
no single deterministic decoder recovers both robustly.
```

Lean source:

```text
formal/lean/OmegaProper/Recovery/Examples.lean
```

Representative theorem name:

```text
identity_flip_each_recoverable_not_robust
```

### 4.11 Prior-Relative Recovery

A prior-relative scalar can hide localized failure. The prior layer defines:

```text
ExpectedSuccess(mu,profile)
  = sum_x mu(x) * profile(x).
```

Worst-case threshold recovery implies expected threshold recovery under any
prior, but not conversely. The examples include a skewed prior where a constant
observation reaches high expected success while failing worst-case recovery.

Lean source:

```text
formal/lean/OmegaProper/Recovery/Prior.lean
formal/lean/OmegaProper/Recovery/Examples.lean
```

Representative theorem names:

```text
worstCase_threshold_implies_expected_threshold
declaredRecoveryAt_implies_expectedRecoveryAt
recoveryAt_implies_expectedRecoveryAt
skewedPrior_constantObservation_expectedRecoveryAt_99_100
high_expected_not_worstCase_recovery
```

### 4.12 Joint Recovery

Joint target recovery implies marginal target recovery. Recovering `(d1,d2)`
lets us recover `d1` and `d2` by postprocessing the decoded pair:

```text
joint recovery -> first marginal recovery
joint recovery -> second marginal recovery
```

The reverse is not automatic. If both marginal decoders use the same
observation panel, they can be paired into a joint decoder, with the finite
union-bound lower bound:

```text
joint_success >= marginal_success_1 + marginal_success_2 - 1.
```

For exact same-panel marginal decoders, the paired decoder gives exact joint
recovery. But separate observations can each recover a marginal while neither
observation recovers the joint target.

Lean source:

```text
formal/lean/OmegaProper/Recovery/Joint.lean
formal/lean/OmegaProper/Recovery/Examples.lean
```

Representative theorem names:

```text
joint_success_le_first
joint_success_le_second
jointRecoveryAt_implies_firstRecoveryAt
jointRecoveryAt_implies_secondRecoveryAt
pair_success_add_one_ge_marginal_success_sum
marginalRecoveryAt_pair_jointRecoveryAt_unionBound
marginalExactRecovery_pair_jointExactRecovery
firstPairObservation_recovers_first
secondPairObservation_recovers_second
firstPairObservation_not_jointExact
secondPairObservation_not_jointExact
```

### 4.13 Policy-Conditioned Continuation

The policy-continuation layer defines finite rational action kernels:

```text
P(x' | x,a)
```

and induces a Markov kernel from a policy:

```text
pi : X -> A.
```

The hit profile is horizon-indexed:

```text
HitProfile(K,target,start)(n)
  = Pr[target is hit within n steps | start].
```

The formal layer proves nonnegativity, upper bounds by one, target states hit
with probability one, monotonicity in the horizon, and equality of hit profiles
when selected policy rows agree. It also defines robust and policy-family
robust hit predicates over ambiguity sets of action kernels.

Lean source:

```text
formal/lean/OmegaProper/Recovery/PolicyContinuation.lean
formal/lean/OmegaProper/Recovery/Examples.lean
```

Representative theorem names:

```text
inducedKernel_valid
hitWithin_nonneg
hitWithin_le_one
hitWithin_target_eq_one
hitWithin_mono_horizon
selected_action_rows_equal_implies_inducedKernel_prob_equal
inducedKernel_prob_equal_implies_hitWithin_equal
jointShock_individual_robust_not_joint_robust
```

## 5. Canonical Strictness Examples

The paper relies on finite examples that separate tempting but false
identifications.

### High Confidence Is Not Zero Error

The 99/100 binary channel has strong approximate recovery but fails
support-exact recovery because every output remains possible from every source.

### Same Support, Different Recovery

Two full-support channels can agree on positive support while disagreeing on
threshold recovery. Support loses the probability mass that matters for
approximate recovery.

### Randomization Is a Separate Axis

With one observation label and two possible targets, no deterministic decoder
can recover both classes at threshold 1/2. A uniform randomized decoder reaches
1/2. This does not make randomized decoding "better" in every sense; it shows
that decoder class is part of the claim.

### Prior Success Can Hide Worst-Case Failure

A skewed prior can make a bad deterministic decoder look highly successful in
expectation while one source class remains unrecoverable. Expected recovery
does not replace source-indexed recovery.

### Separate Marginals Do Not Give Joint Recovery

One observation can recover the first coordinate and another can recover the
second coordinate, while neither observation recovers the pair. Joint recovery
requires a common panel or a declared coupling condition.

### Robust Recovery Is Not Pointwise Recoverability

Two channels can each be exactly recoverable by different decoders while no
single decoder works across both. Robust recovery is a one-decoder-across-the
ambiguity-set condition.

### Individual Robust Hits Do Not Imply Joint Robust Hit

In the policy-conditioned example, one policy robustly hits target A and
another robustly hits target B, but the available policy family does not
robustly hit the joint target across the ambiguity set. This is the
continuation analogue of the marginal/joint warning.

## 6. What This Paper Claims

This paper claims:

```text
support-exact recovery is the threshold-one endpoint of a source-indexed
recovery profile;

finite recovery depends on the declared target, observation, decoder class,
channel, risk criterion, prior, ambiguity set, and continuation horizon;

deterministic observation refinement preserves recovery ability, while
failure persists under deterministic coarsening;

positive support alone does not determine approximate recovery;

prior-relative success, randomized success, robust success, joint recovery,
and policy-conditioned hit profiles are distinct axes, not notational variants;

the listed finite laws and strictness examples are machine-checked in Lean.
```

## 7. What This Paper Does Not Claim

This paper does not claim:

```text
identity;
agency;
value;
valuerhood;
Omega validation;
empirical validity of any channel;
naturalness of any declared target;
naturalness of any decoder class;
correctness of any prior;
completeness of any ambiguity set;
a moral threshold;
an asymptotic channel capacity theorem;
a replacement for Blackwell comparison, Shannon theory, or robust MDP theory.
```

The formal layer proves facts relative to declared finite structures. The
adapter and empirical layers must justify why a real-world substrate should be
represented by those structures.

## 8. Why the Result Is Useful

The recovery layer is useful because it prevents several common shortcuts.

First, it prevents exact-support overreach. A full-support noisy channel can be
highly reliable without being zero-error. If the theory only has support-exact
recovery, it will classify too much realistic recovery as failure.

Second, it prevents scalar overreach. An expected score can hide localized
failure. A source-indexed profile exposes where the recovery works and where it
does not.

Third, it prevents observation overreach. Coarser observations cannot
magically recover distinctions that a finer observation could not recover under
the same decoder assumptions. Any apparent gain must come from changing the
task, changing the observer, changing the decoder class, or adding semantic
structure not present in the deterministic coarsening.

Fourth, it prevents robustness overreach. Recoverability for each possible
channel does not imply robust recoverability by one decoder across the
ambiguity set.

Fifth, it provides a tractable bridge to finite continuation. A policy can be
audited by a horizon-indexed hit profile before any value function or optimal
control claim is introduced.

For alignment-facing work, this gives a concrete discipline:

```text
do not treat a benchmark, proxy, observation, prior, or abstraction as evidence
for a target unless the target is recoverable from that retained surface under
the declared decoder and uncertainty assumptions.
```

## 9. Open Gaps Before a Submission Draft

The technical spine is strong enough for a paper draft, but several items
remain before this should be treated as submission-ready.

1. The related-work section needs full bibliographic cleanup and sharper
positioning against Blackwell comparison, zero-error communication, robust MDPs,
POMDPs, and task-relative information measures.

2. The Lean theorem spine should be summarized in a compact appendix table
with exact module and theorem names. The present draft includes a source map,
but it is not yet typeset as an appendix.

3. The examples should be diagrammed. The binary channels, one-label randomized
decoder witness, skewed-prior witness, separate-marginal witness, and robust
ambiguity witness are all small enough to display as tables.

4. The paper should include a short proof-sketch section that explains the
main theorem mechanisms without forcing readers to inspect Lean.

5. The Python adapter parity should be turned into a reproducibility appendix:
which validation commands run, which retained artifacts are produced, and which
claims those artifacts do and do not support.

6. The paper needs a tighter title decision. The current title is accurate but
long. Possible alternatives:

```text
Finite Recovery Profiles for Noisy Observation
Recovery Is a Profile, Not a Scalar
Zero-Error Recovery as a Boundary Case
```

## 10. Lean Source Map

Public umbrella:

```text
formal/lean/OmegaProper/Recovery.lean
```

Core modules:

```text
formal/lean/OmegaProper/Recovery/FiniteChannel.lean
formal/lean/OmegaProper/Recovery/Deterministic.lean
formal/lean/OmegaProper/Recovery/ObservationRefinement.lean
formal/lean/OmegaProper/Recovery/CoarseningPermanence.lean
formal/lean/OmegaProper/Recovery/TargetPostprocessing.lean
formal/lean/OmegaProper/Recovery/ConfusionBound.lean
formal/lean/OmegaProper/Recovery/Randomized.lean
formal/lean/OmegaProper/Recovery/RandomizedFamily.lean
formal/lean/OmegaProper/Recovery/Robust.lean
formal/lean/OmegaProper/Recovery/RobustRandomized.lean
formal/lean/OmegaProper/Recovery/Prior.lean
formal/lean/OmegaProper/Recovery/Joint.lean
formal/lean/OmegaProper/Recovery/PolicyContinuation.lean
formal/lean/OmegaProper/Recovery/Examples.lean
```

Compatibility bridge:

```text
formal/lean/OmegaProper/BaselineWitnesses/ExactRecoverySupport.lean
```

Relevant documentation:

```text
docs/research_notes/omega_theory/stochastic_recovery_formalization_v0.md
docs/research_notes/omega_theory/stochastic_recovery_theorem_spine_v0.md
docs/research_notes/omega_theory/recovery_layer_checkpoint_v0.md
docs/research_notes/omega_theory/layer_a_theorem_spine_v0.md
docs/CLAIMS_LEDGER.md
docs/VALIDATION.md
```

## References To Develop

This draft currently uses citation notes rather than a finished bibliography.
The final paper should include at least:

- D. Blackwell, "Comparison of Experiments," 1951.
- D. Blackwell, "Equivalent Comparisons of Experiments," 1953.
  https://doi.org/10.1214/aoms/1177729032
- C. E. Shannon, "The Zero Error Capacity of a Noisy Channel," 1956.
- C. E. Shannon, "A Mathematical Theory of Communication," 1948.
- A. Wald, *Statistical Decision Functions*, 1950.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, 2nd ed.,
  2006.
- M. L. Puterman, *Markov Decision Processes: Discrete Stochastic Dynamic
  Programming*, 1994.
- G. N. Iyengar, "Robust Dynamic Programming," 2005.
- A. Nilim and L. El Ghaoui, "Robust Control of Markov Decision Processes with
  Uncertain Transition Matrices," 2005.
- M. Suilen, T. Badings, E. M. Bovy, D. Parker, and N. Jansen, "Robust Markov
  Decision Processes: A Place Where AI and Formal Methods Meet," 2024.
  https://arxiv.org/abs/2411.11451
- M. T. Bennett, "Is Complexity an Illusion?", 2024.
  https://arxiv.org/abs/2404.07227
- M. Finzi, S. Qiu, Y. Jiang, P. Izmailov, J. Z. Kolter, and A. G. Wilson,
  "From Entropy to Epiplexity: Rethinking Information for Computationally
  Bounded Intelligence," 2026.
  https://arxiv.org/abs/2601.03220
