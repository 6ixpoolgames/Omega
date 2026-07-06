import OmegaProper.Decision.DominanceAcceptance

/-!
OmegaProper.Decision.ExpansionDominance

Thin order layer for declared expansion profiles.

This is the gain-side mirror of declared nonrecoverable-loss dominance. It is
only a comparison surface over registered facts. It does not create an
expansion gate, obligation to expand, value theory, standing relation,
population comparison, agency claim, identity claim, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace ExpansionDominance

open Dominance

universe u

variable {Fact : Type u} [Preorder Fact]

/-- A declared expansion profile: `P f` means fact/capacity `f` is expanded. -/
abbrev ExpansionProfile (Fact : Type u) := Fact -> Prop

/--
Closure of an expansion profile in the declared fact preorder.

If a stronger declared fact is expanded, weaker facts below it count as covered.
The preorder is registered structure, not derived value.
-/
def CoveredExpansion (P : ExpansionProfile Fact) : ExpansionProfile Fact :=
  fun f => exists g, P g /\ f <= g

/--
`P` expansion-dominates `Q` when every covered declared expansion of `Q` is
also covered by `P`.

This compares declared expansion profiles only. It is not an obligation to
choose `P`, and it is not a claim about final value.
-/
def ExpansionDominates (P Q : ExpansionProfile Fact) : Prop :=
  forall f, CoveredExpansion Q f -> CoveredExpansion P f

/-- Equivalence under the declared expansion preorder. -/
def ExpansionEquivalent (P Q : ExpansionProfile Fact) : Prop :=
  ExpansionDominates P Q /\ ExpansionDominates Q P

/-- Incomparability under the declared expansion preorder. -/
def ExpansionIncomparable (P Q : ExpansionProfile Fact) : Prop :=
  Not (ExpansionDominates P Q) /\ Not (ExpansionDominates Q P)

/-- A named witness that `P` fails to expansion-dominate `Q`. -/
def ExpansionFailureCertificate
    (P Q : ExpansionProfile Fact) (f : Fact) : Prop :=
  CoveredExpansion Q f /\ Not (CoveredExpansion P f)

theorem expansionDominates_refl (P : ExpansionProfile Fact) :
    ExpansionDominates P P := by
  intro f hf
  exact hf

theorem expansionDominates_trans {P Q R : ExpansionProfile Fact}
    (hPQ : ExpansionDominates P Q)
    (hQR : ExpansionDominates Q R) :
    ExpansionDominates P R := by
  intro f hf
  exact hPQ f (hQR f hf)

theorem profile_mem_coveredExpansion {P : ExpansionProfile Fact} {f : Fact}
    (hf : P f) :
    CoveredExpansion P f := by
  exact Exists.intro f (And.intro hf le_rfl)

theorem expansionDominates_iff_hoareDominates
    (P Q : ExpansionProfile Fact) :
    ExpansionDominates P Q <-> HoareDominates P Q := by
  constructor
  · intro hExpansion q hQ
    rcases hExpansion q (profile_mem_coveredExpansion hQ) with
      ⟨p, hP, hqp⟩
    exact ⟨p, hP, hqp⟩
  · intro hHoare f hQCovered
    rcases hQCovered with ⟨q, hQ, hfq⟩
    rcases hHoare q hQ with ⟨p, hP, hqp⟩
    exact ⟨p, hP, le_trans hfq hqp⟩

theorem not_expansionDominates_iff_exists_failure_certificate
    (P Q : ExpansionProfile Fact) :
    Not (ExpansionDominates P Q) <->
      exists f, ExpansionFailureCertificate P Q f := by
  constructor
  · intro hNot
    classical
    rcases not_forall.mp hNot with ⟨f, hfNot⟩
    have hQCovered : CoveredExpansion Q f := Classical.byContradiction (by
      intro hNoQ
      exact hfNot (fun hQ => False.elim (hNoQ hQ)))
    exact ⟨f, hQCovered, (by
      intro hPCovered
      exact hfNot (fun _ => hPCovered))⟩
  · intro hCert hExpansion
    rcases hCert with ⟨f, hQCovered, hNoPCovered⟩
    exact hNoPCovered (hExpansion f hQCovered)

/--
Acceptance bridge inherited from ODT1 Hoare dominance.

Expansion dominance is equivalent to unanimous pointwise cover across monotone
valuations of declared facts. This is value-parametric: the fact preorder and
admissible monotone valuations are registered inputs.
-/
theorem expansionDominates_iff_all_monotone_valuation_covers
    [DecidableRel ((· <= ·) : Fact -> Fact -> Prop)]
    (P Q : ExpansionProfile Fact) :
    ExpansionDominates P Q <->
      forall v : Fact -> Nat,
        MonotoneValuation v ->
        AngelicValuationCovers P Q v := by
  rw [expansionDominates_iff_hoareDominates]
  exact hoare_iff_all_monotone_angelic_covers P Q

/-- Verdict vocabulary for consumers that need a finite comparison surface. -/
inductive ExpansionDominanceVerdict where
  | dominates
  | dominated
  | equivalent
  | incomparable
deriving DecidableEq, Repr

end ExpansionDominance
end Decision
end OmegaProper
