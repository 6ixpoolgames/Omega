import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.Trajectory.PresentationInvariant

/-!
OmegaProper.Trajectory.PresentationInvariantExamples

Finite examples for presentation-invariant consequence.

These examples make the audit test concrete on the existing four-state X2
systems: a presentation that keeps consequence-separated fragments apart is
sound, while a constant presentation that erases a merge-separated pair is
unsound.
-/

namespace OmegaProper
namespace Trajectory
namespace PresentationInvariantExamples

open BaselineWitnesses
open ConsequenceRelation
open PresentationInvariant
open SoundQuotient

/-- Presentation by the declared first coordinate. -/
def firstBitPresentation : X2 -> Bit :=
  firstBit

/-- Constant presentation that erases every X2 state. -/
def constantUnitPresentation (_x : X2) : Unit :=
  ()

/--
Presenting `declaredFirstSystem` by the first bit is sound: it identifies only
pairs with equal first-bit consequences.
-/
theorem firstBitPresentation_sound_declaredFirst :
    SoundQuotient declaredFirstSystem firstBitPresentation := by
  intro x y hxy
  constructor
  case left =>
    intro c _hEval
    cases c
    exact hxy
  case right =>
    intro c _hEval
    cases c
    exact Eq.symm hxy

theorem firstBitPresentation_keeps_x00_x10_apart :
    Not (PairErasedByPresentation firstBitPresentation X2.x00 X2.x10) := by
  intro h
  cases h

theorem x00_x10_invariant_under_sound_quotients :
    PairInvariantUnderSoundQuotients declaredFirstSystem X2.x00 X2.x10 := by
  exact mergeSeparated_invariantUnderSoundQuotients first_blocks_x00_x10

theorem x00_x10_invariant_blocks_firstBit_erasure :
    Not (PairErasedByPresentation firstBitPresentation X2.x00 X2.x10) := by
  exact x00_x10_invariant_under_sound_quotients
    firstBitPresentation
    firstBitPresentation_sound_declaredFirst

theorem constantUnitPresentation_erases_x00_x10 :
    PairErasedByPresentation constantUnitPresentation X2.x00 X2.x10 := by
  rfl

theorem constantUnitPresentation_erases_mergeSeparatedPair :
    ErasesMergeSeparatedPair
      declaredFirstSystem
      constantUnitPresentation := by
  exact Exists.intro X2.x00
    (Exists.intro X2.x10
      (And.intro
        constantUnitPresentation_erases_x00_x10
        first_blocks_x00_x10))

theorem constantUnitPresentation_not_sound_declaredFirst :
    Not (SoundQuotient declaredFirstSystem constantUnitPresentation) := by
  exact erasesMergeSeparatedPair_not_sound
    constantUnitPresentation_erases_mergeSeparatedPair

/--
The constant presentation is not merely coarse; it is unsound because it erases
a consequence-blocked distinction.
-/
theorem constantUnitPresentation_erasure_certifies_unsoundness :
    PairErasedByPresentation constantUnitPresentation X2.x00 X2.x10 /\
    ConsequenceMergeSeparated declaredFirstSystem X2.x00 X2.x10 /\
    Not (SoundQuotient declaredFirstSystem constantUnitPresentation) := by
  exact And.intro
    constantUnitPresentation_erases_x00_x10
    (And.intro
      first_blocks_x00_x10
      constantUnitPresentation_not_sound_declaredFirst)

end PresentationInvariantExamples
end Trajectory
end OmegaProper
