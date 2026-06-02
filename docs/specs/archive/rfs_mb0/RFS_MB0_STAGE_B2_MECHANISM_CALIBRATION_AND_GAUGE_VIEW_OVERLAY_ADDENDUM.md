# RFS-MB0 Stage B-2 Spec Addendum: Desktop Validation and Control Naming Discipline

Status: addendum to `docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_MECHANISM_CALIBRATION_AND_GAUGE_VIEW_OVERLAY_SPEC.md`
Scope: corrections after desktop Phase B / Stage A / Stage B validation and implementation-risk review
Claim boundary: no holdout, no candidate promotion, no Omega detection, no agent detection, no identity detection, no valuer detection

## 0. Why this addendum exists

The base Stage B-2 spec was written after the laptop Stage B mechanism smoke. Since then, desktop validation of the regenerated Phase B full-control path, read-only Stage A syndrome audit, and Stage B mechanism-control smoke has completed.

This addendum corrects the Stage B-2 background and tightens the most important implementation-risk rule:

```text
If the intended generator-level mechanism cannot be isolated cleanly,
the runner must name the proxy honestly and report what was actually preserved.
```

Naming discipline matters more than producing a positive-looking dependency score.

## 1. Desktop validation supersedes laptop-only interpretation

The base spec's background should be read as laptop-smoke context only.

The current strongest result is the desktop Phase B / Stage A / Stage B validation.

Desktop validation summary:

```text
Phase B regenerated full controls:
  jobs_completed: 1120 / 1120
  metric_rows: 134400
  control_rows: 13165111
  stage_a_control_value_rows: 13163988
  errors: 0
  holdout_scoring_count: 0
  phase_c_ready: 0
  decision_class: phase_c_blocked_no_recurrence

Stage A syndrome audit:
  syndrome_component_rows: 940800
  marginal_control_replicates: 500
  decision_class: syndrome_smoke_joint_positive_above_marginal_controls
  stage_b_allowed: 1

Stage B mechanism smoke:
  jobs_completed: 4480 / 4480
  metric_rows: 376320
  component_score_rows: 2822400
  errors: 0
  holdout_scoring_count: 0
  n6_run_count: 0
  alphabet_expansion_count: 0
```

The correct high-level read is:

```text
The syndrome branch is stronger than the marginal-recurrence branch.
Stage A found preregistered joint signed syndromes above marginal-preserving controls.
Stage B remains mechanism-control underdetermined because many controls are too destructive.
Holdout remains blocked.
```

## 2. Corrected syndrome status

The base spec says SYN_B and SYN_D were not measurable in the limited Stage B design. That was true for the earlier laptop smoke, but is no longer the current desktop result.

Corrected desktop Stage B status:

```text
SYN_A_low_growth_high_bottleneck_low_offdiag:
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.02857142857142857
  max_mechanism_dependency_score: 1.0

SYN_B_high_turnover_high_offdiag_high_window_delta:
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.08684895833333334
  max_mechanism_dependency_score: 0.14242878560719646

SYN_C_low_growth_high_concentration_low_entropy:
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.03549107142857143
  max_mechanism_dependency_score: 1.0

SYN_D_high_turnover_high_entropy_low_bottleneck_control:
  decision_class: control_too_destructive_underdetermined
  baseline_syndrome_rate: 0.03850446428571429
  max_mechanism_dependency_score: 0.4753623188405797
```

Stage B-2 should therefore treat:

```text
SYN_A and SYN_C:
  primary stabilizing / bottleneck / concentration syndromes

SYN_B and SYN_D:
  secondary turnover / diffusion / contrast syndromes
```

SYN_B and SYN_D are now measurable enough to report, but they should not dominate Stage B-2 runtime unless their interpretability improves under preservation-first controls.

## 3. Corrected non-destructive dependency read

The desktop Stage B non-destructive controls were limited to:

```text
roughness_resampled_transform_control p0.01
asymmetry_flip_sweep_control p0.01
asymmetry_flip_sweep_control p0.02
```

The most informative non-destructive dependency rows were:

```text
SYN_C roughness p0.01:
  baseline 0.03549 -> control 0.02422
  dependency 0.31761

SYN_C asymmetry p0.02:
  baseline 0.03549 -> control 0.02467
  dependency 0.30503

SYN_A asymmetry p0.02:
  baseline 0.02857 -> control 0.01987
  dependency 0.30469

SYN_A roughness p0.01:
  baseline 0.02857 -> control 0.01998
  dependency 0.30078
```

This updates the laptop-only read. The desktop run no longer supports the simple statement that gentle asymmetry leaves the signal unchanged. Instead:

```text
both gentle roughness and gentle asymmetry-flip controls can reduce SYN_A/SYN_C rates;
this is still not clean generator-level mechanism attribution;
the controls remain topology-level unless implemented and named otherwise.
```

## 4. Control identity contract

Every Stage B-2 mechanism control must report what it intended to test and what it actually tested.

Required fields in every mechanism-control manifest row:

```text
intended_control_name
actual_control_name
control_family
control_variant
proxy_level
intended_mechanism
actual_intervention
preserved_fields_json
changed_fields_json
unpreserved_fields_json
preservation_failure_reason
allowed_interpretation_level
```

Allowed `proxy_level` values:

```text
exact_mechanism_control
near_mechanism_proxy
generation_level_proxy
topology_level_proxy
presentation_level_control
not_available
```

Allowed `allowed_interpretation_level` values:

```text
mechanism_specific_interpretation_allowed
mechanism_proxy_interpretation_only
topology_sensitivity_only
presentation_sensitivity_only
underdetermined_due_to_destructiveness
not_interpretable
```

## 5. Naming discipline rules

A control name must describe the actual intervention, not the hoped-for interpretation.

### 5.1 Roughness naming

Use:

```text
roughness_seed_resample_generation_control
```

only if the implementation actually preserves the intended generator conditions except the roughness seed/path.

Minimum preservation expectation:

```text
same RelationParams except roughness seed/path;
same constraint set or explicitly preserved constraint metadata;
same asymmetry weights or explicitly preserved bias metadata;
same candidate-successor construction;
same post-generation reversibility and rewire settings unless declared otherwise.
```

If these are not preserved, use an honest proxy name such as:

```text
roughness_generation_proxy_control
roughness_seed_proxy_control
small_edge_resample_control
edge_roughening_control
```

Do not infer roughness-term dependence from `small_edge_resample_control` or `edge_roughening_control`. Those controls support only topology-sensitivity or edge-fragility interpretations.

### 5.2 Asymmetry naming

Use:

```text
asymmetry_strength_sweep_control
```

only if the implementation actually varies the generator's asymmetry strength while preserving other generator conditions well enough for interpretation.

Use:

```text
bias_weight_resample_generation_control
```

only if fresh bias weights are the intended and actual change, and other relevant fields are preserved or reported.

Use:

```text
asymmetric_edge_flip_control
```

for post-hoc realized-edge direction flips.

Do not infer generator-level asymmetry dependence or independence from asymmetric edge flips alone.

### 5.3 Constraint naming

Use:

```text
constraint_assignment_local_shuffle_control
```

only if actual constraint assignments are locally shuffled while preserving count/type/arity/strength distribution.

Use:

```text
constraint_residue_jitter_control
```

only if preferred residues are jittered while count/type/arity are preserved.

Use:

```text
constraint_weight_jitter_control
```

only if weights are jittered while assignments and residues are preserved.

Use:

```text
constraint_resampled_generation_proxy
```

when the system is regenerated with resampled constraints rather than locally perturbing the realized constraint structure.

Do not call a generation-level proxy a shuffle.

## 6. Interpretation gates

Stage B-2 reports must enforce these gates.

```text
Exact mechanism controls:
  may support mechanism-specific sensitivity claims if non-destructive or mildly destructive.

Near-mechanism proxies:
  may support mechanism-proxy interpretation only.

Generation-level proxies:
  may support broad generation-sensitivity interpretation only.

Topology-level proxies:
  may support edge/topology sensitivity or fragility interpretation only.

Presentation-level controls:
  may support presentation/probe sensitivity interpretation only.

Destructive controls:
  may support only underdetermined or too-destructive classes.
```

No proxy may be silently promoted to exact mechanism evidence.

No destructive-control result may be used as a positive or negative mechanism conclusion.

No mechanism-control result may imply agent, valuer, identity, or Omega detection.

## 7. Stage B-2 priority order after desktop validation

Stage B-2 should prioritize:

```text
1. control identity / naming discipline;
2. non-destructive preservation-first mechanism ladders;
3. SYN_A/SYN_C primary mechanism read;
4. SYN_B/SYN_D secondary contrast read;
5. entropy-flow-horizon gauge overlay;
6. corridor / trap / fakeout provisional classification;
7. decision on whether a full RFS-MB0G gauge-coherent shadow spec is warranted.
```

Do not increase seeds until the control identity contract and preservation audit are working.

Do not open holdout.

## 8. Updates to the gauge overlay interpretation

The desktop result strengthens the case for the gauge overlay because Stage A now shows joint syndromes above marginal-preserving controls.

However, Stage B also shows why gauge transformations must be preservation-aware:

```text
A cross-view or mechanism-dependent shadow is meaningful only if the view/control transform preserves enough substrate for comparison.
```

The entropy-flow-horizon overlay remains diagnostic.

It should ask:

```text
Do the selected syndromes show coherent residual structure as:
  entropy / shape;
  flow / transport;
  horizon / consequence?
```

It should not claim:

```text
gauge-coherent shadow validated
agent-shadow detected
future-shaping source identified
```

## 9. Required report addendum section

The Stage B-2 final report must include a section titled:

```text
Control identity and proxy discipline
```

It must answer:

```text
Which controls were exact mechanism controls?
Which were near-mechanism proxies?
Which were generation-level proxies?
Which were topology-level proxies?
Which were too destructive?
Which interpretation levels were allowed for each?
Were any intended controls downgraded to proxy names at runtime?
```

If any intended exact mechanism control cannot be implemented cleanly, the report must say so directly and use the downgraded actual control name in all decision tables.

## 10. Bottom-line correction

The base Stage B-2 spec remains directionally correct, but its background should be updated by this addendum:

```text
Stage A is now stronger than the laptop context implied:
  preregistered joint signed syndromes separate from marginal-preserving controls
  on regenerated desktop Phase B rows.

Stage B is also broader:
  all four selected syndromes are measurable in the desktop run.

But the mechanism layer remains underdetermined:
  most controls are too destructive,
  and current roughness/asymmetry controls are not automatically clean generator-level interventions.
```

Therefore the roadmap remains:

```text
Run Stage B-2.
Prioritize preservation-first controls and honest proxy naming.
Keep the entropy-flow-horizon overlay diagnostic.
Do not open holdout.
Do not promote candidates.
```
