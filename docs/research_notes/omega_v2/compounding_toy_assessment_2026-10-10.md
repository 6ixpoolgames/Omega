# Compounding breadth toy: assessment and next audit

**Status:** analytical review of the user-supplied `compounding_toy_report.html`,
10 October 2026. The report attributes its results to `compounding_toy.py` and
`run_report.py`; neither source file was supplied or found in the workspace.
Reported simulations have not been reproduced. No new numerical experiment was
run for this review. The attachment and its embedded images remain outside Git.

## What the toy contributes

The stipulated law offers background moves, tool-use moves and construction
moves enabled by tool pairs. Products persist and can enable further products.
All arms reportedly share the same production table and law, with different
initial inventories. A 1,000-type repertoire bounds construction; resource inflow
and heat leakage continue. A high-closure seed reportedly overtakes a control
starting with four times as many moves near step 3,145, then reaches about 11
bits per update against 7.3. A low-closure seed remains near 19 tool types.

This is a useful candidate mechanism witness: investment in products can create
later construction opportunities and repay an initial branching disadvantage.
The measure contains no separate semantic reward for a generator. The law does,
however, stipulate that tools provide two use choices and that their products
are durable. The experiment therefore investigates this law's consequences;
it does not independently establish those physical assumptions.

Construction saturates at 1,000 types. The continuing entropy-rate gap then
reflects repeated use of unequal retained repertoires, not ongoing repertoire
growth. Distinguish the generative episode from its persistent legacy. A fixed
state universe containing all inventories can represent this entire episode:
newly accessible states need not be newly created mathematical states.

## First gate: which histories are being counted?

For M(x) uniformly selected event choices e, the conditional **event-choice**
entropy is log₂ M(x). If each choice has a deterministic successor f(x,e), the
state kernel instead has

\[
K(x,y)=m_y(x)/M(x),\qquad
m_y(x)=|\{e:f(x,e)=y\}|,
\]

\[
H(K(x,\cdot))=\log_2 M(x)
-\sum_y\frac{m_y(x)}{M(x)}\log_2 m_y(x).
\]

Equivalently, H(E|x)=H(X'|x)+H(E|X',x). These coincide when the event is recoverable
from the successor. Distinct physical events with the same modeled endpoint can
also belong in complete developments, but the physical event distinction must
be supplied. It cannot be justified solely by naming simulator choices.

The report says the controls are deterministic in state while assigning positive
breadth to them. Thus either their event choices carry additional physical
history, or the calculation measures random scheduling labels omitted by the
state description. The HTML does not resolve this. Audit complete developments,
not just endpoint states: a genuinely different intervening physical event need
not leave a permanent record to count.

Use two invariance checks. Splitting one mathematical event label into duplicate
labels with its weight divided must leave physical breadth unchanged. Adding
an actual physically distinguishable alternative may change breadth. Compute
both endpoint-state and resolved physical-event histories from the same law,
showing explicitly why they agree or differ. If resource arrivals, leakage or
outcomes are additionally random, include their conditional contributions in
the joint law; log M alone is then not automatically the full history entropy.

## What makes the sustained gap possible?

Irreversible retained tools can preserve differences between preparations, but
durability alone does not prove multiple recurrent classes. All roots might
still reach the same final inventory. Establish reachable closures and the
actual long-run classes or invariant sets. The thermal and inert roots appear
unable to reach the generative repertoire; if so, the comparison spans different
long-run sectors. This is informative, but is not excess over the generative
root's own stationary reference.

Adding tool decay does not automatically restore irreducibility. If the last
generative seed can disappear and no native route recreates it, extinction can
be an absorbing class. Conversely, maintenance within a finite irreducible,
aperiodic chain does not evade the mixing theorem. It may prolong a metastable
regime substantially; preparation-dependent rate advantage still disappears
asymptotically. This corrects the report's phrase "unless maintenance is modeled."

The finite-mixing theorem also requires a finite sufficient state space. Resource
or heat variables may be unbounded or continuous in this toy; their actual
implementation must be inspected rather than inferred from the finite type list.
External drive, persistent initial inventories and irreversible construction
must be analyzed separately.

## Controls and physical accounting

The inert workshop and noise-ahead controls are useful. Matching resource influx
is not full resource matching: the inventories differ, construction has a cost,
use choices apparently persist without specified operating cost, and heat choices
leak away. Thermal here names a stipulated background, not a derived equilibrium
gas. Report clock conventions, storage bounds, integer versus continuous heat,
resource bookkeeping and what the exported heat does outside the modeled region.
A subsystem comparison with a common reservoir is legitimate, but differs from
a complete-universe comparison that includes the reservoir and its histories.

A particularly discriminating additional control is **durable non-reproductive
construction**. Under one common law, allow another seed type to convert the same
resource into equally durable products with the same physical use alternatives,
but without offspring enabling further constructors. Compare against recursively
enabling products and short-lived heat. This separates the value of durable
storage from the additional effect of recursive enabling. Match initial material
and initial branching where possible; report the noise-ahead arm separately as
a stress control. Do not match complete path entropy, which would force a tie.

The two use alternatives per tool must have physically modeled consequences and
weights. Treating labels as branches or selecting parameters to force a desired
ranking would not establish the intended mechanism. Vary durability, operating
cost, heat retention, construction access and seed closure independently.

## What the sweeps establish

The reported sweeps suggest sensitive dependence on heat export, inflow and seed
closure over 20,000 updates. They do not establish asymptotic critical thresholds.
At zero leakage the report shows no takeoff by 20,000, not a proof that takeoff
never occurs. Every positive inflow displayed has a reported crossover; the
inflow table therefore does not bracket a no-compounding threshold.

The production table is part of the fixed law. Separate uncertainty across
stochastic runs under one table from robustness across separately sampled tables.
Report random seeds, seed-selection rules, per-arm uncertainty and the definition
of the crossover statistic. Crossing mean curves is not necessarily mean
per-run crossover. The main baseline crosses at 3,145, whereas nominally matching
sweep rows show 3,105; different sampling batches could explain this, but the
source should identify the reason. The 200-run claim alone supplies no error bar.

A difference of expected logbreadths yields a ratio of geometric mean breadths.
Exponentiating it does not give the ratio of arithmetic mean breadths. Keep the
bits and rate gaps as primary reports; large exponentiated ratios add little.

## Recommended sequence

1. Obtain the two source files and enough configuration/seed information to
   reproduce the existing report. Preserve its results as supplied evidence.
2. Resolve the physical event/state distinction and audit the native transition
   probabilities, label invariance, clock and resource boundaries.
3. Identify recurrent structure and separate construction, saturation and fresh
   continuation. Verify the claimed rate plateau against the actual kernel.
4. Add the durable non-reproductive control, then independently vary decay and
   maintenance. Classify extinction, metastability and mixing before interpreting
   long-horizon gaps.
5. Only after those checks, enlarge the repertoire or vary cutoffs to investigate
   compounding duration and scaling. No new quantum or universal extent claim is
   needed to make this classical mechanism test useful.

The toy advances the mechanism question. Its present evidential claim is a
reported construction-to-breadth effect under a transparent stipulated law.
A physically grounded gas comparison and a reproduced complete-development
breadth result remain separate deliverables.
