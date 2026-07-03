import OmegaProper.Decision.Arbitration

/-!
OmegaProper.Decision.ArbitrationExamples

Tiny registered least-violation example for ODT2 v0.
-/

namespace OmegaProper
namespace Decision
namespace ArbitrationExamples

open Arbitration

inductive ToyOption where
  | a
  | b
  | c
deriving DecidableEq

def toyViolation : ToyOption -> Nat
  | ToyOption.a => 2
  | ToyOption.b => 0
  | ToyOption.c => 1

def toyFrame : NatViolationFrame ToyOption where
  candidates := {ToyOption.a, ToyOption.b, ToyOption.c}
  nonempty := by
    exact ⟨ToyOption.a, by simp⟩
  violation := toyViolation

theorem toy_b_is_leastViolation :
    LeastViolation toyFrame ToyOption.b := by
  constructor
  · simp [NatViolationFrame.Candidate, toyFrame]
  · intro y hy
    cases y <;> simp [toyFrame, toyViolation]

theorem toy_choice_has_zero_violation :
    toyFrame.violation (leastViolationChoice toyFrame) = 0 := by
  have hMin := leastViolationChoice_spec toyFrame
  have hb : NatViolationFrame.Candidate toyFrame ToyOption.b := by
    simp [NatViolationFrame.Candidate, toyFrame]
  have hLe := hMin.right ToyOption.b hb
  have hNonneg : 0 <= toyFrame.violation (leastViolationChoice toyFrame) :=
    Nat.zero_le _
  have hUpper : toyFrame.violation (leastViolationChoice toyFrame) <= 0 := by
    simpa [toyFrame, toyViolation] using hLe
  exact Nat.le_antisymm hUpper hNonneg

end ArbitrationExamples
end Decision
end OmegaProper
