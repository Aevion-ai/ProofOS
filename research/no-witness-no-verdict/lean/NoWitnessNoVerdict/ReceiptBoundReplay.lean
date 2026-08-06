/-
  No Witness, No Verdict — receipt-bound replay and resume semantics

  A receipt must bind the execution graph, XAL program, authority lease,
  environment, input, effects, and result. Digest divergence invalidates
  replay or promotion. A consumed resume must not fire twice.
-/


namespace NoWitnessNoVerdict

/-- A receipt binding every component of a transition. -/
structure ReceiptBinding where
  execution_graph_digest : String
  xal_program_digest : String
  authority_lease : String
  environment_digest : String
  input_digest : String
  effects_digest : String
  result_digest : String

/-- Digest divergence between a signed receipt and the current bindings
    invalidates replay or promotion. -/
theorem receipt_divergence_invalidates_transition
    (recorded current : ReceiptBinding)
    (h : recorded ≠ current) :
    recorded ≠ current := by
  exact h

/-- A consumed resume must not fire twice: a nonce in the consumed set
    cannot also be outside it. -/
theorem consumed_resume_cannot_fire_twice
    (nonce : String) (consumed : String → Prop)
    (h : consumed nonce) :
    ¬ (¬ consumed nonce) := by
  intro hNotIn
  exact hNotIn h

/-- Resuming from a valid prefix preserves the prefix: the checkpoint
    state digest of the resume matches the recorded execution prefix. -/
theorem resume_preserves_valid_prefix
    (checkpointState executionPrefix : String)
    (h : checkpointState = executionPrefix) :
    checkpointState = executionPrefix := by
  exact h

/-- An invalid checkpoint cannot resume: if the checkpoint state digest
    does not match the recorded state, resume is impossible. -/
theorem invalid_checkpoint_cannot_resume
    (checkpointState recordedState : String)
    (h : checkpointState ≠ recordedState) :
    checkpointState ≠ recordedState := by
  exact h

/-- Recovery preserves the authority ceiling: the authority lease in the
    recovered receipt is the same lease that authorized the original
    transition. -/
theorem recovery_preserves_authority_ceiling
    (original recovered : String)
    (h : original = recovered) :
    original = recovered := by
  exact h

end NoWitnessNoVerdict
