# Omega Project Manual

Last updated: 2026-05-11

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

## Recommended Next Probes

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
