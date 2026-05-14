# Omega Project Manual

Last updated: 2026-05-14

Repository: https://github.com/6ixpoolgames/Omega

## Purpose

This repository is the local validation workspace for the Omega theory project.
Its purpose is not to prove the theory by simulation. Its purpose is to extract
candidate mathematical objects, make them operational, test them against nulls,
and force clear failure modes.

Project stance:

- scientific and skeptical;
- minimal before broad;
- propagation/viability before entropy;
- controls and nulls before interpretation;
- toy-substrate evidence must not be overstated as theory validation.

## How A New Codex Instance Should Start

1. Read this file.
2. Read `docs/OMEGA_RUNNING_LOG.md`.
3. Read `README.md`.
4. Inspect the latest probe scripts:
   - `probe_09_robust_fiber_reachability.py`
   - `probe_10_com_viable_propagation_robustness.py`
   - `probe_I0_invariant_stack_audit.py`
   - `probe_DA1b_apparent_vs_viable_slack.py`
   - `probe_DA1c_noncommutative_relational_history.py`
   - `probe_DA2_relational_edge_memory_world.py`
   - `probe_DAX_branching_connection_graph_validity_revised.py`
   - `probe_DAX_G0_minimal_DAR_rule_space_persistence.py`
   - `probe_DAX_G1_persistence_motif_anatomy_and_robustness.py`
   - `probe_DAX_G2_persistence_phase_map_minimal_rule_spaces.py`
   - `probe_DAX_G2b_control_adjusted_primitive_guardrail.py`
   - `probe_DAX_G3_q3r1_guardrailed_phase_map.py`
5. Inspect compact summaries, not raw caches:
   - `probe_09_robust_fiber_reachability_results/summary.json`
   - `probe_10_com_viable_propagation_robustness_extended_results/summary.json`
   - `probe_10_com_targeted_fragility_refinement_results/summary.json`
6. Preserve the running log after every meaningful run.

Use this Python executable locally:

```powershell
.\.venv\Scripts\python.exe
```

Use 18 worker processes for CPU-heavy runs unless deliberately stress testing.

## Context From The Theory/Paper Side

The broader Omega work, as represented in the handoff documents and older local
papers, is trying to determine whether there is a real scientific object behind
the proposed Omega formalism.

The recurring conceptual thread is:

> Omega is not raw entropy. Omega is viable propagation.

Older papers and drafts motivate variants of:

- viable futures;
- irreversibility and recoverability;
- field-like gradients over future viability;
- agency under computational irreducibility;
- gradient/value interpretations;
- multifield or fiber formulations where coupled systems preserve viable
  structure through lower-dimensional macro descriptions.

Important caveat: the original papers are not all reproduced inside this repo.
Some source PDFs are now included under `docs/progenitor_drafts/` as early
theoretical provenance. They are drafts only and should not be treated as
current validation results, peer-reviewed claims, or final formal statements.
The current theory/status draft lives under `docs/current_theory/`. Active
trajectory-space branch notes live under `docs/research_notes/trajectory_space/`.
Some text drafts still live only in the local project folder outside Git.

## Working Definitions

### Single Omega

Early executable work used:

```text
I_T^C(s) = H(F_T(s) / C)
```

where:

- `F_T(s)` is the set of viable trajectories from state `s` to horizon `T`;
- `C` is a coarse-graining;
- `H` is Shannon entropy over distinguishable viable macro-trajectory classes.

This was useful but dangerous because high entropy can be meaningless if it is
created by random labels, noise, or overfragmentation.

Single-Omega work therefore shifted toward profile tuples:

```text
p_viable
H_conditional
H_weighted = p_viable * H_conditional
H_recovery
coarse-graining/admissibility diagnostics
```

The strongest lesson from the single-object phase:

> Entropy is diagnostic. It is not the object.

### Multifield / Fiber Omega

