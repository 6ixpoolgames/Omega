import OmegaProper.Trajectory.RecurrentSupportExtension

/-!
OmegaProper.Trajectory.RecurrentSupportLineage

Support-lineage transfer for recurrently carried consequence distinctions.

`RecurrentSupportExtension` handles the subset-shaped case: carrying transfers
from `C` into a larger support `D`. This file records a weaker handoff shape:
`C` and `D` need not be related by inclusion. The source support contributes
the declared merge-separated consequence distinction; the target support must
independently provide recurrent viability and internal paths for the same
declared endpoints.

This is not recoverability, identity, agency, deformer structure, value,
alignment, or Omega proper. It is a pair-relative support handoff contract.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportLineage

open ConsequenceRelation
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportExtension
open RecurrentSupportPathTransfer
open RecurrentSupportRobustness
open RecurrentViableClass
open SupportRestriction
open SustainingViableClass

universe w k o

/-- Two supports are incomparable when neither is included in the other. -/
def SupportsIncomparable
    {X : Type w}
    (C D : X -> Prop) : Prop :=
  Not (SupportSub C D) /\ Not (SupportSub D C)

/--
Pair-relative lineage contract.

The source support is not required to be included in the target support. The
target support must recurrently carry the same declared endpoints, using the
source carrying proof only for the consequence merge-separation itself.
-/
def RecurrentSupportLineageContract
    {X : Type w}
    (Next1 : X -> X -> Prop)
    (safe1 : X -> Prop)
    (D : X -> Prop)
    (x y : X) : Prop :=
  RecurrentViableClass (dynFromNext Next1) safe1 D /\
    D x /\
    D y /\
    InternalPath (dynFromNext Next1) D x y /\
    InternalPath (dynFromNext Next1) D y x

theorem supportsMergeSeparatedPair_lineage_of_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next0 C x y)
    (hContract : RecurrentSupportLineageContract Next1 safe1 D x y) :
    SupportsMergeSeparatedPair S Next1 D x y := by
  exact And.intro
    hContract.right.left
    (And.intro
      hContract.right.right.left
      (And.intro
        hContract.right.right.right.left
        (And.intro
          hContract.right.right.right.right
          hSupport.right.right.right.right)))

theorem recurrentSupportCarries_lineage_of_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hContract : RecurrentSupportLineageContract Next1 safe1 D x y) :
    RecurrentSupportCarries S Next1 safe1 D x y := by
  exact And.intro
    hContract.left
    (supportsMergeSeparatedPair_lineage_of_contract hCarry.right hContract)

/-! ## Finite incomparable-support handoff witness -/

inductive LineageState where
  | left
  | old
  | new
  | right
  deriving DecidableEq

def lineageSourceClass : LineageState -> Prop
  | LineageState.left => True
  | LineageState.old => True
  | LineageState.new => False
  | LineageState.right => True

def lineageTargetClass : LineageState -> Prop
  | LineageState.left => True
  | LineageState.old => False
  | LineageState.new => True
  | LineageState.right => True

def lineageSafe (_x : LineageState) : Prop :=
  True

def lineageSourceNext : LineageState -> LineageState -> Prop
  | LineageState.left, LineageState.old => True
  | LineageState.old, LineageState.right => True
  | LineageState.right, LineageState.left => True
  | _, _ => False

def lineageTargetNext : LineageState -> LineageState -> Prop
  | LineageState.left, LineageState.right => True
  | LineageState.right, LineageState.new => True
  | LineageState.new, LineageState.left => True
  | _, _ => False

inductive LineageContext where
  | ctx
  deriving DecidableEq

def lineageConsequenceSystem : ConsequenceSystem where
  Fragment := LineageState
  Context := LineageContext
  Outcome := LineageState
  consequence := fun _ x => x
  Compare := fun _ x y => x = y
  Evaluated := fun _ => True

theorem lineage_left_separated_right :
    ConsequenceSeparated
      lineageConsequenceSystem
      LineageState.left
      LineageState.right := by
  exists LineageContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem lineage_supports_incomparable :
    SupportsIncomparable lineageSourceClass lineageTargetClass := by
  constructor
  case left =>
    intro hSub
    exact hSub LineageState.old trivial
  case right =>
    intro hSub
    exact hSub LineageState.new trivial

