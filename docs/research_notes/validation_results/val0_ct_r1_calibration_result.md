# VAL0-CT R1 Calibration Result

Positive calibration evidence for future-preserving reachability in constructor task algebras

## Status

This note records the current strongest VAL0-CT result.

It is a validation-result note, not a claim of full Omega validation.

Current status:

```text
VAL0-CT:
  positive calibration signal strengthened

R1:
  separates from equal-budget R0-lookahead in generated brittle/robust task algebras

Boundary:
  T = 64 exceeds current 64-task generator depth and collapses global LHR
```

Short claim:

> VAL0-CT now has positive calibration evidence that robust future-preserving reachability can outperform equal-budget greedy peak reachability in generated brittle/robust task algebras.

Important caveat:

> This is calibration evidence, not full Omega validation and not yet held-out generator generalization.

## Background

VAL0-CT tests a single-field proto-Omega precursor in constructor-style task space.

The operational distinction is:

```text
R0:
  raw reachability
  what is reachable?

R1:
  future-preserving reachability
  what is reachable that still leaves futures open?
```

The core comparison is:

```text
R1:
  robust future-preserving reachability selector

R0-lookahead:
  equal-budget greedy peak reachability control
```

The question is whether R1 can preserve long-horizon reachability better than an equal-budget control that simply maximizes peak future reachability.

## Run lineage

### Initial bounded smoke

The first bounded VAL0-CT smoke validated the harness and destructive-lock-in diagnostic, but did not distinguish R1 from R0-lookahead.

Primary read:

```text
harness:
  worked

destructive lock-in / pseudo-Omega:
  behaved as intended

R1 vs R0-lookahead:
  nearly indistinguishable
```

This motivated a targeted calibration pass focused on brittle-peak vs robust-plateau separation.

### Overnight attempt and harness hardening

A full overnight grid timed out before producing analyzable rows because the runner buffered rows until normal completion.

Harness fixes added afterward:

```text
streaming results.jsonl
checkpointed aggregate.csv
checkpointed summary.md
status.json
runner-owned wall-clock controls
graceful partial shutdown
interleaved job ordering
first-completed result collection rather than ordered executor.map
```

This converted long runs from all-or-nothing jobs into salvageable partial jobs.

### Safe breadth run

The safe breadth run completed normally and produced 21,000 condition rows.

Config summary:

```text
families:
  brittle_peak = 150 seeds
  structured_asymmetric_v2 = 100 seeds
  lock_in_seeded = 50 seeds
  low_resolution_dense = 50 seeds

h:
  1, 2, 4

H:
  4, 8

T:
  16, 32

workers:
  18

sample_size:
  256

max_paths:
  512
```

Primary result:

```text
brittle_peak:
  R1 mean global LHR = 0.471
  R0-lookahead mean global LHR = 0.383

structured_asymmetric_v2:
  R1 mean global LHR = 0.496
  R0-lookahead mean global LHR = 0.432

low_resolution_dense:
  R1 mean global LHR = 0.717
  R0-lookahead mean global LHR = 0.718

lock_in_seeded / pseudo_omega:
  mean global LHR = 0.213
  mean local LHR = 22.190
  pseudo-Omega flag rate = 1.000
```

Interpretation:

```text
R1 separated from R0-lookahead in brittle/robust generated families.
R1 did not spuriously separate in the low-resolution dense control.
Destructive lock-in replicated as local/global divergence.
```

Horizon dependence:

```text
R1 advantage appears mainly at h = 1 and h = 2.
At h = 4, same-choice rates rise and the R1/R0-lookahead difference mostly collapses.
```

This suggests the signal is not a generic R1 advantage. It appears when the near-term candidate horizon is short enough that greedy peak reachability and robust retention remain behaviorally distinct.

### H16 / T64 collapse-boundary run

A harder targeted run tested:

```text
H = 16
T = 64
h = 1, 2
```

Result:

```text
global LHR collapsed to zero across all families and policies
```

Interpretation:

```text
T = 64 is beyond the current generator depth for 64-task algebras.
This run is a generator-depth boundary diagnostic, not negative evidence against R1.
```

Do not use this run as an R1/R0-lookahead comparison. Use deeper generators or larger task algebras before retesting T = 64.

### H16 / T32 targeted confirmation

The strongest current run tested:

```text
H = 16
T = 32
h = 1, 2
```

This increased the continuation horizon while keeping the rollout horizon inside the current generator's nonterminal depth.

Primary result:

```text
brittle_peak:
  R1 mean global LHR = 0.539
  R0-lookahead mean global LHR = 0.189

structured_asymmetric_v2:
  R1 mean global LHR = 0.577
  R0-lookahead mean global LHR = 0.289

low_resolution_dense:
  R1 mean global LHR = 0.534
  R0-lookahead mean global LHR = 0.535

lock_in_seeded:
  destructive-lock-in diagnostic retained
```