The multifield branch asks whether coupled systems produce viable macro-fiber
transport that survives null comparisons.

Core objects:

- macro nodes: states/classes induced by a kappa map;
- fibers: sets of viable micro-trajectories realizing a macro node/path;
- certified nodes: macro nodes with enough viable fiber mass;
- certified edges: transitions with enough viable transported mass;
- viable propagation: multi-step propagation through certified fibers while
  preserving component structure.

Primary current diagnostic:

```text
viable_propagation_index =
certified_path_mass_survival_to_final_segment
* transport_survival_mean
* min(component_A_preservation, component_B_preservation)
* (1 - singleton_fraction)
```

This index is a summary diagnostic, not a law.

## Probe Line Summary

### Environment And Early Single-Omega Probes

The environment was calibrated on a Ryzen 5900X and RTX 4070 Ti. For these
Python/NumPy CPU probes, process parallelism dominates. The working target is
18 worker processes.

Early probes established:

- local Python/NumPy/pandas/matplotlib workflow is functional;
- large multiprocess runs write stable CSV/JSON artifacts;
- naive entropy is insufficient;
- random/high-cardinality coarse-grainings can look falsely rich;
- admissibility and estimator integrity are central.

### Probe 06a: Minimal Admissible Quotient Gate

Goal: distinguish useful coarse-grainings from null labels.

Result:

- predictive/behavioral quotients were more credible than random/hash labels;
- identity/all-one diagnostics behaved as expected;
- some trap-mixing cases were too permissive, motivating stronger profile tests.

### Probe 07 / 07b: Omega Profile Decomposition

Goal: decompose viability, entropy, recoverability, and estimator behavior.

Key result:

- irreversibility remained visible in profile components;
- hash/random labels could be entropy-rich without being meaningful;
- long horizons made raw `p_viable` contrasts shrink, while conditional and
  recovery-weighted entropy still carried signal;
- tuple reporting became mandatory.

### Supplementary Single-Omega Sanity Check

Goal: see whether claimed older single-Omega reports could be qualitatively
reproduced.

Result:

- calibrated reconstruction reproduced six qualitative flags:
  - irreversible sink filtering;
  - survival insufficiency;
  - trajectory-feature ordering;
  - noise robustness;
  - state-marginal poor proxy;
  - feature-map robustness.

Caveat:

- this was reconstruction, not exact original-code reproduction.

### Probe 08a: Multifield Profile Reconciliation

Goal: revisit old multifield hints around:

```text
F,T initial pair
attractive coupling
center_of_mass kappa
alpha around 0.45-0.525
```

Result:

- `center_of_mass` did not look like raw positive richness;
- it showed negative/mixed entropy deltas but positive transport advantage;
- `boundary_v2_regime_sequence` produced pseudo-risk behavior: high richness
  without transport support.

Interpretation:

> The multifield object, if present, is likely transport/fiber persistence, not
> raw entropy expansion.

### Probe 08b: Transport-Dominant Multifield Validation

Goal: test the transport-dominant interpretation at higher sampling.

Result:

- `center_of_mass` survived as stable transport-positive, entropy-negative,
  non-overfragmented, and component-preserving at primary horizons;
- `joint_basin` and `basin_transition_profile` showed stronger one-step
  transport but required multi-step testing;
- `boundary_v2_regime_sequence` remained pseudo-risk.

### Probe 09: Robust Fiber Reachability

Goal: test multi-step viable propagation through certified fibers.

Run:

- `N_TRAJ=10000`
- `160` seeds
- `800` bootstraps
- 18 workers
- horizons `900, 1500, 2400`
- kappas: `center_of_mass`, `joint_basin`, `basin_transition_profile`,
  `boundary_v2_regime_sequence`

Result:

- `center_of_mass` was the only clean multi-step viable propagation-positive
  kappa across all alpha/horizon rows;
- `joint_basin` and `basin_transition_profile` looked like local transport
  artifacts rather than robust multi-step propagation;
