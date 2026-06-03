import OmegaCore.Presentations.ProbabilisticChannel

/-!
OmegaCore.Presentations.ProbabilisticChannelPolicy

Finite policy-separation example for the probabilistic channel presentation.

This file shows that fixed-declared target recovery and Bayes-best target
recovery are formally distinct policies: an available alternate target
observation can recover a source distinction perfectly while the fixed-declared
target observation fails a declared recovery threshold.

This is a worked finite presentation example. It is not an empirical adapter,
compatibility/completion machinery, valuerhood, agency, identity, ethics, or
Omega validation.
-/

namespace OmegaCore

namespace Presentations

namespace ProbabilisticChannel

/-- Identity-like two-point channel. -/
def policyIdChannel : Bit -> Bit -> Nat
  | Bit.zero, Bit.zero => 1
  | Bit.zero, Bit.one => 0
  | Bit.one, Bit.zero => 0
  | Bit.one, Bit.one => 1

/-- Uniform natural-weight prior on the two-point source. -/
def policyUniformPrior : Bit -> Nat
  | Bit.zero => 1
  | Bit.one => 1

/-- Fixed-declared target observation that collapses the bit. -/
def fixedBadObs : Bit -> Bool
  | _ => false

/-- Alternate available target observation that preserves the bit. -/
def alternateGoodObs : Bit -> Bool := bitObs

inductive TargetCandidate where
  | fixed
  | alternate
  deriving DecidableEq

instance : Fintype TargetCandidate where
  elems := {TargetCandidate.fixed, TargetCandidate.alternate}
  complete := by
    intro c
    cases c <;> simp

/-- Candidate target observation used by the tiny policy-separation example. -/
def candidateObs : TargetCandidate -> Bit -> Bool
  | TargetCandidate.fixed => fixedBadObs
  | TargetCandidate.alternate => alternateGoodObs

/-- Candidate decoder used by the tiny policy-separation example. -/
def candidateDec (_ : TargetCandidate) : Bool -> Bool := boolId

theorem policyExample_totalMass :
    totalMass policyIdChannel policyUniformPrior = 2 := by
  unfold totalMass rowSum policyIdChannel policyUniformPrior
  native_decide

theorem fixedBad_successMass :
    successMass policyIdChannel policyUniformPrior bitObs fixedBadObs boolId = 1 := by
  unfold successMass policyIdChannel policyUniformPrior bitObs fixedBadObs boolId
  native_decide

theorem alternateGood_successMass :
    successMass policyIdChannel policyUniformPrior bitObs alternateGoodObs boolId = 2 := by
  unfold successMass policyIdChannel policyUniformPrior bitObs alternateGoodObs boolId
  native_decide

/-- The alternate available target observation strictly exceeds the
fixed-declared target observation in this finite example. -/
theorem alternate_target_strictly_exceeds_fixed_declared :
    successMass policyIdChannel policyUniformPrior bitObs alternateGoodObs boolId
      >
    successMass policyIdChannel policyUniformPrior bitObs fixedBadObs boolId := by
  rw [alternateGood_successMass, fixedBad_successMass]
  native_decide

theorem alternateGood_perfectProb :
    PerfectProbRecovers policyIdChannel policyUniformPrior bitObs alternateGoodObs boolId := by
  unfold PerfectProbRecovers
  rw [alternateGood_successMass, policyExample_totalMass]

theorem fixedBad_not_atLeast75 :
    ¬ ProbRecoversAtLeast policyIdChannel policyUniformPrior bitObs fixedBadObs boolId 75 100 := by
  unfold ProbRecoversAtLeast
  rw [fixedBad_successMass, policyExample_totalMass]
  native_decide

/-- Fixed-declared and Bayes-best-style target policies can diverge: a candidate
target set can contain an alternate target observation that recovers perfectly
while the fixed-declared target fails a declared threshold. -/
theorem bayes_best_can_exceed_fixed_declared :
    successMass policyIdChannel policyUniformPrior bitObs alternateGoodObs boolId
      >
    successMass policyIdChannel policyUniformPrior bitObs fixedBadObs boolId
    ∧
    PerfectProbRecovers policyIdChannel policyUniformPrior bitObs alternateGoodObs boolId
    ∧
    ¬ ProbRecoversAtLeast policyIdChannel policyUniformPrior bitObs fixedBadObs boolId 75 100 := by
  exact
    And.intro alternate_target_strictly_exceeds_fixed_declared
      (And.intro alternateGood_perfectProb fixedBad_not_atLeast75)

theorem candidate_fixed_successMass :
    successMass policyIdChannel policyUniformPrior bitObs
        (candidateObs TargetCandidate.fixed)
        (candidateDec TargetCandidate.fixed)
      =
    1 := by
  unfold candidateObs candidateDec
  exact fixedBad_successMass

theorem candidate_alternate_successMass :
    successMass policyIdChannel policyUniformPrior bitObs
        (candidateObs TargetCandidate.alternate)
        (candidateDec TargetCandidate.alternate)
      =
    2 := by
  unfold candidateObs candidateDec
  exact alternateGood_successMass

/-- In the explicit two-candidate example, the alternate candidate dominates all
available candidate target observations by success mass. -/
theorem bayes_best_is_alternate_in_two_candidate_example :
    forall c : TargetCandidate,
      successMass policyIdChannel policyUniformPrior bitObs
          (candidateObs c)
          (candidateDec c)
        <=
      successMass policyIdChannel policyUniformPrior bitObs
          (candidateObs TargetCandidate.alternate)
          (candidateDec TargetCandidate.alternate) := by
  intro c
  cases c
  · rw [candidate_fixed_successMass, candidate_alternate_successMass]
    native_decide
  · rw [candidate_alternate_successMass]

end ProbabilisticChannel

end Presentations

end OmegaCore