theorem lineage_source_path_left_old :
    InternalPath
      (dynFromNext lineageSourceNext)
      lineageSourceClass
      LineageState.left
      LineageState.old := by
  exact internalPath_single_step trivial trivial trivial

theorem lineage_source_path_old_right :
    InternalPath
      (dynFromNext lineageSourceNext)
      lineageSourceClass
      LineageState.old
      LineageState.right := by
  exact internalPath_single_step trivial trivial trivial

theorem lineage_source_path_left_right :
    InternalPath
      (dynFromNext lineageSourceNext)
      lineageSourceClass
      LineageState.left
      LineageState.right := by
  exact internalPathAppend
    lineage_source_path_left_old
    lineage_source_path_old_right

theorem lineage_source_path_right_left :
    InternalPath
      (dynFromNext lineageSourceNext)
      lineageSourceClass
      LineageState.right
      LineageState.left := by
  exact internalPath_single_step trivial trivial trivial

theorem lineage_source_path_old_left :
    InternalPath
      (dynFromNext lineageSourceNext)
      lineageSourceClass
      LineageState.old
      LineageState.left := by
  exact internalPathAppend
    lineage_source_path_old_right
    lineage_source_path_right_left

theorem lineage_source_path_right_old :
    InternalPath
      (dynFromNext lineageSourceNext)
      lineageSourceClass
      LineageState.right
      LineageState.old := by
  exact internalPathAppend
    lineage_source_path_right_left
    lineage_source_path_left_old

theorem lineage_source_recurrent :
    RecurrentViableClass
      (dynFromNext lineageSourceNext)
      lineageSafe
      lineageSourceClass := by
  exact And.intro
    (by
      intro x _hx
      trivial)
    (And.intro
      (by
        intro x y hx hStep
        cases x <;> cases y <;> trivial)
      (And.intro
        (by
          intro x y hx hy
          cases x <;> cases y
          case left.left =>
            exact InternalPath.refl hx
          case left.old =>
            exact lineage_source_path_left_old
          case left.new =>
            exact False.elim hy
          case left.right =>
            exact lineage_source_path_left_right
          case old.left =>
            exact lineage_source_path_old_left
          case old.old =>
            exact InternalPath.refl hx
          case old.new =>
            exact False.elim hy
          case old.right =>
            exact lineage_source_path_old_right
          case new.left =>
            exact False.elim hx
          case new.old =>
            exact False.elim hx
          case new.new =>
            exact False.elim hx
          case new.right =>
            exact False.elim hx
          case right.left =>
            exact lineage_source_path_right_left
          case right.old =>
            exact lineage_source_path_right_old
          case right.new =>
            exact False.elim hy
          case right.right =>
            exact InternalPath.refl hx)
        (by
          intro x hx
          cases x
          case left =>
            exact Exists.intro LineageState.old (And.intro trivial trivial)
          case old =>
            exact Exists.intro LineageState.right (And.intro trivial trivial)
          case new =>
            exact False.elim hx
          case right =>
            exact Exists.intro LineageState.left (And.intro trivial trivial))))

theorem lineage_source_supports_left_right :
    SupportsMergeSeparatedPair
      lineageConsequenceSystem
      lineageSourceNext
      lineageSourceClass
      LineageState.left
      LineageState.right := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        lineage_source_path_left_right
        (And.intro
          lineage_source_path_right_left
          (separated_implies_mergeSeparated
            lineage_left_separated_right))))

theorem lineage_source_carries_left_right :
    RecurrentSupportCarries
      lineageConsequenceSystem
      lineageSourceNext
      lineageSafe
      lineageSourceClass
      LineageState.left
      LineageState.right := by
  exact And.intro
    lineage_source_recurrent
    lineage_source_supports_left_right

theorem lineage_target_path_left_right :
    InternalPath
      (dynFromNext lineageTargetNext)
      lineageTargetClass
      LineageState.left
      LineageState.right := by
  exact internalPath_single_step trivial trivial trivial

theorem lineage_target_path_right_new :
    InternalPath
      (dynFromNext lineageTargetNext)
      lineageTargetClass
      LineageState.right
      LineageState.new := by
  exact internalPath_single_step trivial trivial trivial

