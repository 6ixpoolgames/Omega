# RFS0 Strict Reachable Futures Batch Spec

Finite exact substrate batch for strict recovery-conditioned viability

## Purpose

This spec defines the first batch for the reachable-futures substrate reset.

The project is moving away from asking whether a permissive toy substrate can culture something Omega-shaped. Viable continuation appears easy to culture in nontrivial systems with distinction, asymmetry, and relation. The current blocker is substrate resolution: can we define a minimal substrate where a stricter, recovery-conditioned viable-futures object can be resolved without tuning toward a desired result?

RFS0 should therefore use a deliberately harsh formal filter.

Core question:

```text
In a small exact finite transition system, does any reachable future structure
survive a naively strict recovery-conditioned viability definition?
```

If something survives this filter, it is not Omega validation, but it is a cleaner candidate object than generic viability. It means the substrate contains a sparse region compatible with the broader theory target: continuation that is not merely nonterminal, but future-bearing, recoverable, and resistant to immediate collapse.

## Theory rationale

### Why reset to RFS0?

Previous probes taught useful lessons:

```text
VAL0-CT:
  R1 anchor wins showed future-retention reachability can beat greedy reachability
  in designed task geometries, but broad held-out generalization did not pass.

VAL0-G:
  neutral grammars cultured stable viability regimes, but high-mass regions were
  cap-censored and not discriminating enough.

VAL1-MF enumeration:
  adding fields worsened cap censoring under raw joint enumeration.

VAL1-MF interference audit:
  sampled counterfactual deltas detected constructive support-like interference,
  but not robust destructive/capture dynamics.
```

Interpretation:

```text
viability is easy to culture;
Omega-compatible discrimination is not yet demonstrated;
the likely blocker is substrate resolution, not compute.
```

RFS0 should establish the exact finite measurement floor before returning to agents, constructors, or multifield coupling.

### Why strict viability first?

Generic viability is too permissive as an empirical target.

The first RFS0 batch should intentionally overfilter:

```text
not:
  any continuation

but:
  continuation that already satisfies a harsh recovery-conditioned admissibility proxy
```

This mitigates overfit criticism. We are not tuning a permissive substrate until something appears. We are first asking whether anything survives a strict formal filter.

The strict object is a proxy, not Omega itself.

Allowed claim if successful:

```text
A sparse strict viable-futures object survives exact reachability, recovery, and
anti-collapse filters in a finite substrate.
```

Forbidden claim:

```text
Omega has been detected.
```

## 3P audit

### Principled

The substrate is grounded in:

```text
distinction:
  finite states differ by explicit attributes

asymmetry:
  transformations have different consequences for future reachability

relation:
  reachable futures are linked by transition structure over time
```

Strict viability is defined through formal admissibility and reachability, not outcome labels.

### Parsimonious

Do not add:

```text
agents
constructor candidates
multifield coupling
R1/R2 policies
Omega-positive labels
large random grammars
GPU work
```

Use the smallest exact finite system capable of computing reachable sets, viability kernels, capture basins, perturbation recovery, and future-space contraction.

### Predictive

The batch should distinguish these regimes:

```text
trivial viability:
  loose and strict viability both too large

self-termination:
  loose viability exists but strict viability vanishes quickly

recoverable sparse object:
  strict viability kernel and strict capture basin are sparse but nonzero

future-space contraction:
  immediate strict admissibility is preserved while future strict reachability shrinks

null/trivial controls:
  strict object disappears or becomes obviously trivial
```

## Substrate overview

Implement a small finite transition system.

### State

A state should be a finite attribute vector.

Suggested attributes:

```text
capacity:
  integer resource/slack value

integrity:
  integer structural/coherence value

repair:
  binary or small integer repair/re-entry channel

option:
  integer option-space/access channel

commit:
  binary irreversible-loss marker

location / mode:
  small discrete region marker, optional
```

Keep state count small enough for exact enumeration.

Recommended first range:

```text
capacity: 0..4
integrity: 0..4
repair: 0..2
option: 0..4
commit: 0..1
mode: 0..2 optional
```

Approximate state count if using all six attributes:

