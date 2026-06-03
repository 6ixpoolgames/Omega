# Stochastic Distinction Channel Probe v0

## Executive Summary

A tiny finite stochastic-channel substrate was built with declared carriers, distinctions, priors, decoders, thresholds, support projections, and composition checks. Identity recovers the declared joint distinction, total erasure does not, and nonzero stochastic noise separates support-level exact recoverability from probabilistic decoder success. This tightened pass adds formal decoder policies, selected target-observation provenance, support-vs-probability summaries, fixed declared target summaries, and theorem-transfer readiness. Scope is finite channel recovery and formal consumption.

## Summary

- probe id: `stochastic_distinction_channel_probe_v0`
- channel count: 22
- distinction count: 15
- identity joint best success: 1.000000
- total erasure joint best success: 0.250000

## Scope

finite stochastic channel probe; scope limited to declared channel, distinction, decoder, threshold, and formal-consumption measurements

## Carriers And Distinctions

Primary source carrier is `X2 = {00,01,10,11}`. Distinctions include `D_A`, `D_B`, `D_joint`, `D_parity`, and `D_trivial`. Target observation scope is explicit in every distinction and recoverability row.

## Channel Families

Included identity, total erasure, projection, independent bit-flip, asymmetric bit noise, asymmetric bit erasure, marginal-preserving joint-degrading, output-marginal matched, deterministic entropy-matched random-like, and composed cascade channels.

## Priors And Decoders

Uniform source priors are declared for `X2` and `Y2`. Bayes-optimal decoders are emitted for all distinction pairs; exact decoders are emitted when support-level exact recovery exists; declared same-label decoders are emitted when label sets match.

Decoder policies are explicit:

- `bayes_best_target_distinction`: co_primary_diagnostic_policy
- `fixed_declared_target_distinction`: co_primary_strict_observation_policy
- `support_exact_candidate`: support_level_root_calculus_candidate

The fixed-declared-observation policy is co-primary with Bayes-best for summary reads, so target observations are visible rather than optimized silently.

- fixed `bit_flip_p_0_05` / `D_A` -> `E_A`: success 0.950000, delta vs Bayes-best 0.000000
- fixed `bit_flip_p_0_05` / `D_joint` -> `E_joint`: success 0.902500, delta vs Bayes-best 0.000000
- fixed `identity_channel` / `D_joint` -> `E_joint`: success 1.000000, delta vs Bayes-best 0.000000
- fixed `marginal_joint_degrade_q_0_10` / `D_A` -> `E_A`: success 0.950000, delta vs Bayes-best 0.000000
- fixed `marginal_joint_degrade_q_0_10` / `D_joint` -> `E_joint`: success 0.900000, delta vs Bayes-best 0.000000
- fixed `total_erasure_channel` / `D_joint` -> `unavailable`: success 0.000000, delta vs Bayes-best -0.250000

## Audit Summary

- `channel_row_stochastic_audit.csv` failures: 0
- `decoder_totality_audit.csv` failures: 0
- `distinction_partition_audit.csv` failures: 0
- `threshold_application_audit.csv` failures: 0

## Exact And Probabilistic Recoverability

Support-level exact recoverability and probabilistic decoder success are separate columns. For stochastic channels with full support, exact support recovery can fail while Bayes success remains above chance. Exact support recovery now requires both nonambiguous target support and coverage of all positive-prior source labels.

- `bit_flip_p_0_05` / `D_A`: probabilistic_without_exact_support (best target `E_A`, success 0.950000)
- `bit_flip_p_0_05` / `D_joint`: neither_exact_nor_high (best target `E_joint`, success 0.902500)
- `identity_channel` / `D_joint`: exact_and_high_probability (best target `E_joint`, success 1.000000)
- `marginal_joint_degrade_q_0_10` / `D_A`: probabilistic_without_exact_support (best target `E_A`, success 0.950000)
- `marginal_joint_degrade_q_0_10` / `D_joint`: neither_exact_nor_high (best target `E_joint`, success 0.900000)
- `total_erasure_channel` / `D_joint`: neither_exact_nor_high (best target `E_trivial_star`, success 0.250000)

## Non-Erasure Requirement Sets

