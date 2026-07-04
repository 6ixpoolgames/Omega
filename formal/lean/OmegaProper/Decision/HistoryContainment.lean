import OmegaProper.Decision.Containment

/-!
OmegaProper.Decision.HistoryContainment

Fixed-point history-policy containment for ambiguity-family robust viability.

A history policy may choose an action from the prior finite history and current
state. Its guarantee kernel is a greatest fixed point over `(history, state)`
pairs. The main result is that such history dependence does not enlarge the
set of states from which persistence can be guaranteed, at this fixed-point
level: existence of a history-policy guarantee is equivalent to membership in
the shared-action RVK, hence equivalent to existence of a stationary guarantee.

This remains below trajectory/maximality semantics. It does not define value,
agency, identity, moral standing, stochastic risk, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace HistoryContainment

open Trajectory.PredicateFixpoint
open AmbiguityFamily
open Containment

universe u v w

/-- A history policy sees the prior finite history and the current state. -/
abbrev HistoryPolicy (State : Type u) (Action : Type v) :=
  List State -> State -> Action

/-- Extend the prior history by the state whose action is now being taken. -/
def extendHistory (hist : List State) (x : State) : List State :=
  hist ++ [x]

/--
History-policy closed-loop operator over `(history, current state)` pairs.

The successor state is checked against the kernel at the extended history.
-/
def historyKernelOp
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action)
    (S : (List State × State) -> Prop) :
    (List State × State) -> Prop :=
  fun hx =>
    F.Constraint hx.2 /\
    Requirement hx.2 /\
    ActionRobustKeepsAmb F Allowed
      (fun y => S (extendHistory hx.1 hx.2, y))
      hx.2 (sigma hx.1 hx.2)

/-- History-policy guarantee kernel. -/
def HistoryKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action) :
    List State -> State -> Prop :=
  fun hist x => gfp (historyKernelOp F Allowed Requirement sigma) (hist, x)

/-- Fixed-point reading of a history policy guaranteeing from a site. -/
def HistoryGuarantees
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action)
    (hist : List State)
    (x : State) : Prop :=
  HistoryKernel F Allowed Requirement sigma hist x

theorem historyKernelOp_mono
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action) :
    Mono (historyKernelOp F Allowed Requirement sigma) := by
  intro p q hpq hx h
  rcases h with ⟨hConstraint, hReq, hKeep⟩
  rcases hKeep with ⟨hAllowed, hEnabled, hSafe⟩
  exact ⟨hConstraint, hReq, hAllowed, hEnabled,
    (by
      intro i y hStep
      exact hpq (extendHistory hx.1 hx.2, y) (hSafe i y hStep))⟩

theorem historyKernel_fixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action) :
    PSub (fun hx => HistoryKernel F Allowed Requirement sigma hx.1 hx.2)
        (historyKernelOp F Allowed Requirement sigma
          (fun hx => HistoryKernel F Allowed Requirement sigma hx.1 hx.2)) /\
      PSub
        (historyKernelOp F Allowed Requirement sigma
          (fun hx => HistoryKernel F Allowed Requirement sigma hx.1 hx.2))
        (fun hx => HistoryKernel F Allowed Requirement sigma hx.1 hx.2) := by
  exact gfp_fixed (historyKernelOp_mono F Allowed Requirement sigma)

theorem historyKernel_sub_constraint
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action)
    (hist : List State) :
    PSub (HistoryKernel F Allowed Requirement sigma hist) F.Constraint := by
  intro x hx
  exact ((historyKernel_fixed F Allowed Requirement sigma).left
    (hist, x) hx).left

theorem historyKernel_sub_requirement
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action)
    (hist : List State) :
    PSub (HistoryKernel F Allowed Requirement sigma hist) Requirement := by
  intro x hx
  exact ((historyKernel_fixed F Allowed Requirement sigma).left
    (hist, x) hx).right.left

theorem historyKernel_action_safe
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action)
    {hist : List State} {x : State}
    (hx : HistoryKernel F Allowed Requirement sigma hist x) :
    ActionRobustKeepsAmb F Allowed
      (fun y => HistoryKernel F Allowed Requirement sigma
        (extendHistory hist x) y)
      x (sigma hist x) := by
  exact ((historyKernel_fixed F Allowed Requirement sigma).left
    (hist, x) hx).right.right

theorem historyKernel_step_closed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action)
    {hist : List State} {x y : State} {i : F.Model}
    (hx : HistoryKernel F Allowed Requirement sigma hist x)
    (hStep : F.Step i x (sigma hist x) y) :
    HistoryKernel F Allowed Requirement sigma (extendHistory hist x) y := by
  rcases historyKernel_action_safe F Allowed Requirement sigma hx with
    ⟨_hAllowed, _hEnabled, hSafe⟩
  exact hSafe i y hStep

/-- Some history policy guarantees at the current state, for some history. -/
def SomeHistoryGuarantee
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    State -> Prop :=
  fun x =>
    exists sigma hist,
      HistoryGuarantees F Allowed Requirement sigma hist x

