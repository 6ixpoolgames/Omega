import OmegaProper.Trajectory.CarrierCertificate

/-!
OmegaProper.Trajectory.CarrierTrajectoryLanguage

Trajectory-language view of carrier certificates.

This file gives a small bridge away from spatial "support" language. A
candidate carrier also determines a path language: which endpoint pairs are
connected by internal paths through the carrier. A carrier certificate can then
be read as recurrence plus round-trip path-language membership plus merge
separation.

This does not define identity, agency, value, deformer structure, alignment, or
Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace CarrierTrajectoryLanguage

open CarrierCertificate
open CarriedDistinction
open ConsequenceRelation
open PathCarriedDistinction
open RecurrentViableClass
open SustainingViableClass

universe w k o

/-- The internal path language induced by a carrier candidate. -/
def CarrierPathLanguage
    {X : Type w}
    (Next : X -> X -> Prop)
    (C : CarrierCandidate X)
    (x y : X) : Prop :=
  InternalPath (dynFromNext Next) C x y

/-- Round-trip path-language membership between two endpoints. -/
def CarrierRoundTripLanguage
    {X : Type w}
    (Next : X -> X -> Prop)
    (C : CarrierCandidate X)
    (x y : X) : Prop :=
  CarrierPathLanguage Next C x y /\
    CarrierPathLanguage Next C y x

/-- A certificate gives round-trip path-language membership. -/
theorem certificate_roundTripLanguage
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y) :
    CarrierRoundTripLanguage Next C x y := by
  exact And.intro
    (certificate_forward_path hCert)
    (certificate_reverse_path hCert)

/-- A certificate gives forward path-language membership. -/
theorem certificate_forwardLanguage
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y) :
    CarrierPathLanguage Next C x y := by
  exact (certificate_roundTripLanguage hCert).left

/-- A certificate gives reverse path-language membership. -/
theorem certificate_reverseLanguage
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y) :
    CarrierPathLanguage Next C y x := by
  exact (certificate_roundTripLanguage hCert).right

/--
Round-trip language plus recurrence, endpoint membership, and merge separation
reconstructs a carrier certificate.

This says the certificate can be read in trajectory-language terms without
treating the carrier as an object.
-/
theorem certificate_of_roundTripLanguage
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hRec : RecurrentViableClass (dynFromNext Next) safe C)
    (hx : C x)
    (hy : C y)
    (hRound : CarrierRoundTripLanguage Next C x y)
    (hSep : ConsequenceMergeSeparated S x y) :
    CarrierCertificate S Next safe C x y := by
  exact And.intro
    hRec
    (And.intro
      hx
      (And.intro
        hy
        (And.intro
          hRound.left
          (And.intro
            hRound.right
            hSep))))

/-- The two-state cycle certificate has a round-trip carrier language. -/
theorem cycle_roundTripLanguage :
    CarrierRoundTripLanguage
      cycleNext
      cycleClass
      CycleState.left
      CycleState.right := by
  exact certificate_roundTripLanguage cycle_carrier_certificate

end CarrierTrajectoryLanguage
end Trajectory
end OmegaProper
