import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.BaselineWitnesses.InvarianceNonFactorization
import OmegaProper.BaselineWitnesses.NonFactorization

/-!
OmegaProper.BaselineWitnesses.ReachabilityDeclaredRecovery

Lean conversion of the finite witness:
`same_reachability_different_recovery`.

Two support relations have the same coarse finite reachability shape: each
source reaches exactly two targets, and every target is globally reachable.
Only the first-coordinate support relation recovers the declared first
coordinate.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace ReachabilityDeclaredRecovery

open NonFactorization
open InvarianceNonFactorization

/-- A finite reachability/support relation. -/
abbrev SupportRelation := X2 -> X2 -> Prop

def sameFirstReach : SupportRelation :=
  fun source target => firstBit target = firstBit source

def sameSecondReach : SupportRelation :=
  fun source target => secondBit target = secondBit source

/-! ## Computed summary/target form -/

/-- Which of the two finite support relations is being summarized. -/
inductive ReachabilityExposure where
  | sameFirst
  | sameSecond
  deriving DecidableEq

def swapReachabilityExposure : ReachabilityExposure -> ReachabilityExposure
  | ReachabilityExposure.sameFirst => ReachabilityExposure.sameSecond
  | ReachabilityExposure.sameSecond => ReachabilityExposure.sameFirst

def supportOfExposure : ReachabilityExposure -> SupportRelation
  | ReachabilityExposure.sameFirst => sameFirstReach
  | ReachabilityExposure.sameSecond => sameSecondReach

def supportBool : ReachabilityExposure -> X2 -> X2 -> Bool
  | ReachabilityExposure.sameFirst, source, target =>
      decide (firstBit target = firstBit source)
  | ReachabilityExposure.sameSecond, source, target =>
      decide (secondBit target = secondBit source)

def reachableOrderedPairCount (e : ReachabilityExposure) : Nat :=
  (x2OrderedPairs.filter (fun p => supportBool e p.1 p.2)).length

def sourceReachCount (e : ReachabilityExposure) (source : X2) : Nat :=
  (x2States.filter (fun target => supportBool e source target)).length

def targetSupportCount (e : ReachabilityExposure) (target : X2) : Nat :=
  (x2States.filter (fun source => supportBool e source target)).length

def sourceReachCountSignature (e : ReachabilityExposure) : List Nat :=
  [sourceReachCount e X2.x00, sourceReachCount e X2.x01,
    sourceReachCount e X2.x10, sourceReachCount e X2.x11]

def targetSupportCountSignature (e : ReachabilityExposure) : List Nat :=
  [targetSupportCount e X2.x00, targetSupportCount e X2.x01,
    targetSupportCount e X2.x10, targetSupportCount e X2.x11]

/--
Computed coarse reachability summary: how many targets each source reaches,
how many sources reach each target, and the total reachable ordered-pair count.
-/
structure ReachabilityCountSummary where
  sourceCount : Nat
  targetCount : Nat
  sourceReachCounts : List Nat
  targetSupportCounts : List Nat
  reachableOrderedPairs : Nat
  deriving DecidableEq

def balancedReachabilityCountSummary : ReachabilityCountSummary where
  sourceCount := 4
  targetCount := 4
  sourceReachCounts := [2, 2, 2, 2]
  targetSupportCounts := [2, 2, 2, 2]
  reachableOrderedPairs := 8

def reachabilitySummaryOfExposure
    (e : ReachabilityExposure) : ReachabilityCountSummary where
  sourceCount := x2States.length
  targetCount := x2States.length
  sourceReachCounts := sourceReachCountSignature e
  targetSupportCounts := targetSupportCountSignature e
  reachableOrderedPairs := reachableOrderedPairCount e

def declaredRecoveryViolationCount (e : ReachabilityExposure) : Nat :=
  (x2OrderedPairs.filter (fun p =>
    supportBool e p.1 p.2 &&
      decide (Not (firstBit p.2 = firstBit p.1)))).length

def declaredRecoveryTargetOfExposure (e : ReachabilityExposure) : Bool :=
  decide (declaredRecoveryViolationCount e = 0)

