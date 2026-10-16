# Weighted timing-volume counterexample report v0

Date: 2026-10-01. Status: **candidate rejected as a complete lushness comparison**.
This is a reproducible mathematical counterexample in a declared finite model,
not an independent empirical finding or a cosmology result.

## Result

The frozen probability-weighted timing-volume profile ties four arrangements
at every horizon, although their records, downstream access, and recovery
trajectories differ. The full process represents the differences. Its summary
loses them. No coefficient, event exclusion, alternative partition, or added
coordinate was fitted after observing this result.

The [contract](timing_volume_counterexample_protocol_v0.md) was written before
the implementation and numerical run. Its SHA-256 (UTF-8, LF newlines) is
`0d11446db47cab51d23131b2b5412b5dbc713d837b3c045ac837d3ecf63cd538`. The all-horizon collision was an explicit analytic
prediction in that contract. Checking it is not independent discovery.

## Frozen comparison

An exact-n-event trace class c has timing volume v_c(H)=m_c H^n/n!, where m_c
counts its disjoint chronological domains after independent presentations are
grouped. The candidate is L_n=sum_c p_Phi(c;H) v_c(H), with ordinary physical
conditional probabilities, including no-event and unfinished histories.
Coordinates retain their time^n units; neither dimensions nor horizons are
summed. This report rejects this particular functional, not all possible
probability-weighted volumes.

The reference is one common guarded physical update table: record acquisition,
retention/erasure, relay, record-keyed assembly/repair, then downstream forwarding.
One shared actuator serializes updates. Each uses one unit of a ten-unit fuel
stock and incurs one actuator operation. The packet registers replenish in
the second cycle; this is not the earlier private-fuel once-only class.
Only initial wire/switch/socket orientations differ. The preparation bill is
declared and equal; no realistic thermodynamic equivalence is asserted.

## Why the tie holds for every horizon

All reachable nonabsorbed states have total firing rate 1. Ten firings exhaust
the physical stock. Consequently N_H=min(Poisson(H),10), in every arrangement.
All updates share the actuator and fuel, so every trace class here is one
serial word with timing volume H^n/n!. Therefore

    L_n(H) = P(N_H=n) H^n/n!,  n=0,...,10.

Only the number of firings survives this aggregation. Their physical effects,
the location of accessible records, and the future couplings they establish
do not. This is a class-wide identity for serial constant-total-rate models
with this stopping stock, not an inference from five sampled deadlines.

For n<10 the count probability is exp(-H) H^n/n!; n=10 retains the entire
Poisson upper tail. It is not dropped or renormalized. At H=0 the known empty
history is the sole positive-probability event-count sector.

All four profiles at H=4 (separate units time^n):

| n | L_n, each arrangement |
|---:|---:|
| 0 | 0.0183156388887 |
| 1 | 0.29305022222 |
| 2 | 1.17220088888 |
| 3 | 2.08391269134 |
| 4 | 2.08391269134 |
| 5 | 1.33370412246 |
| 6 | 0.592757387759 |
| 7 | 0.193553432738 |
| 8 | 0.0483883581844 |
| 9 | 0.00955819420927 |
| 10 | 0.00234988828898 |

## Structural differences retained by the process

The source is a fair physical bit. The reference records joint laws, not a
selected utility or an optimized achievement target.

| Arrangement | After event 3 | After event 4 | After event 5 | After event 10 |
|---|---|---|---|---|
| Intact | Relay carries source bit | Link installed | Downstream carries source bit | Downstream carries source bit |
| Damaged coupling | Relay is blank | Wire repaired and link installed | Earlier obstruction still leaves downstream blank | Next cycle transmits source bit |
| Erased record | Relay is an independent fair bit | No record key; link absent | Downstream blank | Downstream blank |
| Cycling apparatus | Relay carries source bit | Rotor turns; link absent | Downstream blank | Downstream blank |

At the first boundary, all preparations physically record the source. At the
second, the erased preparation has r=blank and source posterior (1/2,1/2) from
that accessible register. The other preparations retain the bit. The analyst's
full histories still include the old record; the physical reader never sees
those histories. Every blank-reader outcome remains in the law and volume.

Wire repair occurs at the fourth firing in the damaged preparation and is
permanent under these rules: the corrected region w=1 is closed. This does not
restore the already missed first-cycle transmission. The first nonblank
downstream output occurs at event 5 for intact and event 10 for damaged; it
never occurs for erased or cycling. Thus their deadline probabilities are
P(Poisson(H)>=5), P(Poisson(H)>=10), 0, and 0 respectively:

| H | Intact | Damaged | Erased | Cycling |
|---:|---:|---:|---:|---:|
| 0.5 | 0.00017211563 | 1.70967003e-10 | 0 | 0 |
| 1 | 0.00365984683 | 1.11425478e-07 | 0 | 0 |
| 2 | 0.0526530173 | 4.6498075e-05 | 0 | 0 |
| 4 | 0.371163065 | 0.0081322428 | 0 | 0 |
| 8 | 0.9003676 | 0.283375741 | 0 | 0 |

These are witnesses of propagating obstruction and generated access within
the full process. They do not define lushness by a favored task. Construction
is an explicit new coupling under fixed rules; nothing requires a new law or
an outcome unpredictable from the complete initial dynamics.

## Verification and reproducibility

The engine enumerates every physically possible finite history. Jump-boundary
probabilities use exact rational arithmetic. Timed probabilities use numerical
matrix exponentials and are checked against a separate state-space CTMC
calculation and the analytic count law. No trajectories are sampled.

Maximum numerical residuals in this run:

- Total probability: 5.55e-16.
- Path enumeration versus state-space CTMC: 2.22e-16.
- Intermediate-cut composition: 1.72e-15.
- Profile versus analytic Poisson certificate: 1.42e-13.
- Difference between paired profiles: 1.42e-14.

Tolerance: 2e-11. Machinery gates passed: True.
The companion tests separately check independent/exclusive/enabling race laws,
three-way diamond grouping, relabeling, subdivision as integration, positive
duration, physical fuel/cost accounting, record erasure, conditioning, repair
persistence and composition-generated access. Passing these verifies the
implementation; the candidate's substantive result is failure.

Run from the repository root:

```text
python -m pytest tests/test_timing_volume_counterexample.py -q
python -m omega_v2.validation.timing_volume_counterexample_v0
```

[Machine-readable evidence](../validation_results/timing_volume_counterexample_v0/20261001/evidence.json)
contains the common rule table, full paths, endpoint laws, record-conditioned
frames, costs, calibrations, versions, source hashes and repository state.
The output directory for this run is `docs/research_notes/validation_results/timing_volume_counterexample_v0/20261001`.

## Consequence and limits

Keep the complete weighted continuation process and these counterexamples.
Retire L_n as the proposed complete comparison. Do not proceed to the large
lattice sweep with this volume, or append a bonus to rescue its rankings.
Any successor must explain how it uses causal incidence and residual coupling
that the present functional discards. That is a new mathematical obligation,
not a completed replacement measure.

The model's physical mechanisms are stipulated. The collision refutes a
completeness claim for this summary; it does not prove a universal moral order,
establish a noise filter, reject the substrate motivation, or establish the
adequacy of the quantum object. No quantum-volume extension, Planck cutoff,
cosmology release, unseen-world evaluation, or push accompanies this report.
The collision concerns L_n at the stated comparison frame. It does not show
that an atlas retaining the occurrence, weights and relationships of all frames
is identical between arrangements. Those relationships remain in the process;
no complete volume functional on that richer atlas has been supplied here.
