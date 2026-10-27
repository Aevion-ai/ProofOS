"""Policy gate — ALLOW / DENY on verified evidence (halt + envelope rules)."""

from __future__ import annotations

from dataclasses import dataclass

from aevion_runtime.evidence import EvidenceVerdict


@dataclass(frozen=True)
class PolicyDecision:
    decision: str  # ALLOW or DENY
    policy_version: str
    reason: str


class PolicyGate:
    """Mirrors haltSoundness (3f < n) plus ModelAccessEnvelope deployment rules."""

    @staticmethod
    def halt_passes(n: int, f: int) -> bool:
        return 3 * f < n

    @staticmethod
    def evaluate(verdict: EvidenceVerdict) -> PolicyDecision:
        if not verdict.passed or verdict.envelope is None:
            return PolicyDecision("DENY", "unknown", "evidence not verified")

        envelope = verdict.envelope
        policy_version = envelope.policy_version
        n = verdict.consensus_n or 0
        f = verdict.consensus_f or 0
        requested = verdict.requested_tier

        if not PolicyGate.halt_passes(n, f):
            return PolicyDecision(
                "DENY",
                policy_version,
                f"halt gate failed: honest majority requires 3*f < n (n={n}, f={f})",
            )

        if not envelope.is_safe_deployable():
            return PolicyDecision(
                "DENY",
                policy_version,
                "envelope fails is_safe_deployable()",
            )

        if requested is None or not envelope.can_serve(requested):
            return PolicyDecision(
                "DENY",
                policy_version,
                f"envelope cannot serve requested tier {requested}",
            )

        return PolicyDecision("ALLOW", policy_version, "policy checks passed")
