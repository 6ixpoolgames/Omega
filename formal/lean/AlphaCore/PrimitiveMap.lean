import AlphaCore.Nondegenerate

/-!
AlphaCore.PrimitiveMap

Primitive-preserving transformations between Alpha frames.

This file does not assert that all coarse-grainings preserve primitive work.
It defines transformations that preserve primitive work and proves that
collapsed targets cannot receive nondegenerate primitive work through such maps.

This is a pre-recoverability bridge: recoverability should later be expressed
through admissible transformations, not exact object sameness.
-/

namespace AlphaCore
namespace Frame

universe u v u' v' u'' v''

/--
A primitive-preserving map carries relata and distinctions from one frame to
another while preserving relation, separation, and asymmetry.

This is not an object-sameness map. It is a structure-preserving transformation
between primitive presentations.
-/
structure PrimitiveMap
    (A : Frame.{u, v})
    (B : Frame.{u', v'}) where
  mapX : A.X -> B.X
  mapD : A.Dist -> B.Dist
  rel_preserving :
    forall {x y : A.X},
      A.Rel x y ->
      B.Rel (mapX x) (mapX y)
  sep_preserving :
    forall {d : A.Dist} {x y : A.X},
      A.Sep d x y ->
      B.Sep (mapD d) (mapX x) (mapX y)
  asym_preserving :
    forall {d : A.Dist} {x y : A.X},
      A.Asym d x y ->
      B.Asym (mapD d) (mapX x) (mapX y)

/-- Existence predicate for primitive-preserving maps. -/
def HasPrimitiveMap
    (A : Frame.{u, v})
    (B : Frame.{u', v'}) : Prop :=
  Nonempty (PrimitiveMap A B)

namespace PrimitiveMap

variable {A : Frame.{u, v}}
variable {B : Frame.{u', v'}}
variable {C : Frame.{u'', v''}}

/-- A primitive-preserving map sends joint witnesses to joint witnesses. -/
def mapJointWitness
    (f : PrimitiveMap A B)
    (w : JointPrimitiveWitness A) :
    JointPrimitiveWitness B where
  d := f.mapD w.d
  x := f.mapX w.x
  y := f.mapX w.y
  rel := f.rel_preserving w.rel
  sep := f.sep_preserving w.sep

/-- A primitive-preserving map sends asymmetry witnesses to asymmetry witnesses. -/
def mapAsymmetryWitness
    (f : PrimitiveMap A B)
    (w : AsymmetryPrimitiveWitness A) :
    AsymmetryPrimitiveWitness B where
  d := f.mapD w.d
  x := f.mapX w.x
  y := f.mapX w.y
  asym := f.asym_preserving w.asym

/-- Reflexive primitive-preserving map. -/
def id (A : Frame.{u, v}) : PrimitiveMap A A where
  mapX := fun x => x
  mapD := fun d => d
  rel_preserving := by
    intro _x _y h
    exact h
  sep_preserving := by
    intro _d _x _y h
    exact h
  asym_preserving := by
    intro _d _x _y h
    exact h

/-- Composition of primitive-preserving maps. -/
def comp
    (g : PrimitiveMap B C)
    (f : PrimitiveMap A B) :
    PrimitiveMap A C where
  mapX := fun x => g.mapX (f.mapX x)
  mapD := fun d => g.mapD (f.mapD d)
  rel_preserving := by
    intro _x _y h
    exact g.rel_preserving (f.rel_preserving h)
  sep_preserving := by
    intro _d _x _y h
    exact g.sep_preserving (f.sep_preserving h)
  asym_preserving := by
    intro _d _x _y h
    exact g.asym_preserving (f.asym_preserving h)

theorem preserves_jointPrimitiveWitness
    (f : PrimitiveMap A B)
    (h : HasJointPrimitiveWitness A) :
    HasJointPrimitiveWitness B := by
  match h with
  | Nonempty.intro w =>
      exact Nonempty.intro (f.mapJointWitness w)

theorem preserves_asymmetryPrimitiveWitness
    (f : PrimitiveMap A B)
    (h : HasAsymmetryPrimitiveWitness A) :
    HasAsymmetryPrimitiveWitness B := by
  match h with
  | Nonempty.intro w =>
      exact Nonempty.intro (f.mapAsymmetryWitness w)

theorem preserves_primitiveNondegenerate
    (f : PrimitiveMap A B)
    (h : PrimitiveNondegenerate A) :
    PrimitiveNondegenerate B := by
  exact preserves_asymmetryPrimitiveWitness f h

theorem no_map_to_identificationCollapse
    (hA : HasJointPrimitiveWitness A)
    (hB : IdentificationCollapse B) :
    Not (HasPrimitiveMap A B) := by
  intro hMap
  match hMap with
  | Nonempty.intro f =>
      match hA with
      | Nonempty.intro w =>
          let wB := f.mapJointWitness w
          exact hB wB.d wB.x wB.y wB.sep

theorem no_map_to_relationCollapse
    (hA : HasJointPrimitiveWitness A)
    (hB : RelationCollapse B) :
    Not (HasPrimitiveMap A B) := by
  intro hMap
  match hMap with
  | Nonempty.intro f =>
      match hA with
      | Nonempty.intro w =>
          let wB := f.mapJointWitness w
          exact hB wB.x wB.y wB.rel

theorem no_map_to_asymmetryCollapse
    (hA : PrimitiveNondegenerate A)
    (hB : AsymmetryCollapse B) :
    Not (HasPrimitiveMap A B) := by
  intro hMap
  match hMap with
  | Nonempty.intro f =>
      exact hB (preserves_primitiveNondegenerate f hA)

end PrimitiveMap
end Frame
end AlphaCore
