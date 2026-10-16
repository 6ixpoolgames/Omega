# Modelling refinement: residual identity and transport

2026-10-05. Assessment and concrete next design, prompted by the supplied
`sol Convo - modelling update .txt`. Checked against the current chemistry,
residual atlas, Alpha files and primary literature. This note proposes changes;
it does not implement a new generator, run a simulation or select lushness.

Subsequent user authorization requested the three recommended refinements
together and publication. They are now implemented in the
[refinement probe](lattice_refinement_report_v0.md). The sequential ordering
below records the original recommendation, superseded by that instruction.

## Recommendation

Keep the reversible chemistry and refine two specific things: how histories
share residual futures, and how fuel transport produces physical coupling.
First implement the former on the existing model; then introduce a small
compartment fuel model whose fast-mixing limit recovers the existing rates.
Expose mobility as the inexpensive next sensitivity axis. Do not combine
rotations, boundaries, saturation, new templates and a new kinetic law in the
first comparison: that would obscure which change explains the result.

Exploration stays revisable. Retain code versions, parameters and failures;
there is no mandatory preregistration or required winner. Thermal continuation
remains a matched baseline, including every physical fluctuation. The goal is
still a possibility-extent profile, not merely more realistic chemistry.

## 1. The architecture and what the source files establish

The user's clarification places Alpha below a particular physical realization.
A physical theory, exposed through an adapter, supplies lawful evolution;
Omega describes its continuation. The adapter is an interface, not another
physical layer. A universal construction need not posit one universal CTMC
generator, or derive molecular rates from the abstract primitive vocabulary.

The current checkout's `formal/lean/AlphaCore/Primitive.lean` still uses
Rel/Sep/Asym. `PrimitiveSoundPresentation.lean` prohibits a presentation from
identifying primitively separated relata, and explicitly distinguishes this
from evaluated consequence. `alpha_primitive_derived_surfaces_v0.md` says that
Alpha's derived paths do not yet supply physical time or dynamics. These are
useful existing boundaries. A bounded search of locally available refs and
Alpha-related history did not locate the recalled September replacement of
the primitive record. That does not establish that the revision does not
exist; do not promote the old record to current conceptual canon.

Working adapter obligations are physical configuration and incidence,
occurrence-level local rule applications, native rates/timing or quantum
process data, resource state, and frame observation/restriction maps. Terms
such as repair, catalyst and harm describe consequences of those rules. They
are not bonuses or semantic labels in the proposed extent.

## 2. Three identifications with different meanings

1. **Description equivalence.** A consistent renaming of the entire apparatus,
   including records and couplings, preserves its physical description.
   Moving one apparatus relative to its surroundings is not such a renaming.
   Different serial listings of the same timed partial-order development can
   be equivalent descriptions. Swapping physical event times is not generally
   harmless: intermediate records and elapsed delays can differ.
2. **Residual equivalence.** At a common cut, two histories may supply exactly
   the same remaining physical process. Store that process once, with both
   incoming histories and their native weights retained.
3. **Frame projection.** A bounded frame may be unable to distinguish two
   different complete states. This defines its coarser description and induced
   law. It does not assert identity in the encompassing physical object.

This distinction accepts the user's same-point/same-future-field intuition
without treating every inaccessible distinction as nonexistent. In particular,
two identical structures at two physical locations remain two embedded
occurrences. Reusing a description of their type does not remove one copy or
its possible joint interactions.

### Residual equality is already concrete in this CTMC

For a fixed, time-homogeneous generator Q and complete state x at a deterministic
cut t (also at a stopping time under the strong Markov property),

    Law(future | full history through t) = Law_x,Q(future).

Here x includes positions, conformations, bonds and remaining fuel. Thus
equal complete states under the same generator have equal residual laws.
This is not a new theorem about lushness. It is the implementable first case
of the proposed equivalence. If the generator, boundary conditions or physical
clock phase differ, the comparison must retain that difference.

Equal energy, fuel total or branching topology is insufficient. The existing
adjacent/opposite two-bond witness has equal E/F/bond count and state-ball
counts, but next-two-fuel-binding probability by time 1 is approximately
0.346834 versus 0.098421. The structure's native law distinguishes it.

