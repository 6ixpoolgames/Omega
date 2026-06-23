# Omega Theory Notes

Status: theory-note navigation surface
Scope: current formal stack, supporting scaffolds, empirical bridges, and historical lineage
Claim boundary: navigation only; not empirical validation, not theorem closure, not Omega validation

This folder contains dense theory-side notes for the Omega / Reachable Futures
project. It is not the first-contact onboarding layer.

Start with:

```text
../../../README.md
layer_a_theorem_spine_v0.md
current_theory_posture_v0.md
constraint_based_alignment_floor_v0.md
alphaomega_continuation_proto_teleology_v0.md
../../VALUER_FORMAL_TARGET_V0.md
../../OMEGA_COMPATIBLE_VALUER_TRAJECTORY_SPACE_V0.md
../../OMEGA_FORMALISM_PRIMER.md
alpha_primitive_core_v0.md
alpha_primitive_derived_surfaces_v0.md
laws_of_form_adjacency_v0.md
adapter_provenance_v0.md
audit_response_roadmap_v0.md
finite_relational_adapter_design_v0.md
useful_information_and_constraint_selection_v0.md
declaration_budget_and_transport_profiles_v0.md
deterministic_pre_stochastic_layer_v0.md
stochastic_recovery_characterization_v0.md
stochastic_recovery_theorem_spine_v0.md
stochastic_recovery_formalization_v0.md
recovery_layer_checkpoint_v0.md
coarsening_permanence_v0.md
presentation_fact_closure_v0.md
robust_recovery_ambiguity_sets_v0.md
prior_relative_recovery_v0.md
bridge_claims_ledger_v0.md
stochastic_continuation_loss_v0.md
policy_conditioned_stochastic_dynamics_v0.md
invariant_profile_compression_v0.md
primitive_exposure_realization_bridge_v0.md
presentation_soundness_pattern_v0.md
continuation_deformation_nonfactorization_v0.md
ai_proxy_failure_nonfactorization_v0.md
approximation_contract_v0.md
carrier_semantics_compression_v0.md
compression_guardrails_v0.md
alpha_omega_unification_map_v0.md
omega_primitive_calculus_v0_lean_root_skeleton.md
theory_arm_map_v0.md
omega_formal_core_v0_2_future_distinction_dynamics.md
```

## Current Stack

The current best formal stack is:

```text
Layer 0: Alpha Primitive Core v0
Layer 0b: AlphaOmega facade stack
Layer 0c: distinction transport and recoverability audit machinery
Layer 1: finite presentations and theorem-transfer adapters
Layer 2: trajectory families and process-bundle scaffolds
Layer 3: viability and action-channel scaffolds
Layer 4: compatible valuer-bearing future target
Layer 5: empirical interface targets
```

Compact target:

```text
Omega is the possible maximal compatible unfolding of consequence-bearing
structure across admissible continuations.

Value-bearing futures are a downstream manifestation, not the primitive
starting point.
```

This is a formal target, not an empirical result.

## Lean Status

The current Lean root skeleton lives in:

```text
../../../formal/lean/
```

Checked files now include:

