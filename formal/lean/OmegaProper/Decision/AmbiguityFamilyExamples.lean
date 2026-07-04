import OmegaProper.Decision.AmbiguityFamily

/-!
OmegaProper.Decision.AmbiguityFamilyExamples

W1 shared-action strictness witness.

The start state is inside each per-model robust corridor, because each model
has some safe action. It is outside the ambiguity RVK, because no single shared
action is safe across both models.
-/

namespace OmegaProper
namespace Decision
namespace AmbiguityFamilyExamples

open AmbiguityFamily
open Trajectory.PredicateFixpoint

inductive Model where
  | m0
  | m1
deriving DecidableEq

instance : Fintype Model where
  elems := {Model.m0, Model.m1}
  complete := by
    intro i
    cases i <;> simp

inductive State where
  | start
  | ok
  | bad
deriving DecidableEq

inductive Action where
  | a
  | b
deriving DecidableEq

def Step : Model -> State -> Action -> State -> Prop
  | Model.m0, State.start, Action.a, State.ok => True
  | Model.m0, State.start, Action.b, State.bad => True
  | Model.m1, State.start, Action.a, State.bad => True
  | Model.m1, State.start, Action.b, State.ok => True
  | _, State.ok, _, State.ok => True
  | _, State.bad, _, State.bad => True
  | _, _, _, _ => False

def Constraint : State -> Prop
  | State.start => True
  | State.ok => True
  | State.bad => False

def F : AmbFamily State Action where
  Model := Model
  modelFinite := inferInstance
  modelNonempty := ⟨Model.m0⟩
  Step := Step
  Constraint := Constraint

def Allowed (_ : State) (_ : Action) : Prop := True

def Requirement (_ : State) : Prop := True

abbrev SharedRVK : State -> Prop :=
  RVK F Allowed Requirement

abbrev PerModelCorridor (i : Model) : State -> Prop :=
  RobustCorridor (perModelDecision F i) Allowed Requirement

theorem bad_not_shared_rvk :
    Not (SharedRVK State.bad) := by
  intro hBad
  exact rvk_sub_constraint F Allowed Requirement State.bad hBad

theorem start_not_shared_rvk :
    Not (SharedRVK State.start) := by
  intro hStart
  rcases rvk_has_shared_action F Allowed Requirement hStart with
    ⟨act, _hAllowed, _hEnabled, hSafe⟩
  cases act
  · exact bad_not_shared_rvk
      (hSafe Model.m1 State.bad (by simp [F, Step]))
  · exact bad_not_shared_rvk
      (hSafe Model.m0 State.bad (by simp [F, Step]))

private theorem m0_postfixed :
    Postfixed
      (robustCorridorOp (perModelDecision F Model.m0) Allowed Requirement)
      (fun x => x = State.start \/ x = State.ok) := by
  intro x hx
  cases hx with
  | inl hStart =>
      cases hStart
      exact ⟨trivial, trivial, Action.a, trivial,
        ⟨State.ok, by simp [F, Step, perModelDecision]⟩,
        (by
          intro y hStep
          cases y <;> simp [F, Step, perModelDecision] at hStep
          · exact Or.inr rfl)⟩
  | inr hOk =>
      cases hOk
      exact ⟨trivial, trivial, Action.a, trivial,
        ⟨State.ok, by simp [F, Step, perModelDecision]⟩,
        (by
          intro y hStep
          cases y <;> simp [F, Step, perModelDecision] at hStep
          exact Or.inr rfl)⟩

private theorem m1_postfixed :
    Postfixed
      (robustCorridorOp (perModelDecision F Model.m1) Allowed Requirement)
      (fun x => x = State.start \/ x = State.ok) := by
  intro x hx
  cases hx with
  | inl hStart =>
      cases hStart
      exact ⟨trivial, trivial, Action.b, trivial,
        ⟨State.ok, by simp [F, Step, perModelDecision]⟩,
        (by
          intro y hStep
          cases y <;> simp [F, Step, perModelDecision] at hStep
          · exact Or.inr rfl)⟩
  | inr hOk =>
      cases hOk
      exact ⟨trivial, trivial, Action.a, trivial,
        ⟨State.ok, by simp [F, Step, perModelDecision]⟩,
        (by
          intro y hStep
          cases y <;> simp [F, Step, perModelDecision] at hStep
          exact Or.inr rfl)⟩

theorem start_in_m0_corridor :
    PerModelCorridor Model.m0 State.start :=
  postfixed_le_gfp m0_postfixed State.start (Or.inl rfl)

theorem start_in_m1_corridor :
    PerModelCorridor Model.m1 State.start :=
  postfixed_le_gfp m1_postfixed State.start (Or.inl rfl)

theorem start_in_each_perModelCorridor :
    forall i : Model, PerModelCorridor i State.start := by
  intro i
  cases i
  · exact start_in_m0_corridor
  · exact start_in_m1_corridor

theorem W1_intersection_contains_start_but_not_shared_rvk :
    (forall i : Model, PerModelCorridor i State.start) /\
      Not (SharedRVK State.start) :=
  ⟨start_in_each_perModelCorridor, start_not_shared_rvk⟩

end AmbiguityFamilyExamples
end Decision
end OmegaProper
