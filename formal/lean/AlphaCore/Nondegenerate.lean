import AlphaCore.Primitive

/-!
AlphaCore.Nondegenerate

Primitive nondegeneracy witnesses.

This file does not define Omega, value, agency, future, continuation, or
deformers. It records two Alpha-native witness layers:

* a joint relation/separation witness, which blocks relation and identification
  collapse;
* an asymmetry witness, which supplies such a joint witness because `Frame.Asym`
  already implies both `Rel` and `Sep`.
-/

namespace AlphaCore
namespace Frame

universe u v

/--
A joint primitive witness is relation and separation in contact over the same
two relata and distinction.

This is the lower collapse-blocking object. It does not require asymmetric
nonreciprocity by itself.
-/
structure JointPrimitiveWitness (A : Frame.{u, v}) where
  d : A.Dist
  x : A.X
  y : A.X
  rel : A.Rel x y
  sep : A.Sep d x y

/--
An asymmetry primitive witness is an actual asymmetric bearing of a distinction
across two relata.
-/
structure AsymmetryPrimitiveWitness (A : Frame.{u, v}) where
  d : A.Dist
  x : A.X
  y : A.X
  asym : A.Asym d x y

/-- Every asymmetry witness supplies relation/separation contact. -/
def AsymmetryPrimitiveWitness.toJoint
    {A : Frame.{u, v}}
    (w : AsymmetryPrimitiveWitness A) :
    JointPrimitiveWitness A where
  d := w.d
  x := w.x
  y := w.y
  rel := A.asym_rel w.asym
  sep := A.asym_sep w.asym

def HasJointPrimitiveWitness (A : Frame.{u, v}) : Prop :=
  Nonempty (JointPrimitiveWitness A)

def HasAsymmetryPrimitiveWitness (A : Frame.{u, v}) : Prop :=
  Nonempty (AsymmetryPrimitiveWitness A)

/--
Compatibility name for the existing Alpha seed condition: an actual asymmetry
witness exists. The lower collapse proofs factor through `JointPrimitiveWitness`.
-/
abbrev PrimitiveWitness (A : Frame.{u, v}) : Prop :=
  HasAsymmetryPrimitiveWitness A

/--
Primitive nondegeneracy is currently the existence of an asymmetry primitive
witness.

This should not be read as Omega. It is only the seed condition that the
primitive grammar is not decorative.
-/
abbrev PrimitiveNondegenerate (A : Frame.{u, v}) : Prop :=
  HasAsymmetryPrimitiveWitness A

/--
A stronger directional witness: the asymmetric bearing is not reciprocated under
the same distinction.

This is stronger than primitive nondegeneracy and should not be required for
every substrate unless we explicitly want nonreciprocity rather than mere
non-identification.
-/
def DirectionalPrimitiveWitness (A : Frame.{u, v}) : Prop :=
  exists w : AsymmetryPrimitiveWitness A, Not (A.Asym w.d w.y w.x)

/--
A total identification collapse: no distinction separates any two relata. If
this holds, there can be no joint primitive witness.
-/
def IdentificationCollapse (A : Frame.{u, v}) : Prop :=
  forall d x y, Not (A.Sep d x y)

/-- A relation collapse: no relation holds anywhere. -/
def RelationCollapse (A : Frame.{u, v}) : Prop :=
  forall x y, Not (A.Rel x y)

/-- An asymmetry collapse: no asymmetric bearing holds anywhere. -/
def AsymmetryCollapse (A : Frame.{u, v}) : Prop :=
  Not (PrimitiveWitness A)

theorem jointWitness_implies_relationWitness
    {A : Frame.{u, v}}
    (w : JointPrimitiveWitness A) :
    HasRelation A := by
  exact Exists.intro w.x (Exists.intro w.y w.rel)

theorem jointWitness_implies_distinctionWitness
    {A : Frame.{u, v}}
    (w : JointPrimitiveWitness A) :
    HasDistinction A := by
  exact Exists.intro w.d
    (Exists.intro w.x
      (Exists.intro w.y w.sep))

theorem jointWitness_implies_distinct_relata
    {A : Frame.{u, v}}
    (w : JointPrimitiveWitness A) :
    Not (w.x = w.y) := by
  intro hxy
  have hsep : A.Sep w.d w.y w.y := by
    simpa [hxy] using w.sep
  exact A.sep_irrefl w.d w.y hsep

theorem jointWitness_blocks_identificationCollapse
    {A : Frame.{u, v}}
    (w : JointPrimitiveWitness A) :
    Not (IdentificationCollapse A) := by
  intro hCollapse
  exact hCollapse w.d w.x w.y w.sep

theorem jointWitness_blocks_relationCollapse
    {A : Frame.{u, v}}
    (w : JointPrimitiveWitness A) :
    Not (RelationCollapse A) := by
  intro hCollapse
  exact hCollapse w.x w.y w.rel

