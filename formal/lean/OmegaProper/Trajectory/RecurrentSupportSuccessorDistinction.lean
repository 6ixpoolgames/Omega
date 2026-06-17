import OmegaProper.Trajectory.RecurrentSupportLineage

/-!
OmegaProper.Trajectory.RecurrentSupportSuccessorDistinction

Successor-distinction handoff for recurrently carried consequence distinctions.

`RecurrentSupportLineage` still uses the same declared endpoints `x,y` in the
source and target supports. This file allows the carried pair itself to change:
source support `C` carries `x,y`, while target support `D` carries a translated
pair `x',y'`.

The translation is explicit. A relation connects `x` to `x'` and `y` to `y'`,
and the contract requires merge-separation of `x,y` to imply
merge-separation of `x',y'`.

This is not identity, recoverability, agency, deformer structure, value,
alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportSuccessorDistinction

open ConsequenceRelation
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportLineage
open RecurrentSupportPathTransfer
open RecurrentSupportRobustness
open RecurrentViableClass
open SustainingViableClass

universe w k o

/--
A pair translation relates source endpoints `x,y` to target endpoints `x',y'`.
-/
def PairTranslation
    {X : Type w}
    (R : X -> X -> Prop)
    (x y x' y' : X) : Prop :=
  R x x' /\ R y y'

/--
A translation preserves merge-separation when source merge-separation implies
target merge-separation.
-/
def MergeSeparationPreservingTranslation
    (S : ConsequenceSystem.{w, k, o})
    (R : S.Fragment -> S.Fragment -> Prop)
    (x y x' y' : S.Fragment) : Prop :=
  PairTranslation R x y x' y' /\
    (ConsequenceMergeSeparated S x y ->
      ConsequenceMergeSeparated S x' y')

/--
Successor-distinction handoff contract.

The target support must recurrently carry the translated endpoints, and the
translation must preserve merge-separation from the source pair to the target
pair.
-/
def RecurrentSupportSuccessorContract
    (S : ConsequenceSystem.{w, k, o})
    (Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe1 : S.Fragment -> Prop)
    (D : S.Fragment -> Prop)
    (R : S.Fragment -> S.Fragment -> Prop)
    (x y x' y' : S.Fragment) : Prop :=
  RecurrentViableClass (dynFromNext Next1) safe1 D /\
    D x' /\
    D y' /\
    InternalPath (dynFromNext Next1) D x' y' /\
    InternalPath (dynFromNext Next1) D y' x' /\
    MergeSeparationPreservingTranslation S R x y x' y'

theorem supportsMergeSeparatedPair_successor_of_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe1 C D : S.Fragment -> Prop}
    {R : S.Fragment -> S.Fragment -> Prop}
    {x y x' y' : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next0 C x y)
    (hContract :
      RecurrentSupportSuccessorContract S Next1 safe1 D R x y x' y') :
    SupportsMergeSeparatedPair S Next1 D x' y' := by
  exact And.intro
    hContract.right.left
    (And.intro
      hContract.right.right.left
      (And.intro
        hContract.right.right.right.left
        (And.intro
          hContract.right.right.right.right.left
          (hContract.right.right.right.right.right.right
            hSupport.right.right.right.right))))

theorem recurrentSupportCarries_successor_of_contract
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 C D : S.Fragment -> Prop}
    {R : S.Fragment -> S.Fragment -> Prop}
    {x y x' y' : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x y)
    (hContract :
      RecurrentSupportSuccessorContract S Next1 safe1 D R x y x' y') :
    RecurrentSupportCarries S Next1 safe1 D x' y' := by
  exact And.intro
    hContract.left
    (supportsMergeSeparatedPair_successor_of_contract hCarry.right hContract)

/-! ## Finite successor-distinction witness -/

inductive SuccessorState where
  | sourceLeft
  | sourceRight
  | targetLeft
  | bridge
  | targetRight
  deriving DecidableEq

def successorSourceClass : SuccessorState -> Prop
  | SuccessorState.sourceLeft => True
  | SuccessorState.sourceRight => True
  | _ => False

