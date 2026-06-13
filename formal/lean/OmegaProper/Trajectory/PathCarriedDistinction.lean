import OmegaProper.Trajectory.RecurrentViableClass

/-!
OmegaProper.Trajectory.PathCarriedDistinction

Consequence distinctions carried through internal class paths.

`CarriedDistinction` says a class can contain consequence-separated members.
This file strengthens that shape: the separated members are connected by
internal paths in both directions inside the class.

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace PathCarriedDistinction

open CarriedDistinction
open ConsequenceClasses
open ConsequenceRelation
open ReachabilityViability
open RecurrentViableClass
open SustainingViableClass

universe w k o

/-- Build a dynamics object over an existing carrier from a transition relation. -/
def dynFromNext {X : Type w} (Next : X -> X -> Prop) : Dyn.{w} where
  State := X
  Next := Next

/--
A class path-carries a directional consequence distinction when it contains a
separated pair and internally connects the pair in both directions.
-/
def ClassPathCarriesSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  C x /\
  C y /\
  InternalPath (dynFromNext Next) C x y /\
  InternalPath (dynFromNext Next) C y x /\
  ConsequenceSeparated S x y

/--
A class path-carries a merge-blocking distinction when it contains a
merge-separated pair and internally connects the pair in both directions.
-/
def ClassPathCarriesMergeSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  C x /\
  C y /\
  InternalPath (dynFromNext Next) C x y /\
  InternalPath (dynFromNext Next) C y x /\
  ConsequenceMergeSeparated S x y

/-- Existential class-level version of path-carried directional separation. -/
def ClassPathCarriesSomeSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop) : Prop :=
  exists x y, ClassPathCarriesSeparatedPair S Next C x y

/-- Existential class-level version of path-carried merge separation. -/
def ClassPathCarriesSomeMergeSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C : S.Fragment -> Prop) : Prop :=
  exists x y, ClassPathCarriesMergeSeparatedPair S Next C x y

theorem pathCarriedSeparated_implies_carried
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : ClassPathCarriesSeparatedPair S Next C x y) :
    ClassCarriesSeparatedPair S C := by
  exact Exists.intro x
    (Exists.intro y
      (And.intro h.left
        (And.intro h.right.left h.right.right.right.right)))

theorem pathCarriedMergeSeparated_implies_carried
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : ClassPathCarriesMergeSeparatedPair S Next C x y) :
    ClassCarriesMergeSeparatedPair S C := by
  exact Exists.intro x
    (Exists.intro y
      (And.intro h.left
        (And.intro h.right.left h.right.right.right.right)))

theorem pathCarriedSeparated_blocks_classRespect
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : ClassPathCarriesSeparatedPair S Next C x y) :
    Not (ClassRespectsConsequences S C) := by
  exact separatedPair_carried_blocks_classRespect
    (pathCarriedSeparated_implies_carried h)

theorem pathCarriedMergeSeparated_blocks_classRespect
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (h : ClassPathCarriesMergeSeparatedPair S Next C x y) :
    Not (ClassRespectsConsequences S C) := by
  exact mergeSeparatedPair_carried_blocks_classRespect_or_reverse
    (pathCarriedMergeSeparated_implies_carried h)

/-! ## Tiny finite witness -/

theorem cycleClass_pathCarries_left_right :
    ClassPathCarriesSeparatedPair
      cycleConsequenceSystem
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        (internalPath_single_step trivial trivial trivial)
        (And.intro
          (internalPath_single_step trivial trivial trivial)
          cycle_left_separated_right)))

theorem cycleClass_pathCarries_merge_left_right :
    ClassPathCarriesMergeSeparatedPair
      cycleConsequenceSystem
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        (internalPath_single_step trivial trivial trivial)
        (And.intro
          (internalPath_single_step trivial trivial trivial)
          (separated_implies_mergeSeparated cycle_left_separated_right))))

theorem recurrent_cycle_pathCarries_distinction :
    RecurrentViableClass cycleDyn cycleSafe cycleClass /\
    ClassPathCarriesSeparatedPair
      cycleConsequenceSystem
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right /\
    Not (ClassRespectsConsequences cycleConsequenceSystem cycleClass) := by
  exact And.intro
    cycleClass_recurrent
    (And.intro
      cycleClass_pathCarries_left_right
      (pathCarriedSeparated_blocks_classRespect cycleClass_pathCarries_left_right))

end PathCarriedDistinction
end Trajectory
end OmegaProper
