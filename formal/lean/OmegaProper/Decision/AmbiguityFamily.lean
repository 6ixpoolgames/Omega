import Mathlib.Data.Fintype.Basic
import OmegaProper.Decision.RobustCorridor

/-!
OmegaProper.Decision.AmbiguityFamily

Batch A' for the containment theorem direction.

An ambiguity family is represented as a transformation into the existing
`RobustCorridor` surface, not as a second fixed-point theory. The family is
merged into one possibilistic decision structure whose step relation is the
union of all model steps, while admissible actions are strengthened to require
enabledness in every model.

This file does not define value, agency, identity, moral standing, stochastic
risk, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace AmbiguityFamily

open Trajectory.PredicateFixpoint

universe u v w

/--
A finite nonempty ambiguity family over shared states, actions, and constraint.
Only the transition relation varies by model.
-/
structure AmbFamily (State : Type u) (Action : Type v) where
  Model : Type w
  modelFinite : Fintype Model
  modelNonempty : Nonempty Model
  Step : Model -> State -> Action -> State -> Prop
  Constraint : State -> Prop

instance (F : AmbFamily State Action) : Fintype F.Model :=
  F.modelFinite

instance (F : AmbFamily State Action) : Nonempty F.Model :=
  F.modelNonempty

/-- The merged possibilistic system: a step exists if some model permits it. -/
def mergedDecision (F : AmbFamily State Action) : DecisionStructure where
  State := State
  Action := Action
  Step := fun x a y => exists i : F.Model, F.Step i x a y
  Constraint := F.Constraint

/-- The single-model decision structure for one model in the family. -/
def perModelDecision (F : AmbFamily State Action) (i : F.Model) :
    DecisionStructure where
  State := State
  Action := Action
  Step := F.Step i
  Constraint := F.Constraint

/--
Allowedness strengthened by family-wide enabledness.

This is the anti-sprawl move: ambiguity is folded into the action predicate of
the merged ordinary robust corridor.
-/
def familyEnabledAllowed
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop) :
    State -> Action -> Prop :=
  fun x a => Allowed x a /\ forall i : F.Model, exists y, F.Step i x a y

/-- Shared-action robust keeping over an ambiguity family. -/
def ActionRobustKeepsAmb
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (S : State -> Prop)
    (x : State) (a : Action) : Prop :=
  Allowed x a /\
    (forall i : F.Model, exists y, F.Step i x a y) /\
    (forall i y, F.Step i x a y -> S y)

/--
Family reduction lemma at action level: shared-action robust keeping for the
family is equivalent to ordinary robust keeping in the merged system with the
strengthened allowedness predicate.
-/
theorem actionRobustKeepsAmb_iff_merged
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (S : State -> Prop)
    (x : State) (a : Action) :
    ActionRobustKeepsAmb F Allowed S x a <->
      ActionRobustKeeps (mergedDecision F)
        (familyEnabledAllowed F Allowed) S x a := by
  constructor
  · intro hAmb
    rcases hAmb with ⟨hAllowed, hEnabledAll, hSafeAll⟩
    constructor
    · exact ⟨hAllowed, hEnabledAll⟩
    constructor
    · rcases F.modelNonempty with ⟨i⟩
      rcases hEnabledAll i with ⟨y, hStep⟩
      exact ⟨y, ⟨i, hStep⟩⟩
    · intro y hStep
      rcases hStep with ⟨i, hModelStep⟩
      exact hSafeAll i y hModelStep
  · intro hMerged
    rcases hMerged with ⟨hAllowedEnabled, _hMergedEnabled, hSafeMerged⟩
    rcases hAllowedEnabled with ⟨hAllowed, hEnabledAll⟩
    exact ⟨hAllowed, hEnabledAll, by
      intro i y hStep
      exact hSafeMerged y ⟨i, hStep⟩⟩

/--
Shared-action robust viability kernel for an ambiguity family.

This is definitionally the robust corridor of the merged system. No second
fixed-point theory is introduced.
-/
def RVK
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    State -> Prop :=
  RobustCorridor (mergedDecision F) (familyEnabledAllowed F Allowed)
    Requirement

/-- The family RVK is exactly the ordinary robust corridor of the merged system. -/
theorem rvk_eq_merged_robustCorridor
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    RVK F Allowed Requirement =
      RobustCorridor (mergedDecision F) (familyEnabledAllowed F Allowed)
        Requirement := by
  rfl

theorem rvk_sub_constraint
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    PSub (RVK F Allowed Requirement) F.Constraint := by
  exact robustCorridor_sub_constraint
    (mergedDecision F) (familyEnabledAllowed F Allowed) Requirement

