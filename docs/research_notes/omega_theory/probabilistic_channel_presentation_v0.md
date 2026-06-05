# Probabilistic Channel Presentation v0

Status: formal presentation draft
Role: probabilistic enrichment of the finite channel presentation
Scope: finite stochastic channel recovery under declared carriers, distinctions,
target observations, decoders, priors, thresholds, and formal-consumption
policies

Lean status:

```text
formal/lean/OmegaCore/Presentations/ProbabilisticChannel.lean
formal/lean/OmegaCore/Presentations/ProbabilisticChannelPolicy.lean

Checked:
  exact support recovery implies perfect probabilistic recovery;
  perfect probabilistic recovery under a full-support prior implies exact
  support recovery;
  perfect probabilistic recovery under a non-full-support prior need not imply
  exact support recovery;
  high probabilistic recovery need not imply exact support recovery;
  composite decoder error over a finite cascade is bounded by first-stage plus
  second-stage decoder error over the same path ensemble;
  fixed-declared and Bayes-best target policies can diverge in a finite
  two-candidate example.

Pending:
  normalized or constant-row-total cascade variants, if needed.
```

Empirical theorem-transfer audit:

```text
docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_channel_theorem_transfer_audit_result.md
results/stochastic_distinction_channel/20260604_stochastic_channel_theorem_transfer_audit_v0/
```

Status:

```text
support_and_probabilistic_transfer_ready
```

The audit converts retained fixed-policy stochastic-channel outputs into exact
natural-weight path ensembles and checks the finite cascade error-bound
conditions over a shared denominator. It also keeps Bayes-best policy rows
diagnostic rather than using them as declared composition proofs.

Thresholded probabilistic non-erasure package:

```text
docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_thresholded_prob_non_erasure_result.md
results/stochastic_distinction_channel/20260604_thresholded_prob_non_erasure_v0/
```

Status:

```text
thresholded_prob_non_erasure_measurement_ready
```

This package supplies the empirical target for a future Lean definition:

```text
ProbNonErasing(K, pi, Req, threshold, target_policy)
```

and for the monotonicity theorem under requirement-set weakening.

## 0. Purpose

The Omega Primitive Calculus root is support-level:

```text
A : C -> DistTrans
```

where recoverability is binary:

```text
A_r(d,e)
```

meaning target distinction `e` recovers source distinction `d` through
relational unfolding `r`.

The finite channel presentation already gives an exact support-level
interpretation:

```text
source distinction D
target distinction E
channel support K(y | x) > 0
decoder dec : E.Label -> D.Label
```

This note adds a probabilistic measurement layer:

```text
decoder success probability
decoder error probability
Bayes-best recovery
fixed-declared target recovery
thresholded recovery
composition error bounds
```

The purpose is to handle stochastic channels without collapsing
high-probability recovery into exact support recovery.

## 1. Core Separation

There are two different recovery notions.

### 1.1 Exact Support Recovery

Exact support recovery asks:

```text
For every source x and every target y with K(y|x) > 0,
does the target observation decode the source distinction?
```

This is strict. It supports root theorem transfer.

### 1.2 Probabilistic Recovery

Probabilistic recovery asks:

```text
Under a declared prior pi and decoder dec,
with what probability does dec(E(Y)) equal D(X)?
```

This is graded. It supports empirical measurement and thresholded claims, but
not automatic root theorem transfer unless an appropriate theorem is proved.

## 2. Finite Stochastic Channel

A finite stochastic channel consists of finite carriers:

```text
X:
  source carrier

Y:
  target carrier
```

and a row-stochastic kernel:

```text
K : X -> Y -> [0,1]
```

with:

```text
for all x:
  sum_y K(y | x) = 1
```

The support relation is:

```text
Supp_K(x,y) iff K(y | x) > 0
```

The support relation is what connects the probabilistic channel back to the
support-level root calculus.

## 3. Distinctions As Labelings

