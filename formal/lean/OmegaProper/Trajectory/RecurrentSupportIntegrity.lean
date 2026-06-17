import OmegaProper.Trajectory.CarriedDistinction
import OmegaProper.Trajectory.CarrierCertificate
import OmegaProper.Trajectory.CarrierPresentationValidity
import OmegaProper.Trajectory.CarrierSemantics
import OmegaProper.Trajectory.CarrierTrajectoryLanguage
import OmegaProper.Trajectory.GeneratedCarrier
import OmegaProper.Trajectory.JointRecurrentSupport
import OmegaProper.Trajectory.ParameterizedRecurrentSupport
import OmegaProper.Trajectory.RecurrentSupportExtension
import OmegaProper.Trajectory.RecurrentSupportLineage
import OmegaProper.Trajectory.RecurrentSupportPathTransfer
import OmegaProper.Trajectory.RecurrentSupportPerturbationBudget
import OmegaProper.Trajectory.RecurrentSupportRestoration
import OmegaProper.Trajectory.RecurrentSupportSuccessorDistinction
import OmegaProper.Trajectory.SimulationTransfer

/-!
OmegaProper.Trajectory.RecurrentSupportIntegrity

Facade for the recurrent-support integrity stack.

This module does not add new ontology. It gathers the current recurrent-support
story under one public import surface:

* a support can recurrently carry a merge-separated consequence distinction;
* carrying can be destroyed by missing endpoints or missing internal return
  paths;
* edge-level contracts preserve carrying;
* path-level contracts preserve carrying under rerouting;
* restoration can return carrying after a witnessed loss;
* the one-way loss pattern holds in a bounded finite family.
* the two-state cycle has a first perturbation-budget floor: zero dynamic
  change cannot destroy carrying, while one return-edge removal can.
* individual recurrent carrying under separate safety predicates need not
  compose into joint recurrent carrying under shared safety.
* support is treated as a candidate carrier; certificate, generated carrier,
  and simulation-transfer layers make validity and principled transfer
  explicit.
* carrier trajectory-language wrappers expose internal path facts without
  object-like support language.
* sound presentations cannot erase certified carrier endpoints.

This is still finite/local infrastructure. It does not define identity, agency,
deformer structure, value, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportIntegrity

open ConsequenceRelation
open CarrierCertificate
open CarrierPresentationValidity
open CarrierSemantics
open CarrierTrajectoryLanguage
open CarriedDistinction
open DistinctionSupport
open GeneratedCarrier
open IrreversibleRecurrentSupportLoss
open JointRecurrentSupport
open ParameterizedRecurrentSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportPathTransfer
open RecurrentSupportExtension
open RecurrentSupportLineage
open RecurrentSupportRestoration
open RecurrentSupportRobustness
open RecurrentSupportPerturbationBudget
open RecurrentSupportSuccessorDistinction
open RecurrentSupportTransfer
open SimulationTransfer
open RecurrentViableClass
open SupportRestriction
open SupportUnderPerturbation
open SustainingViableClass

universe w k o

/-! ## Public vocabulary aliases -/

