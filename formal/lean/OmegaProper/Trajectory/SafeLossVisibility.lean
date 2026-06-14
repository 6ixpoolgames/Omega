import OmegaProper.Trajectory.HiddenLossUnderBadPresentation
import OmegaProper.Trajectory.HiddenViabilityLossUnderBadPresentation

/-!
OmegaProper.Trajectory.SafeLossVisibility

Packaged visibility conditions for exact reachability and viability loss.

The hidden-loss modules prove that a bad presentation can erase the difference
between a before-loss state and an after-loss state. This file names the
positive guardrail: a presentation makes loss visible when it does not collapse
any exact loss step.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace SafeLossVisibility

open IrreversibleReachLoss
open IrreversibleViabilityLoss
open PresentationInvariant
open ReachabilityViability
open TargetPresentationInvariant

universe u q

/--
A presentation makes reachability loss visible when it never identifies the
source and target of a reach-loss step.
-/
def ReachLossVisibleToPresentation
    (D : Dyn.{u})
    (target : D.State -> Prop)
    {Q : Type q}
    (present : D.State -> Q) : Prop :=
  forall x y,
    ReachLossStep D target x y ->
      Not (PairErasedByPresentation present x y)

/--
A presentation makes viability loss visible when it never identifies the source
and target of a viability-loss step.
-/
def ViabilityLossVisibleToPresentation
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    {Q : Type q}
    (present : D.State -> Q) : Prop :=
  forall x y,
    ViabilityLossStep D safe x y ->
      Not (PairErasedByPresentation present x y)

theorem hiddenReachLoss_blocks_visibility
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden :
      HiddenLossUnderBadPresentation.PresentationHidesReachLoss
        D
        target
        present
        x
        y) :
    Not (ReachLossVisibleToPresentation D target present) := by
  intro hVisible
  exact hVisible x y hHidden.left hHidden.right

theorem reachLossVisibility_blocks_hiddenLoss
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    (hVisible : ReachLossVisibleToPresentation D target present)
    {x y : D.State} :
    Not (
      HiddenLossUnderBadPresentation.PresentationHidesReachLoss
        D
        target
        present
        x
        y
    ) := by
  intro hHidden
  exact hiddenReachLoss_blocks_visibility hHidden hVisible

theorem reachTargetRespect_implies_lossVisible
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    (hRespect :
      TargetRespectsPresentation
        (HiddenLossUnderBadPresentation.ReachabilityTarget D target)
        present) :
    ReachLossVisibleToPresentation D target present := by
  intro x y hLoss hErased
  exact HiddenLossUnderBadPresentation.targetRespect_blocks_hiddenReachLoss
    hRespect
    (And.intro hLoss hErased)

theorem hiddenViabilityLoss_blocks_visibility
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden :
      HiddenViabilityLossUnderBadPresentation.PresentationHidesViabilityLoss
        D
        safe
        present
        x
        y) :
    Not (ViabilityLossVisibleToPresentation D safe present) := by
  intro hVisible
  exact hVisible x y hHidden.left hHidden.right

theorem viabilityLossVisibility_blocks_hiddenLoss
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    (hVisible : ViabilityLossVisibleToPresentation D safe present)
    {x y : D.State} :
    Not (
      HiddenViabilityLossUnderBadPresentation.PresentationHidesViabilityLoss
        D
        safe
        present
        x
        y
    ) := by
  intro hHidden
  exact hiddenViabilityLoss_blocks_visibility hHidden hVisible

theorem viabilityTargetRespect_implies_lossVisible
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    (hRespect :
      TargetRespectsPresentation
        (HiddenViabilityLossUnderBadPresentation.ViabilityTarget D safe)
        present) :
    ViabilityLossVisibleToPresentation D safe present := by
  intro x y hLoss hErased
  exact HiddenViabilityLossUnderBadPresentation.targetRespect_blocks_hiddenViabilityLoss
    hRespect
    (And.intro hLoss hErased)

/-! ## Tiny finite controls -/

theorem constantPresentation_not_reachLossVisible :
    Not (
      ReachLossVisibleToPresentation
        IrreversibleReachLoss.lossDyn
        IrreversibleReachLoss.lossTarget
        HiddenLossUnderBadPresentation.constantPresentation
    ) := by
  exact hiddenReachLoss_blocks_visibility
    HiddenLossUnderBadPresentation.constantPresentation_hides_start_dead_reach_loss

theorem constantPresentation_not_viabilityLossVisible :
    Not (
      ViabilityLossVisibleToPresentation
        IrreversibleViabilityLoss.viabilityLossDyn
        IrreversibleViabilityLoss.viabilityLossSafe
        HiddenViabilityLossUnderBadPresentation.constantPresentation
    ) := by
  exact hiddenViabilityLoss_blocks_visibility
    HiddenViabilityLossUnderBadPresentation.constantPresentation_hides_loop_dead_viability_loss

end SafeLossVisibility
end Trajectory
end OmegaProper
