import OmegaProper.Decision.RecoveryAwareCorridor

/-!
OmegaProper.Decision.RecoveryLossStress

Finite stress witnesses for local-vs-joint nonrecoverable loss.

The point is deliberately below "harm": a locally total nonrecoverable
contraction can preserve a declared joint recovery fact, while local persistence
can coexist with nonrecoverable contraction of the joint fact. This blocks a
naive local-only loss proxy.

This file does not define harm, moral standing, patienthood, rights, value,
agency, identity, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace RecoveryLossStress

open RecoveryFrame
open RecoveryAwareCorridor
open Trajectory.PredicateFixpoint

inductive State where
  | whole
  | sacrifice
  | cancer
deriving DecidableEq, Repr

inductive Action where
  | sacrificeMove
  | cancerMove
  | idle
deriving DecidableEq, Repr

def Step : State -> Action -> State -> Prop
  | State.whole, Action.sacrificeMove, State.sacrifice => True
  | State.whole, Action.cancerMove, State.cancer => True
  | State.whole, Action.idle, State.whole => True
  | State.sacrifice, Action.idle, State.sacrifice => True
  | State.cancer, Action.idle, State.cancer => True
  | _, _, _ => False

def Constraint (_ : State) : Prop := True

def D : DecisionStructure where
  State := State
  Action := Action
  Step := Step
  Constraint := Constraint

def Allowed (_ : State) (_ : Action) : Prop := True

def LocalFact : State -> Prop
  | State.sacrifice => False
  | _ => True

def JointFact : State -> Prop
  | State.cancer => False
  | _ => True

def RepairAllowed : State -> Action -> Prop
  | State.whole, Action.idle => True
  | State.sacrifice, Action.idle => True
  | State.cancer, Action.idle => True
  | _, _ => False

def LocalFrame : RecoveryFrame State Action where
  Step := Step
  RepairAllowed := RepairAllowed
  Fact := LocalFact
  species := FactSpecies.state

def JointFrame : RecoveryFrame State Action where
  Step := Step
  RepairAllowed := RepairAllowed
  Fact := JointFact
  species := FactSpecies.state

abbrev LocalCorridor : State -> Prop :=
  RecoveryAwareCorridor D LocalFrame 0 Allowed

abbrev JointCorridor : State -> Prop :=
  RecoveryAwareCorridor D JointFrame 0 Allowed

def trivialJustification : CertifiedJustification where
  abstractFact := True
  concreteFact := True
  abstract_holds := trivial
  reflects := fun _ => trivial

private theorem whole_joint_postfixed :
    Postfixed
      (robustCorridorOp D Allowed (RecoveryRequirement JointFrame 0))
      (fun s => s = State.whole \/ s = State.sacrifice) := by
  intro s hs
  rcases hs with hWhole | hSacrifice
  · cases hWhole
    refine ⟨trivial, ?_, Action.sacrificeMove, trivial, ?_, ?_⟩
    · exact fact_recoverable_upTo JointFrame (by simp [JointFrame, JointFact])
    · exact ⟨State.sacrifice, by simp [D, Step]⟩
    · intro y hStep
      cases y <;> simp [D, Step] at hStep
      exact Or.inr rfl
  · cases hSacrifice
    refine ⟨trivial, ?_, Action.idle, trivial, ?_, ?_⟩
    · exact fact_recoverable_upTo JointFrame (by simp [JointFrame, JointFact])
    · exact ⟨State.sacrifice, by simp [D, Step]⟩
    · intro y hStep
      cases y <;> simp [D, Step] at hStep
      exact Or.inr rfl

private theorem whole_local_postfixed :
    Postfixed
      (robustCorridorOp D Allowed (RecoveryRequirement LocalFrame 0))
      (fun s => s = State.whole \/ s = State.cancer) := by
  intro s hs
  rcases hs with hWhole | hCancer
  · cases hWhole
    refine ⟨trivial, ?_, Action.cancerMove, trivial, ?_, ?_⟩
    · exact fact_recoverable_upTo LocalFrame (by simp [LocalFrame, LocalFact])
    · exact ⟨State.cancer, by simp [D, Step]⟩
    · intro y hStep
      cases y <;> simp [D, Step] at hStep
      exact Or.inr rfl
  · cases hCancer
    refine ⟨trivial, ?_, Action.idle, trivial, ?_, ?_⟩
    · exact fact_recoverable_upTo LocalFrame (by simp [LocalFrame, LocalFact])
    · exact ⟨State.cancer, by simp [D, Step]⟩
    · intro y hStep
      cases y <;> simp [D, Step] at hStep
      exact Or.inr rfl

theorem whole_in_jointCorridor :
    JointCorridor State.whole :=
  postfixed_le_gfp whole_joint_postfixed State.whole (Or.inl rfl)

theorem whole_in_localCorridor :
    LocalCorridor State.whole :=
  postfixed_le_gfp whole_local_postfixed State.whole (Or.inl rfl)

theorem sacrifice_joint_recoverable :
    RecoverableUpTo JointFrame 0 State.sacrifice :=
  fact_recoverable_upTo JointFrame (by simp [JointFrame, JointFact])

