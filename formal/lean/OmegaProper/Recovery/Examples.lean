import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import OmegaProper.Recovery.Joint
import OmegaProper.Recovery.PolicyContinuation
import OmegaProper.Recovery.Prior
import OmegaProper.Recovery.Randomized
import OmegaProper.Recovery.Robust

/-!
OmegaProper.Recovery.Examples

Small finite witnesses for the graded recovery layer.

These examples show:

* high-confidence recovery need not be support-exact;
* positive support does not determine graded recovery thresholds;
* per-channel exact recovery does not imply robust recovery with one common
  decoder over an ambiguity set;
* high expected recovery under a skewed prior does not imply worst-case
  threshold recovery.
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

/-- Constant zero decoder for erased one-label observations. -/
def constZeroUnitDecoder : Unit -> Bit :=
  fun _ => 0

/-- Flip the two-point value. -/
def bitFlip (b : Bit) : Bit :=
  if b = 0 then 1 else 0

/-- Constant observation erases the two output labels. -/
def constantObserve : Bit -> Unit :=
  fun _ => ()

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

/-- Identity channel on the two-point space. -/
def identityBitChannel : RatChannel Bit Bit where
  prob x y := if y = x then (1 : ℚ) else 0
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/-- Exact channel whose output is the flipped source bit. -/
def flipBitChannel : RatChannel Bit Bit where
  prob x y := if y = bitFlip x then (1 : ℚ) else 0
  nonneg := by
    intro x y
    by_cases h : y = bitFlip x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [bitFlip, Finset.univ_fin2]

/-- Uniform randomized decoder from one observation label to two target values. -/
def uniformBitRandomizedDecoder : RandomizedDecoder Unit Bit where
  prob _ _ := (1 / 2 : ℚ)
  nonneg := by
    intro _ _
    norm_num
  row_sum_one := by
    intro _
    norm_num [Finset.univ_fin2]

/-- Prior putting `99/100` mass on source `0` and `1/100` on source `1`. -/
def skewedZeroPrior : RatPrior Bit where
  mass x := if x = 0 then (99 / 100 : ℚ) else (1 / 100 : ℚ)
  nonneg := by
    intro x
    by_cases h : x = 0
    · norm_num [h]
    · norm_num [h]
  sum_one := by
    norm_num [Finset.univ_fin2]

/-- Identity support relation for the two-bit panel witness. -/
def pairSupport (x y : Bit × Bit) : Prop :=
  y = x

/-- First marginal observation for a two-bit output. -/
def firstPairObserve (y : Bit × Bit) : Bit :=
  y.1

/-- Second marginal observation for a two-bit output. -/
def secondPairObserve (y : Bit × Bit) : Bit :=
  y.2

/-- First declared component of a two-bit source. -/
def firstPairTarget (x : Bit × Bit) : Bit :=
  x.1

/-- Second declared component of a two-bit source. -/
def secondPairTarget (x : Bit × Bit) : Bit :=
  x.2

/-- Joint declared target for a two-bit source. -/
def wholePairTarget (x : Bit × Bit) : Bit × Bit :=
  x

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

/--
A single deterministic observation label cannot recover two source classes at
threshold `1/2`.
-/
theorem constantObservation_not_recoveryAt_half :
    Not (RecoveryExistsAt identityBitChannel bitTarget constantObserve (1 / 2 : ℚ)) := by
  intro hRecovery
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      rcases bit_eq_zero_or_one (decoder ()) with hDecoderValue | hDecoderValue
      · have hSrc := hDecoder 1
        norm_num [DeclaredRecoveryAt, Success, identityBitChannel,
          bitTarget, constantObserve, hDecoderValue, Finset.univ_fin2] at hSrc
      · have hSrc := hDecoder 0
        norm_num [DeclaredRecoveryAt, Success, identityBitChannel,
          bitTarget, constantObserve, hDecoderValue, Finset.univ_fin2] at hSrc

/--
The uniform randomized decoder reaches threshold `1/2` for the same one-label
observation.
-/
theorem constantObservation_randomizedRecoveryAt_half :
    RandomizedRecoveryAt identityBitChannel bitTarget constantObserve (1 / 2 : ℚ) := by
  exact Exists.intro uniformBitRandomizedDecoder fun x => by
    fin_cases x <;> norm_num [RandomizedSuccess, identityBitChannel, bitTarget,
      constantObserve, uniformBitRandomizedDecoder, Finset.univ_fin2]

/-- The identity bit channel has exact deterministic recovery. -/
theorem identityBitChannel_recoveryAt_one :
    RecoveryExistsAt identityBitChannel bitTarget bitObserve 1 := by
  exact Exists.intro bitDecoder fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, identityBitChannel,
      bitTarget, bitObserve, bitDecoder, Finset.univ_fin2]

