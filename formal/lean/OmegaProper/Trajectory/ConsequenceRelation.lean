/-!
OmegaProper.Trajectory.ConsequenceRelation

Consequence-native separation for trajectory fragments.

The primary object here is not a quotient, representation, or label. It is the
relation carved by continuation consequences: a proposed identification is
blocked when an evaluated continuation context separates the consequences of
two fragments.
-/

namespace OmegaProper
namespace Trajectory
namespace ConsequenceRelation

universe w k o

/--
A consequence system records how fragments behave under continuation contexts.

`Compare` is context-indexed because different continuation tests may use
different consequence comparisons.
-/
structure ConsequenceSystem where
  Fragment : Type w
  Context : Type k
  Outcome : Type o
  consequence : Context -> Fragment -> Outcome
  Compare : Context -> Outcome -> Outcome -> Prop
  Evaluated : Context -> Prop

/--
Two fragments are compatible when every evaluated context compares their
consequences.
-/
def ConsequenceCompatible (S : ConsequenceSystem.{w, k, o})
    (x y : S.Fragment) : Prop :=
  forall c,
    S.Evaluated c ->
    S.Compare c (S.consequence c x) (S.consequence c y)

/--
Directional allowance: every evaluated context compares `x`'s consequence to
`y`'s consequence.

This is not yet a symmetric identification.
-/
abbrev ConsequenceAllows (S : ConsequenceSystem.{w, k, o}) :=
  ConsequenceCompatible S

/-- True identification requires both directed allowances. -/
def ConsequenceIdentifiable (S : ConsequenceSystem.{w, k, o})
    (x y : S.Fragment) : Prop :=
  ConsequenceAllows S x y /\ ConsequenceAllows S y x

/--
Two fragments are separated when some evaluated context refuses to compare their
consequences.
-/
def ConsequenceSeparated (S : ConsequenceSystem.{w, k, o})
    (x y : S.Fragment) : Prop :=
  exists c,
    S.Evaluated c /\
    Not (S.Compare c (S.consequence c x) (S.consequence c y))

/-- Directional separation: an evaluated context refuses comparison from `x` to `y`. -/
abbrev ConsequenceSeparates (S : ConsequenceSystem.{w, k, o}) :=
  ConsequenceSeparated S

/-- Symmetric merge-blocking separation: either direction is separated. -/
def ConsequenceMergeSeparated (S : ConsequenceSystem.{w, k, o})
    (x y : S.Fragment) : Prop :=
  ConsequenceSeparated S x y \/ ConsequenceSeparated S y x

/-- A proposed identification is allowed only when both directions compare. -/
abbrev AllowedIdentification (S : ConsequenceSystem.{w, k, o}) :=
  ConsequenceIdentifiable S

/-- A one-way allowance is not by itself an identification. -/
def OneWayAllowance (S : ConsequenceSystem.{w, k, o})
    (x y : S.Fragment) : Prop :=
  ConsequenceAllows S x y /\ Not (ConsequenceAllows S y x)

/--
A proposed identification relation respects consequences when it never
identifies fragments unless both directed allowances hold.
-/
def IdentificationRespectsConsequences (S : ConsequenceSystem.{w, k, o})
    (R : S.Fragment -> S.Fragment -> Prop) : Prop :=
  forall {x y}, R x y -> ConsequenceIdentifiable S x y

/-- A pair carries a consequence-bearing distinction when an evaluated context separates it. -/
abbrev ConsequenceBearingPair (S : ConsequenceSystem.{w, k, o}) :=
  ConsequenceSeparated S

/--
A pair carries merge-blocking consequence structure when either directed
comparison is separated. Use this for symmetric identification/merge claims.
-/
abbrev ConsequenceMergeBearingPair (S : ConsequenceSystem.{w, k, o}) :=
  ConsequenceMergeSeparated S

def HasEvaluatedContext (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists c, S.Evaluated c

def HasSeparatedPair (S : ConsequenceSystem.{w, k, o}) : Prop :=
  exists x y, ConsequenceSeparated S x y

/-- The evaluated consequence system collapses all fragments together. -/
def ConsequenceCollapsed (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall x y, ConsequenceCompatible S x y

def CompareReflexive (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall c z, S.Evaluated c -> S.Compare c z z

def CompareSymmetric (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall c z1 z2,
    S.Evaluated c ->
    S.Compare c z1 z2 ->
    S.Compare c z2 z1

def CompareTransitive (S : ConsequenceSystem.{w, k, o}) : Prop :=
  forall c z1 z2 z3,
    S.Evaluated c ->
    S.Compare c z1 z2 ->
    S.Compare c z2 z3 ->
    S.Compare c z1 z3

theorem compatible_not_separated
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceCompatible S x y) :
    Not (ConsequenceSeparated S x y) := by
  intro hsep
  match hsep with
  | Exists.intro c hc =>
      exact hc.right (h c hc.left)

theorem separated_not_compatible
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceSeparated S x y) :
    Not (ConsequenceCompatible S x y) := by
  intro hcompat
  exact compatible_not_separated hcompat h

theorem not_separated_implies_compatible
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : Not (ConsequenceSeparated S x y)) :
    ConsequenceCompatible S x y := by
  intro c hcEval
  classical
  by_cases hcCompare : S.Compare c (S.consequence c x) (S.consequence c y)
  case pos =>
    exact hcCompare
  case neg =>
    exact False.elim (h (Exists.intro c (And.intro hcEval hcCompare)))

theorem compatible_iff_not_separated
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment} :
    ConsequenceCompatible S x y <-> Not (ConsequenceSeparated S x y) := by
  constructor
  case mp =>
    exact compatible_not_separated
  case mpr =>
    exact not_separated_implies_compatible

