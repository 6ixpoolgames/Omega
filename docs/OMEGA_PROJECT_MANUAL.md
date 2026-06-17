# Omega Project Manual

Last updated: 2026-06-18

Repository: https://github.com/6ixpoolgames/Omega

## Purpose

This repository is the local validation workspace for the Omega theory project.
Its purpose is not to prove the theory by simulation. Its purpose is to extract
candidate mathematical objects, make them operational, test them against nulls,
and force clear failure modes.

## Documentation Roles

The top-level documentation now has separated jobs:

```text
README.md:
  public pitch and current state

docs/OMEGA_FORMALISM_PRIMER.md:
  readable bridge to the current formal stack

docs/EXTERNAL_READER_GUIDE.md:
  longer collaborator onboarding guide

docs/OMEGA_PROJECT_MANUAL.md:
  operations, local commands, run workflow, retention, repo process

docs/PUBLIC_RESULTS_INDEX.md:
  empirical result index

docs/OMEGA_RUNNING_LOG.md:
  chronological project log
```

Do not make this manual the canonical public pitch. Keep public-facing summary
language in `README.md` and formal onboarding in `docs/OMEGA_FORMALISM_PRIMER.md`.

## Current Workflow Snapshot

Last workflow refresh: 2026-06-18

Active project posture:

```text
Current contribution:
  Layer A is a continuation-map integrity discipline.

Active formal stack:
  AlphaCore primitive floor;
  consequence/profile/sound-presentation guardrails;
  non-factorization and exact recovery compression;
  viability/reachability;
  recurrent support carrying, loss, restoration, transfer, lineage,
  successor handoff, perturbation budget, joint carrying failures;
  finite relational adapter pilot.

Active adapter path:
  source artifact
  -> deterministic source compiler
  -> finite relational IR
  -> generic audits
  -> retained provenance and digests.

Current adapter compiler:
  derived graph source
  -> finite relational IR.

Current non-claims:
  no Omega validation;
  no value, agency, valuerhood, or identity theorem;
  no substrate-general empirical transfer;
  no frontier-model alignment claim.
```

Current front-door notes:

- `README.md`
- `docs/OMEGA_FORMALISM_PRIMER.md`
- `docs/EXTERNAL_READER_GUIDE.md`
- `docs/research_notes/omega_theory/layer_a_theorem_spine_v0.md`
- `docs/research_notes/omega_theory/layer_a_derivation_audit_v0.md`
- `docs/research_notes/omega_theory/standard_core_compression_v0.md`
- `docs/research_notes/omega_theory/finite_relational_adapter_design_v0.md`
- `docs/research_notes/omega_theory/finite_relational_adapter_checkpoint_v0.md`
- `docs/research_notes/omega_theory/adapter_provenance_v0.md`
- `docs/research_notes/omega_theory/README.md`

Legacy Future Field Atlas checkpoint:

The following checkpoint records the historical empirical line. It is retained
for provenance and rerun instructions only. It is not the current active
workflow unless the user explicitly resumes Future Field Atlas work.

```text
Formal arm:
  AlphaCore is now the standalone primitive floor over relation, distinction,
  and asymmetry. AlphaOmega is the active umbrella stack. OmegaCore remains the
  older Lean-backed support/recoverability and presentation namespace during
  the facade migration. Current checked presentations include Boolean relation
  support, finite channel / partition recovery, and probabilistic channel
  recovery with finite cascade error bounds.

Empirical arm:
  Future Field Atlas is the current reachable-future microscope. The stochastic
  distinction-channel probe is the clean finite channel bridge for formal
  consumption. Historical RFS/VAL/DAX branches are provenance, not the public
  front door.
```

Legacy Future Field Atlas public posture:

This block is historical. Do not use it as the current public pitch. It records
the last Future Field Atlas stance before the current Layer A / adapter
consolidation.

