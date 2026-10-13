# Modular channel-loss and recovery extension — implementation handoff

**For Sol. Draft r1, 13 October 2026.** This specifies implementation and engineering
validation. It is not a frozen scientific preregistration or an instruction to run
a research sweep. Continue in the original Omega repository, current active branch.
No commit, push or publication is implicit in this handoff.

## 1. Research purpose and commitments

The recurring workflow is: identify a missing modeled consequence, add a versioned
physical module, validate its consequences, then test the same lushness objective
in the expanded world. Expansion should produce comparable experiments without
turning each experiment into a new engine.

The immediate question is whether maximizing native weighted continuation sustains
the capacity for further continuation when that capacity can be damaged, recovered
at a cost, or become inaccessible. Maximum active population is a diagnostic
benchmark. It is not the ethical objective. Structure matters through its effects
on native continuation; add no survival, protection, welfare or generativity bonus.

Keep the unfiltered sampled full-state history entropy objective. Thermal motion,
stochastic damage, random control and post-collapse branching all count at the
declared grain. Rule A remains parked. Coarse population remains functional
apparatus, not identified valuers, lineages or new autonomous controllers.

The motivating dynamical idea is renewal that keeps enabling channels available
while opening further continuation. Literal criticality remains an optional
hypothesis. Do not build an edge-of-chaos preference into either law or objective.
The ethical bridge remains value requires valuers plus conditional normativity.

Previous G4 maintenance results stay as registered. Future reports call the
quantity a **functioning-margin trade-off**. Correcting its ethical interpretation
does not change the numbers or retrospectively turn it into a passed channel test.
Any channel analysis of earlier runs is explicitly exploratory.

## 2. Architecture assessment: reusable foundation, incomplete modularity

The current model can support this extension after a bounded refactor. A full
rewrite or a new substrate is unnecessary. The following observations come from
inspection of the current implementation, including uncommitted growth work.

| Current component | Reuse | Required change |
|---|---|---|
| `omega_v2/testbed/growing_population.py` | Native event generation, thermodynamic accounting, sparse generator and counted state | State is fixed to two `(w,a,f,g)` tuples; rules and ledger updates are hardcoded together. Introduce state/rule/accounting interfaces and preserve the old adapter. |
| `growing_reference.py` | Independent labeled-body projection checks | Extend independently to the new material state; do not derive the reference by calling the production event emitter. |
| `growing_comparison.py` | Finite entropy recurrence, sparse flux surveys, policy enumeration | Remove policy-specific gate restriction from the generic solver; detect reachable states and recurrent classes from actual transitions. Extract objective, query and survey code from experiment orchestration. |
| `controlled_slice.stationary` | Single irreducible-class stationary solve | Retain as a checked specialized method. It cannot solve a world with transient states and multiple closed classes. |
| `bng_network.transition/history_bits` | Small exact sampled-state calculation | Add memory/capability gates; sparse Q does not imply sparse sampled transition matrix. |
| `run_growing_comparison.py` and capped runner | Process-tree caps, manifests, hashing, artifact inventory | Execute the frozen source bundle, not the live checkout. Current worker imports the live repository after snapshots have been taken. |
| `report_growing_comparison.py` | Compact tables and automated outcome evaluation | Replace experiment-specific prose/scoring with versioned readout and comparison records. Interpretation must distinguish observed trade-offs from ethical verdicts. |

The interfaces already proposed in [experiment-workflow.md](experiment-workflow.md)
remain the design spine. This handoff makes their next implementation concrete.
The [foundation contract](testbed-foundation-contract.md) and
[measurement contract](MEASUREMENT_r1.md) still apply, with Rule A parked by the
later user instruction. Historical modules and reports remain reproducible.

## 3. Minimal extension contracts

Use small typed Python interfaces/dataclasses and an explicit registry. Do not
start with a general plugin loader, new DSL or arbitrary executable JSON formulas.
The first extraction should support the old growth adapter and this extension.

