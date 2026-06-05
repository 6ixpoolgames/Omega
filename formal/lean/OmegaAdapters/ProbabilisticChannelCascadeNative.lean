import OmegaAdapters.ProbabilisticChannelNative

/-!
OmegaAdapters.ProbabilisticChannelCascadeNative

Alpha-native finite probabilistic channel cascade layer.

The cascade layer uses path-level natural weights. Its first- and second-stage
error masses are measured over the same finite path ensemble as the composite
decoder error. They are not standalone independently normalized stage errors.
-/

namespace OmegaAdapters
namespace ProbabilisticChannelNative

universe u v w z q

/-- Natural-weight channel composition by finite path summation. -/
def chanComp
    {X : Type u} {Y : Type v} {Z : Type w}
    [Fintype Y]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat) : X -> Z -> Nat :=
  fun x z => Finset.univ.sum fun y => K x y * L y z

/-- Weight of one finite cascade path `x -> y -> z`. -/
def tripleWeight
    {X : Type u} {Y : Type v} {Z : Type w}
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (x : X) (y : Y) (z : Z) : Nat :=
  pi x * K x y * L y z

/-- Total natural-weight mass of the finite cascade path ensemble. -/
def cascadeTotalMass
    {X : Type u} {Y : Type v} {Z : Type w}
    [Fintype X] [Fintype Y] [Fintype Z]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat) : Nat :=
  Finset.univ.sum fun x =>
    Finset.univ.sum fun y =>
      Finset.univ.sum fun z =>
        tripleWeight K L pi x y z

/-- Composite decoder error over the finite cascade path ensemble. -/
def cascadeCompositeErrorMass
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (F : Z -> LF)
    (dec1 : LE -> LD)
    (dec2 : LF -> LE) : Nat :=
  Finset.univ.sum fun x =>
    Finset.univ.sum fun y =>
      Finset.univ.sum fun z =>
        if dec1 (dec2 (F z)) = D x then 0 else tripleWeight K L pi x y z

/-- First-stage decoder error, lifted to the cascade path ensemble. -/
def cascadeFirstErrorMass
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (dec1 : LE -> LD) : Nat :=
  Finset.univ.sum fun x =>
    Finset.univ.sum fun y =>
      Finset.univ.sum fun z =>
        if dec1 (E y) = D x then 0 else tripleWeight K L pi x y z

/-- Second-stage decoder error, lifted to the cascade path ensemble. -/
def cascadeSecondErrorMass
    {X : Type u} {Y : Type v} {Z : Type w}
    {LE : Type q} {LF : Type}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LE]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (E : Y -> LE)
    (F : Z -> LF)
    (dec2 : LF -> LE) : Nat :=
  Finset.univ.sum fun x =>
    Finset.univ.sum fun y =>
      Finset.univ.sum fun z =>
        if dec2 (F z) = E y then 0 else tripleWeight K L pi x y z

/-- If the composed decoder fails at a path, at least one stage decoder fails
at that path. -/
lemma composite_failure_implies_stage_failure
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    {D : X -> LD}
    {E : Y -> LE}
    {F : Z -> LF}
    {dec1 : LE -> LD}
    {dec2 : LF -> LE}
    (x : X) (y : Y) (z : Z)
    (h : Not (dec1 (dec2 (F z)) = D x)) :
    Not (dec1 (E y) = D x) \/ Not (dec2 (F z) = E y) := by
  by_cases hSecond : dec2 (F z) = E y
  case pos =>
    left
    intro hFirst
    apply h
    rw [hSecond, hFirst]
  case neg =>
    right
    exact hSecond

/-- Pointwise finite union bound for one cascade path. -/
lemma cascade_pointwise_composite_error_le_stage_errors
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    [DecidableEq LD] [DecidableEq LE]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (F : Z -> LF)
    (dec1 : LE -> LD)
    (dec2 : LF -> LE)
    (x : X) (y : Y) (z : Z) :
    (if dec1 (dec2 (F z)) = D x then 0 else tripleWeight K L pi x y z)
      <=
    (if dec1 (E y) = D x then 0 else tripleWeight K L pi x y z)
      +
    (if dec2 (F z) = E y then 0 else tripleWeight K L pi x y z) := by
  by_cases hComp : dec1 (dec2 (F z)) = D x
  case pos =>
    simp [hComp]
  case neg =>
    have hStage :=
      composite_failure_implies_stage_failure
        (D := D) (E := E) (F := F) (dec1 := dec1) (dec2 := dec2)
        x y z hComp
    cases hStage with
    | inl hFirst =>
        simp [hComp, hFirst]
    | inr hSecond =>
        simp [hComp, hSecond]

