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

`reconstruction_audit_summary.csv`
: Audit file reporting whether derived atlas artifacts reconstruct from raw
rows and formal specs.

`artifact_completeness_summary.csv`
: Audit file reporting whether topology-derived artifacts are complete,
losslessly compressed, sampled, or truncated/non-interpretable.

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