```text
5 * 5 * 3 * 5 * 2 * 3 = 2250 states
```

This is acceptable for exact graph methods.

### Transformations

Transformations are neutral attribute updates.

Example transformation families:

```text
expand:
  increases option, consumes capacity

maintain:
  preserves/increases integrity, consumes capacity

repair:
  increases repair or integrity, consumes capacity

harvest:
  increases capacity, may reduce option or integrity

commit:
  increases short-term option or capacity, sets irreversible marker

decay:
  exogenous or transition-linked reduction in integrity/option

reroute:
  changes mode and may restore option if repair is available
```

These names are implementation conveniences. Do not label transformations as good, bad, Omega, pseudo-Omega, or aligned.

### Admissibility

Define multiple admissibility sets for diagnostics, but make the primary target strict.

```text
K0_loose:
  nonterminal / at least one valid outgoing transformation

K1_option:
  K0 + reachable futures above minimum threshold

K2_recovery:
  K1 + perturbation can return to K1 within Hr

K3_repair:
  K2 + repair/re-entry channel available

K4_anticollapse:
  K3 + no irreversible loss marker + bounded future-space contraction

K_strict:
  naively strict recovery-conditioned admissibility
  normally equivalent to K4 or K5 below

K5_multi_perturb optional:
  K4 + survives multiple perturbation samples / horizons
```

Primary reported kernel:

```text
Viab(K_strict, H)
```

Diagnostic ladder:

```text
|K0|, |K1|, |K2|, |K3|, |K4|, |K_strict|
|Viab(K0)|, |Viab(K1)|, ..., |Viab(K_strict)|
```

## Exact definitions

### Reachable set

```text
Reach(x, H) = states reachable from x in <= H transitions
```

### Strict viability kernel

```text
Viab(K_strict, H) =
  states x such that there exists a path of length H from x
  and every state along that path remains in K_strict
```

Use existential viability first.

Optional later:

```text
robust viability:
  all allowed perturbations or adversarial disturbances still permit recovery
```

### Capture / recovery basin

```text
Capture(K_strict, Hr) =
  states x such that there exists a path of length <= Hr from x into K_strict
```

Recovery after perturbation:

```text
Recoverable_strict(x) =
  perturb(x) in Capture(K_strict, Hr)
```

This is what we mean by exact recovery: graph search into an explicit admissible set, not a learned or semantic detector.

### Future-space contraction

For transition/action `a: x -> y`:

```text
StrictReach(x, H) = Reach(x, H) intersect Viab(K_strict, H)

contraction_ratio(a, H) =
  |StrictReach(y, H)| / max(1, |StrictReach(x, H)|)
```

A contraction event:

```text
x in K_strict
y in K_strict
contraction_ratio(a, H) < threshold
```

This is a first formal proxy for local viability that narrows future viability. Do not call it pseudo-Omega yet.

## Batch structure

Run four small probes as one batch.

```text
RFS0-A:
  strict finite viability kernel smoke

RFS0-B:
  strict recovery / capture basin smoke

RFS0-C:
  future-space contraction smoke

RFS0-D:
  null / triviality controls
```

All should run on the same core finite substrate implementation.

## RFS0-A: strict finite viability kernel smoke

### Purpose

Ask whether the strict admissible object exists at all.

### Measurements

For each generated finite system:

```text
num_states
num_transitions
|K0|
|K1|
|K2|
|K3|
|K4|
|K_strict|
|Viab(K0, H)|
|Viab(K_strict, H)|
strict_kernel_fraction = |Viab(K_strict, H)| / num_states
strict_given_loose_fraction = |Viab(K_strict, H)| / max(1, |Viab(K0, H)|)
```

Horizons:

```text
H = 4, 8, 16
```

### Minimal success

```text
K0 nonempty
K_strict not equal to K0
Viab(K_strict, H) computable
```

### Strong success

```text
Viab(K_strict, H) sparse but nonzero for at least one nontrivial parameter regime
```

## RFS0-B: strict recovery / capture basin smoke

### Purpose

Ask whether perturbed states can return to the strict region.

### Perturbations

Define neutral perturbation operators such as:

