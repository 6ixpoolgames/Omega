import OmegaProper.Trajectory.ConsequenceClasses
import OmegaProper.Trajectory.SustainingViableClass

/-!
OmegaProper.Trajectory.CarriedDistinction

Consequence distinctions carried inside sustaining classes.

A sustaining class can contain consequence-separated members. Such a class
carries structure; it is not a quotient class that may merge those members.

This does not define agency, identity, consciousness, value, alignment, or
Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace CarriedDistinction

open ConsequenceClasses
open ConsequenceRelation
open ReachabilityViability
open SustainingViableClass

universe w k o

/-- A class contains a pair when it contains both members. -/
def ClassContainsPair
    {X : Type w}
    (C : X -> Prop)
    (x y : X) : Prop :=
  C x /\ C y

/--
A class carries a directional consequence distinction when it contains a pair
separated by the consequence system.
-/
def ClassCarriesSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (C : S.Fragment -> Prop) : Prop :=
  exists x y,
    C x /\
    C y /\
    ConsequenceSeparated S x y

/--
A class carries a merge-blocking distinction when it contains a pair that is
merge-separated in either direction.
-/
def ClassCarriesMergeSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    (C : S.Fragment -> Prop) : Prop :=
  exists x y,
    C x /\
    C y /\
    ConsequenceMergeSeparated S x y

theorem separatedPair_carried_blocks_classRespect
    {S : ConsequenceSystem.{w, k, o}}
    {C : S.Fragment -> Prop}
    (hCarry : ClassCarriesSeparatedPair S C) :
    Not (ClassRespectsConsequences S C) := by
  exact separated_pair_blocks_class_respect hCarry

theorem mergeSeparatedPair_carried_blocks_classRespect_or_reverse
    {S : ConsequenceSystem.{w, k, o}}
    {C : S.Fragment -> Prop}
    (hCarry : ClassCarriesMergeSeparatedPair S C) :
    Not (ClassRespectsConsequences S C) := by
  intro hClass
  match hCarry with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          cases hy.right.right with
          | inl hSep =>
              exact separated_not_compatible hSep
                (hClass x y hy.left hy.right.left)
          | inr hSep =>
              exact separated_not_compatible hSep
                (hClass y x hy.right.left hy.left)

/-! ## Tiny finite witness -/

inductive CarryContext where
  | ctx
  deriving DecidableEq

def cycleConsequenceSystem : ConsequenceSystem where
  Fragment := CycleState
  Context := CarryContext
  Outcome := CycleState
  consequence := fun _ x => x
  Compare := fun _ x y => x = y
  Evaluated := fun _ => True

theorem cycle_left_separated_right :
    ConsequenceSeparated cycleConsequenceSystem CycleState.left CycleState.right := by
  exists CarryContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem cycleClass_carries_separated_pair :
    ClassCarriesSeparatedPair cycleConsequenceSystem cycleClass := by
  exact Exists.intro CycleState.left
    (Exists.intro CycleState.right
      (And.intro
        trivial
        (And.intro trivial cycle_left_separated_right)))

theorem cycleClass_carries_mergeSeparated_pair :
    ClassCarriesMergeSeparatedPair cycleConsequenceSystem cycleClass := by
  exact Exists.intro CycleState.left
    (Exists.intro CycleState.right
      (And.intro
        trivial
        (And.intro
          trivial
          (separated_implies_mergeSeparated cycle_left_separated_right))))

theorem cycleClass_not_consequenceRespecting :
    Not (ClassRespectsConsequences cycleConsequenceSystem cycleClass) := by
  exact separatedPair_carried_blocks_classRespect
    cycleClass_carries_separated_pair

theorem cycleClass_sustains_and_carries_distinction :
    ClosedSustainingViableClass cycleDyn cycleSafe cycleClass /\
    ClassCarriesSeparatedPair cycleConsequenceSystem cycleClass /\
    Not (ClassRespectsConsequences cycleConsequenceSystem cycleClass) := by
  exact And.intro
    cycleClass_closedSustaining
    (And.intro
      cycleClass_carries_separated_pair
      cycleClass_not_consequenceRespecting)

end CarriedDistinction
end Trajectory
end OmegaProper
