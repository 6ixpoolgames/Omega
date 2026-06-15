import OmegaProper.Trajectory.RecurrentSupportRobustness

/-!
OmegaProper.Trajectory.IrreversibleRecurrentSupportLoss

One-way dynamic loss of recurrent support.

The finite witness here changes the two-state cycle into a one-way system:
`left` can still reach `right`, and both endpoints remain safe and supported,
but `right` cannot internally return to `left`. The consequence distinction is
therefore no longer recurrently carried.

This is a small irreversible-loss guardrail for recurrent support. It does not
define identity, agency, deformers, boundaries, value, alignment, or Omega
proper.
-/

namespace OmegaProper
namespace Trajectory
namespace IrreversibleRecurrentSupportLoss

open ConsequenceClasses
open ConsequenceRelation
open CarriedDistinction
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRobustness
open RecurrentViableClass
open SupportRestriction
open SupportUnderPerturbation
open SustainingViableClass

universe u

/--
Broken cycle dynamics: `left` can still move to `right`, but `right` can only
remain at `right`.
-/
def brokenCycleNext : CycleState -> CycleState -> Prop
  | CycleState.left, CycleState.right => True
  | CycleState.right, CycleState.right => True
  | _, _ => False

def brokenCycleDyn : Dyn where
  State := CycleState
  Next := brokenCycleNext

theorem brokenCycleClass_closedSustaining :
    ClosedSustainingViableClass brokenCycleDyn cycleSafe cycleClass := by
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
        exact Exists.intro CycleState.right (And.intro trivial trivial)

theorem broken_left_viable :
    Viable brokenCycleDyn cycleSafe CycleState.left := by
  exact closedSustainingClass_member_viable
    brokenCycleClass_closedSustaining
    trivial

theorem broken_right_viable :
    Viable brokenCycleDyn cycleSafe CycleState.right := by
  exact closedSustainingClass_member_viable
    brokenCycleClass_closedSustaining
    trivial

theorem broken_left_path_right :
    InternalPath
      (dynFromNext brokenCycleNext)
      cycleClass
      CycleState.left
      CycleState.right := by
  exact internalPath_single_step trivial trivial trivial

/--
Internal paths preserve any predicate that is preserved by every internal step.
This is a local helper for detecting that a one-way dynamics cannot carry a
reverse internal path.
-/
theorem internalPath_preserves_stepInvariant
    {D : Dyn.{u}}
    {C P : D.State -> Prop}
    {x y : D.State}
    (hInvariant :
      forall a b,
        C a ->
        C b ->
        D.Next a b ->
        P a ->
        P b)
    (hx : P x)
    (hPath :
      InternalPath
        D
        C
        x
        y) :
    P y := by
  induction hPath with
  | refl _hMem =>
      exact hx
  | step _hxMem _hyMem hEdge _hRest ih =>
      exact ih (hInvariant _ _ _hxMem _hyMem hEdge hx)

/-- Predicate selecting the right endpoint. -/
def IsRight : CycleState -> Prop
  | CycleState.left => False
  | CycleState.right => True

theorem brokenCycleNext_preserves_isRight :
    forall a b,
      cycleClass a ->
      cycleClass b ->
      brokenCycleNext a b ->
      IsRight a ->
      IsRight b := by
  intro a b _ha _hb hStep hRight
  cases a <;> cases b
  case left.left =>
    exact False.elim hStep
  case left.right =>
    trivial
  case right.left =>
    exact False.elim hStep
  case right.right =>
    trivial

theorem broken_no_path_right_left :
    Not (InternalPath
      (dynFromNext brokenCycleNext)
      cycleClass
      CycleState.right
      CycleState.left) := by
  intro hPath
  exact internalPath_preserves_stepInvariant
    brokenCycleNext_preserves_isRight
    trivial
    hPath

theorem broken_not_supports_merge_left_right :
    Not (SupportsMergeSeparatedPair
      cycleConsequenceSystem
      brokenCycleNext
      cycleClass
      CycleState.left
      CycleState.right) := by
  intro hSupport
  exact broken_no_path_right_left hSupport.right.right.right.left

theorem broken_not_recurrentSupportCarries_left_right :
    Not (RecurrentSupportCarries
      cycleConsequenceSystem
      brokenCycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right) := by
  exact not_recurrentSupportCarries_if_reverse_path_missing
    broken_no_path_right_left

theorem broken_destroys_recurrent_support :
    RecurrentSupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      brokenCycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right := by
  exact recurrentSupportDestroyed_if_reverse_path_missing
    cycle_recurrentSupportCarries_left_right
    broken_no_path_right_left

theorem irreversible_recurrent_support_loss_witness :
    RecurrentSupportCarries
      cycleConsequenceSystem
      cycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right /\
    Viable brokenCycleDyn cycleSafe CycleState.left /\
    Viable brokenCycleDyn cycleSafe CycleState.right /\
    InternalPath
      (dynFromNext brokenCycleNext)
      cycleClass
      CycleState.left
      CycleState.right /\
    Not (InternalPath
      (dynFromNext brokenCycleNext)
      cycleClass
      CycleState.right
      CycleState.left) /\
    RecurrentSupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      brokenCycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    cycle_recurrentSupportCarries_left_right
    (And.intro
      broken_left_viable
      (And.intro
        broken_right_viable
        (And.intro
          broken_left_path_right
          (And.intro
            broken_no_path_right_left
            broken_destroys_recurrent_support))))

end IrreversibleRecurrentSupportLoss
end Trajectory
end OmegaProper
