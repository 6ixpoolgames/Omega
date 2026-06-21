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

/-- Some randomized decoder reaches threshold `tau` for every source state. -/
def RandomizedRecoveryAt {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ) : Prop :=
  exists decoder : RandomizedDecoder O D,
    forall x, tau <= RandomizedSuccess C target observe decoder x

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
