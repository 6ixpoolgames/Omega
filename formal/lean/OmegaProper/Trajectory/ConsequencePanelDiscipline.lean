import OmegaProper.Trajectory.ConsequenceComparison

/-!
OmegaProper.Trajectory.ConsequencePanelDiscipline

Panel-level guardrails for consequence systems.

This layer distinguishes three low-level degeneracies in an evaluated
consequence panel:

* no evaluated contexts;
* every evaluated comparison allows every pair;
* evaluated contexts refuse every pair.

It does not define relevance, quotient structure, deformers, or upward
trajectory objects. A local allowance in one evaluated context is not global
compatibility; compatibility still requires every evaluated context to compare
the pair.
-/

namespace OmegaProper
namespace Trajectory
namespace ConsequencePanelDiscipline

open ConsequenceRelation
open ConsequenceDiscipline
open ConsequenceComparison

universe w k o

/-- A context allows at least one pair of fragment consequences. -/
def ContextAllowsPair (S : ConsequenceSystem.{w, k, o})
    (c : S.Context) : Prop :=
  exists x y, S.Compare c (S.consequence c x) (S.consequence c y)

/-- A context refuses at least one pair of fragment consequences. -/
def ContextRefusesPair (S : ConsequenceSystem.{w, k, o})
    (c : S.Context) : Prop :=
  exists x y, Not (S.Compare c (S.consequence c x) (S.consequence c y))

/-- Some evaluated context allows at least one pair. -/
def EvaluatedContextAllowsPair (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists c, S.Evaluated c /\ ContextAllowsPair S c

/-- Some evaluated context refuses at least one pair. -/
def EvaluatedContextRefusesPair (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists c, S.Evaluated c /\ ContextRefusesPair S c

/--
A balanced panel has both an evaluated allowance and an evaluated refusal.

This is only a nondegeneracy guardrail. It does not say the contexts are
substantively relevant or that any proposed class/quotient is valid.
-/
def BalancedContextPanel (S : ConsequenceSystem.{w, k, o}) : Prop :=
  EvaluatedContextAllowsPair S /\ EvaluatedContextRefusesPair S

/--
Every evaluated context refuses every pair. This is an all-refusing panel
pathology, stronger than merely being noncollapsed.
-/
def EvaluatedContextsRefuseAllPairs (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall c, S.Evaluated c ->
    forall x y, Not (S.Compare c (S.consequence c x) (S.consequence c y))

theorem evaluated_context_refusal_separates
    {S : ConsequenceSystem.{w, k, o}}
    {c : S.Context}
    (hcEval : S.Evaluated c)
    {x y : S.Fragment}
    (hRefuse : Not (S.Compare c (S.consequence c x) (S.consequence c y))) :
    ConsequenceSeparated S x y := by
  exact Exists.intro c (And.intro hcEval hRefuse)

theorem evaluated_context_refuses_pair_noncollapsed
    {S : ConsequenceSystem.{w, k, o}}
    (h : EvaluatedContextRefusesPair S) :
    ConsequenceNoncollapsed S := by
  match h with
  | Exists.intro c hc =>
      match hc.right with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hxy =>
              exists x
              exists y
              exact evaluated_context_refusal_separates hc.left hxy

theorem balanced_has_evaluated_context
    {S : ConsequenceSystem.{w, k, o}}
    (h : BalancedContextPanel S) :
    HasEvaluatedContext S := by
  match h.left with
  | Exists.intro c hc =>
      exact Exists.intro c hc.left

theorem balanced_not_vacuous
    {S : ConsequenceSystem.{w, k, o}}
    (h : BalancedContextPanel S) :
    Not (EvaluationVacuous S) := by
  intro hvacuous
  match balanced_has_evaluated_context h with
  | Exists.intro c hcEval =>
      exact hvacuous c hcEval

theorem balanced_noncollapsed
    {S : ConsequenceSystem.{w, k, o}}
    (h : BalancedContextPanel S) :
    ConsequenceNoncollapsed S := by
  exact evaluated_context_refuses_pair_noncollapsed h.right

theorem balanced_not_universal_comparison
    {S : ConsequenceSystem.{w, k, o}}
    (h : BalancedContextPanel S) :
    Not (ComparisonUniversalOnEvaluated S) := by
  exact noncollapsed_not_universal_comparison (balanced_noncollapsed h)

theorem no_evaluated_refusals_collapses
    {S : ConsequenceSystem.{w, k, o}}
    (h : Not (EvaluatedContextRefusesPair S)) :
    ConsequenceCollapsed S := by
  intro x y
  apply not_separated_implies_compatible
  intro hsep
  match hsep with
  | Exists.intro c hc =>
      apply h
      exists c
      constructor
      case left =>
        exact hc.left
      case right =>
        exists x
        exists y
        exact hc.right

theorem refuse_all_blocks_evaluated_allowance
    {S : ConsequenceSystem.{w, k, o}}
    (hAll : EvaluatedContextsRefuseAllPairs S) :
    Not (EvaluatedContextAllowsPair S) := by
  intro hAllow
  match hAllow with
  | Exists.intro c hc =>
      match hc.right with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hxy =>
              exact hAll c hc.left x y hxy

theorem refuse_all_blocks_balanced_panel
    {S : ConsequenceSystem.{w, k, o}}
    (hAll : EvaluatedContextsRefuseAllPairs S) :
    Not (BalancedContextPanel S) := by
  intro hBalanced
  exact refuse_all_blocks_evaluated_allowance hAll hBalanced.left

theorem nonTransitive_toy_balanced_panel :
    BalancedContextPanel nonTransitiveToySystem := by
  exact And.intro
    (Exists.intro ToyContext.ctx
      (And.intro trivial
        (Exists.intro ToyFragment.a
          (Exists.intro ToyFragment.b toy_compare_zero_one))))
    (Exists.intro ToyContext.ctx
      (And.intro trivial
        (Exists.intro ToyFragment.a
          (Exists.intro ToyFragment.c toy_not_compare_zero_two))))

theorem all_refusing_contexts_refuse_all_pairs :
    EvaluatedContextsRefuseAllPairs allRefusingSystem := by
  intro c _hcEval x y
  cases c
  intro h
  exact h

theorem all_refusing_panel_not_balanced :
    Not (BalancedContextPanel allRefusingSystem) := by
  exact refuse_all_blocks_balanced_panel all_refusing_contexts_refuse_all_pairs

end ConsequencePanelDiscipline
end Trajectory
end OmegaProper
