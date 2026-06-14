import OmegaProper.Trajectory.IrreversibleViabilityLoss
import OmegaProper.Trajectory.TargetPresentationInvariant

/-!
OmegaProper.Trajectory.HiddenViabilityLossUnderBadPresentation

Bad presentations can hide exact viability loss.

`IrreversibleViabilityLoss` defines exact loss of viability. This file shows
how a presentation can hide that loss: if it maps the before-loss and
after-loss states together, then the exact viability target is not constant on
the presentation's fibers.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace HiddenViabilityLossUnderBadPresentation

open IrreversibleViabilityLoss
open PresentationInvariant
open ReachabilityViability
open TargetPresentationInvariant

universe u q

/-- Exact viability as a target predicate. -/
def ViabilityTarget
    (D : Dyn.{u})
    (safe : D.State -> Prop) :
    D.State -> Prop :=
  fun x => Viable D safe x

/--
A presentation hides a viability loss when it identifies the source and target
of a viability-loss step.
-/
def PresentationHidesViabilityLoss
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    {Q : Type q}
    (present : D.State -> Q)
    (x y : D.State) : Prop :=
  ViabilityLossStep D safe x y /\
    PairErasedByPresentation present x y

theorem viabilityLoss_targetSeparated
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {x y : D.State}
    (hLoss : ViabilityLossStep D safe x y) :
    TargetSeparatedBy (ViabilityTarget D safe) x y := by
  intro hEq
  change Viable D safe x = Viable D safe y at hEq
  exact hLoss.right.right (Eq.mp hEq hLoss.right.left)

theorem hiddenViabilityLoss_obstructs_presentation
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden : PresentationHidesViabilityLoss D safe present x y) :
    TargetObstructedByPresentation
      (ViabilityTarget D safe)
      present := by
  exact Exists.intro x
    (Exists.intro y
      (And.intro
        hHidden.right
        (viabilityLoss_targetSeparated hHidden.left)))

theorem hiddenViabilityLoss_blocks_targetRespect
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden : PresentationHidesViabilityLoss D safe present x y) :
    Not (TargetRespectsPresentation (ViabilityTarget D safe) present) := by
  exact targetObstruction_blocks_respectPresentation
    (hiddenViabilityLoss_obstructs_presentation hHidden)

theorem targetRespect_blocks_hiddenViabilityLoss
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hRespect :
      TargetRespectsPresentation
        (ViabilityTarget D safe)
        present) :
    Not (PresentationHidesViabilityLoss D safe present x y) := by
  intro hHidden
  exact hiddenViabilityLoss_blocks_targetRespect hHidden hRespect

/-! ## Tiny finite witness -/

def constantPresentation (_x : ViabilityLossState) : Unit :=
  ()

theorem constantPresentation_hides_loop_dead_viability_loss :
    PresentationHidesViabilityLoss
      viabilityLossDyn
      viabilityLossSafe
      constantPresentation
      ViabilityLossState.loop
      ViabilityLossState.dead := by
  exact And.intro loop_to_dead_loses_viability rfl

theorem constantPresentation_obstructs_viabilityTarget :
    TargetObstructedByPresentation
      (ViabilityTarget viabilityLossDyn viabilityLossSafe)
      constantPresentation := by
  exact hiddenViabilityLoss_obstructs_presentation
    constantPresentation_hides_loop_dead_viability_loss

theorem constantPresentation_not_viabilityRespecting :
    Not (
      TargetRespectsPresentation
        (ViabilityTarget viabilityLossDyn viabilityLossSafe)
        constantPresentation
    ) := by
  exact hiddenViabilityLoss_blocks_targetRespect
    constantPresentation_hides_loop_dead_viability_loss

end HiddenViabilityLossUnderBadPresentation
end Trajectory
end OmegaProper
