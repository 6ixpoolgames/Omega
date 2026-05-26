# RFS-MB0 Boundary Resolution Sweep Partial Result

Date: 2026-05-27  
Spec: `C:\Users\paolo\Desktop\Echo\Omega\Handoff files\Codex handoff 38.txt`  
Runner: `omega/rfs_mb0_future_landscape/run_deformation_detector_sweep.py`  
Output: `results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep/`

## Claim Boundary

This is a boundary-resolution audit for the neutral relation substrate. It does
not claim Omega, agency, value, identity, viability, path-process detection, or
scientific-gate passage.

## Execution Status

This run used `18` workers. The runner checkpointed outputs successfully, but
the external command wrapper interrupted the process before the runner could
mark final status as complete. Treat the result as a large partial run, not a
fully completed batch.

```text
status in status.json: RUNNING
workers requested: 18
anchors selected: 6
sweep jobs requested: 5440
sweep jobs completed at checkpoint: 3790
sweep rows completed: 187560
rank/effect rows: 39424
errors: 0
wall clock at checkpoint: 14114.8 seconds
```

The intended `--anchors 10` request selected only `6` anchors because the
source repair-smoke atlas exposed six boundary anchors.

## Headline

The boundary-focused sweep found real transition structure, but it did not
resolve the main blocker.

```text
candidate-like rows: 44388
non-saturation candidate-like rows: 44388
probe-recurrent bands: 0
fresh-seed recurrent variant groups: 28
stable candidate bands: 0
saturation audit rows: 76467
probe-resolution audit rows: 78427
```

Transition counts:

```text
candidate_stable_region: 9
candidate_to_fakeout_transition: 23
fakeout_to_candidate_transition: 9
probe_resolution_boundary: 9
saturation_boundary: 46
```

Required-answer provenance:

```text
candidate_stable_local_neighborhoods_generalized: false, 0 / 6
fakeout_to_candidate_transition_graph_count: true, 9 / 96
fakeout_to_candidate_band_level_count: true, 4 / 6
fakeout_to_candidate_fresh_seed_recurrent_count: true, 28 / 96
n6_transfer_completed: false
```

## Interpretation

The run supports continuing MB0 boundary work, but not promoting a stable
candidate band.

What improved:

```text
fakeout-to-candidate transitions recur
fresh-seed recurrent boundary groups are present
candidate-like behavior appears outside the simple saturation-ceiling label
```

What did not improve:

```text
stable candidate bands remain zero
probe recurrence remains zero across selected bands
saturation/probe-resolution boundaries still dominate the audit surface
n=6 transfer is still not justified
```

## Recommendation

Do not run n=6 yet.

Next useful MB0 pass should be smaller and more surgical:

```text
1. select only the fakeout-to-candidate fresh-seed recurrent variant groups
2. run explicit cross-probe recurrence repair on those rows
3. use an internal runtime cap at least 10 minutes shorter than the command timeout
4. only consider n=6 if one n=5 band clears cross-probe recurrence and remains non-saturation-limited
```

If cross-probe recurrence remains zero after that repair, the next artifact
should be a measurement-limits note rather than a larger sweep.

