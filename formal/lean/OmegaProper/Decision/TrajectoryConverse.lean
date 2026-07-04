import OmegaProper.Decision.TrajectoryBridge

/-!
OmegaProper.Decision.TrajectoryConverse

Finite bad-prefix semantics for stationary ambiguity-family guarantees.

The RVK operator is robust to ambiguity after every step: a successor produced
by any model must again be safe for every model. The matching trajectory
semantics is therefore switching-adversary semantics, where a finite trace may
choose a model at each transition.

This module proves that the no-bad-finite-prefix reading is equivalent to the
stationary closed-loop fixed point. It does not define value, agency, identity,
moral standing, stochastic risk, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace TrajectoryConverse

open AmbiguityFamily
open Containment
open TrajectoryBridge
open Trajectory.PredicateFixpoint

universe u v w

/-- A finite policy-following trace where the adversary may choose a model per step. -/
structure FiniteSwitchingPolicyTrace
    (F : AmbFamily State Action)
    (policy : StationaryPolicy State Action)
    (start : State)
    (len : Nat) where
  state : Nat -> State
  model : Nat -> F.Model
  starts : state 0 = start
  step : forall n, n < len ->
    F.Step (model n) (state n) (policy (state n)) (state (n + 1))

/-- No successor for the policy action in a particular model. -/
def Deadlocked
    (F : AmbFamily State Action)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (x : State) : Prop :=
  Not (exists y, F.Step i x (policy x) y)

/-- A state-local bad event: outside constraint, requirement, or allowedness. -/
def BadState
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (x : State) : Prop :=
  Not (F.Constraint x) \/
    Not (Requirement x) \/
    Not (Allowed x (policy x))

/-- A finite bad prefix: bad state along the trace or deadlock at the endpoint. -/
def BadFiniteSwitchingTrace
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {start : State} {len : Nat}
    (tr : FiniteSwitchingPolicyTrace F policy start len) : Prop :=
  (exists n, n <= len /\ BadState F Allowed Requirement policy (tr.state n)) \/
    exists i : F.Model, Deadlocked F policy i (tr.state len)

/--
Trajectory guarantee as absence of finite switching bad prefixes.

This is a safety-game style finite-refutation semantics, not a maximal
trajectory object.
-/
def SwitchingTrajectoryGuarantees
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (start : State) : Prop :=
  forall len,
    forall tr : FiniteSwitchingPolicyTrace F policy start len,
      Not (BadFiniteSwitchingTrace F Allowed Requirement policy tr)

/-- Length-zero trace at a state, using an arbitrary model as placeholder. -/
def singletonTrace
    (F : AmbFamily State Action)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (x : State) :
    FiniteSwitchingPolicyTrace F policy x 0 where
  state := fun _ => x
  model := fun _ => i
  starts := rfl
  step := by
    intro n hn
    exact False.elim (Nat.not_lt_zero n hn)

theorem switchingGuarantee_constraint
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x : State}
    (h : SwitchingTrajectoryGuarantees F Allowed Requirement policy x) :
    F.Constraint x := by
  rcases F.modelNonempty with ⟨i⟩
  by_contra hBad
  exact h 0 (singletonTrace F policy i x)
    (Or.inl ⟨0, Nat.le_refl 0, Or.inl hBad⟩)

theorem switchingGuarantee_requirement
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x : State}
    (h : SwitchingTrajectoryGuarantees F Allowed Requirement policy x) :
    Requirement x := by
  rcases F.modelNonempty with ⟨i⟩
  by_contra hBad
  exact h 0 (singletonTrace F policy i x)
    (Or.inl ⟨0, Nat.le_refl 0, Or.inr (Or.inl hBad)⟩)

theorem switchingGuarantee_allowed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x : State}
    (h : SwitchingTrajectoryGuarantees F Allowed Requirement policy x) :
    Allowed x (policy x) := by
  rcases F.modelNonempty with ⟨i⟩
  by_contra hBad
  exact h 0 (singletonTrace F policy i x)
    (Or.inl ⟨0, Nat.le_refl 0, Or.inr (Or.inr hBad)⟩)

theorem switchingGuarantee_enabled
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x : State}
    (h : SwitchingTrajectoryGuarantees F Allowed Requirement policy x) :
    forall i : F.Model, exists y, F.Step i x (policy x) y := by
  intro i
  by_contra hDead
  exact h 0 (singletonTrace F policy i x)
    (Or.inr ⟨i, hDead⟩)

/-- Prepend one policy step to a finite switching trace. -/
def prependTrace
    (F : AmbFamily State Action)
    (policy : StationaryPolicy State Action)
    {x y : State} {i : F.Model} {len : Nat}
    (hStep : F.Step i x (policy x) y)
    (tr : FiniteSwitchingPolicyTrace F policy y len) :
    FiniteSwitchingPolicyTrace F policy x (len + 1) where
  state
    | 0 => x
    | n + 1 => tr.state n
  model
    | 0 => i
    | n + 1 => tr.model n
  starts := rfl
  step := by
    intro n hn
    cases n with
    | zero =>
        change F.Step i x (policy x) (tr.state 0)
        rw [tr.starts]
        exact hStep
    | succ n =>
        have hnTail : n < len := by
          exact Nat.succ_lt_succ_iff.mp hn
        simpa using tr.step n hnTail

