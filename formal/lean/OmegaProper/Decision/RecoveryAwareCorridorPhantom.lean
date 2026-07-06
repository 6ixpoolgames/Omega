import OmegaProper.Decision.RecoveryAwareCorridorExamples

/-!
OmegaProper.Decision.RecoveryAwareCorridorPhantom

Phantom recoverability meets the recovery-aware gate.

The true recovery-aware corridor refuses the correction-register collapse
action. A corrupted/phantom recovery frame that reports the collapsed state as
already recoverable can license the same action. This is the recovery-aware
analog of a phantom corridor: the gate is only as sound as the recovery facts
registered into it.

This does not define harm, rights, moral standing, value, agency, identity, or
Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace RecoveryAwareCorridorPhantom

open RecoveryFrame
open RecoveryAwareCorridor
open Trajectory.PredicateFixpoint

def D : DecisionStructure :=
  RecoveryAwareCorridorExamples.SelfLobotomyGate.D

def Allowed : D.State -> D.Action -> Prop :=
  RecoveryAwareCorridorExamples.SelfLobotomyGate.Allowed

abbrev correctable : D.State :=
  RecoveryFrameExamples.CorrectionRegisterCollapse.State.correctable

abbrev collapsed : D.State :=
  RecoveryFrameExamples.CorrectionRegisterCollapse.State.collapsed

abbrev preserve : D.Action :=
  RecoveryFrameExamples.CorrectionRegisterCollapse.Action.preserve

abbrev collapse : D.Action :=
  RecoveryFrameExamples.CorrectionRegisterCollapse.Action.collapse

abbrev TrueCorridor : D.State -> Prop :=
  RecoveryAwareCorridorExamples.SelfLobotomyGate.Corridor

abbrev PhantomCorridor : D.State -> Prop :=
  RecoveryAwareCorridor D
    RecoveryFrameExamples.PhantomRecoverability.PhantomFrame 0 Allowed

def trivialJustification : CertifiedJustification :=
  RecoveryAwareCorridorExamples.SelfLobotomyGate.trivialJustification

theorem true_gate_refuses_collapse :
    Not
      (LicensedVia D TrueCorridor (fun _ => True) True
        correctable collapse) :=
  RecoveryAwareCorridorExamples.SelfLobotomyGate.collapse_cannot_be_licensed

private theorem phantom_collapsed_postfixed :
    Postfixed
      (robustCorridorOp D Allowed
        (RecoveryRequirement
          RecoveryFrameExamples.PhantomRecoverability.PhantomFrame 0))
      (fun s => s = collapsed) := by
  intro s hs
  cases hs
  refine ⟨trivial, ?_, preserve, trivial, ?_, ?_⟩
  · exact fact_recoverable_upTo
      RecoveryFrameExamples.PhantomRecoverability.PhantomFrame
      (by
        simp [RecoveryFrameExamples.PhantomRecoverability.PhantomFrame,
          RecoveryFrameExamples.PhantomRecoverability.PhantomFact])
  · exact ⟨collapsed,
      by
        simp [D, RecoveryAwareCorridorExamples.SelfLobotomyGate.D,
          RecoveryFrameExamples.CorrectionRegisterCollapse.Step]⟩
  · intro y hStep
    cases y <;>
      simp [D, RecoveryAwareCorridorExamples.SelfLobotomyGate.D,
        RecoveryFrameExamples.CorrectionRegisterCollapse.Step] at hStep
    rfl

theorem collapsed_in_phantom_corridor :
    PhantomCorridor collapsed :=
  postfixed_le_gfp phantom_collapsed_postfixed collapsed rfl

theorem phantom_gate_licenses_collapse :
    LicensedVia D PhantomCorridor (fun _ => True) True
      correctable collapse := by
  refine Nonempty.intro ?_
  exact
    { justification := trivialJustification
      route_available := trivial
      enabled := ⟨collapsed,
        by
          simp [D, RecoveryAwareCorridorExamples.SelfLobotomyGate.D,
            RecoveryFrameExamples.CorrectionRegisterCollapse.Step]⟩
      corridor_safe := by
        intro y hStep
        cases y <;>
          simp [D, RecoveryAwareCorridorExamples.SelfLobotomyGate.D,
            RecoveryFrameExamples.CorrectionRegisterCollapse.Step] at hStep
        exact collapsed_in_phantom_corridor
      quotients_certified := trivial }

theorem W_phantom_recoverability_creates_phantom_license :
    Not
      (LicensedVia D TrueCorridor (fun _ => True) True
        correctable collapse) /\
    LicensedVia D PhantomCorridor (fun _ => True) True
      correctable collapse := by
  exact ⟨true_gate_refuses_collapse, phantom_gate_licenses_collapse⟩

end RecoveryAwareCorridorPhantom
end Decision
end OmegaProper
