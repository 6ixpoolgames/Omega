import OmegaProper.Trajectory.ConsequenceClasses

/-!
OmegaProper.BaselineWitnesses.ChainEvidenceClassSoundness

Lean conversion of the finite witness:
`same_chain_evidence_different_class_soundness`.

Two proposed three-fragment classes pass the same adjacent-chain checks. One is
pairwise consequence-compatible; the other contains a separated endpoint pair.
The point is narrow: chain evidence is not class soundness unless transitivity
or pairwise compatibility has been earned.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace ChainEvidenceClassSoundness

open Trajectory.ConsequenceClasses
open Trajectory.ConsequenceRelation

inductive ChainFragment where
  | v0
  | v1
  | v2
  | i0
  | i1
  | i2
  deriving DecidableEq

inductive ChainContext where
  | ctx
  deriving DecidableEq

def chainConsequence : ChainContext -> ChainFragment -> ChainFragment
  | _, x => x

def chainCompare : ChainContext -> ChainFragment -> ChainFragment -> Prop
  | _, ChainFragment.v0, ChainFragment.v0 => True
  | _, ChainFragment.v0, ChainFragment.v1 => True
  | _, ChainFragment.v0, ChainFragment.v2 => True
  | _, ChainFragment.v1, ChainFragment.v0 => True
  | _, ChainFragment.v1, ChainFragment.v1 => True
  | _, ChainFragment.v1, ChainFragment.v2 => True
  | _, ChainFragment.v2, ChainFragment.v0 => True
  | _, ChainFragment.v2, ChainFragment.v1 => True
  | _, ChainFragment.v2, ChainFragment.v2 => True
  | _, ChainFragment.i0, ChainFragment.i0 => True
  | _, ChainFragment.i0, ChainFragment.i1 => True
  | _, ChainFragment.i0, ChainFragment.i2 => False
  | _, ChainFragment.i1, ChainFragment.i0 => True
  | _, ChainFragment.i1, ChainFragment.i1 => True
  | _, ChainFragment.i1, ChainFragment.i2 => True
  | _, ChainFragment.i2, ChainFragment.i0 => False
  | _, ChainFragment.i2, ChainFragment.i1 => True
  | _, ChainFragment.i2, ChainFragment.i2 => True
  | _, _, _ => False

def chainWitnessSystem : ConsequenceSystem where
  Fragment := ChainFragment
  Context := ChainContext
  Outcome := ChainFragment
  consequence := chainConsequence
  Compare := chainCompare
  Evaluated := fun _ => True

def validClass : ChainFragment -> Prop
  | ChainFragment.v0 => True
  | ChainFragment.v1 => True
  | ChainFragment.v2 => True
  | _ => False

def invalidClass : ChainFragment -> Prop
  | ChainFragment.i0 => True
  | ChainFragment.i1 => True
  | ChainFragment.i2 => True
  | _ => False

def validDeclaredChainStep : ChainFragment -> ChainFragment -> Prop
  | ChainFragment.v0, ChainFragment.v1 => True
  | ChainFragment.v1, ChainFragment.v2 => True
  | _, _ => False

def invalidDeclaredChainStep : ChainFragment -> ChainFragment -> Prop
  | ChainFragment.i0, ChainFragment.i1 => True
  | ChainFragment.i1, ChainFragment.i2 => True
  | _, _ => False

theorem valid_declared_chain_step_respects :
    ChainStepRespectsConsequences chainWitnessSystem validDeclaredChainStep := by
  intro x y hstep
  cases x <;> cases y <;> try cases hstep
  all_goals
    intro c _hEval
    cases c
    trivial

theorem invalid_declared_chain_step_respects :
    ChainStepRespectsConsequences chainWitnessSystem invalidDeclaredChainStep := by
  intro x y hstep
  cases x <;> cases y <;> try cases hstep
  all_goals
    intro c _hEval
    cases c
    trivial

theorem valid_class_respects_consequences :
    ClassRespectsConsequences chainWitnessSystem validClass := by
  intro x y hx hy c _hEval
  cases x <;> try cases hx <;>
    cases y <;> try cases hy <;>
    cases c <;> trivial

theorem invalid_endpoint_separated :
    ConsequenceSeparated chainWitnessSystem ChainFragment.i0 ChainFragment.i2 := by
  exists ChainContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    exact h

theorem invalid_class_has_separated_pair :
    ClassHasSeparatedPair chainWitnessSystem invalidClass := by
  exists ChainFragment.i0
  exists ChainFragment.i2
  exact And.intro trivial (And.intro trivial invalid_endpoint_separated)

theorem invalid_class_not_respects_consequences :
    Not (ClassRespectsConsequences chainWitnessSystem invalidClass) := by
  exact separated_pair_blocks_class_respect invalid_class_has_separated_pair

theorem same_chain_evidence_different_class_soundness :
    ChainStepRespectsConsequences chainWitnessSystem validDeclaredChainStep /\
    ChainStepRespectsConsequences chainWitnessSystem invalidDeclaredChainStep /\
    ClassRespectsConsequences chainWitnessSystem validClass /\
    Not (ClassRespectsConsequences chainWitnessSystem invalidClass) := by
  exact And.intro valid_declared_chain_step_respects
    (And.intro invalid_declared_chain_step_respects
      (And.intro valid_class_respects_consequences
        invalid_class_not_respects_consequences))

end ChainEvidenceClassSoundness
end BaselineWitnesses
end OmegaProper
