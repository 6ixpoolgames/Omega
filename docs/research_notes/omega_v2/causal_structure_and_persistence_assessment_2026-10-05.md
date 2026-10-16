# Causal structure, persistence and continuation extent

2026-10-05. Assessment of the user's causal-set preference and Sol's three proposed branches. No new simulation or adopted extent. This note is subsequent to the log publication at 27fb522.

## Recommendation

Prioritize an explicit causal/event representation of the existing dynamics before adding persistent homology. Keep weighted history coverings as an instrument on that representation. Smooth intrinsic volume remains a restricted calibration case.

The reason is structural, not aesthetic agreement with a cosmology: a history has internal enabling, rate modulation, resource competition and composition even when a path-diversity measure represents it by one point. An event representation can retain that internal structure. It does not by itself supply its extent.

Cost is manageable for a small replay/provenance prototype. The more difficult unresolved question is which relations the representation asserts. Reconstructing a dependency graph is different from establishing interventionist causal effects or enumerating every possible continuation.

## Three different causal constructions

1. A realized event dependency graph records relations within one physical history. Its transitive closure is a partial order when edges point forward in time. Temporal succession alone is not a dependency.
2. Causal set quantum gravity postulates fundamental spacetime elements with local finiteness and causal order. In a continuum approximation, number corresponds to spacetime volume under a specified element density. Our chemical reaction events are not established spacetime atoms.
3. A continuation structure must additionally represent alternative events, joint compatibility/conflict, physical timing, resources and the native probability law. Event structures and causal unfoldings supply relevant established mathematics, although a particular stochastic, rate-dependent adapter still needs its semantics specified.

For example, two possible consumers of one token can be individually enabled but mutually incompatible. A bare partial order of possible events does not record that distinction. Joint prerequisites and alternative sufficient routes also need to be distinguished; a list of incoming edges without enabling semantics is insufficient.

For this programme, the third construction is the appropriate classical target. The first is a tractable view of it. The second is a potential fundamental-physics connection, not a justification for assigning a fixed physical volume to every simulated reaction.

## Relation to Wolfram, block descriptions and quantum continuation

The alignment is architectural. Wolfram's technical description distinguishes a single-evolution causal graph from multiway state and causal graphs that represent alternatives. A history can be treated as a completed event structure with cuts through it; a continuation construction relates the allowed extensions and their weights.

A consistent cut should include a causally closed past and the physical records/resource state at its boundary. An arbitrary antichain is not automatically a complete state for future prediction. Existing frame conditioning and physical time remain in force.

This supplies a route compatible with the user's block/Everett motivation, not a derivation of quantum mechanics. Causal order alone does not supply amplitudes, interference or Born weights. A quantum extension needs quantum process/history data; classical probabilities for alternative histories require an appropriate decoherent family. Counting paths or event descendants cannot substitute for that construction.

## What present records support

Inspected lattice_chemistry.py: each recorded event includes time, channel kind, participants, movement direction, catalytic template and rate. Full initial configurations plus events permit state replay. lattice_history_profile.py already tracks some bond-episode formation and later catalytic use.

That is enough to begin a retrospective structural account. It is not yet a complete dependency graph. It lacks a stored distinction between:

- state supplied or consumed;
- state read to enable a reaction;
- state affecting a rate while the reaction remains possible;
- vacancy/blocking conditions and excluded alternatives;
- resource-pool changes affecting many otherwise distant reactions.

These can be reconstructed or instrumented from the unchanged rules. Include initial conditions as boundary facts, rather than inventing earlier reactions. Record conjunctive requirements together and keep alternative routes distinguishable. Particle identifiers remain replay handles, not valued identities.

Two current modeling choices directly affect ancestry. Fuel is a well-mixed count, so a change in its stock can alter rates across the lattice. Do not invent a molecular token lineage absent from that representation. Bonded components move rigidly and their size changes their mobility; this is a collective dependency. Neither should be silently removed to obtain more local-looking causal cones.

Do not add causal edges merely because the simulator shares a random-number generator or computes a global race. Dependency instrumentation should follow the physical transition rules, not execution details.

## Provenance is not necessity or a counterfactual effect

A fired catalytic channel reads a particular template. That does not establish that the same target transformation could not have happened through a thermal channel. A resource register can appear in a rate expression without making its last update a necessary cause of a particular later event.

Keep typed rule dependencies as such. Use the existing native-event broken-versus-skipped residual-law method on selected examples to assess whether an identified dependency changes future distributions. Do not claim a uniquely coupled individual counterfactual path: a generator specifies marginal laws, while a joint coupling of alternative worlds needs additional assumptions.

Blocking also matters. A realized-event graph alone can omit the events prevented by a fuel drain or occupied site. Retain the residual enabled-channel/rate description at cuts and the alternative legal continuations. Otherwise the representation can miss exactly the foreclosure the programme is studying.

