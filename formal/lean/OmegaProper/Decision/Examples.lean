import OmegaProper.Decision.License

/-!
OmegaProper.Decision.Examples

Small strictness/control examples for the ODT0 decision-floor interface.

These examples are intentionally tiny. They show:

* a true abstract fact with a false concrete fact cannot be reflected;
* context-register expansion can revoke a quotient/inseparability claim.
-/

namespace OmegaProper
namespace Decision
namespace Examples

theorem abstract_true_concrete_false_blocks_reflection :
    Not (True -> False) :=
  no_reflected_fact_of_abstract_true_concrete_false
    (show True from trivial)
    (by intro hFalse; exact hFalse)

inductive TwoCtx where
  | old
  | new
deriving DecidableEq

inductive TwoProc where
  | p
  | q
deriving DecidableEq

def oldRegister : TwoCtx -> Prop
  | TwoCtx.old => True
  | TwoCtx.new => False

def expandedRegister : TwoCtx -> Prop :=
  fun _ => True

def separatesNewOnly : TwoCtx -> TwoProc -> TwoProc -> Prop
  | TwoCtx.new, TwoProc.p, TwoProc.q => True
  | _, _, _ => False

theorem oldRegister_inseparable :
    Inseparable oldRegister separatesNewOnly TwoProc.p TwoProc.q := by
  intro c hOld hSep
  cases c with
  | old =>
      simp [separatesNewOnly] at hSep
  | new =>
      simp [oldRegister] at hOld

theorem not_expandedRegister_inseparable :
    Not (Inseparable expandedRegister separatesNewOnly TwoProc.p TwoProc.q) := by
  intro hInsep
  exact hInsep TwoCtx.new trivial (by simp [separatesNewOnly])

theorem context_expansion_can_revoke_inseparability :
    Inseparable oldRegister separatesNewOnly TwoProc.p TwoProc.q /\
      Not (Inseparable expandedRegister separatesNewOnly TwoProc.p TwoProc.q) :=
  And.intro oldRegister_inseparable not_expandedRegister_inseparable

end Examples
end Decision
end OmegaProper
