import OmegaProper.Decision.RecoveryFrame
import OmegaProper.Decision.RobustCorridor

/-!
OmegaProper.Decision.RecoveryAwareCorridor

Recovery-aware corridor bridge.

This file specializes the existing robust-corridor/ODT0 gate to declared
recovery facts. If a corridor's state-local requirement is bounded
recoverability of a declared fact, then any action with a successor exhibiting
nonrecoverable contraction of that fact fails the corridor gate and cannot be
licensed against that corridor.

This does not define harm, value, moral standing, rights, agency, identity, or
Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace RecoveryAwareCorridor

open RecoveryFrame

universe u v w

/-- A state-local requirement saying the declared fact is recoverable by `h`. -/
def RecoveryRequirement {State : Type u} {RepairAction : Type v}
    (R : RecoveryFrame State RepairAction) (h : Nat) : State -> Prop :=
  fun s => RecoverableUpTo R h s

/--
The existing robust corridor instantiated with a recovery requirement.

`DecisionAction` and `RepairAction` are intentionally separate: the action that
causes a transition need not itself be an admissible repair action.
-/
def RecoveryAwareCorridor
    (D : DecisionStructure)
    {RepairAction : Type v}
    (R : RecoveryFrame D.State RepairAction)
    (h : Nat)
    (Allowed : D.State -> D.Action -> Prop) :
    D.State -> Prop :=
  RobustCorridor D Allowed (RecoveryRequirement R h)

theorem nonrecoverable_successor_not_requirement
    {State : Type u} {RepairAction : Type v}
    {R : RecoveryFrame State RepairAction} {h : Nat}
    {source y : State}
    (hLoss : NonrecoverableContraction R h source y) :
    Not (RecoveryRequirement R h y) :=
  nonrecoverableContraction_not_recoverable hLoss

theorem nonrecoverable_successor_not_corridor
    {D : DecisionStructure}
    {RepairAction : Type v}
    {R : RecoveryFrame D.State RepairAction}
    {Allowed : D.State -> D.Action -> Prop}
    {h : Nat} {source y : D.State}
    (hLoss : NonrecoverableContraction R h source y) :
    Not (RecoveryAwareCorridor D R h Allowed y) := by
  intro hy
  exact nonrecoverable_successor_not_requirement hLoss
    (robustCorridor_sub_requirement D Allowed (RecoveryRequirement R h) y hy)

/--
If an action has a successor where the declared recovery fact is
nonrecoverably contracted, then it cannot be licensed against the
recovery-aware corridor.
-/
theorem action_with_nonrecoverable_successor_not_licensed
    {D : DecisionStructure}
    {RepairAction : Type v}
    {R : RecoveryFrame D.State RepairAction}
    {Allowed : D.State -> D.Action -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {h : Nat} {x source y : D.State} {a : D.Action}
    (hStep : D.Step x a y)
    (hLoss : NonrecoverableContraction R h source y) :
    Not
      (LicensedVia D (RecoveryAwareCorridor D R h Allowed)
        Available quotientsCertified x a) := by
  exact action_with_exit_not_licensed
    (D := D)
    (Allowed := Allowed)
    (Requirement := RecoveryRequirement R h)
    (Available := Available)
    (quotientsCertified := quotientsCertified)
    (x := x)
    (a := a)
    ⟨y, hStep, nonrecoverable_successor_not_corridor
      (D := D) (R := R) (Allowed := Allowed) hLoss⟩

end RecoveryAwareCorridor
end Decision
end OmegaProper