A source distinction is a labeling:

```text
D : X -> L_D
```

A target distinction is a labeling:

```text
E : Y -> L_E
```

The labels define partitions of the source and target carriers.

A target distinction `E` refines or is sufficient for a source distinction `D`
across a channel only relative to a decoder.

## 4. Decoders

A decoder from target distinction `E` to source distinction `D` is:

```text
dec : L_E -> L_D
```

A decoder is not evidence by itself. It must be evaluated against a channel,
prior, and source distinction.

For theorem-transfer claims that depend on instrument provenance, the finite
channel layer now distinguishes existence-style recovery from registered
decoder recovery. A post-hoc decoder may show channel capacity, but registered
or declared registered evidence is needed when the claim is about a supplied
instrument.

Required decoder policies:

```text
fixed-declared decoder:
  decoder associated with declared source-target distinction pair

Bayes-optimal decoder:
  decoder minimizing error under declared prior and target observation

exact decoder:
  decoder with zero error under support-level recovery
```

## 5. Exact Support Recovery

Given:

```text
K : X -> Y
D : X -> L_D
E : Y -> L_E
dec : L_E -> L_D
```

`E` exactly support-recovers `D` through `K` using `dec` when:

```text
for all x in X and y in Y:
  if K(y | x) > 0, then dec(E(y)) = D(x)
```

Write:

```text
ExactRec_K(D,E,dec)
```

There exists exact support recovery when:

```text
ExactRec_K(D,E) iff exists dec such that ExactRec_K(D,E,dec)
```

This is the stochastic-channel version of root support recovery.

## 6. Probabilistic Recovery

Given a prior:

```text
pi : X -> [0,1]
```

with:

```text
sum_x pi(x) = 1
```

the decoder success probability is:

```text
Success(K,pi,D,E,dec)
=
sum_x pi(x) * sum_y K(y|x) * 1[dec(E(y)) = D(x)]
```

The decoder error probability is:

```text
Error(K,pi,D,E,dec)
=
1 - Success(K,pi,D,E,dec)
```

For a decoder policy `P`, define:

```text
Success_P(K,pi,D,E)
Error_P(K,pi,D,E)
```

according to the decoder selected by policy `P`.

## 7. Fixed-Declared Versus Bayes-Best Target Policy

Two target-selection policies must be kept separate.

### 7.1 Fixed-Declared Target Policy

The fixed-declared policy evaluates a predeclared source-target distinction
pair:

```text
D_A      -> E_A
D_B      -> E_B
D_joint  -> E_joint
D_parity -> E_parity
```

This policy preserves provenance. It asks:

```text
Does the declared target observation recover the declared source distinction?
```

### 7.2 Bayes-Best Target Policy

The Bayes-best policy searches over available target distinctions and chooses
the target/decoder pair with maximal success under the declared prior.

This policy is diagnostically useful, but it can obscure which target
observation is doing the work.

### 7.3 Policy Relation

If the fixed-declared target is included among the Bayes-best candidate targets,
then:

```text
Success_BayesBest(K,pi,D) >= Success_FixedDeclared(K,pi,D)
```

Equality is not guaranteed. Divergence between the two policies is informative
and must be reported, not hidden.

## 8. Exact Support Recovery Implies Perfect Probabilistic Recovery

### Proposition

If `E` exactly support-recovers `D` through `K` using decoder `dec`, then for
every prior `pi`:

```text
Success(K,pi,D,E,dec) = 1
```

### Reason

Every positive-probability channel transition from `x` to `y` decodes correctly
by exact support recovery. Therefore every term with nonzero probability in the
success sum is correct.

## 9. Perfect Probabilistic Recovery Does Not Always Imply Exact Support Recovery

If the prior assigns zero probability to some source states, then perfect
success under that prior does not require correct decoding on those zero-prior
states.

Thus:

```text
Success(K,pi,D,E,dec) = 1
```

