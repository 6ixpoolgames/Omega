import OmegaProper.Trajectory.JointViability
import OmegaProper.Trajectory.RecurrentSupportRobustness

/-!
OmegaProper.Trajectory.JointRecurrentSupport

Joint recurrent-support guardrails.

This file records a small finite witness: two supports can each recurrently
carry a consequence distinction under their own declared safety predicate,
while no recurrent support carries any distinction under the shared joint
safety predicate.

This is not agency, identity, value, alignment, deformer theory, or Omega
proper. It is a local finite warning: individual recurrent carrying does not
automatically compose into joint recurrent carrying.
-/

namespace OmegaProper
namespace Trajectory
namespace JointRecurrentSupport

open ConsequenceRelation
open JointViability
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRobustness
open RecurrentViableClass
open SustainingViableClass

/-! ## Tiny finite disjoint-support witness -/

inductive JointCarryState where
  | aLeft
  | aRight
  | bLeft
  | bRight
  deriving DecidableEq

def jointCarryNext : JointCarryState -> JointCarryState -> Prop
  | JointCarryState.aLeft, JointCarryState.aRight => True
  | JointCarryState.aRight, JointCarryState.aLeft => True
  | JointCarryState.bLeft, JointCarryState.bRight => True
  | JointCarryState.bRight, JointCarryState.bLeft => True
  | _, _ => False

def jointCarryDyn : Dyn where
  State := JointCarryState
  Next := jointCarryNext

def carrySafeA : JointCarryState -> Prop
  | JointCarryState.aLeft => True
  | JointCarryState.aRight => True
  | JointCarryState.bLeft => False
  | JointCarryState.bRight => False

def carrySafeB : JointCarryState -> Prop
  | JointCarryState.aLeft => False
  | JointCarryState.aRight => False
  | JointCarryState.bLeft => True
  | JointCarryState.bRight => True

def supportA : JointCarryState -> Prop
  | JointCarryState.aLeft => True
  | JointCarryState.aRight => True
  | JointCarryState.bLeft => False
  | JointCarryState.bRight => False

def supportB : JointCarryState -> Prop
  | JointCarryState.aLeft => False
  | JointCarryState.aRight => False
  | JointCarryState.bLeft => True
  | JointCarryState.bRight => True

inductive JointCarryContext where
  | ctx
  deriving DecidableEq

def jointCarryConsequenceSystem : ConsequenceSystem where
  Fragment := JointCarryState
  Context := JointCarryContext
  Outcome := JointCarryState
  consequence := fun _ x => x
  Compare := fun _ x y => x = y
  Evaluated := fun _ => True

theorem aLeft_separated_aRight :
    ConsequenceSeparated
      jointCarryConsequenceSystem
      JointCarryState.aLeft
      JointCarryState.aRight := by
  exists JointCarryContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem bLeft_separated_bRight :
    ConsequenceSeparated
      jointCarryConsequenceSystem
      JointCarryState.bLeft
      JointCarryState.bRight := by
  exists JointCarryContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem supportA_recurrent :
    RecurrentViableClass
      jointCarryDyn
      carrySafeA
      supportA := by
  constructor
  case left =>
    intro x hx
    cases x <;> simp [supportA, carrySafeA] at *
  case right =>
    constructor
    case left =>
      intro x y hx hStep
      cases x <;> cases y <;>
        simp [supportA, jointCarryDyn, jointCarryNext] at *
    case right =>
      constructor
      case left =>
        intro x y hx hy
        cases x <;> cases y <;> simp [supportA] at *
        case aLeft.aLeft =>
          exact InternalPath.refl hx
        case aLeft.aRight =>
          exact internalPath_single_step hx hy trivial
        case aRight.aLeft =>
          exact internalPath_single_step hx hy trivial
        case aRight.aRight =>
          exact InternalPath.refl hx
      case right =>
        intro x hx
        cases x <;> simp [supportA, jointCarryDyn, jointCarryNext] at *
        case aLeft =>
          exact Exists.intro JointCarryState.aRight (And.intro trivial trivial)
        case aRight =>
          exact Exists.intro JointCarryState.aLeft (And.intro trivial trivial)