```text
capacity_loss:
  capacity -= 1 or 2

integrity_damage:
  integrity -= 1 or 2

option_loss:
  option -= 1 or 2

repair_loss:
  repair -= 1

commit_flip:
  optional irreversible marker stress; use carefully
```

Clamp attributes to valid ranges.

### Measurements

```text
|Capture(K_strict, Hr)|
strict_capture_fraction
recovery_rate_from_K_strict_after_perturbation
recovery_rate_from_K0_after_perturbation
recovery_horizon_distribution
failed_recovery_count_by_perturbation_type
```

Recovery horizons:

```text
Hr = 2, 4, 8
```

### Success

```text
strict capture basin nonempty
strict recovery rate neither 0 nor 1 across all regimes
recovery varies by perturbation type and severity
```

## RFS0-C: future-space contraction smoke

### Purpose

Ask whether immediate strict admissibility can coexist with future strict reachability loss.

### Measurements

For each transition:

```text
source_in_K_strict
target_in_K_strict
strict_reach_source_H
strict_reach_target_H
contraction_ratio_H
contraction_event_flag
expansion_event_flag
neutral_event_flag
```

Aggregate:

```text
mean_contraction_ratio
contraction_event_rate
expansion_event_rate
strict_preserving_transition_count
strict_contracting_transition_count
```

Horizons:

```text
H = 4, 8, 16
```

### Success

```text
some strict-preserving transitions contract strict future reachability
some strict-preserving transitions preserve or expand strict future reachability
```

This distinguishes immediate admissibility from future-bearing admissibility.

## RFS0-D: null / triviality controls

### Purpose

Test whether strict objects are substrate artifacts.

### Controls

Run the same metrics on:

```text
dense_permissive_control:
  transitions dense, constraints loose
  expected: K0 large, strict filter may reveal triviality or remain too large

dead_control:
  transitions sparse/degrading, constraints harsh
  expected: strict kernel vanishes

random_edge_control:
  same edge density as structured substrate, but transformations shuffled
  expected: weaker strict recovery/capture structure

shuffled_admissibility_control:
  same transitions, K_strict labels shuffled preserving size
  expected: capture/recovery geometry changes or weakens

no_perturbation_control:
  removes recovery condition
  expected: shows how much strict object depends on recovery
```

### Success

```text
structured substrate differs from controls in strict kernel size,
capture basin size, recovery rate, or contraction profile
```

No need for all controls to fail. The goal is artifact diagnosis.

## Parameter regimes

Use neutral parameter regimes, not outcome labels.

Suggested regimes:

```text
balanced:
  moderate expansion, maintenance, repair, and decay

permissive:
  high expansion, low decay, loose constraints

harsh:
  low expansion, high decay, tight constraints

repair_rich:
  repair transformations more common

commit_rich:
  irreversible marker more common

capacity_tight:
  capacity-consuming transformations bind frequently
```

These are substrate regimes, not Omega labels.

Run enough seeds per regime to detect obvious degeneracy.

Recommended smoke batch:

```text
regimes:
  6

seeds per regime:
  25

total systems:
  150

state count:
  <= 2500 each

horizons:
  H = 4, 8, 16
  Hr = 2, 4, 8
```

If exact computation is trivial, increase to 50 seeds per regime. Do not add complexity before checking outputs.

## Required outputs

Directory:

```text
results/rfs0/<run_id>_strict_reachable_futures_batch/
```

Files:

```text
config.json
status.json
systems.jsonl
results.csv
kernel_summary.csv
capture_summary.csv
contraction_summary.csv
control_summary.csv
regime_summary.csv
summary.md
```

Per-system fields:

```text
system_id
seed
regime
num_states
num_transitions
constraint_params_json
transform_params_json

K0_size
K1_size
K2_size
K3_size
K4_size
K_strict_size

viab_K0_H4
viab_K0_H8
viab_K0_H16
viab_K_strict_H4
viab_K_strict_H8
viab_K_strict_H16

capture_K_strict_Hr2
capture_K_strict_Hr4
capture_K_strict_Hr8

recovery_rate_K_strict_capacity_loss
recovery_rate_K_strict_integrity_damage
recovery_rate_K_strict_option_loss
recovery_rate_K_strict_repair_loss

mean_contraction_ratio_H4
mean_contraction_ratio_H8
mean_contraction_ratio_H16
contraction_event_rate_H4
contraction_event_rate_H8
contraction_event_rate_H16
expansion_event_rate_H4
expansion_event_rate_H8
expansion_event_rate_H16

control_type
is_control
```

## Summary requirements

The summary should answer:

```text
1. Did the batch complete cleanly?
2. Is K_strict nonempty in the structured substrate?
3. Is Viab(K_strict) sparse, zero, or too large?
4. Where does the filter ladder collapse, if it collapses?
5. Is Capture(K_strict) nonempty?
6. Do perturbation recovery rates vary by perturbation type?
7. Do strict-preserving transitions differ in future-space contraction?
8. Do null controls reproduce the strict object?
9. Is the substrate too permissive, too dead, or appropriately resolving?
10. Should RFS0 proceed to refinement, or should the substrate be redesigned?
```

## Interpretation guide

### Ideal first signal

```text
K0 large
K_strict smaller
Viab(K_strict) sparse nonzero
Capture(K_strict) nonempty
future-space contraction non-degenerate
controls do not trivially match structured substrate
```

Interpretation:

```text
RFS0 can resolve a sparse strict viable-futures object.
```

### Overfiltering

```text
K0 nonempty
K_strict zero or Viab(K_strict) zero everywhere
```

Interpretation:

```text
strict proxy may be too harsh or substrate lacks required recovery structure
```

Action:

```text
inspect filter ladder; do not simply loosen K_strict until success
```

### Trivial viability

```text
K0 large
K_strict large
Viab(K_strict) large
controls match structured substrate
```

Interpretation:

```text
substrate too permissive or filters too weak
```

### Dead substrate

```text
K0 small
K_strict zero
capture basin zero
```

Interpretation:

```text
not enough continuation structure
```

### Useful negative

```text
filter ladder identifies exactly which condition kills the object
```

Interpretation:

```text
substrate design can be revised with evidence rather than intuition
```

## Compute guidance

Use CPU.

Exact graph computation should be cheap at this scale.

Do not use GPU.

Do not add sampling unless exact computation becomes unexpectedly expensive.

If exact computation is expensive:

```text
reduce state dimensions
reduce horizons
reduce seeds
```

Do not switch to approximate estimators before obtaining one exact baseline.

## Implementation notes for Codex

### Suggested module shape

```text
omega/rfs0/__init__.py
omega/rfs0/substrate.py
omega/rfs0/exact.py
omega/rfs0/run_strict_batch.py
```

### Suggested implementation order

```text
1. Define finite state representation and enumeration.
2. Define neutral transformation families.
3. Build transition graph exactly.
4. Define K0..K_strict filters.
5. Implement reachable sets.
6. Implement finite-horizon viability kernel.
7. Implement capture basin.
8. Implement perturbation recovery metrics.
9. Implement contraction metrics.
10. Add controls.
11. Run 5-seed dev smoke.
12. Run full 150-system batch.
```

### Invariants

Preserve these:

```text
1. No Omega-positive labels in the generator.
2. K_strict is harsh and stated before results.
3. Lower filters are reported for diagnostics.
4. Recovery is exact graph capture into K_strict.
5. Controls are mandatory.
6. The summary must classify zero, sparse, large, and control-matched outcomes separately.
```

## What this batch can claim

If successful:

```text
A finite exact reachable-futures substrate can resolve a sparse strict
recovery-conditioned viable object under harsh formal filters.
```

If unsuccessful:

```text
The strict filters or substrate are not yet resolving the target object;
we can identify where the ladder collapses.
```

It cannot claim:

```text
Omega validation
alignment validation
constructor-level agency
pseudo-Omega fully operationalized
```

## Bottom line

RFS0 is the exact measurement floor.

This batch should tell us whether a minimal finite substrate can support a strict recoverable viable-futures object without relying on permissive viability, task-graph overgrowth, or outcome labels.
