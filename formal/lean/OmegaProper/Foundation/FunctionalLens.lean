import OmegaProper.Trajectory.ReachabilityReflection

/-!
OmegaProper.Foundation.FunctionalLens

A minimal proof-backed presentation contract for relational systems.

Forward simulation prevents declared concrete steps from being erased. The back
or zig-zag clause prevents presented steps from being fabricated. Together
with predicate respect, they preserve and reflect one-step modal facts and
finite-path reachability.

This is not a full modal mu-calculus or fixed-point invariance theorem.
-/

namespace OmegaProper
namespace Foundation
namespace FunctionalLens

open Trajectory.ReachabilityReflection
open Trajectory.ReachabilityViability
open Trajectory.TrajectorySemantics

universe u v

/-- A functional relational lens with forward and back step clauses. -/
structure Lens
    (exact : Dyn.{u})
    (presented : Dyn.{v}) where
  map : exact.State -> presented.State
  forward :
    forall {x y : exact.State},
      exact.Next x y ->
      presented.Next (map x) (map y)
  back :
    forall {x : exact.State} {q : presented.State},
      presented.Next (map x) q ->
      exists y : exact.State,
        exact.Next x y /\ map y = q

/-- Exact and presented predicates agree at every mapped exact state. -/
def PredicateRespects
    {Exact : Type u}
    {Presented : Type v}
    (map : Exact -> Presented)
    (exactPredicate : Exact -> Prop)
    (presentedPredicate : Presented -> Prop) : Prop :=
  forall x, exactPredicate x <-> presentedPredicate (map x)

/-- One-step possibility is preserved and reflected by a functional lens. -/
theorem diamond_iff
    {exact : Dyn.{u}}
    {presented : Dyn.{v}}
    (lens : Lens exact presented)
    {exactPredicate : exact.State -> Prop}
    {presentedPredicate : presented.State -> Prop}
    (hPredicate :
      PredicateRespects lens.map exactPredicate presentedPredicate)
    (x : exact.State) :
    (exists y : exact.State,
        exact.Next x y /\ exactPredicate y) <->
      (exists q : presented.State,
        presented.Next (lens.map x) q /\ presentedPredicate q) := by
  constructor
  · intro hx
    match hx with
    | Exists.intro y hy =>
        exact Exists.intro (lens.map y)
          (And.intro
            (lens.forward hy.left)
            ((hPredicate y).mp hy.right))
  · intro hq
    match hq with
    | Exists.intro q hq =>
        match lens.back hq.left with
        | Exists.intro y hy =>
            exact Exists.intro y
              (And.intro
                hy.left
                ((hPredicate y).mpr (by
                  simpa [hy.right] using hq.right)))

/-- One-step necessity is preserved and reflected by a functional lens. -/
theorem box_iff
    {exact : Dyn.{u}}
    {presented : Dyn.{v}}
    (lens : Lens exact presented)
    {exactPredicate : exact.State -> Prop}
    {presentedPredicate : presented.State -> Prop}
    (hPredicate :
      PredicateRespects lens.map exactPredicate presentedPredicate)
    (x : exact.State) :
    (forall y : exact.State,
        exact.Next x y -> exactPredicate y) <->
      (forall q : presented.State,
        presented.Next (lens.map x) q -> presentedPredicate q) := by
  constructor
  · intro hExact q hStep
    match lens.back hStep with
    | Exists.intro y hy =>
        exact (by
          simpa [hy.right] using
            ((hPredicate y).mp (hExact y hy.left)))
  · intro hPresented y hStep
    exact (hPredicate y).mpr
      (hPresented (lens.map y) (lens.forward hStep))

/-- Forward simulation maps every exact finite path to a presented path. -/
theorem finitePath_forward
    {exact : Dyn.{u}}
    {presented : Dyn.{v}}
    (lens : Lens exact presented)
    {x y : exact.State}
    (hPath : FinitePath exact x y) :
    FinitePath presented (lens.map x) (lens.map y) := by
  induction hPath with
  | refl =>
      exact FinitePath.refl
  | step hStep _hRest ih =>
      exact FinitePath.step (lens.forward hStep) ih

/-- Back simulation lifts every presented finite path from an image state. -/
theorem finitePath_back
    {exact : Dyn.{u}}
    {presented : Dyn.{v}}
    (lens : Lens exact presented)
    {x : exact.State}
    {q : presented.State}
    (hPath : FinitePath presented (lens.map x) q) :
    exists y : exact.State,
      FinitePath exact x y /\ lens.map y = q := by
  exact abstractFinitePath_lifts_exactEndpoint
    (DX := exact)
    (DQ := presented)
    (present := lens.map)
    (by
      intro x0 q0 hStep
      exact lens.back hStep)
    rfl
    hPath

/--
Finite-path reachability of a respected predicate is preserved and reflected.
-/
theorem reachable_predicate_iff
    {exact : Dyn.{u}}
    {presented : Dyn.{v}}
    (lens : Lens exact presented)
    {exactPredicate : exact.State -> Prop}
    {presentedPredicate : presented.State -> Prop}
    (hPredicate :
      PredicateRespects lens.map exactPredicate presentedPredicate)
    (x : exact.State) :
    (exists y : exact.State,
        FinitePath exact x y /\ exactPredicate y) <->
      (exists q : presented.State,
        FinitePath presented (lens.map x) q /\ presentedPredicate q) := by
  constructor
  · intro hx
    match hx with
    | Exists.intro y hy =>
        exact Exists.intro (lens.map y)
          (And.intro
            (finitePath_forward lens hy.left)
            ((hPredicate y).mp hy.right))
  · intro hq
    match hq with
    | Exists.intro q hq =>
        match finitePath_back lens hq.left with
        | Exists.intro y hy =>
            exact Exists.intro y
              (And.intro
                hy.left
                ((hPredicate y).mpr (by
                  simpa [hy.right] using hq.right)))

end FunctionalLens
end Foundation
end OmegaProper
