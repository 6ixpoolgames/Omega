import OmegaProper.Recovery.FiniteChannel

/-!
OmegaProper.Recovery.PolicyContinuation

Finite policy-conditioned continuation over exact rational kernels.

This module defines finite-horizon target-hit profiles under a fixed policy.
It does not define policy optimization, value, agency, or Omega structure.
-/

namespace OmegaProper
namespace Recovery

universe u v

/-- A rational Markov kernel on a finite state space. -/
abbrev RatKernel (X : Type u) [Fintype X] :=
  RatChannel X X

/-- An action-indexed rational transition kernel. -/
structure RatActionKernel (X : Type u) (A : Type v) [Fintype X] where
  prob : X -> A -> X -> ℚ
  nonneg : forall x a x', 0 <= prob x a x'
  row_sum_one : forall x a, (Finset.univ.sum fun x' => prob x a x') = 1

/-- The Markov kernel induced by a deterministic policy. -/
def inducedKernel {X : Type u} {A : Type v} [Fintype X]
    (K : RatActionKernel X A)
    (policy : X -> A) : RatKernel X where
  prob x x' := K.prob x (policy x) x'
  nonneg := by
    intro x x'
    exact K.nonneg x (policy x) x'
  row_sum_one := by
    intro x
    exact K.row_sum_one x (policy x)

theorem inducedKernel_prob
    {X : Type u} {A : Type v} [Fintype X]
    (K : RatActionKernel X A)
    (policy : X -> A)
    (x x' : X) :
    (inducedKernel K policy).prob x x' = K.prob x (policy x) x' := rfl

/--
The induced policy kernel is a valid rational Markov kernel. This theorem names
the validity obligations that are already supplied by the `RatKernel`
constructor.
-/
theorem inducedKernel_valid
    {X : Type u} {A : Type v} [Fintype X]
    (K : RatActionKernel X A)
    (policy : X -> A) :
    (forall x x', 0 <= (inducedKernel K policy).prob x x') ∧
      (forall x,
        (Finset.univ.sum fun x' => (inducedKernel K policy).prob x x') = 1) := by
  constructor
  · intro x x'
    exact (inducedKernel K policy).nonneg x x'
  · intro x
    exact (inducedKernel K policy).row_sum_one x

/-- Finite-horizon probability of hitting a target set within `n` steps. -/
def HitWithin {X : Type u} [Fintype X]
    (K : RatKernel X)
    (target : X -> Prop)
    [DecidablePred target] : Nat -> X -> ℚ
  | 0, x => if target x then 1 else 0
  | n + 1, x =>
      if target x then 1
      else Finset.univ.sum fun x' => K.prob x x' * HitWithin K target n x'

/-- Horizon-indexed hit profile from a declared start state. -/
def HitProfile {X : Type u} [Fintype X]
    (K : RatKernel X)
    (target : X -> Prop)
    [DecidablePred target]
    (start : X) : Nat -> ℚ :=
  fun n => HitWithin K target n start

/--
A fixed deterministic policy reaches threshold `tau` from `start` within the
declared horizon for every action kernel in the ambiguity set.
-/
def RobustPolicyHitAt {X : Type u} {A : Type v} [Fintype X]
    (Gamma : Set (RatActionKernel X A))
    (target : X -> Prop)
    [DecidablePred target]
    (start : X)
    (horizon : Nat)
    (tau : ℚ)
    (policy : X -> A) : Prop :=
  forall K, K ∈ Gamma ->
    tau <= HitWithin (inducedKernel K policy) target horizon start

/--
Some policy in an explicitly declared deterministic policy family reaches
threshold `tau` uniformly over the action-kernel ambiguity set.
-/
def PolicyFamilyRobustHitAt {X : Type u} {A : Type v} [Fintype X]
    (Gamma : Set (RatActionKernel X A))
    (target : X -> Prop)
    [DecidablePred target]
    (Allowed : (X -> A) -> Prop)
    (start : X)
    (horizon : Nat)
    (tau : ℚ) : Prop :=
  exists policy : X -> A,
    Allowed policy ∧ RobustPolicyHitAt Gamma target start horizon tau policy

theorem robustPolicyHitAt_mono_threshold
    {X : Type u} {A : Type v} [Fintype X]
    {Gamma : Set (RatActionKernel X A)}
    {target : X -> Prop}
    [DecidablePred target]
    {start : X}
    {horizon : Nat}
    {tau₁ tau₂ : ℚ}
    {policy : X -> A}
    (hTau : tau₁ <= tau₂)
    (hHit : RobustPolicyHitAt Gamma target start horizon tau₂ policy) :
    RobustPolicyHitAt Gamma target start horizon tau₁ policy := by
  intro K hK
  exact le_trans hTau (hHit K hK)

theorem policyFamilyRobustHitAt_mono_threshold
    {X : Type u} {A : Type v} [Fintype X]
    {Gamma : Set (RatActionKernel X A)}
    {target : X -> Prop}
    [DecidablePred target]
    {Allowed : (X -> A) -> Prop}
    {start : X}
    {horizon : Nat}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hHit : PolicyFamilyRobustHitAt Gamma target Allowed start horizon tau₂) :
    PolicyFamilyRobustHitAt Gamma target Allowed start horizon tau₁ := by
  match hHit with
  | Exists.intro policy hPolicy =>
      exact Exists.intro policy
        ⟨hPolicy.1, robustPolicyHitAt_mono_threshold hTau hPolicy.2⟩

