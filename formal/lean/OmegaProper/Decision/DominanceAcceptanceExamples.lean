import OmegaProper.Decision.DominanceAcceptance
import OmegaProper.Decision.DominanceExamples

/-!
OmegaProper.Decision.DominanceAcceptanceExamples

Small examples for the ODT1 acceptance bridge.

These examples reuse the finite W1/W2/W5 surfaces from
`DominanceExamples.lean` and show how failed dominance produces concrete
monotone valuation disagreement.
-/

namespace OmegaProper
namespace Decision
namespace DominanceAcceptanceExamples

open Dominance
open DominanceExamples

/-! ## W1: Hoare failure gives an up-indicator valuation separator. -/

theorem W1_hoare_failure_has_separating_valuation :
    exists out,
      W1B out /\
      MonotoneValuation (UpIndicator out) /\
      forall candidate,
        W1A candidate ->
        UpIndicator out candidate < UpIndicator out out := by
  exact ⟨ThreeDiscrete.c, by
    constructor
    · simp [W1B]
    · constructor
      · exact upIndicator_monotone ThreeDiscrete.c
      · intro candidate hA
        have hNoLe : Not (ThreeDiscrete.c <= candidate) := by
          intro hle
          cases candidate <;> simp [W1A] at hA
          · cases hle
          · cases hle
        have hAZero : UpIndicator ThreeDiscrete.c candidate = 0 :=
          (upIndicator_eq_zero_iff ThreeDiscrete.c candidate).mpr hNoLe
        have hSelf : UpIndicator ThreeDiscrete.c ThreeDiscrete.c = 1 :=
          upIndicator_self ThreeDiscrete.c
        calc
          UpIndicator ThreeDiscrete.c candidate = 0 := hAZero
          _ < 1 := by decide
          _ = UpIndicator ThreeDiscrete.c ThreeDiscrete.c := hSelf.symm⟩

/-! ## W2: Smyth failure gives a down-complement valuation separator. -/

theorem W2_smyth_failure_has_separating_valuation :
    exists a,
      W2A a /\
      MonotoneValuation (AboveComplementIndicator a) /\
      forall b, W2B b ->
        AboveComplementIndicator a b >
          AboveComplementIndicator a a := by
  exact ⟨Chain3.low, by
    constructor
    · simp [W2A]
    · constructor
      · exact aboveComplementIndicator_monotone Chain3.low
      · intro b hB
        have hNoLe : Not (b <= Chain3.low) := by
          cases b <;> simp [W2B] at hB
          intro hle
          have hNo : Not (Chain3.mid <= Chain3.low) := by
            change Not (Chain3.rank Chain3.mid <= Chain3.rank Chain3.low)
            decide
          exact hNo hle
        have hBOne : AboveComplementIndicator Chain3.low b = 1 :=
          (aboveComplementIndicator_eq_one_iff Chain3.low b).mpr hNoLe
        have hSelf : AboveComplementIndicator Chain3.low Chain3.low = 0 :=
          aboveComplementIndicator_self Chain3.low
        calc
          AboveComplementIndicator Chain3.low b = 1 := hBOne
          _ > 0 := by decide
          _ = AboveComplementIndicator Chain3.low Chain3.low := hSelf.symm⟩

/-!
W5 remains valuation-class relative: the acceptance theorem applies to
monotone valuations, while the retained `prefersLow` valuation is nonmonotone.
-/
theorem W5_acceptance_and_nonmonotone_reversal :
    (forall v : TwoOutcome -> Nat,
      MonotoneValuation v ->
      AngelicValuationCovers W5A W5B v) /\
    (forall v : TwoOutcome -> Nat,
      MonotoneValuation v ->
      DemonicValuationFloors W5A W5B v) /\
    prefersLow TwoOutcome.high < prefersLow TwoOutcome.low /\
    Not (MonotoneValuation prefersLow) := by
  exact ⟨
    (hoare_iff_all_monotone_angelic_covers W5A W5B).mp W5_A_hoare_B,
    (smyth_iff_all_monotone_demonic_floors W5A W5B).mp W5_A_smyth_B,
    prefersLow_prefers_low,
    prefersLow_not_monotone⟩

end DominanceAcceptanceExamples
end Decision
end OmegaProper