```text
Lead with reachable futures and neutral future-landscape deformation.
Use Omega as the broader theory and long-term hypothesis.
Do not present VAL0/VAL1 as validation of Omega.
Frame VAL0/VAL1 as reconnaissance probes that exposed viability dynamics and
substrate limitations.
Present RFS-MB0 horizon-transport instrumentation and transition-energy
substrate untethering as the empirical lineage, and state clearly that it has
not passed the scientific gate.
The current active implementation branch is the Future Field Atlas clean
rebuild: raw reachable-frontier topology first, response labels last. After the
schema teardown, condition identity is operator-native: state-space specs,
transition-law specs, selection-operator specs, observable specs, and
frontier-scan specs. Historical treatment names are documented only in the
Future Field Atlas glossary. The formal adapter conformance package now compiles
the retained formal-interface panel into primitive-calculus-facing contexts,
unfoldings, distinction fibers, distinction preorders, transport witnesses,
closed transports, law checks, non-erasure tables, and theorem-transfer status.
Its current status is `generated_presentation_conformance`; strict raw
conformance is not claimed. The follow-up raw/closed gap report confirms that
root-law theorem transfer depends on generated closure, while the passing
finite non-erasure rows are not inflated by closure-only recoveries. Keep
`raw_observed` and closure-derived support kinds separate in future reports.
The stochastic distinction-channel probe is the current clean channel
presentation bridge. It separates support-level exact recovery from
probabilistic decoder recovery under declared finite distinctions, priors,
decoders, and thresholds. Treat it as prebiotic channel formalization only, not
as Omega validation or semantic detection.
The instrument is calibrated against the latest
hard-top-m mechanism result as a fixture, which points toward a fixed low-rank
successor boundary: rank-prefix `m=3`,
rank-subset `m=4` retaining ranks `1;2;3`, and rank-subset `m=5` retaining
ranks `1;2;3` were response-bearing.
Generic lower out-degree is less plausible because random deletion at matched
effective degree stayed stable.
The current H32 atlas smoke now emits formal spec manifests,
condition-identity manifests, artifact-completeness summaries, and
reconstruction audits, so derived topology summaries are treated as
reconstructible measurements rather than unsupported report labels.
The current compact output path also emits `scan_manifest.csv` so high-volume
raw node/edge rows do not repeat full formal metadata on every row.
Primary Future Field Atlas CSV artifacts now write as `.csv.gz` by default.
This preserves logical CSV schemas while cutting compact H32 storage from about
59.7 MB to about 3.1 MB. Use `--csv-output-mode plain` only for local debugging
or `--csv-output-mode both` when a plain CSV compatibility copy is explicitly
needed.
Raw topology artifacts now default to sharded physical output:
`frontier_nodes_by_horizon_shards/part-*.csv.gz` and
`frontier_edges_by_step_shards/part-*.csv.gz`, with shard manifests preserving
row counts and physical file identities.
The coupled atlas runner now follows the same posture for high-volume joint
topology: `coupled_joint_frontier_nodes_by_horizon_shards/part-*.csv.gz` and
`coupled_joint_frontier_edges_by_step_shards/part-*.csv.gz` are the default
physical layout, with shard manifests preserving logical artifact identity.
The medium H128 calibration pass completed cleanly with 128 / 128 scans,
complete artifacts, and passing reconstruction audits. It also showed that the
next scaling bottleneck is post-scan finalization: worker scans finished in
about 19 seconds, while artifact construction and writing dominated the
29.4-minute wall time.
The coupled sharded staged sweep completed bounded H64 pair2 cleanly with no
caps, complete topology-derived artifacts, all reconstruction audits passing,
and about 361.7 MB compressed output. The next coupled scaling repair should be
more careful than a simple steady-state compressor: the exact repeated-block
audit found that counts stabilize but raw state/edge identities do not repeat.
Keep sharded output as the coupled default. If storage becomes limiting, prefer
dictionary/factorized topology or exact delta topology with reconstruction
tests before many-pair H64/H128 runs. A subsequent broad H64 pair8 sweep
completed cleanly with no caps, all reconstruction audits passing, and about
1.21 GiB of compressed output, but confirmed severe heavy-pair skew and
write-out dominance. The H128 coupled pair2 serial depth gate completed cleanly
with about 0.746 GiB of compressed output and no caps, while a H128 pair4
parallel attempt failed on two heavy pairs through a Windows multiprocessing
result-transfer limit. The first repair is now implemented as
`--raw-topology-output-mode worker_spool`, which writes pair-local raw topology
inside worker processes and lets the parent merge compact manifests. Use
`worker_spool` for coupled H128 breadth attempts. Before deleting worker-spooled
raw topology, run `python -m omega.future_field_atlas.retention_summary --run
<run_dir>` and keep the `_retention_summary/` bundle. If the deletion plan says
`delete_raw_spools_allowed`, `--delete-raw-spools` may remove only
`coupled_pair_spool/` while leaving compact manifests, profiles, residuals,
marginal summaries, audits, readiness rows, and rebuild metadata. A short
three-frontier H6 smoke now exists as a profile-only interface probe; it does
not emit raw triadic topology and should not be treated as a coupled science
result. The first constrained coupled H64 ladder completed cleanly across
coupling strengths `0.00`, `0.05`, `0.10`, `0.25`, and `0.50`. The live
instrument read is threshold-like rather than smoothly graded: zero penalty
differs from positive penalty, while the tested positive strengths are
numerically identical in topology-derived summaries after sorting rows and
ignoring operator identity fields. Positive penalty preserved component
marginal reachability in that run, but one heavy pair became much more
joint-restrictive at the final horizon, so future coupled analysis must remain
pair-aware. The follow-up H64 mechanism-resolution pass showed that this read
was too coarse: near-zero strengths `0.001` through `0.010` are distinguishable,
while `0.020` and `0.050` saturate to the same compact topology digest in the
tested design. The true product selector is distinct from zero-penalty joint
rank-prefix selection, so product-selector runs are the neutral reference for
future coupled comparisons. Pair005 remains a heavy-pair / critical-pair clue
and persisted in a targeted H128 depth check.
The substrate morphology atlas now postprocesses retained coupled outputs
directly. After the rank-order-boundary class expansion it ingests 37 coupled
run directories, all clean-gated. The rank-order-boundary branch is no longer
pair005-only: H64 searches found pair012, pair014, and pair026 as high-residual
marginal-preserving exemplars, and targeted H128 confirmed all three. Pair012 is
currently the strongest retained exemplar. The
shared-capacity v1 H64 smoke completed cleanly with no caps, complete artifacts,
and passing reconstruction audits, but it should not be scaled as-is: it prunes
A/B marginal support and then becomes product-dense over the surviving
marginals. The two tested alternate observables,
`hamming_weight_or_nonzero_count` and `total_coordinate_mass`, did not reproduce
the high-yield rank-order signature, so the current class remains
`symbol_histogram_distance`-specific. The next coupled branch should be a
rank-order-boundary representative-control panel with pair005, pair012,
pair014, pair026, low/medium controls, and retained product, zero-penalty joint
rank-prefix, scalar `0.020`, and shared-capacity v1 controls.
```

Terminology rule:

```text
Use "macro-invariant" in public-facing prose.
Use "asymmetry-constrained transition energy" in theory-facing prose.
Use "preservation asymmetry" for the explicit asymmetry-ladder E2 substrate.
Treat "budget_conservation", "budget_kind", "budget_weight", and
"budget_delta" as retained raw implementation/output names only.
```

Legacy Future Field Atlas design/provenance notes:

- `docs/specs/current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`
- `docs/specs/current/FUTURE_FIELD_ATLAS_SUBSTRATE_MORPHOLOGY_SWEEP_SPEC.md`
- `docs/specs/current/FUTURE_FIELD_ATLAS_SHARED_CAPACITY_SMOKE_SPEC.md`
- `docs/FUTURE_FIELD_ATLAS_GLOSSARY.md`
- `docs/implementation/FUTURE_FIELD_ATLAS_CHANGELOG.md`
- `docs/implementation/RUN_RETENTION_POLICY.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_phase0_1_smoke_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_compact_manageability_h64_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_visualization_note.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_neighbor_observable_sweep_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_medium_sweep_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_h64_smoke_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_shared_capacity_h64_smoke_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_default_gzip_compression_smoke.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_h128_calibration_pass_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_writeout_path_repair_note.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_transport_mode_timing_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_probe_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_hardening_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_sharded_staged_sweep_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_lossless_block_audit_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_broad_sweep_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h128_and_triadic_profile_smoke_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_worker_spool_scale_validation_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_ladder_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_coupled_h64_mechanism_resolution_result.md`
- `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_substrate_morphology_atlas_result.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_TOP_M_MECHANISM_AUDIT_SPEC.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_top_m_mechanism_audit_result.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_TOP_M_GEOMETRY_AUDIT_SPEC.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_top_m_geometry_audit_result.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_MAX_ENTROPY_LOCAL_TRANSITION_PREFLIGHT_SPEC.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_max_entropy_local_transition_phase1_preflight_result.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_asymmetry_ladder_transition_energy_result.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_asymmetry_ladder_preservation_scaleup_result.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_low_beta_preservation_sensitivity_scaleup_result.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_TRANSITION_ENERGY_SUBSTRATE_CHARACTERIZATION_RUN_SPEC.md`
- `docs/research_notes/omega_theory/transition_energy_substrate_atlas.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_macro_invariant_due_diligence_result.md`
- `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_option_a_budget_coverage_small_result.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_SUBSTRATE_UNTETHERING_TRANSITION_ENERGY_SWEEP_SPEC.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_HORIZON_TRANSPORT_RESPONSE_SURFACE_H128_SCALEUP_SPEC.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_PATTERN_SPEC.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_DETECTOR_V1_HANDOFF.md`
- `docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_LONG_HORIZON_ENVIRONMENT_AUDIT.md`
- `docs/specs/archive/rfs_mb0/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md`

## Spec Inbox

This section is mostly for Future Field Atlas or other empirical run specs.
For current Layer A / finite relational adapter work, start from the source
files, tests, and design notes named in the current workflow snapshot above.

Always check this folder first for new run specs:

```text
docs/specs/current/
```

This is the active spec inbox. When the user says a new spec is "in the repo",
"live", "uploaded", or "next up", look in `docs/specs/current/` before
searching the rest of the repository.

Do not infer that a spec in this inbox is part of the current default workflow.
It is active only when the user explicitly resumes that run line or asks for the
spec.

Naming convention:

```text
docs/specs/current/FUTURE_FIELD_ATLAS_<SHORT_NAME>_SPEC.md
```

Examples:

```text
docs/specs/current/FUTURE_FIELD_ATLAS_COUPLED_SHARED_CAPACITY_SMOKE_SPEC.md
docs/specs/current/FUTURE_FIELD_ATLAS_PAIR005_THRESHOLD_BRACKET_SPEC.md
```

Lifecycle:

```text
1. User or assistant adds active/new specs to docs/specs/current/.
2. Assistant reads docs/specs/current/ first when starting a new run.
3. After completion, write retained result notes under
   docs/research_notes/validation_results/future_field_atlas/.
4. When a spec is superseded, move it to docs/specs/archive/<branch>/ and
   update public-facing indexes if it remains important.
```

Do not add new run specs to the repo root, `docs/` root, or the flat
`validation_results/` root.

Project stance:

- scientific and skeptical;
- minimal before broad;
- propagation/viability before entropy;
- controls and nulls before interpretation;
- toy-substrate evidence must not be overstated as theory validation.

Onboarding terminology:

> Omega is best introduced as a structural theory of value-bearing futures.

For the empirical repo, the front-door object is:

```text
neutral future-landscape profiles under matched-null comparison
```

The current empirical question is:

```text
Can raw horizon-indexed reachable-frontier topology distinguish structured
future-field deformation, rank-boundary anatomy, transport flow, and
matched-control artifacts before any semantic or response label is applied?
```

This keeps the philosophical connection to formal value theory and axiology,
while also being legible to alignment readers as a claim about
future-preserving reachability, recoverability, and compatibility under
constraint.

Use `docs/research_notes/omega_theory/public_terms_and_translations.md` when
writing public summaries. Use `docs/research_notes/omega_theory/omega_glossary.md`
as the canonical internal definition anchor.

## How A New Codex Instance Should Start

Current default startup:

1. Read this file through the current workflow snapshot and adapter workflow.
2. Read `README.md`.
3. Read `docs/OMEGA_FORMALISM_PRIMER.md`.
4. Read `docs/EXTERNAL_READER_GUIDE.md` if external-facing framing matters.
5. Read the current Layer A / adapter anchors:
   - `docs/research_notes/omega_theory/layer_a_theorem_spine_v0.md`
   - `docs/research_notes/omega_theory/layer_a_derivation_audit_v0.md`
   - `docs/research_notes/omega_theory/standard_core_compression_v0.md`
   - `docs/research_notes/omega_theory/finite_relational_adapter_design_v0.md`
   - `docs/research_notes/omega_theory/adapter_provenance_v0.md`
   - `docs/research_notes/omega_theory/README.md`
6. Check the working tree:
   - `git status --short`
7. For current adapter work, run the focused adapter validation command listed
   in the finite relational adapter workflow section.
8. Use `docs/specs/current/` only when the user explicitly resumes a spec-driven
   empirical run.

Legacy startup checklist:

The older checklist below is retained for provenance and for deliberate Future
Field Atlas / historical-probe resumption. It is not the default startup path
for current Layer A or finite relational adapter work.

1. Read this file.
2. Read `README.md`.
3. Read `docs/OMEGA_FORMALISM_PRIMER.md`.
4. Read `docs/specs/README.md` and check `docs/specs/current/` for live specs.
5. Read the current status anchors:
   - `formal/lean/README.md`
   - `docs/research_notes/omega_theory/README.md`
   - `docs/research_notes/omega_theory/alpha_primitive_core_v0.md`
   - `docs/research_notes/omega_theory/alpha_omega_unification_map_v0.md`
   - `docs/research_notes/omega_theory/omega_primitive_calculus_v0_lean_root_skeleton.md`
   - `docs/research_notes/omega_theory/probabilistic_channel_presentation_v0.md`
   - `docs/PUBLIC_RESULTS_INDEX.md`