def successorTargetClass : SuccessorState -> Prop
  | SuccessorState.targetLeft => True
  | SuccessorState.bridge => True
  | SuccessorState.targetRight => True
  | _ => False

def successorSafe (_x : SuccessorState) : Prop :=
  True

def successorSourceNext : SuccessorState -> SuccessorState -> Prop
  | SuccessorState.sourceLeft, SuccessorState.sourceRight => True
  | SuccessorState.sourceRight, SuccessorState.sourceLeft => True
  | _, _ => False

def successorTargetNext : SuccessorState -> SuccessorState -> Prop
  | SuccessorState.targetLeft, SuccessorState.bridge => True
  | SuccessorState.bridge, SuccessorState.targetRight => True
  | SuccessorState.targetRight, SuccessorState.targetLeft => True
  | _, _ => False

inductive SuccessorContext where
  | ctx
  deriving DecidableEq

inductive SuccessorOutcome where
  | left
  | right
  | other
  deriving DecidableEq

def successorOutcome : SuccessorState -> SuccessorOutcome
  | SuccessorState.sourceLeft => SuccessorOutcome.left
  | SuccessorState.targetLeft => SuccessorOutcome.left
  | SuccessorState.sourceRight => SuccessorOutcome.right
  | SuccessorState.targetRight => SuccessorOutcome.right
  | SuccessorState.bridge => SuccessorOutcome.other

def successorConsequenceSystem : ConsequenceSystem where
  Fragment := SuccessorState
  Context := SuccessorContext
  Outcome := SuccessorOutcome
  consequence := fun _ x => successorOutcome x
  Compare := fun _ x y => x = y
  Evaluated := fun _ => True

def successorTranslation : SuccessorState -> SuccessorState -> Prop
  | SuccessorState.sourceLeft, SuccessorState.targetLeft => True
  | SuccessorState.sourceRight, SuccessorState.targetRight => True
  | _, _ => False

theorem successor_sourceLeft_separated_sourceRight :
    ConsequenceSeparated
      successorConsequenceSystem
      SuccessorState.sourceLeft
      SuccessorState.sourceRight := by
  exists SuccessorContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem successor_targetLeft_separated_targetRight :
    ConsequenceSeparated
      successorConsequenceSystem
      SuccessorState.targetLeft
      SuccessorState.targetRight := by
  exists SuccessorContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem successor_translation_preserves_merge :
    MergeSeparationPreservingTranslation
      successorConsequenceSystem
      successorTranslation
      SuccessorState.sourceLeft
      SuccessorState.sourceRight
      SuccessorState.targetLeft
      SuccessorState.targetRight := by
  exact And.intro
    (And.intro trivial trivial)
    (by
      intro _hSep
      exact separated_implies_mergeSeparated
        successor_targetLeft_separated_targetRight)

theorem successor_source_path_left_right :
    InternalPath
      (dynFromNext successorSourceNext)
      successorSourceClass
      SuccessorState.sourceLeft
      SuccessorState.sourceRight := by
  exact internalPath_single_step trivial trivial trivial

theorem successor_source_path_right_left :
    InternalPath
      (dynFromNext successorSourceNext)
      successorSourceClass
      SuccessorState.sourceRight
      SuccessorState.sourceLeft := by
  exact internalPath_single_step trivial trivial trivial

