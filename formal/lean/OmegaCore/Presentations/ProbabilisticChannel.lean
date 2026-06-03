import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.Basic

/-!
OmegaCore.Presentations.ProbabilisticChannel

Finite probabilistic channel presentation for Omega Primitive Calculus v0.

This file layers finite stochastic measurement over the existing support-level
finite channel presentation. It keeps exact support recovery separate from
probabilistic decoder success.

The numerical layer uses natural-number weights. A channel is `K : X -> Y -> Nat`
and a prior is `pi : X -> Nat`; probabilities are represented by exact
cross-multiplied mass comparisons rather than by `Rat` or `Real`.

This is a formal presentation/enrichment. It is not an empirical adapter,
Future Field Atlas semantics, compatibility/completion machinery, valuerhood,
agency, identity, ethics, or Omega validation.
-/

namespace OmegaCore

namespace Presentations

namespace ProbabilisticChannel

universe u v w z

/-- Finite channel support induced by positive natural-number weight. -/
def Supports {X : Type u} {Y : Type v}
    (K : X -> Y -> Nat) (x : X) (y : Y) : Prop :=
  K x y > 0

/-- Row total for a finite natural-weight channel. -/
def rowSum {X : Type u} {Y : Type v} [Fintype Y]
    (K : X -> Y -> Nat) (x : X) : Nat :=
  Finset.univ.sum (fun y => K x y)

/-- Prior total for a finite natural-weight prior. -/
def priorSum {X : Type u} [Fintype X]
    (pi : X -> Nat) : Nat :=
  Finset.univ.sum pi

/-- Observable distinction as a labeling / partition of a carrier. -/
structure Distinction (X : Type u) where
  Label : Type v
  obs : X -> Label

/-- Exact support-level recovery through a natural-weight channel. -/
def ExactSupportRecovers
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    (K : X -> Y -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec : LE -> LD) : Prop :=
  forall x y, Supports K x y -> dec (E y) = D x

/-- Unnormalized decoder success mass under a finite channel and prior. -/
def successMass
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec : LE -> LD) : Nat :=
  Finset.univ.sum fun x =>
    pi x * Finset.univ.sum fun y =>
      if dec (E y) = D x then K x y else 0

/-- Unnormalized decoder error mass under a finite channel and prior. -/
def errorMass
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec : LE -> LD) : Nat :=
  Finset.univ.sum fun x =>
    pi x * Finset.univ.sum fun y =>
      if dec (E y) = D x then 0 else K x y

/-- Total channel/prior mass. -/
def totalMass
    {X : Type u} {Y : Type v}
    [Fintype X] [Fintype Y]
    (K : X -> Y -> Nat)
    (pi : X -> Nat) : Nat :=
  Finset.univ.sum fun x => pi x * rowSum K x

/-- Every source row has positive channel mass. -/
def PositiveRows {X : Type u} {Y : Type v} [Fintype Y]
    (K : X -> Y -> Nat) : Prop :=
  forall x, rowSum K x > 0

/-- The declared prior has positive total mass. -/
def NonzeroPrior {X : Type u} [Fintype X]
    (pi : X -> Nat) : Prop :=
  priorSum pi > 0

/-- The channel/prior pairing has positive observable total mass. -/
def PositiveTotalMass
    {X : Type u} {Y : Type v}
    [Fintype X] [Fintype Y]
    (K : X -> Y -> Nat)
    (pi : X -> Nat) : Prop :=
  totalMass K pi > 0

/-- Valid cross-multiplied success threshold `num / den`. -/
def ThresholdValid (num den : Nat) : Prop :=
  den > 0 ∧ num <= den

/-- Perfect probabilistic recovery means success mass equals total mass. -/
def PerfectProbRecovers
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec : LE -> LD) : Prop :=
  successMass K pi D E dec = totalMass K pi

/-- Cross-multiplied thresholded probabilistic recovery.

`num / den` is the intended success threshold. For example, `95 100` means
success at least 95%. -/
def ProbRecoversAtLeast
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec : LE -> LD)
    (num den : Nat) : Prop :=
  den * successMass K pi D E dec >= num * totalMass K pi

/-- Full-support prior predicate for later probabilistic converse theorems. -/
def FullSupportPrior {X : Type u} (pi : X -> Nat) : Prop :=
  forall x, pi x > 0

/-- Lightweight policy marker. Full Bayes optimization is intentionally outside
this first skeleton. -/
structure RecoveryPolicy where
  name : String

def fixedDeclaredPolicy : RecoveryPolicy where
  name := "fixed_declared_target_distinction"

def bayesBestPolicy : RecoveryPolicy where
  name := "bayes_best_target_distinction"

