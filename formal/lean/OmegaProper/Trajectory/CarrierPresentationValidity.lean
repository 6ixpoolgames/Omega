import OmegaProper.Trajectory.CarrierCertificate
import OmegaProper.Trajectory.PresentationInvariant
import OmegaProper.Trajectory.SafePresentationContract

/-!
OmegaProper.Trajectory.CarrierPresentationValidity

Carrier certificates and sound presentations.

This file connects the carrier-certificate repair back to the sound quotient /
presentation discipline. A certified carrier keeps a merge-separated pair
visible. Therefore a sound presentation cannot erase the certified endpoints.

This is not boundary realism, identity, agency, value, alignment, or Omega
proper.
-/

namespace OmegaProper
namespace Trajectory
namespace CarrierPresentationValidity

open CarrierCertificate
open ConsequenceRelation
open PresentationInvariant
open ReachabilityViability

universe w k o q v

/-- A presentation keeps a pair visible when it does not erase the pair. -/
def PairVisibleUnderPresentation
    {X : Type w}
    {Q : Type q}
    (present : X -> Q)
    (x y : X) : Prop :=
  Not (PairErasedByPresentation present x y)

/--
A certified carrier pair is invariant under all sound quotients of the
consequence system.
-/
theorem certificate_pair_invariant_under_soundQuotients
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y) :
    PairInvariantUnderSoundQuotients S x y := by
  exact mergeSeparated_invariantUnderSoundQuotients
    (certificate_mergeSeparated hCert)

/--
Any sound presentation keeps certified carrier endpoints visible.
-/
theorem soundPresentation_keeps_certified_pair_visible
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {Q : Type q}
    {present : S.Fragment -> Q}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y)
    (hSound : SoundQuotient.SoundQuotient S present) :
    PairVisibleUnderPresentation present x y := by
  exact (certificate_pair_invariant_under_soundQuotients hCert)
    present
    hSound

/--
If a presentation erases certified carrier endpoints, it is not sound.
-/
theorem erases_certified_pair_not_sound
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {Q : Type q}
    {present : S.Fragment -> Q}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y)
    (hErases : PairErasedByPresentation present x y) :
    Not (SoundQuotient.SoundQuotient S present) := by
  exact invariantPair_erasingPresentation_not_sound
    (certificate_pair_invariant_under_soundQuotients hCert)
    hErases

/--
Reachability-safe presentations also keep certified carrier endpoints visible.
The proof uses only the consequence-sound field of the packaged contract.
-/
theorem reachabilitySafePresentation_keeps_certified_pair_visible
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S NextX safe C x y)
    (hContract :
      SafePresentationContract.ReachabilitySafePresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ) :
    PairVisibleUnderPresentation present x y := by
  exact soundPresentation_keeps_certified_pair_visible
    hCert
    hContract.consequence_sound

/--
Viability-safe presentations also keep certified carrier endpoints visible.
The proof uses only the consequence-sound field of the packaged contract.
-/
theorem viabilitySafePresentation_keeps_certified_pair_visible
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S NextX safe C x y)
    (hContract :
      SafePresentationContract.ViabilitySafePresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ) :
    PairVisibleUnderPresentation present x y := by
  exact soundPresentation_keeps_certified_pair_visible
    hCert
    hContract.consequence_sound

end CarrierPresentationValidity
end Trajectory
end OmegaProper
