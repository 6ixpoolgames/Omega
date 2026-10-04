# Model comparison and choice ledger

4 October 2026. Current implementation: research branch at d5c213b. This map
compares the recent catalytic substrate with established model families and
states reasons for keeping, changing or exploring its choices. No new dynamics
or numerical sweep is implemented here.

## Standard for adaptation

The originator permits substantial principled adaptation. A choice can be
supported by a published model, an explicit physical argument, a derivation,
or a clear computational simplification. A paper for every line of code is
unnecessary. Tuning and parameter sweeps are legitimate ways to locate useful
regimes, provided their purpose and selection history are visible. The aim is
to understand dynamics, not to maximize a favored lushness score.

This updates the preceding [provenance assessment](model_provenance_assessment_2026-10-04.md):
reproducing a published baseline is useful where inexpensive and relevant, not
a mandatory gate before every justified adaptation. Credibility comes from a
traceable argument about the actual rules, not attaching a citation to a model
with materially different assumptions.

## 1. Which neighboring models answer which questions?

The relationships below are comparisons identified now, not a claim that the
current code was originally copied from these sources.

| Family and source | Relevant physical content | Difference from our model | What to borrow; what not to infer |
|---|---|---|---|
| **2D catalytic surface lattice models: Ziff–Gulari–Barshad (ZGB)** [1] | Local adsorption/reaction and competition for surface sites; active and poisoned regimes | A fixed catalytic substrate with irreversible reaction rules and external reactant supply, rather than our moving, forming catalytic bonds | Strong reference for spatial occupancy and obstruction. It does not itself model apparatus constructing further apparatus, and its irreversible boundaries are not a finite equilibrium reservoir. |
| **2D reaction–diffusion pattern formation: Gray–Scott / Pearson** [2] | A small autocatalytic reaction network, feed/removal and diffusion can produce several spatial regimes | The cited model uses deterministic concentration fields and irreversible reactions; our model retains finite stochastic particles and reversible channels | Useful comparator for spatial amplification, depletion and regime maps. A striking pattern alone does not establish a new construction repertoire or a weighted continuation extent. |
| **Reversible spatial stochastic reactions: Isaacson–Zhang CRDME** [3] | A spatial jump approximation derived from a particle reaction–diffusion model; reversible association and explicit placement of products | Mesh cells are resolution elements, not automatically hard one-particle sites. Our rigid clusters, exclusion and conformation rule are additional assumptions | Strong reference for local resources, encounter geometry and spatially resolved reactions. It supplies spatial mechanics, not every assembly/catalysis rule we might want. |
| **Collective-motion self-assembly: Whitelam et al.** [4] | Assemblies move and become participants in later assembly; collective motion has different consequences in different settings | Our line supports only short chains and rigid translations; the published work examines richer assembly geometries | A close conceptual relative for compositions changing later physical development. Collective mobility should be a modeled mechanism, not an unexplained bonus for being an assembly. |
| **2D interacting-block assembly: Bupathy–Frenkel–Sastry** [5] | Oriented square components, edge interactions, cluster motion and competition between assemblies | Its interaction design targets particular structures. Our intended field does not select a target structure as the definition of success | Borrow the explicit geometry and interaction representation. Do not import target yield as lushness or silently tune our interactions to a desired final object. |

**Best fit for our next substrate:** a 2D stochastic reaction-and-assembly model,
using explicit geometry from assembly models and local reversible reactions
with a resource account. Surface-catalysis and pattern-forming systems can serve
as comparators. This is a proposed synthesis with stated assumptions, not an
already published model under a borrowed name. We need not implement all these
families, or combine every feature, before learning anything.

## 2. What we actually chose, and why

The inspected sources are [spatial_binding.py](../../../omega_v2/finite/spatial_binding.py),
[catalytic_binding.py](../../../omega_v2/finite/catalytic_binding.py), their
focused tests, and the [binding](thermal_binding_report_v0.md) and
[catalytic](catalytic_binding_report_v0.md) reports. These record the rules and
the progression from transport to catalytic reuse. Where an original design
reason was not recorded, the rationale below is explicitly a present assessment,
not an invented historical intention.

