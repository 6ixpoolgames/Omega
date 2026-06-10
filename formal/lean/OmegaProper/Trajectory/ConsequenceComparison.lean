import OmegaProper.Trajectory.ConsequenceDiscipline

/-!
OmegaProper.Trajectory.ConsequenceComparison

Over-separation guardrails for consequence systems.

Noncollapse only says the apparatus can refuse at least one identification.
This layer records separate checks showing that an apparatus can also be too
sharp: it may refuse even self-comparison or every pairwise comparison.
-/

namespace OmegaProper
namespace Trajectory
namespace ConsequenceComparison

open ConsequenceRelation
open ConsequenceClasses
open ConsequenceDiscipline

universe w k o

/-- Every fragment is compatible with itself. -/
def SelfCompatible (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall x, ConsequenceCompatible S x x

/-- The system allows at least one compatible pair. -/
def HasCompatiblePair (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists x y, ConsequenceCompatible S x y

/-- The system allows at least one compatible pair of distinct fragments. -/
def HasDistinctCompatiblePair (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists x y, Not (x = y) /\ ConsequenceCompatible S x y

/-- Every pair is separated. This is an over-separation pathology. -/
def AllPairsSeparated (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall x y, ConsequenceSeparated S x y

/-- A system is over-separated when it separates every fragment from itself. -/
def SelfSeparated (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall x, ConsequenceSeparated S x x

/-- Every evaluated context compares each fragment consequence with itself. -/
def EvaluationSelfCompatible (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall c x,
    S.Evaluated c ->
    S.Compare c (S.consequence c x) (S.consequence c x)

/-- Some evaluated context allows at least one pair. -/
def HasEvaluatedCompatiblePair (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists c x y,
    S.Evaluated c /\
    S.Compare c (S.consequence c x) (S.consequence c y)

/-- Some evaluated context refuses at least one pair. -/
def HasEvaluatedRefusedPair (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists c x y,
    S.Evaluated c /\
    Not (S.Compare c (S.consequence c x) (S.consequence c y))

/--
A modest panel check: evaluated self-comparisons pass, and the evaluated panel
contains at least one allowance and at least one refusal.

This does not prove context relevance or substantive meaning.
-/
def EvaluatedPanelNonpathological (S : ConsequenceSystem.{w, k, o}) : Prop :=
  EvaluationSelfCompatible S /\
  HasEvaluatedCompatiblePair S /\
  HasEvaluatedRefusedPair S

theorem compare_reflexive_implies_self_compatible
    {S : ConsequenceSystem.{w, k, o}}
    (h : CompareReflexive S) :
    SelfCompatible S := by
  intro x
  exact compatible_refl_of_compare_reflexive h x

theorem evaluationSelfCompatible_implies_selfCompatible
    {S : ConsequenceSystem.{w, k, o}}
    (h : EvaluationSelfCompatible S) :
    SelfCompatible S := by
  intro x c hcEval
  exact h c x hcEval

theorem self_compatible_has_compatible_pair
    {S : ConsequenceSystem.{w, k, o}}
    (hSelf : SelfCompatible S)
    (hFrag : Nonempty S.Fragment) :
    HasCompatiblePair S := by
  match hFrag with
  | Nonempty.intro x =>
      exact Exists.intro x (Exists.intro x (hSelf x))

theorem all_pairs_separated_blocks_self_compatible_with_fragment
    {S : ConsequenceSystem.{w, k, o}}
    (hAll : AllPairsSeparated S)
    (hFrag : Nonempty S.Fragment) :
    Not (SelfCompatible S) := by
  intro hSelf
  match hFrag with
  | Nonempty.intro x =>
      exact compatible_not_separated (hSelf x) (hAll x x)

theorem all_pairs_separated_blocks_distinct_compatible
    {S : ConsequenceSystem.{w, k, o}}
    (hAll : AllPairsSeparated S) :
    Not (HasDistinctCompatiblePair S) := by
  intro hPair
  match hPair with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact compatible_not_separated hy.right (hAll x y)

theorem all_pairs_separated_noncollapsed_with_fragment
    {S : ConsequenceSystem.{w, k, o}}
    (hAll : AllPairsSeparated S)
    (hFrag : Nonempty S.Fragment) :
    ConsequenceNoncollapsed S := by
  match hFrag with
  | Nonempty.intro x =>
      exists x
      exists x
      exact hAll x x

theorem hasEvaluatedCompatiblePair_not_vacuous
    {S : ConsequenceSystem.{w, k, o}}
    (h : HasEvaluatedCompatiblePair S) :
    Not (EvaluationVacuous S) := by
  intro hvacuous
  match h with
  | Exists.intro c hc =>
      match hc with
      | Exists.intro _x hx =>
          match hx with
          | Exists.intro _y hy =>
              exact hvacuous c hy.left

theorem hasEvaluatedRefusedPair_noncollapsed
    {S : ConsequenceSystem.{w, k, o}}
    (h : HasEvaluatedRefusedPair S) :
    ConsequenceNoncollapsed S := by
  match h with
  | Exists.intro c hc =>
      match hc with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hy =>
              exact Exists.intro x
                (Exists.intro y
                  (Exists.intro c hy))

theorem evaluatedPanelNonpathological_selfCompatible
    {S : ConsequenceSystem.{w, k, o}}
    (h : EvaluatedPanelNonpathological S) :
    SelfCompatible S := by
  exact evaluationSelfCompatible_implies_selfCompatible h.left

theorem evaluatedPanelNonpathological_not_vacuous
    {S : ConsequenceSystem.{w, k, o}}
    (h : EvaluatedPanelNonpathological S) :
    Not (EvaluationVacuous S) := by
  exact hasEvaluatedCompatiblePair_not_vacuous h.right.left

theorem evaluatedPanelNonpathological_noncollapsed
    {S : ConsequenceSystem.{w, k, o}}
    (h : EvaluatedPanelNonpathological S) :
    ConsequenceNoncollapsed S := by
  exact hasEvaluatedRefusedPair_noncollapsed h.right.right

/-! ## All-refusing toy guardrail -/

inductive RefuseFragment where
  | only
  deriving DecidableEq

inductive RefuseContext where
  | ctx
  deriving DecidableEq

inductive RefuseOutcome where
  | out
  deriving DecidableEq

def allRefusingSystem : ConsequenceSystem where
  Fragment := RefuseFragment
  Context := RefuseContext
  Outcome := RefuseOutcome
  consequence := fun _ _ => RefuseOutcome.out
  Compare := fun _ _ _ => False
  Evaluated := fun _ => True

theorem all_refusing_all_pairs_separated :
    AllPairsSeparated allRefusingSystem := by
  intro x y
  exists RefuseContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    exact h

theorem all_refusing_noncollapsed :
    ConsequenceNoncollapsed allRefusingSystem := by
  exact all_pairs_separated_noncollapsed_with_fragment
    all_refusing_all_pairs_separated
    (Nonempty.intro RefuseFragment.only)

theorem all_refusing_not_self_compatible :
    Not (SelfCompatible allRefusingSystem) := by
  exact all_pairs_separated_blocks_self_compatible_with_fragment
    all_refusing_all_pairs_separated
    (Nonempty.intro RefuseFragment.only)

theorem all_refusing_no_distinct_compatible_pair :
    Not (HasDistinctCompatiblePair allRefusingSystem) := by
  exact all_pairs_separated_blocks_distinct_compatible all_refusing_all_pairs_separated

/--
Noncollapse alone is not enough: this toy is noncollapsed, but it rejects even
self-comparison.
-/
theorem noncollapsed_does_not_imply_self_compatible :
    ConsequenceNoncollapsed allRefusingSystem /\
    Not (SelfCompatible allRefusingSystem) := by
  exact And.intro all_refusing_noncollapsed all_refusing_not_self_compatible

theorem all_refusing_not_evaluatedPanelNonpathological :
    Not (EvaluatedPanelNonpathological allRefusingSystem) := by
  intro h
  exact all_refusing_not_self_compatible
    (evaluatedPanelNonpathological_selfCompatible h)

end ConsequenceComparison
end Trajectory
end OmegaProper
