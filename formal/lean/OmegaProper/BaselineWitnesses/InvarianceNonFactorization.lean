import OmegaProper.BaselineWitnesses.NonFactorization

/-!
OmegaProper.BaselineWitnesses.InvarianceNonFactorization

General non-factorization theorem for symmetry-forgetting summaries.

If a summary is invariant under a move but the declared target changes under
that move, then the target cannot factor through the summary.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace InvarianceNonFactorization

open NonFactorization

universe u v w

/-- A summary is invariant under a move when the move does not change it. -/
def SummaryInvariantUnder
    {A : Type u} {B : Type v}
    (summary : A -> B)
    (move : A -> A) : Prop :=
  forall x, summary (move x) = summary x

/-- A target changes under a move when at least one input is distinguished. -/
def TargetChangesUnder
    {A : Type u} {C : Type w}
    (target : A -> C)
    (move : A -> A) : Prop :=
  exists x, Not (target (move x) = target x)

/--
Any target that changes under a move cannot factor through a summary that is
invariant under that move.
-/
theorem invariant_summary_target_change_nonFactorization
    {A : Type u} {B : Type v} {C : Type w}
    {summary : A -> B}
    {target : A -> C}
    {move : A -> A}
    (hSummary : SummaryInvariantUnder summary move)
    (hTarget : TargetChangesUnder target move) :
    NonFactorization summary target := by
  match hTarget with
  | Exists.intro x hx =>
      exact nonFactorization_of_same_summary_different_target
        (hSummary x)
        hx

end InvarianceNonFactorization
end BaselineWitnesses
end OmegaProper
