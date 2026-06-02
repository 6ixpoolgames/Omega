# RFS-MB0 Laptop Spectral Subspace Control Repair Smoke Result

Date: 2026-05-30

## Executive Summary

Decision: `not_ready_repair_required`.

Next action: `repair_shuffle_controls`.

The laptop sweep completed cleanly: 9/9 targeted sweep cases, 0 errors, 20/20
manifest outputs present, and no generated CSV/JSON artifacts committed. This
was an instrument-building run, not a validation run.

Structure-destroying controls did not pass. Across the widened aperture,
structure-shuffle matrix/statistic pass fraction was `0.3925` with catastrophic
fraction `0.51`. Every case-level runner still reported
`spectral_shuffle_controls_control_equivalent` with blocker
`structure_shuffle_controls_not_passed`.

The most important read is not "no signal"; it is "statistic mismatch plus
control-equivalence risk." Scalar statistics mostly failed, while
`top_k_subspace_alignment_to_baseline` separated almost everywhere. That makes
the instrument more incisive: baseline-alignment is sensitive, but too permissive
to rescue the channel while scalar structure controls remain weak.

Subspace transfer had non-null hints but did not clear the structure-control
gate. Overall subspace above-control fraction was `0.53`, but against the two
structure-destroying subspace controls specifically it was mixed rather than
decisive.

The spectral object is not cleanly item-local. Distributedness reads were:
`control_equivalent` 28, `distributed` 8, `diffuse_noise_like` 8,
`cluster_local` 5, and `item_local` 1.

Recommended next action: repair the shuffle/statistic instrument before any
graph perturbation. In particular, do not let the baseline-alignment statistic
override failed structure-shuffle scalar gates.

Artifact policy: local sweep outputs remain under `results/local_runs/` and are
not repository artifacts.

## Claim Boundary

This was a laptop-safe spectral-control and subspace diagnostic smoke.

It was not holdout validation, candidate promotion, Omega detection, agency
detection, identity detection, valuer detection, value detection, or graph-level
causal evidence.

Run counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## Runtime And Hardware Profile

Machine posture:

```text
local laptop hardware
workers: 7
job_batch_size: 2
thread caps: OMP/OPENBLAS/MKL/NUMEXPR/NUMBA = 1
```

Local output:

```text
results/local_runs/20260530_laptop_spectral_subspace_control_repair_sweeps_v2/
```

Status:

```text
status: COMPLETED
finalization_reason: all_cases_completed
elapsed_seconds: 39.009
cases_completed: 9 / 9
cases_failed: 0
errors: 0
manifest: 20 / 20 present
```

## Sweep Shape

The sweep widened the aperture across horizon, condition, item pool, and
selection/evaluation split balance:

```text
primary_middle
horizon_short
horizon_downstream
baseline_only_middle
resample_only_middle
asym_only_middle
lower_item_floor_middle
partition_40_middle
partition_60_middle
```

Each case used 5 shuffle replicates and 5 subspace-control replicates.

## Shuffle Failure Anatomy

Aggregate decision fields:

```text
structure_shuffle_matrix_pass_fraction: 0.3925
structure_shuffle_catastrophic_fraction: 0.51
decision_class: not_ready_repair_required
next_action_fork: repair_shuffle_controls
```

Horizon/family read:

```text
short context_shuffle:
  pass_fraction: 0.75
  catastrophic_fraction: 0.0417

middle context_shuffle:
  pass_fraction: 0.4605
  catastrophic_fraction: 0.4342

middle horizon_order_shuffle:
  pass_fraction: 0.2829
  catastrophic_fraction: 0.6382

downstream context_shuffle:
  pass_fraction: 0.375
  catastrophic_fraction: 0.5417

downstream horizon_order_shuffle:
  pass_fraction: 0.375
  catastrophic_fraction: 0.5833
```

Read:

```text
Failures are not just one bad probe or one condition. There is some context
heterogeneity, especially short-horizon context shuffle, but horizon-order
shuffle remains weak across the aperture.
```

