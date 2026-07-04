import OmegaProper.Decision.Containment
import OmegaProper.Decision.AmbiguityFamilyExamples

/-!
OmegaProper.Decision.ContainmentExamples

Stationary containment examples reusing the W1 ambiguity-family witness.

The `ok` state has a stationary guarantee. The `start` state has no stationary
guarantee, even though it lies in each per-model corridor, because no shared
action is safe across both models.
-/

namespace OmegaProper
namespace Decision
namespace ContainmentExamples

open Trajectory.PredicateFixpoint
open AmbiguityFamily
open Containment
open AmbiguityFamilyExamples

instance : Inhabited Action :=
  ⟨Action.a⟩

private theorem ok_postfixed :
    Postfixed
      (robustCorridorOp (mergedDecision F)
        (familyEnabledAllowed F Allowed) Requirement)
      (fun x => x = State.ok) := by
  intro x hx
  cases hx
  exact ⟨trivial, trivial, Action.a,
    ⟨trivial,
      (by
        intro i
        exact ⟨State.ok, by cases i <;> simp [F, Step]⟩)⟩,
    ⟨State.ok, ⟨Model.m0, by simp [F, Step]⟩⟩,
    (by
      intro y hStep
      rcases hStep with ⟨i, hModelStep⟩
      cases y <;> simp [F, Step] at hModelStep
      rfl)⟩

theorem ok_in_shared_rvk :
    SharedRVK State.ok :=
  postfixed_le_gfp ok_postfixed State.ok rfl

theorem ok_has_stationary_guarantee :
    exists policy : StationaryPolicy State Action,
      StationaryGuarantees F Allowed Requirement policy State.ok := by
  exact (exists_stationaryGuarantees_iff_rvk F Allowed Requirement
    State.ok).mpr ok_in_shared_rvk

theorem start_has_no_stationary_guarantee :
    Not
      (exists policy : StationaryPolicy State Action,
        StationaryGuarantees F Allowed Requirement policy State.start) := by
  intro h
  exact start_not_shared_rvk
    ((exists_stationaryGuarantees_iff_rvk F Allowed Requirement
      State.start).mp h)

theorem guaranteed_reachable_states_are_shared_rvk
    {policy : StationaryPolicy State Action}
    {y : State}
    (hGuarantee :
      StationaryGuarantees F Allowed Requirement policy State.ok)
    (hReach : PolicyReach F policy State.ok y) :
    SharedRVK y :=
  stationaryGuarantee_reachable_confined F Allowed Requirement
    policy hGuarantee hReach

end ContainmentExamples
end Decision
end OmegaProper
