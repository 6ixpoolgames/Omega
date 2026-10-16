# Next batch: reserve-sensitive control

Draft scope, 2026-10-14. Engineering and preregistration first; no science launch
authorized by this file. This batch tests stage1, not every roadmap expansion.

## Engineering gate

Implement active/worn-count observations that remain unchanged across the gate
switching pair, retaining the existing embodied law and its fuel costs. Reject
fuel/gate-sensitive feedback until its physical mechanism is implemented. Keep
shared local policy parameters for this batch; independent controllers come later.
Verify old-policy embedding, physical rate ratios, aliases, and full-query runtime.
Freeze at most48 unique candidates per law, including all required old controls.

Mandatory reserve-sensitive coverage: for every nontrivial integer threshold
k=2,3 in the 3+1 world, include service for 0<a<k and each of mix25, mix50,
mix75 and export for a>=k. At a=0 commanded actuation is absent. Include k=1
constant-response controls and the all-service endpoint. Publish actual response
vectors for a=0,1,2,3 and alias maps; thresholds unattainable in the one-slot
compartment do not count as observed adaptation there. Add worn-sensitive policies
within the cap after this mandatory coverage. A positive-reach witness must show
each claimed adaptive policy issues distinct responses. Do not fill the family
with renamed old policies and interpret a null result as a test of reserve sensing.

## Proposed physical cases

Use the existing 3+1 inventory and shallow reversible depth -1 for a focused set:

1. No added shocks.
2. Independent shocks at the previous h=0.02 calibration.
3. Correlated shocks at p=1 with the same conditional first damage moments.
4. Independent shocks at h=0.04, twice that hazard, to test risk sensitivity.

Add one separate absorbing worn-damage sentinel with positive policy-independent
basal relaxation, no added shocks. This tests genuine closure consequences without
reintroducing frozen-gate residual classes. Keep all post-collapse activity.
These are prospective proposed cases; any feasibility changes precede the freeze
and are disclosed. Do not select hazard levels by whether protection wins.

Use native sampled-state history entropy at cadence0.25 and horizons1,4,16,64,256
in the existing physical time units. Retain the existing declared seed and matched
reference root law with their exact IDs/weights in the machine-readable freeze.
Do not silently substitute entropy of a root mixture for expected root-conditioned
entropy. Optimize each horizon separately and report log-breadth in bits, avoiding
overflow from exponentiation. No time-average objective and no horizon-weighted sum.

The maintained external drive makes256 a declared analysis horizon, not the end
of the physical universe. Include secondary asymptotic rates/offsets and any
certified crossings. Finite depletion or shutdown needs a later physical module.

## What to score

- Does richer observation change the winning physical response on reachable states?
- Does the winning response change with shock risk, rather than only its occupancy?
- What does each horizon's winner trade in closure, recovery, exposure and costs?
- How much lushness does the rate-first winner forgo at each finite horizon?
- Does the apparent protection advantage survive unconditional availability checks?

Keep policy adaptation and improved access as separate predictions. Allow negative
results: unchanged service, damage-favoured breadth, higher closure, and equal
breadth with different access outcomes. Exposure alone is not a verdict.

Register these fallible directional predictions at each declared horizon:
reserve-threshold policies beat constant responses; higher independent hazard
raises the service threshold; correlated shocks raise it at matched hazard; longer
horizons raise it. Compare canonical response vectors, not nominal threshold names.
For policies with worn-state dependence, report the response surface rather than
forcing a scalar threshold. Tied winners give an interval/set of responses; mixed
directions are inconclusive, not a selected favorable winner. A lack of risk
response is a failed adaptation prediction, not a general refutation of lushness.

For this implemented22-policy family, file the concrete stronger predictions as
well: at nonzero shock hazard a genuinely nonconstant reserve/worn response strictly
beats all six constant controls; doubling h=.02 to.04 increases service response
on the reachable audit surface (threshold2 to3 or extra worn servicing); matched
fully correlated shocks increase service relative to independent shocks. Identify
the physical response surface after aliases, not just a policy named 'threshold'.
Score separately per horizon; ties with constants do not establish strict advantage.
Count comparisons favoring higher service across the frozen horizons without
treating those correlated comparisons as independent statistical replicates.
All reserve/worn adaptation is a left-compartment result: with capacity1 the right
compartment has no second active unit and no active+worn state. Its outcomes can
change through exchange and the shared controller, but not through richer reserve
discrimination. Keep the absorbing-sentinel reserve prediction explicitly fallible.

Report the absorbing sentinel's reserve alongside reversible cases, but do not
attribute the contrast solely to irreversibility: their physical laws differ in
other respects. Increased exposure with hazard is an alert requiring fixed-policy
replay and access/cost analysis, not proof the optimizer seeks damage for entropy.

Always retain idle, service, export, half/half, preceding winner and best nonrandom
candidate. Replay policies across laws to separate altered behavior from altered
physics. Use one common T64 deadline and common-probe severity for protection
comparisons, even when the optimization horizon differs. Show all ties.

## Small resolution audit and budget

At cadences0.125 and0.5 replay the frozen primary candidate family in the no-shock
and correlated-shock cases only. Policies selected after seeing results are not the
sole audit set. This controls cost while allowing ranking changes to be detected.
Include relabeling invariance. Genuine state-grain projections are deferred until
their adequacy and hidden-Markov evaluation pass engineering; cadence robustness
alone must not be called full grain robustness.

Within the two audited laws, register fixed-pair sign stability across all three
cadences at common physical horizons: each primary-cadence winner versus idle,
service, export and the primary-cadence best nonrandom candidate. All belong to
the frozen family. Keep these identities fixed when testing signs; separately
report reoptimized winners at other cadences. Declare a three-way sign using
numerical error/tolerance (positive, unresolved/tie, negative). A certified
positive-to-negative reversal is a temporal-resolution sensitivity finding;
a transition to a tie is loss of strict robustness. Do not call it full grain
sensitivity or extend this result to unaudited laws.

Numerical tolerance, root records, candidate list, predictions, batch wall-time
budget and hashes must be filled before freeze. Use the roadmap's per-process
caps and measured resource forecast; no automatic full launch after smoke.

## Subsequent batches

Schedule the [locked-resource access fixture](LOCKED_RESOURCE_SPEC_r1.md) alongside
stage1 as an independent workstream with its own engineering gate and budget.
It need not wait for the domination module. This is not authorization to launch
parallel jobs beyond the measured memory limits.
The maintained-inflow increment is now explicitly scheduled for that workstream;
the completed finite-store smoke is its control. It needs another physical-model
smoke before scientific use. Between-law rate enhancement is a mechanism readout;
it does not replace primary complete-continuation lushness comparisons.

Stage2: tiny exact typed damage (capture versus repair/control), loss/restoration
queries, then costed repair-versus-construction allocation. Stage3 combines these
with disturbances to test what preserved capability enables. Stage4 adds separate
controllers, appropriation, complementarity and self-subject optimization.
Open-ended population expansion, a richer microscopic thermal reference and
criticality remain later work, not claims of this batch. Rule A remains parked.
