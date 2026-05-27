# Gauge-Coherent Shadow Formalism v0

Status: theory note / pivot proposal  
Scope: Omega primitive stack, boundary non-privileging, and the next RFS-MB0 measurement object  
Claim boundary: not a validation result, not agent detection, not identity detection, not value detection

## 0. One-sentence version

A **gauge-coherent shadow** is a control-resistant pattern of reachable-future deformation that appears across multiple non-privileged ways of viewing a transition system, where the pattern seen in one view helps predict the pattern seen in other views.

In plainer terms:

```text
We do not first find the true boundary of the agent.
We look for the coherent shadow an agency-like process casts on the field of possible futures.
```

This note uses **view** as the public-facing term. The word **gauge** is the technical analogy: a view is a useful way of describing the system, not an ontologically privileged boundary.

## 1. Why this note exists

The current RFS-MB0 branch has repeatedly encountered the same problem from different angles:

```text
agent
identity
valuer
self
bounded object
Markov blanket
```

are exactly the classes the theory wants to derive, not categories that should be installed as primitives.

The frontier-transform Phase B result sharpened the measurement problem. Raw recurrence appeared in the design set, but the strongest recurrence rows were matched by controls. That means single-view or marginal recurrence is too cheap to carry the theory.

The boundary non-privileging argument sharpens the conceptual problem. A useful boundary can support prediction and action without being evidence for an ontologically final self/world division. This means Omega should not search for one privileged boundary and then treat it as the agent.

The resulting pivot is:

```text
from:
  detect the bounded identity directly

to:
  measure future-field deformation across many non-privileged views
  and test whether those deformations cohere better than controls
```

This is the **shadow** approach.

## 2. Project discipline: principled, parsimonious, predictive

Every part of this formalism should pass the 3P constraint.

### 2.1 Principled

The object must follow from the primitive stack and previous failures, not from a desire to rescue the theory.

Gauge-coherent shadow is motivated by:

```text
1. boundary and identity should not be primitives;
2. one privileged boundary is not available;
3. raw recurrence is control-equivalent;
4. future deformation remains the correct measurable target.
```

### 2.2 Parsimonious

Shadow is not a new primitive.

It is a derived object built from:

```text
distinction
relation
asymmetry
reachable futures
matched controls
cross-view prediction
```

The point is to reduce the need for premature labels such as agent, identity, valuer, and self.

### 2.3 Predictive

A shadow should not merely look interesting in one view.

It must predict something risky:

```text
Given deformation in some views,
can we predict deformation in held-out views
better than matched controls?
```

If not, the object is not yet scientifically useful.

## 3. Primitive floor

The current primitive floor remains:

```text
S = (X, ->)
```

where:

```text
X:
  finite distinction space

->:
  neutral transition relation
```

Plainly:

```text
distinction:
  configurations can differ

relation:
  configurations can transform into other configurations

asymmetry:
  transformations have non-equivalent future consequences
```

The older two-term compression is still useful:

```text
gradient:
  directed difference induced by distinction

filter:
  asymmetric selection or persistence under relation
```

In this note, gradient and filter are not extra primitives. They are readings of distinction, relation, and asymmetry.

## 4. Derived objects from the primitives

From the primitive substrate, define reachable futures in the usual way:

```text
Reach_H(x) = { y in X : y is reachable from x in <= H steps }
```

A transition `x -> y` is future-asymmetric when it changes the reachable future structure:

```text
Reach_H(x) != Reach_H(y)
```

A **future field** is the horizon-indexed pattern of reachable futures:

```text
Reach_0(x), Reach_1(x), Reach_2(x), ..., Reach_H(x)
```

A **future-field deformation** is a change in that pattern across transitions, horizons, perturbations, or views.

This gives the first important compression:

```text
Omega should not begin with value labels.
Omega should begin with future-field deformation.
```

## 5. Views instead of true boundaries

A **view** is a declared way of looking at the same transition substrate.

A view may include:

```text
a projection or probe;
a coarse-graining;
a boundary convention;
a scale;
a horizon-window choice;
a perturbation relation;
a metric family;
a matched-control bundle.
```

Notation:

```text
lambda in Lambda
```

where `Lambda` is a predeclared family of views.

A view can be useful without being true in an ontological sense. Different views may reveal different aspects of the same future-field structure. The question is not which view is the true one. The question is whether the deformations seen through different views cohere.

For public-facing language:

```text
view:
  a lens for measuring future structure

gauge:
  technical analogy for a non-privileged but useful description frame
```

## 6. Future profiles under a view

Given a view `lambda`, let:

```text
pi_lambda
```

be the projection, probe, or coarse-graining associated with that view.

The visible future profile at horizon `H` is:

```text
F_lambda(x, H) = pi_lambda(Reach_H(x))
```

Plainly:

```text
F_lambda(x, H):
  what the reachable futures from x look like through view lambda
```

For a horizon window `Ha -> Hb`, define a deformation profile:

```text
D_lambda(x; Ha -> Hb)
```

as the declared measurement of how the visible future profile changes from `Ha` to `Hb`.

Examples:

```text
frontier growth
support turnover
new or lost signatures
transition-matrix change
bottlenecking
window stability
recovery after perturbation
compatibility or capture effects
```

The exact components of `D_lambda` must be declared before scoring.

## 7. Control-relative residual deformation

A raw deformation is not enough.

Phase B showed that raw or marginal recurrence can be generic. The correct object must be control-relative.

Let `N_lambda` be the matched-control bundle for view `lambda`.

Define the residual deformation:

```text
R_lambda(x; Ha -> Hb) = residual(D_lambda observed relative to N_lambda)
```

The residual may be represented as:

```text
signed difference from control mean;
signed z-score;
control percentile;
rank excess;
component pass/fail relative to controls;
or a preregistered vector combining these.
```

The important point is:

```text
R_lambda is what remains after the matched controls have had their say.
```

A shadow should never be based on raw deformation alone.

## 8. Shadow

For a predeclared family of views `Lambda`, the shadow of a substrate region or start state is the bundle of residual deformations:

```text
Shadow_Lambda(S, x) = { R_lambda(x) : lambda in Lambda }
```

A shadow is observable. It is not yet an agent.

Many things can cast shadows:

```text
generic finite-frontier phase behavior;
saturation;
probe collision;
frontier-size effects;
start artifacts;
fakeout systems;
true agency-like future shaping.
```

Therefore the key question is not whether a shadow exists. The key question is whether it is coherent across views in a way controls do not match.

## 9. Cross-view coherence

If a latent future-shaping structure is real, it should not require exactly one sacred view. It may look different under different views, but those differences should be structured.

For two views `lambda` and `mu`, define a declared translation rule:

```text
T_{lambda -> mu}
```

This rule says how a residual deformation seen in view `lambda` should appear in view `mu`.

Examples:

```text
coarse-graining translation:
  aggregate fine signatures into coarser signatures

refinement translation:
  map coarse signatures into compatible fine-signature families

horizon translation:
  predict a longer-window profile from shorter-window profiles

scale translation:
  relate component-level deformation to collective-level deformation

boundary translation:
  map an inside/interface/outside convention to a neighboring convention
```

Pairwise coherence can then be written as:

```text
Coh(lambda, mu; x) = similarity(T_{lambda -> mu}(R_lambda(x)), R_mu(x))
```

Plainly:

```text
Do the residuals seen in one view help predict the residuals seen in another view?
```

The translation rules must be declared before the test or learned only on training views and evaluated on held-out views.

## 10. Gauge-coherent shadow

A **gauge-coherent shadow** exists when the residual deformation bundle is more mutually predictive across views than matched-control bundles.

Compact definition:

```text
GCS_Lambda(S, x) exists when:

  { R_lambda(x) : lambda in Lambda }

is more coherent under declared translations T_{lambda -> mu}
than the corresponding residual bundles from matched controls.
```

