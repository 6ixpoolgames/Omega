import OmegaProper.Recovery.Randomized
import OmegaProper.Recovery.Robust

/-!
OmegaProper.Recovery.CoarseningPermanence

Failure persistence under deterministic observation coarsening.

The observation-refinement theorem says: if a coarse observation factors
through a fine observation, any coarse decoder can be simulated by a fine
decoder. This file records the contrapositive forms used by the bridge ledger:
once an unrestricted recovery threshold fails for an available fine
observation, deterministic coarsening cannot restore it.

Restricted decoder-class variants need an explicit lifting law from coarse
decoders to fine decoders. Without that law, the decoder class itself may be
doing the work.

This file does not define value, agency, identity, or Omega structure.
-/

namespace OmegaProper
namespace Recovery

universe u v w z z'

/--
Restricted deterministic observation refinement.

If each allowed coarse decoder lifts to an allowed fine decoder, then recovery
from the coarse observation implies recovery from the fine observation.
-/
theorem recoveryInAt_mono_observation_refinement
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {AllowedCoarse : (Coarse -> D) -> Prop}
    {AllowedFine : (Fine -> D) -> Prop}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hAllowed :
      forall g decoder,
        (forall y, g (fine y) = coarse y) ->
          AllowedCoarse decoder ->
            AllowedFine (liftDecoder g decoder))
    (hRecovery : RecoveryExistsInAt C target coarse AllowedCoarse tau) :
    RecoveryExistsInAt C target fine AllowedFine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftDecoder g decoder)
            ⟨hAllowed g decoder hFactor hDecoder.1, fun x => by
              rw [lifted_decoder_success_eq (C := C) (target := target)
                (fine := fine) (coarse := coarse) (g := g)
                (decoder := decoder) hFactor x]
              exact hDecoder.2 x⟩

/--
If recovery fails for the available fine observation, deterministic coarsening
cannot restore it for unrestricted deterministic decoders.
-/
theorem recoveryAt_failure_persists_under_coarsening
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
    (hFineFailure : Not (RecoveryExistsAt C target fine tau)) :
    Not (RecoveryExistsAt C target coarse tau) := by
  intro hCoarse
  exact hFineFailure
    (recoveryAt_mono_observation_refinement hRefine hCoarse)

/--
Restricted decoder-class version. The lifting law is explicit: allowed coarse
decoders must become allowed fine decoders after composition with the
coarsening map.
-/
theorem recoveryInAt_failure_persists_under_coarsening
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {AllowedCoarse : (Coarse -> D) -> Prop}
    {AllowedFine : (Fine -> D) -> Prop}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hAllowed :
      forall g decoder,
        (forall y, g (fine y) = coarse y) ->
          AllowedCoarse decoder ->
            AllowedFine (liftDecoder g decoder))
    (hFineFailure :
      Not (RecoveryExistsInAt C target fine AllowedFine tau)) :
    Not (RecoveryExistsInAt C target coarse AllowedCoarse tau) := by
  intro hCoarse
  exact hFineFailure
    (recoveryInAt_mono_observation_refinement hRefine hAllowed hCoarse)

/--
Support-exact failure also persists under deterministic coarsening.
-/
theorem supportExact_failure_persists_under_coarsening
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hFineFailure :
      Not (BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        (PositiveSupport C) target fine)) :
    Not (BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      (PositiveSupport C) target coarse) := by
  intro hCoarse
  exact hFineFailure
    (supportExact_mono_observation_refinement hRefine hCoarse)

/--
Robust recovery failure persists under deterministic coarsening for
unrestricted deterministic decoders.
-/
theorem robustRecoveryAt_failure_persists_under_coarsening
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [DecidableEq D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hFineFailure : Not (RobustRecoveryAt Gamma target fine tau)) :
    Not (RobustRecoveryAt Gamma target coarse tau) := by
  intro hCoarse
  exact hFineFailure
    (robustRecoveryAt_mono_observation_refinement hRefine hCoarse)

/--
Restricted robust version with an explicit allowed-decoder lifting law.
-/
theorem robustRecoveryInAt_failure_persists_under_coarsening
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [DecidableEq D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {AllowedCoarse : (Coarse -> D) -> Prop}
    {AllowedFine : (Fine -> D) -> Prop}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hAllowed :
      forall g decoder,
        (forall y, g (fine y) = coarse y) ->
          AllowedCoarse decoder ->
            AllowedFine (liftDecoder g decoder))
    (hFineFailure :
      Not (RobustRecoveryInAt Gamma target fine AllowedFine tau)) :
    Not (RobustRecoveryInAt Gamma target coarse AllowedCoarse tau) := by
  intro hCoarse
  exact hFineFailure
    (robustRecoveryInAt_mono_observation_refinement
      hRefine hAllowed hCoarse)

/--
Randomized recovery failure persists under deterministic coarsening for
unrestricted randomized decoders.
-/
theorem randomizedRecoveryAt_failure_persists_under_coarsening
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
    (hFineFailure : Not (RandomizedRecoveryAt C target fine tau)) :
    Not (RandomizedRecoveryAt C target coarse tau) := by
  intro hCoarse
  exact hFineFailure
    (randomizedRecoveryAt_mono_observation_refinement hRefine hCoarse)

/--
Restricted randomized observation refinement.

This is separate from the unrestricted theorem because a restricted randomized
decoder class may fail to include lifted coarse decoders.
-/
theorem randomizedRecoveryInAt_mono_observation_refinement
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {AllowedCoarse : RandomizedDecoder Coarse D -> Prop}
    {AllowedFine : RandomizedDecoder Fine D -> Prop}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hAllowed :
      forall g decoder,
        (forall y, g (fine y) = coarse y) ->
          AllowedCoarse decoder ->
            AllowedFine (liftRandomizedDecoder g decoder))
    (hRecovery : RandomizedRecoveryInAt C target coarse AllowedCoarse tau) :
    RandomizedRecoveryInAt C target fine AllowedFine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftRandomizedDecoder g decoder)
            ⟨hAllowed g decoder hFactor hDecoder.1, fun x => by
              rw [lifted_randomizedDecoder_success_eq (C := C)
                (target := target) (fine := fine) (coarse := coarse)
                (g := g) (decoder := decoder) hFactor x]
              exact hDecoder.2 x⟩

/--
Restricted randomized failure persists under coarsening when the randomized
decoder classes respect deterministic lifting.
-/
theorem randomizedRecoveryInAt_failure_persists_under_coarsening
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {AllowedCoarse : RandomizedDecoder Coarse D -> Prop}
    {AllowedFine : RandomizedDecoder Fine D -> Prop}
    {tau : ℚ}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hAllowed :
      forall g decoder,
        (forall y, g (fine y) = coarse y) ->
          AllowedCoarse decoder ->
            AllowedFine (liftRandomizedDecoder g decoder))
    (hFineFailure :
      Not (RandomizedRecoveryInAt C target fine AllowedFine tau)) :
    Not (RandomizedRecoveryInAt C target coarse AllowedCoarse tau) := by
  intro hCoarse
  exact hFineFailure
    (randomizedRecoveryInAt_mono_observation_refinement
      hRefine hAllowed hCoarse)

end Recovery
end OmegaProper
