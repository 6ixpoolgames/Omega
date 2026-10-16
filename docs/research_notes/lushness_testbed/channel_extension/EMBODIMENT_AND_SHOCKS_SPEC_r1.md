# Embodied actuation and matched shocks: implementation handoff for Sol

> Implemented amendment: see [embodiment_shocks/IMPLEMENTATION.md](embodiment_shocks/IMPLEMENTATION.md).
> The primary arm now adds policy-independent basal gate relaxation; zero basal
> remains a sensitivity. The preregistration fixes matched shocks and a common
> reserve probe. Increased exposure is a diagnostic flag, not an automatic hit.

Status: implementation specification, 2026-10-13. Scientific protocol remains
draft. Implement and engineering-smoke first; freeze predictions and budget before
any policy-ranking run. Work in the original Omega repository and active branch.
No commit, push, Drive publication or raw-output deletion is implied by this spec.

## Research question and fixed commitments

What additional native continuation does keeping functional machinery available
enable, and do correlated disturbances make the breadth optimizer preserve more
of that capacity? Test instrumental protection through downstream consequences.
Maximum apparatus stock is not the objective. Native physical randomness counts;
Rule A stays parked. Do not stop scoring at closure, subtract the thermal tail,
add a survival reward, or choose shock strengths by which policies win.

The current adapter permits controller-mediated gate switching after all apparatus
is trapped. That is a valid surviving-hardware world, but it does not model control
whose operation depends on the apparatus. Preserve it as a control arm.

The seven preceding grids remain unchanged. Their shallow-well S1 prediction
(winner retains more usable material than constant service) failed at all four
depths; S2 versus constant export passed. These are not maximum-protection tests.
See SCIENTIFIC_ASSESSMENT_r1.md for the current evidence and limitations.

## Scope and architecture

Reuse Event, RuleModule, WorldSpec, compiler, finite_classes, channel_access,
event_sequences, registry and frozen-run workflow. Exact and sampled execution
must consume the same native event enumeration. Readouts never modify the state
or transition law. Family labels are provenance, not additional entropy symbols.

Add independently versioned modules/configurations:

- `modules/actuation.py`: validated ActuationSpec and symmetric availability factor.
- `modules/shocks.py`: validated ShockSpec and explicit aggregate shock events.
- An experiment adapter/protocol version that composes these with growth and damage.
- Registered resilience and capability readouts, compact reporting and tests.

Use defaults `actuation=legacy`, `shocks=disabled`, reproducing old kernels exactly.
Do not silently reinterpret saved manifests. Module IDs, versions, parameters,
state schema and analysis versions participate in snapshot/cache hashes.

The first slice retains local state `(w,a,d,f,g)` and fixed inventory `(3,1)`.
Population remains coarse apparatus, not persons or lineages. No new controller
coordinate is necessary for this slice. A later independent controller/sensor
module may extend the state explicitly; this spec must not claim to implement it.

## M1: minimal embodied actuation

Treat active apparatus as the catalyst implementing gate switching. For each
compartment c and every existing controller-mediated switch event, set

    q_embodied(x,y) = b_c(x) q_legacy(x,y)
    b_c(x) = a_c / M_c.

This first law expresses independent per-unit actuator capacity with fixed
maximum capacity at full inventory. It is a declared physical hypothesis, not a
universal derivation. A binary `1[a_c>0]` availability law may be implemented as a
named sensitivity option, but is not added to the first scientific grid by default.

Switching changes fuel and gate state, not a_c. Therefore b_c(x)=b_c(y) on every
switch pair: multiply both directions identically, preserving their existing
forward/reverse ratio wherever the channel is enabled. Zero active apparatus
removes both directions. Retain native switch fuel stoichiometry and work/heat
accounting. Do not merely suppress the forward commanded switch.

This makes sensing/response a coarse catalytic dependence on local apparatus,
not a separately modeled measurement cycle. No fictitious sensing bill is added.
Independent sensor maintenance, memory and damage remain explicitly open.

When a_c=0, gates stay in their physical state until native apparatus recovery
allows control again. Passive exchange through existing open gates, bath/drive
carrier motion, basal reconstruction and all other native events continue.
No free gate reset at failure. Existing active-independent drive capture remains
an external maintained boundary, disclosed in the manifest.

