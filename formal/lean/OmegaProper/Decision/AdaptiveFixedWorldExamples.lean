import OmegaProper.Decision.AdaptiveFixedWorld

/-!
OmegaProper.Decision.AdaptiveFixedWorldExamples

Strictness witnesses for the adaptive fixed-world lift.

The learnable witness separates switching ambiguity from fixed-world ambiguity:
the concrete start state is outside the switching RVK, while the information
state with both models possible is inside the adaptive lifted kernel because a
safe probe identifies the model.
-/

namespace OmegaProper
namespace Decision
namespace AdaptiveFixedWorldExamples

open AmbiguityFamily
open AdaptiveFixedWorld
open Trajectory.PredicateFixpoint

namespace Learnable

inductive Model where
  | left
  | right
deriving DecidableEq

instance : Fintype Model where
  elems := {Model.left, Model.right}
  complete := by
    intro i
    cases i <;> simp

inductive State where
  | start
  | leftSafe
  | rightSafe
  | bad
deriving DecidableEq

inductive Action where
  | probe
  | keepLeft
  | keepRight
deriving DecidableEq

def Step : Model -> State -> Action -> State -> Prop
  | Model.left, State.start, Action.probe, State.leftSafe => True
  | Model.right, State.start, Action.probe, State.rightSafe => True
  | _, State.start, Action.keepLeft, State.bad => True
  | _, State.start, Action.keepRight, State.bad => True
  | Model.left, State.leftSafe, Action.keepLeft, State.leftSafe => True
  | Model.left, State.leftSafe, Action.probe, State.bad => True
  | Model.left, State.leftSafe, Action.keepRight, State.bad => True
  | Model.right, State.leftSafe, _, State.bad => True
  | Model.right, State.rightSafe, Action.keepRight, State.rightSafe => True
  | Model.right, State.rightSafe, Action.probe, State.bad => True
  | Model.right, State.rightSafe, Action.keepLeft, State.bad => True
  | Model.left, State.rightSafe, _, State.bad => True
  | _, State.bad, _, State.bad => True
  | _, _, _, _ => False

def Constraint : State -> Prop
  | State.bad => False
  | _ => True

def F : AmbFamily State Action where
  Model := Model
  modelFinite := inferInstance
  modelNonempty := ⟨Model.left⟩
  Step := Step
  Constraint := Constraint

def Allowed (_ : State) (_ : Action) : Prop := True

def Requirement (_ : State) : Prop := True

abbrev SharedRVK : State -> Prop :=
  RVK F Allowed Requirement

abbrev AK : InfoState F -> Prop :=
  AdaptiveKernel F Allowed Requirement

def allModels (_ : Model) : Prop := True

def onlyLeft : Model -> Prop
  | Model.left => True
  | Model.right => False

def onlyRight : Model -> Prop
  | Model.left => False
  | Model.right => True

def startInfo : InfoState F where
  state := State.start
  possible := allModels

def leftInfo : InfoState F where
  state := State.leftSafe
  possible := onlyLeft

def rightInfo : InfoState F where
  state := State.rightSafe
  possible := onlyRight

def InfoMatches (s : State) (P : Model -> Prop) (info : InfoState F) : Prop :=
  info.state = s /\ forall i : Model, info.possible i <-> P i

def GoodInfo (info : InfoState F) : Prop :=
  InfoMatches State.start allModels info \/
    InfoMatches State.leftSafe onlyLeft info \/
      InfoMatches State.rightSafe onlyRight info

theorem startInfo_good : GoodInfo startInfo := by
  exact Or.inl ⟨rfl, by intro i; cases i <;> simp [startInfo, allModels]⟩

theorem bad_not_shared_rvk :
    Not (SharedRVK State.bad) := by
  intro hBad
  exact rvk_sub_constraint F Allowed Requirement State.bad hBad

theorem leftSafe_not_shared_rvk :
    Not (SharedRVK State.leftSafe) := by
  intro hLeft
  rcases rvk_has_shared_action F Allowed Requirement hLeft with
    ⟨a, _hAllowed, _hEnabled, hSafe⟩
  cases a <;>
    exact bad_not_shared_rvk
      (hSafe Model.right State.bad (by simp [F, Step]))

