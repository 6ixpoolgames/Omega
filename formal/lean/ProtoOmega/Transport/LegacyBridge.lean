import OmegaCore.DistTrans
import ProtoOmega.Transport.Native

/-!
ProtoOmega.Transport.LegacyBridge

One-way bridge from Alpha-native transport presentations to the legacy checked
`OmegaCore.DistTrans` object. This is the only new transport file that imports
legacy `OmegaCore`.
-/

namespace ProtoOmega
namespace Transport

universe u v uA vA uB vB

/-- View a presentation-level Alpha distinction order as the legacy preorder
frame used by `OmegaCore.DistTrans`. -/
def DistOrder.toPreorderFrame
    {A : AlphaCore.Frame.{u, v}}
    (PA : DistOrder A) :
    OmegaCore.PreorderFrame A.Dist where
  le := PA.le
  le_refl := PA.le_refl
  le_trans := PA.le_trans

/-- View an Alpha-native transport as a legacy `OmegaCore.DistTransport`. -/
def NativeTransport.toLegacy
    {A : AlphaCore.Frame.{uA, vA}}
    {B : AlphaCore.Frame.{uB, vB}}
    {PA : DistOrder A} {PB : DistOrder B}
    (Phi : NativeTransport PA PB) :
    OmegaCore.DistTransport
      (DistOrder.toPreorderFrame PA)
      (DistOrder.toPreorderFrame PB) where
  rel := Phi.rel
  closed := Phi.closed

end Transport
end ProtoOmega
