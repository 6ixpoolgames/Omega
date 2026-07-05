# Finite Relational Closure Guard Attribution v2.1.5

Status: PASS

## Headline

- Cases: 204
- Surplus facts: 2567
- Theorem-backed facts: 2567
- Classifier-only facts: 0
- Residual cases: 0
- Residual facts: 0
- Process-coherence profile guard facts: 202
- Step-to-path guard facts: 444

## Guard Theorems

| theorem | count |
| --- | ---: |
| `closure.guard.globally_valid_surplus` | 754 |
| `closure.guard.process_coherence_entails_bounded_profile_invariance` | 202 |
| `closure.guard.profile_fiber_separation_reflects_visibility` | 864 |
| `closure.guard.seed_forced_structural` | 54 |
| `closure.guard.seed_profile_functionality` | 249 |
| `closure.guard.step_lifting_implies_bounded_path_lifting` | 444 |

## Family Breakdown

| family | cases | theorem-backed | classifier-only | residual facts |
| --- | ---: | ---: | ---: | ---: |
| current_v2_attribution | 132 | 1531 | 0 | 0 |
| heldout_n4_step_lifting_sample | 32 | 477 | 0 | 0 |
| heldout_n4_observed_word_sample | 32 | 541 | 0 | 0 |
| heldout_n4_constant_control | 8 | 18 | 0 | 0 |

## Read

Closure v2.1.5 adds proof attribution to the v2.1 classifier. Each surplus fact is now attached to a named finite guard theorem and the hypothesis facts used by that theorem.

The process-coherence bucket is no longer merely a label: the runner verifies, for each case, that every generated presentation satisfying the support fact also satisfies the attributed bounded profile or visibility fact.

This remains a finite guard pass over the generated Closure v2 fact language. It is not a global modal fixed-point theorem or a natural-admissibility theorem.
