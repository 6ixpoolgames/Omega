import OmegaAdapters.ProbabilisticChannelNative

/-!
OmegaAdapters.ProbabilisticNonErasureNative

Finite thresholded probabilistic non-erasure over an externally supplied
recovery predicate.

This module intentionally does not define recovery by searching for a decoder.
The predicate `RecoveredAtThreshold` is supplied by a presentation, registry, or
measurement layer. The theorem surface only proves requirement-set structure.
-/

namespace OmegaAdapters
namespace ProbabilisticChannelNative

universe u v w z

/-- Requirement-set inclusion over distinction tokens. -/
def RequirementSubset {Dist : Type u}
    (Small Large : Dist -> Prop) : Prop :=
  forall d, Small d -> Large d

/-- Thresholded probabilistic non-erasure for a declared finite requirement set.

`RecoveredAtThreshold` is external evidence. It may come from a declared
registry, a fixed-policy measurement, or another explicitly classified source.
This definition does not manufacture recovery evidence. -/
def ProbNonErasing {Dist : Type u}
    (Req : Dist -> Prop)
    (RecoveredAtThreshold : Dist -> Prop) : Prop :=
  forall d, Req d -> RecoveredAtThreshold d

/-- Exact-support non-erasure, kept separate from thresholded probabilistic
non-erasure. -/
def ExactSupportNonErasing {Dist : Type u}
    (Req : Dist -> Prop)
    (ExactRecovered : Dist -> Prop) : Prop :=
  forall d, Req d -> ExactRecovered d

/-- Monotonicity under requirement-set weakening.

If a larger requirement set is probabilistically non-erased, every declared
subset requirement set is also probabilistically non-erased. -/
theorem probNonErasing_mono_requirement
    {Dist : Type u}
    {Small Large : Dist -> Prop}
    {RecoveredAtThreshold : Dist -> Prop}
    (hSubset : RequirementSubset Small Large)
    (hLarge : ProbNonErasing Large RecoveredAtThreshold) :
    ProbNonErasing Small RecoveredAtThreshold := by
  intro d hSmall
  exact hLarge d (hSubset d hSmall)

/-- Exact-support non-erasure transfers into thresholded non-erasure only when
an explicit bridge from exact recovery to thresholded recovery is supplied. -/
theorem exactSupport_nonErasing_transfers_to_prob
    {Dist : Type u}
    {Req : Dist -> Prop}
    {ExactRecovered RecoveredAtThreshold : Dist -> Prop}
    (hBridge : forall d, ExactRecovered d -> RecoveredAtThreshold d)
    (hExact : ExactSupportNonErasing Req ExactRecovered) :
    ProbNonErasing Req RecoveredAtThreshold := by
  intro d hReq
  exact hBridge d (hExact d hReq)

/-- Thresholded recovery by one declared decoder and target observation. -/
def ThresholdedDecoderRecovers
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec : LE -> LD)
    (num den : Nat) : Prop :=
  ThresholdValid num den /\ ProbRecoversAtLeast K pi D E dec num den

/-- Exact support recovery gives thresholded decoder recovery at the full
success threshold. -/
theorem exactSupport_implies_thresholdedDecoderRecovers_100
    {X : Type u} {Y : Type v} {LD : Type w} {LE : Type z}
    [Fintype X] [Fintype Y] [DecidableEq LD]
    {K : X -> Y -> Nat}
    {pi : X -> Nat}
    {D : X -> LD}
    {E : Y -> LE}
    {dec : LE -> LD}
    (h : ExactSupportRecovers K D E dec) :
    ThresholdedDecoderRecovers K pi D E dec 100 100 := by
  constructor
  · exact And.intro (by decide) (by decide)
  · exact exactSupport_implies_probAtLeast_100 h

/-! ## Finite requirement-set separations -/

/-- Tiny distinction-token space for requirement-set examples. -/
inductive RequirementToken where
  | A
  | B
  | Joint
  deriving DecidableEq

instance : Fintype RequirementToken where
  elems := {RequirementToken.A, RequirementToken.B, RequirementToken.Joint}
  complete := by
    intro x
    cases x <;> simp

def reqMarginals : RequirementToken -> Prop
  | RequirementToken.A => True
  | RequirementToken.B => True
  | RequirementToken.Joint => False

def reqAllNontrivial (_ : RequirementToken) : Prop := True

def recoveredMarginalsOnly : RequirementToken -> Prop
  | RequirementToken.A => True
  | RequirementToken.B => True
  | RequirementToken.Joint => False

theorem reqMarginals_subset_all :
    RequirementSubset reqMarginals reqAllNontrivial := by
  intro d _h
  trivial

theorem marginals_probNonErasing :
    ProbNonErasing reqMarginals recoveredMarginalsOnly := by
  intro d hReq
  cases d <;> simp [reqMarginals, recoveredMarginalsOnly] at *

theorem all_not_probNonErasing :
    Not (ProbNonErasing reqAllNontrivial recoveredMarginalsOnly) := by
  intro h
  have hJoint := h RequirementToken.Joint (by trivial)
  simp [recoveredMarginalsOnly] at hJoint

/-- Recovering marginal requirements does not force recovering the larger
joint-inclusive requirement set. -/
theorem marginal_recovery_does_not_force_all_requirements :
    ProbNonErasing reqMarginals recoveredMarginalsOnly /\
      Not (ProbNonErasing reqAllNontrivial recoveredMarginalsOnly) := by
  exact And.intro marginals_probNonErasing all_not_probNonErasing

/-- Thresholded probabilistic non-erasure can hold while exact support recovery
fails. This reuses the finite high-probability/support-ambiguous channel from
`ProbabilisticChannelNative`. -/
theorem thresholded_nonErasing_not_exactSupport :
    ProbNonErasing
      (fun (_ : Unit) => True)
      (fun (_ : Unit) =>
        ThresholdedDecoderRecovers
          highButAmbiguousChannel uniformPriorBit bitObs bitObs boolId 95 100) /\
      Not (ExactSupportRecovers highButAmbiguousChannel bitObs bitObs boolId) := by
  refine And.intro ?_ highButAmbiguous_not_exactSupport
  intro _ _hReq
  constructor
  · exact And.intro (by decide) (by decide)
  · exact highButAmbiguous_atLeast95

end ProbabilisticChannelNative
end OmegaAdapters
