/-!
OmegaProper.Decision.License

Minimal decision-floor interface.

This module is intentionally a thin consumer of the lower stack. It does not
construct the controlled viability kernel, certify presentations, define value,
define agency, or choose actions. It only records the shape of an ODT0-style
license:

* a certified justification whose abstract fact reflects to a concrete fact;
* a concrete action that keeps every successor inside a declared corridor;
* a quotient/identification side condition supplied as an explicit proposition.

The corridor predicate is treated as an already certified object. In the full
stack it should be instantiated by the controlled viability kernel or by a
reflected certified presentation of that kernel.
-/

namespace OmegaProper
namespace Decision

universe u v w

/-- A finite or infinite possibilistic decision structure. -/
structure DecisionStructure where
  State : Type u
  Action : Type v
  Step : State -> Action -> State -> Prop
  Constraint : State -> Prop

/--
A certified justification for one declared fact.

`abstractFact` is the fact asserted on a presentation or other registered
surface. `concreteFact` is the concrete fact needed for decision use.
`reflects` is the load-bearing direction: abstract truth implies concrete
truth. Without this field, the justification is not decision-usable.
-/
structure CertifiedJustification where
  abstractFact : Prop
  concreteFact : Prop
  abstract_holds : abstractFact
  reflects : abstractFact -> concreteFact

theorem CertifiedJustification.concrete_holds
    (J : CertifiedJustification) : J.concreteFact :=
  J.reflects J.abstract_holds

/-- A phantom abstract fact cannot be reflected into a false concrete fact. -/
theorem no_reflected_fact_of_abstract_true_concrete_false
    {abstract concrete : Prop}
    (hAbstract : abstract)
    (hConcreteFalse : Not concrete) :
    Not (abstract -> concrete) := by
  intro hReflect
  exact hConcreteFalse (hReflect hAbstract)

/-- An action is enabled when it has at least one concrete successor. -/
def ActionEnabled
    (D : DecisionStructure) (x : D.State) (a : D.Action) : Prop :=
  exists y, D.Step x a y

/--
Concrete corridor safety for an action.

This is the ODT0 demonic/worst-case clause: every concrete successor of the
action must lie inside the declared corridor.
-/
def ActionCorridorSafe
    (D : DecisionStructure) (Corridor : D.State -> Prop)
    (x : D.State) (a : D.Action) : Prop :=
  forall y, D.Step x a y -> Corridor y

/--
A license routed through an available certified justification.

`Available` represents the current register of usable certified routes. Adding
new certified presentations/routes is modeled by weakening this predicate.
`quotientsCertified` is an explicit side condition for quotient or decision-node
identifications used by the justification.
-/
structure LicenseVia
    (D : DecisionStructure)
    (Corridor : D.State -> Prop)
    (Available : CertifiedJustification -> Prop)
    (quotientsCertified : Prop)
    (x : D.State) (a : D.Action) where
  justification : CertifiedJustification
  route_available : Available justification
  enabled : ActionEnabled D x a
  corridor_safe : ActionCorridorSafe D Corridor x a
  quotients_certified : quotientsCertified

/-- Unrestricted license specialization: any certified justification is usable. -/
abbrev License
    (D : DecisionStructure)
    (Corridor : D.State -> Prop)
    (quotientsCertified : Prop)
    (x : D.State) (a : D.Action) : Type _ :=
  LicenseVia D Corridor (fun _ => True) quotientsCertified x a

/-- Proposition-valued form: there exists a license certificate. -/
def LicensedVia
    (D : DecisionStructure)
    (Corridor : D.State -> Prop)
    (Available : CertifiedJustification -> Prop)
    (quotientsCertified : Prop)
    (x : D.State) (a : D.Action) : Prop :=
  Nonempty (LicenseVia D Corridor Available quotientsCertified x a)

/-- Proposition-valued unrestricted license. -/
abbrev Licensed
    (D : DecisionStructure)
    (Corridor : D.State -> Prop)
    (quotientsCertified : Prop)
    (x : D.State) (a : D.Action) : Prop :=
  LicensedVia D Corridor (fun _ => True) quotientsCertified x a

theorem LicenseVia.concrete_justification
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State} {a : D.Action}
    (L : LicenseVia D Corridor Available quotientsCertified x a) :
    L.justification.concreteFact :=
  L.justification.concrete_holds

theorem LicensedVia.concrete_justification
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State} {a : D.Action}
    (L : LicensedVia D Corridor Available quotientsCertified x a) :
    exists J : CertifiedJustification, J.concreteFact := by
  rcases L with ⟨cert⟩
  exact ⟨cert.justification, cert.concrete_justification⟩

theorem LicenseVia.successor_in_corridor
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x y : D.State} {a : D.Action}
    (L : LicenseVia D Corridor Available quotientsCertified x a)
    (hStep : D.Step x a y) :
    Corridor y :=
  L.corridor_safe y hStep