Do not assert all post-collapse rates become equal: frozen gate configurations can
select distinct residual classes with different passive dynamics. Compute those
classes and their root-dependent absorption weights using the existing solver.
If a common thermal tail is desired later, it requires a separately specified
physical gate relaxation mechanism, not an analysis correction.

## M2: matched shocks

Introduce a disturbance module whose physical effect is one degradation step:

    A -> W; W -> D; P and existing D unchanged.

Use pre-event categories, so a single shock cannot send one A through W into D.
Initially the same per-unit hazard h applies to A and W. Distinguishing their
susceptibilities is a future explicitly versioned option, not a tuned first arm.

Independent arm: emit A->W at rate h*a and W->D at rate h*w per compartment.

Correlated arm: shocks arrive at rate nu. Each A or W unit present immediately
before a shock is independently hit with probability p. All selected changes
occur simultaneously across both compartments. Enforce nu*p=h.

For compartment c, enumerate k_A~Binomial(a_c,p) and k_W~Binomial(w_c,p).
The target is `(w_c+k_A-k_W, a_c-k_A, d_c+k_W, f_c, g_c)`.
Emit each nonidentity joint target at rate nu times the product of its binomial
probabilities. Aggregate duplicate physical endpoints in the ordinary compiler.
Do not enumerate molecular identity labels or add a shock flag to the state.

Both arms then satisfy, conditional on every physical state:

    E[active units damaged]/dt = h * sum(a_c)
    E[worn units trapped]/dt  = h * sum(w_c).

They also have identical instantaneous expected energy change from shock damage.
Their joint-event structure differs: p controls clustering, with nu=h/p. At p=1,
every vulnerable unit is hit together. As p approaches zero at fixed h, the
physical generator approaches the independent arm. Disabled shocks implement h=0
directly; reject p=0 in the finite correlated parametrization.

This is matched exposure conditional on state, not guaranteed equality of realized
damage totals after the policies change state occupancy. Report both the exact
matching audit and realized totals. Do not adjust hazards afterward to equalize
damage outcomes.

Shocks are an externally imposed nonequilibrium disturbance boundary. One-way
degradation is not claimed to satisfy thermal detailed balance. Record its signed
energy transfer separately from ordinary thermal heat and chemical drive. Map
that ledger consistently into the compiler's energy identity and document the
chosen boundary convention. If a thermal shock bath is implemented instead, its
reverse channels and temperature must be explicit and it becomes a different law.

No-effect shocks are invisible at this physical-state grain and are omitted from
Q. Do not manufacture entropy from an unobserved clock. Native state changes caused
by random shocks do count. Keep a diagnostic of clock rate and realized damage;
do not subtract a putative additive shock entropy from total history entropy.

## M3: access, closure and what the channel buys

For each policy retain the full rate/offset and horizon breadth profile, every
reachable recurrent class, class entropy rate and absorption probability. Include:

1. Structural access under available physical responses, and access under the
   actual fixed policy. Recompute with the actuator prerequisite; never infer
   actuation availability from policy weights alone.
2. First passage to loss of any-active reachability, compartment-specific loss,
   and paid-construction access loss. Exact positive recovery rates remain edges.
3. Recovery first hit, function at deadline, integrated functional occupancy and
   optional post-recovery loss. Keep these distinct.
4. Usable/active stock, gross build/loss, assisted construction, fuel used for
   service/switching, drive work, ordinary heat and shock energy transfers.
5. Residual rates and physical transition availability after apparatus closure.
   Identify whether variation comes from gates, carriers or surviving actuation;
   event counts alone are not an entropy decomposition.

Add matched counterfactual continuation queries for specified intact/damaged
states under one law and table. Their breadth difference is the future consequence
of different present conditions. If energy differs, disclose it; an energy-matched
repair/removal intervention must include its resource bill in the state. Do not
label a state comparison as a free executable action.

For timed resilience queries, propagate to a declared shock time, apply the same
normalized shock channel, then propagate under the native law. Label this a
forced-disturbance diagnostic, separate from the primary stochastic-shock world.
Preserve state uncertainty through the query; do not restart from an average state.

Compare planning-horizon winners at the SAME closure/recovery deadline. Retain
all tied winners with the registered numerical tolerance. The existing short-
horizon result is exploratory; new directional predictions must be frozen first.

## M4: experiments and freeze gates

Stage A: embodiment with shocks disabled, legacy hardware as control. Hold base
physical parameters, cadence, inventory and policy search fixed. Start with worn
absorbing damage and the already studied depth -1 reversible arm. Root/reference
comparisons stay within each law. Cross-module differences are mechanism contrasts.

