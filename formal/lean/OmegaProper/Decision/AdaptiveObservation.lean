import OmegaProper.Decision.AdaptiveFixedWorld
import OmegaProper.Decision.BlackwellDeterministic

/-!
OmegaProper.Decision.AdaptiveObservation

Observation-parametric adaptive fixed-world corridors.

The original B2.1 lift in `AdaptiveFixedWorld` uses successor-state observation.
This file adds a small deterministic observation interface and proves the
monotonicity theorem needed for the next epistemic layer:

if a coarser observation factors through a finer one, then every adaptive
corridor state for the coarser observation is also a corridor state for the
finer observation, provided the finer information state is nonempty and refines
the coarser one.

This is a deterministic, possibilistic, finite-model theorem. It is not a full
POMDP theorem, not stochastic risk, not value, not agency, and not Omega
validation.
-/

namespace OmegaProper
namespace Decision
namespace AdaptiveObservation

open AmbiguityFamily
open AdaptiveFixedWorld
open BlackwellDeterministic
open Trajectory.PredicateFixpoint

universe u v w o1 o2

/--
Observation-based sound update.

The concrete successor is still recorded as the next state, but model
elimination is driven only by the declared observation of that successor.
-/
def observedUpdate
    (F : AmbFamily State Action)
    (Obs : DetExperiment State ObsTy)
    (info : InfoState F)
    (a : Action)
    (observed : State) :
    F.Model -> Prop :=
  fun i =>
    info.possible i /\
      exists y, F.Step i info.state a y /\
        Obs.observe y = Obs.observe observed

/-- A true model that produced the observed successor survives observed update. -/
theorem observedUpdate_truth_preserves
    (F : AmbFamily State Action)
    (Obs : DetExperiment State ObsTy)
    (info : InfoState F)
    (a : Action)
    (observed : State)
    (i : F.Model)
    (hPossible : info.possible i)
    (hStep : F.Step i info.state a observed) :
    observedUpdate F Obs info a observed i := by
  exact And.intro hPossible
    (Exists.intro observed (And.intro hStep rfl))

/-- Lifted step for an arbitrary deterministic observation interface. -/
def ObservedLiftedStep
    (F : AmbFamily State Action)
    (Obs : DetExperiment State ObsTy)
    (info : InfoState F)
    (a : Action)
    (next : InfoState F) : Prop :=
  exists i observed,
    info.possible i /\
    F.Step i info.state a observed /\
    next.state = observed /\
    forall j : F.Model,
      next.possible j <-> observedUpdate F Obs info a observed j

/-- Observed lifted decision structure. -/
def observedLiftedDecision
    (F : AmbFamily State Action)
    (Obs : DetExperiment State ObsTy) : DecisionStructure where
  State := InfoState F
  Action := Action
  Step := ObservedLiftedStep F Obs
  Constraint := fun info =>
    F.Constraint info.state /\ RemainingNonempty info

/-- Adaptive kernel under a declared deterministic observation interface. -/
def ObservedAdaptiveKernel
    (F : AmbFamily State Action)
    (Obs : DetExperiment State ObsTy)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    InfoState F -> Prop :=
  RobustCorridor (observedLiftedDecision F Obs) (liftedAllowed F Allowed)
    (liftedRequirement F Requirement)

/--
Information-state refinement: `fine` has the same concrete state, a nonempty
remaining set, and no possible model absent from `coarse`.
-/
def InfoRefines
    {F : AmbFamily State Action}
    (fine coarse : InfoState F) : Prop :=
  fine.state = coarse.state /\
    RemainingNonempty fine /\
    forall i : F.Model, fine.possible i -> coarse.possible i

