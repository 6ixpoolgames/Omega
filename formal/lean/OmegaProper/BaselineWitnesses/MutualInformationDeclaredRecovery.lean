import OmegaProper.BaselineWitnesses.FiniteBits

/-!
OmegaProper.BaselineWitnesses.MutualInformationDeclaredRecovery

Lean conversion of the finite witness:
`same_mutual_information_different_declared_recovery`.

This module does not formalize Shannon information. It proves the exact finite
shape used by the Python witness: two deterministic balanced one-bit channels
over the same four-point carrier, one carrying the declared first coordinate
and one carrying the nuisance second coordinate.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace MutualInformationDeclaredRecovery

/-- A deterministic binary-output channel over the four-point carrier. -/
abbrev BinaryChannel := X2 -> Bit

def transmitFirst : BinaryChannel := firstBit

def transmitSecond : BinaryChannel := secondBit

/--
Finite baseline shape for a deterministic balanced one-bit channel.

The two alternatives correspond to grouping the four carrier points by one of
the two binary coordinates. This is the exact finite shape behind the retained
mutual-information witness, without importing numeric information theory.
-/
def BalancedOneBitBaseline (f : BinaryChannel) : Prop :=
  (f X2.x00 = f X2.x01 /\
    f X2.x10 = f X2.x11 /\
    Not (f X2.x00 = f X2.x10) /\
    Not (f X2.x01 = f X2.x11)) \/
  (f X2.x00 = f X2.x10 /\
    f X2.x01 = f X2.x11 /\
    Not (f X2.x00 = f X2.x01) /\
    Not (f X2.x10 = f X2.x11))

/-- The output recovers the declared first coordinate when equal outputs imply equal first bits. -/
def RecoversDeclaredFirst (f : BinaryChannel) : Prop :=
  forall x y, f x = f y -> firstBit x = firstBit y

theorem transmitFirst_balancedOneBitBaseline :
    BalancedOneBitBaseline transmitFirst := by
  exact Or.inl
    (And.intro rfl
      (And.intro rfl
        (And.intro
          (by intro h; cases h)
          (by intro h; cases h))))

theorem transmitSecond_balancedOneBitBaseline :
    BalancedOneBitBaseline transmitSecond := by
  exact Or.inr
    (And.intro rfl
      (And.intro rfl
        (And.intro
          (by intro h; cases h)
          (by intro h; cases h))))

theorem transmitFirst_recoversDeclaredFirst :
    RecoversDeclaredFirst transmitFirst := by
  intro x y h
  exact h

theorem transmitSecond_not_recoversDeclaredFirst :
    Not (RecoversDeclaredFirst transmitSecond) := by
  intro hRecovers
  have hSameOutput : transmitSecond X2.x00 = transmitSecond X2.x10 := rfl
  have hSameFirst := hRecovers X2.x00 X2.x10 hSameOutput
  cases hSameFirst

theorem same_mutual_information_baseline_different_declared_recovery :
    BalancedOneBitBaseline transmitFirst /\
    BalancedOneBitBaseline transmitSecond /\
    RecoversDeclaredFirst transmitFirst /\
    Not (RecoversDeclaredFirst transmitSecond) := by
  exact And.intro transmitFirst_balancedOneBitBaseline
    (And.intro transmitSecond_balancedOneBitBaseline
      (And.intro transmitFirst_recoversDeclaredFirst
        transmitSecond_not_recoversDeclaredFirst))

end MutualInformationDeclaredRecovery
end BaselineWitnesses
end OmegaProper

