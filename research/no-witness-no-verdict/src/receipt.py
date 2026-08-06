"""Receipt-bound replay and resume semantics.

A receipt must bind: execution graph, XAL program, authority lease,
environment, input, effects, and result. Digest divergence invalidates
replay or promotion (theorem receipt_divergence_invalidates_transition).

Resume semantics (Resume Means Resume): a transition must record whether
it was NEW, RETRIED, RESUMED, FORKED, REPLAYED, or COMPENSATED, and a
consumed resume must not fire twice (theorem
resume_cannot_repeat_consumed_effect).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class TransitionOrigin(str, Enum):
    NEW = "NEW"
    RETRIED = "RETRIED"
    RESUMED = "RESUMED"
    FORKED = "FORKED"
    REPLAYED = "REPLAYED"
    COMPENSATED = "COMPENSATED"


@dataclass(frozen=True)
class ReceiptBindings:
    execution_graph_digest: str
    xal_program_digest: str
    authority_lease: str
    environment_digest: str
    input_digest: str
    effects_digest: str
    result_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_graph_digest": self.execution_graph_digest,
            "xal_program_digest": self.xal_program_digest,
            "authority_lease": self.authority_lease,
            "environment_digest": self.environment_digest,
            "input_digest": self.input_digest,
            "effects_digest": self.effects_digest,
            "result_digest": self.result_digest,
        }


def sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def receipt_body_hash(bindings: ReceiptBindings, origin: TransitionOrigin | str) -> str:
    origin_value = origin.value if isinstance(origin, TransitionOrigin) else origin
    canonical = json.dumps(
        {"origin": origin_value, **bindings.to_dict()},
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_hex(canonical)


@dataclass(frozen=True)
class TransitionReceipt:
    receipt_id: str
    transition_id: str
    bindings: ReceiptBindings
    origin: TransitionOrigin
    body_hash: str
    signature: str = ""
    admission_disposition: str = "ADMIT"
    execution_outcome: str = "PENDING"

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "transition_id": self.transition_id,
            "bindings": self.bindings.to_dict(),
            "origin": self.origin.value,
            "body_hash": self.body_hash,
            "signature": self.signature,
            "admission_disposition": self.admission_disposition,
            "execution_outcome": self.execution_outcome,
        }


def receipt_divergence_invalidates(
    receipt: TransitionReceipt,
    current_bindings: ReceiptBindings,
) -> bool:
    """Any digest divergence between the signed receipt and the current
    bindings invalidates replay or promotion. Returns True when valid
    (no divergence)."""
    recomputed = receipt_body_hash(current_bindings, receipt.origin)
    return recomputed == receipt.body_hash


@dataclass(frozen=True)
class ResumeMarker:
    checkpoint_id: str
    checkpoint_state_digest: str
    execution_prefix_digest: str
    prior_effect_set_digest: str
    resume_nonce: str
    consume_claim: str
    fork_intent: str | None = None
    recovery_epoch: int = 0
    attempt_number: int = 1
    effect_idempotency_key: str = ""
    effect_delivery_semantics: str = "at_least_once"

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_state_digest": self.checkpoint_state_digest,
            "execution_prefix_digest": self.execution_prefix_digest,
            "prior_effect_set_digest": self.prior_effect_set_digest,
            "resume_nonce": self.resume_nonce,
            "consume_claim": self.consume_claim,
            "fork_intent": self.fork_intent,
            "recovery_epoch": self.recovery_epoch,
            "attempt_number": self.attempt_number,
            "effect_idempotency_key": self.effect_idempotency_key,
            "effect_delivery_semantics": self.effect_delivery_semantics,
        }


def resume_cannot_repeat_consumed_effect(
    marker: ResumeMarker,
    already_consumed: set[str],
) -> bool:
    """A consumed resume must not fire twice.

    Returns True when the resume is admissible (nonce not consumed).
    Fail-closed: consumed nonce -> False (REJECT).
    """
    if marker.consume_claim in already_consumed:
        return False
    if marker.effect_idempotency_key and marker.effect_idempotency_key in already_consumed:
        return False
    return True


def invalid_checkpoint_cannot_resume(
    marker: ResumeMarker,
    recorded_checkpoint_digest: str,
) -> bool:
    """A resume referencing a checkpoint whose digest does not match the
    recorded state is invalid. Returns True when the checkpoint is valid."""
    return marker.checkpoint_state_digest == recorded_checkpoint_digest


def receipt_origin_classifier(
    marker: ResumeMarker | None,
    fork_intent: str | None = None,
) -> TransitionOrigin:
    if fork_intent:
        return TransitionOrigin.FORKED
    if marker is not None:
        if marker.consume_claim:
            return TransitionOrigin.RESUMED
        return TransitionOrigin.REPLAYED
    return TransitionOrigin.NEW