```text
AlphaOmega.lean
AlphaCore/Primitive.lean
AlphaCore/PrimitiveApartness.lean
AlphaCore/PrimitivePath.lean
AlphaCore/Reachability.lean
AlphaCore/Examples.lean
AlphaCore/Independence.lean
AlphaCore/Nondegenerate.lean
AlphaCore/PrimitiveMap.lean
AlphaCore/PrimitiveSoundPresentation.lean
ProtoOmega/Presentation/Native.lean
ProtoOmega/Transport/Native.lean
ProtoOmega/Transport/LegacyBridge.lean
ProtoOmega/Transport/NativeExamples.lean
ProtoOmega/Transport/Preorder.lean
ProtoOmega/Recoverability/Native.lean
ProtoOmega/Recoverability/LegacyBridge.lean
ProtoOmega/Recoverability/NativeExamples.lean
ProtoOmega/Recoverability/NormalLax.lean
ProtoOmega/Recoverability/RecurrentNative.lean
ProtoOmega/Recoverability/RecurrentNativeExamples.lean
ProtoOmega/Recoverability/Recurrent.lean
ProtoOmega/Separations/MarginalJointNative.lean
ProtoOmega/Separations/MarginalJoint.lean
OmegaAdapters/FiniteBoolean.lean
OmegaAdapters/FiniteBooleanNative.lean
OmegaAdapters/FiniteChannel.lean
OmegaAdapters/FiniteChannelDecoderNative.lean
OmegaAdapters/FiniteChannelNative.lean
OmegaAdapters/ProbabilisticChannel.lean
OmegaAdapters/ProbabilisticChannelNative.lean
OmegaAdapters/ProbabilisticChannelCascadeNative.lean
OmegaAdapters/ProbabilisticChannelCascadeEvidenceNative.lean
OmegaAdapters/ProbabilisticChannelPolicy.lean
OmegaAdapters/SubstrateBridge.lean
OmegaAdapters/Audit/AdapterFailures.lean
OmegaProper/Compatibility/JointPresentation.lean
OmegaProper/Scaffolds/FiniteMaximal.lean
OmegaProper/Scaffolds/CompletionCounterexamples.lean
OmegaProper/Trajectory/AlphaConsequenceSeed.lean
OmegaProper/Trajectory/AlphaConsequenceSeedExamples.lean
OmegaProper/Trajectory/ApproximationContract.lean
OmegaProper/Trajectory/CarrierCertificate.lean
OmegaProper/Trajectory/CarrierPresentationValidity.lean
OmegaProper/Trajectory/CarrierSemantics.lean
OmegaProper/Trajectory/CarrierTrajectoryLanguage.lean
OmegaProper/Trajectory/ContinuationDeformation.lean
OmegaProper/Trajectory/DeformationProfile.lean
OmegaProper/Trajectory/DeformationProfileExamples.lean
OmegaProper/Trajectory/GeneratedCarrier.lean
OmegaProper/Trajectory/ProtoTeleologicalSeed.lean
OmegaProper/Trajectory/ProtoTeleologicalSeedDiscipline.lean
OmegaProper/Trajectory/ProtoTeleologicalSeedExamples.lean
OmegaProper/Trajectory/ProtoTeleologicalProfile.lean
OmegaProper/Trajectory/ProfileAbstraction.lean
OmegaProper/Trajectory/ProfileApproximation.lean
OmegaProper/Trajectory/PrimitiveConsequenceExposure.lean
OmegaProper/Trajectory/PrimitiveDynamicsRealization.lean
OmegaProper/Trajectory/PresentationSoundness.lean
OmegaProper/Trajectory/PresentationSoundnessInstances.lean
OmegaProper/Trajectory/ConsequenceRelation.lean
OmegaProper/Trajectory/ConsequenceClasses.lean
OmegaProper/Trajectory/ConsequenceDiscipline.lean
OmegaProper/Trajectory/ConsequenceComparison.lean
OmegaProper/Trajectory/ConsequencePanelDiscipline.lean
OmegaProper/Trajectory/ParameterizedRecurrentSupport.lean
OmegaProper/Trajectory/PresentationFactClosure.lean
OmegaProper/Trajectory/PresentationFactClosureExamples.lean
OmegaProper/Trajectory/PresentationFactCarrierExamples.lean
OmegaProper/Trajectory/PresentationFactRecoveryExamples.lean
OmegaProper/Trajectory/PresentationFactViabilityExamples.lean
OmegaProper/Trajectory/RecurrentSupportExtension.lean
OmegaProper/Trajectory/RecurrentSupportLineage.lean
OmegaProper/Trajectory/RecurrentSupportPathTransfer.lean
OmegaProper/Trajectory/RecurrentSupportPerturbationBudget.lean
OmegaProper/Trajectory/RecurrentSupportIntegrity.lean
OmegaProper/Trajectory/RecurrentSupportRobustness.lean
OmegaProper/Trajectory/RecurrentSupportRestoration.lean
OmegaProper/Trajectory/RecurrentSupportSuccessorDistinction.lean
OmegaProper/Trajectory/RecurrentSupportTransfer.lean
OmegaProper/Trajectory/IrreversibleRecurrentSupportLoss.lean
OmegaProper/Trajectory/JointRecurrentSupport.lean
OmegaProper/Trajectory/SimulationTransfer.lean
OmegaProper/Trajectory/SupportUnderPerturbation.lean
OmegaProper/Recovery/FiniteChannel.lean
OmegaProper/Recovery/ConfusionBound.lean
OmegaProper/Recovery/CoarseningPermanence.lean
OmegaProper/Recovery/Deterministic.lean
OmegaProper/Recovery/ObservationRefinement.lean
OmegaProper/Recovery/Randomized.lean
OmegaProper/Recovery/RandomizedFamily.lean
OmegaProper/Recovery/Robust.lean
OmegaProper/Recovery/RobustRandomized.lean
OmegaProper/Recovery/Joint.lean
OmegaProper/Recovery/PolicyContinuation.lean
OmegaProper/Recovery/Prior.lean
OmegaProper/Recovery/Examples.lean
OmegaArchive/Basic.lean
OmegaArchive/PrimitiveWitness.lean
OmegaCore/DistTrans.lean
OmegaCore/AdapterFailures.lean
OmegaCore/NormalLax.lean
OmegaCore/Recurrent.lean
OmegaCore/Completion.lean
OmegaCore/Counterexamples.lean
OmegaCore/MarginalJoint.lean
OmegaCore/Presentations/FiniteBoolean.lean
OmegaCore/Presentations/FiniteChannel.lean
OmegaCore/Presentations/ProbabilisticChannel.lean
OmegaCore/Presentations/ProbabilisticChannelPolicy.lean
```

