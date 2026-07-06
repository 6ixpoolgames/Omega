import OmegaProper.Decision.RecoveryFrame

/-!
OmegaProper.Decision.RecoveryFrameExamples

Finite witnesses for the recovery/irreversibility interface.

The examples are intentionally small. They show state recovery, epistemic
recovery, correction-register collapse (the internal "self-lobotomy" alias),
and phantom recoverability. They do not define harm, value, patienthood,
standing, agency, identity, rights, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace RecoveryFrameExamples

open RecoveryFrame

/-! ## State recovery witness -/

namespace StateRecovery

inductive State where
  | ok
  | lost
  | repaired
  | collapsed
deriving DecidableEq, Repr

inductive Action where
  | repair
  | idle
deriving DecidableEq, Repr

def Step : State -> Action -> State -> Prop
  | State.lost, Action.repair, State.repaired => True
  | State.ok, Action.idle, State.ok => True
  | State.repaired, Action.idle, State.repaired => True
  | State.collapsed, Action.idle, State.collapsed => True
  | _, _, _ => False

def RepairAllowed : State -> Action -> Prop
  | State.lost, Action.repair => True
  | State.ok, Action.idle => True
  | State.repaired, Action.idle => True
  | _, _ => False

def Fact : State -> Prop
  | State.ok => True
  | State.repaired => True
  | _ => False

def R : RecoveryFrame State Action where
  Step := Step
  RepairAllowed := RepairAllowed
  Fact := Fact
  species := FactSpecies.state

theorem lost_recoverable_within_one :
    RecoverableWithin R 1 State.lost := by
  refine ⟨State.repaired, ?_, by simp [R, Fact]⟩
  exact RepairReach.step (R := R) (a := Action.repair)
    (by simp [R, RepairAllowed])
    (by simp [R, Step])
    (RepairReach.refl (R := R) State.repaired)

theorem lost_recoverable_upTo_one :
    RecoverableUpTo R 1 State.lost := by
  exact ⟨1, Nat.le_refl 1, lost_recoverable_within_one⟩

theorem collapsed_not_recoverable_zero :
    Not (RecoverableUpTo R 0 State.collapsed) := by
  intro h
  rcases h with ⟨n, hn, hWithin⟩
  have hn0 : n = 0 := Nat.eq_zero_of_le_zero hn
  subst n
  rcases hWithin with ⟨t, hReach, hFact⟩
  have hEq : State.collapsed = t := repairReach_zero_eq hReach
  subst t
  simp [R, Fact] at hFact

theorem ok_to_collapsed_nonrecoverable_contraction :
    NonrecoverableContraction R 0 State.ok State.collapsed := by
  exact ⟨by simp [R, Fact], by simp [R, Fact],
    collapsed_not_recoverable_zero⟩

end StateRecovery

/-! ## Epistemic recovery witness -/

namespace EpistemicRecovery

inductive InfoState where
  | separated
  | merged
  | reSeparated
deriving DecidableEq, Repr

inductive Action where
  | probe
  | idle
deriving DecidableEq, Repr

def Step : InfoState -> Action -> InfoState -> Prop
  | InfoState.merged, Action.probe, InfoState.reSeparated => True
  | InfoState.separated, Action.idle, InfoState.separated => True
  | InfoState.reSeparated, Action.idle, InfoState.reSeparated => True
  | _, _, _ => False

def RepairAllowed : InfoState -> Action -> Prop
  | InfoState.merged, Action.probe => True
  | InfoState.separated, Action.idle => True
  | InfoState.reSeparated, Action.idle => True
  | _, _ => False

def Fact : InfoState -> Prop
  | InfoState.separated => True
  | InfoState.reSeparated => True
  | _ => False

def R : RecoveryFrame InfoState Action where
  Step := Step
  RepairAllowed := RepairAllowed
  Fact := Fact
  species := FactSpecies.epistemic

theorem merged_recovers_epistemic_separation_within_one :
    RecoverableWithin R 1 InfoState.merged := by
  refine ⟨InfoState.reSeparated, ?_, by simp [R, Fact]⟩
  exact RepairReach.step (R := R) (a := Action.probe)
    (by simp [R, RepairAllowed])
    (by simp [R, Step])
    (RepairReach.refl (R := R) InfoState.reSeparated)

