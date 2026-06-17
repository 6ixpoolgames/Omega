import AlphaCore.PrimitiveMap
import AlphaCore.PrimitivePath

/-!
AlphaCore.PrimitiveSoundPresentation

Primitive-sound presentations.

This is the Alpha-native analogue of consequence-sound quotient discipline:
a primitive-sound presentation may identify only primitively inseparable relata.
It does not assert that primitive apartness is already evaluated consequence.
-/

namespace AlphaCore
namespace Frame

universe u v q u' v'

/-- A presentation erases a pair when it assigns both relata the same code. -/
def PairErasedByPrimitivePresentation
    {A : Frame.{u, v}}
    {Q : Type q}
    (present : A.X -> Q)
    (x y : A.X) : Prop :=
  present x = present y

/--
A primitive-sound presentation never merges primitively apart relata.

This is kernel containment in primitive inseparability.
-/
def PrimitiveSoundPresentation
    (A : Frame.{u, v})
    {Q : Type q}
    (present : A.X -> Q) : Prop :=
  forall x y : A.X,
    present x = present y ->
      PrimitiveInseparable A x y

/-- A pair is invariant under all primitive-sound presentations. -/
def PairInvariantUnderPrimitiveSoundPresentations
    (A : Frame.{u, v})
    (x y : A.X) : Prop :=
  forall {Q : Type q} (present : A.X -> Q),
    PrimitiveSoundPresentation A present ->
      Not (present x = present y)

theorem primitiveSoundPresentation_iff_kernelContained
    (A : Frame.{u, v})
    {Q : Type q}
    (present : A.X -> Q) :
    PrimitiveSoundPresentation A present <->
      forall x y : A.X,
        present x = present y ->
          PrimitiveInseparable A x y := by
  rfl

theorem primitiveSoundPresentation_blocks_apart_kernel
    {A : Frame.{u, v}}
    {Q : Type q}
    {present : A.X -> Q}
    (hSound : PrimitiveSoundPresentation A present)
    {x y : A.X}
    (hApart : PrimitiveApart A x y)
    (hErased : present x = present y) :
    False := by
  exact hSound x y hErased hApart

theorem primitiveApart_kernel_blocks_soundPresentation
    {A : Frame.{u, v}}
    {Q : Type q}
    {present : A.X -> Q}
    {x y : A.X}
    (hApart : PrimitiveApart A x y)
    (hErased : present x = present y) :
    Not (PrimitiveSoundPresentation A present) := by
  intro hSound
  exact primitiveSoundPresentation_blocks_apart_kernel hSound hApart hErased

theorem primitiveApart_invariantUnderSoundPresentations
    {A : Frame.{u, v}}
    {x y : A.X}
    (hApart : PrimitiveApart A x y) :
    PairInvariantUnderPrimitiveSoundPresentations A x y := by
  intro _Q present hSound hErased
  exact primitiveSoundPresentation_blocks_apart_kernel hSound hApart hErased

theorem asymmetryWitness_invariantUnderSoundPresentations
    {A : Frame.{u, v}}
    (w : AsymmetryPrimitiveWitness A) :
    PairInvariantUnderPrimitiveSoundPresentations A w.x w.y := by
  exact primitiveApart_invariantUnderSoundPresentations
    (asymmetryWitness_implies_primitiveApart w)

theorem primitiveWitness_constantPresentation_not_sound
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    Not (PrimitiveSoundPresentation A (fun _ : A.X => ())) := by
  intro hSound
  match h with
  | Nonempty.intro w =>
      exact primitiveSoundPresentation_blocks_apart_kernel
        hSound
        (asymmetryWitness_implies_primitiveApart w)
        rfl

theorem primitiveMap_preserves_primitiveApart
    {A : Frame.{u, v}}
    {B : Frame.{u', v'}}
    (f : PrimitiveMap A B)
    {x y : A.X}
    (hApart : PrimitiveApart A x y) :
    PrimitiveApart B (f.mapX x) (f.mapX y) := by
  match hApart with
  | Exists.intro d hSep =>
      exact Exists.intro (f.mapD d) (f.sep_preserving hSep)

/--
Primitive-sound presentations pull back along primitive-preserving maps.

If `B` has a primitive-sound presentation, then composing it with a
primitive-preserving map `A -> B` gives a primitive-sound presentation of `A`.
-/
theorem primitiveMap_pullback_soundPresentation
    {A : Frame.{u, v}}
    {B : Frame.{u', v'}}
    (f : PrimitiveMap A B)
    {Q : Type q}
    {present : B.X -> Q}
    (hSound : PrimitiveSoundPresentation B present) :
    PrimitiveSoundPresentation A (fun x => present (f.mapX x)) := by
  intro x y hEq hApart
  exact hSound
    (f.mapX x)
    (f.mapX y)
    hEq
    (primitiveMap_preserves_primitiveApart f hApart)

end Frame
end AlphaCore
