import OmegaProper.Trajectory.PathCarriedDistinction

/-!
OmegaProper.Trajectory.DistinctionSupport

Support/extent language for path-carried consequence distinctions.

This file packages path-carried distinction as a support relation. A support is
not an object, identity, self, or boundary. It is a declared class/region over
which a consequence distinction is internally connected by the dynamics.

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace DistinctionSupport

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open PathCarriedDistinction
open ReachabilityViability
open RecurrentViableClass
open SustainingViableClass

universe w k o

/-- Membership spelling for support classes. -/
def SupportContains
    {X : Type w}
    (C : X -> Prop)
    (x : X) : Prop :=
  C x

/-- Support inclusion. -/
def SupportSub
    {X : Type w}
    (C D : X -> Prop) : Prop :=
  forall x, C x -> D x

/-- Proper support inclusion. -/
def ProperSupportSub
    {X : Type w}
    (C D : X -> Prop) : Prop :=
  SupportSub C D /\ exists x, D x /\ Not (C x)

/--
A support for a directional separated pair is exactly a class that
path-carries that pair.
-/
def SupportsSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  ClassPathCarriesSeparatedPair S Next C x y

/-- Support for a merge-blocking separated pair. -/
def SupportsMergeSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  ClassPathCarriesMergeSeparatedPair S Next C x y

theorem support_implies_pathCarried
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsSeparatedPair S Next C x y) :
    ClassPathCarriesSeparatedPair S Next C x y := by
  exact hSupport

theorem mergeSupport_implies_pathCarried
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next C x y) :
    ClassPathCarriesMergeSeparatedPair S Next C x y := by
  exact hSupport

theorem support_blocks_classRespect
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsSeparatedPair S Next C x y) :
    Not (ClassRespectsConsequences S C) := by
  exact pathCarriedSeparated_blocks_classRespect hSupport

theorem mergeSupport_blocks_classRespect
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next C x y) :
    Not (ClassRespectsConsequences S C) := by
  exact pathCarriedMergeSeparated_blocks_classRespect hSupport

theorem recurrentSupport_left_viable
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hRec : RecurrentViableClass (dynFromNext Next) safe C)
    (hSupport : SupportsSeparatedPair S Next C x y) :
    Viable (dynFromNext Next) safe x := by
  exact recurrentClass_member_viable hRec hSupport.left

theorem recurrentSupport_right_viable
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hRec : RecurrentViableClass (dynFromNext Next) safe C)
    (hSupport : SupportsSeparatedPair S Next C x y) :
    Viable (dynFromNext Next) safe y := by
  exact recurrentClass_member_viable hRec hSupport.right.left

/-! ## Tiny finite witness -/

theorem cycleClass_recurrent_fromNext :
    RecurrentViableClass (dynFromNext cycleNext) cycleSafe cycleClass := by
  exact cycleClass_recurrent

theorem cycle_supports_left_right :
    SupportsSeparatedPair
      cycleConsequenceSystem
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right := by
  exact cycleClass_pathCarries_left_right

theorem cycle_support_blocks_mergeClass :
    Not (ClassRespectsConsequences cycleConsequenceSystem cycleClass) := by
  exact support_blocks_classRespect cycle_supports_left_right

theorem cycle_support_left_viable :
    Viable (dynFromNext cycleNext) cycleSafe CycleState.left := by
  exact recurrentSupport_left_viable
    cycleClass_recurrent_fromNext
    cycle_supports_left_right

theorem cycle_support_right_viable :
    Viable (dynFromNext cycleNext) cycleSafe CycleState.right := by
  exact recurrentSupport_right_viable
    cycleClass_recurrent_fromNext
    cycle_supports_left_right

theorem recurrent_cycle_is_support_for_distinction :
    RecurrentViableClass (dynFromNext cycleNext) cycleSafe cycleClass /\
    SupportsSeparatedPair
      cycleConsequenceSystem
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right /\
    Not (ClassRespectsConsequences cycleConsequenceSystem cycleClass) := by
  exact And.intro
    cycleClass_recurrent_fromNext
    (And.intro
      cycle_supports_left_right
      cycle_support_blocks_mergeClass)

end DistinctionSupport
end Trajectory
end OmegaProper
