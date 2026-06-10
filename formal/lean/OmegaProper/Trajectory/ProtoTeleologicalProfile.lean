import OmegaProper.Trajectory.ProfileAbstraction
import OmegaProper.Trajectory.ProtoTeleologicalSeed

/-!
OmegaProper.Trajectory.ProtoTeleologicalProfile

Bridge from proto-teleological seed conditions to exact consequence profiles.

This file closes the loop between the seed layer and the deformation/profile
layer: a proto-teleological seed supplies a nonempty merge-block profile.

It does not define recoverability, identity, persistence, coarse-graining,
deformer structure, boundary, value, valuerhood, agency, Omega-seed, or
Omega-terminal.
-/

namespace OmegaProper
namespace Trajectory
namespace ProtoTeleologicalProfile

open AlphaConsequenceSeed
open DeformationProfile
open ProfileAbstraction
open ProtoTeleologicalSeed

universe u v k o

theorem jointSeed_hasBlockProfile
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : JointProtoTeleologicalSeed S) :
    HasBlockProfile S.toConsequenceSystem := by
  match h with
  | Exists.intro w hBearing =>
      exact profileBlock_implies_hasBlockProfile
        (S := S.toConsequenceSystem)
        (a := w.x)
        (b := w.y)
        hBearing

theorem asymmetrySeed_hasBlockProfile
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : AsymmetryProtoTeleologicalSeed S) :
    HasBlockProfile S.toConsequenceSystem := by
  match h with
  | Exists.intro w hBearing =>
      exact profileBlock_implies_hasBlockProfile
        (S := S.toConsequenceSystem)
        (a := w.x)
        (b := w.y)
        hBearing

theorem protoSeed_hasBlockProfile
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : ProtoTeleologicalSeed S) :
    HasBlockProfile S.toConsequenceSystem := by
  exact asymmetrySeed_hasBlockProfile h

theorem protoSeed_not_consequenceCollapsed
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : ProtoTeleologicalSeed S) :
    Not (ConsequenceRelation.ConsequenceCollapsed S.toConsequenceSystem) := by
  intro hCollapsed
  exact collapsed_no_blockProfile hCollapsed
    (protoSeed_hasBlockProfile h)

theorem protoSeed_blocks_universalAllowSoundness
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    (h : ProtoTeleologicalSeed S) :
    Not (SoundAllows (UniversalAllowAbstraction S.toConsequenceSystem)) := by
  exact universalAllow_not_soundAllows_of_blockProfile
    (protoSeed_hasBlockProfile h)

end ProtoTeleologicalProfile
end Trajectory
end OmegaProper
