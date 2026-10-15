# Robust compounding: engineering result

15 October 2026. **Engineering complete; scientific protocol remains unfrozen.**
No preparation ranking, mechanism winner, C/R/L/J verdict or hypothesis score
has been inspected. The implemented chemistry is ready for scientific-batch
integration and freeze, not an already completed robust-compounding experiment.

33 focused tests pass. They cover full-packet dark detailed balance for all
six mechanisms and both feedback shapes; saturated capture reverses; conserved
material and bank/energy accounting; constant damage hazard with irreversible
loss; graph-defined closure; neutral depth monitors; exact versus sampled
dynamics; pulse/recovery conditioning; and class-aware finite entropy, rates and
offsets against the independent dense backend.

## Measured budget

Every job ran from a hash-verified source/config snapshot with hard limits of
120 seconds, 512 MiB process-tree memory and 32 MiB output. The full physical
sampled kernel has a separate 160 MiB gate. Tracker matrices remain sparse and
are excluded from the physical entropy readout.

| Validation | Physical states | Tracker states | Seconds | Peak MiB | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| SMOKE_M4 | 630 | 3150 | 1.09 | 120.2 | passed |
| SMOKE_M6 | 1,512 | 7560 | 3.56 | 145.5 | passed |
| SMOKE_M8 | 2,970 | 14850 | 6.59 | 216.3 | passed |
| SMOKE_SINK_M6 | 3,780 | 18900 | 9.71 | 337.9 | passed |
| GATE_SINK_M8 | 8,910 | — | 0.55 | 48.8 | kernel gate; not run |
| CORNER_LOW | 3,780 | 18900 | 5.83 | 338.7 | passed |
| CORNER_HIGH | 3,780 | 18900 | 9.61 | 338.8 | passed |

M6 profiles execute the finite-history numerical route through horizons
16/64/256/1024/4096 and the strong path query through 256. These computations
retain timing and validity receipts only, not scientific arm comparisons.
Corner cases additionally cover the all-assistance-off low-source sink at
cadence 0.125 and high-source, high-damage sublinear sink at cadence 0.5.
All ran within caps. The 8,910-state sink kernel needs about 606 MiB **for the
kernel alone**, so it is rejected before calculation; the physical world is
not pruned or made less stochastic to fit memory.

Maximum absolute residuals across completed cases:

- dark_balance_residual: 1.08e-19
- bank_ledger_residual: 1.78e-15
- energy_ledger_residual: 4.22e-15
- poisson_residual: 2.2e-10
- harmonic_rate_residual: 3.23e-15
- one_step_identity_residual: 2.22e-10

## Corrections made during engineering

The first M6 smoke exposed rare-state amplification at the arbitrary Poisson
anchor. The solve now uses a normalized stationary equation and a high-mass
anchor per recurrent class. A regression test retains the failed case. The
failed receipt and all subsequent attempts remain in
[ENGINEERING_ATTEMPTS.json](ENGINEERING_ATTEMPTS.json); frozen runs were not
overwritten or deleted.

Reversible capture also required a funding correction before science. Gross
capture can recycle initial, bath-return and reverse-capture packets. The
external-spending lower bound deducts their full possible contribution; a
zero-drive test verifies that recycling cannot become external funding. The
complete bank ledger includes reverse capture's charge debit.

## Implemented foundation and next boundary

- Physical cycle A→B→C→A, positive basal chemistry, paid construction/capture,
  fractional feedback, bilateral link ablations, repairable damage and a real
  material sink.
- Permanent initial-seed witness and separately resetting any-start detector.
  Detected-chain intensity is a conservative lower bound, not complete genealogy.
- Joint depth/retained-expansion/later-function query, deterministic one-B pulse,
  unconditional recovery, functional uptime and graph closure.
- Memory-gated sampled kernels, sparse recurrent/transient Poisson analysis and
  exact finite-history identities. Finite lushness stays primary; rates diagnose
  sustained contribution under the declared boundary.

The next stage implements the scientific batch/report orchestration, including
the complete piecewise history score for pulse arms, coordinate/activity
decomposition, all registered C/R/L/J maps, and final prediction/tolerance
freeze. No scientific run is authorized by this engineering report. Individual
modules are validated; the complete scientific workload is not yet profiled.
The measured M6 costs support proceeding without increasing caps or reducing
the declared physical inventory.

The source-window test remains separate. A repayment estimate applies only to
an appropriate positive mechanism-rate contrast; same-Q irreducible roots
cannot acquire different limiting rates. Persistence-versus-repayment is a
restricted prediction, not a general theorem. Whole-type knockout and a
matched single-type comparator remain follow-ups. Count-stage success cannot
overturn the earlier spatial seed-versus-unbound reversal.

See [specification](PROPOSED_SPEC_r1.md), [monitor contract](MONITOR_CONTRACT.md),
[physics/numerics](PHYSICS_AND_NUMERICS.md), and
[machine-readable receipts](ENGINEERING_SUMMARY.json). No commit, push or Drive
change was made.
