import OmegaProper.Trajectory.LossAwarePresentationContract

/-!
OmegaProper.Trajectory.LossAwarePresentationStrictness

Small negative controls showing that loss-aware contracts are strictly stronger
than safe/reflection contracts alone.

A presentation can satisfy the safe/reflection contract vacuously while still
hiding exact reachability or viability loss. Loss visibility is therefore an
extra obligation, not just a restatement of reflection.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace LossAwarePresentationStrictness

open ConsequenceRelation
open HiddenLossUnderBadPresentation
open HiddenViabilityLossUnderBadPresentation
open IrreversibleReachLoss
open IrreversibleViabilityLoss
open LossAwarePresentationContract
open ReachabilityReflection
open ReachabilityViability
open SafeLossVisibility
open SafePresentationContract
open ViabilityReflection

/-- A one-state abstract dynamics with no transitions. -/
def noStepUnitDyn : Dyn where
  State := Unit
  Next := fun _ _ => False

def noTarget (_q : Unit) : Prop :=
  False

def noSafe (_q : Unit) : Prop :=
  False

/--
Universal consequence comparison over the reach-loss witness carrier.

This makes the constant presentation consequence-sound, so the example isolates
loss visibility rather than consequence soundness.
-/
def universalReachLossConsequenceSystem : ConsequenceSystem where
  Fragment := LossState
  Context := Unit
  Outcome := Unit
  consequence := fun _ _ => ()
  Compare := fun _ _ _ => True
  Evaluated := fun _ => True

/--
Universal consequence comparison over the viability-loss witness carrier.
-/
def universalViabilityLossConsequenceSystem : ConsequenceSystem where
  Fragment := ViabilityLossState
  Context := Unit
  Outcome := Unit
  consequence := fun _ _ => ()
  Compare := fun _ _ _ => True
  Evaluated := fun _ => True

theorem reachConstantPresentation_sound :
    SoundQuotient.SoundQuotient
      universalReachLossConsequenceSystem
      HiddenLossUnderBadPresentation.constantPresentation := by
  intro _x _y _hErased
  constructor <;>
    intro _ctx _hEval <;>
    trivial

theorem viabilityConstantPresentation_sound :
    SoundQuotient.SoundQuotient
      universalViabilityLossConsequenceSystem
      HiddenViabilityLossUnderBadPresentation.constantPresentation := by
  intro _x _y _hErased
  constructor <;>
    intro _ctx _hEval <;>
    trivial

theorem noTarget_reflects_reachLoss :
    TargetReflects
      (exactDynFromNext IrreversibleReachLoss.lossNext)
      noStepUnitDyn
      HiddenLossUnderBadPresentation.constantPresentation
      IrreversibleReachLoss.lossTarget
      noTarget := by
  intro _x hTarget
  exact False.elim hTarget

theorem noStep_reflects_reachLoss :
    StepReflects
      (exactDynFromNext IrreversibleReachLoss.lossNext)
      noStepUnitDyn
      HiddenLossUnderBadPresentation.constantPresentation := by
  intro _x _z hStep
  exact False.elim hStep

theorem noSafe_reflects_viabilityLoss :
    SafeReflects
      (exactDynFromNext IrreversibleViabilityLoss.viabilityLossNext)
      noStepUnitDyn
      HiddenViabilityLossUnderBadPresentation.constantPresentation
      IrreversibleViabilityLoss.viabilityLossSafe
      noSafe := by
  intro _x hSafe
  exact False.elim hSafe

theorem noStep_reflects_viabilityLoss :
    StepReflects
      (exactDynFromNext IrreversibleViabilityLoss.viabilityLossNext)
      noStepUnitDyn
      HiddenViabilityLossUnderBadPresentation.constantPresentation := by
  intro _x _z hStep
  exact False.elim hStep

/--
The constant reach-loss presentation satisfies the safe/reflection contract,
but it does not make reachability loss visible.
-/
theorem reachSafeContract_without_lossVisibility :
    ReachabilitySafePresentationContract
      universalReachLossConsequenceSystem
      noStepUnitDyn
      HiddenLossUnderBadPresentation.constantPresentation
      IrreversibleReachLoss.lossNext
      IrreversibleReachLoss.lossTarget
      noTarget /\
    Not (
      ReachLossVisibleToPresentation
        (exactDynFromNext IrreversibleReachLoss.lossNext)
        IrreversibleReachLoss.lossTarget
        HiddenLossUnderBadPresentation.constantPresentation
    ) := by
  constructor
  case left =>
    exact {
      consequence_sound := reachConstantPresentation_sound,
      target_reflects := noTarget_reflects_reachLoss,
      step_reflects := noStep_reflects_reachLoss
    }
  case right =>
    exact SafeLossVisibility.constantPresentation_not_reachLossVisible

theorem reachSafeContract_not_lossAware :
    Not (
      LossAwareReachabilityPresentationContract
        universalReachLossConsequenceSystem
        noStepUnitDyn
        HiddenLossUnderBadPresentation.constantPresentation
        IrreversibleReachLoss.lossNext
        IrreversibleReachLoss.lossTarget
        noTarget
    ) := by
  intro hContract
  exact SafeLossVisibility.constantPresentation_not_reachLossVisible
    hContract.loss_visible

/--
The constant viability-loss presentation satisfies the safe/reflection
contract, but it does not make viability loss visible.
-/
theorem viabilitySafeContract_without_lossVisibility :
    ViabilitySafePresentationContract
      universalViabilityLossConsequenceSystem
      noStepUnitDyn
      HiddenViabilityLossUnderBadPresentation.constantPresentation
      IrreversibleViabilityLoss.viabilityLossNext
      IrreversibleViabilityLoss.viabilityLossSafe
      noSafe /\
    Not (
      ViabilityLossVisibleToPresentation
        (exactDynFromNext IrreversibleViabilityLoss.viabilityLossNext)
        IrreversibleViabilityLoss.viabilityLossSafe
        HiddenViabilityLossUnderBadPresentation.constantPresentation
    ) := by
  constructor
  case left =>
    exact {
      consequence_sound := viabilityConstantPresentation_sound,
      safe_reflects := noSafe_reflects_viabilityLoss,
      step_reflects := noStep_reflects_viabilityLoss
    }
  case right =>
    exact SafeLossVisibility.constantPresentation_not_viabilityLossVisible

theorem viabilitySafeContract_not_lossAware :
    Not (
      LossAwareViabilityPresentationContract
        universalViabilityLossConsequenceSystem
        noStepUnitDyn
        HiddenViabilityLossUnderBadPresentation.constantPresentation
        IrreversibleViabilityLoss.viabilityLossNext
        IrreversibleViabilityLoss.viabilityLossSafe
        noSafe
    ) := by
  intro hContract
  exact SafeLossVisibility.constantPresentation_not_viabilityLossVisible
    hContract.loss_visible

end LossAwarePresentationStrictness
end Trajectory
end OmegaProper