| Current choice | Defensible rationale and provenance | Effect / proposed treatment |
|---|---|---|
| Continuous-time Markov jump process | Established stochastic modeling machinery. The current calculation propagates the full finite law. | Keep as the core for event histories. In a larger model, use stochastic trajectories with small exact cases as checks; do not identify deterministic mean-field trajectories with the same finite stochastic object. |
| Five reflecting sites, four occupied | The run is explicitly small and exact. Computational tractability is a reasonable reconstructed rationale, not an empirical justification for these numbers. | Density is 0.8 and boundaries dominate. Treat size, density and geometry as exploratory choices, not universal constants. |
| One particle at most per site | A clear excluded-volume idealization; common in surface/lattice assembly models. | Keep if a site represents physical occupancy. Do not inherit it automatically if a site becomes an arbitrary reaction–diffusion mesh voxel. |
| Identical particles carrying binary internal states | Minimal finite internal structure without organism/constructor labels. | Keep as an explicit two-state abstraction if useful. The bit is not currently a derived molecular conformation or orientation. Additional physical types are allowed if their interactions, rather than their names, do the work. |
| Bonded cluster translation at mobility/n | Makes composites mobile while slowing larger groups; collective diffusion has published precedent [4,5]. The exact scaling remains a coarse choice. | In 2D, specify translation, rotation and deformation separately. A citation to collective motion does not supply all three rates. |
| Internal-state exchange at rate 1, whether bonded or unbound | The reports explicitly avoid giving bound particles a special exchange-speed advantage. | It transports internal distinctions even without whole-particle translation. Interpret it as an effective exchange channel, not automatically literal molecular swapping. Retain or replace with a stated microscopic/effective rationale. |
| Independent internal flips at rate 0.05 | Preserves spontaneous state change and a competing timescale; the magnitude has no identified empirical calibration. | Sweep flip time relative to reaction/transport times. A change of overall time units cannot change this ratio. |
| Thermal bond formation and breakdown | Provides a reversible equilibrium reference with ongoing events. | Keep the principle. The chosen energetics and barrier placement are separately revisable. |
| E = 4(F + number of bonds) | Gives transparent storage/accounting and simple matching. No identified physical reason forces equal fuel and bond energies, or makes all bonds costly. | Separate fuel free-energy differences from bond energetics when useful, then rederive all forward/reverse ratios and the stationary law. Changing only one rate while keeping the old equilibrium would be inconsistent. |
| Finite F/spent inventory with binomial degeneracy | A simple count of a fixed inventory in two states, with rates proportional to available reactants. | A legitimate finite reservoir idealization. Its rates and degeneracy must remain consistent when the inventory is spatialized or resolved into individual particles. |
| Fuel-assisted breakdown can regenerate fuel | This is the reverse of the modeled energy-storage reaction, not a bookkeeping refund added after simulation. | Defensible as a reversible conversion pathway. It is not generic fuel-consuming maintenance chemistry; alternative stoichiometries need an explicit reaction scheme. |
| Shared well-mixed fuel | Removes transport variables and permits exact small calculations. This is a present computational rationale, not a demonstrated fast-mixing limit. | Keep as a limiting comparison. Local fuel introduces a real mechanism and can reveal when the well-mixed assumption fails. |
| Neighboring bond with equal endpoint bits supplies catalysis | Explicit hypothesis that local structure changes another reaction's kinetics. The equality predicate preserves global bit-inversion symmetry and does not name a preferred bit value. | The general idea is defensible; the exact predicate is bespoke. Compare simple alternative local configurations or replace it with binding/orientation mechanics, for a stated physical question. Do not merely multiply catalysts until a preferred readout rises. |
| Same unchanged-context catalytic factor on each reverse pair | Preserves the forward/reverse ratio and equilibrium. This is a direct mathematical justification, consistent with catalysis's kinetic role [6]. | Keep this constraint when changing rates in the equilibrium model. With explicit external drive, account for reservoirs and local thermodynamics instead of demanding global equilibrium. |
| Two catalytic neighbors add parallel pathways | A simple independent-channel assumption. | It is not a model of a shared occupied active site. Saturation/exclusion requires intermediate states or another justified reduced-rate law. |
| Full laws and resource profiles retained alongside readouts | Enables diagnosis when a summary conceals a physical difference. | Keep. It does not validate a bad summary merely because the source data survive. |

