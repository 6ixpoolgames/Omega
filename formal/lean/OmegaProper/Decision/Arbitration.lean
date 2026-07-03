import Mathlib.Data.Finset.Basic

/-!
OmegaProper.Decision.Arbitration

ODT2 v0: registered least-violation arbitration over a finite candidate
frontier.

This file supplies only the procedural scaffold: given a nonempty finite
frontier and a declared Nat-valued violation score, a least-violation candidate
exists. The violation score is registered input. This file does not define
final value, moral standing, valuerhood, aggregation, agency, identity,
stochastic risk, quantum structure, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace Arbitration

universe u

/-- A nonempty finite candidate frontier with a registered violation score. -/
structure NatViolationFrame (Opt : Type u) where
  candidates : Finset Opt
  nonempty : candidates.Nonempty
  violation : Opt -> Nat

namespace NatViolationFrame

/-- Predicate view of registered candidacy. -/
def Candidate (F : NatViolationFrame Opt) : Opt -> Prop :=
  fun x => x ∈ F.candidates

end NatViolationFrame

/-- `x` is a candidate with minimal registered violation. -/
def LeastViolation
    (F : NatViolationFrame Opt)
    (x : Opt) : Prop :=
  F.Candidate x /\
    forall y, F.Candidate y -> F.violation x <= F.violation y

private theorem exists_leastViolation_list
    (violation : Opt -> Nat) :
    forall (l : List Opt), l ≠ [] ->
      exists x, x ∈ l /\ forall y, y ∈ l -> violation x <= violation y
  | [], h => False.elim (h rfl)
  | x :: xs, _ =>
      by
        by_cases hxs : xs = []
        · exact ⟨x,
            by
              constructor
              · simp
              · intro y hy
                simp [hxs] at hy
                cases hy
                exact Nat.le_refl (violation x)⟩
        · rcases exists_leastViolation_list violation xs hxs with
            ⟨z, hzMem, hzMin⟩
          by_cases hxz : violation x <= violation z
          · exact ⟨x,
              by
                constructor
                · simp
                · intro y hy
                  cases hy with
                  | head =>
                      exact Nat.le_refl (violation x)
                  | tail _ hyTail =>
                      exact Nat.le_trans hxz (hzMin y hyTail)⟩
          · exact ⟨z,
              by
                constructor
                · simp [hzMem]
                · intro y hy
                  cases hy with
                  | head =>
                      exact Nat.le_of_not_ge hxz
                  | tail _ hyTail =>
                      exact hzMin y hyTail⟩

theorem exists_leastViolation
    (F : NatViolationFrame Opt) :
    exists x, LeastViolation F x := by
  rcases F.nonempty with ⟨x0, hx0⟩
  have hListNonempty : F.candidates.toList ≠ [] := by
    intro hEmpty
    have hNotMem : x0 ∉ F.candidates.toList := by simp [hEmpty]
    exact hNotMem (by simpa using hx0)
  rcases exists_leastViolation_list F.violation F.candidates.toList
      hListNonempty with
    ⟨x, hxMem, hxMin⟩
  exact ⟨x,
    by
      constructor
      · simpa [NatViolationFrame.Candidate] using hxMem
      · intro y hy
        exact hxMin y (by simpa [NatViolationFrame.Candidate] using hy)⟩

noncomputable def leastViolationChoice
    (F : NatViolationFrame Opt) : Opt :=
  Classical.choose (exists_leastViolation F)

theorem leastViolationChoice_spec
    (F : NatViolationFrame Opt) :
    LeastViolation F (leastViolationChoice F) :=
  Classical.choose_spec (exists_leastViolation F)

/-- Minimal verdict shell for later registered-arbitration layers. -/
inductive ArbitrationVerdict (Opt : Type u) where
  | arbitrated : Opt -> ArbitrationVerdict Opt
  | authorityMissing : ArbitrationVerdict Opt
  | unresolved : ArbitrationVerdict Opt

end Arbitration
end Decision
end OmegaProper
