# Horizon Transport and Aligned Amplification

Status: theory / instrument reorientation note after H128 response-surface scaleup  
Scope: RFS-MB0 horizon-transport branch  
Claim boundary: not Omega detection, not agent detection, not valuer detection, not identity detection, not candidate promotion

## 0. One-sentence update

The current live empirical object is **matched-marginal-separated horizon transport** with a horizon-dependent response surface: short horizons remain stable under nonlethal perturbation, while middle and deep horizons show **aligned amplification** rather than collapse, weakening, rerouting, or reopening.

In compact form:

```text
horizon transport persists above matched marginal nulls;
perturbation changes the shape of futures;
the first nonstable response moves earlier as perturbation strength increases;
through H=128, the observed nonstable response is aligned amplification.
```

This earns a theory/instrument update, not a validation claim.

## 1. Result grounding

The H128 response-surface scaleup completed on regenerated design-set inputs:

```text
jobs_completed: 11520 / 11520
errors: 0
matrix_count: 660
null_replicates: 15
matched_marginal_detector_null_separation: passed
synthetic_fixture_contract: 8 / 8
terminal_saturation_flagged_rows: 0 / 660
```

Required horizon pairs were emitted through H=128:

```text
0->1
1->2
2->4
4->8
8->16
16->24
24->32
32->48
48->64
64->96
96->128
```

The empirical response classes in the full run were:

```text
transport_stable: 235
transport_amplified_aligned: 381
```

No empirical rows were classified as:

```text
transport_weakened
transport_rerouted
transport_reopens
transport_collapses
transport_control_equivalent
```

The threshold table showed a consistent horizon response surface. For asymmetric edge flips, the first amplified horizon moved earlier as perturbation strength rose:

```text
p0.006 -> 16->24
p0.008 through p0.020 -> 8->16
p0.030 -> 4->8
```

For small edge resampling, the same broad trend appeared with some probe/flow dependence:

```text
p0.006 -> mixed: none or 8->16
p0.008 -> mixed: 8->16 or 16->24
p0.010 through p0.015 -> 8->16
p0.020 -> mixed: 4->8 or 8->16
p0.030 -> 4->8
```

The result note retains the proper caveat: no holdout scoring, no graph-channel causality, no candidate promotion, and no Omega / agency / value claim.

## 2. Why this changes the live empirical branch

Earlier RFS-MB0 work moved through endpoint support/distribution probes, frontier-transform syndromes, static cofrontier/coflow spectral matrices, and high-loading item/channel tests.

Those branches were useful but limited:

```text
endpoint signatures:
  too collision-prone or too weak

static cofrontier/coflow spectra:
  mechanically visible but control-sensitive and too diffuse

high-loading item/channel targeting:
  export and mapping worked, but ablation was random-equivalent
```

The horizon-transport branch repaired two core problems:

```text
1. object mismatch:
   use directional horizon-to-horizon transport rather than static co-occurrence;

2. control philosophy drift:
   separate detector nulls from candidate perturbation-response profiles.
```

The H128 result is the first run where the branch simultaneously shows:

```text
matched marginal detector-null separation;
extended horizon coverage;
expanded response fixtures passing;
no terminal saturation through H=128;
a structured response threshold across horizon and perturbation strength.
```

Therefore the live empirical object should now be stated as:

```text
matched-marginal-separated horizon transport with horizon-dependent aligned amplification under nonlethal perturbation
```

not merely:

```text
frontier-transform recurrence
```

or:

```text
static spectral geometry
```

## 3. The new response class: transport_amplified_aligned

The previous response bucket `transport_control_equivalent` was too broad. The H128 run now distinguishes true control equivalence from aligned mass-growth response.

Provisional definition:

```text
transport_amplified_aligned:
  baseline-to-perturbed transport subspace alignment remains high;
  transport / spectral mass grows substantially;
  matched marginal detector nulls still separate;
  no collapse is detected;
  no weakening is detected;
  no low-alignment rerouting is detected;
  no entropy reopening is detected.
```

The class means:

```text
perturbation increased the transport geometry while preserving its orientation
```

not:

```text
the detector failed
```

and not:

```text
the system became more Omega-like
```

This distinction is important. Perturbation does not necessarily destroy futures. It can alter, amplify, concentrate, reroute, weaken, reopen, or collapse the transport geometry.

## 4. Horizon as a response coordinate

The H128 result suggests horizon is not merely metadata. Horizon behaves like a response coordinate.

The live pattern is:

```text
short horizons:
  stable

middle/deep horizons:
  amplified-aligned

higher perturbation strength:
  first amplified horizon shifts earlier

extended horizons through H=128:
  still interpretable in this run;
  no terminal saturation flags emitted
```

This makes the response surface a central object:

```text
ResponseClass = f(horizon_pair, perturbation_family, perturbation_strength, probe, flow_mode)
```

A useful next theory quantity is:

```text
H_amp(p, family, probe, flow)
```

where `H_amp` is the first horizon pair at which the response becomes amplified-aligned.

This is not yet a theory of agency. It is a theory of how future-transport geometry responds to nonlethal perturbation.

## 5. Control philosophy: detector nulls versus response profiles

The control reorientation remains load-bearing.

```text
Null controls test the detector.
Perturbations test the candidate response profile.
Destructive ablation maps viability boundaries; it is not ordinary negative evidence.
```

For this branch:

```text
detector-null controls:
  context/horizon shuffles;
  row marginal matched transport nulls;
  column marginal matched transport nulls;
  row-column marginal matched transport nulls;
  marginal residual fraction;
  synthetic marginal fakeout fixtures.

candidate perturbation-response probes:
  small edge resampling;
  asymmetric edge flipping;
  graded nonlethal strength ladders;
  response class by horizon pair.
```

Do not collapse these into one pass/fail claim.

A structure-destroying detector null may block detector claims. A perturbation response may reveal how the future field deforms. These are different epistemic roles.

## 6. Relationship to the hierarchical concept geometry paper

The hierarchical concept geometry paper was useful because it showed that pairwise relational statistics can produce coarse-to-fine spectral geometry. In that setting, the latent object is a known semantic hierarchy and the relation is word co-occurrence.

The Omega analogue is different.

```text
language case:
  known semantic hierarchy;
  static co-occurrence relation;
  spectrum recovers coarse-to-fine tree structure.

Omega horizon case:
  unknown future-field object;
  directional horizon transport;
  singular subspaces may reveal how future structures become later future structures.
```

The lesson is not that static co-occurrence is enough. The lesson is that the right relational matrix can expose latent geometry.

For Omega, the better relational matrix appears to be directional horizon transport:

```text
T_{H_a -> H_b}
```

rather than a static cofrontier/coflow co-occurrence matrix.

The H128 result supports that reorientation: horizon-transport matrices stayed interpretable and matched-marginal-separated through extended horizons, while the response surface varied systematically with horizon depth.

## 7. Relationship to X-Token

The X-Token paper was useful methodologically, but it should not yet be imported into the empirical runner.

Its relevant lesson is:

```text
when two decompositions carve the same underlying object differently,
build explicit projection/alignment machinery and audit coverage before choosing the objective.
```

That suggests a future Omega branch:

```text
projection-guided gauge alignment
```

where projection maps relate horizon, probe, scale, or boundary views.

But this should remain future work because:

```text
1. the current live object is horizon transport itself;
2. projection maps require grounded equivalence relations between views;
3. adding projection now would confound the cleaner horizon-transport question;
4. the H128 result already shows a coherent response surface without projection machinery.
```

So X-Token informs later gauge-composition theory, not the next empirical step.

## 8. What this does not show

The H128 branch has not shown:

```text
agency;
valuerhood;
identity;
Omega-compatible structure;
graph-channel causality;
holdout generalization;
weakened/rerouted/reopened/collapsed empirical response regimes;
```

The absence of weakened/rerouted/reopened/collapsed empirical rows matters. Fixtures can emit those classes, but the generated substrate has not yet surfaced them under the tested perturbation ladder.

Therefore the current theory update is bounded:

```text
horizon-transport aligned amplification is an empirically surfaced response pattern;
it is not a value-bearing or agentic classification.
```

## 9. Next theoretical questions

The H128 result opens several specific theory questions.

### 9.1 What is aligned amplification?

Possible interpretations:

```text
increased transport coherence;
noise-induced opening of additional aligned routes;
roughness increasing future-transport mass without changing branch identity;
finite substrate effect;
precursor to later weakening/collapse at higher perturbation;
measurement artifact not yet caught by current nulls.
```

The next empirical branch should distinguish these.

### 9.2 Is there a critical horizon threshold?

The first amplified horizon moves earlier as perturbation strength rises.

This suggests a response-threshold object:

```text
H_amp(p)
```

or more generally:

```text
H_response(class, p, family, probe, flow)
```

A future theory note should ask whether this behaves like a phase boundary, a finite-horizon artifact, or a genuine transport response curve.

### 9.3 Does amplified alignment precede weakening, rerouting, reopening, or collapse?

The ladder has not yet found later classes.

A future response-surface run may test:

```text
higher perturbation strengths;
more graded boundary probes;
longer horizons;
alternate perturbation families;
resolution changes;
fixture-derived classifier checks.
```

But those should remain response-profile tests, not survival/failure tests.

## 10. Next empirical posture

The branch has earned more horizon-transport work.

It has not earned holdout, graph perturbation, or candidate promotion.

Reasonable next actions:

```text
write this theory/instrument note;
run response-threshold mapping around H_amp;
try slightly stronger boundary probes with explicit viability-boundary labels;
compare response surfaces across resolution/scale views;
only later consider direct channel diagnostics if response profiles suggest localized functional dependence.
```

Still blocked:

```text
holdout scoring;
n=6 transfer;
alphabet expansion as promotion;
graph-channel causal claims;
agent/value/Omega labels.
```

## 11. 3P check

### Principled

The object is horizon transport, directly tied to the theory's concern with future continuability across horizon.

### Parsimonious

The live branch uses one directional matrix family, matched marginal detector nulls, and response classes instead of adding semantic labels.

### Predictive

The H128 result produced a concrete prediction target:

```text
as perturbation strength rises, the first amplified-aligned horizon shifts earlier.
```

Future work should test whether this response surface persists, sharpens, changes class, or disappears under stronger controls and broader substrate views.

## 12. Bottom line

The new intermediate theory object is:

```text
matched-marginal-separated horizon transport with horizon-dependent aligned amplification under nonlethal perturbation
```

This is the cleanest empirical object the project has surfaced so far.

It should now be front and center in the RFS-MB0 branch.

It is still only an intermediate object. It is not Omega. It is not agency. It is not value. It is the current best handle on future-field deformation.
