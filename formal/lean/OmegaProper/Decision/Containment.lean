import OmegaProper.Decision.AmbiguityFamily

/-!
OmegaProper.Decision.Containment

Stationary containment for ambiguity-family robust viability.

This module stays fixed-point-first. A stationary policy induces a closed-loop
kernel. Persistence-guarantee language is represented by membership in that
kernel, and containment is proved by comparing that closed-loop kernel to the
shared-action RVK from `AmbiguityFamily`.

This is not the full trajectory theorem. It does not define value, agency,
identity, moral standing, stochastic risk, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace Containment

open Trajectory.PredicateFixpoint
open AmbiguityFamily

universe u v w

/-- A stationary policy chooses one action at each state. -/
abbrev StationaryPolicy (State : Type u) (Action : Type v) :=
  State -> Action

/-- A stationary policy robustly keeps a set when its chosen action does. -/
def PolicyRobustKeepsAmb
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (S : State -> Prop)
    (policy : StationaryPolicy State Action)
    (x : State) : Prop :=
  ActionRobustKeepsAmb F Allowed S x (policy x)

/-- Closed-loop robust predecessor for one fixed stationary policy. -/
def policyKernelOp
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (S : State -> Prop) :
    State -> Prop :=
  fun x =>
    F.Constraint x /\
    Requirement x /\
    PolicyRobustKeepsAmb F Allowed S policy x

/-- Closed-loop kernel for a fixed stationary policy. -/
def PolicyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    State -> Prop :=
  gfp (policyKernelOp F Allowed Requirement policy)

/--
Fixed-point reading of "the stationary policy guarantees persistence from x."

The trajectory bridge is intentionally deferred; this is the closed-loop kernel
surface used for the containment theorem.
-/
def StationaryGuarantees
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (x : State) : Prop :=
  PolicyKernel F Allowed Requirement policy x

theorem policyKernelOp_mono
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    Mono (policyKernelOp F Allowed Requirement policy) := by
  intro p q hpq x hx
  rcases hx with ⟨hConstraint, hReq, hKeep⟩
  rcases hKeep with ⟨hAllowed, hEnabled, hSafe⟩
  exact ⟨hConstraint, hReq, hAllowed, hEnabled,
    (by
      intro i y hStep
      exact hpq y (hSafe i y hStep))⟩

theorem policyKernel_fixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    PSub (PolicyKernel F Allowed Requirement policy)
        (policyKernelOp F Allowed Requirement policy
          (PolicyKernel F Allowed Requirement policy)) /\
      PSub
        (policyKernelOp F Allowed Requirement policy
          (PolicyKernel F Allowed Requirement policy))
        (PolicyKernel F Allowed Requirement policy) := by
  exact gfp_fixed (policyKernelOp_mono F Allowed Requirement policy)

theorem policyKernel_sub_constraint
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    PSub (PolicyKernel F Allowed Requirement policy) F.Constraint := by
  intro x hx
  exact ((policyKernel_fixed F Allowed Requirement policy).left x hx).left

theorem policyKernel_sub_requirement
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    PSub (PolicyKernel F Allowed Requirement policy) Requirement := by
  intro x hx
  exact ((policyKernel_fixed F Allowed Requirement policy).left x hx).right.left

theorem policyKernel_action_safe
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x : State}
    (hx : PolicyKernel F Allowed Requirement policy x) :
    ActionRobustKeepsAmb F Allowed
      (PolicyKernel F Allowed Requirement policy) x (policy x) := by
  exact ((policyKernel_fixed F Allowed Requirement policy).left x hx).right.right

/-- A closed-loop guarantee is confined by the shared-action RVK. -/
theorem policyKernel_sub_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    PSub (PolicyKernel F Allowed Requirement policy)
      (RVK F Allowed Requirement) := by
  apply postfixed_le_gfp
  intro x hx
  have hClosed :=
    (policyKernel_fixed F Allowed Requirement policy).left x hx
  rcases hClosed with ⟨hConstraint, hReq, hKeepAmb⟩
  have hKeepMerged :
      ActionRobustKeeps (mergedDecision F)
        (familyEnabledAllowed F Allowed)
        (PolicyKernel F Allowed Requirement policy) x (policy x) := by
    exact (actionRobustKeepsAmb_iff_merged F Allowed
      (PolicyKernel F Allowed Requirement policy) x (policy x)).mp hKeepAmb
  exact ⟨hConstraint, hReq, policy x, hKeepMerged⟩

