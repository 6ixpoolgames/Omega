# VAL0-CT Brittleness Sidecar Diagnostic Spec

Operationalizing perturbation-sensitive structured reachability

## Purpose

The current VAL0-CT calibration result shows that R1 can outperform equal-budget R0-lookahead in generated brittle/robust task algebras.

However, `brittle_peak` is still a generator label. To reduce overfit risk, brittleness should become a measured structural property of candidate branches and task repertoires.

This spec defines a lightweight brittleness diagnostic sidecar.

Important constraint:

> Brittleness is diagnostic only. Do not change R1, R0-lookahead, policies, or success criteria for the next held-out run.

The goal is to ask:

> Does R1 advantage track measured brittleness rather than merely named generator families?

## Canonical definition

```text
Brittleness is perturbation-sensitive structured reachability.
```

Expanded definition:

> A path, policy, task family, or trajectory is brittle when it opens or preserves a non-noise near-term repertoire, but that repertoire loses future-bearing reachability under small perturbations, modest horizon extension, cost/reliability stress, or adjacent path variation.

Brittleness is not low reachability.

Brittleness is not noise branching.

```text
noise branching:
  many apparent branches, little structured continuation to preserve

brittleness:
  structured reachability exists, but its continuation is fragile

robust/lush reachability:
  structured reachability exists and propagates under stress

destructive lock-in:
  local structure persists while broader future possibility collapses
```

## Why this matters

Without an operational brittleness measure, the claim remains:

```text
R1 wins in brittle_peak.
```

With a brittleness diagnostic, the stronger question becomes:

```text
Does R1 advantage increase when measured brittleness is high?
```

This directly supports the held-out generator generalization phase.

## 3P status

### Principled

Brittleness follows from the primitive stack:

```text
distinction:
  branches differ

asymmetry:
  perturbations or small path variations have unequal downstream effects

relation:
  continuation depends on causal structure across time

brittleness:
  structured reachability exists, but its continuation relation is fragile
```

### Parsimonious

The minimal definition is sufficient:

```text
perturbation-sensitive structured reachability
```

Do not turn brittleness into a new grand primitive.

### Predictive

Expected predictions:

```text
high structuredness + high perturbation sensitivity:
  R1 should tend to outperform R0-lookahead

low structuredness:
  classify as noise branching, not brittleness

high structuredness + low perturbation sensitivity:
  robust/lush reachability

local stability + global collapse:
  destructive lock-in
```

## Operational form

Use the following decomposition:

```text
brittleness_score = structuredness_score × perturbation_sensitivity
```

Where:

```text
structuredness_score:
  how much coherent downstream task structure the branch opens

perturbation_sensitivity:
  how much retained reachability collapses under small stress
```

## Candidate-level procedure

For a candidate path `p` from algebra state `A`:

```text
1. Apply candidate path:
     A_p = apply_path(A, p)

2. Compute unperturbed future reachability:
     base_R0 = R0(A_p, H)

3. Estimate structuredness:
     structuredness_score = estimate_structuredness(A_p, H)

4. Sample small stresses:
     s_1, ..., s_k

5. For each stress:
     A_ps = apply_stress(A_p, s_i)
     stressed_R0_i = R0(A_ps, H)

6. Compute stress retention:
     stress_retention = mean_i(stressed_R0_i) / max(1, base_R0)

7. Compute perturbation sensitivity:
     perturbation_sensitivity = 1 - stress_retention

8. Compute brittleness:
     brittleness_score = normalized_structuredness × perturbation_sensitivity
```

This is a sidecar calculation. It should not alter policy selection.

## Initial structuredness proxy

Do not overbuild structuredness in the first smoke.

Recommended first proxy:

```text
structuredness_score(p) = R0(A_p, H) × mean_downstream_depth(A_p, H)
```

If `mean_downstream_depth` is unavailable, use:

```text
structuredness_score(p) = R0(A_p, H)
```

but mark this as weak because it risks conflating structure with raw reachability.

Preferred later proxy:

```text
structuredness_score(p) =
  R0(A_p, H)
  × mean_downstream_depth(A_p, H)
  × coherence_score(A_p, H)
```

Where `coherence_score` measures whether reachable tasks form connected downstream structure rather than isolated leaves.

## Initial perturbation set

Start with cheap perturbations that already fit the task-algebra representation.

### stress_enabled_drop

```text
Remove one task from the enabled/reachable downstream set.
```

Purpose:

```text
test dependence on narrow enabled-task support
```

### stress_obstruction_add

```text
Add one obstruction from a completed or candidate-path task to one reachable downstream task.
```

Purpose:

```text
test whether small new obstructions collapse continuation
```

### stress_horizon_extension

```text
Compare R0(A_p, H) with R0(A_p, H + Δ)
```

Purpose:

```text
test horizon brittleness
```

Recommended Δ:

```text
Δ = 4 or 8
```

### Defer cost/reliability stresses

Do not include cost or reliability stresses unless the current generator and R0 implementation use cost/reliability meaningfully.

Deferred stresses:

```text
stress_cost_increase:
  multiply downstream reachable task costs by 1.1 or 1.25

stress_reliability_drop:
  multiply downstream reachable task reliability by 0.9
```

## Compute impact

Naive brittleness diagnostics are expensive.

