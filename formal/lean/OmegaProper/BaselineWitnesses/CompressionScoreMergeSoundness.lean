import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.BaselineWitnesses.NonFactorization
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
open NonFactorization

def SameFirstClass (x y : X2) : Prop :=
  firstBit x = firstBit y

def SameSecondClass (x y : X2) : Prop :=
  secondBit x = secondBit y

/-! ## Computed summary/target form -/

/-- Which binary class relation is being summarized. -/
inductive CompressionExposure where
  | sameFirst
  | sameSecond
  deriving DecidableEq

def classRelationBool : CompressionExposure -> X2 -> X2 -> Bool
  | CompressionExposure.sameFirst, x, y => decide (firstBit x = firstBit y)
  | CompressionExposure.sameSecond, x, y => decide (secondBit x = secondBit y)

def claimedOrderedPairCount (e : CompressionExposure) : Nat :=
  (x2OrderedPairs.filter (fun p => classRelationBool e p.1 p.2)).length

def rejectedOrderedPairCount (e : CompressionExposure) : Nat :=
  (x2OrderedPairs.filter (fun p => !(classRelationBool e p.1 p.2))).length

/--
Computed coarse compression summary: how many ordered pairs the binary relation
claims as same-class versus rejected.
-/
structure CompressionCountSummary where
  sourceCount : Nat
  claimedOrderedPairs : Nat
  rejectedOrderedPairs : Nat
  deriving DecidableEq

def balancedCompressionCountSummary : CompressionCountSummary where
  sourceCount := 4
  claimedOrderedPairs := 8
  rejectedOrderedPairs := 8

def compressionSummaryOfExposure
    (e : CompressionExposure) : CompressionCountSummary where
  sourceCount := x2States.length
  claimedOrderedPairs := claimedOrderedPairCount e
  rejectedOrderedPairs := rejectedOrderedPairCount e

def mergeSoundnessViolationCount (e : CompressionExposure) : Nat :=
  (x2OrderedPairs.filter (fun p =>
    classRelationBool e p.1 p.2 &&
      decide (Not (firstBit p.1 = firstBit p.2)))).length

def mergeSoundnessTargetOfExposure (e : CompressionExposure) : Bool :=
  decide (mergeSoundnessViolationCount e = 0)

theorem compressionSummary_sameFirst :
    compressionSummaryOfExposure CompressionExposure.sameFirst =
      balancedCompressionCountSummary := by
  native_decide

theorem compressionSummary_sameSecond :
    compressionSummaryOfExposure CompressionExposure.sameSecond =
      balancedCompressionCountSummary := by
  native_decide

theorem same_compression_computed_summary :
    compressionSummaryOfExposure CompressionExposure.sameFirst =
      compressionSummaryOfExposure CompressionExposure.sameSecond := by
  rw [compressionSummary_sameFirst, compressionSummary_sameSecond]

theorem sameFirst_mergeSoundnessTarget :
    mergeSoundnessTargetOfExposure CompressionExposure.sameFirst = true := by
  native_decide

theorem sameSecond_mergeSoundnessTarget :
    mergeSoundnessTargetOfExposure CompressionExposure.sameSecond = false := by
  native_decide

theorem different_mergeSoundnessTarget :
    Not (
      mergeSoundnessTargetOfExposure CompressionExposure.sameFirst =
        mergeSoundnessTargetOfExposure CompressionExposure.sameSecond
    ) := by
  native_decide

theorem compressionScore_computedSummary_nonFactorization :
    NonFactorization
      compressionSummaryOfExposure
      mergeSoundnessTargetOfExposure := by
  exact nonFactorization_of_same_summary_different_target
    same_compression_computed_summary
    different_mergeSoundnessTarget

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