theorem successor_source_recurrent :
    RecurrentViableClass
      (dynFromNext successorSourceNext)
      successorSafe
      successorSourceClass := by
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
          case sourceLeft.sourceLeft =>
            exact InternalPath.refl hx
          case sourceLeft.sourceRight =>
            exact successor_source_path_left_right
          case sourceLeft.targetLeft =>
            exact False.elim hy
          case sourceLeft.bridge =>
            exact False.elim hy
          case sourceLeft.targetRight =>
            exact False.elim hy
          case sourceRight.sourceLeft =>
            exact successor_source_path_right_left
          case sourceRight.sourceRight =>
            exact InternalPath.refl hx
          case sourceRight.targetLeft =>
            exact False.elim hy
          case sourceRight.bridge =>
            exact False.elim hy
          case sourceRight.targetRight =>
            exact False.elim hy
          case targetLeft.sourceLeft =>
            exact False.elim hx
          case targetLeft.sourceRight =>
            exact False.elim hx
          case targetLeft.targetLeft =>
            exact False.elim hx
          case targetLeft.bridge =>
            exact False.elim hx
          case targetLeft.targetRight =>
            exact False.elim hx
          case bridge.sourceLeft =>
            exact False.elim hx
          case bridge.sourceRight =>
            exact False.elim hx
          case bridge.targetLeft =>
            exact False.elim hx
          case bridge.bridge =>
            exact False.elim hx
          case bridge.targetRight =>
            exact False.elim hx
          case targetRight.sourceLeft =>
            exact False.elim hx
          case targetRight.sourceRight =>
            exact False.elim hx
          case targetRight.targetLeft =>
            exact False.elim hx
          case targetRight.bridge =>
            exact False.elim hx
          case targetRight.targetRight =>
            exact False.elim hx)
        (by
          intro x hx
          cases x
          case sourceLeft =>
            exact Exists.intro SuccessorState.sourceRight
              (And.intro trivial trivial)
          case sourceRight =>
            exact Exists.intro SuccessorState.sourceLeft
              (And.intro trivial trivial)
          case targetLeft =>
            exact False.elim hx
          case bridge =>
            exact False.elim hx
          case targetRight =>
            exact False.elim hx)))

theorem successor_source_supports_left_right :
    SupportsMergeSeparatedPair
      successorConsequenceSystem
      successorSourceNext
      successorSourceClass
      SuccessorState.sourceLeft
      SuccessorState.sourceRight := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        successor_source_path_left_right
        (And.intro
          successor_source_path_right_left
          (separated_implies_mergeSeparated
            successor_sourceLeft_separated_sourceRight))))

theorem successor_source_carries_left_right :
    RecurrentSupportCarries
      successorConsequenceSystem
      successorSourceNext
      successorSafe
      successorSourceClass
      SuccessorState.sourceLeft
      SuccessorState.sourceRight := by
  exact And.intro
    successor_source_recurrent
    successor_source_supports_left_right

theorem successor_target_path_left_bridge :
    InternalPath
      (dynFromNext successorTargetNext)
      successorTargetClass
      SuccessorState.targetLeft
      SuccessorState.bridge := by
  exact internalPath_single_step trivial trivial trivial

theorem successor_target_path_bridge_right :
    InternalPath
      (dynFromNext successorTargetNext)
      successorTargetClass
      SuccessorState.bridge
      SuccessorState.targetRight := by
  exact internalPath_single_step trivial trivial trivial

theorem successor_target_path_left_right :
    InternalPath
      (dynFromNext successorTargetNext)
      successorTargetClass
      SuccessorState.targetLeft
      SuccessorState.targetRight := by
  exact internalPathAppend
    successor_target_path_left_bridge
    successor_target_path_bridge_right

theorem successor_target_path_right_left :
    InternalPath
      (dynFromNext successorTargetNext)
      successorTargetClass
      SuccessorState.targetRight
      SuccessorState.targetLeft := by
  exact internalPath_single_step trivial trivial trivial

theorem successor_target_path_right_bridge :
    InternalPath
      (dynFromNext successorTargetNext)
      successorTargetClass
      SuccessorState.targetRight
      SuccessorState.bridge := by
  exact internalPathAppend
    successor_target_path_right_left
    successor_target_path_left_bridge

theorem successor_target_path_bridge_left :
    InternalPath
      (dynFromNext successorTargetNext)
      successorTargetClass
      SuccessorState.bridge
      SuccessorState.targetLeft := by
  exact internalPathAppend
    successor_target_path_bridge_right
    successor_target_path_right_left

