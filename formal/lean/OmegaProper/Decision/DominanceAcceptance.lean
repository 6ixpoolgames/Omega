import OmegaProper.Decision.Dominance

/-!
OmegaProper.Decision.DominanceAcceptance

Pointwise monotone-valuation acceptance bridge for ODT1 dominance.

This file proves that the structural Hoare and Smyth dominance relations have
the expected unanimous pointwise interpretation over monotone valuations. It is
not ODT2: it does not define final value, choose an action, aggregate standing,
or introduce probability/stochastic/quantum structure.
-/

namespace OmegaProper
namespace Decision
namespace Dominance

universe u

variable {W : Type u} [Preorder W]

/--
For a valuation `v`, every `B` outcome can be matched by an `A` outcome with at
least as much `v`-value.
-/
def AngelicValuationCovers (A B : W -> Prop) (v : W -> Nat) : Prop :=
  forall b, B b -> exists a, A a /\ v b <= v a

/--
For a valuation `v`, every `A` outcome has some `B` floor beneath it in
`v`-value.
-/
def DemonicValuationFloors (A B : W -> Prop) (v : W -> Nat) : Prop :=
  forall a, A a -> exists b, B b /\ v b <= v a

theorem upIndicator_self
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (b : W) :
    UpIndicator b b = 1 := by
  unfold UpIndicator
  simp

theorem upIndicator_eq_one_iff
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (b w : W) :
    UpIndicator b w = 1 <-> b <= w := by
  unfold UpIndicator
  by_cases h : b <= w
  · simp [h]
  · simp [h]

theorem upIndicator_eq_zero_iff
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (b w : W) :
    UpIndicator b w = 0 <-> Not (b <= w) := by
  unfold UpIndicator
  by_cases h : b <= w
  · simp [h]
  · simp [h]

/--
Down-set complement indicator around `a`: it is `0` on outcomes below `a` and
`1` elsewhere.
-/
def AboveComplementIndicator
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (a : W) : W -> Nat :=
  fun w => if w <= a then 0 else 1

theorem aboveComplementIndicator_monotone
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (a : W) :
    MonotoneValuation (AboveComplementIndicator a) := by
  intro x y hxy
  unfold AboveComplementIndicator
  by_cases hxa : x <= a
  · by_cases hya : y <= a
    · simp [hxa, hya]
    · simp [hxa, hya]
  · have hyaFalse : Not (y <= a) := by
      intro hya
      exact hxa (le_trans hxy hya)
    simp [hxa, hyaFalse]

theorem aboveComplementIndicator_self
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (a : W) :
    AboveComplementIndicator a a = 0 := by
  unfold AboveComplementIndicator
  simp

theorem aboveComplementIndicator_eq_zero_iff
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (a w : W) :
    AboveComplementIndicator a w = 0 <-> w <= a := by
  unfold AboveComplementIndicator
  by_cases h : w <= a
  · simp [h]
  · simp [h]

theorem aboveComplementIndicator_eq_one_iff
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (a w : W) :
    AboveComplementIndicator a w = 1 <-> Not (w <= a) := by
  unfold AboveComplementIndicator
  by_cases h : w <= a
  · simp [h]
  · simp [h]

/--
Hoare dominance is exactly unanimous pointwise angelic cover across monotone
valuations.
-/
theorem hoare_iff_all_monotone_angelic_covers
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (A B : W -> Prop) :
    HoareDominates A B <->
      forall v : W -> Nat,
        MonotoneValuation v ->
        AngelicValuationCovers A B v := by
  constructor
  · intro hHoare v hMono b hB
    rcases hHoare b hB with ⟨a, hA, hba⟩
    exact ⟨a, hA, hMono b a hba⟩
  · intro hAll b hB
    have hCover :=
      hAll (UpIndicator b) (upIndicator_monotone b) b hB
    rcases hCover with ⟨a, hA, hVal⟩
    have hSelf : UpIndicator b b = 1 := upIndicator_self b
    have hAValOne : UpIndicator b a = 1 := by
      have hOneLe : 1 <= UpIndicator b a := by
        simpa [hSelf] using hVal
      have hUpper : UpIndicator b a <= 1 := by
        unfold UpIndicator
        by_cases hba : b <= a <;> simp [hba]
      exact Nat.le_antisymm hUpper hOneLe
    exact ⟨a, hA, (upIndicator_eq_one_iff b a).mp hAValOne⟩

/--
Smyth dominance is exactly unanimous pointwise demonic flooring across monotone
valuations.
-/
theorem smyth_iff_all_monotone_demonic_floors
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (A B : W -> Prop) :
    SmythDominates A B <->
      forall v : W -> Nat,
        MonotoneValuation v ->
        DemonicValuationFloors A B v := by
  constructor
  · intro hSmyth v hMono a hA
    rcases hSmyth a hA with ⟨b, hB, hba⟩
    exact ⟨b, hB, hMono b a hba⟩
  · intro hAll a hA
    have hFloor :=
      hAll (AboveComplementIndicator a)
        (aboveComplementIndicator_monotone a) a hA
    rcases hFloor with ⟨b, hB, hVal⟩
    have hSelf : AboveComplementIndicator a a = 0 :=
      aboveComplementIndicator_self a
    have hBValZero : AboveComplementIndicator a b = 0 := by
      have hLeZero : AboveComplementIndicator a b <= 0 := by
        simpa [hSelf] using hVal
      exact Nat.eq_zero_of_le_zero hLeZero
    exact ⟨b, hB, (aboveComplementIndicator_eq_zero_iff a b).mp hBValZero⟩

end Dominance
end Decision
end OmegaProper