theorem compatible_of_no_evaluated_contexts
    {S : ConsequenceSystem.{w, k, o}}
    (h : forall c, Not (S.Evaluated c))
    (x y : S.Fragment) :
    ConsequenceCompatible S x y := by
  intro c hcEval
  exact False.elim (h c hcEval)

theorem collapsed_of_no_evaluated_contexts
    {S : ConsequenceSystem.{w, k, o}}
    (h : forall c, Not (S.Evaluated c)) :
    ConsequenceCollapsed S := by
  intro x y
  exact compatible_of_no_evaluated_contexts h x y

theorem compatible_of_universal_compare
    {S : ConsequenceSystem.{w, k, o}}
    (h : forall c z1 z2,
      S.Evaluated c ->
      S.Compare c z1 z2)
    (x y : S.Fragment) :
    ConsequenceCompatible S x y := by
  intro c hcEval
  exact h c (S.consequence c x) (S.consequence c y) hcEval

theorem collapsed_of_universal_compare
    {S : ConsequenceSystem.{w, k, o}}
    (h : forall c z1 z2,
      S.Evaluated c ->
      S.Compare c z1 z2) :
    ConsequenceCollapsed S := by
  intro x y
  exact compatible_of_universal_compare h x y

theorem compatible_refl_of_compare_reflexive
    {S : ConsequenceSystem.{w, k, o}}
    (h : CompareReflexive S)
    (x : S.Fragment) :
    ConsequenceCompatible S x x := by
  intro c hcEval
  exact h c (S.consequence c x) hcEval

theorem compatible_symm_of_compare_symmetric
    {S : ConsequenceSystem.{w, k, o}}
    (h : CompareSymmetric S)
    {x y : S.Fragment}
    (hxy : ConsequenceCompatible S x y) :
    ConsequenceCompatible S y x := by
  intro c hcEval
  exact h c (S.consequence c x) (S.consequence c y) hcEval (hxy c hcEval)

theorem compatible_trans_of_compare_transitive
    {S : ConsequenceSystem.{w, k, o}}
    (h : CompareTransitive S)
    {x y z : S.Fragment}
    (hxy : ConsequenceCompatible S x y)
    (hyz : ConsequenceCompatible S y z) :
    ConsequenceCompatible S x z := by
  intro c hcEval
  exact h c
    (S.consequence c x)
    (S.consequence c y)
    (S.consequence c z)
    hcEval
    (hxy c hcEval)
    (hyz c hcEval)

theorem identifiable_left
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceIdentifiable S x y) :
    ConsequenceCompatible S x y := by
  exact h.left

theorem identifiable_right
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceIdentifiable S x y) :
    ConsequenceCompatible S y x := by
  exact h.right

theorem identifiable_symm
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceIdentifiable S x y) :
    ConsequenceIdentifiable S y x := by
  exact And.intro h.right h.left

theorem oneWayAllowance_not_identifiable
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : OneWayAllowance S x y) :
    Not (ConsequenceIdentifiable S x y) := by
  intro hId
  exact h.right hId.right

theorem separated_blocks_identifiable_left
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (hsep : ConsequenceSeparated S x y) :
    Not (ConsequenceIdentifiable S x y) := by
  intro hId
  exact separated_not_compatible hsep hId.left

theorem separated_blocks_identifiable_right
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (hsep : ConsequenceSeparated S y x) :
    Not (ConsequenceIdentifiable S x y) := by
  intro hId
  exact separated_not_compatible hsep hId.right

theorem mergeSeparated_blocks_identifiable
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceMergeSeparated S x y) :
    Not (ConsequenceIdentifiable S x y) := by
  intro hId
  cases h with
  | inl hsep =>
      exact separated_not_compatible hsep hId.left
  | inr hsep =>
      exact separated_not_compatible hsep hId.right

theorem mergeSeparated_symm
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceMergeSeparated S x y) :
    ConsequenceMergeSeparated S y x := by
  cases h with
  | inl hsep =>
      exact Or.inr hsep
  | inr hsep =>
      exact Or.inl hsep

theorem separated_implies_mergeSeparated
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceSeparated S x y) :
    ConsequenceMergeSeparated S x y := by
  exact Or.inl h

theorem reverseSeparated_implies_mergeSeparated
    {S : ConsequenceSystem.{w, k, o}} {x y : S.Fragment}
    (h : ConsequenceSeparated S y x) :
    ConsequenceMergeSeparated S x y := by
  exact Or.inr h

