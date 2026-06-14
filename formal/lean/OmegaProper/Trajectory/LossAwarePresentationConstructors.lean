import OmegaProper.Trajectory.LossAwarePresentationContract

/-!
OmegaProper.Trajectory.LossAwarePresentationConstructors

Constructor theorems for loss-aware presentation contracts.

`LossAwarePresentationContract` packages two obligations:

* a safe/reflection contract, which blocks fabricated continuation claims;
* loss visibility, which blocks hidden exact loss.

This file records useful sufficient conditions for constructing loss-aware
contracts. The nontrivial constructor says that if the exact reachability or
viability target is constant on presentation fibers, then exact loss steps
cannot be hidden by that presentation.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace LossAwarePresentationConstructors

open ConsequenceRelation
open HiddenLossUnderBadPresentation
open HiddenViabilityLossUnderBadPresentation
open LossAwarePresentationContract
open ReachabilityViability
open SafeLossVisibility
open SafePresentationContract
open TargetPresentationInvariant

universe w k o v

/-- Direct constructor for reachability loss-aware contracts. -/
theorem mk_lossAwareReachability
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hSafe :
      ReachabilitySafePresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    (hVisible :
      ReachLossVisibleToPresentation
        (exactDynFromNext NextX)
        targetX
        present) :
    LossAwareReachabilityPresentationContract
      S
      DQ
      present
      NextX
      targetX
      targetQ where
  reachability_safe := hSafe
  loss_visible := hVisible

/-- Direct constructor for viability loss-aware contracts. -/
theorem mk_lossAwareViability
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hSafe :
      ViabilitySafePresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    (hVisible :
      ViabilityLossVisibleToPresentation
        (exactDynFromNext NextX)
        safeX
        present) :
    LossAwareViabilityPresentationContract
      S
      DQ
      present
      NextX
      safeX
      safeQ where
  viability_safe := hSafe
  loss_visible := hVisible

/--
If exact reachability is constant on presentation fibers, then a
reachability-safe presentation is loss-aware.
-/
theorem mk_lossAwareReachability_of_targetRespect
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hSafe :
      ReachabilitySafePresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    (hRespect :
      TargetRespectsPresentation
        (ReachabilityTarget (exactDynFromNext NextX) targetX)
        present) :
    LossAwareReachabilityPresentationContract
      S
      DQ
      present
      NextX
      targetX
      targetQ := by
  exact mk_lossAwareReachability
    hSafe
    (reachTargetRespect_implies_lossVisible hRespect)

/--
If exact viability is constant on presentation fibers, then a viability-safe
presentation is loss-aware.
-/
theorem mk_lossAwareViability_of_targetRespect
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hSafe :
      ViabilitySafePresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    (hRespect :
      TargetRespectsPresentation
        (ViabilityTarget (exactDynFromNext NextX) safeX)
        present) :
    LossAwareViabilityPresentationContract
      S
      DQ
      present
      NextX
      safeX
      safeQ := by
  exact mk_lossAwareViability
    hSafe
    (viabilityTargetRespect_implies_lossVisible hRespect)

/--
The target-respect constructor inherits reachability reflection from its safe
contract.
-/
theorem targetRespectReachabilityConstructor_reflects_reach
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hSafe :
      ReachabilitySafePresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    (hRespect :
      TargetRespectsPresentation
        (ReachabilityTarget (exactDynFromNext NextX) targetX)
        present)
    {x : S.Fragment}
    (hReachQ : Reach DQ targetQ (present x)) :
    Reach (exactDynFromNext NextX) targetX x := by
  exact lossAwareReachability_reflects_reach
    (mk_lossAwareReachability_of_targetRespect hSafe hRespect)
    hReachQ

/--
The target-respect constructor inherits viability reflection from its safe
contract.
-/
theorem targetRespectViabilityConstructor_reflects_viability
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hSafe :
      ViabilitySafePresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    (hRespect :
      TargetRespectsPresentation
        (ViabilityTarget (exactDynFromNext NextX) safeX)
        present)
    {x : S.Fragment}
    (hViableQ : Viable DQ safeQ (present x)) :
    Viable (exactDynFromNext NextX) safeX x := by
  exact lossAwareViability_reflects_viability
    (mk_lossAwareViability_of_targetRespect hSafe hRespect)
    hViableQ

end LossAwarePresentationConstructors
end Trajectory
end OmegaProper
