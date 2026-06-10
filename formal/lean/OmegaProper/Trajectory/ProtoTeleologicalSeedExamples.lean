import OmegaProper.Trajectory.AlphaConsequenceSeedExamples
import OmegaProper.Trajectory.ProtoTeleologicalSeed

/-!
OmegaProper.Trajectory.ProtoTeleologicalSeedExamples

Tiny examples for proto-teleological seed wrappers.

These examples keep the claim narrow:

  primitive Alpha witness + evaluated consequence merge-separation

They also show that primitive nondegeneracy alone is not enough when the
consequence apparatus is vacuous or universally permissive.
-/

namespace OmegaProper
namespace Trajectory
namespace ProtoTeleologicalSeedExamples

open AlphaConsequenceSeed
open AlphaConsequenceSeedExamples
open ConsequenceDiscipline
open ConsequenceRelation
open ProtoTeleologicalSeed

def chainVacuousConsequenceSystem :
    AlphaConsequenceSystem AlphaCore.Examples.chainFrame where
  Context := SeedContext
  Outcome := SeedOutcome
  consequence := chainSeedConsequence
  Compare := seedCompare
  Evaluated := fun _ => False

def chainUniversalConsequenceSystem :
    AlphaConsequenceSystem AlphaCore.Examples.chainFrame where
  Context := SeedContext
  Outcome := SeedOutcome
  consequence := chainSeedConsequence
  Compare := fun _ _ _ => True
  Evaluated := fun _ => True

theorem chain_asymmetry_protoTeleologicalSeed :
    AsymmetryProtoTeleologicalSeed chainAlphaConsequenceSystem := by
  exact Exists.intro chainAsymmetryWitness chain_witness_mergeSeparated

theorem chain_protoTeleologicalSeed :
    ProtoTeleologicalSeed chainAlphaConsequenceSystem := by
  exact chain_asymmetry_protoTeleologicalSeed

theorem chain_joint_protoTeleologicalSeed :
    JointProtoTeleologicalSeed chainAlphaConsequenceSystem := by
  exact asymmetrySeed_implies_jointSeed chain_asymmetry_protoTeleologicalSeed

theorem chain_seed_blocks_consequenceCollapse :
    Not (ConsequenceCollapsed chainAlphaConsequenceSystem.toConsequenceSystem) := by
  exact asymmetrySeed_blocks_consequenceCollapse
    chain_asymmetry_protoTeleologicalSeed

theorem chain_seed_has_blocked_identification_witness :
    exists w : AlphaCore.Frame.AsymmetryPrimitiveWitness AlphaCore.Examples.chainFrame,
      ConsequenceBearingAlphaWitness chainAlphaConsequenceSystem w /\
      Not (
        ConsequenceIdentifiable
          chainAlphaConsequenceSystem.toConsequenceSystem
          w.x
          w.y
      ) := by
  exact asymmetrySeed_has_witness_blocking_identification
    chain_asymmetry_protoTeleologicalSeed

theorem chain_vacuous_no_asymmetry_seed :
    Not (AsymmetryProtoTeleologicalSeed chainVacuousConsequenceSystem) := by
  intro h
  match h with
  | Exists.intro _w hBearing =>
      cases hBearing with
      | inl hsep =>
          match hsep with
          | Exists.intro _c hc =>
              exact False.elim hc.left
      | inr hsep =>
          match hsep with
          | Exists.intro _c hc =>
              exact False.elim hc.left

theorem chain_vacuous_no_protoTeleologicalSeed :
    Not (ProtoTeleologicalSeed chainVacuousConsequenceSystem) := by
  exact chain_vacuous_no_asymmetry_seed

theorem chain_universal_no_asymmetry_seed :
    Not (AsymmetryProtoTeleologicalSeed chainUniversalConsequenceSystem) := by
  intro h
  match h with
  | Exists.intro _w hBearing =>
      cases hBearing with
      | inl hsep =>
          match hsep with
          | Exists.intro _c hc =>
              exact hc.right trivial
      | inr hsep =>
          match hsep with
          | Exists.intro _c hc =>
              exact hc.right trivial

theorem chain_universal_no_protoTeleologicalSeed :
    Not (ProtoTeleologicalSeed chainUniversalConsequenceSystem) := by
  exact chain_universal_no_asymmetry_seed

theorem primitiveNondegenerate_not_sufficient_for_protoTeleologicalSeed :
    exists A : AlphaCore.Frame.{0, 0},
      exists S : AlphaConsequenceSystem.{0, 0, 0, 0} A,
        AlphaCore.Frame.PrimitiveNondegenerate A /\
        Not (AsymmetryProtoTeleologicalSeed S) := by
  exact Exists.intro AlphaCore.Examples.chainFrame
    (Exists.intro chainVacuousConsequenceSystem
      (And.intro
        AlphaCore.Examples.chainFrame_primitiveNondegenerate
        chain_vacuous_no_asymmetry_seed))

end ProtoTeleologicalSeedExamples
end Trajectory
end OmegaProper
