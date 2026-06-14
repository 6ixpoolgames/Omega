import OmegaProper.Trajectory.TrajectorySemantics

/-!
OmegaProper.Trajectory.ReachabilityReflection

Reflection contracts for reachability under presentations.

`PhantomReachability` shows that an unsound presentation can fabricate apparent
reachability. This file gives the positive dynamics-side contract: if abstract
targets and abstract steps reflect back to exact targets and exact steps, then
abstract reachability reflects back to exact reachability.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace ReachabilityReflection

open PredicateFixpoint
open ReachabilityViability
open TrajectorySemantics

universe u v

/--
Abstract target membership reflects to exact target membership through the
presentation.
-/
def TargetReflects
    (DX : Dyn.{u})
    (DQ : Dyn.{v})
    (present : DX.State -> DQ.State)
    (targetX : DX.State -> Prop)
    (targetQ : DQ.State -> Prop) : Prop :=
  forall x, targetQ (present x) -> targetX x

/--
Every abstract step out of a presented exact state is witnessed by an exact
step from that exact state.
-/
def StepReflects
    (DX : Dyn.{u})
    (DQ : Dyn.{v})
    (present : DX.State -> DQ.State) : Prop :=
  forall x z,
    DQ.Next (present x) z ->
      exists y, DX.Next x y /\ present y = z

/--
A presentation reflects reachability when it reflects both targets and steps.
This is a dynamics contract, not a quotient or identity claim.
-/
structure ReachabilityReflectingPresentation
    (DX : Dyn.{u})
    (DQ : Dyn.{v})
    (present : DX.State -> DQ.State)
    (targetX : DX.State -> Prop)
    (targetQ : DQ.State -> Prop) where
  target_reflects : TargetReflects DX DQ present targetX targetQ
  step_reflects : StepReflects DX DQ present

/--
If abstract target membership and abstract steps reflect to exact target
membership and exact steps, then abstract reachability cannot be fabricated:
abstract reachability of `present x` implies exact reachability of `x`.
-/
theorem abstractReach_reflects_exactReach
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {targetX : DX.State -> Prop}
    {targetQ : DQ.State -> Prop}
    (hReflect :
      ReachabilityReflectingPresentation DX DQ present targetX targetQ)
    {x : DX.State}
    (hReachQ : Reach DQ targetQ (present x)) :
    Reach DX targetX x := by
  let pullbackReach : DQ.State -> Prop :=
    fun q => forall x0, present x0 = q -> Reach DX targetX x0
  have hPref : Prefixed (reachOp DQ targetQ) pullbackReach := by
    intro q hq x0 hx0q
    cases hq with
    | inl hTargetQ =>
        exact target_sub_reach DX targetX x0
          (hReflect.target_reflects x0 (by
            simpa [hx0q] using hTargetQ))
    | inr hStepQ =>
        match hStepQ with
        | Exists.intro z hz =>
            have hNextFromPresented :
                DQ.Next (present x0) z := by
              simpa [hx0q] using hz.left
            match hReflect.step_reflects x0 z hNextFromPresented with
            | Exists.intro y hy =>
                exact reach_step DX targetX
                  hy.left
                  (hz.right y hy.right)
  exact hReachQ pullbackReach hPref x rfl

/-- Direct spelling without packaging the two reflection hypotheses. -/
theorem abstractReach_reflects_exactReach_of_reflects
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {targetX : DX.State -> Prop}
    {targetQ : DQ.State -> Prop}
    (hTarget : TargetReflects DX DQ present targetX targetQ)
    (hStep : StepReflects DX DQ present)
    {x : DX.State}
    (hReachQ : Reach DQ targetQ (present x)) :
    Reach DX targetX x := by
  exact abstractReach_reflects_exactReach
    { target_reflects := hTarget, step_reflects := hStep }
    hReachQ

/--
Path-level reflection: an abstract finite path to the abstract target, starting
from a presented exact state, reflects to an exact finite path to the exact
target.

This reuses the fixed-point reflection theorem plus the finite-path semantics
for `Reach`.
-/
theorem abstractFinitePath_reflects_exactFinitePath
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {targetX : DX.State -> Prop}
    {targetQ : DQ.State -> Prop}
    (hReflect :
      ReachabilityReflectingPresentation DX DQ present targetX targetQ)
    {x : DX.State}
    (hPathQ : FinitePathToTarget DQ targetQ (present x)) :
    FinitePathToTarget DX targetX x := by
  exact reach_implies_finitePathToTarget
    (abstractReach_reflects_exactReach
      hReflect
      (finitePathToTarget_implies_reach hPathQ))

/-- Direct spelling without packaging the two reflection hypotheses. -/
theorem abstractFinitePath_reflects_exactFinitePath_of_reflects
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {targetX : DX.State -> Prop}
    {targetQ : DQ.State -> Prop}
    (hTarget : TargetReflects DX DQ present targetX targetQ)
    (hStep : StepReflects DX DQ present)
    {x : DX.State}
    (hPathQ : FinitePathToTarget DQ targetQ (present x)) :
    FinitePathToTarget DX targetX x := by
  exact abstractFinitePath_reflects_exactFinitePath
    { target_reflects := hTarget, step_reflects := hStep }
    hPathQ

end ReachabilityReflection
end Trajectory
end OmegaProper
