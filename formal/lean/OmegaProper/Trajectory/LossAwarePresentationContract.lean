import OmegaProper.Trajectory.SafeLossVisibility
import OmegaProper.Trajectory.SafePresentationContract

/-!
OmegaProper.Trajectory.LossAwarePresentationContract

Packaged contracts for presentations that must not fabricate continuation and
must not hide exact continuation loss.

`SafePresentationContract` blocks fabricated reachability and viability via
soundness/reflection obligations. `SafeLossVisibility` blocks hidden loss by
requiring exact loss steps to remain separated. This file packages those two
obligations together.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace LossAwarePresentationContract

open ConsequenceRelation
open IrreversibleReachLoss
open IrreversibleViabilityLoss
open ReachabilityViability
open SafeLossVisibility
open SafePresentationContract
open TrajectorySemantics

universe w k o v

/--
Loss-aware reachability presentations cannot fabricate reachability and cannot
hide exact reachability-loss steps.
-/
structure LossAwareReachabilityPresentationContract
    (S : ConsequenceSystem.{w, k, o})
    (DQ : Dyn.{v})
    (present : S.Fragment -> DQ.State)
    (NextX : S.Fragment -> S.Fragment -> Prop)
    (targetX : S.Fragment -> Prop)
    (targetQ : DQ.State -> Prop) where
  reachability_safe :
    ReachabilitySafePresentationContract
      S
      DQ
      present
      NextX
      targetX
      targetQ
  loss_visible :
    ReachLossVisibleToPresentation
      (exactDynFromNext NextX)
      targetX
      present

/--
Loss-aware viability presentations cannot fabricate viability and cannot hide
exact viability-loss steps.
-/
structure LossAwareViabilityPresentationContract
    (S : ConsequenceSystem.{w, k, o})
    (DQ : Dyn.{v})
    (present : S.Fragment -> DQ.State)
    (NextX : S.Fragment -> S.Fragment -> Prop)
    (safeX : S.Fragment -> Prop)
    (safeQ : DQ.State -> Prop) where
  viability_safe :
    ViabilitySafePresentationContract
      S
      DQ
      present
      NextX
      safeX
      safeQ
  loss_visible :
    ViabilityLossVisibleToPresentation
      (exactDynFromNext NextX)
      safeX
      present

theorem lossAwareReachability_reflects_reach
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hContract :
      LossAwareReachabilityPresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    {x : S.Fragment}
    (hReachQ : Reach DQ targetQ (present x)) :
    Reach (exactDynFromNext NextX) targetX x := by
  exact reachabilityContract_reflects_reach
    hContract.reachability_safe
    hReachQ

theorem lossAwareReachability_reflects_finitePath
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hContract :
      LossAwareReachabilityPresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    {x : S.Fragment}
    (hPathQ : FinitePathToTarget DQ targetQ (present x)) :
    FinitePathToTarget (exactDynFromNext NextX) targetX x := by
  exact reachabilityContract_reflects_finitePath
    hContract.reachability_safe
    hPathQ

theorem lossAwareReachability_blocks_hiddenReachLoss
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hContract :
      LossAwareReachabilityPresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    {x y : S.Fragment} :
    Not (
      HiddenLossUnderBadPresentation.PresentationHidesReachLoss
        (exactDynFromNext NextX)
        targetX
        present
        x
        y
    ) := by
  exact reachLossVisibility_blocks_hiddenLoss hContract.loss_visible

theorem lossAwareReachability_blocks_lossStep_erasure
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hContract :
      LossAwareReachabilityPresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    {x y : S.Fragment}
    (hLoss : ReachLossStep (exactDynFromNext NextX) targetX x y) :
    Not (PresentationInvariant.PairErasedByPresentation present x y) := by
  exact hContract.loss_visible x y hLoss

theorem lossAwareViability_reflects_viability
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hContract :
      LossAwareViabilityPresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    {x : S.Fragment}
    (hViableQ : Viable DQ safeQ (present x)) :
    Viable (exactDynFromNext NextX) safeX x := by
  exact viabilityContract_reflects_viability
    hContract.viability_safe
    hViableQ

theorem lossAwareViability_reflects_safePrefixes
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hContract :
      LossAwareViabilityPresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    {x : S.Fragment}
    (hViableQ : Viable DQ safeQ (present x)) :
    ArbitrarilyLongSafePrefixes (exactDynFromNext NextX) safeX x := by
  exact viabilityContract_reflects_safePrefixes
    hContract.viability_safe
    hViableQ

theorem lossAwareViability_reflects_safePrefix
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hContract :
      LossAwareViabilityPresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    {n : Nat}
    {x : S.Fragment}
    (hPrefixQ : SafePrefix DQ safeQ n (present x)) :
    SafePrefix (exactDynFromNext NextX) safeX n x := by
  exact viabilityContract_reflects_safePrefix
    hContract.viability_safe
    hPrefixQ

theorem lossAwareViability_blocks_hiddenViabilityLoss
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hContract :
      LossAwareViabilityPresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    {x y : S.Fragment} :
    Not (
      HiddenViabilityLossUnderBadPresentation.PresentationHidesViabilityLoss
        (exactDynFromNext NextX)
        safeX
        present
        x
        y
    ) := by
  exact viabilityLossVisibility_blocks_hiddenLoss hContract.loss_visible

theorem lossAwareViability_blocks_lossStep_erasure
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hContract :
      LossAwareViabilityPresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    {x y : S.Fragment}
    (hLoss : ViabilityLossStep (exactDynFromNext NextX) safeX x y) :
    Not (PresentationInvariant.PairErasedByPresentation present x y) := by
  exact hContract.loss_visible x y hLoss

end LossAwarePresentationContract
end Trajectory
end OmegaProper