theorem rightSafe_not_shared_rvk :
    Not (SharedRVK State.rightSafe) := by
  intro hRight
  rcases rvk_has_shared_action F Allowed Requirement hRight with
    ⟨a, _hAllowed, _hEnabled, hSafe⟩
  cases a <;>
    exact bad_not_shared_rvk
      (hSafe Model.left State.bad (by simp [F, Step]))

theorem start_not_switching_rvk :
    Not (SharedRVK State.start) := by
  intro hStart
  rcases rvk_has_shared_action F Allowed Requirement hStart with
    ⟨a, _hAllowed, _hEnabled, hSafe⟩
  cases a
  · exact leftSafe_not_shared_rvk
      (hSafe Model.left State.leftSafe (by simp [F, Step]))
  · exact bad_not_shared_rvk
      (hSafe Model.left State.bad (by simp [F, Step]))
  · exact bad_not_shared_rvk
      (hSafe Model.left State.bad (by simp [F, Step]))

private theorem start_probe_enabled
    {info : InfoState F}
    (hState : info.state = State.start)
    (_hPossible : forall i : Model, info.possible i <-> allModels i) :
    liftedAllowed F Allowed info Action.probe := by
  constructor
  · trivial
  · intro i _hi
    cases i
    · exact ⟨State.leftSafe, by rw [hState]; simp [F, Step]⟩
    · exact ⟨State.rightSafe, by rw [hState]; simp [F, Step]⟩

private theorem left_keep_enabled
    {info : InfoState F}
    (hState : info.state = State.leftSafe)
    (hPossible : forall i : Model, info.possible i <-> onlyLeft i) :
    liftedAllowed F Allowed info Action.keepLeft := by
  constructor
  · trivial
  · intro i hi
    cases i
    · exact ⟨State.leftSafe, by rw [hState]; simp [F, Step]⟩
    · have hFalse : False := by
        simpa [onlyLeft] using (hPossible Model.right).mp hi
      exact False.elim hFalse

private theorem right_keep_enabled
    {info : InfoState F}
    (hState : info.state = State.rightSafe)
    (hPossible : forall i : Model, info.possible i <-> onlyRight i) :
    liftedAllowed F Allowed info Action.keepRight := by
  constructor
  · trivial
  · intro i hi
    cases i
    · have hFalse : False := by
        simpa [onlyRight] using (hPossible Model.left).mp hi
      exact False.elim hFalse
    · exact ⟨State.rightSafe, by rw [hState]; simp [F, Step]⟩

private theorem start_probe_has_successor
    {info : InfoState F}
    (hState : info.state = State.start)
    (hPossible : forall i : Model, info.possible i <-> allModels i) :
    exists next : InfoState F, LiftedStep F info Action.probe next := by
  refine ⟨leftInfo, Model.left, State.leftSafe, ?_, ?_, rfl, ?_⟩
  · exact (hPossible Model.left).mpr trivial
  · rw [hState]
    simp [F, Step]
  · intro j
    cases j <;>
      simp [leftInfo, onlyLeft, soundUpdate, F, Step, hState,
        (hPossible Model.left).mpr trivial,
        (hPossible Model.right).mpr trivial]

private theorem left_keep_has_successor
    {info : InfoState F}
    (hState : info.state = State.leftSafe)
    (hPossible : forall i : Model, info.possible i <-> onlyLeft i) :
    exists next : InfoState F, LiftedStep F info Action.keepLeft next := by
  refine ⟨leftInfo, Model.left, State.leftSafe, ?_, ?_, rfl, ?_⟩
  · exact (hPossible Model.left).mpr trivial
  · rw [hState]
    simp [F, Step]
  · intro j
    cases j <;>
      simp [leftInfo, onlyLeft, soundUpdate, F, Step, hState,
        (hPossible Model.left).mpr trivial] at *