A conservative additional certificate is an explicit whole-description
isomorphism f preserving physical incidence, resources, observations and
occurrence channels, with Q_B(f(x),f(y)) = Q_A(x,y). A state-generator
isomorphism alone need not preserve resolved channel histories or concurrency;
retain the channel mapping and local update semantics as well. An unlabelled
graph match, a few matching marginals or a bare diamond is not a certificate.

For coarser state blocks, matching exit rates into every block is a sufficient
strong-lumpability condition for an exact projected CTMC. It establishes that
projection's law, not fundamental physical identity. A coarse process may have
memory when this condition fails.

### Resource expenditure and historical contribution

Past expenditure belongs to historical accounting. Any surviving effect on
fuel, waste, records or surroundings belongs in the residual physical state.
Do not append a history-dependent cost variable to the residual identity if it
has no future physical effect in this adapter. Conversely, equal remaining
energy cannot justify discarding differently situated waste or records in an
adapter that actually resolves them.

For histories h1 and h2 reaching the same residual r, classical future-event
weight is (P(h1)+P(h2)) P(E | r), when h1 and h2 are disjoint prefix events.
The shared suffix is stored once; the prefixes remain available for historical
extent. Conditional laws for precise continuous event times require kernels
or densities, not probabilities assigned to singleton timed histories.

**Residual reconvergence does not erase historical contribution.** Nor does
storing one continuation template establish how an eventual volume should
count multiple uses of it. That arithmetic remains part of the extent problem.

## 3. Chemistry audit and priorities

| Proposal | Assessment and action |
|---|---|
| Reversible CTMC, thermal units, symmetric catalytic acceleration | Keep. The implementation already has these. Detailed balance constrains forward/reverse ratios, not absolute speeds. |
| Conformation parameter p0 | Useful reporting coordinate: p0 = 1/(1+exp(delta)) for an isolated two-state block with the stated equal degeneracies. It is not another independent parameter beside delta. |
| Catalytic enhancement chi | Useful reporting coordinate, chi = exp(b) for one template. With m routes the current total multiplier is 1 + m(exp(b)-1), not exp(mb). |
| Concealed-bond specificity s | A defensible sensitivity parameter. Update conformation energy differences and the equilibrium sampler as well as bond energies. s=1 removes conformation dependence of bond energy; it does not remove the existing exposed-state requirement for catalytic templates. |
| Mobility D_n = D_1 n^(-gamma) | Cheap and relevant. gamma=1 is the current additive-drag approximation; 1/2 is a hydrodynamic scaling comparison under additional geometric/solvent assumptions. A power law is not the Saffman-Delbruck membrane law. Keep this a declared transport family. |
| Local diffusing fuel | Highest-priority physical refinement for causal geometry. It must specify reservoir volumes, diffusion, reverse placement and reaction contact rules. Derive the old model as a limit. |
| Arrhenius/Eyring alternative | Valid later sensitivity test. It introduces a saddle/prefactor model; thermodynamics does not choose that model. Replacing Glauber is not automatically more principled or less arbitrary. |
| Rotations | Potentially important, but specify pivot, swept exclusion and inverse moves. Endpoint-valid lattice rotations can pass through occupied sites. Large collective moves remain an effective mechanical approximation. |
| Periodic boundary | A new physical boundary condition. Useful for a bulk comparison, but not automatically preferable for the present finite box. Small tori can duplicate neighbor channels; do not silently change the baseline. |
| Template geometry family | Useful after the transport question. Preserve locality and forward/reverse symmetry. Normalizing by number of templates or forcing equal total rate would be a new choice, not a neutral comparison. |
| Saturation m/(K+m) in template count | Do not adopt as a default repair. Ordinary substrate saturation does not generally imply saturation in catalyst count. Specify occupied intermediates, product inhibition or shared contact competition if that is the mechanism. |
| Equilibrium diagnostics | Add autocorrelation/ESS and compare dispersed/compact starts when needed. The current sampler already analytically sums bonds and uses nonphysical relocation moves for sampling, so slow physical cluster diffusion does not directly set its mixing rate. Strong-binding mixing remains a real concern. |
| Finite versus maintained drive | Keep distinct. A chemostat introduces external chemical work; it is not the same matched finite inventory with a longer lifetime. |