theorem successor_target_recurrent :
    RecurrentViableClass
      (dynFromNext successorTargetNext)
      successorSafe
      successorTargetClass := by
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
          case sourceLeft.sourceLeft =>
            exact False.elim hx
          case sourceLeft.sourceRight =>
            exact False.elim hx
          case sourceLeft.targetLeft =>
            exact False.elim hx
          case sourceLeft.bridge =>
            exact False.elim hx
          case sourceLeft.targetRight =>
            exact False.elim hx
          case sourceRight.sourceLeft =>
            exact False.elim hx
          case sourceRight.sourceRight =>
            exact False.elim hx
          case sourceRight.targetLeft =>
            exact False.elim hx
          case sourceRight.bridge =>
            exact False.elim hx
          case sourceRight.targetRight =>
            exact False.elim hx
          case targetLeft.sourceLeft =>
            exact False.elim hy
          case targetLeft.sourceRight =>
            exact False.elim hy
          case targetLeft.targetLeft =>
            exact InternalPath.refl hx
          case targetLeft.bridge =>
            exact successor_target_path_left_bridge
          case targetLeft.targetRight =>
            exact successor_target_path_left_right
          case bridge.sourceLeft =>
            exact False.elim hy
          case bridge.sourceRight =>
            exact False.elim hy
          case bridge.targetLeft =>
            exact successor_target_path_bridge_left
          case bridge.bridge =>
            exact InternalPath.refl hx
          case bridge.targetRight =>
            exact successor_target_path_bridge_right
          case targetRight.sourceLeft =>
            exact False.elim hy
          case targetRight.sourceRight =>
            exact False.elim hy
          case targetRight.targetLeft =>
            exact successor_target_path_right_left
          case targetRight.bridge =>
            exact successor_target_path_right_bridge
          case targetRight.targetRight =>
            exact InternalPath.refl hx)
        (by
          intro x hx
          cases x
          case sourceLeft =>
            exact False.elim hx
          case sourceRight =>
            exact False.elim hx
          case targetLeft =>
            exact Exists.intro SuccessorState.bridge
              (And.intro trivial trivial)
          case bridge =>
            exact Exists.intro SuccessorState.targetRight
              (And.intro trivial trivial)
          case targetRight =>
            exact Exists.intro SuccessorState.targetLeft
              (And.intro trivial trivial))))

theorem successor_contract_left_right :
    RecurrentSupportSuccessorContract
      successorConsequenceSystem
      successorTargetNext
      successorSafe
      successorTargetClass
      successorTranslation
      SuccessorState.sourceLeft
      SuccessorState.sourceRight
      SuccessorState.targetLeft
      SuccessorState.targetRight := by
  exact And.intro
    successor_target_recurrent
    (And.intro
      trivial
      (And.intro
        trivial
        (And.intro
          successor_target_path_left_right
          (And.intro
            successor_target_path_right_left
            successor_translation_preserves_merge))))

theorem successor_target_carries_translated_pair :
    RecurrentSupportCarries
      successorConsequenceSystem
      successorTargetNext
      successorSafe
      successorTargetClass
      SuccessorState.targetLeft
      SuccessorState.targetRight := by
  exact recurrentSupportCarries_successor_of_contract
    successor_source_carries_left_right
    successor_contract_left_right

theorem successor_distinction_handoff_witness :
    RecurrentSupportCarries
      successorConsequenceSystem
      successorSourceNext
      successorSafe
      successorSourceClass
      SuccessorState.sourceLeft
      SuccessorState.sourceRight /\
    RecurrentSupportSuccessorContract
      successorConsequenceSystem
      successorTargetNext
      successorSafe
      successorTargetClass
      successorTranslation
      SuccessorState.sourceLeft
      SuccessorState.sourceRight
      SuccessorState.targetLeft
      SuccessorState.targetRight /\
    RecurrentSupportCarries
      successorConsequenceSystem
      successorTargetNext
      successorSafe
      successorTargetClass
      SuccessorState.targetLeft
      SuccessorState.targetRight := by
  exact And.intro
    successor_source_carries_left_right
    (And.intro
      successor_contract_left_right
      successor_target_carries_translated_pair)

end RecurrentSupportSuccessorDistinction
end Trajectory
end OmegaProper
