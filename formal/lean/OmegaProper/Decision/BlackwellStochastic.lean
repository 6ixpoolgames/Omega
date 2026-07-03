import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Rat.Lemmas
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-!
OmegaProper.Decision.BlackwellStochastic

Finite rational stochastic Blackwell-shaped forward bridge for ODT1.

This file proves the conservative direction only: if stochastic experiment `F`
is obtained from stochastic experiment `E` by a finite rational garbling, then
every randomized policy over `F` observations compiles into a randomized policy
over `E` observations that preserves the induced state/action mass.

It does not prove the full stochastic Blackwell theorem, Le Cam deficiency,
separation/Farkas results, Bayes risk, expected utility, value, agency,
identity, quantum structure, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace BlackwellStochastic

universe u v w a

/-- A finite exact-rational stochastic experiment. -/
structure RatExperiment (State : Type u) (Obs : Type v) [Fintype Obs] where
  prob : State -> Obs -> ℚ
  nonneg : forall s obs, 0 <= prob s obs
  row_sum_one : forall s, (Finset.univ.sum fun obs => prob s obs) = 1

/-- A finite exact-rational randomized policy. -/
structure RandomizedPolicy (Obs : Type v) (Act : Type a)
    [Fintype Act] where
  prob : Obs -> Act -> ℚ
  nonneg : forall obs act, 0 <= prob obs act
  row_sum_one : forall obs, (Finset.univ.sum fun act => prob obs act) = 1

/--
`F` is obtained from `E` by a finite rational garbling.

Reading: observe through `E`, then sample a coarser `F` observation using
`garble`.
-/
structure StochasticGarbling
    {State : Type u} {ObsE : Type v} {ObsF : Type w}
    [Fintype ObsE] [Fintype ObsF]
    (E : RatExperiment State ObsE)
    (F : RatExperiment State ObsF) where
  garble : ObsE -> ObsF -> ℚ
  nonneg : forall e f, 0 <= garble e f
  row_sum_one : forall e, (Finset.univ.sum fun f => garble e f) = 1
  commutes : forall s f,
    F.prob s f = Finset.univ.sum fun e => E.prob s e * garble e f

/-- Probability assigned to action `act` after observing through an experiment. -/
def InducedActionMass
    {State : Type u} {Obs : Type v} {Act : Type a}
    [Fintype Obs]
    (E : RatExperiment State Obs)
    (policy : Obs -> Act -> ℚ)
    (s : State)
    (act : Act) : ℚ :=
  Finset.univ.sum fun obs => E.prob s obs * policy obs act

/-- Compiled randomized policy probabilities along a garbling. -/
def compilePolicyProb
    {State : Type u} {ObsE : Type v} {ObsF : Type w} {Act : Type a}
    [Fintype ObsE] [Fintype ObsF]
    {E : RatExperiment State ObsE}
    {F : RatExperiment State ObsF}
    (h : StochasticGarbling E F)
    (policyF : ObsF -> Act -> ℚ) :
    ObsE -> Act -> ℚ :=
  fun e act => Finset.univ.sum fun f => h.garble e f * policyF f act

theorem compilePolicyProb_nonneg
    {State : Type u} {ObsE : Type v} {ObsF : Type w} {Act : Type a}
    [Fintype ObsE] [Fintype ObsF] [Fintype Act]
    {E : RatExperiment State ObsE}
    {F : RatExperiment State ObsF}
    (h : StochasticGarbling E F)
    (policyF : RandomizedPolicy ObsF Act)
    (e : ObsE) (act : Act) :
    0 <= compilePolicyProb h policyF.prob e act := by
  unfold compilePolicyProb
  exact Finset.sum_nonneg fun f _ =>
    mul_nonneg (h.nonneg e f) (policyF.nonneg f act)