theorem robustPolicyHitAt_mono_ambiguity
    {X : Type u} {A : Type v} [Fintype X]
    {Gamma₁ Gamma₂ : Set (RatActionKernel X A)}
    {target : X -> Prop}
    [DecidablePred target]
    {start : X}
    {horizon : Nat}
    {tau : ℚ}
    {policy : X -> A}
    (hSubset : Gamma₁ ⊆ Gamma₂)
    (hHit : RobustPolicyHitAt Gamma₂ target start horizon tau policy) :
    RobustPolicyHitAt Gamma₁ target start horizon tau policy := by
  intro K hK
  exact hHit K (hSubset hK)

theorem policyFamilyRobustHitAt_mono_ambiguity
    {X : Type u} {A : Type v} [Fintype X]
    {Gamma₁ Gamma₂ : Set (RatActionKernel X A)}
    {target : X -> Prop}
    [DecidablePred target]
    {Allowed : (X -> A) -> Prop}
    {start : X}
    {horizon : Nat}
    {tau : ℚ}
    (hSubset : Gamma₁ ⊆ Gamma₂)
    (hHit : PolicyFamilyRobustHitAt Gamma₂ target Allowed start horizon tau) :
    PolicyFamilyRobustHitAt Gamma₁ target Allowed start horizon tau := by
  match hHit with
  | Exists.intro policy hPolicy =>
      exact Exists.intro policy
        ⟨hPolicy.1, robustPolicyHitAt_mono_ambiguity hSubset hPolicy.2⟩

theorem hitWithin_nonneg {X : Type u} [Fintype X]
    (K : RatKernel X)
    (target : X -> Prop)
    [DecidablePred target] :
    forall n x, 0 <= HitWithin K target n x := by
  intro n
  induction n with
  | zero =>
      intro x
      by_cases h : target x
      · simp [HitWithin, h]
      · simp [HitWithin, h]
  | succ n ih =>
      intro x
      by_cases h : target x
      · simp [HitWithin, h]
      · simp [HitWithin, h]
        exact Finset.sum_nonneg fun x' _hx' =>
          mul_nonneg (K.nonneg x x') (ih x')

