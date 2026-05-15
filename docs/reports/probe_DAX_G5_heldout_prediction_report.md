# Probe DAX-G5 q=3/r=1 Held-Out Prediction Report

Date: 2026-05-15

Script:

- `probe_DAX_G5_q3r1_detector_freeze_heldout_prediction.py`

Result directory:

- `probe_DAX_G5_q3r1_detector_freeze_heldout_prediction_results/`

## Purpose

DAX-G5 freezes the q=3/r=1 DAR-persistence detector and asks whether G4 fertile
bands predict held-out primary positives better than matched controls.

## Freeze

Freeze and preregistration were written before held-out sampling:

- `probe_DAX_G5_q3r1_detector_freeze_heldout_prediction_results/detector_freeze.json`
- `docs/research_notes/primitive_branch/q3r1_detector_freeze_v1.md`
- `docs/research_notes/primitive_branch/q3r1_G5_preregistration.md`

The primary detector required:

```text
adjusted_persistence > 0
relation_load_bearing_adjusted > 0
asymmetry_load_bearing_adjusted > 0
local_phase_fakeout_rejected = true
reclassification == control_adjusted_positive
```

Composition was tracked only as a secondary signal.

## Run

- held-out rules: `5000`
- fertile rules: `3000`
- control rules: `2000`
- workers: `18`
- Stage 2 cap: `50` rules per band
- runtime: about `140.6` minutes

## Result

```text
heldout_prediction_passed: false
fertile_primary_positive_count: 7
control_primary_positive_count: 4
fertile_primary_positive_rate: 0.00233
control_primary_positive_rate: 0.00200
fertile_vs_control_enrichment: 1.17x
fisher_exact_greater_p: 0.533
control_leak_count: 4
```

Band positives:

```text
F1 G4 top S1 random-unbiased: 2 / 1000
F2 high relation/asymmetry: 3 / 1000
F3 near-validation PRA: 2 / 1000
B1 S7 symmetric: 0 / 500
B2 S8 self-only: 0 / 500
B3 output-matched random: 0 / 500
B4 high-chaos/high-frozen barren: 4 / 500
```

Secondary composition:

```text
non_emission_composition_positive_count: 42
new_motif_persistent_count: 4
composition_overlap_with_primary_count: 0
```

## Interpretation

G5 is a useful negative result. The q=3/r=1 ecology is not imaginary: held-out
fertile bands did produce positives. But the frozen fertile-band hypothesis did
not predict positives better than controls at the required level, and the B4
barren band leaked.

The detector should not be modified inside G5 to rescue the result. The next
work should inspect B4 leaks against fertile positives mechanistically, or
define a narrower target that separates DAR-persistence from generic
high-future-distinct persistence.
