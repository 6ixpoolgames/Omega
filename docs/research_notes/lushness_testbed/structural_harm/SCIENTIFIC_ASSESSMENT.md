# Scientific assessment: structural consequences of impairment

All twelve frozen cases completed, representing 264 declared controller rows and
216 distinct numerical evaluations. Every case used the same 3+1 inventory and
22-candidate family. Total charged execution was 1040.33 seconds (17.34 minutes),
under the 2400-second budget. Peak job memory was 268.59 MiB; no caps or numerical
gates failed. The compact complete report is 743078 bytes, with no raw kernels.

The primary objective is full conditional sampled-history entropy at each horizon,
from the identical pre-fault physical present. Rates remain secondary. Faults
reduce active apparatus by one in all three arms; recovery differs through fast
paired repair, slow paired repair, or irreversible loss of local powered-repair
hardware. No survival, stock or repair reward is added. The conditional post-fault
roots have equal apparatus impairment but different energy when hardware breaks.

## What changed in policy

Primary cadence 0.25, with mixtures named by their export percentage:

| Consequence | Hazard | T1 | T4 | T16 | T64 | T256 |
|---|---:|---|---|---|---|---|
| Fast repair | 0.02 | Export | Mix75 | Mix25 | Reserve3/Mix25 | Service |
| Fast repair | 0.04 | Export | Mix75 | Mix25 | Service | Service |
| Slow repair | 0.02 | Export | Mix75 | Mix50 | Mix25 | Reserve3/Mix25 |
| Slow repair | 0.04 | Export | Mix75 | Mix50 | Reserve3/Mix25 | Service |
| Repair-hardware loss | 0.02 | Export | Mix75 | Mix25 | Mix25 | Reserve3/Mix25 |
| Repair-hardware loss | 0.04 | Export | Mix75 | Mix50 | Mix25 | Service |

Reserve3/Mix25 services below three active units, and uses 75% service/25% export
at three. Both compartments share policy parameters; richer reserve discrimination
is possible only in the left compartment. These are stationary policies selected
for each horizon, not receding-horizon or uncertain agents.

H1 passed: service response increased in 22 of 24 adjacent primary horizon
comparisons, plateaued twice, and never decreased. C1 passed: fast repair versus
hardware loss changes the winner at T64 and T256 under hazard 0.02. Crucially,
hardware loss favors less servicing in those comparisons. Losing an effective
repair pathway can make use of remaining channels preferable to trying to repair
through it. This does not imply that more severe harm always elicits preservation.

R1 passed: doubling hazard increased service response in four of fifteen
mode/horizon comparisons (fast T64; slow T64 and T256; hardware loss T256).
The hardware-loss T16 comparison goes in the other direction, from Mix25 to
Mix50. The prediction was existential, not universal. Results show a response
within this physical model and candidate family; they do not establish an
uncertainty or moral-precaution theorem.

## Adverse outcomes retained

S1 fired for two distinct comparisons: Reserve3/Mix25 versus constant service
in fast repair at T64, and slow repair at T256. Each also appears under the
best-nonrandom comparator because service is that same baseline, not a second
independent adverse finding.

| Comparison | Cadence 0.125 | Cadence 0.25 | Cadence 0.5 |
|---|---:|---:|---:|
| Fast, T64: reserve minus service | -0.965799 bits | +0.206495 | +1.288463 |
| Slow, T256: reserve minus service | -0.240741 bits | +0.551416 | +1.392199 |

The positive primary-cadence advantages are therefore not sign-robust across the
registered temporal corridor. Cadence is only temporal sampling resolution;
this experiment makes no claim of full state-grain robustness.

E1 also fired: in slow repair at T64, the higher-hazard winner has stationary
exposure 2.165960 versus 1.897105 for the lower-hazard winner, an increase of
0.268856. The alert remains in the registered ledger. Fixed-policy replay explains
its composition: holding Mix25 constant, higher hazard reduces exposure from
1.897105 to 1.812415. Changing the policy at high hazard to Reserve3/Mix25 adds
0.353545. The extra exposed stock accompanies more servicing and higher stationary
active reserve (1.047309 versus 0.857735 across winners). Exposure increase alone
does not establish that the optimizer seeks damage for its entropy; attributing
that motive requires a separate causal comparison. Random damage remains counted.

## Structural damage, restoration and sustained breadth

In the hardware-loss arm at h=0.02, the T64 Mix25 winner has 0.805733 intact
repair assemblies on average at the deadline and an 87.16% chance of at least
one hardware loss. The T256 reserve winner has 0.696176 remaining and a 91.36%
loss chance. Hardware preservation is not maximized. Whole-channel closure is
zero because basal construction and thermal recovery remain accessible after
powered-repair loss. This is irreversible loss of one capability, with substitutes,
not irreversible extinction of all function or a demonstrated valuer.

Restoration means regaining the original left reserve of two active units. Under
the h=0.02 hardware-loss T64 winner, this is reached by T64 with probability
0.965681, but is present at T64 with probability 0.196592. First restoration is
therefore a poor substitute for maintained reserve; uninterrupted retention is
reported separately in the complete data.

Rate winners are constant service in fast and slow repair. Under hardware loss,
the h=0.02 rate winner is Reserve3/Mix25, and the h=0.04 rate winner is constant
service. Finite-horizon choices differ from those limiting choices. All hardware
is eventually broken in the loss arm's reachable limiting class; its rate describes
the remaining basal/actuation process, not preserved repair hardware. There is no
open-ended growth or autonomous upkeep loop in this damage experiment.

## What this establishes and what comes next

Making recovery consequences physically different changes policies, and the
richer reserve setting now admits some hazard-sensitive servicing. That supports
using structural Omega readouts to explain complete-continuation lushness. It does
not remove the central limitations: temporal ordering can flip, preserving a
particular capability remains instrumental, and basal substitutes make total
closure unavailable in this fixture.

The next proposed resource-use loop must physically fund the maintenance or
construction of its enabler. The current maintained-resource energies cannot
support free carrier recharge from downstream use. NEXT_LOOP_DRAFT.md therefore
sets out a new matched energy/coupling prescription, without retrofitting current
results. Separate later modules can test loss of substitutes/material and bounded
controller uncertainty. No new semantic rewards or persistence filter are implied.

See [automated report](report/RESULTS.md), [complete compact data](report/SUMMARY.json),
[frozen registration](PROTOCOL.json), [physical specification](SPEC.md), and
[next loop draft](NEXT_LOOP_DRAFT.md).