6. Skim `docs/OMEGA_RUNNING_LOG.md` for the latest chronological changes.
7. Use the historical validation-design notes below only when provenance is
   needed:
   - `docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_PATTERN_SPEC.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_DETECTOR_V1_HANDOFF.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_V1_1_CODE_TARGETS.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_future_landscape_detector_v1_1_smoke_result.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_future_landscape_long_horizon_environment_audit_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_ACTION_GENERATED_RELATION_SUBSTRATE_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_action_generated_relation_atlas_v0_calibration_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_RELATION_ATLAS_5H_BATCH_RUN_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_relation_atlas_5h_batch_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_RELATION_ATLAS_BATCH_RUNNER_REPAIR_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_relation_atlas_repaired_batch_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_EXPLORATORY_ITERATION_PASS_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_exploratory_iteration_pass_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_SPECTRAL_FUTURE_FIELD_GEOMETRY_SMOKE_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_SPECTRAL_CHANNEL_EDGE_SMOKE_REPAIR_PREP_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_spectral_channel_high_loading_repair_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_STAGE_B2_LAPTOP_SPECTRAL_CONTROL_MAPPING_SMOKE_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_laptop_spectral_control_mapping_smoke_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_HORIZON_TRANSPORT_MATCHED_NULL_AND_FIXTURE_SMOKE_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_matched_null_fixture_smoke_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_HORIZON_TRANSPORT_EXPANSION_SMOKE_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_expansion_smoke_result.md`
   - `docs/research_notes/omega_theory/horizon_transport_aligned_amplification.md`
   - `docs/research_notes/omega_theory/transition_energy_and_constraint_untethering.md`
   - `docs/research_notes/omega_theory/transition_energy_substrate_atlas.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_TRANSITION_ENERGY_SUBSTRATE_CHARACTERIZATION_RUN_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_transition_energy_substrate_characterization_result.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_macro_invariant_due_diligence_result.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_option_a_budget_coverage_small_result.md`
   - `docs/specs/archive/rfs_mb0/RFS_MB0_SUBSTRATE_UNTETHERING_TRANSITION_ENERGY_SWEEP_SPEC.md`
   - `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_substrate_untethering_transition_energy_sweep_result.md`
   - `docs/specs/archive/rfs_mb0/REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md`
   - `docs/research_notes/validation_design/val_ecology_viability_reorientation.md`
   - `docs/research_notes/validation_design/README.md`
5. Read the current theory-pivot notes:
   - `docs/research_notes/omega_theory/constructor_theory_and_omega_axiology.md`
   - `docs/research_notes/omega_theory/deriving_omega_relevance_from_primitives.md`
   - `docs/research_notes/omega_theory/formal_stack_v0.md`
   - `docs/research_notes/omega_theory/omega_glossary.md`
   - `docs/research_notes/omega_theory/public_terms_and_translations.md`
   - `docs/research_notes/omega_theory/historical_probe_terms.md`
   - `docs/research_notes/omega_theory/omega_as_viable_value_bearing_trajectory_space.md`
   - `docs/research_notes/primitive_branch/omega_meets_fep.md`
   - `docs/research_notes/primitive_branch/valuerhood_as_recoverable_historical_identity.md`
6. Treat older probe scripts as historical unless deliberately revisiting a
   branch:
   - COM/fiber scripts: `probe_09` through `probe_13b`
   - trajectory-space scripts: `probe_T0`, `probe_T1`, `probe_T1F`, `probe_I0`, `probe_I0b`
   - primitive/DAX scripts: `probe_DA0` through `probe_DAX_G5`
7. Inspect compact historical summaries, not raw caches:
   - `results/historical_probes/probe_09_robust_fiber_reachability_results/summary.json`
   - `results/historical_probes/probe_10_com_viable_propagation_robustness_extended_results/summary.json`
   - `results/historical_probes/probe_10_com_targeted_fragility_refinement_results/summary.json`
8. Preserve the running log after every meaningful run.

Use this Python executable locally:

```powershell
.\.venv\Scripts\python.exe
```

Use 18 worker processes for CPU-heavy runs unless deliberately stress testing.

## Finite Relational Adapter Workflow

Adapter architecture is:

```text
source artifact
-> deterministic source compiler
-> finite relational IR
-> generic audits
-> retained provenance and digests
```

This is the principled boundary. Source compilers may be substrate-specific, but
generic audits should consume the finite relational IR rather than private
source-specific assumptions.

The finite relational adapter has two surfaces:

```text
finite grid source:
  low-label input for small rectangular grid substrates.

derived graph source:
  low-label input for graph-like substrates.

finite relational IR:
  explicit normalized audit surface used by the generic adapter checks.
```

Prefer the highest source layer that still honestly represents the substrate:
finite grid for grid-like examples, derived graph for graph-like examples, and
low-level finite relational IR only for regression fixtures, theorem-facing toy
examples, or cases where the exact relations are already externally declared.

Derived graph sources declare:

```text
nodes;
edges;
observations;
presentations;
safety;
provenance.
```

They do not declare `primitive_rel`, `primitive_sep`, `primitive_asym`, carrier
predicates, profiles, or audits. The compiler derives:

```text
Rel:
  graph edge.

Sep:
  declared observation difference.

Asym:
  strict one-way edge plus Sep.

merge_separated:
  state pairs separated by some declared observation.

carrier candidates:
  mutual-reach components carrying separated pairs.
```

Finite grid sources declare:

```text
width;
height;
blocked cells;
movement rule;
observations;
presentations;
safety;
provenance.
```

The finite grid compiler derives cells and movement edges, then routes through
the derived graph compiler. It exists to test source-compiler reuse: a new
source format targets the same finite relational IR and the same generic audit
engine.

Run a finite grid source with:

```powershell
.\.venv\Scripts\python.exe -m omega.adapters.finite_relational.grid_cli `
  --source omega\adapters\finite_relational\fixtures\finite_grid_east_asymmetry.json `
  --out .tmp\finite_grid_east_asymmetry
```

The finite grid CLI retains the same source/compiled/digest/provenance/audit
artifacts as the derived graph CLI.

Run a derived graph source with:

```powershell
.\.venv\Scripts\python.exe -m omega.adapters.finite_relational.graph_cli `
  --source omega\adapters\finite_relational\fixtures\derived_graph_strict_asymmetry.json `
  --out .tmp\derived_graph_strict_asymmetry
```

