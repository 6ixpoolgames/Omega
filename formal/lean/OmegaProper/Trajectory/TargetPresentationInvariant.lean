import OmegaProper.Trajectory.PresentationInvariant

/-!
OmegaProper.Trajectory.TargetPresentationInvariant

Target-level presentation invariance.

The pair-level invariant layer says a sound presentation cannot erase a
merge-separated pair. This file lifts that idea to targets: a target survives a
presentation when it is constant on the presentation's fibers.

This is the same mathematical shape as fiber constancy for summaries, but it
lives in the trajectory/presentation layer to avoid depending on baseline
witness modules.
-/

namespace OmegaProper
namespace Trajectory
namespace TargetPresentationInvariant

open ConsequenceRelation
open PresentationInvariant

universe w k o q t

/--
A target respects a presentation when equal presented values force equal target
values.

Equivalently: the target is constant on the presentation's fibers.
-/
def TargetRespectsPresentation
    {X : Type w} {Q : Type q} {T : Type t}
    (target : X -> T)
    (present : X -> Q) : Prop :=
  forall x y, present x = present y -> target x = target y

/-- A target distinguishes a pair when the target values differ. -/
def TargetSeparatedBy
    {X : Type w} {T : Type t}
    (target : X -> T)
    (x y : X) : Prop :=
  Not (target x = target y)

/--
A presentation obstructs a target when it erases a pair that the target
distinguishes.
-/
def TargetObstructedByPresentation
    {X : Type w} {Q : Type q} {T : Type t}
    (target : X -> T)
    (present : X -> Q) : Prop :=
  exists x y,
    PairErasedByPresentation present x y /\
      TargetSeparatedBy target x y

/--
A target respects consequence identifiability when it is constant on every
consequence-identifiable pair.
-/
def TargetRespectsIdentifiability
    (S : ConsequenceSystem.{w, k, o})
    {T : Type t}
    (target : S.Fragment -> T) : Prop :=
  forall x y, ConsequenceIdentifiable S x y -> target x = target y

/--
A target is invariant under sound quotients when every sound presentation
preserves it.
-/
def TargetInvariantUnderSoundQuotients
    (S : ConsequenceSystem.{w, k, o})
    {T : Type t}
    (target : S.Fragment -> T) : Prop :=
  forall {Q : Type q} (present : S.Fragment -> Q),
    SoundQuotient.SoundQuotient S present ->
      TargetRespectsPresentation target present

theorem targetObstruction_blocks_respectPresentation
    {X : Type w} {Q : Type q} {T : Type t}
    {target : X -> T}
    {present : X -> Q}
    (h : TargetObstructedByPresentation target present) :
    Not (TargetRespectsPresentation target present) := by
  intro hRespect
  match h with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact hy.right (hRespect x y hy.left)

theorem targetRespectsPresentation_blocks_obstruction
    {X : Type w} {Q : Type q} {T : Type t}
    {target : X -> T}
    {present : X -> Q}
    (h : TargetRespectsPresentation target present) :
    Not (TargetObstructedByPresentation target present) := by
  intro hObstruction
  exact targetObstruction_blocks_respectPresentation hObstruction h

/--
If a target is constant on consequence-identifiable pairs, then any sound
presentation preserves the target.
-/
theorem soundPresentation_preserves_respecting_target
    {S : ConsequenceSystem.{w, k, o}}
    {T : Type t}
    {target : S.Fragment -> T}
    {Q : Type q}
    {present : S.Fragment -> Q}
    (hSound : SoundQuotient.SoundQuotient S present)
    (hTarget : TargetRespectsIdentifiability S target) :
    TargetRespectsPresentation target present := by
  intro x y hErased
  exact hTarget x y (hSound x y hErased)

theorem targetRespectsIdentifiability_invariantUnderSoundQuotients
    {S : ConsequenceSystem.{w, k, o}}
    {T : Type t}
    {target : S.Fragment -> T}
    (hTarget : TargetRespectsIdentifiability S target) :
    TargetInvariantUnderSoundQuotients S target := by
  intro Q present hSound
  exact soundPresentation_preserves_respecting_target hSound hTarget

/--
If a sound presentation erases a target distinction, then the target is not
constant on consequence-identifiable pairs.
-/
theorem soundPresentation_targetObstruction_blocks_identifiabilityRespect
    {S : ConsequenceSystem.{w, k, o}}
    {T : Type t}
    {target : S.Fragment -> T}
    {Q : Type q}
    {present : S.Fragment -> Q}
    (hSound : SoundQuotient.SoundQuotient S present)
    (hObstruction : TargetObstructedByPresentation target present) :
    Not (TargetRespectsIdentifiability S target) := by
  intro hRespect
  exact targetObstruction_blocks_respectPresentation hObstruction
    (soundPresentation_preserves_respecting_target hSound hRespect)

/--
If a target respects consequence identifiability and distinguishes a pair, no
sound presentation can erase that pair.
-/
theorem targetSeparated_invariantUnderSoundQuotients
    {S : ConsequenceSystem.{w, k, o}}
    {T : Type t}
    {target : S.Fragment -> T}
    (hRespect : TargetRespectsIdentifiability S target)
    {x y : S.Fragment}
    (hSep : TargetSeparatedBy target x y) :
    PairInvariantUnderSoundQuotients S x y := by
  intro Q present hSound hErased
  exact hSep
    (soundPresentation_preserves_respecting_target hSound hRespect x y hErased)

end TargetPresentationInvariant
end Trajectory
end OmegaProper
