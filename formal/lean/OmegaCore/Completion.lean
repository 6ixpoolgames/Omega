import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Fintype.Powerset

/-!
OmegaCore.Completion

Finite maximal admissible completion skeleton for Omega Primitive Calculus v0.

This module is intentionally abstract. It does not define compatibility,
valuerhood, ethics, empirical adapters, or Future Field Atlas semantics. It
only proves that a finite, explicitly enumerated admissible-family space has a
subset-maximal admissible member when at least one admissible member exists.
-/

namespace OmegaCore

universe u

namespace Completion

/-- `Y` is subset-maximal for `Adm` under inclusion-like relation `le` when it
is admissible and every admissible extension of `Y` is extension-equivalent. -/
def SubsetMaximal
    {Fam : Type u}
    (Adm : Fam -> Prop)
    (le : Fam -> Fam -> Prop)
    (Y : Fam) : Prop :=
  Adm Y /\ forall Z : Fam, Adm Z -> le Y Z -> le Z Y

/-- Finset-specialized subset maximality under subset inclusion. -/
def SubsetMaximalFinset
    {a : Type u}
    [DecidableEq a]
    (Adm : Finset a -> Prop)
    (Y : Finset a) : Prop :=
  SubsetMaximal Adm (fun A B => A <= B) Y

/-- `Y` is an admissible member of `xs` whose size is at least every other
admissible listed member. -/
def MaxSizedInList
    {Fam : Type u}
    (Adm : Fam -> Prop)
    (size : Fam -> Nat)
    (xs : List Fam)
    (Y : Fam) : Prop :=
  Adm Y /\ List.Mem Y xs /\
    forall Z : Fam, Adm Z -> List.Mem Z xs -> size Z <= size Y

theorem exists_maxSizedInList
    {Fam : Type u}
    (Adm : Fam -> Prop)
    (size : Fam -> Nat)
    (xs : List Fam)
    (h : exists Y : Fam, Adm Y /\ List.Mem Y xs) :
    exists Y : Fam, MaxSizedInList Adm size xs Y := by
  induction xs with
  | nil =>
      cases h with
      | intro Y hY =>
          exact False.elim (List.not_mem_nil hY.right)
  | cons x xs ih =>
      by_cases hx : Adm x
      case pos =>
        by_cases htail : exists Y : Fam, Adm Y /\ List.Mem Y xs
        case pos =>
          cases ih htail with
          | intro y hy =>
              cases Nat.le_total (size y) (size x) with
              | inl hy_le_x =>
                  exact Exists.intro x
                    (And.intro hx
                      (And.intro List.mem_cons_self
                        (by
                          intro Z hAdmZ hmemZ
                          cases (List.mem_cons.mp hmemZ) with
                          | inl hz_eq =>
                              simp [hz_eq]
                          | inr hz_tail =>
                              exact Nat.le_trans (hy.right.right Z hAdmZ hz_tail) hy_le_x)))
              | inr hx_le_y =>
                  exact Exists.intro y
                    (And.intro hy.left
                      (And.intro (List.mem_cons_of_mem x hy.right.left)
                        (by
                          intro Z hAdmZ hmemZ
                          cases (List.mem_cons.mp hmemZ) with
                          | inl hz_eq =>
                              rw [hz_eq]
                              exact hx_le_y
                          | inr hz_tail =>
                              exact hy.right.right Z hAdmZ hz_tail)))
        case neg =>
          exact Exists.intro x
            (And.intro hx
              (And.intro List.mem_cons_self
                (by
                  intro Z hAdmZ hmemZ
                  cases (List.mem_cons.mp hmemZ) with
                  | inl hz_eq =>
                      simp [hz_eq]
                  | inr hz_tail =>
                      exact False.elim (htail (Exists.intro Z (And.intro hAdmZ hz_tail))))))
      case neg =>
        have htail : exists Y : Fam, Adm Y /\ List.Mem Y xs := by
          cases h with
          | intro Y hY =>
              cases (List.mem_cons.mp hY.right) with
              | inl hy_eq =>
                  rw [hy_eq] at hY
                  exact False.elim (hx hY.left)
              | inr hy_tail =>
                  exact Exists.intro Y (And.intro hY.left hy_tail)
        cases ih htail with
        | intro y hy =>
            exact Exists.intro y
              (And.intro hy.left
                (And.intro (List.mem_cons_of_mem x hy.right.left)
                  (by
                    intro Z hAdmZ hmemZ
                    cases (List.mem_cons.mp hmemZ) with
                    | inl hz_eq =>
                        rw [hz_eq] at hAdmZ
                        exact False.elim (hx hAdmZ)
                    | inr hz_tail =>
                        exact hy.right.right Z hAdmZ hz_tail)))

