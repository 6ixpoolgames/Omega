import OmegaProper.Recovery.TargetPostprocessing

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
  decoderPostprocess Prod.fst decoder

/-- Project the second component of a joint decoder. -/
def secondDecoder {O : Type z} {D₁ : Type w₁} {D₂ : Type w₂}
    (decoder : O -> D₁ × D₂) : O -> D₂ :=
  decoderPostprocess Prod.snd decoder

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
  simpa [jointTarget, firstDecoder, targetPostprocess, decoderPostprocess]
    using
      success_le_targetPostprocess
        C (jointTarget target₁ target₂) observe decoder Prod.fst x

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
  simpa [jointTarget, secondDecoder, targetPostprocess, decoderPostprocess]
    using
      success_le_targetPostprocess
        C (jointTarget target₁ target₂) observe decoder Prod.snd x

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
  simpa [jointTarget, targetPostprocess]
    using
      recoveryAt_targetPostprocess
        (map := Prod.fst)
        (target := jointTarget target₁ target₂)
        hRecovery

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
  simpa [jointTarget, targetPostprocess]
    using
      recoveryAt_targetPostprocess
        (map := Prod.snd)
        (target := jointTarget target₁ target₂)
        hRecovery

/--
For paired decoders over the same observation panel, joint success is bounded
below by the Frechet/union-bound expression `first + second - 1`.

This is intentionally weaker than exact composition. It records the safe
approximate statement: two high-probability marginal recoveries give a joint
lower bound, but failures may be correlated.
-/
theorem pair_success_add_one_ge_marginal_success_sum
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    (C : RatChannel X Y)
    (target₁ : X -> D₁)
    (target₂ : X -> D₂)
    (observe : Y -> O)
    (decoder₁ : O -> D₁)
    (decoder₂ : O -> D₂)
    (x : X) :
    Success C target₁ observe decoder₁ x +
        Success C target₂ observe decoder₂ x <=
      Success C (jointTarget target₁ target₂) observe
          (pairDecoder decoder₁ decoder₂) x + 1 := by
  classical
  calc
    Success C target₁ observe decoder₁ x +
        Success C target₂ observe decoder₂ x
        =
      Finset.univ.sum fun y =>
        (if decoder₁ (observe y) = target₁ x then C.prob x y else 0) +
          if decoder₂ (observe y) = target₂ x then C.prob x y else 0 := by
        unfold Success
        rw [Finset.sum_add_distrib]
    _ <=
      Finset.univ.sum fun y =>
        (if pairDecoder decoder₁ decoder₂ (observe y) =
              (target₁ x, target₂ x) then C.prob x y else 0) +
          C.prob x y := by
        apply Finset.sum_le_sum
        intro y _hy
        by_cases h₁ : decoder₁ (observe y) = target₁ x
        · by_cases h₂ : decoder₂ (observe y) = target₂ x
          · have hPair :
                pairDecoder decoder₁ decoder₂ (observe y) =
                  (target₁ x, target₂ x) := by
              simp [pairDecoder, h₁, h₂]
            simp [h₁, h₂, hPair]
          · have hPair :
                ¬ pairDecoder decoder₁ decoder₂ (observe y) =
                    (target₁ x, target₂ x) := by
              intro hPair
              exact h₂ (congrArg Prod.snd hPair)
            simp [h₁, h₂, hPair]
        · by_cases h₂ : decoder₂ (observe y) = target₂ x
          · have hPair :
                ¬ pairDecoder decoder₁ decoder₂ (observe y) =
                    (target₁ x, target₂ x) := by
              intro hPair
              exact h₁ (congrArg Prod.fst hPair)
            simp [h₁, h₂, hPair]
          · have hPair :
                ¬ pairDecoder decoder₁ decoder₂ (observe y) =
                    (target₁ x, target₂ x) := by
              intro hPair
              exact h₁ (congrArg Prod.fst hPair)
            simp [h₁, h₂, hPair, C.nonneg x y]
    _ =
      Success C (jointTarget target₁ target₂) observe
          (pairDecoder decoder₁ decoder₂) x + 1 := by
        unfold Success jointTarget
        rw [Finset.sum_add_distrib, C.row_sum_one x]

