# RFS-MB0 Future Landscape Pattern Spec

Status: corrected theory-to-implementation spec

Purpose: interrogate Omega-adjacent structure without defining agents, identities, valuers, viable paths, goals, rewards, or semantic substrates.

## 0. Core reset

The empirical arm should not begin by asking:

```text
What is an agent?
What is a valuer?
What is identity?
Which path is viable?
Which future is good?
```

It should begin from the primitive triad:

```text
distinction
relation
asymmetry
```

and derive future-landscape structure.

The first observable is not an agent.

The first observable is:

```text
structured deformation of future space
```

The value-bearing thing, if it exists, remains latent. It is inferred only later from how future landscapes are shaped.

## 1. Hard neutrality constraints

Do not hand-define:

```text
agent
valuer
identity
goal
reward
utility
viability
harm
support
recovery
degradation
Omega-like
pseudo-Omega-like
```

Do not hand-label paths as:

```text
viable
nonviable
good
bad
valuable
agent-preserving
```

Do not add primitive resource/cost/fuel coordinates such as:

```text
energy
kappa
budget
health
resource
metabolism
```

Cost is not part of the primitive substrate for this probe.

If a cost analogue is reported, it must be derived after the fact as null-to-structure divergence.

## 2. Primitive substrate

The primitive substrate is:

```text
S = (X, R)
```

where:

```text
X:
  finite distinction space

R subset X x X:
  neutral relation over distinctions
```

A transition is:

```text
x R y
```

meaning only that `y` is related/reachable from `x` by one primitive step.

A transformation presentation is allowed:

```text
T = {t_i}
```

with:

```text
x R y iff exists t in T such that y in t(x)
```

but transformation names must remain operational and neutral.

Allowed naming style:

```text
shift
swap
rotate
project
copy
couple
decouple
scramble
contract
expand
phase_advance
```

Forbidden naming style:

```text
repair
harm
support
capture
degrade
recover
heal
attack
protect
```

## 3. Asymmetry is derived, not labeled

Asymmetry is not a semantic property.

It is derived from relation:

```text
x reaches y but y does not reach x
x has more/fewer futures than y
paths from x bottleneck through z
future profiles expand, collapse, cycle, or randomize after transitions
```

The probe should measure these relational asymmetries rather than label them.

## 4. Future landscape

For each state:

```text
x in X
```

define the finite-horizon reachable future set:

```text
Reach_H(x) = { y in X : y is reachable from x by a path of length <= H }
```

and exact-H frontier:

```text
Exact_H(x) = { y in X : y is reachable from x by a path of length exactly H }
```

The raw future landscape is the filtration:

```text
Lambda_H(x) = (Reach_0(x), Reach_1(x), ..., Reach_H(x))
```

This filtration is derived only from `(X, R)`.

## 5. Neutral probes and signatures

To describe future landscapes, define a family of neutral probes:

```text
Sigma_sigma
```

Each probe is a map:

```text
sigma : X -> A_sigma
```

The probe family must be generated mechanically from the substrate presentation, not chosen to represent agents or values.

Allowed probe families:

```text
coordinate projections
coordinate-pair relations
modular / equality relations
local transition response profiles
bounded-depth behavioral signatures
quotient / role signatures
```

The implementation must report which probes were generated and how many were used.

No probe may be named after an agent, valuer, identity, support relation, harm relation, recovery relation, or viability relation.

## 6. Future signature distributions

For each state `x`, horizon `h`, and probe `sigma`, compute a distribution over exact-horizon signatures:

```text
P_h^sigma(. | x)
```

This distribution may be endpoint-count based or path-measure based.

For the first exact finite probe, endpoint-count distributions are acceptable:

```text
P_h^sigma(s | x) =
  count({ y in Exact_h(x) : sigma(y) = s }) / |Exact_h(x)|
```

If exact path enumeration is tractable, also report path-count distributions.