| Contract | Required responsibilities |
|---|---|
| `WorldSpec` | Versioned physical fields/species, compartments/incidence, units, parameters, material constraints, boundary assumptions, enabled modules and dependencies. |
| `StateCodec` | Immutable state encoding, validation, canonical index/order, field access and optional bounded state enumeration. No assumption that all future models can enumerate every state. |
| `RuleModule` | Stable ID/version, required fields/capabilities, event enumeration from the sufficient present, declared support and rate law. No access to scores or report verdicts. |
| `Event` | Rule/family ID, target, nonnegative finite rate, read/write support, reservoir exchanges and event increments. Source is supplied by enumeration. IDs support audit and do not themselves add entropy. |
| `Accounting` | State energy, conserved totals, optional degeneracy and equilibrium law, named extensive quantities and signed event exchanges with units. Derive state deltas centrally. |
| `ControllerSpec` | Observation, memory if physically present, response table, action implementation and costs. Search randomness is separate from stochastic execution. |
| `MeasurementSpec` | Physical state grain, cadence, objective version, supported likelihood operations and tolerances. Analytical survey flags are not part of the measured physical state. |
| `SurveySpec` | Versioned target/predicate or event functional, required capabilities, estimator, units, supported horizons and missing-result reason. |
| `ExperimentSpec` | Roots/references, laws, controllers, comparisons, hypotheses, numerical budgets, seeds, artifact policy and freeze status. |

Composition must be explicit. A module declares fields/rules it adds and any
existing rule it replaces. Reject duplicate IDs, missing dependencies and
undeclared overrides. Module order must not change the law. Independent physical
channels leading to one resolved target add rates in Q; their separate resource
exchanges remain in the event ledger. Never multiply whole-generator rates as an
implicit side effect of enabling a feature.

State extensions may change constraints used by old rules. In this slice, every
rule must obtain available precursor count from the shared state schema, rather
than retaining an old `M-w-a` expression that forgets the new inaccessible pool.
Such incompatible extensions require a new adapter version, not monkey-patching.

Compiler output: state codec/index, sparse Q or native propensity backend,
state observables, per-state expected ledger rates, event provenance, module
versions and capability flags. Exact propagation and SSA consume the same event
semantics. A separate tiny reference supplies independent validation.

Do not put future topology or lineage into the present as empty identity fields.
Provide extension points for heterogeneous controllers, dynamic connections,
spatial transport, memory, multistage assemblies and population-dependent sensing.
Any such feature must re-establish sufficient-state and lumpability conditions.
Quantum backends require a different coherent-process contract; a classical event
registry is not a quantum representation.

## 4. First physical module: material that becomes inaccessible

Retain the existing two compartments and local carrier pools. Extend the counted
local state to `(w,a,d,f,g)`, where `d` counts material in a specified inactive,
chemically trapped or exported class. Then

    p = M - w - a - d;   p,w,a,d >= 0;   0 <= f <= K=M;   g in {0,1}.

`D` is a modeled material fate, not a death label. The material inventory remains
`p+w+a+d=M`; carriers remain a separate conserved inventory. Keep ordinary bath
and carrier dynamics after apparatus loss. Existing controller hardware survives
in this first adapter, as it does now: closure concerns the apparatus-production
channel, not all activity, all agency, or the conditions of valuing in general.
Controller embodiment is a subsequent module.

The original energies remain `eP=0, eW=1, eA=2, eFuel=2`, beta=1 in the declared
coarse units. Add a declared `eD`; energy is

    E(x) = sum_c [w_c + 2 a_c + eD d_c + 2 f_c].

The candidate degeneracy is

    g(x) = product_c M_c!/(p_c! w_c! a_c! d_c!) * choose(K_c,f_c).

Validate it by a labeled-body projection. The law still uses original physical
capacities M,K in contact-rate denominators. Losing usable material does not
silently shrink carrier capacity or rescale all remaining rates.

All existing construction, assistance, repair, capture and exchange modules use
the updated state schema. Preserve the parent/recipient distinction for assisted
construction. New ledger fields include transfers into D by source species,
returns from D, usable material, and returns into built/active apparatus.
Do not reuse the old gross-birth identity without these additional terms.

### 4.1 Finite-barrier mode: physically reversible trapping

For each enabled `v in {P,W,A}`, implement `v <-> D` with forward per-unit hazard
lambda*c_v and the paired reverse rate

    q(v -> D | x) = lambda*c_v*n_v(x)
    q(D -> v | y) = lambda*c_v*n_D(y)*exp[beta*(eD-e_v)].

Here y is the post-forward state when checking a pair. With zero drive these
rates obey detailed balance against the declared degeneracy-weighted Boltzmann
law. Work for this thermal pair is zero; bath heat is minus the state-energy
change. A negative eD makes return rare without deleting it. No free restoration
is added. This is a stipulated coarse chemical mechanism, not measured chemistry.

