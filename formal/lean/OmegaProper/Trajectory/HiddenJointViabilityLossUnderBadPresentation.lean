import OmegaProper.Trajectory.JointViability
import OmegaProper.Trajectory.TargetPresentationInvariant

/-!
OmegaProper.Trajectory.HiddenJointViabilityLossUnderBadPresentation

Bad presentations can hide exact joint-viability loss.

`JointViability` shows that marginal viability does not imply joint viability.
This file adds the loss-side guardrail: a transition can leave the jointly
viable corridor while remaining viable for one marginal, and a presentation
that merges the before-loss and after-loss states hides that exact joint loss.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace HiddenJointViabilityLossUnderBadPresentation

open JointViability
open PredicateFixpoint
open PresentationInvariant
open ReachabilityViability
open TargetPresentationInvariant

universe u q

/-- Exact joint viability as a target predicate. -/
def JointViabilityTarget
    (D : Dyn.{u})
    (safeA safeB : D.State -> Prop) :
    D.State -> Prop :=
  fun x => JointViable D safeA safeB x

/--
A step loses joint viability when it moves from a jointly viable state to a
state that is not jointly viable.
-/
def JointViabilityLossStep
    (D : Dyn.{u})
    (safeA safeB : D.State -> Prop)
    (x y : D.State) : Prop :=
  D.Next x y /\
    JointViable D safeA safeB x /\
    Not (JointViable D safeA safeB y)

/--
A presentation hides joint-viability loss when it identifies the source and
target of a joint-viability-loss step.
-/
def PresentationHidesJointViabilityLoss
    (D : Dyn.{u})
    (safeA safeB : D.State -> Prop)
    {Q : Type q}
    (present : D.State -> Q)
    (x y : D.State) : Prop :=
  JointViabilityLossStep D safeA safeB x y /\
    PairErasedByPresentation present x y

theorem jointViabilityLoss_targetSeparated
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {x y : D.State}
    (hLoss : JointViabilityLossStep D safeA safeB x y) :
    TargetSeparatedBy (JointViabilityTarget D safeA safeB) x y := by
  intro hEq
  change JointViable D safeA safeB x =
    JointViable D safeA safeB y at hEq
  exact hLoss.right.right (Eq.mp hEq hLoss.right.left)

theorem hiddenJointViabilityLoss_obstructs_presentation
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden :
      PresentationHidesJointViabilityLoss D safeA safeB present x y) :
    TargetObstructedByPresentation
      (JointViabilityTarget D safeA safeB)
      present := by
  exact Exists.intro x
    (Exists.intro y
      (And.intro
        hHidden.right
        (jointViabilityLoss_targetSeparated hHidden.left)))

theorem hiddenJointViabilityLoss_blocks_targetRespect
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hHidden :
      PresentationHidesJointViabilityLoss D safeA safeB present x y) :
    Not (
      TargetRespectsPresentation
        (JointViabilityTarget D safeA safeB)
        present
    ) := by
  exact targetObstruction_blocks_respectPresentation
    (hiddenJointViabilityLoss_obstructs_presentation hHidden)

theorem targetRespect_blocks_hiddenJointViabilityLoss
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {Q : Type q}
    {present : D.State -> Q}
    {x y : D.State}
    (hRespect :
      TargetRespectsPresentation
        (JointViabilityTarget D safeA safeB)
        present) :
    Not (PresentationHidesJointViabilityLoss D safeA safeB present x y) := by
  intro hHidden
  exact hiddenJointViabilityLoss_blocks_targetRespect hHidden hRespect

/-! ## Tiny finite witness -/

inductive JointLossState where
  | joint
  | onlyA
  deriving DecidableEq

def jointLossNext : JointLossState -> JointLossState -> Prop
  | JointLossState.joint, JointLossState.joint => True
  | JointLossState.joint, JointLossState.onlyA => True
  | JointLossState.onlyA, JointLossState.onlyA => True
  | _, _ => False

def jointLossDyn : Dyn where
  State := JointLossState
  Next := jointLossNext