theorem stationaryGuarantee_implies_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x : State}
    (hx : StationaryGuarantees F Allowed Requirement policy x) :
    RVK F Allowed Requirement x :=
  policyKernel_sub_rvk F Allowed Requirement policy x hx

theorem policyKernel_step_closed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x y : State} {i : F.Model}
    (hx : PolicyKernel F Allowed Requirement policy x)
    (hStep : F.Step i x (policy x) y) :
    PolicyKernel F Allowed Requirement policy y := by
  rcases policyKernel_action_safe F Allowed Requirement policy hx with
    ⟨_hAllowed, _hEnabled, hSafe⟩
  exact hSafe i y hStep

/-- Finite reachability under a stationary policy, allowing model choice per step. -/
inductive PolicyReach
    (F : AmbFamily State Action)
    (policy : StationaryPolicy State Action) :
    State -> State -> Prop where
  | refl (x : State) : PolicyReach F policy x x
  | step {x y z : State} {i : F.Model} :
      PolicyReach F policy x y ->
      F.Step i y (policy y) z ->
      PolicyReach F policy x z

theorem policyKernel_reach_closed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x y : State}
    (hx : PolicyKernel F Allowed Requirement policy x)
    (hReach : PolicyReach F policy x y) :
    PolicyKernel F Allowed Requirement policy y := by
  induction hReach with
  | refl =>
      exact hx
  | step hReach hStep ih =>
      exact policyKernel_step_closed F Allowed Requirement policy ih hStep

/--
Confinement: every finite policy-reachable state from a guaranteed start lies
inside the shared-action RVK.
-/
theorem stationaryGuarantee_reachable_confined
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x y : State}
    (hx : StationaryGuarantees F Allowed Requirement policy x)
    (hReach : PolicyReach F policy x y) :
    RVK F Allowed Requirement y :=
  policyKernel_sub_rvk F Allowed Requirement policy y
    (policyKernel_reach_closed F Allowed Requirement policy hx hReach)

noncomputable section

/--
Canonical RVK policy: choose a shared safe action on RVK states and use an
arbitrary default elsewhere.
-/
def rvkPolicy
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    StationaryPolicy State Action := by
  classical
  exact fun x =>
    if hx : RVK F Allowed Requirement x then
      Classical.choose (rvk_has_shared_action F Allowed Requirement hx)
    else
      default

theorem rvkPolicy_spec
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    {x : State}
    (hx : RVK F Allowed Requirement x) :
    ActionRobustKeepsAmb F Allowed
      (RVK F Allowed Requirement) x
      (rvkPolicy F Allowed Requirement x) := by
  classical
  have hSpec :=
    Classical.choose_spec (rvk_has_shared_action F Allowed Requirement hx)
  simpa [rvkPolicy, hx] using hSpec

theorem rvkPolicy_postfixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    Postfixed
      (policyKernelOp F Allowed Requirement
        (rvkPolicy F Allowed Requirement))
      (RVK F Allowed Requirement) := by
  intro x hx
  exact ⟨rvk_sub_constraint F Allowed Requirement x hx,
    rvk_sub_requirement F Allowed Requirement x hx,
    rvkPolicy_spec F Allowed Requirement hx⟩

theorem rvk_sub_rvkPolicyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    PSub (RVK F Allowed Requirement)
      (PolicyKernel F Allowed Requirement
        (rvkPolicy F Allowed Requirement)) := by
  exact postfixed_le_gfp (rvkPolicy_postfixed F Allowed Requirement)

/-- One stationary policy guarantees from every RVK state simultaneously. -/
theorem rvkPolicy_guarantees_all_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action] :
    forall x,
      RVK F Allowed Requirement x ->
        StationaryGuarantees F Allowed Requirement
          (rvkPolicy F Allowed Requirement) x :=
  rvk_sub_rvkPolicyKernel F Allowed Requirement

/--
Stationary existence theorem for the fixed-point guarantee surface.

The `[Inhabited Action]` assumption supplies the arbitrary action needed to
make the extracted policy total outside the RVK.
-/
theorem exists_stationaryGuarantees_iff_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    (x : State) :
    (exists policy : StationaryPolicy State Action,
      StationaryGuarantees F Allowed Requirement policy x) <->
        RVK F Allowed Requirement x := by
  constructor
  · intro h
    rcases h with ⟨policy, hx⟩
    exact stationaryGuarantee_implies_rvk F Allowed Requirement policy hx
  · intro hx
    exact ⟨rvkPolicy F Allowed Requirement,
      rvk_sub_rvkPolicyKernel F Allowed Requirement x hx⟩

end

end Containment
end Decision
end OmegaProper