Freeze lambda, eD and the exposure coefficients before scientific ranking.
If rates underflow, fail or use a supported stable method; underflow must not
silently turn reversible trapping into exact closure. Any additional repair route
must have its own resource bill and reverse/boundary contract.

### 4.2 Absorbing mode: an explicit kinetic/boundary idealization

For a separate module/version, keep the forward transfers but omit returns from D.
This is an absorbing material sink within the modeled accessible domain. Declare
whether it represents export or an idealized inaccessible reaction product.
Retain its material/energy accounting and the residual thermal world.

This mode is not a finite-temperature closed equilibrium model. Energy ledger
closure alone does not establish local detailed balance. The report must expose
the irreversible boundary assumption; only the remaining reversible subnetwork
receives the equilibrium-pair audit. Compare it with finite-barrier results rather
than presenting zero reverse rate as fundamental physical irreversibility.

Never approximate this sink by setting the entire world's generator to zero, by
terminating entropy accumulation, or by conditioning and renormalizing on survival.

## 5. Shock/exposure module and a protection-neutral control

First implement homogeneous stochastic material-damage events through the rules
above. Event timing supplies the stochastic shocks. An instantaneous correlated
multi-unit shock or a fluctuating environment is a later kernel implementation;
it must not be represented as an arbitrary order of single-unit events if those
intermediate states are not physical.

Two exposure mechanisms are required:

1. **Uniform exposure:** `cP=cW=cA=1`. In absorbing mode every usable material unit
   has the same independent destruction hazard lambda. Usable population N then
   follows a pure-death process of rate lambda*N, irrespective of construction or
   controller. This is a structural negative control: maintaining more apparatus
   cannot improve material survival under this stipulated law.
2. **Worn-state exposure:** `cW=1, cP=cA=0`. Material becomes trapped only while
   worn. Existing repair, wear, construction and resource allocation can now
   affect access to the sink. This is an explicit hypothesis about susceptibility,
   not an assumption that organization is generically protective. Register the
   exposure choice and retain a null or reversed policy response.

Both use the same lambda across policy/preparation comparisons. Rate changes are
world parameters, not controls the optimizer may choose. A later active-exposure
arm can test the opposite susceptibility assumption; it is not required for the
first bounded scientific batch.

For a tiny uniform absorbing fixture with N usable units, the all-material-loss
CDF is `(1-exp(-lambda*T))**N`. Use it as an independent first-passage check. This
control cannot test a claim that maintenance improves closure risk; it tests
whether the pipeline invents such an improvement.

## 6. Define channel queries before interpreting protection

Use a versioned family of operational targets, not a universal scalar viability
score. First targets: any active apparatus; active apparatus in each compartment;
and access to a paid construction event. These are apparatus capabilities only.
A two-generation assisted-construction witness is a separate sequence query.

For a state target G, form the graph of **all physically admissible transitions**
under the declared actuator class. The structural closure set is

    C_G = {x : no lawful path from x reaches G}.

Construct it by reverse reachability from G. For an event target, use states where
that event has positive propensity as the target. Preserve a path/event witness
for reachable cases and an outgoing-edge closure certificate for C_G. At a state
with no current apparatus, thermal or paid reconstruction can keep the channel
open; `a=0` is not itself closure.

Also compute closure under each fixed policy, `C_G^pi`. A policy may disable a
route that remains available under another lawful controller. Do not conflate
this with structural loss. The all-action graph is a physical-access upper
envelope; it may permit switching actions in ways the restricted stationary
table class cannot implement. Name that quantifier in every access result.

For fixed policy pi, report separate first-entry distributions into structural
closure C_G and policy closure C_G^pi, naming the set in each result. Also report
instantaneous active occupancy, probability of recovery by each deadline, and
time spent active afterward. Exact
structural closure is distinct from negligible recovery probability within T.
An operational threshold, if used for classification, is a preregistered query
parameter and cannot delete small physical rates from Q.

For either selected closure set C, verify that C is closed under the propagated
fixed-policy generator. Given its complement U, use the killed subgenerator Q_UU
with the original exit-rate diagonals:

    P_x(tau_C <= T) = 1 - delta_x|U exp(T Q_UU) 1.

