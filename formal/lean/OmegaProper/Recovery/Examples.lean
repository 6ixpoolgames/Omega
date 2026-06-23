import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import OmegaProper.Recovery.Joint
import OmegaProper.Recovery.PolicyContinuation
import OmegaProper.Recovery.Prior
import OmegaProper.Recovery.Randomized
import OmegaProper.Recovery.Robust

/-!
OmegaProper.Recovery.Examples

Small finite witnesses for the graded recovery layer.

These examples show:

* high-confidence recovery need not be support-exact;
* positive support does not determine graded recovery thresholds;
* per-channel exact recovery does not imply robust recovery with one common
  decoder over an ambiguity set;
* high expected recovery under a skewed prior does not imply worst-case
  threshold recovery.
-/

namespace OmegaProper
namespace Recovery
namespace Examples

abbrev Bit := Fin 2

lemma bit_eq_zero_or_one (b : Bit) : b = 0 ∨ b = 1 := by
  fin_cases b <;> simp

/-- Declared two-point target. -/
def bitTarget : Bit -> Bit :=
  id

/-- Declared two-point observation. -/
def bitObserve : Bit -> Bit :=
  id

/-- Identity decoder for two-point observations. -/
def bitDecoder : Bit -> Bit :=
  id

/-- Constant zero decoder for erased one-label observations. -/
def constZeroUnitDecoder : Unit -> Bit :=
  fun _ => 0

/-- Flip the two-point value. -/
def bitFlip (b : Bit) : Bit :=
  if b = 0 then 1 else 0

/-- Constant observation erases the two output labels. -/
def constantObserve : Bit -> Unit :=
  fun _ => ()

/-- Binary symmetric channel with `99/100` correct mass and full support. -/
def highConfidenceChannel : RatChannel Bit Bit where
  prob x y := if y = x then (99 / 100 : ℚ) else (1 / 100 : ℚ)
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/-- Binary symmetric channel with `9/10` correct mass and full support. -/
def highFullSupportChannel : RatChannel Bit Bit where
  prob x y := if y = x then (9 / 10 : ℚ) else (1 / 10 : ℚ)
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/-- Binary symmetric channel with `3/5` correct mass and full support. -/
def lowFullSupportChannel : RatChannel Bit Bit where
  prob x y := if y = x then (3 / 5 : ℚ) else (2 / 5 : ℚ)
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/-- Identity channel on the two-point space. -/
def identityBitChannel : RatChannel Bit Bit where
  prob x y := if y = x then (1 : ℚ) else 0
  nonneg := by
    intro x y
    by_cases h : y = x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [Finset.univ_fin2]

/-- Exact channel whose output is the flipped source bit. -/
def flipBitChannel : RatChannel Bit Bit where
  prob x y := if y = bitFlip x then (1 : ℚ) else 0
  nonneg := by
    intro x y
    by_cases h : y = bitFlip x
    · norm_num [h]
    · norm_num [h]
  row_sum_one := by
    intro x
    fin_cases x <;> norm_num [bitFlip, Finset.univ_fin2]

/-- Uniform randomized decoder from one observation label to two target values. -/
def uniformBitRandomizedDecoder : RandomizedDecoder Unit Bit where
  prob _ _ := (1 / 2 : ℚ)
  nonneg := by
    intro _ _
    norm_num
  row_sum_one := by
    intro _
    norm_num [Finset.univ_fin2]

/-- Prior putting `99/100` mass on source `0` and `1/100` on source `1`. -/
def skewedZeroPrior : RatPrior Bit where
  mass x := if x = 0 then (99 / 100 : ℚ) else (1 / 100 : ℚ)
  nonneg := by
    intro x
    by_cases h : x = 0
    · norm_num [h]
    · norm_num [h]
  sum_one := by
    norm_num [Finset.univ_fin2]

/-- Identity support relation for the two-bit panel witness. -/
def pairSupport (x y : Bit × Bit) : Prop :=
  y = x

/-- First marginal observation for a two-bit output. -/
def firstPairObserve (y : Bit × Bit) : Bit :=
  y.1

/-- Second marginal observation for a two-bit output. -/
def secondPairObserve (y : Bit × Bit) : Bit :=
  y.2

/-- First declared component of a two-bit source. -/
def firstPairTarget (x : Bit × Bit) : Bit :=
  x.1