/-- Success mass plus error mass accounts for all channel/prior mass. -/
theorem successMass_add_errorMass_eq_totalMass
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec : LE -> LD) :
    successMass K pi D E dec + errorMass K pi D E dec = totalMass K pi := by
  unfold successMass errorMass totalMass rowSum
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro x _hx
  rw [← Nat.mul_add]
  congr 1
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro y _hy
  by_cases hEq : dec (E y) = D x
  · simp [hEq]
  · simp [hEq]

/-- Perfect probabilistic recovery has zero error mass. -/
theorem perfectProb_implies_errorMass_zero
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    {K : X -> Y -> Nat}
    {pi : X -> Nat}
    {D : X -> LD}
    {E : Y -> LE}
    {dec : LE -> LD}
    (h : PerfectProbRecovers K pi D E dec) :
    errorMass K pi D E dec = 0 := by
  have hAccount := successMass_add_errorMass_eq_totalMass K pi D E dec
  unfold PerfectProbRecovers at h
  rw [h] at hAccount
  exact Nat.add_eq_left.mp hAccount

/-- A single incorrectly decoded positive-support transition creates positive
error mass under a full-support prior. -/
theorem errorMass_pos_of_bad_support
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    {K : X -> Y -> Nat}
    {pi : X -> Nat}
    {D : X -> LD}
    {E : Y -> LE}
    {dec : LE -> LD}
    (hfull : FullSupportPrior pi)
    {x : X} {y : Y}
    (hSupport : Supports K x y)
    (hBad : dec (E y) ≠ D x) :
    errorMass K pi D E dec > 0 := by
  unfold errorMass
  refine Finset.sum_pos' (fun _ _ => Nat.zero_le _) ?_
  refine ⟨x, Finset.mem_univ x, ?_⟩
  have hInnerPos :
      (Finset.univ.sum fun y' =>
        if dec (E y') = D x then 0 else K x y') > 0 := by
    refine Finset.sum_pos' (fun _ _ => Nat.zero_le _) ?_
    refine ⟨y, Finset.mem_univ y, ?_⟩
    simpa [Supports, hBad] using hSupport
  exact Nat.mul_pos (hfull x) hInnerPos

/-- With a full-support prior, perfect probabilistic recovery forces exact
support recovery. -/
theorem perfectProb_fullPrior_implies_exactSupport
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    {K : X -> Y -> Nat}
    {pi : X -> Nat}
    {D : X -> LD}
    {E : Y -> LE}
    {dec : LE -> LD}
    (hfull : FullSupportPrior pi)
    (hperf : PerfectProbRecovers K pi D E dec) :
    ExactSupportRecovers K D E dec := by
  intro x y hSupport
  by_contra hBad
  have hErrorZero := perfectProb_implies_errorMass_zero hperf
  have hErrorPos :=
    errorMass_pos_of_bad_support
      (K := K) (pi := pi) (D := D) (E := E) (dec := dec)
      hfull hSupport hBad
  rw [hErrorZero] at hErrorPos
  exact Nat.lt_irrefl 0 hErrorPos

theorem exactSupport_indicator_eq
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [DecidableEq LD]
    {K : X -> Y -> Nat}
    {D : X -> LD}
    {E : Y -> LE}
    {dec : LE -> LD}
    (h : ExactSupportRecovers K D E dec)
    (x : X) (y : Y) :
    (if dec (E y) = D x then K x y else 0) = K x y := by
  by_cases hK : K x y > 0
  · have hCorrect : dec (E y) = D x := h x y hK
    simp [hCorrect]
  · have hZero : K x y = 0 := Nat.eq_zero_of_not_pos hK
    simp [hZero]

/-- Exact support recovery implies perfect probabilistic recovery under every
prior. No full-support prior assumption is needed. -/
theorem exactSupport_implies_perfectProb
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    {K : X -> Y -> Nat}
    {pi : X -> Nat}
    {D : X -> LD}
    {E : Y -> LE}
    {dec : LE -> LD}
    (h : ExactSupportRecovers K D E dec) :
    PerfectProbRecovers K pi D E dec := by
  unfold PerfectProbRecovers successMass totalMass rowSum
  apply Finset.sum_congr rfl
  intro x _hx
  congr 1
  apply Finset.sum_congr rfl
  intro y _hy
  exact exactSupport_indicator_eq h x y

/-- Exact support recovery gives threshold recovery at the full-success
threshold. -/
theorem exactSupport_implies_probAtLeast_100
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    {K : X -> Y -> Nat}
    {pi : X -> Nat}
    {D : X -> LD}
    {E : Y -> LE}
    {dec : LE -> LD}
    (h : ExactSupportRecovers K D E dec) :
    ProbRecoversAtLeast K pi D E dec 100 100 := by
  unfold ProbRecoversAtLeast
  rw [exactSupport_implies_perfectProb h]

/-- Two-point carrier for finite stochastic-channel counterexamples. -/
inductive Bit where
  | zero
  | one
  deriving DecidableEq

instance : Fintype Bit where
  elems := {Bit.zero, Bit.one}
  complete := by
    intro x
    cases x <;> simp

def bitObs : Bit -> Bool
  | Bit.zero => false
  | Bit.one => true

def boolId (b : Bool) : Bool := b

/-!
Counterexample 1:

Perfect probabilistic recovery under a non-full-support prior does not imply
exact support recovery.
-/

def collapseToZeroChannel : Bit -> Bit -> Nat
  | Bit.zero, Bit.zero => 1
  | Bit.zero, Bit.one => 0
  | Bit.one, Bit.zero => 1
  | Bit.one, Bit.one => 0

def priorOnlyZero : Bit -> Nat
  | Bit.zero => 1
  | Bit.one => 0

theorem collapseToZero_successMass :
    successMass collapseToZeroChannel priorOnlyZero bitObs bitObs boolId = 1 := by
  unfold successMass collapseToZeroChannel priorOnlyZero bitObs boolId
  native_decide

theorem collapseToZero_totalMass :
    totalMass collapseToZeroChannel priorOnlyZero = 1 := by
  unfold totalMass rowSum collapseToZeroChannel priorOnlyZero
  native_decide

theorem collapseToZero_perfectProb :
    PerfectProbRecovers collapseToZeroChannel priorOnlyZero bitObs bitObs boolId := by
  unfold PerfectProbRecovers
  rw [collapseToZero_successMass, collapseToZero_totalMass]

theorem collapseToZero_not_exactSupport :
    ¬ ExactSupportRecovers collapseToZeroChannel bitObs bitObs boolId := by
  intro h
  have hSupport : Supports collapseToZeroChannel Bit.one Bit.zero := by
    simp [Supports, collapseToZeroChannel]
  have hBad : boolId (bitObs Bit.zero) = bitObs Bit.one :=
    h Bit.one Bit.zero hSupport
  cases hBad

theorem perfectProb_not_exact_without_full_prior :
    PerfectProbRecovers collapseToZeroChannel priorOnlyZero bitObs bitObs boolId ∧
      ¬ ExactSupportRecovers collapseToZeroChannel bitObs bitObs boolId := by
  exact And.intro collapseToZero_perfectProb collapseToZero_not_exactSupport

/-!
Counterexample 2:

High probabilistic recovery can coexist with support-level ambiguity.
-/

def highButAmbiguousChannel : Bit -> Bit -> Nat
  | Bit.zero, Bit.zero => 100
  | Bit.zero, Bit.one => 0
  | Bit.one, Bit.zero => 1
  | Bit.one, Bit.one => 99

def uniformPriorBit : Bit -> Nat
  | Bit.zero => 1
  | Bit.one => 1

theorem highButAmbiguous_successMass :
    successMass highButAmbiguousChannel uniformPriorBit bitObs bitObs boolId = 199 := by
  unfold successMass highButAmbiguousChannel uniformPriorBit bitObs boolId
  native_decide

theorem highButAmbiguous_totalMass :
    totalMass highButAmbiguousChannel uniformPriorBit = 200 := by
  unfold totalMass rowSum highButAmbiguousChannel uniformPriorBit
  native_decide

theorem highButAmbiguous_atLeast95 :
    ProbRecoversAtLeast highButAmbiguousChannel uniformPriorBit bitObs bitObs boolId 95 100 := by
  unfold ProbRecoversAtLeast
  rw [highButAmbiguous_successMass, highButAmbiguous_totalMass]
  native_decide

theorem highButAmbiguous_not_exactSupport :
    ¬ ExactSupportRecovers highButAmbiguousChannel bitObs bitObs boolId := by
  intro h
  have hSupport : Supports highButAmbiguousChannel Bit.one Bit.zero := by
    simp [Supports, highButAmbiguousChannel]
  have hBad : boolId (bitObs Bit.zero) = bitObs Bit.one :=
    h Bit.one Bit.zero hSupport
  cases hBad

theorem highProb_not_exactSupport :
    ProbRecoversAtLeast highButAmbiguousChannel uniformPriorBit bitObs bitObs boolId 95 100 ∧
      ¬ ExactSupportRecovers highButAmbiguousChannel bitObs bitObs boolId := by
  exact And.intro highButAmbiguous_atLeast95 highButAmbiguous_not_exactSupport

end ProbabilisticChannel

end Presentations

end OmegaCore
