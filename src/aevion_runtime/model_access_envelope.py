"""Model Access Envelope — CapabilityAccessSeparationLemma runtime.

Aevion does not need to own the frontier model. Aevion owns the access envelope
around frontier capability.

Validated by Anthropic Fable 5 / Mythos 5 launch (June 9, 2026):
  Fable 5 = Mythos-class model + PUBLIC tier + FULL safeguards + Opus fallback
  Mythos 5 = same model + TRUSTED_ACCESS tier + SELECTED_LIFTED safeguards

This module provides the Python runtime for the ModelAccessEnvelope schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CapabilityClass(str, Enum):
    GENERAL = "GENERAL"
    MYTHOS_CLASS = "MYTHOS_CLASS"
    DUAL_USE_CRITICAL = "DUAL_USE_CRITICAL"


class AccessTier(str, Enum):
    PUBLIC = "PUBLIC"
    BUSINESS = "BUSINESS"
    TRUSTED_ACCESS = "TRUSTED_ACCESS"
    HUMAN_ONLY = "HUMAN_ONLY"

    def __ge__(self, other: AccessTier) -> bool:  # type: ignore[override]
        """Partial order: more restrictive >= less restrictive."""
        order = {
            AccessTier.PUBLIC: 0,
            AccessTier.BUSINESS: 1,
            AccessTier.TRUSTED_ACCESS: 2,
            AccessTier.HUMAN_ONLY: 3,
        }
        return order[self] >= order[other]

    def __gt__(self, other: AccessTier) -> bool:  # type: ignore[override]
        """Strict partial order: more restrictive > less restrictive."""
        order = {
            AccessTier.PUBLIC: 0,
            AccessTier.BUSINESS: 1,
            AccessTier.TRUSTED_ACCESS: 2,
            AccessTier.HUMAN_ONLY: 3,
        }
        return order[self] > order[other]


class SafeguardMode(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    LIFTED_BY_APPROVAL = "LIFTED_BY_APPROVAL"


@dataclass(frozen=True)
class ModelAccessEnvelope:
    """Access envelope around a frontier model capability.

    The envelope, not the model, determines deployment safety.
    This is the CapabilityAccessSeparationLemma in code form:

      model + policy + access + receipts + audit + fallback = deployable product
    """

    model_id: str
    capability_class: CapabilityClass
    access_tier: AccessTier
    safeguard_mode: SafeguardMode
    fallback_model: str = ""
    retention_policy_days: int = 30
    receipt_required: bool = True
    human_gate_required: bool = True
    policy_version: str = "capability_access_v0.1"

    def __post_init__(self) -> None:
        """Validate envelope invariants after construction."""
        self._validate_public_tier()
        self._validate_human_only_tier()
        self._validate_dual_use_critical()

    def _validate_public_tier(self) -> None:
        if self.access_tier != AccessTier.PUBLIC:
            return
        if self.safeguard_mode != SafeguardMode.FULL:
            raise ValueError("PUBLIC tier requires FULL safeguard mode")
        if not self.fallback_model:
            raise ValueError("PUBLIC tier requires a fallback_model")

    def _validate_human_only_tier(self) -> None:
        if self.access_tier != AccessTier.HUMAN_ONLY:
            return
        if not self.human_gate_required:
            raise ValueError("HUMAN_ONLY tier requires human_gate_required=True")
        if not self.receipt_required:
            raise ValueError("HUMAN_ONLY tier requires receipt_required=True")

    def _validate_dual_use_critical(self) -> None:
        if self.capability_class != CapabilityClass.DUAL_USE_CRITICAL:
            return
        if self.access_tier not in (
            AccessTier.TRUSTED_ACCESS,
            AccessTier.HUMAN_ONLY,
        ):
            raise ValueError(
                f"DUAL_USE_CRITICAL requires TRUSTED_ACCESS or HUMAN_ONLY, "
                f"got {self.access_tier.value}"
            )
        if not self.human_gate_required:
            raise ValueError("DUAL_USE_CRITICAL requires human_gate_required=True")
        if self.retention_policy_days < 30:
            raise ValueError("DUAL_USE_CRITICAL requires retention >= 30 days")

    def is_safe_deployable(self) -> bool:
        """A deployment is safe IFF the envelope, not the model, guarantees it.

        Theorem (deployment_safety_not_model_intrinsic):
          SafeDeployable(M, E) ↔
            E.receipt_required = true ∧
            E.human_gate_req = true ∧
            E.fallback_model ≠ "" ∧
            E.retention_days ≥ 30
        """
        return (
            self.receipt_required
            and self.human_gate_required
            and self.fallback_model != ""
            and self.retention_policy_days >= 30
        )

    def can_serve(self, requested_tier: AccessTier) -> bool:
        """Check if this envelope can serve a request at the given tier.

        More restrictive envelopes can serve less restrictive requests.
        """
        return self.access_tier >= requested_tier

    def fallback_envelope(self) -> ModelAccessEnvelope:
        """Produce a safer fallback envelope (constitutional halt / capability subtraction)."""
        if not self.fallback_model:
            raise ValueError("No fallback model configured")

        # Fallback is always more restrictive
        fallback_tier = AccessTier.BUSINESS
        if self.access_tier > AccessTier.BUSINESS:
            fallback_tier = self.access_tier

        return ModelAccessEnvelope(
            model_id=self.fallback_model,
            capability_class=CapabilityClass.GENERAL,
            access_tier=fallback_tier,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="",
            retention_policy_days=self.retention_policy_days,
            receipt_required=True,
            human_gate_required=True,
            policy_version=f"{self.policy_version}-fallback",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "capability_class": self.capability_class.value,
            "access_tier": self.access_tier.value,
            "safeguard_mode": self.safeguard_mode.value,
            "fallback_model": self.fallback_model,
            "retention_policy_days": self.retention_policy_days,
            "receipt_required": self.receipt_required,
            "human_gate_required": self.human_gate_required,
            "policy_version": self.policy_version,
        }

    @classmethod
    def fable_5(cls) -> ModelAccessEnvelope:
        """Anthropic Fable 5: Mythos-class model, PUBLIC tier, FULL safeguards."""
        return cls(
            model_id="claude-mythos-5",
            capability_class=CapabilityClass.MYTHOS_CLASS,
            access_tier=AccessTier.PUBLIC,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="claude-opus-4-8",
            retention_policy_days=30,
            receipt_required=False,
            human_gate_required=False,
            policy_version="anthropic-fable-5-20260609",
        )

    @classmethod
    def mythos_5(cls) -> ModelAccessEnvelope:
        """Anthropic Mythos 5: same model, TRUSTED_ACCESS, SELECTED_LIFTED."""
        return cls(
            model_id="claude-mythos-5",
            capability_class=CapabilityClass.MYTHOS_CLASS,
            access_tier=AccessTier.TRUSTED_ACCESS,
            safeguard_mode=SafeguardMode.PARTIAL,
            fallback_model="claude-opus-4-8",
            retention_policy_days=30,
            receipt_required=False,
            human_gate_required=True,
            policy_version="anthropic-mythos-5-20260609",
        )

    @classmethod
    def aevion_proof_os(cls, model_id: str) -> ModelAccessEnvelope:
        """Aevion ProofOS envelope: receipted, human-gated, auditable."""
        return cls(
            model_id=model_id,
            capability_class=CapabilityClass.MYTHOS_CLASS,
            access_tier=AccessTier.BUSINESS,
            safeguard_mode=SafeguardMode.FULL,
            fallback_model="safe-degraded-mode",
            retention_policy_days=90,
            receipt_required=True,
            human_gate_required=True,
            policy_version="aevion-proofos-v1.0",
        )