/-- Second declared component of a two-bit source. -/
def secondPairTarget (x : Bit × Bit) : Bit :=
  x.2

/-- Joint declared target for a two-bit source. -/
def wholePairTarget (x : Bit × Bit) : Bit × Bit :=
  x

/-- Tiny shared-resource state space for policy-family robustness. -/
inductive JointShockState
  | start
  | aOnly
  | bOnly
  | bothGoal
  | fail
  deriving DecidableEq

instance : Fintype JointShockState where
  elems := {JointShockState.start, JointShockState.aOnly,
    JointShockState.bOnly, JointShockState.bothGoal, JointShockState.fail}
  complete := by
    intro x
    cases x <;> simp

lemma univ_jointShockState :
    (Finset.univ : Finset JointShockState) =
      {JointShockState.start, JointShockState.aOnly, JointShockState.bOnly,
        JointShockState.bothGoal, JointShockState.fail} := rfl

/-- Tiny action space for the shared-resource policy witness. -/
inductive JointShockAction
  | protectA
  | protectB
  | split
  | wait
  deriving DecidableEq

instance : Fintype JointShockAction where
  elems := {JointShockAction.protectA, JointShockAction.protectB,
    JointShockAction.split, JointShockAction.wait}
  complete := by
    intro x
    cases x <;> simp

lemma univ_jointShockAction :
    (Finset.univ : Finset JointShockAction) =
      {JointShockAction.protectA, JointShockAction.protectB,
        JointShockAction.split, JointShockAction.wait} := rfl

open JointShockState
open JointShockAction

/-- Point-mass transition helper for the shared-resource witness. -/
def jointShockPointMass (target : JointShockState) :
    JointShockState -> ℚ :=
  fun state => if state = target then 1 else 0

lemma jointShockPointMass_nonneg (target state : JointShockState) :
    0 <= jointShockPointMass target state := by
  unfold jointShockPointMass
  by_cases h : state = target <;> simp [h]

lemma jointShockPointMass_sum_one (target : JointShockState) :
    (Finset.univ.sum fun state => jointShockPointMass target state) = 1 := by
  cases target <;> simp [jointShockPointMass]

/-- In the nominal kernel, any active start action reaches the joint target. -/
def jointShockNominalTarget : JointShockAction -> JointShockState
  | protectA => bothGoal
  | protectB => bothGoal
  | split => bothGoal
  | wait => fail

/--
In the correlated-shock kernel, protecting one side reaches only that side;
splitting the shared resource reaches neither side.
-/
def jointShockCorrelatedTarget : JointShockAction -> JointShockState
  | protectA => aOnly
  | protectB => bOnly
  | split => fail
  | wait => fail

/-- Nominal shared-resource action kernel. -/
def jointShockNominalKernel : RatActionKernel JointShockState JointShockAction where
  prob state action next :=
    match state with
    | start => jointShockPointMass (jointShockNominalTarget action) next
    | _ => jointShockPointMass state next
  nonneg := by
    intro state action next
    cases state <;> cases action <;>
      exact jointShockPointMass_nonneg _ next
  row_sum_one := by
    intro state action
    cases state <;> cases action <;>
      simp [jointShockNominalTarget, jointShockPointMass_sum_one]

/-- Correlated-shock shared-resource action kernel. -/
def jointShockCorrelatedKernel : RatActionKernel JointShockState JointShockAction where
  prob state action next :=
    match state with
    | start => jointShockPointMass (jointShockCorrelatedTarget action) next
    | _ => jointShockPointMass state next
  nonneg := by
    intro state action next
    cases state <;> cases action <;>
      exact jointShockPointMass_nonneg _ next
  row_sum_one := by
    intro state action
    cases state <;> cases action <;>
      simp [jointShockCorrelatedTarget, jointShockPointMass_sum_one]

/-- Ambiguity set containing the nominal and correlated-shock kernels. -/
def jointShockAmbiguity : Set (RatActionKernel JointShockState JointShockAction) :=
  {jointShockNominalKernel, jointShockCorrelatedKernel}

/-- Policy that protects target A at the start state. -/
def protectAPolicy : JointShockState -> JointShockAction
  | start => protectA
  | _ => wait

/-- Policy that protects target B at the start state. -/
def protectBPolicy : JointShockState -> JointShockAction
  | start => protectB
  | _ => wait

/-- Target A is satisfied by the A-only state or by the joint target. -/
def targetA : JointShockState -> Prop
  | aOnly => True
  | bothGoal => True
  | _ => False

