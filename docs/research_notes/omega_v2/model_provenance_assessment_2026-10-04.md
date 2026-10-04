# Provenance assessment of the current physical substrate

4 October 2026. Scope: the recent local-flow, finite-fuel, spatial-binding,
catalytic-binding and historical-volume work. This is a source/code provenance
assessment, not a new numerical run or an exhaustive literature survey.

**Subsequent clarification, same day:** the originator permits heavy adaptation
supported by literature OR a sound physical/mathematical argument; exact-paper
replication is not a universal prerequisite. The new
[comparison map and choice ledger](model_comparison_map_2026-10-04.md) supersedes
any overly restrictive reading of the recommendation below. It documents
neighboring 2D model families, explicit reasons for our choices, parameter
exploration and the distinction between an information share and physical extent.

## Assessment

The current substrate is a **custom finite stochastic model built from established
methods and some physically motivated rules**. It is not presently a documented
replication or a derived variant of one particular published physical model.
Internal consistency is stronger than its demonstrated physical representativeness.

The originator now explicitly requires models established in the literature or
principled extensions with a documented connection. Broadly citing statistical
mechanics is not sufficient to meet that requirement. The next physical extension
should have a source model, an explicit mapping and a small baseline reproduction
before new mechanism combinations are introduced. This is a grounding step for
exploration, not a requirement that a lushness result be favorable or universal.

## Layer-by-layer provenance

| Layer | Current status | What the literature connection does and does not support |
|---|---|---|
| Continuous-time Markov jump dynamics; matrix propagation; first-hitting calculations | Established mathematical machinery | Numerical solutions describe the declared generator. They do not identify a physical system represented by that generator. |
| Reversible channels, stationary distribution, fuel/spent inventory, relative entropy to equilibrium | Standard stochastic-thermodynamic framework; internally checked finite construction | Chemical master-equation thermodynamics has published foundations [1]. Our selected reaction network and parameters are not thereby empirically justified. |
| Catalysis changes kinetics while leaving equilibrium unchanged | Principled kinetic construction | The catalyst remains unchanged and the same state-symmetric factor multiplies both directions. This agrees with the defining thermodynamic distinction for catalysis [2]. No derivation of our precise catalytic predicate from a molecule or published coarse model has been supplied. |
| Hard site exclusion, local motion and bonded-cluster translation | Familiar lattice/coarse-particle ingredients, custom combination | Collective motion and hierarchical self-assembly are studied in published models [3]. Inverse-size translational mobility has explicit precedent [4]. This does not make our five-site process an implementation of those models. These links are retrospective connections found in this assessment. |
| Aligned endpoint bits on a neighboring bond enable extra reaction channels | Bespoke, explicitly stipulated mechanism | Conformation-dependent chemistry is a reasonable motivation, but the exact equal-bit/local-bond rule has no paper-to-code derivation in the inspected work. Its presence cannot be a discovery of generativity. Its downstream consequences can still be nontrivial model results. |
| Equal energy per fuel packet and per bond, E = 4(F + number of bonds) | Bespoke coarse energetic choice | The rates are constructed to respect this energy and fuel degeneracy. All bonds are energetically costly, so the model selects a specific relaxation landscape. Fuel-assisted reversal regenerates fuel; thermal breakdown transfers energy to the implicit bath. This is an idealized reversible conversion mechanism, not generic biochemical fuel use. |
| Five-site geometry, four particles, one vacancy, rigid clusters, fixed flip/exchange rates | Tractability choices | Dense one-dimensional dynamics sharply restrict encounter and rearrangement possibilities. There is no mapping to measured length/time scales or a demonstrated coarse-graining of molecular motion. |
| Shared fuel stock and implicit bath | Declared coarse assumptions | Useful approximations in appropriate regimes, but their suitability for the present spatial interpretation has not been demonstrated. Shared fuel couples distant reactions without spatial transport. |
| Ancestry observer and sampled-history calculations | Internal observational extensions | Physical marginal preservation and direct tiny-case checks support the calculations. Observational history is not a physically implemented memory or decoder. |
| Flux-weighted response, frame-volume profile and coverage envelope as lushness diagnostics | Project-specific applications/readouts | Shannon information is standard mathematics; its use as the proposed extent or physical-access compression is the research hypothesis. These readouts are not independently established physical observables of lushness. |

