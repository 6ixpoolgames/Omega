import OmegaProper.Trajectory.AlphaConsequenceSeed
import OmegaProper.Trajectory.ConsequenceDiscipline

/-!
OmegaProper.Trajectory.ProtoTeleologicalSeed

Minimal proto-teleological seed wrappers.

This file does not define purpose, value, agency, identity, deformer structure,
boundary, valuerhood, Omega-seed, or Omega-terminal. It only names the small
formal hinge:

  primitive Alpha contact + evaluated consequence merge-separation

The joint-witness version is primary. The asymmetry-witness version factors
through `AsymmetryPrimitiveWitness.toJoint`.
-/

namespace OmegaProper
namespace Trajectory
namespace ProtoTeleologicalSeed

open ConsequenceRelation
open ConsequenceDiscipline
open AlphaConsequenceSeed

universe u v k o

/--
A joint proto-teleological seed is relation/separation contact whose endpoints
are merge-separated by evaluated consequence.
-/
def JointProtoTeleologicalSeed
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A) : Prop :=
  exists w : AlphaCore.Frame.JointPrimitiveWitness A,
    ConsequenceBearingJointWitness S w

/--
An asymmetry proto-teleological seed is an asymmetry witness whose supplied
joint witness is merge-separated by evaluated consequence.
-/
def AsymmetryProtoTeleologicalSeed
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A) : Prop :=
  exists w : AlphaCore.Frame.AsymmetryPrimitiveWitness A,
    ConsequenceBearingAlphaWitness S w

/--
Compatibility name for the current Alpha-native seed: asymmetry witness plus
evaluated consequence merge-separation.
-/
abbrev ProtoTeleologicalSeed
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A) : Prop :=
  AsymmetryProtoTeleologicalSeed S

theorem asymmetrySeed_implies_jointSeed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : AsymmetryProtoTeleologicalSeed S) :
    JointProtoTeleologicalSeed S := by
  match h with
  | Exists.intro w hBearing =>
      exact Exists.intro w.toJoint hBearing

theorem jointSeed_implies_jointPrimitiveWitness
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : JointProtoTeleologicalSeed S) :
    AlphaCore.Frame.HasJointPrimitiveWitness A := by
  match h with
  | Exists.intro w _hBearing =>
      exact Nonempty.intro w

theorem asymmetrySeed_implies_primitiveNondegenerate
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : AsymmetryProtoTeleologicalSeed S) :
    AlphaCore.Frame.PrimitiveNondegenerate A := by
  match h with
  | Exists.intro w _hBearing =>
      exact Nonempty.intro w

theorem jointSeed_implies_consequenceNoncollapsed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : JointProtoTeleologicalSeed S) :
    ConsequenceNoncollapsed S.toConsequenceSystem := by
  match h with
  | Exists.intro w hBearing =>
      cases hBearing with
      | inl hsep =>
          exact Exists.intro w.x (Exists.intro w.y hsep)
      | inr hsep =>
          exact Exists.intro w.y (Exists.intro w.x hsep)

theorem asymmetrySeed_implies_consequenceNoncollapsed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : AsymmetryProtoTeleologicalSeed S) :
    ConsequenceNoncollapsed S.toConsequenceSystem := by
  exact jointSeed_implies_consequenceNoncollapsed
    (asymmetrySeed_implies_jointSeed h)

theorem jointSeed_blocks_consequenceCollapse
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : JointProtoTeleologicalSeed S) :
    Not (ConsequenceCollapsed S.toConsequenceSystem) := by
  exact separated_pair_not_collapsed
    (jointSeed_implies_consequenceNoncollapsed h)

theorem asymmetrySeed_blocks_consequenceCollapse
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : AsymmetryProtoTeleologicalSeed S) :
    Not (ConsequenceCollapsed S.toConsequenceSystem) := by
  exact jointSeed_blocks_consequenceCollapse
    (asymmetrySeed_implies_jointSeed h)

theorem jointSeed_has_witness_blocking_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : JointProtoTeleologicalSeed S) :
    exists w : AlphaCore.Frame.JointPrimitiveWitness A,
      ConsequenceBearingJointWitness S w /\
      Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  match h with
  | Exists.intro w hBearing =>
      exact Exists.intro w
        (And.intro hBearing
          (jointWitness_mergeSeparated_blocks_identification hBearing))

theorem asymmetrySeed_has_witness_blocking_identification
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : AsymmetryProtoTeleologicalSeed S) :
    exists w : AlphaCore.Frame.AsymmetryPrimitiveWitness A,
      ConsequenceBearingAlphaWitness S w /\
      Not (ConsequenceIdentifiable S.toConsequenceSystem w.x w.y) := by
  match h with
  | Exists.intro w hBearing =>
      exact Exists.intro w
        (And.intro hBearing
          (asymmetryWitness_mergeSeparated_blocks_identification hBearing))

end ProtoTeleologicalSeed
end Trajectory
end OmegaProper
