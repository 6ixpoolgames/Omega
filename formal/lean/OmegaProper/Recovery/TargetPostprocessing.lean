import OmegaProper.Recovery.Deterministic

/-!
OmegaProper.Recovery.TargetPostprocessing

Recovering a finer declared target entails recovery of any deterministic
post-processing of that target. Joint-to-marginal recovery is an instance with
`Prod.fst` or `Prod.snd`.
-/

namespace OmegaProper
namespace Recovery

universe u v w w' z

/-- Post-process a declared target by a deterministic map. -/
def targetPostprocess {X : Type u} {D : Type w} {E : Type w'}
    (map : D -> E)
    (target : X -> D) : X -> E :=
  fun x => map (target x)

/-- Post-process a decoder by the same deterministic map. -/
def decoderPostprocess {O : Type z} {D : Type w} {E : Type w'}
    (map : D -> E)
    (decoder : O -> D) : O -> E :=
  fun o => map (decoder o)

theorem success_le_targetPostprocess
    {X : Type u} {Y : Type v} {D : Type w} {E : Type w'} {O : Type z}
    [Fintype Y] [DecidableEq D] [DecidableEq E]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (map : D -> E)
    (x : X) :
    Success C target observe decoder x <=
      Success C (targetPostprocess map target) observe
        (decoderPostprocess map decoder) x := by
  classical
  unfold Success targetPostprocess decoderPostprocess
  apply Finset.sum_le_sum
  intro y _hy
  by_cases hFine : decoder (observe y) = target x
  · simp [hFine]
  · by_cases hCoarse : map (decoder (observe y)) = map (target x)
    · simp [hFine, hCoarse, C.nonneg x y]
    · simp [hFine, hCoarse]

theorem declaredRecoveryAt_targetPostprocess
    {X : Type u} {Y : Type v} {D : Type w} {E : Type w'} {O : Type z}
    [Fintype Y] [DecidableEq D] [DecidableEq E]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {decoder : O -> D}
    {map : D -> E}
    {tau : ℚ}
    (hRecovery : DeclaredRecoveryAt C target observe tau decoder) :
    DeclaredRecoveryAt C (targetPostprocess map target) observe tau
      (decoderPostprocess map decoder) := by
  intro x
  exact le_trans (hRecovery x)
    (success_le_targetPostprocess C target observe decoder map x)

theorem recoveryAt_targetPostprocess
    {X : Type u} {Y : Type v} {D : Type w} {E : Type w'} {O : Type z}
    [Fintype Y] [DecidableEq D] [DecidableEq E]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {map : D -> E}
    {tau : ℚ}
    (hRecovery : RecoveryExistsAt C target observe tau) :
    RecoveryExistsAt C (targetPostprocess map target) observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (decoderPostprocess map decoder)
        (declaredRecoveryAt_targetPostprocess hDecoder)

theorem recoveryInAt_targetPostprocess
    {X : Type u} {Y : Type v} {D : Type w} {E : Type w'} {O : Type z}
    [Fintype Y] [DecidableEq D] [DecidableEq E]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {AllowedFine : (O -> D) -> Prop}
    {AllowedCoarse : (O -> E) -> Prop}
    {map : D -> E}
    {tau : ℚ}
    (hAllowed :
      forall {decoder : O -> D},
        AllowedFine decoder ->
        AllowedCoarse (decoderPostprocess map decoder))
    (hRecovery : RecoveryExistsInAt C target observe AllowedFine tau) :
    RecoveryExistsInAt C (targetPostprocess map target) observe
      AllowedCoarse tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (decoderPostprocess map decoder)
        ⟨hAllowed hDecoder.1,
          declaredRecoveryAt_targetPostprocess hDecoder.2⟩

theorem exactDecoder_targetPostprocess
    {X : Type u} {Y : Type v} {D : Type w} {E : Type w'} {O : Type z}
    {support : X -> Y -> Prop}
    {target : X -> D}
    {observe : Y -> O}
    {decoder : O -> D}
    {map : D -> E}
    (hExact :
      BaselineWitnesses.ExactRecoverySupport.ExactDecoder
        support target observe decoder) :
    BaselineWitnesses.ExactRecoverySupport.ExactDecoder
      support (targetPostprocess map target) observe
        (decoderPostprocess map decoder) := by
  intro x y hSupport
  exact congrArg map (hExact x y hSupport)

theorem exactRecovery_targetPostprocess
    {X : Type u} {Y : Type v} {D : Type w} {E : Type w'} {O : Type z}
    {support : X -> Y -> Prop}
    {target : X -> D}
    {observe : Y -> O}
    {map : D -> E}
    (hExact :
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        support target observe) :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      support (targetPostprocess map target) observe := by
  match hExact with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (decoderPostprocess map decoder)
        (exactDecoder_targetPostprocess hDecoder)

end Recovery
end OmegaProper
