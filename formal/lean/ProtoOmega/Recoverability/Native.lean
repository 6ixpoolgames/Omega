import ProtoOmega.Transport.Native

/-!
ProtoOmega.Recoverability.Native

Alpha-native recoverability layer over `ProtoOmega.Transport.Native`.

This is a ProtoOmega presentation layer, not primitive Alpha. `NonErasing` here
means requirement-relative transport coverage. Downstream interpretation is out
of scope for this module.
-/

namespace ProtoOmega
namespace Recoverability

universe u v x y

/-- A small presentation category of contexts and unfoldings. -/
structure ContextCategory where
  Ctx : Type u
  Hom : Ctx -> Ctx -> Type v
  id : (X : Ctx) -> Hom X X
  comp : {X Y Z : Ctx} -> Hom X Y -> Hom Y Z -> Hom X Z
  id_left : forall {X Y : Ctx} (f : Hom X Y), comp (id X) f = f
  id_right : forall {X Y : Ctx} (f : Hom X Y), comp f (id Y) = f
  assoc :
    forall {W X Y Z : Ctx}
      (f : Hom W X) (g : Hom X Y) (h : Hom Y Z),
      comp (comp f g) h = comp f (comp g h)

/-- Native recoverability model.

Each context receives an Alpha frame plus a presentation-level distinction
order. Each unfolding receives a native distinction transport. -/
structure NativeModel where
  C : ContextCategory.{u, v}
  frame : C.Ctx -> AlphaCore.Frame.{x, y}
  order : forall X : C.Ctx, Transport.DistOrder (frame X)
  A :
    forall {X Y : C.Ctx},
      C.Hom X Y ->
      Transport.NativeTransport (order X) (order Y)
  id_normal :
    forall {X : C.Ctx} (d e : (frame X).Dist),
      (A (C.id X)).rel d e <-> (order X).le d e
  lax_comp :
    forall {X Y Z : C.Ctx} (f : C.Hom X Y) (g : C.Hom Y Z),
      Transport.NativeTransport.Subset
        (Transport.NativeTransport.compose (A f) (A g))
        (A (C.comp f g))

namespace NativeModel

/-- Recoverability is native distinction transport along a declared unfolding. -/
def Recovers
    (M : NativeModel)
    {X Y : M.C.Ctx}
    (f : M.C.Hom X Y)
    (d : (M.frame X).Dist)
    (e : (M.frame Y).Dist) : Prop :=
  (M.A f).rel d e

/-- Requirement-relative transport coverage. -/
def NonErasing
    (M : NativeModel)
    {X Y : M.C.Ctx}
    (f : M.C.Hom X Y)
    (Req : (M.frame X).Dist -> Prop) : Prop :=
  forall d, Req d -> exists e, Recovers M f d e

theorem identity_recoverability
    (M : NativeModel)
    {X : M.C.Ctx}
    {d e : (M.frame X).Dist}
    (hle : (M.order X).le d e) :
    Recovers M (M.C.id X) d e := by
  exact (M.id_normal d e).mpr hle

theorem identity_recoverability_iff
    (M : NativeModel)
    {X : M.C.Ctx}
    (d e : (M.frame X).Dist) :
    Recovers M (M.C.id X) d e <-> (M.order X).le d e := by
  exact M.id_normal d e

theorem recoverability_weaken_source
    (M : NativeModel)
    {X Y : M.C.Ctx} {f : M.C.Hom X Y}
    {d d' : (M.frame X).Dist}
    {e : (M.frame Y).Dist}
    (hrec : Recovers M f d e)
    (hle : (M.order X).le d' d) :
    Recovers M f d' e := by
  exact (M.A f).closed hle hrec ((M.order Y).le_refl e)

theorem recoverability_strengthen_target
    (M : NativeModel)
    {X Y : M.C.Ctx} {f : M.C.Hom X Y}
    {d : (M.frame X).Dist}
    {e e' : (M.frame Y).Dist}
    (hrec : Recovers M f d e)
    (hle : (M.order Y).le e e') :
    Recovers M f d e' := by
  exact (M.A f).closed ((M.order X).le_refl d) hrec hle

theorem compositional_recoverability
    (M : NativeModel)
    {X Y Z : M.C.Ctx}
    {f : M.C.Hom X Y}
    {g : M.C.Hom Y Z}
    {d : (M.frame X).Dist}
    {e : (M.frame Y).Dist}
    {z : (M.frame Z).Dist}
    (h1 : Recovers M f d e)
    (h2 : Recovers M g e z) :
    Recovers M (M.C.comp f g) d z := by
  exact Transport.NativeTransport.compose_subset_of_rel
    (M.lax_comp f g) h1 h2

theorem non_erasure_monotonicity
    (M : NativeModel)
    {X Y : M.C.Ctx}
    {f : M.C.Hom X Y}
    (Req Req' : (M.frame X).Dist -> Prop)
    (hsub : forall d, Req' d -> Req d)
    (hne : NonErasing M f Req) :
    NonErasing M f Req' := by
  intro d hreq'
  exact hne d (hsub d hreq')

end NativeModel

end Recoverability
end ProtoOmega
