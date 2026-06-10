import OmegaProper.Trajectory.DeformationProfile

/-!
OmegaProper.Trajectory.ProfileAbstraction

Abstraction contracts for exact consequence profiles.

An abstraction is not an identity claim. It is a coarse view that may claim
that a fragment pair is merge-allowed or merge-blocked. Those claims only
become usable through explicit soundness and completeness contracts against
the exact profile.

This file does not define recoverability, identity, persistence, deformer
structure, boundary, value, valuerhood, agency, Omega-seed, or Omega-terminal.
-/

namespace OmegaProper
namespace Trajectory
namespace ProfileAbstraction

open ConsequenceRelation
open DeformationProfile

universe u k o

/--
A coarse profile view over an exact consequence system.

`allows` and `blocks` are claims made by the abstraction. They are not trusted
unless soundness/completeness contracts are supplied separately.
-/
structure Abstraction (S : ConsequenceSystem.{u, k, o}) where
  allows : S.Fragment -> S.Fragment -> Prop
  blocks : S.Fragment -> S.Fragment -> Prop

abbrev AbstractionAllows
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S)
    (a b : S.Fragment) : Prop :=
  P.allows a b

abbrev AbstractionBlocks
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S)
    (a b : S.Fragment) : Prop :=
  P.blocks a b

def SoundAllows
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) : Prop :=
  forall {a b : S.Fragment},
    AbstractionAllows P a b ->
    ProfileAllows S a b

def SoundBlocks
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) : Prop :=
  forall {a b : S.Fragment},
    AbstractionBlocks P a b ->
    ProfileBlocks S a b

def SoundProfileAbstraction
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) : Prop :=
  SoundAllows P /\ SoundBlocks P

def CompleteForAllows
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) : Prop :=
  forall {a b : S.Fragment},
    ProfileAllows S a b ->
    AbstractionAllows P a b

def CompleteForBlocks
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) : Prop :=
  forall {a b : S.Fragment},
    ProfileBlocks S a b ->
    AbstractionBlocks P a b

def CompleteProfileAbstraction
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) : Prop :=
  CompleteForAllows P /\ CompleteForBlocks P

def HasAllowProfile
    (S : ConsequenceSystem.{u, k, o}) : Prop :=
  exists a b : S.Fragment, ProfileAllows S a b

theorem soundProfile_no_allow_and_block
    {S : ConsequenceSystem.{u, k, o}}
    {P : Abstraction S}
    (hSound : SoundProfileAbstraction P)
    {a b : S.Fragment}
    (hAllow : AbstractionAllows P a b)
    (hBlock : AbstractionBlocks P a b) :
    False := by
  exact profileBlock_not_profileAllow
    (hSound.right hBlock)
    (hSound.left hAllow)

/-- The abstraction that claims nothing. It is sound but generally incomplete. -/
def EmptyAbstraction (S : ConsequenceSystem.{u, k, o}) :
    Abstraction S where
  allows := fun _ _ => False
  blocks := fun _ _ => False

theorem empty_soundAllows
    (S : ConsequenceSystem.{u, k, o}) :
    SoundAllows (EmptyAbstraction S) := by
  intro _a _b h
  cases h

theorem empty_soundBlocks
    (S : ConsequenceSystem.{u, k, o}) :
    SoundBlocks (EmptyAbstraction S) := by
  intro _a _b h
  cases h

theorem empty_soundProfile
    (S : ConsequenceSystem.{u, k, o}) :
    SoundProfileAbstraction (EmptyAbstraction S) := by
  exact And.intro (empty_soundAllows S) (empty_soundBlocks S)

theorem empty_not_completeForBlocks_of_block
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileBlocks S a b) :
    Not (CompleteForBlocks (EmptyAbstraction S)) := by
  intro hComplete
  exact hComplete h

theorem empty_not_completeProfile_of_block
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileBlocks S a b) :
    Not (CompleteProfileAbstraction (EmptyAbstraction S)) := by
  intro hComplete
  exact empty_not_completeForBlocks_of_block h hComplete.right

/--
The abstraction that allows every merge and blocks none.
It fails allow-soundness whenever the exact profile has a blocked pair.
-/
def UniversalAllowAbstraction (S : ConsequenceSystem.{u, k, o}) :
    Abstraction S where
  allows := fun _ _ => True
  blocks := fun _ _ => False

theorem universalAllow_not_soundAllows_of_block
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileBlocks S a b) :
    Not (SoundAllows (UniversalAllowAbstraction S)) := by
  intro hSound
  exact profileBlock_not_profileAllow h (hSound trivial)

