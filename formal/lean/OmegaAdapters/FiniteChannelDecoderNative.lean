import OmegaAdapters.FiniteChannelNative

/-!
OmegaAdapters.FiniteChannelDecoderNative

Decoder provenance split for finite channel recovery.

`FiniteChannelNative.ExactRecovers` is existence-style recovery: it proves that
some decoder can recover a distinction through channel support. This module
separates that capacity result from recovery by a supplied decoder spec or
registry.
-/

namespace OmegaAdapters
namespace FiniteChannelNative
namespace DecoderProvenance

universe u v w q

/-- Decoder provenance policy marker. The registry/spec structure, not this tag
alone, is the theorem-surface guardrail. -/
inductive DecoderPolicy where
  | declared
  | existence
  | optimized
  | oracleForbidden
  deriving DecidableEq

/-- One supplied decoder with provenance metadata. -/
structure DecoderSpec
    {X : Type u} {Y : Type w}
    (D : ObsDist.{u, v} X)
    (E : ObsDist.{w, v} Y) where
  policy : DecoderPolicy
  decode : E.Label -> D.Label

/-- A supplied family of decoders for one source/target distinction pair. -/
structure DecoderRegistry
    {X : Type u} {Y : Type w}
    (D : ObsDist.{u, v} X)
    (E : ObsDist.{w, v} Y) where
  Dec : Type q
  policy : DecoderPolicy
  decode : Dec -> E.Label -> D.Label

/-- A supplied decoder exactly recovers through channel support. -/
def SpecExactRecovers
    {X : Type u} {Y : Type w}
    (K : X -> Y -> Prop)
    (D : ObsDist.{u, v} X)
    (E : ObsDist.{w, v} Y)
    (dec : DecoderSpec D E) : Prop :=
  forall x y, K x y -> dec.decode (E.obs y) = D.obs x

/-- A supplied decoder registry contains a decoder that exactly recovers through
channel support. -/
def RegisteredExactRecovers
    {X : Type u} {Y : Type w}
    (K : X -> Y -> Prop)
    (D : ObsDist.{u, v} X)
    (E : ObsDist.{w, v} Y)
    (Reg : DecoderRegistry D E) : Prop :=
  exists dec : Reg.Dec,
    forall x y, K x y -> Reg.decode dec (E.obs y) = D.obs x

/-- Declared registered recovery requires both a declared registry policy and a
working registered decoder. -/
def DeclaredRegisteredExactRecovers
    {X : Type u} {Y : Type w}
    (K : X -> Y -> Prop)
    (D : ObsDist.{u, v} X)
    (E : ObsDist.{w, v} Y)
    (Reg : DecoderRegistry D E) : Prop :=
  Reg.policy = DecoderPolicy.declared /\
    RegisteredExactRecovers K D E Reg

/-- Explicit capacity/existence alias for the older `ExactRecovers` surface. -/
abbrev ExistsExactRecovers
    {X : Type u} {Y : Type w}
    (K : X -> Y -> Prop)
    (D : ObsDist.{u, v} X)
    (E : ObsDist.{w, v} Y) : Prop :=
  ExactRecovers K D E

/-- Registered recovery implies existence-style recovery. -/
theorem registered_exact_implies_exists_exact
    {X : Type u} {Y : Type w}
    {K : X -> Y -> Prop}
    {D : ObsDist.{u, v} X}
    {E : ObsDist.{w, v} Y}
    {Reg : DecoderRegistry D E}
    (h : RegisteredExactRecovers K D E Reg) :
    ExistsExactRecovers K D E := by
  cases h with
  | intro dec hDec =>
      exact Exists.intro (Reg.decode dec) hDec

/-- Declared registered recovery implies existence-style recovery. -/
theorem declared_registered_exact_implies_exists_exact
    {X : Type u} {Y : Type w}
    {K : X -> Y -> Prop}
    {D : ObsDist.{u, v} X}
    {E : ObsDist.{w, v} Y}
    {Reg : DecoderRegistry D E}
    (h : DeclaredRegisteredExactRecovers K D E Reg) :
    ExistsExactRecovers K D E := by
  exact registered_exact_implies_exists_exact h.right

