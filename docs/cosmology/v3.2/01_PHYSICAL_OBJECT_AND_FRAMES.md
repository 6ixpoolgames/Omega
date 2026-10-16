# 01 — The physical object and situated access

## One object, many situated descriptions

Begin with a lawful physical world: its states, interactions, causal relations, and boundary conditions. Call its complete physical description Ω_phys. The symbol does not presuppose that this description is a finite data structure, or that any inhabitant could calculate it.

In a closed quantum model, a state and unitary dynamics give a familiar realization. In relativistic settings, local observables, causal regions, and states on suitable hypersurfaces are the better language. These are ways of representing one physical situation at different scopes.

The block viewpoint places relations among events inside the description rather than adding a privileged present that moves through it. Clocks, records, organisms, and deliberating agents still occur, and their succession is an internal relation. An action matters through the dependencies it takes part in, whether those dependencies are described sequentially or all at once. Everett's relative-state formulation is the foundational quantum neighbour, and the program's cosmology adopts its block picture; the operational machinery does not depend on that choice. [R28]

"Completed" describes the viewpoint. It does not give a finite observer complete knowledge, and it does not imply a single classical trajectory. Much of the operational work below proceeds without settling between interpretations of quantum mechanics.

## Quantum alternatives have structure

A quantum superposition is more than a list of classical possibilities. Relative phase can change later outcomes. Entangled systems carry correlations that their reduced states do not specify. Decomposing a state into vectors is not the same as decomposing the world into physically autonomous branches.

So "branch" is read by context. In a decohered regime it can mean an approximately autonomous history with stable records. Before that, it can mean an interfering contribution to an amplitude. The mathematics has to keep the difference. Decoherent-histories methods supply the discipline for when classical probabilities may be assigned to a family of alternatives, and they forbid pooling incompatible families into one classical tree. [established; R01; formulas in Part 12]

Multiway graphs are useful pictures of alternatives, convergence, and shared dependence. A quantum multiway representation must still carry amplitudes or an equivalent process structure. Counting graph paths alone discards part of the physics.

## Relative presents

A **present membrane** is the program's image for a boundary through which a situated process is described. In a relativistic model a spacelike hypersurface can play that role; specifying it requires geometry and a choice of slicing. A worldline at one event does not pick out a unique global hypersurface.

Different admissible sections can describe the same physical situation, and their descriptions must be related by the appropriate dynamics and frame transformations. Quantum reference-frame research gives explicit constructions in controlled settings, and relational quantum hypersurfaces are a close neighbour. [established; R02–R04]

The framework therefore works with a family of descriptions rather than one privileged universal membrane. Some perspectives are better represented by local regions, worldtubes, or interfaces than by a whole-universe slice. The membrane is not a globally privileged time slice.

## Local access and global correlations

A subsystem S has a reduced state ρ_S, obtained by tracing out its environment. That state predicts the statistics of measurements on S at that boundary. Predicting later interactions can require the joint state ρ_SE and the dynamics coupling S to its environment.

Two joint states can share their local marginals and still produce different later behaviour. A local present is therefore not automatically a complete, standalone specification of continuation. Part 11 (Example 2) shows this with two classical correlations and a reversible interaction.

Quantum probabilities come from the state and the Born rule. Missing local information and intrinsic quantum uncertainty are related features of prediction, but they are not interchangeable explanations.

## Nonlocality and the block picture

Entangled correlations can span distant regions of the shared object. A block description places their common preparation and later interactions in one account. It does not turn Bell correlations into ordinary local hidden variables: Bell's theorem constrains exactly that kind of explanation under its assumptions. [established; R05] The useful move is to represent correlations where they physically belong, without adding any mechanism that sends controllable signals outside the relevant causal structure.

## Perspective as situated continuation

A **physical perspective** is a process described from a situated interface with the rest of reality. Its specification includes where and how it couples, which degrees of freedom belong to the description, which correlations cross its boundary, and how continuation is organized there.

This is broader than observation by a mind. A photon hitting a detector, a gas exchanging energy with its surroundings, a crystal carrying an excitation, and a civilization building instruments all have situated continuation. Agency and awareness are further kinds of organization within that domain.

For concrete work, a perspective can be specified schematically as

```text
P = (region or interface, observable algebra,
     boundary condition, coupling structure, continuation domain).
```

This is a modelling interface, not a new entity. Subsystem structure itself deserves care: accessible observables help determine a useful tensor-product decomposition, and different couplings can support different decompositions. That is why "the same thing from another perspective" needs a transformation rule rather than an intuition. [established; R13] Quantum reference frames and relational quantum mechanics are complementary precedents; neither is adopted wholesale as the definition of an Omega perspective. [established; R02, R03, R14]

## Focus, and four operations to keep apart

A **focus** relates a situated boundary to the compatible contributions that connect to a specified condition. Asking how a prepared system could reach a particular detector effect is a focus: the condition organizes the relevant contributions, and the dynamics supplies their propagation and interference. A focus can be a physical detector condition, a boundary constraint, or a mathematical query. It does not require attention, intention, or agency.