private theorem right_keep_has_successor
    {info : InfoState F}
    (hState : info.state = State.rightSafe)
    (hPossible : forall i : Model, info.possible i <-> onlyRight i) :
    exists next : InfoState F, LiftedStep F info Action.keepRight next := by
  refine ⟨rightInfo, Model.right, State.rightSafe, ?_, ?_, rfl, ?_⟩
  · exact (hPossible Model.right).mpr trivial
  · rw [hState]
    simp [F, Step]
  · intro j
    cases j <;>
      simp [rightInfo, onlyRight, soundUpdate, F, Step, hState,
        (hPossible Model.right).mpr trivial] at *

private theorem start_probe_safe
    {info next : InfoState F}
    (hState : info.state = State.start)
    (hPossible : forall i : Model, info.possible i <-> allModels i)
    (hLift : LiftedStep F info Action.probe next) :
    GoodInfo next := by
  rcases hLift with ⟨i, observed, _hi, hStep, hNextState, hNextPossible⟩
  rw [hState] at hStep
  cases i <;> cases observed <;> simp [F, Step] at hStep
  · exact Or.inr (Or.inl ⟨hNextState, by
      intro j
      cases j <;>
        simp [onlyLeft, soundUpdate, F, Step, hState,
          (hPossible Model.left).mpr trivial,
          (hPossible Model.right).mpr trivial,
          hNextPossible]⟩)
  · exact Or.inr (Or.inr ⟨hNextState, by
      intro j
      cases j <;>
        simp [onlyRight, soundUpdate, F, Step, hState,
          (hPossible Model.left).mpr trivial,
          (hPossible Model.right).mpr trivial,
          hNextPossible]⟩)

private theorem left_keep_safe
    {info next : InfoState F}
    (hState : info.state = State.leftSafe)
    (hPossible : forall i : Model, info.possible i <-> onlyLeft i)
    (hLift : LiftedStep F info Action.keepLeft next) :
    GoodInfo next := by
  rcases hLift with ⟨i, observed, hi, hStep, hNextState, hNextPossible⟩
  have hiLeft : i = Model.left := by
    cases i
    · rfl
    · have hFalse : False := by
        simpa [onlyLeft] using (hPossible Model.right).mp hi
      exact False.elim hFalse
  cases hiLeft
  rw [hState] at hStep
  cases observed <;> simp [F, Step] at hStep
  exact Or.inr (Or.inl ⟨hNextState, by
    intro j
    cases j <;>
      simp [onlyLeft, soundUpdate, F, Step, hState,
        (hPossible Model.left).mpr trivial,
        hNextPossible]⟩)

private theorem right_keep_safe
    {info next : InfoState F}
    (hState : info.state = State.rightSafe)
    (hPossible : forall i : Model, info.possible i <-> onlyRight i)
    (hLift : LiftedStep F info Action.keepRight next) :
    GoodInfo next := by
  rcases hLift with ⟨i, observed, hi, hStep, hNextState, hNextPossible⟩
  have hiRight : i = Model.right := by
    cases i
    · have hFalse : False := by
        simpa [onlyRight] using (hPossible Model.left).mp hi
      exact False.elim hFalse
    · rfl
  cases hiRight
  rw [hState] at hStep
  cases observed <;> simp [F, Step] at hStep
  exact Or.inr (Or.inr ⟨hNextState, by
    intro j
    cases j <;>
      simp [onlyRight, soundUpdate, F, Step, hState,
        (hPossible Model.right).mpr trivial,
        hNextPossible]⟩)

private theorem good_postfixed :
    Postfixed
      (robustCorridorOp (liftedDecision F) (liftedAllowed F Allowed)
        (liftedRequirement F Requirement))
      GoodInfo := by
  intro info hInfo
  rcases hInfo with hStart | hLeft | hRight
  · rcases hStart with ⟨hState, hPossible⟩
    refine ⟨?_, trivial, Action.probe,
      start_probe_enabled hState hPossible,
      start_probe_has_successor hState hPossible,
      ?_⟩
    · exact ⟨by rw [hState]; trivial, ⟨Model.left, (hPossible Model.left).mpr trivial⟩⟩
    · intro next hLift
      exact start_probe_safe hState hPossible hLift
  · rcases hLeft with ⟨hState, hPossible⟩
    refine ⟨?_, trivial, Action.keepLeft,
      left_keep_enabled hState hPossible,
      left_keep_has_successor hState hPossible,
      ?_⟩
    · exact ⟨by rw [hState]; trivial, ⟨Model.left, (hPossible Model.left).mpr trivial⟩⟩
    · intro next hLift
      exact left_keep_safe hState hPossible hLift
  · rcases hRight with ⟨hState, hPossible⟩
    refine ⟨?_, trivial, Action.keepRight,
      right_keep_enabled hState hPossible,
      right_keep_has_successor hState hPossible,
      ?_⟩
    · exact ⟨by rw [hState]; trivial, ⟨Model.right, (hPossible Model.right).mpr trivial⟩⟩
    · intro next hLift
      exact right_keep_safe hState hPossible hLift

