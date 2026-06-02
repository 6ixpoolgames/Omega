# Future Field Atlas Transport Mode Timing Result

Status: operational timing/calibration pass completed  
Runner: `omega.future_field_atlas.run_future_field_atlas`

## Summary

This was an instrument-throughput pass, not a science result. We added explicit
transport and residual modes so large Future Field Atlas runs can choose how
much transport structure to materialize:

```text
--transport-output-mode adjacent_only | selected_multiscale | full
--composition-residual-mode none | selected | full
```

The default is now:

```text
--transport-output-mode selected_multiscale
--composition-residual-mode selected
```

This keeps adjacent transport, selected milestone multiscale transport, and a
small set of consecutive milestone composition checks. Full closure is still
available, but it is no longer the default.

## Smokes

Two H8 smokes passed:

```text
default selected mode:
  status: COMPLETED
  scans_completed: 8 / 8
  reconstruction_audit_passed: 1
  multiscale_transport_pair_count: 7
  composition_residual_triple_count: 3

adjacent-only/no-residual mode:
  status: COMPLETED
  scans_completed: 8 / 8
  reconstruction_audit_passed: 1
  multiscale_transport_pair_count: 0
  composition_residual_triple_count: 0
```

## H128 Timing Comparison

Both timing runs used:

```text
groups: 2
fresh_seeds_per_group: 2
start_samples: 1
conditions: 32
scans_completed: 32 / 32
horizon_max: 128
workers: 18
raw_topology_output_mode: sharded
gzip_compresslevel: 1
```

### Selected Multiscale

Local output:

```text
results/future_field_atlas/20260601_transport_modes_h128_timing_g2_fresh2_start1/
```

Run summary:

```text
status: COMPLETED
elapsed_seconds: 119.445
scan phase completed by elapsed_seconds: 5.643
frontier_node_rows: 153327
frontier_edge_rows: 2098158
total output size: about 66.6 MB
transport_output_mode: selected_multiscale
composition_residual_mode: selected
multiscale_transport_pair_count: 21
composition_residual_triple_count: 10
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
```

Finalization timings:

```text
flatten_rows: 0.059s
adjacent_transport_matrices: 1.610s
multiscale_transport_matrices: 75.394s
composition_residuals: 6.091s
summaries_manifests_audits: 4.050s
raw_topology_shard_writes: 22.170s
parallel_artifact_writes: 4.426s
```

### Adjacent Only

Local output:

```text
results/future_field_atlas/20260601_transport_modes_h128_adjacent_timing_g2_fresh2_start1/
```

Run summary:

```text
status: COMPLETED
elapsed_seconds: 33.948
scan phase completed by elapsed_seconds: 5.565
frontier_node_rows: 153327
frontier_edge_rows: 2098158
total output size: about 64.8 MB
transport_output_mode: adjacent_only
composition_residual_mode: none
multiscale_transport_pair_count: 0
composition_residual_triple_count: 0
reconstruction_audit_passed: 1
artifact_completeness_statuses: complete
```

Finalization timings:

```text
flatten_rows: 0.059s
adjacent_transport_matrices: 1.542s
multiscale_transport_matrices: 0.000s
composition_residuals: 0.000s
summaries_manifests_audits: 3.983s
raw_topology_shard_writes: 22.171s
parallel_artifact_writes: 0.627s
```

## Read

The previous write-out repair helped storage safety and observability, but this
pass confirms the larger runtime lever is transport materialization:

```text
selected_multiscale elapsed: 119.445s
adjacent_only elapsed: 33.948s
difference: about 85.5s
```

The selected-mode difference is mostly:

```text
multiscale_transport_matrices: 75.394s
composition_residuals: 6.091s
extra multiscale artifact write: about 3.8s
```

Raw topology shard writing is now visible and predictable at this scale:

```text
raw_topology_shard_writes: about 22.17s
```

That is meaningful, but it is not the dominant selected-mode bottleneck.

## Data Retention

Per the updated local policy, these timing/calibration outputs are retained
locally for a short grace period instead of being deleted immediately. They
should be removed by age-based cleanup unless explicitly promoted.

## Recommendation

Use the modes intentionally:

```text
adjacent_only + none:
  fast calibration and raw-topology instrumentation checks

selected_multiscale + selected:
  default medium calibration and pre-coupling checks

full + full:
  targeted audit only, because it is expensive
```

The next optimization target is not CSV writing. It is the multiscale transport
algorithm itself, if full or selected multiscale transport remains scientifically
load-bearing.
