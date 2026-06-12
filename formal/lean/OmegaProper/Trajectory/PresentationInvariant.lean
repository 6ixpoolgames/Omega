import OmegaProper.Trajectory.SoundQuotient

/-!
OmegaProper.Trajectory.PresentationInvariant

Presentation-invariant consequence distinctions.

This file gives the first small invariant layer: a distinction is not a
presentation artifact when no sound quotient/presentation can erase it.

This does not define identity, selfhood, value, agency, recoverability,
boundary realism, or Omega proper. It only packages an existing consequence
guardrail in invariant language.
-/

namespace OmegaProper
namespace Trajectory
namespace PresentationInvariant

open ConsequenceRelation

universe w k o q i

/--
A presentation erases a pair when it assigns both fragments the same presented
value.
-/
def PairErasedByPresentation
    {X : Type w} {Q : Type q}
    (present : X -> Q)
    (x y : X) : Prop :=
  present x = present y

/--
A pair is invariant under sound quotients when every sound quotient keeps the
pair separated.

The quantification is over quotient codomains in universe `q`; this is enough
for the finite presentation families used in the current repo.
-/
def PairInvariantUnderSoundQuotients
    (S : ConsequenceSystem.{w, k, o})
    (x y : S.Fragment) : Prop :=
  forall {Q : Type q} (present : S.Fragment -> Q),
    SoundQuotient.SoundQuotient S present ->
      Not (PairErasedByPresentation present x y)

/--
Declared-family version: inside a family of presentations with a common
codomain, every sound member keeps the pair separated.
-/
def PairInvariantUnderSoundFamily
    (S : ConsequenceSystem.{w, k, o})
    {I : Type i} {Q : Type q}
    (present : I -> S.Fragment -> Q)
    (x y : S.Fragment) : Prop :=
  forall i,
    SoundQuotient.SoundQuotient S (present i) ->
      Not (PairErasedByPresentation (present i) x y)

/--
Sound presentations can identify only consequence-identifiable pairs.
-/
theorem soundPresentation_identification_implies_identifiable
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {present : S.Fragment -> Q}
    (hSound : SoundQuotient.SoundQuotient S present)
    {x y : S.Fragment}
    (hErased : PairErasedByPresentation present x y) :
    ConsequenceIdentifiable S x y := by
  exact hSound x y hErased

/--
If a pair is not consequence-identifiable, every sound quotient must keep it
separated.
-/
theorem notIdentifiable_invariantUnderSoundQuotients
    {S : ConsequenceSystem.{w, k, o}}
    {x y : S.Fragment}
    (hNot : Not (ConsequenceIdentifiable S x y)) :
    PairInvariantUnderSoundQuotients S x y := by
  intro Q present hSound hErased
  exact hNot
    (soundPresentation_identification_implies_identifiable hSound hErased)

/--
Merge-separated pairs are presentation-invariant under sound quotients.
-/
theorem mergeSeparated_invariantUnderSoundQuotients
    {S : ConsequenceSystem.{w, k, o}}
    {x y : S.Fragment}
    (hSep : ConsequenceMergeSeparated S x y) :
    PairInvariantUnderSoundQuotients S x y := by
  exact notIdentifiable_invariantUnderSoundQuotients
    (mergeSeparated_blocks_identifiable hSep)

/--
If a pair is invariant under all sound quotients, any presentation that erases
it is not sound.
-/
theorem invariantPair_erasingPresentation_not_sound
    {S : ConsequenceSystem.{w, k, o}}
    {x y : S.Fragment}
    {Q : Type q}
    {present : S.Fragment -> Q}
    (hInv : PairInvariantUnderSoundQuotients.{w, k, o, q} S x y)
    (hErased : PairErasedByPresentation present x y) :
    Not (SoundQuotient.SoundQuotient S present) := by
  intro hSound
  exact hInv present hSound hErased

/--
Merge-separated pairs remain separated inside any declared family of sound
presentations.
-/
theorem mergeSeparated_invariantUnderSoundFamily
    {S : ConsequenceSystem.{w, k, o}}
    {I : Type i} {Q : Type q}
    {present : I -> S.Fragment -> Q}
    {x y : S.Fragment}
    (hSep : ConsequenceMergeSeparated S x y) :
    PairInvariantUnderSoundFamily S present x y := by
  intro i hSound hErased
  exact mergeSeparated_blocks_identifiable hSep
    (hSound x y hErased)

/--
A presentation erases some merge-separated pair when it collapses a distinction
that the consequence system blocks.
-/
def ErasesMergeSeparatedPair
    (S : ConsequenceSystem.{w, k, o})
    {Q : Type q}
    (present : S.Fragment -> Q) : Prop :=
  exists x y,
    PairErasedByPresentation present x y /\
      ConsequenceMergeSeparated S x y

/--
Any presentation that erases a merge-separated pair is unsound.
-/
theorem erasesMergeSeparatedPair_not_sound
    {S : ConsequenceSystem.{w, k, o}}
    {Q : Type q}
    {present : S.Fragment -> Q}
    (hErase : ErasesMergeSeparatedPair S present) :
    Not (SoundQuotient.SoundQuotient S present) := by
  intro hSound
  match hErase with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact mergeSeparated_blocks_identifiable hy.right
            (hSound x y hy.left)

end PresentationInvariant
end Trajectory
end OmegaProper