/-- Finite cascade union bound: composite decoder failure is bounded by the sum
of first-stage and second-stage decoder failures over the same weighted path
ensemble. -/
theorem cascade_composite_error_le_stage_errors
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LD] [DecidableEq LE]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (E : Y -> LE)
    (F : Z -> LF)
    (dec1 : LE -> LD)
    (dec2 : LF -> LE) :
    cascadeCompositeErrorMass K L pi D F dec1 dec2
      <=
    cascadeFirstErrorMass K L pi D E dec1
      +
    cascadeSecondErrorMass K L pi E F dec2 := by
  unfold cascadeCompositeErrorMass cascadeFirstErrorMass cascadeSecondErrorMass
  rw [<- Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro x _hx
  rw [<- Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro y _hy
  rw [<- Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro z _hz
  exact
    cascade_pointwise_composite_error_le_stage_errors
      K L pi D E F dec1 dec2 x y z

/-- Cross-multiplied finite error threshold. `num / den` is the intended error
upper bound. -/
def ErrorMassAtMost (err total : Nat) (num den : Nat) : Prop :=
  den * err <= num * total

/-- Same-denominator threshold form of the finite cascade union bound. -/
theorem cascade_error_bound_same_denominator
    {errComp errFirst errSecond total num1 num2 den : Nat}
    (hcomp : errComp <= errFirst + errSecond)
    (h1 : ErrorMassAtMost errFirst total num1 den)
    (h2 : ErrorMassAtMost errSecond total num2 den) :
    ErrorMassAtMost errComp total (num1 + num2) den := by
  unfold ErrorMassAtMost at *
  calc
    den * errComp <= den * (errFirst + errSecond) :=
      Nat.mul_le_mul_left den hcomp
    _ = den * errFirst + den * errSecond := by
      rw [Nat.left_distrib]
    _ <= num1 * total + num2 * total :=
      Nat.add_le_add h1 h2
    _ = (num1 + num2) * total := by
      rw [Nat.right_distrib]

/-- Cascade path-ensemble total mass agrees with the total mass of the composed
natural-weight channel. -/
theorem cascadeTotalMass_eq_totalMass_chanComp
    {X : Type u} {Y : Type v} {Z : Type w}
    [Fintype X] [Fintype Y] [Fintype Z]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat) :
    cascadeTotalMass K L pi = totalMass (chanComp K L) pi := by
  unfold cascadeTotalMass totalMass rowSum chanComp tripleWeight
  apply Finset.sum_congr rfl
  intro x _hx
  calc
    (Finset.univ.sum fun y =>
      Finset.univ.sum fun z => pi x * K x y * L y z)
        =
      Finset.univ.sum fun z =>
        Finset.univ.sum fun y => pi x * K x y * L y z := by
          rw [Finset.sum_comm]
    _ =
      Finset.univ.sum fun z => pi x * Finset.univ.sum fun y => K x y * L y z := by
          apply Finset.sum_congr rfl
          intro z _hz
          rw [Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro y _hy
          rw [Nat.mul_assoc]
    _ = pi x * Finset.univ.sum fun z =>
          Finset.univ.sum fun y => K x y * L y z := by
          rw [Finset.mul_sum]

/-- Cascade composite error mass agrees with the ordinary error mass of the
composed natural-weight channel and composed decoder. -/
theorem cascadeCompositeErrorMass_eq_errorMass_chanComp
    {X : Type u} {Y : Type v} {Z : Type w}
    {LD : Type z} {LE : Type q} {LF : Type}
    [Fintype X] [Fintype Y] [Fintype Z] [DecidableEq LD]
    (K : X -> Y -> Nat)
    (L : Y -> Z -> Nat)
    (pi : X -> Nat)
    (D : X -> LD)
    (F : Z -> LF)
    (dec1 : LE -> LD)
    (dec2 : LF -> LE) :
    cascadeCompositeErrorMass K L pi D F dec1 dec2 =
      errorMass (chanComp K L) pi D F (fun fLabel => dec1 (dec2 fLabel)) := by
  unfold cascadeCompositeErrorMass errorMass chanComp tripleWeight
  apply Finset.sum_congr rfl
  intro x _hx
  calc
    (Finset.univ.sum fun y =>
      Finset.univ.sum fun z =>
        if dec1 (dec2 (F z)) = D x then 0 else pi x * K x y * L y z)
        =
      Finset.univ.sum fun z =>
        Finset.univ.sum fun y =>
          if dec1 (dec2 (F z)) = D x then 0 else pi x * K x y * L y z := by
        rw [Finset.sum_comm]
    _ =
      Finset.univ.sum fun z =>
        if dec1 (dec2 (F z)) = D x then 0
        else pi x * Finset.univ.sum fun y => K x y * L y z := by
        apply Finset.sum_congr rfl
        intro z _hz
        by_cases hCorrect : dec1 (dec2 (F z)) = D x
        case pos =>
          simp [hCorrect]
        case neg =>
          simp [hCorrect, Finset.mul_sum, Nat.mul_assoc]
    _ =
      pi x * Finset.univ.sum fun z =>
        if dec1 (dec2 (F z)) = D x then 0
        else Finset.univ.sum fun y => K x y * L y z := by
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro z _hz
        by_cases hCorrect : dec1 (dec2 (F z)) = D x
        case pos =>
          simp [hCorrect]
        case neg =>
          simp [hCorrect]

end ProbabilisticChannelNative
end OmegaAdapters
