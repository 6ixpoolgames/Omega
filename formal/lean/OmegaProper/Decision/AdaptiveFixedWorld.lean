import OmegaProper.Decision.AmbiguityFamily

/-!
OmegaProper.Decision.AdaptiveFixedWorld

Information-state lift for unknown-but-fixed possibilistic ambiguity.

The lifted state is a concrete state together with the remaining set of models
consistent with the observations so far. In v0, observations are successor
states. The adaptive kernel is not a new fixed-point theory: it is the existing
`RobustCorridor` of the lifted decision structure with remaining-model
enabledness folded into `Allowed`.

This file does not prove the full fixed-world correspondence theorem. It does
not define stochastic risk, value, agency, identity, moral standing, or Omega
validation.
-/

namespace OmegaProper
namespace Decision
namespace AdaptiveFixedWorld

open AmbiguityFamily
open Trajectory.PredicateFixpoint

universe u v w

/-- Information state: current concrete state plus remaining possible models. -/
structure InfoState (F : AmbFamily State Action) where
  state : State
  possible : F.Model -> Prop

/-- The current information state still has at least one possible model. -/
def RemainingNonempty {F : AmbFamily State Action}
    (info : InfoState F) : Prop :=
  exists i : F.Model, info.possible i

/--
Sound successor-state update: keep exactly the remaining models that can
produce the observed successor.
-/
def soundUpdate
    (F : AmbFamily State Action)
    (info : InfoState F)
    (a : Action)
    (observed : State) :
    F.Model -> Prop :=
  fun i => info.possible i /\ F.Step i info.state a observed

/-- Sound updates never eliminate a true model that produced the observation. -/
theorem soundUpdate_truth_preserves
    (F : AmbFamily State Action)
    (info : InfoState F)
    (a : Action)
    (observed : State)
    (i : F.Model)
    (hPossible : info.possible i)
    (hStep : F.Step i info.state a observed) :
    soundUpdate F info a observed i := by
  exact And.intro hPossible hStep

/--
The lifted transition relation. The next information state's possible models
are exactly the sound update for the observed successor.
-/
def LiftedStep
    (F : AmbFamily State Action)
    (info : InfoState F)
    (a : Action)
    (next : InfoState F) : Prop :=
  exists i observed,
    info.possible i /\
    F.Step i info.state a observed /\
    next.state = observed /\
    forall j : F.Model,
      next.possible j <-> soundUpdate F info a observed j

/-- The lifted ordinary decision structure consumed by `RobustCorridor`. -/
def liftedDecision (F : AmbFamily State Action) : DecisionStructure where
  State := InfoState F
  Action := Action
  Step := LiftedStep F
  Constraint := fun info =>
    F.Constraint info.state /\ RemainingNonempty info

/--
Lifted allowedness: the action must be allowed at the concrete state and enabled
in every remaining possible model.
-/
def liftedAllowed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop) :
    InfoState F -> Action -> Prop :=
  fun info a =>
    Allowed info.state a /\
    forall i : F.Model, info.possible i -> exists y, F.Step i info.state a y

/-- Lift a state-local requirement to information states. -/
def liftedRequirement
    (F : AmbFamily State Action)
    (Requirement : State -> Prop) :
    InfoState F -> Prop :=
  fun info => Requirement info.state

/--
Adaptive fixed-world kernel. This is definitionally the existing robust
corridor of the lifted system.
-/
def AdaptiveKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    InfoState F -> Prop :=
  RobustCorridor (liftedDecision F) (liftedAllowed F Allowed)
    (liftedRequirement F Requirement)

/-- Reduction: adaptive fixed-world corridor is an ordinary robust corridor. -/
theorem adaptiveKernel_eq_liftedRobustCorridor
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    AdaptiveKernel F Allowed Requirement =
      RobustCorridor (liftedDecision F) (liftedAllowed F Allowed)
        (liftedRequirement F Requirement) := by
  rfl

theorem adaptiveKernel_sub_base_constraint
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    PSub (AdaptiveKernel F Allowed Requirement)
      (fun info => F.Constraint info.state) := by
  intro info hInfo
  exact (robustCorridor_sub_constraint
    (liftedDecision F) (liftedAllowed F Allowed)
    (liftedRequirement F Requirement) info hInfo).left

theorem adaptiveKernel_remaining_nonempty
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    PSub (AdaptiveKernel F Allowed Requirement) RemainingNonempty := by
  intro info hInfo
  exact (robustCorridor_sub_constraint
    (liftedDecision F) (liftedAllowed F Allowed)
    (liftedRequirement F Requirement) info hInfo).right

