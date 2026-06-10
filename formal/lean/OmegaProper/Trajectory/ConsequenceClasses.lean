import OmegaProper.Trajectory.ConsequenceRelation

/-!
OmegaProper.Trajectory.ConsequenceClasses

Class-level guardrails for consequence-native separation.

A proposed class of fragments must be pairwise consequence-compatible unless
additional transitivity structure has been earned. Chain-connectedness is not
enough in a non-transitive consequence system.
-/

namespace OmegaProper
namespace Trajectory
namespace ConsequenceClasses

open ConsequenceRelation

universe w k o

/-- A class respects consequences when every pair of its members is compatible. -/
def ClassRespectsConsequences (S : ConsequenceSystem.{w, k, o})
    (member : S.Fragment -> Prop) : Prop :=
  forall x y,
    member x ->
    member y ->
    ConsequenceCompatible S x y

/-- A class has at least one member. -/
def ClassNonempty {S : ConsequenceSystem.{w, k, o}}
    (member : S.Fragment -> Prop) : Prop :=
  exists x, member x

/-- A class has at least two distinct members. -/
def ClassHasDistinctMembers {S : ConsequenceSystem.{w, k, o}}
    (member : S.Fragment -> Prop) : Prop :=
  exists x y,
    member x /\
    member y /\
    Not (x = y)

/--
Class nontriviality is kept separate from consequence-respect. Empty and
singleton classes may be valid, but they are not evidence of a multi-fragment
pattern.
-/
abbrev ClassNontrivial {S : ConsequenceSystem.{w, k, o}}
    (member : S.Fragment -> Prop) : Prop :=
  ClassHasDistinctMembers member

/-- A class contains a separated pair when two members are consequence-separated. -/
def ClassHasSeparatedPair (S : ConsequenceSystem.{w, k, o})
    (member : S.Fragment -> Prop) : Prop :=
  exists x y,
    member x /\
    member y /\
    ConsequenceSeparated S x y

/-- A class with distinct members is nonempty. -/
theorem classHasDistinctMembers_nonempty
    {S : ConsequenceSystem.{w, k, o}}
    {member : S.Fragment -> Prop}
    (h : ClassHasDistinctMembers member) :
    ClassNonempty member := by
  match h with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro _y hy =>
          exact Exists.intro x hy.left

/-- A class that respects consequences contains no separated pair. -/
theorem class_respects_no_separated_pair
    {S : ConsequenceSystem.{w, k, o}}
    {member : S.Fragment -> Prop}
    (h : ClassRespectsConsequences S member) :
    Not (ClassHasSeparatedPair S member) := by
  intro hsep
  match hsep with
  | Exists.intro x hx =>
      match hx with
      | Exists.intro y hy =>
          exact separated_not_compatible hy.right.right
            (h x y hy.left hy.right.left)

/-- If a class contains a separated pair, it does not respect consequences. -/
theorem separated_pair_blocks_class_respect
    {S : ConsequenceSystem.{w, k, o}}
    {member : S.Fragment -> Prop}
    (h : ClassHasSeparatedPair S member) :
    Not (ClassRespectsConsequences S member) := by
  intro hclass
  exact class_respects_no_separated_pair hclass h

/-- A binary chain relation contained in compatibility. -/
def ChainStepRespectsConsequences (S : ConsequenceSystem.{w, k, o})
    (step : S.Fragment -> S.Fragment -> Prop) : Prop :=
  forall {x y}, step x y -> ConsequenceCompatible S x y

/--
Under transitive consequence comparison, two compatible steps license endpoint
compatibility.
-/
theorem two_step_chain_compatible_of_compare_transitive
    {S : ConsequenceSystem.{w, k, o}}
    (htrans : CompareTransitive S)
    {x y z : S.Fragment}
    (hxy : ConsequenceCompatible S x y)
    (hyz : ConsequenceCompatible S y z) :
    ConsequenceCompatible S x z := by
  exact compatible_trans_of_compare_transitive htrans hxy hyz

/-! ## Toy class guardrails -/

def toyFullClass (x : ToyFragment) : Prop :=
  match x with
  | ToyFragment.a => True
  | ToyFragment.b => True
  | ToyFragment.c => True

def toyAdjacentStep : ToyFragment -> ToyFragment -> Prop
  | ToyFragment.a, ToyFragment.b => True
  | ToyFragment.b, ToyFragment.c => True
  | _, _ => False

theorem toy_full_class_has_separated_pair :
    ClassHasSeparatedPair nonTransitiveToySystem toyFullClass := by
  exists ToyFragment.a
  exists ToyFragment.c
  exact And.intro trivial (And.intro trivial toy_a_separated_c)

theorem toy_full_class_not_respects_consequences :
    Not (ClassRespectsConsequences nonTransitiveToySystem toyFullClass) := by
  exact separated_pair_blocks_class_respect toy_full_class_has_separated_pair

theorem toy_adjacent_step_respects_consequences :
    ChainStepRespectsConsequences nonTransitiveToySystem toyAdjacentStep := by
  intro x y hstep
  cases x <;> cases y <;> try cases hstep
  case a.b =>
    exact toy_a_compatible_b
  case b.c =>
    exact toy_b_compatible_c

theorem toy_chain_connected_class_can_fail_pairwise :
    ChainStepRespectsConsequences nonTransitiveToySystem toyAdjacentStep /\
    ClassHasSeparatedPair nonTransitiveToySystem toyFullClass := by
  exact And.intro toy_adjacent_step_respects_consequences toy_full_class_has_separated_pair

end ConsequenceClasses
end Trajectory
end OmegaProper
