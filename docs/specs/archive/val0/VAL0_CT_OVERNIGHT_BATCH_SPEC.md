# VAL0-CT Overnight Batch Spec

Compute budget plan for the next 8-10 hour VAL0-CT calibration run

## Purpose

The first VAL0-CT smoke validated the harness and the destructive-lock-in diagnostic, but did not validate the R1 distinction. R1 and equal-budget R0-lookahead were nearly indistinguishable under the current generator families.

This overnight batch should therefore not simply scale the same smoke. It should be a targeted calibration run designed to answer:

> Can we construct and randomize task algebras where greedy peak reachability and robust future-preserving reachability diverge?

Specifically:

```text
R0-lookahead:
  selects brittle peak future reachability

R1:
  selects robust retained future reachability

Desired result:
  R1 and R0-lookahead choose different paths in structured cases,
  and R1 has better long-horizon reachability retention when the algebra
  contains brittle-peak / robust-plateau structure.
```

This remains a calibration batch, not a full Omega validation result.

## Budget allocation

Recommended 8-10 hour allocation:

```text
A. 1 hour:
  deterministic divergence tests

B. 5-6 hours:
  brittle_peak / robust_plateau generator sweep

C. 1-2 hours:
  lock_in_seeded confirmation + local/global audit

D. 30-60 minutes:
  aggregation, summary, and diagnostics
```

If time is limited, prioritize A and B. Do not spend the night scaling the original `structured_asymmetric` generator unless it has been revised to create peak-vs-robust divergence.

## A. Deterministic divergence tests

Before launching the full batch, run hand-built cases where the correct qualitative behavior is known.

### Required toy cases

#### Case 1: brittle peak

```text
start
  -> greedy_branch
      opens many immediate tasks
      downstream tasks mutually obstruct or terminate
      high max future_R0
      low mean retained reachability
      low LHR at T

  -> robust_branch
      opens fewer immediate tasks
      downstream tasks remain enabled and low-obstruction
      lower max future_R0
      higher mean retained reachability
      higher LHR at T
```

Expected:

```text
R0-lookahead chooses greedy_branch
R1 chooses robust_branch
R1 global_LHR > R0-lookahead global_LHR
```

#### Case 2: flat / low-resolution

```text
all branches preserve similar future_R0
```

Expected:

```text
R1 ≈ R0-lookahead
flat_asymmetry flag fires
```

#### Case 3: lock-in

```text
P-family self-enables
P-family obstructs non-P tasks
```

Expected:

```text
pseudo_omega policy increases local/P-family reachability
global_LHR falls
pseudo_omega_flag fires
```

#### Case 4: sparse collapse

```text
few branches exist
most terminate quickly
```

Expected:

```text
too_sparse or low-resolution flags fire
R1 differentiation is not expected
```

### Go / no-go criterion

Proceed to the overnight randomized sweep only if Case 1 produces actual R1/R0-lookahead divergence.

Minimum pass:

```text
same_choice_rate < 1.0 on the hand-built brittle-peak case
R1 chooses robust branch
R0-lookahead chooses greedy branch
R1 LHR > R0-lookahead LHR
```

If this fails, patch the R1 selector or candidate aggregation before running the full batch.

## B. Main generator sweep

The main batch should target generator families that create the exact separation geometry VAL0 needs.

### Required generator families

#### brittle_peak

Purpose:

```text
create paths with high peak future reachability but poor retention
```

Generator structure:

```text
brittle branch:
  high immediate enabling
  high downstream obstruction
  high variance across continuations
  high R1_best_future_R0
  lower R1_mean_future_R0
  lower LHR

robust branch:
  moderate immediate enabling
  low downstream obstruction
  lower R1_best_future_R0
  higher R1_mean_future_R0
  higher R1_fraction
  higher LHR
```

Expected:

```text
R0-lookahead often chooses brittle peak
R1 often chooses robust plateau
same_choice_rate < structured_asymmetric_v1
R1 global_LHR > R0-lookahead global_LHR when asymmetry is sufficient
```

#### structured_asymmetric_v2

Purpose:

```text
revise the current structured_asymmetric family so asymmetry affects retained reachability, not only immediate reachability
```

Generator structure:

```text
moderate branching
moderate obstruction
some branches brittle
some branches robust
nontrivial variance in future_R0 across candidates
```

Expected:

```text
R1/R0-lookahead divergence appears in a subset of seeds/horizons
asymmetry_score predicts divergence
```

#### lock_in_seeded

Purpose:

```text
confirm destructive-lock-in diagnostic and audit local/global ratios
```

Expected:

```text
pseudo_omega policy produces high local retention and low global LHR
pseudo_omega_flag rate remains high
local/global divergence is not a denominator artifact
```

#### low_resolution_dense

Purpose:

```text
negative calibration where R1 ≈ R0-lookahead is expected
```

Expected:

```text
R1_R0lookahead_same_choice_rate high
R1 ≈ R0-lookahead
low-resolution / too-dense flags fire
```

### Optional generator family

#### low_resolution_sparse

Only include if time permits.

Purpose:

```text
negative calibration where too little reachable structure exists for R1 to matter
```

Do not include `mixed`, `noise_branching`, R3/lushness, multifield coupling, or lineage in this overnight batch.

## Recommended run grid

### Primary grid

```text
families:
  brittle_peak
  structured_asymmetric_v2
  lock_in_seeded
  low_resolution_dense

num_tasks:
  64

num_constructors:
  2

seeds:
  brittle_peak: 150-250
  structured_asymmetric_v2: 100-200
  lock_in_seeded: 50-100
  low_resolution_dense: 50-100

h:
  1, 2, 4

H:
  4, 8, 16

T:
  16, 32, 64

policies:
  random
  R0
  R0_lookahead
  R1
  pseudo_omega

R1 sample size:
  256 candidate paths

max_paths:
  512 initially
```

