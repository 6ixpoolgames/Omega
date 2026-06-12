import OmegaProper.Trajectory.TargetPresentationInvariant

/-!
OmegaProper.Trajectory.SoundPresentationFamily

Declared families of sound presentations.

This file packages the finite "presentation family" layer: instead of asking
whether one presentation preserves a target, it asks whether every sound member
of a declared family preserves it.

This is still a declared-family theorem, not a claim about all possible
boundaries, selves, observers, or value-bearing structures.
-/

namespace OmegaProper
namespace Trajectory
namespace SoundPresentationFamily

open ConsequenceRelation
open PresentationInvariant
open TargetPresentationInvariant

universe w k o q t i

/-- Every presentation in a declared family is sound. -/
def SoundPresentationFamily
    (S : ConsequenceSystem.{w, k, o})
    {I : Type i} {Q : Type q}
    (present : I -> S.Fragment -> Q) : Prop :=
  forall i, SoundQuotient.SoundQuotient S (present i)

/-- A target is preserved by every presentation in a declared family. -/
def TargetInvariantUnderFamily
    {X : Type w} {I : Type i} {Q : Type q} {T : Type t}
    (target : X -> T)
    (present : I -> X -> Q) : Prop :=
  forall i, TargetRespectsPresentation target (present i)

/--
A declared presentation family obstructs a target when some member erases a
target-distinct pair.
-/
def TargetObstructedByFamily
    {X : Type w} {I : Type i} {Q : Type q} {T : Type t}
    (target : X -> T)
    (present : I -> X -> Q) : Prop :=
  exists i, TargetObstructedByPresentation target (present i)

/-- A pair is kept apart by every presentation in a declared family. -/
def PairInvariantUnderFamily
    {X : Type w} {I : Type i} {Q : Type q}
    (present : I -> X -> Q)
    (x y : X) : Prop :=
  forall i, Not (PairErasedByPresentation (present i) x y)

theorem soundFamily_targetRespectsIdentifiability_invariant
    {S : ConsequenceSystem.{w, k, o}}
    {I : Type i} {Q : Type q} {T : Type t}
    {target : S.Fragment -> T}
    {present : I -> S.Fragment -> Q}
    (hFamily : SoundPresentationFamily S present)
    (hTarget : TargetRespectsIdentifiability S target) :
    TargetInvariantUnderFamily target present := by
  intro i
  exact soundPresentation_preserves_respecting_target
    (hFamily i)
    hTarget

theorem targetFamilyObstruction_blocks_invariance
    {X : Type w} {I : Type i} {Q : Type q} {T : Type t}
    {target : X -> T}
    {present : I -> X -> Q}
    (hObstruction : TargetObstructedByFamily target present) :
    Not (TargetInvariantUnderFamily target present) := by
  intro hInvariant
  match hObstruction with
  | Exists.intro i hTargetObstruction =>
      exact targetObstruction_blocks_respectPresentation
        hTargetObstruction
        (hInvariant i)

theorem targetInvariantUnderFamily_blocks_obstruction
    {X : Type w} {I : Type i} {Q : Type q} {T : Type t}
    {target : X -> T}
    {present : I -> X -> Q}
    (hInvariant : TargetInvariantUnderFamily target present) :
    Not (TargetObstructedByFamily target present) := by
  intro hObstruction
  exact targetFamilyObstruction_blocks_invariance hObstruction hInvariant

theorem mergeSeparated_pairInvariantUnderSoundFamily
    {S : ConsequenceSystem.{w, k, o}}
    {I : Type i} {Q : Type q}
    {present : I -> S.Fragment -> Q}
    (hFamily : SoundPresentationFamily S present)
    {x y : S.Fragment}
    (hSep : ConsequenceMergeSeparated S x y) :
    PairInvariantUnderFamily present x y := by
  intro i hErased
  exact mergeSeparated_blocks_identifiable hSep
    (hFamily i x y hErased)

theorem targetSeparated_pairInvariantUnderSoundFamily
    {S : ConsequenceSystem.{w, k, o}}
    {I : Type i} {Q : Type q} {T : Type t}
    {target : S.Fragment -> T}
    {present : I -> S.Fragment -> Q}
    (hFamily : SoundPresentationFamily S present)
    (hTarget : TargetRespectsIdentifiability S target)
    {x y : S.Fragment}
    (hSeparated : TargetSeparatedBy target x y) :
    PairInvariantUnderFamily present x y := by
  intro i hErased
  exact hSeparated
    (soundPresentation_preserves_respecting_target
      (hFamily i)
      hTarget
      x y hErased)

/--
If a sound presentation family contains a target obstruction, then the target
does not respect consequence identifiability.
-/
theorem soundFamily_targetObstruction_blocks_identifiabilityRespect
    {S : ConsequenceSystem.{w, k, o}}
    {I : Type i} {Q : Type q} {T : Type t}
    {target : S.Fragment -> T}
    {present : I -> S.Fragment -> Q}
    (hFamily : SoundPresentationFamily S present)
    (hObstruction : TargetObstructedByFamily target present) :
    Not (TargetRespectsIdentifiability S target) := by
  intro hTarget
  exact targetFamilyObstruction_blocks_invariance hObstruction
    (soundFamily_targetRespectsIdentifiability_invariant hFamily hTarget)

end SoundPresentationFamily
end Trajectory
end OmegaProper
