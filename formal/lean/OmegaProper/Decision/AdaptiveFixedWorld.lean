import Mathlib.Data.Finset.Max
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

/-! ### Finite model-set view and infinite lifted traces -/

/--
Finite view of an information state's possible models. The core state keeps
`possible` as a predicate; this view is only for finite stabilization arguments.
-/
noncomputable def possibleFinset
    (F : AmbFamily State Action)
    (info : InfoState F) : Finset F.Model := by
  classical
  exact Finset.univ.filter info.possible

theorem mem_possibleFinset_iff
    (F : AmbFamily State Action)
    (info : InfoState F)
    (i : F.Model) :
    i ∈ possibleFinset F info <-> info.possible i := by
  classical
  simp [possibleFinset]

theorem possibleFinset_nonempty_iff
    (F : AmbFamily State Action)
    (info : InfoState F) :
    (possibleFinset F info).Nonempty <-> RemainingNonempty info := by
  constructor
  · intro h
    rcases h with ⟨i, hi⟩
    exact ⟨i, (mem_possibleFinset_iff F info i).mp hi⟩
  · intro h
    rcases h with ⟨i, hi⟩
    exact ⟨i, (mem_possibleFinset_iff F info i).mpr hi⟩

theorem liftedStep_possibleFinset_subset
    (F : AmbFamily State Action)
    {info next : InfoState F}
    {a : Action}
    (hLift : LiftedStep F info a next) :
    possibleFinset F next ⊆ possibleFinset F info := by
  intro i hi
  exact (mem_possibleFinset_iff F info i).mpr
    (liftedStep_remaining_sub F hLift i
      ((mem_possibleFinset_iff F next i).mp hi))

/-- If finite sets descend one step at a time, later sets are subsets of earlier sets. -/
theorem finset_descending_subset
    {α : Type u} [DecidableEq α]
    (S : Nat -> Finset α)
    (hDesc : forall n, S (n + 1) ⊆ S n)
    {m n : Nat}
    (hmn : m ≤ n) :
    S n ⊆ S m := by
  induction hmn with
  | refl =>
      intro x hx
      exact hx
  | step hmn ih =>
      intro x hx
      exact ih (hDesc _ hx)

/--
A descending nonempty sequence of finite subsets of a finite type has a model
that remains present forever.
-/
theorem descending_nonempty_finset_has_persistent_member
    {α : Type u} [Fintype α] [DecidableEq α]
    (S : Nat -> Finset α)
    (hDesc : forall n, S (n + 1) ⊆ S n)
    (hNonempty : forall n, (S n).Nonempty) :
    exists i : α, forall n, i ∈ S n := by
  classical
  by_contra hNone
  have hNoPersistent : forall i : α, Not (forall n, i ∈ S n) := by
    intro i hAll
    exact hNone ⟨i, hAll⟩
  have hDrops : forall i : α, exists n, i ∉ S n := by
    intro i
    simpa [not_forall] using hNoPersistent i
  let drop : α -> Nat := fun i => Nat.find (hDrops i)
  have hImageNonempty : (Finset.univ.image drop).Nonempty := by
    rcases hNonempty 0 with ⟨i, _hi⟩
    exact ⟨drop i, by
      apply Finset.mem_image.mpr
      exact ⟨i, by simp, rfl⟩⟩
  let bound : Nat := (Finset.univ.image drop).max' hImageNonempty
  have hDropLeBound : forall i : α, drop i ≤ bound := by
    intro i
    have hi : drop i ∈ Finset.univ.image drop := by
      apply Finset.mem_image.mpr
      exact ⟨i, by simp, rfl⟩
    exact (Finset.univ.image drop).le_max' (drop i) hi
  have hNoAtBoundSucc : forall i : α, i ∉ S (bound + 1) := by
    intro i hi
    have hDropNot : i ∉ S (drop i) := Nat.find_spec (hDrops i)
    have hSubset : S (bound + 1) ⊆ S (drop i) := by
      exact finset_descending_subset S hDesc
        (Nat.le_trans (hDropLeBound i) (Nat.le_succ bound))
    exact hDropNot (hSubset hi)
  rcases hNonempty (bound + 1) with ⟨i, hi⟩
  exact hNoAtBoundSucc i hi

