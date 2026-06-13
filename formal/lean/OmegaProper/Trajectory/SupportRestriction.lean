import OmegaProper.Trajectory.DistinctionSupport

/-!
OmegaProper.Trajectory.SupportRestriction

Restriction checks for distinction supports.

Support is endpoint-sensitive: a class that drops either endpoint of a
supported separated pair no longer supports that pair. This file records that
guardrail and a tiny finite witness where a proper sub-support destroys support.

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace SupportRestriction

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open DistinctionSupport
open PathCarriedDistinction
open RecurrentViableClass
open SustainingViableClass

universe w k o

theorem support_requires_left
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsSeparatedPair S Next C x y) :
    C x := by
  exact hSupport.left

theorem support_requires_right
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsSeparatedPair S Next C x y) :
    C y := by
  exact hSupport.right.left

theorem not_supports_if_left_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing : Not (C x)) :
    Not (SupportsSeparatedPair S Next C x y) := by
  intro hSupport
  exact hMissing (support_requires_left hSupport)

theorem not_supports_if_right_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing : Not (C y)) :
    Not (SupportsSeparatedPair S Next C x y) := by
  intro hSupport
  exact hMissing (support_requires_right hSupport)

theorem mergeSupport_requires_left
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next C x y) :
    C x := by
  exact hSupport.left

theorem mergeSupport_requires_right
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next C x y) :
    C y := by
  exact hSupport.right.left

theorem not_mergeSupports_if_left_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing : Not (C x)) :
    Not (SupportsMergeSeparatedPair S Next C x y) := by
  intro hSupport
  exact hMissing (mergeSupport_requires_left hSupport)

theorem not_mergeSupports_if_right_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMissing : Not (C y)) :
    Not (SupportsMergeSeparatedPair S Next C x y) := by
  intro hSupport
  exact hMissing (mergeSupport_requires_right hSupport)

/-! ## Tiny finite witness -/

/-- The proper sub-support that keeps only the left cycle state. -/
def leftOnlyClass : CycleState -> Prop
  | CycleState.left => True
  | CycleState.right => False

theorem leftOnly_sub_cycleClass :
    SupportSub leftOnlyClass cycleClass := by
  intro x _hx
  trivial

theorem leftOnly_proper_sub_cycleClass :
    ProperSupportSub leftOnlyClass cycleClass := by
  exact And.intro
    leftOnly_sub_cycleClass
    (Exists.intro CycleState.right
      (And.intro
        trivial
        (by
          intro hRight
          exact hRight)))

theorem leftOnly_not_supports_left_right :
    Not (SupportsSeparatedPair
      cycleConsequenceSystem
      cycleNext
      leftOnlyClass
      CycleState.left
      CycleState.right) := by
  exact not_supports_if_right_missing
    (by
      intro hRight
      exact hRight)

theorem leftOnly_not_mergeSupports_left_right :
    Not (SupportsMergeSeparatedPair
      cycleConsequenceSystem
      cycleNext
      leftOnlyClass
      CycleState.left
      CycleState.right) := by
  exact not_mergeSupports_if_right_missing
    (by
      intro hRight
      exact hRight)

theorem restriction_can_destroy_support :
    SupportsSeparatedPair
      cycleConsequenceSystem
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right /\
    ProperSupportSub leftOnlyClass cycleClass /\
    Not (SupportsSeparatedPair
      cycleConsequenceSystem
      cycleNext
      leftOnlyClass
      CycleState.left
      CycleState.right) := by
  exact And.intro
    cycle_supports_left_right
    (And.intro
      leftOnly_proper_sub_cycleClass
      leftOnly_not_supports_left_right)

end SupportRestriction
end Trajectory
end OmegaProper