- `boundary_v2` stayed pseudo-risk/control-like.

Reference COM propagation deltas vs shuffled:

```text
alpha=0.45:  T900 +0.0576, T1500 +0.0708, T2400 +0.0787
alpha=0.50:  T900 +0.0699, T1500 +0.0867, T2400 +0.0948
alpha=0.525: T900 +0.0752, T1500 +0.0954, T2400 +0.1014
```

Interpretation:

> Within the toy substrate, the first credible multifield object is COM-like
> viable propagation.

### Probe 10: COM Viable Propagation Robustness

Goal: test whether the COM channel survives perturbations.

Perturbation families:

- potential shape;
- noise;
- sink threshold;
- initial location;
- time discretization;
- certification threshold/reference checks.

Contained run:

- `N_TRAJ=7500`
- `80` seeds
- `500` bootstraps
- 2 variants/family
- all controls

Result:

- COM overall retention about `0.96`;
- sink and initial-location perturbations retained strongly;
- noise and potential shape were weaker.

Extended run:

- `N_TRAJ=10000`
- `160` seeds
- `800` bootstraps
- 10 variants/family
- all controls
- runtime about 5.1 hours

COM retention:

```text
initial_location:     1.000
noise:                0.878
potential_shape:      0.922
reference:            1.000
sink_threshold:       1.000
time_discretization:  0.944
overall:              0.950
```

Targeted refinement:

- COM only;
- 20 variants each for noise, potential shape, time discretization;
- `N_TRAJ=10000`, `160` seeds, `800` bootstraps;
- runtime about 5.6 hours.

COM retention:

```text
noise mild:                 0.956
noise moderate:             0.800
potential_shape mild:       0.933
potential_shape moderate:   0.844
time_discretization mild:   0.933
time_discretization moderate: 0.956
reference:                  1.000
overall:                    0.905
```

Interpretation:

> COM viable propagation is robust in the toy substrate, but the channel is
> sensitive to harder noise and potential-shape perturbations. Failures are
> mostly component-preservation/erasure failures rather than estimator failures.

### Probe 11: Learned Predictive Kappa

Goal: test whether a simple learned quotient can discover viable propagation
without being handed COM bins as labels.

Run:

- `N_TRAJ=3000`
- `100` seeds
- `300` bootstraps
- 18 workers
- train alphas `0.45, 0.50`
- test alpha `0.525`
- train horizons `900, 1500`
- test horizons `1500, 2400`
- train/validation/test variants: `25 / 12 / 24`

Learned candidates:

- `predictive_kmeans_k5`
- `predictive_kmeans_k8`
- `predictive_kmeans_k13`
- `predictive_kmeans_k21`
- `predictive_kmeans_no_COM_k8`
- `predictive_kmeans_no_COM_k13`

Result:

- best validation quotient: `predictive_kmeans_k21`;
- best learned COM association: about `0.468`;
- best learned mean test delta viable propagation vs shuffled: about `-0.0023`;
- COM mean test delta viable propagation vs shuffled: about `+0.0849`;
- `predictive_kmeans_k5` and `predictive_kmeans_k8` showed partial
  propagation-positive behavior, but the learned family did not recover COM as a
  strong coordinate;
- higher-k learned quotients tended toward fragmentation and entropy-positive
  pseudo-risk behavior.

Interpretation:

> Simple learned predictive quotients can see part of the signal, but COM
> remains the stronger analytic coordinate in the current toy substrate.

### Probe 12: COM Formalization + Learned-Kappa Diagnosis

Goal: separate the COM witness from the learned-kappa failure mode.

Run:

- `N_TRAJ=3000`
- `100` seeds
- `300` bootstraps
- 18 workers
- alphas `0.45, 0.50, 0.525`
- horizons `900, 1500, 2400`
- runtime about 38.3 minutes.

Probe 12A audited COM as a fiber-transport witness:

```text
COM viable propagation index:      0.2556
COM delta vs shuffled:             +0.0673
component B preservation:          0.7893
lower-rank erasure:                0.1054
singleton fraction:                0.4567
```

Threshold sensitivity was small:

```text
loose:  0.2569
main:   0.2556
strict: 0.2537
```

Control nuance:

- `boundary_v2_regime_sequence` and `joint_basin` can score high in absolute
  viable-propagation-index terms in the anatomy table;
- their average deltas vs shuffled are negative;
- COM remains the positive baseline-separated witness.

Probe 12B diagnosed learned-kappa failures:

- higher-k predictive k-means mostly splits COM fibers and inflates
  small-fiber/fragmentation structure;
- lower-k variants can merge distinct COM fibers;
- `predictive_kmeans_k5` and `predictive_kmeans_k8` remain partial quotients,
  not replacements;
- `predictive_kmeans_k21` can win validation while failing the heldout
  propagation/anatomy test.

Probe 12C smoke-tested transition-aware balanced predictive clustering:

- best smoke learner: `transition_balanced_k21`;
- validation predictive loss: `4.26e-05`;
- COM association: `0.443`;
- useful as a direction, but not yet a propagation-scale replacement for COM.

Interpretation:

> COM remains the current witness. Learned-kappa work should be revised after
> the COM fiber-transport object is formalized.

### Probe T0: Trajectory-Space Branch Triage

Goal: decide whether the trajectory-space pivot is worth a first formal probe,
and if so which readout family should lead.

Run:

- `N_TRAJ=15000`
- `180` seeds
- `200` bootstraps
- 18 workers
- single worlds: open field, sink trap, rigid attractor, noise swamp
- multifield corridor: `alpha=0.50, 0.525`, horizons `900, 1500`
- controls: coupled, product, shuffled, time-shuffled, independent alpha-0
- runtime about 8.4 minutes
- GPU concentration path used on about `95.8%` of seed evaluations.

Branch scores:

```text
concentration_collapse:          12
component_balance:               12
predictive_temporal_dependence:  11
tube_thickness:                  11
kernel_hazard_erosion:           10
restoration:                     10
```

Interpretation:

> The trajectory-space branch is worth one focused T1 probe, but this does not
> supersede the COM fiber-transport trunk. The next trajectory-space target is
> viable trajectory geometry: concentration-collapse as the lead geometry
> readout, component-balance as the non-redundancy guardrail, and predictive
> temporal dependence as a secondary diagnostic.

### Probe T1: Viable Trajectory Geometry

Goal: falsify or support the T0 trajectory-geometry branch under clean
false-positive controls.

Run:

- `N_TRAJ=15000`
- `180` seeds
- `300` bootstraps
- 18 workers
- alphas `0.45, 0.50, 0.525`
- horizons `900, 1500, 2400`
- conditions: coupled, product, shuffled, time-shuffled, independent alpha-0
- false-positive controls: rigid collapse, noise fakeout, single-component
  erasure
- grouped GPU geometry batches, not seed-loop GPU calls
- runtime about 24.7 minutes
- GPU usage fraction `1.0`
- max GPU temperature `52 C`
- no thermal throttle events.

Result:

```text
geometry_branch_supported: false
effective_rank correlation with p_viable_T: 0.271
component_balance_passed: false
temporal_fakeout_passed: false
strongest positive effective-rank null delta: +0.0017
```

Important failure modes:

- `rigid_collapse` leaves effective rank nearly unchanged because rank is mostly
  scale-invariant;
- `noise_fakeout` scores higher effective rank than coupled, which means
  unstructured variance can masquerade as geometry;
- `time_shuffled` also scores high, so the current geometry readouts do not
  enforce temporal order strongly enough;
- `single_component_erasure` is detected correctly, but the coupled condition
  itself has weak component balance.

Interpretation:

> T1 demotes simple effective-rank/collapse geometry from candidate object to
> diagnostic. The trajectory-space branch may still be useful, but it needs a
> failure-mode/component-erasure atlas or a stronger temporal-order-sensitive
> metric before scaling.

### Probe T1F: Ordered Trajectory Structure Atlas

Goal: test whether the trajectory-native branch survives after replacing
generic geometry with ordered distinction structure.

Run:

- `N_TRAJ=15000`
- `180` seeds
- `300` bootstraps
- 18 workers
- alphas `0.45, 0.50, 0.525`
- horizons `900, 1500, 2400`
- conditions: coupled, product, shuffled, time-shuffled, independent alpha-0
- false-positive controls: rigid collapse, noise fakeout, single-component
  erasure, endpoint fakeout
- runtime about 25.2 minutes
- GPU usage fraction `1.0`
- max GPU temperature `49 C`
- no thermal throttle events.

Family scores:

```text
component_conditioned_temporal_continuity: 15
ordered_distinction_persistence:          14
conditional_temporal_dependence_proxy:    14
minimal_recoverable_continuation:         14
```

Guardrail result:

```text
component_continuity_passed: false
false-positive rejection: failed
best metric correlation with p_viable_T: 0.442
```

Important details:

- The pivot fixed one T1 failure mode: noise fakeout scored near zero on ordered
  persistence.
- The pivot did not fix endpoint and single-component false positives.
- Component-conditioned temporal continuity was the top scoring diagnostic, but
  it still failed the global component-continuity threshold and did not reject
  false positives strongly enough.

Interpretation:

> T1F demotes the trajectory-native branch for now. Ordered distinction readouts
> are useful diagnostics, but not yet a candidate object. The better next move
> is COM fiber-transport formalization or a separate agent-relevant
> distinction/control probe.

### Probe I0: Invariant Stack Audit

Goal: give the trajectory-native branch one longer stacked-invariant test before
returning to COM formalization.

Run:

- `N_TRAJ=15000`
- `180` seeds
- `300` bootstraps
- 18 workers
- alphas `0.45, 0.50, 0.525`
- horizons `900, 1500, 2400`
- GPU metric path used throughout
- runtime about 47.3 minutes.

Invariants:

- `I1_viability`
- `I2_ordered_distinction_persistence`
- `I3_component_non_erasure`
- `I4_counterfactual_affordance_relevance`
- `I5_minimal_recoverability`
- `I6_horizon_coherence`

Ablation:

```text
S1: retention 0.444, known rejection 0.556, holdout rejection 0.556
S2: retention 0.111, known rejection 0.917, holdout rejection 0.833
S3: retention 0.111, known rejection 1.000, holdout rejection 0.833
S4: retention 0.000, known rejection 1.000, holdout rejection 0.944
S5: retention 0.000, known rejection 1.000, holdout rejection 1.000
S6: retention 0.000, known rejection 1.000, holdout rejection 1.000
```

Interpretation:

> Probe I0 does not rescue the trajectory-native branch. The invariants become a
> strong rejection filter, but not a coupled-object witness. The decisive
> ablation pattern is that rejection improves while coupled retention collapses.
> This makes the result useful as a falsification of the current
> trajectory-stack attempt, not as support for a new trajectory object.

### Probe I0b: Invariant Threshold and Dropout Audit

Goal: determine whether Probe I0 failed because of overstrict thresholds or
hard AND-stacking rather than because the trajectory-native invariant profile is
insufficient.

Run:

- reused existing Probe I0 estimator outputs;
- no simulation rerun;
- analysis runtime under one second.

Best hard threshold result:

```text
threshold family: coupled_q10
stack: S5
coupled retention: 0.533
known rejection: 0.722
holdout rejection: 0.833
balanced score: 0.321
```

Best soft stack result:

```text
rule: I3 mandatory plus 1 of I2/I4/I5/I6
coupled retention: 0.222
known rejection: 0.806
holdout rejection: 0.500
balanced score: 0.090
```

Interpretation:

> I0b confirms the branch closure. Relaxing thresholds recovers coupled
> retention, but control rejection falls below the reopen criterion. Soft stacks
> do not recover enough coupled retention. I5 and I6 remain diagnostics rather
> than gate-ready invariants.

## Current Scientific Position

What we can say:

- We have not validated Omega as a scientific theory.
- We have extracted an executable candidate object in a toy multifield substrate.
- The best current object is:

```text
COM-like multi-step viable propagation through certified fibers
in F,T attractive coupling
alpha approximately 0.45-0.525
horizons 900-2400
```

- The object survives product/shuffled/independent baselines.
- It survives a meaningful perturbation battery.
- It is not merely high entropy.
- A first learned-quotient test partially sees the signal but does not replace
  COM.
- A follow-up diagnosis shows the simple learned route mostly fails by
  splitting/merging COM fibers and by small-fiber inflation.
- A quotient-light trajectory-space triage found a plausible parallel branch,
  but only as roadmap evidence; it is not yet a validation result.
- T1 then falsified the simple geometry-positive version of that branch under
  noise, time-shuffle, rigid-collapse, and component-erasure controls.
- T1F tested a stricter ordered-structure pivot and still failed global
  component/false-positive guardrails, so trajectory-native work is currently
  diagnostic rather than object-defining.
- I0 tested the stacked-invariant version of that branch and found an
  overconstraint failure: strong false-positive rejection with zero coupled
  retention in the best stacks.
- I0b checked whether this was merely threshold/conjunction overstrictness. It
  found partial continuous separation, but no robust hard or soft profile that
  met the branch-reopen criteria.
- Probe 13 smoke returned to COM/fiber formalization and confirmed a base-null
  signal, but the first formal definition admitted component-only,
  time-shuffled, rigid-collapse, endpoint, and delayed-trap false positives.
- Probe 13b smoke tested minimal refinements for those false positives. COM
  remained base-null positive, but failed the refined object via component
  necessity, within-fiber nondegeneracy, and delayed-trap/late-retention
  blockers.
- Probe DA0 opened a new discrete primitive branch around distinction,
  asymmetry, and relation. The smoke result made full_DAR the best aggregate
  world, but did not reject the relation-shuffled control, so DA0 needs relation
  metric refinement before scaling.
- A primitive-branch theory addendum now frames relation as persistent
  causal-history dependence and points toward connection-like transport,
  closure, and viable slack.
- Probe DA0b rejected random-stepwise relation, but failed overall because
  relation lock-in and independent distinction still dominate key scores. DA0b
  should not be scaled until viable slack and relation-conditioned lineage are
  tightened.
- Probe DA1 tested viable slack as a phase hypothesis. It found positive
  relation-lineage excess with closure and alternatives, but the best point was
  an extreme and lock-in/symmetric controls still looked viable, so the phase
  map is not ready for main-scale validation.
- Probe DA1b diagnosed apparent versus viable slack. It rejects the prior
  lock-in and symmetric false positives under stricter future-distinct and
  asymmetry diagnostics, but the extreme corner remains strongest and is
  classified as apparent slack, not viable slack. DA1 needs a world-design
  revision rather than a larger grid.
- Probe DA1c implemented asymmetry as non-commutative relational history:
  `A then B != B then A`. The smoke result still failed because the
  no-relation non-commutative control ranked best, W5 had no positive
  relation-conditioned excess, and asymmetry remained non-load-bearing. The DAR
  world family should be paused or redesigned rather than scaled.
- Probe DA2 moved history onto persistent directed edge memory. The initial
  smoke rejected local/no-relation fakeouts and relation-without-memory
  fakeouts, but failed because commutative edge memory ranked best and
  asymmetry was not required. One documented two-edge-support revision also
  failed. Do not scale the current DAR edge-memory generator.