def jointLossSafeA : JointLossState -> Prop
  | JointLossState.joint => True
  | JointLossState.onlyA => True

def jointLossSafeB : JointLossState -> Prop
  | JointLossState.joint => True
  | JointLossState.onlyA => False

theorem joint_state_jointViable :
    JointViable
      jointLossDyn
      jointLossSafeA
      jointLossSafeB
      JointLossState.joint := by
  let p : JointLossState -> Prop :=
    fun x =>
      match x with
      | JointLossState.joint => True
      | JointLossState.onlyA => False
  have hPost :
      Postfixed
        (viabilityOp
          jointLossDyn
          (JointSafe jointLossSafeA jointLossSafeB))
        p := by
    intro x hx
    cases x
    case joint =>
      exact And.intro
        (And.intro trivial trivial)
        (Exists.intro JointLossState.joint
          (And.intro trivial trivial))
    case onlyA =>
      exact False.elim hx
  exact Exists.intro p (And.intro hPost trivial)

theorem onlyA_viable_A :
    Viable jointLossDyn jointLossSafeA JointLossState.onlyA := by
  let p : JointLossState -> Prop :=
    fun x =>
      match x with
      | JointLossState.onlyA => True
      | _ => False
  have hPost :
      Postfixed (viabilityOp jointLossDyn jointLossSafeA) p := by
    intro x hx
    cases x
    case joint =>
      exact False.elim hx
    case onlyA =>
      exact And.intro trivial
        (Exists.intro JointLossState.onlyA
          (And.intro trivial trivial))
  exact Exists.intro p (And.intro hPost trivial)

theorem onlyA_not_jointViable :
    Not (
      JointViable
        jointLossDyn
        jointLossSafeA
        jointLossSafeB
        JointLossState.onlyA
    ) := by
  intro hJoint
  have hSafe :
      JointSafe jointLossSafeA jointLossSafeB JointLossState.onlyA :=
    viable_sub_safe
      jointLossDyn
      (JointSafe jointLossSafeA jointLossSafeB)
      JointLossState.onlyA
      hJoint
  exact hSafe.right

theorem joint_to_onlyA_loses_jointViability :
    JointViabilityLossStep
      jointLossDyn
      jointLossSafeA
      jointLossSafeB
      JointLossState.joint
      JointLossState.onlyA := by
  exact And.intro trivial
    (And.intro joint_state_jointViable onlyA_not_jointViable)

def constantPresentation (_x : JointLossState) : Unit :=
  ()

theorem constantPresentation_hides_joint_to_onlyA_loss :
    PresentationHidesJointViabilityLoss
      jointLossDyn
      jointLossSafeA
      jointLossSafeB
      constantPresentation
      JointLossState.joint
      JointLossState.onlyA := by
  exact And.intro joint_to_onlyA_loses_jointViability rfl

theorem constantPresentation_obstructs_jointViabilityTarget :
    TargetObstructedByPresentation
      (JointViabilityTarget
        jointLossDyn
        jointLossSafeA
        jointLossSafeB)
      constantPresentation := by
  exact hiddenJointViabilityLoss_obstructs_presentation
    constantPresentation_hides_joint_to_onlyA_loss

theorem constantPresentation_not_jointViabilityRespecting :
    Not (
      TargetRespectsPresentation
        (JointViabilityTarget
          jointLossDyn
          jointLossSafeA
          jointLossSafeB)
        constantPresentation
    ) := by
  exact hiddenJointViabilityLoss_blocks_targetRespect
    constantPresentation_hides_joint_to_onlyA_loss

/--
The after-loss state can remain viable for one marginal constraint even though
joint viability has been lost.
-/
theorem joint_loss_can_leave_marginal_viability :
    Viable jointLossDyn jointLossSafeA JointLossState.onlyA /\
    Not (
      JointViable
        jointLossDyn
        jointLossSafeA
        jointLossSafeB
        JointLossState.onlyA
    ) := by
  exact And.intro onlyA_viable_A onlyA_not_jointViable

end HiddenJointViabilityLossUnderBadPresentation
end Trajectory
end OmegaProper