theorem adaptiveKernel_sub_base_requirement
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    PSub (AdaptiveKernel F Allowed Requirement)
      (fun info => Requirement info.state) := by
  intro info hInfo
  exact robustCorridor_sub_requirement
    (liftedDecision F) (liftedAllowed F Allowed)
    (liftedRequirement F Requirement) info hInfo

/-- Every adaptive-kernel information state has a lifted robust action. -/
theorem adaptiveKernel_has_action
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    {info : InfoState F}
    (hInfo : AdaptiveKernel F Allowed Requirement info) :
    exists a,
      ActionRobustKeeps (liftedDecision F)
        (liftedAllowed F Allowed)
        (AdaptiveKernel F Allowed Requirement) info a := by
  exact robustCorridor_action_safe
    (liftedDecision F) (liftedAllowed F Allowed)
    (liftedRequirement F Requirement) hInfo

/--
If a lifted step observes a successor generated by model `i`, then `i` is
possible in the next information state.
-/
theorem liftedStep_preserves_generating_model
    (F : AmbFamily State Action)
    {info next : InfoState F}
    {a : Action}
    {i : F.Model}
    {observed : State}
    (hLift : LiftedStep F info a next)
    (hPossible : info.possible i)
    (hStep : F.Step i info.state a observed)
    (hObserved : next.state = observed) :
    next.possible i := by
  rcases hLift with ⟨_k, y, _hPossibleK, _hStepK,
    hNextState, hNextPossible⟩
  have hObservedEq : observed = y := by
    rw [<- hObserved, hNextState]
  have hStepY : F.Step i info.state a y := by
    rw [hObservedEq] at hStep
    exact hStep
  have hSound : soundUpdate F info a y i := by
    exact soundUpdate_truth_preserves F info a y i hPossible hStepY
  exact (hNextPossible i).mpr hSound

/-- A lifted step never invents a model that was not previously possible. -/
theorem liftedStep_remaining_sub
    (F : AmbFamily State Action)
    {info next : InfoState F}
    {a : Action}
    (hLift : LiftedStep F info a next) :
    forall i : F.Model, next.possible i -> info.possible i := by
  intro i hNext
  rcases hLift with ⟨_k, y, _hPossibleK, _hStepK,
    _hNextState, hNextPossible⟩
  exact ((hNextPossible i).mp hNext).left

/-- Every lifted step leaves at least one possible model: the model that generated it. -/
theorem liftedStep_remaining_nonempty
    (F : AmbFamily State Action)
    {info next : InfoState F}
    {a : Action}
    (hLift : LiftedStep F info a next) :
    RemainingNonempty next := by
  rcases hLift with ⟨k, y, hPossibleK, hStepK,
    _hNextState, hNextPossible⟩
  exact ⟨k, (hNextPossible k).mpr
    (soundUpdate_truth_preserves F info a y k hPossibleK hStepK)⟩

/-- The lifted successor state's model set is exactly the sound update. -/
theorem liftedStep_possible_iff_soundUpdate
    (F : AmbFamily State Action)
    {info next : InfoState F}
    {a : Action}
    {observed : State}
    (hLift : LiftedStep F info a next)
    (hObserved : next.state = observed)
    (i : F.Model) :
    next.possible i <-> soundUpdate F info a observed i := by
  rcases hLift with ⟨_k, y, _hPossibleK, _hStepK,
    hNextState, hNextPossible⟩
  have hObservedEq : observed = y := by
    rw [<- hObserved, hNextState]
  constructor
  · intro hNext
    have hSoundY := (hNextPossible i).mp hNext
    simpa [hObservedEq] using hSoundY
  · intro hSoundObserved
    have hSoundY : soundUpdate F info a y i := by
      simpa [hObservedEq] using hSoundObserved
    exact (hNextPossible i).mpr hSoundY

/-- Finite policy-following reachability in the lifted information-state system. -/
inductive LiftedReach
    (F : AmbFamily State Action)
    (policy : InfoState F -> Action) :
    InfoState F -> InfoState F -> Prop where
  | refl (info : InfoState F) :
      LiftedReach F policy info info
  | step {start current next : InfoState F} :
      LiftedReach F policy start current ->
      LiftedStep F current (policy current) next ->
      LiftedReach F policy start next

/-- Finite reachability through the concrete steps of one fixed model. -/
inductive FixedModelReach
    (F : AmbFamily State Action)
    (policy : InfoState F -> Action)
    (actual : F.Model) :
    InfoState F -> InfoState F -> Prop where
  | refl (info : InfoState F) :
      FixedModelReach F policy actual info info
  | step {start current next : InfoState F} :
      FixedModelReach F policy actual start current ->
      F.Step actual current.state (policy current) next.state ->
      FixedModelReach F policy actual start next

