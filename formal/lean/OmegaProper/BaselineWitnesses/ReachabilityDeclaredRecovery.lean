import OmegaProper.BaselineWitnesses.FiniteBits

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

/-- A finite reachability/support relation. -/
abbrev SupportRelation := X2 -> X2 -> Prop

def sameFirstReach : SupportRelation :=
  fun source target => firstBit target = firstBit source

def sameSecondReach : SupportRelation :=
  fun source target => secondBit target = secondBit source

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
