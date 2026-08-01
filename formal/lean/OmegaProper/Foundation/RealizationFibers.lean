import Mathlib.Data.Set.Basic

/-!
OmegaProper.Foundation.RealizationFibers

The witness-retaining May-realization object.

For a witness-to-candidate incidence relation, `Real realizes G` is the set of
witnesses realizing every candidate in `G`. Inclusion of candidate families
induces restriction in the opposite direction. Nonempty fibers therefore form
a downward-closed compatibility support.

This file does not select a maximal face and does not define value or standing.
-/

namespace OmegaProper
namespace Foundation
namespace RealizationFibers

universe u v

/-- Witnesses that jointly realize every candidate in a family. -/
def Real
    {Witness : Type u}
    {Candidate : Type v}
    (realizes : Witness -> Candidate -> Prop)
    (family : Set Candidate) :
    Set Witness :=
  {witness | forall candidate, candidate ∈ family -> realizes witness candidate}

/-- May compatibility is nonemptiness of the full realization fiber. -/
def MayCompatible
    {Witness : Type u}
    {Candidate : Type v}
    (realizes : Witness -> Candidate -> Prop)
    (family : Set Candidate) : Prop :=
  (Real realizes family).Nonempty

/--
Adding candidates can only remove realization witnesses.
-/
theorem real_antitone
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small large : Set Candidate}
    (hSubset : small ⊆ large) :
    Real realizes large ⊆ Real realizes small := by
  intro witness hLarge candidate hCandidate
  exact hLarge candidate (hSubset hCandidate)

/--
May compatibility is downward closed under removal of candidates.
-/
theorem mayCompatible_downward
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small large : Set Candidate}
    (hSubset : small ⊆ large)
    (hCompatible : MayCompatible realizes large) :
    MayCompatible realizes small := by
  match hCompatible with
  | Exists.intro witness hWitness =>
      exact Exists.intro witness (real_antitone hSubset hWitness)

/-- Every witness realizes the empty family. -/
theorem real_empty
    {Witness : Type u}
    {Candidate : Type v}
    (realizes : Witness -> Candidate -> Prop) :
    Real realizes (∅ : Set Candidate) = Set.univ := by
  ext witness
  simp [Real]

/-- Joint realization of a union is intersection of the two fibers. -/
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
    exact And.intro
      (by
        intro candidate hCandidate
        exact hBoth candidate (Or.inl hCandidate))
      (by
        intro candidate hCandidate
        exact hBoth candidate (Or.inr hCandidate))
  · intro hSeparate candidate hCandidate
    cases hCandidate with
    | inl hLeft =>
        exact hSeparate.left candidate hLeft
    | inr hRight =>
        exact hSeparate.right candidate hRight

/--
Restriction sends a witness for a larger family to the same witness for any
smaller family.
-/
def restrict
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small large : Set Candidate}
    (hSubset : small ⊆ large) :
    Real realizes large -> Real realizes small :=
  fun witness =>
    ⟨witness.1, real_antitone hSubset witness.2⟩

theorem restrict_identity
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {family : Set Candidate}
    (witness : Real realizes family) :
    restrict (Set.Subset.rfl : family ⊆ family) witness = witness := by
  rfl

theorem restrict_composition
    {Witness : Type u}
    {Candidate : Type v}
    {realizes : Witness -> Candidate -> Prop}
    {small middle large : Set Candidate}
    (hSmallMiddle : small ⊆ middle)
    (hMiddleLarge : middle ⊆ large)
    (witness : Real realizes large) :
    restrict hSmallMiddle (restrict hMiddleLarge witness) =
      restrict (fun _ hSmall => hMiddleLarge (hSmallMiddle hSmall)) witness := by
  rfl

end RealizationFibers
end Foundation
end OmegaProper
