# Future Field Atlas Glossary

Status: human reference only  
Scope: terminology, historical translation, and onboarding for the clean atlas branch

This document is not imported by the runtime. The clean atlas code should use
mathematical specs and operator fields, not historical treatment-arm names.

## Runtime Vocabulary

`StateSpaceSpec`
: Finite set of states the frontier can occupy. Current Phase 0/1 calibration
uses `Z3^5`, meaning five coordinates with three symbols per coordinate.

`TransformationLawSpec`
: Lawful local transition rule that generates candidate futures and scores
successor states. Current calibration uses the preservation-asymmetry energy
machinery as a narrow backend, not as an Omega claim. The invariant/asymmetry
engine belongs here: candidate successor rule, admissibility predicate, energy
function, invariant observable, preservation/asymmetry term, roughness term, and
seed policy.

`SelectionOperatorSpec`
: Mathematical rule selecting which ranked successors remain available from
each state. This is the native condition identity for the Future Field Atlas.

`ObservableSpec`
: Declares which raw or derived features are emitted from a scan. Current
observables include frontier topology, rank-boundary anatomy, and transport
matrices.

`FrontierScanSpec`
: Declares how reachable frontiers are unfolded and retained: expansion rule,
horizon schedule, horizon cap, and artifact retention policy.

`frontier`
: Set of states reachable at a horizon from a start state under a specified
law and selection operator.

`horizon`
: Discrete step count from the start state.

`candidate_rank`
: Rank of a candidate successor under the local transition energy. Rank `1` is
the lowest-energy candidate.

`rank_boundary_k`
: Calibration boundary used to compare retained rank sets against an observable
low-rank prefix. It is an instrument parameter, not a theory primitive.

`rank_offset_from_boundary`
: `candidate_rank - rank_boundary_k`. Nonpositive values are inside the current
calibration boundary; positive values are outside it.

`retained_rank_set`
: Candidate ranks retained by a deterministic selection operator.

`removed_rank_set`
: Candidate ranks removed by a deterministic selection operator.

`rank_prefix`
: Operator retaining ranks `1..m`.

`rank_subset`
: Operator retaining an explicit rank set from a base rank set.

`stochastic_rank_subset`
: Operator sampling a lower effective out-degree from the top-ranked candidate
set under a stable seeded policy.

`selection_operator_geometry_summary.csv`
: Primary Phase 0/1 calibration summary. It reports continuous operator and
rank-boundary geometry, not a boolean mechanism-recovery label.

`formal_spec_manifest.csv`
: Manifest of first-class formal specs with canonical JSON and stable digests.

`condition_identity_manifest.csv`
: Manifest tying each condition to state-space, transformation-law,
selection-operator, observable, frontier-scan, and seed identity.

`scan_manifest.csv`
: Manifest tying each concrete scan/start-state instance to condition identity
and formal spec digests. Bulk raw topology rows refer to this file instead of
repeating all spec metadata.

`reconstruction_audit_summary.csv`
: Audit file reporting whether derived atlas artifacts reconstruct from raw
rows and formal specs.

`artifact_completeness_summary.csv`
: Audit file reporting whether topology-derived artifacts are complete,
losslessly compressed, sampled, or truncated/non-interpretable.

`csv_output_mode`
: Runner storage mode for primary CSV artifacts. The default is `gzip`, so
logical artifacts such as `frontier_edges_by_step.csv` normally appear on disk
as `frontier_edges_by_step.csv.gz`. `plain` and `both` are available for local
debugging or compatibility, but gzip is the normal atlas storage posture.

`raw_topology_output_mode`
: Physical storage mode for the large raw node/edge topology artifacts. The
default is `sharded`: logical `frontier_nodes_by_horizon.csv` and
`frontier_edges_by_step.csv` are represented by shard manifests and
`part-*.csv.gz` shard files. `consolidated` writes the older single-file form;
`both` writes both layouts for compatibility checks.

`raw_topology_shard_pair_count`
: Coupled-runner shard parameter. It controls how many completed coupled pair
scans are packed into each physical raw-topology shard. The default physical
coupled layout is
`coupled_joint_frontier_nodes_by_horizon_shards/part-*.csv.gz` and
`coupled_joint_frontier_edges_by_step_shards/part-*.csv.gz`, with shard
manifests preserving logical artifact identity and row counts.

`finalization_timings_json`
: Status/manifest field reporting coarse timings for row flattening, transport
matrix construction, residual construction, audits, shard writes, and parallel
artifact writes. It is operational instrumentation, not a science metric.

