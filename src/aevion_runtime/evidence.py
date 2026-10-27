"""Evidence bundle verification — authentic PASS, forged REJECT (fail-closed)."""

from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import jsonschema

from aevion_runtime.canonical import CanonicalJson
from aevion_runtime.model_access_envelope import (
    AccessTier,
    CapabilityClass,
    ModelAccessEnvelope,
    SafeguardMode,
)


_SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent.parent / "schemas" / "model_access_envelope.schema.json"
)

_REQUIRED_BUNDLE_KEYS = frozenset(
    {
        "envelope",
        "artifact_b64",
        "artifact_sha256",
        "requested_access_tier",
        "consensus_n",
        "consensus_f",
    }
)


@dataclass(frozen=True)
class EvidenceVerdict:
    passed: bool
    reason: str
    envelope: ModelAccessEnvelope | None = None
    artifact_bytes: bytes | None = None
    requested_tier: AccessTier | None = None
    consensus_n: int | None = None
    consensus_f: int | None = None
    bundle_digest: str | None = None


class EvidenceVerifier:
    """Verify envelope + artifact evidence bundles."""

    @staticmethod
    def _load_schema() -> dict[str, Any]:
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

    @staticmethod
    def build_bundle(
        envelope_dict: dict[str, Any],
        artifact_bytes: bytes,
        requested_access_tier: str,
        consensus_n: int = 10,
        consensus_f: int = 3,
    ) -> dict[str, Any]:
        digest = sha256(artifact_bytes).hexdigest()
        return {
            "envelope": envelope_dict,
            "artifact_b64": base64.standard_b64encode(artifact_bytes).decode("ascii"),
            "artifact_sha256": digest,
            "requested_access_tier": requested_access_tier,
            "consensus_n": consensus_n,
            "consensus_f": consensus_f,
        }

    @staticmethod
    def bundle_digest(bundle: dict[str, Any]) -> str:
        return CanonicalJson.digest_payload(bundle)

    @staticmethod
    def _check_required_fields(bundle: dict[str, Any]) -> EvidenceVerdict | None:
        if not isinstance(bundle, dict):
            return EvidenceVerdict(False, "bundle must be a mapping")
        missing = _REQUIRED_BUNDLE_KEYS - bundle.keys()
        if missing:
            return EvidenceVerdict(False, f"missing required field(s): {sorted(missing)}")
        return None

    @staticmethod
    def _parse_envelope(envelope_raw: Any) -> tuple[ModelAccessEnvelope | None, EvidenceVerdict | None]:
        if not isinstance(envelope_raw, dict):
            return None, EvidenceVerdict(False, "envelope must be a mapping")
        try:
            jsonschema.validate(
                instance=envelope_raw, schema=EvidenceVerifier._load_schema()
            )
        except jsonschema.ValidationError as exc:
            return None, EvidenceVerdict(
                False, f"envelope schema validation failed: {exc.message}"
            )
        envelope = ModelAccessEnvelope(
            model_id=envelope_raw["model_id"],
            capability_class=CapabilityClass(envelope_raw["capability_class"]),
            access_tier=AccessTier(envelope_raw["access_tier"]),
            safeguard_mode=SafeguardMode(envelope_raw["safeguard_mode"]),
            fallback_model=envelope_raw.get("fallback_model", ""),
            retention_policy_days=int(envelope_raw["retention_policy_days"]),
            receipt_required=bool(envelope_raw["receipt_required"]),
            human_gate_required=bool(envelope_raw["human_gate_required"]),
            policy_version=str(envelope_raw["policy_version"]),
        )
        return envelope, None

    @staticmethod
    def _decode_artifact(artifact_b64: Any) -> tuple[bytes | None, EvidenceVerdict | None]:
        if not isinstance(artifact_b64, str):
            return None, EvidenceVerdict(False, "artifact_b64 must be a string")
        try:
            return base64.standard_b64decode(artifact_b64), None
        except (ValueError, binascii.Error) as exc:
            return None, EvidenceVerdict(False, f"artifact_b64 decode failed: {exc}")

    @staticmethod
    def _verify_artifact_hash(
        artifact_bytes: bytes, claimed: Any
    ) -> EvidenceVerdict | None:
        if not isinstance(claimed, str) or len(claimed) != 64:
            return EvidenceVerdict(False, "artifact_sha256 must be a 64-char hex string")
        actual = sha256(artifact_bytes).hexdigest()
        if actual != claimed.lower():
            return EvidenceVerdict(False, "artifact_sha256 does not match artifact bytes")
        return None

    @staticmethod
    def _parse_requested_tier(tier_raw: Any) -> tuple[AccessTier | None, EvidenceVerdict | None]:
        if not isinstance(tier_raw, str):
            return None, EvidenceVerdict(False, "requested_access_tier must be a string")
        try:
            return AccessTier(tier_raw), None
        except ValueError:
            return None, EvidenceVerdict(
                False, f"unknown requested_access_tier: {tier_raw!r}"
            )

    @staticmethod
    def _parse_consensus(n: Any, f: Any) -> EvidenceVerdict | None:
        if not isinstance(n, int) or not isinstance(f, int):
            return EvidenceVerdict(False, "consensus_n and consensus_f must be integers")
        if n < 0 or f < 0:
            return EvidenceVerdict(False, "consensus_n and consensus_f must be non-negative")
        return None

    @staticmethod
    def verify(bundle: dict[str, Any]) -> EvidenceVerdict:
        """Fail-closed: any ambiguity or error yields passed=False."""
        failure = EvidenceVerifier._check_required_fields(bundle)
        if failure is not None:
            return failure

        envelope, failure = EvidenceVerifier._parse_envelope(bundle["envelope"])
        if failure is not None:
            return failure

        artifact_bytes, failure = EvidenceVerifier._decode_artifact(bundle["artifact_b64"])
        if failure is not None:
            return failure

        failure = EvidenceVerifier._verify_artifact_hash(
            artifact_bytes, bundle["artifact_sha256"]
        )
        if failure is not None:
            return failure

        requested, failure = EvidenceVerifier._parse_requested_tier(
            bundle["requested_access_tier"]
        )
        if failure is not None:
            return failure

        n = bundle["consensus_n"]
        f = bundle["consensus_f"]
        failure = EvidenceVerifier._parse_consensus(n, f)
        if failure is not None:
            return failure

        digest = EvidenceVerifier.bundle_digest(bundle)
        return EvidenceVerdict(
            True,
            "PASS",
            envelope=envelope,
            artifact_bytes=artifact_bytes,
            requested_tier=requested,
            consensus_n=n,
            consensus_f=f,
            bundle_digest=digest,
        )
