import OmegaCore.Completion

/-!
OmegaCore.Counterexamples

Finite completion counterexamples for Omega Primitive Calculus v0.

This module stays inside abstract finite admissibility structure. It does not
define recoverability, recurrent recovery, process bundles, proto-valuers,
compatibility semantics, empirical adapters, or Future Field Atlas language.
-/

namespace OmegaCore

namespace CompletionCounterexamples

universe u

/-- Abstract pairwise-style admissibility on a three-element universe:
admissible families have size at most two. -/
def AdmAtMostTwo (Y : Finset (Fin 3)) : Prop :=
  Y.card <= 2

instance admAtMostTwoDecidable (Y : Finset (Fin 3)) :
    Decidable (AdmAtMostTwo Y) := by
  unfold AdmAtMostTwo
  infer_instance

/-- Every two-element family is admissible under `AdmAtMostTwo`. -/
theorem admAtMostTwo_pair
    (Y : Finset (Fin 3)) :
    Y.card = 2 -> AdmAtMostTwo Y := by
  intro hcard
  unfold AdmAtMostTwo
  rw [hcard]

/-- The full three-element family is not admissible under `AdmAtMostTwo`. -/
theorem admAtMostTwo_not_triple :
    Not (AdmAtMostTwo (Finset.univ : Finset (Fin 3))) := by
  native_decide

/-- Pairwise admissibility does not imply joint admissibility. -/
theorem pairwise_admissible_not_joint :
    (forall Y : Finset (Fin 3), Y.card = 2 -> AdmAtMostTwo Y) /\
      Not (AdmAtMostTwo (Finset.univ : Finset (Fin 3))) := by
  exact And.intro admAtMostTwo_pair admAtMostTwo_not_triple

/-- One maximal branch in the fork counterexample. -/
def ab : Finset (Fin 3) :=
  {0, 1}

/-- Another maximal branch in the fork counterexample. -/
def ac : Finset (Fin 3) :=
  {0, 2}

/-- Downward-closed fork admissibility: a family is admissible when it lies in
one of two incompatible branches. -/
def AdmFork (Y : Finset (Fin 3)) : Prop :=
  Y <= ab \/ Y <= ac

instance admForkDecidable (Y : Finset (Fin 3)) :
    Decidable (AdmFork Y) := by
  unfold AdmFork
  infer_instance

/-- The `ab` branch is not contained in the `ac` branch. -/
theorem not_ab_subset_ac :
    Not (ab <= ac) := by
  unfold ab ac
  decide

/-- The `ac` branch is not contained in the `ab` branch. -/
theorem not_ac_subset_ab :
    Not (ac <= ab) := by
  unfold ab ac
  decide

/-- The two fork branches are distinct. -/
theorem ab_ne_ac :
    Not (ab = ac) := by
  unfold ab ac
  decide

/-- `ab` is subset-maximal for the downward-closed fork. -/
theorem ab_subsetMaximal :
    Completion.SubsetMaximalFinset AdmFork ab := by
  unfold Completion.SubsetMaximalFinset Completion.SubsetMaximal
  exact And.intro (Or.inl le_rfl)
    (by
      intro Z hAdmZ hAbZ
      cases hAdmZ with
      | inl hZab =>
          exact hZab
      | inr hZac =>
          exact False.elim (not_ab_subset_ac (le_trans hAbZ hZac)))

/-- `ac` is subset-maximal for the downward-closed fork. -/
theorem ac_subsetMaximal :
    Completion.SubsetMaximalFinset AdmFork ac := by
  unfold Completion.SubsetMaximalFinset Completion.SubsetMaximal
  exact And.intro (Or.inr le_rfl)
    (by
      intro Z hAdmZ hAcZ
      cases hAdmZ with
      | inl hZab =>
          exact False.elim (not_ac_subset_ab (le_trans hAcZ hZab))
      | inr hZac =>
          exact hZac)

/-- The two maximal admissible completions are distinct. -/
theorem distinct_maximal_completions :
    exists Y Z : Finset (Fin 3),
      Completion.SubsetMaximalFinset AdmFork Y /\
        Completion.SubsetMaximalFinset AdmFork Z /\
        Not (Y = Z) := by
  exact Exists.intro ab
    (Exists.intro ac
      (And.intro ab_subsetMaximal
        (And.intro ac_subsetMaximal ab_ne_ac)))

/-- A greatest admissible family is admissible and contains every admissible
family. -/
def GreatestFinset
    {a : Type u}
    [DecidableEq a]
    (Adm : Finset a -> Prop)
    (G : Finset a) : Prop :=
  Adm G /\ forall Y : Finset a, Adm Y -> Y <= G

/-- The downward-closed fork has maximal completions but no greatest
completion. -/
theorem no_greatest_completion :
    Not (exists G : Finset (Fin 3), GreatestFinset AdmFork G) := by
  intro hGreatest
  cases hGreatest with
  | intro G hG =>
      have hAbG : ab <= G := hG.right ab (Or.inl le_rfl)
      have hAcG : ac <= G := hG.right ac (Or.inr le_rfl)
      cases hG.left with
      | inl hGab =>
          exact not_ac_subset_ab (le_trans hAcG hGab)
      | inr hGac =>
          exact not_ab_subset_ac (le_trans hAbG hGac)

end CompletionCounterexamples

end OmegaCore