theorem bad_prepend_of_bad
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x y : State} {i : F.Model} {len : Nat}
    (hStep : F.Step i x (policy x) y)
    {tr : FiniteSwitchingPolicyTrace F policy y len}
    (hBad : BadFiniteSwitchingTrace F Allowed Requirement policy tr) :
    BadFiniteSwitchingTrace F Allowed Requirement policy
      (prependTrace F policy hStep tr) := by
  cases hBad with
  | inl hState =>
      rcases hState with ⟨n, hn, hBadState⟩
      exact Or.inl ⟨n + 1, Nat.succ_le_succ hn, by
        simpa [prependTrace] using hBadState⟩
  | inr hDead =>
      rcases hDead with ⟨j, hDead⟩
      exact Or.inr ⟨j, by
        simpa [prependTrace] using hDead⟩

theorem switchingGuarantee_step
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x y : State} {i : F.Model}
    (h : SwitchingTrajectoryGuarantees F Allowed Requirement policy x)
    (hStep : F.Step i x (policy x) y) :
    SwitchingTrajectoryGuarantees F Allowed Requirement policy y := by
  intro len tr hBad
  exact h (len + 1) (prependTrace F policy hStep tr)
    (bad_prepend_of_bad F Allowed Requirement policy hStep hBad)

theorem switchingTrajectoryGuarantee_postfixed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    Postfixed (policyKernelOp F Allowed Requirement policy)
      (SwitchingTrajectoryGuarantees F Allowed Requirement policy) := by
  intro x h
  exact ⟨
    switchingGuarantee_constraint F Allowed Requirement policy h,
    switchingGuarantee_requirement F Allowed Requirement policy h,
    switchingGuarantee_allowed F Allowed Requirement policy h,
    switchingGuarantee_enabled F Allowed Requirement policy h,
    (by
      intro i y hStep
      exact switchingGuarantee_step F Allowed Requirement policy h hStep)⟩

theorem switchingTrajectoryGuarantee_implies_policyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    PSub (SwitchingTrajectoryGuarantees F Allowed Requirement policy)
      (PolicyKernel F Allowed Requirement policy) :=
  postfixed_le_gfp
    (switchingTrajectoryGuarantee_postfixed F Allowed Requirement policy)

theorem switchingTrajectoryGuarantee_implies_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action) :
    PSub (SwitchingTrajectoryGuarantees F Allowed Requirement policy)
      (RVK F Allowed Requirement) := by
  intro x h
  exact policyKernel_sub_rvk F Allowed Requirement policy x
    (switchingTrajectoryGuarantee_implies_policyKernel
      F Allowed Requirement policy x h)

theorem policyKernel_policy_allowed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {x : State}
    (hx : PolicyKernel F Allowed Requirement policy x) :
    Allowed x (policy x) := by
  exact (policyKernel_action_safe F Allowed Requirement policy hx).1

theorem finiteTrace_state_in_policyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {start : State} {len : Nat}
    (tr : FiniteSwitchingPolicyTrace F policy start len)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    forall n, n <= len -> PolicyKernel F Allowed Requirement policy (tr.state n) := by
  intro n hn
  induction n with
  | zero =>
      simpa [tr.starts] using hStart
  | succ n ih =>
      have hnPrev : n <= len := Nat.le_trans (Nat.le_succ n) hn
      have hnStep : n < len := Nat.lt_of_succ_le hn
      exact policyKernel_step_closed F Allowed Requirement policy
        (ih hnPrev) (tr.step n hnStep)

theorem policyKernel_no_bad_finiteTrace
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {start : State}
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    SwitchingTrajectoryGuarantees F Allowed Requirement policy start := by
  intro len tr hBad
  cases hBad with
  | inl hState =>
      rcases hState with ⟨n, hn, hBadState⟩
      have hKernelN :=
        finiteTrace_state_in_policyKernel F Allowed Requirement policy tr
          hStart n hn
      cases hBadState with
      | inl hNoConstraint =>
          exact hNoConstraint
            (policyKernel_sub_constraint F Allowed Requirement policy
              (tr.state n) hKernelN)
      | inr hRest =>
          cases hRest with
          | inl hNoRequirement =>
              exact hNoRequirement
                (policyKernel_sub_requirement F Allowed Requirement policy
                  (tr.state n) hKernelN)
          | inr hNoAllowed =>
              exact hNoAllowed
                (policyKernel_policy_allowed F Allowed Requirement policy
                  hKernelN)
  | inr hDead =>
      rcases hDead with ⟨i, hDead⟩
      have hKernelEnd :=
        finiteTrace_state_in_policyKernel F Allowed Requirement policy tr
          hStart len (Nat.le_refl len)
      rcases policyKernel_action_safe F Allowed Requirement policy hKernelEnd with
        ⟨_hAllowed, hEnabled, _hSafe⟩
      exact hDead (hEnabled i)

theorem policyKernel_iff_switchingTrajectoryGuarantees
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (x : State) :
    PolicyKernel F Allowed Requirement policy x <->
      SwitchingTrajectoryGuarantees F Allowed Requirement policy x := by
  constructor
  · exact policyKernel_no_bad_finiteTrace F Allowed Requirement policy
  · exact switchingTrajectoryGuarantee_implies_policyKernel
      F Allowed Requirement policy x

theorem stationaryGuarantee_iff_switchingTrajectoryGuarantees
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (x : State) :
    StationaryGuarantees F Allowed Requirement policy x <->
      SwitchingTrajectoryGuarantees F Allowed Requirement policy x :=
  policyKernel_iff_switchingTrajectoryGuarantees
    F Allowed Requirement policy x

end TrajectoryConverse
end Decision
end OmegaProper