The progression had identifiable experimental purposes: the spatial extension
tested moving particles and binding instead of a fixed record apparatus; the
catalytic extension added construction affecting subsequent construction; the
history observer tested what original-bond monitoring misses. Those purposes
justify investigating the mechanisms. They do not establish that the chosen
numbers or every local rule are representative of real chemistry.

## 3. Parameter ledger and legitimate exploration

Current time units are abstract. One overall reference rate can define a unit;
the remaining rate ratios are substantive. The fixed values below are code
facts, not estimates of universal physical constants.

| Quantity | Current choice | Appropriate justification or exploration |
|---|---|---|
| Occupancy | 4/5 | Sweep density separately from system size; include less crowded states and larger domains. |
| Boundaries | Reflecting line | Compare reflecting/periodic domains where they answer a geometry question; an open boundary must specify influx/outflux. |
| Fuel inventory B | 3 | Explore fuel per particle or available reaction opportunity; retain the distribution and matching convention. |
| Fuel and bond energy parameter | Both 4 in thermal units | Separate the two physical roles; investigate costly, favorable and kinetically persistent assemblies without assigning any of them a lushness bonus. |
| Catalytic barrier reduction b | 0, 1, 2 | For one catalytic neighbor these give rate factors 1, 2.718 and 7.389. They are three strengths, not three levels of recursive organization. Explore relative to encounter, reversal and internal-flip rates. |
| Background fuel reaction coefficient | 0.25 times available F or spent stock | Compare actual reaction times in specified local contexts with transport and degradation times; the coefficient alone is not a concentration-independent reaction hazard. |
| Thermal bond prefactor | 0.02 | Its forward/backward rates are 0.02 exp(−2) and 0.02 exp(2) under the current energy. Vary barriers separately from equilibrium preference. |
| Monomer motion scale | 0.1 or 1 in earlier runs; 1 in catalytic run | Compare diffusion and reaction times; retain cluster-size dependence. |
| Internal exchange / flip | 1 / 0.05 | Explore the lifetime and spread of the conformation that supports catalysis. |
| Observation times | Selected finite cuts and lags | Choose them relative to relaxation, reaction and transport times; observation refinement must not be confused with a change of physics. |

A practical sweep can use ratios such as reaction time / encounter time,
breakdown time / construction time, internal-state lifetime / reaction time,
and supply time / consumption time. Define these in stated contexts; no single
number covers every occupancy and concentration. Broad logarithmic exploration
followed by denser sampling around changes is reasonable. Record why ranges
were chosen and retain quiet, jammed, rapidly relaxing and active regimes.

Tuning to resolve otherwise invisible dynamics, reproduce a known behavior,
or examine a transition is legitimate. Selecting a tuned region for detailed
study is legitimate too; identify it as selected. Tuning to maximize the
proposed lushness ranking and presenting the resulting alignment as independent
evidence is circular. No compulsory preregistration is introduced here.

## 4. Geometry is an explanatory variable

The current line excludes geometric loops and alternative spatial routes;
the shared fuel nevertheless supplies a nonlocal coupling. A 2D extension
can separate those effects. Useful geometry questions include:

- Do alternate routes change how a disturbance or resource shortage propagates?
- Does local crowding inhibit encounters, or keep reaction partners together?
- Do compact aggregates, extended chains and loops expose different reaction
  surfaces and transport paths under the same local interactions?
- Do rotation and orientation open reactions that translation alone cannot?
- Does localized supply produce different organization from a rapidly mixed stock?

Moving from a line to a square lattice also changes the number of neighbors.
Keep a ledger of spacing, density, domain size, interaction radius and rate
convention. Holding a rate per contact fixed and holding a total attempt rate
per particle fixed answer different questions. For a simple nearest-neighbor
diffusion discretization with spacing a, per-neighbor hopping D/a^2 supplies
the conventional diffusion scaling; a coarse physical lattice need not be
interpreted as a continuum discretization at all. State which interpretation
is intended before comparing grid sizes.

Product placement after reactions is another geometric assumption. In bounded
reversible particle models it can affect detailed balance near walls [7]. Thus
"add 2D" requires explicit movement and placement rules, not just a larger array.
None of these questions requires a favored structure or a value label.

