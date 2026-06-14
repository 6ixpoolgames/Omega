import OmegaProper.Trajectory.ReachabilityViability

/-!
OmegaProper.Trajectory.TrajectorySemantics

Operational trajectory semantics for the reachability/viability fixed-point
layer.

The fixed-point layer defines `Reach` and `Viable` order-theoretically. This
file connects those predicates to finite path language:

* `Reach` is equivalent to existence of a finite path to the target.
* `Viable` supplies arbitrarily long finite safe prefixes.

The viability result is intentionally one-way. An infinite trajectory theorem
or a converse from arbitrarily long prefixes requires additional compactness or
choice/branching assumptions and is not claimed here.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace TrajectorySemantics

open PredicateFixpoint
open ReachabilityViability

universe u

/--
A finite path in a nondeterministic transition system.

The path length is implicit in the derivation: `refl` is the empty path, and
`step` prepends one transition.
-/
inductive FinitePath
    (D : Dyn.{u}) :
    D.State -> D.State -> Prop where
  | refl {x : D.State} :
      FinitePath D x x
  | step {x y z : D.State} :
      D.Next x y ->
      FinitePath D y z ->
      FinitePath D x z

/-- A state has a finite path to the target when some finite path ends in it. -/
def FinitePathToTarget
    (D : Dyn.{u})
    (target : D.State -> Prop)
    (x : D.State) : Prop :=
  exists y, FinitePath D x y /\ target y

theorem finitePathToTarget_of_target
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x : D.State}
    (hTarget : target x) :
    FinitePathToTarget D target x := by
  exact Exists.intro x
    (And.intro FinitePath.refl hTarget)

theorem finitePathToTarget_step
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x y : D.State}
    (hStep : D.Next x y)
    (hPath : FinitePathToTarget D target y) :
    FinitePathToTarget D target x := by
  match hPath with
  | Exists.intro z hz =>
      exact Exists.intro z
        (And.intro (FinitePath.step hStep hz.left) hz.right)

theorem finitePathToTarget_prefixed
    (D : Dyn.{u})
    (target : D.State -> Prop) :
    Prefixed (reachOp D target) (FinitePathToTarget D target) := by
  intro x hx
  cases hx with
  | inl hTarget =>
      exact finitePathToTarget_of_target hTarget
  | inr hStep =>
      match hStep with
      | Exists.intro y hy =>
          exact finitePathToTarget_step hy.left hy.right

theorem finitePath_endpoint_reaches
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x y : D.State}
    (hPath : FinitePath D x y)
    (hTarget : target y) :
    Reach D target x := by
  induction hPath with
  | refl =>
      exact target_sub_reach D target _ hTarget
  | step hStep _hRest ih =>
      exact reach_step D target hStep (ih hTarget)

theorem finitePathToTarget_implies_reach
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x : D.State}
    (hPath : FinitePathToTarget D target x) :
    Reach D target x := by
  match hPath with
  | Exists.intro y hy =>
      exact finitePath_endpoint_reaches hy.left hy.right

theorem reach_implies_finitePathToTarget
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x : D.State}
    (hReach : Reach D target x) :
    FinitePathToTarget D target x := by
  exact hReach
    (FinitePathToTarget D target)
    (finitePathToTarget_prefixed D target)

theorem reach_iff_finitePathToTarget
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x : D.State} :
    Reach D target x <-> FinitePathToTarget D target x := by
  exact Iff.intro
    reach_implies_finitePathToTarget
    finitePathToTarget_implies_reach

/--
A finite safe prefix of length `n`.

The index counts transitions, not states. A zero-length prefix only requires
the current state to be safe.
-/
inductive SafePrefix
    (D : Dyn.{u})
    (safe : D.State -> Prop) :
    Nat -> D.State -> Prop where
  | zero {x : D.State} :
      safe x ->
      SafePrefix D safe 0 x
  | step {n : Nat} {x y : D.State} :
      safe x ->
      D.Next x y ->
      SafePrefix D safe n y ->
      SafePrefix D safe (Nat.succ n) x

/-- A state has safe prefixes of every finite transition length. -/
def ArbitrarilyLongSafePrefixes
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    (x : D.State) : Prop :=
  forall n : Nat, SafePrefix D safe n x

theorem safePrefix_start_safe
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {n : Nat}
    {x : D.State}
    (hPrefix : SafePrefix D safe n x) :
    safe x := by
  cases hPrefix with
  | zero hSafe =>
      exact hSafe
  | step hSafe _hStep _hRest =>
      exact hSafe

theorem viable_has_safePrefix
    (D : Dyn.{u})
    (safe : D.State -> Prop) :
    forall n x, Viable D safe x -> SafePrefix D safe n x := by
  intro n
  induction n with
  | zero =>
      intro x hViable
      exact SafePrefix.zero ((viable_sub_safe D safe) x hViable)
  | succ n ih =>
      intro x hViable
      match viable_has_successor D safe hViable with
      | Exists.intro y hy =>
          exact SafePrefix.step
            ((viable_sub_safe D safe) x hViable)
            hy.left
            (ih y hy.right)

theorem viable_implies_arbitrarilyLongSafePrefixes
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {x : D.State}
    (hViable : Viable D safe x) :
    ArbitrarilyLongSafePrefixes D safe x := by
  intro n
  exact viable_has_safePrefix D safe n x hViable

end TrajectorySemantics
end Trajectory
end OmegaProper
