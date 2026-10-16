# Temporal profile audit results

The exact histories reproduce the previous adverse comparisons and explain their temporal reversals. No physical cutoff was supplied and no term was subtracted from lushness.

| Parent / T | Asymptotic crossing estimate | Exact integer-schedule crossing bracket |
| --- | ---: | --- |
| W1-00 / 64 | 0.103160 | 0.141907–0.142222 |
| W1-00 / 256 | 0.103161 | 0.142064–0.142143 |
| W1-08 / 64 | 0.138351 | 0.179775–0.180282 |
| W1-08 / 256 | 0.138352 | 0.180155–0.180282 (one endpoint within bit tolerance) |

The leading formula underestimates these finite-cadence crossing locations. Exact matrix exponentials remain necessary. Brackets compare adjacent integer sample schedules at a fixed physical horizon, rather than claiming an arbitrary-cadence exact root.

Across both parents and horizons, B_R exceeds B, A0 exceeds A, and A loses to B_R at every tested resolved cadence (0.5 through 1/512). A versus B changes sign in all four profiles. The original coarse-cadence counterexamples remain valid within their declared grain.

All 48 overlapping earlier comparisons reproduce within 3.3e-12 bits. Maximum probability residual 7.14e-13. The run took 6.09s, peaking at 154.2MiB.

The finest sign agrees with the nonzero jump-count difference in 16/16 pairs. Final pair error is smaller than coarsest error in 16/16. The stricter final-four monotone-error check passes only 10/16: higher-order cancellation can make signed pair error cross zero. Do not infer that every halving improves an asymptotic approximation monotonically.

In A−B, expected physical jumps are lower by about 0.472/0.504, while the finite terms are higher by about 1.547/1.438 bits at T64. Thus sufficiently fine timing favors B, even though A wins at cadence 0.25. F contains timing and destination uncertainty; it is not a structure or welfare score.

H(N_T) is bounded for all eight worlds at T64, with interval widths below 4e-9 bits (analytic tail uncertainty, in addition to numerical residuals). Overflow physical dynamics remain present; only the auxiliary count label is censored. Fixed-jump entropy and expected local destination surprisal are separate diagnostics. The full random-length conditional mark/timing decomposition was not computed.

Hidden-signal bounds at the original three cadences remain in SUMMARY.json. They are non-Markov bounds, not an invented coarse CTMC. The new fine grid does not settle spatial grain, physical distinguishability, or a universal temporal band.

Interpretation revised15October2026: this is a measurement calibration on fixed functional adversaries. It preserves both the original resolved counterexamples and their resolution dependence. A temporal crossover varies cadence at fixed horizon; a horizon repayment crossover varies duration at fixed cadence. These are different diagnostics. F is a finite temporal-resolution term, not a measure of organization.

The subsequent [exploration](../exploration/RESULTS.md), [paid sensing](../paid_sensing/RESULTS.md) and [renewal](../renewal/RESULTS.md) batches are complete. The new renewal rate advantages describe ongoing contributions under a different law; they do not remove this calibration or its counterexamples. See [cross-run synthesis](../INTERPRETATION_SYNTHESIS_2026-10-15.md).

Reproduce: `python scripts/run_temporal_profile.py smoke`, then `science`, then `python scripts/report_temporal_profile.py`. Existing frozen registration is reused; `prepare` is only for creating it once. Raw snapshots/results remain ignored locally. Sources, protocol, full compact summary and comparison map are retained.

Frozen scientific input hash: `6d2a0f7299e0c2f30246e7246d0369c62a2c4a8ed6f9f2f1f07cc6f70b42211b`.
The first smoke exposed a descriptive protocol key incorrectly forwarded as a function argument. That engineering call was repaired before successful source-identical smoke and science; physical parameters and registered queries were unchanged.
