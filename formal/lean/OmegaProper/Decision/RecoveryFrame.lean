/-!
OmegaProper.Decision.RecoveryFrame

A small recovery/irreversibility interface for decision-adjacent corridor work.

This file defines bounded repair reachability to a declared fact and
nonrecoverable contraction of that fact. It does not define value, harm, moral
standing, patienthood, agency, identity, rights, quantum structure, or Omega
validation.
-/

namespace OmegaProper
namespace Decision
namespace RecoveryFrame

universe u v

/--
Fact species mark which kind of declared profile a recovery frame is tracking.

The species tags are bookkeeping only. They do not supply standing or value.
-/
inductive FactSpecies where
  | prefix
  | state
  | epistemic
  | lineage
deriving DecidableEq, Repr

/--
A bounded recovery frame.

`Fact` is the declared profile fact being preserved or recovered. `RepairAllowed`
restricts which actions count as admissible repair moves for this frame.
-/
structure RecoveryFrame (State : Type u) (Action : Type v) where
  Step : State -> Action -> State -> Prop
  RepairAllowed : State -> Action -> Prop
  Fact : State -> Prop
  species : FactSpecies

/-- Exact-length repair reachability using only registered repair moves. -/
inductive RepairReach {State : Type u} {Action : Type v}
    (R : RecoveryFrame State Action) : Nat -> State -> State -> Prop where
  | refl (s : State) : RepairReach R 0 s s
  | step {n : Nat} {s t u : State} {a : Action} :
      R.RepairAllowed s a ->
      R.Step s a t ->
      RepairReach R n t u ->
      RepairReach R (n + 1) s u

/-- Recovery in exactly `h` registered repair steps. -/
def RecoverableWithin {State : Type u} {Action : Type v}
    (R : RecoveryFrame State Action) (h : Nat) (s : State) : Prop :=
  exists t, RepairReach R h s t /\ R.Fact t

/-- Recovery in at most `h` registered repair steps. -/
def RecoverableUpTo {State : Type u} {Action : Type v}
    (R : RecoveryFrame State Action) (h : Nat) (s : State) : Prop :=
  exists n, n <= h /\ RecoverableWithin R n s

/--
The declared fact held at `s`, fails at `t`, and cannot be recovered from `t`
within the registered horizon.
-/
def NonrecoverableContraction {State : Type u} {Action : Type v}
    (R : RecoveryFrame State Action) (h : Nat) (s t : State) : Prop :=
  R.Fact s /\ Not (R.Fact t) /\ Not (RecoverableUpTo R h t)

theorem repairReach_zero_eq {State : Type u} {Action : Type v}
    {R : RecoveryFrame State Action} {s t : State}
    (h : RepairReach R 0 s t) :
    s = t := by
  cases h
  rfl

theorem fact_recoverable_within_zero {State : Type u} {Action : Type v}
    (R : RecoveryFrame State Action) {s : State}
    (hFact : R.Fact s) :
    RecoverableWithin R 0 s := by
  exact ⟨s, RepairReach.refl (R := R) s, hFact⟩

theorem fact_recoverable_upTo {State : Type u} {Action : Type v}
    (R : RecoveryFrame State Action) {h : Nat} {s : State}
    (hFact : R.Fact s) :
    RecoverableUpTo R h s := by
  exact ⟨0, Nat.zero_le h, fact_recoverable_within_zero R hFact⟩

theorem nonrecoverableContraction_loses_fact {State : Type u} {Action : Type v}
    {R : RecoveryFrame State Action} {h : Nat} {s t : State}
    (hContraction : NonrecoverableContraction R h s t) :
    Not (R.Fact t) :=
  hContraction.2.1

theorem nonrecoverableContraction_not_recoverable {State : Type u}
    {Action : Type v}
    {R : RecoveryFrame State Action} {h : Nat} {s t : State}
    (hContraction : NonrecoverableContraction R h s t) :
    Not (RecoverableUpTo R h t) :=
  hContraction.2.2

/--
A declared correction register: a finite or infinite family of distinctions
that remain live at a state.

This is not a value register. It is only a declared surface for future
correction, comparison, or revision capacity.
-/
structure CorrectionRegister (State : Type u) where
  Distinction : Type v
  Live : Distinction -> State -> Prop

namespace CorrectionRegister

/-- All declared correction distinctions are still live. -/
def AllLive {State : Type u}
    (C : CorrectionRegister.{u, v} State) (s : State) : Prop :=
  forall d : C.Distinction, C.Live d s

end CorrectionRegister

end RecoveryFrame
end Decision
end OmegaProper
