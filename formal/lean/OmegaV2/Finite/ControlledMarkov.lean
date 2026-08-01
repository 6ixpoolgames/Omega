import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Rat.Lemmas
import Mathlib.Tactic.Linarith

/-!
OmegaV2.Finite.ControlledMarkov

Exact rational finite controlled Markov systems. This namespace is independent
of the historical Omega formal stack and is intended to migrate as a unit.
-/

namespace OmegaV2
namespace Finite

universe u v

/-- A finite action-indexed Markov kernel with exact rational rows. -/
structure ControlledKernel
    (State : Type u)
    (Action : Type v)
    [Fintype State] where
  prob : State -> Action -> State -> ℚ
  nonneg : forall state action target, 0 <= prob state action target
  row_sum_one :
    forall state action,
      (Finset.univ.sum fun target => prob state action target) = 1

/-- The one-step expectation under a deterministic policy. -/
def oneStep
    {State : Type u}
    {Action : Type v}
    [Fintype State]
    (K : ControlledKernel State Action)
    (policy : State -> Action)
    (observable : State -> ℚ)
    (state : State) : ℚ :=
  Finset.univ.sum fun target =>
    K.prob state (policy state) target * observable target

/-- Probability of hitting `target` at or before the declared horizon. -/
def HitWithin
    {State : Type u}
    {Action : Type v}
    [Fintype State]
    (K : ControlledKernel State Action)
    (policy : State -> Action)
    (target : State -> Prop)
    [DecidablePred target] :
    Nat -> State -> ℚ
  | 0, state => if target state then 1 else 0
  | horizon + 1, state =>
      if target state then 1
      else oneStep K policy (HitWithin K policy target horizon) state

theorem oneStep_nonneg
    {State : Type u}
    {Action : Type v}
    [Fintype State]
    (K : ControlledKernel State Action)
    (policy : State -> Action)
    (observable : State -> ℚ)
    (hObservable : forall state, 0 <= observable state)
    (state : State) :
    0 <= oneStep K policy observable state := by
  unfold oneStep
  exact Finset.sum_nonneg fun target _ =>
    mul_nonneg
      (K.nonneg state (policy state) target)
      (hObservable target)

theorem hitWithin_nonneg
    {State : Type u}
    {Action : Type v}
    [Fintype State]
    (K : ControlledKernel State Action)
    (policy : State -> Action)
    (target : State -> Prop)
    [DecidablePred target] :
    forall horizon state, 0 <= HitWithin K policy target horizon state := by
  intro horizon
  induction horizon with
  | zero =>
      intro state
      by_cases h : target state <;> simp [HitWithin, h]
  | succ horizon ih =>
      intro state
      by_cases h : target state
      · simp [HitWithin, h]
      · simp only [HitWithin, h, ↓reduceIte]
        exact oneStep_nonneg K policy _ ih state

end Finite
end OmegaV2