theorem compilePolicyProb_row_sum_one
    {State : Type u} {ObsE : Type v} {ObsF : Type w} {Act : Type a}
    [Fintype ObsE] [Fintype ObsF] [Fintype Act]
    {E : RatExperiment State ObsE}
    {F : RatExperiment State ObsF}
    (h : StochasticGarbling E F)
    (policyF : RandomizedPolicy ObsF Act)
    (e : ObsE) :
    (Finset.univ.sum fun act =>
      compilePolicyProb h policyF.prob e act) = 1 := by
  unfold compilePolicyProb
  calc
    (Finset.univ.sum fun act =>
        Finset.univ.sum fun f => h.garble e f * policyF.prob f act)
        =
        Finset.univ.sum fun f =>
          Finset.univ.sum fun act => h.garble e f * policyF.prob f act := by
          rw [Finset.sum_comm]
    _ = Finset.univ.sum fun f =>
          h.garble e f * (Finset.univ.sum fun act => policyF.prob f act) := by
          apply Finset.sum_congr rfl
          intro f _hf
          rw [Finset.mul_sum]
    _ = Finset.univ.sum fun f => h.garble e f * 1 := by
          apply Finset.sum_congr rfl
          intro f _hf
          rw [policyF.row_sum_one f]
    _ = Finset.univ.sum fun f => h.garble e f := by
          simp
    _ = 1 := h.row_sum_one e

/-- Compile a valid randomized policy along a garbling. -/
def compileRandomizedPolicy
    {State : Type u} {ObsE : Type v} {ObsF : Type w} {Act : Type a}
    [Fintype ObsE] [Fintype ObsF] [Fintype Act]
    {E : RatExperiment State ObsE}
    {F : RatExperiment State ObsF}
    (h : StochasticGarbling E F)
    (policyF : RandomizedPolicy ObsF Act) :
    RandomizedPolicy ObsE Act where
  prob := compilePolicyProb h policyF.prob
  nonneg := compilePolicyProb_nonneg h policyF
  row_sum_one := compilePolicyProb_row_sum_one h policyF

/--
Forward stochastic Blackwell conservativity: garbling and randomized policy
compilation preserve induced action mass at every state/action pair.
-/
theorem inducedActionMass_compile_eq
    {State : Type u} {ObsE : Type v} {ObsF : Type w} {Act : Type a}
    [Fintype ObsE] [Fintype ObsF]
    {E : RatExperiment State ObsE}
    {F : RatExperiment State ObsF}
    (h : StochasticGarbling E F)
    (policyF : ObsF -> Act -> ℚ)
    (s : State)
    (act : Act) :
    InducedActionMass E (compilePolicyProb h policyF) s act =
      InducedActionMass F policyF s act := by
  unfold InducedActionMass compilePolicyProb
  calc
    (Finset.univ.sum fun e =>
        E.prob s e *
          (Finset.univ.sum fun f => h.garble e f * policyF f act))
        =
        Finset.univ.sum fun e =>
          Finset.univ.sum fun f =>
            E.prob s e * (h.garble e f * policyF f act) := by
          apply Finset.sum_congr rfl
          intro e _he
          rw [Finset.mul_sum]
    _ = Finset.univ.sum fun f =>
          Finset.univ.sum fun e =>
            E.prob s e * (h.garble e f * policyF f act) := by
          rw [Finset.sum_comm]
    _ = Finset.univ.sum fun f =>
          Finset.univ.sum fun e =>
            (E.prob s e * h.garble e f) * policyF f act := by
          apply Finset.sum_congr rfl
          intro f _hf
          apply Finset.sum_congr rfl
          intro e _he
          ring
    _ = Finset.univ.sum fun f =>
          (Finset.univ.sum fun e => E.prob s e * h.garble e f) *
            policyF f act := by
          apply Finset.sum_congr rfl
          intro f _hf
          rw [Finset.sum_mul]
    _ = Finset.univ.sum fun f => F.prob s f * policyF f act := by
          apply Finset.sum_congr rfl
          intro f _hf
          rw [<- h.commutes s f]

theorem inducedActionMass_compileRandomizedPolicy_eq
    {State : Type u} {ObsE : Type v} {ObsF : Type w} {Act : Type a}
    [Fintype ObsE] [Fintype ObsF] [Fintype Act]
    {E : RatExperiment State ObsE}
    {F : RatExperiment State ObsF}
    (h : StochasticGarbling E F)
    (policyF : RandomizedPolicy ObsF Act)
    (s : State)
    (act : Act) :
    InducedActionMass E (compileRandomizedPolicy h policyF).prob s act =
      InducedActionMass F policyF.prob s act :=
  inducedActionMass_compile_eq h policyF.prob s act

end BlackwellStochastic
end Decision
end OmegaProper
