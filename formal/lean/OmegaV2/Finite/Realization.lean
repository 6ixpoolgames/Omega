import Mathlib.Data.Set.Basic

/-!
OmegaV2.Finite.Realization

Witness-retaining May and Robust realization fibers. Robust realization uses
one policy across every environment in a declared scope. The outcome function
supplies the deterministic finite run witness for each policy/environment pair.

This file does not select a maximal face and does not define identity, agency,
standing, value, or moral license.
-/

namespace OmegaV2
namespace Finite

universe u v w x

/-- Witnesses jointly realizing every candidate in a family. -/
def Real
    {Witness : Type u}
    {Candidate : Type v}
    (realizes : Witness -> Candidate -> Prop)
    (family : Set Candidate) :
    Set Witness :=
  {witness | forall candidate, candidate ∈ family -> realizes witness candidate}

/-- May compatibility is nonemptiness of the complete realization fiber. -/
def MayCompatible
    {Witness : Type u}
    {Candidate : Type v}
    (realizes : Witness -> Candidate -> Prop)
    (family : Set Candidate) : Prop :=
  (Real realizes family).Nonempty

/--
Policies whose deterministic outcome realizes the family in every environment
of the declared scope.
-/
def Secure
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    (outcome : Policy -> Environment -> Witness)
    (realizes : Witness -> Candidate -> Prop)
    (environments : Set Environment)
    (family : Set Candidate) :
    Set Policy :=
  {policy |
    forall environment,
      environment ∈ environments ->
      outcome policy environment ∈ Real realizes family}

/-- Robust compatibility is nonemptiness of the securing-policy fiber. -/
def RobustCompatible
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    (outcome : Policy -> Environment -> Witness)
    (realizes : Witness -> Candidate -> Prop)
    (environments : Set Environment)
    (family : Set Candidate) : Prop :=
  (Secure outcome realizes environments family).Nonempty

/-- Adding candidates can only remove realization witnesses. -/
theorem real_antitone
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small large : Set Candidate}
    (hSubset : small ⊆ large) :
    Real realizes large ⊆ Real realizes small := by
  intro witness hLarge candidate hCandidate
  exact hLarge candidate (hSubset hCandidate)

/-- May compatibility is downward closed under candidate removal. -/
theorem mayCompatible_downward
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small large : Set Candidate}
    (hSubset : small ⊆ large)
    (hCompatible : MayCompatible realizes large) :
    MayCompatible realizes small := by
  obtain ⟨witness, hWitness⟩ := hCompatible
  exact ⟨witness, real_antitone hSubset hWitness⟩

/-- Realization of a union is intersection of the two realization fibers. -/
theorem real_union
    {Witness : Type u}
    {Candidate : Type v}
    (realizes : Witness -> Candidate -> Prop)
    (left right : Set Candidate) :
    Real realizes (left ∪ right) =
      Real realizes left ∩ Real realizes right := by
  ext witness
  constructor
  · intro hBoth
    exact ⟨
      (fun candidate hLeft => hBoth candidate (Or.inl hLeft)),
      (fun candidate hRight => hBoth candidate (Or.inr hRight))
    ⟩
  · intro hSeparate candidate hCandidate
    cases hCandidate with
    | inl hLeft => exact hSeparate.1 candidate hLeft
    | inr hRight => exact hSeparate.2 candidate hRight

/-- Adding candidates can only remove securing policies. -/
theorem secure_candidate_antitone
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {environments : Set Environment}
    {small large : Set Candidate}
    (hSubset : small ⊆ large) :
    Secure outcome realizes environments large ⊆
      Secure outcome realizes environments small := by
  intro policy hSecure environment hEnvironment
  exact real_antitone hSubset (hSecure environment hEnvironment)

/-- Adding environments can only remove securing policies. -/
theorem secure_environment_antitone
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {smallEnvironment largeEnvironment : Set Environment}
    {family : Set Candidate}
    (hSubset : smallEnvironment ⊆ largeEnvironment) :
    Secure outcome realizes largeEnvironment family ⊆
      Secure outcome realizes smallEnvironment family := by
  intro policy hSecure environment hEnvironment
  exact hSecure environment (hSubset hEnvironment)

/-- Robust compatibility is downward closed under candidate removal. -/
theorem robustCompatible_candidate_downward
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {environments : Set Environment}
    {small large : Set Candidate}
    (hSubset : small ⊆ large)
    (hCompatible :
      RobustCompatible outcome realizes environments large) :
    RobustCompatible outcome realizes environments small := by
  obtain ⟨policy, hPolicy⟩ := hCompatible
  exact ⟨policy, secure_candidate_antitone hSubset hPolicy⟩