Allow initial mass in C. This killed calculation is a survey only; the entropy
objective still propagates the complete physical process including C. Any flags
used to track first entry, ordered enabling or retained recovery are analytical
state augmentation and must not create additional physical history entropy.

For finite-barrier models C_G may be empty. Report recovery probabilities and
times as the relevant result instead of declaring an uninformative closure test
passed. Record hitting and endpoint probabilities separately. Never claim high
first-hit probability implies durable occupation.

## 7. Solver upgrade: reducible dynamics without a new objective

The primary readout remains, at fixed cadence delta,

    P = exp(delta Q),   g(x) = H_2(P(x,.)),
    ell_n(x) = sum_{k=0}^{n-1} (P^k g)(x).

For a preparation prior nu, report `nu ell_n`, the mean conditional history bits;
do not add preparation entropy. Re-rooting uses the actual sufficient state.
No survival conditioning or event-family entropy substitution is allowed.

Build reachable states from all declared roots/reference support; do not discard
states merely because they have low probability. Find strongly connected
components and their closed classes. For each closed class compute its stationary
law and entropy rate; compute transient absorption probabilities into each class.
Do not select an arbitrary stationary solution of the full reducible generator.

For a finite homogeneous CTMC with P=exp(delta Q), let Pi be the limiting
projection formed from these absorption weights and class stationary laws. Define

    r = Pi g,
    (I-P+Pi)b = g-r,   Pi b = 0,
    ell_n = n r + b - P^n b.

The root rate is `nu r/delta` and the root offset is `nu b`. This preserves the
existing rate-first, offset-second comparison while extending it to reducible
worlds. Use block methods where appropriate rather than materializing a large Pi.
Check class stationarity, absorption equations, Pi identities and Poisson/finite
recurrence residuals on supported tiny exact cases.

If every root eventually reaches the same residual thermal class, rates may tie;
the offset still accounts for all pre-closure branching and the approach to that
class. A closed apparatus channel need not have zero entropy rate. Expected
closure time may be infinite; use a typed status, never JSON Infinity or zero.

Scheduled shocks or a changing external drive require time-dependent propagators,
or an explicit sufficient Markov environment in the physical state. Reject the
stationary solver for such a model until that capability is implemented. Finite
row-entropy recurrences remain possible for declared time-dependent kernels.

## 8. Compute gates and scaling

Expose capabilities separately: event sampling, sparse finite distributions,
integrated fluxes, first passage, exact sampled-state entropy, limiting entropy,
and policy search. Large SSA runs do not automatically provide the sampled-state
likelihoods needed for this entropy objective. Unsupported is a result status.

The four-material-state local count is `choose(M+3,3)*(K+1)*2`. With K=M:

| Inventory | Extended Cartesian states | One float64 dense matrix |
|---|---:|---:|
| 1+1 | 256 | 0.5 MiB |
| 3+1 | 2,560 | 50 MiB |
| 3+3 | 25,600 | 5,000 MiB |

These are storage estimates, not peak-memory or speed promises. Matrix exponentials
and solves need multiple workspaces. Reachability can reduce counts; it cannot be
used to remove low-probability states. The old 6,400-state smoke certified sparse
surveys only, not exact large-state entropy optimization.

Start at 1+1 for engineering, then profile a single 3+1 controller. Reuse initial
caps: 120 seconds, 1 GiB whole-process-tree memory, one numerical thread, 256 MiB
output and one worker. Decide a bounded search budget from that profile before
freezing the scientific batch. Do not silently lower physical inventory, coarsen
the clock, or replace the objective to fit the cap. Do not attempt 3+3 dense entropy.

## 9. Scientific protocol to freeze after engineering

The implementation should emit a validated `PROTOCOL_DRAFT.json` containing these
fields and refusing scientific execution until all required values are frozen:

- model/module/measurement versions, exact source/dependency hashes and units;
- material inventory, eD, lambda, susceptibility vector, reversible/sink mode,
  thermal rates, chemical drive and the exact scope of irreversibility;
- root states, reference constraints/weights and matching audits;
- controller observation/costs/class, complete or selected-candidate search;
- primary cadence, horizons, limiting comparison, numerical/ranking tolerances;
- channel target definitions, physical/policy reachability quantifiers, recovery
  deadlines, retention surveys and uncertainty thresholds if any;
- registered comparisons, outcome predicates, caps, RNG streams and retention.

