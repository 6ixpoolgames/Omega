import AlphaCore

/-!
ProtoOmega.Presentation.Native

Presentation-native distinction structures.

These structures separate distinction/transport presentations from full Alpha
substrates. A presentation can expose distinctions, separations, orders, and
transport laws without claiming that the relation/asymmetry parts of an
`AlphaCore.Frame` have been instantiated by the substrate.
-/

namespace ProtoOmega
namespace Presentation

universe u v w

/-- A distinction presentation without substrate relation/asymmetry. -/
structure DistPresentation where
  Dist : Type u

/-- A distinction presentation with a carrier and separation predicate, but no
primitive relation or asymmetry. -/
structure SepPresentation where
  X : Type u
  Dist : Type v
  Sep : Dist -> X -> X -> Prop
  sep_irrefl : forall d x, Not (Sep d x x)
  sep_symm : forall d x y, Sep d x y -> Sep d y x

/-- Forget carrier/separation data and keep only the distinction presentation. -/
def SepPresentation.toDistPresentation
    (P : SepPresentation.{u, v}) : DistPresentation.{v} where
  Dist := P.Dist

/-- Presentation-level order over distinctions. -/
structure DistOrder (P : DistPresentation.{u}) where
  le : P.Dist -> P.Dist -> Prop
  le_refl : forall d, le d d
  le_trans : forall {a b c}, le a b -> le b c -> le a c

/-- Presentation-level transport relation closed under source weakening and
target strengthening. -/
structure Transport
    {P : DistPresentation.{u}}
    {Q : DistPresentation.{v}}
    (PP : DistOrder P)
    (QQ : DistOrder Q) where
  rel : P.Dist -> Q.Dist -> Prop
  closed :
    forall {d' d : P.Dist} {e e' : Q.Dist},
      PP.le d' d ->
      rel d e ->
      QQ.le e e' ->
      rel d' e'

namespace Transport

/-- Transport inclusion. -/
def Subset
    {P : DistPresentation.{u}}
    {Q : DistPresentation.{v}}
    {PP : DistOrder P} {QQ : DistOrder Q}
    (Phi Psi : Transport PP QQ) : Prop :=
  forall d e, Phi.rel d e -> Psi.rel d e

/-- Identity transport is presentation-level distinction order. -/
def id
    {P : DistPresentation.{u}}
    (PP : DistOrder P) : Transport PP PP where
  rel := fun d e => PP.le d e
  closed := by
    intro d' d e e' hsrc h htar
    exact PP.le_trans hsrc (PP.le_trans h htar)

/-- Sequential transport composition: `compose Phi Psi` means `Psi` after
`Phi`. -/
def compose
    {P : DistPresentation.{u}}
    {Q : DistPresentation.{v}}
    {R : DistPresentation.{w}}
    {PP : DistOrder P} {QQ : DistOrder Q} {RR : DistOrder R}
    (Phi : Transport PP QQ)
    (Psi : Transport QQ RR) :
    Transport PP RR where
  rel := fun d f => exists e, Phi.rel d e /\ Psi.rel e f
  closed := by
    intro d' d f f' hsrc h htar
    cases h with
    | intro e he =>
        exact Exists.intro e
          (And.intro
            (Phi.closed hsrc he.left (QQ.le_refl e))
            (Psi.closed (QQ.le_refl e) he.right htar))

theorem compose_subset_of_rel
    {P : DistPresentation.{u}}
    {Q : DistPresentation.{v}}
    {R : DistPresentation.{w}}
    {PP : DistOrder P} {QQ : DistOrder Q} {RR : DistOrder R}
    {Phi : Transport PP QQ}
    {Psi : Transport QQ RR}
    {Xi : Transport PP RR}
    (hsub : Subset (compose Phi Psi) Xi)
    {d : P.Dist} {e : Q.Dist} {f : R.Dist}
    (hPhi : Phi.rel d e)
    (hPsi : Psi.rel e f) :
    Xi.rel d f := by
  exact hsub d f (Exists.intro e (And.intro hPhi hPsi))

end Transport

end Presentation
end ProtoOmega

namespace AlphaCore
namespace Frame

/-- Forget relation/asymmetry and expose an Alpha frame as a separation
presentation. -/
def toSepPresentation
    (A : AlphaCore.Frame.{u, v}) :
    ProtoOmega.Presentation.SepPresentation.{u, v} where
  X := A.X
  Dist := A.Dist
  Sep := A.Sep
  sep_irrefl := A.sep_irrefl
  sep_symm := A.sep_symm

/-- Forget relation/asymmetry/carrier data and expose only the distinction type
of an Alpha frame. -/
def toDistPresentation
    (A : AlphaCore.Frame.{u, v}) :
    ProtoOmega.Presentation.DistPresentation.{v} where
  Dist := A.Dist

end Frame
end AlphaCore
