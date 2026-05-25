# RFS-MB0 Probe Resolution Calibration Spec

Status: bounded next-run spec after path metric calibration smoke

Purpose: run one small probe-resolution calibration smoke to determine whether path metrics are uninterpretable because current probe families are too collision-prone. This is a bounded diagnostic step, not a new open-ended rabbit hole.

This spec follows:

```text
docs/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_SPEC.md
docs/RFS_MB0_PATH_PROCESS_DIAGNOSTIC_ADDENDUM_METRIC_CALIBRATION.md
docs/RFS_MB0_PATH_METRIC_CALIBRATION_SMOKE_TIGHTENING.md
```

## 0. Strategic framing

The previous path metric calibration smoke succeeded as a guardrail:

```text
matched controls were attached
promotion was disabled
fakeouts headed the report
all candidate rows remained descriptive
```

But it also showed that current path metrics are not interpretable under the dominant probe families:

```text
probe_collision_fakeout dominated
support_ceiling_fakeout dominated
mean probe_collision_rate was extreme
pairwise projection probes collapsed too much of the finite state space
```

The immediate bottleneck is therefore not:

```text
absence of path organization
```

but:

```text
insufficient probe resolution for path-language metrics
```

This run asks:

```text
Which neutral probe families, if any, provide enough resolution for path metrics to be meaningful without becoming identity-like overfits?
```

## 1. Hard boundary

This is a single bounded smoke.

Do not expand into a large probe-search project yet.

After this run, force a branch decision:

```text
A. medium-resolution probes reduce collision and discriminate candidates -> continue path calibration v2
B. path metrics remain fakeout-dominated -> downgrade path-process work and focus on support/distribution deformation taxonomy
C. only identity-like/full-state probes work -> pause path-process branch and write measurement-limits note
```

Do not add new theory machinery, cost economies, agent labels, identity labels, value labels, or viability labels.

## 2. Promotion remains disabled

No active `path_process_candidate` class in this run.

Allowed evidence levels:

```text
probe_resolution_descriptive
probe_resolution_pass
probe_resolution_fail_collision
probe_resolution_fail_support_ceiling
probe_resolution_pass_but_control_also_passes
probe_resolution_identity_like_only
path_descriptive
path_fakeout
underdetermined
```

If a row looks strong, write:

```text
would_promote_if_enabled = 1
promotion_blocked_by_probe_resolution_policy = 1
```

but do not promote.

## 3. Probe families to add or audit

Use only neutral, mechanically derived probes.

### 3.1 Existing low-resolution probes

Include existing probe families as baselines:

```text
coordinate
ordered_pair
unordered_pair if present
modular/equality signatures if present
```

These are expected to be collision-prone but provide continuity with prior runs.

### 3.2 Medium-resolution coordinate tuple probes

Add:

```text
coordinate_tuple_k3
coordinate_tuple_k4
```

Definition:

```text
signature = tuple of selected coordinate values
```

Selection should be mechanically generated:

```text
all contiguous ring-local coordinate windows of size k
or deterministic sampled coordinate subsets if all combinations are too many
```

Do not attach semantic labels to coordinates.

### 3.3 Composite multi-probe signatures

Add composite signatures built from multiple existing primitive probes:

```text
composite_pair_plus_single
composite_two_pairs
composite_local_window_plus_constraint_count
```

Definition:

```text
signature = tuple(probe_1(state), probe_2(state), ...)
```

Composites should be mechanically generated and capped to avoid exploding path alphabet.

### 3.4 Constraint-profile probes

Because the generator is constraint-dominated, add probes derived from generated constraint status.

Options:

```text
constraint_profile_full
constraint_profile_hash
constraint_violation_count
constraint_violation_count_plus_local_tuple
```

Definitions:

```text
constraint_profile_full:
  vector of satisfied/violated generated constraints for the state

constraint_profile_hash:
  stable hash or bucketed encoding of the profile

constraint_violation_count:
  total number or weighted sum of violated constraints
```

Important:

```text
constraint-profile probes are mechanism-proximal.
They are allowed as diagnostic probes, but must be reported separately from coordinate-only probes.
```

### 3.5 Relation-role probes

Add simple relation-derived probes:

```text
out_degree_bucket
in_degree_bucket
reciprocity_bucket
local_reachability_bucket_depth1
local_reachability_bucket_depth2
```

These help test whether path metrics are mostly graph-role artifacts.

They should be treated as diagnostic controls, not primary evidence probes.

### 3.6 Strict-state resolution controls

Add strict controls:

```text
full_state_strict
full_state_hash
```

These are not evidence probes.

They are resolution ceilings.

Interpretation:

```text
If only full_state_strict/full_state_hash clears collision and produces path separation,
then lower probes are too lossy or the signal is representation-specific.
```

Do not promote candidates based only on strict-state probes.

## 4. Probe-resolution diagnostics

For every probe family and path row, compute:

```text
probe_signature_alphabet_size
observed_signature_support_size
observed_signature_support_fraction
probe_collision_rate
effective_signature_count
unigram_entropy
unigram_entropy_ceiling
entropy_ceiling_fraction
bigram_possible_count
bigram_observed_count
bigram_observed_fraction
trigram_possible_count
trigram_observed_count
trigram_observed_fraction
```

Add probe class:

```text
too_coarse
usable_low_resolution
usable_medium_resolution
high_resolution_control
identity_like_control
overfit_or_identity_like
```

Suggested initial classification:

```text
too_coarse:
  probe_collision_rate >= 0.90 or effective_signature_count too small

usable_low_resolution:
  0.75 <= probe_collision_rate < 0.90 and support not at ceiling/floor

usable_medium_resolution:
  0.40 <= probe_collision_rate < 0.75 and support not at ceiling/floor

high_resolution_control:
  0.10 <= probe_collision_rate < 0.40

identity_like_control:
  probe_collision_rate < 0.10 or signature almost uniquely identifies states
```

Thresholds are diagnostic defaults, not theory claims.

## 5. Path metric rerun by probe family

Run path metric calibration separately by probe family.

Do not aggregate across probe families before fakeout classification.

For each row:

```text
environment_id
row_kind: candidate / matched_control / same_environment_window_control
probe_family
probe_resolution_class
path_horizon
start_samples
path_count
bigram_MI
trigram_context_MI
predictive_gain_bigram_context
path_motif_reuse_rate
endpoint_null_rank
unigram_null_rank
candidate_minus_control
candidate_control_effect_size
fakeout_class
path_evidence_level
```

## 6. Matched controls remain mandatory

Every candidate row must have matched middle-regime non-candidate controls.

If no matched control exists:

```text
descriptive_only_no_matched_control
```

and the row cannot be stronger than descriptive.

Matching should include:

```text
parameter region
out-degree target
constraint density
constraint strength
asymmetry strength
reversibility fraction
roughness strength
probe family
path horizon
start_samples
```

## 7. Low-outdegree/path-count controls

Add low-outdegree/path-count matched controls or report why unavailable.

For each row, report:

```text
effective_branch_factor
sampled_path_count
unique_path_count_proxy
frontier_size_by_H
path_count_matched_control_id
path_count_match_quality
```

This is required because low out-degree makes path predictability cheap.

## 8. Resolution curve

For each candidate/control pair, output a probe-resolution curve:

```text
existing_low_probe -> k3_tuple -> k4_tuple -> composite -> constraint_profile -> relation_role -> full_state_strict
```

Report:

```text
probe_family
probe_collision_rate
observed_support_fraction
candidate_minus_control
endpoint_null_rank
unigram_null_rank
fakeout_class
path_evidence_level
```

Interpretation:

```text
signal appears only at low resolution:
  likely fake recurrence / collision artifact

signal appears only at full-state resolution:
  likely identity-like or representation-specific

signal appears at medium resolution and separates from controls:
  promising for path calibration v2

signal appears equally in controls:
  metric too generic

no signal at any resolution:
  path metrics not useful for this candidate/regime
```

## 9. Outputs

Required outputs:

```text
probe_resolution_calibration_report.md
probe_resolution_by_family.csv
path_metric_by_probe_family.csv
candidate_control_probe_matrix.csv
probe_resolution_curves.csv
probe_fakeout_summary.csv
probe_collision_diagnostics.csv
low_outdegree_path_count_controls.csv
status.json
```

Optional:

```text
probe_family_examples.json
strict_state_control_summary.csv
constraint_profile_probe_summary.csv
relation_role_probe_summary.csv
```

## 10. Final report requirements

The final report must answer:

```text
Which probe families are too collision-prone?
Which probe families are identity-like controls?
Are there any usable medium-resolution probes?
Do candidate/control differences persist at medium resolution?
Do candidate/control differences vanish when probe collision is reduced?
Do matched controls show the same path metrics?
Are path metrics mostly explained by low out-degree/path count?
Should path metrics be kept, tightened, or deferred?
Which branch decision is recommended: A, B, or C?
```

## 11. Suggested smoke shape

Keep the run small.

Suggested:

```text
candidate environments: 6-10
matched controls: 6-10
start_samples: 3
path_horizons: 4, 8
sample_paths_per_start: 256
path_null_replicates: 3
probe families: existing low, k3, k4, composite, constraint-profile, relation-role, full-state control
workers: 18
queued jobs: at least 18
wall clock: 20-60 minutes
promotion_enabled: false
```

If runtime is extremely cheap, add:

```text
start_samples: 8
path_horizon: 12
more matched controls
```

but do not scale into a broad atlas yet.

## 12. Decision gate after this run

After this run, make one of three decisions.

### A. Continue path calibration v2

Criteria:

```text
at least one non-identity-like medium-resolution probe reduces collision
candidate/control separation remains visible
fakeouts are not dominant
matched controls do not also pass
```

Next action:

```text
run path calibration v2 with those probes, still promotion cautious
```

### B. Downgrade path-process, focus support/distribution taxonomy

Criteria:

```text
path metrics remain fakeout-dominated
but support/distribution deformation remains reproducible
```

Next action:

```text
stop chasing path-process for now
write support/distribution deformation taxonomy
map generator regimes that produce those phenotypes
```

### C. Pause empirical branch / write measurement-limits note

Criteria:

```text
only identity-like probes work
or all interpretable signals vanish under matched controls
or every metric becomes calibration artifact
```

Next action:

```text
write measurement-limits note
reassess whether this empirical route is too under-instrumented
```

## 13. Claim boundary

Allowed:

```text
Probe family X is too collision-prone for path metrics.
Probe family Y is usable medium-resolution under this calibration.
Path metrics are or are not discriminative after probe-resolution controls.
```

Not allowed:

```text
path-process object detected
Omega detected
agency detected
identity detected
valuer detected
viability detected
scientific gate passed
```

## 14. Bottom line

This is a bounded probe-resolution smoke.

Do not dig indefinitely.

Run it once, then make a branch decision.
