import OmegaProper.Decision.Dominance

/-!
OmegaProper.Decision.DominanceExamples

Finite ODT1 v0 examples:

* W1: overlapping non-nested sets are incomparable under a discrete preorder;
* W2: Hoare/angelic and Smyth/demonic dominance point opposite ways;
* W5: structural dominance is relative to an admissible monotone valuation
  discipline; arbitrary nonmonotone valuations can reverse the declared order.
-/

namespace OmegaProper
namespace Decision
namespace DominanceExamples

open Dominance

/-! ## W1: Incomparability under a discrete preorder -/

inductive ThreeDiscrete where
  | a
  | b
  | c
deriving DecidableEq

instance : LE ThreeDiscrete where
  le x y := x = y

instance : Preorder ThreeDiscrete where
  le_refl := by
    intro x
    rfl
  le_trans := by
    intro x y z hxy hyz
    exact Eq.trans hxy hyz

instance : DecidableRel ((· <= ·) : ThreeDiscrete -> ThreeDiscrete -> Prop) := by
  intro x y
  change Decidable (x = y)
  infer_instance

def W1A : ThreeDiscrete -> Prop
  | ThreeDiscrete.a => True
  | ThreeDiscrete.b => True
  | ThreeDiscrete.c => False

def W1B : ThreeDiscrete -> Prop
  | ThreeDiscrete.a => False
  | ThreeDiscrete.b => True
  | ThreeDiscrete.c => True

theorem W1_not_hoare_A_B :
    Not (HoareDominates W1A W1B) := by
  rw [Dominance.not_hoare_iff_exists_failure_certificate]
  exact ⟨ThreeDiscrete.c, (by
    constructor
    · simp [W1B]
    · intro x hA hle
      cases x <;> simp [W1A] at hA
      · cases hle
      · cases hle)⟩

theorem W1_not_hoare_B_A :
    Not (HoareDominates W1B W1A) := by
  rw [Dominance.not_hoare_iff_exists_failure_certificate]
  exact ⟨ThreeDiscrete.a, (by
    constructor
    · simp [W1A]
    · intro x hB hle
      cases x <;> simp [W1B] at hB
      · cases hle
      · cases hle)⟩

theorem W1_not_smyth_A_B :
    Not (SmythDominates W1A W1B) := by
  rw [Dominance.not_smyth_iff_exists_failure_certificate]
  exact ⟨ThreeDiscrete.a, (by
    constructor
    · simp [W1A]
    · intro x hB hle
      cases x <;> simp [W1B] at hB
      · cases hle
      · cases hle)⟩

theorem W1_not_smyth_B_A :
    Not (SmythDominates W1B W1A) := by
  rw [Dominance.not_smyth_iff_exists_failure_certificate]
  exact ⟨ThreeDiscrete.c, (by
    constructor
    · simp [W1B]
    · intro x hA hle
      cases x <;> simp [W1A] at hA
      · cases hle
      · cases hle)⟩

theorem W1_incomparable :
    DominanceIncomparable W1A W1B :=
  ⟨W1_not_hoare_A_B, W1_not_hoare_B_A,
    W1_not_smyth_A_B, W1_not_smyth_B_A⟩

/-! ## W2: Hoare and Smyth point opposite ways -/

inductive Chain3 where
  | low
  | mid
  | high
deriving DecidableEq

def Chain3.rank : Chain3 -> Nat
  | Chain3.low => 0
  | Chain3.mid => 1
  | Chain3.high => 2

instance : LE Chain3 where
  le x y := x.rank <= y.rank

instance : Preorder Chain3 where
  le_refl := by
    intro x
    exact Nat.le_refl x.rank
  le_trans := by
    intro x y z hxy hyz
    exact Nat.le_trans hxy hyz

instance : DecidableRel ((· <= ·) : Chain3 -> Chain3 -> Prop) := by
  intro x y
  change Decidable (x.rank <= y.rank)
  infer_instance

def W2A : Chain3 -> Prop
  | Chain3.low => True
  | Chain3.mid => False
  | Chain3.high => True

def W2B : Chain3 -> Prop
  | Chain3.low => False
  | Chain3.mid => True
  | Chain3.high => False

theorem W2_A_hoare_B :
    HoareDominates W2A W2B := by
  intro b hB
  cases b <;> simp [W2B] at hB
  exact ⟨Chain3.high, by
    constructor
    · simp [W2A]
    · change Chain3.rank Chain3.mid <= Chain3.rank Chain3.high
      decide⟩

