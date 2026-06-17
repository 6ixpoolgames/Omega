import OmegaProper.Trajectory.RecurrentSupportRestoration

/-!
OmegaProper.Trajectory.RecurrentSupportPerturbationBudget

The first exact perturbation-budget witness for recurrent support carrying.

This file does not define a general graph cut, probability of recovery,
identity, agency, deformer structure, value, alignment, or Omega proper. It
only records the smallest current threshold fact:

* same dynamics cannot be a destruction witness;
* removing the return edge in the two-state recurrent cycle can destroy
  recurrent carrying, even while endpoint viability and forward reachability
  remain.

Later adapters may turn this into a numeric or probabilistic robustness
measure. The core fact here is finite and exact.
-/

namespace OmegaProper
namespace Trajectory
namespace RecurrentSupportPerturbationBudget

open CarriedDistinction
open ConsequenceRelation
open DistinctionSupport
open IrreversibleRecurrentSupportLoss
open PathCarriedDistinction
open ReachabilityViability
open RecurrentSupportRestoration
open RecurrentSupportRobustness
open RecurrentViableClass
open SupportRestriction
open SupportUnderPerturbation
open SustainingViableClass

universe w k o

/-! ## Generic budget guardrail -/

/--
A directed edge is removed from `Next0` to `Next1` when the edge exists before
the change and not after the change.

This is only a local edge predicate. It does not count all changes between two
dynamics.
-/
def RemovesDirectedEdge
    {X : Type w}
    (Next0 Next1 : X -> X -> Prop)
    (x y : X) : Prop :=
  Next0 x y /\ Not (Next1 x y)

/--
Same dynamics cannot be a destruction witness for recurrent carrying.

This is the exact zero-perturbation floor: if nothing changes, recurrent
carrying is not destroyed by the change.
-/
theorem sameDynamics_not_recurrentSupportDestroyed
    {S : ConsequenceSystem.{w, k, o}}
    {Next : S.Fragment -> S.Fragment -> Prop}
    {safe C : S.Fragment -> Prop}
    {x y : S.Fragment} :
    Not (RecurrentSupportDestroyedUnder S Next Next safe safe C C x y) := by
  intro hDestroyed
  exact (recurrentSupportDestroyed_not_integrity hDestroyed)
    sameRecurrentSupport_preserves_integrity

/-! ## Two-state cycle budget witness -/

/-- The broken cycle removes the return edge from `right` back to `left`. -/
theorem brokenCycle_removes_return_edge :
    RemovesDirectedEdge
      cycleNext
      brokenCycleNext
      CycleState.right
      CycleState.left := by
  exact And.intro
    trivial
    (by
      intro hStep
      exact hStep)

/-- The broken cycle keeps the forward edge from `left` to `right`. -/
theorem brokenCycle_keeps_forward_edge :
    cycleNext CycleState.left CycleState.right /\
      brokenCycleNext CycleState.left CycleState.right := by
  exact And.intro trivial trivial

/--
Zero perturbation cannot destroy recurrent carrying in the two-state cycle.
-/
theorem cycle_zeroPerturbation_not_destroyed :
    Not (RecurrentSupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      cycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right) := by
  exact sameDynamics_not_recurrentSupportDestroyed

/--
One strategically placed return-edge removal can destroy recurrent carrying in
the two-state cycle.
-/
theorem cycle_oneReturnEdgeRemoval_destroys_carrying :
    RemovesDirectedEdge
      cycleNext
      brokenCycleNext
      CycleState.right
      CycleState.left /\
    RecurrentSupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      brokenCycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    brokenCycle_removes_return_edge
    broken_destroys_recurrent_support

/--
The finite perturbation-budget floor for the two-state recurrent support:

* zero dynamic change cannot destroy recurrent carrying;
* removing the return edge can destroy recurrent carrying;
* the forward path and endpoint viability facts still survive in the broken
  dynamics.

This is a threshold witness, not a general minimum-cut theorem.
-/
theorem two_state_recurrent_support_budget_floor :
    Not (RecurrentSupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      cycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right) /\
    RemovesDirectedEdge
      cycleNext
      brokenCycleNext
      CycleState.right
      CycleState.left /\
    cycleNext CycleState.left CycleState.right /\
    brokenCycleNext CycleState.left CycleState.right /\
    Viable brokenCycleDyn cycleSafe CycleState.left /\
    Viable brokenCycleDyn cycleSafe CycleState.right /\
    InternalPath
      (dynFromNext brokenCycleNext)
      cycleClass
      CycleState.left
      CycleState.right /\
    Not (InternalPath
      (dynFromNext brokenCycleNext)
      cycleClass
      CycleState.right
      CycleState.left) /\
    RecurrentSupportDestroyedUnder
      cycleConsequenceSystem
      cycleNext
      brokenCycleNext
      cycleSafe
      cycleSafe
      cycleClass
      cycleClass
      CycleState.left
      CycleState.right := by
  exact And.intro
    cycle_zeroPerturbation_not_destroyed
    (And.intro
      brokenCycle_removes_return_edge
      (And.intro
        brokenCycle_keeps_forward_edge.left
        (And.intro
          brokenCycle_keeps_forward_edge.right
          (And.intro
            broken_left_viable
            (And.intro
              broken_right_viable
              (And.intro
                broken_left_path_right
                (And.intro
                  broken_no_path_right_left
                  broken_destroys_recurrent_support)))))))

end RecurrentSupportPerturbationBudget
end Trajectory
end OmegaProper