/--
Finite reach generated by one actual fixed model with sound information-state
updates.
-/
inductive SoundFixedWorldReach
    (F : AmbFamily State Action)
    (policy : InfoState F -> Action)
    (actual : F.Model) :
    InfoState F -> InfoState F -> Prop where
  | refl (info : InfoState F) :
      SoundFixedWorldReach F policy actual info info
  | step {start current next : InfoState F} :
      SoundFixedWorldReach F policy actual start current ->
      F.Step actual current.state (policy current) next.state ->
      (forall j : F.Model,
        next.possible j <->
          soundUpdate F current (policy current) next.state j) ->
      SoundFixedWorldReach F policy actual start next

/-- Lifted finite reach never invents a model. -/
theorem liftedReach_remaining_sub
    (F : AmbFamily State Action)
    (policy : InfoState F -> Action)
    {start finish : InfoState F}
    (hReach : LiftedReach F policy start finish) :
    forall i : F.Model, finish.possible i -> start.possible i := by
  intro i hFinish
  induction hReach with
  | refl =>
      exact hFinish
  | step hPrev hStep ih =>
      exact ih (liftedStep_remaining_sub F hStep i hFinish)

/--
For sound fixed-world reach, an initially possible actual model remains
possible at the terminal information state.
-/
theorem soundFixedWorldReach_preserves_trueModel
    (F : AmbFamily State Action)
    (policy : InfoState F -> Action)
    {actual : F.Model}
    {start finish : InfoState F}
    (hStart : start.possible actual)
    (hReach : SoundFixedWorldReach F policy actual start finish) :
    finish.possible actual := by
  induction hReach with
  | refl =>
      exact hStart
  | step hPrev hStep hUpdate ih =>
      exact (hUpdate actual).mpr (And.intro ih hStep)

/-- Sound fixed-world reach induces lifted reach when the actual model is possible initially. -/
theorem soundFixedWorldReach_to_liftedReach
    (F : AmbFamily State Action)
    (policy : InfoState F -> Action)
    {actual : F.Model}
    {start finish : InfoState F}
    (hStart : start.possible actual)
    (hReach : SoundFixedWorldReach F policy actual start finish) :
    LiftedReach F policy start finish := by
  induction hReach with
  | refl =>
      exact LiftedReach.refl _
  | step hPrev hStep hUpdate ih =>
      rename_i current next
      have hCurrentPossible :
          current.possible actual :=
        soundFixedWorldReach_preserves_trueModel F policy hStart hPrev
      have hLift :
          LiftedStep F current (policy current) next := by
        exact ⟨actual, next.state, hCurrentPossible, hStep, rfl, hUpdate⟩
      exact LiftedReach.step ih hLift

/--
If a model is possible after a lifted step, that model realizes the observed
concrete transition of that step.
-/
theorem liftedStep_terminalModel_realizes_step
    (F : AmbFamily State Action)
    {info next : InfoState F}
    {a : Action}
    {i : F.Model}
    (hLift : LiftedStep F info a next)
    (hNextPossible : next.possible i) :
    F.Step i info.state a next.state := by
  rcases hLift with ⟨_k, y, _hPossibleK, _hStepK,
    hNextState, hNextPossibleIff⟩
  have hSound : soundUpdate F info a y i :=
    (hNextPossibleIff i).mp hNextPossible
  simpa [hNextState] using hSound.right

/--
Finite play correspondence, terminal-model direction: if model `i` remains
possible at the end of a lifted finite reach, then `i` realizes the concrete
state transitions of that reach.
-/
theorem liftedReach_terminalModel_realizes_fixedModelReach
    (F : AmbFamily State Action)
    (policy : InfoState F -> Action)
    {start finish : InfoState F}
    {i : F.Model}
    (hReach : LiftedReach F policy start finish)
    (hFinishPossible : finish.possible i) :
    FixedModelReach F policy i start finish := by
  induction hReach with
  | refl =>
      exact FixedModelReach.refl _
  | step hPrev hLift ih =>
      have hCurrentPossible :
          _ := liftedStep_remaining_sub F hLift i hFinishPossible
      have hFixedPrev := ih hCurrentPossible
      have hConcrete :
          F.Step i _ (policy _) _ :=
        liftedStep_terminalModel_realizes_step F hLift hFinishPossible
      exact FixedModelReach.step hFixedPrev hConcrete

end AdaptiveFixedWorld
end Decision
end OmegaProper