/-- Robustness over a larger environment scope implies robustness over a subset. -/
theorem robustCompatible_environment_downward
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {smallEnvironment largeEnvironment : Set Environment}
    {family : Set Candidate}
    (hSubset : smallEnvironment ⊆ largeEnvironment)
    (hCompatible :
      RobustCompatible outcome realizes largeEnvironment family) :
    RobustCompatible outcome realizes smallEnvironment family := by
  obtain ⟨policy, hPolicy⟩ := hCompatible
  exact ⟨policy, secure_environment_antitone hSubset hPolicy⟩

/-- Securing a union is securing both component families. -/
theorem secure_union
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    (outcome : Policy -> Environment -> Witness)
    (realizes : Witness -> Candidate -> Prop)
    (environments : Set Environment)
    (left right : Set Candidate) :
    Secure outcome realizes environments (left ∪ right) =
      Secure outcome realizes environments left ∩
        Secure outcome realizes environments right := by
  ext policy
  constructor
  · intro hBoth
    constructor
    · intro environment hEnvironment
      have hRun := hBoth environment hEnvironment
      exact (Set.ext_iff.mp (real_union realizes left right)
        (outcome policy environment)).mp hRun |>.1
    · intro environment hEnvironment
      have hRun := hBoth environment hEnvironment
      exact (Set.ext_iff.mp (real_union realizes left right)
        (outcome policy environment)).mp hRun |>.2
  · intro hSeparate environment hEnvironment
    have hLeft := hSeparate.1 environment hEnvironment
    have hRight := hSeparate.2 environment hEnvironment
    exact (Set.ext_iff.mp (real_union realizes left right)
      (outcome policy environment)).mpr ⟨hLeft, hRight⟩

/--
Over a nonempty environment scope, every robustly compatible family is
May-compatible.
-/
theorem robustCompatible_implies_mayCompatible
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {environments : Set Environment}
    {family : Set Candidate}
    (hEnvironment : environments.Nonempty)
    (hRobust : RobustCompatible outcome realizes environments family) :
    MayCompatible realizes family := by
  obtain ⟨environment, hEnvironmentMember⟩ := hEnvironment
  obtain ⟨policy, hPolicy⟩ := hRobust
  exact ⟨
    outcome policy environment,
    hPolicy environment hEnvironmentMember
  ⟩

/-- Restrict a realization witness to a smaller candidate family. -/
def restrictReal
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small large : Set Candidate}
    (hSubset : small ⊆ large) :
    Real realizes large -> Real realizes small :=
  fun witness => ⟨witness.1, real_antitone hSubset witness.2⟩

theorem restrictReal_identity
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {family : Set Candidate}
    (witness : Real realizes family) :
    restrictReal (Set.Subset.rfl : family ⊆ family) witness = witness := by
  rfl

theorem restrictReal_composition
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small middle large : Set Candidate}
    (hSmallMiddle : small ⊆ middle)
    (hMiddleLarge : middle ⊆ large)
    (witness : Real realizes large) :
    restrictReal hSmallMiddle (restrictReal hMiddleLarge witness) =
      restrictReal
        (fun _ hSmall => hMiddleLarge (hSmallMiddle hSmall))
        witness := by
  rfl

/-- Restrict a securing-policy witness to a smaller candidate family. -/
def restrictSecure
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {environments : Set Environment}
    {small large : Set Candidate}
    (hSubset : small ⊆ large) :
    Secure outcome realizes environments large ->
      Secure outcome realizes environments small :=
  fun witness =>
    ⟨witness.1, secure_candidate_antitone hSubset witness.2⟩

theorem restrictSecure_identity
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {environments : Set Environment}
    {family : Set Candidate}
    (witness : Secure outcome realizes environments family) :
    restrictSecure (Set.Subset.rfl : family ⊆ family) witness = witness := by
  rfl

theorem restrictSecure_composition
    {Witness : Type u}
    {Candidate : Type v}
    {Policy : Type w}
    {Environment : Type x}
    {outcome : Policy -> Environment -> Witness}
    {realizes : Witness -> Candidate -> Prop}
    {environments : Set Environment}
    {small middle large : Set Candidate}
    (hSmallMiddle : small ⊆ middle)
    (hMiddleLarge : middle ⊆ large)
    (witness : Secure outcome realizes environments large) :
    restrictSecure hSmallMiddle (restrictSecure hMiddleLarge witness) =
      restrictSecure
        (fun _ hSmall => hMiddleLarge (hSmallMiddle hSmall))
        witness := by
  rfl

end Finite
end OmegaV2
