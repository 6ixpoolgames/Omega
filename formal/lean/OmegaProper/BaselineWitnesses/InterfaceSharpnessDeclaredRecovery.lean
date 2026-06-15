import OmegaProper.BaselineWitnesses.FiniteBits
import OmegaProper.BaselineWitnesses.InvarianceNonFactorization
import OmegaProper.BaselineWitnesses.NonFactorization

/-!
OmegaProper.BaselineWitnesses.InterfaceSharpnessDeclaredRecovery

Finite witness for the holographic/interface discipline:

same sharp two-output interface profile,
different declared input-distinction recovery.

The module intentionally does not define a deformer, singularity, agent,
identity, value, alignment, or Omega proper. It only proves that a coarse
"structured output" summary need not determine which declared input distinction
survived the interface.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace InterfaceSharpnessDeclaredRecovery

open NonFactorization
open InvarianceNonFactorization

/-- A deterministic binary interface from four diffuse inputs to two outputs. -/
abbrev InterfaceChannel := X2 -> Bit

def emitDeclaredFirst : InterfaceChannel := firstBit

def emitNuisanceSecond : InterfaceChannel := secondBit

/-- Which interface channel is being summarized. -/
inductive InterfaceExposure where
  | emitFirst
  | emitSecond
  deriving DecidableEq

def swapInterfaceExposure : InterfaceExposure -> InterfaceExposure
  | InterfaceExposure.emitFirst => InterfaceExposure.emitSecond
  | InterfaceExposure.emitSecond => InterfaceExposure.emitFirst

def channelOfExposure : InterfaceExposure -> InterfaceChannel
  | InterfaceExposure.emitFirst => emitDeclaredFirst
  | InterfaceExposure.emitSecond => emitNuisanceSecond

def outputOfExposure (e : InterfaceExposure) (x : X2) : Bit :=
  channelOfExposure e x

def outputIsZero (e : InterfaceExposure) (x : X2) : Bool :=
  decide (outputOfExposure e x = Bit.zero)

def outputIsOne (e : InterfaceExposure) (x : X2) : Bool :=
  decide (outputOfExposure e x = Bit.one)

def zeroFiberCount (e : InterfaceExposure) : Nat :=
  (x2States.filter (outputIsZero e)).length

def oneFiberCount (e : InterfaceExposure) : Nat :=
  (x2States.filter (outputIsOne e)).length

/--
Coarse interface sharpness profile.

This summary sees that the interface turns four inputs into two balanced output
fibers. It does not record which input distinction the output preserves.
-/
structure SharpInterfaceSummary where
  inputCount : Nat
  outputCount : Nat
  zeroFiber : Nat
  oneFiber : Nat
  deriving DecidableEq

def balancedSharpInterfaceSummary : SharpInterfaceSummary where
  inputCount := 4
  outputCount := 2
  zeroFiber := 2
  oneFiber := 2

def sharpInterfaceSummaryOfExposure
    (e : InterfaceExposure) : SharpInterfaceSummary where
  inputCount := x2States.length
  outputCount := bitOutcomes.length
  zeroFiber := zeroFiberCount e
  oneFiber := oneFiberCount e

def sameOutputPair (e : InterfaceExposure) (p : Prod X2 X2) : Bool :=
  decide (outputOfExposure e p.1 = outputOfExposure e p.2)

def declaredRecoveryViolationCount (e : InterfaceExposure) : Nat :=
  (x2OrderedPairs.filter (fun p =>
    sameOutputPair e p &&
      decide (Not (firstBit p.1 = firstBit p.2)))).length

/--
The target asks whether the interface output recovers the declared first input
coordinate.
-/
def declaredInputRecoveryTarget (e : InterfaceExposure) : Bool :=
  decide (declaredRecoveryViolationCount e = 0)

theorem sharpInterfaceSummary_emitFirst :
    sharpInterfaceSummaryOfExposure InterfaceExposure.emitFirst =
      balancedSharpInterfaceSummary := by
  native_decide

theorem sharpInterfaceSummary_emitSecond :
    sharpInterfaceSummaryOfExposure InterfaceExposure.emitSecond =
      balancedSharpInterfaceSummary := by
  native_decide

theorem same_sharpInterface_computed_summary :
    sharpInterfaceSummaryOfExposure InterfaceExposure.emitFirst =
      sharpInterfaceSummaryOfExposure InterfaceExposure.emitSecond := by
  rw [sharpInterfaceSummary_emitFirst, sharpInterfaceSummary_emitSecond]

theorem emitFirst_declaredInputRecoveryTarget :
    declaredInputRecoveryTarget InterfaceExposure.emitFirst = true := by
  native_decide

theorem emitSecond_declaredInputRecoveryTarget :
    declaredInputRecoveryTarget InterfaceExposure.emitSecond = false := by
  native_decide

theorem different_declaredInputRecoveryTarget :
    Not (
      declaredInputRecoveryTarget InterfaceExposure.emitFirst =
        declaredInputRecoveryTarget InterfaceExposure.emitSecond
    ) := by
  native_decide

theorem sharpInterfaceSummary_invariantUnder_swap :
    SummaryInvariantUnder
      sharpInterfaceSummaryOfExposure
      swapInterfaceExposure := by
  intro e
  cases e
  case emitFirst =>
    exact Eq.symm same_sharpInterface_computed_summary
  case emitSecond =>
    exact same_sharpInterface_computed_summary

theorem declaredInputRecovery_changesUnder_swap :
    TargetChangesUnder
      declaredInputRecoveryTarget
      swapInterfaceExposure := by
  exact Exists.intro InterfaceExposure.emitFirst (by native_decide)

/--
A sharp two-output interface profile does not determine declared input recovery.
-/
theorem sharpInterfaceSummary_declaredRecovery_nonFactorization :
    NonFactorization
      sharpInterfaceSummaryOfExposure
      declaredInputRecoveryTarget := by
  exact invariant_summary_target_change_nonFactorization
    sharpInterfaceSummary_invariantUnder_swap
    declaredInputRecovery_changesUnder_swap

/--
Expanded witness statement: both interfaces have the same computed sharpness
summary, but only the first recovers the declared input distinction.
-/
theorem same_sharp_interface_different_declared_recovery :
    sharpInterfaceSummaryOfExposure InterfaceExposure.emitFirst =
      sharpInterfaceSummaryOfExposure InterfaceExposure.emitSecond /\
    declaredInputRecoveryTarget InterfaceExposure.emitFirst = true /\
    declaredInputRecoveryTarget InterfaceExposure.emitSecond = false /\
    NonFactorization
      sharpInterfaceSummaryOfExposure
      declaredInputRecoveryTarget := by
  exact And.intro same_sharpInterface_computed_summary
    (And.intro emitFirst_declaredInputRecoveryTarget
      (And.intro emitSecond_declaredInputRecoveryTarget
        sharpInterfaceSummary_declaredRecovery_nonFactorization))

end InterfaceSharpnessDeclaredRecovery
end BaselineWitnesses
end OmegaProper
