import OmegaProper.Trajectory.ReachabilityViability

/-!
OmegaProper.Trajectory.JointViability

Joint viability for multiple safety predicates.

This file records a basic guardrail: being viable for each of two safety
predicates separately does not imply being viable for their conjunction.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace JointViability

open PredicateFixpoint
open ReachabilityViability

universe u

/-- Joint safety is conjunction of two declared safety predicates. -/
def JointSafe
    {X : Type u}
    (safeA safeB : X -> Prop) : X -> Prop :=
  fun x => safeA x /\ safeB x

/-- Joint viability is viability under joint safety. -/
def JointViable
    (D : Dyn.{u})
    (safeA safeB : D.State -> Prop) : D.State -> Prop :=
  Viable D (JointSafe safeA safeB)

/-- Viability is monotone in the safety predicate. -/
theorem viable_mono_safe
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    (hSub : forall x, safeA x -> safeB x) :
    PSub (Viable D safeA) (Viable D safeB) := by
  intro x hx
  match hx with
  | Exists.intro p hp =>
      have hPost : Postfixed (viabilityOp D safeB) p := by
        intro z hz
        have hA : viabilityOp D safeA p z :=
          hp.left z hz
        exact And.intro
          (hSub z hA.left)
          hA.right
      exact Exists.intro p (And.intro hPost hp.right)

theorem jointViable_left
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop} :
    PSub (JointViable D safeA safeB) (Viable D safeA) := by
  exact viable_mono_safe
    (fun x hx => hx.left)

theorem jointViable_right
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop} :
    PSub (JointViable D safeA safeB) (Viable D safeB) := by
  exact viable_mono_safe
    (fun x hx => hx.right)

/-! ## Tiny finite witness -/

inductive JointState where
  | start
  | aLoop
  | bLoop
  deriving DecidableEq

def jointNext : JointState -> JointState -> Prop
  | JointState.start, JointState.aLoop => True
  | JointState.start, JointState.bLoop => True
  | JointState.aLoop, JointState.aLoop => True
  | JointState.bLoop, JointState.bLoop => True
  | _, _ => False

def jointDyn : Dyn where
  State := JointState
  Next := jointNext

def safeA : JointState -> Prop
  | JointState.start => True
  | JointState.aLoop => True
  | JointState.bLoop => False

def safeB : JointState -> Prop
  | JointState.start => True
  | JointState.aLoop => False
  | JointState.bLoop => True

theorem aLoop_viable_A :
    Viable jointDyn safeA JointState.aLoop := by
  let p : JointState -> Prop :=
    fun x =>
      match x with
      | JointState.aLoop => True
      | _ => False
  have hPost : Postfixed (viabilityOp jointDyn safeA) p := by
    intro x hx
    cases x
    case start =>
      exact False.elim hx
    case aLoop =>
      exact And.intro trivial
        (Exists.intro JointState.aLoop (And.intro trivial trivial))
    case bLoop =>
      exact False.elim hx
  exact Exists.intro p (And.intro hPost trivial)

theorem bLoop_viable_B :
    Viable jointDyn safeB JointState.bLoop := by
  let p : JointState -> Prop :=
    fun x =>
      match x with
      | JointState.bLoop => True
      | _ => False
  have hPost : Postfixed (viabilityOp jointDyn safeB) p := by
    intro x hx
    cases x
    case start =>
      exact False.elim hx
    case aLoop =>
      exact False.elim hx
    case bLoop =>
      exact And.intro trivial
        (Exists.intro JointState.bLoop (And.intro trivial trivial))
  exact Exists.intro p (And.intro hPost trivial)

theorem start_viable_A :
    Viable jointDyn safeA JointState.start := by
  exact (viability_fixed jointDyn safeA).right JointState.start
    (And.intro
      trivial
      (Exists.intro JointState.aLoop
        (And.intro trivial aLoop_viable_A)))

theorem start_viable_B :
    Viable jointDyn safeB JointState.start := by
  exact (viability_fixed jointDyn safeB).right JointState.start
    (And.intro
      trivial
      (Exists.intro JointState.bLoop
        (And.intro trivial bLoop_viable_B)))

theorem aLoop_not_jointSafe :
    Not (JointSafe safeA safeB JointState.aLoop) := by
  intro h
  exact h.right

theorem bLoop_not_jointSafe :
    Not (JointSafe safeA safeB JointState.bLoop) := by
  intro h
  exact h.left

theorem start_not_jointViable :
    Not (JointViable jointDyn safeA safeB JointState.start) := by
  intro hJoint
  have hSucc :=
    viable_has_successor
      jointDyn
      (JointSafe safeA safeB)
      hJoint
  match hSucc with
  | Exists.intro y hy =>
      have hyJoint : JointViable jointDyn safeA safeB y := hy.right
      have hySafe :
          JointSafe safeA safeB y :=
        viable_sub_safe jointDyn (JointSafe safeA safeB) y hyJoint
      cases y
      case start =>
        exact hy.left
      case aLoop =>
        exact aLoop_not_jointSafe hySafe
      case bLoop =>
        exact bLoop_not_jointSafe hySafe

/--
Marginal viability for each safety predicate does not imply joint viability for
their conjunction.
-/
theorem marginal_viability_does_not_imply_joint_viability :
    Viable jointDyn safeA JointState.start /\
    Viable jointDyn safeB JointState.start /\
    Not (JointViable jointDyn safeA safeB JointState.start) := by
  exact And.intro
    start_viable_A
    (And.intro
      start_viable_B
      start_not_jointViable)

end JointViability
end Trajectory
end OmegaProper