The precedent for collective-motion sensitivity is
[Whitelam et al., collective motion in self-assembly](https://arxiv.org/abs/0806.3903).
Reversible spatial reaction kernels and product placement must be jointly
consistent with equilibrium; see
[Zhang and Isaacson, detailed balance in bounded domains](https://open.bu.edu/items/4b8fb255-7254-4f87-b928-00ff3ef2594b).
These precedents justify model classes, not our particular chemical mechanism.

### Corrections to parameter and entropy language

Sol reverses the timescale form of the Damkohler ratio in one passage. Use
Da = tau_transport/tau_reaction = k_reaction/k_transport with the relevant
length and concentration specified. The code's D is a hop rate *per cardinal
direction*; the total unconstrained monomer escape rate is 4D. A switching
prefactor of 0.2 does not mean each actual switch takes five monomer waiting
times: the logistic factor and four movement channels also enter.

The fuel parameter 4 is already a standard free-energy difference in kBT
units. For the ideal large-count mixture the chemical-potential difference
also includes log(F/W). Exact finite-count transitions use combinatorial
increments, including the destination's +1; do not replace them with a
singular concentration formula at empty/full stocks. Concentration factors
and the binomial term must be included once, not twice.

The sum of log forward/reverse rate ratios is not generally the full entropy
production. For this closed detailed-balance generator it telescopes to
G(x0)-G(xT). Add log[p0(x0)/pT(xT)] for total stochastic entropy production.
Its expectation is D_KL(p0||pi)-D_KL(pT||pi), nonnegative under this relaxation.
With coarse states, rate-ratio terms can also include intrinsic-state entropy;
calling them solely environmental heat is too strong. At equilibrium the
mean production vanishes, not every individual trajectory contribution.
The thermodynamic basis is
[Rao and Esposito](https://arxiv.org/abs/1805.12077); the telescoping and relative-
entropy statements here follow directly from this model's detailed balance.

## 4. A specific local-fuel extension that can recover the old model

Begin with two adjacent reservoir compartments, then a small spatial grid.
Each contains ideal fuel/waste counts F_c,W_c and has declared volume v_c.
Total B=sum_c(F_c+W_c) is fixed, while local occupancy can change by diffusion.
Fuel lives in an adjacent reservoir layer; it does not silently acquire the
building blocks' excluded-volume interaction. This is a proposed adaptation,
not a unique molecular interpretation.

In dimensionless thermal and reference-volume units, use

    G_local = E_structure + delta_mu_standard * sum_c F_c
              + sum_c [log(F_c!) + log(W_c!)
                       - (F_c+W_c) log(v_c)].

An overall constant for fixed B is immaterial. Let V=sum_c v_c. Summing the
equilibrium weights over all allocations at fixed F yields a factor
V^B/[F!(B-F)!], hence the current binomial fuel multiplicity up to a constant.

Fuel/waste hop independently between adjacent compartments. Per-molecule
transport coefficients d_cd must satisfy v_c d_cd = v_d d_dc; equal-volume
symmetric hopping is the simplest case. This supplies a specific reversible
transport process rather than a guessed local correction to the global rate.

For a binding channel using compartment c, set rates proportional to

    forward: k w_c (F_c/v_c) f(e-delta_mu_standard)
    reverse: k w_c (W_c/v_c) f(delta_mu_standard-e),

where f is the existing logistic function and the geometric contact weights
w_c sum to one for that target bond. For example, the two endpoint reservoir
compartments each contribute half; this is a declared symmetric contact rule.
Binding and unbinding use the same rule and deposit waste/fuel locally.
The unchanged catalyst multiplies both directions as before.

The forward rate at x divided by its reverse at y is
F_c/(W_c+1) times exp[-(e-delta_mu_standard)], exactly the required local
free-energy ratio. Under rapid mixing, conditional mean F_c/v_c=F/V and
W_c/v_c=W/V. Choosing V=B in the existing concentration units recovers the
old F/B and W/B propensities. A different V is an explicit concentration
change. This derivation supplies a meaningful limit to test, rather than
assuming any spatial-fuel implementation must reproduce Chemistry v0.

At finite diffusion, the aggregate fuel process usually has memory when
positions/allocations are hidden. It is not exactly the old CTMC. Compare
laws on the same projected chemistry observations as diffusion increases;
retain fuel hops in the full physical histories. Prepare initial allocations
from their conditional mixing distribution for a clean limit, or explicitly
resolve the initial transport transient.

Nearest-neighbor diffusion is still an effective nonrelativistic model. Its
CTMC tails do not impose a strict light cone, and the current rigid cluster
translations remain collective updates. Local fuel addresses one measured
coupling assumption; it does not make this a relativistic field theory.

## 5. Quantum and relativistic boundary

Sol is right that equal reduced quantum states need not determine equal
future processes with system-environment memory. A process tensor is an
established way to retain that memory relative to specified intervention
slots and instruments; see
[Pollock et al.](https://arxiv.org/abs/1512.00589). It does not supply an
unrestricted experimenter for Omega: physical interactions and resources
must remain in the adapter. Equality over a finite diagnostic family is only
that family's equivalence, not equality of the encompassing continuation.

Decoherence is not a universal equivalence algorithm. It suppresses
interference between alternatives in an appropriate description; it does not
declare their different records physically identical or select a unique
partition at every scale. See
[Schlosshauer's review](https://arxiv.org/abs/quant-ph/0312059). Under common
closed-system unitary evolution, distinct global states cannot exactly merge:
unitary evolution is invertible. Subsystem reconvergence can coexist with a
remaining distinction in environmental correlations. This is compatible with
residual sharing in a declared effective classical adapter.

For history sets a decoherence functional retains off-diagonal interference.
Its classical counterpart is D(A,B)=P(A intersection B), so it is zero for
*disjoint* alternatives, not for every unequal pair of sets. This gives a
useful generalized weight structure, not a geometric lushness volume; see
[Sorkin](https://arxiv.org/abs/gr-qc/9401003). Renaming classical branches as
quantum branches does not cure the extent problem.

The present membrane anchors residual comparison. Equivalent descriptions of
the same physical development should agree across admissible foliations;
different cuts need not have equal residual fields. Causal order alone does
not set elapsed time. The current nonrelativistic adapter supplies its own
physical time coordinate and is not evidence for refoliation invariance.

[Wolfram's multiway/branchial taxonomy](https://wolframphysics.org/technical-introduction/the-updating-process-in-our-models/branchial-graphs-and-multiway-causal-graphs/)
is relevant architectural inspiration. The associated
[quantum-formalism proposal](https://www.wolframphysics.org/technical-introduction/potential-relation-to-physics/quantum-formalism/)
does not make an ordinary stochastic rewrite graph a verified quantum model.
Any such port must reproduce interference and quantum operational predictions.

## 6. Next concrete deliverable

Implement a small **history-to-residual atlas** on the existing exact chemistry:

- Preserve timed event occurrences, their resolved physical dependencies,
  incoming prefix weights and the full source state.
- Map each cut to a cached full residual state and unchanged native generator.
  Share identical residuals; retain a witness for any broader description
  isomorphism. Keep the current conservative rule-provenance DAG identified as
  provenance rather than proven counterfactual causality.
- Retain occurrence/channel data and joint alternatives, including untaken
  ones. A graph diamond alone does not supply independent physical execution.
- Keep frame restrictions and native conditional weights. Do not compute a
  new prior over residual classes or renormalize away omitted jump tails.
- Export finite profiles of residual structures, rates and probability mass
  alongside the old naive counts. This gives the extent calculation an actual
  structural input while leaving its proposed arithmetic open.

The first checks are whole-description relabelling, physically different
equal-topology rates, reconvergent histories with distinct prefixes, shared
resource competition, and the existing adjacent/opposite catalytic witness.
These establish representation fidelity, not the value premise.

Then compare the two-compartment fuel extension against the shared pool on a
small exact state space: detailed balance, equilibrium marginalization and
fast-transport convergence first; finite-transport deformation second. A
mobile patch and the mobility exponent comparison follow. This orders work
by questions the existing results actually raised.

The extent remains the central open item. A quotient can remove duplicated
descriptions, but neither the number of residual process types nor their
summed probability becomes lushness by that fact. Deterministic structured
histories, finite contributions followed by dissolution, thermal fluctuations
and reliability concentration remain live challenges. Gas has no prescribed
ranking. No ethical reward/penalty sum from the attachment is adopted.

Generated runs stay local and ignored; publish code and readable results only
when requested. No simulation or push accompanied this assessment.