/-- Public alias for recurrent support carrying. -/
abbrev Carries
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (safe : S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  RecurrentSupportCarries S Next safe C x y

/-- Public alias for certified recurrent carrier validity. -/
abbrev CertifiedCarrier
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (safe : S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  CarrierCertificate S Next safe C x y

/-- Public alias for recurrent support integrity under change. -/
abbrev IntegrityUnder
    (S : ConsequenceSystem.{w, k, o})
    (Next0 Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe0 safe1 : S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  RecurrentSupportIntegrityUnder S Next0 Next1 safe0 safe1 C D x y

/-- Public alias for destroyed recurrent support carrying. -/
abbrev DestroyedUnder
    (S : ConsequenceSystem.{w, k, o})
    (Next0 Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe0 safe1 : S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  RecurrentSupportDestroyedUnder S Next0 Next1 safe0 safe1 C D x y

/-- Public alias for edge-level same-support transfer contracts. -/
abbrev EdgeTransferContract
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (safe0 safe1 : X -> Prop)
    (C : X -> Prop) : Prop :=
  RecurrentSupportTransferContract Next0 Next1 safe0 safe1 C

/-- Public alias for path-level same-support transfer contracts. -/
abbrev PathTransferContract
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (safe0 safe1 : X -> Prop)
    (C : X -> Prop) : Prop :=
  RecurrentSupportPathTransferContract Next0 Next1 safe0 safe1 C

/-- Public alias for support-extension transfer contracts. -/
abbrev ExtensionContract
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (safe1 : X -> Prop)
    (C D : X -> Prop) : Prop :=
  RecurrentSupportExtensionContract Next0 Next1 safe1 C D

/-- Public alias for pair-relative support-lineage contracts. -/
abbrev LineageContract
    {X : Type w}
    (Next1 : X -> X -> Prop)
    (safe1 : X -> Prop)
    (D : X -> Prop)
    (x y : X) : Prop :=
  RecurrentSupportLineageContract Next1 safe1 D x y

/-- Public alias for successor-distinction handoff contracts. -/
abbrev SuccessorContract
    (S : ConsequenceSystem.{w, k, o})
    (Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe1 : S.Fragment -> Prop)
    (D : S.Fragment -> Prop)
    (R : S.Fragment -> S.Fragment -> Prop)
    (x y x' y' : S.Fragment) : Prop :=
  RecurrentSupportSuccessorContract S Next1 safe1 D R x y x' y'

/-! ## Central transfer wrappers -/

theorem carries_transfers_by_edge_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : Carries S Next0 safe0 C x y)
    (hContract : EdgeTransferContract Next0 Next1 safe0 safe1 C) :
    Carries S Next1 safe1 C x y := by
  exact recurrentSupportCarries_transfers_of_contract hCarry hContract

theorem carries_transfers_by_path_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : Carries S Next0 safe0 C x y)
    (hContract : PathTransferContract Next0 Next1 safe0 safe1 C) :
    Carries S Next1 safe1 C x y := by
  exact recurrentSupportCarries_transfers_of_path_contract hCarry hContract

theorem edge_contract_implies_path_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    (hRec : RecurrentViableClass (dynFromNext Next0) safe0 C)
    (hContract : EdgeTransferContract Next0 Next1 safe0 safe1 C) :
    PathTransferContract Next0 Next1 safe0 safe1 C := by
  exact edgeTransferContract_implies_pathTransferContract hRec hContract

theorem destroyed_blocks_integrity
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hDestroyed : DestroyedUnder S Next0 Next1 safe0 safe1 C D x y) :
    Not (IntegrityUnder S Next0 Next1 safe0 safe1 C D x y) := by
  exact recurrentSupportDestroyed_not_integrity hDestroyed

theorem carries_extends_by_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : Carries S Next0 safe0 C x y)
    (hContract : ExtensionContract Next0 Next1 safe1 C D) :
    Carries S Next1 safe1 D x y := by
  exact recurrentSupportCarries_extends_of_contract hCarry hContract

theorem carries_lineages_by_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : Carries S Next0 safe0 C x y)
    (hContract : LineageContract Next1 safe1 D x y) :
    Carries S Next1 safe1 D x y := by
  exact recurrentSupportCarries_lineage_of_contract hCarry hContract

theorem carries_successor_by_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {R : S.Fragment -> S.Fragment -> Prop}
    {x y x' y' : S.Fragment}
    (hCarry : Carries S Next0 safe0 C x y)
    (hContract : SuccessorContract S Next1 safe1 D R x y x' y') :
    Carries S Next1 safe1 D x' y' := by
  exact recurrentSupportCarries_successor_of_contract hCarry hContract

/-! ## Headline finite witnesses -/

def two_state_cycle_carries_left_right :=
  cycle_recurrentSupportCarries_left_right

def two_state_carrier_certificate :=
  cycle_carrier_certificate

theorem two_state_certificate_sub_generated
    {z : CycleState}
    (hz : cycleClass z) :
    MutualReachCarrier cycleNext cycleClass CycleState.left CycleState.right z := by
  exact cycle_certificate_sub_generated hz

def two_state_identity_simulation_transfer :=
  cycle_certificate_transfers_by_identity_simulation

def two_state_identity_relation_simulation_transfer :=
  cycle_certificate_transfers_by_identity_relation_simulation_exists

def two_state_carrier_round_trip_language :=
  cycle_roundTripLanguage

def two_state_carrier_semantic_certificate :=
  cycle_carrier_semanticCertificate