theorem separated_blocks_respected_identification
    {S : ConsequenceSystem.{w, k, o}}
    {R : S.Fragment -> S.Fragment -> Prop}
    (hR : IdentificationRespectsConsequences S R)
    {x y : S.Fragment}
    (hsep : ConsequenceSeparated S x y) :
    Not (R x y) := by
  intro hxy
  exact separated_blocks_identifiable_left hsep (hR hxy)

theorem identified_pair_not_separated
    {S : ConsequenceSystem.{w, k, o}}
    {R : S.Fragment -> S.Fragment -> Prop}
    (hR : IdentificationRespectsConsequences S R)
    {x y : S.Fragment}
    (hxy : R x y) :
    Not (ConsequenceSeparated S x y) := by
  exact compatible_not_separated (hR hxy).left

theorem identified_pair_merge_not_separated
    {S : ConsequenceSystem.{w, k, o}}
    {R : S.Fragment -> S.Fragment -> Prop}
    (hR : IdentificationRespectsConsequences S R)
    {x y : S.Fragment}
    (hxy : R x y) :
    Not (ConsequenceMergeSeparated S x y) := by
  intro hsep
  exact mergeSeparated_blocks_identifiable hsep (hR hxy)

/-! ## Non-transitive toy guardrail -/

inductive ToyFragment where
  | a
  | b
  | c
  deriving DecidableEq

inductive ToyContext where
  | ctx
  deriving DecidableEq

inductive ToyOutcome where
  | zero
  | one
  | two
  deriving DecidableEq

def toyConsequence : ToyContext -> ToyFragment -> ToyOutcome
  | ToyContext.ctx, ToyFragment.a => ToyOutcome.zero
  | ToyContext.ctx, ToyFragment.b => ToyOutcome.one
  | ToyContext.ctx, ToyFragment.c => ToyOutcome.two

def toyCompare : ToyContext -> ToyOutcome -> ToyOutcome -> Prop
  | ToyContext.ctx, ToyOutcome.zero, ToyOutcome.zero => True
  | ToyContext.ctx, ToyOutcome.zero, ToyOutcome.one => True
  | ToyContext.ctx, ToyOutcome.zero, ToyOutcome.two => False
  | ToyContext.ctx, ToyOutcome.one, ToyOutcome.zero => True
  | ToyContext.ctx, ToyOutcome.one, ToyOutcome.one => True
  | ToyContext.ctx, ToyOutcome.one, ToyOutcome.two => True
  | ToyContext.ctx, ToyOutcome.two, ToyOutcome.zero => False
  | ToyContext.ctx, ToyOutcome.two, ToyOutcome.one => True
  | ToyContext.ctx, ToyOutcome.two, ToyOutcome.two => True

def nonTransitiveToySystem : ConsequenceSystem where
  Fragment := ToyFragment
  Context := ToyContext
  Outcome := ToyOutcome
  consequence := toyConsequence
  Compare := toyCompare
  Evaluated := fun _ => True

theorem toy_compare_zero_one :
    nonTransitiveToySystem.Compare ToyContext.ctx ToyOutcome.zero ToyOutcome.one := by
  trivial

theorem toy_compare_one_two :
    nonTransitiveToySystem.Compare ToyContext.ctx ToyOutcome.one ToyOutcome.two := by
  trivial

theorem toy_not_compare_zero_two :
    Not (nonTransitiveToySystem.Compare ToyContext.ctx ToyOutcome.zero ToyOutcome.two) := by
  intro h
  exact h

theorem toy_a_compatible_b :
    ConsequenceCompatible nonTransitiveToySystem ToyFragment.a ToyFragment.b := by
  intro c _hEval
  cases c
  trivial

theorem toy_b_compatible_c :
    ConsequenceCompatible nonTransitiveToySystem ToyFragment.b ToyFragment.c := by
  intro c _hEval
  cases c
  trivial

theorem toy_a_separated_c :
    ConsequenceSeparated nonTransitiveToySystem ToyFragment.a ToyFragment.c := by
  exists ToyContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    exact toy_not_compare_zero_two

theorem toy_a_not_compatible_c :
    Not (ConsequenceCompatible nonTransitiveToySystem ToyFragment.a ToyFragment.c) := by
  exact separated_not_compatible toy_a_separated_c

theorem connected_chain_does_not_license_endpoint_identification :
    ConsequenceCompatible nonTransitiveToySystem ToyFragment.a ToyFragment.b /\
    ConsequenceCompatible nonTransitiveToySystem ToyFragment.b ToyFragment.c /\
    ConsequenceSeparated nonTransitiveToySystem ToyFragment.a ToyFragment.c := by
  exact And.intro toy_a_compatible_b (And.intro toy_b_compatible_c toy_a_separated_c)

theorem toy_compare_not_transitive :
    Not (CompareTransitive nonTransitiveToySystem) := by
  intro htrans
  have h02 := htrans ToyContext.ctx
    ToyOutcome.zero
    ToyOutcome.one
    ToyOutcome.two
    trivial
    toy_compare_zero_one
    toy_compare_one_two
  exact toy_not_compare_zero_two h02

end ConsequenceRelation
end Trajectory
end OmegaProper
