import OmegaProper.BaselineWitnesses.NonFactorization
import OmegaProper.Recovery.Deterministic

/-!
OmegaProper.Recovery.ObservationRefinement

Deterministic observation refinement for recovery profiles.

If a coarse observation factors through a fine observation, any coarse decoder
can be lifted to the fine observation without changing per-source success.
This is the deterministic data-processing direction used by the recovery layer.
-/

namespace OmegaProper
namespace Recovery

universe u v w z z'

/-- Lift a decoder along a deterministic observation post-map. -/
def liftDecoder {Fine : Type z} {Coarse : Type z'} {D : Type w}
    (g : Fine -> Coarse)
    (decoder : Coarse -> D) : Fine -> D :=
  fun fine => decoder (g fine)

theorem lifted_decoder_success_eq
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {g : Fine -> Coarse}
    {decoder : Coarse -> D}
    (hFactor : forall y, g (fine y) = coarse y)
    (x : X) :
    Success C target fine (liftDecoder g decoder) x =
      Success C target coarse decoder x := by
  classical
  unfold Success liftDecoder
  apply Finset.sum_congr rfl
  intro y _hy
  simp [hFactor y]

theorem recoveryAt_mono_observation_refinement
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hRecovery : RecoveryExistsAt C target coarse tau) :
    RecoveryExistsAt C target fine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftDecoder g decoder) fun x => by
            rw [lifted_decoder_success_eq (C := C) (target := target)
              (fine := fine) (coarse := coarse) (g := g)
              (decoder := decoder) hFactor x]
            exact hDecoder x

theorem supportExact_mono_observation_refinement
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hExact :
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        (PositiveSupport C) target coarse) :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      (PositiveSupport C) target fine := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hExact with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftDecoder g decoder) fun x y hSupport => by
            unfold liftDecoder
            rw [hFactor y]
            exact hDecoder x y hSupport

end Recovery
end OmegaProper