theorem cancer_local_recoverable :
    RecoverableUpTo LocalFrame 0 State.cancer :=
  fact_recoverable_upTo LocalFrame (by simp [LocalFrame, LocalFact])

theorem sacrifice_local_not_recoverable :
    Not (RecoverableUpTo LocalFrame 0 State.sacrifice) := by
  intro h
  rcases h with ⟨n, hn, hWithin⟩
  have hn0 : n = 0 := Nat.eq_zero_of_le_zero hn
  subst n
  rcases hWithin with ⟨t, hReach, hFact⟩
  have hEq : State.sacrifice = t := repairReach_zero_eq hReach
  subst t
  simp [LocalFrame, LocalFact] at hFact

theorem cancer_joint_not_recoverable :
    Not (RecoverableUpTo JointFrame 0 State.cancer) := by
  intro h
  rcases h with ⟨n, hn, hWithin⟩
  have hn0 : n = 0 := Nat.eq_zero_of_le_zero hn
  subst n
  rcases hWithin with ⟨t, hReach, hFact⟩
  have hEq : State.cancer = t := repairReach_zero_eq hReach
  subst t
  simp [JointFrame, JointFact] at hFact

theorem sacrifice_local_nonrecoverable_contraction :
    NonrecoverableContraction LocalFrame 0 State.whole State.sacrifice := by
  exact ⟨by simp [LocalFrame, LocalFact],
    by simp [LocalFrame, LocalFact],
    sacrifice_local_not_recoverable⟩

theorem cancer_joint_nonrecoverable_contraction :
    NonrecoverableContraction JointFrame 0 State.whole State.cancer := by
  exact ⟨by simp [JointFrame, JointFact],
    by simp [JointFrame, JointFact],
    cancer_joint_not_recoverable⟩

theorem sacrifice_licensed_by_jointCorridor :
    LicensedVia D JointCorridor (fun _ => True) True
      State.whole Action.sacrificeMove := by
  refine Nonempty.intro ?_
  exact
    { justification := trivialJustification
      route_available := trivial
      enabled := ⟨State.sacrifice, by simp [D, Step]⟩
      corridor_safe := by
        intro y hStep
        cases y <;> simp [D, Step] at hStep
        exact postfixed_le_gfp whole_joint_postfixed
          State.sacrifice (Or.inr rfl)
      quotients_certified := trivial }

theorem sacrifice_refused_by_localCorridor :
    Not
      (LicensedVia D LocalCorridor (fun _ => True) True
        State.whole Action.sacrificeMove) := by
  exact action_with_nonrecoverable_successor_not_licensed
    (D := D)
    (R := LocalFrame)
    (Allowed := Allowed)
    (Available := fun _ => True)
    (quotientsCertified := True)
    (h := 0)
    (x := State.whole)
    (source := State.whole)
    (y := State.sacrifice)
    (a := Action.sacrificeMove)
    (by simp [D, Step])
    sacrifice_local_nonrecoverable_contraction

theorem cancer_licensed_by_localCorridor :
    LicensedVia D LocalCorridor (fun _ => True) True
      State.whole Action.cancerMove := by
  refine Nonempty.intro ?_
  exact
    { justification := trivialJustification
      route_available := trivial
      enabled := ⟨State.cancer, by simp [D, Step]⟩
      corridor_safe := by
        intro y hStep
        cases y <;> simp [D, Step] at hStep
        exact postfixed_le_gfp whole_local_postfixed State.cancer (Or.inr rfl)
      quotients_certified := trivial }

theorem cancer_refused_by_jointCorridor :
    Not
      (LicensedVia D JointCorridor (fun _ => True) True
        State.whole Action.cancerMove) := by
  exact action_with_nonrecoverable_successor_not_licensed
    (D := D)
    (R := JointFrame)
    (Allowed := Allowed)
    (Available := fun _ => True)
    (quotientsCertified := True)
    (h := 0)
    (x := State.whole)
    (source := State.whole)
    (y := State.cancer)
    (a := Action.cancerMove)
    (by simp [D, Step])
    cancer_joint_nonrecoverable_contraction

/--
Stress witness:

* the sacrifice move is locally nonrecoverable but joint-corridor licensed;
* the cancer move locally persists but is joint-corridor refused.

This blocks treating local nonrecoverable contraction as a complete harm proxy.
-/
theorem W_sacrifice_cancer_joint_stress :
    NonrecoverableContraction LocalFrame 0 State.whole State.sacrifice /\
      RecoverableUpTo JointFrame 0 State.sacrifice /\
      LicensedVia D JointCorridor (fun _ => True) True
        State.whole Action.sacrificeMove /\
      LicensedVia D LocalCorridor (fun _ => True) True
        State.whole Action.cancerMove /\
      Not
        (LicensedVia D JointCorridor (fun _ => True) True
          State.whole Action.cancerMove) := by
  exact ⟨sacrifice_local_nonrecoverable_contraction,
    sacrifice_joint_recoverable,
    sacrifice_licensed_by_jointCorridor,
    cancer_licensed_by_localCorridor,
    cancer_refused_by_jointCorridor⟩

end RecoveryLossStress
end Decision
end OmegaProper
