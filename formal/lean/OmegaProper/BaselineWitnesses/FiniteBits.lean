import OmegaProper.Trajectory.ConsequenceRelation

/-!
OmegaProper.BaselineWitnesses.FiniteBits

Shared finite carriers for exact baseline-witness conversions.

These helpers are intentionally small. They do not define identity,
recoverability, value, agency, or Omega; they only provide two declared
coordinate consequence systems over a four-point carrier.
-/

namespace OmegaProper
namespace BaselineWitnesses

open Trajectory.ConsequenceRelation

/-- A two-value coordinate. -/
inductive Bit where
  | zero
  | one
  deriving DecidableEq

/-- A four-point carrier with two binary coordinates. -/
inductive X2 where
  | x00
  | x01
  | x10
  | x11
  deriving DecidableEq

/-- Single evaluated context used by the finite witnesses. -/
inductive OneContext where
  | ctx
  deriving DecidableEq

def firstBit : X2 -> Bit
  | X2.x00 => Bit.zero
  | X2.x01 => Bit.zero
  | X2.x10 => Bit.one
  | X2.x11 => Bit.one

def secondBit : X2 -> Bit
  | X2.x00 => Bit.zero
  | X2.x01 => Bit.one
  | X2.x10 => Bit.zero
  | X2.x11 => Bit.one

def bitEqualityCompare : OneContext -> Bit -> Bit -> Prop
  | _, x, y => x = y

/-- Consequence system that exposes the first declared coordinate. -/
def declaredFirstSystem : ConsequenceSystem where
  Fragment := X2
  Context := OneContext
  Outcome := Bit
  consequence := fun _ x => firstBit x
  Compare := bitEqualityCompare
  Evaluated := fun _ => True

/-- Consequence system that exposes the second declared coordinate. -/
def declaredSecondSystem : ConsequenceSystem where
  Fragment := X2
  Context := OneContext
  Outcome := Bit
  consequence := fun _ x => secondBit x
  Compare := bitEqualityCompare
  Evaluated := fun _ => True

theorem first_allows_x00_x01 :
    ConsequenceIdentifiable declaredFirstSystem X2.x00 X2.x01 := by
  constructor <;> intro c _hEval <;> cases c <;> rfl

theorem first_allows_x10_x11 :
    ConsequenceIdentifiable declaredFirstSystem X2.x10 X2.x11 := by
  constructor <;> intro c _hEval <;> cases c <;> rfl

theorem second_allows_x00_x10 :
    ConsequenceIdentifiable declaredSecondSystem X2.x00 X2.x10 := by
  constructor <;> intro c _hEval <;> cases c <;> rfl

theorem second_allows_x01_x11 :
    ConsequenceIdentifiable declaredSecondSystem X2.x01 X2.x11 := by
  constructor <;> intro c _hEval <;> cases c <;> rfl

theorem first_separates_x00_x10 :
    ConsequenceSeparated declaredFirstSystem X2.x00 X2.x10 := by
  exists OneContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem second_separates_x00_x01 :
    ConsequenceSeparated declaredSecondSystem X2.x00 X2.x01 := by
  exists OneContext.ctx
  constructor
  case left =>
    trivial
  case right =>
    intro h
    cases h

theorem first_blocks_x00_x10 :
    ConsequenceMergeSeparated declaredFirstSystem X2.x00 X2.x10 := by
  exact Or.inl first_separates_x00_x10

theorem second_blocks_x00_x01 :
    ConsequenceMergeSeparated declaredSecondSystem X2.x00 X2.x01 := by
  exact Or.inl second_separates_x00_x01

end BaselineWitnesses
end OmegaProper