The derived graph CLI retains:

```text
source.json
compiled_model.json
source_digest.txt
compiled_model_digest.txt
provenance_check.json
audit_results.json
summary.json
```

Run a low-level finite relational IR fixture with:

```powershell
.\.venv\Scripts\python.exe -m omega.adapters.finite_relational.cli `
  --model omega\adapters\finite_relational\fixtures\sound_pass.json `
  --out .tmp\finite_relational_adapter_smoke
```

The low-level IR CLI retains:

```text
model_digest.txt
provenance_check.json
audit_results.json
summary.json
```

Focused adapter validation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -m pytest `
  tests\test_finite_relational_adapter.py `
  tests\test_derived_graph_adapter.py `
  tests\test_finite_grid_adapter.py `
  tests\test_finite_relational_adapter_smoke.py `
  -q --basetemp .tmp\pytest-adapters -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check `
  omega\adapters\finite_relational `
  omega\validation\finite_relational_adapter_smoke.py `
  tests\test_finite_relational_adapter.py `
  tests\test_derived_graph_adapter.py `
  tests\test_finite_grid_adapter.py `
  tests\test_finite_relational_adapter_smoke.py
```

External adapter smoke:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_smoke `
  --out-root .tmp\finite_relational_adapter_smoke
```

Generated/adversarial adapter validation:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_adapter_adversarial `
  --out-root .tmp\finite_relational_adapter_adversarial
```

Claim boundary:

```text
the adapter compiles declared finite sources and runs exact finite audits;
it does not validate the source model, prove Omega, infer value, or certify a
real-world substrate.
```

Adapter non-negotiables:

```text
1. Do not trust hand-labeled asymmetry in adapter-facing sources when it can be
   derived from declared post-adapter structure.

2. Do not let source compilers add private audit semantics. They should compile
   into the finite relational IR and then call the generic audit engine.

3. Do not mix discovery and validation. Exploratory candidate generation may
   suggest observations, carriers, or presentations, but validation claims must
   use retained predeclared inputs.

4. Retain both source and compiled model whenever a source compiler is used.
   The compiled model is the audit surface; the source artifact is the
   provenance surface.

5. Every derivation rule must be named in the compiled model provenance.

6. A passing audit means only that the declared finite structure satisfies the
   declared finite check. It does not certify that the source abstraction is
   empirically correct.

7. Hidden-loss checks are distinct from phantom-reachability checks. Phantom
   reachability catches abstract futures that the exact model never had;
   hidden reachability loss catches an abstract surface that still reports a
   path after the exact changed model has lost it.

8. Generated/adversarial adapter cases are hardening checks, not empirical
   validation. They are useful when they search for finite failure modes and
   then retain the generated source, compiled model, digests, audit results,
   and summary.

9. Carrier-transfer audits are same-model, two-snapshot contracts. They check
   declared source and target carriers plus a declared correspondence; they do
   not assert object identity, recoverability, lineage, agency, or Omega.
```

Future source adapters should follow this rule:

```text
new substrate format:
  add a compiler to finite relational IR;
  add fixtures and provenance;
  reuse existing audits where possible;
  add a new generic audit only if the existing IR cannot express the needed
  check.
```

## Repository Layout Rules

Keep the repository root uncluttered.

Current root-level folders should stay limited to:

- `docs/`
- `formal/`
- `omega/`
- `scripts/`
- `tests/`
- `results/`
- local/private or environment folders that are ignored

Public front-door files should stay synchronized after a formal pivot:

- `README.md`
- `docs/OMEGA_FORMALISM_PRIMER.md`
- `docs/EXTERNAL_READER_GUIDE.md`
- `docs/research_notes/omega_theory/README.md`

If the root formalism changes, update those files in the same commit as the
technical proof or theory note. Older notes should be marked as historical or
strict-presentation explorations rather than silently deleted.

## Lean Formalism Workflow

The Lean sandbox lives under:

```text
formal/lean/
```

Default repository-root build command:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
```

Use narrower builds only when the edited layer is narrow:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaCore
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaProper
```

The wrapper runs from `formal/lean`, prefers the pinned installed toolchain, and
falls back to Elan/PATH discovery. Direct Lake commands are a fallback for
interactive local debugging, not the default validation path.

Fallback direct setup:

```powershell
$env:PATH = (Resolve-Path '.tools\lean-4.30.0\lean-4.30.0-windows\bin').Path + ';' + $env:PATH
cd formal\lean
lake build AlphaCore
lake build AlphaOmega
lake build OmegaCore
```

Current proof-side dependency:

```text
mathlib4 v4.30.0
```

The Windows cache fetch may be unreliable locally. If `lake exe cache get`
fails, continue with source builds as long as `lake build OmegaCore` succeeds.
For Alpha-specific edits, `lake build AlphaCore` must also pass. For layer-map
or facade edits, `lake build AlphaOmega` must pass.

Before promoting a broad formalism update, verify:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
rg -n "\b(sorry|admit|axiom)\b" formal\lean -g "*.lean"
```

Use the expanded namespace build only when editing legacy compatibility
surfaces:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaCore
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build ProtoOmega
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaAdapters
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaProper
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaArchive
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaCore
```

Current active Lean posture:

```text
AlphaCore:
  primitive floor and derived primitive surfaces.

OmegaProper:
  consequence discipline, sound quotients, non-factorization compression,
  viability/reachability, recurrent support carrying/loss/transfer, and
  Layer A guardrails.

AlphaOmega:
  broad umbrella for active proof-stack validation.

OmegaCore / ProtoOmega / OmegaAdapters / OmegaArchive:
  compatibility and provenance surfaces. Build when touched, but do not treat
  them as the conceptual front door.
```

Historical executable probes live under:

- `scripts/historical_probes/`

Historical compact result artifacts live under:

- `results/historical_probes/`

Future RFS-MB0 future-landscape outputs should use:

```text
results/rfs_mb0_future_landscape/<timestamp-or-run-id>/
```

Future RFS-MB0 relation-atlas outputs should use:

```text
results/rfs_mb0_relation_atlas/<timestamp-or-run-id>/
```