theorem merged_recovers_epistemic_separation_upTo_one :
    RecoverableUpTo R 1 InfoState.merged := by
  exact ⟨1, Nat.le_refl 1, merged_recovers_epistemic_separation_within_one⟩

end EpistemicRecovery

/-!
## Correction-register collapse / self-lobotomy witness

The formal phrase is "correction-register collapse" or "nonrecoverable
revision-capacity loss." `self-lobotomy` is retained as an evocative internal
alias for this finite pattern: task success remains true while a declared
correction register is nonrecoverably destroyed.
-/

namespace CorrectionRegisterCollapse

inductive State where
  | correctable
  | collapsed
deriving DecidableEq, Repr

inductive Action where
  | preserve
  | collapse
deriving DecidableEq, Repr

inductive Distinction where
  | revision
deriving DecidableEq, Repr

def Register : CorrectionRegister State where
  Distinction := Distinction
  Live
    | Distinction.revision, State.correctable => True
    | Distinction.revision, State.collapsed => False

def Fact : State -> Prop :=
  Register.AllLive

def Step : State -> Action -> State -> Prop
  | State.correctable, Action.preserve, State.correctable => True
  | State.correctable, Action.collapse, State.collapsed => True
  | State.collapsed, Action.preserve, State.collapsed => True
  | _, _, _ => False

def RepairAllowed : State -> Action -> Prop
  | State.correctable, Action.preserve => True
  | State.collapsed, Action.preserve => True
  | _, _ => False

def R : RecoveryFrame State Action where
  Step := Step
  RepairAllowed := RepairAllowed
  Fact := Fact
  species := FactSpecies.epistemic

/-- The toy task is deliberately too coarse: both states count as task success. -/
def TaskSuccess (_ : State) : Prop := True

theorem collapsed_not_recoverable_zero :
    Not (RecoverableUpTo R 0 State.collapsed) := by
  intro h
  rcases h with ⟨n, hn, hWithin⟩
  have hn0 : n = 0 := Nat.eq_zero_of_le_zero hn
  subst n
  rcases hWithin with ⟨t, hReach, hFact⟩
  have hEq : State.collapsed = t := repairReach_zero_eq hReach
  subst t
  simp [R, Fact, Register, CorrectionRegister.AllLive] at hFact
  exact hFact Distinction.revision

theorem correctable_to_collapsed_nonrecoverable_revision_loss :
    NonrecoverableContraction R 0 State.correctable State.collapsed := by
  exact ⟨by
      intro d
      cases d
      trivial,
    by
      intro hFact
      exact hFact Distinction.revision,
    collapsed_not_recoverable_zero⟩

theorem W_self_lobotomy_correction_register_collapse :
    TaskSuccess State.correctable /\
      TaskSuccess State.collapsed /\
      NonrecoverableContraction R 0 State.correctable State.collapsed := by
  exact ⟨trivial, trivial, correctable_to_collapsed_nonrecoverable_revision_loss⟩

end CorrectionRegisterCollapse

/-! ## Phantom recoverability witness -/

namespace PhantomRecoverability

open CorrectionRegisterCollapse

/--
The corrupted frame reports the collapsed state as already satisfying the
correction fact. This models phantom recoverability by erasing the refuting
distinction.
-/
def PhantomFact : State -> Prop
  | State.correctable => True
  | State.collapsed => True

def PhantomFrame : RecoveryFrame State Action where
  Step := Step
  RepairAllowed := RepairAllowed
  Fact := PhantomFact
  species := FactSpecies.epistemic

theorem true_frame_rejects_collapsed_recovery_zero :
    Not (RecoverableUpTo R 0 State.collapsed) :=
  collapsed_not_recoverable_zero

theorem phantom_frame_reports_collapsed_recoverable_zero :
    RecoverableUpTo PhantomFrame 0 State.collapsed :=
  fact_recoverable_upTo PhantomFrame (by simp [PhantomFrame, PhantomFact])

theorem W_phantom_recoverability :
    Not (RecoverableUpTo R 0 State.collapsed) /\
      RecoverableUpTo PhantomFrame 0 State.collapsed := by
  exact ⟨true_frame_rejects_collapsed_recovery_zero,
    phantom_frame_reports_collapsed_recoverable_zero⟩

end PhantomRecoverability

end RecoveryFrameExamples
end Decision
end OmegaProper
