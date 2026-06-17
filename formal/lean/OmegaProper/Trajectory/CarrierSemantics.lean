import OmegaProper.Trajectory.CarrierTrajectoryLanguage
import OmegaProper.Trajectory.GeneratedCarrier

/-!
OmegaProper.Trajectory.CarrierSemantics

Compression layer for carrier/support presentations.

Raw support predicates, generated mutual-reach carriers, and trajectory-language
views all denote a carrier semantics: a candidate carrier plus the internal
paths it admits. Certification remains a checked property of that semantics,
not a claim that the carrier is an object or identity.
-/

namespace OmegaProper
namespace Trajectory
namespace CarrierSemantics

open CarrierCertificate
open CarrierTrajectoryLanguage
open CarriedDistinction
open ConsequenceRelation
open GeneratedCarrier
open PathCarriedDistinction
open RecurrentViableClass
open SustainingViableClass

universe w k o

/-- Carrier semantics: a carrier predicate plus its admitted path relation. -/
structure CarrierSemantics (X : Type w) where
  carrier : X -> Prop
  path : X -> X -> Prop

namespace CarrierSemantics

/--
The semantics induced by a raw carrier candidate and adapter dynamics.

This is the canonical denotation of support predicates in the current finite
stack.
-/
def ofCandidate
    {X : Type w}
    (Next : X -> X -> Prop)
    (C : X -> Prop) :
    CarrierSemantics X where
  carrier := C
  path := CarrierPathLanguage Next C

/-- The generated mutual-reach carrier as carrier semantics. -/
def ofGeneratedMutualReach
    {X : Type w}
    (Next : X -> X -> Prop)
    (Ambient : X -> Prop)
    (x y : X) :
    CarrierSemantics X :=
  ofCandidate Next (MutualReachCarrier Next Ambient x y)

end CarrierSemantics

/-- Both endpoints lie in the carrier semantics. -/
def PairInCarrier
    {X : Type w}
    (K : CarrierSemantics X)
    (x y : X) : Prop :=
  K.carrier x /\ K.carrier y

/-- Round-trip path membership in the carrier semantics. -/
def RoundTrip
    {X : Type w}
    (K : CarrierSemantics X)
    (x y : X) : Prop :=
  K.path x y /\ K.path y x

/-- The carrier semantics path relation agrees with internal paths. -/
def PathMatchesDynamics
    {X : Type w}
    (K : CarrierSemantics X)
    (Next : X -> X -> Prop) : Prop :=
  forall x y,
    K.path x y <->
      InternalPath (dynFromNext Next) K.carrier x y

/-- The carrier semantics is recurrent viable under the supplied dynamics/safety. -/
def RecurrentCarrierSemantics
    {X : Type w}
    (K : CarrierSemantics X)
    (Next : X -> X -> Prop)
    (safe : X -> Prop) : Prop :=
  RecurrentViableClass (dynFromNext Next) safe K.carrier

/--
Semantic carrier certificate.

This is the compressed form: recurrence, endpoint membership, round-trip path
language, and merge separation.
-/
def CarrierSemanticCertificate
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (safe : S.Fragment -> Prop)
    (K : CarrierSemantics S.Fragment)
    (x y : S.Fragment) : Prop :=
  RecurrentCarrierSemantics K Next safe /\
    PairInCarrier K x y /\
    RoundTrip K x y /\
    ConsequenceMergeSeparated S x y

theorem ofCandidate_pathMatchesDynamics
    {X : Type w}
    (Next : X -> X -> Prop)
    (C : X -> Prop) :
    PathMatchesDynamics (CarrierSemantics.ofCandidate Next C) Next := by
  intro x y
  rfl

theorem ofCandidate_roundTrip_iff
    {X : Type w}
    (Next : X -> X -> Prop)
    (C : X -> Prop)
    (x y : X) :
    RoundTrip (CarrierSemantics.ofCandidate Next C) x y <->
      CarrierRoundTripLanguage Next C x y := by
  rfl

/--
A semantic certificate whose path relation matches adapter internal paths
reconstructs an ordinary carrier certificate.
-/
theorem semanticCertificate_to_carrierCertificate
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {K : CarrierSemantics S.Fragment}
    {x y : S.Fragment}
    (hMatch : PathMatchesDynamics K Next)
    (hCert : CarrierSemanticCertificate S Next safe K x y) :
    CarrierCertificate S Next safe K.carrier x y := by
  exact And.intro
    hCert.left
    (And.intro
      hCert.right.left.left
      (And.intro
        hCert.right.left.right
        (And.intro
          ((hMatch x y).mp hCert.right.right.left.left)
          (And.intro
            ((hMatch y x).mp hCert.right.right.left.right)
            hCert.right.right.right))))

/--
Ordinary carrier certificates become semantic certificates for the raw
candidate semantics.
-/
theorem carrierCertificate_to_semanticCertificate_ofCandidate
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hCert : CarrierCertificate S Next safe C x y) :
    CarrierSemanticCertificate
      S
      Next
      safe
      (CarrierSemantics.ofCandidate Next C)
      x
      y := by
  exact And.intro
    (certificate_recurrent hCert)
    (And.intro
      (And.intro
        (certificate_contains_left hCert)
        (certificate_contains_right hCert))
      (And.intro
        (certificate_roundTripLanguage hCert)
        (certificate_mergeSeparated hCert)))

/--
Generated mutual-reach carrier certificates also become semantic certificates.
This compresses the generated-carrier layer into the same carrier-semantics
surface.
-/
theorem generatedMutualReach_semanticCertificate_of_recurrent
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe Ambient : S.Fragment -> Prop}
    {x y : S.Fragment}
    (hRec :
      RecurrentViableClass
        (dynFromNext Next)
        safe
        (MutualReachCarrier Next Ambient x y))
    (hx : MutualReachCarrier Next Ambient x y x)
    (hy : MutualReachCarrier Next Ambient x y y)
    (hSep : ConsequenceMergeSeparated S x y) :
    CarrierSemanticCertificate
      S
      Next
      safe
      (CarrierSemantics.ofGeneratedMutualReach Next Ambient x y)
      x
      y := by
  exact carrierCertificate_to_semanticCertificate_ofCandidate
    (mutualReachCarrier_certificate_of_recurrent hRec hx hy hSep)

/-- The two-state cycle certificate as carrier semantics. -/
theorem cycle_carrier_semanticCertificate :
    CarrierSemanticCertificate
      cycleConsequenceSystem
      cycleNext
      cycleSafe
      (CarrierSemantics.ofCandidate cycleNext cycleClass)
      CycleState.left
      CycleState.right := by
  exact carrierCertificate_to_semanticCertificate_ofCandidate
    cycle_carrier_certificate

end CarrierSemantics
end Trajectory
end OmegaProper
