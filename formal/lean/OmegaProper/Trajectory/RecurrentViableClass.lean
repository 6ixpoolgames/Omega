import OmegaProper.Trajectory.CarriedDistinction

/-!
OmegaProper.Trajectory.RecurrentViableClass

Recurrent viable classes.

`SustainingViableClass` gives a modest persistence object: every member is safe
and has an internal successor. This file adds a stronger finite-graph shape:
internal paths and strong connectivity inside a closed safe class.

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentViableClass

open CarriedDistinction
open ConsequenceClasses
open ConsequenceRelation
open ReachabilityViability
open SustainingViableClass

universe u

/--
An internal path stays inside the declared class at every step.

The reflexive constructor makes internal reachability reflexive for members.
The step constructor requires both the source and immediate successor to be in
the class.
-/
inductive InternalPath
    (D : Dyn.{u})
    (C : D.State -> Prop) :
    D.State -> D.State -> Prop where
  | refl {x : D.State} :
      C x ->
      InternalPath D C x x
  | step {x y z : D.State} :
      C x ->
      C y ->
      D.Next x y ->
      InternalPath D C y z ->
      InternalPath D C x z

/-- A one-step internal path. -/
theorem internalPath_single_step
    {D : Dyn.{u}}
    {C : D.State -> Prop}
    {x y : D.State}
    (hx : C x)
    (hy : C y)
    (hStep : D.Next x y) :
    InternalPath D C x y := by
  exact InternalPath.step hx hy hStep (InternalPath.refl hy)

/-- Internal paths start in the class. -/
theorem internalPath_start_mem
    {D : Dyn.{u}}
    {C : D.State -> Prop}
    {x y : D.State}
    (hPath : InternalPath D C x y) :
    C x := by
  cases hPath with
  | refl hx =>
      exact hx
  | step hx _hy _hStep _hRest =>
      exact hx

/-- Internal paths end in the class. -/
theorem internalPath_end_mem
    {D : Dyn.{u}}
    {C : D.State -> Prop}
    {x y : D.State}
    (hPath : InternalPath D C x y) :
    C y := by
  induction hPath with
  | refl hx =>
      exact hx
  | step _hx _hy _hStep _hRest ih =>
      exact ih

/-- A class is internally strongly connected when members have internal paths. -/
def ClassStronglyConnected
    (D : Dyn.{u})
    (C : D.State -> Prop) : Prop :=
  forall x y, C x -> C y -> InternalPath D C x y

/--
A recurrent viable class is safe, closed under outgoing transitions,
internally strongly connected, and sustaining.
-/
def RecurrentViableClass
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    (C : D.State -> Prop) : Prop :=
  ClassSafe safe C /\
  ClassClosed D C /\
  ClassStronglyConnected D C /\
  ClassHasSuccessorIn D C

theorem recurrent_implies_closedSustaining
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (h : RecurrentViableClass D safe C) :
    ClosedSustainingViableClass D safe C := by
  exact And.intro h.left
    (And.intro h.right.left h.right.right.right)

theorem recurrent_implies_sustaining
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (h : RecurrentViableClass D safe C) :
    SustainingViableClass D safe C := by
  exact closedSustaining_implies_sustaining
    (recurrent_implies_closedSustaining h)

theorem recurrentClass_member_viable
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (h : RecurrentViableClass D safe C)
    {x : D.State}
    (hx : C x) :
    Viable D safe x := by
  exact closedSustainingClass_member_viable
    (recurrent_implies_closedSustaining h)
    hx

/-! ## Tiny finite witness -/

theorem cycleClass_stronglyConnected :
    ClassStronglyConnected cycleDyn cycleClass := by
  intro x y hx hy
  cases x <;> cases y
  case left.left =>
    exact InternalPath.refl hx
  case left.right =>
    exact internalPath_single_step hx hy trivial
  case right.left =>
    exact internalPath_single_step hx hy trivial
  case right.right =>
    exact InternalPath.refl hx

theorem cycleClass_recurrent :
    RecurrentViableClass cycleDyn cycleSafe cycleClass := by
  exact And.intro
    cycleClass_closedSustaining.left
    (And.intro
      cycleClass_closedSustaining.right.left
      (And.intro
        cycleClass_stronglyConnected
        cycleClass_closedSustaining.right.right))

theorem recurrent_cycle_left_viable :
    Viable cycleDyn cycleSafe CycleState.left := by
  exact recurrentClass_member_viable cycleClass_recurrent trivial

theorem recurrent_cycle_right_viable :
    Viable cycleDyn cycleSafe CycleState.right := by
  exact recurrentClass_member_viable cycleClass_recurrent trivial

theorem recurrent_cycle_carries_distinction :
    RecurrentViableClass cycleDyn cycleSafe cycleClass /\
    ClassCarriesSeparatedPair cycleConsequenceSystem cycleClass /\
    Not (ClassRespectsConsequences cycleConsequenceSystem cycleClass) := by
  exact And.intro
    cycleClass_recurrent
    (And.intro
      cycleClass_carries_separated_pair
      cycleClass_not_consequenceRespecting)

end RecurrentViableClass
end Trajectory
end OmegaProper
