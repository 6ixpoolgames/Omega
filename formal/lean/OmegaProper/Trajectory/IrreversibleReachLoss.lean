import OmegaProper.Trajectory.ReachabilityViability

/-!
OmegaProper.Trajectory.IrreversibleReachLoss

Exact reachability loss.

This file gives the first narrow irreversible-loss object: a transition can
move from a state that reaches a declared target to a state that does not.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace IrreversibleReachLoss

open PredicateFixpoint
open ReachabilityViability

universe u

/--
A step loses reachability to a target when it moves from a target-reaching
state to a state that cannot reach that target.
-/
def ReachLossStep
    (D : Dyn.{u})
    (target : D.State -> Prop)
    (x y : D.State) : Prop :=
  D.Next x y /\ Reach D target x /\ Not (Reach D target y)

/--
A state is dead outside the target when it is not already in the target and
has no outgoing transitions.
-/
def DeadOutsideTarget
    (D : Dyn.{u})
    (target : D.State -> Prop)
    (y : D.State) : Prop :=
  Not (target y) /\ forall z, Not (D.Next y z)

/--
A dead state outside the target cannot reach the target.

The proof uses the least fixed-point definition directly: the predicate
excluding `y` is prefixed when `y` is not a target and has no outgoing step.
-/
theorem deadOutsideTarget_not_reach
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {y : D.State}
    (hDead : DeadOutsideTarget D target y) :
    Not (Reach D target y) := by
  intro hReach
  let barrier : D.State -> Prop := fun z => Not (z = y)
  have hPref : Prefixed (reachOp D target) barrier := by
    intro x hx hxy
    subst hxy
    cases hx with
    | inl hTarget =>
        exact hDead.left hTarget
    | inr hStep =>
        match hStep with
        | Exists.intro z hz =>
            exact hDead.right z hz.left
  exact hReach barrier hPref rfl

/--
Stepping into a dead state outside the target loses reachability whenever the
source state could reach the target.
-/
theorem step_to_deadOutsideTarget_loses_reach
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x y : D.State}
    (hStep : D.Next x y)
    (hReach : Reach D target x)
    (hDead : DeadOutsideTarget D target y) :
    ReachLossStep D target x y := by
  exact And.intro hStep
    (And.intro hReach (deadOutsideTarget_not_reach hDead))

/-! ## Tiny finite witness -/

inductive LossState where
  | start
  | goal
  | dead
  deriving DecidableEq

def lossNext : LossState -> LossState -> Prop
  | LossState.start, LossState.goal => True
  | LossState.start, LossState.dead => True
  | _, _ => False

def lossDyn : Dyn where
  State := LossState
  Next := lossNext

def lossTarget : LossState -> Prop
  | LossState.goal => True
  | _ => False

theorem goal_reaches_goal :
    Reach lossDyn lossTarget LossState.goal := by
  exact target_sub_reach lossDyn lossTarget LossState.goal trivial

theorem start_reaches_goal :
    Reach lossDyn lossTarget LossState.start := by
  exact reach_step lossDyn lossTarget
    (by trivial)
    goal_reaches_goal

theorem dead_is_deadOutsideTarget :
    DeadOutsideTarget lossDyn lossTarget LossState.dead := by
  constructor
  case left =>
    intro h
    exact h
  case right =>
    intro z hStep
    cases z <;> exact hStep

theorem dead_not_reaches_goal :
    Not (Reach lossDyn lossTarget LossState.dead) := by
  exact deadOutsideTarget_not_reach dead_is_deadOutsideTarget

theorem start_to_dead_loses_reach :
    ReachLossStep lossDyn lossTarget LossState.start LossState.dead := by
  exact step_to_deadOutsideTarget_loses_reach
    (by trivial)
    start_reaches_goal
    dead_is_deadOutsideTarget

end IrreversibleReachLoss
end Trajectory
end OmegaProper