Future VAL0-CT outputs, if deliberately revisited, should use:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Future VAL0-G outputs should use:

```text
results/val0_g/<timestamp-or-run-id>/
```

with a compact structure such as:

```text
config.json
results.jsonl
aggregate.csv
summary.md
```

Scratch, calibration, smoke, stress, and oversized local-only outputs should go
under:

```text
results/local_runs/
```

and should remain ignored.

For large RFS-MB0 relation-atlas and future-landscape runs, the raw CSV
directories should also remain local/ignored unless a compact subset is
explicitly promoted. The public record should normally be:

```text
docs/research_notes/validation_results/<retained_result_note>.md
```

For Future Field Atlas runs, primary CSV artifacts should use the default gzip
mode unless there is a concrete compatibility reason not to:

```text
--csv-output-mode gzip
```

This keeps logical CSV schemas but writes physical `.csv.gz` artifacts. Plain
CSV output is still available with `--csv-output-mode plain`; compatibility
runs can write both forms with `--csv-output-mode both`.

Default raw topology output should remain sharded unless a compatibility check
requires the older consolidated form:

```text
--raw-topology-output-mode sharded
```

Default transport output should remain selected unless a run specifically needs
full closure:

```text
--transport-output-mode selected_multiscale
--composition-residual-mode selected
```

Use adjacent-only mode for fast calibration and raw-topology checks:

```text
--transport-output-mode adjacent_only
--composition-residual-mode none
```

Bulky local calibration outputs should be deleted after the retained note and
logs are updated unless the run is still inside the short local review grace
period, carries strong evidence, or is explicitly promoted as a retained
dataset.

Use dry-run cleanup first:

```powershell
.\.venv\Scripts\python.exe -m omega.future_field_atlas.cleanup_runs --older-than-days 3
```

Delete only after reviewing the candidates:

```powershell
.\.venv\Scripts\python.exe -m omega.future_field_atlas.cleanup_runs --older-than-days 3 --delete
```

Do not add new root-level `*_results` folders. If a historical script defaults
to root-level output, override its output directory when rerunning it.

### Coupled Atlas Runs

Use `coupled`, not `comField`, for the two-frontier Future Field Atlas branch.

Current runner:

```powershell
.\.venv\Scripts\python.exe -m omega.future_field_atlas.run_coupled_future_field_atlas `
  --out results\future_field_atlas\<run_id> `
  --horizon-max 32 `
  --workers 18
```

The current coupled layer is an infrastructure probe. It must keep product
baselines, marginal-retention rows, joint-vs-product residual rows, and
reconstruction audits before any interpretation. Do not report Omega, agency,
value, identity, valuerhood, or candidate-promotion language from coupled probe
outputs.

Current hardening requirements:

```text
coupled_operator_manifest.csv.gz must identify the coupled operator by canonical JSON and digest
condition_pairing_policy = index_matched
start_pairing_policy = zip_selected_starts
cap poisoning must persist after any internal frontier cap
PASS_WITH_SKIPS is not a clean reconstruction pass
NO_COMPLETE_ROWS blocks interpretation
medium-scale readiness must be checked before any coupled sweep is interpreted
```

Use `coupled_marginal_projection_delta_by_horizon.csv[.gz]` for product-vs-
coupled marginal-set deltas. It must carry:

```text
projection_semantics = product_vs_coupled_marginal_set_delta
causal_interpretation = none
```

Do not use marginal projection rows as directional-causal evidence.

Mechanism-resolution rule after the H64 near-zero pass:

```text
Do not treat coupling_strength = 0.000 under joint_energy_rank_prefix as a
product-equivalence baseline. It is already a joint selector over additive
energy. Use joint_selection_family = product when a true product reference is
needed.

Do not broaden scalar mismatch sweeps unless a specific threshold bracket is
being tested. In the current H64 pair8 design, scalar effects remain distinct
through 0.010 and saturate by 0.020.

Keep pair-aware summaries mandatory. Pair005 is currently a heavy-pair /
critical-pair clue, not a row to average away.
```

## Context From The Theory/Paper Side

The broader Omega work, as represented in the handoff documents and older local
papers, is trying to determine whether there is a real scientific object behind
the proposed Omega formalism.

The recurring conceptual thread is:

> Omega is not raw entropy. Omega is viable propagation.

The current formal correction is sharper:

> Primitive probes calibrate distinction, asymmetry, and causal continuity.
> Omega validation begins only once minimal valuers and value-bearing
> trajectory space are in scope.

The previous validation pivot was VAL0-CT:

> Use constructor-style task algebras to test whether future-preserving
> reachability `R1` predicts long-horizon reachability retention better than
> raw reachability `R0` and equal-budget `R0_lookahead` controls.

Reconnaissance status:

> VAL0-CT reproduced R1 advantages in designed anchors and kept dense controls
> clean, but did not establish broad held-out or unlabeled generalization.

VAL0-G then tested neutral grammar geometry:

> Generate constructor-like task worlds from neutral transformation primitives
> and ask whether asymmetric continuation dynamics produce measurable geometry
> classes such as self-termination, brittle ridges, noisy fragments, lock-in,
> and recoverable basins without hand-labeling outcomes.

VAL1-MF then tested simple multifield coupling and sampled interference:

> Naive joint enumeration worsened cap-censoring, while sampled counterfactual
> deltas detected constructive support-like interference but not robust
> destructive/capture dynamics.

The current empirical pivot is now RFS-MB0 future-landscape detection:

> Build minimal neutral transition substrates, measure their horizon-indexed
> reachable-future profiles, and ask whether structured future deformation
> survives matched-null comparison without semantic labels.

Current detector status:

```text
RFS-MB0 future-landscape detector v1.1 + long-horizon audit:
  implementation passed
  scientific gate not passed
  current result: zero aggregate structured families
  long-horizon read: failure is not just an H16 cutoff
