import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.BaselineWitnesses.NonFactorization

/-!
OmegaProper.BaselineWitnesses.CoordinateSplit

Boolean coordinate-split non-factorization template.

This module packages the common finite-witness shape: a baseline summary is
invariant across declared/nuisance coordinate exposure, while the declared
target distinguishes them.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace CoordinateSplit

open NonFactorization
open Trajectory.ConsequenceRelation

/-! ## Coordinate exposures -/

/-- Which coordinate a finite presentation exposes. -/
inductive CoordinateExposure where
  | declared
  | nuisance
  deriving DecidableEq

/-- The consequence system associated with each coordinate exposure. -/
def exposureSystem : CoordinateExposure -> ConsequenceSystem
  | CoordinateExposure.declared => declaredFirstSystem
  | CoordinateExposure.nuisance => declaredSecondSystem

/-! ## Schematic and nontrivial coordinate-symmetric summaries -/

/--
A deliberately coarse baseline summary invariant under the declared/nuisance
coordinate swap.

This `Unit` summary is a minimal schematic invariant, not a substantive
baseline metric. Later coordinate-split theorems should instantiate less
trivial coordinate-symmetric summaries.
-/
def swapInvariantBaseline (_e : CoordinateExposure) : Unit := ()

/--
A finite count summary for the balanced two-by-two profile shape on the
four-point carrier.

The allowed/blocked pair counts are ordered-pair counts including self-pairs.
For either coordinate exposure, two classes of size two give:

```text
allowed ordered pairs = 2 * 2 * 2 = 8
blocked ordered pairs = 4 * 4 - 8 = 8
```
-/
structure ProfileCountSummary where
  sourceCount : Nat
  outcomeCount : Nat
  compatibleOrderedPairs : Nat
  blockedOrderedPairs : Nat
  deriving DecidableEq

def balancedTwoByTwoCountSummary : ProfileCountSummary where
  sourceCount := 4
  outcomeCount := 2
  compatibleOrderedPairs := 8
  blockedOrderedPairs := 8

/--
Nontrivial coordinate-symmetric baseline summary: it records the finite
two-by-two profile counts while forgetting which coordinate supplied the split.
-/
def coordinateSymmetricCountBaseline (_e : CoordinateExposure) :
    ProfileCountSummary :=
  balancedTwoByTwoCountSummary

/-- Whether the exposure carries the declared first coordinate. -/
def carriesDeclaredFirst : CoordinateExposure -> Bool
  | CoordinateExposure.declared => true
  | CoordinateExposure.nuisance => false

/-! ## Non-factorization through coordinate-symmetric summaries -/

theorem coordinate_split_same_baseline :
    swapInvariantBaseline CoordinateExposure.declared =
      swapInvariantBaseline CoordinateExposure.nuisance := by
  rfl

theorem coordinate_split_same_count_baseline :
    coordinateSymmetricCountBaseline CoordinateExposure.declared =
      coordinateSymmetricCountBaseline CoordinateExposure.nuisance := by
  rfl

theorem coordinate_split_different_declared_target :
    Not (
      carriesDeclaredFirst CoordinateExposure.declared =
        carriesDeclaredFirst CoordinateExposure.nuisance
    ) := by
  intro h
  cases h

/--
The coordinate-split pattern is a non-factorization witness: the declared
target does not factor through the swap-invariant baseline.
-/
theorem coordinateSplit_nonFactorization :
    NonFactorization swapInvariantBaseline carriesDeclaredFirst := by
  exact nonFactorization_of_same_summary_different_target
    coordinate_split_same_baseline
    coordinate_split_different_declared_target

/--
The same coordinate-split non-factorization, using the nontrivial finite count
summary instead of the schematic `Unit` baseline.
-/
theorem coordinateSplit_countBaseline_nonFactorization :
    NonFactorization coordinateSymmetricCountBaseline carriesDeclaredFirst := by
  exact nonFactorization_of_same_summary_different_target
    coordinate_split_same_count_baseline
    coordinate_split_different_declared_target

/-! ## Exact profile contrast behind the count summary -/

