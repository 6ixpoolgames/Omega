import Mathlib.Data.Int.Basic

/-!
OmegaProper.Trajectory.FiniteDeformerProfileStrictness

Finite profile-coordinate strictness witnesses extracted from the
operational-causal-diamond pilots.

This file intentionally uses a minimal profile-row interface. It does not
formalize a full controlled system, policy class, stochastic kernel, agency,
identity, value, valuerhood, moral standing, or Omega. Its only purpose is to
make the first strictness spine precise:

* persistence does not imply positive feedback advantage;
* control reach does not imply positive feedback advantage;
* positive feedback advantage does not imply positive reflexive maintenance;
* one own-maintenance scalar does not determine joint-continuation effect.
-/

namespace OmegaProper
namespace Trajectory
namespace FiniteDeformerProfileStrictness

/--
A retained finite profile row.

The numeric fields are deliberately uninterpreted integer scores. Their
semantics are supplied by an adapter or controlled-system realization. This
module only proves that the coordinates are not logically interchangeable.
-/
structure FiniteProfile where
  persistent : Prop
  controlReach : Prop
  feedbackAdvantage : Int
  reflexiveMaintenance : Int
  ownMaintenanceScore : Int
  jointEffect : Int

def PositiveFeedbackAdvantage (P : FiniteProfile) : Prop :=
  0 < P.feedbackAdvantage

def PositiveReflexiveMaintenance (P : FiniteProfile) : Prop :=
  0 < P.reflexiveMaintenance

def SameOwnMaintenance (P Q : FiniteProfile) : Prop :=
  P.ownMaintenanceScore = Q.ownMaintenanceScore

def DifferentJointEffect (P Q : FiniteProfile) : Prop :=
  Not (P.jointEffect = Q.jointEffect)

/-- Passive persistence row: persistent, but no feedback advantage. -/
def passivePersistentProfile : FiniteProfile where
  persistent := True
  controlReach := False
  feedbackAdvantage := 0
  reflexiveMaintenance := 0
  ownMaintenanceScore := 1
  jointEffect := 0

/-- Control reach row: action-distinct futures, but no feedback advantage. -/
def controlReachNoFeedbackProfile : FiniteProfile where
  persistent := True
  controlReach := True
  feedbackAdvantage := 0
  reflexiveMaintenance := 0
  ownMaintenanceScore := 1
  jointEffect := 0

/-- Feedback row: feedback advantage without reflexive channel maintenance. -/
def feedbackNoReflexiveProfile : FiniteProfile where
  persistent := True
  controlReach := True
  feedbackAdvantage := 1
  reflexiveMaintenance := 0
  ownMaintenanceScore := 1
  jointEffect := 0

/-- Same own-maintenance, positive joint-continuation effect. -/
def sameOwnPositiveJointProfile : FiniteProfile where
  persistent := True
  controlReach := True
  feedbackAdvantage := 1
  reflexiveMaintenance := 1
  ownMaintenanceScore := 1
  jointEffect := 1

/-- Same own-maintenance, negative joint-continuation effect. -/
def sameOwnNegativeJointProfile : FiniteProfile where
  persistent := True
  controlReach := True
  feedbackAdvantage := 1
  reflexiveMaintenance := 1
  ownMaintenanceScore := 1
  jointEffect := -1

theorem persistence_not_imply_positiveFeedbackAdvantage :
    exists P : FiniteProfile,
      P.persistent /\ Not (PositiveFeedbackAdvantage P) := by
  exact Exists.intro passivePersistentProfile
    (And.intro trivial (by
      simp [PositiveFeedbackAdvantage, passivePersistentProfile]))

theorem controlReach_not_imply_positiveFeedbackAdvantage :
    exists P : FiniteProfile,
      P.controlReach /\ Not (PositiveFeedbackAdvantage P) := by
  exact Exists.intro controlReachNoFeedbackProfile
    (And.intro trivial (by
      simp [PositiveFeedbackAdvantage, controlReachNoFeedbackProfile]))

theorem positiveFeedbackAdvantage_not_imply_positiveReflexiveMaintenance :
    exists P : FiniteProfile,
      PositiveFeedbackAdvantage P /\
        Not (PositiveReflexiveMaintenance P) := by
  exact Exists.intro feedbackNoReflexiveProfile
    (And.intro
      (by simp [PositiveFeedbackAdvantage, feedbackNoReflexiveProfile])
      (by simp [PositiveReflexiveMaintenance, feedbackNoReflexiveProfile]))

theorem ownMaintenanceScore_does_not_determine_jointEffect :
    exists P Q : FiniteProfile,
      SameOwnMaintenance P Q /\ DifferentJointEffect P Q := by
  exact Exists.intro sameOwnPositiveJointProfile
    (Exists.intro sameOwnNegativeJointProfile
      (And.intro
        (by
          simp [SameOwnMaintenance,
            sameOwnPositiveJointProfile,
            sameOwnNegativeJointProfile])
        (by
          simp [DifferentJointEffect,
            sameOwnPositiveJointProfile,
            sameOwnNegativeJointProfile])))

theorem sameOwnMaintenance_allows_positive_and_negative_jointEffect :
    SameOwnMaintenance
      sameOwnPositiveJointProfile
      sameOwnNegativeJointProfile /\
    sameOwnPositiveJointProfile.jointEffect = 1 /\
    sameOwnNegativeJointProfile.jointEffect = -1 := by
  exact And.intro
    (by
      simp [SameOwnMaintenance,
        sameOwnPositiveJointProfile,
        sameOwnNegativeJointProfile])
    (And.intro
      (by simp [sameOwnPositiveJointProfile])
      (by simp [sameOwnNegativeJointProfile]))

end FiniteDeformerProfileStrictness
end Trajectory
end OmegaProper
