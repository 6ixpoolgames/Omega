import OmegaProper.BaselineWitnesses.ExactRecoverySupport
import OmegaProper.Recovery.FiniteChannel

/-!
OmegaProper.Recovery.Deterministic

Deterministic recovery at a declared threshold.

Support-exact recovery is recovered here as the `tau = 1` endpoint of the
source-indexed recovery profile.
-/

namespace OmegaProper
namespace Recovery

universe u v w z

/-- The source-indexed deterministic recovery profile of a decoder. -/
def RecoveryProfile {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D) : X -> ℚ :=
  fun x => Success C target observe decoder x

/-- Pointwise dominance between source-indexed rational profiles. -/
def ProfileDominates {X : Type u} (p q : X -> ℚ) : Prop :=
  forall x, q x <= p x

/-- A declared decoder reaches threshold `tau` for every source state. -/
def DeclaredRecoveryAt {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ)
    (decoder : O -> D) : Prop :=
  forall x, tau <= Success C target observe decoder x

/-- Some deterministic decoder reaches threshold `tau` for every source state. -/
def RecoveryExistsAt {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ) : Prop :=
  exists decoder : O -> D, DeclaredRecoveryAt C target observe tau decoder

theorem recoveryAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hRecovery : RecoveryExistsAt C target observe tau₂) :
    RecoveryExistsAt C target observe tau₁ := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder fun x => le_trans hTau (hDecoder x)

theorem declaredRecoveryAt_implies_exists
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ}
    {decoder : O -> D}
    (hDecoder : DeclaredRecoveryAt C target observe tau decoder) :
    RecoveryExistsAt C target observe tau := by
  exact Exists.intro decoder hDecoder

theorem recoveryAt_one_iff_perfect
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O} :
    RecoveryExistsAt C target observe 1 <->
      exists decoder : O -> D, forall x, Success C target observe decoder x = 1 := by
  constructor
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder fun x =>
          le_antisymm
            (success_le_one C target observe decoder x)
            (hDecoder x)
  · intro hPerfect
    match hPerfect with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder fun x => by
          rw [hDecoder x]

theorem no_recovery_above_one
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D] [Nonempty X]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ}
    (hTau : 1 < tau) :
    Not (RecoveryExistsAt C target observe tau) := by
  intro hRecovery
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      let x : X := Classical.choice (show Nonempty X from inferInstance)
      have hlow : tau <= Success C target observe decoder x := hDecoder x
      have hhigh : Success C target observe decoder x <= 1 :=
        success_le_one C target observe decoder x
      linarith

/--
If a decoder is exact on the positive support, then every source has success
one.
-/
theorem exactDecoder_implies_success_one
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {decoder : O -> D}
    (hExact :
      BaselineWitnesses.ExactRecoverySupport.ExactDecoder
        (PositiveSupport C) target observe decoder) :
    forall x, Success C target observe decoder x = 1 := by
  intro x
  have hFailure :
      FailureMass C target observe decoder x = 0 := by
    classical
    unfold FailureMass
    apply Finset.sum_eq_zero
    intro y _hy
    by_cases hDecode : decoder (observe y) = target x
    · simp [hDecode]
    · have hNotPositive : ¬ 0 < C.prob x y := by
        intro hPos
        exact hDecode (hExact x y hPos)
      have hLeZero : C.prob x y <= 0 := le_of_not_gt hNotPositive
      have hZero : C.prob x y = 0 := le_antisymm hLeZero (C.nonneg x y)
      simp [hDecode, hZero]
  exact (success_eq_one_iff_failureMass_eq_zero C target observe decoder x).mpr hFailure

/--
If every source has success one, the decoder is exact on every positive-support
output.
-/
theorem success_one_implies_exactDecoder
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {decoder : O -> D}
    (hSuccess : forall x, Success C target observe decoder x = 1) :
    BaselineWitnesses.ExactRecoverySupport.ExactDecoder
      (PositiveSupport C) target observe decoder := by
  intro x y hPositive
  unfold PositiveSupport at hPositive
  classical
  by_contra hDecode
  have hFailure :
      FailureMass C target observe decoder x = 0 :=
    (success_eq_one_iff_failureMass_eq_zero C target observe decoder x).mp
      (hSuccess x)
  have hTermNonneg :
      forall z, z ∈ (Finset.univ : Finset Y) ->
        0 <= if decoder (observe z) = target x then 0 else C.prob x z := by
    intro z _hz
    by_cases h : decoder (observe z) = target x
    · simp [h]
    · simp [h, C.nonneg x z]
  have hTermsZero :
      forall z, z ∈ (Finset.univ : Finset Y) ->
        (if decoder (observe z) = target x then 0 else C.prob x z) = 0 := by
    simpa [FailureMass] using
      (Finset.sum_eq_zero_iff_of_nonneg hTermNonneg).mp hFailure
  have hY :
      (if decoder (observe y) = target x then 0 else C.prob x y) = 0 :=
    hTermsZero y (Finset.mem_univ y)
  simp [hDecode] at hY
  linarith

/--
Support-exact decoding is exactly success-one decoding for a fixed decoder.
-/
theorem exactDecoder_iff_success_one
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {decoder : O -> D} :
    BaselineWitnesses.ExactRecoverySupport.ExactDecoder
        (PositiveSupport C) target observe decoder <->
      forall x, Success C target observe decoder x = 1 := by
  constructor
  · exact exactDecoder_implies_success_one
  · exact success_one_implies_exactDecoder

/--
Support-exact recovery is the `tau = 1` endpoint of deterministic threshold
recovery.
-/
theorem supportExactRecovery_iff_recoveryAt_one
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O} :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        (PositiveSupport C) target observe <->
      RecoveryExistsAt C target observe 1 := by
  constructor
  · intro hExact
    match hExact with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder fun x => by
          rw [(exactDecoder_iff_success_one (C := C)
            (target := target) (observe := observe) (decoder := decoder)).mp hDecoder x]
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder
          ((exactDecoder_iff_success_one (C := C)
            (target := target) (observe := observe) (decoder := decoder)).mpr
            (fun x =>
              le_antisymm
                (success_le_one C target observe decoder x)
                (hDecoder x)))

end Recovery
end OmegaProper
