# Probe DAX-G1 Targeted Report

Date: 2026-05-14

Script:

- `scripts/historical_probes/probe_DAX_G1_persistence_motif_anatomy_and_robustness.py`

Result directory:

- `probe_DAX_G1_persistence_motif_anatomy_and_robustness_results/`

## Purpose

DAX-G1 tested whether the DAX-G0 minimal-rule-space persistence signal was
actually identity-through-transformation, rather than frozen order, raw chaos,
collapse, or identity/shift triviality.

This is a diagnostic anatomy probe. It is not a validation of Omega as a theory.

## Run Configuration

- Candidates: G0 localized, transported-identity, and emitter/generator rules.
- Controls: collapse, frozen/orderly, chaotic, identity/shift/complement rules.
- Horizons: `T=256,512,1024`.
- Ring sizes: `256,512`.
- Initial-condition families: six G0 families plus two motif-focused seeds.
- Seeds: `256` per evaluation cell.
- Workers: `18` CPU workers.
- Runtime: about `16.7` minutes.

GPU was not used because the workload is ECA simulation plus motif/component
bookkeeping, not dense batched linear algebra.

## Main Result

Confirmed robust motif rules:

```text
169, 225, 73, 109
```

Top confirmed rule:

```text
rule: 169
motif_type: emitter
recurrence_up_to_shift: 0.769
material_turnover_rate: 0.246
background_contrast: 1.000
post_perturbation_survival_rate: 1.000
future_distinct_descendant_count: 236
frozen_order_index: 0.070
chaos_index: 0.266
```

Confirmed fractions:

```text
rule 169: 0.417
rule 225: 0.396
rule 109: 0.375
rule 73:  0.375
```

Control result:

```text
collapse controls rejected: true
frozen controls rejected: true
chaotic controls rejected: true
identity/shift controls rejected: true
```

## Sidecar Result

Recoverability:

```text
robust motif count: 15
best post-perturbation survival rate: 1.000
```

Primitive load-bearing:

```text
relation-dependence positive count: 10
asymmetry-dependence positive count: 7
```

Interaction/composition:

```text
composition-positive count: 0
best stable product rate: 0.000
```

## Interpretation

DAX-G1 supports the narrow claim that robust local persistence motifs exist in
the minimal ECA rule space and are not explained away by the main static,
chaotic, collapse, or identity/shift controls.

It does not support the stronger claim that the filtered motifs are cleanly
DAR-complete or DAR-asymmetric. After the anatomy filter:

```text
DAR-complete enriched: false
DAR-asymmetric enriched: false
relation-dependent enriched: true
asymmetry-dependent enriched: false
```

The strongest current read is therefore:

```text
robust individual persistence motifs are real;
relation-dependence remains weakly positive;
asymmetry and composition remain open.
```

## Recommendation

Proceed to DAX-G2 only as a phase-map/anatomy follow-up. The goal should be to
test whether relation/asymmetry load-bearing and composition reappear in richer
but still minimal rule spaces. Do not treat G1 as a theory validation.
