import OmegaProper.Decision.TrajectoryConverse
import OmegaProper.Decision.ContainmentExamples

/-!
OmegaProper.Decision.TrajectoryConverseExamples

W1-based examples for switching finite bad-prefix trajectory semantics.
-/

namespace OmegaProper
namespace Decision
namespace TrajectoryConverseExamples

open AmbiguityFamilyExamples
open Containment
open ContainmentExamples
open TrajectoryConverse

instance : Inhabited Action :=
  ⟨Action.a⟩

theorem ok_has_switching_trajectory_guarantee :
    SwitchingTrajectoryGuarantees F Allowed Requirement
      (rvkPolicy F Allowed Requirement) State.ok := by
  exact (stationaryGuarantee_iff_switchingTrajectoryGuarantees
    F Allowed Requirement (rvkPolicy F Allowed Requirement) State.ok).mp
      ((rvkPolicy_guarantees_all_rvk F Allowed Requirement)
        State.ok ok_in_shared_rvk)

theorem start_has_no_switching_trajectory_guarantee
    (policy : StationaryPolicy State Action) :
    Not
      (SwitchingTrajectoryGuarantees F Allowed Requirement policy
        State.start) := by
  intro h
  exact start_not_shared_rvk
    (switchingTrajectoryGuarantee_implies_rvk
      F Allowed Requirement policy State.start h)

theorem switching_guarantee_equiv_stationary_at_ok :
    StationaryGuarantees F Allowed Requirement
      (rvkPolicy F Allowed Requirement) State.ok <->
    SwitchingTrajectoryGuarantees F Allowed Requirement
      (rvkPolicy F Allowed Requirement) State.ok :=
  stationaryGuarantee_iff_switchingTrajectoryGuarantees
    F Allowed Requirement (rvkPolicy F Allowed Requirement) State.ok

end TrajectoryConverseExamples
end Decision
end OmegaProper
