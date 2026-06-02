# VAL1-MF Interference Audit Smoke Result

Date: 2026-05-21

Status: complete.

Primary artifact:

```text
results/val1_mf/20260521_interference_audit_smoke/summary.md
```

## Purpose

This probe was the follow-up to the first VAL1-MF two-field compatibility
smoke. The previous run showed that raw joint enumeration was mostly a cap
artifact. This run changed the question from descendant-mass enumeration to
counterfactual sampled interference:

```text
same generated pair
same starting fields
different coupling masks
measure sampled alive / terminal deltas
```

Raw joint enumeration is retained only as a diagnostic. Sampled deltas are the
primary readout.

## Run Shape

```text
paired worlds:
  100

num_tasks per field:
  64

rollout_samples:
  256

horizon:
  d16

workers:
  18

max_states_per_depth:
  2048 diagnostic only

elapsed:
  17.0 seconds

errors:
  0
```

## Main Readout

Aggregate sampled deltas:

| n | constructive | destructive | A harm | B harm | mutual support | cap any | low confidence |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 0.083 | -0.083 | -0.052 | -0.040 | 0.083 | 0.960 | 0.000 |

Mode summary:

| mode | A alive | B alive | joint alive | joint terminal | joint valid actions |
|---|---:|---:|---:|---:|---:|
| `uncoupled_parallel` | 0.833 | 0.833 | 0.734 | 0.068 | 14.815 |
| `full_coupling` | 0.885 | 0.873 | 0.816 | 0.058 | 15.983 |
| `cross_enable_only` | 0.868 | 0.860 | 0.787 | 0.060 | 15.596 |
| `cross_obstruct_only` | 0.834 | 0.830 | 0.731 | 0.066 | 14.638 |
| `cross_restore_only` | 0.869 | 0.856 | 0.787 | 0.062 | 15.395 |
| `cross_commit_only` | 0.837 | 0.833 | 0.735 | 0.066 | 14.761 |
| `shared_capacity_only` | 0.839 | 0.830 | 0.734 | 0.066 | 14.770 |

Neutral bins:

| neutral bin | n | read |
|---|---:|---|
| `constructive_delta_bin` | 22 | full coupling improved sampled joint alive probability |
| `A_local_dominance_bin` | 1 | one provisional asymmetric harm case |
| `no_detectable_interference_bin` | 77 | full coupling and uncoupled were similar at this horizon |

## Ablation Read

Mean joint-alive deltas against uncoupled:

| ablation | joint delta | A delta | B delta |
|---|---:|---:|---:|
| `enable` | 0.054 | 0.035 | 0.027 |
| `restore` | 0.054 | 0.036 | 0.023 |
| `obstruct` | -0.003 | 0.001 | -0.003 |
| `commit` | 0.001 | 0.003 | -0.000 |
| `shared_capacity` | 0.001 | 0.006 | -0.003 |

The signal is mostly constructive and is concentrated in cross-enable and
cross-restore masks. Cross-obstruct and cross-commit did not produce strong
destructive interference under the current neutral operator sampling.

## Interpretation

Minimal success passed:

```text
runner completed
same pairs were evaluated under multiple coupling masks
ablation modes produced non-identical sampled geometry
counterfactual deltas were non-degenerate
sampling confidence fields were reported
```

Stronger success partially passed:

```text
full coupling produced constructive and no-effect cases
cross-enable and cross-restore produced measurable support-like deltas
```

Stronger success did not fully pass:

```text
cross-obstruct and cross-commit did not produce clear destructive deltas
only one local-dominance candidate appeared
diagnostic enumeration still capped often, so descendant mass remains unusable
```

## Scientific Read

This is a better measurement substrate than the previous VAL1-MF enumerator.
The sampled counterfactual setup can detect cross-field effects without using
outcome labels and without treating cap-filled mass as evidence.

The object currently visible is support/recovery interference, not destructive
pseudo-Omega-like interference. That is useful but asymmetric:

```text
the toy can host measurable constructive compatibility dynamics
the current neutral cross-obstruct / cross-commit operators are too weak,
too rare, or not measured at the right horizon to expose robust destructive
interference
```

The one `A_local_dominance_bin` row should be treated as an audit example, not
as a result class.

## Recommendation

Do not scale this exact run shape into a long atlas yet.

Next probe should remain small and targeted:

```text
keep the counterfactual sampled-ablation framework
increase sensitivity to destructive interference without outcome-labeling
try d32 and/or stricter alive definitions
track valid-action loss and irreversible-disabled growth as secondary hazards
keep enable/restore constructive deltas as positive controls
```

This updates the roadmap: VAL1-MF now has a viable sampled interference
measurement pattern, but destructive-field filtering is not yet strong enough
for a broad validation run.