theorem W2_not_B_hoare_A :
    Not (HoareDominates W2B W2A) := by
  rw [Dominance.not_hoare_iff_exists_failure_certificate]
  exact ⟨Chain3.high, (by
    constructor
    · simp [W2A]
    · intro b hB hle
      cases b <;> simp [W2B] at hB
      have hNo : Not (Chain3.high <= Chain3.mid) := by
        change Not (Chain3.rank Chain3.high <= Chain3.rank Chain3.mid)
        decide
      exact hNo hle)⟩

theorem W2_not_A_smyth_B :
    Not (SmythDominates W2A W2B) := by
  rw [Dominance.not_smyth_iff_exists_failure_certificate]
  exact ⟨Chain3.low, (by
    constructor
    · simp [W2A]
    · intro b hB hle
      cases b <;> simp [W2B] at hB
      have hNo : Not (Chain3.mid <= Chain3.low) := by
        change Not (Chain3.rank Chain3.mid <= Chain3.rank Chain3.low)
        decide
      exact hNo hle)⟩

theorem W2_B_smyth_A :
    SmythDominates W2B W2A := by
  intro b hB
  cases b <;> simp [W2B] at hB
  exact ⟨Chain3.low, by
    constructor
    · simp [W2A]
    · change Chain3.rank Chain3.low <= Chain3.rank Chain3.mid
      decide⟩

theorem W2_angelic_demonic_diverge :
    HoareDominates W2A W2B /\
      Not (HoareDominates W2B W2A) /\
      Not (SmythDominates W2A W2B) /\
      SmythDominates W2B W2A :=
  ⟨W2_A_hoare_B, W2_not_B_hoare_A,
    W2_not_A_smyth_B, W2_B_smyth_A⟩

/-! ## W5: valuation-class relativity -/

inductive TwoOutcome where
  | low
  | high
deriving DecidableEq

def TwoOutcome.rank : TwoOutcome -> Nat
  | TwoOutcome.low => 0
  | TwoOutcome.high => 1

instance : LE TwoOutcome where
  le x y := x.rank <= y.rank

instance : Preorder TwoOutcome where
  le_refl := by
    intro x
    exact Nat.le_refl x.rank
  le_trans := by
    intro x y z hxy hyz
    exact Nat.le_trans hxy hyz

instance : DecidableRel ((· <= ·) : TwoOutcome -> TwoOutcome -> Prop) := by
  intro x y
  change Decidable (x.rank <= y.rank)
  infer_instance

def W5A : TwoOutcome -> Prop
  | TwoOutcome.low => False
  | TwoOutcome.high => True

def W5B : TwoOutcome -> Prop
  | TwoOutcome.low => True
  | TwoOutcome.high => False

theorem W5_A_hoare_B :
    HoareDominates W5A W5B := by
  intro b hB
  cases b <;> simp [W5B] at hB
  exact ⟨TwoOutcome.high, by
    constructor
    · simp [W5A]
    · change TwoOutcome.rank TwoOutcome.low <= TwoOutcome.rank TwoOutcome.high
      decide⟩

theorem W5_A_smyth_B :
    SmythDominates W5A W5B := by
  intro a hA
  cases a <;> simp [W5A] at hA
  exact ⟨TwoOutcome.low, by
    constructor
    · simp [W5B]
    · change TwoOutcome.rank TwoOutcome.low <= TwoOutcome.rank TwoOutcome.high
      decide⟩

def prefersLow : TwoOutcome -> Nat
  | TwoOutcome.low => 1
  | TwoOutcome.high => 0

theorem prefersLow_prefers_low :
    prefersLow TwoOutcome.high < prefersLow TwoOutcome.low := by
  simp [prefersLow]

theorem prefersLow_not_monotone :
    Not (MonotoneValuation prefersLow) := by
  intro hMono
  have hLe : TwoOutcome.low <= TwoOutcome.high := by
    change TwoOutcome.rank TwoOutcome.low <= TwoOutcome.rank TwoOutcome.high
    decide
  have hVal := hMono TwoOutcome.low TwoOutcome.high hLe
  have hNo : Not (prefersLow TwoOutcome.low <= prefersLow TwoOutcome.high) := by
    change Not (1 <= 0)
    decide
  exact hNo hVal

theorem W5_structural_dominance_and_nonmonotone_reversal :
    HoareDominates W5A W5B /\
      SmythDominates W5A W5B /\
      prefersLow TwoOutcome.high < prefersLow TwoOutcome.low /\
      Not (MonotoneValuation prefersLow) :=
  ⟨W5_A_hoare_B, W5_A_smyth_B,
    prefersLow_prefers_low, prefersLow_not_monotone⟩

end DominanceExamples
end Decision
end OmegaProper
