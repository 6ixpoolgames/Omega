import Mathlib.Data.Set.Basic

/-!
OmegaV2.Finite.Identifiability

Evidence fibers and refinement laws for finite identification. These results
formalize the distinction between observational and intervention evidence.
They do not define a process, agent, valuer, or preferred interface.
-/

namespace OmegaV2
namespace Finite

universe u v w

/-- Models producing the selected evidence value. -/
def EvidenceFiber
    {Model : Type u}
    {Evidence : Type v}
    (evidence : Model -> Evidence)
    (value : Evidence) :
    Set Model :=
  {model | evidence model = value}

/--
`rich` refines `coarse` when agreement under rich evidence always implies
agreement under coarse evidence.
-/
def EvidenceRefines
    {Model : Type u}
    {RichEvidence : Type v}
    {CoarseEvidence : Type w}
    (rich : Model -> RichEvidence)
    (coarse : Model -> CoarseEvidence) : Prop :=
  forall left right, rich left = rich right -> coarse left = coarse right

/-- A refined evidence fiber is contained in the corresponding coarse fiber. -/
theorem refined_fiber_subset
    {Model : Type u}
    {RichEvidence : Type v}
    {CoarseEvidence : Type w}
    {rich : Model -> RichEvidence}
    {coarse : Model -> CoarseEvidence}
    (hRefines : EvidenceRefines rich coarse)
    (target : Model) :
    EvidenceFiber rich (rich target) ⊆
      EvidenceFiber coarse (coarse target) := by
  intro model hRich
  exact hRefines model target hRich

/-- Identification of one target inside a declared model family. -/
def IdentifiedBy
    {Model : Type u}
    {Evidence : Type v}
    (models : Set Model)
    (evidence : Model -> Evidence)
    (target : Model) : Prop :=
  target ∈ models ∧
    forall other, other ∈ models ->
      evidence other = evidence target ->
      other = target

/--
If coarse evidence already identifies a target, any refinement also
identifies it.
-/
theorem identified_under_coarse_implies_identified_under_refinement
    {Model : Type u}
    {RichEvidence : Type v}
    {CoarseEvidence : Type w}
    {models : Set Model}
    {rich : Model -> RichEvidence}
    {coarse : Model -> CoarseEvidence}
    {target : Model}
    (hRefines : EvidenceRefines rich coarse)
    (hIdentified : IdentifiedBy models coarse target) :
    IdentifiedBy models rich target := by
  constructor
  · exact hIdentified.1
  · intro other hOther hRich
    exact hIdentified.2 other hOther (hRefines other target hRich)

/-- Agreement on one declared baseline intervention. -/
def ObservationallyEquivalent
    {Model : Type u}
    {Intervention : Type v}
    {Outcome : Type w}
    (response : Model -> Intervention -> Outcome)
    (baseline : Intervention)
    (left right : Model) : Prop :=
  response left baseline = response right baseline

/-- Agreement under every declared intervention. -/
def InterventionallyEquivalent
    {Model : Type u}
    {Intervention : Type v}
    {Outcome : Type w}
    (response : Model -> Intervention -> Outcome)
    (left right : Model) : Prop :=
  forall intervention, response left intervention = response right intervention

/-- Intervention equivalence implies baseline observational equivalence. -/
theorem interventional_equivalence_implies_observational_equivalence
    {Model : Type u}
    {Intervention : Type v}
    {Outcome : Type w}
    (response : Model -> Intervention -> Outcome)
    (baseline : Intervention)
    (left right : Model)
    (hEquivalent : InterventionallyEquivalent response left right) :
    ObservationallyEquivalent response baseline left right := by
  exact hEquivalent baseline

/--
Finite counterexample: agreement at one baseline does not imply agreement
under every intervention.
-/
theorem observational_equivalence_does_not_imply_interventional_equivalence :
    ∃ response : Bool -> Bool -> Bool,
      ∃ left right baseline : Bool,
        ObservationallyEquivalent response baseline left right ∧
          ¬ InterventionallyEquivalent response left right := by
  refine ⟨fun model intervention => model && intervention, false, true, false, ?_, ?_⟩
  · rfl
  · intro hEquivalent
    have hAtTrue := hEquivalent true
    simp at hAtTrue

end Finite
end OmegaV2
