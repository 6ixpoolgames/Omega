import OmegaProper.Decision.NonrecoverableLossDominance

/-!
OmegaProper.Decision.TerminationSupremum

Measure-free replacement for denominator/fraction-of-field rhetoric.

If a per-valuer termination profile contracts a declared top fact, then it
nonrecoverable-loss-dominates every other contraction profile over that
valuer's declared fact order. This is still only a declared-profile theorem:
it is not cross-valuer aggregation, moral standing, patienthood, rights,
agency, identity, value, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace TerminationSupremum

open NonrecoverableLossDominance

universe u

variable {Fact : Type u} [Preorder Fact]

/--
If `top` is above every declared fact and `Termination` contracts `top`, then
`Termination` loss-dominates every declared contraction profile.
-/
theorem termination_contracts_top_lossDominates_all
    (top : Fact)
    (hTop : forall f : Fact, f <= top)
    (Termination Other : ContractionProfile Fact)
    (hTermTop : Termination top) :
    LossDominates Termination Other := by
  intro f _hf
  exact ⟨top, hTermTop, hTop f⟩

/--
Valuation-facing corollary via the existing loss-dominance acceptance bridge.
-/
theorem termination_contracts_top_monotone_covers_all
    [DecidableRel ((· <= ·) : Fact -> Fact -> Prop)]
    (top : Fact)
    (hTop : forall f : Fact, f <= top)
    (Termination Other : ContractionProfile Fact)
    (hTermTop : Termination top) :
    forall v : Fact -> Nat,
      Dominance.MonotoneValuation v ->
      Dominance.AngelicValuationCovers Termination Other v := by
  exact
    (lossDominates_iff_all_monotone_valuation_covers
      Termination Other).mp
      (termination_contracts_top_lossDominates_all
        top hTop Termination Other hTermTop)

end TerminationSupremum
end Decision
end OmegaProper
