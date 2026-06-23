import OmegaProper.Trajectory.DistinctionSupport
import OmegaProper.Trajectory.RecurrentSupportRobustness

/-!
OmegaProper.Trajectory.CarrierTransport

Generic carrier-handoff theorem.

Several recurrent-support files prove the same last step: once a target support
is recurrent viable, contains target endpoints, internally connects them, and
preserves the source merge-separation fact, recurrent carrying transfers. This
module packages that last step without imposing a particular source of the
handoff data.

It is a theorem about a sufficient transport certificate, not identity,
agency, value, valuerhood, alignment, or Omega proper.
-/

namespace OmegaProper
namespace Trajectory
namespace CarrierTransport

open ConsequenceRelation
open DistinctionSupport
open PathCarriedDistinction
open RecurrentViableClass
open RecurrentSupportRobustness

universe w k o

/--
Generic pair-relative carrier handoff data.

`x₀,y₀` are the source endpoints whose merge separation is already known.
`x₁,y₁` are the target endpoints carried by the target support. The contract
does not assert that these are the same object or identity across time; it only
records the exact data needed to transport the carried consequence distinction.
-/
structure CarrierTransport
    (S : ConsequenceSystem.{w, k, o})
    (Next1 : S.Fragment -> S.Fragment -> Prop)
    (safe1 : S.Fragment -> Prop)
    (D : S.Fragment -> Prop)
    (x₀ y₀ x₁ y₁ : S.Fragment) : Prop where
  recurrent :
    RecurrentViableClass (dynFromNext Next1) safe1 D
  left_mem : D x₁
  right_mem : D y₁
  forward :
    InternalPath (dynFromNext Next1) D x₁ y₁
  backward :
    InternalPath (dynFromNext Next1) D y₁ x₁
  separation :
    ConsequenceMergeSeparated S x₀ y₀ ->
      ConsequenceMergeSeparated S x₁ y₁

theorem supportsMergeSeparatedPair_transport
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe1 C D : S.Fragment -> Prop}
    {x₀ y₀ x₁ y₁ : S.Fragment}
    (hSupport : SupportsMergeSeparatedPair S Next0 C x₀ y₀)
    (hTransport : CarrierTransport S Next1 safe1 D x₀ y₀ x₁ y₁) :
    SupportsMergeSeparatedPair S Next1 D x₁ y₁ := by
  exact And.intro
    hTransport.left_mem
    (And.intro
      hTransport.right_mem
      (And.intro
        hTransport.forward
        (And.intro
          hTransport.backward
          (hTransport.separation hSupport.right.right.right.right))))

theorem recurrentSupportCarries_transport
    {S : ConsequenceSystem.{w, k, o}}
    {Next0 Next1 : S.Fragment -> S.Fragment -> Prop}
    {safe0 safe1 : S.Fragment -> Prop}
    {C D : S.Fragment -> Prop}
    {x₀ y₀ x₁ y₁ : S.Fragment}
    (hCarry : RecurrentSupportCarries S Next0 safe0 C x₀ y₀)
    (hTransport : CarrierTransport S Next1 safe1 D x₀ y₀ x₁ y₁) :
    RecurrentSupportCarries S Next1 safe1 D x₁ y₁ := by
  exact And.intro
    hTransport.recurrent
    (supportsMergeSeparatedPair_transport hCarry.right hTransport)

end CarrierTransport
end Trajectory
end OmegaProper
