import OmegaProper.BaselineWitnesses.NonFactorization

/-!
OmegaProper.EffectiveLayers.Underdetermination

Small cross-layer witness for the effective-layer reorientation.

The point is not to define real agency. The point is to record the category
boundary: a shared Alpha-facing trace does not by itself determine a
higher-layer agency-realization profile. The witness is deliberately finite and
uses the existing non-factorization schema.
-/

namespace OmegaProper
namespace EffectiveLayers
namespace Underdetermination

open BaselineWitnesses.NonFactorization

/-- A two-point carrier for the finite trace witness. -/
inductive Point where
  | left
  | right
deriving DecidableEq

/-- A minimal Alpha-facing trace over a fixed carrier. -/
structure AlphaTrace where
  rel : Point -> Point -> Prop
  sep : Point -> Point -> Prop
  asym : Point -> Point -> Prop

/-- A simple nontrivial relation on the two-point carrier. -/
def primitiveRel (x y : Point) : Prop :=
  x != y

/-- A simple separation predicate on the two-point carrier. -/
def primitiveSep (x y : Point) : Prop :=
  x != y

/-- A directed asymmetry witness from `left` to `right`. -/
def primitiveAsym (x y : Point) : Prop :=
  x = Point.left /\ y = Point.right

/-- The shared Alpha trace used by both higher-layer realizations. -/
def sharedAlphaTrace : AlphaTrace where
  rel := primitiveRel
  sep := primitiveSep
  asym := primitiveAsym

/--
A toy higher-layer realization record.

The Alpha field is the lower trace. The remaining fields are deliberately
higher-layer realization fields: they are not reconstructed from `alpha`.
-/
structure Realization where
  alpha : AlphaTrace
  hasEndogenousAlternatives : Bool
  feedbackMaintainsSelector : Bool

/-- A passive realization over the shared Alpha trace. -/
def passiveRealization : Realization where
  alpha := sharedAlphaTrace
  hasEndogenousAlternatives := false
  feedbackMaintainsSelector := false

/-- A feedback-maintenance realization over the same shared Alpha trace. -/
def feedbackRealization : Realization where
  alpha := sharedAlphaTrace
  hasEndogenousAlternatives := true
  feedbackMaintainsSelector := true

/-- Forget a realization down to its Alpha-facing trace. -/
def forgetAlpha (R : Realization) : AlphaTrace :=
  R.alpha

/--
A toy agency-profile bit. This is not a full agency definition; it marks
whether the realization exposes both endogenous alternatives and feedback
maintenance of the selector.
-/
def agencyProfile (R : Realization) : Bool :=
  R.hasEndogenousAlternatives && R.feedbackMaintainsSelector

/-- The two toy realizations have the same Alpha trace. -/
theorem passive_feedback_same_alpha :
    forgetAlpha passiveRealization = forgetAlpha feedbackRealization := by
  rfl

/-- The two toy realizations have different higher-layer agency profiles. -/
theorem passive_feedback_different_agencyProfile :
    Not (agencyProfile passiveRealization = agencyProfile feedbackRealization) := by
  decide

/--
The Alpha trace does not determine the higher-layer agency profile: the same
forgotten Alpha trace supports two realizations with different agency-profile
values.
-/
theorem alphaTrace_does_not_determine_agencyProfile :
    NonFactorization forgetAlpha agencyProfile := by
  exact nonFactorization_of_same_summary_different_target
    passive_feedback_same_alpha
    passive_feedback_different_agencyProfile

/--
Equivalently, the toy agency profile does not factor through the Alpha trace.
-/
theorem alphaTrace_blocks_agencyProfile_factorization :
    Not (FactorsThrough forgetAlpha agencyProfile) := by
  exact nonFactorization_blocks_factorization
    alphaTrace_does_not_determine_agencyProfile

end Underdetermination
end EffectiveLayers
end OmegaProper