instance : DecidablePred targetA := by
  intro state
  cases state
  · exact isFalse (by intro h; cases h)
  · exact isTrue trivial
  · exact isFalse (by intro h; cases h)
  · exact isTrue trivial
  · exact isFalse (by intro h; cases h)

/-- Target B is satisfied by the B-only state or by the joint target. -/
def targetB : JointShockState -> Prop
  | bOnly => True
  | bothGoal => True
  | _ => False

instance : DecidablePred targetB := by
  intro state
  cases state
  · exact isFalse (by intro h; cases h)
  · exact isFalse (by intro h; cases h)
  · exact isTrue trivial
  · exact isTrue trivial
  · exact isFalse (by intro h; cases h)

/-- The joint target requires both sides to be achieved. -/
def targetJoint : JointShockState -> Prop
  | bothGoal => True
  | _ => False

instance : DecidablePred targetJoint := by
  intro state
  cases state
  · exact isFalse (by intro h; cases h)
  · exact isFalse (by intro h; cases h)
  · exact isFalse (by intro h; cases h)
  · exact isTrue trivial
  · exact isFalse (by intro h; cases h)

/-- Hit mass of a point-mass next state against a target predicate. -/
def targetHitMass
    (target : JointShockState -> Prop)
    [DecidablePred target]
    (next : JointShockState) : ℚ :=
  Finset.univ.sum fun state =>
    jointShockPointMass next state * if target state then 1 else 0

lemma targetA_bothGoal_hitMass :
    targetHitMass targetA bothGoal = 1 := by
  rw [targetHitMass, univ_jointShockState]
  simp [targetA, jointShockPointMass]

lemma targetA_aOnly_hitMass :
    targetHitMass targetA aOnly = 1 := by
  rw [targetHitMass, univ_jointShockState]
  simp [targetA, jointShockPointMass]

lemma targetB_bothGoal_hitMass :
    targetHitMass targetB bothGoal = 1 := by
  rw [targetHitMass, univ_jointShockState]
  simp [targetB, jointShockPointMass]

lemma targetB_bOnly_hitMass :
    targetHitMass targetB bOnly = 1 := by
  rw [targetHitMass, univ_jointShockState]
  simp [targetB, jointShockPointMass]

lemma targetJoint_aOnly_hitMass :
    targetHitMass targetJoint aOnly = 0 := by
  rw [targetHitMass, univ_jointShockState]
  simp [targetJoint, jointShockPointMass]

lemma targetJoint_bOnly_hitMass :
    targetHitMass targetJoint bOnly = 0 := by
  rw [targetHitMass, univ_jointShockState]
  simp [targetJoint, jointShockPointMass]

lemma targetJoint_fail_hitMass :
    targetHitMass targetJoint fail = 0 := by
  rw [targetHitMass, univ_jointShockState]
  simp [targetJoint, jointShockPointMass]

/--
The `99/100` channel has deterministic recovery at threshold `99/100`.
-/
theorem highConfidence_recoveryAt_99_100 :
    RecoveryExistsAt highConfidenceChannel bitTarget bitObserve (99 / 100 : ℚ) := by
  exact Exists.intro bitDecoder fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, highConfidenceChannel,
      bitTarget, bitObserve, bitDecoder, Finset.univ_fin2]

/--
The same high-confidence channel is not support-exact, because every output has
positive support from every source.
-/
theorem highConfidence_not_supportExact :
    Not (
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        (PositiveSupport highConfidenceChannel) bitTarget bitObserve
    ) := by
  intro hExact
  match hExact with
  | Exists.intro decoder hDecoder =>
      have hZero : decoder 0 = 0 :=
        hDecoder 0 0 (by norm_num [PositiveSupport, highConfidenceChannel])
      have hOne : decoder 0 = 1 :=
        hDecoder 1 0 (by norm_num [PositiveSupport, highConfidenceChannel])
      rw [hZero] at hOne
      norm_num at hOne

/--
The two full-support channels have the same positive-support relation.
-/
theorem high_low_same_positiveSupport :
    forall x y,
      PositiveSupport highFullSupportChannel x y <->
        PositiveSupport lowFullSupportChannel x y := by
  intro x y
  fin_cases x <;> fin_cases y <;>
    norm_num [PositiveSupport, highFullSupportChannel, lowFullSupportChannel]

