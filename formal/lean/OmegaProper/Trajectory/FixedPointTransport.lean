import OmegaProper.Trajectory.PredicateFixpoint

/-!
OmegaProper.Trajectory.FixedPointTransport

Small reusable transport lemmas for predicate fixed points.

The reachability and viability reflection files use the same two proof shapes:

* least-fixed-point reflection by building a prefixed predicate over abstract
  states that says every exact representative satisfies the exact lfp;
* greatest-fixed-point reflection by pulling abstract postfixed predicates back
  along a presentation.

This file packages those proof shapes without adding a new dynamics ontology.
-/

namespace OmegaProper
namespace Trajectory
namespace FixedPointTransport

open PredicateFixpoint

universe u v

/-- Pull an abstract predicate back along a presentation. -/
def Pullback
    {X : Type u} {Q : Type v}
    (present : X -> Q)
    (p : Q -> Prop) : X -> Prop :=
  fun x => p (present x)

/-- A predicate on abstract states holding when every exact representative satisfies `p`. -/
def FiberForall
    {X : Type u} {Q : Type v}
    (present : X -> Q)
    (p : X -> Prop) : Q -> Prop :=
  fun q => forall x, present x = q -> p x

/--
Lfp reflection by a fiber-wise prefixed witness.

If the abstract transformer has `FiberForall present (lfp FX)` as a prefixed
point, then abstract lfp membership of `present x` reflects to exact lfp
membership of `x`.
-/
theorem lfp_reflects_of_fiberForall_prefixed
    {X : Type u} {Q : Type v}
    {FX : (X -> Prop) -> (X -> Prop)}
    {FQ : (Q -> Prop) -> (Q -> Prop)}
    {present : X -> Q}
    {x : X}
    (hPref :
      Prefixed FQ (FiberForall present (lfp FX)))
    (hQ : lfp FQ (present x)) :
    lfp FX x := by
  exact hQ (FiberForall present (lfp FX)) hPref x rfl

/--
Gfp reflection by pullback of postfixed predicates.

If every abstract postfixed predicate pulls back to an exact postfixed
predicate, then abstract gfp membership of `present x` reflects to exact gfp
membership of `x`.
-/
theorem gfp_reflects_of_pullback_postfixed
    {X : Type u} {Q : Type v}
    {FX : (X -> Prop) -> (X -> Prop)}
    {FQ : (Q -> Prop) -> (Q -> Prop)}
    {present : X -> Q}
    {x : X}
    (hPost :
      forall p, Postfixed FQ p -> Postfixed FX (Pullback present p))
    (hQ : gfp FQ (present x)) :
    gfp FX x := by
  match hQ with
  | Exists.intro p hp =>
      exact Exists.intro (Pullback present p)
        (And.intro
          (hPost p hp.left)
          hp.right)

end FixedPointTransport
end Trajectory
end OmegaProper
