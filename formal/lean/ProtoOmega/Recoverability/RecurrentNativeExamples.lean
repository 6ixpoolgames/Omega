import ProtoOmega.Recoverability.NativeExamples
import ProtoOmega.Recoverability.RecurrentNative

/-!
ProtoOmega.Recoverability.RecurrentNativeExamples

Tiny examples for finite-chain native recoverability.
-/

namespace ProtoOmega
namespace Recoverability
namespace RecurrentNativeExamples

def tinyChain :
    NativeModel.Chain
      NativeExamples.tinyModel
      NativeExamples.UnitCtx.star
      NativeExamples.UnitCtx.star :=
  NativeModel.Chain.cons
    (NativeExamples.tinyModel.C.id NativeExamples.UnitCtx.star)
    NativeModel.Chain.nil

theorem tiny_chain_sound :
    NativeModel.Recovers
      NativeExamples.tinyModel
      (NativeModel.Chain.toHom tinyChain)
      AlphaCore.Examples.OneDist.d
      AlphaCore.Examples.OneDist.d := by
  exact NativeModel.recoverChain_sound
    NativeExamples.tinyModel
    (NativeModel.RecoverChain.step
      (NativeModel.identity_recoverability NativeExamples.tinyModel rfl)
      (NativeModel.RecoverChain.nil rfl))

theorem tiny_one_step_chain_exists :
    exists p : NativeModel.Chain
      NativeExamples.tinyModel
      NativeExamples.UnitCtx.star
      NativeExamples.UnitCtx.star,
      NativeModel.Recovers
        NativeExamples.tinyModel
        (NativeModel.Chain.toHom p)
        AlphaCore.Examples.OneDist.d
        AlphaCore.Examples.OneDist.d := by
  exact Exists.intro tinyChain tiny_chain_sound

end RecurrentNativeExamples
end Recoverability
end ProtoOmega
