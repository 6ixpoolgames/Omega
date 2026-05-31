# Omega / Reachable Futures Lab

This repository is the empirical workspace for the **Omega** theory project.

The current empirical arm studies **reachable futures**: how neutral transition substrates shape, constrain, concentrate, transform, or collapse possible futures under relation, asymmetry, horizon, and matched-control structure.

The long-term Omega ambition is broader: a structural account of value-bearing futures and alignment-relevant failure modes that does not begin from reward functions, utility functions, fixed preference aggregation, or moral rules. The executable work in this repo is narrower and earlier-stage: building minimal substrates where fragments of that idea can become mathematically testable.

This repo contains theory notes, foundational drafts, historical validation attempts, current substrate-design notes, executable probes, result logs, and control/audit specifications.

It does **not** prove Omega. It is a controlled workspace for turning the theory into testable mathematical objects, identifying substrate artifacts, and letting weak formulations fail.

## One-sentence summary

**We study reachable futures: how neutral relation systems shape which futures remain reachable, excluded, concentrated, transformed, control-equivalent, or measurement-limited.**

The active empirical question is currently narrower than agency, identity, or value detection:

**Can neutral transition systems produce measurable future-landscape deformation that separates from matched nulls without importing semantic labels such as agent, valuer, identity, or good?**

Current status, in one line:

**VAL0/VAL1 were useful reconnaissance probes; RFS-MB0 has reoriented from endpoint support/distribution deformation and static coflow spectra toward directional horizon-transport instrumentation. The H128 horizon-transport response-surface scaleup passed matched-marginal instrument gates and surfaced a stable-to-amplified-aligned response surface. The transition-energy characterization turned that into a substrate-response atlas, and the newest asymmetry-ladder run compares locality, directional asymmetry, preservation asymmetry, and combined asymmetry directly. The first seed-scaled ladder batch reached `preservation_asymmetry_loadbearing`: locality-only stayed a baseline, directional/combined asymmetry produced rerouting without aligned amplification, and preservation asymmetry carried aligned response. This is still not a scientific validation gate, candidate promotion, or Omega/agency/value claim.**

## Current empirical branch: horizon transport

The live empirical object is now:

```text
matched-marginal-separated horizon transport
with horizon-dependent aligned amplification under nonlethal perturbation
```

Horizon transport asks what earlier future structures become at later horizons:

```text
T_{H_a -> H_b}
```

This is a directional object, measured with transport matrices and SVD, not a static co-occurrence object. It is closer to the theory's central concern with continuability across horizon than earlier endpoint or static coflow/cofrontier probes.

The H128 response-surface scaleup reported:

```text
jobs_completed: 11520 / 11520
errors: 0
matrix_count: 660
null_replicates: 15
matched_marginal_detector_null_separation: passed
synthetic_fixture_contract: 8 / 8
terminal_saturation_flagged_rows: 0 / 660
```

Empirical response classes in the full run:

```text
transport_stable: 235
transport_amplified_aligned: 381
```

The important horizon pattern:

```text
short horizons:
  stable

middle/deep horizons:
  amplified-aligned

higher perturbation strength:
  first amplified-aligned horizon shifts earlier

extended horizons through H=128:
  interpretable in this run, with no terminal saturation flags
```

## Transition-energy substrate atlas

The current substrate program now treats substrate-law differences as signal, not noise.

The clean terminology is:

```text
locality-only:
  baseline local branching

smooth directional field:
  directional asymmetry field A(s), using A(t)-A(s)

macro-invariant / asymmetry-preservation:
  coarse invariant I(s), using |I(t)-I(s)|

constraint-template substrate:
  historical comparator using hand-built symbolic constraint templates
```

Do not describe the macro-invariant family as a budget family. The concept is **asymmetry preservation**: some coarse distinction is costly to erase, so transport can remain coherent without hand-picked symbolic laws.

The transition-energy substrate atlas currently reads:

```text
locality-only:
  clean baseline; no aligned amplification in the tested grid

smooth directional field:
  response-bearing; rerouting/reopening/weakening appear, but no aligned amplification in the tested grid

macro-invariant / asymmetry-preservation:
  aligned response appears; total-coordinate-mass strongest but coverage-limited

constraint-template comparator:
  still positive; no longer unique
```

This is a substrate-characterization result, not validation.