/-- The high full-support channel reaches threshold `9/10`. -/
theorem highFullSupport_recoveryAt_9_10 :
    RecoveryExistsAt highFullSupportChannel bitTarget bitObserve (9 / 10 : ℚ) := by
  exact Exists.intro bitDecoder fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, highFullSupportChannel,
      bitTarget, bitObserve, bitDecoder, Finset.univ_fin2]

/--
The low full-support channel cannot reach threshold `4/5` with any deterministic
two-point decoder.
-/
theorem lowFullSupport_not_recoveryAt_4_5 :
    Not (RecoveryExistsAt lowFullSupportChannel bitTarget bitObserve (4 / 5 : ℚ)) := by
  intro hRecovery
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      rcases bit_eq_zero_or_one (decoder 0) with hFalse | hFalse
      · rcases bit_eq_zero_or_one (decoder 1) with hTrue | hTrue
        · have hSrc := hDecoder 1
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc
        · have hSrc := hDecoder 0
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc
      · rcases bit_eq_zero_or_one (decoder 1) with hTrue | hTrue
        · have hSrc := hDecoder 0
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc
        · have hSrc := hDecoder 0
          norm_num [DeclaredRecoveryAt, Success, lowFullSupportChannel,
            bitTarget, bitObserve, hFalse, hTrue, Finset.univ_fin2] at hSrc

/--
A single deterministic observation label cannot recover two source classes at
threshold `1/2`.
-/
theorem constantObservation_not_recoveryAt_half :
    Not (RecoveryExistsAt identityBitChannel bitTarget constantObserve (1 / 2 : ℚ)) := by
  intro hRecovery
  match hRecovery with
  | Exists.intro decoder hDecoder =>
      rcases bit_eq_zero_or_one (decoder ()) with hDecoderValue | hDecoderValue
      · have hSrc := hDecoder 1
        norm_num [DeclaredRecoveryAt, Success, identityBitChannel,
          bitTarget, constantObserve, hDecoderValue, Finset.univ_fin2] at hSrc
      · have hSrc := hDecoder 0
        norm_num [DeclaredRecoveryAt, Success, identityBitChannel,
          bitTarget, constantObserve, hDecoderValue, Finset.univ_fin2] at hSrc

/--
The uniform randomized decoder reaches threshold `1/2` for the same one-label
observation.
-/
theorem constantObservation_randomizedRecoveryAt_half :
    RandomizedRecoveryAt identityBitChannel bitTarget constantObserve (1 / 2 : ℚ) := by
  exact Exists.intro uniformBitRandomizedDecoder fun x => by
    fin_cases x <;> norm_num [RandomizedSuccess, identityBitChannel, bitTarget,
      constantObserve, uniformBitRandomizedDecoder, Finset.univ_fin2]

/-- The identity bit channel has exact deterministic recovery. -/
theorem identityBitChannel_recoveryAt_one :
    RecoveryExistsAt identityBitChannel bitTarget bitObserve 1 := by
  exact Exists.intro bitDecoder fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, identityBitChannel,
      bitTarget, bitObserve, bitDecoder, Finset.univ_fin2]

/-- The flipped bit channel has exact deterministic recovery using the flipped decoder. -/
theorem flipBitChannel_recoveryAt_one :
    RecoveryExistsAt flipBitChannel bitTarget bitObserve 1 := by
  exact Exists.intro bitFlip fun x => by
    fin_cases x <;> norm_num [DeclaredRecoveryAt, Success, flipBitChannel,
      bitTarget, bitObserve, bitFlip, Finset.univ_fin2]

/--
Each channel in the ambiguity set is exactly recoverable on its own, but no
single deterministic decoder recovers both channels at threshold one.
-/
theorem identity_flip_each_recoverable_not_robust :
    RecoveryExistsAt identityBitChannel bitTarget bitObserve 1 ∧
      RecoveryExistsAt flipBitChannel bitTarget bitObserve 1 ∧
      Not (
        RobustRecoveryAt
          ({identityBitChannel, flipBitChannel} : Set (RatChannel Bit Bit))
          bitTarget bitObserve 1
      ) := by
  refine ⟨identityBitChannel_recoveryAt_one, flipBitChannel_recoveryAt_one, ?_⟩
  intro hRobust
  match hRobust with
  | Exists.intro decoder hDecoder =>
      have hIdZero :
          (1 : ℚ) <=
            Success identityBitChannel bitTarget bitObserve decoder 0 :=
        hDecoder identityBitChannel (by simp) 0
      have hFlipOne :
          (1 : ℚ) <=
            Success flipBitChannel bitTarget bitObserve decoder 1 :=
        hDecoder flipBitChannel (by simp) 1
      rcases bit_eq_zero_or_one (decoder 0) with hDecoderZero | hDecoderZero
      · norm_num [Success, flipBitChannel, bitTarget, bitObserve, bitFlip,
          hDecoderZero, Finset.univ_fin2] at hFlipOne
      · norm_num [Success, identityBitChannel, bitTarget, bitObserve,
          hDecoderZero, Finset.univ_fin2] at hIdZero