theorem sound_presentation_keeps_two_state_certificate_visible
    {Q : Type k}
    {present : cycleConsequenceSystem.Fragment -> Q}
    (hSound : SoundQuotient.SoundQuotient cycleConsequenceSystem present) :
    PairVisibleUnderPresentation
      present
      CycleState.left
      CycleState.right := by
  exact soundPresentation_keeps_certified_pair_visible
    cycle_carrier_certificate
    hSound

def two_state_one_way_loss_witness :=
  irreversible_recurrent_support_loss_witness

def two_state_loss_and_restoration_witness :=
  cycle_recurrentSupport_restored_after_broken_loss

def two_state_perturbation_budget_floor :=
  two_state_recurrent_support_budget_floor

def individual_vs_joint_recurrent_support_witness :=
  individual_carrying_does_not_imply_joint_carrying

theorem rerouted_path_transfer_strictness_witness :
    Not (EdgeTransferContract
      directReturnNext
      reroutedReturnNext
      rerouteSafe
      rerouteSafe
      rerouteClass) /\
    PathTransferContract
      directReturnNext
      reroutedReturnNext
      rerouteSafe
      rerouteSafe
      rerouteClass /\
    Carries
      rerouteConsequenceSystem
      reroutedReturnNext
      rerouteSafe
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact path_transfer_strictly_relaxes_edge_transfer_witness

theorem strict_support_extension_witness_public :
    ProperSupportSub endpointRerouteClass rerouteClass /\
    Carries
      rerouteConsequenceSystem
      endpointCycleNext
      rerouteSafe
      endpointRerouteClass
      RerouteState.left
      RerouteState.right /\
    ExtensionContract
      endpointCycleNext
      reroutedReturnNext
      rerouteSafe
      endpointRerouteClass
      rerouteClass /\
    Carries
      rerouteConsequenceSystem
      reroutedReturnNext
      rerouteSafe
      rerouteClass
      RerouteState.left
      RerouteState.right := by
  exact strict_support_extension_witness

theorem incomparable_support_lineage_witness_public :
    SupportsIncomparable lineageSourceClass lineageTargetClass /\
    Carries
      lineageConsequenceSystem
      lineageSourceNext
      lineageSafe
      lineageSourceClass
      LineageState.left
      LineageState.right /\
    LineageContract
      lineageTargetNext
      lineageSafe
      lineageTargetClass
      LineageState.left
      LineageState.right /\
    Carries
      lineageConsequenceSystem
      lineageTargetNext
      lineageSafe
      lineageTargetClass
      LineageState.left
      LineageState.right := by
  exact incomparable_support_lineage_witness

theorem successor_distinction_handoff_witness_public :
    Carries
      successorConsequenceSystem
      successorSourceNext
      successorSafe
      successorSourceClass
      SuccessorState.sourceLeft
      SuccessorState.sourceRight /\
    SuccessorContract
      successorConsequenceSystem
      successorTargetNext
      successorSafe
      successorTargetClass
      successorTranslation
      SuccessorState.sourceLeft
      SuccessorState.sourceRight
      SuccessorState.targetLeft
      SuccessorState.targetRight /\
    Carries
      successorConsequenceSystem
      successorTargetNext
      successorSafe
      successorTargetClass
      SuccessorState.targetLeft
      SuccessorState.targetRight := by
  exact successor_distinction_handoff_witness

theorem bounded_family_one_way_loss_witness
    (n : Nat) :
    Carries
      endpointConsequenceSystem
      (boundedCycleNext n)
      boundedCycleSafe
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) /\
    Viable (boundedBrokenDyn n) boundedCycleSafe (0 : Nat) /\
    Viable (boundedBrokenDyn n) boundedCycleSafe (1 : Nat) /\
    InternalPath
      (dynFromNext (boundedBrokenNext n))
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) /\
    Not (InternalPath
      (dynFromNext (boundedBrokenNext n))
      (boundedCycleSupport n)
      (1 : Nat)
      (0 : Nat)) /\
    DestroyedUnder
      endpointConsequenceSystem
      (boundedCycleNext n)
      (boundedBrokenNext n)
      boundedCycleSafe
      boundedCycleSafe
      (boundedCycleSupport n)
      (boundedCycleSupport n)
      (0 : Nat)
      (1 : Nat) := by
  exact parameterized_recurrent_support_loss_witness n

end RecurrentSupportIntegrity
end Trajectory
end OmegaProper
