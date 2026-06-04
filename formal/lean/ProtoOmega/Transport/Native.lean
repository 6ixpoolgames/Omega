import AlphaCore

/-!
ProtoOmega.Transport.Native

Alpha-native distinction transport presentation.

This is ProtoOmega, not primitive Alpha. It adds presentation-level distinction
order and transport relations over Alpha distinctions. It does not define
Omega, value, agency, life, viability, lushness, anti-value, identity, or
alignment.
-/

namespace ProtoOmega
namespace Transport

universe u v uA vA uB vB uC vC uD vD

/-- Presentation-level order over the distinctions of an Alpha frame.

Alpha provides distinctions as non-equivalence structure. `DistOrder` adds a
preorder/refinement structure over those distinctions for transport
presentations. -/
structure DistOrder (A : AlphaCore.Frame.{u, v}) where
  le : A.Dist -> A.Dist -> Prop
  le_refl : forall d, le d d
  le_trans : forall {a b c}, le a b -> le b c -> le a c

/-- Alpha-native distinction transport between ordered distinction
presentations. -/
structure NativeTransport
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    (PA : DistOrder A)
    (PB : DistOrder B) where
  rel : A.Dist -> B.Dist -> Prop
  closed :
    forall {d' d : A.Dist} {e e' : B.Dist},
      PA.le d' d ->
      rel d e ->
      PB.le e e' ->
      rel d' e'

namespace NativeTransport

/-- Transport inclusion. -/
def Subset
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {PA : DistOrder A} {PB : DistOrder B}
    (Phi Psi : NativeTransport PA PB) : Prop :=
  forall d e, Phi.rel d e -> Psi.rel d e

/-- Identity transport is presentation-level distinction order. -/
def id
    {A : AlphaCore.Frame.{uA, vA}}
    (PA : DistOrder A) : NativeTransport PA PA where
  rel := fun d e => PA.le d e
  closed := by
    intro d' d e e' hsrc h htar
    exact PA.le_trans hsrc (PA.le_trans h htar)

/-- Sequential transport composition: `compose Phi Psi` means `Psi` after
`Phi`. -/
def compose
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {C : AlphaCore.Frame.{uC, vC}}
    {PA : DistOrder A} {PB : DistOrder B} {PC : DistOrder C}
    (Phi : NativeTransport PA PB)
    (Psi : NativeTransport PB PC) :
    NativeTransport PA PC where
  rel := fun d f => exists e, Phi.rel d e /\ Psi.rel e f
  closed := by
    intro d' d f f' hsrc h htar
    cases h with
    | intro e he =>
        exact Exists.intro e
          (And.intro
            (Phi.closed hsrc he.left (PB.le_refl e))
            (Psi.closed (PB.le_refl e) he.right htar))

theorem id_closed
    {A : AlphaCore.Frame.{uA, vA}}
    (PA : DistOrder A)
    {d' d e e' : A.Dist}
    (hsrc : PA.le d' d)
    (h : (id PA).rel d e)
    (htar : PA.le e e') :
    (id PA).rel d' e' := by
  exact (id PA).closed hsrc h htar

theorem compose_closed
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {C : AlphaCore.Frame.{uC, vC}}
    {PA : DistOrder A} {PB : DistOrder B} {PC : DistOrder C}
    (Phi : NativeTransport PA PB)
    (Psi : NativeTransport PB PC)
    {d' d : A.Dist} {f f' : C.Dist}
    (hsrc : PA.le d' d)
    (h : (compose Phi Psi).rel d f)
    (htar : PC.le f f') :
    (compose Phi Psi).rel d' f' := by
  exact (compose Phi Psi).closed hsrc h htar

theorem left_id_iff
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {PA : DistOrder A} {PB : DistOrder B}
    (Phi : NativeTransport PA PB)
    (d : A.Dist) (e : B.Dist) :
    (compose (id PA) Phi).rel d e <-> Phi.rel d e := by
  constructor
  case mp =>
    intro h
    cases h with
    | intro d0 hd0 =>
        exact Phi.closed hd0.left hd0.right (PB.le_refl e)
  case mpr =>
    intro h
    exact Exists.intro d (And.intro (PA.le_refl d) h)

theorem right_id_iff
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {PA : DistOrder A} {PB : DistOrder B}
    (Phi : NativeTransport PA PB)
    (d : A.Dist) (e : B.Dist) :
    (compose Phi (id PB)).rel d e <-> Phi.rel d e := by
  constructor
  case mp =>
    intro h
    cases h with
    | intro e0 he0 =>
        exact Phi.closed (PA.le_refl d) he0.left he0.right
  case mpr =>
    intro h
    exact Exists.intro e (And.intro h (PB.le_refl e))

theorem assoc_iff
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {C : AlphaCore.Frame.{uC, vC}}
    {D : AlphaCore.Frame.{uD, vD}}
    {PA : DistOrder A} {PB : DistOrder B}
    {PC : DistOrder C} {PD : DistOrder D}
    (Phi : NativeTransport PA PB)
    (Psi : NativeTransport PB PC)
    (Chi : NativeTransport PC PD)
    (d : A.Dist) (g : D.Dist) :
    (compose (compose Phi Psi) Chi).rel d g <->
      (compose Phi (compose Psi Chi)).rel d g := by
  constructor
  case mp =>
    intro h
    cases h with
    | intro f hf =>
        cases hf.left with
        | intro e he =>
            exact Exists.intro e
              (And.intro he.left (Exists.intro f (And.intro he.right hf.right)))
  case mpr =>
    intro h
    cases h with
    | intro e he =>
        cases he.right with
        | intro f hf =>
            exact Exists.intro f
              (And.intro (Exists.intro e (And.intro he.left hf.left)) hf.right)

theorem compose_subset_of_rel
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {C : AlphaCore.Frame.{uC, vC}}
    {PA : DistOrder A} {PB : DistOrder B} {PC : DistOrder C}
    {Phi : NativeTransport PA PB}
    {Psi : NativeTransport PB PC}
    {Xi : NativeTransport PA PC}
    (hsub : Subset (compose Phi Psi) Xi)
    {d : A.Dist} {e : B.Dist} {f : C.Dist}
    (hPhi : Phi.rel d e)
    (hPsi : Psi.rel e f) :
    Xi.rel d f := by
  exact hsub d f (Exists.intro e (And.intro hPhi hPsi))

end NativeTransport

end Transport
end ProtoOmega
