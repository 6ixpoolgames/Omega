# Stage1/3: adaptive access and protective choices

Status: implementation design, 2026-10-14. Read README.md in this directory first.
Keep the current physical law as a control; richer observation/action contracts
must be independently versioned. An expanded policy class is not a new finding
about the old class.

## Observation contract

Replace hard-coded `a>0` table indexing with a pure declared observation function.
The initial richer local frame exposes own active count, worn count, fuel count
and gate position. An optional bucketed observation is a named lossy projection,
not the default physical state. Foreign state is unavailable to local controllers
unless a physical sensing/communication channel is modeled. No event-family label,
future outcome, hidden policy ID or damage-history label may leak into observations.

After typed damage, use own counts of active capture and repair/control capacity,
damaged material, fuel and selector state. Initially controllers remain memoryless.
Past shocks can affect policy only through current physical consequences. Adding
memory requires explicit stored state, write/erase/maintenance dynamics and costs.

A lookup using local counts is a coarse physical response law. It does not yet
establish a thermodynamic sensor model. State this limitation; do not invent a
generic information-processing bill in its place.

## First controller family on the existing law

Provide a finite threshold-policy constructor, retaining all previous tables:

    if no active actuator: no commanded switch
    elif worn material exists and fuel >= repair_threshold: service response
    elif active <= reserve_threshold: service response
    elif fuel >= surplus_threshold: surplus response
    else: fallback response

Thresholds range over actual local counts. Responses come from the existing
idle/service/export/mixed library. Make the exact generated list and its size
available before solving. Do not claim this family exhausts all local controllers.
Asymmetric controllers have independent parameter records, with shared-controller
and left/right-swapped controls. Capacity-normalized thresholds are a separate
family from absolute thresholds and must not be interchanged after results.

There is an important physical constraint: a state-dependent policy can alter
forward and reverse rates differently when a switching event changes the observed
fuel or gate. Do not simply substitute it into the existing rate prefactors.

For the cheap compatibility slice, observations used to modulate a switching pair
must be unchanged by that pair (for example active/worn counts). That permits
reserve-sensitive switching while preserving existing thermodynamic ratios.
Fuel-aware or gate-aware commands require an explicit selector/sensing mechanism
with its energy/work accounting, or a proved symmetric spectator construction.
Implement the cheap slice first; reject unsupported observations rather than
quietly treating feedback as a free nonthermal drive.

## Meaningful allocation, staged

The existing service gate jointly enables construction and repair. It can test
reserve-sensitive service versus exchange, but cannot show a chosen allocation
between repairing damaged capability and constructing new capability.

The subsequent action module must expose at least repair, construction, exchange
and idle/operate modes. Implement a physical selector with bounded switching
rates and explicit costs, replacing/extending the existing gate rather than adding
an unrecorded action variable. Selection controls availability/barriers of reaction
pairs symmetrically; it does not add a score. Unselected native thermal routes remain.
Multiple commands compete for the same finite actuator/fuel budget, rather than
each receiving a full independent rate budget.

Before code, forecast the selector state expansion. A three-mode selector replacing
each binary gate multiplies the two-compartment state bound by9/4; independent
extra selectors can be much worse. Engineering may therefore stage a two-mode
repair/construction adapter separately from the exchange adapter. Label each
physical law and avoid claiming they are one jointly tested world.

## Scientific questions and readouts

Use risk0 and a short preregistered range tied to native wear/recovery timescales.
The independent/correlated damage comparison retains conditional first-moment
matching. Choose a common probe severity independently of the native shock law.

Primary hypothesis: enabling reserve observation changes the breadth-optimal
allocation as disturbance risk changes, and the new allocation improves a declared
unconditional continuation-access outcome relative to a fixed baseline policy.
Split this into two predicates: policy change and access consequence. Neither may
be inferred solely from a changed stationary distribution.

To compare different observation maps, evaluate policies on a fixed audit set of
physical states and report their commanded reaction propensities there. Report
on-policy occupation-weighted action flux separately. An unreachable table entry
change is not meaningful adaptation; include states with positive relevant reach.

Primary ranking is complete-continuation lushness at each declared horizon.
Retain rate-first/offset-second as a secondary operational comparator, following
[the comparison amendment](ROBUST_CONTINUATION_COMPARISON_r1.md). Report when its
winner differs and the finite-horizon breadth lost by following it. Compare
closure/recovery of all winners at a COMMON deadline. A high rate conditional on
survival is insufficient even for the rate diagnostic. Preserve old-run scoring.
Register equal-law fixed-policy replay: evaluate both the old and new winning
policies in each law, rather than confounding policy and environment changes.

Always report: unconditional function/access at deadlines; first-hit and retained
recovery; integrated functioning; closure; stock and exposure; common-probe reserve
with its conditioning denominator; construction, repair and transfer costs; full
breadth profiles. A conditional improvement with worse unconditional availability
is not an overall protection success. Increased exposure is a diagnostic, not an
automatic adverse verdict. The native breadth objective includes stochastic damage.

Retain passive idle, constant service, constant export, unconditional half/half,
the preceding binary-observation winner, and best nonrandom candidate from the
declared search. Report all objective ties and the range of access outcomes among
them, not just the favorable representative.

## Solver gate

Count generated policies, canonical aliases and unique kernel-plus-ledger models
before a scientific budget is frozen. For stage1, target a preregistered shortlist
of at most48 unique candidates per law initially, retaining required controls.
This is a restricted search, not a global optimum certificate. Larger finite
families may be batched only under a declared total budget.

If using policy iteration or a general MDP solver later, account for the physical
selector and sampled interval: `exp(delta*Q_policy)` couples within-interval
decisions. Rowwise optimization of already-sampled kernels is not automatically
equivalent to the original continuously responding controller. Require an explicit
decision-timing model and a small exhaustive equivalence check first.

Acceptance tests: old-policy embedding; observation non-leakage; paired-rate
thermodynamics; actual allocation witnesses; exact alias/readout agreement;
fixed-policy replay; all-tie preservation; and full-query capped profiling.