/-- The flipped bit channel has exact deterministic recovery using the flipped decoder. -/
theorem flipBitChannel_recoveryAt_one :
    RecoveryExistsAt flipBitChannel bitTarget bitObserve 1 := by
  exact Exists.intro bitFlip fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, flipBitChannel,
      bitTarget, bitObserve, bitFlip, Finset.univ_fin2]

/--
Each channel in the ambiguity set is exactly recoverable on its own, but no
single deterministic decoder recovers both channels at threshold one.
-/
theorem identity_flip_each_recoverable_not_robust :
    RecoveryExistsAt identityBitChannel bitTarget bitObserve 1 ∧
      RecoveryExistsAt flipBitChannel bitTarget bitObserve 1 ∧
      Not (
        RobustRecoveryAt
          ({identityBitChannel, flipBitChannel} : Set (RatChannel Bit Bit))
          bitTarget bitObserve 1
      ) := by
  refine ⟨identityBitChannel_recoveryAt_one, flipBitChannel_recoveryAt_one, ?_⟩
  intro hRobust
  match hRobust with
  | Exists.intro decoder hDecoder =>
      have hIdZero :
          (1 : ℚ) <=
            Success identityBitChannel bitTarget bitObserve decoder 0 :=
        hDecoder identityBitChannel (by simp) 0
      have hFlipOne :
          (1 : ℚ) <=
            Success flipBitChannel bitTarget bitObserve decoder 1 :=
        hDecoder flipBitChannel (by simp) 1
      rcases bit_eq_zero_or_one (decoder 0) with hDecoderZero | hDecoderZero
      · norm_num [Success, flipBitChannel, bitTarget, bitObserve, bitFlip,
          hDecoderZero, Finset.univ_fin2] at hFlipOne
      · norm_num [Success, identityBitChannel, bitTarget, bitObserve,
          hDecoderZero, Finset.univ_fin2] at hIdZero

/--
Under a skewed source prior, the erased observation with a constant decoder has
high expected success.
-/
theorem skewedPrior_constantObservation_expectedRecoveryAt_99_100 :
    ExpectedRecoveryExistsAt skewedZeroPrior identityBitChannel bitTarget
      constantObserve (99 / 100 : ℚ) := by
  refine Exists.intro constZeroUnitDecoder ?_
  norm_num [ExpectedDeclaredRecoveryAt, ExpectedDecoderSuccess,
    ExpectedSuccess, RecoveryProfile, Success, skewedZeroPrior,
    identityBitChannel, bitTarget, constantObserve, constZeroUnitDecoder,
    Finset.univ_fin2]

/--
High expected recovery under a declared prior does not imply worst-case
threshold recovery.
-/
theorem high_expected_not_worstCase_recovery :
    ExpectedRecoveryExistsAt skewedZeroPrior identityBitChannel bitTarget
        constantObserve (99 / 100 : ℚ) ∧
      Not (RecoveryExistsAt identityBitChannel bitTarget constantObserve
        (1 / 2 : ℚ)) := by
  exact ⟨skewedPrior_constantObservation_expectedRecoveryAt_99_100,
    constantObservation_not_recoveryAt_half⟩

/--
The first marginal observation exactly recovers the first declared component.
-/
theorem firstPairObservation_recovers_first :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      pairSupport firstPairTarget firstPairObserve := by
  exact Exists.intro id fun x y hSupport => by
    cases hSupport
    rfl

/--
The second marginal observation exactly recovers the second declared component.
-/
theorem secondPairObservation_recovers_second :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      pairSupport secondPairTarget secondPairObserve := by
  exact Exists.intro id fun x y hSupport => by
    cases hSupport
    rfl

/--
The first marginal observation does not recover the full joint target.
-/
theorem firstPairObservation_not_jointExact :
    Not (
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        pairSupport wholePairTarget firstPairObserve
    ) := by
  intro hExact
  match hExact with
  | Exists.intro decoder hDecoder =>
      have h00 : decoder 0 = ((0, 0) : Bit × Bit) :=
        hDecoder (0, 0) (0, 0) rfl
      have h01 : decoder 0 = ((0, 1) : Bit × Bit) :=
        hDecoder (0, 1) (0, 1) rfl
      rw [h00] at h01
      norm_num at h01

/--
The second marginal observation does not recover the full joint target.
-/
theorem secondPairObservation_not_jointExact :
    Not (
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        pairSupport wholePairTarget secondPairObserve
    ) := by
  intro hExact
  match hExact with
  | Exists.intro decoder hDecoder =>
      have h00 : decoder 0 = ((0, 0) : Bit × Bit) :=
        hDecoder (0, 0) (0, 0) rfl
      have h10 : decoder 0 = ((1, 0) : Bit × Bit) :=
        hDecoder (1, 0) (1, 0) rfl
      rw [h00] at h10
      norm_num at h10

end Examples
end Recovery
end OmegaProper
