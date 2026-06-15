import OmegaProper.Trajectory.SupportRestriction

/-!
OmegaProper.Trajectory.SupportUnderPerturbation

Support integrity under changed support predicates.

This file does not define perturbing objects, agents, deformers, identity, or
boundaries. It only records a small support-level fact: a changed support
predicate preserves a carried merge-separated pair only when the new support
still carries that pair. Dropping an endpoint destroys support for the pair.
-/

namespace OmegaProper
namespace Trajectory
namespace SupportUnderPerturbation

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
A support change preserves integrity for a fixed merge-separated pair when
support for that pair in `C` transfers to support for the same pair in `D`.

This is pair-relative and support-relative. It is not an identity claim about
an object persisting through perturbation.
-/
def SupportIntegrityUnder
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  SupportsMergeSeparatedPair S Next C x y ->
    SupportsMergeSeparatedPair S Next D x y

/--
A support change destroys support for a fixed merge-separated pair when the
original support carries the pair and the changed support does not.
-/
def SupportDestroyedUnder
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (C D : S.Fragment -> Prop)
    (x y : S.Fragment) : Prop :=
  SupportsMergeSeparatedPair S Next C x y /\
    Not (SupportsMergeSeparatedPair S Next D x y)

theorem sameSupport_preserves_integrity
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C : S.Fragment -> Prop}
    {x y : S.Fragment} :
    SupportIntegrityUnder S Next C C x y := by
  intro hSupport
  exact hSupport

theorem supportDestroyed_not_integrity
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hDestroyed : SupportDestroyedUnder S Next C D x y) :
    Not (SupportIntegrityUnder S Next C D x y) := by
  intro hIntegrity
  exact hDestroyed.right (hIntegrity hDestroyed.left)

theorem supportDestroyed_if_left_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next C x y)
    (hMissing : Not (D x)) :
    SupportDestroyedUnder S Next C D x y := by
  exact And.intro
    hSupport
    (not_mergeSupports_if_left_missing hMissing)

theorem supportDestroyed_if_right_missing
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next C x y)
    (hMissing : Not (D y)) :
    SupportDestroyedUnder S Next C D x y := by
  exact And.intro
    hSupport
    (not_mergeSupports_if_right_missing hMissing)

/-! ## Tiny finite perturbation witness -/

/--
Three declared support levels for the finite recurrent cycle witness.

`mild` keeps the recurrent support unchanged. `severe` removes the right
endpoint of the carried pair. These are named support predicates, not a
numeric physical perturbation model.
-/
inductive CyclePerturbationLevel where
  | baseline
  | mild
  | severe

/-- Support predicate selected by a declared perturbation level. -/
def cycleSupportAt : CyclePerturbationLevel -> CycleState -> Prop
  | CyclePerturbationLevel.baseline => cycleClass
  | CyclePerturbationLevel.mild => cycleClass
  | CyclePerturbationLevel.severe => leftOnlyClass

theorem cycle_baseline_supports_merge_left_right :
    SupportsMergeSeparatedPair
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.baseline)
      CycleState.left
      CycleState.right := by
  exact cycleClass_pathCarries_merge_left_right

theorem cycle_mild_supports_merge_left_right :
    SupportsMergeSeparatedPair
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.mild)
      CycleState.left
      CycleState.right := by
  exact cycleClass_pathCarries_merge_left_right

theorem cycle_severe_not_supports_merge_left_right :
    Not (SupportsMergeSeparatedPair
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.severe)
      CycleState.left
      CycleState.right) := by
  exact leftOnly_not_mergeSupports_left_right

theorem cycle_mild_preserves_baseline_support_integrity :
    SupportIntegrityUnder
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.baseline)
      (cycleSupportAt CyclePerturbationLevel.mild)
      CycleState.left
      CycleState.right := by
  exact sameSupport_preserves_integrity

theorem cycle_severe_destroys_baseline_support :
    SupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.baseline)
      (cycleSupportAt CyclePerturbationLevel.severe)
      CycleState.left
      CycleState.right := by
  exact And.intro
    cycle_baseline_supports_merge_left_right
    cycle_severe_not_supports_merge_left_right

theorem cycle_severe_not_support_integrity :
    Not (SupportIntegrityUnder
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.baseline)
      (cycleSupportAt CyclePerturbationLevel.severe)
      CycleState.left
      CycleState.right) := by
  exact supportDestroyed_not_integrity
    cycle_severe_destroys_baseline_support

theorem cycle_support_threshold_witness :
    SupportsMergeSeparatedPair
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.baseline)
      CycleState.left
      CycleState.right /\
    SupportIntegrityUnder
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.baseline)
      (cycleSupportAt CyclePerturbationLevel.mild)
      CycleState.left
      CycleState.right /\
    SupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      (cycleSupportAt CyclePerturbationLevel.baseline)
      (cycleSupportAt CyclePerturbationLevel.severe)
      CycleState.left
      CycleState.right := by
  exact And.intro
    cycle_baseline_supports_merge_left_right
    (And.intro
      cycle_mild_preserves_baseline_support_integrity
      cycle_severe_destroys_baseline_support)

end SupportUnderPerturbation
end Trajectory
end OmegaProper