### If runtime is too high

Cut in this order:

```text
1. reduce seeds for low_resolution_dense
2. reduce seeds for lock_in_seeded
3. drop T = 64
4. drop H = 16
5. reduce brittle_peak seeds only as a last resort
```

Do not cut the R0-lookahead policy. It is the critical matched baseline.

Do not cut the h/H sweep completely. Horizon dependence is part of the probe.

### If runtime is lower than expected

Add:

```text
num_tasks = 128 for brittle_peak only
R1 sample size = 512 for a confirmation subset
threshold sensitivity at 0.25 and 0.75 for a confirmation subset
```

## Required diagnostics before batch

Add these diagnostics before launching if possible. They are more valuable than simply adding seeds.

### R1/R0-lookahead divergence

```text
R1_R0lookahead_same_choice_rate
R1_R0lookahead_score_gap
R1_chosen_path_id
R0_lookahead_chosen_path_id
```

Most important:

```text
same_choice_rate
```

If R1 and R0-lookahead choose the same path almost always, the batch is still only harness calibration.

### Candidate distribution diagnostics

For each decision point or summarized over rollout:

```text
candidate_future_R0_max
candidate_future_R0_mean
candidate_future_R0_variance
candidate_future_R0_range
candidate_R1_fraction
candidate_obstruction_mean
candidate_obstruction_variance
```

### Chosen-path diagnostics

For the path selected by each policy:

```text
chosen_future_R0
chosen_future_R0_mean_context
chosen_future_R0_rank
chosen_R1_fraction
chosen_obstruction_count
chosen_enabled_count
chosen_lock_in_family_count
```

### Local/global audit

For lock-in diagnostics:

```text
local_R0_initial
local_R0_final
global_R0_initial
global_R0_final
local_LHR
global_LHR
local_global_divergence
P_family_reachability_initial
P_family_reachability_final
P_family_completed_count
```

This is required because the first smoke produced very large local LHR ratios in `lock_in_seeded`. The next run should verify that this is a real local/global split and not a denominator artifact.

## Required result fields

Add these fields to per-run JSONL if they are not already present:

```text
R1_R0lookahead_same_choice_rate
R1_R0lookahead_score_gap
candidate_future_R0_max_mean
candidate_future_R0_mean_mean
candidate_future_R0_variance_mean
candidate_future_R0_range_mean
candidate_R1_fraction_mean
chosen_path_obstruction_mean
local_R0_initial
local_R0_final
global_R0_initial
global_R0_final
P_family_reachability_initial
P_family_reachability_final
```

Add to aggregate CSV:

```text
mean_same_choice_rate
mean_score_gap
mean_candidate_future_R0_variance
mean_candidate_R1_fraction
mean_local_global_divergence
mean_P_family_reachability_delta
```

## Success criteria for this overnight batch

This is a calibration success if:

```text
1. Hand-built brittle-peak case separates R1 from R0-lookahead.

2. brittle_peak generator produces lower same_choice_rate than low_resolution_dense.

3. In brittle_peak, R1 has higher mean global_LHR than R0-lookahead
   in at least one nontrivial h/H/T band.

4. same_choice_rate and candidate_future_R0_variance explain where
   R1/R0-lookahead separation appears.

5. lock_in_seeded again shows pseudo-Omega local/global divergence,
   with absolute local/global R0 values confirming the ratio is not a denominator artifact.
```

## Failure / ambiguity criteria

### Expected diagnostic, not failure

```text
R1 ≈ R0-lookahead in low_resolution_dense
R1 ≈ R0-lookahead in flat_asymmetry cases
```

### Concerning result

```text
R1 ≈ R0-lookahead in hand-built brittle-peak case
```

This implies the selector or candidate aggregation is not actually capturing robust retention.

### Ambiguous result

```text
R1 separates in hand-built cases but not in generated brittle_peak
```

Interpretation:

```text
generator does not reliably produce separation geometry
or the generator parameters are too weak / too noisy
```

### Strong negative for current R1

```text
R1 separates from R0-lookahead but does not improve LHR in brittle_peak
```

Interpretation:

```text
R1 is measuring a different robust-retention property than the outcome
or LHR is not the right held-out outcome for this generator
```

## Summary expected after run

The summary should explicitly answer:

```text
1. Did deterministic brittle-peak hand tests pass?
2. What was R1_R0lookahead_same_choice_rate by family?
3. Did brittle_peak produce R1 > R0-lookahead on global_LHR?
4. Which h/H/T bands showed separation?
5. Did low_resolution_dense remain a collapse control?
6. Did lock_in_seeded confirm destructive-lock-in local/global divergence?
7. Were large local LHR ratios denominator artifacts?
8. What generator or selector change is next?
```

## Do not broaden tonight

Do not spend this batch on:

```text
multifield coupling
lineage
corridors
R3 / lushness
noise_branching
mixed generators
embodied agents
GPU acceleration
large task counts beyond small confirmation subsets
```

The current bottleneck is not scale. It is separation geometry.

## Final target

The overnight batch should determine whether VAL0-CT can produce a clean, equal-budget divergence between:

```text
greedy peak reachability
```

and:

```text
robust future-preserving reachability
```

If yes, the project has its first real proto-Omega signal in constructor-style task space.

If no, the next move is not bigger runs. It is revising R1 or the generator geometry.