theorem lineage_target_path_new_left :
    InternalPath
      (dynFromNext lineageTargetNext)
      lineageTargetClass
      LineageState.new
      LineageState.left := by
  exact internalPath_single_step trivial trivial trivial

theorem lineage_target_path_right_left :
    InternalPath
      (dynFromNext lineageTargetNext)
      lineageTargetClass
      LineageState.right
      LineageState.left := by
  exact internalPathAppend
    lineage_target_path_right_new
    lineage_target_path_new_left

theorem lineage_target_path_left_new :
    InternalPath
      (dynFromNext lineageTargetNext)
      lineageTargetClass
      LineageState.left
      LineageState.new := by
  exact internalPathAppend
    lineage_target_path_left_right
    lineage_target_path_right_new

theorem lineage_target_path_new_right :
    InternalPath
      (dynFromNext lineageTargetNext)
      lineageTargetClass
      LineageState.new
      LineageState.right := by
  exact internalPathAppend
    lineage_target_path_new_left
    lineage_target_path_left_right

theorem lineage_target_recurrent :
    RecurrentViableClass
      (dynFromNext lineageTargetNext)
      lineageSafe
      lineageTargetClass := by
  exact And.intro
    (by
      intro x _hx
      trivial)
    (And.intro
      (by
        intro x y hx hStep
        cases x <;> cases y <;> trivial)
      (And.intro
        (by
          intro x y hx hy
          cases x <;> cases y
          case left.left =>
            exact InternalPath.refl hx
          case left.old =>
            exact False.elim hy
          case left.new =>
            exact lineage_target_path_left_new
          case left.right =>
            exact lineage_target_path_left_right
          case old.left =>
            exact False.elim hx
          case old.old =>
            exact False.elim hx
          case old.new =>
            exact False.elim hx
          case old.right =>
            exact False.elim hx
          case new.left =>
            exact lineage_target_path_new_left
          case new.old =>
            exact False.elim hy
          case new.new =>
            exact InternalPath.refl hx
          case new.right =>
            exact lineage_target_path_new_right
          case right.left =>
            exact lineage_target_path_right_left
          case right.old =>
            exact False.elim hy
          case right.new =>
            exact lineage_target_path_right_new
          case right.right =>
            exact InternalPath.refl hx)
        (by
          intro x hx
          cases x
          case left =>
            exact Exists.intro LineageState.right (And.intro trivial trivial)
          case old =>
            exact False.elim hx
          case new =>
            exact Exists.intro LineageState.left (And.intro trivial trivial)
          case right =>
            exact Exists.intro LineageState.new (And.intro trivial trivial))))

theorem lineage_contract_left_right :
    RecurrentSupportLineageContract
      lineageTargetNext
      lineageSafe
      lineageTargetClass
      LineageState.left
      LineageState.right := by
  exact And.intro
    lineage_target_recurrent
    (And.intro
      trivial
      (And.intro
        trivial
        (And.intro
          lineage_target_path_left_right
          lineage_target_path_right_left)))

theorem lineage_target_carries_left_right :
    RecurrentSupportCarries
      lineageConsequenceSystem
      lineageTargetNext
      lineageSafe
      lineageTargetClass
      LineageState.left
      LineageState.right := by
  exact recurrentSupportCarries_lineage_of_contract
    lineage_source_carries_left_right
    lineage_contract_left_right

theorem incomparable_support_lineage_witness :
    SupportsIncomparable lineageSourceClass lineageTargetClass /\
    RecurrentSupportCarries
      lineageConsequenceSystem
      lineageSourceNext
      lineageSafe
      lineageSourceClass
      LineageState.left
      LineageState.right /\
    RecurrentSupportLineageContract
      lineageTargetNext
      lineageSafe
      lineageTargetClass
      LineageState.left
      LineageState.right /\
    RecurrentSupportCarries
      lineageConsequenceSystem
      lineageTargetNext
      lineageSafe
      lineageTargetClass
      LineageState.left
      LineageState.right := by
  exact And.intro
    lineage_supports_incomparable
    (And.intro
      lineage_source_carries_left_right
      (And.intro
        lineage_contract_left_right
        lineage_target_carries_left_right))

end RecurrentSupportLineage
end Trajectory
end OmegaProper
