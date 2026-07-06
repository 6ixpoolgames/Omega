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
open Trajectory.PredicateFixpoint

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

/--
Recovery-frame reflection: every bounded recovery fact accepted by the believed
frame is accepted by the true frame.

This is the non-fabrication condition needed to transport recovery-aware
licenses from a believed register to a true register.
-/
def RecoveryFrameReflects {State : Type u} {RepairAction : Type v}
    (Believed True : RecoveryFrame State RepairAction) (h : Nat) : Prop :=
  forall s, RecoveryRequirement Believed h s -> RecoveryRequirement True h s

theorem recoveryAwareCorridor_reflects_of_recoveryFrameReflects
    {D : DecisionStructure}
    {RepairAction : Type v}
    {Believed True : RecoveryFrame D.State RepairAction}
    {Allowed : D.State -> D.Action -> Prop}
    {h : Nat}
    (hReflect : RecoveryFrameReflects Believed True h) :
    PSub
      (RecoveryAwareCorridor D Believed h Allowed)
      (RecoveryAwareCorridor D True h Allowed) := by
  intro x hx
  rcases hx with ⟨p, hPost, hxP⟩
  apply postfixed_le_gfp
  · intro z hz
    rcases hPost z hz with ⟨hConstraint, hReq, a, hAllowed, hEnabled, hSafe⟩
    exact ⟨hConstraint, hReflect z hReq, a, hAllowed, hEnabled, hSafe⟩
  · exact hxP

/--
If the believed recovery frame reflects into the true one, any license against
the believed recovery-aware corridor is also a license against the true
recovery-aware corridor.
-/
theorem recoveryFrame_reflection_preserves_license
    {D : DecisionStructure}
    {RepairAction : Type v}
    {Believed True : RecoveryFrame D.State RepairAction}
    {Allowed : D.State -> D.Action -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {h : Nat} {x : D.State} {a : D.Action}
    (hReflect : RecoveryFrameReflects Believed True h)
    (L :
      LicensedVia D (RecoveryAwareCorridor D Believed h Allowed)
        Available quotientsCertified x a) :
    LicensedVia D (RecoveryAwareCorridor D True h Allowed)
        Available quotientsCertified x a := by
  rcases L with ⟨cert⟩
  exact ⟨
    { justification := cert.justification
      route_available := cert.route_available
      enabled := cert.enabled
      corridor_safe := by
        intro y hStep
        exact recoveryAwareCorridor_reflects_of_recoveryFrameReflects
          (D := D) (Believed := Believed) (True := True)
          (Allowed := Allowed) hReflect y (cert.corridor_safe y hStep)
      quotients_certified := cert.quotients_certified }⟩

end RecoveryAwareCorridor
end Decision
end OmegaProper