theorem rvk_sub_requirement
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    PSub (RVK F Allowed Requirement) Requirement := by
  exact robustCorridor_sub_requirement
    (mergedDecision F) (familyEnabledAllowed F Allowed) Requirement

/-- Every RVK state has one action that is enabled and safe in every model. -/
theorem rvk_has_shared_action
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    {x : State}
    (hx : RVK F Allowed Requirement x) :
    exists a,
      ActionRobustKeepsAmb F Allowed (RVK F Allowed Requirement) x a := by
  rcases robustCorridor_action_safe
      (mergedDecision F) (familyEnabledAllowed F Allowed)
      Requirement hx with
    ⟨a, hKeep⟩
  exact ⟨a,
    (actionRobustKeepsAmb_iff_merged F Allowed
      (RVK F Allowed Requirement) x a).mpr hKeep⟩

/--
RVK is contained in every per-model robust corridor.

This is the formal upper-bound lemma: the shared-action kernel is below the
intersection of per-model kernels.
-/
theorem rvk_sub_perModelCorridor
    (F : AmbFamily State Action)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop)
    (i : F.Model) :
    PSub (RVK F Allowed Requirement)
      (RobustCorridor (perModelDecision F i) Allowed Requirement) := by
  apply postfixed_le_gfp
  intro x hx
  have hConstraint : F.Constraint x :=
    rvk_sub_constraint F Allowed Requirement x hx
  have hRequirement : Requirement x :=
    rvk_sub_requirement F Allowed Requirement x hx
  rcases rvk_has_shared_action F Allowed Requirement hx with
    ⟨a, hAllowed, hEnabledAll, hSafeAll⟩
  exact ⟨hConstraint, hRequirement, a, hAllowed,
    hEnabledAll i,
    (by
      intro y hStep
      exact hSafeAll i y hStep)⟩

/--
Embedding of one ambiguity family into another over the same state/action
types. Dynamics and constraints are pointwise preserved/reflected.
-/
structure FamilyEmbeds
    (Fsmall Fbig : AmbFamily State Action) where
  embed : Fsmall.Model -> Fbig.Model
  step_iff : forall i x a y,
    Fsmall.Step i x a y <-> Fbig.Step (embed i) x a y
  constraint_iff : forall x, Fsmall.Constraint x <-> Fbig.Constraint x

/--
Adding models narrows the shared-action robust kernel.

This is stated through an explicit embedding from the smaller family into the
larger family.
-/
theorem rvk_mono_family
    {Fsmall Fbig : AmbFamily State Action}
    (hEmbed : FamilyEmbeds Fsmall Fbig)
    (Allowed : State -> Action -> Prop)
    (Requirement : State -> Prop) :
    PSub (RVK Fbig Allowed Requirement)
      (RVK Fsmall Allowed Requirement) := by
  apply postfixed_le_gfp
  intro x hx
  have hConstraintBig : Fbig.Constraint x :=
    rvk_sub_constraint Fbig Allowed Requirement x hx
  have hConstraintSmall : Fsmall.Constraint x :=
    (hEmbed.constraint_iff x).mpr hConstraintBig
  have hRequirement : Requirement x :=
    rvk_sub_requirement Fbig Allowed Requirement x hx
  rcases rvk_has_shared_action Fbig Allowed Requirement hx with
    ⟨a, hAllowed, hEnabledBig, hSafeBig⟩
  have hEnabledSmall :
      forall i : Fsmall.Model, exists y, Fsmall.Step i x a y := by
    intro i
    rcases hEnabledBig (hEmbed.embed i) with ⟨y, hStepBig⟩
    exact ⟨y, (hEmbed.step_iff i x a y).mpr hStepBig⟩
  have hSafeSmall :
      forall i y, Fsmall.Step i x a y -> RVK Fbig Allowed Requirement y := by
    intro i y hStepSmall
    exact hSafeBig (hEmbed.embed i) y
      ((hEmbed.step_iff i x a y).mp hStepSmall)
  have hAmbSmall :
      ActionRobustKeepsAmb Fsmall Allowed
        (RVK Fbig Allowed Requirement) x a := by
    exact And.intro hAllowed (And.intro hEnabledSmall hSafeSmall)
  have hKeepSmall :
      ActionRobustKeeps (mergedDecision Fsmall)
        (familyEnabledAllowed Fsmall Allowed)
        (RVK Fbig Allowed Requirement) x a := by
    exact (actionRobustKeepsAmb_iff_merged Fsmall Allowed
      (RVK Fbig Allowed Requirement) x a).mp hAmbSmall
  exact And.intro hConstraintSmall
    (And.intro hRequirement (Exists.intro a hKeepSmall))

end AmbiguityFamily
end Decision
end OmegaProper
