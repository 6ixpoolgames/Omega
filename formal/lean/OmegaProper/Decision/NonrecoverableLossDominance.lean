import OmegaProper.Decision.DominanceAcceptance

/-!
OmegaProper.Decision.NonrecoverableLossDominance

Thin order layer for declared nonrecoverable-loss profiles.

This file deliberately stays below harm, rights, patienthood, moral standing,
agency, identity, value, and Omega validation. A profile is just a declared
family of facts contracted by an intervention. The order says only that one
profile contains at least as much declared nonrecoverable loss as another, after
down-closure in the declared fact preorder.
-/

namespace OmegaProper
namespace Decision
namespace NonrecoverableLossDominance

open Dominance

universe u

variable {Fact : Type u} [Preorder Fact]

/-- A declared intervention-loss profile: `P f` means fact `f` is lost. -/
abbrev ContractionProfile (Fact : Type u) := Fact -> Prop

/--
Down-closure of a contraction profile in the declared fact preorder.

If a stronger fact is contracted, facts below it in the declared order count as
contracted by closure. The preorder is registered structure, not derived value.
-/
def DownClosedProfile (P : ContractionProfile Fact) : ContractionProfile Fact :=
  fun f => exists g, P g /\ f <= g

/--
`P` nonrecoverable-loss-dominates `Q` when every down-closed declared loss of
`Q` is also a down-closed declared loss of `P`.

This is a relation between interventions/profiles, not between patients or
moral weights.
-/
def LossDominates (P Q : ContractionProfile Fact) : Prop :=
  forall f, DownClosedProfile Q f -> DownClosedProfile P f

/-- Equivalence under the declared nonrecoverable-loss preorder. -/
def LossEquivalent (P Q : ContractionProfile Fact) : Prop :=
  LossDominates P Q /\ LossDominates Q P

/-- Incomparability under the declared nonrecoverable-loss preorder. -/
def LossIncomparable (P Q : ContractionProfile Fact) : Prop :=
  Not (LossDominates P Q) /\ Not (LossDominates Q P)

/-- A named witness that `P` fails to loss-dominate `Q`. -/
def LossFailureCertificate
    (P Q : ContractionProfile Fact) (f : Fact) : Prop :=
  DownClosedProfile Q f /\ Not (DownClosedProfile P f)

theorem lossDominates_refl (P : ContractionProfile Fact) :
    LossDominates P P := by
  intro f hf
  exact hf

theorem lossDominates_trans {P Q R : ContractionProfile Fact}
    (hPQ : LossDominates P Q)
    (hQR : LossDominates Q R) :
    LossDominates P R := by
  intro f hf
  exact hPQ f (hQR f hf)

theorem profile_mem_downClosed {P : ContractionProfile Fact} {f : Fact}
    (hf : P f) :
    DownClosedProfile P f := by
  exact ⟨f, hf, le_rfl⟩

theorem lossDominates_iff_hoareDominates
    (P Q : ContractionProfile Fact) :
    LossDominates P Q <-> HoareDominates P Q := by
  constructor
  · intro hLoss q hQ
    rcases hLoss q (profile_mem_downClosed hQ) with ⟨p, hP, hqp⟩
    exact ⟨p, hP, hqp⟩
  · intro hHoare f hQDown
    rcases hQDown with ⟨q, hQ, hfq⟩
    rcases hHoare q hQ with ⟨p, hP, hqp⟩
    exact ⟨p, hP, le_trans hfq hqp⟩

theorem not_lossDominates_iff_exists_failure_certificate
    (P Q : ContractionProfile Fact) :
    Not (LossDominates P Q) <->
      exists f, LossFailureCertificate P Q f := by
  constructor
  · intro hNot
    classical
    rcases not_forall.mp hNot with ⟨f, hfNot⟩
    have hQDown : DownClosedProfile Q f := Classical.byContradiction (by
      intro hNoQ
      exact hfNot (fun hQ => False.elim (hNoQ hQ)))
    exact ⟨f, hQDown, (by
      intro hPDown
      exact hfNot (fun _ => hPDown))⟩
  · intro hCert hLoss
    rcases hCert with ⟨f, hQDown, hNoPDown⟩
    exact hNoPDown (hLoss f hQDown)

/--
Acceptance bridge inherited from ODT1 Hoare dominance.

Loss dominance is equivalent to unanimous pointwise cover across monotone
valuations of declared facts. This is value-parametric: the fact preorder and
admissible monotone valuations are registered inputs.
-/
theorem lossDominates_iff_all_monotone_valuation_covers
    [DecidableRel ((· <= ·) : Fact -> Fact -> Prop)]
    (P Q : ContractionProfile Fact) :
    LossDominates P Q <->
      forall v : Fact -> Nat,
        MonotoneValuation v ->
        AngelicValuationCovers P Q v := by
  rw [lossDominates_iff_hoareDominates]
  exact hoare_iff_all_monotone_angelic_covers P Q

/-- Verdict vocabulary for consumers that need a finite comparison surface. -/
inductive LossDominanceVerdict where
  | dominates
  | dominated
  | equivalent
  | incomparable
deriving DecidableEq, Repr

end NonrecoverableLossDominance
end Decision
end OmegaProper
