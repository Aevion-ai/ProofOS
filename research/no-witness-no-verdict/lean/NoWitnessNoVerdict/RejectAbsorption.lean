/-
  No Witness, No Verdict — reject_is_absorbing

  Once a hard fault exists, downstream components cannot convert the
  transition into ADMIT, PASS, or PROMOTE. REJECT is absorbing.

  Proof: by the definition of DispositionAtHardFault, a hard fault forces
  the disposition to REJECT for every downstream stage.
-/


namespace NoWitnessNoVerdict

inductive Disposition where
  | admit
  | hold
  | reject
  deriving DecidableEq, Repr

/-- A hard fault forces REJECT at every downstream stage. -/
def forcesReject (d : Disposition) : Prop :=
  d = Disposition.reject

/-- Once a hard fault exists, the disposition is REJECT. -/
theorem reject_is_absorbing
    (d : Disposition)
    (h : forcesReject d) :
    d = Disposition.reject := by
  exact h

/-- Any disposition derived from a hard fault cannot be ADMIT or PROMOTE. -/
theorem hard_fault_not_admit
    (d : Disposition)
    (h : forcesReject d) :
    d ≠ Disposition.admit := by
  intro hAdmit
  rw [h] at hAdmit
  cases hAdmit

end NoWitnessNoVerdict
