import OmegaProper.Recovery.ObservationRefinement

/-!
OmegaProper.Recovery.Randomized

Randomized decoders for finite recovery profiles.

This file only adds the decoder class and deterministic embedding. It does not
define randomized optimization or a global randomized capacity.
-/

namespace OmegaProper
namespace Recovery

universe u v w z

/-- A finite rational randomized decoder from observations to declared values. -/
structure RandomizedDecoder (O : Type z) (D : Type w) [Fintype D] where
  prob : O -> D -> ℚ
  nonneg : forall o d, 0 <= prob o d
  row_sum_one : forall o, (Finset.univ.sum fun d => prob o d) = 1

namespace RandomizedDecoder

theorem prob_le_one {O : Type z} {D : Type w} [Fintype D]
    (decoder : RandomizedDecoder O D)
    (o : O)
    (d : D) :
    decoder.prob o d <= 1 := by
  have hle :
      decoder.prob o d <=
        Finset.univ.sum fun d' => decoder.prob o d' := by
    exact Finset.single_le_sum
      (fun d' _hd' => decoder.nonneg o d')
      (Finset.mem_univ d)
  rw [decoder.row_sum_one o] at hle
  exact hle

/-- Embed a deterministic decoder as a point-mass randomized decoder. -/
def ofDeterministic {O : Type z} {D : Type w} [Fintype D] [DecidableEq D]
    (decoder : O -> D) : RandomizedDecoder O D where
  prob o d := if d = decoder o then 1 else 0
  nonneg := by
    intro o d
    by_cases h : d = decoder o
    · simp [h]
    · simp [h]
  row_sum_one := by
    intro o
    classical
    rw [Finset.sum_eq_single (decoder o)]
    · simp
    · intro d _hd hne
      simp [hne]
    · intro hmem
      exact False.elim (hmem (Finset.mem_univ (decoder o)))

end RandomizedDecoder

/-- Per-source success for a randomized decoder. -/
def RandomizedSuccess {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : RandomizedDecoder O D)
    (x : X) : ℚ :=
  Finset.univ.sum fun y =>
    C.prob x y * decoder.prob (observe y) (target x)

/-- A declared randomized decoder reaches threshold `tau` for every source. -/
def RandomizedDeclaredRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ)
    (decoder : RandomizedDecoder O D) : Prop :=
  forall x, tau <= RandomizedSuccess C target observe decoder x

/-- Some randomized decoder reaches threshold `tau` for every source state. -/
def RandomizedRecoveryAt {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ) : Prop :=
  exists decoder : RandomizedDecoder O D,
    RandomizedDeclaredRecoveryAt C target observe tau decoder

/--
Some decoder from an explicitly allowed randomized decoder class reaches
threshold `tau` for every source state.

`RandomizedRecoveryAt` is the unrestricted specialization where every
randomized decoder is allowed.
-/
def RandomizedRecoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (Allowed : RandomizedDecoder O D -> Prop)
    (tau : ℚ) : Prop :=
  exists decoder : RandomizedDecoder O D,
    Allowed decoder ∧ RandomizedDeclaredRecoveryAt C target observe tau decoder

/-- Lift a randomized decoder along a deterministic observation post-map. -/
def liftRandomizedDecoder {Fine : Type z} {Coarse : Type z'} {D : Type w}
    [Fintype D]
    (g : Fine -> Coarse)
    (decoder : RandomizedDecoder Coarse D) : RandomizedDecoder Fine D where
  prob fine d := decoder.prob (g fine) d
  nonneg := by
    intro fine d
    exact decoder.nonneg (g fine) d
  row_sum_one := by
    intro fine
    exact decoder.row_sum_one (g fine)

theorem randomizedSuccess_nonneg
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : RandomizedDecoder O D)
    (x : X) :
    0 <= RandomizedSuccess C target observe decoder x := by
  unfold RandomizedSuccess
  exact Finset.sum_nonneg fun y _hy =>
    mul_nonneg (C.nonneg x y) (decoder.nonneg (observe y) (target x))

