import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.BaselineWitnesses.NonFactorization

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

open NonFactorization

/-- A deterministic binary-output channel over the four-point carrier. -/
abbrev BinaryChannel := X2 -> Bit

def transmitFirst : BinaryChannel := firstBit

def transmitSecond : BinaryChannel := secondBit

/-! ## Computed summary/target form -/

/-- Which deterministic binary channel is being summarized. -/
inductive ChannelExposure where
  | transmitFirst
  | transmitSecond
  deriving DecidableEq

def channelOfExposure : ChannelExposure -> BinaryChannel
  | ChannelExposure.transmitFirst => transmitFirst
  | ChannelExposure.transmitSecond => transmitSecond

def outputOfExposure (e : ChannelExposure) (x : X2) : Bit :=
  channelOfExposure e x

def outputIsZero (e : ChannelExposure) (x : X2) : Bool :=
  decide (outputOfExposure e x = Bit.zero)

def outputIsOne (e : ChannelExposure) (x : X2) : Bool :=
  decide (outputOfExposure e x = Bit.one)

def outputZeroCount (e : ChannelExposure) : Nat :=
  (x2States.filter (outputIsZero e)).length

def outputOneCount (e : ChannelExposure) : Nat :=
  (x2States.filter (outputIsOne e)).length

def sameOutputPair (e : ChannelExposure) (p : Prod X2 X2) : Bool :=
  decide (outputOfExposure e p.1 = outputOfExposure e p.2)

def sameOutputOrderedPairCount (e : ChannelExposure) : Nat :=
  (x2OrderedPairs.filter (sameOutputPair e)).length

def differentOutputOrderedPairCount (e : ChannelExposure) : Nat :=
  (x2OrderedPairs.filter (fun p => !(sameOutputPair e p))).length

/--
Computed finite proxy for the balanced one-bit information baseline. It counts
the output fiber sizes and the induced same/different-output ordered pairs.
-/
structure BinaryChannelCountSummary where
  sourceCount : Nat
  outputCount : Nat
  zeroOutputCount : Nat
  oneOutputCount : Nat
  sameOutputOrderedPairs : Nat
  differentOutputOrderedPairs : Nat
  deriving DecidableEq

def balancedBinaryChannelCountSummary : BinaryChannelCountSummary where
  sourceCount := 4
  outputCount := 2
  zeroOutputCount := 2
  oneOutputCount := 2
  sameOutputOrderedPairs := 8
  differentOutputOrderedPairs := 8

def binaryChannelSummaryOfExposure
    (e : ChannelExposure) : BinaryChannelCountSummary where
  sourceCount := x2States.length
  outputCount := bitOutcomes.length
  zeroOutputCount := outputZeroCount e
  oneOutputCount := outputOneCount e
  sameOutputOrderedPairs := sameOutputOrderedPairCount e
  differentOutputOrderedPairs := differentOutputOrderedPairCount e

def declaredRecoveryViolationCount (e : ChannelExposure) : Nat :=
  (x2OrderedPairs.filter (fun p =>
    sameOutputPair e p &&
      decide (Not (firstBit p.1 = firstBit p.2)))).length

def declaredRecoveryTargetOfExposure (e : ChannelExposure) : Bool :=
  decide (declaredRecoveryViolationCount e = 0)

theorem binaryChannelSummary_transmitFirst :
    binaryChannelSummaryOfExposure ChannelExposure.transmitFirst =
      balancedBinaryChannelCountSummary := by
  native_decide

theorem binaryChannelSummary_transmitSecond :
    binaryChannelSummaryOfExposure ChannelExposure.transmitSecond =
      balancedBinaryChannelCountSummary := by
  native_decide

theorem same_binaryChannel_computed_summary :
    binaryChannelSummaryOfExposure ChannelExposure.transmitFirst =
      binaryChannelSummaryOfExposure ChannelExposure.transmitSecond := by
  rw [binaryChannelSummary_transmitFirst, binaryChannelSummary_transmitSecond]

theorem transmitFirst_declaredRecoveryTarget :
    declaredRecoveryTargetOfExposure ChannelExposure.transmitFirst = true := by
  native_decide

theorem transmitSecond_declaredRecoveryTarget :
    declaredRecoveryTargetOfExposure ChannelExposure.transmitSecond = false := by
  native_decide

theorem different_binaryChannel_declaredRecoveryTarget :
    Not (
      declaredRecoveryTargetOfExposure ChannelExposure.transmitFirst =
        declaredRecoveryTargetOfExposure ChannelExposure.transmitSecond
    ) := by
  native_decide

theorem mutualInformationProxy_computedSummary_nonFactorization :
    NonFactorization
      binaryChannelSummaryOfExposure
      declaredRecoveryTargetOfExposure := by
  exact nonFactorization_of_same_summary_different_target
    same_binaryChannel_computed_summary
    different_binaryChannel_declaredRecoveryTarget

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
