import OmegaProper.Decision.NonrecoverableLossDominance

/-!
OmegaProper.Decision.NonrecoverableLossDominanceExamples

Small finite witnesses for declared nonrecoverable-loss profile comparison.

The examples rank profiles/interventions relative to declared facts only. They
do not rank patients, moral worth, standing, value, rights, agency, identity,
or Omega.
-/

namespace OmegaProper
namespace Decision
namespace NonrecoverableLossDominanceExamples

open NonrecoverableLossDominance

inductive DeclaredFact where
  | local
  | joint
deriving DecidableEq, Repr

instance : LE DeclaredFact where
  le x y := x = y

instance : Preorder DeclaredFact where
  le_refl := by
    intro x
    rfl
  le_trans := by
    intro x y z hxy hyz
    exact Eq.trans hxy hyz

instance : DecidableRel ((· <= ·) : DeclaredFact -> DeclaredFact -> Prop) := by
  intro x y
  change Decidable (x = y)
  infer_instance

def LoseLocal : ContractionProfile DeclaredFact
  | DeclaredFact.local => True
  | DeclaredFact.joint => False

def LoseJoint : ContractionProfile DeclaredFact
  | DeclaredFact.local => False
  | DeclaredFact.joint => True

def LoseBoth : ContractionProfile DeclaredFact
  | DeclaredFact.local => True
  | DeclaredFact.joint => True

private theorem joint_not_downClosed_local :
    Not (DownClosedProfile LoseLocal DeclaredFact.joint) := by
  intro h
  rcases h with ⟨g, hg, hjg⟩
  cases g <;> simp [LoseLocal] at hg
  cases hjg

private theorem local_not_downClosed_joint :
    Not (DownClosedProfile LoseJoint DeclaredFact.local) := by
  intro h
  rcases h with ⟨g, hg, hlg⟩
  cases g <;> simp [LoseJoint] at hg
  cases hlg

theorem not_localLoss_dominates_jointLoss :
    Not (LossDominates LoseLocal LoseJoint) := by
  rw [not_lossDominates_iff_exists_failure_certificate]
  exact ⟨DeclaredFact.joint, by
    constructor
    · exact profile_mem_downClosed (P := LoseJoint) (by simp [LoseJoint])
    · exact joint_not_downClosed_local⟩

theorem not_jointLoss_dominates_localLoss :
    Not (LossDominates LoseJoint LoseLocal) := by
  rw [not_lossDominates_iff_exists_failure_certificate]
  exact ⟨DeclaredFact.local, by
    constructor
    · exact profile_mem_downClosed (P := LoseLocal) (by simp [LoseLocal])
    · exact local_not_downClosed_joint⟩

theorem W_disjoint_loss_profiles_incomparable :
    LossIncomparable LoseLocal LoseJoint :=
  ⟨not_localLoss_dominates_jointLoss,
    not_jointLoss_dominates_localLoss⟩

theorem bothLoss_dominates_localLoss :
    LossDominates LoseBoth LoseLocal := by
  intro f hf
  rcases hf with ⟨g, hg, hfg⟩
  exact ⟨g, by cases g <;> simp [LoseBoth], hfg⟩

theorem bothLoss_dominates_jointLoss :
    LossDominates LoseBoth LoseJoint := by
  intro f hf
  rcases hf with ⟨g, hg, hfg⟩
  exact ⟨g, by cases g <;> simp [LoseBoth], hfg⟩

/--
The ODT1 acceptance bridge applies to loss profiles: if `LoseBoth`
loss-dominates `LoseLocal`, every monotone valuation gives the corresponding
pointwise cover.
-/
theorem bothLoss_monotone_cover_localLoss :
    forall v : DeclaredFact -> Nat,
      Dominance.MonotoneValuation v ->
      Dominance.AngelicValuationCovers LoseBoth LoseLocal v := by
  exact
    (lossDominates_iff_all_monotone_valuation_covers
      LoseBoth LoseLocal).mp bothLoss_dominates_localLoss

end NonrecoverableLossDominanceExamples
end Decision
end OmegaProper