/-- A lifted observed step always leaves a nonempty remaining model set. -/
theorem observedLiftedStep_remaining_nonempty
    (F : AmbFamily State Action)
    (Obs : DetExperiment State ObsTy)
    {info next : InfoState F}
    {a : Action}
    (hStep : ObservedLiftedStep F Obs info a next) :
    RemainingNonempty next := by
  rcases hStep with
    ⟨i, observed, hPossible, hConcrete, _hState, hNextPossible⟩
  exact ⟨i, (hNextPossible i).mpr
    (observedUpdate_truth_preserves F Obs info a observed i
      hPossible hConcrete)⟩

/--
Under deterministic factorization, the finer-observation update is a subset of
the coarser-observation update.
-/
theorem observedUpdate_subset_of_factorization
    (F : AmbFamily State Action)
    {Fine : DetExperiment State ObsFine}
    {Coarse : DetExperiment State ObsCoarse}
    (hFactor : DetFactorization Fine Coarse)
    {fineInfo coarseInfo : InfoState F}
    {a : Action} {observed : State}
    (hRef : InfoRefines fineInfo coarseInfo)
    {i : F.Model}
    (hFine : observedUpdate F Fine fineInfo a observed i) :
    observedUpdate F Coarse coarseInfo a observed i := by
  rcases hRef with ⟨hState, hInfoNonempty, hSubset⟩
  rcases hFine with ⟨hPossibleFine, y, hStepFine, hObsFine⟩
  have hPossibleCoarse : coarseInfo.possible i := hSubset i hPossibleFine
  have hStepCoarse : F.Step i coarseInfo.state a y := by
    simpa [hState] using hStepFine
  have hObsCoarse : Coarse.observe y = Coarse.observe observed := by
    calc
      Coarse.observe y = hFactor.map (Fine.observe y) := hFactor.commutes y
      _ = hFactor.map (Fine.observe observed) := by rw [hObsFine]
      _ = Coarse.observe observed := (hFactor.commutes observed).symm
  exact ⟨hPossibleCoarse, y, hStepCoarse, hObsCoarse⟩

/-- Canonical successor for an observed lifted step. -/
def observedSuccessor
    (F : AmbFamily State Action)
    (Obs : DetExperiment State ObsTy)
    (info : InfoState F)
    (a : Action)
    (observed : State) : InfoState F where
  state := observed
  possible := observedUpdate F Obs info a observed

/--
A finer observed step refines the matching coarser observed successor under a
factorization of the coarse observation through the fine one.
-/
theorem observedLiftedStep_refines_successor_of_factorization
    (F : AmbFamily State Action)
    {Fine : DetExperiment State ObsFine}
    {Coarse : DetExperiment State ObsCoarse}
    (hFactor : DetFactorization Fine Coarse)
    {fineInfo coarseInfo nextFine : InfoState F}
    {a : Action}
    (hRef : InfoRefines fineInfo coarseInfo)
    (hStepFine : ObservedLiftedStep F Fine fineInfo a nextFine) :
    exists nextCoarse,
      ObservedLiftedStep F Coarse coarseInfo a nextCoarse /\
        InfoRefines nextFine nextCoarse := by
  rcases hRef with ⟨hState, hInfoNonempty, hSubset⟩
  rcases hStepFine with
    ⟨i, observed, hPossibleFine, hConcreteFine, hNextState, hNextPossible⟩
  let nextCoarse := observedSuccessor F Coarse coarseInfo a observed
  have hPossibleCoarse : coarseInfo.possible i := hSubset i hPossibleFine
  have hConcreteCoarse : F.Step i coarseInfo.state a observed := by
    simpa [hState] using hConcreteFine
  have hStepCoarse : ObservedLiftedStep F Coarse coarseInfo a nextCoarse := by
    exact ⟨i, observed, hPossibleCoarse, hConcreteCoarse, rfl, by
      intro j
      rfl⟩
  have hNextNonempty : RemainingNonempty nextFine := by
    exact observedLiftedStep_remaining_nonempty F Fine
      ⟨i, observed, hPossibleFine, hConcreteFine, hNextState,
        hNextPossible⟩
  have hNextSubset :
      forall j : F.Model,
        nextFine.possible j -> nextCoarse.possible j := by
    intro j hj
    exact observedUpdate_subset_of_factorization F hFactor
      (And.intro hState (And.intro hInfoNonempty hSubset))
      ((hNextPossible j).mp hj)
  exact ⟨nextCoarse, hStepCoarse,
    ⟨by simpa [nextCoarse, observedSuccessor] using hNextState,
      hNextNonempty,
      hNextSubset⟩⟩

