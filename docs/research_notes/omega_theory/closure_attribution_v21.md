# Closure Attribution v2.1

Status: retained finite attribution result / closure calibration checkpoint
Scope: current Closure v2 plus held-out n=4 sampled families
Claim boundary: not global invariance, not natural admissibility, not a modal
fixed-point theorem, not a canonical implication basis, not agency, not
identity, not value, not valuerhood, not Omega validation

## Purpose

Closure v2 showed that richer dynamic fact languages can produce dynamic
surplus:

```text
132 cases;
101 dynamic-surplus cases;
36 cases with unclassified dynamic-profile surplus;
constant controls collapsed.
```

Closure v2.1 asks whether that unclassified bucket is actually explained by a
fixed process-coherence attribution rule.

Protocol:

```text
closure_attribution_protocol_v21.md
```

## Implementation

The attribution layer lives at:

```text
omega/adapters/finite_relational/closure_attribution_v21.py
```

The validation runner is:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_closure_attribution_v21 `
  --out-root .tmp\finite_relational_closure_attribution_v21
```

The retained result is:

```text
docs/research_notes/validation_results/finite_relational_closure_attribution_v21/
```

Tests:

```text
tests/test_finite_relational_closure_attribution_v21.py
```

## Current Result

The retained run reports:

```text
case_count: 204
residual_case_count: 0
residual_fact_count: 0
```

Attribution bucket counts:

```text
bounded_process_coherence_invariance: 202
globally_valid: 754
profile_fiber_separation: 380
seed_determined_profile: 249
seed_forced_structural: 54
seed_profile_separation: 484
step_implies_path_lifting: 444
```

Support counts:

```text
struct:step_lifting: 700
profile:observed_words:goal_status:h=1: 504
profile:safe_prefix_count:h=1: 134
profile:extendable_safe_prefix_count:h=1: 120
profile:reach:goal: 90
profile:safe_prefix_count:h=2: 16
```

## Family Breakdown

```text
current_v2_attribution:
  132 cases;
  0 residual cases;
  120 bounded process-coherence invariance attributions;
  294 step-implies-path attributions.

heldout_n4_step_lifting_sample:
  32 cases;
  0 residual cases;
  82 bounded process-coherence invariance attributions;
  96 step-implies-path attributions.

heldout_n4_observed_word_sample:
  32 cases;
  0 residual cases.

heldout_n4_constant_control:
  8 cases;
  0 residual cases;
  only globally valid surplus.
```

## Interpretation

The key current-v2 result is:

```text
all 120 previously unclassified dynamic-profile surplus facts
attribute to bounded process-coherence invariance.
```

This supports Fable's audit read:

```text
Closure v2 likely rediscovered the finite shadow of a process-coherence /
behavioral-invariance theorem.
```

That is a useful calibration result. It means the closure instrument can find
theorem-shaped structure without being explicitly told the theorem.

It does not yet produce unexplained new closure structure.

## Repricing

Before v2:

```text
closure positives existed but reduced to complements/separation.
```

After v2:

```text
process-coherence admissibility can force dynamic profile surplus.
```

After v2.1:

```text
the observed surplus is attributable to fixed process-coherence / profile-fiber
rules, including held-out n=4 samples.
```

Therefore the closure branch is live, but the next target is not more sweeps.
The next target is theorem extraction or an implication-basis classifier:

```text
prove or mechanize the process-coherence invariance principle;
then search for residual surplus after known-theory attribution.
```

## Nonclaims

This note does not claim:

```text
global invariance;
natural admissibility;
semantic adequacy of the generated fact language;
canonical implication basis;
modal mu-calculus theorem;
agency;
identity;
value;
valuerhood;
moral standing;
Omega validation.
```

## Next Steps

Recommended next steps:

```text
1. extract the focused process-coherence / behavior-profile theorem;
2. add an implication-basis or proof-attribution layer;
3. only then run larger held-out families;
4. treat residuals after attribution as the next genuine closure signal.
```

## Public Compression

Closure v2.1 attributes all Closure v2 dynamic-profile surplus, including
held-out n=4 samples, to fixed process-coherence and profile-fiber rules. This
calibrates the closure instrument and points toward theorem extraction rather
than more raw sweeps.
