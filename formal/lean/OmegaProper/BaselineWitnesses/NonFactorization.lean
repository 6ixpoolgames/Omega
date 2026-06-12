/-!
OmegaProper.BaselineWitnesses.NonFactorization

Common theorem schema for baseline witnesses.

Many finite witnesses have the shape: a proposed summary agrees on two systems
while the declared target differs. This is exactly a non-factorization witness:
the declared target cannot be recovered as a function of that summary.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace NonFactorization

universe u v w

/--
`g` factors through `f` when there is a post-map from summary values to target
values that reconstructs `g`.
-/
def FactorsThrough {A : Type u} {B : Type v} {C : Type w}
    (f : A -> B)
    (g : A -> C) : Prop :=
  exists h : B -> C, forall x, h (f x) = g x

/--
A non-factorization witness: two inputs have the same summary but different
declared target values.
-/
def NonFactorization {A : Type u} {B : Type v} {C : Type w}
    (f : A -> B)
    (g : A -> C) : Prop :=
  exists x y, f x = f y /\ Not (g x = g y)

/--
If `g` factors through `f`, equal `f` values force equal `g` values.
-/
theorem factorsThrough_preserves_equal_summary
    {A : Type u} {B : Type v} {C : Type w}
    {f : A -> B}
    {g : A -> C}
    (hFactor : FactorsThrough f g)
    {x y : A}
    (hxy : f x = f y) :
    g x = g y := by
  match hFactor with
  | Exists.intro h hh =>
      calc
        g x = h (f x) := (hh x).symm
        _ = h (f y) := by rw [hxy]
        _ = g y := hh y

/--
A non-factorization witness rules out factorization.

The converse requires a quotient/range or choice principle for summary values
outside the image of `f`, so this first module only states the direction used
by finite baseline witnesses.
-/
theorem nonFactorization_blocks_factorization
    {A : Type u} {B : Type v} {C : Type w}
    {f : A -> B}
    {g : A -> C}
    (hNon : NonFactorization f g) :
    Not (FactorsThrough f g) := by
  intro hFactor
  match hNon with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact hy.right
            (factorsThrough_preserves_equal_summary hFactor hy.left)

/--
Direct constructor for the common witness shape.
-/
theorem nonFactorization_of_same_summary_different_target
    {A : Type u} {B : Type v} {C : Type w}
    {f : A -> B}
    {g : A -> C}
    {x y : A}
    (hSummary : f x = f y)
    (hTarget : Not (g x = g y)) :
    NonFactorization f g := by
  exact Exists.intro x (Exists.intro y (And.intro hSummary hTarget))

end NonFactorization
end BaselineWitnesses
end OmegaProper
