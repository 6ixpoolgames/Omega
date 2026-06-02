# VAL0-G Neutral Grammar Stability Probe Result

Date: 2026-05-21

Status: complete.

Primary artifact:

```text
results/val0_g/20260521_neutral_grammar_stability_probe_cap2048/summary.md
```

Cap-512 comparison artifact:

```text
results/val0_g/20260521_neutral_grammar_stability_probe/summary.md
```

## Purpose

This probe audited the first VAL0-G neutral grammar smoke for forced-fit,
cap, signature-compression, and shallow-cut artifacts.

The grammar was frozen. No generator probabilities or class thresholds were
changed after seeing the stability run.

## Run Shape

Main cap-2048 run:

```text
neutral_grammar_v1:
  250 seeds

guardrails:
  low_resolution_dense: 50 seeds
  brittle_peak: 50 seeds

signature modes:
  coarse
  full

rows:
  700

errors:
  0

max_states_per_depth:
  2048

depths:
  1, 2, 4, 8, 16, 32
```

A matching cap-512 run was also retained for cap sensitivity.

## Main Readout

Family aggregate at cap 2048:

| family | n | survival AUC | mass d16 | mass d32 | P terminal d16 | P terminal d32 | initial cut | downstream cut | cap d16 | cap d32 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| brittle_peak | 100 | 605.394 | 2048.000 | 2045.760 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.990 |
| low_resolution_dense | 100 | 55.162 | 2048.000 | 2048.000 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| neutral_grammar_v1 | 500 | 286.230 | 1415.658 | 1080.990 | 0.369 | 0.650 | 0.547 | 0.673 | 0.676 | 0.500 |

Neutral full-signature bin counts at cap 2048:

```text
high_mass_high_cut_bin:
  145 / 250

high_terminal_bin:
  85 / 250

mixed_or_noise_bin:
  9 / 250

high_mass_low_cut_bin:
  6 / 250

high_branching_low_terminal_bin:
  3 / 250

depth_persistent_bin:
  2 / 250
```

Neutral full-signature cap rates:

```text
d16:
  0.676

d32:
  0.492
```

## Signature Audit

Coarse/full signatures agreed strongly:

| family | same class | same neutral bin | rel mass d16 diff | rel survival AUC diff | rel downstream cut diff |
|---|---:|---:|---:|---:|---:|
| brittle_peak | 1.000 | 1.000 | 0.000 | -0.001 | 0.000 |
| low_resolution_dense | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| neutral_grammar_v1 | 0.996 | 0.996 | -0.003 | -0.000 | 0.001 |

Interpretation:

```text
signature compression is not the dominant artifact in this probe.
```

The current coarse signature is acceptable for small probes, though full
signature should remain available until the atlas substrate is settled.

## Cap Audit

Increasing the cap from 512 to 2048 did not collapse the class/bin structure:

```text
cap 512, full signature:
  high_mass_high_cut_bin: 145
  high_terminal_bin: 85
  mixed_or_noise_bin: 9
  high_mass_low_cut_bin: 5
  depth_persistent_bin: 4
  high_branching_low_terminal_bin: 2

cap 2048, full signature:
  high_mass_high_cut_bin: 145
  high_terminal_bin: 85
  mixed_or_noise_bin: 9
  high_mass_low_cut_bin: 6
  high_branching_low_terminal_bin: 3
  depth_persistent_bin: 2
```

This is good for forced-fit risk.

But the high-mass bins remain heavily capped:

```text
neutral high_mass_high_cut_bin:
  cap_hit_d16: 1.000
  cap_hit_d32: 0.841

low_resolution_dense:
  cap_hit_d16: 1.000
  cap_hit_d32: 1.000

brittle_peak:
  cap_hit_d16: 1.000
  cap_hit_d32: 0.990
```

Interpretation:

```text
class existence is fairly stable,
but raw descendant mass is not yet trustworthy for high-mass classes.
```

The next runner should treat cap-hit high-mass rows as censored observations or
switch to sampled survival/filter-ratio estimates.

## Cut Audit

Initial and downstream cut sensitivity separate some bins:

```text
high_mass_low_cut_bin:
  initial cut:    0.364
  downstream cut: 0.173

high_terminal_bin:
  initial cut:    0.116
  downstream cut: 0.116

high_mass_high_cut_bin:
  initial cut:    0.828
  downstream cut: 0.995

mixed_or_noise_bin:
  initial cut:    0.243
  downstream cut: 0.932
```

Interpretation:

```text
downstream cut adds information, but the current implementation still samples
task removal coarsely. It is useful enough to keep, not mature enough to be a
primary ontology claim.
```

## Guardrails

Dense and brittle guardrails are not yet semantically clean:

```text
low_resolution_dense:
  identifiable as cap-saturated and cut-robust
  not cleanly labeled flat_dense by the current classifier

brittle_peak:
  cap-saturated and cut-robust at current measurement resolution
  not a good thin-ridge guardrail under VAL0-G metrics
```

This does not invalidate the neutral grammar result, but it means the guardrails
need revision before atlas scale.

## Conclusion

Minimal success passed:

```text
no errors
multiple neutral bins appeared again
cap-hit reporting works
coarse/full signature comparison works
downstream cut reporting works
```

Strong success partially passed:

```text
bin counts are stable under signature mode and cap increase
self-terminating rows remain high-terminal
high-mass/high-cut rows remain low-terminal and cut-robust
high-mass/low-cut rows remain distinguishable
```

Main unresolved issue:

```text
high-mass classes are still cap-censored at d16/d32.
```

## Recommendation

Do not run a full 1000-3000 seed atlas yet.

Run one more measurement-substrate probe first:

```text
keep grammar frozen
increase or replace capped enumeration
add cap-aware / sampled survival estimates
improve flat_dense and brittle/thin-ridge guardrails
keep neutral bins primary and interpretive labels secondary
```

The substrate is on the right object. The remaining risk is not obvious
fine-tuning; it is measurement censoring in high-mass regions.
