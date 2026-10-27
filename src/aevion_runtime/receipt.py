"""Content-addressed decision receipts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aevion_runtime.canonical import CanonicalJson


@dataclass(frozen=True)
class ReceiptBodyFields:
    """Fields hashed into a receipt_id (excluding receipt_id itself)."""

    prev_receipt_id: str
    evidence_bundle: dict[str, Any]
    bundle_digest: str
    evidence_verdict: str
    decision: str
    policy_version: str
    policy_reason: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "prev_receipt_id": self.prev_receipt_id,
            "evidence_bundle": self.evidence_bundle,
            "bundle_digest": self.bundle_digest,
            "evidence_verdict": self.evidence_verdict,
            "decision": self.decision,
            "policy_version": self.policy_version,
            "policy_reason": self.policy_reason,
        }


class Receipt:
    """SHA-256 receipt_id over canonical JSON body (excluding receipt_id)."""

    @staticmethod
    def build_body(fields: ReceiptBodyFields) -> dict[str, Any]:
        return fields.to_mapping()

    @staticmethod
    def with_id(body: dict[str, Any]) -> dict[str, Any]:
        if "receipt_id" in body:
            raise ValueError("body must not already include receipt_id")
        receipt_id = CanonicalJson.digest_payload(body)
        return {**body, "receipt_id": receipt_id}

    @staticmethod
    def verify_id(receipt: dict[str, Any]) -> bool:
        receipt_id = receipt.get("receipt_id")
        if not isinstance(receipt_id, str):
            return False
        body = {k: v for k, v in receipt.items() if k != "receipt_id"}
        return CanonicalJson.digest_payload(body) == receipt_id