/--
Adding certified routes cannot revoke an existing route-based license, provided
the quotient side condition and corridor are unchanged.
-/
def licenseVia_mono_routes
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available Available' : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State} {a : D.Action}
    (hSub : forall J, Available J -> Available' J)
    (L : LicenseVia D Corridor Available quotientsCertified x a) :
    LicenseVia D Corridor Available' quotientsCertified x a where
  justification := L.justification
  route_available := hSub L.justification L.route_available
  enabled := L.enabled
  corridor_safe := L.corridor_safe
  quotients_certified := L.quotients_certified

theorem licensedVia_mono_routes
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available Available' : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State} {a : D.Action}
    (hSub : forall J, Available J -> Available' J)
    (L : LicensedVia D Corridor Available quotientsCertified x a) :
    LicensedVia D Corridor Available' quotientsCertified x a := by
  rcases L with ⟨cert⟩
  exact ⟨licenseVia_mono_routes hSub cert⟩

/--
A plan license is checked against transported successor surfaces: after the
head action, every concrete successor must carry a license for the tail plan.
-/
inductive PlanLicense
    (D : DecisionStructure)
    (Corridor : D.State -> Prop)
    (Available : CertifiedJustification -> Prop)
    (quotientsCertified : Prop) :
    D.State -> List D.Action -> Type _ where
  | nil {x : D.State} :
      Corridor x ->
      PlanLicense D Corridor Available quotientsCertified x []
  | cons {x : D.State} {a : D.Action} {rest : List D.Action} :
      LicenseVia D Corridor Available quotientsCertified x a ->
      (forall y, D.Step x a y ->
        PlanLicense D Corridor Available quotientsCertified y rest) ->
      PlanLicense D Corridor Available quotientsCertified x (a :: rest)

def PlanLicense.head_license
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State} {a : D.Action} {rest : List D.Action}
    (P : PlanLicense D Corridor Available quotientsCertified x (a :: rest)) :
    LicenseVia D Corridor Available quotientsCertified x a := by
  cases P with
  | cons L _ => exact L

def PlanLicense.successor_tail
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x y : D.State} {a : D.Action} {rest : List D.Action}
    (P : PlanLicense D Corridor Available quotientsCertified x (a :: rest))
    (hStep : D.Step x a y) :
    PlanLicense D Corridor Available quotientsCertified y rest := by
  cases P with
  | cons _ tail => exact tail y hStep

theorem PlanLicense.head_successor_in_corridor
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x y : D.State} {a : D.Action} {rest : List D.Action}
    (P : PlanLicense D Corridor Available quotientsCertified x (a :: rest))
    (hStep : D.Step x a y) :
    Corridor y :=
  (P.head_license).successor_in_corridor hStep

def planLicense_cons
    {D : DecisionStructure}
    {Corridor : D.State -> Prop}
    {Available : CertifiedJustification -> Prop}
    {quotientsCertified : Prop}
    {x : D.State} {a : D.Action} {rest : List D.Action}
    (L : LicenseVia D Corridor Available quotientsCertified x a)
    (tail : forall y, D.Step x a y ->
      PlanLicense D Corridor Available quotientsCertified y rest) :
    PlanLicense D Corridor Available quotientsCertified x (a :: rest) :=
  PlanLicense.cons L tail

/--
Consequence-inseparability for quotient or decision-node identification.

Adding contexts makes this condition harder to satisfy because it is universal
over the admissible context register.
-/
def Inseparable
    {Context : Type u} {Process : Type v}
    (Admissible : Context -> Prop)
    (Separates : Context -> Process -> Process -> Prop)
    (p p' : Process) : Prop :=
  forall c, Admissible c -> Not (Separates c p p')

/-- If the context register shrinks, inseparability is preserved. -/
theorem inseparable_of_contexts_subset
    {Context : Type u} {Process : Type v}
    {Old New : Context -> Prop}
    {Separates : Context -> Process -> Process -> Prop}
    {p p' : Process}
    (hSub : forall c, New c -> Old c)
    (hOld : Inseparable Old Separates p p') :
    Inseparable New Separates p p' := by
  intro c hNew
  exact hOld c (hSub c hNew)

/--
If the context register expands, inseparability under the expanded register
implies inseparability under the old one. The converse is intentionally not
available in general.
-/
theorem inseparable_expanded_implies_old
    {Context : Type u} {Process : Type v}
    {Old New : Context -> Prop}
    {Separates : Context -> Process -> Process -> Prop}
    {p p' : Process}
    (hOldSubsetNew : forall c, Old c -> New c)
    (hNew : Inseparable New Separates p p') :
    Inseparable Old Separates p p' := by
  intro c hOld
  exact hNew c (hOldSubsetNew c hOld)

end Decision
end OmegaProper
