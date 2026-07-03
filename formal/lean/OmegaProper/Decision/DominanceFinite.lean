import Mathlib.Data.Finset.Basic
import OmegaProper.Decision.DominanceAcceptance

/-!
OmegaProper.Decision.DominanceFinite

Finite best/worst monotone-valuation acceptance theorems for ODT1 dominance.

This file lifts the pointwise acceptance bridge to nonempty finite outcome
surfaces. It remains ODT1: it does not define final value, choose an action,
aggregate standing, introduce stochastic risk, prove Blackwell, or validate
Omega.
-/

namespace OmegaProper
namespace Decision
namespace Dominance

universe u

variable {W : Type u}

/-- A nonempty finite outcome surface. -/
structure FiniteOutcomeSurface (W : Type u) where
  carrier : Finset W
  nonempty : carrier.Nonempty

namespace FiniteOutcomeSurface

/-- Predicate view of membership in a finite outcome surface. -/
def Holds (S : FiniteOutcomeSurface W) : W -> Prop :=
  fun w => w ∈ S.carrier

theorem exists_mem (S : FiniteOutcomeSurface W) :
    exists w, S.Holds w := by
  rcases S.nonempty with ⟨w, hw⟩
  exact ⟨w, hw⟩

theorem mem_carrier_iff (S : FiniteOutcomeSurface W) (w : W) :
    S.Holds w <-> w ∈ S.carrier :=
  Iff.rfl

end FiniteOutcomeSurface

/-- `n` is a best value attained on `S`. -/
def IsBestValue
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat)
    (n : Nat) : Prop :=
  (exists w, S.Holds w /\ v w = n) /\
    forall w, S.Holds w -> v w <= n

/-- `n` is a worst value attained on `S`. -/
def IsWorstValue
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat)
    (n : Nat) : Prop :=
  (exists w, S.Holds w /\ v w = n) /\
    forall w, S.Holds w -> n <= v w

private theorem exists_best_value_list
    (v : W -> Nat) :
    forall (l : List W), l ≠ [] ->
      exists n,
        (exists w, w ∈ l /\ v w = n) /\
          forall w, w ∈ l -> v w <= n
  | [], h => False.elim (h rfl)
  | w :: ws, _ =>
      by
        by_cases hws : ws = []
        · exact ⟨v w,
            ⟨⟨w, by simp, rfl⟩,
              (by
                intro x hx
                simp [hws] at hx
                cases hx
                exact Nat.le_refl (v w))⟩⟩
        · rcases exists_best_value_list v ws hws with ⟨n, hAtt, hMax⟩
          by_cases hwn : v w <= n
          · exact ⟨n,
              ⟨hAtt.imp (by
                intro x hx
                exact ⟨by simp [hx.left], hx.right⟩),
                (by
                  intro x hx
                  cases hx with
                  | head =>
                      exact hwn
                  | tail _ hTail =>
                      exact hMax x hTail)⟩⟩
          · exact ⟨v w,
              ⟨⟨w, by simp, rfl⟩,
                (by
                  intro x hx
                  cases hx with
                  | head =>
                      exact Nat.le_refl (v w)
                  | tail _ hTail =>
                      have hnw : n <= v w := Nat.le_of_not_ge hwn
                      exact Nat.le_trans (hMax x hTail) hnw)⟩⟩

private theorem exists_worst_value_list
    (v : W -> Nat) :
    forall (l : List W), l ≠ [] ->
      exists n,
        (exists w, w ∈ l /\ v w = n) /\
          forall w, w ∈ l -> n <= v w
  | [], h => False.elim (h rfl)
  | w :: ws, _ =>
      by
        by_cases hws : ws = []
        · exact ⟨v w,
            ⟨⟨w, by simp, rfl⟩,
              (by
                intro x hx
                simp [hws] at hx
                cases hx
                exact Nat.le_refl (v w))⟩⟩
        · rcases exists_worst_value_list v ws hws with ⟨n, hAtt, hMin⟩
          by_cases hnw : n <= v w
          · exact ⟨n,
              ⟨hAtt.imp (by
                intro x hx
                exact ⟨by simp [hx.left], hx.right⟩),
                (by
                  intro x hx
                  cases hx with
                  | head =>
                      exact hnw
                  | tail _ hTail =>
                      exact hMin x hTail)⟩⟩
          · exact ⟨v w,
              ⟨⟨w, by simp, rfl⟩,
                (by
                  intro x hx
                  cases hx with
                  | head =>
                      exact Nat.le_refl (v w)
                  | tail _ hTail =>
                      have hwn : v w <= n := Nat.le_of_not_ge hnw
                      exact Nat.le_trans hwn (hMin x hTail))⟩⟩