Operational requirements:

```text
1. residual deformation is present above matched controls;
2. multiple views participate;
3. no single privileged boundary or probe is required;
4. cross-view prediction beats shuffled-view and matched-control baselines;
5. small changes of view do not immediately destroy the result;
6. mechanism perturbations change the shadow in expected ways;
7. multiplicity and probe-collision risks are reported.
```

A scalar score may be useful:

```text
GCS_score =
  cross_view_prediction_score
  - matched_control_prediction_score
  - frame_fragility_penalty
  - probe_collision_penalty
  - multiplicity_penalty
```

But the score is not the object. The object is the residual deformation bundle and its cross-view predictive structure.

## 11. Action, agency, and cost

Agency requires action.

In this framework, action is not merely movement. It is future-shaping selection among possible relations.

A minimal action channel is:

```text
A:
  a channel through which alternative transitions or policies can be selected,
  biased, inhibited, maintained, or amplified
```

A process is action-relevant when interventions on this channel change reachable-future structure:

```text
intervene on A
  -> reachable futures change
```

An **agent-shadow** is therefore stricter than a gauge-coherent shadow.

```text
agent-shadow:
  a gauge-coherent shadow whose residual deformation is action-relevant
```

More explicitly:

```text
An agent-shadow is present when:
  1. a gauge-coherent shadow exists;
  2. the shadow is tied to an action channel;
  3. interventions on that channel change which futures remain reachable,
     recoverable, compatible, or closed;
  4. the effect is not matched by controls.
```

This captures the working intuition:

```text
agency = costly pursuit of future-shaping asymmetry in distinctions
```

Cost should be treated carefully.

In real physical systems, maintaining and exploiting asymmetry has thermodynamic and informational cost. In toy substrates, we should not install cost as a primitive resource coordinate too early. Instead, use cost-like diagnostics:

```text
probability steering needed to produce the structure;
extra constraint maintenance;
path length or action burden;
recovery burden after perturbation;
information required to track or stabilize the pattern;
control effort required to preserve the deformation;
dissipation proxy where physically meaningful.
```

Cost is therefore downstream of action and asymmetry:

```text
asymmetry is not free;
action selects or maintains asymmetry;
cost measures the burden of doing so under the substrate's constraints.
```

## 12. Identity and boundedness after the pivot

This formalism does not delete identity or boundedness. It demotes them.

Old order:

```text
find identity / boundary first
then measure its futures
```

New order:

```text
measure future-field shadows first
then ask which boundary views best compress, predict, or explain them
```

Definitions become frame-relative:

```text
identity:
  a useful continuity convention inside one or more views

boundedness:
  a useful compression or prediction frame for a shadow

Markov blanket:
  one possible boundary view, not an ontologically privileged edge

agent:
  not a boundary itself, but a latent future-shaping process inferred from a coherent, action-relevant shadow
```

This is a stricter version of the dark-matter intuition:

```text
we may not see the agent boundary directly;
we infer agency-like structure from coherent deformation of the future field.
```

The better public term is **shadow**, not dark matter, because the deformation itself is visible. What remains uncertain is the privileged boundary of the source.

## 13. Multiscale and composability

Because views can vary by scale, this formalism naturally supports multiscale agency without assuming it as a primitive.

A scale view may track:

```text
components;
local neighborhoods;
meso-scale clusters;
whole-system coarse grains;
collective processes;
interacting systems.
```

A composable agency-like process should show structured cross-scale behavior:

```text
component-level deformation predicts meso-level deformation;
meso-level perturbation changes component recovery;
collective collapse narrows local futures;
local damage propagates upward in predictable ways;
recovery at one scale reopens futures at another scale.
```

This is where fractal or nested agency can become empirical rather than rhetorical.

Do not assert:

```text
agency is fractal
```

Test:

```text
cross-scale shadow coherence exceeds controls
```

## 14. Minimal empirical audit shape

A minimal RFS-MB0G audit should be small and preregistered.

