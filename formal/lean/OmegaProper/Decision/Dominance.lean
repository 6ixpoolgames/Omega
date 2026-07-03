import Mathlib.Order.Basic

/-!
OmegaProper.Decision.Dominance

ODT1 v0: value-parametric dominance over already-licensed continuation outcome
surfaces.

ODT0 licenses options. ODT1 compares the certified outcome surfaces of options
relative to a declared preorder over outcomes. This file does not define value,
aggregation, arbitration, agency, identity, probability, stochastic risk,
Blackwell theory, quantum structure, or Omega.
-/

namespace OmegaProper
namespace Decision
namespace Dominance

universe u

variable {W : Type u} [Preorder W]

/--
An already-licensed option's certified achievable outcome surface.

ODT1 v0 keeps this abstract. In later work, `Achievable` should be produced by
an ODT0 `LicenseVia` or `PlanLicense` plus an outcome-surface compiler.
-/
structure LicensedOption (W : Type u) where
  Achievable : W -> Prop
  nonempty : exists w, Achievable w

/--
Hoare/angelic dominance.

`A` Hoare-dominates `B` when every `B` outcome is no better than some achievable
`A` outcome.
-/
def HoareDominates (A B : W -> Prop) : Prop :=
  forall b, B b -> exists a, A a /\ b <= a

/--
Smyth/demonic dominance.

`A` Smyth-dominates `B` when every `A` outcome has some `B` outcome beneath it.
-/
def SmythDominates (A B : W -> Prop) : Prop :=
  forall a, A a -> exists b, B b /\ b <= a

/-- Plotkin dominance requires both Hoare and Smyth dominance. -/
def PlotkinDominates (A B : W -> Prop) : Prop :=
  HoareDominates A B /\ SmythDominates A B

/-- Equivalence under both Hoare and Smyth preorders. -/
def DominanceEquivalent (A B : W -> Prop) : Prop :=
  HoareDominates A B /\ HoareDominates B A /\
    SmythDominates A B /\ SmythDominates B A

/-- Full structural incomparability under the v0 dominance relations. -/
def DominanceIncomparable (A B : W -> Prop) : Prop :=
  Not (HoareDominates A B) /\
    Not (HoareDominates B A) /\
    Not (SmythDominates A B) /\
    Not (SmythDominates B A)

/-- A named witness that `A` fails to Hoare-dominate `B`. -/
def HoareFailureCertificate (A B : W -> Prop) (b : W) : Prop :=
  B b /\ forall a, A a -> Not (b <= a)

/-- A named witness that `A` fails to Smyth-dominate `B`. -/
def SmythFailureCertificate (A B : W -> Prop) (a : W) : Prop :=
  A a /\ forall b, B b -> Not (b <= a)

theorem hoare_refl (A : W -> Prop) :
    HoareDominates A A := by
  intro a hA
  exact ⟨a, hA, le_rfl⟩

theorem hoare_trans {A B C : W -> Prop}
    (hAB : HoareDominates A B)
    (hBC : HoareDominates B C) :
    HoareDominates A C := by
  intro c hC
  rcases hBC c hC with ⟨b, hB, hcb⟩
  rcases hAB b hB with ⟨a, hA, hba⟩
  exact ⟨a, hA, le_trans hcb hba⟩

theorem smyth_refl (A : W -> Prop) :
    SmythDominates A A := by
  intro a hA
  exact ⟨a, hA, le_rfl⟩

theorem smyth_trans {A B C : W -> Prop}
    (hAB : SmythDominates A B)
    (hBC : SmythDominates B C) :
    SmythDominates A C := by
  intro a hA
  rcases hAB a hA with ⟨b, hB, hba⟩
  rcases hBC b hB with ⟨c, hC, hcb⟩
  exact ⟨c, hC, le_trans hcb hba⟩

theorem plotkin_refl (A : W -> Prop) :
    PlotkinDominates A A :=
  ⟨hoare_refl A, smyth_refl A⟩

theorem plotkin_trans {A B C : W -> Prop}
    (hAB : PlotkinDominates A B)
    (hBC : PlotkinDominates B C) :
    PlotkinDominates A C :=
  ⟨hoare_trans hAB.left hBC.left, smyth_trans hAB.right hBC.right⟩

theorem not_hoare_iff_exists_failure_certificate
    (A B : W -> Prop) :
    Not (HoareDominates A B) <->
      exists b, HoareFailureCertificate A B b := by
  classical
  constructor
  · intro hNot
    rcases not_forall.mp hNot with ⟨b, hbNot⟩
    have hB : B b := Classical.byContradiction (by
      intro hNotB
      exact hbNot (fun hB => False.elim (hNotB hB)))
    exact ⟨b, hB, (by
      intro a hA hle
      exact hbNot (fun _ => ⟨a, hA, hle⟩))⟩
  · intro hCert hHoare
    rcases hCert with ⟨b, hB, hNoA⟩
    rcases hHoare b hB with ⟨a, hA, hle⟩
    exact hNoA a hA hle

theorem not_smyth_iff_exists_failure_certificate
    (A B : W -> Prop) :
    Not (SmythDominates A B) <->
      exists a, SmythFailureCertificate A B a := by
  classical
  constructor
  · intro hNot
    rcases not_forall.mp hNot with ⟨a, haNot⟩
    have hA : A a := Classical.byContradiction (by
      intro hNotA
      exact haNot (fun hA => False.elim (hNotA hA)))
    exact ⟨a, hA, (by
      intro b hB hle
      exact haNot (fun _ => ⟨b, hB, hle⟩))⟩
  · intro hCert hSmyth
    rcases hCert with ⟨a, hA, hNoB⟩
    rcases hSmyth a hA with ⟨b, hB, hle⟩
    exact hNoB b hB hle

/-- A monotone valuation over the declared outcome preorder. -/
def MonotoneValuation (v : W -> Nat) : Prop :=
  forall x y, x <= y -> v x <= v y

/--
An up-set indicator valuation: it returns `1` exactly above the threshold `b`.

This is a small separating-valuation primitive for later acceptance theorems.
-/
def UpIndicator [DecidableRel ((· <= ·) : W -> W -> Prop)] (b : W) :
    W -> Nat :=
  fun w => if b <= w then 1 else 0

theorem upIndicator_monotone
    [DecidableRel ((· <= ·) : W -> W -> Prop)]
    (b : W) :
    MonotoneValuation (UpIndicator b) := by
  intro x y hxy
  unfold UpIndicator
  by_cases hbx : b <= x
  · have hby : b <= y := le_trans hbx hxy
    simp [hbx, hby]
  · by_cases hby : b <= y
    · simp [hbx, hby]
    · simp [hbx, hby]

end Dominance
end Decision
end OmegaProper
