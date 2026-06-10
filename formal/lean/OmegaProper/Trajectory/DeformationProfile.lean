import OmegaProper.Trajectory.AlphaConsequenceSeed
import OmegaProper.Trajectory.ConsequenceDiscipline

/-!
OmegaProper.Trajectory.DeformationProfile

Status: speculative formal extension / pre-recoverability bridge.

This file defines exact qualitative profile views over consequence systems and
strict block-vs-allow profile deformation between two `AlphaConsequenceSystem`s
over the same Alpha frame.

The shared Alpha carrier is a measurement setup, not an identity claim. This
file does not define recoverability, identity, persistence, coarse-graining,
deformer structure, boundary, value, valuerhood, agency, Omega-seed, or
Omega-terminal.
-/

namespace OmegaProper
namespace Trajectory
namespace DeformationProfile

open AlphaConsequenceSeed
open ConsequenceDiscipline
open ConsequenceRelation

universe u v k o k' o'

/-- A profile blocks a pair when symmetric merge/identification is separated. -/
abbrev ProfileBlocks
    (S : ConsequenceSystem.{u, k, o})
    (a b : S.Fragment) : Prop :=
  ConsequenceMergeSeparated S a b

/-- A profile allows a pair when both directed consequence comparisons hold. -/
abbrev ProfileAllows
    (S : ConsequenceSystem.{u, k, o})
    (a b : S.Fragment) : Prop :=
  ConsequenceIdentifiable S a b

/-- A consequence system has a nonempty merge-block profile. -/
def HasBlockProfile
    (S : ConsequenceSystem.{u, k, o}) : Prop :=
  exists a b : S.Fragment, ProfileBlocks S a b

theorem profileBlock_implies_hasBlockProfile
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileBlocks S a b) :
    HasBlockProfile S := by
  exact Exists.intro a (Exists.intro b h)

theorem profileBlock_not_profileAllow
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileBlocks S a b) :
    Not (ProfileAllows S a b) := by
  exact mergeSeparated_blocks_identifiable h

theorem profileAllow_not_profileBlock
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileAllows S a b) :
    Not (ProfileBlocks S a b) := by
  intro hBlock
  exact profileBlock_not_profileAllow hBlock h

theorem collapsed_no_profileBlocks
    {S : ConsequenceSystem.{u, k, o}}
    (h : ConsequenceCollapsed S)
    {a b : S.Fragment} :
    Not (ProfileBlocks S a b) := by
  intro hBlock
  cases hBlock with
  | inl hSep =>
      exact compatible_not_separated (h a b) hSep
  | inr hSep =>
      exact compatible_not_separated (h b a) hSep

theorem collapsed_no_blockProfile
    {S : ConsequenceSystem.{u, k, o}}
    (h : ConsequenceCollapsed S) :
    Not (HasBlockProfile S) := by
  intro hProfile
  match hProfile with
  | Exists.intro a ha =>
      match ha with
      | Exists.intro b hBlock =>
          exact collapsed_no_profileBlocks h hBlock

theorem universalComparison_no_blockProfile
    {S : ConsequenceSystem.{u, k, o}}
    (h : ComparisonUniversalOnEvaluated S) :
    Not (HasBlockProfile S) := by
  exact collapsed_no_blockProfile (universal_comparison_collapses h)

/--
The strict block/allow status of a pair changed between two consequence systems
over the same Alpha frame.

This detects only a clean flip between merge-blocked and merge-allowed. It does
not detect all possible profile differences.
-/
def AlphaProfileBlockChanged
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (T : AlphaConsequenceSystem.{u, v, k', o'} A)
    (a b : A.X) : Prop :=
  (ProfileBlocks S.toConsequenceSystem a b /\
    ProfileAllows T.toConsequenceSystem a b) \/
  (ProfileAllows S.toConsequenceSystem a b /\
    ProfileBlocks T.toConsequenceSystem a b)

/--
Two Alpha consequence systems strictly deform each other's exact qualitative
profile when some pair changes between merge-blocked and merge-allowed.
-/
def AlphaProfileDeforms
    {A : AlphaCore.Frame.{u, v}}
    (S : AlphaConsequenceSystem.{u, v, k, o} A)
    (T : AlphaConsequenceSystem.{u, v, k', o'} A) : Prop :=
  exists a b : A.X, AlphaProfileBlockChanged S T a b

theorem alphaProfileBlockChanged_symm
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {T : AlphaConsequenceSystem.{u, v, k', o'} A}
    {a b : A.X}
    (h : AlphaProfileBlockChanged S T a b) :
    AlphaProfileBlockChanged T S a b := by
  cases h with
  | inl hST =>
      exact Or.inr (And.intro hST.right hST.left)
  | inr hST =>
      exact Or.inl (And.intro hST.right hST.left)

theorem alphaProfileDeforms_symm
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {T : AlphaConsequenceSystem.{u, v, k', o'} A}
    (h : AlphaProfileDeforms S T) :
    AlphaProfileDeforms T S := by
  match h with
  | Exists.intro a ha =>
      match ha with
      | Exists.intro b hChanged =>
          exact Exists.intro a
            (Exists.intro b (alphaProfileBlockChanged_symm hChanged))

theorem alphaProfileDeforms_of_block_allow
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {T : AlphaConsequenceSystem.{u, v, k', o'} A}
    {a b : A.X}
    (hBlock : ProfileBlocks S.toConsequenceSystem a b)
    (hAllow : ProfileAllows T.toConsequenceSystem a b) :
    AlphaProfileDeforms S T := by
  exact Exists.intro a
    (Exists.intro b (Or.inl (And.intro hBlock hAllow)))

theorem alphaProfileDeforms_of_allow_block
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {T : AlphaConsequenceSystem.{u, v, k', o'} A}
    {a b : A.X}
    (hAllow : ProfileAllows S.toConsequenceSystem a b)
    (hBlock : ProfileBlocks T.toConsequenceSystem a b) :
    AlphaProfileDeforms S T := by
  exact Exists.intro a
    (Exists.intro b (Or.inr (And.intro hAllow hBlock)))

theorem alphaProfileBlockChanged_not_self
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A}
    {a b : A.X} :
    Not (AlphaProfileBlockChanged S S a b) := by
  intro h
  cases h with
  | inl hBoth =>
      exact profileBlock_not_profileAllow hBoth.left hBoth.right
  | inr hBoth =>
      exact profileBlock_not_profileAllow hBoth.right hBoth.left

theorem alphaProfileDeforms_not_self
    {A : AlphaCore.Frame.{u, v}}
    {S : AlphaConsequenceSystem.{u, v, k, o} A} :
    Not (AlphaProfileDeforms S S) := by
  intro h
  match h with
  | Exists.intro a ha =>
      match ha with
      | Exists.intro b hChanged =>
          exact alphaProfileBlockChanged_not_self hChanged

end DeformationProfile
end Trajectory
end OmegaProper