Current checked scope:

```text
Alpha primitive frame over relation, distinction, and asymmetry;
Alpha-native primitive apartness, relation-generated primitive paths, and
primitive-sound presentations;
Alpha reachability generated by relation;
finite Alpha separation examples showing distinction without asymmetry, local
asymmetry without global reach irreversibility, and local nonreciprocity
without global reach irreversibility;
finite Alpha independence examples showing relation, distinction, asymmetry,
and reach irreversibility do not automatically supply one another;
Alpha primitive nondegeneracy witnesses showing that an actual
asymmetry-bearing distinction blocks total relation and identification
collapse;
primitive-preserving maps between Alpha frames showing identity, composition,
witness preservation, primitive nondegeneracy preservation, and no-map-to-
collapse guardrails;
presentation-native distinction, separation, order, and transport structures
for separating presentation machinery from full Alpha substrate contact;
support-level distinction transport;
normal-lax recoverability and non-erasure consequences;
finite-chain recurrent recoverability;
finite maximal completion existence, including Finset/Fintype specialization;
finite completion counterexamples for pairwise-vs-joint admissibility,
non-unique maximal completions, and nonexistence of a greatest completion;
finite distinction-transport counterexample for marginal-like non-erasure not
implying strictly joint non-erasure;
adapter-failure examples showing theorem transfer failure without closure or
laxity laws;
finite Boolean relation support presentation with presentation-native
separation/order/transport, Alpha-frame-compatible relation-induced transports,
identity relation, relational composition, and changed-carrier recovery;
finite channel / partition presentation with presentation-native
separation/order/transport, Alpha-frame-compatible exact decoder recovery,
channel composition, changed-carrier recovery, and constant-channel separation;
finite channel decoder provenance split separating existence-style recovery
from registered and declared registered decoder recovery, with counterexamples
blocking the reverse implication;
explicit substrate bridge objects separating presentation-level machinery from
substrate-contact claims;
Alpha-native probabilistic channel core with exact/probabilistic separation,
full-support converse, high-probability counterexample, native finite-channel
support projection, and finite cascade error bound;
finite cascade evidence object separating path-ensemble theorem input from
independently normalized summary rates;
finite policy-separation example showing that Bayes-best target recovery can
strictly exceed fixed-declared target recovery;
OmegaProper recovery profile layer showing that support-exact recovery is the
threshold-one endpoint of source-indexed recovery, observation refinement
preserves deterministic and randomized recovery, randomized decoding is a
separate decoder axis, explicit deterministic/randomized decoder-class
predicates specialize to the unrestricted recovery predicates, joint recovery
safely projects to marginal recovery, and fixed-policy finite-horizon hit
profiles are bounded and horizon-monotone; robust recovery over declared
ambiguity sets reduces to ordinary recovery on singleton sets, is monotone in
threshold and ambiguity-set inclusion, and is preserved by observation
refinement under explicit decoder-class lifting; robust randomized recovery
adds the same ambiguity-set discipline for one shared randomized decoder and
explicit randomized-decoder classes; declared randomized-decoder family
surfaces are finite enumeration objects and do not claim global randomized
optimization;
prior-relative expected recovery is kept separate from worst-case and robust
recovery, with worst-case thresholds implying expected thresholds under any
declared prior and a skewed-prior witness showing expected success can hide
worst-case failure; shared observation mass between target-distinct sources
quantitatively blocks deterministic threshold recovery above `1 - epsilon`;
failure of deterministic, robust, support-exact, or randomized recovery
persists under deterministic coarsening when the appropriate decoder-class
lifting law is present; presentation/fact closure now exposes the Galois
surface for common facts under declared admissible presentation families,
with an X2 pilot showing first-coordinate facts disappear when a second
coordinate presentation is admitted and a recovery pilot showing exact bit
recovery disappears when a constant observation is admitted, plus a viability
pilot showing exact viability status disappears when a constant status
presentation is admitted, plus a carrier pilot showing certified endpoint
visibility disappears when a constant endpoint-erasing presentation is
admitted;
consequence-native trajectory guardrails for separation, consequence-respecting
classes, directional allowance versus symmetric identification,
collapse/noncollapse, over-separation, and mixed evaluated panels;
Alpha-to-consequence seed bridge showing that evaluated consequence refusal
over primitive witness endpoints blocks symmetric consequence identification;
proto-teleological seed wrappers showing that primitive Alpha contact plus
evaluated consequence merge-separation implies primitive nondegeneracy,
consequence noncollapse, and a witness blocking symmetric consequence
identification, while primitive nondegeneracy alone and consequence
noncollapse alone are not sufficient;
speculative deformation-profile bridge comparing exact merge-block and
merge-allow profiles between consequence systems over the same Alpha carrier,
without defining identity or recoverability;
profile-abstraction contracts separating coarse allow/block claims from exact
profiles via explicit soundness and completeness predicates;
generic approximation contracts showing that profile abstraction soundness and
completeness are instances of abstract/exact claim implication;
proto-teleological profile bridge showing that a proto seed supplies a
nonempty exact merge-block profile and defeats universal-allow abstraction
soundness;
generic presentation-soundness compression showing that primitive soundness,
consequence sound quotients, target-respecting presentations, and certified
carrier endpoint visibility are all forbidden-merge kernel checks;
continuation-deformation compression showing that finite deformation/proxy
failure is non-factorization of a declared continuation fact through a summary;
primitive exposure/realization bridge showing that Alpha primitive apartness
feeds consequence separation only under an exposure contract, and Alpha
relation-generated paths feed carrier certificates only under dynamics
realization and recurrence/safety contracts;
reachability/viability fixed-point semantics, trajectory safe-prefix
semantics, joint viability guardrails, hidden reach/viability/joint-viability
loss under bad presentations, loss-aware abstraction contracts,
support-level perturbation guardrails showing when changed support predicates
preserve or destroy carried merge-separated pairs, recurrent-support
robustness guardrails, positive recurrent-support transfer contracts,
path-level transfer contracts that allow internal rerouting, a finite one-way
dynamics witness where endpoint viability and forward reachability remain
while recurrent carrying is lost, and a restoration witness where an explicit
repair contract restores recurrent carrying; a parameterized bounded finite
family showing that the one-way recurrent-support loss pattern persists across
supports of size `n + 2`; and a support-extension transfer contract showing
that carrying can move from support `C` into larger support `D` when old
internal paths are replaceable inside `D`; and a support-lineage handoff
contract showing that carrying can move between incomparable supports when the
target support explicitly carries the same declared endpoints; and a successor
distinction handoff showing that carrying can move to a translated pair under
an explicit merge-separation-preserving relation; and a first exact
perturbation-budget floor showing that same dynamics cannot destroy recurrent
carrying, while one return-edge removal can destroy recurrent carrying even
when endpoint viability and forward reachability remain; and individual
recurrent carrying under separate safety predicates need not compose into
recurrent carrying under shared joint safety; carrier-certificate,
generated-carrier, and simulation-transfer repairs now mark declared support as
a candidate, generate principled carrier candidates from mutual reach, and
derive transfer through map-based and relation-based simulation rather than only bespoke support
contracts; carrier trajectory-language wrappers expose internal path facts
without treating carrier predicates as object-like supports; and certified
carrier endpoints are kept visible by sound presentations.
carrier semantics compression treats raw supports, generated mutual-reach
carriers, and trajectory-language views as presentations of one carrier
semantics surface.
```