/-- A declared decoder spec that works also gives existence-style recovery. -/
theorem spec_declared_exact_implies_exists_exact
    {X : Type u} {Y : Type w}
    {K : X -> Y -> Prop}
    {D : ObsDist.{u, v} X}
    {E : ObsDist.{w, v} Y}
    {dec : DecoderSpec D E}
    (_hpolicy : dec.policy = DecoderPolicy.declared)
    (h : SpecExactRecovers K D E dec) :
    ExistsExactRecovers K D E := by
  exact Exists.intro dec.decode h

/-! ## Tiny finite separations -/

inductive Bit where
  | zero
  | one
  deriving DecidableEq

def bitIdChannel : Bit -> Bit -> Prop :=
  fun x y => x = y

def bitDist : ObsDist Bit where
  Label := Bool
  obs := fun
    | Bit.zero => false
    | Bit.one => true

def goodDeclaredSpec : DecoderSpec bitDist bitDist where
  policy := DecoderPolicy.declared
  decode := fun label => label

def badDeclaredSpec : DecoderSpec bitDist bitDist where
  policy := DecoderPolicy.declared
  decode := fun _ => false

def emptyDeclaredRegistry : DecoderRegistry bitDist bitDist where
  Dec := Empty
  policy := DecoderPolicy.declared
  decode := fun dec => nomatch dec

def badDeclaredRegistry : DecoderRegistry bitDist bitDist where
  Dec := Unit
  policy := DecoderPolicy.declared
  decode := fun _ _ => false

theorem good_declared_spec_recovers :
    SpecExactRecovers bitIdChannel bitDist bitDist goodDeclaredSpec := by
  intro x y hxy
  cases hxy
  rfl

theorem bad_declared_spec_not_recovers :
    Not (SpecExactRecovers bitIdChannel bitDist bitDist badDeclaredSpec) := by
  intro h
  have hOne := h Bit.one Bit.one rfl
  cases hOne

theorem bit_exists_exact :
    ExistsExactRecovers bitIdChannel bitDist bitDist := by
  exact Exists.intro (fun label => label)
    (by
      intro x y hxy
      cases hxy
      rfl)

/-- A working decoder exists, but an empty declared registry does not recover. -/
theorem exists_exact_not_empty_registered :
    ExistsExactRecovers bitIdChannel bitDist bitDist /\
      Not (RegisteredExactRecovers bitIdChannel bitDist bitDist emptyDeclaredRegistry) := by
  exact And.intro bit_exists_exact
    (by
      intro h
      cases h with
      | intro dec _ =>
          cases dec)

/-- The channel has recoverable information, but the declared decoder registry
can still fail. -/
theorem bad_declared_registry_but_exists_exact :
    Not (DeclaredRegisteredExactRecovers bitIdChannel bitDist bitDist badDeclaredRegistry) /\
      ExistsExactRecovers bitIdChannel bitDist bitDist := by
  refine And.intro ?_ bit_exists_exact
  intro h
  cases h.right with
  | intro dec hDec =>
      cases dec
      have hOne := hDec Bit.one Bit.one rfl
      cases hOne

/-- A good supplied decoder and a bad supplied decoder separate instrument
success from channel capacity. -/
theorem bad_declared_good_exists :
    SpecExactRecovers bitIdChannel bitDist bitDist goodDeclaredSpec /\
      Not (SpecExactRecovers bitIdChannel bitDist bitDist badDeclaredSpec) /\
      ExistsExactRecovers bitIdChannel bitDist bitDist := by
  exact And.intro good_declared_spec_recovers
    (And.intro bad_declared_spec_not_recovers bit_exists_exact)

end DecoderProvenance
end FiniteChannelNative
end OmegaAdapters
