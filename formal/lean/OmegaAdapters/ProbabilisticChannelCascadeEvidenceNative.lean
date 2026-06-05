import Mathlib.Data.Fintype.Prod
import OmegaAdapters.ProbabilisticChannelCascadeNative

/-!
OmegaAdapters.ProbabilisticChannelCascadeEvidenceNative

Generic path-ensemble evidence for finite cascade error bounds.

The existing channel-specific cascade theorem is already measured over a shared
path ensemble. This module makes that path ensemble an explicit object:
the generic theorem consumes `CascadeEvidence`, not independently normalized
summary rates.
-/

namespace OmegaAdapters
namespace ProbabilisticChannelNative

universe u v w z q

/-- A finite weighted path ensemble with first-stage, second-stage, and
composite error predicates. -/
structure CascadeEvidence where
  Path : Type u
  pathFintype : Fintype Path
  weight : Path -> Nat
  firstErr : Path -> Bool
  secondErr : Path -> Bool
  compErr : Path -> Bool

namespace CascadeEvidence

/-- Total mass of all paths in an evidence object. -/
def totalMass (E : CascadeEvidence.{u}) : Nat :=
  letI : Fintype E.Path := E.pathFintype
  Finset.univ.sum fun p => E.weight p

/-- Error mass induced by one Boolean error predicate over the evidence object. -/
def errorMass (E : CascadeEvidence.{u}) (err : E.Path -> Bool) : Nat :=
  letI : Fintype E.Path := E.pathFintype
  Finset.univ.sum fun p => if err p then E.weight p else 0

def firstErrorMass (E : CascadeEvidence.{u}) : Nat :=
  E.errorMass E.firstErr

def secondErrorMass (E : CascadeEvidence.{u}) : Nat :=
  E.errorMass E.secondErr

def compositeErrorMass (E : CascadeEvidence.{u}) : Nat :=
  E.errorMass E.compErr

/-- Every composite failure is covered by at least one stage failure. -/
def CompositeFailureCovered (E : CascadeEvidence.{u}) : Prop :=
  forall p, E.compErr p = true -> E.firstErr p = true \/ E.secondErr p = true

/-- Pointwise union bound for one path in an evidence object. -/
lemma pointwise_composite_error_le_stage_errors
    (E : CascadeEvidence.{u})
    (h : E.CompositeFailureCovered)
    (p : E.Path) :
    (if E.compErr p then E.weight p else 0)
      <=
    (if E.firstErr p then E.weight p else 0)
      +
    (if E.secondErr p then E.weight p else 0) := by
  cases hComp : E.compErr p
  case false =>
    simp
  case true =>
    have hStage := h p (by simp [hComp])
    cases hStage with
    | inl hFirst =>
        simp [hFirst]
    | inr hSecond =>
        simp [hSecond]

/-- Generic finite cascade union bound over one explicit path ensemble. -/
theorem union_bound
    (E : CascadeEvidence.{u})
    (h : E.CompositeFailureCovered) :
    E.compositeErrorMass <= E.firstErrorMass + E.secondErrorMass := by
  unfold compositeErrorMass firstErrorMass secondErrorMass errorMass
  letI : Fintype E.Path := E.pathFintype
  rw [<- Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro p _hp
  exact pointwise_composite_error_le_stage_errors E h p

end CascadeEvidence

/-- Channel cascade path evidence using paths `x -> y -> z`. -/
def channelCascadeEvidence
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LD] [DecidableEq LE]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (F : Z -> LF)
    (dec1 : LE -> LD)
    (dec2 : LF -> LE) : CascadeEvidence where
  Path := Prod X (Prod Y Z)
  pathFintype := inferInstance
  weight := fun p => tripleWeight K L pi p.1 p.2.1 p.2.2
  firstErr := fun p =>
    if dec1 (E p.2.1) = D p.1 then false else true
  secondErr := fun p =>
    if dec2 (F p.2.2) = E p.2.1 then false else true
  compErr := fun p =>
    if dec1 (dec2 (F p.2.2)) = D p.1 then false else true

/-- Channel cascade evidence satisfies composite-failure coverage. -/
theorem channelCascadeEvidence_covered
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LD] [DecidableEq LE]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (F : Z -> LF)
    (dec1 : LE -> LD)
    (dec2 : LF -> LE) :
    (channelCascadeEvidence K L pi D E F dec1 dec2).CompositeFailureCovered := by
  intro p hComp
  by_cases hCompEq : dec1 (dec2 (F p.2.2)) = D p.1
  case pos =>
    simp [channelCascadeEvidence, hCompEq] at hComp
  case neg =>
    have hStage :=
      composite_failure_implies_stage_failure
        (D := D) (E := E) (F := F) (dec1 := dec1) (dec2 := dec2)
        p.1 p.2.1 p.2.2 hCompEq
    cases hStage with
    | inl hFirst =>
        left
        simp [channelCascadeEvidence, hFirst]
    | inr hSecond =>
        right
        simp [channelCascadeEvidence, hSecond]

/-- Channel cascade bound obtained from the generic evidence-object theorem. -/
theorem channel_cascade_bound_from_evidence
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LD] [DecidableEq LE]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (F : Z -> LF)
    (dec1 : LE -> LD)
    (dec2 : LF -> LE) :
    (channelCascadeEvidence K L pi D E F dec1 dec2).compositeErrorMass
      <=
    (channelCascadeEvidence K L pi D E F dec1 dec2).firstErrorMass
      +
    (channelCascadeEvidence K L pi D E F dec1 dec2).secondErrorMass := by
  exact CascadeEvidence.union_bound
    (channelCascadeEvidence K L pi D E F dec1 dec2)
    (channelCascadeEvidence_covered K L pi D E F dec1 dec2)

end ProbabilisticChannelNative
end OmegaAdapters
