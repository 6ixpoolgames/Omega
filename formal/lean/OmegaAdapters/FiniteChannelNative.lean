import ProtoOmega.Transport.Native

/-!
OmegaAdapters.FiniteChannelNative

Alpha-native finite channel / observable-partition presentation.

Distinctions are observable labelings. A target distinction refines a source
distinction when the source labels can be decoded from the target labels.
Channel recovery is exact decoder reconstruction through a support relation.
-/

namespace OmegaAdapters
namespace FiniteChannelNative

universe u v w z

/-- Observable distinction as a labeling / partition of a carrier. -/
structure ObsDist (X : Type u) where
  Label : Type v
  obs : X -> Label

/-- Observable distinctions separate points when their labels differ. -/
def ObsSep {X : Type u} (D : ObsDist.{u, v} X) (x y : X) : Prop :=
  Not (D.obs x = D.obs y)

theorem obsSep_irrefl {X : Type u} (D : ObsDist.{u, v} X) (x : X) :
    Not (ObsSep D x x) := by
  intro h
  exact h rfl

theorem obsSep_symm {X : Type u} (D : ObsDist.{u, v} X) (x y : X) :
    ObsSep D x y -> ObsSep D y x := by
  intro h hyx
  exact h (Eq.symm hyx)

/-- Alpha frame whose distinctions are observable labelings. The support
channel itself is external to the frame and appears in `channelTransport`. -/
def obsAlphaFrame (X : Type u) : AlphaCore.Frame where
  X := X
  Rel := fun _ _ => False
  Dist := ObsDist.{u, v} X
  Sep := ObsSep
  sep_irrefl := obsSep_irrefl
  sep_symm := obsSep_symm
  Asym := fun _ _ _ => False
  asym_rel := by
    intro _ _ _ h
    cases h
  asym_sep := by
    intro _ _ _ h
    cases h

/-- `Refines D E` means `E` is fine enough to decode `D`. -/
def Refines {X : Type u} (D E : ObsDist.{u, v} X) : Prop :=
  exists decode : E.Label -> D.Label,
    forall x, decode (E.obs x) = D.obs x

theorem refines_refl {X : Type u} (D : ObsDist.{u, v} X) :
    Refines D D := by
  exact Exists.intro (fun label => label)
    (by
      intro x
      rfl)

theorem refines_trans
    {X : Type u} {D E F : ObsDist.{u, v} X} :
    Refines D E -> Refines E F -> Refines D F := by
  intro hDE hEF
  cases hDE with
  | intro decodeDE hDecodeDE =>
      cases hEF with
      | intro decodeEF hDecodeEF =>
          exact Exists.intro (fun label => decodeDE (decodeEF label))
            (by
              intro x
              change decodeDE (decodeEF (F.obs x)) = D.obs x
              calc
                decodeDE (decodeEF (F.obs x)) = decodeDE (E.obs x) := by
                  rw [hDecodeEF x]
                _ = D.obs x := hDecodeDE x)

/-- Observable-distinction order over the Alpha-native observable frame. -/
def obsDistOrder (X : Type u) :
    ProtoOmega.Transport.DistOrder (obsAlphaFrame (X := X)) where
  le := Refines
  le_refl := refines_refl
  le_trans := @refines_trans X

/-- Exact decoder recovery through a support channel. -/
def ExactRecovers
    {X : Type u} {Y : Type w}
    (K : X -> Y -> Prop)
    (D : ObsDist.{u, v} X)
    (E : ObsDist.{w, v} Y) : Prop :=
  exists decode : E.Label -> D.Label,
    forall x y, K x y -> decode (E.obs y) = D.obs x

