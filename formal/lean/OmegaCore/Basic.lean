/-!
OmegaCore.Basic

This is an intentionally small Lean pressure test for the Omega formalism.
It does not formalize the full quantale-presheaf kernel yet. Instead it checks
the order-theoretic recoverability lemmas that the prose kernel depends on.
-/

namespace OmegaCore

universe u v w x

/-- A minimal preorder-like frame for distinction objects. -/
structure DistinctionFrame (D : Type u) where
  le : D → D → Prop
  le_refl : ∀ d, le d d
  le_trans : ∀ {a b c}, le a b → le b c → le a c

/-- A minimal ordered tensor structure for asymmetry/support values. -/
structure ValueFrame (V : Type u) where
  le : V → V → Prop
  le_refl : ∀ v, le v v
  le_trans : ∀ {a b c}, le a b → le b c → le a c
  tensor : V → V → V
  tensor_mono :
    ∀ {a b c d}, le a b → le c d → le (tensor a c) (tensor b d)

attribute [simp] DistinctionFrame.le_refl ValueFrame.le_refl

/--
`Recovers DX DY VX pb A theta delta epsilon` means target distinction `epsilon`
structurally reconstructs source distinction `delta` through pullback `pb`, and
the asymmetry/support assignment `A` meets threshold `theta`.
-/
def Recovers
    {DX : Type u} {DY : Type v} {V : Type w}
    (DXF : DistinctionFrame DX) (VF : ValueFrame V)
    (pb : DY → DX) (A : DX → DY → V)
    (theta : V) (delta : DX) (epsilon : DY) : Prop :=
  DXF.le delta (pb epsilon) ∧ VF.le theta (A delta epsilon)

/-- A declared distinction requirement set is non-erased when each required
source distinction has some recovering target witness. -/
def NonErasing
    {DX : Type u} {DY : Type v} {V : Type w}
    (DXF : DistinctionFrame DX) (VF : ValueFrame V)
    (pb : DY → DX) (A : DX → DY → V)
    (Req : DX → Prop) (theta : DX → V) : Prop :=
  ∀ delta, Req delta → ∃ epsilon, Recovers DXF VF pb A (theta delta) delta epsilon

theorem recoverability_weaken_source
    {DX : Type u} {DY : Type v} {V : Type w}
    (DXF : DistinctionFrame DX) (VF : ValueFrame V)
    (pb : DY → DX) (A : DX → DY → V)
    (source_contra :
      ∀ {delta' delta : DX} {epsilon : DY},
        DXF.le delta' delta → VF.le (A delta epsilon) (A delta' epsilon))
    {theta : V} {delta delta' : DX} {epsilon : DY}
    (hrec : Recovers DXF VF pb A theta delta epsilon)
    (hle : DXF.le delta' delta) :
    Recovers DXF VF pb A theta delta' epsilon := by
  constructor
  · exact DXF.le_trans hle hrec.1
  · exact VF.le_trans hrec.2 (source_contra hle)

theorem recoverability_strengthen_target
    {DX : Type u} {DY : Type v} {V : Type w}
    (DXF : DistinctionFrame DX) (DYF : DistinctionFrame DY) (VF : ValueFrame V)
    (pb : DY → DX) (A : DX → DY → V)
    (pb_mono :
      ∀ {epsilon epsilon' : DY},
        DYF.le epsilon epsilon' → DXF.le (pb epsilon) (pb epsilon'))
    (target_mono :
      ∀ {delta : DX} {epsilon epsilon' : DY},
        DYF.le epsilon epsilon' → VF.le (A delta epsilon) (A delta epsilon'))
    {theta : V} {delta : DX} {epsilon epsilon' : DY}
    (hrec : Recovers DXF VF pb A theta delta epsilon)
    (hle : DYF.le epsilon epsilon') :
    Recovers DXF VF pb A theta delta epsilon' := by
  constructor
  · exact DXF.le_trans hrec.1 (pb_mono hle)
  · exact VF.le_trans hrec.2 (target_mono hle)

theorem non_erasure_monotonicity
    {DX : Type u} {DY : Type v} {V : Type w}
    (DXF : DistinctionFrame DX) (VF : ValueFrame V)
    (pb : DY → DX) (A : DX → DY → V)
    (Req Req' : DX → Prop) (theta : DX → V)
    (hsub : ∀ delta, Req' delta → Req delta)
    (hne : NonErasing DXF VF pb A Req theta) :
    NonErasing DXF VF pb A Req' theta := by
  intro delta hreq'
  exact hne delta (hsub delta hreq')

theorem compositional_recoverability
    {DX : Type u} {DY : Type v} {DZ : Type w} {V : Type x}
    (DXF : DistinctionFrame DX) (DYF : DistinctionFrame DY) (VF : ValueFrame V)
    (pbF : DY → DX) (pbG : DZ → DY) (pbGoF : DZ → DX)
    (AF : DX → DY → V) (AG : DY → DZ → V) (AGoF : DX → DZ → V)
    (pbF_mono :
      ∀ {epsilon epsilon' : DY},
        DYF.le epsilon epsilon' → DXF.le (pbF epsilon) (pbF epsilon'))
    (pb_functorial : ∀ zeta, pbGoF zeta = pbF (pbG zeta))
    (composite_support :
      ∀ {delta : DX} {epsilon : DY} {zeta : DZ},
        VF.le (VF.tensor (AF delta epsilon) (AG epsilon zeta)) (AGoF delta zeta))
    {theta psi : V} {delta : DX} {epsilon : DY} {zeta : DZ}
    (hF : Recovers DXF VF pbF AF theta delta epsilon)
    (hG : Recovers DYF VF pbG AG psi epsilon zeta) :
    Recovers DXF VF pbGoF AGoF (VF.tensor theta psi) delta zeta := by
  constructor
  · have hpb : DXF.le (pbF epsilon) (pbF (pbG zeta)) := pbF_mono hG.1
    have hstruct : DXF.le delta (pbF (pbG zeta)) := DXF.le_trans hF.1 hpb
    rw [pb_functorial zeta]
    exact hstruct
  · have htensor :
      VF.le (VF.tensor theta psi) (VF.tensor (AF delta epsilon) (AG epsilon zeta)) :=
        VF.tensor_mono hF.2 hG.2
    exact VF.le_trans htensor composite_support

end OmegaCore
