import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.Trajectory.PresentationFactClosure

/-!
OmegaProper.Trajectory.PresentationFactClosureExamples

Finite examples for presentation/fact closure.

These examples instantiate the generic Galois layer on the existing four-state
`X2` carrier. They show a small adversarial pattern:

* the first-bit target is common to a first-bit presentation family;
* admitting a second-bit presentation removes that first-bit target from the
  common facts;
* the same expansion removes visibility of the `x00/x10` pair;
* constant targets still survive, so this is not "no facts survive" but a
  strict collapse of coordinate-specific facts.

This does not define an admissibility criterion. It only shows how a declared
presentation family determines which facts survive common-fact closure.
-/

namespace OmegaProper
namespace Trajectory
namespace PresentationFactClosureExamples

open BaselineWitnesses
open PresentationFactClosure

/-- Declared presentation family containing only the first-bit presentation. -/
def firstOnlyPresentations : Set (X2 -> Bit) :=
  fun present => present = firstBit

/-- Expanded family containing both coordinate presentations. -/
def firstSecondPresentations : Set (X2 -> Bit) :=
  fun present => present = firstBit ∨ present = secondBit

/-- The declared first-coordinate target. -/
def firstTarget : X2 -> Bit := firstBit

/-- The declared second-coordinate target. -/
def secondTarget : X2 -> Bit := secondBit

/-- A constant target, used as a nontriviality control for family expansion. -/
def constantZeroTarget (_x : X2) : Bit := Bit.zero

/-- The pair separated by first bit but erased by second bit. -/
def x00_x10_pair : X2 × X2 := (X2.x00, X2.x10)

/-- Target-preservation satisfaction for `X2 -> Bit` presentations and facts. -/
abbrev X2TargetSatisfies : (X2 -> Bit) -> (X2 -> Bit) -> Prop :=
  TargetSatisfiesPresentation

/-- Common `X2 -> Bit` target facts for a declared presentation family. -/
abbrev X2CommonTargets (presentations : Set (X2 -> Bit)) :
    Set (X2 -> Bit) :=
  CommonTargets (X := X2) (Q := Bit) (T := Bit) presentations

/-- Common visible pairs for a declared `X2 -> Bit` presentation family. -/
abbrev X2CommonVisiblePairs (presentations : Set (X2 -> Bit)) :
    Set (X2 × X2) :=
  CommonVisiblePairs (X := X2) (Q := Bit) presentations

theorem firstOnly_subset_firstSecond :
    firstOnlyPresentations ⊆ firstSecondPresentations := by
  intro present hPresent
  exact Or.inl hPresent

theorem firstTarget_common_firstOnly :
    firstTarget ∈ X2CommonTargets firstOnlyPresentations := by
  intro present hPresent x y hErased
  rw [hPresent] at hErased
  exact hErased

theorem secondTarget_common_secondOnly :
    secondTarget ∈
      X2CommonTargets (fun present : X2 -> Bit => present = secondBit) := by
  intro present hPresent x y hErased
  rw [hPresent] at hErased
  exact hErased

theorem firstTarget_not_common_firstSecond :
    Not (firstTarget ∈ X2CommonTargets firstSecondPresentations) := by
  intro hCommon
  have hRespect := hCommon secondBit (Or.inr rfl)
  have hEq : firstBit X2.x00 = firstBit X2.x10 :=
    hRespect X2.x00 X2.x10 rfl
  cases hEq

theorem secondTarget_not_common_firstSecond :
    Not (secondTarget ∈ X2CommonTargets firstSecondPresentations) := by
  intro hCommon
  have hRespect := hCommon firstBit (Or.inl rfl)
  have hEq : secondBit X2.x00 = secondBit X2.x01 :=
    hRespect X2.x00 X2.x01 rfl
  cases hEq

theorem constantZeroTarget_common_firstSecond :
    constantZeroTarget ∈ X2CommonTargets firstSecondPresentations := by
  intro _present _hPresent _x _y _hErased
  rfl

/--
Adding the second-bit presentation strictly shrinks the common target facts:
everything common to the larger family is common to the first-only family, but
the first-bit target itself is lost.
-/
theorem commonTargets_strictly_shrink_when_second_admitted :
    X2CommonTargets firstSecondPresentations ⊆
        X2CommonTargets firstOnlyPresentations ∧
      firstTarget ∈ X2CommonTargets firstOnlyPresentations ∧
      Not (firstTarget ∈ X2CommonTargets firstSecondPresentations) := by
  exact And.intro
    (commonClaims_antitone firstOnly_subset_firstSecond)
    (And.intro
      firstTarget_common_firstOnly
      firstTarget_not_common_firstSecond)

theorem x00_x10_visible_firstOnly :
    x00_x10_pair ∈ X2CommonVisiblePairs firstOnlyPresentations := by
  intro present hPresent hErased
  rw [hPresent] at hErased
  cases hErased

theorem x00_x10_not_visible_firstSecond :
    Not (x00_x10_pair ∈ X2CommonVisiblePairs firstSecondPresentations) := by
  intro hCommon
  have hVisible := hCommon secondBit (Or.inr rfl)
  exact hVisible rfl

theorem commonVisiblePairs_strictly_shrink_when_second_admitted :
    X2CommonVisiblePairs firstSecondPresentations ⊆
        X2CommonVisiblePairs firstOnlyPresentations ∧
      x00_x10_pair ∈ X2CommonVisiblePairs firstOnlyPresentations ∧
      Not (x00_x10_pair ∈ X2CommonVisiblePairs firstSecondPresentations) := by
  exact And.intro
    (commonClaims_antitone firstOnly_subset_firstSecond)
    (And.intro
      x00_x10_visible_firstOnly
      x00_x10_not_visible_firstSecond)

/-- The first-bit presentation is included in the target-closure it generates. -/
theorem firstBitPresentation_in_targetClosure_firstOnly :
    firstBit ∈
      PresentationClosure X2TargetSatisfies firstOnlyPresentations := by
  exact presentations_subset_closure rfl

/--
The second-bit presentation is excluded from the first-only target closure,
because the first-bit target is common to the first-only family and second bit
does not preserve it.
-/
theorem secondBit_not_in_targetClosure_firstOnly :
    Not (secondBit ∈
      PresentationClosure X2TargetSatisfies firstOnlyPresentations) := by
  intro hClosure
  have hRespect : TargetSatisfiesPresentation secondBit firstTarget :=
    hClosure firstTarget firstTarget_common_firstOnly
  have hEq : firstBit X2.x00 = firstBit X2.x10 :=
    hRespect X2.x00 X2.x10 rfl
  cases hEq

end PresentationFactClosureExamples
end Trajectory
end OmegaProper
