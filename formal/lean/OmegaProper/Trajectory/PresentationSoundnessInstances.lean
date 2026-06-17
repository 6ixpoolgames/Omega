import AlphaCore.PrimitiveSoundPresentation
import OmegaProper.Trajectory.CarrierPresentationValidity
import OmegaProper.Trajectory.PresentationSoundness
import OmegaProper.Trajectory.TargetPresentationInvariant

/-!
OmegaProper.Trajectory.PresentationSoundnessInstances

Compression bridges showing that existing presentation-soundness notions are
instances of generic forbidden-merge avoidance.
-/

namespace OmegaProper
namespace Trajectory
namespace PresentationSoundnessInstances

open CarrierCertificate
open CarrierPresentationValidity
open ConsequenceRelation
open PresentationSoundness
open TargetPresentationInvariant

universe u v w k o q t

theorem primitiveSoundPresentation_iff_soundPresentationBy_primitiveApart
    (A : AlphaCore.Frame.{u, v})
    {Q : Type q}
    (present : A.X -> Q) :
    AlphaCore.Frame.PrimitiveSoundPresentation A present <->
      SoundPresentationBy (AlphaCore.Frame.PrimitiveApart A) present := by
  rfl

theorem primitiveApart_forbiddenPreserving_of_primitiveMap
    {A : AlphaCore.Frame.{u, v}}
    {B : AlphaCore.Frame.{w, k}}
    (f : AlphaCore.Frame.PrimitiveMap A B) :
    ForbiddenPreservingMap
      (AlphaCore.Frame.PrimitiveApart A)
      (AlphaCore.Frame.PrimitiveApart B)
      f.mapX := by
  intro x y hApart
  exact AlphaCore.Frame.primitiveMap_preserves_primitiveApart f hApart

theorem primitiveMap_pullback_soundPresentation_generic
    {A : AlphaCore.Frame.{u, v}}
    {B : AlphaCore.Frame.{w, k}}
    (f : AlphaCore.Frame.PrimitiveMap A B)
    {Q : Type q}
    {present : B.X -> Q}
    (hSound : AlphaCore.Frame.PrimitiveSoundPresentation B present) :
    AlphaCore.Frame.PrimitiveSoundPresentation
      A
      (fun x => present (f.mapX x)) := by
  exact pullback_soundPresentationBy
    (primitiveApart_forbiddenPreserving_of_primitiveMap f)
    hSound

theorem soundQuotient_implies_soundPresentationBy_mergeSeparated
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {present : S.Fragment -> Q}
    (hSound : SoundQuotient.SoundQuotient S present) :
    SoundPresentationBy (ConsequenceMergeSeparated S) present := by
  intro x y hEq hForbidden
  exact SoundQuotient.soundQuotient_blocks_mergeSeparated_kernel
    hSound
    hForbidden
    hEq

theorem soundPresentationBy_mergeSeparated_implies_soundQuotient
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {present : S.Fragment -> Q}
    (hSound : SoundPresentationBy (ConsequenceMergeSeparated S) present) :
    SoundQuotient.SoundQuotient S present := by
  intro x y hEq
  have hNoMerge : Not (ConsequenceMergeSeparated S x y) :=
    hSound x y hEq
  have hNoSepXY : Not (ConsequenceSeparated S x y) := by
    intro hSep
    exact hNoMerge (Or.inl hSep)
  have hNoSepYX : Not (ConsequenceSeparated S y x) := by
    intro hSep
    exact hNoMerge (Or.inr hSep)
  exact And.intro
    (not_separated_implies_compatible hNoSepXY)
    (not_separated_implies_compatible hNoSepYX)

theorem soundQuotient_iff_soundPresentationBy_mergeSeparated
    (S : ConsequenceSystem.{w, k, o})
    {Q : Type q}
    (present : S.Fragment -> Q) :
    SoundQuotient.SoundQuotient S present <->
      SoundPresentationBy (ConsequenceMergeSeparated S) present := by
  constructor
  case mp =>
    exact soundQuotient_implies_soundPresentationBy_mergeSeparated
  case mpr =>
    exact soundPresentationBy_mergeSeparated_implies_soundQuotient

theorem targetRespectsPresentation_iff_soundPresentationBy_targetSeparated
    {X : Type w}
    {Q : Type q}
    {T : Type t}
    (target : X -> T)
    (present : X -> Q) :
    TargetRespectsPresentation target present <->
      SoundPresentationBy (TargetSeparatedBy target) present := by
  constructor
  case mp =>
    intro hRespect x y hEq hForbidden
    exact hForbidden (hRespect x y hEq)
  case mpr =>
    intro hSound x y hEq
    classical
    by_cases hTarget : target x = target y
    case pos =>
      exact hTarget
    case neg =>
      exact False.elim (hSound x y hEq hTarget)

theorem targetObstructedByPresentation_iff_forbidden_kernel
    {X : Type w}
    {Q : Type q}
    {T : Type t}
    (target : X -> T)
    (present : X -> Q) :
    TargetObstructedByPresentation target present <->
      exists x y,
        PairErased present x y /\
          TargetSeparatedBy target x y := by
  rfl

theorem carrierCertificate_forbiddenBy_mergeSeparated
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y) :
    ConsequenceMergeSeparated S x y := by
  exact CarrierCertificate.certificate_mergeSeparated hCert

theorem soundPresentationBy_keeps_certified_pair_visible
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {Q : Type q}
    {present : S.Fragment -> Q}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y)
    (hSound : SoundPresentationBy (ConsequenceMergeSeparated S) present) :
    PairVisibleUnderPresentation present x y := by
  exact forbiddenPair_visible_under_soundPresentationBy
    hSound
    (carrierCertificate_forbiddenBy_mergeSeparated hCert)

end PresentationSoundnessInstances
end Trajectory
end OmegaProper
