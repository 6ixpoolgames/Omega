import OmegaProper.Decision.TrajectoryBridge
import OmegaProper.Decision.ContainmentExamples

/-!
OmegaProper.Decision.TrajectoryBridgeExamples

W1-based examples for the positive stationary trajectory bridge.
-/

namespace OmegaProper
namespace Decision
namespace TrajectoryBridgeExamples

open AmbiguityFamilyExamples
open Containment
open ContainmentExamples
open TrajectoryBridge

instance : Inhabited Action :=
  ⟨Action.a⟩

theorem ok_has_model_trace
    (i : Model) :
    exists tr : InfinitePolicyTrace F
        (rvkPolicy F Allowed Requirement) i State.ok,
      TraceInPolicyKernel F Allowed Requirement
        (rvkPolicy F Allowed Requirement) tr.state /\
      TraceInConstraint F tr.state /\
      TraceInRequirement Requirement tr.state /\
      TraceInRVK F Allowed Requirement tr.state :=
  rvk_has_model_trace F Allowed Requirement ok_in_shared_rvk i

theorem ok_model_trace_stays_shared_rvk
    (i : Model) :
    exists tr : InfinitePolicyTrace F
        (rvkPolicy F Allowed Requirement) i State.ok,
      TraceInRVK F Allowed Requirement tr.state := by
  rcases ok_has_model_trace i with
    ⟨tr, _hKernel, _hConstraint, _hRequirement, hRVK⟩
  exact ⟨tr, hRVK⟩

end TrajectoryBridgeExamples
end Decision
end OmegaProper
