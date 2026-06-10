import AlphaCore.Examples
import OmegaProper.Trajectory.ProtoTeleologicalSeed

/-!
OmegaProper.Trajectory.ProtoTeleologicalSeedDiscipline

Guardrails for proto-teleological seed wrappers.

This file keeps the current seed small:

  primitive Alpha contact + evaluated consequence merge-separation

It proves that a seed implies both primitive nondegeneracy and consequence
noncollapse, and gives a negative control showing that consequence noncollapse
alone does not imply a seed.

It does not define purpose, value, agency, identity, deformer structure,
boundary, valuerhood, Omega-seed, or Omega-terminal.
-/

namespace OmegaProper
namespace Trajectory
namespace ProtoTeleologicalSeedDiscipline

open AlphaConsequenceSeed
open ConsequenceDiscipline
open ConsequenceRelation
open ProtoTeleologicalSeed

universe u v k o

theorem protoSeed_implies_primitiveNondegenerate
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : ProtoTeleologicalSeed S) :
    AlphaCore.Frame.PrimitiveNondegenerate A := by
  exact asymmetrySeed_implies_primitiveNondegenerate h

theorem protoSeed_implies_consequenceNoncollapsed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : ProtoTeleologicalSeed S) :
    ConsequenceNoncollapsed S.toConsequenceSystem := by
  exact asymmetrySeed_implies_consequenceNoncollapsed h

theorem protoSeed_blocks_consequenceCollapse
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : ProtoTeleologicalSeed S) :
    Not (ConsequenceCollapsed S.toConsequenceSystem) := by
  exact asymmetrySeed_blocks_consequenceCollapse h

inductive SymmetricOutcome where
  | zero
  | one
  deriving DecidableEq

inductive SymmetricContext where
  | ctx
  deriving DecidableEq

def symmetricConsequence :
    SymmetricContext -> AlphaCore.Examples.Two -> SymmetricOutcome
  | SymmetricContext.ctx, AlphaCore.Examples.Two.a => SymmetricOutcome.zero
  | SymmetricContext.ctx, AlphaCore.Examples.Two.b => SymmetricOutcome.one

def symmetricCompare :
    SymmetricContext -> SymmetricOutcome -> SymmetricOutcome -> Prop
  | _, x, y => x = y

def symmetricTwoConsequenceSystem :
    AlphaConsequenceSystem AlphaCore.Examples.symmetricTwoFrame where
  Context := SymmetricContext
  Outcome := SymmetricOutcome
  consequence := symmetricConsequence
  Compare := symmetricCompare
  Evaluated := fun _ => True

theorem symmetricTwo_a_b_separated :
    ConsequenceSeparated
      symmetricTwoConsequenceSystem.toConsequenceSystem
      AlphaCore.Examples.Two.a
      AlphaCore.Examples.Two.b := by
  exists SymmetricContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem symmetricTwo_consequenceNoncollapsed :
    ConsequenceNoncollapsed symmetricTwoConsequenceSystem.toConsequenceSystem := by
  exact Exists.intro AlphaCore.Examples.Two.a
    (Exists.intro AlphaCore.Examples.Two.b symmetricTwo_a_b_separated)

theorem symmetricTwo_no_asymmetryProtoTeleologicalSeed :
    Not (AsymmetryProtoTeleologicalSeed symmetricTwoConsequenceSystem) := by
  intro h
  match h with
  | Exists.intro w _hBearing =>
      cases w.asym

theorem consequenceNoncollapsed_not_sufficient_for_protoTeleologicalSeed :
    exists A : AlphaCore.Frame.{0, 0},
      exists S : AlphaConsequenceSystem.{0, 0, 0, 0} A,
        ConsequenceNoncollapsed S.toConsequenceSystem /\
        Not (AsymmetryProtoTeleologicalSeed S) := by
  exact Exists.intro AlphaCore.Examples.symmetricTwoFrame
    (Exists.intro symmetricTwoConsequenceSystem
      (And.intro
        symmetricTwo_consequenceNoncollapsed
        symmetricTwo_no_asymmetryProtoTeleologicalSeed))

end ProtoTeleologicalSeedDiscipline
end Trajectory
end OmegaProper
