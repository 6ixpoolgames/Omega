# Finite Relational Closure Attribution v2.1

Status: PASS

## Headline

- Cases: 204
- Residual cases: 0
- Residual facts: 0
- Bounded process-coherence attributions: 202
- Step-implies-path attributions: 444

## Family Breakdown

| family | cases | residual cases | residual facts |
| --- | ---: | ---: | ---: |
| current_v2_attribution | 132 | 0 | 0 |
| heldout_n4_step_lifting_sample | 32 | 0 | 0 |
| heldout_n4_observed_word_sample | 32 | 0 | 0 |
| heldout_n4_constant_control | 8 | 0 | 0 |

## Attribution Buckets

| bucket | count |
| --- | ---: |
| bounded_process_coherence_invariance | 202 |
| globally_valid | 754 |
| profile_fiber_separation | 380 |
| seed_determined_profile | 249 |
| seed_forced_structural | 54 |
| seed_profile_separation | 484 |
| step_implies_path_lifting | 444 |

## Read

The fixed classifier attributes all current-v2 and held-out surplus facts. The current-v2 dynamic-profile facts that were previously unclassified are attributed to bounded process-coherence invariance under step lifting.

This is a calibration result. It supports the interpretation that Closure v2 found the finite shadow of a known process-coherence invariance pattern, not yet unexplained new closure structure.

## Representatives

### current_v2_attribution

Attributes the retained Closure v2 n=3 graph sweep without changing the v2 fact universe or case definitions.

- `step_lifting_seed_01`: residuals none; buckets globally_valid=6, bounded_process_coherence_invariance=1, step_implies_path_lifting=3, profile_fiber_separation=4
- `step_lifting_seed_00`: residuals none; buckets globally_valid=10

### heldout_n4_step_lifting_sample

Held-out sampled loop-free four-state graphs with step lifting as the only seed.

- `heldout_n4_step_00`: residuals none; buckets globally_valid=6, bounded_process_coherence_invariance=1, step_implies_path_lifting=3, profile_fiber_separation=8

### heldout_n4_observed_word_sample

Held-out sampled loop-free four-state graphs with the horizon-1 observed extendable word profile as seed.

- `heldout_n4_observed_word_00`: residuals none; buckets globally_valid=5

### heldout_n4_constant_control

Held-out sampled loop-free four-state graphs with only the constant profile as seed.

- `heldout_n4_constant_00`: residuals none; buckets globally_valid=1

## Claim Boundary

Closure v2.1 is a finite attribution pilot. It does not prove global invariance, natural admissibility, a modal fixed-point theorem, agency, identity, value, valuerhood, moral standing, or Omega validation.