/--
Under a skewed source prior, the erased observation with a constant decoder has
high expected success.
-/
theorem skewedPrior_constantObservation_expectedRecoveryAt_99_100 :
    ExpectedRecoveryExistsAt skewedZeroPrior identityBitChannel bitTarget
      constantObserve (99 / 100 : ℚ) := by
  refine Exists.intro constZeroUnitDecoder ?_
  norm_num [ExpectedDeclaredRecoveryAt, ExpectedDecoderSuccess,
    ExpectedSuccess, RecoveryProfile, Success, skewedZeroPrior,
    identityBitChannel, bitTarget, constantObserve, constZeroUnitDecoder,
    Finset.univ_fin2]

/--
High expected recovery under a declared prior does not imply worst-case
threshold recovery.
-/
theorem high_expected_not_worstCase_recovery :
    ExpectedRecoveryExistsAt skewedZeroPrior identityBitChannel bitTarget
        constantObserve (99 / 100 : ℚ) ∧
      Not (RecoveryExistsAt identityBitChannel bitTarget constantObserve
        (1 / 2 : ℚ)) := by
  exact ⟨skewedPrior_constantObservation_expectedRecoveryAt_99_100,
    constantObservation_not_recoveryAt_half⟩

/--
The first marginal observation exactly recovers the first declared component.
-/
theorem firstPairObservation_recovers_first :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      pairSupport firstPairTarget firstPairObserve := by
  exact Exists.intro id fun x y hSupport => by
    cases hSupport
    rfl

/--
The second marginal observation exactly recovers the second declared component.
-/
theorem secondPairObservation_recovers_second :
    BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
      pairSupport secondPairTarget secondPairObserve := by
  exact Exists.intro id fun x y hSupport => by
    cases hSupport
    rfl

/--
The first marginal observation does not recover the full joint target.
-/
theorem firstPairObservation_not_jointExact :
    Not (
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        pairSupport wholePairTarget firstPairObserve
    ) := by
  intro hExact
  match hExact with
  | Exists.intro decoder hDecoder =>
      have h00 : decoder 0 = ((0, 0) : Bit × Bit) :=
        hDecoder (0, 0) (0, 0) rfl
      have h01 : decoder 0 = ((0, 1) : Bit × Bit) :=
        hDecoder (0, 1) (0, 1) rfl
      rw [h00] at h01
      norm_num at h01

/--
The second marginal observation does not recover the full joint target.
-/
theorem secondPairObservation_not_jointExact :
    Not (
      BaselineWitnesses.ExactRecoverySupport.ExactRecoveryExists
        pairSupport wholePairTarget secondPairObserve
    ) := by
  intro hExact
  match hExact with
  | Exists.intro decoder hDecoder =>
      have h00 : decoder 0 = ((0, 0) : Bit × Bit) :=
        hDecoder (0, 0) (0, 0) rfl
      have h10 : decoder 0 = ((1, 0) : Bit × Bit) :=
        hDecoder (1, 0) (1, 0) rfl
      rw [h00] at h10
      norm_num at h10

/--
Target A is robustly attainable across the nominal/correlated-shock ambiguity
set by protecting A.
-/
theorem jointShock_targetA_policyFamilyRobustHitAt_one :
    PolicyFamilyRobustHitAt jointShockAmbiguity targetA
      (fun _ => True) start 1 1 := by
  refine Exists.intro protectAPolicy ⟨True.intro, ?_⟩
  intro K hK
  rcases hK with hK | hK
  · subst K
    simp only [HitWithin, inducedKernel, jointShockNominalKernel,
      protectAPolicy, jointShockNominalTarget, targetA]
    change (1 : ℚ) <= targetHitMass targetA bothGoal
    rw [targetA_bothGoal_hitMass]
  · subst K
    simp only [HitWithin, inducedKernel, jointShockCorrelatedKernel,
      protectAPolicy, jointShockCorrelatedTarget, targetA]
    change (1 : ℚ) <= targetHitMass targetA aOnly
    rw [targetA_aOnly_hitMass]

