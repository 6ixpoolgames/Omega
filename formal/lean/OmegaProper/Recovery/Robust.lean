import OmegaProper.Recovery.ObservationRefinement

/-!
OmegaProper.Recovery.Robust

Worst-case recovery over a declared ambiguity set of exact rational channels.

This file keeps uncertainty explicit: robust recovery means that one decoder
meets the declared threshold for every channel in a supplied set. It does not
define priors, Bayes risk, value, agency, identity, or Omega structure.
-/

namespace OmegaProper
namespace Recovery

universe u v w z z'

/--
A fixed deterministic decoder reaches threshold `tau` for every source under
every channel in the ambiguity set `Gamma`.
-/
def RobustDeclaredRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (Gamma : Set (RatChannel X Y))
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ)
    (decoder : O -> D) : Prop :=
  forall C, C ∈ Gamma -> DeclaredRecoveryAt C target observe tau decoder

/--
Some deterministic decoder reaches threshold `tau` uniformly over the declared
ambiguity set.
-/
def RobustRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (Gamma : Set (RatChannel X Y))
    (target : X -> D)
    (observe : Y -> O)
    (tau : ℚ) : Prop :=
  exists decoder : O -> D,
    RobustDeclaredRecoveryAt Gamma target observe tau decoder

/--
Robust recovery inside an explicitly allowed deterministic decoder class.

`RobustRecoveryAt` is the unrestricted specialization where every deterministic
decoder is allowed.
-/
def RobustRecoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (Gamma : Set (RatChannel X Y))
    (target : X -> D)
    (observe : Y -> O)
    (Allowed : (O -> D) -> Prop)
    (tau : ℚ) : Prop :=
  exists decoder : O -> D,
    Allowed decoder ∧ RobustDeclaredRecoveryAt Gamma target observe tau decoder

theorem robustRecoveryAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hRecovery : RobustRecoveryAt Gamma target observe tau₂) :
    RobustRecoveryAt Gamma target observe tau₁ := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder fun C hC x =>
        le_trans hTau (hDecoder C hC x)

theorem robustRecoveryInAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : (O -> D) -> Prop}
    {tau₁ tau₂ : ℚ}
    (hTau : tau₁ <= tau₂)
    (hRecovery : RobustRecoveryInAt Gamma target observe Allowed tau₂) :
    RobustRecoveryInAt Gamma target observe Allowed tau₁ := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder ⟨hDecoder.1, fun C hC x =>
        le_trans hTau (hDecoder.2 C hC x)⟩

/-- Larger ambiguity sets are harder: a decoder robust on `Gamma₂` is robust on
any subset `Gamma₁`. -/
theorem robustRecoveryAt_mono_ambiguity
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {Gamma₁ Gamma₂ : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ}
    (hSubset : Gamma₁ ⊆ Gamma₂)
    (hRecovery : RobustRecoveryAt Gamma₂ target observe tau) :
    RobustRecoveryAt Gamma₁ target observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder fun C hC =>
        hDecoder C (hSubset hC)

theorem robustRecoveryInAt_mono_ambiguity
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {Gamma₁ Gamma₂ : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : (O -> D) -> Prop}
    {tau : ℚ}
    (hSubset : Gamma₁ ⊆ Gamma₂)
    (hRecovery : RobustRecoveryInAt Gamma₂ target observe Allowed tau) :
    RobustRecoveryInAt Gamma₁ target observe Allowed tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder ⟨hDecoder.1, fun C hC =>
        hDecoder.2 C (hSubset hC)⟩

theorem robustRecoveryAt_iff_robustRecoveryInAt_unrestricted
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ} :
    RobustRecoveryAt Gamma target observe tau <->
      RobustRecoveryInAt Gamma target observe (fun _ => True) tau := by
  constructor
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder ⟨True.intro, hDecoder⟩
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder hDecoder.2

theorem singleton_ambiguity_reduces_to_recoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : ℚ} :
    RobustRecoveryAt ({C} : Set (RatChannel X Y)) target observe tau <->
      RecoveryExistsAt C target observe tau := by
  constructor
  · intro hRobust
    match hRobust with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder (hDecoder C (by simp))
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder fun C' hC' => by
          have hEq : C' = C := by simpa using hC'
          subst C'
          exact hDecoder

theorem singleton_ambiguity_reduces_to_recoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : (O -> D) -> Prop}
    {tau : ℚ} :
    RobustRecoveryInAt ({C} : Set (RatChannel X Y)) target observe Allowed tau <->
      RecoveryExistsInAt C target observe Allowed tau := by
  constructor
  · intro hRobust
    match hRobust with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder ⟨hDecoder.1, hDecoder.2 C (by simp)⟩
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder ⟨hDecoder.1, fun C' hC' => by
          have hEq : C' = C := by simpa using hC'
          subst C'
          exact hDecoder.2⟩

theorem robustRecoveryAt_mono_observation_refinement
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
    (hRecovery : RobustRecoveryAt Gamma target coarse tau) :
    RobustRecoveryAt Gamma target fine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftDecoder g decoder) fun C hC x => by
            rw [lifted_decoder_success_eq (C := C) (target := target)
              (fine := fine) (coarse := coarse) (g := g)
              (decoder := decoder) hFactor x]
            exact hDecoder C hC x

theorem robustRecoveryInAt_mono_observation_refinement
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
    (hRecovery : RobustRecoveryInAt Gamma target coarse AllowedCoarse tau) :
    RobustRecoveryInAt Gamma target fine AllowedFine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftDecoder g decoder)
            ⟨hAllowed g decoder hFactor hDecoder.1, fun C hC x => by
              rw [lifted_decoder_success_eq (C := C) (target := target)
                (fine := fine) (coarse := coarse) (g := g)
                (decoder := decoder) hFactor x]
              exact hDecoder.2 C hC x⟩

end Recovery
end OmegaProper
