/-!
OmegaCore.PrimitiveWitness

This file pressure-tests the proposed "Omega Primitive Calculus v0" as a
substrate-independent witness calculus. It formalizes the recoverability,
non-erasure, and joint-presentation fragments without committing to a numeric
support codomain or a quantale-presheaf presentation.
-/

namespace OmegaCore

universe u v w x

/--
A minimal primitive witness calculus.

`Ctx`, `Rel`, and `Dist` are bookkeeping types for the three primitive roles:
relation, distinction, and asymmetry. The primitive asymmetry role appears as
typed witnesses `Wit r d e`, read as "d transports through r into e".
-/
structure PrimitiveCalculus where
  Ctx : Type u
  Rel : Ctx -> Ctx -> Type v
  id : (X : Ctx) -> Rel X X
  comp : {X Y Z : Ctx} -> Rel X Y -> Rel Y Z -> Rel X Z

  Dist : Ctx -> Type w
  dle : {X : Ctx} -> Dist X -> Dist X -> Prop
  dle_refl : forall {X : Ctx} (d : Dist X), dle d d
  dle_trans : forall {X : Ctx} {a b c : Dist X}, dle a b -> dle b c -> dle a c

  Wit : {X Y : Ctx} -> Rel X Y -> Dist X -> Dist Y -> Type x

  /-- Witness-strength preorder. It permits endpoint weakening/strengthening,
  so the compared witnesses need not have identical source/target distinctions. -/
  wle :
    {X Y : Ctx} -> {r : Rel X Y} ->
    {d d' : Dist X} -> {e e' : Dist Y} ->
    Wit r d e -> Wit r d' e' -> Prop
  wle_refl :
    forall {X Y : Ctx} {r : Rel X Y} {d : Dist X} {e : Dist Y}
      (a : Wit r d e), wle a a
  wle_trans :
    forall {X Y : Ctx} {r : Rel X Y}
      {d1 d2 d3 : Dist X} {e1 e2 e3 : Dist Y}
      {a : Wit r d1 e1} {b : Wit r d2 e2} {c : Wit r d3 e3},
      wle a b -> wle b c -> wle a c

  /-- Identity relation recovers a coarser distinction from a finer one. -/
  id_wit :
    forall {X : Ctx} {d e : Dist X}, dle d e -> Wit (id X) d e

  /-- If a relation carries `d` to `e`, it also carries any coarser source
  distinction to any finer target distinction, with no weaker witness support. -/
  weaken_strengthen :
    forall {X Y : Ctx} {r : Rel X Y}
      {d d' : Dist X} {e e' : Dist Y}
      (a : Wit r d e),
      dle d' d -> dle e e' ->
      exists a' : Wit r d' e', wle a a'

  /-- Sequential witness composition. The condition `dle h e` says the first
  target distinction is fine enough to supply the source distinction required by
  the second witness. -/
  compose_wit :
    forall {X Y Z : Ctx} {r : Rel X Y} {s : Rel Y Z}
      {d : Dist X} {e h : Dist Y} {z : Dist Z},
      Wit r d e -> Wit s h z -> dle h e -> Wit (comp r s) d z

  /-- Witness composition preserves witness strengthening. This is the first
  formal version of Axiom A6. -/
  compose_mono :
    forall {X Y Z : Ctx} {r : Rel X Y} {s : Rel Y Z}
      {d d' : Dist X} {e e' h h' : Dist Y} {z z' : Dist Z}
      {a : Wit r d e} {a' : Wit r d' e'}
      {b : Wit s h z} {b' : Wit s h' z'},
      wle a a' -> wle b b' ->
      (mid : dle h e) -> (mid' : dle h' e') ->
      wle (compose_wit a b mid) (compose_wit a' b' mid')

namespace PrimitiveWitness

/-- Target distinction `e` recovers source distinction `d` through relation `r`
when there exists an asymmetric distinction-transport witness. -/
def Recovers
    (K : PrimitiveCalculus)
    {X Y : K.Ctx} (r : K.Rel X Y)
    (d : K.Dist X) (e : K.Dist Y) : Prop :=
  Nonempty (K.Wit r d e)

/-- A relation is non-erasing for a declared requirement set if every required
source distinction has some recovering target distinction. -/
def NonErasing
    (K : PrimitiveCalculus)
    {X Y : K.Ctx} (r : K.Rel X Y)
    (Req : K.Dist X -> Prop) : Prop :=
  forall d, Req d -> exists e, Recovers K r d e

theorem recoverability_weaken_source
    (K : PrimitiveCalculus)
    {X Y : K.Ctx} {r : K.Rel X Y}
    {d d' : K.Dist X} {e : K.Dist Y}
    (hrec : Recovers K r d e)
    (hle : K.dle d' d) :
    Recovers K r d' e := by
  cases hrec with
  | intro a =>
      exact Exists.elim
        (K.weaken_strengthen a hle (K.dle_refl e))
        (fun a' _ => Nonempty.intro a')

theorem recoverability_strengthen_target
    (K : PrimitiveCalculus)
    {X Y : K.Ctx} {r : K.Rel X Y}
    {d : K.Dist X} {e e' : K.Dist Y}
    (hrec : Recovers K r d e)
    (hle : K.dle e e') :
    Recovers K r d e' := by
  cases hrec with
  | intro a =>
      exact Exists.elim
        (K.weaken_strengthen a (K.dle_refl d) hle)
        (fun a' _ => Nonempty.intro a')

theorem compositional_recoverability
    (K : PrimitiveCalculus)
    {X Y Z : K.Ctx} {r : K.Rel X Y} {s : K.Rel Y Z}
    {d : K.Dist X} {e h : K.Dist Y} {z : K.Dist Z}
    (hF : Recovers K r d e)
    (hG : Recovers K s h z)
    (hmid : K.dle h e) :
    Recovers K (K.comp r s) d z := by
  cases hF with
  | intro a =>
      cases hG with
      | intro b =>
          exact Nonempty.intro (K.compose_wit a b hmid)

theorem non_erasure_monotonicity
    (K : PrimitiveCalculus)
    {X Y : K.Ctx} {r : K.Rel X Y}
    (Req Req' : K.Dist X -> Prop)
    (hsub : forall d, Req' d -> Req d)
    (hne : NonErasing K r Req) :
    NonErasing K r Req' := by
  intro d hreq'
  exact hne d (hsub d hreq')

/-- A candidate process-bundle is bookkeeping only; it is not a primitive self,
agent, valuer, or identity. -/
structure ProcessBundle (K : PrimitiveCalculus) where
  X : K.Ctx
  Y : K.Ctx
  required : K.Dist X -> Prop
  unfold : K.Rel X Y

/-- A joint presentation for a family of contexts indexed by `I`. -/
structure JointPresentation
    (K : PrimitiveCalculus) (I : Type u) (X : I -> K.Ctx) where
  J : K.Ctx
  emb : forall i, K.Rel (X i) J
  Y : K.Ctx
  unfold : K.Rel J Y

/-- Joint compatibility is n-ary and presentation-relative: every required
member distinction must be non-erased through its joint composite. -/
def Compatible
    (K : PrimitiveCalculus) {I : Type u} {X : I -> K.Ctx}
    (JP : JointPresentation K I X)
    (Req : forall i, K.Dist (X i) -> Prop) : Prop :=
  forall i, NonErasing K (K.comp (JP.emb i) JP.unfold) (Req i)

/-- An intentionally indiscrete tiny model. It is useful as a type-checking
smoke, not as a substantive empirical adapter. -/
def IndiscreteUnit : PrimitiveCalculus where
  Ctx := Unit
  Rel := fun _ _ => Unit
  id := fun _ => ()
  comp := fun _ _ => ()
  Dist := fun _ => Unit
  dle := fun _ _ => True
  dle_refl := fun _ => trivial
  dle_trans := fun _ _ => trivial
  Wit := fun _ _ _ => Unit
  wle := fun _ _ => True
  wle_refl := fun _ => trivial
  wle_trans := fun _ _ => trivial
  id_wit := fun _ => ()
  weaken_strengthen := fun _ _ _ => Exists.intro () trivial
  compose_wit := fun _ _ _ => ()
  compose_mono := fun _ _ _ _ => trivial

theorem indiscrete_unit_recovers :
    Recovers IndiscreteUnit (X := ()) (Y := ()) () () () := by
  exact Nonempty.intro ()

end PrimitiveWitness

end OmegaCore
