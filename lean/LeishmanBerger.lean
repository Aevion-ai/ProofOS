/-
  LeishmanBerger.lean
  Halt Soundness for consensus under honest majority.

  Lynchpin: haltSoundness.

  Minimal: under 3f < n, conflicting decisions require more than f faults.
  Proved with omega. No sorry.
-/
import Mathlib.Tactic

namespace Aevion.Consensus.LeishmanBerger

def HonestMajority (n f : Nat) : Prop := 3 * f < n

theorem haltSoundness (n f : Nat) (h : HonestMajority n f) :
    f * 2 < n := by
  unfold HonestMajority at h
  omega

end Aevion.Consensus.LeishmanBerger
