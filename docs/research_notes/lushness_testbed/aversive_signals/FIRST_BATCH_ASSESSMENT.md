# First W1/W2 adversaries: scientific assessment

All 384 registered arm/cadence analyses completed, covering 32 parameter points
and four horizons. The first slice yields two valid **adapter-relative functional
K1 counterexamples** at the primary cadence and horizon. It yields no registered
stronger full-corridor kill, and no clean K2 verdict. These statements have
different scopes and must not be collapsed into either “the wager passed” or
“suffering has been proved valuable.”

## K1: obstructed tracking signal versus calm obstruction

Both winning cases pass the frozen tracking, escape-disposition and obstruction
checks. They have escape bias 0.25, upkeep/metabolism ratio 0.05 and damage rate
0.15. They differ in escape/forage cost ratio: 1 versus 2. The physical costs
are positive. Fourteen of the sixteen primary K1 points favour calm obstruction.

| Case | Cost ratio | Resolved A-B at T64, dt 0.25 | Limiting offset A-B | Expected living time A / B |
| --- | ---: | ---: | ---: | ---: |
| W1-00 | 1 | +0.257938 bits | +0.257929 bits | 7.075 / 7.535 |
| W1-08 | 2 | +0.153484 bits | +0.153480 bits | 6.721 / 7.183 |

All arms eventually lose the valuer and retain the same environmental tail
rate at a given cadence. At dt 0.25 the two rates are approximately 2.284090
bits/time. Their finite-history difference tends to a nonzero offset. Equal
eventual rates therefore do not erase the comparison. Extending the horizon
to 256 or 1024 retains both positive resolved rankings at this cadence.

The obstructed arm receives less food, survives for less expected time and
performs more failed escape. In W1-00, accepted food falls from 1.584785 to
1.448350 energy units and failed escapes rise from 0.452078 to 0.506619 expected
events. No escape succeeds in either arm. The signal is a charged physical
register with upkeep; these are not uncosted action labels.

## What supplies the extra breadth?

With the preregistered destination order hazard, patch, energy, location,
signal, the W1-00 T64 comparison decomposes as:

| Coordinate | A-B conditional history contribution |
| --- | ---: |
| Hazard and patch | zero to numerical precision |
| Energy | -1.421278 bits |
| Location | zero to numerical precision |
| Signal | +1.679216 bits |
| Total | +0.257938 bits |

W1-08 has the same pattern: energy -1.512208, signal +1.665692, total
+0.153484 bits. The declared background process is genuinely matched here;
its contribution cancels in this particular decomposition. No background,
signal or struggle term is subtracted from the objective.

The signal-coordinate share is a conditional destination decomposition, not
a uniquely identified causal entropy contribution of a reaction family. The
native event ledger separately shows fewer total jumps in the worse arm:
W1-00 has 36.741946 versus 37.214010 expected jumps by T64; W1-08 has 36.152841
versus 36.656883. Thus “the worse world simply has more events” is not the
explanation at this cadence. Resolving the physical signal supplies distinctions
that compensate for reduced energy-path breadth in the sampled representation.

## Why neither is a stronger corridor kill

At T64 the resolved ranking varies with cadence:

| Case | dt 0.125 | dt 0.25 | dt 0.5 |
| --- | ---: | ---: | ---: |
| W1-00 | -0.065599 | +0.257938 | +0.479025 |
| W1-08 | -0.196217 | +0.153484 | +0.390743 |

Those sign differences persist in the limiting offset. This is temporal
dependence, not a failure of numerical precision or a rescue by a later horizon.
No crossover location was computed in this batch.

Hiding the signal reverses the positive rankings. At T64, dt 0.25,
the certified A-B interval is [-1.421278,-1.410772] bits for W1-00 and
[-1.512208,-1.505006] for W1-08. All 192 registered merged-signal K1
comparisons are strictly negative. The bounds are valid for the non-Markov
observed process; no projected CTMC was substituted.

The registered main criterion requires positive ranking at both grains, every
cadence, both long horizons and the applicable limit. No point meets it.
Nevertheless, merging a physically real signal deliberately omits a distinction
being tested. Failure of the stronger corridor criterion does not invalidate
the fully resolved, registered functional counterexamples. It does not license
choosing the merged grain as the preferred ethical metric after seeing results.

## K2: independent firing did not instantiate the intended nontracking object

Two of sixteen primary raw D-versus-max(E-prime,N-prime) comparisons are positive:
W2-00 +0.802271 bits and W2-08 +0.430365 bits. Neither is a clean K2 hit.

At every primary W2 point, D fails the registered low-MI nontracking condition.
Independent activation can still correlate with subsequent narrowing through
its physical costs and behavioural consequences. Conversely, E-prime fails
tracking and sustained disposition in this rare-hazard preparation. Every W2
point also improves successful escape beyond the frozen comparator tolerance,
triggering the functional-gain veto. These outcomes are retained rather than
repaired by redefining T, relaxing occupancy thresholds or erasing escape gains.

The appropriate result is **K2 not instantiated**, not “hijacked suffering
cannot win.” This first batch has not tested that proposition cleanly.

## Interpretation and next boundary

The unrestricted *functional* claim that adding an obstructed tracking aversive
state necessarily reduces fully resolved sampled-history lushness fails in
these declared regimes. The failures are small, exact and persistent as offsets,
while their sign depends on temporal and state resolution. This is evidence
against sufficiency of that operational readout as an unrestricted ethical
proxy, conditional on the chosen functional interpretation.

It is not evidence that real felt suffering is morally desirable. The model is
a coarse physical controller, its tracking diagnostic is local, its cost ratios
are model assumptions, and its background is not microscopic thermal physics.
Those scope limits were registered before the run.

The next useful diagnostic is the temporal crossover profile on these fixed
pairs, under a separate registration. The next K2 model must separate an
external narrowing detector from signal-induced downstream narrowing while
also providing a functional tracking comparator. W3 sensitivity design and W4
domination remain unimplemented. Neither should be silently appended to this
completed protocol or used to reinterpret these K1 findings.

## Verification and storage

- Scientific wall time: 42.738 seconds; peak memory: 140.8 MiB.
- Hard caps: 600 seconds, 512 MiB, 64 MiB output; none hit.
- Maximum numerical residual: 1.82e-12.
- 45 focused and neighbouring tests pass; static checks clean.
- Full grid, raw signs, eligibility and vetoes: FIRST_BATCH_SUMMARY.json and
  FIRST_BATCH_PARAMETER_MAP.csv. Raw per-arm readouts remain in the ignored run.
- Input hash: `d4027d688924ccc02627421b96415e3c3e8f55f00a9ce9be70eeca22f5f5d191`.

Some equal entropy-bound endpoints reversed by floating-point errors of at most
2.3e-12 bits. Reporting expanded them outward within the already frozen 1e-8
residual gate; the 1e-5 scientific comparison tolerance was unchanged. The raw
results are preserved. No physics, grid or qualification threshold was changed
after scientific inspection.
