/-!
OmegaProper.Trajectory.PredicateFixpoint

Predicate fixed-point layer.

This file provides a small reusable least/greatest fixed-point calculus for
monotone operators on predicates. It does not define dynamics, reachability,
viability, value, agency, identity, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace PredicateFixpoint

universe u

/-- Predicate inclusion. -/
def PSub {X : Type u} (p q : X -> Prop) : Prop :=
  forall x, p x -> q x

/-- Monotonicity for predicate transformers. -/
def Mono {X : Type u} (F : (X -> Prop) -> (X -> Prop)) : Prop :=
  forall p q, PSub p q -> PSub (F p) (F q)

/-- A prefixed point satisfies `F p <= p`. -/
def Prefixed {X : Type u} (F : (X -> Prop) -> (X -> Prop))
    (p : X -> Prop) : Prop :=
  PSub (F p) p

/-- A postfixed point satisfies `p <= F p`. -/
def Postfixed {X : Type u} (F : (X -> Prop) -> (X -> Prop))
    (p : X -> Prop) : Prop :=
  PSub p (F p)

/-- Least fixed-point candidate: intersection of all prefixed points. -/
def lfp {X : Type u} (F : (X -> Prop) -> (X -> Prop)) : X -> Prop :=
  fun x => forall p, Prefixed F p -> p x

/-- Greatest fixed-point candidate: union of all postfixed points. -/
def gfp {X : Type u} (F : (X -> Prop) -> (X -> Prop)) : X -> Prop :=
  fun x => exists p, Postfixed F p /\ p x

theorem psub_refl {X : Type u} (p : X -> Prop) :
    PSub p p := by
  intro x hx
  exact hx

theorem psub_trans
    {X : Type u} {p q r : X -> Prop}
    (hpq : PSub p q)
    (hqr : PSub q r) :
    PSub p r := by
  intro x hx
  exact hqr x (hpq x hx)

/-- The least fixed-point candidate is below every prefixed point. -/
theorem lfp_le_prefixed
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    {p : X -> Prop}
    (hPref : Prefixed F p) :
    PSub (lfp F) p := by
  intro x hx
  exact hx p hPref

/-- Every postfixed point is below the greatest fixed-point candidate. -/
theorem postfixed_le_gfp
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    {p : X -> Prop}
    (hPost : Postfixed F p) :
    PSub p (gfp F) := by
  intro x hx
  exact Exists.intro p (And.intro hPost hx)

/-- Under monotonicity, `F (lfp F) <= lfp F`. -/
theorem F_lfp_le_lfp
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    (hMono : Mono F) :
    PSub (F (lfp F)) (lfp F) := by
  intro x hxF p hPref
  have hLfpSubP : PSub (lfp F) p := lfp_le_prefixed hPref
  have hFLfpSubFp : PSub (F (lfp F)) (F p) :=
    hMono (lfp F) p hLfpSubP
  exact hPref x (hFLfpSubFp x hxF)

/-- Under monotonicity, `lfp F <= F (lfp F)`. -/
theorem lfp_le_F_lfp
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    (hMono : Mono F) :
    PSub (lfp F) (F (lfp F)) := by
  intro x hxLfp
  exact hxLfp (F (lfp F)) (hMono (F (lfp F)) (lfp F) (F_lfp_le_lfp hMono))

/-- Under monotonicity, `lfp F` is a fixed point. -/
theorem lfp_fixed
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    (hMono : Mono F) :
    PSub (F (lfp F)) (lfp F) /\ PSub (lfp F) (F (lfp F)) := by
  exact And.intro (F_lfp_le_lfp hMono) (lfp_le_F_lfp hMono)

/-- Under monotonicity, `gfp F <= F (gfp F)`. -/
theorem gfp_le_F_gfp
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    (hMono : Mono F) :
    PSub (gfp F) (F (gfp F)) := by
  intro x hxGfp
  match hxGfp with
  | Exists.intro p hp =>
      have hPSubGfp : PSub p (gfp F) := postfixed_le_gfp hp.left
      have hFpSubFGfp : PSub (F p) (F (gfp F)) :=
        hMono p (gfp F) hPSubGfp
      exact hFpSubFGfp x (hp.left x hp.right)

/-- Under monotonicity, `F (gfp F) <= gfp F`. -/
theorem F_gfp_le_gfp
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    (hMono : Mono F) :
    PSub (F (gfp F)) (gfp F) := by
  intro x hxF
  exact Exists.intro (F (gfp F))
    (And.intro
      (hMono (gfp F) (F (gfp F)) (gfp_le_F_gfp hMono))
      hxF)

/-- Under monotonicity, `gfp F` is a fixed point. -/
theorem gfp_fixed
    {X : Type u}
    {F : (X -> Prop) -> (X -> Prop)}
    (hMono : Mono F) :
    PSub (gfp F) (F (gfp F)) /\ PSub (F (gfp F)) (gfp F) := by
  exact And.intro (gfp_le_F_gfp hMono) (F_gfp_le_gfp hMono)

end PredicateFixpoint
end Trajectory
end OmegaProper
