import OmegaProper.Trajectory.FixedPointTransport
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
open FixedPointTransport
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
  have hPref :
      Prefixed
        (reachOp DQ targetQ)
        (FiberForall present (Reach DX targetX)) := by
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
  exact
    lfp_reflects_of_fiberForall_prefixed
      (FX := reachOp DX targetX)
      (FQ := reachOp DQ targetQ)
      (present := present)
      hPref
      hReachQ

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
Direct path lifting under step reflection.

An abstract finite path starting at `present x` can be lifted to an exact
finite path starting at `x`, ending at some exact state whose presentation is
the abstract endpoint.
-/
theorem abstractFinitePath_lifts_exactEndpoint
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    (hStep : StepReflects DX DQ present)
    {x : DX.State}
    {q0 : DQ.State}
    {q : DQ.State}
    (hStart : present x = q0)
    (hPathQ : FinitePath DQ q0 q) :
    exists y : DX.State, FinitePath DX x y /\ present y = q := by
  match hPathQ with
  | FinitePath.refl =>
      exact Exists.intro x (And.intro FinitePath.refl hStart)
  | @FinitePath.step _ qStart qNext qEnd hStepQ hRest =>
      have hStepFromPresented :
          DQ.Next (present x) qNext := by
        simpa [hStart] using hStepQ
      match hStep x _ hStepFromPresented with
      | Exists.intro y hy =>
          match abstractFinitePath_lifts_exactEndpoint
              hStep
              hy.right
              hRest with
          | Exists.intro z hz =>
              exact Exists.intro z
                (And.intro
                  (FinitePath.step hy.left hz.left)
                  hz.right)

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
  match hPathQ with
  | Exists.intro q hq =>
      match abstractFinitePath_lifts_exactEndpoint
          hReflect.step_reflects
          rfl
          hq.left with
      | Exists.intro y hy =>
          exact Exists.intro y
            (And.intro
              hy.left
              (hReflect.target_reflects y (by
                simpa [hy.right] using hq.right)))

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
