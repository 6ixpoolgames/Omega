# RFS-MB0 Relation Atlas Audit Update Note

Status: branch update after detector, substrate, relation-atlas, null, start, roughness, and phenotype audits

Purpose: record what changed in the branch, what the audits found, and how the interpretation standards were corrected before the next path/process diagnostic run.

## 0. Executive summary

The branch has moved through several important phases:

```text
1. hand-named future-landscape substrate
2. detector overcall repair
3. horizon/null audit
4. neutral action-generated relation atlas
5. breadth/null-repair batches
6. control-taxonomy correction
7. candidate phenotype audit
8. relation-generator phenotype repair
```

The current read is:

```text
The relation generator is worth keeping.
The scientific gate has not passed.
The old roughness-artifact interpretation was too blunt.
The generator is constraint-dominated and produces recurring candidate-window phenotypes.
Most candidates in the latest repair pass are not start-fragile and not confirmed roughness artifacts.
The next live question is whether these phenotypes show real path/process structure beyond endpoint support and lightweight transition proxies.
```

## 1. Initial detector problem

The first future-landscape detector overcalled structure.

The original `structured_propagation` decision was too close to an absolute-threshold heuristic:

```text
entropy high enough
predictive proxy high enough
motif reuse high enough
not collapse
not cycle
```

This allowed random, degree-preserving, and coordinate controls to be classified as structured.

Main correction:

```text
separate local profile candidates from aggregate family/probe-family decisions
make structure classification control-relative
prevent local false positives from promoting aggregate claims
```

Result:

```text
local degree-control hits remained visible
aggregate degree-control passes dropped to zero
aggregate structured family count dropped to zero
scientific gate remained not passed, but for the correct reason
```

Interpretation shift:

```text
The detector became conservative enough to expose substrate/environment issues.
```

## 2. Horizon audit

Concern:

```text
Maybe the detector was ending too early or measuring only after saturation.
```

A long-horizon audit kept the same substrate and extended the horizon grid well beyond the original H16 window.

Result:

```text
Longer horizons did not rescue the hand-named substrate.
Fast saturation and underdetermined behavior persisted.
The previous negative result was not merely a horizon cutoff artifact.
```

Interpretation:

```text
The current hand-named substrate was not adequate for evidence-bearing work.
But the long-horizon machinery became a useful standard diagnostic layer.
```

## 3. Substrate hygiene correction

Problem:

Even after removing overt semantic labels, the substrate still contained hand-picked relation families:

```text
structured_relation
expanding_relation
contracting_relation
cyclic_relation
```

This still encoded expected roles.

Correction:

```text
replace hand-named positive/negative relation families with an action-generated neutral relation atlas
```

New substrate structure:

```text
finite distinction space X = A^n
local neighborhoods
local candidate transitions
seeded local constraints
action-like transition score
top-k outgoing relation edges
controlled asymmetry/reversibility/rewiring/roughness
matched nulls and environment-shape diagnostics
```

The new relation generator made relation/transformation explicitly load-bearing, rather than hiding it behind named regimes.

## 4. Action-generated relation atlas smoke

The first relation-atlas calibration smoke showed:

```text
neutral generator works
middle-regime environments are produced
hand-named positive families were removed
atlas gate pass count remained zero
```

Interpretation:

```text
This was not a scientific success, but it was a substrate-hygiene success.
The problem became one of parameter-regime cartography and candidate interpretation rather than semantic toy design.
```

## 5. Five-hour batch and breadth lesson

The broader relation-atlas batch emphasized phase-space cartography.

Findings:

```text
many middle-regime environments can be generated cheaply
n=5 trends partially transfer to n=6
local/window candidates appear
aggregate scientific gate remains zero
```

Important interpretation:

```text
Breadth matters more than raw state-space size at this stage.
The goal is a regime map: where do neutral relation substrates produce saturation, collapse, clocks, null mimicry, support deformation, local candidates, or reproducible process-like phenotypes?
```

## 6. Null-repair and control-taxonomy correction

The null-repair audits revealed a major interpretive bug:

```text
All controls/nulls were being treated as if they asked the same question.
```

Correction:

Controls are now separated into categories.

### 6.1 Triviality controls

```text
frontier_size_only
probe_marginal_only
frontier_size_plus_probe_marginal
```

These ask whether a candidate is explained by low-level endpoint/probe facts.

These are fair filters for stronger claims.

### 6.2 Support-level controls

```text
signature_support_matched
horizon_local_frontier_matched
window_local_frontier_matched
```

These ask whether the signal is mostly about which signatures/futures become reachable.

Failing these should not mean automatic rejection. It may indicate:

```text
support_deformation_candidate
```

### 6.3 Mechanistic ablations

```text
constraint_shuffled
asymmetry_shuffled
```

These disrupt the mechanisms that generate the relation landscape.

Meaningful candidates may be expected to die under these.

They should answer:

```text
Does the candidate depend on the specific local constraint/asymmetry geometry?
```

not:

```text
Can the candidate survive having its own substrate destroyed?
```

### 6.4 Strong graph/relation ablations

```text
degree_preserving_rewire
out_degree_preserving_random
```

Important correction:

Current `degree_preserving_rewire` is not a true directed in/out degree-sequence preserving rewire. It is closer to an out-degree-preserving random target rewire without replacement.

These are destructive relation ablations. They are useful to diagnose generic branching artifacts, but should not be treated as must-survive gates for relation-specific candidates.

### 6.5 Robustness perturbations

```text
multiple starts
roughness sweeps
small edge/constraint/asymmetry perturbations
presentation changes
```

These are graded robustness tests.

## 7. Ranked-null result and reinterpretation

The ranked-null run was stricter than deterministic nulls.

It showed that candidate windows often failed replicate-ranked degree/out-degree/constraint/asymmetry/roughness comparisons.

Original risk:

```text
interpret all failures as false positives
```

Corrected interpretation:

```text
Some failures indicate triviality weakness.
Some failures indicate mechanism dependence.
Some failures indicate destructive-ablation sensitivity.
Some failures indicate reproducibility problems.
They must not be collapsed into one survival table.
```

The strongest real worries after the ranked run were:

```text
start_samples was only 1
localized reproducibility was weak
roughness sensitivity was unresolved
endpoint/support and process nulls were mixed
candidate selection may have favored locally flashy windows
path/process diagnostics were missing
```

## 8. Candidate phenotype audit

A candidate phenotype audit was added to stop treating candidates as pass/fail objects and start classifying what kind of deformation they represent.

Required phenotype dimensions included:

```text
start coverage
triviality controls
support-level controls
constraint/asymmetry dependence
roughness response
out-degree ablation response
transition/process proxy
near-tie/roughness decisiveness
candidate phenotype class
```

The first sanity audit found:

```text
most candidates were basin-local or environment-level across start_samples 1, 3, 8
all rows were initially labeled roughness_brittle_artifact
score decomposition contradicted the roughness-artifact interpretation
```

The score audit showed:

```text
generator was constraint-dominated
roughness term was tiny
roughness-decisive edge fraction was modest
```

Interpretation:

```text
The old roughness label was overbroad. Roughness-resampled failure did not imply roughness-generated artifact.
```

## 9. Relation-generator phenotype repair

The next repair split roughness into:

```text
roughness response class
roughness edge sensitivity class
roughness strength profile class
confirmed roughness artifact flag
```

It also added roughness replay support and expanded score decomposition around selected, near-cutoff, and tail candidates.

Latest finding:

```text
candidate rows: 88
start coverage mostly environment-level or basin-local
constraint_dominated_roughness_sensitive: 62
roughness_edge_brittle_candidate: 25
confirmed_roughness_artifact: 1
noise_tolerant: 69
noise_sensitive_smooth: 9
roughness_strength_brittle: 10
```

This substantially repaired the previous interpretation.

Current read:

```text
roughness-resampled null sensitivity is common
confirmed roughness artifact is rare in this pass
most candidates are constraint-dominated, roughness-sensitive, but edge-stable/noise-tolerant
```

## 10. Constraint/score findings

The repaired audit found strong constraint dominance:

```text
constraint_term_dominance high
asymmetry_term_dominance low
roughness_term_dominance tiny
dominance_class = constraint_dominated
constraint_conflict_proxy_rate high
```

Interpretation:

```text
The generator is not roughness-driven.
It appears to be navigating conflicted local compatibility landscapes.
This may be the right kind of substrate to interrogate, but it needs path/process diagnostics.
```

Important caution:

```text
Constraint dominance does not validate anything by itself.
It only says the generator is producing structured compatibility pressure rather than random tie-break noise.
```

## 11. What changed in the branch

Major branch changes include:

```text
added detector v1/v1.1 control-relative aggregation
added long-horizon auditing
added action-generated relation generator
added neutral relation-atlas runner
added staged 5h batch runner
added null-repair and breadth diagnostics
added ranked null replicate handling
added candidate phenotype audit runner
added roughness replay support via roughness_seed
added roughness_sensitivity_summary.csv
expanded score-term decomposition
added per-environment top-k margin summaries
repaired roughness phenotype classification
```

Key interpretation changes:

```text
nulls are not one category
constraint/asymmetry shuffle failures are mechanism dependence, not automatic rejection
roughness resampling failure is not automatically roughness artifact
multiple starts are mandatory
candidate recurrence should be phenotype-level, not exact-window-level
support deformation is a valid lower-level phenotype, not a failed structured-propagation claim
path/process diagnostics are now the next bottleneck
```

## 12. Current claim boundary

Allowed:

```text
The action-generated relation generator remains worth keeping.
The branch now produces recurring candidate-window phenotypes in middle-regime environments.
Most candidate rows in the latest audit are not start-fragile and not confirmed roughness artifacts.
The generator is strongly constraint-dominated under the tested parameter regions.
The phenotype machinery is now less misleading about roughness.
```

Not allowed:

```text
Omega detected
agency detected
identity detected
valuer detected
viability detected
scientific gate passed
robust path/process object detected
```

## 13. Current bottleneck

The current bottleneck is no longer:

```text
Is the relation generator obviously garbage?
```

The current bottleneck is:

```text
Do the constraint-dominated, edge-stable/noise-tolerant phenotypes contain path/process structure beyond endpoint support and lightweight transition proxies?
```

That is the next run.