theorem reachabilitySummary_sameFirst :
    reachabilitySummaryOfExposure ReachabilityExposure.sameFirst =
      balancedReachabilityCountSummary := by
  native_decide

theorem reachabilitySummary_sameSecond :
    reachabilitySummaryOfExposure ReachabilityExposure.sameSecond =
      balancedReachabilityCountSummary := by
  native_decide

theorem same_reachability_computed_summary :
    reachabilitySummaryOfExposure ReachabilityExposure.sameFirst =
      reachabilitySummaryOfExposure ReachabilityExposure.sameSecond := by
  rw [reachabilitySummary_sameFirst, reachabilitySummary_sameSecond]

theorem sameFirst_declaredRecoveryTarget :
    declaredRecoveryTargetOfExposure ReachabilityExposure.sameFirst = true := by
  native_decide

theorem sameSecond_declaredRecoveryTarget :
    declaredRecoveryTargetOfExposure ReachabilityExposure.sameSecond = false := by
  native_decide

theorem different_declaredRecoveryTarget :
    Not (
      declaredRecoveryTargetOfExposure ReachabilityExposure.sameFirst =
        declaredRecoveryTargetOfExposure ReachabilityExposure.sameSecond
    ) := by
  native_decide

theorem reachabilitySummary_invariantUnder_swap :
    SummaryInvariantUnder
      reachabilitySummaryOfExposure
      swapReachabilityExposure := by
  intro e
  cases e
  case sameFirst =>
    exact Eq.symm same_reachability_computed_summary
  case sameSecond =>
    exact same_reachability_computed_summary

theorem reachabilityTarget_changesUnder_swap :
    TargetChangesUnder
      declaredRecoveryTargetOfExposure
      swapReachabilityExposure := by
  exact Exists.intro ReachabilityExposure.sameFirst (by native_decide)

theorem reachability_computedSummary_nonFactorization :
    NonFactorization
      reachabilitySummaryOfExposure
      declaredRecoveryTargetOfExposure := by
  exact invariant_summary_target_change_nonFactorization
    reachabilitySummary_invariantUnder_swap
    reachabilityTarget_changesUnder_swap

def SourceExactlyTwoTargets (R : SupportRelation) (source : X2) : Prop :=
  exists a b : X2,
    Not (a = b) /\
    R source a /\
    R source b /\
    forall target, R source target -> target = a \/ target = b

def UniformTwoTargetReach (R : SupportRelation) : Prop :=
  forall source, SourceExactlyTwoTargets R source

def GlobalTargetSupport (R : SupportRelation) : Prop :=
  forall target, exists source, R source target

def ReachabilityBaseline (R : SupportRelation) : Prop :=
  UniformTwoTargetReach R /\ GlobalTargetSupport R

def SupportRecoversDeclaredFirst (R : SupportRelation) : Prop :=
  forall source target, R source target -> firstBit target = firstBit source

theorem sameFirst_x00_exactlyTwo :
    SourceExactlyTwoTargets sameFirstReach X2.x00 := by
  exists X2.x00
  exists X2.x01
  constructor
  case left =>
    intro h
    cases h
  case right =>
    constructor
    case left =>
      rfl
    case right =>
      constructor
      case left =>
        rfl
      case right =>
        intro target h
        cases target
        case x00 => exact Or.inl rfl
        case x01 => exact Or.inr rfl
        case x10 => cases h
        case x11 => cases h

theorem sameFirst_x01_exactlyTwo :
    SourceExactlyTwoTargets sameFirstReach X2.x01 := by
  exact sameFirst_x00_exactlyTwo

theorem sameFirst_x10_exactlyTwo :
    SourceExactlyTwoTargets sameFirstReach X2.x10 := by
  exists X2.x10
  exists X2.x11
  constructor
  case left =>
    intro h
    cases h
  case right =>
    constructor
    case left =>
      rfl
    case right =>
      constructor
      case left =>
        rfl
      case right =>
        intro target h
        cases target
        case x00 => cases h
        case x01 => cases h
        case x10 => exact Or.inl rfl
        case x11 => exact Or.inr rfl