theorem hitWithin_le_one {X : Type u} [Fintype X]
    (K : RatKernel X)
    (target : X -> Prop)
    [DecidablePred target] :
    forall n x, HitWithin K target n x <= 1 := by
  intro n
  induction n with
  | zero =>
      intro x
      by_cases h : target x
      · simp [HitWithin, h]
      · simp [HitWithin, h]
  | succ n ih =>
      intro x
      by_cases h : target x
      · simp [HitWithin, h]
      · simp [HitWithin, h]
        calc
          (Finset.univ.sum fun x' => K.prob x x' * HitWithin K target n x')
              <= Finset.univ.sum fun x' => K.prob x x' * 1 := by
                apply Finset.sum_le_sum
                intro x' _hx'
                exact mul_le_mul_of_nonneg_left (ih x') (K.nonneg x x')
          _ = Finset.univ.sum fun x' => K.prob x x' := by
                simp
          _ = 1 := K.row_sum_one x

theorem hitWithin_target_eq_one {X : Type u} [Fintype X]
    (K : RatKernel X)
    (target : X -> Prop)
    [DecidablePred target]
    {n : Nat}
    {x : X}
    (hTarget : target x) :
    HitWithin K target n x = 1 := by
  cases n <;> simp [HitWithin, hTarget]

theorem hitWithin_mono_horizon {X : Type u} [Fintype X]
    (K : RatKernel X)
    (target : X -> Prop)
    [DecidablePred target] :
    forall n x, HitWithin K target n x <= HitWithin K target (n + 1) x := by
  intro n
  induction n with
  | zero =>
      intro x
      by_cases h : target x
      · simp [HitWithin, h]
      · simp [HitWithin, h]
        exact Finset.sum_nonneg fun x' _hx' => by
          by_cases hTarget : target x'
          · simp [hTarget, K.nonneg x x']
          · simp [hTarget]
  | succ n ih =>
      intro x
      by_cases h : target x
      · simp [HitWithin, h]
      · simp [HitWithin, h]
        apply Finset.sum_le_sum
        intro x' _hx'
        by_cases hTarget : target x'
        · calc
            K.prob x x' * HitWithin K target n x'
                <= K.prob x x' * 1 := by
                  exact mul_le_mul_of_nonneg_left
                    (hitWithin_le_one K target n x') (K.nonneg x x')
            _ = if target x' then K.prob x x'
                  else K.prob x x' *
                    Finset.univ.sum
                      (fun x'' => K.prob x' x'' * HitWithin K target n x'') := by
                    simp [hTarget]
        · have hMono :=
            mul_le_mul_of_nonneg_left (ih x') (K.nonneg x x')
          simpa [HitWithin, hTarget] using hMono

theorem selected_action_rows_equal_implies_inducedKernel_prob_equal
    {X : Type u} {A : Type v} [Fintype X]
    {K₁ K₂ : RatActionKernel X A}
    {policy₁ policy₂ : X -> A}
    (hRows : forall x x',
      K₁.prob x (policy₁ x) x' = K₂.prob x (policy₂ x) x') :
    forall x x',
      (inducedKernel K₁ policy₁).prob x x' =
        (inducedKernel K₂ policy₂).prob x x' := by
  intro x x'
  exact hRows x x'

theorem hitWithin_eq_of_kernel_prob_equal
    {X : Type u} [Fintype X]
    {K₁ K₂ : RatKernel X}
    {target : X -> Prop}
    [DecidablePred target]
    (hKernel : forall x x', K₁.prob x x' = K₂.prob x x') :
    forall n x, HitWithin K₁ target n x = HitWithin K₂ target n x := by
  intro n
  induction n with
  | zero =>
      intro x
      by_cases h : target x <;> simp [HitWithin, h]
  | succ n ih =>
      intro x
      by_cases h : target x
      · simp [HitWithin, h]
      · simp [HitWithin, h]
        apply Finset.sum_congr rfl
        intro x' _hx'
        rw [hKernel x x', ih x']

theorem inducedKernel_prob_equal_implies_hitWithin_equal
    {X : Type u} {A : Type v} [Fintype X]
    {K₁ K₂ : RatActionKernel X A}
    {policy₁ policy₂ : X -> A}
    {target : X -> Prop}
    [DecidablePred target]
    (hRows : forall x x',
      K₁.prob x (policy₁ x) x' = K₂.prob x (policy₂ x) x') :
    forall n x,
      HitWithin (inducedKernel K₁ policy₁) target n x =
        HitWithin (inducedKernel K₂ policy₂) target n x := by
  exact hitWithin_eq_of_kernel_prob_equal
    (selected_action_rows_equal_implies_inducedKernel_prob_equal hRows)

end Recovery
end OmegaProper
