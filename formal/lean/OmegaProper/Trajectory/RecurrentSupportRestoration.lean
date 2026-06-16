import OmegaProper.Trajectory.IrreversibleRecurrentSupportLoss
import OmegaProper.Trajectory.RecurrentSupportTransfer

/-!
OmegaProper.Trajectory.RecurrentSupportRestoration

Restoration after recurrent support loss.

The loss witness shows that a one-way dynamic change can destroy recurrent
support carrying. The transfer contract gives sufficient conditions for
preservation. This file combines them: if recurrent carrying is lost under one
changed dynamics, and a later changed dynamics satisfies the transfer contract
from the original recurrent support, then recurrent carrying is restored.

This does not define identity, agency, repair-as-selfhood, deformer structure,
value, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportRestoration

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open DistinctionSupport
open IrreversibleRecurrentSupportLoss
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRobustness
open RecurrentSupportTransfer
open RecurrentViableClass
open SupportRestriction
open SupportUnderPerturbation
open SustainingViableClass

universe w k o

/--
Recurrent support is restored after loss when a loss step is witnessed and a
later dynamics/support again recurrently carries the same declared pair.

The definition is intentionally pair-relative. It is not an identity or object
restoration predicate.
-/
def RecurrentSupportRestoredAfterLoss
    (S : ConsequenceSystem.{w, k, o})
    (Next0 NextLoss NextRestored : S.Fragment -> S.Fragment -> Prop)
    (safe0 safeLoss safeRestored : S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  RecurrentSupportDestroyedUnder S Next0 NextLoss safe0 safeLoss C C x y /\
    RecurrentSupportCarries S NextRestored safeRestored C x y

theorem recurrentSupportRestored_of_loss_and_repairContract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 NextLoss NextRestored : S.Fragment -> S.Fragment -> Prop}
    {safe0 safeLoss safeRestored C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hLoss :
      RecurrentSupportDestroyedUnder S Next0 NextLoss safe0 safeLoss C C x y)
    (hRepair :
      RecurrentSupportTransferContract Next0 NextRestored safe0 safeRestored C) :
    RecurrentSupportRestoredAfterLoss
      S
      Next0
      NextLoss
      NextRestored
      safe0
      safeLoss
      safeRestored
      C
      x
      y := by
  exact And.intro
    hLoss
    (recurrentSupportCarries_transfers_of_contract hLoss.left hRepair)

/-! ## Tiny finite restoration witness -/

/-- Repaired dynamics restores the original two-way cycle. -/
def repairedCycleNext : CycleState -> CycleState -> Prop :=
  cycleNext

def repairedCycleDyn : Dyn where
  State := CycleState
  Next := repairedCycleNext

theorem repairedCycle_transfer_contract_from_baseline :
    RecurrentSupportTransferContract
      cycleNext
      repairedCycleNext
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

theorem repaired_right_path_left :
    InternalPath
      (dynFromNext repairedCycleNext)
      cycleClass
      CycleState.right
      CycleState.left := by
  exact internalPath_single_step trivial trivial trivial

theorem repaired_recurrentSupportCarries_left_right :
    RecurrentSupportCarries
      cycleConsequenceSystem
      repairedCycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right := by
  exact recurrentSupportCarries_transfers_of_contract
    cycle_recurrentSupportCarries_left_right
    repairedCycle_transfer_contract_from_baseline

theorem broken_safeTransfers_from_baseline :
    SafeTransfersOn cycleClass cycleSafe cycleSafe := by
  intro x _hx _hSafe
  trivial

theorem broken_noNewExits_from_baseline :
    NoNewExitsFrom brokenCycleNext cycleClass := by
  intro x y _hx _hStep
  trivial

theorem broken_not_internalEdgesPreserved_from_baseline :
    Not (InternalEdgesPreservedOn cycleNext brokenCycleNext cycleClass) := by
  intro hEdges
  exact hEdges
    CycleState.right
    CycleState.left
    trivial
    trivial
    trivial

theorem broken_not_transfer_contract_from_baseline :
    Not (RecurrentSupportTransferContract
      cycleNext
      brokenCycleNext
      cycleSafe
      cycleSafe
      cycleClass) := by
  intro hContract
  exact broken_not_internalEdgesPreserved_from_baseline hContract.right.right

theorem cycle_recurrentSupport_restored_after_broken_loss :
    RecurrentSupportRestoredAfterLoss
      cycleConsequenceSystem
      cycleNext
      brokenCycleNext
      repairedCycleNext
      cycleSafe
      cycleSafe
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right := by
  exact recurrentSupportRestored_of_loss_and_repairContract
    broken_destroys_recurrent_support
    repairedCycle_transfer_contract_from_baseline

theorem recurrent_support_loss_and_restoration_witness :
    RecurrentSupportCarries
      cycleConsequenceSystem
      cycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right /\
    Not (RecurrentSupportCarries
      cycleConsequenceSystem
      brokenCycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right) /\
    Not (RecurrentSupportTransferContract
      cycleNext
      brokenCycleNext
      cycleSafe
      cycleSafe
      cycleClass) /\
    SafeTransfersOn cycleClass cycleSafe cycleSafe /\
    NoNewExitsFrom brokenCycleNext cycleClass /\
    Not (InternalEdgesPreservedOn cycleNext brokenCycleNext cycleClass) /\
    RecurrentSupportCarries
      cycleConsequenceSystem
      repairedCycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right /\
    RecurrentSupportRestoredAfterLoss
      cycleConsequenceSystem
      cycleNext
      brokenCycleNext
      repairedCycleNext
      cycleSafe
      cycleSafe
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    cycle_recurrentSupportCarries_left_right
    (And.intro
      broken_not_recurrentSupportCarries_left_right
      (And.intro
        broken_not_transfer_contract_from_baseline
        (And.intro
          broken_safeTransfers_from_baseline
          (And.intro
            broken_noNewExits_from_baseline
            (And.intro
              broken_not_internalEdgesPreserved_from_baseline
              (And.intro
                repaired_recurrentSupportCarries_left_right
                cycle_recurrentSupport_restored_after_broken_loss))))))

end RecurrentSupportRestoration
end Trajectory
end OmegaProper