The first implemented asymmetry-ladder batch currently reads:

```text
locality-only:
  clean baseline in the seed-scaled batch

directional asymmetry:
  rerouting/differentiated response, no aligned amplification

preservation asymmetry:
  current loadbearing family; aligned response under matched controls

combined asymmetry:
  clean and rerouting-bearing, but not yet synergistic in the sparse tested grid
```

## Minimal transition-energy ladder

The transition-energy substrate program maps directly onto the primitives:

```text
distinction:
  finite states differ

relation:
  selected transitions connect states

asymmetry:
  transition energy / selection makes transformations non-equivalent
```

The minimal ladder is:

```text
E0 locality only:
  E(s,t) = d(s,t) + roughness

E1 directional asymmetry:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + roughness

E2 preservation asymmetry:
  E(s,t) = d(s,t) + beta * |I(t)-I(s)| + roughness

E3 combined:
  E(s,t) = d(s,t) + alpha * (A(t)-A(s)) + beta * |I(t)-I(s)| + roughness
```

`A(s)` is a directional asymmetry field. `I(s)` is a macro-invariant / coarse asymmetry coordinate. Neither is value, utility, reward, fitness, or Omega.

## What current results do and do not mean

Current results mean:

```text
horizon transport is the current live instrument;
matched marginal nulls did not explain away the H128 response surface;
perturbation changed future transport geometry without simply destroying it;
horizon depth appears loadbearing in the response profile;
transition-energy substrate laws express different response regimes.
```

Current results do **not** mean:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
candidate promoted;
holdout ready;
graph-channel causality shown;
value-bearing structure demonstrated.
```

## Control philosophy: detector nulls versus perturbations

A key reorientation in the project is the separation between detector-null controls and perturbation-response profiles.

```text
Null controls test the detector.
Perturbations test the candidate response profile.
Destructive ablation maps viability boundaries; it is not ordinary negative evidence.
```

For the current branch:

```text
detector-null controls:
  context/horizon shuffles
  row marginal matched transport nulls
  column marginal matched transport nulls
  row-column marginal matched transport nulls
  marginal residual fraction
  synthetic marginal fakeout fixtures

perturbation-response probes:
  small edge resampling
  asymmetric edge flipping
  graded nonlethal strength ladders
  response class by horizon pair