If passive random walks are used, use a neutral kernel such as uniform over outgoing edges and clearly label it as a measurement kernel, not a value model.

## 7. Future-profile map

Define a future-profile map:

```text
Phi_H : X -> Profile
```

`Phi_H(x)` summarizes the structure of future signature distributions across horizons and probes.

Required profile components:

```text
reach_count_by_h
exact_count_by_h
growth_rate_by_h
signature_entropy_by_h
signature_support_size_by_h
recurrence_rate_by_h
transition_motif_count_by_h
predictive_information_by_h
compression_proxy_by_h
saturation_horizon
cycle_indicator
collapse_indicator
```

All components must be descriptive and neutral.

No component may encode a hand-defined viable path set.

## 8. Pattern vs noise detector

The detector must classify future-profile behavior into neutral classes only.

Required classes:

```text
noise_like
collapse_like
cycle_like
permissive_blur
strict_fragmentation
structured_propagation
underdetermined
```

Class definitions must be based on profile statistics and controls, not semantic labels.

### 8.1 noise_like

High variation without reusable structure.

Typical profile:

```text
high entropy
low predictive information
low recurrence
weak compression
similar to random / degree controls
```

### 8.2 collapse_like

Low diversity and early saturation.

Typical profile:

```text
low entropy
low exact frontier growth
early saturation
fixed-point or tiny-attractor behavior
```

### 8.3 cycle_like

Periodic recurrence with low generative breadth.

Typical profile:

```text
recurring signatures
periodic future profiles
low novelty
bounded future diversity
```

### 8.4 permissive_blur

The probe collapses too many distinctions.

Typical profile:

```text
too few signatures
low distinction power
apparent coherence from overbroad equivalence
```

### 8.5 strict_fragmentation

The probe separates too much.

Typical profile:

```text
too many one-off signatures
low recurrence
low reusable motif structure
```

### 8.6 structured_propagation

Nontrivial future structure that is neither noise, collapse, nor mere cycle.

Typical profile:

```text
nontrivial branching
nonzero predictive structure
recurring motifs
compression above random controls
stable across horizon
not fixed-point collapse
not phase-only recurrence
```

This is the minimal operational analogue of the older theory phrase:

```text
structured branching that propagates
```

Do not call it Omega-like.

## 9. Established measures to borrow

Use established tools wherever possible.

Required initial measures:

```text
Shannon entropy
conditional entropy
mutual information / predictive information
recurrence / motif reuse
compression or grammar-size proxy
JS divergence from null
smoothed KL divergence from null
```

Optional later measures:

```text
bounded-depth bisimulation / behavioral quotient size
information bottleneck-style compressed predictors
computational-mechanics-style predictive states
symbolic-dynamics language growth
topological / sheaf tools only after local-to-global compatibility is earned
```

## 10. Null models and controls

Pattern is not absolute. It is structure relative to matched nulls.

Implement matched controls:

```text
random_relation_control
degree_preserving_control
coordinate_permutation_control
phase_cycle_control
fixed_point_control
permissive_probe_control
strict_probe_control
```

The detector must compare future-profile statistics against these controls.

A profile is not considered structured merely because it differs from one weak null.

## 11. Null-to-structure divergence as cost analogue

Do not add cost to the substrate.

Instead, define cost analogue as probability steering from null to observed structure.

For observed distribution:

```text
P_h^sigma(. | x)
```

and matched null distribution:

```text
Q_h^sigma(. | x)
```

report:

```text
JS(P_h^sigma, Q_h^sigma)
smoothed_KL(P_h^sigma || Q_h^sigma)
```

Interpretation:

```text
How much probability mass must be reshaped away from the null
in order to reproduce the observed future-signature distribution?
```

This is an information-theoretic work analogue, not literal thermodynamic work.

Divergence alone must not define success.

A fixed point or clock may have high divergence from null. Therefore the detector must always report:

```text
profile class + divergence from null
```

## 12. Deformation of future landscape

For each edge:

