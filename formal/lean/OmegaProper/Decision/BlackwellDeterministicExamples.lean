import OmegaProper.Decision.BlackwellDeterministic

/-!
OmegaProper.Decision.BlackwellDeterministicExamples

Small deterministic examples for the ODT1 Blackwell-shaped conservativity
wrapper: identity observations factor to constant observations, constant
observations do not factor back to identity observations, and compilation
preserves outcome surfaces.
-/

namespace OmegaProper
namespace Decision
namespace BlackwellDeterministicExamples

open BlackwellDeterministic

/-! ## Two-state deterministic strictness witness -/

inductive TwoState where
  | s0
  | s1
deriving DecidableEq

inductive TwoAct where
  | a0
  | a1
deriving DecidableEq

inductive GoodBad where
  | bad
  | good
deriving DecidableEq

def GoodBad.rank : GoodBad -> Nat
  | GoodBad.bad => 0
  | GoodBad.good => 1

instance : LE GoodBad where
  le x y := x.rank <= y.rank

instance : Preorder GoodBad where
  le_refl := by
    intro x
    exact Nat.le_refl x.rank
  le_trans := by
    intro x y z hxy hyz
    exact Nat.le_trans hxy hyz

def identityExperiment : DetExperiment TwoState TwoState where
  observe := fun s => s

def constantExperiment : DetExperiment TwoState Unit where
  observe := fun _ => ()

def identity_to_constant_factorization :
    DetFactorization identityExperiment constantExperiment where
  map := fun _ => ()
  commutes := by
    intro s
    rfl

theorem identity_factors_to_constant :
    DetBlackwellDominates identityExperiment constantExperiment :=
  ⟨identity_to_constant_factorization⟩

theorem constant_does_not_factor_to_identity :
    Not (DetBlackwellDominates constantExperiment identityExperiment) := by
  intro hDom
  rcases hDom with ⟨fac⟩
  have hs : TwoState.s0 = TwoState.s1 := by
    calc
      TwoState.s0 = identityExperiment.observe TwoState.s0 := rfl
      _ = fac.map (constantExperiment.observe TwoState.s0) :=
        fac.commutes TwoState.s0
      _ = fac.map (constantExperiment.observe TwoState.s1) := rfl
      _ = identityExperiment.observe TwoState.s1 :=
        (fac.commutes TwoState.s1).symm
      _ = TwoState.s1 := rfl
  cases hs

/-! ## Matching task outcome surfaces -/

def matchingOutcome : TwoState -> TwoAct -> GoodBad
  | TwoState.s0, TwoAct.a0 => GoodBad.good
  | TwoState.s1, TwoAct.a1 => GoodBad.good
  | _, _ => GoodBad.bad

def identityPolicy : TwoState -> TwoAct
  | TwoState.s0 => TwoAct.a0
  | TwoState.s1 => TwoAct.a1

def constantPolicyA0 : Unit -> TwoAct :=
  fun _ => TwoAct.a0

theorem identity_policy_has_good :
    PolicyOutcomeSurface identityExperiment identityPolicy
      matchingOutcome GoodBad.good :=
  ⟨TwoState.s0, rfl⟩

theorem identity_policy_no_bad :
    Not (PolicyOutcomeSurface identityExperiment identityPolicy
      matchingOutcome GoodBad.bad) := by
  rintro ⟨s, hs⟩
  cases s <;> simp [identityExperiment, identityPolicy, matchingOutcome] at hs

theorem constant_policy_a0_has_good :
    PolicyOutcomeSurface constantExperiment constantPolicyA0
      matchingOutcome GoodBad.good :=
  ⟨TwoState.s0, rfl⟩

theorem constant_policy_a0_has_bad :
    PolicyOutcomeSurface constantExperiment constantPolicyA0
      matchingOutcome GoodBad.bad :=
  ⟨TwoState.s1, rfl⟩

theorem identity_compiles_constant_policy_surface
    (policy : Unit -> TwoAct)
    (w : GoodBad) :
    PolicyOutcomeSurface identityExperiment
      (compilePolicy identity_to_constant_factorization policy)
      matchingOutcome w <->
      PolicyOutcomeSurface constantExperiment policy matchingOutcome w :=
  compiled_policy_surface_iff identity_to_constant_factorization policy
    matchingOutcome w

theorem identity_compiles_constant_policy_plotkin_equiv
    (policy : Unit -> TwoAct) :
    Dominance.PlotkinDominates
      (PolicyOutcomeSurface identityExperiment
        (compilePolicy identity_to_constant_factorization policy)
        matchingOutcome)
      (PolicyOutcomeSurface constantExperiment policy matchingOutcome)
    /\
    Dominance.PlotkinDominates
      (PolicyOutcomeSurface constantExperiment policy matchingOutcome)
      (PolicyOutcomeSurface identityExperiment
        (compilePolicy identity_to_constant_factorization policy)
        matchingOutcome) :=
  compiled_policy_plotkin_equiv identity_to_constant_factorization policy
    matchingOutcome

end BlackwellDeterministicExamples
end Decision
end OmegaProper
