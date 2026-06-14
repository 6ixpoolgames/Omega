import OmegaProper.Trajectory.SafePresentationContract
import OmegaProper.Trajectory.ViabilityReflection

/-!
OmegaProper.Trajectory.PhantomViability

Bad presentations can fabricate apparent viability.

This file gives a tiny finite counterexample: the exact system has one safe
state with no sustaining transition, so it is not viable. The abstract system
adds a safe self-loop, so the presented abstract state is viable. The
presentation fails the step-reflection contract.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace PhantomViability

open PredicateFixpoint
open ConsequenceRelation
open ReachabilityReflection
open ReachabilityViability
open SafePresentationContract
open TrajectorySemantics
open ViabilityReflection

/-- One exact state with no outgoing step. -/
inductive ExactState where
  | x
  deriving DecidableEq

/-- One abstract state with a self-loop. -/
inductive AbstractState where
  | qx
  deriving DecidableEq

def exactNext : ExactState -> ExactState -> Prop
  | _, _ => False

def exactDyn : Dyn where
  State := ExactState
  Next := exactNext

def exactSafe : ExactState -> Prop
  | ExactState.x => True

def abstractNext : AbstractState -> AbstractState -> Prop
  | AbstractState.qx, AbstractState.qx => True

def abstractDyn : Dyn where
  State := AbstractState
  Next := abstractNext

def abstractSafe : AbstractState -> Prop
  | AbstractState.qx => True

def present : ExactState -> AbstractState
  | ExactState.x => AbstractState.qx

def identityConsequenceSystem : ConsequenceSystem where
  Fragment := ExactState
  Context := Unit
  Outcome := ExactState
  consequence := fun _ state => state
  Compare := fun _ left right => left = right
  Evaluated := fun _ => True

/-- No predicate can be postfixed for exact viability at `x`. -/
theorem exact_x_not_viable :
    Not (Viable exactDyn exactSafe ExactState.x) := by
  intro hViable
  have hStep := viable_has_successor exactDyn exactSafe hViable
  match hStep with
  | Exists.intro y hy =>
      cases y
      exact hy.left

/-- The abstract singleton predicate is postfixed because `qx` has a self-loop. -/
theorem abstract_qx_viable :
    Viable abstractDyn abstractSafe AbstractState.qx := by
  let p : AbstractState -> Prop := fun _ => True
  have hPost : Postfixed (viabilityOp abstractDyn abstractSafe) p := by
    intro q _hq
    cases q
    exact And.intro trivial
      (Exists.intro AbstractState.qx (And.intro trivial trivial))
  exact Exists.intro p (And.intro hPost trivial)

/-- The abstract self-loop has no exact step witness, so step reflection fails. -/
theorem not_stepReflects :
    Not (StepReflects exactDyn abstractDyn present) := by
  intro hReflect
  have hWitness :=
    hReflect ExactState.x AbstractState.qx trivial
  match hWitness with
  | Exists.intro y hy =>
      cases y
      exact hy.left

theorem not_viabilityReflectingPresentation :
    Not (
      ViabilityReflectingPresentation
        exactDyn
        abstractDyn
        present
        exactSafe
        abstractSafe
    ) := by
  intro hReflect
  exact not_stepReflects hReflect.step_reflects

/--
The exact state is not viable, while its abstract presentation is viable. The
presentation responsible for that apparent viability fails step reflection.
-/
theorem bad_presentation_fabricates_phantom_viability :
    Not (Viable exactDyn exactSafe ExactState.x) /\
    Viable abstractDyn abstractSafe (present ExactState.x) /\
    Not (
      ViabilityReflectingPresentation
        exactDyn
        abstractDyn
        present
        exactSafe
        abstractSafe
    ) := by
  exact And.intro
    exact_x_not_viable
    (And.intro
      abstract_qx_viable
      not_viabilityReflectingPresentation)

theorem exact_x_no_safePrefix_one :
    Not (SafePrefix exactDyn exactSafe 1 ExactState.x) := by
  intro hPrefix
  match hPrefix with
  | SafePrefix.step _hSafe hStep _hRest =>
      exact hStep

theorem exact_x_not_arbitrarilyLongSafePrefixes :
    Not (ArbitrarilyLongSafePrefixes exactDyn exactSafe ExactState.x) := by
  intro hPrefixes
  exact exact_x_no_safePrefix_one (hPrefixes 1)

theorem abstract_qx_arbitrarilyLongSafePrefixes :
    ArbitrarilyLongSafePrefixes abstractDyn abstractSafe AbstractState.qx := by
  exact viable_implies_arbitrarilyLongSafePrefixes abstract_qx_viable

/--
Operational version of the phantom viability witness: the bad presentation
fabricates arbitrarily long abstract safe prefixes, while the exact state has
no one-step safe prefix.
-/
theorem bad_presentation_fabricates_arbitrarily_long_safe_prefixes :
    Not (ArbitrarilyLongSafePrefixes exactDyn exactSafe ExactState.x) /\
    ArbitrarilyLongSafePrefixes abstractDyn abstractSafe (present ExactState.x) /\
    Not (
      ViabilityReflectingPresentation
        exactDyn
        abstractDyn
        present
        exactSafe
        abstractSafe
    ) := by
  exact And.intro
    exact_x_not_arbitrarilyLongSafePrefixes
    (And.intro
      abstract_qx_arbitrarilyLongSafePrefixes
      not_viabilityReflectingPresentation)

/--
The packaged safe-presentation contract excludes the phantom viability
presentation because the presentation fails step reflection.
-/
theorem bad_presentation_not_viabilitySafeContract :
    Not (
      ViabilitySafePresentationContract
        identityConsequenceSystem
        abstractDyn
        present
        exactNext
        exactSafe
        abstractSafe
    ) := by
  intro hContract
  exact not_stepReflects hContract.step_reflects

end PhantomViability
end Trajectory
end OmegaProper
