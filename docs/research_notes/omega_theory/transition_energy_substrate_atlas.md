# Transition-Energy Substrate Atlas

Status: theory / instrument atlas note after transition-energy substrate characterization  
Scope: RFS-MB0 horizon-transport branch and transition-energy substrate program  
Claim boundary: not Omega detection, not agency detection, not valuer detection, not identity detection, not life detection, not candidate promotion

Terminology update:

```text
Use "macro-invariant" in public-facing prose.
Use "asymmetry-constrained transition energy" in theory-facing prose.
The raw implementation/output name "budget_conservation" is retained only for
backward compatibility with scripts and CSVs.
```

## 0. One-sentence update

The transition-energy characterization run turns the horizon-transport branch from a single-substrate detector into a **substrate-response atlas**: different transition-energy laws express different horizon-transport response profiles, and those differences are signal rather than noise.

In compact form:

```text
locality alone:
  clean baseline; no aligned amplification in the tested grid

smooth random potential:
  response-bearing; rerouting/reopening/weakening appear, but no aligned amplification in this grid

macro-invariant / asymmetry-constrained transition energy:
  aligned response appears; total-coordinate-mass is strongest but coverage-limited

constraint template comparator:
  still positive; no longer unique
```

This is a substrate-characterization result, not validation.

## 1. Result grounding

The larger transition-energy characterization run completed cleanly:

```text
jobs_completed: 7744 / 7744
errors: 0
null_replicates: 13
matrix_count: 10324
substrate_family_variant_count: 22
perturbation_response_rows: 9410
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: 8 / 8
```

The runner also repaired a load-bearing bug before the run: perturbation-response baselines are now keyed by:

```text
substrate_family, substrate_variant, probe, flow, H_a, H_b
```

rather than only:

```text
probe, flow, H_a, H_b
```

This matters because substrate-family comparisons are invalid if perturbation matrices can be compared to baselines from other substrate families or variants.

The retained result's decision was:

```text
locality_only_baseline_confirmed
```

with next action:

```text
write_transition_energy_substrate_atlas_note
```

This note is that atlas.

## 2. Why this atlas matters

The project has been trying to avoid discovering artifacts of its own hand-built machinery.

Earlier horizon-transport results were strong inside the current constraint-template substrate, but that substrate used a hand-picked law vocabulary:

```text
local_modular_sum_preference
local_equality_relation
local_difference_relation
```

The transition-energy program asks whether the same horizon-transport instrument remains meaningful when substrate laws are written as generic transition-energy families:

```text
E(s,t):
  transition energy / edge-selection score

Q(s -> t):
  local proposal neighborhood

R:
  edge selection rule
```

The characterization run shows that the instrument does not merely light up everywhere. It distinguishes substrate-law families:

```text
locality-only behaves like a baseline;
smooth potential generates differentiated response without aligned amplification;
macro-invariant / asymmetry-constrained transition energy produces aligned response;
constraint templates remain positive but no longer exclusive.
```

This is exactly what an instrument should do if substrate law matters.

## 3. Atlas entries

### 3.1 Locality-only

Result:

```text
response rows: 1320
interpretable rows: 1320
dominant response: transport_stable
aligned fraction: 0.000
stable rows: 1221
rerouted rows: 99
```

Interpretation:

```text
bounded local branching alone is not sufficient for aligned amplification in this tested grid.
```

This is useful. Locality-only should remain the baseline family, not the target object.

If locality-only eventually produces aligned amplification under a different setting, that would be important, but current evidence says:

```text
locality alone is not the H128 object.
```

### 3.2 Smooth random potential

Result:

```text
response rows: 3960
interpretable rows: 3960
dominant response: transport_stable
aligned fraction: 0.000
stable rows: 3480
weakened rows: 20
rerouted rows: 229
reopened rows: 231
```

Interpretation:

```text
smooth potential is response-bearing but not aligned-amplifying in this beta/smoothness grid.
```

This is not a dead branch. It may be the better family for studying differentiated responses such as rerouting and reopening.

Current read:

```text
smooth-potential law supports response diversity;
it does not currently support the aligned-amplification object.
```

Next questions:

```text
Does a different smoothness / beta / roughness regime produce aligned amplification?
Is smooth potential a route to rerouting/reopening rather than amplification?
Can smooth-potential response diversity be made cleaner under max-entropy control?
```

### 3.3 Macro-Invariant / Asymmetry-Constrained Transition Energy