/--
Coordinate-symmetric two-by-two profile shape for the two coordinate-exposure
systems: either the first-coordinate pairs are allowed and cross-first pairs
are blocked, or the analogous second-coordinate shape holds.
-/
def BalancedTwoByTwoProfileShape : CoordinateExposure -> Prop
  | CoordinateExposure.declared =>
      (ConsequenceIdentifiable declaredFirstSystem X2.x00 X2.x01 /\
        ConsequenceIdentifiable declaredFirstSystem X2.x10 X2.x11 /\
        ConsequenceMergeSeparated declaredFirstSystem X2.x00 X2.x10 /\
        ConsequenceMergeSeparated declaredFirstSystem X2.x01 X2.x11)
  | CoordinateExposure.nuisance =>
      (ConsequenceIdentifiable declaredSecondSystem X2.x00 X2.x10 /\
        ConsequenceIdentifiable declaredSecondSystem X2.x01 X2.x11 /\
        ConsequenceMergeSeparated declaredSecondSystem X2.x00 X2.x01 /\
        ConsequenceMergeSeparated declaredSecondSystem X2.x10 X2.x11)

/--
Under declared-coordinate exposure, the pair differing only in the declared
coordinate is blocked.
-/
theorem declared_exposure_blocks_declared_split :
    ConsequenceMergeSeparated
      (exposureSystem CoordinateExposure.declared)
      X2.x00
      X2.x10 := by
  exact first_blocks_x00_x10

/-- The other cross-declared-coordinate pair is also blocked. -/
theorem declared_exposure_blocks_other_declared_split :
    ConsequenceMergeSeparated
      (exposureSystem CoordinateExposure.declared)
      X2.x01
      X2.x11 := by
  apply separated_implies_mergeSeparated
  refine Exists.intro OneContext.ctx (And.intro True.intro ?_)
  intro h
  cases h

/--
Under nuisance-coordinate exposure, the same declared-coordinate split is
allowed.
-/
theorem nuisance_exposure_allows_declared_split :
    ConsequenceIdentifiable
      (exposureSystem CoordinateExposure.nuisance)
      X2.x00
      X2.x10 := by
  exact second_allows_x00_x10

/-- The cross-nuisance pair is blocked under nuisance-coordinate exposure. -/
theorem nuisance_exposure_blocks_nuisance_split :
    ConsequenceMergeSeparated
      (exposureSystem CoordinateExposure.nuisance)
      X2.x00
      X2.x01 := by
  exact second_blocks_x00_x01

/-- The other cross-nuisance pair is also blocked. -/
theorem nuisance_exposure_blocks_other_nuisance_split :
    ConsequenceMergeSeparated
      (exposureSystem CoordinateExposure.nuisance)
      X2.x10
      X2.x11 := by
  apply separated_implies_mergeSeparated
  refine Exists.intro OneContext.ctx (And.intro True.intro ?_)
  intro h
  cases h

theorem coordinate_split_profile_contrast :
    ConsequenceMergeSeparated
      (exposureSystem CoordinateExposure.declared)
      X2.x00
      X2.x10 /\
    ConsequenceIdentifiable
      (exposureSystem CoordinateExposure.nuisance)
      X2.x00
      X2.x10 := by
  exact And.intro
    declared_exposure_blocks_declared_split
    nuisance_exposure_allows_declared_split

theorem declared_exposure_balancedTwoByTwoProfileShape :
    BalancedTwoByTwoProfileShape CoordinateExposure.declared := by
  exact And.intro first_allows_x00_x01
    (And.intro first_allows_x10_x11
      (And.intro
        declared_exposure_blocks_declared_split
        declared_exposure_blocks_other_declared_split))

theorem nuisance_exposure_balancedTwoByTwoProfileShape :
    BalancedTwoByTwoProfileShape CoordinateExposure.nuisance := by
  exact And.intro second_allows_x00_x10
    (And.intro second_allows_x01_x11
      (And.intro
        nuisance_exposure_blocks_nuisance_split
        nuisance_exposure_blocks_other_nuisance_split))

theorem coordinate_split_same_profile_shape :
    BalancedTwoByTwoProfileShape CoordinateExposure.declared /\
    BalancedTwoByTwoProfileShape CoordinateExposure.nuisance := by
  exact And.intro
    declared_exposure_balancedTwoByTwoProfileShape
    nuisance_exposure_balancedTwoByTwoProfileShape

end CoordinateSplit
end BaselineWitnesses
end OmegaProper
