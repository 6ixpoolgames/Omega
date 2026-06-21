import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Rat.Lemmas
import Mathlib.Tactic.Linarith

/-!
OmegaProper.Recovery.FiniteChannel

Exact rational finite channels and source-indexed recovery profiles.

This file supplies the finite probability object used by the recovery layer.
It does not define value, agency, identity, or Omega structure.
-/

namespace OmegaProper
namespace Recovery

universe u v w z

/--
An exact rational channel from source states `X` to finite outputs `Y`.

The source type is not required to be finite. Finiteness is required only for
the output rows, because each row is summed over `Y`.
-/
structure RatChannel (X : Type u) (Y : Type v) [Fintype Y] where
  prob : X -> Y -> ℚ
  nonneg : forall x y, 0 <= prob x y
  row_sum_one : forall x, (Finset.univ.sum fun y => prob x y) = 1

/-- Positive-probability support of a rational channel. -/
def PositiveSupport {X : Type u} {Y : Type v} [Fintype Y]
    (C : RatChannel X Y) (x : X) (y : Y) : Prop :=
  0 < C.prob x y

/--
Per-source deterministic decoding success.

For a source `x`, this sums the channel mass of outputs whose observed value is
decoded to the declared target value of `x`.
-/
def Success {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) : ℚ :=
  Finset.univ.sum fun y =>
    if decoder (observe y) = target x then C.prob x y else 0

/--
Per-source failure mass for a deterministic decoder.

This is the complement of `Success` in the source row.
-/
def FailureMass {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) : ℚ :=
  Finset.univ.sum fun y =>
    if decoder (observe y) = target x then 0 else C.prob x y

theorem success_nonneg {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) :
    0 <= Success C target observe decoder x := by
  classical
  unfold Success
  exact Finset.sum_nonneg fun y _hy => by
    by_cases h : decoder (observe y) = target x
    · simp [h, C.nonneg x y]
    · simp [h]

theorem failureMass_nonneg {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) :
    0 <= FailureMass C target observe decoder x := by
  classical
  unfold FailureMass
  exact Finset.sum_nonneg fun y _hy => by
    by_cases h : decoder (observe y) = target x
    · simp [h]
    · simp [h, C.nonneg x y]

theorem success_add_failureMass {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) :
    Success C target observe decoder x +
      FailureMass C target observe decoder x = 1 := by
  classical
  unfold Success FailureMass
  rw [← Finset.sum_add_distrib]
  calc
    (Finset.univ.sum fun y =>
        (if decoder (observe y) = target x then C.prob x y else 0) +
          if decoder (observe y) = target x then 0 else C.prob x y)
        = Finset.univ.sum (fun y => C.prob x y) := by
          apply Finset.sum_congr rfl
          intro y _hy
          by_cases h : decoder (observe y) = target x
          · simp [h]
          · simp [h]
    _ = 1 := C.row_sum_one x

theorem success_le_one {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) :
    Success C target observe decoder x <= 1 := by
  have hsum := success_add_failureMass C target observe decoder x
  have hfail := failureMass_nonneg C target observe decoder x
  linarith

theorem success_eq_one_iff_failureMass_eq_zero
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [DecidableEq D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (decoder : O -> D)
    (x : X) :
    Success C target observe decoder x = 1 <->
      FailureMass C target observe decoder x = 0 := by
  constructor
  · intro hsuccess
    have hsum := success_add_failureMass C target observe decoder x
    linarith
  · intro hfailure
    have hsum := success_add_failureMass C target observe decoder x
    linarith

end Recovery
end OmegaProper