def asymmetryWitness_implies_jointWitness
    {A : Frame.{u, v}}
    (w : AsymmetryPrimitiveWitness A) :
    JointPrimitiveWitness A :=
  w.toJoint

theorem asymmetryWitness_blocks_identificationCollapse
    {A : Frame.{u, v}}
    (w : AsymmetryPrimitiveWitness A) :
    Not (IdentificationCollapse A) := by
  exact jointWitness_blocks_identificationCollapse w.toJoint

theorem asymmetryWitness_blocks_relationCollapse
    {A : Frame.{u, v}}
    (w : AsymmetryPrimitiveWitness A) :
    Not (RelationCollapse A) := by
  exact jointWitness_blocks_relationCollapse w.toJoint

theorem primitiveWitness_iff_hasAsymmetry
    (A : Frame.{u, v}) :
    PrimitiveWitness A <-> HasAsymmetry A := by
  constructor
  case mp =>
    intro h
    match h with
    | Nonempty.intro w =>
        exact Exists.intro w.d
          (Exists.intro w.x
            (Exists.intro w.y w.asym))
  case mpr =>
    intro h
    match h with
    | Exists.intro d hd =>
        match hd with
        | Exists.intro x hx =>
            match hx with
            | Exists.intro y hAsym =>
                exact Nonempty.intro
                  { d := d, x := x, y := y, asym := hAsym }

theorem primitiveWitness_implies_relationWitness
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    HasRelation A := by
  match h with
  | Nonempty.intro w =>
      exact jointWitness_implies_relationWitness w.toJoint

theorem primitiveWitness_implies_distinctionWitness
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    HasDistinction A := by
  match h with
  | Nonempty.intro w =>
      exact jointWitness_implies_distinctionWitness w.toJoint

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
  | Nonempty.intro w =>
      exact Exists.intro w.d
        (Exists.intro w.x
          (Exists.intro w.y
            (And.intro w.asym
              (jointWitness_implies_distinct_relata w.toJoint))))

theorem primitiveWitness_blocks_identificationCollapse
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    Not (IdentificationCollapse A) := by
  match h with
  | Nonempty.intro w =>
      exact asymmetryWitness_blocks_identificationCollapse w

theorem primitiveWitness_blocks_relationCollapse
    {A : Frame.{u, v}}
    (h : PrimitiveWitness A) :
    Not (RelationCollapse A) := by
  match h with
  | Nonempty.intro w =>
      exact asymmetryWitness_blocks_relationCollapse w

theorem identificationCollapse_blocks_jointWitness
    {A : Frame.{u, v}}
    (h : IdentificationCollapse A) :
    Not (HasJointPrimitiveWitness A) := by
  intro hWitness
  match hWitness with
  | Nonempty.intro w =>
      exact jointWitness_blocks_identificationCollapse w h

theorem relationCollapse_blocks_jointWitness
    {A : Frame.{u, v}}
    (h : RelationCollapse A) :
    Not (HasJointPrimitiveWitness A) := by
  intro hWitness
  match hWitness with
  | Nonempty.intro w =>
      exact jointWitness_blocks_relationCollapse w h

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

theorem directionalPrimitiveWitness_implies_asymmetryWitness
    {A : Frame.{u, v}}
    (h : DirectionalPrimitiveWitness A) :
    HasAsymmetryPrimitiveWitness A := by
  match h with
  | Exists.intro w _hNoReverse =>
      exact Nonempty.intro w

theorem directionalPrimitiveWitness_implies_primitiveWitness
    {A : Frame.{u, v}}
    (h : DirectionalPrimitiveWitness A) :
    PrimitiveWitness A := by
  exact directionalPrimitiveWitness_implies_asymmetryWitness h

theorem directionalPrimitiveWitness_implies_alphaInstantiated
    {A : Frame.{u, v}}
    (h : DirectionalPrimitiveWitness A) :
    AlphaInstantiated A := by
  exact primitiveWitness_implies_alphaInstantiated
    (directionalPrimitiveWitness_implies_primitiveWitness h)

theorem subsingleton_blocks_jointWitness
    {A : Frame.{u, v}}
    (hSub : Subsingleton A.X) :
    Not (HasJointPrimitiveWitness A) := by
  intro hWitness
  match hWitness with
  | Nonempty.intro w =>
      have hxy : w.x = w.y := Subsingleton.elim w.x w.y
      exact (jointWitness_implies_distinct_relata w) hxy

theorem subsingleton_blocks_primitiveWitness
    {A : Frame.{u, v}}
    (hSub : Subsingleton A.X) :
    Not (PrimitiveWitness A) := by
  intro hWitness
  match hWitness with
  | Nonempty.intro w =>
      exact subsingleton_blocks_jointWitness hSub
        (Nonempty.intro w.toJoint)

end Frame
end AlphaCore