Checkpoint:

```text
Layer A now has a first finite local perturbation calculus for recurrently
carried consequence distinctions: support, loss, preservation, restoration,
rerouting, extension, lineage, successor handoff, perturbation budget, and
joint recurrent-support failure. The current repair layer rebases support as
candidate carrier plus certificate, adds generated carrier candidates, and
derives transfer through map simulation while exposing the path-language view
of carrier certificates and blocking sound presentations from erasing certified
endpoints.
```

This is formal infrastructure only. It does not instantiate an empirical
adapter, prove valuerhood, prove compatibility in the data, or validate Omega.
AlphaCore is currently standalone; AlphaOmega is the active facade stack; the
old OmegaCore namespace is retained for compatibility during migration.

External-audit response:

```text
adapter_provenance_v0.md
audit_response_roadmap_v0.md
../../OMEGA_LITE_WORKED_EXAMPLES.md
../../HOW_TO_ADD_A_WITNESS.md
```

These notes address scale, provenance, onboarding, and contribution surfaces.

## Current Anchors

Read these as current active anchors:

```text
layer_a_theorem_spine_v0.md
layer_a_derivation_audit_v0.md
current_theory_posture_v0.md
constraint_based_alignment_floor_v0.md
bridge_claims_ledger_v0.md
alphaomega_continuation_proto_teleology_v0.md
../../VALUER_FORMAL_TARGET_V0.md
../../OMEGA_COMPATIBLE_VALUER_TRAJECTORY_SPACE_V0.md
alpha_primitive_core_v0.md
alpha_primitive_derived_surfaces_v0.md
laws_of_form_adjacency_v0.md
adapter_provenance_v0.md
audit_response_roadmap_v0.md
finite_relational_adapter_design_v0.md
deterministic_pre_stochastic_layer_v0.md
stochastic_recovery_characterization_v0.md
stochastic_recovery_theorem_spine_v0.md
stochastic_recovery_formalization_v0.md
recovery_layer_checkpoint_v0.md
recovery_policy_consolidation_audit_v0.md
coarsening_permanence_v0.md
presentation_fact_closure_v0.md
robust_recovery_ambiguity_sets_v0.md
prior_relative_recovery_v0.md
stochastic_continuation_loss_v0.md
policy_conditioned_stochastic_dynamics_v0.md
primitive_exposure_realization_bridge_v0.md
presentation_soundness_pattern_v0.md
continuation_deformation_nonfactorization_v0.md
ai_proxy_failure_nonfactorization_v0.md
carrier_semantics_compression_v0.md
approximation_contract_v0.md
compression_guardrails_v0.md
alpha_omega_unification_map_v0.md
omega_primitive_calculus_v0_lean_root_skeleton.md
lean_formalization_smoke_v0.md
primitive_witness_calculus_lean_smoke_v0.md
omega_formal_core_v0_2_future_distinction_dynamics.md
theory_arm_map_v0.md
admissibility_enrichment_and_identity_decay_nulls.md
omega_proto_valuer_compatibility_completions.md
finite_omega_completion_theorems_v0.md
finite_distinction_measures_v0.md
probabilistic_channel_presentation_v0.md
compatibility_audit_taxonomy_v0.md
dynamics_abstraction_status_v0.md
boundary_invariant_continuation_roadmap_v0.md
joint_viability_v0.md
joint_recurrent_support_v0.md
hidden_joint_viability_loss_under_bad_presentation_v0.md
viable_trajectory_language_v0.md
safe_presentation_contract_v0.md
safe_loss_visibility_v0.md
loss_aware_presentation_contract_v0.md
loss_aware_presentation_constructors_v0.md
loss_aware_presentation_strictness_v0.md
support_under_perturbation_v0.md
carrier_certificate_v0.md
carrier_presentation_validity_v0.md
carrier_trajectory_language_v0.md
generated_carrier_v0.md
simulation_transfer_v0.md
recurrent_support_path_transfer_v0.md
recurrent_support_perturbation_floor_v0.md
recurrent_support_perturbation_budget_v0.md
parameterized_recurrent_support_v0.md
recurrent_support_integrity_v0.md
recurrent_support_extension_v0.md
recurrent_support_lineage_v0.md
recurrent_support_successor_distinction_v0.md
recurrent_support_robustness_v0.md
recurrent_support_restoration_v0.md
recurrent_support_transfer_v0.md
irreversible_recurrent_support_loss_v0.md
```