```

Older papers and drafts motivate variants of:

- viable futures;
- irreversibility and recoverability;
- field-like gradients over future viability;
- agency under computational irreducibility;
- gradient/value interpretations;
- multifield or fiber formulations where coupled systems preserve viable
  structure through lower-dimensional macro descriptions.

Important caveat: the original papers are not all reproduced inside this repo.
Some source PDFs are now included under `docs/theory_archive/progenitor_drafts/` as early
theoretical provenance. They are drafts only and should not be treated as
current validation results, peer-reviewed claims, or final formal statements.
The earlier theory/status draft lives under `docs/theory_archive/current_theory/`. Active
trajectory-space branch notes live under `docs/research_notes/trajectory_space/`.
The current formal-stack and glossary notes live under
`docs/research_notes/omega_theory/`. The primitive/FEP/valuerhood bridge notes
live under `docs/research_notes/primitive_branch/`. Current validation-design
notes live under `docs/research_notes/validation_design/`.
Some text drafts still live only in the local project folder outside Git.

## Working Definitions

### Current Formal Stack

The current stack is:

```text
distinction
-> asymmetry
-> relation / causal continuity
-> identity
-> recoverability
-> valuerhood
-> viability
-> Omega-compatible viability
```

Lushness is adjacent to this chain rather than identical to Omega. It names
structured branching that propagates. Omega-compatible lushness is lushness
filtered by recoverable value-bearing compatibility.

Working thesis:

```text
Omega is the asymptotic compatibility structure of value-bearing trajectory
space.
```

Important level boundary:

- relation is causal continuity through transformation, not merely graph
  adjacency or coupling;
- identity is organized causal continuity through change;
- recoverability is perturbation-continuability, not exact restoration;
- a valuer is a bounded historical identity for which different continuations
  asymmetrically affect recoverable continuability;
- viability is the gate;
- Omega compatibility is the target constraint;
- lushness is a richness desideratum only after compatibility filtering.

Consequence for empirical work:

```text
CA, DAR, DAX, and bare field probes are primitive-floor or fakeout-calibration
probes unless they include explicit valuerhood and recoverable continuability.
```

### Current Validation Target: RFS-MB0 Future Landscape

RFS-MB0 future-landscape detection is the current active validation design target.

It is not full Omega validation. It is a finite reachable-futures substrate
intended to measure neutral future-profile structure before adding richer
agency, valuerhood, identity, or constructor language.

Primary question:

```text
Can horizon-indexed reachable-future profiles distinguish structured future
deformation from saturation, clocks, collapse, and matched-control artifacts?
```

Implementation:

```text
omega/rfs_mb0_future_landscape/
```

Latest result:

```text
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_result.md
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_spectral_channel_high_loading_repair_result.md
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_response_resolution_scaleup_result.md
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_expansion_smoke_result.md
docs/research_notes/validation_results/rfs_mb0/rfs_mb0_stage_b2_exploratory_iteration_pass_result.md
```

Current live read:

```text
Stage B-2 strengthened the read that preregistered A/C joint signed syndromes
are sensitive to topology-level edge perturbations. The spectral future-field
smoke found a nonblank direct-control spectral object over future-frontier and
transition-flow matrices. The channel-edge repair prep added cheap shuffle
controls, high-loading export, item-to-edge mapping, and ablation checks, but
blocked the 24h channel-edge run because high-loading ablation was
random-equivalent at the small-smoke scale. The follow-up high-loading repair
added stable item selection and frequency/baseline-flow matched random
ablation; the repaired small smoke cleared the instrument gate for a larger
spectral channel-edge exploratory run, while leaving frontier-size and
probe-marginal controls as caveats. The live spectral branch then reoriented to
directional horizon-transport matrices; row/column/bimarginal matched nulls,
fixtures, and committed-input scaleups now pass instrument gates. Tiny
perturbations remain mostly stable, while stronger nonlethal p0.015/p0.02
ladders produce high-alignment mass-growth/control-equivalent departures in
mid/downstream horizon transport. The H128 response-surface scaleup then
resolved this into a stable-to-amplified-aligned horizon response surface with
8/8 response fixtures passing, matched marginal separation to H128, and no
terminal-saturation flags. The next task is a horizon-transport theory note,
not holdout, graph-channel diagnostics, or candidate promotion.
```

RFS-MB0 is now the recommended starting point for new implementation work.
VAL0-CT, VAL0-G, VAL1-MF, COM/fiber, trajectory-space, CA, DAR, and DAX work
remain important historical provenance and failure analysis, but they are not
the current front edge.

### VAL0-CT Status

VAL0-CT tested whether `R1` could serve as a minimal future-preserving
reachability predictor.

Current result:

```text
designed anchors:
  R1 advantage reproduced

low_resolution_dense:
  clean control

held-out named generators:
  no broad R1 generalization

unlabeled geometry battery:
  global R1 advantage remained negative
  corridor d8 did not survive scale as a robust predictor
  candidate future-R0 variance was the best weak stratifier
```

Interpretation:

> R1 remains useful as a probe and guardrail, but the project should not treat
> policy victory as the object. The object is now recoverable-continuation
> geometry itself.

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

The current adapter-facing refinement is:

```text
raw entropy / raw complexity / unordered summaries
  are proxy summaries;

boundedly recoverable consequence structure
  is the thing those summaries must be tested against.
```

This is why the finite relational adapter now includes a bounded-recovery audit:
a declared observation and a declared decoder family are checked against a
declared target predicate. The result is intentionally observer-class relative:
failure means no decoder in the declared bounded family recovers the target, not
that no possible unbounded decoder could.

This also tightens the project language around lushness:

```text
avoid:
  lushness = entropy
  lushness = complexity
  lushness = branch count

use, provisionally:
  lushness candidate =
    soundly presented,
    boundedly recoverable,
    consequence-bearing continuation structure
    inside the relevant viability and compatibility constraints.