## Statistic View

Scalar statistics failed the structure controls:

```text
positive_spectral_mass:
  context_shuffle pass_fraction: 0.36
  horizon_order_shuffle pass_fraction: 0.06

effective_rank:
  context_shuffle pass_fraction: 0.30
  horizon_order_shuffle pass_fraction: 0.12

participation_ratio:
  context_shuffle pass_fraction: 0.28
  horizon_order_shuffle pass_fraction: 0.02
```

Baseline-alignment separated:

```text
top_k_subspace_alignment_to_baseline:
  context_shuffle pass_fraction: 1.00
  horizon_order_shuffle pass_fraction: 1.00
  label_shuffle pass_fraction: 0.96
```

Read:

```text
This is the clearest instrumentation result. The instrument should not treat
baseline-alignment separation as sufficient by itself. It is sensitive, but too
permissive while scalar structure-destroying controls remain control-equivalent.
The next repair should build a non-tautological transfer/separation statistic
that does not simply reward observed-to-self alignment.
```

## Primary-Context Refinement

Recommendation counts:

```text
drop_for_now_due_to_control_equivalence: 46
keep_primary: 20
needs_more_replicates: 6
```

Promising but not sufficient contexts included:

```text
short context_shuffle:
  pass_fraction: 0.75
  catastrophic_fraction: 0.0417

constraint_violation_count_plus_local_tuple / constrained_window_flow /
small_edge_resample_control:p0.02 / middle / context_shuffle:
  pass_fraction: 0.95
```

Read:

```text
The aperture found islands worth preserving for later narrowing, but not enough
to claim the full structure-control layer works.
```

## Subspace Transfer Against Controls

Aggregate:

```text
subspace_above_control_fraction: 0.53
```

Control-family counts:

```text
label_shuffle:
  above_controls: 38
  control_equivalent: 12

context_shuffle:
  above_controls: 11
  control_equivalent: 39

horizon_order_shuffle:
  above_controls: 18
  control_equivalent: 31
  underpowered: 1

random_subspace_baseline:
  above_controls: 39
  control_equivalent: 10
  underpowered: 1
```

Read:

```text
Subspace transfer is non-null, but it is not strong enough against the
structure-destroying controls to override the failed shuffle gate.
```

## Distributedness Diagnostic

Distributedness v2 counts:

```text
control_equivalent: 28
distributed: 8
diffuse_noise_like: 8
cluster_local: 5
item_local: 1
```

Read:

```text
The object is not cleanly item-local. Most rows are control-equivalent under the
current instrument, with a minority of distributed or cluster-local hints.
```

## Optional Subspace Ablation Design Smoke

Not run.

Reason:

```text
Structure-destroying controls remain blocked. Subspace ablation should wait for
a cleaner non-tautological transfer statistic or a narrowed primary context.
```

## Decision Class

```text
not_ready_repair_required
```

## Next-Action Fork

```text
repair_shuffle_controls
```

Repair target:

```text
Separate statistic sensitivity from structure-control validity. Preserve the
full multi-stat anatomy, but do not promote baseline-alignment separation into a
pass criterion unless it is paired with structure-destroying controls that pass
on non-tautological transfer statistics.
```

## Output Manifest

Local-only output directory:

```text
results/local_runs/20260530_laptop_spectral_subspace_control_repair_sweeps_v2/
```

Key local files:

```text
spectral_shuffle_failure_anatomy_v2.csv
spectral_shuffle_failure_by_statistic.csv
spectral_shuffle_failure_by_case.csv
spectral_shuffle_failure_by_probe.csv
spectral_shuffle_failure_by_flow_mode.csv
spectral_shuffle_failure_by_condition.csv
spectral_shuffle_failure_by_horizon.csv
spectral_primary_context_recommendation.csv
spectral_subspace_control_alignment_v2.csv
spectral_subspace_distributedness_v2.csv
spectral_subspace_repair_report.md
spectral_subspace_repair_status.json
```