theorem startInfo_in_adaptiveKernel :
    AK startInfo :=
  postfixed_le_gfp good_postfixed startInfo startInfo_good

theorem W_learnable_adaptive_strictness :
    Not (SharedRVK State.start) /\ AK startInfo :=
  ⟨start_not_switching_rvk, startInfo_in_adaptiveKernel⟩

end Learnable

namespace Unlearnable

inductive Model where
  | left
  | right
deriving DecidableEq

instance : Fintype Model where
  elems := {Model.left, Model.right}
  complete := by
    intro i
    cases i <;> simp

inductive State where
  | start
  | leftSafe
  | rightSafe
  | bad
deriving DecidableEq

inductive Action where
  | chooseLeft
  | chooseRight
  | probe
deriving DecidableEq

def Step : Model -> State -> Action -> State -> Prop
  | Model.left, State.start, Action.chooseLeft, State.leftSafe => True
  | Model.left, State.start, Action.chooseRight, State.bad => True
  | Model.left, State.start, Action.probe, State.bad => True
  | Model.right, State.start, Action.chooseLeft, State.bad => True
  | Model.right, State.start, Action.chooseRight, State.rightSafe => True
  | Model.right, State.start, Action.probe, State.rightSafe => True
  | Model.left, State.leftSafe, Action.chooseLeft, State.leftSafe => True
  | Model.left, State.leftSafe, _, State.bad => True
  | Model.right, State.rightSafe, Action.chooseRight, State.rightSafe => True
  | Model.right, State.rightSafe, _, State.bad => True
  | _, State.bad, _, State.bad => True
  | _, _, _, _ => False

def Constraint : State -> Prop
  | State.bad => False
  | _ => True

def F : AmbFamily State Action where
  Model := Model
  modelFinite := inferInstance
  modelNonempty := ⟨Model.left⟩
  Step := Step
  Constraint := Constraint

def Allowed (_ : State) (_ : Action) : Prop := True

def Requirement (_ : State) : Prop := True

abbrev AK : InfoState F -> Prop :=
  AdaptiveKernel F Allowed Requirement

def allModels (_ : Model) : Prop := True

def startInfo : InfoState F where
  state := State.start
  possible := allModels

theorem bad_not_adaptiveKernel
    {info : InfoState F}
    (hBad : info.state = State.bad) :
    Not (AK info) := by
  intro hInfo
  have hConstraint :=
    adaptiveKernel_sub_base_constraint F Allowed Requirement info hInfo
  simp [F, Constraint, hBad] at hConstraint

theorem startInfo_not_adaptiveKernel :
    Not (AK startInfo) := by
  intro hStart
  rcases adaptiveKernel_has_action F Allowed Requirement hStart with
    ⟨a, _hAllowed, _hEnabled, hSafe⟩
  cases a
  · have hExit : exists next : InfoState F,
        LiftedStep F startInfo Action.chooseLeft next /\ next.state = State.bad := by
      refine ⟨{ state := State.bad, possible := fun i => i = Model.right },
        ?_, rfl⟩
      refine ⟨Model.right, State.bad, trivial, by simp [F, Step, startInfo],
        rfl, ?_⟩
      intro j
      cases j <;> simp [soundUpdate, F, Step, startInfo, allModels]
    rcases hExit with ⟨next, hLift, hBad⟩
    exact bad_not_adaptiveKernel hBad (hSafe next hLift)
  · have hExit : exists next : InfoState F,
        LiftedStep F startInfo Action.chooseRight next /\ next.state = State.bad := by
      refine ⟨{ state := State.bad, possible := fun i => i = Model.left },
        ?_, rfl⟩
      refine ⟨Model.left, State.bad, trivial, by simp [F, Step, startInfo],
        rfl, ?_⟩
      intro j
      cases j <;> simp [soundUpdate, F, Step, startInfo, allModels]
    rcases hExit with ⟨next, hLift, hBad⟩
    exact bad_not_adaptiveKernel hBad (hSafe next hLift)
  · have hExit : exists next : InfoState F,
        LiftedStep F startInfo Action.probe next /\ next.state = State.bad := by
      refine ⟨{ state := State.bad, possible := fun i => i = Model.left },
        ?_, rfl⟩
      refine ⟨Model.left, State.bad, trivial, by simp [F, Step, startInfo],
        rfl, ?_⟩
      intro j
      cases j <;> simp [soundUpdate, F, Step, startInfo, allModels]
    rcases hExit with ⟨next, hLift, hBad⟩
    exact bad_not_adaptiveKernel hBad (hSafe next hLift)

