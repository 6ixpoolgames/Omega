# Probe DAX-G3 q=3/r=1 Phase Map Report

Date: 2026-05-14

Script:

- `scripts/historical_probes/probe_DAX_G3_q3r1_guardrailed_phase_map.py`

Result directory:

- `probe_DAX_G3_q3r1_guardrailed_phase_map_results/`

## Purpose

DAX-G3 tests whether q=3/r=1 contains a reproducible class of
control-adjusted primitive-positive motifs, or whether the G2b survivor was an
isolated accident.

## Run

- sampled rules: `2006`
- Stage 2 candidates: `225`
- Stage 1: `T=256`, ring `256`, `64` seeds
- Stage 2: `T=512`, ring `256`, `96` seeds
- workers: `18`
- runtime: about `48.5` minutes

A larger half-scale run hit the two-hour command cap, so the retained run uses a
stricter fallback while preserving q=3/r=1-only scope and active guardrails.

## Result

```text
q3r1_trunk_reproduced: true
strong_pass: false
guardrails_remained_clean: true
control_adjusted_positive_count: 9
relation_adjusted_positive_count: 161
asymmetry_adjusted_positive_count: 145
local_phase_fakeout_rejected_count: 99
non_emission_composition_positive_count: 25
remaining leaks: none
```

Best control-adjusted candidate:

```text
rule_id: q3g3_s1_00108
stratum: S1_random_unbiased
adjusted_persistence: 0.1303
relation_load_bearing_adjusted: 0.1193
asymmetry_load_bearing_adjusted: 0.1881
local_phase_fakeout_rejected: true
composition_adjusted_delta: 0.000
dominant_interaction_outcome: collapse
```

Reproduced G2b anchor:

```text
rule_id: q3r1_s1_0002
adjusted_persistence: 0.0167
relation_load_bearing_adjusted: 0.0744
asymmetry_load_bearing_adjusted: 0.1676
local_phase_fakeout_rejected: true
composition_adjusted_delta: 1.000
dominant_interaction_outcome: new_motif
```

## Interpretation

G3 passes: q=3/r=1 contains a reproducible guardrailed primitive-positive family.

It is not a strong pass. Several high adjusted-persistence rows are emission-only
or local-phase/self fakeouts once reclassified. Composition exists in the
candidate set, but it is not yet cleanly unified with the strongest persistence
and load-bearing rows.

## Recommendation

Proceed to:

```text
DAX-G4 q=3/r=1 motif ecology and mechanism anatomy
```

Keep q=3/r=1 as the trunk. Do not broaden rule space yet.
