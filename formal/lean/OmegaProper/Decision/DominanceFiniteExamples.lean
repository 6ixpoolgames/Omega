import OmegaProper.Decision.DominanceFinite
import OmegaProper.Decision.DominanceExamples

/-!
OmegaProper.Decision.DominanceFiniteExamples

Small finite examples for ODT1 best/worst acceptance.
-/

namespace OmegaProper
namespace Decision
namespace DominanceFiniteExamples

open Dominance
open DominanceExamples

def W2FiniteA : FiniteOutcomeSurface Chain3 where
  carrier := {Chain3.low, Chain3.high}
  nonempty := by
    exact ⟨Chain3.low, by simp⟩

def W2FiniteB : FiniteOutcomeSurface Chain3 where
  carrier := {Chain3.mid}
  nonempty := by
    exact ⟨Chain3.mid, by simp⟩

theorem W2FiniteA_holds_iff (w : Chain3) :
    W2FiniteA.Holds w <-> W2A w := by
  cases w <;> simp [W2FiniteA, FiniteOutcomeSurface.Holds, W2A]

theorem W2FiniteB_holds_iff (w : Chain3) :
    W2FiniteB.Holds w <-> W2B w := by
  cases w <;> simp [W2FiniteB, FiniteOutcomeSurface.Holds, W2B]

def chainValue : Chain3 -> Nat := Chain3.rank

theorem chainValue_monotone :
    MonotoneValuation chainValue := by
  intro x y hxy
  exact hxy

theorem W2_best_accepts_A_over_B :
    BestValueGE W2FiniteA W2FiniteB chainValue := by
  have hHoareFinite : HoareDominates W2FiniteA.Holds W2FiniteB.Holds := by
    intro b hB
    rcases W2_A_hoare_B b ((W2FiniteB_holds_iff b).mp hB) with
      ⟨a, hA, hle⟩
    exact ⟨a, (W2FiniteA_holds_iff a).mpr hA, hle⟩
  exact
    (hoare_iff_all_monotone_bestValue_ge W2FiniteA W2FiniteB).mp
      hHoareFinite chainValue chainValue_monotone

theorem W2_worst_rejects_A_over_B :
    Not (WorstValueGE W2FiniteA W2FiniteB chainValue) := by
  intro hWorst
  have hWorstA : worstValue W2FiniteA chainValue = 0 := by
    apply worstValue_eq_of_isWorstValue
    constructor
    · exact ⟨Chain3.low, by simp [W2FiniteA, FiniteOutcomeSurface.Holds],
        rfl⟩
    · intro w hw
      cases w <;> simp [W2FiniteA, FiniteOutcomeSurface.Holds, chainValue,
        Chain3.rank] at hw ⊢
  have hWorstB : worstValue W2FiniteB chainValue = 1 := by
    apply worstValue_eq_of_isWorstValue
    constructor
    · exact ⟨Chain3.mid, by simp [W2FiniteB, FiniteOutcomeSurface.Holds],
        rfl⟩
    · intro w hw
      cases w <;> simp [W2FiniteB, FiniteOutcomeSurface.Holds, chainValue,
        Chain3.rank] at hw ⊢
  simp [WorstValueGE, hWorstA, hWorstB] at hWorst

def W5FiniteA : FiniteOutcomeSurface TwoOutcome where
  carrier := {TwoOutcome.high}
  nonempty := by
    exact ⟨TwoOutcome.high, by simp⟩

def W5FiniteB : FiniteOutcomeSurface TwoOutcome where
  carrier := {TwoOutcome.low}
  nonempty := by
    exact ⟨TwoOutcome.low, by simp⟩

theorem W5FiniteA_holds_iff (w : TwoOutcome) :
    W5FiniteA.Holds w <-> W5A w := by
  cases w <;> simp [W5FiniteA, FiniteOutcomeSurface.Holds, W5A]

theorem W5FiniteB_holds_iff (w : TwoOutcome) :
    W5FiniteB.Holds w <-> W5B w := by
  cases w <;> simp [W5FiniteB, FiniteOutcomeSurface.Holds, W5B]

theorem W5_finite_best_and_worst_acceptance :
    (forall v : TwoOutcome -> Nat,
      MonotoneValuation v ->
      BestValueGE W5FiniteA W5FiniteB v) /\
    (forall v : TwoOutcome -> Nat,
      MonotoneValuation v ->
      WorstValueGE W5FiniteA W5FiniteB v) := by
  have hHoareFinite : HoareDominates W5FiniteA.Holds W5FiniteB.Holds := by
    intro b hB
    rcases W5_A_hoare_B b ((W5FiniteB_holds_iff b).mp hB) with
      ⟨a, hA, hle⟩
    exact ⟨a, (W5FiniteA_holds_iff a).mpr hA, hle⟩
  have hSmythFinite : SmythDominates W5FiniteA.Holds W5FiniteB.Holds := by
    intro a hA
    rcases W5_A_smyth_B a ((W5FiniteA_holds_iff a).mp hA) with
      ⟨b, hB, hle⟩
    exact ⟨b, (W5FiniteB_holds_iff b).mpr hB, hle⟩
  exact
    ⟨(hoare_iff_all_monotone_bestValue_ge W5FiniteA W5FiniteB).mp
        hHoareFinite,
      (smyth_iff_all_monotone_worstValue_ge W5FiniteA W5FiniteB).mp
        hSmythFinite⟩

end DominanceFiniteExamples
end Decision
end OmegaProper