If the diagnostic evaluates `k` stresses for every candidate path, the cost is roughly:

```text
baseline candidate evaluation:
  N candidate paths × 1 R0 computation

with brittleness sidecar:
  N candidate paths × (1 + k) R0 computations
```

For example:

```text
sample_size = 256
stress_samples = 8

approximate extra diagnostic cost:
  ~9× candidate R0 computations
```

Therefore, do not run full diagnostic coverage initially.

## Smoke-first implementation

Implement brittleness as a low-sample diagnostic smoke before adding it to held-out runs.

Recommended smoke grid:

```text
families:
  brittle_peak
  structured_asymmetric_v2
  low_resolution_dense

optional:
  lock_in_seeded

seeds:
  5-10 per family

h:
  1, 2

H:
  16

T:
  32

policies:
  R0-lookahead
  R1
  random optional

candidate sample for brittleness:
  32 paths

stress samples:
  4 per path

stress types:
  enabled_drop
  obstruction_add
  horizon_extension
```

The smoke should complete quickly and produce coherent diagnostics before any larger run.

## Expected smoke patterns

Expected qualitative results:

```text
brittle_peak:
  high structuredness
  high perturbation sensitivity
  high brittleness score

structured_asymmetric_v2:
  intermediate or mixed brittleness

low_resolution_dense:
  low meaningful brittleness;
  either low structure discrimination or low perturbation sensitivity

R0-lookahead selected paths:
  higher brittleness than R1 selected paths in brittle_peak

R1 selected paths:
  lower brittleness and higher retained LHR in brittle_peak
```

Key sanity check:

```text
R0lookahead_chosen_brittleness > R1_chosen_brittleness
```

in `brittle_peak` and possibly `structured_asymmetric_v2`.

If this pattern does not appear, the brittleness metric may not be measuring the intended property.

## Required result fields

Add these per-run or per-decision aggregate fields:

```text
brittleness_candidate_sample_size
brittleness_stress_sample_size
brittleness_stress_types

candidate_structuredness_mean
candidate_structuredness_max
candidate_stress_retention_mean
candidate_perturbation_sensitivity_mean
candidate_brittleness_mean
candidate_brittleness_max

R0lookahead_chosen_brittleness
R1_chosen_brittleness
chosen_brittleness_gap
```

Where:

```text
chosen_brittleness_gap =
  R0lookahead_chosen_brittleness - R1_chosen_brittleness
```

Add aggregate fields:

```text
mean_candidate_structuredness
mean_candidate_perturbation_sensitivity
mean_candidate_brittleness
mean_chosen_brittleness_gap
corr_brittleness_R1_advantage
```

## Primary analysis

The main analysis is not whether brittleness is high in a named family.

The main analysis is:

```text
Does measured brittleness predict R1 advantage?
```

Recommended derived variable:

```text
R1_advantage = R1_global_LHR - R0lookahead_global_LHR
```

Primary relationship:

```text
R1_advantage ~ measured_brittleness
```

Expected:

```text
low measured brittleness:
  R1 ≈ R0-lookahead

high structured brittleness:
  R1 > R0-lookahead

noise-like branching:
  no reliable R1 advantage
```

## Interpretation rules

Pre-register:

```text
brittle_peak high brittleness + positive chosen_brittleness_gap:
  brittleness sidecar is directionally coherent

low_resolution_dense high brittleness:
  suspicious; metric may be conflating density/noise with brittleness

R0lookahead_chosen_brittleness <= R1_chosen_brittleness in brittle_peak:
  metric may not be capturing the intended distinction

R1 advantage correlates with measured brittleness:
  supports using brittleness as an explanatory diagnostic

R1 advantage does not correlate with measured brittleness:
  current R1 wins may reflect generator-specific structure not captured by this diagnostic
```

## Guardrails

Do not:

```text
change R1 based on brittleness smoke results
make brittleness a policy objective yet
use brittleness to filter runs silently
claim Omega validation from brittleness diagnostics
interpret noise branching as brittleness
```

Do:

```text
report brittleness as a sidecar diagnostic
use it to classify regimes after generation
compare it against R1 advantage
use it to decide whether held-out generators are producing useful structure
```

## Integration with held-out generalization

If the smoke produces coherent data, include low-sample brittleness diagnostics in the held-out generalization run.

Recommended held-out diagnostic settings:

```text
brittleness_candidate_sample_size:
  32 or 64

brittleness_stress_sample_size:
  4

stress types:
  enabled_drop
  obstruction_add
  horizon_extension
```

Do not increase beyond this until runtime is profiled.

## Future extensions

After held-out generalization, possible extensions:

```text
cost brittleness:
  cost stress once cost_brittle is implemented

reliability brittleness:
  reliability stress once reliability_brittle is implemented

path-variation brittleness:
  adjacent candidate paths produce sharply different retained reachability

local/global brittleness:
  local repertoire is stable but global repertoire collapses

T64 brittleness:
  deeper generators test whether structure survives longer rollout horizons
```

## Final target

The brittleness sidecar should let future VAL0-CT reports say:

```text
R1 advantage tracks measured perturbation-sensitive structured reachability.
```

instead of merely:

```text
R1 wins in a generator named brittle_peak.
```

That is the reason this diagnostic matters.