theorem W_unlearnable_adaptive_exclusion :
    Not (AK startInfo) :=
  startInfo_not_adaptiveKernel

end Unlearnable

namespace FakeUpdate

inductive Model where
  | trueWorld
  | fakeWorld
deriving DecidableEq

instance : Fintype Model where
  elems := {Model.trueWorld, Model.fakeWorld}
  complete := by
    intro i
    cases i <;> simp

inductive State where
  | start
  | safe
  | bad
deriving DecidableEq

inductive Action where
  | trustFake
deriving DecidableEq

def Step : Model -> State -> Action -> State -> Prop
  | Model.trueWorld, State.start, Action.trustFake, State.bad => True
  | Model.fakeWorld, State.start, Action.trustFake, State.safe => True
  | Model.fakeWorld, State.safe, Action.trustFake, State.safe => True
  | _, State.bad, Action.trustFake, State.bad => True
  | _, _, _, _ => False

def Constraint : State -> Prop
  | State.bad => False
  | _ => True

def F : AmbFamily State Action where
  Model := Model
  modelFinite := inferInstance
  modelNonempty := ⟨Model.trueWorld⟩
  Step := Step
  Constraint := Constraint

def Allowed (_ : State) (_ : Action) : Prop := True

def Requirement (_ : State) : Prop := True

abbrev AK : InfoState F -> Prop :=
  AdaptiveKernel F Allowed Requirement

def allModels (_ : Model) : Prop := True

def onlyFake : Model -> Prop
  | Model.trueWorld => False
  | Model.fakeWorld => True

def fullStart : InfoState F where
  state := State.start
  possible := allModels

/--
An intentionally unsound "identification" update. It is not `soundUpdate` and
is not used by the core lift; it is a witness for fabricated model elimination.
-/
def fakeUpdate (_info : InfoState F) (_a : Action) (_observed : State) :
    Model -> Prop :=
  onlyFake

def fakeStart : InfoState F where
  state := State.start
  possible := fakeUpdate fullStart Action.trustFake State.safe

def fakeSafe : InfoState F where
  state := State.safe
  possible := onlyFake

theorem fakeUpdate_drops_true_model :
    fullStart.possible Model.trueWorld /\
      Not (fakeUpdate fullStart Action.trustFake State.safe Model.trueWorld) := by
  exact ⟨trivial, by simp [fakeUpdate, onlyFake]⟩

theorem fakeStart_excludes_true_model :
    Not (fakeStart.possible Model.trueWorld) := by
  simp [fakeStart, fakeUpdate, onlyFake]

private theorem info_eq_fakeSafe
    {info : InfoState F}
    (hState : info.state = State.safe)
    (hPossible : forall j : Model, info.possible j <-> onlyFake j) :
    info = fakeSafe := by
  cases info with
  | mk state possible =>
      dsimp at hState hPossible
      subst state
      simp [fakeSafe]
      funext j
      exact propext (hPossible j)

private theorem fakeStart_good :
    fakeStart = fakeStart \/ fakeStart = fakeSafe := by
  exact Or.inl rfl

