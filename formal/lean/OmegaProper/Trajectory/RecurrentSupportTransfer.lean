import OmegaProper.Trajectory.RecurrentSupportRobustness

/-!
OmegaProper.Trajectory.RecurrentSupportTransfer

Positive transfer contracts for recurrent supports carrying consequence
distinctions.

The loss files show how recurrent carrying can fail. This file records a
matching positive contract: if a changed dynamics preserves the original
internal class edges, does not add exits from the declared support, and
transfers safety on that support, then recurrent support carrying transfers.

This is a same-declared-support theorem. It does not assert object identity,
agency, deformer structure, value, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportTransfer

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRobustness
open RecurrentViableClass
open SupportRestriction
open SupportUnderPerturbation
open SustainingViableClass

universe w k o

/-- Safety transfer on a declared support. -/
def SafeTransfersOn
    {X : Type w}
    (C : X -> Prop)
    (safe0 safe1 : X -> Prop) : Prop :=
  forall x, C x -> safe0 x -> safe1 x

/-- The changed dynamics has no outgoing exits from the declared support. -/
def NoNewExitsFrom
    {X : Type w}
    (Next : X -> X -> Prop)
    (C : X -> Prop) : Prop :=
  forall x y, C x -> Next x y -> C y

/-- Old internal support edges remain available in the changed dynamics. -/
def InternalEdgesPreservedOn
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (C : X -> Prop) : Prop :=
  forall x y, C x -> C y -> Next0 x y -> Next1 x y

/--
Same-support transfer contract for recurrent carrying.

The contract is intentionally structural: safety transfers on the support,
new dynamics cannot exit the support, and old internal support edges are still
present.
-/
def RecurrentSupportTransferContract
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (safe0 safe1 : X -> Prop)
    (C : X -> Prop) : Prop :=
  SafeTransfersOn C safe0 safe1 /\
    NoNewExitsFrom Next1 C /\
    InternalEdgesPreservedOn Next0 Next1 C

def internalPathTransferOfEdges
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C : X -> Prop}
    {x y : X}
    (hEdges : InternalEdgesPreservedOn Next0 Next1 C)
    (hPath : InternalPath (dynFromNext Next0) C x y) :
    InternalPath (dynFromNext Next1) C x y :=
  match hPath with
  | InternalPath.refl hx =>
      InternalPath.refl hx
  | InternalPath.step hx hy hEdge hRest =>
      InternalPath.step
        hx
        hy
        (hEdges _ _ hx hy hEdge)
        (internalPathTransferOfEdges hEdges hRest)

theorem internalPath_transfer_of_edges
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {C : X -> Prop}
    {x y : X}
    (hEdges : InternalEdgesPreservedOn Next0 Next1 C)
    (hPath : InternalPath (dynFromNext Next0) C x y) :
    InternalPath (dynFromNext Next1) C x y := by
  exact internalPathTransferOfEdges hEdges hPath

theorem recurrentViableClass_transfer_of_contract
    {X : Type w}
    {Next0 Next1 : X -> X -> Prop}
    {safe0 safe1 C : X -> Prop}
    (hRec : RecurrentViableClass (dynFromNext Next0) safe0 C)
    (hContract : RecurrentSupportTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentViableClass (dynFromNext Next1) safe1 C := by
  exact And.intro
    (by
      intro x hx
      exact hContract.left x hx (hRec.left x hx))
    (And.intro
      (by
        intro x y hx hStep
        exact hContract.right.left x y hx hStep)
      (And.intro
        (by
          intro x y hx hy
          exact internalPath_transfer_of_edges
            hContract.right.right
            (hRec.right.right.left x y hx hy))
        (by
          intro x hx
          match hRec.right.right.right x hx with
          | Exists.intro y hy =>
              exact Exists.intro y
                (And.intro
                  hy.left
                  (hContract.right.right x y hx hy.left hy.right)))))

theorem supportsMergeSeparatedPair_transfer_of_edges
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next0 C x y)
    (hEdges : InternalEdgesPreservedOn Next0 Next1 C) :
    SupportsMergeSeparatedPair S Next1 C x y := by
  exact And.intro
    hSupport.left
    (And.intro
      hSupport.right.left
      (And.intro
        (internalPath_transfer_of_edges hEdges hSupport.right.right.left)
        (And.intro
          (internalPath_transfer_of_edges hEdges hSupport.right.right.right.left)
          hSupport.right.right.right.right)))

theorem recurrentSupportCarries_transfers_of_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hContract : RecurrentSupportTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentSupportCarries S Next1 safe1 C x y := by
  exact And.intro
    (recurrentViableClass_transfer_of_contract hCarry.left hContract)
    (supportsMergeSeparatedPair_transfer_of_edges
      hCarry.right
      hContract.right.right)

theorem recurrentSupportIntegrity_of_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hContract : RecurrentSupportTransferContract Next0 Next1 safe0 safe1 C) :
    RecurrentSupportIntegrityUnder
      S
      Next0
      Next1
      safe0
      safe1
      C
      C
      x
      y := by
  intro hCarry
  exact recurrentSupportCarries_transfers_of_contract hCarry hContract

/-! ## Tiny finite transfer witness -/

theorem cycle_self_transfer_contract :
    RecurrentSupportTransferContract
      cycleNext
      cycleNext
      cycleSafe
      cycleSafe
      cycleClass := by
  exact And.intro
    (by
      intro x _hx _hSafe
      trivial)
    (And.intro
      (by
        intro x y _hx _hStep
        trivial)
      (by
        intro x y _hx _hy hStep
        exact hStep))

theorem cycle_self_transfer_preserves_recurrent_support :
    RecurrentSupportCarries
      cycleConsequenceSystem
      cycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right := by
  exact recurrentSupportCarries_transfers_of_contract
    cycle_recurrentSupportCarries_left_right
    cycle_self_transfer_contract

theorem cycle_self_transfer_integrity :
    RecurrentSupportIntegrityUnder
      cycleConsequenceSystem
      cycleNext
      cycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right := by
  exact recurrentSupportIntegrity_of_contract
    cycle_self_transfer_contract

end RecurrentSupportTransfer
end Trajectory
end OmegaProper
