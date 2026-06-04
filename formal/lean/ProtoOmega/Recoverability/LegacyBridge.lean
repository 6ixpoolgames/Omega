import OmegaCore.NormalLax
import ProtoOmega.Recoverability.Native
import ProtoOmega.Transport.LegacyBridge

/-!
ProtoOmega.Recoverability.LegacyBridge

One-way bridge from Alpha-native recoverability models to the legacy checked
`OmegaCore.NormalLaxDistinctionTransport` shape.
-/

namespace ProtoOmega
namespace Recoverability

universe u v x y

/-- View a native context category as the legacy context-category shape. -/
def ContextCategory.toLegacy
    (C : ContextCategory.{u, v}) :
    OmegaCore.ContextCategory.{u, v} where
  Ctx := C.Ctx
  Rel := C.Hom
  id := C.id
  comp := C.comp
  id_left := C.id_left
  id_right := C.id_right
  assoc := C.assoc

/-- View a native recoverability model as a legacy normal-lax distinction
transport model. -/
def NativeModel.toLegacy
    (M : NativeModel.{u, v, x, y}) :
    OmegaCore.NormalLaxDistinctionTransport.{u, v, y} where
  C := ContextCategory.toLegacy M.C
  Dist := fun X => (M.frame X).Dist
  frame := fun X => Transport.DistOrder.toPreorderFrame (M.order X)
  A := fun f => Transport.NativeTransport.toLegacy (M.A f)
  id_normal := M.id_normal
  lax_comp := M.lax_comp

end Recoverability
end ProtoOmega
