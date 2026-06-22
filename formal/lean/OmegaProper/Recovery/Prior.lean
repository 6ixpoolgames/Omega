import Mathlib.Algebra.BigOperators.Ring.Finset
import OmegaProper.Recovery.Deterministic

/-!
OmegaProper.Recovery.Prior

Prior-relative expected recovery over exact rational finite channels.

This file keeps expected recovery separate from worst-case and robust recovery.
A prior is supplied structure. The results here do not define value, agency,
identity, or Omega structure.
-/

namespace OmegaProper
namespace Recovery

universe u v w z

/-- An exact rational prior on a finite source type. -/
structure RatPrior (X : Type u) [Fintype X] where
  mass : X -> ℚ
  nonneg : forall x, 0 <= mass x
  sum_one : (Finset.univ.sum fun x => mass x) = 1

/-- Expected value of a source-indexed rational profile under a prior. -/
def ExpectedSuccess {X : Type u} [Fintype X]
    (mu : RatPrior X)
    (profile : X -> ℚ) : ℚ :=
  Finset.univ.sum fun x => mu.mass x * profile x

/-- Expected success of a deterministic decoder under a source prior. -/
def ExpectedDecoderSuccess
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    (mu : RatPrior X)
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D) : ℚ :=
  ExpectedSuccess mu (RecoveryProfile C target observe decoder)

/-- A declared decoder reaches expected threshold `tau` under a supplied prior. -/
def ExpectedDeclaredRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    (mu : RatPrior X)
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ)
    (decoder : O -> D) : Prop :=
  tau <= ExpectedDecoderSuccess mu C target observe decoder

/-- Some deterministic decoder reaches expected threshold `tau`. -/
def ExpectedRecoveryExistsAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    (mu : RatPrior X)
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ) : Prop :=
  exists decoder : O -> D,
    ExpectedDeclaredRecoveryAt mu C target observe tau decoder

/-- Expected recovery inside an explicitly allowed deterministic decoder class. -/
def ExpectedRecoveryExistsInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    (mu : RatPrior X)
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (Allowed : (O -> D) -> Prop)
    (tau : ℚ) : Prop :=
  exists decoder : O -> D,
    Allowed decoder ∧ ExpectedDeclaredRecoveryAt mu C target observe tau decoder

theorem expectedSuccess_nonneg {X : Type u} [Fintype X]
    (mu : RatPrior X)
    {profile : X -> ℚ}
    (hProfile : forall x, 0 <= profile x) :
    0 <= ExpectedSuccess mu profile := by
  unfold ExpectedSuccess
  exact Finset.sum_nonneg fun x _hx =>
    mul_nonneg (mu.nonneg x) (hProfile x)

theorem expectedSuccess_le_one {X : Type u} [Fintype X]
    (mu : RatPrior X)
    {profile : X -> ℚ}
    (hProfile : forall x, profile x <= 1) :
    ExpectedSuccess mu profile <= 1 := by
  unfold ExpectedSuccess
  calc
    (Finset.univ.sum fun x => mu.mass x * profile x)
        <= Finset.univ.sum fun x => mu.mass x * 1 := by
          apply Finset.sum_le_sum
          intro x _hx
          exact mul_le_mul_of_nonneg_left (hProfile x) (mu.nonneg x)
    _ = Finset.univ.sum fun x => mu.mass x := by
          simp
    _ = 1 := mu.sum_one

theorem worstCase_threshold_implies_expected_threshold
    {X : Type u} [Fintype X]
    (mu : RatPrior X)
    {profile : X -> ℚ}
    {tau : ℚ}
    (hProfile : forall x, tau <= profile x) :
    tau <= ExpectedSuccess mu profile := by
  unfold ExpectedSuccess
  calc
    tau = tau * 1 := by
      simp
    _ = tau * (Finset.univ.sum fun x => mu.mass x) := by
      rw [mu.sum_one]
    _ = Finset.univ.sum fun x => tau * mu.mass x := by
      rw [Finset.mul_sum]
    _ = Finset.univ.sum fun x => mu.mass x * tau := by
      apply Finset.sum_congr rfl
      intro x _hx
      rw [mul_comm]
    _ <= Finset.univ.sum fun x => mu.mass x * profile x := by
      apply Finset.sum_le_sum
      intro x _hx
      exact mul_le_mul_of_nonneg_left (hProfile x) (mu.nonneg x)

theorem declaredRecoveryAt_implies_expectedRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    {mu : RatPrior X}
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ}
    {decoder : O -> D}
    (hDecoder : DeclaredRecoveryAt C target observe tau decoder) :
    ExpectedDeclaredRecoveryAt mu C target observe tau decoder := by
  exact worstCase_threshold_implies_expected_threshold mu hDecoder

theorem recoveryAt_implies_expectedRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    {mu : RatPrior X}
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ}
    (hRecovery : RecoveryExistsAt C target observe tau) :
    ExpectedRecoveryExistsAt mu C target observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder
        (declaredRecoveryAt_implies_expectedRecoveryAt hDecoder)

theorem recoveryInAt_implies_expectedRecoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    {mu : RatPrior X}
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : (O -> D) -> Prop}
    {tau : ℚ}
    (hRecovery : RecoveryExistsInAt C target observe Allowed tau) :
    ExpectedRecoveryExistsInAt mu C target observe Allowed tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder
        ⟨hDecoder.1, declaredRecoveryAt_implies_expectedRecoveryAt hDecoder.2⟩

theorem expectedRecoveryAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    {mu : RatPrior X}
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hRecovery : ExpectedRecoveryExistsAt mu C target observe tau₂) :
    ExpectedRecoveryExistsAt mu C target observe tau₁ := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder (le_trans hTau hDecoder)

theorem expectedRecoveryInAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    {mu : RatPrior X}
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : (O -> D) -> Prop}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hRecovery : ExpectedRecoveryExistsInAt mu C target observe Allowed tau₂) :
    ExpectedRecoveryExistsInAt mu C target observe Allowed tau₁ := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder ⟨hDecoder.1, le_trans hTau hDecoder.2⟩

theorem expectedRecoveryAt_iff_expectedRecoveryInAt_unrestricted
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype X] [Fintype Y] [DecidableEq D]
    {mu : RatPrior X}
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ} :
    ExpectedRecoveryExistsAt mu C target observe tau <->
      ExpectedRecoveryExistsInAt mu C target observe (fun _ => True) tau := by
  constructor
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder ⟨True.intro, hDecoder⟩
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder hDecoder.2

/-- Point-mass prior on a finite source. -/
def pointMassPrior {X : Type u} [Fintype X] [DecidableEq X]
    (x₀ : X) : RatPrior X where
  mass x := if x = x₀ then 1 else 0
  nonneg := by
    intro x
    by_cases h : x = x₀
    · simp [h]
    · simp [h]
  sum_one := by
    classical
    rw [Finset.sum_eq_single x₀]
    · simp
    · intro x _hx hne
      simp [hne]
    · intro hmem
      exact False.elim (hmem (Finset.mem_univ x₀))

theorem expectedSuccess_pointMass {X : Type u} [Fintype X] [DecidableEq X]
    (x₀ : X)
    (profile : X -> ℚ) :
    ExpectedSuccess (pointMassPrior x₀) profile = profile x₀ := by
  classical
  unfold ExpectedSuccess pointMassPrior
  rw [Finset.sum_eq_single x₀]
  · simp
  · intro x _hx hne
    simp [hne]
  · intro hmem
    exact False.elim (hmem (Finset.mem_univ x₀))

end Recovery
end OmegaProper