## 5. The readout needs a direct verdict

The implemented local formula is

    V_phi = 2^(I(X;R_phi) - H(X)) = 2^(-H(X|R_phi)).

It measures how little uncertainty about a declared X remains given R_phi.
For our historical projections, this becomes 2^(H(R_phi)-H(X)). This is a
coherent information diagnostic, but **using it alone as the sought physical
continuation volume is a category mistake**. The formula does not specify
physical transformation costs, a common extent across different encompassing
objects, or which further joint compositions those records support. Equal
information can require different physical decoding or recovery routes, as
the repository's existing examples demonstrate.

Normalizing the encompassing frame to one is not itself the error. Promoting
these local normalized information shares to the missing physical extent,
without the additional construction, is the error. More simulation of that
formula cannot supply what it does not represent. Retain the calculation and
its counterexamples as diagnostics; do not tune the physics to rescue it as
lushness. A future proposal needs to state its carrier and how physical
composition changes the measured extent before implementation earns priority.

## 6. Recommended next design step

Draft a small 2D stochastic reaction-and-assembly specification using this
ledger. Keep only the mechanisms needed for the immediate geometry question:
explicit positions, reversible local transformations, resource inventory,
and composition-dependent rates. Decide whether sites represent excluded
physical locations or mesh cells, then choose the corresponding transport
and reaction conventions. Add rotation, catalytic occupancy, or local fuel
only where the question needs them; document the approximation if deferred.

Each rule should have five fields: **rule; source or reasoning; physical role;
parameter interpretation; observable consequence/limiting comparison**.
For example, spatial fuel is justified by finite transport, and its fast-mixing
limit supplies a comparison with our current shared pool. Do not claim that
limit reproduces every old rate unless the averaging actually gives it.

A small published example or an analytic limiting case is a useful check of
the borrowed part. It need not become a lengthy replication project. The
scientific description can be precise about a heavily modified model: "a 2D
stochastic reaction-and-assembly model using these established ingredients,
with these physically motivated extensions." That is stronger than either
pretending nothing is new or presenting every choice as unconstrained invention.

## 7. Agreed simplifications and proposed chemical representation

Follow-up, 2026-10-04. The user accepts reversible catalysis, a shared finite
fuel pool initially, increasing particle counts in 2D, and keeping a simple
representation until a physical question requires more resolution. These are
design directions; no 2D implementation or new run has been made.

**Internal state.** A two-state particle can represent two coarse conformations
of the same building block. Whitelam et al. [8] explicitly model switching
between two internal states favoring different local binding geometries.
This supplies a precedent for state-dependent interactions, not a derivation
of our present equal-bit catalytic predicate. Position is a separate variable;
an internal conformation is not a direction on the square lattice. An initial
isotropic interaction table can defer explicit orientation. If the mechanism
requires directional recognition or steric exposure, patches/orientation then
become necessary. A state switch must include changes in its existing contacts
when determining its energy change. Symmetric switch rates are justified only
when the total free-energy change vanishes.

**Energies.** Borrow additive local contact energies from lattice assembly [5]
and finite chemical-inventory thermodynamics from [9]. One proposed minimal
combination is

    G(x) = sum_i g(s_i) + sum_b g_b(s_i,s_j) + G_pool(n_F).

Here sites have excluded occupancy, explicit bonds are local, and contact
energies may be favorable. These are effective coarse free energies at fixed
temperature; spatial configurations are already explicit and their entropy
must not be counted again inside G. For an ideal shared pool with fixed total
B of interconvertible fuel/waste molecules, an elementary inventory model is

    G_pool(n_F) = n_F*g_F + (B-n_F)*g_W
                  - k_B*T*log(binomial(B,n_F)),

up to a constant at fixed volume and B. The combinatorial term represents
unresolved inventory arrangements. It must not also be inserted as an extra
degeneracy factor in the equilibrium distribution. This is a proposed ideal
pool specialization, not a claim that [9] supplies our complete spatial model.

