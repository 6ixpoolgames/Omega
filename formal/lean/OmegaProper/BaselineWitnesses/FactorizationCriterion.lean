import OmegaProper.BaselineWitnesses.NonFactorization

/-!
OmegaProper.BaselineWitnesses.FactorizationCriterion

Conservative factorization criterion for baseline summaries.

The key standard compression is: if a declared target factors through a
summary, it is constant on summary fibers. A finite witness with equal summary
and different target therefore refutes both factorization and fiber constancy.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace FactorizationCriterion

open NonFactorization

universe u v w

/--
`g` is constant on the fibers of `f`: equal summary values force equal target
values.
-/
def FiberConstant {A : Type u} {B : Type v} {C : Type w}
    (f : A -> B)
    (g : A -> C) : Prop :=
  forall x y, f x = f y -> g x = g y

/-- Factorization through a summary implies fiber constancy. -/
theorem factorsThrough_implies_fiberConstant
    {A : Type u} {B : Type v} {C : Type w}
    {f : A -> B}
    {g : A -> C}
    (h : FactorsThrough f g) :
    FiberConstant f g := by
  intro x y hxy
  exact factorsThrough_preserves_equal_summary h hxy

/-- A non-factorization witness refutes fiber constancy. -/
theorem nonFactorization_blocks_fiberConstant
    {A : Type u} {B : Type v} {C : Type w}
    {f : A -> B}
    {g : A -> C}
    (h : NonFactorization f g) :
    Not (FiberConstant f g) := by
  intro hFiber
  match h with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact hy.right (hFiber x y hy.left)

/-- Fiber constancy rules out non-factorization witnesses. -/
theorem fiberConstant_blocks_nonFactorization
    {A : Type u} {B : Type v} {C : Type w}
    {f : A -> B}
    {g : A -> C}
    (h : FiberConstant f g) :
    Not (NonFactorization f g) := by
  intro hNon
  exact nonFactorization_blocks_fiberConstant hNon h

/--
Non-factorization is equivalent to failure of fiber constancy.

This is the theorem needed by the baseline witness suite. A full total-map
converse from fiber constancy to `FactorsThrough f g` requires additional
handling of summary values outside the image of `f`.
-/
theorem nonFactorization_iff_not_fiberConstant
    {A : Type u} {B : Type v} {C : Type w}
    {f : A -> B}
    {g : A -> C} :
    NonFactorization f g <-> Not (FiberConstant f g) := by
  constructor
  · exact nonFactorization_blocks_fiberConstant
  · intro hNotFiber
    classical
    by_cases hNon : NonFactorization f g
    · exact hNon
    · exfalso
      apply hNotFiber
      intro x y hxy
      by_cases hTarget : g x = g y
      · exact hTarget
      · exfalso
        exact hNon
          (nonFactorization_of_same_summary_different_target hxy hTarget)

end FactorizationCriterion
end BaselineWitnesses
end OmegaProper