private theorem fake_good_postfixed :
    Postfixed
      (robustCorridorOp (liftedDecision F) (liftedAllowed F Allowed)
        (liftedRequirement F Requirement))
      (fun info => info = fakeStart \/ info = fakeSafe) := by
  intro info hInfo
  rcases hInfo with hStart | hSafe
  · subst info
    refine ⟨?_, trivial, Action.trustFake, ?_, ?_, ?_⟩
    · exact ⟨by simp [fakeStart, F, Constraint],
        ⟨Model.fakeWorld, by simp [fakeStart, fakeUpdate, onlyFake]⟩⟩
    · constructor
      · trivial
      · intro i hi
        cases i
        · have hFalse : False := by
            simp [fakeStart, fakeUpdate, onlyFake] at hi
          exact False.elim hFalse
        · exact ⟨State.safe, by simp [F, Step, fakeStart]⟩
    · exact ⟨fakeSafe, Model.fakeWorld, State.safe,
        by simp [fakeStart, fakeUpdate, onlyFake],
        by simp [F, Step, fakeStart],
        rfl,
        (by
          intro j
          cases j <;>
            simp [fakeSafe, onlyFake, soundUpdate, fakeStart, fakeUpdate, F, Step])⟩
    · intro next hLift
      right
      rcases hLift with ⟨i, observed, hi, hStep, hNextState, hNextPossible⟩
      have hiFake : i = Model.fakeWorld := by
        cases i
        · have hFalse : False := by
            simp [fakeStart, fakeUpdate, onlyFake] at hi
          exact False.elim hFalse
        · rfl
      cases hiFake
      cases observed <;> simp [F, Step, fakeStart] at hStep
      exact info_eq_fakeSafe hNextState (by
        intro j
        cases j <;>
          simp [onlyFake, soundUpdate, fakeStart, fakeUpdate,
            F, Step, hNextPossible])
  · subst info
    refine ⟨?_, trivial, Action.trustFake, ?_, ?_, ?_⟩
    · exact ⟨by simp [fakeSafe, F, Constraint],
        ⟨Model.fakeWorld, by simp [fakeSafe, onlyFake]⟩⟩
    · constructor
      · trivial
      · intro i hi
        cases i
        · have hFalse : False := by
            simp [fakeSafe, onlyFake] at hi
          exact False.elim hFalse
        · exact ⟨State.safe, by simp [F, Step, fakeSafe]⟩
    · exact ⟨fakeSafe, Model.fakeWorld, State.safe,
        by simp [fakeSafe, onlyFake],
        by simp [F, Step, fakeSafe],
        rfl,
        (by
          intro j
          cases j <;>
            simp [fakeSafe, onlyFake, soundUpdate, F, Step])⟩
    · intro next hLift
      right
      rcases hLift with ⟨i, observed, hi, hStep, hNextState, hNextPossible⟩
      have hiFake : i = Model.fakeWorld := by
        cases i
        · have hFalse : False := by
            simp [fakeSafe, onlyFake] at hi
          exact False.elim hFalse
        · rfl
      cases hiFake
      cases observed <;> simp [F, Step, fakeSafe] at hStep
      exact info_eq_fakeSafe hNextState (by
        intro j
        cases j <;>
          simp [fakeSafe, onlyFake, soundUpdate, F, Step, hNextPossible])

theorem fakeStart_in_adaptiveKernel :
    AK fakeStart :=
  postfixed_le_gfp fake_good_postfixed fakeStart fakeStart_good

theorem excluded_true_model_trustFake_exits_constraint :
    F.Step Model.trueWorld fakeStart.state Action.trustFake State.bad /\
      Not (F.Constraint State.bad) := by
  exact ⟨by simp [F, Step, fakeStart], by simp [F, Constraint]⟩

theorem W_fake_update_phantom_corridor :
    Not (fakeStart.possible Model.trueWorld) /\
      AK fakeStart /\
      F.Step Model.trueWorld fakeStart.state Action.trustFake State.bad /\
      Not (F.Constraint State.bad) := by
  exact ⟨fakeStart_excludes_true_model, fakeStart_in_adaptiveKernel,
    excluded_true_model_trustFake_exits_constraint⟩

end FakeUpdate

end AdaptiveFixedWorldExamples
end Decision
end OmegaProper