`transport_output_mode`
: Controls how much non-adjacent transport is materialized. `adjacent_only`
emits adjacent transport only. `selected_multiscale` emits the current selected
milestone transport set. `full` emits the full horizon-pair closure and should
be used only for targeted audits.

`composition_residual_mode`
: Controls transport-composition residual audits. `none` skips them, `selected`
computes consecutive-milestone residuals, and `full` computes all available
closure residuals. Full residuals require full transport output.

`coupled`
: Runtime/public term for the two-frontier Future Field Atlas branch. The
current coupled probe compares product-baseline joint topology against a
coupled joint selector over the same product successors.

`product_baseline`
: Coupled-branch baseline that unfolds the cartesian product of A-field and
B-field selected successors.

`joint_vs_product_residual`
: Coupled-branch feature comparing coupled joint support against product
baseline joint support. It is a topology residual, not an interpretive label.

`marginal_retention`
: Coupled-branch feature reporting how much A and B marginal support remains in
the coupled joint frontier relative to the product baseline.

`substrate_morphology_summary`
: Postprocessing layer that maps retained Future Field Atlas outputs into
field, pair, operator-sensitivity, horizon-onset, observable-coverage, exemplar,
and next-target tables. It is an atlas over existing measurements, not a new
semantic detector or validation claim.

`CoupledOperatorSpec`
: First-class formal identity for the current coupled probe operator. It records
the product baseline definition, joint candidate set, joint energy function,
coupling term, coupling strength, joint selection family, effective out-degree,
stochastic flag, seed policy, canonical JSON, and stable digest.

`cap_poisoned_flag`
: Coupled-branch completeness flag. Once a product or coupled frontier is
internally capped, all later descendants from that mode are poisoned and must be
treated as `truncated_noninterpretable`.

`PASS_WITH_SKIPS`
: Reconstruction audit status meaning at least one complete row was checked,
zero checked rows failed, and at least one non-complete row was skipped.

`NO_COMPLETE_ROWS`
: Reconstruction audit status meaning all candidate rows were skipped because
none were complete. This is not a clean pass and blocks interpretation of that
artifact's coupled geometry.

`coupled_marginal_projection_delta_by_horizon.csv`
: Coupled-branch artifact comparing product and coupled marginal sets. It must
carry `projection_semantics = product_vs_coupled_marginal_set_delta` and
`causal_interpretation = none`.

`lossless_compressed`
: Artifact-completeness status reserved for topology represented by a
mathematically exact compressed form. The coupled branch has an optional
`lossless_blocks` audit mode for exact repeated-horizon blocks, but the H32
pair2 audit found no repeated exact topology. Future compression should remain
lossless and reconstructible, for example dictionary/factorized topology or
exact delta topology.

## Historical Translation

These names appeared in old notes and early smoke outputs. They should be read
as historical shorthand only.

| Historical phrase | Clean atlas expression |
|---|---|
| `baseline_m3` | `rank_prefix:m=3` |
| `baseline_m4` | `rank_prefix:m=4` |
| `baseline_m5` | `rank_prefix:m=5` |
| `drop_weakest_m4_to_core3` | `rank_subset:m=4:retain=1|2|3:remove=4` |
| `drop_two_weakest_m5_to_core3` | `rank_subset:m=5:retain=1|2|3:remove=4|5` |
| `drop_strongest_m4_to_m3` | `rank_subset:m=4:retain=2|3|4:remove=1` |
| `random_delete_one_m4_to_core3` | `stochastic_rank_subset:m=4:effective=3` |
| `random_delete_two_m5_to_core3` | `stochastic_rank_subset:m=5:effective=3` |
| `comField` | `coupled` |

## Public Language Guidance

Prefer:

```text
rank-boundary anatomy
selection operator
frontier topology
reachable-future geometry
transport composition residual
operator rank-boundary distance
```

Avoid as runtime terms:

```text
boundary_control
condition_role
known_mechanism_recovery
drop weakest
baseline arm
response-bearing condition
```

Those phrases can appear in historical notes when needed, but they should not
be schema fields, CLI options, or primary artifact names.

## Clean Slate Rule

If a future empirical result forces the theory to change, add or revise formal
specs first:

```text
StateSpaceSpec
TransformationLawSpec
SelectionOperatorSpec
ObservableSpec
FrontierScanSpec
```

Then add human-facing prose afterward. Do not add adapter names as runtime
identity.
