# Embodied control and matched shocks

Seven frozen exhaustive36-table searches. Exact equal-kernel and equal-ledger aliases are retained; only unique models are evaluated. Native sampled physical count histories remain the sole objective, ranked by long-run rate then root offset. Random damage is included.

| Case | Winner inactive / active | Unique models | Rate bits/time | Active at64 | Closure64 | Stationary exposed | Stationary function probability | Common-probe conditional reserve |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_reversible | mix25 / mix25 | 36 | 7.145668 | 1.068790 | 0.000000 | 0.901403 | 0.444927 | 0.569378 |
| embodied_reversible | inoperative / service | 6 | 6.195478 | 1.344372 | 0.000000 | 0.926470 | 0.451598 | 0.580167 |
| independent_reversible | inoperative / service | 6 | 5.581759 | 1.004282 | 0.000000 | 0.636165 | 0.314321 | 0.552557 |
| correlated_half_reversible | inoperative / service | 6 | 5.579020 | 1.004588 | 0.000000 | 0.636468 | 0.312600 | 0.554186 |
| correlated_all_reversible | inoperative / service | 6 | 5.573154 | 1.004658 | 0.000000 | 0.636741 | 0.310716 | 0.555975 |
| embodied_absorbing | inoperative / service | 6 | 3.620640 | 1.267047 | 0.012457 | 0.000000 | 0.000000 | undefined |
| frozen_gate_absorbing | inoperative / export | 6 | 4.099945 | 0.377414 | 0.025404 | 0.000000 | 0.000000 | undefined |

## Prospective comparisons

| Hypothesis | Verdict | Value (difference where applicable) |
|---|---|---:|
| E1-service | pass | 0.25 |
| E2-common-tail | pass | 3.9968028886505635e-14 |
| E3-frozen-tail | pass | 1.363306872267387 |
| R1-half-reserve | pass | 0.0016292398854809154 |
| R1-all-reserve | pass | 0.003418627527328466 |
| R2-exposure | open_outcome | -0.2903053588879333 |
| R3-horizon | pass | 0.012481735509572767 |

Reserve uses one identical hypothetical .5 hit-probability shock across all winning state distributions: probability that some active apparatus remains, conditional on function before the probe. It avoids comparing different native shock severities as though their per-arrival risks were directly interchangeable. Native-clock risks are retained separately. Absorbing stationary function is absent; inspect finite-deadline diagnostics instead.

Increasing exposure is a diagnostic flag. It does not prove the optimizer farms damage: more machinery can also produce more useful continuation. Family event flux is not an additive decomposition of sampled-state entropy. Independent and correlated damage have equal conditional first moments, but distinct laws and distinct history breadth.

Conditional reserve can improve while function is present less often. Read its registered verdict alongside stationary function probability and unconditional post-probe function probability (the product of function probability and conditional reserve), not as proof of improved overall resilience. Embodied inactive instructions are all physically equivalent; their printed raw table names are alias labels without operational meaning.

Basal gate relaxation is policy-independent and thermally symmetric because gate energy is zero. Commanded switching has its existing fuel accounting and requires a/M functioning capacity. Separate controller memory/sensing is not modeled. The chemical boundary and passive carrier motion continue after apparatus collapse. No tail subtraction or survival bonus is used.

Shocks are an external nonequilibrium energy boundary. Their signed energy transfers are kept separate from chemical drive work; thermal balance is asserted only for the isolated thermal modules, not the driven shocked world. Four material slots cannot establish open-ended compounding. The matched preparation reference is a coarse count ensemble, not molecular gas.

## Standard controls

| Case | Passive idle rate | Always service rate | Always export rate | Half/half rate | Best service/export deterministic rate |
|---|---:|---:|---:|---:|---:|
| legacy_reversible | 5.903046 | 6.861119 | 6.076322 | 7.051563 | 6.861119 |
| embodied_reversible | 5.903046 | 6.195478 | 5.393957 | 5.758865 | 6.195478 |
| independent_reversible | 5.446443 | 5.581759 | 5.140084 | 5.344025 | 5.581759 |
| correlated_half_reversible | 5.443509 | 5.579020 | 5.138177 | 5.342163 | 5.579020 |
| correlated_all_reversible | 5.437885 | 5.573154 | 5.134811 | 5.338395 | 5.573154 |
| embodied_absorbing | 3.620640 | 3.620640 | 3.620640 | 3.620640 | 3.620640 |
| frozen_gate_absorbing | 2.736638 | 3.055134 | 4.099945 | 3.862808 | 4.099945 |

## Provenance

- channel-scientific-uniform_absorbing-20261013T145541Z-9fc4b1: 328.11s, 582.03MiB; input `0a587ed99738bfde80a4d91e096096d3718f386467597188fbd2cfd0eb3dae4a`.
- channel-scientific-uniform_absorbing-20261013T145541Z-433143: 70.01s, 573.59MiB; input `77d735f0b74885be6c6d4533ed159e7d6b5caf95bc53023be4c4817ffea6f7c3`.
- channel-scientific-uniform_absorbing-20261013T145737Z-486223: 73.69s, 574.37MiB; input `9d2176e32ffefa111783401487a445f9067f09bc4432a2638dd227fe4f01c6ac`.
- channel-scientific-uniform_absorbing-20261013T145912Z-a15569: 78.41s, 575.55MiB; input `bc84dbb1f90159f8b83c9e67a36306877c26c06f06a7966061031c72e66515b5`.
- channel-scientific-uniform_absorbing-20261013T150107Z-0b8887: 73.47s, 575.56MiB; input `4eb8361bd307b4b6cfc061489a8bd3f090640d755eb9c971aac42b17f07c011f`.
- channel-scientific-uniform_absorbing-20261013T150130Z-7f4a7f: 65.76s, 572.42MiB; input `2d1d6b81f50ea109e4a8b8e1d424d26d4b1eafacdc918c9af6554232ae86b860`.
- channel-scientific-uniform_absorbing-20261013T150447Z-160060: 56.59s, 572.74MiB; input `7226bc77e897432b93341295df71c9733db7899edbe19b0e6a23891bb6b80cea`.

Full compact policy profiles, aliases, failures and diagnostic roots are in SUMMARY.json. Raw state/class vectors remain ignored local artifacts. No prior run has been overwritten or rescored.
