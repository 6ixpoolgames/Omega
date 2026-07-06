import OmegaProper.Decision.RecoveryAwareCorridor
import OmegaProper.Decision.RecoveryFrameExamples

/-!
OmegaProper.Decision.RecoveryAwareCorridorExamples

Finite witnesses for recovery-aware corridor gates:

* same coarse task success, but correction-register collapse cannot be licensed
  against a recovery-aware corridor;
* an informative probe can be forbidden when every revealing route causes
  nonrecoverable loss of the declared recovery fact.

These are corridor/gate facts, not harm, standing, value, agency, identity, or
rights theorems.
-/

namespace OmegaProper
namespace Decision
namespace RecoveryAwareCorridorExamples

open RecoveryFrame
open RecoveryAwareCorridor
open Trajectory.PredicateFixpoint

/-! ## Recovery-aware self-lobotomy / correction-register gate -/

namespace SelfLobotomyGate

open RecoveryFrameExamples.CorrectionRegisterCollapse

def D : DecisionStructure where
  State := State
  Action := Action
  Step := Step
  Constraint := TaskSuccess

def Allowed (_ : State) (_ : Action) : Prop := True

abbrev Corridor : State -> Prop :=
  RecoveryAwareCorridor D R 0 Allowed

def trivialJustification : CertifiedJustification where
  abstractFact := True
  concreteFact := True
  abstract_holds := trivial
  reflects := fun _ => trivial

private theorem correctable_postfixed :
    Postfixed
      (robustCorridorOp D Allowed (RecoveryRequirement R 0))
      (fun s => s = State.correctable) := by
  intro s hs
  cases hs
  refine ⟨trivial, ?_, Action.preserve, trivial, ?_, ?_⟩
  · exact fact_recoverable_upTo R (by
      intro d
      cases d
      trivial)
  · exact ⟨State.correctable, by simp [D, Step]⟩
  · intro y hStep
    cases y <;> simp [D, Step] at hStep
    rfl

theorem correctable_in_recoveryAwareCorridor :
    Corridor State.correctable :=
  postfixed_le_gfp correctable_postfixed State.correctable rfl

theorem preserve_can_be_licensed :
    LicensedVia D Corridor (fun _ => True) True
      State.correctable Action.preserve := by
  refine Nonempty.intro ?_
  exact
    { justification := trivialJustification
      route_available := trivial
      enabled := ⟨State.correctable, by simp [D, Step]⟩
      corridor_safe := by
        intro y hStep
        cases y <;> simp [D, Step] at hStep
        exact correctable_in_recoveryAwareCorridor
      quotients_certified := trivial }

theorem collapse_cannot_be_licensed :
    Not
      (LicensedVia D Corridor (fun _ => True) True
        State.correctable Action.collapse) := by
  exact action_with_nonrecoverable_successor_not_licensed
    (D := D)
    (R := R)
    (Allowed := Allowed)
    (Available := fun _ => True)
    (quotientsCertified := True)
    (h := 0)
    (x := State.correctable)
    (source := State.correctable)
    (y := State.collapsed)
    (a := Action.collapse)
    (by simp [D, Step])
    correctable_to_collapsed_nonrecoverable_revision_loss

theorem W_same_task_success_but_collapse_unlicensed :
    TaskSuccess State.correctable /\
      TaskSuccess State.collapsed /\
      LicensedVia D Corridor (fun _ => True) True
        State.correctable Action.preserve /\
      Not
        (LicensedVia D Corridor (fun _ => True) True
          State.correctable Action.collapse) := by
  exact ⟨trivial, trivial, preserve_can_be_licensed,
    collapse_cannot_be_licensed⟩

end SelfLobotomyGate

/-! ## Forbidden probe witness -/

namespace ForbiddenProbe

inductive State where
  | unknown
  | stable
  | collapsed
deriving DecidableEq, Repr

inductive Action where
  | wait
  | reveal
deriving DecidableEq, Repr

/-- `reveal` is declared informative, but its only route collapses the fact. -/
def Informative : Action -> Prop
  | Action.reveal => True
  | Action.wait => False