theorem sameFirst_x11_exactlyTwo :
    SourceExactlyTwoTargets sameFirstReach X2.x11 := by
  exact sameFirst_x10_exactlyTwo

theorem sameSecond_x00_exactlyTwo :
    SourceExactlyTwoTargets sameSecondReach X2.x00 := by
  exists X2.x00
  exists X2.x10
  constructor
  case left =>
    intro h
    cases h
  case right =>
    constructor
    case left =>
      rfl
    case right =>
      constructor
      case left =>
        rfl
      case right =>
        intro target h
        cases target
        case x00 => exact Or.inl rfl
        case x01 => cases h
        case x10 => exact Or.inr rfl
        case x11 => cases h

theorem sameSecond_x10_exactlyTwo :
    SourceExactlyTwoTargets sameSecondReach X2.x10 := by
  exact sameSecond_x00_exactlyTwo

theorem sameSecond_x01_exactlyTwo :
    SourceExactlyTwoTargets sameSecondReach X2.x01 := by
  exists X2.x01
  exists X2.x11
  constructor
  case left =>
    intro h
    cases h
  case right =>
    constructor
    case left =>
      rfl
    case right =>
      constructor
      case left =>
        rfl
      case right =>
        intro target h
        cases target
        case x00 => cases h
        case x01 => exact Or.inl rfl
        case x10 => cases h
        case x11 => exact Or.inr rfl

theorem sameSecond_x11_exactlyTwo :
    SourceExactlyTwoTargets sameSecondReach X2.x11 := by
  exact sameSecond_x01_exactlyTwo

theorem sameFirst_uniformTwoTargetReach :
    UniformTwoTargetReach sameFirstReach := by
  intro source
  cases source
  case x00 => exact sameFirst_x00_exactlyTwo
  case x01 => exact sameFirst_x01_exactlyTwo
  case x10 => exact sameFirst_x10_exactlyTwo
  case x11 => exact sameFirst_x11_exactlyTwo

theorem sameSecond_uniformTwoTargetReach :
    UniformTwoTargetReach sameSecondReach := by
  intro source
  cases source
  case x00 => exact sameSecond_x00_exactlyTwo
  case x01 => exact sameSecond_x01_exactlyTwo
  case x10 => exact sameSecond_x10_exactlyTwo
  case x11 => exact sameSecond_x11_exactlyTwo

theorem sameFirst_globalTargetSupport :
    GlobalTargetSupport sameFirstReach := by
  intro target
  exists target

theorem sameSecond_globalTargetSupport :
    GlobalTargetSupport sameSecondReach := by
  intro target
  exists target

theorem sameFirst_reachabilityBaseline :
    ReachabilityBaseline sameFirstReach := by
  exact And.intro sameFirst_uniformTwoTargetReach sameFirst_globalTargetSupport

theorem sameSecond_reachabilityBaseline :
    ReachabilityBaseline sameSecondReach := by
  exact And.intro sameSecond_uniformTwoTargetReach sameSecond_globalTargetSupport

theorem sameFirst_recoversDeclaredFirst :
    SupportRecoversDeclaredFirst sameFirstReach := by
  intro source target h
  exact h

theorem sameSecond_not_recoversDeclaredFirst :
    Not (SupportRecoversDeclaredFirst sameSecondReach) := by
  intro hRecovers
  have hReach : sameSecondReach X2.x00 X2.x10 := rfl
  have hSameFirst := hRecovers X2.x00 X2.x10 hReach
  cases hSameFirst

theorem same_reachability_baseline_different_declared_recovery :
    ReachabilityBaseline sameFirstReach /\
    ReachabilityBaseline sameSecondReach /\
    SupportRecoversDeclaredFirst sameFirstReach /\
    Not (SupportRecoversDeclaredFirst sameSecondReach) := by
  exact And.intro sameFirst_reachabilityBaseline
    (And.intro sameSecond_reachabilityBaseline
      (And.intro sameFirst_recoversDeclaredFirst
        sameSecond_not_recoversDeclaredFirst))

end ReachabilityDeclaredRecovery
end BaselineWitnesses
end OmegaProper