## Active Scaffolds

These notes support the current stack but are narrower than the anchors:

```text
identity_decay_null_taxonomy_v0.md
finite_proto_valuer_separation_theorems_v0.md
tiny_transition_system_witnesses_v0.md
future_field_atlas_phase_ladder_and_terminal_object_update.md
minimal_compatibility_roadmap.md
transition_energy_substrate_atlas.md
transition_energy_and_constraint_untethering.md
horizon_transport_aligned_amplification.md
probabilistic_channel_presentation_v0.md
interface_sharpness_nonfactorization_v0.md
```

## Translation And Glossary Notes

Use these for terminology, but prefer the primer for first-contact onboarding:

```text
omega_glossary.md
public_terms_and_translations.md
historical_probe_terms.md
```

`omega_glossary.md` and `public_terms_and_translations.md` contain useful older
RFS-MB0 language. Where they conflict with the current README or
`docs/OMEGA_FORMALISM_PRIMER.md`, treat the README/primer as the current public
presentation.

## Historical Or Superseded Context

These notes remain useful provenance, but they should not be treated as the
current front door:

```text
omega_core_axioms_v0.md
omega_formal_core_v0.md
formal_stack_v0.md
minimal_reachable_futures_formalism.md
constructor_theory_and_omega_axiology.md
deriving_omega_relevance_from_primitives.md
omega_as_viable_value_bearing_trajectory_space.md
progenitor_stack_as_pipeline.md
primitive_interactions_boundary_irreversibility_fep.md
regenerative_filtering_slack_and_parasitic_modes.md
boundary_nonprivileging_and_field_deformation.md
gauge_coherent_shadow_formalism_v0.md
roadmap_gates_and_connections.md
horizon_transport_and_control_reorientation_note.md
```

Historical notes are not wrong merely because they are older. They record the
path into the current formalism. But public summaries should use the current
stack language unless explicitly discussing provenance.

## Empirical Claim Boundary

Current Future Field Atlas results do not claim:

```text
Omega validation;
proto-valuer detection;
valuer detection;
agent detection;
identity detection;
value detection;
compatibility detection;
support / capture / erasure detection;
substrate-general theory validation.
```

Current empirical results are precursor topology measurements under formal
operators. See:

```text
../validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md
../validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_visualization_note.md
../validation_results/future_field_atlas/future_field_atlas_substrate_morphology_atlas_result.md
```
