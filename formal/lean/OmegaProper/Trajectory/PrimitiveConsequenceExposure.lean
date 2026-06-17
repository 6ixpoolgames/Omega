import AlphaCore.PrimitiveSoundPresentation
import OmegaProper.Trajectory.AlphaConsequenceSeed
import OmegaProper.Trajectory.ProtoTeleologicalSeed
import OmegaProper.Trajectory.SoundQuotient

/-!
OmegaProper.Trajectory.PrimitiveConsequenceExposure

Bridge from Alpha-native primitive apartness to evaluated consequence.

This file does not claim that Alpha derives consequence systems. It defines the
adapter contract under which primitive apartness is exposed as merge-blocking
consequence separation.
-/

namespace OmegaProper
namespace Trajectory
namespace PrimitiveConsequenceExposure

open AlphaConsequenceSeed
open ConsequenceRelation
open ProtoTeleologicalSeed

universe u v k o q

/--
The consequence apparatus exposes primitive apartness when every primitively
apart pair is merge-separated by evaluated consequence.
-/
def ConsequenceExposesPrimitiveApartness
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A) : Prop :=
  forall x y : A.X,
    AlphaCore.Frame.PrimitiveApart A x y ->
      ConsequenceMergeSeparated S.toConsequenceSystem x y

theorem exposure_mergeSeparates_primitiveApart
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    {x y : A.X}
    (hApart : AlphaCore.Frame.PrimitiveApart A x y) :
    ConsequenceMergeSeparated S.toConsequenceSystem x y := by
  exact hExpose x y hApart

theorem exposure_blocks_identification_of_primitiveApart
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    {x y : A.X}
    (hApart : AlphaCore.Frame.PrimitiveApart A x y) :
    Not (ConsequenceIdentifiable S.toConsequenceSystem x y) := by
  exact mergeSeparated_blocks_identifiable
    (exposure_mergeSeparates_primitiveApart hExpose hApart)

theorem exposure_jointWitness_consequenceBearing
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    (w : AlphaCore.Frame.JointPrimitiveWitness A) :
    ConsequenceBearingJointWitness S w := by
  exact hExpose w.x w.y
    (AlphaCore.Frame.jointWitness_implies_primitiveApart w)

theorem exposure_asymmetryWitness_consequenceBearing
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    (w : AlphaCore.Frame.AsymmetryPrimitiveWitness A) :
    ConsequenceBearingAlphaWitness S w := by
  exact exposure_jointWitness_consequenceBearing hExpose w.toJoint

theorem exposure_jointWitness_protoSeed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    (w : AlphaCore.Frame.JointPrimitiveWitness A) :
    JointProtoTeleologicalSeed S := by
  exact Exists.intro w (exposure_jointWitness_consequenceBearing hExpose w)

theorem exposure_asymmetryWitness_protoSeed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    (w : AlphaCore.Frame.AsymmetryPrimitiveWitness A) :
    AsymmetryProtoTeleologicalSeed S := by
  exact Exists.intro w (exposure_asymmetryWitness_consequenceBearing hExpose w)

/--
Primitive nondegeneracy yields a proto seed only once primitive apartness is
exposed by evaluated consequence.
-/
theorem primitiveNondegenerate_exposed_protoSeed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    (hPrim : AlphaCore.Frame.PrimitiveNondegenerate A) :
    ProtoTeleologicalSeed S := by
  match hPrim with
  | Nonempty.intro w =>
      exact exposure_asymmetryWitness_protoSeed hExpose w

/--
Under exposure, any consequence-sound presentation is primitive-sound.

This is the formal bridge between consequence-sound quotient discipline and
the new Alpha-native primitive-sound presentation discipline.
-/
theorem consequenceSound_implies_primitiveSound_underExposure
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    {Q : Type q}
    {present : A.X -> Q}
    (hSound : SoundQuotient.SoundQuotient S.toConsequenceSystem present) :
    AlphaCore.Frame.PrimitiveSoundPresentation A present := by
  intro x y hEq hApart
  have hMerge :
      ConsequenceMergeSeparated S.toConsequenceSystem x y :=
    hExpose x y hApart
  exact SoundQuotient.soundQuotient_blocks_mergeSeparated_kernel
    hSound
    hMerge
    hEq

theorem exposedPrimitiveApart_erasingPresentation_not_consequenceSound
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (hExpose : ConsequenceExposesPrimitiveApartness S)
    {Q : Type q}
    {present : A.X -> Q}
    {x y : A.X}
    (hApart : AlphaCore.Frame.PrimitiveApart A x y)
    (hErased : present x = present y) :
    Not (SoundQuotient.SoundQuotient S.toConsequenceSystem present) := by
  intro hSound
  exact SoundQuotient.soundQuotient_blocks_mergeSeparated_kernel
    hSound
    (hExpose x y hApart)
    hErased

end PrimitiveConsequenceExposure
end Trajectory
end OmegaProper
