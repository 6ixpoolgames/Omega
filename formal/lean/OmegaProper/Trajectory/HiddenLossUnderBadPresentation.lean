import OmegaProper.Trajectory.IrreversibleReachLoss
import OmegaProper.Trajectory.TargetPresentationInvariant

/-!
OmegaProper.Trajectory.HiddenLossUnderBadPresentation

Bad presentations can hide exact reachability loss.

`IrreversibleReachLoss` defines exact loss of access to a target. This file
shows how a presentation can hide that loss: if it maps the before-loss and
after-loss states together, then the exact reachability target is not constant
on the presentation's fibers.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace HiddenLossUnderBadPresentation

open IrreversibleReachLoss
open PresentationInvariant
open ReachabilityViability
open TargetPresentationInvariant

universe u q

/-- Exact reachability as a target predicate. -/
def ReachabilityTarget
    (D : Dyn.{u})
    (target : D.State -> Prop) :
    D.State -> Prop :=
  fun x => Reach D target x

/--
A presentation hides a reach loss when it identifies the source and target of a
reach-loss step.
-/
def PresentationHidesReachLoss
    (D : Dyn.{u})
    (target : D.State -> Prop)
    {Q : Type q}
    (present : D.State -> Q)
    (x y : D.State) : Prop :=
  ReachLossStep D target x y /\
    PairErasedByPresentation present x y

theorem reachLoss_targetSeparated
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {x y : D.State}
    (hLoss : ReachLossStep D target x y) :
    TargetSeparatedBy (ReachabilityTarget D target) x y := by
  intro hEq
  change Reach D target x = Reach D target y at hEq
  exact hLoss.right.right (Eq.mp hEq hLoss.right.left)

theorem hiddenReachLoss_obstructs_presentation
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden : PresentationHidesReachLoss D target present x y) :
    TargetObstructedByPresentation
      (ReachabilityTarget D target)
      present := by
  exact Exists.intro x
    (Exists.intro y
      (And.intro
        hHidden.right
        (reachLoss_targetSeparated hHidden.left)))

theorem hiddenReachLoss_blocks_targetRespect
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden : PresentationHidesReachLoss D target present x y) :
    Not (TargetRespectsPresentation (ReachabilityTarget D target) present) := by
  exact targetObstruction_blocks_respectPresentation
    (hiddenReachLoss_obstructs_presentation hHidden)

theorem targetRespect_blocks_hiddenReachLoss
    {D : Dyn.{u}}
    {target : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hRespect :
      TargetRespectsPresentation
        (ReachabilityTarget D target)
        present) :
    Not (PresentationHidesReachLoss D target present x y) := by
  intro hHidden
  exact hiddenReachLoss_blocks_targetRespect hHidden hRespect

/-! ## Tiny finite witness -/

def constantPresentation (_x : LossState) : Unit :=
  ()

theorem constantPresentation_hides_start_dead_reach_loss :
    PresentationHidesReachLoss
      lossDyn
      lossTarget
      constantPresentation
      LossState.start
      LossState.dead := by
  exact And.intro start_to_dead_loses_reach rfl

theorem constantPresentation_obstructs_reachabilityTarget :
    TargetObstructedByPresentation
      (ReachabilityTarget lossDyn lossTarget)
      constantPresentation := by
  exact hiddenReachLoss_obstructs_presentation
    constantPresentation_hides_start_dead_reach_loss

theorem constantPresentation_not_reachabilityRespecting :
    Not (
      TargetRespectsPresentation
        (ReachabilityTarget lossDyn lossTarget)
        constantPresentation
    ) := by
  exact hiddenReachLoss_blocks_targetRespect
    constantPresentation_hides_start_dead_reach_loss

end HiddenLossUnderBadPresentation
end Trajectory
end OmegaProper
