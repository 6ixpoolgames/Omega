import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.BaselineWitnesses.NonFactorization

/-!
OmegaProper.BaselineWitnesses.MarginalCouplingNonFactorization

Finite witness that local marginals do not determine joint coupling.

Two binary joint tables can have the same row and column marginals while one
factorizes and the other does not. This is a small standard-math bridge toward
boundary/coupling discipline: local summaries need not determine joint
structure.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace MarginalCouplingNonFactorization

open NonFactorization

/-- Two binary joint tables used by the witness. -/
inductive JointTable where
  | productUniform
  | diagonalCoupled
  deriving DecidableEq

/--
Integer weight of a binary joint table.

`productUniform`:

```text
1 1
1 1
```

`diagonalCoupled`:

```text
2 0
0 2
```
-/
def jointWeight : JointTable -> Bit -> Bit -> Nat
  | JointTable.productUniform, _, _ => 1
  | JointTable.diagonalCoupled, Bit.zero, Bit.zero => 2
  | JointTable.diagonalCoupled, Bit.zero, Bit.one => 0
  | JointTable.diagonalCoupled, Bit.one, Bit.zero => 0
  | JointTable.diagonalCoupled, Bit.one, Bit.one => 2

def rowWeight (table : JointTable) (a : Bit) : Nat :=
  jointWeight table a Bit.zero + jointWeight table a Bit.one

def colWeight (table : JointTable) (e : Bit) : Nat :=
  jointWeight table Bit.zero e + jointWeight table Bit.one e

def totalWeight (table : JointTable) : Nat :=
  rowWeight table Bit.zero + rowWeight table Bit.one

/--
Local marginal summary: row counts, column counts, and total mass.
-/
structure MarginalSummary where
  rowCounts : List Nat
  colCounts : List Nat
  total : Nat
  deriving DecidableEq

def balancedMarginalSummary : MarginalSummary where
  rowCounts := [2, 2]
  colCounts := [2, 2]
  total := 4

def marginalSummary (table : JointTable) : MarginalSummary where
  rowCounts := [rowWeight table Bit.zero, rowWeight table Bit.one]
  colCounts := [colWeight table Bit.zero, colWeight table Bit.one]
  total := totalWeight table

/--
Integer cross-multiplication check for product factorization:

```text
weight(a,e) * total = row(a) * col(e)
```

This avoids fractions.
-/
def productEquationHolds (table : JointTable) (a e : Bit) : Bool :=
  decide (
    jointWeight table a e * totalWeight table =
      rowWeight table a * colWeight table e
  )

def jointFactorizes (table : JointTable) : Bool :=
  productEquationHolds table Bit.zero Bit.zero &&
    productEquationHolds table Bit.zero Bit.one &&
    productEquationHolds table Bit.one Bit.zero &&
    productEquationHolds table Bit.one Bit.one

theorem productUniform_marginalSummary :
    marginalSummary JointTable.productUniform = balancedMarginalSummary := by
  native_decide

theorem diagonalCoupled_marginalSummary :
    marginalSummary JointTable.diagonalCoupled = balancedMarginalSummary := by
  native_decide

theorem same_marginalSummary :
    marginalSummary JointTable.productUniform =
      marginalSummary JointTable.diagonalCoupled := by
  rw [productUniform_marginalSummary, diagonalCoupled_marginalSummary]

theorem productUniform_factorizes :
    jointFactorizes JointTable.productUniform = true := by
  native_decide

theorem diagonalCoupled_not_factorizes :
    jointFactorizes JointTable.diagonalCoupled = false := by
  native_decide

theorem different_jointFactorizationTarget :
    Not (
      jointFactorizes JointTable.productUniform =
        jointFactorizes JointTable.diagonalCoupled
    ) := by
  native_decide

/--
Same local marginals, different joint factorization target: local marginal
summary does not determine joint coupling.
-/
theorem marginalSummary_jointFactorization_nonFactorization :
    NonFactorization marginalSummary jointFactorizes := by
  exact nonFactorization_of_same_summary_different_target
    same_marginalSummary
    different_jointFactorizationTarget

end MarginalCouplingNonFactorization
end BaselineWitnesses
end OmegaProper
