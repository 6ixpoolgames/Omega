import OmegaProper.Trajectory.ReachabilityReflection
import OmegaProper.Trajectory.TrajectorySemantics

/-!
OmegaProper.Trajectory.ViabilityReflection

Reflection contracts for viability under presentations.

`ReachabilityReflection` proves that target and step reflection prevent
fabricated reachability. This file gives the analogous greatest-fixed-point
result for viability: if abstract safety and abstract steps reflect back to the
exact system, then abstract viability reflects back to exact viability.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace ViabilityReflection

open PredicateFixpoint
open ReachabilityReflection
open ReachabilityViability
open TrajectorySemantics

universe u v

/--
Abstract safety membership reflects to exact safety membership through the
presentation.
-/
def SafeReflects
    (DX : Dyn.{u})
    (DQ : Dyn.{v})
    (present : DX.State -> DQ.State)
    (safeX : DX.State -> Prop)
    (safeQ : DQ.State -> Prop) : Prop :=
  forall x, safeQ (present x) -> safeX x

/--
A presentation reflects viability when it reflects both safety and steps. This
is a dynamics contract, not an identity or value claim.
-/
structure ViabilityReflectingPresentation
    (DX : Dyn.{u})
    (DQ : Dyn.{v})
    (present : DX.State -> DQ.State)
    (safeX : DX.State -> Prop)
    (safeQ : DQ.State -> Prop) where
  safe_reflects : SafeReflects DX DQ present safeX safeQ
  step_reflects : StepReflects DX DQ present

/--
If abstract safety membership and abstract steps reflect to exact safety
membership and exact steps, then abstract viability cannot be fabricated:
abstract viability of `present x` implies exact viability of `x`.
-/
theorem abstractViable_reflects_exactViable
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {safeX : DX.State -> Prop}
    {safeQ : DQ.State -> Prop}
    (hReflect :
      ViabilityReflectingPresentation DX DQ present safeX safeQ)
    {x : DX.State}
    (hViableQ : Viable DQ safeQ (present x)) :
    Viable DX safeX x := by
  match hViableQ with
  | Exists.intro pQ hpQ =>
      let pullbackViable : DX.State -> Prop :=
        fun x0 => pQ (present x0)
      have hPost : Postfixed (viabilityOp DX safeX) pullbackViable := by
        intro x0 hx0
        have hQStep :
            viabilityOp DQ safeQ pQ (present x0) :=
          hpQ.left (present x0) hx0
        exact And.intro
          (hReflect.safe_reflects x0 hQStep.left)
          (match hQStep.right with
            | Exists.intro z hz =>
                match hReflect.step_reflects x0 z hz.left with
                | Exists.intro y hy =>
                    Exists.intro y
                      (And.intro hy.left (by
                        simpa [pullbackViable, hy.right] using hz.right)))
      exact Exists.intro pullbackViable
        (And.intro hPost hpQ.right)

/-- Direct spelling without packaging the two reflection hypotheses. -/
theorem abstractViable_reflects_exactViable_of_reflects
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {safeX : DX.State -> Prop}
    {safeQ : DQ.State -> Prop}
    (hSafe : SafeReflects DX DQ present safeX safeQ)
    (hStep : StepReflects DX DQ present)
    {x : DX.State}
    (hViableQ : Viable DQ safeQ (present x)) :
    Viable DX safeX x := by
  exact abstractViable_reflects_exactViable
    { safe_reflects := hSafe, step_reflects := hStep }
    hViableQ

/-- A generalized safe-prefix lifting theorem with an explicit start equality. -/
theorem abstractSafePrefix_lifts_exactSafePrefix
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {safeX : DX.State -> Prop}
    {safeQ : DQ.State -> Prop}
    (hSafe : SafeReflects DX DQ present safeX safeQ)
    (hStep : StepReflects DX DQ present)
    {n : Nat}
    {x : DX.State}
    {q : DQ.State}
    (hStart : present x = q)
    (hPrefixQ : SafePrefix DQ safeQ n q) :
    SafePrefix DX safeX n x := by
  match hPrefixQ with
  | SafePrefix.zero hSafeQ =>
      exact SafePrefix.zero
        (hSafe x (by
          simpa [hStart] using hSafeQ))
  | @SafePrefix.step _ _ n qStart qNext hSafeQ hStepQ hRest =>
      have hStepFromPresented :
          DQ.Next (present x) qNext := by
        simpa [hStart] using hStepQ
      match hStep x _ hStepFromPresented with
      | Exists.intro y hy =>
          exact SafePrefix.step
            (hSafe x (by
              simpa [hStart] using hSafeQ))
            hy.left
            (abstractSafePrefix_lifts_exactSafePrefix
              hSafe
              hStep
              hy.right
              hRest)

/--
Direct safe-prefix lifting under safety and step reflection.

An abstract safe prefix from `present x` lifts to an exact safe prefix of the
same length from `x`.
-/
theorem abstractSafePrefix_reflects_exactSafePrefix
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {safeX : DX.State -> Prop}
    {safeQ : DQ.State -> Prop}
    (hSafe : SafeReflects DX DQ present safeX safeQ)
    (hStep : StepReflects DX DQ present)
    {n : Nat}
    {x : DX.State}
    (hPrefixQ : SafePrefix DQ safeQ n (present x)) :
    SafePrefix DX safeX n x := by
  exact abstractSafePrefix_lifts_exactSafePrefix
    hSafe
    hStep
    rfl
    hPrefixQ

theorem abstractSafePrefix_reflects_exactSafePrefix_of_presentation
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {safeX : DX.State -> Prop}
    {safeQ : DQ.State -> Prop}
    (hReflect :
      ViabilityReflectingPresentation DX DQ present safeX safeQ)
    {n : Nat}
    {x : DX.State}
    (hPrefixQ : SafePrefix DQ safeQ n (present x)) :
    SafePrefix DX safeX n x := by
  exact abstractSafePrefix_reflects_exactSafePrefix
    hReflect.safe_reflects
    hReflect.step_reflects
    hPrefixQ

/--
Operational viability reflection: abstract viability of a presented state
reflects to arbitrarily long exact safe prefixes.

This does not claim an infinite exact trajectory. It composes viability
reflection with the safe-prefix semantics for `Viable`.
-/
theorem abstractViable_reflects_exactSafePrefixes
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {safeX : DX.State -> Prop}
    {safeQ : DQ.State -> Prop}
    (hReflect :
      ViabilityReflectingPresentation DX DQ present safeX safeQ)
    {x : DX.State}
    (hViableQ : Viable DQ safeQ (present x)) :
    ArbitrarilyLongSafePrefixes DX safeX x := by
  exact viable_implies_arbitrarilyLongSafePrefixes
    (abstractViable_reflects_exactViable hReflect hViableQ)

/-- Direct spelling without packaging the two reflection hypotheses. -/
theorem abstractViable_reflects_exactSafePrefixes_of_reflects
    {DX : Dyn.{u}}
    {DQ : Dyn.{v}}
    {present : DX.State -> DQ.State}
    {safeX : DX.State -> Prop}
    {safeQ : DQ.State -> Prop}
    (hSafe : SafeReflects DX DQ present safeX safeQ)
    (hStep : StepReflects DX DQ present)
    {x : DX.State}
    (hViableQ : Viable DQ safeQ (present x)) :
    ArbitrarilyLongSafePrefixes DX safeX x := by
  exact abstractViable_reflects_exactSafePrefixes
    { safe_reflects := hSafe, step_reflects := hStep }
    hViableQ

end ViabilityReflection
end Trajectory
end OmegaProper
