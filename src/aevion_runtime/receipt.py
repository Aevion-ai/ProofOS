"""Content-addressed decision receipts."""

from __future__ import annotations

from typing import Any

from aevion_runtime.canonical import CanonicalJson


class Receipt:
    """SHA-256 receipt_id over canonical JSON body (excluding receipt_id)."""

    @staticmethod
    def build_body(
        prev_receipt_id: str,
        evidence_bundle: dict[str, Any],
        bundle_digest: str,
        evidence_verdict: str,
        decision: str,
        policy_version: str,
        policy_reason: str,
    ) -> dict[str, Any]:
        return {
            "prev_receipt_id": prev_receipt_id,
            "evidence_bundle": evidence_bundle,
            "bundle_digest": bundle_digest,
            "evidence_verdict": evidence_verdict,
            "decision": decision,
            "policy_version": policy_version,
            "policy_reason": policy_reason,
        }

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
