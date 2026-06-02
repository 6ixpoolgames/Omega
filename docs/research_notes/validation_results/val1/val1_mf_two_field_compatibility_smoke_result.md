# VAL1-MF Two-Field Compatibility Smoke Result

Date: 2026-05-21

Status: complete.

Primary artifact:

```text
results/val1_mf/20260521_two_field_compatibility_smoke_cap4096/summary.md
```

## Purpose

This was the first minimal multifield probe after VAL0-G. The intent was not to
validate Omega. It was to ask whether two neutral grammar fields with simple
cross-field effects could filter the reachable object enough to reduce the cap
censoring seen in single-field high-mass regimes.

The generator was kept deliberately small:

- two frozen `neutral_grammar_v1` fields;
- one valid action from either field per transition;
- minimal cross enable, obstruct, restore, commit, and shared-capacity effects;
- neutral compatibility bins primary, interpretive labels secondary.

No generator probabilities or bin thresholds were tuned after seeing the smoke
counts. An initial diagnostic run exposed a ratio-estimator bug; the estimator
was fixed before this result was interpreted, and the invalid diagnostic output
was not retained as a public artifact.

## Run Shape

```text
paired worlds:
  150

num_tasks per field:
  64

workers:
  18

max_states_per_depth:
  4096

rollout_samples:
  128

wall-clock cap:
  1800 seconds

elapsed:
  about 79 seconds

errors:
  0
```

## Main Readout

Aggregate:

| n | A filter | B filter | joint filter | compatibility | A divergence | B divergence | joint cap | joint terminal |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 150 | 0.677 | 0.672 | 0.967 | 0.967 | -0.289 | -0.295 | 0.947 | 0.055 |

Compatibility bins:

| neutral bin | n | joint cap | joint terminal | read |
|---|---:|---:|---:|---|
| `mixed_or_censored_bin` | 142 | 1.000 | 0.018 | dominant outcome; mostly not interpretable because joint enumeration hit cap |
| `mutual_collapse_bin` | 5 | 0.000 | 1.000 | real non-censored collapse cases |
| `joint_viable_bin` | 2 | 0.000 | 0.105 | rare non-censored viable cases |
| `uncoupled_parallel_bin` | 1 | 0.000 | 0.555 | rare non-censored parallel case |

Cap audit:

```text
mixed_or_censored_bin:
  A single cap d16: 0.718
  B single cap d16: 0.697
  joint cap d16:    1.000
```

The high aggregate compatibility ratio is therefore not a clean positive
signal. It mostly means the capped joint search filled its allowed budget.

## Interpretation

Minimal smoke success passed:

```text
the runner completed
checkpointed outputs were produced
joint metrics are nondegenerate
multiple bins appeared
cap censoring is surfaced directly
```

Strong success did not pass:

```text
the two-field construction did not reduce censoring
joint enumeration is more cap-prone than the single-field substrate
no broad A-dominant or B-dominant compatibility structure appeared
most rows are mixed/censored rather than interpretable compatibility regimes
```

The current multifield enumerator is therefore not yet the right scaled
measurement substrate. Conceptually, multifield compatibility remains relevant,
but naive joint-state enumeration multiplies the state space faster than the
minimal cross-effects filter it.

## Recommendation

Do not scale this exact two-field enumerator to a long atlas run.

The next multifield attempt should change the measurement method before
increasing compute:

```text
keep the neutral two-field generator frozen or nearly frozen
replace raw joint enumeration with sampled or cap-aware compatibility estimates
separate "cap-filled compatibility" from genuine survivable compatibility
promote non-censored joint_viable / mutual_collapse cases as audit examples
keep compatibility bins neutral and treat interpretive labels as provisional
```

This is a useful negative result. It says the project is interrogating a real
measurement bottleneck rather than simply increasing budget until a desired
shape appears.
