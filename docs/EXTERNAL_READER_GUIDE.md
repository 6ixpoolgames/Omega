# External Reader Guide

Status: onboarding guide for outside collaborators  
Scope: current RFS-MB0 horizon-transport / transition-energy substrate branch  
Claim boundary: this repository does not claim Omega validation, agency detection, value detection, identity detection, life detection, candidate promotion, holdout readiness, or graph-channel causality.

## 0. What this repository is

This repository is an empirical research workspace for the Omega / Reachable Futures project.

The current work asks a narrow question:

```text
Can neutral finite transition systems produce measurable future-landscape
structure that separates from matched nulls, without importing semantic labels
such as agent, valuer, identity, or good?
```

The current live instrument is **horizon transport**:

```text
T_{H_a -> H_b}
```

It measures how structures in earlier reachable-future frontiers become structures in later reachable-future frontiers.

The current live substrate program uses explicit **transition energy**:

```text
E(s,t)
```

where `E(s,t)` is an edge-selection score over possible transitions. It is not utility, reward, fitness, value, thermodynamic energy, or Omega.

## 1. What this repository is not claiming

This repository does **not** currently claim:

```text
Omega validated;
agent detected;
valuer detected;
identity detected;
life detected;
self-replication detected;
candidate promoted;
holdout ready;
graph-channel causality established;
value-bearing structure demonstrated.
```

Positive results should be read as **instrument and substrate-characterization results**, not as full theory validation.

## 2. Current result in plain English

The project has moved from static endpoint/co-occurrence probes toward directional horizon transport.

The strongest current pattern is:

```text
locality-only substrates:
  behave like a baseline

smooth directional fields:
  produce rerouting/reopening/differentiated response, but not aligned amplification in the tested grid

preservation asymmetry:
  carries aligned amplification under matched controls

combined asymmetry:
  clean and rerouting-bearing, but not yet synergistic in the sparse tested grid
```

The latest preservation-focused asymmetry-ladder scaleup strengthened the preservation-asymmetry read. The cleanest current target is `symbol_histogram_distance`, because it produced aligned amplification, rerouting, reopening, weakening, and no baseline-missing rows.

## 3. Core vocabulary

### Distinction

A finite state space:

```text
X
```

States differ from one another.

### Relation

A transition relation:

```text
s -> t
```

Some states can transform into other states.

### Asymmetry

A transformation is not equivalent to its reverse, or does not have the same future consequences.

### Horizon

A finite lookahead scale. Horizon transport compares structures at one horizon to structures at another.

### Horizon transport

A directional matrix family:

```text
T_{H_a -> H_b}
```

This asks what earlier reachable-future structures become later.

### Transition energy

An edge-selection score:

```text
E(s,t)
```

Lower-energy transitions are selected more readily. This is a substrate-generation rule, not a value claim.

### Directional asymmetry

A scalar asymmetry field:

```text
A(s)
```

used through:

```text
A(t) - A(s)
```

This makes one direction across the field different from the reverse.

### Preservation asymmetry

A macro-invariant or coarse asymmetry coordinate:

```text
I(s)
```

used through:

```text
|I(t) - I(s)|
```

This makes erasing or changing a coarse distinction less available than preserving it.

### Matched nulls

Control matrices that preserve important low-level structure, such as row/column marginals, while destroying the candidate structure being tested. Passing these nulls is an instrument requirement, not a theory validation claim.

### Perturbation response

A perturbation is not treated as simple survival/failure. It can produce response profiles:

```text
stable
amplified-aligned
weakened
rerouted
reopened
collapsed
control-equivalent
measurement-limited
```

## 4. Current transition-energy ladder

The current minimal substrate ladder is:

```text
E0 locality only:
  E(s,t) = d(s,t) + roughness

E1 directional asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + roughness

E2 preservation asymmetry:
  E(s,t) = d(s,t) + beta * |I(t)-I(s)| + roughness

E3 combined asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + beta * |I(t)-I(s)| + roughness
```

The current evidence supports this provisional read:

```text
E0:
  baseline

E1:
  differentiated response / rerouting

E2:
  aligned amplification

E3:
  clean but not yet tuned or synergistic
```

## 5. Best first reading path

### 15-minute orientation

Read:

1. `README.md`
2. this guide
3. `docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md`

Goal: understand what the live result is and what it does not claim.

### 60-minute technical orientation

Read:

1. `docs/research_notes/omega_theory/horizon_transport_aligned_amplification.md`
2. `docs/research_notes/omega_theory/transition_energy_and_constraint_untethering.md`
3. `docs/research_notes/omega_theory/transition_energy_substrate_atlas.md`
4. `docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_transition_energy_result.md`
5. `docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md`

Goal: understand why the project moved from hand-built constraint templates toward transition-energy asymmetry families.

### Implementation orientation

Read:

1. `docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md`
2. `docs/RFS_MB0_TRANSITION_ENERGY_SUBSTRATE_CHARACTERIZATION_RUN_SPEC.md`
3. `docs/implementation/horizon_transport_runner_map.md`
4. `docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md`

Goal: understand what the runner emits, what controls are required, and how result notes should be interpreted.

### Historical orientation

Read only after the current branch is clear:

1. `docs/PUBLIC_RESULTS_INDEX.md`
2. `docs/OMEGA_RUNNING_LOG.md`
3. `docs/OMEGA_PROJECT_MANUAL.md`
4. `docs/research_notes/omega_theory/historical_probe_terms.md`

Goal: understand the failed and demoted branches that led to the current instrument.

## 6. Current empirical state

The current empirical state is:

```text
horizon transport:
  mature enough for substrate-response characterization

matched marginal nulls:
  mandatory and currently passing in the live branch

fixture contract:
  required before response classes are interpreted

locality-only:
  baseline

directional asymmetry:
  rerouting / differentiated response

preservation asymmetry:
  current loadbearing branch for aligned amplification

symbol-composition preservation:
  current cleanest target inside preservation asymmetry

combined asymmetry:
  not yet abandoned; needs better parameterization after preservation is resolved
```

## 7. Current next step

The immediate next empirical task is not holdout and not candidate promotion.

It is:

```text
low-beta preservation-asymmetry sensitivity
```

The latest scaleup found that beta values from `0.25` to `4.0` mostly sit on a saturated selected-edge plateau. The next run should resolve beta values below `0.25`:

```text
0
0.005
0.01
0.025
0.05
0.10
0.15
0.25
```

The focus should be:

```text
symbol_histogram_distance:
  cleanest current target

total_coordinate_mass:
  still live but paired-baseline limited

hamming_weight_or_nonzero_count:
  clean low-signal comparator
```

A max-entropy local transition ensemble should come after this sensitivity map is clearer.

## 8. How to evaluate a result note

When reading a result note, look for these questions:

```text
Did all jobs complete?
Were there errors?
Did matched marginal detector-null gates pass?
Did the fixture contract pass?
Are response rows interpretable, or measurement-limited?
Are baseline-missing rows separated from real response classes?
Does the result change the instrument, the substrate family, or the broader theory?
Does the note explicitly block Omega/agency/value/candidate claims?
```

A result can be very useful while still making no Omega claim.

## 9. How an outside collaborator can help

Useful contributions include:

```text
reviewing the transition-energy formalism;
checking whether the matched null suite is strong enough;
proposing cleaner maximum-entropy transition ensembles;
reviewing matrix and spectral methodology;
stress-testing the response taxonomy;
helping design non-semantic substrate families;
improving documentation and reproducibility;
identifying hidden assumptions in E(s,t), A(s), and I(s).
```

The project especially benefits from criticism that distinguishes:

```text
instrument artifact;
substrate artifact;
real but low-level transport structure;
stronger theory-relevant structure.
```

## 10. The mantra

The working mantra is:

```text
Principled.
Parsimonious.
Predictive.
```

Principled: define objects from the substrate and controls, not from semantic labels.

Parsimonious: prefer the smallest substrate ingredients that can explain the observed response.

Predictive: every theory update should imply a concrete next run or failure mode.