- `bayes_best_target_distinction` / `identity_channel` / `req_marginals`: 2/2 recovered at `high_recovery`
- `bayes_best_target_distinction` / `identity_channel` / `req_joint`: 1/1 recovered at `high_recovery`
- `bayes_best_target_distinction` / `identity_channel` / `req_parity`: 1/1 recovered at `high_recovery`
- `bayes_best_target_distinction` / `identity_channel` / `req_all_nontrivial`: 4/4 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `identity_channel` / `req_marginals`: 2/2 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `identity_channel` / `req_joint`: 1/1 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `identity_channel` / `req_parity`: 1/1 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `identity_channel` / `req_all_nontrivial`: 4/4 recovered at `high_recovery`
- `bayes_best_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_marginals`: 2/2 recovered at `high_recovery`
- `bayes_best_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_joint`: 0/1 recovered at `high_recovery`
- `bayes_best_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_parity`: 0/1 recovered at `high_recovery`
- `bayes_best_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_all_nontrivial`: 2/4 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_marginals`: 2/2 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_joint`: 0/1 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_parity`: 0/1 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `marginal_joint_degrade_q_0_10` / `req_all_nontrivial`: 2/4 recovered at `high_recovery`
- `bayes_best_target_distinction` / `total_erasure_channel` / `req_marginals`: 0/2 recovered at `high_recovery`
- `bayes_best_target_distinction` / `total_erasure_channel` / `req_joint`: 0/1 recovered at `high_recovery`
- `bayes_best_target_distinction` / `total_erasure_channel` / `req_parity`: 0/1 recovered at `high_recovery`
- `bayes_best_target_distinction` / `total_erasure_channel` / `req_all_nontrivial`: 0/4 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `total_erasure_channel` / `req_marginals`: 0/2 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `total_erasure_channel` / `req_joint`: 0/1 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `total_erasure_channel` / `req_parity`: 0/1 recovered at `high_recovery`
- `fixed_declared_target_distinction` / `total_erasure_channel` / `req_all_nontrivial`: 0/4 recovered at `high_recovery`

## Marginal-Versus-Joint Diagnostic

- `bayes_best_target_distinction` / `all_nontrivial_lost`: 8
- `bayes_best_target_distinction` / `marginal_and_joint_recovered`: 2
- `bayes_best_target_distinction` / `marginal_recovered_joint_not_recovered`: 3
- `bayes_best_target_distinction` / `mixed_or_partial`: 6
- `fixed_declared_target_distinction` / `all_nontrivial_lost`: 8
- `fixed_declared_target_distinction` / `marginal_and_joint_recovered`: 2
- `fixed_declared_target_distinction` / `marginal_recovered_joint_not_recovered`: 3
- `fixed_declared_target_distinction` / `mixed_or_partial`: 6

The diagnostic reports finite channel structure under the declared policies.

## Baseline Comparisons

- `marginal_joint_degrade_q_0_10` `D_A` vs `identity_channel`: delta -0.050000
- `marginal_joint_degrade_q_0_10` `D_joint` vs `identity_channel`: delta -0.100000
- `marginal_joint_degrade_q_0_10` `D_parity` vs `identity_channel`: delta -0.100000
- `marginal_joint_degrade_q_0_10` `D_A` vs `independent_noise_matched_channel`: delta 0.000000
- `marginal_joint_degrade_q_0_10` `D_joint` vs `independent_noise_matched_channel`: delta -0.002500
- `marginal_joint_degrade_q_0_10` `D_parity` vs `independent_noise_matched_channel`: delta -0.005000
- `bit_flip_p_0_10` `D_A` vs `identity_channel`: delta -0.100000
- `bit_flip_p_0_10` `D_joint` vs `identity_channel`: delta -0.190000
- `bit_flip_p_0_10` `D_parity` vs `identity_channel`: delta -0.180000
- `bit_flip_p_0_10` `D_A` vs `total_erasure_channel`: delta 0.400000
- `bit_flip_p_0_10` `D_joint` vs `total_erasure_channel`: delta 0.560000
- `bit_flip_p_0_10` `D_parity` vs `total_erasure_channel`: delta 0.320000

## Channel Composition

- composition check rows: 10
Composition rows report measured composed success and a simple product-success reference. They are measurement rows, not standalone theorems.

## Support-Level Export For Lean Root Calculus

`support_relation.csv` and `support_recoverability.csv` expose `K(y|x) > 0` and exact support-recoverability candidates so the formal arm can compare support-level root calculus against probabilistic recovery.

## Theorem Transfer Readiness

- `support_level_exact_channel_presentation`: ready_for_formal_support_consumption
- `probabilistic_recovery_layer`: measurement_only_pending_formal_theorem
- `thresholded_non_erasure_layer`: measurement_only_thresholded
- `composition_probability_bounds`: measurement_only_pending_formal_bound
- `completion_or_candidate_family`: not_applicable

## Formal Consumption Bundle

`formal_channel_consumption_bundle.json` identifies the compact artifact set that the formal arm should consume. Support-level exact rows are separated from probabilistic measurement rows.

## Limits

The carrier is tiny, thresholds are conventional rather than discovered, and all distinctions are hand-declared finite labels. Larger scientific interpretation depends on subsequent formal and empirical work.

## Recommended Next Formal Target

Ask the formal arm to consume the support-level exact rows and the probabilistic recovery rows separately. If useful, the next empirical repair should add a theorem or audit for probabilistic composition bounds, not broader channels.