def Step : State -> Action -> State -> Prop
  | State.unknown, Action.wait, State.unknown => True
  | State.unknown, Action.reveal, State.collapsed => True
  | State.stable, Action.wait, State.stable => True
  | State.collapsed, Action.wait, State.collapsed => True
  | _, _, _ => False

def Constraint (_ : State) : Prop := True

def D : DecisionStructure where
  State := State
  Action := Action
  Step := Step
  Constraint := Constraint

def Allowed (_ : State) (_ : Action) : Prop := True

def Fact : State -> Prop
  | State.collapsed => False
  | _ => True

def RepairAllowed : State -> Action -> Prop
  | State.unknown, Action.wait => True
  | State.stable, Action.wait => True
  | State.collapsed, Action.wait => True
  | _, _ => False

def R : RecoveryFrame State Action where
  Step := Step
  RepairAllowed := RepairAllowed
  Fact := Fact
  species := FactSpecies.epistemic

abbrev Corridor : State -> Prop :=
  RecoveryAwareCorridor D R 0 Allowed

def trivialJustification : CertifiedJustification where
  abstractFact := True
  concreteFact := True
  abstract_holds := trivial
  reflects := fun _ => trivial

private theorem unknown_postfixed :
    Postfixed
      (robustCorridorOp D Allowed (RecoveryRequirement R 0))
      (fun s => s = State.unknown) := by
  intro s hs
  cases hs
  refine ⟨trivial, ?_, Action.wait, trivial, ?_, ?_⟩
  · exact fact_recoverable_upTo R (by simp [R, Fact])
  · exact ⟨State.unknown, by simp [D, Step]⟩
  · intro y hStep
    cases y <;> simp [D, Step] at hStep
    rfl

theorem unknown_in_recoveryAwareCorridor :
    Corridor State.unknown :=
  postfixed_le_gfp unknown_postfixed State.unknown rfl

theorem collapsed_not_recoverable_zero :
    Not (RecoverableUpTo R 0 State.collapsed) := by
  intro h
  rcases h with ⟨n, hn, hWithin⟩
  have hn0 : n = 0 := Nat.eq_zero_of_le_zero hn
  subst n
  rcases hWithin with ⟨t, hReach, hFact⟩
  have hEq : State.collapsed = t := repairReach_zero_eq hReach
  subst t
  simp [R, Fact] at hFact

theorem reveal_nonrecoverably_contracts_fact :
    NonrecoverableContraction R 0 State.unknown State.collapsed := by
  exact ⟨by simp [R, Fact], by simp [R, Fact],
    collapsed_not_recoverable_zero⟩

theorem wait_can_be_licensed :
    LicensedVia D Corridor (fun _ => True) True
      State.unknown Action.wait := by
  refine Nonempty.intro ?_
  exact
    { justification := trivialJustification
      route_available := trivial
      enabled := ⟨State.unknown, by simp [D, Step]⟩
      corridor_safe := by
        intro y hStep
        cases y <;> simp [D, Step] at hStep
        exact unknown_in_recoveryAwareCorridor
      quotients_certified := trivial }

theorem reveal_cannot_be_licensed :
    Not
      (LicensedVia D Corridor (fun _ => True) True
        State.unknown Action.reveal) := by
  exact action_with_nonrecoverable_successor_not_licensed
    (D := D)
    (R := R)
    (Allowed := Allowed)
    (Available := fun _ => True)
    (quotientsCertified := True)
    (h := 0)
    (x := State.unknown)
    (source := State.unknown)
    (y := State.collapsed)
    (a := Action.reveal)
    (by simp [D, Step])
    reveal_nonrecoverably_contracts_fact

theorem W_forbidden_probe :
    Informative Action.reveal /\
      LicensedVia D Corridor (fun _ => True) True State.unknown Action.wait /\
      Not
        (LicensedVia D Corridor (fun _ => True) True
          State.unknown Action.reveal) := by
  exact ⟨trivial, wait_can_be_licensed, reveal_cannot_be_licensed⟩

end ForbiddenProbe

end RecoveryAwareCorridorExamples
end Decision
end OmegaProper