```text
x -> y
```

compare:

```text
Delta Phi_H(x -> y) = compare(Phi_H(x), Phi_H(y))
```

Report neutral deformation descriptors:

```text
future_entropy_delta
reach_growth_delta
predictive_information_delta
recurrence_delta
compression_delta
collapse_indicator_delta
cycle_indicator_delta
JS_to_null_delta
```

No deformation descriptor should be called support, harm, recovery, degradation, or improvement.

## 13. Candidate organizers are downstream

Do not implement agents or identities in this probe.

If structured future landscapes are detected, define future-profile equivalence:

```text
x ~_Phi y iff Phi_H(x) approximately equals Phi_H(y)
```

Candidate organizers may later be inferred as:

```text
stable equivalence classes or latent factors explaining future-profile deformation
```

But they are not part of the first implementation gate.

## 14. Implementation target

Create a new package:

```text
omega/rfs_mb0_future_landscape/
```

Suggested files:

```text
substrate.py
probes.py
landscape.py
detectors.py
controls.py
run_smoke.py
```

### substrate.py

Neutral finite substrate generators.

Must expose:

```text
states
relation / edges
transform presentation if used
initial states or sampled states
```

No semantic state labels.

### probes.py

Generate neutral probes mechanically from the substrate presentation.

Must expose:

```text
generate_probes(sigma)
probe(state) -> signature
```

### landscape.py

Compute:

```text
Reach_H
Exact_H
signature distributions
future profiles Phi_H
edge deformation profiles Delta Phi_H
```

### detectors.py

Compute:

```text
entropy
conditional entropy
mutual information / predictive information
recurrence
compression proxy
JS divergence
smoothed KL divergence
profile class
```

### controls.py

Generate matched null/control substrates and probe controls.

### run_smoke.py

Run small exact/sampled smoke and write outputs.

## 15. Required outputs

Write:

```text
results.csv
future_profiles.csv
signature_distributions.csv
control_comparison.csv
profile_classes.csv
divergence_summary.csv
deformation_summary.csv
summary.md
status.json
```

`summary.md` must include:

```text
run shape
substrate summary
probe summary
future-profile class counts
pattern/noise/collapse/cycle separation
JS/KL divergence by class and horizon
control comparison
claim boundary
next recommendation
```

## 16. Initial smoke size

Keep small:

```text
states: finite and exactly enumerable if possible
horizons: 0,1,2,4,8,12,16
probes: sigma <= 2 initially
controls: all required controls
seeds: small, enough for smoke only
```

Do not scale until the detector separates at least:

```text
noise_like
collapse_like
cycle_like
structured_propagation
```

under matched controls.

## 17. Success criteria

Instrumentation success:

```text
future landscapes computed
neutral probes generated
profile statistics computed
null controls generated
JS/KL divergence reported
profile classes assigned
```

Scientific gate success:

```text
structured_propagation separates from noise_like, collapse_like, cycle_like,
permissive_blur, strict_fragmentation, random controls, and degree controls
by multiple independent measures.
```

Failure:

```text
profile classes do not separate from controls
probe choice dominates results
all structures collapse into noise/cycle/fixed-point profiles
JS/KL divergence is high only for collapse/cycle artifacts
```

## 18. Claim boundary

Allowed:

```text
We implemented a neutral future-landscape probe derived from distinction,
relation, and asymmetry.
```

Allowed if supported:

```text
The detector separated structured future-landscape propagation from noise,
collapse, cycle, permissive, strict, random, and degree controls.
```

Not allowed:

```text
Omega detected
valuer detected
agent detected
identity detected
viability detected
moral value detected
```

## 19. Bottom line

The first object is:

```text
Phi_H(x)
```

the future landscape profile induced by the primitive triad.

The first signal is:

```text
structured propagation in future space
```

The first cost analogue is:

```text
null-to-structure divergence
```

Agents, identities, valuers, and Omega interpretations remain downstream and latent.