theorem exists_best_value
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat) :
    exists n, IsBestValue S v n := by
  rcases S.nonempty with ⟨w0, hw0⟩
  have hListNonempty : S.carrier.toList ≠ [] := by
    intro hEmpty
    have hNotMem : w0 ∉ S.carrier.toList := by simp [hEmpty]
    exact hNotMem (by simpa using hw0)
  rcases exists_best_value_list v S.carrier.toList hListNonempty with
    ⟨n, hAtt, hMax⟩
  exact ⟨n,
    ⟨hAtt.imp (by
      intro w hw
      exact ⟨by simpa using hw.left, hw.right⟩),
      (by
        intro w hw
        exact hMax w (by simpa using hw))⟩⟩

theorem exists_worst_value
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat) :
    exists n, IsWorstValue S v n := by
  rcases S.nonempty with ⟨w0, hw0⟩
  have hListNonempty : S.carrier.toList ≠ [] := by
    intro hEmpty
    have hNotMem : w0 ∉ S.carrier.toList := by simp [hEmpty]
    exact hNotMem (by simpa using hw0)
  rcases exists_worst_value_list v S.carrier.toList hListNonempty with
    ⟨n, hAtt, hMin⟩
  exact ⟨n,
    ⟨hAtt.imp (by
      intro w hw
      exact ⟨by simpa using hw.left, hw.right⟩),
      (by
        intro w hw
        exact hMin w (by simpa using hw))⟩⟩

noncomputable def bestValue
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat) : Nat :=
  Classical.choose (exists_best_value S v)

noncomputable def worstValue
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat) : Nat :=
  Classical.choose (exists_worst_value S v)

theorem bestValue_isBestValue
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat) :
    IsBestValue S v (bestValue S v) :=
  Classical.choose_spec (exists_best_value S v)

theorem worstValue_isWorstValue
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat) :
    IsWorstValue S v (worstValue S v) :=
  Classical.choose_spec (exists_worst_value S v)

theorem IsBestValue.unique
    {S : FiniteOutcomeSurface W}
    {v : W -> Nat}
    {n m : Nat}
    (hn : IsBestValue S v n)
    (hm : IsBestValue S v m) :
    n = m := by
  rcases hn.left with ⟨wn, hwn, hvn⟩
  rcases hm.left with ⟨wm, hwm, hvm⟩
  have hnm : n <= m := by
    rw [← hvn]
    exact hm.right wn hwn
  have hmn : m <= n := by
    rw [← hvm]
    exact hn.right wm hwm
  exact Nat.le_antisymm hnm hmn

theorem IsWorstValue.unique
    {S : FiniteOutcomeSurface W}
    {v : W -> Nat}
    {n m : Nat}
    (hn : IsWorstValue S v n)
    (hm : IsWorstValue S v m) :
    n = m := by
  rcases hn.left with ⟨wn, hwn, hvn⟩
  rcases hm.left with ⟨wm, hwm, hvm⟩
  have hnm : n <= m := by
    rw [← hvm]
    exact hn.right wm hwm
  have hmn : m <= n := by
    rw [← hvn]
    exact hm.right wn hwn
  exact Nat.le_antisymm hnm hmn

theorem bestValue_eq_of_isBestValue
    {S : FiniteOutcomeSurface W}
    {v : W -> Nat}
    {n : Nat}
    (h : IsBestValue S v n) :
    bestValue S v = n :=
  (bestValue_isBestValue S v).unique h

theorem worstValue_eq_of_isWorstValue
    {S : FiniteOutcomeSurface W}
    {v : W -> Nat}
    {n : Nat}
    (h : IsWorstValue S v n) :
    worstValue S v = n :=
  (worstValue_isWorstValue S v).unique h

def BestValueGE
    (A B : FiniteOutcomeSurface W)
    (v : W -> Nat) : Prop :=
  bestValue B v <= bestValue A v

def WorstValueGE
    (A B : FiniteOutcomeSurface W)
    (v : W -> Nat) : Prop :=
  worstValue B v <= worstValue A v

