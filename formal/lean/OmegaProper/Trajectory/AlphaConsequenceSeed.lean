import AlphaCore.Examples
import AlphaCore.Nondegenerate
import OmegaProper.Trajectory.ConsequenceRelation

/-!
OmegaProper.Trajectory.AlphaConsequenceSeed

Bridge from Alpha primitive witnesses to consequence-native separation.

This file does not define proto-teleology, Omega-seed, deformers, boundary,
value, agency, identity, or valuerhood. It only proves that when an Alpha
primitive witness endpoint pair is separated by an evaluated consequence
context, the pair carries merge-blocking consequence structure.
-/

namespace OmegaProper
namespace Trajectory
namespace AlphaConsequenceSeed

open ConsequenceRelation

universe u v k o

/--
A consequence system whose fragments are the carrier of an Alpha frame.

This avoids subtype/coercion plumbing while making the bridge explicit:
Alpha supplies fragments; the consequence layer supplies continuation contexts,
outcomes, comparison, and evaluation.
-/
structure AlphaConsequenceSystem (A : AlphaCore.Frame.{u, v}) where
  Context : Type k
  Outcome : Type o
  consequence : Context -> A.X -> Outcome
  Compare : Context -> Outcome -> Outcome -> Prop
  Evaluated : Context -> Prop

def AlphaConsequenceSystem.toConsequenceSystem
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A) :
    ConsequenceSystem.{u, k, o} where
  Fragment := A.X
  Context := S.Context
  Outcome := S.Outcome
  consequence := S.consequence
  Compare := S.Compare
  Evaluated := S.Evaluated

def JointWitnessConsequenceSeparated
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.JointPrimitiveWitness A) : Prop :=
  ConsequenceSeparated S.toConsequenceSystem w.x w.y

def JointWitnessReverseConsequenceSeparated
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.JointPrimitiveWitness A) : Prop :=
  ConsequenceSeparated S.toConsequenceSystem w.y w.x

def JointWitnessMergeSeparated
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.JointPrimitiveWitness A) : Prop :=
  ConsequenceMergeSeparated S.toConsequenceSystem w.x w.y

/--
The joint Alpha witness endpoints carry merge-blocking consequence structure.
This means only that symmetric identification is blocked by consequences.
-/
def ConsequenceBearingJointWitness
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.JointPrimitiveWitness A) : Prop :=
  JointWitnessMergeSeparated S w

def AsymmetryWitnessConsequenceSeparated
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.AsymmetryPrimitiveWitness A) : Prop :=
  JointWitnessConsequenceSeparated S w.toJoint

def AsymmetryWitnessReverseConsequenceSeparated
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.AsymmetryPrimitiveWitness A) : Prop :=
  JointWitnessReverseConsequenceSeparated S w.toJoint

def AsymmetryWitnessMergeSeparated
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.AsymmetryPrimitiveWitness A) : Prop :=
  JointWitnessMergeSeparated S w.toJoint

/--
An asymmetry witness is consequence-bearing when its supplied joint witness is
merge-separated by evaluated consequence.
-/
def ConsequenceBearingAlphaWitness
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (w : AlphaCore.Frame.AsymmetryPrimitiveWitness A) : Prop :=
  AsymmetryWitnessMergeSeparated S w

theorem jointWitness_separated_is_consequenceBearing
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.JointPrimitiveWitness A}
    (h : JointWitnessConsequenceSeparated S w) :
    ConsequenceBearingPair S.toConsequenceSystem w.x w.y := by
  exact h

theorem jointWitness_separated_is_mergeSeparated
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.JointPrimitiveWitness A}
    (h : JointWitnessConsequenceSeparated S w) :
    JointWitnessMergeSeparated S w := by
  exact separated_implies_mergeSeparated h

theorem jointWitness_reverseSeparated_is_mergeSeparated
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.JointPrimitiveWitness A}
    (h : JointWitnessReverseConsequenceSeparated S w) :
    JointWitnessMergeSeparated S w := by
  exact reverseSeparated_implies_mergeSeparated h

theorem jointWitness_mergeSeparated_blocks_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.JointPrimitiveWitness A}
    (h : JointWitnessMergeSeparated S w) :
    Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  exact mergeSeparated_blocks_identifiable h

theorem jointWitness_separation_blocks_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.JointPrimitiveWitness A}
    (h : JointWitnessConsequenceSeparated S w) :
    Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  exact jointWitness_mergeSeparated_blocks_identification
    (jointWitness_separated_is_mergeSeparated h)

theorem jointWitness_reverseSeparation_blocks_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.JointPrimitiveWitness A}
    (h : JointWitnessReverseConsequenceSeparated S w) :
    Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  exact jointWitness_mergeSeparated_blocks_identification
    (jointWitness_reverseSeparated_is_mergeSeparated h)

theorem asymmetryWitness_separated_is_consequenceBearing
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.AsymmetryPrimitiveWitness A}
    (h : AsymmetryWitnessConsequenceSeparated S w) :
    ConsequenceBearingPair S.toConsequenceSystem w.x w.y := by
  exact h

theorem asymmetryWitness_separated_is_mergeSeparated
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.AsymmetryPrimitiveWitness A}
    (h : AsymmetryWitnessConsequenceSeparated S w) :
    AsymmetryWitnessMergeSeparated S w := by
  exact jointWitness_separated_is_mergeSeparated h

theorem asymmetryWitness_reverseSeparated_is_mergeSeparated
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.AsymmetryPrimitiveWitness A}
    (h : AsymmetryWitnessReverseConsequenceSeparated S w) :
    AsymmetryWitnessMergeSeparated S w := by
  exact jointWitness_reverseSeparated_is_mergeSeparated h

theorem asymmetryWitness_mergeSeparated_blocks_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.AsymmetryPrimitiveWitness A}
    (h : AsymmetryWitnessMergeSeparated S w) :
    Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  exact jointWitness_mergeSeparated_blocks_identification (w := w.toJoint) h

theorem asymmetryWitness_separation_blocks_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.AsymmetryPrimitiveWitness A}
    (h : AsymmetryWitnessConsequenceSeparated S w) :
    Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  exact asymmetryWitness_mergeSeparated_blocks_identification
    (asymmetryWitness_separated_is_mergeSeparated h)

theorem asymmetryWitness_reverseSeparation_blocks_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {w : AlphaCore.Frame.AsymmetryPrimitiveWitness A}
    (h : AsymmetryWitnessReverseConsequenceSeparated S w) :
    Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  exact asymmetryWitness_mergeSeparated_blocks_identification
    (asymmetryWitness_reverseSeparated_is_mergeSeparated h)

/-! ## Tiny Alpha/consequence bridge example -/

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

end AlphaConsequenceSeed
end Trajectory
end OmegaProper
