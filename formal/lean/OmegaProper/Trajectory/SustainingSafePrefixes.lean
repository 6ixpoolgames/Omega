import OmegaProper.Trajectory.RecurrentViableClass
import OmegaProper.Trajectory.TrajectorySemantics

/-!
OmegaProper.Trajectory.SustainingSafePrefixes

Safe-prefix semantics for sustaining and recurrent viable classes.

`TrajectorySemantics` proves that viability supplies arbitrarily long finite
safe prefixes. This file connects that operational reading to the existing
sustaining/recurrent class witnesses.

This is a constructive bridge, not a compactness theorem: it does not prove the
converse from arbitrarily long finite prefixes to viability.

This does not define value, agency, identity, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace SustainingSafePrefixes

open PredicateFixpoint
open ReachabilityViability
open RecurrentViableClass
open SustainingViableClass
open TrajectorySemantics

universe u

theorem sustainingClass_member_safePrefixes
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (hClass : SustainingViableClass D safe C)
    {x : D.State}
    (hx : C x) :
    ArbitrarilyLongSafePrefixes D safe x := by
  exact viable_implies_arbitrarilyLongSafePrefixes
    (sustainingClass_member_viable hClass hx)

theorem closedSustainingClass_member_safePrefixes
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (hClass : ClosedSustainingViableClass D safe C)
    {x : D.State}
    (hx : C x) :
    ArbitrarilyLongSafePrefixes D safe x := by
  exact sustainingClass_member_safePrefixes
    (closedSustaining_implies_sustaining hClass)
    hx

theorem recurrentClass_member_safePrefixes
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {C : D.State -> Prop}
    (hClass : RecurrentViableClass D safe C)
    {x : D.State}
    (hx : C x) :
    ArbitrarilyLongSafePrefixes D safe x := by
  exact closedSustainingClass_member_safePrefixes
    (recurrent_implies_closedSustaining hClass)
    hx

/-! ## Tiny finite witnesses -/

theorem loopClass_member_safePrefixes :
    ArbitrarilyLongSafePrefixes sustainDyn sustainSafe SustainState.loop := by
  exact closedSustainingClass_member_safePrefixes
    loopClass_closedSustaining
    trivial

theorem cycle_left_safePrefixes :
    ArbitrarilyLongSafePrefixes cycleDyn cycleSafe CycleState.left := by
  exact closedSustainingClass_member_safePrefixes
    cycleClass_closedSustaining
    trivial

theorem cycle_right_safePrefixes :
    ArbitrarilyLongSafePrefixes cycleDyn cycleSafe CycleState.right := by
  exact closedSustainingClass_member_safePrefixes
    cycleClass_closedSustaining
    trivial

theorem recurrent_cycle_left_safePrefixes :
    ArbitrarilyLongSafePrefixes cycleDyn cycleSafe CycleState.left := by
  exact recurrentClass_member_safePrefixes
    cycleClass_recurrent
    trivial

theorem recurrent_cycle_right_safePrefixes :
    ArbitrarilyLongSafePrefixes cycleDyn cycleSafe CycleState.right := by
  exact recurrentClass_member_safePrefixes
    cycleClass_recurrent
    trivial

theorem recurrent_cycle_supplies_safePrefixes :
    RecurrentViableClass cycleDyn cycleSafe cycleClass /\
    ArbitrarilyLongSafePrefixes cycleDyn cycleSafe CycleState.left /\
    ArbitrarilyLongSafePrefixes cycleDyn cycleSafe CycleState.right := by
  exact And.intro
    cycleClass_recurrent
    (And.intro
      recurrent_cycle_left_safePrefixes
      recurrent_cycle_right_safePrefixes)

end SustainingSafePrefixes
end Trajectory
end OmegaProper