/--
Target B is robustly attainable across the nominal/correlated-shock ambiguity
set by protecting B.
-/
theorem jointShock_targetB_policyFamilyRobustHitAt_one :
    PolicyFamilyRobustHitAt jointShockAmbiguity targetB
      (fun _ => True) start 1 1 := by
  refine Exists.intro protectBPolicy ⟨True.intro, ?_⟩
  intro K hK
  rcases hK with hK | hK
  · subst K
    simp only [HitWithin, inducedKernel, jointShockNominalKernel,
      protectBPolicy, jointShockNominalTarget, targetB]
    change (1 : ℚ) <= targetHitMass targetB bothGoal
    rw [targetB_bothGoal_hitMass]
  · subst K
    simp only [HitWithin, inducedKernel, jointShockCorrelatedKernel,
      protectBPolicy, jointShockCorrelatedTarget, targetB]
    change (1 : ℚ) <= targetHitMass targetB bOnly
    rw [targetB_bOnly_hitMass]

/--
No deterministic policy robustly attains the joint target at threshold one
under the correlated shock. This is the Lean version of the adapter witness:
individual robust policy attainability does not imply joint robust policy
attainability under shared correlated constraints.
-/
theorem jointShock_not_joint_policyFamilyRobustHitAt_one :
    Not (
      PolicyFamilyRobustHitAt jointShockAmbiguity targetJoint
        (fun _ => True) start 1 1
    ) := by
  intro hHit
  match hHit with
  | Exists.intro policy hPolicy =>
      have hCorr :
          (1 : ℚ) <=
            HitWithin (inducedKernel jointShockCorrelatedKernel policy)
              targetJoint 1 start :=
        hPolicy.2 jointShockCorrelatedKernel (by simp [jointShockAmbiguity])
      cases hAction : policy start
      · simp only [HitWithin, inducedKernel, jointShockCorrelatedKernel,
          jointShockCorrelatedTarget, hAction, targetJoint] at hCorr
        change (1 : ℚ) <= targetHitMass targetJoint aOnly at hCorr
        rw [targetJoint_aOnly_hitMass] at hCorr
        norm_num at hCorr
      · simp only [HitWithin, inducedKernel, jointShockCorrelatedKernel,
          jointShockCorrelatedTarget, hAction, targetJoint] at hCorr
        change (1 : ℚ) <= targetHitMass targetJoint bOnly at hCorr
        rw [targetJoint_bOnly_hitMass] at hCorr
        norm_num at hCorr
      · simp only [HitWithin, inducedKernel, jointShockCorrelatedKernel,
          jointShockCorrelatedTarget, hAction, targetJoint] at hCorr
        change (1 : ℚ) <= targetHitMass targetJoint fail at hCorr
        rw [targetJoint_fail_hitMass] at hCorr
        norm_num at hCorr
      · simp only [HitWithin, inducedKernel, jointShockCorrelatedKernel,
          jointShockCorrelatedTarget, hAction, targetJoint] at hCorr
        change (1 : ℚ) <= targetHitMass targetJoint fail at hCorr
        rw [targetJoint_fail_hitMass] at hCorr
        norm_num at hCorr

/--
The shared-resource witness packages the strictness result: each individual
target is robustly attainable by some policy, but the joint target is not.
-/
theorem jointShock_individual_robust_not_joint_robust :
    PolicyFamilyRobustHitAt jointShockAmbiguity targetA
        (fun _ => True) start 1 1 ∧
      PolicyFamilyRobustHitAt jointShockAmbiguity targetB
        (fun _ => True) start 1 1 ∧
      Not (
        PolicyFamilyRobustHitAt jointShockAmbiguity targetJoint
          (fun _ => True) start 1 1
      ) := by
  exact ⟨jointShock_targetA_policyFamilyRobustHitAt_one,
    jointShock_targetB_policyFamilyRobustHitAt_one,
    jointShock_not_joint_policyFamilyRobustHitAt_one⟩

end Examples
end Recovery
end OmegaProper
