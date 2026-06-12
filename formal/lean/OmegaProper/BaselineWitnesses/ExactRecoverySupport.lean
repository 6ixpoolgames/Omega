/-!
OmegaProper.BaselineWitnesses.ExactRecoverySupport

Exact declared recovery for finite/support-style channels.

The standard compression: a declared decoder exists exactly when declared
source classes do not collide under the declared target observation on the
support of the channel. The reverse direction for a total decoder needs an
arbitrary value for observations that are never produced, expressed here as
`[Nonempty D]`.
-/

namespace OmegaProper
namespace BaselineWitnesses
namespace ExactRecoverySupport

universe u v w z

/--
A decoder exactly recovers the declared source value whenever the support
relation allows source `x` to produce output `y`.
-/
def ExactDecoder {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    (support : X -> Y -> Prop)
    (declared : X -> D)
    (observe : Y -> O)
    (decoder : O -> D) : Prop :=
  forall x y, support x y -> decoder (observe y) = declared x

def ExactRecoveryExists {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    (support : X -> Y -> Prop)
    (declared : X -> D)
    (observe : Y -> O) : Prop :=
  exists decoder : O -> D, ExactDecoder support declared observe decoder

/--
Observed support disjointness: if two supported outputs have the same declared
observation, their source states must have the same declared value.
-/
def ObservedSupportDisjoint
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    (support : X -> Y -> Prop)
    (declared : X -> D)
    (observe : Y -> O) : Prop :=
  forall x1 x2 y1 y2,
    support x1 y1 ->
    support x2 y2 ->
    observe y1 = observe y2 ->
    declared x1 = declared x2

theorem exactDecoder_implies_observedSupportDisjoint
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    {support : X -> Y -> Prop}
    {declared : X -> D}
    {observe : Y -> O}
    {decoder : O -> D}
    (hDecoder : ExactDecoder support declared observe decoder) :
    ObservedSupportDisjoint support declared observe := by
  intro x1 x2 y1 y2 h1 h2 hObs
  calc
    declared x1 = decoder (observe y1) := (hDecoder x1 y1 h1).symm
    _ = decoder (observe y2) := by rw [hObs]
    _ = declared x2 := hDecoder x2 y2 h2

theorem exactRecoveryExists_implies_observedSupportDisjoint
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    {support : X -> Y -> Prop}
    {declared : X -> D}
    {observe : Y -> O}
    (hExists : ExactRecoveryExists support declared observe) :
    ObservedSupportDisjoint support declared observe := by
  match hExists with
  | Exists.intro decoder hDecoder =>
      exact exactDecoder_implies_observedSupportDisjoint
        (decoder := decoder) hDecoder

theorem observedSupportDisjoint_implies_exactRecoveryExists
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Nonempty D]
    {support : X -> Y -> Prop}
    {declared : X -> D}
    {observe : Y -> O}
    (hDisjoint : ObservedSupportDisjoint support declared observe) :
    ExactRecoveryExists support declared observe := by
  classical
  let decoder : O -> D := fun obs =>
    if hObs : exists x, exists y, support x y /\ observe y = obs then
      declared (Classical.choose hObs)
    else
      Classical.choice inferInstance
  exists decoder
  intro x y hSupport
  dsimp [decoder]
  have hObs : exists x0, exists y0, support x0 y0 /\ observe y0 = observe y := by
    exact Exists.intro x (Exists.intro y (And.intro hSupport rfl))
  rw [dif_pos hObs]
  match Classical.choose_spec hObs with
  | Exists.intro y0 hy0 =>
      exact hDisjoint
        (Classical.choose hObs)
        x
        y0
        y
        hy0.left
        hSupport
        hy0.right

theorem exactRecoveryExists_iff_observedSupportDisjoint
    {X : Type u} {Y : Type v} {D : Type w} {O : Type z}
    [Nonempty D]
    {support : X -> Y -> Prop}
    {declared : X -> D}
    {observe : Y -> O} :
    ExactRecoveryExists support declared observe <->
      ObservedSupportDisjoint support declared observe := by
  constructor
  · exact exactRecoveryExists_implies_observedSupportDisjoint
  · exact observedSupportDisjoint_implies_exactRecoveryExists

end ExactRecoverySupport
end BaselineWitnesses
end OmegaProper