theorem supportB_recurrent :
    RecurrentViableClass
      jointCarryDyn
      carrySafeB
      supportB := by
  constructor
  case left =>
    intro x hx
    cases x <;> simp [supportB, carrySafeB] at *
  case right =>
    constructor
    case left =>
      intro x y hx hStep
      cases x <;> cases y <;>
        simp [supportB, jointCarryDyn, jointCarryNext] at *
    case right =>
      constructor
      case left =>
        intro x y hx hy
        cases x <;> cases y <;> simp [supportB] at *
        case bLeft.bLeft =>
          exact InternalPath.refl hx
        case bLeft.bRight =>
          exact internalPath_single_step hx hy trivial
        case bRight.bLeft =>
          exact internalPath_single_step hx hy trivial
        case bRight.bRight =>
          exact InternalPath.refl hx
      case right =>
        intro x hx
        cases x <;> simp [supportB, jointCarryDyn, jointCarryNext] at *
        case bLeft =>
          exact Exists.intro JointCarryState.bRight (And.intro trivial trivial)
        case bRight =>
          exact Exists.intro JointCarryState.bLeft (And.intro trivial trivial)

theorem supportA_pathCarries_merge :
    ClassPathCarriesMergeSeparatedPair
      jointCarryConsequenceSystem
      jointCarryNext
      supportA
      JointCarryState.aLeft
      JointCarryState.aRight := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        (internalPath_single_step trivial trivial trivial)
        (And.intro
          (internalPath_single_step trivial trivial trivial)
          (separated_implies_mergeSeparated aLeft_separated_aRight))))

theorem supportB_pathCarries_merge :
    ClassPathCarriesMergeSeparatedPair
      jointCarryConsequenceSystem
      jointCarryNext
      supportB
      JointCarryState.bLeft
      JointCarryState.bRight := by
  exact And.intro
    trivial
    (And.intro
      trivial
      (And.intro
        (internalPath_single_step trivial trivial trivial)
        (And.intro
          (internalPath_single_step trivial trivial trivial)
          (separated_implies_mergeSeparated bLeft_separated_bRight))))

theorem supportA_recurrently_carries :
    RecurrentSupportCarries
      jointCarryConsequenceSystem
      jointCarryNext
      carrySafeA
      supportA
      JointCarryState.aLeft
      JointCarryState.aRight := by
  exact And.intro supportA_recurrent supportA_pathCarries_merge

theorem supportB_recurrently_carries :
    RecurrentSupportCarries
      jointCarryConsequenceSystem
      jointCarryNext
      carrySafeB
      supportB
      JointCarryState.bLeft
      JointCarryState.bRight := by
  exact And.intro supportB_recurrent supportB_pathCarries_merge

theorem no_jointSafe_state
    (x : JointCarryState) :
    Not (JointSafe carrySafeA carrySafeB x) := by
  intro h
  cases x <;> simp [JointSafe, carrySafeA, carrySafeB] at h

theorem no_recurrentSupportCarries_under_jointSafety
    {C : JointCarryState -> Prop}
    {x y : JointCarryState} :
    Not (RecurrentSupportCarries
      jointCarryConsequenceSystem
      jointCarryNext
      (JointSafe carrySafeA carrySafeB)
      C
      x
      y) := by
  intro hCarry
  exact no_jointSafe_state x
    (hCarry.left.left x hCarry.right.left)

/--
Individual recurrent carrying under separate safety predicates does not imply
any recurrent carrying under their shared joint safety predicate.
-/
theorem individual_carrying_does_not_imply_joint_carrying :
    RecurrentSupportCarries
      jointCarryConsequenceSystem
      jointCarryNext
      carrySafeA
      supportA
      JointCarryState.aLeft
      JointCarryState.aRight /\
    RecurrentSupportCarries
      jointCarryConsequenceSystem
      jointCarryNext
      carrySafeB
      supportB
      JointCarryState.bLeft
      JointCarryState.bRight /\
    Not (exists C x y,
      RecurrentSupportCarries
        jointCarryConsequenceSystem
        jointCarryNext
        (JointSafe carrySafeA carrySafeB)
        C
        x
        y) := by
  exact And.intro
    supportA_recurrently_carries
    (And.intro
      supportB_recurrently_carries
      (by
        intro hJoint
        match hJoint with
        | Exists.intro _C hC =>
            match hC with
            | Exists.intro _x hx =>
                match hx with
                | Exists.intro _y hCarry =>
                    exact no_recurrentSupportCarries_under_jointSafety hCarry))

end JointRecurrentSupport
end Trajectory
end OmegaProper
