"""Canonical JSON serialization for content-addressed receipts."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any


class CanonicalJson:
    """Stable JSON encoding for hashing (sorted keys, no insignificant whitespace)."""

    @staticmethod
    def dumps(value: Any) -> str:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )

    @staticmethod
    def digest_payload(body: dict[str, Any]) -> str:
        """SHA-256 hex of canonical JSON for a mapping without a receipt_id field."""
        if "receipt_id" in body:
            raise ValueError("digest_payload must not include receipt_id")
        return sha256(CanonicalJson.dumps(body).encode("utf-8")).hexdigest()