/-- An infinite lifted trace with explicitly recorded actions. -/
structure InfiniteLiftedTrace
    (F : AmbFamily State Action) where
  info : Nat -> InfoState F
  action : Nat -> Action
  step : forall n,
    LiftedStep F (info n) (action n) (info (n + 1))

theorem infiniteLiftedTrace_possibleFinset_descends
    (F : AmbFamily State Action)
    (trace : InfiniteLiftedTrace F) :
    forall n,
      possibleFinset F (trace.info (n + 1)) ⊆
        possibleFinset F (trace.info n) := by
  intro n
  exact liftedStep_possibleFinset_subset F (trace.step n)

/--
Fixed-model realizer theorem: every infinite lifted trace whose information
states remain nonempty has one fixed model that realizes every observed step.

This is intentionally weaker than the full fixed-world correspondence theorem:
it extracts a fixed-model realizer for the concrete trace.
-/
theorem infiniteLiftedTrace_has_fixedModelRealizer
    (F : AmbFamily State Action)
    (trace : InfiniteLiftedTrace F)
    (hNonempty : forall n, RemainingNonempty (trace.info n)) :
    exists i : F.Model,
      forall n,
        F.Step i (trace.info n).state (trace.action n)
          (trace.info (n + 1)).state := by
  classical
  let S : Nat -> Finset F.Model := fun n => possibleFinset F (trace.info n)
  have hDesc : forall n, S (n + 1) ⊆ S n := by
    intro n
    exact infiniteLiftedTrace_possibleFinset_descends F trace n
  have hNonemptyFin : forall n, (S n).Nonempty := by
    intro n
    exact (possibleFinset_nonempty_iff F (trace.info n)).mpr (hNonempty n)
  rcases descending_nonempty_finset_has_persistent_member S hDesc hNonemptyFin with
    ⟨i, hPersistent⟩
  exact ⟨i, by
    intro n
    exact liftedStep_terminalModel_realizes_step F (trace.step n)
      ((mem_possibleFinset_iff F (trace.info (n + 1)) i).mp
        (hPersistent (n + 1)))⟩

/-! ### Policy-level adaptive guarantee surface -/

/-- A stationary adaptive policy chooses from the current information state. -/
abbrev AdaptivePolicy
    (F : AmbFamily State Action) :=
  InfoState F -> Action

/-- Closed-loop operator for one fixed adaptive policy on the lifted system. -/
def adaptivePolicyKernelOp
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F)
    (S : InfoState F -> Prop) :
    InfoState F -> Prop :=
  fun info =>
    (liftedDecision F).Constraint info /\
    liftedRequirement F Requirement info /\
    ActionRobustKeeps (liftedDecision F) (liftedAllowed F Allowed)
      S info (policy info)

/-- Closed-loop adaptive policy kernel. -/
def AdaptivePolicyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F) :
    InfoState F -> Prop :=
  gfp (adaptivePolicyKernelOp F Allowed Requirement policy)

/-- Fixed-point reading of an adaptive policy guaranteeing from an information state. -/
def AdaptivePolicyGuarantees
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F)
    (info : InfoState F) : Prop :=
  AdaptivePolicyKernel F Allowed Requirement policy info

theorem adaptivePolicyKernelOp_mono
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F) :
    Mono (adaptivePolicyKernelOp F Allowed Requirement policy) := by
  intro p q hpq info hInfo
  rcases hInfo with ⟨hConstraint, hReq, hKeep⟩
  rcases hKeep with ⟨hAllowed, hEnabled, hSafe⟩
  exact ⟨hConstraint, hReq, hAllowed, hEnabled, by
    intro next hStep
    exact hpq next (hSafe next hStep)⟩

theorem adaptivePolicyKernel_fixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F) :
    PSub (AdaptivePolicyKernel F Allowed Requirement policy)
        (adaptivePolicyKernelOp F Allowed Requirement policy
          (AdaptivePolicyKernel F Allowed Requirement policy)) /\
      PSub
        (adaptivePolicyKernelOp F Allowed Requirement policy
          (AdaptivePolicyKernel F Allowed Requirement policy))
        (AdaptivePolicyKernel F Allowed Requirement policy) := by
  exact gfp_fixed
    (adaptivePolicyKernelOp_mono F Allowed Requirement policy)

