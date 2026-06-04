/-!
Alpha primitive frame.

This file gives a minimal carrier with relation, distinction, and asymmetry.
-/

namespace AlphaCore

universe u v

/-- A minimal Alpha frame. -/
structure Frame where
  X : Type u
  Rel : X -> X -> Prop
  Dist : Type v
  Sep : Dist -> X -> X -> Prop
  sep_irrefl : forall d x, Not (Sep d x x)
  sep_symm : forall d x y, Sep d x y -> Sep d y x
  Asym : Dist -> X -> X -> Prop
  asym_rel : forall {d x y}, Asym d x y -> Rel x y
  asym_sep : forall {d x y}, Asym d x y -> Sep d x y

namespace Frame

def HasRelation (A : Frame) : Prop :=
  exists x y : A.X, A.Rel x y

def HasDistinction (A : Frame) : Prop :=
  exists d : A.Dist, exists x y : A.X, A.Sep d x y

def HasAsymmetry (A : Frame) : Prop :=
  exists d : A.Dist, exists x y : A.X, A.Asym d x y

def AlphaInstantiated (A : Frame) : Prop :=
  HasRelation A /\ HasDistinction A /\ HasAsymmetry A

theorem asymmetry_implies_relation
    (A : Frame) {d : A.Dist} {x y : A.X}
    (h : A.Asym d x y) : A.Rel x y := by
  exact A.asym_rel h

theorem asymmetry_implies_distinction
    (A : Frame) {d : A.Dist} {x y : A.X}
    (h : A.Asym d x y) : A.Sep d x y := by
  exact A.asym_sep h

theorem asymmetry_implies_not_same
    (A : Frame) {d : A.Dist} {x y : A.X}
    (h : A.Asym d x y) : Not (x = y) := by
  intro hxy
  subst hxy
  exact A.sep_irrefl d x (A.asym_sep h)

theorem hasAsymmetry_implies_alphaInstantiated
    (A : Frame)
    (h : HasAsymmetry A) : AlphaInstantiated A := by
  match h with
  | Exists.intro d (Exists.intro x (Exists.intro y hAsym)) =>
      exact And.intro
        (Exists.intro x (Exists.intro y (A.asym_rel hAsym)))
        (And.intro
          (Exists.intro d (Exists.intro x (Exists.intro y (A.asym_sep hAsym))))
          (Exists.intro d (Exists.intro x (Exists.intro y hAsym))))

end Frame

end AlphaCore