### 14.1 Inputs

```text
S:
  neutral transition substrate

Lambda:
  small declared view family
```

Possible first views:

```text
constraint-profile view
constraint-violation/local-tuple view
transition-role view
frontier-size/support view
perturbation-response view
recovery-basin view, if available
```

### 14.2 Per-view computation

For each view:

```text
F_lambda:
  visible future profile

D_lambda:
  deformation profile

R_lambda:
  control-relative residual deformation
```

### 14.3 Cross-view test

Use a train/test split over views:

```text
train views:
  lambda_1, lambda_2, lambda_3

held-out views:
  lambda_4, lambda_5
```

Fit or compute the shadow structure on train views only.

Then ask:

```text
Can train-view residuals predict held-out-view residuals
better than matched controls?
```

### 14.4 Required controls

At minimum:

```text
shuffled view-pair control;
frontier-size matched control;
probe-marginal control or honest placeholder exclusion;
horizon-order control;
start-shuffled control;
matched fakeout systems;
neutral generated systems;
saturation-timing audit;
probe-collision audit;
mechanism perturbation controls where implementable.
```

### 14.5 Pass condition

A strong pass requires:

```text
held-out view prediction excess > 0;
multiple view families contributing;
no single identity-like view driving the result;
probe-collision audit clean enough;
frontier-size and saturation controls not sufficient;
mechanism perturbation profile interpretable;
holdout untouched until definitions are frozen.
```

## 15. Suggested decision classes

```text
gauge_coherent_shadow_candidate:
  cross-view residual prediction beats controls under preregistered views

agent_shadow_candidate:
  gauge-coherent shadow plus action-channel intervention relevance

single_view_artifact:
  strong residual in one view but no cross-view coherence

probe_collision_shadow:
  apparent coherence explained by low-resolution projection collision

generic_phase_shadow:
  cross-view pattern matched by finite-frontier or saturation controls

mechanism_dependent_shadow:
  baseline shadow present and expected mechanism perturbation degrades or changes it

roughness_brittle_shadow:
  tiny roughness perturbation destroys the pattern without interpretable mechanism profile

frame_fragile_shadow:
  neighboring view choices do not preserve or predict the pattern

no_resolved_shadow:
  no residual bundle above controls
```

None of these classes imply Omega detection by themselves.

## 16. Claim boundary

Allowed claims from this formalism:

```text
We define a boundary-nonprivileging object for future-field deformation.

We treat boundaries as useful views rather than ontological edges.

We test whether residual deformations cohere across views better than controls.

We define agency only after action relevance is shown.

We keep identity, boundedness, and valuerhood as derived, frame-relative concepts.
```

Not allowed:

```text
Omega has been detected.

An agent has been detected.

A valuer has been detected.

The true boundary has been found.

Identity has been solved.

A single frontier-transform recurrence is evidence of agency.

A gauge-coherent shadow is automatically good, valuable, conscious, or ethical.
```

## 17. Relation to the current branch

The current frontier-transform work remains useful.

It already measures parts of `D_lambda`:

```text
frontier growth;
support turnover;
transition-matrix structure;
bottlenecking;
window stability.
```

Phase B taught that marginal recurrence is too generic.

The gauge-coherent shadow pivot says:

```text
Do not ask one metric or one view to carry the object.
Ask whether residual deformation predicts across views.
```

This makes the next measurement object stricter, not looser.

## 18. Bottom line

The clean object is:

```text
Gauge-coherent shadow:
  a control-resistant, cross-view-predictive deformation of reachable futures.
```

The stricter agency object is:

```text
Agent-shadow:
  a gauge-coherent shadow tied to costly action-relevant shaping of future distinctions.
```

In compressed form:

```text
distinction + relation + asymmetry
  -> reachable future field
  -> control-relative deformation
  -> shadow
  -> gauge-coherent shadow
  -> action-relevant agent-shadow
```

This preserves the primitive floor while avoiding premature commitment to a privileged boundary.
