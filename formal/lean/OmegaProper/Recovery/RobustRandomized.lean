import OmegaProper.Recovery.Randomized
import OmegaProper.Recovery.Robust

/-!
OmegaProper.Recovery.RobustRandomized

Worst-case recovery over a declared ambiguity set using one randomized decoder.

This combines two already explicit axes:

* robust recovery over a supplied channel ambiguity set;
* randomized decoder recovery with a supplied randomized-decoder class when
  restrictions are needed.

It does not define randomized optimization, value, agency, identity, or Omega
structure.
-/

namespace OmegaProper
namespace Recovery

universe u v w z z'

/--
A fixed randomized decoder reaches threshold `tau` for every source under every
channel in the ambiguity set `Gamma`.
-/
def RobustRandomizedDeclaredRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (Gamma : Set (RatChannel X Y))
    (target : X -> D)
    (observe : Y -> O)
    (tau : Rat)
    (decoder : RandomizedDecoder O D) : Prop :=
  forall C, C ∈ Gamma ->
    RandomizedDeclaredRecoveryAt C target observe tau decoder

/--
Some randomized decoder reaches threshold `tau` uniformly over the declared
ambiguity set.
-/
def RobustRandomizedRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (Gamma : Set (RatChannel X Y))
    (target : X -> D)
    (observe : Y -> O)
    (tau : Rat) : Prop :=
  exists decoder : RandomizedDecoder O D,
    RobustRandomizedDeclaredRecoveryAt Gamma target observe tau decoder

/--
Robust randomized recovery inside an explicitly allowed randomized-decoder
class.

`RobustRandomizedRecoveryAt` is the unrestricted specialization where every
randomized decoder is allowed.
-/
def RobustRandomizedRecoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (Gamma : Set (RatChannel X Y))
    (target : X -> D)
    (observe : Y -> O)
    (Allowed : RandomizedDecoder O D -> Prop)
    (tau : Rat) : Prop :=
  exists decoder : RandomizedDecoder O D,
    Allowed decoder ∧
      RobustRandomizedDeclaredRecoveryAt Gamma target observe tau decoder

theorem robustRandomizedRecoveryAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {tau1 tau2 : Rat}
    (hTau : tau1 <= tau2)
    (hRecovery : RobustRandomizedRecoveryAt Gamma target observe tau2) :
    RobustRandomizedRecoveryAt Gamma target observe tau1 := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder fun C hC x =>
        le_trans hTau (hDecoder C hC x)

theorem robustRandomizedRecoveryInAt_mono_threshold
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : RandomizedDecoder O D -> Prop}
    {tau1 tau2 : Rat}
    (hTau : tau1 <= tau2)
    (hRecovery : RobustRandomizedRecoveryInAt Gamma target observe Allowed tau2) :
    RobustRandomizedRecoveryInAt Gamma target observe Allowed tau1 := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder ⟨hDecoder.1, fun C hC x =>
        le_trans hTau (hDecoder.2 C hC x)⟩

/-- Larger ambiguity sets are harder for one randomized decoder. -/
theorem robustRandomizedRecoveryAt_mono_ambiguity
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {Gamma1 Gamma2 : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {tau : Rat}
    (hSubset : Gamma1 ⊆ Gamma2)
    (hRecovery : RobustRandomizedRecoveryAt Gamma2 target observe tau) :
    RobustRandomizedRecoveryAt Gamma1 target observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder fun C hC =>
        hDecoder C (hSubset hC)

theorem robustRandomizedRecoveryInAt_mono_ambiguity
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {Gamma1 Gamma2 : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : RandomizedDecoder O D -> Prop}
    {tau : Rat}
    (hSubset : Gamma1 ⊆ Gamma2)
    (hRecovery : RobustRandomizedRecoveryInAt Gamma2 target observe Allowed tau) :
    RobustRandomizedRecoveryInAt Gamma1 target observe Allowed tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro decoder ⟨hDecoder.1, fun C hC =>
        hDecoder.2 C (hSubset hC)⟩

theorem robustRandomizedRecoveryAt_iff_robustRandomizedRecoveryInAt_unrestricted
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {tau : Rat} :
    RobustRandomizedRecoveryAt Gamma target observe tau <->
      RobustRandomizedRecoveryInAt Gamma target observe (fun _ => True) tau := by
  constructor
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder ⟨True.intro, hDecoder⟩
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        exact Exists.intro decoder hDecoder.2

theorem singleton_ambiguity_reduces_to_randomizedRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {tau : Rat} :
    RobustRandomizedRecoveryAt ({C} : Set (RatChannel X Y)) target observe tau <->
      RandomizedRecoveryAt C target observe tau := by
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

theorem singleton_ambiguity_reduces_to_randomizedRecoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {Allowed : RandomizedDecoder O D -> Prop}
    {tau : Rat} :
    RobustRandomizedRecoveryInAt ({C} : Set (RatChannel X Y))
        target observe Allowed tau <->
      RandomizedRecoveryInAt C target observe Allowed tau := by
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

theorem robustRecoveryAt_implies_robustRandomizedRecoveryAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D] [DecidableEq D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {tau : Rat}
    (hRecovery : RobustRecoveryAt Gamma target observe tau) :
    RobustRandomizedRecoveryAt Gamma target observe tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (RandomizedDecoder.ofDeterministic decoder) fun C hC x => by
        rw [randomizedSuccess_ofDeterministic C target observe decoder x]
        exact hDecoder C hC x

theorem robustRecoveryInAt_implies_robustRandomizedRecoveryInAt
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D] [DecidableEq D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {AllowedDet : (O -> D) -> Prop}
    {AllowedRand : RandomizedDecoder O D -> Prop}
    {tau : Rat}
    (hAllowed :
      forall decoder,
        AllowedDet decoder ->
          AllowedRand (RandomizedDecoder.ofDeterministic decoder))
    (hRecovery : RobustRecoveryInAt Gamma target observe AllowedDet tau) :
    RobustRandomizedRecoveryInAt Gamma target observe AllowedRand tau := by
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      exact Exists.intro (RandomizedDecoder.ofDeterministic decoder)
        ⟨hAllowed decoder hDecoder.1, fun C hC x => by
          rw [randomizedSuccess_ofDeterministic C target observe decoder x]
          exact hDecoder.2 C hC x⟩

theorem robustRandomizedRecoveryAt_mono_observation_refinement
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {tau : Rat}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hRecovery : RobustRandomizedRecoveryAt Gamma target coarse tau) :
    RobustRandomizedRecoveryAt Gamma target fine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftRandomizedDecoder g decoder) fun C hC x => by
            rw [lifted_randomizedDecoder_success_eq (C := C)
              (target := target) (fine := fine) (coarse := coarse)
              (g := g) (decoder := decoder) hFactor x]
            exact hDecoder C hC x