Stage B: matched independent/correlated shocks on the embodied world, retaining
no-shock and legacy-hardware controls where needed to identify the interaction.
Provisional design: one nonzero h, two p values, absorbing and depth -1 reversible
damage. Do not launch a full Cartesian grid automatically. Final case list follows
engineering feasibility and a preregistered scientific budget.

Choose h from declared native wear/recovery timescales or fixed reference-policy
calibration, without viewing candidate policy rankings. Record calibration data,
selection rule and rationale. Choose p to span moderate and strong correlation;
register exact values before scientific execution. No favorable-results search.

Use the existing 36 shared local inactive/active response tables first. An
embodied world may make inactive responses behaviorally identical: detect exactly
equal generators, evaluate each once and retain aliases/ties. Do not treat aliases
as independent policies or extra branching. Future richer observations/memory
belong to a new controller search class.

Predictions to register as fallible, individually scored hypotheses:

- Kernel invariance, conditional shock matching and numerical accounting pass.
- Embodiment removes commanded switching at zero local active apparatus.
- Longer-horizon winners accept less closure risk at a common deadline.
- Correlated damage changes the optimum toward greater functional reserve or
  less simultaneous vulnerability. Specify the operational statistic before freeze.
- Preserved access yields greater downstream native breadth in designated matched
  queries. Allow sign reversal; no built-in requirement that repair must win.

The latter three are scientific hypotheses, not implementation acceptance tests.
Record negative and tied results. Equal expected damage does not imply a universal
ordering of closure risk. No target that the winner exceed constant-service stock.

## Acceptance checks and runtime gates

- Legacy defaults reproduce old Q, ledgers and endpoint laws.
- At a_c=0 all local controller-mediated switch rates vanish; at a_c=M_c they
  equal legacy. Other rates are unchanged. Forward/reverse switch ratios agree.
- Shocks conserve material and bounds, implement one step per selected unit,
  match conditional first moments analytically at small inventories, and approach
  the independent generator as p decreases. Self-events add no state-path entropy.
- Hand-solvable one-unit/two-unit shock fixtures verify joint-event probabilities.
- Source support includes every physically involved compartment; energy and gross
  damage ledgers close; shock boundary transfer is reported separately.
- Exact and sampled modes use one kernel; a bounded statistical check compares
  endpoint/damage expectations with declared tolerance and fixed seeds.
- Closure witnesses, multiple recurrent classes and recovery queries pass analytic
  fixtures. A frozen gate is not silently reset and is not counted as active control.
- Relabeling and bookkeeping channel splitting leave aggregated-grain results
  unchanged. Physical state refinement remains a separate grain, not an invariance.
- Freeze/hash execution includes new sources; cache keys distinguish module laws.

Run 1+1 engineering smoke with hard 120s/1GiB/256MiB process-tree caps, one numerical
thread. Then one complete 3+1 policy preflight, including all new readouts, under
600s/1GiB/256MiB. Forecast the full search from that measurement and exact kernel
deduplication. If it exceeds budget, split capped batches or optimize computation;
do not silently shrink the physical world or omit difficult policies. No more than
two concurrent full jobs at the currently measured memory footprint.

## Deliverables and continuation workflow

Deliver source, focused tests, MODULE_CONTRACTS.md updates, an engineering report
with measured cost, a LIMITATIONS.json update, and a machine-readable draft
protocol with named outcomes and an explicit unresolved freeze gate. Include a
plain-language interpretation template separating rate, offset, access, recovery,
resource accounting and model limitations. Scientific runs require the later
frozen protocol; this handoff authorizes implementation and engineering smoke only.

Compact reports retain every policy/alias, verdict, run hash and numerical audit.
Raw arrays, state/class vectors and source snapshots stay in ignored local runs.
Keep current safe cache inventory and dry-run eviction behavior; no automatic
deletion of cited or pinned evidence. Do not copy full result.json into Git reports.

Further modules remain independent: controller memory/sensing, autonomous gate
relaxation, external drive failure, population expansion, spatial thermal baseline,
cross-scale agency and criticality diagnostics. Each addition gets a native-law
contract, disabled-module compatibility test, physical ledger, readout contract,
feasibility gate and prospective protocol. The objective does not change merely
because the model gains a new failure or recovery mechanism.
