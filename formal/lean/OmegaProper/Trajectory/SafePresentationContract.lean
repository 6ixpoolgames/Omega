import OmegaProper.Trajectory.SoundQuotient
import OmegaProper.Trajectory.ViabilityReflection

/-!
OmegaProper.Trajectory.SafePresentationContract

Packaged contracts for using presentations in reachability and viability claims.

The repo keeps consequence soundness and dynamics reflection separate because
they answer different questions. This file packages them for convenience:
reachability and viability claims over an abstraction should carry both a
consequence-sound presentation and the relevant dynamics reflection contract.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace SafePresentationContract

open ConsequenceRelation
open ReachabilityReflection
open ReachabilityViability
open ViabilityReflection

universe w k o v

/-- Build exact dynamics over a consequence-system carrier from a transition relation. -/
def exactDynFromNext
    {X : Type w}
    (Next : X -> X -> Prop) : Dyn.{w} where
  State := X
  Next := Next

/--
Contract for using a presentation in a reachability claim.

The consequence-sound field says the presentation does not merge
consequence-separated fragments. The target/step fields say abstract
reachability reflects back to exact reachability.
-/
structure ReachabilitySafePresentationContract
    (S : ConsequenceSystem.{w, k, o})
    (DQ : Dyn.{v})
    (present : S.Fragment -> DQ.State)
    (NextX : S.Fragment -> S.Fragment -> Prop)
    (targetX : S.Fragment -> Prop)
    (targetQ : DQ.State -> Prop) where
  consequence_sound : SoundQuotient.SoundQuotient S present
  target_reflects :
    TargetReflects
      (exactDynFromNext NextX)
      DQ
      present
      targetX
      targetQ
  step_reflects :
    StepReflects
      (exactDynFromNext NextX)
      DQ
      present

/--
A reachability-safe presentation cannot fabricate reachability.

The consequence-sound field is part of the packaged contract; the proof uses
the dynamics reflection fields.
-/
theorem reachabilityContract_reflects_reach
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {targetX : S.Fragment -> Prop}
    {targetQ : DQ.State -> Prop}
    (hContract :
      ReachabilitySafePresentationContract
        S
        DQ
        present
        NextX
        targetX
        targetQ)
    {x : S.Fragment}
    (hReachQ : Reach DQ targetQ (present x)) :
    Reach (exactDynFromNext NextX) targetX x := by
  exact ReachabilityReflection.abstractReach_reflects_exactReach
    {
      target_reflects := hContract.target_reflects,
      step_reflects := hContract.step_reflects
    }
    hReachQ

/--
Contract for using a presentation in a viability claim.

The consequence-sound field says the presentation does not merge
consequence-separated fragments. The safety/step fields say abstract viability
reflects back to exact viability.
-/
structure ViabilitySafePresentationContract
    (S : ConsequenceSystem.{w, k, o})
    (DQ : Dyn.{v})
    (present : S.Fragment -> DQ.State)
    (NextX : S.Fragment -> S.Fragment -> Prop)
    (safeX : S.Fragment -> Prop)
    (safeQ : DQ.State -> Prop) where
  consequence_sound : SoundQuotient.SoundQuotient S present
  safe_reflects :
    SafeReflects
      (exactDynFromNext NextX)
      DQ
      present
      safeX
      safeQ
  step_reflects :
    StepReflects
      (exactDynFromNext NextX)
      DQ
      present

/--
A viability-safe presentation cannot fabricate viability.

The consequence-sound field is part of the packaged contract; the proof uses
the dynamics reflection fields.
-/
theorem viabilityContract_reflects_viability
    {S : ConsequenceSystem.{w, k, o}}
    {DQ : Dyn.{v}}
    {present : S.Fragment -> DQ.State}
    {NextX : S.Fragment -> S.Fragment -> Prop}
    {safeX : S.Fragment -> Prop}
    {safeQ : DQ.State -> Prop}
    (hContract :
      ViabilitySafePresentationContract
        S
        DQ
        present
        NextX
        safeX
        safeQ)
    {x : S.Fragment}
    (hViableQ : Viable DQ safeQ (present x)) :
    Viable (exactDynFromNext NextX) safeX x := by
  exact ViabilityReflection.abstractViable_reflects_exactViable
    {
      safe_reflects := hContract.safe_reflects,
      step_reflects := hContract.step_reflects
    }
    hViableQ

end SafePresentationContract
end Trajectory
end OmegaProper
