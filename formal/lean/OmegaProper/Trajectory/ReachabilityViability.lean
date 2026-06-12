import OmegaProper.Trajectory.PredicateFixpoint

/-!
OmegaProper.Trajectory.ReachabilityViability

Reachability and viability as predicate fixed points.

This file gives the first dynamics layer over `PredicateFixpoint`: reachability
is a least fixed point, and viability is a greatest fixed point. It does not
define value, agency, identity, irreversible loss, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace ReachabilityViability

open PredicateFixpoint

universe u

/-- A nondeterministic transition system. -/
structure Dyn where
  State : Type u
  Next : State -> State -> Prop

/--
Reachability operator: a state reaches the target if it is already in the
target or can step to a state in the candidate set.
-/
def reachOp (D : Dyn.{u}) (target : D.State -> Prop)
    (p : D.State -> Prop) : D.State -> Prop :=
  fun x => target x \/ exists y, D.Next x y /\ p y

/-- Least fixed-point reachability set. -/
def Reach (D : Dyn.{u}) (target : D.State -> Prop) : D.State -> Prop :=
  lfp (reachOp D target)

/--
Viability operator: a state is safe and can step to a state in the candidate
set.
-/
def viabilityOp (D : Dyn.{u}) (safe : D.State -> Prop)
    (p : D.State -> Prop) : D.State -> Prop :=
  fun x => safe x /\ exists y, D.Next x y /\ p y

/-- Greatest fixed-point viability kernel. -/
def Viable (D : Dyn.{u}) (safe : D.State -> Prop) : D.State -> Prop :=
  gfp (viabilityOp D safe)

theorem reachOp_mono
    (D : Dyn.{u})
    (target : D.State -> Prop) :
    Mono (reachOp D target) := by
  intro p q hpq x hx
  cases hx with
  | inl hTarget =>
      exact Or.inl hTarget
  | inr hStep =>
      match hStep with
      | Exists.intro y hy =>
          exact Or.inr
            (Exists.intro y
              (And.intro hy.left (hpq y hy.right)))

theorem viabilityOp_mono
    (D : Dyn.{u})
    (safe : D.State -> Prop) :
    Mono (viabilityOp D safe) := by
  intro p q hpq x hx
  exact And.intro hx.left
    (match hx.right with
      | Exists.intro y hy =>
          Exists.intro y
            (And.intro hy.left (hpq y hy.right)))

theorem reach_fixed
    (D : Dyn.{u})
    (target : D.State -> Prop) :
    PSub (reachOp D target (Reach D target)) (Reach D target) /\
      PSub (Reach D target) (reachOp D target (Reach D target)) := by
  exact lfp_fixed (reachOp_mono D target)

theorem viability_fixed
    (D : Dyn.{u})
    (safe : D.State -> Prop) :
    PSub (Viable D safe) (viabilityOp D safe (Viable D safe)) /\
      PSub (viabilityOp D safe (Viable D safe)) (Viable D safe) := by
  exact gfp_fixed (viabilityOp_mono D safe)

theorem target_sub_reach
    (D : Dyn.{u})
    (target : D.State -> Prop) :
    PSub target (Reach D target) := by
  intro x hxTarget
  exact (reach_fixed D target).left x (Or.inl hxTarget)

theorem reach_step
    (D : Dyn.{u})
    (target : D.State -> Prop)
    {x y : D.State}
    (hStep : D.Next x y)
    (hReach : Reach D target y) :
    Reach D target x := by
  exact (reach_fixed D target).left x
    (Or.inr (Exists.intro y (And.intro hStep hReach)))

theorem viable_sub_safe
    (D : Dyn.{u})
    (safe : D.State -> Prop) :
    PSub (Viable D safe) safe := by
  intro x hxViable
  exact ((viability_fixed D safe).left x hxViable).left

theorem viable_has_successor
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    {x : D.State}
    (hxViable : Viable D safe x) :
    exists y, D.Next x y /\ Viable D safe y := by
  exact ((viability_fixed D safe).left x hxViable).right

end ReachabilityViability
end Trajectory
end OmegaProper
