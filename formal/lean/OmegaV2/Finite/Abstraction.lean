import OmegaV2.Finite.ControlledMarkov
import Mathlib.Algebra.BigOperators.Ring.Finset

/-!
OmegaV2.Finite.Abstraction

Action-aware strong lumpability and exact finite state aggregation.
-/

namespace OmegaV2
namespace Finite

universe u v w

/-- A surjective state aggregation with an explicit representative per fiber. -/
structure StateAggregation
    (Concrete : Type u)
    (Abstract : Type v) where
  map : Concrete -> Abstract
  representative : Abstract -> Concrete
  representative_maps :
    forall abstractState, map (representative abstractState) = abstractState

/-- Transition mass from one concrete row into one aggregate target state. -/
def blockMass
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [DecidableEq Abstract]
    (K : ControlledKernel Concrete Action)
    (Q : StateAggregation Concrete Abstract)
    (state : Concrete)
    (action : Action)
    (target : Abstract) : ℚ :=
  ∑ concreteTarget ∈ Finset.univ.filter (fun x => Q.map x = target),
    K.prob state action concreteTarget

/-- Strong lumpability, checked separately for every action. -/
def ActionwiseLumpable
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [DecidableEq Abstract]
    (K : ControlledKernel Concrete Action)
    (Q : StateAggregation Concrete Abstract) : Prop :=
  forall left right,
    Q.map left = Q.map right ->
    forall action target,
      blockMass K Q left action target =
        blockMass K Q right action target

/-- A deterministic policy factors through an aggregate-state policy. -/
def PolicyFactors
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    (Q : StateAggregation Concrete Abstract)
    (concretePolicy : Concrete -> Action)
    (abstractPolicy : Abstract -> Action) : Prop :=
  forall state, concretePolicy state = abstractPolicy (Q.map state)

/-- Representative-selected aggregate transition probability. -/
def quotientProb
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [DecidableEq Abstract]
    (K : ControlledKernel Concrete Action)
    (Q : StateAggregation Concrete Abstract)
    (state : Abstract)
    (action : Action)
    (target : Abstract) : ℚ :=
  blockMass K Q (Q.representative state) action target

theorem blockMass_nonneg
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [DecidableEq Abstract]
    (K : ControlledKernel Concrete Action)
    (Q : StateAggregation Concrete Abstract)
    (state : Concrete)
    (action : Action)
    (target : Abstract) :
    0 <= blockMass K Q state action target := by
  unfold blockMass
  exact Finset.sum_nonneg fun concreteTarget _ =>
    K.nonneg state action concreteTarget

theorem blockMass_representative_independent
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [DecidableEq Abstract]
    {K : ControlledKernel Concrete Action}
    {Q : StateAggregation Concrete Abstract}
    (hLumpable : ActionwiseLumpable K Q)
    {state : Concrete}
    (action : Action)
    (target : Abstract) :
    blockMass K Q state action target =
      quotientProb K Q (Q.map state) action target := by
  unfold quotientProb
  apply hLumpable
  symm
  exact Q.representative_maps (Q.map state)

theorem blockMass_sum_one
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [Fintype Abstract]
    [DecidableEq Abstract]
    (K : ControlledKernel Concrete Action)
    (Q : StateAggregation Concrete Abstract)
    (state : Concrete)
    (action : Action) :
    (Finset.univ.sum fun target =>
      blockMass K Q state action target) = 1 := by
  classical
  unfold blockMass
  rw [Finset.sum_fiberwise]
  simpa using K.row_sum_one state action

/-- The representative-selected quotient is a normalized controlled kernel. -/
def quotientKernel
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [Fintype Abstract]
    [DecidableEq Abstract]
    (K : ControlledKernel Concrete Action)
    (Q : StateAggregation Concrete Abstract) :
    ControlledKernel Abstract Action where
  prob := quotientProb K Q
  nonneg := by
    intro state action target
    exact blockMass_nonneg K Q (Q.representative state) action target
  row_sum_one := by
    intro state action
    exact blockMass_sum_one K Q (Q.representative state) action

theorem weighted_sum_fiberwise
    {Concrete : Type u}
    {Abstract : Type v}
    [Fintype Concrete]
    [Fintype Abstract]
    [DecidableEq Abstract]
    (Q : StateAggregation Concrete Abstract)
    (weight : Concrete -> ℚ)
    (observable : Abstract -> ℚ) :
    (Finset.univ.sum fun state =>
      weight state * observable (Q.map state)) =
    Finset.univ.sum fun abstractState =>
      (Finset.univ.filter (fun state => Q.map state = abstractState)).sum weight *
        observable abstractState := by
  classical
  rw [← Finset.sum_fiberwise (s := Finset.univ) Q.map
    (fun state => weight state * observable (Q.map state))]
  apply Finset.sum_congr rfl
  intro abstractState _hAbstract
  rw [Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro state hState
  have hMap : Q.map state = abstractState := (Finset.mem_filter.mp hState).2
  rw [hMap]

theorem oneStep_transport
    {Concrete : Type u}
    {Abstract : Type v}
    {Action : Type w}
    [Fintype Concrete]
    [Fintype Abstract]
    [DecidableEq Abstract]
    {K : ControlledKernel Concrete Action}
    {Q : StateAggregation Concrete Abstract}
    {concretePolicy : Concrete -> Action}
    {abstractPolicy : Abstract -> Action}
    (hLumpable : ActionwiseLumpable K Q)
    (hPolicy : PolicyFactors Q concretePolicy abstractPolicy)
    (observable : Abstract -> ℚ)
    (state : Concrete) :
    oneStep K concretePolicy (fun target => observable (Q.map target)) state =
      oneStep (quotientKernel K Q) abstractPolicy observable (Q.map state) := by
  unfold oneStep
  rw [weighted_sum_fiberwise Q
    (fun target => K.prob state (concretePolicy state) target)
    observable]
  apply Finset.sum_congr rfl
  intro target _hTarget
  rw [hPolicy state]
  change
    blockMass K Q state (abstractPolicy (Q.map state)) target *
        observable target =
      quotientProb K Q (Q.map state) (abstractPolicy (Q.map state)) target *
        observable target
  rw [blockMass_representative_independent hLumpable]

end Finite
end OmegaV2
