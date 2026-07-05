# Finite Relational Closure Implication Basis v2.2

Status: PASS

## Headline

- Cases: 204
- Implications: 2567
- Guard-accounted implications: 2567
- Classifier-only implications: 0
- Residual implications: 0
- Unique seed implication signatures: 56
- Unique guard implication signatures: 87

## Basis Kinds

| kind | count |
| --- | ---: |
| `globally_valid` | 754 |
| `process_coherence_profile_guard` | 202 |
| `process_coherence_structural_guard` | 54 |
| `profile_fiber_visibility_guard` | 864 |
| `seed_profile_functionality_guard` | 249 |
| `step_to_path_guard` | 444 |

## Antecedent Sizes

| antecedent | size | count |
| --- | ---: | ---: |
| seed | 0 | 754 |
| seed | 1 | 1813 |
| guard | 0 | 754 |
| guard | 1 | 1813 |

## Family Breakdown

| family | cases | implications | guard-accounted | residual |
| --- | ---: | ---: | ---: | ---: |
| current_v2_attribution | 132 | 1531 | 1531 | 0 |
| heldout_n4_step_lifting_sample | 32 | 477 | 477 | 0 |
| heldout_n4_observed_word_sample | 32 | 541 | 541 | 0 |
| heldout_n4_constant_control | 8 | 18 | 18 | 0 |

## Read

Closure v2.2 extracts minimal seed and guard antecedents for the retained v2.1.5 surplus facts. It does not run a larger graph sweep or add new fact kinds.

The current run leaves no classifier-only or residual implications. The implication basis is therefore guard-accounted over the current and held-out v2.1.5 families.

This is still finite and key-level. Unique implication signatures are not claimed as global theorems over all graphs.