Code inspected: [local flow](../../../omega_v2/finite/local_flow.py),
[finite fuel](../../../omega_v2/finite/fuel_flow.py),
[spatial binding](../../../omega_v2/finite/spatial_binding.py),
[catalytic binding](../../../omega_v2/finite/catalytic_binding.py), and
[history volume](../../../omega_v2/finite/history_volume.py).
The local-flow report already cites Horowitz and Esposito for its thermodynamic
information-flow setting. No source-to-generator derivation or published-model
baseline replication was located in the inspected binding/catalysis reports.
That is not a claim that no equivalent model exists anywhere in the literature.

## Where model construction can shape the conclusions

The main flexibility lies in the mechanisms and energetic assumptions, not in the
matrix solver. The aligned-bond rule explicitly supplies composition-dependent
facilitation. The positive bond energy favors eventual dissolution. The shared
fuel stock supplies nonlocal coupling. The single vacancy constrains motion.
These choices can influence access, persistence and apparent construction benefits
before any candidate readout is applied. Detailed balance alone cannot select
the right physical choices: it constrains rate ratios, not a unique kinetics.

The record has useful protections against silently tailoring a winner: physical
noise remains, costs are reported, catalytic reversal is retained, and results
include unfavorable comparisons and crossings. The lushness readout does not
enter the current physical rates. These are methodological strengths, but they
do not substitute for model provenance or physical calibration.

## What the existing work is good for

- Exact examples of how response, information, historical observations and
  resource use can separate under one declared dynamics.
- Counterexamples to overstrong claims about particular summaries.
- Reusable observation, propagation and resource-accounting machinery.
- Mechanism hypotheses worth examining in established physical models.

It does not yet establish that real chemical or biological systems occupy the
same regimes, or that the chosen generativity mechanism is a representative
coarse-graining of them. The reported results remain valid conditional on their
specified models; they need not be discarded.

## Recommended adjustment

Keep this toy as a diagnostic fixture. Before extending its physics, choose an
established substrate and attach our observation machinery to it. Candidate
sources to inspect are the collective-motion/self-assembly models in [3] and
the reversible reaction-diffusion construction in [5]. Neither is claimed to
have been implemented here, and they address different questions.

For the selected baseline, retain its published state variables, reaction/motion
rules and a published parameter case. Reproduce one inexpensive behavior or
curve before applying the project's readouts. Then document each necessary
extension with its source, physical rationale and the parameter limit that
recovers the baseline. A single source need not supply all future features,
but combining sources requires checking that their assumptions fit together.

This changes the previous extension ranking. Local fuel transport is promising
through an established spatial reaction model; elementary binding/turnover steps
are promising through a published catalytic network. Arbitrarily adding these
to the current toy is not the recommended next move. Even mesh refinement has
model-specific limits: a standard reaction-diffusion master equation is not
automatically a convergent molecular approximation; [5] supplies a particular
construction designed to address that issue.

The practical target is a defensible statement: "We reproduced this published
physical model, added these declared features, and measured these continuation
properties." Novelty can remain in the continuation analysis and its relation
to lushness. The physical substrate need not also be an ungrounded novelty.

## Sources and their scope

1. Rao and Esposito, [Conservation Laws and Work Fluctuation Relations in Chemical
   Reaction Networks](https://arxiv.org/abs/1805.12077), J. Chem. Phys. 149, 245101
   (2018). Supports the chemical-master-equation thermodynamic framework, not our
   particular lattice and catalytic rules.
2. IUPAC, [catalyst](https://goldbook.iupac.org/terms/view/C00876). Supports the
   distinction between altered reaction kinetics and unchanged reaction free
   energy, not our exact conformation-dependent implementation.
3. Whitelam, Feng, Hagan and Geissler, [The role of collective motion in examples
   of coarsening and self-assembly](https://arxiv.org/abs/0806.3903), Soft Matter 5,
   1251–1262 (2009). Published lattice/off-lattice and assembly settings investigate
   collective motion, with different consequences for different assemblies.
4. [Temperature protocols to guide selective self-assembly of competing
   structures](https://doi.org/10.1073/pnas.2119315119), PNAS (2022). Its methods
   report inverse-cluster-size translational diffusion within VMMC. This is a
   precedent for that scaling, not for our entire transition generator.
5. Isaacson and Zhang, [An Unstructured Mesh Convergent Reaction-Diffusion Master
   Equation for Reversible Reactions](https://arxiv.org/abs/1711.04220), J. Comput.
   Phys. (2018). Supplies a published spatial construction with a stated
   continuum relationship and reversible reactions; not an automatic validation
   of our hard-exclusion, rigid-cluster lattice model.
