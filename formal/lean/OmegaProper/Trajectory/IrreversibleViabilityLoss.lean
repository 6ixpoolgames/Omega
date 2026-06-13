import OmegaProper.Trajectory.ReachabilityViability

/-!
OmegaProper.Trajectory.IrreversibleViabilityLoss

Exact viability loss.

This file gives the viability-side loss object: a transition can move from a
viable state to a state that is not viable.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace IrreversibleViabilityLoss

open PredicateFixpoint
open ReachabilityViability

universe u

/--
A step loses viability when it moves from a viable state to a state that is not
viable.
-/
def ViabilityLossStep
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    (x y : D.State) : Prop :=
  D.Next x y /\ Viable D safe x /\ Not (Viable D safe y)

/-- A state has no outgoing transition. -/
def NoOutgoing (D : Dyn.{u}) (y : D.State) : Prop :=
  forall z, Not (D.Next y z)

/-- A state with no outgoing transition is not viable. -/
theorem noOutgoing_not_viable
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {y : D.State}
    (hNoOutgoing : NoOutgoing D y) :
    Not (Viable D safe y) := by
  intro hViable
  match viable_has_successor D safe hViable with
  | Exists.intro z hz =>
      exact hNoOutgoing z hz.left

/--
Stepping into a state with no outgoing transition loses viability whenever the
source state was viable.
-/
theorem step_to_noOutgoing_loses_viability
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {x y : D.State}
    (hStep : D.Next x y)
    (hViable : Viable D safe x)
    (hNoOutgoing : NoOutgoing D y) :
    ViabilityLossStep D safe x y := by
  exact And.intro hStep
    (And.intro hViable (noOutgoing_not_viable hNoOutgoing))

/-! ## Tiny finite witness -/

inductive ViabilityLossState where
  | loop
  | dead
  deriving DecidableEq

def viabilityLossNext : ViabilityLossState -> ViabilityLossState -> Prop
  | ViabilityLossState.loop, ViabilityLossState.loop => True
  | ViabilityLossState.loop, ViabilityLossState.dead => True
  | _, _ => False

def viabilityLossDyn : Dyn where
  State := ViabilityLossState
  Next := viabilityLossNext

def viabilityLossSafe : ViabilityLossState -> Prop
  | ViabilityLossState.loop => True
  | ViabilityLossState.dead => True

theorem loop_viable :
    Viable viabilityLossDyn viabilityLossSafe ViabilityLossState.loop := by
  let p : ViabilityLossState -> Prop :=
    fun x =>
      match x with
      | ViabilityLossState.loop => True
      | ViabilityLossState.dead => False
  have hPost : Postfixed (viabilityOp viabilityLossDyn viabilityLossSafe) p := by
    intro x hx
    cases x
    case loop =>
      exact And.intro trivial
        (Exists.intro ViabilityLossState.loop (And.intro trivial trivial))
    case dead =>
      exact False.elim hx
  exact Exists.intro p (And.intro hPost trivial)

theorem dead_noOutgoing :
    NoOutgoing viabilityLossDyn ViabilityLossState.dead := by
  intro z hStep
  cases z <;> exact hStep

theorem dead_not_viable :
    Not (Viable viabilityLossDyn viabilityLossSafe ViabilityLossState.dead) := by
  exact noOutgoing_not_viable dead_noOutgoing

theorem loop_to_dead_loses_viability :
    ViabilityLossStep
      viabilityLossDyn
      viabilityLossSafe
      ViabilityLossState.loop
      ViabilityLossState.dead := by
  exact step_to_noOutgoing_loses_viability
    (by trivial)
    loop_viable
    dead_noOutgoing

end IrreversibleViabilityLoss
end Trajectory
end OmegaProper
