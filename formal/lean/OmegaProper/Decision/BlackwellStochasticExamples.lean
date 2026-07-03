import Mathlib.Tactic.NormNum
import OmegaProper.Decision.BlackwellStochastic

/-!
OmegaProper.Decision.BlackwellStochasticExamples

Tiny finite rational example for the stochastic Blackwell forward bridge.
-/

namespace OmegaProper
namespace Decision
namespace BlackwellStochasticExamples

open BlackwellStochastic

inductive OneState where
  | s
deriving DecidableEq

inductive TwoObs where
  | left
  | right
deriving DecidableEq

inductive TwoAct where
  | a0
  | a1
deriving DecidableEq

instance : Fintype OneState where
  elems := {OneState.s}
  complete := by
    intro x
    cases x
    simp

instance : Fintype TwoObs where
  elems := {TwoObs.left, TwoObs.right}
  complete := by
    intro x
    cases x <;> simp

instance : Fintype TwoAct where
  elems := {TwoAct.a0, TwoAct.a1}
  complete := by
    intro x
    cases x <;> simp

def pointExperiment : RatExperiment OneState TwoObs where
  prob _ obs :=
    match obs with
    | TwoObs.left => 1
    | TwoObs.right => 0
  nonneg := by
    intro _st obs
    cases obs <;> norm_num
  row_sum_one := by
    intro st
    cases st
    simp [Finset.univ, Fintype.elems]

def halfExperiment : RatExperiment OneState TwoObs where
  prob _ _ := (1 / 2 : ℚ)
  nonneg := by
    intro _st _obs
    norm_num
  row_sum_one := by
    intro st
    cases st
    simp [Finset.univ, Fintype.elems]

def point_to_half_garbling :
    StochasticGarbling pointExperiment halfExperiment where
  garble e f :=
    match e, f with
    | TwoObs.left, _ => (1 / 2 : ℚ)
    | TwoObs.right, TwoObs.left => 1
    | TwoObs.right, TwoObs.right => 0
  nonneg := by
    intro e f
    cases e <;> cases f <;> norm_num
  row_sum_one := by
    intro e
    cases e <;>
      simp [Finset.univ, Fintype.elems]
  commutes := by
    intro st f
    cases st
    cases f <;>
      simp [halfExperiment, pointExperiment, Finset.univ, Fintype.elems]

def fairPolicy : RandomizedPolicy TwoObs TwoAct where
  prob _ _ := (1 / 2 : ℚ)
  nonneg := by
    intro obs act
    norm_num
  row_sum_one := by
    intro obs
    cases obs <;>
      simp [Finset.univ, Fintype.elems]

theorem fairPolicy_compilation_preserves_mass
    (act : TwoAct) :
    InducedActionMass pointExperiment
        (compileRandomizedPolicy point_to_half_garbling fairPolicy).prob
        OneState.s act =
      InducedActionMass halfExperiment fairPolicy.prob OneState.s act :=
  inducedActionMass_compileRandomizedPolicy_eq
    point_to_half_garbling fairPolicy OneState.s act

end BlackwellStochasticExamples
end Decision
end OmegaProper
