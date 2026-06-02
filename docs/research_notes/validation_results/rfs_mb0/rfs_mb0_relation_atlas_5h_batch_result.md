# RFS-MB0 Relation Atlas 5-Hour Batch Result

Date: 2026-05-23

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_RELATION_ATLAS_5H_BATCH_RUN_SPEC.md
```

Primary local result root:

```text
results/rfs_mb0_relation_atlas/
```

Primary summary:

```text
results/rfs_mb0_relation_atlas/5h_batch_summary.md
```

## Purpose

This batch used the action-generated relation atlas to map parameter trends,
increase n=5 sample size, target middle-regime parameter regions with fresh
seeds, test limited n=6 transfer, and stress window-level/null diagnostics.

The batch did not tune detector thresholds and did not promote local/window
candidates to scientific positives.

## Run Shape

The planned A-E stages completed, then an extra targeted n=5 extension was run
because the planned stages finished well under the 5-hour cap.

Total wall clock used:

```text
about 8367 seconds
about 2.32 hours
```

Total generated environments:

```text
1140
```

Total middle-regime environments:

```text
674
```

Total atlas gate passes:

```text
0
```

## Stage Results

Stage A:

```text
existing-run trend mining completed
```

Stage B broad n=5:

```text
environments: 200
middle-regime: 120
profiles: 33000
errors: 0
atlas gate passes: 0
elapsed: about 1254 seconds
```

Stage C targeted n=5:

```text
selected regions: 9
environments: 300
middle-regime: 162
profiles: 49500
errors: 0
atlas gate passes: 0
elapsed: about 2011 seconds
```

Stage D targeted n=6 transfer:

```text
environments: 40
middle-regime: 24
profiles: 9720
errors: 0
atlas gate passes: 0
elapsed: about 501 seconds
```

Stage E window/null stress:

```text
structured-candidate windows inspected: 200
promotion blocker: aggregate gate not passed
```

Stage C2 targeted n=5 extension:

```text
environments: 600
middle-regime: 368
profiles: 99000
errors: 0
atlas gate passes: 0
elapsed: about 4598 seconds
```

## Parameter Trend Read

Broad n=5 trends from Stage B:

```text
out_degree_target = 2:
  middle-regime rate about 0.725
  fast-saturation rate 0.000
  cycle rate about 0.088

reversibility_fraction = 0.25:
  middle-regime rate about 0.847
  underconnected rate 0.000
  fast-saturation rate about 0.042

update_footprint = 2:
  middle-regime rate about 0.634

constraint_density = 0.25 or 0.40:
  middle-regime rate about 0.646 and 0.639

constraint_strength = 1.0:
  middle-regime rate about 0.695

asymmetry_strength = 0.5:
  middle-regime rate about 0.655
```

The selected Stage C region file therefore emphasized:

```text
update_footprint: 2
out_degree_target: 2
constraint_density: 0.25
constraint_strength: 1.0
asymmetry_strength: 0.5
reversibility_fraction: 0.25
rewire_probability: 0.0
constraint_arity: 2
```

These are environment-shape associations only. They are not causal claims and
were not selected by detector-pass labels.

## Interpretation

The relation atlas is now useful as an environment calibration substrate.

The strongest operational finding is that middle-regime environments are
reproducibly generated under neutral parameter sweeps and targeted fresh seeds.
The strongest scientific finding remains negative: no generated environment
passed the aggregate atlas gate.

The n=6 transfer result is encouraging for substrate hygiene:

```text
targeted n=6 environments: 40
n=6 middle-regime environments: 24
```

This suggests at least some n=5 middle-regime parameter regions transfer to a
larger distinction space without immediate collapse or saturation.

Window-level candidates remain diagnostic only. Stage E inspected 200
structured-candidate windows, but the aggregate gate was still the promotion
blocker.

## Recommendation

Keep the relation-atlas branch and move next to confirmatory design:

- freeze a small set of environment-shape-selected parameter regions;
- run fresh-seed confirmatory n=5 and limited n=6 transfer;
- improve window/null stress reporting so separations are per-null, not only
  aggregate;
- keep `atlas_gate_pass_count` as the headline scientific gate.

Do not claim Omega validation, agency, identity, valuerhood, viability, or a
scientific gate pass from this batch.