/-- A maximum-size admissible family is subset-maximal when admissible
extensions cannot have smaller or equal size unless they are reverse-included.

For ordinary finite subsets, `le` is subset inclusion and `size` is cardinality;
the final assumption is the usual finite-cardinality antisymmetry obligation. -/
theorem subsetMaximal_of_maxSized
    {Fam : Type u}
    {Adm : Fam -> Prop}
    {le : Fam -> Fam -> Prop}
    {size : Fam -> Nat}
    {Y : Fam}
    (hmax : forall Z : Fam, Adm Z -> size Z <= size Y)
    (hY : Adm Y)
    (hfinite_antisym :
      forall Z : Fam, Adm Y -> Adm Z -> le Y Z -> size Z <= size Y -> le Z Y) :
    SubsetMaximal Adm le Y := by
  exact And.intro hY
    (by
      intro Z hAdmZ hleYZ
      exact hfinite_antisym Z hY hAdmZ hleYZ (hmax Z hAdmZ))

/-- Finite maximal completion existence from an explicit finite enumeration of
admissible family candidates.

`enum_complete` is the finite-search obligation: every admissible family appears
in `enum`. `hfinite_antisym` is the finite-subset obligation: an admissible
extension with no larger size is reverse-included. -/
theorem exists_subsetMaximal_of_finite_enumeration
    {Fam : Type u}
    (Adm : Fam -> Prop)
    (le : Fam -> Fam -> Prop)
    (size : Fam -> Nat)
    (enum : List Fam)
    (enum_complete : forall Y : Fam, Adm Y -> List.Mem Y enum)
    (h : exists Y : Fam, Adm Y)
    (hfinite_antisym :
      forall Y Z : Fam, Adm Y -> Adm Z -> le Y Z -> size Z <= size Y -> le Z Y) :
    exists Y : Fam, SubsetMaximal Adm le Y := by
  have hlisted : exists Y : Fam, Adm Y /\ List.Mem Y enum := by
    cases h with
    | intro Y hY =>
        exact Exists.intro Y (And.intro hY (enum_complete Y hY))
  cases exists_maxSizedInList Adm size enum hlisted with
  | intro Y hmax =>
      exact Exists.intro Y
        (subsetMaximal_of_maxSized
          (Adm := Adm) (le := le) (size := size) (Y := Y)
          (by
            intro Z hAdmZ
            exact hmax.right.right Z hAdmZ (enum_complete Z hAdmZ))
          hmax.left
        (hfinite_antisym Y))

/-- Finite maximal completion existence for `Finset` candidate families.

If `a` is finite and at least one candidate family is admissible, then at least
one subset-maximal admissible family exists. The theorem is abstract in `Adm`;
it does not define compatibility, valuerhood, ethics, or empirical semantics. -/
theorem exists_subsetMaximal_finset
    {a : Type u}
    [Fintype a]
    [DecidableEq a]
    (Adm : Finset a -> Prop)
    (h : exists Y : Finset a, Adm Y) :
    exists Y : Finset a, SubsetMaximalFinset Adm Y := by
  exact exists_subsetMaximal_of_finite_enumeration
    Adm
    (fun A B : Finset a => A <= B)
    (fun A : Finset a => A.card)
    ((Finset.univ : Finset (Finset a)).toList)
    (by
      intro Y _hY
      exact Finset.mem_toList.mpr (Finset.mem_univ Y))
    h
    (by
      intro Y Z _hY _hZ hYZ hcard
      have hEq : Y = Z := Finset.eq_of_subset_of_card_le hYZ hcard
      rw [hEq])

end Completion

end OmegaCore