theorem adaptivePolicyKernel_action_safe
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F)
    {info : InfoState F}
    (hInfo : AdaptivePolicyKernel F Allowed Requirement policy info) :
    ActionRobustKeeps (liftedDecision F) (liftedAllowed F Allowed)
      (AdaptivePolicyKernel F Allowed Requirement policy)
      info (policy info) := by
  exact ((adaptivePolicyKernel_fixed F Allowed Requirement policy).left
    info hInfo).right.right

theorem adaptivePolicyKernel_sub_adaptiveKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F) :
    PSub (AdaptivePolicyKernel F Allowed Requirement policy)
      (AdaptiveKernel F Allowed Requirement) := by
  apply postfixed_le_gfp
  intro info hInfo
  have hClosed :=
    (adaptivePolicyKernel_fixed F Allowed Requirement policy).left
      info hInfo
  rcases hClosed with ⟨hConstraint, hReq, hKeep⟩
  exact ⟨hConstraint, hReq, policy info, hKeep⟩

theorem adaptivePolicyGuarantee_implies_adaptiveKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : AdaptivePolicy F)
    {info : InfoState F}
    (hInfo : AdaptivePolicyGuarantees F Allowed Requirement policy info) :
    AdaptiveKernel F Allowed Requirement info :=
  adaptivePolicyKernel_sub_adaptiveKernel F Allowed Requirement policy
    info hInfo

noncomputable section

/--
Canonical adaptive-kernel policy: choose a robust lifted action on adaptive
kernel states and use an arbitrary default elsewhere.
-/
def adaptiveKernelPolicy
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    AdaptivePolicy F := by
  classical
  exact fun info =>
    if hInfo : AdaptiveKernel F Allowed Requirement info then
      Classical.choose
        (adaptiveKernel_has_action F Allowed Requirement hInfo)
    else
      default

theorem adaptiveKernelPolicy_spec
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    {info : InfoState F}
    (hInfo : AdaptiveKernel F Allowed Requirement info) :
    ActionRobustKeeps (liftedDecision F) (liftedAllowed F Allowed)
      (AdaptiveKernel F Allowed Requirement) info
      (adaptiveKernelPolicy F Allowed Requirement info) := by
  classical
  have hSpec :=
    Classical.choose_spec
      (adaptiveKernel_has_action F Allowed Requirement hInfo)
  simpa [adaptiveKernelPolicy, hInfo] using hSpec

theorem adaptiveKernelPolicy_postfixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    Postfixed
      (adaptivePolicyKernelOp F Allowed Requirement
        (adaptiveKernelPolicy F Allowed Requirement))
      (AdaptiveKernel F Allowed Requirement) := by
  intro info hInfo
  exact ⟨
    (robustCorridor_sub_constraint (liftedDecision F)
      (liftedAllowed F Allowed) (liftedRequirement F Requirement)
      info hInfo),
    (robustCorridor_sub_requirement (liftedDecision F)
      (liftedAllowed F Allowed) (liftedRequirement F Requirement)
      info hInfo),
    adaptiveKernelPolicy_spec F Allowed Requirement hInfo⟩

theorem adaptiveKernel_sub_adaptivePolicyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    PSub (AdaptiveKernel F Allowed Requirement)
      (AdaptivePolicyKernel F Allowed Requirement
        (adaptiveKernelPolicy F Allowed Requirement)) := by
  exact postfixed_le_gfp
    (adaptiveKernelPolicy_postfixed F Allowed Requirement)

/--
Policy-level fixed-point correspondence for the adaptive lift: a stationary
information-state policy guarantees exactly from adaptive-kernel states.
-/
theorem exists_adaptivePolicyGuarantees_iff_adaptiveKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    (info : InfoState F) :
    (exists policy : AdaptivePolicy F,
      AdaptivePolicyGuarantees F Allowed Requirement policy info) <->
        AdaptiveKernel F Allowed Requirement info := by
  constructor
  · intro h
    rcases h with ⟨policy, hPolicy⟩
    exact adaptivePolicyGuarantee_implies_adaptiveKernel
      F Allowed Requirement policy hPolicy
  · intro hInfo
    exact ⟨adaptiveKernelPolicy F Allowed Requirement,
      adaptiveKernel_sub_adaptivePolicyKernel F Allowed Requirement
        info hInfo⟩

end

end AdaptiveFixedWorld
end Decision
end OmegaProper
