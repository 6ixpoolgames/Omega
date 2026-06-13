import OmegaProper.Trajectory.ReachabilityViability

/-!
OmegaProper.Trajectory.SustainingViableClass

Sustaining viable classes.

This file gives a modest, identity-free persistence object: a declared class of
states is sustaining when every member is safe and every member has an internal
successor in the class. Membership in such a class witnesses viability.

This does not define recurrence in the strong graph-theoretic sense, agency,
identity, value, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace SustainingViableClass

open PredicateFixpoint
open ReachabilityViability

universe u

/-- A class is safe when every member satisfies the safety predicate. -/
def ClassSafe
    {X : Type u}
    (safe : X -> Prop)
    (C : X -> Prop) : Prop :=
  forall x, C x -> safe x

/-- A class is closed when every outgoing step from a member stays in the class. -/
def ClassClosed
    (D : Dyn.{u})
    (C : D.State -> Prop) : Prop :=
  forall x y, C x -> D.Next x y -> C y

/-- A class is sustaining when every member has an internal successor. -/
def ClassHasSuccessorIn
    (D : Dyn.{u})
    (C : D.State -> Prop) : Prop :=
  forall x, C x -> exists y, C y /\ D.Next x y

/--
A sustaining viable class is safe and has an internal successor for every
member.
-/
def SustainingViableClass
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    (C : D.State -> Prop) : Prop :=
  ClassSafe safe C /\ ClassHasSuccessorIn D C

/--
A closed sustaining viable class includes both closure and internal successor
data. The closure field is useful for later stronger recurrence-like claims,
but is not needed to witness viability.
-/
def ClosedSustainingViableClass
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    (C : D.State -> Prop) : Prop :=
  ClassSafe safe C /\ ClassClosed D C /\ ClassHasSuccessorIn D C

theorem closedSustaining_implies_sustaining
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (h : ClosedSustainingViableClass D safe C) :
    SustainingViableClass D safe C := by
  exact And.intro h.left h.right.right

/--
Membership in a sustaining viable class witnesses viability.

The class predicate itself is a postfixed point for the viability operator.
-/
theorem sustainingClass_member_viable
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (hClass : SustainingViableClass D safe C)
    {x : D.State}
    (hx : C x) :
    Viable D safe x := by
  have hPost : Postfixed (viabilityOp D safe) C := by
    intro y hy
    exact And.intro
      (hClass.left y hy)
      (match hClass.right y hy with
        | Exists.intro z hz =>
            Exists.intro z (And.intro hz.right hz.left))
  exact Exists.intro C (And.intro hPost hx)

theorem closedSustainingClass_member_viable
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (hClass : ClosedSustainingViableClass D safe C)
    {x : D.State}
    (hx : C x) :
    Viable D safe x := by
  exact sustainingClass_member_viable
    (closedSustaining_implies_sustaining hClass)
    hx

/-! ## Tiny finite witnesses -/

inductive SustainState where
  | loop
  | other
  deriving DecidableEq

def sustainNext : SustainState -> SustainState -> Prop
  | SustainState.loop, SustainState.loop => True
  | SustainState.other, SustainState.other => True
  | _, _ => False

def sustainDyn : Dyn where
  State := SustainState
  Next := sustainNext

def sustainSafe : SustainState -> Prop
  | SustainState.loop => True
  | SustainState.other => True

def loopClass : SustainState -> Prop
  | SustainState.loop => True
  | SustainState.other => False

theorem loopClass_closedSustaining :
    ClosedSustainingViableClass sustainDyn sustainSafe loopClass := by
  constructor
  case left =>
    intro x hx
    cases x
    case loop =>
      trivial
    case other =>
      exact False.elim hx
  case right =>
    constructor
    case left =>
      intro x y hx hStep
      cases x
      case loop =>
        cases y
        case loop =>
          trivial
        case other =>
          exact hStep
      case other =>
        exact False.elim hx
    case right =>
      intro x hx
      cases x
      case loop =>
        exact Exists.intro SustainState.loop (And.intro trivial trivial)
      case other =>
        exact False.elim hx

theorem loopClass_member_viable :
    Viable sustainDyn sustainSafe SustainState.loop := by
  exact closedSustainingClass_member_viable
    loopClass_closedSustaining
    trivial

/-- Two-state cyclic class witness. -/
inductive CycleState where
  | left
  | right
  deriving DecidableEq

def cycleNext : CycleState -> CycleState -> Prop
  | CycleState.left, CycleState.right => True
  | CycleState.right, CycleState.left => True
  | _, _ => False

def cycleDyn : Dyn where
  State := CycleState
  Next := cycleNext

def cycleSafe (_x : CycleState) : Prop :=
  True

def cycleClass (_x : CycleState) : Prop :=
  True

theorem cycleClass_closedSustaining :
    ClosedSustainingViableClass cycleDyn cycleSafe cycleClass := by
  constructor
  case left =>
    intro x _hx
    trivial
  case right =>
    constructor
    case left =>
      intro x y _hx _hStep
      trivial
    case right =>
      intro x _hx
      cases x
      case left =>
        exact Exists.intro CycleState.right (And.intro trivial trivial)
      case right =>
        exact Exists.intro CycleState.left (And.intro trivial trivial)

theorem cycle_left_viable :
    Viable cycleDyn cycleSafe CycleState.left := by
  exact closedSustainingClass_member_viable
    cycleClass_closedSustaining
    trivial

theorem cycle_right_viable :
    Viable cycleDyn cycleSafe CycleState.right := by
  exact closedSustainingClass_member_viable
    cycleClass_closedSustaining
    trivial

end SustainingViableClass
end Trajectory
end OmegaProper