theorem universalAllow_not_soundAllows_of_blockProfile
    {S : ConsequenceSystem.{u, k, o}}
    (h : HasBlockProfile S) :
    Not (SoundAllows (UniversalAllowAbstraction S)) := by
  match h with
  | Exists.intro a ha =>
      match ha with
      | Exists.intro b hBlock =>
          exact universalAllow_not_soundAllows_of_block hBlock

/--
The abstraction that blocks every merge and allows none.
It fails allow-completeness whenever the exact profile has an allowed pair.
-/
def UniversalBlockAbstraction (S : ConsequenceSystem.{u, k, o}) :
    Abstraction S where
  allows := fun _ _ => False
  blocks := fun _ _ => True

theorem universalBlock_not_completeForAllows_of_allow
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileAllows S a b) :
    Not (CompleteForAllows (UniversalBlockAbstraction S)) := by
  intro hComplete
  exact hComplete h

theorem universalBlock_not_completeForAllows_of_allowProfile
    {S : ConsequenceSystem.{u, k, o}}
    (h : HasAllowProfile S) :
    Not (CompleteForAllows (UniversalBlockAbstraction S)) := by
  match h with
  | Exists.intro a ha =>
      match ha with
      | Exists.intro b hAllow =>
          exact universalBlock_not_completeForAllows_of_allow hAllow

/--
The abstraction that claims both allow and block for every pair.
It is complete by construction, but generally unsound.
-/
def TotalAbstraction (S : ConsequenceSystem.{u, k, o}) :
    Abstraction S where
  allows := fun _ _ => True
  blocks := fun _ _ => True

theorem total_completeForAllows
    (S : ConsequenceSystem.{u, k, o}) :
    CompleteForAllows (TotalAbstraction S) := by
  intro _a _b _hAllow
  trivial

theorem total_completeForBlocks
    (S : ConsequenceSystem.{u, k, o}) :
    CompleteForBlocks (TotalAbstraction S) := by
  intro _a _b _hBlock
  trivial

theorem total_completeProfile
    (S : ConsequenceSystem.{u, k, o}) :
    CompleteProfileAbstraction (TotalAbstraction S) := by
  exact And.intro (total_completeForAllows S) (total_completeForBlocks S)

theorem total_not_soundAllows_of_block
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileBlocks S a b) :
    Not (SoundAllows (TotalAbstraction S)) := by
  intro hSound
  exact profileBlock_not_profileAllow h (hSound trivial)

theorem total_not_soundProfile_of_block
    {S : ConsequenceSystem.{u, k, o}} {a b : S.Fragment}
    (h : ProfileBlocks S a b) :
    Not (SoundProfileAbstraction (TotalAbstraction S)) := by
  intro hSound
  exact total_not_soundAllows_of_block h hSound.left

theorem toy_hasBlockProfile :
    HasBlockProfile nonTransitiveToySystem := by
  exact profileBlock_implies_hasBlockProfile
    (S := nonTransitiveToySystem)
    (a := ToyFragment.a)
    (b := ToyFragment.c)
    (Or.inl toy_a_separated_c)

theorem soundness_not_sufficient_for_completeness :
    exists S : ConsequenceSystem.{0, 0, 0},
      exists P : Abstraction S,
        SoundProfileAbstraction P /\
        Not (CompleteProfileAbstraction P) := by
  exact Exists.intro nonTransitiveToySystem
    (Exists.intro (EmptyAbstraction nonTransitiveToySystem)
      (And.intro
        (empty_soundProfile nonTransitiveToySystem)
        (empty_not_completeProfile_of_block
          (S := nonTransitiveToySystem)
          (a := ToyFragment.a)
          (b := ToyFragment.c)
          (Or.inl toy_a_separated_c))))

theorem completeness_not_sufficient_for_soundness :
    exists S : ConsequenceSystem.{0, 0, 0},
      exists P : Abstraction S,
        CompleteProfileAbstraction P /\
        Not (SoundProfileAbstraction P) := by
  exact Exists.intro nonTransitiveToySystem
    (Exists.intro (TotalAbstraction nonTransitiveToySystem)
      (And.intro
        (total_completeProfile nonTransitiveToySystem)
        (total_not_soundProfile_of_block
          (S := nonTransitiveToySystem)
          (a := ToyFragment.a)
          (b := ToyFragment.c)
          (Or.inl toy_a_separated_c))))

end ProfileAbstraction
end Trajectory
end OmegaProper
