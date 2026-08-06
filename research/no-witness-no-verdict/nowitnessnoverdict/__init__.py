"""Package entry: the six formal claims as executable predicates.

1. reject_is_absorbing
2. candidate_only_cannot_authorize
3. no_same_epoch_self_certification
4. same_authority_root_is_not_independent
5. resume_cannot_repeat_consumed_effect
6. receipt_divergence_invalidates_transition
"""

from .candidate_only import (
    AuthorityGrant,
    AuthorityRoot,
    CandidateOnlyViolation,
    EpochContext,
    assert_reflection_only,
    candidate_cannot_authorize,
    promote_candidate,
    same_authority_root_is_not_independent,
    same_epoch_self_certification,
)
from .fail_closed import (
    Disposition,
    MANDATORY_OBLIGATIONS,
    Obligation,
    ObligationDischarge,
    ObligationKind,
    TransitionRequest,
    decide_transition,
    obligations_met,
    reject_is_absorbing,
)
from .receipt import (
    ReceiptBindings,
    ResumeMarker,
    TransitionOrigin,
    TransitionReceipt,
    invalid_checkpoint_cannot_resume,
    receipt_body_hash,
    receipt_divergence_invalidates,
    receipt_origin_classifier,
    resume_cannot_repeat_consumed_effect,
    sha256_hex,
)

__all__ = [
    "AuthorityGrant",
    "AuthorityRoot",
    "CandidateOnlyViolation",
    "Disposition",
    "EpochContext",
    "MANDATORY_OBLIGATIONS",
    "Obligation",
    "ObligationDischarge",
    "ObligationKind",
    "ReceiptBindings",
    "ResumeMarker",
    "TransitionOrigin",
    "TransitionReceipt",
    "TransitionRequest",
    "assert_reflection_only",
    "candidate_cannot_authorize",
    "decide_transition",
    "invalid_checkpoint_cannot_resume",
    "obligations_met",
    "promote_candidate",
    "receipt_body_hash",
    "receipt_divergence_invalidates",
    "receipt_origin_classifier",
    "reject_is_absorbing",
    "resume_cannot_repeat_consumed_effect",
    "same_authority_root_is_not_independent",
    "same_epoch_self_certification",
    "sha256_hex",
]
