import OmegaProper.Decision.HistoryContainment

/-!
OmegaProper.Decision.TrajectoryBridge

Positive trajectory bridge for stationary ambiguity-family guarantees.

The fixed-point containment stack proves that stationary guarantees are exactly
RVK membership. This file adds the conservative operational reading: from a
stationary guarantee, each model in the ambiguity family admits an infinite
policy-following trace whose states remain in the closed-loop kernel, the
declared constraint/requirement surface, and the RVK.

This is only the positive bridge. It does not formalize maximal finite
deadlock-failure semantics or the converse from trajectory properties back to
the fixed point. It does not define value, agency, identity, moral standing,
stochastic risk, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace TrajectoryBridge

open AmbiguityFamily
open Containment

universe u v w

/-- An infinite trace following a stationary policy in one model. -/
structure InfinitePolicyTrace
    (F : AmbFamily State Action)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State) where
  state : Nat -> State
  starts : state 0 = start
  step : forall n,
    F.Step i (state n) (policy (state n)) (state (n + 1))

/-- The trace remains inside the closed-loop kernel at every time. -/
def TraceInPolicyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (trace : Nat -> State) : Prop :=
  forall n, PolicyKernel F Allowed Requirement policy (trace n)

/-- The trace remains inside the ambiguity-family RVK at every time. -/
def TraceInRVK
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (trace : Nat -> State) : Prop :=
  forall n, RVK F Allowed Requirement (trace n)

/-- The trace remains inside the declared constraint at every time. -/
def TraceInConstraint
    (F : AmbFamily State Action)
    (trace : Nat -> State) : Prop :=
  forall n, F.Constraint (trace n)

/-- The trace remains inside the declared requirement at every time. -/
def TraceInRequirement
    (Requirement : State -> Prop)
    (trace : Nat -> State) : Prop :=
  forall n, Requirement (trace n)

noncomputable section

/--
Internal dependent trace: at each time it stores both the current state and the
proof that the state remains in the policy kernel.
-/
def policyKernelTrace
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    Nat -> {x : State // PolicyKernel F Allowed Requirement policy x}
  | 0 => ⟨start, hStart⟩
  | n + 1 =>
      let cur := policyKernelTrace F Allowed Requirement policy i start hStart n
      let hKeep :=
        policyKernel_action_safe F Allowed Requirement policy cur.property
      let hEnabled := hKeep.2.1 i
      let next := Classical.choose hEnabled
      ⟨next, hKeep.2.2 i next (Classical.choose_spec hEnabled)⟩

/-- The state component of the extracted dependent trace. -/
def policyTrace
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    Nat -> State :=
  fun n => (policyKernelTrace F Allowed Requirement policy i start hStart n).1

theorem policyTrace_starts
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    policyTrace F Allowed Requirement policy i start hStart 0 = start := by
  rfl

theorem policyTrace_in_policyKernel
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    TraceInPolicyKernel F Allowed Requirement policy
      (policyTrace F Allowed Requirement policy i start hStart) := by
  intro n
  exact (policyKernelTrace F Allowed Requirement policy i start hStart n).2

theorem policyTrace_step
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    forall n,
      F.Step i
        (policyTrace F Allowed Requirement policy i start hStart n)
        (policy (policyTrace F Allowed Requirement policy i start hStart n))
        (policyTrace F Allowed Requirement policy i start hStart (n + 1)) := by
  intro n
  unfold policyTrace
  let cur := policyKernelTrace F Allowed Requirement policy i start hStart n
  let hKeep :=
    policyKernel_action_safe F Allowed Requirement policy cur.property
  let hEnabled := hKeep.2.1 i
  change F.Step i cur.1 (policy cur.1) (Classical.choose hEnabled)
  exact Classical.choose_spec hEnabled

theorem policyTrace_in_constraint
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    TraceInConstraint F
      (policyTrace F Allowed Requirement policy i start hStart) := by
  intro n
  exact policyKernel_sub_constraint F Allowed Requirement policy
    (policyTrace F Allowed Requirement policy i start hStart n)
    (policyTrace_in_policyKernel F Allowed Requirement policy i start hStart n)

theorem policyTrace_in_requirement
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    TraceInRequirement Requirement
      (policyTrace F Allowed Requirement policy i start hStart) := by
  intro n
  exact policyKernel_sub_requirement F Allowed Requirement policy
    (policyTrace F Allowed Requirement policy i start hStart n)
    (policyTrace_in_policyKernel F Allowed Requirement policy i start hStart n)

theorem policyTrace_in_rvk
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    (i : F.Model)
    (start : State)
    (hStart : PolicyKernel F Allowed Requirement policy start) :
    TraceInRVK F Allowed Requirement
      (policyTrace F Allowed Requirement policy i start hStart) := by
  intro n
  exact policyKernel_sub_rvk F Allowed Requirement policy
    (policyTrace F Allowed Requirement policy i start hStart n)
    (policyTrace_in_policyKernel F Allowed Requirement policy i start hStart n)

/--
A stationary fixed-point guarantee supplies an infinite policy-following trace
for every model in the ambiguity family.
-/
theorem stationaryGuarantee_has_model_trace
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (policy : StationaryPolicy State Action)
    {start : State}
    (hStart : StationaryGuarantees F Allowed Requirement policy start)
    (i : F.Model) :
    exists tr : InfinitePolicyTrace F policy i start,
      TraceInPolicyKernel F Allowed Requirement policy tr.state /\
      TraceInConstraint F tr.state /\
      TraceInRequirement Requirement tr.state /\
      TraceInRVK F Allowed Requirement tr.state := by
  let trState := policyTrace F Allowed Requirement policy i start hStart
  exact ⟨
    { state := trState
      starts := policyTrace_starts F Allowed Requirement policy i start hStart
      step := policyTrace_step F Allowed Requirement policy i start hStart },
    policyTrace_in_policyKernel F Allowed Requirement policy i start hStart,
    policyTrace_in_constraint F Allowed Requirement policy i start hStart,
    policyTrace_in_requirement F Allowed Requirement policy i start hStart,
    policyTrace_in_rvk F Allowed Requirement policy i start hStart⟩

/--
Any RVK state supplies an infinite trace in every model under the extracted RVK
policy.
-/
theorem rvk_has_model_trace
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    [Inhabited Action]
    {start : State}
    (hStart : RVK F Allowed Requirement start)
    (i : F.Model) :
    exists tr : InfinitePolicyTrace F
        (rvkPolicy F Allowed Requirement) i start,
      TraceInPolicyKernel F Allowed Requirement
        (rvkPolicy F Allowed Requirement) tr.state /\
      TraceInConstraint F tr.state /\
      TraceInRequirement Requirement tr.state /\
      TraceInRVK F Allowed Requirement tr.state :=
  stationaryGuarantee_has_model_trace F Allowed Requirement
    (rvkPolicy F Allowed Requirement)
    (rvk_sub_rvkPolicyKernel F Allowed Requirement start hStart) i

end

end TrajectoryBridge
end Decision
end OmegaProper
