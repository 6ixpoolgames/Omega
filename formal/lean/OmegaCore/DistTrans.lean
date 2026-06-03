/-!
OmegaCore.DistTrans

Support-level distinction transports for the Omega Primitive Calculus v0.

This module formalizes the Lean-native root skeleton:

* objects are preorder frames;
* morphisms are source-weakening / target-strengthening closed relations;
* identity is refinement;
* composition is ordinary relational composition.

The category laws are stated as relation-level iff theorems. This avoids
claiming definitional equality of transport structures where extensional
equality is the intended mathematical notion.
-/

namespace OmegaCore

universe u v w x

/-- A minimal preorder frame. -/
structure PreorderFrame (P : Type u) where
  le : P -> P -> Prop
  le_refl : forall p, le p p
  le_trans : forall {a b c}, le a b -> le b c -> le a c

/-- A distinction transport is a relation closed under source weakening and
target strengthening. Equivalently, it is a support-level profunctor
`P^op x Q -> Prop`. -/
structure DistTransport
    {P : Type u} {Q : Type v}
    (PF : PreorderFrame P) (QF : PreorderFrame Q) where
  rel : P -> Q -> Prop
  closed :
    forall {p' p : P} {q q' : Q},
      PF.le p' p -> rel p q -> QF.le q q' -> rel p' q'

namespace DistTransport

/-- Transport inclusion. -/
def Subset
    {P : Type u} {Q : Type v}
    {PF : PreorderFrame P} {QF : PreorderFrame Q}
    (Phi Psi : DistTransport PF QF) : Prop :=
  forall p q, Phi.rel p q -> Psi.rel p q

/-- Identity transport is refinement. -/
def id
    {P : Type u} (PF : PreorderFrame P) : DistTransport PF PF where
  rel := fun p q => PF.le p q
  closed := by
    intro p' p q q' hp h hq
    exact PF.le_trans hp (PF.le_trans h hq)

/-- Sequential transport composition: `compose Phi Psi` means `Psi` after
`Phi`. -/
def compose
    {P : Type u} {Q : Type v} {R : Type w}
    {PF : PreorderFrame P} {QF : PreorderFrame Q} {RF : PreorderFrame R}
    (Phi : DistTransport PF QF)
    (Psi : DistTransport QF RF) : DistTransport PF RF where
  rel := fun p r => exists q, Phi.rel p q /\ Psi.rel q r
  closed := by
    intro p' p r r' hp h hr
    cases h with
    | intro q hq =>
        exact Exists.intro q
          (And.intro
            (Phi.closed hp hq.left (QF.le_refl q))
            (Psi.closed (QF.le_refl q) hq.right hr))

theorem id_closed
    {P : Type u} (PF : PreorderFrame P)
    {p' p q q' : P}
    (hp : PF.le p' p)
    (h : (id PF).rel p q)
    (hq : PF.le q q') :
    (id PF).rel p' q' := by
  exact (id PF).closed hp h hq

theorem compose_closed
    {P : Type u} {Q : Type v} {R : Type w}
    {PF : PreorderFrame P} {QF : PreorderFrame Q} {RF : PreorderFrame R}
    (Phi : DistTransport PF QF)
    (Psi : DistTransport QF RF)
    {p' p : P} {r r' : R}
    (hp : PF.le p' p)
    (h : (compose Phi Psi).rel p r)
    (hr : RF.le r r') :
    (compose Phi Psi).rel p' r' := by
  exact (compose Phi Psi).closed hp h hr

theorem left_id_iff
    {P : Type u} {Q : Type v}
    {PF : PreorderFrame P} {QF : PreorderFrame Q}
    (Phi : DistTransport PF QF)
    (p : P) (q : Q) :
    (compose (id PF) Phi).rel p q <-> Phi.rel p q := by
  constructor
  case mp =>
    intro h
    cases h with
    | intro p0 hp0 =>
        exact Phi.closed hp0.left hp0.right (QF.le_refl q)
  case mpr =>
    intro h
    exact Exists.intro p (And.intro (PF.le_refl p) h)

theorem right_id_iff
    {P : Type u} {Q : Type v}
    {PF : PreorderFrame P} {QF : PreorderFrame Q}
    (Phi : DistTransport PF QF)
    (p : P) (q : Q) :
    (compose Phi (id QF)).rel p q <-> Phi.rel p q := by
  constructor
  case mp =>
    intro h
    cases h with
    | intro q0 hq0 =>
        exact Phi.closed (PF.le_refl p) hq0.left hq0.right
  case mpr =>
    intro h
    exact Exists.intro q (And.intro h (QF.le_refl q))

theorem assoc_iff
    {P : Type u} {Q : Type v} {R : Type w} {S : Type x}
    {PF : PreorderFrame P} {QF : PreorderFrame Q}
    {RF : PreorderFrame R} {SF : PreorderFrame S}
    (Phi : DistTransport PF QF)
    (Psi : DistTransport QF RF)
    (Chi : DistTransport RF SF)
    (p : P) (s : S) :
    (compose (compose Phi Psi) Chi).rel p s <->
      (compose Phi (compose Psi Chi)).rel p s := by
  constructor
  case mp =>
    intro h
    cases h with
    | intro r hr =>
        cases hr.left with
        | intro q hq =>
            exact Exists.intro q
              (And.intro hq.left (Exists.intro r (And.intro hq.right hr.right)))
  case mpr =>
    intro h
    cases h with
    | intro q hq =>
        cases hq.right with
        | intro r hr =>
            exact Exists.intro r
              (And.intro (Exists.intro q (And.intro hq.left hr.left)) hr.right)

theorem compose_subset_of_rel
    {P : Type u} {Q : Type v} {R : Type w}
    {PF : PreorderFrame P} {QF : PreorderFrame Q} {RF : PreorderFrame R}
    {Phi : DistTransport PF QF}
    {Psi : DistTransport QF RF}
    {Xi : DistTransport PF RF}
    (hsub : Subset (compose Phi Psi) Xi)
    {p : P} {q : Q} {r : R}
    (hPhi : Phi.rel p q)
    (hPsi : Psi.rel q r) :
    Xi.rel p r := by
  exact hsub p r (Exists.intro q (And.intro hPhi hPsi))

end DistTransport

end OmegaCore
