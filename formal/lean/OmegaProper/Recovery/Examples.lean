import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import OmegaProper.Recovery.Deterministic

/-!
OmegaProper.Recovery.Examples

Small finite witnesses for the graded recovery layer.

These examples show:

* high-confidence recovery need not be support-exact;
* positive support does not determine graded recovery thresholds.
-/

namespace OmegaProper
namespace Recovery
namespace Examples

abbrev Bit := Fin 2

lemma bit_eq_zero_or_one (b : Bit) : b = 0 ∨ b = 1 := by
  fin_cases b <;> simp

/-- Declared two-point target. -/
def bitTarget : Bit -> Bit :=
  id

/-- Declared two-point observation. -/
def bitObserve : Bit -> Bit :=
  id

/-- Identity decoder for two-point observations. -/
def bitDecoder : Bit -> Bit :=
  id

/-- Binary symmetric channel with `99/100` correct mass and full support. -/
def highConfidenceChannel : RatChannel Bit Bit where
  prob x y := if y = x then (99 / 100 : ℚ) else (1 / 100 : ℚ)
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/-- Binary symmetric channel with `9/10` correct mass and full support. -/
def highFullSupportChannel : RatChannel Bit Bit where
  prob x y := if y = x then (9 / 10 : ℚ) else (1 / 10 : ℚ)
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/-- Binary symmetric channel with `3/5` correct mass and full support. -/
def lowFullSupportChannel : RatChannel Bit Bit where
  prob x y := if y = x then (3 / 5 : ℚ) else (2 / 5 : ℚ)
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/--
The `99/100` channel has deterministic recovery at threshold `99/100`.
-/
theorem highConfidence_recoveryAt_99_100 :
    RecoveryExistsAt highConfidenceChannel bitTarget bitObserve (99 / 100 : ℚ) := by
  exact Exists.intro bitDecoder fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, highConfidenceChannel,
      bitTarget, bitObserve, bitDecoder, Finset.univ_fin2]

/--
The same high-confidence channel is not support-exact, because every output has
positive support from every source.
-/
theorem highConfidence_not_supportExact :
    Not (
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        (PositiveSupport highConfidenceChannel) bitTarget bitObserve
    ) := by
  intro hExact
  match hExact with
  | Exists.intro decoder hDecoder =>
      have hZero : decoder 0 = 0 :=
        hDecoder 0 0 (by norm_num [PositiveSupport, highConfidenceChannel])
      have hOne : decoder 0 = 1 :=
        hDecoder 1 0 (by norm_num [PositiveSupport, highConfidenceChannel])
      rw [hZero] at hOne
      norm_num at hOne

/--
The two full-support channels have the same positive-support relation.
-/
theorem high_low_same_positiveSupport :
    forall x y,
      PositiveSupport highFullSupportChannel x y <->
        PositiveSupport lowFullSupportChannel x y := by
  intro x y
  fin_cases x <;> fin_cases y <;>
    norm_num [PositiveSupport, highFullSupportChannel, lowFullSupportChannel]

/-- The high full-support channel reaches threshold `9/10`. -/
theorem highFullSupport_recoveryAt_9_10 :
    RecoveryExistsAt highFullSupportChannel bitTarget bitObserve (9 / 10 : ℚ) := by
  exact Exists.intro bitDecoder fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, highFullSupportChannel,
      bitTarget, bitObserve, bitDecoder, Finset.univ_fin2]

/--
The low full-support channel cannot reach threshold `4/5` with any deterministic
two-point decoder.
-/
theorem lowFullSupport_not_recoveryAt_4_5 :
    Not (RecoveryExistsAt lowFullSupportChannel bitTarget bitObserve (4 / 5 : ℚ)) := by
  intro hRecovery
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      rcases bit_eq_zero_or_one (decoder 0) with hFalse | hFalse
      · rcases bit_eq_zero_or_one (decoder 1) with hTrue | hTrue
        · have hSrc := hDecoder 1
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc
        · have hSrc := hDecoder 0
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc
      · rcases bit_eq_zero_or_one (decoder 1) with hTrue | hTrue
        · have hSrc := hDecoder 0
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc
        · have hSrc := hDecoder 0
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc

end Examples
end Recovery
end OmegaProper
