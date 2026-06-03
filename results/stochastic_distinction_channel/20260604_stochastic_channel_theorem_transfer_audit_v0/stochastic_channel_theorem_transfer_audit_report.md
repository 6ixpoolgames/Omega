# Stochastic Channel Theorem-Transfer Audit v0

## Executive Summary

This audit converts the tightened stochastic-channel probe into a formal-consumption package for the Lean probabilistic channel presentation. The key repair is the cascade path ensemble: first-stage, second-stage, and composite decoder errors are measured on the same finite path denominator, so the Lean union-bound theorem is instantiable for the declared fixed-policy cascades. Bayes-best rows remain available as diagnostics, but they are not substituted into composition proofs.

- overall status: `support_and_probabilistic_transfer_ready`
- cascade bound rows: 10
- cascade bound passes: 10
- theorem-applicable cascade rows: 10
- decoder audit failures: 0

## Scope

finite stochastic channel theorem-transfer audit; support/probability separation, decoder-policy provenance, and cascade error-bound applicability only

## Inputs And Source Probe Digest

- source output: `results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_fixed_policy`
- source digest: `9777bb7e5f3fba4f554bfb42`
- input status: `ready`
- missing inputs: `none`

## Rational And Natural Weights

Channel probabilities and source priors are rationalized exactly from retained fraction columns. Channel rows are converted to row-scaled natural weights, matching the finite Lean presentation style.

## Cascade Path Ensemble

Each cascade row emits path records with `mass(x,y,z)=pi(x)*K(y|x)*L(z|y)`. The composed-channel total is recomputed from the same generated natural cascade, rather than from independently normalized stage summaries.

## Error Mass And Bound Checks

- `comp_bitflip_0_10_then_0_25` / `D_A`: composite 1920 <= 640 + 1600 (theorem_applicable_generated_natural_weights)
- `comp_bitflip_0_10_then_0_25` / `D_B`: composite 1920 <= 640 + 1600 (theorem_applicable_generated_natural_weights)
- `comp_bitflip_0_10_then_0_25` / `D_joint`: composite 3264 <= 1216 + 2800 (theorem_applicable_generated_natural_weights)
- `comp_bitflip_0_10_then_0_25` / `D_parity`: composite 2688 <= 1152 + 2400 (theorem_applicable_generated_natural_weights)
- `comp_bitflip_0_10_then_0_25` / `D_trivial`: composite 0 <= 0 + 0 (theorem_applicable_generated_natural_weights)
- `comp_identity_then_marginal_degrade_0_10` / `D_A`: composite 4 <= 0 + 4 (theorem_applicable_generated_natural_weights)
- `comp_identity_then_marginal_degrade_0_10` / `D_B`: composite 4 <= 0 + 4 (theorem_applicable_generated_natural_weights)
- `comp_identity_then_marginal_degrade_0_10` / `D_joint`: composite 8 <= 0 + 8 (theorem_applicable_generated_natural_weights)
- `comp_identity_then_marginal_degrade_0_10` / `D_parity`: composite 8 <= 0 + 8 (theorem_applicable_generated_natural_weights)
- `comp_identity_then_marginal_degrade_0_10` / `D_trivial`: composite 0 <= 0 + 0 (theorem_applicable_generated_natural_weights)

## Denominator Alignment

- aligned rows: 10
- independent-normalization rows used for theorem evidence: 0

## Decoder-Policy Alignment

- `aligned_declared_composition`: 10
- `measurement_only_best_decoder_comparison`: 10

## No-Self-Evidencing Decoder Audit

Allowed recovery decoders map declared target-observation labels to source labels; they do not consume source-state IDs, source labels, hidden states, or candidate IDs.

## Support Versus Probability Boundary

- `exact_support_and_perfect_probability`: 302
- `high_probability_without_exact_support`: 24
- `support_exact_failure_probability_high`: 70
- `support_exact_failure_probability_low`: 453

## Threshold Sensitivity

- threshold sensitivity rows: 4245
Thresholds tested: 0.80, 0.90, 0.95, 0.99, and 1.00.

## Marginal-Versus-Joint Examples

- `asym_A_erased_B_preserved` / `bayes_best_target_distinction`: mixed_or_partial
- `asym_A_erased_B_preserved` / `fixed_declared_target_distinction`: mixed_or_partial
- `asym_A_noisy_B_preserved_p_0_25` / `bayes_best_target_distinction`: mixed_or_partial
- `asym_A_noisy_B_preserved_p_0_25` / `fixed_declared_target_distinction`: mixed_or_partial
- `asym_A_preserved_B_noisy_p_0_25` / `bayes_best_target_distinction`: mixed_or_partial
- `asym_A_preserved_B_noisy_p_0_25` / `fixed_declared_target_distinction`: mixed_or_partial
- `asym_B_erased_A_preserved` / `bayes_best_target_distinction`: mixed_or_partial
- `asym_B_erased_A_preserved` / `fixed_declared_target_distinction`: mixed_or_partial
- `bit_flip_p_0_00` / `bayes_best_target_distinction`: marginal_and_joint_recovered
- `bit_flip_p_0_00` / `fixed_declared_target_distinction`: marginal_and_joint_recovered
- `bit_flip_p_0_05` / `bayes_best_target_distinction`: marginal_recovered_joint_not_recovered
- `bit_flip_p_0_05` / `fixed_declared_target_distinction`: marginal_recovered_joint_not_recovered

## Theorem-Transfer Readiness

- `support_level_exact_channel_presentation`: ready_for_formal_consumption
- `exact_implies_perfect_probability`: ready_for_formal_consumption
- `perfect_full_prior_implies_exact`: ready_for_formal_consumption
- `perfect_nonfull_prior_not_exact_counterexample`: ready_for_measurement_only
- `high_probability_not_exact_counterexample`: ready_for_formal_consumption
- `cascade_error_bound`: ready_for_formal_consumption
- `cascade_same_denominator_threshold_bound`: ready_for_formal_consumption
- `bayes_best_vs_fixed_declared_policy_separation`: ready_for_formal_consumption
- `thresholded_non_erasure_layer`: ready_for_measurement_only
- `completion_or_candidate_family`: not_applicable

## Blocked Claims And Next Formal Asks

Thresholded non-erasure remains a measurement layer unless a matching theorem is declared. Candidate-family and completion objects are still out of scope for this adapter. The next useful formal ask is not broader channel data; it is either a thresholded probabilistic non-erasure theorem or a deliberate candidate-family presentation.