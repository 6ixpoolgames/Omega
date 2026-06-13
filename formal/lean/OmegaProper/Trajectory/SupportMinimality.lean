import OmegaProper.Trajectory.SupportRestriction

/-!
OmegaProper.Trajectory.SupportMinimality

Minimal support for a fixed consequence-separated pair.

Minimality here is pair-relative: a support is minimal for endpoints `x` and
`y` when every sub-support that still supports that same pair must contain all
members of the original support. This is not an object identity claim and not a
global boundary claim.

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace SupportMinimality

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open DistinctionSupport
open PathCarriedDistinction
open RecurrentViableClass
open SupportRestriction
open SustainingViableClass

universe w k o

/--
A minimal support for a directional separated pair: any sub-support that still
supports the same pair must contain the original support.
-/
def MinimalSupportForSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  SupportsSeparatedPair S Next C x y /\
  forall C' : S.Fragment -> Prop,
    SupportSub C' C ->
    SupportsSeparatedPair S Next C' x y ->
    SupportSub C C'

/--
A minimal support for a merge-separated pair: the merge-blocking analogue of
`MinimalSupportForSeparatedPair`.
-/
def MinimalSupportForMergeSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  SupportsMergeSeparatedPair S Next C x y /\
  forall C' : S.Fragment -> Prop,
    SupportSub C' C ->
    SupportsMergeSeparatedPair S Next C' x y ->
    SupportSub C C'

theorem minimalSupport_supports
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMin : MinimalSupportForSeparatedPair S Next C x y) :
    SupportsSeparatedPair S Next C x y := by
  exact hMin.left

theorem minimalMergeSupport_supports
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMin : MinimalSupportForMergeSeparatedPair S Next C x y) :
    SupportsMergeSeparatedPair S Next C x y := by
  exact hMin.left

theorem minimalSupport_no_proper_support_sub
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMin : MinimalSupportForSeparatedPair S Next C x y) :
    Not (exists C' : S.Fragment -> Prop,
      ProperSupportSub C' C /\
      SupportsSeparatedPair S Next C' x y) := by
  intro hExists
  match hExists with
  | Exists.intro C' hCandidate =>
      have hBack : SupportSub C C' :=
        hMin.right C' hCandidate.left.left hCandidate.right
      match hCandidate.left.right with
      | Exists.intro z hz =>
          exact hz.right (hBack z hz.left)

theorem minimalMergeSupport_no_proper_support_sub
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hMin : MinimalSupportForMergeSeparatedPair S Next C x y) :
    Not (exists C' : S.Fragment -> Prop,
      ProperSupportSub C' C /\
      SupportsMergeSeparatedPair S Next C' x y) := by
  intro hExists
  match hExists with
  | Exists.intro C' hCandidate =>
      have hBack : SupportSub C C' :=
        hMin.right C' hCandidate.left.left hCandidate.right
      match hCandidate.left.right with
      | Exists.intro z hz =>
          exact hz.right (hBack z hz.left)

/-! ## Tiny finite witness -/

theorem cycleClass_minimal_support_left_right :
    MinimalSupportForSeparatedPair
      cycleConsequenceSystem
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    cycle_supports_left_right
    (by
      intro C' _hSub hSupport z _hzCycle
      cases z with
      | left =>
          exact hSupport.left
      | right =>
          exact hSupport.right.left)

theorem cycleClass_no_proper_support_sub_left_right :
    Not (exists C' : CycleState -> Prop,
      ProperSupportSub C' cycleClass /\
      SupportsSeparatedPair
        cycleConsequenceSystem
        cycleNext
        C'
        CycleState.left
        CycleState.right) := by
  exact minimalSupport_no_proper_support_sub
    cycleClass_minimal_support_left_right

end SupportMinimality
end Trajectory
end OmegaProper
