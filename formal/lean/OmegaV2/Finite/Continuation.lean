import OmegaV2.Finite.Abstraction

/-!
OmegaV2.Finite.Continuation

Transport of finite-horizon target-hit probabilities through an exact
action-aware lumpable state aggregation.
-/

namespace OmegaV2
namespace Finite

universe u v w

theorem hitWithin_transport
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
    {concreteTarget : Concrete -> Prop}
    {abstractTarget : Abstract -> Prop}
    [DecidablePred concreteTarget]
    [DecidablePred abstractTarget]
    (hLumpable : ActionwiseLumpable K Q)
    (hPolicy : PolicyFactors Q concretePolicy abstractPolicy)
    (hTarget : forall state,
      concreteTarget state <-> abstractTarget (Q.map state)) :
    forall horizon state,
      HitWithin K concretePolicy concreteTarget horizon state =
        HitWithin
          (quotientKernel K Q)
          abstractPolicy
          abstractTarget
          horizon
          (Q.map state) := by
  intro horizon
  induction horizon with
  | zero =>
      intro state
      by_cases hConcrete : concreteTarget state
      · have hAbstract : abstractTarget (Q.map state) :=
          (hTarget state).mp hConcrete
        simp [HitWithin, hConcrete, hAbstract]
      · have hAbstract : ¬ abstractTarget (Q.map state) := by
          intro h
          exact hConcrete ((hTarget state).mpr h)
        simp [HitWithin, hConcrete, hAbstract]
  | succ horizon ih =>
      intro state
      by_cases hConcrete : concreteTarget state
      · have hAbstract : abstractTarget (Q.map state) :=
          (hTarget state).mp hConcrete
        simp [HitWithin, hConcrete, hAbstract]
      · have hAbstract : ¬ abstractTarget (Q.map state) := by
          intro h
          exact hConcrete ((hTarget state).mpr h)
        simp only [HitWithin, hConcrete, hAbstract, ↓reduceIte]
        calc
          oneStep K concretePolicy
              (HitWithin K concretePolicy concreteTarget horizon) state =
            oneStep K concretePolicy
              (fun target =>
                HitWithin
                  (quotientKernel K Q)
                  abstractPolicy
                  abstractTarget
                  horizon
                  (Q.map target))
              state := by
                unfold oneStep
                apply Finset.sum_congr rfl
                intro target _hTarget
                rw [ih target]
          _ =
            oneStep
              (quotientKernel K Q)
              abstractPolicy
              (HitWithin
                (quotientKernel K Q)
                abstractPolicy
                abstractTarget
                horizon)
              (Q.map state) :=
                oneStep_transport
                  hLumpable
                  hPolicy
                  (HitWithin
                    (quotientKernel K Q)
                    abstractPolicy
                    abstractTarget
                    horizon)
                  state

end Finite
end OmegaV2