Fuel and bond free energies are independent physical parameters. In particular,
the old equality between the cost of a bond and one fuel packet is dropped.
The forward/reverse rate ratio for each paired mechanism is fixed by the full
state free-energy change, including inventory multiplicity:

    q(x,y) / q(y,x) = exp(-(G(y)-G(x))/(k_B*T)).

This constrains a ratio, not an absolute speed. Kinetic barriers/attempt rates
remain separately specified. A catalyst lowers a common transition barrier
for a forward/reverse pair without changing its equilibrium ratio. The local
contact arrangement responsible for that lowering still needs a declared
mechanistic rationale; state names alone do not provide it. The exact rule is
not yet selected. A spontaneous thermal bond break need not regenerate fuel;
only reversal of the explicitly fuel-coupled reaction does that. Reversibility
does not require equal forward and reverse rates.

**Spatial and numerical scope.** Start with excluded sites on a 2D lattice,
short-range interactions, two internal states, reversible binding and switching,
and a shared finite fuel/waste pool. Shared fuel approximates mixing faster
than its consumption; it cannot yet resolve local depletion or supply shadows.
Treat the lattice as a coarse physical geometry, not automatically a numerical
mesh whose refinement represents the same world. Movement and boundary rules
still need an explicit choice consistent with the same equilibrium law.

Use sampled continuous-time trajectories at larger N, retaining an exactly
solvable tiny version. Tens of particles (for example 16-64 after a runtime
pilot) are a computational starting range, not a chemical calibration. Vary N
at fixed occupancy fraction and fuel per particle to distinguish system size
from concentration; study density separately. Store physical events and states
so later continuation diagnostics need not depend on one chosen score. Exact
enumeration of every state/frame does not scale with N and is not promised.

Add spatial fuel, orientation, explicit catalyst binding/occupancy or additional
conformations when the current representation cannot express the mechanism
being asked about, or when a targeted refinement changes the interpretation.
An unfavorable lushness readout is not itself a reason to add physics.

## 8. Implementation follow-up

The first 2D pilot is now implemented and run. The design discussion in
Section 7 above records the preceding stage. See the
[implemented protocol](lattice_chemistry_protocol_v0.md) for the exact local
template rule and rates, and the [pilot report](lattice_chemistry_report_v0.md)
for 384 trajectories at 16/36 particles. Bond and fuel energies are separated;
all physical reverse pathways and the finite ideal pool are retained.
No lushness aggregation was added. The philosophical direction assessment is
[recorded separately](persistence_addendum_assessment_2026-10-04.md).

## Primary sources

1. Ziff, Gulari and Barshad (1986), [Kinetic Phase Transitions in an Irreversible
   Surface-Reaction Model](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.56.2553).
2. Pearson (1993), [Complex Patterns in a Simple System](https://arxiv.org/abs/patt-sol/9304003).
3. Isaacson and Zhang (2018), [An Unstructured Mesh Convergent Reaction-Diffusion
   Master Equation for Reversible Reactions](https://arxiv.org/html/1711.04220v2).
4. Whitelam, Feng, Hagan and Geissler (2009), [The role of collective motion in
   examples of coarsening and self-assembly](https://arxiv.org/abs/0806.3903).
5. Bupathy, Frenkel and Sastry (2022), [Temperature protocols to guide selective
   self-assembly of competing structures](https://doi.org/10.1073/pnas.2119315119),
   with [author manuscript](https://arxiv.org/abs/2110.11274). The lattice/interaction
   structure is the relevant borrowing; its target-design objective is separate.
6. IUPAC, [catalyst](https://goldbook.iupac.org/terms/view/C00876).
7. Zhang and Isaacson (2022), [Detailed Balance for Particle Models of Reversible
   Reactions in Bounded Domains](https://arxiv.org/abs/2201.04099).
8. Whitelam et al. (2009), [The impact of conformational fluctuations on
   self-assembly: cooperative aggregation of archaeal chaperonin proteins](https://wrap.warwick.ac.uk/id/eprint/28672/).
   Supports two-state conformational particles and geometry-dependent assembly,
   not our particular catalytic predicate or an identical 2D lattice model.
9. Rao and Esposito (2018), [Conservation Laws and Work Fluctuation Relations
   in Chemical Reaction Networks](https://arxiv.org/abs/1805.12077), especially
   the closed-network local-detailed-balance relation in Section III B.