```

This distinction is loadbearing. Living or life-like systems do not survive arbitrary destructive ablation. Perturbation should be interpreted as a response profile: stable, amplified, weakened, rerouted, reopened, collapsed, or control-equivalent.

## Workflow: human-directed, AI-assisted research

This repository is developed through a human-directed, AI-assisted research workflow.

The core theoretical motivation, project judgment, branch selection, interpretive standards, and many key pivots are human-generated. AI systems are used as implementation and critique accelerators: they draft specs, modify runners, generate reports, audit code, summarize results, and propose follow-up experiments.

This distinction matters. The workflow is semi-autonomous in the sense that AI coding agents can carry out bounded implementation tasks and produce structured artifacts, but the scientific direction is not autonomous. Human review decides which failures matter, which claims are allowed, when a result is overinterpreted, and when a branch should be repaired, paused, or redirected.

## Why this matters for alignment

Omega is motivated by a central alignment problem:

> A system can become highly capable, persistent, and effective while degrading the broader conditions under which value-bearing futures remain possible.

This is the failure mode the internal notes call **pseudo-Omega**. In public-facing terms, it is a **locally viable / globally degrading capture regime** or **destructive lock-in**: local success that collapses broader future possibility.

Omega tries to formalize this failure mode without starting from a fixed reward function or a direct aggregation of human preferences.

The current empirical program is still only a first step. It does not validate alignment. It asks what substrate and measurement discipline are needed before the earliest precursor can be resolved:

> Can future-landscape deformation be measured well enough to distinguish nontrivial future-structuring effects from saturation, trivial persistence, clocks, collapse, probe artifacts, generic finite-frontier dynamics, and matched-control equivalence?

## Important current docs

### Start here

- [Horizon Transport and Aligned Amplification](docs/research_notes/omega_theory/horizon_transport_aligned_amplification.md)
- [Transition Energy and Constraint Untethering](docs/research_notes/omega_theory/transition_energy_and_constraint_untethering.md)
- [Transition-Energy Substrate Atlas](docs/research_notes/omega_theory/transition_energy_substrate_atlas.md)
- [Asymmetry-ladder transition-energy result](docs/research_notes/validation_results/rfs_mb0_asymmetry_ladder_transition_energy_result.md)
- [Asymmetry-ladder transition-energy spec](docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md)
- [Macro-invariant due-diligence result](docs/research_notes/validation_results/rfs_mb0_macro_invariant_due_diligence_result.md)
- [Transition-energy substrate characterization result](docs/research_notes/validation_results/rfs_mb0_transition_energy_substrate_characterization_result.md)
- [Transition-energy substrate characterization spec](docs/RFS_MB0_TRANSITION_ENERGY_SUBSTRATE_CHARACTERIZATION_RUN_SPEC.md)
- [Substrate-untethering transition-energy larger smoke result](docs/research_notes/validation_results/rfs_mb0_substrate_untethering_transition_energy_sweep_result.md)
- [Substrate-untethering transition-energy sweep spec](docs/RFS_MB0_SUBSTRATE_UNTETHERING_TRANSITION_ENERGY_SWEEP_SPEC.md)
- [Horizon-transport response-surface H128 scaleup result](docs/research_notes/validation_results/rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md)
- [Horizon-transport response-surface H128 scaleup spec](docs/RFS_MB0_HORIZON_TRANSPORT_RESPONSE_SURFACE_H128_SCALEUP_SPEC.md)

### Theory foundations

- [Minimal reachable futures formalism](docs/research_notes/omega_theory/minimal_reachable_futures_formalism.md)
- [Boundary non-privileging and field-deformation theory note](docs/research_notes/omega_theory/boundary_nonprivileging_and_field_deformation.md)
- [Reachable Futures Substrate Program](docs/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)
- [Branch evolution update note](docs/RFS_MB0_BRANCH_EVOLUTION_UPDATE_NOTE.md)
- [Omega glossary](docs/research_notes/omega_theory/omega_glossary.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)

## Current next step

The current next step is **not** holdout, graph perturbation, direct channel diagnostics, or candidate promotion.

The current next step is to continue the transition-energy substrate program using the cleaned terminology:

```text
near-term options:
  expand preservation-asymmetry variants and seed/start diversity;
  optionally repair total-coordinate-mass paired-baseline availability;
  move toward a max-entropy local transition ensemble with explicit macro-invariant constraints;
  keep grammar-neutral probes such as relation_role and full_state_hash;
  preserve matched-marginal detector gates and response-profile taxonomy;
  compare response surfaces across substrate families and scales;
  only later consider direct channel diagnostics if response profiles suggest localized functional dependence.

still blocked:
  holdout scoring;
  n=6 transfer;
  alphabet expansion as promotion;
  graph-channel causal claims;
  agent/value/Omega labels.
```

## Roadmap

```text
VAL0/VAL1:
  historical reconnaissance; useful but not the active empirical frame

RFS0:
  exact finite reachability measurement-floor smoke; insufficient control separation

RFS-MB0:
  active neutral future-landscape deformation program;
  endpoint support/distribution and quotient probes became measurement-limited;
  frontier-transform instrumentation matured into horizon-transport instrumentation;
  current live object is matched-marginal-separated horizon transport with aligned amplification;
  current substrate program uses transition-energy families rather than hand-built symbolic laws

RFS-MB1:
  only after MB0 control separation and response-profile taxonomy mature;
  perturbation and recovery of future-profile structure

RFS-MB2:
  coupled future landscapes; compatibility, capture, erasure

RFS-MB3:
  scale hierarchy; nested or composable bounded structures

RFS-MB4:
  constructor-like transformation capacity of bounded processes, if the earlier substrate and measurement layers mature enough to justify revisiting it
```

Later stages should not be implemented until RFS-MB0 has clean definitions, controls, and failure modes.

## Important caveat

This repository does not prove Omega as a scientific theory.

The current scientific claim is modest:

> Directional horizon-transport instrumentation can measure a matched-marginal-separated response surface in neutral toy substrates. Transition-energy substrate characterization shows that different generic substrate laws express different response regimes. Omega-compatible subobjects have not been demonstrated.

VAL0/VAL1 tested earlier precursors. The project is now centered on neutral future landscapes, horizon-transport instrumentation, transition-energy substrate design, and control-relative deformation taxonomy.
