import ProtoOmega.Recoverability.Native
import ProtoOmega.Transport.NativeExamples

/-!
ProtoOmega.Recoverability.NativeExamples

Tiny examples for Alpha-native recoverability.
-/

namespace ProtoOmega
namespace Recoverability
namespace NativeExamples

inductive UnitCtx
  | star
  deriving DecidableEq

def unitCategory : ContextCategory where
  Ctx := UnitCtx
  Hom := fun _ _ => Unit
  id := fun _ => ()
  comp := fun _ _ => ()
  id_left := by
    intro _ _ _
    rfl
  id_right := by
    intro _ _ _
    rfl
  assoc := by
    intro _ _ _ _ _ _ _
    rfl

def tinyModel : NativeModel where
  C := unitCategory
  frame := fun _ => AlphaCore.Examples.chainFrame
  order := fun _ =>
    Transport.NativeExamples.discreteOrder AlphaCore.Examples.chainFrame
  A := fun _ =>
    Transport.NativeTransport.id
      (Transport.NativeExamples.discreteOrder AlphaCore.Examples.chainFrame)
  id_normal := by
    intro _ source target
    exact Iff.rfl
  lax_comp := by
    intro _ _ _ _ _ source target h
    exact (Transport.NativeTransport.left_id_iff
      (Transport.NativeTransport.id
        (Transport.NativeExamples.discreteOrder AlphaCore.Examples.chainFrame))
      source target).mp h

theorem tiny_model_identity_recovers :
    exists M : NativeModel.{0, 0, 0, 0}, exists X : M.C.Ctx,
      exists d : (M.frame X).Dist,
        NativeModel.Recovers M (M.C.id X) d d := by
  exact Exists.intro tinyModel
    (Exists.intro UnitCtx.star
      (Exists.intro AlphaCore.Examples.OneDist.d
        (NativeModel.identity_recoverability tinyModel rfl)))

theorem tiny_model_non_erasing_trivial_req :
    exists M : NativeModel.{0, 0, 0, 0}, exists X : M.C.Ctx,
      NativeModel.NonErasing M (M.C.id X) (fun _ => True) := by
  exact Exists.intro tinyModel
    (Exists.intro UnitCtx.star
      (by
        intro source _
        exact Exists.intro source
          (NativeModel.identity_recoverability tinyModel rfl)))

theorem tiny_model_compositional_recoverability :
    exists M : NativeModel.{0, 0, 0, 0}, exists X : M.C.Ctx,
      exists d : (M.frame X).Dist,
        NativeModel.Recovers M
          (M.C.comp (M.C.id X) (M.C.id X)) d d := by
  exact Exists.intro tinyModel
    (Exists.intro UnitCtx.star
      (Exists.intro AlphaCore.Examples.OneDist.d
        (NativeModel.compositional_recoverability tinyModel
          (NativeModel.identity_recoverability tinyModel rfl)
          (NativeModel.identity_recoverability tinyModel rfl))))

end NativeExamples
end Recoverability
end ProtoOmega