## Causal-cone cardinality is not yet possibility volume

Sol's suggestion that a thermal fluctuation typically has a one-event cone is not established. In an interacting gas a small change can propagate broadly, and the current shared fuel pool can spread rate effects throughout the apparatus. All such consequence remains represented.

A long chain can have a large descendant count but little joint freedom. Branching, reconvergence, shared prerequisites and bottlenecks can differ at equal counts. Conversely, a damaging act can influence many later events while reducing residual access. Preserve the distinction between the act's reach and the residual continuation it leaves.

In causal set theory, E[N]=rho*V for a Poisson sprinkling at density rho links counts to spacetime volume. A chemistry event rate is not that density. Replacing event count with ordinary spacetime cone volume would measure a physical region's extent, not automatically the extent of its possible continuations.

Hence causal structure is a stronger candidate carrier, but raw descendant counts and spacetime volume remain diagnostics. Reach facilitates lushness; it does not define it.

## Corrections to the persistent-homology proposal

- Topology does not imply a unique intrinsic dimension or a volume law. An interval and balls of different dimensions are all contractible and have the same ordinary homology. Persistent data may distinguish some metric constructions, but a stable barcode does not establish manifold structure or a scaling exponent.
- A loop in an undirected neighborhood complex is not automatically a physical feedback loop, a recovery route or causal reconvergence. The complex is built from similarity between whole histories. Its adjacency does not mean that the system can move between those histories. A directed physical process needs its direction and enabling semantics retained.
- Under the existing whole-state metric, the matched coupling examples are measure-preserving isometric. Adding any isometry-invariant persistent-homology calculation on that same metric cannot repair this loss.
- Ordinary Vietoris-Rips persistence on a fixed finite support does not use the masses on its points. Rates can change native weights without changing that barcode. A probability-aware construction must be explicitly supplied, not inferred from calling the input metric-measure.
- A vector of frame tolerances, optionally with a probability coordinate, gives a multiparameter filtration. A one-parameter barcode follows only after a declared slice or scale path; that choice does not disappear by using persistence.
- For a finite exact observed-history support, the sufficiently small-scale covering count is constant. A fitted intermediate-scale exponent is a resolution-dependent observation, not an automatic nonzero asymptotic dimension of that finite set.
- Short-lived topological features can be real physical consequences. Persistence is an informative scale diagnostic, not a rule to delete noise or admit only features surviving many scales.

The proposed chain topology -> dimension -> volume therefore is not automatic. Covering growth estimates dimension directly under stated limits; topology is complementary evidence. Agreement among methods sharing the same metric or supplied manifold assumptions is not independent confirmation of that metric or of lushness.

## Expense and a bounded next sequence

With explicit bounded read/write footprints, recording direct dependencies can be close to linear in the number of events and recorded references. The present model has collective components, so actual footprint costs need measurement. Do not materialize every ancestor-descendant pair: a sparse dependency graph can have a quadratic transitive closure. Query selected cones or use compact reachability methods.

The expensive tasks are complete multiway enumeration, exact counterfactual families, large graph-equivalence searches, and high-dimensional or multiparameter persistence. None is required for a first representation check. Finite-state CTMCs can still have unbounded jump counts by a finite horizon; finite prefixes/samples are restrictions, not exhaustive completed futures.

Recommended order:

1. Replay a few existing histories and attach typed dependency/provenance records, including initial facts, rate effects, shared-pool use, and blocked opportunities at declared cuts. Keep the generator unchanged.
2. On a tiny exact system, retain alternatives and joint compatibility as well as the realized DAG. Use independence, shared-token exclusion and joint enabling to inspect semantics; treat these as representation checks, not discovery of generativity.
3. Apply the existing matched coupling and repair/deformation comparisons. Check whether the causal representation and the frame geometry identify the same physical changes, including losses of alternatives that never became actual events.
4. Compare the repaired covering profile with a few causal structural summaries. Do not declare any of them the extent just because their signs agree.
5. Add low-dimensional persistent topology only after the physical interpretation of its neighborhoods is clear. Keep the smooth volume example as analytic calibration.

This modestly revises the previous recommendation: causal instrumentation now comes before a larger joint-covering or topology run because it tackles the internal-structure limitation explicitly. It is still part of developing a quantified continuation extent, not a replacement objective of maximizing causal reach.

## Sources checked

