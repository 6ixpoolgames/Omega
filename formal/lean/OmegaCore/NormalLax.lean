import OmegaCore.DistTrans

/-!
OmegaCore.NormalLax

Normal lax distinction transport models for Omega Primitive Calculus v0.

This module treats asymmetry as a normal lax assignment from relational
contexts to `DistTrans`.
-/

namespace OmegaCore

universe u v w

/-- A small internal category of relational contexts and unfoldings. -/
structure ContextCategory where
  Ctx : Type u
  Rel : Ctx -> Ctx -> Type v
  id : (X : Ctx) -> Rel X X
  comp : {X Y Z : Ctx} -> Rel X Y -> Rel Y Z -> Rel X Z
  id_left : forall {X Y : Ctx} (r : Rel X Y), comp (id X) r = r
  id_right : forall {X Y : Ctx} (r : Rel X Y), comp r (id Y) = r
  assoc :
    forall {W X Y Z : Ctx}
      (r : Rel W X) (s : Rel X Y) (t : Rel Y Z),
      comp (comp r s) t = comp r (comp s t)

/-- A normal lax support-level Omega model. The object part assigns each
context a distinction preorder. The morphism part assigns each unfolding a
closed distinction transport. -/
structure NormalLaxDistinctionTransport where
  C : ContextCategory.{u, v}
  Dist : C.Ctx -> Type w
  frame : forall X : C.Ctx, PreorderFrame (Dist X)
  A :
    forall {X Y : C.Ctx},
      C.Rel X Y -> DistTransport (frame X) (frame Y)
  id_normal :
    forall {X : C.Ctx} (d e : Dist X),
      (A (C.id X)).rel d e <-> (frame X).le d e
  lax_comp :
    forall {X Y Z : C.Ctx} (r : C.Rel X Y) (s : C.Rel Y Z),
      DistTransport.Subset
        (DistTransport.compose (A r) (A s))
        (A (C.comp r s))

namespace NormalLaxDistinctionTransport

/-- Recoverability is support-level distinction transport. -/
def Recovers
    (M : NormalLaxDistinctionTransport)
    {X Y : M.C.Ctx} (r : M.C.Rel X Y)
    (d : M.Dist X) (e : M.Dist Y) : Prop :=
  (M.A r).rel d e

/-- Non-erasure for a declared requirement set. -/
def NonErasing
    (M : NormalLaxDistinctionTransport)
    {X Y : M.C.Ctx} (r : M.C.Rel X Y)
    (Req : M.Dist X -> Prop) : Prop :=
  forall d, Req d -> exists e, Recovers M r d e

theorem identity_recoverability
    (M : NormalLaxDistinctionTransport)
    {X : M.C.Ctx} {d e : M.Dist X}
    (hle : (M.frame X).le d e) :
    Recovers M (M.C.id X) d e := by
  exact (M.id_normal d e).mpr hle

theorem identity_recoverability_iff
    (M : NormalLaxDistinctionTransport)
    {X : M.C.Ctx} (d e : M.Dist X) :
    Recovers M (M.C.id X) d e <-> (M.frame X).le d e := by
  exact M.id_normal d e

theorem recoverability_weaken_source
    (M : NormalLaxDistinctionTransport)
    {X Y : M.C.Ctx} {r : M.C.Rel X Y}
    {d d' : M.Dist X} {e : M.Dist Y}
    (hrec : Recovers M r d e)
    (hle : (M.frame X).le d' d) :
    Recovers M r d' e := by
  exact (M.A r).closed hle hrec ((M.frame Y).le_refl e)

theorem recoverability_strengthen_target
    (M : NormalLaxDistinctionTransport)
    {X Y : M.C.Ctx} {r : M.C.Rel X Y}
    {d : M.Dist X} {e e' : M.Dist Y}
    (hrec : Recovers M r d e)
    (hle : (M.frame Y).le e e') :
    Recovers M r d e' := by
  exact (M.A r).closed ((M.frame X).le_refl d) hrec hle

theorem compositional_recoverability
    (M : NormalLaxDistinctionTransport)
    {X Y Z : M.C.Ctx} {r : M.C.Rel X Y} {s : M.C.Rel Y Z}
    {d : M.Dist X} {e : M.Dist Y} {z : M.Dist Z}
    (hF : Recovers M r d e)
    (hG : Recovers M s e z) :
    Recovers M (M.C.comp r s) d z := by
  exact DistTransport.compose_subset_of_rel
    (M.lax_comp r s) hF hG

theorem non_erasure_monotonicity
    (M : NormalLaxDistinctionTransport)
    {X Y : M.C.Ctx} {r : M.C.Rel X Y}
    (Req Req' : M.Dist X -> Prop)
    (hsub : forall d, Req' d -> Req d)
    (hne : NonErasing M r Req) :
    NonErasing M r Req' := by
  intro d hreq'
  exact hne d (hsub d hreq')

/-- A process-bundle remains bookkeeping: it indexes tests but does not prove
identity, agency, valuerhood, or moral status. -/
structure ProcessBundle (M : NormalLaxDistinctionTransport) where
  X : M.C.Ctx
  Y : M.C.Ctx
  required : M.Dist X -> Prop
  unfold : M.C.Rel X Y

/-- Joint presentations are explicit and presentation-relative. -/
structure JointPresentation
    (M : NormalLaxDistinctionTransport)
    (I : Type u) (X : I -> M.C.Ctx) where
  J : M.C.Ctx
  emb : forall i, M.C.Rel (X i) J
  Y : M.C.Ctx
  unfold : M.C.Rel J Y

/-- Compatibility is n-ary joint non-erasure through the chosen presentation. -/
def Compatible
    (M : NormalLaxDistinctionTransport)
    {I : Type u} {X : I -> M.C.Ctx}
    (JP : JointPresentation M I X)
    (Req : forall i, M.Dist (X i) -> Prop) : Prop :=
  forall i, NonErasing M (M.C.comp (JP.emb i) JP.unfold) (Req i)

end NormalLaxDistinctionTransport

end OmegaCore
