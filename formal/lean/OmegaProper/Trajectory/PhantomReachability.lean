import OmegaProper.Trajectory.PresentationInvariant
import OmegaProper.Trajectory.ReachabilityViability
import OmegaProper.Trajectory.SafePresentationContract
import OmegaProper.Trajectory.TrajectorySemantics

/-!
OmegaProper.Trajectory.PhantomReachability

Unsound presentations can fabricate apparent reachability.

This file gives a tiny finite counterexample: the exact transition system has
two disjoint edges, but a presentation that merges the middle states creates an
abstract path that did not exist exactly. The merged presentation is also
formally unsound against a consequence system that separates those middle
states.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace PhantomReachability

open ConsequenceRelation
open PredicateFixpoint
open PresentationInvariant
open ReachabilityViability
open SafePresentationContract
open TrajectorySemantics

/-- Exact four-state system: `a -> b` and `c -> d`, with no bridge. -/
inductive ExactState where
  | a
  | b
  | c
  | d
  deriving DecidableEq

/-- Abstract system after merging exact states `b` and `c`. -/
inductive AbstractState where
  | qa
  | qm
  | qd
  deriving DecidableEq

def exactNext : ExactState -> ExactState -> Prop
  | ExactState.a, ExactState.b => True
  | ExactState.c, ExactState.d => True
  | _, _ => False

def exactDyn : Dyn where
  State := ExactState
  Next := exactNext

def exactTarget : ExactState -> Prop
  | ExactState.d => True
  | _ => False

/--
The prefixed barrier containing only `c` and `d`. It excludes `a`, so it will
witness that `a` is not in the least fixed-point reachability set for target
`d`.
-/
def exactReachBarrier : ExactState -> Prop
  | ExactState.c => True
  | ExactState.d => True
  | _ => False

theorem exactReachBarrier_prefixed :
    Prefixed (reachOp exactDyn exactTarget) exactReachBarrier := by
  intro x hx
  cases x
  case a =>
    change False
    simp [reachOp, exactDyn, exactNext, exactTarget, exactReachBarrier] at hx
    match hx with
    | Exists.intro y hy =>
        cases y <;>
          simp at hy
  case b =>
    simp [reachOp, exactDyn, exactNext, exactTarget, exactReachBarrier] at hx
  case c =>
    trivial
  case d =>
    trivial

theorem exact_a_not_reaches_d :
    Not (Reach exactDyn exactTarget ExactState.a) := by
  intro hReach
  exact hReach exactReachBarrier exactReachBarrier_prefixed

/-- Presentation that merges `b` and `c`. -/
def mergePresentation : ExactState -> AbstractState
  | ExactState.a => AbstractState.qa
  | ExactState.b => AbstractState.qm
  | ExactState.c => AbstractState.qm
  | ExactState.d => AbstractState.qd

/--
Abstract dynamics induced by the unsound merge: `qa -> qm` comes from `a -> b`,
and `qm -> qd` comes from `c -> d`.
-/
def abstractNext : AbstractState -> AbstractState -> Prop
  | AbstractState.qa, AbstractState.qm => True
  | AbstractState.qm, AbstractState.qd => True
  | _, _ => False

def abstractDyn : Dyn where
  State := AbstractState
  Next := abstractNext

def abstractTarget : AbstractState -> Prop
  | AbstractState.qd => True
  | _ => False

theorem abstract_qd_reaches_qd :
    Reach abstractDyn abstractTarget AbstractState.qd := by
  exact target_sub_reach abstractDyn abstractTarget AbstractState.qd trivial

theorem abstract_qm_reaches_qd :
    Reach abstractDyn abstractTarget AbstractState.qm := by
  exact reach_step abstractDyn abstractTarget
    (by trivial)
    abstract_qd_reaches_qd

theorem abstract_qa_reaches_qd :
    Reach abstractDyn abstractTarget AbstractState.qa := by
  exact reach_step abstractDyn abstractTarget
    (by trivial)
    abstract_qm_reaches_qd

/-- A one-context consequence system that separates exact states by identity. -/
inductive IdentityContext where
  | ctx
  deriving DecidableEq

def identityConsequenceSystem : ConsequenceSystem where
  Fragment := ExactState
  Context := IdentityContext
  Outcome := ExactState
  consequence := fun _ x => x
  Compare := fun _ x y => x = y
  Evaluated := fun _ => True

theorem exact_b_separated_c :
    ConsequenceSeparated identityConsequenceSystem ExactState.b ExactState.c := by
  exists IdentityContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem exact_b_mergeSeparated_c :
    ConsequenceMergeSeparated identityConsequenceSystem ExactState.b ExactState.c := by
  exact separated_implies_mergeSeparated exact_b_separated_c

theorem mergePresentation_erases_b_c :
    PairErasedByPresentation mergePresentation ExactState.b ExactState.c := by
  rfl

theorem mergePresentation_not_sound :
    Not (SoundQuotient.SoundQuotient identityConsequenceSystem mergePresentation) := by
  exact SoundQuotient.mergeSeparated_kernel_blocks_soundQuotient
    mergePresentation_erases_b_c
    exact_b_mergeSeparated_c

/--
The exact system cannot reach `d` from `a`, while the merged abstract system can
reach `qd` from `qa`; the presentation responsible for that apparent path is
not consequence-sound.
-/
theorem unsound_merge_fabricates_phantom_reachability :
    Not (Reach exactDyn exactTarget ExactState.a) /\
    Reach abstractDyn abstractTarget AbstractState.qa /\
    Not (SoundQuotient.SoundQuotient identityConsequenceSystem mergePresentation) := by
  exact And.intro
    exact_a_not_reaches_d
    (And.intro
      abstract_qa_reaches_qd
      mergePresentation_not_sound)

theorem exact_a_no_finitePathToTarget_d :
    Not (FinitePathToTarget exactDyn exactTarget ExactState.a) := by
  intro hPath
  exact exact_a_not_reaches_d (finitePathToTarget_implies_reach hPath)

theorem abstract_qa_finitePathToTarget_qd :
    FinitePathToTarget abstractDyn abstractTarget AbstractState.qa := by
  exact reach_implies_finitePathToTarget abstract_qa_reaches_qd

/--
Operational version of the phantom reachability witness: the unsound merge
fabricates an abstract finite path to target while no exact finite path exists
from the corresponding exact state.
-/
theorem unsound_merge_fabricates_phantom_finite_path :
    Not (FinitePathToTarget exactDyn exactTarget ExactState.a) /\
    FinitePathToTarget abstractDyn abstractTarget AbstractState.qa /\
    Not (SoundQuotient.SoundQuotient identityConsequenceSystem mergePresentation) := by
  exact And.intro
    exact_a_no_finitePathToTarget_d
    (And.intro
      abstract_qa_finitePathToTarget_qd
      mergePresentation_not_sound)

/--
The packaged safe-presentation contract excludes the phantom reachability
presentation because the presentation is not consequence-sound.
-/
theorem mergePresentation_not_reachabilitySafeContract :
    Not (
      ReachabilitySafePresentationContract
        identityConsequenceSystem
        abstractDyn
        mergePresentation
        exactNext
        exactTarget
        abstractTarget
    ) := by
  intro hContract
  exact mergePresentation_not_sound hContract.consequence_sound

end PhantomReachability
end Trajectory
end OmegaProper
