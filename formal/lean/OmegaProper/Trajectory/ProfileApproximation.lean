import OmegaProper.Trajectory.ApproximationContract
import OmegaProper.Trajectory.ProfileAbstraction

/-!
OmegaProper.Trajectory.ProfileApproximation

Profile abstraction as generic sound/complete approximation.
-/

namespace OmegaProper
namespace Trajectory
namespace ProfileApproximation

open ApproximationContract
open ConsequenceRelation
open DeformationProfile
open ProfileAbstraction

universe u k o

/-- Ordered fragment-pair index for profile claims. -/
abbrev PairIndex (X : Type u) : Type u :=
  Prod X X

def ExactAllowClaim
    (S : ConsequenceSystem.{u, k, o}) :
    PairIndex S.Fragment -> Prop :=
  fun p => ProfileAllows S p.fst p.snd

def ExactBlockClaim
    (S : ConsequenceSystem.{u, k, o}) :
    PairIndex S.Fragment -> Prop :=
  fun p => ProfileBlocks S p.fst p.snd

def AbstractAllowClaim
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    PairIndex S.Fragment -> Prop :=
  fun p => AbstractionAllows P p.fst p.snd

def AbstractBlockClaim
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    PairIndex S.Fragment -> Prop :=
  fun p => AbstractionBlocks P p.fst p.snd

theorem soundAllows_iff_soundApprox_allow
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    SoundAllows P <->
      SoundApprox (ExactAllowClaim S) (AbstractAllowClaim P) := by
  constructor
  case mp =>
    intro hSound p hAbs
    exact hSound hAbs
  case mpr =>
    intro hSound a b hAbs
    exact hSound (a, b) hAbs

theorem soundBlocks_iff_soundApprox_block
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    SoundBlocks P <->
      SoundApprox (ExactBlockClaim S) (AbstractBlockClaim P) := by
  constructor
  case mp =>
    intro hSound p hAbs
    exact hSound hAbs
  case mpr =>
    intro hSound a b hAbs
    exact hSound (a, b) hAbs

theorem completeForAllows_iff_completeApprox_allow
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    CompleteForAllows P <->
      CompleteApprox (ExactAllowClaim S) (AbstractAllowClaim P) := by
  constructor
  case mp =>
    intro hComplete p hExact
    exact hComplete hExact
  case mpr =>
    intro hComplete a b hExact
    exact hComplete (a, b) hExact

theorem completeForBlocks_iff_completeApprox_block
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    CompleteForBlocks P <->
      CompleteApprox (ExactBlockClaim S) (AbstractBlockClaim P) := by
  constructor
  case mp =>
    intro hComplete p hExact
    exact hComplete hExact
  case mpr =>
    intro hComplete a b hExact
    exact hComplete (a, b) hExact

theorem soundProfile_iff_soundApprox_pair
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    SoundProfileAbstraction P <->
      SoundApprox (ExactAllowClaim S) (AbstractAllowClaim P) /\
        SoundApprox (ExactBlockClaim S) (AbstractBlockClaim P) := by
  constructor
  case mp =>
    intro hSound
    exact And.intro
      ((soundAllows_iff_soundApprox_allow P).mp hSound.left)
      ((soundBlocks_iff_soundApprox_block P).mp hSound.right)
  case mpr =>
    intro hSound
    exact And.intro
      ((soundAllows_iff_soundApprox_allow P).mpr hSound.left)
      ((soundBlocks_iff_soundApprox_block P).mpr hSound.right)

theorem completeProfile_iff_completeApprox_pair
    {S : ConsequenceSystem.{u, k, o}}
    (P : Abstraction S) :
    CompleteProfileAbstraction P <->
      CompleteApprox (ExactAllowClaim S) (AbstractAllowClaim P) /\
        CompleteApprox (ExactBlockClaim S) (AbstractBlockClaim P) := by
  constructor
  case mp =>
    intro hComplete
    exact And.intro
      ((completeForAllows_iff_completeApprox_allow P).mp hComplete.left)
      ((completeForBlocks_iff_completeApprox_block P).mp hComplete.right)
  case mpr =>
    intro hComplete
    exact And.intro
      ((completeForAllows_iff_completeApprox_allow P).mpr hComplete.left)
      ((completeForBlocks_iff_completeApprox_block P).mpr hComplete.right)

end ProfileApproximation
end Trajectory
end OmegaProper
