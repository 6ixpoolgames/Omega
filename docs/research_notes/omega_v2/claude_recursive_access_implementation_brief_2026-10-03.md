# Implementation brief for Claude: recursive physical access, v0

2026-10-03. Prepared for the user to share with Claude. Exploratory implementation guidance, incorporating the October 3 synergy report. This proposes a finite implementation of the candidate architecture; it does not declare a lushness measure.

## 1. Deliverable

Build an atlas of **joint physical response laws, their implementation bills, and the continuation remaining after their execution**. Start with a finite operation language and small apparatus. Produce inspectable witnesses and machine-readable results before proposing an aggregate extent.

Use the existing frame construction to condition the actual law. Keep every consequential process eligible for representation. A readable record, organism, preferred task, or source identity is not an admission condition. No noise quotient, uniform prior over programs, synergy bonus, or expected winning arrangement.

Exploration is versioned, not gated by preregistration. Change a model or readout for a stated reason, preserve the earlier result, and identify the version used. The checks below establish implementation properties; passing them is not empirical support for lushness.

## 2. Starting code and scope

Reference repository: [6ixpoolgames/Omega, commit 04149e0](https://github.com/6ixpoolgames/Omega/tree/04149e09fddc66439c6760f59f1aeb232cec7572), branch `codex/operational-continuation-comparison`.

Useful existing modules:

- `omega_v2/finite/quantum_profile.py`: `Density`, `ensemble_density`, `single_gate`, `controlled_x`, `mutual_information`, `contract_inputs`.
- `omega_v2/experiments/quantum_record_structure_v0.py`: `Gate`, `apply_gate`, `evolve`, `routing_setup`, `routing_state`, `bath_start`, `bath_layer`, `inverse`, apparatus isomorphism checks.
- `omega_v2/experiments/quantum_frame_profile_v0.py`: the earlier four arrangements and boundary-channel controls.
- Reports and tests under `docs/research_notes/omega_v2/` and `tests/` with corresponding names.

Read those modules before reuse. `Density.matrix()` returns a matrix on its nonzero support, not necessarily the full computational basis; do not apply full-space gates to that compressed matrix. `Density.law()` reads computational-basis diagonal entries; it is not a basis-independent quantum branching law. Existing ensemble decompositions are numerical representations, not automatically physical outcomes. Existing Choi interfaces do not authorize arbitrary new intervention slots.

Suggested new modules, rather than rewriting the prior experiments:

```
omega_v2/finite/physical_access.py
omega_v2/experiments/recursive_access_v0.py
omega_v2/validation/recursive_access_v0.py
tests/test_physical_access.py
docs/research_notes/omega_v2/recursive_access_report_v0.md
```

First support finite serial circuits, with integer primitive durations and a finite gate alphabet. This is a computational restriction, not a fundamental clock or a claim about Planck discreteness. Preserve quantum coherence on the quantum backend. The synergy model supplies a useful classical sector and calibration backend.

## 3. The mathematical record to implement

Use the following schematic family:

```
AccessAtlas(frame, cut, budget_vector, horizon)
    -> physically realizable joint response-and-residual processes
```

A member contains an implementation witness, not just a response score. The member's actual outcome weights come from the physical initial law and execution. Membership in the atlas does not assign a probability that this implementation is selected.

Keep two clearly identified uses:

1. **Actual execution:** the embedded controller/selector determines what runs, from records it actually holds.
2. **Realization search:** enumerate alternative physically supported programs or preparations as counterfactual witnesses. Charge their preparation and control resources. Do not call their unweighted union the actual distribution of futures.

If a proposed program requires an unavailable gate, hidden input, unprovided memory or unprovided preparation, it is not a realization. A program chosen after inspecting an inaccessible simulator state is invalid. Any adaptive branch may depend only on an actual accessible classical record; coherent control must be a quantum operation on the physical control register.

## 4. Concrete data model

The names below are suggested interfaces, not existing APIs.

| Record | Required content |
|---|---|
| `Apparatus` | Physical factors and dimensions; couplings; gate alphabet and exact parameters; controller and its memory; clock/scheduler; observation instruments; resource rules; autonomous evolution; initial preparation. |
| `WorldState` | Full joint quantum state or exact classical distribution, including environment, records and correlations; controller state; resource inventories; elapsed time; pending operations. |
| `FrameSpec` | Physical record factors and their declared accessible algebra/readout; record history needed for conditioning; relational observation attachments. No access granted by a register's name alone. |
| `Primitive` | Physical map or dilation, target/control incidence, duration, occupancy, resource transitions, and any actual recorded outcomes. Unobserved Kraus indices are not controller-visible outcomes. |
| `Program` | Finite sequence or finite record-conditioned controller, explicit preparation, program-memory footprint and causal observation dependencies. |
| `Bill` | Separate cumulative expenditures, elapsed duration, peak memory/occupancy and remaining inventory. State how each component composes. |
| `Execution` | Every physical outcome, its weight, branch bill and residual state, plus the executed causal history. Include exhaustion, failure and deadline statuses. |
| `Residual` | Full state and remaining apparatus/controller dynamics sufficient to continue execution, including environment correlations. A reduced register marginal alone is insufficient in a memory-bearing process. |
| `Witness` | Program, initial apparatus/version, validity checks, execution, observation interface, and precise search bound. |

Durations add in the initial serial backend. Expenditures add; peak space takes a maximum; inventories evolve physically. Replenishing a stock does not erase past expenditure. Do not replace the bill vector by a sum with invented coefficients. A gate-count comparison may be reported as an explicitly declared slice of this vector.

Keep sunk preparation and further execution bills separately, so a post-cut comparison does not silently treat earlier construction as free. Do not claim an energy cost from gate counts unless the adapter actually supplies that cost model.

## 5. Execution semantics

For an actual recorded outcome y, a quantum instrument gives an unnormalized conditional state:

```
rho_tilde[y] = sum_alpha K[y, alpha] @ rho @ K[y, alpha].dagger()
p[y] = trace(rho_tilde[y])
rho_given_y = rho_tilde[y] / p[y]             # only when p[y] > 0
```

The alpha index is summed inside the physical outcome y. Do not condition on alpha unless the apparatus genuinely records it. If information carried by an environment is relevant to later access, retain that environment through an explicit dilation; tracing it out is only a declared interface restriction. Do not invent a classical history decomposition for coherent alternatives.

Maintain branch mass separately from conditional state normalization. All execution outcomes must sum to the input mass. Never renormalize over successful outcomes. A small positive weight remains part of the result.

An explicit finite controller enforces budget and deadline stopping. A branch that stops retains its unfinished residual and probability. Expand multi-gate macros into primitives; a deadline may interrupt the macro. Environmental evolution must continue during operations, waiting and controller termination according to the model. A task having returned an answer does not halt its physical environment.

Version whether preparations are exact ideal circuit operations or approximations. Numerical tolerance is not a physical error threshold or permission to delete low-probability outcomes.

## 6. Search and recursive continuation

Begin with finite open-loop programs; then add a small number of adaptive steps with explicit records. Bound gate alphabet, depth, memory and hardware footprint. A first complete sweep can use the synergy apparatus's three sources, three blanks and depth at most three. A search on the seven-qubit bath should use a much smaller legal gate repertoire or a restricted recovery family.

Enumerate prefixes, propagate the full state and bill, and retain each prefix as a residual. From that residual, execute legal suffixes using the state, inventory and controller left behind. This is the first finite representation of recursion. Verify that direct execution of prefix-plus-suffix agrees with restart from the saved residual.

Do not enumerate all arbitrary rotations. Use a finite declared angle list, including the published bath gates where relevant. An inverse circuit is one witness; it is not a shortest-path certificate. Exhausting a finite language can establish a minimum within that language and bound only.

Avoid outcome-based pruning in the first version. Equal entropy, equal output distributions, and even equal current reduced states do not establish equal future response. Deduplicating final Boolean truth tables is legitimate for the endpoint population audit, but not for deleting differently timed, differently resourced or differently correlated execution histories from the continuation object.

For a specified response-and-residual requirement, report nondominated feasible bills. Routes costing (1,10) and (10,1) do not imply an available route costing (1,1). Keep cost/outcome correlations; expected cost alone cannot certify a hard budget.

## 7. Jointness and physical interfaces

Do not construct a joint point by taking separate best deliveries. Require one physical program realizing their joint law with the common apparatus. Store the joint output distribution or quantum instrument, not only its marginals.

Queries such as copying a source, reading a parity or producing an AND output are diagnostic interfaces. They do not define valuers or constitute a preferred task family. Store the underlying process so later queries can be evaluated. Coverage is explicitly limited to the interfaces actually checked.

A copied classical bit can support several readers. An unknown quantum state cannot be treated as a copyable classical label. General quantum response claims require channel/instrument checks on the declared input interface, not agreement on one diagonal preparation. Virtual Choi references are mathematical probes; they are not available decoder hardware.

Keep dormant couplings, accessible construction controls and their resource requirements in one common apparatus. If a link can be installed, give the physical transition that installs it. Do not create a new Python operation merely because the analyst announces that construction succeeded. Changing which primitive interactions are effective through physical configuration is legitimate; fixed microscopic laws need not change.

## 8. Use the synergy result as a calibration, with corrected interpretation

The report's deterministic classical sector obeys:

```
record information = I(X; F) = H(F)       # F is a deterministic record of X
Syn(F) = I(X; F) - sum_i I(X_i; F)
       = sum_i H(X_i | F) - H(X | F)     # independent initial sources only
```

This Syn is conditional total correlation under source independence. Keep that operational name; do not assume it is a unique general synergy decomposition. With dependent sources the expression instead equals TC(X|F)-TC(X) and can be negative.

Codex independently reconstructed the gate language and matched all reported reachable-map counts at depth at most three: 130, 10,372 and 38,366. The worked p=q=.2 examples also check:

| Record | H(F), bits | Syn(F), bits |
|---|---:|---:|
| One source copy | .721928095 | 0 |
| NOR of three sources | .999584464 | .263270726 |
| Hierarchical four-cell record | 1.761504552 | 0 |
| Parity of three sources | .966078098 | .780988178 |

The hierarchy can be realized in three gates: r0 = not s AND not f1; r1 ^= s; r1 ^= r0 AND f2. Its cell weights are .512, .128, .16 and .2. All sources remain physically present.

This provides evidence that the selected bounded-record readout benefits from both posterior source coupling and conditional routing. It does not identify that readout with lushness. More Syn can coexist with less record information, as the parity/NOR pair shows.

Retain full truth maps, wiring and bills alongside partition classes. A full invertible recoding and literal copies induce the same partition into singleton source states, while their local readers and decoding bills can differ. Classifying both as `product` is valid for that partition classification, not a physical equivalence of apparatuses.

Report raw laws, record information and Syn separately. Do not name an output column `lushness`. Do not introduce a synergy or hierarchy bonus. Source factorization, frame choice and gate resources remain explicit.

## 9. Work in small stages

**A. Endpoint calibration.** Reproduce the synergy truth tables, worked examples and information identities independently. Preserve raw maps and minimal-depth witnesses. Full correlation/frontier claims need the actual definitions, tie handling and population data; the supplied report alone does not verify them.

**B. Lift maps to executions.** Add bills, controller constraints, physical time and saved residuals. Use pairs with identical record information but different subsequent response, and pairs with identical outputs but different remaining resources. This checks whether the atlas retains what the entropy projection discards.

**C. Existing quantum circuits.** Reuse source laws and apparatuses from the published probes. Record explicit recovery/delivery witnesses for intact, damaged, erased and cycling preparations only where the allowed hardware supports them. For bath spreading, start with inverse suffixes and a small declared local decoder family. Report restricted-search bounds, not a universal minimum.

**D. Composition.** Use a common physical switching/construction mechanism and vary available budgets, source laws and downstream couplings. Compare present response, spent resources and subsequent joint response. Include copies, conditional routing, parity, coherent basis changes and noise where supported. No required winner or required interior optimum.

Do not jump directly to 4-5 sources, 6 registers and depth 6. First estimate unique-prefix growth and memory use, then extend one dimension. Stop and report a partial atlas when resource limits are reached; do not label it exhaustive.

## 10. Necessary checks and informative outcomes

Check probability conservation, positivity, instrument completeness, and direct/restarted agreement. Check that inaccessible hidden source values cannot influence adaptive program selection. Check partial deadline cutoff without lost mass. Check two individually feasible deliveries that cannot run jointly with one consumable token. Check same output with different residual resources or future coupling. Check coherent inputs and that Kraus bookkeeping does not become an extra readable record.

Preserve the existing relabelling rule: consistently rename the complete apparatus, preparations, controls, readers, resources and clocks. A physical rewiring or basis change with a fixed reader is not harmless redescription. A macro and its identical primitive expansion should match at the same physical boundaries; inserting actual delay need not.

For floating-point checks, begin with the existing matrix/probability tolerance 1e-11 and information tolerance 1e-9; record errors and conditioning. Numerical agreement is not an exact symbolic equality theorem. Do not merge outcomes because two floating values are close.

Use the terms `witnessed`, `excluded within declared finite search`, and `undetermined`. Do not report global impossibility or incomparability after a bounded failed search. Cross-apparatus realization would require a single causal, resource-accounted compiler consistent across histories; leave that theorem/search as a later milestone unless a concrete bounded instance is supplied.

## 11. Outputs and stopping point

Export:

- A human-readable model manifest, version/hash, legal operation alphabet, frames, actual source law, budgets and search bounds.
- All tested programs or a reproducible enumeration with representative witnesses and a complete coverage record.
- Joint response laws, branch weights, bills, stopping statuses and full residual-state references.
- Search frontiers with the exact response/residual equivalence used; no unlabeled scalar score.
- A small report separating model premises, implementation checks, measured differences, analytic facts, failed expectations and untested extensions.

Use compressed arrays for quantum states and structured records for metadata. A content hash can index stored state data but is not proof of physical equivalence or preregistration.

The first useful deliverable is a small atlas showing how physical composition changes jointly available responses and later access, with witnesses someone else can rerun. No claim is made yet that the atlas supplies a unique extent, an ultimate-frame order, gas dominance, open-ended generativity, or the ethical bridge. Those remain substantive questions to investigate on this substrate.
