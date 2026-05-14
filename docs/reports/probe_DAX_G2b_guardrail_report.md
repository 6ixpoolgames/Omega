# Probe DAX-G2b Guardrail Report

Date: 2026-05-14

Script:

- `probe_DAX_G2b_control_adjusted_primitive_guardrail.py`

Result directory:

- `probe_DAX_G2b_control_adjusted_primitive_guardrail_results/`

## Purpose

DAX-G2b separates generic persistence from control-adjusted
relation/asymmetry/composition-bearing persistence. It repairs the failed G2
guardrail before any larger phase map.

## Run

- target rules: `50`
- matched controls: `765`
- scale: `T=512`, ring `256`, `128` seeds
- workers: `18`
- runtime: about `14.6` minutes

Matched controls included center-only, neighbor-removed, symmetrized,
symbol-phase-only, output-histogram-matched random, and stratum-matched null
rules.

## Result

```text
guardrail_passed: true
q3_control_leaks_resolved: true
control_adjusted_positive_count: 6
relation_adjusted_positive_count: 42
asymmetry_adjusted_positive_count: 30
local_phase_fakeout_rejected_count: 16
composition_adjusted_positive_count: 2
remaining_leaks: none
```

Clean q=3/r=1 survivor:

```text
rule_id: q3r1_s1_0002
stratum: S1_random_unbiased
adjusted_persistence: 0.0734
relation_load_bearing_adjusted: 0.0755
asymmetry_load_bearing_adjusted: 0.1686
local_phase_fakeout_rejected: true
composition_adjusted_delta: 1.000
dominant_interaction_outcome: new_motif
reclassification: control_adjusted_positive
```

Important demotion:

```text
rule_id: q3r1_s5_0016
relation_load_bearing_adjusted: 0.1475
asymmetry_load_bearing_adjusted: 0.1253
reclassification: emission_only
```

`q3r1_s5_0016` remains interesting for persistence and load-bearing
relation/asymmetry, but its interaction signal should not be counted as
composition yet.

## Interpretation

G2b changes the status of q=3/r=1. G2 was only a promising smoke because controls
leaked. G2b resolves that leak and leaves a clean q=3/r=1 survivor.

This still does not validate Omega. It says the next primitive-branch trunk
should be a focused q=3/r=1 guardrailed phase map, with composition tracked
separately from persistence.

## Recommendation

Proceed to:

```text
DAX-G3: q=3/r=1 guardrailed phase map
```

Do not broaden to q=4, Game of Life, neural encoders, agents, or COM/fiber
machinery in this branch.
