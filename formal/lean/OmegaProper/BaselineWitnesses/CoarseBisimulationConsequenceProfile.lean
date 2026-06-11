import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.Trajectory.ProfileAbstraction

/-!
OmegaProper.BaselineWitnesses.CoarseBisimulationConsequenceProfile

Lean conversion of the finite witness:
`same_coarse_bisimulation_different_consequence_profile`.

Both declared panels can share the same coarse one-block view. The exact
expanded consequence profiles still differ: a pair allowed by the first
coordinate panel is blocked by the second, and conversely for another pair.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace CoarseBisimulationConsequenceProfile

open Trajectory.DeformationProfile
open Trajectory.ProfileAbstraction

def coarseFirstView :=
  UniversalAllowAbstraction declaredFirstSystem

def coarseSecondView :=
  UniversalAllowAbstraction declaredSecondSystem

theorem coarse_views_claim_all_pairs :
    (forall x y : X2, AbstractionAllows coarseFirstView x y) /\
    (forall x y : X2, AbstractionAllows coarseSecondView x y) := by
  constructor <;> intro _x _y <;> trivial

theorem first_allows_second_blocks_x00_x01 :
    ProfileAllows declaredFirstSystem X2.x00 X2.x01 /\
    ProfileBlocks declaredSecondSystem X2.x00 X2.x01 := by
  exact And.intro first_allows_x00_x01 second_blocks_x00_x01

theorem first_blocks_second_allows_x00_x10 :
    ProfileBlocks declaredFirstSystem X2.x00 X2.x10 /\
    ProfileAllows declaredSecondSystem X2.x00 X2.x10 := by
  exact And.intro first_blocks_x00_x10 second_allows_x00_x10

theorem coarseFirstView_not_soundAllows :
    Not (SoundAllows coarseFirstView) := by
  exact universalAllow_not_soundAllows_of_block first_blocks_x00_x10

theorem coarseSecondView_not_soundAllows :
    Not (SoundAllows coarseSecondView) := by
  exact universalAllow_not_soundAllows_of_block second_blocks_x00_x01

theorem same_coarse_bisimulation_different_consequence_profile :
    (forall x y : X2, AbstractionAllows coarseFirstView x y) /\
    (forall x y : X2, AbstractionAllows coarseSecondView x y) /\
    ProfileAllows declaredFirstSystem X2.x00 X2.x01 /\
    ProfileBlocks declaredSecondSystem X2.x00 X2.x01 /\
    ProfileBlocks declaredFirstSystem X2.x00 X2.x10 /\
    ProfileAllows declaredSecondSystem X2.x00 X2.x10 := by
  exact And.intro coarse_views_claim_all_pairs.left
    (And.intro coarse_views_claim_all_pairs.right
      (And.intro first_allows_x00_x01
        (And.intro second_blocks_x00_x01
          (And.intro first_blocks_x00_x10 second_allows_x00_x10))))

end CoarseBisimulationConsequenceProfile
end BaselineWitnesses
end OmegaProper
