import AlphaCore.Examples
import OmegaProper.Trajectory.AlphaConsequenceSeed

/-!
OmegaProper.Trajectory.AlphaConsequenceSeedExamples

Tiny examples for the Alpha-to-consequence seed bridge.

Examples live outside the core bridge so the abstraction only depends on
`AlphaCore.Nondegenerate` and the consequence relation layer.
-/

namespace OmegaProper
namespace Trajectory
namespace AlphaConsequenceSeedExamples

open ConsequenceRelation
open AlphaConsequenceSeed

inductive SeedOutcome where
  | zero
  | one
  deriving DecidableEq

inductive SeedContext where
  | ctx
  deriving DecidableEq

def chainSeedConsequence :
    SeedContext -> AlphaCore.Examples.Two -> SeedOutcome
  | SeedContext.ctx, AlphaCore.Examples.Two.a => SeedOutcome.zero
  | SeedContext.ctx, AlphaCore.Examples.Two.b => SeedOutcome.one

def seedCompare : SeedContext -> SeedOutcome -> SeedOutcome -> Prop
  | _, x, y => x = y

def chainAlphaConsequenceSystem :
    AlphaConsequenceSystem AlphaCore.Examples.chainFrame where
  Context := SeedContext
  Outcome := SeedOutcome
  consequence := chainSeedConsequence
  Compare := seedCompare
  Evaluated := fun _ => True

def chainAsymmetryWitness :
    AlphaCore.Frame.AsymmetryPrimitiveWitness AlphaCore.Examples.chainFrame where
  d := AlphaCore.Examples.OneDist.d
  x := AlphaCore.Examples.Two.a
  y := AlphaCore.Examples.Two.b
  asym := And.intro rfl rfl

theorem chain_witness_separated :
    AsymmetryWitnessConsequenceSeparated
      chainAlphaConsequenceSystem
      chainAsymmetryWitness := by
  exists SeedContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem chain_witness_mergeSeparated :
    AsymmetryWitnessMergeSeparated
      chainAlphaConsequenceSystem
      chainAsymmetryWitness := by
  exact asymmetryWitness_separated_is_mergeSeparated chain_witness_separated

theorem chain_witness_blocks_identification :
    Not (
      ConsequenceIdentifiable
        chainAlphaConsequenceSystem.toConsequenceSystem
        chainAsymmetryWitness.x
        chainAsymmetryWitness.y
    ) := by
  exact asymmetryWitness_separation_blocks_identification
    chain_witness_separated

end AlphaConsequenceSeedExamples
end Trajectory
end OmegaProper
