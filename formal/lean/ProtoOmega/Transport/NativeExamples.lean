import ProtoOmega.Transport.LegacyBridge

/-!
ProtoOmega.Transport.NativeExamples

Tiny examples for the Alpha-native transport presentation.
-/

namespace ProtoOmega
namespace Transport
namespace NativeExamples

universe u v

/-- Discrete presentation order over Alpha distinctions. -/
def discreteOrder (A : AlphaCore.Frame.{u, v}) : DistOrder A where
  le := fun d e => d = e
  le_refl := by
    intro d
    rfl
  le_trans := by
    intro _ _ _ hab hbc
    exact Eq.trans hab hbc

/-- Indiscrete presentation order over Alpha distinctions. -/
def indiscreteOrder (A : AlphaCore.Frame.{u, v}) : DistOrder A where
  le := fun _ _ => True
  le_refl := by
    intro _
    trivial
  le_trans := by
    intro _ _ _ _ _
    trivial

def P : DistOrder AlphaCore.Examples.chainFrame :=
  discreteOrder AlphaCore.Examples.chainFrame

theorem native_identity_exists :
    exists _Phi : NativeTransport P P, True := by
  exact Exists.intro (NativeTransport.id P) True.intro

theorem native_to_legacy_exists :
    exists _PhiLegacy : OmegaCore.DistTransport
      (DistOrder.toPreorderFrame P)
      (DistOrder.toPreorderFrame P),
      True := by
  exact Exists.intro (NativeTransport.toLegacy (NativeTransport.id P)) True.intro

/-- A closed transport over the indiscrete order. -/
def indiscreteTransport
    (A : AlphaCore.Frame.{u, v})
    (PA : DistOrder A := indiscreteOrder A) :
    NativeTransport PA PA where
  rel := fun _ _ => True
  closed := by
    intro _ _ _ _ _ _ _
    trivial

theorem nontrivial_closed_transport_exists :
    exists Phi : NativeTransport
      (indiscreteOrder AlphaCore.Examples.chainFrame)
      (indiscreteOrder AlphaCore.Examples.chainFrame),
      forall source target, Phi.rel source target := by
  exact Exists.intro
    (indiscreteTransport AlphaCore.Examples.chainFrame)
    (by
      intro source target
      trivial)

end NativeExamples
end Transport
end ProtoOmega