/--
The union of all history-policy guarantee kernels is postfixed for the ordinary
ambiguity-family RVK operator.
-/
theorem someHistoryGuarantee_postfixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    Postfixed
      (robustCorridorOp (mergedDecision F)
        (familyEnabledAllowed F Allowed) Requirement)
      (SomeHistoryGuarantee F Allowed Requirement) := by
  intro x hx
  rcases hx with ⟨sigma, hist, hHist⟩
  have hClosed :=
    (historyKernel_fixed F Allowed Requirement sigma).left
      (hist, x) hHist
  rcases hClosed with ⟨hConstraint, hReq, hKeepHist⟩
  rcases hKeepHist with ⟨hAllowed, hEnabled, hSafeHist⟩
  have hKeepSome :
      ActionRobustKeepsAmb F Allowed
        (SomeHistoryGuarantee F Allowed Requirement)
        x (sigma hist x) := by
    exact ⟨hAllowed, hEnabled, by
      intro i y hStep
      exact ⟨sigma, extendHistory hist x, hSafeHist i y hStep⟩⟩
  have hKeepMerged :
      ActionRobustKeeps (mergedDecision F)
        (familyEnabledAllowed F Allowed)
        (SomeHistoryGuarantee F Allowed Requirement)
        x (sigma hist x) := by
    exact (actionRobustKeepsAmb_iff_merged F Allowed
      (SomeHistoryGuarantee F Allowed Requirement)
      x (sigma hist x)).mp hKeepSome
  exact ⟨hConstraint, hReq, sigma hist x, hKeepMerged⟩

theorem someHistoryGuarantee_sub_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    PSub (SomeHistoryGuarantee F Allowed Requirement)
      (RVK F Allowed Requirement) :=
  postfixed_le_gfp
    (someHistoryGuarantee_postfixed F Allowed Requirement)

theorem historyGuarantee_implies_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (sigma : HistoryPolicy State Action)
    (hist : List State)
    {x : State}
    (hx : HistoryGuarantees F Allowed Requirement sigma hist x) :
    RVK F Allowed Requirement x :=
  someHistoryGuarantee_sub_rvk F Allowed Requirement x
    ⟨sigma, hist, hx⟩

/-- Turn a stationary policy into a history policy by ignoring history. -/
def stationaryAsHistory
    (policy : StationaryPolicy State Action) :
    HistoryPolicy State Action :=
  fun _hist x => policy x

noncomputable section

theorem rvkHistoryPolicy_postfixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    Postfixed
      (historyKernelOp F Allowed Requirement
        (stationaryAsHistory (rvkPolicy F Allowed Requirement)))
      (fun hx : List State × State => RVK F Allowed Requirement hx.2) := by
  intro hx hRVK
  have hSpec :=
    rvkPolicy_spec F Allowed Requirement hRVK
  rcases hSpec with ⟨hAllowed, hEnabled, hSafe⟩
  exact ⟨rvk_sub_constraint F Allowed Requirement hx.2 hRVK,
    rvk_sub_requirement F Allowed Requirement hx.2 hRVK,
    hAllowed, hEnabled,
    (by
      intro i y hStep
      exact hSafe i y hStep)⟩

theorem rvk_has_historyGuarantee
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    (hist : List State)
    {x : State}
    (hx : RVK F Allowed Requirement x) :
    HistoryGuarantees F Allowed Requirement
      (stationaryAsHistory (rvkPolicy F Allowed Requirement)) hist x := by
  exact postfixed_le_gfp
    (rvkHistoryPolicy_postfixed F Allowed Requirement)
    (hist, x) hx

/--
History-policy guarantees exist exactly on the RVK.

This is the fixed-point memorylessness result: history dependence does not
expand the robust persistence-guarantee region.
-/
theorem exists_historyGuarantees_iff_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    (x : State) :
    (exists sigma : HistoryPolicy State Action,
      HistoryGuarantees F Allowed Requirement sigma [] x) <->
        RVK F Allowed Requirement x := by
  constructor
  · intro h
    rcases h with ⟨sigma, hSigma⟩
    exact historyGuarantee_implies_rvk F Allowed Requirement sigma [] hSigma
  · intro hx
    exact ⟨stationaryAsHistory (rvkPolicy F Allowed Requirement),
      rvk_has_historyGuarantee F Allowed Requirement [] hx⟩

/-- History-policy existence is equivalent to stationary-policy existence. -/
theorem exists_historyGuarantees_iff_stationaryGuarantees
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    (x : State) :
    (exists sigma : HistoryPolicy State Action,
      HistoryGuarantees F Allowed Requirement sigma [] x) <->
    (exists policy : StationaryPolicy State Action,
      StationaryGuarantees F Allowed Requirement policy x) := by
  constructor
  · intro h
    have hRVK :=
      (exists_historyGuarantees_iff_rvk F Allowed Requirement x).mp h
    exact (exists_stationaryGuarantees_iff_rvk F Allowed Requirement x).mpr hRVK
  · intro h
    have hRVK :=
      (exists_stationaryGuarantees_iff_rvk F Allowed Requirement x).mp h
    exact (exists_historyGuarantees_iff_rvk F Allowed Requirement x).mpr hRVK

end

end HistoryContainment
end Decision
end OmegaProper
