# q3/r1 Detector Freeze v1

Probe: DAX-G5 q3/r1 detector freeze and held-out prediction.

Frozen detector name:

```text
q3r1_DAR_persistence_v1
```

Primary target:

```text
DAR-persistence motifs in q=3/r=1 cellular rule space.
```

Primary positive definition:

```text
adjusted_persistence > 0
relation_load_bearing_adjusted > 0
asymmetry_load_bearing_adjusted > 0
local_phase_fakeout_rejected = true
reclassification == control_adjusted_positive
```

Composition is tracked but not required for the primary claim.

Frozen held-out fertile bands:

- F1: G4 top fertile band, `S1_random_unbiased`.
- F2: high relation/asymmetry structural band.
- F3: near-validation PRA structural band.

Frozen held-out controls:

- B1: S7 symmetric controls.
- B2: S8 self-only controls.
- B3: output-distribution matched random q3/r1 rules.
- B4: high-chaos/high-frozen barren region.

Forbidden after freeze:

- detector metric changes;
- threshold changes;
- matched-control construction changes;
- candidate promotion changes;
- fertile/control band relabeling.