/--
Observation-informativeness monotonicity.

If `Coarse` factors through `Fine`, then a coarser-observation adaptive kernel
certificate transports to any nonempty finer information state that refines it.
-/
theorem observedAdaptiveKernel_mono_of_factorization
    (F : AmbFamily State Action)
    {Fine : DetExperiment State ObsFine}
    {Coarse : DetExperiment State ObsCoarse}
    (hFactor : DetFactorization Fine Coarse)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    {fineInfo coarseInfo : InfoState F}
    (hRef : InfoRefines fineInfo coarseInfo)
    (hCoarse : ObservedAdaptiveKernel F Coarse Allowed Requirement coarseInfo) :
    ObservedAdaptiveKernel F Fine Allowed Requirement fineInfo := by
  let S : InfoState F -> Prop := fun info =>
    exists coarse,
      InfoRefines info coarse /\
        ObservedAdaptiveKernel F Coarse Allowed Requirement coarse
  have hPost :
      Postfixed
        (robustCorridorOp (observedLiftedDecision F Fine)
          (liftedAllowed F Allowed) (liftedRequirement F Requirement))
        S := by
    intro info hInfo
    rcases hInfo with ⟨coarse, hInfoRef, hCoarseKernel⟩
    rcases hInfoRef with ⟨hState, hInfoNonempty, hSubset⟩
    have hCoarseClosed :=
      (robustCorridor_fixed (observedLiftedDecision F Coarse)
        (liftedAllowed F Allowed) (liftedRequirement F Requirement)).left
        coarse hCoarseKernel
    rcases hCoarseClosed with
      ⟨hCoarseConstraint, hCoarseReq, a, hAllowedCoarse,
        hEnabledCoarse, hSafeCoarse⟩
    have hFineConstraint :
        (observedLiftedDecision F Fine).Constraint info := by
      exact ⟨by
        simpa [hState] using hCoarseConstraint.left,
        hInfoNonempty⟩
    have hFineReq : liftedRequirement F Requirement info := by
      simpa [liftedRequirement, hState] using hCoarseReq
    have hFineAllowed : liftedAllowed F Allowed info a := by
      constructor
      · simpa [liftedAllowed, hState] using hAllowedCoarse.left
      · intro i hi
        rcases hAllowedCoarse.right i (hSubset i hi) with ⟨y, hStep⟩
        exact ⟨y, by simpa [hState] using hStep⟩
    have hFineEnabled :
        exists next, ObservedLiftedStep F Fine info a next := by
      rcases hInfoNonempty with ⟨i, hi⟩
      rcases hFineAllowed.right i hi with ⟨observed, hStep⟩
      exact ⟨observedSuccessor F Fine info a observed,
        i, observed, hi, hStep, rfl, by intro j; rfl⟩
    exact ⟨hFineConstraint, hFineReq, a, hFineAllowed, hFineEnabled, by
      intro nextFine hStepFine
      rcases observedLiftedStep_refines_successor_of_factorization
          F hFactor (And.intro hState (And.intro hInfoNonempty hSubset))
          hStepFine with
        ⟨nextCoarse, hStepCoarse, hNextRef⟩
      exact ⟨nextCoarse, hNextRef, hSafeCoarse nextCoarse hStepCoarse⟩⟩
  exact postfixed_le_gfp hPost fineInfo ⟨coarseInfo, hRef, hCoarse⟩

end AdaptiveObservation
end Decision
end OmegaProper