Band-level result:

```text
brittle_peak, h = 1:
  R1 = 0.360
  R0-lookahead = 0.190

brittle_peak, h = 2:
  R1 = 0.719
  R0-lookahead = 0.188

structured_asymmetric_v2, h = 1:
  R1 = 0.412
  R0-lookahead = 0.313

structured_asymmetric_v2, h = 2:
  R1 = 0.742
  R0-lookahead = 0.265
```

Interpretation:

```text
This is the strongest current VAL0-CT calibration evidence that robust
future-preserving reachability can outperform equal-budget greedy peak
reachability in generated brittle/robust task algebras.
```

## What this result establishes

This result establishes:

```text
1. R1 can separate from equal-budget R0-lookahead in generated task algebras.

2. The separation appears in brittle_peak and structured_asymmetric_v2,
   not only in deterministic hand-built sanity cases.

3. The separation survives a harder continuation horizon H = 16 when rollout
   remains inside the current generator depth at T = 32.

4. Low-resolution dense controls remain matched, as expected.

5. Destructive lock-in / pseudo-Omega continues to show the expected
   local/global divergence pattern.
```

This is a real calibration milestone for VAL0-CT.

## What this result does not establish

This result does not establish:

```text
full Omega validation
alignment validation
valuerhood detection
multifield compatibility
lineage continuity
scale consistency
lushness proper
held-out generator generalization
physical Constructor Theory derivation
```

It also does not show that R1 is generically superior to reachability.

The correct claim is narrower:

> In generated brittle/robust task algebras, the current R1 selector can outperform an equal-budget greedy peak reachability selector on long-horizon reachability retention.

## Overfit risk

Overfit risk remains real.

The current positive families are deliberately shaped around the distinction VAL0-CT is trying to test:

```text
brittle_peak:
  high peak reachability with poor retention

structured_asymmetric_v2:
  generated asymmetry where some branches preserve future reachability better
```

This is acceptable for calibration, but not enough for a stronger validation claim.

Current overfit assessment:

```text
risk:
  medium-high

why not fatal:
  signal appears in randomized generated families, not only hand-built cases
  low-resolution dense remains matched
  destructive lock-in replicates separately
  horizon dependence is interpretable

next bar:
  held-out generator generalization
```

## Interpretation of horizon dependence

The current signal is horizon-sensitive.

Observed pattern:

```text
h = 1 or h = 2:
  R1/R0-lookahead separation appears

h = 4:
  same-choice rates rise and the distinction mostly collapses

T = 64:
  global LHR collapses across the current 64-task generators
```

Interpretation:

```text
R1 helps when short near-term candidate horizons make greedy peak reachability
misleading, while continuation horizon reveals retention differences.

When the candidate horizon is long enough, R1 and R0-lookahead may converge.
When the rollout horizon exceeds generator depth, all policies collapse.
```

This is not a defect by itself. It helps identify the regime where future-preserving reachability differs from greedy reachability.

## Recommended next validation step

The next validation run should not simply scale the same generators.

The next step is:

```text
VAL0-CT Held-Out Generator Generalization
```

Purpose:

> Freeze R1 and test whether the signal survives generator variation rather than only brittle_peak / structured_asymmetric_v2-style worlds.

Core requirements:

```text
freeze R1 selector
freeze R0-lookahead baseline
freeze diagnostics
freeze success criteria
```

Then vary generator structure:

```text
obstruction-based brittle failure
cost-inflation brittle failure
reliability-decay brittle failure
delayed-enabling robust paths
unlabeled structural generators
higher-depth generators for T = 64 retest
adversarial R1-looking but LHR-negative controls
```

The next result should report success by regime, not only global mean.

## Suggested project status line

Use this status line in summaries:

> VAL0-CT has positive calibration evidence that robust future-preserving reachability can outperform equal-budget greedy peak reachability in generated brittle/robust task algebras. The effect survives H=16,T=32, collapses at T=64 due to generator-depth exhaustion, and remains absent in the low-resolution dense control. This is not full Omega validation, but it is the strongest current proto-Omega calibration signal.

## Linked run artifacts

Primary run artifacts:

```text
results/val0_ct/20260518_safe_main_h4h8_t16t32/
results/val0_ct/20260519_h16_t64_boundary/
results/val0_ct/20260519_h16_t32_confirmation/
```

Use exact directory names from the repository if they differ from the above labels.

## Bottom line

VAL0-CT has crossed from harness validation into positive calibration.

The R1/R0-lookahead distinction is now visible in generated brittle/robust task algebras and survives a harder continuation horizon. The result remains scoped and vulnerable to generator-overfit, but it is a genuine milestone for the current proto-Omega validation path.