First candidate batch: legacy no-loss regression; uniform absorbing control;
worn absorbing damage; worn finite-barrier trapping. Begin with existing 36 shared
inactive/active tables and the prior cadence/horizons where profiling permits.
Keep the same physical controller observation (`own a>0`); D is not magically
visible to it. A D-aware controller needs a separate sensing/implementation arm.
Use a small, declared rate range only after timing and rate-scale calibration.
Calibration may inspect feasibility and closure/relaxation times, but not choose
parameters because an optimized policy looks ethical. Disclose inspected outputs.

References condition on the same initial usable inventory (`d=0` for the first
slice), energy, gates, temperature, carrier pools, drive and controller. The prior
energy-8 roots can embed with d=0 for 3+1 inventory. Weight the matching shell by
declared degeneracy; describe it as a coarse preparation reference, not a complete
molecular gas. Do not mix already-lost material into only one preparation arm.
Comparisons across sink/reversible/exposure laws are mechanism contrasts; each
also has its own matched same-law preparation comparison.

Evaluate fixed-table contrasts and separately optimized tables. Report all
registered finite-horizon and limiting results. Preserve tied policies and
numerical uncertainty. Margin, recovery and closure are readouts, never tie-break
rewards. A maximum-functioning or minimum-closure-risk policy is a diagnostic
benchmark, not the lushness objective.

Registered interpretations must include:

| Observation | Permitted interpretation |
|---|---|
| Winner retains fewer active units | Margin/opportunity trade-off; no standalone ethical verdict. |
| Winner has lower closure risk in susceptible law | Evidence of instrumental protection in that world/controller class. |
| Winner has greater closure risk and greater breadth | Channel/breadth tension retained as an adverse proxy test; identify lost capabilities and all post-loss branching. |
| Uniform absorbing control changes closure risk across policies | Implementation/measurement error unless another declared rule changes usable inventory. |
| Reversible trapping gives no exact closure | Expected access property; use deadline recovery results. |
| Seed loses to its matched reference | Retain negative preparation result even if the law supports recursive construction. |
| Every policy ultimately loses the channel | Report times and offsets; no claim of indefinite preservation. |

No automatic label of ethical behavior follows from any single row. Apparatus
closure is not yet valuer extinction, and enabling a route is not evidence of
learning, intentional exploration or new-function invention.

## 10. Automated analysis and reusable research loop

Make new readouts register their input requirements, units, estimator and output
schema. Report generation consumes those records rather than recomputing physics.
Structured statuses: supported/pass/fail/open-outcome, exploratory, unsupported,
incomplete, cap-hit and numerical-failure. Missing values carry a reason.

Required plots/tables: breadth and matched excess versus horizon; policy ranking;
closure CDF and recovery profile; active/usable/built occupation; gross and net
construction/loss/return; fuel/work/heat; class absorption weights and rates;
fixed-policy versus reoptimized mechanism effects; numerical and resource audits.
Where a readout has Monte Carlo uncertainty, retain its estimator/sample count
and interval separately from numerical tolerances. Do not sum overlapping
recovery windows or invent additive entropy shares for reaction families.

Every feature increment follows:

    question and missing consequence -> module contract and costs -> tiny witnesses
    -> independent audits -> bounded profile -> protocol freeze -> search/evaluate
    -> automatic report -> interpretation -> next explicit model limitation.

Track a limitation registry: assumption, affected claim, evidence, proposed module,
status and successor experiment. Failed predictions remain; a richer successor
does not erase them. Law, controller, measurement, analysis and interpretation
versions are distinct so a prose correction does not pretend to be a new run.

Criticality diagnostics are deferred optional surveys. If later added, declare
perturbation and observable, finite response, relaxation method and size series.
An interior optimum or one response peak does not certify a transition. Do not
delay the channel experiment to build a criticality framework.

## 11. Provenance, storage and reruns

Reuse the existing capped runner but launch the copied worker/package from its
snapshot root, with module/spec paths resolved there. Verify source hashes at
launch and record imported module locations. The current snapshot alone does not
guarantee that those bytes were what ran. Include transitive local imports and
dependency versions; use immutable manifests and atomic status/result writes.

Separate reusable operator keys (world, policy implementation, grain, compiler,
backend) from query keys (root/prior, horizon, cadence, readouts) and report keys.
Cadence is additionally part of any cached sampled-transition operator key.
Include all semantic parameters/seeds/source contents, including uncommitted
code. Failed/incomplete jobs are never successful cache hits.

