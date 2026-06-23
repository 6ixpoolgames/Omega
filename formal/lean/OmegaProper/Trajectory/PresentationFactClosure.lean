import Mathlib.Data.Set.Basic
import OmegaProper.Trajectory.TargetPresentationInvariant

/-!
OmegaProper.Trajectory.PresentationFactClosure

Generic fact/presentation closure for admissibility pilots.

This file isolates the standard formal-context pattern that keeps recurring in
the project:

* presentations, summaries, quotients, or observations live on one side;
* facts, targets, distinctions, or continuation claims live on the other;
* a supplied satisfaction relation says which presentation preserves which
  fact.

From only that relation we get common facts, models of facts, and the Galois
connection between them. This does not decide which presentations are
admissible. It gives a disciplined surface for asking what follows from a
declared admissible family and for testing whether a proposed family collapses
all nontrivial facts.

This file does not define value, agency, identity, boundary realism, or Omega
structure.
-/

namespace OmegaProper
namespace Trajectory
namespace PresentationFactClosure

open PresentationInvariant
open TargetPresentationInvariant

universe u v w t

/-- Claims common to every presentation in a declared presentation set. -/
def CommonClaims
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (presentations : Set Presentation) : Set Claim :=
  fun claim => forall present, present ∈ presentations -> Satisfies present claim

/-- Presentations satisfying every claim in a declared claim set. -/
def ModelsOfClaims
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (claims : Set Claim) : Set Presentation :=
  fun present => forall claim, claim ∈ claims -> Satisfies present claim

/--
The formal-context Galois law: a claim set is contained in the common facts of
a presentation set exactly when the presentation set is contained in the
models of that claim set.
-/
theorem commonClaims_modelsOfClaims_galois
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (presentations : Set Presentation)
    (claims : Set Claim) :
    claims ⊆ CommonClaims Satisfies presentations <->
      presentations ⊆ ModelsOfClaims Satisfies claims := by
  constructor
  · intro hClaims present hPresent claim hClaim
    exact hClaims hClaim present hPresent
  · intro hPresent claim hClaim present hIn
    exact hPresent hIn claim hClaim

/-- Common claims are contravariant in the presentation set. -/
theorem commonClaims_antitone
    {Presentation : Type u}
    {Claim : Type v}
    {Satisfies : Presentation -> Claim -> Prop}
    {small large : Set Presentation}
    (hSubset : small ⊆ large) :
    CommonClaims Satisfies large ⊆ CommonClaims Satisfies small := by
  intro claim hCommon present hSmall
  exact hCommon present (hSubset hSmall)

/-- Models of claims are contravariant in the claim set. -/
theorem modelsOfClaims_antitone
    {Presentation : Type u}
    {Claim : Type v}
    {Satisfies : Presentation -> Claim -> Prop}
    {small large : Set Claim}
    (hSubset : small ⊆ large) :
    ModelsOfClaims Satisfies large ⊆ ModelsOfClaims Satisfies small := by
  intro present hModel claim hSmall
  exact hModel claim (hSubset hSmall)

/-- Presentation closure induced by the common claims of a presentation set. -/
def PresentationClosure
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (presentations : Set Presentation) : Set Presentation :=
  ModelsOfClaims Satisfies (CommonClaims Satisfies presentations)

/-- Claim closure induced by all presentations satisfying a claim set. -/
def ClaimClosure
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (claims : Set Claim) : Set Claim :=
  CommonClaims Satisfies (ModelsOfClaims Satisfies claims)

/-- A presentation set is contained in its induced presentation closure. -/
theorem presentations_subset_closure
    {Presentation : Type u}
    {Claim : Type v}
    {Satisfies : Presentation -> Claim -> Prop}
    {presentations : Set Presentation} :
    presentations ⊆ PresentationClosure Satisfies presentations := by
  intro present hPresent claim hClaim
  exact hClaim present hPresent

/-- A claim set is contained in its induced claim closure. -/
theorem claims_subset_closure
    {Presentation : Type u}
    {Claim : Type v}
    {Satisfies : Presentation -> Claim -> Prop}
    {claims : Set Claim} :
    claims ⊆ ClaimClosure Satisfies claims := by
  intro claim hClaim present hModel
  exact hModel claim hClaim

/-- Presentation closure is monotone in the presentation set. -/
theorem presentationClosure_mono
    {Presentation : Type u}
    {Claim : Type v}
    {Satisfies : Presentation -> Claim -> Prop}
    {small large : Set Presentation}
    (hSubset : small ⊆ large) :
    PresentationClosure Satisfies small ⊆
      PresentationClosure Satisfies large := by
  intro present hModel claim hCommonLarge
  exact hModel claim (commonClaims_antitone hSubset hCommonLarge)

