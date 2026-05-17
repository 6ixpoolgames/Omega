# Probe DAX-G4 q=3/r=1 Motif Ecology Report

Date: 2026-05-15

Script:

- `scripts/historical_probes/probe_DAX_G4_q3r1_motif_ecology_mechanism.py`

Result directory:

- `probe_DAX_G4_q3r1_motif_ecology_mechanism_results/`

## Purpose

DAX-G4 explains the q=3/r=1 trunk found by G3. It does not broaden the rule
space and does not change the G2b/G3 guardrail definitions.

## Run

- analyzed rules: `225`
- source: full G3 Stage 2 candidate set
- new-motif persistence check: reused G3 Stage 2 T=512, ring=256, N=96
  measurements, exceeding the requested N=64 check
- runtime: about `6` seconds

## Result

```text
control_adjusted_positive_count: 9
motif_family_count: 11
all_core_invariants_count: 3
persistence_relation_asymmetry_count: 34
composition_overlap_count: 3
new_motif_count: 7
new_motif_persistent_count: 4
strong_persistence_composition_overlap_count: 0
```

The validation positives are not a single monolithic family. They split into
strong-persistence, weak-persistence, and composition-overlap families. A larger
near-validation group has persistence/relation/asymmetry without composition.

## Interpretation

G4 supports q=3/r=1 as a real primitive-branch motif ecology, not merely a
single survivor. The cleanest next detector target is persistence + relation +
asymmetry + local-phase rejection.

Composition is not dismissed: three validation positives overlap with
non-emission composition, and four new-motif outcomes persist under the reused
G3 Stage 2 check. But composition is sparse and does not align with the strongest
persistence band, so it should remain secondary.

## Recommendation

Proceed to:

```text
DAX-G5 detector freeze for q=3/r=1 persistence/relation/asymmetry
```

Track composition as a secondary branch. Do not use discovery-leaderboard rules
as validation evidence.