/-- Channel-induced exact-recovery native transport. -/
def channelTransport
    {X : Type u} {Y : Type w}
    (K : X -> Y -> Prop) :
    ProtoOmega.Transport.NativeTransport (obsDistOrder (X := X)) (obsDistOrder (X := Y)) where
  rel := ExactRecovers K
  closed := by
    intro D' D E E' hSource hRec hTarget
    cases hSource with
    | intro decodeSource hDecodeSource =>
        cases hRec with
        | intro decodeRec hDecodeRec =>
            cases hTarget with
            | intro decodeTarget hDecodeTarget =>
                exact Exists.intro
                  (fun label => decodeSource (decodeRec (decodeTarget label)))
                  (by
                    intro x y hK
                    change
                      decodeSource (decodeRec (decodeTarget (E'.obs y))) =
                        D'.obs x
                    calc
                      decodeSource (decodeRec (decodeTarget (E'.obs y))) =
                          decodeSource (decodeRec (E.obs y)) := by
                        rw [hDecodeTarget y]
                      _ = decodeSource (D.obs x) := by
                        rw [hDecodeRec x y hK]
                      _ = D'.obs x := hDecodeSource x)

/-- Identity channel support. -/
def IdChan (X : Type u) : X -> X -> Prop :=
  fun x y => x = y

/-- Identity channel recovery is exactly distinction refinement. -/
theorem exactRecovers_id_iff_refines
    {X : Type u}
    (D E : ObsDist.{u, v} X) :
    ExactRecovers (IdChan X) D E <-> Refines D E := by
  constructor
  case mp =>
    intro hRec
    cases hRec with
    | intro decode hDecode =>
        exact Exists.intro decode
          (by
            intro x
            exact hDecode x x rfl)
  case mpr =>
    intro hRefines
    cases hRefines with
    | intro decode hDecode =>
        exact Exists.intro decode
          (by
            intro x y hxy
            cases hxy
            exact hDecode x)

/-- Channel support composition. `ChanComp K L` means `L` after `K`. -/
def ChanComp
    {X : Type u} {Y : Type w} {Z : Type z}
    (K : X -> Y -> Prop)
    (L : Y -> Z -> Prop) : X -> Z -> Prop :=
  fun x z => exists y, K x y /\ L y z

/-- Exact channel recovery composes by decoder composition. -/
theorem exactRecovers_comp
    {X : Type u} {Y : Type w} {Z : Type z}
    {K : X -> Y -> Prop}
    {L : Y -> Z -> Prop}
    {D : ObsDist.{u, v} X}
    {E : ObsDist.{w, v} Y}
    {F : ObsDist.{z, v} Z}
    (hKE : ExactRecovers K D E)
    (hLF : ExactRecovers L E F) :
    ExactRecovers (ChanComp K L) D F := by
  cases hKE with
  | intro decodeKE hDecodeKE =>
      cases hLF with
      | intro decodeLF hDecodeLF =>
          exact Exists.intro (fun label => decodeKE (decodeLF label))
            (by
              intro x z hKz
              cases hKz with
              | intro y hy =>
                  change decodeKE (decodeLF (F.obs z)) = D.obs x
                  calc
                    decodeKE (decodeLF (F.obs z)) = decodeKE (E.obs y) := by
                      rw [hDecodeLF y z hy.right]
                    _ = D.obs x := hDecodeKE x y hy.left)

/-- Channel-induced native transport is lax over channel composition. -/
theorem channelTransport_comp_subset
    {X : Type u} {Y : Type w} {Z : Type z}
    (K : X -> Y -> Prop)
    (L : Y -> Z -> Prop) :
    ProtoOmega.Transport.NativeTransport.Subset
      (ProtoOmega.Transport.NativeTransport.compose
        (channelTransport K) (channelTransport L))
      (channelTransport (ChanComp K L)) := by
  intro D F hComp
  cases hComp with
  | intro E hE =>
      exact exactRecovers_comp hE.left hE.right

/-- Source carrier for changed-carrier exact recovery. -/
inductive X0 where
  | zero
  | one
  deriving DecidableEq

/-- Middle carrier for changed-carrier exact recovery. -/
inductive X1 where
  | left
  | right
  deriving DecidableEq

/-- Target carrier for changed-carrier exact recovery. -/
inductive X2 where
  | low
  | high
  deriving DecidableEq

def D0 : ObsDist X0 where
  Label := Bool
  obs := fun
    | X0.zero => false
    | X0.one => true

def D1 : ObsDist X1 where
  Label := Bool
  obs := fun
    | X1.left => false
    | X1.right => true

def D2 : ObsDist X2 where
  Label := Bool
  obs := fun
    | X2.low => false
    | X2.high => true

def K01 : X0 -> X1 -> Prop
  | X0.zero, X1.left => True
  | X0.one, X1.right => True
  | _, _ => False

def K12 : X1 -> X2 -> Prop
  | X1.left, X2.low => True
  | X1.right, X2.high => True
  | _, _ => False

theorem exact_recovers_K01 :
    ExactRecovers K01 D0 D1 := by
  exact Exists.intro (fun label => label)
    (by
      intro x y hK
      cases x <;> cases y <;> simp [K01, D0, D1] at hK |-)

theorem exact_recovers_K12 :
    ExactRecovers K12 D1 D2 := by
  exact Exists.intro (fun label => label)
    (by
      intro x y hK
      cases x <;> cases y <;> simp [K12, D1, D2] at hK |-)

/-- Exact recovery composes across changed carrier types with no shared literal
state identity. -/
theorem exact_recovers_changed_carrier_comp :
    ExactRecovers (ChanComp K01 K12) D0 D2 := by
  exact exactRecovers_comp exact_recovers_K01 exact_recovers_K12

/-- Source carrier for the erasure example. -/
inductive BitSource where
  | zero
  | one
  deriving DecidableEq

/-- Singleton target carrier for the erasure example. -/
inductive StarTarget where
  | star
  deriving DecidableEq

def Dbit : ObsDist BitSource where
  Label := Bool
  obs := fun
    | BitSource.zero => false
    | BitSource.one => true

def DunitTarget : ObsDist StarTarget where
  Label := Unit
  obs := fun
    | StarTarget.star => Unit.unit

def DunitSource : ObsDist BitSource where
  Label := Unit
  obs := fun
    | BitSource.zero => Unit.unit
    | BitSource.one => Unit.unit

/-- Constant channel support from both source states to one target state. -/
def Kconst : BitSource -> StarTarget -> Prop
  | BitSource.zero, StarTarget.star => True
  | BitSource.one, StarTarget.star => True

/-- A constant channel erases a nontrivial bit distinction. -/
theorem not_exact_recovers_constant_bit :
    Not (ExactRecovers Kconst Dbit DunitTarget) := by
  intro hRec
  cases hRec with
  | intro decode hDecode =>
      have hZero : decode Unit.unit = false :=
        hDecode BitSource.zero StarTarget.star (by simp [Kconst])
      have hOne : decode Unit.unit = true :=
        hDecode BitSource.one StarTarget.star (by simp [Kconst])
      rw [hZero] at hOne
      cases hOne

/-- The same constant channel recovers the trivial source distinction. -/
theorem exact_recovers_constant_trivial :
    ExactRecovers Kconst DunitSource DunitTarget := by
  exact Exists.intro (fun _ => Unit.unit)
    (by
      intro x y hK
      cases x <;> cases y <;> rfl)

end FiniteChannelNative
end OmegaAdapters
