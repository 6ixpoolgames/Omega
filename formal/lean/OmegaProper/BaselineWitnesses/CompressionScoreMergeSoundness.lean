import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.Trajectory.DeformationProfile

/-!
OmegaProper.BaselineWitnesses.CompressionScoreMergeSoundness

Lean conversion of the finite witness:
`same_compression_score_different_merge_soundness`.

Two binary abstractions over the same four fragments have the same simple
two-pair compression shape. Grouping by the declared coordinate respects the
exact consequence profile; grouping by the nuisance coordinate does not.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace CompressionScoreMergeSoundness

open Trajectory.ConsequenceRelation
open Trajectory.DeformationProfile

def SameFirstClass (x y : X2) : Prop :=
  firstBit x = firstBit y

def SameSecondClass (x y : X2) : Prop :=
  secondBit x = secondBit y

/--
The coarse compression score used by this witness: on the four-point carrier,
the relation claims exactly one of the two axis-aligned two-pair shapes.
-/
def TwoPairCompressionShape (R : X2 -> X2 -> Prop) : Prop :=
  (R X2.x00 X2.x01 /\
    R X2.x10 X2.x11 /\
    Not (R X2.x00 X2.x10) /\
    Not (R X2.x01 X2.x11)) \/
  (R X2.x00 X2.x10 /\
    R X2.x01 X2.x11 /\
    Not (R X2.x00 X2.x01) /\
    Not (R X2.x10 X2.x11))

theorem sameFirst_twoPairCompressionShape :
    TwoPairCompressionShape SameFirstClass := by
  exact Or.inl
    (And.intro rfl
      (And.intro rfl
        (And.intro
          (by intro h; cases h)
          (by intro h; cases h))))

theorem sameSecond_twoPairCompressionShape :
    TwoPairCompressionShape SameSecondClass := by
  exact Or.inr
    (And.intro rfl
      (And.intro rfl
        (And.intro
          (by intro h; cases h)
          (by intro h; cases h))))

theorem sameFirst_respects_declaredFirstProfile :
    IdentificationRespectsConsequences declaredFirstSystem SameFirstClass := by
  intro x y hSame
  constructor
  case left =>
    intro c _hEval
    cases c
    exact hSame
  case right =>
    intro c _hEval
    cases c
    exact Eq.symm hSame

theorem sameSecond_not_respects_declaredFirstProfile :
    Not (IdentificationRespectsConsequences declaredFirstSystem SameSecondClass) := by
  intro hSound
  have hSameSecond : SameSecondClass X2.x00 X2.x10 := rfl
  exact mergeSeparated_blocks_identifiable
    first_blocks_x00_x10
    (hSound hSameSecond)

theorem same_compression_score_different_merge_soundness :
    TwoPairCompressionShape SameFirstClass /\
    TwoPairCompressionShape SameSecondClass /\
    IdentificationRespectsConsequences declaredFirstSystem SameFirstClass /\
    Not (IdentificationRespectsConsequences declaredFirstSystem SameSecondClass) := by
  exact And.intro sameFirst_twoPairCompressionShape
    (And.intro sameSecond_twoPairCompressionShape
      (And.intro sameFirst_respects_declaredFirstProfile
        sameSecond_not_respects_declaredFirstProfile))

theorem nuisance_class_claim_blocks_exact_profile :
    ProfileBlocks declaredFirstSystem X2.x00 X2.x10 /\
    SameSecondClass X2.x00 X2.x10 := by
  exact And.intro first_blocks_x00_x10 rfl

end CompressionScoreMergeSoundness
end BaselineWitnesses
end OmegaProper
