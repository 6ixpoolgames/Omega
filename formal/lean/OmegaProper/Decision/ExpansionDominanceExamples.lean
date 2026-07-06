import OmegaProper.Decision.ExpansionDominance

/-!
OmegaProper.Decision.ExpansionDominanceExamples

Small finite witnesses for declared expansion profile comparison.

The examples compare registered expansion profiles only. They do not rank
patients, moral worth, standing, value, rights, agency, identity, or Omega.
-/

namespace OmegaProper
namespace Decision
namespace ExpansionDominanceExamples

open ExpansionDominance

inductive DeclaredCapacity where
  | task
  | revision
deriving DecidableEq, Repr

instance : LE DeclaredCapacity where
  le x y := x = y

instance : Preorder DeclaredCapacity where
  le_refl := by
    intro x
    rfl
  le_trans := by
    intro x y z hxy hyz
    exact Eq.trans hxy hyz

instance : DecidableRel ((· <= ·) : DeclaredCapacity -> DeclaredCapacity -> Prop) := by
  intro x y
  change Decidable (x = y)
  infer_instance

/-- Baseline expansion: the task-success capacity is expanded. -/
def ExpandTask : ExpansionProfile DeclaredCapacity
  | DeclaredCapacity.task => True
  | DeclaredCapacity.revision => False

/--
Enriched expansion: the same task-success capacity is expanded, and declared
correction/revision capacity is expanded too.
-/
def ExpandTaskAndRevision : ExpansionProfile DeclaredCapacity
  | DeclaredCapacity.task => True
  | DeclaredCapacity.revision => True

private theorem revision_not_covered_by_task :
    Not (CoveredExpansion ExpandTask DeclaredCapacity.revision) := by
  intro h
  rcases h with ⟨g, hg, hrg⟩
  cases g <;> simp [ExpandTask] at hg
  cases hrg

theorem enrichedExpansion_dominates_taskExpansion :
    ExpansionDominates ExpandTaskAndRevision ExpandTask := by
  intro f hf
  rcases hf with ⟨g, hg, hfg⟩
  exact ⟨g, by cases g <;> simp [ExpandTaskAndRevision], hfg⟩

theorem taskExpansion_not_dominates_enrichedExpansion :
    Not (ExpansionDominates ExpandTask ExpandTaskAndRevision) := by
  rw [not_expansionDominates_iff_exists_failure_certificate]
  exact ⟨DeclaredCapacity.revision, by
    constructor
    · exact
        profile_mem_coveredExpansion
          (P := ExpandTaskAndRevision)
          (by simp [ExpandTaskAndRevision])
    · exact revision_not_covered_by_task⟩

theorem W_enrichment_strictness :
    ExpansionDominates ExpandTaskAndRevision ExpandTask /\
      Not (ExpansionDominates ExpandTask ExpandTaskAndRevision) :=
  ⟨enrichedExpansion_dominates_taskExpansion,
    taskExpansion_not_dominates_enrichedExpansion⟩

/--
The ODT1 acceptance bridge applies to declared expansion profiles: if the
enriched expansion dominates the task-only expansion, every monotone valuation
gives the corresponding pointwise cover.
-/
theorem enrichedExpansion_monotone_cover_taskExpansion :
    forall v : DeclaredCapacity -> Nat,
      Dominance.MonotoneValuation v ->
      Dominance.AngelicValuationCovers ExpandTaskAndRevision ExpandTask v := by
  exact
    (expansionDominates_iff_all_monotone_valuation_covers
      ExpandTaskAndRevision ExpandTask).mp enrichedExpansion_dominates_taskExpansion

end ExpansionDominanceExamples
end Decision
end OmegaProper
