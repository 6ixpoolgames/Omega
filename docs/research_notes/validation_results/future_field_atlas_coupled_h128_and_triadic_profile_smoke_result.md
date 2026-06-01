# Future Field Atlas H128 Coupled Depth Gate And Triadic Profile Smoke

Status: coupled H128 depth gate passed in serial pair2; parallel pair4 exposed worker IPC limit  
Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`  
Triadic smoke runner: `omega.future_field_atlas.run_triadic_future_field_smoke`

## Summary

This pass pushed the coupled Future Field Atlas to H128 and added a small
three-frontier profile-only smoke. It was an infrastructure and manageability
pass, not a science run.

Allowed claim:

```text
The coupled atlas can complete a clean H128 pair2 depth gate with complete
topology-derived artifacts, passing reconstruction audits, and sharded raw
topology. A short profile-only triadic smoke also runs without emitting raw
triadic topology.
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

## Coupled H128 Pair4 Parallel Attempt

Local output:

```text
results/future_field_atlas/20260601_coupled_sharded_h128_pair4/
```

Readout:

```text
workers: 4
horizon_max: 128
pair_count_requested: 4
coupled_pairs_submitted: 4
coupled_pairs_completed: 2
coupled_pairs_failed: 2
elapsed_seconds: 651.267
finalization_seconds: 54.972
joint_node_rows: 266977
joint_edge_rows: 1737824
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
total_output_size: about 0.096 GiB
```

Two worker tasks failed:

```text
pair001: OSError(22, 'The parameter is incorrect', None, 87, None)
pair003: OSError(22, 'The parameter is incorrect', None, 87, None)
```

Read:

```text
The partial pair4 output is useful as an engineering signal, not as a clean
scale result. The failure is consistent with Windows multiprocessing IPC/result
transfer limits when a worker returns a very large CoupledProbeResult.
```

The runner was patched after this attempt so future runs report
`COMPLETED_WITH_ERRORS`, `coupled_pairs_failed`, and `error_count` when all
pairs are attempted but some fail. The medium-sweep readiness guard now also
sets `medium_sweep_interpretation_allowed = 0` when run errors are present.
The pre-patch local status JSON for this run says `COMPLETED`; the retained
note should be treated as authoritative for the pair4 read.

## Coupled H128 Pair2 Serial Depth Gate

Local output:

```text
results/future_field_atlas/20260601_coupled_sharded_h128_pair2_serial/
```

Readout:

```text
workers: 1
horizon_max: 128
pair_count_requested: 2
coupled_pairs_completed: 2 / 2
elapsed_seconds: 624.553
finalization_seconds: 402.605
joint_node_rows: 2078735
joint_edge_rows: 13570754
internal_cap_events: 0
artifact_completeness_statuses: complete
audit status counts: PASS 3
medium_sweep_interpretation_allowed: 1
total_output_size: about 0.746 GiB
```

Finalization dominated:

```text
flatten_rows: 7.992s
summaries_manifests_audits: 6.836s
raw_topology_shard_writes: 387.740s
parallel_artifact_writes: 0.037s
```

Pair skew was extreme:

```text
pair000:
  nodes: 24869 rows, about 0.86 MB compressed
  edges: 161388 rows, about 8.38 MB compressed

pair001:
  nodes: 2053866 rows, about 66.58 MB compressed
  edges: 13409366 rows, about 687.59 MB compressed
```

Horizon profile:

```text
H0: total states 4, max mode 1
H1: total states 26, max mode 9
H2: total states 160, max mode 81
H4: total states 1729, max mode 1365
H8: total states 13730, max mode 8265
H16/H32/H64/H96/H128: total states 17004, max mode 8613
```

Read:

```text
H128 depth is feasible on the desktop for a small number of coupled pairs.
The limiting factor is not CPU arithmetic. It is high-skew raw topology size,
worker result transfer, and shard write-out time.
```

## Output Manageability

The pair2 H128 serial result used about `0.746 GiB`. A naive pair-count
projection is unsafe because pair skew dominates. A rough planning envelope is:

```text
pair2 H128 serial observed: about 0.746 GiB
average pair implied by pair2: about 0.373 GiB
heavy pair observed: about 0.754 GiB by raw node/edge shards alone

pair12 H128 broad run:
  optimistic average projection: about 4.5 GiB
  conservative skew-aware planning envelope: about 8-10 GiB
```

Do not run a broad H128 parallel survey by returning full pair results through
Windows multiprocessing. Before broad H128, implement one of:

```text
worker-side spooling of per-pair raw rows to disk
pair-index targeting with known heavy pairs run serially
bounded H64 breadth plus selected H128 depth probes
dictionary/factorized raw topology with reconstruction tests
```

## Triadic Profile-Only Smoke

Implemented a deliberately small, non-monolithic triadic smoke layer:

```text
omega/future_field_atlas/triadic.py
omega/future_field_atlas/run_triadic_future_field_smoke.py
```

The smoke keeps raw topology out of scope and emits only profile-level
frontier counts and product-vs-triadic support residuals.

Local output:

```text
results/future_field_atlas/20260601_triadic_h6_profile_smoke_cap500k/
```

Readout:

```text
status: COMPLETED
elapsed_seconds: 6.277
horizon_max: 6
triple_count_completed: 1 / 1
profile_rows: 14
residual_rows: 7
internal_cap_events: 0
artifact_completeness_statuses: complete
total_output_size: about 4 KB
raw_topology_retention: not_emitted_profile_only_smoke
```

Terminal profile:

```text
product_baseline H6: 60830 joint states, density 1.0000
triadic H6: 9101 joint states, density 0.1496
terminal residual: 0.8504
```

An earlier H6 smoke with `max_internal_joint_frontier_states=50000` produced
one product-baseline cap event, so the no-cap H6 run used a `500000` internal
state cap. The triadic output should be read only as an interface and growth
probe.

## Validation

Passed:

```text
ruff check omega/future_field_atlas tests/test_coupled_atlas_hardening.py tests/test_triadic_future_field_smoke.py
python -m compileall omega/future_field_atlas tests
python -m pytest tests/test_coupled_atlas_hardening.py tests/test_triadic_future_field_smoke.py -q
git diff --check
```

Test result:

```text
10 passed
```

## Recommendation

Next engineering step:

```text
Add worker-side spooling or pair-indexed heavy-pair handling before any broad
H128 coupled survey.
```

Next research-infrastructure step:

```text
Use H64 breadth for coupled surface exploration and selected H128 serial depth
checks until raw topology write-out and worker result transfer are repaired.
```

Triadic branch:

```text
Keep triadic as profile-only until the two-frontier coupled path is stable.
Do not build full raw triadic topology yet; the H6 profile smoke already shows
that the product baseline grows quickly enough to require careful compression
and completeness semantics.
```
