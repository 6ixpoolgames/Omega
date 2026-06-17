import OmegaProper.Trajectory.RecurrentSupportRobustness

/-!
OmegaProper.Trajectory.CarrierCertificate

Carrier certificates for recurrently carried consequence distinctions.

This file repairs the status of "support" language. A predicate `C` is only a
candidate carrier until it is certified for a declared pair. Certification is
currently the existing recurrent-support carrying package: recurrent viability
plus internal path-carrying of a merge-separated consequence distinction.

This does not define objecthood, identity, boundaries, agency, value, deformer
structure, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace CarrierCertificate

open CarriedDistinction
open ConsequenceRelation
open DistinctionSupport
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRobustness
open RecurrentViableClass
open SustainingViableClass

universe w k o

/--
A carrier candidate is just a declared predicate over a carrier type.

It has no standing by declaration alone.
-/
abbrev CarrierCandidate (X : Type w) : Type w :=
  X -> Prop

/--
A carrier certificate says that a candidate carrier recurrently carries a
declared merge-separated consequence distinction.

This is an alias for the existing formal package. The name records the claim
hygiene: candidate support is supplied; certification is checked.
-/
abbrev CarrierCertificate
    (S : ConsequenceSystem.{w, k, o})
    (Next : S.Fragment -> S.Fragment -> Prop)
    (safe : S.Fragment -> Prop)
    (C : CarrierCandidate S.Fragment)
    (x y : S.Fragment) : Prop :=
  RecurrentSupportCarries S Next safe C x y

/-- A certified carrier is recurrent viable. -/
theorem certificate_recurrent
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    RecurrentViableClass (dynFromNext Next) safe C := by
  exact recurrentSupportCarries_recurrent h

/-- A certified carrier contains the left endpoint of the declared pair. -/
theorem certificate_contains_left
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    C x := by
  exact h.right.left

/-- A certified carrier contains the right endpoint of the declared pair. -/
theorem certificate_contains_right
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    C y := by
  exact h.right.right.left

/-- A certified carrier internally connects the pair forward. -/
theorem certificate_forward_path
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    InternalPath (dynFromNext Next) C x y := by
  exact h.right.right.right.left

/-- A certified carrier internally connects the pair backward. -/
theorem certificate_reverse_path
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    InternalPath (dynFromNext Next) C y x := by
  exact h.right.right.right.right.left

/-- A certified carrier keeps the pair merge-separated. -/
theorem certificate_mergeSeparated
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    ConsequenceMergeSeparated S x y := by
  exact h.right.right.right.right.right

/-- A certified carrier gives viability of the left endpoint. -/
theorem certificate_left_viable
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    Viable (dynFromNext Next) safe x := by
  exact recurrentSupportCarries_left_viable h

/-- A certified carrier gives viability of the right endpoint. -/
theorem certificate_right_viable
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (h : CarrierCertificate S Next safe C x y) :
    Viable (dynFromNext Next) safe y := by
  exact recurrentSupportCarries_right_viable h

/-- Missing the left endpoint blocks certification. -/
theorem missing_left_blocks_certificate
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hMissing : Not (C x)) :
    Not (CarrierCertificate S Next safe C x y) := by
  exact not_recurrentSupportCarries_if_left_missing hMissing

/-- Missing the right endpoint blocks certification. -/
theorem missing_right_blocks_certificate
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hMissing : Not (C y)) :
    Not (CarrierCertificate S Next safe C x y) := by
  exact not_recurrentSupportCarries_if_right_missing hMissing

/-- Missing the forward internal path blocks certification. -/
theorem missing_forward_path_blocks_certificate
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hMissing :
      Not (InternalPath (dynFromNext Next) C x y)) :
    Not (CarrierCertificate S Next safe C x y) := by
  exact not_recurrentSupportCarries_if_forward_path_missing hMissing

/-- Missing the reverse internal path blocks certification. -/
theorem missing_reverse_path_blocks_certificate
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe : S.Fragment -> Prop}
    {C : CarrierCandidate S.Fragment}
    {x y : S.Fragment}
    (hMissing :
      Not (InternalPath (dynFromNext Next) C y x)) :
    Not (CarrierCertificate S Next safe C x y) := by
  exact not_recurrentSupportCarries_if_reverse_path_missing hMissing

/-- The two-state cycle support is a certified carrier for `left/right`. -/
theorem cycle_carrier_certificate :
    CarrierCertificate
      cycleConsequenceSystem
      cycleNext
      cycleSafe
      cycleClass
      CycleState.left
      CycleState.right := by
  exact cycle_recurrentSupportCarries_left_right

end CarrierCertificate
end Trajectory
end OmegaProper
