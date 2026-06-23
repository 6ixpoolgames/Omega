import OmegaProper.Recovery.RobustRandomized

/-!
OmegaProper.Recovery.RandomizedFamily

Declared randomized-decoder family surfaces.

This file does not solve global randomized maximin optimization. It names the
finite/declared-family pattern: a candidate randomized decoder must come from a
declared indexed family, and threshold recovery is recovery by one member of
that family.
-/

namespace OmegaProper
namespace Recovery

universe u v w z i

/-- A decoder is allowed by an indexed declared family when it is one of its members. -/
def RandomizedFamilyAllowed
    {I : Type i} {O : Type z} {D : Type w} [Fintype D]
    (family : I -> RandomizedDecoder O D)
    (decoder : RandomizedDecoder O D) : Prop :=
  exists index : I, family index = decoder

/--
One member of a declared randomized-decoder family reaches threshold `tau`.

The index type may be finite in adapter use; this definition only needs the
declared family itself.
-/
def RandomizedFamilyRecoveryAt
    {I : Type i} {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (C : RatChannel X Y)
    (target : X -> D)
    (observe : Y -> O)
    (family : I -> RandomizedDecoder O D)
    (tau : Rat) : Prop :=
  exists index : I,
    RandomizedDeclaredRecoveryAt C target observe tau (family index)

/--
Declared-family recovery is the same as restricted randomized recovery where
the allowed class is exactly the image of the family.
-/
theorem randomizedFamilyRecoveryAt_iff_randomizedRecoveryInAt_image
    {I : Type i} {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {C : RatChannel X Y}
    {target : X -> D}
    {observe : Y -> O}
    {family : I -> RandomizedDecoder O D}
    {tau : Rat} :
    RandomizedFamilyRecoveryAt C target observe family tau <->
      RandomizedRecoveryInAt C target observe
        (RandomizedFamilyAllowed family) tau := by
  constructor
  · intro hFamily
    match hFamily with
    | Exists.intro index hDecoder =>
        exact Exists.intro (family index)
          ⟨Exists.intro index rfl, hDecoder⟩
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        match hDecoder.1 with
        | Exists.intro index hEq =>
            subst decoder
            exact Exists.intro index hDecoder.2

/--
One member of a declared randomized-decoder family reaches threshold `tau`
uniformly over an ambiguity set.
-/
def RobustRandomizedFamilyRecoveryAt
    {I : Type i} {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    (Gamma : Set (RatChannel X Y))
    (target : X -> D)
    (observe : Y -> O)
    (family : I -> RandomizedDecoder O D)
    (tau : Rat) : Prop :=
  exists index : I,
    RobustRandomizedDeclaredRecoveryAt Gamma target observe tau (family index)

/--
Declared-family robust randomized recovery is the restricted robust randomized
recovery surface whose allowed class is exactly the image of the family.
-/
theorem robustRandomizedFamilyRecoveryAt_iff_robustRandomizedRecoveryInAt_image
    {I : Type i} {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Fintype Y] [Fintype D]
    {Gamma : Set (RatChannel X Y)}
    {target : X -> D}
    {observe : Y -> O}
    {family : I -> RandomizedDecoder O D}
    {tau : Rat} :
    RobustRandomizedFamilyRecoveryAt Gamma target observe family tau <->
      RobustRandomizedRecoveryInAt Gamma target observe
        (RandomizedFamilyAllowed family) tau := by
  constructor
  · intro hFamily
    match hFamily with
    | Exists.intro index hDecoder =>
        exact Exists.intro (family index)
          ⟨Exists.intro index rfl, hDecoder⟩
  · intro hRecovery
    match hRecovery with
    | Exists.intro decoder hDecoder =>
        match hDecoder.1 with
        | Exists.intro index hEq =>
            subst decoder
            exact Exists.intro index hDecoder.2

end Recovery
end OmegaProper