/--
If two marginal decoders over the same observation panel reach thresholds
`tau₁` and `tau₂`, their paired joint decoder reaches threshold
`tau₁ + tau₂ - 1`.
-/
theorem marginalDeclaredRecoveryAt_pair_jointDeclaredRecoveryAt_unionBound
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    {C : RatChannel X Y}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {decoder₁ : O -> D₁}
    {decoder₂ : O -> D₂}
    {tau₁ tau₂ : ℚ}
    (hRecovery₁ : DeclaredRecoveryAt C target₁ observe tau₁ decoder₁)
    (hRecovery₂ : DeclaredRecoveryAt C target₂ observe tau₂ decoder₂) :
    DeclaredRecoveryAt C (jointTarget target₁ target₂) observe
      (tau₁ + tau₂ - 1) (pairDecoder decoder₁ decoder₂) := by
  intro x
  have hBound :=
    pair_success_add_one_ge_marginal_success_sum
      C target₁ target₂ observe decoder₁ decoder₂ x
  have h₁ := hRecovery₁ x
  have h₂ := hRecovery₂ x
  linarith

/--
Existential version of the Frechet/union-bound joint recovery theorem.
-/
theorem marginalRecoveryAt_pair_jointRecoveryAt_unionBound
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    {C : RatChannel X Y}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {tau₁ tau₂ : ℚ}
    (hRecovery₁ : RecoveryExistsAt C target₁ observe tau₁)
    (hRecovery₂ : RecoveryExistsAt C target₂ observe tau₂) :
    RecoveryExistsAt C (jointTarget target₁ target₂) observe
      (tau₁ + tau₂ - 1) := by
  match hRecovery₁ with
  | Exists.intro decoder₁ hDecoder₁ =>
      match hRecovery₂ with
      | Exists.intro decoder₂ hDecoder₂ =>
          exact Exists.intro (pairDecoder decoder₁ decoder₂)
            (marginalDeclaredRecoveryAt_pair_jointDeclaredRecoveryAt_unionBound
              hDecoder₁ hDecoder₂)

/--
Allowed-decoder-class version of the Frechet/union-bound joint recovery
theorem. The joint decoder class must explicitly allow the pairing of the two
marginal decoders.
-/
theorem marginalRecoveryInAt_pair_jointRecoveryInAt_unionBound
    {X : Type u} {Y : Type v} {D₁ : Type w₁} {D₂ : Type w₂} {O : Type z}
    [Fintype Y] [DecidableEq D₁] [DecidableEq D₂]
    {C : RatChannel X Y}
    {target₁ : X -> D₁}
    {target₂ : X -> D₂}
    {observe : Y -> O}
    {Allowed₁ : (O -> D₁) -> Prop}
    {Allowed₂ : (O -> D₂) -> Prop}
    {AllowedJoint : (O -> D₁ × D₂) -> Prop}
    {tau₁ tau₂ : ℚ}
    (hPairAllowed :
      forall {decoder₁ : O -> D₁} {decoder₂ : O -> D₂},
        Allowed₁ decoder₁ ->
        Allowed₂ decoder₂ ->
        AllowedJoint (pairDecoder decoder₁ decoder₂))
    (hRecovery₁ : RecoveryExistsInAt C target₁ observe Allowed₁ tau₁)
    (hRecovery₂ : RecoveryExistsInAt C target₂ observe Allowed₂ tau₂) :
    RecoveryExistsInAt C (jointTarget target₁ target₂) observe AllowedJoint
      (tau₁ + tau₂ - 1) := by
  match hRecovery₁ with
  | Exists.intro decoder₁ hDecoder₁ =>
      match hRecovery₂ with
      | Exists.intro decoder₂ hDecoder₂ =>
          exact Exists.intro (pairDecoder decoder₁ decoder₂)
            ⟨hPairAllowed hDecoder₁.1 hDecoder₂.1,
              marginalDeclaredRecoveryAt_pair_jointDeclaredRecoveryAt_unionBound
                hDecoder₁.2 hDecoder₂.2⟩

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
  simpa [jointTarget, firstDecoder, targetPostprocess, decoderPostprocess]
    using
      exactDecoder_targetPostprocess
        (map := Prod.fst)
        (target := jointTarget target₁ target₂)
        hExact

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
  simpa [jointTarget, secondDecoder, targetPostprocess, decoderPostprocess]
    using
      exactDecoder_targetPostprocess
        (map := Prod.snd)
        (target := jointTarget target₁ target₂)
        hExact

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
