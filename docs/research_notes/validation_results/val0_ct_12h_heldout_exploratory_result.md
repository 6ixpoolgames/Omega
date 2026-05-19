# VAL0-CT 12-Hour Held-Out Exploratory Result

Status: exploratory result  
Date: 2026-05-19

## Purpose

This run tested whether the current R1 advantage generalizes beyond the original
designed brittle/robust calibration generators.

The run was intentionally 3P:

```text
principled:
  freeze R1 and compare against equal-budget R0-lookahead

parsimonious:
  no brittleness sidecar scaling, no T64, no multifield additions

predictive:
  ask whether held-out generator mechanisms preserve the R1 advantage while
  low_resolution_dense remains matched
```

## Main Run

Artifact:

```text
results/val0_ct/20260519_12h_heldout_exploratory/
```

Scope:

```text
families:
  unlabeled_structural = 150 seeds
  cost_brittle = 100 seeds
  delayed_robust = 100 seeds
  low_resolution_dense = 50 seeds
  lock_in_seeded = 50 seeds
  brittle_peak = 40 seeds
  structured_asymmetric_v2 = 40 seeds

h = 1, 2
H = 16
T = 32
workers = 18
sample_size = 256
max_paths = 512
rows = 5300
elapsed = 5477.0 seconds
status = completed
```

## Results

### Calibration Anchors

```text
brittle_peak:
  R1 = 0.547
  R0-lookahead = 0.176

structured_asymmetric_v2:
  R1 = 0.571
  R0-lookahead = 0.277
```

The known positive anchors reproduced strongly.

### Controls

```text
low_resolution_dense:
  R1 = 0.534
  R0-lookahead = 0.535

lock_in_seeded / pseudo_omega:
  global_LHR = 0.000
  local_LHR = 22.400
  pseudo-Omega flag rate = 1.000
```

The dense negative control remained matched, and the destructive-lock-in
diagnostic replicated.

### Held-Out Families

```text
cost_brittle:
  R1 = 0.576
  R0-lookahead = 0.664

delayed_robust:
  R1 = 0.614
  R0-lookahead = 0.740

unlabeled_structural:
  R1 = 0.398
  R0-lookahead = 0.440
```

The held-out families did not produce broad R1 wins.

## Unlabeled Structural Extension

Artifact:

```text
results/val0_ct/20260519_unlabeled_structural_extension/
```

Scope:

```text
unlabeled_structural = 300 seeds
h = 1, 2
H = 16
T = 32
rows = 3000
elapsed = 1682.5 seconds
status = completed
```

Combined with the main exploratory run, unlabeled structural showed:

```text
h = 1:
  mean R1 advantage = -0.057
  win rate = 0.23

h = 2:
  mean R1 advantage = -0.031
  win rate = 0.26
```

Variance-bin analysis:

```text
highest variance quintiles:
  h = 1 mean R1 advantage = -0.027, win rate = 0.309
  h = 2 mean R1 advantage = -0.006, win rate = 0.346
```

Candidate variance therefore looks relevant, but not sufficient. Higher
variance moves R1 toward parity with R0-lookahead, but does not produce a clean
mean R1 win.

## Interpretation

This is not a held-out generalization success.

The current best read is:

```text
R1 is strongly positive in designed brittle/robust calibration families.
R1 does not yet cleanly generalize across the current held-out generators.
Unlabeled structural variance is a promising surface for future probes.
```

`cost_brittle` and `delayed_robust` are currently better understood as
generator-debug surfaces than as successful held-out mechanisms.

## Decision

Do not claim positive held-out generator generalization yet.

Recommended next work:

```text
1. Focus on unlabeled_structural regime classification.
2. Define post-hoc peak-retention or terminal-depth classes without using them
   to tune R1.
3. Test whether R1 advantage appears specifically in structurally classified
   high peak-retention-gap regimes.
4. Keep cost_brittle and delayed_robust small unless their mechanisms are made
   more faithful without changing R1.
```

This is useful progress because it narrows the next scientific question:

```text
Can R1 advantage be predicted from measured task-space structure in unlabeled
generators, rather than from named generator families?
```

