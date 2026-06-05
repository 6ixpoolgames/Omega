import AlphaCore.Reachability

/-!
AlphaCore.Independence

Primitive non-collapse examples for the Alpha floor.

These finite witnesses separate relation, distinction, asymmetry, local
nonreciprocity, and reach irreversibility. They are guardrails against treating
one primitive role as if it automatically supplied the others.
-/

namespace AlphaCore
namespace Independence

/-- Two-point carrier for primitive independence examples. -/
inductive Two
  | a
  | b
  deriving DecidableEq

/-- One distinction symbol. -/
inductive OneDist
  | d
  deriving DecidableEq

def apart {T : Type} (x y : T) : Prop :=
  Not (x = y)

def oneWayRel : Two -> Two -> Prop
  | Two.a, Two.b => True
  | _, _ => False

/-- A frame with relation but no distinction symbols. -/
def relationOnlyFrame : Frame.{0, 0} where
  X := Two
  Rel := oneWayRel
  Dist := Empty
  Sep := fun d _ _ => nomatch d
  sep_irrefl := by
    intro d
    cases d
  sep_symm := by
    intro d
    cases d
  Asym := fun d _ _ => nomatch d
  asym_rel := by
    intro d
    cases d
  asym_sep := by
    intro d
    cases d

/-- A frame with distinction but no relation. -/
def distinctionOnlyFrame : Frame.{0, 0} where
  X := Two
  Rel := fun _ _ => False
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

/-- A frame with relation and distinction but no asymmetry witness. -/
def relationDistinctionNoAsymFrame : Frame.{0, 0} where
  X := Two
  Rel := oneWayRel
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

theorem relationOnly_has_relation :
    Frame.HasRelation relationOnlyFrame := by
  exact Exists.intro Two.a (Exists.intro Two.b trivial)

theorem relationOnly_no_distinction :
    Not (Frame.HasDistinction relationOnlyFrame) := by
  intro h
  cases h with
  | intro d _ =>
      cases d

/-- Relation can exist without distinction. -/
theorem relation_without_distinction :
    exists A : Frame.{0, 0},
      Frame.HasRelation A /\ Not (Frame.HasDistinction A) := by
  exact Exists.intro relationOnlyFrame
    (And.intro relationOnly_has_relation relationOnly_no_distinction)

theorem distinctionOnly_has_distinction :
    Frame.HasDistinction distinctionOnlyFrame := by
  exact Exists.intro OneDist.d
    (Exists.intro Two.a
      (Exists.intro Two.b
        (by
          intro hab
          cases hab)))

theorem distinctionOnly_no_relation :
    Not (Frame.HasRelation distinctionOnlyFrame) := by
  intro h
  cases h with
  | intro _ hxy =>
      cases hxy with
      | intro _ hRel =>
          cases hRel

/-- Distinction can exist without relation. -/
theorem distinction_without_relation :
    exists A : Frame.{0, 0},
      Frame.HasDistinction A /\ Not (Frame.HasRelation A) := by
  exact Exists.intro distinctionOnlyFrame
    (And.intro distinctionOnly_has_distinction distinctionOnly_no_relation)

theorem relationDistinction_has_relation :
    Frame.HasRelation relationDistinctionNoAsymFrame := by
  exact Exists.intro Two.a (Exists.intro Two.b trivial)

theorem relationDistinction_has_distinction :
    Frame.HasDistinction relationDistinctionNoAsymFrame := by
  exact Exists.intro OneDist.d
    (Exists.intro Two.a
      (Exists.intro Two.b
        (by
          intro hab
          cases hab)))

theorem relationDistinction_no_asymmetry :
    Not (Frame.HasAsymmetry relationDistinctionNoAsymFrame) := by
  intro h
  cases h with
  | intro _ hxy =>
      cases hxy with
      | intro _ hyz =>
          cases hyz with
          | intro _ hAsym =>
              cases hAsym

/-- Relation plus distinction need not supply asymmetry. -/
theorem relation_and_distinction_without_asymmetry :
    exists A : Frame.{0, 0},
      Frame.HasRelation A /\
        Frame.HasDistinction A /\
        Not (Frame.HasAsymmetry A) := by
  exact Exists.intro relationDistinctionNoAsymFrame
    (And.intro relationDistinction_has_relation
      (And.intro relationDistinction_has_distinction relationDistinction_no_asymmetry))

theorem no_reach_b_a :
    Not (Reach relationDistinctionNoAsymFrame Two.b Two.a) := by
  intro h
  have hEq : Two.b = Two.a :=
    reach_from_sink_eq relationDistinctionNoAsymFrame
      (x := Two.b) (y := Two.a)
      (by
        intro z hz
        cases z <;> cases hz)
      h
  cases hEq

/-- Reach irreversibility can exist without an Alpha asymmetry witness. -/
theorem reach_irreversibility_without_asymmetry :
    exists A : Frame.{0, 0},
      exists x y : A.X,
        ReachIrreversible A x y /\ Not (Frame.HasAsymmetry A) := by
  exact Exists.intro relationDistinctionNoAsymFrame
    (Exists.intro Two.a
      (Exists.intro Two.b
        (And.intro
          (And.intro
            (Reach.step
              (A := relationDistinctionNoAsymFrame)
              (x := Two.a) (y := Two.b) (z := Two.b)
              trivial
              (Reach.refl (A := relationDistinctionNoAsymFrame) Two.b))
            no_reach_b_a)
          relationDistinction_no_asymmetry)))

/-- Asymmetry supplying relation and distinction is a typed consequence of the
Alpha frame, not a reverse implication. -/
theorem asymmetry_implies_relation_and_distinction
    (A : Frame)
    (h : Frame.HasAsymmetry A) :
    Frame.HasRelation A /\ Frame.HasDistinction A := by
  have hAlpha := Frame.hasAsymmetry_implies_alphaInstantiated A h
  exact And.intro hAlpha.left hAlpha.right.left

end Independence
end AlphaCore
