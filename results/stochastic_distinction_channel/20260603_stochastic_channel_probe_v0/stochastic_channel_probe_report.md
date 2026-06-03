# Stochastic Distinction Channel Probe v0

## Executive Summary

A tiny finite stochastic-channel substrate was built with declared carriers, distinctions, priors, decoders, thresholds, support projections, and composition checks. Identity recovers the declared joint distinction, total erasure does not, and nonzero stochastic noise separates support-level exact recoverability from probabilistic decoder success. The probe is suitable as a formal-consumption bridge only; it makes no Omega, agency, identity, value, compatibility, or ethical claim.

## Summary

- probe id: `stochastic_distinction_channel_probe_v0`
- channel count: 22
- distinction count: 15
- identity joint best success: 1.000000
- total erasure joint best success: 0.250000

## Claim Boundary

prebiotic stochastic channel probe only; no Omega validation, no valuer detection, no agency, no identity, no compatibility detection, no ethical claim

## Carriers And Distinctions

Primary source carrier is `X2 = {00,01,10,11}`. Distinctions include `D_A`, `D_B`, `D_joint`, `D_parity`, and `D_trivial`. Target observation scope is explicit in every distinction and recoverability row.

## Channel Families

Included identity, total erasure, projection, independent bit-flip, asymmetric bit noise, asymmetric bit erasure, marginal-preserving joint-degrading, output-marginal matched, deterministic entropy-matched random-like, and composed cascade channels.

## Priors And Decoders

Uniform source priors are declared for `X2` and `Y2`. Bayes-optimal decoders are emitted for all distinction pairs; exact decoders are emitted when support-level exact recovery exists; declared same-label decoders are emitted when label sets match.

## Audit Summary

- `channel_row_stochastic_audit.csv` failures: 0
- `decoder_totality_audit.csv` failures: 0
- `distinction_partition_audit.csv` failures: 0
- `threshold_application_audit.csv` failures: 0

## Exact And Probabilistic Recoverability

Support-level exact recoverability and probabilistic decoder success are separate columns. For stochastic channels with full support, exact support recovery can fail while Bayes success remains above chance.

## Non-Erasure Requirement Sets

- `identity_channel` / `req_marginals`: 2/2 recovered at `high_recovery`
- `identity_channel` / `req_joint`: 1/1 recovered at `high_recovery`
- `identity_channel` / `req_parity`: 1/1 recovered at `high_recovery`
- `identity_channel` / `req_all_nontrivial`: 4/4 recovered at `high_recovery`
- `marginal_joint_degrade_q_0_10` / `req_marginals`: 2/2 recovered at `high_recovery`
- `marginal_joint_degrade_q_0_10` / `req_joint`: 0/1 recovered at `high_recovery`
- `marginal_joint_degrade_q_0_10` / `req_parity`: 0/1 recovered at `high_recovery`
- `marginal_joint_degrade_q_0_10` / `req_all_nontrivial`: 2/4 recovered at `high_recovery`
- `total_erasure_channel` / `req_marginals`: 0/2 recovered at `high_recovery`
- `total_erasure_channel` / `req_joint`: 0/1 recovered at `high_recovery`
- `total_erasure_channel` / `req_parity`: 0/1 recovered at `high_recovery`
- `total_erasure_channel` / `req_all_nontrivial`: 0/4 recovered at `high_recovery`

## Marginal-Versus-Joint Diagnostic

- `all_nontrivial_lost`: 8
- `marginal_and_joint_recovered`: 2
- `marginal_recovered_joint_not_recovered`: 3
- `mixed_or_partial`: 6

The diagnostic is finite stochastic-channel structure only. It is not compatibility or ethical erasure.

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

## Limitations

The carrier is tiny, thresholds are conventional rather than discovered, and all distinctions are hand-declared finite labels. This is a clean formal bridge, not a scientific validation result.

## Recommended Next Formal Target

Ask the formal arm to consume the support-level exact rows and the probabilistic recovery rows separately. If useful, the next empirical repair should add a theorem or audit for probabilistic composition bounds, not broader channels.