- Sumati Surya, [The causal set approach to quantum gravity](https://link.springer.com/article/10.1007/s41114-019-0023-1): order, local finiteness, sprinkling and continuum volume interpretation.
- Glynn Winskel, [Event structures](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-95.html): causal dependence and concurrent-process semantics.
- Wolfram Physics Project, [Appendix: graph types](https://wolframphysics.org/technical-introduction/additional-material/appendix-graph-types/): single-history versus multiway causal representations. These are the project's proposed physical connections, not established identification with quantum spacetime.
- Gell-Mann and Hartle, [Alternative decohering histories in quantum mechanics](https://arxiv.org/abs/1905.05859): probabilities for alternative decoherent histories.
- Chazal and Michel, [An introduction to topological data analysis](https://arxiv.org/abs/1710.04019): metric complexes, inference assumptions and probability-sensitive constructions.
- Gaefvert and Chacholski, [Stable invariants for multiparameter persistence](https://arxiv.org/abs/1703.03632): distinction between one-parameter barcode information and multiparameter invariants.

The elementary topology, metric-isometry and finite-support observations above are direct deductions. Complexity estimates are conditional algorithmic expectations, not measured runtimes.

## Follow-up: can the complete dynamics make the extra relations derived?

The subsequent Sol proposal is directionally correct: repair, damage, catalysis and generativity should not be primitive semantic edge types. The physical dynamics comes first. Dependency annotations are computational descriptions whose claims must be derivable from those dynamics, not extra preferred mechanisms or rewards.

The compact presentation M=(S,U,W) can express the intended input, provided its components retain enough information:

- S is relational physical configuration, including the locality, resource and record structure relevant at the adapter's resolution. It is not just an arbitrary state identifier.
- U specifies actual local rule applications and their physical action on configurations. A bare list of global before/after pairs can forget locality, resource use and the distinction between competing and independent applications.
- W supplies the complete native dynamic law: for the CTMC, contextual rates and the corresponding holding-time law. Actual event timestamps describe a realized path, while the generator supplies the distribution of possible event times. Quantum amplitudes require coherent composition and cannot be used as interchangeable classical edge probabilities.

Existing frame conditioning and restriction maps remain part of how this input is viewed. The tuple's brevity does not remove their role.

### Diamond is not sufficient for concurrency

Both A;B and B;A reaching the same endpoint establishes that both orders can be realized and their endpoints agree. It does not by itself establish simultaneous executability, absence of resource contention, or stochastic independence. A shared machine can carry out both orders while preventing overlap. Rate changes after the first event can also preserve the graph diamond while destroying factorization of the timed law.

If the complete physical dynamics resolves resource occupancy and duration, those distinctions can indeed be derived from it. They cannot be recovered from a graph that has already abstracted them away. Do not restore the old rule that disjoint footprints alone defines the full physical comparison; footprints are one restricted sufficient check, not a general definition or a new result.

The earlier continuation_field_candidate_v0.md already recorded the equal-endpoint limitation. The finite net contract's shared-token-return example demonstrates it under that contract's step semantics. That example alone does not prove a difference in every observation law or a lushness ordering between instantaneous implementations.

### Conflict can be derived, with occurrence context preserved

Given the complete family of legal physical developments and a specified interpretation of event occurrences, incompatibility can be defined by failure of joint occurrence. It need not be an independently stipulated axiom.

But a graph of reaction names is weaker than that family. Replenishment can allow another occurrence of the same reaction later; two presently competing applications are not the same as two reaction types being forbidden together forever. Higher joint restrictions must also be retained: pairwise compatibility need not imply that an entire set can coexist.

### History preservation and reconvergence need linked descriptions

A literal path-tree unfolding duplicates the past-dependent nodes and does not itself merge branches. Keep an ancestry-preserving development representation together with a projection to the current full physical state or residual process.

Different histories may then project to the same residual continuation without losing their prefixes. Equality of a coarse frame's record is insufficient for this identification; for the CTMC the relevant equality is the complete Markov state at the appropriate cut, with physical resources and timing conditions retained. A separate residual-state projection is bookkeeping for the same process, not an extra metaphysical object or a quotient deleting noise.

### Revised working wording

The candidate carrier is the frame-conditioned, physically timed unfolding of lawful local developments, retaining their internal causal structure and all alternatives, with compatibility derived from the physical update semantics and residual-state projections retaining reconvergence without erasing history.

This is a useful next representation target. No geometric extent has yet been selected by adopting that wording. More branching alone must not be renamed generativity; larger act-consequence alone must not be renamed richer residual continuation. Those interpretations remain to be assessed through the eventual extent and physical deformations.

The next implementation should generate derived dependency/compatibility records from the existing rules and check that they retain the native law. It should not manually assign repair, synergy or harm types. The checks establish representation fidelity; they are not new empirical support for the lushness premise.

Additional source: [Winskel, Events, causality and symmetry](https://www.cl.cam.ac.uk/~gw104/VisionRevised.pdf), on causal/concurrent semantics beyond interleaving descriptions. No new simulation or publication accompanied this follow-up assessment.