theorem bestValue_ge_of_mem
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat)
    {w : W}
    (hw : S.Holds w) :
    v w <= bestValue S v :=
  (bestValue_isBestValue S v).right w hw

theorem worstValue_le_of_mem
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat)
    {w : W}
    (hw : S.Holds w) :
    worstValue S v <= v w :=
  (worstValue_isWorstValue S v).right w hw

theorem exists_mem_of_bestValue_pos
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat)
    (hPos : 0 < bestValue S v) :
    exists w, S.Holds w /\ 0 < v w := by
  rcases (bestValue_isBestValue S v).left with ⟨w, hw, hv⟩
  exact ⟨w, hw, by simpa [hv] using hPos⟩

theorem exists_mem_of_worstValue_eq_zero
    (S : FiniteOutcomeSurface W)
    (v : W -> Nat)
    (hZero : worstValue S v = 0) :
    exists w, S.Holds w /\ v w = 0 := by
  rcases (worstValue_isWorstValue S v).left with ⟨w, hw, hv⟩
  exact ⟨w, hw, by simpa [hZero] using hv⟩

variable [Preorder W]

/--
Finite Hoare acceptance: structural Hoare dominance is equivalent to unanimous
best-case weak preference across monotone valuations.
-/
theorem hoare_iff_all_monotone_bestValue_ge
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (A B : FiniteOutcomeSurface W) :
    HoareDominates A.Holds B.Holds <->
      forall v : W -> Nat,
        MonotoneValuation v ->
        BestValueGE A B v := by
  constructor
  · intro hHoare v hMono
    rcases (bestValue_isBestValue B v).left with ⟨b, hB, hbBest⟩
    rcases hHoare b hB with ⟨a, hA, hba⟩
    have hb_le_va : v b <= v a := hMono b a hba
    have hva_le_bestA : v a <= bestValue A v :=
      bestValue_ge_of_mem A v hA
    calc
      bestValue B v = v b := hbBest.symm
      _ <= v a := hb_le_va
      _ <= bestValue A v := hva_le_bestA
  · intro hAll
    have hPointwise :=
      (hoare_iff_all_monotone_angelic_covers A.Holds B.Holds).mpr
        (by
          intro v hMono b hB
          have hBest : bestValue B v <= bestValue A v := hAll v hMono
          have hvb_le_bestB : v b <= bestValue B v :=
            bestValue_ge_of_mem B v hB
          rcases (bestValue_isBestValue A v).left with ⟨a, hA, haBest⟩
          exact ⟨a, hA, by
            calc
              v b <= bestValue B v := hvb_le_bestB
              _ <= bestValue A v := hBest
              _ = v a := haBest.symm⟩)
    exact hPointwise

/--
Finite Smyth acceptance: structural Smyth dominance is equivalent to unanimous
worst-case weak preference across monotone valuations.
-/
theorem smyth_iff_all_monotone_worstValue_ge
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (A B : FiniteOutcomeSurface W) :
    SmythDominates A.Holds B.Holds <->
      forall v : W -> Nat,
        MonotoneValuation v ->
        WorstValueGE A B v := by
  constructor
  · intro hSmyth v hMono
    rcases (worstValue_isWorstValue A v).left with ⟨a, hA, haWorst⟩
    rcases hSmyth a hA with ⟨b, hB, hba⟩
    have hvb_le_va : v b <= v a := hMono b a hba
    have worstB_le_vb : worstValue B v <= v b :=
      worstValue_le_of_mem B v hB
    calc
      worstValue B v <= v b := worstB_le_vb
      _ <= v a := hvb_le_va
      _ = worstValue A v := haWorst
  · intro hAll
    have hPointwise :=
      (smyth_iff_all_monotone_demonic_floors A.Holds B.Holds).mpr
        (by
          intro v hMono a hA
          have hWorst : worstValue B v <= worstValue A v := hAll v hMono
          have worstA_le_va : worstValue A v <= v a :=
            worstValue_le_of_mem A v hA
          rcases (worstValue_isWorstValue B v).left with ⟨b, hB, hbWorst⟩
          exact ⟨b, hB, by
            calc
              v b = worstValue B v := hbWorst
              _ <= worstValue A v := hWorst
              _ <= v a := worstA_le_va⟩)
    exact hPointwise

end Dominance
end Decision
end OmegaProper