implies exact support recovery only over the prior-supported source states.

A stronger converse requires a full-support prior:

```text
for all x, pi(x) > 0
```

The Lean skeleton checks the corresponding finite natural-weight theorem:
under a full-support prior, perfect probabilistic recovery forces exact support
recovery.

## 10. High Probabilistic Recovery Does Not Imply Exact Support Recovery

High success probability can coexist with support-level ambiguity.

Example:

```text
X = {0,1}
Y = {0,1}
D(x) = x
E(y) = y

K(0|0) = 1
K(1|1) = 0.99
K(0|1) = 0.01
```

Using the identity decoder:

```text
dec(E(y)) = y
```

success under uniform prior is high:

```text
Success = 0.995
```

but exact support recovery fails because `x=1` can produce `y=0`, which decodes
as `0`.

Therefore:

```text
high probability recovery != exact support recovery
```

This distinction is central.

## 11. Thresholded Recovery

A thresholded probabilistic recovery claim has the form:

```text
Success(K,pi,D,E,dec) >= theta
```

or:

```text
Error(K,pi,D,E,dec) <= epsilon
```

Thresholds must be declared before interpretation.

Suggested thresholds:

```text
exact:
  Error = 0

high_recovery:
  Success >= 0.95

moderate_recovery:
  Success >= 0.75

chance_baseline:
  Success exceeds best constant decoder under same prior
```

Thresholded recovery is not automatically a root `DistTrans` relation unless
closure and composition conditions are separately proved.

## 12. Non-Erasure Under Probabilistic Recovery

Given a declared distinction requirement set:

```text
Req = {D_1, ..., D_n}
```

and threshold policy `theta`, a channel is probabilistically non-erasing for
`Req` when each required distinction is recovered above threshold under the
declared policy:

```text
for every D_i in Req:
  exists target E_i and decoder dec_i such that
  Success(K,pi,D_i,E_i,dec_i) >= theta_i
```

This is claim-relative and presentation-relative.

## 13. Composition Of Probabilistic Recovery

Support-level composition is exact:

```text
ExactRec_K(D,E)
and
ExactRec_L(E,F)
imply
ExactRec_(L o K)(D,F)
```

For probabilistic recovery, composition requires an error-bound theorem.

Suppose:

```text
D recovered from E through K with error <= epsilon1
E recovered from F through L with error <= epsilon2
```

where:

```text
K : X -> Y
L : Y -> Z
pi : X -> [0,1]
K_* pi : Y -> [0,1] is the pushed-forward prior on Y
dec1 : L_E -> L_D
dec2 : L_F -> L_E
dec_comp = dec1 o dec2
```

Then the composed decoder recovers `D` from `F` through `L o K` with error
bounded by:

```text
epsilon1 + epsilon2
```

under the usual joint process:

```text
X ~ pi
Y ~ K(.|X)
Z ~ L(.|Y)
```

No independence assumption is needed beyond the declared channel cascade. The
bound is a union-bound statement:

```text
composite failure subset
  {dec1(E(Y)) != D(X)} union {dec2(F(Z)) != E(Y)}
```

The checked finite natural-weight theorem works at cascade path-ensemble level.
It declares:

```text
source prior pi on X
decoder dec1 : E.Label -> D.Label
decoder dec2 : F.Label -> E.Label
composed decoder dec1 o dec2
channel composition L o K
first-stage and second-stage decoder-error masses over the same path ensemble
```

The empirical arm should report measured composed success and should not replace
this cascade-level theorem with independently normalized stage-error claims
unless additional normalization assumptions are supplied.

The Lean presentation also checks that the cascade path-ensemble total mass and
composite error mass agree with the corresponding `chanComp` total/error masses.
This ties the path-level proof back to the composed natural-weight channel.

## 14. Support Projection For Root Theorem Transfer

Every stochastic channel presentation should emit a support projection:

```text
Supp_K(x,y) iff K(y | x) > 0
```