theorem randomizedSuccess_le_one
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : RandomizedDecoder O D)
    (x : X) :
    RandomizedSuccess C target observe decoder x <= 1 := by
  unfold RandomizedSuccess
  calc
    (Finset.univ.sum fun y =>
        C.prob x y * decoder.prob (observe y) (target x))
        <= Finset.univ.sum fun y => C.prob x y * 1 := by
          apply Finset.sum_le_sum
          intro y _hy
          exact mul_le_mul_of_nonneg_left
            (RandomizedDecoder.prob_le_one decoder (observe y) (target x))
            (C.nonneg x y)
    _ = Finset.univ.sum fun y => C.prob x y := by
          simp
    _ = 1 := C.row_sum_one x

theorem randomizedSuccess_ofDeterministic
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) :
    RandomizedSuccess C target observe
        (RandomizedDecoder.ofDeterministic decoder) x =
      Success C target observe decoder x := by
  classical
  unfold RandomizedSuccess Success RandomizedDecoder.ofDeterministic
  apply Finset.sum_congr rfl
  intro y _hy
  change
    C.prob x y * (if target x = decoder (observe y) then (1 : ℚ) else 0) =
      if decoder (observe y) = target x then C.prob x y else 0
  by_cases h : decoder (observe y) = target x
  · have h' : target x = decoder (observe y) := h.symm
    rw [if_pos h', if_pos h, mul_one]
  · have h' : ¬ target x = decoder (observe y) := by
      intro hs
      exact h hs.symm
    rw [if_neg h', if_neg h, mul_zero]

theorem lifted_randomizedDecoder_success_eq
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {g : Fine -> Coarse}
    {decoder : RandomizedDecoder Coarse D}
    (hFactor : forall y, g (fine y) = coarse y)
    (x : X) :
    RandomizedSuccess C target fine (liftRandomizedDecoder g decoder) x =
      RandomizedSuccess C target coarse decoder x := by
  unfold RandomizedSuccess liftRandomizedDecoder
  apply Finset.sum_congr rfl
  intro y _hy
  change
    C.prob x y * decoder.prob (g (fine y)) (target x) =
      C.prob x y * decoder.prob (coarse y) (target x)
  rw [hFactor y]

theorem recoveryAt_implies_randomizedRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ}
    (hRecovery : RecoveryExistsAt C target observe tau) :
    RandomizedRecoveryAt C target observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (RandomizedDecoder.ofDeterministic decoder) fun x => by
        rw [randomizedSuccess_ofDeterministic C target observe decoder x]
        exact hDecoder x

theorem recoveryInAt_implies_randomizedRecoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ}
    {AllowedDet : (O -> D) -> Prop}
    {AllowedRand : RandomizedDecoder O D -> Prop}
    (hAllowed :
      forall decoder,
        AllowedDet decoder ->
          AllowedRand (RandomizedDecoder.ofDeterministic decoder))
    (hRecovery : RecoveryExistsInAt C target observe AllowedDet tau) :
    RandomizedRecoveryInAt C target observe AllowedRand tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (RandomizedDecoder.ofDeterministic decoder)
        ⟨hAllowed decoder hDecoder.1, fun x => by
          rw [randomizedSuccess_ofDeterministic C target observe decoder x]
          exact hDecoder.2 x⟩

theorem randomizedRecoveryAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hRecovery : RandomizedRecoveryAt C target observe tau₂) :
    RandomizedRecoveryAt C target observe tau₁ := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder fun x => le_trans hTau (hDecoder x)

theorem randomizedRecoveryInAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : RandomizedDecoder O D -> Prop}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hRecovery : RandomizedRecoveryInAt C target observe Allowed tau₂) :
    RandomizedRecoveryInAt C target observe Allowed tau₁ := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder ⟨hDecoder.1, fun x =>
        le_trans hTau (hDecoder.2 x)⟩

theorem randomizedRecoveryAt_iff_randomizedRecoveryInAt_unrestricted
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ} :
    RandomizedRecoveryAt C target observe tau <->
      RandomizedRecoveryInAt C target observe (fun _ => True) tau := by
  constructor
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder ⟨True.intro, hDecoder⟩
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder hDecoder.2

theorem randomizedRecoveryAt_mono_observation_refinement
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hRecovery : RandomizedRecoveryAt C target coarse tau) :
    RandomizedRecoveryAt C target fine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftRandomizedDecoder g decoder) fun x => by
            rw [lifted_randomizedDecoder_success_eq (C := C) (target := target)
              (fine := fine) (coarse := coarse) (g := g)
              (decoder := decoder) hFactor x]
            exact hDecoder x

end Recovery
end OmegaProper
