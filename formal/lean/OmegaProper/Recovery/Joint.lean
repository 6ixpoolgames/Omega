import OmegaProper.Recovery.Deterministic

/-!
OmegaProper.Recovery.Joint

Safe joint-recovery directions.

This file does not claim that independently chosen observations or panels can
recover a joint target. It only proves same-observation/same-panel directions.
-/

namespace OmegaProper
namespace Recovery

universe u v w₁ w₂ z

/-- Pair two declared targets into one joint declared target. -/
def jointTarget {X : Type u} {D₁ : Type w₁} {D₂ : Type w₂}
    (target₁ : X -> D₁)
    (target₂ : X -> D₂) : X -> D₁ × D₂ :=
  fun x => (target₁ x, target₂ x)

/-- Project the first component of a joint decoder. -/
def firstDecoder {O : Type z} {D₁ : Type w₁} {D₂ : Type w₂}
    (decoder : O -> D₁ × D₂) : O -> D₁ :=
  fun o => (decoder o).1

/-- Project the second component of a joint decoder. -/
def secondDecoder {O : Type z} {D₁ : Type w₁} {D₂ : Type w₂}
    (decoder : O -> D₁ × D₂) : O -> D₂ :=
  fun o => (decoder o).2

/-- Pair two marginal decoders over the same observation type. -/
def pairDecoder {O : Type z} {D₁ : Type w₁} {D₂ : Type w₂}
    (decoder₁ : O -> D₁)
    (decoder₂ : O -> D₂) : O -> D₁ × D₂ :=
  fun o => (decoder₁ o, decoder₂ o)

theorem joint_success_le_first
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    (C : RatChannel X Y)
    (target₁ : X -> D₁)
    (target₂ : X -> D₂)
    (observe : Y -> O)
    (decoder : O -> D₁ × D₂)
    (x : X) :
    Success C (jointTarget target₁ target₂) observe decoder x <=
      Success C target₁ observe (firstDecoder decoder) x := by
  classical
  unfold Success jointTarget firstDecoder
  apply Finset.sum_le_sum
  intro y _hy
  by_cases hPair : decoder (observe y) = (target₁ x, target₂ x)
  · simp [hPair]
  · by_cases hFirst : (decoder (observe y)).1 = target₁ x
    · simp [hPair, hFirst, C.nonneg x y]
    · simp [hPair, hFirst]

theorem joint_success_le_second
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    (C : RatChannel X Y)
    (target₁ : X -> D₁)
    (target₂ : X -> D₂)
    (observe : Y -> O)
    (decoder : O -> D₁ × D₂)
    (x : X) :
    Success C (jointTarget target₁ target₂) observe decoder x <=
      Success C target₂ observe (secondDecoder decoder) x := by
  classical
  unfold Success jointTarget secondDecoder
  apply Finset.sum_le_sum
  intro y _hy
  by_cases hPair : decoder (observe y) = (target₁ x, target₂ x)
  · simp [hPair]
  · by_cases hSecond : (decoder (observe y)).2 = target₂ x
    · simp [hPair, hSecond, C.nonneg x y]
    · simp [hPair, hSecond]

theorem jointRecoveryAt_implies_firstRecoveryAt
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    {C : RatChannel X Y}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {tau : ℚ}
    (hRecovery : RecoveryExistsAt C (jointTarget target₁ target₂) observe tau) :
    RecoveryExistsAt C target₁ observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (firstDecoder decoder) fun x =>
        le_trans (hDecoder x)
          (joint_success_le_first C target₁ target₂ observe decoder x)

theorem jointRecoveryAt_implies_secondRecoveryAt
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    {C : RatChannel X Y}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {tau : ℚ}
    (hRecovery : RecoveryExistsAt C (jointTarget target₁ target₂) observe tau) :
    RecoveryExistsAt C target₂ observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (secondDecoder decoder) fun x =>
        le_trans (hDecoder x)
          (joint_success_le_second C target₁ target₂ observe decoder x)

theorem jointExactDecoder_implies_firstExactDecoder
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    {support : X -> Y -> Prop}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {decoder : O -> D₁ × D₂}
    (hExact :
      BaselineWitnesses.ExactRecoverySupport.ExactDecoder
        support (jointTarget target₁ target₂) observe decoder) :
    BaselineWitnesses.ExactRecoverySupport.ExactDecoder
      support target₁ observe (firstDecoder decoder) := by
  intro x y hSupport
  have hJoint := hExact x y hSupport
  exact congrArg Prod.fst hJoint

theorem jointExactDecoder_implies_secondExactDecoder
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    {support : X -> Y -> Prop}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {decoder : O -> D₁ × D₂}
    (hExact :
      BaselineWitnesses.ExactRecoverySupport.ExactDecoder
        support (jointTarget target₁ target₂) observe decoder) :
    BaselineWitnesses.ExactRecoverySupport.ExactDecoder
      support target₂ observe (secondDecoder decoder) := by
  intro x y hSupport
  have hJoint := hExact x y hSupport
  exact congrArg Prod.snd hJoint

theorem marginalExactDecoders_pair_jointExactDecoder
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    {support : X -> Y -> Prop}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {decoder₁ : O -> D₁}
    {decoder₂ : O -> D₂}
    (hExact₁ :
      BaselineWitnesses.ExactRecoverySupport.ExactDecoder
        support target₁ observe decoder₁)
    (hExact₂ :
      BaselineWitnesses.ExactRecoverySupport.ExactDecoder
        support target₂ observe decoder₂) :
    BaselineWitnesses.ExactRecoverySupport.ExactDecoder
      support (jointTarget target₁ target₂) observe
        (pairDecoder decoder₁ decoder₂) := by
  intro x y hSupport
  exact Prod.ext (hExact₁ x y hSupport) (hExact₂ x y hSupport)

theorem marginalExactRecovery_pair_jointExactRecovery
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    {support : X -> Y -> Prop}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    (hExact₁ :
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        support target₁ observe)
    (hExact₂ :
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        support target₂ observe) :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      support (jointTarget target₁ target₂) observe := by
  match hExact₁ with
  | Exists.intro decoder₁ hDecoder₁ =>
      match hExact₂ with
      | Exists.intro decoder₂ hDecoder₂ =>
          exact Exists.intro (pairDecoder decoder₁ decoder₂)
            (marginalExactDecoders_pair_jointExactDecoder hDecoder₁ hDecoder₂)

end Recovery
end OmegaProper
