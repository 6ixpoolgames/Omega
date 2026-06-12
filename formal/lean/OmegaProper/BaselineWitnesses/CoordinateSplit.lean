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

/-- Which coordinate a finite presentation exposes. -/
inductive CoordinateExposure where
  | declared
  | nuisance
  deriving DecidableEq

/-- The consequence system associated with each coordinate exposure. -/
def exposureSystem : CoordinateExposure -> ConsequenceSystem
  | CoordinateExposure.declared => declaredFirstSystem
  | CoordinateExposure.nuisance => declaredSecondSystem

/--
A deliberately coarse baseline summary invariant under the declared/nuisance
coordinate swap.

This `Unit` summary is a minimal schematic invariant, not a substantive
baseline metric. Later coordinate-split theorems should instantiate less
trivial coordinate-symmetric summaries.
-/
def swapInvariantBaseline (_e : CoordinateExposure) : Unit := ()

/-- Whether the exposure carries the declared first coordinate. -/
def carriesDeclaredFirst : CoordinateExposure -> Bool
  | CoordinateExposure.declared => true
  | CoordinateExposure.nuisance => false

theorem coordinate_split_same_baseline :
    swapInvariantBaseline CoordinateExposure.declared =
      swapInvariantBaseline CoordinateExposure.nuisance := by
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
Under declared-coordinate exposure, the pair differing only in the declared
coordinate is blocked.
-/
theorem declared_exposure_blocks_declared_split :
    ConsequenceMergeSeparated
      (exposureSystem CoordinateExposure.declared)
      X2.x00
      X2.x10 := by
  exact first_blocks_x00_x10

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

end CoordinateSplit
end BaselineWitnesses
end OmegaProper
