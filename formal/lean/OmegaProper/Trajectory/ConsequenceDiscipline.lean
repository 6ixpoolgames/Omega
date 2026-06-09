import OmegaProper.Trajectory.ConsequenceClasses

/-!
OmegaProper.Trajectory.ConsequenceDiscipline

Collapse and noncollapse discipline for consequence systems.

This layer says when a consequence apparatus has at least one refused
identification. It does not define deformers or build upward from that refusal.
-/

namespace OmegaProper
namespace Trajectory
namespace ConsequenceDiscipline

open ConsequenceRelation
open ConsequenceClasses

universe w k o

/-- The evaluated comparison is universal when it compares every evaluated pair. -/
def ComparisonUniversalOnEvaluated (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall c z1 z2,
    S.Evaluated c ->
    S.Compare c z1 z2

/-- The evaluation is vacuous when no context is evaluated. -/
def EvaluationVacuous (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall c, Not (S.Evaluated c)

/-- A consequence system is noncollapsed when it has at least one separated pair. -/
abbrev ConsequenceNoncollapsed (S : ConsequenceSystem.{w, k, o}) : Prop :=
  HasSeparatedPair S

/-- A universal class contains every fragment. -/
def UniversalClass {S : ConsequenceSystem.{w, k, o}} (_x : S.Fragment) : Prop :=
  True

theorem vacuous_evaluation_collapses
    {S : ConsequenceSystem.{w, k, o}}
    (h : EvaluationVacuous S) :
    ConsequenceCollapsed S := by
  exact collapsed_of_no_evaluated_contexts h

theorem universal_comparison_collapses
    {S : ConsequenceSystem.{w, k, o}}
    (h : ComparisonUniversalOnEvaluated S) :
    ConsequenceCollapsed S := by
  exact collapsed_of_universal_compare h

theorem separated_pair_not_collapsed
    {S : ConsequenceSystem.{w, k, o}}
    (h : HasSeparatedPair S) :
    Not (ConsequenceCollapsed S) := by
  intro hCollapsed
  match h with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hxy =>
          exact separated_not_compatible hxy (hCollapsed x y)

theorem not_collapsed_has_separated_pair
    {S : ConsequenceSystem.{w, k, o}}
    (h : Not (ConsequenceCollapsed S)) :
    HasSeparatedPair S := by
  classical
  by_cases hsep : HasSeparatedPair S
  case pos =>
    exact hsep
  case neg =>
    exfalso
    apply h
    intro x y
    exact not_separated_implies_compatible (fun hxy => hsep (Exists.intro x (Exists.intro y hxy)))

theorem noncollapsed_iff_not_collapsed
    {S : ConsequenceSystem.{w, k, o}} :
    ConsequenceNoncollapsed S <-> Not (ConsequenceCollapsed S) := by
  constructor
  case mp =>
    exact separated_pair_not_collapsed
  case mpr =>
    exact not_collapsed_has_separated_pair

theorem noncollapsed_has_evaluated_context
    {S : ConsequenceSystem.{w, k, o}}
    (h : ConsequenceNoncollapsed S) :
    HasEvaluatedContext S := by
  match h with
  | Exists.intro _x hx =>
      match hx with
      | Exists.intro _y hsep =>
          match hsep with
          | Exists.intro c hc =>
              exact Exists.intro c hc.left

theorem noncollapsed_not_vacuous
    {S : ConsequenceSystem.{w, k, o}}
    (h : ConsequenceNoncollapsed S) :
    Not (EvaluationVacuous S) := by
  intro hvac
  exact separated_pair_not_collapsed h (vacuous_evaluation_collapses hvac)

theorem noncollapsed_not_universal_comparison
    {S : ConsequenceSystem.{w, k, o}}
    (h : ConsequenceNoncollapsed S) :
    Not (ComparisonUniversalOnEvaluated S) := by
  intro huniv
  exact separated_pair_not_collapsed h (universal_comparison_collapses huniv)

theorem universal_class_has_separated_pair_of_noncollapsed
    {S : ConsequenceSystem.{w, k, o}}
    (h : ConsequenceNoncollapsed S) :
    ClassHasSeparatedPair S (UniversalClass (S := S)) := by
  match h with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hxy =>
          exact Exists.intro x (Exists.intro y (And.intro trivial (And.intro trivial hxy)))

theorem universal_class_not_respects_consequences_of_noncollapsed
    {S : ConsequenceSystem.{w, k, o}}
    (h : ConsequenceNoncollapsed S) :
    Not (ClassRespectsConsequences S (UniversalClass (S := S))) := by
  exact separated_pair_blocks_class_respect
    (universal_class_has_separated_pair_of_noncollapsed h)

theorem toy_system_noncollapsed :
    ConsequenceNoncollapsed nonTransitiveToySystem := by
  exists ToyFragment.a
  exists ToyFragment.c
  exact toy_a_separated_c

theorem toy_system_not_collapsed :
    Not (ConsequenceCollapsed nonTransitiveToySystem) := by
  exact separated_pair_not_collapsed toy_system_noncollapsed

theorem toy_universal_class_not_respects_consequences :
    Not (ClassRespectsConsequences nonTransitiveToySystem
      (UniversalClass (S := nonTransitiveToySystem))) := by
  exact universal_class_not_respects_consequences_of_noncollapsed toy_system_noncollapsed

end ConsequenceDiscipline
end Trajectory
end OmegaProper