theorem robustRandomizedRecoveryInAt_mono_observation_refinement
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {AllowedCoarse : RandomizedDecoder Coarse D -> Prop}
    {AllowedFine : RandomizedDecoder Fine D -> Prop}
    {tau : Rat}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hAllowed :
      forall g decoder,
        (forall y, g (fine y) = coarse y) ->
          AllowedCoarse decoder ->
            AllowedFine (liftRandomizedDecoder g decoder))
    (hRecovery :
      RobustRandomizedRecoveryInAt Gamma target coarse AllowedCoarse tau) :
    RobustRandomizedRecoveryInAt Gamma target fine AllowedFine tau := by
  match hRefine with
  | Exists.intro g hFactor =>
      match hRecovery with
      | Exists.intro decoder hDecoder =>
          exact Exists.intro (liftRandomizedDecoder g decoder)
            ⟨hAllowed g decoder hFactor hDecoder.1, fun C hC x => by
              rw [lifted_randomizedDecoder_success_eq (C := C)
                (target := target) (fine := fine) (coarse := coarse)
                (g := g) (decoder := decoder) hFactor x]
              exact hDecoder.2 C hC x⟩

/--
Failure of unrestricted robust randomized recovery persists under deterministic
coarsening.
-/
theorem robustRandomizedRecoveryAt_failure_persists_under_coarsening
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {tau : Rat}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hFineFailure :
      Not (RobustRandomizedRecoveryAt Gamma target fine tau)) :
    Not (RobustRandomizedRecoveryAt Gamma target coarse tau) := by
  intro hCoarse
  exact hFineFailure
    (robustRandomizedRecoveryAt_mono_observation_refinement
      hRefine hCoarse)

/--
Restricted robust randomized failure persists under coarsening when the
randomized decoder classes respect deterministic lifting.
-/
theorem robustRandomizedRecoveryInAt_failure_persists_under_coarsening
    {X : Type u} {Y : Type v} {D : Type w}
    {Fine : Type z} {Coarse : Type z'}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {fine : Y -> Fine}
    {coarse : Y -> Coarse}
    {AllowedCoarse : RandomizedDecoder Coarse D -> Prop}
    {AllowedFine : RandomizedDecoder Fine D -> Prop}
    {tau : Rat}
    (hRefine :
      BaselineWitnesses.NonFactorization.FactorsThrough fine coarse)
    (hAllowed :
      forall g decoder,
        (forall y, g (fine y) = coarse y) ->
          AllowedCoarse decoder ->
            AllowedFine (liftRandomizedDecoder g decoder))
    (hFineFailure :
      Not (RobustRandomizedRecoveryInAt Gamma target fine AllowedFine tau)) :
    Not (RobustRandomizedRecoveryInAt Gamma target coarse AllowedCoarse tau) := by
  intro hCoarse
  exact hFineFailure
    (robustRandomizedRecoveryInAt_mono_observation_refinement
      hRefine hAllowed hCoarse)

end Recovery
end OmegaProper