- Probe DAX-R connected the primitive branch to coarse-graining admissibility
  for `I_T^C(s) = H(F_T(s) / C)`, then tested a branching connection graph as a
  constructed relation substrate. It did not establish substrate validity:
  local-memory fakeouts were not rejected, loop closure was trivial, and lineage
  cap hits were frequent.
- Probe DAX-G0 stopped hand-designing worlds and exhaustively audited all 256
  elementary cellular automata as the smallest DAR-capable local rule space. It
  found nontrivial persistence enriched among DAR-complete and DAR-asymmetric
  rules, motivating a G1 motif-anatomy probe.
- Probe DAX-G1 anatomized the G0 candidates and confirmed four robust
  emitter-like persistence motifs across horizons, ring sizes, and light
  perturbations. It also narrowed the primitive claim: relation-dependence
  remains enriched after filtering, but DAR-complete/DAR-asymmetric enrichment
  does not survive the stricter anatomy filter, and the motif-composition
  sidecar is negative.
- Probe DAX-G2 ran a budgeted minimal-expansion smoke over q=3/r=1 and q=2/r=2
  sampled cellular automata. Expanded spaces produced stronger missing-invariant
  hints than ECA anchors, especially q=3/r=1, but symmetric/self-control strata
  leaked into persistence classes. This blocks interpretation and makes the next
  task a metric guardrail revision rather than a full phase-map scale-up.
- Probe DAX-G2b applied matched controls to the G2 positives. It resolved the
  q=3/r=1 control leaks and left one clean q=3/r=1 control-adjusted positive
  with relation/asymmetry load-bearing and non-emission composition signal:
  `q3r1_s1_0002`. It also demoted `q3r1_s5_0016` to emission-only despite strong
  relation/asymmetry load-bearing.
- Probe DAX-G3 reproduced the q=3/r=1 branch under active guardrails. It found
  9 control-adjusted positives and no remaining S7/S8 control leaks. This is a
  pass but not a strong pass: composition-positive readouts exist, but they are
  not yet cleanly unified with the strongest persistence/load-bearing rows.
- Probe DAX-G4 anatomized the full G3 Stage 2 q=3/r=1 candidate set. It found
  11 descriptive motif families, 3 all-core invariant overlaps, and a clear
  composition gap: new-motif outcomes can persist, but composition does not
  overlap the strongest persistence band. This supports a detector freeze for
  persistence/relation/asymmetry while keeping composition secondary.
- Controls behave differently:
  - `boundary_v2` is pseudo-risk/propagation-negative;
  - `joint_basin` can show local transport but usually fails multi-step
    propagation.

What we cannot say:

- That this proves the theory.
- That the object exists outside the toy substrate.
- That COM is the final or canonical kappa.
- That the toy simulator matches the unpublished older simulator exactly.

## Known Risks

- Toy substrate dependence.
- Kappa design may be hand-aligned to the object; Probe 11 reduces but does not
  eliminate this concern because simple learned quotients underperform COM.
- Component preservation is currently entropy-ratio based and should be
  formalized more rigorously.
- Product baseline is an approximation built from independent component
  profiles.
- CuPy GPU execution works after prepending Torch's bundled CUDA 13 NVRTC DLL
  directory to `PATH` and setting `CUPY_CACHE_DIR=.cupy-cache`. This is encoded
  in `omega_env.bat` and `omega_env.ps1`.
- Some result directories contain compact tracked summaries, while large raw
  per-seed/intermediate files are intentionally ignored.
- Existing code is research-code quality, not library quality.
- Probe T1 staged local trajectory samples under `_trajectory_samples/`; those
  are intentionally untracked because they are large generated intermediates.

## Recommended Next Probes

### Primitive Branch: DAR Pause Or Redesign

Question:

> Can the distinction/asymmetry/relation world be redesigned so relation and
> non-commutative history are jointly load-bearing, rather than producing
> history fakeouts or no-relation non-commutative signal?

Do not scale DA1/DA1b/DA1c until this is resolved. A reasonable alternative is
to return to formalizing the stronger COM/fiber witness instead of continuing
to tune the DAR toy generator.

DA2 tested one stronger edge-memory redesign and one documented revision. Those
results narrow the issue: local history can now be rejected, but the generator
still cannot make non-commutative relational asymmetry necessary. Further DAR
work should be treated as a new design problem, not as scale-up of the current
world family.

DAX-R is the first explicit connection-admissibility framing. It should be read
as a negative substrate-validity smoke, not an Omega validation. Passing a later
DAX-style probe would mean only that a constructed connection substrate is valid
enough for viable-slack tests; it would not show spontaneous emergence of
connection-like relation.

DAX-G0 is the first positive result in the primitive branch since the DA0-DA2
failures. It is still modest: it shows that nontrivial persistence exists in a
minimal exhaustible DAR-capable rule space and is enriched in the expected
primitive classes.

DAX-G1 confirms that some of those motifs are robust individual structures, but
it weakens the primitive-enrichment claim after stricter anatomy filtering. The
correct next step is a DAX-G2 phase map across minimal rule spaces, with the
explicit goal of testing whether relation/asymmetry load-bearing and
composition reappear under richer but still principled conditions.

DAX-G2 smoke found promising q=3/r=1 and q=2/r=2 hits, including nonzero
composition readouts, but failed the control-rejection guardrail. The next
primitive-branch step is not a larger run. It is a G2 metric guardrail revision
that separates persistence from control-adjusted load-bearing persistence.

DAX-G2b performed that revision and passed the guardrail. The next step is a
focused q=3/r=1 guardrailed phase map, not a broad expansion to richer rule
spaces. Composition should remain separately tracked because only one q=3/r=1
candidate currently has a non-emission adjusted composition signal.

DAX-G3 ran that focused q=3/r=1 map and reproduced the trunk. The correct next
primitive-branch step is DAX-G4 motif ecology/mechanism anatomy inside q=3/r=1.
Do not broaden rule space until the mechanism and composition overlap are
understood.

DAX-G4 completed that anatomy pass. It found coherent descriptive families and
nonempty invariant overlap, but composition remains sparse relative to the
strongest persistence/load-bearing candidates. The next primitive-branch step is
therefore DAX-G5: freeze the q=3/r=1 detector for persistence/relation/asymmetry
and use held-out prediction or prospective sampling to test whether the fertile
bands predict new validation positives. Composition should remain a tracked
secondary readout until it earns a primary criterion.

### Probe 13: Formal COM Fiber Transport Object

Goal: turn the current empirical object into a precise mathematical definition.

Tasks:

- define macro segment node;
- define viable fiber;
- define certified node/edge;
- define component projection preservation;
- define viable propagation index and its limits;
- prove which choices are estimator conventions versus object definitions.

### Probe 14: Revised Learned Kappa Recovery

Question:

> Can a learned or constrained kappa rediscover COM-like propagation without
> being handed center_of_mass, after the COM fiber object is formalized?

Controls:

- random kappas;
- high-cardinality identity-like kappas;
- basin-only kappas;
- compression-regularized learned kappas.

### Probe 15: Substrate Generalization

Question:

> Does COM-like viable propagation survive a different toy substrate, or is it
> local to the current dynamics?

Do not broaden until the COM fiber object is formalized.

## Maintenance Rule

Every new substantial probe must update:

- `docs/OMEGA_RUNNING_LOG.md`
- this manual if concepts or conclusions change
- `README.md` only when usage/setup changes

When adding results to Git:

- commit scripts and compact summaries;
- do not commit virtual environments, caches, smoke runs, or massive raw graph
  dumps;
- check `git diff --cached --name-only` and staged file sizes before commit.
