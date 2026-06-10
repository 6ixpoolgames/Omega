import AlphaCore.Primitive

/-!
AlphaCore.Nondegenerate

Primitive nondegeneracy witnesses.

This file does not define Omega, value, agency, future, continuation, or
deformers. It only records the Alpha-native seed condition: relation,
distinction, and asymmetry are jointly instantiated in a way that blocks total
identification collapse.
-/

namespace AlphaCore
namespace Frame

universe u v

/--
A primitive witness is an actual asymmetric bearing of a distinction across two
relata.

Because `Frame.Asym` already implies `Rel` and `Sep`, this is the smallest
Alpha-native joint-instantiation witness.
-/
def PrimitiveWitness (A : Frame.{u, v}) : Prop :=
  exists d : A.Dist, exists x y : A.X, A.Asym d x y

/--
Primitive nondegeneracy is currently the existence of a primitive witness.

This should not be read as Omega. It is only the seed condition that the
primitive grammar is not decorative.
-/
abbrev PrimitiveNondegenerate (A : Frame.{u, v}) : Prop :=
  PrimitiveWitness A

/--
A stronger directional witness: the asymmetric bearing is not reciprocated under
the same distinction.

This is stronger than primitive nondegeneracy and should not be required for
every substrate unless we explicitly want nonreciprocity rather than mere
non-identification.
-/
def DirectionalPrimitiveWitness (A : Frame.{u, v}) : Prop :=
  exists d : A.Dist, exists x y : A.X,
    A.Asym d x y /\ Not (A.Asym d y x)

/--
A total identification collapse: no distinction separates any two relata. If
this holds, there can be no primitive witness.
-/
def IdentificationCollapse (A : Frame.{u, v}) : Prop :=
  forall d x y, Not (A.Sep d x y)

/-- A relation collapse: no relation holds anywhere. -/
def RelationCollapse (A : Frame.{u, v}) : Prop :=
  forall x y, Not (A.Rel x y)

/-- An asymmetry collapse: no asymmetric bearing holds anywhere. -/
def AsymmetryCollapse (A : Frame.{u, v}) : Prop :=
  Not (PrimitiveWitness A)

theorem primitiveWitness_iff_hasAsymmetry
    (A : Frame.{u, v}) :
    PrimitiveWitness A <-> HasAsymmetry A := by
  rfl

theorem primitiveWitness_implies_relationWitness
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    HasRelation A := by
  match h with
  | Exists.intro _d hd =>
      match hd with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hAsym =>
              exact Exists.intro x (Exists.intro y (A.asym_rel hAsym))

theorem primitiveWitness_implies_distinctionWitness
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    HasDistinction A := by
  match h with
  | Exists.intro d hd =>
      match hd with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hAsym =>
              exact Exists.intro d
                (Exists.intro x
                  (Exists.intro y (A.asym_sep hAsym)))

theorem primitiveWitness_implies_alphaInstantiated
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    AlphaInstantiated A := by
  exact hasAsymmetry_implies_alphaInstantiated A
    ((primitiveWitness_iff_hasAsymmetry A).mp h)

theorem primitiveWitness_implies_distinct_relata
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    exists d : A.Dist, exists x y : A.X,
      A.Asym d x y /\ Not (x = y) := by
  match h with
  | Exists.intro d hd =>
      match hd with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hAsym =>
              exact Exists.intro d
                (Exists.intro x
                  (Exists.intro y
                    (And.intro hAsym
                      (asymmetry_implies_not_same A hAsym))))

theorem primitiveWitness_blocks_identificationCollapse
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    Not (IdentificationCollapse A) := by
  intro hCollapse
  match h with
  | Exists.intro d hd =>
      match hd with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hAsym =>
              exact hCollapse d x y (A.asym_sep hAsym)

theorem primitiveWitness_blocks_relationCollapse
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    Not (RelationCollapse A) := by
  intro hCollapse
  match h with
  | Exists.intro _d hd =>
      match hd with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hAsym =>
              exact hCollapse x y (A.asym_rel hAsym)

theorem identificationCollapse_blocks_primitiveWitness
    {A : Frame.{u, v}}
    (h : IdentificationCollapse A) :
    Not (PrimitiveWitness A) := by
  intro hWitness
  exact primitiveWitness_blocks_identificationCollapse hWitness h

theorem relationCollapse_blocks_primitiveWitness
    {A : Frame.{u, v}}
    (h : RelationCollapse A) :
    Not (PrimitiveWitness A) := by
  intro hWitness
  exact primitiveWitness_blocks_relationCollapse hWitness h

theorem directionalPrimitiveWitness_implies_primitiveWitness
    {A : Frame.{u, v}}
    (h : DirectionalPrimitiveWitness A) :
    PrimitiveWitness A := by
  match h with
  | Exists.intro d hd =>
      match hd with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hy =>
              exact Exists.intro d
                (Exists.intro x
                  (Exists.intro y hy.left))

theorem directionalPrimitiveWitness_implies_alphaInstantiated
    {A : Frame.{u, v}}
    (h : DirectionalPrimitiveWitness A) :
    AlphaInstantiated A := by
  exact primitiveWitness_implies_alphaInstantiated
    (directionalPrimitiveWitness_implies_primitiveWitness h)

theorem subsingleton_blocks_primitiveWitness
    {A : Frame.{u, v}}
    (hSub : Subsingleton A.X) :
    Not (PrimitiveWitness A) := by
  intro hWitness
  match hWitness with
  | Exists.intro _d hd =>
      match hd with
      | Exists.intro x hx =>
          match hx with
          | Exists.intro y hAsym =>
              have hxy : x = y := Subsingleton.elim x y
              exact (asymmetry_implies_not_same A hAsym) hxy

end Frame
end AlphaCore
