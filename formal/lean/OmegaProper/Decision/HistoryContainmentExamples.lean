import OmegaProper.Decision.HistoryContainment
import OmegaProper.Decision.AmbiguityFamilyExamples
import OmegaProper.Decision.ContainmentExamples

/-!
OmegaProper.Decision.HistoryContainmentExamples

History-policy memorylessness examples over the W1 ambiguity-family witness.
-/

namespace OmegaProper
namespace Decision
namespace HistoryContainmentExamples

open AmbiguityFamilyExamples
open HistoryContainment
open Containment

instance : Inhabited Action :=
  ⟨Action.a⟩

theorem ok_has_history_guarantee :
    exists sigma : HistoryPolicy State Action,
      HistoryGuarantees F Allowed Requirement sigma [] State.ok := by
  exact (exists_historyGuarantees_iff_stationaryGuarantees
    F Allowed Requirement State.ok).mpr
      ContainmentExamples.ok_has_stationary_guarantee

theorem start_has_no_history_guarantee :
    Not
      (exists sigma : HistoryPolicy State Action,
        HistoryGuarantees F Allowed Requirement sigma [] State.start) := by
  intro h
  exact AmbiguityFamilyExamples.start_not_shared_rvk
    ((exists_historyGuarantees_iff_rvk F Allowed Requirement State.start).mp h)

theorem history_and_stationary_agree_at_start :
    (exists sigma : HistoryPolicy State Action,
      HistoryGuarantees F Allowed Requirement sigma [] State.start) <->
    (exists policy : StationaryPolicy State Action,
      StationaryGuarantees F Allowed Requirement policy State.start) :=
  exists_historyGuarantees_iff_stationaryGuarantees
    F Allowed Requirement State.start

end HistoryContainmentExamples
end Decision
end OmegaProper
