import OmegaProper.Trajectory.DeformationProfile
import OmegaProper.Trajectory.ProtoTeleologicalSeedExamples

/-!
OmegaProper.Trajectory.DeformationProfileExamples

Tiny checked examples for the speculative deformation-profile bridge.

The example compares two consequence systems over the same `chainFrame`
carrier: the equality-based seed system and a universally permissive system.
This is not a recoverability or identity claim.
-/

namespace OmegaProper
namespace Trajectory
namespace DeformationProfileExamples

open AlphaConsequenceSeedExamples
open DeformationProfile
open ProtoTeleologicalSeedExamples

theorem chainUniversal_allows_witness :
    ProfileAllows
      chainUniversalConsequenceSystem.toConsequenceSystem
      chainAsymmetryWitness.x
      chainAsymmetryWitness.y := by
  constructor
  case left =>
    intro c _hEval
    cases c
    trivial
  case right =>
    intro c _hEval
    cases c
    trivial

theorem chain_deforms_universal :
    AlphaProfileDeforms
      chainAlphaConsequenceSystem
      chainUniversalConsequenceSystem := by
  exact alphaProfileDeforms_of_block_allow
    chain_witness_mergeSeparated
    chainUniversal_allows_witness

theorem universal_deforms_chain :
    AlphaProfileDeforms
      chainUniversalConsequenceSystem
      chainAlphaConsequenceSystem := by
  exact alphaProfileDeforms_symm chain_deforms_universal

theorem chain_not_self_deforming :
    Not (AlphaProfileDeforms
      chainAlphaConsequenceSystem
      chainAlphaConsequenceSystem) := by
  exact alphaProfileDeforms_not_self

end DeformationProfileExamples
end Trajectory
end OmegaProper
