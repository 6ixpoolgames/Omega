import AlphaCore.Reachability

/-!
Finite Alpha examples.

These examples prove separation facts for the primitive layer.
-/

namespace AlphaCore
namespace Examples

inductive Two
  | a
  | b
  deriving DecidableEq

inductive Three
  | a
  | b
  | c
  deriving DecidableEq

inductive OneDist
  | d
  deriving DecidableEq

def apart {T : Type} (x y : T) : Prop :=
  Not (x = y)

def symmetricTwoFrame : Frame where
  X := Two
  Rel := fun x y => apart x y
  Dist := OneDist
  Sep := fun _ x y => apart x y
  sep_irrefl := by
    intro _ x h
    exact h rfl
  sep_symm := by
    intro _ x y h hxy
    exact h (Eq.symm hxy)
  Asym := fun _ _ _ => False
  asym_rel := by
    intro _ _ _ h
    cases h
  asym_sep := by
    intro _ _ _ h
    cases h

def cycleRel : Three -> Three -> Prop
  | Three.a, Three.b => True
  | Three.b, Three.c => True
  | Three.c, Three.a => True
  | _, _ => False

def cycleFrame : Frame where
  X := Three
  Rel := cycleRel
  Dist := OneDist
  Sep := fun _ x y => apart x y
  sep_irrefl := by
    intro _ x h
    exact h rfl
  sep_symm := by
    intro _ x y h hxy
    exact h (Eq.symm hxy)
  Asym := fun _ x y => x = Three.a /\ y = Three.b
  asym_rel := by
    intro _ _ _ h
    cases h.left
    cases h.right
    trivial
  asym_sep := by
    intro _ _ _ h
    cases h.left
    cases h.right
    intro hab
    cases hab

def chainRel : Two -> Two -> Prop
  | Two.a, Two.b => True
  | _, _ => False

def chainFrame : Frame where
  X := Two
  Rel := chainRel
  Dist := OneDist
  Sep := fun _ x y => apart x y
  sep_irrefl := by
    intro _ x h
    exact h rfl
  sep_symm := by
    intro _ x y h hxy
    exact h (Eq.symm hxy)
  Asym := fun _ x y => x = Two.a /\ y = Two.b
  asym_rel := by
    intro _ _ _ h
    cases h.left
    cases h.right
    trivial
  asym_sep := by
    intro _ _ _ h
    cases h.left
    cases h.right
    intro hab
    cases hab

theorem cycle_reach_b_a :
    Reach cycleFrame Three.b Three.a := by
  exact Reach.step
    (A := cycleFrame) (x := Three.b) (y := Three.c) (z := Three.a)
    trivial
    (Reach.step
      (A := cycleFrame) (x := Three.c) (y := Three.a) (z := Three.a)
      trivial
      (Reach.refl (A := cycleFrame) Three.a))

theorem no_chain_reach_b_a :
    Not (Reach chainFrame Two.b Two.a) := by
  intro h
  have hEq : Two.b = Two.a :=
    reach_from_sink_eq chainFrame
      (x := Two.b) (y := Two.a)
      (by
        intro z hz
        cases z <;> cases hz)
      h
  cases hEq

theorem distinction_without_asymmetry :
    exists A : Frame.{0, 0}, Frame.HasDistinction A /\ Not (Frame.HasAsymmetry A) := by
  exact Exists.intro symmetricTwoFrame
    (And.intro
      (Exists.intro OneDist.d
        (Exists.intro Two.a
          (Exists.intro Two.b
            (by
              intro hab
              cases hab))))
      (by
        intro h
        match h with
        | Exists.intro _ (Exists.intro _ (Exists.intro _ hAsym)) =>
            cases hAsym))

theorem asymmetry_not_reach_irreversibility :
    exists A : Frame.{0, 0},
      exists d : A.Dist,
      exists x y : A.X,
        A.Asym d x y /\ Reach A y x := by
  exact Exists.intro cycleFrame
    (Exists.intro OneDist.d
      (Exists.intro Three.a
        (Exists.intro Three.b
          (And.intro
            (And.intro rfl rfl)
            cycle_reach_b_a))))

theorem reach_irreversibility_exists :
    exists A : Frame.{0, 0},
      exists x y : A.X,
        ReachIrreversible A x y := by
  exact Exists.intro chainFrame
    (Exists.intro Two.a
      (Exists.intro Two.b
        (And.intro
          (Reach.step
            (A := chainFrame) (x := Two.a) (y := Two.b) (z := Two.b)
            trivial
            (Reach.refl (A := chainFrame) Two.b))
          no_chain_reach_b_a)))

theorem local_nonreciprocity_not_reach_irreversibility :
    exists A : Frame.{0, 0},
      exists x y : A.X,
        LocalNonreciprocal A x y /\ Reach A y x := by
  exact Exists.intro cycleFrame
    (Exists.intro Three.a
      (Exists.intro Three.b
        (And.intro
          (And.intro trivial (by intro h; cases h))
          cycle_reach_b_a)))

theorem tiny_alpha_instantiated :
    exists A : Frame.{0, 0}, Frame.AlphaInstantiated A := by
  exact Exists.intro chainFrame
    (Frame.hasAsymmetry_implies_alphaInstantiated chainFrame
      (Exists.intro OneDist.d
        (Exists.intro Two.a
          (Exists.intro Two.b
            (And.intro rfl rfl)))))

end Examples
end AlphaCore
