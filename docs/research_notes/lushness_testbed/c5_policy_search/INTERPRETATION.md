# Reactive allocation: what the complete policy search shows

**The whole-field optimum changes its response with physical state and horizon.**
The first exhaustive assay compares all 36 tables available to one paid local
selector, from the same preparation and with the same underlying reaction menu.
At T64 and T256, a nonconstant table beats every constant response at all three
cadences. The numerical comparison decides the winner; no preferred behaviour
was put into the objective.

## The policy result

Rows specify the command target with one and two working D apparatus units.
They do not specify the selector's instantaneous conformation: switching takes
time, spends stored energy, and has a physical reverse.

| Horizon | Whole-field winner | Cadence dependence |
| ---: | --- | --- |
| 16 | idle / idle | Same at all three clocks |
| 64 | idle / donate | Same at all three clocks |
| 256 | donate / extract | Same at all three clocks |
| 1024 | donate / extract at 0.125; extract / donate at 0.25 and 0.5 | Winner changes with cadence |

At T256 and cadence 0.25, donate/extract gives 891.024518 bits. The best constant
table, extract/extract, gives 886.154679: adaptation adds 4.869839 bits. This
advantage remains positive at the other two clocks, at 5.763627 and 4.042148 bits.
The corresponding T64 advantages over the best constant table are 4.579475,
3.691920 and 2.865168 bits.

Stationary rate is useful here as a diagnostic of the horizon change. At cadence
0.25, extract/donate has a slightly higher rate than donate/extract, 3.596457
versus 3.594189 bits/time. Donate/extract wins the actual T256 comparison;
extract/donate wins T1024. Rates explain part of that comparison rather than
replacing complete finite histories with a rate-first ordering.

## What those mode names actually do

All five physical modes remain available through autonomous selector relaxation
and command reversals. A table commanding donation does not pin the world into
permanent donation. Native reverse transport also remains possible.

At T256, donate/extract moves a net 0.772098 energy units toward D. Hold/hold,
the no-command reference, moves 0.171964 toward D. After every cost, conversion,
capture and refund is included, the winner's D owned energy at the deadline is
0.015699 above that reference; S owned energy is 0.090203 below it. This is a real
positive endpoint material advantage for D, not a name assigned to an action.
It does not establish that this table is D's own optimal choice.

Both marginal history breadths increase relative to hold/hold. D's certified
difference interval is [254.5371, 306.4701] bits; S's is [44.8877, 95.2482] bits.
Lower S stock therefore does not amount to narrower S histories in this assay.
S's time-mean apparatus count falls from 0.739333 to 0.708527; that readout is kept
alongside the positive breadth result rather than substituted for it.

## Activity remains part of the result

Commanding idle is physically different from holding the selector alone. The
constant idle table enables forward paid commands and reverse refunds; these
move actual selector and bank coordinates. At T256/cadence 0.25 it already adds
223.919394 whole-field bits over hold/hold. The overall winner adds 286.446242.

Expected native jump counts rise from 89.119482 for hold/hold to 124.744372 for
idle/idle and 138.334079 for donate/extract. Accepted net boundary work rises from
15.729799 to 16.634422 and 18.009346 energy units. These are observed differences
under the shared resource prescription, not matched-work comparisons. They do
not supply a unique additive attribution of entropy to switching or capture.

The objective is allowed to prefer that physical activity. It has not been
cleaned out as a nuisance after the run. Matching activity or fuel remains a
way to investigate the mechanism, not a condition that the optimizer must obey.

## What is resolved about the subject question

The search resolves the whole-field optimum within this controller class. It
does not resolve a unique D-optimal or S-optimal table. At T256/cadence 0.25,
14 D candidates and 21 S candidates remain in the respective possible-maximizer
sets. The whole-field winner belongs to both sets. An outer set containing a
table does not certify that the table is optimal.

Across the complete 7,560 pair/clock/horizon comparisons, 19 have separated D/S
rankings, while none has a separated D ranking opposed to the whole-field
ranking at the current bound depth. Those are counts of correlated comparisons,
not independent observations. The absence of a certified opposition does not
prove agreement. The earlier spatial friction result showing D+/S-/whole-
therefore remains separate evidence; it is not overwritten by this assay.

All policy/horizon gains against hold/hold retain their sign over the three
cadences, but the identity of the long-horizon maximizing table changes. That
distinction is retained in the automated readouts.

## Scope and the next physical expansion

This adapter fixes both parties in contact and tests paid catalytic allocation.
It contains resource competition and joint transfers, but no movement, spatial
confinement, discovery or irreversible material loss. Its apparatus channels
are not certified conscious valuers. It is a tractable first policy-search
assay, not a replacement for the spatial domination programme.

The next useful transfer is this same selector-and-table architecture into the
spatial opportunity/harm world, with confinement and productive access both
available. Leading subject comparisons also need tighter marginal-history
queries before claiming that D would choose a different optimum. Population,
cross-scale composition and uncertainty are further extensions, with their own
physical state and costs, rather than hidden assumptions of these results.

## Verification

All 36 kernels are distinct; all 36 executions completed under the caps. Wall
time was 722.468 seconds with two workers, and maximum worker memory 364.5 MiB.
The maximum checked resource/solver residual was 8.88e-10. Focused engineering
checks cover thermal detailed balance with all channels enabled, both energy
accounts, fractional costs, physical command reverses and exhaustive table
coverage. The new streamed subject query agrees with the original tensor query
and encloses directly enumerated small hidden-Markov histories.

The compact report packet is about 4 MiB; full transition kernels are not saved.
The specification, exact source snapshots, configurations, receipts and full
signed policy map are retained. Nothing has been committed or pushed.