```

See:

```text
docs/research_notes/omega_theory/useful_information_and_constraint_selection_v0.md
```

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

## Legacy Probe Line Summary

This section is retained as historical probe provenance. It is not the current
active workflow. Use it when deliberately resuming or auditing older
VAL/COM/RFS/Future Field Atlas branches.

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

What we can currently say:

- We have not validated Omega as a scientific theory.
- We have a Layer A theorem stack for continuation-map integrity: which
  summaries, quotients, presentations, supports, carriers, and transformations
  preserve or destroy declared continuation facts.
- We have standard-core compression results: sound quotient as kernel
  containment, class soundness as clique soundness, non-factorization as the
  anti-proxy schema, and exact recovery as support disjointness.
- We have viability/reachability and recurrent-support machinery showing that
  endpoint viability and forward reachability are weaker than recurrent
  distinction-carrying support.
- We have perturbation/loss/restoration/transfer guardrails for recurrently
  carried consequence distinctions.
- We have a finite relational adapter pilot that compiles declared finite
  sources into a normalized IR, runs generic audits, and retains provenance.
- The adapter layer is infrastructure only. It does not validate real-world
  source models, infer value, certify agency, or prove Omega.

Current near-term engineering target:

```text
make source compilers increasingly adaptive while keeping generic audits,
retained source/IR digests, and predeclared provenance non-negotiable.
```

Current near-term theory target:

```text
connect derived primitive exposure, consequence profiles, and recurrent support
without reintroducing hidden identity or hand-labeled asymmetry.
```

## Legacy Scientific Position Before Layer A Consolidation

The following block is retained for historical context. It records the state of
the empirical and primitive-probe branches before the current Layer A / adapter
workflow became the default.

What we can say:

- We have not validated Omega as a scientific theory.
- The current formal target is Omega Primitive Calculus v0 plus checked finite
  presentations that make theorem transfer and failure modes explicit.
- The current empirical target is bridge discipline: Future Field Atlas and the
  stochastic distinction-channel probe should emit formal-consumption artifacts
  without semantic promotion.
- VAL0-G and VAL1-MF are historical reconnaissance layers, not the current
  validation center.
- VAL0-CT remains the preceding calibration layer: R1 anchor wins reproduced,
  dense controls stayed clean, but broad held-out or unlabeled generalization
  was not established.
- Earlier work extracted an executable candidate object in a toy multifield
  substrate:

```text
COM-like multi-step viable propagation through certified fibers
in F,T attractive coupling
alpha approximately 0.45-0.525
horizons 900-2400
```

- That COM/fiber object survived product/shuffled/independent baselines.
- It survived a meaningful perturbation battery.
- It was not merely high entropy.
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
- Probe DAX-G5 froze that detector and tested 5000 held-out q=3/r=1 rules. It
  failed held-out prediction: fertile bands produced positives, but only 1.17x
  the control rate, and the B4 high-chaos/high-frozen control band produced 4
  primary positives. G3/G4 therefore describe a motif ecology, not yet a
  validation-ready predictive detector.
- The May 2026 formal-stack update recentered the project around valuerhood and
  value-bearing trajectory space. This demotes CA/DAR/DAX-style probes to
  primitive-floor calibration unless the tested world includes bounded
  historical identities with recoverable continuability.
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
  in `scripts/setup/omega_env.bat` and `scripts/setup/omega_env.ps1`.
- Some result directories contain compact tracked summaries, while large raw
  per-seed/intermediate files are intentionally ignored.
- Existing code is research-code quality, not library quality.
- Probe T1 staged local trajectory samples under `_trajectory_samples/`; those
  are intentionally untracked because they are large generated intermediates.

## Legacy Recommended Next Probes

This section is deprecated for default work selection. It is retained as a
record of the pre-consolidation empirical roadmap. Current next work should be
chosen from the Layer A / finite relational adapter workflow unless the user
explicitly resumes a historical probe line.

### RFS-MB0.1: Substrate/Environment Redesign and Window-Control Repair

Question:

> Can future-landscape structure survive controls that preserve degree,
> frontier size, saturation profile, and probe-family marginals?

Current status:

```text
RFS-MB0 detector v1.1 + long-horizon audit:
  implementation passed
  local false positives are exposed but do not promote aggregate claims
  no aggregate structured family passes yet
  H1024 audit does not reveal delayed long-horizon onset
  nominal structured families are saturation dominated
```

Do not scale this exact RFS-MB0 substrate into longer runs until this is
addressed.

Required next changes:

- revise environment families so candidate structured cases stay
  non-saturated for meaningful windows;
- add frontier-size-preserving nulls;
- add saturation-matched nulls;
- strengthen window-level controls before promoting early/pre-saturation
  profile windows;
- report family-level and probe-family-level ranks against controls;
- require degree-control separation before assigning `structured_propagation`;
- preserve v0/v1 outputs as historical baselines.

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

DAX-G5 froze the detector and failed the held-out prediction test. This is an
important negative result: q=3/r=1 still contains real motifs, but the G4 fertile
bands are not predictive enough under the frozen detector. The next step should
not be a larger G5 with tuned thresholds. It should be either a focused anatomy
of the B4 leaks and fertile positives, or a narrower detector target that
separates DAR-persistence from generic high-future-distinct persistence.

### Probe 13: Formal COM Fiber Transport Object

Historical goal: turn the COM/fiber empirical object into a precise
mathematical definition.

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

### Probe V0: Minimal Valuer-World Benchmark

Question:

> Given minimal self-maintaining valuers, do Omega-style predictors explain
> persistence, collapse, recovery, pseudo-Omega trapping, and mutual corridor
> preservation better than survival, reward, reachability, empowerment, or
> local viability alone?

Required ingredients:

- bounded historical identities;
- perturbation recovery;
- path consequences for future continuability;
- action or interaction channels;
- slack, filtering, and failure/re-entry dynamics;
- controls for stasis, clocks, lock-in, externally maintained persistence, and
  high reachability without self-maintenance.

This is the first probe family aimed at Omega proper rather than the primitive
floor.

## Maintenance Rule

Every new substantial workflow, adapter, or probe must update:

- `docs/OMEGA_RUNNING_LOG.md`
- this manual if concepts or conclusions change
- `README.md` only when usage/setup changes

When a workflow is superseded:

- do not silently delete its instructions;
- mark the old section as legacy, deprecated, or resume-only;
- add the current workflow above the old one;
- state the current claim boundary and validation command;
- preserve retained artifacts and result notes as provenance.

When adding results to Git:

- commit scripts and compact summaries;
- do not commit virtual environments, caches, smoke runs, or massive raw graph
  dumps;
- check `git diff --cached --name-only` and staged file sizes before commit.
