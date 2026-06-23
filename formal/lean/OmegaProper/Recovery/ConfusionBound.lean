import OmegaProper.Recovery.Deterministic

/-!
OmegaProper.Recovery.ConfusionBound

Quantitative recovery obstruction from shared observed mass.

If two target-distinct sources put at least `epsilon` probability mass on
outputs with the same observed label, then a deterministic decoder must be
wrong on at least that mass for one of the two sources. Thus worst-case
deterministic threshold recovery above `1 - epsilon` is impossible.

This is a finite bridge from consequence/observation confusion to graded
recovery. It does not define value, agency, identity, or Omega structure.
-/

namespace OmegaProper
namespace Recovery

universe u v w z

/--
If an output is decoded to the wrong target value, its channel mass contributes
to the deterministic failure mass for that source.
-/
theorem wrong_observation_mass_le_failureMass
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X)
    (y : Y)
    (hWrong : decoder (observe y) ≠ target x) :
    C.prob x y <= FailureMass C target observe decoder x := by
  classical
  unfold FailureMass
  have hTermNonneg :
      forall z, z ∈ (Finset.univ : Finset Y) ->
        0 <= if decoder (observe z) = target x then 0 else C.prob x z := by
    intro z _hz
    by_cases h : decoder (observe z) = target x
    · simp [h]
    · simp [h, C.nonneg x z]
  have hSingle :
      (if decoder (observe y) = target x then 0 else C.prob x y) <=
        Finset.univ.sum
          (fun z => if decoder (observe z) = target x then 0 else C.prob x z) :=
    Finset.single_le_sum hTermNonneg (Finset.mem_univ y)
  simpa [hWrong] using hSingle

/--
If two target-distinct sources put at least `epsilon` mass on outputs with the
same observed label, no deterministic decoder can recover above threshold
`1 - epsilon`.
-/
theorem shared_observation_mass_blocks_recoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {x₀ x₁ : X}
    {y₀ y₁ : Y}
    {epsilon tau : ℚ}
    (hTarget : target x₀ ≠ target x₁)
    (hObserve : observe y₀ = observe y₁)
    (hMass₀ : epsilon <= C.prob x₀ y₀)
    (hMass₁ : epsilon <= C.prob x₁ y₁)
    (hTau : 1 - epsilon < tau) :
    Not (RecoveryExistsAt C target observe tau) := by
  intro hRecovery
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      by_cases hDecode₀ : decoder (observe y₀) = target x₀
      · have hWrong₁ : decoder (observe y₁) ≠ target x₁ := by
          intro hDecode₁
          apply hTarget
          rw [← hDecode₀, hObserve, hDecode₁]
        have hFailMass :
            epsilon <= FailureMass C target observe decoder x₁ :=
          le_trans hMass₁
            (wrong_observation_mass_le_failureMass
              C target observe decoder x₁ y₁ hWrong₁)
        have hSum := success_add_failureMass C target observe decoder x₁
        have hThreshold := hDecoder x₁
        linarith
      · have hWrong₀ : decoder (observe y₀) ≠ target x₀ := hDecode₀
        have hFailMass :
            epsilon <= FailureMass C target observe decoder x₀ :=
          le_trans hMass₀
            (wrong_observation_mass_le_failureMass
              C target observe decoder x₀ y₀ hWrong₀)
        have hSum := success_add_failureMass C target observe decoder x₀
        have hThreshold := hDecoder x₀
        linarith

end Recovery
end OmegaProper
