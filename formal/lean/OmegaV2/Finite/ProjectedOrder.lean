import Mathlib.Logic.Relation
import Mathlib.Order.Antisymmetrization

/-!
OmegaV2.Finite.ProjectedOrder

Projection-relative reachability over a generic ordered index. The file
assumes no finiteness, totality, determinism, persistence, or value predicate.
-/

namespace OmegaV2
namespace Finite

universe u v

/-- A support-level transition relation. -/
structure TransitionSystem (State : Type u) where
  step : State -> State -> Prop

/-- A projection into a declared ordered index. -/
structure OrderedProjection (State : Type u) (Index : Type v) where
  level : State -> Index

variable
    {State : Type u}
    {Index : Type v}
    [Preorder Index]
    (system : TransitionSystem State)
    (projection : OrderedProjection State Index)

/-- A transition retained by the declared nondecreasing projection view. -/
def ProjectedStep (source target : State) : Prop :=
  system.step source target /\
    projection.level source <= projection.level target

/-- Reflexive-transitive reachability through projected steps. -/
def ProjectedReach (source target : State) : Prop :=
  Relation.ReflTransGen (ProjectedStep system projection) source target

/-- Mutual projected reachability, the kernel of antisymmetrization. -/
def MutualProjectedReach (left right : State) : Prop :=
  ProjectedReach system projection left right /\
    ProjectedReach system projection right left

namespace ProjectedReach

theorem refl (state : State) :
    ProjectedReach system projection state state :=
  Relation.ReflTransGen.refl

theorem trans {left middle right : State}
    (hLeft : ProjectedReach system projection left middle)
    (hRight : ProjectedReach system projection middle right) :
    ProjectedReach system projection left right :=
  Relation.ReflTransGen.trans hLeft hRight

theorem level_mono {source target : State}
    (hReach : ProjectedReach system projection source target) :
    projection.level source <= projection.level target := by
  induction hReach with
  | refl =>
      exact le_rfl
  | tail hPrefix hStep ih =>
      exact ih.trans hStep.2

end ProjectedReach

namespace MutualProjectedReach

theorem refl (state : State) :
    MutualProjectedReach system projection state state :=
  ⟨ProjectedReach.refl system projection state,
    ProjectedReach.refl system projection state⟩

theorem symm {left right : State}
    (hMutual : MutualProjectedReach system projection left right) :
    MutualProjectedReach system projection right left :=
  ⟨hMutual.2, hMutual.1⟩

theorem trans {left middle right : State}
    (hLeft : MutualProjectedReach system projection left middle)
    (hRight : MutualProjectedReach system projection middle right) :
    MutualProjectedReach system projection left right :=
  ⟨ProjectedReach.trans system projection hLeft.1 hRight.1,
    ProjectedReach.trans system projection hRight.2 hLeft.2⟩

end MutualProjectedReach

/-- Projected reachability is a preorder on the original state type. -/
instance projectedReachIsPreorder :
    IsPreorder State (ProjectedReach system projection) where
  refl := fun state => ProjectedReach.refl system projection state
  trans := fun _left _middle _right =>
    ProjectedReach.trans system projection

/-- The original state type equipped with projected reach as its preorder. -/
abbrev ProjectedPreorder
    (_system : TransitionSystem State)
    (_projection : OrderedProjection State Index) :
    Type u := State

instance projectedPreorder :
    Preorder (ProjectedPreorder system projection) where
  le := ProjectedReach system projection
  le_refl := ProjectedReach.refl system projection
  le_trans := fun _left _middle _right =>
    ProjectedReach.trans system projection

/--
The standard antisymmetrization quotients states by mutual projected
reachability and supplies the induced partial order.
-/
abbrev ProjectedOrder : Type u :=
  Antisymmetrization
    (ProjectedPreorder system projection)
    (· <= ·)

noncomputable instance projectedOrderPartialOrder :
    PartialOrder (ProjectedOrder system projection) :=
  inferInstance

theorem mutualProjectedReach_is_equivalence :
    Equivalence (MutualProjectedReach system projection) :=
  ⟨MutualProjectedReach.refl system projection,
    MutualProjectedReach.symm system projection,
    MutualProjectedReach.trans system projection⟩

end Finite
end OmegaV2
