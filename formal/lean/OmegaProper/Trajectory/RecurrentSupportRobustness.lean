import OmegaProper.Trajectory.SupportUnderPerturbation

/-!
OmegaProper.Trajectory.RecurrentSupportRobustness

Robustness guardrails for recurrent supports carrying consequence distinctions.

This file strengthens support perturbation from endpoint support alone to
recurrent path-carrying support. A recurrent support carries a fixed
merge-separated pair only when it is recurrent/viable and the support still
contains the endpoints, connects them internally in both directions, and keeps
the merge separation visible.

This does not define agency, identity, deformers, boundaries, value,
alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportRobustness

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentViableClass
open SupportRestriction
open SupportUnderPerturbation
open SustainingViableClass

universe w k o

/--
A recurrent support carries a fixed merge-separated pair when the class is
recurrent viable under `Next` and path-carries the merge-separated pair.

This is still pair-relative and support-relative. It is not a persistence or
identity predicate for an object.
-/
def RecurrentSupportCarries
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (safe : S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  RecurrentViableClass (dynFromNext Next) safe C /\
    SupportsMergeSeparatedPair S Next C x y

/--
A recurrent support change preserves a fixed carried pair when recurrent
carrying transfers from the original dynamics/support to the changed
dynamics/support.
-/
def RecurrentSupportIntegrityUnder
    (S : ConsequenceSystem.{w, k, o})
    (Next0 Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe0 safe1 : S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  RecurrentSupportCarries S Next0 safe0 C x y ->
    RecurrentSupportCarries S Next1 safe1 D x y

/--
A recurrent support change destroys recurrent carrying for a fixed pair when
the original recurrent support carries the pair and the changed one does not.
-/
def RecurrentSupportDestroyedUnder
    (S : ConsequenceSystem.{w, k, o})
    (Next0 Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe0 safe1 : S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  RecurrentSupportCarries S Next0 safe0 C x y /\
    Not (RecurrentSupportCarries S Next1 safe1 D x y)

theorem recurrentSupportCarries_recurrent
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : RecurrentSupportCarries S Next safe C x y) :
    RecurrentViableClass (dynFromNext Next) safe C := by
  exact h.left

theorem recurrentSupportCarries_support
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : RecurrentSupportCarries S Next safe C x y) :
    SupportsMergeSeparatedPair S Next C x y := by
  exact h.right

theorem recurrentSupportCarries_left_viable
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : RecurrentSupportCarries S Next safe C x y) :
    Viable (dynFromNext Next) safe x := by
  exact recurrentClass_member_viable h.left h.right.left

theorem recurrentSupportCarries_right_viable
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : RecurrentSupportCarries S Next safe C x y) :
    Viable (dynFromNext Next) safe y := by
  exact recurrentClass_member_viable h.left h.right.right.left

theorem not_recurrentSupportCarries_if_left_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing : Not (C x)) :
    Not (RecurrentSupportCarries S Next safe C x y) := by
  intro hCarry
  exact hMissing hCarry.right.left

theorem not_recurrentSupportCarries_if_right_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing : Not (C y)) :
    Not (RecurrentSupportCarries S Next safe C x y) := by
  intro hCarry
  exact hMissing hCarry.right.right.left

theorem not_recurrentSupportCarries_if_forward_path_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing :
      Not (InternalPath (dynFromNext Next) C x y)) :
    Not (RecurrentSupportCarries S Next safe C x y) := by
  intro hCarry
  exact hMissing hCarry.right.right.right.left

theorem not_recurrentSupportCarries_if_reverse_path_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing :
      Not (InternalPath (dynFromNext Next) C y x)) :
    Not (RecurrentSupportCarries S Next safe C x y) := by
  intro hCarry
  exact hMissing hCarry.right.right.right.right.left

theorem sameRecurrentSupport_preserves_integrity
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment} :
    RecurrentSupportIntegrityUnder S Next Next safe safe C C x y := by
  intro hCarry
  exact hCarry

theorem recurrentSupportDestroyed_not_integrity
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hDestroyed :
      RecurrentSupportDestroyedUnder S Next0 Next1 safe0 safe1 C D x y) :
    Not (RecurrentSupportIntegrityUnder S Next0 Next1 safe0 safe1 C D x y) := by
  intro hIntegrity
  exact hDestroyed.right (hIntegrity hDestroyed.left)

theorem recurrentSupportDestroyed_if_left_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hMissing : Not (D x)) :
    RecurrentSupportDestroyedUnder S Next0 Next1 safe0 safe1 C D x y := by
  exact And.intro
    hCarry
    (not_recurrentSupportCarries_if_left_missing hMissing)

theorem recurrentSupportDestroyed_if_right_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hMissing : Not (D y)) :
    RecurrentSupportDestroyedUnder S Next0 Next1 safe0 safe1 C D x y := by
  exact And.intro
    hCarry
    (not_recurrentSupportCarries_if_right_missing hMissing)

theorem recurrentSupportDestroyed_if_forward_path_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hMissing :
      Not (InternalPath (dynFromNext Next1) D x y)) :
    RecurrentSupportDestroyedUnder S Next0 Next1 safe0 safe1 C D x y := by
  exact And.intro
    hCarry
    (not_recurrentSupportCarries_if_forward_path_missing hMissing)

theorem recurrentSupportDestroyed_if_reverse_path_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hMissing :
      Not (InternalPath (dynFromNext Next1) D y x)) :
    RecurrentSupportDestroyedUnder S Next0 Next1 safe0 safe1 C D x y := by
  exact And.intro
    hCarry
    (not_recurrentSupportCarries_if_reverse_path_missing hMissing)

/-! ## Tiny finite recurrent-support witness -/

theorem cycle_recurrentSupportCarries_left_right :
    RecurrentSupportCarries
      cycleConsequenceSystem
      cycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    cycleClass_recurrent_fromNext
    cycleClass_pathCarries_merge_left_right

theorem cycle_sameSupport_preserves_recurrent_integrity :
    RecurrentSupportIntegrityUnder
      cycleConsequenceSystem
      cycleNext
      cycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right := by
  exact sameRecurrentSupport_preserves_integrity

theorem cycle_leftOnly_destroys_recurrent_support :
    RecurrentSupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      cycleNext
      cycleSafe
      cycleSafe
      cycleClass
      leftOnlyClass
      CycleState.left
      CycleState.right := by
  exact recurrentSupportDestroyed_if_right_missing
    cycle_recurrentSupportCarries_left_right
    (by
      intro hRight
      exact hRight)

end RecurrentSupportRobustness
end Trajectory
end OmegaProper