The elementary construction pairs a forward state with a backward-propagated effect (Part 12, §L). The backward-propagated effect is an inference object. It does not assert that a later event rewrites an earlier state. [established; R06–R08]

Four operations must be kept distinct:

- **Redescription** changes coordinates, basis, or frame while preserving physical content.
- **Conditioning** asks about the process given a record or specified outcome.
- **Intervention** inserts a physical operation and can change the process.
- **Decoherence** is produced by physical correlations that suppress interference in a reduced description.

A focus can be involved in all four, and using the word without saying which is meant manufactures paradoxes. A focus chosen on paper does not decohere a beam; a detector interaction can. Sorting existing data by a correlated record is conditioning. The delayed quantum eraser is the standard illustration: conditional subsets show complementary interference patterns, and recombining them restores the unchanged unconditional distribution. No awareness-induced collapse is needed, and no later choice rewrites earlier detections. [established; R12; Part 11, Example 3]

## Memory and the full process

Physical memory is dependence carried by the present organization of a system and its correlations. A durable register is one architecture for it; a temporary environmental correlation can also carry memory into later behaviour.

A full relevant joint state and its dynamics can encode that dependence at one boundary. When access is restricted to a subsystem across several times, a **process tensor** (or quantum comb) represents how the subsystem responds to sequences of operations, including environmental memory. [established; R15, R16, R31] So "the present contains the relevant past" and "a local description needs multi-time information" can both be true. The first concerns a sufficient physical boundary description. The second concerns a reduced description whose instantaneous state omits consequential correlations.

## Composition and scale

Perspectives can overlap, share records, exchange signals, or combine into a larger process. The combination must keep joint correlations. A product of reduced descriptions is valid only where the required independence actually holds; joint systems are not automatically tensor products of their parts.

Higher-level perspectives become useful when stable organization supports repeatable continuation: molecules, cells, organisms, institutions. The same relational move applies across scales, while the effective variables and mathematics change. Massive worldlines admit proper-time descriptions; massless propagation follows null structure and has no rest frame. Both take part in causal dependence. [established; R17, R18]

## Frames, history and accessible information

For one classical physical law P and a positive-probability record condition
α, the frame weight is μ_α(E) = P(E | α). Within a compatible decoherent
quantum history family, use its Born weights in the same conditioning
formula. For a general coherent process use instruments; do not impose a
classical joint law on incompatible alternatives.

The information accumulated in a history and the information available now
are different. Write F_t = σ(H_t) for the accumulated observation/action/memory
history, and G_t = σ(O_t, M_t) for the current observation and accessible
memory. F_t is an increasing filtration; G_t need not increase. Forgetting
can remove a record from current access without deleting its place in history
or the encompassing physical process.

Under one law, nested conditioning obeys the tower identity. Thus conditional
expectations of a fixed integrable readout form a martingale along F_t.
The same assertion for G_t requires nesting; it is not guaranteed after
erasure. An analyst retaining H_t does not supply it to the controller.
Physical archive access must be represented with its coupling, delay and bill.
The [frame-information audit](../../research_notes/omega_v2/frame_information_audit_v0.md)
provides an exact finite witness.

Every future time retains total conditional probability one. Individual fine
alternatives can thin without discounting the future as a whole. Horizons
index restrictions of the field; they do not supply an arbitrary time weight.
Compatible quantum restrictions use the corresponding causal process maps.

## Completion and physical scale

The completed object retains every finite restriction and its consequences.
It is not replaced by a terminal state, a growth exponent or a total entropy.
A pure global quantum state can have zero von Neumann entropy while its
subsystem couplings and response processes differ substantially. Normalized
weight one is therefore not a proof that the continuation geometry is trivial.

A finite discretization must state its physical meaning. Planck units alone
do not establish a discrete clock, lattice or smallest record in this
construction. The present membrane anchors a causal restriction relative to
the physical model; changing the slicing requires a valid transport of the
same apparatus and events. A general relativistic quantum implementation of
the atlas remains beyond the finite circuit backend.

## What this foundation provides

Ω_phys is the source of continuation constraints. Perspectives inherit their possibilities from it. State space, causal accessibility, coherent interference, and stable records determine what can be combined and what can be distinguished. Every compression later in the primer must respect these constraints.

Quantum machinery constrains what a faithful continuation representation must keep. It is not required to pose the finite classical generativity questions of Parts 02–03, and it does not confer moral standing. Part 12 gives the quantum realization after the finite classical presentation.

Further reading: decoherent histories [R01]; quantum reference frames and hypersurfaces [R02–R04]; Bell [R05]; channels and distinguishability [R06, R07]; past quantum states [R08]; decoherence [R09, R10]; eraser [R12]; subsystem structure [R13]; relational QM [R14]; process tensors and combs [R15, R16, R31].

---
