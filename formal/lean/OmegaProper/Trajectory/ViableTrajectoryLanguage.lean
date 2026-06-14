import OmegaProper.Trajectory.JointViability
import OmegaProper.Trajectory.TrajectorySemantics

/-!
OmegaProper.Trajectory.ViableTrajectoryLanguage

Finite viable trajectory language.

`TrajectorySemantics` already defines `SafePrefix`: a finite prefix that remains
inside a declared safety predicate. This file gives that object the language
name needed by the boundary-invariant continuation roadmap.

This does not define value, lushness, agency, identity, alignment, or Omega
proper. It only packages finite safe-prefix facts as the next exact object for
later path-count / richness candidates.
-/

namespace OmegaProper
namespace Trajectory
namespace ViableTrajectoryLanguage

open JointViability
open ReachabilityViability
open TrajectorySemantics

universe u

/--
A finite viable word is a safe prefix of a declared transition length.

The word length counts transitions, not states.
-/
abbrev ViableWord
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    (n : Nat)
    (x : D.State) : Prop :=
  SafePrefix D safe n x

/-- A state has viable words at every finite horizon. -/
abbrev ViableLanguage
    (D : Dyn.{u})
    (safe : D.State -> Prop)
    (x : D.State) : Prop :=
  ArbitrarilyLongSafePrefixes D safe x

/-- Joint viable words are viable words for the conjunction of two constraints. -/
abbrev JointViableWord
    (D : Dyn.{u})
    (safeA safeB : D.State -> Prop)
    (n : Nat)
    (x : D.State) : Prop :=
  ViableWord D (JointSafe safeA safeB) n x

/-- Joint viable language is finite-prefix language inside the joint corridor. -/
abbrev JointViableLanguage
    (D : Dyn.{u})
    (safeA safeB : D.State -> Prop)
    (x : D.State) : Prop :=
  ViableLanguage D (JointSafe safeA safeB) x

theorem viable_supplies_word
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {x : D.State}
    (hViable : Viable D safe x)
    (n : Nat) :
    ViableWord D safe n x := by
  exact viable_has_safePrefix D safe n x hViable

theorem viable_supplies_language
    {D : Dyn.{u}}
    {safe : D.State -> Prop}
    {x : D.State}
    (hViable : Viable D safe x) :
    ViableLanguage D safe x := by
  exact viable_implies_arbitrarilyLongSafePrefixes hViable

theorem jointViable_supplies_jointWord
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {x : D.State}
    (hJoint : JointViable D safeA safeB x)
    (n : Nat) :
    JointViableWord D safeA safeB n x := by
  exact viable_supplies_word hJoint n

theorem jointViable_supplies_jointLanguage
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {x : D.State}
    (hJoint : JointViable D safeA safeB x) :
    JointViableLanguage D safeA safeB x := by
  exact viable_supplies_language hJoint

theorem jointViable_supplies_leftLanguage
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {x : D.State}
    (hJoint : JointViable D safeA safeB x) :
    ViableLanguage D safeA x := by
  exact viable_supplies_language (jointViable_left x hJoint)

theorem jointViable_supplies_rightLanguage
    {D : Dyn.{u}}
    {safeA safeB : D.State -> Prop}
    {x : D.State}
    (hJoint : JointViable D safeA safeB x) :
    ViableLanguage D safeB x := by
  exact viable_supplies_language (jointViable_right x hJoint)

end ViableTrajectoryLanguage
end Trajectory
end OmegaProper
