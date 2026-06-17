import OmegaProper.BaselineWitnesses.NonFactorization
import OmegaProper.Trajectory.TargetPresentationInvariant

/-!
OmegaProper.Trajectory.ContinuationDeformation

Compression of "deformation" language into non-factorization.

The safe finite form of deformation is not a deformer object. It is a failure
of a proposed summary/presentation to determine a declared continuation fact:
same summary, different fact.
-/

namespace OmegaProper
namespace Trajectory
namespace ContinuationDeformation

open BaselineWitnesses.NonFactorization
open TargetPresentationInvariant

universe u v w

/--
A summary hides a fact when the fact does not factor through the summary.

This is the generic anti-Goodhart / proxy-failure shape.
-/
abbrev SummaryHidesFact
    {A : Type u}
    {B : Type v}
    {C : Type w}
    (summary : A -> B)
    (fact : A -> C) : Prop :=
  NonFactorization summary fact

/--
Finite continuation deformation: a declared continuation fact changes while
the proposed summary stays fixed.

This is deliberately an alias for non-factorization, not a new ontology.
-/
abbrev ContinuationDeformation
    {A : Type u}
    {B : Type v}
    {C : Type w}
    (summary : A -> B)
    (fact : A -> C) : Prop :=
  NonFactorization summary fact

theorem continuationDeformation_of_sameSummary_differentFact
    {A : Type u}
    {B : Type v}
    {C : Type w}
    {summary : A -> B}
    {fact : A -> C}
    {x y : A}
    (hSummary : summary x = summary y)
    (hFact : Not (fact x = fact y)) :
    ContinuationDeformation summary fact := by
  exact nonFactorization_of_same_summary_different_target hSummary hFact

theorem continuationDeformation_blocks_factorization
    {A : Type u}
    {B : Type v}
    {C : Type w}
    {summary : A -> B}
    {fact : A -> C}
    (h : ContinuationDeformation summary fact) :
    Not (FactorsThrough summary fact) := by
  exact nonFactorization_blocks_factorization h

/--
Target obstruction by a presentation is exactly non-factorization of the target
through that presentation.
-/
theorem targetObstructedByPresentation_iff_continuationDeformation
    {A : Type u}
    {Q : Type v}
    {T : Type w}
    (target : A -> T)
    (present : A -> Q) :
    TargetObstructedByPresentation target present <->
      ContinuationDeformation present target := by
  rfl

/--
If a target survives a presentation, there is no finite deformation witness
against that presentation.
-/
theorem targetRespectsPresentation_blocks_deformation
    {A : Type u}
    {Q : Type v}
    {T : Type w}
    {target : A -> T}
    {present : A -> Q}
    (hRespect : TargetRespectsPresentation target present) :
    Not (ContinuationDeformation present target) := by
  intro hDeform
  match hDeform with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact hy.right (hRespect x y hy.left)

end ContinuationDeformation
end Trajectory
end OmegaProper
