import OmegaProper.Decision.RobustCorridor

/-!
OmegaProper.Decision.RobustCorridorExamples

Tiny corridor example for the ODT0 robust-continuation floor.

`good` can remain in the corridor by choosing `stay`. `fall` exits to `bad`,
which violates the declared constraint and therefore cannot be licensed against
the robust corridor.
-/

namespace OmegaProper
namespace Decision
namespace RobustCorridorExamples

inductive State where
  | good
  | bad
deriving DecidableEq

inductive Action where
  | stay
  | fall
deriving DecidableEq

def Step : State -> Action -> State -> Prop
  | State.good, Action.stay, State.good => True
  | State.good, Action.fall, State.bad => True
  | State.bad, Action.stay, State.bad => True
  | State.bad, Action.fall, State.bad => True
  | _, _, _ => False

def Constraint : State -> Prop
  | State.good => True
  | State.bad => False

def D : DecisionStructure where
  State := State
  Action := Action
  Step := Step
  Constraint := Constraint

def Allowed (_ : State) (_ : Action) : Prop := True

def Requirement (_ : State) : Prop := True

abbrev Corridor : State -> Prop :=
  RobustCorridor D Allowed Requirement

theorem good_in_corridor : Corridor State.good := by
  refine Exists.intro (fun x => x = State.good) ?_
  constructor
  · intro x hx
    cases hx
    exact ⟨trivial, trivial, Action.stay, trivial,
      (Exists.intro State.good (by simp [D, Step])),
      (by
        intro y hStep
        cases y <;> simp [D, Step] at hStep
        rfl)⟩
  · rfl

theorem bad_not_in_corridor : Not (Corridor State.bad) := by
  intro hBad
  exact robustCorridor_sub_constraint D Allowed Requirement
    State.bad hBad

theorem fall_exits_corridor :
    exists y, D.Step State.good Action.fall y /\ Not (Corridor y) := by
  exact ⟨State.bad, (by simp [D, Step]), bad_not_in_corridor⟩

def trivialJustification : CertifiedJustification where
  abstractFact := True
  concreteFact := True
  abstract_holds := trivial
  reflects := fun _ => trivial

theorem stay_can_be_licensed :
    exists a,
      Allowed State.good a /\
      LicensedVia D Corridor (fun _ => True) True State.good a := by
  exact robustCorridor_supplies_license
    good_in_corridor trivialJustification trivial trivial

theorem fall_cannot_be_licensed :
    Not (LicensedVia D Corridor (fun _ => True) True State.good Action.fall) := by
  exact action_with_exit_not_licensed fall_exits_corridor

end RobustCorridorExamples
end Decision
end OmegaProper
