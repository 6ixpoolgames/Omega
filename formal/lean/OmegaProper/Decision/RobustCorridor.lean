import OmegaProper.Decision.License
import OmegaProper.Trajectory.PredicateFixpoint

/-!
OmegaProper.Decision.RobustCorridor

Controlled robust-continuation corridor for the ODT0 floor.

This module instantiates the abstract `Corridor` predicate consumed by
`LicenseVia` as a greatest fixed point of a controlled robust-predecessor
operator. The content remains conditional on:

* a declared state-local requirement;
* a declared action-admissibility predicate;
* the concrete possibilistic transition relation.

It does not define value, agency, identity, moral standing, or Omega.
-/

namespace OmegaProper
namespace Decision

open Trajectory.PredicateFixpoint

universe u v

/--
An action robustly keeps a candidate set when it is allowed, enabled, and every
concrete successor remains in the candidate set.
-/
def ActionRobustKeeps
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (S : D.State -> Prop)
    (x : D.State) (a : D.Action) : Prop :=
  Allowed x a /\ ActionEnabled D x a /\ forall y, D.Step x a y -> S y

/-- Controlled robust predecessor for a candidate set. -/
def RobustPre
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (S : D.State -> Prop)
    (x : D.State) : Prop :=
  exists a, ActionRobustKeeps D Allowed S x a

/--
Robust continuation operator.

`Requirement` is intentionally explicit. ODT0 proves consequences conditional
on this state-local requirement; it does not derive `Requirement` from Alpha or
from value.
-/
def robustCorridorOp
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop)
    (S : D.State -> Prop) :
    D.State -> Prop :=
  fun x =>
    D.Constraint x /\
    Requirement x /\
    RobustPre D Allowed S x

/-- Greatest controlled robust-continuation corridor. -/
def RobustCorridor
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop) :
    D.State -> Prop :=
  gfp (robustCorridorOp D Allowed Requirement)

theorem robustCorridorOp_mono
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop) :
    Mono (robustCorridorOp D Allowed Requirement) := by
  intro p q hpq x hx
  rcases hx with ⟨hConstraint, hReq, a, hAllowed, hEnabled, hSucc⟩
  exact ⟨hConstraint, hReq, a, hAllowed, hEnabled,
    (by
      intro y hStep
      exact hpq y (hSucc y hStep))⟩

theorem robustCorridor_fixed
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop) :
    PSub (RobustCorridor D Allowed Requirement)
        (robustCorridorOp D Allowed Requirement
          (RobustCorridor D Allowed Requirement)) /\
      PSub
        (robustCorridorOp D Allowed Requirement
          (RobustCorridor D Allowed Requirement))
        (RobustCorridor D Allowed Requirement) := by
  exact gfp_fixed (robustCorridorOp_mono D Allowed Requirement)

theorem robustCorridor_sub_constraint
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop) :
    PSub (RobustCorridor D Allowed Requirement) D.Constraint := by
  intro x hx
  exact ((robustCorridor_fixed D Allowed Requirement).left x hx).left

theorem robustCorridor_sub_requirement
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop) :
    PSub (RobustCorridor D Allowed Requirement) Requirement := by
  intro x hx
  exact ((robustCorridor_fixed D Allowed Requirement).left x hx).right.left

theorem robustCorridor_has_action
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop)
    {x : D.State}
    (hx : RobustCorridor D Allowed Requirement x) :
    exists a,
      Allowed x a /\
      ActionEnabled D x a /\
      ActionCorridorSafe D (RobustCorridor D Allowed Requirement) x a := by
  exact ((robustCorridor_fixed D Allowed Requirement).left x hx).right.right

theorem robustCorridor_action_safe
    (D : DecisionStructure)
    (Allowed : D.State -> D.Action -> Prop)
    (Requirement : D.State -> Prop)
    {x : D.State}
    (hx : RobustCorridor D Allowed Requirement x) :
    exists a,
      ActionRobustKeeps D Allowed
        (RobustCorridor D Allowed Requirement) x a := by
  exact robustCorridor_has_action D Allowed Requirement hx

/--
If a state is inside the robust corridor, then some allowed action can satisfy
the ODT0 corridor gate for that corridor. Supplying a certified route and the
quotient side condition turns that action into a `LicenseVia` certificate.
-/
theorem robustCorridor_supplies_license
    {D : DecisionStructure}
    {Allowed : D.State -> D.Action -> Prop}
    {Requirement : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State}
    (hx : RobustCorridor D Allowed Requirement x)
    (J : CertifiedJustification)
    (hAvail : Available J)
    (hQuotients : quotientsCertified) :
    exists a,
      Allowed x a /\
      LicensedVia D (RobustCorridor D Allowed Requirement)
        Available quotientsCertified x a := by
  rcases robustCorridor_has_action D Allowed Requirement hx with
    ⟨a, hAllowed, hEnabled, hSafe⟩
  exact ⟨a, hAllowed, Nonempty.intro
    { justification := J
      route_available := hAvail
      enabled := hEnabled
      corridor_safe := hSafe
      quotients_certified := hQuotients }⟩

/--
An action with any concrete successor outside the robust corridor fails the
ODT0 corridor gate.
-/
theorem action_with_exit_not_corridorSafe
    {D : DecisionStructure}
    {Allowed : D.State -> D.Action -> Prop}
    {Requirement : D.State -> Prop}
    {x : D.State} {a : D.Action}
    (hExit : exists y,
      D.Step x a y /\ Not (RobustCorridor D Allowed Requirement y)) :
    Not (ActionCorridorSafe D (RobustCorridor D Allowed Requirement) x a) := by
  intro hSafe
  rcases hExit with ⟨y, hStep, hNot⟩
  exact hNot (hSafe y hStep)

/-- Therefore an action with a corridor exit cannot be licensed on that corridor. -/
theorem action_with_exit_not_licensed
    {D : DecisionStructure}
    {Allowed : D.State -> D.Action -> Prop}
    {Requirement : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State} {a : D.Action}
    (hExit : exists y,
      D.Step x a y /\ Not (RobustCorridor D Allowed Requirement y)) :
    Not
      (LicensedVia D (RobustCorridor D Allowed Requirement)
        Available quotientsCertified x a) := by
  intro hLicense
  rcases hLicense with ⟨cert⟩
  exact action_with_exit_not_corridorSafe hExit cert.corridor_safe

end Decision
end OmegaProper