Exact support recovery over `Supp_K` can instantiate the root support calculus.

Probabilistic recovery is an enrichment layered on top.

Therefore theorem transfer splits:

```text
root support theorems:
  transfer through exact support recovery

probabilistic threshold claims:
  require probabilistic presentation theorems

composition bounds:
  require probabilistic composition assumptions
```

## 15. What This Presentation Can Say

This presentation supports statements of the following form:

```text
Declared distinctions are recovered exactly over channel support.

Declared distinctions are recovered probabilistically above threshold under a
specified prior, decoder, and target observation.

High-probability recovery can be distinguished from exact support recovery.

Bayes-best and fixed-declared target policies can diverge and must be reported.

Channel composition requires explicit probabilistic error accounting.
```

It does not by itself promote stochastic channel recovery into a theory-wide
validation or semantic detection claim. Such claims require additional
presentations, adapters, and evidence.

## 16. Formal-Arm Next Theorem Targets

### Target 1: Exact Implies Probabilistic

Prove:

```text
Exact support recovery => Success = 1
```

Checked in Lean as:

```text
exactSupport_implies_perfectProb
exactSupport_implies_probAtLeast_100
```

### Target 2: High Probability Does Not Imply Exact Support

Provide a finite counterexample.

### Target 3: Zero-Prior Caveat

Show that `Success = 1` under a non-full-support prior does not imply exact
support recovery.

Checked in Lean as:

```text
perfectProb_not_exact_without_full_prior
```

### Target 4: Full-Support Converse

Show that `Success = 1` under a full-support prior implies exact support
recovery.

Checked in Lean as:

```text
perfectProb_fullPrior_implies_exactSupport
```

### Target 5: Fixed-Declared Versus Bayes-Best Policy Separation

Show that Bayes-best success can exceed fixed-declared success.

Checked in Lean as:

```text
bayes_best_can_exceed_fixed_declared
bayes_best_is_alternate_in_two_candidate_example
```

### Target 6: Composition Error Bound

Prove a finite error-bound theorem for composed channels under declared decoder
composition assumptions.

Checked in Lean as:

```text
cascade_composite_error_le_stage_errors
cascade_error_bound_same_denominator
cascadeTotalMass_eq_totalMass_chanComp
cascadeCompositeErrorMass_eq_errorMass_chanComp
```

## 17. Empirical-Arm Contract

The empirical arm should emit:

```text
channel_matrix.csv
support_relation.csv
distinction_manifest.csv
target_policy_manifest.csv
decoder_manifest.csv
source_prior_manifest.csv
recoverability_by_distinction.csv
support_vs_probability_summary.csv
declared_target_policy_summary.csv
non_erasure_by_channel.csv
composition_recoverability_check.csv
formal_channel_consumption_bundle.json
```

Every probabilistic recovery row must include:

```text
channel_id
source_distinction_id
target_distinction_id
target_policy
decoder_id
prior_id
success_probability
error_probability
exact_support_recoverable
threshold_id
passes_threshold
```

No recovery claim is admissible without a declared:

```text
source distinction
target observation
decoder
prior
threshold
```

## 18. Relation To No-Self-Evidencing

This presentation does not treat a distinction, partition, or boundary as
self-evidenced.

All recovery claims are conditional on declared modeling choices:

```text
source distinction
target observation
channel
decoder
prior
threshold
```

The result of a decoder does not prove the ontological privilege of the
distinction. It only measures recovery under the declared presentation.

## 19. Summary

Compact distinction:

```text
exact support recovery:
  all possible channel outputs decode correctly

probabilistic recovery:
  channel outputs decode correctly with high probability under a prior

Bayes-best:
  diagnostic best available target/decoder policy

fixed-declared:
  provenance-preserving declared target/decoder policy
```

Core principle:

```text
Probabilistic recovery enriches the root calculus.
It does not replace exact support recovery.
```
