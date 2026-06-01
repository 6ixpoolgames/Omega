# Future Field Atlas Coupled H64 Broad Sweep Result

Status: completed cleanly  
Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

## Summary

This pass fills the missing breadth gate before further H128 work. The earlier
coupled H64 gate was only pair2. This run expands to H64 pair8 with sharded
raw topology and the current coupled infrastructure guards.

This is still an infrastructure and manageability run, not a science result.

Allowed claim:

```text
The coupled atlas completed a broader H64 pair8 sweep with complete artifacts,
no caps, no run errors, passing reconstruction audits, and manageable but
skewed sharded output.
```

Blocked claims:

```text
interaction
compatibility
support
capture
erasure
agency
identity
value
valuerhood
Omega validation
```

## Run

Local output:

```text
results/future_field_atlas/20260601_coupled_sharded_h64_pair8_broad/
```

Configuration:

```text
horizon_max: 64
horizon_schedule: dense
pair_count: 8
groups: 8
workers: 4
artifact_write_workers: 8
raw_topology_output_mode: sharded
raw_topology_shard_pair_count: 1
csv_output_mode: gzip
gzip_compresslevel: 1
joint_effective_out_degree: 4
coupling_strength: 0.25
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta: 0.10
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 1182.177
coupled_pairs_completed: 8 / 8
coupled_pairs_failed: 0
joint_node_rows: 3231039
joint_edge_rows: 22127782
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
total_output_size: about 1.21 GiB
```

Finalization remained the dominant cost:

```text
flatten_rows: 8.530s
summaries_manifests_audits: 70.096s
raw_topology_shard_writes: 720.585s
parallel_artifact_writes: 0.201s
finalization_seconds: 799.430s
```

## Shard Skew

Edge rows by pair shard:

```text
pair000:   78828
pair002:  755316
pair004:  665609
pair006:  679489
pair007:  676574
pair005: 6379696
pair001: 6348438
pair003: 6543832
```

Node rows by pair shard:

```text
pair000:   12229
pair002:  116828
pair004:  103008
pair006:  105066
pair007:  104060
pair005:  808383
pair001:  977674
pair003: 1003791
```

Largest compressed shards:

```text
edge part-00007: about 335.37 MB
edge part-00006: about 325.49 MB
edge part-00005: about 322.26 MB
node part-00007: about 32.41 MB
node part-00006: about 31.69 MB
node part-00005: about 26.41 MB
```

Read:

```text
Broad H64 is operationally safe at pair8 on the desktop. The bottleneck is not
completion or reconstruction. It is skewed raw edge output and write time.
```

## Relation To H128

Compared with the H128 pair2 serial depth gate:

```text
H64 pair8 broad:
  output: about 1.21 GiB
  edges: 22.13M
  elapsed: 19.7 min
  finalization: 13.3 min

H128 pair2 serial:
  output: about 0.746 GiB
  edges: 13.57M
  elapsed: 10.4 min
  finalization: 6.7 min
```

H64 breadth gives the better near-term surface-area probe. H128 should stay
targeted until worker-side spooling or heavy-pair handling is implemented.

## Recommendation

Use this as the current breadth baseline:

```text
H64 pair8 broad, sharded, gzip level 1, workers 4
```

Next engineering repair:

```text
worker-side spooling of heavy pair outputs
```

Next possible empirical move:

```text
H64 pair8 or pair12 breadth with varied coupling strength / operator settings,
plus selected H128 serial depth checks on the most informative pair classes.
```

Do not run broad H128 in parallel yet.