Result:

```text
response rows: 3690
interpretable rows: 3420
dominant response: transport_stable
aligned fraction: 0.109
stable rows: 2589
amplified rows: 402
weakened rows: 120
rerouted rows: 51
reopened rows: 258
resolution mismatch rows: 270
```

Invariant kinds:

```text
total_coordinate_mass:
  aligned fraction: 0.203
  strongest aligned fraction;
  but 270 resolution-mismatch rows

hamming_weight_or_nonzero_count:
  aligned fraction: 0.084
  cleaner matched-null behavior;
  lower aligned fraction

symbol_histogram_distance:
  aligned fraction: 0.059
  more weakened/reopened response;
  lower aligned fraction
```

Interpretation:

```text
approximate invariants appear to be a productive generic lawlike ingredient.
```

But the note should remain cautious:

```text
Macro-invariant / asymmetry-constrained transition energy is promising, but total-coordinate-mass cannot be declared the winner without coverage / paired-baseline repair.
```

Current read:

```text
macro-invariant / asymmetry-constrained terms are the strongest non-template route to aligned amplification;
they should guide the next substrate repair and max-entropy design.
```

### 3.4 Constraint-template comparator

Result:

```text
response rows: 440
interpretable rows: 440
dominant response: transport_stable
aligned fraction: 0.180
stable rows: 228
amplified rows: 79
rerouted rows: 94
reopened rows: 39
```

Interpretation:

```text
the original constraint-template substrate remains useful, but it is no longer the only substrate family producing aligned response.
```

The correct role of this family is now comparator, not privileged primary substrate.

## 4. Substrate law differences are signal

The key interpretive change is:

```text
Do not force substrate families to behave the same.
```

Different substrate laws should be expected to express different transport response regimes.

A useful atlas may look like:

```text
locality-only:
  baseline / diffusion / bounded branching

smooth-potential:
  rerouting / reopening / differentiated response

macro-invariant / asymmetry-constrained:
  aligned amplification / high-viscosity transport

constraint-template:
  historical comparator / mixed response
```

This is not failure to converge. It is the beginning of substrate taxonomy.

## 5. Current ontology of substrate families

The current atlas suggests a provisional substrate-law taxonomy:

### 5.1 Baseline local branching

```text
family:
  locality_only

signature:
  high stability;
  no aligned amplification;
  occasional rerouting;
  useful null-like comparator.
```

### 5.2 Landscape response substrate

```text
family:
  smooth_random_potential

signature:
  stable dominant response;
  rerouting/reopening/weakening can appear;
  aligned amplification absent in tested grid.
```

### 5.3 Invariant-constrained amplifier

```text
family:
  macro_invariant / asymmetry_constrained
  raw implementation alias: budget_conservation

signature:
  aligned amplification appears;
  high-viscosity aligned-amplifier read plausible;
  coverage / resolution mismatch must be repaired.
```

### 5.4 Symbolic-law comparator

```text
family:
  constraint_template_current

signature:
  aligned amplification still appears;
  rerouting/reopening also appear;
  no longer unique or primary.
```

This taxonomy is provisional and instrument-relative.

## 6. Relation to the theory primitives

The transition-energy program maps cleanly onto the primitives:

```text
distinction:
  finite states differ

relation:
  selected transitions connect states

asymmetry:
  transition energy / selection can make s -> t and t -> s non-equivalent
```

Substrate families differ by the generic lawlike ingredients used to shape `E(s,t)`:

```text
locality:
  distance in distinction space

potential:
  smooth scalar landscape over states

macro-invariant / asymmetry-constrained:
  approximate invariant or resource-like macro quantity

constraint templates:
  named symbolic relations, now demoted to comparator
```

The important move is that `E(s,t)` concentrates assumptions into an explicit, inspectable object rather than scattering them across opaque constraint vocabularies.

## 7. Why Macro-Invariants Are Theoretically Interesting

The macro-invariant / asymmetry-constrained family is currently the most interesting non-template route to aligned amplification.

This may matter because invariants are what make a substrate feel universe-like:

```text
some quantities are conserved;
some changes are costly;
some trajectories preserve macro-structure;
some deformations are possible but expensive.
```

A future-bearing object may require more than locality and smoothness. It may require an approximately conserved structure that lets transport persist, concentrate, and amplify without immediately diffusing.

This is still speculative. The current empirical statement is narrower:

```text
macro-invariant transition-energy terms produced aligned amplification in this grid;
locality-only did not;
smooth-potential did not, though it produced other response classes.
```

## 8. Why smooth potential is still useful

The smooth-potential family did not produce aligned amplification here. But it produced rerouting and reopening rows.

This makes it valuable for a different question:

```text
What substrate laws support differentiated response rather than aligned amplification?
```

The project should not collapse all progress into the aligned-amplification class. A richer life-like branch may require response diversity. Smooth potential may be a candidate family for that later branch.

## 9. What this does not show

The transition-energy substrate atlas does not show:

```text
Omega;
agency;
valuerhood;
identity;
life;
self-replication;
functional channels;
graph-channel causality;
holdout generalization.
```

It also does not yet show:

```text
macro-invariant transition energy cleanly wins;
max-entropy local transition ensemble is implemented;
aligned amplification is substrate-general across all generic laws;
smooth potential cannot produce aligned amplification under any parameterization.
```

The atlas is a map of current instrument behavior, not a final substrate theory.

## 10. Next empirical decisions

The retained result recommends:

```text
write_transition_energy_substrate_atlas_note
```

Then choose between:

```text
repair_budget_coverage
implement_max_entropy_local_transition
```

This note recommends a hybrid sequence:

```text
1. repair macro-invariant coverage / paired-baseline availability;
2. use macro-invariant marginal constraints to design the first max-entropy local transition ensemble;
3. keep locality-only as a baseline family;
4. keep smooth-potential as a differentiated-response branch;
5. keep constraint-template only as comparator.
```

## 11. Max-entropy direction

The next major substrate should not be an unconstrained random graph.

It should be a max-entropy local transition ensemble with explicit macro constraints, likely including macro-invariant marginals:

```text
state count;
coordinate count;
alphabet size;
local proposal radius;
out-degree distribution;
reversibility fraction;
roughness / energy marginal profile;
optional macro-invariant marginal constraints.
```

Reason:

```text
locality-only is too weak for aligned amplification;
macro-invariant constraints appear loadbearing;
max-entropy should preserve only macro constraints needed to make the substrate generative, not hand-picked symbolic laws.
```

This is the cleanest path away from hand-built constraint vocabulary while preserving enough structure to remain falsifiable.

## 12. Recommended immediate spec direction

A next spec should probably be one of two things.

### Option A: Macro-invariant coverage repair

Purpose:

```text
Resolve whether macro-invariant / asymmetry-constrained aligned amplification remains strong after coverage / baseline-availability repair.
```

Focus:

```text
total coordinate-mass invariant;
nonzero-support invariant;
symbol-composition invariant;
coverage and paired-baseline availability;
matched-null stability;
response thresholds by invariant weight.
```

### Option B: Max-entropy local transition preflight

Purpose:

```text
Implement a minimal max-entropy local transition ensemble with macro constraints suggested by the atlas.
```

Focus:

```text
locality;
out-degree;
reversibility;
roughness;
optional macro-invariant marginal;
no named symbolic law templates.
```

My recommendation:

```text
Do Option A first if the goal is empirical cleanliness.
Do Option B first if the goal is substrate-principle progress.
```

A hybrid preflight is acceptable if kept small.

## 13. 3P check

### Principled

The atlas organizes substrate families by explicit transition-law ingredients: locality, smooth potential, macro-invariance/asymmetry constraint, and symbolic constraint templates.

### Parsimonious

It does not add agent/value/life labels. It keeps the same horizon-transport instrument and lets substrate laws differ.

### Predictive

The atlas produces testable predictions:

```text
locality-only should remain a baseline unless roughness/out-degree changes move it into response-bearing regimes;
macro-invariant constraints should continue to support aligned amplification if coverage is repaired;
smooth-potential should continue to support differentiated response, and may or may not amplify under different beta/smoothness;
max-entropy with macro-invariant marginals should be more promising than max-entropy locality-only.
```

## 14. Bottom line

The current substrate atlas says:

```text
The instrument is now discriminating substrate laws rather than merely detecting an artifact everywhere.
```

That is a major improvement.

The next substrate target should preserve this lesson:

```text
Do not erase substrate-law differences by forcing all families into one response curve.
```

The project should proceed either to a narrow macro-invariant paired-baseline repair or to a max-entropy local transition preflight with macro-invariant constraints, while keeping the claim boundary closed.