/-- Claim closure is monotone in the claim set. -/
theorem claimClosure_mono
    {Presentation : Type u}
    {Claim : Type v}
    {Satisfies : Presentation -> Claim -> Prop}
    {small large : Set Claim}
    (hSubset : small ⊆ large) :
    ClaimClosure Satisfies small ⊆ ClaimClosure Satisfies large := by
  intro claim hClosed present hModelLarge
  exact hClosed present (modelsOfClaims_antitone hSubset hModelLarge)

/--
Every claim common to a presentation set is also common to the closure of that
presentation set.
-/
theorem commonClaims_subset_commonClaims_closure
    {Presentation : Type u}
    {Claim : Type v}
    {Satisfies : Presentation -> Claim -> Prop}
    {presentations : Set Presentation} :
    CommonClaims Satisfies presentations ⊆
      CommonClaims Satisfies
        (PresentationClosure Satisfies presentations) := by
  intro claim hCommon present hClosed
  exact hClosed claim hCommon

/-- Presentation closure is idempotent. -/
theorem presentationClosure_idempotent
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (presentations : Set Presentation) :
    PresentationClosure Satisfies
        (PresentationClosure Satisfies presentations) =
      PresentationClosure Satisfies presentations := by
  apply Set.Subset.antisymm
  · intro present hClosed claim hCommon
    have hCommonClosed :
        claim ∈
          CommonClaims Satisfies
            (PresentationClosure Satisfies presentations) :=
      commonClaims_subset_commonClaims_closure hCommon
    exact hClosed claim hCommonClosed
  · exact presentations_subset_closure

/-- Claim closure is idempotent. -/
theorem claimClosure_idempotent
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (claims : Set Claim) :
    ClaimClosure Satisfies (ClaimClosure Satisfies claims) =
      ClaimClosure Satisfies claims := by
  apply Set.Subset.antisymm
  · intro claim hClosed present hModel
    have hModelClosed :
        present ∈ ModelsOfClaims Satisfies (ClaimClosure Satisfies claims) := by
      intro claim' hClaim'
      exact hClaim' present hModel
    exact hClosed present hModelClosed
  · exact claims_subset_closure

/--
Admissible common claim: a claim satisfied by every presentation in a declared
admissible set.
-/
def ClaimInvariantUnderAdmissible
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (Admissible : Set Presentation)
    (claim : Claim) : Prop :=
  claim ∈ CommonClaims Satisfies Admissible

/--
A presentation satisfies the closed theory generated by a claim set.
-/
def PresentationModelsClosedClaims
    {Presentation : Type u}
    {Claim : Type v}
    (Satisfies : Presentation -> Claim -> Prop)
    (claims : Set Claim)
    (present : Presentation) : Prop :=
  present ∈ ModelsOfClaims Satisfies (ClaimClosure Satisfies claims)

/-- A fixed-codomain presentation satisfies a target when it preserves it. -/
def TargetSatisfiesPresentation
    {X : Type u}
    {Q : Type v}
    {T : Type t}
    (present : X -> Q)
    (target : X -> T) : Prop :=
  TargetRespectsPresentation target present

/-- A fixed-codomain presentation satisfies a pair when it keeps it visible. -/
def PairVisibleSatisfiesPresentation
    {X : Type u}
    {Q : Type v}
    (present : X -> Q)
    (pair : X × X) : Prop :=
  Not (PairErasedByPresentation present pair.1 pair.2)

/-- Targets common to all declared admissible presentations. -/
abbrev CommonTargets
    {X : Type u}
    {Q : Type v}
    {T : Type t}
    (Admissible : Set (X -> Q)) : Set (X -> T) :=
  CommonClaims TargetSatisfiesPresentation Admissible

/-- Pairs kept visible by all declared admissible presentations. -/
abbrev CommonVisiblePairs
    {X : Type u}
    {Q : Type v}
    (Admissible : Set (X -> Q)) : Set (X × X) :=
  CommonClaims PairVisibleSatisfiesPresentation Admissible

theorem target_mem_commonTargets_iff
    {X : Type u}
    {Q : Type v}
    {T : Type t}
    {Admissible : Set (X -> Q)}
    {target : X -> T} :
    target ∈ CommonTargets Admissible <->
      forall present, present ∈ Admissible ->
        TargetRespectsPresentation target present := by
  rfl

theorem pair_mem_commonVisiblePairs_iff
    {X : Type u}
    {Q : Type v}
    {Admissible : Set (X -> Q)}
    {pair : X × X} :
    pair ∈ CommonVisiblePairs Admissible <->
      forall present, present ∈ Admissible ->
        Not (PairErasedByPresentation present pair.1 pair.2) := by
  rfl

end PresentationFactClosure
end Trajectory
end OmegaProper