Store packed states and sparse arrays in NPZ/NPY, compact metadata and results in
JSON, small policy tables in CSV/JSON. Do not dump every event or persist dense P
by default. Retain bounded witnesses plus their selection rules. New readouts may
require reconstruction; summaries do not promise arbitrary later analysis.

Implement a local run/artifact index and cache dry-run eviction using the existing
[workflow retention rules](experiment-workflow.md#7-retention-and-cleanup).
Default cache budget 5 GiB, target 4 GiB; permanent small evidence and executable
rebuild inputs are excluded from eviction. Protect active/locked/pinned/cited
artifacts. Delete only listed, path-validated cache/scratch files; reject escaping
symlinks/junctions. Log eligibility and bytes. Do not migrate/delete historical
outputs as part of this slice. Enable actual eviction only after a tiny rebuild
and safe-deletion test, as a separate explicit rollout step.

Compact canonical results use numerical tolerances for reproducibility where
platform arithmetic differs. Raw file hashes attest artifact identity, not
cross-platform numerical equality. A failed rebuild pins affected evidence.
No recurring automation is requested. Raw runs remain ignored by Git.

## 12. Implementation sequence and acceptance tests

**M1 — Extract and preserve.** Add contracts/compiler, a legacy growth adapter and
readout registry. Reproduce the existing small generator, ledgers, sampled entropy
and representative policy evaluations with all new features off. Do not rerun the
whole historical suite without a regression discrepancy. Preserve old entry points.

**M2 — Add the D and damage modules.** Implement both exposure mechanisms and both
boundary modes, independent tiny labeled-body checks, reachability targets and
resource ledgers. Verify enabling, trapping, rare return, and absorbing closure
with actual event witnesses. Disabling the feature restricts to d=0 and reproduces
legacy dynamics; leaving inert extra state coordinates reachable is not a regression.

**M3 — General finite analysis.** Implement reachable SCCs, class absorption,
reducible rate/offset, first passage and deadline recovery. Validate with an
analytically solvable transient fork into two recurrent classes of different
entropy rates; a closed channel with a continuing random thermal subsystem; the
uniform pure-death control; and an irreducible recovery example. Check the finite
entropy identity against direct recurrence and independent sampled paths.

**M4 — Workflow integration.** Implement frozen-bundle execution, capability and
memory gates, typed results, automated interpretations and cache/index dry-run.
Test that a readout-only change leaves the world/operator hash unchanged, a physical
rate change invalidates it, and editing the live checkout after freezing cannot
change the executed snapshot. Verify failure/cap statuses and bounded output.
Use temporary fixture checkouts for mutation tests; do not alter research source
or historical evidence to test isolation.

**M5 — Capped engineering handoff.** Run 1+1 smoke and one 3+1 timing pilot under
the stated caps. Deliver state/edge counts, actual peak memory, timing, audits,
reproduction command and a proposed frozen scientific budget. No claim of a
large-state entropy solver from sparse-survey success. Scientific launch follows
the separate frozen protocol and authorization.

Suggested new implementation layout (names may change together with the spec):

    omega_v2/testbed/contracts.py
    omega_v2/testbed/compiler.py
    omega_v2/testbed/modules/growth.py
    omega_v2/testbed/modules/material_sink.py
    omega_v2/testbed/modules/damage.py
    omega_v2/testbed/analysis/finite_classes.py
    omega_v2/testbed/analysis/channel_access.py
    omega_v2/testbed/analysis/registry.py
    omega_v2/testbed/experiments/channel_comparison.py
    omega_v2/testbed/workflow/{manifest,runner,artifacts}.py
    scripts/run_channel_comparison.py
    scripts/report_channel_comparison.py
    tests/test_testbed_contracts.py
    tests/test_material_sink.py
    tests/test_finite_classes.py
    tests/test_channel_access.py
    tests/test_snapshot_execution.py

Do not create empty abstraction layers solely to match this layout. Reuse or move
existing helpers with compatibility imports. Required deliverables are executable
contracts, module/model documentation, draft/frozen protocol distinction, compact
engineering evidence, and a report that retains adverse and unsupported outcomes.

**Handoff boundary:** this packet specifies what Sol should implement. No new
physics, optimizer run, scientific ranking or previous-result rescoring has been
performed in preparing it.
